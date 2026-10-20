---
title: GitHub - charlie947/ai-second-brain: Build a living, searchable AI second brain from your ChatGPT, Claude, and research history - Karpathy-style. A Claude Code skill. · GitHub
url: https://github.com/charlie947/ai-second-brain
final_url: https://github.com/charlie947/ai-second-brain
source_type: web
providers: brave, tavily
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:54+00:00
published: 2026-04-03
content_digest: ea23d1fe754955ee
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

charlie947

ai-second-brain

## Repository navigation

Code

Issues

Pull requests

Actions

Projects

Security and quality

Insights

More items

ai-second-brain
Public

NotificationsYou must be signed in to change notification settings

Fork40 (40)

Star201 (201)You must be signed in to star a repository

## About

Build a living, searchable AI second brain from your ChatGPT, Claude, and research history - Karpathy-style. A Claude Code skill.

### Topics

aiclaude-codekarpathy-wikiknowledge-managementobsidianpkmsecond-brain

### Resources

Readme

MIT license

Activity

### Stars

201 stars

### Watchers

3 watching

### Forks

40 forks

Report repository

main

BranchesTags

Go to file

Code
Open more actions menu

## Latest commit

## History
7 Commits

7 Commits

## Folders and files

NameName
Last commit message

Last commit date

.gitattributes

.gitattributes

.gitignore

.gitignore

CHANGELOG.md

CHANGELOG.md

LICENSE

LICENSE

README.md

README.md

SKILL.md

SKILL.md

ai-second-brain.skill

ai-second-brain.skill

render-social-preview.js

render-social-preview.js

social-preview.html

social-preview.html

social-preview.png

social-preview.png

View all files

## Repository files navigation

README

MIT license

More items

# AI Second Brain

A Claude Code skill that walks you through building a living, searchable, AI-powered knowledge base from your own ChatGPT and Claude history, your raw research, and your daily inputs.

On 3rd April 2026, Andrej Karpathy published a 1,500-word gist describing how to build a personal wiki using a folder of markdown and an LLM. Within 48 hours the X thread about it hit 16 million views.

This skill packages Karpathy's idea — plus an AI-history organiser by Alex Freedman and the slash-command workflow shared by Greg Isenberg — into a single Claude Code skill that walks any user through the full setup.

Built for non-technical readers of MarTech AI.

## Install

The reliable way (works on every Mac, easy to update later):

git clone https://github.com/charlie947/ai-second-brain.git ~/.claude/skills/ai-second-brain

If ~/.claude/skills/ai-second-brain already exists, back it up first:

mv ~/.claude/skills/ai-second-brain ~/.claude/skills/ai-second-brain.backup

Then open Claude Code in any folder and say:

Set up my AI second brain.

To update later:

cd~/.claude/skills/ai-second-brain && git pull

### Verify it installed

In Claude Code, type:

/skills

You should see ai-second-brain in the list. If you don't, the folder is in the wrong place — re-run the clone command and double-check the destination path.

## What it does

flowchart LR
A[Your ChatGPT<br/>& Claude exports] --> B[Step 1<br/>AI Brain]
C[PDFs, articles,<br/>transcripts] --> D[Step 2<br/>Karpathy Wiki]
E[Gmail, Granola,<br/>NotebookLM] --> F[Step 3<br/>Living Wiki]
B --> G[Tagged, linked<br/>Obsidian vault]
D --> G
F --> G
G --> H[Talk to it from<br/>your phone via iMessage]

Loading

The skill walks you through three stages. You can do all three or pick one — just tell it.

AI Brain — exports your full ChatGPT and Claude history and turns the lot into a tagged, linked Obsidian vault you can search by topic, project, or person.

Karpathy Wiki — sets up a raw/ and wiki/ folder pair so Claude Code can compile a living wiki from your research. Drop a PDF in, the wiki updates itself.

Living Wiki — connects Gmail, NotebookLM and Granola, sets up iMessage Channels so you can text your second brain from your phone, and scaffolds three slash commands (/today, /ideas, /create).

Every step where Claude Code can do the work for you, it does. Every step that needs you (data exports, granting macOS permissions, NotebookLM browser login) pauses until you confirm.

## What you need before starting

Claude Code installed and working

Obsidian (free)

About 30 minutes of attention, plus 1–3 days of background waiting for OpenAI to email your ChatGPT export

## Trigger phrases

The skill activates when you ask Claude Code anything like:

"Set up my AI seco