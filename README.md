# SENTINEL — Real-Time Stock Market Sentiment Dashboard

> **Combining Financial News, Reddit Sentiment, and Market Price Data for Real-Time Financial Analytics**

SENTINEL is a real-time financial analytics dashboard built with **Python and Streamlit** that combines stock market data, financial news, and Reddit discussions to generate weighted market sentiment signals.

The system applies **NLP-based sentiment analysis using TextBlob**, incorporates **recency and engagement weighting**, combines news and social sentiment, and provides an interactive dashboard for analyzing stock price movements, technical indicators, sentiment trends, and market signals.

---

## 🚀 Features

* 📈 Real-time/near-real-time stock market data
* 📰 Financial news sentiment analysis
* 💬 Reddit social sentiment analysis
* 🧠 NLP-based sentiment analysis using TextBlob
* ⚖️ Weighted combination of news and Reddit sentiment
* ⏱️ Recency-based sentiment weighting
* 🔥 Reddit engagement-based weighting
* 📊 Interactive stock price and volume charts
* 📉 RSI, MA20 and MA50 technical indicators
* 📈 Historical sentiment tracking
* 🔄 Automatic dashboard refresh
* 🗄️ SQLite-based local sentiment history and caching
* 📊 Multi-stock comparison
* 🟢 BUY / 🟡 HOLD / 🔴 SELL sentiment signals
* 📰 Google News RSS fallback when NewsAPI data is unavailable

---

## 🧠 How It Works

SENTINEL follows a multi-source financial sentiment analysis pipeline:

```text
                    ┌──────────────────┐
                    │   Stock Symbol   │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌───────────────┐             ┌────────────────┐
      │ Market Data   │             │ News + Reddit  │
      │   yFinance    │             │    Sources     │
      └───────┬───────┘             └───────┬────────┘
              │                             │
              │                      ┌──────┴──────┐
              │                      │             │
              │                      ▼             ▼
              │                  NewsAPI       Reddit
              │                  / RSS
              │                      │             │
              │                      └──────┬──────┘
              │                             │
              │                             ▼
              │                    ┌─────────────────┐
              │                    │ NLP Sentiment   │
              │                    │    TextBlob     │
              │                    └────────┬────────┘
              │                             │
              │                   Recency + Engagement
              │                       Weighting
              │                             │
              └──────────────┬──────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Sentiment Fusion │
                    │  News 60% +       │
                    │  Reddit 40%       │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ BUY / HOLD / SELL│
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Streamlit        │
                    │ Dashboard        │
                    └──────────────────┘
```

---

## 🛠️ Tech Stack

### Programming Language

* Python

### Framework

* Streamlit

### Data & Finance

* yFinance
* Pandas
* NumPy

### NLP & Sentiment Analysis

* TextBlob

### News & Social Data

* NewsAPI
* Google News RSS
* Reddit public JSON endpoints

### Visualization

* Matplotlib
* Streamlit charts

### Database

* SQLite

### Other Libraries

* Requests
* BeautifulSoup
* lxml
* pytz
* Streamlit Autorefresh

---

## 📊 Sentiment Methodology

### News Sentiment

Financial news articles are processed using TextBlob polarity scores.

The system considers:

* Article sentiment
* Article recency
* Duplicate headlines

More recent articles receive greater importance through recency weighting.

### Reddit Sentiment

Reddit posts are collected from:

* `r/wallstreetbets`
* `r/stocks`
* `r/investing`

Reddit sentiment considers:

* Text polarity
* Post age
* Reddit engagement/score

This provides an additional social sentiment signal alongside financial news.

---

## ⚖️ Sentiment Fusion

When both news and Reddit sentiment are available, the combined sentiment score uses:

```text
Combined Sentiment =
    60% News Sentiment
  + 40% Reddit Sentiment
```

The resulting score is converted into a market sentiment signal.

### Signal Thresholds

| Sentiment Score    | Signal |
| ------------------ | ------ |
| Greater than +0.10 | BUY    |
| -0.10 to +0.10     | HOLD   |
| Less than -0.10    | SELL   |

These signals are intended as **analytics indicators**, not financial advice or guaranteed trading predictions.

---

## 📈 Technical Analysis

The dashboard also provides market indicators including:

* Current stock price
* Price change
* Trading volume
* Moving Average 20 (MA20)
* Moving Average 50 (MA50)
* Relative Strength Index (RSI 14)
* Historical price movement

These indicators are presented alongside sentiment data to provide broader market context.

---

## 🗄️ Data Storage

SENTINEL uses SQLite for local storage.

The application maintains tables for:

* Historical sentiment
* News cache
* Reddit cache

This allows sentiment history and retrieved data to be reused within the application.

---

## 🔑 API Key Configuration

This project requires a **NewsAPI API key** to retrieve financial news.

For security reasons, the API key is **not included in this GitHub repository**.

Create a `.env` file in the project directory:

```env
NEWS_API_KEY=your_newsapi_key_here
```

A `.env.example` file is included in the repository as a template.

### Important Security Note

Never commit your actual `.env` file or API key to GitHub.

If an API key has previously been exposed publicly, revoke or rotate that key and generate a new one.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/sentinel-stock-market-sentiment-dashboard.git
```

### 2. Navigate to the project

```bash
cd sentinel-stock-market-sentiment-dashboard
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the API key

Create a `.env` file:

```env
NEWS_API_KEY=your_newsapi_key_here
```

### 7. Run the application

```bash
streamlit run app.py
```

The dashboard will open in your browser.

---

## 📁 Project Structure

```text
sentinel-stock-market-sentiment-dashboard/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
│
└── runtime files
    └── sentinel_dashboard.db
```

Runtime-generated files such as SQLite databases and local environment files should not be committed to the repository.

---

## 🔄 Dashboard Workflow

1. Select one or more stock symbols.
2. Retrieve historical market data.
3. Retrieve financial news.
4. Retrieve Reddit discussions.
5. Perform NLP sentiment analysis.
6. Apply recency weighting.
7. Apply Reddit engagement weighting.
8. Combine news and social sentiment.
9. Generate sentiment signals.
10. Display price, volume, technical indicators and sentiment trends.
11. Store historical sentiment locally.

---

## 📌 Example Use Cases

SENTINEL can be used for:

* Financial sentiment analysis
* NLP experimentation
* Stock market data visualization
* Social media sentiment research
* News analytics
* Financial data science projects
* Interactive Streamlit dashboards
* Demonstrating API integration
* Demonstrating data pipelines

---

## ⚠️ Limitations

* Market data availability depends on the external data provider.
* NewsAPI usage depends on API availability and account limits.
* Reddit data depends on public endpoint availability.
* TextBlob provides general-purpose sentiment analysis and may not fully understand financial terminology.
* Sentiment signals should not be interpreted as guaranteed stock-price predictions.
* The project does not currently contain a trained machine-learning model for stock-price prediction.
* The dashboard is intended for educational and analytical purposes.

---

## 🔮 Future Enhancements

Potential future improvements include:

* Financial-domain NLP models such as FinBERT
* Transformer-based sentiment analysis
* Real-time streaming infrastructure
* Additional social media sources
* Advanced stock-price prediction models
* Machine-learning-based signal generation
* Backtesting framework
* Portfolio-level sentiment analysis
* SHAP-based model explainability
* Cloud deployment
* User authentication
* PostgreSQL or other production database
* Docker containerization

---

## 👨‍💻 Author

**Rohan Lawrence**

BE — Data Science Engineering

PES Institute of Technology and Management

---

## 📜 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

SENTINEL is an educational and analytical software project. The BUY, HOLD, and SELL signals generated by the application are based on sentiment scoring rules and should not be considered financial advice, investment recommendations, or guaranteed predictions of future market movements.
