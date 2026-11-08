"""Applicants K01-K12 run through the same API the UI uses."""
import pytest
from fastapi.testclient import TestClient

from app import data, kyc
from app.main import app

client = TestClient(app)

# applicant -> (overall result, id of the check that should be flagged or None)
EXPECTED = {
    "K01": ("pass", None), "K02": ("fail", "names"), "K03": ("fail", "gst_on_cert"), "K04": ("fail", "bill_date"),
    "K05": ("fail", "docs"), "K06": ("pass", "gstin"), "K07": ("pass", "gstin"), "K08": ("fail", "id"),
    "K09": ("fail", "address"), "K10": ("fail", "gstin"), "K11": ("fail", "udyam"), "K12": ("review", "address"),
}


def session(msg=None):
    sid = client.post("/api/session", json={"language": "en"}).json()["session_id"]
    if msg:
        client.post("/api/chat", json={"session_id": sid, "message": msg})
    return sid


def run_applicant(kid, sid=None):
    sid = sid or session()
    assert client.post("/api/kyc/gstin", json={"session_id": sid, "gstin": "x"}).status_code == 403  # consent first
    client.post("/api/consent", json={"session_id": sid})
    s = next(x for x in data.SAMPLES if x["id"] == kid)
    client.post("/api/kyc/gstin", json={"session_id": sid, "gstin": s["typed_gstin"]})
    client.post("/api/kyc/udyam", json={"session_id": sid, "udyam_number": s["udyam_number"]})
    for dt, path in s["docs"].items():
        client.post("/api/kyc/upload", data={"session_id": sid, "doc_type": dt, "sample": path})
    return client.post("/api/kyc/verify", json={"session_id": sid}).json()


@pytest.mark.parametrize("kid", list(EXPECTED))
def test_applicant(kid):
    res = run_applicant(kid)
    overall, flagged = EXPECTED[kid]
    assert res["overall"] == overall, res
    if flagged:
        c = next(c for c in res["checks"] if c["id"] == flagged)
        assert c["passed"] is False or c["review"], c
        assert c["message"]


def test_checksum_matches_whole_registry():
    assert data.GSTIN_REG and all(kyc.gstin_valid(g) for g in data.GSTIN_REG)


def test_x_as_fourth_pan_character_is_accepted():
    g = "27ABCXE1234F1Z"
    assert kyc.GSTIN_RE.match(g + kyc.gstin_check_char(g))


def test_cancelled_gst_removes_gst_products_from_plan():
    sid = session("Kirana shop in Ahmedabad, 3 staff, GSTIN, pays 1000 rupees")
    client.post("/api/consent", json={"session_id": sid})
    s = next(x for x in data.SAMPLES if x["id"] == "K06")
    r = client.post("/api/kyc/gstin", json={"session_id": sid, "gstin": s["typed_gstin"]}).json()
    assert r["plan_changed"] and "cancelled or suspended" in r["message"]
    assert all(e["allowed"] is False for e in r["quote"]["extras"] if e["id"] == "P15")


def test_full_happy_path_creates_order_and_tracker_advances():
    sid = session("Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees")
    assert run_applicant("K01", sid)["overall"] == "pass"
    o = client.post("/api/order", json={"session_id": sid}).json()["order"]
    assert o["expected_days"] == 5 and o["stage"] == 0
    for _ in range(4):
        o = client.post(f"/api/order/{o['id']}/advance").json()["order"]
    assert o["done"] and o["stages"][-1] == "Service started"


def test_order_refused_until_paperwork_passes():
    sid = session("Clinic in Mumbai, Tier 1, 6 staff, GSTIN")
    assert client.post("/api/order", json={"session_id": sid}).status_code == 409
