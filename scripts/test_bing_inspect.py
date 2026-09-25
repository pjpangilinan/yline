import urllib.request
import re
import json
import html

def test_bing(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC2&first=1"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        content = response.read().decode("utf-8", errors="ignore")
    
    # Extract metadata items (murl, title/t, desc)
    matches = re.findall(r'm="(\{[^"]+\})"', content)
    results = []
    for m in matches:
        try:
            data = json.loads(html.unescape(m))
            results.append({
                "murl": data.get("murl"),
                "title": data.get("t", ""),
                "desc": data.get("desc", ""),
            })
        except Exception:
            pass
    return results

if __name__ == "__main__":
    queries = [
        "scattered gold coins dark floor",
        "cracked spine fragile structure",
        "soft candlelight calming atmosphere",
        "fading summer sunset horizon",
        "autumn withering leaves decay"
    ]
    for q in queries:
        res = test_bing(q)
        print(f"Query: '{q}' -> Found {len(res)} results with metadata")
        for r in res[:3]:
            print(f"   Title: {r['title']}")
            print(f"   URL: {r['murl'][:80]}")
