---
title: Memanto: Typed Semantic Memory with Information-Theoretic Retrieval for Long-Horizon Agents
url: https://arxiv.org/html/2604.22085v1
final_url: https://arxiv.org/html/2604.22085v1
source_type: social
providers: brave
topic: Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
fetched_at: 2026-08-28T20:52:06+00:00
published: 2026-04-23
content_digest: 445a79c28ca27fe0
---

Report GitHub Issue×
Title:
Content selection saved. Describe the issue below:
Description:
Submit without GitHubSubmit in GitHub
arXiv is now an independent nonprofit!Learn more×

Back to arXiv
Why HTML?Report IssueBack to AbstractDownload PDF
Abstract

I Introduction
I-AContributions

II Background and Related Work
II-ACognitive Foundations of Memory Taxonomy

II-BMemory Surveys and Taxonomies (2024 to 2026)

II-CKnowledge Graph Based Memory Systems (2024 to 2026)

II-DThe Indexing and Ingestion Bottleneck

II-EEvaluation Benchmarks

III Design Principles and Architecture
III-ASix Desiderata for Production Agentic Memory

III-BSystem Overview

III-CThe Moorcheh Foundation: Information Theoretic Search

III-DTyped Memory Schema

III-EConflict Resolution

III-FTemporal Versioning

III-GSession and Namespace Management

III-HDaily Intelligence

IV Experimental Evaluation and Results
IV-ABenchmarks and Evaluation Protocol

IV-BProgressive Ablation Study
IV-B1 Stage 1: Naive Baseline

IV-B2 Stage 2: Recall Expansion

IV-B3 Stage 3: Prompt Optimization

IV-B4 Stage 4: Maximum Recall

IV-B5 Stage 5: Inference Model Upgrade

IV-CFinal Results by Category

IV-DComparative Results

IV-EThe Memory Tax: Overhead Analysis

V Discussion
V-AWhy Optimized Retrieval Outperforms Graph Complexity

V-BThe Recall over Precision Principle

V-CConflict Resolution as a Production Necessity

V-DDeterminism for Agentic Stability

V-ELimitations and Future Work

References

-FSoftware Configuration

-GHardware Requirements

-HMemory Type Assignment

-IFinal Retrieval Parameters

License: CC BY-SA 4.0

arXiv:2604.22085v1 [cs.AI] 23 Apr 2026

# Memanto: Typed Semantic Memory with Information-Theoretic Retrieval for Long-Horizon Agents

Seyed Moein Abtahi
Affiliation: Moorcheh AI

EdgeAI Innovations

seyedmoein.abtahi@ontariotechu.net
Rasa Rahnema
Affiliation: Moorcheh AI

EdgeAI Innovations

ryrahnem@uwaterloo.ca
Hetkumar Patel
Affiliation: Moorcheh AI

EdgeAI Innovations

hetkumardineshbhai.patel@sheridancollege.ca
Affiliation: Neel Patel
Affiliation: Moorcheh AI

EdgeAI Innovations

neel@edgeaiinnovations.com
Majid Fekri
Affiliation: Moorcheh AI

EdgeAI Innovations

majid.fekri@edgeaiinnovations.com
Tara Khani
Affiliation: Moorcheh AI

EdgeAI Innovations

tara.khani@edgeaiinnovations.com

Abstract
The transition from stateless language model inference to persistent, multi session autonomous agents has revealed memory to be a primary architectural bottleneck in the deployment of production grade agentic systems. Existing methodologies largely depend on hybrid semantic graph architectures, which impose substantial computational overhead during both ingestion and retrieval. These systems typically require large language model mediated entity extraction, explicit graph schema maintenance, and multi query retrieval pipelines. This paper introduces Memanto, a universal memory layer for agentic artificial intelligence that challenges the prevailing assumption that knowledge graph complexity is necessary to achieve high fidelity agent memory. Memanto integrates a typed semantic memory schema comprising thirteen predefined memory categories, an automated conflict resolution mechanism, and temporal versioning. These components are enabled by Moorcheh’s Information Theoretic Search engine, a no indexing semantic database that provides deterministic retrieval within sub ninety millisecond latency while eliminating ingestion delay. Through systematic benchmarking on the LongMemEval and LoCoMo evaluation suites, Memanto achieves state of the art accuracy scores of 89.8 percent and 87.1 percent respectively. These results surpass all evaluated hybrid graph and vector based systems while requiring only a single retrieval query, incurring no ingestion cost, and maintaining substantially lower operational complexity. A five stage progressive ablation study is presented to quantify the contribution of each architectural component, followed by a discussion of the implications for scalable deployment of agentic memory systems.

Index Terms: Agentic AI, long term memory, retrieval augmented generation, information theory, vector search, semantic memory, large language models, autonomous agents

## I Introduction

Memory has become a fundamental architectural component in the design of foundation model based agents [1, 2]. As large language models transition from single turn question answering systems to autonomous agents capable of multi step reasoning, tool utilization, and long horizon task execution [3, 4], their inherent limitation, namely the lack of persistent state across sessions, has emerged as a central engineering challenge in the development of agentic artificial intelligence systems.

Industry projections indicate that the agentic artificial intelligence market will expand from 7.8 billion dollars to more than 52 billion dollars by 2030. Gartner further estimates that 40 percent of enterprise applications will incorporate AI agents by the end of 2026, compared to less than 5 percent in 2025. This accelerated adoption has generated a critical need for memory infrastructure that satisfies production requirements, including high accuracy, low latency, cost efficiency, and reduced operational complexity.

Current approaches within the field remain heterogeneous and increasingly complex. A range of frameworks, including Mem0 [5], Zep [6], Letta [7], and A-MEM
[8], propose architectures that integrate knowledge graphs, temporal graph databases, multi query retrieval strategies, and recursive large language model driven ingestion pipelines. Although these systems demonstrate competitive benchmark performance, they introduce substantial computational and operational overhead. This paper characterizes this phenomenon as the “Memory Tax”, defined as the cumulative increase in compute cost, latency, and system complexity associated with memory ingestion and retrieval processes.

Memanto, built upon Moorcheh’s Information Theoretic