---
title: Mem0 vs Zep vs Letta vs Cognee vs LangMem vs Mnemoverse: An Honest Map of Agent Memory in 2026 - DEV Community
url: https://dev.to/izgorodin/mem0-vs-zep-vs-letta-vs-cognee-vs-langmem-vs-mnemoverse-an-honest-map-of-agent-memory-in-2026-3l7b
final_url: https://dev.to/izgorodin/mem0-vs-zep-vs-letta-vs-cognee-vs-langmem-vs-mnemoverse-an-honest-map-of-agent-memory-in-2026-3l7b
source_type: social
providers: brave, exa, site:exa
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:11+00:00
published: 2026-08-12
content_digest: 4ec82ff4f656ee4e
---

Skip to content

Powered by Algolia

Log in

Create account

## DEV Community

Add reaction

Like

Unicorn

Exploding Head

Raised Hands

Fire

Jump to Comments

Save

Boost

Copy link
Copied to Clipboard

Share to X

Share to LinkedIn

Share to Facebook

Share to Mastodon

Report Abuse

Edward Izgorodin
Posted on Aug 10•Edited on Aug 12•Originally published at mnemoverse.com

#
Mem0 vs Zep vs Letta vs Cognee vs LangMem vs Mnemoverse: An Honest Map of Agent Memory in 2026

#ai#llm#opensource#tooling

The short answer up front: there is no best agent memory tool. These six projects solve genuinely different problems that happen to share the word "memory," and picking between them by star count or a leaderboard screenshot is how teams end up running a temporal knowledge graph to store "user prefers dark mode."

I am Edward, co-founder of Mnemoverse. One of the six tools below is mine, so read this whole piece knowing that. I have tried to handle the bias the way I would want a competitor to: my product gets one section among equals, and I tell you when not to pick it.

This is a map, not a ranking. For each tool: what it actually is, the job it wins, and when you should walk past it.

##
Mem0: extracted facts, open-source SDK, managed option

What it is: an Apache-2.0 open-source memory SDK with a managed cloud on top. Its core move is fact extraction: it distills conversations into discrete facts it can recall in later sessions.

The job it wins: adding a memory layer to a conversational product quickly, with an exit hatch. Because the SDK is open source, you can start on the managed cloud and move toward self-hosting if compliance or cost pushes you there. If "remember what the user told us and recall it next session" describes your need, this is a short path to it.

When not to pick it: when facts change over time and you need to know what was true when. Plain fact extraction flattens time; that job belongs to Zep. And if what you actually want is a structured graph over your documents rather than conversation-derived facts, look at Cognee.

##
Zep: facts with expiry dates

What it is: a managed memory service built on the open-source Graphiti temporal knowledge graph. The defining feature is that facts carry validity windows. The graph does not just know the customer's plan is Enterprise; it knows when that became true and when it stopped being true. The free tier is 10,000 credits a month.

The job it wins: any domain where state changes and history matters. Support agents, sales agents, anything touching accounts, subscriptions, or relationships. When an agent has to answer "what changed since last quarter," temporal validity is the actual feature, and Zep is honestly the tool I point people to for it.

When not to pick it: strict local-first or data-residency requirements. Graphiti is open source, but the managed service is what Zep sells. Also skip it if your memory needs are simple preferences and session context; a temporal graph is real machinery, and machinery you don't need is just operational surface.

##
Letta: the agent owns its memory

What it is: an Apache-2.0 agent framework in the MemGPT lineage. Memory here is not a sidecar service. Agents edit their own memory as a first-class behavior, rewriting what they know instead of delegating that to an external lookup.

The job it wins: building agents from scratch where memory management is part of the agent's cognition. If the MemGPT idea feels philosophically right to you, that the agent itself should curate what it remembers, Letta is the direct descendant of that idea and you should build inside it.

When not to pick it: when you already have an agent stack and just want memory bolted on. Letta is a framework, and adopting a framework to get a memory feature is a large trade that most existing codebases will not want to make.

##
Cognee: your graph, your infra

What it is: an Apache-2.0 framework that builds a knowledge graph on your own infrastructure through an extract-cognify-load pipeline. You feed it data, it constructs the graph, and everything stays inside your walls.

The job it wins: self-hosted knowledge graphs. If your security team's first question is "where does the data live" and the only acceptable answer is "our VPC," Cognee is designed for exactly you. It wins on data control the same way hosted services win on convenience.

When not to pick it: when nobody on the team wants to own a pipeline. Extract-cognify-load is yours to run, monitor, and evolve. If you want an API that just answers, a hosted service will cost you less in engineer-hours.

##
LangMem: memory that speaks LangGraph natively

What it is: LangChain's memory SDK, native to LangGraph's Long-term Memory Store, with storage in memory or in Postgres.

The job it wins: memory for teams already building on LangGraph. Native means no adapter layer and no impedance mismatch with your graph state, and Postgres persistence keeps operations boring. If your agents are LangGraph agents, LangMem is the honest default, and I say that as someone selling an alternative.

When not to pick it: outside the LangChain ecosystem. Its advantage is integration depth, and away from LangGraph that advantage evaporates. If your agents live in Claude Code, Cursor, or a custom stack, you take on the concepts without the payoff.

##
Mnemoverse: one memory across your tools (mine, so calibrate)

I build Mnemoverse. Read this section knowing that.

What it is: a hosted persistent-memory API that agents reach over MCP. All integrations reach the same account and memory, but authentication differs: the local MCP package and a Custom GPT action use an API key; compatible remote MCP clients use OAuth. The design bet is cognitive rather than graph-first: memories get an importance score on write; concepts form Hebbian associations tuned by a Rescorla-Wagner update; consolidation merges similar memories into prototypes while Von Restorff protection keeps distinctive ones from 