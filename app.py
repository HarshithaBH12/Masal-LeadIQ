import streamlit as st
from datetime import date, datetime
from uuid import uuid4

from ai_engine import analyze_lead, answer_lead_question
from lead_manager import load_leads, save_leads, upsert_lead, delete_lead, update_lead
from prompts import SAMPLE_LEADS

st.set_page_config(page_title="Masal LeadIQ", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#0b1020; --panel:#111a2e; --panel2:#151f36; --line:#26334d; --muted:#94a3b8; --text:#edf2ff; --accent:#8b9cff; --mint:#55d6be; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, #182447 0%, #0b1020 42%, #090e1b 100%); color:var(--text); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#0d1528; border-right:1px solid #26334d; }
[data-testid="stSidebar"] * { color:#dbe5fa; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; color:#f4f7ff; }
p, label, span, div { }
.small-muted { color:#94a3b8; font-size:.86rem; }
.hero { padding: 1.1rem 1.35rem; border:1px solid #2a3857; border-radius:18px; background:linear-gradient(120deg,rgba(31,46,82,.92),rgba(17,26,46,.9)); margin-bottom:1rem; }
.hero-kicker { color:#9eafff; text-transform:uppercase; letter-spacing:.13em; font-size:.72rem; font-weight:700; }
.hero-title { font-family:'Manrope',sans-serif; font-size:2rem; font-weight:800; color:#f5f7ff; margin:.15rem 0; }
.hero-sub { color:#aebbd3; font-size:.95rem; }
.metric { background:linear-gradient(145deg,#151f36,#10182b); border:1px solid #293752; border-radius:15px; padding:16px 18px; min-height:104px; }
.metric-label { color:#9aa9c2; font-size:.78rem; font-weight:600; }
.metric-value { font-family:'Manrope',sans-serif; color:#f5f7ff; font-size:1.8rem; font-weight:800; margin-top:4px; }
.metric-foot { color:#7183a4; font-size:.73rem; }
.panel { background:#111a2e; border:1px solid #263650; border-radius:16px; padding:17px; }
.lead-row { background:#111a2e; border:1px solid #263650; border-radius:13px; padding:13px 15px; margin-bottom:9px; }
.tag { display:inline-block; border-radius:99px; padding:4px 10px; font-size:.72rem; font-weight:700; }
.tag-hot { color:#ff9b9b; background:#4b202d; border:1px solid #743346; }
.tag-warm { color:#ffd28a; background:#49351c; border:1px solid #715329; }
.tag-cold { color:#9db6d8; background:#1d3550; border:1px solid #315273; }
.tag-neutral { color:#aab7cc; background:#202b40; border:1px solid #35445e; }
div.stButton > button { border-radius:10px; border:1px solid #465a84; background:#28385f; color:#f4f7ff; font-weight:650; }
div.stButton > button:hover { border-color:#9aa9ff; background:#344878; color:white; }
div[data-testid="stForm"] { background:#111a2e; border:1px solid #263650; padding:18px; border-radius:16px; }
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { background:#0d1629 !important; color:#edf2ff !important; border-color:#33435f !important; }
[data-testid="stMetric"] { background:#111a2e; border:1px solid #263650; padding:12px; border-radius:12px; }
hr { border-color:#263650; }
div[data-testid="stChatMessage"] { background:#111a2e; border:1px solid #263650; border-radius:13px; }
.stAlert { border-radius:12px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "Not specified"

def priority_class(priority):
    p = (priority or "Unscored").lower()
    return {"hot":"tag-hot", "warm":"tag-warm", "cold":"tag-cold"}.get(p, "tag-neutral")

def show_priority(priority):
    return f'<span class="tag {priority_class(priority)}">{(priority or "Not scored").upper()}</span>'

def lead_label(lead):
    analysis = lead.get("analysis") or {}
    priority = analysis.get("priority", "Unscored")
    score = analysis.get("lead_score")
    score_text = f" · {score}/100" if score is not None else ""
    return f'{lead.get("name","Unnamed lead")} · {priority}{score_text}'

if "leads" not in st.session_state:
    st.session_state.leads = load_leads()
if "active_lead_id" not in st.session_state:
    st.session_state.active_lead_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def persist():
    save_leads(st.session_state.leads)

def nav_button(label, page):
    if st.sidebar.button(label, use_container_width=True, type="primary" if st.session_state.get("page","Dashboard")==page else "secondary"):
        st.session_state.page = page
        st.rerun()

with st.sidebar:
    st.markdown("## ✦ Masal **LeadIQ**")
    st.caption("REAL ESTATE · LEAD INTELLIGENCE")
    st.markdown("---")
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    nav_button("◫  Overview", "Dashboard")
    nav_button("＋  Add a lead", "Add Lead")
    nav_button("◎  Lead workspace", "Workspace")
    st.markdown("---")
    analyzed = sum(1 for x in st.session_state.leads if x.get("analysis"))
    st.caption(f"{len(st.session_state.leads)} leads saved · {analyzed} analyzed")
    st.markdown('<div class="small-muted">Built for thoughtful, timely follow-up.</div>', unsafe_allow_html=True)

page = st.session_state.page

if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">Sales intelligence workspace</div>
      <div class="hero-title">See the signal in every enquiry.</div>
      <div class="hero-sub">Prioritize the right conversations, understand what buyers need, and move each opportunity forward.</div>
    </div>
    """, unsafe_allow_html=True)
    leads = st.session_state.leads
    analyzed_leads = [x for x in leads if x.get("analysis")]
    hot = [x for x in analyzed_leads if x["analysis"].get("priority") == "Hot"]
    warm = [x for x in analyzed_leads if x["analysis"].get("priority") == "Warm"]
    cold = [x for x in analyzed_leads if x["analysis"].get("priority") == "Cold"]
    cols = st.columns(4)
    metrics = [("TOTAL LEADS", len(leads), "Saved in this workspace"), ("HOT LEADS", len(hot), "High-priority opportunities"), ("WARM LEADS", len(warm), "Worth nurturing"), ("ANALYZED", len(analyzed_leads), "AI-reviewed enquiries")]
    for col, (label, value, foot) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.5, 1])
    with left:
        st.subheader("Priority queue")
        if not leads:
            st.info("Your lead queue is empty. Add your first enquiry to start building your pipeline.")
            if st.button("＋ Add your first lead"):
                st.session_state.page = "Add Lead"; st.rerun()
        else:
            order = {"Hot":0, "Warm":1, "Cold":2}
            sorted_leads = sorted(leads, key=lambda x: (0 if x.get("analysis") else 1, order.get((x.get("analysis") or {}).get("priority"), 3), -(x.get("analysis") or {}).get("lead_score", 0)))
            for lead in sorted_leads[:8]:
                a = lead.get("analysis") or {}
                score = a.get("lead_score")
                c1, c2 = st.columns([4,1])
                with c1:
                    st.markdown(f'**{lead.get("name","Unnamed")}** &nbsp; {show_priority(a.get("priority"))}', unsafe_allow_html=True)
                    st.caption(f'{lead.get("location","")} · {lead.get("property_requirement","")} · {money(lead.get("budget"))}')
                    st.caption(a.get("recommended_next_action", "Awaiting AI analysis") if a else "Not analyzed yet")
                with c2:
                    st.markdown(f'<div style="text-align:right;color:#aebcff;font-weight:800;font-size:1.15rem">{score if score is not None else "—"}</div><div style="text-align:right;color:#8191ae;font-size:.7rem">SCORE</div>', unsafe_allow_html=True)
                    if st.button("Open", key=f"open_{lead['id']}"):
                        st.session_state.active_lead_id = lead["id"]
                        st.session_state.page = "Workspace"; st.rerun()
                st.markdown("<hr>", unsafe_allow_html=True)
    with right:
        st.subheader("How to read the queue")
        st.markdown('<div class="panel"><span class="tag tag-hot">HOT</span><p>Strong buying signals and/or a near-term timeline. Contact promptly.</p><span class="tag tag-warm">WARM</span><p>Real interest, but needs clarification, nurturing or timing alignment.</p><span class="tag tag-cold">COLD</span><p>Early-stage, low-intent or missing key information. Keep the conversation open.</p></div>', unsafe_allow_html=True)
        st.caption("AI priority is a decision-support signal, not a guarantee of conversion. Salespeople should verify details with the customer.")
        if st.button("＋ Add a new lead", use_container_width=True):
            st.session_state.page = "Add Lead"; st.rerun()
        if st.button("Load sample enquiries", use_container_width=True):
            existing = {x.get("name") for x in st.session_state.leads}
            for sample in SAMPLE_LEADS:
                if sample["name"] not in existing:
                    st.session_state.leads.append({"id":str(uuid4()), **sample, "analysis":None, "created_at":datetime.now().isoformat(timespec="seconds"), "status":"New"})
            persist()
            st.success("Sample enquiries added. Analyze each one to generate real AI insights.")
            st.rerun()

elif page == "Add Lead":
    st.markdown('<div class="hero"><div class="hero-kicker">New opportunity</div><div class="hero-title">Capture a customer enquiry.</div><div class="hero-sub">Add the context your team has. LeadIQ will use it to prepare a practical next step.</div></div>', unsafe_allow_html=True)
    with st.form("lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer name *", placeholder="e.g. Aanya Rao")
            location = st.text_input("Preferred location *", placeholder="e.g. Whitefield, Bengaluru")
            property_requirement = st.selectbox("Property requirement *", ["Apartment", "Villa", "Plot", "Independent house", "Commercial", "Not sure yet"])
            budget = st.number_input("Budget (INR) *", min_value=0, value=7500000, step=500000, help="Enter the total budget in Indian rupees.")
        with c2:
            timeline = st.selectbox("Buying timeline *", ["Immediately / within 1 month", "1–3 months", "3–6 months", "6–12 months", "More than 12 months", "Just exploring"])
            contact_channel = st.selectbox("Enquiry source (optional)", ["Website", "Phone call", "WhatsApp", "Property portal", "Walk-in", "Referral", "Other"])
            st.caption("The customer message is especially useful for identifying intent and objections.")
        message = st.text_area("Customer message / chat transcript *", height=170, placeholder="Paste the customer's enquiry or summarize what they said...")
        submitted = st.form_submit_button("Save lead & run AI analysis", type="primary", use_container_width=True)
    if submitted:
        if not all([name.strip(), location.strip(), property_requirement, message.strip()]) or budget <= 0:
            st.error("Please complete the required fields and enter a budget greater than zero.")
        else:
            lead = {"id":str(uuid4()), "name":name.strip(), "location":location.strip(), "property_requirement":property_requirement, "budget":int(budget), "timeline":timeline, "message":message.strip(), "source":contact_channel, "status":"New", "created_at":datetime.now().isoformat(timespec="seconds"), "analysis":None}
            with st.spinner("Saving the enquiry and asking Grok to assess it..."):
                try:
                    lead["analysis"] = analyze_lead(lead)
                    lead["status"] = "AI reviewed"
                except Exception as e:
                    lead["analysis_error"] = str(e)
            st.session_state.leads = upsert_lead(st.session_state.leads, lead)
            persist()
            st.session_state.active_lead_id = lead["id"]
            st.session_state.page = "Workspace"
            if lead.get("analysis"):
                st.success("Lead saved and analyzed.")
            else:
                st.warning("Lead saved, but AI analysis could not run. Add your Grok API key in the setup instructions, then retry from the workspace.")
            st.rerun()

elif page == "Workspace":
    leads = st.session_state.leads
    if not leads:
        st.info("No leads yet. Add a customer enquiry to open the workspace.")
        if st.button("Add a lead"):
            st.session_state.page = "Add Lead"; st.rerun()
    else:
        ids = [x["id"] for x in leads]
        selected_default = st.session_state.active_lead_id if st.session_state.active_lead_id in ids else ids[0]
        selected_id = st.selectbox("Select a customer", ids, index=ids.index(selected_default), format_func=lambda x: lead_label(next(l for l in leads if l["id"] == x)))
        st.session_state.active_lead_id = selected_id
        lead = next(x for x in leads if x["id"] == selected_id)
        a = lead.get("analysis") or {}
        top1, top2 = st.columns([3,1])
        with top1:
            st.markdown(f'<div class="hero"><div class="hero-kicker">Lead workspace</div><div class="hero-title">{lead["name"]}</div><div class="hero-sub">{lead["location"]} · {lead["property_requirement"]} · {money(lead["budget"])}</div></div>', unsafe_allow_html=True)
        with top2:
            st.markdown(f'<div class="panel">{show_priority(a.get("priority"))}<div style="font-size:2.2rem;font-weight:800;margin-top:8px">{a.get("lead_score","—")}<span style="font-size:.9rem;color:#91a0bb"> / 100</span></div><div class="small-muted">AI lead score</div></div>', unsafe_allow_html=True)
        tabs = st.tabs(["AI overview", "Smart Call Companion", "Ask about this lead", "Lead details"])
        with tabs[0]:
            if not a:
                st.warning("This lead has not been analyzed yet. Run a live Grok analysis to generate its priority and recommendations.")
                if st.button("Analyze this lead with Grok", type="primary"):
                    with st.spinner("Grok is reviewing the enquiry..."):
                        try:
                            lead["analysis"] = analyze_lead(lead)
                            lead.pop("analysis_error", None)
                            lead["status"] = "AI reviewed"
                            update_lead(st.session_state.leads, lead); persist(); st.rerun()
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
            else:
                st.markdown(f"**Lead summary**\n\n{a.get('lead_summary','—')}")
                st.markdown("#### Customer intent")
                st.write(a.get("customer_intent","—"))
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("#### Key requirements")
                    for item in a.get("key_requirements",[]): st.markdown(f"- {item}")
                with c2:
                    st.markdown("#### Objections & concerns")
                    for item in a.get("objections_concerns",[]): st.markdown(f"- {item}")
                st.markdown("#### Recommended next action")
                st.success(a.get("recommended_next_action","—"))
                st.markdown("#### Suggested customer response")
                st.info(a.get("suggested_response","—"))
                st.caption(f"Confidence: {a.get('confidence','Not specified')} · Score rationale: {a.get('score_rationale','Not specified')}")
                if a.get("missing_information"):
                    st.caption("Information to clarify: " + " · ".join(a["missing_information"]))
        with tabs[1]:
            st.subheader("Go into the call prepared.")
            if not a:
                st.info("Analyze this lead first. The call plan is generated from the customer's actual context.")
            else:
                call = a.get("call_companion", {})
                st.markdown("#### Opening angle")
                st.write(call.get("opening_angle","—"))
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("#### Talking points")
                    for item in call.get("talking_points",[]): st.markdown(f"- {item}")
                with c2:
                    st.markdown("#### If they raise an objection")
                    for item in call.get("objection_responses",[]): st.markdown(f"- {item}")
                st.markdown("#### Suggested call outcome")
                st.info(call.get("desired_call_outcome","—"))
                st.markdown("#### Follow-up suggestion")
                st.write(call.get("follow_up_suggestion","—"))
                st.caption("Use this as preparation, not a script. Confirm property availability, pricing and commitments with your team.")
        with tabs[2]:
            st.subheader("Ask LeadIQ")
            st.caption("Answers are generated using this customer's saved details and AI analysis.")
            history = st.session_state.chat_history.setdefault(selected_id, [])
            for item in history:
                with st.chat_message(item["role"]):
                    st.markdown(item["content"])
            question = st.chat_input("Ask about this customer, their concerns or your next move...")
            if question:
                history.append({"role":"user","content":question})
                with st.chat_message("user"): st.markdown(question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking through this lead..."):
                        try:
                            answer = answer_lead_question(lead, question, history[:-1])
                            st.markdown(answer)
                            history.append({"role":"assistant","content":answer})
                        except Exception as e:
                            st.error(f"Could not get an answer: {e}")
        with tabs[3]:
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("#### Customer information")
                st.write(f"**Location:** {lead.get('location')}")
                st.write(f"**Property:** {lead.get('property_requirement')}")
                st.write(f"**Budget:** {money(lead.get('budget'))}")
                st.write(f"**Timeline:** {lead.get('timeline')}")
                st.write(f"**Source:** {lead.get('source','Not specified')}")
                st.write(f"**Added:** {lead.get('created_at','')}")
            with c2:
                st.markdown("#### Sales status")
                status = st.selectbox("Update status", ["New","AI reviewed","Contacted","Site visit planned","Negotiation","Won","Lost"], index=["New","AI reviewed","Contacted","Site visit planned","Negotiation","Won","Lost"].index(lead.get("status","New")) if lead.get("status") in ["New","AI reviewed","Contacted","Site visit planned","Negotiation","Won","Lost"] else 0, key=f"status_{selected_id}")
                if st.button("Save status"):
                    lead["status"] = status; update_lead(st.session_state.leads, lead); persist(); st.success("Status updated.")
                st.markdown("**Original customer message**")
                st.write(lead.get("message",""))
            st.markdown("---")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("Re-run AI analysis", use_container_width=True):
                    with st.spinner("Refreshing the lead assessment..."):
                        try:
                            lead["analysis"] = analyze_lead(lead); lead.pop("analysis_error",None); update_lead(st.session_state.leads,lead); persist(); st.success("Analysis refreshed."); st.rerun()
                        except Exception as e: st.error(f"Analysis failed: {e}")
            with c2:
                if st.button("Delete this lead", use_container_width=True):
                    st.session_state.leads = delete_lead(st.session_state.leads, selected_id); persist()
                    st.session_state.active_lead_id = None; st.session_state.chat_history.pop(selected_id,None)
                    st.success("Lead deleted."); st.rerun()

st.markdown("<div style='text-align:center;color:#63728d;font-size:.75rem;padding:22px 0 8px'>MASAL LEADIQ · AI-ASSISTED SALES WORKSPACE · VERIFY CUSTOMER DETAILS BEFORE MAKING COMMITMENTS</div>", unsafe_allow_html=True)
