# 自然语言驱动的 Agent 工作流构建器需求文档

> 版本：v0.1  
> 状态：开发执行基线  
> 更新日期：2026-06-02  
> 原始需求来源：`nlp_agent.pdf`

## 1. 文档目的

本文档用于统一产品目标、MVP 范围、架构约束、验收标准和开发顺序。后续实现以本文档为基线；新增需求、边界调整和重要技术取舍应同步更新本文档及决策日志。

## 2. 项目概述

### 2.1 项目目标

构建一个面向普通用户的自然语言 Agent 工作流构建器。用户不需要理解代码、Agent、Chain、Tool、节点或参数，只需要描述想完成的事情，系统即可：

1. 理解用户目标。
2. 在信息不足时主动追问。
3. 生成人话版执行方案。
4. 在用户确认后真实执行任务。
5. 展示结果、依据和执行状态。
6. 根据用户后续反馈调整工作流并重新执行。

### 2.2 目标用户

目标用户是不具备技术背景的普通用户。产品需要隐藏内部技术复杂度，使用自然语言完成交互。

### 2.3 核心闭环

```text
用户描述需求
-> 系统判断信息是否充分
-> 信息不足时追问 1 到 3 个关键问题
-> 生成人话版执行方案
-> 用户确认执行
-> 校验并真实执行 Workflow
-> 展示结果、来源和运行状态
-> 用户提出修改意见
-> 创建新版本 Workflow
-> 用户确认后重新执行
```

## 3. 产品原则

### 3.1 设计原则

- 不构建复杂的多 Agent 平台。
- 不提供拖拽式节点编辑器。
- 不要求用户理解内部工作流语法。
- 前台不暴露 Agent、Chain、Tool、节点或参数等技术概念。
- 后台使用受约束的 Workflow JSON 表示可执行任务。
- Workflow Step 只能来自有限的 Step Registry。
- 每项承诺支持的能力都必须能够真实执行，不能只输出建议文本。
- 不支持的需求需要明确说明边界，不能由模型虚构能力。

### 3.2 MVP 产品形态

- 使用 Streamlit 构建本地启动的 Web App。
- 使用 OpenAI-compatible LLM API，并通过环境变量配置。
- 业务层通过轻量模型适配层调用 LLM，避免直接绑定单一供应商 SDK。
- 使用 SQLite 保存会话、Workflow 版本和执行记录。
- 使用本地文件目录保存上传文件和生成产物。

## 4. 用户体验要求

### 4.1 用户可见内容

普通用户只需要看到：

- 自然语言输入框和文件上传入口。
- 系统提出的补充问题。
- 人话版执行方案。
- 数据来源限制，例如“只使用你上传的文件，不访问网络”。
- 每一步的简短运行状态。
- 最终结果、图表、依据片段和可下载产物。
- 修改需求的自然语言输入入口。

### 4.2 执行详情

页面提供默认折叠的“执行详情”区域，用于工程评审和问题定位。该区域展示：

- Workflow JSON。
- Workflow 版本号。
- 每一步的执行状态。
- 输入输出摘要。
- 错误信息。
- 运行记录。

### 4.3 执行确认

系统生成方案后，默认需要用户确认才能执行。MVP 不做自动立即执行，也不做风险分级自动执行。

## 5. MVP 能力范围

### 5.1 P0：必须实现

#### 文档总结与资料整理

- 支持上传 `PDF`、`TXT`、`MD`、`DOCX`。
- 读取并整理文本。
- 根据用户要求生成摘要、要点列表或报告。
- 支持用户反馈，例如“简短一点”“改成表格”“增加建议”。

#### 文档问答

- 基于用户上传文档回答问题。
- 支持文本切分和简单检索。
- 展示答案及依据片段。
- 当用户要求“只使用上传文件”时，禁止联网检索。

#### 文件数据分析

- 支持上传 `CSV` 和 `XLSX`。
- 使用固定 `pandas` 操作读取和分析数据。
- 支持字段识别、统计摘要、筛选、聚合、排序和简单图表。
- 支持生成基于分析结果的业务建议。
- 不允许执行 LLM 生成的 Python 代码。

#### FAQ 客服问答封装

- 用户可以上传 FAQ、产品介绍或客服话术。
- 产品提供应用内模拟问答体验。
- 该场景复用文档切分、检索和依据回答能力，不实现独立客服 Agent。

#### 本地持久化与执行记录

- 保存会话。
- 保存每一个 Workflow 版本。
- 保存每次运行记录和步骤状态。
- 用户修改需求时创建新 Workflow 版本，不覆盖历史记录。

### 5.2 P1：时间允许时实现

#### 可控联网检索

- 默认关闭。
- 只有用户明确需要外部资料并授权后才允许使用。
- 人话版方案中必须明确说明将访问网络。
- 执行结果需要展示外部来源。
- 核心架构预留联网 Step，但 P1 不阻塞 P0 交付。

### 5.3 暂不实现

- 后台定时执行。
- 模型生成 Python 代码并执行。
- 图片 OCR 和扫描件识别。
- 多用户账号、权限系统和云端协作。
- 外部客服渠道接入。
- 拖拽式节点编辑器。
- 复杂工作流分支、并行执行和 DAG 调度。
- 复杂向量数据库。MVP 优先采用简单检索；后续再评估 FAISS 或 Chroma。

### 5.4 不支持需求的降级策略

当用户提出暂不支持的需求时，系统需要明确说明限制，并提供当前可执行的替代方案。

示例：

```text
当前版本可以立即生成一次报告，但暂不支持在后台按周自动运行。
```

## 6. 核心架构

### 6.1 总体结构

```text
User Message
-> Orchestrator
-> Planner(mode=clarify | create_workflow | revise_workflow)
-> Workflow Validation
-> Executor
-> Step Registry
-> Tool Implementation
-> Execution Trace + Artifacts
```

### 6.2 单一 Orchestrator

系统只实现一个 Orchestrator 状态编排器。

- Clarification 不是独立 Agent，而是 Orchestrator 在信息不足时调用 Planner 的行为。
- Feedback Modifier 不是独立 Agent，而是 Orchestrator 收到修改意见后调用 Planner 的行为。
- 客服问答不是独立 Agent，而是文档问答能力的场景封装。

Planner 提供三个明确入口：

```text
planner.clarify(...)
planner.create_workflow(...)
planner.revise_workflow(...)
```

### 6.3 Workflow JSON

后台使用结构化 Workflow JSON 表达任务计划。Workflow 必须满足：

- 只能引用 Step Registry 中已注册的 `step_type`。
- 第一版只支持线性有序步骤。
- 每一步允许引用任意前序步骤输出。
- 输入引用使用结构化 `InputBinding`，不解析字符串模板表达式。
- Workflow 显式声明最终展示的 `result_bindings`。
- Workflow 创建后不原地修改；反馈修改生成 `version + 1` 的新版本。
- 所有模型生成内容必须经过严格校验后才能交给 Executor。

示例：

```json
{
  "id": "workflow_001",
  "version": 1,
  "goal": "生成文档摘要和 5 个要点",
  "source_policy": "uploaded_files_only",
  "workflow_inputs": [
    {
      "name": "source_files",
      "value_type": "files",
      "required": true
    }
  ],
  "steps": [
    {
      "id": "read_1",
      "step_type": "read_document",
      "inputs": [
        {
          "name": "files",
          "bindings": [
            {
              "source": "workflow_input",
              "input_name": "source_files"
            }
          ]
        }
      ],
      "params": {}
    },
    {
      "id": "generate_1",
      "step_type": "generate_text",
      "inputs": [
        {
          "name": "materials",
          "bindings": [
            {
              "source": "step_output",
              "step_id": "read_1",
              "output_name": "documents"
            }
          ]
        }
      ],
      "params": {
        "task": "summary",
        "bullet_count": 5
      }
    }
  ],
  "result_bindings": [
    {
      "step_id": "generate_1",
      "output_name": "text",
      "label": "整理结果"
    }
  ]
}
```

### 6.4 Step Registry

`core/step_registry.py` 负责声明系统允许规划和执行的步骤契约。每个注册项需要包含：

- `step_type`
- 输入端口及允许类型
- 输出端口及类型
- 参数 Pydantic Model
- 对应 handler 名称
- 是否需要联网

具体工具实现后续放在 `tools/` 目录。Planner 不能直接调用工具。

### 6.5 首批步骤白名单

```text
read_document       files -> documents
chunk_document      documents -> chunks
retrieve_chunks     chunks + query -> retrieved_chunks
read_table          file -> table
profile_table       table -> table_profile
filter_table        table -> table
aggregate_table     table -> table
sort_table          table -> table
render_chart        table -> chart
generate_text       materials[] -> text
answer_with_sources retrieved_chunks + question -> text + citations
```

P1 预留：

```text
web_search
merge_sources
```

### 6.6 文本生成复用

报告生成和资料总结共用 `generate_text` Step。不同任务通过受约束参数表达，例如：

```text
summary
report
business_insights
```

文档问答中的依据回答使用 `answer_with_sources`，以便强制输出依据片段。

### 6.7 声明式数据分析

LLM 只能生成声明式分析计划，后端将计划翻译为固定 `pandas` 操作。

允许的第一批聚合操作：

```text
count
sum
mean
min
max
```

筛选操作也必须来自白名单。禁止：

- 任意 Python 代码。
- 任意 pandas 表达式。
- 字符串拼接执行查询。
- `eval`、`exec` 或等价动态执行机制。

## 7. 核心数据模型

### 7.1 Workflow

描述任务目标、来源策略、输入、线性步骤、版本和最终输出绑定。

### 7.2 Step

描述单个可执行步骤：

- `id`
- `step_type`
- `inputs`
- `params`
- 面向用户展示的标题

### 7.3 InputBinding

描述步骤输入来源：

- Workflow 输入。
- 任意前序 Step 输出。

### 7.4 StepOutput

使用统一输出结构记录：

- 输出名称。
- 值类型。
- 持久化引用。
- 预览摘要。
- 产物 ID。

### 7.5 ExecutionContext

保存：

- 会话 ID。
- 运行 ID。
- Workflow 输入。
- 当前运行中的实际对象引用。

`DataFrame` 等实际运行对象不直接持久化为 Workflow JSON。持久化层只保存引用、摘要和产物路径。

### 7.6 WorkflowResult

保存：

- Workflow ID 和版本。
- 运行 ID。
- 整体状态。
- 每个 Step 的执行结果。
- 最终展示输出。
- 错误信息。

## 8. Orchestrator 状态机

### 8.1 状态

```text
COLLECTING_REQUIREMENTS
AWAITING_CONFIRMATION
RUNNING
COMPLETED
FAILED
REVISING
UNSUPPORTED
```

### 8.2 主要转换

```text
COLLECTING_REQUIREMENTS --needs_more_info--> COLLECTING_REQUIREMENTS
COLLECTING_REQUIREMENTS --workflow_ready--> AWAITING_CONFIRMATION
AWAITING_CONFIRMATION --user_confirmed--> RUNNING
RUNNING --execution_succeeded--> COMPLETED
RUNNING --execution_failed--> FAILED
COMPLETED --user_requested_change--> REVISING
FAILED --user_requested_change--> REVISING
REVISING --workflow_ready--> AWAITING_CONFIRMATION
FAILED --user_retry_requested--> RUNNING
```

`UNSUPPORTED` 不应成为无法恢复的终态。用户重新描述需求或接受替代方案后，可以回到需求收集状态。

## 9. Executor 校验与执行规则

### 9.1 执行前校验

Executor 在执行前必须完成以下检查：

1. Workflow 结构字段完整且符合 Pydantic Schema。
2. `step.id` 唯一。
3. 所有 `step_type` 均已注册。
4. 每个 Step 参数符合专属 Pydantic Model。
5. 未声明的参数字段直接拒绝，不静默忽略。
6. 所有必需输入端口均已绑定。
7. 不允许绑定未声明的输入端口。
8. Step 只能引用 Workflow 输入或前序 Step 输出。
9. 被引用输出真实存在。
10. 输入与输出的值类型兼容。
11. `result_bindings` 引用真实输出。
12. `uploaded_files_only` 策略下禁止联网步骤。
13. 上传文件真实存在且格式受支持。
14. Workflow 步骤数、文件数量和数据量不超过配置上限。

### 9.2 执行规则

- 第一版按顺序执行步骤。
- 任意一步失败后立即停止。
- 保留已完成步骤的结果和日志。
- 向用户展示可理解的错误信息。
- 用户可以修改需求，生成新版本后重新执行。
- MVP 默认重新执行完整 Workflow，不实现增量执行和缓存复用优化。

## 10. 推荐目录结构

```text
project-nlp/
├── app.py
├── config.py
├── core/
│   ├── orchestrator.py
│   ├── orchestrator_state.py
│   ├── planner.py
│   ├── executor.py
│   ├── workflow_schema.py
│   ├── step_registry.py
│   └── llm.py
├── tools/
│   ├── documents.py
│   ├── retrieval.py
│   ├── data_analysis.py
│   ├── text_generation.py
│   └── web_search.py
├── storage/
│   ├── sqlite_store.py
│   └── file_store.py
├── prompts/
│   ├── plan.md
│   ├── revise.md
│   └── answer.md
├── tests/
│   ├── test_executor.py
│   ├── test_tools.py
│   └── test_workflows.py
├── examples/
│   ├── sample.csv
│   └── sample.txt
├── .env.example
├── README.md
├── requirements.md
├── requirements.txt
└── nlp_agent.pdf
```

当前阶段只创建本文档，不创建上述业务代码或目录。

## 11. 验收场景

### 11.1 场景清单

| 优先级 | 场景 | 主要验证内容 |
| --- | --- | --- |
| P0 | 上传文档并生成总结 | 追问、确认、文件解析、文本生成、结果修改 |
| P0 | 只基于文件回答问题 | 文档切分、检索、依据片段、禁止联网 |
| P0 | 分析销售表格 | 声明式聚合、排序、图表、业务建议 |
| P0 | 基于 FAQ 模拟客服问答 | 复用文档问答能力，不增加独立 Agent |
| P0 | 用户要求每周生成报告 | 识别不支持能力，并提示只能立即执行一次 |

### 11.2 详细场景：上传文档并生成总结

#### 用户对话

```text
用户：帮我整理这份文件。
系统：你希望得到哪种结果？例如简短摘要、详细报告或要点列表。
用户：给我一份简短摘要和 5 个要点，只用上传的文件。
系统：展示人话版方案，并说明不会访问网络。
用户：确认执行。
系统：读取文件并生成摘要和要点，展示执行记录。
用户：还是太长了，摘要缩短到 100 字以内。
系统：创建新版本 Workflow，展示修订方案。
用户：确认执行。
系统：重新生成，并保留两次 Workflow 版本和运行记录。
```

#### 人话版方案示例

```text
我准备：
1. 读取你上传的文件。
2. 只使用文件中的内容生成简短摘要。
3. 提取 5 个关键要点。

本次任务不会访问网络。
```

#### Workflow 组合

```text
read_document -> generate_text
```

#### 验收标准

- 文件能够上传并被真实解析。
- 初始模糊需求触发必要追问。
- 用户确认前不执行 Workflow。
- 页面明确展示“不会访问网络”。
- 结果包含摘要和 5 个要点。
- 用户反馈后创建 `workflow_version = 2`。
- 第二次结果满足摘要不超过 100 字的要求。
- 两次 Workflow 版本和运行记录均可在执行详情中查看。

### 11.3 其他场景的最小验收方向

#### 只基于文件回答问题

- 组合：`read_document -> chunk_document -> retrieve_chunks -> answer_with_sources`
- 结果必须包含答案和依据片段。
- 来源策略为 `uploaded_files_only`。

#### 分析销售表格

- 组合：`read_table -> profile_table -> aggregate_table -> sort_table -> render_chart -> generate_text`
- 分析计划只能使用声明式参数。
- 结果包含表格、简单图表和业务建议。

#### 基于 FAQ 模拟客服问答

- 复用文档问答步骤。
- 在应用内提供模拟用户问题输入框。
- 回答附带 FAQ 或产品资料中的依据片段。

#### 用户要求每周生成报告

- 不生成虚假的定时执行 Workflow。
- 明确说明当前只能立即执行一次。
- 允许用户接受替代方案后继续生成一次性报告。

## 12. 开发顺序

### 阶段 1：固化契约

1. 完善 5 个验收场景。
2. 定义 `workflow_schema.py`。
3. 定义 `orchestrator_state.py`。
4. 定义 `step_registry.py`。
5. 实现 Executor 的 Workflow 校验逻辑。
6. 为 Schema、状态转换和校验逻辑编写单元测试。

### 阶段 2：完成首个纵向闭环

1. 实现文档上传。
2. 实现文档解析。
3. 实现 Planner 的追问、创建和修订行为。
4. 实现方案确认。
5. 实现 `read_document -> generate_text`。
6. 展示结果、执行详情、Workflow 版本和运行记录。

### 阶段 3：扩展 P0 能力

1. 实现文档切分、简单检索和依据回答。
2. 实现 FAQ 客服问答场景封装。
3. 实现 CSV/XLSX 声明式分析。
4. 实现简单图表和业务建议。
5. 完善错误处理和边界提示。

### 阶段 4：实现 P1 能力

1. 增加联网检索 Step。
2. 增加用户授权确认。
3. 展示联网数据来源。
4. 完善相关策略校验和测试。

## 13. 交付与验证要求

- 提供可以本地启动的 Web App。
- 提供简洁运行说明。
- 使用环境变量配置模型服务。
- 核心能力有可复现的验收场景。
- 保留开发过程、重要决策和测试结果。
- 初始化 Git 仓库后，将 `nlp_agent.pdf` 纳入版本管理，作为原始需求来源。

## 14. 待确认项

以下问题不阻塞 v0.1 文档生成，后续实现前逐步确认：

1. OpenAI-compatible LLM API 的默认服务地址、模型名称和环境变量命名。
2. 单个上传文件、总文件数和数据表行数上限。
3. 简单检索第一版采用 BM25、TF-IDF 还是其他本地实现。
4. 文本切分大小、重叠区间和检索返回片段数量。
5. 图表第一版支持的类型：建议先支持柱状图、折线图和饼图中的有限集合。
6. SQLite 表结构和本地产物目录命名。
7. P1 联网检索供应商及来源引用格式。
8. 是否需要在最终交付中额外提供 Codex Skill 或 Plugin 作为可选展示能力。

## 15. 决策日志

| 日期 | 决策 | 原因 |
| --- | --- | --- |
| 2026-06-02 | 产品采用本地启动的 Streamlit Web App | 面向非技术用户，Web 交互比 CLI 更适合文件上传、方案确认和结果展示 |
| 2026-06-02 | 使用云端 OpenAI-compatible LLM API，并保留轻量适配层 | 将精力投入产品闭环，同时保留替换模型服务的边界 |
| 2026-06-02 | 不构建多 Agent 平台 | MVP 更需要稳定、可演示的闭环，而不是复杂平台能力 |
| 2026-06-02 | 使用单一 Orchestrator 状态编排器 | Clarification 和 Feedback 本质上是不同状态下的规划行为 |
| 2026-06-02 | Workflow JSON 只能组合 Step Registry 中的有限步骤 | 避免模型虚构不可执行能力，便于校验和测试 |
| 2026-06-02 | 第一版只支持线性步骤，不实现 DAG | 已足以覆盖 P0 场景，并降低调度和错误传播复杂度 |
| 2026-06-02 | 步骤输入使用结构化 InputBinding | 便于静态校验，避免字符串表达式解析错误 |
| 2026-06-02 | Workflow 显式声明 result_bindings | 支持文本、图表和依据片段等多种最终产物 |
| 2026-06-02 | 参数校验使用严格模式，未知字段直接拒绝 | 防止模型生成的配置看似生效但实际被忽略 |
| 2026-06-02 | Executor 执行失败后立即停止 | 保持结果可信度，并降低下游错误处理复杂度 |
| 2026-06-02 | 数据分析只允许声明式计划，不执行模型生成 Python | 提高安全性、可审计性和结果稳定性 |
| 2026-06-02 | FAQ 客服问答复用文档问答能力 | 避免增加独立 Agent 和重复实现 |
| 2026-06-02 | 资料总结和报告生成共用 generate_text Step | 减少重复逻辑，通过受约束任务类型表达差异 |
| 2026-06-02 | 暂不实现后台定时任务，也不展示模拟定时入口 | 避免用户误解产品已具备自动运行能力 |
| 2026-06-02 | 可控联网检索放在 P1，默认关闭 | 优先确保文件总结、问答和表格分析稳定 |
| 2026-06-02 | 页面提供折叠执行详情 | 保持普通用户界面简洁，同时方便工程评审验证内部机制 |
| 2026-06-02 | 先细化 5 个验收场景，再实现核心契约 | 使用真实场景验证 Schema、状态机和步骤契约是否够用 |
| 2026-06-02 | 首个纵向闭环选择文档总结 | 依赖最少，但能够覆盖追问、确认、执行和反馈修改完整流程 |
| 2026-06-02 | `requirements.md` 作为单一需求基线 | 便于一周 MVP 持续维护，避免需求和技术约束分散 |

