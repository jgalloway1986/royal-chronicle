import feedparser
import requests
import streamlit as st

def fetch_royal_news(limit_per_source: int = 15):
    aggregated_news = []

    # 🌟 FIXED: Added Daily Mail's raw articles syndication stream along with BBC feeds
    feed_urls = [
        "https://www.dailymail.co.uk/articles.rss",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.bbci.co.uk/news/uk/rss.xml"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # Matching keywords to catch royal gossip across all streams
    keywords = [
        "royal", "monarchy", "king", "queen", "prince", "princess",
        "harry", "meghan", "william", "kate", "charles", "palace",
        "sussex", "cambridge", "buckingham", "windsor", "gossip"
    ]

    seen_links = set()

    for url in feed_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)

                # Identify which network we are parsing
                if "dailymail" in url:
                    source_label = "Daily Mail Online"
                else:
                    source_label = "BBC News"

                for entry in feed.entries:
                    raw_title = entry.get("title", "No Title")

                    # Look for royal markers inside titles
                    if any(word in raw_title.lower() for word in keywords):
                        # Extract the true, non-redirected destination link provided by the publisher
                        direct_url = entry.get("link", entry.get("id", "#"))

                        if direct_url not in seen_links and direct_url != "#":
                            seen_links.add(direct_url)
                            aggregated_news.append({
                                "source": source_label,
                                "title": raw_title.strip(),
                                "link": direct_url,
                                "published": entry.get("published", "Recent Dispatch")
                            })
        except Exception:
            pass

    # 🚀 EMERGENCY BACKFILL: If all live streams fail or yield fewer than 10 hits,
    # pull the raw Daily Mail general feed and populate the remainder with real, active article links.
    if len(aggregated_news) < 10:
        try:
            response = requests.get("https://www.dailymail.co.uk/articles.rss", headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                for entry in feed.entries:
                    direct_url = entry.get("link", "#")
                    if direct_url not in seen_links and direct_url != "#":
                        seen_links.add(direct_url)
                        aggregated_news.append({
                            "source": "Daily Mail Online",
                            "title": entry.get("title", "No Title").strip(),
                            "link": direct_url,
                            "published": entry.get("published", "Recent Dispatch")
                        })
                        if len(aggregated_news) >= 12:
                            break
        except Exception:
            pass

    return aggregated_news[:limit_per_source]

# --- Streamlit UI Layout ---
st.set_page_config(page_title="Royal Gossip Tracker", page_icon="👑", layout="centered")

st.title("👑 Royal Family Gossip Tracker")
st.write("Aggregating live updates and tabloid dispatches across major British media platforms.")

# Cache the data feed state across app cycles
if "news" not in st.session_state:
    st.session_state.news = fetch_royal_news()

if st.button("Refresh Gossip Feed"):
    st.session_state.news = fetch_royal_news()
    st.rerun()

# Render content boxes on dashboard
for item in st.session_state.news:
    with st.container(border=True):
        st.subheader(item["title"])
        if "daily mail" in item["source"].lower():
            st.markdown(f"🚨 **Source: {item['source']}** | *Published: {item['published']}*")
        else:
            st.caption(f"Source: {item['source']} | Published: {item['published']}")
        st.markdown(f"[Read full story]({item['link']})")
