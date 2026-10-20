---
title: GBrain vs Hindsight vs Mem0 vs Zep: Memory Compared
url: https://vectorize.io/articles/gbrain-vs-hindsight-vs-mem0-vs-zep
final_url: https://vectorize.io/articles/gbrain-vs-hindsight-vs-mem0-vs-zep
source_type: social
providers: brave
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:10+00:00
published: 2026-05-09
content_digest: 9f26a84913a9ba46
---

Vectorize

Open main menu

ProductPricingDocsBlogAbout

Star—
Hindsight Cloud

# GBrain vs Hindsight vs Mem0 vs Zep: Memory Compared

May 9, 2026

Four AI agent memory systems dominate the conversation right now: GBrain, the markdown-first personal brain Y Combinator CEO Garry Tan open-sourced in April; Hindsight by Vectorize, the production memory platform with BEAM SOTA at 10M tokens; Mem0, the most established commercial memory-as-a-service; and Zep, the temporal-knowledge-graph option for conversational AI.

Each is excellent for the audience it's designed for. None is the right answer for everyone. This GBrain vs Hindsight vs Mem0 vs Zep comparison covers what each system actually is, how the architectures differ, where the retrieval design wins, what integrations ship out of the box, what they cost, and which one fits which kind of team.

## At-a-Glance Verdict

Pick GBrain if you run OpenClaw or Hermes Agent, want to author skill workflows yourself, and value plain-text markdown ownership of your brain.

Pick Hindsight if you want production memory infrastructure that synthesizes structure from raw facts automatically (observations + mental models), with 40+ first-class integrations and a managed cloud option.

Pick Mem0 if you want a mature managed service with broad SDK language coverage and don't need graph or temporal reasoning.

Pick Zep if your application is conversational-first and temporal-graph reasoning is a hard requirement.

The detailed comparison is below.

## What Each System Is

### GBrain

GBrain is an open-source markdown-first knowledge system released by Garry Tan on April 5, 2026. ~14,000 GitHub stars, MIT license. Three layers: a Brain Repo (Markdown files in git), GBrain Retrieval (Postgres + pgvector with hybrid search), and an AI Agent Skills layer (34 markdown workflow files plus 30+ contract-first operations). Built specifically for OpenClaw and Hermes Agent operators running personal brains. Self-hosted only — no managed cloud. PGLite (WASM Postgres) for zero-config local mode.

For a deeper explainer, see What Is GBrain?.

### Hindsight

Hindsight is a production agent memory platform built by Vectorize and released in December 2025. ~12,800 GitHub stars, MIT license. Three core operations: retain, recall, reflect. Background consolidation creates observations — evidence-grounded beliefs with proof counts, freshness trends, and contradiction reconciliation — without operator-defined patterns. Mental models are user-defined topics that auto-refresh as new facts arrive. Multi-strategy retrieval (TEMPR) runs semantic + BM25 + graph traversal + temporal reasoning in parallel, fused via RRF and reranked with a cross-encoder. Available as managed cloud or self-hosted via Docker, Helm, or bare-metal pip install.

### Mem0

Mem0 is the most established commercial agent memory layer, with broad SDK language support (Python, Node, Go) and a fully managed cloud service. Server-side LLM extraction creates facts and preferences from conversations automatically. Dual memory scope (user-level and session-level). Single-strategy semantic retrieval with metadata filtering. Self-hosting exists but is less polished than the cloud experience.

### Zep

Zep is a long-term memory store designed specifically for conversational AI applications. Its distinctive feature is a temporal knowledge graph — every fact is timestamped so the agent knows when something was true. Strong on session management and user-level scoping. Cloud-managed; self-hosting is via Graphiti (the underlying graph engine), which is more involved.

## Quick Comparison Table

DimensionGBrainHindsightMem0Zep

Created byGarry Tan (YC CEO)VectorizeMem0 Inc.Zep

ReleasedApr 2026Dec 202520232023

LicenseMITMITOSS + paid cloudOSS + paid cloud

Source of truthMarkdown in gitStructured storeCloud DBTemporal KG

Auto-learningOperator-authored skills on cronObservations + mental models (auto)Fact extractionFact + temporal extraction

RetrievalHybrid (HNSW + tsvector + RRF)Multi-strategy (semantic + BM25 + graph + temporal) + rerankerSemantic + metadataSemantic + temporal graph

Multi-hop graph at retrievalHas edges, not primaryYesNoYes

Temporal reasoningNoYes (native)NoYes (graph-scoped)

Cross-encoder rerankingBacklink boostYesNoBasic

Managed cloudNoYesYesYes

Self-hostYes (PGLite or Postgres)Yes (Docker, Helm, pip on Linux/macOS/Windows)LimitedVia Graphiti

Multi-tenant by designNoYesYesYes

Model Context Protocol (MCP) serverNative + OAuth 2.1 (gbrain serve --http)Native + OAuth 2.1 (cloud)SDKSDK

Official integrationsOpenClaw + Hermes (skill packs)40+ across coding tools, frameworks, orchestration, gatewaysMajor frameworks via SDKMajor frameworks via SDK

Benchmark highlightBrainBench: P@5 49.1%, R@5 97.9% (240-page corpus)BEAM 10M tokens: 64.1% (SOTA)LongMemEval: varies by methodologyLongMemEval: solid conversational results

GitHub stars~14,000~12,800HighModerate

## Architecture: Markdown-First vs Structured-First vs Conversational-First

The four systems differ most sharply on what they treat as the source of truth and where automation lives.

GBrain treats human-readable markdown as primary. The agent reads, writes, and reasons against .md files in a git repo. The Postgres index serves queries; the markdown is what you keep, edit, and version-control. Automation runs operator-authored skills on cron — the signal-detector skill captures entity mentions on every message, enrich updates person and company pages, maintain audits citations and detects stale pages. The intelligence lives in markdown skill files the operator owns.

Hindsight treats the structured store as primary. Memories enter via retain, get extracted into facts, get consolidated into observations in the background, and feed mental models the operator defines as named topics. Automation is generative — the system synthesizes new structure (observations) from raw facts without operator-authored patterns. When new evidence contradicts an exist