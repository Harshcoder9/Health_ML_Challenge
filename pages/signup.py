import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Signup | CareRoute",
    page_icon="📝",
    layout="centered"
)

# =========================
# HIDE SIDEBAR + BUTTON STYLE
# =========================
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
div.stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown(
    "<h2 style='text-align:center;'>📝 Create CareRoute Account</h2>",
    unsafe_allow_html=True
)

st.markdown("---")

# =========================
# FORM INPUTS
# =========================
name = st.text_input("👤 Full Name")
email = st.text_input("📧 Email")

col1, col2 = st.columns(2)
with col1:
    password = st.text_input("🔑 Password", type="password")
with col2:
    confirm_password = st.text_input("🔁 Confirm Password", type="password")

st.markdown("### 🩺 Health Details")

col3, col4 = st.columns(2)
with col3:
    gender = st.selectbox("⚧️ Gender", ["Select", "Male", "Female", "Other"])
with col4:
    dob = st.date_input(
        "🎂 Date of Birth",
        min_value=date(1950, 1, 1),
        max_value=date.today()
    )

col5, col6 = st.columns(2)
with col5:
    blood_group = st.selectbox(
        "🩸 Blood Group",
        ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    )
with col6:
    location = st.text_input("📍 Location / City")

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# SIGNUP BUTTON
# =========================
if st.button("Signup", use_container_width=True):
    if not (name and email and password and confirm_password and location):
        st.error("Please fill all required fields")
    elif gender == "Select" or blood_group == "Select":
        st.error("Please select gender and blood group")
    elif password != confirm_password:
        st.error("Passwords do not match")
    else:
        # Demo signup (session-based)
        st.session_state.logged_in = True
        st.session_state.user_profile = {
            "name": name,
            "email": email,
            "gender": gender,
            "dob": str(dob),
            "blood_group": blood_group,
            "location": location
        }

        st.success("Account created successfully!")
        st.switch_page("pages/dashboard.py")

# =========================
# EMERGENCY CTA (INTEGRATED)
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

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

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# NAVIGATION
# =========================
if st.button("Already have an account? Login"):
    st.switch_page("pages/login.py")
