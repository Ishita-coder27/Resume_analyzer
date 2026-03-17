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

# ══════════════════════════════════════════════════════════
#  CSS — only styling native Streamlit elements
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#MainMenu {visibility:hidden;}
footer    {visibility:hidden;}
header    {visibility:hidden;}

/* Page background */
.stApp, [data-testid="stAppViewContainer"] {
    background: #f0f2f8 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="block-container"] {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
}

/* ── All text black by default ── */
*, *::before, *::after {
    font-family: 'Inter', sans-serif !important;
}
p, span, div, label {
    color: #111827 !important;
}

/* ── h1 title ── */
h1 {
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    color: #111827 !important;
    letter-spacing: -1.5px !important;
    line-height: 1.1 !important;
    margin-bottom: 0 !important;
}

/* ── h2 used as section labels ── */
h2 {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    color: #6366f1 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    border: none !important;
    margin: 1.6rem 0 0.4rem !important;
}

/* ── h3 subheadings ── */
h3 {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
    border: none !important;
    margin: 1rem 0 0.4rem !important;
    letter-spacing: -0.2px !important;
    text-transform: none !important;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #d1d5db !important;
    gap: 0 !important;
    margin-bottom: 1.5rem !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #6b7280 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    clip-path: none !important;
    border-radius: 0 !important;
    transition: color 0.2s !important;
}
[data-baseweb="tab"]:hover { color: #4f46e5 !important; }
[aria-selected="true"][data-baseweb="tab"] {
    color: #4f46e5 !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #4f46e5 !important;
}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] { display: none !important; }

/* ── INPUTS & TEXTAREAS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: #ffffff !important;
    border: 2px solid #e5e7eb !important;
    border-left: 2px solid #e5e7eb !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.1) !important;
    transform: translateY(-1px) !important;
}
input, textarea {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    background: transparent !important;
    font-size: 0.9rem !important;
}
textarea::placeholder, input::placeholder {
    color: #9ca3af !important;
    -webkit-text-fill-color: #9ca3af !important;
}
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px dashed #a5b4fc !important;
    border-left: 2px dashed #a5b4fc !important;
    border-radius: 14px !important;
    transition: all 0.25s !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #6366f1 !important;
    background: #fafafe !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.1) !important;
}
[data-testid="stFileUploader"] section > div > div > span,
[data-testid="stFileUploader"] section small {
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
}
[data-testid="stFileUploader"] button {
    background: #6366f1 !important;
    border: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    clip-path: none !important;
    box-shadow: 0 3px 10px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #4f46e5 !important;
    box-shadow: 0 6px 18px rgba(99,102,241,0.45) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stFileUploader"] button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stFileUploader"] label p {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.75rem 2.5rem !important;
    border-radius: 99px !important;
    clip-path: none !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.4) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin-top: 0.5rem !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.04) !important;
    box-shadow: 0 14px 36px rgba(79,70,229,0.5) !important;
}
.stButton > button:active {
    transform: translateY(-1px) scale(0.98) !important;
}
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 2px solid #e5e7eb !important;
    border-top: 4px solid #6366f1 !important;
    border-radius: 16px !important;
    padding: 1.3rem !important;
    box-shadow: 0 3px 14px rgba(99,102,241,0.07) !important;
    transition: all 0.25s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 14px 32px rgba(99,102,241,0.15) !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 2.1rem !important;
    font-weight: 900 !important;
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
    letter-spacing: -1px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
    font-weight: 500 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #fffbeb !important;
    border: 1.5px solid #fde68a !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p {
    color: #92400e !important;
    -webkit-text-fill-color: #92400e !important;
    font-size: 0.85rem !important;
}

/* ── CODE BLOCK (builder preview) ── */
.stCode > pre {
    background: #fafaff !important;
    border: 2px solid #e5e7eb !important;
    border-left: 4px solid #6366f1 !important;
    border-radius: 14px !important;
}
.stCode > pre > code,
.stCode > pre > code * {
    color: #3730a3 !important;
    -webkit-text-fill-color: #3730a3 !important;
    font-size: 0.8rem !important;
}

/* ── DOWNLOAD BUTTONS ── */
[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    border: 2px solid #6366f1 !important;
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    clip-path: none !important;
    padding: 0.65rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.1) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border-color: transparent !important;
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 10px 28px rgba(79,70,229,0.35) !important;
}
[data-testid="stDownloadButton"] > button:hover * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stDownloadButton"] > button * {
    color: #4f46e5 !important;
    -webkit-text-fill-color: #4f46e5 !important;
}

/* ── MARKDOWN TEXT ── */
[data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem !important;
    line-height: 1.75 !important;
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes popIn {
    0%   { transform: scale(0.5); opacity: 0; }
    70%  { transform: scale(1.08); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes growBar { from { width: 0%; } }

.fade-up   { animation: fadeUp  0.45s cubic-bezier(0.4,0,0.2,1) forwards; }
.pop-in    { animation: popIn   0.6s  cubic-bezier(0.34,1.56,0.64,1) forwards; }
.grow-bar  { animation: growBar 1.2s  cubic-bezier(0.4,0,0.2,1) forwards; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #a5b4fc; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HEADER — pure Streamlit markdown, white on light bg
# ══════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom:0.3rem;">
  <span style="font-size:0.68rem; font-weight:700; letter-spacing:3px;
        text-transform:uppercase; color:#6366f1;">
    AI POWERED &nbsp;·&nbsp; FREE &nbsp;·&nbsp; INSTANT RESULTS
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="font-size:2.8rem; font-weight:900; color:#111827;
    letter-spacing:-2px; line-height:1.05; margin:0 0 0.5rem;">
  Acadence <span style="color:#6366f1;">Resume Lab</span>
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="font-size:1rem; color:#4b5563; max-width:520px;
   line-height:1.65; margin-bottom:1.5rem;">
  Score your resume against real recruiter criteria.
  Get actionable fixes and land more interviews.
</p>
""", unsafe_allow_html=True)

# feature pills row
st.markdown("""
<div style="display:flex; gap:10px; margin-bottom:2rem; flex-wrap:wrap;">
  <div style="display:inline-flex; align-items:center; gap:7px;
       background:#fff; border:1.5px solid #e5e7eb; border-radius:99px;
       padding:6px 16px; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <span style="font-size:0.9rem;">🧠</span>
    <span style="font-size:0.78rem; font-weight:600; color:#374151;">AI-Powered Insights</span>
  </div>
  <div style="display:inline-flex; align-items:center; gap:7px;
       background:#fff; border:1.5px solid #e5e7eb; border-radius:99px;
       padding:6px 16px; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <span style="font-size:0.9rem;">⚡</span>
    <span style="font-size:0.78rem; font-weight:600; color:#374151;">Instant Analysis</span>
  </div>
  <div style="display:inline-flex; align-items:center; gap:7px;
       background:#fff; border:1.5px solid #e5e7eb; border-radius:99px;
       padding:6px 16px; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <span style="font-size:0.9rem;">🎯</span>
    <span style="font-size:0.78rem; font-weight:600; color:#374151;">ATS Optimised</span>
  </div>
  <div style="display:inline-flex; align-items:center; gap:7px;
       background:#fff; border:1.5px solid #e5e7eb; border-radius:99px;
       padding:6px 16px; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <span style="width:8px; height:8px; background:#22c55e; border-radius:50%;
          display:inline-block; box-shadow:0 0 6px #22c55e;"></span>
    <span style="font-size:0.78rem; font-weight:600; color:#374151;">AI Engine Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════
#  FUNCTIONS
# ══════════════════════════════════════════════════════════

def extract_pdf_text(uploaded_file):
    if uploaded_file is None:
        st.error("No file uploaded."); return ""
    try:
        reader = pdf.PdfReader(uploaded_file); text = ""
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
        st.error(f"Failed to read PDF: {e}"); return ""

def extract_keywords(text):
    skills = ["python","java","c++","javascript","react","node","docker","kubernetes",
              "mongodb","sql","aws","machine learning","tensorflow","pytorch",
              "data structures","algorithms","rest api"]
    return [s for s in skills if s in text.lower()]

def calculate_match(resume_skills, jd_skills):
    if not jd_skills: return 0, []
    matched = set(resume_skills) & set(jd_skills)
    return int(len(matched)/len(jd_skills)*100), list(set(jd_skills)-set(resume_skills))

def ats_check(resume_text, jd):
    text = resume_text.lower(); score = 100; issues = []
    for sec in ["education","experience","skills","projects"]:
        if sec not in text: score -= 12; issues.append(f"Missing section: {sec}")
    words = len(resume_text.split())
    if words < 400:    score -= 25; issues.append("Too short (under 400 words)")
    elif words > 900:  score -= 12; issues.append("Too long (over 900 words)")
    bullets = resume_text.count("•") + resume_text.count("-")
    if bullets < 5:    score -= 15; issues.append("Very few bullet points")
    elif bullets < 10: score -= 8;  issues.append("Not enough bullet points")
    verbs = ["developed","built","designed","implemented","optimized","created",
             "engineered","improved","automated","led","managed","architected","analyzed"]
    vc = sum(1 for v in verbs if v in text)
    if vc < 3:   score -= 15; issues.append("Weak action verbs — use Built, Led, Optimized etc.")
    elif vc < 6: score -= 8
    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15; issues.append("No quantified achievements — add numbers like 40%, 2x, 500+")
    if "|" in resume_text:                score -= 12; issues.append("Tables/pipes detected — risky for ATS parsing")
    if len(resume_text.split("\n")) < 15: score -= 10; issues.append("Poor structure or spacing")
    if "@" not in resume_text:            score -= 5;  issues.append("Missing contact email")
    jd_words = re.findall(r"[a-zA-Z]{4,}", jd.lower())
    if jd_words:
        ks = sum(1 for w in jd_words if w in text)/len(jd_words)
        if ks < 0.2:   score -= 25; issues.append("Very low keyword match with job description")
        elif ks < 0.4: score -= 18; issues.append("Low keyword match with job description")
        elif ks < 0.6: score -= 10; issues.append("Moderate keyword match — room to improve")
    rs = extract_keywords(resume_text); js = extract_keywords(jd)
    if js:
        sr = len(set(rs)&set(js))/len(js)
        if sr < 0.3:   score -= 20; issues.append("Very low skill match with job description")
        elif sr < 0.6: score -= 10; issues.append("Partial skill match with job description")
    if text.count("project")>12 or text.count("experience")>12:
        score -= 8; issues.append("Possible keyword stuffing detected")
    if "responsible for" in text:
        score -= 8; issues.append("Avoid 'responsible for' — use impact-focused language instead")
    return max(0, min(88, score)), issues

def ai_feedback(resume_text):
    try:
        r = MODEL.generate_content(f"Improve this resume:\n{resume_text[:2000]}"); return r.text
    except Exception as e: return f"Gemini Error: {str(e)}"

def export_pdf(content):
    file = "resume.pdf"; c = canvas.Canvas(file); y = 800
    for line in content.split("\n"): c.drawString(40, y, line); y -= 20
    c.save(); return file


# ══════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════

tab1, tab2 = st.tabs(["  Resume Analyzer  ", "  Resume Builder  "])

# ──────────────────────────────────────────────────────────
#  TAB 1 — ANALYZER
# ──────────────────────────────────────────────────────────
with tab1:

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        # Step card
        st.markdown("""
        <div style="background:#ffffff; border:2px solid #e5e7eb; border-radius:16px;
             padding:18px 20px 10px; box-shadow:0 2px 12px rgba(0,0,0,0.05);
             margin-bottom:8px;">
          <div style="display:flex; align-items:center; justify-content:space-between;
               margin-bottom:10px;">
            <div style="display:flex; align-items:center; gap:10px;">
              <div style="width:34px; height:34px; border-radius:10px;
                   background:linear-gradient(135deg,#ede9fe,#ddd6fe);
                   display:flex; align-items:center; justify-content:center; font-size:1rem;">📋</div>
              <span style="font-size:0.72rem; font-weight:800; color:#1e1b4b;
                    letter-spacing:1.5px; text-transform:uppercase;">STEP 1 — JOB DESCRIPTION</span>
            </div>
            <span style="font-size:0.72rem; font-weight:500; color:#6366f1;">ⓘ Help</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        jd = st.text_area(
            "Job Description", height=200,
            placeholder='e.g., "Software Engineer with 5+ years of Python experience..."',
            label_visibility="collapsed"
        )
        st.markdown(f"""
        <p style="text-align:right; font-size:0.72rem; color:#9ca3af;
           margin-top:-8px;">{len(jd)} / 10000</p>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="background:#ffffff; border:2px solid #e5e7eb; border-radius:16px;
             padding:18px 20px 10px; box-shadow:0 2px 12px rgba(0,0,0,0.05);
             margin-bottom:8px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <div style="width:34px; height:34px; border-radius:10px;
                 background:linear-gradient(135deg,#e0f2fe,#bae6fd);
                 display:flex; align-items:center; justify-content:center; font-size:1rem;">📄</div>
            <span style="font-size:0.72rem; font-weight:800; color:#1e1b4b;
                  letter-spacing:1.5px; text-transform:uppercase;">STEP 2 — YOUR RESUME</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload PDF", type=["pdf"],
            label_visibility="collapsed"
        )

    # Centered scan button
    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        analyze = st.button("🔍   Scan Resume", use_container_width=True)

    # ── RESULTS ──────────────────────────────────────────
    if analyze:
        try:
            if uploaded_file is None:
                st.warning("Please upload your resume first."); st.stop()
            if jd.strip() == "":
                st.warning("Please paste a job description."); st.stop()

            with st.spinner("Analysing your resume with AI..."):
                text = extract_pdf_text(uploaded_file)
                if not text or len(text.strip()) < 50:
                    st.error("Could not extract text. Try a different PDF."); st.stop()
                res_skills        = extract_keywords(text)
                jd_skills         = extract_keywords(jd)
                match, missing    = calculate_match(res_skills, jd_skills)
                ats_score, issues = ats_check(text, jd)
                feedback          = ai_feedback(text)

            overall = int((ats_score + match) / 2)

            # Score colours
            if overall >= 70:
                ring_bg = "linear-gradient(135deg,#10b981,#34d399)"
                ring_sh = "rgba(16,185,129,0.4)"
                ban_bg  = "#ecfdf5"; ban_bd = "#6ee7b7"; ban_txt = "#065f46"
                verdict = "🎉 Great work! Your resume is well-optimised."
            elif overall >= 50:
                ring_bg = "linear-gradient(135deg,#f59e0b,#fbbf24)"
                ring_sh = "rgba(245,158,11,0.4)"
                ban_bg  = "#fffbeb"; ban_bd = "#fde68a"; ban_txt = "#92400e"
                verdict = "⚡ Good start — a few tweaks and you'll be interview-ready."
            else:
                ring_bg = "linear-gradient(135deg,#ef4444,#f87171)"
                ring_sh = "rgba(239,68,68,0.4)"
                ban_bg  = "#fff1f2"; ban_bd = "#fca5a5"; ban_txt = "#991b1b"
                verdict = "📋 Needs work — follow the recommendations below."

            st.markdown(f"""
            <div class="fade-up" style="background:{ban_bg}; border:2px solid {ban_bd};
                 border-radius:20px; padding:1.4rem 1.8rem; margin:1.5rem 0;
                 display:flex; align-items:center; gap:20px;
                 box-shadow:0 6px 24px {ring_sh.replace('0.4','0.1')};">
              <div class="pop-in" style="background:{ring_bg}; color:#fff; font-weight:900;
                   font-size:1.75rem; width:76px; height:76px; border-radius:50%; flex-shrink:0;
                   display:flex; align-items:center; justify-content:center;
                   box-shadow:0 6px 20px {ring_sh}; letter-spacing:-2px;">{overall}</div>
              <div>
                <p style="font-weight:800; font-size:1.1rem; color:{ban_txt};
                   -webkit-text-fill-color:{ban_txt}; margin:0 0 3px;">
                   Your resume scored {overall} / 100</p>
                <p style="font-size:0.88rem; color:{ban_txt}; -webkit-text-fill-color:{ban_txt};
                   margin:0; opacity:0.78;">{verdict}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2 = st.columns(2)
            m1.metric("ATS Score",  f"{ats_score} / 100")
            m2.metric("JD Match",   f"{match}%")

            # Bars
            ac = "#10b981" if ats_score>=70 else "#f59e0b" if ats_score>=50 else "#ef4444"
            mc = "#6366f1" if match>=60    else "#f59e0b" if match>=40    else "#ef4444"

            st.markdown(f"""
            <div class="fade-up" style="background:#fff; border:2px solid #f0f2f8;
                 border-radius:16px; padding:1.3rem 1.6rem; margin:0.6rem 0;
                 box-shadow:0 3px 14px rgba(0,0,0,0.05);">

              <div style="margin-bottom:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:7px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:9px; height:9px; border-radius:50%;
                         background:{ac}; box-shadow:0 0 7px {ac};"></div>
                    <span style="font-size:0.83rem; font-weight:600; color:#374151;">ATS Compatibility</span>
                  </div>
                  <span style="font-size:0.88rem; font-weight:800; color:{ac};">{ats_score}%</span>
                </div>
                <div style="height:9px; background:#f1f5f9; border-radius:99px; overflow:hidden;">
                  <div class="grow-bar" style="width:{ats_score}%; height:100%;
                       background:linear-gradient(90deg,{ac}88,{ac}); border-radius:99px;
                       box-shadow:0 2px 6px {ac}55;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:7px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:9px; height:9px; border-radius:50%;
                         background:{mc}; box-shadow:0 0 7px {mc};"></div>
                    <span style="font-size:0.83rem; font-weight:600; color:#374151;">Job Description Match</span>
                  </div>
                  <span style="font-size:0.88rem; font-weight:800; color:{mc};">{match}%</span>
                </div>
                <div style="height:9px; background:#f1f5f9; border-radius:99px; overflow:hidden;">
                  <div class="grow-bar" style="width:{match}%; height:100%;
                       background:linear-gradient(90deg,{mc}88,{mc}); border-radius:99px;
                       box-shadow:0 2px 6px {mc}55;"></div>
                </div>
              </div>

            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            if issues:
                st.markdown("""
                <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
                   letter-spacing:2.5px; text-transform:uppercase;
                   margin:1.4rem 0 0.6rem;">Recommendations</p>
                """, unsafe_allow_html=True)
                for idx, issue in enumerate(issues, 1):
                    sc = "#ef4444" if idx<=2 else "#f59e0b" if idx<=5 else "#6366f1"
                    sb = "#fff1f2" if idx<=2 else "#fffbeb" if idx<=5 else "#f5f3ff"
                    sd = "#fca5a5" if idx<=2 else "#fde68a" if idx<=5 else "#c4b5fd"
                    st.markdown(f"""
                    <div class="fade-up" style="display:flex; align-items:flex-start; gap:12px;
                         background:#fff; border:1.5px solid {sd}; border-left:4px solid {sc};
                         border-radius:12px; padding:12px 15px; margin-bottom:9px;
                         box-shadow:0 2px 8px {sc}16;">
                      <div style="background:{sb}; color:{sc}; font-weight:800; font-size:0.7rem;
                           min-width:24px; height:24px; border-radius:7px; flex-shrink:0;
                           display:flex; align-items:center; justify-content:center;
                           border:1.5px solid {sd};">{idx}</div>
                      <p style="font-size:0.86rem; color:#374151;
                         -webkit-text-fill-color:#374151; margin:0; line-height:1.55;
                         padding-top:1px;">{issue}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Missing skills
            if missing:
                st.markdown("""
                <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
                   letter-spacing:2.5px; text-transform:uppercase;
                   margin:1.4rem 0 0.5rem;">Missing Skills</p>
                """, unsafe_allow_html=True)
                chips = "".join([
                    f'<span style="display:inline-flex; align-items:center; gap:5px;'
                    f'background:linear-gradient(135deg,#f5f3ff,#ede9fe);'
                    f'border:1.5px solid #c4b5fd; color:#5b21b6;'
                    f'-webkit-text-fill-color:#5b21b6;'
                    f'font-size:0.77rem; font-weight:600;'
                    f'padding:5px 13px; border-radius:99px; margin:3px;'
                    f'box-shadow:0 2px 6px rgba(124,58,237,0.1);">'
                    f'<span style="width:5px;height:5px;border-radius:50%;'
                    f'background:#7c3aed;display:inline-block;"></span>{s}</span>'
                    for s in missing
                ])
                st.markdown(f"<div style='line-height:2.4;'>{chips}</div>", unsafe_allow_html=True)

            # AI Feedback
            st.markdown("""
            <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
               letter-spacing:2.5px; text-transform:uppercase;
               margin:1.4rem 0 0.5rem;">AI Feedback</p>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fade-up" style="background:#fff; border:2px solid #f0f2f8;
                 border-top:4px solid #6366f1; border-radius:16px;
                 padding:1.4rem 1.7rem; box-shadow:0 4px 16px rgba(0,0,0,0.05);">
              <div style="display:flex; align-items:center; gap:9px; margin-bottom:10px;">
                <div style="width:30px; height:30px; border-radius:9px;
                     background:linear-gradient(135deg,#6366f1,#8b5cf6);
                     display:flex; align-items:center; justify-content:center;
                     font-size:0.85rem;">✨</div>
                <span style="font-weight:700; font-size:0.88rem; color:#1e1b4b;
                      -webkit-text-fill-color:#1e1b4b;">Gemini AI Suggestions</span>
              </div>
              <p style="font-size:0.86rem; color:#374151; -webkit-text-fill-color:#374151;
                 line-height:1.85; margin:0; white-space:pre-wrap;">{feedback}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")


# ──────────────────────────────────────────────────────────
#  TAB 2 — BUILDER
# ──────────────────────────────────────────────────────────
with tab2:

    st.markdown("""
    <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
       letter-spacing:2.5px; text-transform:uppercase; margin-bottom:0.5rem;">
       Your Details</p>
    """, unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    with ca: name  = st.text_input("Full Name",  placeholder="Ishita")
    with cb: email = st.text_input("Email",      placeholder="ishita@email.com")
    with cc: phone = st.text_input("Phone",      placeholder="+91 98765 43210")

    st.markdown("""
    <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
       letter-spacing:2.5px; text-transform:uppercase;
       margin:1.4rem 0 0.4rem;">Resume Content</p>
    """, unsafe_allow_html=True)

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
    wc   = len([w for w in preview.split() if w.strip()])
    wcc  = "#10b981" if 400<=wc<=900 else "#f59e0b"
    wcl  = "✓ Perfect length" if 400<=wc<=900 else "Aim for 400–900 words"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
         margin:1.3rem 0 4px;">
      <p style="font-size:0.68rem; font-weight:700; color:#6366f1;
         letter-spacing:2.5px; text-transform:uppercase; margin:0;">Live Preview</p>
      <span style="font-size:0.74rem; font-weight:600; color:{wcc};
            -webkit-text-fill-color:{wcc}; background:{wcc}18;
            padding:3px 11px; border-radius:99px; border:1.5px solid {wcc}44;">
        {wc} words · {wcl}
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.code(preview, language=None)

    _, gc, _ = st.columns([2, 2, 2])
    with gc:
        if st.button("⬇   Generate Resume", use_container_width=True):
            doc = Document()
            for line in preview.split("\n"):
                doc.add_paragraph(line)
            doc.save("resume.docx")
            pdf_file = export_pdf(preview)

            st.markdown("""
            <div style="background:#ecfdf5; border:2px solid #6ee7b7; border-radius:14px;
                 padding:12px 16px; margin:10px 0; display:flex; align-items:center; gap:10px;
                 box-shadow:0 3px 12px rgba(16,185,129,0.12);">
              <span style="font-size:1.2rem;">🎉</span>
              <p style="font-size:0.88rem; font-weight:700; color:#065f46;
                 -webkit-text-fill-color:#065f46; margin:0;">
                 Resume compiled! Download your files below.</p>
            </div>
            """, unsafe_allow_html=True)

            d1, d2 = st.columns(2)
            with d1:
                with open("resume.docx","rb") as f:
                    st.download_button("📄  Download DOCX", f, "resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with d2:
                with open(pdf_file,"rb") as f:
                    st.download_button("📑  Download PDF", f, "resume.pdf", mime="application/pdf")