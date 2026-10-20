---
title: Introducing the Open Knowledge Format - StorageNewsletter
url: https://www.storagenewsletter.com/2026/07/06/introducing-the-open-knowledge-format/
final_url: https://www.storagenewsletter.com/2026/07/06/introducing-the-open-knowledge-format/
source_type: social
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:22+00:00
published: 2026-07-06
content_digest: c332c8bc2a20946e
---

-- Categories --
M&As
Start-Ups
Systems (RAID, NAS, SAN, Appliance)
Financial Results, Investments and IPOs
Market Reports/Research & Certifications
Solid State (flash, SSD...), Memory...
Hard Disk Drives
Tapes
Optical, DNA
Software
People
Cloud, Online Backup, SSPs, MSPs
Networking and Connectivity
Security
Partnership (OEM, Channel, Dist. & Alliance)
Customer Wins, Awards
Business & Corporate
Exhibitions & Conferences
History
Miscellaneous

-- More resources --
Complete List of 235 SSD Makers
All Financial Rounds of Funding of Storage Start-Ups Since 2000
All M&As in 2023
All Companies in All-Flash Subsystems
Storage Dictionary (SNIA)
History of Storage Industry
Storage Abbreviations
Top Fastest Growing Storage Companies in 2022
Top Storage Companies in 2023
Total Enterprise Storage Systems Installed Base Expected to Grow at 30.9% CAGR between 2020–2025
What Do Represent All These Bytes?

About Us

Submit News

Editorial Policy

Contact Us

Advertise with Us

Conf. Dir

Awards

What are you looking for ?Search for:

About Us

Submit News

Editorial Policy

Contact Us

Advertise with Us

Conf. Dir

Awards

Search for:

Categories-- Navigate --
M&As
Start-Ups
Systems (RAID, NAS, SAN, Appliance)
Financial Results, Investments and IPOs
Market Reports/Research & Certifications
Solid State (flash, SSD...), Memory...
Hard Disk Drives
Tapes
Optical, DNA
Software
People
Cloud, Online Backup, SSPs, MSPs
Networking and Connectivity
Security
Partnership (OEM, Channel, Dist. & Alliance)
Customer Wins, Awards
Business & Corporate
Exhibitions & Conferences
History
Miscellaneous

More Resources

Complete List of 235 SSD Makers

All Financial Rounds of Funding of Storage Start-Ups Since 2000

All M&As in 2023

All Companies in All-Flash Subsystems

Storage Dictionary (SNIA)

History of Storage Industry

Storage Abbreviations

Top Fastest Growing Storage Companies in 2022

Top Storage Companies in 2023

Total Enterprise Storage Systems Installed Base Expected to Grow at 30.9% CAGR between 2020–2025

What Do Represent All These Bytes?

Home » Software » Introducing the Open Knowledge Format

# Introducing the Open Knowledge Format

## Promoting a portable, interoperable format

By Philippe Nicolas | July 6, 2026 at 2:00 pm

Blog written by Sam McVeety, tech lead, data analytics, engineering, data cloud, Google Cloud, and Amir Hormati, tech lead, BigQuery, engineering, data cloud, Google Cloud, published June 12, 2026

As foundation models continue to improve, the lack of relevant context often limits what they can do, especially as they are used to build agentic systems. While these models can help you write code, summarize documents, or analyze a dataset, they still need the right information to produce accurate and actionable results.

That’s why today, we’re introducing the Open Knowledge Format (OKF), an open specification that formalizes the LLM-wiki pattern into a portable, interoperable format. This is a vendor-neutral, agent- and human-friendly standard for representing the metadata, context, and curated knowledge that modern AI systems need.

As published, OKF v0.1 represents knowledge as a directory of markdown files with YAML frontmatter, with a small set of agreed-upon conventions that let wikis written by different producers be consumed by different agents without translation.

That’s it. No complex compression scheme, no new runtime, no required SDK. A bundle of OKF documents is:

Just markdown — readable in any editor, renderable on GitHub, indexable by any search tool

Just files — shippable as a tarball, hostable in any git repo, mountable on any filesystem

Just YAML frontmatter — for the small set of structured fields that need to be queryable: type, title, description, resource, tags, and timestamp

If you’ve used Obsidian, Notion, Hugo, or any of the LLM wiki patterns that have emerged over the past year, the shape will feel familiar. OKF formalizes the small set of conventions needed to make these patterns interoperable.

Let’s take a look at the problem that OKF can solve for your organization, how it works, how to get started with it, and what’s next.

A fragmented context landscape

In most organizations, the information that foundation models use is overwhelmingly internal knowledge: the schema of a table, your business’ meaning of a metric, the runbook for an incident, the join paths between two systems, the deprecation notice for an old API, etc.

Today, these atoms of knowledge live in a variety of highly fragmented systems:

Metadata catalogs with their own APIs

Wikis, third-party systems, or in shared drives

Code comments, docstrings, or notebook cells

The heads of a few senior engineers

When an AI agent needs to answer “How do I compute weekly active users from our event stream?” it has to assemble the answer from these scattered, mutually incompatible surfaces. Every vendor offers its own catalog, its own SDK, its own knowledge-graph schema, and none of the knowledge is easily portable across products or organizations.

The result: Every agent builder is solving the same context-assembly problem from scratch, every catalog vendor is reinventing the same data models, and the knowledge itself is locked behind whichever surface created it.

Knowledge as a living wiki

Developer teams are changing how they build AI agents. Instead of using models to search the same documents for the same facts over and over, you can give your agents a shared markdown library that grows more useful over time. This lets your agents take on the drudgery of reading and updating their own files, while your team curates the content and manages it like code.

Andrej Karpathy, the prominent AI researcher and educator, articulates this idea most crisply in his LLM Wiki gist. “LLMs don’t get bored, don’t forget to update a cross-reference, and can touch 15 files in one pass,” he writes. The bookkeeping that causes humans to abandon personal wikis is exactly what LLMs are good at.

Similar knowledg