import json
import re

with open("output/rorschach_blots_by_the_ridleys_state.json", encoding="utf-8") as f:
    state = json.load(f)

# Format lyrics
lyrics_lines = []
for line in state['lyrics']:
    mm = int(line['start_ms'] / 1000 // 60)
    ss = (line['start_ms'] / 1000) % 60
    lyrics_lines.append(f"[{mm:02d}:{ss:05.2f}] {line['text']}")
lyrics_str = "\n".join(lyrics_lines).replace('`', '\\`')

with open("docs/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace lyrics for rorschach
idx = js.find('rorschach: {')
lyrics_idx = js.find('lyrics:', idx)
lyrics_end = js.find('`,', lyrics_idx) + 2

js = js[:lyrics_idx] + f'lyrics: `{lyrics_str}`,' + js[lyrics_end:]

# Bust cache on videoSrc
js = js.replace('videoSrc: "assets/videos/rorschach.mp4?v=1"', 'videoSrc: "assets/videos/rorschach.mp4?v=2"')

with open("docs/app.js", "w", encoding="utf-8") as f:
    f.write(js)
