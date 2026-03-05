import feedparser
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def gather_filings():
    # SEC Atom feed for Form D
    feed_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D&owner=include&output=atom"
    feed = feedparser.parse(feed_url, request_headers={'User-Agent': 'Company Name yourname@example.com'})

    for entry in feed.entries:
        # Accession number is usually in the ID or Link
        acc_no = entry.id.split('=')[-1]
        
        # SETNX returns 1 if added (new), 0 if it already exists
        if r.setnx(f"seen:{acc_no}", 1):
            r.expire(f"seen:{acc_no}", 172800) # Keep for 48 hours
            r.rpush("daily_queue", entry.link) # Add XML link to processing queue
            print(f"Added new filing: {acc_no}")

if __name__ == "__main__":
    gather_filings()
