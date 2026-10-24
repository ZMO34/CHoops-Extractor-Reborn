"""Bounded full supplied-IFF motion audit, retaining every channel family gate."""

from collections import Counter

from ..formats.motion_frames import layout
from .donor_registry import MOTION
from .signature_motion import SignatureMotionSource

MAX_RECORDS = 100000
MAX_ERRORS = 256


def inspect_library(banks, *, coalesce_identical=False):
    source = SignatureMotionSource(banks, coalesce_identical=coalesce_identical)
    count = sum(r["type_hash"] == MOTION for iff in source.banks for r in iff.records)
    if not 1 <= count <= MAX_RECORDS:
        raise ValueError("Choose a motion library containing 1..100000 typed records")
    counts, families, unmapped_events, opaque_events = (Counter() for _ in range(4))
    errors, bank_reports, owners = [], [], {}
    for bi, iff in enumerate(source.banks):
        local = Counter()
        for record in iff.records:
            if record["type_hash"] != MOTION:
                continue
            counts["records"] += 1
            local["records"] += 1
            try:
                _, report = source.inspect_tracks(bi, record["index"])
            except ValueError as error:
                counts["blocked_records"] += 1
                local["blocked_records"] += 1
                if len(errors) < MAX_ERRORS:
                    errors.append(
                        dict(bank=bi, record=record["index"], reason=str(error))
                    )
                continue
            counts["inspected_records"] += 1
            local["inspected_records"] += 1
            counts["alias_headers"] += len(report["alias_path"]) > 1
            counts["identical_duplicate_aliases"] += any(
                "equivalent_alias_targets" in entry for entry in report["alias_path"]
            )
            ch = report["channels"]
            families[
                ch["declared_bones"], ch["rotation_mask"], ch["translation_mask"]
            ] += 1
            counts["canonical_family_candidates"] += (
                ch["declared_bones"] == 21
                and ch["rotation_mask"] == 0x1DF7DD
                and ch["translation_mask"] >> 21 == 0
            )
            coverage = report["established_event_mapping"]
            counts["event_rows"] += coverage["events"]
            counts["mapped_event_rows"] += coverage["mapped_events"]
            unmapped_events.update(x["source_id"] for x in coverage["unmapped_rules"])
            opaque_events.update(coverage["opaque_payload_ids"])
            root_extent = next(x for x in report["extents"] if x["role"] == "root")
            root_stride = root_extent["bytes"] // report["source_key_count"]
            frames = report["target_frame_count"]
            stride, _ = layout(ch["rotations"], ch["translations"], 1)
            pose_bytes = stride * frames
            counts["fixed_frame_count_overflows"] += frames > 65535
            owners[report["payload_record_sha256"]] = pose_bytes + frames * root_stride
        bank_reports.append(
            dict(
                bank=bi,
                name=banks[bi][0],
                sha256=source.fingerprints[bi],
                counts=dict(local),
            )
        )
    return dict(
        schema=1,
        profile="nba-2k11",
        mode="read-only",
        counts=dict(counts),
        banks=bank_reports,
        distinct_payload_record_hashes=len(owners),
        fixed_rate_pose_root_bytes_before_bind_mapping=sum(owners.values()),
        largest_fixed_rate_pose_root_component=max(owners.values(), default=0),
        expansion_estimate_excludes_headers_events_selectors_and_registration=True,
        channel_families=[
            dict(
                bones=k[0],
                rotation_mask=k[1],
                translation_mask=k[2],
                count=value,
                target_bone_map_established=False,
            )
            for k, value in sorted(families.items())
        ],
        unmapped_event_rule_counts=dict(sorted(unmapped_events.items())),
        opaque_event_record_counts=dict(sorted(opaque_events.items())),
        errors=errors,
        errors_truncated=counts["blocked_records"] > len(errors),
        all_supplied_typed_records_inspected=not counts["blocked_records"],
        identical_record_coalescing_enabled=coalesce_identical,
        archive_discovery_complete=False,
        executable_held_library_included=False,
        conversion_bind_gate_retained=True,
        complete_target_port=False,
        gameplay_ready=False,
    )
