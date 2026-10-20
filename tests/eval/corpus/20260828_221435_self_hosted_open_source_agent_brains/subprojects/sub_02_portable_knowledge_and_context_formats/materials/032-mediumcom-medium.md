---
title: Medium
url: https://medium.com/@piyushrajyadav28/google-quietly-released-a-standard-for-how-ai-agents-should-read-your-companys-knowledge-9e780b476648
final_url: https://medium.com/@piyushrajyadav28/google-quietly-released-a-standard-for-how-ai-agents-should-read-your-companys-knowledge-9e780b476648
source_type: social
providers: exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:39+00:00
published: 2026-06-30T00:00:00.000Z
content_digest: 2185846232e2d9d8
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

Inside the Open Knowledge Format (OKF) — and why it might matter more than the announcement suggests

The problem OKF is trying to solve

What OKF actually is

Why “just markdown” is the point, not a limitation

Where the spec stops short

Should you build on it?

## Piyush Yadav

casually building for the next billion people

AI

AI Agent

Software Development

Software Engineering

Artificial Intelligence

# Google Quietly Released a Standard for How AI Agents Should Read Your Company’s Knowledge

Piyush Yadav

5 min read
·
Jun 30, 2026

--

Listen

Share

## Inside the Open Knowledge Format (OKF) — and why it might matter more than the announcement suggests

Press enter or click to view image in full size

On June 12, 2026, two Google Cloud tech leads, Sam McVeety and Amir Hormati, published a blog post introducing something called the Open Knowledge Format, or OKF. No flashy product launch, no keynote moment — just a spec, a GitHub repo, and a few reference tools.

It’s easy to scroll past announcements like this. But this one is worth a closer look, because it’s trying to fix a problem almost every team building AI agents has run into and quietly worked around in their own way.

## The problem OKF is trying to solve

Foundation models are good at reasoning. What they’re not good at is knowing anything specific about your organization — what your “active_users” metric actually measures, which database table is the real source of truth, or the operational knowledge that exists only in a senior engineer’s head.

Every time a new agent gets built, someone has to solve this from scratch: scrape the wiki, export the catalog, write a custom retrieval pipeline, hope it stays up to date. Google’s framing is direct about this — the context an agent needs is usually locked inside fragmented data catalogs, isolated wikis, and scattered code comments, and every new agent ends up re-solving the same assembly problem.

This pattern already had a name circulating in AI engineering circles: the “LLM-wiki” pattern, popularized by an Andrej Karpathy gist about markdown libraries that agents read, update, and maintain themselves. Teams had been building informal versions of this everywhere — AGENTS.md files, CLAUDE.md files, Obsidian vaults wired into coding agents, folders of index.md and log.md that agents consult before acting. OKF is Google's attempt to take that pattern and give it one agreed-upon shape, so these stop being a hundred incompatible reinventions of the same idea.

## What OKF actually is

Strip the spec down and it’s refreshingly unglamorous: a directory of markdown files with YAML frontmatter.

Each file represents one “concept” — a table, a metric, an API, a process — and its file path doubles as its identifier. Every file opens with a small YAML block, and the only field that’s actually required is type. Everything else is optional: title, description, resource, tags, timestamp. Below the frontmatter is a normal markdown body that any human can read.

Files link to each other with ordinary markdown links, which turns a flat folder into a navigable graph. Two filenames are reserved for structure: index.md for a directory listing, and log.md for a change history.

That’s the entire spec. No compression scheme, no new runtime, no required SDK. A bundle of OKF files is, in Google’s own words, “just markdown” — readable in any editor, renderable on GitHub — and “just files,” shippable as a tarball or stored in any git repo.

Google also shipped reference tooling alongside the spec: a producer agent (built on Google’s Agent Development Kit and Gemini) that walks a BigQuery dataset and drafts one OKF concept file per table, and a static HTML visualizer that turns any bundle into an interactive graph view, no backend required. Three sample bundles were published too, covering GA4 e-commerce data, Stack Overflow data, and Bitcoin datasets. The whole thing is published on GitHub under the Apache 2.0 license.

## Why “just markdown” is the point, not a limitation

It’s tempting to dismiss OKF as nothing new — developers have organized documentation as markdown-plus-metadata for years, and some early critics have said exactly that. But the value proposition was never about inventing a new file format. It’s about agreement.

The real cost in agent tooling right now isn’t a lack of formats — it’s that everyone’s format is slightly different, so every producer-consumer pair needs custom glue code. If a knowledge bundle authored by one team, or generated automatically by one company’s pipeline, can be read directly by a completely different agent without translation, that’s the actual unlock. The format is deliberately boring so that adoption friction stays near zero: anyone who already knows markdown, git, and YAML is already most of the way to being OKF-conformant.

## Where the spec stops short

Version 0.1 solves structural interoperability — where files live, what they’re named, what shape the metadata takes. It does not solve semantic interoperability — what the content actually means.

Since type is the only required field and there's no registry of valid type values, two producers can describe the exact same kind of object differently: one writes "BigQuery Table", another writes "table". Links between concepts are untyped too — a link just asserts that two things are related, not how. Consumers are explicitly expected to tolerate unknown types and broken links rather than fail.

There’s also a fair observation that despite the “vendor-neutral” framing, the gravity of the initial ecosystem still sits with Google: the reference producer runs on Gemini, the demonstrated data source is BigQuery, and the natural ingestion path is Google Cloud’s own Knowledge Catalog product (a rebrand of what used to be Dataplex). The license is open. The center of gravity, for now, is not.

## Should you build on it?

If you’re