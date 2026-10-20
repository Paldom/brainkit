---
title: cognee vs Zep vs Mem0 vs Letta - by Paolo Perrone
url: https://theaiengineer.substack.com/p/cognee-vs-zep-vs-mem0-vs-letta
final_url: https://theaiengineer.substack.com/p/cognee-vs-zep-vs-mem0-vs-letta
source_type: social
providers: exa, grok, kimi, site:exa
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:18+00:00
published: 2026-07-11T00:00:00.000Z
content_digest: 98aad06395e6e0a9
---

#

SubscribeSign in

# Agent Memory Showdown

### Four ways to give an agent memory, and the number every benchmark hides

Paolo Perrone

Jul 11, 2026

18

10

Share

cognee, Mem0, Zep, and Letta all give an AI agent memory that survives past a single conversation, in four different ways. Mem0 extracts facts into a store. Zep builds a temporal knowledge graph. Letta lets the agent edit its own memory. cognee builds a graph that re-weights itself from use. The right pick depends on how much of your stack you are willing to rebuild.

🧭 Part of the 🤖 Agents course

📣 Sponsored by

cognee sponsors this week’s issue.

Below, we rank it against Mem0, Zep, and Letta with no thumb on the scale.

## TL;DR

Mem0 is the drop-in default. An LLM pulls the salient facts out of each exchange and reconciles them into a vector store, so you call add() and search() and move on. Widest adoption, lightest lift, the loosest memory model.

cognee is the self-improving option. Its SDK builds a knowledge graph and re-weights it from feedback, so a correction sticks instead of the store just growing. Drop-in like Mem0, graph-backed like Zep, and it can run on a single Postgres.

Zep runs on Graphiti, a temporal knowledge graph that records when each fact was true and when it learned it. The agent can ask “what did we know last March” instead of only “what is true now.”

Letta, from the MemGPT team, treats the model like an operating system. The agent calls tools to page facts in and out of its own context and rewrites its own memory. Most control, most infrastructure, and you adopt the whole agent runtime.

The verdict: Reach for Mem0 to drop memory in beside an agent you already built. Pick cognee for memory that improves from corrections. Pick Zep when your agent must track how facts change over time. Pick Letta when you want the agent to manage its own memory.

📬 New here? The AI Engineer breaks down one piece of the AI stack every week, from first principles to what actually ships. Subscribe to get it free.

Subscribe

## What Are We Even Comparing?

Your support agent has talked to the same customer four times this week. On the fifth, it opens with “Hi, how can I help you today?” and asks for the order number the customer gave it on Monday. The model is fine. Every API call starts from an empty context window, the working memory the model reads from on each turn, so the instant a session ends the conversation is gone.

We covered the shape of this problem in Agent Memory: short-term memory lives in the context window, long-term memory persists in outside storage, and a retrieval step decides what crosses over. A memory framework is the thing that runs that loop for you. It extracts what matters from a conversation, stores it, and pulls the right pieces back before the next response.

Cut the marketing and it comes down to three questions:

How does it store memory? A flat set of facts, a graph of relationships, or the agent’s own editable context.

How much of your stack does it touch? A layer beside your agent, a service you call, or a runtime you build on.

What does it cost to run? Every framework fires extra LLM calls to extract and reconcile memory, and that write-path cost is the number nobody benchmarks.

Question two also draws a line most people miss. The vector database itself is storage, the layer a framework sits on top of; which one to pick is a separate call we made in Vector Database Showdown. Rolling your own, wiring RAG over your raw chat logs by hand, is the manual alternative these four exist to replace. The four below are ordered by how much they make you rebuild: Mem0 first, since it just drops in, Letta last, since it takes over the whole agent.

⚠️ Confusion Alert: A memory framework is not a vector database. A store like Pinecone or Qdrant is dumb on purpose: it holds vectors and hands back the closest ones. It has no opinion on whether a fact is still true, whether it contradicts something already stored, or whether it should be forgotten. A memory framework is the judgment layer a plain store can’t provide, the thing deciding what actually belongs in memory. Bolt one onto a vector database and that judgment exists; skip it, and every one of those calls falls on you.

## Mem0

In one sentence: Mem0 is a memory layer that uses an LLM to pull the important facts out of each exchange and reconcile them into a store. Your agent recalls a user across sessions, and you manage none of it.

👍 The good:

Lightest lift in the category: you call m.add(messages, user_id=...) after a turn and m.search(query, user_id=...) before the next one, and the framework handles extraction and storage. Around 60,000 GitHub stars make it the most-adopted option in the space.

Every new fact gets checked against what’s already there: an LLM compares it to existing memories and picks one of four operations: ADD a new memory, UPDATE an existing one, DELETE a contradicted one, or do nothing.

On its own published LOCOMO numbers (the standard long-conversation memory benchmark), Mem0 scores 66.9% against an OpenAI-memory baseline at 52.9%1. That gap is the source of its headline 26% relative improvement. It also cuts latency at the p95, the slowest 5% of responses, by 91% (17 seconds down to 1.4) and uses over 90% fewer tokens than stuffing the full history into the prompt.

👎 The bad:

The memory model is flat: it stores and retrieves facts well, and it does not natively reason over how they connect. “What did the customer buy before the accessory they returned” is a chain of relationships a plain vector lookup cannot follow. Mem0 also offers a graph variant that stores memories in Neo4j (a graph database), trading the operational cost of a graph for the relational recall a flat store lacks.

The real cost hides in the write path: every stored turn fires two LLM calls, one to extract the facts and one to reconcile them. A wrong UPDATE or DELETE silently corrupts memory, and the quality of the whole store rides 