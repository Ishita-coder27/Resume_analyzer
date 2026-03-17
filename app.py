import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import re
from docx import Document
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Acadence Resume Lab",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CONFIG

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("models/gemini-2.5-flash")

#SESSION STATE

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# UI STYLING 

st.markdown("""
<style>
/* 1. App Background */
.stApp {
    background: linear-gradient(135deg, #e0ecff, #c7dbff, #a9c9ff);
}

/* 2. Global Text Colors - Force Dark Blue */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #1e3a8a !important;
}

/* 3. Inputs & Text Areas - Force White Background & Dark Text */
/* This targets the stubborn Streamlit wrapper divs */
div[data-baseweb="input"] > div, 
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
}

/* This targets the actual typing area */
input, textarea {
    color: #1e3a8a !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #1e3a8a !important;
}

/* 4. File Uploader - Force White Background */
[data-testid="stFileUploader"] > section {
    background-color: #ffffff !important;
    border: 2px dashed #3b82f6 !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] button {
    background-color: #3b82f6 !important;
    color: white !important;
}
[data-testid="stFileUploader"] button * {
    color: white !important;
}

/* 5. Main Action Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
    font-weight: bold !important;
}
.stButton > button * {
    color: white !important;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
}

/* 6. Tabs Styling */
.stTabs [data-baseweb="tab"] {
    font-weight: bold;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid #2563eb !important;
}

/* 7. Resume Builder Preview Box (st.code) */
.stCode > pre {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
.stCode > pre > code, .stCode > pre > code * {
    color: #1e3a8a !important;
    text-shadow: none !important;
}

/* Hide Streamlit fluff */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

#  FUNCTIONS

def is_resume(text):
    text = text.lower()
    resume_keywords = [
        "education","experience","skills","projects",
        "certifications","internship","summary"
    ]
    return sum([1 for w in resume_keywords if w in text]) >= 2


def extract_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t
    return text


def extract_keywords(text):
    skills = [
        "python","java","c++","javascript","react","node",
        "docker","kubernetes","mongodb","sql","aws",
        "machine learning","tensorflow","pytorch",
        "data structures","algorithms","rest api"
    ]
    text = text.lower()
    return [s for s in skills if s in text]


def calculate_match(resume_skills, jd_skills):
    if not jd_skills:
        return 0, []
    matched = set(resume_skills) & set(jd_skills)
    score = int(len(matched) / len(jd_skills) * 100)
    missing = list(set(jd_skills) - set(resume_skills))
    return score, missing


def ats_check(resume_text, jd):

    text = resume_text.lower()
    score = 100
    issues = []

    # ---------------- SECTION CHECK (STRICT) ----------------
    required_sections = ["education", "experience", "skills", "projects"]

    missing_sections = 0
    for sec in required_sections:
        if sec not in text:
            missing_sections += 1
            issues.append(f"Missing section: {sec}")

    score -= missing_sections * 12   # stronger penalty


    # LENGTH CHECK 
    words = len(resume_text.split())

    if words < 400:
        score -= 25
        issues.append("Too short (<400 words)")

    elif words > 900:
        score -= 12
        issues.append("Too long (>900 words)")


    # BULLET POINT QUALITY 
    bullet_count = resume_text.count("•") + resume_text.count("-")

    if bullet_count < 5:
        score -= 15
        issues.append("Very few bullet points")

    elif bullet_count < 10:
        score -= 8
        issues.append("Insufficient bullet points")


    # ACTION VERBS 
    action_verbs = [
        "developed","built","designed","implemented","optimized",
        "created","engineered","improved","automated","led",
        "managed","architected","analyzed"
    ]

    verb_count = sum([1 for v in action_verbs if v in text])

    if verb_count < 3:
        score -= 15
        issues.append("Weak action verbs")

    elif verb_count < 6:
        score -= 8


    # METRICS CHECK 
    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15
        issues.append("No quantified achievements")

    
    # FORMATTING CHECK
    if "|" in resume_text:
        score -= 12
        issues.append("Tables detected (ATS risk)")

    if len(resume_text.split("\n")) < 15:
        score -= 10
        issues.append("Poor structure / spacing")

    if "@" not in resume_text:
        score -= 5
        issues.append("Missing contact info")


    # KEYWORD MATCH (VERY STRICT)
    jd_words = re.findall(r"[a-zA-Z]{4,}", jd.lower())

    if jd_words:
        match = sum([1 for w in jd_words if w in text])
        keyword_score = match / len(jd_words)
    else:
        keyword_score = 0

    if keyword_score < 0.2:
        score -= 25
        issues.append("Very low JD keyword match")

    elif keyword_score < 0.4:
        score -= 18
        issues.append("Low JD keyword match")

    elif keyword_score < 0.6:
        score -= 10
        issues.append("Moderate JD keyword match")


    #  SKILL MATCH
    resume_skills = extract_keywords(resume_text)
    jd_skills = extract_keywords(jd)

    if jd_skills:
        skill_ratio = len(set(resume_skills) & set(jd_skills)) / len(jd_skills)

        if skill_ratio < 0.3:
            score -= 20
            issues.append("Very low skill match")

        elif skill_ratio < 0.6:
            score -= 10
            issues.append("Partial skill match")


    # REPETITION / SPAM 
    if text.count("project") > 12 or text.count("experience") > 12:
        score -= 8
        issues.append("Keyword stuffing detected")


    #  IMPACT CHECK
    if "responsible for" in text:
        score -= 8
        issues.append("Weak phrasing (responsibility-based, not impact-based)")


    #  FINAL CAP 
    if score > 88:
        score = 88   # never perfect

    if score < 0:
        score = 0

    return score, issues


def ai_feedback(resume_text):
    response = MODEL.generate_content(f"Improve this resume:\n{resume_text[:3000]}")
    return response.text


def export_pdf(content):
    file = "resume.pdf"
    c = canvas.Canvas(file)
    y = 800
    for line in content.split("\n"):
        c.drawString(40, y, line)
        y -= 20
    c.save()
    return file


#  UI 

st.title("Acadence Resume Lab")

tabs = st.tabs(["Analyzer", "Builder"])

# ANALYZER 

with tabs[0]:

    st.subheader("Resume Analysis")

    jd = st.text_area("Job Description")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

    if st.button("Analyze"):

        if uploaded_file and jd:

            text = extract_pdf_text(uploaded_file)

            res_skills = extract_keywords(text)
            jd_skills = extract_keywords(jd)

            match, missing = calculate_match(res_skills, jd_skills)
            ats_score, issues = ats_check(text, jd)

            feedback = ai_feedback(text)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("ATS Score", ats_score)
            with col2:
                st.metric("Match Score", f"{match}%")

            st.subheader("Feedback")
            st.write(feedback)

            if issues:
                st.subheader("Issues Found")
                for i in issues:
                    st.write("-", i)


#  BUILDER 

with tabs[1]:

    st.subheader("Resume Builder")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    skills = st.text_area("Skills")
    exp = st.text_area("Experience")
    proj = st.text_area("Projects")
    edu = st.text_area("Education")

    preview = f"""
{name}
{email} | {phone}

Skills:
{skills}

Experience:
{exp}

Projects:
{proj}

Education:
{edu}
"""

    st.subheader("Preview")
    st.code(preview)

    if st.button("Generate Resume"):

        doc = Document()
        for line in preview.split("\n"):
            doc.add_paragraph(line)

        doc.save("resume.docx")

        pdf_file = export_pdf(preview)

        with open("resume.docx", "rb") as f:
            st.download_button("Download DOCX", f, "resume.docx")

        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, "resume.pdf")