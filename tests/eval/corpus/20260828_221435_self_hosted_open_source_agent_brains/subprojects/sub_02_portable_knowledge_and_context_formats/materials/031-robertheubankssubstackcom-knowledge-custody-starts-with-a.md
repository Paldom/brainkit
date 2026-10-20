---
title: Knowledge Custody Starts With a File Format
url: https://robertheubanks.substack.com/p/knowledge-custody-starts-with-a-file
final_url: https://robertheubanks.substack.com/p/knowledge-custody-starts-with-a-file
source_type: social
providers: exa
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:38+00:00
published: 2026-07-05T00:00:00.000Z
content_digest: fe2026bbabdfae30
---

# Robert H. Eubanks

SubscribeSign in

# Knowledge Custody Starts With a File Format

### Part Two of the Knowledge Custody series.

Robert H. Eubanks

Jul 05, 2026

6

Share

Google’s Open Knowledge Format (OKF) is easy to describe as markdown plus metadata. That description is true, but it undersells it. The important thing is not that a knowledge base can be written in markdown. It is that agent-ready knowledge can live outside the product, the index, and the model currently using it. It can be held as files, opened, moved, inspected by a human, and parsed by an agent.

That is a different category of artifact. A chat history is something you access. A vector index is something you query. A proprietary memory store is something a product manages for you. A file-based knowledge bundle is something the organization can actually hold.

OKF matters for two reasons, and neither is that Google found the perfect representation for enterprise knowledge. It did not. The first is that the format is specified. The wiki-as-knowledge-base pattern has been reappearing for more than a year under a dozen bespoke conventions, and OKF pins down the small set of rules that let those conventions interoperate, without dictating the tooling. The second is that it makes the first layer of the custody problem concrete. It turns “own your context” from a slogan into files, metadata, links, citations, indexes, and logs.

In other words, it makes the custody problem file-shaped.

## The first custody layer

Part One argued that the durable enterprise AI asset is not the model. The model is increasingly rentable. The durable asset is the learning loop around the model, the documents, tickets, chats, code, corrections, feedback, evaluations, and institutional patterns that agents read from and write back to. That argument can sound abstract until you ask a simple question. Where does the loop live?

If the loop lives only inside a vendor’s memory system, the organization may be able to use it, search it, even administer it. None of that is the same as holding it. Custody starts lower than strategy. It starts with format. Can the firm inspect the knowledge its agents depend on, diff the changes, and move the corpus somewhere else? Can a human read it without a proprietary interface, and an agent parse it without a vendor SDK? Can the same body of knowledge survive a new model, a new index, a new agent framework, or a new platform?

Format is not enough. But custody means holding. Without format, there is nothing to hold. That is the quiet importance of OKF. It gives the knowledge layer somewhere to stand.

## What OKF actually is

OKF is not a database. It is not a vector store. It is not an agent framework. It is not a governance platform. It is a format.

The v0.1 specification describes it as an open, human- and agent-friendly way to represent the metadata, context, and curated insight around data and systems. The unit of distribution is a knowledge bundle, which is a directory tree. Most files are concept documents, and a concept can describe a table, an API, a metric, a playbook, a business process, or an abstract idea. Each concept file has two parts, YAML frontmatter for structured metadata and a markdown body for the explanation.

The required metadata is deliberately small. A concept needs a type. Everything else is optional, including title, description, resource, tags, and timestamp, alongside producer-defined fields. The body is plain markdown. Concepts link to each other with standard markdown links, which turns the directory into a graph richer than the folder hierarchy. OKF also defines a citation convention, a numbered # Citations section that gives claims a trail back to the external sources behind them. index.md files give navigation and log.md files record update history. Both are optional.

This is not glamorous architecture. That is the point. Plain files have properties enterprise AI needs more than it admits. They are readable, diffable, and at home in version control. They can be exported, indexed, linted, reviewed, backed up, bundled, and moved. A human can read one in a text editor and an agent can read it in a retrieval pipeline. A proprietary memory store may have better product polish. A directory of files has custody properties.

The first layer of ownership is not whether you trained the model. It is whether the knowledge the model depends on can leave the system that currently serves it.

## The format is permissive on purpose

The most interesting design choice in OKF is not strictness. It is tolerance. Consumers are expected to tolerate unknown types, unknown fields, missing optional metadata, missing indexes, and even broken links. That sounds loose if you think like a database designer. It makes sense if you think like someone trying to represent a living corpus that agents are partly maintaining.

Enterprise knowledge is messy and grows unevenly. Some of it is structured and some is prose, some is fresh and some is stale, some is authoritative and some is a useful clue that still needs review. A brittle schema would force a bad choice, either rejecting too much or pretending the corpus is cleaner than it is. OKF takes the other path. It standardizes the small set of conventions needed for interoperability and leaves the rest flexible enough for real corpora. The format should make knowledge portable without pretending knowledge work is tidy.

## Three things people will conflate

The OKF conversation gets confusing because three layers sit near each other, and people collapse them into one story.

The first is the open format. This is the part that matters for knowledge custody, the markdown, the YAML frontmatter, the bundle structure, the concept documents, the links, the citations, the indexes, the logs, and the conformance rules. It is portable by design.

The second is Google’s reference implementation and tooling. The GitHub repository ships sample bundles, a proof-of-con