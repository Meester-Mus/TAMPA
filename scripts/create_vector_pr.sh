#!/usr/bin/env bash
set -e

# Script to create branch, add files, commit, push and open PR for FAISS vector search prototype

BRANCH_NAME="feat/mcp-vector"
BASE_BRANCH="main"
COMMIT_MSG="feat(mcp): add FAISS vector search prototype"
PR_TITLE="feat(mcp): add FAISS vector search prototype"
PR_BODY_FILE="pr_body_mcp_vector.txt"

echo "Creating branch $BRANCH_NAME from $BASE_BRANCH..."
git checkout -b "$BRANCH_NAME" "$BASE_BRANCH" || git checkout "$BRANCH_NAME"

echo "Adding all files..."
git add .

echo "Committing changes..."
git commit -m "$COMMIT_MSG"

echo "Pushing to origin..."
git push -u origin "$BRANCH_NAME"

echo "Creating pull request..."
if command -v gh &> /dev/null; then
    gh pr create --base "$BASE_BRANCH" --head "$BRANCH_NAME" --title "$PR_TITLE" --body-file "$PR_BODY_FILE"
    echo "Pull request created successfully!"
else
    echo "GitHub CLI (gh) not found. Please create the PR manually:"
    echo "  gh pr create --base $BASE_BRANCH --head $BRANCH_NAME --title \"$PR_TITLE\" --body-file $PR_BODY_FILE"
fi
