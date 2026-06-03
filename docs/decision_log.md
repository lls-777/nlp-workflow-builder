# Decision Log

## Single Orchestrator

The MVP uses one Orchestrator to coordinate state transitions, planning, execution, and persistence. This keeps the product flow understandable and avoids introducing a complex multi-agent platform before the core workflow contract is stable.

## Limited Step Registry

Workflow steps must come from a finite Step Registry. The Executor rejects unknown, disabled, or policy-incompatible steps before execution. This keeps generated workflows constrained and testable.

## Linear Workflow

The first version supports only linear step execution. DAG execution, partial reruns, cache reuse, and background scheduling are intentionally out of scope for the MVP.

## Declarative Table Analysis

Table analysis is expressed through declarative parameters such as filters, aggregations, sort fields, and chart specs. The system does not execute LLM-generated Python or dynamic expressions.

## Offline By Default

The default LLM mode is `mock`, and document QA uses local parsing, chunking, and TF-IDF retrieval. The application can be validated without API keys or network access.

## P1 Network Retrieval Reserved

Network retrieval is reserved for future work. A disabled network step can exist in the registry, but offline source policies reject it even if a future version enables the handler.

## Scheduled Requests Downgrade

Recurring requests such as weekly reports are downgraded to one immediate run. The MVP does not create schedule, cron, timer, recurrence, or background job configuration.

## Feedback Reruns

Feedback that changes the processing plan creates `version + 1` and reruns the complete workflow. Incremental execution and cache reuse are not implemented in the first version.
