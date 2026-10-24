"""Observed header+0x18 consumer predicates, not a complete state-word map.

NBA11/CH compare mask0x3F0 on the current motion. Separate actor-list routines
skip clearing a context pair when bit30 is set. Other consumers remain unknown.
"""


def state_predicates(word):
    """Inspect ONLY native-tested predicates; keep individual tag bits unnamed."""
    if type(word) is not int or not 0 <= word <= 0xFFFFFFFF:
        raise ValueError("Motion state word must be an unsigned32-bit integer")
    return dict(
        mask_0x3f0_nonzero=bool(word & 0x3F0),
        skips_context_pair_clear=bool(word & 0x40000000),
    )


def compare_motion_states(source_word, target_word):
    """Expose behavior differences in explicit authoring assertions, never fix them.

    Predicate equality does not establish a complete flag map or compatible move.
    A deliberate context adaptation may change a predicate; this report retains
    that choice for review rather than silently coercing either input.
    """
    source, target = state_predicates(source_word), state_predicates(target_word)
    changed = [key for key in source if source[key] != target[key]]
    return dict(
        schema=1,
        header_field=0x18,
        source_word=source_word,
        target_word=target_word,
        source_predicates=source,
        target_predicates=target,
        changed_predicates=changed,
        observed_predicates_preserved=not changed,
        source_consumers=["0x471C3C", "0x38CC90"],
        target_consumers=["0x3095F8", "0x23B794"],
        individual_bits_4_to_9_mapped=False,
        complete_state_mapping_established=False,
        target_compatibility_established=False,
    )
