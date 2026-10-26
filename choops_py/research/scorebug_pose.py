"""Read-only inspection of observed split-HUD skeleton and pose storage.

Native source evidence: instance pose update 829E18, composition 7F8D08,
and text marker consumption 6AEF0..6AF48. No executable writes.
"""

import math
import struct
import zlib

from choops_py.formats.binary import Binary


def inspect_contract(header):
    b = Binary(header)
    models = {}
    if not 0 < b.u32(0x44) <= 4096 or not 0 < b.u32(0x3C) <= 4096:
        raise ValueError("Unsupported model/instance count")
    bone_budget = 0
    t = b.relative(0x48)
    for i in range(b.u32(0x44)):
        q = t + i * 176
        name = b.utf16(b.relative(q), "be")
        key = b.u32(q + 4)
        if key in models:
            raise ValueError("Ambiguous model hash")
        count = b.u32(q + 0x60)
        if not 1 <= count <= 4096:
            raise ValueError("Unsupported model bone count")
        bone_budget += count
        if bone_budget > 100000:
            raise ValueError("Bone audit exceeds budget")
        bt = b.relative(q + 0x64)
        b.slice(bt, count * 48)
        bones = []
        for j in range(count):
            at = bt + j * 48
            n = b.utf16(b.relative(at + 32), "be")
            parent = b.u32(at + 40) >> 16
            if parent != 65535 and not 0 <= parent < j:
                raise ValueError("Unsupported bone parent ordering")
            if b.u32(at + 36) != zlib.crc32(n.encode("ascii")) & 0xFFFFFFFF:
                raise ValueError("Native marker hash mismatch")
            bones.append(
                dict(
                    name=n,
                    at=at,
                    parent=parent,
                    local=list(struct.unpack_from(">3f", header, at + 16)),
                )
            )
        models[key] = dict(name=name, at=q, bones=bones)
    out = []
    t = b.relative(0x40)
    for i in range(b.u32(0x3C)):
        q = t + i * 144
        name = b.utf16(b.relative(q + 64), "be")
        model = models.get(b.u32(q + 68))
        if model is None:
            raise ValueError("Unresolved instance model")
        p = b.relative(q + 0x74)
        count = len(model["bones"])
        if p % 16:
            raise ValueError("Unaligned pose matrix array")
        b.slice(p, count * 64)
        for j in range(count):
            m = struct.unpack_from(">16f", header, p + j * 64)
            if not all(math.isfinite(v) and abs(v) < 1e8 for v in m):
                raise ValueError("Invalid authored pose matrix extent")
            if any(abs(m[k]) > 1e-5 for k in (3, 7, 11)) or abs(m[15] - 1) > 1e-5:
                raise ValueError(
                    "Declared bone count exceeds valid affine pose storage"
                )
        # In the observed scenes names immediately follow their own matrix array.
        # Do not allow an enlarged bone count to consume the instance name pool.
        for field in (q + 64, q + 96, q + 128):
            if b.u32(field):
                start = b.relative(field)
                if p <= start < p + count * 64:
                    raise ValueError("Pose matrix array overlaps instance strings")
        out.append(
            dict(
                name=name,
                at=q,
                flags=b.u32(q + 0x6C),
                poses=p,
                model=model,
                bone_count=count,
            )
        )
    return out
