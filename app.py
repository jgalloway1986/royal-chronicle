import streamlit as st
import sys
import os

# Secure pathing for our subfolder scraper script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from scrapers.royal_scraper import fetch_royal_news
except ImportError:
    fetch_royal_news = None

# --- UK ROYAL PALETTE CONFIGURATION ---
st.set_page_config(
    page_title="The Royal Chronicle",
    page_icon="👑",
    layout="centered"
)

# Custom injection for British theme styling (Royal Blue: #00247D, Imperial Gold: #CFB53B)
st.markdown("""
    <style>
    .stApp {
        background-color: #F9F9FB;
    }
    h1 {
        color: #00247D !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
        text-align: center;
        border-bottom: 3px double #CFB53B;
        padding-bottom: 10px;
    }
    .story-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #00247D;
        border-right: 5px solid #CFB53B;
        margin-bottom: 15px;
    }
    .story-source {
        color: #CFB53B;
        font-weight: bold;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .story-title {
        color: #111111;
        font-size: 1.25em;
        font-family: 'Georgia', serif;
        margin: 5px 0px;
    }
    .story-date {
        color: #777777;
        font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# --- APP LAYOUT UI ---
st.markdown("<h1>👑 THE ROYAL CHRONICLE 👑</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #555;'>Her Majesty's Latest Royal News & High-Society Gossip</p>", unsafe_allow_html=True)

# Sidebar UI inputs for simple controls
st.sidebar.markdown("<h2 style='color: #00247D;'>🇬🇧 App Controls</h2>", unsafe_allow_html=True)
story_limit = st.sidebar.slider("Number of stories to pull:", min_value=3, max_value=15, value=6)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 0.8em; color: #666;'>Built locally on Bazzite. Powered by Qwen 2.5 AI acceleration.</p>", unsafe_allow_html=True)

# Main action trigger button
if st.button("🇬🇧 Fetch Latest Royal Briefing", use_container_width=True):
    with st.spinner("Dispatching royal couriers to extract gossip..."):
        if not fetch_royal_news:
            st.error("Scraper layout engine missing. Check your folders.")
        else:
            stories = fetch_royal_news(limit_per_source=story_limit)
            
            if not stories or "error" in stories:
                st.error("Apologies! Could not establish a connection to the royal dispatch networks.")
            else:
                st.success(f"Successfully gathered the latest {len(stories)} updates!")
                st.markdown("---")
                
                # Print each story element cleanly structured using the theme styling layout
                for item in stories:
                    st.markdown(f"""
                        <div class="story-card">
                            <div class="story-source">📍 {item['source']}</div>
                            <div class="story-title">📄 <a href="{item['link']}" target="_blank" style="color: #00247D; text-decoration: none;">{item['title']}</a></div>
                            <div class="story-date">📅 Published: {item['published']}</div>
                        </div>
                    """, unsafe_allow_html=True)
else:
    # Warm welcome state when app opens
    st.info("Welcome to the Chronicle. Click the big button above to pull the latest headlines directly from the UK press networks!")
