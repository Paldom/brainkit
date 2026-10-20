---
title: llm-wiki · GitHub
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
final_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
source_type: social
providers: brave, gemini, kimi
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:22+00:00
published: 2026-10-17
content_digest: 90b290b03da901ad
---

Skip to content

Search Gists

Search Gists

All gistsBack to GitHub
Sign in

Sign up

Sign in

Sign up

You signed in with another tab or window. Reload to refresh your session.You signed out in another tab or window. Reload to refresh your session.You switched accounts on another tab or window. Reload to refresh your session.Dismiss alert

Instantly share code, notes, and snippets.

# karpathy/llm-wiki.md

Created
April 4, 2026 16:25

Show Gist options

Download ZIP

Star5,000+(5,000+)You must be signed in to star a gist

Fork5,000+(5,000+)You must be signed in to fork a gist

Embed

#
Select an option

Embed
Embed this gist in your website.

Share
Copy sharable link for this gist.

Clone via HTTPS
Clone using the web URL.

## No results found

Learn more about clone URLs

Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;

Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

Code

Revisions
1
Stars
5,000+
Forks
5,000+

Embed

#
Select an option

Embed
Embed this gist in your website.

Share
Copy sharable link for this gist.

Clone via HTTPS
Clone using the web URL.

## No results found

Learn more about clone URLs

Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;

Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

Download ZIP

llm-wiki

Raw

llm-wiki.md

# LLM Wiki

A pattern for building personal knowledge bases using LLMs.

This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.). Its goal is to communicate the high level idea, but your agent will build out the specifics in collaboration with you.

## The core idea

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up. NotebookLM, ChatGPT file uploads, and most RAG systems work this way.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis. The knowledge is compiled once and then kept current, not re-derived on every query.

This is the key difference: the wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.

You never (or rarely) write the wiki yourself — the LLM writes and maintains all of it. You're in charge of sourcing, exploration, and asking the right questions. The LLM does all the grunt work — the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice, I have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on our conversation, and I browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

This can apply to a lot of different contexts. A few examples:

Personal: tracking your own goals, health, psychology, self-improvement — filing journal entries, articles, podcast notes, and building up a structured picture of yourself over time.

Research: going deep on a topic over weeks or months — reading papers, articles, reports, and incrementally building a comprehensive wiki with an evolving thesis.

Reading a book: filing each chapter as you go, building out pages for characters, themes, plot threads, and how they connect. By the end you have a rich companion wiki. Think of fan wikis like Tolkien Gateway — thousands of interlinked pages covering characters, places, events, languages, built by a community of volunteers over years. You could build something like that personally as you read, with the LLM doing all the cross-referencing and maintenance.

Business/team: an internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents, customer calls. Possibly with humans in the loop reviewing updates. The wiki stays current because the LLM does the maintenance that no one on the team wants to do.

Competitive analysis, due diligence, trip planning, course notes, hobby deep-dives — anything where you're accumulating knowledge over time and want it organized rather than scattered.

## Architecture

There are three layers:

Raw sources — your curated collection of source documents. Articles, papers, images, data files. These are immutable — the LLM reads from them but never modifies them. This is your source of truth.

The wiki — a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.

The schema — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is str