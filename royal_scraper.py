import feedparser
import requests
import urllib.parse
import streamlit as st

def fetch_royal_news(limit_per_source: int = 10):
    aggregated_news = []

    # Base RSS search cluster endpoint
    base_url = "https://google.com"

    # Bulletproof simplified query targeting the core entity.
    # Google News will automatically float high-gossip tabloid items (like Daily Mail) to the top.
    params = {
        "q": "Royal Family",
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en"
    }

    feed_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # Standard desktop user agent signature to clear anti-bot challenges
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/xml, text/xml, */*"
    }

    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        if not feed.entries:
            return [{"source": "Scraper Engine", "error": "Firewall cleared, but feed returned no current items."}]

        for entry in feed.entries[:limit_per_source]:
            raw_title = entry.get("title", "No Title")

            # Clean up source formatting tag appended by Google News
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

# --- Streamlit UI Layout Layout ---
st.set_page_config(page_title="Royal Gossip Tracker", page_icon="👑", layout="centered")

st.title("👑 Royal Family Gossip Tracker")
st.write("Aggregating live dispatches from Google News, Daily Mail, and tabloid publishers.")

# Cache the data feed state across app cycles
if "news" not in st.session_state:
    st.session_state.news = fetch_royal_news()

if st.button("Refresh Gossip Feed"):
    st.session_state.news = fetch_royal_news()
    st.rerun()

# Render content boxes on dashboard
for item in st.session_state.news:
    if "error" in item:
        st.error(f"Error ({item['source']}): {item['error']}")
    else:
        with st.container(border=True):
            st.subheader(item["title"])
            # Visual highlights if the content explicitly originates from Daily Mail
            if "daily mail" in item["source"].lower():
                st.markdown(f"🚨 **Source: {item['source']}** | *Published: {item['published']}*")
            else:
                st.caption(f"Source: {item['source']} | Published: {item['published']}")
            st.markdown(f"[Read full story]({item['link']})")
