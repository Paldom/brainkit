---
title: LLM Knowledge Bases: Karpathy's Self-Improving Second Brain
url: https://lmmarketcap.com/reports/llm-knowledge-bases-karpathy
final_url: https://lmmarketcap.com/reports/llm-knowledge-bases-karpathy
source_type: web
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:31+00:00
published: 2026-04-03
content_digest: 9aeb36a268d1e7d9
---

Skip to content

LMC Feed-Models, Papers, Benchmarks. Zero Fluff.Live

LMMarketCap.comLMMC

Discover

Pricing

Compare

Tools

Developers

Monitor

More

⌘K

EN

Menu

⌘K

Home

AI News

Overview

Compare

Benchmarks

Search

Lifecycle

Discover

Trending

New Models

AI Trends

Providers

Explorers

Coding Models

Image Models

Video Models

Pricing

Pricing Table

Cheapest Models

Free Models

Cost Calculator

Token Counter

Pricing History

Subscription Calc

OpenAI Plans

Anthropic Plans

API Pricing Table

Embedding Models

Fine-tuning Pricing

Compare & Benchmarks

Compare Models

Popular Matchups

Provider vs Provider

Best for Coding

Best for Math

Best for Reasoning

Best for Instructions

Recommendation

Custom Rankings

Tools & Directory

Best for Cursor

Best for Claude Code

Best for Copilot

Best for Windsurf

Best for Aider

OpenAI Endpoints

Anthropic Endpoints

Google Endpoints

Coding Assistants

Agent Frameworks

Local LLM Runners

LLM Observability

VRAM Calculator

Monitor

Watchlist

Rank Changes

Price Changes

Service Status

All Trackers

Value Tracker

Stability Tracker

Pricing Trends

Weekly Reports

Modalities & More

Image Generation

Video Generation

Audio & Speech

Methodology

AI Glossary

Reports

EN

AI Model Rankings

Reports

LLM Knowledge Bases: Karpathy's Self-Improving Second Brain

Guide
April 3, 202612 min read

# LLM Knowledge Bases: Karpathy's Self-Improving Second Brain

Andrej Karpathy shared his workflow for building personal knowledge bases with LLMs - no RAG needed. We break down the architecture, explain why it works, identify the best models for each step, and show how to build your own.

On April 2, 2026, Andrej Karpathy - co-founder of OpenAI, former Tesla AI lead, and one of the most influential voices in machine learning - shared a workflow that quietly redefines how we should think about personal knowledge management. His approach: use LLMs not as chatbots, but as compilers that transform raw information into structured, queryable knowledge bases.

The key insight that makes the community sit up: no RAG needed. No vector databases, no embedding pipelines, no retrieval infrastructure. Just raw files, an LLM with a large enough context window, and markdown. The entire compiled knowledge base fits in context for modern long-context models - making the whole RAG stack unnecessary for personal-scale knowledge management.

This is not a theoretical exercise. Karpathy is actively using this system for his own work, and the architecture he describes maps directly onto tools and models available today. Below, we break down every component of his workflow, explain the technical reasoning behind each design decision, identify thebest models for each step, and show exactly how to build your own.

335

128K+ Context Models

available today

181

1M+ Context Models

full-codebase scale

10

Free Models

zero cost

350

Coding Models Tracked

live rankings

## Karpathy's Architecture: The Six-Stage Pipeline

Karpathy's system is not a single tool - it is asix-stage pipeline where each stage serves a distinct purpose. Understanding the architecture requires understanding what each stage does, why it exists, and what model capabilities it demands.

1

### raw/ - The Ingestion Layer

A flat directory where you dump source materials in any format: PDFs, HTML pages, API docs, research papers, tweets, code snippets, transcripts. No preprocessing required - the LLM handles format normalization in the next stage. Karpathy treats this as a "read-later queue on steroids" where the barrier to adding information is zero. The key design principle: capture first, organize later. You do not curate at ingestion time because curation is exactly what the LLM is better at.

2

### LLM Compilation - The Intelligence Layer

This is the core innovation. An LLM reads every document in raw/ and compiles them into structured markdown files organized by topic. Not summarization - compilation. The distinction matters: summarization loses detail, while compilation restructures information into a consistent format that preserves key details while adding cross-references, resolving contradictions between sources, and establishing a coherent ontology. The LLM acts as a knowledge compiler, analogous to how a C compiler transforms source code into machine code - different representation, same semantics.

Each compiled markdown page covers one topic and includes: a summary, key facts, source attribution, related topics (as wiki links), open questions, and areas where sources disagree. The LLM decides the taxonomy - you do not predefine categories.

3

### Obsidian IDE - The Visualization Layer

The compiled markdown wiki is opened in Obsidian (or any markdown editor with backlink support). This turns the flat files into a navigable knowledge graph. Obsidian's graph view shows topic connections. Its backlinks panel shows which pages reference the current topic. You can browse and edit the wiki manually, but the primary interaction mode is through the LLM in the next stage. Karpathy emphasizes that the human reads the wiki, but the LLM writes it.

4

### Q&A Against Wiki - The Query Layer

Instead of searching your knowledge base with keywords (grep, Ctrl+F), you ask it questions in natural language. The entire compiled wiki is passed as context to an LLM, and you query it conversationally. "What do the sources say about X?" "What are the open disagreements about Y?" "How does Z relate to W?" Because the wiki is already compiled and structured, the LLM can answer with high accuracy and cite specific source pages. This is where the no-RAG claim becomes concrete: if your compiled wiki fits in the model's context window, you do not need retrieval at all. You getperfect recall over your entire knowledge base.

5

### Output Filing - The Learning Loop

When the Q&A session produces new insights, synthesized conclusions, or identified gaps, those outputs are filed back into the wiki. T