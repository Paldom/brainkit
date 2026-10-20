---
title: LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory
url: https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
final_url: https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
source_type: social
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:48+00:00
published: 2026-10-17
content_digest: 7322cde2e8c640c2
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

# rohitg00/llm-wiki.md

Forked from karpathy/llm-wiki.md

Last active
October 19, 2026 12:09

Show Gist options

Download ZIP

Star1,717(1,717)You must be signed in to star a gist

Fork240(240)You must be signed in to fork a gist

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

Clone this repository at &lt;script src=&quot;https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2.js&quot;&gt;&lt;/script&gt;

Save rohitg00/2067ab416f7bbe447c1977edaaa681e2 to your computer and use it in GitHub Desktop.

Code

Revisions
7
Stars
1,710
Forks
240

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

Clone this repository at &lt;script src=&quot;https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2.js&quot;&gt;&lt;/script&gt;

Save rohitg00/2067ab416f7bbe447c1977edaaa681e2 to your computer and use it in GitHub Desktop.

Download ZIP

LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory

Raw

llm-wiki.md

# LLM Wiki v2

A pattern for building personal knowledge bases using LLMs. Extended with lessons from building agentmemory 20K+ Stars ⭐️, a persistent memory engine for AI coding agents.

This builds on Andrej Karpathy's original LLM Wiki idea file. Everything in the original still applies. This document adds what we learned running the pattern in production: what breaks at scale, what's missing, and what separates a wiki that stays useful from one that rots.

## What the original gets right

The core insight is correct: stop re-deriving, start compiling. RAG retrieves and forgets. A wiki accumulates and compounds. The three-layer architecture (raw sources, wiki, schema) works. The operations (ingest, query, lint) cover the basics. If you haven't read the original, start there.

What follows is what we found after building and running this pattern across thousands of sessions.

## The missing layer: memory lifecycle

The original treats all wiki content as equally valid forever. In practice, knowledge has a lifecycle. A bug you discovered last week matters more than one from six months ago. A pattern you've seen twelve times is more reliable than one you've seen once. A claim from a newer source should weaken an older one automatically.

Confidence scoring. Every fact in the wiki should carry a confidence score: how many sources support it, how recently it was confirmed, whether anything contradicts it. When the LLM writes "Project X uses Redis for caching," that claim should know it came from two sources, was last confirmed three weeks ago, and sits at confidence 0.85. Confidence decays with time and strengthens with reinforcement. This turns the wiki from a flat collection of equally-weighted claims into a living model where the LLM can say "I'm fairly sure about X but less sure about Y."

Supersession. When new information contradicts or updates an existing claim, the old claim shouldn't just sit there with a note. The new one should explicitly supersede it. Linked, timestamped, old version preserved but marked stale. Version control for knowledge, not just for files.

Forgetting. Not everything should live forever. A wiki that never forgets becomes noisy. Implement a retention curve: facts that were important once but haven't been accessed or reinforced in months should gradually fade. Not deleted, but deprioritized. The LLM equivalent of moving something to a bottom drawer. Ebbinghaus's forgetting curve works well here: retention decays exponentially with time, but each reinforcement (access, confirmation from a new source) resets the curve. Architecture decisions decay slowly. Transient bugs decay fast.

Consolidation tiers. Raw observations aren't the same as established facts. Build a pipeline:

Working memory: recent observations, not yet processed

Episodic memory: session summaries, compressed from raw observations

Semantic memory: cross-session facts, consolidated from episodes

Procedural memory: workflows and patterns, extracted from repeated semantics

Each tier is more compressed, more confident, and longer-lived than the one below it. The LLM promotes information up the tiers as evidence accumulates. This is how you go from "I saw this once" to "this is how things work."

## Beyond flat pages: the knowledge graph

The original wiki is pages with wikilinks. That works, but you're leaving structure on the table. What you actually want is a typed knowledge graph layered on top of the pages.

Entity extraction. When the LLM ingests a source, it shouldn't just write prose. It should extract structured entities. People, projects, libraries, concepts, files, decisions. Each entity gets a type, attributes, and relationships to other entities. "React" is a library. "Auth migration" is a project. "Sarah" is a person who owns the auth migration and has opinions about React.

Typed relationships. Not all connections are equal. "uses," "depends on," "contradicts," "caused," "fixed," "supersedes" carry different semantic weight. A link that says "A relates to B" is less useful than "A caused B, confirmed by 3 sources, confidence 0.9."

Graph traversal for queries. When someone asks "what's the impact of upgrading Redis?", the LLM shouldn't just keyword-search. It should start at the Redis node, walk outward through "depends on" and "uses" edges, and find ever