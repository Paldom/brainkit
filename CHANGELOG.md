# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
