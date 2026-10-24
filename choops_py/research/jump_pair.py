"""Prepare category-14 paired NBA11 motions without losing row metadata.

Provider selector 20 selects registry category 14; selector/category zero is a
separate four-pair sequence family. This API does not install gameplay dispatch.
"""

from .shot_family import _compose_headers, _entry
from .target_motion import MAX_IMAGE


def prepare_jump_pair(
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
    """Prepare both direct headers and preserve every unclassified metadata word.

    Per-motion contracts establish the same bounded component transport as the
    complete-family path. Registry metadata is retained in the manifest only;
    missing target row semantics block any claim of playable registration.
    """
    if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
        raise ValueError("Pair budget must be 64 bytes..16 MiB")
    row = _entry(source, bank, collection, index, category=14)
    if row["tail_bytes"] != 36 or row["paired_jump_shot"] is None:
        raise ValueError("Unknown paired jump-shot payload layout blocks preparation")
    locations = []
    for ref in row["references"]:
        if ref["empty"] or ref["raw_kind"] != 0:
            raise ValueError("Both jump-shot lanes require established direct motions")
        candidates = source.index.get(ref["resource_id"], [])
        if len(candidates) != 1:
            raise ValueError("Jump-shot reference is missing or ambiguous")
        locations.append(candidates[0])
    image, offsets, components, indices = _compose_headers(
        source,
        locations,
        donor_elf,
        target_elf,
        motion_contracts,
        event_contract,
        budget,
    )
    return image, dict(
        schema=1,
        registry_category=14,
        provider_selector=20,
        source_bank=bank,
        collection_record=collection,
        entry_index=index,
        source_banks_sha256=list(source.fingerprints),
        source_lookup_key=row["raw_lookup_key"],
        header_offsets=offsets,
        bytes=len(image),
        source_slots=[
            dict(slot=i, resource_id=ref["resource_id"], header_index=indices[loc])
            for i, (ref, loc) in enumerate(zip(row["references"], locations))
        ],
        header_indices_when_one=[indices[locations[0]]],
        header_indices_when_zero=[indices[locations[1]]],
        source_payload_tail_words=list(row["paired_jump_shot"]["payload_tail_words"]),
        components=components,
        target_registration_metadata_established=False,
        native_target_dispatch_installed=False,
        gameplay_ready=False,
    )
