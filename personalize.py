"""
Phase 2: Query Pinecone with the user's interest profile and return the top stories.

Usage: python personalize.py
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

import config

load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "news-anchor")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


@dataclass
class Story:
    title: str
    summary: str
    url: str
    source: str
    score: float


def retrieve_top_stories(n: int = config.TOP_STORIES_COUNT) -> list[Story]:
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_vector = model.encode(config.PROFILE_QUERY).tolist()

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    results = index.query(
        vector=query_vector,
        top_k=n,
        include_metadata=True,
    )

    stories = []
    for match in results["matches"]:
        meta = match["metadata"]
        stories.append(Story(
            title=meta.get("title", ""),
            summary=meta.get("summary", ""),
            url=meta.get("url", ""),
            source=meta.get("source", ""),
            score=round(match["score"], 3),
        ))

    return stories


if __name__ == "__main__":
    print(f"Querying Pinecone with your interest profile...\n")
    print(f"Profile: {config.PROFILE_QUERY[:120]}...\n")

    stories = retrieve_top_stories()

    print(f"Top {len(stories)} stories:\n")
    for i, story in enumerate(stories, 1):
        print(f"{i}. [{story.score}] {story.title}")
        print(f"   Source: {story.source}")
        print(f"   URL: {story.url}")
        print(f"   Summary: {story.summary[:120]}...")
        print()
