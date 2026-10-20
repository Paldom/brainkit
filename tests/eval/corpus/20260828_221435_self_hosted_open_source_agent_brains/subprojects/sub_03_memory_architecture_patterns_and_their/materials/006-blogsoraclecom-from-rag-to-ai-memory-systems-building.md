---
title: From RAG to AI Memory Systems: Building Stateful Architectures for Durable, Context-Aware Agents
url: https://blogs.oracle.com/developers/from-rag-to-memory-systems-building-stateful-ai-architecture
final_url: https://blogs.oracle.com/developers/from-rag-to-memory-systems-building-stateful-ai-architecture
source_type: social
providers: brave, site:exa
topic: Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
fetched_at: 2026-08-28T20:51:56+00:00
content_kind: summary
published: 2026-06-04
content_digest: 310c29ad4f8effa3
---

## TL;DR
- Summary:

The article analyzes memory architecture patterns for stateful AI agents and their trade-offs across retrieval quality, cost, and failure modes. Key points:

- Two common patterns for memory:
  - Middle pattern: split between durable memory and conversation/history traces. Examples include LangGraph (BaseStore + checkpointer) and Letta (core memory, recall memory, archival memory). Oracle’s AI Agent Memory SDK ships with three primitives (users/agents, memories, threads) and separate storage for threads, messages, memory records, and actor profiles. Traces are append-only and high-volume; they are best kept separate from durable memory to avoid bloat.
  - One-table-per-memory-type (recommended in the article): stores per-memory-type rules in the schema itself (per-type retention, per-type indexes, per-type access patterns). This enables enforceable policies without extra application logic. Moving from the middle pattern to this one is incremental, often starting with separating traces and then splitting policy/preference from fact/episodic memory.

- Practical considerations:
  - Memory is more than retrieval: a single query should enforce policy, user preferences, access controls, and semantic ranking within one transactional boundary and security model.
  - Token use and context length: more tokens can degrade model performance (context rot, attention dilution). Avoid “everything everywhere” as default.
  - Data isolation and retrieval: queries should filter by scope (e.g., cross-tenant data invisibility) and avoid embedding-based drift that can misalign policy.

- Converged/hybrid approach:
  - A converged platform aims to co-locate hybrid retrieval with relational data to satisfy policy, preferences, access control, and semantic ranking in one query plan. Purely separate stores (Postgres for relational data, vector stores for similarity, blob storage for large docs) can cause costly cross-store joins when context must cross boundaries.
  - Still valuable to use specialized stores for certain data (high-volume traces, large documents) but the goal is to minimize the expensive cross-store joins between governed data and semantic data.

- Practical guidance:
  - Start with a middle pattern, then move toward a one-table-per-memory-type design to hard-code rules and retention per memory type.
  - Prefer consolidated retrieval that enforces policy and access controls in a single query.
  - Be mindful of memory poisoning and false positives from drift in policy retrieval; avoid embeddings as the sole mechanism for critical policy enforcement.

If you want, I can tailor these patterns to your target architecture (e.g., PostgreSQL + vector store vs. fully converged memory) and compare estimated costs and risk factors.
- Multi-turn continuity. The system has no memory of what was just said unless you re-stuff the transcript every turn. Stuff it and you pay tokens and lose model quality to context rot. Skip it and the agent forgets what the user asked three messages ago. Retrieval alone won’t fix this.
...
The middle pattern splits by access pattern. The most common shape is two stores: one for durable memory and a separate store for conversation history or traces. LangGraph does this at the framework level(BaseStore for cross-thread memory, checkpointer for thread-local conversation state). Letta splits further into core memory (in-context blocks), recall memory (conversation history), and archival memory (durable facts in a vector store). Oracle’s AI Agent Memory SDK lands here too: its public API exposes three primitives (users and agents, memories, threads), with the underlying storage split across distinct tables for threads, messages, memory records, and actor profiles. The reasoning is consistent across these systems. Traces are append-only, high-volume, and queried by run_id for replay. They share almost nothing at the storage layer with durable memory. Letting traces grow inside the same table as facts means heavy trace writes bloat the working set for every other query.
...
The third pattern is one table per memory type, the model this article describes. The cost is real: more DDL, more places to touch when something cross-cutting changes, more conceptual surface area for someone new to the codebase. The payoff is that the rules each type follows live in the schema itself. Per-type retention, per-type indexes (no wasted vector index on policy or preference), and per-type access patterns become enforceable without application code having to remember them. The shift from the middle pattern to this one is incremental: you’re already splitting traces out, now you split policy and preference out from fact and episodic for the same reason.
...
More tokens often make the model worse. Lost-in-the-middle, attention dilution, and context rot all show up in production at long context lengths. The default instinct to give the model everything is the default wrong answer.
...
A couple of things to call out. The query filters by scope before doing anything else, so cross-tenant data is structurally invisible. And there’s no embedding involved anywhere in the path. Policy retrieval that uses similarity drifts silently away from the rule that’s actually in force, which is one of the worst failure modes in this space.
...
, and a recent-trace summary fan out in parallel, either across stores, or as a single unified retrieval query when the data is co-located in one
...
The accidental architecture most teams arrive at splits the memory layer along the axis that hurts most. Relational data goes in Postgres. Hybrid retrieval goes in Elasticsearch, OpenSearch, or a dedicated vector store. Traces end up in S3 or a time-series database. Each of these is a strong choice for the job it was built for, and many production stacks use them well. The problem is what happens when context has to cross between them.
...
Memory is more than retrieval. The capability that actually matters is hybri