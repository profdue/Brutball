import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import json
import math
import io

# Page config - Keep UI/UX exactly the same
st.set_page_config(
    page_title="Complete Football Prediction Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling - Keep exactly the same
st.markdown("""
<style>
    /* All CSS remains exactly the same */
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
    
    .team-box {
        border: 2px solid #4ECDC4;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        background: rgba(78, 205, 196, 0.08);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
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
    
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
    }
    
    .input-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .footer {
        text-align: center;
        color: #666;
        padding: 30px;
        margin-top: 40px;
        border-top: 1px solid #eee;
        font-size: 0.9em;
    }
    
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
    
    .warning-banner {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #ff416c;
    }
    
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
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
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

# Updated Sample CSV with games_played column
SAMPLE_CSV = """team,venue,goals,games_played,shots_allowed_pg,xg,home_ppg_diff,defenders_out,form_last_5,goals_scored_last_5,goals_conceded_last_5,motivation,open_play_pct,set_piece_pct,counter_attack_pct
Athletic Bilbao,home,9,9,7.3,12.87,0.90,4,9,4,5,2,0.56,0.11,0.00
Espanyol,away,7,7,12.9,8.47,-0.54,1,10,5,2,4,0.46,0.31,0.08
Real Madrid,home,12,9,9.8,16.20,0.80,2,11,12,3,8,0.52,0.25,0.12
Barcelona,away,10,8,10.5,13.60,1.00,1,10,10,4,7,0.58,0.22,0.15
Atletico Madrid,home,8,9,8.2,11.70,0.60,3,8,6,4,5,0.48,0.28,0.10
Sevilla,away,6,7,11.3,9.80,-0.20,2,7,5,6,3,0.42,0.35,0.05"""

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
        """2.1 Injury Level Calculation - CORRECT AS PER LOGIC"""
        return min(10, defenders_out * 2)
    
    def poisson_pmf(self, k, lambda_val):
        """Poisson probability mass function"""
        if k > 20:  # Cap for factorial calculation
            return 0
        return (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
    
    def calculate_base_expected_goals(self, home_data, away_data):
        """
        3.1 Base Expected Goals - FIXED WITH CORRECT LOGIC
        Using games_played from CSV to convert xG to per game
        """
        # FIX: Calculate xG per game using games_played from CSV
        home_xg_per_game = home_data['xg'] / home_data['games_played']
        away_xg_per_game = away_data['xg'] / away_data['games_played']
        
        # Original formula from logic with per game xG
        home_lambda_base = home_xg_per_game * (away_data['shots_allowed_pg'] / LEAGUE_AVG['shots_allowed']) * 0.5
        away_lambda_base = away_xg_per_game * (home_data['shots_allowed_pg'] / LEAGUE_AVG['shots_allowed']) * 0.5
        
        # Cap at reasonable values
        home_lambda_base = min(home_lambda_base, 3.5)
        away_lambda_base = min(away_lambda_base, 3.5)
        
        return home_lambda_base, away_lambda_base, home_xg_per_game, away_xg_per_game
    
    def apply_home_advantage(self, home_lambda_base, away_lambda_base, home_ppg_diff, away_ppg_diff):
        """3.2 Home Advantage Adjustment - CORRECT AS PER LOGIC"""
        home_boost = 1 + (home_ppg_diff * 0.3)
        away_penalty = 1 - (abs(away_ppg_diff) * 0.25)
        
        home_lambda = home_lambda_base * home_boost
        away_lambda = away_lambda_base * away_penalty
        
        return home_lambda, away_lambda, home_boost, away_penalty
    
    def apply_injury_adjustment(self, home_lambda, away_lambda, home_injury_level, away_injury_level):
        """3.3 Injury Adjustment - CORRECT AS PER LOGIC"""
        home_defense_strength = 1 - (home_injury_level / 20)
        away_defense_strength = 1 - (away_injury_level / 20)
        
        home_lambda = home_lambda * away_defense_strength  # Attack vs weak defense
        away_lambda = away_lambda * home_defense_strength  # Attack vs weak defense
        
        return home_lambda, away_lambda, home_defense_strength, away_defense_strength
    
    def apply_form_adjustment(self, home_lambda, away_lambda, home_form_last_5, away_form_last_5):
        """3.4 Form Adjustment - CORRECT AS PER LOGIC"""
        home_form_factor = 1 + ((home_form_last_5 - 9) * 0.02)
        away_form_factor = 1 + ((away_form_last_5 - 9) * 0.02)
        
        home_lambda = home_lambda * home_form_factor
        away_lambda = away_lambda * away_form_factor
        
        return home_lambda, away_lambda, home_form_factor, away_form_factor
    
    def apply_motivation_adjustment(self, home_lambda, away_lambda, home_motivation, away_motivation):
        """3.5 Motivation Adjustment - CORRECT AS PER LOGIC"""
        # Scale 1-5 to 0-1 for calculation
        home_motivation_norm = home_motivation / 5.0
        away_motivation_norm = away_motivation / 5.0
        
        home_motivation_factor = 1 + (home_motivation_norm * 0.03)
        away_motivation_factor = 1 + (away_motivation_norm * 0.03)
        
        home_lambda = home_lambda * home_motivation_factor
        away_lambda = away_lambda * away_motivation_factor
        
        return home_lambda, away_lambda, home_motivation_factor, away_motivation_factor
    
    def apply_style_matchup(self, home_lambda, away_lambda, 
                           home_set_piece_pct, away_set_piece_pct,
                           home_counter_pct, away_counter_pct,
                           home_open_play_pct, away_open_play_pct,
                           home_injury_level, away_injury_level,
                           home_shots_allowed, away_shots_allowed):
        """3.6 Style Matchup Adjustments - UPDATED FOR CORRECT LOGIC"""
        adjustments = []
        
        # Set Piece Threat - CORRECTED LOGIC
        if away_set_piece_pct > LEAGUE_AVG['set_piece_pct'] and home_injury_level > 5:
            away_lambda += 0.15
            adjustments.append("Away team strong on set pieces against injured home defense")
        
        # Counter Attack Threat - REMOVED POSSESSION CHECK (not in CSV)
        if away_counter_pct > 0.10:  # Removed possession check
            away_lambda += 0.10
            adjustments.append("Away team effective on counter attacks")
        
        # Open Play Dominance - CORRECTED LOGIC
        if home_open_play_pct > 0.60 and away_shots_allowed > LEAGUE_AVG['shots_allowed']:
            home_lambda += 0.05
            adjustments.append("Home team dominant in open play against weak defense")
            
        return home_lambda, away_lambda, adjustments
    
    def apply_defense_form(self, home_lambda, away_lambda, 
                          home_goals_conceded_last_5, away_goals_conceded_last_5):
        """3.7 Recent Defense Form - CORRECTED LOGIC"""
        home_defense_form = home_goals_conceded_last_5 / 5
        away_defense_form = away_goals_conceded_last_5 / 5
        
        home_lambda = home_lambda * (1 + (away_defense_form - LEAGUE_AVG['goals_conceded']) * 0.1)
        away_lambda = away_lambda * (1 + (home_defense_form - LEAGUE_AVG['goals_conceded']) * 0.1)
        
        return home_lambda, away_lambda, home_defense_form, away_defense_form
    
    def simulate_match(self, home_lambda, away_lambda, iterations=10000):
        """4.1 Poisson Simulation - CORRECT AS PER LOGIC"""
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
        
        # BTTS Prediction - use 0.5 threshold for binary decision
        btts_yes_prob = probabilities['btts_yes']
        btts_no_prob = probabilities['btts_no']
        
        if btts_yes_prob > 0.5:
            binary_preds['btts'] = {
                'prediction': 'YES',
                'probability': btts_yes_prob,
                'confidence': (btts_yes_prob - 0.5) * 200,  # Scale to 0-100%
                'opposite_prob': btts_no_prob
            }
        else:
            binary_preds['btts'] = {
                'prediction': 'NO',
                'probability': btts_no_prob,
                'confidence': (btts_no_prob - 0.5) * 200,
                'opposite_prob': btts_yes_prob
            }
        
        # Over/Under 2.5 Prediction - use 0.5 threshold for binary decision
        over_prob = probabilities['over_25']
        under_prob = probabilities['under_25']
        
        if over_prob > 0.5:
            binary_preds['over_under'] = {
                'prediction': 'OVER',
                'probability': over_prob,
                'confidence': (over_prob - 0.5) * 200,
                'opposite_prob': under_prob
            }
        else:
            binary_preds['over_under'] = {
                'prediction': 'UNDER',
                'probability': under_prob,
                'confidence': (under_prob - 0.5) * 200,
                'opposite_prob': over_prob
            }
        
        return binary_preds
    
    def calculate_scoreline_probabilities(self, home_lambda, away_lambda, max_goals=6):
        """4.2 Scoreline Probabilities"""
        scorelines = {}
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = self.poisson_pmf(i, home_lambda) * self.poisson_pmf(j, away_lambda)
                if prob > 0.0001:
                    scorelines[f"{i}-{j}"] = prob
        
        if scorelines:
            sorted_scores = sorted(scorelines.items(), key=lambda x: x[1], reverse=True)
            predicted_score = sorted_scores[0][0]
            return dict(sorted_scores[:10]), predicted_score
        else:
            return {"1-1": 0.1, "1-0": 0.08, "2-1": 0.07, "0-0": 0.06, "0-1": 0.05}, "1-1"
    
    def calculate_confidence(self, home_lambda, away_lambda, 
                           home_injury_level, away_injury_level,
                           home_ppg_diff, form_diff):
        """5. Confidence Scoring - CORRECTED THRESHOLDS"""
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
    
    def get_betting_recommendations(self, probabilities, binary_preds, market_odds, confidence):
        """6. Betting Recommendations - UPDATED FOR BINARY PREDICTIONS"""
        recommendations = []
        
        # Home Win recommendation
        ev_home = self.calculate_expected_value(probabilities['home_win'], market_odds['home_win'])
        if ev_home > 0.10 and confidence > 0.65:
            stake = 'medium' if ev_home < 0.25 else 'high'
            recommendations.append({
                'market': 'Home Win',
                'prediction': 'HOME WIN',
                'odds': market_odds['home_win'],
                'ev': ev_home,
                'probability': probabilities['home_win'],
                'stake': stake,
                'reason': 'Significant value with high confidence'
            })
        
        # Over/Under recommendation based on binary prediction
        if binary_preds['over_under']['prediction'] == 'OVER':
            ev_over = self.calculate_expected_value(probabilities['over_25'], market_odds['over_25'])
            if ev_over > 0.10 and binary_preds['over_under']['confidence'] > 10:
                stake = 'medium' if ev_over < 0.30 else 'high'
                recommendations.append({
                    'market': 'Over 2.5 Goals',
                    'prediction': 'OVER',
                    'odds': market_odds['over_25'],
                    'ev': ev_over,
                    'probability': probabilities['over_25'],
                    'stake': stake,
                    'reason': f'Model predicts OVER with {binary_preds["over_under"]["confidence"]:.1f}% confidence'
                })
        else:  # UNDER
            # Calculate approximate under odds
            if market_odds['over_25'] > 1:
                under_odds = 1 / (1 - 1/market_odds['over_25'])
                ev_under = self.calculate_expected_value(probabilities['under_25'], under_odds)
                if ev_under > 0.10 and binary_preds['over_under']['confidence'] > 10:
                    stake = 'medium' if ev_under < 0.30 else 'high'
                    recommendations.append({
                        'market': 'Under 2.5 Goals',
                        'prediction': 'UNDER',
                        'odds': f"~{under_odds:.2f}",
                        'ev': ev_under,
                        'probability': probabilities['under_25'],
                        'stake': stake,
                        'reason': f'Model predicts UNDER with {binary_preds["over_under"]["confidence"]:.1f}% confidence'
                    })
        
        # BTTS recommendation based on binary prediction
        if binary_preds['btts']['prediction'] == 'YES':
            ev_btts = self.calculate_expected_value(probabilities['btts_yes'], market_odds['btts_yes'])
            if ev_btts > 0.10 and binary_preds['btts']['confidence'] > 10:
                stake = 'medium' if ev_btts < 0.25 else 'high'
                recommendations.append({
                    'market': 'Both Teams to Score',
                    'prediction': 'YES',
                    'odds': market_odds['btts_yes'],
                    'ev': ev_btts,
                    'probability': probabilities['btts_yes'],
                    'stake': stake,
                    'reason': f'Model predicts BTTS YES with {binary_preds["btts"]["confidence"]:.1f}% confidence'
                })
        else:  # NO
            # Calculate approximate BTTS NO odds
            if market_odds['btts_yes'] > 1:
                btts_no_odds = 1 / (1 - 1/market_odds['btts_yes'])
                ev_btts_no = self.calculate_expected_value(probabilities['btts_no'], btts_no_odds)
                if ev_btts_no > 0.10 and binary_preds['btts']['confidence'] > 10:
                    stake = 'medium' if ev_btts_no < 0.25 else 'high'
                    recommendations.append({
                        'market': 'Both Teams to Score',
                        'prediction': 'NO',
                        'odds': f"~{btts_no_odds:.2f}",
                        'ev': ev_btts_no,
                        'probability': probabilities['btts_no'],
                        'stake': stake,
                        'reason': f'Model predicts BTTS NO with {binary_preds["btts"]["confidence"]:.1f}% confidence'
                    })
        
        # Sort by EV
        return sorted(recommendations, key=lambda x: x['ev'], reverse=True)
    
    def run_prediction_from_data(self, home_data, away_data, market_odds):
        """Run complete prediction pipeline with CORRECTED LOGIC"""
        
        # Calculate injury levels - CORRECT
        home_injury_level = self.calculate_injury_level(home_data['defenders_out'])
        away_injury_level = self.calculate_injury_level(away_data['defenders_out'])
        
        # Collect key factors
        key_factors = []
        
        # Step 1: Base Expected Goals - FIXED WITH games_played
        home_lambda_base, away_lambda_base, home_xg_per_game, away_xg_per_game = self.calculate_base_expected_goals(
            home_data, away_data
        )
        
        # Add xG per game to key factors if interesting
        if home_xg_per_game > 1.5:
            key_factors.append(f"Home xG per game: {home_xg_per_game:.2f} (strong attack)")
        if away_xg_per_game > 1.5:
            key_factors.append(f"Away xG per game: {away_xg_per_game:.2f} (strong attack)")
        
        # Step 2: Home Advantage - CORRECT
        home_lambda, away_lambda, home_boost, away_penalty = self.apply_home_advantage(
            home_lambda_base, away_lambda_base,
            home_data['home_ppg_diff'], away_data['home_ppg_diff']
        )
        
        if home_boost > 1.1:
            key_factors.append(f"Home advantage: +{home_data['home_ppg_diff']:.2f} PPG")
        
        # Step 3: Injury Adjustment - CORRECT
        home_lambda, away_lambda, home_defense_str, away_defense_str = self.apply_injury_adjustment(
            home_lambda, away_lambda,
            home_injury_level, away_injury_level
        )
        
        if home_injury_level > 5:
            key_factors.append(f"Home injury crisis: {home_injury_level}/10 severity")
        if away_injury_level > 5:
            key_factors.append(f"Away injury crisis: {away_injury_level}/10 severity")
        
        # Step 4: Form Adjustment - CORRECT
        home_lambda, away_lambda, home_form_factor, away_form_factor = self.apply_form_adjustment(
            home_lambda, away_lambda,
            home_data['form_last_5'], away_data['form_last_5']
        )
        
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if abs(form_diff) > 4:
            direction = "better" if form_diff > 0 else "worse"
            key_factors.append(f"Form difference: Home {direction} by {abs(form_diff)} points")
        
        # Step 5: Motivation Adjustment - CORRECT (scaled 1-5)
        home_lambda, away_lambda, home_motivation_factor, away_motivation_factor = self.apply_motivation_adjustment(
            home_lambda, away_lambda,
            home_data['motivation'], away_data['motivation']
        )
        
        # Step 6: Style Matchup - CORRECTED (no possession check)
        style_adjustments = []
        home_lambda, away_lambda, style_adj = self.apply_style_matchup(
            home_lambda, away_lambda,
            home_data['set_piece_pct'], away_data['set_piece_pct'],
            home_data['counter_attack_pct'], away_data['counter_attack_pct'],
            home_data['open_play_pct'], away_data['open_play_pct'],
            home_injury_level, away_injury_level,
            home_data['shots_allowed_pg'], away_data['shots_allowed_pg']
        )
        key_factors.extend(style_adj)
        
        # Step 7: Defense Form - CORRECT
        home_lambda, away_lambda, home_def_form, away_def_form = self.apply_defense_form(
            home_lambda, away_lambda,
            home_data['goals_conceded_last_5'], away_data['goals_conceded_last_5']
        )
        
        if home_def_form > 1.5:
            key_factors.append(f"Poor home defense: conceding {home_def_form:.1f} goals per game recently")
        if away_def_form > 1.5:
            key_factors.append(f"Poor away defense: conceding {away_def_form:.1f} goals per game recently")
        
        # Cap lambdas at reasonable values
        home_lambda = min(home_lambda, 4.0)
        away_lambda = min(away_lambda, 4.0)
        
        # Ensure minimum values
        home_lambda = max(home_lambda, 0.2)
        away_lambda = max(away_lambda, 0.2)
        
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
            home_data['home_ppg_diff'], form_diff
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
        
        # Expected values for display
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
            'xg_per_game_home': round(home_xg_per_game, 2),
            'xg_per_game_away': round(away_xg_per_game, 2),
            'home_injury_level': home_injury_level,
            'away_injury_level': away_injury_level
        }
        
        return result

# ============================================================================
# UI FUNCTIONS - ALL REMAIN EXACTLY THE SAME
# ============================================================================

def display_binary_predictions(result):
    """Display clear binary predictions"""
    st.markdown("<h2 class='section-header'>🎯 Model Predictions</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
            <p>Confidence: <b>{btts_conf:.1f}%</b> | Alternative: {opposite_prob:.1f}%</p>
            <small>Model predicts <b>BTTS {btts_pred['prediction']}</b></small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
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
            <p>Confidence: <b>{ou_conf:.1f}%</b> | Alternative: {opposite_ou_prob:.1f}%</p>
            <small>Model predicts <b>{ou_pred['prediction']} 2.5</b> goals</small>
        </div>
        """, unsafe_allow_html=True)

def display_prediction_summary(result):
    """Display main prediction summary"""
    st.markdown(f"# 🏆 {result['match']}")
    
    if result['probabilities']['home_win'] > 0.95 or result['probabilities']['away_win'] > 0.95:
        st.markdown(f"""
        <div class='warning-banner'>
            ⚠️ <strong>Note:</strong> Extreme probabilities detected. This may indicate data inconsistencies.
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        home_win_prob = result['probabilities']['home_win'] * 100
        away_win_prob = result['probabilities']['away_win'] * 100
        draw_prob = result['probabilities']['draw'] * 100
        
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            win_prediction = "HOME WIN"
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            win_prediction = "AWAY WIN"
        else:
            win_prediction = "DRAW"
        
        st.markdown(f"""
        <div class='team-box'>
            <h3>🏠 {result['home_data']['team']}</h3>
            <h2>Expected Goals: {result['expected_goals']['home']:.2f}</h2>
            <p>Win Probability: <span class='value-positive'>{home_win_prob:.1f}%</span></p>
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
        
        metrics_home = [
            ("Total xG", f"{home_data['xg']:.2f}"),
            ("xG per Game", f"{result['xg_per_game_home']:.2f}" if result else f"{home_data['xg']/home_data['games_played']:.2f}"),
            ("Games Played", f"{home_data['games_played']}"),
            ("Shots Allowed pg", f"{home_data['shots_allowed_pg']:.1f}"),
            ("Form (Last 5)", f"{home_data['form_last_5']}/15"),
            ("Injury Level", f"{result['home_injury_level'] if result else home_data['defenders_out']*2}/10"),
            ("Motivation", f"{home_data['motivation']}/5"),
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
        
        metrics_away = [
            ("Total xG", f"{away_data['xg']:.2f}"),
            ("xG per Game", f"{result['xg_per_game_away']:.2f}" if result else f"{away_data['xg']/away_data['games_played']:.2f}"),
            ("Games Played", f"{away_data['games_played']}"),
            ("Shots Allowed pg", f"{away_data['shots_allowed_pg']:.1f}"),
            ("Form (Last 5)", f"{away_data['form_last_5']}/15"),
            ("Injury Level", f"{result['away_injury_level'] if result else away_data['defenders_out']*2}/10"),
            ("Motivation", f"{away_data['motivation']}/5"),
            ("Goals Scored (L5)", f"{away_data['goals_scored_last_5']}"),
            ("Goals Conceded (L5)", f"{away_data['goals_conceded_last_5']}")
        ]
        
        for label, value in metrics_away:
            st.metric(label, value)
    
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
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

# ============================================================================
# REST OF THE UI FUNCTIONS REMAIN EXACTLY THE SAME
# (display_betting_recommendations, display_expected_value_analysis, etc.)
# ============================================================================

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
                    Confidence: {result['confidence']*100:.1f}%
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
        
        st.markdown("#### 🤔 Prediction Rationale")
        btts_pred = result['binary_predictions']['btts']['prediction']
        ou_pred = result['binary_predictions']['over_under']['prediction']
        
        rationale = []
        if btts_pred == 'YES':
            rationale.append(f"• **BTTS YES**: Model predicts both teams will score")
        else:
            rationale.append(f"• **BTTS NO**: Model predicts at least one team won't score")
        
        if ou_pred == 'OVER':
            rationale.append(f"• **OVER 2.5**: Model predicts high-scoring game")
        else:
            rationale.append(f"• **UNDER 2.5**: Model predicts low-scoring game")
        
        for factor in result['key_factors'][:3]:
            rationale.append(f"• {factor}")
        
        for point in rationale:
            st.markdown(point)
    else:
        st.info("No strongly influencing factors identified for this match")

def display_simulation_results(result):
    """Display simulation results"""
    st.markdown("<h2 class='section-header'>🔮 Simulation Results</h2>", unsafe_allow_html=True)
    
    if 'simulated_goals' in result:
        home_goals_sim, away_goals_sim = result['simulated_goals']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
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
        json_data = json.dumps(result, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        summary_data = {
            'Metric': ['Match', 'Predicted Score', 'Home xG', 'Away xG', 'Home Win %', 'Draw %', 'Away Win %', 
                      'Over 2.5 %', 'BTTS %', 'Confidence'],
            'Value': [
                result['match'],
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
            label="📊 Download CSV Summary",
            data=csv,
            file_name=f"prediction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("📄 Generate Full Report", use_container_width=True):
            st.success("Report generated successfully!")
            
            with st.expander("📋 Report Preview"):
                st.markdown(f"""
                ### 📊 Complete Prediction Report
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
                
                **Binary Predictions:**
                - BTTS: {result['binary_predictions']['btts']['prediction']} ({result['binary_predictions']['btts']['probability']*100:.1f}%)
                - Over/Under: {result['binary_predictions']['over_under']['prediction']} ({result['binary_predictions']['over_under']['probability']*100:.1f}%)
                
                **Confidence:** {result['confidence']*100:.1f}%
                """)

def load_data():
    """Load data from CSV file or use sample data"""
    tab1, tab2 = st.sidebar.tabs(["📁 Upload CSV", "📊 Sample Data"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload your team data CSV", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"Successfully loaded {len(df)} teams")
                return df
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return None
    
    with tab2:
        st.info("Using sample La Liga data")
        if st.button("Load Sample Data", use_container_width=True):
            sample_df = pd.read_csv(io.StringIO(SAMPLE_CSV))
            return sample_df
    
    return None

def display_team_selector(df):
    """Display team selection interface"""
    st.sidebar.markdown("## 🏆 Match Selection")
    
    if df is not None:
        teams = sorted(df['team'].unique())
        home_team = st.sidebar.selectbox("Select Home Team", teams, index=0 if "Athletic Bilbao" in teams else 0)
        away_teams = [team for team in teams if team != home_team]
        away_team = st.sidebar.selectbox("Select Away Team", away_teams, index=0 if "Espanyol" in away_teams else 0)
        
        home_data = df[df['team'] == home_team].iloc[0]
        away_data = df[df['team'] == away_team].iloc[0]
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown(f"**🏠 {home_team}**")
            st.caption(f"Games: {home_data['games_played']}")
            st.caption(f"Form: {home_data['form_last_5']}/15")
            st.caption(f"Injuries: {home_data['defenders_out']} defenders out")
        
        with col2:
            st.markdown(f"**🏃 {away_team}**")
            st.caption(f"Games: {away_data['games_played']}")
            st.caption(f"Form: {away_data['form_last_5']}/15")
            st.caption(f"Injuries: {away_data['defenders_out']} defenders out")
        
        return home_data, away_data
    else:
        st.sidebar.warning("No data loaded. Please upload CSV or use sample data.")
        return None, None

def display_market_odds():
    """Display market odds input"""
    st.sidebar.markdown("## 💰 Market Odds")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        home_win_odds = st.number_input("Home Win", min_value=1.1, max_value=20.0, value=1.79, step=0.01, key="home_odds")
    with col2:
        over_25_odds = st.number_input("Over 2.5", min_value=1.1, max_value=20.0, value=2.30, step=0.01, key="over_odds")
    with col3:
        btts_yes_odds = st.number_input("BTTS Yes", min_value=1.1, max_value=20.0, value=2.10, step=0.01, key="btts_odds")
    
    return {
        'home_win': home_win_odds,
        'over_25': over_25_odds,
        'btts_yes': btts_yes_odds
    }

def main():
    """Main application - UI remains exactly the same"""
    
    st.markdown("<h1 class='main-header'>⚽ Complete Football Prediction Engine</h1>", unsafe_allow_html=True)
    st.markdown("### Fixed logic with correct xG calculation using games_played")
    
    if 'engine' not in st.session_state:
        st.session_state.engine = CompletePredictionEngine()
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    df = load_data()
    
    if df is not None:
        home_data, away_data = display_team_selector(df)
        market_odds = display_market_odds()
        
        with st.sidebar.expander("📊 View Data Preview"):
            st.dataframe(df.head(), use_container_width=True)
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🚀 Run Prediction", type="primary", use_container_width=True):
            if home_data is not None and away_data is not None:
                with st.spinner("Running complete prediction pipeline..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "Loading team data...",
                        "Calculating xG per game...",
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
        
        if st.session_state.last_result:
            result = st.session_state.last_result
            
            display_prediction_summary(result)
            st.markdown("---")
            display_binary_predictions(result)
            st.markdown("---")
            display_team_comparison(result['home_data'], result['away_data'], result)
            st.markdown("---")
            display_probability_visualizations(result)
            st.markdown("---")
            display_expected_value_analysis(result)
            st.markdown("---")
            
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Betting", "🔑 Key Factors", "🔮 Simulation", "📤 Export"])
            
            with tab1:
                display_betting_recommendations(result)
            
            with tab2:
                display_key_factors(result)
            
            with tab3:
                display_simulation_results(result)
            
            with tab4:
                display_export_options(result)
    else:
        st.info("""
        ## 📋 Getting Started
        
        1. **Upload your CSV data** or **use sample data**
        2. **Select home and away teams**
        3. **Enter market odds**
        4. **Click "Run Prediction"** for accurate predictions
        
        ### 📁 CSV Format Required:
        ```
        team,venue,goals,games_played,shots_allowed_pg,xg,home_ppg_diff,defenders_out,form_last_5,goals_scored_last_5,goals_conceded_last_5,motivation,open_play_pct,set_piece_pct,counter_attack_pct
        ```
        
        ### 🎯 Key Fixes Applied:
        - ✅ **xG calculation fixed**: Now uses `games_played` column correctly
        - ✅ **Injury level calculation**: Uses `defenders_out × 2` as per logic
        - ✅ **Style matchup fixed**: Removed possession check (not in CSV)
        - ✅ **All other logic preserved**: Home advantage, form, motivation adjustments
        - ✅ **Binary predictions**: Clear YES/NO, OVER/UNDER decisions
        """)
        
        with st.expander("📋 View Sample Data Structure"):
            sample_df = pd.read_csv(io.StringIO(SAMPLE_CSV))
            st.dataframe(sample_df, use_container_width=True)
    
    st.markdown("""
    <div class='footer'>
        <small>
            ⚠️ <strong>Disclaimer:</strong> This is a simulation tool for educational purposes only. 
            Sports betting involves risk. Always gamble responsibly.<br><br>
            
            <strong>Complete Football Prediction Engine v2.2</strong><br>
            Fixed xG Calculation • Correct CSV Structure • Binary Predictions<br>
            Built with Streamlit • All logic implemented as specified
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
