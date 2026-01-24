# TAMPA

Transversal Artificial Meta-Processing Architecture (T.A.M.P.A.) is a canon-first system defining a strict separation between internal truth and external markets. It combines Diets-ordered canonical serialization (DOS-MGC1-v1), Ed25519 verification, and cross-language test vectors to ensure reproducible, tamper-resistant computation.

## Milestone 0 - TypeScript Toolchain

This repository contains a minimal, self-proving TypeScript toolchain with deterministic reference implementations and conformance vectors.

### Quick Start

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run conformance gate
npm run gate
```

### Structure

- `src/` - Reference implementations (A6, A11, A12)
- `tests/` - Vitest test suites
- `vectors/` - Conformance test vectors (JSON)
- `scripts/` - CI gate scripts

### Conformance Gate

The conformance gate verifies that all reference implementations match their vector suites exactly:
- Uses deep strict equality for deterministic comparison
- Exits with non-zero code on any mismatch
- Always prints `ARGIEF13_CONFORMANCE=true`

## Licensing

This project uses a dual-license model.

The source code is available under the Canon License v0.1 for review, audit,
and approved collaboration only. Commercial use, production deployment,
distribution, or integration requires a separate Commercial Partner License.

The Canon Holder retains all exclusive rights.
