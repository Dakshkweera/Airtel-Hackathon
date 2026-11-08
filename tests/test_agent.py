"""Custom plan flow, the LLM agent (model call mocked), and the no-key fallbacks."""
import json

import pytest
from fastapi.testclient import TestClient

from app import llm_agent
from app.main import app

client = TestClient(app)


def start():
    return client.post("/api/session", json={"language": "en"}).json()["session_id"]


def chat(sid, msg="", payload=None):
    return client.post("/api/chat", json={"session_id": sid, "message": msg, "payload": payload, "label": msg}).json()


def text_of(r):
    return " ".join(m.get("text", "") for m in r["messages"])


def need(sid, pid, qty=1):
    return chat(sid, payload={"action": "need", "id": pid, "qty": qty})


# ------------------------------------------------------------------ custom plan
def test_greeting_offers_build_your_own():
    r = client.post("/api/session", json={}).json()
    assert any(c.get("action") == "custom" for c in r["messages"][0]["chips"])


def test_custom_cost_updates_in_real_time_and_estimate_is_flagged():
    sid = start()
    r = chat(sid, payload={"action": "custom"})
    assert any(c["type"] == "needs" for m in r["messages"] for c in m.get("cards", [])) and r["needs"]
    r = need(sid, "P07")
    assert r["preview"]["quote"]["totals"]["monthly"] == 299 and not r["preview"]["final"]
    assert set(r["preview"]["pending"]) == {"city", "staff", "gst"}
    r = need(sid, "P07", 3)
    assert r["preview"]["quote"]["totals"]["monthly"] == 897
    r = need(sid, "P07", 0)
    assert r["preview"] is None


def test_custom_cctv_pulls_in_internet_and_says_why():
    sid = start()
    chat(sid, payload={"action": "custom"})
    r = need(sid, "P23")
    assert "internet connection" in text_of(r) or any(n for n in r["preview"]["quote"]["notes"])
    assert {i["id"] for i in r["preview"]["quote"]["items"]} >= {"P23"}
    assert any(i["id"] in ("P01", "P02", "P03", "P04") for i in r["preview"]["quote"]["items"])


def test_custom_typed_requests_are_understood_with_quantities():
    sid = start()
    chat(sid, payload={"action": "custom"})
    r = chat(sid, "I need 3 mobile lines and a website")
    ids = {i["id"]: i["qty"] for i in r["preview"]["quote"]["items"]}
    assert ids == {"P07": 3, "P18": 1}
    r = chat(sid, "remove the website")
    assert "P18" not in {i["id"] for i in r["preview"]["quote"]["items"]}


def test_custom_gst_item_is_refused_once_gst_is_known_to_be_missing():
    sid = start()
    chat(sid, payload={"action": "custom"})
    need(sid, "P15")                                           # pending GST, allowed for the estimate
    chat(sid, payload={"slot": "city", "value": "Indore"})
    chat(sid, payload={"slot": "counts", "staff": 3, "sites": 1})
    r = chat(sid, payload={"slot": "gst", "value": False})
    assert "P15" not in {i["id"] for i in (r["preview"] or {"quote": {"items": []}})["quote"]["items"]}
    assert "needs an active GST" in text_of(r)


def test_custom_suggests_once_without_pressure_and_stops_after_no():
    sid = start()
    chat(sid, payload={"action": "custom"})
    chat(sid, payload={"slot": "city", "value": "Mumbai"})
    chat(sid, payload={"slot": "counts", "staff": 4, "sites": 1})
    chat(sid, payload={"slot": "gst", "value": True})
    r = need(sid, "P02")
    assert "Backup" in text_of(r) and "No pressure" in text_of(r)
    assert any(c.get("action") == "suggest_no" for m in r["messages"] for c in m.get("chips", []))
    chat(sid, payload={"action": "suggest_no"})
    r = need(sid, "P16", 4)
    assert "Many people" not in text_of(r)                    # no more suggestions after a no


def test_custom_done_gives_a_plan_with_exactly_what_was_picked():
    sid = start()
    chat(sid, payload={"action": "custom"})
    need(sid, "P03"); need(sid, "P07")
    for p in ({"slot": "city", "value": "Pune"}, {"slot": "counts", "staff": 2, "sites": 1}, {"slot": "gst", "value": False}):
        chat(sid, payload=p)
    r = chat(sid, payload={"action": "custom_done"})
    card = next(c for m in r["messages"] for c in m.get("cards", []) if c["type"] == "plan")
    assert {i["id"] for i in card["quote"]["items"]} == {"P03", "P07"} and card["quote"]["totals"]["monthly"] == 799 + 299
    assert r["preview"]["final"] and r["needs"] is None
    # the plan stays custom when facts change later: no standard plan is swapped in
    r = chat(sid, "I pay 2000 rupees today")
    card = next(c for m in r["messages"] for c in m.get("cards", []) if c["type"] == "plan")
    assert card["quote"]["plan_key"] == "custom" and card["quote"]["savings"]["diff"] == 2000 - 1098


def test_custom_explains_a_product_without_adding_it():
    sid = start()
    chat(sid, payload={"action": "custom"})
    r = chat(sid, "why do I need backup internet?")
    assert "Backup internet takes over" in text_of(r) and r["preview"] is None


def test_custom_done_before_anything_picked_asks_to_pick():
    sid = start()
    chat(sid, payload={"action": "custom"})
    assert "Nothing picked" in text_of(chat(sid, payload={"action": "custom_done"}))


def test_typing_build_my_own_plan_starts_it():
    sid = start()
    assert any(c["type"] == "needs" for m in chat(sid, "I want to build my own plan")["messages"] for c in m.get("cards", []))


# ------------------------------------------------------------------ no-key fallbacks understand more
def test_unknown_kind_of_business_is_not_rejected():
    sid = start()
    r = chat(sid, "I sell handmade candles from home")
    assert r["profile"]["business_type"] == "shop" and "small shop" in text_of(r)


def test_a_greeting_is_not_a_business():
    sid = start()
    assert "business_type" not in chat(sid, "hello")["profile"]


def test_spend_in_words_and_k():
    sid = start()
    assert chat(sid, "clinic in Mumbai Tier 1 6 staff GST, I pay 2k a month")["profile"]["monthly_spend"] == 2000
    sid = start()
    assert chat(sid, "clinic in Mumbai Tier 1 6 staff GST, spend about two thousand per month")["profile"]["monthly_spend"] == 2000


def test_price_questions_get_a_factual_answer_and_the_chat_continues():
    sid = start()
    chat(sid, "clinic")
    r = chat(sid, "how much is CCTV?")
    assert "₹799" in text_of(r) and "How many people" in text_of(r)


def test_gst_answers_in_natural_words():
    for said, expect in (("haan hai mere paas", True), ("nahi hai abhi", False), ("we don't have it", False), ("yes we have it", True)):
        sid = start()
        chat(sid, "clinic in Mumbai Tier 1 6 staff")
        assert chat(sid, said)["profile"].get("has_gstin") is expect, said


# ------------------------------------------------------------------ LLM agent (model mocked)
def scripted(monkeypatch, steps, seen=None):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    it = iter(steps)

    def fake(messages, tools):
        if seen is not None:
            seen.append(messages)
        return next(it)
    monkeypatch.setattr(llm_agent, "_http_chat", fake)


def call(i, name, **args):
    return {"id": f"c{i}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


def test_agent_writes_the_words_but_prices_come_from_tools(monkeypatch):
    scripted(monkeypatch, [
        {"content": "", "tool_calls": [call(1, "save_profile", business_type="office", employees=6, sites=1, city="Mumbai", has_gstin=True, monthly_spend=2000),
                                       call(2, "recommend_plan")]},
        {"content": "Namaste Doctor! A clinic like yours does well on Clinic & Office Pro. Shall we start the paperwork?"},
    ])
    sid = start()
    r = chat(sid, "bhai mera clinic hai Mumbai me, 6 log, GST hai, abhi 2000 dete hain")
    assert r["messages"][0]["text"].startswith("Namaste Doctor")
    card = next(c for m in r["messages"] for c in m.get("cards", []) if c["type"] == "plan")
    assert card["quote"]["totals"]["monthly"] == 3742
    assert r["preview"]["final"] and r["profile"]["employees"] == 6
    assert any(t["tool"] == "llm" for t in r["trace"])
    assert any(c.get("action") == "start_kyc" for m in r["messages"] for c in m.get("chips", []))


def test_agent_gets_refusals_from_the_rules_engine(monkeypatch):
    seen = []
    scripted(monkeypatch, [
        {"content": "", "tool_calls": [call(1, "save_profile", business_type="salon", employees=3, sites=1, city="Pune", has_gstin=False),
                                       call(2, "check_eligibility", ids=["P15"])]},
        {"content": "WhatsApp Business needs a GST number, so not yet. A website works without one."},
    ], seen)
    sid = start()
    chat(sid, "salon owner, want whatsapp business, no gst")
    tool_msgs = [m for m in seen[1] if m["role"] == "tool"]
    assert any("needs an active GST" in m["content"] for m in tool_msgs)


def test_agent_sees_state_and_history_for_memory(monkeypatch):
    seen = []
    scripted(monkeypatch, [{"content": "Sure."}, {"content": "You said Indore."}], seen)
    sid = start()
    chat(sid, "I have a clinic in Indore")
    chat(sid, "where is my business?")
    second = seen[1]
    assert any(m["role"] == "user" and "Indore" in m["content"] for m in second)       # earlier turn is in the history
    assert any(m["role"] == "system" and "STATE" in m["content"] for m in second)


def test_agent_failure_falls_back_to_the_keyword_advisor(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def boom(messages, tools):
        raise OSError("network down")
    monkeypatch.setattr(llm_agent, "_http_chat", boom)
    sid = start()
    r = chat(sid, "clinic in Mumbai, Tier 1, 6 staff, GSTIN, pays 2000 rupees")
    card = next(c for m in r["messages"] for c in m.get("cards", []) if c["type"] == "plan")
    assert card["quote"]["totals"]["monthly"] == 3742                                   # still works


def test_agent_custom_products_and_handoff(monkeypatch):
    scripted(monkeypatch, [
        {"content": "", "tool_calls": [call(1, "set_products", ops=[{"id": "P23", "qty": 2}, {"id": "P07", "qty": 3}])]},
        {"content": "Added. Running total is on the right."},
    ])
    sid = start()
    r = chat(sid, "I want 2 cctv cameras and 3 mobile lines")
    ids = {i["id"]: i["qty"] for i in r["preview"]["quote"]["items"]}
    assert ids["P23"] == 2 and ids["P07"] == 3 and any(k in ids for k in ("P03", "P02", "P04", "P01"))
    scripted(monkeypatch, [{"content": "", "tool_calls": [call(1, "handoff_to_human", reason="owner asked")]}, {"content": "Done, sales will call."}])
    r = chat(sid, "let me talk to someone")
    assert any(c["type"] == "handoff" for m in r["messages"] for c in m.get("cards", []))


def test_agent_chip_taps_are_understood_too(monkeypatch):
    seen = []
    scripted(monkeypatch, [{"content": "Got it, Indore."}], seen)
    sid = start()
    chat(sid, payload={"slot": "city", "value": "Indore"})
    assert any(m["role"] == "user" and "city" in m["content"] and "Indore" in m["content"] for m in seen[0])


def test_listing_needs_in_plain_words_switches_to_custom_plan_automatically():
    sid = start()
    r = chat(sid, "I sell handmade candles from home, need 2 mobile lines and a website")
    assert r["needs"] is not None                                           # the picker is up
    ids = {i["id"]: i["qty"] for i in r["preview"]["quote"]["items"]}
    assert ids == {"P07": 2, "P18": 1}
    assert "Running total" in text_of(r)


def test_unrelated_sentence_still_gets_a_useful_reply_not_a_dead_end():
    sid = start()
    r = chat(sid, "my brother also runs a similar place, we are thinking about it")
    assert r["profile"]["business_type"] == "shop" and "small shop" in text_of(r)
    assert "How many people" in text_of(r)                                  # moves on to the next question


def test_unrecognised_sentence_after_a_plan_keeps_the_plan_and_does_not_redo_it():
    """Regression from a real session: 'let me give you paper' re-ran recommend and the hand-off."""
    sid = start()
    r = chat(sid, "shop in Haldwani, 20 staff, 3 branches, no GST, skip")
    n_leads = sum(1 for t in r["trace"] if t["tool"] == "handoff_to_human")
    r2 = chat(sid, "blah something completely unrelated")
    assert not any(c["type"] == "plan" for m in r2["messages"] for c in m.get("cards", []))
    assert not any(t["tool"] in ("recommend_plan", "handoff_to_human") for t in r2["trace"])
    assert "didn't catch that" in text_of(r2) and any(c.get("action") == "start_kyc" for m in r2["messages"] for c in m.get("chips", []))


def test_give_you_paper_opens_the_paperwork_even_for_a_big_order():
    sid = start()
    chat(sid, "shop in Haldwani, 20 staff, 3 branches, no GST, skip")
    r = chat(sid, "let me give you paper")
    assert any(c["type"] == "open_kyc" for m in r["messages"] for c in m.get("cards", []))
    assert not any(t["tool"] == "recommend_plan" for t in r["trace"])


def test_big_orders_can_still_choose_to_continue_online():
    sid = start()
    r = chat(sid, "4-store restaurant chain in Delhi, 20 staff, GSTIN, skip")
    chips = [c for m in r["messages"] for c in m.get("chips", [])]
    assert any(c.get("action") == "start_kyc" and "online" in c["label"] for c in chips)


def test_spend_chip_after_a_custom_plan_keeps_it_custom():
    sid = start()
    chat(sid, payload={"action": "custom"})
    need(sid, "P03"); need(sid, "P07")
    for p in ({"slot": "city", "value": "Pune"}, {"slot": "counts", "staff": 2, "sites": 1}, {"slot": "gst", "value": False}):
        chat(sid, payload=p)
    chat(sid, payload={"action": "custom_done"})
    chat(sid, payload={"action": "ask_spend"})
    r = chat(sid, payload={"slot": "spend", "value": 2000})
    card = next(c for m in r["messages"] for c in m.get("cards", []) if c["type"] == "plan")
    assert card["quote"]["plan_key"] == "custom" and card["quote"]["savings"]["spend"] == 2000


def test_voice_transcript_in_another_script_does_not_flip_the_language():
    sid = start()
    r = client.post("/api/chat", json={"session_id": sid, "message": "केन वे कंटिन्यू राइट हेरे", "voice": True}).json()
    assert r["lang"] == "en"
    r = client.post("/api/chat", json={"session_id": sid, "message": "मेरा क्लिनिक है"}).json()   # typed Hindi still switches
    assert r["lang"] == "hi"


def test_agent_big_order_still_gets_a_way_forward(monkeypatch):
    scripted(monkeypatch, [
        {"content": "", "tool_calls": [call(1, "save_profile", business_type="shop", employees=20, sites=3), call(2, "handoff_to_human", reason="3 branches"),
                                       call(3, "recommend_plan")]},
        {"content": "Sales will help, and here is an indicative plan. You can also continue online."},
    ])
    sid = start()
    r = chat(sid, "I have over 20 people and three shops")
    assert any(c["type"] == "plan" for m in r["messages"] for c in m.get("cards", []))
    assert any(c.get("action") == "start_kyc" for m in r["messages"] for c in m.get("chips", []))


def test_agent_state_tells_the_model_what_to_do_next(monkeypatch):
    seen = []
    scripted(monkeypatch, [{"content": "ok"}, {"content": "ok"}], seen)
    sid = start()
    chat(sid, "hello there")
    assert "ask what kind of business" in json.dumps([m["content"] for m in seen[0] if m["role"] == "system"])
    S = __import__("app.main", fromlist=["SESSIONS"]).SESSIONS[sid]
    S["profile"].update(business_type="office", employees=6, sites=1)
    chat(sid, "ok so")
    assert "call recommend_plan NOW" in json.dumps([m["content"] for m in seen[1] if m["role"] == "system"])


def test_agent_retries_once_before_falling_back(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    calls = {"n": 0}

    def flaky(messages, tools):
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("blip")
        return {"content": "Recovered fine."}
    monkeypatch.setattr(llm_agent, "_http_chat", flaky)
    sid = start()
    r = chat(sid, "hello")
    assert r["messages"][0]["text"] == "Recovered fine." and calls["n"] == 2


def test_agent_offers_a_plan_chip_when_business_known_but_no_plan_yet(monkeypatch):
    scripted(monkeypatch, [{"content": "", "tool_calls": [call(1, "save_profile", business_type="office")]}, {"content": "Nice, a clinic. How many staff?"}])
    sid = start()
    r = chat(sid, "I run a clinic")
    assert any("plan" in (c.get("text") or "") for m in r["messages"] for c in m.get("chips", []))


# ------------------------------------------------------------------ language follows the owner automatically
def test_voice_follows_the_script_of_the_text_not_the_toggle():
    from app import tts
    assert tts.pick_lang("मुझे खेद है GST", "en") == "hi"
    assert tts.pick_lang("तुमचा प्लान तयार आहे", "mr") == "mr"
    assert tts.pick_lang("உங்கள் திட்டம் தயார்", "en") == "ta"
    assert tts.pick_lang("మీ ప్లాన్ సిద్ధం", "en") == "te"
    assert tts.pick_lang("Your plan is ready", "en") == "en"
    assert tts.pick_lang("Your plan is ready", "xx") == "en"          # unknown language: English, never a crash


def test_tts_cleaning_is_localised():
    from app import tts
    assert "रुपये" in tts.clean("₹3,742/month", "hi") and "3742" in tts.clean("₹3,742/month", "hi")
    assert "rupees per month" in tts.clean("₹3,742/month", "en")


def test_agent_sets_the_language_and_the_reply_reports_it(monkeypatch):
    scripted(monkeypatch, [
        {"content": "", "tool_calls": [call(1, "set_language", code="mr")]},
        {"content": "नमस्कार! तुमचा व्यवसाय कोणता आहे?"},
    ])
    sid = start()
    r = chat(sid, "mala ek dukan aahe")
    assert r["speech_lang"] == "mr" and r["lang"] == "hi"             # Marathi uses the Hindi screen text
    assert any(t["tool"] == "set_language" for t in r["trace"])


def test_agent_is_told_the_current_language_and_to_follow_the_owner(monkeypatch):
    seen = []
    scripted(monkeypatch, [{"content": "ok"}], seen)
    sid = start()
    chat(sid, "hello")
    system = json.dumps([m["content"] for m in seen[0] if m["role"] == "system"])
    assert "reply_language" in system and "set_language" in system and "native script" in system


def test_manual_language_choice_sets_speech_language_too():
    sid = start()
    r = client.post("/api/lang", json={"session_id": sid, "language": "hi", "speech_lang": "ta"}).json()
    assert r["lang"] == "hi"
    assert chat(sid, "hello")["speech_lang"] == "ta"


def test_greeting_says_any_language_is_fine():
    r = client.post("/api/session", json={}).json()
    assert "any language" in r["messages"][0]["text"] and r["speech_lang"] == "en"


# ------------------------------------------------------------------ paperwork: "where do I upload?"
def at_paperwork():
    sid = start()
    chat(sid, "shop in Haldwani, 20 staff, 3 branches, no GST, skip")
    chat(sid, payload={"action": "start_kyc"})
    return sid


def test_asking_where_to_upload_reopens_the_paperwork_screen():
    sid = at_paperwork()
    for said in ("where do I submit the PDF? I can't see the button",
                 "मुझे बताओ कि मुझे पीडीएफ कहां सबमिट करनी है वह मुझे ऑप्शन नहीं दिख रहा है बटन",
                 "how do I upload my documents"):
        r = chat(sid, said)
        assert any(c["type"] == "open_kyc" for m in r["messages"] for c in m.get("cards", [])), said
        assert "PDF" in text_of(r) and any(c.get("action") == "start_kyc" for m in r["messages"] for c in m.get("chips", []))


def test_reopen_works_even_if_the_ai_is_down_or_slow(monkeypatch):
    sid = at_paperwork()
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def boom(messages, tools):
        raise AssertionError("the model must not be needed to re-open the screen")
    monkeypatch.setattr(llm_agent, "_http_chat", boom)
    r = chat(sid, "where is the upload option")
    assert any(c["type"] == "open_kyc" for m in r["messages"] for c in m.get("cards", []))


def test_no_profile_questions_are_asked_while_paperwork_is_open():
    sid = at_paperwork()
    r = chat(sid, "hmm okay")
    assert "What do you pay" not in text_of(r) and any(c["type"] == "open_kyc" for m in r["messages"] for c in m.get("cards", []))


def test_agent_always_offers_the_open_paperwork_button_during_kyc(monkeypatch):
    sid = at_paperwork()
    scripted(monkeypatch, [{"content": "Sure, tell me about the documents."}])
    r = chat(sid, "tell me about aadhaar privacy")           # no upload words: goes to the model
    assert any(c.get("action") == "start_kyc" for m in r["messages"] for c in m.get("chips", []))
