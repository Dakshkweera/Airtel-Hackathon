"""LLM conversation agent (OpenRouter). Active only when OPENROUTER_API_KEY is set.

The model writes the words and decides what to ask next. It cannot invent a product, price or rule:
everything factual comes back from tools backed by the rules engine. If anything goes wrong (no key,
network, bad reply) handle() falls back to the keyword advisor, so the app never goes silent.
"""
import json
import os
import re
import urllib.request

from . import advisor, data, rules
from .i18n import STAGES

MAX_ROUNDS = 5

SYSTEM = """You are Udyam Digital's helper for small business owners in India (shops, clinics, salons, offices, factories).
Talk like a friendly, sharp shop-floor advisor, not a form. Understand free speech: Hindi, English or mixed Hinglish, typos, rambling.
Reply in the language the owner uses (Hindi in Devanagari if they write Hindi). Keep every reply under 60 words, plain and warm. One question at a time.

LANGUAGE
- Detect the language the owner speaks or writes, even when the text is romanized or garbled by speech recognition ("kya aapane kya bola" is Hindi; Devanagari letters spelling English words means they spoke English).
  Reply in THAT language, in its own native script (Hindi and Marathi in Devanagari, Tamil in Tamil script, and so on), keeping product names, rupee prices and words like GST in English. Never ask which language they prefer, just follow them, and switch when they switch.
- Call set_language with the code (en, hi, mr, ta, te, bn, gu, kn, ml) whenever their language differs from STATE.reply_language, or when they ask you to change language.

HARD RULES
- Every product, price, eligibility answer and total MUST come from a tool result. Never state a price, discount, product or rule a tool did not return. Never do arithmetic on prices yourself: call a tool.
- Learn about the owner as you talk and save EVERY fact you hear with save_profile in the same turn (business type, staff, branches, city, whether they have GST, monthly spend today). "Over 20 people" means employees=20; "three shops" means sites=3. Do not re-ask what you already know (see STATE).
- Keep the conversation moving toward a plan. STATE.next_step tells you what to do next: follow it. As soon as business type, staff and branches are known, call recommend_plan so the owner SEES a plan and price, even for big setups. City and GST can be asked after the plan is shown. Never end a turn with a vague "anything else?" question: ask the one question that moves things forward.
- If the owner wants to choose things themselves, use set_products and keep a running cost: after each change tell them the new monthly total from the tool.
- Sell honestly: explain value in the owner's terms (billing and UPI keep working, one bill, one helpline, backup internet). Compare only with what the owner said they pay today. Never claim facts about named competitors. Never invent discounts or urgency. Offer only what the owner's situation needs. If price is the worry call smaller_option. If the owner says a clear no, stop selling, be gracious, offer a reminder.
- If a tool refuses a product, explain the reason in one simple sentence and offer the nearest allowed option the tool gives.
- Factories, 3 or more branches, or a request for a person: also call handoff_to_human so sales can help, BUT a hand-off never blocks the owner. Still show the plan with recommend_plan, and if they want to continue online, go ahead.
- When the owner says continue, yes, ok, go ahead, proceed, "kagaz", paperwork, documents, "let's do it" or anything that means "next step", call start_paperwork immediately (never answer "yes, continue here in chat" instead of acting).
- Documents are uploaded on the PAPERWORK SCREEN, never in the chat. Each document row there has "📷 Photo" and "📎 PDF / file" buttons, and a PDF works. If the owner asks where to upload or submit anything, or cannot find a button, call start_paperwork (it re-opens that screen) and tell them to tap the buttons on each document row.
- Use show_options to display tappable choices when you ask a closed question (business_type, city, gst, spend, counts).
- If asked something unrelated to connectivity and business tools, answer in a sentence and steer back.

PRODUCT IDS (names only; get prices from tools): """


def available():
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def _catalogue_line():
    return "; ".join(f"{p['id']}={p['name']}" for p in data.PRODUCTS.values())


def _tool(name, desc, props=None, required=None):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props or {}, "required": required or []}}}


TOOLS = [
    _tool("save_profile", "Save facts the owner told you. Only include what they actually said.", {
        "business_type": {"type": "string", "enum": ["shop", "salon", "office", "restaurant", "factory", "mobile"],
                          "description": "shop=kirana/retail, salon=salon/pharmacy, office=clinic/CA/coaching/office, restaurant=restaurant or multi-store chain, factory=manufacturer, mobile=wants only a mobile plan"},
        "employees": {"type": "integer"}, "sites": {"type": "integer", "description": "number of shops/branches"},
        "city": {"type": "string"}, "has_gstin": {"type": "boolean"},
        "gstin_status": {"type": "string", "enum": ["Active", "Cancelled", "Suspended"]},
        "monthly_spend": {"type": "integer", "description": "what they pay today for internet and phone, rupees per month"}}),
    _tool("recommend_plan", "Compute the best ready plan for the saved profile. Needs at least business_type; missing staff, branches, city or GST are assumed and listed."),
    _tool("set_products", "Build or edit the owner's own plan. ops: add/remove/set quantity for catalogue product ids. The rules engine refuses anything not allowed and adds required internet automatically.", {
        "ops": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"}, "qty": {"type": "integer", "description": "0 removes"}}, "required": ["id", "qty"]}}}, ["ops"]),
    _tool("get_product_info", "Facts for explaining products to the owner: price, setup, contract, install days, what it is for, and whether they can buy it.", {
        "ids": {"type": "array", "items": {"type": "string"}}}, ["ids"]),
    _tool("check_eligibility", "Check whether the owner may buy these products, with plain reasons and nearest options.", {
        "ids": {"type": "array", "items": {"type": "string"}}}, ["ids"]),
    _tool("smaller_option", "A cheaper arrangement of the current plan, from the catalogue. Never a discount."),
    _tool("show_plan", "Show the owner their final plan card (use when they say that's all for a custom plan)."),
    _tool("show_options", "Show tappable choices for a question you are asking.", {
        "kind": {"type": "string", "enum": ["business_type", "city", "gst", "spend", "counts"]}}, ["kind"]),
    _tool("set_language", "Tell the app which language the owner is using so the microphone, voice and screen follow it.", {
        "code": {"type": "string", "enum": ["en", "hi", "mr", "ta", "te", "bn", "gu", "kn", "ml"]}}, ["code"]),
    _tool("handoff_to_human", "Pass the lead to the sales team with this chat.", {"reason": {"type": "string"}}, ["reason"]),
    _tool("start_paperwork", "The owner agreed to proceed: open the paperwork (KYC) step."),
]


# ------------------------------------------------------------------ transport (patched in tests)
def _http_chat(messages, tools):
    key = os.environ["OPENROUTER_API_KEY"]
    model = os.environ.get("CHAT_MODEL", "anthropic/claude-haiku-5.5")
    body = json.dumps({"model": model, "messages": messages, "tools": tools, "temperature": 0.4, "max_tokens": 400}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body,
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())["choices"][0]["message"]


# ------------------------------------------------------------------ tool implementations
def _summ(q):
    if not q:
        return None
    T = q["totals"]
    return dict(plan=q["plan_name"], monthly_rupees=T["monthly"], setup_rupees=T["setup"], contract_months=T["contract_months"],
                live_in_days=T["expected_days"], estimate=bool(q.get("estimate")),
                items=[dict(id=i["id"], name=i["name"], qty=i["qty"], monthly=i["monthly"], why=i["reason"]) for i in q["items"]],
                refused=[dict(id=r["id"], name=r["name"], reason=r["reason"], nearest=[a["name"] for a in r.get("alternatives", [])]) for r in q["refused"]],
                auto_added=[dict(name=n["name"], for_product=n["for_name"], reason=n["reason"]) for n in q.get("notes", [])],
                savings_vs_today=(q["savings"] if q.get("savings") else None), handoff=q.get("handoff"))


def _state(S):
    p = {k: v for k, v in S["profile"].items() if v is not None and k != "spend_skipped"}
    if not p.get("business_type") and S.get("mode") != "custom":
        nxt = "ask what kind of business they run (call show_options business_type), unless they already described it: then save it"
    elif (p.get("employees") is None or p.get("sites") is None) and S.get("mode") != "custom":
        nxt = "ask how many staff and how many shops/branches (show_options counts), or save it if they said"
    elif not S.get("quote") and S.get("mode") != "custom":
        nxt = "call recommend_plan NOW to show them a plan and price (ask city and GST afterwards)"
    elif S.get("quote") and S.get("stage") == "plan":
        nxt = "plan is on screen: answer their question, handle doubts honestly, and if they agree to proceed call start_paperwork"
    elif S.get("stage") == "kyc":
        nxt = "paperwork is open: help with questions about documents"
    else:
        nxt = "help with what they ask"
    st = dict(next_step=nxt, profile=p, stage=S.get("stage"), mode=S.get("mode"), custom_done=S.get("custom_done"),
              current_quote=_summ(S.get("quote")), has_order=bool(S.get("order")), reply_language=S.get("speech_lang") or S["lang"],
              missing_for_best_quote=[k for k, v in (("business_type", p.get("business_type")), ("employees", p.get("employees")),
                                                      ("sites", p.get("sites")), ("city", p.get("city")), ("has_gstin", p.get("has_gstin"))) if v is None])
    return json.dumps(st, ensure_ascii=False)


class Ctx:
    def __init__(self, S, lang):
        self.S, self.lang, self.cards, self.chips, self.extra, self.done = S, lang, [], None, [], {}


def run_tool(ctx, name, a):
    key = name + json.dumps(a, sort_keys=True)
    if name in ("recommend_plan", "start_paperwork", "show_plan", "smaller_option") and key in ctx.done:
        return ctx.done[key]                      # the model sometimes repeats a call in one turn; do it once
    res = _run_tool(ctx, name, a)
    ctx.done[key] = res
    return res


def _run_tool(ctx, name, a):
    S, lang = ctx.S, ctx.lang
    prof = S["profile"]
    if name == "save_profile":
        facts = {k: v for k, v in a.items() if v is not None}
        if "city" in facts:
            facts["city"] = str(facts["city"]).title()
            facts["city_tier"] = data.city_tier(facts["city"])
        advisor._merge(S, facts)
        S["trace"].append(dict(tool="save_profile", args=json.dumps(facts, ensure_ascii=False), result="saved"))
        return dict(saved=facts, profile={k: v for k, v in prof.items() if v is not None})
    if name == "recommend_plan":
        if not prof.get("business_type"):
            return dict(error="business_type unknown; ask the owner first")
        S["mode"], S["custom_done"] = None, True
        msgs = advisor.recommend(S, lang)
        ctx.extra += [m for m in msgs if m.get("cards") or m.get("chips")]
        for m in msgs:
            m.pop("text", None)
        q = S["quote"]
        S["trace"].append(dict(tool="recommend_plan", args="", result=f"{q['plan_name']} ₹{q['totals']['monthly']:,}/mo"))
        known = [k for k in ("employees", "sites", "city", "has_gstin") if prof.get(k) is None]
        return dict(quote=_summ(q), assumed_unknown=known, note="Values for unknown facts were assumed; ask the owner for them if they matter.")
    if name == "set_products":
        if not S.get("custom") or S.get("mode") != "custom":
            S["mode"], S["custom_done"] = "custom", False
            S["custom"] = dict(items={}, suggested=[], no_suggest=False, refused_seen=[], est_noted=False)
        items = S["custom"]["items"]
        for op in a.get("ops", []):
            pid, qty = op.get("id"), int(op.get("qty", 1))
            if pid not in data.PRODUCTS:
                continue
            if qty <= 0:
                items.pop(pid, None)
            else:
                items[pid] = qty
        q, known = advisor.custom_quote(S, lang)
        S["quote"], S["plan_key"], S["dropped"] = q, "custom", list(q["refused"])
        S["stage"] = "plan" if q["items"] else S["stage"]
        S["trace"].append(dict(tool="set_products", args=",".join(f"{k}×{v}" for k, v in items.items()) or "empty",
                               result=f"₹{q['totals']['monthly']:,}/mo" + (" (estimate)" if q["estimate"] else "")))
        return dict(quote=_summ(q), still_unknown=[k for k, v in (("city", not prof.get("city")), ("staff_count", prof.get("employees") is None),
                                                                     ("gst", prof.get("has_gstin") is None)) if v])
    if name == "get_product_info":
        out = []
        for pid in a.get("ids", []):
            p = data.PRODUCTS.get(pid)
            if not p:
                continue
            pr, _ = advisor.custom_profile(S)
            r = rules.eligibility(pid, pr)
            out.append(dict(id=pid, name=p["name"], monthly_rupees=p["price"], setup_rupees=p["setup"], contract_months=p["contract"],
                            install_days=p["days"], what_it_does=rules.reason_for(pid, pr, 1, lang), can_buy=r is None,
                            why_not=(rules.refusal_text(r[0], r[1], lang) if r else None)))
        return dict(products=out)
    if name == "check_eligibility":
        pr, _ = advisor.custom_profile(S)
        r = rules.check_eligibility(pr, a.get("ids", []), lang)
        S["trace"].append(dict(tool="check_eligibility", args=",".join(a.get("ids", [])), result=f"{len(r['allowed'])} allowed, {len(r['refused'])} refused"))
        return r
    if name == "smaller_option":
        if not S.get("quote"):
            return dict(error="no plan yet")
        sm = rules.smaller_quote(S["profile"], S["quote"], lang)
        if not sm:
            return dict(none=True, note="Already the smallest. Offer to switch extras off.")
        sm["handoff"] = None
        S["alt_quote"] = sm
        ctx.cards.append(dict(type="plan", quote=sm, handoff=False, smaller=True, saves=S["quote"]["totals"]["monthly"] - sm["totals"]["monthly"]))
        ctx.chips = [dict(label="✅ Use this smaller option", hi="✅ यह छोटा विकल्प लें", action="use_smaller"),
                     dict(label="Keep my first plan", hi="पहला प्लान ही रखें", action="keep_plan")]
        S["drop_reason"] = "price"
        S["trace"].append(dict(tool="smaller_option", args="", result=f"₹{sm['totals']['monthly']:,}/mo"))
        return dict(smaller=_summ(sm), saves_per_month=S["quote"]["totals"]["monthly"] - sm["totals"]["monthly"])
    if name == "show_plan":
        if S.get("mode") == "custom" and not S.get("custom_done") and S.get("custom", {}).get("items"):
            missing = advisor.custom_next_slot(prof)
            if missing:
                return dict(error=f"still need: {missing}; ask the owner first")
            msgs = advisor.custom_finish(S, lang)
            ctx.extra += [dict(cards=m.get("cards", []), chips=m.get("chips")) for m in msgs if m.get("cards")]
            return dict(shown=True, quote=_summ(S["quote"]))
        if S.get("quote"):
            ctx.cards.append(advisor.card_for(S, S["quote"]))
            return dict(shown=True, quote=_summ(S["quote"]))
        return dict(error="no plan yet")
    if name == "show_options":
        kind = a.get("kind")
        if kind == "counts":
            ctx.cards.append(dict(type="counts", staff=5, sites=1))
        ctx.chips = advisor._chips(kind, lang)
        S["asked"] = kind
        return dict(shown=kind)
    if name == "set_language":
        code = a.get("code")
        if code in ("en", "hi", "mr", "ta", "te", "bn", "gu", "kn", "ml"):
            S["speech_lang"] = code
            S["lang"] = "hi" if code in ("hi", "mr") else "en"      # screen text exists in English and Hindi
            ctx.lang = S["lang"]
            S["trace"].append(dict(tool="set_language", args=code, result="mic, voice and screen follow"))
            return dict(ok=True, now_replying_in=code)
        return dict(error="unsupported language")
    if name == "handoff_to_human":
        advisor.make_lead(S, a.get("reason", "owner asked"))
        ctx.cards.append(dict(type="handoff", reason=a.get("reason", "")))
        return dict(ok=True)
    if name == "start_paperwork":
        if S.get("mode") == "custom" and not S.get("custom_done"):
            missing = advisor.custom_next_slot(prof)
            if missing:
                return dict(error=f"still need: {missing}")
            advisor.custom_finish(S, lang)
        if not S.get("quote") or not S["quote"].get("items"):
            return dict(error="no plan yet")
        S["stage"] = "kyc"
        ctx.cards.append(dict(type="open_kyc"))
        S["trace"].append(dict(tool="start_kyc", args="", result="consent first"))
        return dict(ok=True)
    return dict(error="unknown tool")


# ------------------------------------------------------------------ the loop
def run(S, text, lang):
    """Return a list of bot messages, or None to fall back to the keyword advisor."""
    if not available() or not text:
        return None
    ctx = Ctx(S, lang)
    hist = [dict(role=("assistant" if h["role"] == "bot" else "user"), content=h["text"]) for h in S.get("history", [])[-18:] if h.get("text")]
    if not hist or hist[-1]["role"] != "user" or hist[-1]["content"] != text:
        hist.append(dict(role="user", content=text))
    msgs = [dict(role="system", content=SYSTEM + _catalogue_line()),
            dict(role="system", content="STATE (truth, from the server): " + _state(S))] + hist
    try:
        for _ in range(MAX_ROUNDS):
            try:
                m = _http_chat(msgs, TOOLS)
            except Exception:                       # one quick retry: transient errors should not cost the conversation
                m = _http_chat(msgs, TOOLS)
            calls = m.get("tool_calls") or []
            if not calls:
                reply = (m.get("content") or "").strip()
                if not reply:
                    return None
                return _assemble(S, ctx, reply)
            msgs.append(dict(role="assistant", content=m.get("content") or "", tool_calls=calls))
            for c in calls:
                try:
                    args = json.loads(c["function"].get("arguments") or "{}")
                except Exception:
                    args = {}
                res = run_tool(ctx, c["function"]["name"], args)
                msgs.append(dict(role="tool", tool_call_id=c["id"], content=json.dumps(res, ensure_ascii=False)))
        return None
    except Exception as e:  # network, bad key, malformed reply: fall back, never go silent
        S["trace"].append(dict(tool="llm", args="", result=f"unavailable ({type(e).__name__}); keyword advisor used"))
        return None


def _assemble(S, ctx, reply):
    S["trace"].append(dict(tool="llm", args=os.environ.get("CHAT_MODEL", "anthropic/claude-haiku-5.5"), result="wrote the reply; prices came from tools"))
    out = [dict(text=reply)]
    cards = list(ctx.cards)
    chips = ctx.chips
    for m in ctx.extra:
        cards += m.get("cards", [])
        chips = chips or m.get("chips")
    seen = set()
    uniq = []
    for c in cards:                                   # one plan card per kind at most
        k = c["type"] + str(c.get("smaller"))
        if k in seen and c["type"] in ("plan", "handoff", "open_kyc"):
            continue
        seen.add(k)
        uniq.append(c)
    if uniq:
        out.append(dict(cards=uniq))
    if not chips and S.get("stage") == "kyc":
        chips = [advisor.OPEN_KYC_CHIP]
    if not chips:
        q = S.get("quote")
        if q and q.get("items") and S.get("stage") == "plan" and (S.get("custom_done") or S.get("mode") != "custom"):
            go = dict(label="🌐 Continue online anyway", hi="🌐 फिर भी ऑनलाइन आगे बढ़ें", action="start_kyc") if q.get("handoff") \
                else dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")
            chips = [go, advisor.CHIP("💬 Too costly", "💬 बहुत महँगा", "too costly")]
            if not q.get("handoff"):
                chips.append(advisor.CHIP("🙋 Talk to a person", "🙋 किसी से बात करें", "talk to a person"))
        elif S.get("mode") == "custom" and not S.get("custom_done") and q and q.get("items"):
            chips = [advisor.SHOW_CHIP]
        elif S["profile"].get("business_type") and not q and S.get("mode") != "custom":
            chips = [advisor.CHIP("📋 Show me a plan now", "📋 अभी प्लान दिखाइए", "show me a plan now")]
    out[-1]["chips"] = chips or []
    return out
