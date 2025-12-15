import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math  # Add this import

# Page configuration
st.set_page_config(
    page_title="Football Betting Strategy Analyzer v3.0",
    page_icon="⚽",
    layout="wide"
)

# App title and description
st.title("⚽ Football Betting Strategy Analyzer v3.0")
st.markdown("""
**Updated with Refined Logic** - Now includes gradient scoring for "Tight" matches and BTTS-aware classification
to avoid false BTTS: No recommendations for balanced 1-1 type matches.
""")

# Sidebar for instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Fill all fields** for both teams
    2. Use **home/away splits** where applicable
    3. **Recent form** = last 5-10 games
    4. **Key absences**: Star attackers or defenders
    5. Click **Analyze Match** when ready
    """)
    
    st.header("🎯 Strategy Rules v3.0")
    st.markdown("""
    **Tight, Cautious Affair** → Under 2.5 Goals  
    - **Defensive Tight**: BTTS: No (if BTTS% < 45)
    - **Balanced Tight**: BTTS: Maybe (if BTTS% 45-55)
    - **Attack-Minded Tight**: BTTS: Yes (if BTTS% > 55)
    
    **One-Sided Dominance** → Favorite Win & BTTS: No  
    **Open Contest** → BTTS: Yes (with Attack Validation)
    """)
    
    st.header("⚠️ Critical Refinements")
    st.markdown("""
    1. **Gradient Scoring**: Tight matches now use 2.8 threshold (not 2.5)
    2. **BTTS-Aware**: Classification considers BTTS percentages
    3. **No Rigid Pairing**: Under 2.5 doesn't auto-pair with BTTS: No
    4. **Expected Outcomes**: Shows most likely scorelines
    """)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Create two columns for team inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Home Team")
    
    home_team = st.text_input("Team Name", key="home_name", value="Charleroi")
    
    # Filter 1: Form & Averages
    st.markdown("### 📊 Form & Averages")
    
    home_form_last5 = st.text_input(
        "Last 5 Results (W/D/L)", 
        placeholder="W,W,D,L,W",
        key="home_form5",
        value="L,W,D,L,D"
    )
    
    home_avg_scored = st.number_input(
        "Avg Goals Scored (Home)", 
        min_value=0.0, max_value=5.0, value=1.20, step=0.1,
        key="home_avg_scored",
        help="Critical for Attack Validation"
    )
    
    home_avg_conceded = st.number_input(
        "Avg Goals Conceded (Home)", 
        min_value=0.0, max_value=5.0, value=0.90, step=0.1,
        key="home_avg_conceded"
    )
    
    home_over25_pct = st.number_input(
        "Over 2.5 Goals % (Last 10)", 
        min_value=0, max_value=100, value=30, step=1,
        key="home_over25"
    )
    
    home_btts_pct = st.number_input(
        "BTTS Yes % (Last 10)", 
        min_value=0, max_value=100, value=60, step=1,
        key="home_btts",
        help="Now actively influences classification"
    )
    
    # Filter 2: Style & Key Stats
    st.markdown("### ⚽ Playing Style")
    
    home_possession = st.number_input(
        "Avg Possession %", 
        min_value=0, max_value=100, value=48, step=1,
        key="home_possession"
    )
    
    home_shots_on_target = st.number_input(
        "Shots on Target (Avg)", 
        min_value=0.0, max_value=10.0, value=4.1, step=0.1,
        key="home_sot"
    )
    
    home_key_attacker_out = st.checkbox(
        "Key Attacker Injured/Suspended",
        key="home_attacker_out"
    )
    
    home_key_defender_out = st.checkbox(
        "Key Defender Injured/Suspended",
        key="home_defender_out"
    )
    
    # Filter 3: Context
    st.markdown("### 🎭 Match Context")
    
    home_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High", "Medium", "Low"],
        key="home_motivation",
        index=2
    )

with col2:
    st.subheader("✈️ Away Team")
    
    away_team = st.text_input("Team Name", key="away_name", value="Union SG")
    
    # Filter 1: Form & Averages
    st.markdown("### 📊 Form & Averages")
    
    away_form_last5 = st.text_input(
        "Last 5 Results (W/D/L)", 
        placeholder="L,W,D,W,D",
        key="away_form5",
        value="W,D,W,L,W"
    )
    
    away_avg_scored = st.number_input(
        "Avg Goals Scored (Away)", 
        min_value=0.0, max_value=5.0, value=1.60, step=0.1,
        key="away_avg_scored",
        help="Critical for Attack Validation"
    )
    
    away_avg_conceded = st.number_input(
        "Avg Goals Conceded (Away)", 
        min_value=0.0, max_value=5.0, value=0.80, step=0.1,
        key="away_avg_conceded"
    )
    
    away_over25_pct = st.number_input(
        "Over 2.5 Goals % (Last 10)", 
        min_value=0, max_value=100, value=40, step=1,
        key="away_over25"
    )
    
    away_btts_pct = st.number_input(
        "BTTS Yes % (Last 10)", 
        min_value=0, max_value=100, value=50, step=1,
        key="away_btts",
        help="Now actively influences classification"
    )
    
    # Filter 2: Style & Key Stats
    st.markdown("### ⚽ Playing Style")
    
    away_possession = st.number_input(
        "Avg Possession %", 
        min_value=0, max_value=100, value=52, step=1,
        key="away_possession"
    )
    
    away_shots_on_target = st.number_input(
        "Shots on Target (Avg)", 
        min_value=0.0, max_value=10.0, value=4.8, step=0.1,
        key="away_sot"
    )
    
    away_key_attacker_out = st.checkbox(
        "Key Attacker Injured/Suspended",
        key="away_attacker_out"
    )
    
    away_key_defender_out = st.checkbox(
        "Key Defender Injured/Suspended",
        key="away_defender_out"
    )
    
    # Filter 3: Context
    st.markdown("### 🎭 Match Context")
    
    away_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High", "Medium", "Low"],
        key="away_motivation",
        index=2
    )
    
    match_context = st.selectbox(
        "Match Type",
        ["Normal League", "Local Derby", "Cup Final", "Relegation Battle", "Title Decider"],
        key="match_context",
        index=0
    )

# Odds section
st.markdown("---")
st.subheader("🎰 Market Odds")

odds_col1, odds_col2, odds_col3 = st.columns(3)

with odds_col1:
    over25_odds = st.number_input(
        "Over 2.5 Goals Odds", 
        min_value=1.01, max_value=10.0, value=2.10, step=0.01,
        key="over25_odds"
    )
    
    under25_odds = st.number_input(
        "Under 2.5 Goals Odds", 
        min_value=1.01, max_value=10.0, value=1.67, step=0.01,
        key="under25_odds"
    )

with odds_col2:
    btts_yes_odds = st.number_input(
        "BTTS Yes Odds", 
        min_value=1.01, max_value=10.0, value=1.85, step=0.01,
        key="btts_yes_odds"
    )
    
    btts_no_odds = st.number_input(
        "BTTS No Odds", 
        min_value=1.01, max_value=10.0, value=1.95, step=0.01,
        key="btts_no_odds"
    )

with odds_col3:
    home_win_odds = st.number_input(
        f"{home_team or 'Home'} Win Odds", 
        min_value=1.01, max_value=10.0, value=2.90, step=0.01,
        key="home_win_odds"
    )
    
    away_win_odds = st.number_input(
        f"{away_team or 'Away'} Win Odds", 
        min_value=1.01, max_value=10.0, value=2.40, step=0.01,
        key="away_win_odds"
    )

# Analysis button
st.markdown("---")
analyze_button = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

# ==================== FIXED: EXPECTED SCORELINE CALCULATION ====================
def calculate_expected_scorelines(home_avg, away_avg):
    """Calculate most likely scorelines based on Poisson approximation"""
    
    # Simple probability calculation
    likely_scores = []
    
    # Common low-scoring outcomes
    scorelines = [
        (0, 0), (1, 0), (0, 1), (1, 1), 
        (2, 0), (0, 2), (2, 1), (1, 2)
    ]
    
    # Simplified Poisson probability - FIXED: use math.factorial instead of np.math.factorial
    for h, a in scorelines:
        # Very basic approximation
        home_prob = np.exp(-home_avg) * (home_avg**h) / math.factorial(h)  # FIXED
        away_prob = np.exp(-away_avg) * (away_avg**a) / math.factorial(a)  # FIXED
        prob = home_prob * away_prob * 100  # as percentage
        
        if prob > 2.0:  # Only show probabilities > 2%
            likely_scores.append({
                'score': f"{h}-{a}",
                'probability': round(prob, 1),
                'type': 'BTTS' if h > 0 and a > 0 else 'Clean Sheet'
            })
    
    # Sort by probability
    likely_scores.sort(key=lambda x: x['probability'], reverse=True)
    return likely_scores[:5]  # Top 5 most likely

# ==================== UPDATED: Profile Calculation with Gradient Scoring ====================
def calculate_match_profile_with_gradient(data):
    """Calculate match profile with gradient scoring and BTTS awareness"""
    
    profile_scores = {
        'tight_cautious': 0,
        'one_sided_dominance': 0,
        'open_contest': 0
    }
    
    # Calculate averages
    total_goals_avg = data['home_avg_scored'] + data['away_avg_scored']
    btts_avg = (data['home_btts_pct'] + data['away_btts_pct']) / 2
    home_strength = data['home_avg_scored'] - data['home_avg_conceded']
    away_strength = data['away_avg_scored'] - data['away_avg_conceded']
    
    # ========== FIX 1: GRADIENT SCORING FOR TIGHT MATCHES ==========
    # Old: if total_goals_avg < 2.5: +2
    # New: Gradient approach
    if total_goals_avg < 2.8:  # Increased threshold
        profile_scores['tight_cautious'] += 1
    if total_goals_avg < 2.3:  # Very tight gets bonus
        profile_scores['tight_cautious'] += 1
    
    # Over 2.5% indicator (both must be low)
    if data['home_over25_pct'] < 40 and data['away_over25_pct'] < 40:
        profile_scores['tight_cautious'] += 1
    
    # Context bonus
    if data['match_context'] in ['Local Derby', 'Cup Final']:
        profile_scores['tight_cautious'] += 2
    
    # ========== FIX 2: BTTS-AWARE CLASSIFICATION ==========
    if btts_avg < 45:  # Low BTTS strongly supports "tight"
        profile_scores['tight_cautious'] += 2
    elif btts_avg > 55:  # High BTTS contradicts "tight"
        profile_scores['tight_cautious'] -= 1
        profile_scores['open_contest'] += 1
    
    # ========== ONE-SIDED DOMINANCE ==========
    form_diff = abs(home_strength - away_strength)
    if form_diff > 1.0:
        profile_scores['one_sided_dominance'] += 2
    if form_diff > 1.5:  # Very one-sided
        profile_scores['one_sided_dominance'] += 1
    
    # Key absences
    if data['home_key_attacker_out'] and not data['away_key_attacker_out']:
        profile_scores['one_sided_dominance'] += 1
    if data['away_key_defender_out'] and not data['home_key_defender_out']:
        profile_scores['one_sided_dominance'] += 1
    
    # ========== OPEN CONTEST ==========
    # Attack Validation (unchanged)
    weak_attack_flag = False
    if data['home_avg_scored'] < 1.3 and data['away_avg_scored'] < 1.3:
        weak_attack_flag = True
        profile_scores['open_contest'] -= 2
    
    if not weak_attack_flag:
        if total_goals_avg > 3.0:
            profile_scores['open_contest'] += 1
        if btts_avg > 60:  # Using our calculated btts_avg
            profile_scores['open_contest'] += 2
        if data['home_shots_on_target'] > 5.0 and data['away_shots_on_target'] > 5.0:
            profile_scores['open_contest'] += 1
    
    # Determine dominant profile
    max_score = max(profile_scores.values())
    dominant_profiles = [k for k, v in profile_scores.items() if v == max_score]
    
    if len(dominant_profiles) > 1:
        # Tie-breaker: prefer tight_cautious
        return 'tight_cautious', profile_scores, btts_avg, total_goals_avg
    else:
        return dominant_profiles[0], profile_scores, btts_avg, total_goals_avg

# ==================== UPDATED: Recommendations with BTTS Sub-Profiles ====================
def get_betting_recommendations_v3(profile, data, btts_avg, total_goals_avg):
    """Get betting recommendations with BTTS-aware sub-profiles"""
    
    recommendations = {
        'primary_markets': [],
        'secondary_markets': [],
        'avoid_markets': [],
        'confidence': 'Medium',
        'sub_profile': None,
        'expected_scorelines': []
    }
    
    # Calculate expected scorelines - NOW WITH FIXED math.factorial
    recommendations['expected_scorelines'] = calculate_expected_scorelines(
        data['home_avg_scored'], 
        data['away_avg_scored']
    )
    
    if profile == 'tight_cautious':
        # ========== FIX 3: BTTS SUB-PROFILES ==========
        if btts_avg < 45:  # Defensive Tight
            recommendations['sub_profile'] = 'Defensive Tight'
            recommendations['primary_markets'] = [
                f"Under {2.5} Goals @ {data['under25_odds']:.2f}",
                f"BTTS: No @ {data['btts_no_odds']:.2f}"
            ]
            recommendations['secondary_markets'] = [
                "0-0 or 1-0 Correct Score",
                "Clean Sheet (Home or Away)"
            ]
            recommendations['confidence'] = 'High' if data['match_context'] == 'Local Derby' else 'Medium'
            
        elif btts_avg > 55:  # Attack-Minded Tight
            recommendations['sub_profile'] = 'Attack-Minded Tight'
            recommendations['primary_markets'] = [
                f"Under {2.5} Goals @ {data['under25_odds']:.2f}",
                f"BTTS: Yes @ {data['btts_yes_odds']:.2f}"
            ]
            recommendations['secondary_markets'] = [
                "1-1 Correct Score",
                "Draw"
            ]
            recommendations['confidence'] = 'Medium'
            
        else:  # Balanced Tight (45-55%)
            recommendations['sub_profile'] = 'Balanced Tight'
            recommendations['primary_markets'] = [
                f"Under {2.5} Goals @ {data['under25_odds']:.2f}"
            ]
            recommendations['secondary_markets'] = [
                "1-1 Correct Score",
                "Draw",
                f"⚠️ BTTS: Too close - check odds value",
                f"(BTTS Avg: {btts_avg:.0f}%)"
            ]
            recommendations['confidence'] = 'Low-Medium'
        
        recommendations['avoid_markets'] = [
            "Over 3.5 Goals",
            "High-scoring correct scores (>2 goals)"
        ]
        
    elif profile == 'open_contest':
        recommendations['primary_markets'] = [
            f"BTTS: Yes @ {data['btts_yes_odds']:.2f}"
        ]
        
        # Only recommend Over 2.5 if strong case
        if total_goals_avg > 3.0 and btts_avg > 60:
            recommendations['secondary_markets'] = [
                f"Over 2.5 Goals @ {data['over25_odds']:.2f}",
                "Draw with BTTS"
            ]
        else:
            recommendations['secondary_markets'] = [
                "⚠️ Over 2.5 Goals - weaker case",
                "Draw with BTTS"
            ]
        
        recommendations['avoid_markets'] = [
            "BTTS: No",
            "Under 1.5 Goals"
        ]
        recommendations['confidence'] = 'Medium'
        
    elif profile == 'one_sided_dominance':
        # Determine favorite
        home_strength = data['home_avg_scored'] - data['home_avg_conceded']
        away_strength = data['away_avg_scored'] - data['away_avg_conceded']
        
        if home_strength > away_strength:
            favorite_odds = data['home_win_odds']
            favorite_name = data['home_team']
        else:
            favorite_odds = data['away_win_odds']
            favorite_name = data['away_team']
        
        recommendations['primary_markets'] = [
            f"{favorite_name} to Win @ {favorite_odds:.2f}",
            f"BTTS: No @ {data['btts_no_odds']:.2f}"
        ]
        
        if abs(home_strength - away_strength) > 1.5:
            recommendations['secondary_markets'] = [
                f"{favorite_name} -1 Asian Handicap",
                f"{favorite_name} to Win to Nil"
            ]
            recommendations['confidence'] = 'High'
        else:
            recommendations['secondary_markets'] = [
                f"{favorite_name} Draw No Bet",
                "Under 3.5 Goals"
            ]
            recommendations['confidence'] = 'Medium'
        
        recommendations['avoid_markets'] = [
            "BTTS: Yes",
            "Over 3.5 Goals"
        ]
    
    return recommendations

# Visualization function
def create_profile_visualization_v3(profile_scores, profile, sub_profile=None):
    """Create visualization with sub-profile indication"""
    
    fig = go.Figure()
    
    profiles = ['Tight/Cautious', 'One-Sided', 'Open Contest']
    scores = [
        profile_scores['tight_cautious'],
        profile_scores['one_sided_dominance'],
        profile_scores['open_contest']
    ]
    
    colors = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)']
    
    profile_index = ['tight_cautious', 'one_sided_dominance', 'open_contest'].index(profile)
    
    for i, (prof, score, color) in enumerate(zip(profiles, scores, colors)):
        fig.add_trace(go.Bar(
            x=[prof],
            y=[score],
            name=prof,
            marker_color=color,
            text=[f"Score: {score}"],
            textposition='auto',
            marker_line=dict(width=3 if i == profile_index else 0),
            opacity=0.9
        ))
    
    title = "Match Profile Analysis"
    if sub_profile:
        title += f" - {sub_profile}"
    
    fig.update_layout(
        title=title,
        yaxis_title="Profile Score",
        showlegend=False,
        height=400
    )
    
    return fig

# Main analysis logic
if analyze_button:
    if not home_team or not away_team:
        st.error("Please enter team names for both home and away teams.")
    else:
        # Prepare data
        analysis_data = {
            'home_team': home_team,
            'away_team': away_team,
            'home_avg_scored': home_avg_scored,
            'home_avg_conceded': home_avg_conceded,
            'home_over25_pct': home_over25_pct,
            'home_btts_pct': home_btts_pct,
            'home_shots_on_target': home_shots_on_target,
            'home_key_attacker_out': home_key_attacker_out,
            'home_key_defender_out': home_key_defender_out,
            'away_avg_scored': away_avg_scored,
            'away_avg_conceded': away_avg_conceded,
            'away_over25_pct': away_over25_pct,
            'away_btts_pct': away_btts_pct,
            'away_shots_on_target': away_shots_on_target,
            'away_key_attacker_out': away_key_attacker_out,
            'away_key_defender_out': away_key_defender_out,
            'match_context': match_context,
            'over25_odds': over25_odds,
            'under25_odds': under25_odds,
            'btts_yes_odds': btts_yes_odds,
            'btts_no_odds': btts_no_odds,
            'home_win_odds': home_win_odds,
            'away_win_odds': away_win_odds
        }
        
        # Calculate profile with new logic
        match_profile, profile_scores, btts_avg, total_goals_avg = calculate_match_profile_with_gradient(analysis_data)
        
        # Get recommendations
        recommendations = get_betting_recommendations_v3(match_profile, analysis_data, btts_avg, total_goals_avg)
        
        # Display results
        st.markdown("---")
        st.header("📈 Analysis Results v3.0")
        
        # Create columns
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            # Profile display
            profile_names = {
                'tight_cautious': '🔒 Tight, Cautious Affair',
                'one_sided_dominance': '⚡ One-Sided Dominance',
                'open_contest': '🔥 Open Contest'
            }
            
            profile_display = profile_names[match_profile]
            if recommendations['sub_profile']:
                profile_display += f" ({recommendations['sub_profile']})"
            
            st.metric(
                "Identified Match Profile",
                profile_display,
                delta=f"Confidence: {recommendations['confidence']}"
            )
            
            # Visualization
            st.plotly_chart(create_profile_visualization_v3(
                profile_scores, match_profile, recommendations['sub_profile']
            ), use_container_width=True)
            
            # Key metrics
            st.metric("Total Goals Avg", f"{total_goals_avg:.1f}")
            st.metric("BTTS Avg %", f"{btts_avg:.0f}%")
        
        with result_col2:
            st.subheader("🎯 Betting Recommendations")
            
            st.markdown("#### Primary Markets")
            for market in recommendations['primary_markets']:
                if "⚠️" in market:
                    st.warning(f"{market}")
                else:
                    st.success(f"✅ {market}")
            
            if recommendations['secondary_markets']:
                st.markdown("#### Secondary Markets")
                for market in recommendations['secondary_markets']:
                    if "⚠️" in market:
                        st.warning(f"{market}")
                    else:
                        st.info(f"💡 {market}")
            
            if recommendations['avoid_markets']:
                st.markdown("#### Markets to Avoid")
                for market in recommendations['avoid_markets']:
                    st.error(f"❌ {market}")
        
        # ========== FIX 4: EXPECTED SCORELINES ==========
        st.markdown("---")
        st.subheader("🎯 Expected Scorelines")
        
        if recommendations['expected_scorelines']:
            scoreline_cols = st.columns(len(recommendations['expected_scorelines']))
            for idx, scoreline in enumerate(recommendations['expected_scorelines']):
                with scoreline_cols[idx]:
                    st.metric(
                        f"{scoreline['score']}",
                        f"{scoreline['probability']}%",
                        scoreline['type']
                    )
        else:
            st.info("Scoreline probability calculation requires more data")
        
        # Detailed analysis
        st.markdown("---")
        st.subheader("🧠 Detailed Analysis v3.0")
        
        analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
        
        with analysis_col1:
            # Attack Analysis
            st.markdown("#### ⚽ Attack Analysis")
            attack_df = pd.DataFrame({
                'Team': [home_team, away_team],
                'Avg Scored': [home_avg_scored, away_avg_scored],
                'Attack Status': [
                    'Weak' if home_avg_scored < 1.3 else 'Moderate' if home_avg_scored < 1.8 else 'Strong',
                    'Weak' if away_avg_scored < 1.3 else 'Moderate' if away_avg_scored < 1.8 else 'Strong'
                ]
            })
            st.dataframe(attack_df, use_container_width=True, hide_index=True)
        
        with analysis_col2:
            # BTTS Analysis
            st.markdown("#### 🎯 BTTS Analysis")
            btts_df = pd.DataFrame({
                'Team': [home_team, away_team, 'Average'],
                'BTTS %': [home_btts_pct, away_btts_pct, btts_avg],
                'Trend': [
                    'High' if home_btts_pct > 60 else 'Low' if home_btts_pct < 40 else 'Medium',
                    'High' if away_btts_pct > 60 else 'Low' if away_btts_pct < 40 else 'Medium',
                    'High' if btts_avg > 55 else 'Low' if btts_avg < 45 else 'Balanced'
                ]
            })
            st.dataframe(btts_df, use_container_width=True, hide_index=True)
        
        with analysis_col3:
            # Profile Scoring
            st.markdown("#### 📊 Profile Scoring")
            score_df = pd.DataFrame({
                'Profile': ['Tight/Cautious', 'One-Sided', 'Open Contest'],
                'Score': [
                    profile_scores['tight_cautious'],
                    profile_scores['one_sided_dominance'],
                    profile_scores['open_contest']
                ],
                'Key Factors': [
                    f"Goals: {total_goals_avg:.1f}, BTTS: {btts_avg:.0f}%",
                    f"Strength Diff: {abs((home_avg_scored-home_avg_conceded)-(away_avg_scored-away_avg_conceded)):.1f}",
                    f"Shots: {home_shots_on_target:.1f}/{away_shots_on_target:.1f}"
                ]
            })
            st.dataframe(score_df, use_container_width=True, hide_index=True)

# Test case explanation
st.markdown("---")
with st.expander("📋 Charleroi vs Union SG Test Case - What Changed"):
    st.markdown("""
    **v2.0 Flaw:** Recommended BTTS: No for a 1-1 match
    **v3.0 Fix:** Now correctly identifies as "Balanced Tight"
    
    **Key Changes:**
    1. **Gradient Scoring**: Tight threshold raised to 2.8 (was 2.5)
    2. **BTTS-Aware**: Classification now considers BTTS% (55% avg → "Balanced")
    3. **Sub-Profiles**: "Tight" now has 3 types based on BTTS%
    4. **Expected Scores**: Shows 1-1 as most likely outcome
    
    **Result:** Under 2.5 ✓ with BTTS warning ⚠️ (not a false BTTS: No)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with the <strong>3-Filter Betting Strategy v3.0</strong></p>
    <p><small>Key Fixes: Gradient scoring, BTTS-aware classification, no rigid BTTS pairing</small></p>
    <p><small>Remember: No betting strategy guarantees wins. Always gamble responsibly.</small></p>
</div>
""", unsafe_allow_html=True)
