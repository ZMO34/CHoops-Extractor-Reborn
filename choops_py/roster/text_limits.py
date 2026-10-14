"""Verified game text-entry capacities, excluding the terminating UTF-16 NUL.

These are editor input limits, not proof of a smaller runtime string ceiling.
Unmapped fields have no invented per-field limit; payload/pointer bounds apply.
"""
INPUT_LIMITS={('players','first_name'):16,('players','last_name'):16}

# Edit Schools save path 0x6D09FC–0x6D0C54 resolves temporary strings to
# anchor +0/+8, +4, +0xC, +0x16C and +0x168 respectively (team bias 0x30).
INPUT_LIMITS.update({('teams','short_name'):16,('teams','school_name'):16,
    ('teams','abbreviation'):4,('teams','mascot_plural'):16,
    ('teams','event_name'):64,('teams','student_section'):32,
    ('arenas','arena_name'):15})
