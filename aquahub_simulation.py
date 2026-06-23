"""
AquaHub Delivery Challenge — Project Management Simulation
MSc Project Management Programme · University of Stirling

Run with:  streamlit run aquahub_simulation.py
"""

import streamlit as st
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaHub Delivery Challenge",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

STIR_GREEN  = "#00573F"
STIR_LT     = "#4A9B6F"
STIR_PALE   = "#E8F5EE"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background:#F4F8F5; }}
  [data-testid="stSidebar"] {{ background:#00573F; }}
  [data-testid="stSidebar"] * {{ color:white !important; }}
  [data-testid="stSidebar"] .stMarkdown h3 {{ color:white !important; }}

  .stButton > button {{
      background:{STIR_GREEN} !important; color:white !important;
      border:none !important; border-radius:8px !important;
      padding:0.55rem 1.8rem !important; font-weight:600 !important;
      font-size:1rem !important;
  }}
  .stButton > button:hover {{ background:{STIR_LT} !important; }}

  .hdr {{
      background:linear-gradient(135deg,{STIR_GREEN},{STIR_LT});
      color:white; padding:22px 28px; border-radius:12px;
      margin-bottom:22px;
  }}
  .hdr h1,.hdr h2 {{ color:white; margin:0; }}
  .hdr p {{ color:rgba(255,255,255,.82); margin:6px 0 0; }}

  .card {{
      background:white; border-radius:12px;
      padding:20px 22px; margin-bottom:16px;
      border-top:5px solid {STIR_GREEN};
      box-shadow:0 2px 8px rgba(0,0,0,.09);
  }}
  .opt-hint {{
      background:{STIR_PALE}; border-left:4px solid {STIR_LT};
      border-radius:0 8px 8px 0; padding:10px 14px;
      font-size:.9rem; color:#333; margin:6px 0 14px;
  }}
  .metric-pill {{
      background:white; border-radius:8px;
      padding:7px 12px; margin:3px 0;
      border-left:4px solid {STIR_GREEN};
      font-size:.82rem;
  }}
  .score-final {{
      background:{STIR_GREEN}; color:white;
      border-radius:12px; padding:28px 20px;
      text-align:center; margin-bottom:18px;
  }}
  .breakdown-row {{
      background:white; border-radius:8px;
      padding:10px 14px; margin:4px 0;
      box-shadow:0 1px 4px rgba(0,0,0,.07);
  }}
  .decision-log-item {{
      background:white; border-radius:8px;
      padding:9px 14px; margin:3px 0;
      border-left:3px solid {STIR_GREEN};
      font-size:.87rem;
  }}
  h1,h2,h3 {{ color:{STIR_GREEN}; }}
  .round-pill {{
      background:{STIR_LT}; color:white;
      padding:3px 12px; border-radius:20px;
      font-size:.82rem; font-weight:600;
      display:inline-block; margin-bottom:8px;
  }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# GAME DATA
# ══════════════════════════════════════════════════════════════════════════════

# ── Round 1 decision tables ───────────────────────────────────────────────────

SCOPE_OPTIONS = {
    "Basic facility (core tanks only)": {
        "scope_pct": 52, "cost_spent": 10, "tech_quality": 62,
        "sustainability": 38, "risk_exposure": 14},
    "Research hub (tanks + monitoring)": {
        "scope_pct": 64, "cost_spent": 16, "tech_quality": 68,
        "sustainability": 45, "risk_exposure": 22},
    "Innovation hub (full research + industry)": {
        "scope_pct": 74, "cost_spent": 24, "tech_quality": 70,
        "sustainability": 50, "risk_exposure": 30},
    "Flagship facility (maximum ambition)": {
        "scope_pct": 84, "cost_spent": 32, "tech_quality": 68,
        "sustainability": 55, "risk_exposure": 42},
}

SCHEDULE_OPTIONS = {
    "Relaxed (+20 % time buffer)": {"schedule_pressure": 10, "rework": 0},
    "Standard schedule":           {"schedule_pressure": 22, "rework": 0},
    "Accelerated (−15 % time)":    {"schedule_pressure": 38, "rework": 6},
    "Fast-track (−25 % time)":     {"schedule_pressure": 54, "rework": 14},
}

PROCUREMENT_OPTIONS = {
    "Standard procurement":        {"risk_exposure":  4, "cost_spent":  0},
    "Early procurement":           {"risk_exposure": -4, "cost_spent":  5},
    "Pre-qualified supplier list": {"risk_exposure": -9, "cost_spent":  8, "tech_quality": 4},
}

CONTRACTOR_OPTIONS = {
    "Minimal contractor capacity": {"risk_exposure": 12, "cost_spent": -5, "tech_quality": -6},
    "Standard contractor team":    {"risk_exposure":  0, "cost_spent":  0},
    "Robust contractor capacity":  {"risk_exposure": -8, "cost_spent": 10, "tech_quality":  8},
}

SUSTAIN_OPTIONS = {
    "Basic compliance only":         {"sustainability":  0, "stakeholder_conf": -8},
    "Enhanced sustainability systems": {"sustainability": 15, "cost_spent": 8, "stakeholder_conf": 8},
    "Flagship sustainability design":  {
        "sustainability": 30, "cost_spent": 18,
        "schedule_pressure": 10, "risk_exposure": 5, "stakeholder_conf": 14},
}

STAKEHOLDER_OPTIONS = {
    "Minimal engagement":               {"stakeholder_conf": -10, "risk_exposure":  8},
    "Standard communication":           {"stakeholder_conf":   0},
    "Proactive stakeholder programme":  {"stakeholder_conf":  13, "cost_spent": 4, "risk_exposure": -5},
}


# ── Rounds 2 – 8 ─────────────────────────────────────────────────────────────

ROUNDS = [
    {
        "num": 2,
        "title": "Equipment Lead-Time Shock",
        "icon": "⚠️",
        "event": """Your specialist **water filtration and monitoring equipment** supplier has reported a **6-week lead-time delay** due to global supply chain pressures. The equipment is critical to both technical quality and sustainability performance. Without it, core facility systems cannot be completed on schedule.

Your **Procurement Manager** and **Engineering Lead** must advise. The **Finance Manager** warns that any workaround will cost more. The **Stakeholder Manager** notes that funders are watching for schedule slippage.""",
        "options": [
            {
                "key": "accept_delay",
                "label": "Accept the delay and reschedule delivery",
                "description": "Absorb the 6-week delay honestly. Adjust the internal programme and communicate with funders. Maintains quality but increases schedule pressure.",
                "impact": {"schedule_pressure": +18, "stakeholder_conf": -7, "risk_exposure": -4, "cost_spent": +2},
            },
            {
                "key": "switch_supplier",
                "label": "Switch to an alternative (untested) supplier",
                "description": "Source equipment from a new supplier. Faster, but the supplier is untested. Quality risk increases.",
                "impact": {"schedule_pressure": +4, "cost_spent": +12, "tech_quality": -9, "risk_exposure": +11},
            },
            {
                "key": "fast_track",
                "label": "Fast-track procurement with premium delivery",
                "description": "Pay for expedited delivery. Keeps schedule close to plan but is expensive and rushed delivery may introduce installation errors.",
                "impact": {"schedule_pressure": +3, "cost_spent": +22, "rework": +9, "risk_exposure": +4},
            },
            {
                "key": "reduce_scope",
                "label": "Remove the delayed component from scope",
                "description": "Remove the affected systems from this phase. Cheaper and faster, but reduces scope and sustainability performance.",
                "impact": {"scope_pct": -10, "schedule_pressure": -8, "sustainability": -12, "risk_exposure": -7},
            },
        ],
    },
    {
        "num": 3,
        "title": "Researcher Scope Request",
        "icon": "🔬",
        "event": """Your research partner has submitted a formal request to expand the facility: **additional experimental tanks, enhanced monitoring stations, and a shared data analysis lab**. The team argues this significantly increases scientific value and will attract future funding.

The request is legitimate but unplanned. The **Finance Manager** flags cost risk. The **Engineering Lead** warns of programme extension. The **Stakeholder Manager** says accepting it will impress funders — but may compromise your schedule commitment.""",
        "options": [
            {
                "key": "accept_full",
                "label": "Accept in full",
                "description": "Add all requested scope. Maximises research value but significantly increases cost, schedule pressure and risk.",
                "impact": {"scope_pct": +13, "cost_spent": +18, "schedule_pressure": +13, "risk_exposure": +12, "stakeholder_conf": +12, "tech_quality": -5},
            },
            {
                "key": "accept_partial",
                "label": "Accept partial scope (monitoring stations only)",
                "description": "A balanced trade-off — adds value without fully overloading schedule and budget.",
                "impact": {"scope_pct": +7, "cost_spent": +8, "schedule_pressure": +5, "risk_exposure": +4, "stakeholder_conf": +8},
            },
            {
                "key": "defer_phase2",
                "label": "Defer entire request to Phase 2",
                "description": "Acknowledge the value but defer to a formally scoped second phase. Pragmatic and honest.",
                "impact": {"stakeholder_conf": +3, "risk_exposure": -4, "schedule_pressure": -2, "sustainability": +3},
            },
            {
                "key": "reject",
                "label": "Reject the request entirely",
                "description": "Decline to protect cost and schedule. Saves budget but damages researcher and funder relationships.",
                "impact": {"stakeholder_conf": -14, "risk_exposure": -7, "schedule_pressure": -4, "cost_spent": -2},
            },
        ],
    },
    {
        "num": 4,
        "title": "Sustainability Review",
        "icon": "🌿",
        "event": """An independent audit triggered by your funder has flagged that current plans meet only **minimum environmental standards**. The funder's criteria require at least 'enhanced' sustainability for the final payment tranche.

The **Engineering Lead** says enhanced systems are technically feasible but require redesign. The **Finance Manager** warns of added cost. The **Stakeholder Manager** says strong sustainability credentials will significantly improve community and partner confidence.""",
        "options": [
            {
                "key": "basic",
                "label": "Maintain basic compliance — argue minimum is sufficient",
                "description": "Saves cost but risks funder relationship and stakeholder confidence. Sustainability score remains weak.",
                "impact": {"sustainability": -5, "stakeholder_conf": -15, "risk_exposure": +10},
            },
            {
                "key": "enhanced",
                "label": "Upgrade to enhanced sustainability systems",
                "description": "Invest in improved water recirculation and energy monitoring. Strong balance of performance and cost.",
                "impact": {"sustainability": +22, "stakeholder_conf": +12, "cost_spent": +10, "tech_quality": +5, "risk_exposure": -5},
            },
            {
                "key": "flagship",
                "label": "Full flagship sustainability redesign",
                "description": "Redesign around leading sustainability standards. Highest reputational value but major cost and schedule impact.",
                "impact": {"sustainability": +35, "stakeholder_conf": +20, "cost_spent": +28, "schedule_pressure": +18, "risk_exposure": +8, "rework": +10},
            },
            {
                "key": "phased",
                "label": "Phased upgrade — enhanced now, flagship deferred",
                "description": "Commit to enhanced systems now. Flagship elements deferred to a funded second phase. Balanced and credible.",
                "impact": {"sustainability": +14, "stakeholder_conf": +8, "cost_spent": +6, "risk_exposure": +2},
            },
        ],
    },
    {
        "num": 5,
        "title": "Community and Planning Concern",
        "icon": "🏘️",
        "event": """A local residents group has submitted formal concerns to the planning authority about **site access routes, construction noise, lighting impact and long-term environmental effects**. If unaddressed, a planning delay notice is possible.

The **Stakeholder Manager** says this is manageable but takes time. The **Project Manager** notes engagement costs schedule days. The **Finance Manager** points out that a planning delay would cost far more than early engagement.""",
        "options": [
            {
                "key": "ignore",
                "label": "Ignore the concerns — continue construction",
                "description": "No engagement. High probability of planning intervention. Fastest short-term but highest long-term risk.",
                "impact": {"stakeholder_conf": -22, "risk_exposure": +18, "schedule_pressure": +8},
            },
            {
                "key": "minimal",
                "label": "Minimal response — formal written clarification",
                "description": "Low effort. Addresses surface concerns but insufficient for deeper community anxieties.",
                "impact": {"stakeholder_conf": -7, "risk_exposure": +5, "schedule_pressure": +2},
            },
            {
                "key": "full",
                "label": "Full community engagement process",
                "description": "Organise a meeting, address concerns and adjust site access. Strong outcome at a moderate schedule cost.",
                "impact": {"stakeholder_conf": +16, "risk_exposure": -12, "schedule_pressure": +8, "cost_spent": +5},
            },
            {
                "key": "co_design",
                "label": "Co-design process with community involvement",
                "description": "Invite the community into the design of affected elements. Highest trust outcome, highest schedule cost.",
                "impact": {"stakeholder_conf": +22, "risk_exposure": -18, "schedule_pressure": +15, "cost_spent": +8, "sustainability": +8},
            },
        ],
    },
    {
        "num": 6,
        "title": "Funder Milestone Pressure",
        "icon": "💼",
        "event": """The funder's programme officer has requested **visible evidence of progress** before releasing the next funding tranche. They want completed physical construction elements and a progress report.

Privately, your **Engineering Lead** reports that while visible construction looks good, **critical technical systems are behind** and not yet integrated. The **Finance Manager** warns that without the next tranche, cash flow becomes difficult within six weeks.""",
        "options": [
            {
                "key": "showcase_only",
                "label": "Showcase visible progress only — don't disclose technical gaps",
                "description": "Secures funding short-term, but hidden technical gaps continue to grow. Increases rework and quality risk.",
                "impact": {"stakeholder_conf": +8, "rework": +13, "tech_quality": -9, "risk_exposure": +12},
            },
            {
                "key": "honest",
                "label": "Provide honest, balanced assessment to funder",
                "description": "Present achievements alongside outstanding technical work. May concern funder short-term but protects long-term trust.",
                "impact": {"stakeholder_conf": +5, "risk_exposure": -10, "tech_quality": +5},
            },
            {
                "key": "accelerate",
                "label": "Accelerate visible milestones to satisfy funder",
                "description": "Redirect resource to complete visible elements faster. Satisfies funder but diverts from critical technical work.",
                "impact": {"schedule_pressure": -4, "cost_spent": +14, "rework": +16, "tech_quality": -11, "risk_exposure": +8},
            },
            {
                "key": "request_ext",
                "label": "Request a milestone reporting extension",
                "description": "Ask the funder for more time to complete properly. Risks funder frustration but avoids misrepresentation.",
                "impact": {"schedule_pressure": -10, "stakeholder_conf": -12, "tech_quality": +10, "risk_exposure": -8},
            },
        ],
    },
    {
        "num": 7,
        "title": "Technical Integration Problem",
        "icon": "⚙️",
        "event": """Your **Engineering Lead** has escalated a critical issue: the **HVAC environmental control system and water treatment system are not integrating correctly**. Sensor incompatibility and failing data feeds have emerged. This affects the facility's core operating capability.

The Engineering Lead estimates three weeks to resolve properly. The **Finance Manager** notes the project is already at 75 % of budget. The **Project Manager** must decide before the problem compounds.""",
        "options": [
            {
                "key": "overtime",
                "label": "Overtime push with existing team",
                "description": "Extend working hours to resolve the issue. Lower cost but increases team fatigue and may not fully fix the root cause.",
                "impact": {"cost_spent": +10, "rework": +8, "tech_quality": +8, "schedule_pressure": +5},
            },
            {
                "key": "specialist",
                "label": "Bring in an external integration specialist",
                "description": "Hire a specialist systems integrator to diagnose and resolve fully. Most effective but expensive.",
                "impact": {"cost_spent": +22, "tech_quality": +20, "schedule_pressure": -5, "risk_exposure": -13, "rework": -5},
            },
            {
                "key": "reduce_tech",
                "label": "Defer the integration — launch with manual monitoring",
                "description": "Remove the linked monitoring function. Saves time but reduces technical quality and sustainability performance.",
                "impact": {"scope_pct": -8, "risk_exposure": -7, "tech_quality": -13, "sustainability": -8, "cost_spent": +2},
            },
            {
                "key": "delay_launch",
                "label": "Delay launch to resolve integration properly",
                "description": "Take the time needed for a full, clean resolution. Protects quality long-term but significantly impacts schedule.",
                "impact": {"schedule_pressure": +20, "stakeholder_conf": -8, "tech_quality": +18, "risk_exposure": -10, "rework": -8},
            },
        ],
    },
    {
        "num": 8,
        "title": "Final Delivery Decision",
        "icon": "🏁",
        "event": """You have reached the **final decision point**. The facility is substantially complete. Your team must now define the official project outcome and present it to the project board.

Your dashboard shows cumulative performance across all metrics. This final decision affects how stakeholders perceive the project and your team's credibility. Choose carefully — and be ready to defend your position.""",
        "options": [
            {
                "key": "full_launch",
                "label": "Full facility launch — declare complete success",
                "description": "Open all systems and present the project as fully complete. Strong confidence outcome — but if quality is low, this is a gamble.",
                "impact": {"stakeholder_conf": +15, "risk_exposure": +8, "scope_pct": +5},
            },
            {
                "key": "partial_launch",
                "label": "Partial launch with documented scope adjustment",
                "description": "Open the core facility and formally document what has been adjusted or deferred. Honest and defensible.",
                "impact": {"stakeholder_conf": +5, "risk_exposure": -12, "scope_pct": -5, "tech_quality": +5},
            },
            {
                "key": "phase_delivery",
                "label": "Phase 1 completion — communicate phased roadmap",
                "description": "Present this as a successful Phase 1 with a clear Phase 2 plan. Professional framing with strong governance.",
                "impact": {"stakeholder_conf": +8, "risk_exposure": -15, "scope_pct": -8, "sustainability": +5, "tech_quality": +8},
            },
            {
                "key": "extend",
                "label": "Recommend formal extension to the project board",
                "description": "Honest recommendation that more time is needed for quality. Lowest short-term confidence, highest long-term value protection.",
                "impact": {"schedule_pressure": -15, "stakeholder_conf": -15, "tech_quality": +16, "risk_exposure": -18},
            },
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def _init():
    defaults = {
        "phase":         "welcome",   # welcome | round1 | game | results
        "round":         2,           # current round (2-8 during game phase)
        "team_name":     "",
        "decisions_log": [],
        "metrics": {
            "scope_pct":        0,
            "schedule_pressure": 0,
            "cost_spent":        0,
            "tech_quality":      0,
            "sustainability":    0,
            "stakeholder_conf":  0,
            "risk_exposure":     0,
            "rework":            0,
        },
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _apply(impact: dict):
    m = st.session_state.metrics
    for key, delta in impact.items():
        if key in m:
            m[key] = max(0, min(100, m[key] + delta))
    st.session_state.metrics = m
    st.session_state.history.append(m.copy())


def _final_score() -> int:
    m = st.session_state.metrics
    s  = (m["scope_pct"] / 100) * 200
    s += max(0, (100 - m["schedule_pressure"]) / 100) * 200
    cost_ctrl = max(0, 100 - max(0, m["cost_spent"] - 80)) / 100
    s += cost_ctrl * 180
    s += (m["tech_quality"]      / 100) * 160
    s += (m["sustainability"]    / 100) * 130
    s += (m["stakeholder_conf"]  / 100) * 80
    s += max(0, (100 - m["risk_exposure"]) / 100) * 50
    s -= (m["rework"] / 100) * 40         # rework penalty
    return int(round(max(0, min(1000, s))))


def _grade(score: int):
    if score >= 800: return "Distinction", "🏆", "#00573F"
    if score >= 650: return "Merit",       "🥈", "#4A9B6F"
    if score >= 500: return "Pass",        "✅", "#2E7D32"
    return "Below Pass", "⚠️", "#C62828"


# ══════════════════════════════════════════════════════════════════════════════
# SHARED WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

def _sidebar_dashboard():
    m = st.session_state.metrics
    with st.sidebar:
        st.markdown(f"### 📊 Live Dashboard")
        if st.session_state.team_name:
            st.markdown(f"**Team:** {st.session_state.team_name}")

        items = [
            ("🎯 Scope Delivered",     "scope_pct",         False, "%"),
            ("⏱️ Schedule Pressure",   "schedule_pressure",  True, "%"),
            ("💰 Cost Spent",          "cost_spent",         True, "% budget"),
            ("🔧 Technical Quality",   "tech_quality",      False, "/100"),
            ("🌿 Sustainability",      "sustainability",     False, "/100"),
            ("🤝 Stakeholder Conf.",   "stakeholder_conf",  False, "/100"),
            ("⚠️ Risk Exposure",       "risk_exposure",      True, "/100"),
            ("🔄 Rework",              "rework",             True, "/100"),
        ]
        for label, key, lower_is_better, unit in items:
            val = m[key]
            if lower_is_better:
                col = "#00573F" if val <= 30 else "#F57F17" if val <= 60 else "#C62828"
            else:
                col = "#C62828" if val <= 30 else "#F57F17" if val <= 60 else "#00573F"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.13);border-radius:7px;
                        padding:7px 11px;margin:3px 0;border-left:4px solid {col};">
              <span style="font-size:.78rem;opacity:.8;">{label}</span><br>
              <span style="font-size:1.2rem;font-weight:700;color:{col};">{val:.0f}{unit}</span>
            </div>""", unsafe_allow_html=True)

        if st.session_state.phase in ("game", "results"):
            proj = _final_score()
            st.markdown("---")
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.18);border-radius:8px;
                        padding:12px;text-align:center;">
              <div style="font-size:.78rem;opacity:.8;">Projected Score</div>
              <div style="font-size:2.2rem;font-weight:700;">{proj}</div>
              <div style="font-size:.75rem;opacity:.65;">out of 1 000</div>
            </div>""", unsafe_allow_html=True)


def _radar_chart():
    m = st.session_state.metrics
    cats = ["Scope", "Schedule", "Cost\nControl", "Technical\nQuality",
            "Sustainability", "Stakeholder\nConf.", "Risk\nControl"]
    vals = [
        m["scope_pct"],
        max(0, 100 - m["schedule_pressure"]),
        max(0, 100 - max(0, (m["cost_spent"] - 80)) * 5),
        m["tech_quality"],
        m["sustainability"],
        m["stakeholder_conf"],
        max(0, 100 - m["risk_exposure"]),
    ]
    vals = [min(100, max(0, v)) for v in vals]

    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(0,87,63,.18)",
        line=dict(color=STIR_GREEN, width=2.5),
        marker=dict(color=STIR_GREEN, size=6),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8)),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _progress_bar(current_round: int):
    """Horizontal round-progress dots."""
    dots = ""
    for i in range(1, 9):
        if i < current_round:
            col, sym = "#00573F", "●"
        elif i == current_round:
            col, sym = "#4A9B6F", "◉"
        else:
            col, sym = "#BCD8CC", "○"
        dots += f'<span style="color:{col};font-size:1.4rem;margin:0 4px;" title="Round {i}">{sym}</span>'
    st.markdown(
        f'<div style="text-align:center;margin:-10px 0 16px;">{dots}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

# ── Welcome ───────────────────────────────────────────────────────────────────
def page_welcome():
    st.markdown(f"""
    <div class="hdr">
      <h1>🌊 AquaHub Delivery Challenge</h1>
      <p>Project Management Simulation &nbsp;·&nbsp; MSc Project Management Programme</p>
      <p style="font-size:.82rem;opacity:.65;">University of Stirling</p>
      <p style="font-size:.78rem;opacity:.55;margin-top:6px;">Created by Areej Riaz · University of Stirling</p>
    </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("""
### Welcome

You are the project delivery team responsible for managing the
**AquaHub sustainable aquaculture research and innovation facility**
for the University of Stirling.

The project is strategically important — but constrained by limited budget,
fixed milestone pressure, specialist procurement, sustainability commitments,
stakeholder scrutiny and technical uncertainty.

**Your task:** make decisions across **8 rounds** as real project conditions
change. Every decision affects scope, cost, schedule, quality, sustainability,
stakeholder trust and risk. There is no single perfect answer.

---
**How to play**

1. Enter your team name and click **Begin Simulation**
2. **Round 1** — set your initial project strategy across six dimensions
3. **Rounds 2 – 8** — respond to live project events with one key decision each
4. Your dashboard updates after every decision
5. After Round 8 — see your final score and breakdown
        """)

        st.markdown("#### 🏷️ Team Setup")
        tname = st.text_input("Team name:", placeholder="e.g. Team Osprey")
        if st.button("Begin Simulation →", use_container_width=True):
            if tname.strip():
                st.session_state.team_name = tname.strip()
                st.session_state.phase = "round1"
                st.rerun()
            else:
                st.error("Please enter a team name.")

    with col_r:
        st.markdown("#### 🎭 Project Team Roles")
        for icon, role, desc in [
            ("🎯", "Project Manager",    "Coordination, final decisions, trade-off management"),
            ("⚙️", "Engineering Lead",   "Technical feasibility, quality, integration"),
            ("📦", "Procurement Manager","Suppliers, equipment, contractor capacity"),
            ("💰", "Finance Manager",    "Budget control, contingency, cost escalation"),
            ("🤝", "Stakeholder Manager","Funders, researchers, community, sustainability"),
        ]:
            st.markdown(f"""
            <div style="background:white;border-radius:8px;padding:9px 13px;margin:5px 0;
                        border-left:3px solid {STIR_GREEN};font-size:.85rem;">
              <strong>{icon} {role}</strong><br>
              <span style="color:#555;">{desc}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 📊 Scoring Model (1 000 pts)")
        for metric, pts in [
            ("Scope Delivered", 200), ("Schedule Performance", 200),
            ("Cost Control", 180),    ("Technical Quality", 160),
            ("Sustainability", 130),  ("Stakeholder Confidence", 80),
            ("Risk Management", 50),
        ]:
            bar = int(pts / 200 * 100)
            st.markdown(f"""
            <div style="margin:3px 0;font-size:.8rem;">
              <div style="display:flex;justify-content:space-between;">
                <span>{metric}</span>
                <span style="color:{STIR_GREEN};font-weight:600;">{pts}</span>
              </div>
              <div style="background:#E8F5EE;border-radius:4px;height:5px;margin-top:2px;">
                <div style="background:{STIR_GREEN};width:{bar}%;height:5px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)


# ── Round 1 ───────────────────────────────────────────────────────────────────
def page_round1():
    _sidebar_dashboard()

    st.markdown(f"""
    <div class="hdr">
      <span class="round-pill">Round 1 of 8</span>
      <h2>Project Initiation</h2>
      <p>Set your project strategy — these foundational choices shape your entire risk profile</p>
    </div>""", unsafe_allow_html=True)

    _progress_bar(1)

    st.markdown("""
    <div class="card">
    <p>The AquaHub facility has been formally approved. Your team must now make the foundational
    decisions that will govern how the project is managed from this point forward.</p>
    <p>The <strong>Project Manager</strong> leads this session. Each role should contribute before the
    team agrees a collective position. Remember: high ambition requires strong resources — and a
    realistic timeline.</p>
    </div>""", unsafe_allow_html=True)

    with st.form("round1_form"):
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**🎯 Scope Level**")
            scope = st.radio("What scope will you commit to?",
                             list(SCOPE_OPTIONS.keys()), index=1, key="r1_scope")

            st.markdown("**⏱️ Schedule Target**")
            schedule = st.radio("Which delivery schedule will you target?",
                                list(SCHEDULE_OPTIONS.keys()), index=1, key="r1_sched")

            st.markdown("**📦 Procurement Approach**")
            procure = st.radio("How will you manage procurement?",
                               list(PROCUREMENT_OPTIONS.keys()), index=0, key="r1_proc")

        with c2:
            st.markdown("**👷 Contractor Capacity**")
            contractor = st.radio("What contractor capacity will you resource?",
                                  list(CONTRACTOR_OPTIONS.keys()), index=1, key="r1_cont")

            st.markdown("**🌿 Sustainability Standard**")
            sustain = st.radio("What sustainability standard will you design to?",
                               list(SUSTAIN_OPTIONS.keys()), index=1, key="r1_sust")

            st.markdown("**🤝 Stakeholder Engagement**")
            stakeholder = st.radio("How will you engage stakeholders?",
                                   list(STAKEHOLDER_OPTIONS.keys()), index=1, key="r1_stak")

        submitted = st.form_submit_button("Confirm Round 1 — Enter the Simulation →",
                                          use_container_width=True)

    if submitted:
        # Build initial metrics from combined choices
        m = {k: 0 for k in st.session_state.metrics}
        m["stakeholder_conf"] = 60  # base

        for table in [
            SCOPE_OPTIONS[scope],
            SCHEDULE_OPTIONS[schedule],
            PROCUREMENT_OPTIONS[procure],
            CONTRACTOR_OPTIONS[contractor],
            SUSTAIN_OPTIONS[sustain],
            STAKEHOLDER_OPTIONS[stakeholder],
        ]:
            for k, v in table.items():
                m[k] = m.get(k, 0) + v

        m = {k: int(max(0, min(100, v))) for k, v in m.items()}
        st.session_state.metrics = m
        st.session_state.history.append(m.copy())
        st.session_state.decisions_log.append({
            "round": 1, "title": "Project Initiation",
            "decision": (
                f"Scope: {scope.split('(')[0].strip()} | "
                f"Schedule: {schedule.split('(')[0].split('+')[0].split('−')[0].strip()} | "
                f"Sustainability: {sustain.split('(')[0].strip()}"
            ),
        })
        st.session_state.round = 2
        st.session_state.phase = "game"
        st.rerun()


# ── Rounds 2–8 ───────────────────────────────────────────────────────────────
def page_game():
    _sidebar_dashboard()

    rnum = st.session_state.round
    rdata = next(r for r in ROUNDS if r["num"] == rnum)

    st.markdown(f"""
    <div class="hdr">
      <span class="round-pill">Round {rnum} of 8</span>
      <h2>{rdata['icon']} {rdata['title']}</h2>
    </div>""", unsafe_allow_html=True)

    _progress_bar(rnum)

    # Midpoint pause
    if rnum == 5:
        st.info(
            "⏸️ **Midpoint Pause** — Your facilitator will now lead a brief dashboard review.  \n"
            "Are you on track? What is your biggest risk? Has your strategy changed?"
        )

    col_main, col_right = st.columns([3, 2])

    with col_main:
        st.markdown(f'<div class="card">{rdata["event"]}</div>', unsafe_allow_html=True)
        st.markdown("#### What does your team decide?")

        choice_label = st.radio(
            "Select your decision:",
            [o["label"] for o in rdata["options"]],
            key=f"r{rnum}_choice",
        )
        chosen = next(o for o in rdata["options"] if o["label"] == choice_label)

        st.markdown(f'<div class="opt-hint">{chosen["description"]}</div>',
                    unsafe_allow_html=True)

        next_label = (
            f"Confirm & Proceed to Round {rnum + 1} →" if rnum < 8
            else "Confirm & See Final Results →"
        )
        if st.button(next_label, use_container_width=True):
            _apply(chosen["impact"])
            st.session_state.decisions_log.append({
                "round": rnum,
                "title": rdata["title"],
                "decision": choice_label,
            })
            if rnum < 8:
                st.session_state.round = rnum + 1
            else:
                st.session_state.phase = "results"
            st.rerun()

    with col_right:
        st.markdown("#### Current Performance")
        st.plotly_chart(_radar_chart(), use_container_width=True)

        done = rnum - 1
        pct  = done / 8 * 100
        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:12px;margin-top:6px;">
          <div style="font-size:.78rem;color:#666;margin-bottom:5px;">Progress</div>
          <div style="background:#E8F5EE;border-radius:4px;height:8px;">
            <div style="background:{STIR_GREEN};width:{pct:.0f}%;height:8px;border-radius:4px;"></div>
          </div>
          <div style="font-size:.78rem;color:{STIR_GREEN};margin-top:4px;text-align:right;">
            {done} / 8 rounds complete
          </div>
        </div>""", unsafe_allow_html=True)

        # Key risk warnings
        m = st.session_state.metrics
        warnings = []
        if m["risk_exposure"] > 60:
            warnings.append("🔴 Risk exposure is high")
        if m["schedule_pressure"] > 65:
            warnings.append("🔴 Schedule pressure critical")
        if m["cost_spent"] > 85:
            warnings.append("🔴 Budget nearly exhausted")
        if m["stakeholder_conf"] < 35:
            warnings.append("🟡 Stakeholder confidence low")
        if m["tech_quality"] < 40:
            warnings.append("🟡 Technical quality at risk")
        if warnings:
            st.markdown("**⚠️ Watch Points**")
            for w in warnings:
                st.markdown(f"<small>{w}</small>", unsafe_allow_html=True)


# ── Results ───────────────────────────────────────────────────────────────────
def page_results():
    _sidebar_dashboard()

    score = _final_score()
    g_label, g_icon, g_col = _grade(score)
    m = st.session_state.metrics

    st.markdown(f"""
    <div class="score-final">
      <div style="font-size:.9rem;opacity:.75;">AquaHub Delivery Challenge — Final Results</div>
      <div style="font-size:1.3rem;font-weight:600;margin-top:6px;">
        {st.session_state.team_name}
      </div>
      <div style="font-size:4.5rem;font-weight:700;line-height:1.1;">{score}</div>
      <div style="font-size:.95rem;opacity:.75;">out of 1 000 points</div>
      <div style="font-size:1.4rem;margin-top:10px;">{g_icon} {g_label}</div>
    </div>""", unsafe_allow_html=True)

    # ── Score breakdown ──
    st.markdown("### Score Breakdown")
    components = [
        ("🎯 Scope Delivered",       (m["scope_pct"] / 100) * 200,                         200),
        ("⏱️ Schedule Performance",  max(0, (100 - m["schedule_pressure"]) / 100) * 200,    200),
        ("💰 Cost Control",          max(0, 100 - max(0, m["cost_spent"] - 80)) / 100 * 180, 180),
        ("🔧 Technical Quality",     (m["tech_quality"] / 100) * 160,                       160),
        ("🌿 Sustainability",        (m["sustainability"] / 100) * 130,                      130),
        ("🤝 Stakeholder Confidence",(m["stakeholder_conf"] / 100) * 80,                     80),
        ("⚠️ Risk Management",       max(0, (100 - m["risk_exposure"]) / 100) * 50,          50),
    ]

    col_a, col_b = st.columns(2)
    for i, (label, pts, max_pts) in enumerate(components):
        pct = pts / max_pts * 100
        col = "#C62828" if pct < 40 else "#F57F17" if pct < 70 else "#00573F"
        bar_html = f"""
        <div class="breakdown-row">
          <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:.9rem;">
            <span>{label}</span>
            <span style="font-weight:700;color:{col};">{pts:.0f} / {max_pts}</span>
          </div>
          <div style="background:#E8F5EE;border-radius:4px;height:7px;">
            <div style="background:{col};width:{pct:.0f}%;height:7px;border-radius:4px;"></div>
          </div>
        </div>"""
        (col_a if i % 2 == 0 else col_b).markdown(bar_html, unsafe_allow_html=True)

    # Rework penalty
    penalty = m["rework"] / 100 * 40
    if penalty > 0:
        col_b.markdown(f"""
        <div style="background:#FFF3E0;border-radius:8px;padding:10px 14px;margin:4px 0;
                    border-left:4px solid #F57F17;font-size:.88rem;">
          🔄 Rework Penalty &nbsp;
          <span style="float:right;font-weight:700;color:#C62828;">−{penalty:.0f} pts</span>
        </div>""", unsafe_allow_html=True)

    # ── Radar ──
    st.markdown("### Project Performance Profile")
    col_chart, col_final = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(_radar_chart(), use_container_width=True)
    with col_final:
        st.markdown("#### Final Metrics")
        for label, key, lower_is_better, unit in [
            ("Scope Delivered",    "scope_pct",         False, "%"),
            ("Schedule Pressure",  "schedule_pressure",  True, "%"),
            ("Cost Spent",         "cost_spent",         True, "% budget"),
            ("Technical Quality",  "tech_quality",      False, "/100"),
            ("Sustainability",     "sustainability",     False, "/100"),
            ("Stakeholder Conf.",  "stakeholder_conf",  False, "/100"),
            ("Risk Exposure",      "risk_exposure",      True, "/100"),
            ("Rework",             "rework",             True, "/100"),
        ]:
            val = m[key]
            col = ("#C62828" if (val > 60 if lower_is_better else val < 40)
                   else "#F57F17" if (val > 30 if lower_is_better else val < 65)
                   else "#00573F")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:7px 11px;margin:3px 0;
                        border-left:4px solid {col};font-size:.82rem;">
              <span style="color:#555;">{label}</span><br>
              <span style="font-weight:700;color:{col};">{val:.0f}{unit}</span>
            </div>""", unsafe_allow_html=True)

    # ── Decision log ──
    st.markdown("### Your Decision Record")
    for d in st.session_state.decisions_log:
        st.markdown(f"""
        <div class="decision-log-item">
          <strong>Round {d['round']}: {d['title']}</strong><br>
          <span style="color:#444;">{d['decision']}</span>
        </div>""", unsafe_allow_html=True)

    # ── Debrief prompts ──
    st.markdown("### 💬 Debrief Discussion Points")
    for q in [
        "Did your Round 1 strategy hold throughout, or did you adapt it? Why?",
        "Which single decision had the biggest impact on your final score?",
        "Did the fastest schedule produce the best overall outcome?",
        "How did your sustainability choices affect other metrics?",
        "Which role's concerns were most important in hindsight?",
        "What would you do differently if you played again?",
        "How would you present this outcome to senior leadership?",
    ]:
        st.markdown(f"""
        <div style="background:{STIR_PALE};border-radius:7px;padding:8px 13px;margin:4px 0;
                    font-size:.88rem;border-left:3px solid {STIR_LT};">
          {q}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Play Again (Reset Simulation)", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    _init()
    phase = st.session_state.phase

    if   phase == "welcome": page_welcome()
    elif phase == "game":    page_game()
    elif phase == "results": page_results()
    st.markdown(
        "<div style='text-align:center;font-size:.78rem;color:#888;padding:8px 0 16px;'>"
        "Created by <strong>Areej Riaz</strong> &nbsp;·&nbsp; University of Stirling &nbsp;·&nbsp; "
        "MSc Project Management Programme</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
