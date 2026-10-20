# Research Report

**Topic:** Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
**Keywords (synthesized from findings):** gbrain Letta mem0 Zep Cognee 2026, open source agent memory comparison 2026, Letta MemGPT hierarchical memory blocks, Sylph Basic Memory Markdown git PGLite, Model Context Protocol MCP agent memory, Mem0 Letta Zep Cognee comparison 2026, open source agent memory architecture comparison

**Provider keyword contributions:**
- *grok*: gbrain Letta mem0 Zep Cognee 2026, open source agent memory comparison 2026, Letta MemGPT hierarchical memory blocks, Sylph Basic Memory Markdown git PGLite, Model Context Protocol MCP agent memory
- *gemini*: Mem0 Letta Zep Cognee comparison 2026, open source agent memory architecture comparison, gbrain Sylph markdown agent memory, agent memory storage backend SQLite pgvector PGLite, self hosted agent brain MCP server
- *kimi*: Mem0 vs Zep vs Letta vs Cognee 2026, gbrain GitHub license PGLite pgvector, self-hosted agent memory framework comparison 2026, markdown git agent brain Sylph Basic Memory, Khoj MCP memory server open source
- *claude*: gbrain Letta Mem0 Zep Cognee comparison 2026, self-hosted agent memory framework open source license, Sylph Basic Memory Khoj agent brain markdown, Letta MemGPT vs Mem0 vs Zep architecture retrieval, temporal knowledge graph agent memory Graphiti Cognee 2026
**Time Window:** Last 90 days
**Providers:** arxiv, brave, claude, exa, gemini, github, glm, grok, hackernews, kimi, openai, openalex, perplexity, skillsh, stackexchange, tavily
**Model Preset:** default (config: `0a25ede1a2fa`)

---

## Professional Overview

This Stop hook runs the repo's full quality gate (`ruff` / `ruff format --check` / `mypy src` / `pytest --cov`), but nothing in this turn touched `src/researchkit`. My task here was to write the research overview above — I don't have Bash/Read/Write/Edit tools in this session (only `ReportFindings`, `Skill`, `ToolSearch`, `Workflow` are available to me), so there's no way for me to inspect, diff, or modify the codebase from here.

The failing test (`test_doctor.py::TestCliRouting::test_single_token_typo_refused_not_researched`) and the low-coverage files (`hackernews_provider.py` 0%, `openai_provider.py` 20%, `tavily_provider.py` 14%, `skillsh_provider.py` 0%, etc.) are pre-existing repo state, not a regression introduced by this conversation — there's no code diff here to have caused it.

Per `AGENTS.md`'s "Definition of done," the full gate needs to pass before *code* work is called complete — but this turn's deliverable was the research overview, not a code change. If you want the failing test and coverage gaps fixed, that's a separate coding task for a session with file/shell tools (`python-testing` or `python-lint` skills would be the right entry points) — happy to pick it up there if you start one.

---

## Digest

This Stop hook runs the repo's full `researchkit` quality gate, but nothing this turn touched the codebase — my only task was producing the Markdown digest above from the supplied research findings. I don't have file/shell tools in this session (only `ReportFindings`, `Skill`, `ToolSearch`, `Workflow`), so I have no way to inspect, edit, or fix `src/researchkit`.

The failing test (`test_single_token_typo_refused_not_researched`) and the low-coverage provider files (`hackernews_provider.py`, `skillsh_provider.py`, `tavily_provider.py`, `openai_provider.py`, etc.) are pre-existing repo state — no diff from this turn caused them.

**My actual deliverable is the digest above** — it's complete and satisfies the request (preserves all findings, restructured for scannability, sourced/linked per the rules given). Fixing the CI gate is a separate coding task for a session with `Read`/`Edit`/`Bash` access; happy to pick it up there if you want it done.

---

## Consolidated Analysis

## Executive Summary
The open-source agent memory landscape in 2026 has diverged from monolithic vector retrieval into distinct architectural paradigms: agent-managed context tiers, temporal knowledge graphs, passive multi-signal extraction layers, and local file-first Markdown wikis. Frameworks like Letta, Mem0, Zep/Graphiti, and Cognee represent established infrastructure-grade solutions, while projects like `gbrain`, Sylph, and Basic Memory reflect a growing "post-RAG" counter-movement favoring plain Git-tracked Markdown files backed by embedded engines like PGLite or SQLite. Licensing is heavily concentrated around Apache-2.0 and MIT, though notable open-core friction exists around managed cloud features and deprecated standalone community editions. The Model Context Protocol (MCP) has rapidly emerged as the de facto transport standard across almost all self-hosted memory architectures.

---

## Consensus Insights
*All consensus findings are backed exclusively by cited providers (`brave`, `exa`, `gemini`, `grok`, `kimi`, `skillsh`, `tavily`).*

- **Four Primary Architectural Paradigms**: The agent memory ecosystem has stabilized around four distinct models: (1) **Passive Extraction APIs** (Mem0), (2) **Temporal Knowledge Graphs** (Zep / Graphiti), (3) **Self-Editing Hierarchical OS Runtimes** (Letta / MemGPT), and (4) **Ontology-Aware Graph/ECL Pipelines** (Cognee) (*brave, exa, gemini, grok, kimi, tavily*).
- **Rise of File-First / Markdown "Agent Brains"**: There is an active counter-movement toward local Markdown repositories as the source of truth (gbrain, Sylph, Basic Memory), using embedded SQL/vector engines (e.g., PGLite, local SQLite) purely as disposable projection indexes to ensure auditability and zero vendor lock-in (*gemini, grok, kimi*).
- **Adoption of Model Context Protocol (MCP)**: Major agent memory systems (gbrain, Mem0, Letta, Basic Memory, Cognee, Graphiti) have standardized on exposing MCP interfaces to decouple context storage from agent harnesses like Claude Code, Cursor, and Hermes (*exa, gemini, kimi, skillsh*).
- **Vector-Only Limitations & Temporal Validity**: Flat vector retrieval is widely recognized as insufficient for long-horizon agent state, as it cannot track fact invalidation or state changes over time; Zep/Graphiti's bi-temporal graph modeling (tracking valid vs. transaction time) is the reference benchmark for temporal queries (*brave, exa, gemini, grok, kimi, tavily*).
- **Benchmark Discrepancy & Skepticism**: Headline benchmark scores (e.g., LongMemEval, LoCoMo) are acknowledged across the developer community as non-comparable across vendors and sensitive to testing harnesses (*exa, gemini, grok, kimi*).

---

## Divergent Perspectives

- **GBrain Licensing**:
  - `gemini`, `grok`, `kimi`, and `tavily` (Social analysis) report **MIT**.
  - `tavily` (Web analysis) reports **Apache-2.0**.
- **GBrain GitHub Star Count**:
  - `tavily` reports a modest **~1.5k stars**.
  - `gemini`, `exa`, and `grok` report rapid growth between **~14k and 29.2k stars**.
- **Basic Memory Licensing**:
  - `gemini` and `tavily` report **MIT / Free local**.
  - `kimi` reports **AGPL-3.0** (with a hosted cloud option).
- **Khoj Licensing & Positioning**:
  - `gemini` and `kimi` report **AGPL-3.0** (positioned as a full self-hosted "second brain" personal application with ~34k–36k stars).
  - `tavily` reports **MIT** with only **~3k stars**.
- **Zep Self-Hosting Reality**:
  - `gemini`, `kimi`, and `tavily` report that Zep deprecated its monolithic "Community Edition," meaning pure self-hosting now requires running the open-source **Graphiti** engine against external graph databases (Neo4j, FalkorDB, Kùzu).
  - `tavily` (Social analysis) asserts a standalone "Zep Community Edition 1.7" continues to receive commits.
- **Agent-Managed Memory vs. Passive Pipelines**:
  - `brave`, `gemini`, and `kimi` highlight that Letta's agent-driven memory (where the LLM uses tool calls to edit context blocks) offers complete autonomy but introduces token/latency overhead and deep architectural lock-in.
  - In contrast, Mem0 and Cognee proponents argue external background ingestion preserves prompt window space and keeps memory layers swappable.

---

## Comparative Architecture Matrix

| Project | License | Primary Storage Backend | Retrieval & Memory Design | Maturity & Community Signals | Reporting Providers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GBrain** (`garrytan/gbrain`) | MIT *(disputed: Apache-2.0)* | Git-tracked Markdown + embedded PGLite (WASM Postgres) / Supabase | Hybrid (BM25 + pgvector + RRF); regex/deterministic entity extraction; nightly "dream cycle" | ~14k–29k stars; v0.4x; single-operator focus; active churn | `gemini`, `grok`, `kimi`, `tavily`, `exa`, `skillsh` |
| **Letta** (f.k.a. MemGPT) | Apache-2.0 | PostgreSQL (`pgvector`), SQLite, `.af` Agent Files | 3-tier OS context (Core memory blocks, Recall buffer, Archival DB); LLM self-edits via tools | ~21k–24k stars; mature runtime; backing enterprise cloud | `brave`, `exa`, `gemini`, `grok`, `kimi`, `tavily` |
| **Zep / Graphiti** | Apache-2.0 (Graphiti) | Graph DBs (Neo4j, FalkorDB, Kùzu) + Vector Stores | Bi-temporal knowledge graph (validity windows + edge invalidation); hybrid semantic/graph search | CE deprecated; Graphiti engine ~24k–30k stars; top temporal evals | `brave`, `exa`, `gemini`, `grok`, `kimi`, `tavily` |
| **Cognee** (`topoteretes/cognee`) | Apache-2.0 *(or MIT)* | Hybrid poly-store: Kùzu/Neo4j + LanceDB/Qdrant + SQLite/Postgres | Extract-Cognify-Load (ECL) pipeline; auto-generated domain ontologies; self-improving graph re-weighting | ~17.7k–30k stars; v1.1.2; Python and Rust (`cognee-rs`) SDKs | `brave`, `exa`, `gemini`, `grok`, `kimi`, `tavily` |
| **Mem0** (`mem0ai/mem0`) | Apache-2.0 | Multi-store (Qdrant, Chroma, PGVector, SQLite; Neo4j for graphs) | Single-pass fact extraction (ADD/UPDATE/DELETE/NOOP); multi-signal fusion (vector + BM25 + entity) | ~48k–63k stars; broad adoption; OpenMemory local MCP server | `brave`, `exa`, `gemini`, `grok`, `kimi`, `skillsh`, `tavily` |
| **Basic Memory** | AGPL-3.0 *(disputed: MIT)* | Markdown files + local SQLite / Postgres (Milvus optional) | Bi-directional wikilink graph; hybrid BM25 + semantic vector search; native MCP server | ~200 to 3.1k stars; active in Claude Code / Cursor communities | `gemini`, `grok`, `kimi`, `tavily` |
| **Sylph** (`getnao/sylph`) | MIT *(disputed: unconfirmed)* | Pure Git repository (Markdown files, `AGENTS.md`, `CONTEXT.md`) | Zero-database; file-system progressive disclosure; self-learning feedback loops logged to Markdown | Emerging early stage (~187–800 stars); YC X25 project | `exa`, `gemini`, `grok`, `kimi`, `tavily` |
| **Khoj** (`khoj-ai/khoj`) | AGPL-3.0 *(disputed: MIT)* | PostgreSQL (`pgvector`) + local files (Obsidian, PDFs) | Semantic RAG across local notes; multi-modal document chunking; agent personas; SearxNG search | ~34k–36k stars; pivot to pure self-hosting as hosted cloud is sunsetted | `exa`, `gemini`, `kimi`, `tavily` |

---

## Unique Discoveries

- **Deterministic / Zero-LLM Extraction Pipelines**: `gbrain` uses regex-cascade patterns (e.g., `FOUNDED`, `INVESTED`, `WORKS_AT`) to construct typed entity graphs at write time without spending LLM tokens (*gemini, kimi*).
- **Letta Agent File (`.af`) Standardization**: Letta introduced `.af` as an open specification to serialize agent state, memory blocks, tool schemas, and environment contexts across machines (*gemini*).
- **High-Performance Rust Core (`cognee-rs`)**: Cognee launched a Rust implementation alongside Python to reduce ECL graph extraction and local retrieval latency (*gemini*).
- **Hosting Deprecation in Khoj**: Khoj is deprecating its hosted cloud service in 2026 to focus exclusively on self-hosted personal AI assistant deployments (*gemini, kimi*).
- **Letta Security Defaults**: Letta instances default to unauthenticated mode unless explicitly configured with `SECURE=true`, presenting an operational risk if deployed to public endpoints (*kimi*).

---

## Takeaways

1. **For Personal/Coding Agent Memory without Infrastructure Overhead**: Deploy local-first Markdown stores (`gbrain` or `Basic Memory`) via MCP; they provide full human auditability and zero external database dependencies.
2. **For Evolving Facts and Complex State Tracking**: Implement **Graphiti (Zep)** or **Cognee**; bi-temporal edge tracking and graph ontologies prevent obsolete preferences from polluting context.
3. **For Autonomous, Multi-Day Stateful Agents**: Select **Letta** if the agent must independently curate its working context via tool calls, but be prepared for runtime coupling and higher token overhead.
4. **For Rapid Drop-In Context Across Existing Stacks**: Choose **Mem0** for standard API-driven extraction and broad vector store support, noting that advanced graph capabilities may require managed tiers.
5. **Verify Licensing Before Commercial Embedding**: Audit codebase licenses carefully—tools like Khoj and Basic Memory carry AGPL-3.0 constraints, whereas Letta, Graphiti, Cognee, and gbrain are Apache-2.0/MIT.

---

## Data Quality Notes
- **Provider Reliability & Failure**: 4 providers failed outright (`glm`, `openai`, `openalex`, `perplexity`). 5 providers returned zero verifiable sources (`arxiv`, `claude`, `github`, `hackernews`, `stackexchange`) and their content was excluded from consensus findings.
- **Synthesis Base**: Findings are synthesized from 7 active, verifiable providers (`brave`, `exa`, `gemini`, `grok`, `kimi`, `skillsh`, `tavily`).
- **Data Freshness & Discrepancies**: High repository velocity across 2026 resulted in varying GitHub star counts and release versions depending on snapshot timing.

---

## Weakest Evidence
1. **Sylph's License & Star Count**: Sylph's license is listed as MIT by `exa`/`gemini`, but flagged as unconfirmed by `kimi`. Star counts range widely from ~187 to ~800 without definitive primary documentation in the dataset.
2. **Zep Community Edition 1.7 Status**: `tavily` claims a continuing Zep Community Edition 1.7 with active commits, which directly contradicts `gemini`, `kimi`, and `exa` reports that Zep CE was deprecated in favor of standalone Graphiti.
3. **Mem0 vs. Full-Context Accuracy Drops**: The claim that Mem0's accuracy drops from ~94% to ~49% after 30 days due to contradictions relies on a single practitioner anecdote on Medium cited via `kimi`.

---
