"""
COMPLETE BETTING SYSTEM - WITH ONE STRONG SECONDARY OPTION
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
    .secondary-card {
        border-left-color: #3B82F6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# ============================================================================
# ENHANCED PREDICTION LOGIC WITH ONE SECONDARY OPTION
# ============================================================================

def check_aligned_strong_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """TIER 1: ALIGNED STRONG TRENDS (≥70%)"""
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

def get_best_secondary_option(primary_bet, expected_goals, home_gf, away_gf, home_ga, away_ga):
    """Get ONE strong secondary option based on primary bet and stats"""
    
    # Calculate goal differentials
    home_offense = home_gf + away_ga  # Home attacking strength
    away_offense = away_gf + home_ga  # Away attacking strength
    total_offense = home_offense + away_offense
    
    # RULE 1: If primary is BTTS, secondary is based on expected goals
    if primary_bet == 'BTTS Yes':
        if expected_goals > 2.8:
            return {
                'bet': 'Over 2.5',
                'probability': 0.65,
                'reason': f"BTTS + High expected goals ({expected_goals:.1f}) suggests Over"
            }
        elif expected_goals < 2.2:
            return {
                'bet': 'Under 2.5',
                'probability': 0.60,
                'reason': f"BTTS but low expected goals ({expected_goals:.1f})"
            }
        else:
            # Moderate expected goals - look at team scoring patterns
            if home_gf > 1.8 and away_gf > 1.2:
                return {
                    'bet': 'Over 2.5',
                    'probability': 0.60,
                    'reason': f"Both teams good scoring form (Home: {home_gf:.1f}, Away: {away_gf:.1f} GF/game)"
                }
            else:
                return {
                    'bet': 'Under 2.5',
                    'probability': 0.58,
                    'reason': f"BTTS likely but limited total goals"
                }
    
    # RULE 2: If primary is Over 2.5
    elif primary_bet == 'Over 2.5':
        if total_offense > 6.0:
            return {
                'bet': 'BTTS Yes',
                'probability': 0.68,
                'reason': f"High offensive power ({total_offense:.1f} total attack rating)"
            }
        elif home_gf > 1.5 and away_gf > 1.5:
            return {
                'bet': 'BTTS Yes',
                'probability': 0.65,
                'reason': f"Both teams score regularly (Home: {home_gf:.1f}, Away: {away_gf:.1f} GF/game)"
            }
        else:
            # Look for alternative Over market
            if expected_goals > 3.2:
                return {
                    'bet': 'Over 3.5',
                    'probability': 0.55,
                    'reason': f"Very high expected goals ({expected_goals:.1f})"
                }
            else:
                return {
                    'bet': 'Home Win & Over 2.5',
                    'probability': 0.52,
                    'reason': f"Home offensive advantage ({home_gf:.1f} GF vs {away_ga:.1f} GA)"
                }
    
    # RULE 3: If primary is Under 2.5
    elif primary_bet == 'Under 2.5':
        if home_ga < 1.0 and away_ga < 1.0:
            return {
                'bet': 'BTTS No',
                'probability': 0.70,
                'reason': f"Both teams strong defense (Home: {home_ga:.1f}, Away: {away_ga:.1f} GA/game)"
            }
        elif expected_goals < 1.8:
            return {
                'bet': 'Under 1.5',
                'probability': 0.55,
                'reason': f"Very low expected goals ({expected_goals:.1f})"
            }
        else:
            return {
                'bet': 'Draw',
                'probability': 0.48,
                'reason': f"Low scoring matches often end level"
            }
    
    # Default fallback
    return {
        'bet': 'No strong secondary',
        'probability': 0.0,
        'reason': 'Insufficient data for secondary recommendation'
    }

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
    st.markdown("**Primary prediction + ONE strong secondary option**")
    
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
        
        # Additional odds for secondary markets
        st.subheader("🔄 Secondary Odds")
        odds_btts_no = st.number_input("BTTS No", 1.01, 10.0, 1.72, 0.01)
        odds_over_35 = st.number_input("Over 3.5", 1.01, 10.0, 2.30, 0.01)
        odds_under_15 = st.number_input("Under 1.5", 1.01, 10.0, 3.50, 0.01)
        
        if st.button("🎯 Run Analysis", type="primary", use_container_width=True):
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
                    'btts_yes': odds_btts,
                    'btts_no': odds_btts_no,
                    'over_25': odds_over,
                    'over_35': odds_over_35,
                    'under_25': odds_under,
                    'under_15': odds_under_15
                }
            }
            st.rerun()
    
    # Check if we have data to analyze
    if not st.session_state.match_data:
        st.info("👈 Enter match data in the sidebar and click 'Run Analysis'")
        return
    
    data = st.session_state.match_data
    
    # Match header
    st.markdown(f"""
    <div class="card">
        <div style="text-align: center;">
            <h2 style="margin: 0;">🏠 {data['home_team']} vs ✈️ {data['away_team']}</h2>
            <div style="color: #718096; margin-top: 0.5rem;">Primary Bet + ONE Strong Secondary</div>
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
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🎯 PRIMARY BET (Aligned Trend)</div>', unsafe_allow_html=True)
    
    if aligned_trends:
        # Take the strongest aligned trend
        primary_trend = aligned_trends[0]  # First one is typically strongest
        
        # Get odds for this bet
        if primary_trend['type'] == 'Over 2.5':
            odds = data['odds']['over_25']
        elif primary_trend['type'] == 'Under 2.5':
            odds = data['odds']['under_25']
        else:  # BTTS Yes
            odds = data['odds']['btts_yes']
        
        value_data = calculate_value(primary_trend['probability'], odds)
        
        # Display primary bet
        st.markdown(f"""
        <div class="prediction-card prediction-high">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0 0 0.5rem 0;">{primary_trend['type']}</h3>
                    <div style="color: #718096; font-size: 0.9rem;">
                        🏆 ALIGNED TREND • {primary_trend['reason']}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{primary_trend['probability']:.0%}</div>
                    <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Market Odds</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{odds:.2f}</div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Value Edge</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {'#10B981' if value_data['value'] >= 0 else '#EF4444'}">
                        {value_data['value']:+.1%}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Action</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{value_data['action']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Store primary bet for secondary option
        primary_bet = primary_trend['type']
        
    else:
        st.warning("⚠️ No aligned strong trends detected - consider different match")
        primary_bet = None
        return
    
    # Get ONE strong secondary option
    secondary_option = get_best_secondary_option(
        primary_bet, expected_goals,
        data['home_gf'], data['away_gf'],
        data['home_ga'], data['away_ga']
    )
    
    # Display secondary option
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🔄 ONE STRONG SECONDARY OPTION</div>', unsafe_allow_html=True)
    
    if secondary_option['probability'] > 0:
        # Get odds for secondary bet
        secondary_bet = secondary_option['bet']
        if secondary_bet == 'BTTS Yes':
            odds = data['odds']['btts_yes']
        elif secondary_bet == 'BTTS No':
            odds = data['odds']['btts_no']
        elif secondary_bet == 'Over 2.5':
            odds = data['odds']['over_25']
        elif secondary_bet == 'Over 3.5':
            odds = data['odds']['over_35']
        elif secondary_bet == 'Under 2.5':
            odds = data['odds']['under_25']
        elif secondary_bet == 'Under 1.5':
            odds = data['odds']['under_15']
        else:
            odds = 2.50  # Default
        
        sec_value_data = calculate_value(secondary_option['probability'], odds)
        
        st.markdown(f"""
        <div class="prediction-card secondary-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0 0 0.5rem 0;">{secondary_option['bet']}</h3>
                    <div style="color: #718096; font-size: 0.9rem;">
                        🔄 STRONG SECONDARY • {secondary_option['reason']}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{secondary_option['probability']:.0%}</div>
                    <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Market Odds</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{odds:.2f}</div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Value Edge</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {'#10B981' if sec_value_data['value'] >= 0 else '#EF4444'}">
                        {sec_value_data['value']:+.1%}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Action</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{sec_value_data['action']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No strong secondary option available for this configuration")
    
    # Expected Goals & Analysis
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">📊 KEY METRICS</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Expected Goals", f"{expected_goals:.2f}", 
                  "Higher = More goals expected")
    with col2:
        total_offense = (data['home_gf'] + data['away_ga']) + (data['away_gf'] + data['home_ga'])
        st.metric("Total Attack Rating", f"{total_offense:.1f}",
                  "Sum of offensive strengths")
    with col3:
        match_rating = min(100, (expected_goals * 20) + (len(aligned_trends) * 20))
        st.metric("Match Confidence", f"{match_rating:.0f}%",
                  "Based on trends & stats")
    
    # Strategy Summary
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">📋 BETTING STRATEGY</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card">
        <h4>🎯 RECOMMENDED APPROACH</h4>
        
        **Primary Bet:**
        - <strong>{primary_bet}</strong> at odds {odds:.2f}
        - Stake: <strong>{value_data['stake']:.1f}%</strong> of bankroll
        - Reason: {primary_trend['reason']}
        
        **Secondary Option:**
        - <strong>{secondary_option['bet']}</strong> at odds {odds if 'odds' in locals() else 'N/A':.2f}
        - Stake: <strong>{sec_value_data['stake'] if secondary_option['probability'] > 0 else 0:.1f}%</strong> of bankroll
        - Reason: {secondary_option['reason']}
        
        **Bankroll Management:**
        - Maximum total stake: 5% of bankroll
        - Split: {value_data['stake']:.1f}% primary, {sec_value_data['stake'] if secondary_option['probability'] > 0 else 0:.1f}% secondary
        - Expected value: {(value_data['value'] + sec_value_data['value']) / 2:+.1%} average
    </div>
    """, unsafe_allow_html=True)
    
    # Logic Explanation
    with st.expander("🧠 SYSTEM LOGIC EXPLAINED", expanded=False):
        st.markdown(f"""
        ### How the system works:
        
        1. **Check for aligned trends (≥70%):**
           - Fenerbahce BTTS: {data['home_btts']}% {'✓' if data['home_btts'] >= 70 else '✗'}
           - Konyaspor BTTS: {data['away_btts']}% {'✓' if data['away_btts'] >= 70 else '✗'}
           - Result: **{primary_bet}** selected as primary
        
        2. **Calculate expected goals:**
           - Formula: (Home GF + Away GA) + (Away GF + Home GA) ÷ 2
           - ({data['home_gf']} + {data['away_ga']}) + ({data['away_gf']} + {data['home_ga']}) ÷ 2
           - Result: **{expected_goals:.2f}** expected goals
        
        3. **Select ONE secondary option:**
           - Primary is: {primary_bet}
           - Based on: Expected goals + Team scoring patterns
           - Selected: **{secondary_option['bet']}**
           - Reason: {secondary_option['reason']}
        
        4. **Value calculation for both bets**
        
        **Key Principle:** When aligned trends exist, they're the strongest signal. 
        The secondary option complements the primary bet based on goal expectations.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <div><strong>🎯 SIMPLIFIED SYSTEM:</strong> One primary bet + One strong secondary option</div>
        <div style="margin-top: 0.5rem;">Clean, focused betting recommendations</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
