# AI News Aggregator — Multi-Agent GenAI Pipeline

An intelligent, fully automated AI news aggregation system that scrapes, summarizes, curates, and delivers personalized daily AI newsletters — powered by a **multi-agent architecture** using open-source LLMs via **Groq**, with zero paid API dependencies.

> Built by **Grishmank Parate** | Dual Degree CSE @ IIITDM Kancheepuram

---

## Key Features

- **Multi-Agent AI Pipeline** — Three specialized AI agents (Digest, Curator, Email) collaborate to process raw news into personalized newsletters
- **100% Free & Open-Source Stack** — Uses Groq's free-tier inference on open-source LLMs instead of paid OpenAI/GPT APIs
- **Automated Daily Delivery** — GitHub Actions cron job sends curated AI news to your inbox every morning
- **Smart Content Curation** — AI ranks articles based on a configurable user profile (interests, expertise level, preferences)
- **Multi-Source Scraping** — Aggregates content from YouTube AI channels, OpenAI Blog, and Anthropic Research
- **Branded HTML Newsletters** — Professional email templates with custom header, footer, and styling
- **Local-First Database** — SQLite for zero-config local development; PostgreSQL + Docker support for production

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA GATHERING LAYER                      │
│                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │   YouTube     │  │  OpenAI Blog │  │  Anthropic Blog  │  │
│   │   Scraper     │  │   Scraper    │  │    Scraper       │  │
│   └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│          └─────────────────┼───────────────────┘             │
│                            ▼                                 │
│                    ┌──────────────┐                           │
│                    │    SQLite    │                           │
│                    │   Database   │                           │
│                    └──────┬──────┘                            │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│              MULTI-AGENT AI PROCESSING LAYER                 │
│                           ▼                                  │
│    ┌─────────────────────────────────────────────┐           │
│    │     Agent 1: DIGEST AGENT                   │           │
│    │  Summarizes raw articles into concise        │           │
│    │  structured digests using Groq LLM           │           │
│    └──────────────────┬──────────────────────────┘           │
│                       ▼                                      │
│    ┌─────────────────────────────────────────────┐           │
│    │   Agent 2: CURATOR AGENT                  │           │
│    │  Scores & ranks digests against user profile │           │
│    │  (interests, expertise, preferences)         │           │
│    └──────────────────┬──────────────────────────┘           │
│                       ▼                                      │
│    ┌─────────────────────────────────────────────┐           │
│    │     Agent 3: EMAIL AGENT                    │           │
│    │  Writes personalized greeting & formats      │           │
│    │  the final newsletter with top articles      │           │
│    └──────────────────┬──────────────────────────┘           │
│                       │                                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
┌───────────────────────┼──────────────────────────────────────┐
│                  DELIVERY LAYER                              │
│                       ▼                                      │
│   ┌──────────────────────────────────────────┐               │
│   │         Gmail SMTP (smtplib)              │               │
│   │  Sends branded HTML email to your inbox   │               │
│   └──────────────────────────────────────────┘               │
│   ┌──────────────────────────────────────────┐               │
│   │      Local Backup (output/ directory)     │               │
│   │  Saves latest_digest.html as fallback     │               │
│   └──────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────┘
```

---

##  Free Alternatives Used (Zero-Cost Stack)

This project was originally designed around paid services. Every paid dependency has been replaced with a **100% free alternative**:

| Component | Original (Paid) | Replacement (Free) | Why |
|-----------|-----------------|-------------------|-----|
| **LLM API** | OpenAI GPT-4 / GPT-3.5 ($$$) | **Groq** (`groq/compound-mini`) | Free-tier inference on open-source models with blazing-fast speed. Custom rate-limit retry logic handles free-tier throttling automatically. |
| **Database** | PostgreSQL (requires hosting) | **SQLite** (local file) | Zero setup — stores everything in a single `ai_news_aggregator.db` file. No server, no Docker, no config. |
| **Email Delivery** | Third-party email services | **Gmail SMTP** (Python `smtplib`) | Free email delivery using Gmail App Passwords. Falls back to saving HTML locally if credentials are not configured. |
| **Deployment** | Cloud VPS / Paid CI-CD | **GitHub Actions** (free tier) | Automated daily cron job runs the pipeline on GitHub's free Ubuntu runners. |

### Centralized LLM Client (`app/agent/llm_client.py`)

A custom abstraction layer was built to support **multiple LLM providers** through a single interface:

```
Priority Order: Groq → Gemini → OpenAI → Ollama (local)
```

Features:
- **Automatic provider detection** from environment variables
- **JSON structured output** with Pydantic schema validation
- **Rate-limit retry logic** with exponential backoff (handles Groq's free-tier 429 errors)
- **Markdown cleanup** for responses wrapped in code blocks

---

## 📂 Project Structure

```
ai-news-aggregator/
│
├── .github/workflows/
│   └── daily_digest.yml          # GitHub Actions: automated daily pipeline
│
├── app/
│   ├── agent/
│   │   ├── llm_client.py         # Centralized LLM client (Groq/OpenAI/Gemini/Ollama)
│   │   ├── digest_agent.py       # Agent 1: Article summarization
│   │   ├── curator_agent.py      # Agent 2: Profile-based ranking & scoring
│   │   └── email_agent.py        # Agent 3: Personalized email generation
│   │
│   ├── database/
│   │   ├── connection.py         # SQLite/PostgreSQL connection manager
│   │   ├── create_tables.py      # Database initialization script
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── repository.py         # Data access layer (CRUD operations)
│   │
│   ├── profiles/
│   │   └── user_profile.py       # Configurable user profile for AI curation
│   │
│   ├── scrapers/
│   │   ├── youtube.py            # YouTube AI channel scraper
│   │   ├── openai.py             # OpenAI Blog RSS scraper
│   │   └── anthropic.py          # Anthropic Research scraper
│   │
│   ├── services/
│   │   ├── email_service.py      # Gmail SMTP sender + branded HTML templates
│   │   ├── process_digest.py     # Batch digest generation orchestrator
│   │   ├── process_email.py      # Email dispatch orchestrator
│   │   ├── process_markdown.py   # HTML to Markdown converter
│   │   └── process_transcripts.py# YouTube transcript cleaner
│   │
│   ├── config.py                 # Logging and path configuration
│   ├── daily_runner.py           # 5-step pipeline orchestrator
│   └── runner.py                 # Standalone scraper runner
│
├── docker/
│   └── docker-compose.yml        # PostgreSQL container for production
│
├── main.py                       # Entry point: runs the full pipeline
├── pyproject.toml                # Python project & dependency configuration
├── .env.example                  # Template for environment variables
└── .gitignore                    # Protects secrets (.env, .db, output/)
```

---

##  Getting Started (Step-by-Step Execution Guide)

### Prerequisites
- **Python 3.10+** installed ([download](https://www.python.org/downloads/))
- A free **Groq API Key** — [Get one here](https://console.groq.com/keys) (takes 30 seconds, no credit card)
- A **Gmail account** with [App Password](https://myaccount.google.com/apppasswords) enabled (for sending emails)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/grishmankp-crypto/ai-news-aggregator.git
cd ai-news-aggregator
```

### Step 2: Create the `.env` Configuration File
Create a file named `.env` in the project root directory (same level as `main.py`):
```env
# LLM Provider
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/compound-mini

# Email Delivery
MY_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password

# Database (SQLite — zero setup)
USE_POSTGRES=false
SQLITE_PATH=ai_news_aggregator.db
```
>  **Never commit `.env` to GitHub** — it's already in `.gitignore`.

### Step 3: Install Python Dependencies
```bash
pip install openai pydantic python-dotenv feedparser beautifulsoup4 markdown markdownify sqlalchemy youtube-transcript-api
```

### Step 4: Initialize the Database
This creates the SQLite database file and all required tables:
```bash
python app/database/create_tables.py
```
**Expected output:**
```
Tables created successfully
```
**What happens:** Creates `ai_news_aggregator.db` in the project root with tables for `articles`, `digests`, and `emails`.

### Step 5: Test the Scrapers (Optional)
Run the scrapers individually to verify they are working:
```bash
python app/runner.py
```
**Expected output:**
```
✓ Scraped 1 YouTube videos, 4 OpenAI articles, 0 Anthropic articles
```

### Step 6: Run the Full AI Pipeline
This is the main command that executes the entire 5-step pipeline:
```bash
python main.py
```

**What happens step-by-step:**
```
============================================================
Starting Daily AI News Aggregator Pipeline
============================================================

[1/5] Scraping articles from sources...
✓ Scraped YouTube videos, OpenAI articles, Anthropic articles

[2/5] Processing Anthropic markdown...
✓ Converts raw HTML blog posts into clean Markdown

[3/5] Processing YouTube transcripts...
✓ Fetches and cleans video transcripts

[4/5] Creating digests for articles...
✓ AI Agent 1 (Digest Agent) summarizes each article using Groq LLM

[5/5] Generating and sending email digest...
✓ AI Agent 2 (Curator Agent) ranks articles against your profile
✓ AI Agent 3 (Email Agent) writes personalized introduction
✓ Email sent successfully with top articles!

============================================================
Pipeline Summary
============================================================
Duration: ~25 seconds
Email: Sent ✓
============================================================
```

### Step 7: View the Newsletter
- **In your inbox:** Check your Gmail for the branded newsletter
- **Local backup:** Open `output/latest_digest.html` in any browser

### Optional: Customize Your Profile
Edit `app/profiles/user_profile.py` to change:
- Your **name** and **background**
- Your **AI interests** (what topics the curator prioritizes)
- Your **expertise level** (affects content complexity)
- Your **preferences** (practical vs theoretical, open-source vs enterprise)

---

## ⚙️ Automated Daily Delivery (GitHub Actions)

The project includes a GitHub Actions workflow that runs the pipeline automatically every day.

### Setup:
1. Push this repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add these repository secrets:
   - `GROQ_API_KEY` — Your Groq API key
   - `MY_EMAIL` — Your Gmail address
   - `APP_PASSWORD` — Your Gmail App Password
4. The workflow runs daily at **06:00 UTC (11:30 AM IST)**
5. You can also trigger it manually from the **Actions** tab

---

## 🔮 Future Roadmap & Scalability

### Multi-User SaaS Architecture
- **User Registration Portal** — Web frontend (React/Next.js + FastAPI) for user signup
- **Password Security** — `bcrypt` hashing for stored credentials
- **Transactional Email** — Migrate from personal Gmail SMTP to AWS SES / SendGrid / Resend for bulk delivery

### Production Infrastructure
- **PostgreSQL via Docker** — Already supported (`docker/docker-compose.yml`). Switch `USE_POSTGRES=true` in `.env`
- **Async Task Queue** — Celery + Redis workers for parallel digest generation across thousands of users
- **Containerized Deployment** — Full Dockerized app with multi-stage builds for cloud hosting (AWS ECS / GCP Cloud Run)

### Content Expansion
- **Additional Sources** — Google DeepMind, Hugging Face blog, arXiv papers, TechCrunch AI
- **Multi-language Support** — Translated digests for non-English readers
- **Web Dashboard** — Real-time article browsing, search, and analytics

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.12+ |
| **AI/LLM** | Groq API (OpenAI-compatible), Pydantic structured output |
| **Database** | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy ORM |
| **Email** | Python `smtplib` + Gmail SMTP SSL |
| **Scraping** | `feedparser`, `BeautifulSoup4`, `youtube-transcript-api` |
| **Automation** | GitHub Actions (cron-based daily pipeline) |
| **Containerization** | Docker Compose (optional PostgreSQL) |

---

##  License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>Built with 🧠 Multi-Agent AI &nbsp;•&nbsp; Powered by Groq Open-Source LLMs &nbsp;•&nbsp; Zero Cost</strong>
</p>
