---
title: Karpathy's LLM Knowledge Base: Build Your Second Brain
url: https://codersera.com/blog/karpathy-llm-knowledge-base-second-brain/
final_url: https://codersera.com/blog/karpathy-llm-knowledge-base-second-brain/
source_type: social
providers: brave, kimi
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:36+00:00
published: 2026-06-19
content_digest: b3ffa19d07e88a68
---

CoderseraAboutServicesContactBlogToolsGuides
Apply as a FreelancerHire Developers
Hire

About usServicesContactBlogToolsGuides
Apply as a FreelancerHire Developers

Search articles, topics, and guidesSearch

AI

# Karpathy's LLM Knowledge Base: How He Uses AI to Build and Manage His Second Brain

Andrej Karpathy revealed a shift from using LLMs for code generation to building a self-maintaining personal knowledge base. Here's the full architecture and how to build your own.

Published
06 Apr 2026•
Updated
19 Jun 2026• 8 min read

Karpathy's LLM Knowledge Base

Quick answer. Andrej Karpathy's LLM knowledge base is a self-maintaining personal wiki: an LLM ingests his notes, conversations, and reading, then writes structured, interlinked markdown files he edits and re-feeds. The result is a second brain that grows itself — not generating code but generating knowledge structure. You can replicate it with any local or hosted LLM plus a markdown editor like Obsidian.

On April 3, 2026, Andrej Karpathy posted something on X that resonated well beyond the usual AI news cycle. He wasn't announcing a new model or a benchmark result. He was describing a change in how he personally uses LLMs — a shift from generating code to generating knowledge structure. He called it the Karpathy LLM knowledge base, a form of AI-powered personal knowledge management that builds a self-maintaining wiki from raw research material. Within days the post had spawned a GitHub Gist, a wave of community implementations, and serious debate about whether this approach makes RAG pipelines obsolete for personal use.

This article breaks down exactly how Karpathy's system works, why he made the design choices he did, and how you can build an identical setup for your own research or engineering work.

Want the full picture? Read our continuously-updated AI coding agents complete guide — how Aider, Cline, Continue, Cursor, Claude Code and friends compare for autonomous software engineering.

## What Karpathy's LLM Knowledge Base Actually Is

Karpathy's framing is precise: he is spending a large fraction of his LLM token budget not on code generation but on knowledge manipulation. The system is a personal wiki — a collection of interlinked Markdown files — that an LLM writes and maintains autonomously as new source material is added.

The result at the time of posting: a single research topic had grown to roughly 100 articles and 400,000 words — longer than most PhD dissertations — without Karpathy writing a single word of it directly. The LLM does the writing, the linking, the categorizing, and the consistency checking.

What makes this different from AI-assisted note-taking tools like Notion AI or standard summary bots is the active maintenance loop. The LLM isn't just summarizing documents once. It is incrementally compiling a structured knowledge base, running "health checks" to detect inconsistencies, and generating backlinks as new concepts appear. It behaves less like a chatbot and more like a diligent research librarian who never sleeps.

## The Three-Folder Architecture Behind Karpathy's Second Brain

The entire system rests on three directories. The simplicity is intentional — Karpathy chose a structure that any LLM agent can navigate without custom tooling.

### raw/ — Ingesting Sources Without Friction

Raw source material goes directly into a folder called raw/. This includes research papers (PDFs converted to Markdown), GitHub repositories, web articles clipped via the Obsidian Web Clipper, datasets, meeting notes, and screenshots. The Obsidian Web Clipper converts web pages to .md files and saves images locally so the LLM can reference them through its vision capabilities — no external URLs, no link rot.

The raw folder is append-only. Nothing is edited here. It is the single source of truth for everything the LLM has ever read.

### wiki/ — Where the LLM Writes and Interlinks

The wiki/ directory is where the LLM outputs structured knowledge. It writes encyclopedia-style articles for each concept it identifies across the raw material, creates backlinks between related articles, and maintains an index file that summarizes the entire wiki at a glance. When a new source is added to raw/, the LLM reads the existing index, identifies which wiki articles need to be updated or created, and runs a targeted update — it does not rewrite everything from scratch.

The format is pure Markdown throughout. This is deliberate: Markdown is the most compact, LLM-readable, and human-auditable structured format that exists. No proprietary schema, no vector embeddings — just files a human can open and read in any text editor or view through Obsidian's graph view.

### outputs/ — Derived Answers and Reports

The outputs/ folder stores query responses, synthesized reports, and analysis results. When Karpathy asks a question — "what are the three most promising architectures for long-context reasoning?" — the LLM reads the wiki index, drills into relevant articles, and writes the answer to outputs/ as a Markdown document. This gives every query a persistent, auditable record.

## The Compilation Step and Linting Passes

Karpathy describes two modes of LLM operation in the system: the compilation step and the linting pass.

The compilation step happens when new material arrives in raw/. The LLM reads the new source, extracts key concepts, checks whether those concepts already exist as wiki articles, and either creates new articles or appends to existing ones. It then updates the index file and generates backlinks. At ~100 articles and 400,000 words, the entire wiki index fits comfortably within a modern LLM's context window, which means the LLM can check for duplicates and contradictions without any retrieval system.

The linting pass is a periodic "health check" that runs independently of new ingestion. The LLM scans the entire wiki for inconsistencies — articles that contradict each other, concepts mentioned in one article but lacking 