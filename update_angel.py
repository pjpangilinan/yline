import json
import re

with open("output/kate_said_by_you_are_an_angel_state.json", encoding="utf-8") as f:
    state = json.load(f)

# Format lyrics
lyrics_lines = []
for line in state['lyrics']:
    mm = int(line['start_ms'] / 1000 // 60)
    ss = (line['start_ms'] / 1000) % 60
    lyrics_lines.append(f"[{mm:02d}:{ss:05.2f}] {line['text']}")
lyrics_str = "\n".join(lyrics_lines).replace('`', '\\`')

# Format images
img_strs = []
for img in state["images"]:
    filename = img["path"].replace("\\\\", "/").replace("\\", "/").split("/")[-1]
    prompt = img["search_query"].replace('"', '\\"')
    img_strs.append(f'        {{ src: "assets/images/angel/{filename}", prompt: "{prompt}" }}')
images_str = '[\n' + ',\n'.join(img_strs) + '\n    ]'

with open("docs/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace lyrics and images for angel
idx = js.find('angel: {')

lyrics_idx = js.find('lyrics:', idx)
lyrics_end = js.find('`,', lyrics_idx) + 2

img_idx = js.find('images:', idx)
img_end = js.find('],', img_idx) + 2

# Replace backwards
js = js[:img_idx] + 'images: ' + images_str + ',' + js[img_end:]
js = js[:lyrics_idx] + f'lyrics: `{lyrics_str}`,' + js[lyrics_end:]

# Bust cache on videoSrc
js = js.replace('videoSrc: "assets/videos/angel.mp4"', 'videoSrc: "assets/videos/angel.mp4?v=1"')

with open("docs/app.js", "w", encoding="utf-8") as f:
    f.write(js)
