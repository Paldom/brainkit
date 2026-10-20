---
title: Google Just Quietly Released the Missing Piece for AI Agents. It’s Called OKF. | by Akhil | Jun, 2026 | Medium
url: https://medium.com/@AkhilAIWorld/google-just-quietly-released-the-missing-piece-for-ai-agents-its-called-okf-7e96a33898ce
final_url: https://medium.com/@AkhilAIWorld/google-just-quietly-released-the-missing-piece-for-ai-agents-its-called-okf-7e96a33898ce
source_type: social
providers: brave, tavily
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:31+00:00
published: 2026-06-30
content_digest: d1584fc01d8e4fc6
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

The Problem It Solves

What OKF Actually Is

The Structure: A Directory Is a Knowledge Graph

Anatomy of an OKF Concept File

The Three Design Principles

1. Minimally opinionated

2. Producer and consumer independence

3. Format, not platform

OKF vs Everything Else You’re Already Using

The Karpathy Connection

What Google Actually Shipped

When to Use OKF

How to Get Started

The Layered Memory Stack

What’s Still Open

Why This Is a Bigger Deal Than It Looks

## Akhil

Artificial Intelligence

Claude

Software Engineering

Developer Tools

Programming

# Google Just Quietly Released the Missing Piece for AI Agents. It’s Called OKF.

Akhil

9 min read
·
Jun 30, 2026

--

8

Listen

Share

The Open Knowledge Format is the standard that makes agent memory portable, versioned, and readable by every tool you use.

Every developer using an AI coding agent has hit the same wall. The session ends. The next morning, you start fresh and the agent has forgotten everything. It re-discovers your auth flow. It re-guesses the reason behind a three-year-old architectural decision. It reads the same five files again to rebuild context you spent an hour explaining yesterday.

The standard fix is CLAUDE.md or AGENTS.md — a context file that loads at the start of every session. But these are blunt instruments. They load everything, every time, whether or not it’s relevant. They’re written for one agent on one platform and don’t travel well. They mix behavioral instructions (“always write tests”) with factual knowledge (“the orders table joins to customers on customer_id”) in ways that get messy fast.

On June 12, 2026, Google Cloud published a specification that changes this. It’s called the Open Knowledge Format, and it’s the cleanest solution to the agent memory problem that’s appeared yet. Here’s what it is, how it works, and why it matters more than most people realize.

## The Problem It Solves

Before getting into what OKF is, it helps to understand exactly what it’s fixing.

When an agent needs to answer “how do we compute weekly active users from our event stream?”, the answer is scattered across at least four places:
+-----------------------+--------------------------------------------+

| WHERE IT LIVES | WHAT'S THERE |

+-----------------------+--------------------------------------------+

| Metadata catalogs | Table schemas (but vendor-locked APIs) |

| Wiki / Notion | Runbooks, metric definitions |

| Code comments | Docstrings, inline notes |

| People's heads | Join paths, deprecation warnings |

+-----------------------+--------------------------------------------+
None of it travels with the code. None of it survives a fresh context window. Every agent builder re-solves the same context assembly problem from scratch. Every catalog vendor reinvents schemas. The knowledge is locked inside whatever surface created it.

OKF’s bet is that the missing piece is a format, not another platform.

## What OKF Actually Is

Open Knowledge Format v0.1 is a vendor-neutral, open specification (Apache 2.0) for representing knowledge as a directory of markdown files with YAML frontmatter. That description sounds simple. It is simple. That’s the point.

No schema registry. No runtime engine. No SDK required. If you can cat a file, you can read it. If you can git clone a repo, you can ship it.

The entire spec fits on one page. It has exactly one required field. Everything else is optional or producer-defined.

## The Structure: A Directory Is a Knowledge Graph

An OKF bundle is just a folder. File path = concept identity.
.okf/

+-- index.md <- progressive entry point

+-- log.md <- dated change history, newest first

+-- services/

| +-- index.md

| +-- auth-api.md <- one concept = one file

| +-- payments-service.md

+-- datasets/

| +-- index.md

| +-- orders-db.md

+-- metrics/

| +-- index.md

| +-- weekly-active-users.md

+-- decisions/

+-- index.md

+-- why-we-use-postgres.md
Two files are reserved across every bundle:

index.md - progressive disclosure. Agents navigate the bundle by reading index files at each level, drilling down only when the task is relevant. This is the same progressive loading that makes Claude Skills token-efficient.

log.md - ISO-dated change history, newest first. Human and agent maintainers both update it when concepts change.

Every other file is a concept document. The path is its ID.

## Anatomy of an OKF Concept File

Each concept needs exactly one thing in its frontmatter: a non-empty type field. Everything else is optional.
---

type: Service

title: "Auth API"

description: "Issues and verifies short-lived access tokens."

resource: https://github.com/acme/auth

tags: [auth, platform]

timestamp: 2026-06-14T10:00:00Z

---## Endpoints| Method | Path | Description |

|--------|----------|---------------------------|

| POST | /token | Exchange creds for a JWT. |

| GET | /verify | Validate a token. |## Why This ExistsSee the decision at [decisions/why-we-separated-auth.md](../decisions/why-we-separated-auth.md).

Joins with [datasets/orders-db.md](../datasets/orders-db.md) for user scoping.
That last part is the key design move. Concepts link to each other with standard markdown links. The directory becomes a graph. Not a flat list of documents — a graph of typed, cross-referenced knowledge where the relationships are explicit and traversable.
[auth-api.md]

/ \

links links

/ \

[decisions/why-separated-auth.md] [datasets/orders-db.md]

|

links

|

[datasets/customers-db.md]
Any tool that can follow a markdown link can traverse this graph. Any agent with file access can read and write it.

## The Three Design Principles

## 1. Minimally opinionated

Only type is required. What types exist (Service, Dataset, Metric, Decision, Runbook), what optional fields to use, what body sections to include - those are the producer's choice. OKF defines interoperability, not content models.

## 