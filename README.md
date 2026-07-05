# brainkit

One portable brain for your agents and your team — a Git-native markdown knowledge base with hybrid retrieval, gated writes, and cited answers.

> [!NOTE]
> **Pre-release.** The implementation is complete and tested but has not landed in this repository yet — nothing here is installable until the first code drop. Everything below describes that release. Watch the repo to catch it.

brainkit turns a folder of plain markdown into long-term memory both your agents and your teammates can trust: ingested sources in `raw/`, curated concept pages in `wiki/`, rebuildable search indexes in `outputs/`. No database, no SaaS, no vector store you can't inspect — if you can read a diff, you can audit your agent's memory.

## Why brainkit

- **Your knowledge is plain text in Git.** Diff it, review it, grep it, roll it back. Humans and agents read the same pages.
- **It never calls an LLM.** Your agent is the intelligence; the brain is the substrate. No API key, no provider lock-in, no double-LLM bill.
- **Retrieval scales itself.** Plain grep → BM25 → hybrid vectors with rank fusion, auto-enabled around ~100 docs. Embeddings are local by default (external embedders are optional and egress-gated); every promotion is audited, and your own eval set holds the veto.
- **Agents propose, humans approve.** Enforced at brainkit's MCP/CLI surface: its tools never write `wiki/` directly — every change stages a reviewable proposal. A wrong page never silently becomes institutional truth.
- **Deletion actually cascades.** `brain purge` chases a source through every operator-controlled store and honestly reports what it could not reach (Git history, backups, provider retention).
- **Claude Code in one command.** `brain connect claude` wires up a five-tool MCP server plus a skill that teaches the agent the workflow. Codex and custom harnesses get the same contract.

## Quick start

Three commands, no API key:

```bash
pip install .            # from a clone of this repository (not yet on PyPI)
brain init my-brain
printf 'brainkit keeps agent knowledge in Git.\n' > note.txt && brain ingest note.txt --brain my-brain && brain query "what is this brain" --brain my-brain
```

Expected result: ranked, cited hits from your new brain in milliseconds.

`brain init` asks exactly one question — whether the brain will hold licensed, personal, or regulated content — and maps your answer to safe storage and egress settings. Pass `--yes` for the open defaults.

## Connect your agent

```bash
pip install ".[serve]"
brain connect claude --brain my-brain
# restart Claude Code, then run /mcp to verify the `brain` server is connected
```

The agent gets five MCP tools — `brain_search`, `brain_read`, `brain_apply`, `brain_lint`, `brain_log` — and one contract: search first, cite always, never edit `wiki/` directly, stage every change as a proposal a human approves. `brain connect codex` writes the same contract into your `AGENTS.md`; `brain connect generic` prints it for any other harness.

## Use it from Python

```python
from pathlib import Path

from brainkit import Bundle, BrainConfig, ingest_source, query

bundle = Bundle.init(Path("brain"), BrainConfig(name="docs"))
ingest_source(bundle, "notes.txt")
for hit in query(bundle, "how does rank fusion work").hits:
    print(hit.score, hit.path, hit.snippet)
```

The top-level exports are the supported public API; every result is a Pydantic model.

## How it works

```
 URL / file ->  raw/  --propose-->  .staging/proposals/  --approve-->  wiki/
                                      (the write gate)                 curated concepts
                                            |
                                            v
                 outputs/  (rebuildable projections — never truth)
                   rung 0: plain files — grep works as-is
                   rung 1: lexical BM25
                   rung 2: embeddings + reciprocal-rank fusion
                   rung 3: typed graph + as-of time travel
                   rung 4: YOUR agent's loop over the MCP/CLI surface
```

One default brain covers reference corpora, docs wikis, codebase notes, and team knowledge bases as-is. A handful of flags cover the edges: `--mode pointer_only` for licensed full text, `--storage private_local --egress local_only` for confidential notes, `--mode purgeable_regulated` for data someone may demand deleted, `--recency` for feeds.

## The ideas behind it

brainkit is a deliberate combination of three ideas:

- **[The Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)** (Google Cloud, 2026) is the bundle layout: knowledge as a folder of markdown with YAML frontmatter, an `index.md` navigation root, and a `log.md` journal. OKF standardizes the container; brainkit layers the meaning on top.
- **[Karpathy's LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** is the maintenance pattern: immutable raw sources, a curated wiki the model writes and refines, three verbs — ingest, query, lint. brainkit productizes it and adds the one thing the gist leaves out: the write gate.
- **[Hybrid RAG retrieval](https://www.infoq.com/articles/vector-search-hybrid-retrieval-rag/)** with [reciprocal-rank fusion (SIGIR 2009)](https://dl.acm.org/doi/10.1145/1571941.1572114) is the access pattern — minus the "G": brainkit retrieves and ranks, your agent generates.

Why combine them? The one [preregistered wiki-vs-RAG head-to-head](https://arxiv.org/abs/2605.18490) ended in a split verdict, not a winner. So brainkit refuses to pick a side: the wiki bundle is the representation layer (what knowledge *is*), the retrieval ladder is the access layer (how it's *found*).

## Honest edges

- No encryption at rest — `private_local` keeps content out of Git, nothing more; use disk encryption underneath.
- No scheduled ingest, no incremental indexing, no cross-trust federation.
- Single-operator concurrency model; the write gate guarantees review, not brilliance — page quality depends on the agent you attach.

## License

See [LICENSE](LICENSE).
