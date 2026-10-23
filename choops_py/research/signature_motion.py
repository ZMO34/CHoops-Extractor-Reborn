"""Read-only NBA11 signature-IFF source adaptation, never bank installation."""

import hashlib
import math
import struct
from collections import defaultdict

from ..formats.binary import Binary
from ..formats.compression import decode
from ..formats.motion_bind import canonical_channels, verify_canonical_bind
from ..formats.motion_envelope import inspect_envelope
from ..formats.motion_events import inspect_auxiliary_pairs, inspect_events
from ..formats.motion_frames import (
    layout,
    nba11_key_ticks,
    resample_nba11_frames,
    resample_nba11_root,
)
from ..formats.standard_iff import StandardIFF
from .donor_registry import MAX_BANK_BYTES, MOTION
from .target_motion import MAX_IMAGE


class SignatureMotionSource:
    """Bound related banks, resolve typed aliases, retain each caller's metadata.

    Record-relative pointers stay within the decoded record. No synthetic ELF or
    invented executable address is introduced. Decoded blocks are cached within
    the combined declared 128-MiB limit; this is not a process/RSS guarantee.
    """

    def __init__(self, banks):
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

    def _record(self, bank, record):
        if (
            type(bank) is not int
            or not 0 <= bank < len(self.banks)
            or type(record) is not int
            or not 0 <= record < len(self.banks[bank].records)
        ):
            raise ValueError("Choose an existing signature bank/record index")
        iff = self.banks[bank]
        item = iff.records[record]
        if item["type_hash"] != MOTION:
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
        raw = Binary(self.cache[key]).slice(start, end - start)
        Binary(raw).slice(0, 56)
        if struct.unpack_from(">I", raw)[0] != item["id"]:
            raise ValueError("Signature record identity disagrees with motion header")
        return raw

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
                raise ValueError("Signature alias identity is missing or ambiguous")
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
        """Read known tracks without inferring auxiliary ends or selector routing."""
        header, raw, path = self.resolve(bank, record)
        envelope = inspect_envelope(raw, "nba-2k11")
        channels = canonical_channels(header, "nba-2k11")
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
        ordered = sorted(
            (e["offset"], e["offset"] + e["bytes"]) for e in extents if e["bytes"]
        )
        if any(a[1] > b[0] for a, b in zip(ordered, ordered[1:])):
            raise ValueError("Known signature dependency extents overlap")
        blockers = ["target-authoring-metadata", "native-registration-and-lifetime"]
        if flags & 63:
            blockers.append("auxiliary-selector-extents-and-semantics")
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
            source_record_sha256=hashlib.sha256(self._record(bank, record)).hexdigest(),
            payload_record_sha256=hashlib.sha256(raw).hexdigest(),
            header_hex=header[:56].hex(),
            original_alias_metadata_retained=True,
            channels=channels,
            source_key_count=keys,
            timing_unused_final_slot_normalized=True,
            target_frame_count=ticks[-1] + 1,
            rate=rate,
            time_scale=scale,
            duration=duration,
            extents=extents,
            auxiliary_pointers=[pointers[hex(56 + i * 4)] for i in range(flags & 63)],
            auxiliary_extents_established=False if flags & 63 else True,
            header_reference=pointers["0x4"],
            membership=membership,
            events=events,
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
