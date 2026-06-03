from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

import pandas as pd
import streamlit as st

from core.orchestrator import Orchestrator, OrchestratorResponse, RunPresentation


STATUS_LABELS = {
    "pending": "等待中",
    "validated": "已检查",
    "running": "处理中",
    "completed": "已完成",
    "failed": "失败",
    "skipped": "未执行",
}
OUTPUT_LABELS = {
    "Offline summary": "总结",
    "Summary": "总结",
    "Summary and key points": "总结与要点",
    "Answer": "回答",
    "Supporting excerpts": "文件依据",
    "Customer answer": "客服回答",
    "FAQ excerpts": "FAQ 依据",
    "Regional sales ranking": "区域销售排行",
    "Regional sales chart": "区域销售图表",
    "Business insights": "业务洞察",
    "Immediate report": "即时报告",
}


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def upload_key(file_name: str, content: bytes) -> str:
    return f"{file_name}:{len(content)}:{sha256(content).hexdigest()}"


def save_selected_files(
    orchestrator: Orchestrator,
    selected_files: Iterable[Any],
    saved_uploads: MutableMapping[str, Dict[str, str]],
) -> List[str]:
    new_uploads = []
    new_keys = []
    for selected_file in selected_files:
        content = selected_file.getvalue()
        key = upload_key(selected_file.name, content)
        if key in saved_uploads or key in new_keys:
            continue
        new_uploads.append((selected_file.name, content))
        new_keys.append(key)
    stored_paths = orchestrator.save_uploads(
        uploads=new_uploads,
        existing_paths=[item["path"] for item in saved_uploads.values()],
    )
    for key, stored_path, upload in zip(new_keys, stored_paths, new_uploads):
        saved_uploads[key] = {
            "name": upload[0],
            "path": str(stored_path),
        }
    return [item["path"] for item in saved_uploads.values()]


def table_records(value: Any) -> Any:
    if isinstance(value, Mapping) and "records" in value:
        return value["records"]
    return value


def chart_frame(chart_spec: Mapping[str, Any]) -> pd.DataFrame:
    data = chart_spec.get("data", [])
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        return pd.DataFrame()
    return pd.DataFrame(data)


def render_output(label: str, display_type: str, value: Any) -> None:
    st.subheader(OUTPUT_LABELS.get(label, label))
    if display_type == "text":
        st.markdown(localize_text(str(value or "暂无文字结果。")))
        return
    if display_type == "table":
        st.dataframe(table_records(value), use_container_width=True)
        return
    if display_type == "citations":
        render_citations(value)
        return
    if display_type == "chart":
        render_chart(value)
        return
    st.write(value)


def localize_text(value: str) -> str:
    replacements = (
        ("Summary:\n", "总结：\n"),
        ("\n\nKey points:\n", "\n\n关键要点：\n"),
        ("Report:\n", "报告：\n"),
        ("Business insights:\n", "业务洞察：\n"),
        ("\n\nRecommendation:\n", "\n\n建议：\n"),
        ("Answer based on the provided files:\n", "根据所提供文件回答：\n"),
    )
    localized_value = value
    for source, target in replacements:
        localized_value = localized_value.replace(source, target)
    return localized_value


def render_citations(value: Any) -> None:
    citations = value if isinstance(value, list) else []
    if not citations:
        st.info("未找到足够的文件依据。")
        return
    for index, citation in enumerate(citations, start=1):
        source_name = citation.get("source_name", "文件")
        excerpt = citation.get("excerpt", "")
        score = citation.get("score")
        score_text = f" · 相关度 {score:.3f}" if isinstance(score, (int, float)) else ""
        st.markdown(f"**依据 {index}：{source_name}**{score_text}")
        st.write(excerpt)


def render_chart(value: Any) -> None:
    chart_spec = value if isinstance(value, Mapping) else {}
    frame = chart_frame(chart_spec)
    x = chart_spec.get("x")
    y = chart_spec.get("y")
    if frame.empty or x not in frame or y not in frame:
        st.info("当前结果没有可展示的图表数据。")
        return
    chart_data = frame.set_index(x)[[y]]
    if chart_spec.get("chart_type") == "line":
        st.line_chart(chart_data)
    else:
        st.bar_chart(chart_data)
    with st.expander("查看图表数据"):
        st.dataframe(frame, use_container_width=True)


def render_presentation(presentation: RunPresentation) -> None:
    status_label = STATUS_LABELS.get(presentation.status, presentation.status)
    if presentation.status == "completed":
        st.success(f"处理完成 · 方案版本 {presentation.version}")
    else:
        reason = public_error_summary(presentation.error_message)
        st.error(f"处理未完成 · {status_label}。原因：{reason}")
    for output in presentation.outputs:
        render_output(output.label, output.display_type, output.value)
    with st.expander("查看执行详情"):
        st.write(f"方案版本：{presentation.version}")
        st.write(f"整体状态：{status_label}")
        if presentation.error_message:
            st.write(f"错误摘要：{presentation.error_message}")
        for index, activity in enumerate(presentation.activities, start=1):
            activity_status = STATUS_LABELS.get(activity.status, activity.status)
            st.write(f"{index}. {activity.title}：{activity_status}")
            if activity.error_message:
                st.write(f"   错误摘要：{activity.error_message}")


def initialize_page_state(orchestrator: Orchestrator) -> None:
    if "session_id" not in st.session_state:
        session = orchestrator.create_session()
        st.session_state.session_id = session["session_id"]
    st.session_state.setdefault("saved_uploads", {})
    st.session_state.setdefault("prepared_response", None)
    st.session_state.setdefault("presentation", None)
    st.session_state.setdefault("last_request", "")
    st.session_state.setdefault("upload_widget_version", 0)


def reset_page_state(orchestrator: Orchestrator) -> None:
    session = orchestrator.create_session()
    st.session_state.session_id = session["session_id"]
    st.session_state.saved_uploads = {}
    st.session_state.prepared_response = None
    st.session_state.presentation = None
    st.session_state.last_request = ""
    st.session_state.upload_widget_version += 1


def saved_paths() -> List[str]:
    return [
        item["path"] for item in st.session_state.saved_uploads.values()
    ]


def prepare_request(
    orchestrator: Orchestrator,
    *,
    request_text: str,
    selected_files: Iterable[Any],
) -> None:
    save_selected_files(
        orchestrator,
        selected_files,
        st.session_state.saved_uploads,
    )
    st.session_state.last_request = request_text
    st.session_state.prepared_response = orchestrator.prepare_new_request(
        session_id=st.session_state.session_id,
        user_request=request_text,
        uploaded_files=saved_paths(),
    )
    st.session_state.presentation = None


def render_plan(orchestrator: Orchestrator, response: OrchestratorResponse) -> None:
    if response.message:
        st.info(response.message)
    if response.questions:
        for question in response.questions:
            st.write(f"- {question}")
    if response.state.value == "UNSUPPORTED":
        if st.button("立即生成一次报告", type="primary"):
            st.session_state.prepared_response = orchestrator.accept_one_time_report(
                session_id=st.session_state.session_id,
                user_request="立即生成一次报告",
                uploaded_files=saved_paths(),
            )
            st.rerun()
        return
    if response.plan is None:
        return
    st.subheader("处理方案")
    st.write(response.plan.plan_text)
    if st.button("确认并开始处理", type="primary"):
        result = orchestrator.execute_prepared_workflow(
            session_id=st.session_state.session_id,
            uploaded_files=saved_paths(),
            user_text=st.session_state.last_request,
        )
        st.session_state.presentation = orchestrator.present_result(result)
        st.session_state.prepared_response = None
        st.rerun()


def render_follow_up(orchestrator: Orchestrator) -> None:
    st.subheader("继续处理")
    follow_up = st.text_input(
        "可以继续提问，或使用同一批文件再次处理",
        key="follow_up_text",
    )
    if st.button("提交新问题") and follow_up.strip():
        result = orchestrator.rerun_current_workflow(
            session_id=st.session_state.session_id,
            uploaded_files=saved_paths(),
            user_text=follow_up.strip(),
        )
        st.session_state.last_request = follow_up.strip()
        st.session_state.presentation = orchestrator.present_result(result)
        st.rerun()

    feedback = st.text_area(
        "需要调整处理方式时，请描述修改要求",
        key="feedback_text",
    )
    if st.button("更新处理方案") and feedback.strip():
        st.session_state.prepared_response = orchestrator.revise_current_workflow(
            session_id=st.session_state.session_id,
            feedback=feedback.strip(),
        )
        st.session_state.presentation = None
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="自然语言工作助手", layout="wide")
    orchestrator = get_orchestrator()
    initialize_page_state(orchestrator)

    st.markdown(
        """
        <h1 style="
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
            line-height: 1.35;
            white-space: normal;
            word-break: keep-all;
        ">自然语言工作助手</h1>
        """,
        unsafe_allow_html=True,
    )
    st.write("上传文件并直接描述你希望完成的事情。")

    with st.sidebar:
        st.subheader("文件")
        selected_files = st.file_uploader(
            "上传需要处理的文件",
            type=["txt", "md", "pdf", "docx", "csv", "xlsx"],
            accept_multiple_files=True,
            key=f"uploaded_files_{st.session_state.upload_widget_version}",
        )
        st.caption("单文件不超过 20MB，最多 10 个文件，总计不超过 50MB。")
        if st.session_state.saved_uploads:
            st.write("当前已保存：")
            for item in st.session_state.saved_uploads.values():
                st.write(f"- {item['name']}")
        if st.button("开始新的会话"):
            reset_page_state(orchestrator)
            st.rerun()

    request_text = st.text_area(
        "请描述你的需求",
        placeholder="例如：请总结这份资料，或者：退款需要提供什么信息？",
    )
    if st.button("生成处理方案 / 处理新需求"):
        if not request_text.strip():
            st.warning("请先描述你的需求。")
        else:
            try:
                prepare_request(
                    orchestrator,
                    request_text=request_text.strip(),
                    selected_files=selected_files,
                )
            except ValueError as exc:
                st.error(friendly_error(exc))

    response = st.session_state.prepared_response
    if response is not None:
        try:
            render_plan(orchestrator, response)
        except ValueError as exc:
            st.error(friendly_error(exc))

    presentation = st.session_state.presentation
    if presentation is not None:
        render_presentation(presentation)
        if presentation.status in {"completed", "failed"}:
            try:
                render_follow_up(orchestrator)
            except ValueError as exc:
                st.error(friendly_error(exc))


def friendly_error(error: ValueError) -> str:
    message = str(error)
    if (
        "Cannot prepare workflow from state" in message
        or "Current workflow cannot run from state" in message
        or "Unsupported orchestrator transition" in message
    ):
        return "当前任务已完成，请点击“开始新的会话”，或输入反馈修改当前结果。"
    return message


def public_error_summary(error_message: Any) -> str:
    message = str(error_message or "").strip()
    if "Unsupported table format" in message:
        return "未找到可分析的表格文件，请上传 CSV 或 XLSX 文件。"
    if message:
        return message
    return "暂时无法完成处理，请展开执行详情查看原因。"


if __name__ == "__main__":
    main()
