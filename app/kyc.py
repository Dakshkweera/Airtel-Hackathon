"""Smart KYC. A vision model (optional) only reads documents into JSON; code makes every decision."""
import base64
import hashlib
import json
import os
import re
import urllib.request
from datetime import date

from . import data
from .data import norm
from .i18n import KYC_MSG, pick

TODAY = date(2026, 7, 15)  # per the case README
GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$")
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DOC_TYPES = ["gst_certificate", "udyam_certificate", "signatory_id", "address_proof"]
LOW_CONFIDENCE = 0.6


def gstin_check_char(gstin):
    total = 0
    for i, ch in enumerate(gstin[:14]):
        product = CHARS.index(ch) * (1 if i % 2 == 0 else 2)
        total += product // 36 + product % 36
    return CHARS[(36 - total % 36) % 36]


def gstin_valid(gstin):
    return len(gstin) == 15 and all(c in CHARS for c in gstin) and gstin_check_char(gstin) == gstin[14]


def mask(value):
    v = value or ""
    return "•" * max(0, len(v) - 4) + v[-4:]


def check_gstin(gstin, lang="en"):
    """Steps 2-4. Returns dict(ok, stage, message, record, status)."""
    g = re.sub(r"\s", "", gstin or "").upper()
    if not GSTIN_RE.match(g):
        return dict(ok=False, stage="format", message=pick(KYC_MSG["gst_format"], lang))
    if not gstin_valid(g):
        return dict(ok=False, stage="checksum", message=pick(KYC_MSG["gst_checksum"], lang))
    rec = data.GSTIN_REG.get(g)
    if not rec:
        return dict(ok=False, stage="registry", message=pick(KYC_MSG["gst_notfound"], lang))
    out = dict(ok=True, stage="registry", status=rec["status"], gstin=g, masked=mask(g),
               legal_name=rec["legal_name"], address=rec["address"], city=rec["city"], pincode=rec["pincode"])
    if rec["status"] != "Active":
        out.update(ok=False, stage="status", message=pick(KYC_MSG["gst_status"], lang))
    return out


def check_udyam(number, lang="en"):
    u = re.sub(r"\s", "", number or "").upper()
    rec = data.UDYAM_REG.get(u)
    if not rec:
        return dict(ok=False, message=pick(KYC_MSG["udyam_notfound"], lang))
    return dict(ok=True, udyam_number=u, masked=mask(u), name=rec["name"], address=rec["address"])


# ------------------------------------------------------------------ reading documents
VISION_PROMPT = (
    "Read this Indian business document image. Return JSON only, no prose, with exactly these keys: "
    "doc_type (gst_certificate|udyam_certificate|signatory_id|address_proof), legal_name, trade_name, gstin, "
    "udyam_number, person_name, id_number, address, document_date (YYYY-MM-DD), expiry_date (YYYY-MM-DD), "
    "confidence (0 to 1). Use null for anything unreadable."
)


def read_document(image_bytes, doc_type, sample_key=None):
    """Return (fields, source). Order: known sample sidecar, vision model if a key exists, else low-confidence."""
    if sample_key and sample_key in data.SIDECAR_BY_PATH:
        return dict(data.SIDECAR_BY_PATH[sample_key]), "sample"
    h = hashlib.sha256(image_bytes).hexdigest()
    if h in data.SIDECAR_BY_HASH:
        return dict(data.SIDECAR_BY_HASH[h]), "sample"
    fields = _vision(image_bytes)
    if fields:
        return fields, "vision"
    return dict(doc_type=doc_type, confidence=0.0), "unreadable"


def _vision(image_bytes):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    model = os.environ.get("VISION_MODEL", "anthropic/claude-haiku-5.5")
    b64 = base64.b64encode(image_bytes).decode()
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": [
        {"type": "text", "text": VISION_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
        "max_tokens": 700, "reasoning": {"enabled": False}}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body,
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = json.loads(r.read())["choices"][0]["message"]["content"]
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
        return json.loads(text)
    except Exception:
        return None


# ------------------------------------------------------------------ cross-checks
def _date(s):
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def _pin(addr):
    m = re.findall(r"\b\d{6}\b", addr or "")
    return m[-1] if m else None


def verify(state, lang="en"):
    """state: dict(gstin, gst_record, udyam_record, docs{doc_type: fields}, has_gstin). Returns checks + overall."""
    docs = state.get("docs", {})
    has_gst = state.get("has_gstin")
    gst_rec = state.get("gst_record")
    ud_rec = state.get("udyam_record")
    checks = []

    def add(cid, label, passed, key=None, doc=None, review=False, msg=None):
        checks.append(dict(id=cid, label=label[1] if lang == "hi" else label[0], passed=passed, review=review,
                           message=msg or (pick(KYC_MSG[key], lang) if key else ""), doc=doc))

    need = DOC_TYPES if has_gst else [d for d in DOC_TYPES if d != "gst_certificate"]
    missing = [d for d in need if d not in docs]
    add("docs", ("All documents uploaded", "सभी दस्तावेज़ अपलोड"), not missing,
        key=("missing_" + missing[0]) if missing else "ok", doc=missing[0] if missing else None)

    def low(doc):
        return doc in docs and (docs[doc].get("confidence") or 0) < LOW_CONFIDENCE

    gst = docs.get("gst_certificate", {})
    ud = docs.get("udyam_certificate", {})
    sid = docs.get("signatory_id", {})
    adr = docs.get("address_proof", {})

    # names match
    if has_gst and gst and ud and gst_rec and ud_rec:
        if low("gst_certificate") or low("udyam_certificate"):
            add("names", ("Business names match", "बिज़नेस नाम मेल"), None, key="review", review=True,
                doc="gst_certificate" if low("gst_certificate") else "udyam_certificate")
        else:
            names = {norm(gst.get("legal_name")), norm(gst_rec["legal_name"]), norm(ud.get("legal_name")), norm(ud_rec["name"])}
            add("names", ("Business names match", "बिज़नेस नाम मेल"), len(names) == 1, key="ok" if len(names) == 1 else "names",
                doc=None if len(names) == 1 else "udyam_certificate")
    elif (not has_gst) and ud and ud_rec:
        ok = norm(ud.get("legal_name")) == norm(ud_rec["name"])
        add("names", ("Business names match", "बिज़नेस नाम मेल"), ok, key="ok" if ok else "names", doc=None if ok else "udyam_certificate")

    # GSTIN on certificate
    if has_gst and gst and state.get("gstin"):
        if low("gst_certificate"):
            add("gst_on_cert", ("GST number matches certificate", "GST नंबर प्रमाणपत्र से मेल"), None, key="review", review=True, doc="gst_certificate")
        else:
            ok = (gst.get("gstin") or "").upper() == state["gstin"]
            add("gst_on_cert", ("GST number matches certificate", "GST नंबर प्रमाणपत्र से मेल"), ok, key="ok" if ok else "gst_on_cert",
                doc=None if ok else "gst_certificate")

    # address
    reg_addr = gst_rec if (has_gst and gst_rec) else ud_rec
    if adr and reg_addr:
        if low("address_proof"):
            add("address", ("Address matches", "पता मेल"), None, key="review", review=True, doc="address_proof")
        else:
            reg_pin = reg_addr.get("pincode") or _pin(reg_addr.get("address"))
            city = (reg_addr.get("city") or "").lower()
            a = (adr.get("address") or "").lower()
            ok = bool(a) and (_pin(a) == reg_pin) and (not city or city in a)
            add("address", ("Address matches", "पता मेल"), ok, key="ok" if ok else "address", doc=None if ok else "address_proof")

        # bill date
        if not low("address_proof"):
            d = _date(adr.get("document_date"))
            ok = bool(d) and 0 <= (TODAY - d).days <= 90
            add("bill_date", ("Address proof is recent", "पता प्रमाण हाल का"), ok, key="ok" if ok else "bill_old",
                doc=None if ok else "address_proof")

    # signatory ID
    if sid:
        if low("signatory_id"):
            add("id", ("ID is valid", "ID वैध"), None, key="review", review=True, doc="signatory_id")
        elif not sid.get("person_name"):
            add("id", ("ID is valid", "ID वैध"), False, key="id_unreadable", doc="signatory_id")
        else:
            e = _date(sid.get("expiry_date"))
            ok = not e or e >= TODAY
            add("id", ("ID is valid", "ID वैध"), ok, key="ok" if ok else "id_expired", doc=None if ok else "signatory_id")

    failed = [c for c in checks if c["passed"] is False]
    review = [c for c in checks if c["review"]]
    overall = "fail" if failed else ("review" if review else "pass")
    return dict(checks=checks, overall=overall)
