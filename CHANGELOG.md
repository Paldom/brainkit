# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `parse_note` / `Note`: markdown documents with `---` frontmatter.
- `slugify`: unicode-folding kebab-case slugs.
- Full toolchain: uv packaging, ruff, strict mypy, pytest with branch coverage,
  pre-commit, CI quality gate, and release automation.
