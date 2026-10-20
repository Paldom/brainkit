---
title: Self-Hosting AI Models: A Practical Guide to Building Your Own Stack
url: https://infinum.com/blog/self-hosting-ai-models-a-practical-guide/
final_url: https://infinum.com/blog/self-hosting-ai-models-a-practical-guide/
source_type: social
providers: brave
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:34+00:00
published: 2026-04-16
content_digest: 1ed2583e5d68689b
---

We use cookies to optimise and continuously improve our website for individual users like you. By clicking “Accept all”, you accept storing of cookies on your device. Find out more at our Privacy Policy and Cookies Policy.

Manage

Accept all

We need your consent to continue

Required cookies

Cookies for the basic functionality of the Infinum website.

Always on

Performance cookies

Performance cookies monitor only the performance of the site as the user interacts with it. These cookies don't collect identifiable information about the visitor. Data is anonymous.

Targeting cookies

Advertising and analytics service cookies that create day-to-day statistics and show ads on their site and on the advertiser’s partners websites.

Confirm choices

Reject all

Accept all

Privacy Policy

|

Cookies Policy

Skip to main content

Expertise

Resources

Delivered

Events

Newsroom

Open Source

Handbook

Accessibility

Certifications

Brand Experience

AI Transformation Consulting

Product Strategy and Design

Mobile and Web Apps

Artificial Intelligence and Data

Custom IoT Solutions

Enterprise Platforms

Cybersecurity

Work

About

Blog

Careers

Contact

Expertise

Brand Experience

AI Transformation Consulting

Product Strategy and Design

Mobile and Web Apps

Artificial Intelligence and Data

Custom IoT Solutions

Enterprise Platforms

Cybersecurity

Resources

Delivered

Events

Newsroom

Open Source

Handbook

Accessibility

Certifications

Work

About

Careers

Blog

Contact

Contact

#
Self-Hosting AI Models: A Practical Guide to Building Your Own Stack

Organizations self-host AI models to maintain data ownership, meet contractual obligations, and exercise control over security, but the resulting infrastructure complexity is significant. This guide documents a production implementation using vLLM on AWS EKS, covering GPU instance selection, quantization, automatic prefix caching, distributed caching via LMCache, tensor parallelism, speculative decoding, and disaggregated prefilling. Infrastructure costs range from $400/month for 7B-parameter models to $30,000/month for 100B+ parameter deployments using open-weight models, including Llama 3, Mistral, and DeepSeek-R1.

Vjekoslav Drakšić

DevOps Engineer

7 min Read in AI & data,Innovation

Published Apr 16, 2026

Thanks!

Many organizations now want full ownership of their AI infrastructure. The motivation for self-hosting ranges from data ownership requirements and contractual obligations to maintaining the highest level of system security.

This post covers the infrastructure decisions, model selection tradeoffs, and performance optimization techniques we encountered while building a self-hosted multi-model inference stack. Security architecture and model licensing are out of scope here as both deserve their own deep dives. Still, everything about building the infrastructure and making it perform is fair game.

Here’s what our stack looked like:

An open-source inference engine (vLLM production stack)

A multi open-weight model setup

Accelerated computing instances on AWS

A scalable, highly available EKS cluster

##
vLLM as an inference engine

There are several open-source inference engines to choose from, including LMDeploy, SGLang, and TensorRT-LLM.

We chose vLLM for its performance, broad model support, extensive documentation, and built-in multi-model type routing.

Their production stack ships with an infrastructure diagram you can extend for your own setup, but the core components are:

Request router

An OpenAI-compatible API layer. It uses prefix-aware routing to direct repeat context to the same worker, reducing time to first token. In a multi-model setup, the router handles requests by endpoint, model name, and worker assignment.

Workers

vLLM instances running on GPU nodes. The stack handles tensor parallelism across multiple GPUs for large models out of the box.

KV cache storage

In a multi-worker setup, previously computed state is retrieved from LMCache, which delivers significant performance gains, especially for models like GPT OSS.

Observability stack

Prometheus and Grafana for monitoring.

###
Simplified end-to-end flow

The request router analyzes the incoming prompt’s prefix and directs it to a worker that already holds that context in memory. The worker processes the request with optimized block-based memory management, pulling previously computed states from a per-node or cluster-wide cache, and generates the response.

##
Choosing the right hosting environment

The AI hosting landscape is competitive. The vLLM production stack has cloud deployment support for AWS, Azure, and GCP, and project velocity matters a lot at this stage.

This is why we chose AWS EKS. The cost savings from alternative providers did not justify the increased setup complexity.

Specialty cloud hosting providers are cheaper, but they often offer unmanaged environments. That means you handle all the heavy lifting yourself, like networking, orchestration, GPU scheduling, the lot.

###
On-premise considerations

Buying hardware immediately is an operational risk. This is true even if you have predictable workloads.

We recommend a phased approach:

#### Phase 1: Model PoC

Optional if you already know the model you want. Use managed services like AWS Bedrock to find the sweet spot between model size and reasoning capability. The open-weight model catalogue is expanding fast and the setup is minimal.

#### Phase 2: Cloud PoC

Use cloud-managed Kubernetes to prototype your multi-model infrastructure. Test different GPU offerings, benchmark your setup, and figure out your TPM and RPM requirements. Test your open-source model choices without locking into expensive hardware early.

#### Phase 3: On-premise refinement

Once you understand your patterns and limits, modify your existing Kubernetes cluster for an on-premise deployment. This is significantly easier than starting here from scratch.

##
Choosing the right model

To simplify the 