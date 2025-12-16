"""
Enhanced Comparative Betting System - RAW LOGIC VERSION
Core Principle Preserved: GF > GA determines predictions
Enhancements provide context only, never flip predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Enhanced Betting System",
    page_icon="🎯",
    layout="wide"
)

# CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 0.5rem;
    }
    .prediction-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-left: 5px solid;
    }
    .yes-box {
        border-left-color: #4CAF50;
    }
    .no-box {
        border-left-color: #f44336;
    }
    .confidence-high {
        color: #4CAF50;
        font-weight: bold;
    }
    .confidence-medium {
        color: #FF9800;
        font-weight: bold;
    }
    .confidence-low {
        color: #f44336;
        font-weight: bold;
    }
    .team-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Core System Logic - NEVER CHANGES
def raw_logic_prediction(team_gf, opponent_ga):
    """Core prediction logic: Team scores if GF > GA"""
    return team_gf > opponent_ga

def calculate_confidence(margin):
    """Calculate confidence based on margin only"""
    if margin > 0.5:
        return "VERY HIGH", "confidence-high"
    elif margin > 0.2:
        return "HIGH", "confidence-high"
    elif margin > 0:
        return "MEDIUM", "confidence-medium"
    elif margin > -0.2:
        return "LOW", "confidence-low"
    else:
        return "VERY LOW", "confidence-low"

def get_defense_strength(ga_per_game):
    """Classify defense strength for context only"""
    if ga_per_game < 0.80:
        return "ELITE", "🔵"
    elif ga_per_game < 1.00:
        return "STRONG", "🟢"
    elif ga_per_game < 1.80:
        return "AVERAGE", "🟡"
    else:
        return "WEAK", "🔴"

def get_defense_context(strength, is_home=True):
    """Get context note about facing defense"""
    context_map = {
        "ELITE": "Very challenging - needs exceptional efficiency",
        "STRONG": "Challenging - needs good conversion",
        "AVERAGE": "Normal defensive challenge",
        "WEAK": "Favorable opportunity - defense vulnerable"
    }
    side = "home" if is_home else "away"
    return f"Facing {strength} {side} defense: {context_map.get(strength, '')}"

# League context for reality check
LEAGUE_AVERAGES = {
    "Premier League": 2.8,
    "Bundesliga": 3.2,
    "Serie A": 2.6,
    "La Liga": 2.5,
    "Ligue 1": 2.7,
    "Turkiye": 2.8,
    "Switzerland": 2.9,
    "Belgium-Challenger": 2.7,
    "Wales": 2.6,
    "Thai League": 2.9,
    "Default": 2.7
}

def get_league_context(expected_total, league_name):
    """Add league context note"""
    league_avg = LEAGUE_AVERAGES.get(league_name, LEAGUE_AVERAGES["Default"])
    
    if expected_total < (league_avg * 0.6):
        return f"⚠️ Predicted total ({expected_total:.1f}) significantly below {league_name} average ({league_avg})"
    elif expected_total < (league_avg * 0.8):
        return f"📉 Predicted total ({expected_total:.1f}) below {league_name} average ({league_avg})"
    elif expected_total > (league_avg * 1.4):
        return f"🔥 Predicted total ({expected_total:.1f}) significantly above {league_name} average ({league_avg})"
    elif expected_total > (league_avg * 1.2):
        return f"📈 Predicted total ({expected_total:.1f}) above {league_name} average ({league_avg})"
    else:
        return f"📊 Predicted total ({expected_total:.1f}) aligns with {league_name} average ({league_avg})"

def calculate_value_bet(probability, current_odds, min_value=1.15):
    """Calculate if bet has value"""
    fair_odds = 1 / probability
    value_ratio = current_odds / fair_odds
    has_value = value_ratio >= min_value
    
    return {
        "fair_odds": round(fair_odds, 2),
        "value_ratio": round(value_ratio, 2),
        "has_value": has_value,
        "stake_pct": min(2.0, max(0.5, probability * 2))  # 0.5% to 2% based on probability
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Enhanced Comparative Betting System</h1>', unsafe_allow_html=True)
    st.markdown("**RAW LOGIC VERSION** - GF > GA determines all predictions | Defensive context informs only")
    
    # Sidebar for match input
    with st.sidebar:
        st.header("📊 Match Analysis Input")
        
        # Match info
        league = st.selectbox(
            "League",
            ["Premier League", "Bundesliga", "Serie A", "La Liga", "Ligue 1", 
             "Turkiye", "Switzerland", "Belgium-Challenger", "Wales", "Thai League", "Other"]
        )
        
        match_date = st.date_input("Match Date", datetime.now())
        
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Soma Spor")
        home_games = st.number_input("Home Games (Last N)", min_value=1, max_value=20, value=10)
        home_gf = st.number_input("Goals Scored (Home)", min_value=0.0, value=4.0, step=0.1)
        home_ga = st.number_input("Goals Conceded (Home)", min_value=0.0, value=20.0, step=0.1)
        
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Team Name ", "Bursaspor")
        away_games = st.number_input("Away Games (Last N)", min_value=1, max_value=20, value=10)
        away_gf = st.number_input("Goals Scored (Away)", min_value=0.0, value=21.0, step=0.1)
        away_ga = st.number_input("Goals Conceded (Away)", min_value=0.0, value=8.0, step=0.1)
        
        st.subheader("📈 Market Odds")
        home_score_odds = st.number_input(f"{home_team} to Score", min_value=1.01, value=1.30, step=0.01)
        away_score_odds = st.number_input(f"{away_team} to Score", min_value=1.01, value=1.17, step=0.01)
        btts_yes_odds = st.number_input("BTTS Yes", min_value=1.01, value=1.88, step=0.01)
        under_25_odds = st.number_input("Under 2.5 Goals", min_value=1.01, value=2.90, step=0.01)
        
        analyze_button = st.button("🎯 Run Enhanced Analysis", type="primary")
    
    if not analyze_button:
        st.info("👈 Enter match data in the sidebar and click 'Run Enhanced Analysis'")
        return
    
    # Calculate averages per game
    home_gf_avg = home_gf / home_games
    home_ga_avg = home_ga / home_games
    away_gf_avg = away_gf / away_games
    away_ga_avg = away_ga / away_games
    
    # Get defensive strength (for context only)
    home_def_strength, home_def_emoji = get_defense_strength(home_ga_avg)
    away_def_strength, away_def_emoji = get_defense_strength(away_ga_avg)
    
    # RAW LOGIC PREDICTIONS (NEVER ADJUSTED)
    home_scores_raw = raw_logic_prediction(home_gf_avg, away_ga_avg)
    away_scores_raw = raw_logic_prediction(away_gf_avg, home_ga_avg)
    
    # Calculate margins
    home_margin = home_gf_avg - away_ga_avg
    away_margin = away_gf_avg - home_ga_avg
    
    # Get confidence levels
    home_conf, home_conf_class = calculate_confidence(home_margin)
    away_conf, away_conf_class = calculate_confidence(away_margin)
    
    # Expected goals (simple average)
    expected_total = home_gf_avg + away_gf_avg
    over_under = "Over 2.5" if expected_total > 2.5 else "Under 2.5"
    
    # BTTS prediction
    btts_prediction = home_scores_raw and away_scores_raw
    btts_probability = min(0.95, max(0.05, (home_gf_avg / away_ga_avg * away_gf_avg / home_ga_avg) * 0.7))
    
    # Display results in main area
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<h3 class="sub-header">🏆 Match Information</h3>', unsafe_allow_html=True)
        st.info(f"**League:** {league}  \n**Date:** {match_date.strftime('%Y/%m/%d')}")
        
        # Home Team Card
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### 🏠 {home_team}")
        st.write(f"**Last {home_games} HOME games:**")
        st.write(f"- Goals Scored: **{home_gf}** ({home_gf_avg:.2f}/game)")
        st.write(f"- Goals Conceded: **{home_ga}** ({home_ga_avg:.2f}/game)")
        st.markdown(f"**Defense:** {home_def_emoji} {home_def_strength} ({home_ga_avg:.2f} conceded/game)")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Away Team Card
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### ✈️ {away_team}")
        st.write(f"**Last {away_games} AWAY games:**")
        st.write(f"- Goals Scored: **{away_gf}** ({away_gf_avg:.2f}/game)")
        st.write(f"- Goals Conceded: **{away_ga}** ({away_ga_avg:.2f}/game)")
        st.markdown(f"**Defense:** {away_def_emoji} {away_def_strength} ({away_ga_avg:.2f} conceded/game)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<h3 class="sub-header">🎯 Enhanced Analysis Results</h3>', unsafe_allow_html=True)
        
        # Home Scores Prediction
        box_class = "yes-box" if home_scores_raw else "no-box"
        result_emoji = "✅" if home_scores_raw else "❌"
        
        st.markdown(f'<div class="prediction-box {box_class}">', unsafe_allow_html=True)
        st.markdown(f"### {home_team} Scores: {result_emoji} {'YES' if home_scores_raw else 'NO'}")
        st.markdown(f"**Raw logic:** {home_gf_avg:.2f} GF vs {away_ga_avg:.2f} GA → Margin: {home_margin:+.2f}")
        st.markdown(f"**Confidence:** <span class='{home_conf_class}'>{home_conf}</span>", unsafe_allow_html=True)
        st.markdown(f"**Note:** {get_defense_context(away_def_strength, is_home=False)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Away Scores Prediction
        box_class = "yes-box" if away_scores_raw else "no-box"
        result_emoji = "✅" if away_scores_raw else "❌"
        
        st.markdown(f'<div class="prediction-box {box_class}">', unsafe_allow_html=True)
        st.markdown(f"### {away_team} Scores: {result_emoji} {'YES' if away_scores_raw else 'NO'}")
        st.markdown(f"**Raw logic:** {away_gf_avg:.2f} GF vs {home_ga_avg:.2f} GA → Margin: {away_margin:+.2f}")
        st.markdown(f"**Confidence:** <span class='{away_conf_class}'>{away_conf}</span>", unsafe_allow_html=True)
        st.markdown(f"**Note:** {get_defense_context(home_def_strength, is_home=True)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # BTTS Prediction
        btts_box_class = "yes-box" if btts_prediction else "no-box"
        btts_emoji = "✅" if btts_prediction else "❌"
        
        st.markdown(f'<div class="prediction-box {btts_box_class}">', unsafe_allow_html=True)
        st.markdown(f"### Both Teams to Score: {btts_emoji} {'YES' if btts_prediction else 'NO'}")
        st.markdown(f"**Probability:** {btts_probability:.1%}")
        
        # Value bet calculation for BTTS
        btts_value = calculate_value_bet(btts_probability, btts_yes_odds)
        if btts_value["has_value"]:
            st.success(f"✅ **VALUE BET** | Fair odds: {btts_value['fair_odds']:.2f} | Current: {btts_yes_odds}")
            st.info(f"**Suggested stake:** {btts_value['stake_pct']:.1f}% of bankroll")
        else:
            st.warning(f"⚠️ **NO VALUE** | Fair odds: {btts_value['fair_odds']:.2f} | Current: {btts_yes_odds}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Total Goals
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.markdown(f"### Total Goals: **{over_under}**")
        st.markdown(f"**Expected:** {expected_total:.2f} goals")
        st.markdown(f"**League context:** {get_league_context(expected_total, league)}")
        
        # Over/Under value
        over_probability = 0.65 if expected_total > 2.5 else 0.35
        under_odds_value = calculate_value_bet(1 - over_probability, under_25_odds)
        
        if expected_total > 2.5:
            st.info(f"📈 Expected high scoring: {home_gf_avg:.1f} + {away_gf_avg:.1f} = {expected_total:.1f}")
            if btts_prediction:
                st.success("✅ Both teams scoring supports Over 2.5")
        else:
            st.info(f"📉 Expected low scoring: {home_gf_avg:.1f} + {away_gf_avg:.1f} = {expected_total:.1f}")
            if not btts_prediction:
                st.success("✅ Single team scoring supports Under 2.5")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Defensive Strength Analysis
    st.markdown(f'<h3 class="sub-header">🛡️ Defensive Strength Analysis (Context Only)</h3>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"##### {home_team} Home Defense")
        st.write(f"**Strength:** {home_def_emoji} {home_def_strength}")
        st.write(f"**Avg Conceded:** {home_ga_avg:.2f} goals/game")
        if home_def_strength in ["ELITE", "STRONG"]:
            st.success(f"✅ Strong home defense - {away_team} may struggle to score")
        elif home_def_strength == "WEAK":
            st.error(f"⚠️ Weak home defense - {away_team} has favorable conditions")
        else:
            st.info(f"📊 Average home defense - normal conditions")
    
    with col4:
        st.markdown(f"##### {away_team} Away Defense")
        st.write(f"**Strength:** {away_def_emoji} {away_def_strength}")
        st.write(f"**Avg Conceded:** {away_ga_avg:.2f} goals/game")
        if away_def_strength in ["ELITE", "STRONG"]:
            st.success(f"✅ Strong away defense - {home_team} may struggle to score")
        elif away_def_strength == "WEAK":
            st.error(f"⚠️ Weak away defense - {home_team} has favorable conditions")
        else:
            st.info(f"📊 Average away defense - normal conditions")
    
    # System Insights
    st.markdown(f'<h3 class="sub-header">💡 System Insights</h3>', unsafe_allow_html=True)
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("##### 📊 Data Quality")
        if home_games >= 10 and away_games >= 10:
            st.success("✅ Excellent sample size (≥10 games)")
        elif home_games >= 5 and away_games >= 5:
            st.warning("⚠️ Moderate sample size (5-9 games)")
        else:
            st.error("❌ Small sample size (<5 games)")
        
        st.info("✅ Raw logic preserved - no prediction adjustments")
        st.info("✅ Defensive strength provides context only")
    
    with insights_col2:
        st.markdown("##### 🎯 Match Dynamics")
        
        # Match tempo
        total_gf_avg = (home_gf_avg + away_gf_avg) / 2
        if total_gf_avg > 2.0:
            st.success("🔥 Attacking match expected")
        elif total_gf_avg > 1.5:
            st.info("⚖️ Balanced match expected")
        else:
            st.warning("🐌 Low tempo expected")
        
        # Home advantage
        home_advantage = home_gf_avg - away_gf_avg
        if home_advantage > 0.5:
            st.success(f"🏠 Strong home advantage (+{home_advantage:.1f} GF/game)")
        elif home_advantage < -0.5:
            st.warning(f"✈️ Strong away advantage ({home_advantage:+.1f} GF/game)")
        
        # Defensive matchup
        if home_def_strength in ["ELITE", "STRONG"] and away_def_strength in ["ELITE", "STRONG"]:
            st.info("⚔️ Defensive battle likely")
        elif home_def_strength == "WEAK" and away_def_strength == "WEAK":
            st.success("🎯 High-scoring game likely")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 🔒 System Principles:
    1. **Predictions based SOLELY on raw GF > GA logic**
    2. **Defensive strength provides context only - never flips predictions**
    3. **Confidence levels inform stake size, not prediction validity**
    4. **League context used for reality checks only**
    
    *Bet responsibly • Track all bets • Never bet more than you can afford to lose*
    """)

if __name__ == "__main__":
    main()
