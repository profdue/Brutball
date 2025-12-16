import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Enhanced Comparative Betting System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚽ Enhanced Comparative Betting System")
st.markdown("""
**Original Logic + Automatic Defensive Strength Detection** - Works for ALL teams without special cases.
""")

# ==================== ENHANCED COMPARATIVE LOGIC ====================

def detect_defensive_strength(conceding_avg, matches_played, league_avg=1.3):
    """
    Auto-detect defensive strength from data alone.
    No team database needed - works for ALL teams.
    
    Returns: 'ELITE', 'STRONG', 'AVERAGE', or 'WEAK'
    """
    if matches_played < 5:
        return 'UNKNOWN'  # Insufficient data
    
    # Universal statistical thresholds (work for any league)
    if conceding_avg < 0.80:
        return 'ELITE'     # Top 10% defenses
    elif conceding_avg <= 1.00:  # FIXED: Changed from < 1.0 to <= 1.0
        return 'STRONG'    # Top 25% defenses  
    elif conceding_avg > 1.80:
        return 'WEAK'      # Bottom 25% defenses
    elif conceding_avg > league_avg * 1.2:
        return 'WEAK'      # Worse than league average
    else:
        return 'AVERAGE'

def get_adjustment_factor(defensive_strength, is_home_advantage=True):
    """
    Get scoring adjustment based on opponent's defensive strength.
    Works universally for ALL teams.
    """
    # Base adjustments (PURE according to stated rules - no extra home/away adjustments)
    adjustments = {
        'ELITE': 0.75,     # 25% reduction vs elite defenses
        'STRONG': 0.85,    # 15% reduction vs strong defenses
        'AVERAGE': 1.0,    # No adjustment
        'WEAK': 1.15,      # 15% boost vs weak defenses
        'UNKNOWN': 1.0     # No adjustment for insufficient data
    }
    
    # FIXED: Return pure adjustment factor without extra home/away multipliers
    # This matches the stated rules exactly
    return adjustments.get(defensive_strength, 1.0)

def predict_scoring_enhanced(home_scoring, home_conceding, away_scoring, away_conceding,
                            home_matches, away_matches, league_avg=1.3):
    """
    ENHANCED comparative logic with automatic defensive strength detection.
    Works for ALL teams without special cases.
    """
    
    # Auto-detect defensive strengths
    home_defense = detect_defensive_strength(home_conceding, home_matches, league_avg)
    away_defense = detect_defensive_strength(away_conceding, away_matches, league_avg)
    
    # Get adjustment factors (pure factors only - no extra home/away multipliers)
    home_scoring_adj = get_adjustment_factor(away_defense, is_home_advantage=True)
    away_scoring_adj = get_adjustment_factor(home_defense, is_home_advantage=False)
    
    # Apply adjustments (pure multiplication)
    home_scoring_adj_value = home_scoring * home_scoring_adj
    away_scoring_adj_value = away_scoring * away_scoring_adj
    
    # Calculate margins with adjustments
    home_margin = home_scoring_adj_value - away_conceding
    away_margin = away_scoring_adj_value - home_conceding
    
    # FIXED BUG: Use pure core principle without extra thresholds
    # Home scores if: Home GF (adjusted) > Away GA
    # Away scores if: Away GF (adjusted) > Home GA
    home_will_score = home_margin > 0
    away_will_score = away_margin > 0
    
    # Calculate confidence based on adjusted margins
    def get_confidence(margin, defense_strength):
        abs_margin = abs(margin)
        
        if defense_strength in ['ELITE', 'STRONG']:
            # Higher threshold for strong defenses for confidence levels only
            if abs_margin > 0.4:
                return 'VERY_HIGH'
            elif abs_margin > 0.2:
                return 'HIGH'
            elif abs_margin > 0.1:
                return 'MEDIUM'
            else:
                return 'LOW'
        else:
            # Standard thresholds for average/weak defenses
            if abs_margin > 0.5:
                return 'VERY_HIGH'
            elif abs_margin > 0.2:
                return 'HIGH'
            elif abs_margin > 0.05:
                return 'MEDIUM'
            else:
                return 'LOW'
    
    home_confidence = get_confidence(home_margin, away_defense)
    away_confidence = get_confidence(away_margin, home_defense)
    
    # Overall confidence
    confidence_levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'VERY_HIGH': 3}
    overall_confidence_level = max(confidence_levels[home_confidence], 
                                  confidence_levels[away_confidence])
    overall_confidence = [k for k, v in confidence_levels.items() 
                         if v == overall_confidence_level][0]
    
    return {
        'home_scores': home_will_score,
        'away_scores': away_will_score,
        'btts': home_will_score and away_will_score,
        'home_margin': home_margin,
        'away_margin': away_margin,
        'home_confidence': home_confidence,
        'away_confidence': away_confidence,
        'overall_confidence': overall_confidence,
        'home_defense_strength': home_defense,
        'away_defense_strength': away_defense,
        'home_adjusted_scoring': home_scoring_adj_value,
        'away_adjusted_scoring': away_scoring_adj_value,
        'expected_total': home_scoring_adj_value + away_scoring_adj_value
    }

def determine_bet_recommendation(predictions):
    """
    Determine betting recommendation based on enhanced predictions.
    """
    
    home_scores = predictions['home_scores']
    away_scores = predictions['away_scores']
    confidence = predictions['overall_confidence']
    expected_total = predictions['expected_total']
    home_defense = predictions['home_defense_strength']
    away_defense = predictions['away_defense_strength']
    
    # Generate reason with defensive strength context
    reason_parts = []
    
    if not home_scores and not away_scores:
        primary_bet = 'UNDER_2.5'
        reason = f"Neither team likely to score "
        if home_defense in ['ELITE', 'STRONG']:
            reason += f"(Home defense: {home_defense}) "
        if away_defense in ['ELITE', 'STRONG']:
            reason += f"(Away defense: {away_defense})"
        reason_parts.append(reason.strip())
        
    elif home_scores and not away_scores:
        primary_bet = 'HOME_TO_SCORE'
        reason = f"Only home team likely to score "
        if away_defense in ['ELITE', 'STRONG']:
            reason += f"(vs {away_defense} away defense)"
        reason_parts.append(reason.strip())
        
    elif not home_scores and away_scores:
        primary_bet = 'AWAY_TO_SCORE'
        reason = f"Only away team likely to score "
        if home_defense in ['ELITE', 'STRONG']:
            reason += f"(vs {home_defense} home defense)"
        reason_parts.append(reason.strip())
        
    else:  # home_scores and away_scores
        primary_bet = 'BTTS_YES'
        reason = f"Both teams likely to score "
        if home_defense in ['ELITE', 'STRONG'] or away_defense in ['ELITE', 'STRONG']:
            reason += f"(despite defensive strengths)"
        reason_parts.append(reason.strip())
    
    # Add expected total info
    reason_parts.append(f"Expected total: {expected_total:.2f} goals")
    
    # Determine secondary bets
    secondary_bets = []
    
    if expected_total > 2.75:
        secondary_bets.append('OVER_2.5')
        if expected_total > 3.25:
            secondary_bets.append('OVER_3.5')
    elif expected_total < 2.25:
        secondary_bets.append('UNDER_2.5')
        if expected_total < 1.75:
            secondary_bets.append('UNDER_1.5')
    
    # Add defensive matchup insights
    if home_defense in ['ELITE', 'STRONG'] and away_defense in ['ELITE', 'STRONG']:
        secondary_bets.append('UNDER_2.5')  # Defensive battle
    
    return {
        'primary_bet': primary_bet,
        'secondary_bets': secondary_bets[:3],  # Limit to top 3
        'confidence': confidence,
        'reason': ' • '.join(reason_parts),
        'home_defense': home_defense,
        'away_defense': away_defense
    }

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("🎯 Enhanced Logic Rules")
    st.markdown("""
    **CORE PRINCIPLE:**
    ```
    Home scores if: Home GF (at home) > Away GA (away)
    Away scores if: Away GF (away) > Home GA (at home)
    ```
    
    **AUTO-ENHANCEMENT:**
    - Detects defensive strength from data
    - Adjusts margins for strong defenses
    - No team database needed
    - Works for ALL leagues/teams
    """)
    
    st.header("🛡️ Defensive Strength Detection")
    st.markdown("""
    **Auto-classification:**
    - **ELITE**: < 0.80 goals conceded/game
    - **STRONG**: 0.80-1.00 goals conceded/game  
    - **AVERAGE**: 1.00-1.80 goals conceded/game
    - **WEAK**: > 1.80 goals conceded/game
    
    **Automatic Adjustments:**
    - Vs ELITE defense: -25% scoring expectation (×0.75)
    - Vs STRONG defense: -15% scoring expectation (×0.85)
    - Vs WEAK defense: +15% scoring expectation (×1.15)
    - Vs AVERAGE defense: No adjustment (×1.00)
    """)
    
    st.header("⚙️ League Settings")
    league_avg = st.number_input(
        "League Average Goals/Game",
        min_value=1.0,
        max_value=4.0,
        value=1.3,
        step=0.1,
        help="Used for defensive strength classification"
    )
    
    st.caption(f"Premier League ≈ 1.3 • Bundesliga ≈ 1.5 • Serie A ≈ 1.2")

# ==================== MAIN INPUT ====================

st.markdown("---")
st.subheader("📊 Match Analysis Input")

# Match Information
st.markdown("#### 🏆 Match Information")
col_info = st.columns([1, 1, 2])
with col_info[0]:
    league = st.text_input("League", value="Premier League", key="league")
with col_info[1]:
    match_date = st.date_input("Match Date", value=datetime.now())

st.markdown("---")

# Team Statistics
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏠 Home Team")
    st.caption("*Last N HOME games*")
    
    home_name = st.text_input("Team Name", value="Rayong FC", key="home_name")
    
    home_matches = st.number_input(
        "Home Games", 
        min_value=1,
        max_value=20,
        value=10,
        step=1,
        key="home_matches"
    )
    
    home_goals_scored = st.number_input(
        "Goals Scored (Home)", 
        min_value=0,
        max_value=100,
        value=11,
        step=1,
        key="home_goals_scored"
    )
    
    home_goals_conceded = st.number_input(
        "Goals Conceded (Home)", 
        min_value=0,
        max_value=100,
        value=6,
        step=1,
        key="home_goals_conceded"
    )
    
    # Auto-display defensive strength
    if home_matches > 0:
        home_conceding_avg = home_goals_conceded / home_matches
        home_def_strength = detect_defensive_strength(home_conceding_avg, home_matches, league_avg)
        st.caption(f"📊 **Defense:** {home_def_strength} ({home_conceding_avg:.2f} conceded/game)")

with col2:
    st.markdown("#### ✈️ Away Team")
    st.caption("*Last N AWAY games*")
    
    away_name = st.text_input("Team Name", value="Ratchaburi", key="away_name")
    
    away_matches = st.number_input(
        "Away Games", 
        min_value=1,
        max_value=20,
        value=10,
        step=1,
        key="away_matches"
    )
    
    away_goals_scored = st.number_input(
        "Goals Scored (Away)", 
        min_value=0,
        max_value=100,
        value=12,
        step=1,
        key="away_goals_scored"
    )
    
    away_goals_conceded = st.number_input(
        "Goals Conceded (Away)", 
        min_value=0,
        max_value=100,
        value=7,
        step=1,
        key="away_goals_conceded"
    )
    
    # Auto-display defensive strength
    if away_matches > 0:
        away_conceding_avg = away_goals_conceded / away_matches
        away_def_strength = detect_defensive_strength(away_conceding_avg, away_matches, league_avg)
        st.caption(f"📊 **Defense:** {away_def_strength} ({away_conceding_avg:.2f} conceded/game)")

# ==================== ODDS INPUT ====================

st.markdown("---")
st.subheader("📈 Market Odds")

odds_cols = st.columns(4)

with odds_cols[0]:
    odds_home_score = st.number_input(
        f"{home_name} to Score", 
        min_value=1.01,
        max_value=10.0,
        value=1.01,
        step=0.01,
        key="odds_home_score"
    )

with odds_cols[1]:
    odds_away_score = st.number_input(
        f"{away_name} to Score", 
        min_value=1.01,
        max_value=10.0,
        value=1.01,
        step=0.01,
        key="odds_away_score"
    )

with odds_cols[2]:
    odds_btts_yes = st.number_input(
        "BTTS Yes", 
        min_value=1.01,
        max_value=10.0,
        value=1.70,
        step=0.01,
        key="odds_btts_yes"
    )

with odds_cols[3]:
    odds_under_25 = st.number_input(
        "Under 2.5 Goals", 
        min_value=1.01,
        max_value=10.0,
        value=2.10,
        step=0.01,
        key="odds_under_25"
    )

# ==================== ANALYSIS ====================

st.markdown("---")
analyze_button = st.button("🔍 Run Enhanced Analysis", type="primary", use_container_width=True)

if analyze_button and home_matches > 0 and away_matches > 0:
    # Calculate averages
    home_scoring = home_goals_scored / home_matches
    home_conceding = home_goals_conceded / home_matches
    away_scoring = away_goals_scored / away_matches
    away_conceding = away_goals_conceded / away_matches
    
    # Run enhanced analysis
    predictions = predict_scoring_enhanced(
        home_scoring, home_conceding, away_scoring, away_conceding,
        home_matches, away_matches, league_avg
    )
    bet_recommendation = determine_bet_recommendation(predictions)
    
    # ==================== RESULTS ====================
    
    st.header("🎯 Enhanced Analysis Results")
    
    # Prediction Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        home_icon = "✅" if predictions['home_scores'] else "❌"
        delta_color = "normal" if predictions['home_margin'] > 0 else "off"
        st.metric(
            f"{home_name} Scores",
            f"{home_icon} {'Yes' if predictions['home_scores'] else 'No'}",
            delta=f"Adj margin: {predictions['home_margin']:.2f}",
            delta_color=delta_color
        )
        st.caption(f"Defense: {predictions['away_defense_strength']}")
    
    with col2:
        away_icon = "✅" if predictions['away_scores'] else "❌"
        delta_color = "normal" if predictions['away_margin'] > 0 else "off"
        st.metric(
            f"{away_name} Scores",
            f"{away_icon} {'Yes' if predictions['away_scores'] else 'No'}",
            delta=f"Adj margin: {predictions['away_margin']:.2f}",
            delta_color=delta_color
        )
        st.caption(f"Defense: {predictions['home_defense_strength']}")
    
    with col3:
        btts_text = "YES" if predictions['btts'] else "NO"
        btts_icon = "✅" if predictions['btts'] else "❌"
        st.metric(
            "Both Teams to Score",
            f"{btts_icon} {btts_text}",
            delta=f"{predictions['overall_confidence'].replace('_', ' ')}"
        )
    
    with col4:
        total_goals = predictions['expected_total']
        over_under = "Over 2.5" if total_goals > 2.5 else "Under 2.5"
        st.metric(
            "Total Goals",
            over_under,
            delta=f"{total_goals:.2f} expected"
        )
    
    # ==================== DEFENSIVE ANALYSIS ====================
    
    st.markdown("---")
    st.subheader("🛡️ Defensive Strength Analysis")
    
    def_col1, def_col2 = st.columns(2)
    
    with def_col1:
        st.markdown(f"#### {home_name} Home Defense")
        strength = predictions['home_defense_strength']
        color = "green" if strength in ['ELITE', 'STRONG'] else "orange" if strength == 'AVERAGE' else "red"
        st.markdown(f"**Strength:** :{color}[{strength}]")
        st.markdown(f"**Avg Conceded:** {home_conceding:.2f} goals/game")
        st.markdown(f"**League Comparison:** {'Better' if home_conceding < league_avg else 'Worse'} than average")
        
        # Recommendation
        if strength in ['ELITE', 'STRONG']:
            st.success(f"✅ Strong home defense - {away_name} may struggle to score")
        elif strength == 'WEAK':
            st.warning(f"⚠️ Weak home defense - {away_name} likely to score")
    
    with def_col2:
        st.markdown(f"#### {away_name} Away Defense")
        strength = predictions['away_defense_strength']
        color = "green" if strength in ['ELITE', 'STRONG'] else "orange" if strength == 'AVERAGE' else "red"
        st.markdown(f"**Strength:** :{color}[{strength}]")
        st.markdown(f"**Avg Conceded:** {away_conceding:.2f} goals/game")
        st.markdown(f"**League Comparison:** {'Better' if away_conceding < league_avg else 'Worse'} than average")
        
        # Recommendation
        if strength in ['ELITE', 'STRONG']:
            st.success(f"✅ Strong away defense - {home_name} may struggle to score")
        elif strength == 'WEAK':
            st.warning(f"⚠️ Weak away defense - {home_name} likely to score")
    
    # ==================== SCORING ADJUSTMENTS ====================
    
    st.markdown("---")
    st.subheader("📈 Scoring Adjustments Applied")
    
    adj_col1, adj_col2 = st.columns(2)
    
    with adj_col1:
        st.markdown(f"#### {home_name} Scoring")
        st.markdown(f"**Raw average:** {home_scoring:.2f} goals/game")
        st.markdown(f"**Vs {away_name} defense ({predictions['away_defense_strength']}):**")
        adj_factor_home = get_adjustment_factor(predictions['away_defense_strength'], True)
        st.markdown(f"**Adjustment factor:** ×{adj_factor_home:.2f}")
        st.markdown(f"**Adjusted expectation:** {predictions['home_adjusted_scoring']:.2f} goals")
        
        # Visual indicator
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predictions['home_adjusted_scoring'],
            title={'text': f"Adjusted Scoring"},
            gauge={'axis': {'range': [0, 3]},
                   'steps': [
                       {'range': [0, 1], 'color': "lightgray"},
                       {'range': [1, 2], 'color': "lightyellow"},
                       {'range': [2, 3], 'color': "lightgreen"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                 'thickness': 0.75,
                                 'value': home_scoring}}  # Raw average line
        ))
        fig1.update_layout(height=200)
        st.plotly_chart(fig1, use_container_width=True)
    
    with adj_col2:
        st.markdown(f"#### {away_name} Scoring")
        st.markdown(f"**Raw average:** {away_scoring:.2f} goals/game")
        st.markdown(f"**Vs {home_name} defense ({predictions['home_defense_strength']}):**")
        adj_factor_away = get_adjustment_factor(predictions['home_defense_strength'], False)
        st.markdown(f"**Adjustment factor:** ×{adj_factor_away:.2f}")
        st.markdown(f"**Adjusted expectation:** {predictions['away_adjusted_scoring']:.2f} goals")
        
        # Visual indicator
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predictions['away_adjusted_scoring'],
            title={'text': f"Adjusted Scoring"},
            gauge={'axis': {'range': [0, 3]},
                   'steps': [
                       {'range': [0, 1], 'color': "lightgray"},
                       {'range': [1, 2], 'color': "lightyellow"},
                       {'range': [2, 3], 'color': "lightgreen"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                 'thickness': 0.75,
                                 'value': away_scoring}}  # Raw average line
        ))
        fig2.update_layout(height=200)
        st.plotly_chart(fig2, use_container_width=True)
    
    # ==================== VERIFICATION CALCULATIONS ====================
    
    # Show the actual calculation verification
    with st.expander("🔍 Verification Calculations"):
        st.markdown("**Core Principle Verification:**")
        st.markdown(f"**{home_name} (Home) scores if:** Home GF (adjusted) > Away GA")
        st.markdown(f"  {predictions['home_adjusted_scoring']:.2f} > {away_conceding:.2f} = **{predictions['home_adjusted_scoring'] > away_conceding}**")
        st.markdown(f"  Margin: {predictions['home_adjusted_scoring']:.2f} - {away_conceding:.2f} = **{predictions['home_margin']:.2f}**")
        
        st.markdown(f"**{away_name} (Away) scores if:** Away GF (adjusted) > Home GA")
        st.markdown(f"  {predictions['away_adjusted_scoring']:.2f} > {home_conceding:.2f} = **{predictions['away_adjusted_scoring'] > home_conceding}**")
        st.markdown(f"  Margin: {predictions['away_adjusted_scoring']:.2f} - {home_conceding:.2f} = **{predictions['away_margin']:.2f}**")
        
        st.markdown("---")
        st.markdown("**Detailed Calculations:**")
        
        st.markdown(f"**{home_name} (Home):**")
        st.markdown(f"- Raw scoring: {home_scoring:.2f}")
        st.markdown(f"- {away_name} away defense: {predictions['away_defense_strength']}")
        st.markdown(f"- Adjustment factor: ×{adj_factor_home:.2f}")
        st.markdown(f"- Adjusted scoring: {home_scoring:.2f} × {adj_factor_home:.2f} = **{predictions['home_adjusted_scoring']:.2f}**")
        st.markdown(f"- {away_name} conceding away: {away_conceding:.2f}")
        
        st.markdown("---")
        
        st.markdown(f"**{away_name} (Away):**")
        st.markdown(f"- Raw scoring: {away_scoring:.2f}")
        st.markdown(f"- {home_name} home defense: {predictions['home_defense_strength']}")
        st.markdown(f"- Adjustment factor: ×{adj_factor_away:.2f}")
        st.markdown(f"- Adjusted scoring: {away_scoring:.2f} × {adj_factor_away:.2f} = **{predictions['away_adjusted_scoring']:.2f}**")
        st.markdown(f"- {home_name} conceding home: {home_conceding:.2f}")
        
        st.markdown("---")
        
        st.markdown(f"**Expected total goals:** {predictions['home_adjusted_scoring']:.2f} + {predictions['away_adjusted_scoring']:.2f} = **{predictions['expected_total']:.2f}**")
    
    # ==================== BET RECOMMENDATION ====================
    
    st.markdown("---")
    st.subheader("💰 Bet Recommendation")
    
    # Display primary bet
    bet_display = {
        'HOME_TO_SCORE': f"{home_name} to Score",
        'AWAY_TO_SCORE': f"{away_name} to Score",
        'BTTS_YES': 'Both Teams to Score: YES',
        'BTTS_NO': 'Both Teams to Score: NO',
        'UNDER_2.5': 'Under 2.5 Goals',
        'OVER_2.5': 'Over 2.5 Goals'
    }
    
    primary_bet = bet_recommendation['primary_bet']
    confidence = bet_recommendation['confidence']
    
    # Confidence icons
    confidence_icons = {
        'VERY_HIGH': '🔥',
        'HIGH': '✅',
        'MEDIUM': '⚠️',
        'LOW': '🔍'
    }
    
    icon = confidence_icons.get(confidence, '📊')
    
    st.success(f"## {icon} {bet_display.get(primary_bet, primary_bet)}")
    st.caption(f"**{confidence.replace('_', ' ')} Confidence** • {bet_recommendation['reason']}")
    
    # Secondary bets
    if bet_recommendation['secondary_bets']:
        st.markdown("**🎯 Secondary Options:**")
        for sec_bet in bet_recommendation['secondary_bets']:
            st.markdown(f"- {sec_bet.replace('_', ' ')}")
    
    # ==================== COMPARATIVE VISUALIZATION ====================
    
    st.markdown("---")
    st.subheader("📊 Comparative Visualization")
    
    # Create enhanced comparison chart
    categories = ['Scoring', 'Adjusted Scoring', 'Opponent Conceding']
    
    fig = go.Figure(data=[
        go.Bar(name=f'{home_name}', x=categories,
               y=[home_scoring, predictions['home_adjusted_scoring'], away_conceding],
               marker_color='blue'),
        go.Bar(name=f'{away_name}', x=categories,
               y=[away_scoring, predictions['away_adjusted_scoring'], home_conceding],
               marker_color='red')
    ])
    
    fig.update_layout(
        title=f"Enhanced Comparison: Raw vs Adjusted Expectations",
        yaxis_title="Goals per Game",
        barmode='group',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== VALUE CALCULATION ====================
    
    st.markdown("---")
    st.subheader("💰 Value Calculation")
    
    # Get odds for primary bet
    odds_map = {
        'HOME_TO_SCORE': odds_home_score,
        'AWAY_TO_SCORE': odds_away_score,
        'BTTS_YES': odds_btts_yes,
        'BTTS_NO': 2.20,  # Default if not provided
        'UNDER_2.5': odds_under_25,
        'OVER_2.5': 1.90   # Default if not provided
    }
    
    primary_odds = odds_map.get(primary_bet, 0)
    
    # Confidence to probability mapping
    confidence_to_prob = {
        'VERY_HIGH': 0.80,
        'HIGH': 0.70,
        'MEDIUM': 0.60,
        'LOW': 0.55
    }
    
    estimated_prob = confidence_to_prob.get(confidence, 0.5)
    
    # Calculate expected value
    win_return = (primary_odds - 1)
    expected_value = (estimated_prob * win_return) - (1 - estimated_prob)
    
    # Display calculations
    calc_cols = st.columns(4)
    
    with calc_cols[0]:
        stake_pct = 0.01 * (1.5 if confidence == 'VERY_HIGH' else 
                           1.2 if confidence == 'HIGH' else 
                           1.0 if confidence == 'MEDIUM' else 0.5)
        st.metric("Suggested Stake", f"{stake_pct*100:.1f}% of bankroll")
    
    with calc_cols[1]:
        st.metric("Win Probability", f"{estimated_prob*100:.1f}%")
    
    with calc_cols[2]:
        st.metric("Current Odds", f"{primary_odds:.2f}")
    
    with calc_cols[3]:
        ev_color = "normal" if expected_value > 0 else "inverse"
        st.metric("Expected Value", f"{expected_value:.3f}", delta_color=ev_color)
    
    # Value assessment
    fair_odds = 1 / estimated_prob
    if primary_odds > fair_odds:
        st.success(f"✅ **Value Bet**: Odds {primary_odds:.2f} > Fair {fair_odds:.2f}")
    else:
        st.warning(f"⚠️ **No Value**: Odds {primary_odds:.2f} ≤ Fair {fair_odds:.2f}")
    
    # ==================== SYSTEM INSIGHTS ====================
    
    st.markdown("---")
    st.subheader("💡 System Insights")
    
    insight_cols = st.columns(2)
    
    with insight_cols[0]:
        st.markdown("#### 📊 Data Quality")
        
        insights = []
        
        # Sample size
        if home_matches >= 10 and away_matches >= 10:
            insights.append("✅ Excellent sample size (≥10 games)")
        elif home_matches >= 5 and away_matches >= 5:
            insights.append("✅ Adequate sample size (≥5 games)")
        else:
            insights.append("⚠️ Small sample size (<5 games)")
        
        # Defensive data quality
        if predictions['home_defense_strength'] != 'UNKNOWN' and predictions['away_defense_strength'] != 'UNKNOWN':
            insights.append("✅ Reliable defensive strength detection")
        
        # Pattern clarity
        total_margin = abs(predictions['home_margin']) + abs(predictions['away_margin'])
        if total_margin > 1.0:
            insights.append("✅ Strong predictive patterns")
        elif total_margin > 0.5:
            insights.append("📊 Moderate predictive patterns")
        else:
            insights.append("⚠️ Weak predictive patterns")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    
    with insight_cols[1]:
        st.markdown("#### 🎯 Match Dynamics")
        
        dynamics = []
        
        # Defensive matchup
        if (predictions['home_defense_strength'] in ['ELITE', 'STRONG'] and 
            predictions['away_defense_strength'] in ['ELITE', 'STRONG']):
            dynamics.append("⚔️ **Defensive battle** - Low scoring likely")
        elif (predictions['home_defense_strength'] in ['WEAK'] and 
              predictions['away_defense_strength'] in ['WEAK']):
            dynamics.append("🔥 **Attacking fest** - High scoring likely")
        
        # Home advantage
        home_advantage = home_scoring - away_scoring
        if home_advantage > 0.5:
            dynamics.append(f"🏠 **Strong home advantage** (+{home_advantage:.2f})")
        elif home_advantage < -0.5:
            dynamics.append(f"✈️ **Strong away advantage** ({home_advantage:.2f})")
        
        # Expected tempo
        expected_total = predictions['expected_total']
        if expected_total > 3.0:
            dynamics.append("⚡ **Fast tempo** - Many chances expected")
        elif expected_total < 2.0:
            dynamics.append("🐌 **Slow tempo** - Few chances expected")
        
        if dynamics:
            for dynamic in dynamics:
                st.markdown(f"- {dynamic}")
        else:
            st.markdown("- ⚖️ **Balanced match** - Could go either way")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Enhanced Comparative Betting System</strong> - Automatic Defensive Strength Detection</p>
    <p><small>Works for ALL teams • No database needed • Self-adjusting logic</small></p>
    <p><small>Bet responsibly • Track all bets • Never bet more than you can afford to lose</small></p>
</div>
""", unsafe_allow_html=True)

# ==================== SAMPLE SCENARIOS ====================

with st.expander("📋 Test Different Scenarios"):
    st.markdown("Test how the system handles different defensive matchups:")
    
    scenarios = {
        "Elite Defense vs Strong Attack": {
            "description": "Top defense faces potent attack",
            "home_goals_scored": 20,  # Strong attack
            "home_goals_conceded": 6,  # Elite defense (0.6/game)
            "away_goals_scored": 18,   # Strong attack
            "away_goals_conceded": 8   # Elite defense (0.8/game)
        },
        "Weak Defense vs Weak Attack": {
            "description": "Both teams struggle defensively and offensively",
            "home_goals_scored": 8,    # Weak attack
            "home_goals_conceded": 20, # Weak defense (2.0/game)
            "away_goals_scored": 9,    # Weak attack  
            "away_goals_conceded": 19  # Weak defense (1.9/game)
        },
        "Balanced Matchup": {
            "description": "Average teams facing each other",
            "home_goals_scored": 13,   # Average (1.3/game)
            "home_goals_conceded": 13, # Average (1.3/game)
            "away_goals_scored": 12,   # Average (1.2/game)
            "away_goals_conceded": 14  # Average (1.4/game)
        },
        "Home Dominance": {
            "description": "Strong home team vs weak away team",
            "home_goals_scored": 22,   # Very strong (2.2/game)
            "home_goals_conceded": 9,  # Strong defense (0.9/game)
            "away_goals_scored": 7,    # Weak attack (0.7/game)
            "away_goals_conceded": 21  # Weak defense (2.1/game)
        }
    }
    
    selected_scenario = st.selectbox("Choose scenario:", list(scenarios.keys()))
    
    if st.button("Load Scenario"):
        scenario = scenarios[selected_scenario]
        st.session_state.home_goals_scored = scenario["home_goals_scored"]
        st.session_state.home_goals_conceded = scenario["home_goals_conceded"]
        st.session_state.away_goals_scored = scenario["away_goals_scored"]
        st.session_state.away_goals_conceded = scenario["away_goals_conceded"]
        
        st.info(f"**{selected_scenario}**: {scenario['description']}")
        st.info("Set 'Home Games' and 'Away Games' to 10 for correct averages")
        st.rerun()
