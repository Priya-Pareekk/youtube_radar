# 📡 TubeRadar: YouTube Sentiment Intelligence Suite

An advanced data analytics tool that performs real-time sentiment analysis on YouTube comments to gauge public mood on any topic or compare competitors.

## 🚀 Features
- **Solo Analysis**: Deep dive into a single topic with thematic bar charts and sentiment distribution.
- **Competitor Battle**: Side-by-side sentiment comparison (e.g., iPhone vs. Samsung) to determine a "Market Winner."
- **Professional Analytics**: Replaces standard word clouds with frequency-based bar charts for better data clarity.

## 🛠️ Tech Stack
- **Python**: Core logic.
- **Streamlit**: Web interface.
- **YouTube Data API v3**: Data sourcing.
- **TextBlob**: Natural Language Processing (NLP) for sentiment scoring.
- **Plotly**: Interactive data visualizations.

## 📦 Installation
1. Clone the repo: `git clone https://github.com/accountname/TubeRadar.git`
2. Install requirements: `pip install -r requirements.txt`
3. Add your `YOUTUBE_API_KEY` to a `.env` file.
4. Run: `streamlit run youtube_radar.py`