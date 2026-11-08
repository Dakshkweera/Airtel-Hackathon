"""Rules engine: eligibility, plans and pricing. Plain Python over the catalogue. Never calls an LLM."""
from . import data
from .i18n import (DEP_ADDED, NO_DEP, PLAN_NAMES, REASON, REFUSE, pick)

P = data.PRODUCTS
EXTRA_IDS = ["P17", "P15", "P19", "P23", "P22"]
EDITABLE = {"P07": 1, "P16": 0, "P20": 0, "P24": 0}  # id -> minimum quantity
# nearest allowed option when a product is refused (first allowed one is substituted in a plan)
ALTS = {"P05": ["P02", "P01"], "P01": ["P02", "P03"], "P02": ["P03", "P04"], "P03": ["P04"], "P10": ["P09"], "P15": ["P18"]}
ALT_PLAN = {"P15": "dukaan"}


def _unknown(profile, key):
    """While a custom plan is being discussed, facts not yet given are not held against the owner."""
    return bool(profile.get("_lenient")) and profile.get(key) is None


def gst_ok(profile):
    if _unknown(profile, "has_gstin"):
        return True
    return bool(profile.get("has_gstin")) and (profile.get("gstin_status") or "Active") == "Active"


def eligibility(pid, profile):
    """None if allowed, else (code, n)."""
    p = P[pid]
    if profile.get("city_tier") and profile["city_tier"] not in p["tiers"]:
        return ("city", 0)
    if not _unknown(profile, "employees") and (profile.get("employees") or 1) < p["min_emp"]:
        return ("staff", p["min_emp"])
    if not _unknown(profile, "sites") and (profile.get("sites") or 1) < p["min_sites"]:
        return ("sites", p["min_sites"])
    if p["gst"] and not gst_ok(profile):
        blocked = profile.get("has_gstin") and profile.get("gstin_status") in ("Cancelled", "Suspended")
        return ("gst_blocked" if blocked else "gst", 0)
    return None


def refusal_text(code, n, lang):
    return pick(REFUSE[code], lang, n=n) if "{n}" in REFUSE[code][0] else pick(REFUSE[code], lang)


def _name(pid):
    return P[pid]["name"]


def _alts(pid, profile):
    return [a for a in ALTS.get(pid, []) if a in P and not eligibility(a, profile)]


def check_eligibility(profile, product_ids, lang="en"):
    allowed, refused, auto_added = [], [], []
    for pid in product_ids:
        if pid not in P:
            continue
        r = eligibility(pid, profile)
        if r:
            refused.append(dict(id=pid, name=_name(pid), reason=refusal_text(r[0], r[1], lang), code=r[0],
                                alternatives=[dict(id=a, name=_name(a)) for a in _alts(pid, profile)],
                                alt_plan=ALT_PLAN.get(pid)))
        else:
            allowed.append(pid)
    for pid in list(allowed):
        dep = _dependency(pid, allowed + [a["id"] for a in auto_added], profile)
        if dep == "none":
            allowed.remove(pid)
            refused.append(dict(id=pid, name=_name(pid), reason=pick(NO_DEP, lang), code="dep", alternatives=[]))
        elif dep:
            auto_added.append(dict(id=dep, name=_name(dep), for_id=pid, for_name=_name(pid), reason=pick(DEP_ADDED, lang)))
    return dict(allowed=allowed, refused=refused, auto_added=auto_added)


def _dependency(pid, selected, profile):
    """None when satisfied, an id when one must be auto-added (cheapest allowed), 'none' if impossible."""
    one_of = P[pid]["one_of"]
    if not one_of or any(d in selected for d in one_of):
        return None
    cands = sorted((d for d in one_of if d in P and not eligibility(d, profile)), key=lambda d: P[d]["price"])
    return cands[0] if cands else "none"


def reason_for(pid, profile, qty, lang):
    tpl = REASON.get(pid)
    if not tpl:
        return "Included in your plan." if lang != "hi" else "आपके प्लान में शामिल।"
    staff = profile.get("employees") or (("आपके" if lang == "hi" else "your") if profile.get("_lenient") else 1)
    sites = profile.get("sites") or (("आपकी" if lang == "hi" else "your") if profile.get("_lenient") else 1)
    return pick(tpl, lang, staff=staff, sites=sites, qty=qty)


def build_quote(profile, items, lang="en", plan_key="custom"):
    """items: {product_id: qty}. Returns a full quote; refusals carry plain reasons."""
    sel, refused, notes = {}, [], []
    for pid, q in items.items():
        if pid not in P or q <= 0:
            continue
        r = eligibility(pid, profile)
        if r:
            refused.append(dict(id=pid, name=_name(pid), reason=refusal_text(r[0], r[1], lang), code=r[0],
                                alternatives=[dict(id=a, name=_name(a)) for a in _alts(pid, profile)],
                                alt_plan=ALT_PLAN.get(pid)))
        else:
            sel[pid] = q
    front = {}
    for pid in list(sel):
        dep = _dependency(pid, list(sel) + list(front), profile)
        if dep == "none":
            del sel[pid]
            refused.append(dict(id=pid, name=_name(pid), reason=pick(NO_DEP, lang), code="dep", alternatives=[]))
        elif dep:
            front[dep] = 1
            notes.append(dict(id=dep, name=_name(dep), for_id=pid, for_name=_name(pid), reason=pick(DEP_ADDED, lang)))
    ordered = {**front, **sel}

    lines = []
    for pid, q in ordered.items():
        p = P[pid]
        lines.append(dict(id=pid, name=p["name"], qty=q, unit=p["price"], monthly=p["price"] * q, setup=p["setup"] * q,
                          reason=reason_for(pid, profile, q, lang), min_qty=EDITABLE.get(pid),
                          editable=pid in EDITABLE, auto_added=pid in front))
    monthly = sum(l["monthly"] for l in lines)
    setup = sum(l["setup"] for l in lines)
    contract = max([P[l["id"]]["contract"] for l in lines], default=0)
    days = max([P[l["id"]]["days"] for l in lines], default=0)

    spend = profile.get("monthly_spend") or 0
    savings = dict(spend=spend, diff=spend - monthly) if spend > 0 and lines else None

    extras = []
    for pid in EXTRA_IDS:
        if plan_key == "mobile" or (plan_key != "custom" and pid in plan_items(plan_key, profile)):
            continue
        r = eligibility(pid, profile)
        dep_ok = True
        if not r and P[pid]["one_of"]:
            dep_ok = _dependency(pid, list(ordered), profile) != "none"
        extras.append(dict(id=pid, name=_name(pid), price=P[pid]["price"], setup=P[pid]["setup"],
                           allowed=(r is None and dep_ok),
                           reason=(refusal_text(r[0], r[1], lang) if r else (pick(NO_DEP, lang) if not dep_ok else "")),
                           blurb=reason_for(pid, profile, 1, lang), on=pid in ordered))
    names = PLAN_NAMES[plan_key]
    return dict(plan_key=plan_key, plan_name=names[1] if lang == "hi" else names[0],
                tagline=names[3] if lang == "hi" else names[2],
                items=lines, refused=refused, notes=notes, extras=extras,
                totals=dict(monthly=monthly, setup=setup, contract_months=contract, expected_days=days),
                savings=savings, quantities={l["id"]: l["qty"] for l in lines})


def plan_items(plan_key, profile):
    emp = profile.get("employees") or 1
    sites = profile.get("sites") or 1
    if plan_key == "mobile":
        return {"P07": 1}
    if plan_key == "factory":
        return {"P05": 1, "P09": 1, "P21": 1, "P08": 3, "P16": 10, "P20": 10, "P24": 10}
    if plan_key == "multi":
        return {"P02": sites, "P09": sites, "P10": sites, "P23": 2 * sites, "P07": sites}
    if plan_key == "clinic":
        return {"P02": 1, "P09": 1, "P07": 2, "P16": max(1, emp), "P20": min(4, max(1, emp))}
    return {"P04": 1, "P07": 1, "P18": 1}  # dukaan


def choose_plan(profile):
    bt = profile.get("business_type")
    sites = profile.get("sites") or 1
    if bt == "mobile":
        return "mobile"
    if bt == "factory":
        return "factory"
    if sites >= 2:
        return "multi"
    if bt == "office":
        return "clinic"
    return "dukaan"


def needs_handoff(profile, asked_person=False):
    if asked_person:
        return "owner asked for a person"
    if profile.get("business_type") == "factory":
        return "factory or manufacturer"
    if (profile.get("sites") or 1) >= 3:
        return "3 or more branches"
    return None


def recommend_plan(profile, lang="en"):
    key = choose_plan(profile)
    intended = plan_items(key, profile)
    items = dict(intended)
    # swap refused items for the nearest allowed option, so the plan stays usable
    for pid in list(intended):
        if eligibility(pid, profile) and pid in ALTS:
            alt = next((a for a in ALTS[pid] if not eligibility(a, profile)), None)
            if alt and alt not in items:
                items = {(alt if k == pid else k): v for k, v in items.items()}
    q = build_quote(profile, items, lang, key)
    # keep the refusal for the swapped-out item, so the owner sees why
    for pid in intended:
        if pid not in items and not any(r["id"] == pid for r in q["refused"]):
            r = eligibility(pid, profile)
            if r:
                q["refused"].append(dict(id=pid, name=_name(pid), reason=refusal_text(r[0], r[1], lang), code=r[0],
                                         alternatives=[dict(id=a, name=_name(a)) for a in _alts(pid, profile)], alt_plan=None))
    q["handoff"] = needs_handoff(profile)
    return q


def smaller_quote(profile, quote, lang="en"):
    """A cheaper arrangement from the same catalogue, or None. Never invents a discount."""
    items = dict(quote["quantities"])
    key = quote["plan_key"]
    for pid in EXTRA_IDS:
        if key == "custom" or pid not in plan_items(key, profile):
            items.pop(pid, None)
    items.pop("P20", None)
    if "P02" in items and sites_one(profile) and not eligibility("P03", profile):
        items = {("P03" if k == "P02" else k): v for k, v in items.items()}
    if key == "dukaan":
        items.pop("P18", None)
    if key == "multi" or key == "factory":
        return None
    q = build_quote(profile, items, lang, "custom")
    q["plan_name"] = "A smaller option" if lang != "hi" else "एक छोटा विकल्प"
    q["tagline"] = "Same essentials, fewer extras" if lang != "hi" else "ज़रूरी चीज़ें वही, एक्स्ट्रा कम"
    if q["totals"]["monthly"] >= quote["totals"]["monthly"] or not q["items"]:
        return None
    return q


def sites_one(profile):
    return (profile.get("sites") or 1) <= 1


# ------------------------------------------------------------------ custom plans
NEED_GROUPS = [
    ("net", ["P03", "P02", "P04", "P01"]),
    ("phone", ["P07", "P11"]),
    ("safe", ["P09", "P20", "P22", "P23", "P17"]),
    ("grow", ["P18", "P15", "P19", "P25"]),
    ("team", ["P16", "P12"]),
]
QTY_EDIT = {"P07", "P16", "P20", "P23", "P11"}
DEFAULT_QTY = {"P07": 1}


def catalogue_view(profile, items, lang="en"):
    """Tiles for the 'what do you need' picker. Eligibility comes from the same rules; nothing is hidden."""
    groups = []
    for gid, ids in NEED_GROUPS:
        tiles = []
        for pid in ids:
            if pid not in P:
                continue
            r = eligibility(pid, profile)
            ok = r is None
            if ok and P[pid]["one_of"] and _dependency(pid, list(items), profile) == "none":
                ok = False
                reason = pick(NO_DEP, lang)
            else:
                reason = "" if ok else refusal_text(r[0], r[1], lang)
            tiles.append(dict(id=pid, name=P[pid]["name"], price=P[pid]["price"], setup=P[pid]["setup"], allowed=ok, reason=reason,
                              blurb=reason_for(pid, profile, 1, lang), qty=items.get(pid, 0), editable=pid in QTY_EDIT,
                              pending=bool(P[pid]["gst"] and profile.get("_lenient") and profile.get("has_gstin") is None)))
        groups.append(dict(id=gid, tiles=tiles))
    return groups
