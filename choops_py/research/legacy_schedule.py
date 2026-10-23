"""Roster-backed fixtures and native conference tournament diagnostics only."""

from collections import Counter
from hashlib import sha256
from struct import unpack_from

from ..roster.schema import CONFERENCE_TOURNAMENT_CAPACITY
from .legacy_backend import _roster_tables
from .legacy_history import directory


def inspect_conference_schedule(payload: bytes):
    tables = _roster_tables(payload)
    games_base, count, stride = directory(payload, 0x30, 20, 65535, tables)
    team_base, teams, team_stride = tables["teams"]
    conf_base, conferences, conf_stride = tables["conferences"]
    membership, rows = {}, []
    for index in range(conferences):
        at = conf_base + index * conf_stride
        size = unpack_from(">H", payload, at + 0x870)[0]
        if size > 100:
            raise ValueError("Conference member count exceeds 100 stored references")
        members, issues = [], []
        for slot in range(size):
            field = at + 0x6E0 + slot * 4
            delta = unpack_from(">i", payload, field)[0]
            q, rem = divmod(field + delta - 1 - team_base - 48, team_stride)
            if delta in (0, -1) or rem or not 0 <= q < teams:
                issues.append(f"invalid_member_reference_{slot}")
                continue
            if q in members:
                issues.append("duplicate_conference_member")
            members.append(q)
            membership.setdefault(q, []).append(index)
            team_field = team_base + q * team_stride + 0x48
            backlink = team_field + unpack_from(">i", payload, team_field)[0] - 1
            if backlink != at:
                issues.append(f"member_{q}_backlink_mismatch")
        tournament, slots = unpack_from(">HH", payload, at + 0x1A)
        if tournament == 96:
            issues.append("native_tournament_event_skipped")
        elif tournament > 96:
            issues.append("tournament_index_outside_native_table")
        if slots == 0:
            issues.append("zero_tournament_entrants")
        if slots > len(set(members)):
            issues.append("tournament_entrants_exceed_members")
        if slots > CONFERENCE_TOURNAMENT_CAPACITY:
            issues.append("tournament_entrants_exceed_native_capacity")
        if index == 13:
            issues.append("native_independent_champion_policy")
        elif index == 14:
            issues.append("native_ivy_regular_season_champion_policy")
        rows.append(
            dict(
                conference_index=index,
                native_season_scope=index < 32,
                declared_members=size,
                team_indices=members,
                tournament_index=tournament,
                tournament_entrants=slots,
                tournament_event_enabled=tournament < 96,
                tournament_day_raw=unpack_from(">H", payload, at + 0x1E)[0],
                issues=issues,
                fixture_count=0,
                per_team=Counter(),
            )
        )
    games, invalid = [], []
    blank = 0
    for index in range(count):
        at = games_base + index * stride
        if not any(payload[at : at + stride]):
            blank += 1
            continue
        key, home, away = unpack_from(">Ihh", payload, at)
        if not 0 <= home < teams or not 0 <= away < teams or home == away:
            invalid.append(dict(slot=index, game_key_raw=key, home=home, away=away))
            continue
        games.append((home, away))
        common = set(membership.get(home, ())).intersection(membership.get(away, ()))
        for conference in common:
            row = rows[conference]
            row["fixture_count"] += 1
            row["per_team"].update((home, away))
    for row in rows:
        counts = row.pop("per_team")
        row["team_fixture_counts"] = [
            dict(team_index=team, fixtures=counts[team]) for team in row["team_indices"]
        ]
        values = [r["fixtures"] for r in row["team_fixture_counts"]]
        row["minimum_fixtures"] = min(values, default=0)
        row["maximum_fixtures"] = max(values, default=0)
        if len(values) > 1 and not all(values):
            row["issues"].append("members_without_current_conference_fixtures")
        row["diagnostics"] = ", ".join(row["issues"])
    duplicate_membership = sorted(
        team for team, refs in membership.items() if len(refs) > 1
    )
    shared_tournaments = {}
    for row in rows:
        if row["native_season_scope"] and row["tournament_index"] < 96:
            shared_tournaments.setdefault(row["tournament_index"], []).append(
                row["conference_index"]
            )
    for row in rows:
        shared = shared_tournaments.get(row["tournament_index"], [])
        if row["native_season_scope"] and len(shared) > 1:
            row["issues"].append("shared_tournament_route")
            row["shared_tournament_conferences"] = shared
            row["diagnostics"] = ", ".join(row["issues"])
    return dict(
        schema=1,
        source_sha256=sha256(payload).hexdigest(),
        schedule_base=games_base,
        allocated_game_records=count,
        scheduled_games=len(games),
        blank_game_records=blank,
        blank_records_certified_available=False,
        invalid_or_unresolved_games=invalid,
        conferences=rows,
        duplicate_membership=duplicate_membership,
        shared_tournament_routes={
            key: value for key, value in shared_tournaments.items() if len(value) > 1
        },
        schedule_regenerated=False,
        native_tournament_registration_modified=False,
        runtime_compatibility_verified=False,
        interpretation="Counts use current membership; raw game flags and calendar encoding are not relabeled.",
    )
