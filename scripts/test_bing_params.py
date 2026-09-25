import urllib.request
import urllib.parse
import re
import json
import html

def test_query(q):
    # Add setlang=en-US and cc=US and qft=+filterui:imagesize-large
    params = urllib.parse.urlencode({
        "q": q,
        "form": "HDRSC2",
        "first": "1",
        "setlang": "en-US",
        "cc": "US",
    })
    url = f"https://www.bing.com/images/search?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "SRCHHPGUSR=ADLT=DEMOTE&NRSLT=50",
        }
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        content = response.read().decode("utf-8", errors="ignore")
    
    matches = re.findall(r'm="(\{[^"]+\})"', content)
    results = []
    for m in matches:
        try:
            data = json.loads(html.unescape(m))
            results.append({
                "murl": data.get("murl"),
                "title": data.get("t", ""),
            })
        except Exception:
            pass
    return len(results), results[:3]

if __name__ == "__main__":
    queries = [
        "candlelight",
        "autumn leaves",
        "holding hands sunset",
        "walking home sunset",
        "vintage bicycle road",
    ]
    for q in queries:
        count, top = test_query(q)
        print(f"'{q}': {count} results")
        for item in top:
            print(f"   -> {item['title'][:60]} | {item['murl'][:60]}")
