---
title: Open Knowledge Format (OKF): The Markdown Standard Your AI Agents Have Been Waiting For 📚 - DEV Community
url: https://dev.to/suhas_mallesh/open-knowledge-format-okf-the-markdown-standard-your-ai-agents-have-been-waiting-for-3mfb
final_url: https://dev.to/suhas_mallesh/open-knowledge-format-okf-the-markdown-standard-your-ai-agents-have-been-waiting-for-3mfb
source_type: social
providers: exa, tavily
topic: Portable knowledge and context formats for agents: OKF (open knowledge format), AGENTS.md/CLAUDE.md conventions, MCP resources, llms.txt, Markdown+frontmatter vaults — and whether any interoperable standard for moving an agent's memory between tools is actually emerging.
fetched_at: 2026-08-28T20:45:40+00:00
published: 2026-07-03T00:00:00.000Z
content_digest: 859f40cd0641f332
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

Suhas Mallesh
Posted on Jul 3

#
Open Knowledge Format (OKF): The Markdown Standard Your AI Agents Have Been Waiting For 📚

#ai#opensource#mlops#architecture

AI agents are only as smart as the context you give them. OKF is a new open specification that packages your organizational knowledge as plain markdown files so any agent can read it without custom integrations or proprietary SDKs.

Every team building AI agents hits the same wall. The model is capable. The agent framework is set up. But the agent doesn't know anything about your organization. It doesn't know what your orders table means, what the churn_score metric formula is, or what the on-call runbook says to do when the pipeline breaks.

That knowledge exists. It's scattered across Confluence pages, Notion wikis, data catalog entries, Slack threads, and the heads of senior engineers. Getting it into an agent means building a custom integration for every source. Every team solves this from scratch.

Published on June 12, 2026, the Open Knowledge Format (OKF) is a vendor-neutral specification that solves this with the simplest possible approach: a directory of markdown files. 🎯

##
🏗️ What OKF Actually Is

An OKF bundle is a directory of markdown files representing concepts: anything you want to capture, including tables, datasets, metrics, playbooks, runbooks, and APIs. Each concept is one file.

That's the entire model. A directory of .md files with YAML frontmatter. The format is deliberately minimal: one required field (type), optional metadata (title, description, resource, tags, timestamp), and a free-form markdown body.

A concept document looks like this:

---type:tabletitle:"orders"description:"Onerowpercustomerorder.Sourceoftruthforrevenuereporting."resource:"postgresql://prod-db/ecommerce/orders"tags:[revenue,core,sla]timestamp:2026-06-15T10:00:00Z---# orders

The `orders` table records every purchase event. It is the join root for all
revenue queries. Do not filter on `status = 'complete'` unless you specifically
want to exclude in-flight orders from the count.

## Key columns
-`order_id` - UUID primary key
-`customer_id` - FK to [customers](../customers.md)-`amount_usd` - Total order value in USD
-`status` - Enum: pending / processing / complete / refunded

## Common joins

Joins to [customers](../customers.md) on `customer_id`.
Joins to [order_items](../order_items.md) on `order_id`.

## Known issues

The `created_at` column is UTC but the BI tool displays it in PST without
conversion. Always convert at query time.

Three things make this powerful:

1. File path is identity. The file tables/orders.md has the concept identifier tables/orders. No registry, no ID generation, no database.

2. Markdown links are the knowledge graph.A link from concept A to concept B asserts a relationship. The specific kind of relationship is conveyed by the surrounding prose, not by the link itself. Concepts linking to each other turns the directory into a navigable graph.

3. No tooling required.No API, no authentication, no SDK. The file system IS the API.

##
📁 Bundle Structure

knowledge-bundle/
├── index.md # Optional: directory listing
├── log.md # Optional: changelog
├── tables/
│ ├── index.md
│ ├── orders.md
│ ├── customers.md
│ └── order_items.md
├── metrics/
│ ├── churn_score.md
│ └── monthly_recurring_revenue.md
├── runbooks/
│ ├── pipeline_failure.md
│ └── incident_response.md
└── apis/
└── payments_api.md

Two reserved filenames carry defined meaning at any directory level. An index.md file enumerates the directory's contents to support progressive disclosure, letting a human or agent see what is available before opening individual documents. A log.md file records changes in date-grouped entries, newest first.

##
🧪 Real-World Examples

###
Example 1: Data Team Knowledge Base

Your data team documents tables, metrics, and known data quality issues. An agent building a SQL query can read the bundle before generating the query, understanding column semantics, join patterns, and gotchas:

---type:metrictitle:monthly_recurring_revenuedescription:Sum of all active subscription charges normalized to a monthly value.tags:[revenue,finance,sla]---# Monthly Recurring Revenue (MRR)

MRR = SUM(subscription_amount / billing_period_months) WHERE status = 'active'

Source table: [subscriptions](../tables/subscriptions.md)## Caveats
- Annual plans divide by 12. Do not count them as 12x monthly.
- Trial accounts are excluded (status = 'trial').
- See [churn_score](./churn_score.md) for related attrition metric.

An agent reading this before writing a revenue dashboard query avoids the annual-plan division error that junior analysts make constantly.

###
Example 2: Platform Team Runbook

Your SRE team writes runbooks as OKF concepts. An on-call agent can navigate the bundle to diagnose and respond to incidents:

---type:runbooktitle:ML Pipeline Failure Responsetags:[on-call,mlops,critical]---# ML Pipeline Failure Response## Symptoms- CloudWatch alarm: `prod-pipeline-5xx-errors`- SageMaker Pipeline execution status: `Failed`## Diagnosis steps
1. Check [pipeline logs](./pipeline_logs.md) in CloudWatch
2. Verify [feature store](../systems/feature_store.md) sync completed
3. Check [training data](../tables/training_data.md) for schema drift

## Resolution

If root cause is data schema drift:
- Update the [preprocessing component](../components/preprocess.md)- Re-run pipeline manually via EventBridge

Escalate to [ML Platform team](../teams/ml_platform.md) if unresolved in 30 minutes.

The agent reads the runbook, follows cross-links to related concepts, and can diagnose or escalate - all from the same markdown files a human uses.

###
Example 3: API Documentat