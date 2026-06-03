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
