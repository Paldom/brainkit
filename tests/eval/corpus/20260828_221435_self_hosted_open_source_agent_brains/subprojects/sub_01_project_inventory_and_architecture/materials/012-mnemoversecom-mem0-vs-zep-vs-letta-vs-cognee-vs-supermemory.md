---
title: Mem0 vs Zep vs Letta vs Cognee vs Supermemory (Q3 2026) | Mnemoverse Docs
url: https://mnemoverse.com/docs/library/ai-memory-solutions-2026-q3
final_url: https://mnemoverse.com/docs/library/ai-memory-solutions-2026-q3
source_type: social
providers: brave, grok, tavily
topic: Project inventory and architecture comparison of self-hosted / open-source agent brain and memory systems as of 2026 — gbrain, Letta (MemGPT), Sylph, mem0, Zep, Cognee, Basic Memory, Khoj and peers — with license, storage backend, retrieval design, maturity and activity signals for each.
fetched_at: 2026-08-28T20:40:08+00:00
published: 2026-08-06
content_digest: 6125b5cb81ec6445
---

Skip to content

MnemoverseDocs

SearchK

Main Navigation Get StartedAPILibraryResearchBenchmarksConsole

Appearance

Menu
Return to top

Sidebar Navigation

## Get Started

Quick Start

API Reference

Agent Setup

Make Agents Remember

Rooms (beta)

## Integrations

Claude Code

Claude Desktop, Web & Mobile

### Editors

Cursor

VS Code

Windsurf

ChatGPT

Python SDK

MCP Server

Remote MCP (OAuth)

## Use Cases

Coding Assistants

Universal AI Chat

Conversational Agents

Agent Frameworks

## Platform

Overview

Multi-Tenant Setup

## More

Overview

Pricing

Security

## Library

Overview

### Agent Memory

Topic overview

AI Agent Memory: What It Is

What Your Agent Is Allowed to Believe

Knowledge Graph vs Retrieval

A2A Protocol Explained

A2A vs MCP

Shared Memory for Multi-Agent Systems

The Missing Layer: Agent Memory Interop

A2A Integration How-To (Python)

The A2A Agent Card

Hebbian Memory for AI Agents

Rescorla-Wagner for Agent Memory

Agent Memory Feedback: The Missing Signal

Is Mnemoverse a Vector Database?

RAG vs Agent Memory: What the Source Code Shows

Nowhere to Put the Disagreement

Knowledge-Graph Memory for AI Agents

Claude's Global Workspace: Why AI Memory Lives Outside

AI Introspection: Why a Voice Is Not an Audit

The Jacobian Lens, Explained

What Is an Agent OS? Six Meanings

### Secrets & Trust

Topic overview

Why AI Agents Nag You About Secrets

Memory Poisoning: The Patient Path to Your API Keys

Shared Memory Poisoning: One Bad Write, Many Agents

A Credential the LLM Never Sees

The Trust-Model Spectrum for Agent Secrets

Prompt Injection Is a Credential-Exfiltration Attack

How Do Two AI Agents Trust Each Other?

Least Privilege for AI Agents

### Memory Science

Topic overview

Why Agent Memory Needs Sleep

Why Does Memory Have So Many Names?

Transactive Memory: Who Remembers What in a Team

Memory, From DRAM to Agents: One Word, Twelve Worlds

Episodic vs Semantic Memory: Tulving for AI Agents

Hopfield Networks & Associative Memory

Is Attention a Hopfield Network?

Bernard Widrow: LMS to Cognitive Memory

Geoffrey Hinton: The Boltzmann Machine

Jeff Hawkins: Hierarchical Temporal Memory

Schema Formation & Memory Consolidation

Working Memory: Capacity, Models & AI Context

Self-Organizing Memory: ART, SOM & GNG

Multimodal Memory: Cross-Modal Binding

### Benchmark Wars

Topic overview

Evaluating AI Agent Memory

LangChain / LangSmith Evaluation

LLM-as-a-Judge & Judge Leniency

Judges, Good & Evil â Judge Variance

Can You Trust an LLM Judge? A Field Manual

AI Memory Benchmarks â Field Guide

Hugging Face Evaluate (BLEU, ROUGE & more)

BLEU vs ROUGE vs F1 vs SARI

DeepEval (Pytest for LLM Evals)

### Context Builder & Orchestration

Topic overview

KV-Cache & Context Engineering

What Breaks Prompt Caching

MCP Federation in 2026

CLAUDE.md, AGENTS.md and Cursor Rules

What Is an MCP Memory Server?

Memory MCP: Persistent Memory for Agents

Memory MCP Servers Compared

Stateless MCP: Where Agent Memory Lives Now

Context Engineering Needs a Compiler

Context Compiler vs Orchestration

Deterministic vs LLM Context Assembly

Context Optimizer

Context Budgeting

### World Representation

Topic overview

Is Memory Hyperbolic? What Neuroscience Shows

Building Memory That Scales

Hypergraph vs Hyperbolic Graph

How AI Agents Navigate Knowledge Graphs

The GraphRAG Tax

Graph Memory MCP Servers Compared

Bitemporal Memory: The Missing Axis

Provenance: The Missing Who

Deduplication: The Missing Error Rate

Who Wins When Agents Disagree?

The Independence Illusion

### Light Reading

Topic overview

Ontology vs Schema vs Topology

The AI Agent Memory Crisis

AI Memory Landscape 2026

AI Memory Solutions Compared: Q3 2026

Agent Memory Is Not a Database

Memory Is Becoming a Procurement Decision

Workflow Intelligence Ships as a Primitive

When AI Cites What Doesn't Exist

Market Landscape 2025

## Research

Overview

SLoD (arXiv:2603.08965)

### Benchmarks

Methodology â how we measure honestly

LoCoMo (primary â conversational memory)

BEAM (10M-token scale)

HotpotQA

MuSiQue

LongMemEval

Tensor-Hyperbolic Graphs

## Vision

Manifesto

Design Language

Sources

## Legal

Terms of Service

Privacy Policy

Cookies Policy

Refund & Cancellation

Free Tier & Startup Program

On this page

Edward IzgorodinÂ·Published Jul 21, 2026Updated Aug 6, 2026

# Five AI memory systems, five different definitions of memory â

TL;DR

Mem0, Letta, Zep/Graphiti, Cognee, and Supermemory make five different architectural bets on what agent memory is. They are not interchangeable storage layers.

The first decision is integration posture: drop-in API, agent runtime, graph library, data pipeline, or managed context engine. Self-host reality is often worse than the license label suggests.

Only Zep/Graphiti offers native bi-temporal validity windows, the sharpest technical divider here.

Vendor benchmark numbers do not survive reproduction â Mem0's LongMemEval figure fell to 73.8% under Maximem's harness (Maximem is itself a memory vendor). Always ask for the harness, and who runs it.

An agent memory choice starts before retrieval quality. It starts with a boundary question: how much of the application should the memory system own?

Choosing a memory layer for an AI agent in mid-2026 means picking an architecture, not just a feature list. Five funded systems â Mem0, Letta, Zep/Graphiti, Cognee, and Supermemory â each answer the boundary question differently.

This is a dated Q3 2026 edition of a recurring comparison. Repository metrics are snapshots from July 20, 2026, and a future edition will supersede it. For the wider market â platform memory from OpenAI, Anthropic, Google, and Microsoft, plus the funding picture â see the parent AI memory landscape 2026.

Correction, 2026-08-03: an earlier version of this page said Mem0's self-editing pipeline resolves conflicting facts on write, and that OSS graph memory runs over Neo4j or Memgraph. Both 