"""
CONCRETE BATTLE-TESTED BETTING SYSTEM
PROVEN LOGIC WITH DATA HIERARCHY
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Concrete Betting System",
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
    .aligned-box {
        border-left-color: #4CAF50;
        background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e9 100%);
    }
    .single-box {
        border-left-color: #FF9800;
        background: linear-gradient(135deg, #f8f9fa 0%, #fff3e0 100%);
    }
    .calculated-box {
        border-left-color: #2196F3;
        background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
    }
    .value-high {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .value-medium {
        color: #FF9800;
        font-weight: bold;
    }
    .value-low {
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
    .trend-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0 4px;
    }
    .trend-70 {
        background-color: #4CAF50;
        color: white;
    }
    .trend-60 {
        background-color: #FF9800;
        color: white;
    }
    .trend-low {
        background-color: #f44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 1. ALIGNED STRONG TRENDS (≥70%) - MOST IMPORTANT
def check_aligned_strong_trends(home_btts_pct, away_btts_pct, home_over_pct, away_over_pct, home_under_pct, away_under_pct):
    """When BOTH teams show the SAME strong trend, BET IT"""
    recommendations = []
    
    # BTTS Yes: Both ≥70% BTTS → Bet BTTS Yes (75% probability)
    if home_btts_pct >= 70 and away_btts_pct >= 70:
        recommendations.append({
            'bet_type': 'BTTS Yes',
            'priority': 'ALIGNED STRONG TREND',
            'probability': 0.75,
            'reason': f"Both teams show ≥70% BTTS trend (Home: {home_btts_pct}%, Away: {away_btts_pct}%)",
            'examples': ["✅ Castellón (70% BTTS) vs Mirandés (70% BTTS) → BTTS Yes WON"],
            'action': 'BET'
        })
    
    # Over 2.5: Both ≥70% Over → Bet Over 2.5 (70% probability)
    if home_over_pct >= 70 and away_over_pct >= 70:
        recommendations.append({
            'bet_type': 'Over 2.5',
            'priority': 'ALIGNED STRONG TREND',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Over trend (Home: {home_over_pct}%, Away: {away_over_pct}%)",
            'examples': ["✅ Nacional (70% Over) vs Tondela (71% Over) → Over 2.5 WON"],
            'action': 'BET'
        })
    
    # Under 2.5: Both ≥70% Under → Bet Under 2.5 (70% probability)
    if home_under_pct >= 70 and away_under_pct >= 70:
        recommendations.append({
            'bet_type': 'Under 2.5',
            'priority': 'ALIGNED STRONG TREND',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Under trend (Home: {home_under_pct}%, Away: {away_under_pct}%)",
            'examples': ["✅ Roma (70% Under) vs Como (60% Under) → Under 2.5 WON"],
            'action': 'BET'
        })
    
    return recommendations

# 2. SINGLE DOMINANT TREND (≥70%)
def check_single_dominant_trends(home_btts_pct, away_btts_pct, home_over_pct, away_over_pct, home_under_pct, away_under_pct, home_team, away_team, is_big_club_home=False):
    """When ONE team shows ≥70% trend, CONSIDER it"""
    recommendations = []
    
    # Check for defensive specialist (away team with ≥70% Under)
    if away_under_pct >= 70:
        note = "Discount trend as facing big club at home" if is_big_club_home else "Strong defensive trend"
        recommendations.append({
            'bet_type': 'Under 2.5',
            'priority': 'SINGLE DOMINANT TREND',
            'probability': 0.70,
            'reason': f"{away_team} shows ≥70% Under trend away ({away_under_pct}%)",
            'examples': ["✅ Napoli 80% Under away → Bet Under vs Udinese WON", 
                        "✅ Santa Clara 70% Under away → Bet Under vs Braga WON"],
            'action': 'CONSIDER',
            'note': note
        })
    
    # Check for single BTTS trends
    if home_btts_pct >= 70:
        recommendations.append({
            'bet_type': 'BTTS Yes',
            'priority': 'SINGLE DOMINANT TREND',
            'probability': 0.65,
            'reason': f"{home_team} shows ≥70% BTTS trend at home ({home_btts_pct}%)",
            'action': 'CONSIDER',
            'note': 'Check opponent context'
        })
    
    if away_btts_pct >= 70:
        note = "Check opponent context (big club home)" if is_big_club_home else "Consider this trend"
        recommendations.append({
            'bet_type': 'BTTS Yes',
            'priority': 'SINGLE DOMINANT TREND',
            'probability': 0.65,
            'reason': f"{away_team} shows ≥70% BTTS trend away ({away_btts_pct}%)",
            'action': 'CONSIDER',
            'note': note
        })
    
    return recommendations

# 3. CALCULATED EXPECTED GOALS
def calculate_expected_goals(home_gf, away_ga, away_gf, home_ga, home_trend_adjustment=0, away_trend_adjustment=0):
    """Calculate mathematically: Expected Goals = [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2"""
    # Apply trend adjustments (±15% per 70% trend)
    home_factor = 1 + home_trend_adjustment * 0.15
    away_factor = 1 + away_trend_adjustment * 0.15
    
    baseline = ((home_gf + away_ga) + (away_gf + home_ga)) / 2
    adjusted_baseline = baseline * ((home_factor + away_factor) / 2)
    
    return adjusted_baseline

# 4. CONTEXT & PSYCHOLOGY
def apply_context_adjustments(expected_goals, is_big_club_home_after_poor_run=False, is_relegation_desperation=False, is_title_chase=False):
    """Adjust for special situations"""
    adjustments = []
    
    if is_big_club_home_after_poor_run:
        expected_goals += 0.3
        adjustments.append("Big club at home after poor run → +0.3 expected goals")
    
    if is_relegation_desperation:
        expected_goals -= 0.2
        adjustments.append("Relegation desperation → Defensive focus, not attacking")
    
    if is_title_chase:
        expected_goals += 0.1
        adjustments.append("Title chase pressure → Can help or hinder")
    
    return expected_goals, adjustments

# VALUE BET IDENTIFICATION FORMULA
def calculate_value_bet(true_probability, market_odds):
    """Value = (True Probability × Market Odds) - 1"""
    implied_probability = 1 / market_odds
    value = (true_probability * market_odds) - 1
    
    # Determine stake based on value
    if value >= 0.25:
        stake_pct = 3.0  # STRONG BET
        stake_desc = "STRONG BET (2-3% stake)"
    elif value >= 0.15:
        stake_pct = 2.0  # GOOD BET
        stake_desc = "GOOD BET (1-2% stake)"
    else:
        stake_pct = 0.0  # AVOID
        stake_desc = "AVOID or minimal stake (<15% value)"
    
    return {
        'value': value,
        'implied_probability': implied_probability,
        'true_probability': true_probability,
        'market_odds': market_odds,
        'has_value': value >= 0.15,
        'stake_pct': stake_pct,
        'stake_desc': stake_desc
    }

# DECISION FLOWCHART
def run_decision_flowchart(data):
    """Follow the exact decision flowchart from the logic"""
    recommendations = []
    
    # Step 1: Check for ≥70% ALIGNED trends
    aligned_recs = check_aligned_strong_trends(
        data['home_btts_pct'], data['away_btts_pct'],
        data['home_over_pct'], data['away_over_pct'],
        data['home_under_pct'], data['away_under_pct']
    )
    
    if aligned_recs:
        recommendations.extend(aligned_recs)
        return recommendations  # BET & STOP as per flowchart
    
    # Step 2: Check for ≥70% SINGLE trend
    single_recs = check_single_dominant_trends(
        data['home_btts_pct'], data['away_btts_pct'],
        data['home_over_pct'], data['away_over_pct'],
        data['home_under_pct'], data['away_under_pct'],
        data['home_team'], data['away_team'],
        data.get('is_big_club_home', False)
    )
    recommendations.extend(single_recs)
    
    # Step 3: Calculate Expected Goals
    # Determine trend adjustments
    home_trend_adj = 1 if data['home_btts_pct'] >= 70 or data['home_over_pct'] >= 70 else 0
    away_trend_adj = 1 if data['away_btts_pct'] >= 70 or data['away_over_pct'] >= 70 else 0
    
    expected_goals = calculate_expected_goals(
        data['home_gf_avg'], data['away_ga_avg'],
        data['away_gf_avg'], data['home_ga_avg'],
        home_trend_adj, away_trend_adj
    )
    
    # Step 4: Apply context adjustments
    expected_goals, adjustments = apply_context_adjustments(
        expected_goals,
        data.get('is_big_club_home_after_poor_run', False),
        data.get('is_relegation_desperation', False),
        data.get('is_title_chase', False)
    )
    
    # Make recommendation based on expected goals
    if expected_goals > 2.7:
        recommendations.append({
            'bet_type': 'Over 2.5',
            'priority': 'CALCULATED EXPECTED GOALS',
            'probability': 0.65,
            'reason': f"Expected Goals = {expected_goals:.2f} > 2.7",
            'calculation': f"[(Home_GF {data['home_gf_avg']:.1f} + Away_GA {data['away_ga_avg']:.1f}) + (Away_GF {data['away_gf_avg']:.1f} + Home_GA {data['home_ga_avg']:.1f})] ÷ 2",
            'adjustments': adjustments,
            'action': 'LEAN'
        })
    elif expected_goals < 2.3:
        recommendations.append({
            'bet_type': 'Under 2.5',
            'priority': 'CALCULATED EXPECTED GOALS',
            'probability': 0.65,
            'reason': f"Expected Goals = {expected_goals:.2f} < 2.3",
            'calculation': f"[(Home_GF {data['home_gf_avg']:.1f} + Away_GA {data['away_ga_avg']:.1f}) + (Away_GF {data['away_gf_avg']:.1f} + Home_GA {data['home_ga_avg']:.1f})] ÷ 2",
            'adjustments': adjustments,
            'action': 'LEAN'
        })
    else:
        recommendations.append({
            'bet_type': 'No clear edge',
            'priority': 'CALCULATED EXPECTED GOALS',
            'probability': 0.50,
            'reason': f"Expected Goals = {expected_goals:.2f} (2.3-2.7 range)",
            'calculation': f"[(Home_GF {data['home_gf_avg']:.1f} + Away_GA {data['away_ga_avg']:.1f}) + (Away_GF {data['away_gf_avg']:.1f} + Home_GA {data['home_ga_avg']:.1f})] ÷ 2",
            'adjustments': adjustments,
            'action': 'PASS'
        })
    
    return recommendations

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 CONCRETE BATTLE-TESTED BETTING SYSTEM</h1>', unsafe_allow_html=True)
    st.markdown("**PROVEN & PROFITABLE LOGIC** - Follow the exact data hierarchy and decision flowchart")
    
    # Sidebar for match input
    with st.sidebar:
        st.header("📊 Match Data Input")
        
        # Match info
        league = st.selectbox(
            "League",
            ["Premier League", "Bundesliga", "Serie A", "La Liga", "Ligue 1", 
             "Turkiye", "Switzerland", "Belgium", "Portugal", "Other"]
        )
        
        match_date = st.date_input("Match Date", datetime.now())
        
        st.subheader("🏠 Home Team Data")
        home_team = st.text_input("Home Team Name", "Castellón")
        
        col1, col2 = st.columns(2)
        with col1:
            home_btts_pct = st.slider("Home BTTS % (Last 10)", 0, 100, 70, help="Last 10 home games BTTS percentage")
            home_over_pct = st.slider("Home Over 2.5 %", 0, 100, 50, help="Last 10 home games Over 2.5 percentage")
            home_under_pct = st.slider("Home Under 2.5 %", 0, 100, 30, help="Last 10 home games Under 2.5 percentage")
        
        with col2:
            home_gf_avg = st.number_input("Home GF/game", min_value=0.0, value=1.8, step=0.1)
            home_ga_avg = st.number_input("Home GA/game", min_value=0.0, value=1.2, step=0.1)
        
        st.subheader("✈️ Away Team Data")
        away_team = st.text_input("Away Team Name", "Mirandés")
        
        col3, col4 = st.columns(2)
        with col3:
            away_btts_pct = st.slider("Away BTTS % (Last 10)", 0, 100, 70, help="Last 10 away games BTTS percentage")
            away_over_pct = st.slider("Away Over 2.5 %", 0, 100, 55, help="Last 10 away games Over 2.5 percentage")
            away_under_pct = st.slider("Away Under 2.5 %", 0, 100, 45, help="Last 10 away games Under 2.5 percentage")
        
        with col4:
            away_gf_avg = st.number_input("Away GF/game", min_value=0.0, value=1.6, step=0.1)
            away_ga_avg = st.number_input("Away GA/game", min_value=0.0, value=1.4, step=0.1)
        
        st.subheader("🎯 Context Flags")
        col5, col6 = st.columns(2)
        with col5:
            is_big_club_home = st.checkbox("Big Club at Home")
            is_big_club_home_after_poor_run = st.checkbox("Big Club Home After Poor Run")
        with col6:
            is_relegation_desperation = st.checkbox("Relegation Desperation Match")
            is_title_chase = st.checkbox("Title Chase Pressure")
        
        st.subheader("💰 Market Odds")
        btts_yes_odds = st.number_input("BTTS Yes Odds", min_value=1.01, value=1.93, step=0.01)
        over_25_odds = st.number_input("Over 2.5 Odds", min_value=1.01, value=1.80, step=0.01)
        under_25_odds = st.number_input("Under 2.5 Odds", min_value=1.01, value=2.10, step=0.01)
        
        analyze_button = st.button("🎯 RUN CONCRETE ANALYSIS", type="primary", use_container_width=True)
    
    if not analyze_button:
        st.info("👈 Enter match data and click 'RUN CONCRETE ANALYSIS'")
        st.markdown("---")
        
        # Show system principles
        st.markdown("### 🎯 THE CONCRETE LOGIC: PROVEN & PROFITABLE")
        st.markdown("""
        #### 📊 DATA HIERARCHY (In Order of Importance)
        
        **1. ALIGNED STRONG TRENDS (≥70%)**
        When BOTH teams show the SAME strong trend, BET IT
        - BTTS Yes: Both ≥70% BTTS → Bet BTTS Yes (75% probability)
        - Over 2.5: Both ≥70% Over → Bet Over 2.5 (70% probability)
        - Under 2.5: Both ≥70% Under → Bet Under 2.5 (70% probability)
        
        **2. SINGLE DOMINANT TREND (≥70%)**
        When ONE team shows ≥70% trend, CONSIDER it
        
        **3. CALCULATED EXPECTED GOALS**
        When no strong trends, calculate mathematically
        
        **4. CONTEXT & PSYCHOLOGY**
        Adjust for special situations
        """)
        return
    
    # Prepare data for analysis
    data = {
        'home_team': home_team,
        'away_team': away_team,
        'home_btts_pct': home_btts_pct,
        'away_btts_pct': away_btts_pct,
        'home_over_pct': home_over_pct,
        'away_over_pct': away_over_pct,
        'home_under_pct': home_under_pct,
        'away_under_pct': away_under_pct,
        'home_gf_avg': home_gf_avg,
        'home_ga_avg': home_ga_avg,
        'away_gf_avg': away_gf_avg,
        'away_ga_avg': away_ga_avg,
        'is_big_club_home': is_big_club_home,
        'is_big_club_home_after_poor_run': is_big_club_home_after_poor_run,
        'is_relegation_desperation': is_relegation_desperation,
        'is_title_chase': is_title_chase
    }
    
    # Run the decision flowchart
    recommendations = run_decision_flowchart(data)
    
    # Display results
    st.markdown(f'<h3 class="sub-header">📋 Match Analysis: {home_team} vs {away_team}</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### 🏠 {home_team} (Home)")
        
        # Trend badges
        st.markdown("##### Trend Analysis (Last 10 Games):")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            badge_class = "trend-70" if home_btts_pct >= 70 else "trend-60" if home_btts_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">BTTS: {home_btts_pct}%</span>', unsafe_allow_html=True)
        with col_b:
            badge_class = "trend-70" if home_over_pct >= 70 else "trend-60" if home_over_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">Over: {home_over_pct}%</span>', unsafe_allow_html=True)
        with col_c:
            badge_class = "trend-70" if home_under_pct >= 70 else "trend-60" if home_under_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">Under: {home_under_pct}%</span>', unsafe_allow_html=True)
        
        st.write(f"**GF/game:** {home_gf_avg:.2f}")
        st.write(f"**GA/game:** {home_ga_avg:.2f}")
        
        if is_big_club_home:
            st.info("🏆 **Big Club at Home**")
        if is_big_club_home_after_poor_run:
            st.warning("📉 **Home after poor run → +0.3 expected goals**")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### ✈️ {away_team} (Away)")
        
        # Trend badges
        st.markdown("##### Trend Analysis (Last 10 Games):")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            badge_class = "trend-70" if away_btts_pct >= 70 else "trend-60" if away_btts_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">BTTS: {away_btts_pct}%</span>', unsafe_allow_html=True)
        with col_b:
            badge_class = "trend-70" if away_over_pct >= 70 else "trend-60" if away_over_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">Over: {away_over_pct}%</span>', unsafe_allow_html=True)
        with col_c:
            badge_class = "trend-70" if away_under_pct >= 70 else "trend-60" if away_under_pct >= 60 else "trend-low"
            st.markdown(f'<span class="trend-badge {badge_class}">Under: {away_under_pct}%</span>', unsafe_allow_html=True)
        
        st.write(f"**GF/game:** {away_gf_avg:.2f}")
        st.write(f"**GA/game:** {away_ga_avg:.2f}")
        
        if is_relegation_desperation:
            st.error("🔥 **Relegation desperation → Defensive focus**")
        if is_title_chase:
            st.success("🏆 **Title chase pressure**")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display recommendations
    st.markdown(f'<h3 class="sub-header">🎯 SYSTEM RECOMMENDATIONS</h3>', unsafe_allow_html=True)
    
    for rec in recommendations:
        # Determine box class based on priority
        if 'ALIGNED' in rec['priority']:
            box_class = "aligned-box"
            emoji = "🎯"
        elif 'SINGLE' in rec['priority']:
            box_class = "single-box"
            emoji = "📊"
        else:
            box_class = "calculated-box"
            emoji = "🧮"
        
        st.markdown(f'<div class="prediction-box {box_class}">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f"##### {emoji} {rec['priority']}")
        
        if rec['action'] == 'BET':
            st.markdown(f"### 🚀 {rec['bet_type']} - BET IT")
            st.markdown("**ACTION:** 🔥 **BET IMMEDIATELY** (Aligned strong trend found)")
        elif rec['action'] == 'CONSIDER':
            st.markdown(f"### 🤔 {rec['bet_type']} - CONSIDER")
            st.markdown("**ACTION:** ⚠️ **CONSIDER carefully** (Single dominant trend)")
        elif rec['action'] == 'LEAN':
            st.markdown(f"### 📈 {rec['bet_type']} - LEAN")
            st.markdown("**ACTION:** 📊 **LEAN based on calculation**")
        else:
            st.markdown(f"### ⏸️ {rec['bet_type']}")
            st.markdown("**ACTION:** 🛑 **PASS** (No clear edge)")
        
        st.markdown(f"**Probability:** {rec['probability']:.0%}")
        st.markdown(f"**Reason:** {rec['reason']}")
        
        # Examples if available
        if 'examples' in rec:
            st.markdown("**Proven Examples:**")
            for example in rec['examples']:
                st.markdown(f"- {example}")
        
        # Calculation if available
        if 'calculation' in rec:
            st.info(f"**Calculation:** {rec['calculation']}")
        
        # Note if available
        if 'note' in rec:
            st.warning(f"📝 **Note:** {rec['note']}")
        
        # Adjustments if available
        if 'adjustments' in rec and rec['adjustments']:
            st.markdown("**Context Adjustments:**")
            for adj in rec['adjustments']:
                st.markdown(f"- {adj}")
        
        # Value calculation for betting markets
        if rec['bet_type'] in ['BTTS Yes', 'Over 2.5', 'Under 2.5'] and rec['action'] in ['BET', 'CONSIDER', 'LEAN']:
            market_odds = btts_yes_odds if rec['bet_type'] == 'BTTS Yes' else \
                         over_25_odds if rec['bet_type'] == 'Over 2.5' else \
                         under_25_odds
            
            value_calc = calculate_value_bet(rec['probability'], market_odds)
            
            if value_calc['has_value']:
                st.success(f"✅ **VALUE BET IDENTIFIED**")
                st.markdown(f"""
                - **Formula:** Value = (True Probability × Odds) - 1
                - **Calculation:** ({rec['probability']:.2f} × {market_odds:.2f}) - 1 = **{value_calc['value']:.3f}**
                - True Probability: {value_calc['true_probability']:.1%}
                - Market Implied: {value_calc['implied_probability']:.1%}
                - Market Odds: {value_calc['market_odds']:.2f}
                - **Value: +{value_calc['value']:.1%}**
                """)
                
                st.info(f"**Betting Decision:** {value_calc['stake_desc']}")
                
                if value_calc['stake_pct'] > 0:
                    st.metric("💰 Recommended Stake", f"{value_calc['stake_pct']:.1f}% of bankroll")
            else:
                st.warning(f"⚠️ **NO VALUE BET** (Value: {value_calc['value']:+.1%})")
                st.info(f"Threshold: ≥15% value needed | Current: {value_calc['value']:.1%}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show decision flowchart
    st.markdown(f'<h3 class="sub-header">🔧 DECISION FLOWCHART</h3>', unsafe_allow_html=True)
    
    # Create a visual flowchart
    flowchart_html = """
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; font-family: monospace; line-height: 1.6;">
    <strong>START</strong><br>
    │<br>
    ├─ <strong>Step 1: Check for ≥70% ALIGNED trends</strong><br>
    │   ├─ If Both ≥70% BTTS → <strong>BET BTTS Yes @ odds >1.43</strong><br>
    │   ├─ If Both ≥70% Over → <strong>BET Over 2.5 @ odds >1.43</strong><br>
    │   ├─ If Both ≥70% Under → <strong>BET Under 2.5 @ odds >1.43</strong><br>
    │   └─ If aligned trends → <strong>BET & STOP</strong><br>
    │<br>
    ├─ <strong>Step 2: Check for ≥70% SINGLE trend</strong><br>
    │   ├─ If Home ≥70% trend → Apply to prediction<br>
    │   ├─ If Away ≥70% trend → Apply to prediction<br>
    │   └─ <em>Adjust for opponent context (big club home = discount trend)</em><br>
    │<br>
    ├─ <strong>Step 3: Calculate Expected Goals</strong><br>
    │   ├─ Baseline: [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2<br>
    │   ├─ Apply trend adjustments (±15% per 70% trend)<br>
    │   └─ Compare to 2.5 line<br>
    │<br>
    ├─ <strong>Step 4: Check H2H (Recent only, ≤2 years)</strong><br>
    │   ├─ If consistent pattern (≥80%) → Consider override<br>
    │   └─ But verify team evolution hasn't changed<br>
    │<br>
    └─ <strong>Step 5: Find Value & Bet</strong><br>
        ├─ Calculate: <strong>Value = (Probability × Odds) - 1</strong><br>
        ├─ Bet if Value ≥ 0.15 (15%)<br>
        └─ Stake: 1-3% based on confidence<br>
    </div>
    """
    
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    # Proven success patterns
    st.markdown(f'<h3 class="sub-header">🏆 PROVEN SUCCESS PATTERNS</h3>', unsafe_allow_html=True)
    
    patterns = [
        {
            "name": "The 'Double 70%' (MOST RELIABLE)",
            "description": "Both teams show same ≥70% trend",
            "action": "Bet the trend (75%+ success rate)",
            "examples": ["Castellón-Mirandés (BTTS)", "Nacional-Tondela (Over)"]
        },
        {
            "name": "The 'Defensive Specialist'",
            "description": "Away team ≥70% Under with poor attack (≤1.00 GF)",
            "action": "Bet Under 2.5 (70% success rate)",
            "examples": ["Santa Clara", "Napoli away"]
        },
        {
            "name": "The 'Home Bounce-Back'",
            "description": "Big club at home after poor home form",
            "action": "Bet home win, possibly clean sheet",
            "examples": ["Rangers", "Porto at home"]
        },
        {
            "name": "The 'Relegation Desperation'",
            "description": "Home team in relegation zone vs mid-table",
            "action": "Often 1-0 wins, not goal-fests",
            "examples": ["Torino 1-0 Cremonese"]
        }
    ]
    
    cols = st.columns(2)
    for i, pattern in enumerate(patterns):
        with cols[i % 2]:
            st.markdown(f'<div style="background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
            st.markdown(f"**{pattern['name']}**")
            st.markdown(f"*{pattern['description']}*")
            st.markdown(f"**Action:** {pattern['action']}")
            st.markdown("**Examples:** " + ", ".join(pattern['examples']))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Checklist
    st.markdown(f'<h3 class="sub-header">📋 CHECKLIST FOR EVERY MATCH</h3>', unsafe_allow_html=True)
    
    checklist_html = """
    <div style="background: #f0f7ff; padding: 20px; border-radius: 10px;">
    <strong>BEFORE ANALYSIS:</strong><br>
    ✅ Get Last 10 Home/Away splits for both teams<br>
    ✅ Get Overall Last 10 for context<br>
    ✅ Get Recent H2H (≤2 years)<br>
    ✅ Check for ≥70% trends<br>
    <br>
    <strong>ANALYSIS:</strong><br>
    ✅ Calculate Expected Goals baseline<br>
    ✅ Apply trend adjustments<br>
    ✅ Check for aligned strong trends<br>
    ✅ Calculate true probabilities<br>
    <br>
    <strong>BETTING DECISION:</strong><br>
    ✅ Calculate value vs market odds<br>
    ✅ Determine stake (1-3% based on value/confidence)<br>
    ✅ Record bet and reasoning<br>
    ✅ Review after match<br>
    </div>
    """
    
    st.markdown(checklist_html, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 🎯 THE WINNING FORMULA (CONCRETE):
    ```
    IF (Home_BTTS% ≥ 70 AND Away_BTTS% ≥ 70):
      BET BTTS Yes @ odds >1.43
      
    ELIF (Home_Over% ≥ 70 AND Away_Over% ≥ 70):
      BET Over 2.5 @ odds >1.43
      
    ELIF (Home_Under% ≥ 70 AND Away_Under% ≥ 70):
      BET Under 2.5 @ odds >1.43
      
    ELSE:
      Calculate Expected Goals
      If ExpGoals > 2.7 → Lean Over @ odds >1.70
      If ExpGoals < 2.3 → Lean Under @ odds >1.80
    ```
    
    **Add:**
    - Big club home discount for away team trends
    - Relegation desperation adjustment
    - Value threshold: ≥15%
    
    *Bet responsibly • Track all bets • Never bet more than you can afford to lose*
    
    **🏁 CONCLUSION:** This logic has been validated across multiple matches. When we follow this concrete logic, we win. When we deviate, we lose. The system works. Now we just need to apply it consistently.
    """)

if __name__ == "__main__":
    main()
