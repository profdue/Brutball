"""
BETTING ANALYTICS PRO - WITH CORRECT ALTERNATIVE BETS LOGIC
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
    
    .prediction-low {
        border-left-color: #6B7280;
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    }
    
    /* Badges for bet types */
    .bet-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .badge-secondary {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
    }
    
    .badge-tertiary {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    
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
        'home_btts': 70,  # Changed to test aligned trends
        'home_over': 20,
        'home_under': 70,
        'home_gf': 1.0,
        'home_ga': 0.8,
        'away_btts': 70,  # Changed to test aligned trends
        'away_over': 35,
        'away_under': 60,
        'away_gf': 1.3,
        'away_ga': 0.9,
        'big_club_home': True,
        'odds_btts': 1.80,
        'odds_over': 2.20,
        'odds_under': 1.58
    }

def check_aligned_trends():
    """Check for aligned strong trends (≥70%) - TIER 1"""
    data = st.session_state.match_data
    
    # Check for BTTS aligned trend
    if data['home_btts'] >= 70 and data['away_btts'] >= 70:
        return {
            'type': 'aligned',
            'primary_bet': 'BTTS Yes',
            'probability': 0.75,
            'reason': f"Both teams show ≥70% BTTS trend (Home: {data['home_btts']}%, Away: {data['away_btts']}%)"
        }
    
    # Check for Over aligned trend
    if data['home_over'] >= 70 and data['away_over'] >= 70:
        return {
            'type': 'aligned',
            'primary_bet': 'Over 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Over trend (Home: {data['home_over']}%, Away: {data['away_over']}%)"
        }
    
    # Check for Under aligned trend
    if data['home_under'] >= 70 and data['away_under'] >= 70:
        return {
            'type': 'aligned',
            'primary_bet': 'Under 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Under trend (Home: {data['home_under']}%, Away: {data['away_under']}%)"
        }
    
    return None

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
        adjustments.append(f"Home has {data['home_under']}% Under trend (-15%)")
    
    # Away team adjustments (with context)
    if data['away_under'] >= 70:
        if data['big_club_home']:
            adjustments.append(f"Away trend discounted (facing big club)")
        else:
            adjusted *= 0.85
            adjustments.append(f"Away has {data['away_under']}% Under trend (-15%)")
    
    if data['big_club_home']:
        adjusted -= 0.1
        adjustments.append("Big club at home (-0.1 goals)")
    
    return baseline, adjusted, adjustments

def calculate_secondary_bet_probability(expected_goals, bet_type):
    """Calculate probability for secondary bet (Over/Under 2.5)"""
    # Formula: Probability = 50 + (|Exp Goals - 2.5| × 40)
    # Cap at 85% max, 25% min
    if bet_type == 'Under 2.5':
        diff = 2.5 - expected_goals
    else:  # Over 2.5
        diff = expected_goals - 2.5
    
    probability = 0.5 + (diff * 0.4)
    probability = max(0.25, min(0.85, probability))
    
    return probability

def get_secondary_bet_recommendation(expected_goals):
    """Get secondary bet recommendation based on expected goals"""
    if expected_goals > 2.7:
        return {
            'bet': 'Over 2.5',
            'probability': calculate_secondary_bet_probability(expected_goals, 'Over 2.5'),
            'reason': f'Expected Goals: {expected_goals:.1f} > 2.7 threshold'
        }
    elif expected_goals < 2.3:
        return {
            'bet': 'Under 2.5',
            'probability': calculate_secondary_bet_probability(expected_goals, 'Under 2.5'),
            'reason': f'Expected Goals: {expected_goals:.1f} < 2.3 threshold'
        }
    else:
        return {
            'bet': 'No clear secondary',
            'probability': 0.5,
            'reason': f'Expected Goals: {expected_goals:.1f} in neutral range (2.3-2.7)'
        }

def get_tertiary_bets(expected_goals, btts_probability):
    """Get tertiary bet recommendations (correct scores)"""
    if expected_goals <= 2.0:
        # Low-scoring match
        if btts_probability < 0.4:
            return ["1-0", "0-0", "2-0", "0-1"]
        else:
            return ["1-1", "1-0", "0-1", "2-1"]
    elif expected_goals <= 2.5:
        # Moderate scoring
        if btts_probability < 0.5:
            return ["2-0", "1-0", "2-1", "1-1"]
        else:
            return ["2-1", "1-1", "2-2", "3-1"]
    else:
        # High scoring
        if btts_probability < 0.6:
            return ["3-0", "2-0", "3-1", "2-1"]
        else:
            return ["2-1", "2-2", "3-1", "3-2"]

def calculate_value(probability, odds):
    """Calculate value metrics"""
    value = (probability * odds) - 1
    implied_prob = 1 / odds
    
    # Determine value category
    if value >= 0.25:
        category = "High Value"
        action = "STRONG BET"
        stake = 3.0
        color = "#10B981"
        badge_class = "prediction-high"
    elif value >= 0.15:
        category = "Good Value"
        action = "BET"
        stake = 2.0
        color = "#3B82F6"
        badge_class = "prediction-high"
    elif value >= 0.05:
        category = "Limited Value"
        action = "CONSIDER"
        stake = 1.0
        color = "#F59E0B"
        badge_class = "prediction-medium"
    else:
        category = "No Value"
        action = "AVOID"
        stake = 0.0
        color = "#6B7280"
        badge_class = "prediction-low"
    
    return {
        'value': value,
        'implied_prob': implied_prob,
        'category': category,
        'action': action,
        'stake': stake,
        'color': color,
        'badge_class': badge_class
    }

def create_prediction_card(bet_type, bet_label, probability, odds, value_data, is_primary=False):
    """Create a prediction card"""
    badge_type = "badge-primary" if is_primary else "badge-secondary" if bet_label == "Secondary" else "badge-tertiary"
    
    st.markdown(f"""
    <div class="prediction-card {value_data['badge_class']}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div>
                <span class="bet-badge {badge_type}">{bet_label} Bet</span>
                <h4 style="margin: 0.25rem 0;">{bet_type}</h4>
                <div style="color: #718096; font-size: 0.9rem;">
                    {value_data['category']} • {value_data['action']}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{probability:.0%}</div>
                <div style="font-size: 0.9rem; color: #718096;">Probability</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Market Odds", f"{odds:.2f}")
    with col2:
        st.metric("Value Edge", f"{value_data['value']:+.1%}")
    with col3:
        if value_data['stake'] > 0:
            st.metric("Stake Size", f"{value_data['stake']:.1f}%")
        else:
            st.metric("Stake Size", "No bet")
    
    # Expected Value
    st.markdown(f"**Expected Value:** `{value_data['value']:.3f}` per unit")

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
                st.markdown('<span class="bet-badge badge-primary">Big Club</span>', unsafe_allow_html=True)
        
        # Two columns for stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trend Analysis**")
            
            # Create trend indicators
            for trend_name, trend_value, trend_key in [
                ("BTTS", stats['btts'], 'btts'),
                ("Over 2.5", stats['over'], 'over'),
                ("Under 2.5", stats['under'], 'under')
            ]:
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"{trend_name}")
                with col_b:
                    st.markdown(f"**{trend_value}%**")
                
                # Progress bar
                progress_color = "#10B981" if trend_value >= 70 else "#F59E0B" if trend_value >= 60 else "#EF4444"
                st.markdown(f"""
                <div style="background: #E2E8F0; border-radius: 10px; height: 8px; margin: 0.25rem 0 1rem 0;">
                    <div style="background: {progress_color}; border-radius: 10px; height: 100%; width: {trend_value}%;"></div>
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
            home_btts = st.slider("Home BTTS %", 0, 100, 70)
            home_over = st.slider("Home Over %", 0, 100, 20)
            home_under = st.slider("Home Under %", 0, 100, 70)
            home_gf = st.number_input("Home GF/game", 0.0, 5.0, 1.0, 0.1)
            home_ga = st.number_input("Home GA/game", 0.0, 5.0, 0.8, 0.1)
            
        with col2:
            away_team = st.text_input("Away Team", "Como")
            away_btts = st.slider("Away BTTS %", 0, 100, 70)
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
    
    # Check for aligned trends (TIER 1)
    st.markdown('<div class="section-title">🎯 Betting Recommendations</div>', unsafe_allow_html=True)
    
    aligned_trend = check_aligned_trends()
    baseline, expected_goals, adjustments = calculate_expected_goals()
    
    # Primary Bet (TIER 1) - Check aligned trends first
    if aligned_trend:
        # We have aligned trends - PRIMARY BET FOUND
        st.markdown("### 🥇 PRIMARY BET (Aligned Trends)")
        
        # Get odds for the primary bet
        if aligned_trend['primary_bet'] == 'BTTS Yes':
            odds = data['odds_btts']
        elif aligned_trend['primary_bet'] == 'Over 2.5':
            odds = data['odds_over']
        else:  # Under 2.5
            odds = data['odds_under']
        
        value_data = calculate_value(aligned_trend['probability'], odds)
        create_prediction_card(
            aligned_trend['primary_bet'],
            "Primary",
            aligned_trend['probability'],
            odds,
            value_data,
            is_primary=True
        )
        
        # Secondary Bet (TIER 2) - Based on Expected Goals
        st.markdown("### 🥈 SECONDARY BET (Expected Goals)")
        secondary = get_secondary_bet_recommendation(expected_goals)
        
        if secondary['bet'] != 'No clear secondary':
            # Get odds for secondary bet
            odds = data['odds_over'] if secondary['bet'] == 'Over 2.5' else data['odds_under']
            sec_value_data = calculate_value(secondary['probability'], odds)
            
            create_prediction_card(
                secondary['bet'],
                "Secondary",
                secondary['probability'],
                odds,
                sec_value_data
            )
            
            # Tertiary Bets (TIER 3) - Correct Scores
            st.markdown("### 🥉 TERTIARY BETS (Correct Score)")
            
            # Calculate BTTS probability for tertiary bets
            btts_prob = min(0.6, max(0.1, expected_goals * 0.25))
            if data['home_under'] >= 70:
                btts_prob *= 0.7
            
            tertiary_scores = get_tertiary_bets(expected_goals, btts_prob)
            
            st.markdown(f"""
            <div class="data-card">
                <h4 style="margin: 0 0 1rem 0;">Most Likely Scores</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 1rem;">
            """, unsafe_allow_html=True)
            
            for score in tertiary_scores:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.75rem; background: #F7FAFC; border-radius: 8px;">
                    <div style="font-weight: 600; font-size: 1.1rem;">{score}</div>
                    <div style="font-size: 0.8rem; color: #718096;">Higher probability</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        # NO aligned trends - use Expected Goals for primary
        st.markdown("### 🥇 PRIMARY BET (Expected Goals)")
        
        # Primary bet based on expected goals
        if expected_goals > 2.5:
            primary_bet = 'Over 2.5'
            odds = data['odds_over']
            prob = calculate_secondary_bet_probability(expected_goals, 'Over 2.5')
            reason = f"Expected Goals: {expected_goals:.1f} > 2.5"
        else:
            primary_bet = 'Under 2.5'
            odds = data['odds_under']
            prob = calculate_secondary_bet_probability(expected_goals, 'Under 2.5')
            reason = f"Expected Goals: {expected_goals:.1f} < 2.5"
        
        primary_value_data = calculate_value(prob, odds)
        create_prediction_card(
            primary_bet,
            "Primary",
            prob,
            odds,
            primary_value_data
        )
        
        # Secondary bet would be the opposite market
        st.markdown("### 🥈 SECONDARY BET (Alternative Market)")
        
        if expected_goals > 2.5:
            secondary_bet = 'Under 2.5'
            sec_odds = data['odds_under']
            sec_prob = 1 - prob  # Opposite of primary
        else:
            secondary_bet = 'Over 2.5'
            sec_odds = data['odds_over']
            sec_prob = 1 - prob
        
        # Ensure probability is reasonable
        sec_prob = max(0.2, min(0.8, sec_prob))
        sec_value_data = calculate_value(sec_prob, sec_odds)
        
        # Only show if there's at least limited value
        if sec_value_data['value'] >= 0.05:
            create_prediction_card(
                secondary_bet,
                "Secondary",
                sec_prob,
                sec_odds,
                sec_value_data
            )
        else:
            st.info(f"**{secondary_bet}** has limited value ({sec_value_data['value']:+.1%}) - not recommended")
        
        # Tertiary Bets
        st.markdown("### 🥉 TERTIARY BETS (Correct Score)")
        
        # Calculate BTTS probability
        btts_prob = min(0.6, max(0.1, expected_goals * 0.25))
        if data['home_under'] >= 70:
            btts_prob *= 0.7
        
        tertiary_scores = get_tertiary_bets(expected_goals, btts_prob)
        
        cols = st.columns(len(tertiary_scores))
        for idx, score in enumerate(tertiary_scores):
            with cols[idx]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: #F7FAFC; border-radius: 8px; margin: 0.5rem 0;">
                    <div style="font-weight: 600; font-size: 1.2rem;">{score}</div>
                    <div style="font-size: 0.8rem; color: #718096;">For bet builders</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Analytical Insights
    st.markdown('<div class="section-title">📊 Analytical Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Expected Goals Model")
        
        st.metric("Baseline Calculation", f"{baseline:.2f}")
        st.metric("Trend Adjustments", "Applied" if adjustments else "None")
        st.metric("Final Expected Goals", f"{expected_goals:.2f}")
        
        if expected_goals < 2.3:
            interpretation = "Low-scoring match expected"
        elif expected_goals < 2.7:
            interpretation = "Moderate scoring expected"
        else:
            interpretation = "High-scoring match expected"
        
        st.info(f"**Interpretation:** {interpretation}")
        
        if adjustments:
            st.markdown("**Adjustments applied:**")
            for adj in adjustments:
                st.markdown(f"- {adj}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Market Odds Analysis")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("BTTS Yes", f"{data['odds_btts']:.2f}", 
                     f"Implied: {(1/data['odds_btts']*100):.1f}%")
        with col_b:
            st.metric("Over 2.5", f"{data['odds_over']:.2f}", 
                     f"Implied: {(1/data['odds_over']*100):.1f}%")
        with col_c:
            st.metric("Under 2.5", f"{data['odds_under']:.2f}", 
                     f"Implied: {(1/data['odds_under']*100):.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <div><strong>🎯 Betting Hierarchy:</strong> Primary (Aligned Trends) → Secondary (Expected Goals) → Tertiary (Bet Builders)</div>
        <div style="margin-top: 0.5rem;">Always bet responsibly • Past performance does not guarantee future results</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
