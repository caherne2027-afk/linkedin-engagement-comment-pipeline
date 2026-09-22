"""
Renders dashboard/index.html from sample_data.json (or live scan output in
production). Surgically regenerates just the lead-card section so any manual
styling edits elsewhere in the template survive a scan run.
"""

import json
import html

CARD_START = "<!-- CARDS_START -->"
CARD_END = "<!-- CARDS_END -->"


def esc(s):
    return html.escape(str(s or ""))


def render_card(lead):
    badge_class = "high" if lead.get("verified") else "medium"
    return f"""
    <div class="lead-card">
      <div class="lead-header">
        <span class="lead-name">{esc(lead.get('name'))}</span>
        <span class="lead-title">{esc(lead.get('title'))}</span>
      </div>
      <div class="lead-badges"><span class="badge {badge_class}">{esc(lead.get('tier'))} · {esc(lead.get('match_score'))}</span></div>
      <div class="lead-source">{esc(lead.get('source'))}</div>
      <blockquote class="comment-text">&ldquo;{esc(lead.get('comment_text'))}&rdquo;</blockquote>
      <div class="reply-draft"><strong>Drafted reply:</strong> {esc(lead.get('reply_draft'))}</div>
      <button class="approve-btn">Approve &amp; copy</button>
    </div>"""


def render_cards(data_path="sample_data.json", html_path="dashboard/index.html"):
    with open(data_path) as f:
        leads = json.load(f)

    cards_html = "\n".join(render_card(l) for l in leads)

    with open(html_path) as f:
        page = f.read()

    start = page.index(CARD_START) + len(CARD_START)
    end = page.index(CARD_END)
    new_page = page[:start] + "\n" + cards_html + "\n    " + page[end:]

    with open(html_path, "w") as f:
        f.write(new_page)

    print(f"rendered {len(leads)} cards into {html_path}")


if __name__ == "__main__":
    render_cards()
