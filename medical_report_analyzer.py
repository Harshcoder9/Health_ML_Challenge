import streamlit as st
import pdfplumber
import re
from sentence_transformers import SentenceTransformer, util
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io
import ai_med

# =========================
# 🔐 AUTH GUARD
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.warning("Please login to continue.")
    st.rerun()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CareRoute | Report Analyzer",
    page_icon="📄",
    layout="wide"
)

# =========================
# LOAD MODEL (OFFLINE)
# =========================


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()

# =========================
# SIDEBAR NAVIGATION
# =========================

with st.sidebar:
    nav = st.radio(
        "Navigation",
        ["🚨 Emergency", "🏥 AI Triage", "📄 Report Analyzer", "👤 My Profile"],
        index=2  # Current page
    )

    st.markdown("---")

    language = st.radio(
        "Language",
        ["English", "Hindi"]
    )

    st.markdown("---")

    # ✅ LOGOUT (CORRECT WAY)
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("landing.py")

# =========================
# NAVIGATION HANDLER
# =========================
if nav == "🚨 Emergency":
    st.switch_page("pages/dashboard.py")   # Dashboard handles Emergency
elif nav == "🏥 AI Triage":
    st.switch_page("pages/dashboard.py")
# 📄 Report Analyzer → stay here

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

# =========================
# HELPER FUNCTIONS
# =========================


def extract_text_from_pdf(pdf_file):
    text = ""

    # 1️⃣ Try normal text extraction
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

            # 2️⃣ If page has images → OCR them
            if len(text.strip()) < 50:
                for img in page.images:
                    try:
                        x0, top, x1, bottom = img["x0"], img["top"], img["x1"], img["bottom"]
                        cropped = page.crop(
                            (x0, top, x1, bottom)).to_image(resolution=300)
                        pil_img = cropped.original
                        ocr_text = pytesseract.image_to_string(pil_img)
                        text += ocr_text + "\n"
                    except:
                        pass

    return text


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)


def analyze_report(report_text, user_symptoms):
    sentences = split_sentences(report_text)
    symptom_list = [s.strip() for s in user_symptoms.split(",")]

    sent_embeddings = model.encode(sentences, convert_to_tensor=True)
    symptom_embeddings = model.encode(symptom_list, convert_to_tensor=True)

    confirmed = []
    for i, symptom in enumerate(symptom_list):
        scores = util.cos_sim(symptom_embeddings[i], sent_embeddings)
        if scores.max() > 0.45:
            confirmed.append(symptom)

    missing = list(set(symptom_list) - set(confirmed))

    text_lower = report_text.lower()

    if any(k in text_lower for k in ["heart", "cardiac", "ecg", "troponin"]):
        specialist = "Cardiologist"
    elif any(k in text_lower for k in ["brain", "neuro", "seizure"]):
        specialist = "Neurologist"
    elif any(k in text_lower for k in ["lung", "asthma", "copd"]):
        specialist = "Pulmonologist"
    elif any(k in text_lower for k in ["blood", "wbc", "rbc", "hemoglobin"]):
        specialist = "Hematologist"
    else:
        specialist = "General Physician"

    return confirmed, missing, specialist


def render_result(confirmed, missing, specialist, lang):
    if lang == "English":
        return f"""
**Disclaimer:** This tool provides guidance only and is not a medical diagnosis.
### 🔍 Symptom Match
- **Confirmed:** {', '.join(confirmed) if confirmed else 'None'}
- **Missing:** {', '.join(missing) if missing else 'None'}

### 🚨 Critical Findings
- Some indicators in the report may require medical attention.

### 🏥 Recommendation
- Specialist: **{specialist}**

"""
    else:
        return f"""
### 🔍 लक्षण मिलान
- **पुष्ट लक्षण:** {', '.join(confirmed) if confirmed else 'कोई नहीं'}
- **गायब लक्षण:** {', '.join(missing) if missing else 'कोई नहीं'}

### 🚨 महत्वपूर्ण निष्कर्ष
- रिपोर्ट में कुछ संकेत डॉक्टर की सलाह की आवश्यकता दर्शाते हैं।

### 🏥 सलाह
- अनुशंसित विशेषज्ञ: **{specialist}**


**अस्वीकरण:** यह टूल केवल मार्गदर्शन के लिए है, चिकित्सीय निदान नहीं।
"""


# =========================
# MAIN UI
# =========================
st.markdown(
    """
    <h1>CareRoute Dashboard </h1>
    <p style="color:gray">
    Understand your medical reports using AI (English / Hindi)
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    uploaded_file = st.file_uploader(
        "Upload Medical Report (PDF)",
        type=["pdf"]
    )

with right:
    symptoms = st.text_area(
        "Enter symptoms (comma separated)",
        placeholder="Example: chest pain, fever, dizziness"
    )

# =========================
# ANALYSIS
# =========================
if st.button("🔍 Analyze Report"):
    if not uploaded_file:
        st.error("Please upload a PDF report.")
    elif not symptoms.strip():
        st.error("Please enter symptoms.")
    else:
        with st.spinner("Analyzing report using AI embeddings..."):
            report_text = extract_text_from_pdf(uploaded_file)

            if len(report_text) < 50:
                st.error("Unable to read PDF content properly.")
            else:
                confirmed, missing, specialist = analyze_report(
                    report_text, symptoms
                )

                st.markdown("---")
                st.markdown(
                    render_result(
                        confirmed, missing, specialist, language
                    )
                )

                # Show simple explanation points in selected language only
                if language == "English":
                    st.subheader("📄 Report Summary (English)")
                    for point in ai_med.generate_report_summary(symptoms, specialist):
                        st.markdown(f"- {point}")
                else:
                    st.subheader("📄 रिपोर्ट का संक्षिप्त सार (Hindi)")
                    for point in ai_med.generate_report_summary_hindi(symptoms, specialist):
                        st.markdown(f"- {point}")

                maps_url = f"https://www.google.com/maps/search/{specialist}+near+me"
                st.link_button(
                    f"📍 Find Nearest {specialist}",
                    maps_url
                )

# =========================
# FOOTER
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("CareRoute | Offline AI Medical Report Understanding")
