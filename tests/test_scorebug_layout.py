import struct

import pytest

from choops_py.modding.scorebug_layout import edit_scene


def fixture():
    head=bytearray(1200);payload=bytearray(4*36+8)
    def u(at,v):struct.pack_into('>I',head,at,v)
    def ptr(at,target):u(at,target-at+1)
    u(0x44,1);ptr(0x48,128);ptr(128,1000);head[1000:1010]='quad\0'.encode('utf-16-be')
    u(128+0x84,1);ptr(128+0x88,320)
    u(320+16,4);u(320+32,36);u(320+40,1)
    u(128+0x94,3);ptr(128+0x9c,400)
    for i,code in enumerate(['2000000002030000','200c000003020800','2010000002040300']):head[408+i*64:416+i*64]=bytes.fromhex(code)
    for i,(x,y,u_,v) in enumerate([(0,0,0,1),(2,2,0,0),(6,0,1,1),(8,2,1,0)]):
        struct.pack_into('>3f2e4fI',payload,i*36,x,y,5,u_,v,.1,.2,.3,.8,0xdeadbeef)
    payload[-8:]=b'KEEPBYTE'
    # One paired authored text record and its independent marker translations.
    u(0x4c,1);ptr(0x50,640);ptr(704,1040);head[1040:1056]='message\0'.encode('utf-16-be')
    for at in (688,736,848,864):struct.pack_into('>3f',head,at,10,20,3)
    ptr(880,1040)
    return [bytes(head),bytes(payload)]


def test_rectification_preserves_interleaved_data_and_moves_all_text_copies():
    source=fixture();result,report=edit_scene(source,dict(parts={'quad':dict(bounds=[20,30,24,34],rectify_uv=True,rgb_scale=.5,z_offset=1)},text={'message':[70,80]}))
    assert list(map(len,result))==list(map(len,source))
    for i in range(4):
        x,y,z=struct.unpack_from('>3f',result[1],i*36);u,v=struct.unpack_from('>2e',result[1],i*36+12)
        assert x==20+u*4 and y==34-v*4 and z==6
        assert result[1][i*36+32:i*36+36]==source[1][i*36+32:i*36+36]
        assert struct.unpack_from('>4f',result[1],i*36+16)==pytest.approx([.05,.1,.15,.8])
    assert result[1][-8:]==source[1][-8:]
    for at in (688,736,848,864):assert struct.unpack_from('>3f',result[0],at)==(70,80,3)
    assert report[-1]['matching_marker']
    assert edit_scene(source,{})[0]==source


def test_bad_target_or_unmatched_marker_does_not_mutate_input():
    source=fixture();before=list(source)
    with pytest.raises(ValueError,match='Unknown HUD part'):edit_scene(source,{'parts':{'missing':{'hide':True}}})
    with pytest.raises(ValueError,match='HUD rectangle'):edit_scene(source,{'parts':{'quad':{'bounds':[0,0,0,4]}}})
    head=bytearray(source[0]);struct.pack_into('>f',head,864,999)
    with pytest.raises(ValueError,match='matching HUD marker'):edit_scene([bytes(head),source[1]],{'text':{'message':[1,2]}})
    assert source==before


def test_hide_changes_only_alpha_and_unknown_vertex_words_stay_exact():
    source=fixture();result,_=edit_scene(source,{'parts':{'quad':{'hide':True}}})
    assert result[0]==source[0]
    for i in range(4):
        assert result[1][i*36:i*36+28]==source[1][i*36:i*36+28]
        assert struct.unpack_from('>f',result[1],i*36+28)[0]==0
        assert result[1][i*36+32:i*36+36]==source[1][i*36+32:i*36+36]


def test_inventory_includes_sixth_man_and_named_authored_anchor():
    from support import iff_fixture
    from choops_py.formats.cdf_backed_iff_writer import name_trailer
    from choops_py.formats.scorebug import inspect_iff
    raw=iff_fixture(fixture(),[(0xe26c9b5d,[0,0])])+name_trailer([dict(name='6th_man_meter',type='SCNE')])
    rows=inspect_iff(raw)
    assert rows[0]['name']=='6th_man_meter'
    assert rows[0]['text_anchors']==[dict(name='message',position=[10.,20.,3.],matrix_copies_match=True)]


def test_single_quad_requires_confirmed_restart_topology_and_keeps_indices():
    source=fixture();head=bytearray(source[0]);first=source[1][:144]
    payload=first+first+struct.pack('>9H',0,1,2,3,65535,4,5,6,7)
    struct.pack_into('>I',head,320+16,8)
    struct.pack_into('>III',head,128+0xa4,0x20000010,9,289)
    result,_=edit_scene([bytes(head),payload],{'parts':{'quad':{'bounds':[0,0,4,4],'rectify_uv':True,'single_quad':True}}})
    assert result[1][288:]==payload[288:]
    assert all(struct.unpack_from('>f',result[1],i*36+28)[0]==0 for i in range(4,8))
    head[128+0xa4:128+0xa8]=bytes(4)
    with pytest.raises(ValueError,match='restart strips'):edit_scene([bytes(head),payload],{'parts':{'quad':{'bounds':[0,0,4,4],'rectify_uv':True,'single_quad':True}}})
