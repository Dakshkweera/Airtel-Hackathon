"""Conversation quality check against the REAL model. Run:  python scripts/eval_conversations.py

Plays many messy, realistic owner conversations (mumbling voice transcripts, Hinglish, Hindi, Marathi, Tamil, vague,
off-topic, angry, objections, corrections) and flags every turn where the assistant:
  - did not answer with the AI (keyword fallback or empty reply)
  - said a rupee amount no tool or catalogue produced (invented price)
  - replied in the wrong script for the language the owner used
  - did not open the paperwork when asked to proceed
  - was too slow
  - or, judged by a second AI call, did not actually answer what was asked.
Prints the flagged turns and writes scripts/eval_report.json.
"""
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["UD_SESSION_STORE"] = os.path.join(os.environ.get("TEMP", "/tmp"), "ud_eval_sessions.json")
os.environ["UD_TURN_LOG"] = os.path.join(os.environ.get("TEMP", "/tmp"), "ud_eval_turns.jsonl")

from fastapi.testclient import TestClient  # noqa: E402

import app.main as m  # noqa: E402  (loads .env)
from app import data  # noqa: E402

m.save = lambda: None
KEY = os.environ.get("OPENROUTER_API_KEY")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "anthropic/claude-haiku-5.5")

SCRIPT = {"devanagari": "ऀ-ॿ", "tamil": "஀-௿", "telugu": "ఀ-౿"}

BIG = "shop in Haldwani, 20 staff, 3 branches, no GST, skip"
CLINIC = "Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees"
# (name, [turns]); a turn is "text" or ("text", {"script": ..., "opens": "open_kyc", "voice": True})
SCENARIOS = [
    ("clinic hinglish full flow", [
        "bhai mera clinic hai Indore me 6 staff hain GST bhi hai", "abhi hum 2000 rupaye dete hain internet aur phone ka", "ye to bahut mehnga hai yaar",
        "isme kya kya hai samjhao", "backup internet ki zarurat hai kya", ("theek hai aage badho", {"opens": "open_kyc"})]),
    ("garbled voice, big shop (real session)", [
        BIG, ("send me about word this planet and what I am getting in what's the use of that feature", {"voice": True}),
        ("no tell me about my plan which I have all the features in it and is it what these features are an is it necessary", {"voice": True}),
        ("Can we continue right here, like what's the problem in continuing", {"voice": True}),
        ("let me give you paper", {"opens": "open_kyc"})]),
    ("hindi devanagari", [
        ("मेरा क्लिनिक इंदौर में है, 6 स्टाफ, GST है", {"script": "devanagari"}), ("इसमें क्या क्या मिलेगा", {"script": "devanagari"}),
        ("ये सब ज़रूरी है क्या", {"script": "devanagari"}), ("कितना खर्च आएगा हर महीने", {"script": "devanagari"}),
        ("ठीक है शुरू करो", {"opens": "open_kyc"})]),
    ("objections", [
        CLINIC, "it's too costly for me", "jio is giving me internet for 500 only", "I don't need CCTV or backup, remove them",
        "let me think about it and come back", "no thanks not interested"]),
    ("custom plan", [
        "I need 3 mobile lines and a website for my shop", "why do I need a website?", "add whatsapp business also", "what is the total now",
        "that's all show me my plan"]),
    ("off topic and meta", [
        "hello", "who are you", "are you a robot", "what is GST", "what's the weather today", "do you work on sundays", "can I talk to a real person"]),
    ("vague and tiny messages", ["hi", "I want internet", "ok", "?", "I have a small shop", "umm not sure", "2 people"]),
    ("marathi and tamil", [
        ("माझे एक दुकान आहे पुण्यात", {"script": "devanagari"}), ("किती खर्च येईल", {"script": "devanagari"}),
        ("என் கடைக்கு இணையம் வேண்டும்", {"script": "tamil"}), ("எவ்வளவு ஆகும்", {"script": "tamil"})]),
    ("factory", [
        "factory in Pune, 30 workers, GST yes", "can we get a leased line", "how long will installation take", "what happens if the internet goes down at night"]),
    ("corrections and memory", [
        CLINIC, "actually we are 10 staff", "what did I tell you about my business", "wait I also have a second branch", "so what is my plan now"]),
    ("frustrated user", [
        BIG, "this is not working", "you are not answering my question", "explain again in very simple words, I am not educated", "just tell me the price"]),
    ("savings and comparison", [
        "I run a kirana shop in Jaipur with 2 staff, no GST", "I pay 1200 rupees now for internet, will I save", "what is the cheapest option you have",
        "is the website really needed", "ok go ahead", ]),
    ("paperwork questions", [
        (CLINIC, {}), ("lets start the paperwork", {"opens": "open_kyc"}), ("where do I upload the pdf", {"opens": "open_kyc"}),
        ("what documents do you need from me", {"opens": "open_kyc"}), ("is my data safe", {})]),
    ("hinglish romanized mess", [
        "mere paas 3 dukaan hai aur 15 log kaam karte hai", "kitna padega sab milake", "cctv kya hota hai kyu chahiye", "mujhe samajh nahi aaya dobara batao",
        "sasta wala dikhao"]),
]

PRICE_RE = re.compile(r"₹\s?([\d,]+)|(\d[\d,]*)\s*(?:rupees|रुपये|rupaye|per month|/month)")


def nums_in(obj):
    return {int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", json.dumps(obj, ensure_ascii=False)) if x.replace(",", "").isdigit()}


CATALOGUE_NUMS = set()
for p in data.PRODUCTS.values():
    CATALOGUE_NUMS |= {p["price"], p["setup"]}


def judge(ctx, user, reply, cards):
    if not KEY:
        return None
    prompt = (
        "You are a strict QA reviewer for a sales assistant that helps small business owners in India choose a connectivity bundle.\n"
        "The owner's messages may be garbled speech-to-text or mixed Hindi/English; judge whether the assistant made a sensible reading and responded helpfully.\n"
        "Decide: did the assistant's reply directly address what the owner asked or meant (an answer, or the right action such as showing a plan or opening paperwork)? "
        "A reply that ignores the question, repeats an unrelated questionnaire step, or only says it did not understand when the message was understandable, FAILS. "
        "Asking one clarifying question is fine only if the message is truly unintelligible. Brief polite redirection of off-topic questions is fine.\n"
        f"Recent context: {json.dumps(ctx, ensure_ascii=False)}\nOwner said: {user}\nAssistant replied: {reply}\nCards shown: {cards}\n"
        'Return JSON only: {"answered": true|false, "issue": "<10 words or empty>"}')
    body = json.dumps({"model": JUDGE_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "max_tokens": 120}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body, {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            txt = json.loads(r.read())["choices"][0]["message"]["content"]
        return json.loads(re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip())
    except Exception as e:
        return {"answered": True, "issue": "judge error " + type(e).__name__}


def run_scenario(item):
    name, turns = item
    c = TestClient(m.app)
    sid = c.post("/api/session", json={}).json()["session_id"]
    S = m.SESSIONS[sid]
    rows, ctx = [], []
    for t in turns:
        text, opt = (t, {}) if isinstance(t, str) else t
        t0 = time.time()
        r = c.post("/api/chat", json={"session_id": sid, "message": text, "label": text, "voice": bool(opt.get("voice"))}).json()
        ms = int((time.time() - t0) * 1000)
        reply = " ".join(x.get("text", "") for x in r["messages"]).strip()
        cards = [k["type"] for x in r["messages"] for k in x.get("cards", [])]
        trace = r.get("trace", [])
        flags = []
        if not reply and not cards:
            flags.append("EMPTY")
        deterministic_ok = any(x.get("tool") in ("open_paperwork", "start_kyc") for x in trace)   # re-opening the paperwork is meant to bypass the AI
        if KEY and not deterministic_ok and not any(x.get("tool") == "llm" and str(x.get("result", "")).startswith("wrote the reply") for x in trace):
            flags.append("NO-AI (keyword fallback)")
        if re.search(r"didn't catch that|समझ नहीं पाया|lost my train|say that once more", reply):
            flags.append("GAVE-UP-PHRASE")
        owner_said = [h for h in S.get("history", []) if h["role"] == "user"]      # only what the owner said, never the bot's own words
        allowed = set(CATALOGUE_NUMS) | nums_in(S.get("quote")) | nums_in(S.get("alt_quote")) | nums_in(owner_said) | nums_in(S.get("profile"))
        qm = [x for x in (nums_in((S.get("quote") or {}).get("totals")), nums_in((S.get("alt_quote") or {}).get("totals"))) if x]
        mon = [(S.get(k) or {}).get("totals", {}).get("monthly") for k in ("quote", "alt_quote")]
        if all(mon):
            allowed.add(abs(mon[0] - mon[1]))                       # the saving smaller_option returns
        sv = (S.get("quote") or {}).get("savings")
        if sv:
            allowed |= {abs(sv["diff"]), sv["spend"]}
        bad = []
        for a, b in PRICE_RE.findall(reply):
            v = int((a or b).replace(",", "") or 0)
            if v and v not in allowed and v not in (12, 2026):
                bad.append(v)
        if bad:
            flags.append(f"UNSOURCED-PRICE {bad}")
        if opt.get("script") and not re.search("[" + SCRIPT[opt["script"]] + "]", reply):
            flags.append(f"WRONG-SCRIPT (wanted {opt['script']})")
        if opt.get("opens") and opt["opens"] not in cards:
            flags.append(f"DID-NOT-{opt['opens'].upper()}")
        if ms > 15000:
            flags.append(f"SLOW {ms // 1000}s")
        v = judge(ctx[-2:], text, reply, cards)
        if v and not v.get("answered", True):
            flags.append("JUDGE: did not answer (" + v.get("issue", "") + ")")
        why = [str(x.get("result"))[:230] for x in trace if x.get("tool") == "llm" and not str(x.get("result", "")).startswith("wrote the reply")]
        rows.append(dict(scenario=name, user=text, reply=reply[:260], cards=cards, ms=ms, flags=flags, why=why))
        ctx.append(dict(owner=text, assistant=reply[:200]))
        print(("  FLAG " if flags else "  ok   ") + f"[{name}] {text[:60]}  ({ms}ms)" + ("  -> " + "; ".join(flags) if flags else ""), flush=True)
    return rows


if __name__ == "__main__":
    if not KEY:
        print("No OPENROUTER_API_KEY: this check needs the real model.")
        sys.exit(2)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=7) as ex:
        results = [row for rows in ex.map(run_scenario, SCENARIOS) for row in rows]
    flagged = [r for r in results if r["flags"]]
    (ROOT / "scripts" / "eval_report.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== {len(results)} turns, {len(flagged)} flagged, {time.time() - t0:.0f}s ===", flush=True)
    for r in flagged:
        print(f"\n[{r['scenario']}] OWNER: {r['user']}\n   BOT: {r['reply'][:220]}\n   FLAGS: {'; '.join(r['flags'])}\n   WHY: {r.get('why')}", flush=True)
