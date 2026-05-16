"""
Phase 5: Email the MP3 briefing via Resend.

Usage: python deliver.py
"""

import os
from datetime import date

import resend
from dotenv import load_dotenv

from personalize import retrieve_top_stories
from write import generate_script
from tts import script_to_mp3

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]
DELIVERY_EMAIL = os.environ["DELIVERY_EMAIL"]
FROM_EMAIL = "briefing@resend.dev"  # Resend's shared domain — no DNS setup needed


def send_briefing(mp3_path: str, script: str, stories: list) -> str:
    today = date.today().strftime("%A, %B %d, %Y")

    source_links = "\n".join(
        f'<li><a href="{s.url}">{s.title}</a> — {s.source}</li>'
        for s in stories
    )

    html_body = f"""
    <h2>Your Morning Briefing — {today}</h2>
    <p>Your personalized audio briefing is attached. Here's today's script:</p>
    <hr/>
    <pre style="font-family: Georgia, serif; line-height: 1.7; white-space: pre-wrap;">{script}</pre>
    <hr/>
    <h3>Sources</h3>
    <ul>{source_links}</ul>
    """

    with open(mp3_path, "rb") as f:
        mp3_bytes = f.read()

    params = {
        "from": FROM_EMAIL,
        "to": [DELIVERY_EMAIL],
        "subject": f"Your Morning Briefing — {today}",
        "html": html_body,
        "attachments": [
            {
                "filename": f"briefing-{date.today().isoformat()}.mp3",
                "content": list(mp3_bytes),
            }
        ],
    }

    response = resend.Emails.send(params)
    return response["id"]


if __name__ == "__main__":
    print("Retrieving top stories...")
    stories = retrieve_top_stories()

    print("Generating script...")
    script = generate_script(stories)

    print("Converting to MP3...")
    mp3_path = script_to_mp3(script)

    print(f"Sending briefing to {DELIVERY_EMAIL}...")
    email_id = send_briefing(mp3_path, script, stories)
    print(f"Delivered. Email ID: {email_id}")
