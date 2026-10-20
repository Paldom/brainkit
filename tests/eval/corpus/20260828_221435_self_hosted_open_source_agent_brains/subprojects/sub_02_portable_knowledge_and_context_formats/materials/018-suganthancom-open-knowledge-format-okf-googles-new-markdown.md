---
title: Open Knowledge Format (OKF): Google's New Markdown Format for AI Agents — Suganthan
url: https://suganthan.com/blog/open-knowledge-format/
final_url: https://suganthan.com/blog/open-knowledge-format/
source_type: social
providers: brave
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:26+00:00
published: 2026-06-14
content_digest: 861c47c85779bc43
---

<Suganthan®/>

~/about ~/ai-seo ~/research ~/projects ~/tools
~/blog

~/notes

~/contact

~/about ~/ai-seo ~/research ~/projects ~/tools ~/blog ~/notes ~/contact

Blog/Open Knowledge Format (OKF): Google's New Markdown Format for AI Agents

# Open Knowledge Format (OKF): Google's New Markdown Format for AI Agents

Google shipped OKF, the Open Knowledge Format, a markdown standard for handing your content to AI agents. What it is, what it does and does not do, and how to generate your bundle free.

By Suganthan Mohanadasan

Updated 24 Jul 2026 (posted 14 Jun 2026 ) 10 min read

Some assembly required
Tags:
#seo
#ai
#tools

A few weeks ago I published a long post on making a website agent-ready. It runs through robots rules, llms.txt, schema, markdown negotiation, MCP cards and more, and almost none of it is officially acknowledged by anyone yet. It is a stack of educated bets. Last month Google turned one of those bets into a published standard, the Open Knowledge Format, and unlike most things Google ships you can write one in a text editor.

It arrived quietly, bolted to a rebrand. Google spent years selling Dataplex as enterprise data plumbing nobody outside a data team ever thought about. It is now Knowledge Catalog, described as an âalways-on context engineâ for AI agents. The product barely moved. The positioning moved completely, which I wrote about when it shipped. OKF is the portable, open piece of that launch, and it is the piece worth your time.

## What OKF actually is

Underneath, OKF is plain. A bundle is a directory of markdown files. Every file carries a short block of YAML up top, the type of thing it is, a title, a description, and it links to its neighbours like any markdown document would. An agent reads it as is, with no scraping and no API in the way.

Here is what a single file looks like, since a whole bundle is just a folder of these.
---type: Articletitle: How to Connect the Ahrefs MCP Server to Manusdescription: The official MCP servers, why they did not connect, and the fix.resource: https://yoursite.com/blog/ahrefs-mcp-manus/tags: [mcp, ahrefs]---# How to Connect the Ahrefs MCP Server to ManusThe body of the post, as clean markdown.
Add an index.md that lists the files so an agent can see what is there before opening everything, and that is the format. There is no registry to join and nothing to install. Googleâs spec is still short enough to read in one sitting.

## Where OKF fits

The web is quietly growing a second layer, one written for machines instead of browsers, and OKF is its newest floor. Sitemap.xml tells a crawler which URLs exist. llms.txt points an agent at the handful of pages you most want read. EntityMap, a separate spec I shipped here last month, declares which entities you own, you, your company, the topics you want your name stuck to, and how they relate. OKF goes one floor higher again and hands over the content itself, every page as a clean markdown concept, cross-linked into a graph an agent can walk.

They stack rather than compete. llms.txt is a signpost, EntityMap is a whoâs who, and OKF is the library itself.

## What changed in v0.2

Google shipped v0.2 on 25 July 2026, six weeks after the first version. If v0.1 asked what your content is, v0.2 asks whether anyone stands behind it.

The reasoning is worth reading even if you never write a bundle. When a person writes a document, accountability is implicit, because somebody put their name on it. When an agent generates ten thousand concepts overnight that guarantee is gone, so whatever reads them next has to judge each one on signals it can actually see. v0.2 adds four families of optional field to carry those signals.

FamilyFieldsWhat it answers

ProvenancesourcesWhat was this built from, and how credible is that?

Trustgenerated, verifiedWho made it, and who confirmed it?

Lifecyclestatus, stale_afterIs this current, and when does it expire?

AttestationAttested ComputationWas this number produced the way we said it must be?

Attestation is BigQuery machinery for finance teams who need proof an agent ran the sanctioned query instead of improvising its own. Ignore it. The rest matters to anyone who publishes.

verified is the one to watch. Itâs a list of confirmations, each naming an actor, and an actor prefixed human: reads differently to a machine one. That gives you three tiers, unverified, machine-confirmed and human-reviewed, arriving at the exact moment the web fills up with generated text nobody has read. Google is careful to say a consumer must never reject a concept for missing any of this, while noting that its absence now carries meaning.

stale_after is the other one Iâd use. Itâs an absolute date rather than a countdown, so staleness is a fact instead of a calculation. Itâs the first time Iâve been able to write my own re-check policy into the page itself rather than keep it in a document nobody else can read.

Two renames come with it, both backward compatible. timestamp becomes generated.at, and the old # Citations list in the body becomes the sources array.

### What I put in my own bundle

I rebuilt my bundle on v0.2, and the honest version is less flattering than the marketing one would be. Hereâs a real concept out of it, the same file an agent would fetch.
---type: "Article"title: "How ChatGPT Actually Picks Sources"resource: "https://suganthan.com/blog/how-chatgpt-picks-sources/"tags: ["geo", "ai-seo", "chatgpt"]generated: { by: "human:suganthan", at: "2026-06-24T00:00:00.000Z" }verified: - { by: "human:suganthan", at: "2026-06-27T00:00:00.000Z" }status: stablestale_after: 2027-06-27---
All 61 concepts carry generated: { by: human:suganthan }, which is true, and which I suspect is about to become unusual.

Only 18 carry a verified entry. I write and edit everything here myself, so I could have stamped all 61 as human-reviewed and nobody could have checked me. But a confirmation is supposed to be separate from the writing, so the only defens