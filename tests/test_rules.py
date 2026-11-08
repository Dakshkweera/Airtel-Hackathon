"""The PRD's advisor cases at rules level: no LLM involved."""
from app import rules


def prof(**k):
    p = dict(business_type="office", employees=6, sites=1, city="Mumbai", city_tier=1, has_gstin=True,
             gstin_status="Active", monthly_spend=0)
    p.update(k)
    return p


def ids(q):
    return [i["id"] for i in q["items"]]


def refused(q):
    return {r["id"]: r for r in q["refused"]}


def test_1_kirana_no_gst_gets_dukaan_starter():
    q = rules.recommend_plan(prof(business_type="shop", employees=2, city_tier=2, has_gstin=False))
    assert q["plan_name"] == "Dukaan Starter"
    assert q["totals"]["monthly"] == 1497 and q["totals"]["setup"] == 0
    p15 = next(e for e in q["extras"] if e["id"] == "P15")
    assert not p15["allowed"] and "GST" in p15["reason"]


def test_2_clinic_pro():
    q = rules.recommend_plan(prof(monthly_spend=2000))
    assert (q["plan_name"], q["totals"]["monthly"], q["totals"]["setup"], q["totals"]["contract_months"]) == ("Clinic & Office Pro", 3742, 1500, 12)
    assert q["totals"]["expected_days"] == 5
    assert q["savings"]["diff"] == 2000 - 3742  # honest: costs more than today


def test_toggle_cloud_backup_changes_total():
    p = prof()
    q = rules.recommend_plan(p)
    q2 = rules.build_quote(p, {**q["quantities"], "P17": 1}, plan_key="clinic")
    assert q2["totals"]["monthly"] == 4241


def test_3_salon_whatsapp_business_refused_without_gst():
    r = rules.check_eligibility(prof(business_type="salon", has_gstin=False), ["P15"])
    assert r["allowed"] == [] and r["refused"][0]["id"] == "P15"
    assert "GST" in r["refused"][0]["reason"]
    assert r["refused"][0]["alt_plan"] == "dukaan" and any(a["id"] == "P18" for a in r["refused"][0]["alternatives"])


def test_4_cctv_alone_gets_broadband_first():
    q = rules.build_quote(prof(city_tier=2), {"P23": 1})
    assert ids(q)[0] in ("P01", "P02", "P03", "P04") and "P23" in ids(q)
    assert q["notes"] and "internet" in q["notes"][0]["reason"]


def test_5_tier2_office_refused_fibre_1g():
    r = rules.check_eligibility(prof(city_tier=2), ["P01"])
    assert r["refused"][0]["code"] == "city"
    assert "P02" in [a["id"] for a in r["refused"][0]["alternatives"]]


def test_6_restaurant_chain_multi_store():
    q = rules.recommend_plan(prof(business_type="restaurant", employees=20, sites=4))
    assert q["plan_name"] == "Multi-Store Connect" and q["totals"]["monthly"] == 20780
    assert q["handoff"]


def test_7_two_store_chain_no_sdwan():
    q = rules.recommend_plan(prof(business_type="restaurant", employees=9, sites=2))
    assert refused(q)["P10"]["code"] == "sites" and "P10" not in ids(q)
    assert "P09" in ids(q)  # failover per store
    assert not q["handoff"]


def test_8_factory_connect():
    q = rules.recommend_plan(prof(business_type="factory", employees=30, sites=1))
    assert q["plan_name"] == "Factory Connect" and q["totals"]["monthly"] == 16025 and q["totals"]["setup"] == 45500
    assert q["handoff"]


def test_9_small_factory_refused_leased_line():
    q = rules.recommend_plan(prof(business_type="factory", employees=8, sites=1))
    assert refused(q)["P05"]["code"] == "staff"
    assert "P05" not in ids(q) and ("P02" in ids(q) or "P01" in ids(q))


def test_10_mobile_only():
    q = rules.recommend_plan(prof(business_type="mobile"))
    assert ids(q) == ["P07"] and q["totals"]["monthly"] == 299 and not q["extras"]


def test_12_cancelled_gst_blocks_gst_products():
    p = prof(gstin_status="Cancelled")
    r = rules.check_eligibility(p, ["P15"])
    assert r["refused"][0]["code"] == "gst_blocked" and "cancelled or suspended" in r["refused"][0]["reason"]


def test_never_an_ineligible_product_or_wrong_total():
    for emp in (1, 5, 12):
        for sites in (1, 2, 4):
            for bt in ("shop", "office", "factory", "restaurant", "salon", "mobile"):
                for tier in (1, 2, 3):
                    for gst in (True, False):
                        p = prof(business_type=bt, employees=emp, sites=sites, city_tier=tier, has_gstin=gst)
                        q = rules.recommend_plan(p)
                        for i in q["items"]:
                            assert rules.eligibility(i["id"], p) is None
                        assert q["totals"]["monthly"] == sum(rules.P[i["id"]]["price"] * i["qty"] for i in q["items"])
