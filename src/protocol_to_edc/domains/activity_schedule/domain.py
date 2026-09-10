"""Domain 8 -- Activity and ScheduledActivityInstance.

The Schedule of Activities: the visits, the assessments performed at each, and
the timeline that puts them in order. This is the densest domain and the one the
whole EDC build hangs off, since each encounter becomes a folder and each
activity a form.

USDM splits the grid into four parts that have to agree with each other:

* `Activity` -- an assessment, defined once regardless of how often it recurs.
* `Encounter` -- a visit, defined once.
* `ScheduledActivityInstance` -- one cell of the grid: *this* visit performs
  *these* activities, in *this* epoch. This is where the ticks in the SoA table
  actually land.
* `Timing` -- when an instance happens, relative to another instance, with its
  visit window.

`Timing` is the fiddly one. It is relative, not absolute: every timing points at
the instance it is measured from, so 'Day 8, +/- 2 days' is a timing of value
'P7D' from the Day 1 instance with a window of -2 to +2 days. ISO 8601 durations
are what the value takes, which is why the prompt asks for them explicitly.

This domain depends on `epoch` and `study_arm`, so it can attach each visit to
the epoch it falls in rather than guessing.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ...usdm import ids
from ..base import DomainContext, compose_prompt


class VisitRef(Grounded):
    """One visit, with the activities performed at it.

    The schedule is returned as a flat list of visits rather than as a grid
    object holding both an activity list and a visit list. Two sibling arrays of
    objects nested inside a third was rejected by the structured-outputs API as
    "Schema is too complex", regardless of the schema's size -- the limit is on
    structure, not bytes.

    Flattening costs nothing real. The activity list is recoverable as the union
    of every visit's `activity_names`, which is also the more robust shape: a
    truncated response still yields whole visits rather than a grid missing its
    columns.
    """

    name: str = Field(description="The visit's name, e.g. 'Visit 1' or 'Screening'.")
    label: str = Field(default="", description="A display label, e.g. 'Day 1'.")
    epoch_name: str = Field(
        default="",
        description=(
            "The epoch this visit falls in, named exactly as the epoch domain "
            "named it, so the two can be linked."
        ),
    )
    encounter_type: str = Field(
        default="", description="Visit type, in the permitted wording."
    )
    contact_modes: list[str] = Field(
        default_factory=list,
        description="How contact is made -- in person, telephone -- permitted wording.",
    )
    study_day: str = Field(
        default="",
        description="The study day or window as the SoA prints it, e.g. 'Day 1' or 'Day 8'.",
    )
    timing_value_iso: str = Field(
        default="",
        description=(
            "The visit's offset from the previous visit as an ISO 8601 duration, "
            "e.g. 'P7D' for one week later, 'P0D' for the anchor visit. Leave "
            "empty if the protocol does not support computing it."
        ),
    )
    window_lower_iso: str = Field(
        default="",
        description="Lower visit window as an ISO 8601 duration, e.g. '-P2D' for minus 2 days.",
    )
    window_upper_iso: str = Field(
        default="", description="Upper visit window, e.g. 'P2D' for plus 2 days."
    )
    window_label: str = Field(
        default="", description="The window as printed, e.g. '+/- 2 days'."
    )
    activity_names: list[str] = Field(
        default_factory=list,
        description=(
            "Names of every activity marked as performed at this visit, matching "
            "the activity names exactly. This is the ticked column of the SoA."
        ),
    )
    is_conditional: bool = Field(
        default=False,
        description="True when a footnote makes this visit or its activities conditional.",
    )
    footnotes: list[str] = Field(
        default_factory=list,
        description="Footnote text that qualifies this visit, verbatim.",
    )
    source_page: int = Field(
        default=0, description="PDF page of the schedule table this column came from."
    )


PAYLOAD_MODEL = VisitRef
OutputModel = DomainOutput[VisitRef]


def build_prompt(ctx: DomainContext) -> str:
    epochs = _upstream_names(ctx, "epoch")
    epoch_note = (
        "The epoch agent found these epochs; use these exact names in `epoch_name`:\n  "
        + "\n  ".join(f"- {name}" for name in epochs)
        if epochs
        else "The epoch domain produced no epochs, so leave `epoch_name` empty."
    )

    return compose_prompt(
        ctx,
        task=(
            "Read the Schedule of Activities table and reproduce it as structured "
            "data.\n\n"
            "Return one item per visit column, in the order the table prints them. "
            "For each visit, list in `activity_names` exactly those assessments the "
            "table marks as performed at it, naming each one exactly as its row is "
            "labelled so the same assessment reads identically across visits. That "
            "mapping is the substance of this task -- the table's ticks are what an "
            "EDC build is generated from."
        ),
        guidance=f"""\
{epoch_note}

Work the table structurally. Read the column headers to get the visits, the row \
labels to get the activities, and then, for each visit, which rows are marked. \
A mark may be an X, a dot, a filled cell or a footnote reference; any of them \
means performed.

Do not summarise. Every row is an activity, every column a visit. A schedule with \
40 rows and 12 visits produces 40 activities and 12 visits, and the marks are \
however many they are. Truncating this table is the most damaging error available \
in this pipeline, because the omission is invisible downstream.

Read the footnotes. They carry the conditions that the grid cannot: activities \
done only for a subset, visits that only happen on early termination, windows \
that differ from the default, assessments repeated at times within a visit. Put \
the footnote text verbatim in `footnotes` and set `is_conditional` when a \
footnote makes a visit or its contents conditional.

Timings are relative and expressed as ISO 8601 durations. The anchor visit -- \
usually Day 1 or randomisation -- is 'P0D'. A visit one week later is 'P7D' from \
the previous one. A window of plus or minus two days is `window_lower_iso` '-P2D' \
and `window_upper_iso` 'P2D'. Where the protocol gives a study day but no basis \
for computing an offset, leave the ISO fields empty, keep the printed day in \
`study_day`, and record a gap rather than inventing a duration.

Where the schedule is cycle-based ('Day 1 of each 21-day cycle'), describe the \
cycle in the visit description and record a gap: repeating cycles need a decision \
from a reviewer about how many to expand, and guessing is not useful.

If the protocol has more than one schedule table -- a main one and a follow-up or \
early-termination one -- extract the main one and record the others as gaps \
naming their page, rather than merging them.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    if not output.items:
        return {}

    # Activities are the union of what the visits reference, in first-seen order.
    # Each is defined once no matter how many visits perform it.
    activities: list[dict[str, Any]] = []
    known_activities: dict[str, str] = {}
    for visit in output.items:
        for name in visit.activity_names:
            key = ids.slug(name)
            if not name or key in known_activities:
                continue
            placeholder = ctx.placeholder("Activity", key)
            known_activities[key] = placeholder
            activities.append(
                {
                    "id": placeholder,
                    "name": name,
                    "label": name,
                    "description": name,
                    "instanceType": "Activity",
                }
            )
    _chain(activities)

    epoch_ids = _upstream_epoch_ids(ctx)
    encounters: list[dict[str, Any]] = []
    instances: list[dict[str, Any]] = []
    timings: list[dict[str, Any]] = []

    for position, visit in enumerate(output.items, start=1):
        if not visit.name:
            continue
        key = ids.slug(visit.name)
        encounters.append(
            {
                "id": ctx.placeholder("Encounter", key),
                "name": visit.name,
                "label": visit.label or visit.study_day or visit.name,
                "description": visit.study_day or visit.name,
                "type": ctx.resolve_code("Encounter", "type", visit.encounter_type or "Visit")
                or ctx.terminology.sponsor_code(visit.encounter_type or "Visit"),
                "contactModes": [
                    code
                    for code in (
                        ctx.resolve_code("Encounter", "contactModes", mode)
                        for mode in visit.contact_modes
                    )
                    if code
                ],
                "scheduledAtId": ctx.placeholder("ScheduledActivityInstance", key),
                "instanceType": "Encounter",
            }
        )

        matched = [
            known_activities[ids.slug(name)]
            for name in visit.activity_names
            if ids.slug(name) in known_activities
        ]
        instance: dict[str, Any] = {
            "id": ctx.placeholder("ScheduledActivityInstance", key),
            "name": visit.name,
            "label": visit.label or visit.name,
            "description": " ".join(visit.footnotes) or visit.study_day or visit.name,
            "encounterId": ctx.placeholder("Encounter", key),
            "activityIds": matched,
            "instanceType": "ScheduledActivityInstance",
        }
        epoch_id = epoch_ids.get(ids.slug(visit.epoch_name))
        if epoch_id:
            instance["epochId"] = epoch_id
        instances.append(instance)

        timing = _timing(ctx, visit, key, position, instances)
        if timing:
            timings.append(timing)

    _chain(encounters)

    if not (activities or encounters):
        return {}

    timeline = {
        "id": ctx.placeholder("ScheduleTimeline", "main"),
        "name": "Main Timeline",
        "label": "Main Timeline",
        "description": "Schedule of activities as stated in the protocol.",
        "mainTimeline": True,
        "entryCondition": "Subject enrolled in the study.",
        "entryId": instances[0]["id"] if instances else "",
        "instances": instances,
        "timings": timings,
        "instanceType": "ScheduleTimeline",
    }

    fragment: dict[str, Any] = {}
    if activities:
        fragment["studyDesign.activities"] = activities
    if encounters:
        fragment["studyDesign.encounters"] = encounters
    if instances:
        fragment["studyDesign.scheduleTimelines"] = [timeline]
    return fragment


def _timing(
    ctx: DomainContext,
    visit: VisitRef,
    key: str,
    position: int,
    instances: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """A Timing for this visit, if the agent gave enough to build a valid one.

    Every required field must be present or the object is invalid, so a partial
    timing is dropped rather than half-built -- the study day survives on the
    encounter either way.
    """
    if not visit.timing_value_iso:
        return None

    anchor = instances[position - 2]["id"] if position > 1 else instances[0]["id"]
    timing: dict[str, Any] = {
        "id": ctx.placeholder("Timing", key),
        "name": f"{visit.name} timing",
        "label": visit.study_day or visit.name,
        "description": visit.study_day or visit.name,
        "type": ctx.resolve_code("Timing", "type", "After" if position > 1 else "Fixed Reference")
        or ctx.terminology.sponsor_code("After"),
        "value": visit.timing_value_iso,
        "valueLabel": visit.study_day or visit.timing_value_iso,
        "relativeToFrom": ctx.resolve_code("Timing", "relativeToFrom", "Start to Start")
        or ctx.terminology.sponsor_code("Start to Start"),
        "relativeFromScheduledInstanceId": ctx.placeholder(
            "ScheduledActivityInstance", key
        ),
        "instanceType": "Timing",
    }
    if position > 1:
        timing["relativeToScheduledInstanceId"] = anchor
    if visit.window_lower_iso:
        timing["windowLower"] = visit.window_lower_iso
    if visit.window_upper_iso:
        timing["windowUpper"] = visit.window_upper_iso
    if visit.window_label:
        timing["windowLabel"] = visit.window_label
    return timing


def _chain(items: list[dict[str, Any]]) -> None:
    """Link a list with previousId / nextId, as USDM expects for ordered entities."""
    for index, entry in enumerate(items):
        if index > 0:
            entry["previousId"] = items[index - 1]["id"]
        if index < len(items) - 1:
            entry["nextId"] = items[index + 1]["id"]


def _upstream_names(ctx: DomainContext, domain_id: str) -> list[str]:
    output = ctx.upstream.get(domain_id)
    if output is None:
        return []
    return [getattr(item, "name", "") for item in getattr(output, "items", []) if
            getattr(item, "name", "")]


def _upstream_epoch_ids(ctx: DomainContext) -> dict[str, str]:
    """Map epoch name slug -> the placeholder the epoch domain used for it."""
    return {
        ids.slug(name): ctx.placeholder("StudyEpoch", ids.slug(name))
        for name in _upstream_names(ctx, "epoch")
    }
