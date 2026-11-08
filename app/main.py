"""FastAPI app. Prototype-grade: in-memory sessions, one process. Run: uvicorn app.main:app --port 8000"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import advisor, data, kyc, orders, rules, tts
from .i18n import KYC_MSG, STAGES, pick, t
from .scenarios import SCENARIOS

ROOT = Path(__file__).resolve().parent.parent
env = ROOT / ".env"
if env.exists() and not os.environ.get("UD_NO_DOTENV"):  # tiny .env reader, no dependency (tests skip it)
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

app = FastAPI(title="Udyam Digital")
STORE = Path(os.environ.get("UD_SESSION_STORE") or (ROOT / "data" / "sessions.json"))
SESSIONS = {}
try:  # conversation memory survives a restart
    SESSIONS = json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else {}
except Exception:
    SESSIONS = {}


TURN_LOG = Path(os.environ.get("UD_TURN_LOG") or (ROOT / "data" / "turn_log.jsonl"))


def log_turn(S, text, msgs, ms):
    """One line per owner message: was the AI used, did it fall back, how long. Lets problems be found without anyone reporting them."""
    try:
        llm_ok = any(t.get("tool") == "llm" and str(t.get("result", "")).startswith("wrote the reply") for t in S.get("trace", []))
        fell_back = bool(text) and not llm_ok and bool(os.environ.get("OPENROUTER_API_KEY"))
        reply = " ".join((m.get("text") or "") for m in msgs)[:300]
        row = dict(ts=datetime.now().isoformat(timespec="seconds"), sid=S["id"], user=(text or "")[:200], llm_answered=llm_ok,
                   fell_back=fell_back, ms=ms, reply=reply, trace=[t.get("tool") + ":" + str(t.get("result"))[:60] for t in S.get("trace", [])][:6])
        with open(TURN_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def save():
    try:
        STORE.write_text(json.dumps(SESSIONS, default=str), encoding="utf-8")
    except Exception:
        pass


@app.middleware("http")
async def persist(request, call_next):
    resp = await call_next(request)
    if request.method == "POST":
        save()
    return resp

CONSENT_VERSION = "v1.0"


def sess(sid):
    S = SESSIONS.get(sid)
    if not S:
        raise HTTPException(404, "session not found")
    return S


def new_session(lang="en"):
    S = dict(id=uuid.uuid4().hex[:12], lang=lang, history=[], profile=advisor.new_profile(), wanted=[], trace=[], stage="chat",
             asked=None, quote=None, plan_key=None, dropped=[], consent=None, order=None, lead=None,
             kyc=dict(docs={}, has_gstin=None, gst_record=None, udyam_record=None, gstin=None, gst_check=None,
                      udyam_check=None, sources={}), created=datetime.now().isoformat(timespec="seconds"))
    SESSIONS[S["id"]] = S
    return S


def remember(S, role, text):
    if text:
        S.setdefault("history", []).append(dict(role=role, text=text))


def preview(S):
    """Live plan for the side panel. Before the plan is final, missing facts are assumed and listed."""
    p = S["profile"]
    if S.get("mode") == "custom" and not S.get("custom_done"):       # custom plan still being built
        q = S.get("quote")
        if not q or not q["items"]:
            return None
        pending = [k for k, miss in (("city", not p.get("city")), ("staff", p.get("employees") is None),
                                     ("gst", p.get("has_gstin") is None)) if miss]
        return dict(quote=q, assumed=[], pending=pending, final=False)
    if S.get("quote") and S["quote"].get("items") is not None and S["stage"] != "chat":
        return dict(quote=S["quote"], assumed=[], final=True)
    if not p.get("business_type"):
        return None
    pr, assumed = dict(p), []
    if pr.get("employees") is None:
        pr["employees"] = 5; assumed.append("staff")
    if pr.get("sites") is None:
        pr["sites"] = 1; assumed.append("sites")
    if not pr.get("city"):
        pr["city_tier"] = 1; assumed.append("city")
    if pr.get("has_gstin") is None:
        pr["has_gstin"] = False; assumed.append("gst")
    q = rules.recommend_plan(pr, S["lang"])
    return dict(quote=q, assumed=assumed, final=False,
                values=dict(staff=pr["employees"], sites=pr["sites"], tier=pr.get("city_tier")))


def needs_for(S):
    return advisor.custom_tiles(S, S["lang"]) if (S.get("mode") == "custom" and not S.get("custom_done")) else None


def reply(S, msgs, **extra):
    return dict(speech_lang=S.get("speech_lang") or S["lang"], needs=needs_for(S), messages=msgs, lang=S["lang"], stage=S["stage"], trace=S["trace"], preview=preview(S),
                profile={k: v for k, v in S["profile"].items() if v is not None}, **extra)


class SessionIn(BaseModel):
    language: str = "en"


class LangIn(BaseModel):
    session_id: str
    language: str
    speech_lang: str = ""


class ChatIn(BaseModel):
    session_id: str
    message: str = ""
    label: str = ""
    voice: bool = False
    payload: dict | None = None


class QuoteIn(BaseModel):
    session_id: str
    items: dict[str, int]


class SidIn(BaseModel):
    session_id: str


class ConsentIn(BaseModel):
    session_id: str
    version: str = CONSENT_VERSION
    accept: bool = True


class GstinIn(BaseModel):
    session_id: str
    gstin: str = ""
    no_gst: bool = False


class UdyamIn(BaseModel):
    session_id: str
    udyam_number: str


@app.post("/api/session")
def api_session(b: SessionIn):
    S = new_session("hi" if b.language == "hi" else "en")
    msgs = advisor.greeting(S)
    remember(S, "bot", msgs[0]["text"])
    return reply(S, msgs, session_id=S["id"])


@app.post("/api/lang")
def api_lang(b: LangIn):
    S = sess(b.session_id)
    S["lang"] = "hi" if b.language == "hi" else "en"
    S["lang_locked"] = True
    if b.speech_lang in tts.VOICES:
        S["speech_lang"] = b.speech_lang
    elif b.language in tts.VOICES:
        S["speech_lang"] = b.language
    # re-render the current plan in the new language so product reasons switch too
    q = None
    if S.get("mode") == "custom" and not S.get("custom_done") and S.get("custom"):
        q, _ = advisor.custom_quote(S, S["lang"])
        S["quote"] = q
    elif S.get("quote") and S["profile"].get("business_type") or (S.get("quote") and S.get("plan_key") == "custom"):
        key = S["plan_key"]
        if key in ("custom",):
            q = rules.build_quote(S["profile"], S["quote"]["quantities"], S["lang"], "custom")
        else:
            q = rules.build_quote(S["profile"], S["quote"]["quantities"], S["lang"], key)
        q["handoff"] = S["quote"].get("handoff")
        q["refused"] = _merge_refused(S, q)
        S["quote"] = q
    return dict(lang=S["lang"], quote=q, needs=needs_for(S))


@app.post("/api/chat")
def api_chat(b: ChatIn):
    S = sess(b.session_id)
    remember(S, "user", b.label or b.message)
    t_start = datetime.now()
    was_locked = S.get("lang_locked")
    if b.voice:                      # a speech transcript in the wrong script must never flip the app's language
        S["lang_locked"] = True
    try:
        msgs = advisor.handle(S, b.message, b.payload)
    finally:
        if b.voice:
            S["lang_locked"] = was_locked
    log_turn(S, b.message, msgs, int((datetime.now() - t_start).total_seconds() * 1000))
    S["_last_chips"] = next((m["chips"] for m in reversed(msgs) if m.get("chips")), [])
    for msg in msgs:
        remember(S, "bot", msg.get("text"))
    for msg in msgs:
        for c in msg.get("cards", []):
            if c["type"] == "tracker":
                c["order"] = orders.view(S["order"], S["lang"])
    return reply(S, msgs)


@app.get("/api/session/{sid}")
def api_restore(sid: str):
    """Bring a returning owner back to where they were: history, profile, plan, order."""
    S = SESSIONS.get(sid)
    if not S:
        raise HTTPException(404, "session not found")
    lang = S["lang"]
    resume = []
    if S.get("order"):
        resume.append(dict(cards=[dict(type="tracker", order=orders.view(S["order"], lang))],
                           chips=[dict(label="📦 Where is my order?", hi="📦 मेरा ऑर्डर कहाँ है?", text="Where is my order?")]))
    elif S.get("mode") == "custom" and not S.get("custom_done"):
        m = dict(cards=[dict(type="needs", tiles=advisor.custom_tiles(S, lang))])
        if S.get("asked"):
            m2, chips = advisor._ask(S["asked"], lang)
            m2["chips"] = chips
            resume.extend([m, m2])
        else:
            m["chips"] = [advisor.SHOW_CHIP] if S["custom"]["items"] else []
            resume.append(m)
    elif S.get("asked"):
        m, chips = advisor._ask(S["asked"], lang)
        m["chips"] = chips
        resume.append(m)
    elif S.get("quote") and S["quote"].get("items"):
        resume.append(dict(cards=[advisor.card_for(S, S["quote"])],
                           chips=[dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")]))
    return dict(needs=needs_for(S), history=S.get("history", []), resume=resume, lang=lang, stage=S["stage"], trace=[],
                profile={k: v for k, v in S["profile"].items() if v is not None}, preview=preview(S))


def _merge_refused(S, q):
    have = {r["id"] for r in q["refused"]}
    return q["refused"] + [r for r in S.get("dropped", []) if r["id"] not in have and r["id"] not in q["quantities"]]


@app.post("/api/quote")
def api_quote(b: QuoteIn):
    S = sess(b.session_id)
    q = rules.build_quote(S["profile"], b.items, S["lang"], S.get("plan_key") or "custom")
    q["refused"] = _merge_refused(S, q)
    q["handoff"] = (S.get("quote") or {}).get("handoff")
    S["quote"] = q
    return dict(quote=q)


# ---------------------------------------------------------------------- KYC
def need_consent(S):
    if not S["consent"]:
        raise HTTPException(403, "consent required before any document step")


@app.get("/api/kyc/state")
def kyc_state(session_id: str):
    S = sess(session_id)
    K = S["kyc"]
    has_gst = rules.gst_ok(S["profile"]) or S["profile"].get("has_gstin")
    return dict(consent=S["consent"], consent_version=CONSENT_VERSION, has_gstin=bool(has_gst),
                typed_gstin=S.get("typed_gstin"),
                docs={k: dict(ok=True) for k in K["docs"]}, samples=[dict(id=s["id"], label=s["label"], issue=s["issue"]) for s in data.SAMPLES],
                gst=_gst_view(K), udyam=K.get("udyam_check"))


def _gst_view(K):
    c = K.get("gst_check")
    if not c:
        return None
    return {k: v for k, v in c.items() if k not in ("gstin",)}


@app.post("/api/consent")
def api_consent(b: ConsentIn):
    S = sess(b.session_id)
    if b.accept:
        S["consent"] = dict(version=b.version, purpose="Check your business and start your service",
                            accepted_at=datetime.now().isoformat(timespec="seconds"))
    else:
        S["consent"] = None
    return dict(consent=S["consent"])


@app.post("/api/consent/withdraw")
def api_withdraw(b: SidIn):
    S = sess(b.session_id)
    S["consent"] = None
    S["kyc"] = dict(docs={}, has_gstin=None, gst_record=None, udyam_record=None, gstin=None, gst_check=None, udyam_check=None, sources={})
    S["typed_gstin"] = None
    return dict(ok=True, message=pick(("Your paperwork data has been deleted.", "आपका कागज़ी डेटा मिटा दिया गया है।"), S["lang"]))


@app.post("/api/kyc/gstin")
def kyc_gstin(b: GstinIn):
    S = sess(b.session_id)
    need_consent(S)
    K = S["kyc"]
    lang = S["lang"]
    if b.no_gst:
        K.update(has_gstin=False, gst_record=None, gstin=None, gst_check=None)
        S["profile"]["has_gstin"] = False
        S["profile"]["gstin_status"] = None
        return dict(ok=True, no_gst=True)
    res = kyc.check_gstin(b.gstin, lang)
    K["has_gstin"] = True  # the owner says they have one; a typo must still be reported, not skipped
    K["gst_check"] = {k: v for k, v in res.items()}
    out = {k: v for k, v in res.items() if k != "gstin"}
    out["plan_changed"] = False
    if res.get("legal_name"):  # registry found: keep record for cross-checks
        K["gst_record"] = data.GSTIN_REG[res["gstin"]]
        K["gstin"] = res["gstin"]
        K["has_gstin"] = True
        S["profile"]["has_gstin"] = True
        S["profile"]["gstin_status"] = res["status"]
        if res["status"] != "Active":
            q = rules.recommend_plan(S["profile"], lang)
            q["handoff"] = rules.needs_handoff(S["profile"])
            S["quote"], S["plan_key"], S["dropped"] = q, q["plan_key"], list(q["refused"])
            out.update(plan_changed=True, quote=q, chat=t("kyc_blocked_gst", lang))
        elif S["profile"].get("gstin_status") != "Active":
            S["profile"]["gstin_status"] = "Active"
    else:
        K["gst_record"] = None
        K["gstin"] = None
    return out


@app.post("/api/kyc/udyam")
def kyc_udyam(b: UdyamIn):
    S = sess(b.session_id)
    need_consent(S)
    res = kyc.check_udyam(b.udyam_number, S["lang"])
    S["kyc"]["udyam_check"] = {k: v for k, v in res.items()}
    S["kyc"]["udyam_record"] = data.UDYAM_REG.get(res.get("udyam_number")) if res["ok"] else None
    return res


@app.post("/api/kyc/upload")
async def kyc_upload(session_id: str = Form(...), doc_type: str = Form(...), sample: str = Form(""),
                     file: UploadFile | None = File(None)):
    S = sess(session_id)
    need_consent(S)
    if doc_type not in kyc.DOC_TYPES:
        raise HTTPException(400, "unknown doc_type")
    img, sample_key = b"", sample or None
    if sample_key:
        p = data.DOC_DIR / sample_key
        if not p.exists():
            raise HTTPException(404, "sample not found")
        img = p.read_bytes()
    elif file is not None:
        img = await file.read()
    else:
        raise HTTPException(400, "no file")
    fields, source = kyc.read_document(img, doc_type, sample_key)
    fields["doc_type"] = doc_type
    del img  # retention: the image is never stored; only the extracted fields live in the session
    K = S["kyc"]
    K["docs"][doc_type] = fields
    K["sources"][doc_type] = source
    return dict(ok=True, doc_type=doc_type, source=source, low_confidence=(fields.get("confidence") or 0) < kyc.LOW_CONFIDENCE)


@app.post("/api/kyc/remove")
def kyc_remove(session_id: str = Form(...), doc_type: str = Form(...)):
    S = sess(session_id)
    S["kyc"]["docs"].pop(doc_type, None)
    return dict(ok=True)


@app.post("/api/kyc/verify")
def kyc_verify(b: SidIn):
    S = sess(b.session_id)
    need_consent(S)
    K = S["kyc"]
    lang = S["lang"]
    has_gst = bool(K.get("has_gstin"))
    state = dict(docs=K["docs"], has_gstin=has_gst, gst_record=K.get("gst_record"), udyam_record=K.get("udyam_record"), gstin=K.get("gstin"))
    res = kyc.verify(state, lang)
    pre = []
    L = lambda en, hi: hi if lang == "hi" else en
    pre.append(dict(id="consent", label=L("Consent recorded", "सहमति दर्ज"), passed=True, review=False, message=pick(KYC_MSG["ok"], lang), doc=None))
    g = K.get("gst_check")
    if has_gst and g is not None:
        if g["ok"]:
            pre.append(dict(id="gstin", label=L("GST number is valid and active", "GST नंबर सही और चालू"), passed=True, review=False,
                            message=g.get("legal_name", ""), doc=None))
        else:
            warn = g.get("stage") == "status"
            pre.append(dict(id="gstin", label=L("GST number is valid and active", "GST नंबर सही और चालू"), passed=False, review=False,
                            message=g["message"], doc=None, severity="warn" if warn else "error", field="gstin"))
    elif has_gst:
        pre.append(dict(id="gstin", label=L("GST number is valid and active", "GST नंबर सही और चालू"), passed=False, review=False,
                        message=pick(KYC_MSG["gst_format"], lang), doc=None, field="gstin"))
    u = K.get("udyam_check")
    if u is not None and u["ok"]:
        pre.append(dict(id="udyam", label=L("Udyam number found", "Udyam नंबर मिला"), passed=True, review=False, message=u.get("name", ""), doc=None))
    else:
        pre.append(dict(id="udyam", label=L("Udyam number found", "Udyam नंबर मिला"), passed=False, review=False,
                        message=(u or {}).get("message") or pick(KYC_MSG["udyam_notfound"], lang), doc=None, field="udyam"))
    checks = pre + res["checks"]
    blocking_fail = [c for c in checks if c["passed"] is False and c.get("severity") != "warn"]
    review = [c for c in checks if c.get("review")]
    overall = "fail" if blocking_fail else ("review" if review else "pass")
    S["kyc"]["status"] = overall
    S["stage"] = "kyc"
    S["trace"] = [dict(tool="kyc.verify", args=f"{len(K['docs'])} docs", result=overall)]
    if overall == "review":
        advisor.make_lead(S, "KYC needs human review")
    return dict(checks=checks, overall=overall, trace=S["trace"])


# ---------------------------------------------------------------------- orders
@app.post("/api/order")
def api_order(b: SidIn):
    S = sess(b.session_id)
    if S["kyc"].get("status") != "pass":
        raise HTTPException(409, "paperwork has not passed")
    if not S.get("quote") or not S["quote"]["items"]:
        raise HTTPException(409, "no quote")
    if not S.get("order"):
        S["order"] = orders.create(S, S["quote"])
        S["stage"] = "order"
    S["trace"] = [dict(tool="create_order", args=S["order"]["id"], result=f"expected {S['order']['expected_date']}")]
    return dict(order=orders.view(S["order"], S["lang"]), message=t("order_placed", S["lang"]), trace=S["trace"])


@app.get("/api/order/{oid}")
def api_get_order(oid: str):
    for S in SESSIONS.values():
        if S.get("order") and S["order"]["id"] == oid:
            return orders.view(S["order"], S["lang"])
    raise HTTPException(404)


@app.post("/api/order/{oid}/advance")
def api_advance(oid: str):
    for S in SESSIONS.values():
        if S.get("order") and S["order"]["id"] == oid:
            orders.advance(S["order"])
            v = orders.view(S["order"], S["lang"])
            return dict(order=v, message=t("stage_update", S["lang"], stage=v["stages"][v["stage"]]))
    raise HTTPException(404)


# ---------------------------------------------------------------------- staff + demo
SEED_LEADS = [
    dict(name="Bansal Restaurants, Delhi", reason="4 branches · quote unanswered 72h", score=88, summary="restaurant · 20 staff · 4 sites · quote ₹20,780/mo", sample=True),
    dict(name="Kulkarni Precision Works, Pune", reason="factory · KYC pending 3 days", score=81, summary="factory · 30 staff · 1 site · quote ₹16,025/mo", sample=True),
    dict(name="Verma Kirana, Bhopal", reason="payment failed", score=44, summary="shop · 2 staff · 1 site · quote ₹1,497/mo", sample=True),
]


@app.get("/api/staff/leads")
def staff_leads():
    out = [dict(l) for l in SEED_LEADS]
    for S in SESSIONS.values():
        l = S.get("lead")
        if l:
            out.append(dict(name=f"Chat {S['id'][:6]}", reason=l["reason"], score=l["score"], summary=l["summary"]))
        elif S.get("quote") and not S.get("order") and S["stage"] in ("kyc", "declined", "plan") and S["quote"]["items"]:
            sc = advisor._score(S)
            out.append(dict(name=f"Chat {S['id'][:6]}", reason={"kyc": "KYC pending", "declined": "declined, stop selling", "plan": "quote not accepted yet"}[S["stage"]],
                            score=sc, summary=f"{S['profile'].get('business_type')} · quote ₹{S['quote']['totals']['monthly']:,}/mo"))
    return sorted(out, key=lambda x: -x["score"])


@app.get("/api/kyc/samples-detail")
def samples_detail():
    return data.SAMPLES


@app.get("/api/debug/turns")
def debug_turns(n: int = 60, only_problems: bool = False):
    """Recent owner messages and how they were handled. Problems = the AI did not answer, so a keyword fallback did."""
    rows = []
    try:
        for line in TURN_LOG.read_text(encoding="utf-8").splitlines()[-500:]:
            rows.append(json.loads(line))
    except Exception:
        pass
    if only_problems:
        rows = [r for r in rows if r.get("fell_back")]
    return rows[-n:]


@app.get("/api/scenarios")
def api_scenarios():
    return SCENARIOS


class TtsIn(BaseModel):
    text: str
    lang: str = "en"


@app.post("/api/tts")
async def api_tts(b: TtsIn):
    """Neural voice. 503 means: use the browser's own voice instead."""
    if tts.edge_tts is None or not b.text.strip():
        raise HTTPException(503, "neural voice unavailable")
    gen = tts.stream(b.text[:600], b.lang)
    try:
        first = await gen.__anext__()
    except Exception:
        raise HTTPException(503, "neural voice unreachable")

    async def body():
        yield first
        async for c in gen:
            yield c
    return StreamingResponse(body(), media_type="audio/mpeg")


@app.get("/api/health")
def health():
    return dict(ok=True, products=len(data.PRODUCTS), llm=bool(os.environ.get("OPENROUTER_API_KEY")), neural_voice=tts.edge_tts is not None)


app.mount("/sample-docs", StaticFiles(directory=str(data.DOC_DIR)), name="sample-docs")


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/staff")
def staff_page():
    return FileResponse(ROOT / "static" / "staff.html")


app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
