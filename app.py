import streamlit as st
import html as html_lib
from workflow.state import ResearchState
from workflow.search import search_sources
from workflow.scraper import scrape_sources
from workflow.reader import summarize_sources
from workflow.context import build_research_context
from workflow.writer import generate_report
from workflow.critic import review_report
from workflow.config import TARGET_SOURCES, MIN_CONTENT_LENGTH, BAD_KEYWORDS
from agents import reader_chain

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
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, .stApp { background:#080a10 !important; color:#bec8e0; font-family:'Inter',sans-serif; }

[data-testid="stSidebar"] { background:#0b0d16 !important; border-right:1px solid #161c30 !important; }
[data-testid="stSidebar"] * { color:#bec8e0 !important; }
#MainMenu, footer, header { visibility:hidden; }
[data-testid="stDecoration"] { display:none; }
.block-container { max-width:980px; padding:2rem 2.5rem 5rem; }

.wm { font-size:1.85rem; font-weight:700; letter-spacing:-0.04em; color:#e4ecff; margin:0; line-height:1; }
.wm-accent { background:linear-gradient(100deg,#4a7aff 0%,#9d6fff 100%);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.wm-sub { font-size:0.7rem; color:#2e3858; letter-spacing:0.18em; text-transform:uppercase;
          font-weight:600; margin-top:5px; font-family:'JetBrains Mono',monospace; }

.snode { display:flex; align-items:flex-start; gap:12px; padding:10px 0; border-bottom:1px solid #131828; }
.snode:last-child { border-bottom:none; }
.snode-num { width:24px; height:24px; border-radius:50%; border:1.5px solid #1e2848;
             display:flex; align-items:center; justify-content:center; font-size:0.65rem;
             font-weight:700; color:#4a7aff; flex-shrink:0; margin-top:1px; font-family:'JetBrains Mono',monospace; }
.snode-name { font-size:0.8rem; font-weight:600; color:#c0cce0; }
.snode-desc { font-size:0.68rem; color:#2e3858; margin-top:2px; line-height:1.4; }

.stack-row { display:flex; justify-content:space-between; padding:5px 0;
             border-bottom:1px solid #0f1422; font-size:0.73rem; }
.stack-k { color:#2e3858; }
.stack-v { color:#6478a8; font-family:'JetBrains Mono',monospace; font-size:0.68rem; }

.rule { border:none; border-top:1px solid #161c30; margin:1.25rem 0; }

/* ── Step card ── */
.step-card {
    border:1px solid #161c30; border-radius:10px;
    overflow:hidden; margin:1rem 0 0.3rem;
}
.step-hdr {
    display:flex; align-items:center; gap:10px;
    padding:12px 18px; background:#0c0f1c;
}
.step-body { background:#090c18; padding:14px 18px; border-top:1px solid #161c30; }
.step-tag { font-family:'JetBrains Mono',monospace; font-size:0.62rem; font-weight:600;
            color:#4a7aff; background:#0e1428; border:1px solid #1a2848;
            border-radius:4px; padding:2px 8px; letter-spacing:0.06em; white-space:nowrap; }
.step-name { flex:1; font-size:0.87rem; font-weight:600; color:#d8e2f8; }
.step-status-ok  { font-size:0.7rem; color:#3dba7a; font-family:'JetBrains Mono',monospace; }
.step-status-run { font-size:0.7rem; color:#c0a030; font-family:'JetBrains Mono',monospace; }

/* ── Tavily answer ── */
.tav-banner { background:#0c1224; border:1px solid #1a2848; border-left:3px solid #4a7aff;
              border-radius:6px; padding:13px 16px; font-size:0.82rem;
              line-height:1.7; color:#9aa8cc; margin-bottom:8px; }
.tav-label { font-size:0.6rem; font-weight:700; letter-spacing:0.16em;
             text-transform:uppercase; color:#4a7aff; margin-bottom:5px;
             font-family:'JetBrains Mono',monospace; }

/* ── Result card ── */
.rcard { background:#080b16; border:1px solid #131828; border-radius:7px;
         padding:11px 15px; margin-bottom:7px; }
.rcard-title { font-size:0.82rem; font-weight:600; color:#c0cce0; margin-bottom:3px; line-height:1.35; }
.rcard-url   { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4a7aff;
               display:block; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rcard-snip  { font-size:0.76rem; color:#4a5878; line-height:1.5; }

/* ── Scrape table ── */
.stbl { border:1px solid #131828; border-radius:8px; overflow:hidden; }
.srow { display:flex; align-items:center; justify-content:space-between;
        gap:12px; padding:9px 14px; border-bottom:1px solid #0c0f1c; background:#080b16; }
.srow:last-child { border-bottom:none; }
.srow-url { font-family:'JetBrains Mono',monospace; font-size:0.67rem;
            color:#344060; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:72%; }
.srow-right { display:flex; align-items:center; gap:7px; flex-shrink:0; }
.pill-ok  { background:#0b2218; color:#3dba7a; border:1px solid #143a28;
            border-radius:99px; padding:2px 9px; font-size:0.64rem; font-weight:600; font-family:'JetBrains Mono',monospace; }
.pill-err { background:#1e0c12; color:#c84060; border:1px solid #3c1822;
            border-radius:99px; padding:2px 9px; font-size:0.64rem; font-weight:600; font-family:'JetBrains Mono',monospace; }
.srow-chars { font-size:0.62rem; color:#1e2840; font-family:'JetBrains Mono',monospace; }

/* ── Summary card ── */
.sumcard { background:#080b16; border:1px solid #131828; border-radius:8px;
           padding:13px 16px; margin-bottom:9px; }
.sumcard-lbl { font-size:0.58rem; font-weight:700; letter-spacing:0.16em; text-transform:uppercase;
               color:#9d6fff; font-family:'JetBrains Mono',monospace; margin-bottom:5px; }
.sumcard-title { font-size:0.82rem; font-weight:600; color:#d0daf0; margin-bottom:3px; }
.sumcard-url   { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4a7aff; display:block; margin-bottom:9px; }
.sumcard-body  { font-size:0.78rem; color:#6878a0; line-height:1.7; white-space:pre-wrap; }

/* ── Metrics grid ── */
.mgrid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:6px 0 2px; }
.mbox  { background:#080b16; border:1px solid #131828; border-radius:8px; padding:13px 14px; text-align:center; }
.mbox-val { font-size:1.45rem; font-weight:700; color:#4a7aff; line-height:1; font-family:'JetBrains Mono',monospace; }
.mbox-lbl { font-size:0.6rem; color:#283048; text-transform:uppercase; letter-spacing:0.12em; margin-top:5px; font-weight:600; }

/* ── Context preview ── */
.ctx-preview { background:#080b16; border:1px solid #131828; border-radius:8px;
               padding:13px 16px; font-family:'JetBrains Mono',monospace;
               font-size:0.7rem; color:#344060; line-height:1.6; white-space:pre-wrap;
               max-height:200px; overflow:hidden; }
.ctx-fade { text-align:center; color:#1e2840; font-size:0.7rem; margin-top:6px; }

/* ── Score badge ── */
.score-wrap { display:inline-flex; align-items:center; gap:12px; background:#0c1224;
              border:1px solid #1a2848; border-radius:8px; padding:10px 22px; margin-bottom:12px; }
.score-num { font-size:1.6rem; font-weight:700; color:#4a7aff; line-height:1; font-family:'JetBrains Mono',monospace; }
.score-lbl { font-size:0.62rem; color:#2e3858; text-transform:uppercase; letter-spacing:0.12em; font-weight:600; }

/* ── Log console ── */
.logbox { background:#050710; border:1px solid #0f1422; border-radius:8px; padding:12px 16px;
          font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#2e4060;
          line-height:1.8; max-height:220px; overflow-y:auto; white-space:pre-wrap; }

/* ── Done banner ── */
.done-banner { background:#0c1224; border:1px solid #1a2848; border-radius:10px;
               padding:20px 24px; text-align:center; margin-top:1.5rem; }
.done-title { font-size:0.7rem; letter-spacing:0.18em; text-transform:uppercase;
              color:#2e3858; font-weight:700; font-family:'JetBrains Mono',monospace; }
.done-sub { font-size:0.82rem; color:#4a5878; margin-top:6px; }

/* ── Running status line ── */
.run-status { font-size:0.78rem; color:#344060; padding:4px 0; line-height:1.6; }
.run-status span.hi { color:#9d6fff; }
.run-status span.dim { color:#1e2840; }

/* ── Inline status line ── */
.inline-status {
    font-size:0.78rem; color:#2e3858; padding:8px 0;
    font-family:'JetBrains Mono',monospace; letter-spacing:0.02em;
}
.inline-status.done { color:#3a4a6a; }
.inline-status.done span { color:#4a7aff; font-weight:600; }

/* ── Run summary panel ── */
.summary-panel {
    background:#0b0e1c; border:1px solid #1a2040;
    border-radius:10px; padding:20px 24px;
}
.sp-label {
    font-size:0.6rem; font-weight:700; letter-spacing:0.18em;
    text-transform:uppercase; color:#2e3858; margin-bottom:16px;
    font-family:'JetBrains Mono',monospace;
}
.sp-grid {
    display:grid; grid-template-columns:repeat(4,1fr); gap:0;
}
.sp-item {
    padding:0 20px; border-right:1px solid #161c30;
}
.sp-item:first-child { padding-left:0; }
.sp-item:last-child  { padding-right:0; border-right:none; }
.sp-group-label {
    font-size:0.58rem; font-weight:700; letter-spacing:0.14em;
    text-transform:uppercase; color:#4a7aff; margin-bottom:10px;
    font-family:'JetBrains Mono',monospace;
}
.sp-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:5px 0; border-bottom:1px solid #0f1422;
}
.sp-row:last-child { border-bottom:none; }
.sp-k { font-size:0.73rem; color:#2e3858; }
.sp-v { font-size:0.73rem; color:#7a8ab0; font-family:'JetBrains Mono',monospace; font-weight:500; }
.sp-ok    { color:#3dba7a !important; }
.sp-err   { color:#c84060 !important; }
.sp-score { color:#4a7aff !important; font-weight:700 !important; font-size:0.82rem !important; }

/* ── Streamlit widget overrides ── */
.stTextInput>div>div>input {
    background:#0c0f1c !important; border:1px solid #161c30 !important;
    border-radius:8px !important; color:#e4ecff !important;
    font-size:0.88rem !important; padding:10px 14px !important;
}
.stTextInput>div>div>input:focus {
    border-color:#4a7aff !important; box-shadow:0 0 0 2px rgba(74,122,255,.14) !important;
}
.stButton>button {
    background:linear-gradient(120deg,#3a6aff 0%,#7a4dff 100%) !important;
    color:#fff !important; border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:0.86rem !important;
    padding:10px 22px !important; letter-spacing:0.02em !important;
}
.stButton>button:hover { opacity:.86 !important; }
.stDownloadButton>button {
    background:#0c0f1c !important; color:#4a7aff !important;
    border:1px solid #1a2848 !important; border-radius:8px !important;
    font-size:0.8rem !important; font-weight:500 !important;
}
.stProgress>div>div>div>div { background:linear-gradient(90deg,#4a7aff,#9d6fff) !important; }
[data-testid="stExpander"] {
    background:#090c18 !important; border:1px solid #131828 !important;
    border-radius:8px !important; margin-top:5px;
}
[data-testid="stExpander"] summary {
    font-size:0.77rem !important; color:#344060 !important; font-weight:500 !important; padding:9px 14px !important;
}
[data-testid="stExpander"] summary:hover { color:#bec8e0 !important; }
[data-testid="stAlert"] { border-radius:8px !important; font-size:0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def e(t: str) -> str:
    """HTML-escape so scraped content never breaks layout."""
    return html_lib.escape(str(t))

def plain(t: str, max_len: int = 220) -> str:
    """Escape + strip markdown symbols for safe plain-text display."""
    import re
    t = str(t)[:max_len]
    t = re.sub(r'#+\s*', '', t)          # headings
    t = re.sub(r'\*{1,2}|_{1,2}', '', t) # bold/italic
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)  # links
    return html_lib.escape(t)

def step_html(tag: str, name: str, status: str, status_cls: str, body_html: str) -> str:
    """Build a complete self-contained step card as an HTML string."""
    return f"""
<div class="step-card">
  <div class="step-hdr">
    <span class="step-tag">{tag}</span>
    <span class="step-name">{name}</span>
    <span class="step-status-{status_cls}">{status}</span>
  </div>
  <div class="step-body">{body_html}</div>
</div>"""

def metric_grid(items: list) -> str:
    boxes = "".join(
        f'<div class="mbox"><div class="mbox-val">{e(str(v))}</div>'
        f'<div class="mbox-lbl">{e(l)}</div></div>'
        for v, l in items
    )
    return f'<div class="mgrid">{boxes}</div>'

def scrape_table(rows: list[str]) -> str:
    return '<div class="stbl">' + "".join(rows) + "</div>"

def scrape_row(url: str, ok: bool, chars: int = 0) -> str:
    pill  = "<span class='pill-ok'>✓ ok</span>" if ok else "<span class='pill-err'>✗ skip</span>"
    ch    = f"<span class='srow-chars'>{chars:,} ch</span>" if ok else ""
    return (f'<div class="srow"><span class="srow-url">{e(url)}</span>'
            f'<span class="srow-right">{pill}{ch}</span></div>')

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:6px 0 18px">
        <p class="wm">Deep<span class="wm-accent">Research</span></p>
        <p class="wm-sub">Multi-Agent AI Pipeline</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.58rem;letter-spacing:0.18em;text-transform:uppercase;"
                "color:#1e2840;font-weight:700;margin-bottom:10px;"
                "font-family:JetBrains Mono,monospace'>Architecture</div>", unsafe_allow_html=True)

    for num, name, desc in [
        ("01", "Search",          "Tavily Advanced · top 20 → 5 unique"),
        ("02", "Scraper",         "Trafilatura · full-text extraction"),
        ("03", "Reader Agent",    "LLM per-source structured summary"),
        ("04", "Context Builder", "Merge Tavily + snippets + summaries"),
        ("05", "Writer Agent",    "LLM → professional research report"),
        ("06", "Critic Agent",    "LLM quality review & numeric score"),
    ]:
        st.markdown(f"""
        <div class="snode">
            <div class="snode-num">{num}</div>
            <div><div class="snode-name">{name}</div><div class="snode-desc">{desc}</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.58rem;letter-spacing:0.18em;text-transform:uppercase;"
                "color:#1e2840;font-weight:700;margin-bottom:8px;"
                "font-family:JetBrains Mono,monospace'>Tech Stack</div>", unsafe_allow_html=True)

    for k, v in [("LLM", "mistral-medium-latest"), ("Search", "Tavily Advanced"),
                 ("Scraper", "Trafilatura"), ("Framework", "LangChain"), ("UI", "Streamlit")]:
        st.markdown(f'<div class="stack-row"><span class="stack-k">{k}</span>'
                    f'<span class="stack-v">{v}</span></div>', unsafe_allow_html=True)

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.68rem;color:#1e2840;line-height:1.7">
        Searches → Scrapes → Summarises<br>→ Builds context → Writes → Critiques
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:6px 0 2px">
    <p class="wm" style="font-size:2.1rem">Deep<span class="wm-accent">Research</span></p>
    <p class="wm-sub" style="color:#1e2840">
        Autonomous · 6-stage · Search → Scrape → Read → Synthesise → Write → Critique
    </p>
</div>""", unsafe_allow_html=True)
st.markdown("<hr class='rule'>", unsafe_allow_html=True)

col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input("topic",
        placeholder="Enter a research topic — e.g. 'State of agentic AI frameworks in 2025'",
        label_visibility="collapsed")
with col_btn:
    run = st.button("Run Pipeline", use_container_width=True, type="primary")

st.markdown("<hr class='rule'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PIPELINE  —  each step owns one st.empty() slot that gets
#              replaced in-place (no duplication ever)
# ─────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.error("Please enter a research topic.")
        st.stop()

    progress = st.progress(0)
    state    = ResearchState()
    state.topic = topic

    # ══════════════════════════════════════════════════════
    # 01 · SEARCH
    # ══════════════════════════════════════════════════════
    slot1 = st.empty()
    slot1.markdown(step_html(
        "01 · SEARCH", "Web Search", "running…", "run",
        "<div class='run-status'>Querying Tavily Advanced…</div>"
    ), unsafe_allow_html=True)

    try:
        state = search_sources(state)
    except Exception as ex:
        slot1.error(f"Search failed: {ex}")
        st.stop()

    # Build result cards HTML (snippets escaped as plain text)
    result_cards = "".join(
        f'<div class="rcard">'
        f'<div class="rcard-title">{e(r["title"])}</div>'
        f'<span class="rcard-url">{e(r["url"])}</span>'
        f'<div class="rcard-snip">{plain(r["snippet"], 210)}</div>'
        f'</div>'
        for r in state.search_results
    )
    tav_html = ""
    if state.tavily_answer:
        tav_html = (f'<div class="tav-banner">'
                    f'<div class="tav-label">⬡ Tavily AI Answer</div>'
                    f'{plain(state.tavily_answer, 600)}</div>')

    # Results hidden behind a native expander — but we build the
    # static HTML for the step card itself then use an expander below
    slot1.markdown(step_html(
        "01 · SEARCH", "Web Search",
        f"✓ {len(state.search_results)} sources", "ok",
        tav_html   # body only shows the Tavily answer; results go in expander below
    ), unsafe_allow_html=True)

    with st.expander(f"View {len(state.search_results)} search results"):
        st.markdown(result_cards, unsafe_allow_html=True)

    progress.progress(17)

    # ══════════════════════════════════════════════════════
    # 02 · SCRAPER  (live row-by-row inside one slot)
    # ══════════════════════════════════════════════════════
    slot2 = st.empty()
    slot2.markdown(step_html(
        "02 · SCRAPE", "Source Scraper", "running…", "run",
        "<div class='run-status'>Starting scraper…</div>"
    ), unsafe_allow_html=True)

    from tools import scrape_url
    scraped_contents, rows_html = [], []
    attempted = accepted = skipped = 0

    for result in state.search_results:
        if accepted >= TARGET_SOURCES:
            break
        attempted += 1
        url = result["url"]

        try:
            content = scrape_url.invoke({"url": url})
        except Exception:
            content = ""
            skipped += 1

        reason = None
        if not content:                                          reason = "empty"
        elif content.startswith("Scraping failed"):             reason = "failed"
        elif len(content) < MIN_CONTENT_LENGTH:                 reason = "too short"
        elif any(k in content.lower() for k in BAD_KEYWORDS):  reason = "blocked"

        ok = reason is None
        if ok:
            scraped_contents.append({"title": result["title"], "url": url,
                                     "snippet": result["snippet"], "content": content})
            accepted += 1
        else:
            skipped += 1

        rows_html.append(scrape_row(url, ok, len(content) if ok else 0))

        # Replace slot2 with live progress
        slot2.markdown(step_html(
            "02 · SCRAPE", "Source Scraper", "running…", "run",
            scrape_table(rows_html)
        ), unsafe_allow_html=True)

    if not scraped_contents:
        slot2.error("No pages scraped. Check network access.")
        st.stop()

    state.scraped_contents = scraped_contents
    state.metrics.update({"attempted": attempted, "accepted": accepted,
                           "skipped": skipped, "target": TARGET_SOURCES})

    # Final replace — done state
    slot2.markdown(step_html(
        "02 · SCRAPE", "Source Scraper",
        f"✓ {accepted}/{attempted} scraped", "ok",
        scrape_table(rows_html)
    ), unsafe_allow_html=True)

    with st.expander(f"View {accepted} page previews"):
        for page in scraped_contents:
            st.markdown(f"**{e(page['title'])}**  \n`{e(page['url'])}`")
            st.code(page["content"][:500] + "…", language=None)

    progress.progress(33)

    # ══════════════════════════════════════════════════════
    # 03 · READER AGENT
    # ══════════════════════════════════════════════════════
    slot3 = st.empty()
    summaries = []

    for i, page in enumerate(scraped_contents):
        slot3.markdown(step_html(
            "03 · READER", "Reader Agent — Summarising Sources", "running…", "run",
            f"<div class='run-status'>Summarising "
            f"<span class='hi'>{e(page['title'][:55])}…</span> "
            f"<span class='dim'>({i+1}/{len(scraped_contents)})</span></div>"
        ), unsafe_allow_html=True)

        summary = reader_chain.invoke({
            "title": page["title"],
            "url": page["url"],
            "content": page["content"],
        })
        summaries.append({"title": page["title"], "url": page["url"], "summary": summary})

    state.summaries = summaries

    slot3.markdown(step_html(
        "03 · READER", "Reader Agent — Summarising Sources",
        f"✓ {len(summaries)} summaries", "ok", ""
    ), unsafe_allow_html=True)

    with st.expander(f"View {len(summaries)} AI source summaries"):
        cards = "".join(
            f'<div class="sumcard">'
            f'<div class="sumcard-lbl">⬡ Source {i} · Reader Summary</div>'
            f'<div class="sumcard-title">{e(s["title"])}</div>'
            f'<span class="sumcard-url">{e(s["url"])}</span>'
            f'<div class="sumcard-body">{e(s["summary"])}</div>'
            f'</div>'
            for i, s in enumerate(summaries, 1)
        )
        st.markdown(cards, unsafe_allow_html=True)

    progress.progress(50)

    # ══════════════════════════════════════════════════════
    # 04 · CONTEXT BUILDER
    # ══════════════════════════════════════════════════════
    slot4 = st.empty()
    slot4.markdown(
        "<div class='inline-status'>⬡ Building research context…</div>",
        unsafe_allow_html=True)

    state = build_research_context(state)
    m = state.metrics

    slot4.markdown(
        f"<div class='inline-status done'>"
        f"✓ Research context built — "
        f"<span>{m['context_chars']:,} chars</span> across "
        f"<span>{m['accepted']}</span> sources</div>",
        unsafe_allow_html=True)

    progress.progress(67)

    # ══════════════════════════════════════════════════════
    # 05 · WRITER AGENT
    # ══════════════════════════════════════════════════════
    slot5 = st.empty()
    slot5.markdown(step_html(
        "05 · WRITER", "Writer Agent — Drafting Report", "running…", "run",
        "<div class='run-status'>Generating report…</div>"
    ), unsafe_allow_html=True)

    try:
        state = generate_report(state)
    except Exception as ex:
        slot5.error(f"Writer failed: {ex}")
        st.stop()

    slot5.markdown(step_html(
        "05 · WRITER", "Writer Agent — Drafting Report",
        f"✓ {state.metrics['report_words']:,} words", "ok", ""
    ), unsafe_allow_html=True)

    with st.expander("📄 View Full Report", expanded=True):
        st.markdown(state.report)

    st.download_button(
        label="⬇  Download Report (.md)",
        data=state.report,
        file_name=f"deepresearch_{topic[:45].strip().replace(' ', '_')}.md",
        mime="text/markdown",
    )

    progress.progress(84)

    # ══════════════════════════════════════════════════════
    # 06 · CRITIC AGENT
    # ══════════════════════════════════════════════════════
    slot6 = st.empty()
    slot6.markdown(step_html(
        "06 · CRITIC", "Critic Agent — Quality Review", "running…", "run",
        "<div class='run-status'>Evaluating report…</div>"
    ), unsafe_allow_html=True)

    try:
        state = review_report(state)
    except Exception as ex:
        slot6.error(f"Critic failed: {ex}")
        st.stop()

    score_line, feedback_lines = "", []
    for line in state.feedback.strip().splitlines():
        if line.lower().startswith("score:"):
            score_line = (line.split(":", 1)[-1].replace("**", "").replace("*", "").strip())
        else:
            feedback_lines.append(line)

    score_html = ""
    if score_line:
        score_html = (f'<div class="score-wrap">'
                      f'<div class="score-num">{e(score_line)}</div>'
                      f'<div class="score-lbl">Quality<br>Score</div></div>')

    slot6.markdown(step_html(
        "06 · CRITIC", "Critic Agent — Quality Review",
        f"✓ score: {score_line}" if score_line else "✓ complete", "ok",
        score_html
    ), unsafe_allow_html=True)

    with st.expander("📋 View Critic Feedback", expanded=True):
        st.markdown("\n".join(feedback_lines))

    progress.progress(100)

    # ══════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ══════════════════════════════════════════════════════
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    score_display = score_line if score_line else "—"
    st.markdown(f"""
    <div class="summary-panel">
        <div class="sp-label">⬡ Run Summary</div>
        <div class="sp-grid">
            <div class="sp-item">
                <div class="sp-group-label">SEARCH</div>
                <div class="sp-row">
                    <span class="sp-k">Results returned</span>
                    <span class="sp-v">{m.get("returned", 0)}</span>
                </div>
                <div class="sp-row">
                    <span class="sp-k">Attempted to scrape</span>
                    <span class="sp-v">{m.get("attempted", 0)}</span>
                </div>
            </div>
            <div class="sp-item">
                <div class="sp-group-label">SCRAPING</div>
                <div class="sp-row">
                    <span class="sp-k">Sources accepted</span>
                    <span class="sp-v sp-ok">{m.get("accepted", 0)}</span>
                </div>
                <div class="sp-row">
                    <span class="sp-k">Sources skipped</span>
                    <span class="sp-v sp-err">{m.get("skipped", 0)}</span>
                </div>
            </div>
            <div class="sp-item">
                <div class="sp-group-label">CONTEXT</div>
                <div class="sp-row">
                    <span class="sp-k">Context size</span>
                    <span class="sp-v">{m.get("context_chars", 0):,} ch</span>
                </div>
                <div class="sp-row">
                    <span class="sp-k">Summaries generated</span>
                    <span class="sp-v">{len(summaries)}</span>
                </div>
            </div>
            <div class="sp-item">
                <div class="sp-group-label">OUTPUT</div>
                <div class="sp-row">
                    <span class="sp-k">Report words</span>
                    <span class="sp-v">{m.get("report_words", 0):,}</span>
                </div>
                <div class="sp-row">
                    <span class="sp-k">Quality score</span>
                    <span class="sp-v sp-score">{score_display}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🗒 View full pipeline logs"):
        st.markdown(f'<div class="logbox">{e(chr(10).join(state.logs))}</div>',
                    unsafe_allow_html=True)