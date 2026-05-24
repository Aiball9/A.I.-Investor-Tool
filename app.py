import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import google.generativeai as genai
import time
import json
import traceback
from datetime import datetime, date
from pathlib import Path

## ─────────────────────────────────────────────────────────────────────────────
## PAGE CONFIG — must be the very first Streamlit call
## ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Munger/Buffett Equity Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

## ─────────────────────────────────────────────────────────────────────────────
## CONSTANTS
## ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "research_ledger.db"
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = SYSTEM_PROMPT = SYSTEM_PROMPT = SYSTEM_PROMPT = """
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

  ✦ EXPONENTIAL CURVE RECOGNITION
    He sees technological progress not as linear improvement but as
    compounding curves that reach inflection points most people miss
    until the change is already irreversible. You must ask of every
    company: Where is this business on the exponential curve of its
    industry — and is it BEFORE or AFTER the inflection point?

  ✦ BOTTLENECK IDENTIFICATION
    Aschenbrenner's most powerful analytical tool is identifying
    the specific bottlenecks that will constrain an entire industry
    or technology wave. The company that SOLVES the bottleneck —
    or IS the bottleneck's solution — captures disproportionate value.
    For every company analyzed, you must:
    → Identify the 1 to 3 most critical bottlenecks in its industry
    → State whether this company is positioned as a BOTTLENECK SOLVER,
      a BOTTLENECK SUFFERER, or BOTTLENECK NEUTRAL
    → Name which other companies (whether partners, competitors, or
      unrelated players) are the most realistic solutions to each bottleneck

  ✦ INFRASTRUCTURE & SUPPLY CHAIN INTELLIGENCE
    He understands that the real value in a technology wave rarely
    goes to the most visible application layer — it goes to the
    picks-and-shovels infrastructure layer that everything else
    depends on. You must always ask: Is this company at the
    APPLICATION layer or the INFRASTRUCTURE layer — and which
    layer is currently capturing more economic value in this wave?

  ✦ GEOPOLITICAL & INDUSTRIAL DEPENDENCY MAPPING
    Aschenbrenner factors in national security implications,
    supply chain sovereignty, and government industrial policy
    as investment variables — not background noise.
    For relevant companies: identify any geopolitical dependencies,
    domestic vs. foreign supply chain exposure, and whether
    government industrial policy (IRA, CHIPS Act, defense spending,
    energy policy) creates a structural tailwind or risk.

  ✦ SECOND AND THIRD ORDER CONSEQUENCE THINKING
    He does not stop at the obvious conclusion. He asks:
    "If X happens, what does that mean for Y — and what does
    THAT mean for Z?" You must apply this chain of consequence
    thinking to every major catalyst, partnership, or trend identified.
    Show the downstream implications, not just the first-order effect.

  ✦ PUZZLE ASSEMBLY — PIECE BY PIECE TO INEVITABLE CONCLUSION
    Aschenbrenner assembles individual signals — technology curves,
    bottleneck positions, capital flows, geopolitical moves,
    talent concentration, infrastructure buildouts — into a
    coherent picture that points to an inevitable conclusion
    most investors are not yet seeing.
    Your analysis must do the same: name each piece of the puzzle
    explicitly, then assemble them into the conclusion they point to.

  ✦ REALISTIC SOLUTION MAPPING
    For every bottleneck or challenge identified, name the most
    REALISTIC solutions — not the most hyped ones. Identify which
    companies, technologies, or partnerships are most likely to
    deliver those solutions based on current positioning, capital,
    and technical capability. Include companies that are not yet
    in partnership with the analyzed company but SHOULD BE
    or LIKELY WILL BE given the trajectory.

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
  The fundamentals, the structural logic, and the numbers are your authority.
- If the numbers show a business improving, say so clearly and directly —
  regardless of what critics or headlines say.
- If the numbers show a business deteriorating, say so with equal clarity —
  regardless of how optimistic management sounds in press releases.
- Think in decades. Write for today. Decide with evidence.
  See around corners. Name what you see.

=============================================================
TREND DETECTION MANDATE
=============================================================
Before writing any section, answer these internal diagnostic questions:

  1. Is revenue growing, shrinking, or plateauing — and is the RATE of
     change itself accelerating or decelerating?
  2. Is net income expanding or contracting — and is margin improving
     or compressing relative to revenue growth?
  3. Are there NEW streams of revenue appearing in recent quarters
     that did not exist or were immaterial 12 to 24 months ago?
  4. Is there a visible INFLECTION POINT in the data — a quarter where
     trajectory materially changed direction — and what caused it?
  5. Is free cash flow moving in the same direction as reported earnings,
     or is there a divergence signaling accounting noise vs. real cash generation?
  6. Where does this company sit on the exponential curve of its industry —
     and is it BEFORE or AFTER the curve's critical inflection point?
  7. What is the single most important BOTTLENECK in this company's industry —
     and is this company positioned to solve it, suffer from it, or neutral?
  8. Taken together, do ALL directional signals point the same way —
     and if not, which signal is the most reliable leading indicator?

Weave the answers throughout every relevant section.
They are the lens through which every section must be read.

=============================================================
ANALYSIS FRAMEWORK — EXECUTE ALL SECTIONS IN ORDER
=============================================================

=============================================================
SECTION 0: EXECUTIVE SUMMARY
=============================================================
CRITICAL INSTRUCTION FOR THIS SECTION:
This section is written LAST but displayed FIRST.
After completing the full analysis across all sections below,
return here and write this summary with the benefit of every
insight, number, signal, and conclusion already assembled.

This is not an introduction. It is a verdict delivered upfront —
earned by the full analysis that follows it.

It must be direct, thoughtful, and grounded in fundamentals only.
No filler. No hedging. No generic language.
A serious investor should be able to read this section alone
and understand exactly what kind of business this is,
where it stands today, and where it is most likely heading —
then read the full analysis to see every piece of evidence
that supports that summary.

Structure this section exactly as follows:

  ✦ THE BUSINESS IN ONE PARAGRAPH
    Describe what this company fundamentally is — not what it says
    it is, but what the numbers and operational reality confirm it to be.
    What does it sell, who buys it, how does it make money,
    and what is the single most important thing to understand
    about its business model right now?
    Write this as if explaining to an exceptional investor
    who has never heard of this company but will make a decision
    based on your words. Be precise. Be complete. Be direct.

  ✦ WHERE IT STANDS TODAY — FUNDAMENTAL SNAPSHOT
    In 3 to 5 sentences, state the current fundamental reality:
    → Is the business growing or contracting — and at what rate?
    → Is profitability expanding or compressing?
    → Is the balance sheet a strength or a concern?
    → Are partnerships and catalysts adding measurable value
      or are they still pre-revenue strategic bets?
    → What is the single most important number that defines
      where this business stands right now?
    Use actual numbers. Do not speak in generalities.

  ✦ THE NEAR-FUTURE TRAJECTORY (12 TO 24 MONTHS)
    Based on the full analysis — quarterly trends, inflection points,
    new revenue streams, partnership synergies, bottleneck position,
    exponential curve placement, catalyst pipeline, and insider signals —
    state the most likely near-future trajectory of this business.
    → Is the business entering an acceleration phase,
      a consolidation phase, or a deterioration phase?
    → What are the 2 to 3 most important drivers of that trajectory?
    → What would have to go wrong to change it — and how likely is that?
    Be direct. State the trajectory as a conclusion, not a possibility.

  ✦ THE SINGLE MOST IMPORTANT INSIGHT
    After assembling every piece of this analysis —
    the one insight about this business that matters most.
    The thing that, if a serious investor understood it clearly,
    would most change how they think about this company.
    It could be a hidden strength, an overlooked risk, a bottleneck
    position, a partnership with second-order consequences,
    an inflection point in the data, or a moat that is wider
    or narrower than the market currently believes.
    State it in 2 to 4 sentences. Make it count.

  ✦ OVERALL FUNDAMENTAL RATING
    Rate this business across four dimensions using only
    the data and fundamentals as evidence:

    FINANCIAL HEALTH:        STRONG | ADEQUATE | WEAK
    GROWTH TRAJECTORY:       ACCELERATING | STABLE | DECELERATING | DECLINING
    STRATEGIC POSITION:      DOMINANT | COMPETITIVE | VULNERABLE | UNCLEAR
    NEAR-TERM OUTLOOK:       POSITIVE | NEUTRAL | CAUTIOUS | NEGATIVE

    One sentence of justification for each rating.
    Numbers only. No opinion. No narrative inflation.

--- SECTION 1: COMPANY OVERVIEW & BUSINESS MODEL ---
- Briefly describe what the company actually does in the real world.
- Identify its primary revenue drivers and customer base.
- Identify ALL current revenue streams — including any new or emerging ones
  that have appeared or grown meaningfully in the last 12 to 24 months.
  Label each stream as: ESTABLISHED | GROWING | EMERGING | DECLINING
- Note the sector and industry context and whether it represents a tailwind
  or headwind for this company right now.
- Apply the Aschenbrenner layer: Is this company at the APPLICATION layer
  or the INFRASTRUCTURE layer of its industry wave — and which layer is
  currently capturing more economic value?
- Ask the Munger question: "Is this a business I could understand completely
  in 10 minutes?" If yes, explain it. If no, flag the complexity.

--- SECTION 2: PARTNERSHIPS, ALLIANCES & ECOSYSTEM SYNERGY ---
This section must be comprehensive and specific.
List EVERY known current and recent partnership, alliance, joint venture,
or strategic relationship this company has — drawn from the news,
filings, and business summary provided.

For EACH partnership identified, provide:

  ✦ PARTNER NAME & RELATIONSHIP TYPE
    TECHNOLOGY PARTNER | DISTRIBUTION PARTNER | GOVERNMENT CONTRACT |
    SUPPLY CHAIN PARTNER | RESEARCH & DEVELOPMENT ALLIANCE |
    LICENSING AGREEMENT | JOINT VENTURE | STRATEGIC INVESTMENT |
    CUSTOMER RELATIONSHIP (enterprise) | OTHER

  ✦ WHAT THE PARTNERSHIP DOES
    In plain operational terms — what does each party contribute
    and what does each party receive?

  ✦ SYNERGY ASSESSMENT
    How does this partnership fit into the company's overall
    strategic architecture? Does it:
    → Strengthen the moat?
    → Open a new revenue stream?
    → Solve a bottleneck?
    → Reduce a key operational risk?
    → Expand geographic or market reach?
    → Accelerate a technology development timeline?
    Classify: CORE SYNERGY | COMPLEMENTARY | PERIPHERAL | UNCLEAR

  ✦ FINANCIAL MATERIALITY
    REVENUE-ACTIVE | PRE-REVENUE STRATEGIC | COST-REDUCTION | UNKNOWN

  ✦ ASCHENBRENNER SECOND-ORDER ANALYSIS
    If this partnership succeeds and scales — what does it unlock
    for the company 2 to 4 years from now that is not yet
    priced into the stock?

  ✦ MISSING PARTNERSHIPS — STRATEGIC GAPS
    What partnerships does this company NOT YET HAVE that it logically
    SHOULD have or WILL LIKELY need within the next 12 to 36 months?
    Name specific companies. Explain why each makes structural sense.

--- SECTION 3: THE ECONOMIC MOAT ---
- Identify and explain this company's durable competitive advantage.
- Classify:
    → BRAND STRENGTH
    → SWITCHING COSTS
    → NETWORK EFFECTS
    → COST ADVANTAGES
    → INTANGIBLE ASSETS
    → EFFICIENT SCALE
- Rate: WIDE | NARROW | NONE IDENTIFIED
- Connect to quarterly revenue and net income trends.
- Apply Aschenbrenner: Is the moat being WIDENED by the company's
  bottleneck position — or at risk of obsolescence from a new wave?

--- SECTION 4: THE BUFFETT/MUNGER CHECKLIST ---

  ✦ CAPITAL ALLOCATION STRATEGY
  ✦ PRICING POWER
  ✦ STABLE EARNING POWER
  ✦ CORPORATE STRUCTURE VIABILITY & EFFICIENCY
  ✦ MANAGEMENT QUALITY (INTEGRITY + COMPETENCE)
    Are they building the RIGHT partnerships for the company's
    stated strategic direction — or announcing partnerships for
    press release value without operational substance?

--- SECTION 5: CONSECUTIVE QUARTERLY TREND ANALYSIS ---

  ✦ REVENUE TREND (4 Consecutive Quarters — Oldest to Newest)
    Exact figures. Sequential change. Classification.
    Inflection points. Partnership contribution.

  ✦ NET INCOME TREND (4 Consecutive Quarters — Oldest to Newest)
    Exact figures. Sequential change. Classification.
    Margin compression flags. Operating leverage flags.

  ✦ YEAR-OVER-YEAR NET INCOME TREND
    Exact YoY figures. Percentage change.
    NET INCOME EXPANSION or NET INCOME CONTRACTION.
    Buffett earnings-per-dollar question answered.

  ✦ MARGIN TRAJECTORY
    TIER 1 SIGNAL if widening margin + revenue growth.
    WARNING SIGNAL if contracting margin + revenue growth.

  ✦ INFLECTION POINT IDENTIFICATION
    Quarter named. Shift quantified. Cause connected.
    STRUCTURAL or ONE-TIME classification.

--- SECTION 6: BOTTLENECK & FUTURE VISION ANALYSIS ---

  ✦ INDUSTRY BOTTLENECK MAP
    1 to 3 critical bottlenecks. Each named precisely.
    Trajectory: WORSENING | STABLE | BEING SOLVED

  ✦ THIS COMPANY'S BOTTLENECK POSITION
    BOTTLENECK SOLVER | BOTTLENECK SUFFERER | BOTTLENECK NEUTRAL
    Evidence-based classification.

  ✦ REALISTIC SOLUTION COMPANIES
    Named companies. Current partners and non-partners.
    Why each is the realistic solution.

  ✦ EXPONENTIAL CURVE POSITION
    PRE-INFLECTION | AT INFLECTION | POST-INFLECTION SCALING |
    PLATEAU | DECLINING CURVE

  ✦ GEOPOLITICAL & INDUSTRIAL POLICY LAYER
    National security implications, supply chain sovereignty,
    government policy tailwinds/headwinds. Quantified where possible.

  ✦ SECOND & THIRD ORDER CONSEQUENCE CHAIN
    If X → then Y → which means Z → companies that benefit most from Z.

  ✦ PUZZLE ASSEMBLY — THE FULL PICTURE
    Every piece named. Every connection made.
    Single coherent conclusion stated directly.

--- SECTION 7: VALUATION & FUNDAMENTAL SNAPSHOT ---
- P/E, P/B, Debt/Equity, ROE assessment.
- UNDERVALUED | FAIRLY VALUED | OVERVALUED
- Buffett margin-of-safety lens.
- Aschenbrenner pre vs. post inflection pricing gap.
- Analyst target vs. current price.
- Red flags flagged explicitly.

--- SECTION 8: CATALYST & FILING INTELLIGENCE ---
- All recent news reviewed.
- Each catalyst classified and connected to revenue/margin impact.
- Munger filter applied.
- Aschenbrenner bottleneck and curve filter applied.
- Structural inflection point catalysts flagged.

--- SECTION 9: INSIDER SENTIMENT ANALYSIS ---
- PLANNED SELLING | CONVICTION SELLING | CONVICTION BUYING
- Skin in the game vs. public optimism assessment.
- Connected to quarterly trend and bottleneck position.
- Inflection point awareness buying signal identified if present.

--- SECTION 10: POTENTIAL FUTURE & HIDDEN ADVANTAGES ---
- Hidden, emerging, underappreciated advantages.
- Emerging revenue streams not yet in headline numbers.
- Companies this company SHOULD be working with named explicitly.
- Munger: "What is the market systematically ignoring?"

--- SECTION 11: REAL-WORLD POSSIBILITIES & OPERATIONAL ADVANTAGES ---
- Full synthesis: quarterly trends + catalysts + moat + partnerships
  + bottleneck position + inflection points + insider sentiment.
- Real-world advantages named specifically.
- Financial trend connected to operational story directly.

--- SECTION 12: RISK LAYER ---
- 2 to 3 specific risks from actual data.
- Each: EXISTENTIAL | MATERIAL | MANAGEABLE
- Early warning signal named for each.
- Aschenbrenner bottleneck displacement risk assessed.
- Downtrend data named directly — not softened.

=============================================================
SECTION 13: FUNDAMENTALS-ONLY SUMMARY & FINAL VERDICT
=============================================================
Numbers and fundamentals only. No opinion. No narrative. No spin.

  ✦ WHAT THE NUMBERS ACTUALLY SHOW
    IMPROVING | DETERIORATING | MIXED | STABLE
    Key directional signals quantified.

  ✦ PARTNERSHIP SYNERGY SCORECARD
    Which partnerships are revenue-active vs. pre-revenue strategic.
    STRONG & DIVERSIFIED | DEVELOPING | CONCENTRATED RISK | WEAK

  ✦ NEW REVENUE STREAMS & INFLECTION POINT SUMMARY
    Named, dated, quantified, classified as structural or one-time.

  ✦ BOTTLENECK VERDICT
    One sentence on position. One paragraph on 12 to 36 month implication.

  ✦ DIRECTIONAL VERDICT (NUMBERS ONLY)
    UP | DOWN | SIDEWAYS
    Strongest bullish signal. Most important risk signal.
    Valuation vs. trajectory alignment stated.

  ✦ BUFFETT/MUNGER QUALITY GATE
    YES | PARTIALLY | NO
    What it passes. What it fails. Numbers only.

  ✦ ASCHENBRENNER VISION GATE
    YES | CONDITIONALLY | NO
    Strategically inevitable position assessment.
    Single most important piece of evidence stated.

  ✦ THE 90-DAY WATCH SIGNAL
    Metric named. Threshold stated. Thesis implications defined.
    Above threshold means: ___. Below threshold means: ___.

=============================================================
ABSOLUTE RULES
=============================================================
- Never fabricate data. If something is missing, say so and state
  what it would change if available.
- Never give generic advice. Every insight anchored to THIS company.
- Never skip a section. State what is missing and its impact if
  data is insufficient.
- Always use exact quarterly figures when referencing numbers.
- Always connect Buffett/Munger principles to THIS company's data.
- Always apply Aschenbrenner bottleneck and curve analysis to THIS
  company's specific industry position — applied structural logic,
  not abstract theory.
- Do not let critic narratives, analyst consensus, or media framing
  override what the fundamental data shows.
- If fundamentals show improvement — say so completely and without
  hedging to appease negative sentiment.
- If fundamentals show deterioration — say so completely and without
  softening to appease management optimism.
- Partnerships must be assessed for REAL synergy — not announced synergy.
  If a partnership has no measurable financial contribution after
  12 months, flag it as PRE-REVENUE STRATEGIC or question its substance.
- The Executive Summary is written LAST but displayed FIRST.
  It must reflect the full weight of everything discovered in the
  complete analysis — not a preview written before the work is done.
- The puzzle must be assembled. Every piece named. Every connection made.
  The conclusion must be earned by the evidence — not assigned by opinion.
- Format response with clear section headers matching the framework above.
- Think in decades. Write for today. Decide with evidence.
  See around corners. Name what you see. Assemble the puzzle.
"""



## ─────────────────────────────────────────────────────────────────────────────
## CSS — dark terminal aesthetic
## ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
.stApp {
    background-color: ##0d1117;
    color: ##c9d1d9;
}
[data-testid="stSidebar"] {
    background-color: ##161b22;
    border-right: 1px solid ##30363d;
}
.metric-card {
    background: ##161b22;
    border: 1px solid ##30363d;
    border-radius: 8px;
    padding: 16px;
    margin: 4px 0;
}
.metric-card h4 {
    color: ##58a6ff;
    margin: 0 0 4px 0;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-card p {
    color: ##e6edf3;
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}
.ai-report {
    background: ##161b22;
    border: 1px solid ##30363d;
    border-left: 3px solid ##58a6ff;
    border-radius: 8px;
    padding: 24px;
    line-height: 1.7;
}
.section-header {
    border-bottom: 1px solid ##30363d;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
    color: ##58a6ff;
    font-size: 1.1rem;
    font-weight: 600;
}
.stButton > button {
    background: linear-gradient(135deg, ##238636, ##2ea043);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    width: 100%;
    padding: 12px;
    font-size: 1rem;
}
.stButton > button:hover {
    opacity: 0.85;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


## ─────────────────────────────────────────────────────────────────────────────
## DATABASE LAYER
## ─────────────────────────────────────────────────────────────────────────────
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


## ─────────────────────────────────────────────────────────────────────────────
## YFINANCE DATA FETCHER
## ─────────────────────────────────────────────────────────────────────────────
def safe_get(info: dict, *keys, default=None):
    """Try multiple key names and return the first match found."""
    for key in keys:
        val = info.get(key)
        if val is not None:
            return val
    return default


def fetch_ticker_data(ticker: str):
    """
    Fetch all required data points for a single ticker via yfinance.
    Returns a dict on success, or None if the ticker is unusable.
    Never raises — all exceptions are caught and logged.
    """
    try:
        tk = yf.Ticker(ticker)
        info = tk.info

        if not info or len(info) < 5:
            return None

        ## ── Core financials ──
        current_price = safe_get(
            info,
            "currentPrice", "regularMarketPrice",
            "navPrice", "previousClose",
            default=None,
        )
        total_debt = safe_get(
            info,
            "totalDebt",
            default=0.0,
        )
        net_income = safe_get(
            info,
            "netIncomeToCommon", "netIncome",
            default=None,
        )
        total_equity = safe_get(
            info,
            "stockholdersEquity", "bookValue",
            default=None,
        )
        market_cap  = safe_get(info, "marketCap", default=None)
        sector      = safe_get(info, "sector", default="N/A")
        industry    = safe_get(info, "industry", default="N/A")
        company_name = safe_get(info, "longName", "shortName", default=ticker)
        business_summary = safe_get(
            info,
            "longBusinessSummary",
            default="No summary available.",
        )

        ## ── Debt-to-equity calculation ──
        if total_equity and total_equity != 0 and total_debt is not None:
            debt_to_equity = total_debt / total_equity
        else:
            debt_to_equity = None

        ## ── Insider transactions ──
        insider_summary = {"buys": 0, "sells": 0, "transactions": []}
        try:
            insider_df = tk.insider_transactions
            if insider_df is not None and not insider_df.empty:
                for _, row in insider_df.head(20).iterrows():
                    text   = str(row.get("Text", "")).lower()
                    shares = row.get("Shares", 0) or 0
                    value  = row.get("Value", 0) or 0
                    name   = row.get("Insider", "Unknown")
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

        return {
            "ticker":           ticker,
            "company_name":     company_name,
            "current_price":    current_price,
            "total_debt":       total_debt,
            "net_income":       net_income,
            "debt_to_equity":   debt_to_equity,
            "market_cap":       market_cap,
            "sector":           sector,
            "industry":         industry,
            "business_summary": business_summary,
            "insider_summary":  insider_summary,
        }

    except Exception as exc:
        print(f"[WARN] {ticker}: {exc}")
        return None


## ─────────────────────────────────────────────────────────────────────────────
## GEMINI AI ENGINE
## ─────────────────────────────────────────────────────────────────────────────
def run_gemini_analysis(data: dict, api_key: str) -> str:
    """
    Send financial data to Gemini and return the markdown report.
    Returns an error string instead of raising so the app stays alive.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        insider = data.get("insider_summary", {})
        txn_lines = (
            "\n".join(insider.get("transactions", []))
            or "No recent transactions found."
        )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== COMPANY: {data['company_name']} ({data['ticker']}) ===\n\n"
            f"SECTOR: {data.get('sector', 'N/A')}\n"
            f"INDUSTRY: {data.get('industry', 'N/A')}\n\n"
            f"--- FINANCIAL METRICS ---\n"
            f"Current Price    : ${data.get('current_price', 'N/A')}\n"
            f"Market Cap       : ${(data.get('market_cap') or 0) / 1e9:.2f}B\n"
            f"Net Income       : ${(data.get('net_income') or 0) / 1e6:.1f}M\n"
            f"Total Debt       : ${(data.get('total_debt') or 0) / 1e6:.1f}M\n"
            f"Debt-to-Equity   : {data.get('debt_to_equity', 'N/A')}\n\n"
            f"--- INSIDER TRANSACTIONS (last 20) ---\n"
            f"Total Buys  : {insider.get('buys', 0)}\n"
            f"Total Sells : {insider.get('sells', 0)}\n"
            f"Transactions:\n{txn_lines}\n\n"
            f"--- BUSINESS SUMMARY ---\n"
            f"{data.get('business_summary', 'No summary available.')}\n"
        )

        response = model.generate_content(prompt)
        return response.text

    except Exception as exc:
        return (
            f"**AI Analysis Error:** {exc}\n\n"
            f"{traceback.format_exc()}"
        )


## ─────────────────────────────────────────────────────────────────────────────
## HELPER FORMATTERS
## ─────────────────────────────────────────────────────────────────────────────
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


## ─────────────────────────────────────────────────────────────────────────────
## STREAMLIT UI
## ─────────────────────────────────────────────────────────────────────────────
def main():
    ## ── Initialise DB on every cold start ──
    init_db()

    ## ─────────────────────────────────────
    ## SIDEBAR
    ## ─────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📈 Equity Terminal")
        st.markdown("---")

        ## ── Gemini API Key ──
        st.markdown("#### 🔑 Gemini API Key")
        api_key = st.text_input(
            "Google AI Studio Key",
            type="password",
            placeholder="AIza...",
            help="Get a free key at https://aistudio.google.com/app/apikey",
        )

        st.markdown("---")

        ## ── Single ticker input ──
        st.markdown("#### 🔎 Ticker Lookup")
        ticker_input = st.text_input(
            "Enter a ticker symbol",
            placeholder="e.g. AAPL, MSFT, BRK-B",
            max_chars=10,
            help="Type any valid stock ticker. Use a dash for dot tickers e.g. BRK-B",
        ).strip().upper()

        st.markdown("---")

        ## ── Run button ──
        run_analysis = st.button(
            "🚀 Run Analysis",
            use_container_width=True,
            disabled=not ticker_input,
        )

        st.markdown("---")
        st.markdown(
            "<small style='color:##8b949e;'>"
            "Data: yfinance<br>"
            "AI: Google Gemini (free tier)<br>"
            "Storage: Local SQLite"
            "</small>",
            unsafe_allow_html=True,
        )

    ## ─────────────────────────────────────
    ## HEADER
    ## ─────────────────────────────────────
    st.markdown(
        "<h1 style='color:##58a6ff; margin-bottom:0;'>"
        "📊 Ai's Buffet/Munger/Leopold Company Analysis Tool"
        "</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:##8b949e; margin-top:4px;'>"
        "Single-ticker deep value analysis · "
        "Munger/Buffett AI engine · "
        "Local research ledger"
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    ## ─────────────────────────────────────
    ## TABS
    ## ─────────────────────────────────────
    tab_analysis, tab_dashboard, tab_detail = st.tabs(
        ["🔬 Analysis", "📋 Research Dashboard", "🔍 Detail View"]
    )

    ## ═══════════════════════════════════════
    ## TAB 1 — LIVE ANALYSIS
    ## ═══════════════════════════════════════
    with tab_analysis:

        ## ── Idle state ──
        if not run_analysis:
            st.markdown(
                "<div style='background:##161b22; border:1px dashed ##30363d; "
                "border-radius:8px; padding:40px; text-align:center; color:##8b949e;'>"
                "<h3 style='color:##58a6ff;'>Ready for Analysis</h3>"
                "<p>① Enter a ticker symbol in the sidebar<br>"
                "② Paste your Gemini API key<br>"
                "③ Click <strong>🚀 Run Analysis</strong></p>"
                "<p style='font-size:0.85rem; margin-top:16px;'>"
                "Results are automatically saved to your local research ledger."
                "</p>"
                "</div>",
                unsafe_allow_html=True,
            )

        ## ── Analysis triggered ──
        else:
            if not api_key:
                st.error(
                    "⚠️ No Gemini API key found. "
                    "Please paste your key in the sidebar. "
                    "Get one free at https://aistudio.google.com/app/apikey"
                )
                st.stop()

            if not ticker_input:
                st.error("⚠️ Please enter a ticker symbol in the sidebar.")
                st.stop()

            ## ── Step 1: Fetch data ──
            with st.status(
                f"Fetching data for **{ticker_input}**...",
                expanded=True,
            ) as status:
                st.write("📡 Connecting to yfinance...")
                data = fetch_ticker_data(ticker_input)

                if data is None:
                    status.update(label="Data fetch failed.", state="error")
                    st.error(
                        f"Could not retrieve data for **{ticker_input}**. "
                        "Please check the ticker symbol and try again."
                    )
                    st.stop()

                st.write(
                    f"✅ Retrieved data for "
                    f"**{data.get('company_name', ticker_input)}**"
                )

                ## ── Step 2: AI analysis ──
                st.write("🤖 Running Gemini AI analysis...")
                ai_report = run_gemini_analysis(data, api_key)
                st.write("✅ AI analysis complete.")

                ## ── Step 3: Save to DB ──
                st.write("💾 Saving to local research ledger...")
                insider = data.get("insider_summary", {})
                record = {
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
                    label=f"Analysis complete for {ticker_input}!",
                    state="complete",
                )

            ## ── Results display ──
            st.markdown("---")
            company_name = data.get("company_name", ticker_input)
            st.markdown(
                f"<h2 style='color:##e6edf3;'>{company_name} "
                f"<span style='color:##58a6ff;'>({ticker_input})</span></h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='color:##8b949e; margin-top:-12px;'>"
                f"{data.get('sector','N/A')} · {data.get('industry','N/A')}"
                f"</p>",
                unsafe_allow_html=True,
            )

            ## ── Two-column layout ──
            col_metrics, col_report = st.columns([1, 2])

            with col_metrics:
                st.markdown(
                    "<div class='section-header'>📊 Financial Snapshot</div>",
                    unsafe_allow_html=True,
                )

                metrics = [
                    ("Current Price", fmt_price(data.get("current_price"))),
                    ("Market Cap",    fmt_billions(data.get("market_cap"))),
                    ("Net Income",    fmt_millions(data.get("net_income"))),
                    ("Total Debt",    fmt_millions(data.get("total_debt"))),
                    ("Debt / Equity", fmt_ratio(data.get("debt_to_equity"))),
                    ("Analysis Date", date.today().isoformat()),
                ]

                for label, value in metrics:
                    st.markdown(
                        f"<div class='metric-card'>"
                        f"<h4>{label}</h4>"
                        f"<p>{value}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

                ## ── Insider activity ──
                st.markdown(
                    "<div class='section-header'>👤 Insider Activity</div>",
                    unsafe_allow_html=True,
                )

                insider = data.get("insider_summary", {})
                buys  = insider.get("buys", 0)
                sells = insider.get("sells", 0)

                ins_col1, ins_col2 = st.columns(2)
                ins_col1.metric("🟢 Buys",  buys)
                ins_col2.metric("🔴 Sells", sells)

                transactions = insider.get("transactions", [])
                if transactions:
                    with st.expander("View transaction details"):
                        for txn in transactions:
                            color = (
                                "##3fb950" if txn.startswith("BUY")
                                else "##f85149"
                            )
                            st.markdown(
                                f"<p style='color:{color}; "
                                f"font-family:monospace; "
                                f"font-size:0.8rem; "
                                f"margin:2px 0;'>{txn}</p>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.caption("No insider transaction details available.")

            with col_report:
                st.markdown(
                    "<div class='section-header'>"
                    "🤖 Gemini AI — Munger/Buffett Analysis"
                    "</div>",
                    unsafe_allow_html=True,
                )

                if ai_report and not ai_report.startswith("**AI Analysis Error"):
                    st.markdown(
                        f"<div class='ai-report'>{ai_report}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("The AI analysis encountered an error.")
                    st.markdown(ai_report)

    ## ═══════════════════════════════════════
    ## TAB 2 — RESEARCH DASHBOARD
    ## ═══════════════════════════════════════
    with tab_dashboard:
        st.markdown(
            "<div class='section-header'>Historical Research Ledger</div>",
            unsafe_allow_html=True,
        )

        df = load_all_records()

        if df.empty:
            st.info(
                "No records yet. "
                "Enter a ticker in the sidebar and click "
                "**🚀 Run Analysis** to get started."
            )
        else:
            ## ── Summary KPIs ──
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Companies Analysed", df["ticker"].nunique())
            k2.metric("Total Scan Records", len(df))
            k3.metric("Avg Net Income",     fmt_millions(df["net_income"].mean()))
            k4.metric("Avg Debt/Equity",    fmt_ratio(df["debt_to_equity"].mean()))

            st.markdown("---")

            ## ── Display table ──
            display_df = df[[
                "ticker", "company_name", "analysis_date",
                "current_price", "net_income", "total_debt",
                "debt_to_equity", "market_cap", "sector",
            ]].copy()

            display_df.columns = [
                "Ticker", "Company", "Date",
                "Price ($)", "Net Income", "Total Debt",
                "D/E Ratio", "Market Cap", "Sector",
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

            ## ── Download button ──
            csv = df.drop(
                columns=["ai_report", "insider_data"],
                errors="ignore",
            ).to_csv(index=False)

            st.download_button(
                label="⬇️ Download Ledger as CSV",
                data=csv,
                file_name=f"research_ledger_{date.today().isoformat()}.csv",
                mime="text/csv",
            )

    ## ═══════════════════════════════════════
    ## TAB 3 — DETAIL VIEW
    ## ═══════════════════════════════════════
    with tab_detail:
        st.markdown(
            "<div class='section-header'>Deep Dive — Company Detail</div>",
            unsafe_allow_html=True,
        )

        ticker_records = get_distinct_tickers()

        if not ticker_records:
            st.info("No records yet. Run an analysis first.")
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

                col_metrics, col_report = st.columns([1, 2])

                with col_metrics:
                    st.markdown(
                        "<div class='section-header'>📊 Financial Snapshot</div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"<h3 style='color:##e6edf3;'>"
                        f"{record.get('company_name', selected_ticker)}"
                        f"</h3>",
                        unsafe_allow_html=True,                    )
                    st.markdown(
                        f"<p style='color:##8b949e; margin-top:-12px;'>"
                        f"{record.get('sector','N/A')} · "
                        f"{record.get('industry','N/A')}"
                        f"</p>",
                        unsafe_allow_html=True,
                    )

                    metrics = [
                        ("Current Price", fmt_price(record.get("current_price"))),
                        ("Market Cap",    fmt_billions(record.get("market_cap"))),
                        ("Net Income",    fmt_millions(record.get("net_income"))),
                        ("Total Debt",    fmt_millions(record.get("total_debt"))),
                        ("Debt / Equity", fmt_ratio(record.get("debt_to_equity"))),
                        ("Analysis Date", record.get("analysis_date", "N/A")),
                    ]

                    for label, value in metrics:
                        st.markdown(
                            f"<div class='metric-card'>"
                            f"<h4>{label}</h4>"
                            f"<p>{value}</p>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown("---")

                    st.markdown(
                        "<div class='section-header'>👤 Insider Activity</div>",
                        unsafe_allow_html=True,
                    )

                    insider_raw = record.get("insider_data", "{}")
                    try:
                        insider = json.loads(insider_raw) if insider_raw else {}
                    except Exception:
                        insider = {}

                    buys  = insider.get("buys", 0)
                    sells = insider.get("sells", 0)

                    ins_col1, ins_col2 = st.columns(2)
                    ins_col1.metric("🟢 Buys",  buys)
                    ins_col2.metric("🔴 Sells", sells)

                    transactions = insider.get("transactions", [])
                    if transactions:
                        with st.expander("View transaction details"):
                            for txn in transactions:
                                color = (
                                    "##3fb950" if txn.startswith("BUY")
                                    else "##f85149"
                                )
                                st.markdown(
                                    f"<p style='color:{color}; "
                                    f"font-family:monospace; "
                                    f"font-size:0.8rem; "
                                    f"margin:2px 0;'>{txn}</p>",
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.caption("No insider transaction details available.")

                with col_report:
                    st.markdown(
                        "<div class='section-header'>"
                        "🤖 Gemini AI — Munger/Buffett Analysis"
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    ai_report = record.get("ai_report", "")

                    if ai_report and not ai_report.startswith("**AI Analysis Error"):
                        st.markdown(
                            f"<div class='ai-report'>{ai_report}</div>",
                            unsafe_allow_html=True,
                        )
                    elif ai_report.startswith("**AI Analysis Error"):
                        st.error(
                            "The AI analysis encountered an error for this record."
                        )
                        st.markdown(ai_report)
                    else:
                        st.info("No AI report found for this record.")


## ─────────────────────────────────────────────────────────────────────────────
## ENTRY POINT
## ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

