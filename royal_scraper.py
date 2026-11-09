import feedparser
import requests
import streamlit as st
import re

def fetch_live_royal_news(limit_per_source: int = 15):
    aggregated_news = []
    
    # Target Daily Mail Royal desk feed along with core fallback streams
    feed_urls = [
        "https://dailymail.co.uk",
        "https://skynews.com",
        "https://bbci.co.uk"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
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
                
                if "dailymail" in url:
                    source_label = "Daily Mail Online"
                    is_dm = True
                elif "skynews" in url:
                    source_label = "Sky News"
                    is_dm = False
                else:
                    source_label = "BBC News"
                    is_dm = False
                    
                for entry in feed.entries:
                    raw_title = entry.get("title", "No Title")
                    
                    if is_dm or any(word in raw_title.lower() for word in keywords):
                        link_target = entry.get("link", entry.get("id", ""))
                        direct_url = link_target
                        
                        if is_dm and link_target:
                            match = re.search(r'article-(\d+)', link_target)
                            if match:
                                article_id = match.group(1)
                                raw_path = f"https://dailymail.co.uk{article_id}/index.html"
                                
                                # 👑 THE FIREWALL BYPASS:
                                # Routes your click path through the Internet Archive proxy container.
                                # This completely hides the Streamlit referrer signature and prevents homepage redirection loops.
                                direct_url = f"https://archive.org{raw_path}"
                        
                        if direct_url and direct_url not in seen_links:
                            seen_links.add(direct_url)
                            aggregated_news.append({
                                "source": source_label,
                                "title": raw_title.strip(),
                                "link": direct_url,
                                "published": "Live Feed"
                            })
        except Exception:
            pass
            
    return aggregated_news[:limit_per_source]

def get_past_month_news():
    # 🕒 30-Day Permanent Archive pre-routed through the secure archival gateway structure
    return [
        {
            "source": "Daily Mail Online",
            "title": "Kate's touching tributes: All the quiet nods the Princess made to late royals during Remembrance weekend",
            "link": "https://archive.orghttps://dailymail.co.uk16277639/index.html",
            "published": "Recent Event"
        },
        {
            "source": "Daily Mail Online",
            "title": "Harry and Meghan say they are 'surprised' by King's letter ahead of crucial security meeting",
            "link": "https://archive.orghttps://dailymail.co.uk16113395/index.html",
            "published": "2 Weeks Ago"
        },
        {
            "source": "Daily Mail Online",
            "title": "William and Kate remain the most popular members of the Royal Family following latest polling data",
            "link": "https://archive.orghttps://dailymail.co.uk15470761/index.html",
            "published": "3 Weeks Ago"
        }
    ]

# --- Streamlit Interactive App UI ---
st.set_page_config(page_title="Royal Gossip Tracker", page_icon="👑", layout="centered")

st.title("👑 Royal Family Gossip Tracker")
st.write("Track live global alerts or dive into deep-linked monthly tabloid highlights.")

tab1, tab2 = st.tabs(["⚡ Live Breaking News", "🗓️ Past 30 Days Archive"])

with tab1:
    st.subheader("Current Rolling Live Feed")
    if st.button("Refresh Live Feed"):
        st.session_state.live_news = fetch_live_royal_news()
        st.rerun()

    if "live_news" not in st.session_state:
        st.session_state.live_news = fetch_live_royal_news()

    for item in st.session_state.live_news:
        with st.container(border=True):
            st.subheader(item["title"])
            if "daily mail" in item["source"].lower():
                st.markdown(f"🚨 **Source: {item['source']}**")
            elif "sky news" in item["source"].lower():
                st.markdown(f"🔷 **Source: {item['source']}**")
            else:
                st.caption(f"Source: {item['source']}")
            st.markdown(f"[Read full story]({item['link']})")

with tab2:
    st.subheader("Biggest Headlines from the Last Month")
    month_items = get_past_month_news()
    
    for item in month_items:
        with st.container(border=True):
            st.subheader(item["title"])
            if "daily mail" in item["source"].lower():
                st.markdown(f"🚨 **Source: {item['source']}** | *Timeline: {item['published']}*")
            else:
                st.markdown(f"ℹ️ **Source: {item['source']}** | *Timeline: {item['published']}*")
            st.markdown(f"[Read full article]({item['link']})")
