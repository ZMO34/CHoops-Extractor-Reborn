"""Recruit diagnostics stay read-only and cannot become a save-transfer workflow."""

from types import SimpleNamespace

import pytest
from test_recruit_pool import pool_fixture

pytestmark = pytest.mark.gui


def diagnostics(qtbot, payload=None):
    from PySide6.QtWidgets import QWidget

    from choops_py.studio.legacy_recruiting import RecruitingDiagnostics

    owner = QWidget()
    qtbot.addWidget(owner)
    raw = pool_fixture()[0] if payload is None else payload
    owner.roster = SimpleNamespace(data=bytearray(raw), edits=[], history=[])
    dialog = RecruitingDiagnostics(owner, owner.roster)
    qtbot.addWidget(dialog)
    return owner, dialog


def test_metadata_preferences_and_filtering_leave_all_source_bytes_untouched(qtbot):
    owner, dialog = diagnostics(qtbot)
    before = bytes(owner.roster.data)
    dialog.display(dialog.inspect(None))
    assert dialog.view.model().rowCount() == 1
    assert "3 reserved records" in dialog.status.text()
    assert "2 blank" in dialog.status.text()
    assert "not certified" in dialog.status.text()
    assert "Recruit slot 1" in dialog.details.toPlainText()
    assert "weight 1.00" in dialog.details.toPlainText()
    assert "history continuity" in dialog.status.text()
    dialog.search.setText("not a recruit")
    assert dialog.view.model().rowCount() == 0
    assert dialog.details.toPlainText() == ""
    dialog.search.clear()
    assert dialog.view.model().rowCount() == 1
    assert bytes(owner.roster.data) == before
    assert owner.roster.edits == [] and owner.roster.history == []


def test_unknown_preferences_are_unresolved_and_ordinary_rosters_fail_gracefully(qtbot):
    import struct

    data, start = pool_fixture()
    struct.pack_into(">I", data, start + 0xD8 + 0x40, (15 << 21) | (127 << 7))
    _, dialog = diagnostics(qtbot, data)
    dialog.display(dialog.inspect(None))
    assert "Uninitialized profile" in dialog.details.toPlainText()
    assert "unestablished_class_code" in dialog.details.toPlainText()
    _, invalid = diagnostics(qtbot, bytes(0xB0))
    invalid.display(invalid.inspect(None))
    assert "Recruiting records unavailable" in invalid.status.text()
    assert invalid.view.model() is None


@pytest.mark.parametrize("change", ["new_source", "changed_bytes", "closed"])
def test_delayed_worker_results_cannot_populate_changed_or_closed_views(qtbot, change):
    owner, dialog = diagnostics(qtbot)
    report = dialog.inspect(None)
    if change == "new_source":
        owner.roster = SimpleNamespace(data=bytearray(dialog.payload))
    elif change == "changed_bytes":
        owner.roster.data[-1] ^= 1
    else:
        dialog.mark_closed()
    dialog.display(report)
    assert dialog.view.model() is None
    if change != "closed":
        assert "source roster changed" in dialog.status.text()


def test_editor_button_inspects_without_exposing_transfer_mutations(qtbot, monkeypatch):
    from PySide6.QtWidgets import QPushButton
    from support import roster_fixture

    from choops_py.studio.app import Window

    window = Window()
    qtbot.addWidget(window)
    model = roster_fixture()
    window.display_roster(model)
    before = bytes(model.data)
    monkeypatch.setattr(
        window, "run_job", lambda _label, work, display: display(work(None))
    )
    button = next(
        b
        for b in window.findChildren(QPushButton)
        if b.text() == "Recruiting diagnostics…"
    )
    button.click()
    dialog = window.recruiting_diagnostics
    assert "Recruiting records unavailable" in dialog.status.text()
    assert bytes(model.data) == before and model.edits == []
    # No transfer, signing, applying or saving controls exist in the diagnostic view.
    assert [b.text() for b in dialog.findChildren(QPushButton)] == [
        "Inspect native Legacy aggregate…",
    ]
    window.display_roster(model)
    assert dialog.closed


def test_backend_tab_is_available_without_a_save_and_component_errors_are_visible(
    qtbot,
):
    from test_legacy_backend import aggregate_fixture
    from choops_py.research.legacy_backend import inspect_legacy_aggregate
    from PySide6.QtWidgets import QTabWidget

    owner, dialog = diagnostics(qtbot)
    assert dialog.findChild(QTabWidget).tabText(1) == "Legacy backend"
    assert dialog.backend_view.model().rowCount() == 17
    before = bytes(owner.roster.data)
    dialog.display_aggregate(inspect_legacy_aggregate(aggregate_fixture(), before))
    assert "0 component audit errors" in dialog.aggregate_status.text()
    assert "correspondence" in dialog.aggregate_status.text()
    dialog.backend_view.selectRow(13)
    assert "native_portal_installed" in dialog.backend_details.toPlainText()
    assert bytes(owner.roster.data) == before
    owner.roster.data[-1] ^= 1
    dialog.display_aggregate({"error": "must not replace stale results"})
    assert "source roster changed" in dialog.aggregate_status.text()


def test_aggregate_picker_reads_only_exact_size_and_clears_failed_prior_data(
    qtbot, tmp_path, monkeypatch
):
    from PySide6.QtWidgets import QFileDialog
    from test_legacy_backend import aggregate_fixture

    owner, dialog = diagnostics(qtbot)
    owner.active = False
    owner.run_job = lambda _label, work, display: display(work(None))
    path = tmp_path / "aggregate.bin"
    path.write_bytes(aggregate_fixture())
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: (str(path), ""))
    before = bytes(owner.roster.data)
    dialog.open_aggregate()
    assert "0 component audit errors" in dialog.aggregate_status.text()
    dialog.backend_view.selectRow(13)
    assert "active_capacity" in dialog.backend_details.toPlainText()
    path.write_bytes(b"wrong whole save")
    dialog.open_aggregate()
    assert "exactly" in dialog.aggregate_status.text()
    assert dialog.backend_details.toPlainText() == ""
    assert dialog.backend_view.model().rowCount() == 17
    assert bytes(owner.roster.data) == before
    assert path.read_bytes() == b"wrong whole save"


def test_schedule_and_history_tabs_inspect_snapshot_without_editing(qtbot):
    from test_legacy_schedule_history import native_fixture

    owner, dialog = diagnostics(qtbot, native_fixture())
    before = bytes(owner.roster.data)
    dialog.display(dialog.inspect(None))
    assert dialog.schedule_view.model().rowCount() == 2
    assert "5 roster fixtures" in dialog.schedule_status.text()
    assert dialog.history_view.model().rowCount() == 2
    assert "4 referenced statistics records" in dialog.history_status.text()
    dialog.schedule_view.selectRow(1)
    assert "native_tournament_event_skipped" in dialog.schedule_details.toPlainText()
    assert "packed_record_sha256" in dialog.history_details.toPlainText()
    assert bytes(owner.roster.data) == before and owner.roster.edits == []
    dialog.display_research(
        {
            "scheduling": {"error": "unavailable"},
            "player_history": {"error": "unavailable"},
        }
    )
    assert dialog.history_details.toPlainText() == ""
    assert dialog.schedule_details.toPlainText() == ""


def test_stale_worker_cannot_fill_schedule_or_history_tabs(qtbot):
    from test_legacy_schedule_history import native_fixture

    owner, dialog = diagnostics(qtbot, native_fixture())
    report = dialog.inspect(None)
    owner.roster.data[-1] ^= 1
    dialog.display(report)
    assert dialog.schedule_view.model() is None
    assert dialog.history_view.model() is None


def test_portal_research_is_read_only_and_does_not_claim_native_settings(qtbot):
    from PySide6.QtWidgets import QPlainTextEdit, QTabWidget

    owner, dialog = diagnostics(qtbot)
    before = bytes(owner.roster.data)
    tabs = dialog.findChild(QTabWidget)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Portal research")
    page = tabs.widget(index)
    assert isinstance(page, QPlainTextEdit) and page.isReadOnly()
    assert "not working game" in page.toPlainText()
    assert "Not implementation-ready" in page.toPlainText()
    assert bytes(owner.roster.data) == before


def test_both_node_pools_display_snapshot_counts_and_clear_on_source_change(qtbot):
    from test_legacy_backend import aggregate_fixture
    from test_school_recruiting import complete_state
    from choops_py.research.legacy_backend import inspect_legacy_aggregate

    roster, state, _, _ = complete_state()
    aggregate = aggregate_fixture()
    aggregate[0x11418:0x529BC] = state
    owner, dialog = diagnostics(qtbot, roster)
    before = bytes(owner.roster.data)
    report = inspect_legacy_aggregate(aggregate, dialog.payload)
    dialog.display_aggregate(report)
    assert dialog.pool_view.model().rowCount() == 2
    assert "complete disjoint ownership" in dialog.pool_status.text()
    dialog.pool_view.selectRow(1)
    assert '"free_nodes_traced": 16000' in dialog.pool_details.toPlainText()
    assert bytes(owner.roster.data) == before
    owner.roster.data[-1] ^= 1
    dialog.display_aggregate(report)
    assert dialog.pool_view.model().rowCount() == 0
    assert not dialog.pool_details.toPlainText()
    assert "source roster changed" in dialog.pool_status.text()


def test_failed_secondary_audit_is_visible_without_hiding_primary(qtbot):
    from test_legacy_backend import aggregate_fixture
    from choops_py.research.legacy_backend import inspect_legacy_aggregate

    _, dialog = diagnostics(qtbot)
    dialog.display_aggregate(
        inspect_legacy_aggregate(aggregate_fixture(), dialog.payload)
    )
    assert dialog.pool_view.model().rowCount() == 2
    assert "not verified" in dialog.pool_status.text()
    dialog.pool_view.selectRow(1)
    assert '"error"' in dialog.pool_details.toPlainText()
    dialog.display_aggregate({"error": "bad component"})
    assert dialog.pool_view.model().rowCount() == 0
    assert not dialog.pool_details.toPlainText()
