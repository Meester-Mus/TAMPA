"""
FastAPI Application - API Endpoints

Provides REST API for job submission, comparison, canonical proposals, and reviews.
"""

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from .tamparunner import TAMPARunner
from .compare_tampa import compare_tampa_results
from .decision_composer import DecisionComposer
from .storage import get_storage
from .canonicalize_v1 import canonicalize_json, compute_canonical_hash

logger = logging.getLogger(__name__)

# Initialize components
storage = get_storage(storage_type="local", base_path="./data")
decision_composer = DecisionComposer()


# Pydantic models
class JobSubmission(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    agent_code: str = Field(..., description="Agent code or placeholder")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Job inputs")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ComparisonRequest(BaseModel):
    job_ids: List[str] = Field(..., description="List of job IDs to compare")


class CanonProposal(BaseModel):
    current_canon_id: str = Field(..., description="Current canonical spec ID")
    proposed_change: Dict[str, Any] = Field(..., description="Proposed changes")
    rationale: str = Field(..., description="Justification for change")
    author: str = Field(..., description="Proposal author")


class ReviewAction(BaseModel):
    record_id: str = Field(..., description="Decision record ID")
    action: str = Field(..., description="Action: 'approve' or 'reject'")
    reviewer: str = Field(..., description="Reviewer name")
    reason: Optional[str] = Field(None, description="Reason for rejection")


# API Router
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="TAMPA Datanet Agent API",
        description="PoC API for Datanet Agent with TAMPA integration",
        version="0.1.0"
    )
    
    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "name": "TAMPA Datanet Agent",
            "version": "0.1.0",
            "status": "operational",
            "endpoints": [
                "/jobs",
                "/jobs/{job_id}",
                "/submit-agent",
                "/compare",
                "/propose-to-canon",
                "/reviews/pending",
                "/reviews/action"
            ]
        }
    
    @app.get("/jobs")
    async def list_jobs():
        """List all stored jobs."""
        try:
            job_keys = storage.list_keys(prefix="job_")
            jobs = []
            for key in job_keys:
                job_data = storage.retrieve(key)
                if job_data:
                    jobs.append({
                        "job_id": job_data.get("job_id"),
                        "status": job_data.get("status"),
                        "timestamp": job_data.get("timestamp")
                    })
            return {"jobs": jobs, "count": len(jobs)}
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/jobs/{job_id}")
    async def get_job(job_id: str):
        """Get job details by ID."""
        try:
            job_data = storage.retrieve(f"job_{job_id}")
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
            return job_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/submit-agent")
    async def submit_agent(submission: JobSubmission):
        """
        Submit agent job for execution.
        
        NOTE: In PoC, this simulates execution. Production would use actual TAMPA runner.
        """
        try:
            runner = TAMPARunner()
            
            job_spec = {
                "job_id": submission.job_id,
                "agent_code": submission.agent_code,
                "inputs": submission.inputs,
                "metadata": submission.metadata
            }
            
            result = runner.run_job(job_spec)
            result["status"] = "completed"
            result["job_id"] = submission.job_id
            
            # Store result
            storage.store(f"job_{submission.job_id}", result)
            
            runner.cleanup()
            
            return {
                "message": "Job submitted successfully",
                "job_id": submission.job_id,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Failed to submit agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/compare")
    async def compare_jobs(request: ComparisonRequest):
        """Compare multiple job results."""
        try:
            results = []
            for job_id in request.job_ids:
                job_data = storage.retrieve(f"job_{job_id}")
                if job_data:
                    results.append(job_data)
                else:
                    logger.warning(f"Job {job_id} not found")
            
            if not results:
                raise HTTPException(status_code=404, detail="No jobs found for comparison")
            
            comparison = compare_tampa_results(results)
            
            return {
                "comparison": comparison.to_dict(),
                "num_jobs": len(results)
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to compare jobs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/propose-to-canon")
    async def propose_canon_change(proposal: CanonProposal):
        """Propose a change to the canonical specification."""
        try:
            # Load current canon
            current_canon = storage.retrieve(f"canon_{proposal.current_canon_id}")
            if not current_canon:
                raise HTTPException(status_code=404, detail="Current canon not found")
            
            # Compose decision record
            record = decision_composer.compose_canon_proposal(
                current_canon=current_canon,
                proposed_change=proposal.proposed_change,
                rationale=proposal.rationale,
                author=proposal.author
            )
            
            # Store proposal
            storage.store(f"proposal_{record.record_id}", record.to_dict())
            
            return {
                "message": "Proposal created",
                "record_id": record.record_id,
                "status": "pending_review",
                "record": record.to_dict()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create proposal: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/reviews/pending")
    async def get_pending_reviews():
        """Get all pending review records."""
        try:
            pending = decision_composer.get_pending_reviews()
            return {
                "pending_reviews": pending,
                "count": len(pending)
            }
        except Exception as e:
            logger.error(f"Failed to get pending reviews: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/reviews/action")
    async def review_action(action: ReviewAction):
        """Approve or reject a review."""
        try:
            if action.action == "approve":
                success = decision_composer.approve_review(
                    record_id=action.record_id,
                    reviewer=action.reviewer
                )
                message = "Review approved" if success else "Failed to approve"
            elif action.action == "reject":
                if not action.reason:
                    raise HTTPException(status_code=400, detail="Rejection reason required")
                success = decision_composer.reject_review(
                    record_id=action.record_id,
                    reviewer=action.reviewer,
                    reason=action.reason
                )
                message = "Review rejected" if success else "Failed to reject"
            else:
                raise HTTPException(status_code=400, detail="Invalid action")
            
            if not success:
                raise HTTPException(status_code=404, detail="Record not found")
            
            return {
                "message": message,
                "record_id": action.record_id,
                "action": action.action
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to process review action: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


# Create app instance
app = create_app()
