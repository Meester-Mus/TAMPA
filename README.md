# TAMPA - Datanet Agent PoC

Transversal Artificial Meta-Processing Architecture (T.A.M.P.A.) is a canon-first system defining a strict separation between internal truth and external markets. It combines Diets-ordered canonical serialization (DOS-MGC1-v1), Ed25519 verification, and cross-language test vectors to ensure reproducible, tamper-resistant computation.

## Datanet Agent - Proof of Concept

This repository contains a PoC implementation of the TAMPA Datanet Agent, featuring:

- **FastAPI Application**: REST API for job submission and review workflows
- **Canonicalize v1**: DOS-MGC1-v1 reference implementation for deterministic JSON serialization
- **TAMPA Runner**: Local isolated execution environment (simulated in PoC)
- **Comparator**: Consensus detection across multiple executions
- **Decision Composer**: Structured decision records for canonical changes
- **Reviewer CLI**: Command-line interface for approval/rejection workflows
- **Signing Helpers**: GPG detached signatures and JWS support
- **Storage Layer**: Flexible backend (local filesystem or MinIO S3)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start services with Docker Compose
cd compose
docker-compose up -d

# Run tests
pytest tests/ -v
```

For detailed setup instructions, see [docs/RUNNING_LOCALLY.md](docs/RUNNING_LOCALLY.md).

## Documentation

- [docs/README.md](docs/README.md) - Architecture and component overview
- [docs/RUNNING_LOCALLY.md](docs/RUNNING_LOCALLY.md) - Local development guide
- [docs/SIGNING_HOWTO.md](docs/SIGNING_HOWTO.md) - GPG signing guide
- [docs/EXAMPLES/](docs/EXAMPLES/) - Example job specifications

## API Endpoints

- `GET /` - API information
- `POST /submit-agent` - Submit agent job
- `POST /compare` - Compare execution results
- `POST /propose-to-canon` - Propose canonical change
- `GET /reviews/pending` - List pending reviews
- `POST /reviews/action` - Approve/reject reviews

## PoC Limitations

- **Manual Agent Execution**: Agent code requires manual ChatGPT paste (not automated)
- **GPG Signing**: Requires manual GPG setup and key management
- **Simulated Runner**: TAMPA runner simulates execution instead of using containers
- **Local Storage**: Default storage is filesystem-based (MinIO optional)

## Licensing

This project uses a dual-license model:

- Source code available under the Apache License 2.0 (see LICENSE file)
- Additional MIT License for PoC components (see LICENSE-MIT file)
- Canon License v0.1 governs canonical specifications

The Canon Holder retains all exclusive rights to canonical specifications. Commercial use, production deployment, distribution, or integration requires a separate Commercial Partner License.
