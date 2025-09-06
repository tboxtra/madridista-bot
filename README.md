# MadridistaAI — Football Bot

## Quick Start
1) Copy environment:  
   ```bash
   cp .env.example .env
   ```
2) Install deps (Python **3.8+**):  
   ```bash
   pip install -r requirements.txt
   ```
3) Set required variables in `.env` or Railway variables (see below).
4) Run locally:  
   ```bash
   python main.py
   ```

### Railway Deployment
- This project runs as a **worker** (Telegram polling).  
- `Procfile`:
  ```
  worker: python main.py
  ```
- **Required Railway Variables**:
  - `TZ = Africa/Lagos`
  - `TELEGRAM_BOT_TOKEN`
  - `FOOTBALL_DATA_API_KEY`
  - `OPENAI_API_KEY`
  - `SOFA_USER_AGENT = Mozilla/5.0 MadridistaBot/1.0`
  - `SOFA_TEAM_ID = 2817`  # Real Madrid
  - `RAPIDAPI_KEY` (optional; LiveScore news)
  - `CITATIONS = true`
  - `OPENAI_MODEL = gpt-4o-mini` (optional)

### What this bot can do
- Natural language answers to **any football question** (keeps scope football-only)
- **Live**, **next**, **last**, **tables**, **scorers**, **injuries**, **squad**
- **Compare teams** (recent form), **compare players** (per-90), **lineups**, **news**
- Short, human replies grounded in APIs with source tags: `(SofaScore • Football-Data • LiveScore)`

## Commands
- `/start` - Welcome message
- `/matches` - Next fixture
- `/lastmatch` - Last result
- `/live` - Live score
- `/table` - League standings
- `/scorers` - Top scorers
- `/form` - Recent results
- `/lineups` - Next match lineups
- `/compare Team A vs Team B` - Compare teams
- `/compareplayers Player A vs Player B` - Compare players

## Natural Language Examples
- "next madrid fixture"
- "compare madrid vs barcelona form"
- "vinicius vs bellingham per 90"
- "madrid news today"
- "who's injured for real madrid"
- "laliga table top 5"