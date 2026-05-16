"""
Phase 4: Convert the briefing script to an MP3 using Google Cloud TTS.

Usage: python tts.py
Output: briefing.mp3 in the project directory
"""

import os
from datetime import date

from dotenv import load_dotenv
from google.cloud import texttospeech

from personalize import retrieve_top_stories
from write import generate_script

load_dotenv()

# Neural2 voices sound closest to a real broadcaster
VOICE_NAME = "en-US-Neural2-D"  # neutral male, clear and professional
LANGUAGE_CODE = "en-US"
OUTPUT_FILE = "briefing.mp3"


CHUNK_LIMIT = 4800  # bytes, safely under the 5000 byte API limit


def _split_into_chunks(text: str) -> list[str]:
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        candidate = (current + ". " + sentence).strip() if current else sentence
        if len(candidate.encode("utf-8")) > CHUNK_LIMIT:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current.strip())
    return chunks


def script_to_mp3(script: str, output_path: str = OUTPUT_FILE) -> str:
    client = texttospeech.TextToSpeechClient()

    voice = texttospeech.VoiceSelectionParams(
        language_code=LANGUAGE_CODE,
        name=VOICE_NAME,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.05,
        pitch=0.0,
    )

    chunks = _split_into_chunks(script)
    print(f"Sending {len(script)} characters in {len(chunks)} chunks to Google Cloud TTS...")

    audio_parts = []
    for i, chunk in enumerate(chunks, 1):
        response = client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=chunk),
            voice=voice,
            audio_config=audio_config,
        )
        audio_parts.append(response.audio_content)
        print(f"  Chunk {i}/{len(chunks)} done ({len(chunk)} chars)")

    combined = b"".join(audio_parts)
    with open(output_path, "wb") as f:
        f.write(combined)

    size_kb = len(combined) // 1024
    print(f"Saved {output_path} ({size_kb} KB)")
    return output_path


if __name__ == "__main__":
    print("Retrieving top stories...")
    stories = retrieve_top_stories()

    print("Generating script...")
    script = generate_script(stories)

    print()
    output = script_to_mp3(script)
    print(f"\nDone. Open {output} to listen to today's briefing.")
