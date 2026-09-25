import urllib.request
import urllib.parse
import re
import json
import html

def test_query(q):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(q)}&form=HDRSC2&first=1"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
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
    return len(results), results[:2]

if __name__ == "__main__":
    tests = [
        # Original verbose 5-word queries
        "scattered gold coins dark floor",
        "cracked spine fragile structure",
        "soft candlelight calming atmosphere",
        # Concise natural 2-3 word queries
        "gold coins",
        "cracked spine",
        "candlelight",
        "autumn leaves",
        "walking home sunset",
        "broken glass",
        "holding hands"
    ]
    for t in tests:
        count, top = test_query(t)
        print(f"'{t}': {count} results")
        for item in top:
            print(f"   -> {item['title']} ({item['murl'][:60]})")
