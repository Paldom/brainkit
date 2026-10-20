---
title: I built a private, self-hosted AI home lab with Docker (offline ChatGPT + monitoring + backups) - DEV Community
url: https://dev.to/syed_masoodshah_1984/i-built-a-private-self-hosted-ai-home-lab-with-docker-offline-chatgpt-monitoring-backups-56l4
final_url: https://dev.to/syed_masoodshah_1984/i-built-a-private-self-hosted-ai-home-lab-with-docker-offline-chatgpt-monitoring-backups-56l4
source_type: social
providers: exa
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:48+00:00
published: 2026-08-04T00:00:00.000Z
content_digest: 1a6bf4de0cd1b09c
---

Skip to content

Powered by Algolia

Log in

Create account

## DEV Community

Add reaction

Like

Unicorn

Exploding Head

Raised Hands

Fire

Jump to Comments

Save

Boost

Copy link
Copied to Clipboard

Share to X

Share to LinkedIn

Share to Facebook

Share to Mastodon

Report Abuse

Syed Masood Shah
Posted on Aug 4

#
I built a private, self-hosted AI home lab with Docker (offline ChatGPT + monitoring + backups)

#selfhosted#ai#docker#devops

Like a lot of people, I got tired of two things: paying monthly for AI tools, and not knowing where my data ends up. So I built a small, self-hosted "AI home lab" that runs entirely on my own machine — and packaged it so anyone can deploy it in about 5 minutes.

Here's what's in it and how it fits together.

##
The stack

Three independent Docker Compose stacks, each solving one problem:

###
🤖 Private AI (Ollama + Open WebUI)

A ChatGPT-style web interface that runs 100% offline. Ollama is the model engine; Open WebUI is the chat frontend. You pull a model (llama3.2, mistral, qwen2.5…) and chat privately — nothing leaves your box.

services:ollama:image:ollama/ollama:latestvolumes:-ollama-data:/root/.ollamaopen-webui:image:ghcr.io/open-webui/open-webui:mainports:-"3000:8080"environment:-OLLAMA_BASE_URL=http://ollama:11434

The two services talk over an internal Docker network — only the web UI is exposed.

###
📊 Monitoring (Netdata)

Zero-config, per-second dashboards for CPU, RAM, disk, network, and every container. You literally just start it and open the dashboard.

###
💾 Backups (restic)

Scheduled, encrypted, deduplicated backups of your Docker volumes. Set a password and a cron schedule and forget it.

##
Lessons learned building it

Network isolation matters. Each stack gets its own bridge network; only user-facing ports are published. Ollama should never be exposed directly.

Resource limits are not optional. Without deploy.resources limits, a big model can starve the host. Every service got both limits and reservations.

Encryption passwords are a footgun. restic encrypts with a password — lose it and the backups are gone. Document that loudly.

Test before shipping. I deployed every stack and verified the health endpoints before calling it done.

##
Hardware reality check

8 GB RAM runs small models (llama3.2) comfortably on CPU.

16 GB+ or a GPU unlocks the bigger, smarter models.

No GPU required — it just runs slower for large models.

##
Get it

I cleaned this up, documented every stack with step-by-step guides + troubleshooting, and put it up as a downloadable pack for anyone who'd rather not assemble it from scratch:

👉 https://symshah.gumroad.com/l/selfhosted-ai-homelab

Happy to answer questions about the setup in the comments — always keen to hear how others structure their homelab AI.

##
Top comments (0)

Subscribe

PersonalTrusted User

Create template

Templates let you quickly answer FAQs or store snippets for re-use.

SubmitPreviewDismiss

Code of Conduct•Report abuse

Are you sure you want to hide this comment? It will become hidden in your post, but will still be visible via the comment's permalink.

Hide child comments as well

Confirm

For further actions, you may consider blocking this person and/or reporting abuse

Syed Masood Shah

Follow

Joined

Aug 4, 2026

###
More from Syed Masood Shah

My meeting minutes go out as files now, not a chat bubble nobody scrolls back to

#productivity#ai#localllm#windows

A year of meetings, and my minutes are plain text files on my own disk

#productivity#ai#localllm#windows

The server got hit and I only knew because a file quietly changed itself

#docker#infrastructure#monitoring#security

DEV Community — A space to discuss and keep up software development and manage your software career

Home

DEV Challenges

DEV++

Videos

DEV Education Tracks

DEV Help

Advertise on DEV

Organization Accounts

DEV Showcase

About

Contact

Free Postgres Database

DEV Shop

MLH

Code of Conduct

Privacy Policy

Terms of Use

Built on Forem — the open source software that powers DEV and other inclusive communities.

Made with love and Ruby on Rails. DEV Community © 2016 - 2026.

We're a place where coders share, stay up-to-date and grow their careers.

Log in

Create account
