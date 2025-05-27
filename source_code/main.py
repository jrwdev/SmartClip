# main.py (пока просто тестируем резку и звук)
from pathlib import Path
from video_utils import split_video, extract_audio
from transcription import smart_transcribe
from subtitle_generator import words_to_srt
from render import render_with_subs
from upload import upload_clip

src_video = Path("source/test1.mp4")

intervals = [
    ("00:00:00", "00:00:25"),
]

clips = split_video(src_video, intervals)
print("Клипы:", clips)

clip = Path("data/clips/clip_01.mp4")
audio = extract_audio(clip)

text, words = smart_transcribe(audio, engine_name="deep", translate_to_en=False)   # теперь → (text, words)

srt_file = Path("data/subs/clip_01.srt")
words_to_srt(words, srt_file)
final_mp4 = render_with_subs(clip, srt_file, font="Arial", fontsize=48)

upload_clip(final_mp4, "Auto-uploaded from WSL 🤖 #python #automation")

print("🎉 Готово:", final_mp4)
