"""Owner-authorized decoded-ELF resident loading; no GUI or SELF writer.

Always-resident storage avoids heap rebinding, mid-match allocation and premature
alias eviction. This does not establish donor semantics or certify PS3 execution.
"""

import hashlib
import struct

from ..formats.embedded_motion import MAX_ELF, NativeELF
from .target_motion import MAX_IMAGE, inspect_target_motion, relocate_target_image


def append_resident_image(raw, image, header_offsets, *, budget=MAX_IMAGE):
    """Return a separate decoded ELF with an owned motion image in a load segment.

    Preserve original virtual addresses and file-backed load bytes. Materialize
    pre-existing BSS as zeros before appending the relocated image. Shift trailing
    nonloaded sections and their file offsets rather than loading them into BSS.
    Storage lasts until process exit; no runtime allocator or free is introduced.
    Unknown dependency extents remain blocked. No registration is implied.
    """
    if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
        raise ValueError("Resident image budget must be 64 bytes..16 MiB")
    if not isinstance(image, (bytes, bytearray)) or not 64 <= len(image) <= budget:
        raise ValueError("Resident image exceeds payload budget")
    raw, image = bytes(raw), bytes(image)
    header_offsets = tuple(header_offsets)
    elf = NativeELF(raw)
    # Validate the source image before any potentially large output allocation.
    relocate_target_image(image, header_offsets, 0x20000000, source_state="relative")
    for offset in header_offsets:
        if (
            struct.unpack_from(">I", image, offset + 16)[0] & 63
            or struct.unpack_from(">I", image, offset + 60)[0]
        ):
            raise ValueError("Unmapped auxiliary dependencies cannot be installed")
    phoff = struct.unpack_from(">Q", raw, 32)[0]
    phsize, phcount = struct.unpack_from(">HH", raw, 54)
    headers = [
        struct.unpack_from(">II6Q", raw, phoff + i * phsize) for i in range(phcount)
    ]
    loads = [(i, h) for i, h in enumerate(headers) if h[0] == 1 and h[6]]
    index, segment = max(loads, key=lambda item: item[1][2] + item[1][5])
    _, flags, file_at, address, _, file_bytes, memory_bytes, alignment = segment
    cut = file_at + file_bytes
    if flags & 7 != 6 or cut < phoff + phsize * phcount:
        raise ValueError(
            "Last file-backed load must be writable data after program headers"
        )
    if alignment > 1 and (
        alignment & (alignment - 1) or file_at % alignment != address % alignment
    ):
        raise ValueError("Unsupported original load alignment")
    base = (address + memory_bytes + 15) & ~15
    extent = ((base + len(image) + 15) & ~15) - address
    if address + extent > 1 << 32:
        raise ValueError("Resident load exceeds 32-bit native addresses")
    if any(
        i != index
        and h[0] == 1
        and h[6]
        and address < h[3] + h[6]
        and h[3] < address + extent
        for i, h in enumerate(headers)
    ):
        raise ValueError("Resident extension collides with native load memory")
    growth = extent - file_bytes
    if len(raw) + growth > MAX_ELF:
        raise ValueError("Expanded analysis ELF exceeds 256 MiB")
    for i, h in enumerate(headers):
        if i == index:
            continue
        pos, size = h[2], h[5]
        if h[0] == 7 and (
            pos + size > cut or (h[3] < address + extent and base < h[3] + h[6])
        ):
            raise ValueError("Resident extension would alter TLS storage")
        if size and pos < cut < pos + size:
            raise ValueError("Program extent crosses resident insertion boundary")

    shoff = struct.unpack_from(">Q", raw, 40)[0]
    shsize, shcount, shstrings = struct.unpack_from(">HHH", raw, 58)
    if shcount and (
        not shoff
        or shsize != 64
        or shoff + shcount * shsize > len(raw)
        or shstrings >= shcount
    ):
        raise ValueError("Invalid or extended ELF section table")
    if not shcount and shoff:
        raise ValueError("Extended ELF section counts are not supported")
    if shcount and shoff < cut < shoff + shcount * shsize:
        raise ValueError("Section table crosses resident insertion boundary")
    sections = []
    for i in range(shcount):
        at = shoff + i * shsize
        kind = struct.unpack_from(">I", raw, at + 4)[0]
        offset, size = struct.unpack_from(">QQ", raw, at + 24)
        if (
            kind != 8
            and size
            and (offset + size > len(raw) or offset < cut < offset + size)
        ):
            raise ValueError("Section data crosses insertion boundary or file bounds")
        sections.append((at, kind, offset, size))

    native = relocate_target_image(image, header_offsets, base, source_state="relative")
    injection = bytearray(growth)
    image_at = base - address - file_bytes
    injection[image_at : image_at + len(native)] = native
    output = bytearray(raw[:cut] + injection + raw[cut:])
    edits = []

    def moved(offset):
        return offset + growth if offset >= cut else offset

    def put(original_offset, data):
        at = moved(original_offset)
        output[at : at + len(data)] = data
        edits.append(
            (
                original_offset,
                bytes(raw[original_offset : original_offset + len(data)]),
                bytes(data),
            )
        )

    put(phoff + index * phsize + 32, struct.pack(">QQ", extent, extent))
    for i, h in enumerate(headers):
        if i != index and h[2] >= cut and h[2]:
            put(phoff + i * phsize + 8, struct.pack(">Q", h[2] + growth))
    if shcount and shoff >= cut:
        put(40, struct.pack(">Q", shoff + growth))
    for at, kind, offset, size in sections:
        if kind != 8 and offset >= cut and (offset or size):
            put(at + 24, struct.pack(">Q", offset + growth))

    result = NativeELF(output)
    for original in elf.segments:
        if result.read(original["address"], original["file_bytes"]) != elf.read(
            original["address"], original["file_bytes"]
        ):
            # Program/section tables may reside inside an existing load. Their
            # exact permitted edits are checked by the inverse reconstruction.
            first, last = elf.file_span(original["address"], original["file_bytes"])
            expected = bytearray(raw[first:last])
            for at, _, data in edits:
                if first <= at and at + len(data) <= last:
                    expected[at - first : at - first + len(data)] = data
            if result.read(original["address"], original["file_bytes"]) != expected:
                raise ValueError("Existing load bytes were altered")
    if any(result.read(address + file_bytes, base - address - file_bytes)):
        raise ValueError("Original BSS is not zero-initialized")
    if result.read(base, len(native)) != native:
        raise ValueError("Resident image load readback failed")
    for offset in header_offsets:
        inspected = inspect_target_motion(result, base + offset)
        if not inspected["resident_image_supported"]:
            raise ValueError("Resident motion contains unmapped dependencies")
    if (
        relocate_target_image(native, header_offsets, base, source_state="native")
        != image
    ):
        raise ValueError("Resident image relocation inverse failed")
    inverse = bytearray(output[:cut] + output[cut + growth :])
    for at, before, _ in edits:
        inverse[at : at + len(before)] = before
    if inverse != raw:
        raise ValueError("Resident ELF inverse preservation check failed")
    return bytes(output), dict(
        schema=1,
        source_elf_sha256=hashlib.sha256(raw).hexdigest(),
        relative_image_sha256=hashlib.sha256(image).hexdigest(),
        resident_base=base,
        header_addresses=[base + x for x in header_offsets],
        image_bytes=len(image),
        added_file_bytes=growth,
        existing_bss_bytes=memory_bytes - file_bytes,
        segment_address=address,
        original_file_end=cut,
        native_loading="existing-ELF-PT_LOAD",
        storage_lifetime="process-exit",
        runtime_heap_allocations=0,
        runtime_eviction=False,
        inverse_preservation_verified=True,
        registered=False,
        donor_semantics_established=False,
        ps3_runtime_verified=False,
        gameplay_ready=False,
    )


def install_resident_shots(raw, image, header_offsets, contract, *, budget=MAX_IMAGE):
    """Publish complete target motions via existing native shot-table consumers.

    Explicit row metadata/name assertions must be bound to the complete target
    ELF and image. They are not automatic donor metadata proof. The source must
    still have its original 112 entries. No stock style is replaced or truncated.
    """
    from .shot_registration import (
        CAP_INSTRUCTION,
        LABEL_END_SLOT,
        LABEL_START_SLOT,
        STOCK_TABLE,
        TABLE_SLOT,
        inspect_registration,
    )

    if not isinstance(raw, (bytes, bytearray)) or len(raw) > MAX_ELF:
        raise ValueError("Resident source must be bounded decoded ELF bytes")
    if not isinstance(image, (bytes, bytearray)) or not 64 <= len(image) <= MAX_IMAGE:
        raise ValueError("Resident image exceeds payload budget")
    if not isinstance(contract, dict) or contract.get("schema") != 1:
        raise ValueError("An explicit resident registration contract is required")
    if (
        contract.get("target_elf_sha256") != hashlib.sha256(raw).hexdigest()
        or contract.get("image_sha256") != hashlib.sha256(image).hexdigest()
    ):
        raise ValueError("Resident registration contract fingerprints changed")
    raw, image = bytes(raw), bytes(image)
    header_offsets = tuple(header_offsets)
    entries = contract.get("entries")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 144:
        raise ValueError(
            "Adding styles must retain 112 originals within the 256-ID limit"
        )
    if type(budget) is not int or not 64 <= budget <= MAX_IMAGE:
        raise ValueError("Resident registration budget must be 64 bytes..16 MiB")
    if not isinstance(image, (bytes, bytearray)) or not 64 <= len(image) <= budget:
        raise ValueError("Resident image exceeds payload budget")
    # Table/name storage cannot make an escaping source pointer appear owned.
    relocate_target_image(image, header_offsets, 0x20000000, source_state="relative")
    original = inspect_registration(raw, motion_extents=True)
    if original["count"] != 112:
        raise ValueError("Resident installation requires the original 112-style table")
    elf = NativeELF(raw)
    segment = max(elf.segments, key=lambda s: s["offset"] + s["file_bytes"])
    base = (segment["address"] + segment["memory_bytes"] + 15) & ~15
    count = 112 + len(entries)
    table_at = (len(image) + 15) & ~15
    names_at = (table_at + count * 40 + 15) & ~15
    total = names_at + count * 4
    if total > budget:
        raise ValueError("Resident image/table/names exceed byte budget")
    output_image = bytearray(total)
    output_image[: len(image)] = image
    output_image[table_at : table_at + 112 * 40] = elf.read(STOCK_TABLE, 112 * 40)
    assertions = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError("Each resident style needs an explicit metadata assertion")
        indices = entry.get("header_indices")
        metadata = entry.get("playback_metadata_hex")
        label = entry.get("target_label_key")
        evidence = entry.get("evidence")
        if (
            not isinstance(indices, list)
            or len(indices) != 2
            or any(
                type(v) is not int or not 0 <= v < len(header_offsets) for v in indices
            )
        ):
            raise ValueError("Choose both resident header indices explicitly")
        if not isinstance(metadata, str) or len(metadata) != 64:
            raise ValueError("Explicit 32-byte playback metadata is required")
        try:
            metadata = bytes.fromhex(metadata)
        except ValueError as error:
            raise ValueError("Playback metadata must be hexadecimal") from error
        if len(metadata) != 32:
            raise ValueError("Playback metadata must contain exactly 32 bytes")
        if type(label) is not int or not 0 < label <= 0xFFFFFFFF or not label & 1:
            raise ValueError("Target label must be an explicit tagged localization key")
        if not isinstance(evidence, dict) or any(
            not isinstance(evidence.get(k), str)
            or not evidence[k].strip()
            or len(evidence[k]) > 2048
            for k in ("playback", "label")
        ):
            raise ValueError(
                "Playback and label semantics need bounded research assertions"
            )
        assertions.append(dict(
            header_indices=list(indices),
            playback_metadata_hex=metadata.hex(),
            target_label_key=label,
            evidence={k: evidence[k] for k in ("playback", "label")},
        ))
        at = table_at + (112 + i) * 40
        output_image[at : at + 32] = metadata
        struct.pack_into(
            ">II", output_image, at + 32, *(base + header_offsets[v] for v in indices)
        )
        struct.pack_into(">I", output_image, names_at + (112 + i) * 4, label)
    installed, report = append_resident_image(
        raw, output_image, header_offsets, budget=budget
    )
    if report["resident_base"] != base:
        raise ValueError("Resident publication base changed")
    result = bytearray(installed)
    loaded = NativeELF(installed)
    expected_changes = []
    for address, value in (
        (TABLE_SLOT, base + table_at),
        (LABEL_START_SLOT, base + names_at),
        (LABEL_END_SLOT, base + names_at + count * 4),
        (CAP_INSTRUCTION, 0x38000000 | (count - 1)),
    ):
        at = loaded.target(address)["file_offset"]
        expected_changes.append((at, installed[at : at + 4]))
        struct.pack_into(">I", result, at, value)
    audit = inspect_registration(result, motion_extents=True)
    restored = bytearray(result)
    for at, value in expected_changes:
        restored[at : at + 4] = value
    if restored != installed or audit["count"] != count:
        raise ValueError("Native registration preservation check failed")
    owned = set(report["header_addresses"])
    for row in audit["entries"][112:]:
        if not set(row["motions"]) <= owned:
            raise ValueError("Added registration borrows a foreign motion header")
    report.update(
        registered=True,
        registered_count=count,
        original_styles_preserved=112,
        native_publication="existing-shot-table-TOC-slot",
        input_image_sha256=hashlib.sha256(image).hexdigest(),
        registration_metadata_provenance="explicit-caller-research-assertions",
        registration_metadata_automatically_established=False,
        registration_assertions=assertions,
        shutdown_free_required=False,
    )
    return bytes(result), report
