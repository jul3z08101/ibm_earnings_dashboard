"""
Unit tests for the extraction service.
Run with: pytest tests/unit/test_extraction.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from src.services.extraction import extract_measures, FWD_LOOKING_TERMS


# ── Helpers ───────────────────────────────────────────────────────────────────

def names(result) -> set:
    return {item.name for item in result.items}

def types_for(result, name) -> str:
    return next(i.measure_type for i in result.items if i.name == name)


# ── Non-GAAP detection ────────────────────────────────────────────────────────

def test_detects_free_cash_flow():
    r = extract_measures("We generated strong free cash flow this quarter.")
    assert "Free Cash Flow" in names(r)

def test_detects_adjusted_ebitda():
    r = extract_measures("Adjusted EBITDA increased 12% year over year.")
    assert "Adjusted EBITDA" in names(r)

def test_detects_constant_currency():
    r = extract_measures("Revenue grew 8% on a constant-currency basis.")
    assert "Constant Currency Revenue" in names(r)

def test_detects_nongaap_eps():
    r = extract_measures("Non-GAAP diluted EPS was $2.43 for the quarter.")
    assert "Non-GAAP EPS" in names(r)

def test_nongaap_type_assigned_correctly():
    r = extract_measures("Adjusted EBITDA rose to $4.2B.")
    assert types_for(r, "Adjusted EBITDA") == "nongaap"


# ── KPI detection ─────────────────────────────────────────────────────────────

def test_detects_arr():
    r = extract_measures("Our Annual Recurring Revenue reached $10B.")
    assert "Annual Recurring Revenue (ARR)" in names(r)

def test_detects_cloud_revenue():
    r = extract_measures("Cloud revenue was up 20% this period.")
    assert "Cloud Revenue" in names(r)

def test_detects_qualified_bookings():
    r = extract_measures("Consulting signings were $4.5B for the quarter.")
    n = names(r)
    assert any("Signings" in name for name in n)

def test_detects_genai_bookings():
    r = extract_measures("GenAI bookings exceeded $1B in the first half.")
    n = names(r)
    assert any("Bookings" in name for name in n)


# ── GAAP detection ────────────────────────────────────────────────────────────

def test_detects_total_revenue():
    r = extract_measures("Total revenue for the quarter was $14.8B.")
    assert "Total Revenue" in names(r)

def test_detects_net_income():
    r = extract_measures("Net income attributable to IBM was $1.6B.")
    assert "Net Income" in names(r)

def test_detects_capex():
    r = extract_measures("Capital expenditures were $400M in Q2.")
    assert "Capital Expenditures (CapEx)" in names(r)


# ── Operating X reclassification ─────────────────────────────────────────────

def test_operating_reclassification():
    r = extract_measures("Our operating leverage improved significantly.")
    reclassified = [i for i in r.items if i.operating_reclassified]
    assert len(reclassified) > 0

def test_operating_income_not_reclassified():
    # "Operating Income" is a GAAP item — should not be reclassified
    r = extract_measures("Operating income was $2.1B.")
    item = next((i for i in r.items if i.name == "Operating Income"), None)
    if item:
        assert item.operating_reclassified is False


# ── Safe harbor detection ─────────────────────────────────────────────────────

def test_safe_harbor_present():
    r = extract_measures("These statements contain safe harbor language as required by the PSLRA.")
    assert r.has_safe_harbor is True

def test_safe_harbor_absent_with_fwd_looking():
    r = extract_measures("We expect revenue to grow 5% next year.")
    assert r.has_safe_harbor is False
    assert r.has_fwd_looking is True

def test_no_fwd_looking():
    r = extract_measures("Revenue was $14.8B and net income was $1.6B.")
    assert r.has_fwd_looking is False


# ── Context snippets ──────────────────────────────────────────────────────────

def test_context_snippet_captured():
    r = extract_measures("Our free cash flow for the quarter was $2.1 billion, up 15%.")
    item = next(i for i in r.items if i.name == "Free Cash Flow")
    assert len(item.contexts) > 0
    assert "free cash flow" in item.contexts[0].lower()

def test_char_count_returned():
    text = "Total revenue was $14.8B."
    r = extract_measures(text)
    assert r.char_count == len(text)
