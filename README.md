# LinkedIn Engagement Automation — Apify + Claude Reply Pipeline

A reference implementation of a two-layer LinkedIn engagement system I built for a B2B lead-
generation agency. It finds warm conversations before they happen, drafts a relevant reply with
Claude, and puts the result into a review queue with a live dashboard — nothing posts without a
human approving it first.

This repo is a **sanitized showcase** — the architecture and pipeline are real, but all client
identifiers, live account data, and lead information have been replaced with synthetic examples.

## The problem

Manually finding warm LinkedIn conversations — people already engaging with relevant content — was
slow and inconsistent. A single operator could scan a handful of influencer posts or historical
leads per day at most, missing most real engagement opportunities and losing the moment for a
timely, relevant reply.

## What this does

A two-layer engagement system that surfaces and drafts replies to warm conversations before they
go cold:

- **Layer 1 — Influencer scan** (`layer1_influencer_scan.py`) — scrapes commenters on posts from a
  tracked list of industry voices via Apify, filtering each commenter against the client's ICP.
- **Layer 2 — Lead re-scan** (`layer2_lead_rescan.py`) — a separate pass re-scans the client's
  entire historical lead database for fresh posting activity, resurfacing warm leads that would
  otherwise go untouched once an initial outreach sequence ends.
- **Reply drafting** (`reply_drafting.py`) — both layers generate a personalized reply via the
  Claude API and place it into a review queue — nothing posts without human approval.
- **Delivery** — the pipeline runs on a scheduled GitHub Actions workflow (see
  `.github/workflows/run_scan.yml`) and writes results to a static dashboard
  (`dashboard/index.html`) hosted for free on Netlify. Each client gets their own view showing
  flagged leads with the drafted reply, source post, and a one-click approve action. No credentials
  or dashboards are shared between clients.

## Sample dashboard

`dashboard/index.html` renders a small set of synthetic example leads so you can see the review-
queue UI without any real data. `sample_data.json` is the data it's built from — swap in your own
scan output to regenerate it.

## Delivered as

A live web dashboard (GitHub Actions + Netlify Functions triggering Python scan scripts on demand,
static per-client views, no login) so a non-technical operator can review and act on flagged leads
in minutes.

## Stack

Apify · Claude API · Python · GitHub Actions · Netlify Functions

## Outcome

Turned a manual, hit-or-miss process into a repeatable daily workflow, delivered per client with
fully isolated views and no shared credentials.
