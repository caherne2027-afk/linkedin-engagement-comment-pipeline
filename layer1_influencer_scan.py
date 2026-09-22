"""
Layer 1 -- Influencer comment scanner
======================================
Scrapes commenters on recent posts from a tracked list of industry voices,
filters each commenter against the client's ICP, and drafts a reply via
Claude for anyone who's a real fit.

The point isn't the influencer's post -- it's the people commenting on it.
Someone commenting on a well-known voice's post is a real, current signal:
they're engaged, active, and visible in a thread you're already part of.

Uses Apify's harvestapi/linkedin-post-comments actor (or any equivalent
post-comment scraper). Requires the post URL, not just the profile URL.
"""

import os
import re
import time
import requests

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
APIFY_ACTOR = "harvestapi~linkedin-post-comments"
APIFY_BASE = "https://api.apify.com/v2"

# Tracked industry voices -- client-configurable. Replace with real profile
# URLs for the client you're running this for.
TRACKED_INFLUENCERS = [
    "https://www.linkedin.com/in/example-voice-one/",
    "https://www.linkedin.com/in/example-voice-two/",
    "https://www.linkedin.com/in/example-voice-three/",
]

ICP_TITLE_PATTERN = re.compile(
    r"\b(founder|co-founder|ceo|president|owner)\b", re.IGNORECASE
)
EXCLUDE_TITLE_PATTERN = re.compile(
    r"\b(recruiter|bdr|sdr|account executive|i help|coach|top voice)\b",
    re.IGNORECASE,
)


def get_recent_posts_for(profile_url, max_posts=3):
    """Fetch the N most recent posts for a tracked profile. Placeholder --
    swap in your actual profile-post scraper (Apify actor or otherwise)."""
    raise NotImplementedError("Wire up a profile-post scraper here")


def scrape_post_commenters(post_url, retries=1):
    """Scrape commenters for a single post. Runs one post at a time with a
    retry, so a single bad or oversized thread can't take down a whole scan
    -- earlier versions batched every tracked post into one Apify call, and
    one failure discarded everything that had already scraped successfully."""
    for attempt in range(retries + 1):
        try:
            run = requests.post(
                f"{APIFY_BASE}/acts/{APIFY_ACTOR}/run-sync-get-dataset-items",
                params={"token": APIFY_API_KEY},
                json={"posts": [post_url]},
                timeout=120,
            )
            run.raise_for_status()
            return run.json()
        except requests.RequestException as e:
            if attempt == retries:
                print(f"skipping {post_url} after {retries + 1} attempts: {e}")
                return []
            time.sleep(2)


def is_icp_fit(commenter_title):
    title = commenter_title or ""
    if EXCLUDE_TITLE_PATTERN.search(title):
        return False
    return bool(ICP_TITLE_PATTERN.search(title))


def scan_all_tracked_influencers():
    matched = []
    for profile_url in TRACKED_INFLUENCERS:
        try:
            posts = get_recent_posts_for(profile_url)
        except NotImplementedError:
            posts = []  # showcase repo has no live scraper wired up
        for post in posts:
            commenters = scrape_post_commenters(post["url"])
            for c in commenters:
                if is_icp_fit(c.get("commenter_title")):
                    matched.append(
                        {
                            "commenter_name": c.get("commenter_name"),
                            "commenter_title": c.get("commenter_title"),
                            "comment_text": c.get("comment_text"),
                            "comment_url": c.get("comment_url"),
                            "source_influencer": profile_url,
                        }
                    )
    return matched


if __name__ == "__main__":
    results = scan_all_tracked_influencers()
    print(f"{len(results)} ICP-matched commenters found across {len(TRACKED_INFLUENCERS)} tracked profiles")
