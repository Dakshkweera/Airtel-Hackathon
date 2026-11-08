"""Loads the case CSVs once at startup. Drop the real files into data/ to replace the samples."""
import csv
import hashlib
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def _rows(name):
    p = DATA / name
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _pick(row, *keys, default=""):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return default


def _int(v, d=0):
    try:
        return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return d


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("&", "and"))


PRODUCTS = {}
for r in _rows("product_catalogue.csv"):
    pid = _pick(r, "product_id", "id")
    PRODUCTS[pid] = dict(
        id=pid,
        name=_pick(r, "name", "product_name"),
        category=_pick(r, "category"),
        price=_int(_pick(r, "price_min_inr_per_month", "price_min")),
        setup=_int(_pick(r, "one_time_setup_inr", "setup_inr")),
        contract=_int(_pick(r, "min_contract_months"), 1),
        days=_int(_pick(r, "typical_install_days")),
        tiers=[_int(t) for t in re.split(r"[|,; ]+", _pick(r, "available_city_tiers", default="1|2|3")) if t],
        min_emp=_int(_pick(r, "min_employees"), 1),
        min_sites=_int(_pick(r, "min_sites"), 1),
        gst=_pick(r, "requires_gstin", default="N").strip().upper().startswith("Y"),
        one_of=[x for x in re.split(r"[|,; ]+", _pick(r, "requires_one_of")) if x],
    )

GSTIN_REG = {}
for r in _rows("mock_gstin_registry.csv"):
    g = _pick(r, "gstin").strip().upper()
    GSTIN_REG[g] = dict(
        gstin=g,
        legal_name=_pick(r, "legal_name"),
        trade_name=_pick(r, "trade_name"),
        status=_pick(r, "status", default="Active").strip().title(),
        address=_pick(r, "principal_address", "address"),
        city=_pick(r, "city"),
        pincode=_pick(r, "pincode", "pin"),
    )

UDYAM_REG = {}
for r in _rows("mock_udyam_registry.csv"):
    u = _pick(r, "udyam_number", "udyam").strip().upper()
    UDYAM_REG[u] = dict(
        udyam_number=u,
        name=_pick(r, "enterprise_name", "legal_name"),
        address=_pick(r, "address"),
        city=_pick(r, "city"),
        pincode=_pick(r, "pincode", "pin"),
    )

SAMPLES = []
_sp = DATA / "samples.json"
if _sp.exists():
    SAMPLES = json.loads(_sp.read_text(encoding="utf-8"))

# sidecar index: lets the demo "read" sample images without a vision model
DOC_DIR = DATA / "kyc_documents"
SIDECAR_BY_HASH = {}
SIDECAR_BY_PATH = {}
if DOC_DIR.exists():
    for png in DOC_DIR.rglob("*.png"):
        js = png.with_suffix(".json")
        if js.exists():
            fields = json.loads(js.read_text(encoding="utf-8"))
            SIDECAR_BY_HASH[hashlib.sha256(png.read_bytes()).hexdigest()] = fields
            SIDECAR_BY_PATH[png.relative_to(DOC_DIR).as_posix()] = fields

CITY_TIERS = {
    1: ["delhi", "new delhi", "mumbai", "bengaluru", "bangalore", "chennai", "hyderabad", "kolkata", "pune", "ahmedabad"],
    2: ["indore", "jaipur", "lucknow", "nagpur", "surat", "bhopal", "chandigarh", "kochi", "cochin", "coimbatore", "patna",
        "vadodara", "nashik", "ludhiana", "kanpur", "agra", "visakhapatnam", "thane", "noida", "gurgaon", "gurugram",
        "ranchi", "raipur", "bhubaneswar", "dehradun", "amritsar", "jodhpur", "madurai", "mysuru", "mysore", "guwahati"],
}


def city_tier(city):
    c = (city or "").strip().lower()
    for t, names in CITY_TIERS.items():
        if c in names:
            return t
    return 3
