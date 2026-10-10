import struct
import pytest
from choops_py.formats.scne import preview_meshes


def scene_fixture():
    head = bytearray(1024)
    def u(off, value): struct.pack_into('>I', head, off, value)
    def pointer(field, target): u(field, target-field+1)
    u(0x44, 1); pointer(0x48, 0x54)
    off = 0x54
    pointer(off, 900); head[900:910] = 'mesh\0'.encode('utf-16-be')
    u(off+0x84, 1); pointer(off+0x88, 300)
    u(316, 4); u(332, 16); u(336, 64); u(340, 9)
    u(off+0x94, 2); pointer(off+0x9c, 400)
    head[408:416] = bytes.fromhex('2000000002030000')
    head[472:480] = bytes.fromhex('200c000003020800')
    u(off+0xa4, 0x20000010); u(off+0xa8, 4); u(off+0xac, 1)
    u(off+0x7c, 1); pointer(off+0x80, 600)
    u(600, 6); u(604, 0); u(608, 4)
    vertices = [(-1.,0.,-1.,0.,0.), (1.,0.,-1.,1.,0.), (-1.,0.,1.,0.,1.), (1.,0.,1.,1.,1.)]
    data = struct.pack('>4H', 0,1,2,3) + b''.join(struct.pack('>3f2e',*v) for v in vertices)
    return [bytes(head), data]


def test_declared_mesh_strip_winding_and_uv():
    result = preview_meshes(scene_fixture())
    assert result['warnings'] == []
    vertices = result['meshes'][0]['vertices']
    assert len(vertices) == 6
    assert vertices[0] == (-1.,0.,-1.,0.,0.)
    assert vertices[3] == (-1.,0.,1.,0.,1.)
    assert vertices[4] == (1.,0.,-1.,1.,0.)


def test_invalid_indices_skip_part_instead_of_guessing():
    head, data = scene_fixture()
    data = struct.pack('>H',99) + data[2:]
    result = preview_meshes([head,data])
    assert not result['meshes']
    assert 'index outside' in result['warnings'][0]


def test_bad_declaration_and_truncated_payload_are_reported():
    head, data = scene_fixture()
    modified = bytearray(head); modified[412:416] = b'BAD!'
    assert not preview_meshes([bytes(modified),data])['meshes']
    assert not preview_meshes([head,data[:-1]])['meshes']
    with pytest.raises(ValueError): preview_meshes([head])


def test_instance_matrix_places_geometry_without_changing_uv():
    head, data = scene_fixture()
    head = bytearray(head)
    struct.pack_into('>I',head,0x3c,1)
    struct.pack_into('>I',head,0x40,700-0x40+1)
    struct.pack_into('>16f',head,700,2,0,0,0,0,2,0,0,0,0,2,0,10,20,30,1)
    result = preview_meshes([bytes(head),data])
    assert result['meshes'][0]['vertices'][0] == (8.,20.,28.,0.,0.)


def test_signed_normalized_uvs():
    head,data = scene_fixture()
    head = bytearray(head);head[476:480] = bytes.fromhex('01020800')
    data = bytearray(data)
    struct.pack_into('>2h',data,8+12,32767,0)
    result = preview_meshes([bytes(head),bytes(data)])
    assert result['meshes'][0]['vertices'][0][3:] == (1.,0.)


def material_fixture(base_hash=0x12345678):
    head,data = scene_fixture()
    head = bytearray(head)+bytearray(3072)
    def u(off,value): struct.pack_into('>I',head,off,value)
    def ptr(field,target):u(field,target-field+1)
    u(0x20,2);ptr(0x24,1024);u(1024,0x12345678);u(1200,0x87654321)
    u(0x28,1);ptr(0x2c,1400);u(1400,0x11111111);u(1408,2);u(1412,96);ptr(1428,1600)
    u(0x30,1);ptr(0x38,1480);u(1488,0x11111111);ptr(1512,1800)
    # Put the normal map first in parameter memory and the sampler table.
    u(1600,0xab0d0064);struct.pack_into('>H',head,1616,0)
    u(1636,0xb6e7ae40);struct.pack_into('>H',head,1652,20)
    u(1812,0x87654321);u(1832,base_hash)
    return [bytes(head),data]


def test_material_reference_resolves_diffuse_not_first_normal_map():
    result=preview_meshes(material_fixture())
    assert result['meshes'][0]['batches'][0]['texture_index'] == 0
    assert result['meshes'][0]['batches'][0]['count'] == 6


def test_missing_diffuse_never_falls_back_to_embedded_normal_map():
    result=preview_meshes(material_fixture(base_hash=0x99999999))
    assert result['meshes'][0]['batches'][0]['texture_index'] is None


def test_non_power_of_two_compressed_texture_preview():
    import io
    from PIL import Image
    from choops_py.texture_tools.dds import compressed_preview
    # Opaque red DXT5 blocks; final block row extends past the logical image.
    block = bytes.fromhex('ffff000000000000') + bytes.fromhex('00f800f800000000')
    raw = compressed_preview(8,5,'DXT5',block*4)
    with Image.open(io.BytesIO(raw)) as image:
        assert image.size == (8,5)
        assert image.convert('RGBA').getpixel((7,4)) == (255,0,0,255)


@pytest.mark.gui
def test_floor_lift_is_preview_only_and_toggleable(qtbot, monkeypatch):
    from choops_py.studio.app import Window
    window = Window();qtbot.addWidget(window)
    original = [(0.,0.,0.,0.,0.)]*3
    window.scene_meshes = [{'name':'floor/court','vertices':original}, {'name':'arena/bottom','vertices':original}]
    window.scene_parts.addItem('All',-1)
    displayed=[]
    monkeypatch.setattr(window.scene_view,'set_meshes',lambda meshes:displayed.append(meshes))
    window.select_scene_part()
    assert displayed[-1][0]['vertices'][0][1] == 10.
    window.scene_lift_amount.setValue(20.)
    assert displayed[-1][0]['vertices'][0][1] == 20.
    assert displayed[-1][1]['vertices'][0][1] == 0.
    assert window.scene_meshes[0]['vertices'] == original
    window.scene_lift.setChecked(False)
    assert displayed[-1][0]['vertices'][0][1] == 0.
