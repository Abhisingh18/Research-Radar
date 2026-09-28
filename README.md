# Research Radar

An AI research radar for ASR, TTS, speech LLMs, VLMs, multimodal AI, LLMs and AI
agents. It scans arXiv, filters to your interests, runs each candidate paper
through an LLM for a novelty/relevance read, ranks the results, and alerts you
on Telegram and/or WhatsApp — plus a Next.js dashboard to browse everything.

Designed to run on a schedule via **GitHub Actions**, so it keeps working even
when your laptop is off.

## Pipeline

```
arXiv (keyword search)
        |
keyword pre-filter (config/research_profile.yaml — free, no LLM cost)
        |
dedup against previously-seen paper IDs
        |
LLM novelty analysis (OpenRouter — Qwen / GLM / Nvidia / any model you pick)
        |
ranking score (topic priority + novelty + LLM relevance)
        |
threshold  ->  Telegram + WhatsApp alerts
        |
data/papers.json  ->  Next.js dashboard
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in the keys below; .env is gitignored
```

Required for the full pipeline (`python -m research_radar run`):

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | LLM novelty analysis — get one at https://openrouter.ai/keys |
| `OPENROUTER_MODEL` | Any model slug from https://openrouter.ai/models (Qwen, GLM, Nvidia Nemotron, etc.) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Telegram alerts (optional) |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `TWILIO_WHATSAPP_TO` | WhatsApp alerts via Twilio (optional) |

Without any notification channel configured, `run` just prints alerts to
stdout — handy for testing before wiring up Telegram/WhatsApp.

## Usage

```bash
# Full pipeline: fetch, classify, LLM novelty analysis, score, notify
python -m research_radar run --dry-run   # print instead of sending
python -m research_radar run             # send to configured channels

# Lightweight keyword search only, no LLM, no notifications
python -m research_radar search "large language models" "AI agents"
```

Edit `config/research_profile.yaml` to change what topics you care about,
their priority weights, the notify threshold, and per-run LLM/alert caps —
no code changes needed.

## Dashboard

A small Next.js app under [`frontend/`](frontend/) reads `data/papers.json`
(the same file the pipeline writes) and shows the alerted papers as cards.

```bash
cd frontend
npm install
npm run dev
```

## Cloud deployment (works with your laptop off)

[`.github/workflows/research-radar.yml`](.github/workflows/research-radar.yml)
runs the pipeline on a schedule using GitHub Actions, and commits the updated
`data/seen.json` / `data/papers.json` back to the repo so state persists
between runs — no database or server needed.

Add these as **repository secrets** (Settings → Secrets and variables →
Actions) for the scheduled run to work:

- `OPENROUTER_API_KEY`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (if using Telegram)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `TWILIO_WHATSAPP_TO` (if using WhatsApp)

You can also trigger a run manually from the Actions tab (`workflow_dispatch`).

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

## Cost control

Only papers that pass the free keyword pre-filter go to the LLM
(`max_llm_candidates` in the profile, default 15 per run), and only the
highest-scoring ones get sent as alerts (`max_alerts_per_run`, default 5).
Signal over noise — a handful of genuinely interesting papers beats fifty
keyword matches.

## Roadmap

- [ ] Hugging Face Papers + GitHub trending as additional sources
- [ ] Daily/weekly digest summaries
- [ ] Previous-work comparison ("what changed vs. prior approaches")
- [ ] Persistent database (currently a committed JSON file, fine for MVP scale)
