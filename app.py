"""
BETTING ANALYTICS PRO - FIXED VERSION
Professional Football Match Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import math

# Page config
st.set_page_config(
    page_title="Betting Analytics Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Clean and professional
st.markdown("""
<style>
    /* Reset and base styles */
    .main {
        padding: 2rem;
    }
    
    /* Professional headers */
    .dashboard-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2D3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }
    
    /* Cards */
    .data-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    
    .team-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    
    .prediction-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    
    .prediction-high {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .prediction-medium {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    
    /* Progress bars */
    .progress-container {
        background: #E2E8F0;
        border-radius: 10px;
        height: 8px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
    }
    
    .progress-high { background: linear-gradient(90deg, #10B981, #059669); }
    .progress-medium { background: linear-gradient(90deg, #F59E0B, #D97706); }
    .progress-low { background: linear-gradient(90deg, #EF4444, #DC2626); }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }
    
    .badge-high { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
    .badge-medium { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }
    .badge-low { background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for form
if 'match_data' not in st.session_state:
    st.session_state.match_data = {
        'home_team': 'Roma',
        'away_team': 'Como',
        'home_btts': 30,
        'home_over': 20,
        'home_under': 70,
        'home_gf': 1.0,
        'home_ga': 0.8,
        'away_btts': 40,
        'away_over': 35,
        'away_under': 60,
        'away_gf': 1.3,
        'away_ga': 0.9,
        'big_club_home': True,
        'odds_btts': 1.80,
        'odds_over': 2.20,
        'odds_under': 1.58
    }

def calculate_expected_goals():
    """Calculate expected goals with adjustments"""
    data = st.session_state.match_data
    
    # Baseline calculation
    baseline = ((data['home_gf'] + data['away_ga']) + (data['away_gf'] + data['home_ga'])) / 2
    
    # Adjust for single trends
    adjusted = baseline
    
    adjustments = []
    
    # Home team adjustments
    if data['home_under'] >= 70:
        adjusted *= 0.85  # -15% for strong under trend
        adjustments.append(f"Roma has {data['home_under']}% Under trend at home (-15%)")
    
    # Away team adjustments (with context)
    if data['away_under'] >= 70:
        if data['big_club_home']:
            adjustments.append(f"Como's trend discounted (facing big club)")
        else:
            adjusted *= 0.85
            adjustments.append(f"Como has {data['away_under']}% Under trend away (-15%)")
    
    if data['big_club_home']:
        adjusted -= 0.1
        adjustments.append("Big club at home (-0.1 goals)")
    
    return baseline, adjusted, adjustments

def calculate_probabilities(expected_goals):
    """Calculate probabilities for betting markets"""
    data = st.session_state.match_data
    
    # Over/Under probabilities
    if expected_goals < 1.8:
        under_prob = 0.80
        over_prob = 0.20
    elif expected_goals < 2.2:
        under_prob = 0.70
        over_prob = 0.30
    elif expected_goals < 2.8:
        under_prob = 0.55
        over_prob = 0.45
    else:
        under_prob = 0.30
        over_prob = 0.70
    
    # BTTS probability
    btts_prob = min(0.95, max(0.05, (data['home_gf']/data['away_ga'] * data['away_gf']/data['home_ga']) * 0.7))
    
    return {
        'under': under_prob,
        'over': over_prob,
        'btts': btts_prob
    }

def calculate_value(probability, odds):
    """Calculate value metrics"""
    value = (probability * odds) - 1
    
    if value >= 0.25:
        category = "High Value"
        action = "STRONG BET"
        stake = 2.5
        color = "#10B981"
    elif value >= 0.15:
        category = "Good Value"
        action = "BET"
        stake = 1.5
        color = "#3B82F6"
    elif value >= 0.05:
        category = "Low Value"
        action = "CONSIDER"
        stake = 0.5
        color = "#F59E0B"
    else:
        category = "No Value"
        action = "AVOID"
        stake = 0.0
        color = "#6B7280"
    
    return {
        'value': value,
        'category': category,
        'action': action,
        'stake': stake,
        'color': color,
        'implied': 1/odds
    }

def create_team_card(team_name, is_home, stats):
    """Create a team statistics card"""
    with st.container():
        # Team header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {'🏠' if is_home else '✈️'} {team_name}")
            st.caption("Last 10 matches analysis")
        with col2:
            if is_home and st.session_state.match_data['big_club_home']:
                st.markdown('<span class="badge badge-high">Big Club</span>', unsafe_allow_html=True)
        
        # Two columns for stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trend Analysis**")
            
            # BTTS progress bar
            st.markdown(f"BTTS: **{stats['btts']}%**")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar progress-{'high' if stats['btts'] >= 70 else 'medium' if stats['btts'] >= 60 else 'low'}" 
                     style="width: {stats['btts']}%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Over progress bar
            st.markdown(f"Over 2.5: **{stats['over']}%**")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar progress-{'high' if stats['over'] >= 70 else 'medium' if stats['over'] >= 60 else 'low'}" 
                     style="width: {stats['over']}%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Under progress bar
            st.markdown(f"Under 2.5: **{stats['under']}%**")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar progress-{'high' if stats['under'] >= 70 else 'medium' if stats['under'] >= 60 else 'low'}" 
                     style="width: {stats['under']}%"></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Performance Metrics**")
            
            # Create metrics grid
            cols = st.columns(2)
            with cols[0]:
                st.metric("Goals For", f"{stats['gf']:.1f}")
                st.metric("Net Rating", f"{stats['gf'] - stats['ga']:+.1f}")
            with cols[1]:
                st.metric("Goals Against", f"{stats['ga']:.1f}")
                st.metric("Avg Goals", f"{(stats['gf'] + stats['ga'])/2:.1f}")

def create_prediction_card(market, probability, odds, value_data, market_type="Main"):
    """Create a prediction card"""
    card_class = "prediction-high" if value_data['value'] >= 0.15 else "prediction-medium"
    
    with st.container():
        st.markdown(f"""
        <div class="prediction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0;">{market}</h4>
                        <span class="badge" style="background: {value_data['color']};">{value_data['category']}</span>
                    </div>
                    <div style="color: #718096; font-size: 0.9rem;">{market_type} Recommendation</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{probability:.0%}</div>
                    <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics inside the card using Streamlit
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Market Odds", f"{odds:.2f}")
        with col2:
            st.metric("Value Edge", f"{value_data['value']:+.1%}")
        with col3:
            st.metric("Stake Size", f"{value_data['stake']:.1f}%")
        
        # Decision and EV
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**Decision:** {value_data['action']}")
        with col2:
            st.markdown(f"**Expected EV:** `{value_data['value']:.3f}`")

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="dashboard-title">BETTING ANALYTICS PRO</h1>', unsafe_allow_html=True)
    st.markdown('Professional Football Match Analysis Dashboard')
    
    # Quick input form in sidebar
    with st.sidebar:
        st.markdown("### 📊 Quick Input")
        
        col1, col2 = st.columns(2)
        with col1:
            home_team = st.text_input("Home Team", "Roma")
            home_btts = st.slider("Home BTTS %", 0, 100, 30)
            home_over = st.slider("Home Over %", 0, 100, 20)
            home_under = st.slider("Home Under %", 0, 100, 70)
            home_gf = st.number_input("Home GF/game", 0.0, 5.0, 1.0, 0.1)
            home_ga = st.number_input("Home GA/game", 0.0, 5.0, 0.8, 0.1)
            
        with col2:
            away_team = st.text_input("Away Team", "Como")
            away_btts = st.slider("Away BTTS %", 0, 100, 40)
            away_over = st.slider("Away Over %", 0, 100, 35)
            away_under = st.slider("Away Under %", 0, 100, 60)
            away_gf = st.number_input("Away GF/game", 0.0, 5.0, 1.3, 0.1)
            away_ga = st.number_input("Away GA/game", 0.0, 5.0, 0.9, 0.1)
        
        st.markdown("---")
        big_club = st.checkbox("Big Club at Home", True)
        
        st.markdown("### 💰 Market Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            odds_btts = st.number_input("BTTS", 1.01, 10.0, 1.80, 0.01)
        with col2:
            odds_over = st.number_input("Over 2.5", 1.01, 10.0, 2.20, 0.01)
        with col3:
            odds_under = st.number_input("Under 2.5", 1.01, 10.0, 1.58, 0.01)
        
        if st.button("🔄 Update Analysis", type="primary", use_container_width=True):
            st.session_state.match_data.update({
                'home_team': home_team,
                'away_team': away_team,
                'home_btts': home_btts,
                'home_over': home_over,
                'home_under': home_under,
                'home_gf': home_gf,
                'home_ga': home_ga,
                'away_btts': away_btts,
                'away_over': away_over,
                'away_under': away_under,
                'away_gf': away_gf,
                'away_ga': away_ga,
                'big_club_home': big_club,
                'odds_btts': odds_btts,
                'odds_over': odds_over,
                'odds_under': odds_under
            })
            st.rerun()
    
    # Match Header
    data = st.session_state.match_data
    
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        st.markdown(f"### 🏠 {data['home_team']}")
    with col2:
        st.markdown("### vs")
    with col3:
        st.markdown(f"### ✈️ {data['away_team']}")
    
    st.markdown(f"**Serie A** • Today • 20:45 CET • Match ID: `#MAT20231216-001`")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Team Analysis Section
    st.markdown('<div class="section-title">Team Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_team_card(data['home_team'], True, {
            'btts': data['home_btts'],
            'over': data['home_over'],
            'under': data['home_under'],
            'gf': data['home_gf'],
            'ga': data['home_ga']
        })
    
    with col2:
        create_team_card(data['away_team'], False, {
            'btts': data['away_btts'],
            'over': data['away_over'],
            'under': data['away_under'],
            'gf': data['away_gf'],
            'ga': data['away_ga']
        })
    
    # Analytical Insights
    st.markdown('<div class="section-title">Analytical Insights</div>', unsafe_allow_html=True)
    
    baseline, expected_goals, adjustments = calculate_expected_goals()
    probabilities = calculate_probabilities(expected_goals)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Expected Goals Model")
        
        # Metrics
        st.metric("Baseline Calculation", f"{baseline:.2f}")
        st.metric("Trend Adjustments", "Applied" if adjustments else "None")
        st.metric("Final Expected Goals", f"{expected_goals:.2f}")
        
        # Interpretation
        if expected_goals < 2.3:
            interpretation = "Low-scoring match expected"
            color = "#10B981"
        elif expected_goals < 2.7:
            interpretation = "Moderate scoring expected"
            color = "#F59E0B"
        else:
            interpretation = "High-scoring match expected"
            color = "#EF4444"
        
        st.info(f"**Interpretation:** {interpretation}")
        
        # Adjustments list
        if adjustments:
            st.markdown("**Adjustments applied:**")
            for adj in adjustments:
                st.markdown(f"- {adj}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Expected goals chart
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=expected_goals,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Expected Goals"},
            delta={'reference': 2.5},
            gauge={
                'axis': {'range': [None, 4]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 2.3], 'color': "lightgreen"},
                    {'range': [2.3, 2.7], 'color': "lightyellow"},
                    {'range': [2.7, 4], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 2.5
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Probability Distribution")
        
        # Probabilities
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Under 2.5", f"{probabilities['under']:.0%}")
        with col2:
            st.metric("Over 2.5", f"{probabilities['over']:.0%}")
        with col3:
            st.metric("BTTS Yes", f"{probabilities['btts']:.0%}")
        
        # Key insight
        if probabilities['under'] > 0.7:
            insight = "Defensive focus expected"
        elif probabilities['under'] > 0.45:
            insight = "Balanced match expected"
        else:
            insight = "Attacking match expected"
        
        st.success(f"**Key Insight:** {insight}")
        
        # Probability chart
        fig = go.Figure(data=[
            go.Bar(
                x=['Under 2.5', 'Over 2.5', 'BTTS Yes'],
                y=[probabilities['under'], probabilities['over'], probabilities['btts']],
                marker_color=['#10B981', '#EF4444', '#3B82F6']
            )
        ])
        fig.update_layout(
            yaxis_title="Probability",
            yaxis_tickformat='.0%',
            height=250,
            margin=dict(t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Betting Recommendations
    st.markdown('<div class="section-title">Betting Recommendations</div>', unsafe_allow_html=True)
    
    # Generate recommendations
    recommendations = []
    
    # Under 2.5 recommendation
    if expected_goals < 2.5:
        value_data = calculate_value(probabilities['under'], data['odds_under'])
        recommendations.append({
            'market': 'Under 2.5 Goals',
            'probability': probabilities['under'],
            'odds': data['odds_under'],
            'value': value_data,
            'type': 'Main'
        })
    
    # BTTS recommendation
    if probabilities['btts'] > 0.5:
        value_data = calculate_value(probabilities['btts'], data['odds_btts'])
        recommendations.append({
            'market': 'Both Teams to Score',
            'probability': probabilities['btts'],
            'odds': data['odds_btts'],
            'value': value_data,
            'type': 'Alternative'
        })
    
    # Display recommendations
    for rec in recommendations:
        create_prediction_card(
            rec['market'],
            rec['probability'],
            rec['odds'],
            rec['value'],
            rec['type']
        )
    
    # Market Odds Analysis
    st.markdown('<div class="section-title">Market Odds Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("BTTS Yes", f"{data['odds_btts']:.2f}", 
                 f"Implied: {(1/data['odds_btts']*100):.1f}%")
    
    with col2:
        st.metric("Over 2.5", f"{data['odds_over']:.2f}", 
                 f"Implied: {(1/data['odds_over']*100):.1f}%")
    
    with col3:
        st.metric("Under 2.5", f"{data['odds_under']:.2f}", 
                 f"Implied: {(1/data['odds_under']*100):.1f}%")
    
    # Risk Assessment
    st.markdown('<div class="section-title">Risk Assessment</div>', unsafe_allow_html=True)
    
    if recommendations:
        best_rec = recommendations[0]
        
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Risk Level**")
            # Progress bar for probability
            prob_percent = best_rec['probability'] * 100
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar progress-{'high' if best_rec['probability'] >= 0.7 else 'medium' if best_rec['probability'] >= 0.6 else 'low'}" 
                     style="width: {prob_percent}%"></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"{best_rec['probability']:.0%} Probability")
        
        with col2:
            st.metric("Expected Value", f"{best_rec['value']['value']:+.3f}", 
                     "per unit bet")
        
        with col3:
            st.metric("Recommended Stake", f"{best_rec['value']['stake']:.1f}%", 
                     "of bankroll")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <div>Betting Analytics Pro • Version 2.0 • Professional Use Only</div>
        <div style="margin-top: 0.5rem;">Always bet responsibly • Past performance does not guarantee future results</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
