import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import json
import math
from scipy.stats import poisson

# Page config
st.set_page_config(
    page_title="Complete Football Prediction Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        border-left: 5px solid #667eea;
        padding-left: 15px;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.9), rgba(118,75,162,0.9));
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    .prediction-card {
        background: linear-gradient(135deg, rgba(240,147,251,0.9), rgba(245,87,108,0.9));
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Confidence Levels */
    .confidence-high {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    /* Team Boxes */
    .team-box {
        border: 2px solid #4ECDC4;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        background: rgba(78, 205, 196, 0.08);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .factor-badge {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 25px;
        margin: 8px 5px;
        font-size: 0.85em;
        background: rgba(255, 107, 107, 0.15);
        border: 1px solid #FF6B6B;
        color: #FF6B6B;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .factor-badge:hover {
        background: rgba(255, 107, 107, 0.25);
        transform: scale(1.05);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
    }
    
    /* Input styling */
    .input-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 30px;
        margin-top: 40px;
        border-top: 1px solid #eee;
        font-size: 0.9em;
    }
    
    /* Value indicators */
    .value-positive {
        color: #00b09b;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .value-negative {
        color: #ff416c;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .value-neutral {
        color: #f7971e;
        font-weight: bold;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# League averages (La Liga example)
LEAGUE_AVG = {
    'shots_allowed': 12.0,
    'ppg': 1.50,
    'set_piece_pct': 0.20,
    'goals_conceded': 1.2
}

class CompletePredictionEngine:
    def __init__(self):
        self.reset_calculations()
        
    def reset_calculations(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.confidence = 0
        self.expected_values = {}
        self.key_factors = []
        self.betting_recommendations = []
        self.scoreline_probabilities = {}
        
    def calculate_injury_level(self, defenders_out):
        """2.1 Injury Level Calculation"""
        return min(10, defenders_out * 2)
    
    def calculate_goal_percentages(self, total_goals, open_play_goals, set_piece_goals, counter_attack_goals):
        """Calculate goal percentages"""
        if total_goals == 0:
            return 0, 0, 0
        open_play_pct = open_play_goals / total_goals
        set_piece_pct = set_piece_goals / total_goals
        counter_attack_pct = counter_attack_goals / total_goals
        return open_play_pct, set_piece_pct, counter_attack_pct
    
    def poisson_pmf(self, k, lambda_val):
        """Poisson probability mass function"""
        return (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
    
    def calculate_base_expected_goals(self, home_xg, away_xg, home_shots_allowed, away_shots_allowed):
        """3.1 Base Expected Goals"""
        home_lambda_base = home_xg * (away_shots_allowed / LEAGUE_AVG['shots_allowed']) * 0.5
        away_lambda_base = away_xg * (home_shots_allowed / LEAGUE_AVG['shots_allowed']) * 0.5
        return home_lambda_base, away_lambda_base
    
    def apply_home_advantage(self, home_lambda_base, away_lambda_base, home_ppg_diff, away_ppg_diff):
        """3.2 Home Advantage Adjustment"""
        home_boost = 1 + (home_ppg_diff * 0.3)
        away_penalty = 1 - (abs(away_ppg_diff) * 0.25)
        
        home_lambda = home_lambda_base * home_boost
        away_lambda = away_lambda_base * away_penalty
        
        return home_lambda, away_lambda, home_boost, away_penalty
    
    def apply_injury_adjustment(self, home_lambda, away_lambda, home_injury_level, away_injury_level):
        """3.3 Injury Adjustment"""
        home_defense_strength = 1 - (home_injury_level / 20)
        away_defense_strength = 1 - (away_injury_level / 20)
        
        home_lambda = home_lambda * away_defense_strength  # Attack vs weak defense
        away_lambda = away_lambda * home_defense_strength  # Attack vs weak defense
        
        return home_lambda, away_lambda, home_defense_strength, away_defense_strength
    
    def apply_form_adjustment(self, home_lambda, away_lambda, home_form_last_5, away_form_last_5):
        """3.4 Form Adjustment"""
        home_form_factor = 1 + ((home_form_last_5 - 9) * 0.02)
        away_form_factor = 1 + ((away_form_last_5 - 9) * 0.02)
        
        home_lambda = home_lambda * home_form_factor
        away_lambda = away_lambda * away_form_factor
        
        return home_lambda, away_lambda, home_form_factor, away_form_factor
    
    def apply_motivation_adjustment(self, home_lambda, away_lambda, home_motivation, away_motivation):
        """3.5 Motivation Adjustment"""
        home_motivation_factor = 1 + (home_motivation * 0.03)
        away_motivation_factor = 1 + (away_motivation * 0.03)
        
        home_lambda = home_lambda * home_motivation_factor
        away_lambda = away_lambda * away_motivation_factor
        
        return home_lambda, away_lambda, home_motivation_factor, away_motivation_factor
    
    def apply_style_matchup(self, home_lambda, away_lambda, 
                           home_set_piece_pct, away_set_piece_pct,
                           home_counter_pct, away_counter_pct,
                           home_open_play_pct, away_open_play_pct,
                           home_injury_level, away_injury_level,
                           home_shots_allowed, away_shots_allowed):
        """3.6 Style Matchup Adjustments"""
        adjustments = []
        
        # Set Piece Threat
        if away_set_piece_pct > LEAGUE_AVG['set_piece_pct'] and home_injury_level > 5:
            away_lambda += 0.15
            adjustments.append("Away team strong on set pieces against injured home defense")
        
        # Counter Attack Threat
        if away_counter_pct > 0.10 and home_open_play_pct > 0.55:
            away_lambda += 0.10
            adjustments.append("Away team effective on counter attacks")
        
        # Open Play Dominance
        if home_open_play_pct > 0.60 and away_shots_allowed > LEAGUE_AVG['shots_allowed']:
            home_lambda += 0.05
            adjustments.append("Home team dominant in open play against weak defense")
            
        return home_lambda, away_lambda, adjustments
    
    def apply_defense_form(self, home_lambda, away_lambda, 
                          home_goals_conceded_last_5, away_goals_conceded_last_5):
        """3.7 Recent Defense Form"""
        home_defense_form = home_goals_conceded_last_5 / 5
        away_defense_form = away_goals_conceded_last_5 / 5
        
        home_lambda = home_lambda * (1 + (away_defense_form - LEAGUE_AVG['goals_conceded']) * 0.1)
        away_lambda = away_lambda * (1 + (home_defense_form - LEAGUE_AVG['goals_conceded']) * 0.1)
        
        return home_lambda, away_lambda, home_defense_form, away_defense_form
    
    def simulate_match(self, home_lambda, away_lambda, iterations=10000):
        """4.1 Poisson Simulation"""
        home_goals = np.random.poisson(home_lambda, iterations)
        away_goals = np.random.poisson(away_lambda, iterations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        over_25 = np.sum(home_goals + away_goals > 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        
        return {
            'home_win': home_wins / iterations,
            'draw': draws / iterations,
            'away_win': away_wins / iterations,
            'over_25': over_25 / iterations,
            'btts_yes': btts_yes / iterations
        }, home_goals, away_goals
    
    def calculate_scoreline_probabilities(self, home_lambda, away_lambda, max_goals=6):
        """4.2 Scoreline Probabilities"""
        scorelines = {}
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = self.poisson_pmf(i, home_lambda) * self.poisson_pmf(j, away_lambda)
                scorelines[f"{i}-{j}"] = prob
        
        # Get top 5 most likely scorelines
        sorted_scores = sorted(scorelines.items(), key=lambda x: x[1], reverse=True)
        predicted_score = sorted_scores[0][0] if sorted_scores else "0-0"
        
        return dict(sorted_scores[:10]), predicted_score
    
    def calculate_confidence(self, home_lambda, away_lambda, 
                           home_injury_level, away_injury_level,
                           home_ppg_diff, form_diff):
        """5. Confidence Scoring"""
        confidence = 0.5  # Base
        
        # Goal expectation difference
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.0:
            confidence += 0.2
        elif goal_diff > 0.5:
            confidence += 0.1
        
        # Injury mismatch
        injury_diff = abs(home_injury_level - away_injury_level)
        if injury_diff > 4:
            confidence += 0.15
        
        # Form difference
        if abs(form_diff) > 4:
            confidence += 0.1
        
        # Home advantage
        if home_ppg_diff > 0.5:
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    def calculate_expected_value(self, probability, market_odds):
        """6. Value Betting Analysis - Expected Value"""
        if probability == 0:
            return -1
        fair_odds = 1 / probability
        expected_value = (market_odds / fair_odds) - 1
        return expected_value
    
    def get_betting_recommendations(self, probabilities, market_odds, confidence):
        """6. Betting Recommendations"""
        recommendations = []
        
        # Home Win
        ev_home = self.calculate_expected_value(probabilities['home_win'], market_odds['home_win'])
        if ev_home > 0.10 and confidence > 0.65:
            stake = 'medium' if ev_home < 0.25 else 'high'
            recommendations.append({
                'market': 'Home Win',
                'type': 'home_win',
                'odds': market_odds['home_win'],
                'ev': ev_home,
                'stake': stake,
                'probability': probabilities['home_win'],
                'reason': 'Significant value with high confidence'
            })
        
        # Over 2.5
        ev_over = self.calculate_expected_value(probabilities['over_25'], market_odds['over_25'])
        if ev_over > 0.10 and confidence > 0.60:
            stake = 'medium' if ev_over < 0.30 else 'high'
            recommendations.append({
                'market': 'Over 2.5 Goals',
                'type': 'over_25',
                'odds': market_odds['over_25'],
                'ev': ev_over,
                'stake': stake,
                'probability': probabilities['over_25'],
                'reason': 'High probability of goals based on team analysis'
            })
        
        # BTTS Yes
        ev_btts = self.calculate_expected_value(probabilities['btts_yes'], market_odds['btts_yes'])
        if ev_btts > 0.10 and confidence > 0.60:
            stake = 'medium' if ev_btts < 0.25 else 'high'
            recommendations.append({
                'market': 'Both Teams to Score',
                'type': 'btts_yes',
                'odds': market_odds['btts_yes'],
                'ev': ev_btts,
                'stake': stake,
                'probability': probabilities['btts_yes'],
                'reason': 'Defensive vulnerabilities suggest both teams will score'
            })
        
        # Sort by EV
        return sorted(recommendations, key=lambda x: x['ev'], reverse=True)
    
    def run_full_prediction(self, inputs):
        """Run complete prediction pipeline"""
        self.reset_calculations()
        
        # Calculate injury levels
        home_injury_level = self.calculate_injury_level(inputs['home_defenders_out'])
        away_injury_level = self.calculate_injury_level(inputs['away_defenders_out'])
        
        # Calculate goal percentages
        home_open_pct, home_set_piece_pct, home_counter_pct = self.calculate_goal_percentages(
            inputs['home_goals_total'], inputs['home_open_play_goals'],
            inputs['home_set_piece_goals'], inputs['home_counter_attack_goals']
        )
        
        away_open_pct, away_set_piece_pct, away_counter_pct = self.calculate_goal_percentages(
            inputs['away_goals_total'], inputs['away_open_play_goals'],
            inputs['away_set_piece_goals'], inputs['away_counter_attack_goals']
        )
        
        # Step 1: Base Expected Goals
        home_lambda, away_lambda = self.calculate_base_expected_goals(
            inputs['home_xg'], inputs['away_xg'],
            inputs['home_shots_allowed'], inputs['away_shots_allowed']
        )
        
        # Collect key factors
        key_factors = []
        
        # Step 2: Home Advantage
        home_lambda, away_lambda, home_boost, away_penalty = self.apply_home_advantage(
            home_lambda, away_lambda,
            inputs['home_ppg_diff'], inputs['away_ppg_diff']
        )
        
        if home_boost > 1.1:
            key_factors.append(f"Home advantage: +{inputs['home_ppg_diff']:.2f} PPG")
        
        # Step 3: Injury Adjustment
        home_lambda, away_lambda, home_defense_str, away_defense_str = self.apply_injury_adjustment(
            home_lambda, away_lambda,
            home_injury_level, away_injury_level
        )
        
        if home_injury_level > 5:
            key_factors.append(f"Home injury crisis: {home_injury_level}/10 severity")
        if away_injury_level > 5:
            key_factors.append(f"Away injury crisis: {away_injury_level}/10 severity")
        
        # Step 4: Form Adjustment
        home_lambda, away_lambda, home_form_factor, away_form_factor = self.apply_form_adjustment(
            home_lambda, away_lambda,
            inputs['home_form_last_5'], inputs['away_form_last_5']
        )
        
        form_diff = inputs['home_form_last_5'] - inputs['away_form_last_5']
        if abs(form_diff) > 4:
            direction = "better" if form_diff > 0 else "worse"
            key_factors.append(f"Form difference: Home {direction} by {abs(form_diff)} points")
        
        # Step 5: Motivation Adjustment
        home_lambda, away_lambda, home_motivation_factor, away_motivation_factor = self.apply_motivation_adjustment(
            home_lambda, away_lambda,
            inputs['home_motivation'], inputs['away_motivation']
        )
        
        # Step 6: Style Matchup
        style_adjustments = []
        home_lambda, away_lambda, style_adj = self.apply_style_matchup(
            home_lambda, away_lambda,
            home_set_piece_pct, away_set_piece_pct,
            home_counter_pct, away_counter_pct,
            home_open_pct, away_open_pct,
            home_injury_level, away_injury_level,
            inputs['home_shots_allowed'], inputs['away_shots_allowed']
        )
        key_factors.extend(style_adj)
        
        # Step 7: Defense Form
        home_lambda, away_lambda, home_def_form, away_def_form = self.apply_defense_form(
            home_lambda, away_lambda,
            inputs['home_goals_conceded_last_5'], inputs['away_goals_conceded_last_5']
        )
        
        if home_def_form > 2.0:
            key_factors.append(f"Poor home defense: conceding {home_def_form:.1f} goals per game")
        if away_def_form > 2.0:
            key_factors.append(f"Poor away defense: conceding {away_def_form:.1f} goals per game")
        
        # Store final lambdas
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # Step 8: Simulation
        probabilities, home_goals_sim, away_goals_sim = self.simulate_match(home_lambda, away_lambda)
        
        # Step 9: Scoreline probabilities
        scoreline_probs, predicted_score = self.calculate_scoreline_probabilities(home_lambda, away_lambda)
        
        # Step 10: Confidence
        confidence = self.calculate_confidence(
            home_lambda, away_lambda,
            home_injury_level, away_injury_level,
            inputs['home_ppg_diff'], form_diff
        )
        
        # Step 11: Betting Recommendations
        market_odds = {
            'home_win': inputs['home_win_odds'],
            'over_25': inputs['over_25_odds'],
            'btts_yes': inputs['btts_yes_odds']
        }
        
        betting_recommendations = self.get_betting_recommendations(probabilities, market_odds, confidence)
        
        # Fair odds calculation
        fair_odds = {
            'home_win': 1 / probabilities['home_win'] if probabilities['home_win'] > 0 else 0,
            'over_25': 1 / probabilities['over_25'] if probabilities['over_25'] > 0 else 0,
            'btts_yes': 1 / probabilities['btts_yes'] if probabilities['btts_yes'] > 0 else 0
        }
        
        # Expected values
        expected_values = {
            'home_win': self.calculate_expected_value(probabilities['home_win'], market_odds['home_win']),
            'over_25': self.calculate_expected_value(probabilities['over_25'], market_odds['over_25']),
            'btts_yes': self.calculate_expected_value(probabilities['btts_yes'], market_odds['btts_yes'])
        }
        
        result = {
            'match': f"{inputs['home_name']} vs {inputs['away_name']}",
            'predicted_score': predicted_score,
            'expected_goals': {
                'home': round(home_lambda, 2),
                'away': round(away_lambda, 2)
            },
            'probabilities': {k: round(v, 4) for k, v in probabilities.items()},
            'confidence': round(confidence, 3),
            'key_factors': key_factors,
            'betting_recommendations': betting_recommendations,
            'scoreline_probabilities': scoreline_probs,
            'fair_odds': {k: round(v, 2) for k, v in fair_odds.items()},
            'expected_values': {k: round(v, 4) for k, v in expected_values.items()},
            'simulated_goals': (home_goals_sim, away_goals_sim)
        }
        
        return result

def create_input_interface():
    """Create the input interface with tabs for different sections"""
    
    st.sidebar.markdown("## ⚙️ Match Configuration")
    
    # Use tabs for organization
    tab1, tab2, tab3, tab4 = st.sidebar.tabs(["🏠 Home", "🏃 Away", "📊 League", "💰 Market"])
    
    with tab1:
        st.markdown("### Home Team Details")
        home_name = st.text_input("Team Name", "Barcelona", key="home_name")
        
        col1, col2 = st.columns(2)
        with col1:
            home_xg = st.number_input("xG (per game)", min_value=0.0, max_value=5.0, value=1.43, step=0.01, key="home_xg")
            home_shots_allowed = st.number_input("Shots Allowed", min_value=0.0, max_value=30.0, value=7.3, step=0.1, key="home_shots_allowed")
            home_ppg_diff = st.number_input("PPG Diff", min_value=-2.0, max_value=2.0, value=0.28, step=0.01, key="home_ppg_diff", 
                                          help="Difference from league average PPG")
        with col2:
            home_form_last_5 = st.slider("Form (Last 5)", min_value=0, max_value=15, value=9, key="home_form")
            home_defenders_out = st.slider("Defenders Out", min_value=0, max_value=10, value=4, key="home_def_out")
            home_motivation = st.slider("Motivation", min_value=1, max_value=10, value=2, key="home_motivation")
        
        st.markdown("---")
        st.markdown("#### Recent Performance")
        col1, col2, col3 = st.columns(3)
        with col1:
            home_goals_scored_last_5 = st.number_input("Goals Scored (L5)", min_value=0, max_value=30, value=8, key="home_goals_scored")
        with col2:
            home_goals_conceded_last_5 = st.number_input("Goals Conceded (L5)", min_value=0, max_value=30, value=6, key="home_goals_conceded")
        with col3:
            home_goals_total = st.number_input("Total Goals", min_value=0, max_value=100, value=40, key="home_goals_total")
        
        st.markdown("#### Goal Types")
        col1, col2, col3 = st.columns(3)
        with col1:
            home_open_play_goals = st.number_input("Open Play Goals", min_value=0, max_value=100, value=25, key="home_open")
        with col2:
            home_set_piece_goals = st.number_input("Set Piece Goals", min_value=0, max_value=100, value=10, key="home_set")
        with col3:
            home_counter_attack_goals = st.number_input("Counter Attack Goals", min_value=0, max_value=100, value=5, key="home_counter")
    
    with tab2:
        st.markdown("### Away Team Details")
        away_name = st.text_input("Team Name", "Real Madrid", key="away_name")
        
        col1, col2 = st.columns(2)
        with col1:
            away_xg = st.number_input("xG (per game)", min_value=0.0, max_value=5.0, value=0.94, step=0.01, key="away_xg")
            away_shots_allowed = st.number_input("Shots Allowed", min_value=0.0, max_value=30.0, value=12.9, step=0.1, key="away_shots_allowed")
            away_ppg_diff = st.number_input("PPG Diff", min_value=-2.0, max_value=2.0, value=0.07, step=0.01, key="away_ppg_diff")
        with col2:
            away_form_last_5 = st.slider("Form (Last 5)", min_value=0, max_value=15, value=10, key="away_form")
            away_defenders_out = st.slider("Defenders Out", min_value=0, max_value=10, value=1, key="away_def_out")
            away_motivation = st.slider("Motivation", min_value=1, max_value=10, value=4, key="away_motivation")
        
        st.markdown("---")
        st.markdown("#### Recent Performance")
        col1, col2, col3 = st.columns(3)
        with col1:
            away_goals_scored_last_5 = st.number_input("Goals Scored (L5)", min_value=0, max_value=30, value=10, key="away_goals_scored")
        with col2:
            away_goals_conceded_last_5 = st.number_input("Goals Conceded (L5)", min_value=0, max_value=30, value=5, key="away_goals_conceded")
        with col3:
            away_goals_total = st.number_input("Total Goals", min_value=0, max_value=100, value=35, key="away_goals_total")
        
        st.markdown("#### Goal Types")
        col1, col2, col3 = st.columns(3)
        with col1:
            away_open_play_goals = st.number_input("Open Play Goals", min_value=0, max_value=100, value=20, key="away_open")
        with col2:
            away_set_piece_goals = st.number_input("Set Piece Goals", min_value=0, max_value=100, value=8, key="away_set")
        with col3:
            away_counter_attack_goals = st.number_input("Counter Attack Goals", min_value=0, max_value=100, value=7, key="away_counter")
    
    with tab3:
        st.markdown("### League Settings")
        st.info(f"Current League Averages:\n- Shots Allowed: {LEAGUE_AVG['shots_allowed']}\n- PPG: {LEAGUE_AVG['ppg']}\n- Set Piece %: {LEAGUE_AVG['set_piece_pct']*100}%")
        
        # Allow league averages to be adjusted
        st.markdown("#### Adjust League Averages")
        league_shots_allowed = st.slider("League Avg Shots Allowed", min_value=8.0, max_value=16.0, value=LEAGUE_AVG['shots_allowed'], step=0.5)
        league_ppg = st.slider("League Avg PPG", min_value=1.0, max_value=2.0, value=LEAGUE_AVG['ppg'], step=0.1)
        league_set_piece = st.slider("League Avg Set Piece %", min_value=0.0, max_value=0.5, value=LEAGUE_AVG['set_piece_pct'], step=0.01)
        league_goals_conceded = st.slider("League Avg Goals Conceded", min_value=0.5, max_value=2.0, value=LEAGUE_AVG['goals_conceded'], step=0.1)
        
        # Update league averages
        LEAGUE_AVG['shots_allowed'] = league_shots_allowed
        LEAGUE_AVG['ppg'] = league_ppg
        LEAGUE_AVG['set_piece_pct'] = league_set_piece
        LEAGUE_AVG['goals_conceded'] = league_goals_conceded
        
        st.markdown("---")
        st.markdown("#### Simulation Settings")
        iterations = st.slider("Simulation Iterations", min_value=1000, max_value=50000, value=10000, step=1000)
    
    with tab4:
        st.markdown("### Market Odds")
        st.markdown("Enter current market odds for value betting analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            home_win_odds = st.number_input("Home Win Odds", min_value=1.1, max_value=20.0, value=1.79, step=0.01, key="home_odds")
            st.caption("Market: 1.79")
        with col2:
            over_25_odds = st.number_input("Over 2.5 Goals", min_value=1.1, max_value=20.0, value=2.30, step=0.01, key="over_odds")
            st.caption("Market: 2.30")
        with col3:
            btts_yes_odds = st.number_input("BTTS Yes", min_value=1.1, max_value=20.0, value=2.10, step=0.01, key="btts_odds")
            st.caption("Market: 2.10")
    
    # Compile all inputs
    inputs = {
        'home_name': home_name,
        'away_name': away_name,
        'home_xg': home_xg,
        'away_xg': away_xg,
        'home_shots_allowed': home_shots_allowed,
        'away_shots_allowed': away_shots_allowed,
        'home_ppg_diff': home_ppg_diff,
        'away_ppg_diff': away_ppg_diff,
        'home_defenders_out': home_defenders_out,
        'away_defenders_out': away_defenders_out,
        'home_form_last_5': home_form_last_5,
        'away_form_last_5': away_form_last_5,
        'home_goals_scored_last_5': home_goals_scored_last_5,
        'away_goals_scored_last_5': away_goals_scored_last_5,
        'home_goals_conceded_last_5': home_goals_conceded_last_5,
        'away_goals_conceded_last_5': away_goals_conceded_last_5,
        'home_motivation': home_motivation,
        'away_motivation': away_motivation,
        'home_goals_total': home_goals_total,
        'away_goals_total': away_goals_total,
        'home_open_play_goals': home_open_play_goals,
        'away_open_play_goals': away_open_play_goals,
        'home_set_piece_goals': home_set_piece_goals,
        'away_set_piece_goals': away_set_piece_goals,
        'home_counter_attack_goals': home_counter_attack_goals,
        'away_counter_attack_goals': away_counter_attack_goals,
        'home_win_odds': home_win_odds,
        'over_25_odds': over_25_odds,
        'btts_yes_odds': btts_yes_odds,
        'simulation_iterations': iterations
    }
    
    return inputs

def display_prediction_summary(result):
    """Display main prediction summary"""
    st.markdown(f"# 🏆 {result['match']}")
    
    # Main prediction card
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏠 Home Team</h3>
            <h2>Expected Goals: {result['expected_goals']['home']:.2f}</h2>
            <p>Win Probability: <span class='value-positive'>{result['probabilities']['home_win']*100:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='prediction-card' style='text-align: center;'>
            <h4>🎯 Predicted Score</h4>
            <h1 style='font-size: 3.5rem; margin: 10px 0;'>{result['predicted_score']}</h1>
            <small>Most likely outcome</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏃 Away Team</h3>
            <h2>Expected Goals: {result['expected_goals']['away']:.2f}</h2>
            <p>Win Probability: <span class='value-positive'>{result['probabilities']['away_win']*100:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)

def display_probability_visualizations(result):
    """Display probability charts and visualizations"""
    st.markdown("<h2 class='section-header'>📊 Probability Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Match outcome probabilities
        fig = go.Figure(data=[
            go.Bar(
                x=['Home Win', 'Draw', 'Away Win'],
                y=[result['probabilities']['home_win'], 
                   result['probabilities']['draw'], 
                   result['probabilities']['away_win']],
                marker_color=['#4ECDC4', '#FFD166', '#FF6B6B'],
                text=[f"{p*100:.1f}%" for p in [result['probabilities']['home_win'], 
                                               result['probabilities']['draw'], 
                                               result['probabilities']['away_win']]],
                textposition='auto',
                textfont=dict(size=14, color='white')
            )
        ])
        
        fig.update_layout(
            title="Match Outcome Probabilities",
            yaxis_title="Probability",
            yaxis=dict(range=[0, 1]),
            height=400,
            template="plotly_white",
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scoreline probabilities
        top_scores = list(result['scoreline_probabilities'].items())[:5]
        scores = [score for score, _ in top_scores]
        probs = [prob * 100 for _, prob in top_scores]
        
        fig = go.Figure(data=[
            go.Bar(
                x=scores,
                y=probs,
                marker_color='#667eea',
                text=[f"{p:.1f}%" for p in probs],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top 5 Most Likely Scorelines",
            yaxis_title="Probability (%)",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional probabilities
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h4>⚽ Over 2.5 Goals</h4>
            <h2>{result['probabilities']['over_25']*100:.1f}%</h2>
            <small>Probability of 3+ goals</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h4>🎯 Both Teams to Score</h4>
            <h2>{result['probabilities']['btts_yes']*100:.1f}%</h2>
            <small>Probability both teams score</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Confidence display
        confidence = result['confidence']
        if confidence > 0.7:
            conf_class = "confidence-high"
        elif confidence > 0.6:
            conf_class = "confidence-medium"
        else:
            conf_class = "confidence-low"
        
        st.markdown(f"""
        <div class='{conf_class}'>
            <h4>🎯 Prediction Confidence</h4>
            <h2>{confidence*100:.1f}%</h2>
            <small>Model confidence in predictions</small>
        </div>
        """, unsafe_allow_html=True)

def display_betting_recommendations(result):
    """Display betting recommendations"""
    st.markdown("<h2 class='section-header'>💰 Betting Recommendations</h2>", unsafe_allow_html=True)
    
    if result['betting_recommendations']:
        for rec in result['betting_recommendations']:
            ev = rec['ev']
            ev_class = "value-positive" if ev > 0 else "value-negative"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{rec['market']}**")
                st.caption(f"Probability: {rec['probability']*100:.1f}% | Fair Odds: {1/rec['probability']:.2f}")
            
            with col2:
                st.metric("Market Odds", f"{rec['odds']:.2f}")
            
            with col3:
                st.metric("Expected Value", f"{ev*100:.1f}%", delta=f"{ev*100:.1f}%")
            
            with col4:
                stake_color = "green" if rec['stake'] == 'high' else "orange" if rec['stake'] == 'medium' else "red"
                st.markdown(f"**Stake:** <span style='color:{stake_color}; font-weight:bold;'>{rec['stake'].upper()}</span>", unsafe_allow_html=True)
            
            st.info(f"**Reason:** {rec['reason']}")
            st.markdown("---")
    else:
        st.warning("No value bets identified at current market odds (need >10% edge and >60% confidence)")

def display_expected_value_analysis(result):
    """Display expected value analysis"""
    st.markdown("<h2 class='section-header'>📈 Expected Value Analysis</h2>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    markets = [
        ("Home Win", result['expected_values']['home_win'], 
         result['fair_odds']['home_win'], result['probabilities']['home_win']),
        ("Over 2.5 Goals", result['expected_values']['over_25'],
         result['fair_odds']['over_25'], result['probabilities']['over_25']),
        ("BTTS Yes", result['expected_values']['btts_yes'],
         result['fair_odds']['btts_yes'], result['probabilities']['btts_yes'])
    ]
    
    for idx, (market, ev, fair_odds, prob) in enumerate(markets):
        with cols[idx]:
            if ev > 0.1:
                badge = "✅ RECOMMENDED"
                color = "green"
            elif ev > 0:
                badge = "⚠️ MARGINAL"
                color = "orange"
            else:
                badge = "❌ AVOID"
                color = "red"
            
            ev_display = f"{ev*100:.1f}%"
            ev_color = "green" if ev > 0.1 else "orange" if ev > 0 else "red"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4>{market} {badge}</h4>
                <h3 style='color: {ev_color}'>{ev_display}</h3>
                <small>
                    Fair Odds: {fair_odds:.2f}<br>
                    Probability: {prob*100:.1f}%<br>
                    Required Confidence: {result['confidence']*100:.1f}%
                </small>
            </div>
            """, unsafe_allow_html=True)

def display_key_factors(result):
    """Display key influencing factors"""
    st.markdown("<h2 class='section-header'>🔑 Key Influencing Factors</h2>", unsafe_allow_html=True)
    
    if result['key_factors']:
        cols = st.columns(2)
        mid_point = len(result['key_factors']) // 2 + len(result['key_factors']) % 2
        
        with cols[0]:
            for factor in result['key_factors'][:mid_point]:
                st.markdown(f"<span class='factor-badge'>{factor}</span>", unsafe_allow_html=True)
        
        with cols[1]:
            for factor in result['key_factors'][mid_point:]:
                st.markdown(f"<span class='factor-badge'>{factor}</span>", unsafe_allow_html=True)
    else:
        st.info("No strongly influencing factors identified for this match")

def display_simulation_results(result):
    """Display simulation results"""
    st.markdown("<h2 class='section-header'>🔮 Simulation Results</h2>", unsafe_allow_html=True)
    
    if 'simulated_goals' in result:
        home_goals_sim, away_goals_sim = result['simulated_goals']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Goal distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=home_goals_sim, 
                name='Home Goals', 
                opacity=0.7, 
                marker_color='#4ECDC4',
                nbinsx=10
            ))
            fig.add_trace(go.Histogram(
                x=away_goals_sim, 
                name='Away Goals', 
                opacity=0.7, 
                marker_color='#FF6B6B',
                nbinsx=10
            ))
            
            fig.update_layout(
                title="Goal Distribution",
                xaxis_title="Goals",
                yaxis_title="Frequency",
                barmode='overlay',
                height=350,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Match statistics
            avg_home = np.mean(home_goals_sim)
            avg_away = np.mean(away_goals_sim)
            total_goals = home_goals_sim + away_goals_sim
            
            metrics = [
                ("Avg Home Goals", f"{avg_home:.2f}"),
                ("Avg Away Goals", f"{avg_away:.2f}"),
                ("Avg Total Goals", f"{np.mean(total_goals):.2f}"),
                ("Clean Sheet (Home)", f"{np.sum(away_goals_sim == 0) / len(away_goals_sim):.1%}"),
                ("Clean Sheet (Away)", f"{np.sum(home_goals_sim == 0) / len(home_goals_sim):.1%}"),
                ("Exact 2.5+ Goals", f"{np.sum(total_goals > 2.5) / len(total_goals):.1%}")
            ]
            
            for label, value in metrics:
                st.metric(label, value)
        
        with col3:
            # Win probabilities from simulation
            home_wins = np.sum(home_goals_sim > away_goals_sim) / len(home_goals_sim)
            draws = np.sum(home_goals_sim == away_goals_sim) / len(home_goals_sim)
            away_wins = np.sum(home_goals_sim < away_goals_sim) / len(home_goals_sim)
            
            fig = go.Figure(data=[go.Pie(
                labels=['Home Win', 'Draw', 'Away Win'],
                values=[home_wins, draws, away_wins],
                marker_colors=['#4ECDC4', '#FFD166', '#FF6B6B'],
                hole=0.4,
                textinfo='percent+label'
            )])
            
            fig.update_layout(
                title="Win/Draw/Loss Distribution",
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_export_options(result):
    """Display export options"""
    st.markdown("<h2 class='section-header'>📤 Export Results</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        json_data = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV export
        summary_data = {
            'Metric': ['Predicted Score', 'Home xG', 'Away xG', 'Home Win %', 'Draw %', 'Away Win %', 
                      'Over 2.5 %', 'BTTS %', 'Confidence'],
            'Value': [
                result['predicted_score'],
                f"{result['expected_goals']['home']:.2f}",
                f"{result['expected_goals']['away']:.2f}",
                f"{result['probabilities']['home_win']*100:.1f}%",
                f"{result['probabilities']['draw']*100:.1f}%",
                f"{result['probabilities']['away_win']*100:.1f}%",
                f"{result['probabilities']['over_25']*100:.1f}%",
                f"{result['probabilities']['btts_yes']*100:.1f}%",
                f"{result['confidence']*100:.1f}%"
            ]
        }
        
        df = pd.DataFrame(summary_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download CSV",
            data=csv,
            file_name=f"prediction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Report generation
        if st.button("📄 Generate Report", use_container_width=True):
            st.success("Report generated successfully!")
            
            # Display report preview
            with st.expander("📋 Report Preview"):
                st.markdown(f"""
                ### 📊 Prediction Report
                **Match:** {result['match']}
                
                **Predicted Score:** {result['predicted_score']}
                
                **Expected Goals:**
                - Home: {result['expected_goals']['home']:.2f}
                - Away: {result['expected_goals']['away']:.2f}
                
                **Probabilities:**
                - Home Win: {result['probabilities']['home_win']*100:.1f}%
                - Draw: {result['probabilities']['draw']*100:.1f}%
                - Away Win: {result['probabilities']['away_win']*100:.1f}%
                - Over 2.5 Goals: {result['probabilities']['over_25']*100:.1f}%
                - Both Teams to Score: {result['probabilities']['btts_yes']*100:.1f}%
                
                **Confidence:** {result['confidence']*100:.1f}%
                
                **Key Factors:**
                {chr(10).join(['- ' + factor for factor in result['key_factors']])}
                
                **Betting Recommendations:**
                {chr(10).join(['- ' + rec['market'] + f" (EV: {rec['ev']*100:.1f}%)" for rec in result['betting_recommendations']]) if result['betting_recommendations'] else 'No value bets identified'}
                """)

def main():
    """Main application"""
    
    # Header
    st.markdown("<h1 class='main-header'>⚽ Complete Football Prediction Engine</h1>", unsafe_allow_html=True)
    st.markdown("### Advanced match prediction using 15+ data points and Poisson simulation")
    
    # Initialize session state
    if 'engine' not in st.session_state:
        st.session_state.engine = CompletePredictionEngine()
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    # Get inputs from sidebar
    inputs = create_input_interface()
    
    # Calculate button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Run Complete Prediction", type="primary", use_container_width=True):
        with st.spinner("Running complete prediction pipeline..."):
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Collecting inputs...",
                "Calculating injury levels...",
                "Applying home advantage...",
                "Adjusting for form and motivation...",
                "Analyzing style matchups...",
                "Running Poisson simulation...",
                "Calculating probabilities...",
                "Generating recommendations..."
            ]
            
            for i, step in enumerate(steps):
                progress_bar.progress((i + 1) / len(steps))
                status_text.text(f"Step {i+1}/{len(steps)}: {step}")
                time.sleep(0.3)
            
            # Run prediction
            result = st.session_state.engine.run_full_prediction(inputs)
            st.session_state.last_result = result
            
            progress_bar.progress(100)
            status_text.text("✅ Prediction complete!")
            time.sleep(0.5)
            st.success("Prediction engine complete! Results displayed below.")
    
    # Display results if available
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        # Display all sections
        display_prediction_summary(result)
        st.markdown("---")
        display_probability_visualizations(result)
        st.markdown("---")
        display_expected_value_analysis(result)
        st.markdown("---")
        
        # Tabs for detailed analysis
        tab1, tab2, tab3 = st.tabs(["🎯 Betting Recommendations", "🔑 Key Factors", "🔮 Simulation Details"])
        
        with tab1:
            display_betting_recommendations(result)
        
        with tab2:
            display_key_factors(result)
        
        with tab3:
            display_simulation_results(result)
        
        st.markdown("---")
        display_export_options(result)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <small>
            ⚠️ <strong>Disclaimer:</strong> This is a simulation tool for educational purposes only. 
            Sports betting involves risk. Always gamble responsibly.<br><br>
            
            <strong>Complete Football Prediction Engine v2.0</strong><br>
            15+ Data Points | Poisson Distribution | Value Betting Analysis<br>
            Built with Streamlit • All formulas implemented as specified
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
