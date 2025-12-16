"""
COMPLETE BETTING SYSTEM - WITH SECONDARY OPTIONS EVEN FOR ALIGNED TRENDS
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Complete Betting System",
    page_icon="🎯",
    layout="wide"
)

# CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
    .prediction-low {
        border-left-color: #6B7280;
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    }
    .secondary-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #E2E8F0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# ============================================================================
# ENHANCED PREDICTION LOGIC WITH SECONDARY OPTIONS
# ============================================================================

def check_aligned_strong_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """TIER 1: ALIGNED STRONG TRENDS (≥70%) - RETURN ALL OPTIONS"""
    aligned_trends = []
    
    # Check for BTTS aligned trend
    if home_btts >= 70 and away_btts >= 70:
        aligned_trends.append({
            'type': 'BTTS Yes',
            'probability': 0.75,
            'reason': f"Both teams show ≥70% BTTS trend (Home: {home_btts}%, Away: {away_btts}%)"
        })
    
    # Check for Over aligned trend
    if home_over >= 70 and away_over >= 70:
        aligned_trends.append({
            'type': 'Over 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Over trend (Home: {home_over}%, Away: {away_over}%)"
        })
    
    # Check for Under aligned trend
    if home_under >= 70 and away_under >= 70:
        aligned_trends.append({
            'type': 'Under 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Under trend (Home: {home_under}%, Away: {away_under}%)"
        })
    
    return aligned_trends

def calculate_expected_goals(home_gf, away_ga, away_gf, home_ga, aligned_trends=None):
    """Calculate expected goals with trend adjustments"""
    baseline = ((home_gf + away_ga) + (away_gf + home_ga)) / 2
    
    # Apply adjustments for aligned trends
    if aligned_trends:
        for trend in aligned_trends:
            if trend['type'] == 'Over 2.5':
                baseline *= 1.30  # +30% for aligned Over trends
            elif trend['type'] == 'Under 2.5':
                baseline *= 0.70  # -30% for aligned Under trends
    
    return baseline

def get_secondary_options(expected_goals, primary_bet, aligned_trends):
    """Get secondary betting options even when aligned trends are found"""
    secondary_options = []
    
    # Secondary: Over/Under based on expected goals (if not primary)
    if primary_bet != 'Over 2.5' and primary_bet != 'Under 2.5':
        if expected_goals > 2.7:
            sec_prob = 0.70
            sec_reason = f"Expected Goals: {expected_goals:.1f} > 2.7"
            secondary_options.append({
                'type': 'Secondary',
                'bet': 'Over 2.5',
                'probability': sec_prob,
                'reason': sec_reason
            })
        elif expected_goals < 2.3:
            sec_prob = 0.70
            sec_reason = f"Expected Goals: {expected_goals:.1f} < 2.3"
            secondary_options.append({
                'type': 'Secondary',
                'bet': 'Under 2.5',
                'probability': sec_prob,
                'reason': sec_reason
            })
    
    # Alternative: If primary is Over/Under, suggest BTTS as secondary
    if primary_bet in ['Over 2.5', 'Under 2.5']:
        btts_prob = 0.40 if expected_goals < 2.5 else 0.55
        secondary_options.append({
            'type': 'Secondary',
            'bet': 'BTTS Yes',
            'probability': btts_prob,
            'reason': f"Complementary to {primary_bet}"
        })
    
    return secondary_options

def get_tertiary_options(expected_goals, primary_bet, home_team, away_team):
    """Get tertiary options (correct scores)"""
    if expected_goals > 3.0:
        scores = [f"{home_team} 3-1 {away_team}", f"{home_team} 2-2 {away_team}", 
                  f"{home_team} 3-2 {away_team}", f"{home_team} 4-1 {away_team}"]
    elif expected_goals > 2.5:
        scores = [f"{home_team} 2-1 {away_team}", f"{home_team} 2-2 {away_team}",
                  f"{home_team} 3-1 {away_team}", f"{away_team} 1-2 {home_team}"]
    else:
        scores = [f"{home_team} 1-0 {away_team}", f"{home_team} 2-0 {away_team}",
                  f"{home_team} 1-1 {away_team}", f"{away_team} 0-1 {home_team}"]
    
    return scores

def calculate_value(probability, odds):
    """Calculate value: Value = (Probability × Odds) - 1"""
    value = (probability * odds) - 1
    
    if value >= 0.25:
        return {'value': value, 'category': 'High Value', 'stake': 3.0, 'action': 'STRONG BET'}
    elif value >= 0.15:
        return {'value': value, 'category': 'Good Value', 'stake': 2.0, 'action': 'BET'}
    elif value >= 0.05:
        return {'value': value, 'category': 'Limited Value', 'stake': 1.0, 'action': 'CONSIDER'}
    else:
        return {'value': value, 'category': 'No Value', 'stake': 0.0, 'action': 'AVOID'}

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    st.markdown('<div class="header">🎯 COMPLETE BETTING SYSTEM</div>', unsafe_allow_html=True)
    st.markdown("**All prediction logic with secondary options**")
    
    # Sidebar for data input
    with st.sidebar:
        st.header("📊 Match Data Input")
        
        # Basic info
        league = st.selectbox("League", ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "Other"])
        match_date = st.date_input("Match Date", datetime.now())
        
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Fenerbahce")
        
        col1, col2 = st.columns(2)
        with col1:
            home_btts = st.slider("BTTS % (Last 10)", 0, 100, 70)
            home_over = st.slider("Over 2.5 %", 0, 100, 50)
            home_under = st.slider("Under 2.5 %", 0, 100, 50)
        with col2:
            home_gf = st.number_input("GF/game", 0.0, 5.0, 1.90, 0.01)
            home_ga = st.number_input("GA/game", 0.0, 5.0, 0.90, 0.01)
        
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Team Name ", "Konyaspor")
        
        col1, col2 = st.columns(2)
        with col1:
            away_btts = st.slider("BTTS % (Last 10) ", 0, 100, 80)
            away_over = st.slider("Over 2.5 % ", 0, 100, 60)
            away_under = st.slider("Under 2.5 % ", 0, 100, 40)
        with col2:
            away_gf = st.number_input("GF/game ", 0.0, 5.0, 1.40, 0.01)
            away_ga = st.number_input("GA/game ", 0.0, 5.0, 1.70, 0.01)
        
        st.subheader("💰 Market Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            odds_btts = st.number_input("BTTS Yes", 1.01, 10.0, 2.02, 0.01)
        with col2:
            odds_over = st.number_input("Over 2.5", 1.01, 10.0, 1.46, 0.01)
        with col3:
            odds_under = st.number_input("Under 2.5", 1.01, 10.0, 2.48, 0.01)
        
        if st.button("🎯 Run Complete Analysis", type="primary", use_container_width=True):
            st.session_state.match_data = {
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
                'odds': {
                    'btts': odds_btts,
                    'over': odds_over,
                    'under': odds_under
                }
            }
            st.rerun()
    
    # Check if we have data to analyze
    if not st.session_state.match_data:
        st.info("👈 Enter match data in the sidebar and click 'Run Complete Analysis'")
        return
    
    data = st.session_state.match_data
    
    # Match header
    st.markdown(f"""
    <div class="card">
        <div style="text-align: center;">
            <h2 style="margin: 0;">🏠 {data['home_team']} vs ✈️ {data['away_team']}</h2>
            <div style="color: #718096; margin-top: 0.5rem;">Complete Analysis with Secondary Options</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for aligned trends
    aligned_trends = check_aligned_strong_trends(
        data['home_btts'], data['home_over'], data['home_under'],
        data['away_btts'], data['away_over'], data['away_under']
    )
    
    # Calculate expected goals
    expected_goals = calculate_expected_goals(
        data['home_gf'], data['away_ga'], data['away_gf'], data['home_ga'],
        aligned_trends
    )
    
    # Display primary predictions
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🎯 PRIMARY BETS (Aligned Trends)</div>', unsafe_allow_html=True)
    
    if aligned_trends:
        for trend in aligned_trends:
            # Get odds for this bet
            if trend['type'] == 'Over 2.5':
                odds = data['odds']['over']
            elif trend['type'] == 'Under 2.5':
                odds = data['odds']['under']
            else:  # BTTS Yes
                odds = data['odds']['btts']
            
            value_data = calculate_value(trend['probability'], odds)
            
            # Display primary bet
            card_class = "prediction-high" if value_data['value'] >= 0.15 else "prediction-medium"
            
            st.markdown(f"""
            <div class="prediction-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0 0 0.5rem 0;">{trend['type']}</h3>
                        <div style="color: #718096; font-size: 0.9rem;">
                            ALIGNED TREND • {trend['reason']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{trend['probability']:.0%}</div>
                        <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Odds", f"{odds:.2f}")
            with col2:
                st.metric("Value Edge", f"{value_data['value']:+.1%}")
            with col3:
                if value_data['stake'] > 0:
                    st.metric("Stake", f"{value_data['stake']:.1f}%")
                else:
                    st.metric("Stake", "No bet")
            
            st.markdown(f"**Decision:** {value_data['action']} ({value_data['category']})")
            
            # Store primary bet for secondary options
            primary_bet = trend['type']
    else:
        st.info("No aligned strong trends detected")
        primary_bet = None
    
    # Display Expected Goals
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">📊 Expected Goals Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        baseline = ((data['home_gf'] + data['away_ga']) + (data['away_gf'] + data['home_ga'])) / 2
        st.metric("Baseline Goals", f"{baseline:.2f}")
    with col2:
        st.metric("Adjusted Goals", f"{expected_goals:.2f}")
    with col3:
        if expected_goals > 2.5:
            st.metric("Recommendation", "Over 2.5", "Based on expected goals")
        else:
            st.metric("Recommendation", "Under 2.5", "Based on expected goals")
    
    # Secondary Options - ALWAYS SHOW THESE
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🔄 SECONDARY OPTIONS</div>', unsafe_allow_html=True)
    
    if primary_bet:
        secondary_options = get_secondary_options(expected_goals, primary_bet, aligned_trends)
        
        if secondary_options:
            for option in secondary_options:
                # Get odds for secondary bet
                if option['bet'] == 'Over 2.5':
                    odds = data['odds']['over']
                elif option['bet'] == 'Under 2.5':
                    odds = data['odds']['under']
                else:  # BTTS Yes
                    odds = data['odds']['btts']
                
                value_data = calculate_value(option['probability'], odds)
                
                st.markdown(f"""
                <div class="secondary-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <div>
                            <h4 style="margin: 0 0 0.5rem 0;">{option['bet']}</h4>
                            <div style="color: #718096; font-size: 0.9rem;">
                                SECONDARY OPTION • {option['reason']}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: 700; color: #2D3748;">{option['probability']:.0%}</div>
                            <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div>
                            <div style="font-size: 0.9rem; color: #718096;">Market Odds</div>
                            <div style="font-weight: 600;">{odds:.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #718096;">Value</div>
                            <div style="font-weight: 600; color: {'#10B981' if value_data['value'] >= 0 else '#EF4444'}">
                                {value_data['value']:+.1%}
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #718096;">Action</div>
                            <div style="font-weight: 600;">{value_data['action']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No suitable secondary options for this match configuration")
    else:
        st.info("No primary bet identified for secondary options")
    
    # Tertiary Options (Correct Scores)
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🎰 TERTIARY OPTIONS (Correct Score)</div>', unsafe_allow_html=True)
    
    tertiary_scores = get_tertiary_options(expected_goals, primary_bet, data['home_team'], data['away_team'])
    
    cols = st.columns(len(tertiary_scores))
    for idx, score in enumerate(tertiary_scores):
        with cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #F7FAFC; border-radius: 8px; margin: 0.5rem 0;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #2D3748;">{score}</div>
                <div style="font-size: 0.8rem; color: #718096; margin-top: 0.5rem;">For bet builders</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Market Analysis
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">💰 MARKET ODDS ANALYSIS</div>', unsafe_allow_html=True)
    
    # Calculate probabilities for all markets
    if aligned_trends and any(t['type'] == 'BTTS Yes' for t in aligned_trends):
        btts_prob = 0.75
    else:
        btts_prob = 0.50
    
    if aligned_trends and any(t['type'] == 'Over 2.5' for t in aligned_trends):
        over_prob = 0.70
    else:
        over_prob = 0.65 if expected_goals > 2.5 else 0.35
    
    under_prob = 1 - over_prob
    
    # Display market comparison
    markets = [
        ("BTTS Yes", data['odds']['btts'], btts_prob),
        ("Over 2.5", data['odds']['over'], over_prob),
        ("Under 2.5", data['odds']['under'], under_prob)
    ]
    
    for market_name, odds, true_prob in markets:
        implied_prob = 1 / odds
        value = (true_prob * odds) - 1
        
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="font-weight: 600; font-size: 1.1rem;">{market_name}</div>
                <div style="font-size: 1.2rem; font-weight: 700;">{odds:.2f}</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Implied Probability</div>
                    <div style="font-weight: 600;">{implied_prob:.1%}</div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">True Probability</div>
                    <div style="font-weight: 600;">{true_prob:.1%}</div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Value Edge</div>
                    <div style="font-weight: 600; color: {'#10B981' if value >= 0 else '#EF4444'}">
                        {value:+.1%}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # System Logic Summary
    with st.expander("📋 System Logic Summary", expanded=True):
        st.markdown(f"""
        ### 🎯 SYSTEM DECISION PATH
        
        **1. Checked for aligned ≥70% trends:**
        - Fenerbahce: {data['home_btts']}% BTTS {'✓ ≥70%' if data['home_btts'] >= 70 else '✗ <70%'}
        - Konyaspor: {data['away_btts']}% BTTS {'✓ ≥70%' if data['away_btts'] >= 70 else '✗ <70%'}
        - **Result:** {'ALIGNED BTTS TREND FOUND' if data['home_btts'] >= 70 and data['away_btts'] >= 70 else 'No aligned trends'}
        
        **2. Calculated Expected Goals:**
        - Formula: [({data['home_gf']} + {data['away_ga']}) + ({data['away_gf']} + {data['home_ga']})] ÷ 2
        - Result: {expected_goals:.2f} expected goals
        - **Interpretation:** {'High-scoring' if expected_goals > 2.7 else 'Moderate' if expected_goals > 2.3 else 'Low-scoring'} match expected
        
        **3. Generated secondary options:**
        - Primary: {primary_bet if primary_bet else 'None'}
        - Secondary: {' and '.join([opt['bet'] for opt in secondary_options]) if 'secondary_options' in locals() and secondary_options else 'None'}
        - Tertiary: Correct score options shown
        
        **4. Value calculation applied to ALL options**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <div><strong>🎯 COMPLETE SYSTEM:</strong> Primary bets + Secondary options + Tertiary bets</div>
        <div style="margin-top: 0.5rem;">Always shows secondary options even when aligned trends are found</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
