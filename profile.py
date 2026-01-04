import streamlit as st

st.set_page_config(
    page_title="Profile | CareRoute",
    page_icon="👤",
    layout="wide"
)

# Hide sidebar
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# AUTH CHECK
# -------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view your profile")
    st.switch_page("pages/login.py")

# -------------------------
# INIT DATA
# -------------------------
user = st.session_state.get("user_profile", {})

if "past_cases" not in st.session_state:
    st.session_state.past_cases = []

# -------------------------
# HEADER
# -------------------------
st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------
# PROFILE INFO
# -------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🧾 Personal Details")
    st.write(f"**Name:** {user.get('name','-')}")
    st.write(f"**Email:** {user.get('email','-')}")
    st.write(f"**Gender:** {user.get('gender','-')}")
    st.write(f"**DOB:** {user.get('dob','-')}")
    st.write(f"**Blood Group:** {user.get('blood_group','-')}")
    st.write(f"**Location:** {user.get('location','-')}")

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

st.markdown("<br>")

# -------------------------
# NAVIGATION
# -------------------------
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")
