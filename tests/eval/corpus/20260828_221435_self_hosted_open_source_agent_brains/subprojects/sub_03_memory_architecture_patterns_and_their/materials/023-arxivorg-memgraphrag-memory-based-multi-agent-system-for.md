---
title: MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation
url: https://arxiv.org/html/2606.00610v1
final_url: https://arxiv.org/html/2606.00610v1
source_type: web
providers: brave, gemini
topic: Memory architecture patterns and their measured trade-offs: hierarchical/paged context, vector RAG, knowledge graphs, plain-file/git stores, background consolidation — including retrieval quality, cost, and failure modes like context rot and memory poisoning.
fetched_at: 2026-08-28T20:52:09+00:00
published: 2026-05-30
content_digest: 382d5c04d2cbf066
---

Report GitHub Issue×
Title:
Content selection saved. Describe the issue below:
Description:
Submit without GitHubSubmit in GitHub
arXiv is now an independent nonprofit!Learn more×

Back to arXiv
Why HTML?Report IssueBack to AbstractDownload PDF
Abstract.

1 Introduction

2 Problem Statement
2.1 Key Definitions

2.2 Problem Formulation

3 Preliminary Study
3.1 Performance Degradation

3.2 Error Analysis

3.3 Discussion

4 Our Framework
4.1 MemGraphRAG Architecture

4.2 Memory-based Indexing Graph Construction
4.2.1 Thematic Denoising via Unified Schema Filtering

4.2.2 Consistency Maintenance via Global Adjudication

4.2.3 Structural Unification via Memory-Guided Bridging

4.3 Memory-guided Online Retrieval
4.3.1 Multi-Layer Memory Filtering

4.3.2 Structure-Aware Node Initialization

4.3.3 Personalized PageRank

5 Experiments
5.1 Experimental Setting

5.2 Generation Accuracy (Q1)

5.3 Retrieval Analysis (Q2)

5.4 Indexing Graph Adaptability Analysis (Q3)

5.5 Ablation Study (Q4)

6 Conclusion

Acknowledgements

References

A Additional Experiments
A.1 Ablation on Backbone LLMs

A.2 Graph Analysis

A.3 Case Study

B Related Work
B.1 Retrieval-Augmented Generation

B.2 Graph Retrieval-Augmented Generation

C Details of Preliminary Study

D Details of the Proposed Method
D.1 Key Definitions

D.2 MemGraphRAG architecture

D.3 Memory-based Indexing Graph Construction
D.3.1 Thematic Denoising via Unified Schema Filtering

D.3.2 Consistency Maintenance via Global Adjudication

D.3.3 Structural Unification via Memory-Guided Bridging

E Prompt Set
E.1 Memory-guided Online Retrieval
E.1.1 Multi-Layer Memory Filtering

E.1.2 Structure-Aware Node Initialization

E.1.3 Personalized PageRank

F Benchmark Dataset

G Implementation Details of Baselines

License: CC BY 4.0

arXiv:2606.00610v1 [cs.IR] 30 May 2026

# MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation
Conference: Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2; August 9–13, 2026; Jeju Island, Republic of Korea.Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD 2026), August 9–13, 2026, Jeju Island, Republic of KoreaISBN: 979-8-4007-2259-2/2026/08DOI: 10.1145/3770855.3818074CCS: Information systems Retrieval models and rankingCCS: Computing methodologies Information extraction; Knowledge representation and reasoning
Chuanjie Wu
Note: Contributed equally.
email: wuchuanjie@stu.xmu.edu.cnAffiliation: Xiamen University1, 2, Xiamen, China, Zhishang Xiang
email: xiangzhishang@stu.xmu.edu.cnAffiliation: Xiamen University2, 3, Xiamen, China, Yunbo Tang
email: tangyunbo@stu.xmu.edu.cnAffiliation: Xiamen University1, Xiamen, China, Zerui Chen
email: chenzerui1@stu.xmu.edu.cnAffiliation: Xiamen University1, Xiamen, China, Qinggang Zhang
email: qinggangzhang@jlu.edu.cnAffiliation: Jilin University, Changchun, China and Jinsong Su
Note: Corresponding author.
email: jssu@xmu.edu.cnAffiliation: Xiamen University1, 2, 3, Xiamen, China

© cc

Abstract.11footnotetext: School of Informatics22footnotetext: Key Laboratory of Digital Protection and Intelligent Processing of Intangible Cultural Heritage of Fujian and Taiwan,Ministry of Culture and Tourism33footnotetext: Institute of Artificial Intelligence
Retrieval-Augmented Generation (RAG) has become an essential method for mitigating hallucinations in Large Language Models (LLMs) by leveraging external knowledge. Although effective for simple queries, traditional RAG struggles with large-scale, unstructured corpora where information is highly fragmented. Graph-based RAG (GraphRAG) incorporates knowledge graphs to capture structural relationships, enabling more comprehensive retrieval for complex reasoning. However, existing GraphRAG methods rely on isolated, fragment-level extraction for graph construction, lacking a global perspective on the whole corpus. As a result, these methods frequently lead to thematically inconsistent, logically conflicting, and structurally fragmented graphs that degrade retrieval performance. In this paper, we propose MemGraphRAG, a novel framework that introduces a memory-based multi-agent system to ensure high-quality graph construction. Specifically, MemGraphRAG employs a collaborative society of agents supported by shared memory, which provides a unified global context throughout the extraction process. This mechanism allows agents to dynamically resolve logical conflicts and maintain structural connectivity throughout the corpus. Furthermore, we propose a memory-aware hierarchical retrieval algorithm tailored for the constructed graph. Extensive experiments on multiple benchmarks demonstrate that MemGraphRAG outperforms the state-of-the-art baseline models with comparable efficiency. Our code is available at https://github.com/XMUDeepLIT/MemGraphRAG.

Keywords: RAG, GraphRAG, Multi Agent, Agent Memory, Indexing Graph

††cc-license: byFigure 1. Comparison between existing GraphRAG and MemGraphRAG. Exiting GraphRAG performs isolated chunk-level extraction without the global view, resulting in a noisy and inconsistent indexing graph. While MemGraphRAG incorporates global memory to ensure global consistency.

## 1. Introduction

Recently, Retrieval-Augmented Generation (RAG) effectively extends the capabilities of Large Language Models (LLMs) by leveraging external knowledge (Gao et al., 2023; Lewis et al., 2020; Zhang et al., 2025c). However, existing RAG systems suffer from critical challenges in real-world scenarios. This is due to the unstructured and heterogeneous nature of large-scale corpora, where relevant information is often sparsely distributed. The contexts retrieved by RAG systems are often noisy and lack structural coherence. Although recent methods attempt to segment documents into smaller chunks for efficient indexing (Borgeaud et al., 2022; Izacard et al., 2023; Jiang et al., 2023), this strategy disrupts long-range dependencies and loses critica