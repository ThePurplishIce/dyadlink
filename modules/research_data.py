import plotly.graph_objects as go

from modules.i18n import tr


PAPER_DOI = "https://doi.org/10.21203/rs.3.rs-10884877/v3"
PAPER_CITATION = (
    "Cheng, W. W., for the Alzheimer’s Disease Neuroimaging Initiative. "
    "(2026). *Separating ECog scale-score information from dyad availability: "
    "observation-process contributions to dyadic prediction of cognitive "
    "impairment in ADNI* (Version 3). Research Square."
)
ACOUSTIC_PAPER_DOI = "https://doi.org/10.3233/JAD-150520"
ACOUSTIC_PAPER_CITATION = (
    "Fraser, K. C., Meltzer, J. A., & Rudzicz, F. (2016). Linguistic features "
    "identify Alzheimer’s disease in narrative speech. *Journal of "
    "Alzheimer’s Disease*, 49(2), 407–422."
)

PAPER_SUMMARY = (
    "In this ADNI analysis, missingness-indicator imputation may increase the "
    "apparent discriminative contribution of dyadic measures; much of the "
    "observed gain was associated with dyad availability, and limited evidence "
    "was found for an independent contribution from ECog scale scores."
)

RESULTS = (
    {
        "label": "M2 基準模型",
        "label_key": "chart_m2",
        "detail_key": "chart_detail_m2",
        "delta_key": "chart_delta_base",
        "chart_label": "M2 基準",
        "value": 0.680,
        "detail": "傳統預測因子模型（M2）",
        "delta": "基準",
    },
    {
        "label": "加入配對資料可得性",
        "label_key": "chart_availability",
        "detail_key": "chart_detail_availability",
        "delta_key": "chart_delta_availability",
        "chart_label": "＋配對可得性",
        "value": 0.733,
        "detail": "M2 + ADNI 配對 ECog 報告可得性",
        "delta": "論文報告 ΔC = +0.052；95% CI 0.023–0.082",
    },
    {
        "label": "再加入 ECog 平均分數",
        "label_key": "chart_ecog",
        "detail_key": "chart_detail_ecog",
        "delta_key": "chart_delta_ecog",
        "chart_label": "＋ECog 分數",
        "value": 0.758,
        "detail": "M3：M2 + 配對資料可得性 + dyadic ECog mean",
        "delta": "相對於可得性模型，論文報告 ΔC = +0.026；95% CI 0.007–0.045",
    },
)

COLORS = ("#244B69", "#168A78", "#D59A35")


def build_c_index_figure() -> go.Figure:
    labels = [tr(item["label_key"]) for item in RESULTS]
    values = [item["value"] for item in RESULTS]
    hover_details = [
        f"<b>{tr(item['label_key'])}</b><br>{tr(item['detail_key'])}<br>"
        f"C-index: {item['value']:.3f}<br>{tr(item['delta_key'])}"
        for item in RESULTS
    ]

    figure = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker={"color": COLORS, "line": {"width": 0}},
            text=[f"{value:.3f}" for value in values],
            textposition="outside",
            textfont={"color": "#18344A", "size": 15},
            customdata=hover_details,
            hovertemplate="%{customdata}<extra></extra>",
            cliponaxis=False,
        )
    )
    figure.update_layout(
        height=330,
        margin={"l": 108, "r": 28, "t": 54, "b": 44},
        bargap=0.48,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#234158"},
        xaxis={
            "title": {"text": tr("cindex_axis"), "standoff": 12},
            "range": [0, 1],
            "tickvals": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "tickformat": ".1f",
            "gridcolor": "#E9F0F5",
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "autorange": "reversed",
            "showgrid": False,
            "ticks": "",
            "fixedrange": True,
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#D8E3EB",
            "font": {"color": "#18344A", "size": 13},
            "align": "left",
        },
    )
    figure.add_annotation(
        x=1,
        y=1.12,
        xref="paper",
        yref="paper",
        text=tr("chart_aha_annotation"),
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        align="right",
        bgcolor="#E8F3F6",
        bordercolor="#C7DDE5",
        borderpad=6,
        font={"color": "#18344A", "size": 12},
    )
    return figure
