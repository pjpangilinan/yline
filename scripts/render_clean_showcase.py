import os
import json
import re
import subprocess
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

def ms_to_ass(ms):
    if ms < 0: ms = 0
    h = ms // 3600000; ms %= 3600000
    m = ms // 60000; ms %= 60000
    s = ms // 1000; cs = (ms % 1000) // 10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 1
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,50,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def render_part(images, durations, start_idx, end_idx, out_part_mp4):
    cmd = [ffmpeg, "-y"]
    filter_complex = []
    concat_inputs = ""
    part_len = end_idx - start_idx
    for local_i, idx in enumerate(range(start_idx, end_idx)):
        dur = durations[idx]
        img_p = os.path.abspath(images[idx]).replace("\\", "/")
        cmd.extend(["-loop", "1", "-t", f"{dur:.3f}", "-i", img_p])
        filter_complex.append(f"[{local_i}:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[v{local_i}]")
        concat_inputs += f"[v{local_i}]"
    
    filter_complex.append(f"{concat_inputs}concat=n={part_len}:v=1:a=0[vout]")
    cmd.extend([
        "-filter_complex", ";".join(filter_complex),
        "-map", "[vout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        out_part_mp4
    ])
    print(f"Rendering batch {out_part_mp4} ({part_len} clips)...", flush=True)
    subprocess.run(cmd, check=True)

def render_split_cfr_video(images, durations, ass_path, audio_path, output_video, batch_size=20):
    total_slides = len(images)
    parts = []
    split_indices = list(range(0, total_slides, batch_size))
    if split_indices[-1] != total_slides:
        split_indices.append(total_slides)
        
    tag = os.path.basename(output_video).replace(".mp4", "")
    for i in range(len(split_indices) - 1):
        s_idx = split_indices[i]
        e_idx = split_indices[i+1]
        part_name = f"docs/assets/videos/temp_{tag}_part_{i}.mp4"
        render_part(images, durations, s_idx, e_idx, part_name)
        parts.append(part_name)
        
    concat_list = f"docs/assets/videos/temp_{tag}_parts.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p).replace('\\', '/')}'\n")
            
    ass_escaped = os.path.abspath(ass_path).replace("\\", "/").replace(":", "\\:")
    cmd_final = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", audio_path,
        "-vf", f"drawbox=y=(ih-300)/2:color=black@0.6:width=iw:height=300:t=fill,ass='{ass_escaped}'",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_video
    ]
    print(f"Compositing final video: {output_video}...", flush=True)
    subprocess.run(cmd_final, check=True)
    
    # Cleanup temp parts
    for p in parts + [concat_list]:
        if os.path.exists(p):
            os.remove(p)
    print(f"Finished {output_video} successfully!", flush=True)

def render_jane():
    print("\n================== RENDERING JANE! ==================", flush=True)
    with open("lrc_Jane.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    lines = [l for l in data["lines"] if l["text"].strip()]
    total_duration_ms = 187490  # 3:07.49
    
    # Subtitle events with vocal end capping
    ass_lines = [f"Dialogue: 0,0:00:00.00,{ms_to_ass(lines[0]['start_ms'])},Default,,0,0,0,,Now Playing\\N\\Njane!"]
    for i, l in enumerate(lines):
        t = l["text"].replace("\n", "\\N").replace(",", "\\,")
        start_ms = l["start_ms"]
        end_ms = l["end_ms"]
        # Line 4: vocal singing ends at 29.5s; guitar solo plays until line 5 starts at 41.87s
        if i == 4:
            end_ms = 29500
        # Check any other long instrumental gaps > 4.5s
        elif i < len(lines) - 1:
            next_start = lines[i+1]["start_ms"]
            if next_start - start_ms > 4500:
                end_ms = min(end_ms, start_ms + 4000)
        ass_lines.append(f"Dialogue: 0,{ms_to_ass(start_ms)},{ms_to_ass(end_ms)},Default,,0,0,0,,{t}")
        
    ass_path = "docs/assets/videos/jane.ass"
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(ass_lines) + "\n")
        
    # Slide durations
    durations = []
    for i in range(len(lines)):
        start = lines[i]["start_ms"]
        if i == 0: start = 0
        if i < len(lines) - 1:
            d = (lines[i+1]["start_ms"] - start) / 1000.0
        else:
            d = (total_duration_ms - start) / 1000.0
        if d <= 0: d = 0.1
        durations.append(d)
        
    images = [f"docs/assets/images/jane/img_{i:03d}.jpg" for i in range(len(lines))]
    render_split_cfr_video(
        images=images,
        durations=durations,
        ass_path=ass_path,
        audio_path="output/jane/audio.mp3",
        output_video="docs/assets/videos/jane.mp4",
        batch_size=15
    )

def render_take_me_dancing():
    print("\n================== RENDERING TAKE ME DANCING ==================", flush=True)
    with open("lrc_Take_Me_Dancing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    lines = [l for l in data["lines"] if l["text"].strip()]
    lines[0]["start_ms"] = 1740  # True vocal onset after acoustic guitar intro
    total_duration_ms = 190700  # 3:10.70
    
    ass_lines = [f"Dialogue: 0,0:00:00.00,{ms_to_ass(lines[0]['start_ms'])},Default,,0,0,0,,Now Playing\\N\\Ntake me dancing"]
    for i, l in enumerate(lines):
        t = l["text"].replace("\n", "\\N").replace(",", "\\,")
        start_ms = l["start_ms"]
        end_ms = l["end_ms"]
        if i < len(lines) - 1:
            next_start = lines[i+1]["start_ms"]
            if next_start - start_ms > 4500:
                end_ms = min(end_ms, start_ms + 4000)
        ass_lines.append(f"Dialogue: 0,{ms_to_ass(start_ms)},{ms_to_ass(end_ms)},Default,,0,0,0,,{t}")
        
    ass_path = "docs/assets/videos/take_me_dancing.ass"
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(ass_lines) + "\n")
        
    durations = []
    for i in range(len(lines)):
        start = lines[i]["start_ms"]
        if i == 0: start = 0
        if i < len(lines) - 1:
            d = (lines[i+1]["start_ms"] - start) / 1000.0
        else:
            d = (total_duration_ms - start) / 1000.0
        if d <= 0: d = 0.1
        durations.append(d)
        
    images = [f"docs/assets/images/take_me_dancing/img_{i:03d}.jpg" for i in range(len(lines))]
    render_split_cfr_video(
        images=images,
        durations=durations,
        ass_path=ass_path,
        audio_path="output/take_me_dancing/audio.mp3",
        output_video="docs/assets/videos/take_me_dancing.mp4",
        batch_size=20
    )

def render_kalapastangan():
    print("\n================== RENDERING KALAPASTANGAN ==================", flush=True)
    with open("lrc_Kalapastangan.json", "r", encoding="utf-8") as f:
        item = json.load(f)
    synced = item.get("syncedLyrics", "")
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
    
    raw_lines = []
    for l in synced.splitlines():
        m = pattern.match(l.strip())
        if m:
            mins, secs, text = m.groups()
            ms = int(int(mins) * 60000 + float(secs) * 1000)
            raw_lines.append({"start_ms": ms, "text": text.strip()})
            
    # Apply verified vocal onset adjustments
    if len(raw_lines) > 4 and "Sino ba ako" in raw_lines[4]["text"]:
        raw_lines[4]["start_ms"] = 31500
    if len(raw_lines) > 5 and "Mga dalangin" in raw_lines[5]["text"]:
        raw_lines[5]["start_ms"] = 42500
        
    total_duration_ms = 276100  # 4:36.10
    
    # Calculate end_ms for all slides
    for i in range(len(raw_lines)):
        if i < len(raw_lines) - 1:
            raw_lines[i]["end_ms"] = raw_lines[i+1]["start_ms"]
        else:
            raw_lines[i]["end_ms"] = total_duration_ms
            
    # Subtitle events: only non-empty lines get dialogue captions
    ass_lines = [f"Dialogue: 0,0:00:00.00,{ms_to_ass(raw_lines[0]['start_ms'])},Default,,0,0,0,,Now Playing\\N\\Nkalapastangan"]
    for l in raw_lines:
        if l["text"]:
            t = l["text"].replace("\n", "\\N").replace(",", "\\,")
            ass_lines.append(f"Dialogue: 0,{ms_to_ass(l['start_ms'])},{ms_to_ass(l['end_ms'])},Default,,0,0,0,,{t}")
            
    ass_path = "docs/assets/videos/kalapastangan.ass"
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(ass_lines) + "\n")
        
    durations = []
    for i in range(len(raw_lines)):
        start = raw_lines[i]["start_ms"]
        if i == 0: start = 0
        if i < len(raw_lines) - 1:
            d = (raw_lines[i+1]["start_ms"] - start) / 1000.0
        else:
            d = (total_duration_ms - start) / 1000.0
        if d <= 0: d = 0.1
        durations.append(d)
        
    images = [f"docs/assets/images/kalapastangan/img_{i:03d}.jpg" for i in range(len(raw_lines))]
    render_split_cfr_video(
        images=images,
        durations=durations,
        ass_path=ass_path,
        audio_path="output/kalapastangan/audio.mp3",
        output_video="docs/assets/videos/kalapastangan.mp4",
        batch_size=17
    )

if __name__ == "__main__":
    render_jane()
    render_take_me_dancing()
    render_kalapastangan()
    print("\nAll 3 videos rendered cleanly!", flush=True)
