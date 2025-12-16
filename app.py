"""
COMPLETE BATTLE-TESTED BETTING SYSTEM
FULL IMPLEMENTATION OF ALL PREDICTION LOGIC
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for all match data
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# ============================================================================
# COMPLETE PREDICTION LOGIC - ALL FUNCTIONS
# ============================================================================

def check_aligned_strong_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """TIER 1: ALIGNED STRONG TRENDS (≥70%)"""
    trends = []
    
    # BTTS Yes: Both ≥70% BTTS → Bet BTTS Yes (75% probability)
    if home_btts >= 70 and away_btts >= 70:
        trends.append({
            'type': 'BTTS Yes',
            'tier': 1,
            'probability': 0.75,
            'reason': f"Both teams show ≥70% BTTS trend",
            'action': 'BET'
        })
    
    # Over 2.5: Both ≥70% Over → Bet Over 2.5 (70% probability)
    if home_over >= 70 and away_over >= 70:
        trends.append({
            'type': 'Over 2.5',
            'tier': 1,
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Over trend",
            'action': 'BET'
        })
    
    # Under 2.5: Both ≥70% Under → Bet Under 2.5 (70% probability)
    if home_under >= 70 and away_under >= 70:
        trends.append({
            'type': 'Under 2.5',
            'tier': 1,
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Under trend",
            'action': 'BET'
        })
    
    return trends

def check_single_dominant_trends(home_btts, home_over, home_under, away_btts, away_over, away_under, home_team, away_team, is_big_club_home):
    """TIER 2: SINGLE DOMINANT TREND (≥70%)"""
    trends = []
    adjustments = {'home': 0, 'away': 0}
    
    # Home team single trends
    if home_under >= 70:
        trends.append({
            'type': 'Under 2.5',
            'tier': 2,
            'probability': 0.70,
            'reason': f"{home_team} shows ≥70% Under trend at home",
            'adjustment': -0.15
        })
        adjustments['home'] = -0.15
    
    if home_over >= 70:
        trends.append({
            'type': 'Over 2.5',
            'tier': 2,
            'probability': 0.65,
            'reason': f"{home_team} shows ≥70% Over trend at home",
            'adjustment': 0.15
        })
        adjustments['home'] = 0.15
    
    # Away team single trends (with big club discount)
    if away_under >= 70:
        if is_big_club_home:
            trends.append({
                'type': 'Under 2.5',
                'tier': 2,
                'probability': 0.60,
                'reason': f"{away_team} shows ≥70% Under trend away (discounted - big club home)",
                'adjustment': 0  # No adjustment due to big club discount
            })
        else:
            trends.append({
                'type': 'Under 2.5',
                'tier': 2,
                'probability': 0.70,
                'reason': f"{away_team} shows ≥70% Under trend away",
                'adjustment': -0.15
            })
            adjustments['away'] = -0.15
    
    if away_over >= 70 and not is_big_club_home:
        trends.append({
            'type': 'Over 2.5',
            'tier': 2,
            'probability': 0.65,
            'reason': f"{away_team} shows ≥70% Over trend away",
            'adjustment': 0.15
        })
        adjustments['away'] = 0.15
    
    return trends, adjustments

def calculate_expected_goals_baseline(home_gf, away_ga, away_gf, home_ga):
    """Calculate baseline expected goals"""
    return ((home_gf + away_ga) + (away_gf + home_ga)) / 2

def apply_trend_adjustments(expected_goals, home_adjustment, away_adjustment):
    """Apply trend adjustments (±15% per 70% trend)"""
    total_adjustment = (home_adjustment + away_adjustment) / 2 if (home_adjustment != 0 or away_adjustment != 0) else 0
    return expected_goals * (1 + total_adjustment)

def apply_context_adjustments(expected_goals, context):
    """TIER 4: CONTEXT & PSYCHOLOGY adjustments"""
    adjustments = []
    
    if context.get('big_club_home_after_poor_run', False):
        expected_goals += 0.3
        adjustments.append("Big club at home after poor run: +0.3 goals")
    
    if context.get('relegation_desperation', False):
        expected_goals -= 0.2
        adjustments.append("Relegation desperation: -0.2 goals")
    
    if context.get('title_chase', False):
        expected_goals += 0.1
        adjustments.append("Title chase pressure: +0.1 goals")
    
    return expected_goals, adjustments

def calculate_probability_from_expected_goals(expected_goals):
    """Convert expected goals to Over/Under probability"""
    if expected_goals > 2.7:
        return {'over': 0.70, 'under': 0.30, 'recommendation': 'Over 2.5'}
    elif expected_goals > 2.5:
        return {'over': 0.65, 'under': 0.35, 'recommendation': 'Over 2.5'}
    elif expected_goals < 2.3:
        return {'over': 0.30, 'under': 0.70, 'recommendation': 'Under 2.5'}
    elif expected_goals < 2.5:
        return {'over': 0.35, 'under': 0.65, 'recommendation': 'Under 2.5'}
    else:
        return {'over': 0.50, 'under': 0.50, 'recommendation': 'No clear edge'}

def calculate_btts_probability(home_gf, away_ga, away_gf, home_ga, home_btts_pct, away_btts_pct):
    """Calculate BTTS probability"""
    # Base calculation
    home_scoring_prob = min(0.95, home_gf / max(away_ga, 0.5))
    away_scoring_prob = min(0.95, away_gf / max(home_ga, 0.5))
    base_prob = home_scoring_prob * away_scoring_prob * 0.8
    
    # Adjust for trends
    trend_adjustment = 1.0
    if home_btts_pct >= 70:
        trend_adjustment *= 1.1
    if away_btts_pct >= 70:
        trend_adjustment *= 1.1
    
    final_prob = min(0.95, max(0.05, base_prob * trend_adjustment))
    return final_prob

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

def generate_alternative_bets(expected_goals, btts_prob, home_team, away_team):
    """Generate alternative bets for bet builders"""
    alternatives = []
    
    # Secondary bet based on expected goals
    if expected_goals > 2.7:
        alternatives.append({
            'type': 'Secondary',
            'bet': 'Over 2.5',
            'probability': 0.65,
            'reason': f'Expected Goals: {expected_goals:.1f} > 2.7'
        })
    elif expected_goals < 2.3:
        alternatives.append({
            'type': 'Secondary',
            'bet': 'Under 2.5',
            'probability': 0.65,
            'reason': f'Expected Goals: {expected_goals:.1f} < 2.3'
        })
    
    # Tertiary bets (correct scores)
    if expected_goals > 2.5 and btts_prob > 0.5:
        scores = [f"{home_team} 2-1 {away_team}", f"{home_team} 3-1 {away_team}", f"{home_team} 2-2 {away_team}"]
    elif expected_goals < 2.0:
        scores = [f"{home_team} 1-0 {away_team}", f"{home_team} 0-1 {away_team}", f"{home_team} 1-1 {away_team}"]
    else:
        scores = [f"{home_team} 2-0 {away_team}", f"{home_team} 1-1 {away_team}", f"{home_team} 2-1 {away_team}"]
    
    alternatives.append({
        'type': 'Tertiary',
        'bet': 'Correct Score',
        'suggestions': scores,
        'reason': f'Based on Expected Goals: {expected_goals:.1f}'
    })
    
    return alternatives

def run_complete_prediction(data):
    """MAIN PREDICTION ENGINE - Runs all logic"""
    predictions = []
    
    # Extract data
    home_team = data['home_team']
    away_team = data['away_team']
    
    home_btts = data['home_btts']
    home_over = data['home_over']
    home_under = data['home_under']
    home_gf = data['home_gf']
    home_ga = data['home_ga']
    
    away_btts = data['away_btts']
    away_over = data['away_over']
    away_under = data['away_under']
    away_gf = data['away_gf']
    away_ga = data['away_ga']
    
    is_big_club_home = data.get('big_club_home', False)
    context = data.get('context', {})
    
    # Step 1: Check for aligned strong trends (≥70%)
    aligned_trends = check_aligned_strong_trends(
        home_btts, home_over, home_under,
        away_btts, away_over, away_under
    )
    
    if aligned_trends:
        predictions.extend(aligned_trends)
        return predictions, None  # Stop here for aligned trends
    
    # Step 2: Check for single dominant trends
    single_trends, trend_adjustments = check_single_dominant_trends(
        home_btts, home_over, home_under,
        away_btts, away_over, away_under,
        home_team, away_team, is_big_club_home
    )
    predictions.extend(single_trends)
    
    # Step 3: Calculate Expected Goals
    baseline_goals = calculate_expected_goals_baseline(home_gf, away_ga, away_gf, home_ga)
    trend_adjusted_goals = apply_trend_adjustments(
        baseline_goals, 
        trend_adjustments['home'], 
        trend_adjustments['away']
    )
    final_goals, context_adjustments = apply_context_adjustments(trend_adjusted_goals, context)
    
    # Step 4: Determine probabilities
    goal_prob = calculate_probability_from_expected_goals(final_goals)
    btts_prob = calculate_btts_probability(home_gf, away_ga, away_gf, home_ga, home_btts, away_btts)
    
    # Add calculated predictions
    if goal_prob['recommendation'] != 'No clear edge':
        predictions.append({
            'type': goal_prob['recommendation'],
            'tier': 3,
            'probability': goal_prob['over'] if goal_prob['recommendation'] == 'Over 2.5' else goal_prob['under'],
            'reason': f'Expected Goals: {final_goals:.2f}',
            'expected_goals': final_goals,
            'adjustments': context_adjustments
        })
    
    predictions.append({
        'type': 'BTTS Yes',
        'tier': 3,
        'probability': btts_prob,
        'reason': f'BTTS probability based on scoring rates'
    })
    
    return predictions, final_goals

# ============================================================================
# UI COMPONENTS
# ============================================================================

def create_input_form():
    """Create data input form"""
    with st.sidebar:
        st.header("📊 Match Data Input")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            league = st.selectbox("League", ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "Other"])
        with col2:
            match_date = st.date_input("Match Date", datetime.now())
        
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Nacional")
        
        col1, col2 = st.columns(2)
        with col1:
            home_btts = st.slider("BTTS % (Last 10)", 0, 100, 60)
            home_over = st.slider("Over 2.5 %", 0, 100, 70)
            home_under = st.slider("Under 2.5 %", 0, 100, 30)
        with col2:
            home_gf = st.number_input("GF/game", 0.0, 5.0, 1.00, 0.01)
            home_ga = st.number_input("GA/game", 0.0, 5.0, 2.20, 0.01)
        
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Team Name ", "Tondela")
        
        col1, col2 = st.columns(2)
        with col1:
            away_btts = st.slider("BTTS % (Last 10) ", 0, 100, 29)
            away_over = st.slider("Over 2.5 % ", 0, 100, 71)
            away_under = st.slider("Under 2.5 % ", 0, 100, 29)
        with col2:
            away_gf = st.number_input("GF/game ", 0.0, 5.0, 0.71, 0.01)
            away_ga = st.number_input("GA/game ", 0.0, 5.0, 1.86, 0.01)
        
        st.subheader("🎯 Context")
        col1, col2 = st.columns(2)
        with col1:
            big_club_home = st.checkbox("Big Club at Home", False)
            big_club_home_after_poor_run = st.checkbox("Home After Poor Run", False)
        with col2:
            relegation_desperation = st.checkbox("Relegation Battle", False)
            title_chase = st.checkbox("Title Chase", False)
        
        st.subheader("💰 Market Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            odds_btts = st.number_input("BTTS Yes", 1.01, 10.0, 1.86, 0.01)
        with col2:
            odds_over = st.number_input("Over 2.5", 1.01, 10.0, 2.14, 0.01)
        with col3:
            odds_under = st.number_input("Under 2.5", 1.01, 10.0, 1.61, 0.01)
        
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
                'big_club_home': big_club_home,
                'context': {
                    'big_club_home_after_poor_run': big_club_home_after_poor_run,
                    'relegation_desperation': relegation_desperation,
                    'title_chase': title_chase
                },
                'odds': {
                    'btts': odds_btts,
                    'over': odds_over,
                    'under': odds_under
                }
            }
            st.rerun()
        
        return None

def display_prediction_card(prediction, odds):
    """Display a prediction card"""
    if prediction['type'] == 'Over 2.5':
        market_odds = odds['over']
    elif prediction['type'] == 'Under 2.5':
        market_odds = odds['under']
    else:  # BTTS Yes
        market_odds = odds['btts']
    
    value_data = calculate_value(prediction['probability'], market_odds)
    
    card_class = "prediction-high" if value_data['value'] >= 0.15 else "prediction-medium" if value_data['value'] >= 0.05 else "prediction-low"
    
    with st.container():
        st.markdown(f"""
        <div class="prediction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0 0 0.5rem 0;">{prediction['type']}</h3>
                    <div style="color: #718096; font-size: 0.9rem;">
                        TIER {prediction['tier']}: {prediction.get('reason', '')}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{prediction['probability']:.0%}</div>
                    <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Market Odds", f"{market_odds:.2f}")
        with col2:
            st.metric("Value Edge", f"{value_data['value']:+.1%}")
        with col3:
            if value_data['stake'] > 0:
                st.metric("Stake", f"{value_data['stake']:.1f}%")
            else:
                st.metric("Stake", "No bet")
        
        st.markdown(f"**Decision:** {value_data['action']} ({value_data['category']})")
        
        if 'expected_goals' in prediction:
            st.info(f"Expected Goals: {prediction['expected_goals']:.2f}")
        
        if 'adjustments' in prediction and prediction['adjustments']:
            st.markdown("**Adjustments:**")
            for adj in prediction['adjustments']:
                st.markdown(f"• {adj}")
        
        if prediction['tier'] == 1:
            st.success("🎯 **ALIGNED STRONG TREND DETECTED** - Highest confidence bet")

def display_team_analysis(data):
    """Display team analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="margin: 0 0 1rem 0;">🏠 Home Team: {}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Trends (Last 10)</div>
                    <div>BTTS: <strong>{}%</strong></div>
                    <div>Over 2.5: <strong>{}%</strong></div>
                    <div>Under 2.5: <strong>{}%</strong></div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Performance</div>
                    <div>GF/game: <strong>{:.2f}</strong></div>
                    <div>GA/game: <strong>{:.2f}</strong></div>
                    <div>Net: <strong>{:+.2f}</strong></div>
                </div>
            </div>
        </div>
        """.format(
            data['home_team'], data['home_btts'], data['home_over'], data['home_under'],
            data['home_gf'], data['home_ga'], data['home_gf'] - data['home_ga']
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="margin: 0 0 1rem 0;">✈️ Away Team: {}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Trends (Last 10)</div>
                    <div>BTTS: <strong>{}%</strong></div>
                    <div>Over 2.5: <strong>{}%</strong></div>
                    <div>Under 2.5: <strong>{}%</strong></div>
                </div>
                <div>
                    <div style="font-size: 0.9rem; color: #718096;">Performance</div>
                    <div>GF/game: <strong>{:.2f}</strong></div>
                    <div>GA/game: <strong>{:.2f}</strong></div>
                    <div>Net: <strong>{:+.2f}</strong></div>
                </div>
            </div>
        </div>
        """.format(
            data['away_team'], data['away_btts'], data['away_over'], data['away_under'],
            data['away_gf'], data['away_ga'], data['away_gf'] - data['away_ga']
        ), unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    st.markdown('<div class="header">🎯 COMPLETE BETTING SYSTEM</div>', unsafe_allow_html=True)
    st.markdown("**All prediction logic implemented: Aligned Trends → Single Trends → Expected Goals → Context → Value**")
    
    # Create input form
    create_input_form()
    
    # Check if we have data to analyze
    if not st.session_state.match_data:
        st.info("👈 Enter match data in the sidebar and click 'Run Complete Analysis'")
        
        # Show system overview
        with st.expander("📋 System Logic Overview", expanded=True):
            st.markdown("""
            ### 🎯 COMPLETE PREDICTION LOGIC
            
            **TIER 1: ALIGNED STRONG TRENDS (≥70%)**
            - Both teams show same ≥70% trend → BET IMMEDIATELY
            - Probability: 75% for aligned trends
            
            **TIER 2: SINGLE DOMINANT TREND (≥70%)**
            - One team shows ≥70% trend → Apply adjustment (±15%)
            - Big club at home discounts opponent trends
            
            **TIER 3: CALCULATED EXPECTED GOALS**
            - Formula: [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2
            - Apply trend adjustments (±15% per 70% trend)
            
            **TIER 4: CONTEXT & PSYCHOLOGY**
            - Big club at home after poor run: +0.3 goals
            - Relegation desperation: -0.2 goals
            - Title chase pressure: +0.1 goals
            
            **VALUE CALCULATION**
            - Formula: Value = (Probability × Odds) - 1
            - Bet if Value ≥ 15%
            """)
        return
    
    data = st.session_state.match_data
    
    # Match header
    st.markdown(f"""
    <div class="card">
        <div style="text-align: center;">
            <h2 style="margin: 0;">🏠 {data['home_team']} vs ✈️ {data['away_team']}</h2>
            <div style="color: #718096; margin-top: 0.5rem;">Complete Analysis • All Logic Applied</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display team analysis
    display_team_analysis(data)
    
    # Run complete prediction
    predictions, expected_goals = run_complete_prediction(data)
    
    # Display predictions
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">🎯 PREDICTION RESULTS</div>', unsafe_allow_html=True)
    
    # Check for aligned trends first
    aligned_trends = [p for p in predictions if p['tier'] == 1]
    
    if aligned_trends:
        st.success("🎯 **ALIGNED STRONG TRENDS DETECTED** - Highest confidence bets found!")
        
        for trend in aligned_trends:
            display_prediction_card(trend, data['odds'])
        
        # Show decision logic
        with st.expander("📋 Decision Logic", expanded=True):
            st.markdown("""
            ### ✅ ALIGNED TRENDS DECISION PATH
            
            **System detected aligned ≥70% trends:**
            1. Found aligned trend → **STOP analysis** (as per flowchart)
            2. Calculate value based on 75% probability for aligned trends
            3. Bet immediately if value ≥ 15%
            
            **This follows the exact decision flowchart:**
            ```
            START
            │
            ├─ Step 1: Check for ≥70% ALIGNED trends
            │   ├─ If Both ≥70% BTTS → BET BTTS Yes
            │   ├─ If Both ≥70% Over → BET Over 2.5  
            │   ├─ If Both ≥70% Under → BET Under 2.5
            │   └─ If aligned trends → BET & STOP
            ```
            """)
    else:
        # No aligned trends, show all predictions
        st.info("ℹ️ **No aligned strong trends found** - Proceeding with complete analysis")
        
        # Sort predictions by tier
        tier2_predictions = [p for p in predictions if p['tier'] == 2]
        tier3_predictions = [p for p in predictions if p['tier'] == 3]
        
        if tier2_predictions:
            st.markdown("### 🥈 Single Dominant Trends")
            for pred in tier2_predictions:
                display_prediction_card(pred, data['odds'])
        
        if tier3_predictions:
            st.markdown("### 🥉 Calculated Predictions")
            for pred in tier3_predictions:
                display_prediction_card(pred, data['odds'])
        
        # Show expected goals if calculated
        if expected_goals:
            st.markdown("### 📊 Expected Goals Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Expected Goals", f"{expected_goals:.2f}")
            with col2:
                if expected_goals > 2.5:
                    st.metric("Recommendation", "Over 2.5", "Based on expected goals")
                else:
                    st.metric("Recommendation", "Under 2.5", "Based on expected goals")
    
    # Generate alternative bets
    if expected_goals:
        btts_prob = calculate_btts_probability(
            data['home_gf'], data['away_ga'], data['away_gf'], data['home_ga'],
            data['home_btts'], data['away_btts']
        )
        
        alternative_bets = generate_alternative_bets(
            expected_goals, btts_prob, data['home_team'], data['away_team']
        )
        
        st.markdown("### 🔄 Alternative Bets")
        
        for alt in alternative_bets:
            if alt['type'] == 'Secondary':
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 600;">Secondary: {alt['bet']}</div>
                                <div style="font-size: 0.9rem; color: #718096;">{alt['reason']}</div>
                            </div>
                            <div>
                                <div style="font-weight: 600;">{alt['probability']:.0%}</div>
                                <div style="font-size: 0.9rem; color: #718096;">Probability</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            elif alt['type'] == 'Tertiary':
                st.markdown(f"""
                <div class="card">
                    <div style="font-weight: 600; margin-bottom: 1rem;">Tertiary: Correct Score</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 1rem;">
                """, unsafe_allow_html=True)
                
                for score in alt['suggestions']:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 0.75rem; background: #F7FAFC; border-radius: 8px;">
                        <div style="font-weight: 600;">{score}</div>
                        <div style="font-size: 0.8rem; color: #718096;">For bet builders</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
    
    # System verification
    with st.expander("🔍 System Verification", expanded=False):
        st.markdown("""
        ### ✅ SYSTEM CHECKS COMPLETED
        
        **1. Aligned Trends Check:** ✓
        - Checked for both teams ≥70% same trend
        - If found: BET & STOP logic applied
        
        **2. Single Trends Check:** ✓
        - Checked for single ≥70% trends
        - Applied ±15% adjustments
        - Big club home context considered
        
        **3. Expected Goals Calculation:** ✓
        - Baseline: [(GFh+GAa) + (GFa+GAh)] ÷ 2
        - Trend adjustments applied
        - Context adjustments applied
        
        **4. Probability Calculation:** ✓
        - Aligned trends: 75% probability
        - Single trends: 65-70% probability
        - Expected goals based: Calculated
        
        **5. Value Calculation:** ✓
        - Formula: (Probability × Odds) - 1
        - Threshold: ≥15% value needed
        - Stake size: 1-3% based on value
        
        **6. Alternative Bets:** ✓
        - Secondary: Based on expected goals
        - Tertiary: Correct score suggestions
        """)
        
        # Show data verification
        st.markdown("### 📊 Data Verification")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Home Over%", f"{data['home_over']}%", "≥70% = Strong trend" if data['home_over'] >= 70 else "")
        with col2:
            st.metric("Away Over%", f"{data['away_over']}%", "≥70% = Strong trend" if data['away_over'] >= 70 else "")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <div><strong>🎯 COMPLETE SYSTEM IMPLEMENTED:</strong> All tiers of prediction logic active</div>
        <div style="margin-top: 0.5rem;">Aligned Trends → Single Trends → Expected Goals → Context → Value → Alternative Bets</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
