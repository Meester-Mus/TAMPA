"""
Tests for compare_tampa module
"""

import pytest
from src.datanet.compare_tampa import (
    compare_tampa_results,
    validate_against_canon,
    ComparisonResult
)


def test_compare_single_execution():
    """Test comparison with single execution."""
    executions = [
        {"job_id": "1", "outputs": {"result": 42}}
    ]
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is True
    assert result.canonical_output == {"result": 42}
    assert len(result.discrepancies) == 0


def test_compare_identical_executions():
    """Test comparison with identical executions."""
    executions = [
        {"job_id": "1", "outputs": {"result": 42}},
        {"job_id": "2", "outputs": {"result": 42}},
        {"job_id": "3", "outputs": {"result": 42}}
    ]
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is True
    assert result.canonical_output == {"result": 42}
    assert len(result.discrepancies) == 0


def test_compare_different_order_same_data():
    """Test that different key order doesn't affect comparison."""
    executions = [
        {"job_id": "1", "outputs": {"a": 1, "b": 2}},
        {"job_id": "2", "outputs": {"b": 2, "a": 1}}
    ]
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is True
    assert len(result.discrepancies) == 0


def test_compare_different_executions():
    """Test comparison with different executions."""
    executions = [
        {"job_id": "1", "outputs": {"result": 42}},
        {"job_id": "2", "outputs": {"result": 43}},
    ]
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is False
    assert len(result.discrepancies) > 0


def test_compare_empty_list():
    """Test comparison with empty execution list."""
    executions = []
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is False
    assert result.canonical_output is None


def test_comparison_result_to_dict():
    """Test conversion of ComparisonResult to dict."""
    executions = [
        {"job_id": "1", "outputs": {"result": 42}}
    ]
    
    result = compare_tampa_results(executions)
    result_dict = result.to_dict()
    
    assert "consensus_reached" in result_dict
    assert "canonical_output" in result_dict
    assert "num_executions" in result_dict
    assert "num_discrepancies" in result_dict
    assert result_dict["num_executions"] == 1


def test_validate_against_canon_matching():
    """Test validation with matching canonical spec."""
    result = {
        "job_id": "1",
        "outputs": {"value": 100}
    }
    canon_spec = {
        "expected_output": {"value": 100}
    }
    
    is_valid, reason = validate_against_canon(result, canon_spec)
    
    assert is_valid is True
    assert "matches" in reason.lower()


def test_validate_against_canon_mismatch():
    """Test validation with non-matching canonical spec."""
    result = {
        "job_id": "1",
        "outputs": {"value": 100}
    }
    canon_spec = {
        "expected_output": {"value": 200}
    }
    
    is_valid, reason = validate_against_canon(result, canon_spec)
    
    assert is_valid is False
    assert "mismatch" in reason.lower()


def test_compare_complex_nested_outputs():
    """Test comparison with complex nested outputs."""
    executions = [
        {
            "job_id": "1",
            "outputs": {
                "data": {
                    "values": [1, 2, 3],
                    "metadata": {"count": 3}
                }
            }
        },
        {
            "job_id": "2",
            "outputs": {
                "data": {
                    "metadata": {"count": 3},
                    "values": [1, 2, 3]
                }
            }
        }
    ]
    
    result = compare_tampa_results(executions)
    
    assert result.consensus_reached is True


def test_compare_with_missing_outputs():
    """Test comparison when some executions have no outputs."""
    executions = [
        {"job_id": "1", "outputs": {"result": 42}},
        {"job_id": "2"}  # No outputs field
    ]
    
    result = compare_tampa_results(executions)
    
    # Should handle gracefully
    assert isinstance(result, ComparisonResult)
