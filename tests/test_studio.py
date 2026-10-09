import os
import uuid
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from pathlib import Path
from choops_py.studio.app import Window, Rows, selected
from choops_py.studio.services import extract, JobContext, stage_folder
from choops_py.archive.usrdir_reader import Archive
from choops_py.archive.manifests import OUTPUT
from support import game_fixture, iff_fixture


def test_streaming_cancellation_and_collision(tmp_path):
    source=game_fixture(tmp_path/'game',iff_fixture())
    archive=Archive(source)
    job=JobContext()
    job.cancelled.set()
    output=OUTPUT/'temp'/(tmp_path.name+uuid.uuid4().hex)/'cancel'
    result=extract(archive,archive.entries,output,job)
    assert result['status']=='cancelled'
    assert result['completed']==0
    assert not list(output.glob('.extract_*'))
    with pytest.raises(ValueError,match='destination'):
        extract(archive,archive.entries,output)


def test_exclusive_extraction_and_folder_stage(tmp_path):
    source=game_fixture(tmp_path/'game',iff_fixture())
    archive=Archive(source)
    out=OUTPUT/'temp'/(tmp_path.name+uuid.uuid4().hex)/'rip'
    result=extract(archive,archive.entries,out)
    assert result['completed']==1
    assert (out/'ua000.iff').read_bytes()==archive.read(archive.entries[0])
    with pytest.raises(ValueError,match='existing'):
        extract(archive,archive.entries,out)
    mod=OUTPUT/'temp'/(tmp_path.name+uuid.uuid4().hex)/'mod'
    assert stage_folder(source,out,mod)['staged']==1
    assert (mod/'source_preconditions.json').exists()


def test_qt_game_model_and_navigation(qtbot,tmp_path):
    source=game_fixture(tmp_path/'game',iff_fixture())
    window=Window()
    qtbot.addWidget(window)
    window.show()
    window.open_game(source)
    qtbot.waitUntil(lambda: window.active is None,timeout=10000)
    assert window.archive is not None
    assert window.explorer.model().rowCount()==1
    window.search.setText('no matching entry')
    assert window.explorer.model().rowCount()==0
    window.search.setText('ua000')
    assert window.explorer.model().rowCount()==1
    window.explorer.selectRow(0)
    window.inspect_selected()
    qtbot.waitUntil(lambda: window.active is None,timeout=10000)
    assert window.nested.topLevelItemCount()==1
    for i in range(7):
        window.navigation.setCurrentItem(window.navigation.topLevelItem(i))
        assert window.pages.currentIndex()==i
    window.close()


def test_roster_redo_and_new_edit_clears_future():
    from support import roster_fixture
    model=roster_fixture()
    model.edit('players',0,'jersey_number',20)
    model.undo()
    assert model.rows['players'][0]['jersey_number']==10
    model.redo()
    assert model.rows['players'][0]['jersey_number']==20
    model.undo()
    model.edit('players',0,'jersey_number',30)
    model.redo()
    assert model.rows['players'][0]['jersey_number']==30


def test_source_precondition_rejects_changed_original(tmp_path):
    from choops_py.archive.build_copy import preflight
    source=game_fixture(tmp_path/'game',iff_fixture())
    archive=Archive(source)
    out=OUTPUT/'temp'/(tmp_path.name+uuid.uuid4().hex)/'rip'
    extract(archive,archive.entries,out)
    mod=OUTPUT/'temp'/(tmp_path.name+uuid.uuid4().hex)/'mod'
    stage_folder(source,out,mod)
    part=source/'PS3_GAME'/'USRDIR'/'0A'
    raw=bytearray(part.read_bytes())
    raw[4095]^=1
    part.write_bytes(raw)
    with pytest.raises(ValueError,match='changed'):
        preflight(source,mod)


def test_actual_cli_gui_launch(qapp):
    from PySide6.QtCore import QTimer
    from choops_py.cli import main
    QTimer.singleShot(100,qapp.quit)
    assert main(['gui'])==0


def test_archive_rejects_toc_overlap(tmp_path):
    import struct
    source=game_fixture(tmp_path/'game',iff_fixture())
    path=source/'PS3_GAME'/'USRDIR'/'0A'
    raw=bytearray(path.read_bytes());struct.pack_into('>I',raw,44,0);path.write_bytes(raw)
    with pytest.raises(ValueError,match='overlaps'):
        Archive(source)
