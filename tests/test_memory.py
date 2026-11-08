"""Conversation memory and the live plan preview."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def start():
    return client.post("/api/session", json={"language": "en"}).json()["session_id"]


def chat(sid, msg):
    return client.post("/api/chat", json={"session_id": sid, "message": msg, "label": msg}).json()


def test_preview_builds_up_as_facts_arrive():
    sid = start()
    r = chat(sid, "clinic")
    p = r["preview"]
    assert p and not p["final"] and p["quote"]["plan_name"] == "Clinic & Office Pro"
    assert "staff" in p["assumed"]                       # says what it is guessing
    before = p["quote"]["totals"]["monthly"]
    r = chat(sid, "6 staff")
    assert r["preview"]["quote"]["totals"]["monthly"] == 3742 != before
    assert "staff" not in r["preview"]["assumed"]


def test_preview_is_empty_before_the_owner_says_anything():
    sid = start()
    r = client.post("/api/chat", json={"session_id": sid, "message": "hello"}).json()
    assert r["preview"] is None


def test_preview_becomes_final_when_plan_is_shown():
    sid = start()
    r = chat(sid, "Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees")
    assert r["preview"]["final"] and r["preview"]["quote"]["totals"]["monthly"] == 3742


def test_advisor_remembers_and_says_it_back():
    sid = start()
    chat(sid, "I have a clinic in Indore with 6 staff and GST")
    r = chat(sid, "what did I tell you?")
    text = r["messages"][0]["text"]
    assert "office or clinic" in text and "Indore" in text and "Staff: 6" in text and "GST: yes" in text


def test_recall_in_hindi():
    sid = start()
    chat(sid, "मेरा क्लिनिक इंदौर में है, 6 कर्मचारी")
    r = chat(sid, "मैंने क्या बताया था?")
    assert "याद" in r["messages"][0]["text"] and "6" in r["messages"][0]["text"]


def test_correction_updates_memory_and_plan():
    sid = start()
    chat(sid, "Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees")
    r = chat(sid, "actually we are 10 staff")
    assert r["profile"]["employees"] == 10
    assert any(c["type"] == "plan" for m in r["messages"] for c in m.get("cards", []))


def test_restore_returns_history_plan_and_resumes_where_we_left_off():
    sid = start()
    chat(sid, "Clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees")
    d = client.get(f"/api/session/{sid}").json()
    assert len(d["history"]) >= 3 and d["history"][0]["role"] == "bot"
    assert d["preview"]["final"] and d["profile"]["employees"] == 6
    assert any(c["type"] == "plan" for m in d["resume"] for c in m.get("cards", []))


def test_restore_midway_reasks_the_pending_question():
    sid = start()
    chat(sid, "clinic")
    d = client.get(f"/api/session/{sid}").json()
    assert d["profile"]["business_type"] == "office"
    assert d["resume"] and "How many people" in d["resume"][0]["text"]


def test_restore_unknown_session_is_404():
    assert client.get("/api/session/nope").status_code == 404
