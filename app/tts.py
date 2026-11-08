"""Neural text-to-speech via the edge-tts package (Microsoft neural voices, no API key).
If the package or the network is missing the endpoint returns 503 and the browser falls back to its own voice.

The voice is chosen from the text itself (its script), then from the conversation language: a Hindi sentence
read by an English voice would skip every Hindi word."""
import re

try:
    import edge_tts
except Exception:  # package not installed
    edge_tts = None

VOICES = {
    "en": "en-IN-NeerjaNeural", "hi": "hi-IN-SwaraNeural", "mr": "mr-IN-AarohiNeural", "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural", "bn": "bn-IN-TanishaaNeural", "gu": "gu-IN-DhwaniNeural", "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
}
# (script range, language). Devanagari is shared by Hindi and Marathi: the conversation language decides.
SCRIPTS = [("ऀ", "ॿ", "hi"), ("஀", "௿", "ta"), ("ఀ", "౿", "te"), ("ঀ", "৿", "bn"),
           ("઀", "૿", "gu"), ("ಀ", "೿", "kn"), ("ഀ", "ൿ", "ml")]
RUPEE = {"en": "rupees", "hi": "रुपये", "mr": "रुपये", "ta": "ரூபாய்", "te": "రూపాయలు", "bn": "টাকা", "gu": "રૂપિયા", "kn": "ರೂಪಾಯಿ", "ml": "രൂപ"}
PER_MONTH = {"en": " per month", "hi": " प्रति माह", "mr": " प्रति महिना", "ta": " மாதத்திற்கு", "te": " నెలకు", "bn": " প্রতি মাসে",
             "gu": " દર મહિને", "kn": " ತಿಂಗಳಿಗೆ", "ml": " പ്രതിമാസം"}


def pick_lang(text, lang):
    counts = {}
    for ch in text or "":
        for lo, hi, code in SCRIPTS:
            if lo <= ch <= hi:
                counts[code] = counts.get(code, 0) + 1
    if counts:
        code = max(counts, key=counts.get)
        return "mr" if (code == "hi" and lang == "mr") else code
    return lang if lang in VOICES else "en"


def clean(text, lang):
    t = re.sub(r"\*\*", "", text)
    t = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", t)
    t = re.sub(r"₹\s?([\d,]+)", lambda m: m.group(1).replace(",", "") + " " + RUPEE.get(lang, "rupees"), t)
    t = t.replace("/month", PER_MONTH.get(lang, " per month")).replace("/माह", PER_MONTH["hi"])
    t = re.sub(r"\s*\n+\s*", ". ", t)
    return re.sub(r"\s+", " ", t).strip()


async def stream(text, lang):
    lang = pick_lang(text, lang)
    async for chunk in edge_tts.Communicate(clean(text, lang), VOICES[lang]).stream():
        if chunk["type"] == "audio":
            yield chunk["data"]
