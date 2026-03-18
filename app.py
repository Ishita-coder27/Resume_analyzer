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
#  CSS — DARK THEME
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#MainMenu {visibility:hidden;}
footer    {visibility:hidden;}
header    {visibility:hidden;}

/* ── Page background ── */
.stApp,
[data-testid="stAppViewContainer"] {
    background: #0d0f14 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="block-container"] {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
}

/* ── Base text ── */
*, *::before, *::after { font-family: 'Inter', sans-serif !important; }
p, span, div, label    { color: #e2e8f0 !important; }

/* ── Headings ── */
h1 {
    font-size: 2.7rem !important; font-weight: 900 !important;
    color: #f8fafc !important; letter-spacing: -2px !important;
    line-height: 1.05 !important; margin-bottom: 0 !important;
}
h2 {
    font-size: 0.65rem !important; font-weight: 700 !important;
    color: #818cf8 !important; letter-spacing: 2.5px !important;
    text-transform: uppercase !important; border: none !important;
    margin: 1.6rem 0 0.4rem !important;
}
h3 {
    font-size: 1rem !important; font-weight: 700 !important;
    color: #f1f5f9 !important; border: none !important;
    margin: 1rem 0 0.4rem !important; letter-spacing: -0.2px !important;
    text-transform: none !important;
}

/* ── Divider ── */
hr { border-color: #1e2433 !important; }

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #1e2433 !important;
    gap: 0 !important; margin-bottom: 1.5rem !important;
}
[data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    color: #64748b !important; font-size: 0.9rem !important;
    font-weight: 500 !important; padding: 10px 22px !important;
    clip-path: none !important; border-radius: 0 !important;
    transition: color 0.2s !important;
}
[data-baseweb="tab"]:hover { color: #a5b4fc !important; }
[aria-selected="true"][data-baseweb="tab"] {
    color: #818cf8 !important; font-weight: 700 !important;
    border-bottom: 3px solid #818cf8 !important;
}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] { display: none !important; }

/* ── INPUTS & TEXTAREAS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: #141720 !important;
    border: 1.5px solid #1e2433 !important;
    border-left: 1.5px solid #1e2433 !important;
    border-radius: 12px !important; transition: all 0.2s !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    transform: translateY(-1px) !important;
}
input, textarea {
    color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;
    background: transparent !important; font-size: 0.9rem !important;
    caret-color: #818cf8 !important;
}
textarea::placeholder, input::placeholder {
    color: #374151 !important; -webkit-text-fill-color: #374151 !important;
}
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-size: 0.8rem !important; font-weight: 600 !important;
    color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important;
    text-transform: none !important; letter-spacing: 0 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: #141720 !important;
    border: 2px dashed #2a3147 !important;
    border-left: 2px dashed #2a3147 !important;
    border-radius: 14px !important; transition: all 0.25s !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #6366f1 !important;
    background: #161b2e !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.15) !important;
}
[data-testid="stFileUploader"] section > div > div > span,
[data-testid="stFileUploader"] section small {
    color: #64748b !important; -webkit-text-fill-color: #64748b !important;
}
[data-testid="stFileUploader"] button {
    background: #6366f1 !important; border: none !important;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important; border-radius: 8px !important;
    clip-path: none !important;
    box-shadow: 0 3px 12px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #4f46e5 !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stFileUploader"] button * {
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stFileUploader"] label p {
    font-size: 0.8rem !important; font-weight: 600 !important;
    color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border: none !important; color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 0.95rem !important; font-weight: 700 !important;
    padding: 0.8rem 2.5rem !important; border-radius: 99px !important;
    clip-path: none !important;
    box-shadow: 0 6px 24px rgba(79,70,229,0.45) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin-top: 0.5rem !important; letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.04) !important;
    box-shadow: 0 14px 40px rgba(79,70,229,0.55) !important;
}
.stButton > button:active { transform: translateY(-1px) scale(0.98) !important; }
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #141720 !important;
    border: 1.5px solid #1e2433 !important;
    border-top: 3px solid #6366f1 !important;
    border-radius: 16px !important; padding: 1.3rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    transition: all 0.25s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    border-color: #6366f1 !important;
    box-shadow: 0 14px 36px rgba(99,102,241,0.2) !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 2.1rem !important; font-weight: 900 !important;
    color: #818cf8 !important; -webkit-text-fill-color: #818cf8 !important;
    letter-spacing: -1px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.7rem !important; font-weight: 600 !important;
    color: #64748b !important; -webkit-text-fill-color: #64748b !important;
    text-transform: uppercase !important; letter-spacing: 1.5px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: #818cf8 !important; -webkit-text-fill-color: #818cf8 !important;
    font-weight: 500 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #1c1610 !important;
    border: 1.5px solid #3d2e0a !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p {
    color: #fbbf24 !important; -webkit-text-fill-color: #fbbf24 !important;
    font-size: 0.85rem !important;
}

/* ── CODE BLOCK ── */
.stCode > pre {
    background: #0a0c11 !important;
    border: 1.5px solid #1e2433 !important;
    border-left: 4px solid #6366f1 !important;
    border-radius: 14px !important;
}
.stCode > pre > code,
.stCode > pre > code * {
    color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important;
    font-size: 0.8rem !important;
}

/* ── DOWNLOAD BUTTONS ── */
[data-testid="stDownloadButton"] > button {
    background: #141720 !important;
    border: 1.5px solid #6366f1 !important;
    color: #818cf8 !important; -webkit-text-fill-color: #818cf8 !important;
    font-weight: 700 !important; border-radius: 12px !important;
    clip-path: none !important; padding: 0.65rem 1.5rem !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.15) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border-color: transparent !important;
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 10px 30px rgba(79,70,229,0.4) !important;
}
[data-testid="stDownloadButton"] > button:hover * {
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stDownloadButton"] > button * {
    color: #818cf8 !important; -webkit-text-fill-color: #818cf8 !important;
}

/* ── MARKDOWN TEXT ── */
[data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem !important; line-height: 1.75 !important;
    color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes popIn {
    0%   { transform: scale(0.5); opacity: 0; }
    70%  { transform: scale(1.1); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes growBar { from { width: 0%; } }

.fade-up  { animation: fadeUp  0.45s cubic-bezier(0.4,0,0.2,1) forwards; }
.pop-in   { animation: popIn   0.6s  cubic-bezier(0.34,1.56,0.64,1) forwards; }
.grow-bar { animation: growBar 1.2s  cubic-bezier(0.4,0,0.2,1) forwards; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a3147; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════



st.markdown("""
<h1 style="font-size:2.8rem; font-weight:900; color:#f8fafc;
    letter-spacing:-2px; line-height:1.05; margin:0 0 0.5rem;">
  Acadence <span style="color:#818cf8;">Resume Lab</span>
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="font-size:0.98rem; color:#64748b; max-width:500px;
   line-height:1.65; margin-bottom:1.5rem;">
  Score your resume against real recruiter criteria.
  Get actionable fixes and land more interviews.
</p>
""", unsafe_allow_html=True)

# Feature pills
st.markdown("""
<div style="display:flex; gap:10px; margin-bottom:2rem; flex-wrap:wrap;">

  <div style="display:inline-flex; align-items:center; gap:8px;
       background:#141720; border:1.5px solid #1e2433; border-radius:99px;
       padding:6px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.3);">
    <div style="width:6px; height:6px; background:#22c55e; border-radius:50%;
         box-shadow:0 0 6px #22c55e;"></div>
    <span style="font-size:0.77rem; font-weight:600; color:#94a3b8;">AI Engine Online</span>
  </div>

  <div style="display:inline-flex; align-items:center; gap:8px;
       background:#141720; border:1.5px solid #1e2433; border-radius:99px;
       padding:6px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.3);">
    <div style="width:6px; height:6px; background:#818cf8; border-radius:50%;"></div>
    <span style="font-size:0.77rem; font-weight:600; color:#94a3b8;">Instant Analysis</span>
  </div>

  <div style="display:inline-flex; align-items:center; gap:8px;
       background:#141720; border:1.5px solid #1e2433; border-radius:99px;
       padding:6px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.3);">
    <div style="width:6px; height:6px; background:#38bdf8; border-radius:50%;"></div>
    <span style="font-size:0.77rem; font-weight:600; color:#94a3b8;">ATS Optimised</span>
  </div>

  <div style="display:inline-flex; align-items:center; gap:8px;
       background:#141720; border:1.5px solid #1e2433; border-radius:99px;
       padding:6px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.3);">
    <div style="width:6px; height:6px; background:#a78bfa; border-radius:50%;"></div>
    <span style="font-size:0.77rem; font-weight:600; color:#94a3b8;">AI-Powered Insights</span>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border:1px solid #1e2433; margin-bottom:0.5rem;">', unsafe_allow_html=True)

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
    if "|" in resume_text:
        score -= 12; issues.append("Tables/pipes detected — risky for ATS parsing")
    if len(resume_text.split("\n")) < 15:
        score -= 10; issues.append("Poor structure or spacing")
    if "@" not in resume_text:
        score -= 5; issues.append("Missing contact email")
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
        st.markdown("""
        <div style="background:#141720; border:1.5px solid #1e2433; border-radius:16px;
             padding:16px 18px 10px; margin-bottom:8px;
             box-shadow:0 4px 20px rgba(0,0,0,0.3);">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex; align-items:center; gap:10px;">
              <div style="width:32px; height:32px; border-radius:9px;
                   background:linear-gradient(135deg,#312e81,#4338ca);
                   display:flex; align-items:center; justify-content:center;">
                <div style="width:14px; height:14px; border:2px solid #a5b4fc;
                     border-radius:3px;"></div>
              </div>
              <span style="font-size:0.7rem; font-weight:800; color:#e2e8f0;
                    letter-spacing:1.5px; text-transform:uppercase;">
                    STEP 1 — JOB DESCRIPTION</span>
            </div>
            <span style="font-size:0.72rem; font-weight:500; color:#6366f1;
                  cursor:pointer;">Help</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        jd = st.text_area(
            "jd", height=200,
            placeholder='e.g., "Software Engineer with 5+ years of Python experience..."',
            label_visibility="collapsed"
        )
        st.markdown(f"""
        <p style="text-align:right; font-size:0.7rem; color:#334155;
           margin-top:-8px;">{len(jd)} / 10000</p>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="background:#141720; border:1.5px solid #1e2433; border-radius:16px;
             padding:16px 18px 10px; margin-bottom:8px;
             box-shadow:0 4px 20px rgba(0,0,0,0.3);">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; border-radius:9px;
                 background:linear-gradient(135deg,#0c4a6e,#0369a1);
                 display:flex; align-items:center; justify-content:center;">
              <div style="width:10px; height:13px; border:2px solid #7dd3fc;
                   border-radius:2px; position:relative;">
                <div style="position:absolute; top:-4px; right:-4px; width:6px; height:6px;
                     background:#7dd3fc; border-radius:50%;"></div>
              </div>
            </div>
            <span style="font-size:0.7rem; font-weight:800; color:#e2e8f0;
                  letter-spacing:1.5px; text-transform:uppercase;">
                  STEP 2 — YOUR RESUME</span>
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
        analyze = st.button("Scan Resume", use_container_width=True)

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

            if overall >= 70:
                ring_bg = "linear-gradient(135deg,#059669,#10b981)"
                ring_sh = "rgba(16,185,129,0.35)"
                ban_bg  = "#052e16"; ban_bd = "#064e3b"; ban_txt = "#6ee7b7"
                verdict = "Great work — your resume is well-optimised."
            elif overall >= 50:
                ring_bg = "linear-gradient(135deg,#b45309,#d97706)"
                ring_sh = "rgba(217,119,6,0.35)"
                ban_bg  = "#1c1407"; ban_bd = "#3d2e0a"; ban_txt = "#fcd34d"
                verdict = "Good start — a few tweaks and you will be interview-ready."
            else:
                ring_bg = "linear-gradient(135deg,#b91c1c,#ef4444)"
                ring_sh = "rgba(239,68,68,0.35)"
                ban_bg  = "#1c0707"; ban_bd = "#3d0a0a"; ban_txt = "#fca5a5"
                verdict = "Needs work — follow the recommendations below."

            st.markdown(f"""
            <div class="fade-up" style="background:{ban_bg}; border:1.5px solid {ban_bd};
                 border-radius:18px; padding:1.4rem 1.8rem; margin:1.5rem 0;
                 display:flex; align-items:center; gap:20px;
                 box-shadow:0 6px 28px rgba(0,0,0,0.4);">
              <div class="pop-in" style="background:{ring_bg}; color:#fff;
                   font-weight:900; font-size:1.7rem; width:74px; height:74px;
                   border-radius:50%; flex-shrink:0;
                   display:flex; align-items:center; justify-content:center;
                   box-shadow:0 6px 20px {ring_sh}; letter-spacing:-2px;">{overall}</div>
              <div>
                <p style="font-weight:800; font-size:1.05rem; color:{ban_txt};
                   -webkit-text-fill-color:{ban_txt}; margin:0 0 4px;">
                   Your resume scored {overall} / 100</p>
                <p style="font-size:0.86rem; color:{ban_txt};
                   -webkit-text-fill-color:{ban_txt}; margin:0; opacity:0.7;">
                   {verdict}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2 = st.columns(2)
            m1.metric("ATS Score",  f"{ats_score} / 100")
            m2.metric("JD Match",   f"{match}%")

            # Progress bars
            ac = "#10b981" if ats_score>=70 else "#f59e0b" if ats_score>=50 else "#ef4444"
            mc = "#818cf8" if match>=60    else "#f59e0b" if match>=40    else "#ef4444"

            st.markdown(f"""
            <div class="fade-up" style="background:#141720; border:1.5px solid #1e2433;
                 border-radius:16px; padding:1.3rem 1.6rem; margin:0.6rem 0;
                 box-shadow:0 4px 20px rgba(0,0,0,0.3);">

              <div style="margin-bottom:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:8px; height:8px; border-radius:50%;
                         background:{ac}; box-shadow:0 0 8px {ac};"></div>
                    <span style="font-size:0.82rem; font-weight:600; color:#94a3b8;">ATS Compatibility</span>
                  </div>
                  <span style="font-size:0.86rem; font-weight:800; color:{ac};
                        -webkit-text-fill-color:{ac};">{ats_score}%</span>
                </div>
                <div style="height:8px; background:#0d0f14; border-radius:99px; overflow:hidden;">
                  <div class="grow-bar" style="width:{ats_score}%; height:100%;
                       background:linear-gradient(90deg,{ac}66,{ac});
                       border-radius:99px; box-shadow:0 0 10px {ac}88;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:8px; height:8px; border-radius:50%;
                         background:{mc}; box-shadow:0 0 8px {mc};"></div>
                    <span style="font-size:0.82rem; font-weight:600; color:#94a3b8;">Job Description Match</span>
                  </div>
                  <span style="font-size:0.86rem; font-weight:800; color:{mc};
                        -webkit-text-fill-color:{mc};">{match}%</span>
                </div>
                <div style="height:8px; background:#0d0f14; border-radius:99px; overflow:hidden;">
                  <div class="grow-bar" style="width:{match}%; height:100%;
                       background:linear-gradient(90deg,{mc}66,{mc});
                       border-radius:99px; box-shadow:0 0 10px {mc}88;"></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            if issues:
                st.markdown("""
                <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
                   letter-spacing:2.5px; text-transform:uppercase;
                   margin:1.5rem 0 0.6rem;">Recommendations</p>
                """, unsafe_allow_html=True)
                for idx, issue in enumerate(issues, 1):
                    if idx <= 2:
                        sc, sb, sd = "#ef4444", "#1c0707", "#3d0a0a"
                    elif idx <= 5:
                        sc, sb, sd = "#f59e0b", "#1c1407", "#3d2e0a"
                    else:
                        sc, sb, sd = "#818cf8", "#13121f", "#2e2c5e"
                    st.markdown(f"""
                    <div class="fade-up" style="display:flex; align-items:flex-start; gap:12px;
                         background:#141720; border:1.5px solid {sd};
                         border-left:3px solid {sc}; border-radius:12px;
                         padding:12px 14px; margin-bottom:8px;
                         box-shadow:0 2px 12px rgba(0,0,0,0.3);">
                      <div style="background:{sb}; color:{sc}; font-weight:800;
                           font-size:0.68rem; min-width:24px; height:24px;
                           border-radius:7px; flex-shrink:0; display:flex;
                           align-items:center; justify-content:center;
                           border:1px solid {sd}; -webkit-text-fill-color:{sc};">{idx}</div>
                      <p style="font-size:0.85rem; color:#94a3b8;
                         -webkit-text-fill-color:#94a3b8; margin:0;
                         line-height:1.6; padding-top:1px;">{issue}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Missing skills
            if missing:
                st.markdown("""
                <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
                   letter-spacing:2.5px; text-transform:uppercase;
                   margin:1.5rem 0 0.5rem;">Missing Skills</p>
                """, unsafe_allow_html=True)
                chips = "".join([
                    f'<span style="display:inline-flex; align-items:center; gap:6px;'
                    f'background:#13121f; border:1px solid #2e2c5e;'
                    f'color:#a5b4fc; -webkit-text-fill-color:#a5b4fc;'
                    f'font-size:0.76rem; font-weight:600;'
                    f'padding:5px 13px; border-radius:99px; margin:3px;'
                    f'box-shadow:0 2px 8px rgba(0,0,0,0.3);">'
                    f'<span style="width:5px;height:5px;border-radius:50%;'
                    f'background:#818cf8;display:inline-block;"></span>{s}</span>'
                    for s in missing
                ])
                st.markdown(f"<div style='line-height:2.4;'>{chips}</div>", unsafe_allow_html=True)

            # AI Feedback
            st.markdown("""
            <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
               letter-spacing:2.5px; text-transform:uppercase;
               margin:1.5rem 0 0.5rem;">AI Feedback</p>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fade-up" style="background:#141720; border:1.5px solid #1e2433;
                 border-top:3px solid #6366f1; border-radius:16px;
                 padding:1.4rem 1.7rem; box-shadow:0 4px 20px rgba(0,0,0,0.3);">
              <div style="display:flex; align-items:center; gap:9px; margin-bottom:12px;
                   padding-bottom:10px; border-bottom:1px solid #1e2433;">
                <div style="width:28px; height:28px; border-radius:8px;
                     background:linear-gradient(135deg,#4f46e5,#7c3aed);
                     flex-shrink:0;"></div>
                <span style="font-weight:700; font-size:0.88rem; color:#e2e8f0;
                      -webkit-text-fill-color:#e2e8f0;">Gemini AI Suggestions</span>
              </div>
              <p style="font-size:0.85rem; color:#94a3b8; -webkit-text-fill-color:#94a3b8;
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
    <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
       letter-spacing:2.5px; text-transform:uppercase; margin-bottom:0.5rem;">
       Your Details</p>
    """, unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    with ca: name  = st.text_input("Full Name",  placeholder="Ishita")
    with cb: email = st.text_input("Email",      placeholder="ishita@email.com")
    with cc: phone = st.text_input("Phone",      placeholder="+91 98765 43210")

    st.markdown("""
    <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
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
    wc  = len([w for w in preview.split() if w.strip()])
    wcc = "#10b981" if 400<=wc<=900 else "#f59e0b"
    wcl = "Perfect length" if 400<=wc<=900 else "Aim for 400-900 words"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
         margin:1.3rem 0 4px;">
      <p style="font-size:0.65rem; font-weight:700; color:#6366f1;
         letter-spacing:2.5px; text-transform:uppercase; margin:0;">Live Preview</p>
      <span style="font-size:0.73rem; font-weight:600; color:{wcc};
            -webkit-text-fill-color:{wcc}; background:{wcc}18;
            padding:3px 11px; border-radius:99px; border:1px solid {wcc}44;">
        {wc} words &nbsp;·&nbsp; {wcl}
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.code(preview, language=None)

    _, gc, _ = st.columns([2, 2, 2])
    with gc:
        if st.button("Generate Resume", use_container_width=True):
            doc = Document()
            for line in preview.split("\n"):
                doc.add_paragraph(line)
            doc.save("resume.docx")
            pdf_file = export_pdf(preview)

            st.markdown("""
            <div style="background:#052e16; border:1.5px solid #064e3b;
                 border-radius:14px; padding:12px 16px; margin:10px 0;
                 display:flex; align-items:center; gap:10px;">
              <div style="width:8px; height:8px; background:#22c55e; border-radius:50%;
                   box-shadow:0 0 8px #22c55e; flex-shrink:0;"></div>
              <p style="font-size:0.88rem; font-weight:700; color:#6ee7b7;
                 -webkit-text-fill-color:#6ee7b7; margin:0;">
                 Resume compiled — download your files below.</p>
            </div>
            """, unsafe_allow_html=True)

            d1, d2 = st.columns(2)
            with d1:
                with open("resume.docx","rb") as f:
                    st.download_button("Download DOCX", f, "resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with d2:
                with open(pdf_file,"rb") as f:
                    st.download_button("Download PDF", f, "resume.pdf", mime="application/pdf")