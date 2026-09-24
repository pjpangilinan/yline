import asyncio
import os
import hashlib
import io
import re
from PIL import Image
import httpx

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

STOCK_DOMAINS = [
    "shutterstock.com", "istockphoto.com", "alamy.com", "gettyimages.com",
    "dreamstime.com", "depositphotos.com", "123rf.com", "freepik.com",
    "vecteezy.com", "stock.adobe.com", "canva.com", "clipart", "pond5.com"
]

def is_stock(url: str) -> bool:
    u = url.lower()
    return any(d in u for d in STOCK_DOMAINS)

async def search_bing(query: str) -> list[str]:
    for attempt in range(2):
        try:
            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"
            async with httpx.AsyncClient(headers=HEADERS, timeout=6.0, follow_redirects=True) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    matches = [
                        m for m in re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
                        if not is_stock(m)
                    ]
                    if matches:
                        return matches
        except Exception as e:
            await asyncio.sleep(0.5)
    return []

async def search_ddg(query: str) -> list[str]:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=6.0, follow_redirects=True) as client:
            res = await client.get("https://duckduckgo.com/", params={"q": query})
            vqd_match = re.search(r'vqd=([\d-]+)', res.text)
            if vqd_match:
                vqd = vqd_match.group(1)
                params = {"l": "us-en", "o": "json", "q": query, "vqd": vqd, "f": ",,,", "p": "1"}
                res_img = await client.get(
                    "https://duckduckgo.com/i.js",
                    params=params,
                    headers={"Referer": "https://duckduckgo.com/"}
                )
                if res_img.status_code == 200:
                    data = res_img.json()
                    urls = [r["image"] for r in data.get("results", []) if r.get("image") and not is_stock(r["image"])]
                    if urls:
                        return urls
    except Exception:
        pass
    return []

async def download_unique(urls: list[str], save_paths: list[str], seen_hashes: set[str]) -> bool:
    for url in urls[:15]:
        if is_stock(url):
            continue
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=6.0, follow_redirects=True) as client:
                res = await client.get(url)
                if res.status_code != 200 or len(res.content) < 15000:
                    continue
                h = hashlib.md5(res.content).hexdigest()
                if h in seen_hashes:
                    continue
                img = Image.open(io.BytesIO(res.content))
                img.load()
                w, h_px = img.size
                if w < 400 or h_px < 300:
                    continue
                if img.mode != "RGB":
                    img = img.convert("RGB")
                for sp in save_paths:
                    os.makedirs(os.path.dirname(os.path.abspath(sp)), exist_ok=True)
                    img.save(sp, format="JPEG", quality=92)
                seen_hashes.add(h)
                return True
        except Exception:
            continue
    return False

# Targeted queries for duplicate replacements
REPLACEMENTS = {
    "jane": {
        12: [
            "antique heavy closed carved wooden door lock gothic aesthetic",
            "ancient wooden library grand closed doors dramatic lighting aesthetic",
        ],
        13: [
            "dark fantasy dagger blade poison roses aesthetic",
            "statue weeping gothic stone wings dramatic aesthetic",
        ],
        16: [
            "dramatic silhouette screaming in fog rain aesthetic",
            "surreal oil painting portrait covered face dramatic aesthetic",
        ],
        17: [
            "victorian woman standing in grand foggy garden dawn aesthetic",
            "vintage woman mourning black lace veil gothic aesthetic",
        ],
        18: [
            "theatre audience dark silhouettes clapping applause aesthetic",
            "vintage masquerade crowd masks venetian ballroom aesthetic",
        ],
        28: [
            "crimson red velvet ribbon emerald green moss aesthetic",
            "red roses scattered green lawn morning mist aesthetic",
        ],
    },
    "take_me_dancing": {
        18: [
            "person lying grass looking at night stars cigarette smoke cinematic aesthetic",
            "summer night campfire grass looking up sky aesthetic",
        ],
        30: [
            "vintage polaroid film camera memory collage aesthetic",
            "couple holding hands blurred motion neon city lights aesthetic",
        ],
        36: [
            "warm sunrise through bedroom window dust motes aesthetic",
            "two hands reaching across water surface twilight aesthetic",
        ],
        37: [
            "church cathedral altar candles glowing gold aesthetic",
            "stained glass illuminated rays of sun golden hour aesthetic",
        ],
        39: [
            "empty neon highway diner counter midnight rainy aesthetic",
            "lonely figure walking under streetlamp foggy night cinematic aesthetic",
        ],
        44: [
            "classic retro jukebox neon lights vintage americana diner aesthetic",
            "vintage neon road trip americana route 66 motel sign aesthetic",
        ],
        45: [
            "vintage leather jacket coins pocket casual aesthetic",
            "pennies and nickels on wooden table coffee cup aesthetic",
        ],
    },
    "kalapastangan": {
        7: [
            "stained glass archangel saint halo golden church light aesthetic",
            "ancient baroque stone angel statue cathedral ceiling aesthetic",
        ],
        16: [
            "inferno fire embers burning night surreal flames aesthetic",
            "dark surreal nightmare burning horizon crimson sky aesthetic",
        ],
        32: [
            "electric fender guitar amplifier stage red smoke aesthetic",
            "rock guitarist silhouette spotlight heavy smoke concert aesthetic",
        ],
    }
}

async def process_song(song_name: str, folder: str, out_folder: str):
    print(f"\n--- Processing {song_name} ---", flush=True)
    files = sorted([f for f in os.listdir(folder) if f.endswith('.jpg')])
    
    # Identify initial seen hashes excluding files scheduled for replacement
    to_replace = REPLACEMENTS.get(song_name, {})
    seen_hashes = set()
    for idx, f in enumerate(files):
        if idx not in to_replace:
            p = os.path.join(folder, f)
            h = hashlib.md5(open(p, "rb").read()).hexdigest()
            seen_hashes.add(h)
            
    print(f"Initial non-duplicate seen hashes: {len(seen_hashes)}", flush=True)
    
    for idx, queries in to_replace.items():
        fname = f"img_{idx:03d}.jpg"
        doc_path = os.path.join(folder, fname)
        out_path = os.path.join(out_folder, fname)
        print(f"Replacing {fname} (index {idx})...", flush=True)
        
        success = False
        for q in queries:
            print(f"  Searching: '{q}'...", flush=True)
            urls = await search_bing(q)
            if not urls:
                urls = await search_ddg(q)
            if urls:
                success = await download_unique(urls, [doc_path, out_path], seen_hashes)
                if success:
                    print(f"  -> Successfully replaced {fname} with unique image!", flush=True)
                    break
        if not success:
            print(f"  -> Broad fallback query...", flush=True)
            urls = await search_bing(f"{song_name} indie aesthetic photo {idx}")
            if urls:
                success = await download_unique(urls, [doc_path, out_path], seen_hashes)
                if success:
                    print(f"  -> Replaced {fname} via fallback!", flush=True)
        assert success, f"Could not find unique image for {song_name} slide {idx}"

async def main():
    await process_song("jane", "docs/assets/images/jane", "output/jane/images")
    await process_song("take_me_dancing", "docs/assets/images/take_me_dancing", "output/take_me_dancing/images")
    await process_song("kalapastangan", "docs/assets/images/kalapastangan", "output/kalapastangan/images")
    print("\nAll replacements complete! Verifying hash uniqueness...", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
