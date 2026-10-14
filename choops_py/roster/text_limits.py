"""Verified game text-entry capacities, excluding the terminating UTF-16 NUL.

These are editor input limits, not proof of a smaller runtime string ceiling.
Unmapped fields have no invented per-field limit; payload/pointer bounds apply.
"""
INPUT_LIMITS={('players','first_name'):16,('players','last_name'):16}
