"""NBA11 complete shot-family preparation, before native contextual fallbacks.

Four reference pairs survive intact. This is not a two-pointer CH registration
or a claim that their basketball roles and fallback graphs are interchangeable.
"""

from ..formats.standard_iff_writer import record_blocks
from .donor_registry import COLLECTION, inspect_entries
from .signature_motion import translate_signature_motion
from .target_motion import MAX_IMAGE, relocate_target_image


def select_shot_pairs(entry, selector_bit):
    """Model native 0x653650/0x6537C8 selection before contextual fallbacks."""
    if type(selector_bit) is not int or selector_bit not in (0, 1):
        raise ValueError("Supply the player +0xCC selector bit as integer 0 or 1")
    if not isinstance(entry, dict) or entry.get("category") != 0:
        raise ValueError("Choose a category-zero shot family")
    refs = entry.get("references")
    if (
        not isinstance(refs, list)
        or len(refs) != 8
        or any(
            not isinstance(r, dict) or type(r.get("slot")) is not int or r["slot"] != i
            for i, r in enumerate(refs)
        )
    ):
        raise ValueError("A shot family needs all eight ordered reference slots")
    slots = list(range(0 if selector_bit else 1, 8, 2))
    return dict(
        selected_slots=slots,
        resource_ids=[refs[i]["resource_id"] for i in slots],
        disabled_or_empty=[refs[i]["empty"] or refs[i]["raw_kind"] == 5 for i in slots],
        source_selection="four-pairs-before-contextual-fallbacks",
        contextual_fallbacks_established=False,
        target_pair_roles_established=False,
        gameplay_ready=False,
    )


def _entry(source, bank, collection, index, category=0):
    if (
        any(type(v) is not int or v < 0 for v in (bank, collection, index))
        or bank >= len(source.banks)
        or collection >= len(source.banks[bank].records)
    ):
        raise ValueError("Choose existing shot collection/entry indices")
    iff = source.banks[bank]
    record = iff.records[collection]
    if record["type_hash"] != COLLECTION or len(list(iff.spans(record))) != 1:
        raise ValueError("Shot family requires one complete typed collection record")
    blocks = record_blocks(iff, record)
    if len(blocks) != 1:
        raise ValueError("Shot collection must occupy one decoded block")
    rows = inspect_entries(blocks[0][3])
    if index >= len(rows) or rows[index]["category"] != category:
        raise ValueError("Choose an existing entry in the required registry category")
    return rows[index]


def prepare_shot_family(
    source,
    bank,
    collection,
    index,
    donor_elf,
    target_elf,
    motion_contracts,
    event_contract,
    *,
    budget=MAX_IMAGE,
):
    """Prepare every nonempty direct motion, retaining all eight source slots.

    Contracts use exact `bank:record` keys, with `metadata` and optional
    `auxiliary` maps per distinct header. Missing/group dependencies reject the
    whole result; empty and explicitly disabled slots remain explicit nulls.
    Native contextual fallback/selection and row metadata are not synthesized.
    """
    if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
        raise ValueError("Shot family budget must be 64 bytes..16 MiB")
    row = _entry(source, bank, collection, index)
    if row["unparsed_tail_bytes"]:
        raise ValueError("Unknown shot family tail bytes block preparation")
    locations = []
    for ref in row["references"]:
        if ref["empty"] or ref["raw_kind"] == 5:
            locations.append(None)
            continue
        if ref["raw_kind"] != 0:
            raise ValueError("Shot group-member translation is not established")
        candidates = source.index.get(ref["resource_id"], [])
        if len(candidates) != 1:
            raise ValueError("Shot reference is missing or ambiguous across banks")
        locations.append(candidates[0])
    output, offsets, components, header_indices = _compose_headers(
        source,
        locations,
        donor_elf,
        target_elf,
        motion_contracts,
        event_contract,
        budget,
    )
    slots = [None if loc is None else header_indices[loc] for loc in locations]
    return bytes(output), dict(
        schema=1,
        source_bank=bank,
        collection_record=collection,
        entry_index=index,
        source_banks_sha256=list(source.fingerprints),
        source_lookup_key=row["raw_lookup_key"],
        intended_port_scope="on-court-5v5",
        source_context="four-pair-gameplay-sequence-0x49FB00",
        target_compatibility_established=False,
        source_control_word=row["shot_family"]["control_word"],
        control_word_target_mapping_established=False,
        header_offsets=offsets,
        bytes=len(output),
        source_slots=[
            dict(
                slot=i,
                resource_id=ref["resource_id"],
                raw_kind=ref["raw_kind"],
                header_index=slots[i],
            )
            for i, ref in enumerate(row["references"])
        ],
        pairs=[slots[i : i + 2] for i in range(0, 8, 2)],
        components=components,
        all_source_slots_accounted_for=True,
        original_pair_presence_by_selector={
            str(bit): [
                not empty for empty in select_shot_pairs(row, bit)["disabled_or_empty"]
            ]
            for bit in (0, 1)
        },
        fallback_resources_included=False,
        native_cache_key_fields=["player-identity", "player+0xD4"],
        fallback_requirements={
            "pair0": "eight-row-weighted-pool-if-empty",
            "pair1": "player+0x1C-modulo-18-if-empty-also-replaces-pair2",
            "pair2": "lane-specific-fixed-header-if-still-empty",
            "pair3": "lane-specific-fixed-header-if-empty-or-context-predicate",
            "control_value": "reset-to-zero-whenever-pair3-is-replaced",
            "presence_flags": "original-pair0-and-pair1-presence-before-fallbacks",
        },
        selected_slots_when_zero=select_shot_pairs(row, 0)["selected_slots"],
        selected_slots_when_one=select_shot_pairs(row, 1)["selected_slots"],
        native_family_selection_installed=False,
        target_playback_metadata_established=False,
        gameplay_ready=False,
    )


def _compose_headers(
    source, locations, donor_elf, target_elf, motion_contracts, event_contract, budget
):
    required = {f"{loc[0]}:{loc[1]}" for loc in locations if loc is not None}
    if not isinstance(motion_contracts, dict) or set(motion_contracts) != required:
        raise ValueError("Contracts must cover exactly every distinct family header")
    if any(
        not isinstance(v, dict)
        or "metadata" not in v
        or set(v) - {"metadata", "auxiliary"}
        for v in motion_contracts.values()
    ):
        raise ValueError("Family header contracts require explicit metadata")
    output = bytearray()
    offsets, components, header_indices = [], [], {}
    for loc in locations:
        if loc is None or loc in header_indices:
            continue
        at = (len(output) + 15) & ~15
        remaining = budget - at
        if remaining < 64:
            raise ValueError("Complete shot family exceeds byte budget")
        c = motion_contracts[f"{loc[0]}:{loc[1]}"]
        image, report = translate_signature_motion(
            source,
            *loc,
            donor_elf,
            target_elf,
            c["metadata"],
            event_contract,
            auxiliary_contracts=c.get("auxiliary"),
            budget=remaining,
        )
        output.extend(bytes(at - len(output)))
        output.extend(image)
        header_indices[loc] = len(offsets)
        offsets.append(at)
        components.append(dict(source_bank=loc[0], source_record=loc[1], report=report))
    if not offsets:
        raise ValueError("Shot family has no materializable motion headers")
    native = relocate_target_image(output, offsets, 0x20000000, source_state="relative")
    if (
        relocate_target_image(native, offsets, 0x20000000, source_state="native")
        != output
    ):
        raise ValueError("Complete family relocation inverse failed")
    return bytes(output), offsets, components, header_indices
