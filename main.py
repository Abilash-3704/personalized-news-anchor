"""
Orchestrator — runs the full pipeline end to end.

Usage: python main.py
"""

import sys

from ingest import run as run_ingest
from personalize import retrieve_top_stories
from write import generate_script
from tts import script_to_mp3
from deliver import send_briefing


def main() -> None:
    print("=== Step 1/4: Ingesting news ===")
    run_ingest()

    print("\n=== Step 2/4: Retrieving top stories ===")
    stories = retrieve_top_stories()
    for i, s in enumerate(stories, 1):
        print(f"  {i}. [{s.score}] {s.title}")

    print("\n=== Step 3/4: Generating script ===")
    script = generate_script(stories)
    print(f"  {len(script.split())} words generated.")

    print("\n=== Step 4/4: Converting to audio and delivering ===")
    mp3_path = script_to_mp3(script)
    email_id = send_briefing(mp3_path, script, stories)
    print(f"  Briefing delivered. Email ID: {email_id}")

    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)
