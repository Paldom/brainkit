---
title: Should You Self-Host LLM Inference? Cost and Risk Guide
url: https://theaiengineer.substack.com/p/should-you-self-host-inference
final_url: https://theaiengineer.substack.com/p/should-you-self-host-inference
source_type: social
providers: exa, kimi
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:49+00:00
published: 2026-07-18T00:00:00.000Z
content_digest: a4a58a7d7a67ee63
---

#

SubscribeSign in

# Should You Self-Host Inference?

### The honest economics of running your own models, and the breakeven most teams get wrong.

Paolo Perrone

Jul 18, 2026

18

8

1

Share

Self-hosting inference pays off in two cases: you push past roughly two million tokens a day, or your data legally cannot leave your network. Below that line a hosted API is cheaper, and it spares your team from running GPUs at all. For most companies the winning setup sits in between, a hybrid that routes each request by how sensitive and how heavy it is.

🧭 Part of the ⚡ Hardware & Inference course

## TL;DR

API is the default, and under about a million tokens a day it is also the cheapest. No GPUs to babysit, and the smartest models are one call away.

Self-hosting wins on volume and control. You buy it for data sovereignty and scale, and you pay for it in engineering time.

The crossover sits near two million tokens a day, with one to two million a genuine toss-up. Below one million, the API wins on cost outright. Above ten million a day, owned hardware pays back in six to twelve months.

The MLOps hire costs more than the GPU. A single MLOps engineer runs roughly 160,000 dollars a year in salary alone, next to a few thousand dollars for the hardware underneath them. Someone has to patch CUDA errors at 2am and watch latency drift, and that salary is the line item teams forget.

Most teams land on a hybrid, and it runs 40 to 70 percent cheaper than going all-API. Sensitive and high-volume work stays local, hard reasoning goes to a frontier model over the wire.

📬 New here? Subscribe to get every issue of The AI Engineer free, and become dangerously good at AI engineering.

Subscribe

## The Three Ways to Run a Model

You shipped a feature on a hosted API. It works. Then finance forwards you the bill. It tripled in a quarter, because API spend scales with every new user you onboard. In the same week your security lead points out that customer records ride along inside every prompt, straight to OpenAI’s servers. Someone in standup finally says it out loud: should we just run our own?

It is the right question. The reflex answer, that owning hardware must be cheaper, is usually wrong.

Inference is the work of serving a trained model. Each prompt makes a GPU matrix multiply your text against the model’s weights to produce the reply one token at a time. It is the forever cost of AI, and we pulled it apart in Why is Inference Slow and Expensive?. Today we are not comparing models or serving engines. We are comparing where the model actually runs, because that one choice sets your bill, your compliance posture, and how much of your team’s week goes to infrastructure.

There are three places to run a model:

A hosted API. Someone else owns the GPUs. You send text, you get text, you pay per token.

A managed deployment. You rent GPUs from a provider that also runs the serving stack for you, but the model weights and your data stay inside your own cloud tenancy. An API endpoint without owning hardware or hiring ops.

Full self-hosting. Your weights, your GPUs, your serving engine. Nothing leaves, and you own every layer and every failure.

Three forces decide between them:

Volume: how many tokens a day you push.

Sovereignty: whether your data can legally leave your network.

People: whether you have engineers to keep GPUs alive.

And a fourth caps the whole thing: model access. The strongest models are closed-weight, so their makers never release the trained weights you would load onto your own GPUs. Which means the best model you can ever own is the best open-weight one, and any workload that needs a stronger model has to call a hosted API, no matter what the other three forces say. Weigh those four and the answer falls out. Let’s grade each option against them, simplest first.

### Hosted API

In one sentence: someone else runs the GPUs; you send text, you get text, and you pay per token with nothing to install.

👍 The good:

There is no infrastructure to own, so a single engineer ships in an afternoon. You get frontier models, the GPT-5 and Claude Opus and Gemini tier, that no consumer hardware can run.

You pay only for what you use, with no GPU sitting idle between requests.

The energy cost per query is small too: independent researchers put a typical GPT-4o (OpenAI’s flagship model) query at about 0.3 watt-hours, in the same range as a web search. The heavy spend in AI goes into training the model once, and serving it afterward is cheap1.

👎 The bad:

Every prompt leaves your network, and 44 percent of companies name data privacy as their top barrier to adopting AI for exactly this reason.

Cost climbs with usage, you also inherit rate limits and whatever pricing change the vendor ships next2.

🎯 Best for: spiky or unpredictable traffic, low-to-moderate volume, and anything that needs the smartest available model.

⚠️ The ceiling: migrate off at either of two lines:

Volume turns steady and large. Past roughly two million steady tokens a day, the per-token markup you pay the provider outgrows the GPUs and the salary you were avoiding, and renting stops being the cheap option.

Compliance hardens. The moment records cannot leave your network, every prompt to a hosted API becomes a violation.

📡 Practitioner signal: plenty of self-hosters still run their real work through a hosted model3. One engineer on r/selfhosted keeps a local stack for play and routes anything serious to a hosted frontier model, because the token cost is trivial next to the electricity his own hardware would burn.

## Managed Deployment

In one sentence: a provider runs the GPUs and the serving stack inside your own cloud tenancy, so your data stays home and you never hire an inference team.

👍 The good:

The data stays inside your own tenancy, which clears most compliance reviews.

You skip hiring MLOps, and most providers expose an OpenAI-compatible endpoint: the same request format your code already sends, so switchin