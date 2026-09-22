"""
Reply drafting
==============
Both Layer 1 and Layer 2 feed matched leads into this module, which drafts a
short, relevant reply via Claude and writes it to a review queue. Nothing in
this pipeline posts automatically -- every reply is reviewed and copy-pasted
in by a human before it goes out. This is a deliberate choice: running two
LinkedIn automation surfaces at once (auto-scan AND auto-post) raises the
same account-safety risk as any other multi-tool automation setup.
"""

import os
import csv
import json
from datetime import datetime
from anthropic import Anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
OUTPUT_FILE = f"reply-queue-{datetime.now().strftime('%Y-%m-%d')}.csv"

SYSTEM_PROMPT = """You write short, genuine LinkedIn comment replies for a B2B \
growth agency. Rules:

- 2-3 sentences, max 50 words.
- One sentence of real reaction to what they wrote -- peer-to-peer tone, no \
flattery, no product mention.
- No fake compliments, no links, no pitch.
- Sound like a practitioner replying in a thread, not a marketer.
- Output valid JSON only: {"reply_draft": "..."}"""


def draft_reply(comment_text, commenter_title=""):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Their comment: \"{comment_text}\"\nTheir title: {commenter_title}\n\nDraft a reply.",
        }],
    )
    return json.loads(resp.content[0].text)["reply_draft"]


def write_review_queue(matched_leads, output_file=OUTPUT_FILE):
    """Writes every matched lead + drafted reply to a CSV review queue.
    A human opens this, approves or edits each row, then posts manually."""
    fieldnames = ["name", "title", "comment_text", "comment_url", "reply_draft", "approved"]
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in matched_leads:
            try:
                reply = draft_reply(lead.get("comment_text", ""), lead.get("commenter_title", ""))
            except Exception as e:
                reply = f"[draft failed: {e}]"
            writer.writerow({
                "name": lead.get("commenter_name", lead.get("name", "")),
                "title": lead.get("commenter_title", lead.get("title", "")),
                "comment_text": lead.get("comment_text", ""),
                "comment_url": lead.get("comment_url", ""),
                "reply_draft": reply,
                "approved": "",  # left blank for human review
            })
    return output_file


if __name__ == "__main__":
    example_matches = [
        {
            "commenter_name": "Priya Nataraj",
            "commenter_title": "Founder, Meridian Ops",
            "comment_text": "This is exactly the gap we've been trying to close for months.",
            "comment_url": "https://www.linkedin.com/feed/update/example",
        }
    ]
    out = write_review_queue(example_matches, output_file="/tmp/example-reply-queue.csv")
    print(f"wrote {out}")
