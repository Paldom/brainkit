---
title: Open Knowledge Format (OKF)
url: https://www.dsebastien.net/open-knowledge-format-okf/
final_url: https://www.dsebastien.net/open-knowledge-format-okf/
source_type: social
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:32+00:00
published: 2026-06-20
content_digest: 7fc525af8f01b140
---

Sébastien Dubois

✨ Start Here

📰 News

📰 Articles

💌 Newsletter

🗒️ Notes

🧬 Community

🛒 Shop

👨‍💻 About

🧰 Projects

Now 🧭

Sign inSubscribe

news↻ Updated Jun 2026

# Open Knowledge Format (OKF)
In short
The Open Knowledge Format (OKF) is an open specification from Google Cloud for representing the metadata, context, and curated knowledge that AI systems need, in a portable, vendor-neutral, human- and agent-readable form. Version 0.1 shipped on 2026-06-12, authored by Sam McVeety and Amir Hormati of

#### Sebastien Dubois

17 Jun 2026· updated 20 Jun 2026— 4 min read

Share

### Sébastien Dubois

Organize your thoughts, life & work ⚡ AI, Personal Organization, LifeOS, Obsidian.
Subscribe

#### Go Further
MOST POPULARKnowii CommunityALL courses + tools + community + future workshopsLearn more →

#### Featured

➤
Knowii Voice AI 0.8.0 - Drop a File, Get the Text

➤
The Complete Guide to Obsidian Automation - From Templates to an AI Operating System

➤
The Complete Guide to Dataview in Obsidian - Query Everything, Then Make It Last

➤
The Complete Guide to the Obsidian CLI - Everything You Can Do From the Terminal

➤
The Complete Guide to Templates and Templater in Obsidian

📚 All Articles🏷️ All Topics🧵 Series

Canonical version: Open Knowledge Format (OKF).

The Open Knowledge Format (OKF) is an open specification from Google Cloud for representing the metadata, context, and curated knowledge that AI systems need, in a portable, vendor-neutral, human- and agent-readable form. Version 0.1 shipped on 2026-06-12, authored by Sam McVeety and Amir Hormati of the Google Cloud Data team. The interesting part for me: it is basically the Obsidian vault plus AGENTS.md pattern turned into a standard. Plain Markdown files with YAML frontmatter, living in Git, readable by a human with cat and by an LLM verbatim. If you already keep a knowledge base this way, you already speak most of OKF.

## Why it matters

Every agent builder is solving the same context-assembly problem from scratch, and every catalog vendor is reinventing the same data model. The knowledge itself stays locked behind whichever tool created it

OKF formalizes the "LLM wiki" pattern that emerged organically: Andrej Karpathy's LLM-wiki gist (April 2026, ~16M views), the AGENTS.md / CLAUDE.md convention used across 60,000+ open-source projects, and Obsidian vaults wired to coding agents

It picks the lowest-friction substrate that already exists (Markdown + frontmatter + Git) instead of inventing a new one. No JSON schema registry, no protobuf, no required SDK

## What it is

An open spec, not a product or platform. Apache 2.0, published in the GoogleCloudPlatform/knowledge-catalog repo

A format, deliberately. "Not tied to any specific cloud, database, model provider, or agent framework. It will never require a proprietary account or SDK"

v0.1 is small on purpose: ~451 lines, fits on one page. Explicitly "a starting point, not a finished standard," versioned for backward-compatible growth

## File format and structure

A bundle is a directory of UTF-8 Markdown files. Ship it as a tarball, host it in any repo, mount it from any filesystem

Example layout:
sales/
├── index.md # directory listing (reserved)
├── log.md # chronological history (reserved)
├── tables/
│ ├── index.md
│ ├── orders.md
│ └── customers.md
└── metrics/
└── weekly_active_users.md

Reserved filenames: index.md (a directory listing, for progressive disclosure) and log.md (chronological update history). Neither is a concept document

Each concept is one Markdown file with YAML frontmatter. The only required field is type (a producer-defined string consumers use for routing, filtering, presentation). Consumers must tolerate unknown types and preserve unknown fields

Recommended optional fields: title, description, resource (canonical URI for the underlying asset), tags, timestamp (ISO 8601)

Conventional body sections when applicable: # Schema, # Examples, # Citations

Relationships are Markdown links. A link from concept A to B asserts a directed, untyped edge, so a bundle is a graph, not just a folder tree. Broken links are tolerated

Conformance (v0.1): every non-reserved .md file has parseable YAML frontmatter; every frontmatter block has a non-empty type; reserved filenames follow their structures when present

Example concept document:
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, revenue]
timestamp: 2026-05-28T14:30:00Z
---
# Schema
| Column | Type | Description |
|--------|------|-------------|
| `order_id` | STRING | Globally unique order identifier. |
| `customer_id` | STRING | FK to [customers](/tables/customers.md). |

## Design principles

Minimally opinionated: OKF requires exactly one thing of every concept, a type field. Everything else is up to the producer

Producer / consumer independence: who writes the knowledge is cleanly separated from who consumes it

Format, not platform: no lock-in, no SDK, no account

## Why it improves data sharing

Human- and agent-readable: no SDK or query language between the reader and the content

Version-controllable out of the box: bundles live in Git, so pull requests, diffs, blame, and review just work. Knowledge curation becomes normal software engineering

Portable and lock-in free: a bundle is a directory

Structured where it helps, prose where it matters: frontmatter for the few fields you query or index on, Markdown body for the schemas, prose, and example queries humans and LLMs actually read

Composes with existing tools: Notion, Obsidian, MkDocs, Hugo, and Jekyll already speak Markdown plus YAML frontmatter

Progressive disclosure built in: auto-generated index.md files let an agent walk the hierarchy one level at a time instead of loading the whole bundle into context

Graph-shaped, via normal Markdown links between concepts

## Relationship to other standards

Complement