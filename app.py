"""
COMPLETE CONCRETE BETTING SYSTEM - FIXED LOGIC (SINGLE TRENDS ADDED)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Complete Betting System",
    page_icon="🎯",
    layout="wide"
)

# CSS for professional styling - MOBILE OPTIMIZED
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .header {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .prediction-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        border-left: 5px solid;
        margin-bottom: 1rem;
    }
    .prediction-high {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border: 1px solid #10B98120;
    }
    .prediction-medium {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #F59E0B20;
    }
    .secondary-card {
        border-left-color: #3B82F6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #3B82F620;
    }
    .no-value-card {
        border-left-color: #6B7280;
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        border: 1px solid #6B728020;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .card, .prediction-card {
            padding: 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h2 {
            font-size: 1.4rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
        .header {
            font-size: 1.6rem !important;
        }
    }
    
    /* Ensure text is always visible */
    .prediction-card h3 {
        color: #1F2937 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .prediction-card div {
        color: #4B5563 !important;
    }
    .card h4 {
        color: #1F2937 !important;
        margin: 0 0 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# ============================================================================
# FIXED LOGIC IMPLEMENTATION - SINGLE TRENDS ADDED
# ============================================================================

def check_aligned_70_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """STEP 1: CHECK FOR ≥70% ALIGNED TRENDS - EXACT LOGIC"""
    aligned_trends = []
    
    # Check for BTTS aligned trend
    if home_btts >= 70 and away_btts >= 70:
        aligned_trends.append({
            'type': 'BTTS Yes',
            'probability': 0.75,  # Fixed 75% for aligned trends
            'min_odds': 1.43,     # Minimum odds >1.43
            'reason': f"ALIGNED ≥70% TREND: Both teams show ≥70% BTTS (Home: {home_btts}%, Away: {away_btts}%)",
            'category': 'PRIMARY'
        })
    
    # Check for Over aligned trend
    if home_over >= 70 and away_over >= 70:
        aligned_trends.append({
            'type': 'Over 2.5',
            'probability': 0.75,  # Fixed 75% for aligned trends
            'min_odds': 1.43,     # Minimum odds >1.43
            'reason': f"ALIGNED ≥70% TREND: Both teams show ≥70% Over 2.5 (Home: {home_over}%, Away: {away_over}%)",
            'category': 'PRIMARY'
        })
    
    # Check for Under aligned trend
    if home_under >= 70 and away_under >= 70:
        aligned_trends.append({
            'type': 'Under 2.5',
            'probability': 0.75,  # Fixed 75% for aligned trends
            'min_odds': 1.43,     # Minimum odds >1.43
            'reason': f"ALIGNED ≥70% TREND: Both teams show ≥70% Under 2.5 (Home: {home_under}%, Away: {away_under}%)",
            'category': 'PRIMARY'
        })
    
    return aligned_trends

def check_single_70_trends_and_get_primary(home_btts, home_over, home_under, away_btts, away_over, away_under, 
                                         home_gf, home_ga, away_gf, away_ga, context_flags):
    """🚨 NEW FIXED FUNCTION: Check for SINGLE ≥70% trends and get primary bet"""
    primary_bets = []
    
    # ============================================================================
    # FIXED LOGIC: SINGLE ≥70% TRENDS CAN BE PRIMARY BETS
    # ============================================================================
    
    # Pattern 1: Defensive Specialist (Away team ≥70% Under AND GF ≤ 1.00)
    if away_under >= 70 and away_gf <= 1.00:
        primary_bets.append({
            'type': 'Under 2.5',
            'probability': 0.70,
            'min_odds': 1.43,
            'reason': f"DEFENSIVE SPECIALIST: Away team shows ≥70% Under trend (Away: {away_under}%) with poor attack ({away_gf:.1f} GF/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Defensive Specialist'
        })
    
    # Pattern 2: Home Bounce-Back (Big club at home after poor home form)
    if context_flags.get('big_club_home') and home_gf < 1.5:
        primary_bets.append({
            'type': 'Under 2.5',
            'probability': 0.65,
            'min_odds': 1.50,
            'reason': f"HOME BOUNCE-BACK: Big club at home with low scoring form ({home_gf:.1f} GF/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Home Bounce-Back'
        })
    
    # Pattern 3: Strong Single BTTS Trend (One team ≥70% BTTS with complementary stats)
    if home_btts >= 70 and away_ga >= 1.5:  # Home scores often, away concedes often
        primary_bets.append({
            'type': 'BTTS Yes',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE BTTS TREND: Home shows ≥70% BTTS ({home_btts}%) vs away team that concedes ({away_ga:.1f} GA/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single BTTS Trend'
        })
    
    if away_btts >= 70 and home_ga >= 1.5:  # Away scores often, home concedes often
        primary_bets.append({
            'type': 'BTTS Yes',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE BTTS TREND: Away shows ≥70% BTTS ({away_btts}%) vs home team that concedes ({home_ga:.1f} GA/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single BTTS Trend'
        })
    
    # Pattern 4: Single Over Trend with complementary stats
    if home_over >= 70 and away_ga >= 1.8:  # Home scores over often, away concedes heavily
        primary_bets.append({
            'type': 'Over 2.5',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE OVER TREND: Home shows ≥70% Over ({home_over}%) vs away team that concedes heavily ({away_ga:.1f} GA/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single Over Trend'
        })
    
    if away_over >= 70 and home_ga >= 1.8:  # Away scores over often, home concedes heavily
        primary_bets.append({
            'type': 'Over 2.5',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE OVER TREND: Away shows ≥70% Over ({away_over}%) vs home team that concedes heavily ({home_ga:.1f} GA/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single Over Trend'
        })
    
    # Pattern 5: Single Under Trend with complementary stats
    if home_under >= 70 and home_ga <= 1.0:  # Home under often, strong defense
        primary_bets.append({
            'type': 'Under 2.5',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE UNDER TREND: Home shows ≥70% Under ({home_under}%) with strong defense ({home_ga:.1f} GA/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single Under Trend'
        })
    
    if away_under >= 70 and away_gf <= 1.2:  # Away under often, poor attack
        primary_bets.append({
            'type': 'Under 2.5',
            'probability': 0.70,
            'min_odds': 1.50,
            'reason': f"SINGLE UNDER TREND: Away shows ≥70% Under ({away_under}%) with poor attack ({away_gf:.1f} GF/game)",
            'category': 'PRIMARY_SINGLE_TREND',
            'pattern': 'Single Under Trend'
        })
    
    return primary_bets

def calculate_adjusted_expected_goals(home_gf, home_ga, away_gf, away_ga, single_adjustments, context_adjustments):
    """Calculate expected goals with ALL adjustments applied"""
    # Baseline calculation
    baseline = ((home_gf + away_ga) + (away_gf + home_ga)) / 2
    
    # Apply single trend adjustments
    adjusted_home_goals = home_gf + single_adjustments['home_goal_adjustment']
    adjusted_away_goals = away_gf + single_adjustments['away_goal_adjustment']
    
    # Apply context adjustments
    adjusted_home_goals += context_adjustments['home_goals']
    adjusted_away_goals += context_adjustments['away_goals']
    
    # Adjust for opponent strength and context
    adjusted_home_goals += away_ga + context_adjustments['opponent_goals']
    adjusted_away_goals += home_ga + context_adjustments['opponent_goals']
    
    # Calculate final expected goals
    expected_goals = (adjusted_home_goals + adjusted_away_goals) / 2
    expected_goals += context_adjustments['total_goals']
    
    # Ensure reasonable bounds
    expected_goals = max(0.5, min(5.0, expected_goals))
    
    return expected_goals, baseline

def apply_context_adjustments(context_flags):
    """Apply context adjustments - EXACT LOGIC"""
    adjustments = {
        'opponent_goals': 0.0,
        'total_goals': 0.0,
        'home_goals': 0.0,
        'away_goals': 0.0,
        'notes': []
    }
    
    # Big Club at Home
    if context_flags.get('big_club_home'):
        adjustments['opponent_goals'] -= 0.2
        adjustments['notes'].append("Big Club at Home: Opponent goals -0.2")
    
    # Relegation Desperation
    if context_flags.get('relegation_home'):
        adjustments['total_goals'] -= 0.3
        adjustments['notes'].append("Relegation Home: Total goals -0.3")
    elif context_flags.get('relegation_away'):
        adjustments['total_goals'] -= 0.3
        adjustments['notes'].append("Relegation Away: Total goals -0.3")
    
    # Title Chase Pressure
    if context_flags.get('title_chase_home'):
        adjustments['home_goals'] += 0.3
        adjustments['notes'].append("Title Chase Home: +0.3 variance")
    elif context_flags.get('title_chase_away'):
        adjustments['away_goals'] += 0.3
        adjustments['notes'].append("Title Chase Away: +0.3 variance")
    
    # European Hangover
    if context_flags.get('european_hangover'):
        adjustments['total_goals'] -= 0.2
        adjustments['notes'].append("European Hangover: Total goals -0.2")
    
    return adjustments

def calculate_over_under_probability(expected_goals):
    """Calculate Over/Under 2.5 probability - EXACT FORMULA"""
    if expected_goals > 2.5:
        probability = 0.50 + ((expected_goals - 2.5) * 0.40)
    else:
        probability = 0.50 + ((2.5 - expected_goals) * 0.40)
    
    # CAP: Minimum 25%, Maximum 85%
    probability = max(0.25, min(0.85, probability))
    return probability

def calculate_btts_probability(home_btts, away_btts, aligned_70=False):
    """Calculate BTTS probability - EXACT FORMULA"""
    if aligned_70:
        return 0.75  # Fixed 75% for aligned trends
    else:
        return (home_btts + away_btts) / 2 / 100

def calculate_value_and_stake(probability, odds):
    """💰 VALUE & STAKE CALCULATION - EXACT LOGIC"""
    if probability == 0 or odds == 0:
        return {'value': -1, 'category': 'NO VALUE', 'stake': 0.0, 'action': 'AVOID'}
    
    value = (probability * odds) - 1
    
    # Value Tiers - EXACT THRESHOLDS
    if value >= 0.25:
        category = "EXCELLENT VALUE"
        stake = 3.0
        action = "STRONG BET"
    elif value >= 0.15:
        category = "GOOD VALUE"
        stake = 2.0
        action = "BET"
    elif value >= 0.05:
        category = "LIMITED VALUE"
        stake = 1.0
        action = "CONSIDER"
    else:
        category = "NO VALUE"
        stake = 0.0
        action = "AVOID"
    
    # Stake Formula: Min(3, Max(1, Value × 10))
    calculated_stake = min(3.0, max(1.0, value * 10))
    stake = min(stake, calculated_stake)  # Use whichever is lower
    
    return {
        'value': value,
        'category': category,
        'stake': stake,
        'action': action,
        'reason': f"{value:+.1%} value edge"
    }

def get_secondary_bet(primary_bet, expected_goals, btts_prob):
    """🥈 Secondary Bet - EXACT LOGIC"""
    # If primary is BTTS, secondary is Over/Under based on expected goals
    if primary_bet == 'BTTS Yes':
        if expected_goals > 2.7:
            return {
                'bet': 'Over 2.5',
                'min_odds': 1.70,
                'reason': f"BTTS Primary + High expected goals ({expected_goals:.2f})",
                'category': 'SECONDARY'
            }
        elif expected_goals < 2.3:
            return {
                'bet': 'Under 2.5',
                'min_odds': 1.80,
                'reason': f"BTTS Primary + Low expected goals ({expected_goals:.2f})",
                'category': 'SECONDARY'
            }
        else:
            return None
    
    # If primary is Over 2.5, secondary is BTTS Yes (high-scoring matches often feature both teams scoring)
    elif primary_bet == 'Over 2.5':
        if btts_prob >= 0.60:
            return {
                'bet': 'BTTS Yes',
                'min_odds': 1.70,
                'reason': f"Over 2.5 Primary + High BTTS probability ({btts_prob:.0%})",
                'category': 'SECONDARY'
            }
    
    # If primary is Under 2.5, secondary is BTTS No (low-scoring matches often mean clean sheets)
    elif primary_bet == 'Under 2.5':
        if btts_prob <= 0.40:
            return {
                'bet': 'BTTS No',
                'min_odds': 1.70,
                'reason': f"Under 2.5 Primary + Low BTTS probability ({btts_prob:.0%})",
                'category': 'SECONDARY'
            }
    
    return None

def get_tertiary_bets(expected_goals, btts_probability, home_team, away_team):
    """🥉 Tertiary Bets (Correct Scores) - EXACT LOGIC"""
    if expected_goals <= 2.0:
        scores = [f"{home_team} 1-0 {away_team}", f"{home_team} 0-0 {away_team}", 
                  f"{home_team} 1-1 {away_team}", f"{home_team} 0-1 {away_team}"]
    elif expected_goals <= 2.5:
        scores = [f"{home_team} 1-1 {away_team}", f"{home_team} 2-1 {away_team}",
                  f"{home_team} 1-2 {away_team}", f"{home_team} 2-0 {away_team}"]
    else:
        scores = [f"{home_team} 2-1 {away_team}", f"{home_team} 2-2 {away_team}",
                  f"{home_team} 3-1 {away_team}", f"{home_team} 3-2 {away_team}"]
    
    return scores

# ============================================================================
# MAIN APPLICATION WITH FIXED LOGIC
# ============================================================================

def main():
    """Main application"""
    
    st.markdown('<div class="header">🏆 COMPLETE CONCRETE BETTING SYSTEM</div>', unsafe_allow_html=True)
    st.markdown("**FIXED LOGIC: Single ≥70% trends now trigger primary bets**")
    
    # Sidebar for data input - ALL REQUIRED INPUTS
    with st.sidebar:
        st.header("📊 DATA REQUIREMENTS (NON-NEGOTIABLE)")
        
        # Basic info
        league = st.selectbox("League", ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "Other"])
        match_date = st.date_input("Match Date", datetime.now())
        
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Fenerbahce")
        
        st.markdown("**LAST 10 HOME SPLITS:**")
        col1, col2 = st.columns(2)
        with col1:
            home_btts = st.slider("BTTS %", 0, 100, 70)
            home_over = st.slider("Over 2.5 %", 0, 100, 50)
            home_under = st.slider("Under 2.5 %", 0, 100, 50)
        with col2:
            home_gf = st.number_input("GF/game", 0.0, 5.0, 1.90, 0.01)
            home_ga = st.number_input("GA/game", 0.0, 5.0, 0.90, 0.01)
        
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Team Name ", "Konyaspor")
        
        st.markdown("**LAST 10 AWAY SPLITS:**")
        col1, col2 = st.columns(2)
        with col1:
            away_btts = st.slider("BTTS % ", 0, 100, 80)
            away_over = st.slider("Over 2.5 % ", 0, 100, 60)
            away_under = st.slider("Under 2.5 % ", 0, 100, 40)
        with col2:
            away_gf = st.number_input("GF/game ", 0.0, 5.0, 1.40, 0.01)
            away_ga = st.number_input("GA/game ", 0.0, 5.0, 1.70, 0.01)
        
        st.subheader("🚨 CONTEXT FLAGS")
        col1, col2 = st.columns(2)
        with col1:
            big_club_home = st.checkbox("Big Club at Home")
            relegation_home = st.checkbox("Home: Relegation Threatened")
            title_chase_home = st.checkbox("Home: Title Chasing")
        with col2:
            relegation_away = st.checkbox("Away: Relegation Threatened")
            title_chase_away = st.checkbox("Away: Title Chasing")
            european_hangover = st.checkbox("European Hangover")
        
        st.subheader("💰 MARKET ODDS")
        col1, col2, col3 = st.columns(3)
        with col1:
            odds_btts = st.number_input("BTTS Yes", 1.01, 10.0, 2.02, 0.01)
            odds_btts_no = st.number_input("BTTS No", 1.01, 10.0, 1.72, 0.01)
        with col2:
            odds_over = st.number_input("Over 2.5", 1.01, 10.0, 1.46, 0.01)
        with col3:
            odds_under = st.number_input("Under 2.5", 1.01, 10.0, 2.48, 0.01)
        
        if st.button("🎯 RUN COMPLETE ANALYSIS", type="primary", use_container_width=True):
            context_flags = {
                'big_club_home': big_club_home,
                'relegation_home': relegation_home,
                'relegation_away': relegation_away,
                'title_chase_home': title_chase_home,
                'title_chase_away': title_chase_away,
                'european_hangover': european_hangover
            }
            
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
                'context_flags': context_flags,
                'odds': {
                    'btts_yes': odds_btts,
                    'btts_no': odds_btts_no,
                    'over': odds_over,
                    'under': odds_under
                }
            }
            st.rerun()
    
    # Check if we have data to analyze
    if not st.session_state.match_data:
        st.info("👈 Enter ALL data requirements and click 'RUN COMPLETE ANALYSIS'")
        return
    
    data = st.session_state.match_data
    
    # Match header
    st.markdown(f"""
    <div class="card">
        <div style="text-align: center;">
            <h2 style="margin: 0; color: #1F2937;">🏠 {data['home_team']} vs ✈️ {data['away_team']}</h2>
            <div style="color: #6B7280; margin-top: 0.5rem;">Fixed System Analysis - Single Trends Enabled</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # STEP 1: CHECK FOR ≥70% ALIGNED TRENDS
    # ============================================================================
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">📊 STEP 1: CHECK ≥70% ALIGNED TRENDS</div>', unsafe_allow_html=True)
    
    aligned_trends = check_aligned_70_trends(
        data['home_btts'], data['home_over'], data['home_under'],
        data['away_btts'], data['away_over'], data['away_under']
    )
    
    primary_bet = None
    primary_trend = None
    
    if aligned_trends:
        primary_trend = aligned_trends[0]
        primary_bet = primary_trend['type']
        
        # Get odds for primary bet
        if primary_bet == 'BTTS Yes':
            odds = data['odds']['btts_yes']
        elif primary_bet == 'Over 2.5':
            odds = data['odds']['over']
        else:  # Under 2.5
            odds = data['odds']['under']
        
        value_data = calculate_value_and_stake(primary_trend['probability'], odds)
        
        # Display primary bet
        card_class = "prediction-high" if value_data['action'] in ['STRONG BET', 'BET'] else "prediction-medium"
        
        st.markdown(f"""
        <div class="prediction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #1F2937;">🏆 PRIMARY BET: {primary_trend['type']}</h3>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">System Logic:</strong> {primary_trend['reason']}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">True Probability:</strong> {primary_trend['probability']:.0%} (Fixed for aligned ≥70% trends)
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Minimum Odds Required:</strong> {primary_trend['min_odds']:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Market Odds:</strong> {odds:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Value Edge:</strong> {value_data['value']:+.1%}
                    </div>
                    <div style="color: #4B5563;">
                        <strong style="color: #374151;">Decision:</strong> {value_data['action']} - {value_data['category']}
                    </div>
                    <div style="color: #4B5563; margin-top: 0.5rem;">
                        <strong style="color: #374151;">Stake:</strong> {value_data['stake']:.1f}% of bankroll
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if odds meet minimum requirement
        if odds < primary_trend['min_odds']:
            st.warning(f"⚠️ Market odds ({odds:.2f}) below minimum required ({primary_trend['min_odds']:.2f}) - Consider avoiding")
    else:
        st.info("No aligned ≥70% trends detected - Checking for SINGLE strong trends...")
    
    # ============================================================================
    # 🚨 STEP 2: CHECK FOR SINGLE ≥70% TRENDS (FIXED LOGIC)
    # ============================================================================
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">🚨 STEP 2: CHECK SINGLE ≥70% TRENDS</div>', unsafe_allow_html=True)
    
    single_trend_bets = []
    
    # Only check single trends if no aligned trends found
    if not aligned_trends:
        single_trend_bets = check_single_70_trends_and_get_primary(
            data['home_btts'], data['home_over'], data['home_under'],
            data['away_btts'], data['away_over'], data['away_under'],
            data['home_gf'], data['home_ga'], data['away_gf'], data['away_ga'],
            data['context_flags']
        )
    
    # Apply single trend adjustments for expected goals calculation
    single_adjustments = {
        'home_goal_adjustment': 0.0,
        'away_goal_adjustment': 0.0
    }
    
    # Check for single ≥70% trends for goal adjustments
    if data['home_over'] >= 70:
        single_adjustments['home_goal_adjustment'] += 0.15
    elif data['home_under'] >= 70:
        single_adjustments['home_goal_adjustment'] -= 0.15
    
    if data['away_over'] >= 70:
        single_adjustments['away_goal_adjustment'] += 0.15
    elif data['away_under'] >= 70:
        single_adjustments['away_goal_adjustment'] -= 0.15
    
    # Apply context adjustments
    context_adjustments = apply_context_adjustments(data['context_flags'])
    
    # Calculate expected goals with all adjustments
    expected_goals, baseline_goals = calculate_adjusted_expected_goals(
        data['home_gf'], data['home_ga'], data['away_gf'], data['away_ga'],
        single_adjustments, context_adjustments
    )
    
    # Display single trend findings
    if single_trend_bets:
        # Take the strongest single trend bet
        single_trend = single_trend_bets[0]
        primary_bet = single_trend['type']
        
        # Get odds for single trend bet
        if primary_bet == 'BTTS Yes':
            odds = data['odds']['btts_yes']
            probability = calculate_btts_probability(data['home_btts'], data['away_btts'], aligned_70=False)
        elif primary_bet == 'Over 2.5':
            odds = data['odds']['over']
            probability = single_trend['probability']
        else:  # Under 2.5
            odds = data['odds']['under']
            probability = single_trend['probability']
        
        value_data = calculate_value_and_stake(probability, odds)
        
        # Display single trend bet
        card_class = "prediction-high" if value_data['action'] in ['STRONG BET', 'BET'] else "prediction-medium"
        
        st.markdown(f"""
        <div class="prediction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #1F2937;">🚀 SINGLE TREND BET: {single_trend['type']}</h3>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Pattern Identified:</strong> {single_trend['pattern']}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">System Logic:</strong> {single_trend['reason']}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">True Probability:</strong> {probability:.0%} (Based on single ≥70% trend)
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Minimum Odds Required:</strong> {single_trend['min_odds']:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Market Odds:</strong> {odds:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Value Edge:</strong> {value_data['value']:+.1%}
                    </div>
                    <div style="color: #4B5563;">
                        <strong style="color: #374151;">Decision:</strong> {value_data['action']} - {value_data['category']}
                    </div>
                    <div style="color: #4B5563; margin-top: 0.5rem;">
                        <strong style="color: #374151;">Stake:</strong> {value_data['stake']:.1f}% of bankroll
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if odds meet minimum requirement
        if odds < single_trend['min_odds']:
            st.warning(f"⚠️ Market odds ({odds:.2f}) below minimum required ({single_trend['min_odds']:.2f}) - Consider avoiding")
    elif not aligned_trends:
        st.info("No single ≥70% trends with complementary stats detected")
    
    # ============================================================================
    # STEP 3: EXPECTED GOALS CALCULATION
    # ============================================================================
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">📊 STEP 3: EXPECTED GOALS CALCULATION</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4 style="color: #1F2937;">📈 Expected Goals Analysis</h4>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Baseline Formula:</strong><br>
                [({data['home_gf']:.2f} + {data['away_ga']:.2f}) + ({data['away_gf']:.2f} + {data['home_ga']:.2f})] ÷ 2
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Baseline:</strong> {baseline_goals:.2f} goals
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Single Trend Adjustments:</strong><br>
                • Home: {single_adjustments['home_goal_adjustment']:+.2f}<br>
                • Away: {single_adjustments['away_goal_adjustment']:+.2f}
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Context Adjustments:</strong><br>
                {''.join([f'• {note}<br>' for note in context_adjustments['notes']]) if context_adjustments['notes'] else '• None'}
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937; margin: 1rem 0;">
                Final: {expected_goals:.2f} expected goals
            </div>
            <div style="color: #4B5563;">
                <strong style="color: #374151;">Interpretation:</strong> {'Over 2.5' if expected_goals > 2.5 else 'Under 2.5'} expected
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate probabilities
        over_under_prob = calculate_over_under_probability(expected_goals)
        btts_prob = calculate_btts_probability(data['home_btts'], data['away_btts'], 
                                              aligned_70=(data['home_btts'] >= 70 and data['away_btts'] >= 70))
        
        st.markdown(f"""
        <div class="card">
            <h4 style="color: #1F2937;">🎯 Probability Calculations</h4>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Over/Under 2.5 Formula:</strong><br>
                Base 50% + (Distance from 2.5 × 40)
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Over 2.5 Probability:</strong> {over_under_prob:.1%} if Over, {1-over_under_prob:.1%} if Under
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">BTTS Probability Formula:</strong><br>
                {'75% fixed for aligned ≥70% trends' if (data['home_btts'] >= 70 and data['away_btts'] >= 70) else f'(Home {data["home_btts"]}% + Away {data["away_btts"]}%) ÷ 2'}
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">BTTS Yes Probability:</strong> {btts_prob:.1%}
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">BTTS No Probability:</strong> {1-btts_prob:.1%}
            </div>
            <div style="color: #4B5563; margin-top: 1rem;">
                <strong style="color: #374151;">Key:</strong> ≥70% = Strong, 50-69% = Moderate, <50% = Weak
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # STEP 4: SECONDARY BETS (IF NO PRIMARY FOUND YET)
    # ============================================================================
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">💰 STEP 4: SECONDARY BETS</div>', unsafe_allow_html=True)
    
    secondary = None
    
    # Only look for secondary bets if no primary bet found yet
    if not primary_bet and not single_trend_bets:
        if expected_goals > 2.7:
            secondary = {
                'bet': 'Over 2.5',
                'min_odds': 1.70,
                'reason': f"Expected Goals {expected_goals:.2f} > 2.7",
                'category': 'SECONDARY'
            }
        elif expected_goals < 2.3:
            secondary = {
                'bet': 'Under 2.5',
                'min_odds': 1.80,
                'reason': f"Expected Goals {expected_goals:.2f} < 2.3",
                'category': 'SECONDARY'
            }
    
    # If we have a primary bet, get complementary secondary
    elif primary_bet:
        secondary = get_secondary_bet(primary_bet, expected_goals, btts_prob)
    
    # Display secondary bet
    if secondary:
        # Get odds and probability for secondary bet
        if secondary['bet'] == 'BTTS Yes':
            sec_odds = data['odds']['btts_yes']
            sec_prob = btts_prob
        elif secondary['bet'] == 'BTTS No':
            sec_odds = data['odds']['btts_no']
            sec_prob = 1 - btts_prob
        elif secondary['bet'] == 'Over 2.5':
            sec_odds = data['odds']['over']
            sec_prob = over_under_prob
        else:  # Under 2.5
            sec_odds = data['odds']['under']
            sec_prob = 1 - over_under_prob
        
        sec_value = calculate_value_and_stake(sec_prob, sec_odds)
        
        # Display secondary bet
        sec_card_class = "secondary-card" if sec_value['action'] not in ['AVOID'] else "no-value-card"
        
        st.markdown(f"""
        <div class="prediction-card {sec_card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #1F2937;">🥈 SECONDARY BET: {secondary['bet']}</h3>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">System Logic:</strong> {secondary['reason']}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">True Probability:</strong> {sec_prob:.1%}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Minimum Odds Required:</strong> {secondary['min_odds']:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Market Odds:</strong> {sec_odds:.2f}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Value Edge:</strong> {sec_value['value']:+.1%}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Decision:</strong> {sec_value['action']} - {sec_value['category']}
                    </div>
                    <div style="color: #4B5563;">
                        <strong style="color: #374151;">Stake:</strong> {sec_value['stake']:.1f}% of bankroll
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if odds meet minimum requirement
        if sec_odds < secondary['min_odds']:
            st.warning(f"⚠️ Market odds ({sec_odds:.2f}) below minimum required ({secondary['min_odds']:.2f}) - Consider avoiding")
    elif not primary_bet and not single_trend_bets:
        st.info("No secondary bet recommendation (expected goals between 2.3-2.7)")
    
    # ============================================================================
    # TERTIARY BETS
    # ============================================================================
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">🥉 TERTIARY BETS (Correct Scores)</div>', unsafe_allow_html=True)
    
    tertiary_scores = get_tertiary_bets(
        expected_goals,
        btts_prob,
        data['home_team'],
        data['away_team']
    )
    
    cols = st.columns(len(tertiary_scores))
    for idx, score in enumerate(tertiary_scores):
        with cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #F7FAFC; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #E2E8F0;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #1F2937;">{score}</div>
                <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.5rem;">For bet builders</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================================
    # SYSTEM SUMMARY
    # ============================================================================
    with st.expander("📋 FIXED SYSTEM LOGIC SUMMARY", expanded=True):
        st.markdown(f"""
        ### 🎯 FIXED LOGIC: SINGLE TRENDS NOW TRIGGER BETS
        
        **STEP 1: Check for aligned ≥70% trends:**
        - Home BTTS: {data['home_btts']}% {'✓ ≥70%' if data['home_btts'] >= 70 else '✗ <70%'}
        - Away BTTS: {data['away_btts']}% {'✓ ≥70%' if data['away_btts'] >= 70 else '✗ <70%'}
        - Home Over: {data['home_over']}% {'✓ ≥70%' if data['home_over'] >= 70 else '✗ <70%'}
        - Away Over: {data['away_over']}% {'✓ ≥70%' if data['away_over'] >= 70 else '✗ <70%'}
        - Home Under: {data['home_under']}% {'✓ ≥70%' if data['home_under'] >= 70 else '✗ <70%'}
        - Away Under: {data['away_under']}% {'✓ ≥70%' if data['away_under'] >= 70 else '✗ <70%'}
        - **Result:** {'ALIGNED TREND FOUND' if aligned_trends else 'No aligned trends'}
        
        **🚨 STEP 2: Check single ≥70% trends (FIXED):**
        - Single trends checked: {len(single_trend_bets)} pattern(s) identified
        - **Key Finding:** {'No single strong trends' if not single_trend_bets else f"{single_trend_bets[0]['pattern']} identified"}
        
        **STEP 3: Expected Goals Calculation:**
        - Baseline: [({data['home_gf']:.2f} + {data['away_ga']:.2f}) + ({data['away_gf']:.2f} + {data['home_ga']:.2f})] ÷ 2 = {baseline_goals:.2f}
        - Adjustments Applied: {len(context_adjustments['notes'])} context adjustments + single trend adjustments
        - **Final Expected Goals:** {expected_goals:.2f}
        
        **STEP 4: Betting Decisions:**
        - Primary Bet: {primary_bet if primary_bet else ('Single Trend: ' + single_trend_bets[0]['type'] if single_trend_bets else 'None')}
        - Secondary Bet: {secondary['bet'] if secondary else 'None'}
        - **CORE PRINCIPLE:** Bet only if value ≥15%
        
        **💎 PROVEN PATTERNS NOW DETECTED:**
        1. {'✓ Double 70% Pattern' if aligned_trends else '✗'}
        2. {'✓ Defensive Specialist' if any(b['pattern'] == 'Defensive Specialist' for b in single_trend_bets) else '✗'}
        3. {'✓ Single BTTS Trend' if any(b['pattern'] == 'Single BTTS Trend' for b in single_trend_bets) else '✗'}
        4. {'✓ Single Over/Under Trend' if any(b['pattern'] in ['Single Over Trend', 'Single Under Trend'] for b in single_trend_bets) else '✗'}
        
        **🔧 SYSTEM FIX APPLIED:**
        - Single ≥70% trends now trigger primary bets
        - Patterns detected: Defensive Specialist, Home Bounce-Back, Single BTTS/Over/Under trends
        - Expected goals now properly adjusted for single trends
        - Bologna-Juventus type matches will now be correctly identified
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <div><strong>🏆 FIXED SYSTEM:</strong> Single ≥70% trends now trigger bets</div>
        <div style="margin-top: 0.5rem;">Matches like Bologna-Juventus will now be correctly analyzed</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
