#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash) — deny a short list of never-do commands.
# Exit 2 blocks the call; the reason on stderr is fed back to the agent.
# Scope honesty: this is an agent convenience guard, not a security boundary
# (regex guards are bypassable via aliases/functions/quoting); server-side
# rules and CI remain the real gate.
set -u

command -v jq >/dev/null 2>&1 || exit 0   # never block on our own missing dep
CMD=$(jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -n "$CMD" ] || exit 0

# Drop quoted strings so flag patterns never match inside commit messages etc.
# (a quoted "--no-verify" would still work as a flag — accepted ceiling; false
# positives on legit commands are worse than a clever bypass here)
STRIPPED=$(printf '%s' "$CMD" | sed -E "s/'[^']*'/ /g; s/\"[^\"]*\"/ /g")

deny() { echo "$1" >&2; exit 2; }

# 1. Bare pip / python -m pip outside uv (command position only — 'uv run
#    python', 'grep python' and 'which pip' stay legal)
if printf '%s' "$STRIPPED" | grep -qE '(^|[;&|]\s*)pip3?\s+install\b'; then
  deny "Blocked: bare 'pip install' breaks the uv-managed environment. Use 'uv add <pkg>' (or 'uv add --dev <pkg>')."
fi
if printf '%s' "$STRIPPED" | grep -qE '(^|[;&|]\s*)python3?\s+-m\s+pip\b'; then
  deny "Blocked: 'python -m pip' bypasses uv. Use 'uv add' / 'uv pip' inside the project environment."
fi

# 2. Recursive force-delete of a broad path (handles combined and split flags)
if printf '%s' "$STRIPPED" | grep -qE '(^|[;&|]\s*)rm\s'; then
  RMPART=$(printf '%s' "$STRIPPED" | sed -E 's/^.*(^|[;&|])[[:space:]]*rm[[:space:]]/rm /')
  has_r=0 has_f=0 broad=0
  set -f  # no glob expansion while tokenizing ('*' must stay literal)
  for tok in $RMPART; do
    case "$tok" in
      --recursive) has_r=1 ;;
      --force) has_f=1 ;;
      --*) : ;;
      -*) case "$tok" in *r*|*R*) has_r=1 ;; esac
          case "$tok" in *f*) has_f=1 ;; esac ;;
      '/'|'/*'|'~'|'~/'|'~/*'|'.'|'./'|'./*'|'..'|'*') broad=1 ;;
    esac
  done
  set +f
  if [ "$has_r" = 1 ] && [ "$has_f" = 1 ] && [ "$broad" = 1 ]; then
    deny "Blocked: recursive force-delete of a broad path. Delete specific paths explicitly."
  fi
fi

exit 0
