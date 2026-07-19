from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Georgia Institutional Effectiveness Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CONSTANTS
# =============================================================================

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "georgia_dashboard_data.csv"

NAVY = "#102A43"
TEAL = "#0F6B68"
GREEN = "#2F855A"
RED = "#C05621"
GOLD = "#B7791F"
GRAY = "#718096"
LIGHT_BG = "#F4F7FA"

STATUS_COLORS = {
    "Higher-than-expected completion": GREEN,
    "Near-expected completion": GRAY,
    "Lower-than-expected completion": RED,
    "Unavailable": "#A0AEC0",
}

EQUITY_COLORS = {
    "Higher-than-expected equity": GREEN,
    "Near-expected equity": GRAY,
    "Lower-than-expected equity": RED,
    "Unavailable": "#A0AEC0",
}

RESOURCE_COLORS = {
    "Higher-than-expected resources": GREEN,
    "Near-expected resources": GRAY,
    "Lower-than-expected resources": RED,
    "Unavailable": "#A0AEC0",
}


# =============================================================================
# STYLING
# =============================================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {LIGHT_BG};
    }}

    .main .block-container {{
        max-width: 1500px;
        padding-top: 1.25rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3 {{
        color: {NAVY};
    }}

    [data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid #D8E1E8;
        border-radius: 0.75rem;
        padding: 0.9rem;
        box-shadow: 0 1px 4px rgba(16, 42, 67, 0.07);
    }}

    [data-testid="stSidebar"] {{
        background-color: #EEF3F7;
    }}

    .dashboard-header {{
        background: linear-gradient(105deg, {NAVY}, #174E63);
        color: white;
        padding: 1.35rem 1.6rem;
        border-radius: 0.85rem;
        margin-bottom: 1rem;
    }}

    .dashboard-header h1 {{
        color: white;
        margin: 0;
        font-size: 2rem;
    }}

    .dashboard-header p {{
        color: #DCEAF0;
        margin: 0.35rem 0 0 0;
    }}

    .interpretation-box {{
        background-color: white;
        border-left: 6px solid {TEAL};
        padding: 0.95rem 1.1rem;
        border-radius: 0.6rem;
        margin: 0.5rem 0 1rem 0;
    }}

    .small-note {{
        color: #5F6F7A;
        font-size: 0.88rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# DATA HELPERS
# =============================================================================

EXPECTED_COLUMNS = [
    "UNITID",
    "institution_name",
    "institution_control",
    "locale",
    "peer_community",
    "profile_label",
    "observed_completion",
    "expected_completion",
    "completion_outperformance",
    "completion_outperformance_z",
    "completion_status",
    "completion_peer_percentile",
    "pell_equity_observed",
    "pell_equity_expected",
    "pell_equity_outperformance",
    "equity_outperformance_z",
    "equity_status",
    "equity_peer_percentile",
    "combined_outperformance_z",
    "combined_performance_status",
    "combined_outcome_peer_percentile",
    "strategic_quadrant",
    "resource_overall",
    "resource_student_facing",
    "resource_affordability",
    "resource_category",
    "resource_status",
    "resource_peer_percentile",
    "outperforming_with_constrained_resources",
    "dual_outcome_outperforming_with_constrained_resources",
    "priority_score",
]

NUMERIC_COLUMNS = [
    "UNITID",
    "observed_completion",
    "expected_completion",
    "completion_outperformance",
    "completion_outperformance_z",
    "completion_peer_percentile",
    "pell_equity_observed",
    "pell_equity_expected",
    "pell_equity_outperformance",
    "equity_outperformance_z",
    "equity_peer_percentile",
    "combined_outperformance_z",
    "combined_outcome_peer_percentile",
    "resource_overall",
    "resource_student_facing",
    "resource_affordability",
    "resource_peer_percentile",
    "priority_score",
]

BOOLEAN_COLUMNS = [
    "outperforming_with_constrained_resources",
    "dual_outcome_outperforming_with_constrained_resources",
]


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the Georgia dashboard data."""

    if not path.exists():
        raise FileNotFoundError(
            "Dashboard data were not found. Expected this file:\n"
            f"{path}\n\n"
            "Repository structure must include:\n"
            "data/georgia_dashboard_data.csv"
        )

    dataframe = pd.read_csv(path, low_memory=False)

    # Remove accidental blank columns caused by trailing commas.
    dataframe = dataframe.loc[
        :,
        ~dataframe.columns.astype(str).str.startswith("Unnamed:")
    ].copy()

    missing_required = [
        column
        for column in [
            "UNITID",
            "institution_name",
            "observed_completion",
            "expected_completion",
            "completion_outperformance",
        ]
        if column not in dataframe.columns
    ]

    if missing_required:
        raise ValueError(
            "The CSV is missing required columns:\n"
            f"{missing_required}\n\n"
            "Columns found:\n"
            f"{dataframe.columns.tolist()}"
        )

    # Add optional columns as missing so the app can still load.
    for column in EXPECTED_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = np.nan

    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe["UNITID"] = dataframe["UNITID"].astype("Int64")

    for column in BOOLEAN_COLUMNS:
        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
            .str.lower()
            .map(
                {
                    "true": True,
                    "1": True,
                    "yes": True,
                    "y": True,
                    "false": False,
                    "0": False,
                    "no": False,
                    "n": False,
                }
            )
            .astype("boolean")
        )

    text_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in NUMERIC_COLUMNS + BOOLEAN_COLUMNS
    ]

    for column in text_columns:
        dataframe[column] = dataframe[column].astype("string")

    dataframe["institution_name"] = (
        dataframe["institution_name"]
        .fillna("Institution " + dataframe["UNITID"].astype(str))
        .str.strip()
    )

    dataframe = (
        dataframe.dropna(subset=["UNITID"])
        .drop_duplicates(subset=["UNITID"], keep="first")
        .sort_values(["institution_name", "UNITID"])
        .reset_index(drop=True)
    )

    if dataframe.empty:
        raise ValueError("The dashboard CSV contains no usable institutions.")

    return dataframe


def valid_number(value: object) -> bool:
    """Return True when value can be displayed as a finite number."""

    try:
        return pd.notna(value) and np.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def format_number(
    value: object,
    suffix: str = "",
    decimals: int = 1,
    signed: bool = False,
) -> str:
    """Format a number for metrics and tables."""

    if not valid_number(value):
        return "Not available"

    number = float(value)
    sign_format = "+" if signed else ""
    return f"{number:{sign_format}.{decimals}f}{suffix}"


def available_values(
    dataframe: pd.DataFrame,
    column: str,
) -> list[str]:
    """Return sorted, nonblank values for a filter."""

    if column not in dataframe.columns:
        return []

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[
        (values != "")
        & (values.str.lower() != "<na>")
        & (values.str.lower() != "nan")
    ]

    return sorted(values.unique().tolist())


def clean_display_value(value: object) -> str:
    """Display missing text values consistently."""

    if pd.isna(value):
        return "Not available"

    text = str(value).strip()

    if text == "" or text.lower() in {"nan", "<na>", "none"}:
        return "Not available"

    return text


def filter_options(
    label: str,
    dataframe: pd.DataFrame,
    column: str,
) -> list[str]:
    """Create a sidebar multiselect that defaults to all values."""

    options = available_values(dataframe, column)

    if not options:
        return []

    return st.sidebar.multiselect(
        label,
        options=options,
        default=options,
    )


def apply_text_filter(
    dataframe: pd.DataFrame,
    column: str,
    selected_values: Iterable[str],
) -> pd.DataFrame:
    """Filter a dataframe by selected text values."""

    selected_values = list(selected_values)

    if not selected_values:
        return dataframe

    return dataframe.loc[
        dataframe[column].astype(str).isin(selected_values)
    ].copy()


def percentile_label(value: object) -> str:
    """Convert a percentile to a readable label."""

    if not valid_number(value):
        return "Not available"

    return f"{float(value):.1f}th percentile"


# =============================================================================
# LOAD DATA
# =============================================================================

try:
    data = load_data(DATA_PATH)
except Exception as error:
    st.error("The dashboard could not load its data.")
    st.exception(error)
    st.stop()


# =============================================================================
# HEADER
# =============================================================================

st.markdown(
    """
    <div class="dashboard-header">
        <h1>Georgia Institutional Effectiveness Dashboard</h1>
        <p>
            Context-adjusted completion, Pell equity, resource adequacy,
            institutional profiles, and empirical peer comparisons
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SIDEBAR FILTERS
# =============================================================================

st.sidebar.title("Dashboard controls")
st.sidebar.caption(
    f"{len(data):,} Georgia institutions are available before filtering."
)

filtered = data.copy()

selected_controls = filter_options(
    "Institutional control",
    filtered,
    "institution_control",
)
filtered = apply_text_filter(
    filtered,
    "institution_control",
    selected_controls,
)

selected_communities = filter_options(
    "Peer community",
    filtered,
    "peer_community",
)
filtered = apply_text_filter(
    filtered,
    "peer_community",
    selected_communities,
)

selected_completion_statuses = filter_options(
    "Completion status",
    filtered,
    "completion_status",
)
filtered = apply_text_filter(
    filtered,
    "completion_status",
    selected_completion_statuses,
)

selected_resource_categories = filter_options(
    "Resource category",
    filtered,
    "resource_category",
)
filtered = apply_text_filter(
    filtered,
    "resource_category",
    selected_resource_categories,
)

if filtered.empty:
    st.warning("No institutions match the current filters.")
    st.stop()

filtered["institution_selector"] = (
    filtered["institution_name"].astype(str)
    + " ("
    + filtered["UNITID"].astype(str)
    + ")"
)

selector_options = filtered["institution_selector"].tolist()

default_index = 0
ksu_matches = [
    option
    for option in selector_options
    if "kennesaw state university" in option.lower()
]

if ksu_matches:
    default_index = selector_options.index(ksu_matches[0])

selected_label = st.sidebar.selectbox(
    "Select institution",
    options=selector_options,
    index=default_index,
)

selected_row = filtered.loc[
    filtered["institution_selector"].eq(selected_label)
].iloc[0]

st.sidebar.markdown("---")

st.sidebar.download_button(
    label="Download filtered Georgia data",
    data=(
        filtered.drop(
            columns=["institution_selector"],
            errors="ignore",
        )
        .to_csv(index=False)
        .encode("utf-8")
    ),
    file_name="filtered_georgia_dashboard_data.csv",
    mime="text/csv",
)

st.sidebar.markdown(
    """
    <p class="small-note">
    Results are institution-level predictive associations intended
    for diagnostic planning, not punitive ranking.
    </p>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SELECTED INSTITUTION HEADER
# =============================================================================

st.subheader(clean_display_value(selected_row["institution_name"]))

descriptor = [
    clean_display_value(selected_row.get("institution_control")),
    clean_display_value(selected_row.get("peer_community")),
    clean_display_value(selected_row.get("profile_label")),
]
descriptor = [
    value
    for value in descriptor
    if value != "Not available"
]

if descriptor:
    st.caption(" • ".join(descriptor))


# =============================================================================
# PRIMARY METRICS
# =============================================================================

observed_completion = selected_row.get("observed_completion")
expected_completion = selected_row.get("expected_completion")
completion_outperformance = selected_row.get("completion_outperformance")
pell_equity_outperformance = selected_row.get("pell_equity_outperformance")

metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    "Observed completion",
    format_number(observed_completion, "%"),
)

metric_2.metric(
    "Context-expected completion",
    format_number(expected_completion, "%"),
)

metric_3.metric(
    "Completion outperformance",
    format_number(
        completion_outperformance,
        " pp",
        signed=True,
    ),
)

metric_4.metric(
    "Pell-equity outperformance",
    format_number(
        pell_equity_outperformance,
        " pp",
        signed=True,
    ),
)


# =============================================================================
# TABS
# =============================================================================

(
    overview_tab,
    comparison_tab,
    equity_tab,
    resources_tab,
    peers_tab,
    data_tab,
) = st.tabs(
    [
        "Institution overview",
        "Georgia comparison",
        "Pell equity",
        "Resources and strategy",
        "Peers and profiles",
        "Data and methods",
    ]
)


# =============================================================================
# TAB 1: INSTITUTION OVERVIEW
# =============================================================================

with overview_tab:
    left_column, right_column = st.columns([1.55, 1])

    with left_column:
        if valid_number(observed_completion) and valid_number(expected_completion):
            comparison_data = pd.DataFrame(
                {
                    "Measure": [
                        "Context-expected completion",
                        "Observed completion",
                    ],
                    "Rate": [
                        float(expected_completion),
                        float(observed_completion),
                    ],
                }
            )

            figure = px.bar(
                comparison_data,
                x="Rate",
                y="Measure",
                orientation="h",
                text="Rate",
                title="Observed versus context-based expected completion",
                color="Measure",
                color_discrete_map={
                    "Context-expected completion": "#718096",
                    "Observed completion": TEAL,
                },
            )

            figure.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
            )

            figure.update_layout(
                height=380,
                showlegend=False,
                xaxis_title="Completion rate (%)",
                yaxis_title="",
                margin=dict(l=20, r=40, t=60, b=40),
            )

            figure.update_xaxes(
                range=[
                    0,
                    max(
                        float(observed_completion),
                        float(expected_completion),
                        1,
                    )
                    * 1.18,
                ]
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Observed and expected completion values are not both "
                "available for this institution."
            )

    with right_column:
        st.markdown("#### Benchmark summary")

        summary_table = pd.DataFrame(
            {
                "Measure": [
                    "Completion status",
                    "Completion peer percentile",
                    "Combined outcome status",
                    "Combined peer percentile",
                    "Strategic quadrant",
                    "Resource status",
                ],
                "Value": [
                    clean_display_value(selected_row.get("completion_status")),
                    percentile_label(
                        selected_row.get("completion_peer_percentile")
                    ),
                    clean_display_value(
                        selected_row.get("combined_performance_status")
                    ),
                    percentile_label(
                        selected_row.get("combined_outcome_peer_percentile")
                    ),
                    clean_display_value(selected_row.get("strategic_quadrant")),
                    clean_display_value(selected_row.get("resource_status")),
                ],
            }
        )

        st.dataframe(
            summary_table,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        """
        <div class="interpretation-box">
            <b>How to read outperformance:</b> positive values indicate
            that the observed outcome exceeded the context-based expectation;
            negative values indicate that the observed outcome was below the
            expectation. These estimates are diagnostic associations and do
            not identify causal institutional effects.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# TAB 2: GEORGIA COMPARISON
# =============================================================================

with comparison_tab:
    st.markdown("### Georgia observed versus expected completion")

    plot_data = filtered.dropna(
        subset=[
            "observed_completion",
            "expected_completion",
        ]
    ).copy()

    if len(plot_data) >= 3:
        scatter = px.scatter(
            plot_data,
            x="expected_completion",
            y="observed_completion",
            color="completion_status",
            color_discrete_map=STATUS_COLORS,
            hover_name="institution_name",
            hover_data={
                "UNITID": True,
                "institution_control": True,
                "peer_community": True,
                "completion_outperformance": ":.1f",
                "completion_peer_percentile": ":.1f",
                "expected_completion": ":.1f",
                "observed_completion": ":.1f",
            },
            labels={
                "expected_completion": "Context-expected completion (%)",
                "observed_completion": "Observed completion (%)",
                "completion_status": "Completion status",
            },
        )

        minimum = float(
            min(
                plot_data["expected_completion"].min(),
                plot_data["observed_completion"].min(),
            )
        )
        maximum = float(
            max(
                plot_data["expected_completion"].max(),
                plot_data["observed_completion"].max(),
            )
        )

        padding = max((maximum - minimum) * 0.05, 1.0)

        scatter.add_shape(
            type="line",
            x0=minimum - padding,
            y0=minimum - padding,
            x1=maximum + padding,
            y1=maximum + padding,
            line=dict(
                dash="dash",
                color="#4A5568",
                width=1.4,
            ),
        )

        selected_plot_row = plot_data.loc[
            plot_data["UNITID"].eq(selected_row["UNITID"])
        ]

        if not selected_plot_row.empty:
            scatter.add_trace(
                go.Scatter(
                    x=selected_plot_row["expected_completion"],
                    y=selected_plot_row["observed_completion"],
                    mode="markers",
                    marker=dict(
                        size=18,
                        symbol="star",
                        color="#111111",
                        line=dict(
                            color="white",
                            width=1.5,
                        ),
                    ),
                    name=clean_display_value(
                        selected_row.get("institution_name")
                    ),
                    hovertemplate=(
                        "<b>"
                        + clean_display_value(
                            selected_row.get("institution_name")
                        )
                        + "</b><extra></extra>"
                    ),
                )
            )

        scatter.update_layout(
            height=620,
            margin=dict(l=20, r=20, t=30, b=40),
        )

        scatter.update_xaxes(
            range=[minimum - padding, maximum + padding]
        )
        scatter.update_yaxes(
            range=[minimum - padding, maximum + padding]
        )

        st.plotly_chart(
            scatter,
            use_container_width=True,
        )

        st.caption(
            "Institutions above the diagonal have observed completion "
            "greater than the context-based expectation."
        )
    else:
        st.info(
            "At least three complete institutions are required for "
            "the Georgia comparison plot."
        )

    st.markdown("### Completion outperformance across Georgia")

    ranking_data = (
        filtered.dropna(subset=["completion_outperformance"])
        .sort_values("completion_outperformance", ascending=True)
        .copy()
    )

    if not ranking_data.empty:
        ranking = px.bar(
            ranking_data,
            x="completion_outperformance",
            y="institution_name",
            orientation="h",
            color="completion_status",
            color_discrete_map=STATUS_COLORS,
            hover_data={
                "observed_completion": ":.1f",
                "expected_completion": ":.1f",
                "completion_peer_percentile": ":.1f",
            },
            labels={
                "completion_outperformance":
                    "Observed minus expected completion (pp)",
                "institution_name": "",
                "completion_status": "Completion status",
            },
        )

        ranking.add_vline(
            x=0,
            line_dash="dash",
            line_color="#4A5568",
        )

        ranking.update_layout(
            height=max(650, 22 * len(ranking_data)),
            margin=dict(l=20, r=20, t=30, b=40),
        )

        st.plotly_chart(
            ranking,
            use_container_width=True,
        )


# =============================================================================
# TAB 3: PELL EQUITY
# =============================================================================

with equity_tab:
    st.markdown("### Selected-institution Pell-equity results")

    equity_1, equity_2, equity_3, equity_4 = st.columns(4)

    equity_1.metric(
        "Observed Pell equity",
        format_number(
            selected_row.get("pell_equity_observed"),
            " pp",
            signed=True,
        ),
    )

    equity_2.metric(
        "Expected Pell equity",
        format_number(
            selected_row.get("pell_equity_expected"),
            " pp",
            signed=True,
        ),
    )

    equity_3.metric(
        "Equity outperformance",
        format_number(
            selected_row.get("pell_equity_outperformance"),
            " pp",
            signed=True,
        ),
    )

    equity_4.metric(
        "Equity peer percentile",
        percentile_label(
            selected_row.get("equity_peer_percentile")
        ),
    )

    st.caption(
        "Pell equity is defined as the Pell-recipient outcome minus "
        "the corresponding non-Pell outcome. Negative values indicate "
        "lower attainment among Pell recipients."
    )

    equity_data = (
        filtered.dropna(subset=["pell_equity_observed"])
        .sort_values("pell_equity_observed")
        .copy()
    )

    if not equity_data.empty:
        equity_figure = px.bar(
            equity_data,
            x="pell_equity_observed",
            y="institution_name",
            orientation="h",
            color="equity_status",
            color_discrete_map=EQUITY_COLORS,
            hover_data={
                "pell_equity_expected": ":.1f",
                "pell_equity_outperformance": ":.1f",
                "equity_peer_percentile": ":.1f",
            },
            labels={
                "pell_equity_observed":
                    "Pell minus non-Pell outcome (pp)",
                "institution_name": "",
                "equity_status": "Equity status",
            },
            title="Observed Pell equity across Georgia institutions",
        )

        equity_figure.add_vline(
            x=0,
            line_dash="dash",
            line_color="#4A5568",
        )

        equity_figure.update_layout(
            height=max(650, 22 * len(equity_data)),
            margin=dict(l=20, r=20, t=60, b=40),
        )

        st.plotly_chart(
            equity_figure,
            use_container_width=True,
        )

    equity_scatter_data = filtered.dropna(
        subset=[
            "pell_equity_expected",
            "pell_equity_observed",
        ]
    ).copy()

    if len(equity_scatter_data) >= 3:
        equity_scatter = px.scatter(
            equity_scatter_data,
            x="pell_equity_expected",
            y="pell_equity_observed",
            color="equity_status",
            color_discrete_map=EQUITY_COLORS,
            hover_name="institution_name",
            hover_data={
                "pell_equity_outperformance": ":.1f",
                "equity_peer_percentile": ":.1f",
            },
            labels={
                "pell_equity_expected": "Expected Pell equity (pp)",
                "pell_equity_observed": "Observed Pell equity (pp)",
                "equity_status": "Equity status",
            },
            title="Observed versus expected Pell equity",
        )

        minimum = float(
            min(
                equity_scatter_data["pell_equity_expected"].min(),
                equity_scatter_data["pell_equity_observed"].min(),
            )
        )
        maximum = float(
            max(
                equity_scatter_data["pell_equity_expected"].max(),
                equity_scatter_data["pell_equity_observed"].max(),
            )
        )

        equity_scatter.add_shape(
            type="line",
            x0=minimum,
            y0=minimum,
            x1=maximum,
            y1=maximum,
            line=dict(
                dash="dash",
                color="#4A5568",
            ),
        )

        equity_scatter.update_layout(height=560)

        st.plotly_chart(
            equity_scatter,
            use_container_width=True,
        )


# =============================================================================
# TAB 4: RESOURCES AND STRATEGY
# =============================================================================

with resources_tab:
    st.markdown("### Need-adjusted resource adequacy")

    resource_data = pd.DataFrame(
        {
            "Resource domain": [
                "Overall resources",
                "Student-facing resources",
                "Affordability",
            ],
            "Adequacy score": [
                selected_row.get("resource_overall"),
                selected_row.get("resource_student_facing"),
                selected_row.get("resource_affordability"),
            ],
        }
    )

    resource_data["Adequacy score"] = pd.to_numeric(
        resource_data["Adequacy score"],
        errors="coerce",
    )
    resource_data = resource_data.dropna(subset=["Adequacy score"])

    resource_left, resource_right = st.columns([1.5, 1])

    with resource_left:
        if not resource_data.empty:
            resource_figure = px.bar(
                resource_data,
                x="Adequacy score",
                y="Resource domain",
                orientation="h",
                text="Adequacy score",
                title="Selected-institution resource profile",
                labels={
                    "Adequacy score": "Standardized adequacy score",
                    "Resource domain": "",
                },
            )

            resource_figure.add_vline(
                x=0,
                line_dash="dash",
                line_color="#4A5568",
            )

            resource_figure.update_traces(
                texttemplate="%{text:.2f}",
                textposition="outside",
            )

            resource_figure.update_layout(
                height=420,
                showlegend=False,
            )

            st.plotly_chart(
                resource_figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Resource-adequacy measures are unavailable for "
                "this institution."
            )

    with resource_right:
        strategy_table = pd.DataFrame(
            {
                "Measure": [
                    "Resource category",
                    "Resource status",
                    "Resource peer percentile",
                    "Strategic quadrant",
                    "Priority score",
                    "Outperforming with constrained resources",
                ],
                "Value": [
                    clean_display_value(
                        selected_row.get("resource_category")
                    ),
                    clean_display_value(
                        selected_row.get("resource_status")
                    ),
                    percentile_label(
                        selected_row.get("resource_peer_percentile")
                    ),
                    clean_display_value(
                        selected_row.get("strategic_quadrant")
                    ),
                    format_number(
                        selected_row.get("priority_score"),
                        decimals=2,
                        signed=True,
                    ),
                    clean_display_value(
                        selected_row.get(
                            "outperforming_with_constrained_resources"
                        )
                    ),
                ],
            }
        )

        st.dataframe(
            strategy_table,
            use_container_width=True,
            hide_index=True,
        )

    resource_scatter_data = filtered.dropna(
        subset=[
            "resource_overall",
            "completion_outperformance",
        ]
    ).copy()

    if len(resource_scatter_data) >= 3:
        resource_scatter = px.scatter(
            resource_scatter_data,
            x="resource_overall",
            y="completion_outperformance",
            color="completion_status",
            color_discrete_map=STATUS_COLORS,
            hover_name="institution_name",
            hover_data={
                "resource_student_facing": ":.2f",
                "resource_affordability": ":.2f",
                "strategic_quadrant": True,
            },
            labels={
                "resource_overall":
                    "Overall need-adjusted resource adequacy (SD)",
                "completion_outperformance":
                    "Completion outperformance (pp)",
                "completion_status":
                    "Completion status",
            },
            title="Resource adequacy and completion outperformance",
        )

        resource_scatter.add_hline(
            y=0,
            line_dash="dash",
            line_color="#4A5568",
        )
        resource_scatter.add_vline(
            x=0,
            line_dash="dash",
            line_color="#4A5568",
        )

        resource_scatter.update_layout(height=570)

        st.plotly_chart(
            resource_scatter,
            use_container_width=True,
        )

    st.caption(
        "Resource adequacy reflects measured capacity relative to "
        "institutional context. It is not a direct measure of service "
        "quality, efficiency, faculty satisfaction, or causal impact."
    )


# =============================================================================
# TAB 5: PEERS AND PROFILES
# =============================================================================

with peers_tab:
    peer_1, peer_2, peer_3, peer_4 = st.columns(4)

    peer_1.metric(
        "Peer community",
        clean_display_value(selected_row.get("peer_community")),
    )

    peer_2.metric(
        "Institutional profile",
        clean_display_value(selected_row.get("profile_label")),
    )

    peer_3.metric(
        "Completion peer percentile",
        percentile_label(
            selected_row.get("completion_peer_percentile")
        ),
    )

    peer_4.metric(
        "Combined outcome percentile",
        percentile_label(
            selected_row.get("combined_outcome_peer_percentile")
        ),
    )

    community_value = selected_row.get("peer_community")
    profile_value = selected_row.get("profile_label")

    peer_subset = filtered.copy()

    if pd.notna(community_value):
        peer_subset = peer_subset.loc[
            peer_subset["peer_community"].eq(community_value)
        ].copy()

    st.markdown(
        "### Institutions in the selected empirical peer community"
    )

    peer_columns = [
        "institution_name",
        "institution_control",
        "profile_label",
        "observed_completion",
        "expected_completion",
        "completion_outperformance",
        "pell_equity_outperformance",
        "resource_overall",
    ]

    peer_display = (
        peer_subset[peer_columns]
        .sort_values(
            "completion_outperformance",
            ascending=False,
            na_position="last",
        )
        .rename(
            columns={
                "institution_name": "Institution",
                "institution_control": "Control",
                "profile_label": "Profile",
                "observed_completion": "Observed completion (%)",
                "expected_completion": "Expected completion (%)",
                "completion_outperformance":
                    "Completion outperformance (pp)",
                "pell_equity_outperformance":
                    "Pell-equity outperformance (pp)",
                "resource_overall": "Resource adequacy (SD)",
            }
        )
    )

    st.dataframe(
        peer_display,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Peer communities represent institutional-context similarity. "
        "They do not indicate institutional rank, collaboration, "
        "transfer relationships, or causal influence."
    )

    st.markdown("### Georgia profile distribution")

    profile_counts = (
        filtered["profile_label"]
        .dropna()
        .astype(str)
        .value_counts()
        .rename_axis("Profile")
        .reset_index(name="Institutions")
    )

    if not profile_counts.empty:
        profile_figure = px.bar(
            profile_counts,
            x="Profile",
            y="Institutions",
            text="Institutions",
        )

        profile_figure.update_layout(
            height=400,
            showlegend=False,
        )

        st.plotly_chart(
            profile_figure,
            use_container_width=True,
        )


# =============================================================================
# TAB 6: DATA AND METHODS
# =============================================================================

with data_tab:
    download_left, download_right = st.columns([1.35, 1])

    with download_left:
        st.markdown("### Selected-institution record")

        selected_record = (
            selected_row.drop(
                labels=["institution_selector"],
                errors="ignore",
            )
            .rename("Value")
            .to_frame()
        )

        st.dataframe(
            selected_record,
            use_container_width=True,
        )

        st.download_button(
            label="Download selected institution",
            data=(
                selected_row.drop(
                    labels=["institution_selector"],
                    errors="ignore",
                )
                .to_frame()
                .T
                .to_csv(index=False)
                .encode("utf-8")
            ),
            file_name=(
                f"{int(selected_row['UNITID'])}_"
                "institution_dashboard_record.csv"
            ),
            mime="text/csv",
        )

    with download_right:
        st.markdown("### Data availability")

        availability_rows = []

        for column in [
            "observed_completion",
            "expected_completion",
            "completion_outperformance",
            "pell_equity_observed",
            "pell_equity_expected",
            "pell_equity_outperformance",
            "resource_overall",
            "resource_student_facing",
            "resource_affordability",
        ]:
            availability_rows.append(
                {
                    "Variable": column,
                    "Available institutions": int(
                        data[column].notna().sum()
                    ),
                    "Total institutions": len(data),
                }
            )

        st.dataframe(
            pd.DataFrame(availability_rows),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Interpretation and methods")

    st.markdown(
        """
        - **Completion outperformance** is observed completion minus
          context-expected completion.
        - **Pell equity** is the Pell-recipient outcome minus the
          corresponding non-Pell outcome.
        - **Equity outperformance** is observed Pell equity minus
          context-expected Pell equity.
        - **Resource adequacy** compares measured institutional
          resources with the level expected for institutional context
          and student need.
        - **Peer communities** and **institutional profiles** are
          descriptive comparison tools rather than rankings.
        - Georgia institutions were evaluated after the national
          model-development framework was established.
        - All results are institution-level predictive associations.
          They do not establish causal effects.
        """
    )


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption(
    "Beyond Rankings: Equity-Conscious Benchmarking of Student Success "
    "in Georgia Higher Education | Brandi Jones"
)
