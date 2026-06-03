# MVP Acceptance Scenarios

This document defines the five P0 acceptance scenarios used to verify the workflow contracts and the current MVP delivery status.

## Current Implementation Status

| Scenario | Status |
| --- | --- |
| Uploaded document summary | Executable |
| Document question answering | Executable |
| Sales table analysis | Executable |
| FAQ customer question simulation | Executable |
| Weekly report request | Downgraded to one immediate report |

## 1. Uploaded Document Summary

### User input

The user uploads one or more files and says: "Please organize these files."

### Clarifying questions

- Do you want a concise summary, a detailed report, or a list of key points?
- How many key points should be included?
- Should the result use only the uploaded files?

### Plain-language plan

1. Read the uploaded files.
2. Use only those files to prepare a concise summary.
3. Extract five key points.
4. Do not access the network.

### Workflow JSON

The executable contract is stored in [`examples/workflows/summary.json`](../examples/workflows/summary.json).

```text
read_document -> generate_text(task=summary, bullet_count=5, max_length=100)
```

### Expected result

A summary no longer than 100 characters and five key points are displayed.

### Feedback handling

When the user asks for a shorter summary, a table format, or additional suggestions, create `version + 1`, show the revised plan, request confirmation, and rerun the complete workflow.

### Acceptance criteria

- The system asks for missing output details.
- The system clearly states that it will not access the network.
- Execution starts only after confirmation.
- A revision creates a new workflow version and preserves prior runs.

### Current implementation status

Executable. The app and demo can run `read_document -> generate_text` for uploaded documents.

## 2. Uploaded Document Question Answering

### User input

The user uploads a contract and asks: "What are the refund conditions? Use only this file."

### Clarifying questions

- If multiple files were uploaded, which files should be used?
- If the question is broad, which clause or business case should the answer focus on?

### Plain-language plan

1. Read the uploaded files.
2. Split the files into searchable excerpts.
3. Find excerpts relevant to the question.
4. Answer only from those excerpts and display the supporting evidence.
5. Do not access the network.

### Workflow JSON

The contract is stored in [`examples/workflows/document_qa.json`](../examples/workflows/document_qa.json).

```text
read_document -> chunk_document -> retrieve_chunks -> answer_with_sources
```

### Expected result

The answer is displayed together with supporting excerpts. If the evidence is insufficient, the answer step must refuse to speculate.

### Feedback handling

A new question reuses the same workflow version as a new run. Changes to the source range, answer style, or processing plan create `version + 1` and rerun the complete workflow.

### Acceptance criteria

- The workflow uses `uploaded_files_only`.
- The answer includes supporting excerpts.
- The workflow contains no network step.
- Insufficient evidence produces a clear refusal instead of an invented answer.

### Current implementation status

Executable. The workflow reads documents, chunks them, retrieves relevant excerpts, answers with citations, and refuses when evidence is insufficient.

## 3. Sales Table Analysis

### User input

The user uploads a CSV or XLSX file and says: "Analyze completed sales by region and give me recommendations."

### Clarifying questions

- Which metric should be calculated?
- Which grouping field should be used?
- Should any rows be filtered out?
- Which chart type should be displayed?

### Plain-language plan

1. Read the uploaded sales table and inspect its fields.
2. Keep completed sales records.
3. Calculate total sales by region and rank the regions.
4. Prepare a bar-chart specification.
5. Generate business insights from the resulting table.

### Workflow JSON

The contract is stored in [`examples/workflows/data_analysis.json`](../examples/workflows/data_analysis.json).

```text
read_table -> profile_table -> filter_table -> aggregate_table
-> sort_table -> render_chart -> generate_text(task=business_insights)
```

### Expected result

The system returns a ranked table, a chart specification, and business insights.

### Feedback handling

When the user changes the metric, grouping, filter, ranking, or chart type, create `version + 1`, request confirmation, and rerun the complete workflow.

### Acceptance criteria

- Analysis parameters are declarative and limited to registered operations.
- The workflow contains no generated code or dynamic expression field.
- The chart step returns a specification for later UI rendering.

### Current implementation status

Executable. CSV/XLSX input runs through declarative table reading, profiling, filtering, aggregation, sorting, chart spec generation, and business insight generation.

## 4. FAQ Customer Question Simulation

### User input

The user uploads FAQ or product documents and asks: "Can a member request a refund?"

### Clarifying questions

- Which FAQ or product files should be used?
- If the question is broad, which product or membership type should the answer focus on?

### Plain-language plan

1. Read the uploaded FAQ files.
2. Split them into searchable excerpts.
3. Find the excerpts relevant to the customer question.
4. Answer from the FAQ excerpts and display the evidence.

### Workflow JSON

The contract is stored in [`examples/workflows/faq_customer_service.json`](../examples/workflows/faq_customer_service.json).

```text
read_document -> chunk_document -> retrieve_chunks -> answer_with_sources
```

### Expected result

The simulated answer is displayed with FAQ excerpts. It reuses document question answering and does not introduce a separate customer-service execution component.

### Feedback handling

A new customer question starts another run of the same workflow. Changes to the source files or response requirements create `version + 1` and rerun the complete workflow.

### Acceptance criteria

- The FAQ scenario reuses the document question-answering steps exactly.
- The workflow contains no dedicated customer-service agent or tool.
- The answer includes supporting FAQ excerpts.

### Current implementation status

Executable. FAQ customer questions reuse the same document QA path and do not introduce a separate customer-service Agent or tool.

## 5. Weekly Report Request Downgraded to One Immediate Run

### User input

The user asks: "Generate a sales report for me every Monday."

### Clarifying questions

- The current MVP cannot run jobs in the background. Would you like to generate one report immediately instead?
- Which uploaded files should be used for the immediate report?

### Plain-language plan

1. Explain that the current MVP can run the report once immediately but cannot repeat it in the background.
2. Ask the user to confirm the immediate alternative.
3. Read the uploaded files.
4. Generate one report immediately.

### Workflow JSON

The accepted fallback contract is stored in [`examples/workflows/one_time_report.json`](../examples/workflows/one_time_report.json).

```text
read_document -> generate_text(task=report)
```

### Expected result

The system clearly explains the limitation. After the user accepts the fallback, it generates one report immediately and does not claim that any background repetition has been configured.

### Feedback handling

If the user accepts the immediate alternative, return to requirements collection and create the one-time workflow. If the user still requires background repetition, keep the request unsupported and explain the current boundary.

### Acceptance criteria

- No background repetition step or configuration is created.
- The user receives an explicit boundary explanation and an executable alternative.
- The resulting workflow performs one immediate run only.

### Current implementation status

Downgraded to one immediate report. Background repetition remains explicitly out of scope.
