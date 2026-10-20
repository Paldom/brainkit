---
title: How the Open Knowledge Format can improve data sharing | Google Cloud Blog
url: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
final_url: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
source_type: social
providers: brave, exa, gemini, grok, kimi, tavily, site:exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:14+00:00
published: 2026-06-12
content_digest: 7c473fef1e9d0c6c
---

Jump to Content

Cloud

Blog

Contact sales Get started for free

Cloud

Blog

Solutions & technology
AI & Machine Learning

API Management

Application Development

Application Modernization

Chrome Enterprise

Compute

Containers & Kubernetes

Data Analytics

Databases

DevOps & SRE

Maps & Geospatial

Security
Security & Identity

Threat Intelligence

Infrastructure

Infrastructure Modernization

Networking

Productivity & Collaboration

SAP on Google Cloud

Storage & Data Transfer

Sustainability

Ecosystem
IT Leaders

Industries
Financial Services

Healthcare & Life Sciences

Manufacturing

Media & Entertainment

Public Sector

Retail

Supply Chain

Telecommunications

Partners

Startups & SMB

Training & Certifications

Inside Google Cloud

Google Cloud Next & Events

Google Cloud Consulting

Google Maps Platform

Google Workspace

Developers & Practitioners

Transform with Google Cloud

Contact sales Get started for free

Data Analytics

#
Introducing the Open Knowledge Format

June 12, 2026

Sam McVeety
Tech Lead, Data Analytics

Amir Hormati
Tech Lead, BigQuery, Engineering, Data Cloud

Try Gemini Enterprise today
The front door to AI in the workplace
Try now

As foundation models continue to improve, the lack of relevant context often limits what they can do, especially as they are used to build agentic systems. While these models can help you write code, summarize documents, or analyze a dataset, they still need the right information to produce accurate and actionable results.

That’s why today, we’re introducing the Open Knowledge Format (OKF), an open specification that formalizes the LLM-wiki pattern into a portable, interoperable format. This is a vendor-neutral, agent- and human-friendly standard for representing the metadata, context, and curated knowledge that modern AI systems need.

As published, OKF v0.1 represents knowledge as a directory of markdown files with YAML frontmatter, with a small set of agreed-upon conventions that let wikis written by different producers be consumed by different agents without translation.

That's it. No complex compression scheme, no new runtime, no required SDK. A bundle of OKF documents is:

Just markdown — readable in any editor, renderable on GitHub, indexable by any search tool

Just files — shippable as a tarball, hostable in any git repo, mountable on any filesystem

Just YAML frontmatter — for the small set of structured fields that need to be queryable: type, title, description, resource, tags, and timestamp

If you've used Obsidian, Notion, Hugo, or any of the LLM wiki patterns that have emerged over the past year, the shape will feel familiar. OKF formalizes the small set of conventions needed to make these patterns interoperable.

Let’s take a look at the problem that OKF can solve for your organization, how it works, how to get started with it, and what’s next.

### A fragmented context landscape

In most organizations, the information that foundation models use is overwhelmingly internal knowledge: the schema of a table, your business’ meaning of a metric, the runbook for an incident, the join paths between two systems, the deprecation notice for an old API, etc.

Today, these atoms of knowledge live in a variety of highly fragmented systems:

Metadata catalogs with their own APIs

Wikis, third-party systems, or in shared drives

Code comments, docstrings, or notebook cells

The heads of a few senior engineers

When an AI agent needs to answer "How do I compute weekly active users from our event stream?" it has to assemble the answer from these scattered, mutually incompatible surfaces. Every vendor offers its own catalog, its own SDK, its own knowledge-graph schema, and none of the knowledge is easily portable across products or organizations.

The result: Every agent builder is solving the same context-assembly problem from scratch, every catalog vendor is reinventing the same data models, and the knowledge itself is locked behind whichever surface created it.

### Knowledge as a living wiki

Developer teams are changing how they build AI agents. Instead of using models to search the same documents for the same facts over and over, you can give your agents a shared markdown library that grows more useful over time. This lets your agents take on the drudgery of reading and updating their own files, while your team curates the content and manages it like code.

Andrej Karpathy, the prominent AI researcher and educator, articulates this idea most crisply in his LLM Wiki gist. "LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass," he writes. The bookkeeping that causes humans to abandon personal wikis is exactly what LLMs are good at.

Similar knowledge-as-Wiki pattern keeps reappearing under different names: Obsidian vaults wired to coding agents, the AGENTS.md / CLAUDE.md family of convention files, repos full of index.md and log.md artifacts that agents consult before doing real work, and "metadata as code" repositories inside data teams.

The pattern is compelling and powerful, but each instance is bespoke. Karpathy's wiki and your team's wiki and a vendor's catalog export may all look alike (markdown, frontmatter, cross-links), but none of them are intentionally designed to cooperate. There is no agreed-upon answer to what fields every document should carry, or what filenames mean what. As a result, the knowledge encoded in wikis remains siloed within the original teams, leading to redundant effort whenever a new agent is built.

### What's missing is a format, not another service

The answer to this problem isn’t another knowledge service. You need a format, a way to represent knowledge that:

Anyone can produce, without an SDK

Anyone can consume, without an integration

Survives moving between systems, organizations, and tools

Lives in version control alongside the code it describes

Is readable by humans and parseable by agents: the same file, no translation layer

B