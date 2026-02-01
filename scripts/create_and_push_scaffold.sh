#!/usr/bin/env bash
set -euo pipefail
BRANCH=feat/rescaffold-datanet
git fetch origin
git checkout -b "$BRANCH" origin/main || git checkout -b "$BRANCH"
# write files (assumes run from repo root)
mkdir -p src/datanet tests scripts
# (the agent should write the files exactly as specified in the PR)

git add -A
git commit -m "chore(scaffold): add datanet scaffold" || true
git push -u origin "$BRANCH"
