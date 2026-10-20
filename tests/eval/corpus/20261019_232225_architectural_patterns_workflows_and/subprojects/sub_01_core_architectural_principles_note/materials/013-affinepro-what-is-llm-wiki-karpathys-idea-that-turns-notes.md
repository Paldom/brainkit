---
title: What Is LLM Wiki? Karpathy's Idea That Turns Notes Into a Brain | AFFiNE
url: https://affine.pro/blog/what-is-llm-wiki
final_url: https://affine.pro/blog/what-is-llm-wiki
source_type: social
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:27+00:00
published: 2026-07-09
content_digest: dcd2cce198178677
---

əˈfʌɪn | a-fine

English

日本語ja-JP

한국어ko-KR

繁體中文zh-TW

Deutschde-DE

Españoles-ES

Françaisfr-FR

Português (Brasil)pt-BR

Italianoit-IT

English

日本語ja-JP

한국어ko-KR

繁體中文zh-TW

Deutschde-DE

Españoles-ES

Françaisfr-FR

Português (Brasil)pt-BR

Italianoit-IT

English

日本語ja-JP

한국어ko-KR

繁體中文zh-TW

Deutschde-DE

Españoles-ES

Françaisfr-FR

Português (Brasil)pt-BR

Italianoit-IT

Product

AFFiNE AI

Create Smarter with AI

Docs

Powerful, Simple for All

Edgeless

Collaborate Without Limits

Download

Team

Teamhub

Unified Team Document Space

Enterprise

Private cloud and self-hosted deployments

Book a Demo

Discuss deployment, security, licensing and pilots

Industries

Resources

Docs

Templates

About Us

Blog

Timers

Community

Discord

Get tips and support from 7k+ users

Twitter

Stay tuned for the latest news

Community

Become an ambassador and track events

Download

Pricing

English
Book a DemoGet Started
Explore on Desktop

70K+

IndustriesBook a Demo

Product

AFFiNE AI

Create Smarter with AI

Docs

Powerful, Simple for All

Edgeless

Collaborate Without Limits

Download

Team

Teamhub

Unified Team Document Space

Enterprise

Private cloud and self-hosted deployments

Book a Demo

Discuss deployment, security, licensing and pilots

Industries

Resource

Docs

Templates

About Us

Blog

Community

Discord

Get tips and support from 7k+ users

Twitter

Stay tuned for the latest news

Community

Become an ambassador and track events

Download

Pricing

English

Book a DemoGet Started

All posts

Allen

Author, Operations Director·Published Jul 09, 2026

# What Is LLM Wiki? Karpathy's Idea That Turns Notes Into a Brain

Content

## What LLM Wiki Actually Means and Why the Term Is So Confusing

Search for "LLM Wiki" and you'll run into a wall of conflicting explanations. Some pages describe a personal note-taking method. Others point to a downloadable desktop app. A few reference GitHub repositories that auto-generate encyclopedia-style articles using AI agents. They're all using the same two-word phrase, but they're talking about very different things.

Before unpacking each layer, here's the simplest definition you need:

An LLM Wiki is a structured collection of markdown files designed to be read, queried, and maintained by a large language model — turning your personal notes and documents into a living knowledge base that an AI can reason over, rather than a static archive only a human can browse.

That core idea, championed by Andrej Karpathy, is where everything starts. But the term has splintered into at least three distinct meanings — and understanding which one someone is referring to saves you hours of confusion.

### The Three Meanings of LLM Wiki

When someone says "LLM Wiki" or "llm-wiki," they could mean any of the following:

• The design pattern — A workflow philosophy where you maintain a directory of plain markdown files organized so that an LLM (like Claude, GPT, or an open-source model) can consume them directly as context. You ask questions in natural language; the model reads your files and gives grounded answers drawn from your knowledge, not the general internet. This is the Karpathy-originated concept at the heart of the movement.

• Open-source CLI and agent tools — Projects like nvk/llm-wiki, which functions as a plugin for coding agents such as Claude Code or OpenAI Codex. It spins up parallel research agents that investigate topics and compile cross-referenced wiki articles — no standalone app required.

• Desktop applications and wiki generators — Tools like nashsu/llm_wiki, a cross-platform desktop app built with Tauri and React that provides a visual knowledge tree, a chat interface, and a knowledge graph view. Other projects, such as Pratiyush/llm-wiki, mine your existing LLM conversation transcripts and generate a browsable static wiki from them.

Each meaning is legitimate. Each serves a different audience. And the overlap between them is exactly what makes a simple search so disorienting.

### Why the Term Has Become So Confusing

The AI knowledge management space has exploded in a remarkably short window. Concepts that barely existed a couple of years ago — retrieval-augmented generation, agent-driven research, context-window optimization — have gone from academic papers to everyday developer tools. In that rush, distinct ideas collapsed into shared shorthand.

"Wiki LLM" might refer to using AI to generate wiki content. "LLM wiki" might mean feeding a wiki to an AI. The design pattern and the tools built around it ended up sharing a name, and most articles you'll find online assume you already know which version they're discussing. Some focus entirely on one GitHub repository without acknowledging the broader concept. Others explain the philosophy without mentioning that installable tools already exist.

The result is a fragmented content landscape where beginners bounce between pages that each tell a different slice of the story, never getting the full picture. This article is designed to fix that. It covers all three meanings, explains how they connect, and helps you decide which approach — or combination of approaches — fits your actual needs.

The concept is deceptively simple on the surface, but the engineering choices underneath it reveal a genuinely new way of thinking about knowledge. To understand why this idea resonates so deeply with developers, researchers, and AI enthusiasts, it helps to trace it back to the person who articulated it most clearly.

## Andrej Karpathy and the Origin of the LLM Wiki Concept

Andrej Karpathy is not someone who needs an introduction in the AI world. As a co-founder of OpenAI, former senior director of AI at Tesla (where he led the Autopilot vision team), and one of the most respected educators in deep learning, his ideas carry serious weight. So when Karpathy published a GitHub Gist titled "LLM Wiki" describing a pattern for building personal knowledge bases with LLMs, the developer communit