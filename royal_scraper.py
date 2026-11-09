import feedparser
import requests
import urllib.parse
import streamlit as st

def fetch_royal_news(limit_per_source: int = 5):
    aggregated_news = []

    base_url = "https://google.com"

    # Updated query string without the rigid word formatting to ensure hits
    params = {
        "q": "British Royal Family Gossip",
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en"
    }

    feed_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # Human-emulating User-Agent signature to slide past anti-bot firewalls
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/xml, text/xml, */*"
    }

    try:
        # Download the raw XML stream data using our browser identity profile
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the raw text content string inside feedparser directly
        feed = feedparser.parse(response.text)

        # Fallback: If Gossip specific search is dry, widen to general Royal Family terms
        if not feed.entries:
            params["q"] = "British Royal Family"
            feed_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            response = requests.get(feed_url, headers=headers, timeout=15)
            feed = feedparser.parse(response.text)

        if not feed.entries:
            return [{"source": "Scraper Engine", "error": "Firewall cleared, but feed returned no current items."}]

        for entry in feed.entries[:limit_per_source]:
            raw_title = entry.get("title", "No Title")

            if " - " in raw_title:
                clean_title, source_name = raw_title.rsplit(" - ", 1)
            else:
                clean_title = raw_title
                source_name = "News Aggregate"

            item = {
                "source": source_name.strip(),
                "title": clean_title.strip(),
                "link": entry.get("link", "#"),
                "published": entry.get("published", "Unknown Date")
            }
            aggregated_news.append(item)
    except Exception as e:
        aggregated_news.append({"source": "Google News Cluster", "error": f"Network extraction breakdown: {str(e)}"})

    return aggregated_news

# --- Simple UI Layout to Display on Streamlit App ---
st.set_page_config(page_title="Royal Gossip Tracker", page_icon="👑", layout="centered")

st.title("👑 Royal Family Gossip Tracker")
st.write("Fetching latest updates from Google News RSS...")

# Automatically fetch news when the page opens
if "news" not in st.session_state:
    st.session_state.news = fetch_royal_news()

if st.button("Refresh Gossip Feed"):
    st.session_state.news = fetch_royal_news()
    st.rerun()

# Render findings on screen
for item in st.session_state.news:
    if "error" in item:
        st.error(f"Error ({item['source']}): {item['error']}")
    else:
        with st.container(border=True):
            st.subheader(item["title"])
            st.caption(f"Source: {item['source']} | Published: {item['published']}")
            st.markdown(f"[Read full story]({item['link']})")
