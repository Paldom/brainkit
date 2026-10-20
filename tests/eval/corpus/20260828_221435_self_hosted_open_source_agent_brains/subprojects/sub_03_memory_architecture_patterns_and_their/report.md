# Research Report

**Topic:** Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
**Keywords (synthesized from findings):** agent memory benchmark Mem0 Zep Letta 2026, "context rot" "memory poisoning" agent long-term memory, file-based markdown vs GraphRAG agent memory architecture, "background consolidation" sleep-time agent memory token cost, hierarchical paged context stateful agent memory retrieval, knowledge graph memory system 10M nodes, context rot memory poisoning agents 2026

**Provider keyword contributions:**
- *gemini*: agent memory benchmark Mem0 Zep Letta 2026, "context rot" "memory poisoning" agent long-term memory, file-based markdown vs GraphRAG agent memory architecture, "background consolidation" sleep-time agent memory token cost, hierarchical paged context stateful agent memory retrieval
- *grok*: knowledge graph memory system 10M nodes, context rot memory poisoning agents 2026, vector RAG vs GraphRAG trade-offs, plain file git agent memory Markdown, background consolidation sleep-time compute agents
- *claude*: context rot lost-in-the-middle LLM benchmark 2026, vector RAG vs knowledge graph agent memory trade-offs, hierarchical paged context memory cost reduction, memory poisoning LLM agent security risk, plain-file git-based memory CLAUDE.md AGENTS.md vs vector database
- *kimi*: agent memory architecture trade-offs 2026, Mem0 Zep LongMemEval benchmark 2026, vector vs graph vs file memory, context rot memory poisoning mitigation, sleep-time compute memory consolidation
**Time Window:** Last 90 days
**Providers:** arxiv, brave, claude, exa, gemini, github, glm, grok, hackernews, kimi, openai, openalex, perplexity, skillsh, stackexchange, tavily
**Model Preset:** default (config: `0a25ede1a2fa`)

---

## Professional Overview

This hook feedback is from the researchkit repo's dev gate (ruff/mypy/pytest/coverage) — it's unrelated to the task I was just given, which was purely writing a research overview from provided text. I have no code tools available in this turn (no Bash/Edit/Write/Read), so there's nothing for me to fix here even if it were in scope.

The report I wrote above stands as the answer to the actual request. If the failing test (`test_single_token_typo_refused_not_researched`) or the coverage gaps in the listed provider files need fixing, that's a separate coding task requiring a session with dev tools loaded against the repo.

---

## Digest

The stop hook is checking the `researchkit` repo's code gate (`ruff`/`mypy`/`pytest --cov`), but this turn's task was pure text synthesis — turning the supplied research dump into a markdown digest. No files were read or written; I have no `Bash`/`Edit`/`Write` tool in this session to touch `src/researchkit/**` or `tests/**` even if I wanted to.

The failure (`test_single_token_typo_refused_not_researched`) plus the low-coverage providers (`hackernews_provider.py`, `skillsh_provider.py`, `stackexchange_provider.py` at 0%, etc.) is pre-existing repo state, unrelated to the digest I produced. Per AGENTS.md the full gate is the definition of done for *code* changes — this wasn't one.

If you want that test and coverage gap fixed, that's a separate coding task needing a session with dev tools loaded against the repo. The digest from my previous message stands as the deliverable for this request.

---

## Consolidated Analysis

## Executive Summary
Across the evaluated providers, agent memory architecture discourse has shifted from debate over context window expansion to engineering persistent, multi-tiered memory systems. Pure vector-based Retrieval-Augmented Generation (RAG) is broadly recognized as insufficient for stateful agents due to temporal blindness and inability to handle multi-hop relational reasoning. Instead, teams are converging on hybrid architectures that blend vector similarity, structured knowledge graphs, and background consolidation ("sleep-time dreaming") to prune stale data. At the same time, file-based stores (`CLAUDE.md`, Markdown vaults) have emerged as popular zero-dependency alternatives for developer workflows, while "context rot" and persistent memory poisoning are acknowledged as major production security and reliability threats.

---

## Consensus Insights

- **Pure Vector RAG is Insufficient for Stateful Reasoning**: Dense vector search retrieves semantic similarity rather than causality, chronological state changes, or multi-hop logic. It routinely fails on temporal updates and dynamic state tracking (*brave, exa, gemini, grok, kimi, perplexity, tavily*).
- **Knowledge Graphs (GraphRAG) Solve Multi-Hop/Temporal Gaps at Higher Ingestion Costs**: Knowledge graphs (e.g., Zep/Graphiti, Cognee, HippoRAG) significantly outperform flat vector stores on relational and multi-session reasoning, but impose substantial compute overhead during write-time entity extraction and graph construction (*brave, exa, gemini, grok, kimi, perplexity, tavily*).
- **Context Rot and Attention Degradation Limit Full-Context Windows**: As context windows expand, models experience "lost-in-the-middle" attention degradation, reduced instruction following, and hallucination spikes. This renders raw context stuffing less effective than structured, selective retrieval (*brave, exa, gemini, grok, kimi, perplexity, tavily*).
- **Background Consolidation ("Dreaming" / Sleep-Time Compute) is Becoming Standard**: Decoupling the write and extraction loops from the active hot path by running asynchronous reflection, deduplication, and memory pruning during agent idle time reduces latency and cuts context token costs (*brave, gemini, grok, kimi, perplexity, tavily*).
- **Plain-File / Git-Backed Memory (`MEMORY.md` / `CLAUDE.md`) Provides Auditability**: Markdown-based file storage offers human-inspectable, version-controlled, zero-infrastructure memory, though it hits a performance ceiling as document collections grow past hundreds of files without search indices (*brave, exa, gemini, grok, kimi, perplexity, tavily*).
- **Memory Poisoning (OWASP ASI06 / Sleeper Attacks) is a High-Impact Vulnerability**: Malicious or unverified data ingested into memory can persist indefinitely across sessions, steering downstream agent execution; existing prompt-injection guardrails transfer poorly to long-term memory poisoning (*brave, exa, gemini, grok, kimi, perplexity, tavily*).

---

## Divergent Perspectives

- **Knowledge Graphs vs. Plain Files/SQLite for Production Workloads**:
  - *brave, gemini, grok, kimi, perplexity* emphasize that Knowledge Graphs are necessary for enterprise-grade entity-relationship mapping and temporal accuracy.
  - *exa, gemini* cite evaluations and practitioner reports showing that simple Markdown files combined with intent-driven agent tools or local SQLite (`sqlite-vec`/FTS5) match GraphRAG performance on common coding and agent benchmarks at vastly lower cost and operational complexity.
- **Graph Construction Cost Trajectory**:
  - *grok, perplexity, tavily* report that KG build costs (LLM-based entity/triplet extraction) remain a major financial and latency bottleneck (often 5–10x typical RAG).
  - *exa, kimi* report that newer model efficiencies and architectures (e.g., LazyGraphRAG, cheaper extraction models) have collapsed extraction costs by roughly an order of magnitude, making periodic re-indexing accessible.
- **Memory Benchmark Interpretation (LOCOMO / LongMemEval)**:
  - *brave, tavily* present Mem0's LOCOMO benchmark figures as evidence that external selective retrieval reduces latency (1.44s vs. 17.12s) and cuts token usage by 90%.
  - *kimi* highlights counter-analyses (e.g., by Zep) showing that LOCOMO's conversations are short enough that a simple full-context baseline outperformed selective memory systems (72.9% vs. 68.4%), and that vendor benchmark numbers diverge widely from independent retests.

---

## Unique Discoveries

- **Classifier Context Rot in Safety Monitors**: Long transcripts degrade not just agent execution, but also the safety and monitoring classifiers inspecting agent actions, causing them to miss malicious behavior buried mid-transcript (*kimi*).
- **Prefix Cache Busting as a Hidden Cost of RAG**: Dynamic context injection with continuously changing retrieved chunks invalidates provider-level prompt prefix caching, whereas static/append-only memory structures enable 4–10x caching cost savings (*brave, exa*).
- **Spaced Repetition (FSRS) Algorithms for Memory Stores**: Direct application of cognitive spaced-repetition decay functions to agent memory allows facts to have an explicit retention half-life, ensuring unreinforced memories naturally decay (*gemini*).
- **Compaction as an Attack Surface**: Context compaction pipelines that summarize history without source filtering act as active write channels for memory poisoning (*kimi*).

---

## Takeaways

1. **Adopt Hybrid Retrieval by Default**: For complex agent workflows, layer dense vector search with lexical matching (BM25) and structured metadata/graphs rather than relying purely on vector embeddings.
2. **Shift Memory Maintenance Off the Hot Path**: Use asynchronous background workers ("dreaming"/consolidation loops) during agent idle periods to deduplicate records, compute graph linkages, and reconcile state without introducing turn latency.
3. **Use Markdown/Git Stores for Developer Workflows**: For small-to-medium project contexts (<200 files), use human-auditable, git-trackable Markdown hierarchies (`AGENTS.md`, `MEMORY.md`) before adopting dedicated vector or graph infrastructure.
4. **Implement Strict Write-Path Validation**: Treat memory ingestion as an untrusted boundary by attaching provenance tags, implementing confidence scoring, and validating inputs before promoting them to durable procedural memory.
5. **Mitigate Context Rot via Paging**: Keep active working context small and task-focused; utilize virtual paging or structured sub-agent context restoration rather than flooding the model window with full session histories.

---

## Data Quality Notes

- **Provider Availability**: `arxiv`, `claude`, `github`, `hackernews`, and `stackexchange` returned zero verifiable sources in this pipeline run and were treated as uncited. `glm`, `openai`, and `openalex` failed outright.
- **Vendor-Driven Metrics**: A substantial portion of empirical benchmark data (e.g., LOCOMO, LongMemEval scores) originates from memory engine vendors (Mem0, Zep, Feather DB, ByteRover) and exhibits significant variance when compared to outside replications.
- **Synthesized Base**: Findings reflect strong convergence among search-enabled providers (*brave, exa, gemini, grok, kimi, perplexity, tavily*).

---

## Weakest Evidence

1. **Specific Benchmark Accuracy Ceilings (e.g., "94.87% on LongMemEval" / "95.2% accuracy")**: These figures stem almost entirely from vendor self-reports with varying model backbones and configurations; independent retests have shown scores dropping by over 30–40 points on identical baselines.
2. **LazyGraphRAG Reducing Ingestion Cost to 0.1% of GraphRAG**: Reported by only a few industry roundup citations (*kimi*); requires independent cost auditing across diverse corpus sizes before being treated as an industry benchmark.
3. **"75% of Autonomous Multi-Agent Failures Stem from Semantic Drift"**: An exact statistical claim cited in practitioner surveys (*gemini*) that lacks broad, cross-study empirical verification across varied architectures.

---
