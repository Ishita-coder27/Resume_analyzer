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

# ─── SCI-FI HUD STYLING ───────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

/* ── GLOBAL RESET ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
    background: #020b18 !important;
    color: #00e5ff !important;
}

[data-testid="stAppViewContainer"] {
    background: #020b18 !important;
}

[data-testid="block-container"] {
    background: transparent !important;
    padding-top: 1rem !important;
}

/* Grid scanline background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,229,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        to bottom,
        transparent 0px,
        transparent 3px,
        rgba(0,229,255,0.012) 3px,
        rgba(0,229,255,0.012) 4px
    );
    pointer-events: none;
    z-index: 1;
}

/* ── GLOBAL TEXT ── */
h1, h2, h3, h4, h5, h6, p, span, label, div,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #00e5ff !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── TITLE ── */
h1 {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    letter-spacing: 8px !important;
    text-align: center !important;
    text-transform: uppercase !important;
    text-shadow: 0 0 30px rgba(0,229,255,0.7), 0 0 60px rgba(0,229,255,0.3) !important;
    padding: 1rem 0 0.25rem !important;
}

h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    font-size: 0.85rem !important;
    color: rgba(0,229,255,0.6) !important;
    border-bottom: 1px solid rgba(0,229,255,0.15) !important;
    padding-bottom: 6px !important;
    margin-top: 1.2rem !important;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,229,255,0.2) !important;
    gap: 4px !important;
}

[data-baseweb="tab"] {
    background: transparent !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
    color: rgba(0,229,255,0.45) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 8px 20px !important;
    clip-path: polygon(8px 0%,100% 0%,calc(100% - 8px) 100%,0% 100%) !important;
    transition: all 0.2s !important;
}

[data-baseweb="tab"]:hover {
    background: rgba(0,229,255,0.08) !important;
    color: #00e5ff !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(0,229,255,0.1) !important;
    color: #00e5ff !important;
    border-color: #00e5ff !important;
    border-bottom: 2px solid #00e5ff !important;
}

[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"] { display: none !important; }

/* ── TEXT AREA & INPUT ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {
    background: rgba(0,20,40,0.85) !important;
    border: 1px solid rgba(0,229,255,0.25) !important;
    border-left: 3px solid #00e5ff !important;
    border-radius: 0 !important;
}

input, textarea {
    color: #00e5ff !important;
    background: transparent !important;
    -webkit-text-fill-color: #00e5ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    caret-color: #00e5ff !important;
}

textarea::placeholder, input::placeholder {
    color: rgba(0,229,255,0.2) !important;
    -webkit-text-fill-color: rgba(0,229,255,0.2) !important;
}

div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
    border-color: #00e5ff !important;
    box-shadow: inset 0 0 20px rgba(0,229,255,0.04), 0 0 10px rgba(0,229,255,0.15) !important;
}

/* Label above inputs */
[data-testid="stTextArea"] label p,
[data-testid="stTextInput"] label p {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    color: rgba(0,229,255,0.5) !important;
    text-transform: uppercase !important;
    -webkit-text-fill-color: rgba(0,229,255,0.5) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
    background: rgba(0,20,40,0.6) !important;
    border: 1px dashed rgba(0,229,255,0.3) !important;
    border-left: 3px solid rgba(0,229,255,0.6) !important;
    border-radius: 0 !important;
}

[data-testid="stFileUploader"] > section:hover {
    border-color: #00e5ff !important;
    background: rgba(0,40,80,0.5) !important;
}

[data-testid="stFileUploader"] button {
    background: rgba(0,229,255,0.08) !important;
    border: 1px solid #00e5ff !important;
    color: #00e5ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 2px !important;
    border-radius: 0 !important;
    clip-path: polygon(6px 0%,100% 0%,calc(100% - 6px) 100%,0% 100%) !important;
}

[data-testid="stFileUploader"] button * {
    color: #00e5ff !important;
    -webkit-text-fill-color: #00e5ff !important;
}

[data-testid="stFileUploader"] label p {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    color: rgba(0,229,255,0.5) !important;
    text-transform: uppercase !important;
    -webkit-text-fill-color: rgba(0,229,255,0.5) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid #00e5ff !important;
    color: #00e5ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 0 !important;
    clip-path: polygon(12px 0%,100% 0%,calc(100% - 12px) 100%,0% 100%) !important;
    transition: all 0.3s !important;
    margin-top: 0.5rem !important;
}

.stButton > button:hover {
    background: rgba(0,229,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.25) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button * {
    color: #00e5ff !important;
    -webkit-text-fill-color: #00e5ff !important;
    font-family: 'Orbitron', monospace !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(0,20,40,0.7) !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
    border-top: 2px solid #00e5ff !important;
    padding: 1rem !important;
    border-radius: 0 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    color: #00e5ff !important;
    -webkit-text-fill-color: #00e5ff !important;
    text-shadow: 0 0 20px rgba(0,229,255,0.5) !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.55rem !important;
    letter-spacing: 3px !important;
    color: rgba(0,229,255,0.45) !important;
    -webkit-text-fill-color: rgba(0,229,255,0.45) !important;
    text-transform: uppercase !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: rgba(0,229,255,0.6) !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 2px !important;
    -webkit-text-fill-color: rgba(0,229,255,0.6) !important;
}

/* ── ALERTS / WARNINGS ── */
[data-testid="stAlert"] {
    background: rgba(255,68,68,0.06) !important;
    border: 1px solid rgba(255,68,68,0.4) !important;
    border-left: 3px solid #ff4444 !important;
    border-radius: 0 !important;
    color: #ff6666 !important;
}

[data-testid="stAlert"] p {
    color: #ff6666 !important;
    -webkit-text-fill-color: #ff6666 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
}

/* ── CODE BLOCK (resume preview) ── */
.stCode > pre {
    background: rgba(10,0,20,0.85) !important;
    border: 1px solid rgba(255,0,255,0.2) !important;
    border-left: 3px solid rgba(255,0,255,0.6) !important;
    border-radius: 0 !important;
}

.stCode > pre > code,
.stCode > pre > code * {
    color: rgba(255,180,255,0.85) !important;
    -webkit-text-fill-color: rgba(255,180,255,0.85) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    text-shadow: none !important;
}

/* ── WRITE / MARKDOWN TEXT ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 0.8rem !important;
    line-height: 1.8 !important;
    color: rgba(0,229,255,0.75) !important;
    -webkit-text-fill-color: rgba(0,229,255,0.75) !important;
}

/* Bullet list items */
[data-testid="stMarkdownContainer"] li::marker {
    color: #00e5ff !important;
}

/* ── COLUMNS ── */
[data-testid="column"] {
    background: transparent !important;
}

/* ── DOWNLOAD BUTTONS ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(255,0,255,0.5) !important;
    color: #ff00ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    clip-path: polygon(10px 0%,100% 0%,calc(100% - 10px) 100%,0% 100%) !important;
    border-radius: 0 !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,0,255,0.08) !important;
    box-shadow: 0 0 16px rgba(255,0,255,0.2) !important;
}

[data-testid="stDownloadButton"] > button * {
    color: #ff00ff !important;
    -webkit-text-fill-color: #ff00ff !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── HUD TITLE BANNER ─────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; margin-bottom:0.25rem;">
    <p style="font-family:'Share Tech Mono',monospace; font-size:0.65rem;
       color:rgba(0,229,255,0.35); letter-spacing:4px; margin:0;">
       /// NEURAL ATS SCANNER v4.2 /// HOLOGRAPHIC INTERFACE ///
    </p>
</div>
""", unsafe_allow_html=True)

st.title("ACADENCE RESUME LAB")

st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <p style="font-family:'Share Tech Mono',monospace; font-size:0.6rem;
       color:rgba(0,229,255,0.25); letter-spacing:3px; margin:0;">
       SYSTEM ONLINE ● GEMINI-2.5-FLASH LOADED ● ATS ENGINE ARMED
    </p>
</div>
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
        st.error("⚠ NO FILE UPLOADED")
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
                st.warning(f"⚠ ERROR READING PAGE {i+1}: {page_error}")
        if not text.strip():
            st.warning("⚠ NO READABLE TEXT FOUND — POSSIBLY SCANNED PDF")
        return text
    except Exception as e:
        st.error(f"⚠ FAILED TO READ PDF: {e}")
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
        issues.append("Too short (<400 words)")
    elif words > 900:
        score -= 12
        issues.append("Too long (>900 words)")

    bullet_count = resume_text.count("•") + resume_text.count("-")
    if bullet_count < 5:
        score -= 15
        issues.append("Very few bullet points")
    elif bullet_count < 10:
        score -= 8
        issues.append("Insufficient bullet points")

    action_verbs = [
        "developed", "built", "designed", "implemented", "optimized",
        "created", "engineered", "improved", "automated", "led",
        "managed", "architected", "analyzed"
    ]
    verb_count = sum([1 for v in action_verbs if v in text])
    if verb_count < 3:
        score -= 15
        issues.append("Weak action verbs")
    elif verb_count < 6:
        score -= 8

    if not re.search(r"\d+%|\d+x|\d+\+", resume_text):
        score -= 15
        issues.append("No quantified achievements")

    if "|" in resume_text:
        score -= 12
        issues.append("Tables detected (ATS risk)")
    if len(resume_text.split("\n")) < 15:
        score -= 10
        issues.append("Poor structure / spacing")
    if "@" not in resume_text:
        score -= 5
        issues.append("Missing contact info")

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

    if text.count("project") > 12 or text.count("experience") > 12:
        score -= 8
        issues.append("Keyword stuffing detected")

    if "responsible for" in text:
        score -= 8
        issues.append("Weak phrasing (responsibility-based, not impact-based)")

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
        return f"GEMINI ERROR: {str(e)}"


def export_pdf(content):
    file = "resume.pdf"
    c = canvas.Canvas(file)
    y = 800
    for line in content.split("\n"):
        c.drawString(40, y, line)
        y -= 20
    c.save()
    return file


# ─── UI TABS ──────────────────────────────────────────────────────────────────

tabs = st.tabs(["[ ANALYZER ]", "[ BUILDER ]"])

# ══════════════════════════════════════════════════════════
#  TAB 1 — ANALYZER
# ══════════════════════════════════════════════════════════

with tabs[0]:

    st.subheader("INPUT PARAMETERS")

    jd = st.text_area("// JOB DESCRIPTION FEED", height=150,
                       placeholder="PASTE TARGET JOB DESCRIPTION HERE...")

    uploaded_file = st.file_uploader("// RESUME UPLOAD [PDF]", type=["pdf"])

    analyze = st.button("⬡ INITIATE NEURAL SCAN")

    if analyze:
        try:
            if uploaded_file is None:
                st.warning("⚠ WARNING :: RESUME FILE REQUIRED")
                st.stop()
            if jd.strip() == "":
                st.warning("⚠ WARNING :: JOB DESCRIPTION REQUIRED")
                st.stop()

            with st.spinner("SCANNING NEURAL PATTERNS... ANALYZING ATS VECTORS..."):
                text = extract_pdf_text(uploaded_file)

                if not text or len(text.strip()) < 50:
                    st.error("⚠ CRITICAL :: COULD NOT EXTRACT TEXT FROM PDF")
                    st.stop()

                res_skills = extract_keywords(text)
                jd_skills = extract_keywords(jd)

                match, missing = calculate_match(res_skills, jd_skills)
                ats_score, issues = ats_check(text, jd)
                feedback = ai_feedback(text)

            st.subheader("SCAN RESULTS")

            col1, col2 = st.columns(2)
            col1.metric("ATS SCORE", f"{ats_score}%")
            col2.metric("MATCH SCORE", f"{match}%")

            # Progress bars styled via markdown
            ats_color = "#00e5ff" if ats_score >= 70 else "#ff9944" if ats_score >= 50 else "#ff4444"
            match_color = "#ff00ff" if match >= 60 else "#ff9944" if match >= 40 else "#ff4444"

            st.markdown(f"""
            <div style="margin:0.5rem 0 1rem;">
                <div style="display:flex;gap:12px;align-items:center;margin-bottom:6px;">
                    <span style="font-family:'Orbitron',monospace;font-size:0.55rem;
                           letter-spacing:2px;color:rgba(0,229,255,0.4);
                           -webkit-text-fill-color:rgba(0,229,255,0.4);width:90px;">ATS POWER</span>
                    <div style="flex:1;height:4px;background:rgba(0,229,255,0.08);position:relative;">
                        <div style="width:{ats_score}%;height:100%;
                             background:linear-gradient(90deg,#002840,{ats_color});
                             position:relative;">
                            <div style="position:absolute;right:0;top:0;bottom:0;width:4px;
                                 background:#fff;box-shadow:0 0 6px {ats_color};"></div>
                        </div>
                    </div>
                    <span style="font-family:'Orbitron',monospace;font-size:0.6rem;
                           color:{ats_color};-webkit-text-fill-color:{ats_color};width:36px;
                           text-align:right;">{ats_score}%</span>
                </div>
                <div style="display:flex;gap:12px;align-items:center;">
                    <span style="font-family:'Orbitron',monospace;font-size:0.55rem;
                           letter-spacing:2px;color:rgba(0,229,255,0.4);
                           -webkit-text-fill-color:rgba(0,229,255,0.4);width:90px;">JD MATCH</span>
                    <div style="flex:1;height:4px;background:rgba(255,0,255,0.08);position:relative;">
                        <div style="width:{match}%;height:100%;
                             background:linear-gradient(90deg,#280030,{match_color});
                             position:relative;">
                            <div style="position:absolute;right:0;top:0;bottom:0;width:4px;
                                 background:#fff;box-shadow:0 0 6px {match_color};"></div>
                        </div>
                    </div>
                    <span style="font-family:'Orbitron',monospace;font-size:0.6rem;
                           color:{match_color};-webkit-text-fill-color:{match_color};width:36px;
                           text-align:right;">{match}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("AI INTELLIGENCE FEED")
            st.write(feedback)

            if issues:
                st.subheader("THREAT VECTORS DETECTED")
                for i in issues:
                    st.markdown(f"""
                    <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
                         color:#ff5555;-webkit-text-fill-color:#ff5555;
                         padding:5px 10px;border-left:2px solid #ff4444;
                         background:rgba(255,68,68,0.05);margin-bottom:4px;
                         letter-spacing:1px;">
                        ⚠ {i.upper()}
                    </div>
                    """, unsafe_allow_html=True)

            if missing:
                st.subheader("MISSING SKILL SIGNATURES")
                cols = st.columns(min(len(missing), 4))
                for idx, skill in enumerate(missing):
                    with cols[idx % len(cols)]:
                        st.markdown(f"""
                        <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;
                             color:rgba(255,0,255,0.7);-webkit-text-fill-color:rgba(255,0,255,0.7);
                             border:1px solid rgba(255,0,255,0.3);padding:4px 10px;
                             text-align:center;letter-spacing:1px;margin:2px;">
                            {skill.upper()}
                        </div>
                        """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠ SYSTEM CRASH :: {str(e)}")

# ══════════════════════════════════════════════════════════
#  TAB 2 — BUILDER
# ══════════════════════════════════════════════════════════

with tabs[1]:

    st.subheader("IDENTITY MATRIX")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        name = st.text_input("// OPERATOR NAME", placeholder="YOUR FULL NAME")
    with col_b:
        email = st.text_input("// COMM CHANNEL [EMAIL]", placeholder="EMAIL@DOMAIN.COM")
    with col_c:
        phone = st.text_input("// SIGNAL FREQ [PHONE]", placeholder="+XX-XXXX-XXXXXX")

    st.subheader("CAPABILITY ARRAY")

    skills = st.text_area("// SKILLS MODULE", placeholder="Python, React, AWS, Docker...", height=80)
    exp = st.text_area("// MISSION LOG [EXPERIENCE]", placeholder="Role @ Company — Built X, improved Y by Z%...", height=100)
    proj = st.text_area("// PROJECT DATABASE", placeholder="Project Name: Tech stack, impact metrics...", height=80)
    edu = st.text_area("// TRAINING RECORDS [EDUCATION]", placeholder="Degree, Institution, Year", height=80)

    preview = f"""{name}
{email} | {phone}

SKILLS:
{skills}

EXPERIENCE:
{exp}

PROJECTS:
{proj}

EDUCATION:
{edu}
"""

    st.subheader("LIVE PREVIEW FEED")
    st.code(preview, language=None)

    word_count = len(preview.split())
    st.markdown(f"""
    <p style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
       color:rgba(0,229,255,0.3);-webkit-text-fill-color:rgba(0,229,255,0.3);
       letter-spacing:2px;text-align:right;margin-top:-0.5rem;">
       TOKEN COUNT :: {word_count} WORDS COMPILED
    </p>
    """, unsafe_allow_html=True)

    if st.button("⬡ COMPILE RESUME OUTPUT"):

        doc = Document()
        for line in preview.split("\n"):
            doc.add_paragraph(line)
        doc.save("resume.docx")

        pdf_file = export_pdf(preview)

        st.markdown("""
        <div style="font-family:'Orbitron',monospace;font-size:0.6rem;
             color:#00ff88;-webkit-text-fill-color:#00ff88;
             letter-spacing:3px;text-align:center;padding:0.5rem;
             border:1px solid rgba(0,255,136,0.3);
             background:rgba(0,255,136,0.04);margin:0.5rem 0;">
            ✓ COMPILE SUCCESSFUL — FILES READY FOR TRANSMISSION
        </div>
        """, unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            with open("resume.docx", "rb") as f:
                st.download_button("⬡ DOWNLOAD DOCX", f, "resume.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with col_dl2:
            with open(pdf_file, "rb") as f:
                st.download_button("⬡ DOWNLOAD PDF", f, "resume.pdf",
                                   mime="application/pdf")

# ─── FOOTER ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center;margin-top:2rem;padding-top:1rem;
     border-top:1px solid rgba(0,229,255,0.1);">
    <p style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
       color:rgba(0,229,255,0.2);-webkit-text-fill-color:rgba(0,229,255,0.2);
       letter-spacing:3px;margin:0;">
       /// ACADENCE NEURAL INTERFACE v4.2 /// POWERED BY GEMINI-2.5-FLASH /// ATS ENGINE ARMED ///
    </p>
</div>
""", unsafe_allow_html=True)