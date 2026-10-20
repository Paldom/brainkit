---
title: Why is self-hosting making a comeback | Plane Blog
url: https://plane.so/blog/why-is-self-hosting-making-a-comeback
final_url: https://plane.so/blog/why-is-self-hosting-making-a-comeback
source_type: social
providers: brave
topic: Self-hosting in practice and the motivation for it: Docker/local-model deployment, embedding choices, privacy and data-ownership arguments, plus practitioner discourse (why Garry Tan built his own) and the own-vs-rent-your-memory debate including vendor business models.
fetched_at: 2026-08-28T20:57:45+00:00
published: 2026-03-25
content_digest: 045cfe668c5af476
---

Product

Solutions

Resources

Pricing

Self-host Plane

Contact salesLoginGet started free

Get started free

Blog / Plane POV

# Why is self-hosting making a comeback

The cloud is here to stay, but after two decades of unquestioned cloud-first strategies, a shift is underway. Here's what's driving enterprises, governments, and engineering teams back to owning their own stack.

Devanshu Arora

●

25 Mar, 2026

Copy as markdown

Share

Start a free trial

Share

Start a free trial

Enterprise infrastructure oscillates between centralization and distribution. Mainframes gave way to client-server. Client-server gave way to cloud. Now, cloud is giving way to something else-not a return to the data center, but a new settlement where organizations choose, workload by workload, what runs where.

The shift has five drivers, all intensifying simultaneously: compliance, trust, AI, sovereignty, and tooling. Anyone would create pressure. Together, they're unwinding assumptions that have governed infrastructure decisions since AWS launched EC2 in 2006.

This isn't nostalgia for the data center era. And it's not a rejection of cloud computing. It's the end of cloud-as-default and the beginning of genuine infrastructure choice. The numbers tell the story. Barclays' Q4 2024 CIO Survey found 86% of CIOs now plan to move some public cloud workloads back on-premises, double the rate measured in 2020. When the overwhelming majority of technology leaders are reconsidering a two-decade architectural assumption, it's worth understanding why.

## The historical pattern

Self-hosted was the only option for decades. Then Salesforce launched in 1999, AWS introduced EC2 in 2006, and by 2013 "cloud-first" had become gospel.

The SaaS market exploded from $31.4 billion in 2015 to $206 billion by 2023, a 7x increase fueled by near-zero interest rates and growth-at-all-costs capital allocation. The average company went from 8 SaaS applications to 130 in the same period. Large enterprises accumulated north of 500.

The intellectual turning point came in May 2021, when Andreessen Horowitz published "The Cost of Cloud, a Trillion Dollar Paradox." Martin Casado and Sarah Wang argued that the top 50 public software companies were collectively losing $100–200 billion in market value due to cloud's impact on margins, with cloud spending consuming 50% or more of cost of revenue. They estimated repatriation could cut infrastructure costs by 33–50%. The paper was careful ("this isn't a blanket 'get out of the cloud' message") but it gave CIOs and CFOs the analytical framework to question what had become an unexamined assumption.

The most visible proof point followed in October 2022, when DHH of 37signals announced his intention to leave AWS, projecting $7 million in savings over five years. By 2025, actual savings exceeded $10 million, achieved without adding a single operations hire.

But here's the distinction that gets lost in the repatriation discourse: moving cloud infrastructure workloads on-premises to cut compute costs is a different decision from self-hosting software. The 37signals story is about infrastructure economics. The self-hosting resurgence is about something else entirely: compliance, security, data control, and the organizational conviction that critical systems shouldn't depend on a vendor's continued goodwill. Cost savings on the software license are rarely the driver. In fact, self-hosting often costs more when you account for the infrastructure you now own and operate. At Plane, cloud and self-hosted are priced identically, dollar for dollar. When users come to us looking primarily to cut costs, we tell them to use the cloud, because self-hosted means paying the same license fee plus their own infrastructure. The organizations that choose self-hosted anyway aren't optimizing for price. They're optimizing for control.

## The SaaS trust tax

If the cloud repatriation story is about infrastructure economics, the self-hosted software story is about something harder to quantify: trust.

SaaS pricing has inflated at roughly 5x the rate of general inflation, 11.4% year-over-year versus 2.7% across G7 economies. Salesforce raised prices 9% in July 2023, then another 6% in August 2025. Slack increased Enterprise pricing 40–125% in August 2024. Adobe raised Creative Cloud prices 16.7%, bundling AI features users didn't request with no opt-out. Monday.com, 29%. Snowflake, 31%. In nearly every case, the justification was identical: AI capabilities bundled in, and you're paying whether you use them or not.

The pricing is a symptom. The disease is dependency. When your project management tool, your communication platform, your analytics stack, and your CRM all live in someone else's infrastructure under someone else's terms, you don't have a software stack. You have a collection of ongoing negotiations where the other party can change terms unilaterally. Zylo's 2025 SaaS Management Index found that only 47.3% of provisioned licenses are actually used. Organizations aren't just overpaying. They've lost visibility into what they're paying for.

This isn't an argument that SaaS is bad. It's an argument that SaaS-only is a risk posture, and an increasing number of engineering leaders are recognizing it as one.

## Trust broke, and forks flourished

The pricing trends eroded trust gradually. Then a cascade of vendor decisions between 2021 and 2024 shattered it.

The pattern is now grimly recognizable: a company builds an open-source product, achieves massive adoption on the implicit promise of community governance, then changes the license or pricing in ways that betray that promise. The community forks the project. The fork gains traction in weeks, not years. And the original vendor discovers that the thing they were actually selling-trust-is the one thing they can't recapture.

The most consequential incident was Broadcom's $61 billion acquisition of VMware in November 2023. Broadcom eliminated perpetual licenses, 