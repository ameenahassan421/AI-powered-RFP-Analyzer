import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_risk_radar_chart(risk_data: dict):
    """Create radar chart for risk assessment"""
    categories = list(risk_data['risk_factors'].keys())
    scores = [risk_data['risk_factors'][cat]['score'] for cat in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=[cat.replace('_', ' ').title() for cat in categories] + [categories[0].replace('_', ' ').title()],
        fill='toself',
        name='Risk Levels'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        title="Risk Assessment Radar"
    )
    return fig

def create_timeline_gantt(timeline_data: dict):
    """Create Gantt chart for project timeline"""
    df = pd.DataFrame(timeline_data['timeline_milestones'])
    df['start'] = pd.to_datetime(df['start_date'])
    df['end'] = pd.to_datetime(df['end_date'])

    fig = px.timeline(df, x_start="start", x_end="end", y="task", title="Proposal Timeline")
    fig.update_yaxes(autorange="reversed")
    return fig

def create_win_probability_gauge(probability: int):
    """Atharii-styled light gauge for win probability."""
    # Brand colors
    OLIVE = "#6F7B57"
    OLIVE_DARK = "#555F40"
    AMBER = "#D7A13C"
    BORDER = "#E6E0D3"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Win Probability", "font": {"color": OLIVE_DARK, "size": 16}},
        delta={"reference": 50, "increasing": {"color": OLIVE}, "decreasing": {"color": "#CB5B3D"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": OLIVE_DARK},
            "bar": {"color": OLIVE},
            "bgcolor": "#FFFFFF",
            "borderwidth": 1,
            "bordercolor": BORDER,
            "steps": [
                {"range": [0, 40], "color": "#F2F2F2"},
                {"range": [40, 70], "color": "#EDEBE6"},
                {"range": [70, 100], "color": "#FFF8EC"},
            ],
            "threshold": {
                "line": {"color": AMBER, "width": 4},
                "thickness": 0.75,
                "value": 90,
            },
        },
        number={"font": {"color": OLIVE, "size": 44}}
    ))

    fig.update_layout(
        template=None,
        paper_bgcolor="rgba(0,0,0,0)",  # transparent to match page
        plot_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=10, b=10),
        font={"color": OLIVE}
    )
    return fig