import feedparser
import requests
import urllib.parse

def fetch_royal_news(limit_per_source: int = 5):
    aggregated_news = []
    
    base_url = "https://news.google.com/rss/search"
    params = {
        "q": "British Royal Family Gossip News",
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
