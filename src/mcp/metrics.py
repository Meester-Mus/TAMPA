from prometheus_client import Counter, Histogram, Gauge
from typing import Optional

# Counters
FUNCTION_CALL_TOTAL = Counter(
    'mcp_function_calls_total',
    'Total number of model-invoked function calls',
    ['function_name']
)

MCP_VALIDATION_FAILURES = Counter(
    'mcp_validation_failures_total',
    'Number of MCP payload validation failures'
)

# Histograms
SEARCH_LATENCY_SECONDS = Histogram(
    'mcp_search_latency_seconds',
    'Latency of search_documents (seconds)'
)

# Gauges
ACTIVE_INDEX_DOCS = Gauge(
    'mcp_index_document_count',
    'Number of documents currently indexed'
)


def incr_function_call(name: str) -> None:
    try:
        FUNCTION_CALL_TOTAL.labels(function_name=name).inc()
    except Exception:
        pass


def observe_search_latency(elapsed_seconds: float) -> None:
    try:
        SEARCH_LATENCY_SECONDS.observe(elapsed_seconds)
    except Exception:
        pass


def set_index_doc_count(n: int) -> None:
    try:
        ACTIVE_INDEX_DOCS.set(n)
    except Exception:
        pass


def incr_validation_failure() -> None:
    try:
        MCP_VALIDATION_FAILURES.inc()
    except Exception:
        pass
