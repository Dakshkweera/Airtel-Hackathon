"""The 12 scenario scripts the demo panel replays, checked through the chat API."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.scenarios import SCENARIOS

client = TestClient(app)


def play(messages, lang="en"):
    sid = client.post("/api/session", json={"language": lang}).json()["session_id"]
    out = []
    for m in messages:
        out.append(client.post("/api/chat", json={"session_id": sid, "message": m}).json())
    return sid, out


def last_quote(out):
    for r in reversed(out):
        for m in reversed(r["messages"]):
            for c in m.get("cards", []):
                if c["type"] == "plan":
                    return c["quote"], c
    return None, None


def all_text(out):
    return " ".join(m.get("text", "") for r in out for m in r["messages"])


def run(i):
    return play(next(s for s in SCENARIOS if s["id"] == i)["messages"])[1]


def test_s1():
    q, _ = last_quote(run(1))
    assert q["plan_name"] == "Dukaan Starter" and q["totals"]["monthly"] == 1497


def test_s2_asks_at_most_5_questions():
    sid, out = play(["Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays ₹2,000 today"])
    q, _ = last_quote(out)
    assert q["totals"] == dict(monthly=3742, setup=1500, contract_months=12, expected_days=5)


def test_clinic_reaches_plan_in_five_questions_from_scratch():
    sid = client.post("/api/session", json={}).json()["session_id"]
    n = 0
    for m in ["clinic", "6 staff", "Indore", "yes", "2000"]:
        r = client.post("/api/chat", json={"session_id": sid, "message": m}).json()
        n += 1
        if any(c["type"] == "plan" for x in r["messages"] for c in x.get("cards", [])):
            break
    assert n <= 5 and any(c["type"] == "plan" for x in r["messages"] for c in x.get("cards", []))


def test_s3_salon_refused_whatsapp():
    out = run(3)
    assert "needs an active GST" in all_text(out) and "Website + Domain Starter" in all_text(out)


def test_s4_cctv_adds_broadband():
    out = run(4)
    q, _ = last_quote(out)
    assert q["items"][0]["id"] in ("P01", "P02", "P03", "P04") and q["items"][-1]["id"] == "P23"
    assert "internet connection" in all_text(out)


def test_s5_fibre_1g_refused():
    out = run(5)
    assert "not yet available in your city" in all_text(out) and "Biz Fibre 300" in all_text(out)


def test_s6_multi_store_handoff():
    q, card = last_quote(run(6))
    assert q["totals"]["monthly"] == 20780 and card["handoff"]


def test_s7_no_sdwan_for_two_stores():
    out = run(7)
    assert "at least 3 branches" in all_text(out)


def test_s8_factory():
    q, card = last_quote(run(8))
    assert q["totals"]["monthly"] == 16025 and card["handoff"]


def test_s9_leased_line_refused():
    out = run(9)
    assert "at least 10 staff" in all_text(out)


def test_s10_mobile_only_has_no_push():
    q, _ = last_quote(run(10))
    assert [i["id"] for i in q["items"]] == ["P07"] and q["extras"] == []


def test_s11_costly_gets_smaller_option_without_invented_discount():
    out = run(11)
    text = all_text(out).lower()
    assert "discount" not in text and "offer ends" not in text
    q, card = last_quote(out)
    assert card.get("smaller") and q["totals"]["monthly"] < 3742


def test_s12_cancelled_gst_blocked():
    out = run(12)
    q, _ = last_quote(out)
    p15 = next(e for e in q["extras"] if e["id"] == "P15")
    assert not p15["allowed"] and "cancelled or suspended" in p15["reason"]


def test_hindi_input_gets_hindi_reply_and_prices_stay_correct():
    sid, out = play(["मेरा क्लिनिक इंदौर में है, 6 कर्मचारी, GST है"])
    assert out[0]["lang"] == "hi"
    r = client.post("/api/chat", json={"session_id": sid, "message": "छोड़ो"}).json()
    q, _ = last_quote([r])
    assert q["totals"]["monthly"] == 3742 and q["plan_name"] == "क्लिनिक और ऑफिस प्रो"
    assert any("ऀ" <= ch <= "ॿ" for ch in q["items"][0]["reason"])


def test_clear_no_stops_selling():
    sid, out = play(["Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays ₹2,000 today", "no thanks"])
    t = all_text(out[1:])
    assert "won't push" in t
    r = client.post("/api/chat", json={"session_id": sid, "message": "ok"}).json()
    assert not any(c["type"] == "open_kyc" for m in r["messages"] for c in m.get("cards", []))
