# AI Coding Usage

This document records how Codex is used during implementation.

## 2026-06-02 - Stage 0 requirements baseline

- Used Codex to inspect the local repository, read `requirements.md`, confirm the MVP boundaries, and prepare the initial project baseline.
- Confirmed that the project keeps a single Orchestrator, a constrained Step Registry, linear workflows, strict validation, and offline-first defaults.
- Added the initial Python dependency list and repository ignore rules before implementation.

## 2026-06-02 - Stage 1 core contracts

- Used Codex to implement the initial Python package structure, strict Pydantic v2 workflow schemas, Orchestrator state transitions, Step Registry declarations, Executor validation, and focused unit tests.
- Kept business handlers out of the Registry and exposed a `handler_map` placeholder so real tools can be added incrementally from stage 2.
