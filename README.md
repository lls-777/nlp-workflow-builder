# Natural Language Workflow Builder MVP

一个自然语言驱动的 Agent 工作流构建器 MVP。用户上传文件并用自然语言描述需求，系统会在必要时追问，生成可理解的处理方案，用户确认后执行，并支持基于反馈创建新版本后完整重跑。

## 运行环境

- 当前项目按 Python 3.9.6 验证。
- Streamlit 固定为 1.48.0。
- 固定 Streamlit 版本是为了兼容当前 Python 3.9.6 环境，避免误装需要更高 Python 版本的新版本。

## 核心功能

- 文档总结：读取 TXT、MD、PDF、DOCX，并生成摘要。
- 文档问答：读取文件、切分、检索，并基于证据回答。
- FAQ 客服问答：复用文档问答链路，不引入独立客服 Agent。
- 声明式表格分析：读取 CSV/XLSX，筛选、聚合、排序并生成图表规格。
- 一次性报告：定时需求会被明确降级为立即执行一次。
- Streamlit Web App：上传文件、输入自然语言、确认方案、查看结果和执行详情、提交反馈重跑。

## 架构说明

项目使用单一 Orchestrator 负责状态流转、Planner 调用、Executor 调用和本地记录。

核心边界：

- `core/workflow_schema.py` 定义严格 Pydantic v2 Workflow 契约。
- `core/step_registry.py` 声明有限可用步骤和参数模型。
- `core/executor.py` 在执行前校验 Workflow，并按线性步骤顺序执行。
- `core/planner.py` 第一版使用规则和模板生成 Workflow。
- `core/orchestrator.py` 封装会话、版本、执行和结果展示。
- `tools/` 放具体能力实现。
- `storage/` 使用 sqlite3 和本地文件存储，不引入复杂 ORM。
- `app.py` 只调用 Orchestrator，不直接拼 Workflow，也不直接调用工具。

Workflow 第一版只支持线性步骤，不实现 DAG。所有业务步骤必须来自 Step Registry。

## 安装方式

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

默认使用 mock LLM，不需要 API Key。需要接 OpenAI-compatible API 时，复制 `.env.example` 并配置对应环境变量。

## 环境变量

```bash
LLM_MODE=mock
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

`LLM_MODE=mock` 是默认模式，无需 API Key，也不会访问外部 LLM 服务。

## 运行测试

```bash
.venv/bin/python -m pytest
```

## 运行 Demo

文档总结：

```bash
.venv/bin/python -m examples.run_demo_workflow
```

文档问答和 FAQ：

```bash
.venv/bin/python -m examples.run_document_qa_workflow
```

表格分析：

```bash
.venv/bin/python -m examples.run_data_analysis_workflow
```

## 启动 Web App

```bash
.venv/bin/python -m streamlit run app.py --server.address localhost
```

本地访问：

```text
http://localhost:8501
```

上传限制：

- 单文件不超过 20MB。
- 最多 10 个文件。
- 总计不超过 50MB。

## 验收场景

1. 上传文档并生成总结：可执行。
2. 只基于文件回答问题：可执行。
3. 分析销售表格：可执行。
4. 基于 FAQ 模拟客服问答：可执行，复用文档问答链路。
5. 用户要求每周生成报告：降级为一次性报告，不创建后台定时任务。

详细说明见 [`docs/acceptance_scenarios.md`](docs/acceptance_scenarios.md)。

## 当前支持能力

- TXT、MD、PDF、DOCX 文档读取。
- 本地字符 n-gram TF-IDF 检索。
- answer_with_sources 在证据不足时拒答。
- CSV/XLSX 表格读取和声明式分析。
- chart_spec 生成，Streamlit 负责展示。
- sqlite3 本地保存 sessions、workflow_versions、runs、step_runs。
- 上传文件保存到 `data/uploads/`，文件名使用 UUID。

## 暂不支持能力

- 不支持真实联网检索。
- 不支持后台定时任务。
- 不执行模型生成的 Python。
- 不做拖拽节点编辑器。
- 不做复杂多 Agent 平台。
- 不做多用户权限或云同步。
- 不实现 DAG、增量执行或缓存复用。

## 工程边界

- 数据分析只允许声明式参数，不允许 `eval`、`exec`、`query`、`pandas_expression`、`lambda` 或模型生成代码。
- `uploaded_files_only` 和 `user_provided_only` 策略下禁止联网步骤。
- 用户上传文件只能来自 `data/uploads/` 或 `examples/`，路径校验使用 `Path.resolve()` 和 `relative_to()`。
- 工具和日志不得记录完整用户文件内容、API Key 或敏感信息。
