from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from . import storage, canonicalize_v1, chatgpt_agent, validate_tampa

app = FastAPI(title="Datanet PoC")

class JobCreate(BaseModel):
    query: str
    snapshot_html: str

@app.post('/jobs')
def create_job(payload: JobCreate):
    job_id = storage.create_job(payload.query, payload.snapshot_html)
    return {"jobId": job_id}

@app.post('/jobs/{jobId}/run-remote')
def run_remote(jobId: str):
    job = storage.load_job(jobId)
    if job is None:
        raise HTTPException(status_code=404, detail='job not found')
    canonical = canonicalize_v1.canonicalize_html(job['snapshot_html'])
    # call chatgpt agent stub
    out = chatgpt_agent.run_chatgpt_tampa(canonical['canonical_text'], canonical['canonical_sample'], canonical['drhash'])
    # attempt to validate
    ok, reason = validate_tampa.validate_tampa_output(out, canonical['canonical_text'])
    if not ok:
        storage.save_agent_output(jobId, 'tampa_chatgpt_invalid', {'reason': reason, 'output': out})
        return {"saved_invalid": True, "reason": reason}
    storage.save_agent_output(jobId, 'tampa_chatgpt', out)
    return {"saved": True}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
