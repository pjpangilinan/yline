import os
import time
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs("output/bench", exist_ok=True)

# Generate 5 test background slides with lyrics using Pillow
t0 = time.perf_counter()
durations = [3.0, 4.0, 3.5, 5.0, 4.5]  # 20 seconds total
concat_txt = os.path.abspath("output/bench/concat.txt")
with open(concat_txt, "w") as f:
    for i, dur in enumerate(durations):
        slide_path = os.path.abspath(f"output/bench/slide_{i:02d}.jpg")
        img = Image.new("RGB", (1920, 1080), (20 * i + 10, 40, 60))
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([0, 440, 1920, 640], fill=(0, 0, 0, 160))
        d.text((960, 540), f"Test Lyric Slide {i+1} Line", fill="white", anchor="mm")
        img.save(slide_path, "JPEG", quality=95)
        # In ffmpeg concat demuxer, forward slashes or escaped paths work
        clean_path = slide_path.replace("\\", "/")
        f.write(f"file '{clean_path}'\nduration {dur}\n")
    # Last file must be repeated per concat demuxer spec
    last_path = os.path.abspath("output/bench/slide_04.jpg").replace("\\", "/")
    f.write(f"file '{last_path}'\n")

t_prep = time.perf_counter() - t0

# Run ffmpeg concat with NVENC
t1 = time.perf_counter()
cmd_nvenc = [
    ffmpeg, "-y",
    "-f", "concat", "-safe", "0", "-i", concat_txt,
    "-c:v", "h264_nvenc", "-preset", "p4", "-pix_fmt", "yuv420p",
    "-r", "24",
    os.path.abspath("output/bench/ffmpeg_nvenc.mp4")
]
res_nvenc = subprocess.run(cmd_nvenc, capture_output=True, text=True)
t_nvenc = time.perf_counter() - t1

# Run ffmpeg concat with CPU libx264 fast
t2 = time.perf_counter()
cmd_cpu = [
    ffmpeg, "-y",
    "-f", "concat", "-safe", "0", "-i", concat_txt,
    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
    "-r", "24",
    os.path.abspath("output/bench/ffmpeg_cpu.mp4")
]
res_cpu = subprocess.run(cmd_cpu, capture_output=True, text=True)
t_cpu = time.perf_counter() - t2

print(f"Slide prep time: {t_prep*1000:.1f}ms")
print(f"Direct FFmpeg + NVENC time: {t_nvenc:.2f}s for 20s video ({20/t_nvenc:.1f}x realtime, code={res_nvenc.returncode})")
print(f"Direct FFmpeg + CPU time: {t_cpu:.2f}s for 20s video ({20/t_cpu:.1f}x realtime, code={res_cpu.returncode})")
