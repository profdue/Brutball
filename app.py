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
    page_title="Advanced Football Prediction Engine",
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
    
    .data-warning {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff416c;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EMPIRICALLY CALIBRATED CONSTANTS
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
    'MIN_AWAY_LAMBDA': 0.4,
    'MIN_HOME_LAMBDA': 0.5,
    'MAX_WIN_PROBABILITY': 0.88,
    'MIN_DRAW_PROBABILITY': 0.08,
    'MIN_AWAY_WIN_PROBABILITY': 0.03,
    'DEFENSE_XGDIFF_ADJUSTMENT': 0.03,  # 3% per xGDiff point
    'FINISHING_EFFICIENCY_IMPACT': 0.1,  # 10% impact of finishing efficiency
}

# ============================================================================
# LEAGUE-SPECIFIC STATISTICS
# ============================================================================

LEAGUE_STATS = {
    'Premier League': {
        'goals_per_match': 2.83,
        'home_goals_per_match': 1.52,
        'away_goals_per_match': 1.31,
        'home_win_pct': 0.46,
        'draw_pct': 0.26,
        'away_win_pct': 0.28,
        'over_25_pct': 0.53,
        'btts_pct': 0.52,
        'shots_allowed_avg': 12.7,
        'avg_goals_conceded': 1.42,
        'scoring_factor': 1.0,
        'variance': 1.05,
        'source': '2022-23 Season Stats'
    },
    'La Liga': {
        'goals_per_match': 2.51,
        'home_goals_per_match': 1.42,
        'away_goals_per_match': 1.09,
        'home_win_pct': 0.45,
        'draw_pct': 0.27,
        'away_win_pct': 0.28,
        'over_25_pct': 0.45,
        'btts_pct': 0.49,
        'shots_allowed_avg': 12.3,
        'avg_goals_conceded': 1.26,
        'scoring_factor': 0.89,
        'variance': 0.95,
        'source': '2022-23 Season Stats'
    },
}

# ============================================================================
# PROFESSIONAL PREDICTION ENGINE WITH COMPLETE LOGIC
# ============================================================================

class AdvancedPredictionEngine:
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
        self.league_stats = None
        
    def validate_input_data(self, home_data, away_data):
        """Validate input data has required fields."""
        required_fields = ['team', 'Matches_Played', 'xG_For', 'Goals', 
                          'Home_xGA', 'Away_xGA', 'Home_xGDiff_Def', 'Away_xGDiff_Def',
                          'defenders_out', 'form_last_5', 'motivation']
        
        for field in required_fields:
            if field not in home_data or field not in away_data:
                return False
        return True
    
    def calculate_weighted_form(self, form_string):
        """Calculate weighted form score from form string."""
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
        
        return sum(form_points) / sum(weights)
    
    def calculate_injury_impact(self, defenders_out):
        """Calculate defensive impact of injuries."""
        base_impact = defenders_out * CONSTANTS['DEFENDER_INJURY_IMPACT']
        if defenders_out > 3:
            base_impact *= 0.8  # Diminishing returns
        return 1 - min(base_impact, 0.40)
    
    def calculate_finishing_efficiency(self, goals_scored, xg_for):
        """Calculate how efficiently team converts chances."""
        if xg_for > 0:
            efficiency = goals_scored / xg_for
            # Normalize: 1.0 = average, >1.0 = clinical, <1.0 = wasteful
            return min(max(efficiency, 0.7), 1.3)  # Bound between 70-130%
        return 1.0
    
    def calculate_defensive_adjustment(self, xg_diff_def):
        """
        Adjust for defensive over/underperformance.
        Negative xGDiff = defense better than xGA suggests
        Positive xGDiff = defense worse than xGA suggests
        """
        # Each point of xGDiff represents 3% adjustment
        adjustment = 1.0 - (xg_diff_def * CONSTANTS['DEFENSE_XGDIFF_ADJUSTMENT'])
        return max(0.7, min(adjustment, 1.3))  # Bound between 70-130%
    
    def calculate_expected_goals(self, attacking_data, defending_data, is_home_team, league_stats):
        """
        Calculate expected goals using complete xG/xGA data.
        
        Args:
            attacking_data: Team that's attacking
            defending_data: Team that's defending
            is_home_team: Boolean, True if attacking team is home
            league_stats: League statistics
        """
        # Get venue-specific data
        if is_home_team:
            # Home team attacking, away team defending
            attack_xg_per_game = attacking_data['xG_For'] / attacking_data['Matches_Played']
            defense_xga_per_game = defending_data['Away_xGA'] / defending_data['Matches_Played']
            defense_xg_diff = defending_data['Away_xGDiff_Def']
            venue = "home"
        else:
            # Away team attacking, home team defending
            attack_xg_per_game = attacking_data['xG_For'] / attacking_data['Matches_Played']
            defense_xga_per_game = defending_data['Home_xGA'] / defending_data['Matches_Played']
            defense_xg_diff = defending_data['Home_xGDiff_Def']
            venue = "away"
        
        # 1. Base attacking strength (xG per game)
        base_attack = attack_xg_per_game
        
        # 2. Adjust for finishing efficiency
        finishing_efficiency = self.calculate_finishing_efficiency(
            attacking_data['Goals'], 
            attacking_data['xG_For']
        )
        base_attack *= finishing_efficiency
        
        # 3. Adjust for defensive quality
        # If defense allows more xGA than league average, attack gets boost
        league_avg_conceded = league_stats['avg_goals_conceded']
        defense_factor = league_avg_conceded / defense_xga_per_game if defense_xga_per_game > 0 else 1.0
        
        # 4. Adjust for defensive over/underperformance (xGDiff)
        defense_adjustment = self.calculate_defensive_adjustment(defense_xg_diff)
        
        # 5. Calculate expected goals
        expected_goals = base_attack / defense_factor * defense_adjustment
        
        # Apply venue factor (home/away)
        if is_home_team:
            expected_goals *= CONSTANTS['HOME_ADVANTAGE_BASE']
        else:
            expected_goals *= (2 - CONSTANTS['HOME_ADVANTAGE_BASE'])  # Complementary
        
        # Apply form adjustment
        form_score = self.calculate_weighted_form(attacking_data.get('form', ''))
        form_factor = 1.0 + (form_score - 0.5) * 0.1
        expected_goals *= form_factor
        
        # Apply motivation adjustment
        motivation = attacking_data['motivation'] / 5.0
        expected_goals *= (1 + (motivation - 0.5) * CONSTANTS['MOTIVATION_SCALING'])
        
        # Apply injury impact (opponent's injuries help scoring)
        opponent_defense_strength = self.calculate_injury_impact(defending_data['defenders_out'])
        expected_goals *= opponent_defense_strength
        
        # Apply style matchup adjustments
        if 'set_piece_pct' in attacking_data and 'set_piece_pct' in defending_data:
            set_piece_diff = attacking_data['set_piece_pct'] - defending_data['set_piece_pct']
            if set_piece_diff > 0.1:
                expected_goals += CONSTANTS['SET_PIECE_ADVANTAGE']
        
        if 'counter_attack_pct' in attacking_data and attacking_data['counter_attack_pct'] > 0.1:
            expected_goals += CONSTANTS['COUNTER_ATTACK_BOOST']
        
        # Ensure realistic bounds
        if is_home_team:
            expected_goals = max(CONSTANTS['MIN_HOME_LAMBDA'], min(expected_goals, 5.0))
        else:
            expected_goals = max(CONSTANTS['MIN_AWAY_LAMBDA'], min(expected_goals, 4.0))
        
        return expected_goals
    
    def apply_football_variance_adjustment(self, probabilities, home_lambda, away_lambda):
        """Apply realistic variance adjustments for football."""
        adjusted = probabilities.copy()
        
        # Cap maximum win probability
        max_win = CONSTANTS['MAX_WIN_PROBABILITY']
        
        if adjusted['home_win'] > max_win:
            excess = adjusted['home_win'] - max_win
            adjusted['home_win'] = max_win
            adjusted['draw'] += excess * 0.7
            adjusted['away_win'] += excess * 0.3
        
        if adjusted['away_win'] > max_win:
            excess = adjusted['away_win'] - max_win
            adjusted['away_win'] = max_win
            adjusted['draw'] += excess * 0.7
            adjusted['home_win'] += excess * 0.3
        
        # Minimum probabilities
        adjusted['draw'] = max(adjusted['draw'], CONSTANTS['MIN_DRAW_PROBABILITY'])
        adjusted['away_win'] = max(adjusted['away_win'], CONSTANTS['MIN_AWAY_WIN_PROBABILITY'])
        
        # For extreme mismatches, ensure some chance for underdog
        if home_lambda > away_lambda * 3:
            min_away = 0.02
            if adjusted['away_win'] < min_away:
                needed = min_away - adjusted['away_win']
                adjusted['away_win'] += needed
                adjusted['home_win'] -= needed * 0.8
                adjusted['draw'] -= needed * 0.2
        
        # Normalize
        total = sum(adjusted.values())
        for key in adjusted:
            adjusted[key] /= total
        
        return adjusted
    
    def calculate_probability_distributions(self, home_lambda, away_lambda):
        """Calculate probability distributions using Poisson."""
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
        
        probabilities = {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations,
            'over_25': over_25 / simulations,
            'under_25': under_25 / simulations,
            'btts_yes': btts_yes / simulations,
            'btts_no': 1 - (btts_yes / simulations)
        }
        
        # Apply variance adjustment
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
        
        # Normalize scoreline probabilities
        total_score_prob = sum(scoreline_probs.values())
        if total_score_prob > 0:
            scoreline_probs = {k: v/total_score_prob for k, v in scoreline_probs.items()}
        
        if scoreline_probs:
            predicted_score = max(scoreline_probs.items(), key=lambda x: x[1])[0]
        else:
            predicted_score = "1-1"
            scoreline_probs = {"1-1": 0.15, "0-0": 0.1, "1-0": 0.1, "0-1": 0.1, "2-1": 0.08}
        
        return ci_probabilities, scoreline_probs, predicted_score
    
    def calculate_model_confidence(self, home_lambda, away_lambda, probabilities):
        """Calculate model confidence with realistic caps."""
        confidence = 0.5
        
        # Goal difference indicates match clarity
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.5:
            confidence += 0.25
        elif goal_diff > 1.0:
            confidence += 0.15
        elif goal_diff > 0.5:
            confidence += 0.05
        
        # Probability clarity
        max_prob = max(probabilities['home_win'], probabilities['away_win'], probabilities['draw'])
        if max_prob > 0.7:
            confidence += 0.2
        elif max_prob > 0.6:
            confidence += 0.1
        
        # Realistic caps
        if max_prob > 0.75:
            confidence = min(confidence, 0.82)
        elif max_prob > 0.65:
            confidence = min(confidence, 0.75)
        elif max_prob > 0.55:
            confidence = min(confidence, 0.68)
        else:
            confidence = min(confidence, 0.60)
        
        return max(0.35, min(confidence, 0.82))
    
    def calculate_expected_value(self, model_prob, market_odds):
        """Calculate Expected Value."""
        if model_prob <= 0 or market_odds <= 1:
            return -1, 0
        
        fair_odds = 1 / model_prob
        ev_simple = (market_odds / fair_odds) - 1
        ev_adjusted = ev_simple * min(1, model_prob * 1.5)
        
        return ev_simple, ev_adjusted
    
    def get_betting_recommendations(self, probabilities, market_odds, confidence, league_stats):
        """Generate betting recommendations."""
        recommendations = []
        MIN_EV = 0.05
        MIN_CONFIDENCE = 0.55
        
        # Match result markets
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
                    if ev_adjusted > 0.25:
                        risk_level = 'High'
                        suffix = "⚠️ Very high EV"
                    elif ev_adjusted > 0.15:
                        risk_level = 'Medium-High'
                        suffix = "Good value"
                    elif ev_adjusted > 0.08:
                        risk_level = 'Medium'
                        suffix = "Moderate value"
                    else:
                        risk_level = 'Low'
                        suffix = "Small edge"
                    
                    league_avg = league_stats.get('home_win_pct', 0.46) if 'home' in market_name.lower() else \
                                league_stats.get('draw_pct', 0.26) if 'draw' in market_name.lower() else \
                                league_stats.get('away_win_pct', 0.28)
                    
                    recommendations.append({
                        'market': 'Match Result',
                        'prediction': market_name,
                        'probability': prob,
                        'market_odds': odds,
                        'fair_odds': 1/prob,
                        'ev': ev_adjusted,
                        'confidence': confidence,
                        'risk_level': risk_level,
                        'rationale': f"Model: {prob*100:.0f}% vs Market: {1/odds*100:.0f}% (League avg: {league_avg*100:.0f}%). {suffix}"
                    })
        
        # Over/Under 2.5
        over_prob = probabilities.get('over_25', 0)
        over_odds = market_odds.get('over_25', 1.85)
        league_over = league_stats.get('over_25_pct', 0.53)
        
        if over_prob > league_over + 0.1:
            ev_simple, ev_adjusted = self.calculate_expected_value(over_prob, over_odds)
            if ev_adjusted >= MIN_EV:
                recommendations.append({
                    'market': 'Total Goals',
                    'prediction': 'Over 2.5',
                    'probability': over_prob,
                    'market_odds': over_odds,
                    'fair_odds': 1/over_prob,
                    'ev': ev_adjusted,
                    'confidence': min(confidence, abs(over_prob - league_over) * 3),
                    'risk_level': 'Medium',
                    'rationale': f"High-scoring pattern ({over_prob*100:.0f}% vs league {league_over*100:.0f}%)"
                })
        
        # BTTS
        btts_prob = probabilities.get('btts_yes', 0)
        btts_odds = market_odds.get('btts_yes', 1.75)
        league_btts = league_stats.get('btts_pct', 0.52)
        
        if abs(btts_prob - league_btts) > 0.15:
            ev_simple, ev_adjusted = self.calculate_expected_value(btts_prob, btts_odds)
            if ev_adjusted >= MIN_EV:
                prediction = 'BTTS Yes' if btts_prob > league_btts else 'BTTS No'
                recommendations.append({
                    'market': 'Both Teams to Score',
                    'prediction': prediction,
                    'probability': btts_prob if prediction == 'BTTS Yes' else 1-btts_prob,
                    'market_odds': btts_odds if prediction == 'BTTS Yes' else 1/(1-1/btts_odds),
                    'fair_odds': 1/(btts_prob if prediction == 'BTTS Yes' else 1-btts_prob),
                    'ev': ev_adjusted,
                    'confidence': min(confidence, abs(btts_prob - league_btts) * 3),
                    'risk_level': 'Medium',
                    'rationale': f"Significant deviation ({btts_prob*100:.0f}% vs league {league_btts*100:.0f}%)"
                })
        
        recommendations.sort(key=lambda x: x['ev'], reverse=True)
        return recommendations
    
    def predict(self, home_data, away_data, league_stats):
        """Main prediction function with complete logic."""
        self.reset_calculations()
        self.league_stats = league_stats
        
        if not self.validate_input_data(home_data, away_data):
            return None
        
        # Track key factors
        self.key_factors = []
        
        # Calculate home team expected goals (attacking vs away defense)
        home_lambda = self.calculate_expected_goals(
            attacking_data=home_data,
            defending_data=away_data,
            is_home_team=True,
            league_stats=league_stats
        )
        
        # Calculate away team expected goals (attacking vs home defense)
        away_lambda = self.calculate_expected_goals(
            attacking_data=away_data,
            defending_data=home_data,
            is_home_team=False,
            league_stats=league_stats
        )
        
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # Add key factors
        self.key_factors.append(f"Home advantage: {CONSTANTS['HOME_ADVANTAGE_BASE']:.2f}x")
        
        home_finishing = self.calculate_finishing_efficiency(home_data['Goals'], home_data['xG_For'])
        away_finishing = self.calculate_finishing_efficiency(away_data['Goals'], away_data['xG_For'])
        
        if home_finishing > 1.1:
            self.key_factors.append(f"Home clinical finishing ({home_finishing:.2f}x)")
        elif home_finishing < 0.9:
            self.key_factors.append(f"Home wasteful finishing ({home_finishing:.2f}x)")
        
        if away_finishing > 1.1:
            self.key_factors.append(f"Away clinical finishing ({away_finishing:.2f}x)")
        elif away_finishing < 0.9:
            self.key_factors.append(f"Away wasteful finishing ({away_finishing:.2f}x)")
        
        # Check defensive over/underperformance
        home_defense_adj = self.calculate_defensive_adjustment(home_data['Home_xGDiff_Def'])
        away_defense_adj = self.calculate_defensive_adjustment(away_data['Away_xGDiff_Def'])
        
        if home_defense_adj < 0.95:
            self.key_factors.append(f"Home defense overperforming ({home_data['Home_xGDiff_Def']:.1f} xGDiff)")
        if away_defense_adj < 0.95:
            self.key_factors.append(f"Away defense overperforming ({away_data['Away_xGDiff_Def']:.1f} xGDiff)")
        
        if home_data['defenders_out'] > 0:
            self.key_factors.append(f"Home injuries: {home_data['defenders_out']} defenders out")
        if away_data['defenders_out'] > 0:
            self.key_factors.append(f"Away injuries: {away_data['defenders_out']} defenders out")
        
        # Calculate probabilities
        probabilities, scoreline_probs, predicted_score = \
            self.calculate_probability_distributions(home_lambda, away_lambda)
        
        self.probabilities = probabilities
        self.scoreline_probabilities = scoreline_probs
        self.predicted_score = predicted_score
        
        # Calculate confidence
        self.confidence = self.calculate_model_confidence(home_lambda, away_lambda, probabilities)
        
        return {
            'probabilities': probabilities,
            'scoreline_probabilities': scoreline_probs,
            'predicted_score': predicted_score,
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'confidence': self.confidence,
            'key_factors': self.key_factors,
            'data_quality': 'Complete xG/xGA data available'
        }

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def display_prediction_box(title, value, subtitle=""):
    """Display prediction in styled box."""
    st.markdown(f"""
    <div class="prediction-box">
        <div class="prediction-label">{title}</div>
        <div class="prediction-value">{value}</div>
        <div class="prediction-label">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_market_odds_interface():
    """Display market odds input."""
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

def validate_data_completeness(df):
    """Check if data has required columns."""
    required = ['Home_xGA', 'Away_xGA', 'Home_xGDiff_Def', 'Away_xGDiff_Def', 'xG_For']
    missing = [col for col in required if col not in df.columns]
    return len(missing) == 0, missing

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Advanced Football Prediction Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Complete xG/xGA Logic • Universal Application • Professional</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        
        available_leagues = ['Premier League', 'La Liga']
        selected_league = st.selectbox("Choose League:", available_leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Load Data")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data..."):
                try:
                    github_base_url = "https://raw.githubusercontent.com/profdue/Brutball/main/leagues/"
                    league_files = {
                        'Premier League': 'epl_complete.csv',
                        'La Liga': 'la_liga_complete.csv',
                    }
                    
                    # Try complete data first, fall back to basic
                    url = f"{github_base_url}{league_files.get(selected_league, 'la_liga_complete.csv')}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
                        is_complete, missing = validate_data_completeness(df)
                        
                        if is_complete:
                            st.session_state['league_data'] = df
                            st.session_state['selected_league'] = selected_league
                            st.session_state['data_quality'] = 'Complete'
                            st.success(f"✅ Loaded complete {selected_league} data ({len(df)} records)")
                        else:
                            st.warning(f"⚠️ Missing columns: {', '.join(missing)}")
                            st.session_state['league_data'] = df
                            st.session_state['selected_league'] = selected_league
                            st.session_state['data_quality'] = 'Basic'
                    else:
                        st.error(f"Failed to load data: HTTP {response.status_code}")
                        
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
        1. **Load Data**: Complete team statistics with xG/xGA
        2. **Select Match**: Choose home and away teams
        3. **Input Odds**: Current market odds for comparison
        4. **Run Analysis**: Advanced model with complete logic
        5. **Review**: Professional predictions and recommendations
        """)
    
    # Main content
    if 'league_data' not in st.session_state:
        st.info("👈 Please load league data from the sidebar to begin.")
        return
    
    df = st.session_state['league_data']
    selected_league = st.session_state['selected_league']
    data_quality = st.session_state.get('data_quality', 'Basic')
    
    # Data quality warning
    if data_quality == 'Basic':
        st.markdown("""
        <div class="data-warning">
        ⚠️ <strong>Basic Data Loaded</strong>: Some defensive metrics (xGA, xGDiff) may be missing. 
        For best results, ensure complete xG/xGA dataset is available.
        </div>
        """, unsafe_allow_html=True)
    
    # Match setup
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 🏟️ Match Setup")
    
    available_teams = sorted(df['team'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", available_teams)
        home_data = df[(df['team'] == home_team) & (df['Venue'] == 'home')]
        if not home_data.empty:
            home_row = home_data.iloc[0]
            
            st.markdown(f"**{home_team} Home Stats:**")
            col1a, col2a = st.columns(2)
            with col1a:
                if 'xG_For' in home_row:
                    xg_per_game = home_row['xG_For'] / home_row['Matches_Played']
                    st.metric("xG/Game", f"{xg_per_game:.2f}")
                st.metric("Form", home_row.get('form', 'N/A'))
            with col2a:
                st.metric("Defenders Out", home_row['defenders_out'])
                st.metric("Motivation", f"{home_row['motivation']}/5")
    
    with col2:
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options)
        away_data = df[(df['team'] == away_team) & (df['Venue'] == 'away')]
        if not away_data.empty:
            away_row = away_data.iloc[0]
            
            st.markdown(f"**{away_team} Away Stats:**")
            col1b, col2b = st.columns(2)
            with col1b:
                if 'xG_For' in away_row:
                    xg_per_game = away_row['xG_For'] / away_row['Matches_Played']
                    st.metric("xG/Game", f"{xg_per_game:.2f}")
                st.metric("Form", away_row.get('form', 'N/A'))
            with col2b:
                st.metric("Defenders Out", away_row['defenders_out'])
                st.metric("Motivation", f"{away_row['motivation']}/5")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market odds
    market_odds = display_market_odds_interface()
    
    # Run prediction
    if st.button("🚀 Run Advanced Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        if home_data.empty or away_data.empty:
            st.error("Could not find data for selected teams.")
            return
        
        engine = AdvancedPredictionEngine()
        league_stats = LEAGUE_STATS[selected_league]
        
        with st.spinner("Running complete analysis with xG/xGA logic..."):
            progress_bar = st.progress(0)
            steps = ["Data Validation", "Attack/Defense Calculation", "Style Matchup", 
                    "Probability Simulation", "Variance Adjustment", "Final Analysis"]
            
            for i, step in enumerate(steps):
                time.sleep(0.3)
                progress_bar.progress((i + 1) / len(steps))
            
            result = engine.predict(home_row.to_dict(), away_row.to_dict(), league_stats)
            
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
                
                st.success("✅ Advanced analysis complete!")
            else:
                st.error("Prediction failed. Please check data completeness.")
    
    # Display results if available
    if 'prediction_result' in st.session_state:
        result = st.session_state['prediction_result']
        recommendations = st.session_state['recommendations']
        engine = st.session_state['engine']
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Match probabilities
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
        
        # Predicted score
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
                f"λ (Poisson mean)"
            )
        
        with col2:
            display_prediction_box(
                "Away Expected Goals",
                f"{result['expected_goals']['away']:.2f}",
                f"λ (Poisson mean)"
            )
        
        # Model confidence
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
        st.markdown(f"{confidence_text} prediction • {result.get('data_quality', 'Basic data')}")
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
        
        # Over/Under and BTTS probabilities
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
