# Simple metrics module stub for MCP functions
# These can be replaced with actual metrics collection in production

def incr_function_call(function_name: str) -> None:
    """Increment function call counter."""
    pass

def incr_validation_failure() -> None:
    """Increment validation failure counter."""
    pass

def observe_search_latency(latency: float) -> None:
    """Record search latency."""
    pass

def set_index_doc_count(count: int) -> None:
    """Set the document count gauge."""
    pass
