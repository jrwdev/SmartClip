# video_utils.py
from pathlib import Path
import subprocess
from typing import List, Tuple

FFMPEG_BIN = "ffmpeg"
CLIPS_DIR  = Path("data/clips")
AUDIO_DIR  = Path("data/audio")

# ──────────────────────────────────────────────────────────────────────────────
def ensure_dirs() -> None:
    for d in (CLIPS_DIR, AUDIO_DIR):
        d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
def split_video(
    src: Path,
    intervals: List[Tuple[str, str]],
    prefix: str = "clip"
) -> List[Path]:
    ensure_dirs()
    out_paths: List[Path] = []

    for idx, (start, end) in enumerate(intervals, 1):
        out_file = CLIPS_DIR / f"{prefix}_{idx:02d}.mp4"
        cmd = [
            FFMPEG_BIN,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            start,
            "-to",
            end,
            "-i",
            str(src),
            "-c",
            "copy",
            str(out_file)
        ]
        subprocess.run(cmd, check=True)
        out_paths.append(out_file)

    return out_paths

# ──────────────────────────────────────────────────────────────────────────────
def extract_audio(video: Path, fmt: str = "mp3") -> Path:
    ensure_dirs()
    out_file = AUDIO_DIR / f"{video.stem}.{fmt}"
    cmd = [
        FFMPEG_BIN, "-hide_banner", "-loglevel", "error",
        "-i", str(video),
        "-vn",
        "-acodec", "copy" if fmt == "aac" else "libmp3lame",
        str(out_file)
    ]
    subprocess.run(cmd, check=True)
    return out_file
