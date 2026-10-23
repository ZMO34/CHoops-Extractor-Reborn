"""Read-only 0x5BDCD8 poll/ranking component, from native save/load evidence."""

from hashlib import sha256
from struct import unpack_from

from .legacy_backend import _reference, _roster_tables

POLL_STATE_SIZE = 0x1D54


def inspect_poll_section(section, roster):
    if not isinstance(section, (bytes, bytearray)) or len(section) != POLL_STATE_SIZE:
        raise ValueError("Native poll component must be exactly 0x1D54 bytes")
    teams = _roster_tables(roster)["teams"]
    week = unpack_from(">i", section)[0]
    if not -1 <= week < 20:
        raise ValueError("Media poll index is outside its 20 stored snapshots")
    issues = []

    def read_rows(name, start, count):
        seen, rows = set(), []
        for slot in range(count):
            pointer, raw = unpack_from(">II", section, start + slot * 8)
            if pointer == 0:
                continue
            ref = _reference(pointer, teams, 48)
            if ref["status"] != "resolved":
                issues.append(dict(table=name, slot=slot, issue=ref["status"]))
            elif ref["index"] in seen:
                issues.append(dict(table=name, slot=slot, issue="duplicate_school"))
            seen.add(ref["index"])
            rows.append(dict(rank=slot + 1, school=ref, raw_value=raw))
        return rows

    # Native mode labels: 0 Media, 1 Coaches, 2 Mid Major, 3 RPI, 4 Conf Champ.
    # Native 0x5BDA8C returns 25 for modes 0..2; the 26th stored row is not
    # silently promoted to a displayed Top-25 rank.
    media = read_rows("media", 0xC94 + week * 0xD0, 25) if week >= 0 else []
    coaches = read_rows("coaches", 0xAF4, 25)
    mid_major = read_rows("mid_major", 0xBC4, 25)
    rpi = read_rows("rpi", 4, min(teams[1], 350))
    if teams[1] > 350:
        issues.append(dict(table="rpi", issue="team_count_exceeds_350_stored_rows"))
    return dict(
        schema=1,
        media_snapshot_index=week,
        current_media=media,
        coaches=coaches,
        mid_major=mid_major,
        rpi=rpi,
        media_snapshot_available=week >= 0 and bool(media),
        media_history_sha256=sha256(section[0xC94:0x1CD4]).hexdigest(),
        conference_champion_region_sha256=sha256(section[0x1CD4:]).hexdigest(),
        issue_count=len(issues),
        issues=issues,
        phase_and_roster_correspondence_verified=False,
        raw_value_semantics_complete=False,
        native_portal_installed=False,
    )
