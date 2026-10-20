---
title: Open Knowledge Format: I Already Do This, and Now It Has a Name | alexop.dev
url: https://alexop.dev/posts/open-knowledge-format-markdown-frontmatter-agent-knowledge/
final_url: https://alexop.dev/posts/open-knowledge-format-markdown-frontmatter-agent-knowledge/
source_type: social
providers: brave, gemini, kimi
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:13+00:00
published: 2026-06-27
content_digest: 4e12547151b0777a
---

Next Talk: Frontend Testing Reimagined: A Black-Box Strategy with Vitest Browser Mode

September 16, 2026 — TACON, Leipzig

Conference

Skip to content

alexop.dev
Posts

TILs

Notes

Talks

Projects

Prompts

Tags

About

SearchSearch (⌘K)

Go back

# Open Knowledge Format: I Already Do This, and Now It Has a Name

Published:Jun 27, 2026 at

## TLDR#

Google Cloud shipped the Open Knowledge Format (OKF): a directory of Markdown files with YAML frontmatter that any agent can read and any human can edit. No SDK, no runtime, no database.

I already do something like this in every coding repo. Markdown files the agent reads before it works, frontmatter on top, linked together. OKF is that pattern with a name and a tiny spec.

The part I actually like is the frontmatter. One required field (type), a handful of optional ones, and now the files are queryable instead of just readable.

This is semantic memory for agents, standardized. It’s the same idea as CLAUDE.md and AGENTS.md, pushed one step toward “portable between tools.”

A format is worth more than another knowledge service. You can write OKF by hand today without installing anything, and that’s the whole point.

## I already keep my knowledge in Markdown#

I don’t write much code by hand anymore. I delegate to a coding agent and review the output. And the single thing that decides whether that goes well is what the agent knows about my project before it starts.

So every repo I work in has the same shape. A CLAUDE.md at the root. A docs/ folder with architecture notes, conventions, gotchas, the stuff that lives in the heads of the people who’ve been here a while. The agent reads those files, then does the work. When it learns something new, it writes it back. Plain Markdown, checked into git, sitting next to the code it describes.

This works really well. It’s simple, it’s versioned, and I can read it myself in any editor. No vendor, no lock-in, no “open the catalog UI to see the metadata.”

And I’ve gone further than a bare docs/ folder. On some projects I ran brainmaxxing: a Markdown vault the agent reads at session start and writes back to when it learns something. It ships a little learning loop, /reflect after a session, /ruminate over old conversations, /meditate to prune stale notes, and because the vault is also an Obsidian vault, I can open the agent’s memory and read it like my own notes. The OKF post names this exact species in passing: “Obsidian vaults wired to coding agents.” It worked really well. But it was bespoke. My folder names, my conventions, my skills, none of it was built to travel to your repo or a different agent.

The thing I never had was a format. My docs/ folder and your docs/ folder both look like Markdown, but they don’t agree on anything. What fields go on top of a file? What does index.md mean? Nothing was written down. It just worked because I was the only one reading it.

That’s the gap Open Knowledge Format is trying to fill, and after reading the spec I think it’s a good move.

## What OKF actually is#

OKF is a directory of Markdown files. Each file is one concept: a table, a dataset, a metric, a runbook, an API, whatever you want to capture. The file path is the concept’s identity.
sales/├── index.md├── datasets/│ └── orders_db.md├── tables/│ ├── orders.md│ └── customers.md└── metrics/ └── weekly_active_users.md
Every concept file has a small block of YAML frontmatter and a Markdown body. The frontmatter holds the few fields that need to be queryable; the body holds everything else.
---type: BigQuery Tabletitle: Ordersdescription: One row per completed customer order.resource: https://console.cloud.google.com/bigquery?...&t=orderstags: [sales, revenue]timestamp: 2026-05-28T14:30:00Z---# Schema| Column | Type | Description ||---------------|--------|------------------------------------------|| `order_id` | STRING | Globally unique order identifier. || `customer_id` | STRING | FK to [customers](/tables/customers.md). |# JoinsJoined with [customers](/tables/customers.md) on `customer_id`.
That’s it. Concepts link to each other with normal Markdown links, which turns the folder into a graph of relationships, not just a tree. Two filenames are reserved: index.md for an overview at each level, and log.md for a running history of changes. The whole v0.1 spec fits on one page.

If you’ve used Obsidian, or written a CLAUDE.md, or kept an AGENTS.md, the shape is immediately familiar. That’s deliberate. OKF isn’t inventing a new thing, it’s writing down the small set of conventions that make the existing thing interoperable.

💡Note

OKF v0.1 comes from the Google Cloud Data Cloud team, and the reference tooling is data-flavored: an agent that walks a BigQuery dataset and drafts a concept file per table, plus a static HTML visualizer. Ignore the BigQuery framing if it’s not your world. The format is just Markdown and frontmatter, and nothing about it is tied to a database or a cloud.

## The frontmatter is the part I like#

The body of these files I already write. Markdown is Markdown. The piece OKF adds that I didn’t have is the agreed-upon frontmatter.

OKF requires exactly one field on every concept: type. Everything else is optional: title, description, resource, tags, timestamp. That’s a good ratio. One thing you must do, a handful of things you can do, and the body is yours.

Why does this matter? Because frontmatter makes the files queryable without parsing prose. An agent can filter “every concept where type: metric” or “everything tagged revenue” or “what changed since this timestamp” without reading the bodies first. It’s the same trick I use on this blog. Every post has frontmatter with title, description, tags, pubDatetime, and that’s what powers the tag pages and the related-posts logic. The body is for humans; the frontmatter is for the machine.

I keep coming back to one line from the OKF principles: it defines the interoperability surface, not the content model. It tells you the file must de