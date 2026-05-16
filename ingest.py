"""
Phase 1: Ingest news from RSS feeds, HackerNews, and Reddit into Pinecone.

Run this daily (or on demand) to refresh the vector DB with today's articles.
Usage: python ingest.py
"""

import hashlib
import os
import time
from dataclasses import dataclass

import feedparser
import requests
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

import config

load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "news-anchor")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384-dim, fast, runs locally
EMBEDDING_DIM = 384
BATCH_SIZE = 64


@dataclass
class Article:
    id: str
    title: str
    summary: str
    url: str
    source: str
    published: str

    @property
    def text(self) -> str:
        return f"{self.title}. {self.summary}"


def _article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


# ── Sources ──────────────────────────────────────────────────────────────────

def fetch_rss(feed_url: str) -> list[Article]:
    feed = feedparser.parse(feed_url)
    source = feed.feed.get("title", feed_url)
    articles = []
    for entry in feed.entries[:20]:
        url = entry.get("link", "")
        if not url:
            continue
        articles.append(Article(
            id=_article_id(url),
            title=entry.get("title", ""),
            summary=entry.get("summary", "")[:500],
            url=url,
            source=source,
            published=entry.get("published", ""),
        ))
    return articles


def fetch_hackernews(limit: int = 30) -> list[Article]:
    top_ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
    ).json()[:limit]

    articles = []
    for story_id in top_ids:
        try:
            story = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=10,
            ).json()
            if story.get("type") != "story" or not story.get("url"):
                continue
            articles.append(Article(
                id=_article_id(story["url"]),
                title=story.get("title", ""),
                summary=story.get("text", "")[:500],
                url=story["url"],
                source="HackerNews",
                published=str(story.get("time", "")),
            ))
        except Exception:
            continue
    return articles


def fetch_all_sources() -> list[Article]:
    articles: list[Article] = []
    seen_ids: set[str] = set()

    print("Fetching HackerNews...")
    for article in fetch_hackernews():
        if article.id not in seen_ids:
            articles.append(article)
            seen_ids.add(article.id)

    for feed_url in config.RSS_FEEDS:
        print(f"Fetching {feed_url}...")
        try:
            for article in fetch_rss(feed_url):
                if article.id not in seen_ids:
                    articles.append(article)
                    seen_ids.add(article.id)
        except Exception as e:
            print(f"  Failed: {e}")

    print(f"Fetched {len(articles)} unique articles total.")
    return articles


# ── Pinecone ─────────────────────────────────────────────────────────────────

def get_or_create_index(pc: Pinecone) -> object:
    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        time.sleep(5)  # wait for index to initialize
    return pc.Index(INDEX_NAME)


def upsert_articles(index, articles: list[Article], model: SentenceTransformer) -> None:
    texts = [a.text for a in articles]

    print(f"Embedding {len(texts)} articles...")
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)

    vectors = []
    for article, embedding in zip(articles, embeddings):
        vectors.append({
            "id": article.id,
            "values": embedding.tolist(),
            "metadata": {
                "title": article.title,
                "summary": article.summary[:300],
                "url": article.url,
                "source": article.source,
                "published": article.published,
            },
        })

    # Upsert in batches of 100 (Pinecone limit)
    for i in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[i:i + 100])

    print(f"Upserted {len(vectors)} vectors into Pinecone.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("Loading embedding model (first run downloads ~90MB)...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = get_or_create_index(pc)

    articles = fetch_all_sources()
    if not articles:
        print("No articles fetched. Check your network or sources.")
        return

    upsert_articles(index, articles, model)
    print("Ingestion complete.")


if __name__ == "__main__":
    run()
