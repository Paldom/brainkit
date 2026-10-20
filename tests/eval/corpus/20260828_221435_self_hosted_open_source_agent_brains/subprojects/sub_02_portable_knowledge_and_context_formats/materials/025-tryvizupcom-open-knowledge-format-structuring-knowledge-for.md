---
title: Open Knowledge Format: Structuring Knowledge for AI Agents | Vizup
url: https://www.tryvizup.com/blog/open-knowledge-format-structuring-knowledge-for-ai-agents
final_url: https://www.tryvizup.com/blog/open-knowledge-format-structuring-knowledge-for-ai-agents
source_type: social
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:33+00:00
published: 2026-06-22
content_digest: 37e501c29507eea1
---

Vizup

Platform

How it Works

Resources

Book A Demo

Vizup

Platform

How it Works

Resources

Book A Demo

Vizup

Blog/Open Knowledge Format (OKF): How Brands Can Structure Knowledge for AI Agents

# Open Knowledge Format (OKF): How Brands Can Structure Knowledge for AI Agents

Anuraag Sharma·June 22, 2026

On this page

Why AI Agents Need a Special Diet

How the Open Knowledge Format Actually Works

What Google Shipped for v0.1

Where OKF Fits with llms.txt and ARD

Why OKF Matters for Brand Visibility

Should Your Team Adopt OKF in 2026?

Key Takeaways

Frequently Asked Questions

Get started

See how Vizup optimizes your organic visibility across search & AI surfaces.
Book a Demo

The Open Knowledge Format (OKF) is a vendor-neutral, open specification from Google Cloud for packaging organizational knowledge (datasets, metrics, APIs, runbooks) as a directory of markdown files with YAML frontmatter. The result is a cross-linked graph an AI agent can read, reason over, and act on. Introduced in June 2026 as OKF v0.1, the format puts a name and a structure on what many teams have already built informally: an LLM wiki.

Most companies' institutional brain is smeared across Notion pages, Confluence spaces, Google Docs, and proprietary catalogs. Each new agent you roll out ends up rebuilding the same context layer: what the canonical metric definition is, which endpoint is deprecated, which runbook applies in the EU. Google is pitching OKF as a single portable structure for that knowledge, aimed less at human browsing and more at the agents teams are starting to rely on. Here's a practical look at how OKF is put together, what Google actually shipped, and how to decide if it's worth adopting.

## Why AI Agents Need a Special Diet

AI agents can execute tasks, but they're notoriously bad at "just knowing" how your organization works. They don't come with the institutional memory a tenured employee has: which metric definition is canonical, which API endpoint is deprecated, which runbook applies to the EU region. Meanwhile, the knowledge they need lives in unstructured docs or locked inside proprietary systems, so every agent ends up with bespoke plumbing to fetch the right context. If you want a concrete example, what an SEO agent is makes the limitation obvious: even a strong agent is capped by the knowledge it can reliably access.

And the tax shows up over and over. A data team builds a connector for one agent; a support team builds another for a different agent; nobody wants to maintain any of it. OKF's pitch is to pay that cost once: give producers a shared format and give consumers a predictable structure. In the spec's language, it's the agent context standard pattern: write knowledge once, let any agent consume it.

## How the Open Knowledge Format Actually Works

OKF is not a platform or a SaaS product. It is a set of conventions for organizing files you probably already have. The building blocks are intentionally plain: directories, markdown files, and YAML frontmatter. If you have seen the LLM wiki pattern, this is the standardized version: maintain interlinked markdown that an agent can read and update, as detailed in the official spec on GitHub.

Architecture diagram of an Open Knowledge Format bundle showing document structure and cross-linksIn OKF, every concept is a document (tree); related documents group into a bundle (forest) connected by markdown cross-links.

### The Anatomy of an OKF Bundle

In OKF, a single concept (a specific dataset, a metric definition, an API endpoint) becomes a document, which Google calls a "tree." Each tree is a directory with a primary markdown file plus any related assets. Group a set of related documents together and you have a bundle, or "forest." Documents connect to each other using standard markdown links, which is enough to produce a navigable knowledge graph without proprietary tooling.

The YAML frontmatter is intentionally sparse. Only one field is mandatory: type. Reserved (but optional) fields include title, description, resource, tags, and timestamp. Two optional files fill in the practical edges: index.md for progressive disclosure (summaries that help agents decide whether to read deeper) and log.md for change history. The official spec on GitHub is explicit that this minimalism is a feature, not an omission.

### Three Design Principles Worth Noting

Minimally opinionated. With only type required, the on-ramp is basically "make a markdown file." Teams can start from whatever documentation they already have.

Producer/consumer independence. The team writing the knowledge doesn't need to predict which agent will consume it, and the agent doesn't need to care who authored it. That decoupling is what gives OKF its portability.

Format, not platform. There's no proprietary SDK to read or write OKF. Any text editor, any CI pipeline, and any agent framework that can handle files can work with it.

## What Google Shipped for v0.1

Google is careful to frame v0.1 as "a starting point, not a finished standard." The goal is to pull in feedback, not to declare OKF the one true way to do knowledge management. Still, this isn't just a PDF spec: Google shipped working code alongside it.

The reference producer is a BigQuery enrichment agent that generates OKF documentation for datasets by turning schema metadata into structured markdown. The reference consumer is a static HTML visualizer that renders an OKF bundle as a browsable site, which is handy for human review and debugging. Google also published sample bundles on GitHub. For Google Cloud customers, the most immediate hook is the Knowledge Catalog OKF integration: Knowledge Catalog can ingest OKF bundles directly, which gives data teams a concrete reason to start producing them now.

Info: Google has framed OKF as an agent-knowledge and data-sharing format, not as an SEO ranking tactic. Whether it matters outside Google Cloud depends on what the broader community does with it.

## Whe