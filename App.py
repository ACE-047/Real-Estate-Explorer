"""
app_merged.py — Nawy Real Estate Explorer
Dark Black & Gold luxury aesthetic (from app.py)  +
Full feature set: manual location entry, interactive image gallery,
multi-location scraping (from apps.py)

Run with: streamlit run app_merged.py
"""

import streamlit as st
import time
import numpy as np
import pandas as pd
import base64

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Real Estate Explorer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS: dark gold & black theme + Cinzel / Cormorant Garamond ────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Cinzel:wght@400;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --bg:           #0A0A0A;
    --bg-card:      #111111;
    --bg-sidebar:   #0D0D0D;
    --gold:         #C9A84C;
    --gold-light:   #E8CC7A;
    --gold-dark:    #A0762A;
    --gold-dim:     #6B4F1A;
    --text-bright:  #F5EDD6;
    --text-mid:     #C8B89A;
    --text-muted:   #7A6A50;
    --border:       #C9A84C44;
    --border-solid: #C9A84C;
    --danger:       #8B2020;
}

/* ── Base reset ── */
html, body, [class*="css"] {
    font-family: 'Cormorant Garamond', 'Georgia', serif !important;
    background-color: var(--bg) !important;
    color: var(--text-bright) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
/* Keep the sidebar collapse/expand button always visible */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── App header banner ── */
.nawy-header {
    background: linear-gradient(135deg, #0A0A0A 0%, #1A1200 50%, #0A0A0A 100%);
    border-bottom: 1px solid var(--border-solid);
    padding: 22px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.nawy-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 40px,
        rgba(201,168,76,0.03) 40px,
        rgba(201,168,76,0.03) 41px
    );
}
.nawy-header h1 {
    font-family: 'Cinzel', serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--gold) !important;
    letter-spacing: 0.35em !important;
    margin: 0 !important;
    text-shadow: 0 0 40px rgba(201,168,76,0.3);
}
.nawy-header .subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.85rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    margin-top: 4px;
    text-transform: uppercase;
}
.nawy-header .ornament {
    color: var(--gold-dim);
    font-size: 0.9rem;
    letter-spacing: 0.5em;
    margin-bottom: 8px;
}

/* ── Sidebar — fully static, never collapsible ── */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"]        { display: none !important; }
section[data-testid="stSidebar"] {
    transform: none !important;
    min-width: 21rem !important;
    max-width: 21rem !important;
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    pointer-events: auto !important;
    visibility: visible !important;
    display: flex !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    margin-left: 0 !important;
    display: flex !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* ── Sidebar section labels ── */
.sidebar-section {
    font-family: 'Cinzel', serif;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: var(--text-muted);
    text-transform: uppercase;
    padding: 12px 0 4px 0;
    border-top: 1px solid var(--border);
    margin-top: 8px;
}
.sidebar-logo {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    color: var(--gold);
    letter-spacing: 0.2em;
    text-align: center;
    padding: 0 0 16px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}

/* ── Streamlit buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 100%) !important;
    color: #0A0A0A !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    padding: 0.55rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 12px rgba(201,168,76,0.2) !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    background: #1A1A1A !important;
    color: var(--text-muted) !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextInput > label {
    background-color: #141414 !important;
    color: var(--text-bright) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
}
.stTextInput > label {
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
}

/* ── Multiselect ── */
.stMultiSelect > label {
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: var(--text-muted) !important;
}
[data-baseweb="select"] {
    background-color: #141414 !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}
[data-baseweb="tag"] {
    background-color: var(--gold-dim) !important;
    color: var(--gold-light) !important;
}

/* ── Status / info boxes ── */
.status-bar {
    background: #111111;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 10px 16px;
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.95rem;
    color: var(--text-mid);
    display: flex;
    align-items: center;
    gap: 10px;
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--gold);
    animation: pulse 2s infinite;
    flex-shrink: 0;
}
.status-dot.idle { background: var(--text-muted); animation: none; }
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.3; }
}

/* ── Property card ── */
.prop-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0;
    overflow: hidden;
    transition: border-color 0.25s, box-shadow 0.25s;
    height: 100%;
}
.prop-card:hover {
    border-color: var(--gold);
    box-shadow: 0 6px 32px rgba(201,168,76,0.12);
}
.prop-card-header {
    background: linear-gradient(135deg, #1A1200 0%, #0D0D0D 100%);
    border-bottom: 1px solid var(--border);
    padding: 14px 16px 10px;
}
.prop-card-name {
    font-family: 'Cinzel', serif;
    font-size: 0.95rem;
    color: var(--gold);
    letter-spacing: 0.06em;
    margin: 0 0 2px 0;
    line-height: 1.3;
}
.prop-card-ref {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
}
.prop-card-body {
    padding: 12px 16px;
}
.prop-field {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 5px 0;
    border-bottom: 1px solid rgba(201,168,76,0.06);
}
.prop-field:last-child { border-bottom: none; }
.prop-label {
    font-family: 'Cinzel', serif;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    color: var(--text-muted);
    text-transform: uppercase;
    flex-shrink: 0;
}
.prop-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: var(--text-bright);
    text-align: right;
    font-weight: 500;
}
.prop-value.price {
    color: var(--gold);
    font-weight: 600;
    font-size: 1.05rem;
}
.prop-card-footer {
    padding: 10px 16px 14px;
}
.prop-link {
    display: block;
    text-align: center;
    padding: 7px;
    background: linear-gradient(135deg, var(--gold-dark), var(--gold));
    color: #0A0A0A !important;
    font-family: 'Cinzel', serif;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    text-decoration: none !important;
    border-radius: 3px;
    font-weight: 600;
    transition: all 0.2s;
}
.prop-link:hover {
    background: linear-gradient(135deg, var(--gold), var(--gold-light));
    box-shadow: 0 3px 14px rgba(201,168,76,0.35);
}

/* ── Stats bar ── */
.stats-strip {
    background: #111111;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px 20px;
    display: flex;
    gap: 40px;
    align-items: center;
    margin-bottom: 16px;
}
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Cinzel', serif;
    font-size: 1.5rem;
    color: var(--gold);
    display: block;
}
.stat-lbl {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.stat-divider {
    width: 1px;
    height: 36px;
    background: var(--border);
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 0.3em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin: 20px 0 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
    text-transform: uppercase !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}
[data-testid="stDataFrameResizable"] th {
    background: #141414 !important;
    color: var(--gold) !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
}
[data-testid="stDataFrameResizable"] td {
    background: var(--bg-card) !important;
    color: var(--text-bright) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 0.95rem !important;
    border-color: var(--border) !important;
}

/* ── Plot containers ── */
.stPlotlyChart, .stImage {
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Alerts / warnings ── */
.stAlert {
    background: #1A1000 !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 4px !important;
    color: var(--text-mid) !important;
}

/* ── No-data placeholder ── */
.empty-state {
    text-align: center;
    padding: 80px 20px;
    color: var(--text-muted);
}
.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.4;
}
.empty-state h3 {
    font-family: 'Cinzel', serif;
    font-size: 1rem;
    letter-spacing: 0.2em;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.empty-state p {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: var(--text-muted);
    opacity: 0.6;
}

/* ── Checkbox ── */
.stCheckbox > label {
    color: var(--text-mid) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--gold) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold) !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: rgba(201,168,76,0.1) !important;
}

/* ── Selectbox ── */
.stSelectbox label {
    font-family: 'Cinzel', serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: var(--text-muted) !important;
}
[data-baseweb="select"] > div {
    background: #141414 !important;
    border-color: var(--border) !important;
    color: var(--text-bright) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "locations":     [],
    "selected":      [],
    "pending_locs":  [],    # manual entry before site locations are fetched
    "df":            None,
    "img_dict":      {},
    "scraped":       {},
    "status":        "Ready.",
    "busy":          False,
    "kde_png":       None,
    "net_png":       None,
    "cloud_png":     None,
    "gallery_state": {},    # {ref_no: current_index}
    "show_gallery":  {},    # {ref_no: bool}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper ───────────────────────────────────────────────────────────────────
def png_to_b64(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode()




# ── Header banner ────────────────────────────────────────────────────────────
st.markdown("""
<div class="nawy-header">
    <div class="ornament">✦ ── ✦ ── ✦</div>
    <h1>REAL  ESTATE  EXPLORER</h1>
    <div class="subtitle">Luxury Property Intelligence · nawy.com</div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">✦ NAWY ✦</div>', unsafe_allow_html=True)

    # ── Status indicator ─────────────────────────────────────────────────
    dot_class = "status-dot" if st.session_state.busy else "status-dot idle"
    st.markdown(f"""
    <div class="status-bar">
        <div class="{dot_class}"></div>
        <span>{st.session_state.status}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── Step 1: Fetch Locations ──────────────────────────────────────────
    st.markdown('<div class="sidebar-section">① Fetch Locations</div>', unsafe_allow_html=True)

    if st.button("⬇  Fetch Locations from Site", disabled=st.session_state.busy):
        st.session_state.busy   = True
        st.session_state.status = "Launching browser to fetch locations…"
        st.rerun()

    if st.session_state.busy and st.session_state.status.startswith("Launching browser"):
        with st.spinner("Connecting to nawy.com…"):
            try:
                from Scraping import initialize_driver, fetch_locations
                _driver = initialize_driver()
                _locs   = fetch_locations(_driver)
                _driver.quit()
                _seen, _deduped = set(), []
                for l in _locs:
                    k = l.strip().lower()
                    if k and k not in _seen:
                        _seen.add(k)
                        _deduped.append(l.strip())
                st.session_state.locations = _deduped
                st.session_state.status    = f"Found {len(_deduped)} locations."
            except Exception as e:
                st.session_state.status = f"Error: {e}"
            finally:
                st.session_state.busy = False
        st.rerun()

    # ── Step 2: Select Locations ─────────────────────────────────────────
    st.markdown('<div class="sidebar-section">② Select Locations</div>', unsafe_allow_html=True)

    # Sub-mode A: site locations loaded → checkboxes
    if st.session_state.locations:
        search_q = st.text_input("", placeholder="🔍  Search location…", label_visibility="collapsed")
        filtered_locs = (
            [l for l in st.session_state.locations if search_q.lower() in l.lower()]
            if search_q else st.session_state.locations
        )
        selected_locs = []
        for loc in filtered_locs:
            if st.checkbox(loc, key=f"loc_{loc}"):
                selected_locs.append(loc)
        if len(selected_locs) > 1:
            st.markdown(
                f'<p style="font-family:\'Cormorant Garamond\',serif;font-size:0.9rem;'
                f'color:#C8B89A;padding:4px 0;">ℹ {len(selected_locs)} locations selected</p>',
                unsafe_allow_html=True,
            )
        st.session_state.selected = selected_locs

    # Sub-mode B: no site locations yet → manual entry
    else:
        st.markdown(
            '<p style="font-family:\'Cormorant Garamond\',serif;font-size:0.9rem;'
            'color:#7A6A50;padding:4px 0;">Fetch locations or add manually below.</p>',
            unsafe_allow_html=True,
        )

        if st.session_state.pending_locs:
            for i, loc in enumerate(st.session_state.pending_locs):
                col_loc, col_del = st.columns([4, 1])
                col_loc.markdown(
                    f'<span style="font-family:\'Cormorant Garamond\',serif;'
                    f'color:#C8B89A;font-size:0.95rem;">· {loc}</span>',
                    unsafe_allow_html=True,
                )
                if col_del.button("✕", key=f"del_loc_{i}"):
                    st.session_state.pending_locs.pop(i)
                    st.rerun()

        new_loc = st.text_input("Location name", placeholder="e.g. New Cairo", key="manual_loc_input")
        col_add, col_clear = st.columns(2)
        

        st.session_state.selected = list(st.session_state.pending_locs)

    # ── Step 3: Parse ────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">③ Parse Properties</div>', unsafe_allow_html=True)

    n_sel = len(st.session_state.selected)
    parse_disabled = st.session_state.busy or not st.session_state.selected

    if n_sel > 0:
        st.markdown(
            f'<p style="font-family:\'Cormorant Garamond\',serif;font-size:0.85rem;'
            f'color:#C8B89A;padding:2px 0 6px;">Ready: {", ".join(st.session_state.selected)}</p>',
            unsafe_allow_html=True,
        )

    btn_label = f"▶  Parse {n_sel} Location(s)" if n_sel > 0 else "▶  Parse Properties"
    if st.button(btn_label, disabled=parse_disabled):
        st.session_state.busy   = True
        st.session_state.status = f"Parsing {n_sel} location(s)…"
        st.session_state.df     = None
        st.rerun()

    if st.session_state.busy and "Parsing" in st.session_state.status:
        with st.spinner(f"Scraping {n_sel} location(s)…"):
            try:
                from Scraping import (
                    initialize_driver, select_locations,
                    get_compound_links, scrape_property_details,
                )
                from UTILITY import clean_area_list, clean_currency_list

                _all = {
                    "compounds": [], "ref_no": [], "prices": [],
                    "areas": [], "links": [], "beds": [], "baths": [], "delivery": [],
                }
                _all_img = {}

                _driver = initialize_driver()

                # Tick all selected locations in one filter session, then Apply once
                st.session_state.status = f"Selecting {len(st.session_state.selected)} location(s)…"
                select_locations(_driver, st.session_state.selected)

                # Scrape the combined results page
                st.session_state.status = "Scraping combined results…"
                _clinks = get_compound_links(_driver)
                if _clinks:
                    _data = scrape_property_details(_driver, _clinks)
                    for k in _all:
                        _all[k].extend(_data.get(k, []))
                    _all_img.update(_data.get("img", {}))

                _driver.quit()

                if _all["links"]:
                    _df = pd.DataFrame({
                        "compound": _all["compounds"],
                        "ref no.":  _all["ref_no"],
                        "area":     _all["areas"],
                        "bed":      _all["beds"],
                        "bath":     _all["baths"],
                        "price":    _all["prices"],
                        "delivery": _all["delivery"],
                        "link":     _all["links"],
                    }).drop_duplicates(subset=["ref no."], keep="first")
                    _df.index = range(1, len(_df) + 1)
                    _df["area_clean"]  = clean_area_list(_df["area"].tolist())
                    _df["price_clean"] = clean_currency_list(_df["price"].tolist())
                    _df["bed_clean"]   = pd.to_numeric(_df["bed"], errors="coerce").fillna(0)
                    st.session_state.df       = _df
                    st.session_state.img_dict = _all_img
                    st.session_state.scraped  = _all
                    st.session_state.status   = f"Done — {len(_df)} properties loaded."
                else:
                    st.session_state.status = "No properties found."
            except Exception as e:
                st.session_state.status = f"Error: {e}"
            finally:
                st.session_state.busy = False
        st.rerun()

    # ── Analysis ─────────────────────────────────────────────────────────
    has_data = st.session_state.df is not None and not st.session_state.df.empty

    st.markdown('<div class="sidebar-section">④ Analysis</div>', unsafe_allow_html=True)

    if st.button("🔥  KDE Heatmap", disabled=not has_data or st.session_state.busy):
        with st.spinner("Generating KDE…"):
            try:
                from Analysis import run_kde_analysis
                _areas  = np.array(st.session_state.df["area_clean"].tolist(), dtype=float)
                _prices = np.array(st.session_state.df["price_clean"].tolist(), dtype=float)
                st.session_state.kde_png = run_kde_analysis(_areas, _prices)
            except Exception as e:
                st.session_state.status = f"KDE error: {e}"
        st.rerun()

    if st.button("🕸  Network Graph", disabled=not has_data or st.session_state.busy):
        with st.spinner("Building network…"):
            try:
                from Analysis import run_network_analysis
                st.session_state.net_png = run_network_analysis(
                    st.session_state.df["compound"].tolist(),
                    np.array(st.session_state.df["price_clean"].tolist(), dtype=float),
                    np.array(st.session_state.df["area_clean"].tolist(), dtype=float),
                )
            except Exception as e:
                st.session_state.status = f"Network error: {e}"
        st.rerun()

    if st.button("🧊  3D Point Cloud", disabled=not has_data or st.session_state.busy):
        with st.spinner("Rendering 3D…"):
            try:
                from Analysis import run_3d_cloud_analysis
                st.session_state.cloud_png = run_3d_cloud_analysis(st.session_state.df)
            except Exception as e:
                st.session_state.status = f"3D error: {e}"
        st.rerun()

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">⑤ Export</div>', unsafe_allow_html=True)

    if has_data:
        _csv = st.session_state.df.to_csv(index=True, encoding="utf-8")
        _ts  = time.strftime("%Y-%m-%d_%H-%M-%S")
        st.download_button(
            label="💾  Download CSV",
            data=_csv,
            file_name=f"nawy_export_{_ts}.csv",
            mime="text/csv",
            disabled=not has_data,
        )
    else:
        st.button("💾  Download CSV", disabled=True)


# ════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
tab_cards, tab_table, tab_analysis = st.tabs([
    "✦  PROPERTIES",
    "⊞  DATA TABLE",
    "◈  ANALYSIS",
])


# ── Tab 1: Property Cards ────────────────────────────────────────────────────
with tab_cards:
    df = st.session_state.df

    if df is None or df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">✦</div>
            <h3>No Properties Loaded</h3>
            <p>Fetch locations, select an area, and parse properties to begin.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        img_dict = st.session_state.img_dict

        # Stats strip
        _total     = len(df)
        _avg_p     = df["price_clean"].mean()
        _avg_a     = df["area_clean"].mean()
        _compounds = df["compound"].nunique()

        def _fmt_price(v):
            if v >= 1_000_000:
                return f"{v/1_000_000:.1f}M EGP"
            if v >= 1_000:
                return f"{v/1_000:.0f}K EGP"
            return f"{v:.0f} EGP"

        st.markdown(f"""
        <div class="stats-strip">
            <div class="stat-item">
                <span class="stat-num">{_total}</span>
                <span class="stat-lbl">Properties</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-num">{_compounds}</span>
                <span class="stat-lbl">Compounds</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-num">{_fmt_price(_avg_p)}</span>
                <span class="stat-lbl">Avg Price</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-num">{_avg_a:.0f} m²</span>
                <span class="stat-lbl">Avg Area</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Filter bar
        with st.expander("🔎  Filter Properties", expanded=False):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                price_filter = st.selectbox(
                    "Price Bracket",
                    ["All", "Budget (<3M)", "Mid-Range (3–8M)", "Luxury (>8M)"],
                )
            with fc2:
                area_filter = st.selectbox(
                    "Area Bracket",
                    ["All", "Small (<100m²)", "Medium (100–200m²)", "Large (>200m²)"],
                )
            with fc3:
                bed_options = sorted(df["bed_clean"].dropna().unique().astype(int).tolist())
                bed_filter  = st.selectbox("Bedrooms", ["All"] + bed_options)

        _fdf = df.copy()
        if price_filter == "Budget (<3M)":
            _fdf = _fdf[_fdf["price_clean"] < 3_000_000]
        elif price_filter == "Mid-Range (3–8M)":
            _fdf = _fdf[(_fdf["price_clean"] >= 3_000_000) & (_fdf["price_clean"] < 8_000_000)]
        elif price_filter == "Luxury (>8M)":
            _fdf = _fdf[_fdf["price_clean"] >= 8_000_000]

        if area_filter == "Small (<100m²)":
            _fdf = _fdf[_fdf["area_clean"] < 100]
        elif area_filter == "Medium (100–200m²)":
            _fdf = _fdf[(_fdf["area_clean"] >= 100) & (_fdf["area_clean"] < 200)]
        elif area_filter == "Large (>200m²)":
            _fdf = _fdf[_fdf["area_clean"] >= 200]

        if bed_filter != "All":
            _fdf = _fdf[_fdf["bed_clean"] == int(bed_filter)]

        st.markdown(f'<div class="section-heading">Showing {len(_fdf)} Properties</div>', unsafe_allow_html=True)

        # Render cards — 3 columns
        COLS      = 3
        rows_list = _fdf.to_dict("records")

        for i in range(0, len(rows_list), COLS):
            chunk = rows_list[i : i + COLS]
            cols  = st.columns(COLS)

            for col, row in zip(cols, chunk):
                compound = str(row.get("compound", "N/A"))
                ref_no   = str(row.get("ref no.", "N/A"))
                area     = str(row.get("area", "N/A"))
                bed      = str(row.get("bed", "N/A"))
                bath     = str(row.get("bath", "N/A"))
                price    = str(row.get("price", "N/A"))
                delivery = str(row.get("delivery", "N/A"))
                link     = str(row.get("link", ""))
                img_urls = img_dict.get(compound, [])
                gkey     = f"gallery_{ref_no}"

                link_html = (
                    f'<a href="{link}" target="_blank" class="prop-link">View Listing →</a>'
                    if link and link != "N/A" else
                    '<span class="prop-link" style="opacity:0.35;cursor:default;">No Link</span>'
                )

                with col:
                    # Styled card header + body via HTML
                    st.markdown(f"""
                    <div class="prop-card">
                        <div class="prop-card-header">
                            <div class="prop-card-name">{compound}</div>
                            <div class="prop-card-ref">Ref · {ref_no}</div>
                        </div>
                        <div class="prop-card-body">
                            <div class="prop-field">
                                <span class="prop-label">Area</span>
                                <span class="prop-value">{area}</span>
                            </div>
                            <div class="prop-field">
                                <span class="prop-label">Beds</span>
                                <span class="prop-value">{bed}</span>
                            </div>
                            <div class="prop-field">
                                <span class="prop-label">Baths</span>
                                <span class="prop-value">{bath}</span>
                            </div>
                            <div class="prop-field">
                                <span class="prop-label">Delivery</span>
                                <span class="prop-value">{delivery}</span>
                            </div>
                            <div class="prop-field">
                                <span class="prop-label">Price</span>
                                <span class="prop-value price">{price}</span>
                            </div>
                        </div>
                        <div class="prop-card-footer">
                            {link_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Interactive image gallery (from apps.py) ──────────
                    if img_urls:
                        n_imgs    = len(img_urls)
                        tog_label = (
                            f"🖼  Hide Photos ({n_imgs})"
                            if st.session_state.show_gallery.get(gkey, False)
                            else f"🖼  Show Photos ({n_imgs})"
                        )
                        if st.button(tog_label, key=f"tog_{gkey}"):
                            current = st.session_state.show_gallery.get(gkey, False)
                            st.session_state.show_gallery[gkey] = not current
                            if gkey not in st.session_state.gallery_state:
                                st.session_state.gallery_state[gkey] = 0
                            st.rerun()

                        if st.session_state.show_gallery.get(gkey, False):
                            idx = st.session_state.gallery_state.get(gkey, 0)
                            idx = max(0, min(idx, n_imgs - 1))

                            st.image(
                                img_urls[idx],
                                caption=f"Photo {idx + 1} of {n_imgs}",
                                use_container_width=True,
                            )

                            nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
                            with nav_l:
                                if st.button("◀ Prev", key=f"prev_{gkey}", disabled=(idx == 0)):
                                    st.session_state.gallery_state[gkey] = idx - 1
                                    st.rerun()
                            with nav_mid:
                                st.markdown(
                                    f'<p style="font-family:\'Cinzel\',serif;font-size:0.65rem;'
                                    f'color:#7A6A50;text-align:center;letter-spacing:0.15em;">'
                                    f'{idx + 1} / {n_imgs}</p>',
                                    unsafe_allow_html=True,
                                )
                            with nav_r:
                                if st.button("Next ▶", key=f"next_{gkey}", disabled=(idx >= n_imgs - 1)):
                                    st.session_state.gallery_state[gkey] = idx + 1
                                    st.rerun()

                            # All photos in 2-column mini grid
                            st.markdown(
                                '<div class="section-heading">All Photos</div>',
                                unsafe_allow_html=True,
                            )
                            for img_i in range(0, n_imgs, 2):
                                img_pair = img_urls[img_i : img_i + 2]
                                img_cols = st.columns(len(img_pair))
                                for ic, iurl in zip(img_cols, img_pair):
                                    ic.image(iurl, use_container_width=True)
                    else:
                        st.markdown(
                            '<p style="font-family:\'Cormorant Garamond\',serif;'
                            'font-size:0.85rem;color:#7A6A50;padding:4px 16px;">No photos available.</p>',
                            unsafe_allow_html=True,
                        )


# ── Tab 2: Data Table ────────────────────────────────────────────────────────
with tab_table:
    if st.session_state.df is None or st.session_state.df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⊞</div>
            <h3>No Data Yet</h3>
            <p>Parse some properties to populate the table.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        _show_cols = ["compound", "ref no.", "area", "bed", "bath", "price", "delivery", "link"]
        _display   = st.session_state.df[[c for c in _show_cols if c in st.session_state.df.columns]]
        st.dataframe(_display, use_container_width=True, height=520)


# ── Tab 3: Analysis ──────────────────────────────────────────────────────────
with tab_analysis:
    if st.session_state.df is None or st.session_state.df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">◈</div>
            <h3>No Data to Analyse</h3>
            <p>Parse properties first, then run analysis from the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        a1, a2 = st.columns(2)

        with a1:
            st.markdown('<div class="section-heading">KDE Heatmap</div>', unsafe_allow_html=True)
            if st.session_state.kde_png:
                st.image(st.session_state.kde_png, use_container_width=True)
            else:
                st.markdown(
                    '<p style="color:#7A6A50;font-family:\'Cormorant Garamond\',serif;'
                    'font-size:0.95rem;padding:24px;text-align:center;">'
                    'Click · KDE Heatmap · in the sidebar to generate.</p>',
                    unsafe_allow_html=True,
                )

        with a2:
            st.markdown('<div class="section-heading">Network Graph</div>', unsafe_allow_html=True)
            if st.session_state.net_png:
                st.image(st.session_state.net_png, use_container_width=True)
            else:
                st.markdown(
                    '<p style="color:#7A6A50;font-family:\'Cormorant Garamond\',serif;'
                    'font-size:0.95rem;padding:24px;text-align:center;">'
                    'Click · Network Graph · in the sidebar to generate.</p>',
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-heading">3D Point Cloud</div>', unsafe_allow_html=True)
        if st.session_state.cloud_png:
            st.image(st.session_state.cloud_png, use_container_width=True)
        else:
            st.markdown(
                '<p style="color:#7A6A50;font-family:\'Cormorant Garamond\',serif;'
                'font-size:0.95rem;padding:24px;text-align:center;">'
                'Click · 3D Point Cloud · in the sidebar to generate.</p>',
                unsafe_allow_html=True,
            )
