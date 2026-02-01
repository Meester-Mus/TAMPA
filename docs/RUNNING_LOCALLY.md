# Running TAMPA Datanet Agent Locally

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for MinIO)
- GPG (optional, for signing)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Services with Docker Compose

```bash
cd compose
docker-compose up -d
```

This will start:
- MinIO on ports 9000 (API) and 9001 (Console)
- TAMPA Datanet Agent API on port 8000

### 3. Verify Services

```bash
# Check MinIO
curl http://localhost:9000/minio/health/live

# Check API
curl http://localhost:8000/
```

## Running Without Docker

### Start API Server

```bash
# From repository root
python -m uvicorn src.datanet.main:app --reload --host 0.0.0.0 --port 8000
```

### Use Local Storage

The application defaults to local filesystem storage in `./data/` directory.

## Using the API

### Submit a Job

```bash
curl -X POST http://localhost:8000/submit-agent \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-001",
    "agent_code": "# Manual ChatGPT paste required",
    "inputs": {"value": 42}
  }'
```

### List Jobs

```bash
curl http://localhost:8000/jobs
```

### Compare Results

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["test-001", "test-002"]
  }'
```

### Propose Canonical Change

```bash
curl -X POST http://localhost:8000/propose-to-canon \
  -H "Content-Type: application/json" \
  -d '{
    "current_canon_id": "v1",
    "proposed_change": {"new_field": "value"},
    "rationale": "Adding new field for clarity",
    "author": "developer@example.com"
  }'
```

## Using the Reviewer CLI

### List Pending Reviews

```bash
python src/datanet/reviewer_cli.py list-pending
```

### Show Review Details

```bash
python src/datanet/reviewer_cli.py show <record_id>
```

### Approve Review

```bash
python src/datanet/reviewer_cli.py approve <record_id> --reviewer "Alice"
```

### Reject Review

```bash
python src/datanet/reviewer_cli.py reject <record_id> \
  --reviewer "Bob" \
  --reason "Insufficient rationale"
```

### View Statistics

```bash
python src/datanet/reviewer_cli.py stats
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/datanet --cov-report=term-missing

# Specific test file
pytest tests/test_canonicalize.py -v
```

## Development

### Hot Reload

The Docker Compose setup mounts source directories for hot reload:

```bash
cd compose
docker-compose up
# Edit files in src/ - changes will reload automatically
```

### Logs

```bash
# API logs
docker-compose logs -f app

# MinIO logs
docker-compose logs -f minio
```

## Stopping Services

```bash
cd compose
docker-compose down

# Remove volumes
docker-compose down -v
```

## Environment Variables

- `MINIO_ENDPOINT` - MinIO endpoint (default: `minio:9000`)
- `MINIO_ACCESS_KEY` - MinIO access key (default: `minioadmin`)
- `MINIO_SECRET_KEY` - MinIO secret key (default: `minioadmin`)
- `MINIO_SECURE` - Use HTTPS for MinIO (default: `false`)

## Troubleshooting

### Port Already in Use

If ports 8000, 9000, or 9001 are in use:

```bash
# Check what's using the port
lsof -i :8000
lsof -i :9000
lsof -i :9001

# Kill the process or change ports in docker-compose.yml
```

### Permission Errors

Ensure the `data/` directory is writable:

```bash
mkdir -p data
chmod 755 data
```

### Docker Issues

```bash
# Rebuild containers
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up --build
```

## Next Steps

- See [SIGNING_HOWTO.md](SIGNING_HOWTO.md) for GPG signature setup
- Check [EXAMPLES/](EXAMPLES/) for sample job specifications
- Review [docs/README.md](README.md) for architecture details
