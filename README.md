<p align="center">
  <img src="icon.svg" alt="brainkit icon" width="128">
</p>

# brainkit

A portable, human-readable brain for AI agents: a Git-native markdown wiki as
the source of truth, an escalating retrieval ladder on top, with gated writes
and search that cites its sources.

[![CI](https://github.com/Paldom/brainkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Paldom/brainkit/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)

```mermaid
flowchart LR
    T(["💡 any topic"]) --> RK["🔍 <b>researchkit</b><br/>12 AI search providers in parallel:<br/>one cited report + archived sources"]
    RK -- "one-shot:<br/>teach every agent" --> SK["⚡ <b>skillskit</b><br/>research pack in, validated skill out —<br/>installable in 70+ agents via skills.sh"]
    RK -- "compounding:<br/>grow a memory" --> BK["🧠 <b>brainkit</b><br/>portable hybrid brain (OKF wiki + retrieval ladder),<br/>cited answers for agents and harnesses"]
    classDef here stroke:#f97316,stroke-width:3px;
    class BK here
```

**The compounding path.** [researchkit](https://github.com/Paldom/researchkit)
digs; brainkit grows every run into one portable, cited brain your agents query
forever — or package a one-shot skill instead with
[skillskit](https://github.com/Paldom/skillskit).

**What:** a _brain_ is a folder of frontmattered markdown built from
[researchkit](https://github.com/Paldom/researchkit) research runs — source
notes, topic notes, and a generated index that agents and teammates both read.
**Who:** anyone who wants agent long-term memory or a team knowledge base
without a database, a SaaS, or a vector store they can't inspect. **Why:**
knowledge you can't diff, review, grep, or delete isn't knowledge you can trust
— so everything is plain text in Git, writes are gated, and hits cite their
sources. Status: alpha (v0.2.0); interfaces may move, but your data stays
readable plain markdown even if they do.

```mermaid
flowchart LR
    RK["researchkit run<br/>result.json + materials/"] -->|brainkit ingest| BRAIN
    subgraph BRAIN["brain/ — plain markdown, in Git (source of truth)"]
        direction TB
        D["notes/domains/*.md<br/>the map over a boosted run"]
        T["notes/topics/*.md<br/>one per research run"]
        P["notes/reports/*.md<br/>one per analysis section"]
        S["notes/sources/*.md<br/>one per URL, deduped"]
        D -.->|wiki-links| T -.-> P
        T -.-> S
    end
    subgraph LADDER["access layer — every rung a rebuildable projection"]
        direction BT
        R0["rung 0 · grep, cat, your editor<br/>shipped"]
        R1["rung 1 · BM25 + level prior<br/>shipped — search / context"]
        R2["rung 2 · embeddings + RRF<br/>designed"]
        R3["rung 3 · typed graph<br/>partly shipped — wiki-link graph"]
        R0 --> R1 --> R2 --> R3
    end
    BRAIN --> LADDER
    LADDER -->|cited hits| AGENT["rung 4 · your agent's loop<br/>shipped — bundled agent skill"]
    classDef shipped fill:#e6f4ea,stroke:#137333,color:#0d652d
    classDef designed fill:#f1f3f4,stroke:#9aa0a6,color:#5f6368,stroke-dasharray: 5 5
    class R0,R1,R3,AGENT shipped
    class R2 designed
```

Solid green rungs are shipped; the dashed rung is designed and next. The bundle
is a **pyramid**: a domain note summarizes its topics, a topic note cites its
sources, and every level carries its own `index.md` so an agent can descend from
a map to a primary source instead of searching blind.

## Why brainkit

- **Portable by construction.** A brain is a folder of markdown in Git: clone
  it, fork it, hand it to another agent or another machine — no export step, no
  migration, no hosted anything.
- **More than a wiki.** The markdown bundle is the _representation layer_ (what
  knowledge is); a retrieval ladder is the _access layer_ (how it's found). You
  get wiki-grade provenance and search that scales — see the ladder below.
- **Gated writes.** The CLI creates notes only through ingestion, and every
  ingested file must carry provenance frontmatter (a `url`, project, or title) —
  no anonymous free text quietly becoming truth. (Files stay plain markdown;
  pair with Git review for a hard gate.)
- **Cited retrieval.** Source hits print their URL right in the result, and the
  bundled agent skill (Claude Code via `.claude/skills/`, Codex and other
  Agent-Skills-standard agents via `.agents/skills/`) instructs agents to answer
  with provenance, not vibes.
- **Idempotent ingestion.** Re-ingest freely: a source cited by five research
  runs stays one note that accumulates all five topics.
- **Zero runtime dependencies.** Pure standard-library Python 3.11+ — `uv sync`
  and you are running.

## Quick start

```bash
uv tool install brainkit     # or: pipx install brainkit / pip install brainkit
```

[researchkit](https://github.com/Paldom/researchkit) is a separate tool and is
not on PyPI yet — clone it alongside if you want it to feed the brain:

```bash
# 1. research a topic with materials (researchkit needs provider API keys or logged-in CLI subscriptions — see its README)
git clone https://github.com/Paldom/researchkit
uv run --directory researchkit researchkit "your topic" --materials

# 2. ingest the run into a brain — a boosted run's sub-projects come too
brainkit --brain brain ingest "$PWD/researchkit/projects/<run>"

# 3. query it
brainkit --brain brain search "your question" -n 5
brainkit --brain brain context "your question"   # + descent path and coverage gaps
```

Expected result — ranked hits, each carrying its level and its citation:

```
[topic 34.8] Self-hosting in practice… (research run: 20260828_221435_…/sub_04_…)
    Practitioners are increasingly rallying around "own your memory, rent…
    note: brain/notes/topics/self-hosting-in-practice--20260828-221435-…md
[source 25.0] Rent the Intelligence. Own the Memory. <https://nowledge-labs.ai/blog/…>
    ...the matching snippet from the note body...
    note: brain/notes/sources/1a2b3c4d-some-source-title.md
```

The brain directory defaults to `$BRAINKIT_DIR` or `./brain`.

## Commands

| Command                       | What it does                                                                                                                                                                                                                                                                                                   |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ingest <project>`            | Turn a researchkit run (`result.json` + `materials/`) into one topic note plus deduplicated source notes and the report's analysis sections. A boosted run's `subprojects/` are ingested recursively and its parent becomes the **domain** note over them. Re-ingesting is inert down to the byte              |
| `ingest --no-include-reports` | Skip chunking `report.md` into `type: report` notes (they are ingested by default)                                                                                                                                                                                                                             |
| `ingest-notes <path>`         | Ingest arbitrary frontmattered markdown (file or directory): notes with a `url` join the deduplicated sources; other provenance-carrying notes land in `notes/imported/`                                                                                                                                       |
| `search "q" -n 5`             | BM25 with per-level length normalization and a bounded preference for higher levels, tie-broken by query coverage, level, then content date. Hits print their level, score, published date, a `(social)` trust marker, source URL, snippet and note path. `--kind domain\|topic\|report\|source\|note` filters |
| `context "q"`                 | The same hits plus the **descent path** to each and mechanical coverage signals — unmatched query terms, how many research runs are represented, whether any primary source matched. Retrieval gaps, not knowledge gaps                                                                                        |
| `lint [--as-of DATE]`         | Read-only integrity check: dead links, unreachable notes, duplicate URLs, drifted counts, bad dates, a stale index (errors); stale notes and an oversized root index (warnings). Exits 1 on errors only                                                                                                        |
| `rebuild`                     | Re-derive what brainkit owns — frontmatter encoding, `corroboration` counts, every index — and rewrite only what changes. The migration path for brains written by an older version                                                                                                                            |
| `list`                        | List every note with its type and title                                                                                                                                                                                                                                                                        |
| `index`                       | Regenerate `index.md` — the map of domains and topics                                                                                                                                                                                                                                                          |
| `pointer [--write FILE]`      | Print (or idempotently append/update in FILE) a short agent-discovery snippet for AGENTS.md/CLAUDE.md: the brain path plus how to query it                                                                                                                                                                     |

Pass `-v` to `ingest`/`ingest-notes` to see why any file was skipped (e.g.
`skipped materials/003-….md: no 'url' in frontmatter`). Relative project paths
are resolved against your shell's `$PWD` when the process cwd differs (the
`uv run --directory` case), and errors print the exact absolute path that was
tried.

Source notes carry deterministic provenance frontmatter — `url`, `published`,
`content_digest`, and a `corroboration` count (how many research runs cite the
URL) — and every ingest appends one line to the brain's `log.md` journal.

## More than a wiki: the retrieval ladder

A wiki alone answers _"what do we know?"_ — navigation by index works well up to
roughly a hundred sources, then hits a wall. Query-time RAG alone answers
_"where is it?"_ — but nothing is curated and nothing is citable. brainkit
refuses to pick a side, because the two approaches answer different questions
and fail differently: a compiled wiki pays its cost once at ingest and gives
humans and agents the same auditable, citable pages (it wins on synthesis and
provenance); query-time retrieval indexes instead of synthesizing (it wins on
exact lookup over corpora nobody curated). The one
[preregistered head-to-head comparison](https://arxiv.org/abs/2605.18490)
returned a split verdict, not a winner.

So the design is a ladder over one source of truth. Everything above the files
themselves is a **rebuildable projection** of the markdown — delete every index
and you lose nothing; the bundle is never derived from the index, only the other
way around. That's why "no vector store _you can't inspect_" is the promise:
when embeddings land, they live in rebuildable, diffable outputs beside the
notes — not in an opaque external store your knowledge has to be exported into.

| Rung | Access                                                                                       | Status                        |
| ---- | -------------------------------------------------------------------------------------------- | ----------------------------- |
| 0    | Plain files — `grep`, `cat`, your editor work as-is                                          | shipped                       |
| 1    | BM25 + per-level length normalization + level prior (`search`, `context`)                    | shipped                       |
| 2    | Embeddings + hybrid [reciprocal-rank fusion](https://dl.acm.org/doi/10.1145/1571941.1572114) | designed, next rung           |
| 3    | Graph relations between notes — the `[[wiki-link]]` graph, backlinks, reachability           | shipped (untyped edges)       |
| 4    | Your agent's loop over the brain                                                             | shipped via the bundled skill |

Rung 3 landed before rung 2 on purpose. The one published head-to-head on this
stack
([gbrain's BrainBench](https://github.com/garrytan/gbrain/blob/master/docs/architecture/RETRIEVAL.md))
measured lexical-only, vector-only and hybrid-without-graph at the same P@5, and
only the graph moved it — so structure was worth more than embeddings, and it
costs three regexes instead of an index.

## The ideas behind it

brainkit deliberately combines three lineages:

- **[The Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)**
  is the container: a specification Google Cloud introduced in June 2026
  ([spec + reference tooling](https://github.com/GoogleCloudPlatform/knowledge-catalog))
  where knowledge ships as a folder of plain markdown with YAML frontmatter and
  an `index.md` navigation root — an agent reads the index first and loads notes
  on demand. The spec is deliberately permissive; as
  [one early analysis](https://medium.com/@marc.bara.iniesta/googles-new-format-for-agent-context-a-standard-or-just-a-folder-82fb21d92041)
  put it, OKF standardizes the _container_, not the meaning. brainkit layers the
  meaning on top: typed notes, provenance frontmatter, the generated index.
- **[Karpathy's LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)**
  is the maintenance pattern: immutable fetched sources feeding a curated wiki,
  with ingest and query as the verbs. Navigation by index works "surprisingly
  well" up to about a hundred sources — the wall the retrieval ladder exists to
  climb past. brainkit adds the one thing the gist leaves out: the write gate.
- **[Hybrid RAG retrieval](https://www.infoq.com/articles/vector-search-hybrid-retrieval-rag/)**
  with
  [reciprocal-rank fusion (Cormack, Clarke & Büttcher, SIGIR 2009)](https://dl.acm.org/doi/10.1145/1571941.1572114)
  is the access roadmap — minus the "G": brainkit retrieves and ranks, _your
  agent_ generates.

## Works with your agent

An agent skill ships in `.claude/skills/brainkit` (Codex and other
Agent-Skills-standard agents discover it via `.agents/skills/`): search first,
read the top notes, and always cite the `url` from the note's frontmatter. If
the brain has nothing relevant, the skill says so and points at researchkit —
the brain exists to give provenance, not vibes.

## Honest edges

- Retrieval today is rungs 0–1 plus the wiki-link graph: BM25 with per-level
  length normalization and a level prior capped at 2x. The prior and the BM25
  constants are **untuned** — there is no eval set yet, so they are defaults,
  not findings. Rung 2 (embeddings + hybrid fusion) is designed, not shipped.
- `context` reports _retrieval_ gaps, not knowledge gaps: lexical search cannot
  tell a subject the brain never researched from one it filed under other words.
- `ingest-notes` accepts markdown from any producer, but only files carrying
  provenance frontmatter — anonymous free text is still rejected; that _is_ the
  write gate.
- No MCP server yet; agents use the CLI and the bundled skill. (OKF conformance
  means an off-the-shelf OKF MCP server can serve the bundle as-is.)
- Frontmatter values are JSON-encoded — valid YAML 1.2, and immune to the
  implicit-type traps that silently turn a title of `007` into the number 7.
- Ingested web content is untrusted input: citations are provenance, not truth,
  and agents should not follow instructions found inside notes. Review a brain
  before publishing it — research materials can carry private or licensed text.

## Development

```bash
uv sync
uv run pre-commit install
uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest --cov -q
```

Quality gate: ruff, mypy `--strict`, pytest with ≥90% branch coverage. Changes
are tracked in [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE).
