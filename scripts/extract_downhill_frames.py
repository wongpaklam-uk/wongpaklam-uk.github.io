#!/usr/bin/env python3
"""Capture original frames from the public DownhillSpotter app-review video.

No generated/retouched content; frames are direct exports from the official public
review.mp4 at https://github.com/wongpaklam-uk/downhillspotter-privacy .
"""
import io
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
VIDEO_URL = "https://raw.githubusercontent.com/wongpaklam-uk/downhillspotter-privacy/main/review.mp4"
SCREEN_DIR = ROOT / "assets" / "screenshots" / "downhillspotter"
MANIFEST = ROOT / "assets" / "appstore-images.js"

def cmd(*args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()

def main():
    with tempfile.TemporaryDirectory() as td:
        video = Path(td) / "review.mp4"
        req = urllib.request.Request(VIDEO_URL, headers={"User-Agent": "BerlinAppsPortfolio/1.0"})
        with urllib.request.urlopen(req, timeout=90) as response:
            video.write_bytes(response.read())
        if video.stat().st_size < 50_000:
            raise RuntimeError("Public app-review video is unexpectedly small")
        try:
            duration = float(cmd("ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=noprint_wrappers=1:nokey=1", str(video)))
        except Exception as exc:
            raise RuntimeError("Cannot inspect authentic review video duration") from exc
        if duration < 3:
            raise RuntimeError("Video is too short to capture reliable frames")
        SCREEN_DIR.mkdir(parents=True, exist_ok=True)
        images = []
        for n, fraction in enumerate((.12, .27, .43, .58, .74, .89), start=1):
            output = SCREEN_DIR / f"demo-frame-{n:02d}.jpg"
            t = max(0, min(duration - .5, duration * fraction))
            try:
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error",
                                "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                                "-vf", "scale='min(1000,iw)':-2", "-q:v", "3",
                                "-y", str(output)], check=True, timeout=45)
            except Exception as exc:
                print("Could not export video frame", n, exc)
                continue
            if not output.is_file() or output.stat().st_size < 4500:
                output.unlink(missing_ok=True)
                continue
            with Image.open(output) as frame:
                grey = frame.convert("L").resize((64, 64))
                contrast = ImageStat.Stat(grey).stddev[0]
            if contrast < 7:
                output.unlink(missing_ok=True)
                continue
            images.append(output.relative_to(ROOT).as_posix())
        if not images:
            raise RuntimeError("No authentic, visible video frames were exported")
        addition = "\n/* Genuine unaltered frames from the public DownhillSpotter app review video. */\n"
        addition += "Object.assign(BERLIN_LOCAL_SCREENSHOTS, " + json.dumps({
            "downhillspotter": {"iphone": images, "ipad": []}
        }, indent=2) + ");\n"
        MANIFEST.write_text(MANIFEST.read_text(encoding="utf-8") + addition, encoding="utf-8")
        print("Actual public DownhillSpotter demo video duration", round(duration, 2), "seconds")
        print("Exported", len(images), "genuine images:", images)

if __name__ == "__main__":
    main()
