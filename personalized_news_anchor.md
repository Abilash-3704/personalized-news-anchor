# Personalized News Anchor — Project Spec

## What it does

Every morning, an agent wakes up, reads dozens of news sources, figures out what's relevant to you, writes a 5-minute briefing script, converts it to audio, and emails it to you — like a personal NPR host who only covers things you care about.

## Stack

| Piece | Tool | Cost |
|---|---|---|
| LLM (writing agent) | Groq (Llama 3) | Free |
| TTS | Google Cloud TTS | Free (1M chars/month) |
| News ingestion | RSS feeds + HackerNews API + Reddit API | Free |
| Vector DB | Pinecone free tier | Free |
| Delivery | Resend (email the MP3) | Free (100 emails/day) |
| Scheduling | GitHub Actions | Free |

**Total cost: $0/month**

## How it works

### 1. Ingestion
- Pull articles from RSS feeds, HackerNews, Reddit
- Chunk and embed content into Pinecone vector DB

### 2. Personalization
- You define a profile: topics, people, companies you care about
- Agent semantically searches Pinecone against your profile
- Picks top 8-10 stories (not keyword filtering — actual semantic relevance)

### 3. Writing Agent
- Groq (Llama 3) takes the top stories and writes a cohesive script
- Grouped by theme, consistent tone, ~5 minutes when read aloud

### 4. TTS
- Script goes to Google Cloud TTS
- Output is an MP3 file

### 5. Delivery
- MP3 is emailed to you via Resend as an attachment

### 6. Scheduling
- GitHub Actions runs the whole pipeline every morning at 7am via cron

## Build Order

1. Get API keys: Groq, Google Cloud TTS, Pinecone, Resend
2. Build the ingestion script (RSS + HN + Reddit → Pinecone)
3. Build the writing agent (Pinecone → Groq → script)
4. Add TTS (script → Google Cloud TTS → MP3)
5. Add delivery (MP3 → Resend email)
6. Add scheduling (GitHub Actions cron job)

## API Keys needed

- Groq — groq.com (free, instant signup)
- Google Cloud — console.cloud.google.com (enable Cloud Text-to-Speech API, free tier)
- Pinecone — pinecone.io (free tier)
- Resend — resend.com (free tier)

## News Sources to start with

- HackerNews: `https://news.ycombinator.com/rss`
- Reddit (pick subreddits via their RSS): `https://www.reddit.com/r/<subreddit>.rss`
- TechCrunch: `https://techcrunch.com/feed/`
- The Verge: `https://www.theverge.com/rss/index.xml`
- Add any others you like
