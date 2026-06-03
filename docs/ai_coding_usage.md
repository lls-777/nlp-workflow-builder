# AI Coding Usage

This document records how Codex is used during implementation.

## 2026-06-02 - Stage 0 requirements baseline

- Used Codex to inspect the local repository, read `requirements.md`, confirm the MVP boundaries, and prepare the initial project baseline.
- Confirmed that the project keeps a single Orchestrator, a constrained Step Registry, linear workflows, strict validation, and offline-first defaults.
- Added the initial Python dependency list and repository ignore rules before implementation.

## 2026-06-02 - Stage 1 core contracts

- Used Codex to implement the initial Python package structure, strict Pydantic v2 workflow schemas, Orchestrator state transitions, Step Registry declarations, Executor validation, and focused unit tests.
- Kept business handlers out of the Registry and exposed a `handler_map` placeholder so real tools can be added incrementally from stage 2.

## 2026-06-02 - Stage 2 offline summary workflow

- Used Codex to add the deterministic mock LLM adapter, TXT and MD document readers, summary handler, lightweight runtime logging, executable demo workflow, and focused tests.
- Kept the stage scoped to `read_document -> generate_text`; PDF and DOCX return clear deferred-support messages, and no real LLM API, retrieval, table analysis, or UI code was added.
- Verification commands: `.venv/bin/python -m pytest` and `.venv/bin/python -m examples.run_demo_workflow`.
- Manual confirmation points: the demo validates before execution, both steps complete, a stable summary is printed, and `logs/app.log` contains identifiers and statuses without document contents.
- Verification result: the complete test suite passed, the demo completed successfully, and the runtime log content check passed.

## 2026-06-02 - Stage 3 acceptance scenarios

- Used Codex to document the five MVP acceptance scenarios and add statically validated Workflow JSON examples for summary, document question answering, declarative sales analysis, FAQ simulation, and the one-time report fallback.
- Reused only registered step types. The FAQ scenario shares the document question-answering workflow, the table example uses declarative parameters only, and the one-time report example contains no background repetition configuration.
- Verification commands: `.venv/bin/python -m pytest` and `.venv/bin/python -m examples.run_demo_workflow`.
- Manual confirmation points: all five examples load through the strict Pydantic schema, pass `validate_workflow`, and do not require new business handlers during stage 3.
- Verification result: the complete test suite passed with 43 tests, and the stage 2 offline summary demo completed successfully as a regression check.

## 2026-06-02 - Stage 4A document question answering

- Used Codex to add PDF and DOCX text extraction, stable document chunking, local character n-gram TF-IDF retrieval, evidence-based answering, safe citations, and an executable document question-answering demo.
- Added optional OpenAI-compatible chat completions support in `core/llm.py`. The default remains `LLM_MODE=mock`, so local demos and tests do not require an API key or network access.
- Added Python 3.9-compatible dependencies for PDF parsing, DOCX parsing, and TF-IDF retrieval.
- Verification commands: `.venv/bin/python -m pytest`, `.venv/bin/python -m examples.run_demo_workflow`, and `.venv/bin/python -m examples.run_document_qa_workflow`.
- Manual confirmation points: document QA and FAQ workflows both execute through the same registered steps, relevant questions return safe citations without absolute paths, unrelated questions refuse to answer with `citations=[]`, and runtime logs contain no document text or API key.
- Installed versions: `pypdf 6.12.2`, `python-docx 1.2.0`, and `scikit-learn 1.6.1`.
- Verification result: the complete suite passed with 62 tests, both executable demos completed successfully, bytecode compilation passed, and the runtime log safety scan passed.

## 2026-06-02 - Stage 4B declarative table analysis

- Used Codex to add CSV and XLSX table reading, table profiling, declarative filtering, declarative aggregation, stable sorting, chart specification generation, and an executable sales-analysis demo.
- Kept table operations constrained to explicit operator branches and registered Pydantic parameter models. No model-generated Python, dynamic expressions, table query strings, chart files, UI code, Planner code, or persistence code were added.
- Added Python 3.9-compatible dependencies for table processing and XLSX reading.
- Verification commands: `.venv/bin/python -m pytest`, `.venv/bin/python -m examples.run_demo_workflow`, `.venv/bin/python -m examples.run_document_qa_workflow`, and `.venv/bin/python -m examples.run_data_analysis_workflow`.
- Manual confirmation points: the sales workflow completes all seven registered steps, returns a ranked table and `chart_spec`, generates deterministic mock business insights, and runtime logs contain identifiers and statuses without table rows.
- Installed versions: `pandas 2.2.3` and `openpyxl 3.1.5`.
- Verification result: the complete suite passed with 95 tests, all three executable demos completed successfully, bytecode compilation passed, and the runtime log safety scan passed.

## 2026-06-02 - Stage 4.5 service layer and local persistence

- Used Codex to add the rule-based Planner, single Orchestrator service, UUID-based upload storage, prompt templates, and sqlite3 persistence for sessions, workflow versions, runs, and step runs.
- Kept the service layer narrow: Planner only clarifies, creates, and revises workflows; Orchestrator coordinates state transitions, Executor calls, and local records; FileStore accepts safe local uploads; SQLite stores JSON snapshots and summaries without an ORM.
- Added explicit state handling for a new document question as a new run of the current workflow version. Workflow feedback creates `version + 1` and reruns the complete workflow after confirmation.
- Verification commands: `.venv/bin/python -m pytest`, `.venv/bin/python -m examples.run_demo_workflow`, `.venv/bin/python -m examples.run_document_qa_workflow`, and `.venv/bin/python -m examples.run_data_analysis_workflow`.
- Manual confirmation points: sqlite3 contains only the four scoped tables, uploaded files receive UUID names, path traversal and symlink escapes are rejected, weekly requests require one-time fallback acceptance, workflow feedback creates `version + 1`, and a new document question reuses the current workflow version while creating a new run.
- Verification result: the complete suite passed with 115 tests, all three executable demos completed successfully, project-source bytecode compilation passed under Python 3.9, and `git diff --check` passed.

## 2026-06-02 - Stage 5 Streamlit MVP app

- Used Codex to add a Streamlit web app that accepts natural-language requests and uploaded files, presents plain-language plans, asks for confirmation, executes through the Orchestrator service, and renders text, tables, citations, and chart specifications.
- Kept the UI boundary narrow: `app.py` calls Orchestrator methods only and does not assemble workflows or call business tools directly. Technical implementation concepts remain hidden from ordinary page content.
- Added structured final-result values for rendering, a clarification prompt, localized result labels, full rerun after feedback, new-request handling after completion, and upload limits aligned with backend validation: 20MB per file, 10 files maximum, and 50MB total.
- Added an execution precheck for declarative table analysis: requests without a CSV or XLSX file now stop before creating a run and return a user-readable prompt to upload a table file.
- Verification commands: `.venv/bin/python -m pytest`, `.venv/bin/python -m examples.run_demo_workflow`, `.venv/bin/python -m examples.run_document_qa_workflow`, `.venv/bin/python -m examples.run_data_analysis_workflow`, and `PYTHONPYCACHEPREFIX=.cache/pycache .venv/bin/python -m compileall .`.
- Manual confirmation points: the local app starts only on `localhost`, the initial page does not show an error state, completed sessions can accept a new requirement, TXT/MD-only table-analysis requests receive a CSV/XLSX prompt, and sales analysis with `sample_sales.csv` renders a ranked table, chart, and business insights.
- Installed version: `streamlit 1.48.0`.
- Verification result: the complete suite passed with 129 tests, all three executable demos completed successfully, bytecode compilation passed under Python 3.9, and `git diff --check` passed.

## 2026-06-03 - Stage 6 delivery documentation

- Used Codex to add the running guide, environment example, decision log, and final acceptance status notes.
- Kept the stage scoped to documentation and delivery checks only. No business tools, core architecture changes, remote configuration, or push operations were added.
- Verification commands: `.venv/bin/python -m pytest`, `.venv/bin/python -m examples.run_demo_workflow`, `.venv/bin/python -m examples.run_document_qa_workflow`, `.venv/bin/python -m examples.run_data_analysis_workflow`, `PYTHONPYCACHEPREFIX=.cache/pycache .venv/bin/python -m compileall .`, `git diff --check`, local Git identity checks, `git status --short`, and `git log --oneline`.
- Verification result: the complete suite passed with 129 tests, all three executable demos completed successfully, bytecode compilation passed under Python 3.9, `git diff --check` passed, and the local Git identity was confirmed as `lls-777 <279362506+lls-777@users.noreply.github.com>`.
