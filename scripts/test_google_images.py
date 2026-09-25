import urllib.request
import urllib.parse
import re

def test_google_images(q):
    url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(q)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req) as r:
        html = r.read().decode("utf-8", errors="ignore")
    
    urls = re.findall(r'\["(https://[^"]+)",\d+,\d+\]', html)
    valid = [
        u for u in urls
        if any(ext in u.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"])
        and not any(bad in u.lower() for bad in ["gstatic.com", "google.com"])
    ]
    print(f"Google images for '{q}': found {len(valid)} images")
    for u in valid[:3]:
        print("  ", u[:80])

if __name__ == "__main__":
    test_google_images("candlelight")
    test_google_images("autumn leaves")
    test_google_images("holding hands")
    test_google_images("broken glass")
