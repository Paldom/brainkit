---
title: Graph-Based Agent Memory: A Complete Guide to Structure, Retrieval, and Evolution | by Shibui Yusuke | Medium
url: https://shibuiyusuke.medium.com/graph-based-agent-memory-a-complete-guide-to-structure-retrieval-and-evolution-6f91637ad078
final_url: https://shibuiyusuke.medium.com/graph-based-agent-memory-a-complete-guide-to-structure-retrieval-and-evolution-6f91637ad078
source_type: social
providers: brave
topic: Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
fetched_at: 2026-08-28T20:52:08+00:00
published: 2026-02-23
content_digest: 11f9ace9975a3101
---

Sitemap

Open in app

Sign up

Sign in

Get app

Write

Search

Sign up

Sign in

The Limits of Conventional Agent Memory

Text-Based Memory

Key-Value Stores

What Graphs Solve

Taxonomy of Graph-Based Agent Memory

By Temporal Scope

By Content Type

By Structure

Five Graph Structure Patterns

1. Knowledge Graph

2. Hierarchical Graph (DAG)

3. Temporal Graph

4. Hypergraph

5. Hybrid Graph

MAGMA: Separating Relationships with Multiple Graphs

Four Graph Layers

Dual-Stream Memory Evolution

Adaptive Traversal Policy

Benchmark Results

Designing the Memory Lifecycle

Extraction

Storage

Retrieval

Evolution

Three Retrieval Paradigms

Semantic Retrieval

Structured Retrieval

Policy-Based Retrieval

Memory Evolution Mechanisms

Internal Self-Evolving

External Self-Exploration

Real-World Application: The DeepImageSearch Case Study

Memory Graph Structure

Dual Memory System

The ImageSeeker Agent

Getting Started: Libraries and Benchmarks

Key Open-Source Libraries

Choosing Benchmarks

Key Takeaways

## Shibui Yusuke

R&D, data, search, cloud, ML, AI, and AR. https://x.com/cv_usk I write my own idea, and do not represent any organization. Apologies if anything wrong.

AI Agent

Agent Memory

Knowledge Graph

Agentic Ai

AI

# Graph-Based Agent Memory: A Complete Guide to Structure, Retrieval, and Evolution

Shibui Yusuke

14 min read
·
Feb 23, 2026

--

1

Listen

Share

Press enter or click to view image in full size

Design patterns for giving AI agents long-term memory that actually reasons

LLM-powered AI agents can generate code, hold conversations, and make decisions. Yet they struggle to retain and leverage past experience over time because of context window limits.

Graph-based memory is a compelling answer to this problem. It represents entities and their relationships as nodes and edges, preserving causal chains and temporal context that flat text retrieval loses.

This article draws primarily on the survey paper “A Survey on Graph-based Agentic Memory” (arXiv:2602.05665), supplemented by two concrete architectures: MAGMA (arXiv:2601.03236) and DeepImageSearch (arXiv:2602.10809). Together, they paint a comprehensive picture of how to design memory for intelligent agents.

What you will learn:

A taxonomy of agent memory and the design decisions it implies

Five graph structure patterns, their strengths, and trade-offs

The full memory lifecycle: extraction, storage, retrieval, and evolution

How MAGMA and DeepImageSearch implement these ideas in practice

Which open-source libraries and benchmarks to start with

## The Limits of Conventional Agent Memory

Before diving into graphs, it helps to understand why simpler approaches fall short.

## Text-Based Memory

The most straightforward approach stores past conversations and documents as text chunks, computes vector embeddings, and retrieves by similarity (RAG).

This has several limitations:

Lost relationships — Causal and dependency links between entities cannot be expressed in flat text

No temporal ordering — The order and timing of when information was learned is discarded

Redundancy and contradiction — The same fact stored in different phrasings can drift into inconsistency

Difficult multi-hop reasoning — Combining multiple facts into a chain of inference requires extra scaffolding

## Key-Value Stores

Structured key-value formats offer fast lookup but provide no way to express relationships between keys. You can store “User A prefers Python” and “User A works on data analysis” separately, but integrating these two facts for inference requires additional logic.

## What Graphs Solve

Graph-based memory addresses these limits structurally:
+-----------+ relationship +-----------+

| Entity | ───────────────> | Entity |

+-----------+ +-----------+

| |

| attribute temporal |

v v

+-----------+ +-----------+

| Property | | Event |

+-----------+ +-----------+

|

causal |

v

+-----------+

| Outcome |

+-----------+
Nodes represent entities and concepts. Edges represent their relationships. This enables:

Explicit relationships — “A depends on B” and “C caused D” are directly represented as edges

Temporal ordering — Timestamped edges preserve the chronological sequence of information

Contradiction detection — Conflicting facts about the same entity surface naturally on the graph

Multi-hop reasoning — Graph traversal chains multiple facts together without extra scaffolding

## Taxonomy of Graph-Based Agent Memory

The survey organizes agent memory along three axes. Understanding this taxonomy is the starting point for any memory system design.

## By Temporal Scope

Memory falls into three categories based on how long it persists:

Sensory memory — Lasts seconds. Buffers the most recent inputs (current prompt, latest API response)

Short-term memory — Lasts for the duration of a task. Holds working state (conversation history, scratchpads)

Long-term memory — Persists indefinitely. Accumulates knowledge and experience (knowledge graphs, user profiles)

Like the human memory model, information is selectively transferred from sensory to short-term, and from short-term to long-term. Graph-based memory primarily serves long-term storage, but its integration with short-term memory is equally important.

## By Content Type

What goes into memory splits into two broad categories:

Knowledge memory holds declarative facts and concepts — “Python is a dynamically typed language,” “Kubernetes is a container orchestration tool.” These are typically structured as knowledge graphs with is-a and has-a relationships.

Experience memory holds procedural knowledge and action histories — “This error was resolved with procedure X,” “The user prefers response format Y.” These are structured as temporal or episodic graphs.

## By Structure

Memory structures divide into unstructured and structured:
Memory Structure

/ \

Unstructured Structured

/ \ / \

Natural Parametric Database Graph

Language (NN weights) (SQL,KVS) (KG, Te