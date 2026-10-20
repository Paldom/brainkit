---
title: GitHub - GoogleCloudPlatform/open-knowledge-format · GitHub
url: https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main
final_url: https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main
source_type: social
providers: exa, site:exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:35+00:00
published: 2026-08-11T00:00:00.000Z
content_digest: 98862dc30ce5d64b
---

Skip to content

## Navigation Menu

Sign in
Appearance settings

Platform

AI CODE CREATION
GitHub CopilotWrite better code with AI

GitHub Copilot appDirect agents from issue to merge

MCP RegistryIntegrate external tools

DEVELOPER WORKFLOWS
ActionsAutomate any workflow

CodespacesInstant dev environments

IssuesPlan and track work

Code ReviewManage code changes

Code QualityEnforce quality at merge

APPLICATION SECURITY
GitHub Advanced SecurityFind and fix vulnerabilities

Code securitySecure your code as you build

Secret protectionStop leaks before they start

EXPLORE
Why GitHub

Documentation

Blog

Changelog

Marketplace

View all features

Solutions

BY COMPANY SIZE
Enterprises

Small and medium teams

Startups

Nonprofits

BY USE CASE
App Modernization

DevSecOps

DevOps

CI/CD

View all use cases

BY INDUSTRY
Healthcare

Financial services

Manufacturing

Government

View all industries

View all solutions

Resources

EXPLORE BY TOPIC
AI

Software Development

DevOps

Security

View all topics

EXPLORE BY TYPE
Customer stories

Events & webinars

Ebooks & reports

Business insights

GitHub Skills

SUPPORT & SERVICES
Documentation

Customer support

Community forum

Trust center

Partners

View all resources

Open Source

COMMUNITY
GitHub SponsorsFund open source developers

PROGRAMS
Security Lab

Maintainer Community

GitHub Stars

Archive Program

REPOSITORIES
Topics

Trending

Collections

Enterprise

ENTERPRISE SOLUTIONS
Enterprise platformAI-powered developer platform

AVAILABLE ADD-ONS
GitHub Advanced SecurityEnterprise-grade security features

Copilot for BusinessEnterprise-grade AI features

Premium SupportEnterprise-grade 24/7 support

Pricing

Search/

Sign in
Sign up
Appearance settings

You signed in with another tab or window. Reload to refresh your session.You signed out in another tab or window. Reload to refresh your session.You switched accounts on another tab or window. Reload to refresh your session.Dismiss alert

### Uh oh!

There was an error while loading. Please reload this page.

GoogleCloudPlatform
/open-knowledge-formatPublic

Notifications
You must be signed in to change notification settings

Fork
6

Star
150

Code

Issues4

Pull requests0

Discussions

Actions

Projects

Security and quality0

Insights

Additional navigation options

Code

Issues

Pull requests

Discussions

Actions

Projects

Security and quality

Insights

main

BranchesTags

Go to file

Code
Open more actions menu

## Latest commit

## History
6 Commits

6 Commits

## Folders and files

NameName
Last commit message

Last commit date

bundles

bundles

connectors

connectors

samples

samples

src/reference_agent

src/reference_agent

tests

tests

.gitignore

.gitignore

CODE_OF_CONDUCT.md

CODE_OF_CONDUCT.md

CONTRIBUTING.md

CONTRIBUTING.md

LICENSE.md

LICENSE.md

README.md

README.md

SPEC.md

SPEC.md

pyproject.toml

pyproject.toml

View all files

## Repository files navigation

README

Code of conduct

Contributing

Apache-2.0 license

More items

# Open Knowledge Format (OKF)

### 📖 Read the Open Knowledge Format v0.2 specification → SPEC.md

This repository is primarily about the Open Knowledge Format
(OKF).

OKF is a universal, vendor-neutral format for representing knowledge
as plain markdown files with YAML frontmatter. It is not tied to any
particular agent, framework, model provider, or serving system. The
goal is simple:

Anyone can produce OKF — humans authoring by hand, agents built on
any framework (Google ADK, LangChain, custom), export pipelines from
existing catalogs (Dataplex, Unity Catalog, Collibra, …), or scripts
walking a database.

Anyone can serve and consume OKF — a static file server, a
knowledge-management UI (Obsidian, Notion, MkDocs), an LLM loading
files into context, a search index, or a graph viewer like the one
bundled in this repo.

The agent below is a proof of concept demonstrating one way to
produce OKF bundles automatically. The format itself is the
contribution; this agent and the visualizer exist to make the format
tangible at both ends — production and consumption.

See OKF in practice — three ready-to-browse bundles produced by this
agent, checked into bundles/:

bundles/ga4/ — GA4 e-commerce dataset
(viz.html)

bundles/stackoverflow/ — Stack Overflow
public dataset (viz.html)

bundles/crypto_bitcoin/ — Bitcoin
blocks/transactions (viz.html)

bundles/acme_retail/ — Acme Retail
(viz.html)

## Why OKF?

OKF represents catalog knowledge as plain markdown files with YAML
frontmatter, organized in a directory hierarchy. That choice unlocks a few
properties that are hard to get from a service-owned metadata store:

Human- and agent-readable. No SDK or query language stands between a
reader and the content. An engineer can cat a concept; an LLM can ingest
it verbatim into context.

Version-controllable out of the box. Bundles live in git. Pull
requests, line-by-line diffs, blame, and review workflows just work —
knowledge curation becomes a normal software-engineering activity.

Portable and lock-in free. A bundle is a directory. Ship it as a
tarball, host it in any repo, mount it from any filesystem, or sync it to
any system that speaks files. No proprietary API stands between you and
your metadata.

Mixes structured and unstructured data deliberately. Use frontmatter
for the few fields you want to query, filter, or index on (type,
resource, tags, generated, status); use the markdown body for the
prose, schemas, and example queries that LLMs and humans actually read.

Trust, provenance, and freshness are first-class. v0.2 puts queryable
signals in frontmatter — where a concept came from (sources with per-source
credibility signals), who produced and confirmed it (generated, verified,
from which consumers derive a trust tier), and whether it is still current
(status, stale_after) — so an agent-maintained corpus stays trustable
without any bespoke runtime.

Minimally opinionated, freely extensible. A small set of required
keys ensures inter