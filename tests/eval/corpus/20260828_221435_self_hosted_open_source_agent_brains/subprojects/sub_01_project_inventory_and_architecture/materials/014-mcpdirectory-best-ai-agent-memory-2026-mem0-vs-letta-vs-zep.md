---
title: Best AI Agent Memory 2026: Mem0 vs Letta vs Zep vs Cognee — MCP.Directory
url: https://mcp.directory/blog/mem0-vs-letta-vs-zep-vs-cognee-2026
final_url: https://mcp.directory/blog/mem0-vs-letta-vs-zep-vs-cognee-2026
source_type: social
providers: brave
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:10+00:00
published: 2026-05-11
content_digest: 01258aa2370c6610
---

MCP.directory
Servers

Skills
ClientsToolsBlogPartners

Submit Server

All posts
On this page

TL;DR + decision tree

What 'agent memory' actually means

Three memory architectures

Side-by-side matrix

Mem0 — install + recipe

Letta — install + recipe

Zep — install + recipe

Cognee — install + recipe

Pick your shape: when memory ≠ vector DB

Common pitfalls

Community signal

FAQ

Sources

Blog

Updated May 2026Comparison22 min read

# Best AI Agent Memory 2026: Mem0 vs Letta vs Zep vs Cognee

Best AI agent memory in 2026 means keeping an agent coherent over weeks, not turns — and the four serious frameworks do this in four genuinely different ways. Mem0 is a memory layer you bolt onto an existing agent. Letta is a runtime where the agentis its memory. Zep builds a temporal knowledge graph from conversation. Cognee builds a knowledge graph from everything else. We pulled architecture details from every repo, then mapped each one to the canonical agent use cases — so you can pick by problem shape, not vendor marketing.

On this page · 13 sections▾
TL;DR + decision tree

What 'agent memory' actually means

Three memory architectures

Side-by-side matrix

Mem0 — install + recipe

Letta — install + recipe

Zep — install + recipe

Cognee — install + recipe

Pick your shape: when memory ≠ vector DB

Common pitfalls

Community signal

FAQ

Sources

## TL;DR + decision tree

If you want the fastest path from zero to working memory on an existing agent — five lines of Python, hosted or self-hosted, with a clean SDK — pickMem0. It’s a memory layer, not a framework. Drop it in.

If memory is the architecture — you want stateful agents you address as services, each with a self-edited core scratchpad plus a giant archival store — pickLetta. The MemGPT lineage makes the memory hierarchy the framework’s reason to exist.

If your agent is conversational and the value is “remember what was true about this user as of last Tuesday” — chronological recall, fact extraction, temporal validity — pickZep. The temporal knowledge graph (Graphiti underneath) is the product.

If your memory problem is shaped like a graph— documents, entities, relationships, codebases, organisation charts — pickCognee. It’s closer to graph-RAG than to chat memory, and the remember / recall / forget / improve pipeline reflects that.

These four overlap less than the marketing surfaces suggest. Mem0 and Zep both call themselves “memory for AI agents,” but Mem0 optimises for stable user-preference recall while Zep optimises for chronologically correct fact lookup. Letta and Mem0 both let you persist agent state, but Letta hosts the agent itself while Mem0 is a library you call from your own runtime. Cognee shares an Apache 2.0 license and a Python-first SDK with all three but lives closer to Neo4j + LLM than to a memory layer in the chat sense. Read the architectures section before you write any code — the wrong choice early costs a refactor that’s harder than picking a database.

## What “agent memory” actually means

The word “memory” gets stretched to cover at least five different things in agent-land. Separate them before comparing frameworks — most arguments about which is best are really arguments about which kind of memory matters for the problem at hand.

Short-term / context-window memory is what the model already has: the prompt plus the last N turns. No framework solves this; it’s a property of the model and the orchestration layer. Token budget, attention degradation, and per-call cost are all in play. Everything below is about externalising state so the model doesn’t hold it all in context every turn.

Long-term / persistent memory is the generic name for anything written to a store that survives between sessions. All four frameworks here are solutions for it; they differ in what they think long-term memory should contain.

Episodic memory records specific things that happened — “on Tuesday the user said the checkout flow was broken, on Wednesday support marked it resolved.” Zep is the framework most obviously designed for this shape: every fact has a valid_at andinvalid_at timestamp so you can ask “was this true on Wednesday morning?” without the model hallucinating. Mem0 stores facts but doesn’t index them temporally as a first-class concern; Letta approximates episodic recall through archival search.

Semantic memory is timeless factual knowledge — “the user prefers metric units,” “HQ is in Amsterdam.” Mem0’s sweet spot. The April 2026 algorithm update reported 91.6 on LoCoMo (a long-conversation recall benchmark), so the team is optimising hard for this shape. Letta’s core-memory blocks are primarily semantic too — facts the agent has learned and edits as the relationship evolves.

Procedural memory — “how to do something” — is the least well-served by any of the four. You’ll mostly handle it yourself by storing tool-call sequences or successful workflows. Letta gets closest, since an agent can self-edit a memory block titled “how I solve refund disputes” and the next session inherits it.

Cognee sits across all of these by being a graph layer rather than a memory layer in the chat sense. Primitives are nodes, edges, and the cognify pipeline that builds them from unstructured input. If your “memory” is really “a corpus of documents the agent traverses by relationship,” Cognee fits even though the chat-memory vocabulary barely applies.

## Three memory architectures

Strip the surface APIs and the four frameworks reduce to three architectural patterns. Knowing which matches your workload is more useful than any benchmark.

### Architecture 1 — vector index + extraction (Mem0)

The cleanest vector-first pattern. New messages arrive, an extraction step pulls out atomic facts, each fact gets embedded and stored with structured metadata (user_id, agent_id, session, timestamp). Retrieval fuses semantic similarity, BM25, and entity match into one ranked list. Mental model: structured notes with a vector index for fuzzy lo