---
title: Open Knowledge Format (OKF): Google AI Agent Standard | explainx.ai Blog | explainx.ai
url: https://explainx.ai/blog/google-open-knowledge-format-okf-ai-agents-2026
final_url: https://explainx.ai/blog/google-open-knowledge-format-okf-ai-agents-2026
source_type: social
providers: brave, exa, kimi
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:21+00:00
published: 2026-06-14
content_digest: a6f9cbdd52f56f15
---

explainx.ainewsletter3.5k

TrendingNewsPathwaysSkills
Explore
Pricing

explainx.ai
Upskill in AI — 16 free pathways, live workshops & bootcamps, and 50+ courses from practitioners. Plus the skills, tools, and MCP servers to practice on.

follow us

corporate training
support@explainx.ai

get started

Find your pathTake Free Evaluation

learn

pathways — start freeworkshopsbootcampscoursescertificationsmock testsexplainx universitycorporate traininglearn skills & mcp

discover

skillsmcp serversexplainx mcptoolsagentsllmsdesignsdictionaryagi trackerranks

company

aboutvisionmissionteaminstructorscommunityhackathonscareers

content

daily AI newsstate of AI — live resultsblogreleasespromptsgeneratorsresource libraryfor LLMsexplainx.ai kids

solutions

all solutionsdeveloper upskillingmarketing upskillingproduct manager upskillingleadership upskilling

newsletter · weekly

Get AI news, tools, and insights in your inbox.

Email for skill picks newsletterSubscribe

supportcontactprivacytermsdata rightshow we create contentsubmission guidelines

© 2026 AISOLO Technologies Pvt Ltd

sharebookmark

On this page

TL;DR

The Problem OKF Solves

What an OKF Bundle Looks Like

Three Design Principles

OKF vs Existing Patterns

What Google Shipped

The Karpathy Connection

Getting Started

Open Questions (v0.1 Is a Starting Point)

Who Should Care

Summary

Related Reading

← Back to blog
explainx / blog

# Open Knowledge Format (OKF): Google's Standard for AI Agent Memory

Google Cloud launched Open Knowledge Format (OKF) v0.1—a vendor-neutral spec for AI agent knowledge as markdown + YAML frontmatter. How it works, vs CLAUDE.md, Karpathy LLM wiki, and sample bundles on GitHub.

Jun 14, 2026·8 min read·Yash Thakker

Google CloudOpen Knowledge FormatAI AgentsAgent MemoryBigQueryStandards

copy for llmcopy text
explain with melofocus readsharego deep

On June 12, 2026, Google Cloud published the Open Knowledge Format (OKF) v0.1—an open specification that turns the emergent "LLM wiki" pattern into a portable standard for AI agent knowledge.

Sam McVeety (Tech Lead, Data Analytics) and Amir Hormati (Tech Lead, BigQuery) announced on the Google Cloud Blog:

OKF is a vendor-neutral, agent- and human-friendly standard for representing the metadata, context, and curated knowledge that modern AI systems need.

No new runtime. No required SDK. Just markdown files with YAML frontmatter in a directory—shippable in git, readable on GitHub, consumable by any agent.

@Karpathy's LLM Wiki gist (5,000+ stars) predicted this shape; Google formalized the interoperability layer. See our complete LLM Wiki guide. @DataChaz called it Google formalizing "the power of the LLM Wiki."

This post explains OKF's structure, design principles, what Google shipped, and how it fits alongside CLAUDE.md and agent skills.

Weekly digest3.5k readers

Catch up on AI

Curated AI updates on agents, skills, and MCP — delivered to your inbox. Unsubscribe anytime.

Leave blank

Email for explainx.ai newsletterSubscribe

## TL;DR

table · 2 colsCopy

QuestionAnswer

WhatOpen spec for agent knowledge as markdown + YAML files

Required fieldtype in frontmatter (only mandatory field)

Optional fieldstitle, description, resource, tags, timestamp

LinksStandard markdown cross-links → knowledge graph

Versionv0.1 (June 2026)

Spec repoGoogleCloudPlatform/knowledge-catalog → okf/SPEC.md

Reference toolsBigQuery enrichment agent + static HTML visualizer

SamplesGA4 e-commerce, Stack Overflow, Bitcoin datasets

## The Problem OKF Solves

Foundation models improve faster than most organizations can assemble context. When an agent needs to answer "How do we compute weekly active users from our event stream?", the answer fragments across:

table · 2 colsCopy

SurfaceExample content

Metadata catalogsTable schemas (vendor-specific APIs)

Wikis / NotionRunbooks, metric definitions

CodeDocstrings, notebook comments

People's headsJoin paths, deprecation notices

Every agent builder re-solves the same context assembly problem. Every catalog vendor reinvents schemas. Knowledge stays locked to the surface that created it.

OKF's bet: the missing piece is a format, not another platform.

## What an OKF Bundle Looks Like

An OKF bundle is a directory of concept documents. File path = concept identity:

snippetCopy
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

Each concept file:

markdownCopy
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, revenue]
timestamp: 2026-05-28T14:30:00Z
---# Schema

| Column | Type | Description |
|---------------|--------|------------------------------------------|
| `order_id` | STRING | Globally unique order identifier. |
| `customer_id` | STRING | FK to [customers](/tables/customers.md). |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.

Markdown links turn the directory into a graph richer than filesystem hierarchy alone.

### Reserved files

table · 2 colsCopy

FilePurpose

index.mdProgressive disclosure as agents navigate

log.mdChronological change history

The full v0.1 spec—including conformance criteria—fits on one page.

## Three Design Principles

### 1. Minimally opinionated

Only type is required. What types exist, what other fields to use, what body sections to include—producer's choice. OKF defines interoperability, not content models.

### 2. Producer/consumer independence

table · 2 colsCopy

ProducerConsumer

Human-authored wikiAI agent

BigQuery export pipelineHTML visualizer

LLM-generated bundleSearch index

Same format, swappable tooling at each end.

### 3. Format, not platform

No proprietary account or SDK required to read or write. Value scales with adoption breadth, not vendor lock-in.

## OKF vs Existing Patterns

