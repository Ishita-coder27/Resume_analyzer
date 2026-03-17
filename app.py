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

# ─── CONFIG ───────────────────────────────────────────────────────────────────

load_dotenv()

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = os.getenv("GOOGLE_API_KEY", "")

genai.configure(api_key=api_key)
MODEL = genai.GenerativeModel("models/gemini-2.5-flash")

# ─── SESSION STATE ────────────────────────────────────────────────────────────

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# ─── STYLING ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #f8f9ff !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="block-container"] {
    padding-top: 2rem !important;
    max-width: 960px !important;
}

/* ── ALL TEXT ── */
h1, h2, h3, h4, h5, h6, p, span, label, div,
[data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', sans-serif !important;
    color: #1a1a2e !important;
}

/* ── TITLE ── */
h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: #1a1a2e !important;
    letter-spacing: -1px !important;
    line-height: 1.2 !important;
    margin-bottom: 0.25rem !important;
}

h2 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: #6366f1 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
}

h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    border: none !important;
    margin-top: 1.2rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid #e5e7eb !important;
    gap: 0 !important;
}

[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #9ca3af !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 10px 20px !important;
    clip-path: none !important;
    border-radius: 0 !important;
}

[data-baseweb="tab"]:hover {
    color: #4f46e5 !important;
    background: transparent !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    color: #4f46e5 !important;
    border-bottom: 2px solid #4f46e5 !important;
    font-weight: 600 !important;
}

[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ── INPUTS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-left: 1.5px solid #e5e7eb !important;
    border-radius: 10px !important;
    transition: border-color 0.2s !important;
}

div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

input, textarea {
    color: #1a1a2e !important;
    background: transparent !important;
    -webkit-text-fill-color: #1a1a2e !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}

textarea::placeholder, input::placeholder {
    color: #9ca3af !important;
    -webkit-text-fill-color: #9ca3af !important;
}

[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
    background: #ffffff !important;
    border: 2px dashed #c7d2fe !important;
    border-left: 2px dashed #c7d2fe !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: all 0.2s !important;
}

[data-testid="stFileUploader"] > section:hover {
    border-color: #6366f1 !important;
    background: #fafafe !important;
}

[data-testid="stFileUploader"] button {
    background: #6366f1 !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    clip-path: none !important;
    padding: 0.5rem 1.2rem !important;
}

[data-testid="stFileUploader"] button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stFileUploader"] label p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: #4f46e5 !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 10px !important;
    clip-path: none !important;
    transition: all 0.2s !important;
    margin-top: 0.5rem !important;
}

.stButton > button:hover {
    background: #4338ca !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.35) !important;
    transform: translateY(-1px) !important;
}

.stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-top: 3px solid #6366f1 !important;
    padding: 1.2rem !important;
    border-radius: 12px !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: #4f46e5 !important;
    font-family: 'Inter', sans-serif !important;
    -webkit-text-fill-color: #4f46e5 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #fff7ed !important;
    border: 1px solid #fed7aa !important;
    border-left: 3px solid #f97316 !important;
    border-radius: 8px !important;
}

[data-testid="stAlert"] p {
    color: #9a3412 !important;
    -webkit-text-fill-color: #9a3412 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
}

/* ── CODE BLOCK ── */
.stCode > pre {
    background: #f8fafc !important;
    border: 1.5px solid #e5e7eb !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 10px !important;
}

.stCode > pre > code,
.stCode > pre > code * {
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 0.8rem !important;
}

/* ── MARKDOWN TEXT ── */
[data-testid="stMarkdownContainer"] p {
    font-size: 0.875rem !important;
    line-height: 1.7 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    border: 1.5px solid #6366f1 !important;
    color: #4f46e5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    clip-path: none !important;
    transition: all 0.2s !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: #f5f3ff !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.2) !important;
}

[data-testid="stDownloadButton"] > button * {
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-bottom: 0.25rem;">
    <span style="font-family:'Inter',sans-serif; font-size:0.7rem; font-weight:600;
          color:#6366f1; letter-spacing:2px; text-transform:uppercase;">
        RESUME CHECKER + BUILDER
    </span>
</div>
""", unsafe_allow_html=True)

st.title("Get expert feedback on your resume, instantly.")

st.markdown("""
<p style="font-family:'Inter',sans-serif; font-size:1rem; color:#6b7280;
   margin-top:0.25rem; margin-bottom:1.5rem; max-width:560px;
   -webkit-text-fill-color:#6b7280;">
    AI-powered resume checker that scores your resume on key criteria recruiters
    look for. Get actionable steps to improve and land more interviews.
</p>
""", unsafe_allow_html=True)

# ─── FUNCTIONS ────────────────────────────────────────────────────────────────

def is_resume(text):
    text = text.lower()
    resume_keywords = [
        "education", "experience", "skills", "projects",
        "certifications", "internship", "summary"
    ]
    return sum([1 for w in resume_keywords if w in text]) >= 2


def extract_pdf_text(uploaded_file):
    if uploaded_file is None:
        st.error("No file uploaded.")
        return ""
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                t = page.extract_text()
                if t:
                    text += t
            except Exception as page_error:
                st.warning(f"Error reading page {i+1}: {page_error}")
        if not text.strip():
            st.warning("No readable text found — possibly a scanned PDF.")
        return text
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""


def extract_keywords(text):
    skills = [
        "python", "java", "c++", "javascript", "react", "node",
        "docker", "kubernetes", "mongodb", "sql", "aws",
        "machine learning", "tensorflow", "pytorch",
        "data structures", "algorithms", "rest api"
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

    required_sections = ["education", "experience", "skills", "projects"]
    missing_sections = 0
    for sec in required_sections:
        if sec not in text:
            missing_sections += 1
            issues.append(f"Missing section: {sec}")
    score -= missing_sections * 12

    words = len(resume_text.split())
    if words < 400:
        score -= 25
        issues.append("Too short (under 400 words)")
    elif words > 900:
        score -= 12
        issues.append("Too long (over 900 words)")

    bullet_count = resume_text.count("•") + resume_text.count("-")
    if bullet_count < 5:
        score -= 15
        issues.append("Very few bullet points")
    elif bullet_count < 10:
        score -= 8
        issues.append("Not enough bullet points")

    action_verbs = [
        "developed", "built", "designed", "implemented", "optimized",
        "created", "engineered", "improved", "automated", "led",
        "managed", "architected", "analyzed"
    ]
    verb_count = sum([1 for v in action_verbs if v in text])
    if verb_count < 3:
        score -= 15
        issues.append("Weak action verbs — use words like Built, Led, Optimized")
    elif verb_count < 6:
        score -= 8

    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15
        issues.append("No quantified achievements (add numbers like 40%, 2x, 500+)")

    if "|" in resume_text:
        score -= 12
        issues.append("Tables or pipes detected — risky for ATS parsing")
    if len(resume_text.split("\n")) < 15:
        score -= 10
        issues.append("Poor structure or spacing")
    if "@" not in resume_text:
        score -= 5
        issues.append("Missing contact email")

    jd_words = re.findall(r"[a-zA-Z]{4,}", jd.lower())
    if jd_words:
        match = sum([1 for w in jd_words if w in text])
        keyword_score = match / len(jd_words)
    else:
        keyword_score = 0

    if keyword_score < 0.2:
        score -= 25
        issues.append("Very low keyword match with job description")
    elif keyword_score < 0.4:
        score -= 18
        issues.append("Low keyword match with job description")
    elif keyword_score < 0.6:
        score -= 10
        issues.append("Moderate keyword match — room to improve")

    resume_skills = extract_keywords(resume_text)
    jd_skills = extract_keywords(jd)
    if jd_skills:
        skill_ratio = len(set(resume_skills) & set(jd_skills)) / len(jd_skills)
        if skill_ratio < 0.3:
            score -= 20
            issues.append("Very low skill match with job description")
        elif skill_ratio < 0.6:
            score -= 10
            issues.append("Partial skill match with job description")

    if text.count("project") > 12 or text.count("experience") > 12:
        score -= 8
        issues.append("Possible keyword stuffing detected")

    if "responsible for" in text:
        score -= 8
        issues.append("Avoid 'responsible for' — use impact-focused language instead")

    if score > 88:
        score = 88
    if score < 0:
        score = 0

    return score, issues


def ai_feedback(resume_text):
    try:
        response = MODEL.generate_content(
            f"Improve this resume:\n{resume_text[:2000]}"
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"


def export_pdf(content):
    file = "resume.pdf"
    c = canvas.Canvas(file)
    y = 800
    for line in content.split("\n"):
        c.drawString(40, y, line)
        y -= 20
    c.save()
    return file


# ─── TABS ─────────────────────────────────────────────────────────────────────

tabs = st.tabs(["Resume Analyzer", "Resume Builder"])

# ══════════════════════════════════════════════════════════
#  TAB 1 — ANALYZER
# ══════════════════════════════════════════════════════════

with tabs[0]:

    st.subheader("Paste the job description")
    jd = st.text_area(
        "Job Description",
        height=160,
        placeholder="Paste the full job description here...",
        label_visibility="collapsed"
    )

    st.subheader("Upload your resume")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    analyze = st.button("Scan Resume")

    if analyze:
        try:
            if uploaded_file is None:
                st.warning("Please upload your resume first.")
                st.stop()
            if jd.strip() == "":
                st.warning("Please paste a job description.")
                st.stop()

            with st.spinner("Analyzing your resume..."):
                text = extract_pdf_text(uploaded_file)

                if not text or len(text.strip()) < 50:
                    st.error("Could not extract text from the PDF. Try a different file.")
                    st.stop()

                res_skills = extract_keywords(text)
                jd_skills = extract_keywords(jd)

                match, missing = calculate_match(res_skills, jd_skills)
                ats_score, issues = ats_check(text, jd)
                feedback = ai_feedback(text)

            # ── Score banner ──
            overall = int((ats_score + match) / 2)
            if overall >= 70:
                banner_color = "#d1fae5"
                banner_border = "#6ee7b7"
                banner_text = "#065f46"
                badge_bg = "#10b981"
                verdict = "Looking good! Your resume is well-optimised."
            elif overall >= 50:
                banner_color = "#fef3c7"
                banner_border = "#fde68a"
                banner_text = "#92400e"
                badge_bg = "#f59e0b"
                verdict = "There's room for improvement. Review the suggestions below."
            else:
                banner_color = "#fee2e2"
                banner_border = "#fca5a5"
                banner_text = "#991b1b"
                badge_bg = "#ef4444"
                verdict = "Your resume needs significant work before applying."

            st.markdown(f"""
            <div style="background:{banner_color}; border:1.5px solid {banner_border};
                 border-radius:12px; padding:1.2rem 1.5rem; margin:1rem 0;
                 display:flex; align-items:center; gap:16px;">
                <div style="background:{badge_bg}; color:#fff; font-family:'Inter',sans-serif;
                     font-weight:800; font-size:1.6rem; width:64px; height:64px;
                     border-radius:50%; display:flex; align-items:center;
                     justify-content:center; flex-shrink:0;">
                    {overall}
                </div>
                <div>
                    <p style="font-family:'Inter',sans-serif; font-weight:700; font-size:1rem;
                       color:{banner_text}; margin:0 0 2px 0;
                       -webkit-text-fill-color:{banner_text};">
                        Your resume scored {overall} out of 100
                    </p>
                    <p style="font-family:'Inter',sans-serif; font-size:0.85rem;
                       color:{banner_text}; margin:0; opacity:0.8;
                       -webkit-text-fill-color:{banner_text};">
                        {verdict}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Metrics ──
            col1, col2 = st.columns(2)
            col1.metric("ATS Score", f"{ats_score} / 100")
            col2.metric("JD Match", f"{match}%")

            # ── Score bars ──
            ats_bar_color = "#10b981" if ats_score >= 70 else "#f59e0b" if ats_score >= 50 else "#ef4444"
            match_bar_color = "#6366f1" if match >= 60 else "#f59e0b" if match >= 40 else "#ef4444"

            st.markdown(f"""
            <div style="background:#ffffff; border:1.5px solid #e5e7eb; border-radius:12px;
                 padding:1.2rem 1.5rem; margin:0.75rem 0;">
                <div style="margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="font-family:'Inter',sans-serif; font-size:0.8rem;
                               font-weight:500; color:#374151;">ATS Compatibility</span>
                        <span style="font-family:'Inter',sans-serif; font-size:0.8rem;
                               font-weight:600; color:{ats_bar_color};">{ats_score}%</span>
                    </div>
                    <div style="height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden;">
                        <div style="width:{ats_score}%; height:100%; background:{ats_bar_color};
                             border-radius:99px; transition:width 0.8s ease;"></div>
                    </div>
                </div>
                <div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="font-family:'Inter',sans-serif; font-size:0.8rem;
                               font-weight:500; color:#374151;">Job Description Match</span>
                        <span style="font-family:'Inter',sans-serif; font-size:0.8rem;
                               font-weight:600; color:{match_bar_color};">{match}%</span>
                    </div>
                    <div style="height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden;">
                        <div style="width:{match}%; height:100%; background:{match_bar_color};
                             border-radius:99px; transition:width 0.8s ease;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Issues ──
            if issues:
                st.subheader("Recommendations")
                for idx, issue in enumerate(issues, 1):
                    st.markdown(f"""
                    <div style="display:flex; align-items:flex-start; gap:12px;
                         background:#ffffff; border:1.5px solid #e5e7eb;
                         border-left:3px solid #f59e0b; border-radius:8px;
                         padding:12px 14px; margin-bottom:8px;">
                        <div style="background:#fef3c7; color:#d97706; font-family:'Inter',sans-serif;
                             font-weight:700; font-size:0.7rem; width:22px; height:22px;
                             border-radius:50%; display:flex; align-items:center;
                             justify-content:center; flex-shrink:0;">{idx}</div>
                        <p style="font-family:'Inter',sans-serif; font-size:0.85rem;
                           color:#374151; -webkit-text-fill-color:#374151; margin:0;
                           line-height:1.5;">{issue}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Missing Skills ──
            if missing:
                st.subheader("Missing Skills")
                chips = "".join([
                    f"""<span style="display:inline-block; background:#f5f3ff;
                        border:1px solid #c7d2fe; color:#4f46e5;
                        -webkit-text-fill-color:#4f46e5;
                        font-family:'Inter',sans-serif; font-size:0.75rem;
                        font-weight:500; padding:4px 12px; border-radius:99px;
                        margin:3px;">{s}</span>"""
                    for s in missing
                ])
                st.markdown(f"<div style='margin-top:4px;'>{chips}</div>", unsafe_allow_html=True)

            # ── AI Feedback ──
            st.subheader("AI Feedback")
            st.markdown(f"""
            <div style="background:#ffffff; border:1.5px solid #e5e7eb; border-radius:12px;
                 padding:1.2rem 1.5rem; margin-top:0.25rem;">
                <p style="font-family:'Inter',sans-serif; font-size:0.875rem; color:#374151;
                   -webkit-text-fill-color:#374151; line-height:1.8; margin:0;
                   white-space:pre-wrap;">{feedback}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# ══════════════════════════════════════════════════════════
#  TAB 2 — BUILDER
# ══════════════════════════════════════════════════════════

with tabs[1]:

    st.subheader("Your details")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        name = st.text_input("Full Name", placeholder="Jane Smith")
    with col_b:
        email = st.text_input("Email", placeholder="jane@email.com")
    with col_c:
        phone = st.text_input("Phone", placeholder="+1 234 567 8900")

    st.subheader("Resume content")

    skills = st.text_area("Skills", placeholder="Python, React, AWS, Docker, SQL...", height=80)
    exp    = st.text_area("Experience", placeholder="Software Engineer @ Acme Corp (2022–Present)\n— Built X, reduced Y by 40%, led team of 5", height=110)
    proj   = st.text_area("Projects", placeholder="Project Name: Description, tech stack, impact...", height=90)
    edu    = st.text_area("Education", placeholder="B.Tech Computer Science — IIT Delhi, 2022", height=70)

    preview = f"""{name}
{email} | {phone}

Skills
{skills}

Experience
{exp}

Projects
{proj}

Education
{edu}
"""

    st.subheader("Preview")

    word_count = len([w for w in preview.split() if w.strip()])
    wc_color = "#10b981" if 400 <= word_count <= 900 else "#f59e0b"

    st.markdown(f"""
    <div style="display:flex; justify-content:flex-end; margin-bottom:4px;">
        <span style="font-family:'Inter',sans-serif; font-size:0.72rem;
               font-weight:500; color:{wc_color}; -webkit-text-fill-color:{wc_color};">
            {word_count} words {"✓ Good length" if 400 <= word_count <= 900 else "— aim for 400–900 words"}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.code(preview, language=None)

    if st.button("Generate Resume"):
        doc = Document()
        for line in preview.split("\n"):
            doc.add_paragraph(line)
        doc.save("resume.docx")
        pdf_file = export_pdf(preview)

        st.markdown("""
        <div style="background:#d1fae5; border:1px solid #6ee7b7; border-radius:8px;
             padding:10px 14px; margin:8px 0;">
            <p style="font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:600;
               color:#065f46; -webkit-text-fill-color:#065f46; margin:0;">
                Resume ready! Download below.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            with open("resume.docx", "rb") as f:
                st.download_button(
                    "Download DOCX", f, "resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        with col_dl2:
            with open(pdf_file, "rb") as f:
                st.download_button(
                    "Download PDF", f, "resume.pdf",
                    mime="application/pdf"
                )

# ─── FOOTER ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem;
     border-top:1px solid #e5e7eb;">
    <p style="font-family:'Inter',sans-serif; font-size:0.75rem; color:#9ca3af;
       -webkit-text-fill-color:#9ca3af; margin:0;">
        Acadence Resume Lab — Powered by Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
