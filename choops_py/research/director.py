"""Read-only indexing of the observed DRCT resource; never execute its commands.

58DC8 relocates the reference, string, 223-group and token-map pointers. 5AA50
decodes command indices using the header threshold and a big-endian u16 map.
Group metadata and command operands remain opaque. This is not a script writer.
"""

from choops_py.formats.binary import Binary

MAGIC = 0x1FF1DF58
GROUPS = 223
MAX_BYTES = 32 * 1024 * 1024
MAX_RECORDS = 65536


def _binary(data):
    if not 32 <= len(data) <= MAX_BYTES:
        raise ValueError("Director resource exceeds bounds or is truncated")
    b = Binary(data)
    if b.u32(0) != MAGIC:
        raise ValueError("Not the observed Director resource")
    if not 1 <= b.u32(0x10) <= 256:
        raise ValueError("Unsupported Director command-index threshold")
    return b


def _target(b, field, size=1):
    target = b.relative(field)
    b.slice(target, size)
    return target


def inspect_director(data):
    """Index observed pointers; do not infer script entry or operand semantics."""
    b = _binary(data)
    reference_count, string_count = b.u16(6), b.u32(0x0C)
    if string_count > 4096:
        raise ValueError("Director string count exceeds inspection budget")
    b.slice(0x20, reference_count * 4)
    references = [_target(b, 0x20 + i * 4) for i in range(reference_count)]
    strings_at = _target(b, 0x14, string_count * 4)
    groups_at = _target(b, 0x18, GROUPS * 4)
    tokens_at = _target(b, 0x1C, 2)
    if any(x % 4 for x in (strings_at, groups_at)) or tokens_at % 2:
        raise ValueError("Unaligned Director table")
    strings = []
    characters = 0
    for i in range(string_count):
        at = _target(b, strings_at + i * 4, 2)
        if at % 2:
            raise ValueError("Unaligned Director string")
        end = at
        while b.slice(end, 2) != bytes(2):
            end += 2
            if end - at > 8192:
                raise ValueError("Director string exceeds inspection budget")
        text = b.slice(at, end - at).decode("utf-16-be")
        characters += len(text)
        if characters > 1024 * 1024:
            raise ValueError("Director strings exceed total inspection budget")
        strings.append(dict(offset=at, text=text))
    groups = []
    total = 0
    for i in range(GROUPS):
        field = groups_at + i * 4
        if not b.u32(field):
            continue
        at = _target(b, field, 28)
        count = b.u32(at)
        total += count
        if total > MAX_RECORDS:
            raise ValueError("Director record count exceeds inspection budget")
        b.slice(at + 28, count * 4)
        sections = [
            _target(b, at + j) if b.u32(at + j) else None
            for j in range(8, 28, 4)
        ]
        records = [_target(b, at + 28 + j * 4, 8) for j in range(count)]
        groups.append(dict(
            index=i, offset=at, opaque_word4=b.u32(at + 4),
            section_targets=sections, records=records,
        ))
    return dict(
        mode="read-only", reference_offsets=references, strings=strings,
        groups=groups, record_reference_count=total,
        token_map_offset=tokens_at, command_index_threshold=b.u32(0x10),
        command_execution_supported=False, writing_supported=False,
    )


def is_stream_end(data, position, end):
    """Check the native byte sentinel at a caller-proven command boundary.

    5AAD0 calls 5A708 before dispatch: zero is end-of-stream, even when there is
    no second byte for the command-index reader. This does not discover command
    boundaries, validate an entire program, execute commands or modify data.
    """
    b = _binary(data)
    if type(position) is not int or type(end) is not int:
        raise ValueError("Director stream bounds must be integers")
    if not 0 <= position < end <= len(data):
        raise ValueError("Invalid Director stream extent")
    return b.slice(position, 1) == bytes(1)


def decode_command(data, position, end):
    """Decode one index at a caller-proven position, not a whole program.

    Operand bytes may look like commands. The caller must supply a verified
    command boundary and stream end; this helper cannot establish either one.
    Call is_stream_end first when following native program control flow; the
    byte sentinel is separate from this command-index decoder.
    """
    b = _binary(data)
    if type(position) is not int or type(end) is not int:
        raise ValueError("Director stream bounds must be integers")
    if not 0 <= position < end <= len(data):
        raise ValueError("Invalid Director stream extent")
    start = position
    index = b.slice(position, 1)[0]
    position += 1
    if index < b.u32(0x10):
        if position == end:
            raise ValueError("Truncated Director command index")
        index = index * 256 + b.slice(position, 1)[0]
        position += 1
    table = _target(b, 0x1C, 2)
    token = b.u16(table + index * 2)
    return dict(offset=start, encoded_index=index, token=token, next=position)
