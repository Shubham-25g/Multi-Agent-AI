import streamlit as st
import html as html_lib
import re
from workflow.state import ResearchState
from workflow.search import search_sources
from workflow.context import build_research_context
from workflow.writer import generate_report
from workflow.critic import review_report
from workflow.config import TARGET_SOURCES, MIN_CONTENT_LENGTH, BAD_KEYWORDS
from agents import reader_chain
from tools import scrape_url

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepResearch · Multi-Agent AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0b0c10;
    --surface: #14161a;
    --border: #282b33;
    --border-hover: #3d424e;
    
    --text-primary: #f0f2f5;
    --text-secondary: #9ba1a6;
    --text-tertiary: #686e75;
    
    --positive: #57b77d;
    --positive-bg: rgba(87, 183, 125, 0.12);
    --positive-border: rgba(87, 183, 125, 0.25);
    
    --negative: #d65d5d;
    --negative-bg: rgba(214, 93, 93, 0.12);
    --negative-border: rgba(214, 93, 93, 0.25);
    
    --neutral: #d4a76a;
    --neutral-bg: rgba(212, 167, 106, 0.12);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text-primary);
    font-family: 'Inter', system-ui, sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { opacity:1 !important; visibility:visible !important; color: var(--text-secondary) !important; }
footer, [data-testid="stDecoration"],
[data-testid="stToolbar"], [data-testid="stStatusWidget"] { display:none !important; }
.block-container { max-width: 1100px !important; padding: 3rem 2rem 6rem !important; }

/* ── Sidebar internals ── */
.sb-logo { padding: 6px 0 24px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
.sb-name { font-family: 'Newsreader', serif; font-size: 26px; font-weight: 500; letter-spacing: -0.02em; color: var(--text-primary); display: flex; align-items: baseline; }
.sb-name em { font-style: normal; color: var(--text-secondary); font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 500; margin-left: 4px; letter-spacing: 0; }
.sb-tag { font-family: 'Inter', sans-serif; font-size: 12px; color: var(--text-secondary); display: block; margin-top: 4px; }

.sb-div { border:none; border-top: 1px solid var(--border); margin: 24px 0; }
.sb-sec { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 16px; }

.sb-node { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; }
.sb-nnum { width: 22px; height: 22px; border-radius: 4px; border: 1px solid var(--border); background: var(--surface);
           font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
           color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
           flex-shrink: 0; margin-top: 2px; }
.sb-nlabel { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.sb-ndesc  { font-size: 12px; color: var(--text-secondary); margin-top: 2px; line-height: 1.5; }

.sb-kv { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border); }
.sb-kv:last-child { border-bottom: none; }
.sb-k { font-size: 12px; color: var(--text-secondary); }
.sb-v { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-primary); }

/* ── Page header ── */
.page-hdr {
    display: flex; align-items: flex-end; justify-content: space-between;
    padding-bottom: 28px; margin-bottom: 36px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap; gap: 20px;
}
.ph-title { font-family: 'Newsreader', serif; font-size: 36px; font-weight: 500; letter-spacing: -0.02em; color: var(--text-primary); display: flex; align-items: baseline; line-height: 1; }
.ph-title em { font-style: normal; color: var(--text-secondary); font-family: 'Inter', sans-serif; font-size: 20px; font-weight: 500; margin-left: 6px; letter-spacing: 0; }
.ph-sub { font-size: 14px; color: var(--text-secondary); margin-top: 10px; }
.ph-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.ph-badge { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-secondary); 
            border: 1px solid var(--border); background: var(--surface); border-radius: 4px; padding: 4px 10px; text-transform: uppercase; letter-spacing: 0.04em; }

/* ── Input area ── */
.input-label { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px; }

/* ── Pipeline tracker ── */
.tracker { display: flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin: 1.5rem 0; background: var(--surface); }
.ts {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 8px; position: relative; border-right: 1px solid var(--border);
    transition: background 0.3s ease;
}
.ts:last-child { border-right: none; }
.ts.active { background: var(--border); }
.ts.done   { background: var(--bg); }
.ts-n { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; color: var(--text-tertiary); margin-bottom: 2px; }
.ts.active .ts-n { color: var(--text-primary); }
.ts.done   .ts-n { color: var(--text-secondary); }
.ts-label { font-size: 12px; font-weight: 500; color: var(--text-tertiary); text-align: center; }
.ts.active .ts-label { color: var(--text-primary); }
.ts.done   .ts-label { color: var(--text-secondary); }
.ts-pip { width: 4px; height: 4px; border-radius: 50%; background: var(--border-hover); margin-top: 4px; transition: all 0.3s ease; }
.ts.active .ts-pip { background: var(--text-primary); }
.ts.done   .ts-pip { background: var(--text-tertiary); }

/* ── Step card ── */
.scard { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.scard-hdr { display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-bottom: 1px solid var(--border); }
.scard-body { padding: 20px; background: var(--bg); }
.sc-tag { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; color: var(--text-secondary); background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; white-space: nowrap; }
.sc-name { flex: 1; font-size: 14px; font-weight: 600; color: var(--text-primary); }
.sc-ok  { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--positive); display: flex; align-items: center; gap: 6px; }
.sc-run { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }
.sc-run::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--text-secondary); display: inline-block; animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── Tavily answer ── */
.tav { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--text-secondary); border-radius: 6px; padding: 16px 20px; }
.tav-eye { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px; }
.tav-txt { font-size: 14px; line-height: 1.6; color: var(--text-primary); }

/* ── Search result card ── */
.rc { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; transition: border-color .2s ease; }
.rc:hover { border-color: var(--border-hover); }
.rc:last-child { margin-bottom: 0; }
.rc-n { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-tertiary); font-weight: 600; margin-bottom: 6px; }
.rc-title { font-size: 15px; font-weight: 500; color: var(--text-primary); line-height: 1.4; margin-bottom: 4px; }
.rc-url   { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-decoration: none; }
.rc-snip  { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }

/* ── Scrape table ── */
.stbl { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: transparent; }
.srow { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--surface); }
.srow:last-child { border-bottom: none; }
.srow-i { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-tertiary); min-width: 20px; }
.srow-u { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.srow-r { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.p-ok  { background: var(--positive-bg); color: var(--positive); border: 1px solid var(--positive-border); border-radius: 4px; padding: 4px 10px; font-size: 10px; font-weight: 600; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
.p-err { background: var(--negative-bg); color: var(--negative); border: 1px solid var(--negative-border); border-radius: 4px; padding: 4px 10px; font-size: 10px; font-weight: 600; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
.srow-ch { font-size: 11px; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; min-width: 60px; text-align: right; }

/* ── Reader progress rows ── */
.rr-wrap { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.rr { display: flex; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--surface); }
.rr:last-child { border-bottom: none; }
.rr.rr-done   { background: var(--bg); }
.rr.rr-active { background: var(--border); }
.rr-i { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-tertiary); min-width: 20px; }
.rr-t { font-size: 13px; color: var(--text-primary); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rr.rr-done   .rr-t { color: var(--text-secondary); }
.rr-s { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-tertiary); }
.rr-s.ok  { color: var(--positive); }
.rr-s.run { color: var(--text-primary); display: flex; align-items: center; gap: 6px; }
.rr-s.run::before { content: ''; width: 4px; height: 4px; border-radius: 50%; background: var(--text-primary); display: inline-block; animation: pulse 1s infinite; }

/* ── Summary card ── */
.sumcard { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 12px; }
.sumcard:last-child { margin-bottom: 0; }
.sumcard-eye { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px; }
.sumcard-title { font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.sumcard-url   { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 16px; }
.sumcard-body  { font-size: 14px; color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; }

/* ── Context inline line ── */
.ctx-line { display: flex; align-items: center; gap: 12px; padding: 14px 20px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
.ctx-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-tertiary); flex-shrink: 0; }
.ctx-dot.ok { background: var(--positive); box-shadow: 0 0 8px rgba(87, 183, 125, 0.4); }
.ctx-txt { font-size: 13px; color: var(--text-primary); flex: 1; }
.ctx-txt strong { color: var(--text-primary); font-weight: 600; }
.ctx-pill { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-secondary); background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 4px 10px; text-transform: uppercase; }

/* ── Score card ── */
.score-card { display: inline-flex; align-items: center; gap: 20px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 24px; }
.score-val { font-family: 'Newsreader', serif; font-size: 42px; font-weight: 400; line-height: 1; color: var(--text-primary); }
.score-info { display: flex; flex-direction: column; gap: 4px; }
.score-lbl { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); }
.score-sub { font-size: 13px; color: var(--text-tertiary); }

/* ── Run summary panel ── */
.rs { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.rs-hdr { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; border-bottom: 1px solid var(--border); background: transparent; }
.rs-htitle { font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); }
.rs-hscore { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: var(--text-primary); background: var(--bg); border: 1px solid var(--border); padding: 4px 10px; border-radius: 4px; }
.rs-body { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
.rs-col { padding: 24px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); background: var(--bg); }
.rs-col:last-child { border-right: none; }
.rs-clabel { font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
.rs-row { display: flex; justify-content: space-between; align-items: baseline; padding: 6px 0; }
.rs-k { font-size: 13px; color: var(--text-secondary); }
.rs-v { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-primary); font-weight: 500; }
.rs-v.ok  { color: var(--positive); }
.rs-v.err { color: var(--negative); }

/* ── Log box ── */
.logbox { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px;
          font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-secondary);
          line-height: 1.8; max-height: 300px; overflow-y: auto; white-space: pre-wrap; }

/* ── Streamlit overrides ── */
.stTextInput>div>div>input {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 6px !important; color: var(--text-primary) !important;
    font-size: 14px !important; padding: 0 16px !important; height: 42px !important;
    font-family: 'Inter', sans-serif !important; transition: border-color .2s ease;
}
.stTextInput>div>div>input::placeholder { color: var(--text-tertiary) !important; }
.stTextInput>div>div>input:focus { border-color: var(--text-primary) !important; box-shadow: none !important; }
.stTextInput>label { display: none !important; }

.stButton>button {
    background: var(--text-primary) !important; color: var(--bg) !important;
    border: none !important; border-radius: 6px !important;
    font-weight: 500 !important; font-size: 14px !important;
    padding: 0 24px !important; height: 42px !important; letter-spacing: 0 !important;
    font-family: 'Inter', sans-serif !important; transition: all .2s ease !important;
    display: flex !important; align-items: center !important; justify-content: center !important; line-height: 1 !important;
}
.stButton>button:hover { background: #ffffff !important; box-shadow: 0 4px 12px rgba(255,255,255,0.1) !important; transform: translateY(-1px); }

.stDownloadButton>button {
    background: var(--surface) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border) !important; border-radius: 6px !important;
    font-size: 13px !important; font-weight: 500 !important; padding: 10px 20px !important;
    transition: all .2s ease !important;
}
.stDownloadButton>button:hover { border-color: var(--text-secondary) !important; background: var(--border) !important; }

/* Progress bar strictly minimalist */
.stProgress>div>div>div>div { background: var(--text-primary) !important; border-radius: 99px !important; }

[data-testid="stExpander"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; margin-top: 8px; overflow: hidden;
}
[data-testid="stExpander"]>details>summary {
    font-size: 13px !important; color: var(--text-primary) !important;
    font-weight: 500 !important; padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important; background: transparent !important;
}
[data-testid="stExpander"]>details>summary:hover { color: var(--text-secondary) !important; }
[data-testid="stAlert"] { border-radius: 8px !important; font-size: 14px !important; border: 1px solid var(--border) !important; background: var(--surface) !important; color: var(--text-primary) !important; }
[data-testid="stMarkdownContainer"] p { margin-bottom: 0.6em; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def e(t):
    return html_lib.escape(str(t))

def plain(t, maxlen=250):
    t = str(t)[:maxlen]
    t = re.sub(r'#+\s*', '', t)
    t = re.sub(r'\*{1,3}|_{1,2}', '', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'`+', '', t)
    return html_lib.escape(t.strip())

def scard(tag, name, status, cls, body=""):
    status_html = f'<span class="sc-{cls}">{e(status)}</span>' if status else ""
    body_html   = f'<div class="scard-body">{body}</div>' if body.strip() else ""
    return (f'<div class="scard">'
            f'<div class="scard-hdr">'
            f'<span class="sc-tag">{tag}</span>'
            f'<span class="sc-name">{name}</span>'
            f'{status_html}</div>'
            f'{body_html}</div>')

STEPS = ["Search", "Scrape", "Reader", "Context", "Writer", "Critic"]

def tracker(done_up_to):
    items = ""
    for i, name in enumerate(STEPS):
        if i < done_up_to:      cls = "done"
        elif i == done_up_to:   cls = "active"
        else:                   cls = ""
        items += (f'<div class="ts {cls}">'
                  f'<span class="ts-n">0{i+1}</span>'
                  f'<span class="ts-label">{name}</span>'
                  f'<div class="ts-pip"></div></div>')
    return f'<div class="tracker">{items}</div>'

def stbl(rows):
    return '<div class="stbl">' + "".join(rows) + "</div>"

def srow(idx, url, ok, chars=0):
    pill = f"<span class='p-ok'>ok</span>" if ok else f"<span class='p-err'>skip</span>"
    ch   = f"<span class='srow-ch'>{chars:,} ch</span>" if ok else ""
    return (f'<div class="srow">'
            f'<span class="srow-i">{idx:02d}</span>'
            f'<span class="srow-u">{e(url)}</span>'
            f'<span class="srow-r">{pill}{ch}</span></div>')

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-name">Deep<em>Research</em></div>
        <span class="sb-tag">Multi-Agent Pipeline</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sb-sec'>Architecture</div>", unsafe_allow_html=True)
    for num, name, desc in [
        ("01","Search",         "Tavily Advanced · up to 20 results"),
        ("02","Scraper",        "Trafilatura · clean text extraction"),
        ("03","Reader Agent",   "LLM · structured per-source summary"),
        ("04","Context Builder","Merges all signals into one prompt"),
        ("05","Writer Agent",   "LLM · full professional report"),
        ("06","Critic Agent",   "LLM · quality review + numeric score"),
    ]:
        st.markdown(f"""
        <div class="sb-node">
            <div class="sb-nnum">{num}</div>
            <div>
                <div class="sb-nlabel">{name}</div>
                <div class="sb-ndesc">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='sb-div'>", unsafe_allow_html=True)
    st.markdown("<div class='sb-sec'>Stack</div>", unsafe_allow_html=True)
    for k, v in [("LLM","mistral-medium-latest"),("Search","Tavily Advanced"),
                 ("Scraper","Trafilatura"),("Framework","LangChain"),("UI","Streamlit")]:
        st.markdown(f'<div class="sb-kv"><span class="sb-k">{k}</span>'
                    f'<span class="sb-v">{v}</span></div>', unsafe_allow_html=True)

    st.markdown("<hr class='sb-div'>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:12px;color:var(--text-tertiary);line-height:1.6">
        Search · Scrape · Summarise<br>Build context · Write · Critique
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hdr">
    <div>
        <div class="ph-title">Deep<em>Research</em></div>
        <div class="ph-sub">Autonomous 6-stage multi-agent research pipeline</div>
    </div>
    <div class="ph-badges">
        <span class="ph-badge">6-Stage Pipeline</span>
        <span class="ph-badge">Mistral AI</span>
        <span class="ph-badge">Tavily Search</span>
        <span class="ph-badge">LangChain</span>
    </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>Research Topic</div>", unsafe_allow_html=True)
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input("t",
        placeholder="e.g. 'Agentic AI frameworks in 2025 — benchmarks, real-world deployments and emerging patterns'",
        label_visibility="collapsed")
with col_btn:
    run = st.button("Run Analysis", use_container_width=True, type="primary")

# ─────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.error("Please enter a research topic.")
        st.stop()

    tracker_slot = st.empty()
    tracker_slot.markdown(tracker(0), unsafe_allow_html=True)
    progress = st.progress(0)

    state = ResearchState()
    state.topic = topic

    # ═══════════════════════════════════════
    # 01 · SEARCH
    # ═══════════════════════════════════════
    s1 = st.empty()
    s1.markdown(scard("01 · SEARCH","Web Search","running","run",
        "<div style='font-size:13px;color:var(--text-secondary);padding:2px 0'>Querying Tavily Advanced…</div>"
    ), unsafe_allow_html=True)

    try:
        state = search_sources(state)
    except Exception as ex:
        st.error(f"Search failed: {ex}"); st.stop()

    tav = ""
    if state.tavily_answer:
        tav = (f'<div class="tav">'
               f'<div class="tav-eye">Tavily AI Answer</div>'
               f'<div class="tav-txt">{plain(state.tavily_answer, 600)}</div></div>')

    s1.markdown(scard("01 · SEARCH","Web Search",
        f"✓  {len(state.search_results)} sources retrieved","ok", tav
    ), unsafe_allow_html=True)

    with st.expander(f"View {len(state.search_results)} search results"):
        html = "".join(
            f'<div class="rc">'
            f'<div class="rc-n">RESULT {i:02d}</div>'
            f'<div class="rc-title">{e(r["title"])}</div>'
            f'<a href="{e(r["url"])}" target="_blank" class="rc-url">{e(r["url"])}</a>'
            f'<div class="rc-snip">{plain(r["snippet"],200)}</div></div>'
            for i, r in enumerate(state.search_results, 1)
        )
        st.markdown(html, unsafe_allow_html=True)

    tracker_slot.markdown(tracker(1), unsafe_allow_html=True)
    progress.progress(17)

    # ═══════════════════════════════════════
    # 02 · SCRAPER
    # ═══════════════════════════════════════
    s2 = st.empty()
    s2.markdown(scard("02 · SCRAPE","Source Scraper","running","run",
        "<div style='font-size:13px;color:var(--text-secondary);padding:2px 0'>Initialising scraper…</div>"
    ), unsafe_allow_html=True)

    scraped, rows, attempted, accepted, skipped = [], [], 0, 0, 0

    for result in state.search_results:
        if accepted >= TARGET_SOURCES: break
        attempted += 1
        url = result["url"]
        try:    content = scrape_url.invoke({"url": url})
        except: content = ""; skipped += 1

        reason = None
        if not content:                                         reason = "empty"
        elif content.startswith("Scraping failed"):            reason = "failed"
        elif len(content) < MIN_CONTENT_LENGTH:                reason = "short"
        elif any(k in content.lower() for k in BAD_KEYWORDS): reason = "blocked"

        ok = reason is None
        if ok:
            scraped.append({"title":result["title"],"url":url,
                            "snippet":result["snippet"],"content":content})
            accepted += 1
        else:
            skipped += 1

        rows.append(srow(attempted, url, ok, len(content) if ok else 0))
        s2.markdown(scard("02 · SCRAPE","Source Scraper","running","run",
            stbl(rows)
        ), unsafe_allow_html=True)

    if not scraped:
        st.error("No pages scraped successfully."); st.stop()

    state.scraped_contents = scraped
    state.metrics.update({"attempted":attempted,"accepted":accepted,
                           "skipped":skipped,"target":TARGET_SOURCES})

    s2.markdown(scard("02 · SCRAPE","Source Scraper",
        f"✓  {accepted} accepted · {skipped} skipped","ok", stbl(rows)
    ), unsafe_allow_html=True)

    with st.expander(f"View {accepted} scraped page previews"):
        for page in scraped:
            st.markdown(f"**{e(page['title'])}**  \n`{e(page['url'])}`")
            st.code(page["content"][:500]+"…", language=None)

    tracker_slot.markdown(tracker(2), unsafe_allow_html=True)
    progress.progress(33)

    # ═══════════════════════════════════════
    # 03 · READER AGENT
    # ═══════════════════════════════════════
    s3 = st.empty()
    summaries = []

    def reader_rows_html(current_idx):
        html = ""
        for j, p in enumerate(scraped):
            if j < current_idx:    cls, lbl = "rr-done",   "<span class='rr-s ok'>✓ done</span>"
            elif j == current_idx: cls, lbl = "rr-active",  "<span class='rr-s run'>reading</span>"
            else:                  cls, lbl = "",            "<span class='rr-s'>pending</span>"
            html += (f'<div class="rr {cls}">'
                     f'<span class="rr-i">{j+1:02d}</span>'
                     f'<span class="rr-t">{e(p["title"][:68])}</span>'
                     f'{lbl}</div>')
        return f'<div class="rr-wrap">{html}</div>'

    for i, page in enumerate(scraped):
        s3.markdown(scard("03 · READER","Reader Agent — Summarising Sources","running","run",
            reader_rows_html(i)
        ), unsafe_allow_html=True)

        summary = reader_chain.invoke({
            "title":page["title"],"url":page["url"],"content":page["content"]
        })
        summaries.append({"title":page["title"],"url":page["url"],"summary":summary})

    state.summaries = summaries

    # All done
    done_rows = "".join(
        f'<div class="rr rr-done">'
        f'<span class="rr-i">{j+1:02d}</span>'
        f'<span class="rr-t">{e(p["title"][:68])}</span>'
        f'<span class="rr-s ok">✓ done</span></div>'
        for j, p in enumerate(scraped)
    )
    s3.markdown(scard("03 · READER","Reader Agent — Summarising Sources",
        f"✓  {len(summaries)} summaries generated","ok",
        f'<div class="rr-wrap">{done_rows}</div>'
    ), unsafe_allow_html=True)

    with st.expander(f"View {len(summaries)} AI-generated summaries"):
        sc_html = "".join(
            f'<div class="sumcard">'
            f'<div class="sumcard-eye">Source {i:02d} · Reader Summary</div>'
            f'<div class="sumcard-title">{e(s["title"])}</div>'
            f'<a href="{e(s["url"])}" target="_blank" class="sumcard-url">{e(s["url"])}</a>'
            f'<div class="sumcard-body">{e(s["summary"])}</div></div>'
            for i, s in enumerate(summaries, 1)
        )
        st.markdown(sc_html, unsafe_allow_html=True)

    tracker_slot.markdown(tracker(3), unsafe_allow_html=True)
    progress.progress(50)

    # ═══════════════════════════════════════
    # 04 · CONTEXT BUILDER  (inline)
    # ═══════════════════════════════════════
    s4 = st.empty()
    s4.markdown(
        '<div class="ctx-line">'
        '<div class="ctx-dot"></div>'
        '<span class="ctx-txt">Building research context…</span></div>',
        unsafe_allow_html=True)

    state = build_research_context(state)
    m = state.metrics

    s4.markdown(
        f'<div class="ctx-line">'
        f'<div class="ctx-dot ok"></div>'
        f'<span class="ctx-txt">Context assembled — '
        f'<strong>{m["context_chars"]:,} chars</strong> from '
        f'<strong>{m["accepted"]}</strong> sources</span>'
        f'<span class="ctx-pill">ready</span></div>',
        unsafe_allow_html=True)

    tracker_slot.markdown(tracker(4), unsafe_allow_html=True)
    progress.progress(67)

    # ═══════════════════════════════════════
    # 05 · WRITER
    # ═══════════════════════════════════════
    s5 = st.empty()
    s5.markdown(scard("05 · WRITER","Writer Agent — Drafting Report","running","run",
        "<div style='font-size:13px;color:var(--text-secondary);padding:2px 0'>Synthesising research…</div>"
    ), unsafe_allow_html=True)

    try:
        state = generate_report(state)
    except Exception as ex:
        st.error(f"Writer failed: {ex}"); st.stop()

    s5.markdown(scard("05 · WRITER","Writer Agent — Drafting Report",
        f"✓  {state.metrics['report_words']:,} words","ok",""
    ), unsafe_allow_html=True)

    with st.expander("View Full Report", expanded=True):
        st.markdown(state.report)

    st.download_button("Download Report (.md)",
        data=state.report,
        file_name=f"deepresearch_{re.sub(r'[^a-z0-9]+','_',topic.lower()[:45])}.md",
        mime="text/markdown")

    tracker_slot.markdown(tracker(5), unsafe_allow_html=True)
    progress.progress(84)

    # ═══════════════════════════════════════
    # 06 · CRITIC
    # ═══════════════════════════════════════
    s6 = st.empty()
    s6.markdown(scard("06 · CRITIC","Critic Agent — Quality Review","running","run",
        "<div style='font-size:13px;color:var(--text-secondary);padding:2px 0'>Evaluating report…</div>"
    ), unsafe_allow_html=True)

    try:
        state = review_report(state)
    except Exception as ex:
        st.error(f"Critic failed: {ex}"); st.stop()

    # Robust score extraction — strips **, __, `` from anywhere around "Score: X"
    score_line, feedback_lines = "", []
    for line in state.feedback.strip().splitlines():
        stripped = line.strip()
        if re.match(r'^[*_`\s]*score\s*:', stripped, re.IGNORECASE):
            score_line = re.sub(r'[*_`]','', re.split(r':',stripped,maxsplit=1)[1]).strip()
        else:
            feedback_lines.append(line)

    score_body = ""
    if score_line:
        score_body = (f'<div class="score-card">'
                      f'<div class="score-val">{e(score_line)}</div>'
                      f'<div class="score-info">'
                      f'<span class="score-lbl">Quality Score</span>'
                      f'<span class="score-sub">Critic Agent review</span>'
                      f'</div></div>')

    s6.markdown(scard("06 · CRITIC","Critic Agent — Quality Review",
        f"✓  score: {score_line}" if score_line else "✓  complete","ok",score_body
    ), unsafe_allow_html=True)

    with st.expander("View Full Critic Feedback", expanded=True):
        header = f"**Score: {score_line}**\n\n" if score_line else ""
        st.markdown(header + "\n".join(feedback_lines))

    tracker_slot.markdown(tracker(6), unsafe_allow_html=True)
    progress.progress(100)

    # ═══════════════════════════════════════
    # RUN SUMMARY
    # ═══════════════════════════════════════
    score_display = score_line if score_line else "—"
    st.markdown(f"""
<div class="rs">
  <div class="rs-hdr">
    <span class="rs-htitle">Run Summary</span>
    <span class="rs-hscore">Score {score_display}</span>
  </div>
  <div class="rs-body">
    <div class="rs-col">
      <div class="rs-clabel">Search</div>
      <div class="rs-row"><span class="rs-k">Results returned</span><span class="rs-v">{m.get('returned',0)}</span></div>
      <div class="rs-row"><span class="rs-k">Attempted scrape</span><span class="rs-v">{m.get('attempted',0)}</span></div>
    </div>
    <div class="rs-col">
      <div class="rs-clabel">Scraping</div>
      <div class="rs-row"><span class="rs-k">Accepted</span><span class="rs-v ok">{m.get('accepted',0)}</span></div>
      <div class="rs-row"><span class="rs-k">Skipped</span><span class="rs-v err">{m.get('skipped',0)}</span></div>
    </div>
    <div class="rs-col">
      <div class="rs-clabel">Context</div>
      <div class="rs-row"><span class="rs-k">Total chars</span><span class="rs-v">{m.get('context_chars',0):,}</span></div>
      <div class="rs-row"><span class="rs-k">Sources used</span><span class="rs-v">{len(summaries)}</span></div>
    </div>
    <div class="rs-col">
      <div class="rs-clabel">Output</div>
      <div class="rs-row"><span class="rs-k">Report words</span><span class="rs-v">{m.get('report_words',0):,}</span></div>
      <div class="rs-row"><span class="rs-k">Review words</span><span class="rs-v">{m.get('feedback_words',0):,}</span></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    with st.expander("View pipeline logs"):
        st.markdown(f'<div class="logbox">{e(chr(10).join(state.logs))}</div>',
                    unsafe_allow_html=True)