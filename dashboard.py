import streamlit as st
from ai_med import executor
from datetime import datetime

# ==================================================
# 🔐 AUTH GUARD
# ==================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.warning("Please login to continue.")
    st.switch_page("pages/login.py")

# init past cases
if "past_cases" not in st.session_state:
    st.session_state.past_cases = []

# ==================================================
# 📄 PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="CareRoute Dashboard 📊",
    page_icon="🏥",
    layout="wide"
)

# ==================================================
# 📌 SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:
    nav = st.radio(
        "Navigation",
        ["🚨 Emergency", "🏥 AI Triage", "📄 Report Analyzer", "👤 My Profile"]
    )

    st.markdown("---")

    # 🚪 LOGOUT
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("landing.py")

# ==================================================
# 🧾 HEADER
# ==================================================
st.markdown(
    """
    <h1>CareRoute Dashboard</h1>
    <p style="color:gray">
    AI-assisted Patient Triage & Hospital Guidance
    </p>
    """,
    unsafe_allow_html=True
)

st.warning("⚠ This system provides guidance only and is not a medical diagnosis.")
st.markdown("<hr>", unsafe_allow_html=True)

# ==================================================
# 🚨 EMERGENCY SECTION
# ==================================================

if nav == "🚨 Emergency":
    st.subheader("🚨 Emergency Help")
    st.error("For accidents or life-threatening situations")

    st.markdown(
        """
        <div style="display:flex; justify-content:center;">
        <a href="https://www.google.com/maps/search/emergency+hospital+near+me"
           target="_blank"
           style="
           display:block;
           background-color:#d32f2f;
           color:white;
           text-align:center;
           padding:18px;
           border-radius:10px;
           font-size:18px;
           font-weight:600;
           text-decoration:none;
           max-width:420px;
           width:100%;
           ">
           🚑 Find Nearest Emergency Hospital
        </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==================================================
# 🏥 AI TRIAGE SECTION
# ==================================================
elif nav == "🏥 AI Triage":
    st.subheader("🏥 Patient Assessment")

    age = st.number_input("Age", min_value=0, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="Example: fever, cough, chest pain, breathlessness"
    )

    if st.button("Analyze & Find Suitable Hospitals"):
        if symptoms.strip() == "":
            st.error("Please enter symptoms.")
        else:
            with st.spinner("Analyzing patient data using AI + RAG..."):
                result = executor(symptoms)

            if not result or not result["recommended_hospitals"]:
                st.warning("No suitable hospitals found.")
            else:
                # -------------------------
                # SHOW HOSPITALS
                # -------------------------
                for hospital in result["recommended_hospitals"]:
                    col_hosp, col_btn = st.columns([4, 1])
                    with col_hosp:
                        st.markdown(f"### 🏥 {hospital['hospital_name']}")
                        st.markdown(
                            f"**Department:** {hospital['department']}")
                        if not hospital["doctor_time_slots"]:
                            st.info("No doctor slots available currently.")
                        else:
                            for doctor in hospital["doctor_time_slots"]:
                                st.write(
                                    f"👨‍⚕️ **{doctor['Doctor_Name']}** "
                                    f"({doctor['Available_Time_Slots']})"
                                )
                    with col_btn:
                        directions_link = hospital.get("Directions_Link")
                        if directions_link:
                            st.markdown(
                                f"<a href='{directions_link}' target='_blank'><button style='background-color:#1976d2;color:white;padding:8px 16px;border:none;border-radius:6px;font-weight:600;'>Get Directions</button></a>", unsafe_allow_html=True)
                # -------------------------
                # SAVE CASE TO PROFILE
                # -------------------------
                st.session_state.past_cases.append({
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "query": symptoms,
                    "department": result["recommended_hospitals"][0]["department"],
                    "summary": result["report_summary_en"]
                })

# ==================================================
# 📄 REPORT ANALYZER SECTION
# ==================================================
elif nav == "📄 Report Analyzer":
    st.switch_page("pages/medical_report_analyzer.py")

# ==================================================
# 👤 PROFILE SECTION
# ==================================================
elif nav == "👤 My Profile":
    st.subheader("👤 My Profile & Past Cases")

    user = st.session_state.get("user_profile", {})

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🧾 Personal Details")
        st.write(f"**Name:** {user.get('name', '-')}")
        st.write(f"**Email:** {user.get('email', '-')}")
        st.write(f"**Gender:** {user.get('gender', '-')}")
        st.write(f"**DOB:** {user.get('dob', '-')}")
        st.write(f"**Blood Group:** {user.get('blood_group', '-')}")
        st.write(f"**Location:** {user.get('location', '-')}")

    with col2:
        st.markdown("### 📜 Past Health Cases")

        if not st.session_state.past_cases:
            st.info("No past health cases found.")
        else:
            for idx, case in enumerate(reversed(st.session_state.past_cases), 1):
                with st.expander(f"🩺 Case {idx} | {case['date']}"):
                    st.write(f"**Symptoms:** {case['query']}")
                    st.write(f"**Department:** {case['department']}")
                    st.write("**Summary:**")
                    for p in case["summary"]:
                        st.markdown(f"- {p}")

# ==================================================
# 📌 FOOTER
# ==================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("CareRoute | Built using ML + RAG + Vector Search")
