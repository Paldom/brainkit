---
title: Stop building Foxconn factories for your agents | Garry Tan
url: https://www.linkedin.com/posts/garrytan_stop-building-foxconn-factories-for-your-activity-7467261872317165569-wF3P
final_url: https://www.linkedin.com/posts/garrytan_stop-building-foxconn-factories-for-your-activity-7467261872317165569-wF3P
source_type: social
providers: exa
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:50+00:00
published: 2026-06-01T00:00:00.000Z
content_digest: af9bd5e4cd5bdd18
---

## LinkedIn respects your privacy

LinkedIn and 3rd parties use essential and non-essential cookies to provide, secure, analyze and improve our Services, and to show you relevant ads (including professional and job ads) on and off LinkedIn. Learn more in our Cookie Policy.

Select Accept to consent or Reject to decline non-essential cookies for this use. You can update your choices at any time in your settings.

Accept

Reject

Agree & Join LinkedIn

By clicking Continue to join or sign in, you agree to LinkedIn’s User Agreement, Privacy Policy, and Cookie Policy.

Skip to main content
LinkedIn

Top Content

People

Learning

Jobs

Games

Sign in

Join now

#
Garry Tan’s Post

Garry Tan
Garry Tan is an Influencer

2mo

Report this post

Stop building Foxconn factories for your agents https://lnkd.in/gRM-rMNt

90

11 Comments

Like

Comment

Share

Copy

LinkedIn

Facebook

X

Ryan Widgeon

2mo

Report this comment

This is the part that feels most true to me. The setup becomes more valuable than the code.

More agents only helps if the system around them has role separation, shared context, deterministic handoffs, regression checks, and eval loops. Otherwise you are just parallelizing ambiguity.

I’ve been approaching it less like “spin up more coding agents” and more like designing a small engineering org. So you have a planner, implementer, reviewer, QA, release, each with different context and verification responsibilities.

Curious where you think the bottleneck moves next is it model capability, shared memory, or the verification layer between each agent role?

Like

Reply

2 Reactions

3 Reactions

Ruslan Kosinov ⚡️

2mo

Report this comment

From what I’ve seen, most agent systems fail not at execution, but at coordination between tools and intent.

Building infrastructure first can accidentally freeze bad assumptions into scale.

Like

Reply

2 Reactions

3 Reactions

Mahesh Konchada

2mo

Report this comment

The Foxconn factory metaphor is the part that stuck with me. Many teams seem to be responding to better models by adding more orchestration, more workflows, and more guardrails. But if model capability continues improving faster than framework complexity, the moat may no longer be in the orchestration layer at all. It may move to distribution, proprietary workflows, and eval systems. Curious where you think durable startup advantages come from in a world where implementation itself becomes increasingly commoditized?

Like

Reply

1 Reaction

AI Optimizer app

2mo

Report this comment

This is one of the clearest descriptions I’ve seen of the shift from “code as the product” to “judgment + instructions + thin deterministic code as the product.” The Foxconn vs freedom framing is strong, but the part that really hits is the economic inversion: people are still rationing model calls with an old map of the world. A lot of teams are going to realize too late that they overbuilt the cage and underbuilt the system for reusable intelligence.

Like

Reply

1 Reaction

Avinash Kumar

2mo

Report this comment

Agree that orchesation/setup is becoming easier. But as agents move into real workflows, another bottleneck starts appearing: trust. Identity, permissions, accountability, and boundaries become production problems, not demo problems.

Like

Reply

1 Reaction

GNANENDAR KUMAR

2mo

Report this comment

Garry Tan, this is such a sharp take — the real moat is the setup and the system, not just the lines of code. When half a million lines become a byproduct of the real work, that's when you know you're building something that compounds. GStack is a brilliant example of shipping value over vanity metrics!

Like

Reply

1 Reaction

Ziya Aktas

2mo

Report this comment

What matters is always the product, not the factory nor how it's built nor who built it.

Like

Reply

1 Reaction

Ademola Adamolekun

2mo

Report this comment

Actually Gstack grew out of the sloppy intellectual property theft you committed against YC applicants. Get over yourself Garry. #Gstack #Gbrain #Gesus #GodThisFreakingGuyLol

Like

Reply

1 Reaction

2 Reactions

AARON K

2mo

Report this comment

Truth

Like

Reply

1 Reaction

Adam Day

2mo

Report this comment

Thank you for this !!!

Like

Reply

1 Reaction

See more comments

To view or add a comment, sign in

341,995 followers

2,333 Posts

View Profile
Follow

##
Explore content categories

Career

Productivity

Finance

Soft Skills & Emotional Intelligence

Project Management

Education

Technology

Leadership

Ecommerce

User Experience

Show more

Show less

LinkedIn© 2026

About

Accessibility

User Agreement

Privacy Policy

Cookie Policy

Copyright Policy

Brand Policy

Guest Controls

Community Guidelines

العربية (Arabic)

বাংলা (Bangla)

Čeština (Czech)

Dansk (Danish)

Deutsch (German)

Ελληνικά (Greek)

English (English)

Español (Spanish)

فارسی (Persian)

Suomi (Finnish)

Français (French)

हिंदी (Hindi)

Magyar (Hungarian)

Bahasa Indonesia (Indonesian)

Italiano (Italian)

עברית (Hebrew)

日本語 (Japanese)

한국어 (Korean)

मराठी (Marathi)

Bahasa Malaysia (Malay)

Nederlands (Dutch)

Norsk (Norwegian)

ਪੰਜਾਬੀ (Punjabi)

Polski (Polish)

Português (Portuguese)

Română (Romanian)

Русский (Russian)

Svenska (Swedish)

తెలుగు (Telugu)

ภาษาไทย (Thai)

Tagalog (Tagalog)

Türkçe (Turkish)

Українська (Ukrainian)

Tiếng Việt (Vietnamese)

简体中文 (Chinese (Simplified))

正體中文 (Chinese (Traditional))

Language

##
Sign in to view more content

Create your free account or sign in to continue your search

Email or phone

Password

Show

Forgot password?
Sign in

Sign in with Email

or

New to LinkedIn? Join now

By clicking Continue to join or sign in, you agree to LinkedIn’s User Agreement, Privacy Policy, and Cookie Policy.
