---
title: Karpathy's LLM Knowledge Base Method - A Practical Starting Point | Jamal Hansen
url: https://jamalhansen.com/blog/road-to-agentic-notes/
final_url: https://jamalhansen.com/blog/road-to-agentic-notes/
source_type: social
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:25+00:00
published: 2026-05-15
content_digest: cd46df5f7b9df38d
---

Jamal Hansen

Blog

Series

Start

About

Subscribe

Home Â» Series Â» Notes and Knowledge
Part 3 of 5 Â· Notes and Knowledge

# Karpathy's LLM Knowledge Base Method - A Practical Starting Point

Karpathy called LLM-based knowledge bases "very useful." Why the architecture works and how to start building one in practice.

April 5, 2026 Â· 7 min Â· Jamal Hansen

Karpathy’s LLM knowledge base method works by having an LLM maintain a wiki of markdown files rather than retrieving from raw documents at query time. When you add a source, the LLM integrates it into the existing network, updating pages, revising summaries, and noting contradictions. By the time you need an answer, the synthesis is already done. Your job is to curate sources and ask good questions. The LLM does everything else.

LLM Knowledge Bases

Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulatingâ¦
— Andrej Karpathy (@karpathy) April 2, 2026

The basic idea is that an LLM builds and maintains a wiki for you. You drop in source material. The LLM reads it, extracts what matters, and integrates it into an existing network of markdown files. It updates pages when new information contradicts old claims. It cross-references concepts across everything you have ever added.

What makes it interesting goes beyond note-taking. That network of markdown files lives on your local device. An LLM you chat with in Claude Code (or any tool with filesystem access, including a model running on your own machine) can use it as context.

Every source you add makes the whole thing richer. Every question compounds.

It is a lot of concepts at once, so you probably should not start here.

## Why most developer knowledge disappears#

You finish a tutorial. You build the thing. Two weeks later, you are back on Stack Overflow (or in your favorite LLM), looking up the same syntax or solving the same issue.

This is not a memory problem. It is a storage problem. You understood the concept. You did not put it anywhere that survives.

Most people keep notes the way that they keep leftover Whataburger ketchup and the extra three birthday candles from the pack: dropped in a drawer, never looked at again. Quietly gone in the next laptop migration. These are not notes. They are evidence that learning happened.

The difference between that and what Karpathy built is not intelligence. It is structure. Notes that reference each other, grow over time, and feed back into your questions are a different category of thing entirely.

## What Karpathy built#

Most AI tools for documents work the same way. NotebookLM, ChatGPT file uploads, most RAG systems: they retrieve from raw documents at query time. The LLM reads your files, answers your question, and forgets. Ask the same question six months later and it starts from scratch. Nothing accumulates.

Karpathy’s wiki is different. The LLM does not retrieve. It compiles. When you add a source, the LLM integrates it into the existing wiki, updating entity pages, revising concept summaries, noting where new information contradicts old claims. The synthesis is already there by the time you need it. The cross-references are already made.

When you ask a question, the answer does not disappear into chat history. It gets filed back into the wiki as a new page. Your explorations compound the same way your sources do.

His description of the division of labor is worth keeping: “The human’s job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM’s job is everything else.”

That is the destination. The starting line is simpler than it looks.

## Retrieve vs. compile: how this differs from other tools#

The distinction matters because a lot of tools sound similar.

ToolHow it worksWhat accumulates

NotebookLM, ChatGPT uploadsRetrieves from raw documents at query timeNothing – each session starts fresh

Standard RAGChunks and embeds docs, retrieves relevant chunksEmbeddings, not synthesized knowledge

Karpathy’s wiki (Foam or Obsidian + LLM)LLM compiles sources into a linked wikiSynthesis, cross-references, updated entity pages

The compile step is what makes knowledge compound. The other tools are retrieval with extra steps.

## Where you can start#

You do not start with a system. You start with a habit.

Before an LLM can maintain your wiki, you need two things: a collection of notes worth maintaining, and the practice of adding to it. Neither of those comes from installing a tool. They come from writing things down consistently until it becomes automatic.

The files in Karpathy’s system are standard markdown text. The notes you create today are the same files an LLM will maintain later. When you start out writing your first note, you are building the foundation.

## Start today#

### Step 1#

Install Foam in VS Code. It takes about two minutes. You probably already have VS Code open. You do not have to learn a new application or leave your editor.

That is it. You have a wiki.

Note: if you already use Obsidian, it’s a perfect alternative.

### Step 2#

Make a dedicated folder for your notes. Call it notes/ or wiki/ or whatever you will actually use. That folder is your wiki.

### Step 3#

Learn the one piece of syntax that makes this work: [[double brackets]]. Write [[merge conflicts]] in any note and Foam treats it as a link to another note. That linked note needs to live as merge conflicts.md in your folder. It does not have to exist yet. Write the link first. Create the file when you get there.

## What a note looks like#

# git pull runs a fetch and a merge under the hood
When you run git pull, it downloads the latest changes (like [[git fetch]])
and merges them into your current branch automatically.
That is why you can still get [[merge conflicts]] from a simple pull.

