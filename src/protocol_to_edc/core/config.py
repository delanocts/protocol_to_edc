"""Layered configuration.

Precedence, lowest to highest:

    config/default.yaml  ->  studies/<ID>/study.yaml  ->  runtime overrides (CLI / web UI)

Secrets never appear in any of those layers; the Anthropic API key is read from
the project-root `.env` (or the ambient environment) and is never persisted back.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

from . import paths

OutputMode = Literal["partial", "strict", "stub"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]


class ConfigError(ValueError):
    """Configuration that cannot be used as given."""


class UsdmConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    version: str = "4.0.0"
    output_mode: OutputMode = "partial"
    # `validate` is the YAML key; the attribute is renamed so it does not shadow
    # pydantic's own BaseModel.validate.
    validate_schema: bool = Field(default=True, alias="validate")
    core_rules: bool = True

    @field_validator("version")
    @classmethod
    def _known_version(cls, v: str) -> str:
        if not paths.usdm_resource_dir(v).is_dir():
            available = ", ".join(paths.available_usdm_versions()) or "none downloaded"
            raise ValueError(
                f"No USDM reference set for version {v!r} under {paths.USDM_RESOURCES}. "
                f"Available: {available}."
            )
        return v


class LlmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = "claude-opus-5"
    effort: Effort = "high"
    max_concurrency: int = Field(default=4, ge=1, le=16)
    cache_protocol: bool = True
    reuse_cached_runs: bool = True


class QcConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    require_citations: bool = True


class DomainToggle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    model: str | None = None
    effort: Effort | None = None


class StudyMeta(BaseModel):
    """Free-form study metadata.

    Seeds the Study/StudyVersion agent as a hint; the protocol itself always wins
    over anything asserted here.
    """

    model_config = ConfigDict(extra="allow")

    id: str = ""
    protocol_number: str = ""
    protocol_version: str = ""
    protocol_date: str = ""
    registry_id: str = ""
    title: str = ""
    sponsor: str = ""
    phase: str = ""
    therapeutic_area: str = ""


class InputConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol_pdf: str = ""
    reference_files: list[str] = Field(default_factory=list)


class Settings(BaseModel):
    """Fully resolved configuration for one run."""

    model_config = ConfigDict(extra="forbid")

    study: StudyMeta = Field(default_factory=StudyMeta)
    input: InputConfig = Field(default_factory=InputConfig)
    usdm: UsdmConfig = Field(default_factory=UsdmConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    domains: dict[str, DomainToggle] = Field(default_factory=dict)
    qc: QcConfig = Field(default_factory=QcConfig)

    # Not read from YAML; filled in by `load`.
    study_id: str = ""

    @property
    def paths(self) -> paths.StudyPaths:
        return paths.for_study(self.study_id)

    def domain(self, domain_id: str) -> DomainToggle:
        return self.domains.get(domain_id, DomainToggle())

    def is_enabled(self, domain_id: str) -> bool:
        return self.domain(domain_id).enabled

    def enabled_domains(self) -> list[str]:
        return [d for d, t in self.domains.items() if t.enabled]

    def model_for(self, domain_id: str) -> str:
        return self.domain(domain_id).model or self.llm.model

    def effort_for(self, domain_id: str) -> Effort:
        return self.domain(domain_id).effort or self.llm.effort

    def protocol_path(self) -> Path:
        if not self.input.protocol_pdf:
            raise ConfigError(
                f"Study {self.study_id!r} has no input.protocol_pdf in study.yaml."
            )
        path = self.paths.resolve_input(self.input.protocol_pdf)
        if not path.is_file():
            raise ConfigError(f"Protocol PDF not found: {path}")
        return path


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping, got {type(data).__name__}")
    return data


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursive merge.

    A null in the overlay means "inherit", not "set to null", so a study.yaml can
    leave `model: null` in place and still fall through to the global default.
    """
    out = copy.deepcopy(base)
    for key, value in overlay.items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_api_key() -> str:
    """Read ANTHROPIC_API_KEY from the project-root .env or the environment."""
    load_dotenv(paths.PROJECT_ROOT / ".env", override=False)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise ConfigError(
            f"ANTHROPIC_API_KEY is not set. Copy {paths.PROJECT_ROOT / '.env.example'} "
            "to .env and fill it in."
        )
    return key


def load(study_id: str, overrides: dict[str, Any] | None = None) -> Settings:
    """Resolve settings for one study across all layers."""
    paths.validate_study_id(study_id)
    sp = paths.for_study(study_id)
    if not sp.root.is_dir():
        known = ", ".join(paths.list_studies()) or "none"
        raise ConfigError(f"No study directory {sp.root}. Existing studies: {known}.")

    merged = _read_yaml(paths.DEFAULT_CONFIG)
    merged = _deep_merge(merged, _read_yaml(sp.config_file))
    if overrides:
        merged = _deep_merge(merged, overrides)
    merged.pop("study_id", None)

    try:
        settings = Settings.model_validate({**merged, "study_id": study_id})
    except Exception as exc:  # pydantic ValidationError -> a readable message
        raise ConfigError(f"Invalid configuration for study {study_id!r}:\n{exc}") from exc

    declared = settings.study.id
    if declared and declared != study_id:
        raise ConfigError(
            f"{sp.config_file} declares study.id={declared!r} but lives in a folder "
            f"named {study_id!r}. Make them match."
        )
    return settings
