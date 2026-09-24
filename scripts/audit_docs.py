import re
import os

files = ['docs/index.html', 'docs/styles.css', 'docs/app.js']
referenced = set()
for path in files:
    with open(path, encoding='utf-8') as f:
        text = f.read()
    matches = re.findall(r'assets/[a-zA-Z0-9_\-\./]+', text)
    for m in matches:
        clean = m.split('?')[0].split('#')[0].rstrip('"\')')
        referenced.add(clean)

print(f'Referenced assets count: {len(referenced)}')
missing = []
for r in sorted(referenced):
    exists = os.path.exists(os.path.join('docs', r))
    if not exists:
        missing.append(r)

if missing:
    print(f'MISSING ASSETS ({len(missing)}):')
    for m in missing:
        print('  -', m)
else:
    print('All referenced assets exist on disk!')

all_assets = []
for root, dirs, fnames in os.walk('docs/assets'):
    for fname in fnames:
        rel = os.path.relpath(os.path.join(root, fname), 'docs').replace('\\', '/')
        all_assets.append(rel)

unreferenced = [a for a in all_assets if a not in referenced]
print(f'Total files in docs/assets: {len(all_assets)}')
print(f'Unreferenced files in docs/assets: {len(unreferenced)}')

unreferenced_dirs = set(os.path.dirname(a) for a in unreferenced)
print('Directories containing unreferenced files:')
for d in sorted(unreferenced_dirs):
    count = sum(1 for a in unreferenced if os.path.dirname(a) == d)
    size = sum(os.path.getsize(os.path.join('docs', a)) for a in unreferenced if os.path.dirname(a) == d) / (1024*1024)
    print(f'  - {d}: {count} files ({size:.2f} MB)')

print('\nAuditing showcase videos:')
import subprocess
import imageio_ffmpeg
import re

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

vids = ['color.mp4', 'panic.mp4', 'take_me_dancing.mp4', 'jane.mp4', 'kalapastangan.mp4']
for v in vids:
    full_path = os.path.join('docs', 'assets', 'videos', v)
    sz = os.path.getsize(full_path) / (1024*1024)
    res = subprocess.run([ffmpeg, '-i', full_path], capture_output=True, text=True)
    dur_m = re.search(r'Duration:\s*(\d+:\d+:\d+\.\d+)', res.stderr)
    video_m = re.search(r'Video:\s*([^,\n]+(?:,[^,\n]+){2,3})', res.stderr)
    audio_m = re.search(r'Audio:\s*([^,\n]+)', res.stderr)
    dur = dur_m.group(1) if dur_m else 'Unknown'
    vinfo = video_m.group(1).strip() if video_m else 'Unknown'
    ainfo = audio_m.group(1).strip() if audio_m else 'Unknown'
    print(f'  {v}: {sz:.2f} MB, Duration: {dur}\n    Video: {vinfo}\n    Audio: {ainfo}')


