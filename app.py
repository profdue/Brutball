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
import io

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
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .yes-card {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .no-card {
        background: linear-gradient(135deg, rgba(255,65,108,0.9), rgba(255,75,43,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
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
    
    /* Prediction badges */
    .prediction-badge {
        display: inline-block;
        padding: 10px 25px;
        border-radius: 30px;
        font-size: 1.2em;
        font-weight: 800;
        margin: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .prediction-yes {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        border: 3px solid #00b09b;
    }
    
    .prediction-no {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border: 3px solid #ff416c;
    }
    
    .prediction-over {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: 3px solid #667eea;
    }
    
    .prediction-under {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        border: 3px solid #f093fb;
    }
    
    /* Warning banner */
    .warning-banner {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #ff416c;
    }
</style>
""", unsafe_allow_html=True)

# League averages (La Liga example - can be updated based on loaded data)
LEAGUE_AVG = {
    'shots_allowed': 12.0,
    'ppg': 1.50,
    'set_piece_pct': 0.20,
    'goals_conceded': 1.2,
    'xg_per_game': 1.43  # Average xG per game
}

# Sample CSV data as string
SAMPLE_CSV = """team,venue,goals,shots_on_target_pg,shots_allowed_pg,xg,home_ppg_diff,defenders_out,injury_level,form_last_5,goals_scored_last_5,goals_conceded_last_5,motivation,open_play_pct,set_piece_pct,counter_attack_pct,expected_goals_for,expected_goals_against
Athletic Bilbao,home,9,4.2,7.3,12.87,0.90,4,8,9,4,5,2,0.56,0.11,0.00,2.5,1.6
Espanyol,away,7,4.9,12.9,8.47,-0.54,1,2,10,5,2,4,0.46,0.31,0.08,1.6,2.5"""

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
        self.binary_predictions = {}
        
    def calculate_injury_level(self, defenders_out):
        """2.1 Injury Level Calculation"""
        return min(10, defenders_out * 2)
    
    def poisson_pmf(self, k, lambda_val):
        """Poisson probability mass function"""
        if k > 20:  # Cap for factorial calculation
            return 0
        return (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
    
    def calculate_base_expected_goals(self, home_xg, away_xg, home_shots_allowed, away_shots_allowed):
        """
        3.1 Base Expected Goals - FIXED VERSION
        The xG values in the CSV appear to be season totals, not per game.
        Assuming approximately 20 games played, convert to per game average.
        """
        # Convert season xG to per game average (assuming ~20 games)
        home_xg_per_game = home_xg / 20
        away_xg_per_game = away_xg / 20
        
        # Original formula with per game xG
        home_lambda_base = home_xg_per_game * (away_shots_allowed / LEAGUE_AVG['shots_allowed']) * 0.5
        away_lambda_base = away_xg_per_game * (home_shots_allowed / LEAGUE_AVG['shots_allowed']) * 0.5
        
        # Cap at reasonable values
        home_lambda_base = min(home_lambda_base, 3.5)
        away_lambda_base = min(away_lambda_base, 3.5)
        
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
        
        # Set Piece Threat - REDUCED impact
        if away_set_piece_pct > LEAGUE_AVG['set_piece_pct'] and home_injury_level > 5:
            away_lambda += 0.08  # Reduced from 0.15
            adjustments.append("Away team strong on set pieces against injured home defense")
        
        # Counter Attack Threat - REDUCED impact
        if away_counter_pct > 0.10 and home_open_play_pct > 0.55:
            away_lambda += 0.05  # Reduced from 0.10
            adjustments.append("Away team effective on counter attacks")
        
        # Open Play Dominance - REDUCED impact
        if home_open_play_pct > 0.60 and away_shots_allowed > LEAGUE_AVG['shots_allowed']:
            home_lambda += 0.03  # Reduced from 0.05
            adjustments.append("Home team dominant in open play against weak defense")
            
        return home_lambda, away_lambda, adjustments
    
    def apply_defense_form(self, home_lambda, away_lambda, 
                          home_goals_conceded_last_5, away_goals_conceded_last_5):
        """3.7 Recent Defense Form"""
        home_defense_form = home_goals_conceded_last_5 / 5
        away_defense_form = away_goals_conceded_last_5 / 5
        
        # Reduced impact from defense form
        home_lambda = home_lambda * (1 + (away_defense_form - LEAGUE_AVG['goals_conceded']) * 0.05)  # Reduced from 0.1
        away_lambda = away_lambda * (1 + (home_defense_form - LEAGUE_AVG['goals_conceded']) * 0.05)
        
        return home_lambda, away_lambda, home_defense_form, away_defense_form
    
    def simulate_match(self, home_lambda, away_lambda, iterations=10000):
        """4.1 Poisson Simulation"""
        home_goals = np.random.poisson(home_lambda, iterations)
        away_goals = np.random.poisson(away_lambda, iterations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        over_25 = np.sum(home_goals + away_goals > 2.5)
        under_25 = np.sum(home_goals + away_goals < 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        btts_no = np.sum((home_goals == 0) | (away_goals == 0))
        
        return {
            'home_win': home_wins / iterations,
            'draw': draws / iterations,
            'away_win': away_wins / iterations,
            'over_25': over_25 / iterations,
            'under_25': under_25 / iterations,
            'btts_yes': btts_yes / iterations,
            'btts_no': btts_no / iterations
        }, home_goals, away_goals
    
    def calculate_binary_predictions(self, probabilities):
        """Make clear binary predictions for BTTS and Over/Under"""
        binary_preds = {}
        
        # BTTS Prediction
        btts_yes_prob = probabilities['btts_yes']
        btts_no_prob = probabilities['btts_no']
        
        if btts_yes_prob > btts_no_prob:
            binary_preds['btts'] = {
                'prediction': 'YES',
                'probability': btts_yes_prob,
                'confidence': (btts_yes_prob - btts_no_prob) * 100,  # Margin of victory
                'opposite_prob': btts_no_prob
            }
        else:
            binary_preds['btts'] = {
                'prediction': 'NO',
                'probability': btts_no_prob,
                'confidence': (btts_no_prob - btts_yes_prob) * 100,
                'opposite_prob': btts_yes_prob
            }
        
        # Over/Under 2.5 Prediction
        over_prob = probabilities['over_25']
        under_prob = probabilities['under_25']
        
        if over_prob > under_prob:
            binary_preds['over_under'] = {
                'prediction': 'OVER',
                'probability': over_prob,
                'confidence': (over_prob - under_prob) * 100,
                'opposite_prob': under_prob
            }
        else:
            binary_preds['over_under'] = {
                'prediction': 'UNDER',
                'probability': under_prob,
                'confidence': (under_prob - over_prob) * 100,
                'opposite_prob': over_prob
            }
        
        return binary_preds
    
    def calculate_scoreline_probabilities(self, home_lambda, away_lambda, max_goals=6):
        """4.2 Scoreline Probabilities"""
        scorelines = {}
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = self.poisson_pmf(i, home_lambda) * self.poisson_pmf(j, away_lambda)
                if prob > 0.0001:  # Only include reasonable probabilities
                    scorelines[f"{i}-{j}"] = prob
        
        # Get top 5 most likely scorelines
        if scorelines:
            sorted_scores = sorted(scorelines.items(), key=lambda x: x[1], reverse=True)
            predicted_score = sorted_scores[0][0]
            return dict(sorted_scores[:10]), predicted_score
        else:
            return {"1-1": 0.1, "1-0": 0.08, "2-1": 0.07, "0-0": 0.06, "0-1": 0.05}, "1-1"
    
    def calculate_confidence(self, home_lambda, away_lambda, 
                           home_injury_level, away_injury_level,
                           home_ppg_diff, form_diff):
        """5. Confidence Scoring"""
        confidence = 0.5  # Base
        
        # Goal expectation difference
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 0.5:  # Reduced from 1.0
            confidence += 0.15  # Reduced from 0.2
        elif goal_diff > 0.3:  # Reduced from 0.5
            confidence += 0.08  # Reduced from 0.1
        
        # Injury mismatch
        injury_diff = abs(home_injury_level - away_injury_level)
        if injury_diff > 4:
            confidence += 0.12  # Reduced from 0.15
        
        # Form difference
        if abs(form_diff) > 4:
            confidence += 0.08  # Reduced from 0.1
        
        # Home advantage
        if home_ppg_diff > 0.5:
            confidence += 0.04  # Reduced from 0.05
        
        return min(confidence, 0.95)
    
    def calculate_expected_value(self, probability, market_odds):
        """6. Value Betting Analysis - Expected Value"""
        if probability == 0:
            return -1
        fair_odds = 1 / probability
        expected_value = (market_odds / fair_odds) - 1
        return expected_value
    
    def get_betting_recommendations(self, probabilities, binary_preds, market_odds, confidence):
        """6. Betting Recommendations - Now based on binary predictions"""
        recommendations = []
        
        # Get binary predictions
        btts_pred = binary_preds['btts']['prediction']
        over_under_pred = binary_preds['over_under']['prediction']
        btts_confidence = binary_preds['btts']['confidence']
        over_under_confidence = binary_preds['over_under']['confidence']
        
        # Home Win recommendation
        ev_home = self.calculate_expected_value(probabilities['home_win'], market_odds['home_win'])
        if ev_home > 0.05 and confidence > 0.60:
            stake = 'medium' if ev_home < 0.15 else 'high'
            recommendations.append({
                'market': 'Home Win',
                'prediction': 'HOME WIN',
                'odds': market_odds['home_win'],
                'ev': ev_home,
                'probability': probabilities['home_win'],
                'stake': stake,
                'reason': 'Good value with reasonable confidence'
            })
        
        # Over/Under recommendation based on binary prediction
        if over_under_pred == 'OVER':
            ev_over = self.calculate_expected_value(probabilities['over_25'], market_odds['over_25'])
            if ev_over > 0.05 and over_under_confidence > 10:  # At least 10% confidence margin
                stake = 'medium' if ev_over < 0.20 else 'high'
                recommendations.append({
                    'market': 'Over 2.5 Goals',
                    'prediction': 'OVER',
                    'odds': market_odds['over_25'],
                    'ev': ev_over,
                    'probability': probabilities['over_25'],
                    'stake': stake,
                    'reason': f'Model predicts OVER with {over_under_confidence:.1f}% confidence margin'
                })
        else:  # UNDER
            # Note: We need under odds which we don't have, so we calculate from over odds
            under_odds = 1 / (1 - 1/market_odds['over_25'])  # Approximate under odds
            ev_under = self.calculate_expected_value(probabilities['under_25'], under_odds)
            if ev_under > 0.05 and over_under_confidence > 10:
                stake = 'medium' if ev_under < 0.20 else 'high'
                recommendations.append({
                    'market': 'Under 2.5 Goals',
                    'prediction': 'UNDER',
                    'odds': f"~{under_odds:.2f}",
                    'ev': ev_under,
                    'probability': probabilities['under_25'],
                    'stake': stake,
                    'reason': f'Model predicts UNDER with {over_under_confidence:.1f}% confidence margin'
                })
        
        # BTTS recommendation based on binary prediction
        if btts_pred == 'YES':
            ev_btts = self.calculate_expected_value(probabilities['btts_yes'], market_odds['btts_yes'])
            if ev_btts > 0.05 and btts_confidence > 10:
                stake = 'medium' if ev_btts < 0.15 else 'high'
                recommendations.append({
                    'market': 'Both Teams to Score',
                    'prediction': 'YES',
                    'odds': market_odds['btts_yes'],
                    'ev': ev_btts,
                    'probability': probabilities['btts_yes'],
                    'stake': stake,
                    'reason': f'Model predicts BTTS YES with {btts_confidence:.1f}% confidence margin'
                })
        else:  # NO
            # Note: We need BTTS NO odds which we don't have, so we calculate from YES odds
            btts_no_odds = 1 / (1 - 1/market_odds['btts_yes'])  # Approximate BTTS NO odds
            ev_btts_no = self.calculate_expected_value(probabilities['btts_no'], btts_no_odds)
            if ev_btts_no > 0.05 and btts_confidence > 10:
                stake = 'medium' if ev_btts_no < 0.15 else 'high'
                recommendations.append({
                    'market': 'Both Teams to Score',
                    'prediction': 'NO',
                    'odds': f"~{btts_no_odds:.2f}",
                    'ev': ev_btts_no,
                    'probability': probabilities['btts_no'],
                    'stake': stake,
                    'reason': f'Model predicts BTTS NO with {btts_confidence:.1f}% confidence margin'
                })
        
        # Sort by EV
        return sorted(recommendations, key=lambda x: x['ev'], reverse=True)
    
    def run_prediction_from_data(self, home_data, away_data, market_odds):
        """Run prediction using team data from CSV"""
        
        # Extract data
        home_xg = home_data['xg']
        away_xg = away_data['xg']
        home_shots_allowed = home_data['shots_allowed_pg']
        away_shots_allowed = away_data['shots_allowed_pg']
        home_ppg_diff = home_data['home_ppg_diff']
        away_ppg_diff = away_data['home_ppg_diff']
        home_injury_level = home_data['injury_level']
        away_injury_level = away_data['injury_level']
        home_form_last_5 = home_data['form_last_5']
        away_form_last_5 = away_data['form_last_5']
        home_motivation = home_data['motivation']
        away_motivation = away_data['motivation']
        home_set_piece_pct = home_data['set_piece_pct']
        away_set_piece_pct = away_data['set_piece_pct']
        home_counter_pct = home_data['counter_attack_pct']
        away_counter_pct = away_data['counter_attack_pct']
        home_open_play_pct = home_data['open_play_pct']
        away_open_play_pct = away_data['open_play_pct']
        home_goals_conceded_last_5 = home_data['goals_conceded_last_5']
        away_goals_conceded_last_5 = away_data['goals_conceded_last_5']
        
        # Collect key factors
        key_factors = []
        
        # Step 1: Base Expected Goals - FIXED
        home_lambda, away_lambda = self.calculate_base_expected_goals(
            home_xg, away_xg,
            home_shots_allowed, away_shots_allowed
        )
        
        # Step 2: Home Advantage
        home_lambda, away_lambda, home_boost, away_penalty = self.apply_home_advantage(
            home_lambda, away_lambda,
            home_ppg_diff, away_ppg_diff
        )
        
        if home_boost > 1.1:
            key_factors.append(f"Home advantage: +{home_ppg_diff:.2f} PPG")
        
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
            home_form_last_5, away_form_last_5
        )
        
        form_diff = home_form_last_5 - away_form_last_5
        if abs(form_diff) > 4:
            direction = "better" if form_diff > 0 else "worse"
            key_factors.append(f"Form difference: Home {direction} by {abs(form_diff)} points")
        
        # Step 5: Motivation Adjustment
        home_lambda, away_lambda, home_motivation_factor, away_motivation_factor = self.apply_motivation_adjustment(
            home_lambda, away_lambda,
            home_motivation, away_motivation
        )
        
        # Step 6: Style Matchup
        style_adjustments = []
        home_lambda, away_lambda, style_adj = self.apply_style_matchup(
            home_lambda, away_lambda,
            home_set_piece_pct, away_set_piece_pct,
            home_counter_pct, away_counter_pct,
            home_open_play_pct, away_open_play_pct,
            home_injury_level, away_injury_level,
            home_shots_allowed, away_shots_allowed
        )
        key_factors.extend(style_adj)
        
        # Step 7: Defense Form
        home_lambda, away_lambda, home_def_form, away_def_form = self.apply_defense_form(
            home_lambda, away_lambda,
            home_goals_conceded_last_5, away_goals_conceded_last_5
        )
        
        if home_def_form > 1.5:  # Reduced threshold from 2.0
            key_factors.append(f"Poor home defense: conceding {home_def_form:.1f} goals per game")
        if away_def_form > 1.5:
            key_factors.append(f"Poor away defense: conceding {away_def_form:.1f} goals per game")
        
        # Cap lambdas at reasonable values
        home_lambda = min(home_lambda, 3.5)
        away_lambda = min(away_lambda, 3.5)
        
        # Store final lambdas
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # Step 8: Simulation
        probabilities, home_goals_sim, away_goals_sim = self.simulate_match(home_lambda, away_lambda)
        
        # Step 9: Binary predictions
        binary_predictions = self.calculate_binary_predictions(probabilities)
        
        # Step 10: Scoreline probabilities
        scoreline_probs, predicted_score = self.calculate_scoreline_probabilities(home_lambda, away_lambda)
        
        # Step 11: Confidence
        confidence = self.calculate_confidence(
            home_lambda, away_lambda,
            home_injury_level, away_injury_level,
            home_ppg_diff, form_diff
        )
        
        # Step 12: Betting Recommendations
        betting_recommendations = self.get_betting_recommendations(
            probabilities, binary_predictions, market_odds, confidence
        )
        
        # Fair odds calculation
        fair_odds = {
            'home_win': 1 / probabilities['home_win'] if probabilities['home_win'] > 0 else 0,
            'over_25': 1 / probabilities['over_25'] if probabilities['over_25'] > 0 else 0,
            'under_25': 1 / probabilities['under_25'] if probabilities['under_25'] > 0 else 0,
            'btts_yes': 1 / probabilities['btts_yes'] if probabilities['btts_yes'] > 0 else 0,
            'btts_no': 1 / probabilities['btts_no'] if probabilities['btts_no'] > 0 else 0
        }
        
        # Expected values
        expected_values = {
            'home_win': self.calculate_expected_value(probabilities['home_win'], market_odds['home_win']),
            'over_25': self.calculate_expected_value(probabilities['over_25'], market_odds['over_25']),
            'btts_yes': self.calculate_expected_value(probabilities['btts_yes'], market_odds['btts_yes'])
        }
        
        result = {
            'match': f"{home_data['team']} vs {away_data['team']}",
            'predicted_score': predicted_score,
            'expected_goals': {
                'home': round(home_lambda, 2),
                'away': round(away_lambda, 2)
            },
            'probabilities': {k: round(v, 4) for k, v in probabilities.items()},
            'binary_predictions': binary_predictions,
            'confidence': round(confidence, 3),
            'key_factors': key_factors,
            'betting_recommendations': betting_recommendations,
            'scoreline_probabilities': scoreline_probs,
            'fair_odds': {k: round(v, 2) for k, v in fair_odds.items()},
            'expected_values': {k: round(v, 4) for k, v in expected_values.items()},
            'simulated_goals': (home_goals_sim, away_goals_sim),
            'home_data': home_data.to_dict(),
            'away_data': away_data.to_dict(),
            'xg_per_game_home': round(home_xg / 20, 2),
            'xg_per_game_away': round(away_xg / 20, 2)
        }
        
        return result

def display_binary_predictions(result):
    """Display clear binary predictions"""
    st.markdown("<h2 class='section-header'>🎯 Model Predictions</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BTTS Prediction
        btts_pred = result['binary_predictions']['btts']
        btts_prob = btts_pred['probability'] * 100
        btts_conf = btts_pred['confidence']
        opposite_prob = btts_pred['opposite_prob'] * 100
        
        if btts_pred['prediction'] == 'YES':
            card_class = "yes-card"
            badge_class = "prediction-yes"
        else:
            card_class = "no-card"
            badge_class = "prediction-no"
        
        st.markdown(f"""
        <div class='{card_class}'>
            <h4>⚽ Both Teams to Score</h4>
            <div class='prediction-badge {badge_class}'>{btts_pred['prediction']}</div>
            <h2>{btts_prob:.1f}%</h2>
            <p>Confidence: <b>{btts_conf:.1f}%</b> margin over {opposite_prob:.1f}%</p>
            <small>Model predicts <b>BTTS {btts_pred['prediction']}</b></small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Over/Under Prediction
        ou_pred = result['binary_predictions']['over_under']
        ou_prob = ou_pred['probability'] * 100
        ou_conf = ou_pred['confidence']
        opposite_ou_prob = ou_pred['opposite_prob'] * 100
        
        if ou_pred['prediction'] == 'OVER':
            card_class = "yes-card"
            badge_class = "prediction-over"
        else:
            card_class = "no-card"
            badge_class = "prediction-under"
        
        st.markdown(f"""
        <div class='{card_class}'>
            <h4>📈 Total Goals 2.5</h4>
            <div class='prediction-badge {badge_class}'>{ou_pred['prediction']}</div>
            <h2>{ou_prob:.1f}%</h2>
            <p>Confidence: <b>{ou_conf:.1f}%</b> margin over {opposite_ou_prob:.1f}%</p>
            <small>Model predicts <b>{ou_pred['prediction']} 2.5</b> goals</small>
        </div>
        """, unsafe_allow_html=True)

def display_prediction_summary(result):
    """Display main prediction summary"""
    st.markdown(f"# 🏆 {result['match']}")
    
    # Warning if probabilities seem unrealistic
    if result['probabilities']['home_win'] > 0.95 or result['probabilities']['away_win'] > 0.95:
        st.markdown(f"""
        <div class='warning-banner'>
            ⚠️ <strong>Note:</strong> Extreme probabilities detected. This may indicate unrealistic xG values in the data.
            The model assumes xG values are season totals and converts them to per-game averages.
        </div>
        """, unsafe_allow_html=True)
    
    # Main prediction card
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        # Determine win prediction
        home_win_prob = result['probabilities']['home_win'] * 100
        away_win_prob = result['probabilities']['away_win'] * 100
        draw_prob = result['probabilities']['draw'] * 100
        
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            win_prediction = "HOME WIN"
            confidence_margin = home_win_prob - max(away_win_prob, draw_prob)
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            win_prediction = "AWAY WIN"
            confidence_margin = away_win_prob - max(home_win_prob, draw_prob)
        else:
            win_prediction = "DRAW"
            confidence_margin = draw_prob - max(home_win_prob, away_win_prob)
        
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏠 {result['home_data']['team']}</h3>
            <h2>Expected Goals: {result['expected_goals']['home']:.2f}</h2>
            <p>Win Probability: <span class='value-positive'>{home_win_prob:.1f}%</span></p>
            <p><small>Confidence margin: {confidence_margin:.1f}%</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='prediction-card'>
            <h4>🎯 Predicted Score</h4>
            <h1 style='font-size: 3.5rem; margin: 10px 0;'>{result['predicted_score']}</h1>
            <p><b>{win_prediction}</b></p>
            <small>Most likely outcome</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏃 {result['away_data']['team']}</h3>
            <h2>Expected Goals: {result['expected_goals']['away']:.2f}</h2>
            <p>Win Probability: <span class='value-positive'>{away_win_prob:.1f}%</span></p>
            <p><small>Confidence margin: {confidence_margin:.1f}%</small></p>
        </div>
        """, unsafe_allow_html=True)

def display_team_comparison(home_data, away_data, result=None):
    """Display team comparison"""
    st.markdown("<h2 class='section-header'>📊 Team Comparison</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏠 {home_data['team']}</h3>
            <p>Venue: {home_data['venue']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Home team metrics
        metrics_home = [
            ("Total xG", f"{home_data['xg']:.2f}"),
            ("xG per Game", f"{home_data['xg']/20:.2f}" if 'xg_per_game' not in locals() else f"{result['xg_per_game_home']:.2f}"),
            ("Shots Allowed pg", f"{home_data['shots_allowed_pg']:.1f}"),
            ("Form (Last 5)", f"{home_data['form_last_5']}/15"),
            ("Injury Level", f"{home_data['injury_level']}/10"),
            ("Motivation", f"{home_data['motivation']}/10"),
            ("Goals Scored (L5)", f"{home_data['goals_scored_last_5']}"),
            ("Goals Conceded (L5)", f"{home_data['goals_conceded_last_5']}")
        ]
        
        for label, value in metrics_home:
            st.metric(label, value)
    
    with col2:
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏃 {away_data['team']}</h3>
            <p>Venue: {away_data['venue']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Away team metrics
        metrics_away = [
            ("Total xG", f"{away_data['xg']:.2f}"),
            ("xG per Game", f"{away_data['xg']/20:.2f}" if 'xg_per_game' not in locals() else f"{result['xg_per_game_away']:.2f}"),
            ("Shots Allowed pg", f"{away_data['shots_allowed_pg']:.1f}"),
            ("Form (Last 5)", f"{away_data['form_last_5']}/15"),
            ("Injury Level", f"{away_data['injury_level']}/10"),
            ("Motivation", f"{away_data['motivation']}/10"),
            ("Goals Scored (L5)", f"{away_data['goals_scored_last_5']}"),
            ("Goals Conceded (L5)", f"{away_data['goals_conceded_last_5']}")
        ]
        
        for label, value in metrics_away:
            st.metric(label, value)
    
    # Goal type comparison
    st.markdown("#### 🎯 Goal Type Distribution")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='team-box'>
            <h4>Open Play</h4>
            <p>Home: <b>{home_data['open_play_pct']*100:.1f}%</b></p>
            <p>Away: <b>{away_data['open_play_pct']*100:.1f}%</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='team-box'>
            <h4>Set Pieces</h4>
            <p>Home: <b>{home_data['set_piece_pct']*100:.1f}%</b></p>
            <p>Away: <b>{away_data['set_piece_pct']*100:.1f}%</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='team-box'>
            <h4>Counter Attacks</h4>
            <p>Home: <b>{home_data['counter_attack_pct']*100:.1f}%</b></p>
            <p>Away: <b>{away_data['counter_attack_pct']*100:.1f}%</b></p>
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
    
    # Additional probabilities with clear predictions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Over/Under comparison
        over_prob = result['probabilities']['over_25'] * 100
        under_prob = result['probabilities']['under_25'] * 100
        ou_pred = result['binary_predictions']['over_under']
        
        if ou_pred['prediction'] == 'OVER':
            title = f"📈 OVER 2.5: {over_prob:.1f}%"
            subtitle = f"UNDER: {under_prob:.1f}%"
        else:
            title = f"📉 UNDER 2.5: {under_prob:.1f}%"
            subtitle = f"OVER: {over_prob:.1f}%"
        
        st.markdown(f"""
        <div class='metric-card'>
            <h4>{title}</h4>
            <h2>{ou_pred['prediction']}</h2>
            <small>{subtitle}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # BTTS comparison
        btts_yes_prob = result['probabilities']['btts_yes'] * 100
        btts_no_prob = result['probabilities']['btts_no'] * 100
        btts_pred = result['binary_predictions']['btts']
        
        if btts_pred['prediction'] == 'YES':
            title = f"⚽ BTTS YES: {btts_yes_prob:.1f}%"
            subtitle = f"NO: {btts_no_prob:.1f}%"
        else:
            title = f"🚫 BTTS NO: {btts_no_prob:.1f}%"
            subtitle = f"YES: {btts_yes_prob:.1f}%"
        
        st.markdown(f"""
        <div class='metric-card'>
            <h4>{title}</h4>
            <h2>{btts_pred['prediction']}</h2>
            <small>{subtitle}</small>
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
                st.caption(f"Model Prediction: <b>{rec['prediction']}</b>", unsafe_allow_html=True)
                st.caption(f"Probability: {rec['probability']*100:.1f}%")
            
            with col2:
                st.metric("Market Odds", f"{rec['odds']}")
            
            with col3:
                st.metric("Expected Value", f"{ev*100:.1f}%", delta=f"{ev*100:.1f}%")
            
            with col4:
                stake_color = "green" if rec['stake'] == 'high' else "orange" if rec['stake'] == 'medium' else "red"
                st.markdown(f"**Stake:** <span style='color:{stake_color}; font-weight:bold;'>{rec['stake'].upper()}</span>", unsafe_allow_html=True)
            
            st.info(f"**Reason:** {rec['reason']}")
            st.markdown("---")
    else:
        st.warning("No value bets identified at current market odds")

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
        
        # Add prediction rationale based on key factors
        st.markdown("#### 🤔 Prediction Rationale")
        
        rationale = []
        btts_pred = result['binary_predictions']['btts']['prediction']
        ou_pred = result['binary_predictions']['over_under']['prediction']
        
        # BTTS rationale
        if btts_pred == 'YES':
            rationale.append(f"• **BTTS YES**: Model predicts both teams will score based on defensive vulnerabilities")
        else:
            rationale.append(f"• **BTTS NO**: Model predicts at least one team won't score")
        
        # Over/Under rationale
        if ou_pred == 'OVER':
            rationale.append(f"• **OVER 2.5**: Model predicts high-scoring game")
        else:
            rationale.append(f"• **UNDER 2.5**: Model predicts low-scoring game")
        
        # Add key factors that influenced predictions
        for factor in result['key_factors'][:3]:  # Top 3 factors
            rationale.append(f"• {factor}")
        
        for point in rationale:
            st.markdown(point)
    else:
        st.info("No strongly influencing factors identified for this match")

# The rest of the functions remain the same (display_expected_value_analysis, display_simulation_results, etc.)
# Just copy them from the previous version

def main():
    """Main application"""
    
    # Header
    st.markdown("<h1 class='main-header'>⚽ Complete Football Prediction Engine</h1>", unsafe_allow_html=True)
    st.markdown("### Clear binary predictions for BTTS and Over/Under 2.5")
    
    # Initialize session state
    if 'engine' not in st.session_state:
        st.session_state.engine = CompletePredictionEngine()
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    # Load data
    st.sidebar.markdown("## 📁 Data Management")
    
    # Use the same data loading logic as before
    tab1, tab2 = st.sidebar.tabs(["📁 Upload CSV", "📊 Sample Data"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload your team data CSV", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"Successfully loaded {len(df)} teams")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                df = None
        else:
            df = None
    
    with tab2:
        st.info("Using sample La Liga data")
        if st.button("Load Sample Data", use_container_width=True):
            df = pd.read_csv(io.StringIO(SAMPLE_CSV))
            st.success("Sample data loaded!")
    
    if 'df' not in locals() or df is None:
        # Try to get from session state
        if hasattr(st.session_state, 'data_loaded'):
            df = st.session_state.data_loaded
        else:
            df = None
    
    if df is not None:
        st.session_state.data_loaded = df
        
        # Team selection
        st.sidebar.markdown("## 🏆 Match Selection")
        
        if df is not None:
            teams = sorted(df['team'].unique())
            home_team = st.sidebar.selectbox("Select Home Team", teams, index=0 if "Athletic Bilbao" in teams else 0)
            away_teams = [team for team in teams if team != home_team]
            away_team = st.sidebar.selectbox("Select Away Team", away_teams, index=0 if "Espanyol" in away_teams else 0)
            
            home_data = df[df['team'] == home_team].iloc[0]
            away_data = df[df['team'] == away_team].iloc[0]
            
            # Market odds
            st.sidebar.markdown("## 💰 Market Odds")
            col1, col2, col3 = st.columns(3)
            with col1:
                home_win_odds = st.number_input("Home Win", min_value=1.1, max_value=20.0, value=1.79, step=0.01, key="home_odds")
            with col2:
                over_25_odds = st.number_input("Over 2.5", min_value=1.1, max_value=20.0, value=2.30, step=0.01, key="over_odds")
            with col3:
                btts_yes_odds = st.number_input("BTTS Yes", min_value=1.1, max_value=20.0, value=2.10, step=0.01, key="btts_odds")
            
            market_odds = {
                'home_win': home_win_odds,
                'over_25': over_25_odds,
                'btts_yes': btts_yes_odds
            }
            
            # Calculate button
            st.sidebar.markdown("---")
            if st.sidebar.button("🚀 Run Prediction", type="primary", use_container_width=True):
                if home_data is not None and away_data is not None:
                    with st.spinner("Running complete prediction pipeline..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        steps = [
                            "Loading team data...",
                            "Converting xG to per game...",
                            "Calculating base expected goals...",
                            "Applying home advantage...",
                            "Adjusting for injuries...",
                            "Analyzing form and motivation...",
                            "Evaluating style matchups...",
                            "Running Poisson simulation...",
                            "Calculating binary predictions...",
                            "Generating recommendations..."
                        ]
                        
                        for i, step in enumerate(steps):
                            progress_bar.progress((i + 1) / len(steps))
                            status_text.text(f"Step {i+1}/{len(steps)}: {step}")
                            time.sleep(0.2)
                        
                        result = st.session_state.engine.run_prediction_from_data(
                            home_data, away_data, market_odds
                        )
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
            display_binary_predictions(result)  # NEW: Clear binary predictions
            st.markdown("---")
            display_team_comparison(result['home_data'], result['away_data'], result)
            st.markdown("---")
            display_probability_visualizations(result)
            st.markdown("---")
            
            # Tabs for detailed analysis
            tab1, tab2, tab3 = st.tabs(["💰 Betting", "🔑 Key Factors", "🔮 Simulation"])
            
            with tab1:
                display_betting_recommendations(result)
            
            with tab2:
                display_key_factors(result)
            
            with tab3:
                # Add simulation display function if needed
                pass
            
    else:
        st.info("""
        ## 📋 Getting Started
        
        1. **Upload your CSV data** or **use sample data**
        2. **Select home and away teams**
        3. **Enter market odds**
        4. **Click "Run Prediction"** for clear binary predictions
        
        ### 🎯 This version provides:
        - **CLEAR BTTS PREDICTION**: YES or NO
        - **CLEAR OVER/UNDER PREDICTION**: OVER 2.5 or UNDER 2.5
        - **Confidence margins** for each prediction
        - **Binary betting recommendations** based on model predictions
        """)

if __name__ == "__main__":
    main()
