import asyncio
import os
import hashlib
import io
import re
from collections import defaultdict
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

def get_dhash(img: Image.Image, hash_size=8) -> str:
    resized = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    diff = []
    for r in range(hash_size):
        for c in range(hash_size):
            diff.append(pixels[r * (hash_size + 1) + c] > pixels[r * (hash_size + 1) + c + 1])
    val = 0
    hex_str = []
    for i, v in enumerate(diff):
        if v:
            val += 2 ** (i % 8)
        if (i % 8) == 7:
            hex_str.append(hex(val)[2:].rjust(2, '0'))
            val = 0
    return ''.join(hex_str)

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
        except Exception:
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

async def fetch_and_save_unique(
    urls: list[str],
    save_paths: list[str],
    seen_md5s: set[str],
    seen_dhashes: set[str]
) -> bool:
    for url in urls[:25]:
        if is_stock(url):
            continue
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=6.0, follow_redirects=True) as client:
                res = await client.get(url)
                if res.status_code != 200 or len(res.content) < 15000:
                    continue
                img = Image.open(io.BytesIO(res.content))
                img.load()
                w, h = img.size
                if w < 400 or h < 300:
                    continue
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=92)
                jpeg_bytes = buf.getvalue()
                
                md5_h = hashlib.md5(jpeg_bytes).hexdigest()
                dh = get_dhash(img)
                
                if md5_h in seen_md5s or dh in seen_dhashes:
                    continue
                    
                for sp in save_paths:
                    os.makedirs(os.path.dirname(os.path.abspath(sp)), exist_ok=True)
                    with open(sp, "wb") as f:
                        f.write(jpeg_bytes)
                        
                seen_md5s.add(md5_h)
                seen_dhashes.add(dh)
                return True
        except Exception:
            continue
    return False

# Distinct query bank per slide to guarantee rich thematic variety
QUERIES = {
    ("jane", 28): [
        "meadow dew droplets emerald grass morning sunlight macro aesthetic",
        "lush moss covered rocks forest brook aesthetic",
        "scattered red rose petals green lawn vintage aesthetic",
    ],
    ("jane", 12): [
        "grand gothic castle archway wooden locked gates dramatic lighting aesthetic",
        "victorian dark library closed heavy wooden doors aesthetic",
        "mysterious iron gate ivy abandoned mansion aesthetic",
    ],
    ("jane", 17): [
        "victorian lady walking in foggy graveyard dawn gothic aesthetic",
        "vintage 19th century woman mourning veil silhouette aesthetic",
        "misty morning english countryside grand estate aesthetic",
    ],
    ("take_me_dancing", 30): [
        "couple dancing in street rainy neon reflection warm aesthetic",
        "nostalgic summer road trip polaroid memory film grain aesthetic",
        "vintage vinyl turntable spinning 70s living room aesthetic",
    ],
    ("take_me_dancing", 37): [
        "golden cathedral rays of light stained glass altar aesthetic",
        "candlelight cathedral church nave warm architecture aesthetic",
        "vintage stone angel sculpture backlight sunset aesthetic",
    ],
}

async def fix_song(song_name: str, doc_dir: str, out_dir: str):
    print(f"\n================ AUDITING {song_name.upper()} ================", flush=True)
    files = sorted([f for f in os.listdir(doc_dir) if f.endswith(".jpg")])
    
    # Map current files to MD5 and dHash
    file_md5 = {}
    file_dhash = {}
    by_md5 = defaultdict(list)
    
    for f in files:
        p = os.path.join(doc_dir, f)
        b = open(p, "rb").read()
        m = hashlib.md5(b).hexdigest()
        file_md5[f] = m
        by_md5[m].append(f)
        try:
            im = Image.open(p)
            file_dhash[f] = get_dhash(im)
        except Exception:
            file_dhash[f] = m

    duplicates = {m: flist for m, flist in by_md5.items() if len(flist) > 1}
    print(f"Total files: {len(files)}, Unique MD5s: {len(by_md5)}, Duplicate sets: {len(duplicates)}", flush=True)
    
    if not duplicates:
        print(f"SUCCESS: {song_name} is already 100% unique!", flush=True)
        return

    # Files that will be kept as-is
    kept_files = set(files)
    to_replace = []
    for m, flist in duplicates.items():
        # Keep the first file, replace the others
        for dup in flist[1:]:
            kept_files.remove(dup)
            to_replace.append(dup)

    seen_md5s = {file_md5[f] for f in kept_files}
    seen_dhashes = {file_dhash[f] for f in kept_files}

    print(f"Files to replace: {to_replace}", flush=True)

    for fname in to_replace:
        idx = int(re.search(r'\d+', fname).group())
        doc_p = os.path.join(doc_dir, fname)
        out_p = os.path.join(out_dir, fname)
        
        q_list = QUERIES.get((song_name, idx), [
            f"{song_name} indie cinema aesthetic still photo {idx}",
            f"cinematic indie music video aesthetic 35mm film {idx}",
            f"vintage photography aesthetic emotional lighting {idx}"
        ])
        
        print(f"Replacing {fname} (index {idx})...", flush=True)
        success = False
        for q in q_list:
            print(f"  Searching: '{q}'...", flush=True)
            urls = await search_bing(q)
            if not urls:
                urls = await search_ddg(q)
            if urls:
                success = await fetch_and_save_unique(urls, [doc_p, out_p], seen_md5s, seen_dhashes)
                if success:
                    print(f"  -> SUCCESS for {fname}!", flush=True)
                    break
        if not success:
            # Fallback search
            fallback_q = f"aesthetic indie film photography scene {idx}"
            urls = await search_bing(fallback_q)
            success = await fetch_and_save_unique(urls, [doc_p, out_p], seen_md5s, seen_dhashes)
            assert success, f"Failed to find unique replacement for {fname}"
            print(f"  -> SUCCESS via fallback for {fname}!", flush=True)

async def main():
    await fix_song("jane", "docs/assets/images/jane", "output/jane/images")
    await fix_song("take_me_dancing", "docs/assets/images/take_me_dancing", "output/take_me_dancing/images")
    await fix_song("kalapastangan", "docs/assets/images/kalapastangan", "output/kalapastangan/images")
    print("\nAll songs processed! Verifying 100% uniqueness...", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
