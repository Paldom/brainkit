---
title: Build a Second Brain: Karpathy's LLM Wiki Method, Step by Step | Professor Glitch
url: https://www.askglitch.com/blog/build-a-second-brain
final_url: https://www.askglitch.com/blog/build-a-second-brain
source_type: web
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:55+00:00
published: 2026-05-02
content_digest: 0699ac42694e44df
---

GLITCHJOIN THE COMMUNITY

Home › Blog › Build a Second Brain: Karpathy's LLM Wiki Method, Step by Step

guides

# Build a Second Brain: Karpathy's LLM Wiki Method, Step by Step

Andrej Karpathy's LLM Wiki turns your notes into a compounding research artifact maintained by an AI. Here's the full method, the 3-layer architecture, and how to wire it up in Obsidian + Claude Code in an afternoon.

Professor Glitch

May 2, 2026

12 min

Now available

The Second Brain Kit is live

Everything in this guide, already built — plus three video lessons (~30 min) walking through the whole thing. The schema, the four commands, the templates, and a finished example vault. Watch lesson 1 free below.

Get The Second Brain Kit — $99 $49 →
Launch price · one-time payment · instant download · Obsidian + Claude Code

Most note-taking systems die for the same reason: maintenance.

You start strong. New folder, fresh Obsidian vault, color-coded tags, a clean PARA structure. Three weeks in, your inbox is full of unfiled notes. Three months in, you're using Apple Notes again because at least it doesn't make you feel guilty.

The reason isn't laziness. It's that "linking 50 notes to each other every time you read a paper" is genuinely boring work that humans don't want to do. The wiki dies when the maintainer gets tired.

Andrej Karpathy posted a gist in early 2026 that fixes the problem at the root: let an LLM maintain it. Not "use an LLM to query your notes." Let it actually own the wiki, write the pages, link the concepts, lint the contradictions, and keep the thing alive while you're asleep.

He calls it the LLM Wiki. It's the cleanest second-brain pattern I've seen in 10 years of failed Notion vaults. This guide walks you through what it is, why it works, and how to wire it up in Obsidian + Claude Code in an afternoon.

### I write deep-dives like this when I find an AI workflow that's actually worth your weekend. Want the next one?
Send me the next deep-dive

## Why every other note-taking system breaks

The pattern is always the same:

Every chat starts from zero. Every insight evaporates when the session closes. You're paying the same context tax every time.

Translated: when you ask ChatGPT or Claude the same question next month, it re-derives the answer from scratch. The 90 minutes you spent thinking about it last time? Gone. The five sources you read? Gone. The mental model you built? Gone.

That's goldfish memory. And that's how 99% of people use AI in 2026: as a smarter Google that forgets you the second you close the tab.

What you actually want is the opposite shape:

A persistent, compounding research artifact. Synthesis happens once, then gets updated instead of recomputed from scratch on every question.

That's Karpathy's framing. Read it twice. The whole method falls out of that one idea.

## The 3-layer architecture

Karpathy's vault has three layers. They're so cleanly separated that even his linter can tell when you've broken the rule.

### Layer 1: Sources (raw, immutable)

"Raw sources — immutable documents (articles, papers, images, data files). The LLM reads but never edits." — Karpathy

Everything you collect goes here, untouched. PDFs, web clippings, podcast transcripts, customer call notes, screenshots, your own raw thoughts. The rule is simple: once it lands in sources/, you don't edit it. Not even for typos. This is your immutable corpus, the source of truth.

In a real sources/ folder you might see:
sources/
├── 2026-04-acme-call.txt
├── customer-survey-q1.csv
├── pitch-deck-v3.pdf
├── competitor-pricing.html
└── onboarding-feedback.md

Why immutable? Because if the LLM ever rewrites a source, you lose the ability to audit what your conclusions are based on. Sources are the bedrock. Everything else is interpretation.

### Layer 2: The wiki (AI-owned)

*"The wiki is LLM-generated markdown files with summaries, entity pages, concepts, and cross-references. You read it; the LLM writes it."* — Karpathy

This is the magic layer. The LLM writes here. You don't.

Account profiles. Concept pages. Weekly recaps. Summaries that pull from 12 sources. Cross-links between everything. The agent maintains it the way a good Wikipedia editor would, except it never gets tired and never abandons a page halfway through.
wiki/
├── acme-account.md
├── pricing-strategy.md
├── competitor-map.md
├── 2026-q1-recap.md
└── stripe-vs-paddle.md

The mental flip that makes this work: stop thinking of these as "my notes." They're notes the AI keeps for you. You direct, you ask questions, you decide what to research. The agent does the editorial work (extracting, summarizing, cross-linking, deduplicating, updating).

A single new source dropped into Layer 1 might trigger writes to 10–15 pages in Layer 2. That's the compounding part. Every source you ingest makes the wiki smarter, not just larger.

### Layer 3: The schema (CLAUDE.md)

"The schema is a configuration document specifying structure, conventions, and workflows. This makes the LLM a disciplined wiki maintainer rather than a generic chatbot." — Karpathy

This is where Claude Code's CLAUDE.md earns its keep. It tells the agent how the vault is organized and which workflows are available.
# LLM Wiki schema

## Layers
- `sources/` — raw, never edit. Cite by filename in frontmatter.
- `wiki/` — AI-maintained. Backlink every concept. Summary at top.
- `log.md` — append-only session log. Newest entries first.

## Workflows
- /capture <url> — clip + ingest a URL into sources/, then update wiki/
- /lint — health check: broken links, orphan pages, contradictions
- /sync — refresh wiki/ pages from any new sources/
- /digest — generate this week's recap from log.md

## Rules for wiki/ pages
- Frontmatter: title, summary, sources, last_updated
- Backlink every concept page from at least one parent
- Cite source filenames inline as [[source: filename.md]]
- Run /lint after every batch write

That CLAUDE.md is what turns Claude Code from a chatbot into a wiki maintain