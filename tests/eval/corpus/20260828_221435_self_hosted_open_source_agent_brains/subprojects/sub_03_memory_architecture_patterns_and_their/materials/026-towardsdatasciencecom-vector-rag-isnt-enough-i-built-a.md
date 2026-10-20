---
title: Vector RAG Isn’t Enough — I Built a Context Graph Layer for Multi-Agent Memory | Towards Data Science
url: https://towardsdatascience.com/vector-rag-isnt-enough-i-built-a-context-graph-layer-for-multi-agent-memory/
final_url: https://towardsdatascience.com/vector-rag-isnt-enough-i-built-a-context-graph-layer-for-multi-agent-memory/
source_type: web
providers: brave, exa
topic: Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
fetched_at: 2026-08-28T20:52:11+00:00
published: 2026-06-26
content_digest: 3f0aa7139605c611
---

Toggle SearchToggle Mobile Navigation

Publish AI, ML & data-science insights to a global community of data professionals.

Sign inSubmit an Article

LatestEditor's PicksDeep DivesNewsletterWrite For TDS
LinkedInXToggle Search

Large Language Model

# Vector RAG Isn’t Enough — I Built a Context Graph Layer for Multi-Agent Memory

A structured context graph beat a flat chat dump and a vector-only RAG pipeline on the same multi-agent conversations — full working code, real benchmark numbers, zero API calls

Emmimal P Alexander
June 26, 202617 min read

Image by the author, generated with ChatGPT (DALL·E)

## TL;DR

I wasn't trying to build a new memory architecture. I was trying to understand why one agent kept forgetting decisions made by another. The benchmark came later.

Multi-agent systems lose cross-agent decisions because flat transcripts and vector search both have a structural blind spot — not just a noise problem.

A context graph stores facts as entities and relationships instead of text chunks, so it can answer questions that need two facts combined.

This is not a concept. Three memory architectures, five scripted scenarios, 18 graded queries, fully deterministic, zero LLM calls.

Context graph: 88.9% accuracy at 26.9 tokens/query. Raw history dump: 61.1% accuracy at 490.9 tokens/query. Vector-only RAG: 50.0% accuracy at 75.9 tokens/query.

I found two real bugs building this — stale-fact retrieval and an entity-matching gap. Both are in the article.

## The Problem That Made Me Build This

I built a three-agent pipeline that worked great for short tasks. But the moment the conversation dragged on and an agent needed to recall a past decision, the whole thing fell apart.

Here is exactly how it broke: Agent_Planner would decide the project should use PostgreSQL. Then, twenty turns of "sounds good" and "I'll get to it" would pass. Eventually, Agent_Reviewer would pipe up and ask what storage technology we were using. Even with the entire raw transcript sitting right there in the context window, the agent couldn't answer reliably.

I was running this pipeline locally as a side project for EmiTechLogic just to see how far I could push multi-agent coordination before it hit a wall. Turns out, it didn't take very long.

Initially, I assumed this was just a model limitation. It isn't. It is a memory architecture problem that usually triggers one of two massive headaches depending on how you try to fix it.

### The Alternative Fix: Vector Search and the Relational Trap

If you switch to vector search, you fix the noise problem but immediately create a different one. A vector store retrieves chunks that look similar to your query; it doesn't retrieve relationships between facts.

If a key decision lives in one chunk and a critical dependency note about that decision lives in another, a similarity search has no way to combine them—no matter how good your embedding model is.

Both approaches hit different structural ceilings. Instead of guessing which compromise was "good enough," I decided to measure them both.

### What This Problem Actually Is

To be clear about what this article is not: this isn't a token-compression problem, and it's not a staleness problem. It's a structural retrieval problem. Some questions can only be answered by combining two separately-stated facts, and neither a growing context window nor a vector index has a mechanism to do that. That is a completely different failure mode than the ones I've written about before, and it needed a different benchmark.

### The Test Setup

To test this, I built five deterministic scenarios containing 18 graded queries and ran all three memory architectures against the exact same conversations.

All the results below come from real runs of that benchmark using a localized setup:

Environment: Python 3.12, CPU-only (no GPU needed)

API Calls: Zero

Consistency: Reproduced identically across two separate machines

Code Repo: You can find the complete implementation and run the tests yourself here: https://github.com/Emmimal/context-graph-benchmark/

## What "Context Graph" Means Here

A flat memory store (whether it is a raw chat transcript or a vector index) treats every single turn as an independent unit of text. To retrieve something, you just find the unit that best matches your query.

A context graph changes the underlying structure entirely. It treats memory as distinct entities with typed relationships connecting them:

AuthModule -----> DEPENDS_ON -----> RateLimiter

Agent_Implementer -----> ASSIGNED_TO -----> AuthModule

Retrieval in this model means traversing these relationships instead of just matching keywords or semantic vectors.

That structural difference only matters for one specific class of questions: anything that requires you to combine two separately-stated facts.

Consider a question like: "Which team owns the component that depends on the service that X chose?"

There is no single answer chunk sitting anywhere in the raw conversation history. The answer does not exist as a block of text. It only exists as a path through multiple facts. A flat store cannot construct that path on the fly. A graph walks right through it.

## Who This Is For

This approach is worth building if you run multi-agent pipelines where one agent's decision must be correctly retrieved by a different agent many turns later. It is built for systems where questions routinely require combining two or more separately-stated facts, or any long-running agent conversation where the token cost of re-sending history is becoming a real line item.

You should skip it for single-agent, single-turn tasks because there is no cross-agent state to lose. Skip it if your queries are always single-fact lookups with no joins. Vector RAG gets you most of the accuracy there at a fraction of the engineering cost. Finally, skip it if your team has no tolerance for an extra moving part. A graph needs an extraction step (which is rule-based in this benchmark, 