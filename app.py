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

load_dotenv()
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = os.getenv("GOOGLE_API_KEY", "")

genai.configure(api_key=api_key)
MODEL = genai.GenerativeModel("models/gemini-2.5-flash")

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# ─── CSS ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

#MainMenu {visibility: hidden;}
footer     {visibility: hidden;}
header     {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #f4f6ff !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="block-container"] {
    padding-top: 0 !important;
    max-width: 980px !important;
}

/* ── HERO ── */
.hero-banner {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #a855f7 100%);
    border-radius: 0 0 28px 28px;
    padding: 2.8rem 3rem 2.4rem;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 280px; height: 280px;
    background: rgba(255,255,255,0.06); border-radius: 50%;
}
.hero-banner::after {
    content: '';
    position: absolute; bottom: -70px; left: 38%;
    width: 380px; height: 220px;
    background: rgba(255,255,255,0.04); border-radius: 50%;
}
.hero-eyebrow {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 3px;
    text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.9rem; font-weight: 900; color: #fff;
    letter-spacing: -2px; line-height: 1.05; margin-bottom: 0.7rem;
}
.hero-title span {
    background: linear-gradient(90deg, #c4b5fd, #f0abfc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.95rem; color: rgba(255,255,255,0.68); max-width: 480px; line-height: 1.6;
}
.stat-row { display: flex; gap: 10px; margin-top: 1.4rem; flex-wrap: wrap; }
.stat-pill {
    background: rgba(255,255,255,0.14); backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2); border-radius: 99px;
    padding: 5px 15px; font-size: 0.73rem; font-weight: 600;
    color: #fff; display: inline-flex; align-items: center; gap: 6px;
}
.stat-pill .dot {
    width: 7px; height: 7px; border-radius: 50%; background: #a3e635;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.5; transform:scale(1.35); }
}

/* ── ALL TEXT ── */
h1,h2,h3,h4,h5,h6,p,span,label,div,
[data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', sans-serif !important;
    color: #1e1b4b !important;
}
h2 {
    font-size: 0.65rem !important; font-weight: 700 !important;
    color: #6366f1 !important; letter-spacing: 2.5px !important;
    text-transform: uppercase !important; border: none !important;
    margin-top: 1.8rem !important; margin-bottom: 0.5rem !important;
}
h3 {
    font-size: 1.05rem !important; font-weight: 700 !important;
    color: #1e1b4b !important; border: none !important;
    margin-top: 1rem !important; letter-spacing: -0.3px !important;
    text-transform: none !important;
}
.section-label {
    font-family: 'Inter', sans-serif; font-size: 0.68rem; font-weight: 700;
    color: #6366f1; letter-spacing: 2.5px; text-transform: uppercase;
    margin-bottom: 6px; display: block;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #e5e7eb !important; gap: 0 !important;
}
[data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    color: #9ca3af !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 500 !important;
    letter-spacing: -0.2px !important; text-transform: none !important;
    padding: 12px 24px !important; clip-path: none !important;
    border-radius: 0 !important; transition: color 0.2s !important;
}
[data-baseweb="tab"]:hover { color: #4f46e5 !important; }
[aria-selected="true"][data-baseweb="tab"] {
    color: #4f46e5 !important;
    border-bottom: 3px solid #4f46e5 !important;
    font-weight: 700 !important;
}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"] { display:none !important; }

/* ── INPUTS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {
    background: #fff !important; border: 2px solid #e5e7eb !important;
    border-left: 2px solid #e5e7eb !important; border-radius: 12px !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12), 0 4px 12px rgba(99,102,241,0.08) !important;
    transform: translateY(-1px) !important;
}
input, textarea {
    color: #1e1b4b !important; background: transparent !important;
    -webkit-text-fill-color: #1e1b4b !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important;
}
textarea::placeholder, input::placeholder {
    color: #c4b5fd !important; -webkit-text-fill-color: #c4b5fd !important;
}
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 600 !important; color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
    letter-spacing: 0 !important; text-transform: none !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
    background: linear-gradient(135deg, #fafafe, #f5f3ff) !important;
    border: 2px dashed #a5b4fc !important;
    border-left: 2px dashed #a5b4fc !important;
    border-radius: 16px !important; padding: 2rem !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stFileUploader"] > section:hover {
    border-color: #6366f1 !important;
    background: linear-gradient(135deg,#f0ebff,#ede9fe) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.15) !important;
}
[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    border: none !important; color: #fff !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 700 !important; border-radius: 10px !important;
    clip-path: none !important; padding: 0.55rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.38) !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] button:hover {
    box-shadow: 0 7px 22px rgba(99,102,241,0.52) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stFileUploader"] button * {
    color: #fff !important; -webkit-text-fill-color: #fff !important;
}
[data-testid="stFileUploader"] label p {
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 600 !important; color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button {
    width: auto !important;
    background: linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%) !important;
    border: none !important; color: #fff !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.95rem !important;
    font-weight: 700 !important; letter-spacing: -0.2px !important;
    text-transform: none !important; padding: 0.8rem 2.5rem !important;
    border-radius: 14px !important; clip-path: none !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.42), 0 2px 6px rgba(79,70,229,0.2) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin-top: 0.75rem !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 14px 36px rgba(79,70,229,0.52), 0 4px 14px rgba(79,70,229,0.28) !important;
}
.stButton > button:active {
    transform: translateY(-1px) scale(0.98) !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.4) !important;
}
.stButton > button * {
    color: #fff !important; -webkit-text-fill-color: #fff !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #fff !important; border: 2px solid #e5e7eb !important;
    border-top: 4px solid #6366f1 !important; padding: 1.4rem !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.08) !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 16px 36px rgba(99,102,241,0.16) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important; font-size: 2.2rem !important;
    font-weight: 900 !important; color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important; letter-spacing: -1px !important;
}
[data-testid="stMetricLabel"] p {
    font-family: 'Inter', sans-serif !important; font-size: 0.72rem !important;
    font-weight: 600 !important; color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
    text-transform: uppercase !important; letter-spacing: 1.5px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: #4f46e5 !important; font-family: 'Inter', sans-serif !important;
    -webkit-text-fill-color: #4f46e5 !important; font-weight: 500 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #fffbeb !important; border: 1.5px solid #fde68a !important;
    border-left: 4px solid #f59e0b !important; border-radius: 12px !important;
}
[data-testid="stAlert"] p {
    color: #92400e !important; -webkit-text-fill-color: #92400e !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
}

/* ── CODE BLOCK ── */
.stCode > pre {
    background: #fafafe !important; border: 2px solid #e5e7eb !important;
    border-left: 4px solid #6366f1 !important; border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.06) !important;
}
.stCode > pre > code, .stCode > pre > code * {
    color: #3730a3 !important; -webkit-text-fill-color: #3730a3 !important;
    font-family: 'JetBrains Mono','Fira Code',monospace !important;
    font-size: 0.8rem !important;
}

/* ── MARKDOWN ── */
[data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem !important; line-height: 1.75 !important;
    color: #374151 !important; -webkit-text-fill-color: #374151 !important;
}

/* ── DOWNLOAD BUTTONS ── */
[data-testid="stDownloadButton"] > button {
    background: #fff !important; border: 2px solid #6366f1 !important;
    color: #4f46e5 !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 700 !important;
    border-radius: 12px !important; clip-path: none !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    padding: 0.65rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.12) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border-color: transparent !important;
    box-shadow: 0 10px 28px rgba(79,70,229,0.38) !important;
    transform: translateY(-3px) scale(1.02) !important;
}
[data-testid="stDownloadButton"] > button:hover * {
    color: #fff !important; -webkit-text-fill-color: #fff !important;
}
[data-testid="stDownloadButton"] > button * {
    color: #4f46e5 !important; -webkit-text-fill-color: #4f46e5 !important;
}

/* ── ANIMATIONS ── */
@keyframes score-pop {
    0%  { transform:scale(0.4); opacity:0; }
    70% { transform:scale(1.1); }
    100%{ transform:scale(1);   opacity:1; }
}
.score-ring { animation: score-pop 0.65s cubic-bezier(0.34,1.56,0.64,1) forwards; }

@keyframes card-in {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0); }
}
.card-animate { animation: card-in 0.45s cubic-bezier(0.4,0,0.2,1) forwards; }

@keyframes bar-grow { from { width:0%; } }
.bar-animated { animation: bar-grow 1.3s cubic-bezier(0.4,0,0.2,1) forwards; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(#a5b4fc,#c4b5fd); border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ─── HERO BANNER ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
    <div class="hero-eyebrow">AI-Powered · Free · Instant Results</div>
    <div class="hero-title">Acadence <span>Resume Lab</span></div>
    <div class="hero-sub">
        Score your resume against real recruiter criteria.
        Get actionable fixes and land more interviews.
    </div>
    <div class="stat-row">
        <div class="stat-pill"><span class="dot"></span> AI Engine Online</div>
        <div class="stat-pill">⚡ Instant Analysis</div>
        <div class="stat-pill">🎯 ATS Optimised</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── FUNCTIONS ────────────────────────────────────────────────────────────────

def is_resume(text):
    text = text.lower()
    return sum(1 for w in ["education","experience","skills","projects",
                            "certifications","internship","summary"] if w in text) >= 2

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
                if t: text += t
            except Exception as e:
                st.warning(f"Error reading page {i+1}: {e}")
        if not text.strip():
            st.warning("No readable text found — possibly a scanned PDF.")
        return text
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def extract_keywords(text):
    skills = ["python","java","c++","javascript","react","node","docker","kubernetes",
              "mongodb","sql","aws","machine learning","tensorflow","pytorch",
              "data structures","algorithms","rest api"]
    text = text.lower()
    return [s for s in skills if s in text]

def calculate_match(resume_skills, jd_skills):
    if not jd_skills: return 0, []
    matched = set(resume_skills) & set(jd_skills)
    score   = int(len(matched) / len(jd_skills) * 100)
    missing = list(set(jd_skills) - set(resume_skills))
    return score, missing

def ats_check(resume_text, jd):
    text  = resume_text.lower()
    score = 100
    issues = []
    for sec in ["education","experience","skills","projects"]:
        if sec not in text:
            score -= 12; issues.append(f"Missing section: {sec}")
    words = len(resume_text.split())
    if words < 400:    score -= 25; issues.append("Too short (under 400 words)")
    elif words > 900:  score -= 12; issues.append("Too long (over 900 words)")
    bullets = resume_text.count("•") + resume_text.count("-")
    if bullets < 5:    score -= 15; issues.append("Very few bullet points")
    elif bullets < 10: score -= 8;  issues.append("Not enough bullet points")
    verbs = ["developed","built","designed","implemented","optimized","created",
             "engineered","improved","automated","led","managed","architected","analyzed"]
    vc = sum(1 for v in verbs if v in text)
    if vc < 3:   score -= 15; issues.append("Weak action verbs — use words like Built, Led, Optimized")
    elif vc < 6: score -= 8
    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15; issues.append("No quantified achievements (add numbers like 40%, 2x, 500+)")
    if "|" in resume_text:             score -= 12; issues.append("Tables or pipes detected — risky for ATS parsing")
    if len(resume_text.split("\n")) < 15: score -= 10; issues.append("Poor structure or spacing")
    if "@" not in resume_text:         score -= 5;  issues.append("Missing contact email")
    jd_words = re.findall(r"[a-zA-Z]{4,}", jd.lower())
    if jd_words:
        ks = sum(1 for w in jd_words if w in text) / len(jd_words)
    else:
        ks = 0
    if ks < 0.2:   score -= 25; issues.append("Very low keyword match with job description")
    elif ks < 0.4: score -= 18; issues.append("Low keyword match with job description")
    elif ks < 0.6: score -= 10; issues.append("Moderate keyword match — room to improve")
    rs = extract_keywords(resume_text); js = extract_keywords(jd)
    if js:
        sr = len(set(rs) & set(js)) / len(js)
        if sr < 0.3:   score -= 20; issues.append("Very low skill match with job description")
        elif sr < 0.6: score -= 10; issues.append("Partial skill match with job description")
    if text.count("project") > 12 or text.count("experience") > 12:
        score -= 8; issues.append("Possible keyword stuffing detected")
    if "responsible for" in text:
        score -= 8; issues.append("Avoid 'responsible for' — use impact-focused language instead")
    return max(0, min(88, score)), issues

def ai_feedback(resume_text):
    try:
        r = MODEL.generate_content(f"Improve this resume:\n{resume_text[:2000]}")
        return r.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

def export_pdf(content):
    file = "resume.pdf"
    c = canvas.Canvas(file)
    y = 800
    for line in content.split("\n"):
        c.drawString(40, y, line); y -= 20
    c.save(); return file

# ─── TABS ─────────────────────────────────────────────────────────────────────

tabs = st.tabs(["✦  Resume Analyzer", "✦  Resume Builder"])

# ══════════════════════════════════════════════════════════
#  TAB 1 — ANALYZER
# ══════════════════════════════════════════════════════════

with tabs[0]:

    st.markdown('<span class="section-label">Step 1 — Job Description</span>', unsafe_allow_html=True)
    jd = st.text_area("Job Description", height=160,
                       placeholder="Paste the full job description here...",
                       label_visibility="collapsed")

    st.markdown('<span class="section-label" style="margin-top:1.2rem;display:block;">Step 2 — Your Resume</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], label_visibility="collapsed")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    analyze = st.button("🔍  Scan Resume")

    if analyze:
        try:
            if uploaded_file is None:
                st.warning("Please upload your resume first."); st.stop()
            if jd.strip() == "":
                st.warning("Please paste a job description."); st.stop()

            with st.spinner("Analysing your resume with AI..."):
                text = extract_pdf_text(uploaded_file)
                if not text or len(text.strip()) < 50:
                    st.error("Could not extract text from the PDF. Try a different file."); st.stop()
                res_skills = extract_keywords(text)
                jd_skills  = extract_keywords(jd)
                match, missing  = calculate_match(res_skills, jd_skills)
                ats_score, issues = ats_check(text, jd)
                feedback   = ai_feedback(text)

            overall = int((ats_score + match) / 2)

            if overall >= 70:
                ring_bg="linear-gradient(135deg,#10b981,#34d399)"; ring_sh="rgba(16,185,129,0.42)"
                banner_bg="linear-gradient(135deg,#ecfdf5,#d1fae5)"; banner_bd="#6ee7b7"; txt="#065f46"
                verdict="🎉 Great work! Your resume is well-optimised."
            elif overall >= 50:
                ring_bg="linear-gradient(135deg,#f59e0b,#fbbf24)"; ring_sh="rgba(245,158,11,0.42)"
                banner_bg="linear-gradient(135deg,#fffbeb,#fef3c7)"; banner_bd="#fde68a"; txt="#92400e"
                verdict="⚡ Good start! A few tweaks and you'll be interview-ready."
            else:
                ring_bg="linear-gradient(135deg,#ef4444,#f87171)"; ring_sh="rgba(239,68,68,0.42)"
                banner_bg="linear-gradient(135deg,#fff1f2,#fee2e2)"; banner_bd="#fca5a5"; txt="#991b1b"
                verdict="📋 Needs work — follow the recommendations below."

            # Score Banner
            st.markdown(f"""
            <div class="card-animate" style="background:{banner_bg}; border:2px solid {banner_bd};
                 border-radius:20px; padding:1.5rem 2rem; margin:1.5rem 0;
                 display:flex; align-items:center; gap:22px;
                 box-shadow:0 8px 32px {ring_sh.replace('0.42','0.1')};">
                <div class="score-ring" style="background:{ring_bg}; color:#fff;
                     font-family:'Inter',sans-serif; font-weight:900; font-size:1.75rem;
                     width:78px; height:78px; border-radius:50%;
                     display:flex; align-items:center; justify-content:center;
                     flex-shrink:0; box-shadow:0 8px 24px {ring_sh}; letter-spacing:-2px;">
                    {overall}
                </div>
                <div>
                    <p style="font-family:'Inter',sans-serif; font-weight:800; font-size:1.1rem;
                       color:{txt}; margin:0 0 4px; -webkit-text-fill-color:{txt};">
                        Your resume scored {overall} / 100
                    </p>
                    <p style="font-family:'Inter',sans-serif; font-size:0.88rem;
                       color:{txt}; margin:0; opacity:0.75; -webkit-text-fill-color:{txt};">
                        {verdict}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Metric Cards
            col1, col2 = st.columns(2)
            col1.metric("ATS Score", f"{ats_score} / 100")
            col2.metric("JD Match",  f"{match}%")

            # Animated Bars
            ac = "#10b981" if ats_score >= 70 else "#f59e0b" if ats_score >= 50 else "#ef4444"
            mc = "#6366f1" if match >= 60 else "#f59e0b" if match >= 40 else "#ef4444"

            st.markdown(f"""
            <div class="card-animate" style="background:#fff; border:2px solid #f1f5f9;
                 border-radius:18px; padding:1.4rem 1.8rem; margin:0.75rem 0;
                 box-shadow:0 4px 20px rgba(0,0,0,0.05);">
                <div style="margin-bottom:20px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:10px;height:10px;border-radius:50%;background:{ac};box-shadow:0 0 8px {ac};"></div>
                            <span style="font-family:'Inter',sans-serif;font-size:0.85rem;font-weight:600;color:#374151;">ATS Compatibility</span>
                        </div>
                        <span style="font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:800;color:{ac};">{ats_score}%</span>
                    </div>
                    <div style="height:10px;background:#f1f5f9;border-radius:99px;overflow:hidden;">
                        <div class="bar-animated" style="width:{ats_score}%;height:100%;
                             background:linear-gradient(90deg,{ac}88,{ac});
                             border-radius:99px;box-shadow:0 2px 8px {ac}55;"></div>
                    </div>
                </div>
                <div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:10px;height:10px;border-radius:50%;background:{mc};box-shadow:0 0 8px {mc};"></div>
                            <span style="font-family:'Inter',sans-serif;font-size:0.85rem;font-weight:600;color:#374151;">Job Description Match</span>
                        </div>
                        <span style="font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:800;color:{mc};">{match}%</span>
                    </div>
                    <div style="height:10px;background:#f1f5f9;border-radius:99px;overflow:hidden;">
                        <div class="bar-animated" style="width:{match}%;height:100%;
                             background:linear-gradient(90deg,{mc}88,{mc});
                             border-radius:99px;box-shadow:0 2px 8px {mc}55;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            if issues:
                st.markdown('<span class="section-label" style="margin-top:1.5rem;display:block;">Recommendations</span>', unsafe_allow_html=True)
                for idx, issue in enumerate(issues, 1):
                    sc = "#ef4444" if idx<=2 else "#f59e0b" if idx<=5 else "#6366f1"
                    sb = "#fff1f2" if idx<=2 else "#fffbeb" if idx<=5 else "#f5f3ff"
                    sd = "#fca5a5" if idx<=2 else "#fde68a" if idx<=5 else "#c4b5fd"
                    st.markdown(f"""
                    <div class="card-animate" style="display:flex;align-items:flex-start;gap:14px;
                         background:#fff;border:1.5px solid {sd};border-left:4px solid {sc};
                         border-radius:12px;padding:14px 16px;margin-bottom:10px;
                         box-shadow:0 2px 10px {sc}18;">
                        <div style="background:{sb};color:{sc};font-family:'Inter',sans-serif;
                             font-weight:800;font-size:0.72rem;min-width:26px;height:26px;
                             border-radius:8px;display:flex;align-items:center;justify-content:center;
                             flex-shrink:0;border:1.5px solid {sd};">{idx}</div>
                        <p style="font-family:'Inter',sans-serif;font-size:0.875rem;color:#374151;
                           -webkit-text-fill-color:#374151;margin:0;line-height:1.55;padding-top:2px;">
                           {issue}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Missing Skills
            if missing:
                st.markdown('<span class="section-label" style="margin-top:1.5rem;display:block;">Missing Skills</span>', unsafe_allow_html=True)
                chips = "".join([
                    f"""<span style="display:inline-flex;align-items:center;gap:5px;
                        background:linear-gradient(135deg,#f5f3ff,#ede9fe);
                        border:1.5px solid #c4b5fd;color:#5b21b6;
                        -webkit-text-fill-color:#5b21b6;
                        font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:600;
                        padding:5px 14px;border-radius:99px;margin:4px;
                        box-shadow:0 2px 8px rgba(124,58,237,0.12);">
                        <span style="width:6px;height:6px;border-radius:50%;background:#7c3aed;display:inline-block;"></span>
                        {s}</span>"""
                    for s in missing
                ])
                st.markdown(f"<div style='margin-top:6px;line-height:2.4;'>{chips}</div>", unsafe_allow_html=True)

            # AI Feedback
            st.markdown('<span class="section-label" style="margin-top:1.5rem;display:block;">AI Feedback</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card-animate" style="background:#fff;border:2px solid #f1f5f9;
                 border-radius:18px;padding:1.5rem 1.8rem;margin-top:0.25rem;
                 box-shadow:0 4px 20px rgba(0,0,0,0.05);border-top:4px solid #6366f1;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="width:32px;height:32px;border-radius:10px;
                         background:linear-gradient(135deg,#6366f1,#8b5cf6);
                         display:flex;align-items:center;justify-content:center;font-size:0.9rem;">✨</div>
                    <span style="font-family:'Inter',sans-serif;font-weight:700;font-size:0.9rem;
                           color:#1e1b4b;-webkit-text-fill-color:#1e1b4b;">Gemini AI Suggestions</span>
                </div>
                <p style="font-family:'Inter',sans-serif;font-size:0.875rem;color:#374151;
                   -webkit-text-fill-color:#374151;line-height:1.85;margin:0;
                   white-space:pre-wrap;">{feedback}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# ══════════════════════════════════════════════════════════
#  TAB 2 — BUILDER
# ══════════════════════════════════════════════════════════

with tabs[1]:

    st.markdown('<span class="section-label">Your Details</span>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        name  = st.text_input("Full Name",  placeholder="Ishita")
    with col_b:
        email = st.text_input("Email",      placeholder="ishita@email.com")
    with col_c:
        phone = st.text_input("Phone",      placeholder="+91 98765 43210")

    st.markdown('<span class="section-label" style="margin-top:1.4rem;display:block;">Resume Content</span>', unsafe_allow_html=True)
    skills = st.text_area("Skills",     placeholder="Python, React, AWS, Docker, SQL...", height=80)
    exp    = st.text_area("Experience", placeholder="Software Engineer @ Company (2022–Present)\n— Built X, reduced Y by 40%, led a team of 5", height=110)
    proj   = st.text_area("Projects",   placeholder="Project Name: Description, tech stack, impact...", height=90)
    edu    = st.text_area("Education",  placeholder="B.Tech Computer Science — IIT Delhi, 2022", height=70)

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

    word_count = len([w for w in preview.split() if w.strip()])
    wc_color   = "#10b981" if 400 <= word_count <= 900 else "#f59e0b"
    wc_label   = "✓ Perfect length" if 400 <= word_count <= 900 else "Aim for 400–900 words"

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin:1.2rem 0 4px;">
        <span style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:700;
               color:#6366f1;letter-spacing:2px;text-transform:uppercase;">Live Preview</span>
        <span style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;
               color:{wc_color};-webkit-text-fill-color:{wc_color};
               background:{wc_color}18;padding:3px 12px;border-radius:99px;
               border:1.5px solid {wc_color}44;">
            {word_count} words · {wc_label}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.code(preview, language=None)

    if st.button("⬇  Generate Resume"):
        doc = Document()
        for line in preview.split("\n"):
            doc.add_paragraph(line)
        doc.save("resume.docx")
        pdf_file = export_pdf(preview)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);
             border:2px solid #6ee7b7;border-radius:14px;padding:14px 18px;margin:10px 0;
             display:flex;align-items:center;gap:12px;
             box-shadow:0 4px 16px rgba(16,185,129,0.15);">
            <span style="font-size:1.3rem;">🎉</span>
            <p style="font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:700;
               color:#065f46;-webkit-text-fill-color:#065f46;margin:0;">
                Resume compiled! Download your files below.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            with open("resume.docx","rb") as f:
                st.download_button("📄  Download DOCX", f, "resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with col_dl2:
            with open(pdf_file,"rb") as f:
                st.download_button("📑  Download PDF", f, "resume.pdf", mime="application/pdf")