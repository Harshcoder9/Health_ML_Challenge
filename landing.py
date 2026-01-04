import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CareRoute | Smart Health",
    page_icon="🏥",
    layout="wide"
)

# =========================
# HIDE STREAMLIT SIDEBAR
# =========================
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
div[data-testid="stAppViewContainer"] { margin-left: 0; }

/* Button Styling */
div.stButton > button {
    width: 100%;
    height: 3.2rem;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# IF ALREADY LOGGED IN → DASHBOARD
# =========================
if st.session_state.logged_in:
    st.switch_page("pages/dashboard.py")

# =========================
# HEADER UI
# =========================
st.markdown(
    """
    <div style="text-align:center;">
        <h1>🏥 CareRoute</h1>
        <p style="color:gray; font-size: 1.5rem;">
            AI-powered emergency & healthcare navigation platform
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# =========================
# MAIN LAYOUT
# =========================
left, right = st.columns([1.3, 1])

with left:
    st.markdown("""
        <ul style="font-size:1.5rem; margin-top:2rem;">
            <li>🚑 24/7 hospital locator for emergencies</li>
            <li>🤖 Instant, reliable AI health advice</li>
            <li>📄 Easy upload & analysis of reports</li>
        </ul>
        <div style="text-align:center; font-size:2rem; margin-top:3rem;">
            Start your health journey with <b>CareRoute</b> today!
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # =========================
    # LOGIN / SIGNUP BUTTONS (FIXED)
    # =========================
    outer_col1, outer_col2, outer_col3 = st.columns([1, 1.2, 1])

    with outer_col2:
        btn_left, btn_right = st.columns(2)

        with btn_left:
            if st.button("Login"):
                st.switch_page("pages/login.py")

        with btn_right:
            if st.button("Signup"):
                st.switch_page("pages/signup.py")

with right:
    st.image(
        "https://img.freepik.com/premium-photo/medical-research-hospital-doctor-neurobiologist-neurosurgeon-looks-tv-screen-with-mri-scan-with-brain-images-thinks-about-treatment-method-sick-patients-saving-lives_1178606-18309.jpg?semt=ais_hybrid&w=740&q=80",
        use_container_width=True
    )
