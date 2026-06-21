"""
The Areej Tea Company Brief: International Strategy Consultancy Simulation
MSc Project Management · University of Stirling
An MSc Project Management teaching simulation.

Pedagogical purpose: Unlike passive case study reading, this simulation places
students inside the PM role of a real consultancy engagement. Every decision
compounds — just as it does in practice. Students experience Brooks's Law,
the overtime paradox, scope creep, rework spirals, and critical path
dependencies firsthand, then debrief against Areej Riaz's actual priorities.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(
    page_title="The Areej Tea Company Brief",
    page_icon="\U0001f375",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

/* University of Stirling brand colours:
   Heritage Green #006938 | Energy Green #76b72a | Teal #008996
   Yellow #edab00 | Orange #d9541a | Dark Green #005734 */

html, body, [class*="css"] {
  font-family: 'DM Sans', Calibri, sans-serif;
}
h1,h2,h3,h4 { font-family: 'Nunito', Calibri, sans-serif; }

.main-header{background:linear-gradient(135deg,#005734 0%,#006938 60%,#008996 100%);
  color:white;padding:1.5rem 2rem;border-radius:12px;margin-bottom:1.5rem;text-align:center;}
.main-header h1{font-size:2rem;margin:0;font-weight:800;font-family:'Nunito',Calibri,sans-serif;}
.main-header p{font-size:1rem;margin:.3rem 0 0;opacity:.9;}
.phase-bar{background:#e8f5ee;border-left:5px solid #006938;border-radius:8px;
  padding:.8rem 1.2rem;margin:.5rem 0 1rem;}
.phase-bar b{color:#005734;}
.event-box{background:#fff8e1;border-left:5px solid #edab00;border-radius:8px;
  padding:1rem 1.2rem;margin:1rem 0;}
.event-box h4{margin:0 0 .4rem;color:#7b5c18;}
.gate-box{background:#e8f5ee;border-left:5px solid #76b72a;border-radius:8px;
  padding:1.2rem 1.5rem;margin:1rem 0;}
.score-box{background:linear-gradient(135deg,#005734 0%,#006938 60%,#008996 100%);
  color:white;border-radius:12px;padding:2rem;text-align:center;margin:1rem 0;}
.score-box .total{font-size:4rem;font-weight:800;font-family:'Nunito',Calibri,sans-serif;}
.brief-box{background:#f2f9f5;border:1px solid #9fcc69;border-radius:10px;
  padding:1.5rem;margin:1rem 0;}
.rec-box{background:#f5f7f2;border:1px solid #c5e28b;border-radius:10px;
  padding:1.2rem 1.5rem;margin:.8rem 0;}
.rec-correct{background:#e8f5ee;border-left:4px solid #006938;border-radius:8px;
  padding:.8rem 1rem;margin:.4rem 0;}
.rec-partial{background:#fff8e1;border-left:4px solid #edab00;border-radius:8px;
  padding:.8rem 1rem;margin:.4rem 0;}
.reflection-box{background:#f2f9f5;border-left:4px solid #76b72a;border-radius:8px;
  padding:1rem 1.2rem;margin:.5rem 0;}
.stButton>button{border-radius:8px;font-weight:600;padding:.5rem 1.5rem;
  font-family:'DM Sans',Calibri,sans-serif;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
BUDGET       = 32000
SKILL_MULT   = {"Graduate Analyst": 0.80, "Consultant": 1.00, "Senior Partner": 1.25}
WEEKLY_COST  = {"Graduate Analyst": 500,  "Consultant": 800,  "Senior Partner": 1200}
OUT_CAP      = {"None": 0.00, "Selective": 0.20, "Full": 0.40}
OUT_COST     = {"None": 0,    "Selective": 1500,  "Full": 3000}
OUT_COORD    = {"None": 0,    "Selective": 5,     "Full": 12}
MTG_COORD    = {"Light": -5,  "Balanced": 8,  "Intensive": 12}
MTG_PROD     = {"Light": 0,   "Balanced": .03,"Intensive": .12}
MTG_MORALE   = {"Light": -2,  "Balanced": 3,  "Intensive": -5}
OT_CAP       = {"None": 0.00, "Allowed": 0.10,"Heavy": 0.22}
OT_STRESS    = {"None": 0,    "Allowed": 6,   "Heavy": 14}
OT_MORALE    = {"None": 0,    "Allowed": -3,  "Heavy": -9}
SCOPE_TASKS  = {"Focused": 60,"Standard": 90,"Comprehensive": 120,"Full-Service": 150}
PILOT_COST   = 1200

PHASES = {
    1: ("Phase 1 — Import Analysis",     "Weeks 1–3",  "Q1 & Q2: Sourcing strategy + financial implications"),
    2: ("Phase 2 — Export Research",     "Weeks 4–6",  "Q3 & Q4: Global demand + target market selection"),
    3: ("Phase 3 — Strategy Synthesis",  "Weeks 7–8+", "Q5 & Q6: Entry mode + financial projections"),
}

SCENARIOS = {
    "Scenario 1 – Balanced Engagement": {
        "desc": "Standard 8-week engagement. Areej is cooperative, data arrives on time, brief is clear. The usual PM tensions — scope, quality, budget, people — all apply.",
        "focus": "Core PM trade-offs · Iron Triangle",
        "events": {},
    },
    "Scenario 2 – Consultant Leaves": {
        "desc": "Week 4: your lead market research consultant goes off sick. Two fewer hands for two weeks, no immediate replacement. Brooks's Law on display.",
        "focus": "People management · Brooks's Law",
        "events": {4: "staffing_shock"},
    },
    "Scenario 3 – Deadline Compression": {
        "desc": "Areej lands an unexpected distributor meeting at a trade fair — she needs your recommendations one week early. Parkinson's Law works in reverse.",
        "focus": "Schedule pressure · Critical path",
        "events": {4: "deadline_compress"},
    },
    "Scenario 4 – Scope Creep": {
        "desc": "Areej asks you to also assess Latin America and evaluate sustainability certification — not in the original brief. Hold the line or absorb the change?",
        "focus": "Scope change · Stakeholder management",
        "events": {5: "scope_creep"},
    },
    "Scenario 5 – High Uncertainty": {
        "desc": "Survey data has gaps, supplier dataset arrives with pricing errors, and Areej pivots her priority export region mid-project. Pilot analysis is your insurance.",
        "focus": "Ambiguity · Rework spiral · Pilot analysis",
        "events": {3: "unclear_needs", 5: "data_gap", 7: "req_change"},
    },
}

RECS = {
    "import_route": {
        "q": "Which import strategy do you recommend to Areej?",
        "opts": [
            "UK Wholesaler only — find a new domestic supplier",
            "International Wholesaler — better pricing, still arm\'s length",
            "Direct from Source — cooperatives in Kenya, Assam, Ceylon",
            "Combination — direct for primary origins, wholesaler as backup",
        ],
        "best": 3,
        "why": "Areej values sustainability, exact pricing, and not exploiting farmers at source. A combination of direct sourcing (primary origins) with a wholesale safety net gives cost control, supply resilience, and ethical alignment.",
    },
    "export_region": {
        "q": "Which region should Areej Tea prioritise for export first?",
        "opts": [
            "Western Europe — proximity, easy logistics",
            "Asia-Pacific — growing premium market, appetite for imported goods",
            "Middle East — luxury culture, strong gifting tradition",
            "Latin America — emerging market, lower competition",
        ],
        "best": 1,
        "why": "Areej explicitly said Europe is already saturated with premium brands. Asia-Pacific offers a growing appetite for premium imported goods and an untapped opportunity for authentic Scottish brand positioning.",
    },
    "entry_mode": {
        "q": "How should Areej Tea enter international markets?",
        "opts": [
            "Direct-to-Consumer online — full margin, but high shipping and duties",
            "International Wholesalers — lower margin, simpler, scalable",
            "Own Distribution Centre — strategic control, high upfront cost",
            "Start with wholesalers, layer in DTC as brand establishes",
        ],
        "best": 3,
        "why": "Areej expressed concern about DTC margin erosion via shipping and duties. Starting with established wholesalers builds market presence with lower risk; adding DTC channels once brand is known is the proven internationalisation path for premium FMCG.",
    },
    "sustainability": {
        "q": "On sustainability in sourcing — what is your recommendation?",
        "opts": [
            "No premium — optimise purely for lowest cost",
            "Only if margin allows — conditional approach",
            "Yes, pay sustainability premium — non-negotiable brand value",
            "Pursue Fairtrade/Rainforest Alliance certification as differentiator",
        ],
        "best": 2,
        "why": "Areej\'s exact words: \'We are willing to pay a little bit more so not to exploit farmers at source.\' Sustainability is a stated founder value, not a financial calculation. Recommending otherwise misreads the client.",
    },
}

# ── State Init ────────────────────────────────────────────────────────────────
def init_state():
    d = dict(
        phase="welcome", scenario=None, week=1, max_weeks=10,
        budget=BUDGET, cost_spent=0.0,
        morale=75.0, stress=30.0, quality=80.0, coordination=60.0,
        tasks_completed=0.0, defects=0.0, tasks_required=90,
        scope="Standard", schedule_target=8, team_size=4, skill="Consultant",
        prototype_count=0, history=[], pending_event=None,
        schedule_weight=100, hiring_freeze=0, event_log=[], final_score=None,
        prev_team_size=4,
        phase1_quality_sum=0.0, phase1_weeks=0,
        phase2_quality_sum=0.0, phase2_weeks=0,
        gate1_done=False, gate2_done=False,
        rec_answers={}, rec_score=0,
    )
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

def current_phase():
    if s.week <= 3: return 1
    if s.week <= 6: return 2
    return 3

def phase_label():
    ph = current_phase()
    return PHASES[ph]

# ── Compute Week ──────────────────────────────────────────────────────────────
def compute_week(team_size, skill, outsourcing, overtime, meetings, pilot):
    # Base output
    base = team_size * SKILL_MULT[skill] * 6
    # Learning curve: team gets faster as they understand the case (2%/week, cap 15%)
    learning = min(1.15, 1.0 + (s.week - 1) * 0.02)
    # If team size changed significantly, learning resets partially (Brooks\'s Law)
    if abs(team_size - s.prev_team_size) >= 2:
        learning = 1.0 + (learning - 1.0) * 0.4
    morale_f   = s.morale / 100
    stress_f   = max(0.45, 1 - s.stress / 140)
    coord_f    = s.coordination / 100
    out_f      = 1 + OUT_CAP[outsourcing]
    ot_f       = 1 + OT_CAP[overtime]
    mtg_pen    = 1 - MTG_PROD[meetings]
    output = base * learning * morale_f * stress_f * coord_f * out_f * ot_f * mtg_pen

    # Quality
    q = 85
    if skill == "Senior Partner": q += 5
    if skill == "Graduate Analyst": q -= 7
    q -= s.stress * 0.20
    if pilot: q += 6
    q += s.coordination * 0.05
    if overtime == "Heavy": q -= 8
    # Critical path: if Phase 1 quality was poor, Phase 3 synthesis suffers
    if current_phase() == 3 and s.phase1_weeks > 0:
        p1q = s.phase1_quality_sum / s.phase1_weeks
        if p1q < 68:
            q -= 10  # built on shaky analytical foundations
    q = min(100, max(0, q))

    rework = output * max(0, (75 - q)) / 100
    net    = max(0, output - rework)

    cost = team_size * WEEKLY_COST[skill] + OUT_COST[outsourcing] + (PILOT_COST if pilot else 0)

    # Stress
    rem_tasks = max(0, s.tasks_required - s.tasks_completed)
    rem_weeks = max(1, s.schedule_target - s.week + 1)
    dl_press  = (rem_tasks / rem_weeks) / 15
    new_stress = s.stress + dl_press + OT_STRESS[overtime]
    new_stress += max(0, team_size - 8) * 1.5
    if meetings == "Balanced": new_stress -= 3
    new_stress = min(100, max(0, new_stress))

    # Morale
    new_morale = s.morale + MTG_MORALE[meetings] + OT_MORALE[overtime]
    new_morale -= max(0, new_stress - 65) * 0.08
    new_morale += 2 if net >= 8 else -2
    new_morale = min(100, max(0, new_morale))

    # Coordination
    new_coord = s.coordination + MTG_COORD[meetings]
    new_coord -= OUT_COORD[outsourcing]
    new_coord -= max(0, team_size - 7) * 2
    if pilot: new_coord += 5
    new_coord = min(100, max(0, new_coord))

    # Track phase quality
    ph = current_phase()
    if ph == 1:
        s.phase1_quality_sum += q
        s.phase1_weeks       += 1
    elif ph == 2:
        s.phase2_quality_sum += q
        s.phase2_weeks       += 1

    s.tasks_completed += net
    s.defects         += rework
    s.cost_spent      += cost
    s.morale           = new_morale
    s.stress           = new_stress
    s.quality          = q
    s.coordination     = new_coord
    s.prev_team_size   = team_size
    if pilot: s.prototype_count += 1

    return dict(week=s.week, net=round(net,1), rework=round(rework,1),
                cost=round(cost), quality=round(q,1), morale=round(new_morale,1),
                stress=round(new_stress,1), team=team_size, skill=skill,
                outsourcing=outsourcing, overtime=overtime, meetings=meetings, pilot=pilot)

def calc_final_score():
    done  = s.tasks_completed
    req   = s.tasks_required
    scope_s    = min(250, 250 * done / req)
    delay      = max(0, s.week - 1 - s.schedule_target)
    sched_s    = 250 if (done >= req and s.week - 1 <= s.schedule_target) else max(0, 250 - delay * 50)
    cost_s     = max(0, 200 * (1 - max(0, s.cost_spent - s.budget) / s.budget))
    qual_s     = 150 * s.quality / 100
    team_s     = 150 * ((s.morale/100)*0.6 + ((100-s.stress)/100)*0.4)
    total      = scope_s + sched_s + cost_s + qual_s + team_s
    return dict(scope=round(scope_s), schedule=round(sched_s), cost=round(cost_s),
                quality=round(qual_s), team=round(team_s), total=round(total))

def apply_event(key, choice=None):
    if key == "staffing_shock":
        s.team_size_post_shock = max(3, s.team_size_snapshot - 2)
        s.morale   = max(0, s.morale - 8)
        s.stress   = min(100, s.stress + 10)
        s.hiring_freeze = 2
        s.event_log.append("Week 4: Lead consultant off sick — 2 fewer people, hiring freeze for 2 weeks. (Brooks\'s Law: the remaining team now spends time covering gaps.)")

    elif key == "deadline_compress":
        s.schedule_target = max(s.week, s.schedule_target - 1)
        s.stress = min(100, s.stress + 12)
        s.schedule_weight = 180
        s.event_log.append("Week 4: Areej secured a distributor meeting at a trade fair — deadline moved forward 1 week.")

    elif key == "scope_creep":
        if choice == "full":
            s.tasks_required += 25
            s.morale = max(0, s.morale - 5)
            s.event_log.append("Week 5: Full scope accepted — Latin America + sustainability audit (+25 deliverables). Schedule at serious risk.")
        elif choice == "partial":
            s.tasks_required += 12
            s.event_log.append("Week 5: Partial scope accepted — Latin America only (+12 deliverables). Compromise reached.")
        else:
            s.event_log.append("Week 5: Scope held — original brief maintained. Client relationship risk acknowledged.")

    elif key == "unclear_needs":
        pen = 0.5 if s.prototype_count >= 1 else 1.0
        lost = round(8 * pen)
        s.tasks_completed = max(0, s.tasks_completed - lost)
        s.event_log.append(f"Week 3: Market survey has insufficient responses for 3 target markets. Rework required ({lost} deliverables lost). Pilot analysis halves this penalty.")

    elif key == "data_gap":
        pen = 0.5 if s.prototype_count >= 2 else 1.0
        lost = round(12 * pen)
        s.tasks_completed = max(0, s.tasks_completed - lost)
        s.stress = min(100, s.stress + 8)
        s.event_log.append(f"Week 5: Supplier dataset has pricing errors — financial analysis must be redone ({lost} deliverables lost).")

    elif key == "req_change":
        pen = 0.5 if s.prototype_count >= 2 else 1.0
        lost = round(10 * pen)
        s.tasks_completed = max(0, s.tasks_completed - lost)
        s.event_log.append(f"Week 7: Areej pivots priority export region to the Middle East after a new distributor contact ({lost} deliverables lost).")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tea.png", width=56)
    st.markdown("## The Areej Tea Company Brief")
    st.caption("MSc Project Management Simulation")
    st.divider()
    if s.phase not in ("welcome","setup"):
        ph_name, ph_weeks, ph_qs = phase_label()
        st.markdown(f"""<div class="phase-bar"><b>{ph_name}</b><br>
        <small>{ph_weeks} &nbsp;|&nbsp; {ph_qs}</small></div>""", unsafe_allow_html=True)
        prog = min(1.0, s.tasks_completed / max(1, s.tasks_required))
        st.markdown("**Deliverables**")
        st.progress(prog)
        st.caption(f"{round(s.tasks_completed)} / {s.tasks_required} ({round(prog*100)}%)")
        st.divider()
        c1,c2 = st.columns(2)
        c1.metric("Budget", f"£{s.budget:,}", f"-£{round(s.cost_spent):,}")
        c2.metric("Week", f"{s.week}", f"/ {s.max_weeks}")
        st.divider()
        st.markdown(f"**Morale:** {round(s.morale)}/100")
        st.progress(s.morale/100)
        st.markdown(f"**Stress:** {round(s.stress)}/100")
        st.progress(s.stress/100)
        st.markdown(f"**Quality:** {round(s.quality)}/100")
        st.progress(s.quality/100)
        if s.phase1_weeks > 0:
            p1q = round(s.phase1_quality_sum / s.phase1_weeks)
            st.caption(f"Phase 1 avg quality: {p1q}/100")
        st.divider()
    if st.button("Restart", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.divider()
    st.caption("Designed by **Areej Riaz** · University of Stirling")

# ── WELCOME ───────────────────────────────────────────────────────────────────
if s.phase == "welcome":
    st.markdown("""<div class="main-header">
    <h1>The Areej Tea Company Brief</h1>
    <p>International Strategy Consultancy Simulation &nbsp;·&nbsp; MSc Project Management</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("""<div class="brief-box">
        <h3>Why a simulation?</h3>
        <p>Reading a case study tells you <em>what</em> happened. This simulation puts you <em>inside</em> it.
        Every decision you make compounds — just as it does in a real consultancy engagement.
        You will feel Brooks\'s Law, the overtime paradox, the rework spiral, and the critical path
        dependency firsthand. Then you will debrief against real data.</p>
        <h3>Your Mission</h3>
        <p>You are a consultancy team hired by <strong>Areej Riaz</strong>, founder of
        <strong>Areej Tea Company</strong> — a Scottish premium tea brand with
        £3.1M turnover, 800 stockists, and a collapsing supplier relationship.
        She needs strategic recommendations on two urgent problems:</p>
        <ul>
        <li><strong>Import crisis:</strong> Her tea leaf supplier tried to near-double prices.
        Find a new strategy — UK wholesale, international wholesale, or direct from source.</li>
        <li><strong>Export ambition:</strong> Which markets? Which entry mode — DTC, wholesale,
        or distribution centre? What are the financial implications?</li>
        </ul>
        <p>You have <strong>£32,000</strong> (Areej\'s professional services budget for this engagement)
        and up to 8 weeks to deliver a strategy report and present to her board.</p>
        <p>Your goal is not just to finish — it is to deliver <strong>rigorous analysis, on time,
        within budget, without burning out your team.</strong></p>
        </div>""", unsafe_allow_html=True)

        st.markdown("**Your Consultancy Team Roles**")
        for r,d in {
            "Project Lead":"Overall accountability. Makes the call each week.",
            "Finance Consultant":"Monitors the £32,000 budget and fee burn.",
            "Research Analyst":"Tracks deliverable quality and rework.",
            "Client Manager":"Manages Areej\'s expectations and scope.",
        }.items():
            st.markdown(f"**{r}** — {d}")

        st.divider()
        if st.button("Begin Simulation", use_container_width=True, type="primary"):
            s.phase = "setup"; st.rerun()

# ── SETUP ─────────────────────────────────────────────────────────────────────
elif s.phase == "setup":
    st.markdown("""<div class="main-header">
    <h1>Set Up Your Engagement</h1>
    <p>Choose your scenario and opening plan</p>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Choose a Scenario")
        sc_name = st.radio("", list(SCENARIOS.keys()), label_visibility="collapsed")
        sc = SCENARIOS[sc_name]
        st.markdown(f"""<div class="brief-box">
        <b>PM focus:</b> {sc["focus"]}<br><br>{sc["desc"]}</div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("### Opening Plan")
        scope = st.selectbox("Engagement scope", list(SCOPE_TASKS.keys()), index=1,
            help="Focused=60 (import only) | Standard=90 | Comprehensive=120 | Full-Service=150")
        st.caption({
            "Focused":"Import strategy only (Q1–Q2)",
            "Standard":"Import + export strategy (Q1–Q6)",
            "Comprehensive":"Full strategy + competitor benchmarking",
            "Full-Service":"Complete analysis + sensitivity modelling",
        }[scope] + f" — {SCOPE_TASKS[scope]} deliverables")

        schedule = st.slider("Delivery target (weeks)", 6, 9, 8)
        team     = st.slider("Starting team size", 2, 8, 4)
        skill    = st.selectbox("Consultant grade", list(SKILL_MULT.keys()), index=1)
        wk_cost  = team * WEEKLY_COST[skill]
        st.caption(f"Weekly fee burn: £{wk_cost:,}  |  {schedule}-week estimate: £{wk_cost*schedule:,}")
        pct = round(wk_cost * schedule / BUDGET * 100)
        st.info(f"That uses **{pct}%** of the £{BUDGET:,} budget before any extras.")

    st.divider()
    if st.button("Start Engagement", use_container_width=True, type="primary"):
        s.scenario=sc_name; s.scope=scope; s.tasks_required=SCOPE_TASKS[scope]
        s.schedule_target=schedule; s.team_size=team; s.skill=skill
        s.prev_team_size=team; s.phase="playing"; st.rerun()

# ── PLAYING ───────────────────────────────────────────────────────────────────
elif s.phase == "playing":
    sc_events = SCENARIOS[s.scenario]["events"]
    if s.week in sc_events and s.pending_event is None:
        evt = sc_events[s.week]
        if evt == "scope_creep":
            s.pending_event = evt; s.phase = "event"; st.rerun()
        else:
            if evt == "staffing_shock": s.team_size_snapshot = s.team_size
            apply_event(evt)
            if evt == "staffing_shock" and hasattr(s,"team_size_post_shock"):
                s.team_size = s.team_size_post_shock

    # Phase gates
    if s.week == 4 and not s.gate1_done:
        s.phase = "gate1"; st.rerun()
    if s.week == 7 and not s.gate2_done:
        s.phase = "gate2"; st.rerun()

    ph_name, ph_wks, ph_qs = phase_label()
    st.markdown(f"""<div class="main-header">
    <h1>Week {s.week} — {ph_name}</h1>
    <p>{ph_qs} &nbsp;·&nbsp; {s.scenario}</p>
    </div>""", unsafe_allow_html=True)

    if s.event_log:
        for e in s.event_log:
            st.markdown(f'<div class="event-box"><h4>Event</h4>{e}</div>', unsafe_allow_html=True)

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric("Deliverables", f"{round(s.tasks_completed)}", f"/ {s.tasks_required}")
    m2.metric("Fees Spent",   f"£{round(s.cost_spent):,}",  f"/ £{BUDGET:,}")
    m3.metric("Morale",       f"{round(s.morale)}/100")
    m4.metric("Stress",       f"{round(s.stress)}/100")
    m5.metric("Quality",      f"{round(s.quality)}/100")
    m6.metric("Rework",       f"{round(s.defects,1)}")

    if len(s.history) >= 2:
        avg_out = sum(h["net"] for h in s.history[-3:]) / min(3, len(s.history))
        left = max(0, s.tasks_required - s.tasks_completed)
        est  = s.week + (left/avg_out if avg_out > 0 else 99)
        st.caption(f"At current pace: completion by **Week {round(est)}** (target: Week {s.schedule_target})")

    st.divider()
    st.markdown("### This Week\'s Decisions")

    frozen = s.hiring_freeze > 0
    if frozen:
        st.warning(f"Hiring freeze — {s.hiring_freeze} week(s) remaining. Team size locked.")
        team = s.team_size
        s.hiring_freeze = max(0, s.hiring_freeze - 1)
    else:
        team = st.slider("Consultants on project", 2, 8, s.team_size)

    ca,cb = st.columns(2)
    with ca:
        skill = st.selectbox("Grade", list(SKILL_MULT.keys()),
            index=list(SKILL_MULT.keys()).index(s.skill))
        overtime = st.selectbox("Overtime", ["None","Allowed","Heavy"])
        pilot    = st.checkbox(f"Run a pilot analysis (+£{PILOT_COST:,} — validates direction early, reduces rework risk)")
    with cb:
        outsourcing = st.selectbox("Sub-contract research", ["None","Selective","Full"])
        meetings    = st.selectbox("Client meetings", ["Light","Balanced","Intensive"])
        st.selectbox("Risk response", ["Ignore","Monitor","Actively mitigate"])

    prev_out = (team * SKILL_MULT[skill] * 6 * (s.morale/100) *
                max(0.45, 1-s.stress/140) * (s.coordination/100) *
                (1+OUT_CAP[outsourcing]) * (1+OT_CAP[overtime]) * (1-MTG_PROD[meetings]))
    est_cost = team * WEEKLY_COST[skill] + OUT_COST[outsourcing] + (PILOT_COST if pilot else 0)
    budget_left = max(0, BUDGET - s.cost_spent)
    st.info(f"Est. deliverables this week: **~{round(prev_out)}**  |  Est. fees: **£{est_cost:,}**  |  Budget remaining: **£{round(budget_left):,}**")

    st.divider()
    if st.button(f"Run Week {s.week}", use_container_width=True, type="primary"):
        res = compute_week(team, skill, outsourcing, overtime, meetings, pilot)
        s.history.append(res)
        s.team_size = team; s.skill = skill
        s.week += 1
        done   = s.tasks_completed >= s.tasks_required
        timeup = s.week > s.max_weeks
        if done or timeup:
            s.final_score = calc_final_score(); s.phase = "recommendation"
        st.rerun()

# ── EVENT: Scope Creep ────────────────────────────────────────────────────────
elif s.phase == "event":
    st.markdown("""<div class="main-header">
    <h1>Client Change Request</h1>
    <p>Areej is on the phone...</p></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="event-box">
    <h4>Week 5 — Scope Change Request</h4>
    <p>Areej has been talking to a contact at a Latin American trade body. She now wants the
    engagement extended to include <strong>Latin American export markets</strong> and an assessment
    of <strong>sustainability certification options</strong> (Fairtrade, Rainforest Alliance).</p>
    <p><em>"I know it wasn\'t in the original brief, but I\'m paying for the best advice and I need
    to make sure I\'m not missing an opportunity."</em></p>
    <p>This is classic scope creep. How do you respond?</p></div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**Accept in Full**\n- +25 deliverables\n- Morale −5 (team overload)\n- Covers Latin America + certification\n- Serious schedule risk")
        if st.button("Accept Full Scope", use_container_width=True):
            apply_event("scope_creep","full"); s.pending_event=None; s.phase="playing"; st.rerun()
    with c2:
        st.markdown("**Accept Partially**\n- +12 deliverables\n- Latin America only\n- Manageable impact\n- Areej accepts compromise")
        if st.button("Accept Partial", use_container_width=True):
            apply_event("scope_creep","partial"); s.pending_event=None; s.phase="playing"; st.rerun()
    with c3:
        st.markdown("**Hold the Brief**\n- No additional deliverables\n- Original scope protected\n- Client relationship risk\n- Professionally justified")
        if st.button("Hold the Brief", use_container_width=True):
            apply_event("scope_creep","reject"); s.pending_event=None; s.phase="playing"; st.rerun()

# ── GATE 1: Mid-Point Review (after Week 3) ───────────────────────────────────
elif s.phase == "gate1":
    st.markdown("""<div class="main-header">
    <h1>Phase Gate 1 — Mid-Point Review</h1>
    <p>End of Phase 1: Import Analysis complete</p></div>""", unsafe_allow_html=True)

    p1q = round(s.phase1_quality_sum / max(1, s.phase1_weeks))
    colour = "#76b72a" if p1q >= 75 else "#edab00" if p1q >= 60 else "#dc3545"
    if p1q >= 75:
        heather_msg = "<p>Areej is impressed: 'The import options analysis is thorough and I can see the financial implications clearly. Good foundation for the export work.'</p>"
    elif p1q >= 60:
        heather_msg = "<p>Areej is cautious: 'The import analysis is okay but I wanted more detail on the direct-source pricing. We need to be sharper in Phase 2.'</p>"
    else:
        heather_msg = "<p>Areej is concerned: 'I am not confident in this import analysis. The financials are vague. Please make sure the export work is more rigorous — Phase 3 projections depend on getting the cost-per-box right.'</p>"
    st.markdown(f"""<div class="gate-box">
    <h4>Areej's Week 3 Check-In</h4>
    <p>Your Phase 1 average analysis quality: <strong style="color:{colour};">{p1q}/100</strong></p>
    {heather_msg}
    <p><small><b>Note:</b> Phase 1 quality below 68/100 applies a 10-point quality penalty in Phase 3 — the export financial projections depend on the import cost assumptions established now.</small></p>
    </div>""", unsafe_allow_html=True)

    st.info("**Critical path reminder:** Q5 & Q6 (entry mode + financial projections) cannot be finalised until Q1 & Q2 (import costs) are solid. Rushing Phase 1 creates rework in Phase 3.")
    if st.button("Continue to Phase 2 — Export Research", use_container_width=True, type="primary"):
        s.gate1_done = True; s.phase = "playing"; st.rerun()

# ── GATE 2: Pre-Synthesis Check (after Week 6) ───────────────────────────────
elif s.phase == "gate2":
    st.markdown("""<div class="main-header">
    <h1>Phase Gate 2 — Pre-Synthesis Check</h1>
    <p>End of Phase 2: Export research complete</p></div>""", unsafe_allow_html=True)

    p2q = round(s.phase2_quality_sum / max(1, s.phase2_weeks))
    p1q = round(s.phase1_quality_sum / max(1, s.phase1_weeks))
    avg_q = (p1q + p2q) / 2
    if avg_q >= 72:
        found_msg = "<p style='color:#76b72a;'><b>Strong foundations.</b> Your analysis to date supports confident recommendations.</p>"
    elif avg_q >= 58:
        found_msg = "<p style='color:#edab00;'><b>Mixed quality.</b> Be precise in Phase 3 — build on your best work from Phases 1 and 2.</p>"
    else:
        found_msg = "<p style='color:#dc3545;'><b>Weak foundations.</b> Phase 3 synthesis will carry forward quality gaps. The 10-point penalty is active.</p>"
    budget_left = round(BUDGET - s.cost_spent)
    st.markdown(f"""<div class="gate-box">
    <h4>Before You Write the Strategy Report</h4>
    <p>Phase 1 avg quality: <strong>{p1q}/100</strong> &nbsp;|&nbsp; Phase 2 avg quality: <strong>{p2q}/100</strong></p>
    <p>You are about to enter Phase 3 — synthesising your import and export findings into
    Areej's strategy report and financial projections. This is where critical path matters most.</p>
    {found_msg}
    <p>Budget remaining: <strong>£{budget_left:,}</strong> of £{BUDGET:,}</p>
    </div>""", unsafe_allow_html=True)

    if st.button("Enter Phase 3 — Strategy Synthesis", use_container_width=True, type="primary"):
        s.gate2_done = True; s.phase = "playing"; st.rerun()

# ── RECOMMENDATION ────────────────────────────────────────────────────────────
elif s.phase == "recommendation":
    sc = s.final_score
    st.markdown(f"""<div class="main-header">
    <h1>Present to the Client</h1>
    <p>Week {s.week-1} — Areej\'s board meeting is tomorrow</p></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="brief-box">
    <h3>Your Strategic Recommendations</h3>
    <p>Before you see your PM score, make your four strategic recommendations to Areej.
    These are the substantive answers her board is waiting for.
    After you submit, you\'ll see how well they align with what Areej told you in the interview.</p>
    </div>""", unsafe_allow_html=True)

    answers = {}
    for key, rec in RECS.items():
        q_text = rec["q"]
        st.markdown(f"**{q_text}**")
        answers[key] = st.radio("", rec["opts"], key=f"rec_{key}", label_visibility="collapsed")

    if st.button("Submit Recommendations to Areej", use_container_width=True, type="primary"):
        bonus = 0
        for key, rec in RECS.items():
            chosen_idx = rec["opts"].index(answers[key])
            if chosen_idx == rec["best"]: bonus += 25
            elif abs(chosen_idx - rec["best"]) == 1: bonus += 12
        s.rec_answers = {k: RECS[k]["opts"].index(v) for k,v in answers.items()}
        s.rec_score   = bonus
        s.phase = "complete"; st.rerun()

# ── COMPLETE ──────────────────────────────────────────────────────────────────
elif s.phase == "complete":
    sc = s.final_score
    total_with_bonus = min(1000, sc["total"] + s.rec_score)
    grade = ("Outstanding" if total_with_bonus>=875 else "Strong" if total_with_bonus>=725
             else "Adequate" if total_with_bonus>=575 else "Marginal" if total_with_bonus>=425
             else "Struggling")

    st.markdown(f"""<div class="main-header">
    <h1>Engagement Complete</h1>
    <p>Week {s.week-1} &nbsp;·&nbsp; {s.scenario}</p></div>""", unsafe_allow_html=True)

    # PM Score
    ca,cb = st.columns(2)
    with ca:
        st.markdown(f"""<div class="score-box">
        <div style="font-size:.9rem;opacity:.8;">PM Score</div>
        <div class="total">{sc["total"]}</div>
        <div style="font-size:.85rem;opacity:.7;">+ {s.rec_score} pts strategy alignment</div>
        <div style="font-size:1.5rem;margin-top:.4rem;">= {total_with_bonus} / 1000</div>
        <div style="font-size:1.2rem;margin-top:.3rem;">{grade}</div>
        </div>""", unsafe_allow_html=True)

    with cb:
        df = pd.DataFrame({
            "Component":["Deliverable Completeness","On-Time Delivery","Budget Control","Analysis Quality","Team & Client Health"],
            "Score":[sc["scope"],sc["schedule"],sc["cost"],sc["quality"],sc["team"]],
            "Max":[250,250,200,150,150],
        })
        fig = go.Figure(go.Bar(
            x=df["Score"], y=df["Component"], orientation="h",
            marker_color=["#006938","#008996","#edab00","#76b72a","#9b59b6"],
            text=[f"{s}/{m}" for s,m in zip(df["Score"],df["Max"])],
            textposition="outside",
        ))
        fig.update_layout(height=270, margin=dict(l=10,r=50,t=10,b=10),
            xaxis=dict(range=[0,270],showgrid=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Strategic recommendation reveal
    st.divider()
    st.markdown("### Areej\'s Verdict on Your Recommendations")
    for key, rec in RECS.items():
        chosen_idx = s.rec_answers.get(key, -1)
        is_best    = chosen_idx == rec["best"]
        is_close   = abs(chosen_idx - rec["best"]) == 1
        box_cls    = "rec-correct" if is_best else "rec-partial" if is_close else "event-box"
        icon       = "✅" if is_best else "🟡" if is_close else "❌"
        your_ans   = rec["opts"][chosen_idx] if chosen_idx >= 0 else "—"
        best_ans   = rec["opts"][rec["best"]]
        pref_line = "" if is_best else f"<em>Areej's preference:</em> {best_ans}<br>"
        st.markdown(f"""<div class="{box_cls}">
        <b>{rec["q"]}</b><br>
        {icon} <em>Your answer:</em> {your_ans}<br>
        {pref_line}
        <small>{rec["why"]}</small>
        </div>""", unsafe_allow_html=True)

    # Charts
    st.divider()
    st.markdown("### Engagement History")
    if s.history:
        hdf = pd.DataFrame(s.history)
        t1,t2,t3 = st.tabs(["Output & Rework","People Metrics","Fee Burn"])
        with t1:
            f1 = go.Figure()
            f1.add_trace(go.Bar(x=hdf["week"],y=hdf["net"],name="Net Deliverables",marker_color="#006938"))
            f1.add_trace(go.Bar(x=hdf["week"],y=hdf["rework"],name="Rework",marker_color="#dc3545"))
            f1.update_layout(barmode="stack",height=280,xaxis_title="Week",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(f1, use_container_width=True)
        with t2:
            f2 = go.Figure()
            f2.add_trace(go.Scatter(x=hdf["week"],y=hdf["morale"],name="Morale",line=dict(color="#76b72a",width=2)))
            f2.add_trace(go.Scatter(x=hdf["week"],y=hdf["stress"],name="Stress",line=dict(color="#dc3545",width=2)))
            f2.add_trace(go.Scatter(x=hdf["week"],y=hdf["quality"],name="Quality",line=dict(color="#edab00",width=2,dash="dot")))
            f2.update_layout(height=280,xaxis_title="Week",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(f2, use_container_width=True)
        with t3:
            cumcost = hdf["cost"].cumsum()
            f3 = go.Figure()
            f3.add_trace(go.Scatter(x=hdf["week"],y=cumcost,fill="tozeroy",name="Cumulative Fees",line=dict(color="#006938")))
            f3.add_hline(y=BUDGET,line_dash="dash",line_color="red",annotation_text=f"Budget £{BUDGET:,}")
            f3.update_layout(height=280,xaxis_title="Week",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(f3, use_container_width=True)

    if s.event_log:
        st.markdown("### Events That Hit Your Engagement")
        for e in s.event_log:
            st.markdown(f'<div class="event-box">{e}</div>', unsafe_allow_html=True)

    if s.history:
        st.markdown("### Decision Log")
        disp = pd.DataFrame(s.history).rename(columns={
            "week":"Week","team":"Team","skill":"Grade","outsourcing":"Sub-contract",
            "overtime":"OT","meetings":"Meetings","pilot":"Pilot",
            "net":"Net","rework":"Rework","quality":"Quality","morale":"Morale","stress":"Stress","cost":"Fees"})
        st.dataframe(disp[["Week","Team","Grade","Sub-contract","OT","Meetings","Pilot","Net","Rework","Quality","Morale","Stress","Fees"]],
            use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Reflection Prompts")
    for p in [
        "Brooks\'s Law: did adding or losing people help or hurt? When did coordination costs outweigh capacity gains?",
        "The overtime paradox: did authorising overtime produce more net deliverables or just more rework?",
        "Critical path: did the quality of your Phase 1 (import analysis) affect your Phase 3 (synthesis)? How?",
        "Scope management: when Areej asked for more, what criteria should determine the answer in real consultancy?",
        "Pilot analysis: did early validation reduce your rework? When is it worth the cost and when is it not?",
        "Budget: with only £32,000 available, what was your biggest trade-off between team size, grade, and time?",
        "What would you recommend differently to Areej now compared to Week 1? What changed your view?",
        "How would you present these findings differently if Areej were risk-averse vs. growth-hungry?",
    ]:
        st.markdown(f'<div class="reflection-box">💬 {p}</div>', unsafe_allow_html=True)

    st.divider()
    ca,cb = st.columns(2)
    with ca:
        if st.button("Run Another Engagement", use_container_width=True, type="primary"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    with cb:
        if st.button("Try a Different Scenario", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 1rem;'>
  <p style='color:#006938;font-size:0.85rem;font-family:DM Sans,Calibri,sans-serif;'>
    <strong style='color:#005734;'>The Areej Tea Company Brief</strong>
    &middot; MSc Project Management Simulation
    &middot; Designed by <strong>Areej Riaz</strong> &middot; University of Stirling
  </p>
</div>""", unsafe_allow_html=True)
