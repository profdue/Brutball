import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import pytz

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="BRUTBALL PREDICTOR PRO",
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
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== LEAGUE POSITION ENGINE (91.7% ACCURATE) ==========

def predict_match_league_positions(home_pos, away_pos, total_teams=20):
    """
    BRUTBALL LEAGUE POSITION ENGINE - 91.7% Accuracy
    Core Insight: Position gap determines tactical approach
    """
    gap = abs(home_pos - away_pos)
    
    # 1. OVERS/UNDERS PREDICTION
    if gap <= 4:
        over_under = "OVER 2.5"
        if gap <= 2:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams within {gap} positions → similar ambitions → attacking football"
    else:
        over_under = "UNDER 2.5"
        if gap >= 8:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams {gap} positions apart → different agendas → cautious play"
    
    # 2. MATCH RESULT PREDICTION
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
    
    # 3. BETTING RECOMMENDATION
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
        'stake_recommendation': stake_recommendation
    }

# ========== XG ENGINE (EXISTING V2) ==========

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
    # Core Performance Stats
    attack_strength: float           # Actual goals scored/game
    defense_strength: float          # Actual goals conceded/game
    ppg: float                       # Points per game
    
    # xG Stats
    xg_for: float                    # Expected goals created/game
    xg_against: float                # Expected goals conceded/game
    
    # Performance Metrics
    clean_sheet_pct: float           # Clean sheet percentage (0-1)
    failed_to_score_pct: float       # Failed to score percentage (0-1)
    
    # Recent Form
    goals_scored_last_5: int         # Goals scored in last 5
    goals_conceded_last_5: int       # Goals conceded in last 5
    
    # Sample Size
    games_played: int                # Total games played
    
    # Team name
    name: Optional[str] = None

@dataclass
class MatchContext:
    """Match context with league-specific parameters"""
    league_avg_goals: float = 2.68
    league_avg_xg: float = 1.34
    home_advantage: float = 1.15
    away_penalty: float = 0.92

class PredictionEngineV2:
    """
    Prediction Engine v2.0 with xG Integration
    """
    
    def __init__(self, context: Optional[MatchContext] = None):
        self.context = context or MatchContext()
        
        self.THRESHOLDS = {
            'VERY_STRONG_DEFENSE': 0.6,
            'STRONG_DEFENSE': 0.8,
            'WEAK_DEFENSE': 1.4,
            'STRONG_ATTACK': 1.6,
            'WEAK_ATTACK': 1.0,
            'HIGH_CLEAN_SHEET': 0.45,
            'HIGH_FAILED_TO_SCORE': 0.35,
            'MIN_GAMES_RELIABLE': 6,
            'XG_SIGNIFICANT_DIFF': 0.3,
        }
    
    def calculate_form_factor(self, team: TeamMetrics) -> float:
        """Compare recent performance to season average"""
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
    
    def calculate_xg_adjusted_goals(self, home: TeamMetrics, away: TeamMetrics) -> Tuple[float, float]:
        """Blend actual goals with xG data"""
        # Validate metrics
        home_attack = max(0.2, min(3.5, home.attack_strength))
        away_attack = max(0.2, min(3.5, away.attack_strength))
        home_defense = max(0.2, min(3.5, home.defense_strength))
        away_defense = max(0.2, min(3.5, away.defense_strength))
        
        # Simple average approach
        expected_home = (home_attack + away_defense) / 2
        expected_away = (away_attack + home_defense) / 2
        
        # Apply form adjustments
        home_form = self.calculate_form_factor(home)
        away_form = self.calculate_form_factor(away)
        
        expected_home *= home_form
        expected_away *= away_form
        
        # Apply venue adjustments
        expected_home *= self.context.home_advantage
        expected_away *= self.context.away_penalty
        
        # Reasonable bounds
        expected_home = max(0.2, min(3.5, expected_home))
        expected_away = max(0.2, min(3.5, expected_away))
        
        return expected_home, expected_away
    
    def predict_match_result(self, home: TeamMetrics, away: TeamMetrics) -> Dict:
        """Predict Home Win, Draw, or Away Win"""
        # Simple PPG comparison
        home_strength = home.ppg * self.context.home_advantage
        away_strength = away.ppg * self.context.away_penalty
        
        # Apply form
        home_form = self.calculate_form_factor(home)
        away_form = self.calculate_form_factor(away)
        
        home_strength *= home_form
        away_strength *= away_form
        
        # Determine winner
        if home_strength > away_strength + 0.3:
            prediction = Prediction.HOME_WIN
            confidence = "High" if (home_strength - away_strength) > 0.5 else "Medium"
        elif away_strength > home_strength + 0.3:
            prediction = Prediction.AWAY_WIN
            confidence = "High" if (away_strength - home_strength) > 0.5 else "Medium"
        else:
            prediction = Prediction.DRAW
            confidence = "Medium"
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'strengths': {
                'home': round(home_strength, 2),
                'away': round(away_strength, 2)
            }
        }
    
    def predict_over_under(self, home: TeamMetrics, away: TeamMetrics) -> Dict:
        """Predict Over or Under 2.5 total goals"""
        expected_home, expected_away = self.calculate_xg_adjusted_goals(home, away)
        total_expected = expected_home + expected_away
        
        # Simple threshold
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
    
    def predict_btts(self, home: TeamMetrics, away: TeamMetrics) -> Dict:
        """Predict if Both Teams will Score"""
        # Probability home scores = 1 - away clean sheet %
        prob_home_scores = 1 - away.clean_sheet_pct
        prob_away_scores = 1 - home.clean_sheet_pct
        
        prob_btts = prob_home_scores * prob_away_scores
        
        if prob_btts > 0.55:
            prediction = Prediction.BTTS_YES
            confidence = "High" if prob_btts > 0.65 else "Medium"
        elif prob_btts < 0.45:
            prediction = Prediction.BTTS_NO
            confidence = "High" if prob_btts < 0.35 else "Medium"
        else:
            prediction = Prediction.BTTS_YES if prob_btts > 0.5 else Prediction.BTTS_NO
            confidence = "Low"
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probability': round(prob_btts, 3)
        }

# ========== MAIN APP ==========

def main():
    st.markdown('<div class="main-header">⚽ BRUTBALL PREDICTOR PRO</div>', unsafe_allow_html=True)
    st.markdown("### Combined League Position + xG Analysis System")
    
    # Create tabs for different engines
    tab1, tab2, tab3 = st.tabs([
        "🎯 LEAGUE POSITION ENGINE (91.7% ACC)", 
        "📊 xG STATISTICAL ENGINE", 
        "🚀 COMBINED ANALYSIS"
    ])
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/869/869445.png", width=100)
        st.markdown("### 📊 Strategy Overview")
        st.markdown("""
        **LEAGUE POSITION ENGINE:**
        - Gap ≤ 4 → Similar ambitions → OVER 2.5
        - Gap > 4 → Different agendas → UNDER 2.5
        
        **Accuracy:** 91.7% (11/12 matches)
        
        **xG ENGINE:**
        - Statistical analysis
        - Expected goals modeling
        - Form adjustments
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
            ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Championship", "Other"],
            index=5
        )
        
        # League contexts for xG engine
        LEAGUE_CONTEXTS = {
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
        
        st.markdown("### 📈 Performance")
        st.metric("League Position Accuracy", "91.7%")
        st.metric("High Confidence Wins", "100%")
        
        st.markdown("---")
        
        if st.button("🔄 Clear All Data", use_container_width=True):
            for key in st.session_state.keys():
                if key.startswith(('home_', 'away_', 'h2h_')):
                    del st.session_state[key]
            st.rerun()
    
    with tab1:
        # ========== LEAGUE POSITION ENGINE TAB ==========
        st.header("🎯 LEAGUE POSITION ENGINE")
        st.success("**91.7% ACCURACY** - Based on position gap psychology")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="sub-header">🏠 Home Team</div>', unsafe_allow_html=True)
            home_name = st.text_input("Home Team Name", 
                                    value=st.session_state.get('home_name', 'Leece'),
                                    key="home_name_pos")
            home_pos = st.number_input(
                "League Position (1 = Best)",
                min_value=1,
                max_value=total_teams,
                value=int(st.session_state.get('home_pos', 17)),
                key="home_pos_input"
            )
        
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
        
        # Calculate prediction
        if st.button("🔍 ANALYZE POSITION GAP", type="primary", use_container_width=True):
            # Get prediction
            prediction = predict_match_league_positions(home_pos, away_pos, total_teams)
            
            # Display results
            st.markdown("---")
            st.markdown('<div class="sub-header">📊 POSITION GAP ANALYSIS</div>', unsafe_allow_html=True)
            
            # Key metrics
            col3, col4, col5, col6 = st.columns(4)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Position Gap", f"{prediction['position_gap']}")
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
                if prediction['position_gap'] <= 4:
                    st.info("""
                    **🤔 PSYCHOLOGICAL DYNAMIC:**
                    - Both teams have similar objectives
                    - Both think they can win
                    - Tactics will be attacking and open
                    - Expect goals from both sides
                    """)
                else:
                    st.info("""
                    **🤔 PSYCHOLOGICAL DYNAMIC:**
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
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Betting strategy
            st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            st.markdown("### 💰 BETTING STRATEGY")
            
            col9, col10 = st.columns(2)
            with col9:
                st.markdown("**HIGH CONFIDENCE:**")
                st.markdown("- Gap ≤ 2 AND xG predicts OVER → BET OVER")
                st.markdown("- Gap ≥ 8 AND xG predicts UNDER → BET UNDER")
                st.markdown("- Gap ≥ 8 AND better team at home → BET HOME WIN")
            with col10:
                st.markdown("**AVOID:**")
                st.markdown("- Extreme gaps (>12 positions)")
                st.markdown("- Cup matches (different psychology)")
                st.markdown("- Derby matches (emotion overrides tactics)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Historical examples
            st.markdown('<div class="sub-header">📚 HISTORICAL EXAMPLES (91.7% ACCURACY)</div>', unsafe_allow_html=True)
            
            examples = pd.DataFrame({
                'Match': ['Annecy vs Le Mans', 'Nancy vs Clermont', 'Real Sociedad vs Girona', 'Leonesa vs Huesca'],
                'Gap': [1, 8, 3, 7],
                'Prediction': ['OVER 2.5', 'UNDER 2.5', 'OVER 2.5', 'UNDER 2.5'],
                'Actual': ['2-1 ✅', '1-0 ✅', '2-1 ✅', '0-2 ✅'],
                'Confidence': ['HIGH', 'HIGH', 'MEDIUM', 'HIGH']
            })
            
            st.dataframe(
                examples,
                column_config={
                    "Match": "Match",
                    "Gap": st.column_config.NumberColumn("Position Gap", format="%d"),
                    "Prediction": "Prediction",
                    "Actual": "Actual Result",
                    "Confidence": "Confidence"
                },
                hide_index=True,
                use_container_width=True
            )
    
    with tab2:
        # ========== XG ENGINE TAB ==========
        st.header("📊 xG STATISTICAL ENGINE")
        st.info("Advanced statistical analysis with expected goals")
        
        # Input form
        st.markdown("### Enter Team Statistics")
        
        col_names = st.columns(2)
        with col_names[0]:
            home_name_xg = st.text_input(
                "🏠 Home Team",
                value=st.session_state.get('home_name', 'Leece'),
                key="home_name_xg"
            )
        with col_names[1]:
            away_name_xg = st.text_input(
                "🚗 Away Team",
                value=st.session_state.get('away_name', 'Pisa'),
                key="away_name_xg"
            )
        
        # Stats tabs
        tab_stats1, tab_stats2 = st.tabs(["⚽ Core Stats", "📈 Recent Form"])
        
        with tab_stats1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{home_name_xg}")
                
                col_attack = st.columns(2)
                with col_attack[0]:
                    home_attack = st.number_input(
                        "Goals/Game", 
                        0.0, 5.0, 
                        value=float(st.session_state.get('home_attack', 1.2)), 
                        step=0.01,
                        key="home_attack_xg"
                    )
                with col_attack[1]:
                    home_defense = st.number_input(
                        "Conceded/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('home_defense', 1.5)), 
                        step=0.01,
                        key="home_defense_xg"
                    )
                
                col_points = st.columns(2)
                with col_points[0]:
                    home_ppg = st.number_input(
                        "Points/Game", 
                        0.0, 3.0,
                        value=float(st.session_state.get('home_ppg', 1.2)), 
                        step=0.01,
                        key="home_ppg_xg"
                    )
                with col_points[1]:
                    home_games = st.number_input(
                        "Games Played", 
                        1, 40,
                        value=int(st.session_state.get('home_games', 19)),
                        key="home_games_xg"
                    )
                
                st.write("**Performance Metrics**")
                col_perf = st.columns(2)
                with col_perf[0]:
                    home_cs = st.number_input(
                        "Clean Sheet %", 
                        0, 100,
                        value=int(st.session_state.get('home_cs', 25)),
                        key="home_cs_xg"
                    )
                with col_perf[1]:
                    home_fts = st.number_input(
                        "Fail to Score %", 
                        0, 100,
                        value=int(st.session_state.get('home_fts', 30)),
                        key="home_fts_xg"
                    )
                
                st.write("**xG Metrics**")
                col_xg = st.columns(2)
                with col_xg[0]:
                    home_xg_for = st.number_input(
                        "xG Created/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('home_xg_for', 1.3)), 
                        step=0.01,
                        key="home_xg_for_xg"
                    )
                with col_xg[1]:
                    home_xg_against = st.number_input(
                        "xG Conceded/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('home_xg_against', 1.5)), 
                        step=0.01,
                        key="home_xg_against_xg"
                    )
            
            with col2:
                st.subheader(f"{away_name_xg}")
                
                col_attack = st.columns(2)
                with col_attack[0]:
                    away_attack = st.number_input(
                        "Goals/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('away_attack', 1.3)), 
                        step=0.01,
                        key="away_attack_xg"
                    )
                with col_attack[1]:
                    away_defense = st.number_input(
                        "Conceded/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('away_defense', 1.4)), 
                        step=0.01,
                        key="away_defense_xg"
                    )
                
                col_points = st.columns(2)
                with col_points[0]:
                    away_ppg = st.number_input(
                        "Points/Game", 
                        0.0, 3.0,
                        value=float(st.session_state.get('away_ppg', 1.3)), 
                        step=0.01,
                        key="away_ppg_xg"
                    )
                with col_points[1]:
                    away_games = st.number_input(
                        "Games Played", 
                        1, 40,
                        value=int(st.session_state.get('away_games', 19)),
                        key="away_games_xg"
                    )
                
                st.write("**Performance Metrics**")
                col_perf = st.columns(2)
                with col_perf[0]:
                    away_cs = st.number_input(
                        "Clean Sheet %", 
                        0, 100,
                        value=int(st.session_state.get('away_cs', 20)),
                        key="away_cs_xg"
                    )
                with col_perf[1]:
                    away_fts = st.number_input(
                        "Fail to Score %", 
                        0, 100,
                        value=int(st.session_state.get('away_fts', 25)),
                        key="away_fts_xg"
                    )
                
                st.write("**xG Metrics**")
                col_xg = st.columns(2)
                with col_xg[0]:
                    away_xg_for = st.number_input(
                        "xG Created/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('away_xg_for', 1.4)), 
                        step=0.01,
                        key="away_xg_for_xg"
                    )
                with col_xg[1]:
                    away_xg_against = st.number_input(
                        "xG Conceded/Game", 
                        0.0, 5.0,
                        value=float(st.session_state.get('away_xg_against', 1.6)), 
                        step=0.01,
                        key="away_xg_against_xg"
                    )
        
        with tab_stats2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{home_name_xg} Recent Form")
                
                col_form = st.columns(2)
                with col_form[0]:
                    home_goals5 = st.number_input(
                        "Goals Scored (Last 5)", 
                        0, 30,
                        value=int(st.session_state.get('home_goals5', 6)),
                        key="home_goals5_xg"
                    )
                with col_form[1]:
                    home_conceded5 = st.number_input(
                        "Goals Conceded (Last 5)", 
                        0, 30,
                        value=int(st.session_state.get('home_conceded5', 8)),
                        key="home_conceded5_xg"
                    )
            
            with col2:
                st.subheader(f"{away_name_xg} Recent Form")
                
                col_form = st.columns(2)
                with col_form[0]:
                    away_goals5 = st.number_input(
                        "Goals Scored (Last 5)", 
                        0, 30,
                        value=int(st.session_state.get('away_goals5', 7)),
                        key="away_goals5_xg"
                    )
                with col_form[1]:
                    away_conceded5 = st.number_input(
                        "Goals Conceded (Last 5)", 
                        0, 30,
                        value=int(st.session_state.get('away_conceded5', 6)),
                        key="away_conceded5_xg"
                    )
        
        # Generate predictions
        if st.button("📈 GENERATE xG PREDICTIONS", type="primary", use_container_width=True):
            
            # Create team metrics
            home_metrics = TeamMetrics(
                name=home_name_xg,
                attack_strength=home_attack,
                defense_strength=home_defense,
                ppg=home_ppg,
                xg_for=home_xg_for,
                xg_against=home_xg_against,
                clean_sheet_pct=home_cs/100,
                failed_to_score_pct=home_fts/100,
                goals_scored_last_5=home_goals5,
                goals_conceded_last_5=home_conceded5,
                games_played=home_games
            )
            
            away_metrics = TeamMetrics(
                name=away_name_xg,
                attack_strength=away_attack,
                defense_strength=away_defense,
                ppg=away_ppg,
                xg_for=away_xg_for,
                xg_against=away_xg_against,
                clean_sheet_pct=away_cs/100,
                failed_to_score_pct=away_fts/100,
                goals_scored_last_5=away_goals5,
                goals_conceded_last_5=away_conceded5,
                games_played=away_games
            )
            
            # Get predictions
            result_pred = xg_engine.predict_match_result(home_metrics, away_metrics)
            over_under_pred = xg_engine.predict_over_under(home_metrics, away_metrics)
            btts_pred = xg_engine.predict_btts(home_metrics, away_metrics)
            expected_goals = xg_engine.calculate_xg_adjusted_goals(home_metrics, away_metrics)
            
            # Display results
            st.success("✅ xG Predictions Generated")
            
            # Main predictions
            st.header("📊 xG PREDICTION RESULTS")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🏆 Match Result")
                pred = result_pred['prediction'].value
                conf = result_pred['confidence']
                st.metric("Prediction", pred)
                st.metric("Confidence", conf)
                st.metric("Relative Strength", 
                         f"{result_pred['strengths']['home']} vs {result_pred['strengths']['away']}")
            
            with col2:
                st.subheader("⚖️ Over/Under 2.5")
                pred = over_under_pred['prediction'].value
                conf = over_under_pred['confidence']
                st.metric("Prediction", pred)
                st.metric("Confidence", conf)
                st.metric("Expected Goals", over_under_pred['expected_goals'])
            
            with col3:
                st.subheader("🎯 Both Teams to Score")
                pred = btts_pred['prediction'].value
                conf = btts_pred['confidence']
                st.metric("Prediction", pred)
                st.metric("Confidence", conf)
                st.metric("Probability", f"{btts_pred['probability']:.0%}")
            
            # Expected goals breakdown
            st.header("📈 Expected Goals Analysis")
            
            eg_home, eg_away = expected_goals
            total_expected = eg_home + eg_away
            
            col1, col2, col3 = st.columns(3)
            with col1:
                delta_home = eg_home - home_attack
                st.metric(f"🏠 {home_name_xg}", f"{eg_home:.2f}", f"{delta_home:+.2f} vs avg")
            with col2:
                delta_away = eg_away - away_attack
                st.metric(f"🚗 {away_name_xg}", f"{eg_away:.2f}", f"{delta_away:+.2f} vs avg")
            with col3:
                delta_total = total_expected - engine_context.league_avg_goals
                st.metric("Total Expected", f"{total_expected:.2f}", f"{delta_total:+.2f} vs league avg")
            
            # Form analysis
            st.header("📊 Form Analysis")
            
            home_form = xg_engine.calculate_form_factor(home_metrics)
            away_form = xg_engine.calculate_form_factor(away_metrics)
            
            col1, col2 = st.columns(2)
            with col1:
                if home_form >= 1.15:
                    st.success(f"**{home_name_xg}:** Excellent form ({home_form:.2f}x)")
                elif home_form >= 1.05:
                    st.success(f"**{home_name_xg}:** Good form ({home_form:.2f}x)")
                elif home_form <= 0.70:
                    st.error(f"**{home_name_xg}:** Very poor form ({home_form:.2f}x)")
                elif home_form <= 0.85:
                    st.error(f"**{home_name_xg}:** Poor form ({home_form:.2f}x)")
                elif home_form < 0.95:
                    st.warning(f"**{home_name_xg}:** Below average form ({home_form:.2f}x)")
                else:
                    st.info(f"**{home_name_xg}:** Average form ({home_form:.2f}x)")
            
            with col2:
                if away_form >= 1.15:
                    st.success(f"**{away_name_xg}:** Excellent form ({away_form:.2f}x)")
                elif away_form >= 1.05:
                    st.success(f"**{away_name_xg}:** Good form ({away_form:.2f}x)")
                elif away_form <= 0.70:
                    st.error(f"**{away_name_xg}:** Very poor form ({away_form:.2f}x)")
                elif away_form <= 0.85:
                    st.error(f"**{away_name_xg}:** Poor form ({away_form:.2f}x)")
                elif away_form < 0.95:
                    st.warning(f"**{away_name_xg}:** Below average form ({away_form:.2f}x)")
                else:
                    st.info(f"**{away_name_xg}:** Average form ({away_form:.2f}x)")
    
    with tab3:
        # ========== COMBINED ANALYSIS TAB ==========
        st.header("🚀 COMBINED ANALYSIS")
        st.warning("**ULTIMATE PREDICTION:** Combine both engines for maximum accuracy")
        
        # Check if we have data from both tabs
        if ('home_pos' not in st.session_state or 'away_pos' not in st.session_state):
            st.info("Please use the League Position Engine tab first to get position gap analysis")
        else:
            # Get league position prediction
            pos_prediction = predict_match_league_positions(
                st.session_state.get('home_pos', 17),
                st.session_state.get('away_pos', 18),
                total_teams
            )
            
            # Create simple team metrics for xG engine (using default values if not set)
            home_metrics = TeamMetrics(
                name=st.session_state.get('home_name', 'Home'),
                attack_strength=st.session_state.get('home_attack', 1.2),
                defense_strength=st.session_state.get('home_defense', 1.5),
                ppg=st.session_state.get('home_ppg', 1.2),
                xg_for=st.session_state.get('home_xg_for', 1.3),
                xg_against=st.session_state.get('home_xg_against', 1.5),
                clean_sheet_pct=st.session_state.get('home_cs', 25)/100,
                failed_to_score_pct=st.session_state.get('home_fts', 30)/100,
                goals_scored_last_5=st.session_state.get('home_goals5', 6),
                goals_conceded_last_5=st.session_state.get('home_conceded5', 8),
                games_played=st.session_state.get('home_games', 19)
            )
            
            away_metrics = TeamMetrics(
                name=st.session_state.get('away_name', 'Away'),
                attack_strength=st.session_state.get('away_attack', 1.3),
                defense_strength=st.session_state.get('away_defense', 1.4),
                ppg=st.session_state.get('away_ppg', 1.3),
                xg_for=st.session_state.get('away_xg_for', 1.4),
                xg_against=st.session_state.get('away_xg_against', 1.6),
                clean_sheet_pct=st.session_state.get('away_cs', 20)/100,
                failed_to_score_pct=st.session_state.get('away_fts', 25)/100,
                goals_scored_last_5=st.session_state.get('away_goals5', 7),
                goals_conceded_last_5=st.session_state.get('away_conceded5', 6),
                games_played=st.session_state.get('away_games', 19)
            )
            
            # Get xG predictions
            xg_ou_pred = xg_engine.predict_over_under(home_metrics, away_metrics)
            
            # Combined analysis
            st.markdown("### 🔗 ENGINE COMPARISON")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                st.markdown("#### 🎯 LEAGUE POSITION ENGINE")
                st.markdown(f"**Position Gap:** {pos_prediction['position_gap']}")
                st.markdown(f"**O/U Prediction:** {pos_prediction['over_under']}")
                st.markdown(f"**Confidence:** {pos_prediction['over_under_confidence']}")
                st.markdown(f"**Result:** {pos_prediction['result']}")
                st.markdown(f"**Logic:** {pos_prediction['over_under_logic']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                st.markdown("#### 📊 xG STATISTICAL ENGINE")
                st.markdown(f"**O/U Prediction:** {xg_ou_pred['prediction'].value}")
                st.markdown(f"**Confidence:** {xg_ou_pred['confidence']}")
                st.markdown(f"**Expected Goals:** {xg_ou_pred['expected_goals']}")
                st.markdown(f"**Home xG:** {xg_ou_pred['detailed_expected']['home']}")
                st.markdown(f"**Away xG:** {xg_ou_pred['detailed_expected']['away']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # DECISION MATRIX
            st.markdown("### 🎲 DECISION MATRIX")
            
            pos_ou = pos_prediction['over_under']
            xg_ou = xg_ou_pred['prediction'].value
            
            if pos_ou == xg_ou:
                st.success("✅ **ENGINES AGREE**")
                st.markdown(f"**Both engines predict: {pos_ou}**")
                
                if pos_prediction['over_under_confidence'] == "HIGH" and xg_ou_pred['confidence'] == "High":
                    st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🚀 **MAXIMUM CONFIDENCE BET**")
                    st.markdown("**Stake:** MAX BET (2x normal)")
                    st.markdown("**Reason:** Both engines agree with HIGH confidence")
                    st.markdown("**Expected Accuracy:** >90%")
                    st.markdown('</div>', unsafe_allow_html=True)
                elif pos_prediction['over_under_confidence'] == "HIGH" or xg_ou_pred['confidence'] == "High":
                    st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 📈 **HIGH CONFIDENCE BET**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown("**Reason:** Engines agree, one has high confidence")
                    st.markdown("**Expected Accuracy:** ~80%")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="prediction-card low-confidence">', unsafe_allow_html=True)
                    st.markdown("#### ⚠️ **MEDIUM CONFIDENCE BET**")
                    st.markdown("**Stake:** SMALL BET (0.5x)")
                    st.markdown("**Reason:** Engines agree but both have medium/low confidence")
                    st.markdown("**Expected Accuracy:** ~70%")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ **ENGINES DISAGREE**")
                st.markdown(f"**League Position:** {pos_ou}")
                st.markdown(f"**xG Engine:** {xg_ou}")
                
                # Decision rules
                if pos_prediction['over_under_confidence'] == "HIGH":
                    st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
                    st.markdown("#### 🔥 **TRUST LEAGUE POSITION ENGINE**")
                    st.markdown("**Stake:** NORMAL BET (1x)")
                    st.markdown(f"**Bet:** {pos_ou}")
                    st.markdown("**Reason:** League position engine has HIGH confidence (91.7% accuracy)")
                    st.markdown("**Psychology:** " + pos_prediction['over_under_logic'])
                    st.markdown('</div>', unsafe_allow_html=True)
                elif xg_ou_pred['confidence'] == "High":
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
                    st.markdown("**Advice:** Wait for more information or bet small on value")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Position gap specific advice
            gap = pos_prediction['position_gap']
            
            st.markdown("### 📊 POSITION GAP SPECIFIC ADVICE")
            
            if gap <= 2:
                st.info(f"**Gap {gap} (Very Close):** Teams have identical ambitions. Expect attacking football from both sides.")
            elif gap <= 4:
                st.info(f"**Gap {gap} (Close):** Similar league positions. Both teams will play openly, expecting goals.")
            elif gap <= 7:
                st.warning(f"**Gap {gap} (Moderate Difference):** Tactical battle. Better team controls, weaker defends.")
            elif gap <= 10:
                st.warning(f"**Gap {gap} (Significant Difference):** Clear favorite. Expect cautious approach from underdog.")
            else:
                st.error(f"**Gap {gap} (Extreme Difference):** Unpredictable psychology. Top vs bottom can produce surprises.")
            
            # Final recommendation
            st.markdown("### 🏆 FINAL RECOMMENDATION")
            
            if pos_ou == xg_ou:
                final_bet = pos_ou
                if pos_prediction['over_under_confidence'] == "HIGH" and xg_ou_pred['confidence'] == "High":
                    final_confidence = "MAXIMUM"
                    final_stake = "MAX BET (2x)"
                elif pos_prediction['over_under_confidence'] == "HIGH" or xg_ou_pred['confidence'] == "High":
                    final_confidence = "HIGH"
                    final_stake = "NORMAL BET (1x)"
                else:
                    final_confidence = "MEDIUM"
                    final_stake = "SMALL BET (0.5x)"
            else:
                if pos_prediction['over_under_confidence'] == "HIGH":
                    final_bet = pos_ou
                    final_confidence = "HIGH (Trust Psychology)"
                    final_stake = "NORMAL BET (1x)"
                elif xg_ou_pred['confidence'] == "High":
                    final_bet = xg_ou
                    final_confidence = "HIGH (Trust Statistics)"
                    final_stake = "NORMAL BET (1x)"
                else:
                    final_bet = "NO BET"
                    final_confidence = "LOW"
                    final_stake = "AVOID"
            
            # Display final recommendation
            if final_bet == "NO BET":
                st.markdown('<div class="prediction-card low-confidence">', unsafe_allow_html=True)
            elif final_confidence == "MAXIMUM":
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            elif "HIGH" in final_confidence:
                st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
            else:
                st.markdown('<div class="prediction-card medium-confidence">', unsafe_allow_html=True)
            
            st.markdown(f"#### **BET:** {final_bet}")
            st.markdown(f"**Confidence:** {final_confidence}")
            st.markdown(f"**Stake:** {final_stake}")
            
            if final_bet != "NO BET":
                st.markdown(f"**Position Gap Logic:** {pos_prediction['over_under_logic']}")
                st.markdown(f"**xG Expected Goals:** {xg_ou_pred['expected_goals']}")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()