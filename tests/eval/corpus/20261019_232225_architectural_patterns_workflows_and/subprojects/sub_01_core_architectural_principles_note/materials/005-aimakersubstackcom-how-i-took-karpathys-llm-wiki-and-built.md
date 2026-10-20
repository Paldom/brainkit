---
title: How I Took Karpathy's LLM Wiki and Built an AI-Powered Second Brain in Obsidian
url: https://aimaker.substack.com/p/llm-wiki-obsidian-knowledge-base-andrej-karphaty
final_url: https://aimaker.substack.com/p/llm-wiki-obsidian-knowledge-base-andrej-karphaty
source_type: social
providers: brave
topic: Core architectural principles, note organization strategies, and retrieval workflows articulated by Andrej Karpathy for personal knowledge bases.
fetched_at: 2026-10-19T21:50:18+00:00
published: 2026-04-17
content_digest: 0256ec2ed643800e
---

#

SubscribeSign in

🧪 Maker Labs

# How I Took Karpathy's LLM Wiki and Built an AI-Powered Second Brain in Obsidian

### Claude Code as the engine, Obsidian Skills as the glue, and a downloadable starter kit so you can set it up this afternoon.

Wyndo

Apr 16, 2026

∙ Paid

174

7

26

Share

I’ve saved hundreds of articles, podcasts, and YouTube videos across Notion, Pocket, and browser bookmarks over the years. And every time I wanted to revisit something I’d read, I had to dig through all of it just to find it. Even when I did, that article sat in complete isolation from everything else I’d saved on the same topic.

When I moved everything into Obsidian (I wrote about this in my project management post), it solved the tool fragmentation. One vault, all markdown, all accessible to Claude Code. But my notes still didn’t talk to each other. An article about automation had no connection to a podcast about AI coding workflows, which had no connection to an essay about why writing forces you to think clearly.

I was the one responsible for drawing those lines. Because it took so much effort, I didn’t actually do it as often as I expected. That’s the honest truth about note‑taking systems like Zettelkasten and “building a second brain.” The theory is beautiful; in practice, the maintenance kills it.

Then I saw what Andrej Karpathy shared. You know how much he inspires me—this is the second workflow I’ve copied from him.

For anyone who doesn’t know him, Karpathy is one of the most respected AI researchers in the world.

Andrej Karpathy@karpathy

LLM Knowledge Bases

Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating

8:42 PM · Apr 2, 2026 · 19.6MViews

2.71KReplies · 6.58KReposts · 55.4KLikes

He described a pattern he called an “LLM Wiki.” The idea is simple but the shift is significant: instead of you maintaining a knowledge base and occasionally asking AI questions about it, the LLM builds and maintains the entire knowledge base for you.

You collect raw sources. Articles, papers, book notes, podcast takeaways, anything. You drop them into a folder. Then you tell the LLM to “compile” them into a wiki. It reads every source, writes summary pages, creates pages for key people and concepts, and cross-references everything. A single article might touch 10-15 pages across your wiki. The LLM handles all the bookkeeping you’d never do yourself.

Karpathy put it this way:

“Obsidian is the IDE, the LLM is the programmer, the wiki is the codebase.”

You rarely ever write or edit the wiki manually. That’s the domain of the LLM.

And the part that hit me hardest: this compounds. Every new source the LLM ingests makes the whole wiki smarter. It becomes a network that grows denser over time. An article about Tim Dettmers’ automation framework gets connected to Addy Osmani’s AI coding workflow, which gets connected to Dan Koe’s essay on why writing is thinking. Three completely different topics, three different authors, one thread running through all of them that I never would have drawn on my own.

Here’s the build: Obsidian as the interface, Claude Code as the agent, and a set of Obsidian Skills that Steph Ango (the CEO of Obsidian) released to teach Claude how to write in Obsidian’s native language. Wikilinks. Callouts. Canvas. A CLI (Command Line Interface) for running the whole thing from the terminal. If you’re an Obsidian nerd, that last piece is what makes this actually work.

I’ve been running this system for my own interests. AI, human psychology, personal productivity, health and fitness, building a business. All of it flowing into one knowledge base where everything connects to everything else.

🚨 Heads up: AI Maker Lab pricing goes up tonight, from $10/month to $15. If you enjoyed this post and want the full library of 25+ paid blueprints, plus everything coming next (video walkthroughs, expert conversations, monthly Q&A), today is the last day to lock in the current rate.

Subscribe

## What’s Inside This Post

This post is the complete blueprint for building the system I just described. Not the theory. The exact folder structure, the commands, the schema, and a starter kit you can download and set up this afternoon.

Here’s what you’ll walk away with:

The Three-Layer Architecture: How the knowledge base is organized: raw sources (your immutable reading material), the wiki (LLM-generated summary pages, cross-references, and concept maps), and the schema (the CLAUDE.md file that turns Claude from a generic chatbot into a disciplined wiki maintainer). I’ll show you how data flows between layers and why this structure makes the whole system work.

The Three Operations That Run the System: The exact slash commands I use daily: /ingest-url (feed it a URL, Claude extracts the article and compiles it into the wiki, touching 5-15 pages in a single pass), /process-inbox (fleeting thoughts and quick notes get classified and integrated automatically), and /lint-wiki (a health check that finds broken links, orphan pages, contradictions, and content gaps the wiki suggests you research next).

Obsidian Skills (The Missing Piece): A set of agent skills that teach Claude how to work fluently with Obsidian’s native features. Wikilinks, callouts, frontmatter, the Obsidian CLI, database views with Bases, and visual canvases. These are what turn Obsidian from “a folder of markdown files” into a proper knowledge management platform that an LLM can operate natively.

Real Examples of the System in Action: I made a video to walk you through this whole process so you can apply it on your own.

The Complete Starter Kit + Setup Guide: A downloadable starter kit with the entire system pre-built: folder structure, three slash commands, all five Obsidian Skills, the schema, templates for books and podcasts, and a