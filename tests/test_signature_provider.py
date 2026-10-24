import pytest

from choops_py.research.signature_provider import (
    registry_binding_selectors,
    signature_binding,
)


def test_provider_code_is_not_the_serialized_category_number():
    assert signature_binding(20)["registry_category"] == 14
    assert signature_binding(20)["player_key_offset"] == 0x124
    assert signature_binding(14)["registry_category"] == 5
    assert signature_binding(0)["registry_category"] == 0
    assert signature_binding(0)["player_key_offset"] == 0xD4
    assert registry_binding_selectors(1) == list(range(1, 11))
    assert registry_binding_selectors(14) == [20]
    assert {signature_binding(i)["registry_category"] for i in range(41)} == set(
        range(31)
    )


def test_alternate_key_field_does_not_swap_registry_category():
    normal = signature_binding(16)
    alternate = signature_binding(16, True)
    assert normal["registry_category"] == alternate["registry_category"] == 11
    assert normal["player_key_offset"] == 0x154
    assert alternate["player_key_offset"] == 0x158
    assert signature_binding(17, True)["registry_category"] == 12
    assert signature_binding(17, True)["player_key_offset"] == 0x154
    assert signature_binding(20, True)["player_key_offset"] == 0x124


@pytest.mark.parametrize("selector", [True, -1, 41, None])
def test_unknown_provider_code_never_defaults_to_category_zero(selector):
    with pytest.raises(ValueError):
        signature_binding(selector)
