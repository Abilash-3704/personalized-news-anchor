"""
Phase 3: Use Groq (Llama 3) to turn the top stories into a ~5 minute briefing script.

Usage: python write.py
"""

import os
from datetime import date

from dotenv import load_dotenv
from groq import Groq

from personalize import Story, retrieve_top_stories
import config

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = "llama-3.3-70b-versatile"
TARGET_WORDS = 750  # ~5 min at 150 wpm


def _build_prompt(stories: list[Story]) -> str:
    today = date.today().strftime("%A, %B %d, %Y")

    stories_block = ""
    for i, story in enumerate(stories, 1):
        stories_block += f"{i}. {story.title} (via {story.source})\n"
        if story.summary:
            stories_block += f"   {story.summary[:300]}\n"
        stories_block += f"   URL: {story.url}\n\n"

    return f"""You are a witty, warm NPR-style news anchor writing a personalized morning briefing script.

Today is {today}. Write a ~{TARGET_WORDS}-word spoken audio script based on the stories below.

Rules:
- Write in flowing prose meant to be read aloud — no bullet points, no headers, no markdown
- Open with a short, engaging greeting that mentions it's the morning briefing
- Group related stories naturally by theme with smooth transitions
- Keep a consistent, intelligent, slightly conversational tone throughout
- End with a brief, warm sign-off
- Do NOT include URLs in the script — they don't work in audio
- Aim for exactly {TARGET_WORDS} words

Stories to cover:
{stories_block}

Write the script now:"""


def generate_script(stories: list[Story]) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": _build_prompt(stories)}],
        temperature=0.7,
        max_tokens=1200,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    print("Retrieving top stories...")
    stories = retrieve_top_stories()

    print(f"Generating script with Groq ({MODEL})...\n")
    script = generate_script(stories)

    word_count = len(script.split())
    print(f"{'='*60}")
    print(script)
    print(f"{'='*60}")
    print(f"\nWord count: {word_count} (~{word_count // 150} min read)")
