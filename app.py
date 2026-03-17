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
#  FULL CSS
# ══════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #f0f4f8 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="block-container"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HERO SECTION ── */
.hero {
    background: linear-gradient(135deg, #0f1b35 0%, #1a2d5a 40%, #0d2444 70%, #0a1628 100%);
    padding: 2rem 3rem 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:'';
    position:absolute; top:0; right:0; bottom:0; left:0;
    background:
        radial-gradient(ellipse at 80% 50%, rgba(56,189,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse at 20% 80%, rgba(99,102,241,0.08) 0%, transparent 50%);
    pointer-events:none;
}
/* Mesh lines effect */
.hero::after {
    content:'';
    position:absolute; top:0; right:0; bottom:0; width:45%;
    background-image:
        linear-gradient(rgba(56,189,248,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.06) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events:none;
}

/* ── NAVBAR ── */
.navbar {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:2rem; position:relative; z-index:10;
}
.nav-logo {
    font-family:'Inter',sans-serif; font-size:1.3rem; font-weight:800;
    color:#ffffff; letter-spacing:-0.5px;
}
.nav-logo span { color:#38bdf8; }
.nav-links {
    display:flex; gap:28px; align-items:center;
}
.nav-link {
    font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:500;
    color:rgba(255,255,255,0.65); text-decoration:none; transition:color 0.2s;
    cursor:pointer;
}
.nav-link.active { color:#ffffff; border-bottom:2px solid #38bdf8; padding-bottom:2px; }
.nav-link:hover  { color:#ffffff; }
.nav-cta {
    background:transparent; border:1.5px solid rgba(255,255,255,0.4);
    color:#ffffff; font-family:'Inter',sans-serif; font-size:0.82rem;
    font-weight:600; padding:7px 18px; border-radius:8px; cursor:pointer;
    transition:all 0.2s;
}
.nav-cta:hover { background:rgba(255,255,255,0.1); border-color:rgba(255,255,255,0.7); }

/* ── HERO BODY ── */
.hero-body { display:flex; align-items:center; gap:3rem; position:relative; z-index:5; }
.hero-left { flex:1; }
.hero-eyebrow {
    font-size:0.65rem; font-weight:700; letter-spacing:3px; text-transform:uppercase;
    color:rgba(56,189,248,0.85); margin-bottom:0.6rem;
}
.hero-title {
    font-size:2.6rem; font-weight:900; color:#ffffff; letter-spacing:-1.5px;
    line-height:1.1; margin-bottom:0.75rem;
}
.hero-sub {
    font-size:0.9rem; color:rgba(255,255,255,0.55); line-height:1.65; max-width:420px;
}

/* ── FEATURE CARDS (top right of hero) ── */
.feature-cards { display:flex; gap:14px; flex-shrink:0; }
.feat-card {
    background:rgba(255,255,255,0.07); backdrop-filter:blur(10px);
    border:1px solid rgba(255,255,255,0.12); border-radius:16px;
    padding:18px 16px; width:130px; text-align:center;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.feat-card:hover {
    background:rgba(255,255,255,0.12);
    border-color:rgba(56,189,248,0.4);
    transform:translateY(-4px);
    box-shadow:0 12px 32px rgba(0,0,0,0.3);
}
.feat-icon {
    width:48px; height:48px; border-radius:12px; margin:0 auto 10px;
    display:flex; align-items:center; justify-content:center; font-size:1.3rem;
}
.feat-card-title {
    font-family:'Inter',sans-serif; font-size:0.62rem; font-weight:700;
    color:#ffffff; letter-spacing:1.5px; text-transform:uppercase; line-height:1.4;
}

/* ── TABS ── */
.tab-row {
    display:flex; gap:0; margin-top:2rem; position:relative; z-index:5;
    border-bottom:2px solid rgba(255,255,255,0.12);
}
.tab-item {
    font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:500;
    color:rgba(255,255,255,0.45); padding:10px 24px; cursor:pointer;
    border-bottom:2px solid transparent; margin-bottom:-2px;
    transition:all 0.2s;
}
.tab-item.active { color:#ffffff; border-bottom:2px solid #38bdf8; font-weight:700; }
.tab-item:hover  { color:rgba(255,255,255,0.8); }

/* ── CONTENT AREA ── */
.content-area {
    background:#f0f4f8; padding:2rem 3rem 3rem;
}

/* ── STEP CARDS ── */
.step-cards { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:24px; }
.step-card {
    background:#ffffff; border:2px solid #e8ecf0; border-radius:16px;
    padding:20px 22px; transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    box-shadow:0 2px 12px rgba(0,0,0,0.04);
}
.step-card:hover {
    border-color:#c7d2fe;
    box-shadow:0 8px 32px rgba(99,102,241,0.1);
    transform:translateY(-2px);
}
.step-header {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:14px;
}
.step-label {
    display:flex; align-items:center; gap:10px;
    font-family:'Inter',sans-serif; font-size:0.72rem; font-weight:800;
    color:#1e1b4b; letter-spacing:1.5px; text-transform:uppercase;
}
.step-icon {
    width:34px; height:34px; border-radius:10px;
    background:linear-gradient(135deg,#ede9fe,#ddd6fe);
    display:flex; align-items:center; justify-content:center; font-size:1rem;
}
.step-help {
    font-family:'Inter',sans-serif; font-size:0.75rem; font-weight:500;
    color:#6366f1; cursor:pointer; display:flex; align-items:center; gap:4px;
}

/* ── UPLOADER BOX ── */
.upload-box {
    background:linear-gradient(135deg,#f0f9ff,#e0f2fe);
    border:2px dashed #7dd3fc; border-radius:12px;
    padding:28px 20px; text-align:center;
    transition:all 0.3s; cursor:pointer;
}
.upload-box:hover {
    border-color:#0284c7;
    background:linear-gradient(135deg,#e0f2fe,#bae6fd);
    transform:scale(1.01);
}
.upload-box-title {
    font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:700;
    color:#0c4a6e; margin-bottom:4px;
}
.upload-box-sub {
    font-family:'Inter',sans-serif; font-size:0.75rem; color:#0284c7; margin-bottom:12px;
}
.upload-browse-btn {
    background:#ffffff; border:1.5px solid #0284c7; color:#0284c7;
    font-family:'Inter',sans-serif; font-size:0.78rem; font-weight:600;
    padding:6px 18px; border-radius:8px; cursor:pointer;
    transition:all 0.2s; display:inline-block;
}
.upload-browse-btn:hover {
    background:#0284c7; color:#ffffff;
}

/* ── CHAR COUNTER ── */
.char-counter {
    text-align:right; font-family:'Inter',sans-serif; font-size:0.72rem;
    color:#9ca3af; margin-top:6px;
}

/* ── SCAN BUTTON ── */
.scan-btn-wrap { display:flex; justify-content:center; margin:8px 0 20px; }

/* ── STREAMLIT OVERRIDES ── */
h1,h2,h3,h4,h5,h6,p,span,label,div,
[data-testid="stMarkdownContainer"] p {
    font-family:'Inter',sans-serif !important;
    color:#1e1b4b !important;
}
h2 {
    font-size:0.65rem !important; font-weight:700 !important;
    color:#6366f1 !important; letter-spacing:2px !important;
    text-transform:uppercase !important; border:none !important;
    margin-top:1.5rem !important; margin-bottom:0.4rem !important;
}
h3 {
    font-size:1rem !important; font-weight:700 !important;
    color:#1e1b4b !important; border:none !important;
    margin-top:0.8rem !important; letter-spacing:-0.2px !important;
    text-transform:none !important;
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {
    background:#fff !important;
    border:2px solid #e5e7eb !important;
    border-left:2px solid #e5e7eb !important;
    border-radius:10px !important;
    transition:all 0.25s !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color:#6366f1 !important;
    box-shadow:0 0 0 4px rgba(99,102,241,0.1) !important;
}
input, textarea {
    color:#1e1b4b !important; background:transparent !important;
    -webkit-text-fill-color:#1e1b4b !important;
    font-family:'Inter',sans-serif !important; font-size:0.88rem !important;
}
textarea::placeholder, input::placeholder {
    color:#a5b4fc !important; -webkit-text-fill-color:#a5b4fc !important;
}
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-family:'Inter',sans-serif !important; font-size:0.8rem !important;
    font-weight:600 !important; color:#374151 !important;
    -webkit-text-fill-color:#374151 !important;
    letter-spacing:0 !important; text-transform:none !important;
}

/* File uploader — hide default, we show custom above */
[data-testid="stFileUploader"] > section {
    background:linear-gradient(135deg,#f0f9ff,#e0f2fe) !important;
    border:2px dashed #7dd3fc !important;
    border-left:2px dashed #7dd3fc !important;
    border-radius:12px !important; padding:1.4rem !important;
    transition:all 0.3s !important;
}
[data-testid="stFileUploader"] > section:hover {
    border-color:#0284c7 !important;
    background:linear-gradient(135deg,#e0f2fe,#bae6fd) !important;
    transform:translateY(-2px) !important;
    box-shadow:0 8px 20px rgba(2,132,199,0.12) !important;
}
[data-testid="stFileUploader"] button {
    background:#ffffff !important; border:1.5px solid #0284c7 !important;
    color:#0284c7 !important; font-family:'Inter',sans-serif !important;
    font-size:0.78rem !important; font-weight:600 !important;
    border-radius:8px !important; clip-path:none !important;
    transition:all 0.2s !important;
}
[data-testid="stFileUploader"] button:hover {
    background:#0284c7 !important; color:#fff !important;
    box-shadow:0 4px 12px rgba(2,132,199,0.3) !important;
}
[data-testid="stFileUploader"] button * {
    color:#0284c7 !important; -webkit-text-fill-color:#0284c7 !important;
}
[data-testid="stFileUploader"] button:hover * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}
[data-testid="stFileUploader"] label p {
    font-family:'Inter',sans-serif !important; font-size:0.8rem !important;
    font-weight:600 !important; color:#374151 !important;
    -webkit-text-fill-color:#374151 !important;
}

/* Primary scan button — pill shaped */
.stButton > button {
    width:340px !important;
    background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#1e1b4b 100%) !important;
    background-size:200% auto !important;
    border:none !important; color:#fff !important;
    font-family:'Inter',sans-serif !important; font-size:1rem !important;
    font-weight:700 !important; letter-spacing:0.5px !important;
    padding:1rem 3rem !important;
    border-radius:99px !important; clip-path:none !important;
    box-shadow:0 8px 28px rgba(30,27,75,0.45), 0 2px 8px rgba(30,27,75,0.2) !important;
    transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    margin:0 auto !important; display:block !important;
}
.stButton > button:hover {
    background-position:right center !important;
    transform:translateY(-4px) scale(1.04) !important;
    box-shadow:0 16px 40px rgba(30,27,75,0.55), 0 4px 14px rgba(30,27,75,0.25) !important;
}
.stButton > button:active {
    transform:translateY(-1px) scale(0.98) !important;
}
.stButton > button * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background:#fff !important; border:2px solid #e5e7eb !important;
    border-top:4px solid #6366f1 !important; padding:1.3rem !important;
    border-radius:16px !important;
    box-shadow:0 4px 16px rgba(99,102,241,0.07) !important;
    transition:all 0.3s !important;
}
[data-testid="stMetric"]:hover {
    transform:translateY(-4px) !important;
    box-shadow:0 14px 32px rgba(99,102,241,0.15) !important;
}
[data-testid="stMetricValue"] {
    font-family:'Inter',sans-serif !important; font-size:2.1rem !important;
    font-weight:900 !important; color:#4f46e5 !important;
    -webkit-text-fill-color:#4f46e5 !important; letter-spacing:-1px !important;
}
[data-testid="stMetricLabel"] p {
    font-family:'Inter',sans-serif !important; font-size:0.7rem !important;
    font-weight:600 !important; color:#6b7280 !important;
    -webkit-text-fill-color:#6b7280 !important;
    text-transform:uppercase !important; letter-spacing:1.5px !important;
}

/* Spinner */
[data-testid="stSpinner"] p {
    color:#4f46e5 !important; font-family:'Inter',sans-serif !important;
    -webkit-text-fill-color:#4f46e5 !important; font-weight:500 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background:#fffbeb !important; border:1.5px solid #fde68a !important;
    border-left:4px solid #f59e0b !important; border-radius:12px !important;
}
[data-testid="stAlert"] p {
    color:#92400e !important; -webkit-text-fill-color:#92400e !important;
    font-family:'Inter',sans-serif !important; font-size:0.85rem !important;
}

/* Code block */
.stCode > pre {
    background:#fafafe !important; border:2px solid #e5e7eb !important;
    border-left:4px solid #6366f1 !important; border-radius:14px !important;
}
.stCode > pre > code, .stCode > pre > code * {
    color:#3730a3 !important; -webkit-text-fill-color:#3730a3 !important;
    font-family:'JetBrains Mono','Fira Code',monospace !important;
    font-size:0.8rem !important;
}

/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background:#fff !important; border:2px solid #6366f1 !important;
    color:#4f46e5 !important; font-family:'Inter',sans-serif !important;
    font-size:0.85rem !important; font-weight:700 !important;
    border-radius:12px !important; clip-path:none !important;
    transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    padding:0.65rem 1.5rem !important;
    box-shadow:0 2px 8px rgba(99,102,241,0.1) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background:linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border-color:transparent !important;
    box-shadow:0 10px 28px rgba(79,70,229,0.38) !important;
    transform:translateY(-3px) scale(1.02) !important;
}
[data-testid="stDownloadButton"] > button:hover * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}
[data-testid="stDownloadButton"] > button * {
    color:#4f46e5 !important; -webkit-text-fill-color:#4f46e5 !important;
}

/* Markdown text */
[data-testid="stMarkdownContainer"] p {
    font-size:0.875rem !important; line-height:1.75 !important;
    color:#374151 !important; -webkit-text-fill-color:#374151 !important;
}

/* section label */
.sec-label {
    font-family:'Inter',sans-serif; font-size:0.65rem; font-weight:700;
    color:#6366f1; letter-spacing:2.5px; text-transform:uppercase;
    margin-bottom:6px; display:block;
}

/* ANIMATIONS */
@keyframes score-pop {
    0%  { transform:scale(0.4); opacity:0; }
    70% { transform:scale(1.1); }
    100%{ transform:scale(1);   opacity:1; }
}
.score-ring { animation:score-pop 0.65s cubic-bezier(0.34,1.56,0.64,1) forwards; }

@keyframes card-in {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
}
.card-animate { animation:card-in 0.45s cubic-bezier(0.4,0,0.2,1) forwards; }

@keyframes bar-grow { from { width:0%; } }
.bar-anim { animation:bar-grow 1.3s cubic-bezier(0.4,0,0.2,1) forwards; }

/* scrollbar */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:linear-gradient(#a5b4fc,#c4b5fd); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HERO + NAVBAR
# ══════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">

  <!-- NAVBAR -->
  <div class="navbar">
    <div class="nav-logo">Acadence<span>.</span></div>
    <div class="nav-links">
      <span class="nav-link active">Analyzer</span>
      <span class="nav-link">Builder</span>
      <span class="nav-link">Features</span>
      <span class="nav-link">Pricing</span>
      <span class="nav-link">Sign In</span>
      <span class="nav-cta">Get Started Free</span>
    </div>
  </div>

  <!-- HERO BODY -->
  <div class="hero-body">
    <div class="hero-left">
      <div class="hero-eyebrow">AI POWERED &nbsp;•&nbsp; FREE &nbsp;•&nbsp; INSTANT RESULTS</div>
      <div class="hero-title">Acadence Resume Lab</div>
      <div class="hero-sub">
        Score your resume against real recruiter criteria. Get actionable
        fixes and land more interviews.
      </div>
    </div>

    <!-- FEATURE CARDS -->
    <div class="feature-cards">
      <div class="feat-card">
        <div class="feat-icon" style="background:linear-gradient(135deg,#1e3a5f,#1e4d6b);">🧠</div>
        <div class="feat-card-title">AI-Powered<br>Insights</div>
      </div>
      <div class="feat-card">
        <div class="feat-icon" style="background:linear-gradient(135deg,#1e3a5f,#1e4d6b);">⚡</div>
        <div class="feat-card-title">Instant<br>Analysis</div>
      </div>
      <div class="feat-card">
        <div class="feat-icon" style="background:linear-gradient(135deg,#1e3a5f,#1e4d6b);">🎯</div>
        <div class="feat-card-title">ATS<br>Optimised</div>
      </div>
    </div>
  </div>

  <!-- TAB ROW -->
  <div class="tab-row">
    <div class="tab-item active">Resume Analyzer</div>
    <div class="tab-item">Resume Builder</div>
  </div>

</div>
""", unsafe_allow_html=True)

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
        if not text.strip(): st.warning("No readable text found — possibly a scanned PDF.")
        return text
    except Exception as e:
        st.error(f"Failed to read PDF: {e}"); return ""

def extract_keywords(text):
    skills = ["python","java","c++","javascript","react","node","docker","kubernetes",
              "mongodb","sql","aws","machine learning","tensorflow","pytorch",
              "data structures","algorithms","rest api"]
    text = text.lower()
    return [s for s in skills if s in text]

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
    if vc < 3:   score -= 15; issues.append("Weak action verbs — use words like Built, Led, Optimized")
    elif vc < 6: score -= 8
    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15; issues.append("No quantified achievements (add numbers like 40%, 2x, 500+)")
    if "|" in resume_text:                score -= 12; issues.append("Tables or pipes detected — risky for ATS parsing")
    if len(resume_text.split("\n")) < 15: score -= 10; issues.append("Poor structure or spacing")
    if "@" not in resume_text:            score -= 5;  issues.append("Missing contact email")
    jd_words = re.findall(r"[a-zA-Z]{4,}", jd.lower())
    if jd_words:
        ks = sum(1 for w in jd_words if w in text)/len(jd_words)
    else: ks = 0
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
#  CONTENT AREA — wrap in padding div
# ══════════════════════════════════════════════════════════

st.markdown('<div style="padding:2rem 3rem 1rem;">', unsafe_allow_html=True)

tabs = st.tabs(["✦  Resume Analyzer", "✦  Resume Builder"])

# ══════════════════════════════════════════════════════════
#  TAB 1 — ANALYZER
# ══════════════════════════════════════════════════════════

with tabs[0]:

    # Two-column step layout
    col_jd, col_resume = st.columns(2, gap="large")

    with col_jd:
        st.markdown("""
        <div class="step-card">
          <div class="step-header">
            <div class="step-label">
              <div class="step-icon">📋</div>
              STEP 1 - JOB DESCRIPTION
            </div>
            <span style="font-family:'Inter',sans-serif;font-size:0.75rem;
                  font-weight:500;color:#6366f1;cursor:pointer;">ⓘ Help</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        jd = st.text_area(
            "jd_input", height=180,
            placeholder='e.g., "Software Engineer with 5+ years..."',
            label_visibility="collapsed"
        )
        char_count = len(jd)
        st.markdown(f"""
        <div class="char-counter">{char_count} / 10000</div>
        """, unsafe_allow_html=True)

    with col_resume:
        st.markdown("""
        <div class="step-card">
          <div class="step-header">
            <div class="step-label">
              <div class="step-icon">📄</div>
              STEP 2 - YOUR RESUME
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF)", type=["pdf"],
            label_visibility="collapsed"
        )

    # Centered pill scan button
    st.markdown('<div style="display:flex;justify-content:center;margin:20px 0 8px;">', unsafe_allow_html=True)
    analyze = st.button("🔍   Scan Resume")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── RESULTS ──────────────────────────────────────────────
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
                match, missing    = calculate_match(res_skills, jd_skills)
                ats_score, issues = ats_check(text, jd)
                feedback          = ai_feedback(text)

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

            st.markdown(f"""
            <div class="card-animate" style="background:{banner_bg};border:2px solid {banner_bd};
                 border-radius:20px;padding:1.4rem 2rem;margin:1.5rem 0;
                 display:flex;align-items:center;gap:20px;
                 box-shadow:0 6px 28px {ring_sh.replace('0.42','0.1')};">
                <div class="score-ring" style="background:{ring_bg};color:#fff;
                     font-family:'Inter',sans-serif;font-weight:900;font-size:1.7rem;
                     width:76px;height:76px;border-radius:50%;flex-shrink:0;
                     display:flex;align-items:center;justify-content:center;
                     box-shadow:0 8px 24px {ring_sh};letter-spacing:-2px;">{overall}</div>
                <div>
                    <p style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.1rem;
                       color:{txt};margin:0 0 3px;-webkit-text-fill-color:{txt};">
                        Your resume scored {overall} / 100</p>
                    <p style="font-family:'Inter',sans-serif;font-size:0.87rem;color:{txt};
                       margin:0;opacity:0.75;-webkit-text-fill-color:{txt};">{verdict}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            c1.metric("ATS Score",  f"{ats_score} / 100")
            c2.metric("JD Match",   f"{match}%")

            ac = "#10b981" if ats_score>=70 else "#f59e0b" if ats_score>=50 else "#ef4444"
            mc = "#6366f1" if match>=60    else "#f59e0b" if match>=40    else "#ef4444"

            st.markdown(f"""
            <div class="card-animate" style="background:#fff;border:2px solid #f0f4f8;
                 border-radius:16px;padding:1.3rem 1.6rem;margin:0.6rem 0;
                 box-shadow:0 3px 16px rgba(0,0,0,0.05);">
              <div style="margin-bottom:18px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
                  <div style="display:flex;align-items:center;gap:9px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:{ac};box-shadow:0 0 7px {ac};"></div>
                    <span style="font-family:'Inter',sans-serif;font-size:0.83rem;font-weight:600;color:#374151;">ATS Compatibility</span>
                  </div>
                  <span style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:800;color:{ac};">{ats_score}%</span>
                </div>
                <div style="height:9px;background:#f1f5f9;border-radius:99px;overflow:hidden;">
                  <div class="bar-anim" style="width:{ats_score}%;height:100%;
                       background:linear-gradient(90deg,{ac}88,{ac});border-radius:99px;
                       box-shadow:0 2px 7px {ac}55;"></div>
                </div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
                  <div style="display:flex;align-items:center;gap:9px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:{mc};box-shadow:0 0 7px {mc};"></div>
                    <span style="font-family:'Inter',sans-serif;font-size:0.83rem;font-weight:600;color:#374151;">Job Description Match</span>
                  </div>
                  <span style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:800;color:{mc};">{match}%</span>
                </div>
                <div style="height:9px;background:#f1f5f9;border-radius:99px;overflow:hidden;">
                  <div class="bar-anim" style="width:{match}%;height:100%;
                       background:linear-gradient(90deg,{mc}88,{mc});border-radius:99px;
                       box-shadow:0 2px 7px {mc}55;"></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if issues:
                st.markdown('<span class="sec-label" style="margin-top:1.4rem;display:block;">Recommendations</span>', unsafe_allow_html=True)
                for idx, issue in enumerate(issues, 1):
                    sc = "#ef4444" if idx<=2 else "#f59e0b" if idx<=5 else "#6366f1"
                    sb = "#fff1f2" if idx<=2 else "#fffbeb" if idx<=5 else "#f5f3ff"
                    sd = "#fca5a5" if idx<=2 else "#fde68a" if idx<=5 else "#c4b5fd"
                    st.markdown(f"""
                    <div class="card-animate" style="display:flex;align-items:flex-start;gap:13px;
                         background:#fff;border:1.5px solid {sd};border-left:4px solid {sc};
                         border-radius:12px;padding:13px 15px;margin-bottom:9px;
                         box-shadow:0 2px 9px {sc}16;">
                        <div style="background:{sb};color:{sc};font-family:'Inter',sans-serif;
                             font-weight:800;font-size:0.7rem;min-width:25px;height:25px;
                             border-radius:7px;display:flex;align-items:center;justify-content:center;
                             flex-shrink:0;border:1.5px solid {sd};">{idx}</div>
                        <p style="font-family:'Inter',sans-serif;font-size:0.86rem;color:#374151;
                           -webkit-text-fill-color:#374151;margin:0;line-height:1.55;padding-top:1px;">{issue}</p>
                    </div>
                    """, unsafe_allow_html=True)

            if missing:
                st.markdown('<span class="sec-label" style="margin-top:1.4rem;display:block;">Missing Skills</span>', unsafe_allow_html=True)
                chips = "".join([
                    f'<span style="display:inline-flex;align-items:center;gap:5px;'
                    f'background:linear-gradient(135deg,#f5f3ff,#ede9fe);'
                    f'border:1.5px solid #c4b5fd;color:#5b21b6;-webkit-text-fill-color:#5b21b6;'
                    f'font-family:Inter,sans-serif;font-size:0.77rem;font-weight:600;'
                    f'padding:5px 13px;border-radius:99px;margin:3px;'
                    f'box-shadow:0 2px 7px rgba(124,58,237,0.1);">'
                    f'<span style="width:6px;height:6px;border-radius:50%;background:#7c3aed;display:inline-block;"></span>'
                    f'{s}</span>'
                    for s in missing
                ])
                st.markdown(f"<div style='margin-top:5px;line-height:2.3;'>{chips}</div>", unsafe_allow_html=True)

            st.markdown('<span class="sec-label" style="margin-top:1.4rem;display:block;">AI Feedback</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card-animate" style="background:#fff;border:2px solid #f0f4f8;
                 border-top:4px solid #6366f1;border-radius:16px;padding:1.4rem 1.7rem;
                 box-shadow:0 4px 18px rgba(0,0,0,0.05);">
                <div style="display:flex;align-items:center;gap:9px;margin-bottom:11px;">
                    <div style="width:30px;height:30px;border-radius:9px;
                         background:linear-gradient(135deg,#6366f1,#8b5cf6);
                         display:flex;align-items:center;justify-content:center;font-size:0.85rem;">✨</div>
                    <span style="font-family:'Inter',sans-serif;font-weight:700;font-size:0.88rem;
                           color:#1e1b4b;-webkit-text-fill-color:#1e1b4b;">Gemini AI Suggestions</span>
                </div>
                <p style="font-family:'Inter',sans-serif;font-size:0.86rem;color:#374151;
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

    st.markdown('<span class="sec-label">Your Details</span>', unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)
    with ca: name  = st.text_input("Full Name",  placeholder="Ishita")
    with cb: email = st.text_input("Email",      placeholder="ishita@email.com")
    with cc: phone = st.text_input("Phone",      placeholder="+91 98765 43210")

    st.markdown('<span class="sec-label" style="margin-top:1.4rem;display:block;">Resume Content</span>', unsafe_allow_html=True)
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
    wc = len([w for w in preview.split() if w.strip()])
    wcc = "#10b981" if 400<=wc<=900 else "#f59e0b"
    wcl = "✓ Perfect length" if 400<=wc<=900 else "Aim for 400–900 words"

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin:1.2rem 0 4px;">
        <span class="sec-label" style="margin:0;">Live Preview</span>
        <span style="font-family:'Inter',sans-serif;font-size:0.74rem;font-weight:600;
               color:{wcc};-webkit-text-fill-color:{wcc};
               background:{wcc}18;padding:3px 11px;border-radius:99px;
               border:1.5px solid {wcc}44;">
            {wc} words · {wcl}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.code(preview, language=None)

    st.markdown('<div style="display:flex;justify-content:center;margin-top:10px;">', unsafe_allow_html=True)
    if st.button("⬇   Generate Resume"):
        doc = Document()
        for line in preview.split("\n"): doc.add_paragraph(line)
        doc.save("resume.docx")
        pdf_file = export_pdf(preview)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);
             border:2px solid #6ee7b7;border-radius:14px;padding:13px 17px;margin:10px 0;
             display:flex;align-items:center;gap:11px;
             box-shadow:0 4px 14px rgba(16,185,129,0.14);">
            <span style="font-size:1.25rem;">🎉</span>
            <p style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:700;
               color:#065f46;-webkit-text-fill-color:#065f46;margin:0;">
                Resume compiled! Download your files below.</p>
        </div>
        """, unsafe_allow_html=True)

        dl1, dl2 = st.columns(2)
        with dl1:
            with open("resume.docx","rb") as f:
                st.download_button("📄  Download DOCX", f, "resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with dl2:
            with open(pdf_file,"rb") as f:
                st.download_button("📑  Download PDF", f, "resume.pdf", mime="application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)