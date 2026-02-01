"""
Decision Record Composer

Composes decision records for canonical changes and proposals.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from .canonicalize_v1 import canonicalize_json, compute_canonical_hash


class DecisionRecord:
    """Represents a decision record for canonical changes."""
    
    def __init__(
        self,
        decision_type: str,
        proposal: Dict[str, Any],
        rationale: str,
        author: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize decision record.
        
        Args:
            decision_type: Type of decision (e.g., 'canon_update', 'acceptance')
            proposal: The proposed change
            rationale: Explanation for the decision
            author: Decision author/authority
            metadata: Additional metadata
        """
        self.decision_type = decision_type
        self.proposal = proposal
        self.rationale = rationale
        self.author = author
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        self.record_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique record ID."""
        content = {
            "type": self.decision_type,
            "proposal": self.proposal,
            "timestamp": self.timestamp,
            "author": self.author
        }
        return compute_canonical_hash(content)[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "record_id": self.record_id,
            "decision_type": self.decision_type,
            "timestamp": self.timestamp,
            "author": self.author,
            "proposal": self.proposal,
            "rationale": self.rationale,
            "metadata": self.metadata
        }
    
    def to_canonical_json(self) -> str:
        """Convert record to canonical JSON."""
        return canonicalize_json(self.to_dict())
    
    def prepare_for_signing(self) -> str:
        """
        Prepare record for signing.
        
        Returns:
            Canonical representation ready for GPG signing
        """
        return self.to_canonical_json()


class DecisionComposer:
    """Composes and manages decision records."""
    
    def __init__(self, authority_config: Optional[Dict[str, Any]] = None):
        """
        Initialize decision composer.
        
        Args:
            authority_config: Configuration for decision authority
        """
        self.authority_config = authority_config or {}
        self.pending_reviews: List[DecisionRecord] = []
    
    def compose_canon_proposal(
        self,
        current_canon: Dict[str, Any],
        proposed_change: Dict[str, Any],
        rationale: str,
        author: str
    ) -> DecisionRecord:
        """
        Compose a proposal to update the canonical specification.
        
        Args:
            current_canon: Current canonical spec
            proposed_change: Proposed changes
            rationale: Justification for change
            author: Proposal author
            
        Returns:
            DecisionRecord for the proposal
        """
        proposal = {
            "current_canon_hash": compute_canonical_hash(current_canon),
            "proposed_change": proposed_change,
            "change_type": "canon_update"
        }
        
        record = DecisionRecord(
            decision_type="canon_proposal",
            proposal=proposal,
            rationale=rationale,
            author=author,
            metadata={"status": "pending_review"}
        )
        
        self.pending_reviews.append(record)
        return record
    
    def compose_acceptance_decision(
        self,
        job_result: Dict[str, Any],
        policy: Dict[str, Any],
        author: str
    ) -> DecisionRecord:
        """
        Compose an acceptance decision for a job result.
        
        Args:
            job_result: Job execution result
            policy: Acceptance policy to apply
            author: Decision author
            
        Returns:
            DecisionRecord for acceptance
        """
        proposal = {
            "job_id": job_result.get("job_id"),
            "result_hash": compute_canonical_hash(job_result),
            "acceptance_status": "accepted",  # Could be accepted/rejected
            "policy_version": policy.get("version", "v1")
        }
        
        return DecisionRecord(
            decision_type="acceptance",
            proposal=proposal,
            rationale="Result meets acceptance criteria",
            author=author,
            metadata={"policy": policy}
        )
    
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get all pending review records."""
        return [r.to_dict() for r in self.pending_reviews if r.metadata.get("status") == "pending_review"]
    
    def approve_review(self, record_id: str, reviewer: str) -> bool:
        """
        Approve a pending review.
        
        Args:
            record_id: ID of record to approve
            reviewer: Reviewer name
            
        Returns:
            True if approved successfully
        """
        for record in self.pending_reviews:
            if record.record_id == record_id:
                record.metadata["status"] = "approved"
                record.metadata["reviewer"] = reviewer
                record.metadata["review_timestamp"] = datetime.utcnow().isoformat() + 'Z'
                return True
        return False
    
    def reject_review(self, record_id: str, reviewer: str, reason: str) -> bool:
        """
        Reject a pending review.
        
        Args:
            record_id: ID of record to reject
            reviewer: Reviewer name
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        for record in self.pending_reviews:
            if record.record_id == record_id:
                record.metadata["status"] = "rejected"
                record.metadata["reviewer"] = reviewer
                record.metadata["rejection_reason"] = reason
                record.metadata["review_timestamp"] = datetime.utcnow().isoformat() + 'Z'
                return True
        return False
