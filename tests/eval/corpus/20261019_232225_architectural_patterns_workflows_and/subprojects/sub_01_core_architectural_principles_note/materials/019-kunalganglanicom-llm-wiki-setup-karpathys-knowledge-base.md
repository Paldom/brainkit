---
title: LLM Wiki Setup: Karpathy's Knowledge Base [2026 Guide]
url: https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base
final_url: https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base
source_type: social
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:30+00:00
published: 2026-09-16
content_digest: af9a23e50c3ca14a
---

Skip to content

KG.Search⌘K

Blog

Work

Hire me, or see what I ship.

ProjectsCase studies & shipped work

ServicesWork with me

SponsorSponsor the blog

Writing

Essays and references on AI engineering.

BlogEssays on AI engineering

Learning PathsGuided curricula

Topic PillarsDeep-dive hubs

GlossaryAI & dev terms, defined

CheatsheetsQuick references

ComparisonsX vs Y, decided

Playground

Things to click, play, and take apart.

Tools28 dev & AI utilities

Games16 browser games

DemosInteractive explainers

ChallengesDaily coding puzzles

About

Me

AboutWho I am

UsesMy gear & setup

ResumeCV (PDF)

Shelf

BookshelfBooks I recommend

Reading ListWhat I'm reading

Subscribe

Let's talk

>_

Home

›

Blog

›

LLM Wiki Setup: Karpathy's Knowledge Base [2026 Guide]

Technology

# LLM Wiki Setup: Karpathy's Knowledge Base [2026 Guide]

I've been running Karpathy's LLM Wiki pattern for three months. Here's the real setup process, which agents work best, and where the pattern breaks down.

Kunal Ganglani April 15, 2026· 15 min read· Updated September 16, 2026

Save

Listen to this article

--:--1x

⚡30-second version

Andrej Karpathy created a pattern where an AI agent builds and maintains a personal wiki from your documents — instead of searching raw files every time you ask a question, like ChatGPT or NotebookLM do. You paste a prompt into a coding agent, point it at your files, and it creates interlinked markdown pages that get smarter over time. It's surprisingly effective for research and engineering notes, but it needs regular maintenance and breaks down when your wiki gets too big for the AI's memory.

An LLM Wiki is a persistent, structured knowledge base made of interlinked markdown files that an LLM agent builds and maintains for you. Instead of re-deriving answers from raw documents on every query like RAG, it compiles knowledge once and keeps it current.

Andrej Karpathy posted a GitHub gist in April 2026 describing this pattern. It now has 5,000+ stars and 5,000+ forks. I've been running it daily for three months, and I think it's the most interesting shift in personal knowledge management since Obsidian itself. But the gist is a starting point, not a finished product. Here's what actually works after sustained daily use — and where it falls apart.

Key takeaways:

The LLM Wiki pattern compiles knowledge into persistent, interlinked markdown files rather than re-retrieving raw chunks on every query like traditional RAG.

Setting up your own LLM Wiki requires an Obsidian vault, a coding agent like Claude Code or OpenAI Codex, and the Karpathy gist pasted into your agent's system prompt.

Incremental updates are the killer feature: you point the agent at new source material and it surgically updates only the affected wiki pages.

The pattern breaks down when your wiki exceeds roughly 200 files and your agent can't hold the full graph in context. Directory-level indexes are the fix.

There is no official "LLM Wiki v2" — but the community has iterated on the original gist with contradiction-checking prompts and auto-index generation.

The LLM Wiki is a compiler for knowledge, not a search engine.

## What Is an LLM Wiki and Why Should You Care?

Most engineers have tried uploading documents to ChatGPT or Google's NotebookLM. You drop in 10 PDFs, ask a question, get a synthesized answer from retrieved chunks. It works. But ask a different question tomorrow and the model starts from scratch. No accumulation. No cross-referencing. No compounding understanding.

An LLM Wiki setup uses Karpathy’s prompt pattern to compile sources into a persistent, interlinked markdown knowledge base.

Obsidian vault containing interlinked markdown files as the wiki artifact

Coding agent like Claude Code or OpenAI Codex to read/write pages

Karpathy gist pasted into the agent’s system prompt as instructions

Incremental updates: point at new sources, update only affected pages

Cross-links between entity/topic pages to make the graph browsable

Contradiction-flagging between sources to surface conflicts in the wiki

Directory-level indexes to cope when the wiki exceeds roughly 200 files

No official “LLM Wiki v2”; community adds contradiction checks and auto-indexing

The LLM Wiki flips this entirely. As Andrej Karpathy, former Director of AI at Tesla and co-founder of OpenAI, puts it: "The knowledge is compiled once and then kept current, not re-derived on every query. This is the key difference: the wiki is a persistent, compounding artifact."

In practice, it's a folder of markdown files that an LLM agent reads, writes, and maintains. Each file represents an entity, topic, or theme. The agent creates cross-links between pages, flags contradictions between sources, and updates summaries as you feed in new material. You never write the wiki yourself. You source, explore, and ask questions. The LLM does the grunt work.

This matters because the gap between "I uploaded some files" and "I have a queryable knowledge base" is enormous. The LLM Wiki pattern bridges it. Based on the search data I track at kunalganglani.com, the query "llm wiki" alone generates over 20,000 impressions per quarter. Thousands of engineers are looking for exactly this kind of structured approach to local AI knowledge management.

$

Hands-on tool

### RAG Cost Calculator

Calculate the full cost of a RAG pipeline: document embedding, vector storage, and LLM generation.
Calculate RAG cost →

## The Karpathy Gist Explained: What It Actually Says

The gist (ID 442a6bf555914893e9891c11519de94f) is surprisingly short. It's not a tool. Not an installable package. Not even a script. It's a prompt pattern — what Karpathy calls "an idea file, designed to be copy pasted to your own LLM Agent."

Here's what the gist actually contains:

The core idea — a prose explanation of why compiling knowledge into a wiki beats RAG-style retrieval for personal knowledge management.

The workflow description — Karpathy's split-screen setup with an 