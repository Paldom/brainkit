---
title: Google Cloud's Open Knowledge Format Is a Standard, Not a Product: A Deep Dive Into OKF v0.1 · typescript.news
url: https://typescript.news/articles/2026-06-17-google-cloud-okf-open-knowledge-format-deep-dive
final_url: https://typescript.news/articles/2026-06-17-google-cloud-okf-open-knowledge-format-deep-dive
source_type: social
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:31+00:00
published: 2026-06-17
content_digest: 5771748c56f9ac26
---

typescript.news

Home

Articles

About

Topics

🇺🇸English

aitoolingecosystem

# Google Cloud's Open Knowledge Format Is a Standard, Not a Product: A Deep Dive Into OKF v0.1

lschvnJune 17, 2026

## TL;DR

•OKF v0.1 was published on June 12, 2026 in the GoogleCloudPlatform/knowledge-catalog repo (Apache-2.0, currently 3.3k stars) and promoted via a Google Cloud Tech tweet on June 16. The spec is a directory of markdown files with YAML frontmatter, one required field (type), five recommended ones (title, description, resource, tags, timestamp), and two reserved filenames (index.md, log.md). There is no schema registry, no central authority, and no required SDK.

•The 'LLM-wiki pattern' OKF formalizes is the same pattern that has been reappearing under different names for a year: Karpathy's LLM Wiki gist, Obsidian vaults wired to coding agents, the AGENTS.md / CLAUDE.md family of convention files, repos full of index.md and log.md artifacts that agents consult, and 'metadata as code' repositories inside data teams. OKF pins down the small set of conventions needed to make these instances interoperable without dictating tooling.

•Google shipped four reference artifacts in the same release: an enrichment agent built on the Google Agent Development Kit with Gemini as the backend, a static HTML visualizer that renders any OKF bundle as a self-contained interactive force-directed graph, three sample bundles (GA4 e-commerce, Stack Overflow, Bitcoin public datasets), and a BigQuery Knowledge Catalog integration that ingests OKF natively. The format is the contribution; the tools are proofs of concept.

•What changes for builders: the BigQuery Knowledge Catalog can now serve a corpus of OKF markdown to agents, which means the spec is not just a format for wikis, it is also a data-catalog export format, and the export target is the place where the most important enterprise knowledge about SQL tables, metrics, and runbooks actually lives. The interesting strategic question is whether OKF becomes the lingua franca, or whether a competing spec emerges in the next six months.

On the evening of June 16, 2026, the Google Cloud Tech account posted a single tweet that drove 117,000 views, 1,800 likes, and 1,800 bookmarks in 24 hours, the highest-engagement knowledge-format announcement of the year by an order of magnitude. The tweet introduced the Open Knowledge Format (OKF), an open specification that "formalizes the LLM-wiki pattern into a portable, interoperable format." The post linked to the spec on GitHub and to a blog post on cloud.google.com by Sam McVeety (Tech Lead, Data Analytics) and Amir Hormati (Tech Lead, BigQuery). The blog post was published four days before the tweet, on June 12, the same day the reference implementation was first pushed to the GoogleCloudPlatform/knowledge-catalog repository.

@GoogleCloudTech - 22:34 · 16 juin 2026

Introducing the Open Knowledge Format (OKF), an open specification that formalizes the LLM-wiki pattern into a portable, interoperable format. AI is only as smart as the context we give it. As we build more advanced, agentic AI systems, they need accurate metadata and context to organizations, that context is locked inside fragmented data catalogs, isolated wikis, scattered code comments, or the minds of senior engineers. Every time a new AI agent is built, teams are forced to solve the exact same context-assembly problem from scratch.

To solve this, we've announced OKF, a vendor-neutral, open specification that formalizes the "LLM-wiki pattern" into a portable, interoperable format. It provides a standardized way to represent the enterprise knowledge that modern AI systems rely on.

Just markdown: readable in any editor, renderable on GitHub, indexable by any search tool.

Just files: shippable as a tarball, hostable in any git repo, mountable on any filesystem.

Just YAML frontmatter: for the small set of structured fields that need to be queryable: type, title, description, resource, tags, and timestamp.

We've also shipped reference implementations to help you hit the ground running, including an enrichment agent for BigQuery, a static HTML visualizer, and live sample bundles on GitHub.

The substance of the announcement is best understood as four distinct moves: the spec itself, the reference implementations, the BigQuery integration, and the positioning move. Each is doing a different job. The spec is a 1,000-line document that defines a directory of markdown files with YAML frontmatter, one required field, and two reserved filenames. The reference implementations are three artifacts: a BigQuery enrichment agent, a static HTML visualizer, and three sample bundles. The BigQuery integration is a native ingest path in the Knowledge Catalog that turns an OKF bundle into a queryable, agent-servable surface. The positioning move is the claim that the LLM-wiki pattern is a category, not a one-off, and that the format is the contribution, not the tooling.

## The framing correction, in one paragraph

The framing worth making up front is that OKF is a format, not a product, and that the most common misreading of the announcement is to treat it as a Google Cloud product launch. The spec text never mentions BigQuery, Gemini, or any Google product. The reference implementations are deliberately called "proofs of concept" in the README, and the spec's "Relationship to other formats" section (SPEC.md §10) is explicit that OKF is downstream of patterns the community has been building for at least a year: Karpathy's LLM Wiki gist, Obsidian vaults wired to coding agents, the AGENTS.md and CLAUDE.md family of convention files, and the "metadata as code" repositories inside data teams. What Google has done, in the cleanest reading, is pin down the small set of conventions that lets these instances cooperate, publish the pin-down under Apache-2.0, and ship one reference implementation per end of the producer/consumer axis. The lock-in question is the one the spec is d