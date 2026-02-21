import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─────────────────────────────────────────────
#  Page config & global CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CO₂ Emissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Root tokens ── */
    :root {
        --bg:        #0d1117;
        --surface:   #161b22;
        --border:    #21262d;
        --accent:    #3fb950;
        --accent2:   #58a6ff;
        --warn:      #f78166;
        --text:      #e6edf3;
        --muted:     #8b949e;
        --font-head: 'DM Serif Display', Georgia, serif;
        --font-body: 'DM Sans', system-ui, sans-serif;
        --radius:    12px;
    }

    /* ── Global resets ── */
    html, body, [class*="css"] {
        font-family: var(--font-body);
        background-color: var(--bg);
        color: var(--text);
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Page header ── */
    .dash-header {
        display: flex;
        align-items: baseline;
        gap: 14px;
        padding: 2rem 0 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    .dash-header h1 {
        font-family: var(--font-head);
        font-size: 2.4rem;
        font-weight: 400;
        letter-spacing: -0.5px;
        margin: 0;
        color: var(--text);
    }
    .dash-header .badge {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        background: var(--accent);
        color: #000;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 4px;
    }

    /* ── Section headings ── */
    .section-label {
        font-family: var(--font-head);
        font-size: 1.3rem;
        font-weight: 400;
        color: var(--text);
        margin: 2rem 0 0.8rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
        margin-left: 8px;
    }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 1rem; margin: 0.5rem 0 2rem; }
    .metric-card {
        flex: 1;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent);
    }
    .metric-card.accent2::before { background: var(--accent2); }
    .metric-card.warn::before    { background: var(--warn); }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: var(--font-head);
        font-size: 1.9rem;
        line-height: 1;
        color: var(--text);
    }
    .metric-sub {
        font-size: 0.78rem;
        color: var(--muted);
        margin-top: 4px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] .sidebar-title {
        font-family: var(--font-head);
        font-size: 1.1rem;
        color: var(--accent);
        padding: 1rem 0 0.3rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    /* ── Chart wrapper ── */
    .chart-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1.2rem 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* ── Streamlit slider & select overrides ── */
    .stSlider > div > div > div { color: var(--accent) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  Matplotlib dark theme shared across all charts
# ─────────────────────────────────────────────
CHART_BG   = "#161b22"
CHART_FG   = "#e6edf3"
MUTED      = "#8b949e"
ACCENT     = "#3fb950"
ACCENT2    = "#58a6ff"
WARN       = "#f78166"


def apply_chart_style(ax, fig):
    """Apply cohesive dark styling to any matplotlib axes."""
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(CHART_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#21262d")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x/1e9:.1f}B" if abs(x) >= 1e9
        else f"{x/1e6:.1f}M" if abs(x) >= 1e6
        else f"{x:,.0f}"
    ))
    ax.grid(axis="y", color="#21262d", linewidth=0.7, linestyle="--")
    ax.grid(axis="x", visible=False)


# ─────────────────────────────────────────────
#  Data
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/processed/co2_cleaned.csv")
    df = df.sort_values(["country", "year"])
    df["annual_co2"] = df.groupby("country")["co2_tons"].diff()
    return df


df = load_data()

# ─────────────────────────────────────────────
#  Sidebar controls
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙ Controls</p>', unsafe_allow_html=True)

    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    selected_year = st.slider("Year", min_year, max_year, max_year)

    countries = sorted(df["country"].dropna().unique())
    default_idx = countries.index("United States") if "United States" in countries else 0
    selected_country = st.selectbox("Country", countries, index=default_idx)

    view_mode = st.radio("View Mode", ["Total Emissions", "Per Capita"])

# ─────────────────────────────────────────────
#  Derived frames
# ─────────────────────────────────────────────
year_df = df[df["year"] == selected_year].copy()
year_df["co2_per_capita"] = year_df["annual_co2"] / year_df["population_2022"]

country_df = df[df["country"] == selected_country].copy()

# ─────────────────────────────────────────────
#  Page header
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <div class="dash-header">
        <h1>🌍 Global CO₂ Emissions</h1>
        <span class="badge">Dashboard</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  Key Metrics
# ─────────────────────────────────────────────
st.markdown(
    f'<p class="section-label">📊 Snapshot — {selected_year}</p>',
    unsafe_allow_html=True,
)

total_global   = year_df["annual_co2"].sum()
country_value  = year_df[year_df["country"] == selected_country]["annual_co2"].sum()
share_str      = f"{(country_value / total_global * 100):.2f}%" if country_value > 0 else "N/A"

st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Global CO₂</div>
            <div class="metric-value">{total_global:,.0f}</div>
            <div class="metric-sub">metric tons total</div>
        </div>
        <div class="metric-card accent2">
            <div class="metric-label">{selected_country}</div>
            <div class="metric-value">{country_value:,.0f}</div>
            <div class="metric-sub">metric tons</div>
        </div>
        <div class="metric-card warn">
            <div class="metric-label">Country Share</div>
            <div class="metric-value">{share_str}</div>
            <div class="metric-sub">of global emissions</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  Charts – side by side
# ─────────────────────────────────────────────
st.markdown(
    f'<p class="section-label">📈 Emissions Trends</p>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns(2)

# Country trend
with col_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(6, 3.4))
    sns.lineplot(
        data=country_df, x="year", y="annual_co2",
        ax=ax, color=ACCENT2, linewidth=2,
    )
    ax.fill_between(country_df["year"], country_df["annual_co2"],
                    alpha=0.12, color=ACCENT2)
    ax.set_title(f"{selected_country}", fontsize=11, pad=8, color=CHART_FG)
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual CO₂")
    apply_chart_style(ax, fig)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

# Global trend
with col_right:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    global_trend = df.groupby("year")["annual_co2"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 3.4))
    sns.lineplot(
        data=global_trend, x="year", y="annual_co2",
        ax=ax, color=ACCENT, linewidth=2,
    )
    ax.fill_between(global_trend["year"], global_trend["annual_co2"],
                    alpha=0.12, color=ACCENT)
    ax.set_title("Global", fontsize=11, pad=8, color=CHART_FG)
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual CO₂")
    apply_chart_style(ax, fig)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Top Emitters + Bubble Chart
# ─────────────────────────────────────────────
col_table, col_bubble = st.columns([1, 1.6])

with col_table:
    st.markdown(
        f'<p class="section-label">🏆 Top 10 Emitters — {selected_year}</p>',
        unsafe_allow_html=True,
    )
    if view_mode == "Total Emissions":
        top_emitters = (
            year_df.groupby("country")["annual_co2"]
            .sum().sort_values(ascending=False).head(10).reset_index()
        )
        value_col, label = "annual_co2", "CO₂ (tons)"
    else:
        top_emitters = (
            year_df.groupby("country")["co2_per_capita"]
            .mean().sort_values(ascending=False).head(10).reset_index()
        )
        value_col, label = "co2_per_capita", "CO₂ per Capita"

    top_emitters.columns = ["Country", label]
    st.dataframe(
        top_emitters.style.format({label: "{:,.2f}"}),
        use_container_width=True,
        height=340,
    )

with col_bubble:
    st.markdown(
        '<p class="section-label">🔵 Population vs Area</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    bubble_df = year_df.dropna(
        subset=["population_2022", "area_km2", "annual_co2"]
    ).copy()
    bubble_df = bubble_df[bubble_df["population_2022"] > 1e6]
    sizes = (bubble_df["annual_co2"] / bubble_df["annual_co2"].max()) * 1500

    fig, ax = plt.subplots(figsize=(7, 4.2))
    scatter = ax.scatter(
        bubble_df["population_2022"],
        bubble_df["area_km2"],
        s=sizes,
        alpha=0.55,
        c=bubble_df["annual_co2"],
        cmap="YlOrRd",
        edgecolors="#21262d",
        linewidths=0.4,
    )
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=MUTED, labelcolor=MUTED)
    cbar.set_label("CO₂ (tons)", color=MUTED, fontsize=8)
    cbar.outline.set_edgecolor("#21262d")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Population (log)")
    ax.set_ylabel("Area km² (log)")
    ax.set_title("Bubble size & colour = CO₂ emissions", fontsize=10, pad=8)

    # Override formatter for log axes
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(
            mticker.FuncFormatter(
                lambda x, _: f"{x/1e6:.0f}M" if x >= 1e6 else f"{x/1e3:.0f}K"
            )
        )

    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(CHART_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#21262d")
    ax.grid(color="#21262d", linewidth=0.5, linestyle="--", alpha=0.6)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)