"""
Project Rescue: Managing Scope, Resources and Schedule Under Pressure
A Streamlit-based project management simulation for MSc-level teaching.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project Rescue Simulation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { font-size: 2rem; margin: 0; font-weight: 700; }
    .main-header p  { font-size: 1rem; margin: 0.3rem 0 0; opacity: 0.85; }

    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #2d6a9f;
        margin-bottom: 0.8rem;
    }
    .metric-card .label { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; }
    .metric-card .delta { font-size: 0.8rem; margin-top: 2px; }

    .event-box {
        background: #fff3cd;
        border-left: 5px solid #f5a623;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
    }
    .event-box h4 { margin: 0 0 0.4rem; color: #7a5500; }

    .score-box {
        background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 100%);
        color: white;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .score-box .total { font-size: 4rem; font-weight: 800; }
    .score-box .label { font-size: 1rem; opacity: 0.85; }

    .brief-box {
        background: #f0f7ff;
        border: 1px solid #b3d4f0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .reflection-box {
        background: #f0fff4;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
SKILL_MULT = {"Junior": 0.80, "Mixed": 1.00, "Expert": 1.25}
WEEKLY_COST = {"Junior": 900, "Mixed": 1200, "Expert": 1600}
OUTSOURCE_CAP  = {"None": 0.00, "Selective": 0.20, "Heavy": 0.40}
OUTSOURCE_COST = {"None": 0,    "Selective": 3000, "Heavy": 6000}
OUTSOURCE_COORD= {"None": 0,    "Selective": 5,    "Heavy": 12}
MTG_COORD  = {"Light": -5, "Balanced": 8, "Intensive": 12}
MTG_PROD   = {"Light": 0,  "Balanced": 0.03, "Intensive": 0.12}
MTG_MORALE = {"Light": -2, "Balanced": 3,  "Intensive": -5}
OT_CAP     = {"None": 0.00, "Allowed": 0.10, "Heavy": 0.22}
OT_STRESS  = {"None": 0,    "Allowed": 6,    "Heavy": 14}
OT_MORALE  = {"None": 0,    "Allowed": -3,   "Heavy": -9}
SCOPE_TASKS = {"Basic": 60, "Standard": 90, "Advanced": 120, "Ambitious": 150}

SCENARIOS = {
    "Scenario 1 – Balanced Base Case": {
        "desc": "A standard project with all the usual tensions. Scope, schedule, cost, quality and morale all matter. No major shocks — yet.",
        "focus": "Core PM trade-offs",
        "events": {},
    },
    "Scenario 2 – Staffing Shock": {
        "desc": "Mid-project, two team members are reassigned to another urgent university initiative. Hiring is frozen for two weeks.",
        "focus": "People, morale, productivity",
        "events": {4: "staffing_shock"},
    },
    "Scenario 3 – Deadline Compression": {
        "desc": "Senior leadership moves the launch date forward by one week for a high-profile stakeholder event.",
        "focus": "Schedule pressure",
        "events": {4: "deadline_compress"},
    },
    "Scenario 4 – Scope Creep": {
        "desc": "Student services request significant new reporting features not in the original brief.",
        "focus": "Uncontrolled change",
        "events": {5: "scope_creep"},
    },
    "Scenario 5 – High Uncertainty": {
        "desc": "User needs shift, a technical integration fails mid-project, and a reporting requirement changes late. Prototyping pays off here.",
        "focus": "Prototyping & adaptation",
        "events": {3: "unclear_needs", 5: "tech_failure", 7: "req_change"},
    },
}

# ─── Session State Init ───────────────────────────────────────────────────────
def init_state():
    defaults = dict(
        phase="welcome",           # welcome | setup | playing | event | complete
        scenario=None,
        week=1,
        max_weeks=10,
        budget=60000,
        cost_spent=0.0,
        morale=75.0,
        stress=30.0,
        quality=80.0,
        coordination=60.0,
        tasks_completed=0.0,
        defects=0.0,
        tasks_required=90,
        scope="Standard",
        schedule_target=8,
        team_size=6,
        skill="Mixed",
        prototype_count=0,
        history=[],
        pending_event=None,
        scope_creep_choice=None,
        schedule_weight=100,
        hiring_freeze=0,
        event_log=[],
        final_score=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

# ─── Helper Functions ─────────────────────────────────────────────────────────
def gauge_color(val, low=40, high=70):
    if val >= high: return "#28a745"
    if val >= low:  return "#f5a623"
    return "#dc3545"

def stress_color(val):
    if val <= 40: return "#28a745"
    if val <= 65: return "#f5a623"
    return "#dc3545"

def compute_week(team_size, skill, outsourcing, overtime, meetings, prototype_this_week):
    """Run one week of simulation and update session state."""
    # Productivity
    base_cap     = team_size * SKILL_MULT[skill] * 6
    morale_f     = s.morale / 100
    stress_f     = max(0.45, 1 - s.stress / 140)
    coord_f      = s.coordination / 100
    outsource_f  = 1 + OUTSOURCE_CAP[outsourcing]
    overtime_f   = 1 + OT_CAP[overtime]
    mtg_penalty  = 1 - MTG_PROD[meetings]
    weekly_output = base_cap * morale_f * stress_f * coord_f * outsource_f * overtime_f * mtg_penalty

    # Quality & rework
    q = 85
    if skill == "Expert": q += 5
    if skill == "Junior": q -= 7
    q -= s.stress * 0.20
    if prototype_this_week: q += 6
    q += s.coordination * 0.05
    if overtime == "Heavy": q -= 8
    q = min(100, max(0, q))

    rework = weekly_output * max(0, (75 - q)) / 100
    net = max(0, weekly_output - rework)

    # Costs
    weekly_cost = (team_size * WEEKLY_COST[skill]
                   + OUTSOURCE_COST[outsourcing]
                   + (2500 if prototype_this_week else 0))

    # Stress update
    remaining_tasks = max(0, s.tasks_required - s.tasks_completed)
    remaining_weeks = max(1, s.schedule_target - s.week + 1)
    dl_pressure = (remaining_tasks / remaining_weeks) / 15
    new_stress = s.stress + dl_pressure + OT_STRESS[overtime]
    new_stress += max(0, team_size - 8) * 1.5
    if meetings == "Balanced": new_stress -= 3
    new_stress = min(100, max(0, new_stress))

    # Morale update
    new_morale = s.morale + MTG_MORALE[meetings] + OT_MORALE[overtime]
    new_morale -= max(0, new_stress - 65) * 0.08
    new_morale += 2 if net >= 10 else -2
    new_morale = min(100, max(0, new_morale))

    # Coordination update
    new_coord = s.coordination + MTG_COORD[meetings]
    new_coord -= OUTSOURCE_COORD[outsourcing]
    new_coord -= max(0, team_size - 7) * 2
    if prototype_this_week: new_coord += 5
    new_coord = min(100, max(0, new_coord))

    # Commit to state
    s.tasks_completed += net
    s.defects         += rework
    s.cost_spent      += weekly_cost
    s.morale           = new_morale
    s.stress           = new_stress
    s.quality          = q
    s.coordination     = new_coord
    if prototype_this_week:
        s.prototype_count += 1

    return dict(
        week=s.week, net=round(net, 1), rework=round(rework, 1),
        cost=round(weekly_cost), quality=round(q, 1),
        morale=round(new_morale, 1), stress=round(new_stress, 1),
        team=team_size, skill=skill, outsourcing=outsourcing,
        overtime=overtime, meetings=meetings, prototype=prototype_this_week,
    )

def calc_final_score():
    tasks_req = s.tasks_required
    tasks_done = s.tasks_completed
    scope_score    = min(250, 250 * tasks_done / tasks_req)
    delay          = max(0, s.week - 1 - s.schedule_target)
    schedule_score = 250 if (tasks_done >= tasks_req and s.week - 1 <= s.schedule_target) \
                     else max(0, 250 - delay * 50)
    cost_score     = max(0, 200 * (1 - max(0, s.cost_spent - s.budget) / s.budget))
    quality_score  = 150 * s.quality / 100
    team_score     = 150 * ((s.morale / 100) * 0.6 + ((100 - s.stress) / 100) * 0.4)
    total          = scope_score + schedule_score + cost_score + quality_score + team_score
    return dict(
        scope=round(scope_score), schedule=round(schedule_score),
        cost=round(cost_score), quality=round(quality_score),
        team=round(team_score), total=round(total),
    )

def apply_event(event_key, choice=None):
    """Apply scenario event effects to session state."""
    if event_key == "staffing_shock":
        s.team_size_post_shock = max(3, s.team_size_snapshot - 2)
        s.morale   = max(0, s.morale - 8)
        s.stress   = min(100, s.stress + 10)
        s.hiring_freeze = 2
        s.event_log.append("⚡ Week 4: Two team members reassigned. Hiring frozen for 2 weeks.")

    elif event_key == "deadline_compress":
        s.schedule_target = max(s.week, s.schedule_target - 1)
        s.stress = min(100, s.stress + 12)
        s.schedule_weight = 180
        s.event_log.append("⚡ Week 4: Deadline brought forward by 1 week.")

    elif event_key == "scope_creep":
        if choice == "full":
            s.tasks_required += 25
            s.morale = max(0, s.morale - 5)
            s.event_log.append("⚡ Week 5: Full scope change accepted (+25 tasks).")
        elif choice == "partial":
            s.tasks_required += 12
            s.event_log.append("⚡ Week 5: Partial scope change accepted (+12 tasks).")
        else:
            s.event_log.append("⚡ Week 5: Scope change rejected.")

    elif event_key == "unclear_needs":
        penalty = 0.5 if s.prototype_count >= 1 else 1.0
        tasks_lost = 8 * penalty
        s.tasks_completed = max(0, s.tasks_completed - tasks_lost)
        s.event_log.append(f"⚡ Week 3: Unclear user needs caused rework ({round(tasks_lost)} tasks lost).")

    elif event_key == "tech_failure":
        penalty = 0.5 if s.prototype_count >= 2 else 1.0
        tasks_lost = 12 * penalty
        s.tasks_completed = max(0, s.tasks_completed - tasks_lost)
        s.stress = min(100, s.stress + 8)
        s.event_log.append(f"⚡ Week 5: Technical integration failure ({round(tasks_lost)} tasks lost).")

    elif event_key == "req_change":
        penalty = 0.5 if s.prototype_count >= 2 else 1.0
        tasks_lost = 10 * penalty
        s.tasks_completed = max(0, s.tasks_completed - tasks_lost)
        s.event_log.append(f"⚡ Week 7: Reporting requirement changed ({round(tasks_lost)} tasks lost).")

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/project-management.png", width=60)
    st.markdown("## 🎯 Project Rescue")
    st.caption("MSc Project Management Simulation")
    st.divider()
    if s.phase not in ("welcome", "setup"):
        prog = min(1.0, s.tasks_completed / max(1, s.tasks_required))
        st.markdown("**📊 Progress**")
        st.progress(prog)
        st.caption(f"{round(s.tasks_completed)} / {s.tasks_required} tasks ({round(prog*100)}%)")
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("💰 Budget", f"£{s.budget:,}", f"-£{round(s.cost_spent):,}")
        col2.metric("📅 Week", f"{s.week}", f"of {s.max_weeks}")
        st.divider()
        st.markdown(f"**😊 Morale:** {round(s.morale)}/100")
        st.progress(s.morale / 100)
        st.markdown(f"**😰 Stress:** {round(s.stress)}/100")
        st.progress(s.stress / 100)
        st.divider()

    if st.button("🔄 Restart Simulation", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ─── PHASE: Welcome ───────────────────────────────────────────────────────────
if s.phase == "welcome":
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Project Rescue</h1>
        <p>Managing Scope, Resources and Schedule Under Pressure</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="brief-box">
        <h3>📋 Your Mission</h3>
        <p>You are the <strong>Project Manager</strong> for a <em>Sustainable Student Support App</em> at a university business school. Senior leadership wants it ready before the new semester.</p>
        <p>The app must help students access academic support, employability resources, wellbeing guidance, and sustainability activities.</p>
        <p>You will make weekly decisions about:</p>
        <ul>
        <li>🧑‍💻 Team size, skill level, and outsourcing</li>
        <li>⏰ Overtime and meeting frequency</li>
        <li>🧪 Whether to build a prototype</li>
        <li>🛡️ How to respond to risks and surprises</li>
        </ul>
        <p><strong>Budget:</strong> £60,000 &nbsp;|&nbsp; <strong>Duration:</strong> up to 10 weeks</p>
        <p>Your goal is not just to finish — it is to <strong>deliver quality while managing people, cost, and uncertainty.</strong></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 👥 Team Roles")
        roles = {
            "🎯 Project Manager": "Final decision-maker. Owns the outcome.",
            "💰 Finance Lead": "Monitors budget, cost, and outsourcing.",
            "❤️ People Lead": "Tracks morale, stress, and overtime.",
            "📦 Delivery Lead": "Manages scope, schedule, quality, and prototypes.",
        }
        for role, desc in roles.items():
            st.markdown(f"**{role}** — {desc}")

        st.divider()
        if st.button("▶️ Begin Simulation", use_container_width=True, type="primary"):
            s.phase = "setup"
            st.rerun()

# ─── PHASE: Setup ─────────────────────────────────────────────────────────────
elif s.phase == "setup":
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Setup Your Project</h1>
        <p>Choose your scenario and build your starting plan</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎭 Choose a Scenario")
        scenario_name = st.radio(
            "Select your scenario:",
            list(SCENARIOS.keys()),
            label_visibility="collapsed",
        )
        sc = SCENARIOS[scenario_name]
        st.markdown(f"""
        <div class="brief-box">
        <b>Teaching focus:</b> {sc['focus']}<br><br>
        {sc['desc']}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📐 Initial Plan")
        scope = st.selectbox(
            "Scope ambition",
            ["Basic", "Standard", "Advanced", "Ambitious"],
            index=1,
            help="Basic=60 tasks | Standard=90 | Advanced=120 | Ambitious=150",
        )
        tasks_req = SCOPE_TASKS[scope]
        st.caption(f"→ Requires completing **{tasks_req} tasks**")

        schedule = st.slider("Schedule target (weeks)", 6, 9, 8)
        team = st.slider("Initial team size", 3, 12, 6)
        skill = st.selectbox("Team skill level", ["Junior", "Mixed", "Expert"], index=1)
        st.caption(f"→ Cost per person/week: £{WEEKLY_COST[skill]:,}")

    st.divider()
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.info(f"📊 Estimated min. cost at {team} × {skill}: "
                f"**£{team * WEEKLY_COST[skill] * schedule:,}** over {schedule} weeks "
                f"(before outsourcing/overtime/prototypes)")
    with col_r:
        if st.button("🚀 Launch Project", use_container_width=True, type="primary"):
            s.scenario       = scenario_name
            s.scope          = scope
            s.tasks_required = tasks_req
            s.schedule_target = schedule
            s.team_size      = team
            s.skill          = skill
            s.phase          = "playing"
            st.rerun()

# ─── PHASE: Playing ───────────────────────────────────────────────────────────
elif s.phase == "playing":

    # Check for scenario events
    sc_events = SCENARIOS[s.scenario]["events"]
    if s.week in sc_events and s.pending_event is None:
        evt = sc_events[s.week]
        # Scope creep needs a choice — pause for it
        if evt == "scope_creep":
            s.pending_event = evt
            s.phase = "event"
            st.rerun()
        else:
            # snapshot team size for staffing shock
            if evt == "staffing_shock":
                s.team_size_snapshot = s.team_size
            apply_event(evt)
            if evt == "staffing_shock" and hasattr(s, "team_size_post_shock"):
                s.team_size = s.team_size_post_shock

    st.markdown(f"""
    <div class="main-header">
        <h1>📅 Week {s.week} Decisions</h1>
        <p>{s.scenario} — {SCENARIOS[s.scenario]['focus']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Event log
    if s.event_log:
        for e in s.event_log:
            st.markdown(f'<div class="event-box"><h4>🚨 Event</h4>{e}</div>', unsafe_allow_html=True)

    # Dashboard
    st.markdown("### 📊 Current Dashboard")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("✅ Tasks Done",  f"{round(s.tasks_completed)}", f"/ {s.tasks_required}")
    m2.metric("💰 Cost Spent", f"£{round(s.cost_spent):,}", f"/ £{s.budget:,}")
    m3.metric("😊 Morale",      f"{round(s.morale)}/100")
    m4.metric("😰 Stress",      f"{round(s.stress)}/100")
    m5.metric("🎯 Quality",     f"{round(s.quality)}/100")
    m6.metric("🔧 Defects",     f"{round(s.defects, 1)} tasks")

    # Estimated completion
    history = s.history
    if len(history) >= 2:
        recent_output = sum(h["net"] for h in history[-3:]) / min(3, len(history))
        tasks_left = max(0, s.tasks_required - s.tasks_completed)
        est_weeks = (tasks_left / recent_output) if recent_output > 0 else 99
        est_finish = s.week + est_weeks
        st.caption(f"🔮 At current pace, estimated completion: **Week {round(est_finish)}** "
                   f"(target: Week {s.schedule_target})")

    st.divider()

    # Weekly decision form
    st.markdown("### 🎮 This Week's Decisions")

    # If hiring freeze, cap team options
    frozen = s.hiring_freeze > 0
    if frozen:
        st.warning(f"🚫 Hiring freeze in effect for {s.hiring_freeze} more week(s). Team size is locked.")
        team_size = s.team_size
        s.hiring_freeze = max(0, s.hiring_freeze - 1)
    else:
        team_size = st.slider("Team size this week", 3, 12, s.team_size)

    col_a, col_b = st.columns(2)
    with col_a:
        skill     = st.selectbox("Skill level", ["Junior", "Mixed", "Expert"],
                                  index=["Junior", "Mixed", "Expert"].index(s.skill))
        overtime  = st.selectbox("Overtime policy", ["None", "Allowed", "Heavy"])
        prototype = st.checkbox("🧪 Build a prototype this week (+£2,500 cost)")
    with col_b:
        outsourcing = st.selectbox("Outsourcing", ["None", "Selective", "Heavy"])
        meetings    = st.selectbox("Meeting intensity", ["Light", "Balanced", "Intensive"])
        risk_resp   = st.selectbox("Risk response", ["Ignore", "Monitor", "Actively mitigate"])

    # Quick preview
    preview_base = team_size * SKILL_MULT[skill] * 6
    preview_out  = preview_base * (s.morale/100) * max(0.45, 1-s.stress/140) * \
                   (s.coordination/100) * (1+OUTSOURCE_CAP[outsourcing]) * \
                   (1+OT_CAP[overtime]) * (1-MTG_PROD[meetings])
    weekly_est_cost = team_size * WEEKLY_COST[skill] + OUTSOURCE_COST[outsourcing] + (2500 if prototype else 0)
    st.info(f"📐 Estimated output this week: **~{round(preview_out)} tasks** | "
            f"Estimated cost: **£{weekly_est_cost:,}**")

    st.divider()
    if st.button("▶️ Run Week " + str(s.week), use_container_width=True, type="primary"):
        result = compute_week(team_size, skill, outsourcing, overtime, meetings, prototype)
        s.history.append(result)
        s.team_size = team_size
        s.skill = skill
        s.week += 1

        # Check completion
        done = s.tasks_completed >= s.tasks_required
        time_up = s.week > s.max_weeks

        if done or time_up:
            s.final_score = calc_final_score()
            s.phase = "complete"
        st.rerun()

# ─── PHASE: Event (Scope Creep) ───────────────────────────────────────────────
elif s.phase == "event":
    st.markdown("""
    <div class="main-header">
        <h1>🚨 Surprise Event!</h1>
        <p>Your project just got more complicated...</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="event-box">
    <h4>📋 Scope Change Request — Week 5</h4>
    <p>Student Services has approached you with an urgent request: they want a <strong>comprehensive reporting dashboard</strong>
    showing engagement analytics, wellbeing trends, and employability outcomes. This was not in the original brief.</p>
    <p>Your sponsor says: <em>"This would really impress the Vice-Chancellor at the launch event."</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Your options:")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **✅ Accept in Full**
        - +25 additional tasks
        - Morale −5 (team overload)
        - Stakeholder score +20
        - Significant schedule risk
        """)
        if st.button("Accept Full Change", use_container_width=True):
            apply_event("scope_creep", choice="full")
            s.pending_event = None
            s.phase = "playing"
            st.rerun()

    with col2:
        st.markdown("""
        **🤝 Accept Partially**
        - +12 additional tasks
        - Manageable schedule impact
        - Stakeholder score +10
        - Compromise solution
        """)
        if st.button("Accept Partial Change", use_container_width=True):
            apply_event("scope_creep", choice="partial")
            s.pending_event = None
            s.phase = "playing"
            st.rerun()

    with col3:
        st.markdown("""
        **🚫 Reject Change**
        - No additional tasks
        - Protects schedule and budget
        - Stakeholder score −15
        - You hold the line
        """)
        if st.button("Reject Change", use_container_width=True):
            apply_event("scope_creep", choice="reject")
            s.pending_event = None
            s.phase = "playing"
            st.rerun()

# ─── PHASE: Complete ──────────────────────────────────────────────────────────
elif s.phase == "complete":
    sc = s.final_score
    grade = ("🏆 Outstanding" if sc["total"] >= 850 else
             "🥇 Strong" if sc["total"] >= 700 else
             "🥈 Adequate" if sc["total"] >= 550 else
             "🥉 Marginal" if sc["total"] >= 400 else
             "⚠️ Struggling")

    st.markdown(f"""
    <div class="main-header">
        <h1>🎯 Project Complete!</h1>
        <p>Week {s.week - 1} | {s.scenario}</p>
    </div>
    """, unsafe_allow_html=True)

    # Score display
    col_main, col_break = st.columns([1, 1])
    with col_main:
        st.markdown(f"""
        <div class="score-box">
        <div class="label">Final Score (out of 1000)</div>
        <div class="total">{sc['total']}</div>
        <div style="font-size:1.4rem; margin-top:0.5rem;">{grade}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_break:
        st.markdown("#### Score Breakdown")
        breakdown_df = pd.DataFrame({
            "Component": ["Scope Delivery", "Schedule", "Cost Control", "Quality", "Team Health"],
            "Score": [sc["scope"], sc["schedule"], sc["cost"], sc["quality"], sc["team"]],
            "Max": [250, 250, 200, 150, 150],
        })
        breakdown_df["Pct"] = (breakdown_df["Score"] / breakdown_df["Max"] * 100).round(0)
        fig = go.Figure(go.Bar(
            x=breakdown_df["Score"],
            y=breakdown_df["Component"],
            orientation="h",
            marker_color=["#2d6a9f", "#1b998b", "#f5a623", "#28a745", "#9b59b6"],
            text=[f"{s}/{m}" for s, m in zip(breakdown_df["Score"], breakdown_df["Max"])],
            textposition="outside",
        ))
        fig.update_layout(
            height=280, margin=dict(l=10, r=60, t=10, b=10),
            xaxis=dict(range=[0, 270], showgrid=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Charts
    st.divider()
    st.markdown("### 📈 Project History")
    if s.history:
        hist_df = pd.DataFrame(s.history)
        tab1, tab2, tab3 = st.tabs(["📦 Output & Rework", "😊 People Metrics", "💰 Cost"])

        with tab1:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=hist_df["week"], y=hist_df["net"],
                                   name="Net Tasks", marker_color="#2d6a9f"))
            fig1.add_trace(go.Bar(x=hist_df["week"], y=hist_df["rework"],
                                   name="Rework", marker_color="#dc3545"))
            fig1.update_layout(barmode="stack", height=300,
                                xaxis_title="Week", yaxis_title="Tasks",
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=hist_df["week"], y=hist_df["morale"],
                                       name="Morale", line=dict(color="#28a745", width=2)))
            fig2.add_trace(go.Scatter(x=hist_df["week"], y=hist_df["stress"],
                                       name="Stress", line=dict(color="#dc3545", width=2)))
            fig2.add_trace(go.Scatter(x=hist_df["week"], y=hist_df["quality"],
                                       name="Quality", line=dict(color="#f5a623", width=2,
                                                                  dash="dot")))
            fig2.update_layout(height=300, xaxis_title="Week", yaxis_title="Score (0-100)",
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            cumcost = hist_df["cost"].cumsum()
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=hist_df["week"], y=cumcost,
                                       name="Cumulative Cost", fill="tozeroy",
                                       line=dict(color="#2d6a9f")))
            fig3.add_hline(y=s.budget, line_dash="dash", line_color="red",
                           annotation_text="Budget £60,000")
            fig3.update_layout(height=300, xaxis_title="Week", yaxis_title="£ Spent",
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)

    # Event log
    if s.event_log:
        st.markdown("### 🚨 Events That Happened")
        for e in s.event_log:
            st.markdown(f'<div class="event-box">{e}</div>', unsafe_allow_html=True)

    # Weekly decision table
    st.markdown("### 📋 Decision History")
    if s.history:
        disp_df = pd.DataFrame(s.history)[
            ["week", "team", "skill", "outsourcing", "overtime", "meetings", "prototype",
             "net", "rework", "quality", "morale", "stress", "cost"]
        ].rename(columns={
            "week": "Week", "team": "Team", "skill": "Skill",
            "outsourcing": "Outsource", "overtime": "OT", "meetings": "Meetings",
            "prototype": "Proto", "net": "Net Tasks", "rework": "Rework",
            "quality": "Quality", "morale": "Morale", "stress": "Stress", "cost": "£ Cost",
        })
        st.dataframe(disp_df, use_container_width=True, hide_index=True)

    # Reflection prompts
    st.divider()
    st.markdown("### 💭 Reflection Prompts")
    prompts = [
        "Which single decision had the biggest negative impact on your score? Why?",
        "Did your overtime choices help or hurt? What were the hidden costs?",
        "How did morale and stress interact over time? What drove the changes?",
        "If you had to redo the project with the same scenario, what would you change first?",
        "What would you tell a real project manager about balancing scope and team health?",
        "Did your prototyping strategy (if any) pay off? When is prototyping worth the cost?",
        "What was the cost of the decisions you made in the first two weeks?",
        "How did your coordination score affect productivity? What moved it most?",
    ]
    for p in prompts:
        st.markdown(f'<div class="reflection-box">💬 {p}</div>', unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Play Another Round", use_container_width=True, type="primary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    with col_b:
        if st.button("🔀 Try a Different Scenario", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
