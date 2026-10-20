---
title: How I Replaced Gemini with a Self-Hosted LLM for Two Production Apps - DEV Community
url: https://dev.to/smngvlkz/how-i-replaced-gemini-with-a-self-hosted-llm-for-two-production-apps-3069
final_url: https://dev.to/smngvlkz/how-i-replaced-gemini-with-a-self-hosted-llm-for-two-production-apps-3069
source_type: social
providers: exa
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:50+00:00
published: 2026-06-27T00:00:00.000Z
content_digest: 037ecfe076be0da6
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

Simangaliso Vilakazi
Posted on Jun 27

#
How I Replaced Gemini with a Self-Hosted LLM for Two Production Apps

#ai#selfhosted#nextjs#ollama

A while back I wrote about my terminal-inspired portfolio and the products it indexes. Two of those products lean on a language model: the portfolio terminal at smngvlkz.com that you can ask questions, and PayChasers, which generates OPTIONAL payment follow-up emails. Both started on Google's Gemini 3 Flash. Both now run on a model I host myself, with a fallback chain that keeps them alive when my hardware is not.

This is the story of that move. The experiment that started it, why I committed to it, what the architecture looks like, the night it broke, and the parts I still have not solved.

##
It started as an experiment

When Qwen 3.5 was announced, it made me curious about how far open models have actually come. Instead of reading benchmarks, I tested it the way I like to learn things, by running it.

It began as a small experiment on my base Mac mini. I pulled Qwen through Ollama just to see how capable the model would be running directly on a local machine. The results were far better than I expected. Good enough that I stopped thinking of it as a toy and started thinking about production.

##
Why move off Gemini at all

Gemini 3 Flash worked. The integration was a few lines and the quality was good. So this was not a "the API is bad" story. It was three smaller pulls that added up.

The first was cost shape. PayChasers generates optional email drafts on demand, and every preview is a few thousand tokens of system prompt plus output. That is fine at zero users and a slow leak at volume. The marginal cost of an inference I run on a machine I already own is electricity.

The second was control and privacy. I wanted to choose the model, pin it, and change the prompt contract without a provider deprecating something underneath me. I also did not love sending client names and payment context to a third party when I did not have to.

The third was the economics of treating AI as infrastructure rather than a metered API. Once the model runs on hardware I control, it stops being a per-call expense and becomes shared infrastructure that multiple applications can use. The same inference server now powers two different products. That reframing is the whole point.

##
Getting it to production was the hard part

The original plan was to host the model on Oracle Cloud using one of their free Ampere ARM instances in the Johannesburg region. If you have ever tried to get one, you know the struggle. Free tier ARM capacity is brutally limited, and after more than 200 automated retry attempts across two days, I still could not get one.

So I pivoted. I wrote a lightweight reverse proxy, set up a Cloudflare Tunnel on one of my domains, and routed production traffic to the model running on my Mac at home. No ports opened on my home network, no static IP, just a tunnel from Cloudflare's edge to the machine on my desk.

There is an honest tension here worth naming. Privacy was one of my reasons for leaving Gemini, and routing client data to a box on my desk is its own tradeoff. The tunnel keeps inbound ports closed and lets Cloudflare terminate TLS at the edge, and the reverse proxy sits in front of Ollama rather than exposing it directly. But this is a single machine I own, not a vendor's hardened, multi-tenant platform, and tightening access control on that endpoint, a service token rather than relying on an obscure hostname, is firmly on the list. Self-hosting moves the privacy boundary onto you, it does not remove it.

It was meant to be temporary. The Oracle instance eventually did come through, but by then the home setup was working well, so I did not throw it away. Instead I kept the Mac mini as the primary and gave Oracle a different job, the always-on backup. More on that in a moment.

This was a small full-circle moment. The Linux and infrastructure fundamentals I picked up during my bootcamp days and years of self-teaching showed up in a real production context. Provisioning tunnels, configuring DNS, writing a proxy service, setting up persistent services. All of it coming together for something real.

One deliberate decision was to keep the infrastructure simple. There are a lot of frameworks and agent systems appearing in the space right now. I focused on straightforward tooling that solved the problems I actually had.

##
The shape of the system

The Mac mini, exposed through Cloudflare tunnel, is the primary. It is fast but it is not always on, because it is a machine in my home. The Oracle Cloud VM is the fallback. It is slower and smaller, but it stays up around the clock.

Every app talks to a thin client that knows about both, tries the fast one first, and silently falls back to the reliable one.

Vercel app
|
v
[ primary: Mac mini via Cloudflare tunnel ] --fail/timeout--> [ fallback: Oracle Cloud VM ]
fast, not always on slow, always on

##
The failover client

This is the whole idea in one function. Hit the primary with a timeout. If anything goes wrong, the status, the timeout, a dropped tunnel, fall through to the fallback.

constPRIMARY_URL=process.env.OLLAMA_PRIMARY_URL||"http://localhost:11434";constFALLBACK_URL=process.env.OLLAMA_FALLBACK_URL||PRIMARY_URL;asyncfunctionfetchWithFallback(path:string,body:object):Promise<Response>{try{constres=awaitfetch(`${PRIMARY_URL}${path}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body),signal:AbortSignal.timeout(15000),});if (!res.ok)thrownewError(`Primary failed (${res.status})`);returnres;}catch{constres=awaitfetch(`${FALLBACK_URL}${path}`,{method:"POST",headers:{"Content-Type":"a