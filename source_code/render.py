# render.py
from pathlib import Path
import subprocess


def render_with_subs(
    video: Path,
    srt: Path,
    out: Path | None = None,
    *,
    font: str | None = None,
    fontsize: int = 48,
    margin_v: int = 50,
) -> Path:
    """
    Накладывает .srt на видео и сохраняет mp4.
      :param video: исходный MP4
      :param srt:   файл субтитров
      :param out:   куда сохранить (по умолч. — final/<video_stem>_sub.mp4)
      :param font:  путь к .ttf или системное имя шрифта (опционально)
      :param fontsize: размер шрифта
      :param margin_v: отступ снизу, px
      :return: Path финального mp4
    """
    video = video.resolve()
    srt   = srt.resolve()
    if out is None:
        out = video.parent.parent / "final" / f"{video.stem}_sub.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg filter для burn‑in
    subtitles_filter = f"subtitles='{srt.as_posix()}'"
    if font:
        # drawtext позволит задать font/size/box, но проще: указать `force_style`
        subtitles_filter = (
            f"subtitles='{srt.as_posix()}':force_style="
            f"'Fontname={font},Fontsize={fontsize},MarginV={margin_v}'"
        )

    cmd = [
        "ffmpeg",
        "-y",                       # overwrite
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(video),
        "-vf", subtitles_filter,
        "-c:a", "copy",             # не перекодируем аудио
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return out
