---
title: FAQ — Open Knowledge Format (OKF)
url: https://okf.md/faq/
final_url: https://okf.md/faq/
source_type: web
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:34+00:00
published: 2026-06-19
content_digest: 57e6db4e6fa7e25b
---

Skip to content
OKFSpec Quickstart Examples Tools Ecosystem Map new
Search docsâ¦âKGet Started

esc

Pages
Spec â The 3 rulesQuickstart â Build your first bundleExamples â Real-world bundlesTools â Validators & integrationsEcosystem Map â Who uses OKFFAQ

ââ navigateâµ openesc close

SpecQuickstartExamplesToolsEcosystem MapGet Started

Spec

Quickstart

Examples

Tools

Ecosystem Map

FAQ

Validator

Skill
OKFâºDocsâºFAQ

# FAQ â Open Knowledge Format (OKF)

Frequently asked questions, answered by a human whoâs read the spec more times than is probably healthy.

## What is OKF?

A folder of Markdown files that represents what your organization knows â tables, metrics, APIs, playbooks, whatever â in a way both humans and AI agents can understand without special tools.

Each .md file is a âconcept.â YAML frontmatter at the top holds metadata. The structure is hierarchical and git-friendly. Thatâs mostly it.

Three mandatory rules:

Every .md (except index.md and log.md) needs parseable YAML frontmatter

Every frontmatter needs a non-empty type field

Reserved files (index.md, log.md) follow a defined structure

Everything else is up to you.

## Who created OKF?

Sam McVeety and Amir Hormati (Tech Leads, Data Analytics Engineering, Google Cloud) designed and announced OKF on June 12, 2026 via the Google Cloud Blog.

Published under Apache 2.0 in the GoogleCloudPlatform/knowledge-catalog repo.

Born inside the Knowledge Catalog (formerly Dataplex) world, but the spec is vendor-neutral. No Google Cloud required. Any org can adopt it.

Current version: 0.1 (Draft). Early, but usable today.

## Whatâs the âLLM Wikiâ pattern?

OKF formalizes a pattern that keeps reappearing under different names: the idea of giving AI agents a shared markdown library that grows more useful over time.

Andrej Karpathy articulated it most crisply in his LLM Wiki gist: âLLMs donât get bored, donât forget to update a cross-reference, and can touch 15 files in one pass.â The bookkeeping that causes humans to abandon personal wikis is exactly what LLMs are good at.

The same idea appears as Obsidian vaults wired to coding agents, the AGENTS.md / CLAUDE.md family of convention files, repos full of index.md and log.md artifacts, and âmetadata as codeâ repositories inside data teams.

The problem: each instance is bespoke. Karpathyâs wiki and your teamâs wiki may look alike (markdown, frontmatter, cross-links), but none are designed to cooperate. Thereâs no agreed-upon answer to what fields every document should carry.

OKF is the missing interoperability layer. It pins down the minimal set of conventions so wikis written by different producers can be consumed by different agents without translation.

## Do I need an SDK?

No. If you need an SDK to write Markdown files, we have bigger problems to discuss.

The spec literally says: âIf you can cat a file, you can read OKF; if you can git clone a repo, you can ship it.â

To produce it: text editor. To consume it: eyes. To validate: check 3 rules.

Tooling exists (validators, generators). None of it is required.

## How is it different from AGENTS.md?

Different jobs entirely.

AGENTS.md tells an agent how to behave. OKF tells an agent what exists in the world.

AGENTS.mdOKF

AnalogyâHereâs how to act""Hereâs what we knowâ

ScopeOne repoAll org knowledge

ConsumerCoding agentsAny agent or human

Theyâre friends, not competitors. Your AGENTS.md can say âcheck the OKF bundle at /knowledge for domain context.â

## How does it compare to Obsidian?

Same DNA (Markdown + frontmatter + links), different species.

Obsidian = personal knowledge tool. Wikilinks, graph view, plugins. Built for one humanâs brain.

OKF = interchange spec. Built so Team Aâs knowledge survives the trip to Team B (or Agent C) intact. Think: the difference between your personal notebook and a published reference manual.

Key differences: OKF uses standard Markdown links (not [[wikilinks]]), mandates a type field, has reserved files with defined structure, and is designed for programmatic consumption.

You can edit OKF bundles in Obsidian. Theyâll coexist peacefully. Just donât expect OKF to generate a pretty graph for you.

## What about DESIGN.md?

DESIGN.md is a document. OKF is a format.

If you converted your DESIGN.md into OKF, itâd become one concept in a bundle â maybe type: Architecture Decision. OKF is the container; DESIGN.md is something that lives inside it.

Thatâs really all there is to say here.

## Does it work with Claude/GPT/Gemini?

Yes. All of them. Any LLM that can read text â so, all of them â handles OKF natively.

Claude/Cursor: Drop the bundle in project context. Done.

GPT/ChatGPT: Upload the .md files or ZIP them.

Gemini: Natural fit via Knowledge Catalog, but works standalone too.

Any MCP agent: Serve the bundle as a resource.

Model agnosticism is a foundational requirement of the spec. No lock-in.

## How do I validate a bundle?

Check 3 things:

Every non-reserved .md has parseable YAML frontmatter

Every frontmatter has a non-empty type field

Reserved files (index.md, log.md) follow their defined structure

Thatâs the whole spec compliance check. Hereâs a one-liner if you want:
for f in $(find ./bundle -name "*.md" ! -name "index.md" ! -name "log.md"); do head -50 "$f" | grep -q "^type:" || echo "FAIL: $f missing type"done
A client-side validator is available at /validator. But honestly, the bash loop above gets you 90% there.

## Will OKF replace data catalogs?

No. The spec explicitly lists this as a non-goal.

Catalogs = platforms (UI, API, governance, lineage, permissions). OKF = export/exchange format.

Your catalog is the system of record. An OKF bundle is the portable snapshot you version in git, share across teams, or feed to an AI agent. Different layers, complementary roles.

## Is it only for BigQuery?

The examples use BigQuery because thatâs where it was born. 