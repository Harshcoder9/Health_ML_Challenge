import streamlit as st
from ai_med import executor   # backend function import

st.set_page_config(page_title="CareRoute", page_icon="🏥")

# -------------------------
# HEADER
# -------------------------
st.title("🏥 CareRoute")
st.caption("AI-assisted Patient Triage & Hospital Guidance")

st.warning("⚠ This system provides guidance only and is not a medical diagnosis.")

# =========================
# 🚨 EMERGENCY BUTTON (NEW)
# =========================
st.markdown("## 🚨 Emergency Help")


emergency_url = "https://www.google.com/maps/search/emergency+hospital+near+me"
st.link_button("📍 Nearest Emergency Hospitals", emergency_url)

st.markdown("---")

# -------------------------
# PATIENT INPUT
# -------------------------
st.subheader("Patient Details")

age = st.number_input("Age", min_value=0, max_value=120)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

symptoms = st.text_area(
    "Describe your symptoms",
    placeholder="Example: fever, cough, chest pain, breathlessness"
)

# -------------------------
# ANALYZE BUTTON
# -------------------------
if st.button("Analyze & Find Suitable Hospitals"):

    if symptoms.strip() == "":
        st.error("Please enter symptoms before analysis.")
    else:
        st.info("Analyzing patient data using AI + RAG...")

        # 🔥 BACKEND CALL
        results = executor(symptoms)

        # -------------------------
        # OUTPUT
        # -------------------------
        st.subheader("🏥 Recommended Hospitals & Doctors")

        if len(results) == 0:
            st.warning("No suitable hospitals found for the detected department.")
        else:
            for hospital in results:
                st.markdown(f"### 🏥 {hospital['hospital_name']}")

                st.markdown("**Available Doctors & Time Slots:**")
                for doctor in hospital["doctor_time_slots"]:
                    st.write(
                        f"👨‍⚕️ **{doctor['Doctor_Name']}** "
                        f"({doctor['Available_Time_Slots']})"
                    )

        st.success("Analysis completed successfully.")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.caption("CareRoute | Built using ML + RAG + Vector Search")
