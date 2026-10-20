---
title: What is OKF? Understanding Google’s Open Knowledge Format | GitBook Blog
url: https://www.gitbook.com/blog/what-is-okf-open-knowledge-format
final_url: https://www.gitbook.com/blog/what-is-okf-open-knowledge-format
source_type: social
providers: brave, gemini
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:24+00:00
published: 2026-06-18
content_digest: db3a3ecc479ec8db
---

Product

Solutions

Resources

Pricing

Login

Book a demo

Start for free

Start for free

Login

Book a demo

Start for free

Industry

Published:

18 Jun, 2026

# What is OKF? Understanding Googleâs Open Knowledge Format

Steve Ashby

Content Lead

AI summary

Googleâs Open Knowledge Format (OKF) is an open, markdown-based specification designed to structure documentation into traversable knowledge graphs for AI agents, moving beyond the limitations of standard RAG systems. By adopting structured metadata, consistent cross-linking, and version-controlled markdown, documentation teams can make their knowledge agent-ready without needing to author a separate, proprietary format.

## TL;DR

The Open Knowledge Format (OKF) is a vendor-neutral, markdown-based open specification from Google Cloud that turns structured documentation into traversable knowledge. A bundle is a directory of markdown files with YAML frontmatter, cross-linked so an AI agent can traverse it deliberately instead of guessing.

This post explains what OKF is, why it changes how you think about docs, and what documentation teams should do about it now.

## The problem OKF is solving

AI agents read your knowledge badly because your knowledge lives everywhere and lacks consistency and structure. RAG chops documents into fragments and retrieves them by similarity, but the relationships between concepts often have to be inferred rather than explicitly represented. At the same time, Metadata catalogs describe the shape of your data behind their own APIs, but they say nothing about how a metric is computed or why a table exists.

Markdown dumps fix the fragmentation but reintroduce the chaos. A folder of .md files has no agreed convention for what a document is about, how documents link, or which fields an agent can query.

Plenty of teams already built around this gap. Andrej Karpathyâs LLM Wiki gist named the pattern, and AGENTS.md files, Obsidian vaults wired to coding agents, and âmetadata as codeâ repos all chase the same idea. Each one is bespoke. You have no standard way to hand structured knowledge to an agent, so every agent builder solves context assembly from scratch.

## What OKF actually is

OKF is an open specification from Google Cloud that defines how to package knowledge as a directory of markdown files with YAML frontmatter, cross-linked into a graph that AI agents can read. The v0.1 spec fits on a single page. It sets a small number of conventions so that a knowledge bundle written by one producer can be consumed by any agent without translation.

Itâs equally important to understand what OKF doesnât do. Itâs not a runtime, so you do not install anything to use it. Itâs not a search index, so it does not retrieve or rank fragments for you. Itâs not a model. Google puts it plainly: âWhatâs missing is a format, not another service.â

The format builds on the LLM-wiki pattern that developers had already started using. Karpathy described the idea in his LLM Wiki gist, and you have probably seen variations of it already in AGENTS.md files and Obsidian vaults wired to coding agents.

Each of those efforts stayed bespoke, with no shared rules for what fields a document carries or what filenames mean. OKF turns the pattern into a defined schema with a portability guarantee, so the same bundle works across tools, clouds, and agent frameworks.

## How an OKF bundle works

A bundle is a directory of markdown files where each file represents one concept. A concept can be a table, a dataset, a metric, a runbook, or an API endpoint.

For example, a SaaS company might represent its orders table, its âweekly active usersâ metric, and the runbook used to investigate billing failures as three separate concepts linked together through markdown references.

The file path becomes the conceptâs identity, so metrics/weekly_active_users.md is both the location and the address other documents point to.

Every file carries YAML frontmatter on top and a markdown body below. The frontmatter holds the queryable fields. OKF v0.1 reserves six of them.

---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: <https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders>
tags: [sales, revenue]

---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: <https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders>
tags: [sales, revenue]

---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: <https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders>
tags: [sales, revenue]

---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: <https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders>
tags: [sales, revenue]

Only type is required. The producer decides what types exist and what other fields each document carries, which keeps the spec minimally opinionated.

Concepts connect to each other with ordinary markdown links. A link from metrics/weekly_active_users.md to tables/orders.md turns a flat directory into a graph that captures relationships the filesystem alone cannot express. index.md files act as entry points and offer progressive disclosure. log.md files record chronological change history. Both are optional.

An agent navigates the bundle by reading an index.md, scoping to a topic, then following links the same way you would click through a wiki. Link resolution is just path resolution, so the agent traverses deliberately rather than guessing. No SDK, no runtime, and no proprietary schema sits between the agent and the files. You can ship the whole thing as a tarball, host it in a git repo, or mount it on a filesystem.

## OKF vs. RAG and metadata catalogs

Retrieval-augmented generation pulls fragments at query time. You embed your docs, store the vectors, and at runtime the system fetches the chunks 