---
title: GitHub - ItamarZand88/awesome-agent-conventions: A curated guide to convention files AI agents read, write, and act on: AGENTS.md, CLAUDE.md, SKILL.md, llms.txt, MCP configs, rules, and examples. · GitHub
url: https://github.com/ItamarZand88/awesome-agent-conventions
final_url: https://github.com/ItamarZand88/awesome-agent-conventions
source_type: social
providers: exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:36+00:00
published: 2026-06-16T00:00:00.000Z
content_digest: 5b9b97b9008c2504
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

ItamarZand88
/awesome-agent-conventionsPublic

Notifications
You must be signed in to change notification settings

Fork
2

Star
29

Code

Issues1

Pull requests4

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
8 Commits

8 Commits

## Folders and files

NameName
Last commit message

Last commit date

.github

.github

assets

assets

categories

categories

conventions

conventions

scripts

scripts

.gitignore

.gitignore

CODE_OF_CONDUCT.md

CODE_OF_CONDUCT.md

CONTRIBUTING.md

CONTRIBUTING.md

LICENSE

LICENSE

Makefile

Makefile

README.md

README.md

ROADMAP.md

ROADMAP.md

SECURITY.md

SECURITY.md

THIRD_PARTY_EXAMPLES.md

THIRD_PARTY_EXAMPLES.md

WATCHLIST.md

WATCHLIST.md

View all files

## Repository files navigation

README

Code of conduct

Contributing

MIT license

Security

More items

# Awesome Agent Conventions

A curated field guide to the convention files AI agents read, write, and act on.

22 conventions across 11 categories. From common project instruction files to newer agent-web discovery and trust formats.

Agent tools increasingly rely on plain files in a repository or website root:
instructions, memory, rules, tool connections, prompt assets, discovery
metadata, and protocol hints. The names are easy to mix up, and the adoption
levels vary a lot.

This repo keeps the map practical:

Know what a file is for. Each entry names the convention, usual filename,
primary readers, and spec or source.

Study real examples. Examples are fetched from public repositories by
script, with provenance kept at the top of each file.

Separate practice from proposal. Maturity labels show what is widely used,
what is early, and what is still only proposed.

## Contents

Instruction & context · category page
🟢 AGENTS.md

🟢 CLAUDE.md

🟢 Tool-specific instruction files

🟠 OKF (Open Knowledge Format)

Memory & state · category page
🟢 MEMORY.md

🟢 Memory Bank

Spec-driven development · category page
🟢 Spec Kit

🟢 Kiro steering files

Skills & prompt assets · category page
🟢 SKILL.md

🟢 Prompt asset files

🟢 Claude Code commands

🟢 Copilot prompt & instruction files

Tooling & connections · category page
🟢 MCP server config

Rules & ignore files · category page
🟢 Rules files

🟢 AI ignore files

Design · category page
🟢 DESIGN.md

Web & discoverability · category page
🟢 llms.txt

🟢 pricing.md

Agent-web trust · category page
🟠 auth.md

🔵 ai.txt

Identity & protocols · category page
🟠 Agent Cards (A2A)

Proposed namespace · category page
🔵 The protocols.md namespace

## What counts

This list is intentionally narrow. A file belongs here when it is a convention
for agent behavior or agent-readable metadata: instructions, memory, skills,
rules, tool config, prompt assets, or web-discovery hints.

Any file type can qualify - .md, .txt, .prompty, .json, dotfiles, or a
directory pattern. Human-first project docs such as README.md,
CONTRIBUTING.md, SECURITY.md, and CHANGELOG.md stay out unless the file has
become an agent convention in its own right.

## Maturity tiers

The badge is a claim about adoption, not quality. It keeps a proven convention
from being presented the same way as a new idea.

BadgeTierMeaning

🟢AdoptedUsed in production by multiple tools, projects, or teams.

🟠EmergingPublished by a real organization, but still early or limited in adoption.

🔵ProposedPublicly described, but without clear adoption beyond the proposal.

## Instruction & context

Standalone page: categories/instruction-context.md

ConventionFilesRead bySpec

🟢AGENTS.mdAGENTS.mdMost coding agents - OpenAI Codex, Cursor, Jules, Aider, Gemini CLI, Zed, and othersspec ↗

🟢CLAUDE.mdCLAUDE.mdClaude Code, and tools that read the Claude memory conventionspec ↗

🟢Tool-specific instruction filesGEMINI.mdAGENT.mdQWEN.mdWARP.mdCONVENTIONS.mdcopilot-instru