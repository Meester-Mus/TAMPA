# Datanet scaffold

This is a small scaffold for the Datanet PoC. It provides a minimal FastAPI app, simple file-based storage, a placeholder canonicalizer and a lightweight validator. Use this as a starting point for iterative development.

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.datanet.api:app --reload
```

Run tests:

```bash
pytest -q
```
