---
title: Open-Source Agent Memory: Mem0 vs Letta vs Zep Compared
url: https://www.digitalapplied.com/blog/open-source-agent-memory-mem0-letta-zep-compared
final_url: https://www.digitalapplied.com/blog/open-source-agent-memory-mem0-letta-zep-compared
source_type: social
providers: brave, exa, site:exa
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:07+00:00
published: 2026-08-04
content_digest: 4545e4e952041d74
---

ServicesAI ToolsBlogAboutContact

Log inStart engines

Home/

Blog/

AI Development/

Open-Source Agent Memory Compared

AI DevelopmentDecision Matrix17 min readPublished August 4, 2026

Three architectures ·Apache-2.0across the board · benchmark numbers thatdo not compare

# Open-Source Agent Memory:Mem0 vsLetta vsZep

Mem0, Letta and Zep are the three most-starred standalone open-source memory projects, and they make three incompatible bets on what remembering means: passive fact extraction, agent-curated tiers, and a temporal knowledge graph. This is the architecture, pricing and benchmark comparison — including why the published scores disagree with each other.

DA

Digital Applied Team

Senior strategists · Published Aug 4, 2026

PublishedAugust 4, 2026

Read time17 min

Sources17 primary and independent

Mem0
62.7k

mem0ai/mem0 · Apache-2.0

Zep / Graphiti
29.6k

getzep/graphiti · Apache-2.0

Letta
24.1k

letta-ai/letta · Apache-2.0

Mem0 LongMemEval spread
45.4pts

94.4 vendor-run vs 49.0 third-party

▼Same benchmark name

Table of contents

00Key takeaways

01Three bets on memory

02Mem0 · extraction

03Letta · tiered self-editing

04Zep · temporal graph

05The benchmark problem

06Pricing mechanics decoded

07What Apache-2.0 gets you

08RAG or a memory layer

09Conclusion

10FAQ

Open-source agent memory is the least standardised layer in the whole agent stack, and the three projects that dominate it — Mem0, Letta and Zep — do not even agree on what the layer is for. One treats memory as a background extraction pipeline. One treats it as a set of tiers the agent edits itself. One treats it as a temporal knowledge graph where facts expire rather than disappear. Picking between them is an architecture decision, not a feature comparison.

The comparison content that already exists mostly reprints each vendor’s own benchmark numbers side by side, as though a score produced by Mem0 on LoCoMo and a score produced by Zep on DMR were two entries in the same league table. They are not. Different benchmarks, different harnesses, different judge models, and in at least one case a 45.4-point gap between a vendor’s own figure and the one independent measurement of the same benchmark name.

This guide covers how each system actually stores and retrieves facts, what the published scores do and do not prove, how three incompatible pricing mechanics translate into real spend, what self-hosting each project genuinely involves, and the decision rule for when plain retrieval-augmented generation is still the better answer. Every figure below is attributed to whoever produced it.

Key takeaways

01
Three architectures, not three feature sets.Mem0 extracts candidate facts from each message pair and reconciles them against what it already holds. Letta gives the agent tiered memory it edits through tool calls. Zep writes a temporal knowledge graph where every fact carries a validity window.

02
Every headline score is vendor-run.Mem0 publishes its own LoCoMo and LongMemEval results, Zep publishes its own DMR results in its own paper, and Letta designed the leaderboard it is measured on. The one clearly independent figure found put Mem0 at 49.0 on LongMemEval against a self-reported 94.4.

03
The circulating LoCoMo numbers disagree with each other.A third-party comparison table reprints 83.2 for Letta and 68.5 for Mem0, while Mem0's own research page carries 92.5 at the time of writing. Both sets are shown below with their sources rather than one being quietly preferred.

04
Open source does not mean one system to run.Zep's self-contained Community Edition server is deprecated. The open path today is Graphiti plus a separate graph database — Neo4j, FalkorDB or Kuzu — which is a different operational shape from Mem0's SDK or Letta's server.

05
The pricing units are not comparable.Mem0 bills memory-add and retrieval requests, Letta bills model usage plus tool-execution seconds, and Zep bills credits by Episode byte size. Comparing the sticker prices without decoding the units gives you the wrong answer.

## 01 — Three BetsThree projects, threeincompatibleideas of memory.

Mem0, Letta (formerly MemGPT) and Zep’s Graphiti are the three most-starred, most-referenced standalone open-source agent-memory projects, and all three ship under Apache-2.0. That is where the similarity ends. If you want the underlying taxonomy first — vector stores versus graphs versus episodic recall — start with ouragent memory architectures breakdown; this post is the vendor-level decision. For where these projects sit in the wider ecosystem, theopen-source agent landscape mapcovers the neighbouring lanes.

Extraction
Mem0
Two phases: extract, then update

An LLM pulls candidate facts out of each new message pair, using the conversation summary plus recent messages for context. A second pass compares every candidate against existing memories by vector similarity and decides ADD, UPDATE, DELETE or NOOP. The application does not have to ask for any of it.

mem0ai/mem0 · Apache-2.0

Self-curation
Letta
Core · Recall · Archival

Memory modelled on computer architecture. Core Memory sits in context like RAM and the agent reads and writes it directly. Recall Memory is searchable conversation history, like a disk cache. Archival Memory is a vector-backed long-term store the agent queries through tool calls.

letta-ai/letta · Apache-2.0

Temporal graph
Zep/ Graphiti
valid_at / invalid_at edges

Every fact lands in a knowledge graph carrying a validity window. When new information contradicts something already stored, the old fact is invalidated rather than deleted — the history and the provenance of the correction both survive.

getzep/graphiti · Apache-2.0

#### GitHub stars · standalone open-source agent-memory projects
Source: GitHub REST API, read at the time of writing

Mem0mem0ai/mem0 · 7,315 forks · Python

62,736

Zep · Graphitigetzep/graphiti · 2,998 forks · the OSS core

29,642

Lettaletta-ai/letta · 2,569 forks · formerly MemG