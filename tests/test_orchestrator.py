from __future__ import annotations

from pathlib import Path

from config import EXAMPLES_DIR
from core.orchestrator import Orchestrator
from core.orchestrator_state import OrchestratorState
from core.workflow_schema import WorkflowStatus
from storage.file_store import FileStore
from storage.sqlite_store import SQLiteStore


def create_orchestrator(tmp_path: Path) -> Orchestrator:
    uploads_dir = tmp_path / "uploads"
    artifacts_dir = tmp_path / "artifacts"
    return Orchestrator(
        store=SQLiteStore(tmp_path / "app.db"),
        file_store=FileStore(
            uploads_dir=uploads_dir,
            artifacts_dir=artifacts_dir,
            allowed_source_roots=(EXAMPLES_DIR, uploads_dir),
        ),
    )


def test_orchestrator_records_summary_run_and_step_runs(tmp_path: Path) -> None:
    orchestrator = create_orchestrator(tmp_path)
    orchestrator.create_session("session_1")
    prepared = orchestrator.prepare_workflow(
        session_id="session_1",
        user_request="请总结这份文件",
        uploaded_files=[EXAMPLES_DIR / "sample.txt"],
    )

    assert prepared.state == OrchestratorState.AWAITING_CONFIRMATION
    result = orchestrator.confirm_and_execute(
        session_id="session_1",
        workflow_inputs={"source_files": [str(EXAMPLES_DIR / "sample.txt")]},
    )

    assert result.status == WorkflowStatus.COMPLETED
    assert orchestrator.store.get_session("session_1")["state"] == (
        OrchestratorState.COMPLETED.value
    )
    runs = orchestrator.store.list_runs("session_1")
    assert len(runs) == 1
    assert len(orchestrator.store.list_step_runs(runs[0]["run_id"])) == 2


def test_orchestrator_feedback_creates_version_two_and_full_rerun(
    tmp_path: Path,
) -> None:
    orchestrator = create_orchestrator(tmp_path)
    orchestrator.create_session("session_1")
    prepared = orchestrator.prepare_workflow(
        session_id="session_1",
        user_request="请总结这份文件",
        uploaded_files=[EXAMPLES_DIR / "sample.txt"],
    )
    orchestrator.confirm_and_execute(
        session_id="session_1",
        workflow_inputs={"source_files": [str(EXAMPLES_DIR / "sample.txt")]},
    )

    revised = orchestrator.revise_current_workflow(
        session_id="session_1",
        feedback="缩短到 80 字，保留 3 个要点",
    )

    assert revised.plan is not None
    assert revised.plan.workflow.id == prepared.plan.workflow.id
    assert revised.plan.workflow.version == 2
    rerun = orchestrator.confirm_and_execute(
        session_id="session_1",
        workflow_inputs={"source_files": [str(EXAMPLES_DIR / "sample.txt")]},
    )
    assert rerun.status == WorkflowStatus.COMPLETED
    assert len(orchestrator.store.list_workflow_versions("session_1")) == 2
    assert len(orchestrator.store.list_runs("session_1")) == 2


def test_new_document_question_reuses_version_and_creates_new_run(
    tmp_path: Path,
) -> None:
    orchestrator = create_orchestrator(tmp_path)
    orchestrator.create_session("session_1")
    prepared = orchestrator.prepare_workflow(
        session_id="session_1",
        user_request="What do users value?",
        uploaded_files=[EXAMPLES_DIR / "sample.txt"],
    )
    assert prepared.plan is not None

    first_result = orchestrator.confirm_and_execute(
        session_id="session_1",
        workflow_inputs={
            "source_files": [str(EXAMPLES_DIR / "sample.txt")],
            "question": "What do users value?",
        },
    )
    second_result = orchestrator.run_current_workflow(
        session_id="session_1",
        workflow_inputs={
            "source_files": [str(EXAMPLES_DIR / "sample.txt")],
            "question": "What should the first release keep simple?",
        },
    )

    assert first_result.status == WorkflowStatus.COMPLETED
    assert second_result.status == WorkflowStatus.COMPLETED
    versions = orchestrator.store.list_workflow_versions("session_1")
    runs = orchestrator.store.list_runs("session_1")
    assert len(versions) == 1
    assert len(runs) == 2
    assert {run["workflow_version"] for run in runs} == {1}


def test_orchestrator_weekly_report_requires_one_time_fallback_acceptance(
    tmp_path: Path,
) -> None:
    orchestrator = create_orchestrator(tmp_path)
    orchestrator.create_session("session_1")
    unsupported = orchestrator.prepare_workflow(
        session_id="session_1",
        user_request="请每周一自动生成报告",
        uploaded_files=[EXAMPLES_DIR / "sample.txt"],
    )

    assert unsupported.state == OrchestratorState.UNSUPPORTED
    assert "暂不支持" in unsupported.message

    accepted = orchestrator.accept_one_time_report(
        session_id="session_1",
        user_request="接受立即生成一次报告",
        uploaded_files=[EXAMPLES_DIR / "sample.txt"],
    )
    assert accepted.state == OrchestratorState.AWAITING_CONFIRMATION
    assert accepted.plan is not None
    serialized_workflow = accepted.plan.workflow.model_dump_json().lower()
    for forbidden_term in ("schedule", "cron", "timer", "recurrence", "定时"):
        assert forbidden_term not in serialized_workflow
