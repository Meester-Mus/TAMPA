# TAMPA Datanet Agent - Documentation

## Overview

The TAMPA Datanet Agent is a proof-of-concept implementation that demonstrates:

- **Canonicalization**: DOS-MGC1-v1 (Diets-ordered serialization) for deterministic data representation
- **TAMPA Runner**: Local isolated execution environment for agent code
- **Comparator**: Consensus detection across multiple executions
- **Decision Composer**: Structured decision records for canonical changes
- **Reviewer CLI**: Command-line tool for approving/rejecting proposals
- **Signing**: GPG and JWS helpers for cryptographic signatures
- **Storage**: Flexible storage layer (local filesystem or MinIO S3)
- **API**: FastAPI REST endpoints for job submission and review workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  /jobs, /submit-agent, /compare, /propose-to-canon, /reviews│
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐    ┌──────▼──────┐    ┌─────▼──────┐
   │  TAMPA   │    │  Comparator │    │  Decision  │
   │  Runner  │    │             │    │  Composer  │
   └──────────┘    └─────────────┘    └────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Storage   │
                    │ (Local/MinIO)│
                    └─────────────┘
```

## Key Components

### Canonicalize v1 (`canonicalize_v1.py`)
- Implements DOS-MGC1-v1 deterministic JSON serialization
- Alphabetically sorted keys (Diets-ordered)
- Consistent numeric representation
- SHA-256 hash computation for canonical data

### TAMPA Runner (`tamparunner.py`)
- Isolated execution environment
- Currently simulates execution (PoC limitation)
- In production: containerized/VM execution with resource limits

### Comparator (`compare_tampa.py`)
- Detects consensus across multiple executions
- Uses canonical hashes for comparison
- Identifies discrepancies

### Decision Composer (`decision_composer.py`)
- Creates structured decision records
- Supports canon proposals and acceptance decisions
- Review workflow management

### Storage (`storage.py`)
- Local filesystem backend
- MinIO S3-compatible backend
- Simple key-value interface

### Sign Helpers (`sign_helpers.py`)
- GPG detached signatures
- JWS (JSON Web Signature) support
- Wrapper for signing decision records

### Reviewer CLI (`reviewer_cli.py`)
- List pending reviews
- Approve/reject proposals
- View review statistics

## API Endpoints

- `GET /` - API information
- `GET /jobs` - List all jobs
- `GET /jobs/{job_id}` - Get job details
- `POST /submit-agent` - Submit agent for execution
- `POST /compare` - Compare multiple job results
- `POST /propose-to-canon` - Propose canonical change
- `GET /reviews/pending` - List pending reviews
- `POST /reviews/action` - Approve/reject review

## Configuration Files

- `configs/canon_change_policy.json` - Policy for canonical changes
- `configs/acceptance_policy_v1.json` - Job acceptance criteria
- `configs/authority_v1.json` - Authority and signing configuration

## See Also

- [RUNNING_LOCALLY.md](RUNNING_LOCALLY.md) - Local development setup
- [SIGNING_HOWTO.md](SIGNING_HOWTO.md) - GPG signing guide
- [EXAMPLES/](EXAMPLES/) - Example job specifications
