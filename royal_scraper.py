import feedparser
import requests
import streamlit as st

def fetch_royal_news(limit_per_source: int = 10):
    aggregated_news = []

    # 💡 SWITCHED: Using the primary, highly-whitelisted Google News Top Stories feed
    # to completely bypass server-side cloud infrastructure firewall blocks.
    feed_url = "https://google.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        if not feed.entries:
            return [{"source": "Scraper Engine", "error": "Google News endpoint did not return any entries to process."}]

        # Defining target gossip and royal family match terms
        keywords = ["royal", "monarchy", "king", "queen", "prince", "princess", "harry", "meghan", "william", "kate", "charles", "gossip", "palace"]

        for entry in feed.entries:
            raw_title = entry.get("title", "No Title")

            # Match any entries containing our core keyword patterns
            if any(word in raw_title.lower() for word in keywords):
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

                # Halt collection once our threshold limit is hit
                if len(aggregated_news) >= limit_per_source:
                    break

        # Bulletproof Fallback: If no custom gossip hits match today's top trends,
        # pull the top global headlines anyway so your app layout never displays empty.
        if not aggregated_news:
            for entry in feed.entries[:limit_per_source]:
                raw_title = entry.get("title", "No Title")
                if " - " in raw_title:
                    clean_title, source_name = raw_title.rsplit(" - ", 1)
                else:
                    clean_title = raw_title
                    source_name = "News Aggregate"
                aggregated_news.append({
                    "source": source_name.strip(),
                    "title": f"🔥 [Trending] {clean_title.strip()}",
                    "link": entry.get("link", "#"),
                    "published": entry.get("published", "Unknown Date")
                })

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
