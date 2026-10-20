---
title: The Complete Guide to Karpathy's Second Brain
url: https://www.aibyaakash.com/p/karpathy-second-brain
final_url: https://www.aibyaakash.com/p/karpathy-second-brain
source_type: social
providers: brave
topic: Survey and technical evaluation of production-grade open-source GitHub implementations replicating Karpathy-style second brain systems.
fetched_at: 2026-10-19T21:50:46+00:00
published: 2026-04-13
content_digest: e057b8fc2d6990aa
---

# AI by Aakash

SubscribeSign in

# The Complete Guide to Karpathy's Second Brain

### Plus: Claude Managed Agents kills the middleware layer, Gemma 4 goes fully open-source, and an AI that broke out of its sandbox. Everything you need to know about AI this week.

Apr 13, 2026

116

5

10

Share

Anthropic just launched Managed Agents and quietly made an entire category of startups obsolete. LangChain, Manus, every custom agent harness: their moat just evaporated.

And in today’s deep dive, I cover the knowledge system Karpathy posted that’s permanently replacing RAGs. It’s the first thing I’ve tried that makes your AI knowledge compound instead of reset.

Subscribe

### Ariso: Your AI Chief of Staff

I had 80+ loose files rotting in my Google Drive root. Asked Ariso’s AI to organize them.

Twenty minutes later: GTM, Product, Finance, Legal, Content - all sorted, no rules or templates needed. It just read the files and figured it out. One less Saturday wasted on admin.

Try it free at ariso.ai/aakash.

Try Ariso

There’s a billion AI news articles every week. Here’s what actually mattered.

#### News

### Anthropic just made every agent orchestration startup obsolete

Claude Managed Agents launched this week in public beta. You describe what you want your agent to do, define your tools and guardrails, and Anthropic runs the whole thing. Sandboxed execution, state management, credential handling, error recovery. All of it, handled.

Aakash Gupta@aakashgupta

Anthropic just mass-obsoleted every agent orchestration startup in a single launch.

The screenshot tells the full story. That's a production fleet dashboard. 8 agents running. 247 completed tasks. Active status. MCP-connected to HubSpot, pulling deals, generating proposals,

Claude@claudeai

Introducing Claude Managed Agents: everything you need to build and deploy agents at scale.

It pairs an agent harness tuned for performance with production infrastructure, so you can go from prototype to launch in days.

Now in public beta on the Claude Platform.

6:04 PM · Apr 8, 2026 · 979KViews

167Replies · 256Reposts · 3.12KLikes

What used to take months of infrastructure work now takes days. In internal testing, structured file generation success rates improved by 10 points over standard prompting. Early adopters include Notion, Rakuten, and Asana, and they’re already shipping production agents built on top of it.

Here’s what people are missing. Every startup that built a business on top of the infrastructure gap, LangChain, Manus, custom agent harnesses, just had their moat evaporate. Anthropic isn’t just offering a faster path to deployment. They’re absorbing the entire orchestration layer into their own platform.

The pricing tells the story. $0.08 per agent runtime hour, on top of model usage. That’s not an enterprise premium. That’s a direct play for developers who were previously forced to build their own scaffolding or pay someone else to build it.

Why this matters for you. If you’re building AI products right now, you need to decide: roll your own orchestration, buy a third-party harness, or just use Managed Agents and ship faster. The third option just got a lot more credible.

The way I see it, this is Anthropic pulling the rug out from under the middleware layer of the AI stack. The companies that survive are the ones with proprietary data, proprietary workflows, or a distribution advantage. Infrastructure players just lost a round.

#### Other News that Mattered this Week

Google released Gemma 4 , the first time the Gemma family ships with a truly open commercial license. The 26B MoE model activates only 3.8B parameters at a time, and the edge models run on Raspberry Pi. The benchmark numbers are strong, the 31B ranks third globally on Arena AI, beating models 20x its size. But the license change is what actually matters. No usage restrictions buried in fine print, no legal review friction. Developers can now build on Gemma the same way they build on anything they actually own.

Anthropic built its most capable model yet and decided not to release it. Claude Mythos Preview found a 27-year-old OpenBSD vulnerability, broke out of its sandbox during testing, and emailed a researcher to confirm it had done so. Instead of a public launch, Anthropic formed Project Glasswing: a restricted coalition of 40+ companies including Apple, Google, Microsoft, and Amazon with $100M in model credits to use Mythos exclusively for defensive security work. Responsible release or competitive gatekeeping? Probably both.

Meta finally released the first model from their team led by Alexandr Wang, Muse Spark. It looks like prior Llama models: good at image and video, benchmark-maxxed, but not huge on real world work use cases yet. Data analysis and counting in images are amongst its top skills.

Claude’s M365 connector is now available on every plan, including free. Claude can read your Outlook, search your SharePoint, and pull from your Teams chats without you uploading a single file. Microsoft Copilot charges $30/user/month for essentially the same access. Anthropic just made that a much harder sell.

#### Resources

AutoAgent is the open-source library every agent builder needs to know about right now. You point it at a task domain with evals, and a meta-agent spends 24 hours autonomously tweaking your agent’s system prompt, tools, and orchestration until performance climbs. No human tuning. It hit #1 on SpreadsheetBench (96.5%) and the top GPT-5 score on TerminalBench (55.1%), beating every hand-engineered entry on both leaderboards. I’ve been watching this closely because it changes the question from “how do I tune my agent?” to “why am I tuning my agent at all?”

## The AI Second Brain That Actually Works

Karpathy posted a knowledge base system that replaces RAGs and achieves what that Knowledge management system is not been able to do for years. I’ve been running it for a week and a half. It’s the first thing I’ve tried that actually makes