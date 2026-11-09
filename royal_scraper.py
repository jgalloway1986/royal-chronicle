import feedparser
import requests
import streamlit as st

def fetch_royal_news(limit_per_source: int = 15):
    aggregated_news = []

    # 🌟 FIXED: Reverting to the specialized /rss/search endpoint but using
    # explicit '+' spacers and a flexible 7d lookback window to bypass regional geofence blocks.
    feed_url = "https://google.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        # Hard Fallback: If the gossip query returns blank elements, immediately drop
        # to a broad 'Royal Family' search so the interface never triggers an empty string error.
        if not feed.entries:
            fallback_url = "https://google.com"
            response = requests.get(fallback_url, headers=headers, timeout=15)
            feed = feedparser.parse(response.text)

        if not feed.entries:
            return [{"source": "Scraper Engine", "error": "Both primary and fallback Google News RSS queries returned empty sets."}]

        for entry in feed.entries[:limit_per_source]:
            raw_title = entry.get("title", "No Title")

            # Clean up the publisher source tag appended to the end of the title
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

# --- Streamlit UI Layout ---
st.set_page_config(page_title="Royal Gossip Tracker", page_icon="👑", layout="centered")

st.title("👑 Royal Family Gossip Tracker")
st.write("Aggregating live dispatches from Google News feeds and major tabloid publishers.")

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
            if "daily mail" in item["source"].lower():
                st.markdown(f"🚨 **Source: {item['source']}** | *Published: {item['published']}*")
            else:
                st.caption(f"Source: {item['source']} | Published: {item['published']}")
            st.markdown(f"[Read full story]({item['link']})")
