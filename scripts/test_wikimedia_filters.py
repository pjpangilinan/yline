import ssl
import certifi
import urllib.request
import urllib.parse
import json

context = ssl.create_default_context(cafile=certifi.where())

def search_wikimedia(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=15&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "YlineBot/1.0 (contact@yline.local)"})
    with urllib.request.urlopen(req, context=context, timeout=8) as r:
        data = json.loads(r.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        items = []
        for k, v in pages.items():
            infos = v.get("imageinfo", [])
            if not infos:
                continue
            info = infos[0]
            if info.get("mime") not in ["image/jpeg", "image/png"]:
                continue
            title = v.get("title", "").lower()
            if any(bad in title for bad in ["flag of", "coat of arms", "icon", "symbol", "map", "diagram", "chart", "logo"]):
                continue
            w = info.get("width", 0)
            h = info.get("height", 0)
            if w < 500 or h < 400:
                continue
            items.append({
                "title": v.get("title"),
                "url": info.get("url"),
                "width": w,
                "height": h
            })
        return items

if __name__ == "__main__":
    queries = [
        "candlelight",
        "autumn leaves",
        "holding hands",
        "broken glass",
        "empty street night",
        "hospital corridor",
        "pocket watch",
        "rainy window",
        "sunset horizon",
        "coffee cup book"
    ]

    for q in queries:
        res = search_wikimedia(q)
        print(f"'{q}': {len(res)} quality photos")
        if res:
            print(f"   -> {res[0]['title']} ({res[0]['width']}x{res[0]['height']})")
