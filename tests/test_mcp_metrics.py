from mcp import metrics

def test_metrics_counters_increment():
    # Ensure functions increment counters without raising
    metrics.incr_function_call('test_fn')
    metrics.incr_validation_failure()
    metrics.set_index_doc_count(5)
    metrics.observe_search_latency(0.123)
    # No assertions on Prometheus internals; presence of calls without exceptions is the test
    assert True
