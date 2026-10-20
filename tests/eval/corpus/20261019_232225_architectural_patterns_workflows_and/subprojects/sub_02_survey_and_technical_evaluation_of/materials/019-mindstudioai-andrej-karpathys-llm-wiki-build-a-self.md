---
title: Andrej Karpathy's LLM Wiki: Build a Self-Updating AI Second Brain with Obsidian in 1 Hour | MindStudio
url: https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-obsidian-ai-second-brain
final_url: https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-obsidian-ai-second-brain
source_type: social
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:51+00:00
published: 2026-05-07
content_digest: 9d37cd594dbb49e8
---

Skip to main content

Product

AI ModelsAI Media WorkbenchAgent Skills PluginWorkflow Capabilities

Pricing
Learn

UniversityDocumentation

BlogAbout

Log inGet Started

My Workspace

Product
AI ModelsAI Media WorkbenchAgent Skills PluginWorkflow Capabilities

Pricing
Learn
UniversityDocumentation

BlogAbout

Log inGet Started

My Workspace

Blog/Andrej Karpathy's LLM Wiki: Build a Self-Updating AI Second Brain with Obsidian in 1 Hour
WorkflowsAutomationProductivity

# Andrej Karpathy's LLM Wiki: Build a Self-Updating AI Second Brain with Obsidian in 1 Hour

Karpathy's LLM Wiki spec is the blueprint. Add Obsidian, Codex automations, and a CRM layer to get a second brain that actually surfaces what you saved.

Edited by Luis Chavez-Mattos, Director of Product·May 7, 2026·RSS

## Andrej Karpathy Designed the Spec. Here’s How to Build the System.

Andrej Karpathy published a GitHub page describing exactly how he thinks an LLM-native knowledge base should work — and it’s the most useful piece of software architecture documentation most people have never read.

The document is called the LLM Wiki. It’s not a product. It’s a spec. A set of principles for how to structure a personal knowledge base so that a language model can actually use it, rather than just search it. Karpathy’s insight is that most second brain systems fail not because they lack content, but because they lack structure that an LLM can navigate. You can have ten thousand notes and still get worse answers than someone with fifty well-organized ones.

If you build from Andrej Karpathy’s LLM Wiki GitHub spec as your architectural foundation, you get something qualitatively different from a RAG pipeline or a vector search over your notes. You get a wiki that an agent can read, reason over, and update — the same way a human researcher would.

This post is about what that spec actually says, why it works, and how to extend it into something you’ll use every day.

## What Karpathy Got Right That Everyone Else Gets Wrong

### Everyone else built a construction worker.
We built the contractor.

🦺

CODING AGENT

Types the code you tell it to.
One file at a time.

🧠

CONTRACTOR · REMY

Runs the entire build.
UI, API, database, deploy.

The world's most powerful product manager agentTry Remy today

Most knowledge management systems are write-only. You clip articles, paste transcripts, dump PDFs. The information goes in and never comes back out in a useful form. The problem isn’t retrieval — it’s that the stored content was never processed into a form that’s easy to reason over.

Karpathy’s spec solves this with a simple architectural decision: separate raw source material from synthesized knowledge. Raw files go into /raw. An agent reads them, extracts concepts, entities, and ideas, and writes structured wiki pages into /wiki. The original source is preserved but the working knowledge lives in a different layer.

This matters because LLMs are much better at reasoning over a well-structured 500-word wiki page than over a raw 8,000-word YouTube transcript. The synthesis step isn’t just compression — it’s translation into a format the model can actually use.

The second key decision is the agents.md file. This is a plain-text prompt file that governs all agent behavior. It’s not code. It’s not a config file. It’s just instructions, written in natural language, that tell any agent how to process new files, how to answer queries, how to update the index. You can edit it directly in Obsidian. If you want the agent to do something new, you add a line.

This is the part most people miss when they try to build systems like this. They reach for databases, vector stores, elaborate APIs. Karpathy’s spec uses markdown files and a text document. The simplicity isn’t a limitation — it’s what makes the system durable and hackable.

## The Architecture, Piece by Piece

The folder structure is minimal by design. You need: /raw for unprocessed source files, /raw/processed for files after ingestion, /wiki for AI-generated pages, /journal for dated entries, /crm for contact records, and three root files: agents.md, index.md, and log.md.

That’s the whole thing. No database. No embeddings. No infrastructure.

The index.md file is the catalog — a running list of everything in the wiki with links to individual pages. The log.md file records every operation: when a file was processed, when a query was answered, when the wiki was updated. These two files give any agent entering the system a complete picture of what’s there and what’s happened.

The Obsidian Web Clipper Chrome extension handles ingestion. Install it, point it at your vault, set the note location to /raw, and it will pull full article content and complete YouTube transcripts directly into your vault with a single click. The front matter it generates includes source title, source URL, and creation date. You can extend it — for instance, adding an instruction to agents.md to extract the YouTube channel name and add it to the source file’s front matter, which is useful when you’re tracking which creators you’re learning from.

When the agent processes a raw file, it does several things in sequence: reads the source, creates or updates wiki pages for the concepts and entities it finds, cross-links those wiki pages back to the original source file, updates index.md, and appends an entry to log.md. Then it moves the source file from /raw to /raw/processed. The processed folder is how you know what’s been ingested. The raw folder is how you know what’s waiting.

## Plans first.Then code.

PROJECTYOUR APP

SCREENS12

DB TABLES6

BUILT BYREMY

1280 px · TYP.

yourapp.msagent.ai

A · UI · FRONT END

Remy writes the spec, manages the build, and ships the app.

The world's most powerful product manager agentTry Remy today

One of the more interesting behaviors in the spec: when you ask the wiki a question, it doesn’t just answer. It checks whether the synthesized answer represents a new concept worth preservi