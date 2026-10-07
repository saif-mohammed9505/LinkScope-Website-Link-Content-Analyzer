"""
LinkScope
A Streamlit UI around scraper.py (fetch_website_data and friends).

Run with:
    streamlit run app.py
"""

import base64
import io
import math
import os
from collections import Counter
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from scraper import FetchError, fetch_website_data

# --------------------------------------------------------------------------
# Page config & theme
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="LinkScope",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

INK = "#15181D"
PANEL = "#20252C"
MINT = "#2BD9A7"
CORAL = "#FF6B5D"
AMBER = "#F5A623"
PAPER = "#FDF6F6"
SLATE = "#6B7280"
BORDER = "#E8E6E0"


def load_svg(name: str) -> str:
    with open(os.path.join(ASSETS_DIR, name), "r") as f:
        return f.read()


def svg_data_uri(svg_text: str) -> str:
    b64 = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return raw
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


@st.cache_data(show_spinner=False, ttl=600)
def cached_fetch(url: str, max_chars: int):
    return fetch_website_data(url, max_chars=max_chars)


def classify(links, base_netloc):
    rows = []
    for link in links:
        netloc = urlparse(link).netloc
        kind = "internal" if netloc == base_netloc else "external"
        rows.append({"link": link, "domain": netloc, "type": kind})
    return pd.DataFrame(rows)


def donut_svg(internal: int, external: int) -> str:
    total = max(internal + external, 1)
    r, cx, cy, sw = 58, 70, 70, 20
    circumference = 2 * math.pi * r
    internal_len = circumference * (internal / total)
    external_len = circumference * (external / total)
    return f"""
    <svg viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#E8E6E0" stroke-width="{sw}"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MINT}" stroke-width="{sw}"
              stroke-dasharray="{internal_len:.1f} {circumference:.1f}"
              stroke-dashoffset="0" transform="rotate(-90 {cx} {cy})" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CORAL}" stroke-width="{sw}"
              stroke-dasharray="{external_len:.1f} {circumference:.1f}"
              stroke-dashoffset="-{internal_len:.1f}" transform="rotate(-90 {cx} {cy})" stroke-linecap="round"/>
      <text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="Georgia, serif" font-size="26" fill="{INK}" font-weight="bold">{total}</text>
    </svg>
    """


# --------------------------------------------------------------------------
# Global CSS
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PAPER}; }}
    section[data-testid="stSidebar"] {{ background-color: {INK}; }}
    section[data-testid="stSidebar"] * {{ color: {PAPER} !important; }}
    h1, h2, h3 {{ font-family: Georgia, 'Times New Roman', serif; color: {INK}; }}
    .ls-hero {{ border-radius: 14px; overflow: hidden; margin-bottom: 1.6rem;
                box-shadow: 0 8px 24px rgba(21,24,29,0.25); }}
    .ls-card {{ background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
                border: 1px solid {BORDER}; box-shadow: 0 2px 10px rgba(21,24,29,0.05);
                margin-bottom: 1rem; height: 100%; }}
    .ls-label {{ text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.72rem;
                 color: {SLATE}; font-weight: 700; }}
    .ls-value {{ font-weight: 700; color: {INK}; font-size: 1.3rem; margin-top: 0.1rem; }}
    .ls-chip {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px;
                font-weight: 700; font-size: 0.68rem; letter-spacing: 0.03em; }}
    .ls-row {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.35rem 0;
               border-bottom: 1px solid #F0EEE8; }}
    .ls-row a {{ color: {INK}; text-decoration: none; font-size: 0.88rem; word-break: break-all; }}
    .ls-row a:hover {{ color: {CORAL}; text-decoration: underline; }}
    .ls-domain {{ color: {SLATE}; font-size: 0.78rem; min-width: 70px; }}
    div.stButton > button {{ background-color: {INK}; color: {PAPER}; border-radius: 8px;
                             border: none; padding: 0.55rem 1.4rem; font-weight: 600; width: 100%; }}
    div.stButton > button:hover {{ background-color: {PANEL}; color: white; }}
    pre, code {{ white-space: pre-wrap !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔎 LinkScope")
    st.caption("Inspect any page's title, text, and links — in a single fetch.")
    st.markdown("---")
    url_input = st.text_input("Page URL", placeholder="example.com/some-page")
    with st.expander("Options"):
        max_chars = st.slider("Preview length (characters)", 500, 8000, 2000, 500)
        force_refresh = st.checkbox("Force refresh (skip cache)")
    fetch_clicked = st.button("Inspect page", use_container_width=True)
    st.markdown("---")
    st.caption("Results are cached for 10 minutes per URL + preview length.")

st.markdown(f'<div class="ls-hero">{load_svg("hero.svg")}</div>', unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.error = None

if fetch_clicked:
    target = normalize_url(url_input)
    if not target or urlparse(target).netloc == "":
        st.session_state.error = "Enter a valid URL first."
        st.session_state.result = None
    else:
        if force_refresh:
            cached_fetch.clear()
        with st.spinner(f"Fetching {target} ..."):
            try:
                st.session_state.result = cached_fetch(target, max_chars)
                st.session_state.error = None
            except FetchError as exc:
                st.session_state.error = str(exc)
                st.session_state.result = None
            except Exception as exc:  # pragma: no cover - safety net
                st.session_state.error = f"Unexpected error: {exc}"
                st.session_state.result = None

if st.session_state.error:
    st.error(st.session_state.error, icon="⚠️")

if st.session_state.result is None and not st.session_state.error:
    st.info("Enter a URL in the sidebar and click **Inspect page** to get started.")

if st.session_state.result is not None:
    data = st.session_state.result
    title = data["title"]
    full_text = data["full_text"]
    preview_text = data["preview_text"]
    links = data["links"]
    final_url = data["url"]
    base_netloc = urlparse(final_url).netloc

    links_df = classify(links, base_netloc)
    n_internal = int((links_df["type"] == "internal").sum()) if not links_df.empty else 0
    n_external = int((links_df["type"] == "external").sum()) if not links_df.empty else 0
    word_count = len(full_text.split())
    reading_minutes = max(1, round(word_count / 200))

    top_row = st.columns([0.8, 1, 1, 1])
    with top_row[0]:
        st.markdown('<div class="ls-card">', unsafe_allow_html=True)
        st.markdown(donut_svg(n_internal, n_external), unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;">'
            f'<span class="ls-chip" style="background:{MINT}22;color:{MINT};">internal {n_internal}</span> '
            f'<span class="ls-chip" style="background:{CORAL}22;color:{CORAL};">external {n_external}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    tiles = [
        ("Title", title if len(title) < 60 else title[:57] + "…"),
        ("Word count", f"{word_count:,}"),
        ("Est. reading time", f"{reading_minutes} min"),
    ]
    for col, (label, value) in zip(top_row[1:], tiles):
        with col:
            st.markdown(
                f'<div class="ls-card"><div class="ls-label">{label}</div>'
                f'<div class="ls-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    tab_summary, tab_links, tab_domains = st.tabs(["Page contents", "Links", "Top domains"])

    with tab_summary:
        st.markdown('<div class="ls-card">', unsafe_allow_html=True)
        st.markdown(f"### {title}")
        st.caption(final_url)
        show_full = st.toggle(f"Show full text ({len(full_text):,} chars) instead of the preview", value=False)
        body = full_text if show_full else preview_text.split("\n\n", 1)[-1]
        st.text_area("Extracted text", body, height=380, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_links:
        st.markdown('<div class="ls-card">', unsafe_allow_html=True)
        if links_df.empty:
            st.caption("No links found on this page.")
        else:
            filter_choice = st.radio(
                "Filter", ["All", "Internal", "External"],
                horizontal=True, label_visibility="collapsed",
            )
            search = st.text_input("Search links", placeholder="Filter by URL text...")

            shown = links_df.copy()
            if filter_choice != "All":
                shown = shown[shown["type"] == filter_choice.lower()]
            if search:
                shown = shown[shown["link"].str.contains(search, case=False, na=False)]

            st.caption(f"{len(shown)} of {len(links_df)} links")

            def chip(t):
                color = MINT if t == "internal" else CORAL
                return f'<span class="ls-chip" style="background:{color}22;color:{color};">{t}</span>'

            rows_html = []
            for _, r in shown.head(500).iterrows():
                rows_html.append(
                    f'<div class="ls-row">{chip(r["type"])}'
                    f'<span class="ls-domain">{r["domain"]}</span>'
                    f'<a href="{r["link"]}" target="_blank">{r["link"]}</a></div>'
                )
            st.markdown("".join(rows_html), unsafe_allow_html=True)
            if len(shown) > 500:
                st.caption(f"Showing first 500 of {len(shown)} matching links — narrow your filter or download the CSV.")

            st.markdown("<br>", unsafe_allow_html=True)
            csv_buf = io.StringIO()
            links_df.to_csv(csv_buf, index=False)
            st.download_button(
                "Download all links as CSV",
                data=csv_buf.getvalue(),
                file_name="linkscope_links.csv",
                mime="text/csv",
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_domains:
        st.markdown('<div class="ls-card">', unsafe_allow_html=True)
        if links_df.empty:
            st.caption("No links found on this page.")
        else:
            domain_counts = Counter(links_df["domain"])
            domain_df = (
                pd.DataFrame(domain_counts.items(), columns=["domain", "links"])
                .sort_values("links", ascending=False)
                .set_index("domain")
            )
            st.markdown("**Links per domain**")
            st.bar_chart(domain_df, color=MINT)
            st.dataframe(domain_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
