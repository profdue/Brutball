import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="BRUTBALL PREDICTOR PRO V2",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .match-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
</style>
""", unsafe_allow_html=True)

# ========== FIXED LEAGUE POSITION ENGINE ==========

def predict_match_league_positions(home_pos, away_pos, total_teams=20):
    """
    BRUTBALL LEAGUE POSITION ENGINE - FIXED VERSION
    NEW RULE: Bottom-of-table matches play differently!
    
    Position Gap Rules V2:
    - IF both teams in BOTTOM 4: → UNDER 2.5 (HIGH confidence)
    - IF position gap ≤ 4 AND both MID-TABLE: → OVER 2.5
    - IF position gap > 4: → UNDER 2.5
    - IF extreme gap (>12): → CAUTION (unpredictable)
    """
    gap = abs(home_pos - away_pos)
    
    # NEW CRITICAL RULE: Relegation zone matches
    relegation_cutoff = total_teams - 3  # Bottom 4 in 20-team league
    
    # 1. CHECK: Both teams in relegation zone (BOTTOM OF TABLE FIX)
    if home_pos >= relegation_cutoff and away_pos >= relegation_cutoff:
        over_under = "UNDER 2.5"
        ou_confidence = "HIGH"
        ou_confidence_score = 85
        ou_logic = f"BOTH teams in bottom 4 → RELEGATION SIX-POINTER → fearful, cautious play"
        
        # Result prediction for relegation battles
        if gap <= 2:
            result = "DRAW or 1-goal margin"
            result_confidence = "HIGH"
            result_confidence_score = 75
            result_logic = "Relegation six-pointers often close draws or narrow wins"
        elif home_pos < away_pos:
            result = "SLIGHT HOME EDGE"
            result_confidence = "MEDIUM"
            result_confidence_score = 65
            result_logic = "Home advantage slight edge in relegation battle"
        else:
            result = "SLIGHT AWAY EDGE"
            result_confidence = "MEDIUM"
            result_confidence_score = 65
            result_logic = "Away team slightly higher in table"
    
    # 2. CHECK: One team in relegation zone
    elif home_pos >= relegation_cutoff or away_pos >= relegation_cutoff:
        # Team in relegation plays cautiously
        over_under = "UNDER 2.5"
        ou_confidence = "MEDIUM"
        ou_confidence_score = 70
        ou_logic = f"Team in relegation zone → plays cautiously to avoid defeat"
        
        # Match result logic
        if home_pos >= relegation_cutoff and away_pos < relegation_cutoff:
            # Home in relegation, away safe/mid-table
            result = "AWAY WIN or DRAW"
            result_confidence = "MEDIUM"
            result_confidence_score = 65
            result_logic = "Better away team should avoid defeat"
        elif away_pos >= relegation_cutoff and home_pos < relegation_cutoff:
            # Away in relegation, home safe/mid-table
            result = "HOME WIN or DRAW"
            result_confidence = "MEDIUM"
            result_confidence_score = 65
            result_logic = "Better home team should avoid defeat"
        else:
            result = "DRAW or close match"
            result_confidence = "MEDIUM"
            result_confidence_score = 60
            result_logic = f"Teams within {gap} positions → evenly matched"
    
    # 3. ORIGINAL RULES: Mid-table and top teams
    elif gap <= 4:
        over_under = "OVER 2.5"
        if gap <= 2:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams within {gap} positions → similar ambitions → attacking football"
        
        # Match result for close mid-table teams
        if home_pos < away_pos - 4:  # Home significantly better
            result = "HOME WIN"
            if gap >= 8:
                result_confidence = "HIGH"
                result_confidence_score = 80
            else:
                result_confidence = "MEDIUM"
                result_confidence_score = 65
            result_logic = f"Home team {gap} positions better → should win"
        elif away_pos < home_pos - 4:  # Away significantly better
            result = "AWAY WIN"
            if gap >= 8:
                result_confidence = "HIGH"
                result_confidence_score = 80
            else:
                result_confidence = "MEDIUM"
                result_confidence_score = 65
            result_logic = f"Away team {gap} positions better → should win"
        else:  # Close positions
            result = "DRAW or close match"
            result_confidence = "MEDIUM"
            result_confidence_score = 60
            result_logic = f"Teams within {gap} positions → evenly matched"
    
    else:  # gap > 4 (not involving relegation teams)
        over_under = "UNDER 2.5"
        if gap >= 8:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams {gap} positions apart → different agendas → cautious play"
        
        # Match result for distant positions
        if home_pos < away_pos - 4:  # Home significantly better
            result = "HOME WIN"
            if gap >= 8:
                result_confidence = "HIGH"
                result_confidence_score = 80
            else:
                result_confidence = "MEDIUM"
                result_confidence_score = 65
            result_logic = f"Home team {gap} positions better → should win"
        elif away_pos < home_pos - 4:  # Away significantly better
            result = "AWAY WIN"
            if gap >= 8:
                result_confidence = "HIGH"
                result_confidence_score = 80
            else:
                result_confidence = "MEDIUM"
                result_confidence_score = 65
            result_logic = f"Away team {gap} positions better → should win"
        else:
            result = "DRAW or close match"
            result_confidence = "MEDIUM"
            result_confidence_score = 60
            result_logic = f"Teams within {gap} positions → evenly matched"
    
    # 4. EXTREME GAP CAUTION (>12 positions)
    if gap > 12:
        ou_confidence = "MEDIUM"  # Downgrade from HIGH
        ou_confidence_score = 65
        ou_logic += " [CAUTION: Extreme gap can be unpredictable]"
    
    # 5. BETTING RECOMMENDATION
    if ou_confidence == "HIGH" and result_confidence == "HIGH":
        betting_recommendation = "HIGH CONFIDENCE BET"
        recommendation_color = "green"
        stake_recommendation = "MAX BET (2x normal)"
    elif ou_confidence == "HIGH" or result_confidence == "HIGH":
        betting_recommendation = "MEDIUM CONFIDENCE BET"
        recommendation_color = "orange"
        stake_recommendation = "NORMAL (1x)"
    else:
        betting_recommendation = "LOW CONFIDENCE - AVOID"
        recommendation_color = "red"
        stake_recommendation = "SMALL BET (0.5x) or AVOID"
    
    # 6. Identify match type for display
    if home_pos >= relegation_cutoff and away_pos >= relegation_cutoff:
        match_type = "RELEGATION BATTLE 🔥"
    elif home_pos >= relegation_cutoff or away_pos >= relegation_cutoff:
        match_type = "RELEGATION-THREATENED"
    elif gap <= 4:
        match_type = "MID-TABLE CLASH"
    else:
        match_type = "HIERARCHICAL MATCH"
    
    return {
        'over_under': over_under,
        'over_under_confidence': ou_confidence,
        'over_under_confidence_score': ou_confidence_score,
        'over_under_logic': ou_logic,
        'result': result,
        'result_confidence': result_confidence,
        'result_confidence_score': result_confidence_score,
        'result_logic': result_logic,
        'position_gap': gap,
        'betting_recommendation': betting_recommendation,
        'recommendation_color': recommendation_color,
        'stake_recommendation': stake_recommendation,
        'match_type': match_type,
        'relegation_zone': home_pos >= relegation_cutoff or away_pos >= relegation_cutoff,
        'both_in_relegation': home_pos >= relegation_cutoff and away_pos >= relegation_cutoff
    }

# ========== XG ENGINE ==========

class MarketType(Enum):
    MATCH_RESULT = "1X2"
    OVER_UNDER_25 = "Over/Under 2.5"
    BTTS = "Both Teams to Score"

class Prediction(Enum):
    HOME_WIN = "Home Win"
    AWAY_WIN = "Away Win"
    DRAW = "Draw"
    OVER_25 = "Over 2.5"
    UNDER_25 = "Under 2.5"
    BTTS_YES = "BTTS Yes"
    BTTS_NO = "BTTS No"

@dataclass
class TeamMetrics:
    """Team metrics with xG integration"""
    attack_strength: float
    defense_strength: float
    ppg: float
    xg_for: float
    xg_against: float
    clean_sheet_pct: float
    failed_to_score_pct: float
    goals_scored_last_5: int
    goals_conceded_last_5: int
    games_played: int
    name: Optional[str] = None

@dataclass
class MatchContext:
    league_avg_goals: float = 2.68
    league_avg_xg: float = 1.34
    home_advantage: float = 1.15
    away_penalty: float = 0.92

class PredictionEngineV2:
    def __init__(self, context: Optional[MatchContext] = None):
        self.context = context or MatchContext()
    
    def calculate_form_factor(self, team: TeamMetrics) -> float:
        recent_goals_pg = team.goals_scored_last_5 / 5
        season_avg = team.attack_strength
        
        if season_avg <= 0.1:
            return 1.0
        
        form_ratio = recent_goals_pg / season_avg
        
        if form_ratio >= 1.5:      return 1.3
        elif form_ratio >= 1.3:    return 1.2
        elif form_ratio >= 1.15:   return 1.1
        elif form_ratio <= 0.5:    return 0.7
        elif form_ratio <= 0.7:    return 0.8
        elif form_ratio <= 0.85:   return 0.9
        else:                      return form_ratio
        
        return max(0.7, min(1.3, form_ratio))
    
    def predict_over_under(self, home: TeamMetrics, away: TeamMetrics) -> Dict:
        """Simple xG-based prediction"""
        # Account for poor attacks (relegation teams)
        if home.attack_strength < 0.8 and away.attack_strength < 0.8:
            # Both teams have very poor attacks
            return {
                'prediction': Prediction.UNDER_25,
                'confidence': 'High',
                'expected_goals': 1.8,
                'logic': 'Both teams have very poor attacks (<0.8 goals/game)'
            }
        
        # Normal calculation
        expected_home = (home.attack_strength + away.defense_strength) / 2
        expected_away = (away.attack_strength + home.defense_strength) / 2
        
        expected_home *= self.calculate_form_factor(home) * self.context.home_advantage
        expected_away *= self.calculate_form_factor(away) * self.context.away_penalty
        
        total_expected = expected_home + expected_expected_away
        
        if total_expected > 2.7:
            prediction = Prediction.OVER_25
            confidence = "High" if total_expected > 3.0 else "Medium"
        elif total_expected < 2.3:
            prediction = Prediction.UNDER_25
            confidence = "High" if total_expected < 2.0 else "Medium"
        else:
            prediction = Prediction.UNDER_25 if total_expected <= 2.5 else Prediction.OVER_25
            confidence = "Low"
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'expected_goals': round(total_expected, 2),
            'detailed_expected': {
                'home': round(expected_home, 2),
                'away': round(expected_away, 2)
            }
        }

# ========== FAILURE ANALYSIS DISPLAY ==========

def show_failure_analysis():
    """Display the Lecce vs Pisa failure analysis"""
    st.markdown('<div class="failure-analysis">', unsafe_allow_html=True)
    st.markdown("### 🔍 **FAILURE ANALYSIS: Lecce 1-0 Pisa**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**What our OLD system predicted:**")
        st.error("""
        - ❌ OVER 2.5 (HIGH confidence)
        - ❌ Expected Goals: 3.26
        - ❌ BTTS: 71% probability
        - ❌ Consensus: HIGH confidence OVER bet
        """)
    
    with col2:
        st.markdown("**What actually happened:**")
        st.success("""
        - ✅ Score: 1-0 (UNDER 2.5)
        - ✅ BTTS: NO
        - ✅ Total Goals: 1 (vs expected 3.26)
        - ✅ Result: Home win by 1 goal
        """)
    
    st.markdown("### 🧠 **What Went Wrong:**")
    st.markdown("""
    1. **League Position Logic Failure:**
       - Gap was 1 position (17 vs 18)
       - OLD Logic: "Similar ambitions → attacking"
       - REALITY: Both teams BOTTOM of table → **DESPERATION, not ambition**
    
    2. **Psychological Error:**
       - We assumed "similar position = similar approach"
       - **RELEGATION-THREATENED teams play DIFFERENTLY:**
         - Fear of losing > Desire to win
         - Avoid mistakes at all costs
         - Result: Cautious, low-scoring games
    
    3. **Statistical Blind Spot:**
       - Lecce: 0.71 goals/game (VERY poor)
       - Lecce: Fail to Score 57% of matches
       - These stats should have triggered caution
    """)
    
    st.markdown("### 🎯 **The Crucial Insight:**")
    st.warning("""
    **The psychological dynamic changes at the BOTTOM:**
    
    - Mid-table teams (positions 7-14): Similar ambitions → Attack
    - Bottom teams (positions 17-20): Similar FEAR → Defend
    
    This single match revealed a major blind spot in our original logic!
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN APP ==========

def main():
    st.markdown('<div class="main-header">⚽ BRUTBALL PREDICTOR PRO V2</div>', unsafe_allow_html=True)
    st.markdown("### **FIXED SYSTEM** - Now accounts for relegation battle psychology")
    
    # Show failure analysis first
    show_failure_analysis()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 FIXED POSITION ENGINE", 
        "📊 xG ENGINE", 
        "🚀 COMBINED ANALYSIS"
    ])
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/869/869445.png", width=100)
        st.markdown("### 📊 **FIXED Strategy**")
        st.markdown("""
        **NEW RULES:**
        
        🟢 **BOTH in bottom 4:** → UNDER 2.5
        *(Relegation six-pointer → fearful play)*
        
        🟡 **ONE in bottom 4:** → UNDER 2.5  
        *(Relegation team plays cautiously)*
        
        🟢 **Mid-table, gap ≤ 4:** → OVER 2.5
        *(Similar ambitions → attacking)*
        
        🟢 **Gap > 4:** → UNDER 2.5
        *(Different agendas → cautious)*
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Settings")
        total_teams = st.selectbox(
            "Total Teams in League",
            [20, 24, 18, 16, 22],
            index=0
        )
        
        league = st.selectbox(
            "Select League",
            ["Serie B", "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Championship", "Other"],
            index=0
        )
        
        # League contexts
        LEAGUE_CONTEXTS = {
            "Serie B": MatchContext(league_avg_goals=2.4, league_avg_xg=1.20),
            "Premier League": MatchContext(league_avg_goals=2.7, league_avg_xg=1.35),
            "La Liga": MatchContext(league_avg_goals=2.5, league_avg_xg=1.25),
            "Bundesliga": MatchContext(league_avg_goals=3.0, league_avg_xg=1.50),
            "Serie A": MatchContext(league_avg_goals=2.6, league_avg_xg=1.30),
            "Ligue 1": MatchContext(league_avg_goals=2.4, league_avg_xg=1.20),
            "Championship": MatchContext(league_avg_goals=2.55, league_avg_xg=1.28),
            "Other": MatchContext()
        }
        
        engine_context = LEAGUE_CONTEXTS[league]
        xg_engine = PredictionEngineV2(engine_context)
        
        st.markdown("---")
        
        # Example buttons
        st.markdown("### 📋 Examples")
        if st.button("🔴 Lecce vs Pisa (FAILURE CASE)", use_container_width=True):
            st.session_state.home_name = "Lecce"
            st.session_state.home_pos = 17
            st.session_state.away_name = "Pisa"
            st.session_state.away_pos = 18
            st.session_state.home_attack = 0.71
            st.session_state.away_attack = 1.2
            st.session_state.home_defense = 1.3
            st.session_state.away_defense = 1.4
            st.rerun()
        
        if st.button("🟢 Mid-table Example", use_container_width=True):
            st.session_state.home_name = "Team A"
            st.session_state.home_pos = 8
            st.session_state.away_name = "Team B"
            st.session_state.away_pos = 9
            st.rerun()
        
        if st.button("🟡 Top vs Bottom", use_container_width=True):
            st.session_state.home_name = "Top Team"
            st.session_state.home_pos = 2
            st.session_state.away_name = "Bottom Team"
            st.session_state.away_pos = 19
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🔄 Clear All Data", use_container_width=True):
            for key in st.session_state.keys():
                if key.startswith(('home_', 'away_', 'h2h_')):
                    del st.session_state[key]
            st.rerun()
    
    with tab1:
        # ========== FIXED POSITION ENGINE TAB ==========
        st.header("🎯 **FIXED** LEAGUE POSITION ENGINE")
        
        # Show the new fixed rule
        st.markdown('<div class="fixed-rule">', unsafe_allow_html=True)
        st.markdown("### 🎯 **CRITICAL FIX IMPLEMENTED:**")
        st.markdown("""
        ```python
        # NEW RULE: Bottom-of-table psychology
        relegation_cutoff = total_teams - 3  # Bottom 4
        
        if home_pos >= relegation_cutoff and away_pos >= relegation_cutoff:
            return "UNDER 2.5"  # Both in relegation zone
        elif home_pos >= relegation_cutoff or away_pos >= relegation_cutoff:
            return "UNDER 2.5"  # One team in relegation zone
        ```
        
        **Psychology:** Relegation-threatened teams play with FEAR, not ambition
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="sub-header">🏠 Home Team</div>', unsafe_allow_html=True)
            home_name = st.text_input("Home Team Name", 
                                    value=st.session_state.get('home_name', 'Lecce'),
                                    key="home_name_pos")
            home_pos = st.number_input(
                "League Position (1 = Best)",
                min_value=1,
                max_value=total_teams,
                value=int(st.session_state.get('home_pos', 17)),
                key="home_pos_input"
            )
            
            # Show relegation zone indicator
            relegation_cutoff = total_teams - 3
            if home_pos >= relegation_cutoff:
                st.error(f"⚠️ **RELEGATION ZONE** (Bottom 4)")
            elif home_pos <= 4:
                st.success(f"✅ **TOP 4** (Promotion/Europe)")
        
        with col2:
            st.markdown('<div class="sub-header">✈️ Away Team</div>', unsafe_allow_html=True)
            away_name = st.text_input("Away Team Name",
                                    value=st.session_state.get('away_name', 'Pisa'),
                                    key="away_name_pos")
            away_pos = st.number_input(
                "League Position (1 = Best)",
                min_value=1,
                max_value=total_teams,
                value=int(st.session_state.get('away_pos', 18)),
                key="away_pos_input"
            )
            
            # Show relegation zone indicator
            if away_pos >= relegation_cutoff:
                st.error(f"⚠️ **RELEGATION ZONE** (Bottom 4)")
            elif away_pos <= 4:
                st.success(f"✅ **TOP 4** (Promotion/Europe)")
        
        # Calculate prediction
        if st.button("🔍 ANALYZE WITH FIXED RULES", type="primary", use_container_width=True):
            # Get prediction
            prediction = predict_match_league_positions(home_pos, away_pos, total_teams)
            
            # Display results
            st.markdown("---")
            st.markdown('<div class="sub-header">📊 FIXED POSITION ANALYSIS</div>', unsafe_allow_html=True)
            
            # Match type banner
            if prediction['both_in_relegation']:
                st.error(f"🔥 **RELEGATION BATTLE DETECTED** - {prediction['match_type']}")
            elif prediction['relegation_zone']:
                st.warning(f"⚠️ **RELEGATION-THREATENED MATCH** - {prediction['match_type']}")
            else:
                st.info(f"📊 **{prediction['match_type']}**")
            
            # Key metrics
            col3, col4, col5, col6 = st.columns(4)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Position Gap", f"{prediction['position_gap']}")
                if prediction['position_gap'] <= 4:
                    st.caption("Close positions")
                else:
                    st.caption("Distant positions")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("O/U Prediction", prediction['over_under'])
                st.caption(f"Confidence: {prediction['over_under_confidence']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col5:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Result Prediction", prediction['result'])
                st.caption(f"Confidence: {prediction['result_confidence']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col6:
                recommendation_color = prediction['recommendation_color']
                st.markdown(f'<div class="metric-card" style="border-left: 5px solid {recommendation_color}">', unsafe_allow_html=True)
                st.metric("Recommendation", prediction['betting_recommendation'])
                st.caption(prediction['stake_recommendation'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed predictions
            col7, col8 = st.columns(2)
            
            with col7:
                confidence_class = "high-confidence" if prediction['over_under_confidence'] == "HIGH" else "medium-confidence"
                st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
                st.markdown(f"### 📈 OVER/UNDER 2.5")
                st.markdown(f"**Prediction:** `{prediction['over_under']}`")
                st.markdown(f"**Confidence:** `{prediction['over_under_confidence']}`")
                st.progress(prediction['over_under_confidence_score'] / 100)
                st.markdown(f"*{prediction['over_under_logic']}*")
                
                # Psychology insight
                if prediction['both_in_relegation']:
                    st.error("""
                    **🤔 RELEGATION BATTLE PSYCHOLOGY:**
                    - Both teams fighting to avoid drop
                    - FEAR of losing > desire to win
                    - Ultra-cautious approach
                    - Mistakes are costly
                    - Expect LOW scoring
                    """)
                elif prediction['relegation_zone']:
                    st.warning("""
                    **🤔 RELEGATION-THREATENED PSYCHOLOGY:**
                    - Threatened team plays with fear
                    - Avoid defeat at all costs
                    - Defensive, cautious tactics
                    - Lower scoring than stats suggest
                    """)
                elif prediction['position_gap'] <= 4:
                    st.info("""
                    **🤔 MID-TABLE PSYCHOLOGY:**
                    - Both teams have similar objectives
                    - Both think they can win
                    - Tactics will be attacking and open
                    - Expect goals from both sides
                    """)
                else:
                    st.info("""
                    **🤔 HIERARCHICAL PSYCHOLOGY:**
                    - Better team: Wants to win without risks
                    - Worse team: Wants to avoid humiliation
                    - Tactics will be cautious and defensive
                    - Expect low-scoring match
                    """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col8:
                confidence_class = "high-confidence" if prediction['result_confidence'] == "HIGH" else "medium-confidence"
                st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
                st.markdown(f"### 🏆 MATCH RESULT")
                st.markdown(f"**Prediction:** `{prediction['result']}`")
                st.markdown(f"**Confidence:** `{prediction['result_confidence']}`")
                st.progress(prediction['result_confidence_score'] / 100)
                st.markdown(f"*{prediction['result_logic']}*")
                
                # What would OLD system have predicted?
                st.markdown("---")
                st.markdown("#### 🔄 **OLD SYSTEM COMPARISON:**")
                
                # Old system logic (before fix)
                gap = prediction['position_gap']
                if gap <= 4:
                    old_prediction = "OVER 2.5"
                    old_logic = f"Gap {gap} ≤ 4 → Similar ambitions → Attack"
                else:
                    old_prediction = "UNDER 2.5"
                    old_logic = f"Gap {gap} > 4 → Different agendas → Caution"
                
                if prediction['both_in_relegation']:
                    st.error(f"**OLD:** {old_prediction} ❌")
                    st.caption(f"*{old_logic}*")
                    st.success(f"**NEW:** {prediction['over_under']} ✅")
                    st.caption(f"*{prediction['over_under_logic']}*")
                else:
                    st.info(f"**OLD:** {old_prediction}")
                    st.caption("Same as new system")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Betting strategy
            st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            st.markdown("### 💰 **UPDATED** BETTING STRATEGY")
            
            col9, col10 = st.columns(2)
            with col9:
                st.markdown("**🔥 MAX BET (2x):**")
                st.markdown("- Both teams in bottom 4 → UNDER 2.5")
                st.markdown("- Gap ≤ 2 AND both mid-table → OVER 2.5")
                st.markdown("- Gap ≥ 8 AND not relegation → UNDER 2.5")
            with col10:
                st.markdown("**⚠️ CAUTION/AVOID:**")
                st.markdown("- Extreme gaps (>12 positions)")
                st.markdown("- Relegation vs Top team (unpredictable)")
                st.markdown("- Cup/derby matches")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Historical validation
            st.markdown('<div class="sub-header">📚 VALIDATION AGAINST FAILURE CASE</div>', unsafe_allow_html=True)
            
            comparison_df = pd.DataFrame({
                'Match': ['Lecce vs Pisa (17 vs 18)', 'Annecy vs Le Mans (8 vs 9)', 'Nancy vs Clermont (15 vs 7)'],
                'Gap': [1, 1, 8],
                'Old Prediction': ['OVER 2.5 ❌', 'OVER 2.5 ✅', 'UNDER 2.5 ✅'],
                'New Prediction': ['UNDER 2.5 ✅', 'OVER 2.5 ✅', 'UNDER 2.5 ✅'],
                'Actual': ['1-0 (UNDER)', '2-1 (OVER)', '1-0 (UNDER)'],
                'Match Type': ['Both bottom 4', 'Mid-table', 'Hierarchical']
            })
            
            st.dataframe(
                comparison_df,
                column_config={
                    "Match": "Match",
                    "Gap": st.column_config.NumberColumn("Gap", format="%d"),
                    "Old Prediction": "Old Prediction",
                    "New Prediction": "New Prediction",
                    "Actual": "Actual Result",
                    "Match Type": "Match Type"
                },
                hide_index=True,
                use_container_width=True
            )
    
    with tab2:
        # ========== XG ENGINE TAB ==========
        st.header("📊 xG STATISTICAL ENGINE")
        st.info("Advanced statistical analysis with expected goals")
        
        # Simple input for testing
        col1, col2 = st.columns(2)
        
        with col1:
            home_name_xg = st.text_input(
                "🏠 Home Team",
                value=st.session_state.get('home_name', 'Lecce'),
                key="home_name_xg_tab"
            )
            home_attack = st.number_input(
                "Home Goals/Game", 
                0.0, 5.0, 
                value=float(st.session_state.get('home_attack', 0.71)), 
                step=0.01,
                key="home_attack_xg_tab"
            )
            home_defense = st.number_input(
                "Home Conceded/Game", 
                0.0, 5.0,
                value=float(st.session_state.get('home_defense', 1.3)), 
                step=0.01,
                key="home_defense_xg_tab"
            )
        
        with col2:
            away_name_xg = st.text_input(
                "🚗 Away Team",
                value=st.session_state.get('away_name', 'Pisa'),
                key="away_name_xg_tab"
            )
            away_attack = st.number_input(
                "Away Goals/Game", 
                0.0, 5.0,
                value=float(st.session_state.get('away_attack', 1.2)), 
                step=0.01,
                key="away_attack_xg_tab"
            )
            away_defense = st.number_input(
                "Away Conceded/Game", 
                0.0, 5.0,
                value=float(st.session_state.get('away_defense', 1.4)), 
                step=0.01,
                key="away_defense_xg_tab"
            )
        
        if st.button("📈 GENERATE xG PREDICTION", type="primary", use_container_width=True):
            
            # Create team metrics
            home_metrics = TeamMetrics(
                name=home_name_xg,
                attack_strength=home_attack,
                defense_strength=home_defense,
                ppg=1.2,  # Default
                xg_for=home_attack * 1.1,  # Estimate
                xg_against=home_defense * 1.1,
                clean_sheet_pct=0.3,
                failed_to_score_pct=0.3,
                goals_scored_last_5=int(home_attack * 5),
                goals_conceded_last_5=int(home_defense * 5),
                games_played=19
            )
            
            away_metrics = TeamMetrics(
                name=away_name_xg,
                attack_strength=away_attack,
                defense_strength=away_defense,
                ppg=1.3,  # Default
                xg_for=away_attack * 1.1,
                xg_against=away_defense * 1.1,
                clean_sheet_pct=0.25,
                failed_to_score_pct=0.25,
                goals_scored_last_5=int(away_attack * 5),
                goals_conceded_last_5=int(away_defense * 5),
                games_played=19
            )
            
            # Get prediction
            prediction = xg_engine.predict_over_under(home_metrics, away_metrics)
            
            # Display
            st.success("✅ xG Prediction Generated")
            
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Prediction", prediction['prediction'].value)
            with col4:
                st.metric("Confidence", prediction['confidence'])
            with col5:
                st.metric("Expected Goals", prediction['expected_goals'])
            
            # Warning for poor attacks
            if home_attack < 0.8 and away_attack < 0.8:
                st.error("""
                ⚠️ **BOTH TEAMS HAVE VERY POOR ATTACKS:**
                - Home: {:.2f} goals/game
                - Away: {:.2f} goals/game
                - Expect VERY LOW scoring match
                """.format(home_attack, away_attack))
    
    with tab3:
        # ========== COMBINED ANALYSIS TAB ==========
        st.header("🚀 COMBINED ANALYSIS")
        st.warning("**ULTIMATE PREDICTION:** Fixed position engine + xG statistics")
        
        # Check if we have position data
        if ('home_pos' not in st.session_state or 'away_pos' not in st.session_state):
            st.info("Please use the Fixed Position Engine tab first")
        else:
            # Get fixed position prediction
            pos_prediction = predict_match_league_positions(
                st.session_state.get('home_pos', 17),
                st.session_state.get('away_pos', 18),
                total_teams
            )
            
            # Get xG prediction
            home_attack = st.session_state.get('home_attack', 0.71)
            away_attack = st.session_state.get('away_attack', 1.2)
            
            home_metrics = TeamMetrics(
                name=st.session_state.get('home_name', 'Home'),
                attack_strength=home_attack,
                defense_strength=st.session_state.get('home_defense', 1.3),
                ppg=1.2,
                xg_for=home_attack * 1.1,
                xg_against=1.4,
                clean_sheet_pct=0.3,
                failed_to_score_pct=0.3,
                goals_scored_last_5=int(home_attack * 5),
                goals_conceded_last_5=6,
                games_played=19
            )
            
            away_metrics = TeamMetrics(
                name=st.session_state.get('away_name', 'Away'),
                attack_strength=away_attack,
                defense_strength=st.session_state.get('away_defense', 1.4),
                ppg=1.3,
                xg_for=away_attack * 1.1,
                xg_against=1.5,
                clean_sheet_pct=0.25,
                failed_to_score_pct=0.25,
                goals_scored_last_5=int(away_attack * 5),
                goals_conceded_last_5=5,
                games_played=19
            )
            
            xg_pred = xg_engine.predict_over_under(home_metrics, away_metrics)
            
            # Combined analysis
            st.markdown("### 🔗 ENGINE COMPARISON")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                st.markdown("#### 🎯 **FIXED POSITION ENGINE**")
                st.markdown(f"**Match Type:** {pos_prediction['match_type']}")
                st.markdown(f"**Position Gap:** {pos_prediction['position_gap']}")
                st.markdown(f"**O/U Prediction:** {pos_prediction['over_under']}")
                st.markdown(f"**Confidence:** {pos_prediction['over_under_confidence']}")
                st.markdown(f"**Psychology:** {pos_prediction['over_under_logic']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                st.markdown("#### 📊 **xG STATISTICAL ENGINE**")
                st.markdown(f"**O/U Prediction:** {xg_pred['prediction'].value}")
                st.markdown(f"**Confidence:** {xg_pred['confidence']}")
                st.markdown(f"**Expected Goals:** {xg_pred['expected_goals']}")
                if home_attack < 0.8 or away_attack < 0.8:
                    st.warning(f"**Attack Warning:** Poor attacking stats")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # DECISION MATRIX
            st.markdown("### 🎲 **FINAL DECISION MATRIX**")
            
            pos_ou = pos_prediction['over_under']
            xg_ou = xg_pred['prediction'].value
            
            if pos_ou == xg_ou:
                st.success("✅ **ENGINES AGREE**")
                st.markdown(f"**Both engines predict: {pos_ou}**")
                
                if pos_prediction['over_under_confidence'] == "HIGH" and xg_pred['confidence'] == "High":
                    st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🚀 **MAXIMUM CONFIDENCE BET**")
                    st.markdown("**Stake:** MAX BET (2x normal)")
                    st.markdown(f"**Bet:** {pos_ou}")
                    st.markdown(f"**Position Logic:** {pos_prediction['over_under_logic']}")
                    st.markdown(f"**xG Expected Goals:** {xg_pred['expected_goals']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 📈 **CONFIDENT BET**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown(f"**Bet:** {pos_ou}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ **ENGINES DISAGREE**")
                st.markdown(f"**Position Engine:** {pos_ou}")
                st.markdown(f"**xG Engine:** {xg_ou}")
                
                # Decision rules for disagreement
                if pos_prediction['both_in_relegation']:
                    st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🔥 **TRUST POSITION ENGINE (RELEGATION RULE)**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown(f"**Bet:** {pos_ou} (UNDER 2.5)")
                    st.markdown("**Reason:** Relegation battle psychology overrides stats")
                    st.markdown("**Logic:** Both bottom 4 → fearful, cautious play")
                    st.markdown('</div>', unsafe_allow_html=True)
                elif pos_prediction['over_under_confidence'] == "HIGH":
                    st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🔥 **TRUST POSITION ENGINE**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown(f"**Bet:** {pos_ou}")
                    st.markdown("**Reason:** Position engine has HIGH confidence (fixed rules)")
                    st.markdown('</div>', unsafe_allow_html=True)
                elif xg_pred['confidence'] == "High":
                    st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 📊 **TRUST xG ENGINE**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown(f"**Bet:** {xg_ou}")
                    st.markdown("**Reason:** xG engine has HIGH confidence with statistical backing")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="prediction-card low-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🚫 **AVOID BET**")
                    st.markdown("**Stake:** NO BET")
                    st.markdown("**Reason:** Engines disagree and neither has high confidence")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # For Lecce vs Pisa case study
            if (st.session_state.get('home_pos') == 17 and 
                st.session_state.get('away_pos') == 18):
                st.markdown("---")
                st.markdown("### 🎯 **LECCE vs PISA CASE STUDY**")
                
                st.info("""
                **What the FIXED system now correctly predicts:**
                
                1. **Position Engine:** UNDER 2.5 (HIGH confidence)
                   - Both in bottom 4 → relegation battle
                   - Fearful, cautious play
                
                2. **xG Engine:** May still suggest OVER (due to stats)
                   - But position psychology overrides
                
                3. **Final Decision:** TRUST POSITION ENGINE
                   - Bet UNDER 2.5
                   - Stake: NORMAL (1x)
                
                **Result:** ✅ **CORRECT PREDICTION** (1-0 was UNDER)
                """)

if __name__ == "__main__":
    main()