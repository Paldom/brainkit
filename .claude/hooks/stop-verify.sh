#!/usr/bin/env bash
# Stop hook — refuse to end the turn while the quality gate fails.
# Exit 2 on Stop means "keep working"; the harness force-overrides after 8
# consecutive blocks. The stop_hook_active guard below is MANDATORY — without
# it this hook loops the first time the agent cannot immediately fix a failure.
set -u

command -v jq >/dev/null 2>&1 || exit 0
INPUT=$(cat)
ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null) || exit 0
[ "$ACTIVE" = "true" ] && exit 0   # already re-running because of us — let go

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# The repo quality gate (same as CI Phase-2).
# --frozen: never re-resolve uv.lock (it is orchestrator-owned).
VERIFY_CMD='uv run --frozen ruff check . && uv run --frozen ruff format --check . && uv run --frozen mypy src tests && uv run --frozen pytest --cov -q'

OUT=$(bash -c "$VERIFY_CMD" 2>&1) || {
  echo "Verification failed ($VERIFY_CMD). Fix before finishing:" >&2
  echo "$OUT" | tail -30 >&2
  exit 2
}

exit 0
