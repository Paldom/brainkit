---
title: Self-hosted AI doesn't mean local weights — here's what actually stays on your box - DEV Community
url: https://dev.to/samadhi_tattoo_7ed1c0d05b/self-hosted-ai-doesnt-mean-local-weights-heres-what-actually-stays-on-your-box-2j6e
final_url: https://dev.to/samadhi_tattoo_7ed1c0d05b/self-hosted-ai-doesnt-mean-local-weights-heres-what-actually-stays-on-your-box-2j6e
source_type: social
providers: exa
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:51+00:00
published: 2026-08-08T00:00:00.000Z
content_digest: c8c0aa556bcb4d43
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

Samadhi Tattoo
Posted on Aug 8

#
Self-hosted AI doesn't mean local weights — here's what actually stays on your box

#ai#selfhosted#privacy#architecture

Every thread about self-hosting AI collapses into the same argument within ten replies: "you can't self-host a frontier model on a $6 VPS." That's true. It's also answering a question nobody useful is asking.

I build a self-hosted personal assistant commercially, so treat this as a field report from an interested party rather than neutral analysis. But the terminology confusion here costs people real decisions, and it's worth untangling.

##
Two different things wear the same word

Self-hosting the model means the weights run on hardware you control. Real, valuable, and expensive: you need a GPU, and what you get is a model measurably weaker than what you're used to. For most people this trade fails on day one, they go back to the hosted product, and conclude self-hosting AI is a fantasy.

Self-hosting everything around the model is a different proposition entirely. The model stays an API call. What moves onto your machine is:

the memory of who you are and what you've discussed

the full conversation archive, searchable

scheduled jobs and automation

skills, integrations, credentials

the orchestration logic that decides what context the model even sees

That runs comfortably on a cheap VPS, because none of it is inference.

##
Why the second one is the interesting one

Think about what actually accumulates value over years of using an assistant. It isn't the model — model weights get replaced every few months and you don't own them either way. It's the context: what it knows about you, what corrections you've made, what it has concluded about how you work.

When that lives inside a vendor product, three things follow:

Its lifetime is a business decision, not an engineering one. Retention windows change. Features get deprecated. Nobody consults you.

Switching cost compounds. Every month you use it, leaving gets more expensive — which is the point, from the vendor's side.

You can't inspect or restructure it. You get whatever memory abstraction they ship.

Move that layer onto your own box and those three invert. The schema is yours, the backups are yours, the migrations are your problem — which is a real operational cost, not a rhetorical one.

##
The honest accounting

Being precise, because vague claims here are how people get burned:

What never leaves your machine: stored memory, conversation history, scheduling state, skill configuration, credentials for the services you connect.

What does leave: the current prompt, going to the model provider under their terms.

So if your threat model is "the model provider must not see my text," this does not solve it, and no amount of self-hosting around the edges will. If your threat model is "my accumulated context must not become someone else's asset, and must survive their product decisions" — that's exactly what it solves.

##
What it costs in practice

A VPS with at least 4 GB of RAM handles it — roughly $5–15/month depending on provider and billing period. Below 4 GB the install starts fighting for memory, so that is the real floor, not the price. The model subscription is separate and is the dominant cost. Setup is an install script and roughly half an hour if nothing goes sideways; when it does go sideways it's usually DNS or a firewall rule, same as any other self-hosted service.

Worth being blunt: if you use AI a few times a week, this is not worth the operational overhead. We wrote that case ourselves — the arithmetic is in is self hosting AI worth it, including where the honest answer is "just use the hosted product."

The broader tradeoff list, including what's overrated about self-hosting, is in self-hosted AI benefits.

##
The point

"Self-hosted AI" being read as "local weights" quietly kills the option that's actually practical for most people. You can have data sovereignty over the part that matters — everything that accumulates — while still using a frontier model through an API.

Those are separable concerns. Treating them as one thing is how the conversation keeps going nowhere.

Curious how others draw this line: if you run any part of your AI stack yourself, which part did you decide to own, and what made that the cutoff?

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

Samadhi Tattoo

Follow

Joined

Jul 16, 2026

###
More from Samadhi Tattoo

Four typed memory layers beat one vector store (for personal AI assistants)

#ai#architecture#sqlite#selfhosted

What 6 months of running a personal AI assistant on a $6 VPS actually costs

#selfhosted#ai#privacy#devops

Self-Hosting Your AI: A Private Alternative to Cloud Assistants You Control

#ai#selfhosted#privacy#opensource

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

We're a place where coders share, stay up