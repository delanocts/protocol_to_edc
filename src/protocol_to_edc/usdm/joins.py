"""Entities that are joins over other domains, not extractions from the protocol.

`InterventionalStudyDesign` requires `studyCells`, and every `StudyCell` requires
an `armId`, an `epochId` and `elementIds`. None of the eight domains owns those:
a study cell is the intersection of an arm and an epoch, which is a cross product
of what the arm agent and the epoch agent produced.

Asking a model to emit that grid would be asking it to do arithmetic it has no
special insight into, and to keep two other agents' outputs consistent. So it is
computed here instead. This is the "code builds" half of the split: the model
decides what the arms and epochs *are*, and this module derives the grid.

`StudyElement` gets the same treatment. An element is what a subject receives
during one cell; with no dedicated agent, one element is derived per arm so that
`StudyCell.elementIds` can be satisfied and the document stays navigable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import ids


@dataclass
class JoinResult:
    study_cells: list[dict[str, Any]]
    study_elements: list[dict[str, Any]]
    note: str

    @property
    def count(self) -> int:
        return len(self.study_cells)


def _placeholder_key(entity_id: str) -> str:
    """'@StudyArm:active' -> 'active'; a real id is used as its own key."""
    match = ids.PLACEHOLDER_RE.match(entity_id or "")
    return match.group(2) if match else ids.slug(entity_id or "unknown")


def build_study_cells(
    arms: list[dict[str, Any]],
    epochs: list[dict[str, Any]],
    *,
    elements: list[dict[str, Any]] | None = None,
) -> JoinResult:
    """Derive the arm x epoch grid.

    One cell per (arm, epoch) pair, which is what a parallel-group design means
    and what the reference document contains: 3 arms x 5 epochs = 15 cells.

    If either side is missing -- its domain was disabled, or the protocol did not
    yield any -- no cells are produced and the reason is recorded rather than
    guessed at.
    """
    if not arms or not epochs:
        missing = " and ".join(
            part for part, value in (("arms", arms), ("epochs", epochs)) if not value
        )
        return JoinResult(
            study_cells=[],
            study_elements=list(elements or []),
            note=f"no study cells derived: {missing} unavailable",
        )

    derived_elements = list(elements or [])
    if not derived_elements:
        for arm in arms:
            arm_key = _placeholder_key(arm.get("id", ""))
            arm_name = arm.get("name") or arm_key
            derived_elements.append(
                {
                    "id": ids.placeholder("StudyElement", arm_key),
                    "name": arm_name,
                    "label": arm.get("label") or arm_name,
                    "description": (
                        f"Intervention received by subjects in the {arm_name} arm. "
                        "Derived from the study arms; not stated separately in the protocol."
                    ),
                    "instanceType": "StudyElement",
                }
            )

    elements_by_arm = {
        _placeholder_key(element["id"]): element["id"] for element in derived_elements
    }

    cells: list[dict[str, Any]] = []
    for arm in arms:
        arm_id = arm.get("id", "")
        arm_key = _placeholder_key(arm_id)
        element_id = elements_by_arm.get(arm_key)
        for epoch in epochs:
            epoch_id = epoch.get("id", "")
            cells.append(
                {
                    "id": ids.placeholder(
                        "StudyCell", f"{arm_key}-{_placeholder_key(epoch_id)}"
                    ),
                    "armId": arm_id,
                    "epochId": epoch_id,
                    "elementIds": [element_id] if element_id else [],
                    "instanceType": "StudyCell",
                }
            )

    return JoinResult(
        study_cells=cells,
        study_elements=derived_elements,
        note=(
            f"{len(cells)} study cells derived from {len(arms)} arms x "
            f"{len(epochs)} epochs; {len(derived_elements)} study elements derived per arm"
        ),
    )
