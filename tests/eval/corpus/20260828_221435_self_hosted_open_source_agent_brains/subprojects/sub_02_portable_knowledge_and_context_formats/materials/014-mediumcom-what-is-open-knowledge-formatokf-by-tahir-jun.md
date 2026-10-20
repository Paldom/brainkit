---
title: What is Open Knowledge Format(OKF)? | by Tahir | Jun, 2026 | Medium
url: https://medium.com/@tahirbalarabe2/what-is-open-knowledge-format-okf-270b20791802
final_url: https://medium.com/@tahirbalarabe2/what-is-open-knowledge-format-okf-270b20791802
source_type: social
providers: brave, kimi, tavily
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:21+00:00
published: 2026-06-30
content_digest: d884fe4b78e50d3f
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

The Pattern That Actually Works

A Format, Not Another Service

Why Simple Wins

What a Bundle Looks Like

Three Principles
Minimally Opinionated

Producer and Consumer Independence

Format, Not Platform

What the Team Is Shipping

Enrichment Agent

Static HTML Visualizer

Sample Bundles

Where the Effort Goes From Here

How the Community Can Participate

The Bottom Line

Further Reading:

OKF Frequently Asked Questions
1. What is the Open Knowledge Format (OKF)?

2. Why was OKF created?

3. What does an OKF bundle actually look like?

4. What are the required fields in an OKF document?

5. Do I need a special SDK or account to use OKF?

6. How is OKF different from a typical knowledge catalog?

7. Can humans read and edit OKF files directly?

8. What is Google Cloud shipping with OKF?

9. How can I get started with OKF?

10. Is OKF a finished standard?

Open Knowledge Format

Okf Specification

Ai Knowledge Format

Llm Context Management

Agent Knowledge Base

# What is Open Knowledge Format(OKF)?

Tahir

8 min read
·
Jun 30, 2026

--

Listen

Share

Press enter or click to view image in full size

Shoutout to Google Cloud Data Cloud

TLDR:Open Knowledge Format is a vendor-neutral open spec for AI context. Use markdown and YAML to build portable interoperable agent knowledge bases.

Read the following first:

What is LLM Wiki Pattern? Persistent Knowledge with LLM Wikis

Automate AI Second Brain(LLM Wiki Pattern) With Claude Code and Obsidian

Build an AI Second Brain(LLM Wiki Pattern) With Claude Code and Obsidian

The feeling of having all the information needed but finding it scattered across ten different places is familiar to anyone working with AI agents today. These systems have access to everything, yet they struggle to find anything useful.

The Google Cloud Data Team has observed this problem up close. Every team building with AI runs into the same wall. The models get smarter every month, but they still need the right context to be useful. That context is scattered across catalogs, wikis, code comments, and the heads of a few senior engineers.

The usual solution is to build another service. Another catalog. Another knowledge graph. Another API. But that just adds to the pile. Organizations end up with more systems, not less fragmentation.

## The Pattern That Actually Works

A different approach is starting to emerge. Teams are discovering that the best way to give AI agents context is a wiki. Not a fancy one with databases and search indexes. Just files. Markdown files that humans can read and agents can parse.

The LLM wiki pattern, as Andrej Karpathy calls it, works because LLMs do not get bored. They do not forget to update cross-references. They can touch fifteen files in one pass. The bookkeeping that makes humans abandon personal wikis is exactly what LLMs are good at.

But there is a problem. Every instance of this pattern is bespoke. One team’s wiki and another team’s wiki look alike, but they do not cooperate. There is no agreement on what fields every document should carry, or what filenames mean what. The knowledge stays siloed. Each new agent has to solve the same context-assembly problem from scratch.

## A Format, Not Another Service

The Google Cloud Data Team is introducing the Open Knowledge Format. It is a specification that formalizes the LLM wiki pattern into something portable and interoperable. Vendor neutral. Agent friendly. Human readable.

The format itself is almost boringly simple. An OKF bundle is a directory of markdown files with YAML frontmatter. That is it.

No complex compression scheme

No new runtime

No required SDK

Every concept gets one file. The file path is its identity. The frontmatter carries a small set of structured fields:

Type

Title

Description

Resource

Tags

Timestamp

The body is markdown. Concepts link to each other with normal markdown links. The whole spec fits on a single page.

The initial reaction is often that this is too simple to work. But that is exactly the point.

## Why Simple Wins

The complexity in knowledge systems comes from the integration, not the representation. Every vendor offers its own catalog with its own API and its own data model. None of the knowledge is portable. None of it works across products or organizations.

A format solves a different problem. Anyone can produce OKF without an SDK. Anyone can consume it without an integration. It survives moving between systems. It lives in version control alongside the code it describes. It is readable by humans and parseable by agents, using the same file for both.

## What a Bundle Looks Like

Here is the shape of a real OKF bundle:
sales/

├── index.md

├── datasets/

│ ├── index.md

│ └── orders_db.md

├── tables/

│ ├── index.md

│ ├── orders.md

│ └── customers.md

└── metrics/

├── index.md

└── weekly_active_users.md
Each concept document has a small block of YAML frontmatter for structured fields and a markdown body for everything else:
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

|---------------|-----------|------------------------------------------|

| `order_id` | STRING | Globally unique order identifier. |

| `customer_id` | STRING | FK to [customers](/tables/customers.md). |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.
The links between concepts turn the directory into a graph of relationships richer than the parent-child links implied by the file system.

## Three Principles

### Minimally Opinionated

The format requires exactly one thing of every concept: a type field. Everything else is left to the producer. The spec defines the interoperability surface, not the content model.

### Producer and 