from __future__ import annotations

import inspect
from pathlib import Path
from typing import Dict, List

import app
from streamlit.testing.v1 import AppTest


class SelectedFile:
    def __init__(self, name: str, content: bytes) -> None:
        self.name = name
        self._content = content

    def getvalue(self) -> bytes:
        return self._content


class UploadRecorder:
    def __init__(self, uploads_dir: Path) -> None:
        self.uploads_dir = uploads_dir
        self.calls: List[Dict[str, object]] = []

    def save_uploads(self, *, uploads: List[object], existing_paths: List[str]):
        self.calls.extend(
            {"original_filename": original_filename, "content": content}
            for original_filename, content in uploads
        )
        return [
            self.uploads_dir / f"stored-{original_filename}"
            for original_filename, _ in uploads
        ]


def test_save_selected_files_deduplicates_same_upload(tmp_path: Path) -> None:
    orchestrator = UploadRecorder(tmp_path)
    selected = SelectedFile("notes.txt", b"same content")
    saved_uploads: Dict[str, Dict[str, str]] = {}

    paths = app.save_selected_files(
        orchestrator,
        [selected, selected],
        saved_uploads,
    )

    assert paths == [str(tmp_path / "stored-notes.txt")]
    assert len(orchestrator.calls) == 1


def test_table_records_and_chart_frame_use_serializable_data() -> None:
    records = [{"region": "North", "sales": 10}, {"region": "South", "sales": 8}]

    assert app.table_records({"records": records}) == records
    frame = app.chart_frame({"data": records})
    assert frame.to_dict(orient="records") == records


def test_localize_text_translates_summary_labels() -> None:
    assert app.localize_text("Summary:\nShort.\n\nKey points:\n- One") == (
        "总结：\nShort.\n\n关键要点：\n- One"
    )


def test_public_error_summary_translates_table_file_error() -> None:
    assert app.public_error_summary("Unsupported table format: .md") == (
        "未找到可分析的表格文件，请上传 CSV 或 XLSX 文件。"
    )


def test_app_depends_on_orchestrator_service_instead_of_business_modules() -> None:
    source = inspect.getsource(app)

    assert "from tools" not in source
    assert "from storage" not in source
    assert "from core.executor" not in source
    assert "from core.planner" not in source
    assert "from core.workflow_schema" not in source


def test_streamlit_page_loads_without_exceptions() -> None:
    page = AppTest.from_file("app.py").run(timeout=10)

    assert not page.exception
    assert not page.error
    assert not page.warning
    assert "自然语言工作助手" in page.markdown[0].value
    assert [button.label for button in page.button] == [
        "生成处理方案 / 处理新需求",
        "开始新的会话",
    ]
