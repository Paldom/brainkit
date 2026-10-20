---
title: Your Second Brain, Rebuilt: A Complete Guide to the Karpathy Knowledge Base Method
url: https://zerofuturetech.substack.com/p/your-second-brain-rebuilt-a-complete
final_url: https://zerofuturetech.substack.com/p/your-second-brain-rebuilt-a-complete
source_type: social
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:29+00:00
published: 2026-04-14
content_digest: 5df264df25e63251
---

# zerofuturetech’s newsletter

SubscribeSign in

# Your Second Brain, Rebuilt: A Complete Guide to the Karpathy Knowledge Base Method

### Build a personal or professional knowledge base using Andrej Karpathy's LLM wiki method — with Obsidian, Claude Code, and Graphify. No RAG, no black boxes, full local control.

zerofuturetech

Apr 14, 2026

4

Share

Reading time: ~15 min | Level: Intermediate | Tools: Obsidian · Claude Code · Claude.md · Graphify

Welcome to subscribe my X: https://x.com/jingwangtalk

If you are a visual learner, please watch my youtube video (Chinese):

Andrej Karpathy recently shared an approach that’s made a lot of people rethink how they manage notes and knowledge.

zerofuturetech's newsletter is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber.

Subscribe

His core idea is straightforward: instead of running vector search over raw source material every time you need something, have an LLM “compile” your raw content into structured wiki files first. When you query later, the LLM is reading already-distilled knowledge — concepts clearly defined, sources traceable, entries cross-linked to each other.

This solves a fundamental problem with traditional RAG. Vector search finds semantically similar text fragments, but it has no idea that “Agent Harness” and “tool calling” are related concepts, or who coined the term, or which other ideas it conflicts with. The wiki format preserves those relationships natively.

More importantly, knowledge compounds as you use it. Every query triggers a wiki update. Your notes stop being a static archive and become a living knowledge network that grows alongside your thinking.

This guide walks you through three versions of the setup:

Obsidian version — GUI-based, ideal for daily knowledge management and content consumption

Local folder version — works directly with Claude Code, ideal if you already have a large collection of work documents

Graphify version — a community-built Python tool that packages the whole pipeline into a single CLI command

my github template: https://github.com/jingw2/llm-wiki-template

## Understand the System Design First

Spend five minutes on the architecture before you build anything. Every step will make more sense.

### Three-Layer File Structure

knowledgebase/
├── raw/ # Read-only source vault — agent never modifies this
│ ├── articles/ # Web clippings
│ ├── podcasts/ # Podcast transcripts
│ ├── my-notes/ # Personal notes
│ └── assets/ # Images, PDFs, attachments
│
├── wiki/ # Agent-maintained knowledge base — the core of retrieval
│ ├── concepts/ # One file per concept: definition, sources, cross-links
│ ├── entities/ # People, tools, organizations, proper nouns
│ ├── summaries/ # One summary per raw file, 1:1 relationship
│ ├── syntheses/ # Cross-source analysis, manually triggered
│ ├── scenarios/ # Applied analysis for specific use cases
│ ├── qa/ # High-quality Q&A records
│ ├── INDEX.md # Navigation index for the entire wiki
│ └── log.md # Append-only operation log
│
└── Claude.md # Agent operating instructions — the soul of the system

One rule for raw/: read-only, always. The agent never touches source files. All original content stays exactly as you added it.

### What Claude.md Is and Why It Matters

Claude.md is not a README. It’s the agent’s behavioral specification — a file that encodes your entire knowledge management logic. Paste it into Claude Code or any agent, and it immediately knows its role, its responsibilities, and the order in which to do things.

It contains several critical design decisions:

Role definition: The agent’s job is to “compile” (distill raw material into wiki pages), not to “answer” (search raw files directly). This distinction matters. Compilation is a one-time upfront investment that makes every future query cheap.

Five page formats: concepts, entities, summaries, syntheses, and qa each have a fixed frontmatter schema. The source_files field is particularly important — it records which raw files each wiki page was generated from. When a source file changes, the system knows exactly which downstream pages need recompilation.

Token budget strategy: Read INDEX.md first (lightweight, a few KB), then 2–3 relevant wiki pages (medium), and only reach for raw source files as a last resort (heavy). This prevents every conversation from loading the entire knowledge base into context.

Dual mandatory outputs: Every conversation must produce both an answer and a wiki update — no choosing one or the other. This is the anti-evaporation constraint. Valuable Q&A doesn’t disappear into chat history; it lands in qa/ where future queries can find it.

Citation format rules: Wiki page references use [[page-name]], raw file references use [filename]. Conclusions without citations don’t count. This keeps the knowledge base traceable from day one.

### Four Standard Operation

## Full Obsidian Setup

### Step 1: Install Obsidian and Create the File Structure

Download Obsidian. It’s free for local use and stores all data on your own device — no cloud dependency.

Once you’ve created a Vault, you have two ways to set up the file structure:

Option A (recommended): Git clone the template
git clone https://github.com/jingw2/llm-wiki-template
cd knowledgebase
The template includes the complete folder structure, Claude.md (English and Chinese versions — keep one), and a preconfigured plugin list.

Option B: Manual setup

Create the folder structure by hand, then download Claude.md from GitHub and drop it in the root.

### Step 2: Install Content Capture Tools

Web articles: Obsidian Web Clipper

Go to Obsidian Settings → Community Plugins → Browse, search for Web Clipper, and install it.

Also install the browser extension (Chrome, Firefox, and Arc are all supported).

Plugin configuration: go to plugin settings → General → Vaults, enter your vault folder name (e.g., knowledgebase), and press Enter to save.

Usage