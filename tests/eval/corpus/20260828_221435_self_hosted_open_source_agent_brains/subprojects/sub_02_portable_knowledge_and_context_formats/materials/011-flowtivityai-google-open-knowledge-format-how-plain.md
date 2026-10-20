---
title: Google Open Knowledge Format: How Plain Markdown Files Are Becoming the Brain of AI Agents | Flowtivity
url: https://flowtivity.ai/blog/google-open-knowledge-format/
final_url: https://flowtivity.ai/blog/google-open-knowledge-format/
source_type: social
providers: brave, kimi
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:19+00:00
published: 2026-07-12
content_digest: c29039a596e27075
---

Flowtivity
HomeServicesPrivate AIMission ControlBlogCase StudiesFAQAbout

Contact Us

Back to Blog

Original

# Google Open Knowledge Format: How Plain Markdown Files Are Becoming the Brain of AI Agents

Google OKF is a plain markdown format for AI agent knowledge exchange. Implementation guide, competitive analysis, and practical business applications.

12 July 202614 min read

Last Updated: July 13, 2026

# Google's Open Knowledge Format: The Markdown Standard That Could Replace Your Wiki

Last Updated: June 13, 2026

Google just formalized the "digital brain" pattern — plain markdown files that AI agents can read, write, and share. Here's what it means for your business and why it matters more than you think.

## What Is the Open Knowledge Format (OKF)?

Answer: OKF is a plain markdown format standardized by Google for AI agent knowledge exchange. It uses simple markdown files with frontmatter conventions that agents can parse without special tools.

The Open Knowledge Format (OKF) is an open, vendor-neutral specification for storing organizational knowledge as a directory of markdown files with YAML frontmatter. Announced by Google Cloud on June 12, 2026, OKF gives AI agents a standardized way to read, write, and exchange knowledge without proprietary platforms, SDKs, or lock-in. Each "concept" is a single markdown file. Files interlink with normal markdown links, creating a living wiki that both humans and AI agents can navigate.

The format is deliberately minimal: one required field (type), optional metadata (title, description, resource, tags, timestamp), and a free-form markdown body. That's it. No database, no runtime, no API keys required to read it.

The key insight: OKF formalizes what teams were already doing ad hoc — using markdown + frontmatter as agent-readable knowledge bases — into something interoperable. Wikis written by different producers can now be consumed by different agents without translation.

Read the official spec on GitHub →

## Why OKF Matters Now

Answer: OKF matters because AI agents need standardized knowledge formats to interoperate. As agent ecosystems grow, a common format for knowledge exchange becomes critical infrastructure.

Organizational knowledge is catastrophically fragmented. The information that AI agents need lives in metadata catalogs with their own APIs, wikis behind login walls, code comments buried in repos, notebook cells, shared drives, and — worst of all — inside the heads of a few senior people.

When an AI agent needs to answer "How do we compute weekly active users from our event stream?", it has to assemble the answer from these scattered, mutually incompatible surfaces. Every agent builder solves the same context-assembly problem from scratch. Every catalog vendor reinvents the same data models. And the knowledge itself is locked behind whichever platform created it.

OKF breaks this pattern by being the lingua franca — a shared format that anyone can produce and anyone can consume. It's the USB-C cable of AI knowledge.

## How OKF Works: The 60-Second Tour

Answer: OKF uses standard markdown with structured frontmatter including title, description, tags, and relationships. Any markdown editor can create OKF-compatible files.

An OKF bundle is a directory of markdown files. Each file represents one "concept" — a table, an API endpoint, a metric, a playbook, anything you want to capture.

### File Structure
my_knowledge/
├── index.md # Directory listing (optional)
├── log.md # Update history (optional)
├── datasets/
│ ├── index.md
│ └── sales.md # A concept: "Sales Dataset"
└── tables/
├── orders.md # A concept: "Orders Table"
└── customers.md # A concept: "Customers Table"

### Each File Has Two Parts

YAML frontmatter for structured, queryable metadata:
---
type: BigQuery Table # REQUIRED — the only mandatory field
title: Customer Orders # Optional display name
description: One row per completed order
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
timestamp: 2026-05-28T14:30:00Z
---

Markdown body for everything else — schemas, examples, citations, prose:
# Schema

ColumnTypeDescription

order_idSTRINGGlobally unique order identifier

customer_idSTRINGFK to customers

total_usdNUMERICOrder total in US dollars

# Joins

Joined with customers on customer_id.

### Concepts Link to Each Other

Normal markdown links create a knowledge graph. The file system hierarchy gives you parent/child relationships. Cross-links add richer connections — joins, dependencies, references. A consumer agent can traverse this graph to build context.

### Reserved Filenames

Only two filenames have special meaning:

index.md — Directory listing for progressive disclosure (let agents see what's available before opening individual files)

log.md — Chronological update history

Everything else is a concept document.

## Three Design Principles That Make OKF Work

Answer: OKF is built on simplicity (plain markdown), interoperability (any agent can read it), and openness (no proprietary tools required). These principles ensure broad adoption.

### 1. Minimally Opinionated

OKF requires exactly one field: type. Everything else — what types exist, what other fields to include, what sections the body has — is left to the producer. The spec defines the interoperability surface, not the content model.

This means a data team can use OKF for table schemas while a DevOps team uses it for runbooks, and neither team has to coordinate on taxonomy. Their bundles can coexist in the same agent's context window.

### 2. Producer/Consumer Independence

This is the killer feature. OKF cleanly separates who writes knowledge from who consumes it:

A human-authored bundle → consumed by an AI agent

A pipeline-generated export → browsed by a human in a visualizer

A bundle written by one LLM → queried by a different LLM

The format is the contract. The tooling at each end is independently swappable. No vendor lock-