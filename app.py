"""
CLEAN BETTING ANALYTICS DASHBOARD
Professional UI with no raw HTML/CSS in output
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Betting Analytics Pro",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# Custom CSS - INVISIBLE to users
st.markdown("""
<style>
    /* Hidden CSS - users won't see this */
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .primary-bet {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #10B981;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .secondary-bet {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-left: 4px solid #3B82F6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PREDICTION LOGIC
# ============================================================================

def check_aligned_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """Check for aligned strong trends (≥70%)"""
    trends = []
    
    if home_btts >= 70 and away_btts >= 70:
        trends.append(('BTTS Yes', 0.75, f"Both teams ≥70% BTTS (Home: {home_btts}%, Away: {away_btts}%)"))
    if home_over >= 70 and away_over >= 70:
        trends.append(('Over 2.5', 0.70, f"Both teams ≥70% Over (Home: {home_over}%, Away: {away_over}%)"))
    if home_under >= 70 and away_under >= 70:
        trends.append(('Under 2.5', 0.70, f"Both teams ≥70% Under (Home: {home_under}%, Away: {away_under}%)"))
    
    return trends

def calculate_expected_goals(home_gf, away_ga, away_gf, home_ga):
    """Calculate expected goals"""
    return ((home_gf + away_ga) + (away_gf + home_ga)) / 2

def calculate_value(probability, odds):
    """Calculate betting value"""
    value = (probability * odds) - 1
    if value >= 0.25:
        return value, "STRONG BET", 3.0, "🟢 High Value"
    elif value >= 0.15:
        return value, "BET", 2.0, "🟡 Good Value"
    elif value >= 0.05:
        return value, "CONSIDER", 1.0, "🟠 Limited Value"
    else:
        return value, "AVOID", 0.0, "🔴 No Value"

def get_secondary_recommendation(expected_goals):
    """Get secondary recommendation based on expected goals"""
    if expected_goals > 2.7:
        return 'Over 2.5', 0.70, f"Expected Goals: {expected_goals:.1f} > 2.7"
    elif expected_goals < 2.3:
        return 'Under 2.5', 0.70, f"Expected Goals: {expected_goals:.1f} < 2.3"
    else:
        return None, 0.50, f"Expected Goals: {expected_goals:.1f} (neutral)"

# ============================================================================
# CLEAN UI COMPONENTS
# ============================================================================

def display_match_header(home_team, away_team):
    """Display match header using clean Streamlit components"""
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        st.markdown(f"### 🏠 {home_team}")
    with col2:
        st.markdown("### vs")
    with col3:
        st.markdown(f"### ✈️ {away_team}")
    
    st.markdown("---")

def display_team_card(team_name, is_home, stats):
    """Display team card using Streamlit components"""
    with st.container():
        if is_home:
            st.subheader(f"🏠 {team_name}")
        else:
            st.subheader(f"✈️ {team_name}")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("BTTS %", f"{stats['btts']}%")
            st.metric("Over 2.5 %", f"{stats['over']}%")
            st.metric("Under 2.5 %", f"{stats['under']}%")
        
        with col2:
            st.metric("GF/game", f"{stats['gf']:.2f}")
            st.metric("GA/game", f"{stats['ga']:.2f}")
        
        with col3:
            net = stats['gf'] - stats['ga']
            st.metric("Net Rating", f"{net:+.2f}")
            avg_goals = (stats['gf'] + stats['ga']) / 2
            st.metric("Avg Goals", f"{avg_goals:.2f}")
        
        st.markdown("---")

def display_primary_bet(bet_type, probability, odds, reason):
    """Display primary bet recommendation"""
    value, action, stake, category = calculate_value(probability, odds)
    
    st.markdown("### 🥇 PRIMARY BET")
    
    # Create a clean card using columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{bet_type}**")
        st.markdown(f"*{reason}*")
        
        # Metrics in a clean layout
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Probability", f"{probability:.0%}")
        with col_b:
            st.metric("Market Odds", f"{odds:.2f}")
        with col_c:
            st.metric("Value Edge", f"{value:+.1%}")
    
    with col2:
        st.markdown("#### Decision")
        if category == "🟢 High Value":
            st.success(f"{action}")
        elif category == "🟡 Good Value":
            st.info(f"{action}")
        elif category == "🟠 Limited Value":
            st.warning(f"{action}")
        else:
            st.error(f"{action}")
        
        if stake > 0:
            st.metric("Stake", f"{stake:.1f}%")

def display_secondary_option(bet_type, probability, odds, reason):
    """Display secondary option"""
    value, action, stake, category = calculate_value(probability, odds)
    
    st.markdown("### 🥈 SECONDARY OPTION")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{bet_type}**")
        st.markdown(f"*{reason}*")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Probability", f"{probability:.0%}")
        with col_b:
            st.metric("Market Odds", f"{odds:.2f}")
        with col_c:
            if value >= 0:
                st.metric("Value", f"{value:+.1%}")
            else:
                st.metric("Value", f"{value:+.1%}", delta_color="inverse")
    
    with col2:
        st.markdown("#### Action")
        if stake > 0:
            st.info(f"{action} ({stake:.1f}% stake)")
        else:
            st.warning(f"{action}")

def display_market_analysis(data, aligned_trends):
    """Display market analysis"""
    st.markdown("### 💰 MARKET ANALYSIS")
    
    # Calculate true probabilities
    if any(t[0] == 'BTTS Yes' for t in aligned_trends):
        btts_prob = 0.75
    else:
        btts_prob = 0.50
    
    expected_goals = calculate_expected_goals(
        data['home_gf'], data['away_ga'], 
        data['away_gf'], data['home_ga']
    )
    
    if any(t[0] == 'Over 2.5' for t in aligned_trends):
        over_prob = 0.70
    else:
        over_prob = 0.70 if expected_goals > 2.7 else 0.65 if expected_goals > 2.5 else 0.35
    
    under_prob = 1 - over_prob
    
    # Display each market
    markets = [
        ("BTTS Yes", data['odds']['btts'], btts_prob),
        ("Over 2.5", data['odds']['over'], over_prob),
        ("Under 2.5", data['odds']['under'], under_prob)
    ]
    
    for market_name, odds, true_prob in markets:
        implied_prob = 1 / odds
        value = (true_prob * odds) - 1
        
        st.markdown(f"**{market_name}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Implied Probability", f"{implied_prob:.1%}")
        with col2:
            st.metric("True Probability", f"{true_prob:.1%}")
        with col3:
            if value >= 0:
                st.metric("Value Edge", f"{value:+.1%}")
            else:
                st.metric("Value Edge", f"{value:+.1%}", delta_color="inverse")
        
        st.markdown("---")

def display_correct_scores(expected_goals, home_team, away_team):
    """Display correct score suggestions"""
    st.markdown("### 🎯 CORRECT SCORE SUGGESTIONS")
    
    if expected_goals > 3.0:
        scores = [
            f"{home_team} 3-1 {away_team}",
            f"{home_team} 2-2 {away_team}",
            f"{home_team} 3-2 {away_team}",
            f"{home_team} 4-1 {away_team}"
        ]
    elif expected_goals > 2.5:
        scores = [
            f"{home_team} 2-1 {away_team}",
            f"{home_team} 2-2 {away_team}",
            f"{home_team} 3-1 {away_team}",
            f"{away_team} 1-2 {home_team}"
        ]
    else:
        scores = [
            f"{home_team} 1-0 {away_team}",
            f"{home_team} 2-0 {away_team}",
            f"{home_team} 1-1 {away_team}",
            f"{away_team} 0-1 {home_team}"
        ]
    
    cols = st.columns(len(scores))
    for idx, score in enumerate(scores):
        with cols[idx]:
            st.info(f"**{score}**")
            st.caption("For bet builders")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application - CLEAN VERSION"""
    
    # Header
    st.title("🎯 Betting Analytics Pro")
    st.markdown("Professional Football Match Analysis")
    
    # Sidebar for data input
    with st.sidebar:
        st.header("📊 Match Data")
        
        # Home Team
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Home Team Name", "Fenerbahce")
        home_btts = st.slider("Home BTTS %", 0, 100, 70)
        home_over = st.slider("Home Over 2.5 %", 0, 100, 50)
        home_under = st.slider("Home Under 2.5 %", 0, 100, 50)
        home_gf = st.number_input("Home GF/game", 0.0, 5.0, 1.90, 0.01)
        home_ga = st.number_input("Home GA/game", 0.0, 5.0, 0.90, 0.01)
        
        # Away Team
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Away Team Name", "Konyaspor")
        away_btts = st.slider("Away BTTS %", 0, 100, 80)
        away_over = st.slider("Away Over 2.5 %", 0, 100, 60)
        away_under = st.slider("Away Under 2.5 %", 0, 100, 40)
        away_gf = st.number_input("Away GF/game", 0.0, 5.0, 1.40, 0.01)
        away_ga = st.number_input("Away GA/game", 0.0, 5.0, 1.70, 0.01)
        
        # Market Odds
        st.subheader("💰 Market Odds")
        odds_btts = st.number_input("BTTS Yes", 1.01, 10.0, 2.02, 0.01)
        odds_over = st.number_input("Over 2.5", 1.01, 10.0, 1.46, 0.01)
        odds_under = st.number_input("Under 2.5", 1.01, 10.0, 2.48, 0.01)
        
        if st.button("🎯 Analyze Match", type="primary", use_container_width=True):
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
    
    # Check if we have data
    if not st.session_state.match_data:
        st.info("👈 Enter match data in the sidebar and click 'Analyze Match'")
        return
    
    data = st.session_state.match_data
    
    # Display match header
    display_match_header(data['home_team'], data['away_team'])
    
    # Team Analysis
    st.header("📊 Team Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_team_card(data['home_team'], True, {
            'btts': data['home_btts'],
            'over': data['home_over'],
            'under': data['home_under'],
            'gf': data['home_gf'],
            'ga': data['home_ga']
        })
    
    with col2:
        display_team_card(data['away_team'], False, {
            'btts': data['away_btts'],
            'over': data['away_over'],
            'under': data['away_under'],
            'gf': data['away_gf'],
            'ga': data['away_ga']
        })
    
    # Check for aligned trends
    aligned_trends = check_aligned_trends(
        data['home_btts'], data['home_over'], data['home_under'],
        data['away_btts'], data['away_over'], data['away_under']
    )
    
    # Expected Goals
    expected_goals = calculate_expected_goals(
        data['home_gf'], data['away_ga'], 
        data['away_gf'], data['home_ga']
    )
    
    st.header("📈 Expected Goals")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Expected Goals", f"{expected_goals:.2f}")
    with col2:
        if expected_goals > 2.5:
            st.success("Over 2.5 expected")
        else:
            st.info("Under 2.5 expected")
    
    # Primary Bet
    if aligned_trends:
        # Use the first aligned trend as primary
        for bet_type, probability, reason in aligned_trends:
            if bet_type == 'BTTS Yes':
                odds = data['odds']['btts']
            elif bet_type == 'Over 2.5':
                odds = data['odds']['over']
            else:  # Under 2.5
                odds = data['odds']['under']
            
            display_primary_bet(bet_type, probability, odds, reason)
            break  # Only show first aligned trend as primary
    
    # Secondary Option
    sec_bet, sec_prob, sec_reason = get_secondary_recommendation(expected_goals)
    
    if sec_bet:
        if sec_bet == 'Over 2.5':
            sec_odds = data['odds']['over']
        else:  # Under 2.5
            sec_odds = data['odds']['under']
        
        display_secondary_option(sec_bet, sec_prob, sec_odds, sec_reason)
    
    # Correct Score Suggestions
    display_correct_scores(expected_goals, data['home_team'], data['away_team'])
    
    # Market Analysis
    display_market_analysis(data, aligned_trends)
    
    # System Info
    with st.expander("ℹ️ System Information", expanded=False):
        st.markdown("""
        ### 🎯 Betting System Logic
        
        **Primary Bets (Aligned Trends):**
        - Both teams ≥70% same trend → 75% probability
        - Bet if value ≥ 15%
        
        **Secondary Options:**
        - Based on Expected Goals
        - Over 2.5 if > 2.7 expected goals
        - Under 2.5 if < 2.3 expected goals
        
        **Value Calculation:**
        - Formula: Value = (Probability × Odds) - 1
        - Minimum value: 15%
        - Stake: 1-3% based on value
        
        **Expected Goals Formula:**
        - [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2
        """)
    
    # Footer
    st.markdown("---")
    st.caption("Betting Analytics Pro • Always bet responsibly")

if __name__ == "__main__":
    main()
