"""
Browser-based voice helpers — works on the live web app with NO server-side
audio libraries and NO paid APIs. Uses:

- speechSynthesis (Web Speech API)         → text-to-speech
- webkitSpeechRecognition (Web Speech API) → speech-to-text
  (wrapped via the streamlit-mic-recorder package)

Designed for Chrome / Edge desktop + mobile. Safari has partial support.
Firefox does not support webkitSpeechRecognition.
"""

import html as _html
import json as _json
import streamlit as st
import streamlit.components.v1 as components

# Languages exposed in the UI
LANGUAGES = [
    ("English (India)", "en-IN"),
    ("English (US)",    "en-US"),
    ("Hindi (India)",   "hi-IN"),
    ("Bengali (India)", "bn-IN"),
]
LANG_CODES = [code for _, code in LANGUAGES]
LANG_LABELS = [name for name, _ in LANGUAGES]


# ─────────────────────────────────────────────────────────
# SPEECH-TO-TEXT (browser → Python)
# ─────────────────────────────────────────────────────────

def _has_mic_recorder():
    try:
        import streamlit_mic_recorder  # noqa: F401
        return True
    except ImportError:
        return False


def listen(language: str = "en-IN", key: str = "voice_listen") -> str | None:
    """
    Render a mic button that captures speech via the browser's
    webkitSpeechRecognition API and returns the recognised transcript.

    Returns the transcript string when the user finishes speaking,
    or None on every other render.
    """
    if not _has_mic_recorder():
        st.info(
            "🎤 Voice input is not available — install `streamlit-mic-recorder` "
            "(`pip install streamlit-mic-recorder`)."
        )
        return None

    from streamlit_mic_recorder import speech_to_text

    return speech_to_text(
        language=language,
        start_prompt="🎤 Tap to speak",
        stop_prompt="⏹ Stop",
        just_once=True,
        use_container_width=False,
        key=key,
    )


# ─────────────────────────────────────────────────────────
# TEXT-TO-SPEECH (Python → browser JS)
# ─────────────────────────────────────────────────────────

def _tts_html(text: str, lang: str = "en-IN", rate: float = 1.0,
              pitch: float = 1.0, autoplay: bool = True) -> str:
    """Generate an HTML/JS snippet that speaks `text` via speechSynthesis."""
    payload = _json.dumps({"text": text, "lang": lang, "rate": rate, "pitch": pitch})
    return f"""
    <div id="tts-host"></div>
    <script>
      (function () {{
        const cfg = {payload};
        if (!('speechSynthesis' in window)) return;

        function speakNow() {{
          try {{
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(cfg.text);
            u.lang   = cfg.lang || 'en-IN';
            u.rate   = cfg.rate || 1.0;
            u.pitch  = cfg.pitch || 1.0;
            u.volume = 1.0;

            // Try to pick a voice that matches the requested language
            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length) {{
              const match = voices.find(v => v.lang === cfg.lang)
                         || voices.find(v => v.lang && v.lang.startsWith(cfg.lang.split('-')[0]));
              if (match) u.voice = match;
            }}
            window.speechSynthesis.speak(u);
          }} catch (e) {{ console.warn('TTS error:', e); }}
        }}

        // Voices load async on some browsers
        if (window.speechSynthesis.getVoices().length === 0) {{
          window.speechSynthesis.onvoiceschanged = speakNow;
          setTimeout(speakNow, 250);
        }} else {{
          speakNow();
        }}
      }})();
    </script>
    """


def speak(text: str, lang: str = "en-IN", rate: float = 1.0, pitch: float = 1.0):
    """
    Speak text in the browser. Renders an invisible HTML component.
    Call this exactly once per AI response (e.g., right after producing it),
    NOT on every rerun, otherwise the line will be re-spoken each time.
    """
    if not text:
        return
    # Trim emojis / markdown that read awkwardly aloud
    cleaned = _clean_for_speech(text)
    if not cleaned:
        return
    components.html(_tts_html(cleaned, lang=lang, rate=rate, pitch=pitch), height=0, width=0)


def render_replay_button(text: str, lang: str = "en-IN", key: str = "tts_replay"):
    """A 🔊 Replay button that re-speaks the given text on click."""
    if not text:
        return
    if st.button("🔊 Replay", key=key):
        speak(text, lang=lang)


def render_test_voice_button(lang: str = "en-IN", key: str = "tts_test"):
    """Renders a Test button + speaks a sample line on click."""
    if st.button("🔊 Test Voice", key=key, use_container_width=False):
        sample = {
            "en-IN": "Hello! This is your AI tutor. Voice is working.",
            "en-US": "Hello! This is your AI tutor. Voice is working.",
            "hi-IN": "नमस्ते! मैं आपका एआई ट्यूटर हूँ। आवाज़ काम कर रही है।",
            "bn-IN": "নমস্কার! আমি আপনার এআই টিউটর। কণ্ঠস্বর কাজ করছে।",
        }.get(lang, "Hello! This is your AI tutor.")
        speak(sample, lang=lang)
        st.success("🔊 Speaking sample…")


# ─────────────────────────────────────────────────────────
# STATUS / CAPABILITIES
# ─────────────────────────────────────────────────────────

def render_capabilities_probe():
    """
    Renders a tiny JS probe that displays the browser's actual voice
    capability flags. Useful on the Settings page so the parent can verify
    on the device the child uses.
    """
    components.html(
        """
        <div style="font-family: 'Nunito', sans-serif; font-size: 0.95rem;">
          <div id="probe-out">Checking browser capabilities…</div>
        </div>
        <script>
          (function () {
            const out = document.getElementById('probe-out');
            const sr = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
            const ss = ('speechSynthesis' in window);
            const ua = navigator.userAgent;
            const isChromium = /Chrome|Edg|Brave|OPR/.test(ua) && !/Firefox/.test(ua);
            const isFirefox = /Firefox/.test(ua);
            const isSafari  = /^((?!chrome|android).)*safari/i.test(ua);

            const row = (icon, label) =>
              `<div style="display:flex;gap:.5rem;align-items:center;margin:.25rem 0;">
                 <span style="font-size:1.1rem;">${icon}</span><span>${label}</span>
               </div>`;

            let html = "";
            html += row(sr ? "✅" : "❌", "Browser Speech Recognition (webkitSpeechRecognition)");
            html += row(ss ? "✅" : "❌", "Speech Synthesis (text-to-speech)");
            html += row(isChromium ? "✅" : (isSafari ? "⚠️" : (isFirefox ? "⚠️" : "ℹ️")),
                        `Browser: ${isChromium ? "Chrome / Edge (best)" : (isSafari ? "Safari (partial)" : (isFirefox ? "Firefox (no STT)" : "Unknown"))}`);

            if (!sr || !ss || isFirefox || isSafari) {
              html += `<div style="margin-top:.6rem;padding:.6rem;border-radius:8px;
                background:#fff8e5;border:1px solid #FDCB6E;color:#7a5c00;font-size:.9rem;">
                ⚠️ For best voice experience, open this app in <b>Google Chrome</b> or <b>Microsoft Edge</b>.
              </div>`;
            }
            out.innerHTML = html;
          })();
        </script>
        """,
        height=170,
    )


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def _clean_for_speech(text: str) -> str:
    """Strip markdown/emoji noise so the TTS reads cleanly."""
    import re
    if not text:
        return ""
    text = re.sub(r"```[\s\S]*?```", " ", text)             # code fences
    text = re.sub(r"`([^`]+)`", r"\1", text)                # inline code
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)            # bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)                # italic
    text = re.sub(r"#{1,6}\s*", "", text)                   # headings
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)    # links
    text = re.sub(r"[•\-]\s", ". ", text)                   # bullet markers
    # Drop most non-letter/digit/punct chars (kills emoji)
    text = re.sub(r"[^\w\s.,;:!?'\"()/-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 800:
        text = text[:800].rsplit(" ", 1)[0] + "."
    return text
