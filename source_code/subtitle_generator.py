# subtitle_generator.py
from pathlib import Path
from typing import List
import pysrt


def words_to_srt(
    words: List[dict],
    outfile: Path,
    max_chars: int = 42,
    max_duration: float = 4.0,
) -> Path:
    """
    Превращает список слов с таймкодами в .srt.

    :param words: [{word, start, end}, ...] – время в секундах
    :param outfile: куда сохранить .srt
    :param max_chars: максимальная длина одной строки
    :param max_duration: макс. продолжительность субтитра
    :return: Path к созданному файлу
    """
    subs = pysrt.SubRipFile()
    idx = 1
    line, start_t, end_t = "", None, None

    for w in words:
        # старт новой фразы?
        if not line:
            start_t = w["start"]

        # добавляем слово
        sep = "" if line == "" else " "
        tentative = f"{line}{sep}{w['word']}"
        end_t = w["end"]

        # если превысили лимиты — завершаем текущую строку
        if (
            len(tentative) > max_chars
            or (end_t - start_t) > max_duration
        ):
            subs.append(
                pysrt.SubRipItem(
                    index=idx,
                    start=pysrt.SubRipTime(seconds=start_t),
                    end=pysrt.SubRipTime(seconds=prev_end),
                    text=line,
                )
            )
            idx += 1
            line = w["word"]
            start_t = w["start"]
        else:
            line = tentative

        prev_end = end_t

    # последняя строка
    if line:
        subs.append(
            pysrt.SubRipItem(
                index=idx,
                start=pysrt.SubRipTime(seconds=start_t),
                end=pysrt.SubRipTime(seconds=end_t),
                text=line,
            )
        )

    outfile.parent.mkdir(parents=True, exist_ok=True)
    subs.save(outfile, encoding="utf‑8")
    return outfile