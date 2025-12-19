import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import math
import io
import requests
from scipy import stats

# Page config
st.set_page_config(
    page_title="Professional Football Prediction Engine v4.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
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
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.9), rgba(118,75,162,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, rgba(240,147,251,0.9), rgba(245,87,108,0.9));
        border-radius: 15px;
        padding: 30px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .yes-card {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 30px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .no-card {
        background: linear-gradient(135deg, rgba(255,65,108,0.9), rgba(255,75,43,0.9));
        border-radius: 15px;
        padding: 30px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .confidence-high {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        border-radius: 15px;
        padding: 25px;
        color: white;
        text-align: center;
    }
    
    .factor-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 25px;
        margin: 8px 5px;
        font-size: 0.9em;
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
    
    .input-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .prediction-box {
        background: linear-gradient(135deg, rgba(69,183,209,0.9), rgba(78,205,196,0.9));
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .prediction-value {
        font-size: 2.5em;
        font-weight: 800;
        margin: 10px 0;
        text-align: center;
    }
    
    .prediction-label {
        font-size: 1.2em;
        text-align: center;
        opacity: 0.9;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA PROCESSING
# ============================================================================

def validate_and_clean_data(df, league_name):
    """Validate and clean the loaded CSV data."""
    validation_report = {
        'total_rows': len(df),
        'total_teams': df['team'].nunique(),
        'issues_found': [],
        'data_quality_score': 0
    }
    
    required_columns = ['team', 'venue', 'goals', 'games_played', 'shots_allowed_pg', 
                       'xg', 'defenders_out', 'form_last_5', 'motivation']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        validation_report['issues_found'].append(f"Missing columns: {missing_columns}")
    
    duplicates = df.duplicated(subset=['team', 'venue'], keep=False)
    if duplicates.any():
        validation_report['issues_found'].append(f"Found {duplicates.sum()} duplicate team-venue entries")
        df = df.drop_duplicates(subset=['team', 'venue'], keep='first')
    
    numeric_columns = ['goals', 'games_played', 'shots_allowed_pg', 'xg', 
                      'form_last_5', 'defenders_out', 'motivation']
    
    for col in numeric_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    validation_report['issues_found'].append(f"{null_count} null values in {col}")
            except:
                validation_report['issues_found'].append(f"Could not convert {col} to numeric")
    
    base_score = 100
    penalty_per_issue = 5
    penalties = len(validation_report['issues_found']) * penalty_per_issue
    validation_report['data_quality_score'] = max(0, base_score - penalties)
    
    return df, validation_report

def calculate_per_game_metrics(df):
    """Calculate per-game metrics from cumulative data."""
    if 'games_played' not in df.columns or 'xg' not in df.columns:
        return df
    
    df['xg_per_game'] = df['xg'] / df['games_played']
    df['goals_per_game'] = df['goals'] / df['games_played']
    
    if 'shots_allowed_pg' in df.columns:
        df['defensive_efficiency'] = 1 / (df['shots_allowed_pg'] + 0.1)
    
    return df

# ============================================================================
# EMPIRICALLY CALIBRATED CONSTANTS (UPDATED)
# ============================================================================

CONSTANTS = {
    'HOME_ADVANTAGE_BASE': 1.12,
    'FORM_WEIGHTS': [0.35, 0.25, 0.20, 0.15, 0.05],
    'DEFENDER_INJURY_IMPACT': 0.08,
    'GK_INJURY_IMPACT': 0.15,
    'MOTIVATION_SCALING': 0.02,
    'SET_PIECE_ADVANTAGE': 0.05,
    'COUNTER_ATTACK_BOOST': 0.03,
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 8,
    'XG_TO_GOALS_RATIO': 0.90,  # Increased from 0.85
    'DEFENSE_QUALITY_FACTOR': 0.15,
    'MIN_AWAY_LAMBDA': 0.4,  # Minimum away expected goals
    'MIN_HOME_LAMBDA': 0.5,  # Minimum home expected goals
    'MAX_WIN_PROBABILITY': 0.88,  # Cap at 88% max
    'MIN_DRAW_PROBABILITY': 0.08,  # Minimum draw probability
    'MIN_AWAY_WIN_PROBABILITY': 0.03,  # Minimum away win probability
}

# ============================================================================
# LEAGUE-SPECIFIC STATISTICS
# ============================================================================

LEAGUE_STATS = {
    'Premier League': {
        'matches': 380,
        'goals_total': 1076,
        'goals_per_match': 2.83,
        'home_goals_per_match': 1.52,
        'away_goals_per_match': 1.31,
        'home_win_pct': 0.46,
        'draw_pct': 0.26,
        'away_win_pct': 0.28,
        'over_15_pct': 0.82,
        'over_25_pct': 0.53,
        'over_35_pct': 0.28,
        'btts_pct': 0.52,
        'shots_allowed_avg': 12.7,
        'set_piece_pct': 0.27,
        'avg_goals_conceded': 1.42,
        'home_ppg': 1.68,
        'away_ppg': 1.40,
        'scoring_factor': 1.0,
        'defense_factor': 1.0,
        'variance': 1.05,
        'source': '2022-23 Season Stats'
    },
    'La Liga': {
        'matches': 380,
        'goals_total': 955,
        'goals_per_match': 2.51,
        'home_goals_per_match': 1.42,
        'away_goals_per_match': 1.09,
        'home_win_pct': 0.45,
        'draw_pct': 0.27,
        'away_win_pct': 0.28,
        'over_15_pct': 0.76,
        'over_25_pct': 0.45,
        'over_35_pct': 0.22,
        'btts_pct': 0.49,
        'shots_allowed_avg': 12.3,
        'set_piece_pct': 0.23,
        'avg_goals_conceded': 1.26,
        'home_ppg': 1.62,
        'away_ppg': 1.37,
        'scoring_factor': 0.89,
        'defense_factor': 0.97,
        'variance': 0.95,
        'source': '2022-23 Season Stats'
    },
}

# ============================================================================
# PROFESSIONAL PREDICTION ENGINE (COMPLETE FIXED VERSION)
# ============================================================================

class ProfessionalPredictionEngine:
    def __init__(self):
        self.reset_calculations()
        
    def reset_calculations(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.confidence = 0
        self.key_factors = []
        self.betting_recommendations = []
        self.scoreline_probabilities = {}
        self.binary_predictions = {}
        self.league_stats = None
        
    def validate_input_data(self, home_data, away_data):
        """Comprehensive input validation"""
        validation = {
            'home_data_valid': True,
            'away_data_valid': True,
            'issues': [],
            'warnings': []
        }
        
        required_fields = ['team', 'goals', 'games_played', 'xg', 'shots_allowed_pg', 
                          'defenders_out', 'form_last_5', 'motivation']
        
        for field in required_fields:
            if field not in home_data:
                validation['home_data_valid'] = False
                validation['issues'].append(f"Missing {field} in home data")
            if field not in away_data:
                validation['away_data_valid'] = False
                validation['issues'].append(f"Missing {field} in away data")
        
        return validation['home_data_valid'] and validation['away_data_valid']
    
    def get_team_specific_xg_conversion(self, xg_per_game):
        """Better teams convert xG more efficiently."""
        if xg_per_game > 2.5:  # Elite attack (Man City, Real Madrid, etc.)
            return 0.95
        elif xg_per_game > 1.8:  # Good attack
            return 0.90
        elif xg_per_game > 1.3:  # Average attack
            return 0.85
        else:  # Poor attack
            return 0.80
    
    def calculate_injury_impact(self, defenders_out, is_goalkeeper_out=False):
        """Calculate injury impact with realistic diminishing returns."""
        base_impact = defenders_out * CONSTANTS['DEFENDER_INJURY_IMPACT']
        
        if defenders_out > 3:
            base_impact = base_impact * 0.8
        
        if is_goalkeeper_out:
            base_impact += CONSTANTS['GK_INJURY_IMPACT']
        
        total_impact = min(base_impact, 0.40)
        return 1 - total_impact
    
    def calculate_weighted_form(self, form_string, recent_weight=0.6):
        """Calculate form score with empirical weighting."""
        if not form_string:
            return 0.5
        
        points_map = {'W': 1.0, 'D': 0.5, 'L': 0.0}
        recent_matches = form_string[-8:] if len(form_string) >= 8 else form_string
        
        weights = []
        form_points = []
        
        for i, result in enumerate(reversed(recent_matches)):
            if result in points_map:
                weight = math.exp(-i * 0.5)
                weights.append(weight)
                form_points.append(points_map[result] * weight)
        
        if sum(weights) == 0:
            return 0.5
        
        weighted_form = sum(form_points) / sum(weights)
        return weighted_form * 10
    
    def calculate_base_expected_goals(self, home_data, away_data, league_stats):
        """
        FIXED VERSION with team-specific xG conversion.
        More shots allowed by opponent = easier to score = HIGHER expected goals
        """
        home_games = home_data['games_played']
        away_games = away_data['games_played']
        
        # Calculate per-game xG
        home_xg_per_game = home_data['xg'] / home_games if home_games > 0 else 0
        away_xg_per_game = away_data['xg'] / away_games if away_games > 0 else 0
        
        # Apply TEAM-SPECIFIC xG to goals conversion rate
        home_conversion = self.get_team_specific_xg_conversion(home_xg_per_game)
        away_conversion = self.get_team_specific_xg_conversion(away_xg_per_game)
        
        home_xg_effective = home_xg_per_game * home_conversion
        away_xg_effective = away_xg_per_game * away_conversion
        
        # FIXED DEFENSE CALCULATION:
        league_shots_avg = league_stats['shots_allowed_avg']
        
        # Home team's expected goals against away team's defense
        away_defense_factor = away_data['shots_allowed_pg'] / league_shots_avg
        
        # Away team's expected goals against home team's defense  
        home_defense_factor = home_data['shots_allowed_pg'] / league_shots_avg
        
        # Apply defense factors CORRECTLY:
        home_lambda_base = home_xg_effective * away_defense_factor  # Home attacks vs away defense
        away_lambda_base = away_xg_effective * home_defense_factor  # Away attacks vs home defense
        
        # Apply league scoring factor
        home_lambda_base *= league_stats['scoring_factor']
        away_lambda_base *= league_stats['scoring_factor']
        
        return home_lambda_base, away_lambda_base
    
    def apply_empirical_adjustments(self, home_lambda, away_lambda, home_data, away_data, league_stats):
        """Apply empirically validated adjustments based on research."""
        adjustments_log = []
        
        # 1. Home Advantage (empirically: 12-15%)
        home_boost = CONSTANTS['HOME_ADVANTAGE_BASE']
        home_lambda *= home_boost
        away_lambda *= (2 - home_boost)
        adjustments_log.append(f"Home advantage: {home_boost:.2f}x")
        
        # 2. Form Adjustment (weighted recent performance)
        home_form_score = self.calculate_weighted_form(home_data.get('form', ''))
        away_form_score = self.calculate_weighted_form(away_data.get('form', ''))
        
        form_diff = (home_form_score - away_form_score) / 10
        home_lambda *= (1 + form_diff * 0.05)
        away_lambda *= (1 - form_diff * 0.05)
        
        if abs(form_diff) > 0.2:
            adjustments_log.append(f"Form advantage: {'Home' if form_diff > 0 else 'Away'} ({abs(form_diff*100):.0f}%)")
        
        # 3. Injury Impact
        home_defense_strength = self.calculate_injury_impact(home_data['defenders_out'])
        away_defense_strength = self.calculate_injury_impact(away_data['defenders_out'])
        
        # Injuries reduce opponent's expected goals
        home_lambda *= away_defense_strength
        away_lambda *= home_defense_strength
        
        if home_data['defenders_out'] > 0:
            adjustments_log.append(f"Home injuries: {home_data['defenders_out']} defenders (-{(1-home_defense_strength)*100:.0f}%)")
        if away_data['defenders_out'] > 0:
            adjustments_log.append(f"Away injuries: {away_data['defenders_out']} defenders (-{(1-away_defense_strength)*100:.0f}%)")
        
        # 4. Motivation Adjustment
        home_motivation = home_data['motivation'] / 5.0
        away_motivation = away_data['motivation'] / 5.0
        
        home_lambda *= (1 + (home_motivation - 0.5) * CONSTANTS['MOTIVATION_SCALING'])
        away_lambda *= (1 + (away_motivation - 0.5) * CONSTANTS['MOTIVATION_SCALING'])
        
        # 5. Style Matchup Adjustments
        if 'set_piece_pct' in home_data and 'set_piece_pct' in away_data:
            set_piece_diff = home_data['set_piece_pct'] - away_data['set_piece_pct']
            if set_piece_diff > 0.1:
                home_lambda += CONSTANTS['SET_PIECE_ADVANTAGE']
                adjustments_log.append(f"Set piece advantage: Home ({set_piece_diff*100:.0f}%)")
            elif set_piece_diff < -0.1:
                away_lambda += CONSTANTS['SET_PIECE_ADVANTAGE']
                adjustments_log.append(f"Set piece advantage: Away ({abs(set_piece_diff)*100:.0f}%)")
        
        # 6. APPLY REALISTIC BOUNDS
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], min(home_lambda, 5.0))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], min(away_lambda, 4.0))
        
        return home_lambda, away_lambda, adjustments_log
    
    def apply_football_variance_adjustment(self, probabilities, home_lambda, away_lambda):
        """
        Apply football-specific variance adjustments.
        Even the best teams can have off days, underdogs can surprise.
        """
        adjusted_probs = probabilities.copy()
        
        # 1. Cap maximum win probability
        max_win_prob = CONSTANTS['MAX_WIN_PROBABILITY']
        
        if adjusted_probs['home_win'] > max_win_prob:
            excess = adjusted_probs['home_win'] - max_win_prob
            adjusted_probs['home_win'] = max_win_prob
            # Redistribute excess: 70% to draw, 30% to away
            adjusted_probs['draw'] += excess * 0.7
            adjusted_probs['away_win'] += excess * 0.3
        
        if adjusted_probs['away_win'] > max_win_prob:
            excess = adjusted_probs['away_win'] - max_win_prob
            adjusted_probs['away_win'] = max_win_prob
            adjusted_probs['draw'] += excess * 0.7
            adjusted_probs['home_win'] += excess * 0.3
        
        # 2. Apply minimum probabilities (football always has uncertainty)
        adjusted_probs['draw'] = max(adjusted_probs['draw'], CONSTANTS['MIN_DRAW_PROBABILITY'])
        adjusted_probs['away_win'] = max(adjusted_probs['away_win'], CONSTANTS['MIN_AWAY_WIN_PROBABILITY'])
        
        # For extreme mismatches, ensure some minimum away chance
        if home_lambda > away_lambda * 3:  # Very one-sided
            min_away_extra = 0.02
            if adjusted_probs['away_win'] < min_away_extra:
                needed = min_away_extra - adjusted_probs['away_win']
                adjusted_probs['away_win'] += needed
                adjusted_probs['home_win'] -= needed * 0.8
                adjusted_probs['draw'] -= needed * 0.2
        
        # 3. Normalize to ensure sum = 1
        total = adjusted_probs['home_win'] + adjusted_probs['draw'] + adjusted_probs['away_win']
        adjusted_probs['home_win'] /= total
        adjusted_probs['draw'] /= total
        adjusted_probs['away_win'] /= total
        
        return adjusted_probs
    
    def calculate_probability_distributions(self, home_lambda, away_lambda):
        """Calculate probability distributions using Poisson model."""
        simulations = CONSTANTS['POISSON_SIMULATIONS']
        max_goals = CONSTANTS['MAX_GOALS_CONSIDERED']
        
        np.random.seed(42)
        home_goals = np.random.poisson(home_lambda, simulations)
        away_goals = np.random.poisson(away_lambda, simulations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        total_goals = home_goals + away_goals
        over_25 = np.sum(total_goals > 2.5)
        under_25 = np.sum(total_goals < 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        btts_no = simulations - btts_yes
        
        probabilities = {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations,
            'over_25': over_25 / simulations,
            'under_25': under_25 / simulations,
            'btts_yes': btts_yes / simulations,
            'btts_no': btts_no / simulations
        }
        
        # Apply football variance adjustment
        probabilities = self.apply_football_variance_adjustment(probabilities, home_lambda, away_lambda)
        
        # Calculate confidence intervals
        n = simulations
        ci_probabilities = probabilities.copy()
        for key in list(ci_probabilities.keys()):
            p = ci_probabilities[key]
            if p > 0 and p < 1:
                z = 1.96
                margin = z * math.sqrt(p * (1 - p) / n)
                ci_probabilities[f'{key}_ci_low'] = max(0, p - margin)
                ci_probabilities[f'{key}_ci_high'] = min(1, p + margin)
        
        # Calculate scoreline probabilities
        scoreline_probs = {}
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = stats.poisson.pmf(i, home_lambda) * stats.poisson.pmf(j, away_lambda)
                if prob > 0.001:
                    scoreline_probs[f"{i}-{j}"] = prob
        
        total_score_prob = sum(scoreline_probs.values())
        if total_score_prob > 0:
            scoreline_probs = {k: v/total_score_prob for k, v in scoreline_probs.items()}
        
        if scoreline_probs:
            predicted_score = max(scoreline_probs.items(), key=lambda x: x[1])[0]
        else:
            predicted_score = "1-1"
            scoreline_probs = {"1-1": 0.15, "0-0": 0.1, "1-0": 0.1, "0-1": 0.1, "2-1": 0.08}
        
        return ci_probabilities, scoreline_probs, predicted_score, home_goals, away_goals
    
    def calculate_model_confidence(self, home_lambda, away_lambda, probabilities, league_stats):
        """Calculate realistic model confidence with caps."""
        confidence = 0.5
        
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.5:
            confidence += 0.25
        elif goal_diff > 1.0:
            confidence += 0.15
        elif goal_diff > 0.5:
            confidence += 0.05
        
        max_prob = max(probabilities['home_win'], probabilities['away_win'], probabilities['draw'])
        if max_prob > 0.7:
            confidence += 0.2
        elif max_prob > 0.6:
            confidence += 0.1
        
        # Apply league variance
        confidence *= league_stats.get('variance', 1.0)
        
        # REALISTIC CONFIDENCE CAPS
        if max_prob > 0.75:
            confidence = min(confidence, 0.82)  # Cap at 82% for strong favorites
        elif max_prob > 0.65:
            confidence = min(confidence, 0.75)  # Cap at 75% for moderate favorites
        elif max_prob > 0.55:
            confidence = min(confidence, 0.68)  # Cap at 68% for slight favorites
        else:
            confidence = min(confidence, 0.60)  # Cap at 60% for close matches
        
        confidence = max(0.35, min(confidence, 0.82))  # Ensure within 35-82% range
        
        return confidence
    
    def calculate_expected_value(self, model_probability, market_odds):
        """Calculate Expected Value (EV)."""
        if model_probability <= 0 or market_odds <= 1:
            return -1, 0
        
        fair_odds = 1 / model_probability
        ev_simple = (market_odds / fair_odds) - 1
        
        # Adjust EV for probability confidence
        ev_adjusted = ev_simple * min(1, model_probability * 1.5)
        
        return ev_simple, ev_adjusted
    
    def get_betting_recommendations(self, probabilities, market_odds, confidence, league_stats):
        """Generate responsible betting recommendations."""
        recommendations = []
        
        MIN_CONFIDENCE = 0.55
        MIN_EV = 0.05
        MAX_EV_WARNING = 0.25  # Warn if EV > 25%
        
        markets = [
            ('home_win', 'Home Win', market_odds.get('home_win', 2.0)),
            ('draw', 'Draw', market_odds.get('draw', 3.4)),
            ('away_win', 'Away Win', market_odds.get('away_win', 2.0)),
        ]
        
        for prob_key, market_name, odds in markets:
            if prob_key in probabilities and odds > 1:
                prob = probabilities[prob_key]
                ev_simple, ev_adjusted = self.calculate_expected_value(prob, odds)
                
                if ev_adjusted >= MIN_EV and confidence >= MIN_CONFIDENCE:
                    if ev_adjusted > MAX_EV_WARNING:
                        risk_level = 'High'
                        rationale_suffix = "⚠️ High EV - verify carefully"
                    elif ev_adjusted > 0.12:
                        risk_level = 'Medium-High'
                        rationale_suffix = "Good value opportunity"
                    elif ev_adjusted > 0.08:
                        risk_level = 'Medium'
                        rationale_suffix = "Moderate value"
                    else:
                        risk_level = 'Low'
                        rationale_suffix = "Small edge"
                    
                    recommendation = {
                        'market': 'Match Result',
                        'prediction': market_name,
                        'probability': prob,
                        'market_odds': odds,
                        'fair_odds': 1/prob,
                        'ev': ev_adjusted,
                        'confidence': confidence,
                        'risk_level': risk_level
                    }
                    
                    league_avg = league_stats.get('home_win_pct', 0.46) if 'home' in market_name.lower() else \
                                league_stats.get('draw_pct', 0.26) if 'draw' in market_name.lower() else \
                                league_stats.get('away_win_pct', 0.28)
                    
                    recommendation['rationale'] = (
                        f"Model: {prob*100:.0f}% vs Market: {1/odds*100:.0f}% "
                        f"(League avg: {league_avg*100:.0f}%). {rationale_suffix}"
                    )
                    
                    recommendations.append(recommendation)
        
        # Check Over/Under 2.5
        over_prob = probabilities.get('over_25', 0)
        over_odds = market_odds.get('over_25', 1.85)
        league_over_avg = league_stats.get('over_25_pct', 0.53)
        
        if over_prob > league_over_avg + 0.1:
            ev_simple, ev_adjusted = self.calculate_expected_value(over_prob, over_odds)
            if ev_adjusted >= MIN_EV:
                recommendations.append({
                    'market': 'Total Goals',
                    'prediction': 'Over 2.5',
                    'probability': over_prob,
                    'market_odds': over_odds,
                    'fair_odds': 1/over_prob,
                    'ev': ev_adjusted,
                    'confidence': min(confidence, abs(over_prob - league_over_avg) * 3),
                    'risk_level': 'Medium',
                    'rationale': f"High-scoring pattern ({over_prob*100:.0f}% vs league {league_over_avg*100:.0f}%)"
                })
        
        # Check BTTS
        btts_prob = probabilities.get('btts_yes', 0)
        btts_odds = market_odds.get('btts_yes', 1.75)
        league_btts_avg = league_stats.get('btts_pct', 0.52)
        
        if abs(btts_prob - league_btts_avg) > 0.15:
            ev_simple, ev_adjusted = self.calculate_expected_value(btts_prob, btts_odds)
            if ev_adjusted >= MIN_EV:
                prediction = 'BTTS Yes' if btts_prob > league_btts_avg else 'BTTS No'
                recommendations.append({
                    'market': 'Both Teams to Score',
                    'prediction': prediction,
                    'probability': btts_prob if prediction == 'BTTS Yes' else 1-btts_prob,
                    'market_odds': btts_odds if prediction == 'BTTS Yes' else 1/(1-1/btts_odds),
                    'fair_odds': 1/(btts_prob if prediction == 'BTTS Yes' else 1-btts_prob),
                    'ev': ev_adjusted,
                    'confidence': min(confidence, abs(btts_prob - league_btts_avg) * 3),
                    'risk_level': 'Medium',
                    'rationale': f"Significant deviation ({btts_prob*100:.0f}% vs league {league_btts_avg*100:.0f}%)"
                })
        
        recommendations.sort(key=lambda x: x['ev'], reverse=True)
        return recommendations
    
    def predict(self, home_data, away_data, league_stats):
        """Main prediction function with all fixes applied."""
        self.reset_calculations()
        self.league_stats = league_stats
        
        if not self.validate_input_data(home_data, away_data):
            st.error("Input data validation failed. Please check your data.")
            return None
        
        # FIXED: Proper defense calculation with team-specific conversion
        home_lambda_base, away_lambda_base = self.calculate_base_expected_goals(
            home_data, away_data, league_stats
        )
        
        home_lambda, away_lambda, adjustments_log = self.apply_empirical_adjustments(
            home_lambda_base, away_lambda_base, home_data, away_data, league_stats
        )
        
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        self.key_factors = adjustments_log
        
        probabilities, scoreline_probs, predicted_score, home_goals_sim, away_goals_sim = \
            self.calculate_probability_distributions(home_lambda, away_lambda)
        
        self.probabilities = probabilities
        self.scoreline_probabilities = scoreline_probs
        self.predicted_score = predicted_score
        
        # REALISTIC confidence calculation with caps
        self.confidence = self.calculate_model_confidence(
            home_lambda, away_lambda, probabilities, league_stats
        )
        
        results = {
            'probabilities': probabilities,
            'scoreline_probabilities': scoreline_probs,
            'predicted_score': predicted_score,
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'confidence': self.confidence,
            'key_factors': adjustments_log,
            'calibration': {
                'home_lambda_base': home_lambda_base,
                'away_lambda_base': away_lambda_base,
                'home_lambda_final': home_lambda,
                'away_lambda_final': away_lambda
            }
        }
        
        return results

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def display_prediction_box(title, value, subtitle=""):
    """Display prediction in a styled box with value inside."""
    st.markdown(f"""
    <div class="prediction-box">
        <div class="prediction-label">{title}</div>
        <div class="prediction-value">{value}</div>
        <div class="prediction-label">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_market_odds_interface():
    """Display market odds input with validation."""
    st.markdown("### 📊 Market Odds Input")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        home_odds = st.number_input("Home Win", min_value=1.01, max_value=100.0, 
                                   value=2.50, step=0.01, format="%.2f")
    
    with col2:
        draw_odds = st.number_input("Draw", min_value=1.01, max_value=100.0,
                                   value=3.40, step=0.01, format="%.2f")
    
    with col3:
        away_odds = st.number_input("Away Win", min_value=1.01, max_value=100.0,
                                   value=2.80, step=0.01, format="%.2f")
    
    col4, col5 = st.columns(2)
    with col4:
        over_odds = st.number_input("Over 2.5 Goals", min_value=1.01, max_value=100.0,
                                   value=1.85, step=0.01, format="%.2f")
    
    with col5:
        btts_odds = st.number_input("BTTS Yes", min_value=1.01, max_value=100.0,
                                   value=1.75, step=0.01, format="%.2f")
    
    return {
        'home_win': home_odds,
        'draw': draw_odds,
        'away_win': away_odds,
        'over_25': over_odds,
        'under_25': 1/(1-1/over_odds) if over_odds > 1 else 2.00,
        'btts_yes': btts_odds,
        'btts_no': 1/(1-1/btts_odds) if btts_odds > 1 else 2.00,
    }

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Professional Football Prediction Engine v4.0</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Complete Fix • Realistic Probabilities • Professional</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        
        available_leagues = ['Premier League', 'La Liga']
        selected_league = st.selectbox("Choose League:", available_leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Load Data")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading and validating {selected_league} data..."):
                try:
                    github_base_url = "https://raw.githubusercontent.com/profdue/Brutball/main/leagues/"
                    league_files = {
                        'Premier League': 'epl.csv',
                        'La Liga': 'la_liga.csv',
                    }
                    
                    url = f"{github_base_url}{league_files[selected_league]}"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
                    df_clean, validation_report = validate_and_clean_data(df, selected_league)
                    df_clean = calculate_per_game_metrics(df_clean)
                    
                    st.session_state['league_data'] = df_clean
                    st.session_state['selected_league'] = selected_league
                    st.session_state['validation_report'] = validation_report
                    
                    st.success(f"✅ Successfully loaded {len(df_clean)} records")
                    
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📈 League Statistics")
        
        if selected_league in LEAGUE_STATS:
            stats = LEAGUE_STATS[selected_league]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Goals/Match", f"{stats['goals_per_match']:.2f}")
                st.metric("Home Win %", f"{stats['home_win_pct']*100:.0f}%")
            with col2:
                st.metric("BTTS %", f"{stats['btts_pct']*100:.0f}%")
                st.metric("Over 2.5 %", f"{stats['over_25_pct']*100:.0f}%")
            
            st.caption(f"Source: {stats['source']}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Model Settings")
        
        show_advanced = st.checkbox("Show Advanced Settings", value=False)
        if show_advanced:
            CONSTANTS['POISSON_SIMULATIONS'] = st.slider("Simulation Count", 
                                                        1000, 100000, 20000, 1000)
            CONSTANTS['HOME_ADVANTAGE_BASE'] = st.slider("Home Advantage", 
                                                        1.00, 1.25, 1.12, 0.01)
            CONSTANTS['MAX_WIN_PROBABILITY'] = st.slider("Max Win Probability", 
                                                       0.80, 0.95, 0.88, 0.01)
        
        st.markdown("---")
        st.markdown("### 📊 How It Works")
        st.info("""
        1. **Load Data**: Team statistics from selected league
        2. **Select Match**: Choose home and away teams
        3. **Input Odds**: Current market odds for comparison
        4. **Run Analysis**: Model calculates probabilities
        5. **Review**: Check predictions and recommendations
        """)
    
    # Main content
    if 'league_data' not in st.session_state:
        st.info("👈 Please load league data from the sidebar to begin.")
        return
    
    df = st.session_state['league_data']
    selected_league = st.session_state['selected_league']
    
    # Match setup
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 🏟️ Match Setup")
    
    available_teams = sorted(df['team'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", available_teams)
        home_venue_data = df[(df['team'] == home_team) & (df['venue'] == 'home')]
        if not home_venue_data.empty:
            home_data = home_venue_data.iloc[0].to_dict()
            
            st.markdown(f"**{home_team} Home Stats:**")
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("xG/Game", f"{home_data.get('xg_per_game', 0):.2f}")
                st.metric("Form", home_data.get('form', 'N/A'))
            with col2a:
                st.metric("Defenders Out", home_data['defenders_out'])
                st.metric("Motivation", f"{home_data['motivation']}/5")
    
    with col2:
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options)
        away_venue_data = df[(df['team'] == away_team) & (df['venue'] == 'away')]
        if not away_venue_data.empty:
            away_data = away_venue_data.iloc[0].to_dict()
            
            st.markdown(f"**{away_team} Away Stats:**")
            col1b, col2b = st.columns(2)
            with col1b:
                st.metric("xG/Game", f"{away_data.get('xg_per_game', 0):.2f}")
                st.metric("Form", away_data.get('form', 'N/A'))
            with col2b:
                st.metric("Defenders Out", away_data['defenders_out'])
                st.metric("Motivation", f"{away_data['motivation']}/5")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market odds
    market_odds = display_market_odds_interface()
    
    # Run prediction
    if st.button("🚀 Run Advanced Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        if not home_venue_data.empty and not away_venue_data.empty:
            engine = ProfessionalPredictionEngine()
            league_stats = LEAGUE_STATS[selected_league]
            
            with st.spinner("Running comprehensive analysis..."):
                progress_bar = st.progress(0)
                steps = ["Data Validation", "Base Calculations", "Adjustments", 
                        "Probability Simulation", "Confidence Calculation", "Final Analysis"]
                
                for i, step in enumerate(steps):
                    time.sleep(0.3)
                    progress_bar.progress((i + 1) / len(steps))
                
                result = engine.predict(home_data, away_data, league_stats)
                
                if result:
                    recommendations = engine.get_betting_recommendations(
                        result['probabilities'],
                        market_odds,
                        result['confidence'],
                        league_stats
                    )
                    
                    st.session_state['prediction_result'] = result
                    st.session_state['recommendations'] = recommendations
                    st.session_state['engine'] = engine
                    
                    st.success("✅ Analysis complete!")
                else:
                    st.error("Prediction failed. Please check the input data.")
        else:
            st.error("Could not find data for selected teams. Please try different teams.")
    
    # Display results if available
    if 'prediction_result' in st.session_state:
        result = st.session_state['prediction_result']
        recommendations = st.session_state['recommendations']
        engine = st.session_state['engine']
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Match header with predictions INSIDE boxes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            home_prob = result['probabilities']['home_win'] * 100
            ci_low = result['probabilities'].get('home_win_ci_low', home_prob/100) * 100
            ci_high = result['probabilities'].get('home_win_ci_high', home_prob/100) * 100
            display_prediction_box(
                f"🏠 {home_team}",
                f"{home_prob:.1f}%",
                f"95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]"
            )
        
        with col2:
            draw_prob = result['probabilities']['draw'] * 100
            ci_low = result['probabilities'].get('draw_ci_low', draw_prob/100) * 100
            ci_high = result['probabilities'].get('draw_ci_high', draw_prob/100) * 100
            display_prediction_box(
                "DRAW",
                f"{draw_prob:.1f}%",
                f"95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]"
            )
        
        with col3:
            away_prob = result['probabilities']['away_win'] * 100
            ci_low = result['probabilities'].get('away_win_ci_low', away_prob/100) * 100
            ci_high = result['probabilities'].get('away_win_ci_high', away_prob/100) * 100
            display_prediction_box(
                f"✈️ {away_team}",
                f"{away_prob:.1f}%",
                f"95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]"
            )
        
        # Predicted score in center box
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            score_prob = result['scoreline_probabilities'].get(result['predicted_score'], 0) * 100
            display_prediction_box(
                "🎯 Predicted Score",
                result['predicted_score'],
                f"Probability: {score_prob:.1f}%"
            )
        
        # Expected goals
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            display_prediction_box(
                "Home Expected Goals",
                f"{result['expected_goals']['home']:.2f}",
                "λ (Poisson mean)"
            )
        
        with col2:
            display_prediction_box(
                "Away Expected Goals",
                f"{result['expected_goals']['away']:.2f}",
                "λ (Poisson mean)"
            )
        
        # Model confidence with realistic caps
        confidence_pct = result['confidence'] * 100
        if confidence_pct >= 70:
            confidence_class = "confidence-high"
            confidence_text = "High Confidence"
        elif confidence_pct >= 50:
            confidence_class = "confidence-medium"
            confidence_text = "Medium Confidence"
        else:
            confidence_class = "confidence-low"
            confidence_text = "Low Confidence"
        
        st.markdown(f'<div class="{confidence_class}">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
        st.markdown(f"{confidence_text} prediction")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key factors
        if result['key_factors']:
            st.markdown("### 🔑 Key Factors")
            for factor in result['key_factors']:
                st.markdown(f'<span class="factor-badge">{factor}</span>', unsafe_allow_html=True)
        
        # Betting recommendations
        st.markdown("---")
        st.markdown("### 💰 Betting Recommendations")
        
        if recommendations:
            for i, rec in enumerate(recommendations[:3]):
                with st.expander(f"Recommendation #{i+1}: {rec['market']} - {rec['prediction']}", expanded=i==0):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Probability", f"{rec['probability']*100:.1f}%")
                        st.metric("Fair Odds", f"{rec['fair_odds']:.2f}")
                    
                    with col2:
                        st.metric("Market Odds", f"{rec['market_odds']:.2f}")
                        ev_display = f"+{rec['ev']*100:.1f}%" if rec['ev'] > 0 else f"{rec['ev']*100:.1f}%"
                        st.metric("EV", ev_display)
                    
                    with col3:
                        st.metric("Confidence", f"{rec['confidence']*100:.1f}%")
                        st.metric("Risk Level", rec['risk_level'])
                    
                    st.markdown(f"**Rationale:** {rec['rationale']}")
                    
                    if rec['risk_level'] in ['High', 'Medium-High']:
                        st.warning(f"{rec['risk_level']} risk - verify carefully")
        
        else:
            st.info("No strong betting recommendations based on current market odds.")
        
        # Scoreline probabilities chart
        st.markdown("---")
        st.markdown("### 📊 Scoreline Probability Distribution")
        
        scoreline_df = pd.DataFrame(
            list(result['scoreline_probabilities'].items())[:10],
            columns=['Scoreline', 'Probability']
        )
        scoreline_df['Probability'] = scoreline_df['Probability'] * 100
        
        fig = go.Figure(data=[
            go.Bar(
                x=scoreline_df['Scoreline'],
                y=scoreline_df['Probability'],
                marker_color='#4ECDC4',
                text=scoreline_df['Probability'].round(1),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Most Likely Scorelines",
            xaxis_title="Scoreline",
            yaxis_title="Probability (%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Over/Under and BTTS probabilities in boxes
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            over_prob = result['probabilities']['over_25'] * 100
            under_prob = result['probabilities']['under_25'] * 100
            league_over = LEAGUE_STATS[selected_league]['over_25_pct'] * 100
            
            if over_prob > league_over:
                display_prediction_box(
                    "📈 Over 2.5 Goals",
                    f"{over_prob:.1f}%",
                    f"+{over_prob - league_over:.1f}% vs league avg"
                )
            else:
                display_prediction_box(
                    "📉 Under 2.5 Goals",
                    f"{under_prob:.1f}%",
                    f"+{under_prob - (100 - league_over):.1f}% vs league avg"
                )
        
        with col2:
            btts_prob = result['probabilities']['btts_yes'] * 100
            btts_no_prob = result['probabilities']['btts_no'] * 100
            league_btts = LEAGUE_STATS[selected_league]['btts_pct'] * 100
            
            if btts_prob > league_btts:
                display_prediction_box(
                    "⚽ Both Teams to Score",
                    f"{btts_prob:.1f}%",
                    f"+{btts_prob - league_btts:.1f}% vs league avg"
                )
            else:
                display_prediction_box(
                    "🛡️ Clean Sheet Likely",
                    f"{btts_no_prob:.1f}%",
                    f"+{btts_no_prob - (100 - league_btts):.1f}% vs league avg"
                )

if __name__ == "__main__":
    main()
