import re

with open("docs/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Remove the entire yoshi object
# Find yoshi: { ... }, up to rorschach: {
start_idx = js.find('    yoshi: {')
end_idx = js.find('    rorschach: {')

if start_idx != -1 and end_idx != -1:
    js = js[:start_idx] + js[end_idx:]

# Add angel object
new_obj = """    angel: {
        metadata: {"artist": "kate said", "title": "you are an angel", "album": "Unknown", "year": 2024},
        lyrics: `> Fetching...`,
        images: [],
        videoSrc: "assets/videos/angel.mp4"
    },
"""
js = js.replace('    rorschach: {', new_obj + '    rorschach: {')

with open("docs/app.js", "w", encoding="utf-8") as f:
    f.write(js)
