"""
User personalization profile. Edit this to match your interests.
"""

PROFILE = {
    "topics": [
        "artificial intelligence",
        "machine learning",
        "startup funding",
        "software engineering",
        "developer tools",
        "open source",
    ],
    "people": [
        "Sam Altman",
        "Andrej Karpathy",
        "Linus Torvalds",
    ],
    "companies": [
        "OpenAI",
        "Anthropic",
        "Google DeepMind",
        "Mistral",
    ],
}

# Combined query used for semantic search against Pinecone
PROFILE_QUERY = " ".join(
    PROFILE["topics"] + PROFILE["people"] + PROFILE["companies"]
)

RSS_FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.reddit.com/r/MachineLearning.rss",
    "https://www.reddit.com/r/programming.rss",
]

TOP_STORIES_COUNT = 10
BRIEFING_DURATION_MINUTES = 5
