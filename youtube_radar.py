import streamlit as st
from googleapiclient.discovery import build
from textblob import TextBlob
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

st.set_page_config(page_title="TubeRadar Pro", page_icon="📡", layout="wide")

# CONNECT TO YOUTUBE
try:
    youtube = build('youtube', 'v3', developerKey=API_KEY)
except Exception as e:
    st.error(f"🚨 API Key Error: {e}")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_comments(video_id, limit=20):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part="snippet", videoId=video_id, textFormat="plainText", maxResults=limit
        ).execute()
        for item in response['items']:
            comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
    except:
        pass 
    return comments

def analyze_topic(topic, max_videos):
    search_response = youtube.search().list(
        q=topic, part="id,snippet", maxResults=max_videos, type="video"
    ).execute()
    data = []
    
    for item in search_response['items']:
        # 🛡️ ADD THIS CHECK HERE:
        if 'videoId' not in item['id']:
            continue  # Skip this item if it's not a video
            
        vid_id = item['id']['videoId']
        vid_title = item['snippet']['title']
        raw_comments = get_comments(vid_id)
        
        for comment in raw_comments:
            score = TextBlob(comment).sentiment.polarity
            label = "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral"
            data.append({
                "Topic": topic, 
                "Video": vid_title, 
                "Comment": comment, 
                "Score": score, 
                "Label": label
            })
            
    if not data: return None, 0
    df = pd.DataFrame(data)
    avg_score = df["Score"].mean()
    return df, avg_score

# --- MAIN APP UI ---
st.title("📡 TubeRadar: Ultimate Suite")

with st.sidebar:
    st.header("🎮 Control Center")
    mode = st.radio("Select Mode:", ["Solo Analysis", "Competitor Battle"])
    st.divider()
    
    if mode == "Solo Analysis":
        query = st.text_input("Topic to Scan", "iPhone 15")
    else:
        query_a = st.text_input("Contender A", "PlayStation 5")
        query_b = st.text_input("Contender B", "Xbox Series X")
    
    # Updated limit to 50
    limit = st.slider("Videos to Scan", 1, 50, 10)
    run_btn = st.button("🚀 Launch Scan")

# --- LOGIC ---
if run_btn:
    if mode == "Solo Analysis":
        st.subheader(f"🔍 Deep Dive: {query}")
        with st.spinner(f"Scanning up to {limit} videos..."):
            df, score = analyze_topic(query, limit)
        
        if df is not None:
            # 1. Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall Sentiment", f"{score:.2f}", delta="Good" if score > 0 else "Bad")
            c2.metric("Total Comments", len(df))
            c3.metric("Video Sample", f"{limit} clips")
            
            # 2. Charts Row
            col_left, col_right = st.columns(2)
            
            # 2. Charts Row
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("#### 📊 Top Discussion Themes")
                
                # --- NEW PROFESSIONAL BLOCK ---
                import collections
                # 1. Process text to get word counts
                text_list = " ".join(df.Comment).lower().split()
                # Filter out short/common words (like 'the', 'and', 'this')
                filtered_words = [w for w in text_list if len(w) > 4 and w.isalpha()]
                word_counts = collections.Counter(filtered_words).most_common(10)
                
                # 2. Convert to DataFrame for plotting
                theme_df = pd.DataFrame(word_counts, columns=['Keyword', 'Count'])
                
                # 3. Create a professional horizontal bar chart
                fig_themes = px.bar(theme_df, 
                                   x='Count', 
                                   y='Keyword', 
                                   orientation='h',
                                   color='Count',
                                   color_continuous_scale='Blues',
                                   text_auto=True)
                
                fig_themes.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                st.plotly_chart(fig_themes, use_container_width=True)

            with col_right:
                st.markdown("#### 📊 Sentiment Split")
                fig_pie = px.pie(df, names='Label', hole=0.4, 
                                 color_discrete_map={"Positive":"#00cc96", "Negative":"#EF553B", "Neutral":"#636efa"})
                st.plotly_chart(fig_pie, use_container_width=True)

            # NEW: SENTIMENT GRAPH (HISTOGRAM)
            st.markdown("#### 📈 Intensity Distribution")
            fig_hist = px.histogram(df, x="Score", nbins=20, 
                                   title="Are opinions mild or extreme?",
                                   labels={'Score': 'Sentiment Score (-1 to +1)'})
            st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown("#### 📄 Raw Data")
            st.dataframe(df)
        else:
            st.warning("No comments found.")

    elif mode == "Competitor Battle":
        st.subheader("⚔️ Head-to-Head Comparison")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Scanning {query_a}...")
            df_a, score_a = analyze_topic(query_a, limit)
        with col2:
            st.info(f"Scanning {query_b}...")
            df_b, score_b = analyze_topic(query_b, limit)

        if df_a is not None and df_b is not None:
            winner = query_a if score_a > score_b else query_b
            st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>🏆 Winner: {winner}</h1>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric(f"{query_a}", f"{score_a:.2f}")
            m2.metric("Sentiment Gap", f"{abs(score_a - score_b):.2f}")
            m3.metric(f"{query_b}", f"{score_b:.2f}")
            full_df = pd.concat([df_a, df_b])
            fig = px.box(full_df, x="Topic", y="Score", color="Topic", title="Sentiment Distribution")
            st.plotly_chart(fig, use_container_width=True)