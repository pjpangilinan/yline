import urllib.request
import urllib.parse
import json
import re
import html

def analyze_overlap(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC2&first=1"
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
    q_words = set(re.findall(r'[a-zA-Z]{3,}', query.lower())) - {"aesthetic", "scene", "view", "photo", "image", "wallpaper"}
    
    scored = []
    for m in matches:
        try:
            d = json.loads(html.unescape(m))
            title = d.get("t", "")
            t_words = set(re.findall(r'[a-zA-Z]{3,}', title.lower()))
            overlap = q_words.intersection(t_words)
            scored.append({
                "overlap": len(overlap),
                "matched_words": list(overlap),
                "title": title,
                "url": d.get("murl")
            })
        except Exception:
            pass
    return q_words, scored

if __name__ == "__main__":
    queries = [
        "autumn leaves path",
        "scattered gold coins dark floor",
        "cracked spine fragile structure",
        "candlelight",
        "holding hands"
    ]
    for q in queries:
        qw, scored = analyze_overlap(q)
        relevant = [s for s in scored if s["overlap"] > 0]
        print(f"\nQuery: '{q}' (Keywords: {qw})")
        print(f"Total results: {len(scored)}, Relevant (overlap > 0): {len(relevant)}")
        for r in relevant[:3]:
            print(f"  [+] Match: {r['matched_words']} | Title: {r['title'][:55]} | {r['url'][:55]}")
        irrelevant = [s for s in scored if s["overlap"] == 0]
        for irr in irrelevant[:2]:
            print(f"  [-] Zero overlap: Title: {irr['title'][:55]} | {irr['url'][:55]}")
