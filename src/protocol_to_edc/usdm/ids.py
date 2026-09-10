"""Identifier minting and cross-reference resolution.

USDM is a graph held together by string ids: `StudyCell.armId` points at a
`StudyArm.id`, `EligibilityCriterion.criterionItemId` at an
`EligibilityCriterionItem.id`, and so on. Agents cannot mint those ids -- they
work one domain at a time and cannot know what the arm agent will call an arm.

So agents emit *placeholders* instead:

    {"id": "@StudyEpoch:screening", "name": "Screening", ...}
    {"armId": "@StudyArm:active", "epochId": "@StudyEpoch:screening"}

A placeholder is `@<Entity>:<key>`, where the key is a slug the agent chooses
from the protocol's own wording. After every fragment is in place, `resolve()`
walks the assembled document once, mints a real id for each distinct
placeholder, and rewrites every reference to it.

Two properties this buys:

* An agent can reference something another agent produced, by key, without
  either of them running first or knowing the other's ids.
* A reference to something nobody produced -- because that domain was disabled,
  or the agent invented it -- cannot be silently written as a valid-looking id.
  It is reported as a dangling reference.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

PLACEHOLDER_RE = re.compile(r"^@([A-Za-z][A-Za-z0-9]*):([A-Za-z0-9._\-]+)$")

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slug(text: str, *, max_length: int = 48) -> str:
    """A stable, readable key from free text: 'Screening Period' -> 'screening-period'."""
    cleaned = _SLUG_RE.sub("-", str(text).strip().lower()).strip("-")
    return (cleaned[:max_length].rstrip("-")) or "unnamed"


def placeholder(entity: str, key: str) -> str:
    return f"@{entity}:{slug(key)}"


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and PLACEHOLDER_RE.match(value) is not None


@dataclass
class Resolution:
    """What `resolve()` did, for the provenance and gap reports."""

    minted: dict[str, str] = field(default_factory=dict)
    dangling: dict[str, list[str]] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.dangling

    def summary(self) -> str:
        entities = ", ".join(f"{k}={v}" for k, v in sorted(self.counts.items()))
        text = f"{len(self.minted)} ids minted ({entities})"
        if self.dangling:
            text += f"; {len(self.dangling)} dangling reference(s)"
        return text


class IdFactory:
    """Mints `Entity_N` ids, matching the convention of published USDM documents."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._assigned: dict[str, str] = {}

    def mint(self, entity: str, key: str) -> str:
        token = placeholder(entity, key)
        if token not in self._assigned:
            self._counters[entity] = self._counters.get(entity, 0) + 1
            self._assigned[token] = f"{entity}_{self._counters[entity]}"
        return self._assigned[token]

    @property
    def assigned(self) -> dict[str, str]:
        return dict(self._assigned)

    @property
    def counts(self) -> dict[str, int]:
        return dict(self._counters)


def _declared_placeholders(node: Any, found: list[str]) -> None:
    """Collect placeholders declared as an object's own `id`, in document order.

    Order matters only for readability: minting in the order objects appear makes
    `StudyArm_1` the first arm in the document rather than whichever arm happened
    to sort first.
    """
    if isinstance(node, dict):
        value = node.get("id")
        if is_placeholder(value) and value not in found:
            found.append(value)
        for child in node.values():
            _declared_placeholders(child, found)
    elif isinstance(node, list):
        for child in node:
            _declared_placeholders(child, found)


def _rewrite(node: Any, mapping: dict[str, str], dangling: dict[str, list[str]], path: str) -> Any:
    if isinstance(node, dict):
        return {
            key: _rewrite(value, mapping, dangling, f"{path}.{key}")
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [
            _rewrite(item, mapping, dangling, f"{path}[{i}]") for i, item in enumerate(node)
        ]
    if is_placeholder(node):
        if node in mapping:
            return mapping[node]
        dangling.setdefault(node, []).append(path)
        return node
    return node


def ensure_ids(node: Any, path: str = "$") -> int:
    """Give every USDM object an `id`, in place.

    Most entities need one, and several -- `Code`, `AliasCode`, `Quantity` --
    are produced by terminology lookup or by an agent describing a value, where
    minting an id at the point of creation would be noise. The id is derived from
    the object's position, which is stable for a given document.

    Returns how many ids were added.
    """
    added = 0
    if isinstance(node, dict):
        kind = node.get("instanceType")
        if isinstance(kind, str) and not node.get("id"):
            node["id"] = placeholder(kind, path.replace("$", "at").replace(".", "-"))
            added += 1
        for key, value in node.items():
            added += ensure_ids(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            added += ensure_ids(item, f"{path}[{index}]")
    return added


def resolve(document: Any) -> tuple[Any, Resolution]:
    """Replace every placeholder with a minted id.

    Ids are minted only for placeholders that some object actually *declares* as
    its own `id`. A reference to a placeholder nobody declared is left in place
    and reported as dangling -- that is the signal that a disabled domain was
    referenced, or that an agent referred to something it did not create.
    """
    declared: list[str] = []
    _declared_placeholders(document, declared)

    factory = IdFactory()
    for token in declared:
        match = PLACEHOLDER_RE.match(token)
        if match:
            factory.mint(match.group(1), match.group(2))

    dangling: dict[str, list[str]] = {}
    rewritten = _rewrite(document, factory.assigned, dangling, "$")

    return rewritten, Resolution(
        minted=factory.assigned, dangling=dangling, counts=factory.counts
    )
