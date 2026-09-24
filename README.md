# SENTINEL — Real-Time Stock Market Sentiment Dashboard

**SENTINEL** is a Python + Streamlit stock intelligence dashboard that combines market-price data with sentiment extracted from financial news and Reddit discussions.

> **Important:** The dashboard is an analytics/education project, not a financial-advice system. Its BUY/HOLD/SELL labels are rule-based sentiment signals, not investment recommendations.

## Project Overview

**Project title:** Real-Time Stock Market Sentiment Dashboard — Combine News + Social Media Sentiment with Live Price Data

**Domain:** Data Science · NLP · Sentiment Analysis · Financial Analytics · Data Visualization · Streamlit

The application:
- Retrieves stock price and volume history with `yfinance`.
- Retrieves financial news through NewsAPI, with Google News RSS as a fallback.
- Retrieves recent posts from selected Reddit communities.
- Calculates text polarity with TextBlob.
- Applies recency weighting to news and Reddit sentiment.
- Applies an engagement weighting to Reddit posts using Reddit score/upvotes.
- Combines news and Reddit sentiment using a 60% / 40% weighting when both sources are available.
- Stores sentiment history and cached news/Reddit records in SQLite.
- Refreshes the Streamlit application every 60 seconds.
- Displays price charts, normalized comparisons, volume, RSI, sentiment distributions, historical sentiment, and source-level data.

## Architecture

```text
                     ┌─────────────────────┐
                     │      Streamlit      │
                     │     Dashboard UI    │
                     └──────────┬──────────┘
                                │
           ┌────────────────────┼─────────────────────┐
           │                    │                     │
           ▼                    ▼                     ▼
      Yahoo Finance          NewsAPI              Reddit
      (yfinance)         Google News RSS       public JSON API
           │                    │                     │
           └──────────────┬─────┴─────────────────────┘
                          ▼
                 TextBlob Sentiment
                          │
                Recency / engagement
                       weighting
                          │
                News + Reddit fusion
                     (60 / 40)
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      Sentiment signal            SQLite DB
       BUY/HOLD/SELL          history + cache
             │
             ▼
         Dashboard
```

## Main Features

### 1. Market Data
- Supports up to 5 stock symbols.
- Configurable periods: 1M, 3M, 6M, 1Y, 2Y.
- Current/latest downloaded close price and previous-period change.
- Normalized multi-symbol comparison.
- Single-symbol price chart with MA20 and MA50.
- Volume visualization.
- RSI (14) visualization.

### 2. Financial News Sentiment
Primary source:
- NewsAPI

Fallback:
- Google News RSS

For each article, the application:
1. Combines title and description.
2. Calculates TextBlob polarity.
3. Removes duplicate titles.
4. Classifies sentiment:
   - Positive: polarity > 0.05
   - Neutral: -0.05 to +0.05
   - Negative: polarity < -0.05
5. Applies a recency-decay weight.

### 3. Reddit Sentiment
The application searches:
- r/wallstreetbets
- r/stocks
- r/investing

It combines post title + body, calculates TextBlob polarity, and weights the result using:
- post age
- Reddit score/upvotes

### 4. Combined Sentiment

When both sources are available:

`Combined Score = 0.60 × News Score + 0.40 × Reddit Score`

If only one source is available, the available source is used directly.

Signal thresholds implemented in the source code:

| Sentiment score | Label |
|---:|---|
| > +0.10 | BUY |
| -0.10 to +0.10 | HOLD |
| < -0.10 | SELL |

These labels are **rule-based project signals**, not validated trading recommendations.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| Dashboard | Streamlit |
| Market data | yfinance |
| News | NewsAPI + Google News RSS fallback |
| Social data | Reddit public JSON endpoints |
| NLP | TextBlob |
| Data processing | Pandas |
| Visualization | Matplotlib |
| Database | SQLite |
| HTTP | Requests |
| HTML/XML parsing | BeautifulSoup + lxml |
| Time zones | pytz |
| Auto-refresh | streamlit-autorefresh |

## Project Structure

```text
SENTINEL/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

Local runtime files are intentionally not committed:
- `sentinel_dashboard.db`
- other `*.db` / SQLite files
- `sentiment_history*.json`
- `.env`

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SENTINEL
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure NewsAPI

Copy `.env.example` to `.env` and add your own NewsAPI key.

```text
NEWS_API_KEY=your_real_key_here
```

Do **not** commit `.env`.

### 5. Run

```bash
streamlit run app.py
```

## GitHub Security — Important

The original uploaded source contained a hard-coded NewsAPI credential. Before publishing the project:

1. **Revoke/rotate that exposed API key in NewsAPI.**
2. Use the environment variable `NEWS_API_KEY`.
3. Never commit `.env`.
4. Search the repository before pushing:
   ```bash
   git grep -n "api_key"
   git grep -n "NEWS_API_KEY"
   ```
5. If the exposed key has already been pushed to GitHub, removing it from the latest commit is not sufficient; rotate the credential.

The GitHub-ready `app.py` in this package has already been changed to read `NEWS_API_KEY` from the environment.

## Data Storage

The app creates a SQLite database named:

`sentinel_dashboard.db`

Tables:
- `sentiment_history`
- `news_cache`
- `reddit_cache`

The database is local application state and is excluded from Git through `.gitignore`.

## Data & Model Methodology

### TextBlob polarity

TextBlob returns a polarity score in the range approximately from -1 to +1.

The project uses:
- Positive > 0.05
- Neutral between -0.05 and +0.05
- Negative < -0.05

### News recency weighting

News weight follows an exponential half-life style decay:

`weight = max(0.5 ** (hours_old / 24), 0.1)`

Thus, older articles receive less influence, with a minimum weight of 0.1.

### Reddit weighting

Reddit sentiment uses the same time-decay concept and multiplies it by an engagement factor based on post score.

### Technical indicators

The dashboard calculates:
- MA20
- MA50
- RSI(14)

These indicators are visualized alongside the sentiment information. They are not used by the current code to calculate the BUY/HOLD/SELL signal.

## Current Scope & Limitations

- The current source uses TextBlob rather than a finance-specific transformer such as FinBERT.
- The current sentiment signal is rule-based and is not trained or statistically validated as a trading strategy.
- NewsAPI is the primary news provider; Google News RSS is used as a fallback.
- Reddit is queried through public JSON endpoints; availability/rate limits can change.
- The code refreshes the dashboard every 60 seconds, but `yfinance` downloads market data rather than providing a guaranteed exchange-grade real-time feed.
- The dashboard does not currently contain a backtested trading strategy or predictive model.
- Sentiment does not prove that sentiment caused a price movement.
- API availability and third-party source policies can affect results.

## Suggested Future Enhancements

- Replace TextBlob with FinBERT or another finance-specific transformer.
- Add sentiment confidence scores.
- Add historical price/sentiment correlation analysis.
- Add a formal backtesting module.
- Add model evaluation metrics for any predictive model.
- Add stronger API error handling and rate-limit handling.
- Add a proper Reddit API integration where appropriate.
- Add PostgreSQL for multi-user/deployed environments.
- Add Docker support.
- Add automated tests and CI/CD.
- Add authentication for private deployments.

## Resume / LinkedIn Description

**Real-Time Stock Market Sentiment Dashboard**
- Developed a Streamlit-based financial analytics dashboard integrating stock market data, financial news, and Reddit discussions.
- Implemented NLP-based sentiment analysis using TextBlob with recency and engagement weighting.
- Designed a 60:40 news-to-Reddit sentiment fusion score with configurable BUY/HOLD/SELL thresholds.
- Built interactive market visualizations including price trends, moving averages, volume, RSI, sentiment distribution, and historical sentiment tracking.
- Implemented SQLite persistence for sentiment history and source-level cache data with automatic dashboard refresh.

## Disclaimer

This project is for educational and analytical purposes. It is not financial advice, does not guarantee market outcomes, and should not be used as the sole basis for investment decisions.
