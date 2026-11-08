"""The advisor: a guided conversation. It extracts facts from what the owner types, asks one question at a
time, and gets every product, price and 'no' from the rules engine.

If OPENROUTER_API_KEY is set, an LLM is also used to understand free text the keyword parser could not
(it only extracts facts as JSON; it never writes prices or decides eligibility).
"""
import json
import os
import re
import urllib.request

from . import data, rules
from .i18n import BTYPE_LABEL, T, pick, t

DEVANAGARI = re.compile(r"[ऀ-ॿ]")
INTERNET = {"P01", "P02", "P03", "P04", "P05"}

CITY_HI = {"इंदौर": "indore", "मुंबई": "mumbai", "दिल्ली": "delhi", "जयपुर": "jaipur", "लखनऊ": "lucknow", "पुणे": "pune",
           "भोपाल": "bhopal", "चेन्नई": "chennai", "कोलकाता": "kolkata", "हैदराबाद": "hyderabad", "बेंगलुरु": "bengaluru",
           "अहमदाबाद": "ahmedabad", "नागपुर": "nagpur", "पटना": "patna", "सूरत": "surat"}
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
           "single": 1, "a": 1}

BTYPE_RULES = [
    ("restaurant", r"restaurant|chain|hotel|caf[eé]|multi[- ]?store|outlets?|रेस्टोरेंट|होटल|रेस्तरां"),
    ("factory", r"factory|manufactur|plant\b|workshop|कारखान|फैक्ट्री|फैक्टरी"),
    ("office", r"clinic|doctor|dental|dentist|hospital|\bca\b|chartered|accountant|lawyer|advocate|coaching|tuition|school|institute|office|consult|क्लिनिक|डॉक्टर|कोचिंग|दफ्तर|दफ़्तर|ऑफिस|वकील"),
    ("salon", r"salon|parlou?r|pharmacy|medical store|chemist|सैलून|पार्लर|फार्मेसी|मेडिकल"),
    ("shop", r"kirana|shop|store|dukaan|grocery|retail|general store|दुकान|किराना"),
]
WANTED_RULES = [
    ("P15", r"whats\s?app\s*business|whatsapp api|व्हाट्सएप|व्हाट्सऐप"),
    ("P23", r"cctv|camera|सीसीटीवी|कैमरा"),
    ("P01", r"\b1\s?g\b|1\s?gbps|gigabit|fibre 1g|fiber 1g"),
    ("P05", r"leased line|लीज्ड"),
    ("P10", r"sd[- ]?wan"),
    ("P19", r"\bpos\b|point of sale|billing machine"),
    ("P17", r"cloud backup|\bbackup\b"),
    ("P18", r"website|domain|वेबसाइट"),
    ("P22", r"secure wi-?fi"),
]
PERSON = r"(talk|speak|connect).{0,20}(person|human|someone|agent|expert|sales|executive)|call me|sales (team|person)|real person|insaan|इंसान|किसी से बात|बात करनी|एजेंट|सेल्स"
COSTLY = r"costly|expensive|too much|\bprice\b|pricey|mehng|महंग|ज़्यादा|ज्यादा|zyada|afford|budget"
CHEAPER = r"cheaper|cheap\b|sasta|सस्त|elsewhere|other (provider|company)|competitor|jio|\bvi\b|tata"
NOTNEEDED = r"not needed|don'?t need|do not need|no need|zarurat nahi|जरूरत नहीं|ज़रूरत नहीं"
THINK = r"\bthink\b|later|soch|सोच|बाद में|remind|will see|let me see"
DECLINE = r"no thanks|not interested|nahi chahiye|नहीं चाहिए|don'?t want|leave it|drop it|रहने दो"
GO = r"^(yes|ok|okay|continue|proceed|start|go ahead|sure|haan|haanji|ha|हाँ|हां|आगे|ठीक है|चलो)\b|paper|document|docs\b|kyc|upload|submit|कागज|दस्तावेज"
ORDER = r"order|status|track|where is|ऑर्डर|कहाँ|कहां|स्टेटस"
CUSTOM = r"build (my|your) own|custom (plan|bundle)|my own plan|own plan|pick (the )?products|choose (the )?products|खुद.{0,12}प्लान|अपना (प्लान|बंडल)|कस्टम"
EXPLAIN = r"\bwhy\b|what is|what does|do i need|is it needed|क्यों|क्या है|क्या होता|kyun|kya hai|zarurat kya"
REMOVE = r"remove|drop|delete|take out|without|cancel|हटा|हटाओ|नहीं चाहिए"
CUSTOM_CHIP = dict(label="🛠️ Build my own plan", hi="🛠️ अपना प्लान खुद बनाएँ", action="custom")
SHOW_CHIP = dict(label="✅ That's all, show my plan", hi="✅ बस, मेरा प्लान दिखाएँ", action="custom_done")
NEED_RULES = [  # most specific first
    ("P22", r"secure wi-?fi|wi-?fi security"),
    ("P09", r"failover|backup (internet|line|net)|internet backup|standby"),
    ("P17", r"cloud backup|\bbackup\b|data backup|बैकअप"),
    ("P23", r"cctv|camera|सीसीटीवी|कैमरा"),
    ("P15", r"whats\s?app|व्हाट्सएप|व्हाट्सऐप"),
    ("P10", r"sd[- ]?wan"),
    ("P05", r"leased line|लीज्ड"),
    ("P08", r"iot sim"),
    ("P21", r"iot gateway"),
    ("P19", r"\bpos\b|point of sale|billing machine|billing software"),
    ("P25", r"accounting|tally|gst filing|हिसाब"),
    ("P18", r"website|domain|वेबसाइट"),
    ("P20", r"security|antivirus|virus|firewall|सुरक्षा|एंटीवायरस"),
    ("P16", r"e-?mail|mail id|ईमेल"),
    ("P12", r"video (call|meeting|conferenc)|conferenc|meeting"),
    ("P11", r"telephony|cloud (phone|calling)|ivr|call centre|call center"),
    ("P07", r"mobile|sim\b|postpaid|phone line|मोबाइल|सिम"),
    ("P04", r"air\s?fiber|airfibre|5g|एयरफाइबर"),
    ("P01", r"\b1\s?g\b|gigabit|1\s?gbps"),
    ("INTERNET", r"internet|fib(re|er)|broadband|wi-?fi|इंटरनेट|ब्रॉडबैंड|वाईफाई|net connection"),
]
QTY_RULES = {"P07": r"(\d+)\s*(?:mobile|sim|line|phone)", "P16": r"(\d+)\s*(?:e-?mail|mail|id|account)",
             "P20": r"(\d+)\s*(?:computer|laptop|pc|licen[cs]e|device)", "P23": r"(\d+)\s*(?:camera|cctv)", "P11": r"(\d+)\s*(?:seat|line|user)"}
SUGGEST = {"INTERNET": ["P09"], "P16": ["P20", "P17"], "P18": ["P15"], "P19": ["P07"], "P23": []}
PRICEQ = r"how much|price of|\bprice\b|cost of|kitna|कितना|कीमत|रेट|charges|\brate\b"
GREET = r"^(hello|hi+|hey+|namaste|namaskar|ok|okay|yes|no|help|test|start|hola|हेलो|हाय|नमस्ते|नमस्कार)(\b|$)"
NEEDVERB = r"\b(need|want|require|looking for|add|get me|chahiye|chahie)\b|चाहिए|चाहिये|लेना है|दीजिए"
GO_NOW = r"^(yes|ok|okay|continue|proceed|start|go ahead|sure|haan|haanji|ha|हाँ|हां|आगे|ठीक है|चलो|theek hai|thik hai|aage|agey|shuru)" + chr(92) + r"b|aage badh|आगे बढ़|let" + chr(39) + r"?s (go|do it|start|proceed)|go ahead|शुरू करो|shuru kar|proceed|paperwork|kyc|कागज़ी कार्रवाई"
UPLOADQ = r"pdf|upload|submit|document|docs|paper|photo|picture|scan|certificate|aadhaar|aadhar|pan card|button|option|where|how do i|कहां|कहाँ|कैसे|सबमिट|अपलोड|पीडीएफ|पीडीफ|दस्तावेज|कागज|डॉक्यूमेंट|फोटो|फ़ोटो|बटन|ऑप्शन|विकल्प|दिख|दिखा"
OPEN_KYC_CHIP = dict(label="📄 Open paperwork", hi="📄 कागज़ात खोलें", action="start_kyc")
RECALL = r"what (did|have) i (say|said|tell|told)|what do you (know|remember)|do you remember|remind me what|मैंने क्या बताया|क्या याद|याद है|क्या पता है"
SKIP = r"skip|no idea|don'?t know|not sure|छोड़|नहीं पता|pass"

CHIP = lambda label_en, label_hi, text: dict(label=label_en, hi=label_hi, text=text)


# --------------------------------------------------------------------------- parsing
def _num(tok):
    tok = tok.lower()
    return int(tok) if tok.isdigit() else WORDNUM.get(tok)


def _find_city(text):
    low = text.lower()
    for hi, en in CITY_HI.items():
        if hi in text:
            return en
    names = sorted([n for ns in data.CITY_TIERS.values() for n in ns], key=len, reverse=True)
    for n in names:
        if re.search(rf"\b{re.escape(n)}\b", low):
            return n
    return None


def parse(text, asked=None):
    """Return a dict of facts found in text. `asked` is the slot we just asked about (lets bare answers work)."""
    low = text.lower().strip()
    out = {}

    if re.search(r"only mobile|just (a )?mobile|mobile plan|mobile only|sirf mobile|सिर्फ़ मोबाइल|सिर्फ मोबाइल|केवल मोबाइल", low):
        out["business_type"] = "mobile"
    else:
        for key, pat in BTYPE_RULES:
            if re.search(pat, low):
                out["business_type"] = key
                break

    wn = "|".join(WORDNUM)
    m = re.search(rf"\b(\d+|{wn})\s*(?:staff|employees?|people|persons?|workers|members|log\b|कर्मचारी|स्टाफ|लोग)", low) or \
        re.search(r"(?:staff|employees?)\s*(?:of|:|is|are)?\s*(\d+)", low) or re.search(r"(\d+)\s*(?:कर्मचारी|स्टाफ|लोग)", text)
    if m and _num(m.group(1)):
        out["employees"] = _num(m.group(1))
    m = re.search(rf"\b(\d+|{wn})\s*-?\s*(?:branch\w*|stores?|shops?|outlets?|sites?|locations?|दुकान\w*|शाखा\w*|आउटलेट)", low) or \
        re.search(r"(\d+)\s*-?\s*(?:दुकान\w*|शाखा\w*)", text)
    if m and _num(m.group(1)):
        out["sites"] = _num(m.group(1))
    if "employees" in out and "sites" not in out:
        out["sites_default"] = 1
    if re.search(r"single (shop|branch|store)|one (shop|branch|store)|\bonly one (shop|branch)", low):
        out.setdefault("sites", 1)

    m = re.search(r"tier\s*-?\s*([123])", low)
    if m:
        out["city_tier"] = int(m.group(1))
        out["city"] = f"Tier {m.group(1)}"
    c = _find_city(text)
    if c:
        out["city"] = c.title()
        out["city_tier"] = data.city_tier(c)
    elif "city" not in out:
        cm = re.search(r"\b(?:in|at|from|near)\s+([A-Z][a-zA-Z]{2,}(?: [A-Z][a-zA-Z]{2,})?)", text)
        if cm and cm.group(1).lower() not in ("india", "tier", "the", "our", "my", "gst", "gstin"):
            out["city"] = cm.group(1).title()
            out["city_tier"] = data.city_tier(cm.group(1))

    gm = re.search(r"\b\d{2}[A-Za-z]{5}\d{4}[A-Za-z][A-Za-z\d]Z[A-Za-z\d]\b", text)
    if gm:
        out["has_gstin"] = True
        out["gstin_typed"] = gm.group(0).upper()
    elif re.search(r"(cancel+ed|suspended|रद्द|निलंबित)", low) and re.search(r"gst|जीएसटी", low):
        out["has_gstin"] = True
        out["gstin_status"] = "Suspended" if re.search(r"suspend|निलंबित", low) else "Cancelled"
    elif re.search(r"\b(no|without|don'?t have|dont have|do not have|nahi|nahin|not have|no)\b.{0,14}(gst|जीएसटी)|(gst|जीएसटी).{0,14}\b(no|nahi|nahin|not)\b|(gst|जीएसटी).{0,10}(नहीं|नही)", low):
        out["has_gstin"] = False
    elif re.search(r"gst|जीएसटी", low):
        out["has_gstin"] = True

    m = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", low) or re.search(r"([\d,]{3,})\s*(?:rupees|rs\b|₹|per month|/month|a month|monthly|महीने|रुपये|रुपए)", low) \
        or re.search(r"(?:pay|pays|paying|spend|spends|खर्च)\D{0,15}([\d,]{3,})", low)
    if m:
        v = int(m.group(1).replace(",", "") or 0)
        if v:
            out["monthly_spend"] = v
    elif re.search(SKIP, low):
        out["spend_skipped"] = True

    # bare answers to the question we just asked
    bare = re.fullmatch(r"[\d,\s]+", low)
    if asked == "counts" and bare:
        nums = [int(x) for x in re.findall(r"\d+", low)]
        if nums:
            out.setdefault("employees", nums[0])
            out.setdefault("sites", nums[1] if len(nums) > 1 else 1)
    elif asked == "counts" and "employees" in out:
        out.setdefault("sites", 1)
    elif asked == "spend" and bare:
        v = int(re.sub(r"\D", "", low) or 0)
        if v:
            out["monthly_spend"] = v
    elif asked == "gst":
        if re.search(r"^(yes|y|yeah|yep|sure|haan|han|ha|hai|haanji|हाँ|हां|है|जी|जी हाँ)\b|i (do )?have|we have|है मेरे पास|है हमारे पास", low) and not re.search(r"\b(no|not|nahi|नहीं)\b", low):
            out["has_gstin"] = True
        elif re.search(r"^(no|n|nope|nahi|nahin|नहीं|नही)\b|don'?t|do not|not (yet|have)|nahi hai|नहीं है|नही है|without", low):
            out["has_gstin"] = False
    elif asked == "city" and "city" not in out and re.fullmatch(r"[A-Za-zऀ-ॿ .'-]{2,30}", text.strip()):
        out["city"] = text.strip().title()
        out["city_tier"] = data.city_tier(text.strip())

    if "monthly_spend" not in out and (asked == "spend" or re.search(r"pay|spend|खर्च|month|महीने|rupee|₹|\brs\b", low)):
        km = re.search(r"(\d+(?:\.\d+)?)\s*(k\b|thousand|hazaar|hazar|हज़ार|हजार)", low)
        wm = re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s*thousand", low)
        if km:
            out["monthly_spend"] = int(float(km.group(1)) * 1000)
        elif wm:
            out["monthly_spend"] = WORDNUM[wm.group(1)] * 1000
        if "monthly_spend" in out:
            out.pop("spend_skipped", None)

    wanted = [pid for pid, pat in WANTED_RULES if re.search(pat, low)]
    if wanted:
        out["wanted"] = wanted
        if re.search(r"\bonly\b|सिर्फ़|सिर्फ|केवल", low) and out.get("business_type") != "mobile":
            out["wanted_only"] = True
    return out


def llm_extract(text, profile):
    """Optional: ask an LLM (via OpenRouter) to pull facts out of free text. Returns {} on any problem."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return {}
    model = os.environ.get("CHAT_MODEL", "anthropic/claude-haiku-5.5")
    prompt = ("Extract facts from a small-business owner's message (English or Hindi). Return JSON only with any of these "
              "keys you are sure about: business_type (shop|salon|office|restaurant|factory|mobile), employees (int), "
              "sites (int), city (string), has_gstin (bool), monthly_spend (int). Message: " + text)
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body,
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            txt = json.loads(r.read())["choices"][0]["message"]["content"]
        txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
        d = json.loads(txt)
        out = {k: d[k] for k in ("business_type", "employees", "sites", "city", "has_gstin", "monthly_spend") if d.get(k) is not None}
        if "city" in out:
            out["city_tier"] = data.city_tier(out["city"])
            out["city"] = str(out["city"]).title()
        return out
    except Exception:
        return {}


# --------------------------------------------------------------------------- conversation
def new_profile():
    return dict(business_type=None, employees=None, sites=None, city=None, city_tier=None, has_gstin=None,
                gstin_status=None, monthly_spend=None, spend_skipped=False)


def next_slot(profile):
    if profile["business_type"] == "mobile":
        return None
    if not profile["business_type"]:
        return "business_type"
    if profile["employees"] is None or profile["sites"] is None:
        return "counts"
    if not profile["city"]:
        return "city"
    if profile["has_gstin"] is None:
        return "gst"
    if profile["monthly_spend"] is None and not profile["spend_skipped"]:
        return "spend"
    return None


def _chips(slot, lang):
    if slot == "business_type":
        return [dict(label="🏪 Shop / Kirana", hi="🏪 दुकान / किराना", slot="business_type", value="shop"),
                dict(label="💇 Salon / Pharmacy", hi="💇 सैलून / फार्मेसी", slot="business_type", value="salon"),
                dict(label="🩺 Clinic / CA / Coaching", hi="🩺 क्लिनिक / CA / कोचिंग", slot="business_type", value="office"),
                dict(label="🍽️ Restaurant / Multi-store", hi="🍽️ रेस्टोरेंट / मल्टी-स्टोर", slot="business_type", value="restaurant"),
                dict(label="🏭 Factory", hi="🏭 फैक्ट्री", slot="business_type", value="factory"),
                dict(label="📱 Just a mobile plan", hi="📱 सिर्फ़ मोबाइल प्लान", slot="business_type", value="mobile")]
    if slot == "city":
        return [dict(label=c, hi=h, slot="city", value=c) for c, h in
                [("Delhi", "दिल्ली"), ("Mumbai", "मुंबई"), ("Bengaluru", "बेंगलुरु"), ("Pune", "पुणे"), ("Indore", "इंदौर"),
                 ("Jaipur", "जयपुर"), ("Lucknow", "लखनऊ")]] + [dict(label="Other city…", hi="दूसरा शहर…", focus=True)]
    if slot == "gst":
        return [dict(label="✅ Yes, I have GST", hi="✅ हाँ, GST है", slot="gst", value=True),
                dict(label="❌ No GST", hi="❌ GST नहीं है", slot="gst", value=False)]
    if slot == "spend":
        return [dict(label=f"₹{v:,}", hi=f"₹{v:,}", slot="spend", value=v) for v in (1000, 2000, 3000, 5000)] + \
               [dict(label="Skip", hi="छोड़ें", slot="spend", value=0)]
    return []


def _ask(slot, lang, prefix=""):
    q = t("q_" + {"business_type": "btype"}.get(slot, slot), lang)
    cards = [dict(type="counts", staff=5, sites=1)] if slot == "counts" else []
    return dict(text=prefix + q, cards=cards), _chips(slot, lang)


def _apply_slot(S, slot, p):
    prof = S["profile"]
    if slot == "business_type":
        prof["business_type"] = p["value"]
    elif slot == "counts":
        prof["employees"], prof["sites"] = int(p["staff"]), int(p["sites"])
    elif slot == "city":
        prof["city"] = p["value"]
        prof["city_tier"] = data.city_tier(p["value"])
    elif slot == "gst":
        prof["has_gstin"] = bool(p["value"])
    elif slot == "spend":
        if p["value"]:
            prof["monthly_spend"] = int(p["value"])
        else:
            prof["spend_skipped"] = True


def _merge(S, facts):
    prof = S["profile"]
    changed = {}
    for k in ("business_type", "employees", "sites", "city", "city_tier", "has_gstin", "gstin_status", "monthly_spend", "spend_skipped"):
        if k in facts and facts[k] is not None and prof.get(k) != facts[k]:
            prof[k] = facts[k]
            changed[k] = facts[k]
    if facts.get("sites_default") and prof.get("sites") is None:
        prof["sites"] = 1
        changed["sites"] = 1
    if facts.get("gstin_typed"):
        S["typed_gstin"] = facts["gstin_typed"]
    if facts.get("wanted"):
        for w in facts["wanted"]:
            if w not in S["wanted"]:
                S["wanted"].append(w)
    return changed


def _btype_label(prof, lang):
    return pick(BTYPE_LABEL.get(prof["business_type"] or "shop", BTYPE_LABEL["shop"]), lang)


def card_for(S, q):
    return dict(type="plan", quote=q, handoff=bool(q.get("handoff")))


def _wanted_report(S, q, lang):
    """Fold the owner's explicit product requests into the quote and explain every 'no'."""
    prof = S["profile"]
    lines = []
    items = dict(q["quantities"])
    changed = False
    for pid in S["wanted"]:
        if pid in items:
            continue
        r = rules.eligibility(pid, prof)
        if r:
            if not any(x["id"] == pid for x in q["refused"]):
                q["refused"].append(dict(id=pid, name=data.PRODUCTS[pid]["name"], reason=rules.refusal_text(r[0], r[1], lang), code=r[0],
                                         alternatives=[dict(id=a, name=data.PRODUCTS[a]["name"]) for a in rules._alts(pid, prof)],
                                         alt_plan=rules.ALT_PLAN.get(pid)))
            rf = next(x for x in q["refused"] if x["id"] == pid)
            alts = [a["name"] for a in rf["alternatives"]]
            if rf.get("alt_plan"):
                alts.append(pick(rules.PLAN_NAMES[rf["alt_plan"]][:2], lang))
            ln = t("refused_one", lang, name=rf["name"], reason=rf["reason"])
            if alts:
                ln += " " + t("offer_instead", lang, alt=" / ".join(alts))
            lines.append(ln)
            S["trace"].append(dict(tool="check_eligibility", args=pid, result=f"refused ({r[0]})"))
        else:
            if pid in INTERNET:
                base_net = next((i for i in items if i in INTERNET), None)
                if base_net:
                    items = {(pid if k == base_net else k): v for k, v in items.items()}
                else:
                    items[pid] = 1
            else:
                items[pid] = 1
            changed = True
    if changed:
        nq = rules.build_quote(prof, items, lang, q["plan_key"])
        nq["refused"] = q["refused"] + [r for r in nq["refused"] if not any(x["id"] == r["id"] for x in q["refused"])]
        nq["handoff"] = q.get("handoff")
        q = nq
    for n in q["notes"]:
        lines.append(t("added_dep", lang, name=n["for_name"], dep=n["name"]))
        S["trace"].append(dict(tool="check_eligibility", args=n["for_id"], result=f"needs internet → added {n['id']}"))
    return q, lines


def _score(S):
    prof = S["profile"]
    s = 30 + min(20, (prof.get("sites") or 1) * 4) + min(15, (prof.get("employees") or 0) // 2)
    s += 15 if rules.gst_ok(prof) else 0
    s += 10 if S.get("quote") else 0
    s += 10 if S.get("stage") in ("kyc", "order") else 0
    s += 10 if prof.get("business_type") == "factory" else 0
    return min(100, s)


def make_lead(S, reason):
    prof = S["profile"]
    q = S.get("quote")
    S["lead"] = dict(session_id=S["id"], reason=reason, score=_score(S), profile=dict(prof),
                     summary=f"{prof.get('business_type') or '?'} · {prof.get('employees') or '?'} staff · {prof.get('sites') or '?'} site(s) · {prof.get('city') or '?'}"
                             + (f" · quote ₹{q['totals']['monthly']:,}/mo" if q else ""))
    S["trace"].append(dict(tool="handoff_to_human", args=reason, result=f"lead score {S['lead']['score']}"))


def recommend(S, lang, prefix_lines=None):
    prof = S["profile"]
    msgs = []
    if prof["business_type"] == "mobile":
        q = rules.recommend_plan(prof, lang)
        q["plan_key"] = "mobile"
        S["trace"].append(dict(tool="recommend_plan", args="mobile only", result="Business Postpaid 299"))
        msgs.append(dict(text=t("reco_mobile", lang)))
        q["handoff"] = None
    else:
        q = rules.recommend_plan(prof, lang)
        S["trace"].append(dict(tool="recommend_plan", args=json.dumps({k: v for k, v in prof.items() if v is not None}),
                               result=f"{q['plan_name']} ₹{q['totals']['monthly']:,}/mo"))
        q, lines = _wanted_report(S, q, lang)
        msgs.append(dict(text=t("reco", lang, btype=_btype_label(prof, lang), plan=q["plan_name"])))
    S["quote"], S["plan_key"], S["dropped"] = q, q["plan_key"], list(q["refused"])
    S["stage"] = "plan"
    msgs.append(dict(cards=[card_for(S, q)]))
    extra = []
    if prof["business_type"] != "mobile":
        extra = lines
        if q["refused"] and not lines:
            extra.append(t("dropped", lang))
    if extra:
        msgs.append(dict(text="\n".join(extra)))
    chips = []
    if q.get("handoff"):
        make_lead(S, q["handoff"])
        msgs.append(dict(text=t("handoff", lang), cards=[dict(type="handoff", reason=q["handoff"])]))
        chips = [dict(label="🌐 Continue online anyway", hi="🌐 फिर भी ऑनलाइन आगे बढ़ें", action="start_kyc"),
                 CHIP("💬 Too costly", "💬 बहुत महँगा", "too costly")]
    else:
        chips = [dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc"),
                 CHIP("💬 Too costly", "💬 बहुत महँगा", "too costly"), CHIP("🙋 Talk to a person", "🙋 किसी से बात करें", "talk to a person")]
    msgs[-1]["chips"] = chips
    return msgs


def handle(S, text="", payload=None):
    """Process one owner turn. Returns list of bot messages: {text?, cards?, chips?}."""
    payload = payload or {}
    S["trace"] = []
    lang = S["lang"]
    prof = S["profile"]
    text = (text or "").strip()

    if text and DEVANAGARI.search(text) and not S.get("lang_locked"):
        S["lang"] = lang = "hi"
        S["speech_lang"] = "hi"

    # ---- direct actions from buttons / cards
    if payload.get("action") == "custom":
        return custom_start(S, lang)
    if payload.get("action") == "ask_spend":
        S["asked"] = "spend"
        m, ch = _ask("spend", lang)
        m["chips"] = ch
        return [m]
    if payload.get("action") == "start_kyc":
        return start_kyc(S, lang)
    if payload.get("action") == "use_smaller" and S.get("alt_quote"):
        S["quote"] = S["alt_quote"]
        S["plan_key"] = "custom"
        return [dict(text=t("go_papers", lang) if False else "👍", cards=[card_for(S, S["quote"])],
                     chips=[dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")])]
    if payload.get("action") == "keep_plan":
        return [dict(cards=[card_for(S, S["quote"])],
                     chips=[dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")])]
    if payload.get("action") == "reminder":
        S["quote_status"] = "saved"
        S["drop_reason"] = S.get("drop_reason") or "will think"
        S["trace"].append(dict(tool="save_quote", args="reminder 24h/72h", result="saved"))
        return [dict(text=t("reminder_set", lang))]
    if payload.get("slot"):
        _apply_slot(S, payload["slot"], payload)
        text = ""
        S["asked"] = None
    asked = S.get("asked")

    # ---- a short, clear "go ahead" while the plan and its Continue button are on screen: just do it
    if (text and S.get("stage") == "plan" and S.get("quote") and S["quote"].get("items") and not (S.get("mode") == "custom" and not S.get("custom_done")) and len(text.split()) <= 6
            and re.search(GO_NOW, text.lower()) and any(c.get("action") == "start_kyc" for c in (S.get("_last_chips") or []))):
        S["trace"].append(dict(tool="open_paperwork", args=text[:50], result="owner said go ahead"))
        return start_kyc(S, lang)

    # ---- paperwork is open and the owner asks where/how to upload: show the screen again, never guess
    if text and S.get("stage") == "kyc" and re.search(UPLOADQ, text.lower()):
        S["trace"].append(dict(tool="open_paperwork", args=text[:50], result="re-opened the paperwork screen"))
        return [dict(text=t("kyc_where", lang), cards=[dict(type="open_kyc")], chips=[OPEN_KYC_CHIP])]

    # ---- LLM agent (when a key is set): free conversation, with tools for every fact
    from . import llm_agent
    if llm_agent.available() and (text or payload.get("slot")):
        slot = payload.get("slot")
        said = text or (f"[counts: {payload.get('staff')} staff, {payload.get('sites')} branch(es)]" if slot == "counts" else f"[{slot}: {payload.get('value')}]")
        r = llm_agent.run(S, said, lang)
        if r is not None:
            S["llm_fail"] = 0
            return r
        S["llm_fail"] = S.get("llm_fail", 0) + 1
        if text and not payload.get("slot") and S["llm_fail"] == 1:
            # first miss on a free-text message: say so honestly instead of carrying on with the questionnaire
            S["trace"].append(dict(tool="llm", args="", result="no answer; asked the owner to repeat"))
            return [dict(text=t("llm_retry", lang), chips=S.get("_last_chips") or [])]

    low = text.lower()
    # ---- global intents
    custom_active = S.get("mode") == "custom" and not S.get("custom_done")
    if text and re.search(RECALL, low):
        return [dict(text=recall(S, lang))]
    if text and re.search(CUSTOM, low) and not custom_active:
        return custom_start(S, lang)
    if text and not custom_active and not S.get("quote") and S.get("mode") != "custom":
        pf = parse(text, S.get("asked"))
        needs_found = parse_needs(text, prof)
        if needs_found and "business_type" not in pf and re.search(NEEDVERB, low) and not re.search(PRICEQ + "|" + EXPLAIN, low):
            first = custom_start(S, lang)
            more = custom_turn(S, text, {}, lang)
            return [dict(text=first[0]["text"], cards=first[0]["cards"])] + more
    if text and not custom_active and re.search(PRICEQ + "|" + EXPLAIN, low):
        found = parse_needs(text, prof)
        if found:
            lines = []
            for pid, _ in found[:3]:
                p = rules.P[pid]
                lines.append(t("price_of", lang, name=p["name"], price=f"{p['price']:,}", reason=rules.reason_for(pid, prof, 1, lang),
                               setup=(t("c_setup", lang, n=f"{p['setup']:,}") if p["setup"] else "")))
            S["trace"].append(dict(tool="get_product_info", args=",".join(f[0] for f in found[:3]), result="from catalogue"))
            out = [dict(text=chr(10).join(lines))]
            if asked and next_slot(prof) == asked:
                m, ch = _ask(asked, lang)
                m["chips"] = ch
                out.append(m)
            return out
    if text and re.search(PERSON, low):
        if not S.get("quote"):
            S["trace"].append(dict(tool="handoff_to_human", args="owner asked", result="lead created"))
        make_lead(S, "owner asked for a person")
        return [dict(text=t("handoff_ask", lang), cards=[dict(type="handoff", reason="owner asked for a person")])]
    if text and re.search(ORDER, low) and S.get("order"):
        return [dict(text=t("order_status", lang), cards=[dict(type="tracker", order=S["order"])])]
    if text and S.get("quote") and S["stage"] in ("plan", "declined"):
        r = _objection(S, low, lang)
        if r:
            return r
        if re.search(GO, low) and S["stage"] == "plan" and not custom_active:
            return start_kyc(S, lang)
    if text and re.search(r"where is my order|order status|ऑर्डर", low) and not S.get("order"):
        return [dict(text=t("order_none", lang))]

    if custom_active and (text or payload.get("action") in ("need", "suggest_no", "custom_done") or payload.get("slot")):
        return custom_turn(S, text, payload, lang)

    # ---- facts from the message
    facts = parse(text, asked) if text else {}
    if text and not facts and asked and S["profile"].get("business_type") != "mobile":
        facts = llm_extract(text, prof) or {}
    guess = False
    if asked == "business_type" and text and "business_type" not in facts and not payload.get("slot") and not re.match(GREET, low) and len(low) >= 4:
        facts = dict(facts, business_type="shop")
        guess = True                                        # unknown kind of business: start as a small shop, say so
    changed = _merge(S, facts)
    if facts.get("wanted_only") and S["wanted"]:
        return custom_only(S, lang)

    # ---- a finished custom plan stays custom: re-price it, never swap in a standard plan
    if S.get("quote") and S.get("plan_key") == "custom" and S.get("custom_done") and S["stage"] == "plan" and (changed or facts.get("wanted")):
        q = rules.build_quote(prof, S["quote"]["quantities"], lang, "custom")
        q["handoff"] = None
        S["quote"] = q
        return [dict(cards=[card_for(S, q)], chips=[dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")])]

    # ---- plan already exists: a new product request or changed fact re-runs the plan
    if S.get("quote") and S["stage"] in ("plan",) and (changed or facts.get("wanted")):
        if facts.get("wanted") and not changed:
            return _add_wanted(S, lang)
        return recommend(S, lang)

    if S.get("stage") == "kyc" and text and not changed:
        return [dict(text=t("kyc_where", lang), cards=[dict(type="open_kyc")], chips=[OPEN_KYC_CHIP])]
    slot = None if (S.get("plan_key") == "custom" and S.get("custom_done") and S.get("quote")) else next_slot(prof)
    if slot is None:
        S["asked"] = None
        q0 = S.get("quote")
        if q0 and q0.get("items") and not payload.get("slot"):
            # a plan already exists and this sentence changed nothing: say so, do not redo the plan
            S["trace"].append(dict(tool="no_match", args=text[:60], result="kept the plan; asked what to do next"))
            chips = [dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc"),
                     CHIP("💬 Too costly", "💬 बहुत महँगा", "too costly"), CHIP("🙋 Talk to a person", "🙋 किसी से बात करें", "talk to a person")]
            return [dict(text=t("fallback_plan", lang), chips=chips)]
        if S.get("plan_key") == "custom" and S.get("custom_done") and q0:
            q = rules.build_quote(prof, q0["quantities"], lang, "custom")
            q["handoff"] = None
            S["quote"] = q
            return [dict(cards=[card_for(S, q)], chips=[dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")])]
        return recommend(S, lang)
    S["asked"] = slot
    prefix = ""
    if text and not changed and not facts and not payload.get("slot"):
        prefix = t("fallback_q", lang)
    elif changed or payload.get("slot"):
        prefix = ""
    if guess:
        prefix = t("bt_guess", lang) + " "
    m, chips = _ask(slot, lang, prefix)
    if prefix == t("fallback_q", lang):
        m["text"] += chr(10) + t("fallback_hint", lang)
    m["chips"] = chips
    return [m]


def recall(S, lang):
    """Conversation memory: say back what the owner has told us, from the stored profile."""
    p = S["profile"]
    hi = lang == "hi"
    lines = []
    if p.get("business_type"):
        lines.append(("• बिज़नेस: " if hi else "• Business: ") + _btype_label(p, lang))
    if p.get("employees") is not None:
        lines.append(f"• {'कर्मचारी' if hi else 'Staff'}: {p['employees']}")
    if p.get("sites") is not None:
        lines.append(f"• {'शाखाएँ' if hi else 'Branches'}: {p['sites']}")
    if p.get("city"):
        lines.append(f"• {'शहर' if hi else 'City'}: {p['city']}")
    if p.get("has_gstin") is not None:
        yn = (("हाँ" if p["has_gstin"] else "नहीं") if hi else ("yes" if p["has_gstin"] else "no"))
        lines.append(f"• GST: {yn}")
    if p.get("monthly_spend"):
        lines.append(f"• {'आज का खर्च' if hi else 'Spend today'}: ₹{p['monthly_spend']:,}")
    if not lines:
        return t("recall_none", lang)
    out = t("recall_head", lang) + chr(10) + chr(10).join(lines)
    q = S.get("quote")
    if q and q.get("items"):
        out += chr(10) + t("recall_plan", lang, plan=q["plan_name"], price=f"{q['totals']['monthly']:,}")
    return out


def _add_wanted(S, lang):
    q, lines = _wanted_report(S, dict(S["quote"]), lang)
    S["quote"] = q
    S["stage"] = "plan"
    msgs = [dict(cards=[card_for(S, q)])]
    if lines:
        msgs.insert(0, dict(text="\n".join([t("wanted_head", lang)] + lines)))
    msgs[-1]["chips"] = [dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")]
    return msgs


def custom_only(S, lang):
    """Owner asked for only certain products: quote just those (plus anything they depend on)."""
    prof = S["profile"]
    items = {pid: 1 for pid in S["wanted"]}
    q = rules.build_quote(prof, items, lang, "custom")
    S["trace"].append(dict(tool="build_quote", args=",".join(items), result=f"₹{q['totals']['monthly']:,}/mo"))
    lines = []
    for r in q["refused"]:
        alts = [a["name"] for a in r["alternatives"]]
        ln = t("refused_one", lang, name=r["name"], reason=r["reason"])
        if alts:
            ln += " " + t("offer_instead", lang, alt=" / ".join(alts))
        lines.append(ln)
    for n in q["notes"]:
        lines.append(t("added_dep", lang, name=n["for_name"], dep=n["name"]))
    q["handoff"] = None
    S["quote"], S["plan_key"], S["dropped"], S["stage"] = q, "custom", list(q["refused"]), "plan"
    msgs = []
    if lines:
        msgs.append(dict(text="\n".join(lines)))
    msgs.append(dict(cards=[card_for(S, q)]))
    msgs[-1]["chips"] = [dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc")]
    if not q["items"]:
        msgs[-1]["chips"] = []
    return msgs


def _objection(S, low, lang):
    q = S["quote"]
    prof = S["profile"]
    if re.search(DECLINE, low):
        S["stage"] = "declined"
        S["drop_reason"] = "declined"
        S["quote_status"] = "abandoned"
        S["trace"].append(dict(tool="save_quote", args="declined", result="abandoned (stop selling)"))
        return [dict(text=t("decline", lang),
                     chips=[dict(label="🔔 Remind me later", hi="🔔 बाद में याद दिलाएँ", action="reminder")])]
    if re.search(NOTNEEDED, low):
        S["drop_reason"] = "not needed"
        return [dict(text=t("notneeded", lang))]
    if re.search(THINK, low):
        S["drop_reason"] = "will think"
        return [dict(text=t("think", lang), chips=[dict(label="🔔 Remind me", hi="🔔 याद दिलाएँ", action="reminder")])]
    kind = "costly" if re.search(COSTLY, low) else ("cheaper" if re.search(CHEAPER, low) else None)
    if kind:
        S["drop_reason"] = "price" if kind == "costly" else "cheaper rival"
        sm = rules.smaller_quote(prof, q, lang)
        S["trace"].append(dict(tool="build_quote", args="smaller option", result=(f"₹{sm['totals']['monthly']:,}/mo" if sm else "none")))
        if not sm:
            return [dict(text=t("costly_min", lang))]
        sm["handoff"] = None
        S["alt_quote"] = sm
        diff = q["totals"]["monthly"] - sm["totals"]["monthly"]
        return [dict(text=t(kind, lang)), dict(cards=[dict(type="plan", quote=sm, handoff=False, smaller=True, saves=diff)],
                                              chips=[dict(label="✅ Use this smaller option", hi="✅ यह छोटा विकल्प लें", action="use_smaller"),
                                                     dict(label="Keep my first plan", hi="पहला प्लान ही रखें", action="keep_plan")])]
    return None


def start_kyc(S, lang):
    S["stage"] = "kyc"
    S["trace"].append(dict(tool="start_kyc", args="", result="consent first"))
    return [dict(text=t("go_papers", lang), cards=[dict(type="open_kyc")],
                 chips=[dict(label="📄 Open paperwork", hi="📄 कागज़ात खोलें", action="start_kyc")])]


def greeting(S):
    lang = S["lang"]
    S["asked"] = "business_type"
    return [dict(text=t("greet", lang), chips=[CUSTOM_CHIP] + _chips("business_type", lang))]


# --------------------------------------------------------------------------- custom plan (build your own)
def custom_profile(S):
    """The profile used for pricing. Until city, team and GST are known, unknowns are not held against the owner."""
    prof = dict(S["profile"])
    known = bool(prof.get("city")) and prof.get("employees") is not None and prof.get("sites") is not None and prof.get("has_gstin") is not None
    if not known:
        prof["_lenient"] = True
    return prof, known


def custom_tiles(S, lang):
    prof, _ = custom_profile(S)
    return rules.catalogue_view(prof, (S.get("custom") or {}).get("items", {}), lang)


def custom_quote(S, lang):
    prof, known = custom_profile(S)
    cs = S["custom"]
    q = rules.build_quote(prof, cs["items"], lang, "custom")
    cs["items"] = dict(q["quantities"])            # what survived the rules is the truth
    for l in q["items"]:
        l["pending"] = bool(rules.P[l["id"]]["gst"] and prof.get("_lenient") and prof.get("has_gstin") is None)
    q["handoff"] = None
    q["estimate"] = not known
    return q, known


def custom_start(S, lang):
    S["mode"], S["custom_done"] = "custom", False
    S["custom"] = dict(items={}, suggested=[], no_suggest=False, refused_seen=[], est_noted=False)
    S["quote"], S["asked"] = None, None
    S["trace"].append(dict(tool="custom_plan", args="start", result="owner builds the plan, code prices it"))
    return [dict(text=t("custom_intro", lang), cards=[dict(type="needs", tiles=custom_tiles(S, lang))],
                 chips=[dict(label="🧭 Not sure, guide me", hi="🧭 पता नहीं, आप बताइए", text="guide me")])]


def _pick_internet(prof):
    if prof.get("city_tier") == 3:
        return "P04"
    return "P02" if (prof.get("employees") or 5) > 3 else "P03"


def parse_needs(text, prof):
    """[(product_id, qty or None)] named in the text, most specific words first."""
    low = text.lower()
    found = []
    for pid, pat in NEED_RULES:
        m = re.search(pat, low)
        if not m:
            continue
        low = low[:m.start()] + " " + low[m.end():]
        real = _pick_internet(prof) if pid == "INTERNET" else pid
        qty = None
        if pid in QTY_RULES:
            qm = re.search(QTY_RULES[pid], text.lower())
            if qm:
                qty = max(1, int(qm.group(1)))
        if real not in [f[0] for f in found]:
            found.append((real, qty))
    return found


def _default_qty(pid, prof):
    return max(1, prof.get("employees") or 1) if pid == "P16" else 1


def custom_next_slot(prof):
    if not prof.get("city"):
        return "city"
    if prof.get("employees") is None or prof.get("sites") is None:
        return "counts"
    if prof.get("has_gstin") is None:
        return "gst"
    return None


def _price_bits(line, lang):
    setup = t("c_setup", lang, n=f"{line['setup']:,}") if line["setup"] else ""
    return f"{line['monthly']:,}", setup


def custom_turn(S, text, payload, lang):
    cs, items, prof = S["custom"], S["custom"]["items"], S["profile"]
    low = (text or "").lower()
    act = payload.get("action")
    added, removed, qtychg, lines = [], [], [], []

    def setq(pid, qty):
        had = items.get(pid)
        if qty <= 0:
            if had:
                del items[pid]
                removed.append(pid)
        elif had is None:
            items[pid] = qty
            added.append(pid)
        elif had != qty:
            items[pid] = qty
            qtychg.append(pid)

    if act == "custom_done":
        return custom_finish(S, lang)
    if act == "suggest_no":
        cs["no_suggest"] = True                       # a clear no: stop suggesting
    elif act == "need":
        setq(payload["id"], int(payload.get("qty", 1)))
    elif text:
        if re.search(r"guide me|not sure|आप बताइए|पता नहीं", low):
            S["mode"], S["custom_done"] = None, True
            S["asked"] = "business_type"
            m, ch = _ask("business_type", lang)
            m["chips"] = [CUSTOM_CHIP] + ch
            return [m]
        facts = parse(text, S.get("asked"))
        facts.pop("wanted", None); facts.pop("wanted_only", None)
        found = parse_needs(text, prof)
        if found and re.search(EXPLAIN, low) and not re.search(REMOVE, low):
            out = []
            for pid, _ in found:
                p = rules.P[pid]
                out.append(t("c_explain", lang, name=p["name"], reason=rules.reason_for(pid, prof, _default_qty(pid, prof), lang),
                             price=f"{p['price']:,}", setup=(t("c_setup", lang, n=f"{p['setup']:,}") if p["setup"] else "")))
            ch = [dict(label=f"➕ Add {rules.P[found[0][0]]['name']}", hi=f"➕ {rules.P[found[0][0]]['name']} जोड़ें", action="need", id=found[0][0], qty=_default_qty(found[0][0], prof))]
            if items:
                ch.append(SHOW_CHIP)
            S["trace"].append(dict(tool="explain_product", args=found[0][0], result="from catalogue"))
            return [dict(text="\n".join(out), chips=ch)]
        changed = _merge(S, facts)
        if found:
            if re.search(REMOVE, low):
                for pid, _ in found:
                    setq(pid, 0)
            else:
                for pid, qty in found:
                    if qty is not None or pid not in items:
                        setq(pid, qty or _default_qty(pid, prof))
        elif not changed and not facts and not S.get("asked"):
            return [dict(text=t("custom_empty", lang) if not items else t("fallback_q", lang) + t("custom_empty", lang),
                         chips=[SHOW_CHIP] if items else [])]
        S["asked"] = None
    S["asked"] = None

    q, known = custom_quote(S, lang)
    S["quote"], S["plan_key"], S["dropped"] = q, "custom", list(q["refused"])
    S["stage"] = "plan" if q["items"] else S["stage"]
    by_id = {l["id"]: l for l in q["items"]}
    S["trace"].append(dict(tool="build_quote", args=",".join(f"{k}×{v}" for k, v in items.items()) or "empty",
                           result=f"₹{q['totals']['monthly']:,}/mo" + (" (estimate)" if q["estimate"] else "")))

    for pid in added:
        if pid in by_id:
            l = by_id[pid]
            m_, s_ = _price_bits(l, lang)
            lines.append(t("c_added", lang, name=l["name"], reason=l["reason"], price=m_, setup=s_))
            if l.get("pending"):
                lines.append("   ⏳ " + t("c_pending", lang))
    for pid in qtychg:
        if pid in by_id:
            lines.append(t("c_qty", lang, name=by_id[pid]["name"], qty=by_id[pid]["qty"]))
    for pid in removed:
        lines.append(t("c_removed", lang, name=rules.P[pid]["name"]))
    for n in q["notes"]:
        if n["id"] in by_id and n["id"] not in cs["refused_seen"] and n["for_id"] in (added + qtychg + [a for a, _ in []]):
            lines.append(t("added_dep", lang, name=n["for_name"], dep=n["name"]))
    seen = set(cs["refused_seen"])
    for r in q["refused"]:
        if r["id"] in seen:
            continue
        alts = [a["name"] for a in r["alternatives"]]
        if r.get("alt_plan"):
            alts.append(pick(rules.PLAN_NAMES[r["alt_plan"]][:2], lang))
        ln = t("c_removed_now", lang, name=r["name"], reason=r["reason"]) if r["id"] in S.get("_had", []) else t("refused_one", lang, name=r["name"], reason=r["reason"])
        if alts:
            ln += " " + t("offer_instead", lang, alt=" / ".join(alts))
        lines.append(ln)
        seen.add(r["id"])
    cs["refused_seen"] = [r["id"] for r in q["refused"]]
    S["_had"] = list(items)

    msgs = []
    if q["items"]:
        if lines:                                     # only talk about the total when something changed
            lines.append(t("c_total", lang, m=f"{q['totals']['monthly']:,}", s=f"{q['totals']['setup']:,}"))
            if q["estimate"] and not cs["est_noted"]:
                cs["est_noted"] = True
                lines.append("ℹ️ " + t("c_note_est", lang))
    elif not lines:
        lines.append(t("custom_empty", lang))
    if lines:
        msgs.append(dict(text="\n".join(lines)))

    if q["items"]:
        slot = custom_next_slot(S["profile"])
        if slot:
            S["asked"] = slot
            m, ch = _ask(slot, lang, t("c_ask_pre", lang))
            m["chips"] = ch
            msgs.append(m)
        else:
            sug = None
            if not cs["no_suggest"]:
                for pid in added:
                    key = "INTERNET" if pid in INTERNET else pid
                    for cand in SUGGEST.get(key, []):
                        if cand not in items and cand not in cs["suggested"] and not rules.eligibility(cand, custom_profile(S)[0]):
                            sug = cand
                            break
                    if sug:
                        break
            if sug:
                cs["suggested"].append(sug)
                p = rules.P[sug]
                S["trace"].append(dict(tool="suggest", args=sug, result="once, no pressure"))
                msgs.append(dict(text=t("c_suggest", lang, name=p["name"], reason=rules.reason_for(sug, S["profile"], _default_qty(sug, S["profile"]), lang), price=f"{p['price']:,}"),
                                 chips=[dict(label=f"➕ Add {p['name']}", hi=f"➕ {p['name']} जोड़ें", action="need", id=sug, qty=_default_qty(sug, S["profile"])),
                                        dict(label="No thanks", hi="नहीं, धन्यवाद", action="suggest_no"), SHOW_CHIP]))
            else:
                if not msgs:
                    msgs.append(dict(text=""))
                msgs[-1]["chips"] = [SHOW_CHIP]
    return msgs


def custom_finish(S, lang):
    cs = S["custom"]
    if not cs["items"]:
        return [dict(text=t("custom_empty", lang))]
    slot = custom_next_slot(S["profile"])
    if slot:
        S["asked"] = slot
        m, ch = _ask(slot, lang, t("c_ask_pre", lang))
        m["chips"] = ch
        return [m]
    S["custom_done"] = True
    q, _ = custom_quote(S, lang)
    S["quote"], S["plan_key"], S["dropped"], S["stage"] = q, "custom", list(q["refused"]), "plan"
    S["trace"].append(dict(tool="build_quote", args="final custom plan", result=f"₹{q['totals']['monthly']:,}/mo"))
    chips = [dict(label="✅ Continue to paperwork", hi="✅ कागज़ी कार्रवाई शुरू करें", action="start_kyc"),
             CHIP("💬 Too costly", "💬 बहुत महँगा", "too costly"), CHIP("🙋 Talk to a person", "🙋 किसी से बात करें", "talk to a person")]
    if not S["profile"].get("monthly_spend"):
        chips.insert(1, dict(label="📊 Compare with what I pay today", hi="📊 आज के खर्च से तुलना", action="ask_spend"))
    return [dict(text=t("c_done", lang), cards=[card_for(S, q)], chips=chips)]
