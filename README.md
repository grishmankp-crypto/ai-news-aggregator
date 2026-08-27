# 🤖 AI News Aggregator SaaS — Multi-Agent GenAI Platform

An intelligent, multi-user AI news aggregation SaaS platform that scrapes, summarizes, curates, and delivers personalized daily AI newsletters — powered by a **multi-agent GenAI architecture** using open-source LLMs via **Groq**, a **Next.js registration portal** deployed on **Vercel**, a **Neon Cloud PostgreSQL** database, and **Resend** transactional email delivery — all built on a **100% free-tier stack ($0/month)**. Engineered for **1000+ subscriber scalability** with batch email delivery, shared digest curation, and **Hacker News AI** as a fourth content source.

> Built by **Grishmank Parate** | Dual Degree CSE @ IIITDM Kancheepuram

---

## ✨ Key Features

- **🌐 Multi-User SaaS Platform** — Users subscribe via a web portal, choose their AI interest topics, and receive personalized daily newsletters
- **🧠 Multi-Agent AI Pipeline** — Three specialized AI agents (Digest, Curator, Email) collaborate to process raw news into personalized newsletters
- **📈 1000+ User Scalability** — Shared global digest ranking (O(1) LLM calls), batch user processing, and Resend batch email API (100 emails/request)
- **⚡ 100% Free & Open-Source Stack** — Zero paid API dependencies: Groq (LLM), Neon (Postgres), Resend (Email), Vercel (Frontend), GitHub Actions (Cron)
- **🎨 Next.js Registration Portal** — Clean, responsive web interface for user onboarding with topic selection and instant database sync
- **📊 Personalized Content Curation** — AI ranks articles based on each user's profile, interests, and expertise level
- **📬 Resend Transactional Email Delivery** — High-deliverability HTML emails with batch API support, automatic Gmail SMTP fallback, and unsubscribe handling
- **📡 Multi-Source Scraping** — Aggregates content from YouTube AI channels, OpenAI Blog, Anthropic Research, and **Hacker News AI stories**
- **⏰ Automated Daily Execution** — GitHub Actions cron job runs the multi-agent pipeline daily at 03:00 UTC (8:30 AM IST)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRATION & WEB LAYER                 │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            Next.js Frontend (Vercel)                │   │
│   │  • Landing Page with AI topic selection             │   │
│   │  • Serverless API (/api/subscribe, /api/unsubscribe)│   │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │ writes user data
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD DATABASE LAYER                     │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           Neon Cloud PostgreSQL (Serverless)        │   │
│   │  • users (id, email, name, interests, is_active)    │   │
│   │  • youtube_videos, openai_articles, anthropic_articles│  │
│   │  • digests (id, title, summary, created_at)         │   │
│   │  • email_logs (id, user_id, subject, status)        │   │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │ reads & writes
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              MULTI-AGENT AI PROCESSING LAYER                 │
│              (GitHub Actions / Local Python)                │
│                                                             │
│   [1] GLOBAL INGESTION (Runs once daily)                    │
│       Scrape YouTube, OpenAI, Anthropic, Hacker News → DB  │
│                                                             │
│   [2] GLOBAL DIGEST AGENT (Runs once daily)                 │
│       Summarize raw articles into digests via Groq LLM      │
│                                                             │
│   [3] GLOBAL RANKING (Runs once, shared across all users)   │
│       Curator Agent ranks digests via single LLM call       │
│                                                             │
│   [4] PER-USER DELIVERY LOOP (handles 1000+ users)          │
│       For each active user (batched, 50 users/batch):       │
│       ├── 📊 Interest Filter: Re-ranks articles per user    │
│       ├── ✉️ Email Agent: Writes personalized intro & HTML   │
│       └── 📬 Resend Batch API: Sends 100 emails/request     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆓 Free-Tier Stack ($0/Month)

| Component | Service | Free Tier Allocation | Why |
|-----------|---------|---------------------|-----|
| **LLM Inference** | [Groq](https://console.groq.com) | Free-tier open-source models | Ultra-fast LPU inference (`groq/compound-mini`). Built-in retry logic handles rate limits automatically. |
| **Cloud Database** | [Neon](https://neon.tech) | 0.5 GB storage, serverless Postgres | Zero-maintenance cloud PostgreSQL accessible from both Vercel serverless functions and Python pipeline. |
| **Transactional Email** | [Resend](https://resend.com) | 3,000 emails/month (100/day) | Modern transactional email API with high deliverability. Automatic fallback to Gmail SMTP. |
| **Frontend Hosting** | [Vercel](https://vercel.com) | 100 GB bandwidth, serverless | Hosts Next.js landing page and subscription API routes. |
| **Automation** | [GitHub Actions](https://github.com) | 2,000 runner minutes/month | Executes the daily multi-agent scraping and email delivery pipeline on a cron schedule. |

---

## 📂 Project Structure

```
ai-news-aggregator/
│
├── .github/workflows/
│   └── daily_digest.yml          # GitHub Actions: automated daily multi-user pipeline
│
├── app/
│   ├── agent/
│   │   ├── llm_client.py         # Multi-provider LLM client with retry logic (Groq/Gemini/OpenAI/Ollama)
│   │   ├── digest_agent.py       # Agent 1: Article summarization
│   │   ├── curator_agent.py      # Agent 2: Profile-based ranking & scoring
│   │   └── email_agent.py        # Agent 3: Personalized email generator
│   │
│   ├── database/
│   │   ├── connection.py         # Neon PostgreSQL / SQLite connection pool
│   │   ├── create_tables.py      # Database table initialization script
│   │   ├── models.py             # SQLAlchemy models (User, EmailLog, Digest, Articles)
│   │   └── repository.py         # Data access layer (User CRUD, Content queries, Email logging)
│   │
│   ├── profiles/
│   │   └── user_profile.py       # Fallback single-user profile configuration
│   │
│   ├── scrapers/
│   │   ├── youtube.py            # YouTube AI channel scraper with transcript extractor
│   │   ├── openai.py             # OpenAI Blog RSS scraper
│   │   ├── anthropic.py          # Anthropic Research scraper with Markdown extractor
│   │   └── hackernews.py         # Hacker News AI story scraper (Algolia Search API)
│   │
│   ├── services/
│   │   ├── email_service.py      # Resend API + Gmail SMTP sender + dynamic HTML templates
│   │   ├── process_digest.py     # Batch digest generation orchestrator
│   │   ├── process_email.py      # Multi-user personalized email dispatch orchestrator
│   │   ├── process_markdown.py   # HTML to Markdown converter
│   │   └── process_transcripts.py# YouTube transcript cleaner
│   │
│   ├── config.py                 # Scraper channel configuration
│   ├── daily_runner.py           # 5-step end-to-end pipeline orchestrator
│   └── runner.py                 # Standalone scraper runner
│
├── frontend/                     # Next.js Web Application (Deploy to Vercel)
│   ├── app/
│   │   ├── api/
│   │   │   ├── subscribe/        # POST: Inserts new subscribers into Neon DB
│   │   │   └── unsubscribe/      # GET: One-click unsubscribe handler
│   │   ├── globals.css           # Tailwind CSS styling
│   │   ├── layout.tsx            # App shell layout
│   │   └── page.tsx              # Landing page with topic selector
│   ├── package.json              # Frontend dependencies
│   ├── tailwind.config.ts        # Tailwind configuration
│   └── tsconfig.json             # TypeScript configuration
│
├── main.py                       # Pipeline entry point
├── pyproject.toml                # Python project configuration (v2.1.0)
├── .env.example                  # Environment variable template
└── .gitignore                    # Protects secrets (.env, output/)
```

---

## 🚀 Getting Started (Step-by-Step Execution Guide)

### Prerequisites
- **Python 3.10+** installed
- **Node.js 18+** (for frontend development)
- Free accounts on:
  - [Groq Console](https://console.groq.com/keys) (LLM API key)
  - [Neon](https://neon.tech) (PostgreSQL connection string)
  - [Resend](https://resend.com) (Email API key)
  - [Vercel](https://vercel.com) (Frontend deployment)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/grishmankp-crypto/ai-news-aggregator.git
cd ai-news-aggregator
```

### Step 2: Configure Environment Variables
Create a `.env` file in the project root:
```env
# LLM Provider (Groq Free Tier)
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=groq/compound-mini

# Transactional Email (Resend Free Tier)
RESEND_API_KEY=re_your_resend_key

# Email Fallback (Gmail SMTP)
MY_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password

# Database (Neon Cloud PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-something.neon.tech/neondb?sslmode=require
USE_POSTGRES=true
```

### Step 3: Install Python Dependencies
```bash
pip install openai pydantic python-dotenv feedparser beautifulsoup4 markdown markdownify sqlalchemy youtube-transcript-api psycopg2-binary requests resend
```

### Step 4: Initialize Cloud Database Tables
```bash
python app/database/create_tables.py
```
**Expected output:**
```
Tables created successfully
```

### Step 5: Run the Full AI Pipeline
```bash
python main.py
```

**Pipeline execution flow:**
```
============================================================
Starting Daily AI News Aggregator Pipeline
============================================================

[1/5] Scraping articles from sources...
✓ Scraped YouTube videos, OpenAI articles, Anthropic articles, Hacker News AI stories

[2/5] Processing Anthropic markdown...
✓ Converts raw HTML blog posts into clean Markdown

[3/5] Processing YouTube transcripts...
✓ Fetches and cleans video transcripts

[4/5] Creating digests for articles...
✓ Agent 1 (Digest Agent) summarizes each article using Groq LLM

[5/5] Generating and sending email digests...
✓ Generates ONE global ranking (shared across all users)
✓ Fetches all active subscribers from Neon PostgreSQL
✓ For each user batch (50 users/batch):
    • Interest Filter: Re-ranks articles per user preferences
    • Email Agent: Writes personalized introduction
    • Resend Batch API: Delivers branded HTML emails (100/request)
✓ Emails delivered: N sent, 0 failed

============================================================
Pipeline Summary
============================================================
Duration: ~30 seconds (scales to 1000+ users)
Email: Sent ✓
============================================================
```

---

## 🌐 Deploying the Next.js Frontend to Vercel

The `frontend/` directory contains a complete Next.js app ready for Vercel deployment:

### 1. Local Testing
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the registration portal.

### 2. Deploy to Vercel
1. Push your repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import your repository.
3. Set **Root Directory** to `frontend`.
4. In **Environment Variables**, add:
   - `DATABASE_URL` = your Neon PostgreSQL connection string
5. Click **Deploy**!

Your registration portal is now live with a public URL (e.g., `https://ai-radar.vercel.app`). Anyone can visit the site, enter their email, select their AI interests, and get added to the daily newsletter database!

---

## ⚙️ Automated Daily Delivery (GitHub Actions)

The repository includes a GitHub Actions workflow that executes the entire pipeline daily.

### Setup Repository Secrets:
Go to **GitHub Repo → Settings → Secrets and variables → Actions** and add:
- `GROQ_API_KEY` — Your Groq API key
- `DATABASE_URL` — Your Neon PostgreSQL connection string
- `RESEND_API_KEY` — Your Resend API key
- `RESEND_FROM_EMAIL` — Your verified Resend sender email (e.g., `newsletter@yourdomain.com`)
- `MY_EMAIL` — Your Gmail address (for fallback)
- `APP_PASSWORD` — Your Gmail App Password (for fallback)

The workflow runs daily at **03:00 UTC (8:30 AM IST)** and can also be triggered manually via the **Run workflow** button in the Actions tab.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| **Frontend Hosting** | Vercel (Serverless Functions) |
| **AI / Multi-Agent** | Groq API (OpenAI-compatible), Pydantic structured output |
| **Backend / Pipeline** | Python 3.12+, SQLAlchemy ORM |
| **Database** | Neon Cloud PostgreSQL (serverless) / SQLite (dev) |
| **Email Delivery** | Resend API (primary) + Python `smtplib` (Gmail fallback) |
| **Scraping** | `feedparser`, `BeautifulSoup4`, `youtube-transcript-api`, Hacker News Algolia API |
| **CI/CD & Cron** | GitHub Actions |

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>Built with 🧠 Multi-Agent AI &nbsp;•&nbsp; Powered by Groq Open-Source LLMs &nbsp;•&nbsp; Hosted on Vercel & Neon &nbsp;•&nbsp; $0/Month</strong>
</p>
