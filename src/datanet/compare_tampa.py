"""
TAMPA Output Comparator

Compares multiple TAMPA execution results to detect discrepancies
and validate consensus.
"""

from typing import List, Dict, Any, Tuple
import json
from .canonicalize_v1 import canonicalize_json, compute_canonical_hash


class ComparisonResult:
    """Result of comparing multiple TAMPA executions."""
    
    def __init__(self, executions: List[Dict[str, Any]]):
        self.executions = executions
        self.consensus_reached = False
        self.canonical_output = None
        self.discrepancies = []
        self._compare()
    
    def _compare(self):
        """Perform comparison of executions."""
        if not self.executions:
            return
        
        if len(self.executions) == 1:
            self.consensus_reached = True
            self.canonical_output = self.executions[0].get("outputs", {})
            return
        
        # Compare outputs using canonical hashes
        hashes = []
        for i, execution in enumerate(self.executions):
            output = execution.get("outputs", {})
            try:
                hash_val = compute_canonical_hash(output)
                hashes.append((i, hash_val, output))
            except Exception as e:
                self.discrepancies.append({
                    "execution_index": i,
                    "error": f"Failed to canonicalize: {str(e)}"
                })
        
        # Check for consensus
        if hashes:
            unique_hashes = set(h[1] for h in hashes)
            if len(unique_hashes) == 1:
                self.consensus_reached = True
                self.canonical_output = hashes[0][2]
            else:
                # Record discrepancies
                for i, hash_val, output in hashes:
                    self.discrepancies.append({
                        "execution_index": i,
                        "canonical_hash": hash_val,
                        "output": output
                    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert comparison result to dictionary."""
        return {
            "consensus_reached": self.consensus_reached,
            "canonical_output": self.canonical_output,
            "num_executions": len(self.executions),
            "num_discrepancies": len(self.discrepancies),
            "discrepancies": self.discrepancies
        }


def compare_tampa_results(results: List[Dict[str, Any]]) -> ComparisonResult:
    """
    Compare multiple TAMPA execution results.
    
    Args:
        results: List of execution results to compare
        
    Returns:
        ComparisonResult object
    """
    return ComparisonResult(results)


def validate_against_canon(result: Dict[str, Any], canon_spec: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate execution result against canonical specification.
    
    Args:
        result: Execution result to validate
        canon_spec: Canonical specification to validate against
        
    Returns:
        Tuple of (is_valid, reason)
    """
    try:
        result_hash = compute_canonical_hash(result.get("outputs", {}))
        canon_hash = compute_canonical_hash(canon_spec.get("expected_output", {}))
        
        if result_hash == canon_hash:
            return True, "Output matches canonical specification"
        else:
            return False, f"Hash mismatch: {result_hash} != {canon_hash}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"
