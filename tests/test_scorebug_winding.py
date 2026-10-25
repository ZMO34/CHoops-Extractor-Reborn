import pytest

from choops_py.modding.scorebug_layout import inspect_xy_winding


def test_stock_facing_and_reversed_rewrite_are_distinguished():
    stock = [(10, 0), (10, 2), (0, 0), (0, 0), (10, 2), (0, 2)]
    reversed_quad = [(0, 0), (0, 2), (10, 0), (10, 0), (0, 2), (10, 2)]
    assert inspect_xy_winding(stock) == dict(positive=2, negative=0, edge_on=0)
    assert inspect_xy_winding(reversed_quad) == dict(positive=0, negative=2, edge_on=0)
    assert len(stock) == len(reversed_quad)


def test_edge_on_geometry_and_invalid_inputs_are_separate():
    assert inspect_xy_winding([(0, 0), (1, 0), (2, 0)])["edge_on"] == 1
    for vertices in [[(0, 0)], [(0, 0), (1, 0), (float("nan"), 2)]]:
        with pytest.raises(ValueError):
            inspect_xy_winding(vertices)
