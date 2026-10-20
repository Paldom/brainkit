---
title: Mem0 vs Letta vs Zep vs Cognee: Four Bets on What "Agent Memory" Actually Means — AI Blog
url: https://menuagentic.com/blogs/mem0-vs-letta-vs-zep-vs-cognee/
final_url: https://menuagentic.com/blogs/mem0-vs-letta-vs-zep-vs-cognee/
source_type: social
providers: brave
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:03+00:00
published: 2026-06-23
content_digest: 72596dc8b4df2d41
---

Skip to contentAgentic AI WikiMenuField GuideConceptsDeep-DivesPlaybooksOperationsAI BlogChangelogAbout
Search

×

EN中文

On this page

AI Blog / Mem0 vs Letta vs Zep vs Cognee: Four Bets on What "Agent Memory" Actually Means
Browse all AI Blog →
AI Blog

# Mem0 vs Letta vs Zep vs Cognee: Four Bets on What "Agent Memory" Actually Means

A 128K-token context window degrades past the first thousand tokens and vanishes the moment the session ends. The agent-memory infrastructure market crossed $6 billion in 2026 because "throw it all in the context" stopped being a strategy — and four frameworks now bet differently on what memory should rank, store, and forget.

Posted 2026-06-23·By Agentic AI Wiki·22 min read

agent-comparison

memory

infrastructure

agent-frameworks

A 128K-token context window degrades past the first thousand tokens and vanishes the moment the session ends. That single fact is what built a market: agent-memory infrastructure is now a real layer in the stack because "throw it all in the context" stopped scaling. Four frameworks have placed architecturally opposite bets on what to do instead — Mem0 leans on an extraction pipeline and multi-store fan-out, Letta productizes the MemGPT memory hierarchy as an agent-as-a-server, Zep stakes everything on a temporal knowledge graph called Graphiti, and Cognee builds an ontology-aware graph from anything you feed it. The pattern across all four: storage isn't the moat; ranking is. As of late June 2026, picking one is picking which retrieval shape your agent will live inside.

## At a glance

Four frameworks, four answers to the same question: what does an agent need to remember between turns, between sessions, and between users — and how is that memory ranked when the next prompt arrives. The table sets the basics; the chart and matrix that follow show where each one leans hardest.

FrameworkApproachSelf-hosted?Headline strength

Mem0Extraction pipeline fanning extracted facts into vector + KV + graph storesYes — Apache-2.0 OSS, plus a managed cloudUser-scoped memory by default; drop-in for chat apps

Letta (formerly MemGPT)Agent-as-a-server with a tiered working/archival memory hierarchyYes — self-hosted server, plus Letta CloudStateful agents you address by ID across processes

ZepTemporal knowledge graph (Graphiti) with bi-temporal fact validityCommunity edition self-hosted; managed Zep CloudTime-aware retrieval — facts know when they stopped being true

CogneeGraph-from-anything ETL pipeline producing an ontology-aware knowledge graphYes — Apache-2.0 OSS, BYO graph + vector DBSchema-disciplined graph built from unstructured corpora

Snapshot: 2026-06-23. Star counts and feature surfaces in this space move fast — re-check each project's repo and docs before sizing a deployment.
GitHub stars at writing — a rough proxy for community surface area, not for production fit. Mem0's lead reflects its drop-in chat-app positioning; Cognee's smaller number reflects how recent the project is.Where each framework leans hardest. The axes diverge most on temporal awareness and graph reasoning — the two places "memory" stops looking like a vector DB.

## Mem0
Mem0 turns conversation into discrete extracted facts, then fans them out across three stores so retrieval can rank by similarity, lookup, and relationship at the same time.

### Extraction pipeline

The defining choice in Mem0 is what gets persisted: not the conversation, but the facts the conversation produced. When a message arrives, an LLM extraction step pulls out atomic claims — "user prefers vegetarian food", "user lives in Berlin", "user's daughter is allergic to peanuts" — and writes those, not the underlying turns. The agent's memory grows as a deduplicated set of statements, not a growing transcript. The trade-off is upfront: every write incurs an extra LLM call to do the extraction, which is real money at high message volume. The payoff is that retrieval never has to wade through chatter to find the signal.

### Multi-store retrieval (vector + KV + graph)

Each extracted fact fans out into three backends in parallel. The vector store indexes the fact's embedding for similarity search; the key-value store keeps it for exact lookup on canonical keys; the graph store records relationships between entities so a query can traverse user → child → allergies. At query time, all three return candidates and Mem0 merges them — vector gives you fuzzy recall on phrasing, KV gives you the precise answer to a structured question, graph gives you the reasoning path between entities. The reason to bother with three stores is that no single one ranks well for all three retrieval shapes: vector misses exact keys, KV misses paraphrase, graph misses the unstructured edges. Hybrid here isn't a feature — it's the architecture.

### User-scoped memory by default

Every memory in Mem0 is tagged with a user_id (and optionally a session_id and agent_id) as a first-class primitive of the API. You don't build the multi-tenant story on top of Mem0; it is the multi-tenant story. For a consumer agent serving thousands of users — a chat app, a coaching bot, a personalized assistant — that scoping model is the path of least resistance: every memory operation is automatically isolated to the right user without your code threading tenant IDs through every call. The cost is that workloads which don't fit a per-user shape (a single agent reasoning over a shared corpus) push against the grain of the API.

## Letta (formerly MemGPT)

### Agent-as-a-server architecture

Letta inverts the question most memory libraries answer. The other three frameworks ship a memory backend you call from your agent code. Letta ships the agent itself as a long-lived server-side resource you address by ID. You don't instantiate an agent in your process and worry about persisting its state across requests — you create an agent in the Letta server, hand back the ID, and every subsequent call (over HTTP, the SDK, or MCP) resumes the same