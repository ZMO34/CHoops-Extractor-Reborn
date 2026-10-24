"""Read-only NBA11 signature-IFF source adaptation, never bank installation."""

import hashlib
import math
import struct
from collections import defaultdict

from ..formats.binary import Binary
from ..formats.compression import decode
from ..formats.motion_bind import (
    canonical_channels,
    declared_channels,
    verify_canonical_bind,
)
from ..formats.motion_envelope import inspect_envelope
from ..formats.motion_events import (
    curve_timing_contract,
    event_mapping_coverage,
    inspect_auxiliary_pairs,
    inspect_events,
    transcode_events,
)
from ..formats.motion_frames import (
    layout,
    nba11_key_ticks,
    resample_nba11_frames,
    resample_nba11_root,
)
from ..formats.standard_iff import StandardIFF
from .donor_registry import COLLECTION, GROUP, MAX_BANK_BYTES, MOTION
from .motion_auxiliary import read_selector_prefix, transcode_selector_curve
from .target_motion import MAX_IMAGE


class SignatureMotionSource:
    """Bound related banks, resolve typed aliases, retain each caller's metadata.

    Record-relative pointers stay within the decoded record. No synthetic ELF or
    invented executable address is introduced. Decoded blocks are cached within
    the combined declared 128-MiB limit; this is not a process/RSS guarantee.
    """

    def __init__(self, banks, *, coalesce_identical=False):
        if type(coalesce_identical) is not bool:
            raise ValueError("Identical-record coalescing must be an explicit boolean")
        self.coalesce_identical = coalesce_identical
        if (
            not 1 <= len(banks) <= 32
            or sum(len(raw) for _, raw in banks) > MAX_BANK_BYTES
        ):
            raise ValueError("Choose 1..32 signature banks within 128 MiB")
        self.banks = [StandardIFF(bytes(raw)) for _, raw in banks]
        if (
            sum(b["logical_size"] for f in self.banks for b in f.blocks)
            > MAX_BANK_BYTES
        ):
            raise ValueError("Combined decoded signature blocks exceed 128 MiB")
        self.fingerprints = [hashlib.sha256(f.raw).hexdigest() for f in self.banks]
        self.index = defaultdict(list)
        self.cache = {}
        for bank, iff in enumerate(self.banks):
            for record in iff.records:
                if record["type_hash"] == MOTION:
                    self.index[record["id"]].append((bank, record["index"]))

    def _record(self, bank, record, *, type_hash=MOTION):
        if type_hash not in (MOTION, GROUP):
            raise ValueError("Signature source must be a typed SingleMoCap record")
        raw = self._record_bytes(bank, record, type_hash=type_hash)
        Binary(raw).slice(0, 56 if type_hash == MOTION else 12)
        if struct.unpack_from(">I", raw)[0] != self.banks[bank].records[record]["id"]:
            raise ValueError("Signature record identity disagrees with motion header")
        return raw

    def _record_bytes(self, bank, record, *, type_hash):
        """Share bounded decoded blocks with typed collection consumers."""
        if (
            type(bank) is not int
            or not 0 <= bank < len(self.banks)
            or type(record) is not int
            or not 0 <= record < len(self.banks[bank].records)
        ):
            raise ValueError("Choose an existing signature bank/record index")
        iff = self.banks[bank]
        item = iff.records[record]
        if type_hash not in (MOTION, GROUP, COLLECTION) or item["type_hash"] != type_hash:
            raise ValueError("Signature source must be a typed SingleMoCap record")
        spans = list(iff.spans(item))
        if len(spans) != 1:
            raise ValueError(
                "Signature motion requires one complete decoded record span"
            )
        bi, start, end = spans[0]
        key = bank, bi
        if key not in self.cache:
            block = iff.blocks[bi]
            self.cache[key] = decode(
                iff.raw[block["start"] : block["start"] + block["size"]],
                block["logical_size"],
            )
        return Binary(self.cache[key]).slice(start, end - start)

    def resolve(self, bank, record):
        """Return original header, track-owning record and an explicit alias path.

        Identity matches alone cannot prove compatibility. Masks, channel/rate/
        auxiliary counts, key counts and root/packing modes must agree. Mirror,
        phase/state and authored timing remain the original header's metadata.
        """
        origin = self._record(bank, record)
        current, path, seen = (bank, record), [], set()
        while True:
            if current in seen or len(path) >= 4096:
                raise ValueError("Signature alias cycle or chain exceeds 4096 records")
            seen.add(current)
            raw = self._record(*current)
            path.append(
                dict(
                    bank=current[0],
                    record=current[1],
                    bank_sha256=self.fingerprints[current[0]],
                )
            )
            # The unresolved +0x28 word is an ID, never a relative pointer.
            if struct.unpack_from(">I", raw, 48)[0]:
                break
            key = struct.unpack_from(">I", raw, 40)[0]
            matches = self.index.get(key, [])
            if len(matches) != 1:
                if not self.coalesce_identical or not matches:
                    raise ValueError("Signature alias identity is missing or ambiguous")
                candidates = [self._record(*loc) for loc in matches]
                if any(candidate != candidates[0] for candidate in candidates[1:]):
                    raise ValueError(
                        "Signature alias duplicate records are not identical"
                    )
                # This equivalence includes all decoded bytes, including unknown
                # tails. No identity/hash-only or load-order winner is selected.
                path[-1]["equivalent_alias_targets"] = [
                    dict(
                        bank=a,
                        record=b,
                        bank_sha256=self.fingerprints[a],
                        record_sha256=hashlib.sha256(data).hexdigest(),
                    )
                    for (a, b), data in zip(matches, candidates)
                ]
                current = min(matches)
            else:
                current = matches[0]
        for entry in path[:-1]:
            alias = self._record(entry["bank"], entry["record"])
            if alias[8:20] != raw[8:20] or (
                (
                    struct.unpack_from(">I", alias, 20)[0]
                    ^ struct.unpack_from(">I", raw, 20)[0]
                )
                & 0x8000FFFF
            ):
                raise ValueError(
                    "Signature alias channel/count/packing metadata disagrees"
                )
            Binary(alias).slice(56, (struct.unpack_from(">I", alias, 16)[0] & 63) * 4)
        return origin, raw, path

    def tracks(self, bank, record):
        """Read canonical-family tracks, retaining the conversion bind gate."""
        return self._tracks(bank, record, canonical=True)

    def inspect_tracks(self, bank, record):
        """Read declared channel families without establishing target rig mapping."""
        return self._tracks(bank, record, canonical=False)

    def _tracks(self, bank, record, *, canonical):
        header, raw, path = self.resolve(bank, record)
        return self._read_tracks(
            header, raw, path, canonical=canonical,
            source_record=self._record(bank, record),
        )

    def _read_tracks(self, header, raw, path, *, canonical, source_record):
        """Shared bounded track reader; grouped headers have a separate resolver."""
        envelope = inspect_envelope(raw, "nba-2k11")
        channel_reader = canonical_channels if canonical else declared_channels
        channels = channel_reader(header, "nba-2k11")
        flags, mode = struct.unpack_from(">2I", header, 16)
        if mode & 0x8000:
            raise ValueError("Unpacked signature pose mode needs a separate decoder")
        keys, rate = mode & 0x7FFF, flags >> 24
        scale, duration = struct.unpack_from(">2f", header, 28)
        if (
            not keys
            or not rate
            or not math.isfinite(scale)
            or scale <= 0
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise ValueError("Invalid signature timing metadata")
        b, pointers = Binary(raw), envelope["pointers"]
        data, extents = {}, []

        def track(field, role, size):
            at = pointers[hex(field)]
            if at is None or at < 56 + (flags & 63) * 4:
                raise ValueError("Signature track is null or overlaps its header")
            value = b.slice(at, size)
            data[role] = value
            extents.append(dict(role=role, offset=at, bytes=size))
            return at

        # The native timeline consumes only keys-1 interval bytes. Serialized
        # records may end there; do not read a byte from the adjacent record.
        track(36, "timing", keys - 1)
        data["timing"] += b"\0"  # unused final slot for the shared resampler API
        ticks = nba11_key_ticks(data["timing"])
        if keys > 1 and not math.isclose(
            ticks[-1], duration * rate * scale, rel_tol=2e-6, abs_tol=0.002
        ):
            raise ValueError("Signature alias timing and authored ticks disagree")
        _, size = layout(channels["rotations"], channels["translations"], keys)
        track(40, "poses", size)
        track(44, "root", keys * (6 if mode & 0x80000000 else 8))
        event_at = pointers["0x30"]
        if event_at is None:
            raise ValueError("Signature event table is null")
        events = inspect_events(raw, "nba-2k11", event_at)
        track(48, "events", events["sentinel"] - event_at + 4)
        membership = None
        if pointers["0x34"] is not None:
            membership = inspect_auxiliary_pairs(raw, pointers["0x34"])
            track(52, "membership", 4 + membership["count"] * 8)
        auxiliary = []
        for i in range(flags & 63):
            field = 56 + i * 4
            pointer = pointers[hex(field)]
            if pointer is None:
                raise ValueError("Signature counted selector pointer is null")
            curve = read_selector_prefix(
                b.slice, pointer, duration=duration, time_scale=scale
            )
            track(field, f"selector:{i}", len(curve))
            auxiliary.append(
                dict(
                    channel=i,
                    offset=pointer,
                    bytes=len(curve),
                    curve_sha256=hashlib.sha256(curve).hexdigest(),
                    selectors=sorted(set(curve[::4])),
                    selector_semantics_established=False,
                )
            )
        ordered = sorted(
            (e["offset"], e["offset"] + e["bytes"], e["role"])
            for e in extents
            if e["bytes"]
        )
        if any(
            a[1] > b[0]
            and not (
                a[:2] == b[:2]
                and a[2].startswith("selector:")
                and b[2].startswith("selector:")
            )
            for a, b in zip(ordered, ordered[1:])
        ):
            raise ValueError("Known signature dependency extents overlap")
        blockers = ["target-authoring-metadata", "native-registration-and-lifetime"]
        if flags & 63:
            blockers.append("auxiliary-selector-semantics")
        if pointers["0x4"] is not None:
            blockers.append("header-reference-dependency")
        if membership is not None:
            blockers.append("membership-semantics")
        if events["entries"]:
            blockers.append("event-contract-required")
        return data, dict(
            schema=1,
            source_kind="nba11-signature-iff",
            alias_path=path,
            source_header_sha256=hashlib.sha256(header[:56]).hexdigest(),
            source_record_sha256=hashlib.sha256(source_record).hexdigest(),
            payload_record_sha256=hashlib.sha256(raw).hexdigest(),
            header_hex=header[:56].hex(),
            original_alias_metadata_retained=True,
            channels=channels,
            canonical_channel_family_required=canonical,
            target_bone_mapping_established=False,
            source_key_count=keys,
            timing_unused_final_slot_normalized=True,
            target_frame_count=ticks[-1] + 1,
            rate=rate,
            time_scale=scale,
            duration=duration,
            extents=extents,
            auxiliary_pointers=[pointers[hex(56 + i * 4)] for i in range(flags & 63)],
            auxiliary_extents_established=True,
            auxiliary_tracks=auxiliary,
            auxiliary_semantics_established=False,
            header_reference=pointers["0x4"],
            membership=membership,
            events=events,
            established_event_mapping=event_mapping_coverage(
                events, curve_timing_contract()
            ),
            complete_motion=False,
            conversion_blockers=blockers,
            gameplay_ready=False,
        )

    def prepare_pose_root(
        self, bank, record, donor_elf, target_elf, *, budget=MAX_IMAGE
    ):
        """Return bounded CH pose/root components, with omitted dependencies explicit.

        Canonical bind proof uses the supplied decoded executables; bank source
        provenance remains independently fingerprinted. This creates no CH header,
        complete motion, installable bank, or executable patch.
        """
        if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
            raise ValueError("Signature component budget must be 64 bytes..16 MiB")
        bind = verify_canonical_bind(donor_elf, target_elf)
        tracks, report = self.tracks(bank, record)
        channels, frames = report["channels"], report["target_frame_count"]
        _, size = layout(channels["rotations"], channels["translations"], frames)
        stride = len(tracks["root"]) // report["source_key_count"]
        if size + frames * stride > budget:
            raise ValueError("Expanded signature components exceed byte budget")
        poses, sampling = resample_nba11_frames(
            tracks["poses"],
            tracks["timing"],
            channels["rotations"],
            channels["translations"],
        )
        root = resample_nba11_root(
            tracks["root"], tracks["timing"], has_heading=stride == 8
        )
        report.update(
            bind=bind,
            donor_elf_sha256=hashlib.sha256(donor_elf).hexdigest(),
            target_elf_sha256=hashlib.sha256(target_elf).hexdigest(),
            mirror_and_phase_baked_into_tracks=False,
            resampling=sampling,
            component_bytes=len(poses) + len(root),
            omitted_dependencies=["header", "events", "auxiliary", "membership"],
            native_loader_installed=False,
        )
        return dict(poses=poses, root=root), report


def translate_signature_motion(
    source,
    bank,
    record,
    donor_elf,
    target_elf,
    metadata_contract,
    event_contract,
    *,
    budget=MAX_IMAGE,
    auxiliary_contracts=None,
):
    """Construct a complete known-layout component using explicit assertions.

    Schema 2 binds metadata to the serialized record, complete bank, donor bind
    executable and target executable. Counted selector curves additionally need
    explicit per-channel contracts. References/membership remain blocked; no
    metadata defaults or native installation are inferred.
    """
    from .donor_header import _assemble_target_image, _authoring_fields

    if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
        raise ValueError("Signature component budget must be 64 bytes..16 MiB")
    bind = verify_canonical_bind(donor_elf, target_elf)
    tracks, report = source.tracks(bank, record)
    header = bytes.fromhex(report["header_hex"])
    c = metadata_contract
    if not isinstance(c, dict) or c.get("schema") != 2:
        raise ValueError("Signature metadata requires a schema-2 research contract")
    expected = dict(
        source_bank_index=bank,
        source_record_index=record,
        source_bank_sha256=source.fingerprints[bank],
        source_banks_sha256=list(source.fingerprints),
        source_header_sha256=report["source_header_sha256"],
        donor_elf_sha256=hashlib.sha256(donor_elf).hexdigest(),
        target_elf_sha256=hashlib.sha256(target_elf).hexdigest(),
    )
    if any(
        c.get(k) != value or type(c.get(k)) is not type(value)
        for k, value in expected.items()
    ):
        raise ValueError("Signature metadata contract identity/fingerprints changed")
    high, state, planar = _authoring_fields(header, c)
    if report["header_reference"] is not None or report["membership"] is not None:
        raise ValueError(
            "Signature auxiliary/reference/membership dependencies remain unmapped"
        )
    pointers = report["auxiliary_pointers"]
    if auxiliary_contracts is None:
        auxiliary_contracts = []
    if not isinstance(auxiliary_contracts, list) or len(auxiliary_contracts) != len(
        pointers
    ):
        raise ValueError("All auxiliary channels need explicit selector contracts")
    selectors, selector_reports = [], []
    for i, contract in enumerate(auxiliary_contracts):
        translated, assertion = transcode_selector_curve(
            tracks[f"selector:{i}"],
            contract,
            channel=i,
            target_elf_sha256=expected["target_elf_sha256"],
            duration=report["duration"],
            time_scale=report["time_scale"],
        )
        selectors.append(translated)
        selector_reports.append(assertion)
    frames, channels = report["target_frame_count"], report["channels"]
    _, pose_bytes = layout(channels["rotations"], channels["translations"], frames)
    root_stride = len(tracks["root"]) // report["source_key_count"]
    pose_at = (64 + 4 * len(selectors) + 15) & ~15
    root_at = (pose_at + pose_bytes + 15) & ~15
    event_at = (root_at + frames * root_stride + 15) & ~15
    if event_at + 4 > budget:
        raise ValueError("Signature target component exceeds byte budget")
    events, event_report = transcode_events(report["events"], event_contract)
    if event_at + len(events) > budget:
        raise ValueError("Signature target events exceed byte budget")
    planned_end = event_at + len(events)
    for curve in selectors:
        planned_end = ((planned_end + 15) & ~15) + len(curve)
    if planned_end > budget:
        raise ValueError("Signature target selectors exceed byte budget")
    poses, sampling = resample_nba11_frames(
        tracks["poses"],
        tracks["timing"],
        channels["rotations"],
        channels["translations"],
    )
    roots = resample_nba11_root(
        tracks["root"], tracks["timing"], has_heading=root_stride == 8
    )
    image, extents = _assemble_target_image(
        header,
        channels,
        high,
        state,
        planar,
        frames,
        poses,
        roots,
        events,
        budget,
        selectors=selectors,
    )
    report.update(
        component_format="owned-relative-CH-motion",
        auxiliary_translation=selector_reports,
        auxiliary_extents_established=True,
        conversion_blockers=[
            "target-authoring-and-selector-semantics-assertions-need-proof",
            "native-publication-and-gameplay-validation",
        ],
        header_offsets=[0],
        extents=extents,
        bytes=len(image),
        bind=bind,
        resampling=sampling,
        events=event_report,
        metadata_bindings=expected,
        metadata_assertions=dict(
            target_mode_high16=high,
            target_state_bits=state,
            authored_planar_float32=list(struct.unpack(">3f", planar)),
            evidence={k: c["evidence"][k] for k in ("mode", "state", "planar")},
        ),
        metadata_automatically_established=False,
        metadata_provenance="explicit-per-record-caller-research-assertions",
        complete_known_layout=True,
        native_loader_installed=False,
        gameplay_ready=False,
    )
    return image, report
