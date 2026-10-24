"""Native NBA11 provider codes are not serialized registry categories."""

# 0x657824 switches over 41 provider selectors, then chooses a 31-category
# registry and a full-word player key. Verified by bounded native instructions.
_CATEGORIES = (
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    2,
    3,
    4,
    5,
    6,
    11,
    12,
    13,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    7,
    10,
    9,
    8,
)
_FIELDS = (
    0xD4,
    0xD8,
    0xDC,
    0xE0,
    0xE4,
    0xE8,
    0xEC,
    0xF0,
    0xF4,
    0xF8,
    0xFC,
    0x100,
    0x104,
    0x108,
    0x10C,
    0x110,
    0x154,
    0x158,
    0x15C,
    0x160,
    0x124,
    0x128,
    0x12C,
    0x130,
    0x134,
    0x138,
    0x13C,
    0x140,
    0x144,
    0x148,
    0x14C,
    0x150,
    0x164,
    0x168,
    0x16C,
    0x170,
    0x174,
    0x11C,
    0x114,
    0x118,
    0x120,
)
_ALTERNATE_PAIRS = ((16, 17), (18, 19), (30, 31), (32, 33), (34, 35))


def signature_binding(selector, alternate=False):
    """Return an established provider/category/key binding, never an animation ID.

    alternate models the native third argument's zero/nonzero selection of the
    paired player key field. Its basketball semantics are intentionally unnamed.
    Invalid selectors reject rather than following native's category-zero default.
    """
    if type(selector) is not int or not 0 <= selector < len(_CATEGORIES):
        raise ValueError("Choose a native provider selector from 0 through 40")
    if type(alternate) is not bool:
        raise ValueError("Alternate-field selection must be an explicit boolean")
    field_selector = selector
    if alternate:
        for a, b in _ALTERNATE_PAIRS:
            if selector in (a, b):
                field_selector = b if selector == a else a
                break
    return dict(
        selector=selector,
        alternate_field=alternate,
        registry_category=_CATEGORIES[selector],
        player_key_offset=_FIELDS[field_selector],
        player_key_bytes=4,
        native_consumer="0x657824",
        native_target_binding_established=False,
    )


def registry_binding_selectors(category):
    if type(category) is not int or not 0 <= category <= 30:
        raise ValueError("Choose a serialized registry category from 0 through 30")
    return [i for i, value in enumerate(_CATEGORIES) if value == category]
