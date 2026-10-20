---
title: "Vector index choice (revised)"
author: "eval"
slug: "lc-new-index"
supersedes: ["lc-old-index"]
published: "2026-07-01"
---
The vector index choice was revised to flat int8 vectors in rebuildable files; HNSW was unnecessary at this scale.
