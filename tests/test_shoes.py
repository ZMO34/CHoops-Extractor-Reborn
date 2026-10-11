import struct
import pytest
from PIL import Image
from choops_py.formats.binary import Binary
from choops_py.roster.shoes import player_fields,team_fields,texture_name
from choops_py.texture_tools.gtf import remap_preview
from choops_py.archive.hash_names import hash_name,namespace


def test_team_default_and_player_shoe_packing_use_distinct_offsets():
    team=bytearray(752);player=bytearray(308)
    struct.pack_into('>I',team,0x2e0,(2<<22)|(4<<17)|(12<<12)|0xabc)
    struct.pack_into('>I',team,0x2e8,1<<20)
    struct.pack_into('>I',player,0xa0,(2<<27)|(4<<22)|(12<<17)|0xabcd)
    struct.pack_into('>I',player,0xa8,1<<29)
    assert team_fields(Binary(team),0)==player_fields(Binary(player),0)
    assert player_fields(Binary(player),0)['home_shoe_texture']=='shoe_102_04.iff'
    assert player_fields(Binary(player),0)['away_shoe_texture']=='shoe_102_12.iff'
    assert texture_name(0,0,1)=='shoe_1.iff'
    assert texture_name(2,1,0) is None and texture_name(4,0,2) is None


def test_shoe_namespace_has_verified_families_and_body_variants():
    names=set(namespace())
    assert len([n for n in names if n.startswith('shoe_')])==90
    assert 'shoe_102_15.iff' in names and 'cloth_wishbone_thin.iff' in names


def test_ps3_green_luminance_remap_and_identity():
    image=Image.new('RGBA',(1,1),(10,80,150,30))
    assert remap_preview(image,0xaae4).getpixel((0,0))==(10,80,150,30)
    assert remap_preview(image,0xa9a8).getpixel((0,0))==(80,80,80,255)
    assert remap_preview(image,0).getpixel((0,0))==(0,0,0,0)
    assert remap_preview(image,0x5555).getpixel((0,0))==(255,255,255,255)
    with pytest.raises(ValueError):remap_preview(image,0x3ff)
