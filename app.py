import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import google.generativeai as genai
import time
import json
import traceback
import requests
from datetime import datetime, date
from pathlib import Path

### ─────────────────────────────────────────────────────────────────────────────
### PAGE CONFIG — must be the very first Streamlit call
### ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Munger/Buffett Equity Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

### ─────────────────────────────────────────────────────────────────────────────
### CONSTANTS
### ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "research_ledger.db"
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are an elite financial intelligence analyst and investment research assistant
who operates at the intersection of three intellectual frameworks:

  1. Warren Buffett and Charlie Munger's chief equity analyst —
     masters of business quality, moat identification, and capital discipline.

  2. Leopold Aschenbrenner's macro-technological forecasting intelligence —
     the ability to see where exponential technological curves are heading,
     identify the infrastructure bottlenecks that will determine who wins,
     map the geopolitical and industrial dependencies that most investors
     ignore until it is too late, and pinpoint which companies are
     quietly positioning themselves at the chokepoints of the future.

  3. An independent fundamentals-first research analyst — whose only
     authority is the numbers, the data, and the structural logic of
     the business itself. Not critics. Not consensus. Not narrative.

Your job is to synthesize all three frameworks into a single coherent
picture of what a business truly is, where it truly stands, and where
it is truly heading — piece by piece, signal by signal, until the
full puzzle is assembled and the investment conclusion is unavoidable
from the evidence alone.

=============================================================
THE ASCHENBRENNER INTELLIGENCE FRAMEWORK
=============================================================
Leopold Aschenbrenner is defined by a specific set of intellectual
characteristics that you must embody in every analysis:

  EXPONENTIAL CURVE RECOGNITION
    He sees technological progress not as linear improvement but as
    compounding curves that reach inflection points most people miss
    until the change is already irreversible. You must ask of every
    company: Where is this business on the exponential curve of its
    industry — and is it BEFORE or AFTER the inflection point?

  BOTTLENECK IDENTIFICATION
    Aschenbrenner's most powerful analytical tool is identifying
    the specific bottlenecks that will constrain an entire industry
    or technology wave. The company that SOLVES the bottleneck —
    or IS the bottleneck's solution — captures disproportionate value.
    For every company analyzed, you must:
    → Identify the 1 to 3 most critical bottlenecks in its industry
    → State whether this company is positioned as a BOTTLENECK SOLVER,
      a BOTTLENECK SUFFERER, or BOTTLENECK NEUTRAL
    → Name which other companies are the most realistic solutions

  INFRASTRUCTURE & SUPPLY CHAIN INTELLIGENCE
    He understands that the real value in a technology wave rarely
    goes to the most visible application layer — it goes to the
    picks-and-shovels infrastructure layer that everything else
    depends on. Always ask: Is this company at the APPLICATION layer
    or the INFRASTRUCTURE layer?

  GEOPOLITICAL & INDUSTRIAL DEPENDENCY MAPPING
    Factor in national security implications, supply chain sovereignty,
    and government industrial policy as investment variables.

  SECOND AND THIRD ORDER CONSEQUENCE THINKING
    Do not stop at the obvious conclusion. Ask:
    "If X happens, what does that mean for Y — and what does
    THAT mean for Z?" Show the downstream implications.

  PUZZLE ASSEMBLY
    Assemble individual signals into a coherent picture that points
    to an inevitable conclusion most investors are not yet seeing.

=============================================================
CORE IDENTITY & COMMUNICATION STYLE
=============================================================
- You think like Buffett and Munger: long-term, business-quality first,
  price second, moat always.
- You think like Aschenbrenner: exponential curves, bottleneck positions,
  infrastructure layers, geopolitical dependencies, puzzle assembly.
- You are precise, confident, and evidence-driven.
- You do not use filler sentences, vague language, or generic financial clichés.
- Every claim must be traceable to a specific data point, insider signal,
  news item, structural logic, or technological dependency in the analysis.
- Tone: Institutional. Direct. Forward-looking. Specific to THIS company.
- You do not defer to analyst consensus, media narratives, or public opinion.
- Think in decades. Write for today. Decide with evidence.

=============================================================
SCORING MANDATE — CRITICAL INSTRUCTION
=============================================================
At the END of EVERY section below, you MUST include a score in
this EXACT format on its own line:

SECTION SCORE: X/10

Where X is an integer from 1 to 10.
1 = critically weak / deeply concerning
5 = average / mixed signals
10 = exceptional / best-in-class

Score each section based ONLY on the evidence presented in that
section. No rounding up for optimism. No rounding down for
pessimism. The number must be earned by the data.

At the very top of the entire report, before Section 0,
output this line using the average of all section scores:

OVERALL COMPANY RATING: X/10 — [ONE SENTENCE VERDICT]

Where the one sentence verdict names the single most important
reason for that rating based on the assembled evidence.

=============================================================
TREND DETECTION MANDATE
=============================================================
Before writing any section, answer these internal diagnostic questions:

  1. Is revenue growing, shrinking, or plateauing — and is the RATE of
     change itself accelerating or decelerating?
  2. Is net income expanding or contracting — and is margin improving
     or compressing relative to revenue growth?
  3. Are there NEW streams of revenue appearing in recent quarters?
  4. Is there a visible INFLECTION POINT in the data?
  5. Is free cash flow moving in the same direction as reported earnings?
  6. Where does this company sit on the exponential curve of its industry?
  7. What is the single most important BOTTLENECK in this company's industry?
  8. Taken together, do ALL directional signals point the same way?

Weave the answers throughout every relevant section.

=============================================================
ANALYSIS FRAMEWORK — EXECUTE ALL SECTIONS IN ORDER
=============================================================

SECTION 0: EXECUTIVE SUMMARY
Write this LAST but display it FIRST.
After completing the full analysis, return here and write this
summary with the benefit of every insight already assembled.

Structure exactly as follows:

  THE BUSINESS IN ONE PARAGRAPH
    Describe what this company fundamentally is — not what it says
    it is, but what the numbers and operational reality confirm.
    Be precise. Be complete. Be direct.

  WHERE IT STANDS TODAY — FUNDAMENTAL SNAPSHOT
    In 3 to 5 sentences, state the current fundamental reality
    using actual numbers. Do not speak in generalities.

  THE NEAR-FUTURE TRAJECTORY (12 TO 24 MONTHS)
    State the most likely near-future trajectory as a conclusion,
    not a possibility. Name the 2 to 3 most important drivers.

  THE SINGLE MOST IMPORTANT INSIGHT
    The one insight that, if a serious investor understood it clearly,
    would most change how they think about this company.
    State it in 2 to 4 sentences. Make it count.

  OVERALL FUNDAMENTAL RATING — scored dimensions:
    FINANCIAL HEALTH:        STRONG | ADEQUATE | WEAK — Score: X/10
    GROWTH TRAJECTORY:       ACCELERATING | STABLE | DECELERATING — Score: X/10
    STRATEGIC POSITION:      DOMINANT | COMPETITIVE | VULNERABLE — Score: X/10
    NEAR-TERM OUTLOOK:       POSITIVE | NEUTRAL | CAUTIOUS | NEGATIVE — Score: X/10
    One sentence of justification for each. Numbers only.

SECTION SCORE: [average of all section scores] /10

---

SECTION 1: COMPANY OVERVIEW & BUSINESS MODEL
- Describe what the company actually does in the real world.
- Identify primary revenue drivers and ALL current revenue streams.
  Label each: ESTABLISHED | GROWING | EMERGING | DECLINING
- Sector and industry context: tailwind or headwind?
- Aschenbrenner layer: APPLICATION layer or INFRASTRUCTURE layer?
- Munger question: Understandable in 10 minutes? If yes, explain it.

SECTION SCORE: X/10

---

SECTION 2: PARTNERSHIPS, ALLIANCES & ECOSYSTEM SYNERGY
List EVERY known current and recent partnership.
For EACH partnership:
  PARTNER NAME & RELATIONSHIP TYPE
  WHAT THE PARTNERSHIP DOES (operational terms)
  SYNERGY ASSESSMENT: CORE SYNERGY | COMPLEMENTARY | PERIPHERAL | UNCLEAR
  FINANCIAL MATERIALITY: REVENUE-ACTIVE | PRE-REVENUE STRATEGIC | COST-REDUCTION | UNKNOWN
  ASCHENBRENNER SECOND-ORDER ANALYSIS: What does it unlock in 2 to 4 years?

MISSING PARTNERSHIPS — STRATEGIC GAPS
  What partnerships does this company NOT YET HAVE that it logically
  SHOULD have? Name specific companies. Explain why.

SECTION SCORE: X/10

---

SECTION 3: THE ECONOMIC MOAT
- Classify moat type:
    BRAND STRENGTH | SWITCHING COSTS | NETWORK EFFECTS |
    COST ADVANTAGES | INTANGIBLE ASSETS | EFFICIENT SCALE
- Rate: WIDE | NARROW | NONE IDENTIFIED
- Connect to quarterly revenue and net income trends.
- Aschenbrenner: Is the moat being WIDENED by bottleneck position
  or at risk of obsolescence from a new wave?

SECTION SCORE: X/10

---

SECTION 4: THE BUFFETT/MUNGER CHECKLIST
  CAPITAL ALLOCATION STRATEGY — evaluated and scored
  PRICING POWER — evaluated and scored
  STABLE EARNING POWER — evaluated and scored
  CORPORATE STRUCTURE VIABILITY & EFFICIENCY — evaluated and scored
  MANAGEMENT QUALITY (INTEGRITY + COMPETENCE) — evaluated and scored
  Are they building the RIGHT partnerships for their stated strategy?

SECTION SCORE: X/10

---

SECTION 5: CONSECUTIVE QUARTERLY TREND ANALYSIS
  REVENUE TREND (4 Consecutive Quarters — Oldest to Newest)
    Exact figures. Sequential change. Classification.
    ACCELERATING | DECELERATING | STABLE | VOLATILE

  NET INCOME TREND (4 Consecutive Quarters — Oldest to Newest)
    Exact figures. Classification. Margin flags.

  YEAR-OVER-YEAR NET INCOME TREND
    Exact YoY figures. Percentage change.
    NET INCOME EXPANSION or NET INCOME CONTRACTION.

  MARGIN TRAJECTORY
    TIER 1 SIGNAL if widening margin + revenue growth.
    WARNING SIGNAL if contracting margin + revenue growth.

  INFLECTION POINT IDENTIFICATION
    Quarter named. Shift quantified. STRUCTURAL or ONE-TIME.

SECTION SCORE: X/10

---

SECTION 6: BOTTLENECK & FUTURE VISION ANALYSIS
  INDUSTRY BOTTLENECK MAP: 1 to 3 critical bottlenecks named precisely.
  THIS COMPANY'S POSITION: BOTTLENECK SOLVER | SUFFERER | NEUTRAL
  REALISTIC SOLUTION COMPANIES: Named. Current and non-partners.
  EXPONENTIAL CURVE POSITION:
    PRE-INFLECTION | AT INFLECTION | POST-INFLECTION SCALING | PLATEAU | DECLINING
  GEOPOLITICAL & INDUSTRIAL POLICY LAYER: quantified where possible.
  SECOND & THIRD ORDER CONSEQUENCE CHAIN: If X → then Y → which means Z.
  PUZZLE ASSEMBLY: Every piece named. Single coherent conclusion stated.

SECTION SCORE: X/10

---

SECTION 7: VALUATION & FUNDAMENTAL SNAPSHOT
- P/E, P/B, Debt/Equity, ROE assessment.
- UNDERVALUED | FAIRLY VALUED | OVERVALUED
- Buffett margin-of-safety lens.
- Analyst target vs. current price and what the gap implies.
- Red flags flagged explicitly.

SECTION SCORE: X/10

---

SECTION 8: CATALYST & FILING INTELLIGENCE
- All recent news reviewed.
- Each catalyst classified: REVENUE-GENERATING | RISK-REDUCING | SPECULATIVE | NEUTRAL
- Connected to revenue/margin impact specifically.
- Munger filter: Does this strengthen the moat or distract from weak fundamentals?
- Aschenbrenner bottleneck and curve filter applied.

SECTION SCORE: X/10

---

SECTION 9: INSIDER SENTIMENT ANALYSIS
- Classify: PLANNED SELLING | CONVICTION SELLING | CONVICTION BUYING
- Skin in the game vs. public optimism assessment.
- HIGH-CONVICTION ALIGNMENT or CREDIBILITY RISK — stated directly.
- Connected to quarterly trend and bottleneck position.

SECTION SCORE: X/10

---

SECTION 10: POTENTIAL FUTURE & HIDDEN ADVANTAGES
- Hidden, emerging, underappreciated advantages named explicitly.
- Emerging revenue streams not yet in headline numbers.
- Companies this company SHOULD be working with — named.
- Munger: "What is the market systematically ignoring right now?"

SECTION SCORE: X/10

---

SECTION 11: REAL-WORLD POSSIBILITIES & OPERATIONAL ADVANTAGES
Full synthesis: quarterly trends + catalysts + moat + partnerships
+ bottleneck position + inflection points + insider sentiment.
Connect financial trend to operational story directly:
"Revenue is accelerating because X created Y which produces Z advantage."

SECTION SCORE: X/10

---

SECTION 12: RISK LAYER
- 2 to 3 specific risks from actual data.
- Each classified: EXISTENTIAL | MATERIAL | MANAGEABLE
- Early warning signal named for each risk.
- Aschenbrenner bottleneck displacement risk assessed.
- Downtrend data named directly — not softened.

SECTION SCORE: X/10

---

SECTION 13: FUNDAMENTALS-ONLY SUMMARY & FINAL VERDICT
Numbers and fundamentals only. No opinion. No narrative. No spin.

  WHAT THE NUMBERS ACTUALLY SHOW: IMPROVING | DETERIORATING | MIXED | STABLE
  PARTNERSHIP SYNERGY SCORECARD: STRONG | DEVELOPING | CONCENTRATED RISK | WEAK
  NEW REVENUE STREAMS & INFLECTION POINT SUMMARY: named, dated, classified.
  BOTTLENECK VERDICT: one sentence position + 12 to 36 month implication.
  DIRECTIONAL VERDICT: UP | DOWN | SIDEWAYS
    Strongest bullish signal. Most important risk signal.
  BUFFETT/MUNGER QUALITY GATE: YES | PARTIALLY | NO — what it passes, what it fails.
  ASCHENBRENNER VISION GATE: YES | CONDITIONALLY | NO — most important evidence.
  THE 90-DAY WATCH SIGNAL:
    Metric named. Threshold stated.
    Above threshold means: ___. Below threshold means: ___.

SECTION SCORE: X/10

=============================================================
ABSOLUTE RULES
=============================================================
- Never fabricate data. If missing, say so and state what it would change.
- Never give generic advice. Every insight anchored to THIS company.
- Never skip a section. State what is missing and its impact.
- Always use exact quarterly figures when referencing numbers.
- Always connect Buffett/Munger principles to THIS company's data.
- Always apply Aschenbrenner analysis to THIS company's specific position.
- Do not let critic narratives override what the fundamental data shows.
- If fundamentals show improvement — say so without hedging.
- If fundamentals show deterioration — say so without softening.
- Partnerships must be assessed for REAL synergy — not announced synergy.
- The Executive Summary is written LAST but displayed FIRST.
- EVERY section MUST end with SECTION SCORE: X/10
- The OVERALL COMPANY RATING must appear at the very top of the report.
- Format with clear section headers. Use plain text formatting only.
  Do NOT use HTML tags inside the AI response.
- Think in decades. Write for today. Decide with evidence.
"""


### ─────────────────────────────────────────────────────────────────────────────
### MOBILE-FIRST CSS
### ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>

/* ── Base & Typography ── */
html, body, [class*="css"] {
    font-size: 16px !important;
    -webkit-text-size-adjust: 100%;
}

.stApp {
    background-color: ##0d1117;
    color: ##c9d1d9;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: ##161b22;
    border-right: 1px solid ##30363d;
    min-width: 280px !important;
}

/* ── Metric Cards ── */
.metric-card {
    background: ##161b22;
    border: 1px solid ##30363d;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 6px 0;
}
.metric-card h4 {
    color: ##58a6ff;
    margin: 0 0 4px 0;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-card p {
    color: ##e6edf3;
    margin: 0;
    font-size: 1.15rem;
    font-weight: 600;
}

/* ── Section Headers ── */
.section-header {
    border-bottom: 1px solid ##30363d;
    padding-bottom: 8px;
    margin: 20px 0 14px 0;
    color: ##58a6ff;
    font-size: 1rem;
    font-weight: 600;
}

/* ── Overall Rating Badge ── */
.rating-badge {
    background: linear-gradient(135deg, ##1f6feb, ##388bfd);
    border-radius: 12px;
    padding: 18px 20px;
    margin: 10px 0 20px 0;
    text-align: center;
}
.rating-badge .rating-number {
    font-size: 3rem;
    font-weight: 800;
    color: ##ffffff;
    line-height: 1;
}
.rating-badge .rating-label {
    font-size: 0.85rem;
    color: ##cae8ff;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.rating-badge .rating-verdict {
    font-size: 0.9rem;
    color: ##e6edf3;
    margin-top: 8px;
    font-style: italic;
}

/* ── Section Score Pills ── */
.score-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    margin: 6px 0 14px 0;
}
.score-high   { background: ##1a4731; color: ##3fb950; border: 1px solid ##3fb950; }
.score-medium { background: ##3d2f00; color: ##d29922; border: 1px solid ##d29922; }
.score-low    { background: ##3d0f0f; color: ##f85149; border: 1px solid ##f85149; }

/* ── AI Report Container ── */
.ai-report {
    background: ##161b22;
    border: 1px solid ##30363d;
    border-left: 3px solid ##58a6ff;
    border-radius: 10px;
    padding: 20px;
    line-height: 1.75;
    font-size: 0.95rem;
    color: ##c9d1d9;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

/* ── Section Nav Button ── */
.nav-section-btn {
    background: ##21262d;
    border: 1px solid ##30363d;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 0;
    color: ##58a6ff;
    font-size: 0.88rem;
    cursor: pointer;
    width: 100%;
    text-align: left;
    transition: background 0.2s;
}
.nav-section-btn:hover {
    background: ##30363d;
}

/* ── Jump Anchor Targets ── */
.section-anchor {
    display: block;
    position: relative;
    top: -70px;
    visibility: hidden;
}

/* ── Run Button ── */
.stButton > button {
    background: linear-gradient(135deg, ##238636, ##2ea043);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
    padding: 14px;
    font-size: 1rem;
    min-height: 48px;
}
.stButton > button:hover { opacity: 0.85; }

/* ── Mobile Responsive ── */
@media (max-width: 768px) {

    html, body, [class*="css"] {
        font-size: 15px !important;
    }

    /* Stack columns on mobile */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    .metric-card p    { font-size: 1.1rem; }
    .metric-card h4   { font-size: 0.72rem; }

    .ai-report {
        padding: 14px;
        font-size: 0.93rem;
        line-height: 1.7;
    }

    .rating-badge .rating-number { font-size: 2.4rem; }

    /* Larger tap targets */
    .stButton > button {
        min-height: 52px;
        font-size: 1rem;
    }

    /* Sidebar collapses by default (already set in config) */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
    }

    /* Tabs scroll horizontally on small screens */
    [data-testid="stHorizontalBlock"] {
        overflow-x: auto;
    }

    .section-header { font-size: 0.95rem; }
}

/* ── Streamlit overrides ── */
.stTextInput input {
    font-size: 1rem !important;
    min-height: 44px;
}
.stSelectbox select, div[data-baseweb="select"] {
    font-size: 0.95rem !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
}
.stExpander {
    border: 1px solid ##30363d !important;
    border-radius: 8px !important;
}

</style>
"""


### ─────────────────────────────────────────────────────────────────────────────
### DATABASE LAYER
### ─────────────────────────────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    sql_create = (
        "CREATE TABLE IF NOT EXISTS research_ledger ("
        "id             INTEGER PRIMARY KEY AUTOINCREMENT, "
        "ticker         TEXT    NOT NULL, "
        "company_name   TEXT, "
        "analysis_date  TEXT    NOT NULL, "
        "current_price  REAL, "
        "total_debt     REAL, "
        "net_income     REAL, "
        "debt_to_equity REAL, "
        "insider_data   TEXT, "
        "ai_report      TEXT, "
        "sector         TEXT, "
        "industry       TEXT, "
        "market_cap     REAL, "
        "created_at     TEXT DEFAULT (datetime('now')), "
        "UNIQUE(ticker, analysis_date)"
        ")"
    )
    sql_index = (
        "CREATE INDEX IF NOT EXISTS idx_ticker_date "
        "ON research_ledger(ticker, analysis_date)"
    )
    with get_db_connection() as conn:
        conn.execute(sql_create)
        conn.execute(sql_index)
        conn.commit()


def upsert_record(record: dict):
    sql = (
        "INSERT INTO research_ledger "
        "(ticker, company_name, analysis_date, current_price, total_debt, "
        "net_income, debt_to_equity, insider_data, ai_report, "
        "sector, industry, market_cap) "
        "VALUES (:ticker, :company_name, :analysis_date, :current_price, "
        ":total_debt, :net_income, :debt_to_equity, :insider_data, "
        ":ai_report, :sector, :industry, :market_cap) "
        "ON CONFLICT(ticker, analysis_date) DO UPDATE SET "
        "current_price  = excluded.current_price, "
        "total_debt     = excluded.total_debt, "
        "net_income     = excluded.net_income, "
        "debt_to_equity = excluded.debt_to_equity, "
        "insider_data   = excluded.insider_data, "
        "ai_report      = excluded.ai_report, "
        "sector         = excluded.sector, "
        "industry       = excluded.industry, "
        "market_cap     = excluded.market_cap"
    )
    with get_db_connection() as conn:
        conn.execute(sql, record)
        conn.commit()


def load_all_records():
    sql = (
        "SELECT ticker, company_name, analysis_date, current_price, "
        "total_debt, net_income, debt_to_equity, sector, industry, "
        "market_cap, insider_data, ai_report "
        "FROM research_ledger "
        "ORDER BY analysis_date DESC, ticker ASC"
    )
    with get_db_connection() as conn:
        rows = conn.execute(sql).fetchall()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


def load_single_record(ticker: str, analysis_date: str):
    sql = (
        "SELECT * FROM research_ledger "
        "WHERE ticker = ? AND analysis_date = ? "
        "LIMIT 1"
    )
    with get_db_connection() as conn:
        row = conn.execute(sql, (ticker, analysis_date)).fetchone()
    return dict(row) if row else None


def get_distinct_tickers():
    sql = (
        "SELECT DISTINCT ticker, company_name "
        "FROM research_ledger "
        "ORDER BY ticker ASC"
    )
    with get_db_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def get_dates_for_ticker(ticker: str):
    sql = (
        "SELECT DISTINCT analysis_date "
        "FROM research_ledger "
        "WHERE ticker = ? "
        "ORDER BY analysis_date DESC"
    )
    with get_db_connection() as conn:
        rows = conn.execute(sql, (ticker,)).fetchall()
    return [r["analysis_date"] for r in rows]


### ─────────────────────────────────────────────────────────────────────────────
### SCORE PARSER — extract overall and section scores from AI text
### ─────────────────────────────────────────────────────────────────────────────
import re

SECTION_LABELS = [
    "Executive Summary",
    "Company Overview & Business Model",
    "Partnerships, Alliances & Ecosystem Synergy",
    "The Economic Moat",
    "The Buffett/Munger Checklist",
    "Consecutive Quarterly Trend Analysis",
    "Bottleneck & Future Vision Analysis",
    "Valuation & Fundamental Snapshot",
    "Catalyst & Filing Intelligence",
    "Insider Sentiment Analysis",
    "Potential Future & Hidden Advantages",
    "Real-World Possibilities & Operational Advantages",
    "Risk Layer",
    "Fundamentals-Only Summary & Final Verdict",
]

def parse_overall_rating(ai_text: str):
    """Extract OVERALL COMPANY RATING: X/10 from AI report."""
    match = re.search(
        r"OVERALL COMPANY RATING[:\s]+(\d{1,2})/10",
        ai_text, re.IGNORECASE
    )
    if match:
        return int(match.group(1))
    return None


def parse_overall_verdict(ai_text: str):
    """Extract the verdict sentence after the overall rating."""
    match = re.search(
        r"OVERALL COMPANY RATING[:\s]+\d{1,2}/10\s*[—\-–]+\s*(.+)",
        ai_text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    return ""


def parse_section_scores(ai_text: str):
    """
    Extract all SECTION SCORE: X/10 occurrences in order.
    Returns list of ints.
    """
    matches = re.findall(
        r"SECTION SCORE[:\s]+(\d{1,2})/10",
        ai_text, re.IGNORECASE
    )
    return [int(m) for m in matches]


def score_color_class(score: int) -> str:
    if score >= 7:
        return "score-high"
    elif score >= 4:
        return "score-medium"
    return "score-low"


def rating_color(score: int) -> str:
    """Return hex color for overall rating badge gradient."""
    if score >= 8:
        return "##238636, ##2ea043"   ## green
    elif score >= 6:
        return "##1f6feb, ##388bfd"   ## blue
    elif score >= 4:
        return "##9e6a03, ##d29922"   ## yellow
    return "##8b1a1a, ##f85149"       ## red


### ─────────────────────────────────────────────────────────────────────────────
### YFINANCE DATA FETCHER
### ─────────────────────────────────────────────────────────────────────────────
def safe_get(info: dict, *keys, default=None):
    for key in keys:
        val = info.get(key)
        if val is not None:
            return val
    return default


def fetch_ticker_data(ticker: str):
    try:
        tk   = yf.Ticker(ticker)
        info = tk.info

        if not info or len(info) < 5:
            return None

        current_price = safe_get(
            info,
            "currentPrice", "regularMarketPrice",
            "navPrice", "previousClose",
            default=None,
        )
        total_debt    = safe_get(info, "totalDebt",    default=0.0)
        net_income    = safe_get(info, "netIncomeToCommon", "netIncome", default=None)
        total_equity  = safe_get(info, "stockholdersEquity", "bookValue", default=None)
        market_cap    = safe_get(info, "marketCap",    default=None)
        sector        = safe_get(info, "sector",       default="N/A")
        industry      = safe_get(info, "industry",     default="N/A")
        company_name  = safe_get(info, "longName", "shortName", default=ticker)
        business_summary = safe_get(info, "longBusinessSummary", default="No summary available.")

        debt_to_equity = None
        if total_equity and total_equity != 0 and total_debt is not None:
            debt_to_equity = total_debt / total_equity

        ### ── Insider transactions ──
        insider_summary = {"buys": 0, "sells": 0, "transactions": []}
        try:
            insider_df = tk.insider_transactions
            if insider_df is not None and not insider_df.empty:
                for _, row in insider_df.head(20).iterrows():
                    text     = str(row.get("Text", "")).lower()
                    shares   = row.get("Shares", 0) or 0
                    value    = row.get("Value", 0) or 0
                    name     = row.get("Insider", "Unknown")
                    txn_date = str(row.get("Start Date", ""))
                    if "sale" in text or "sell" in text or "sold" in text:
                        insider_summary["sells"] += 1
                        insider_summary["transactions"].append(
                            f"SELL | {name} | {shares:,} shares | "
                            f"${value:,.0f} | {txn_date}"
                        )
                    elif "purchase" in text or "buy" in text or "bought" in text:
                        insider_summary["buys"] += 1
                        insider_summary["transactions"].append(
                            f"BUY  | {name} | {shares:,} shares | "
                            f"${value:,.0f} | {txn_date}"
                        )
        except Exception:
            pass

        ### ── Quarterly financials ──
        quarterly_revenue    = {}
        quarterly_net_income = {}
        yoy_trend            = "Insufficient data for YoY calculation."

        try:
            qf = tk.quarterly_financials
            if qf is not None and not qf.empty:
                cols       = list(qf.columns[:4])
                cols_chrono = list(reversed(cols))

                rev_labels = ["Total Revenue", "Revenue"]
                ni_labels  = ["Net Income", "Net Income Common Stockholders"]

                import math
                for label in rev_labels:
                    if label in qf.index:
                        for col in cols_chrono:
                            val   = qf.loc[label, col]
                            month = col.month
                            q_num = (month - 1) // 3 + 1
                            qstr  = f"{col.year}-Q{q_num}"
                            quarterly_revenue[qstr] = (
                                int(val)
                                if isinstance(val, (int, float)) and not math.isnan(val)
                                else 0
                            )
                        break

                for label in ni_labels:
                    if label in qf.index:
                        for col in cols_chrono:
                            val   = qf.loc[label, col]
                            month = col.month
                            q_num = (month - 1) // 3 + 1
                            qstr  = f"{col.year}-Q{q_num}"
                            quarterly_net_income[qstr] = (
                                int(val)
                                if isinstance(val, (int, float)) and not math.isnan(val)
                                else 0
                            )
                        break
        except Exception:
            pass

        ### ── YoY Net Income ──
        try:
            annual = tk.financials
            if annual is not None and not annual.empty and len(annual.columns) >= 2:
                for label in ["Net Income", "Net Income Common Stockholders"]:
                    if label in annual.index:
                        curr_ni  = annual.loc[label, annual.columns[0]]
                        prior_ni = annual.loc[label, annual.columns[1]]
                        if prior_ni and prior_ni != 0:
                            pct       = ((curr_ni - prior_ni) / abs(prior_ni)) * 100
                            direction = "EXPANSION" if pct > 0 else "CONTRACTION"
                            yoy_trend = (
                                f"{direction}: Net Income changed {pct:+.1f}% YoY "
                                f"(${curr_ni:,.0f} vs ${prior_ni:,.0f})"
                            )
                        break
        except Exception:
            pass

        ### ── Recent news ──
        recent_news = []
        try:
            import datetime as dt
            news_items = tk.news or []
            for item in news_items[:10]:
                headline  = item.get("title", "")
                summary   = item.get("summary", "") or item.get("description", "")
                publisher = item.get("publisher", "")
                pub_time  = item.get("providerPublishTime", 0)
                pub_date  = (
                    dt.datetime.utcfromtimestamp(pub_time).strftime("%Y-%m-%d")
                    if pub_time else "Unknown"
                )
                if headline:
                    recent_news.append({
                        "date":      pub_date,
                        "headline":  headline,
                        "summary":   summary[:300] if summary else "",
                        "publisher": publisher,
                    })
        except Exception:
            pass

        return {
            "ticker":                ticker,
            "company_name":          company_name,
            "current_price":         current_price,
            "total_debt":            total_debt,
            "net_income":            net_income,
            "debt_to_equity":        debt_to_equity,
            "market_cap":            market_cap,
            "sector":                sector,
            "industry":              industry,
            "business_summary":      business_summary,
            "insider_summary":       insider_summary,
            "quarterly_revenue":     quarterly_revenue,
            "quarterly_net_income":  quarterly_net_income,
            "yoy_net_income_trend":  yoy_trend,
            "recent_news":           recent_news,
        }

    except Exception as exc:
        print(f"[WARN] {ticker}: {exc}")
        return None


### ─────────────────────────────────────────────────────────────────────────────
### GEMINI AI ENGINE
### ─────────────────────────────────────────────────────────────────────────────
def run_gemini_analysis(data: dict, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        insider  = data.get("insider_summary", {})
        txn_lines = (
            "\n".join(insider.get("transactions", []))
            or "No recent transactions found."
        )

        ### ── Quarterly revenue block ──
        q_rev = data.get("quarterly_revenue", {})
        if q_rev:
            rev_lines = "\n".join(
                f"  {q}: ${v:>15,.0f}" for q, v in q_rev.items()
            )
        else:
            rev_lines = "  Quarterly revenue data unavailable."

        ### ── Quarterly net income block ──
        q_ni = data.get("quarterly_net_income", {})
        if q_ni:
            ni_lines = "\n".join(
                f"  {q}: ${v:>15,.0f}" for q, v in q_ni.items()
            )
        else:
            ni_lines = "  Quarterly net income data unavailable."

        ### ── News block ──
        news_items = data.get("recent_news", [])
        if news_items:
            news_lines = "\n".join(
                f"  [{i+1}] {n['date']} | {n['headline']}"
                + (f"\n       {n['summary']}" if n.get("summary") else "")
                for i, n in enumerate(news_items)
            )
        else:
            news_lines = "  No recent news available."

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== COMPANY: {data['company_name']} ({data['ticker']}) ===\n\n"
            f"SECTOR: {data.get('sector', 'N/A')}\n"
            f"INDUSTRY: {data.get('industry', 'N/A')}\n\n"
            f"--- FINANCIAL METRICS ---\n"
            f"Current Price    : ${data.get('current_price', 'N/A')}\n"
            f"Market Cap       : ${(data.get('market_cap') or 0) / 1e9:.2f}B\n"
            f"Net Income (TTM) : ${(data.get('net_income') or 0) / 1e6:.1f}M\n"
            f"Total Debt       : ${(data.get('total_debt') or 0) / 1e6:.1f}M\n"
            f"Debt-to-Equity   : {data.get('debt_to_equity', 'N/A')}\n\n"
            f"--- CONSECUTIVE QUARTERLY REVENUE (Oldest to Newest) ---\n"
            f"{rev_lines}\n\n"
            f"--- CONSECUTIVE QUARTERLY NET INCOME (Oldest to Newest) ---\n"
            f"{ni_lines}\n\n"
            f"--- YEAR-OVER-YEAR NET INCOME TREND ---\n"
            f"  {data.get('yoy_net_income_trend', 'N/A')}\n\n"
            f"--- RECENT NEWS CATALYSTS (up to 10) ---\n"
            f"{news_lines}\n\n"
            f"--- INSIDER TRANSACTIONS (last 20) ---\n"
            f"Total Buys  : {insider.get('buys', 0)}\n"
            f"Total Sells : {insider.get('sells', 0)}\n"
            f"Transactions:\n{txn_lines}\n\n"
            f"--- BUSINESS SUMMARY ---\n"
            f"{data.get('business_summary', 'No summary available.')}\n\n"
            f"REMINDER: Begin your response with the OVERALL COMPANY RATING: X/10 "
            f"on the very first line, followed by a dash and a one-sentence verdict. "
            f"End every section with SECTION SCORE: X/10 on its own line."
        )

        response = model.generate_content(prompt)
        return response.text

    except Exception as exc:
        return (
            f"**AI Analysis Error:** {exc}\n\n"
            f"{traceback.format_exc()}"
        )


### ─────────────────────────────────────────────────────────────────────────────
### HELPER FORMATTERS
### ─────────────────────────────────────────────────────────────────────────────
def fmt_millions(val):
    if val is None:
        return "N/A"
    try:
        return f"${float(val) / 1e6:,.1f}M"
    except Exception:
        return "N/A"


def fmt_billions(val):
    if val is None:
        return "N/A"
    try:
        return f"${float(val) / 1e9:,.2f}B"
    except Exception:
        return "N/A"


def fmt_price(val):
    if val is None:
        return "N/A"
    try:
        return f"${float(val):,.2f}"
    except Exception:
        return "N/A"


def fmt_ratio(val):
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.2f}x"
    except Exception:
        return "N/A"


### ─────────────────────────────────────────────────────────────────────────────
### REPORT RENDERER — parses AI text into navigable sections
### ─────────────────────────────────────────────────────────────────────────────
def render_report_with_navigation(ai_report: str, container_key: str = "main"):
    """
    Splits AI report into sections using SECTION headers.
    Renders a sticky quick-nav bar and anchored sections with score pills.
    Mobile-friendly: each section in its own expander on small screens.
    """

    ### ── Parse overall rating ──
    overall_score   = parse_overall_rating(ai_report)
    overall_verdict = parse_overall_verdict(ai_report)
    section_scores  = parse_section_scores(ai_report)

    ### ── Overall Rating Badge ──
    if overall_score is not None:
        grad = rating_color(overall_score)
        st.markdown(
            f"<div class='rating-badge' style='"
            f"background: linear-gradient(135deg, {grad});'>"
            f"<div class='rating-number'>{overall_score}/10</div>"
            f"<div class='rating-label'>Overall Company Rating</div>"
            f"<div class='rating-verdict'>{overall_verdict}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Overall rating not parsed — see full report below.")

    ### ── Section splitter ──
    section_pattern = re.compile(
        r"(SECTION\s+\d+[:\s]|"
        r"(?:^|\n)##+\s*(?:SECTION|Section)\s+\d+)",
        re.IGNORECASE | re.MULTILINE,
    )

    ### Split by numbered SECTION headers in the AI text
    raw_sections = re.split(
        r"\n(?=(?:SECTION\s+\d+|##+\s*SECTION\s+\d+))",
        ai_report,
        flags=re.IGNORECASE,
    )

    ### Filter to only blocks that actually start with SECTION
    parsed_sections = []
    intro_block     = ""
    for block in raw_sections:
        stripped = block.strip()
        if re.match(r"(?:##+\s*)?SECTION\s+\d+", stripped, re.IGNORECASE):
            ### Extract section number and title
            title_match = re.match(
                r"(?:##+\s*)?SECTION\s+(\d+)[:\s—\-]*(.*?)(?:\n|$)",
                stripped, re.IGNORECASE
            )
            if title_match:
                sec_num   = int(title_match.group(1))
                sec_title = title_match.group(2).strip() or f"Section {sec_num}"
                parsed_sections.append({
                    "num":     sec_num,
                    "title":   sec_title,
                    "content": stripped,
                    "anchor":  f"section-{sec_num}-{container_key}",
                })
            else:
                parsed_sections.append({
                    "num":     len(parsed_sections),
                    "title":   f"Section {len(parsed_sections)}",
                    "content": stripped,
                    "anchor":  f"section-x-{container_key}",
                })
        else:
            intro_block += stripped + "\n"

    ### ── Quick Navigation Bar ──
    if parsed_sections:
        st.markdown(
            "<div class='section-header'>🧭 Quick Section Navigator</div>",
            unsafe_allow_html=True,
        )
        st.caption("Tap a section to jump directly to it ↓")

        ### Render nav as columns of buttons (2 per row on mobile)
        nav_items = [
            f"§{s['num']} — {s['title'][:35]}"
            for s in parsed_sections
        ]

        ### Pair into rows of 2
        for i in range(0, len(nav_items), 2):
            nav_cols = st.columns(2)
            for j, col in enumerate(nav_cols):
                idx = i + j
                if idx < len(nav_items):
                    with col:
                        ### Use checkbox hack for smooth page jump
                        sec = parsed_sections[idx]
                        score_idx = idx
                        score_val = (
                            section_scores[score_idx]
                            if score_idx < len(section_scores) else None
                        )
                        label = nav_items[idx]
                        if score_val is not None:
                            label += f"  [{score_val}/10]"
                        st.markdown(
                            f"<a href='##{sec['anchor']}' "
                            f"style='text-decoration:none;'>"
                            f"<div class='nav-section-btn'>{label}</div>"
                            f"</a>",
                            unsafe_allow_html=True,
                        )
        st.markdown("---")

    ### ── Render intro block if any ──
    if intro_block.strip():
        st.markdown(intro_block.strip())
        st.markdown("---")

    ### ── Render each section ──
    for idx, sec in enumerate(parsed_sections):
        ### Anchor target
        st.markdown(
            f"<a name='{sec['anchor']}'></a>",
            unsafe_allow_html=True,
        )

        ### Section score pill
        score_val = (
            section_scores[idx]
            if idx < len(section_scores) else None
        )

        score_html = ""
        if score_val is not None:
            css_class = score_color_class(score_val)
            score_html = (
                f"<span class='score-pill {css_class}'>"
                f"Score: {score_val}/10"
                f"</span>"
            )

        ### Section header
        st.markdown(
            f"<div class='section-header'>"
            f"Section {sec['num']}: {sec['title']}"
            f"&nbsp;&nbsp;{score_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

        ### Section content — strip the first line (header) to avoid duplication
        content_lines = sec["content"].split("\n")
        body_lines    = content_lines[1:] if len(content_lines) > 1 else content_lines
        body_text     = "\n".join(body_lines).strip()

        ### Render inside expander for compactness on mobile
        with st.expander(f"View Section {sec['num']} Content", expanded=(idx == 0)):
            st.markdown(body_text)

        st.markdown("")  ### small spacer

    ### ── Fallback: if no sections parsed, render raw ──
    if not parsed_sections and not intro_block.strip():
        st.markdown(
            f"<div class='ai-report'>{ai_report}</div>",
            unsafe_allow_html=True,
        )


### ─────────────────────────────────────────────────────────────────────────────
### STREAMLIT UI — MAIN
### ─────────────────────────────────────────────────────────────────────────────
def main():
    init_db()

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    ### ─────────────────────────────────────
    ### SIDEBAR
    ### ─────────────────────────────────────
    with st.sidebar:
        st.markdown(
            "<h2 style='color:##58a6ff; margin-bottom:4px;'>📈 Equity Terminal</h2>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        st.markdown("## 🔑 Gemini API Key")
        api_key = st.text_input(
            "Google AI Studio Key",
            type="password",
            placeholder="AIza...",
            help="Get a free key at https://aistudio.google.com/app/apikey",
        )

        st.markdown("---")

        st.markdown("## 🔎 Ticker Lookup")
        ticker_input = st.text_input(
            "Enter a ticker symbol",
            placeholder="e.g. AAPL, TSLA, BRK-B",
            max_chars=10,
            help="Any valid stock ticker. Use dash for dot tickers e.g. BRK-B",
        ).strip().upper()

        st.markdown("---")

        run_analysis = st.button(
            "🚀 Run Full Analysis",
            use_container_width=True,
            disabled=not ticker_input,
        )

        st.markdown("---")
        st.markdown(
            "<small style='color:##8b949e;'>"
            "Data: yfinance<br>"
            "AI: Google Gemini<br>"
            "Storage: Local SQLite<br><br>"
            "💡 Tip: On iPhone, tap the ☰ icon "
            "top-left to open this menu."
            "</small>",
            unsafe_allow_html=True,
        )

    ### ─────────────────────────────────────
    ### HEADER
    ### ─────────────────────────────────────
    st.markdown(
        "<h1 style='color:##58a6ff; margin-bottom:0; font-size:1.6rem;'>"
        "📊 Ai's Megamind Tool r<br>"
        "<span style='font-size:1rem; color:##8b949e;'>"
        "Buffet x Munger x Leopold Analysis Terminal</span>"
        "</h1>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    ### ─────────────────────────────────────
    ### TABS
    ### ─────────────────────────────────────
    tab_analysis, tab_dashboard, tab_detail = st.tabs(
        ["🔬 Analysis", "📋 Ledger", "🔍 Detail"]
    )

    ### ═══════════════════════════════════════
    ### TAB 1 — LIVE ANALYSIS
    ### ═══════════════════════════════════════
    with tab_analysis:

        if not run_analysis:
            st.markdown(
                "<div style='background:##161b22; border:1px dashed ##30363d; "
                "border-radius:10px; padding:32px 20px; text-align:center; "
                "color:##8b949e;'>"
                "<h3 style='color:##58a6ff;'>Ready for Analysis</h3>"
                "<p style='font-size:1rem; line-height:1.8;'>"
                "① Open sidebar (☰ top-left on iPhone)<br>"
                "② Enter a ticker symbol<br>"
                "③ Paste your Gemini API key<br>"
                "④ Tap <strong>🚀 Run Full Analysis</strong>"
                "</p>"
                "<p style='font-size:0.85rem; margin-top:16px;'>"
                "Results auto-saved to your local research ledger."
                "</p>"
                "</div>",
                unsafe_allow_html=True,
            )

        else:
            if not api_key:
                st.error(
                    "⚠️ No Gemini API key. "
                    "Paste your key in the sidebar. "
                    "Get one free at https://aistudio.google.com/app/apikey"
                )
                st.stop()

            if not ticker_input:
                st.error("⚠️ Please enter a ticker symbol in the sidebar.")
                st.stop()

            ### ── Fetch + Analyse ──
            with st.status(
                f"Analysing **{ticker_input}**...",
                expanded=True,
            ) as status:
                st.write("📡 Fetching data from yfinance...")
                data = fetch_ticker_data(ticker_input)

                if data is None:
                    status.update(label="Data fetch failed.", state="error")
                    st.error(
                        f"Could not retrieve data for **{ticker_input}**. "
                        "Check the ticker and try again."
                    )
                    st.stop()

                st.write(
                    f"✅ Data retrieved — "
                    f"**{data.get('company_name', ticker_input)}**"
                )
                st.write("🤖 Running Gemini AI analysis (may take 30–60s)...")
                ai_report = run_gemini_analysis(data, api_key)
                st.write("✅ AI analysis complete.")

                st.write("💾 Saving to research ledger...")
                insider = data.get("insider_summary", {})
                record  = {
                    "ticker":         ticker_input,
                    "company_name":   data.get("company_name", ticker_input),
                    "analysis_date":  date.today().isoformat(),
                    "current_price":  data.get("current_price"),
                    "total_debt":     data.get("total_debt"),
                    "net_income":     data.get("net_income"),
                    "debt_to_equity": data.get("debt_to_equity"),
                    "insider_data":   json.dumps(insider),
                    "ai_report":      ai_report,
                    "sector":         data.get("sector"),
                    "industry":       data.get("industry"),
                    "market_cap":     data.get("market_cap"),
                }
                upsert_record(record)
                st.write("✅ Saved to research_ledger.db")
                status.update(
                    label=f"✅ Analysis complete — {ticker_input}",
                    state="complete",
                )

            ### ── Company Header ──
            st.markdown("---")
            company_name = data.get("company_name", ticker_input)
            st.markdown(
                f"<h2 style='color:##e6edf3; font-size:1.4rem; margin-bottom:2px;'>"
                f"{company_name} "
                f"<span style='color:##58a6ff;'>({ticker_input})</span>"
                f"</h2>"
                f"<p style='color:##8b949e; margin-top:0; font-size:0.9rem;'>"
                f"{data.get('sector','N/A')} · {data.get('industry','N/A')}"
                f"</p>",
                unsafe_allow_html=True,
            )

            ### ── Financial Snapshot (horizontal scroll on mobile) ──
            st.markdown(
                "<div class='section-header'>📊 Financial Snapshot</div>",
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Price",      fmt_price(data.get("current_price")))
            m2.metric("Market Cap", fmt_billions(data.get("market_cap")))
            m3.metric("Net Income", fmt_millions(data.get("net_income")))

            m4, m5, m6 = st.columns(3)
            m4.metric("Total Debt", fmt_millions(data.get("total_debt")))
            m5.metric("D/E Ratio",  fmt_ratio(data.get("debt_to_equity")))
            m6.metric("Date",       date.today().isoformat())

            ### ── Insider Activity ──
            st.markdown(
                "<div class='section-header'>👤 Insider Activity</div>",
                unsafe_allow_html=True,
            )
            ins_a, ins_b = st.columns(2)
            insider = data.get("insider_summary", {})
            ins_a.metric("🟢 Buys",  insider.get("buys", 0))
            ins_b.metric("🔴 Sells", insider.get("sells", 0))

            transactions = insider.get("transactions", [])
            if transactions:
                with st.expander("📋 View Insider Transactions"):
                    for txn in transactions:
                        color = "##3fb950" if txn.startswith("BUY") else "##f85149"
                        st.markdown(
                            f"<p style='color:{color}; font-family:monospace; "
                            f"font-size:0.82rem; margin:3px 0;'>{txn}</p>",
                            unsafe_allow_html=True,
                        )
            else:
                st.caption("No insider transaction details available.")

            ### ── AI Report with Navigation ──
            st.markdown("---")
            st.markdown(
                "<div class='section-header'>"
                "🤖 Gemini AI — Full Institutional Analysis"
                "</div>",
                unsafe_allow_html=True,
            )

            if ai_report and not ai_report.startswith("**AI Analysis Error"):
                render_report_with_navigation(ai_report, container_key="analysis")
            else:
                st.error("The AI analysis encountered an error.")
                st.markdown(ai_report)

    ### ═══════════════════════════════════════
    ### TAB 2 — RESEARCH LEDGER DASHBOARD
    ### ═══════════════════════════════════════
    with tab_dashboard:
        st.markdown(
            "<div class='section-header'>📋 Historical Research Ledger</div>",
            unsafe_allow_html=True,
        )

        df = load_all_records()

        if df.empty:
            st.info(
                "No records yet. Enter a ticker in the sidebar "
                "and tap **🚀 Run Full Analysis** to get started."
            )
        else:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Companies",   df["ticker"].nunique())
            k2.metric("Records",     len(df))
            k3.metric("Avg Income",  fmt_millions(df["net_income"].mean()))
            k4.metric("Avg D/E",     fmt_ratio(df["debt_to_equity"].mean()))

            st.markdown("---")

            ### ── Parse and display overall scores from stored reports ──
            scores_col = []
            for _, row in df.iterrows():
                report_text = row.get("ai_report", "") or ""
                score = parse_overall_rating(report_text)
                scores_col.append(f"{score}/10" if score else "N/A")
            df["Overall Score"] = scores_col

            display_df = df[[
                "ticker", "company_name", "analysis_date",
                "current_price", "net_income", "total_debt",
                "debt_to_equity", "market_cap", "sector", "Overall Score",
            ]].copy()

            display_df.columns = [
                "Ticker", "Company", "Date",
                "Price ($)", "Net Income", "Total Debt",
                "D/E Ratio", "Market Cap", "Sector", "AI Score",
            ]

            display_df["Price ($)"]  = display_df["Price ($)"].apply(
                lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A"
            )
            display_df["Net Income"] = display_df["Net Income"].apply(fmt_millions)
            display_df["Total Debt"] = display_df["Total Debt"].apply(fmt_millions)
            display_df["Market Cap"] = display_df["Market Cap"].apply(fmt_billions)
            display_df["D/E Ratio"]  = display_df["D/E Ratio"].apply(fmt_ratio)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

            csv = df.drop(
                columns=["ai_report", "insider_data"],
                errors="ignore",
            ).to_csv(index=False)

          
            st.download_button(
                label="⬇️ Download Ledger as CSV",
                data=csv,
                file_name=f"research_ledger_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    ### ═══════════════════════════════════════
    ### TAB 3 — DETAIL VIEW
    ### ═══════════════════════════════════════
    with tab_detail:
        st.markdown(
            "<div class='section-header'>🔍 Deep Dive — Company Detail</div>",
            unsafe_allow_html=True,
        )

        ticker_records = get_distinct_tickers()

        if not ticker_records:
            st.info(
                "No records yet. Run an analysis first."
            )
        else:
            ticker_options = [
                f"{r['ticker']}  —  {r['company_name'] or ''}"
                for r in ticker_records
            ]

            selected_option = st.selectbox(
                "Select a company to review:",
                options=ticker_options,
                index=0,
            )

            selected_ticker = selected_option.split("—")[0].strip()

            dates = get_dates_for_ticker(selected_ticker)
            selected_date = st.selectbox(
                "Analysis date:",
                options=dates,
                index=0,
            )

            record = load_single_record(selected_ticker, selected_date)

            if record is None:
                st.warning("Could not load record.")
            else:
                st.markdown("---")

                ### ── Company Header ──
                st.markdown(
                    f"<h2 style='color:##e6edf3; font-size:1.4rem; margin-bottom:2px;'>"
                    f"{record.get('company_name', selected_ticker)} "
                    f"<span style='color:##58a6ff;'>({selected_ticker})</span>"
                    f"</h2>"
                    f"<p style='color:##8b949e; margin-top:0; font-size:0.9rem;'>"
                    f"{record.get('sector','N/A')} · {record.get('industry','N/A')}"
                    f"</p>",
                    unsafe_allow_html=True,
                )

                ### ── Financial Snapshot ──
                st.markdown(
                    "<div class='section-header'>📊 Financial Snapshot</div>",
                    unsafe_allow_html=True,
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Price",      fmt_price(record.get("current_price")))
                m2.metric("Market Cap", fmt_billions(record.get("market_cap")))
                m3.metric("Net Income", fmt_millions(record.get("net_income")))

                m4, m5, m6 = st.columns(3)
                m4.metric("Total Debt", fmt_millions(record.get("total_debt")))
                m5.metric("D/E Ratio",  fmt_ratio(record.get("debt_to_equity")))
                m6.metric("Date",       record.get("analysis_date", "N/A"))

                ### ── Overall AI Score from stored report ──
                ai_report = record.get("ai_report", "") or ""
                overall_score   = parse_overall_rating(ai_report)
                overall_verdict = parse_overall_verdict(ai_report)

                if overall_score is not None:
                    st.markdown("---")
                    grad = rating_color(overall_score)
                    st.markdown(
                        f"<div class='rating-badge' style='"
                        f"background: linear-gradient(135deg, {grad});'>"
                        f"<div class='rating-number'>{overall_score}/10</div>"
                        f"<div class='rating-label'>Overall Company Rating</div>"
                        f"<div class='rating-verdict'>{overall_verdict}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                ### ── Insider Activity ──
                st.markdown(
                    "<div class='section-header'>👤 Insider Activity</div>",
                    unsafe_allow_html=True,
                )

                insider_raw = record.get("insider_data", "{}") or "{}"
                try:
                    insider = json.loads(insider_raw)
                except Exception:
                    insider = {}

                buys  = insider.get("buys", 0)
                sells = insider.get("sells", 0)

                ins_a, ins_b = st.columns(2)
                ins_a.metric("🟢 Buys",  buys)
                ins_b.metric("🔴 Sells", sells)

                transactions = insider.get("transactions", [])
                if transactions:
                    with st.expander("📋 View Insider Transactions"):
                        for txn in transactions:
                            color = (
                                "##3fb950" if txn.startswith("BUY")
                                else "##f85149"
                            )
                            st.markdown(
                                f"<p style='color:{color}; "
                                f"font-family:monospace; "
                                f"font-size:0.82rem; "
                                f"margin:3px 0;'>{txn}</p>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.caption("No insider transaction details available.")

                ### ── AI Report with Navigation ──
                st.markdown("---")
                st.markdown(
                    "<div class='section-header'>"
                    "🤖 Gemini AI — Full Institutional Analysis"
                    "</div>",
                    unsafe_allow_html=True,
                )

                if ai_report and not ai_report.startswith("**AI Analysis Error"):
                    render_report_with_navigation(
                        ai_report,
                        container_key=f"detail-{selected_ticker}-{selected_date}",
                    )
                elif ai_report.startswith("**AI Analysis Error"):
                    st.error(
                        "The AI analysis encountered an error for this record."
                    )
                    st.markdown(ai_report)
                else:
                    st.info("No AI report found for this record.")


### ─────────────────────────────────────────────────────────────────────────────
### ENTRY POINT
### ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()


