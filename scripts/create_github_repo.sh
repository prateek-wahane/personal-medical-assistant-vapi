#!/usr/bin/env bash
set -euo pipefail

VISIBILITY="${1:-public}"
REPO="prateek-wahane/personal-medical-assistant-vapi"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Install it first: https://cli.github.com/"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial commit: Personal Medical Assistant with Vapi" || true
fi

git branch -M main

gh repo create "$REPO" --"$VISIBILITY" --source=. --remote=origin --push

echo "Repository created and pushed: https://github.com/$REPO"
