---
title: Medium
url: https://medium.com/data-science-collective/claude-md-vs-agents-md-vs-skill-md-which-file-owns-what-in-2026-13859378f56a
final_url: https://medium.com/data-science-collective/claude-md-vs-agents-md-vs-skill-md-which-file-owns-what-in-2026-13859378f56a
source_type: social
providers: exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:37+00:00
published: 2026-07-09T00:00:00.000Z
content_digest: 94f11e76bbd68d78
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

##
Data Science Collective

·

Advice, insights, and ideas from the Medium data science community

Member-only story

Machine Learning

Deep Learning

Artificial Intelligence

Programming

AI

# CLAUDE.md vs AGENTS.md vs SKILL.md: Which File Owns What in 2026

## Three files, three loading models, one decision you make once.

Anubhav

10 min read
·
Jul 9, 2026

--

3

Listen

Share

Read the article for free here.

Press enter or click to view image in full size

Over 4,300 engineers upvoted the same GitHub issue asking if Claude Code could please read AGENTS.md natively. As of Claude Code 2.1.201 in July 2026, the answer remains no.

Anthropic updated its own memory documentation to tell developers how to force the behavior anyway. The official command is ln -s AGENTS.md CLAUDE.md right in the terminal. Anthropic ships the workaround for the file its own tool refuses to read.

The engineering under this is more interesting than the argument. A single line inside the claude-api SKILL.md in Anthropic's public skills repository explains the situation. The answer lies in the description field of the YAML frontmatter. Unlike CLAUDE.md and AGENTS.md, that description is the reason Claude reads the rest of the file.

Three files, three loading models, and the decision only becomes obvious once you see the gate.

## The Context Reshuffle of Late 2025

The timeline explains how the industry arrived at this split. In August 2025, the AGENTS.md specification launched to give AI coding assistants a…

--

--

3

## Published in Data Science Collective

950K followers

·Last published 20 hours ago

Advice, insights, and ideas from the Medium data science community

## Written by Anubhav

5K followers

·14 following

I write deep-dives on agents, RAG, evals, and what actually breaks when you ship AI systems https://substack.com/@anubhavgoyal10

Help

Status

About

Careers

Press

Blog

Store

Privacy

Rules

Terms

Text to speech
