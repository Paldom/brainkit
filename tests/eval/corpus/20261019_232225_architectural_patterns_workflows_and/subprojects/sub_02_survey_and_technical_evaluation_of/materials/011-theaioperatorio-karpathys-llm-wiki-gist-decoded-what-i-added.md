---
title: Karpathy's LLM Wiki Gist Decoded: What I Added
url: https://theaioperator.io/p/i-rebuilt-karpathys-llm-wiki-heres
final_url: https://theaioperator.io/p/i-rebuilt-karpathys-llm-wiki-heres
source_type: social
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:41+00:00
published: 2026-08-11
content_digest: 5ef4e76d5a97aa16
---

#

SubscribeSign in

# Karpathy's LLM Wiki Gist Decoded: What I Added

### The full three-layer pattern from the gist, plus the five rules I had to add to keep it running for six months.

Eugeniu Ghelbur

Apr 29, 2026

56

8

14

Share

The gist, in short. Karpathy’s pattern is three layers and three operations: raw sources, a wiki the model rewrites, and an index that points at both. Ingest, query, lint. That is the whole thing, and it is genuinely enough to start. The link to the original gist is at the bottom of this post. What follows is what happened when I ran it for six months.

Quick orientation. If you came here searching for Karpathy's original LLM Wiki gist, here it is: Karpathy’s original LLM Wiki gist. Bookmark it, it's still the cleanest starting point. What follows is the version I built on top of it, a second brain that rewrites itself, open-sourced so you can clone it: https://github.com/eugeniughelbur/obsidian-second-brain

## TL;DR

Karpathy’s LLM Wiki gist describes the right pattern but at the intent level: integrate new sources, lint periodically, treat the wiki as primary. It is a conceptual blueprint, not a runnable spec.

The gap between the gist and a working system is in the mechanics: how integration handles contradictions, how lint runs without you asking, and who the wiki is actually written for.

This rebuild fills in the spec on five axes: specified integration mechanics, automatic contradiction reconciliation, unsolicited synthesis, scheduled maintenance agents, and notes written for AI retrieval rather than human reading.

The most contrarian of the five is the AI-First Vault Principle: notes designed so future-Claude can read them in 10 seconds, not so future-you can re-read them in 30 minutes. Karpathy’s gist treats the wiki as serving both humans and LLMs; this rebuild inverts that.

The open-source implementation ships as a Claude Code skill with 31 slash commands and 4 scheduled agents.

## What is Karpathy’s LLM Wiki pattern?

Karpathy’s LLM Wiki is a knowledge-base pattern published as a public gist in early 2026. You drop sources into a folder. An LLM reads them, extracts entities and concepts into wiki pages, and cross-references everything. Future questions are answered from the wiki, not from a fresh web search.

The full pattern lives in Karpathy’s gist. The core insight is correct and important: the wiki is the product, the chat is just the interface. Cross-references already exist. Synthesis already reflects everything that has been read. Knowledge compounds like interest, instead of being regenerated from scratch every time you open a chat.

This was the right starting point. It is also where most implementations stop. As of 2026-04, every public Karpathy-Wiki implementation I have reviewed (six on GitHub, two on Substack, one on dev.to) treats the original gist as a complete spec. None of them solve the problems that show up the moment your wiki crosses a few hundred sources.

The AI Operator is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber.

Subscribe

## Why a conceptual blueprint is not a working second brain

Karpathy's pattern is append-only by design. Every ingest creates new pages and adds cross-references; existing pages stay frozen. This works for the first 50 to 100 sources. Past that, three failure modes compound: claims go stale, contradictions accumulate faster than you resolve them, and the cross-reference graph becomes too dense to navigate manually.

A wiki built this way is essentially a logbook with internal links. It captures what you read, but it does not update what you previously believed. If you ingest a YouTube video about a person who has changed jobs, you get a new source page with the new fact, plus a backlink on the person's existing page. The person's page itself still describes them at their old job. Future-Claude reading the page sees both, has no way to know which is current, and gives you a hedged answer.

The fix is structural. A real second brain has to rewrite, reconcile, synthesize, schedule, and rewrite-for-AI. Five extensions. Below.

## Five things a working second brain has to do that the original doesn't

### 1. Ingest has to rewrite, not just append

Real intelligence rewrites. When I ingest a YouTube video about someone already in my vault, the person’s page itself gets updated. Their startup status changes from “considering joining” to “joined in March 2026.” A thesis that was “speculation” becomes “confirmed.” The old version is preserved as a dated entry below, not deleted, but the live state of the page reflects the latest evidence.

This is the difference between a wiki that grows and a wiki that learns. Append-only knowledge bases get stale invisibly because nothing about reading them tells you that a fact is from 2024. Rewriting forces every page to carry the current best answer at the top.

### 2. Contradictions have to be resolved, not just flagged

Karpathy’s pattern flags contradictions during ingest. You resolve them manually. In a small wiki, that works. In a vault past a few hundred pages, contradictions accumulate faster than you have time to resolve. The wiki becomes internally inconsistent, and future-Claude pulling from it gets contradictory inputs and produces hedged outputs.

The fix is automatic reconciliation. A dedicated process scans the vault, finds claims that contradict each other across pages, and resolves them by source recency, source authority, and explicit confidence levels. The most recent, best-sourced, highest-confidence claim wins. The losing claim gets archived with an explanation of why it was superseded. The vault stays internally consistent without you babysitting it.

### 3. Patterns have to be surfaced without being asked

Karpathy’s wiki answers the questions you ask it. It cannot tell you about the patterns it has noticed and you have not. This is a massive missed opportunity. Hal