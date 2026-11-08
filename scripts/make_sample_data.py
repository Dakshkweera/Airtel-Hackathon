"""Generate SAMPLE case data in the shape described by the PRD.

The real case zip (product_catalogue.csv, mock registries, kyc_documents/) was not
available, so this builds stand-ins. Drop the real files into data/ to replace them.
Run:  python scripts/make_sample_data.py
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = DATA / "kyc_documents"

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def check_char(g14: str) -> str:
    total = 0
    for i, ch in enumerate(g14):
        p = CHARS.index(ch) * (1 if i % 2 == 0 else 2)
        total += p // 36 + p % 36
    return CHARS[(36 - total % 36) % 36]


def make_gstin(state: str, pan: str, entity: str = "1") -> str:
    base = f"{state}{pan}{entity}Z"
    return base + check_char(base)


# ---------------------------------------------------------------- catalogue
# id, name, category, price, setup, contract, install_days, tiers, min_emp, min_sites, gst, one_of
PRODUCTS = [
    ("P01", "Biz Fibre 1G", "internet", 2999, 1500, 12, 7, "1", 1, 1, "N", ""),
    ("P02", "Biz Fibre 300", "internet", 1499, 1500, 12, 5, "1|2", 1, 1, "N", ""),
    ("P03", "Biz Fibre 100", "internet", 799, 1000, 12, 5, "1|2", 1, 1, "N", ""),
    ("P04", "Biz 5G AirFiber 100", "internet", 999, 0, 6, 2, "1|2|3", 1, 1, "N", ""),
    ("P05", "Leased Line 100 Mbps", "internet", 9000, 30000, 12, 21, "1|2", 10, 1, "Y", ""),
    ("P06", "Business Landline Voice", "voice", 299, 0, 6, 3, "1|2", 1, 1, "N", ""),
    ("P07", "Business Postpaid 299", "mobile", 299, 0, 1, 1, "1|2|3", 1, 1, "N", ""),
    ("P08", "IoT SIM", "iot", 299, 500, 12, 3, "1|2", 1, 1, "Y", ""),
    ("P09", "Backup 4G/5G Failover", "internet", 499, 0, 12, 2, "1|2|3", 1, 1, "N", "P01|P02|P03|P04|P05"),
    ("P10", "SD-WAN", "network", 1300, 5000, 12, 10, "1|2", 1, 3, "Y", ""),
    ("P11", "Cloud Telephony", "voice", 399, 0, 6, 2, "1|2", 2, 1, "N", ""),
    ("P12", "Video Conferencing", "collab", 349, 0, 6, 1, "1|2|3", 3, 1, "N", ""),
    ("P13", "Static IP", "internet", 299, 0, 12, 1, "1|2", 1, 1, "N", "P01|P02|P03|P05"),
    ("P14", "Managed Router", "network", 199, 0, 12, 2, "1|2|3", 1, 1, "N", "P01|P02|P03|P04|P05"),
    ("P15", "WhatsApp Business API", "marketing", 599, 0, 6, 1, "1|2|3", 1, 1, "Y", ""),
    ("P16", "Cloud Email", "collab", 119, 0, 12, 0, "1|2|3", 1, 1, "N", ""),
    ("P17", "Cloud Backup 1 TB", "cloud", 499, 0, 12, 0, "1|2|3", 1, 1, "N", ""),
    ("P18", "Website + Domain Starter", "digital", 199, 0, 12, 2, "1|2|3", 1, 1, "N", ""),
    ("P19", "Cloud POS", "retail", 399, 0, 12, 1, "1|2|3", 1, 1, "N", ""),
    ("P20", "Endpoint Security", "security", 108, 0, 12, 0, "1|2|3", 1, 1, "N", ""),
    ("P21", "Industrial IoT Gateway", "iot", 1369, 10000, 12, 14, "1|2", 10, 1, "Y", ""),
    ("P22", "Secure Wi-Fi", "security", 249, 0, 12, 1, "1|2|3", 1, 1, "N", "P01|P02|P03|P04|P05"),
    ("P23", "Cloud CCTV", "security", 799, 1800, 12, 3, "1|2|3", 1, 1, "N", "P01|P02|P03|P04"),
    ("P24", "Cloud Telephony Seat", "voice", 199, 400, 12, 1, "1|2", 1, 1, "N", ""),
    ("P25", "Accounting Software", "digital", 249, 0, 12, 0, "1|2|3", 1, 1, "N", ""),
]
# P10's setup in plan = 5000; P23 setup 1800 each; P02 1500 -> Multi-Store setup 10,100 per site


def write_catalogue():
    cols = ["product_id", "name", "category", "price_min_inr_per_month", "price_max_inr_per_month",
            "one_time_setup_inr", "min_contract_months", "typical_install_days", "available_city_tiers",
            "min_employees", "min_sites", "requires_gstin", "requires_one_of"]
    with open(DATA / "product_catalogue.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for p in PRODUCTS:
            pid, name, cat, price, setup, contract, days, tiers, me, ms, gst, oneof = p
            w.writerow([pid, name, cat, price, int(price * 1.25), setup, contract, days, tiers, me, ms, gst, oneof])


# ---------------------------------------------------------------- applicants
BUSINESSES = {
    "K01": dict(legal="Meena Dental and Family Clinic", city="Indore", pin="452001", addr="12 MG Road, Indore, 452001", state="23", pan="ABCDE1234F", udyam="UDYAM-MP-23-0001001"),
    "K02": dict(legal="Sharma & Associates", city="Jaipur", pin="302001", addr="45 MI Road, Jaipur, 302001", state="08", pan="BCDEF2345G", udyam="UDYAM-RJ-08-0001002"),
    "K03": dict(legal="Gupta Medical Store", city="Lucknow", pin="226001", addr="8 Hazratganj, Lucknow, 226001", state="09", pan="CDEFG3456H", udyam="UDYAM-UP-09-0001003"),
    "K04": dict(legal="Rao Coaching Classes", city="Pune", pin="411001", addr="22 FC Road, Pune, 411001", state="27", pan="DEFGH4567J", udyam="UDYAM-MH-27-0001004"),
    "K05": dict(legal="Singh Unisex Salon", city="Chandigarh", pin="160017", addr="Shop 5, Sector 17, Chandigarh, 160017", state="04", pan="EFGHJ5678K", udyam="UDYAM-CH-04-0001005"),
    "K06": dict(legal="Patel Kirana Store", city="Ahmedabad", pin="380001", addr="3 Ellis Bridge, Ahmedabad, 380001", state="24", pan="FGHJK6789L", udyam="UDYAM-GJ-24-0001006", status="Cancelled"),
    "K07": dict(legal="Joshi Sweets", city="Nagpur", pin="440001", addr="17 Sitabuldi, Nagpur, 440001", state="27", pan="GHJKL7890M", udyam="UDYAM-MH-27-0001007", status="Suspended"),
    "K08": dict(legal="Iyer Tutorials", city="Chennai", pin="600001", addr="9 Anna Salai, Chennai, 600001", state="33", pan="HJKLM8901N", udyam="UDYAM-TN-33-0001008"),
    "K09": dict(legal="Khan Boutique", city="Indore", pin="452010", addr="31 Palasia, Indore, 452010", state="23", pan="JKLMN9012P", udyam="UDYAM-MP-23-0001009"),
    "K10": dict(legal="Nair Hardware Traders", city="Kochi", pin="682001", addr="14 MG Road, Kochi, 682001", state="32", pan="KLMNP0123Q", udyam="UDYAM-KL-32-0001010"),
    "K11": dict(legal="Reddy Electronics", city="Hyderabad", pin="500001", addr="6 Abids Road, Hyderabad, 500001", state="36", pan="LMNPQ1234R", udyam="UDYAM-TS-36-0001011"),
    "K12": dict(legal="Das Stationers", city="Kolkata", pin="700001", addr="27 College Street, Kolkata, 700001", state="19", pan="MNPQR2345S", udyam="UDYAM-WB-19-0001012"),
}
EXTRA = {  # registry-only businesses for quick manual tries
    "X01": dict(legal="Verma Kirana and General Store", city="Bhopal", pin="462001", addr="2 New Market, Bhopal, 462001", state="23", pan="NPQRS3456T", udyam="UDYAM-MP-23-0002001"),
    "X02": dict(legal="Bansal Restaurants Pvt Ltd", city="Delhi", pin="110001", addr="10 Connaught Place, Delhi, 110001", state="07", pan="PQRST4567U", udyam="UDYAM-DL-07-0002002"),
    "X03": dict(legal="Kulkarni Precision Works", city="Pune", pin="411019", addr="Plot 4, MIDC Bhosari, Pune, 411019", state="27", pan="QRSTU5678V", udyam="UDYAM-MH-27-0002003"),
}

SAMPLES = [  # (id, label, issue)
    ("K01", "Meena Dental Clinic, Indore", "Everything correct"),
    ("K02", "Sharma & Associates, Jaipur", "Business name differs between GST and Udyam certificates"),
    ("K03", "Gupta Medical Store, Lucknow", "GST number on certificate differs from the one typed"),
    ("K04", "Rao Coaching Classes, Pune", "Electricity bill is older than 3 months"),
    ("K05", "Singh Unisex Salon, Chandigarh", "Udyam certificate not uploaded"),
    ("K06", "Patel Kirana Store, Ahmedabad", "GST registration is cancelled"),
    ("K07", "Joshi Sweets, Nagpur", "GST registration is suspended"),
    ("K08", "Iyer Tutorials, Chennai", "Signatory ID has expired"),
    ("K09", "Khan Boutique, Indore", "Address on bill is in a different city"),
    ("K10", "Nair Hardware, Kochi", "Typing mistake in GST number"),
    ("K11", "Reddy Electronics, Hyderabad", "Udyam number not found"),
    ("K12", "Das Stationers, Kolkata", "Blurry bill, sent for human review"),
]


def norm_names():
    return {}


def build():
    DATA.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    write_catalogue()

    allb = {**BUSINESSES, **EXTRA}
    for k, b in allb.items():
        b["gstin"] = make_gstin(b["state"], b["pan"])
        b.setdefault("status", "Active")

    with open(DATA / "mock_gstin_registry.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["gstin", "legal_name", "trade_name", "status", "principal_address", "city", "pincode"])
        for b in allb.values():
            w.writerow([b["gstin"], b["legal"], b["legal"], b["status"], b["addr"], b["city"], b["pin"]])

    with open(DATA / "mock_udyam_registry.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["udyam_number", "enterprise_name", "address", "city", "pincode"])
        for k, b in allb.items():
            if k == "K11":  # planted: not in registry
                continue
            w.writerow([b["udyam"], b["legal"], b["addr"], b["city"], b["pin"]])

    samples_json = []
    for kid, label, issue in SAMPLES:
        b = allb[kid]
        gst_name = b["legal"]
        udyam_name = b["legal"]
        udyam_no = b["udyam"]
        gst_on_cert = b["gstin"]
        typed = b["gstin"]
        addr_proof_addr = b["addr"]
        bill_date = "2026-06-28"
        id_expiry = "2031-04-30"
        id_conf = gst_conf = ud_conf = ad_conf = 0.96
        with_udyam = True
        owner = "Owner of " + b["legal"].split(" ")[0]

        if kid == "K02":
            udyam_name = "Sharma Traders"
        if kid == "K03":
            gst_on_cert = make_gstin(b["state"], "ZZZZZ9999Z")
        if kid == "K04":
            bill_date = "2026-03-20"
        if kid == "K05":
            with_udyam = False
        if kid == "K08":
            id_expiry = "2026-05-31"
        if kid == "K09":
            addr_proof_addr = "31 Arera Colony, Bhopal, 462016"
        if kid == "K10":
            typed = b["gstin"][:14] + ("A" if b["gstin"][14] != "A" else "B")
        if kid == "K11":
            udyam_no = "UDYAM-TS-36-0009999"
        if kid == "K12":
            ad_conf = 0.42

        docs = {
            "gst_certificate": dict(doc_type="gst_certificate", legal_name=gst_name, trade_name=gst_name, gstin=gst_on_cert,
                                    udyam_number=None, person_name=None, id_number=None, address=b["addr"],
                                    document_date="2025-04-01", expiry_date=None, confidence=gst_conf),
            "udyam_certificate": dict(doc_type="udyam_certificate", legal_name=udyam_name, trade_name=None, gstin=None,
                                      udyam_number=udyam_no, person_name=None, id_number=None, address=b["addr"],
                                      document_date="2024-11-12", expiry_date=None, confidence=ud_conf),
            "signatory_id": dict(doc_type="signatory_id", legal_name=None, trade_name=None, gstin=None, udyam_number=None,
                                 person_name=owner, id_number="XXXX XXXX 4821", address=None, document_date=None,
                                 expiry_date=id_expiry, confidence=id_conf),
            "address_proof": dict(doc_type="address_proof", legal_name=None, trade_name=None, gstin=None, udyam_number=None,
                                  person_name=owner, id_number=None, address=addr_proof_addr, document_date=bill_date,
                                  expiry_date=None, confidence=ad_conf),
        }
        if not with_udyam:
            docs.pop("udyam_certificate")

        d = DOCS / kid
        d.mkdir(exist_ok=True)
        files = {}
        for dt, fields in docs.items():
            fn = {"gst_certificate": "gst_certificate", "udyam_certificate": "udyam_certificate",
                  "signatory_id": "signatory_id", "address_proof": "address_proof"}[dt]
            png = d / f"{fn}.png"
            render(png, dt, fields, blurry=(kid == "K12" and dt == "address_proof"))
            sidecar = d / f"{fn}.json"
            sidecar.write_text(json.dumps(fields, indent=2), encoding="utf-8")
            files[dt] = f"{kid}/{fn}.png"
        samples_json.append(dict(id=kid, label=label, issue=issue, typed_gstin=typed, udyam_number=udyam_no, docs=files))

    (DATA / "samples.json").write_text(json.dumps(samples_json, indent=2), encoding="utf-8")
    print("wrote", len(PRODUCTS), "products,", len(allb), "businesses,", len(samples_json), "sample applicants")


# ---------------------------------------------------------------- images
def font(size, bold=False):
    for name in (["arialbd.ttf"] if bold else ["arial.ttf"]):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
        except OSError:
            pass
    return ImageFont.load_default()


TITLES = {
    "gst_certificate": ("Government of India", "GST Registration Certificate", (31, 78, 140)),
    "udyam_certificate": ("Ministry of MSME", "Udyam Registration Certificate", (20, 110, 80)),
    "signatory_id": ("Identity Card", "Authorised signatory", (120, 60, 20)),
    "address_proof": ("Electricity Bill", "Address proof", (150, 40, 40)),
}


def render(path: Path, doc_type: str, f: dict, blurry=False):
    w, h = 900, 600
    img = Image.new("RGB", (w, h), (252, 251, 246))
    d = ImageDraw.Draw(img)
    top, title, col = TITLES[doc_type]
    d.rectangle([0, 0, w, 90], fill=col)
    d.text((30, 14), top, font=font(20), fill=(255, 255, 255))
    d.text((30, 42), title, font=font(30, True), fill=(255, 255, 255))
    rows = []
    if doc_type == "gst_certificate":
        rows = [("Legal name", f["legal_name"]), ("Trade name", f["trade_name"]), ("GSTIN", f["gstin"]),
                ("Principal place of business", f["address"]), ("Date of registration", f["document_date"])]
    elif doc_type == "udyam_certificate":
        rows = [("Enterprise name", f["legal_name"]), ("Udyam number", f["udyam_number"]),
                ("Address", f["address"]), ("Date of registration", f["document_date"])]
    elif doc_type == "signatory_id":
        rows = [("Name", f["person_name"]), ("ID number", f["id_number"]), ("Valid until", f["expiry_date"])]
    else:
        rows = [("Consumer name", f["person_name"]), ("Service address", f["address"]), ("Bill date", f["document_date"]),
                ("Amount due", "Rs 2,140")]
    y = 130
    for k, v in rows:
        d.text((40, y), k.upper(), font=font(15), fill=(120, 120, 120))
        d.text((40, y + 22), str(v), font=font(26, True), fill=(30, 30, 30))
        y += 82
    d.text((w - 330, h - 34), "SAMPLE - SYNTHETIC DATA", font=font(18, True), fill=(200, 60, 60))
    if blurry:
        from PIL import ImageFilter
        img = img.filter(ImageFilter.GaussianBlur(5))
    img.save(path)


if __name__ == "__main__":
    build()
    sys.exit(0)
