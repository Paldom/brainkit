# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **researchkit research-pack contract v2.** Ingest checks the materials
  manifest before writing anything. It accepts v1 (no `schema_version`) and v2,
  and refuses an unknown version, an incomplete pack (`complete` not true) or a
  material file whose sha256 differs from the manifest. A `claims.jsonl` whose
  digest differs from `claims_sha256` is refused too.
- **Cited claims in the topic note.** When the run carries `claims.jsonl`, its
  topic note lists the verbatim cited sentences under `## Cited claims`, each
  linked to its source note. With `include_reports=False` the claims replace the
  run's synthesized summary: the brain holds what the sources were cited for,
  not the report's prose.
- **Run ledger** (`.brainkit/ledger.jsonl`): one row per run, URL and content
  digest. A re-ingest skips a capture this run already merged, and the
  provenance trail survives later rewrites.

### Changed

- **`context` leaves superseded notes out by default** (the read-path guard). A
  note another note supersedes no longer reaches the answer pack an agent acts
  on. `--include-superseded` (CLI) and `include_superseded` (MCP) bring it back
  for history questions. `search` still ranks it below its replacement.

## [0.3.0] - 2026-10-20

The brain becomes trustworthy to write into and measurable to search. Every
v0.2.0 data-loss bug found in review is fixed and pinned by a byte-level golden
test against v0.2.0 output; ranking changes now ship only through a labelled
eval with dev/held-out splits.

### Added

- **Eval harness.** `brainkit eval CASES.jsonl` scores Recall@5, MRR, nDCG and
  false positives on no-answer queries. `tests/eval/` holds a pinned corpus,
  lexical/paraphrase/relational/title/negative/multilingual/lifecycle strata,
  per-split floors, and a cluster-bootstrap experiment runner. Each ranking
  decision is recorded in `docs/eval/decisions/`.
- **Agent-facing reads.** `--json` on the read commands (`schema: "brainkit/1"`,
  JSON errors); `read` at abstract/outline/full depth or one `--section`;
  `verify` a quotation against a note; `search --explain` and `--why`;
  `context --budget/--exclude`; `lint --gaps`; `export llms-txt`.
- **Query variants.** `search --also "…"` fuses agent-written paraphrases (RRF,
  original query weighted 2x, skipped when the original is confident).
- **Trust labels.** Computed, never stored: `derived`/`unsourced` for
  agent-written notes without a human verification, `superseded`, and hygiene
  flags for hidden characters, hidden markup, injection-shaped text and
  credentials. `lint` checks grounding (quotes, dates and numbers must occur in
  the sources a note derives from), `^[path:Lx-y]` locators, supersession and
  derivation chains.
- **Cross-run subject notes.** Agent-authored notes keep an append-only history
  below `<!-- brainkit:history -->`; `<!-- brainkit:keep -->` regions survive
  regeneration; replaced captures are archived under `notes/sources/.captures/`.
- **Time and drafts.** `--as-of DATE` and `--include-drafts` on search/context.
- **Rung 2, opt-in.** `brainkit vectors pull|build|status|export|import` and
  `--vectors`: a pinned 256-dimension static embedding model, stdlib-only
  inference, fused by RRF. `vectors pull` is brainkit's only network access.
- **Answer-level check.** `tests/eval/answer_check.py` runs real agents on 20
  fixed questions (CLI + skill vs MCP) and scores consultation, citations,
  superseded decisions and gaps deterministically; results are in the README.
- **MCP server.** `brainkit mcp` serves the brain read-only over stdio (protocol
  2026-07-28 and 2025-11-25).
- **Claude Code plugin.** `.claude-plugin/` packages the skill, plus an opt-in
  SessionStart hook (`BRAINKIT_HOOKS=1`) that prints the brain pointer.
- Markdown links count as graph edges; `aliases` keep old slugs resolvable;
  `ingest-notes --namespace` gives imports a stable origin.

### Changed

- **Ranking** (each change measured): abstention on low-confidence queries, an
  exact title match ranks first, citations propagate half their score to
  unmatched parent notes, superseded notes are halved. Multilingual tokenization
  (accent folding, compounds, CJK bigrams).
- **Write safety.** One OS-level writer lock, atomic writes that preserve file
  mode, symlink confinement. Rewrites refuse a >30% shrink, a rewritten history,
  or a changed type; `--expect-digest` gives compare-and-swap; list fields merge
  instead of being replaced. Refusals exit 1.
- **Provenance admission.** A title alone is no longer provenance; title-only
  imports pass with a warning for one more minor version.
- A no-op ingest writes nothing, including the log; counts are real.
- `context` counts represented runs over plural `projects` and calls archived
  pages "source archives".
- README: the withdrawn gbrain BrainBench P@5 figure is no longer cited.
- CI validates an ingested brain with the independent OKF v0.2 validator
  (`scaccogatto/okf-skills`, pinned).

### Fixed

- A failed or leaked synthesis no longer overwrites a good topic note.
- Imported notes with the same title no longer overwrite each other; an import
  can no longer shadow a slug at another level (`duplicate-slug` lint error).
- Re-ingesting a URL merges provenance instead of dropping it.
- Typed frontmatter (numbers, lists, nested values) round-trips unchanged.

## [0.2.0] - 2026-09-07

The brain becomes a pyramid. Notes now sit at four levels — domain, topic,
report, source — with an index at each, so an agent descends from a map to a
primary source instead of searching a flat namespace. Bundles are Open Knowledge
Format v0.2 conformant, verified with an external validator, and re-ingesting a
research run is inert down to the byte.

Existing brains keep working; run `brainkit rebuild` once to migrate their
frontmatter and regenerate the indexes.

### Added

- **The brain is a pyramid.** A boosted researchkit run already contains a
  hierarchy — a parent over sub-projects — and ingest used to flatten it into
  sibling topic notes. The parent now becomes a `domain` note (`notes/domains/`)
  linking down to its topics, each topic carries a `parent`, and report sections
  are linked from the topic that produced them. Four levels: domain → topic →
  report → source.

- `brainkit context "query"` — the same ranked hits as `search`, plus the
  descent path to each and mechanical **coverage signals**: which query terms
  appear nowhere in the brain, how many research runs are represented, whether
  any primary source matched, how many hits are social-tier. Deliberately not
  called `think`: these are retrieval gaps, and brainkit has no model with which
  to claim anything about knowledge gaps.

- `brainkit lint` — read-only integrity check (dead links, unreachable notes,
  duplicate URLs, drifted `corroboration`, bad dates, case-folding path
  collisions, a stale index) with `--as-of DATE` so a CI run is reproducible and
  cannot turn red without a commit. Staleness and index size are _warnings_ and
  do not fail the gate; `--warnings-as-errors` opts in.

- `brainkit rebuild` — re-derives what brainkit owns (frontmatter encoding,
  `corroboration`, every index) and rewrites only what changes. Separate from
  `lint` so lint keeps a read-only contract. This is the migration path for
  brains written by an older version.

- OKF v0.2 conformance: an `index.md` at every level (§8 progressive
  disclosure), `okf_version` in the bundle-root index (§12), date-grouped
  `log.md` (§9), `generated: {by, at}` actors (§5.2, superseding `ingested_at`),
  `tags` from the run's research keywords (§4.1), and `description` on every
  synthesized note. Verified against an external OKF validator.

- A resolved wiki-link graph: `[[slug]]` links have been written into topic
  notes since v0.1 and never read back. `link_graph()` now resolves them into
  edges and backlinks, and lint uses them for dead-link and reachability checks.
  Body links are read only from notes brainkit or a human authored — a scraped
  article _about_ wikis quotes `[[note-name]]` as an example, which invented 94
  dead links on a real corpus. Any note may instead carry an explicit `related`
  list, which is how a report section or an annotated source gets a real edge.

- A material that is not valid UTF-8 no longer aborts the whole ingest. One bad
  byte in one scraped page used to lose every source in the run, with an error
  that did not even name the file; undecodable bytes are now replaced and the
  repair is reported in `IngestReport.repaired_sources`.

### Changed

- **Frontmatter values are JSON-encoded.** They are now always parseable YAML —
  46% of the notes in a real 87-note brain previously failed `yaml.safe_load`,
  every case a title containing `": "`, because values were emitted unquoted.
  Encoding also removes YAML's implicit-type traps, which quoting-only-when-
  necessary does not: left plain, a title of `007` loads as the integer 7,
  `12:00:00` as 43200 and `2026-01-01` as a date, and which of those fire varies
  between YAML 1.1 and 1.2 consumers. Structure is preserved — `tags` stays a
  list, `generated` stays a mapping. Run `brainkit rebuild` to migrate.

- **`index.md` is a map, not a listing.** It carries domains and topics and
  links to each level's own index; it no longer inlines every source under every
  topic. That listing measured 17.9 KB at 4 topics and 83 sources, which
  extrapolates past 450 KB at a hundred topics — an artifact no agent can afford
  to load, describing a brain it is meant to make navigable. The same corpus now
  produces a 2.7 KB root index at 1185 sources.

- Ranking is BM25 with per-level length normalization plus a level prior
  (domain > topic > report > source), replacing raw term frequency with a flat
  2x kind boost. The generated `## Topics`/`## Sources` link lists are excluded
  from scoring, so a domain note no longer inherits the vocabulary of everything
  beneath it. Ties break on query coverage, then level, then content date. The
  constants are BM25 defaults and the prior keeps the old 2x ceiling — untuned,
  because there is no eval set yet.

- Report sections are ingested by default (`--no-include-reports` opts out), and
  chunking stops at the first raw-archive heading, so the analysis becomes notes
  and the per-provider dumps — which outnumber it roughly 4:1 — do not.

- `search` hits carry their level and their parent; the CLI prints the level
  next to the score, because an agent should decide from a reason rather than a
  bare number.

### Fixed

- **`rebuild` could destroy a value.** It reconstructed frontmatter from
  `Note.meta`, a flat string mapping that cannot distinguish a value written as
  the JSON string `"null"` from one written as the literal `null` — so a title
  of "null" became an actual null, and "25" became a number. Rewrites now work
  from the raw frontmatter text via `raw_frontmatter()`.

- A frontmatter key containing a colon was written correctly and then read back
  wrong, because the reader partitioned on the first colon. Quoted keys are now
  scanned before the split.

- A leading byte-order mark made a note's entire frontmatter invisible.

- `## Report sections` was not excluded from scoring, so a topic note inherited
  the vocabulary of the sections it links to — the same defect already fixed for
  `## Topics` and `## Sources`, missed when the section was added.

- Lone surrogates (which cannot be encoded as UTF-8 at all, and so aborted the
  write) and the U+FFFE/U+FFFF non-characters are now escaped alongside DEL and
  the C1 block. Whitespace is collapsed inside list and map values too, not only
  in top-level strings.

- **A source note's body could end up wearing provenance it did not come from.**
  When two runs archive one URL the fuller capture wins, but the note merged
  _every_ citing run's attribution onto it — so pruning the run that supplied
  the body left the body behind, credited to runs that never fetched it. The
  supplying run is now recorded as `content_from`, and `lint` reports
  `orphaned-content` when it stops citing the note.

- **`topics` and `projects` grew without bound on every re-ingest.** They were
  stored comma-joined and split on `,`, but a researchkit topic is a sentence
  and most contain commas, so the stored value could not be split back into the
  items that went in and the whole topic was appended again each run. Both are
  now JSON lists.

- **Re-ingesting identical input is now inert down to the byte.** It used to
  rewrite every note: `generated.at` always moved, and for a URL archived by two
  sub-projects the note's title, body, `providers` and metadata oscillated
  between the two archives on every run. A note is now left untouched when only
  its timestamp would change, `providers` is a union, and the fuller archive
  wins deterministically.

- Report notes were deleted before being rewritten, which defeated the unchanged
  check; stale sections are now removed after the write instead.

- `_description` skipped a heading and its first sentence together when they
  were separated by a single newline — which is exactly how researchkit writes
  `## Executive Summary` — and then settled on a `---` rule as the description.

- Frontmatter no longer emits DEL or C1 control characters literally. `json`
  leaves them as-is and YAML 1.2 §5.1 excludes them, so mojibake from one
  mis-decoded scraped page was enough to make a note unparseable.

- Index links resolve from the file that contains them; per-level indexes
  previously emitted bundle-root-relative paths that resolved nowhere.

## [0.1.0] - 2026-07-22

### Added

- Codex support at Claude-Code parity: the brainkit skill is discoverable by
  Codex and other Agent-Skills-standard agents via an `.agents/skills/` symlink
  (source of truth stays `.claude/skills/`); AGENTS.md remains the shared
  instruction file.

- Agent-discovery pointer: `brainkit pointer [--write FILE]` prints a short
  marker-fenced snippet for AGENTS.md/CLAUDE.md (brain path + search usage);
  `--write` appends idempotently and UPDATES the fenced block in place when the
  brain path changes. The path is used as given, so the default `./brain` stays
  portable in committed files.
- Deterministic corroboration: source notes carry `corroboration: <N>` — the
  count of research runs citing the URL, derived from the `projects:` list by
  one shared function on both the write and prune paths (no LLM judgment, no
  drift).
- OKF alignment: source notes carry a `description:` blurb (the same derivation
  the index uses), and every ingest appends one line to a root-level `log.md`
  journal (OKF reserved filename; outside note discovery) — a git-diffable
  record of what was written when.

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

[unreleased]: https://github.com/Paldom/brainkit/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Paldom/brainkit/releases/tag/v0.3.0
[0.2.0]: https://github.com/Paldom/brainkit/releases/tag/v0.2.0
[0.1.0]: https://github.com/Paldom/brainkit/tree/045c19d
