# AGENTS.md

brainkit is a portable, human-readable agent brain: Git-native markdown bundles
with hybrid RAG retrieval, gated writes, and cited answers. Python package,
`src/brainkit` layout, tests in `tests/`, managed with uv.

## Commands

- Install/sync: `uv sync`
- Lint: `uv run ruff check .` (auto-fix: `uv run ruff check --fix .`)
- Format: `uv run ruff format .` (verify: `uv run ruff format --check .`)
- Type check: `uv run mypy src tests` (mypy strict)
- Tests: `uv run pytest --cov -q` (branch coverage, fail_under=90)
- Full gate (run before calling any task done):
  `uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest --cov -q`

## Environment

- Use `uv` for everything — never `pip install`, `poetry`, or bare `python`. Run
  tools via `uv run <tool>`.
- Dependencies are added with `uv add <pkg>` (dev: `uv add --dev <pkg>`), but
  `uv.lock` is orchestrator-owned: never edit it by hand and do not run
  `uv add`/`uv lock` yourself — report the dependency need instead.

## Definition of done

- The full gate above passes locally before you present work as complete. Run
  it; do not assume.
- Never weaken a gate to pass it: no lowering the coverage threshold, no
  skipping/deleting failing tests, no `|| true`, no `--no-verify`.
- Requires Python >=3.11; pinned tool versions (ruff 0.15.20, mypy 2.1.0) are
  enforced — do not change them to make errors go away.

## Git

- Never `git commit --no-verify`.
- Never force-push; especially never to `main`/`master`.

## Review boundaries

- Flag — do not silently change — anything touching dependency declarations,
  `uv.lock`, `pyproject.toml` tool config, `.pre-commit-config.yaml`,
  `.github/workflows/`, or `.claude/`.
- New dependencies require explicit human sign-off; verify the package exists
  and is established before proposing it.

## Conventions

- `src/` layout: import as `brainkit`, never add `src` to `sys.path`.
- mypy is strict: every function fully annotated, no untyped defs.
- pytest runs with `filterwarnings = error` — warnings fail tests.
- Line length 88, double quotes (ruff format owns style; don't hand-format).
