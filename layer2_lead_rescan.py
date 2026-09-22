"""
Layer 2 -- Lead re-scan
========================
A separate pass that re-scans the client's ENTIRE historical lead database
for fresh posting activity -- not just this week's new leads. Once an
initial outreach sequence ends, most CRMs treat a lead as done. This module
treats the accumulated lead list as a standing asset: anyone who posts again
later is a fresh, warm signal worth acting on, regardless of when they were
originally sourced.

Written against a generic paginated contacts API -- swap `LEAD_API_BASE`
for whatever CRM / lead-sourcing platform holds the historical list.
"""

import os
import time
import requests

LEAD_API_BASE = os.getenv("LEAD_API_BASE", "https://api.example-crm.com")
LEAD_API_KEY = os.getenv("LEAD_API_KEY", "")
PAGE_SIZE = 100


def _headers():
    return {"Authorization": f"Bearer {LEAD_API_KEY}"}


def fetch_all_historical_leads(list_ids=None, max_pages=500):
    """Paginate through every list in the account, not just the active
    campaign -- this is the full historical pool, thousands of contacts,
    not a sample of this week's activity."""
    leads = []
    for list_id in (list_ids or [None]):
        page = 0
        while page < max_pages:
            resp = requests.get(
                f"{LEAD_API_BASE}/v1/contacts",
                headers=_headers(),
                params={"list_id": list_id, "page": page, "page_size": PAGE_SIZE},
                timeout=30,
            )
            resp.raise_for_status()
            batch = resp.json().get("results", [])
            if not batch:
                break
            leads.extend(batch)
            page += 1
            time.sleep(0.1)
    return leads


def check_for_recent_activity(lead, days=7):
    """Placeholder for a per-lead recent-post check. In production this
    calls a post-scraper (e.g. Apify) per lead's profile URL and checks for
    activity in the last N days. Kept as a stub here since it depends on
    the same scraper used in layer1_influencer_scan.py."""
    raise NotImplementedError("Wire up a per-profile recent-activity check here")


def rescan_for_warm_leads(leads):
    warm = []
    for lead in leads:
        try:
            recent_post = check_for_recent_activity(lead)
        except NotImplementedError:
            recent_post = None  # showcase repo has no live scraper wired up
        if recent_post:
            warm.append({**lead, "recent_post": recent_post})
    return warm


if __name__ == "__main__":
    all_leads = []
    try:
        all_leads = fetch_all_historical_leads()
    except requests.RequestException:
        pass  # no live API configured for this showcase repo
    print(f"{len(all_leads)} historical leads pulled; re-scanning for fresh activity...")
    warm = rescan_for_warm_leads(all_leads)
    print(f"{len(warm)} flagged as warm (posted recently)")
