import streamlit as st
import pandas as pd
import json
from visualization.charts import *

# ---- Atharii tokens used throughout (match your page CSS) ----
ATH = {
    "bg": "#F7F1E6",        # sand page bg
    "surface": "#FFFFFF",   # card
    "border": "#E6E0D3",    # divider
    "text": "#1E2328",      # charcoal
    "muted": "#5F676F",     # secondary
    "olive": "#6F7B57",     # primary accent
    "olive_dark": "#555F40",
    "amber": "#D7A13C",
    "terr": "#CB5B3D",
}

# Inject a tiny bit of card CSS once
def _ensure_card_css():
    if getattr(st.session_state, "_atharii_cards_injected", False):
        return
    st.markdown(f"""
    <style>
      .ath-card {{
        background: {ATH['surface']};
        border: 1px solid {ATH['border']};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,.05);
        color: {ATH['text']};
        margin: 10px 0;
      }}
      .ath-card-left {{
        border-left: 6px solid {ATH['olive']};
      }}
      .ath-kpi {{
        background: #FFFDF8;
        border: 1px solid {ATH['border']};
        border-radius: 14px;
        text-align: center;
        padding: 20px;
        color: {ATH['olive_dark']};
      }}
      .ath-kpi h1 {{ margin: 0; font-size: 2.2rem; color:{ATH['olive_dark']}; }}
      .ath-kpi h3 {{ margin: 0 0 4px; color:{ATH['olive_dark']}; }}
      .ath-chip {{
        display:inline-flex; align-items:center; gap:8px;
        background:#fff; border:1px solid {ATH['border']};
        color:{ATH['olive']}; border-radius:999px; padding:5px 10px; font-size:.9rem;
      }}
    </style>
    """, unsafe_allow_html=True)
    st.session_state._atharii_cards_injected = True


def display_all_tabs(results: dict, organization_profile: str = None):
    """Display all analysis tabs"""
    _ensure_card_css()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Overview", "💰 Financial", "⚠️ Risk", "🏆 Competitive",
        "📅 Planning", "📋 Compliance", "🤝 Stakeholders", "📝 Content", "🔍 Compatibility"
    ])

    with tab1:
        display_overview_tab(results)
    with tab2:
        display_financial_tab(results)
    with tab3:
        display_risk_tab(results)
    with tab4:
        display_competitive_tab(results)
    with tab5:
        display_planning_tab(results)
    with tab6:
        display_compliance_tab(results)
    with tab7:
        display_stakeholder_tab(results)
    with tab8:
        display_content_tab(results)
    with tab9:
        display_compatibility_tab(results, organization_profile)

    display_export_section(results)


def display_overview_tab(results: dict):
    _ensure_card_css()
    st.subheader("📊 Executive Overview")

    basic_info = results['basic_info']
    risk = results['risk_assessment']
    competitive = results['competitive_analysis']

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Win Probability", f"{competitive['win_probability']}%",
                  f"{competitive['win_probability'] - 50}%")
    with col2:
        st.metric("Risk Level", risk['risk_level'],
                  "High" if risk['overall_risk_score'] > 7 else "Medium")
    with col3:
        budget = basic_info.get('total_budget', 'N/A')
        st.metric("Total Budget", budget if isinstance(budget, str) else str(budget), "Available")
    with col4:
        st.metric("Competitors", competitive['estimated_competitors'],
                  "Market" if competitive['estimated_competitors'] > 5 else "Limited")

    # Budget Highlight (calm Atharii card)
    if basic_info.get('total_budget'):
        st.markdown(f"""
        <div class="ath-kpi">
          <h3>💰 Total Contract Value</h3>
          <h1>{basic_info['total_budget']}</h1>
          <div style="color:{ATH['muted']}">Contract Term: {basic_info.get('contract_term', 'Not specified')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Facts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###  Key Information")
        important_fields = ['title', 'department_agency', 'date_of_submission', 'objective']
        for field in important_fields:
            if basic_info.get(field) and basic_info[field] != "null":
                st.markdown(f"""
                <div class="ath-card ath-card-left">
                  <strong>{field.replace('_', ' ').title()}</strong>
                  <p style="margin:.3rem 0 0">{basic_info[field]}</p>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("###  Quick Assessment")
        st.plotly_chart(create_win_probability_gauge(competitive['win_probability']), use_container_width=True)


def display_financial_tab(results: dict):
    _ensure_card_css()
    st.subheader("💰 Financial Deep Dive")

    financial = results['financial_analysis']

    if "error" in financial:
        st.error(f"Financial analysis unavailable: {financial['error']}")
        return

    # Financial Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        budget = financial.get('total_budget', 'N/A')
        st.metric("Total Budget", "Multiple Years" if isinstance(budget, dict) else str(budget))
    with col2:
        annual = financial.get('annual_budget', 'N/A')
        if isinstance(annual, dict):
            first_key = next(iter(annual.keys()))
            st.metric("Annual Budget", str(annual[first_key]))
        else:
            st.metric("Annual Budget", str(annual))
    with col3:
        score = financial.get('financial_score', 'N/A')
        st.metric("Financial Score", str(score))

    # Multi-Year Breakdown
    if isinstance(financial.get('annual_budget'), dict):
        st.markdown("#### 📅 Multi-Year Budget Breakdown")
        for year, amount in financial['annual_budget'].items():
            st.markdown(f"""
            <div class="ath-card ath-card-left">
              <strong>FY {year}</strong>
              <p style="margin:.3rem 0 0">{amount}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 💰 Financial Details")
    for field in ['payment_schedule', 'cost_sharing', 'budget_categories']:
        value = financial.get(field)
        if value and value != "null":
            if isinstance(value, dict):
                with st.expander(field.replace('_',' ').title()):
                    for k, v in value.items(): st.write(f"**{k}:** {v}")
            else:
                st.markdown(f"""
                <div class="ath-card ath-card-left">
                  <strong>{field.replace('_',' ').title()}</strong>
                  <p style="margin:.3rem 0 0">{value}</p>
                </div>
                """, unsafe_allow_html=True)


def display_risk_tab(results: dict):
    _ensure_card_css()
    st.subheader("⚠️ Risk Assessment")

    risk = results['risk_assessment']

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(create_risk_radar_chart(risk), use_container_width=True)
    with col2:
        st.metric("Overall Risk Score", f"{risk['overall_risk_score']}/10")
        st.metric("Risk Level", risk['risk_level'])
        st.metric("High Risks", len(risk['key_risks']))

    st.markdown("#### 🔍 Risk Factor Analysis")
    for risk_type, details in risk['risk_factors'].items():
        st.markdown(f"""
        <div class="ath-card ath-card-left">
          <h4 style="margin:0 0 .25rem">🛡️ {risk_type.replace('_', ' ').title()} (Score: {details['score']}/10)</h4>
          <p><strong>Factors:</strong> {', '.join(details['factors'])}</p>
          <p><strong>Mitigation:</strong> {', '.join(details['mitigation'])}</p>
        </div>
        """, unsafe_allow_html=True)


def display_competitive_tab(results: dict):
    _ensure_card_css()
    st.subheader("🏆 Competitive Intelligence")

    competitive = results['competitive_analysis']

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Win Probability", f"{competitive['win_probability']}%")
    with col2: st.metric("Competitors", competitive['estimated_competitors'])
    with col3: st.metric("Market", competitive['market_maturity'])
    with col4: st.metric("Confidence", competitive['confidence_level'])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Our Advantages")
        for advantage in competitive['our_competitive_advantages']:
            st.markdown(f"<span class='ath-chip'>🎯 {advantage}</span>", unsafe_allow_html=True)
        st.markdown("#### 💎 Differentiators")
        for d in competitive['key_differentiators']:
            st.markdown(f"<span class='ath-chip'>✨ {d}</span>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### ⚠️ Competitive Threats")
        for t in competitive['competitive_threats']:
            st.markdown(f"<span class='ath-chip'>🔴 {t}</span>", unsafe_allow_html=True)
        st.markdown("#### 🚧 Barriers to Entry")
        for b in competitive['barriers_to_entry']:
            st.markdown(f"<span class='ath-chip'>🛑 {b}</span>", unsafe_allow_html=True)

    st.markdown("#### 🎯 Strategic Recommendations")
    for i, rec in enumerate(competitive['strategic_recommendations'], 1):
        st.markdown(f"{i}. {rec}")


def display_planning_tab(results: dict):
    _ensure_card_css()
    st.subheader("📅 Resource & Timeline Planning")

    planning = results['resource_planning']
    st.plotly_chart(create_timeline_gantt(planning), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👥 Team Requirements")
        st.metric("Total Hours", planning['total_estimated_hours'])
        for role in planning['team_requirements']:
            st.markdown(f"👤 {role}")

    with col2:
        st.markdown("#### 📋 Project Details")
        st.metric("Critical Path Items", len(planning['critical_path']))
        st.metric("Resource Constraints", len(planning['resource_constraints']))
        if planning.get('recommended_start_date'):
            st.metric("Start Date", planning['recommended_start_date'])


def display_compliance_tab(results: dict):
    _ensure_card_css()
    st.subheader("📋 Compliance Matrix")

    compliance = results['compliance_matrix']
    total_items = len(compliance)
    compliant_items = sum(1 for item in compliance if item['our_status'] == 'Compliant')
    needs_review = sum(1 for item in compliance if item['our_status'] == 'Needs Review')

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Requirements", total_items)
    with col2: st.metric("Compliant", compliant_items)
    with col3: st.metric("Needs Review", needs_review)

    compliance_df = pd.DataFrame(compliance)
    st.dataframe(compliance_df, use_container_width=True)


def display_stakeholder_tab(results: dict):
    _ensure_card_css()
    st.subheader("🤝 Stakeholder Analysis")

    stakeholders = results['stakeholder_analysis']

    st.markdown("#### 🎯 Key Decision Makers")
    for dm in stakeholders['decision_makers']:
        influence_icon = "🔴" if dm['influence'] == 'High' else "🟡" if dm['influence'] == 'Medium' else "🟢"
        st.markdown(f"""
        <div class="ath-card ath-card-left">
          {influence_icon} <strong>{dm['role']}</strong> (Influence: {dm['influence']}, Interest: {dm['interest']})
          <p style="margin:.35rem 0 0"><strong>Key Concerns:</strong> {', '.join(dm['key_concerns'])}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 👥 Evaluation Committee")
    col1, col2 = st.columns(2)
    with col1:
        for member in stakeholders['evaluation_committee']:
            st.markdown(f"👤 {member}")

    st.markdown("#### 🗺️ Influence Map")
    for category, roles in stakeholders['influence_map'].items():
        st.markdown(f"**{category.replace('_', ' ').title()}:** {', '.join(roles)}")


def display_content_tab(results: dict):
    _ensure_card_css()
    st.subheader("📝 Proposal Content Suggestions")

    content = results['content_suggestions']

    st.markdown("#### 📄 Executive Summary Draft")
    st.info(content['executive_summary'])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎨 Key Themes")
        for theme in content['key_themes']: st.markdown(f"🎯 {theme}")

        st.markdown("#### 🛡️ Risk Mitigation")
        for strategy in content['risk_mitigation_strategies']: st.markdown(f"🛡️ {strategy}")

    with col2:
        st.markdown("#### 💎 Differentiators")
        for d in content['differentiators']: st.markdown(f"✨ {d}")

        st.markdown("#### ✅ Compliance Statements")
        for s in content['compliance_statements']: st.markdown(f"✅ {s}")

    st.markdown("#### 🏆 Winning Strategy")
    st.success(content['winning_strategy'])


def display_compatibility_tab(results: dict, organization_profile: str = None):
    _ensure_card_css()
    st.subheader("🔍 RFP-Organization Compatibility")

    if not organization_profile:
        st.warning("📝 Please upload your organization profile to analyze compatibility")
        return
    if "compatibility_analysis" not in results:
        st.error("Compatibility analysis not available")
        return

    compatibility = results['compatibility_analysis']
    if "error" in compatibility:
        st.error(f"Compatibility analysis error: {compatibility['error']}")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        score = compatibility.get('overall_compatibility_score', 0)
        if isinstance(score, str):
            score = int(''.join(filter(str.isdigit, score)) or 0)
        st.markdown(f"""
        <div class="ath-kpi">
          <h3>Compatibility Score</h3>
          <h1>{score}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric("Compatibility Level", compatibility.get('compatibility_level', 'Unknown'))
    with col3:
        st.metric("Recommendation", compatibility.get('recommendation', 'Unknown'))

    st.markdown("### 🎯 Go/No-Go Decision")
    if score >= 80:
        st.success("**✅ STRONGLY RECOMMENDED** — High alignment with your capabilities.")
    elif score >= 60:
        st.warning("**⚠️ CONDITIONALLY RECOMMENDED** — Moderate fit; close gaps before committing.")
    else:
        st.error("**🚨 NOT RECOMMENDED** — Low fit; consider alternatives.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Strengths & Alignment")
        for s in (compatibility.get('strengths_alignment') or [])[:6]:
            st.markdown(f"<div class='ath-card ath-card-left'><strong>🎯 {s}</strong></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### ⚠️ Gaps & Challenges")
        for g in (compatibility.get('gaps_identified') or [])[:6]:
            st.markdown(f"<div class='ath-card ath-card-left' style='border-left-color:{ATH['terr']}'><strong>🚧 {g}</strong></div>", unsafe_allow_html=True)

    st.markdown("### 📊 Detailed Analysis")
    analysis_fields = {
        'Strategic Fit': compatibility.get('strategic_fit'),
        'Risk Assessment': compatibility.get('risk_assessment'),
        'Resource Gap Analysis': compatibility.get('resource_gap_analysis'),
        'Effort Required': compatibility.get('estimated_effort_required'),
        'Timeline Feasibility': compatibility.get('timeline_feasibility')
    }
    for field, value in analysis_fields.items():
        if value and value != "null":
            st.markdown(f"""
            <div class="ath-card ath-card-left">
              <strong>{field}</strong>
              <p style="margin:.3rem 0 0">{value}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 💎 Your Competitive Advantages")
    for diff in (compatibility.get('key_differentiators') or []):
        st.success(f"✨ {diff}")

    st.markdown("### 🎯 Action Plan")
    if score >= 80:
        st.info("• Assign proposal team • Lead with strengths • Engage stakeholders early")
    elif score >= 60:
        st.warning("• Close gaps • Validate resources • Evaluate ROI/partnerships")
    else:
        st.error("• Reassess strategic fit • Estimate cost to close gaps • Seek alternatives")


def display_export_section(results: dict):
    st.markdown("---")
    st.markdown("### 📤 Export Comprehensive Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Generate Full Report", use_container_width=True):
            st.success("Full report generation started!")
    with col2:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.success("Excel export prepared!")
    with col3:
        json_str = json.dumps(results, indent=2, default=str)
        st.download_button(
            "📄 Download JSON",
            data=json_str,
            file_name="comprehensive_analysis.json",
            mime="application/json",
            use_container_width=True
        )
