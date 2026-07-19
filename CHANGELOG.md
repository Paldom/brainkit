# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Search hits surface their trust tier: source notes found via social queries
  print a `(social)` marker (user-generated content is the classic poisoning
  vector), and `content_digest` from researchkit materials passes through to
  source notes for content lineage across re-downloads.

- Freshness-aware search ranking (deterministic): equal-relevance hits now break
  ties by content date — `published` from the source material, newest first;
  undated notes rank last rather than borrowing freshness from their ingest
  time. Day-ordinal comparison (machine-independent: no local-time
  `timestamp()`, pre-1970 dates need no special case), and the CLI prints the
  date next to each hit. Plain recency logic, no LLM judgment, no decay windows.

- Research metadata passthrough (E2E completeness audit, 2026-07-11): source
  notes now carry `source_type`, `content_kind`, `published`, and `final_url`
  from the material frontmatter; on shared-URL merges, fields the newer material
  lacks keep the existing note's value (union semantics — provenance is never
  lost).

- Boosted-run ingestion (field feedback, 2026-07-08): `ingest` recurses into a
  boosted researchkit run's `subprojects/*` (each a normal project) and
  understands the boost-shaped parent `result.json`
  (`overarching_topic`/`super_summary`), so deep runs no longer ingest to just a
  topic note. Un-run sub-projects are reported, not fatal. Sub-project brain
  identity is parent-qualified (`<parent-run>/<sub>`) because researchkit sub
  names repeat across boosted runs — re-running a boosted topic no longer prunes
  the previous run's sub notes.
- `ingest --include-reports`: chunks `report.md` `##` sections into
  `type: report` notes with project provenance — materials-thin runs stay
  queryable. The splitter is fence-aware (`## ` inside code blocks is content)
  and repeated headings get distinct `-2`/`-3` notes instead of overwriting each
  other.
- `ingest-notes <file|dir>`: ingest arbitrary frontmattered markdown from any
  producer. Notes with a `url` join the deduplicated source notes; other
  provenance-carrying notes land in `notes/imported/`; anonymous free text is
  still rejected (the write gate is provenance, not producer).
- Search: `--kind topic|source|report|note` filter, and a 2x score boost for
  synthesized topic/report notes so long chatty source archives stop outranking
  on-domain knowledge (cross-corroborated relevance feedback).
- CLI `-v/--verbose`: per-file skip reasons on ingest
  (`skipped materials/003-….md: no 'url' in frontmatter`).

### Fixed

- Report-note prefix collision (found by a 900-source live audit): a boosted run
  under a long parent name truncated every `<parent>/sub_NN` slug to the same
  prefix, so each sub-project's stale-prune deleted its siblings' report notes
  (262 written, 63 surviving). The prefix now carries a name-digest suffix, same
  identity trick as topic notes.
- cwd footgun under `uv run --directory`: relative project paths are resolved
  against the shell's `$PWD` when it differs from the process cwd, and a missing
  `result.json` error now prints the exact absolute path that was tried instead
  of misdiagnosing an un-run project.

- Richer index nodes: every source line in `index.md` now carries a one-line
  description (the note's first prose paragraph, truncated), so agents can pick
  sources from the index without opening each note.
- Integration hardening (cross-review + live agent QA): ingestion is
  manifest-driven (stale material files from earlier runs are ignored; glob
  fallback without a manifest), source-note identity is the URL even when
  citation titles drift between runs (digest-verified, hash-collision fallback),
  and search hits without a URL (topic notes) cite their research run instead.
- Brain building: `brainkit ingest` turns researchkit projects (result.json +
  downloaded materials) into a Git-native brain of frontmattered notes — topic
  notes with wiki-links, deduplicated source notes that accumulate topics across
  runs, and a generated `index.md`.
- Cited retrieval: `brainkit search` (title-weighted lexical scoring) plus
  `list`/`index` commands and the `brainkit` console script.
- Claude Code skill (`.claude/skills/brainkit`) for answering from the brain
  with source citations.

- `parse_note` / `Note`: markdown documents with `---` frontmatter.
- `slugify`: unicode-folding kebab-case slugs.
- Full toolchain: uv packaging, ruff, strict mypy, pytest with branch coverage,
  pre-commit, CI quality gate, and release automation.
