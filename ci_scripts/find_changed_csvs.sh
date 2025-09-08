
#!/usr/bin/env bash
set -euo pipefail
BASE_REF="${1:-origin/main}"
git fetch --no-tags --depth=1 origin +refs/heads/*:refs/remotes/origin/*
git diff --name-only "$BASE_REF"...HEAD | grep -E '\.csv$' || true
