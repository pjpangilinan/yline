import os
import subprocess
import time
import imageio_ffmpeg
from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
    ColorClip,
)
from PIL import Image, ImageDraw, ImageFont

# Set up test data
os.makedirs("output/competition", exist_ok=True)
resolution = (1920, 1080)
w, h = resolution

# 5 slides matching Summertown test
lyrics = [
    {"text": "Driving down that southern road", "start_ms": 3000, "end_ms": 7000},
    {"text": "Autumn leaves are falling slow", "start_ms": 7000, "end_ms": 11000},
    {"text": "Golden fields of summer glow", "start_ms": 11000, "end_ms": 15000},
    {"text": "Withered flowers by the door", "start_ms": 15000, "end_ms": 19000},
    {"text": "Welcome home to Summertown", "start_ms": 19000, "end_ms": 23000},
]
image_paths = [
    f"output/The Ridleys - Summertown/images/img_{i:03d}.jpg" for i in range(5)
]
audio_path = "output/The Ridleys - Summertown/Summertown (Official Audio).mp3"

# --- Option 1: MoviePy 2.x ---
def run_moviepy():
    t0 = time.perf_counter()
    clips = []
    # Intro
    intro_img = image_paths[0]
    bg0 = ImageClip(intro_img).resized(height=h).with_duration(3.0)
    txt0 = TextClip(text="Now Playing\nSummertown", font_size=50, color="white", size=(w - 200, 300), method="caption", text_align="center").with_position("center").with_duration(3.0)
    clips.append(CompositeVideoClip([bg0, txt0], size=(w, h)))

    for i, line in enumerate(lyrics):
        dur = (line["end_ms"] - line["start_ms"]) / 1000.0
        bg = ImageClip(image_paths[i]).resized(height=h).with_duration(dur)
        txt = TextClip(text=line["text"], font_size=50, color="white", size=(w - 200, 300), method="caption", text_align="center").with_position("center").with_duration(dur)
        clips.append(CompositeVideoClip([bg, txt], size=(w, h)))

    final = concatenate_videoclips(clips, method="chain")
    if os.path.exists(audio_path):
        aud = AudioFileClip(audio_path).subclipped(0, final.duration)
        final = final.with_audio(aud)
    
    out_mp = "output/competition/moviepy_output.mp4"
    final.write_videofile(out_mp, fps=24, codec="h264_nvenc", audio_codec="aac", threads=8, ffmpeg_params=["-pix_fmt", "yuv420p"])
    final.close()
    return time.perf_counter() - t0, out_mp

# --- Option 2: Pure Pillow + Direct FFmpeg (NVENC) ---
def run_pillow_direct_ffmpeg():
    t0 = time.perf_counter()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    slides_dir = "output/competition/slides"
    os.makedirs(slides_dir, exist_ok=True)
    
    font_path = "C:/Windows/Fonts/arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 54)
    except Exception:
        font = ImageFont.load_default()

    concat_file = os.path.join(slides_dir, "concat.txt")
    
    # Render slides
    timeline = []
    # Intro
    timeline.append((image_paths[0], "Now Playing\n\nThe Ridleys - Summertown", 3.0))
    for i, line in enumerate(lyrics):
        dur = (line["end_ms"] - line["start_ms"]) / 1000.0
        timeline.append((image_paths[i], line["text"], dur))

    with open(concat_file, "w", encoding="utf-8") as f:
        for idx, (img_p, text, dur) in enumerate(timeline):
            slide_out = os.path.join(slides_dir, f"slide_{idx:03d}.jpg")
            
            # Load and crop background
            if img_p and os.path.exists(img_p):
                with Image.open(img_p) as src:
                    src = src.convert("RGB")
                    # Aspect fit/crop to 1920x1080
                    src_w, src_h = src.size
                    scale = max(w / src_w, h / src_h)
                    new_w = int(round(src_w * scale))
                    new_h = int(round(src_h * scale))
                    resized = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    # Center crop
                    x1 = (new_w - w) // 2
                    y1 = (new_h - h) // 2
                    base_img = resized.crop((x1, y1, x1 + w, y1 + h))
            else:
                base_img = Image.new("RGB", (w, h), (10, 10, 10))

            if text:
                # Add semi-transparent banner
                overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw_ov = ImageDraw.Draw(overlay)
                box_top = (h - 220) // 2
                box_bottom = box_top + 220
                draw_ov.rectangle([0, box_top, w, box_bottom], fill=(0, 0, 0, 150))
                
                # Draw text with outline
                for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
                    draw_ov.multiline_text((w // 2 + offset[0], h // 2 + offset[1]), text, font=font, fill=(0, 0, 0, 220), anchor="mm", align="center")
                draw_ov.multiline_text((w // 2, h // 2), text, font=font, fill=(255, 255, 255, 255), anchor="mm", align="center")

                base_img = Image.alpha_composite(base_img.convert("RGBA"), overlay).convert("RGB")

            base_img.save(slide_out, "JPEG", quality=95)
            clean_p = os.path.abspath(slide_out).replace("\\", "/")
            f.write(f"file '{clean_p}'\nduration {dur}\n")

        # Repeat last slide per concat protocol
        last_clean = os.path.abspath(os.path.join(slides_dir, f"slide_{len(timeline)-1:03d}.jpg")).replace("\\", "/")
        f.write(f"file '{last_clean}'\n")

    out_direct = "output/competition/pillow_ffmpeg_nvenc.mp4"
    total_dur = sum(item[2] for item in timeline)
    
    cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", os.path.abspath(concat_file),
        "-ss", "0", "-t", str(total_dur), "-i", os.path.abspath(audio_path),
        "-c:v", "h264_nvenc", "-preset", "p4", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-r", "24",
        "-shortest",
        os.path.abspath(out_direct)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return time.perf_counter() - t0, out_direct

if __name__ == "__main__":
    print("Running Competition Benchmark (23-second video)...")
    
    t_direct, p_direct = run_pillow_direct_ffmpeg()
    print(f"Option 2 [Pillow + Direct FFmpeg NVENC]: {t_direct:.2f} seconds! Output size: {os.path.getsize(p_direct)/1024:.1f} KB")

    t_mp, p_mp = run_moviepy()
    print(f"Option 1 [MoviePy 2.x + NVENC]: {t_mp:.2f} seconds! Output size: {os.path.getsize(p_mp)/1024:.1f} KB")

    print(f"\nSpeedup: Direct FFmpeg is {t_mp / t_direct:.1f}x FASTER than MoviePy!")
