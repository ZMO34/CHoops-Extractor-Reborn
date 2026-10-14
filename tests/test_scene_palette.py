import pytest
from choops_py.formats.scene_palette import associate_palette, palette_tint
from choops_py.roster.schema import CONFIRMED_PALETTE_CAPTIONS


def test_floor_layers_preserve_arena_vertices_and_unknown_materials():
    from choops_py.formats.scene_palette import floor_layers
    batches = [{'material_hash': h, 'first': i * 3, 'count': 3} for i, h in
               enumerate((2310823066, 2600458314, 2218775043, 123))]
    source = [{'court_surface': True, 'vertices': [(0, 0, 0)], 'batches': batches},
              {'court_surface': False, 'vertices': [(1, 2, 3)], 'batches': batches}]
    filtered = floor_layers(source, False, False)
    assert filtered[0]['batches'] == batches[3:]
    assert filtered[1]['batches'] == batches
    assert filtered[0]['vertices'] is source[0]['vertices']
    assert source[0]['batches'] == batches
    assert floor_layers(source)[0]['batches'] == batches


def test_missing_floor_layers_use_authored_game_coordinates_not_apron_bounds():
    from choops_py.formats.scene_palette import supplement_floor_layers, floor_layers
    apron = {'court_surface': True, 'name': 'floor/floor', 'vertices': [(-500, 0, -500)],
             'batches': [{'material_hash': 123, 'first': 0, 'count': 1}]}
    lines = {'court_surface': True, 'name': 'floor/lines', 'vertices': [(17, 0, 4), (18, 0, 5)],
             'batches': [{'material_hash': 2310823066, 'first': 0, 'count': 1, 'texture': 'ink'},
                         {'material_hash': 2218775043, 'first': 1, 'count': 1, 'texture': 'ink'}]}
    selected = {'meshes': [apron], 'images': {'wood': b'art'}, 'warnings': []}
    original = {'meshes': [lines], 'images': {'ink': b'lines'}, 'warnings': []}
    result = supplement_floor_layers(selected, original)
    overlay = result['meshes'][1]
    assert overlay['vertices'] is lines['vertices']
    assert overlay['batches'][0]['texture'] == '__game_floor_lines/ink'
    assert result['images']['__game_floor_lines/ink'] == b'lines'
    assert floor_layers(result['meshes'], False, True)[1]['batches'][0]['first'] == 1
    assert len(supplement_floor_layers(result, original)['meshes']) == 2
    assert len(selected['meshes']) == 1 and lines['batches'][0]['texture'] == 'ink'


def test_runtime_material_route_uses_current_palette_and_preserves_source():
    colors = ['#BEBEBEFF']*31
    colors[19] = '#80400080'
    source = [{'batches':[{'material_hash':0x8a90aba9,'supports_diffuse_color':True,'first':0,'count':3}]}]
    result = associate_palette(source, colors)
    assert result[0]['batches'][0]['palette_tint'] == pytest.approx((.2158605,.0512695,0.,128/255))
    assert 'palette_tint' not in source[0]['batches'][0]
    colors[19] = '#FF0000FF'
    assert associate_palette(source, colors)[0]['batches'][0]['palette_tint'] == (1.,0.,0.,1.)
    assert associate_palette(source, None)[0]['batches'][0]['palette_tint'] is None


def test_default_gray_and_unrecognized_material_do_not_guess_colors():
    colors = ['#BEBEBEFF']*31
    assert palette_tint(0x8a90aba9, colors) is None
    assert palette_tint(0x12345678, colors) is None
    assert CONFIRMED_PALETTE_CAPTIONS[19] == 'Key'
    assert CONFIRMED_PALETTE_CAPTIONS[2] == 'Key Circle Outer'


def test_modded_shader_without_diffuse_uniform_declines_roster_binding():
    source = [{'batches':[{'material_hash':0x8a90aba9, 'supports_diffuse_color':False}]}]
    assert associate_palette(source, ['#FF0000FF']*31)[0]['batches'][0]['palette_tint'] is None
