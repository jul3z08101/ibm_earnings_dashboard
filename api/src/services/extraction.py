"""
extraction.py — Measure and KPI detection service.

Ported from the EXTRACTION_PATTERNS and extraction logic in dashboard.html.
Produces structured extraction results with context snippets for reviewer triage.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

# Stop words for qualifier filtering (mirrors JS STOPS set)
_STOPS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for",
    "with", "our", "its", "all", "new", "total", "both", "each", "these",
    "those", "their", "this", "that", "said", "any", "some", "such", "per",
    "as", "by", "we", "i", "it", "is", "was", "are", "were",
}

# Words that indicate a GAAP line item — suppress operating X non-GAAP reclassification
_GAAP_NOUNS = {
    "income", "profit", "cash", "flow", "expense", "cost", "costs",
    "loss", "lease", "activity", "activities", "revenue", "margin", "expenditure",
    "expenditures", "tax", "taxes", "provision",
}

# Forward-looking terms for safe-harbor detection
FWD_LOOKING_TERMS = [
    "expect", "anticipate", "forecast", "guidance", "outlook", "project",
    "believe", "estimate", "intend", "plan to", "we see", "going forward",
    "will be", "full year",
]


@dataclass
class ExtractionPattern:
    pattern: str          # Python regex string (case-insensitive)
    name: str             # Canonical label
    measure_type: str     # nongaap | kpi | gaap
    category: str         # cashflow | profitability | margin | revenue | growth | cloud | backlog | liquidity | other
    qualified: bool = False   # True for signings/bookings — capture leading qualifier


# Pattern definitions — comprehensive operating statement and non-GAAP metrics
EXTRACTION_PATTERNS: List[ExtractionPattern] = [
    # Non-GAAP Measures — Cash Flow and Liquidity
    ExtractionPattern(r"\bfree cash flow\b",                        "Free Cash Flow",                   "nongaap", "cashflow"),
    ExtractionPattern(r"\badjusted\s+(?:free\s+)?cash\s+flow\b",   "Adjusted Free Cash Flow",           "nongaap", "cashflow"),
    ExtractionPattern(r"\bnet\s+debt\b",                            "Net Debt",                         "nongaap", "liquidity"),
    ExtractionPattern(r"\bcash\s+conversion\s+(?:rate|cycle)?\b",  "Cash Conversion",                  "nongaap", "liquidity"),

    # Non-GAAP Measures — Profitability and Margins
    ExtractionPattern(r"\badjusted\s+ebitda\b",                     "Adjusted EBITDA",                  "nongaap", "profitability"),
    ExtractionPattern(r"\bebitda\b",                                "EBITDA",                           "nongaap", "profitability"),
    ExtractionPattern(r"\bnon[\-\s]gaap\s+(?:operating\s+)?(?:earnings|income|profit)\b", "Non-GAAP Operating Income", "nongaap", "profitability"),
    ExtractionPattern(r"\badjusted\s+(?:operating\s+)?(?:earnings|income|profit)\b",      "Adjusted Operating Income", "nongaap", "profitability"),
    ExtractionPattern(r"\bnon[\-\s]gaap\s+(?:gross\s+)?(?:margin|profit)\b", "Non-GAAP Gross Margin", "nongaap", "margin"),
    ExtractionPattern(r"\badjusted\s+gross\s+(?:margin|profit)\b",  "Adjusted Gross Margin",            "nongaap", "margin"),
    ExtractionPattern(r"\bnon[\-\s]gaap\s+(?:net\s+)?(?:income|earnings)\b", "Non-GAAP Net Income",    "nongaap", "profitability"),
    ExtractionPattern(r"\badjusted\s+net\s+(?:income|earnings)\b",  "Adjusted Net Income",              "nongaap", "profitability"),
    ExtractionPattern(r"\bnon[\-\s]gaap\s+(?:diluted\s+)?(?:eps|earnings\s+per\s+share)\b", "Non-GAAP EPS", "nongaap", "profitability"),
    ExtractionPattern(r"\badjusted\s+(?:diluted\s+)?(?:eps|earnings\s+per\s+share)\b",    "Adjusted EPS", "nongaap", "profitability"),
    ExtractionPattern(r"\bconstant[\s\-]currency\b",                "Constant Currency Revenue",        "nongaap", "revenue"),
    ExtractionPattern(r"\borganic\s+(?:revenue\s+)?growth\b",       "Organic Revenue Growth",           "nongaap", "growth"),
    ExtractionPattern(r"\bpro[\s\-]forma\b",                        "Pro Forma Results",                "nongaap", "other"),
    ExtractionPattern(r"\bnormalized\s+(?:earnings|income|revenue)\b", "Normalized Earnings",           "nongaap", "profitability"),
    ExtractionPattern(r"\bunderlying\s+(?:earnings|income|revenue|growth)\b", "Underlying Revenue Growth", "nongaap", "growth"),
    ExtractionPattern(r"\bcore\s+(?:revenue|income|earnings)\b",    "Core Revenue",                     "nongaap", "revenue"),

    # Full GAAP Operating Statement Line Items
    ExtractionPattern(r"\btotal\s+revenue\b|\bnet\s+sales\b",       "Total Revenue",                    "gaap", "revenue"),
    ExtractionPattern(r"\bcost\s+of\s+(?:goods\s+sold|revenue|services)\b|\bcogs\b", "Cost of Revenue", "gaap", "cost"),
    ExtractionPattern(r"\bgross\s+profit\b",                        "Gross Profit",                     "gaap", "profitability"),
    ExtractionPattern(r"\bresearch\s+and\s+development\b|\br&d\b",  "Research & Development (R&D)",     "gaap", "cost"),
    ExtractionPattern(r"\bselling,?\s+general\s+(?:and|&)\s+administrative\b|\bsg&a\b", "SG&A Expense", "gaap", "cost"),
    ExtractionPattern(r"\btotal\s+operating\s+expenses?\b",         "Total Operating Expenses",         "gaap", "cost"),
    ExtractionPattern(r"\boperating\s+(?:income|profit)\b",         "Operating Income",                 "gaap", "profitability"),
    ExtractionPattern(r"\binterest\s+expense\b",                    "Interest Expense",                 "gaap", "cost"),
    ExtractionPattern(r"\bpre[\-\s]tax\s+income\b|\bincome\s+before\s+(?:income\s+)?taxes\b", "Pre-Tax Income", "gaap", "profitability"),
    ExtractionPattern(r"\bprovision\s+for\s+income\s+taxes\b|\btax\s+expense\b", "Provision for Income Taxes", "gaap", "cost"),
    ExtractionPattern(r"\bnet\s+income\b",                          "Net Income",                       "gaap", "profitability"),
    ExtractionPattern(r"\bbasic\s+(?:eps|earnings\s+per\s+share)\b", "Basic EPS",                       "gaap", "profitability"),
    ExtractionPattern(r"\bearnings\s+per\s+share\b|\bdiluted\s+eps\b", "Diluted EPS",                  "gaap", "profitability"),
    ExtractionPattern(r"\boperating\s+cash\s+flow\b|\bcash\s+provided\s+by\s+operating\s+activities\b", "Operating Cash Flow", "gaap", "cashflow"),
    ExtractionPattern(r"\bcapital\s+expenditures?\b|\bcapex\b",     "Capital Expenditures (CapEx)",     "gaap", "cashflow"),
    ExtractionPattern(r"\bcash\s+and\s+cash\s+equivalents\b",       "Cash & Cash Equivalents",          "gaap", "liquidity"),
    ExtractionPattern(r"\btotal\s+debt\b",                          "Total Debt",                       "gaap", "liquidity"),

    # KPI / Operational Metrics
    ExtractionPattern(r"\bannual\s+recurring\s+revenue\b|\barr\b",  "Annual Recurring Revenue (ARR)",   "kpi", "cloud"),
    ExtractionPattern(r"\bmonthly\s+recurring\s+revenue\b|\bmrr\b", "Monthly Recurring Revenue (MRR)", "kpi", "cloud"),
    ExtractionPattern(r"\bremaining\s+performance\s+obligations?\b|\brpo\b", "Remaining Performance Obligations (RPO)", "kpi", "backlog"),
    ExtractionPattern(r"\btotal\s+(?:contract\s+)?backlog\b",       "Total Backlog",                    "kpi", "backlog"),
    ExtractionPattern(r"(?:(\w+(?:\s+\w+){0,2})\s+)?book(?:ings?)\b", "Bookings",                      "kpi", "backlog", qualified=True),
    ExtractionPattern(r"(?:(\w+(?:\s+\w+){0,2})\s+)?signings?\b",  "Signings",                         "kpi", "backlog", qualified=True),
    ExtractionPattern(r"\bnet\s+revenue\s+retention\b|\bnrr\b",     "Net Revenue Retention (NRR)",      "kpi", "cloud"),
    ExtractionPattern(r"\bcustomer\s+retention\b",                  "Customer Retention Rate",          "kpi", "cloud"),
    ExtractionPattern(r"\bchurn\s+rate\b",                          "Churn Rate",                       "kpi", "cloud"),
    ExtractionPattern(r"\bcloud\s+revenue\b",                       "Cloud Revenue",                    "kpi", "cloud"),
    ExtractionPattern(r"\bhybrid\s+cloud\s+revenue\b",              "Hybrid Cloud Revenue",             "kpi", "cloud"),
    ExtractionPattern(r"\b(?:software\s+)?as[\s\-]a[\s\-]service\b|\bsaas\b", "SaaS Revenue",          "kpi", "cloud"),
    ExtractionPattern(r"\bdeferred\s+revenue\b",                    "Deferred Revenue",                 "kpi", "revenue"),
    ExtractionPattern(r"\bgross\s+profit\s+margin\b|\bgross\s+margin\b", "Gross Margin",               "kpi", "margin"),
    ExtractionPattern(r"\boperating\s+(?:profit\s+)?margin\b",      "Operating Margin",                 "kpi", "margin"),
    ExtractionPattern(r"\bnet\s+(?:profit\s+)?margin\b",            "Net Margin",                       "kpi", "margin"),
    ExtractionPattern(r"\bheadcount\b|\bfull[\s\-]time\s+equivalent\b|\bfte\b", "Headcount / FTEs",    "kpi", "other"),
    ExtractionPattern(r"\butilization\s+rate?\b",                   "Utilization Rate",                 "kpi", "other"),
    ExtractionPattern(r"\bwin\s+rate\b",                            "Win Rate",                         "kpi", "other"),
    ExtractionPattern(r"\bcagr\b",                                  "CAGR",                             "kpi", "growth"),
    ExtractionPattern(r"\bai\s+(?:book(?:ings?|ed)|revenue|signings?)\b", "AI Bookings/Revenue",        "kpi", "cloud"),
    ExtractionPattern(r"\bgenerative\s+ai\s+(?:revenue|bookings?)\b", "Generative AI Revenue",          "kpi", "cloud"),
]


@dataclass
class ExtractedItem:
    name: str
    measure_type: str
    category: str
    contexts: List[str] = field(default_factory=list)
    company: str = ""
    period: str = ""
    source_file: str = ""
    operating_reclassified: bool = False


@dataclass
class ExtractionResult:
    items: List[ExtractedItem]
    has_safe_harbor: bool
    has_fwd_looking: bool
    char_count: int


def _snippet(text: str, match_start: int, match_end: int, window: int = 80) -> str:
    """Extract a context snippet around a regex match."""
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)
    snip = re.sub(r"\s+", " ", text[start:end]).strip()
    if start > 0:
        snip = "..." + snip
    if end < len(text):
        snip += "..."
    return snip


def _title_case(s: str) -> str:
    return re.sub(r"\b\w", lambda m: m.group().upper(), s)


def _norm(name: str) -> str:
    """Normalize a measure name for deduplication."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def extract_measures(
    text: str,
    company: str = "",
    period: str = "",
    source_file: str = "",
    max_contexts: int = 3,
) -> ExtractionResult:
    """
    Run the full extraction pipeline on a text string.
    Returns structured results with context snippets and safe-harbor detection.
    """
    found: List[ExtractedItem] = []
    seen: set = set()

    for ep in EXTRACTION_PATTERNS:
        compiled = re.compile(ep.pattern, re.IGNORECASE)

        if ep.qualified:
            # Qualified patterns (bookings/signings): capture the leading word(s)
            qualified_hits: dict = {}
            for m in compiled.finditer(text):
                qualifier = _title_case(m.group(1).strip()) if m.group(1) else None
                qual_words = qualifier.lower().split() if qualifier else []
                qual_is_stop = bool(qual_words) and all(w in _STOPS for w in qual_words)
                q_name = f"{qualifier} {ep.name}" if qualifier and not qual_is_stop else ep.name
                if q_name not in qualified_hits:
                    qualified_hits[q_name] = []
                if len(qualified_hits[q_name]) < max_contexts:
                    qualified_hits[q_name].append(_snippet(text, m.start(), m.end()))
            for q_name, contexts in qualified_hits.items():
                if _norm(q_name) not in seen:
                    seen.add(_norm(q_name))
                    found.append(ExtractedItem(
                        name=q_name,
                        measure_type=ep.measure_type,
                        category=ep.category,
                        contexts=contexts,
                        company=company,
                        period=period,
                        source_file=source_file,
                    ))
        else:
            contexts = []
            for m in compiled.finditer(text):
                if len(contexts) >= max_contexts:
                    break
                contexts.append(_snippet(text, m.start(), m.end()))
            if contexts and _norm(ep.name) not in seen:
                seen.add(_norm(ep.name))
                found.append(ExtractedItem(
                    name=ep.name,
                    measure_type=ep.measure_type,
                    category=ep.category,
                    contexts=contexts,
                    company=company,
                    period=period,
                    source_file=source_file,
                    operating_reclassified=False,
                ))

    # Dynamic operating X sweep for custom management metrics not in standard GAAP list
    op_re = re.compile(r"\boperating\s+([\w]+(?:\s+[\w]+)?)\b", re.IGNORECASE)
    for m in op_re.finditer(text):
        noun = _title_case(m.group(1).strip())
        candidate = f"Operating {noun}"
        first_word = noun.split()[0].lower()
        if _norm(candidate) not in seen and first_word not in _GAAP_NOUNS:
            seen.add(_norm(candidate))
            found.append(ExtractedItem(
                name=candidate,
                measure_type="nongaap",
                category="profitability",
                contexts=[_snippet(text, m.start(), m.end())],
                company=company,
                period=period,
                source_file=source_file,
                operating_reclassified=True,
            ))

    # Safe-harbor detection
    lower = text.lower()
    has_safe_harbor = "safe harbor" in lower or "forward-looking statement" in lower
    has_fwd_looking = any(term in lower for term in FWD_LOOKING_TERMS)

    return ExtractionResult(
        items=found,
        has_safe_harbor=has_safe_harbor,
        has_fwd_looking=has_fwd_looking,
        char_count=len(text),
    )
