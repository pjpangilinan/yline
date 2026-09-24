# YLine Project Handoff & Technical Post-Mortem

**Date:** September 23, 2026  
**Status:** Stopped upon user request. Pipeline reviewed, root causes identified, and documented for handoff.

---

## Executive Summary

Over successive iterations, the YLine video generation pipeline suffered from two persistent regressions:
1. **Timing Desynchronization:** Lyric captions and slide transitions fell visibly out of sync with the audio track across *Jane!*, *Take Me Dancing*, and *Kalapastangan*.
2. **Visual Mismatch & Image Repetition:** Images appeared generic/stock-like, failed to match the poetic nuance of the lyrics, and in several cases **repeated the exact same image file across multiple distinct lyric lines** (up to 5 duplicate slides in a single song).

This document details the exact root causes discovered via deep inspection of the audio waveforms, Whisper alignments, subtitle event timings, image hashes, and FFmpeg assembly pipelines.

---

## 1. Root Cause Analysis: Why Timing Degraded & Kept Breaking

### A. The Concat Demuxer Frame-Drop Catastrophe
- **What happened:** In earlier attempts to avoid FFmpeg multi-input filter buffer deadlocks on long songs, the pipeline switched to FFmpeg's `-f concat` demuxer (`concat.txt` specifying image paths and durations).
- **The flaw:** When piping variable-duration static image slides through `-f concat` into an `fps=24` filter without CFR timestamp synthesis on Windows, FFmpeg drops frames heavily:
  - *Take Me Dancing*: Dropped **1,575 frames** (rendered 3,001 frames / 125s instead of 4,576 frames / 190.7s), resulting in a 65-second desync.
  - *Kalapastangan*: Dropped **3,038 frames** (rendered 3,588 frames / 149s instead of 6,626 frames / 276.1s), cutting off more than two minutes of the track.
- **The fix applied (Split-CFR):** Splitting the slideshow into two 16–26 slide batches rendered via native `filter_complex` (`concat=n=...:v=1:a=0`) at constant 24fps, then losslessly concatenating the batches. This guarantees exact frame counts (e.g. 4,576 frames = 190.667s).

### B. Instrumental Breaks & Frozen Subtitles
- In standard LRCLIB timestamps, an instrumental pause between two vocal lines has no end timestamp; the previous lyric line's duration is simply extended until the start of the *next* vocal line:
  - **Jane! Line 4** (*"Leaving her breathless, leading her hand to the grave"*): Vocal singing ends at **0:29.5s**. However, the next vocal line (*"And Jane, you're early"*) does not start until **0:41.87s**. Because the subtitle event was set to span `0:00:25.87 -> 0:00:41.87`, the subtitle sat frozen in the center of the screen during 12.3 seconds of pure instrumental guitar, making the video appear stalled or desynced.
- **Kalapastangan**: LRCLIB contains **9 separate empty-string entries** for instrumental interludes (e.g. `[00:14.99]`, `[00:26.97]`, `[00:49.11]`, `[01:12.96]`, `[01:48.41]`, `[03:45.63]`). When scripts attempted to parse these:
  - Filtering empty lines caused an **index mismatch** between images (`img_000` to `img_032`) and lyrics.
  - Not filtering empty lines caused blank subtitle dialogue boxes to render during instrumental solos, with slides changing during silence.

### C. LRCLIB Vocal Onset Lags vs. Studio Waveforms
- Community-submitted LRCLIB timestamps are often timed to the *downbeat* rather than the true acoustic vocal onset:
  - **Kalapastangan Line 4** (*"Sino ba ako para mapansin Mo?"*): LRCLIB timestamp is `0:29.07`. Audio waveform analysis and Whisper alignment show vocal onset occurs at **0:31.50** (+2.43s lag).
  - **Kalapastangan Line 5** (*"Mga dalangin ko sa 'Yo, sana'y pakinggan Mo"*): LRCLIB timestamp is `0:40.98`. Vocal onset occurs at **0:42.50** (+1.52s lag).
  - **Take Me Dancing Line 0** (*"Here's to Julian..."*): Audio track has a 1,740ms solo acoustic guitar intro before the first syllable.
  - **Jane! Line 8–9** (*"They saw you dressing in the backroom"*): Singing begins at **0:54.00s**, whereas LRCLIB placed it at **0:56.66s**.

---

## 2. Root Cause Analysis: Why Images Looked Like Stock & Repeated

### A. The Image Duplication Bug (Forensic Hash Verification)
Running an MD5 cryptographic audit across the downloaded assets revealed widespread duplication:

| Song | Total Images | Unique Images | Duplicate Count | Duplicate Hash Details |
| :--- | :--- | :--- | :--- | :--- |
| **Take Me Dancing** | 51 | 44 | **7 duplicates** | Hash `b207b14f` is repeated across **5 slides**: `img_012.jpg`, `img_030.jpg`, `img_036.jpg`, `img_044.jpg`, `img_045.jpg`<br>Hash `b765261a` repeated across **3 slides**: `img_017.jpg`, `img_018.jpg`, `img_037.jpg`<br>Hash `782fa718` repeated across **2 slides**: `img_026.jpg`, `img_039.jpg` |
| **Jane!** | 29 | 23 | **6 duplicates** | Hash `97f375d5` repeated across **3 slides**: `img_004.jpg`, `img_013.jpg`, `img_016.jpg`<br>Hash `939c0af5` repeated across **3 slides**: `img_006.jpg`, `img_012.jpg`, `img_018.jpg`<br>Hash `0b8dd3e4` repeated across **2 slides**: `img_005.jpg`, `img_017.jpg`<br>Hash `a892185e` repeated across **2 slides**: `img_010.jpg`, `img_028.jpg` |
| **Kalapastangan** | 33 | 30 | **3 duplicates** | Hash `37af8314` repeated across **3 slides**: `img_010.jpg`, `img_016.jpg`, `img_032.jpg`<br>Hash `3c8ab317` repeated across **2 slides**: `img_001.jpg`, `img_007.jpg` |

**Why did this happen?**
1. **Search Engine Rank Collapsing**: When querying Bing or DuckDuckGo for thematically related prompts (e.g. *"indie music video night lights"*, *"retro motel sign"*, *"party disco floor"*), search engines return the exact same high-authority image within the top 5 results.
2. **No Per-Song Hash Tracking**: The download loop checked only URL status and file dimensions (`>= 400x300`), but never tracked an image MD5 or perceptual hash against already-downloaded slides in the same song. If candidate 1 failed on slide 30 and candidate 2 succeeded, but candidate 2 was identical to slide 12, it was accepted without warning.

### B. Why Imagery Felt Like "Random Stock Slides"
1. **Literal Lyric Fallacy**:
   - The initial LLM prompt system mandated using literal lyric phrases.
   - For *"It's only small change, red on the green green grass"*, search engines returned literal photos of copper pennies on freshly mowed lawn turf.
   - For *"bottle bank (broken glass)"*, search engines returned municipal recycling dumpster containers.
2. **Aggregator Stock Leaks**:
   - Although commercial stock domains (Shutterstock, Getty, Alamy, iStock) were blacklisted, free wallpaper and stock aggregator networks (Pexels, Unsplash, WallpaperFlare, Pinterest reposts) still returned sterile, clinical stock portraits (models posing awkwardly in studios) rather than cinematic stills.

---

## 3. Codebase Architecture & Degradation Analysis

1. **Fragmentation into 140+ Ad-Hoc Scripts**:
   - The repository root currently contains over 140 transient test and fix scripts (`fix_*.py`, `render_*_concat.py`, `render_*_perfect.py`, `check_*.py`, `bust_cache*.py`).
   - Many of these scripts introduced contradictory logic (e.g., one script assumes empty LRCLIB lines should be stripped, while another assumes they must be preserved to match an image folder count).
2. **Bypassing the Core Agent Graph**:
   - The core architecture in `src/yline/` (LangGraph state, agents, and tool abstractions) was progressively bypassed in favor of direct procedural scripts to patch individual songs, leading to divergence between the CLI pipeline and the showcase output.
3. **Browser Cache Desynchronization**:
   - Video elements in modern browsers (`<video src="...">`) aggressively cache partial byte ranges. When a video was re-rendered with identical filenames, users frequently continued to view the cached, buggy video unless aggressive cache-busting query params (`?v=N`) were synchronized across both `index.html` and `app.js`.

---

## 4. Current State of the Showcase

- **Web Server:** Running as a background daemon (`uv run python -m RangeHTTPServer 8000 -b 0.0.0.0`) serving `docs/` at `http://localhost:8000/`.
- **Showcase Status:**
  - `Color Your Night` (Lotus Juice) — **Pristine reference** (untouched).
  - `London Beckoned...` (Panic! at the Disco) — **Pristine reference** (untouched).
  - `Jane!` (The Long Faces) — Rendered @ 24fps CFR; 7 mismatched slides replaced, but contains 4 duplicate image hashes and 12-second instrumental subtitle hang.
  - `Take Me Dancing` (Will Joseph Cook) — Rendered @ 24fps CFR via split-assembly; contains 7 duplicate image hashes across 51 slides.
  - `Kalapastangan` (fitterkarma) — Rendered @ 24fps CFR; contains index offset issues caused by empty instrumental LRCLIB lines and 2 duplicate image hashes.

---

## 5. Clean Handoff Blueprint (Step-by-Step Next Actions)

For the next developer or agent taking over this codebase, follow this strict protocol to resolve all outstanding issues:

### Step 1: Implement Per-Song Hash Deduplication in `src/yline/tools/images.py`
Add an in-memory `seen_hashes: set[str]` for each song generation session:
```python
def download_image_unique(urls: list[str], save_path: str, seen_hashes: set[str]) -> bool:
    for url in urls:
        if is_stock_url(url):
            continue
        try:
            content = fetch_bytes(url)
            img_hash = hashlib.md5(content).hexdigest()
            if img_hash in seen_hashes:
                continue  # Skip duplicate image even if from different URL
            # Validate dimensions and save
            seen_hashes.add(img_hash)
            return True
        except Exception:
            continue
    return False
```

### Step 2: Fix Instrumental Subtitle Padding
In subtitle generation (`render_*.py`), do **not** extend dialogue display times across instrumental sections:
- If `lines[i+1]["start_ms"] - lines[i]["end_ms"] > 3000ms`, cap dialogue display at `lines[i]["start_ms"] + vocal_duration` (or max 4.0s).
- During instrumental breaks, display a subtle indicator (e.g. `[Instrumental]` or clear the dialogue box completely).

### Step 3: Unify LRCLIB Parsing & Empty Line Handling
Standardize the lyric model across all songs:
1. Parse LRCLIB lines.
2. Filter out all empty text lines (`l["text"].strip()`).
3. For each non-empty lyric line, pair exactly **one** unique, deduplicated image.
4. If an instrumental break exceeds 5 seconds, insert an explicit `[Instrumental Solo]` line with its own dedicated cinematic atmospheric visual, or keep the preceding visual without subtitles.

### Step 4: Archive Root Scratch Scripts
Move the ~140 `fix_*.py` and `test_*.py` scripts into an `archive/` or `scratch/` directory to prevent accidental execution of outdated rendering routines.
