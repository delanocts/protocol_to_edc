"""The single place this project talks to Claude.

Every domain agent makes the same shape of call: a stable system prefix (which
is prompt-cached), the protocol document, a domain-specific instruction, and a
pydantic output schema. Centralising it means caching, retries, usage accounting
and error handling are written once and behave identically for all eight agents
-- and that adding a ninth domain involves no API code at all.

Request shape, and why:

* `client.messages.parse(output_format=Model)` -- the response is validated
  against the domain's pydantic model by the SDK, so a malformed extraction
  fails loudly here instead of surfacing as a strange USDM document later.
* `thinking={"type": "adaptive"}` with `output_config.effort` -- extraction from
  a dense protocol table is exactly the kind of work that benefits from it.
* `cache_control` marking the end of the system prefix and the document, so the
  seven agents that run after the first read the protocol from cache.
* Streaming, because a large `max_tokens` on a long document otherwise risks an
  HTTP timeout.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Sequence, TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from .cache import ResponseCache, fingerprint
from .documents import UploadedDocument

ModelT = TypeVar("ModelT", bound=BaseModel)

# Streaming removes the HTTP-timeout reason to keep this low, and the schedule
# domain legitimately produces a large document. A ceiling that is too low does
# not truncate cleanly -- it cuts the JSON mid-string, which fails to parse.
DEFAULT_MAX_TOKENS = 64000
RETRYABLE = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.APITimeoutError,
    anthropic.InternalServerError,
)


class LlmError(RuntimeError):
    """A call that could not be completed."""


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    calls: int = 0
    seconds: float = 0.0

    def add(self, other: Usage) -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.cache_write_tokens += other.cache_write_tokens
        self.calls += other.calls
        self.seconds += other.seconds

    @property
    def cache_hit_ratio(self) -> float:
        """Share of the prompt served from cache.

        Cache *writes* count in the denominator: the first agent pays to put the
        protocol in the cache, and leaving that out would report a 100% hit rate
        on a run that in fact paid full price for a 168,000-token document.
        """
        total = self.input_tokens + self.cache_read_tokens + self.cache_write_tokens
        return (self.cache_read_tokens / total) if total else 0.0

    @property
    def billable_input(self) -> int:
        return self.input_tokens + self.cache_read_tokens + self.cache_write_tokens

    def as_dict(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "inputTokens": self.input_tokens,
            "outputTokens": self.output_tokens,
            "cacheReadTokens": self.cache_read_tokens,
            "cacheWriteTokens": self.cache_write_tokens,
            "billableInputTokens": self.billable_input,
            "cacheHitRatio": round(self.cache_hit_ratio, 3),
            "seconds": round(self.seconds, 1),
        }

    def summary(self) -> str:
        return (
            f"{self.calls} call(s), in {self.billable_input:,} "
            f"({self.input_tokens:,} fresh, {self.cache_write_tokens:,} cache-write, "
            f"{self.cache_read_tokens:,} cache-read = {self.cache_hit_ratio:.0%} hit), "
            f"out {self.output_tokens:,}, {self.seconds:.1f}s"
        )


@dataclass
class Result[ModelT: BaseModel]:
    data: ModelT
    usage: Usage
    from_cache: bool = False
    stop_reason: str = ""
    warnings: list[str] = field(default_factory=list)


def _usage_from(response: Any, seconds: float) -> Usage:
    raw = getattr(response, "usage", None)
    return Usage(
        input_tokens=getattr(raw, "input_tokens", 0) or 0,
        output_tokens=getattr(raw, "output_tokens", 0) or 0,
        cache_read_tokens=getattr(raw, "cache_read_input_tokens", 0) or 0,
        cache_write_tokens=getattr(raw, "cache_creation_input_tokens", 0) or 0,
        calls=1,
        seconds=seconds,
    )


class Agent:
    """Runs one structured extraction against the protocol."""

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        *,
        cache: ResponseCache | None = None,
        max_attempts: int = 3,
    ) -> None:
        self.client = client
        self.cache = cache or ResponseCache(enabled=False)
        self.max_attempts = max_attempts

    def _build_messages(
        self,
        *,
        document: UploadedDocument | None,
        instruction: str,
        extra_blocks: Sequence[dict[str, Any]] = (),
    ) -> list[dict[str, Any]]:
        content: list[dict[str, Any]] = []
        if document is not None:
            # Cache breakpoint after the document: it is the largest stable part
            # of the request and every later agent re-reads exactly this prefix.
            content.append(document.as_content_block(cache=True))
        content.extend(extra_blocks)
        content.append({"type": "text", "text": instruction})
        return [{"role": "user", "content": content}]

    async def extract(
        self,
        *,
        domain_id: str,
        model: str,
        effort: str,
        system: str,
        instruction: str,
        output_model: type[ModelT],
        document: UploadedDocument | None = None,
        extra_blocks: Sequence[dict[str, Any]] = (),
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> Result[ModelT]:
        """One agent call, with caching, retries and usage accounting."""
        key = fingerprint(
            domain_id,
            model,
            effort,
            system,
            instruction,
            output_model.model_json_schema(),
            document.digest if document else "",
        )

        cached = self.cache.get(key)
        if cached is not None:
            return Result(
                data=output_model.model_validate(cached.payload),
                usage=Usage(),
                from_cache=True,
                stop_reason="cache",
            )

        messages = self._build_messages(
            document=document, instruction=instruction, extra_blocks=extra_blocks
        )
        # One breakpoint, on the document. Caching is a prefix match and the
        # render order is system -> messages, so the document's breakpoint
        # already covers the system prompt. A second breakpoint on the system
        # block alone would sit below the minimum cacheable prefix length and
        # buy nothing.
        system_blocks = [{"type": "text", "text": system}]

        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            started = time.monotonic()
            try:
                async with self.client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_blocks,
                    messages=messages,
                    thinking={"type": "adaptive"},
                    output_config={"effort": effort},
                    output_format=output_model,
                ) as stream:
                    response = await stream.get_final_message()
            except RETRYABLE as exc:
                last_error = exc
                if attempt == self.max_attempts:
                    break
                await asyncio.sleep(min(2**attempt, 20))
                continue
            except ValidationError as exc:
                # The SDK parses the JSON as it streams, so a response cut off at
                # the token ceiling surfaces here as invalid JSON rather than as a
                # max_tokens stop reason. Retrying is worth one attempt; failing
                # with the real reason is better than reporting a schema mismatch.
                last_error = LlmError(
                    f"{domain_id}: the response did not parse as {output_model.__name__}. "
                    f"If it was cut off mid-value, the {max_tokens:,}-token ceiling is "
                    f"too low for this domain. Detail: {str(exc)[:200]}"
                )
                if attempt == self.max_attempts:
                    break
                continue
            except anthropic.APIStatusError as exc:
                raise LlmError(
                    f"{domain_id}: the API rejected the request "
                    f"({exc.status_code}): {exc.message}"
                ) from exc

            seconds = time.monotonic() - started
            usage = _usage_from(response, seconds)
            warnings: list[str] = []

            if response.stop_reason == "refusal":
                raise LlmError(
                    f"{domain_id}: the model declined this request "
                    f"({getattr(response, 'stop_details', None)})"
                )
            if response.stop_reason == "max_tokens":
                warnings.append(
                    f"output hit the {max_tokens:,} token ceiling and may be truncated"
                )

            parsed = getattr(response, "parsed_output", None)
            if parsed is None:
                # `output_format` guarantees the first text block is valid JSON
                # for the schema, so fall back to parsing it ourselves rather
                # than discarding a response that was actually fine.
                text = next(
                    (b.text for b in response.content if getattr(b, "type", "") == "text"),
                    "",
                )
                try:
                    parsed = output_model.model_validate_json(text)
                except ValueError as exc:
                    last_error = LlmError(
                        f"{domain_id}: response did not match the expected schema: {exc}"
                    )
                    if attempt == self.max_attempts:
                        break
                    continue

            data = (
                parsed
                if isinstance(parsed, output_model)
                else output_model.model_validate(parsed)
            )
            self.cache.put(key, data.model_dump(mode="json"), domain=domain_id)
            return Result(
                data=data,
                usage=usage,
                stop_reason=str(response.stop_reason or ""),
                warnings=warnings,
            )

        raise LlmError(
            f"{domain_id}: failed after {self.max_attempts} attempts: {last_error}"
        ) from last_error
