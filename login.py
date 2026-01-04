import streamlit as st

st.set_page_config(
    page_title="Login | CareRoute",
    page_icon="🔐",
    layout="centered"
)

# Hide sidebar
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>🔐 Login to CareRoute</h2>", unsafe_allow_html=True)
st.markdown("---")

email = st.text_input("📧 Email")
password = st.text_input("🔑 Password", type="password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Login", use_container_width=True):
    if email and password:
        # Dummy authentication (for hackathon/demo)
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.switch_page("pages/dashboard.py")
    else:
        st.error("Please enter email and password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Don't have an account? Signup"):
    st.switch_page("pages/signup.py")
