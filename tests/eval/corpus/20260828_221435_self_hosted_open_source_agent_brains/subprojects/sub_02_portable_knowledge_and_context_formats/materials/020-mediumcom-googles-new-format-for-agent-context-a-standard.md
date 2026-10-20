---
title: Google’s New Format for Agent Context: A Standard, or Just a Folder? | by Marc Bara | Medium
url: https://medium.com/@marc.bara.iniesta/googles-new-format-for-agent-context-a-standard-or-just-a-folder-82fb21d92041
final_url: https://medium.com/@marc.bara.iniesta/googles-new-format-for-agent-context-a-standard-or-just-a-folder-82fb21d92041
source_type: social
providers: brave, tavily
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:28+00:00
published: 2026-06-15
content_digest: 2f1ea414b8d8fcd4
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

What v0.1 actually pins down

What v0.1 deliberately leaves open

Where it sits among the alternatives

The layer it names

AI Agent

Artificial Intelligence

Google

Technology

# Google’s New Format for Agent Context: A Standard, or Just a Folder?

## Released this week, OKF gives AI agents a portable way to read shared knowledge as plain markdown. Its v0.1 standardizes the files, not yet what they mean.

Marc Bara

4 min read
·
Jun 15, 2026

--

2

Listen

Share

Press enter or click to view image in full size

Image: screenshot of Google Cloud’s announcement post header, “Introducing the Open Knowledge Format.” Caption: Google introduced OKF on June 12, 2026, in a post by two tech leads from its Data Cloud team
Google’s Open Knowledge Format, or OKF, wants to be the common language for the knowledge that AI agents read, the table definitions, metric formulas, and runbooks a model needs but rarely has. Google frames it as a vendor-neutral standard for interoperable knowledge. The useful distinction in version 0.1 is between structural interoperability and semantic interoperability. OKF clearly advances the first. It mostly leaves the second to producers, consumers, and future conventions. What the specification actually fixes is a folder layout, markdown files, YAML frontmatter, two reserved filenames, and a single required field. That is useful, and it may be the right place to start. It is also a smaller claim than interoperable knowledge, and the distance between the two is the most interesting thing about the release.

## What v0.1 actually pins down

OKF standardizes a container. A bundle is a directory of markdown files where each file is one concept and its path is its identifier. Each file opens with a YAML block whose only required field is type, followed by a markdown body. Files reference each other with ordinary links, which makes the directory a graph rather than a flat list, and two filenames are reserved, index.md for a listing and log.md for a change history. The spec is short for a spec at 451 lines, even if Google's "single page" framing is more rhetorical than literal.

Two reference tools come with it: a producer built on Google’s Agent Development Kit and the Gemini model that reads a BigQuery dataset and writes one file per table, and a viewer that renders any bundle as a self-contained interactive HTML page. This is where the vendor-neutral framing deserves a caveat. Google does say the format is open and not tied to any model provider or serving system, and that is true of the file format. But the reference implementation is still Google-shaped: the producer uses Gemini, the demonstrated source is BigQuery, and Google’s own Knowledge Catalog is the obvious ingestion path, so the gravity of the ecosystem is still Google Cloud even when the license is not.

## What v0.1 deliberately leaves open

The spec standardizes almost nothing about semantics, and it says so on purpose. Only type is required, and type values are not registered anywhere, so one producer writes BigQuery Table and another writes table for the same thing. Links are untyped: a link asserts that two concepts are related but not how. Consumers are instructed to tolerate unknown types and even broken links. There is no schema registry and no taxonomy of concept types.

The consequence is direct. Two bundles can each be fully conformant and still share no common vocabulary, which means an agent built to read one may get little from the other. The container is standardized; the meaning is left to each producer. A smaller detail points the same way. The spec says one field is required, but Google’s own reference parser rejects any file missing four of them, type, title, description, and timestamp. Even the required surface of the container is not fully settled at v0.1, which is fair for a draft but worth knowing before you treat conformance as a guarantee of anything.

## Where it sits among the alternatives

OKF is easier to place by comparing it one alternative at a time than by lining everything up on a single axis, because the things it resembles resemble it for different reasons.

Press enter or click to view image in full size

The Obsidian comparison is worth getting right, because Obsidian already stores notes as plain markdown files you own, so portability is not what separates it from OKF. Purpose is. Notion is the better example of knowledge trapped inside a product, even though it can export markdown. AGENTS.md, released by OpenAI in August 2025 and now used by more than 60,000 projects, is the nearest convention by shape, but it tells a coding agent how to behave in a repository rather than describing a body of data. The catalogs are the nearest by function, and they already solve problems OKF does not touch.

## The layer it names

OKF is worth watching less for technical depth than for naming a layer the agent ecosystem was missing: a portable context package you can hand to an agent without building a custom integration. None of this is a defect in a one-day-old v0.1 draft. It may be the right first move: standardize the package before arguing about the vocabulary. But it matters because “interoperable knowledge” can mean two different things. OKF already gives agents a shared way to find and read context. It does not yet give them shared semantics for what that context means. Closing that gap is what later versions are for: adding registered types, link vocabularies, or declared profiles so an agent can read another team’s bundle and actually understand it. Until then, OKF is a shared way to store context, not yet a shared way to make sense of it.

Marc Bara is a project management consultant and educator with a PhD in Electrical Engineering. He writes about AI, work, and project management. Find him on LinkedIn.

AI Agent

Artificial Intelligence

Google

Technology

--

--

2

## Written by Marc Bara

