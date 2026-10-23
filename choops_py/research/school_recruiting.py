"""Native school-to-recruit ownership audits, without allocating or editing data.

The second recruiting pool is independent of recruit-to-school interests.
References in a serialized component are relative to the decoded roster base.
"""

from hashlib import sha256
from struct import unpack_from

CAPACITY = 16000
STRIDE = 8


def inspect_school_recruit_graph(
    nodes: bytes,
    heads: dict[int, int],
    *,
    recruit_start: int,
    recruit_count: int,
    free_head: int,
) -> dict:
    """Trace all supplied school lists and the second free list.

    Native 0x5CA108 checks disjoint ownership and complete coverage of this pool.
    0x5C3580 follows school anchor +0x260 and node next +4. 0x5C34F0
    initializes pointer=0, next=-1, word+6=0; 0x5C5468 rebases nonnull
    pointers against the roster base. No relation to first-pool membership
    is assumed: the two lists have different native consumers.
    """
    if not isinstance(nodes, (bytes, bytearray)) or len(nodes) != CAPACITY * STRIDE:
        raise ValueError(
            "school recruit block must contain exactly 16000 eight-byte nodes"
        )
    if (
        type(recruit_start) is not int
        or recruit_start < 0xB0
        or recruit_start % 4
        or type(recruit_count) is not int
        or not 1 <= recruit_count <= 16384
        or recruit_start + recruit_count * 0xD8 > 64 * 1024 * 1024
    ):
        raise ValueError("invalid recruit directory")
    if not isinstance(heads, dict) or not 1 <= len(heads) <= 8192:
        raise ValueError("school heads must be a bounded nonempty mapping")
    if any(type(school) is not int or not 0 <= school < 8192 for school in heads):
        raise ValueError("invalid school identity")

    def node_index(value):
        if type(value) is not int:
            raise ValueError("school recruit node index must be an integer")
        if value in (-1, 0xFFFF):
            return None
        if not 0 <= value < CAPACITY:
            raise ValueError("unsupported school recruit node index")
        return value

    # Validate even empty heads and the free head, before traversing any chain.
    for head in heads.values():
        node_index(head)
    node_index(free_head)
    owners = {}
    chains = []
    free_count = 0
    entries = [(school, heads[school]) for school in sorted(heads)]
    entries.append((None, free_head))
    for school, head in entries:
        index = node_index(head)
        seen_recruits = set()
        chain = []
        while index is not None:
            if index in owners:
                raise ValueError(
                    f"school recruit node cycle or shared ownership at {index}"
                )
            owners[index] = school
            pointer, next_index, word6 = unpack_from(">IhH", nodes, index * STRIDE)
            if school is None:
                if pointer or word6:
                    raise ValueError(
                        "school recruit free list contains an uncleared node"
                    )
                free_count += 1
            else:
                slot, remainder = divmod(pointer - recruit_start, 0xD8)
                if not pointer or remainder or not 0 <= slot < recruit_count:
                    raise ValueError(
                        "school recruit node does not reference an exact recruit anchor"
                    )
                if slot in seen_recruits:
                    raise ValueError("duplicate recruit in school recruiting list")
                seen_recruits.add(slot)
                chain.append(
                    dict(
                        index=index,
                        recruit_slot=slot,
                        roster_relative_reference=pointer,
                        word_6_raw=word6,
                        scholarship_offer_bit_7=bool(word6 & 0x80),
                    )
                )
            index = node_index(next_index)
        if school is not None:
            chains.append(dict(school_index=school, nodes=chain))
    return dict(
        schema=1,
        source_sha256=sha256(nodes).hexdigest(),
        node_capacity=CAPACITY,
        school_heads_supplied=len(heads),
        live_nodes=len(owners) - free_count,
        free_nodes_traced=free_count,
        unowned_nodes=CAPACITY - len(owners),
        all_nodes_owned=len(owners) == CAPACITY,
        chains=chains,
        native_pool_insertion_installed=False,
        gameplay_ready=False,
    )
