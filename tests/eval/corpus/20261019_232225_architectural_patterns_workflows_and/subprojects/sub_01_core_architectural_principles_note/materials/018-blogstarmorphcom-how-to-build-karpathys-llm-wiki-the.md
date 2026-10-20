---
title: How to Build Karpathy's LLM Wiki: The Complete Guide to AI-Maintained Knowledge Bases
url: https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide
final_url: https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide
source_type: social
providers: brave, kimi
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:30+00:00
published: 2026-04-09
content_digest: 95dd1b11d5d64b76
---

Starmorpharticlestopicsmermaideditor.io↗starmorph↗YouTube
Dark

Published onThursday, April 9, 202619 min read

# How to Build Karpathy's LLM Wiki: The Complete Guide to AI-Maintained Knowledge Bases

Authors
NameDylan BoudroTwitterhttps://x.com/StarmorphAI

TL;DR: Andrej Karpathy's LLM Wiki is a pattern — not a product — where an LLM agent builds and maintains a structured markdown knowledge base from your raw sources. Three-layer architecture: raw/ (immutable sources), wiki/ (LLM-generated pages), and CLAUDE.md (schema). Three operations: ingest (process new sources), query (ask questions), lint (health checks). It replaces RAG with plain markdown for personal/team-scale knowledge. This guide covers the complete setup with Claude Code and Obsidian.

In April 2026, Andrej Karpathy posted on X about a workflow shift: instead of using LLMs primarily for code generation, he had been using them to build personal knowledge bases. The post went viral — 16+ million views — and the follow-up GitHub Gist hit 5,000+ stars within days. It touched a nerve because it solved a problem every knowledge worker has: knowledge bases that collapse under their own maintenance weight.

This guide breaks down the pattern, shows you how to build one from scratch with Claude Code and Obsidian, compares it to RAG, and surveys the community implementations that emerged within a week.

## Table of Contents

Why Knowledge Bases Collapse

The Three-Layer Architecture

The Three Operations: Ingest, Query, Lint

Setting Up Your LLM Wiki with Claude Code

The Schema: Your Most Important File

Using Obsidian as the Frontend

LLM Wiki vs RAG: When to Use Which

Tooling and Infrastructure

Community Implementations

The Intellectual Lineage

Criticisms and Limitations

Sources

## Why Knowledge Bases Collapse

Every developer has a graveyard of abandoned knowledge systems. Notion databases with 200 pages and no updates since month three. Bookmarks folders with 500 links and no summaries. Obsidian vaults with promising graphs that went stale. The problem isn't the tools — it's the maintenance cost.

Building a knowledge base has three steps: collect (easy), organize (hard), maintain (impossible at scale). The grunt work of filing, cross-referencing, summarizing, and updating is where systems die. Adding a single new article means reading it, creating a summary, linking it to existing concepts, updating related pages, and checking for contradictions with existing knowledge. Nobody does this consistently.

Karpathy's insight is simple: LLMs are uniquely good at exactly this kind of bookkeeping. They can read a document, identify key concepts, create structured summaries, generate cross-references, update indexes, and flag contradictions — tirelessly, consistently, at near-zero marginal cost. The human curates what goes in; the LLM does everything else.

"The LLM writes and maintains all of the data of the wiki. I rarely touch it directly." — Andrej Karpathy

At the time of the post, Karpathy's wiki on a single research topic had grown to approximately 100 articles and 400,000 words — longer than most PhD dissertations — without him writing any of it directly.

## The Three-Layer Architecture

The LLM Wiki has a deliberately simple structure:

my-research/
├── raw/ # Layer 1: Immutable source documents
│ ├── articles/
│ ├── papers/
│ ├── repos/
│ ├── data/
│ ├── images/
│ └── assets/
├── wiki/ # Layer 2: LLM-generated markdown
│ ├── index.md # Content catalog (updated on every ingest)
│ ├── log.md # Append-only chronological record
│ ├── overview.md
│ ├── concepts/ # Concept pages
│ ├── entities/ # Entity pages
│ ├── sources/ # Source summaries
│ └── comparisons/ # Comparison pages
├── outputs/ # Dated reports, presentations
├── CLAUDE.md # Layer 3: Schema configuration
└── .gitignore

### Layer 1: Raw Sources (raw/)

Your curated collection of source documents — articles, papers, code repos, datasets, images. The LLM reads these but never modifies them. They serve as the verification baseline: every claim in the wiki traces back to a file in raw/.

Think of raw/ as immutable input. You can use the Obsidian Web Clipper browser extension to convert web articles to markdown and drop them directly into raw/articles/.

### Layer 2: The Wiki (wiki/)

LLM-generated markdown pages organized by type:

concepts/ — Concept pages (e.g., attention-mechanism.md, rag.md)

entities/ — Entity pages (e.g., openai.md, anthropic.md)

sources/ — Source summaries (one per ingested document)

comparisons/ — Comparison pages (e.g., rag-vs-fine-tuning.md)

Two structural files are critical:

index.md — Content catalog. Updated on every ingest. The LLM reads this first to navigate the wiki.

log.md — Append-only operation log. Records every ingest, every page update, every contradiction found.

The LLM maintains everything in this directory. Humans mostly read; the LLM mostly writes.

### Layer 3: The Schema (CLAUDE.md)

The most important file in the system. It defines the wiki's structure, naming conventions, page templates, and operational workflows. It transforms a generic LLM into a disciplined knowledge worker.

Named CLAUDE.md because Karpathy uses Claude Code as his primary agent, but the concept applies to any LLM agent with file access.

related
Obsidian + Claude Code: The Complete Integration Guide
5 strategies for connecting Obsidian with Claude Code — symlinks, MCP bridges, vault organization, and community workflows.

## The Three Operations: Ingest, Query, Lint

The LLM Wiki pattern defines three core operations. Karpathy frames the system using a compiler analogy: raw/ is source code, the LLM is the compiler, wiki/ is the executable output, lint is tests, and queries are runtime.

### Ingest

You drop a new source into raw/ and tell the LLM to process it.

> I added a new article to raw/articles/. Please ingest it.

The LLM:

Reads the document and discusses key takeaways

Creates a summary page in wiki/sources/

Cascades updates acr