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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #05060e !important;
    color: #b8c4de;
    font-family: 'Inter', system-ui, sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #070814 !important;
    border-right: 1px solid #0f1628 !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { opacity:1 !important; visibility:visible !important; }
footer,[data-testid="stDecoration"],
[data-testid="stToolbar"],[data-testid="stStatusWidget"] { display:none !important; }
.block-container { max-width:860px !important; padding:2rem 2rem 6rem !important; }

/* ── Sidebar internals ── */
.sb-logo { padding:6px 0 18px; }
.sb-name { font-size:1.15rem; font-weight:700; letter-spacing:-0.035em; color:#e6eeff; }
.sb-name em {
    font-style:normal;
    background:linear-gradient(110deg,#4d7fff,#a066ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.sb-tag { font-family:'JetBrains Mono',monospace; font-size:0.56rem; font-weight:600;
          letter-spacing:0.2em; text-transform:uppercase; color:#141e36;
          display:block; margin-top:3px; }
.sb-div { border:none; border-top:1px solid #0c1122; margin:12px 0; }
.sb-sec { font-family:'JetBrains Mono',monospace; font-size:0.54rem; font-weight:700;
          letter-spacing:0.22em; text-transform:uppercase; color:#0f1a30; margin-bottom:8px; }
.sb-node { display:flex; gap:9px; align-items:flex-start; padding:7px 0;
           border-bottom:1px solid #080e1c; }
.sb-node:last-child { border-bottom:none; }
.sb-nnum { width:20px; height:20px; border-radius:50%; border:1px solid #14203c;
           font-family:'JetBrains Mono',monospace; font-size:0.56rem; font-weight:700;
           color:#4d7fff; display:flex; align-items:center; justify-content:center;
           flex-shrink:0; margin-top:1px; }
.sb-nlabel { font-size:0.75rem; font-weight:600; color:#96a8cc; }
.sb-ndesc  { font-size:0.63rem; color:#1a2840; margin-top:1px; line-height:1.4; }
.sb-kv { display:flex; justify-content:space-between; align-items:center;
         padding:5px 0; border-bottom:1px solid #080e1c; }
.sb-kv:last-child { border-bottom:none; }
.sb-k { font-size:0.68rem; color:#182038; }
.sb-v { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#2e4060; }

/* ── Page header ── */
.page-hdr {
    display:flex; align-items:flex-start; justify-content:space-between;
    padding-bottom:1.5rem; margin-bottom:1.75rem;
    border-bottom:1px solid #0c1122;
}
.ph-title { font-size:1.6rem; font-weight:700; letter-spacing:-0.04em; color:#e6eeff; line-height:1; }
.ph-title em {
    font-style:normal;
    background:linear-gradient(110deg,#4d7fff 0%,#a066ff 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.ph-sub { font-size:0.72rem; color:#1a2840; margin-top:6px; line-height:1.5;
          font-family:'JetBrains Mono',monospace; letter-spacing:0.04em; }
.ph-badges { display:flex; gap:6px; margin-top:2px; flex-wrap:wrap; }
.ph-badge { font-size:0.64rem; color:#1e2d50; border:1px solid #0f1628;
            border-radius:4px; padding:3px 9px; font-weight:500; }

/* ── Input area ── */
.input-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:600;
               letter-spacing:0.18em; text-transform:uppercase; color:#14203c;
               margin-bottom:6px; }

/* ── Pipeline tracker ── */
.tracker { display:flex; border:1px solid #0c1122; border-radius:10px;
           overflow:hidden; margin:1.5rem 0 1.75rem; }
.ts {
    flex:1; display:flex; flex-direction:column; align-items:center;
    padding:10px 6px 9px; position:relative;
    border-right:1px solid #0c1122; background:#060810;
    transition:background .2s;
}
.ts:last-child { border-right:none; }
.ts.active { background:#080d1e; }
.ts.done   { background:#060f0a; }
.ts-n {
    font-family:'JetBrains Mono',monospace; font-size:0.56rem; font-weight:700;
    letter-spacing:0.06em; color:#0f1a30; margin-bottom:3px;
}
.ts.active .ts-n { color:#4d7fff; }
.ts.done   .ts-n { color:#259956; }
.ts-label { font-size:0.62rem; font-weight:600; color:#0f1a30; text-align:center; line-height:1.2; }
.ts.active .ts-label { color:#7a9fff; }
.ts.done   .ts-label { color:#2eaa6a; }
.ts-pip { width:4px; height:4px; border-radius:50%; background:#0c1122; margin-top:5px; }
.ts.active .ts-pip { background:#4d7fff; box-shadow:0 0 5px #4d7fff99; }
.ts.done   .ts-pip { background:#2eaa6a; }

/* ── Step card ── */
.scard { border:1px solid #0c1122; border-radius:10px; overflow:hidden; margin-bottom:8px; }
.scard-hdr { display:flex; align-items:center; gap:9px; padding:10px 16px; background:#06080f; }
.scard-body { border-top:1px solid #0a0f1e; padding:12px 16px; background:#050710; }
.sc-tag {
    font-family:'JetBrains Mono',monospace; font-size:0.56rem; font-weight:700;
    letter-spacing:0.08em; color:#4d7fff; background:#090e1e;
    border:1px solid #141e38; border-radius:4px; padding:2px 7px; white-space:nowrap;
}
.sc-name { flex:1; font-size:0.83rem; font-weight:600; color:#ccd8f5; }
.sc-ok  { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#2eaa6a; }
.sc-run { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#d4912a;
          display:flex; align-items:center; gap:5px; }
.sc-run::before {
    content:''; width:5px; height:5px; border-radius:50%;
    background:#d4912a; display:inline-block;
    animation:blink 1s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }

/* ── Tavily answer ── */
.tav { background:#060c1c; border:1px solid #12194a;
       border-left:3px solid #4d7fff; border-radius:8px; padding:13px 16px; }
.tav-eye { font-family:'JetBrains Mono',monospace; font-size:0.55rem; font-weight:700;
           letter-spacing:0.2em; text-transform:uppercase; color:#3d5fcc; margin-bottom:7px; }
.tav-txt { font-size:0.82rem; line-height:1.72; color:#7a8aae; }

/* ── Search result card ── */
.rc { background:#050710; border:1px solid #0a0f1e; border-radius:7px;
      padding:10px 14px; margin-bottom:5px; }
.rc:last-child { margin-bottom:0; }
.rc-n { font-family:'JetBrains Mono',monospace; font-size:0.55rem; color:#142030;
        font-weight:700; margin-bottom:3px; }
.rc-title { font-size:0.79rem; font-weight:600; color:#a8b8d8; line-height:1.35; margin-bottom:2px; }
.rc-url   { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#3a5fcc;
            display:block; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rc-snip  { font-size:0.73rem; color:#2e3e5a; line-height:1.55; }

/* ── Scrape table ── */
.stbl { border:1px solid #0a0f1e; border-radius:8px; overflow:hidden; }
.srow { display:flex; align-items:center; justify-content:space-between; gap:10px;
        padding:7px 12px; border-bottom:1px solid #080b18; background:#050710; }
.srow:last-child { border-bottom:none; }
.srow-i { font-family:'JetBrains Mono',monospace; font-size:0.55rem; color:#101828; min-width:16px; }
.srow-u { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#1e2e48;
          overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }
.srow-r { display:flex; align-items:center; gap:5px; flex-shrink:0; }
.p-ok  { background:#05120a; color:#2eaa6a; border:1px solid #0a2818;
         border-radius:99px; padding:1px 8px; font-size:0.6rem; font-weight:600;
         font-family:'JetBrains Mono',monospace; }
.p-err { background:#120508; color:#c03858; border:1px solid #280a14;
         border-radius:99px; padding:1px 8px; font-size:0.6rem; font-weight:600;
         font-family:'JetBrains Mono',monospace; }
.srow-ch { font-size:0.58rem; color:#0e1828; font-family:'JetBrains Mono',monospace; }

/* ── Reader progress rows ── */
.rr-wrap { border:1px solid #0a0f1e; border-radius:8px; overflow:hidden; }
.rr { display:flex; align-items:center; gap:9px; padding:7px 12px;
      border-bottom:1px solid #080b18; background:#050710; }
.rr:last-child { border-bottom:none; }
.rr.rr-done   { background:#050a07; }
.rr.rr-active { background:#06080f; }
.rr-i { font-family:'JetBrains Mono',monospace; font-size:0.55rem; color:#101828; min-width:18px; }
.rr-t { font-size:0.73rem; color:#1e2e48; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rr.rr-done   .rr-t { color:#1e3a28; }
.rr.rr-active .rr-t { color:#6a88cc; }
.rr-s { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#101828; }
.rr-s.ok  { color:#2eaa6a; }
.rr-s.run { color:#d4912a; }

/* ── Summary card ── */
.sumcard { background:#050710; border:1px solid #0a0f1e; border-radius:8px;
           padding:13px 16px; margin-bottom:6px; }
.sumcard:last-child { margin-bottom:0; }
.sumcard-eye { font-family:'JetBrains Mono',monospace; font-size:0.54rem; font-weight:700;
               letter-spacing:0.2em; text-transform:uppercase; color:#6040aa; margin-bottom:6px; }
.sumcard-title { font-size:0.79rem; font-weight:600; color:#b8c8e8; margin-bottom:2px; }
.sumcard-url   { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#3a5fcc;
                 display:block; margin-bottom:9px; }
.sumcard-body  { font-size:0.75rem; color:#3a4a6a; line-height:1.78; white-space:pre-wrap; }

/* ── Context inline line ── */
.ctx-line { display:flex; align-items:center; gap:10px; padding:9px 14px;
            background:#050710; border:1px solid #0a0f1e; border-radius:8px; }
.ctx-dot { width:6px; height:6px; border-radius:50%; background:#0a0f1e; flex-shrink:0; }
.ctx-dot.ok { background:#2eaa6a; }
.ctx-txt { font-size:0.76rem; color:#1e2e48; flex:1; }
.ctx-txt strong { color:#3a5fcc; font-weight:600; font-family:'JetBrains Mono',monospace; }
.ctx-pill { font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#2eaa6a;
            background:#05120a; border:1px solid #0a2818; border-radius:4px; padding:2px 8px; }

/* ── Score card ── */
.score-card { display:inline-flex; align-items:center; gap:14px;
              background:#060c1c; border:1px solid #12194a;
              border-radius:10px; padding:12px 20px; }
.score-val {
    font-size:2.1rem; font-weight:700; font-family:'JetBrains Mono',monospace; line-height:1;
    background:linear-gradient(110deg,#4d7fff,#a066ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.score-info { display:flex; flex-direction:column; gap:2px; }
.score-lbl { font-size:0.6rem; font-weight:700; letter-spacing:0.18em;
             text-transform:uppercase; color:#1a2840; }
.score-sub { font-size:0.7rem; color:#2a3a5a; }

/* ── Run summary panel ── */
.rs { background:#060810; border:1px solid #0c1122; border-radius:12px; overflow:hidden; margin-top:1.5rem; }
.rs-hdr { display:flex; align-items:center; justify-content:space-between;
          padding:13px 18px; border-bottom:1px solid #0c1122; background:#07091a; }
.rs-htitle { font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:700;
             letter-spacing:0.18em; text-transform:uppercase; color:#1a2840; }
.rs-hscore { font-family:'JetBrains Mono',monospace; font-size:0.75rem; font-weight:700;
             color:#4d7fff; }
.rs-body { display:grid; grid-template-columns:repeat(4,1fr); }
.rs-col { padding:14px 18px; border-right:1px solid #0c1122; }
.rs-col:last-child { border-right:none; }
.rs-clabel { font-family:'JetBrains Mono',monospace; font-size:0.55rem; font-weight:700;
             letter-spacing:0.2em; text-transform:uppercase; color:#4d7fff; margin-bottom:10px; }
.rs-row { display:flex; justify-content:space-between; align-items:baseline;
          padding:4px 0; border-bottom:1px solid #09101c; }
.rs-row:last-child { border-bottom:none; }
.rs-k { font-size:0.7rem; color:#1a2840; }
.rs-v { font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#384a6a; font-weight:500; }
.rs-v.ok  { color:#2eaa6a; }
.rs-v.err { color:#c03858; }
.rs-v.hi  { color:#4d7fff; }

/* ── Log box ── */
.logbox { background:#030509; border:1px solid #090c18; border-radius:8px; padding:10px 14px;
          font-family:'JetBrains Mono',monospace; font-size:0.64rem; color:#1a2840;
          line-height:1.9; max-height:220px; overflow-y:auto; white-space:pre-wrap; }
.logbox::-webkit-scrollbar { width:3px; }
.logbox::-webkit-scrollbar-thumb { background:#0c1122; border-radius:2px; }

/* ── Streamlit overrides ── */
.stTextInput>div>div>input {
    background:#07091a !important; border:1px solid #0c1122 !important;
    border-radius:8px !important; color:#e6eeff !important;
    font-size:0.87rem !important; padding:10px 14px !important;
    font-family:'Inter',sans-serif !important;
}
.stTextInput>div>div>input::placeholder { color:#1a2840 !important; }
.stTextInput>div>div>input:focus {
    border-color:#4d7fff !important; box-shadow:0 0 0 3px rgba(77,127,255,.08) !important;
}
.stTextInput>label { display:none !important; }
.stButton>button {
    background:linear-gradient(120deg,#2a56ff 0%,#7030ff 100%) !important;
    color:#fff !important; border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:0.84rem !important;
    padding:10px 18px !important; letter-spacing:0.01em !important;
    font-family:'Inter',sans-serif !important;
}
.stButton>button:hover { opacity:.85 !important; }
.stDownloadButton>button {
    background:#07091a !important; color:#4d7fff !important;
    border:1px solid #141e38 !important; border-radius:8px !important;
    font-size:0.76rem !important; font-weight:500 !important; padding:7px 14px !important;
}
.stProgress>div>div>div>div {
    background:linear-gradient(90deg,#2a56ff,#7030ff) !important; border-radius:99px !important;
}
[data-testid="stExpander"] {
    background:#050710 !important; border:1px solid #0a0f1e !important;
    border-radius:8px !important; margin-top:4px;
}
[data-testid="stExpander"]>details>summary {
    font-size:0.74rem !important; color:#1e2e48 !important;
    font-weight:500 !important; padding:8px 13px !important;
    font-family:'Inter',sans-serif !important;
}
[data-testid="stExpander"]>details>summary:hover { color:#7a9fff !important; }
[data-testid="stAlert"] { border-radius:8px !important; font-size:0.79rem !important; }
[data-testid="stMarkdownContainer"] p { margin-bottom:0.4em; }
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

def tracker(done_up_to):   # done_up_to: number of steps fully completed (0–6)
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

    st.markdown("<hr class='sb-div'>", unsafe_allow_html=True)
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
    st.markdown("""<div style="font-size:0.66rem;color:#0f1828;line-height:1.9">
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
    run = st.button("Run →", use_container_width=True, type="primary")

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
        "<div style='font-size:0.74rem;color:#1e2e48;padding:2px 0'>Querying Tavily Advanced…</div>"
    ), unsafe_allow_html=True)

    try:
        state = search_sources(state)
    except Exception as ex:
        st.error(f"Search failed: {ex}"); st.stop()

    tav = ""
    if state.tavily_answer:
        tav = (f'<div class="tav">'
               f'<div class="tav-eye">⬡ Tavily AI Answer</div>'
               f'<div class="tav-txt">{plain(state.tavily_answer, 600)}</div></div>')

    s1.markdown(scard("01 · SEARCH","Web Search",
        f"✓  {len(state.search_results)} sources retrieved","ok", tav
    ), unsafe_allow_html=True)

    with st.expander(f"View {len(state.search_results)} search results"):
        html = "".join(
            f'<div class="rc">'
            f'<div class="rc-n">RESULT {i:02d}</div>'
            f'<div class="rc-title">{e(r["title"])}</div>'
            f'<span class="rc-url">{e(r["url"])}</span>'
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
        "<div style='font-size:0.74rem;color:#1e2e48;padding:2px 0'>Initialising scraper…</div>"
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
            elif j == current_idx: cls, lbl = "rr-active",  "<span class='rr-s run'>reading…</span>"
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
            f'<span class="sumcard-url">{e(s["url"])}</span>'
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
        "<div style='font-size:0.74rem;color:#1e2e48;padding:2px 0'>Synthesising research…</div>"
    ), unsafe_allow_html=True)

    try:
        state = generate_report(state)
    except Exception as ex:
        st.error(f"Writer failed: {ex}"); st.stop()

    s5.markdown(scard("05 · WRITER","Writer Agent — Drafting Report",
        f"✓  {state.metrics['report_words']:,} words","ok",""
    ), unsafe_allow_html=True)

    with st.expander("📄 View Full Report", expanded=True):
        st.markdown(state.report)

    st.download_button("⬇  Download Report (.md)",
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
        "<div style='font-size:0.74rem;color:#1e2e48;padding:2px 0'>Evaluating report…</div>"
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

    with st.expander("📋 View Full Critic Feedback", expanded=True):
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
    <span class="rs-htitle">⬡ Run Summary</span>
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
      <div class="rs-row"><span class="rs-k">Total chars</span><span class="rs-v hi">{m.get('context_chars',0):,}</span></div>
      <div class="rs-row"><span class="rs-k">Sources used</span><span class="rs-v">{len(summaries)}</span></div>
    </div>
    <div class="rs-col">
      <div class="rs-clabel">Output</div>
      <div class="rs-row"><span class="rs-k">Report words</span><span class="rs-v hi">{m.get('report_words',0):,}</span></div>
      <div class="rs-row"><span class="rs-k">Review words</span><span class="rs-v">{m.get('feedback_words',0):,}</span></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    with st.expander("🗒  View pipeline logs"):
        st.markdown(f'<div class="logbox">{e(chr(10).join(state.logs))}</div>',
                    unsafe_allow_html=True)
