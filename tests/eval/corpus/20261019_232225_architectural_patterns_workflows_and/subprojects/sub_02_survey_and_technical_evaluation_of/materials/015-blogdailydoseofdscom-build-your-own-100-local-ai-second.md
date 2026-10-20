---
title: Build Your Own 100% Local AI Second Brain - by Avi Chawla
url: https://blog.dailydoseofds.com/p/build-your-own-100-local-ai-second
final_url: https://blog.dailydoseofds.com/p/build-your-own-100-local-ai-second
source_type: social
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:47+00:00
published: 2026-05-07
content_digest: 093b8acc47a3e8d2
---

# Daily Dose of Data Science

SubscribeSign in

# Build Your Own 100% Local AI Second Brain

### How the best builders in tech are all converging on AI second brains

Avi Chawla

May 07, 2026

8

1

Share

### A tricky LLM interview question

Your RAG system scores 90% retrieval accuracy on 5k company docs.

But scaling to 500k docs drops the accuracy to just 50%, with the same embedding model and retriever.

Why did this happen?

The simplest answer is that more documents mean more competition for the top-k retrieval slots. That is true, but it doesn’t explain why accuracy drops this dramatically.

The answer comes down to how enterprise docs are distributed in the embedding space.

Today, a single product decision in a company generates meeting transcripts, Slack threads, Confluence docs, Jira tickets, and email threads.

They are related to the same event, so they all land in a similar region of the embedding space.

As the company operates over months, this pattern repeats for every project/customer/roadmap, and the embedding space fills up with clusters of closely related documents.

But all related docs don’t contain the same facts.

Slack thread covers the decision made

Jira has the implementation deadline

Confluence has the technical spec

Email thread has the customer request

When a query is about a specific fact (like a deadline), the answer lives in one of those docs.

At a 5K corpus size, there might be 3-5 docs touching that topic, and the correct one easily lands in the top-k results.

But at a 500K corpus size, there could be 40-60 total docs, and the one containing the actual answer can easily get pushed out of the top-k by other topically relevant docs, degrading retrieval.

A recent research paper from Onyx documented this.

The researchers used their newly open-sourced EnterpriseRAG-Bench dataset.

EnterpriseRAG-Bench Data Repo

It has 500k+ synthetic enterprise documents spread across Slack, Gmail, Jira, GitHub, Confluence, Google Drive, HubSpot, Fireflies, and Linear, with realistic noise like misfiled documents, near-duplicates, and conflicting versions.

They ran the same retrievers at five corpus sizes from 5K to 500K.

Vector search accuracy dropped from 90.7% at 5K documents to 50.6% at 500K docs.

BM25 degraded more gracefully, from 85.8% to 68.4%.

At every scale, higher neighborhood density in the embedding space monotonically correlated with lower recall.

The practical implication here is that retrieval accuracy on a 5k test set tells you almost nothing about production-scale performance.

Always test at a realistic volume to measure the neighborhood density in your embedding space to estimate how much headroom the retriever actually has.

The entire EnterpriseRAG-Bench dataset (500K docs with questions, and the whole evaluation harness) is open-source.

Run your retriever against it at 5K, then at 500K, and see where your own accuracy curve breaks.

You can find the GitHub repo here →

EnterpriseRAG-Bench Data Repo

### Build your own 100% local AI second brain

Karpathy’s LLM Wiki compiles raw sources into a persistent Markdown wiki with backlinks and cross-references.

The LLM reads papers, extracts concepts, writes encyclopedia-style articles, and maintains an index. The knowledge is compiled once and kept current, so the LLM never re-derives context from scratch at query time.

This works because research is mostly about concepts and their relationships, which are relatively stable.

But this pattern breaks when you apply it to actual work, where context evolves across conversations constantly.

A compiled wiki would have a page about a project, but it wouldn’t track that a deadline agreed in one email thread and moved to a later date in another thread, while the team still assumed the original date.

A wiki doesn’t track ground truth effectively.

We wrote about this recently, and Karpathy liked it:

Tracking this requires a different data structure altogether. Not a wiki of summaries, but a knowledge graph of typed entities where people, decisions, commitments, and deadlines are separate nodes linked across conversations.

Rowboat (GitHub Repo) is an open-source implementation of exactly this, built on the same Markdown-and-Obsidian foundation that Karpathy uses, but extended into a work context.

The way it works is that it ingests conversations from Gmail, Granola, and Fireflies, and instead of writing a summary page per topic, it extracts each decision, commitment, and deadline as its own Markdown file with backlinks to the people and projects involved.

That’s structurally different from a wiki because:

A wiki page about “Project X” gives you a summary of what was discussed.

But a knowledge graph gives you every decision made, who made it, what was promised, when it was promised, and whether anything has shifted since.

Next, let’s set up Rowboat from scratch, walk through what the knowledge graph looks like on disk, and see what happens once the graph is live.

#### Setup

Rowboat is a local desktop app (Mac, Windows, Linux) that runs entirely on your machine and lets you bring your own model from Ollama, LM Studio, or any hosted API.

It stores everything in ~/.rowboat/ as plain Markdown files in an Obsidian-compatible vault. If you already use Obsidian for notes, you can point it at the same vault and browse Rowboat’s knowledge graph alongside your own files.

If you don’t use Obsidian, the Markdown files are still readable in any editor.

To start, download the app here: rowboatlabs.com/downloads

Next, open ~/.rowboat/config/models.json and point it at whatever you’re running.

For a hosted provider, you can specify:

{
"provider": {
"flavor": "openai",
"apiKey": "sk-..."
},
"model": "gpt-4o"
}

Anthropic, Google, and OpenRouter use the same structure, so you can just swap the flavor property above. If you want inference fully on your machine, Ollama works too:

{
"provider": {
"flavor": "ollama",
"baseURL": "http://localhost:11434"
},