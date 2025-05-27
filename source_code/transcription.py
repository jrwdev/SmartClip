# transcription.py
from __future__ import annotations
import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv
load_dotenv('keys.env')

# ──────────────────────────────────────────────────────────────────
class TranscriptionError(Exception):
    """Базовая ошибка модуля."""
class QuotaExceeded(TranscriptionError):
    """API ответил, что закончилась бесплатная квота."""

# ──────────────────────────────────────────────────────────────────
class STTEngine(ABC):
    """Единый интерфейс для всех движков."""

    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        lang: str = "auto",
        translate_to_en: bool = False,
    ) -> str:
        ...

    # Хелпер для детекции «лимит исчерпан»
    def _is_quota_error(self, exc: Exception) -> bool:
        return False


# ──────────────────────────────────────────────────────────────────
class DeepgramEngine(STTEngine):
    """Deepgram SDK v3 — синхронный threaded‑клиент."""

    def __init__(self):
        from deepgram import DeepgramClient, PrerecordedOptions
        api_key = os.getenv("DEEPGRAM_API_KEY", "")
        if not api_key:
            raise TranscriptionError("DEEPGRAM_API_KEY is missing")
        self.dg = DeepgramClient(api_key)                  # берёт ключ из env
        self.Options = PrerecordedOptions

    def transcribe(
        self,
        audio_path: Path,
        lang: str = "auto",
        translate_to_en: bool = False,
    ) -> tuple[str, list[dict]]:
        import json, httpx

        with open(audio_path, "rb") as f:
            payload = {"buffer": f.read()}

        # ① создаём options БЕЗ аргументов
        opts = self.Options()
        opts.model = "nova-2"
        opts.smart_format = True                 # punctuation + casing
        if lang != "auto":
            opts.language = lang
        if translate_to_en:
            opts.translate = True                # translate→EN

        try:
            resp = (self.dg.listen
                        .rest.v("1")
                        .transcribe_file(payload, opts,
                                         timeout=httpx.Timeout(300.0, connect=10.0)))
            data = json.loads(resp.to_json())
            alt = data["results"]["channels"][0]["alternatives"][0]
            return alt["transcript"], alt["words"]          # ← words уже есть
        except Exception as e:
            if self._is_quota_error(e):
                raise QuotaExceeded from e
            raise

    def _is_quota_error(self, exc: Exception) -> bool:
        msg = str(exc).lower()
        return "quota" in msg or "rate limit" in msg

# ──────────────────────── AssemblyAI (SDK v1.x «Transcriber») ──────────────────
class AssemblyAIEngine(STTEngine):
    """AssemblyAI 1.4 — синхронный Transcriber API."""

    def __init__(self):
        import assemblyai as aai
        api_key = os.getenv("ASSEMBLYAI_API_KEY", "")
        if not api_key:
            raise TranscriptionError("ASSEMBLYAI_API_KEY is missing")

        aai.settings.api_key = api_key
        self.aai = aai
        self.transcriber = aai.Transcriber()

    def transcribe(self, audio_path: Path,
                   lang: str = "auto",
                   translate_to_en: bool = False) -> str:
        """
        AssemblyAI не поддерживает auto‑translate → игнорируем translate_to_en.
        """
        cfg = self.aai.TranscriptionConfig(words=True, language_code=None if lang=="auto" else lang)

        try:
            t = self.transcriber.transcribe(str(audio_path), config=cfg)
            if t.status == self.aai.TranscriptStatus.error:
                raise TranscriptionError(t.error or "AssemblyAI unknown error")
            return t.text, [dict(word=w.text, start=w.start / 1000, end=w.end / 1000) for w in t.words]
        except Exception as e:
            if self._is_quota_error(e):
                raise QuotaExceeded from e
            raise

    def _is_quota_error(self, exc: Exception) -> bool:
        return "insufficient" in str(exc).lower() or "quota" in str(exc).lower()


# ──────────────────────────────────────────────────────────────────
"""
class GoogleEngine(STTEngine):
    def __init__(self):
        from google.cloud import speech
        self.client = speech.SpeechClient()

    def transcribe(self, audio_path, lang="auto", translate_to_en=False):
        from google.cloud.speech_v1 import types as stt_types
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        audio = stt_types.RecognitionAudio(content=audio_bytes)
        config = stt_types.RecognitionConfig(
            language_code="en-US" if lang == "auto" else lang,
            enable_automatic_punctuation=True,
            audio_channel_count=1,
        )
        response = self.client.recognize(config=config, audio=audio)
        if not response.results:
            raise TranscriptionError("Google STT returned empty result")
        transcript = " ".join(r.alternatives[0].transcript for r in response.results)
        # Google‑STT сам не переводит; при translate_to_en → оставляем как есть
        return transcript

    def _is_quota_error(self, exc):
        return "limit" in str(exc).lower() or "Quota" in str(exc)
"""

# ──────────────────────────────────────────────────────────────────
"""
class OpenAIWhisperEngine(STTEngine):
    def __init__(self):
        import openai
        self.openai = openai

    def transcribe(self, audio_path, lang="auto", translate_to_en=False):
        with open(audio_path, "rb") as f:
            params = {"file": f, "model": "whisper-1"}
            if translate_to_en:
                params["response_format"] = "text"
                params["language"] = "en"
            resp = self.openai.audio.transcriptions.create(**params)
            # API возвращает dict/str в зависимости от формата
            return resp["text"] if isinstance(resp, dict) else resp

    def _is_quota_error(self, exc):
        return "Rate limit" in str(exc) or "quota" in str(exc).lower()
"""


# ──────────────────────────────────────────────────────────────────
ENGINE_ORDER = [
    DeepgramEngine(),
    AssemblyAIEngine()
]

def smart_transcribe(
    audio_path: Path,
    *,
    lang: str = "auto",
    translate_to_en: bool = False,
    engine_name: Optional[str] = None,
    engines = ENGINE_ORDER,
) -> tuple[str, list[dict]]:
    """Если задан специфичный транскрайбер"""
    if engine_name:
        selected = next((e for e in engines if e.__class__.__name__.lower().startswith(engine_name.lower())), None)
        if not selected:
            raise ValueError(f"No engine found matching: {engine_name}")
        print(f"[STT] Using selected engine: {selected.__class__.__name__}")
        return selected.transcribe(audio_path, lang, translate_to_en)
    """Пробует движки по очереди, пока один не сработает."""
    last_error: Optional[Exception] = None
    for eng in engines:  # автоматический fallback
        try:
            print(f"[STT] → {eng.__class__.__name__}")
            text, words = eng.transcribe(audio_path, lang, translate_to_en)
            if text.strip():
                return text, words
        except QuotaExceeded:
            print(f"  ‑ лимит исчерпан, пробуем следующий …")
        except Exception as e:
            print(f"  ‑ ошибка: {e.__class__.__name__}")
            last_error = e
    raise TranscriptionError("All engines failed") from last_error
