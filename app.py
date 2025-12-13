import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="BRUTBALL PREDICTOR PRO V3",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INITIALIZE SESSION STATE ==========
if 'match_data' not in st.session_state:
    st.session_state.match_data = {
        'home_name': 'Lecce',
        'away_name': 'Pisa',
        'home_pos': 17,
        'away_pos': 18,
        'home_attack': 0.71,
        'away_attack': 1.2,
        'home_defense': 1.3,
        'away_defense': 1.4,
        'home_goals5': 4,
        'away_goals5': 8,
        'home_conceded5': 4,
        'away_conceded5': 13
    }

# ========== CSS STYLING ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #424242;
        margin-top: 1.5rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .high-confidence {
        border-left-color: #4CAF50 !important;
        background-color: #f1f8e9;
    }
    .medium-confidence {
        border-left-color: #FF9800 !important;
        background-color: #fff3e0;
    }
    .low-confidence {
        border-left-color: #F44336 !important;
        background-color: #ffebee;
    }
    .failure-analysis {
        border-left: 5px solid #F44336 !important;
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .fixed-rule {
        border-left: 5px solid #4CAF50 !important;
        background-color: #e8f5e8;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .data-sync-banner {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ========== FIXED LEAGUE POSITION ENGINE ==========

def predict_match_league_positions(home_pos, away_pos, total_teams=20):
    """
    BRUTBALL LEAGUE POSITION ENGINE - FIXED VERSION
    Accounts for relegation battle psychology
    """
    gap = abs(home_pos - away_pos)
    relegation_cutoff = total_teams - 3  # Bottom 4 in 20-team league
    
    # 1. BOTH in relegation zone (NEW RULE)
    if home_pos >= relegation_cutoff and away_pos >= relegation_cutoff:
        return {
            'over_under': 'UNDER 2.5',
            'over_under_confidence': 'HIGH',
            'over_under_logic': 'BOTH teams in bottom 4 → RELEGATION SIX-POINTER → fearful, cautious play',
            'result': 'DRAW or 1-goal margin',
            'result_confidence': 'HIGH',
            'position_gap': gap,
            'match_type': 'RELEGATION BATTLE 🔥',
            'stake_recommendation': 'MAX BET (2x normal)'
        }
    
    # 2. ONE in relegation zone (NEW RULE)
    elif home_pos >= relegation_cutoff or away_pos >= relegation_cutoff:
        return {
            'over_under': 'UNDER 2.5',
            'over_under_confidence': 'MEDIUM',
            'over_under_logic': 'Team in relegation zone → plays cautiously to avoid defeat',
            'result': 'CLOSE MATCH',
            'result_confidence': 'MEDIUM',
            'position_gap': gap,
            'match_type': 'RELEGATION-THREATENED',
            'stake_recommendation': 'NORMAL (1x)'
        }
    
    # 3. Original rules for mid/top teams
    elif gap <= 4:
        return {
            'over_under': 'OVER 2.5',
            'over_under_confidence': 'HIGH' if gap <= 2 else 'MEDIUM',
            'over_under_logic': f'Teams within {gap} positions → similar ambitions → attacking football',
            'result': 'DRAW or close match',
            'result_confidence': 'MEDIUM',
            'position_gap': gap,
            'match_type': 'MID-TABLE CLASH',
            'stake_recommendation': 'NORMAL (1x)'
        }
    
    else:  # gap > 4
        return {
            'over_under': 'UNDER 2.5',
            'over_under_confidence': 'HIGH' if gap >= 8 else 'MEDIUM',
            'over_under_logic': f'Teams {gap} positions apart → different agendas → cautious play',
            'result': 'BETTER TEAM WINS',
            'result_confidence': 'MEDIUM',
            'position_gap': gap,
            'match_type': 'HIERARCHICAL MATCH',
            'stake_recommendation': 'NORMAL (1x)'
        }

# ========== XG ENGINE ==========

@dataclass
class TeamMetrics:
    """Team metrics for xG engine"""
    attack_strength: float
    defense_strength: float
    goals_scored_last_5: int
    goals_conceded_last_5: int
    name: str = ""

def calculate_xg_prediction(home: TeamMetrics, away: TeamMetrics, league_avg_goals=2.68):
    """Simplified xG prediction"""
    # Calculate form factors
    home_recent_ppg = home.goals_scored_last_5 / 5
    away_recent_ppg = away.goals_scored_last_5 / 5
    
    home_form = home_recent_ppg / home.attack_strength if home.attack_strength > 0 else 1.0
    away_form = away_recent_ppg / away.attack_strength if away.attack_strength > 0 else 1.0
    
    # Bound form factors
    home_form = max(0.7, min(1.3, home_form))
    away_form = max(0.7, min(1.3, away_form))
    
    # Expected goals
    home_expected = (home.attack_strength * home_form * 1.15 + away.defense_strength) / 2
    away_expected = (away.attack_strength * away_form * 0.92 + home.defense_strength) / 2
    
    total_expected = home_expected + away_expected
    
    # Determine prediction
    if total_expected > 2.7:
        prediction = 'OVER 2.5'
        confidence = 'High' if total_expected > 3.0 else 'Medium'
    elif total_expected < 2.3:
        prediction = 'UNDER 2.5'
        confidence = 'High' if total_expected < 2.0 else 'Medium'
    else:
        prediction = 'OVER 2.5' if total_expected > 2.5 else 'UNDER 2.5'
        confidence = 'Low'
    
    # Check for very poor attacks (relegation warning)
    if home.attack_strength < 0.8 and away.attack_strength < 0.8:
        prediction = 'UNDER 2.5'
        confidence = 'High'
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'expected_goals': round(total_expected, 2),
        'home_expected': round(home_expected, 2),
        'away_expected': round(away_expected, 2),
        'home_form': round(home_form, 2),
        'away_form': round(away_form, 2)
    }

# ========== SIDEBAR ==========

def sidebar():
    """Sidebar with shared settings"""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/869/869445.png", width=100)
        st.markdown("### ⚙️ Global Settings")
        
        total_teams = st.selectbox(
            "Total Teams in League",
            [20, 24, 18, 16, 22],
            index=0,
            key="total_teams"
        )
        
        # Data entry section
        st.markdown("---")
        st.markdown("### 📝 Enter Match Data")
        
        col1, col2 = st.columns(2)
        with col1:
            home_name = st.text_input(
                "🏠 Home Team",
                value=st.session_state.match_data['home_name'],
                key="sidebar_home_name"
            )
            home_pos = st.number_input(
                "Home Position",
                min_value=1,
                max_value=total_teams,
                value=st.session_state.match_data['home_pos'],
                key="sidebar_home_pos"
            )
        
        with col2:
            away_name = st.text_input(
                "✈️ Away Team",
                value=st.session_state.match_data['away_name'],
                key="sidebar_away_name"
            )
            away_pos = st.number_input(
                "Away Position",
                min_value=1,
                max_value=total_teams,
                value=st.session_state.match_data['away_pos'],
                key="sidebar_away_pos"
            )
        
        # Save button
        if st.button("💾 Save Match Data", use_container_width=True):
            st.session_state.match_data.update({
                'home_name': home_name,
                'away_name': away_name,
                'home_pos': home_pos,
                'away_pos': away_pos
            })
            st.success("Data saved! Available in all tabs.")
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Examples")
        
        if st.button("🔴 Lecce vs Pisa", use_container_width=True):
            st.session_state.match_data.update({
                'home_name': 'Lecce',
                'away_name': 'Pisa',
                'home_pos': 17,
                'away_pos': 18,
                'home_attack': 0.71,
                'away_attack': 1.2,
                'home_defense': 1.3,
                'away_defense': 1.4,
                'home_goals5': 4,
                'away_goals5': 8,
                'home_conceded5': 4,
                'away_conceded5': 13
            })
            st.rerun()
        
        if st.button("🟢 Mid-table Example", use_container_width=True):
            st.session_state.match_data.update({
                'home_name': 'Team A',
                'away_name': 'Team B',
                'home_pos': 8,
                'away_pos': 9,
                'home_attack': 1.4,
                'away_attack': 1.3,
                'home_defense': 1.2,
                'away_defense': 1.4,
                'home_goals5': 7,
                'away_goals5': 6,
                'home_conceded5': 6,
                'away_conceded5': 7
            })
            st.rerun()
        
        return total_teams

# ========== TAB 1: LEAGUE POSITION ENGINE ==========

def tab_league_position(total_teams):
    """Tab 1: League Position Engine"""
    st.header("🎯 FIXED LEAGUE POSITION ENGINE")
    
    # Show the current match
    st.markdown(f"### 📋 Current Match: {st.session_state.match_data['home_name']} vs {st.session_state.match_data['away_name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Home Position", f"{st.session_state.match_data['home_pos']}/{total_teams}")
        if st.session_state.match_data['home_pos'] >= total_teams - 3:
            st.error("⚠️ RELEGATION ZONE")
    with col2:
        st.metric("Away Position", f"{st.session_state.match_data['away_pos']}/{total_teams}")
        if st.session_state.match_data['away_pos'] >= total_teams - 3:
            st.error("⚠️ RELEGATION ZONE")
    
    # Get prediction
    prediction = predict_match_league_positions(
        st.session_state.match_data['home_pos'],
        st.session_state.match_data['away_pos'],
        total_teams
    )
    
    # Display prediction
    st.markdown("---")
    st.markdown("### 📊 Position Analysis")
    
    # Match type
    st.info(f"**Match Type:** {prediction['match_type']}")
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
        st.markdown("#### 📈 OVER/UNDER 2.5")
        st.markdown(f"**Prediction:** `{prediction['over_under']}`")
        st.markdown(f"**Confidence:** `{prediction['over_under_confidence']}`")
        st.markdown(f"*{prediction['over_under_logic']}*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
        st.markdown("#### 🏆 MATCH RESULT")
        st.markdown(f"**Prediction:** `{prediction['result']}`")
        st.markdown(f"**Confidence:** `{prediction['result_confidence']}`")
        st.markdown(f"**Position Gap:** `{prediction['position_gap']}`")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Betting recommendation
    st.markdown('<div class="fixed-rule">', unsafe_allow_html=True)
    st.markdown("### 💰 Betting Recommendation")
    st.markdown(f"**Stake:** `{prediction['stake_recommendation']}`")
    
    if prediction['match_type'] == 'RELEGATION BATTLE 🔥':
        st.warning("""
        **Relegation Battle Psychology:**
        - Both teams fighting to avoid drop
        - FEAR of losing > desire to win
        - Ultra-cautious approach
        - Expect LOW scoring (1-0, 0-0, 1-1)
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show what old system would have predicted
    gap = prediction['position_gap']
    if gap <= 4 and prediction['match_type'] == 'RELEGATION BATTLE 🔥':
        st.markdown("---")
        st.markdown("### 🔄 Comparison with Old System")
        st.error(f"**OLD SYSTEM:** Would have predicted OVER 2.5 (gap = {gap} ≤ 4) ❌")
        st.success(f"**NEW SYSTEM:** Predicts UNDER 2.5 (relegation battle) ✅")

# ========== TAB 2: XG ENGINE ==========

def tab_xg_engine():
    """Tab 2: xG Statistical Engine"""
    st.header("📊 xG STATISTICAL ENGINE")
    
    # Show current match
    st.markdown(f"### 📋 Analyzing: {st.session_state.match_data['home_name']} vs {st.session_state.match_data['away_name']}")
    
    # Input for xG stats
    st.markdown("### ⚽ Enter Team Statistics")
    
    tab1, tab2 = st.tabs(["Core Stats", "Recent Form"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{st.session_state.match_data['home_name']}")
            home_attack = st.number_input(
                "Goals/Game",
                0.0, 5.0,
                value=st.session_state.match_data['home_attack'],
                key="home_attack_input"
            )
            home_defense = st.number_input(
                "Conceded/Game",
                0.0, 5.0,
                value=st.session_state.match_data['home_defense'],
                key="home_defense_input"
            )
        
        with col2:
            st.subheader(f"{st.session_state.match_data['away_name']}")
            away_attack = st.number_input(
                "Goals/Game",
                0.0, 5.0,
                value=st.session_state.match_data['away_attack'],
                key="away_attack_input"
            )
            away_defense = st.number_input(
                "Conceded/Game",
                0.0, 5.0,
                value=st.session_state.match_data['away_defense'],
                key="away_defense_input"
            )
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{st.session_state.match_data['home_name']} Last 5")
            home_goals5 = st.number_input(
                "Goals Scored",
                0, 30,
                value=st.session_state.match_data['home_goals5'],
                key="home_goals5_input"
            )
            home_conceded5 = st.number_input(
                "Goals Conceded",
                0, 30,
                value=st.session_state.match_data['home_conceded5'],
                key="home_conceded5_input"
            )
        
        with col2:
            st.subheader(f"{st.session_state.match_data['away_name']} Last 5")
            away_goals5 = st.number_input(
                "Goals Scored",
                0, 30,
                value=st.session_state.match_data['away_goals5'],
                key="away_goals5_input"
            )
            away_conceded5 = st.number_input(
                "Goals Conceded",
                0, 30,
                value=st.session_state.match_data['away_conceded5'],
                key="away_conceded5_input"
            )
    
    # Save xG data
    if st.button("💾 Save xG Data", key="save_xg"):
        st.session_state.match_data.update({
            'home_attack': home_attack,
            'home_defense': home_defense,
            'away_attack': away_attack,
            'away_defense': away_defense,
            'home_goals5': home_goals5,
            'home_conceded5': home_conceded5,
            'away_goals5': away_goals5,
            'away_conceded5': away_conceded5
        })
        st.success("xG data saved!")
    
    # Generate prediction
    if st.button("📈 Generate xG Prediction", type="primary"):
        home_metrics = TeamMetrics(
            name=st.session_state.match_data['home_name'],
            attack_strength=st.session_state.match_data['home_attack'],
            defense_strength=st.session_state.match_data['home_defense'],
            goals_scored_last_5=st.session_state.match_data['home_goals5'],
            goals_conceded_last_5=st.session_state.match_data['home_conceded5']
        )
        
        away_metrics = TeamMetrics(
            name=st.session_state.match_data['away_name'],
            attack_strength=st.session_state.match_data['away_attack'],
            defense_strength=st.session_state.match_data['away_defense'],
            goals_scored_last_5=st.session_state.match_data['away_goals5'],
            goals_conceded_last_5=st.session_state.match_data['away_conceded5']
        )
        
        prediction = calculate_xg_prediction(home_metrics, away_metrics)
        
        # Display results
        st.success("✅ xG Prediction Generated")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("O/U Prediction", prediction['prediction'])
            st.metric("Confidence", prediction['confidence'])
        with col4:
            st.metric("Expected Goals", prediction['expected_goals'])
            st.metric("Home xG", prediction['home_expected'])
        with col5:
            st.metric("Away xG", prediction['away_expected'])
            st.metric("Away Form", f"{prediction['away_form']}x")
        
        # Form analysis
        st.markdown("### 📊 Form Analysis")
        col6, col7 = st.columns(2)
        with col6:
            if prediction['home_form'] >= 1.15:
                st.success(f"**{home_metrics.name}:** Excellent form ({prediction['home_form']}x)")
            elif prediction['home_form'] >= 1.05:
                st.success(f"**{home_metrics.name}:** Good form ({prediction['home_form']}x)")
            elif prediction['home_form'] <= 0.7:
                st.error(f"**{home_metrics.name}:** Very poor form ({prediction['home_form']}x)")
            else:
                st.info(f"**{home_metrics.name}:** Average form ({prediction['home_form']}x)")
        
        with col7:
            if prediction['away_form'] >= 1.15:
                st.success(f"**{away_metrics.name}:** Excellent form ({prediction['away_form']}x)")
            elif prediction['away_form'] >= 1.05:
                st.success(f"**{away_metrics.name}:** Good form ({prediction['away_form']}x)")
            elif prediction['away_form'] <= 0.7:
                st.error(f"**{away_metrics.name}:** Very poor form ({prediction['away_form']}x)")
            else:
                st.info(f"**{away_metrics.name}:** Average form ({prediction['away_form']}x)")
        
        # Warning for poor attacks
        if home_metrics.attack_strength < 0.8 or away_metrics.attack_strength < 0.8:
            st.warning("⚠️ **POOR ATTACKING TEAM DETECTED** - Expect lower scoring than stats suggest")

# ========== TAB 3: COMBINED ANALYSIS ==========

def tab_combined_analysis(total_teams):
    """Tab 3: Combined Analysis"""
    st.header("🚀 COMBINED ANALYSIS")
    
    # Get both predictions
    pos_prediction = predict_match_league_positions(
        st.session_state.match_data['home_pos'],
        st.session_state.match_data['away_pos'],
        total_teams
    )
    
    home_metrics = TeamMetrics(
        name=st.session_state.match_data['home_name'],
        attack_strength=st.session_state.match_data['home_attack'],
        defense_strength=st.session_state.match_data['home_defense'],
        goals_scored_last_5=st.session_state.match_data['home_goals5'],
        goals_conceded_last_5=st.session_state.match_data['home_conceded5']
    )
    
    away_metrics = TeamMetrics(
        name=st.session_state.match_data['away_name'],
        attack_strength=st.session_state.match_data['away_attack'],
        defense_strength=st.session_state.match_data['away_defense'],
        goals_scored_last_5=st.session_state.match_data['away_goals5'],
        goals_conceded_last_5=st.session_state.match_data['away_conceded5']
    )
    
    xg_prediction = calculate_xg_prediction(home_metrics, away_metrics)
    
    # Display both predictions
    st.markdown("### 🔗 Engine Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        confidence_class = "high-confidence" if pos_prediction['over_under_confidence'] == "HIGH" else "medium-confidence"
        st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
        st.markdown("#### 🎯 **POSITION ENGINE**")
        st.markdown(f"**Match Type:** {pos_prediction['match_type']}")
        st.markdown(f"**Prediction:** {pos_prediction['over_under']}")
        st.markdown(f"**Confidence:** {pos_prediction['over_under_confidence']}")
        st.markdown(f"**Logic:** {pos_prediction['over_under_logic']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        confidence_class = "high-confidence" if xg_prediction['confidence'] == "High" else "medium-confidence"
        st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
        st.markdown("#### 📊 **xG ENGINE**")
        st.markdown(f"**Prediction:** {xg_prediction['prediction']}")
        st.markdown(f"**Confidence:** {xg_prediction['confidence']}")
        st.markdown(f"**Expected Goals:** {xg_prediction['expected_goals']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Decision matrix
    st.markdown("### 🎲 Decision Matrix")
    
    pos_ou = pos_prediction['over_under']
    xg_ou = xg_prediction['prediction']
    
    if pos_ou == xg_ou:
        st.success(f"✅ **ENGINES AGREE ON {pos_ou}**")
        
        if pos_prediction['over_under_confidence'] == "HIGH" and xg_prediction['confidence'] == "High":
            st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            st.markdown("#### 🚀 **MAXIMUM CONFIDENCE BET**")
            st.markdown(f"**Bet:** {pos_ou}")
            st.markdown("**Stake:** MAX BET (2x normal)")
            st.markdown(f"**Position Logic:** {pos_prediction['over_under_logic']}")
            st.markdown(f"**xG Expected Goals:** {xg_prediction['expected_goals']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
            st.markdown("#### 📈 **CONFIDENT BET**")
            st.markdown(f"**Bet:** {pos_ou}")
            st.markdown("**Stake:** NORMAL BET (1x)")
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.error(f"⚠️ **ENGINES DISAGREE**")
        st.markdown(f"**Position Engine:** {pos_ou}")
        st.markdown(f"**xG Engine:** {xg_ou}")
        
        # Decision rules
        if pos_prediction['match_type'] == 'RELEGATION BATTLE 🔥':
            st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            st.markdown("#### 🔥 **TRUST POSITION ENGINE**")
            st.markdown("**Stake:** NORMAL BET (1x)")
            st.markdown(f"**Bet:** {pos_ou} (UNDER 2.5)")
            st.markdown("**Reason:** Relegation battle psychology overrides stats")
            st.markdown("**Psychology:** Both bottom 4 → fearful, cautious play")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif pos_prediction['over_under_confidence'] == "HIGH":
            st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
            st.markdown("#### 🔥 **TRUST POSITION ENGINE**")
            st.markdown("**Stake:** NORMAL BET (1x)")
            st.markdown(f"**Bet:** {pos_ou}")
            st.markdown("**Reason:** Position engine has HIGH confidence")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif xg_prediction['confidence'] == "High":
            st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
            st.markdown("#### 📊 **TRUST xG ENGINE**")
            st.markdown("**Stake:** NORMAL BET (1x)")
            st.markdown(f"**Bet:** {xg_ou}")
            st.markdown("**Reason:** xG engine has HIGH confidence")
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="prediction-card low-confidence">', unsafe_allow_html=True)
            st.markdown("#### 🚫 **AVOID BET**")
            st.markdown("**Stake:** NO BET")
            st.markdown("**Reason:** Engines disagree and neither has high confidence")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Case study for Lecce vs Pisa
    if (st.session_state.match_data['home_name'] == 'Lecce' and 
        st.session_state.match_data['away_name'] == 'Pisa'):
        st.markdown("---")
        st.markdown("### 🎯 **LECCE vs PISA CASE STUDY**")
        
        st.info("""
        **What happened:**
        - Score: 1-0 (UNDER 2.5, BTTS NO)
        - Expected Goals: 3.26 (xG was wrong)
        - Psychology: Relegation battle dominated
        
        **What our FIXED system predicts:**
        1. **Position Engine:** UNDER 2.5 ✅ (relegation battle)
        2. **xG Engine:** OVER 2.5 ❌ (stats misleading)
        3. **Final Decision:** Trust Position Engine ✅
        
        **Lesson learned:** Relegation psychology > statistics
        """)

# ========== MAIN APP ==========

def main():
    st.markdown('<div class="main-header">⚽ BRUTBALL PREDICTOR PRO V3</div>', unsafe_allow_html=True)
    st.markdown("### **SYNCHRONIZED DATA** - All tabs share the same match data")
    
    # Show data sync banner
    st.markdown('<div class="data-sync-banner">', unsafe_allow_html=True)
    st.markdown(f"📊 **Current Match:** {st.session_state.match_data['home_name']} ({st.session_state.match_data['home_pos']}) vs {st.session_state.match_data['away_name']} ({st.session_state.match_data['away_pos']})")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Failure analysis
    if (st.session_state.match_data['home_name'] == 'Lecce' and 
        st.session_state.match_data['away_name'] == 'Pisa'):
        st.markdown('<div class="failure-analysis">', unsafe_allow_html=True)
        st.markdown("### 🔍 **CASE STUDY: Lecce 1-0 Pisa**")
        st.markdown("""
        - **Old System:** Predicted OVER 2.5 ❌ (gap = 1)
        - **New System:** Predicts UNDER 2.5 ✅ (relegation battle)
        - **Actual:** 1-0 (UNDER) ✅
        - **Lesson:** Relegation teams play with FEAR, not ambition
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get global settings from sidebar
    total_teams = sidebar()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 POSITION ENGINE", 
        "📊 xG ENGINE", 
        "🚀 COMBINED"
    ])
    
    with tab1:
        tab_league_position(total_teams)
    
    with tab2:
        tab_xg_engine()
    
    with tab3:
        tab_combined_analysis(total_teams)

if __name__ == "__main__":
    main()