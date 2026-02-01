import uuid
from pathlib import Path
import json

ROOT = Path('data')
ROOT.mkdir(exist_ok=True)

def create_job(query, snapshot_html):
    job_id = str(uuid.uuid4())
    p = ROOT / job_id
    p.mkdir()
    (p / 'meta.json').write_text(json.dumps({'query': query}))
    (p / 'snapshot.html').write_text(snapshot_html)
    return job_id

def load_job(job_id):
    p = ROOT / job_id
    if not p.exists():
        return None
    snap = (p / 'snapshot.html').read_text(encoding='utf-8')
    meta = json.loads((p / 'meta.json').read_text(encoding='utf-8'))
    return {'query': meta.get('query'), 'snapshot_html': snap}

def save_agent_output(job_id, name, obj):
    p = ROOT / job_id
    p.mkdir(exist_ok=True)
    (p / f"{name}.json").write_text(json.dumps(obj))
