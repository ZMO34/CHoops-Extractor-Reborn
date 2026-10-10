"""PS3 H7A decoding and preservation-oriented same-logical-size encoding."""
import struct
from .binary import Binary
from ..core.errors import ToolError
MAGIC = 0x0E4837C3
MAX_LOGICAL = 512 * 1024 * 1024

def tokens(raw):
    b = Binary(raw)
    if b.u32(0) != MAGIC: raise ToolError('invalid_h7a', 'Missing wrapper magic')
    expected, stored, unknown, shift = [b.u32(i) for i in (4,8,12,16)]
    if stored != len(raw) or expected > MAX_LOGICAL or not 1 <= shift <= 16:
        raise ToolError('invalid_h7a', 'Invalid wrapper sizes or shift')
    pos = 20; output = 0
    while output < expected:
        flags = b.slice(pos,1)[0]; pos += 1
        for bit in range(8):
            if output == expected: break
            if flags & (1 << bit):
                token = b.u16(pos); pos += 2
                distance = token & ((1 << shift)-1)
                length = min((token >> shift)+3, expected-output)
                if not distance or distance > output: raise ToolError('invalid_h7a', 'Backreference outside decoded data')
                yield output, length, distance, None
                output += length
            else:
                value = b.slice(pos,1)[0];pos += 1
                yield output, 1, 0, value
                output += 1

def decode(raw, expected=None):
    if raw[:4] != struct.pack('>I', MAGIC):
        if expected is not None and len(raw) != expected: raise ToolError('block_size_mismatch','Uncompressed block length differs')
        return raw
    declared = Binary(raw).u32(4)
    if expected is not None and declared != expected: raise ToolError('block_size_mismatch','Wrapper/table logical sizes differ')
    out = bytearray()
    for offset, length, distance, literal in tokens(raw):
        if distance:
            for _ in range(length): out.append(out[-distance])
        else: out.append(literal)
    return bytes(out)

def encode_like(original, replacement):
    """Prefer valid old tokens; recompress edited streams when literal expansion grows them.

    Token lengths and descriptor groups are fully recomputed. A bounded
    recompressor competes with literal expansion on growth. The wrapper's
    unknown and shift fields remain unchanged. Unmodified streams are byte exact.
    """
    old = decode(original)
    if len(old) != len(replacement): raise ToolError('logical_size_change_not_supported','H7A replacement must retain logical length')
    if old == replacement: return original
    shift = Binary(original).u32(16); encoded = []; max_distance = (1 << shift)-1
    for offset,length,distance,literal in tokens(original):
        if distance and all(replacement[offset+i] == replacement[offset+i-distance] for i in range(length)):
            encoded.append((1,struct.pack('>H', ((length-3)<<shift)|distance)))
        else:
            # Keeping original token boundaries prevents broad recompression drift.
            for i in range(length): encoded.append((0,bytes([replacement[offset+i]])))
    body = bytearray()
    for start in range(0,len(encoded),8):
        group = encoded[start:start+8]
        body.append(sum(flag<<i for i,(flag,_) in enumerate(group)))
        for _,value in group: body.extend(value)
    header = bytearray(original[:20]);struct.pack_into('>I',header,8,20+len(body))
    result = bytes(header)+body
    if len(result) > len(original):
        recompressed = encode_greedy(original, replacement)
        if len(recompressed) < len(result):result = recompressed
    if decode(result) != replacement: raise ToolError('compression_verification_failed','Encoder round trip mismatch')
    return result


def encode_greedy(original, replacement):
    """Bounded-window H7A recompression; preserve wrapper metadata and bit order."""
    from collections import deque
    shift=Binary(original).u32(16)
    max_distance=(1<<shift)-1
    max_length=(0xffff>>shift)+3
    positions={};body=bytearray();offset=0;bit=8;group=0
    def key(at):return replacement[at:at+3]
    def remember(at):
        expired=at-max_distance-1
        if expired >= 0:
            old=key(expired);chain=positions.get(old)
            if chain:
                while chain and chain[0] <= expired:chain.popleft()
                if not chain:positions.pop(old,None)
        if at+3 <= len(replacement):
            positions.setdefault(key(at),deque(maxlen=32)).append(at)
    while offset < len(replacement):
        if bit == 8:group=len(body);body.append(0);bit=0
        best_length=0;best_distance=0
        candidates=positions.get(key(offset),()) if offset+3 <= len(replacement) else ()
        limit=min(max_length,len(replacement)-offset)
        for previous in reversed(candidates):
            distance=offset-previous
            if distance > max_distance:break
            length=3
            while length < limit and replacement[offset+length] == replacement[offset+length-distance]:length+=1
            if length>best_length:best_length,best_distance=length,distance
            if length==limit:break
        if best_length >= 3:
            body[group] |= 1<<bit
            body.extend(struct.pack('>H',((best_length-3)<<shift)|best_distance))
            length=best_length
        else:
            body.append(replacement[offset]);length=1
        for at in range(offset,offset+length):remember(at)
        offset+=length;bit+=1
    header=bytearray(original[:20])
    struct.pack_into('>I',header,4,len(replacement))
    struct.pack_into('>I',header,8,20+len(body))
    return bytes(header)+body
