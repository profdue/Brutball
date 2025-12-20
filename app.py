import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import math
import io
import requests
from scipy import stats
import json

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
    
    .data-warning {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff416c;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .ev-positive {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 10px;
        padding: 10px;
        color: white;
        font-weight: bold;
    }
    
    .ev-negative {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        border-radius: 10px;
        padding: 10px;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LEAGUE-SPECIFIC PARAMETERS (From your logic)
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'league_avg_goals_conceded': 1.26,
        'league_avg_shots_allowed': 12.3,
        'home_advantage': 1.12,
        'variance_factor': 0.95,
        'source': '2023-24 Season'
    },
    'PREMIER LEAGUE': {
        'league_avg_goals_conceded': 1.42,
        'league_avg_shots_allowed': 12.7,
        'home_advantage': 1.15,
        'variance_factor': 1.05,
        'source': '2023-24 Season'
    }
}

# ============================================================================
# CORE CONSTANTS (From your logic)
# ============================================================================

CONSTANTS = {
    'MIN_HOME_LAMBDA': 0.5,
    'MIN_AWAY_LAMBDA': 0.4,
    'MAX_HOME_LAMBDA': 4.0,
    'MAX_AWAY_LAMBDA': 3.5,
    'HOME_ADVANTAGE_MULTIPLIER': 1.12,
    'AWAY_PENALTY_MULTIPLIER': 0.88,
    'SET_PIECE_THRESHOLD': 0.15,
    'SET_PIECE_BOOST': 0.10,
    'COUNTER_ATTACK_THRESHOLD': 0.15,
    'COUNTER_ATTACK_BOOST': 0.08,
    'OPEN_PLAY_THRESHOLD': 0.70,
    'OPEN_PLAY_BOOST': 0.05,
    'DEFENDER_INJURY_IMPACT': 0.08,
    'MAX_INJURY_REDUCTION': 0.40,
    'FORM_CONTRIBUTION': 0.30,
    'MOTIVATION_ADJUSTMENT': 0.02,
    'XGDIFF_DEF_ADJUSTMENT': 0.10,  # 1/(1 + abs(xGDiff)/10)
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 6,
    'MIN_CONFIDENCE': 35,
    'MAX_CONFIDENCE': 85,
    'MIN_EV_FOR_RECOMMENDATION': 0.05,
    'MIN_CONFIDENCE_FOR_RECOMMENDATION': 55
}

# ============================================================================
# PROFESSIONAL PREDICTION ENGINE (Strictly following your logic)
# ============================================================================

class FootballPredictionEngine:
    def __init__(self, league_params):
        self.league_params = league_params
        self.reset()
        
    def reset(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.scoreline_probs = {}
        self.confidence = 0
        self.key_factors = []
        self.recommendations = []
        
    def validate_data(self, home_data, away_data):
        """Validate required data fields exist."""
        required_fields = [
            'team', 'venue', 'matches_played', 'xg_for', 'goals',
            'home_xga', 'away_xga', 'goals_conceded', 'home_xgdiff_def', 'away_xgdiff_def',
            'defenders_out', 'form_last_5', 'motivation', 'set_piece_pct',
            'counter_attack_pct', 'open_play_pct', 'goals_scored_last_5',
            'goals_conceded_last_5', 'shots_allowed_pg'
        ]
        
        for field in required_fields:
            if field not in home_data or field not in away_data:
                raise ValueError(f"Missing required field: {field}")
        
        return True
    
    def calculate_form_adjustment(self, form_last_5):
        """Convert Form_Last_5 to 0-1 scale: (Form_Last_5 ÷ 15)."""
        if pd.isna(form_last_5):
            return 0.5
        return max(0, min(1, form_last_5 / 15))
    
    def calculate_finishing_efficiency(self, goals, xg_for):
        """Goals ÷ xG_For (cap 0.7-1.3 range)."""
        if xg_for <= 0:
            return 1.0
        efficiency = goals / xg_for
        return max(0.7, min(1.3, efficiency))
    
    def calculate_motivation_boost(self, motivation):
        """1 + (Motivation - 3) × 0.02."""
        if pd.isna(motivation):
            return 1.0
        return 1 + (motivation - 3) * CONSTANTS['MOTIVATION_ADJUSTMENT']
    
    def calculate_injury_impact(self, defenders_out):
        """1 - (Defenders_Out × 0.08) (max 40% reduction)."""
        reduction = defenders_out * CONSTANTS['DEFENDER_INJURY_IMPACT']
        reduction = min(reduction, CONSTANTS['MAX_INJURY_REDUCTION'])
        return 1 - reduction
    
    def calculate_defensive_overperformance(self, xgdiff_def):
        """Adjustment: 1 ÷ (1 + abs(xGDiff_Def) ÷ 10)."""
        if pd.isna(xgdiff_def):
            return 1.0
        return 1 / (1 + abs(xgdiff_def) / 10)
    
    def calculate_home_expected_goals(self, home_data, away_data):
        """Calculate λ_home following your logic exactly."""
        
        # A. HOME TEAM ATTACK STRENGTH
        # Base Attack: xG_For_home ÷ Matches_Played_home
        base_attack = home_data['xg_for'] / home_data['matches_played']
        
        # Finishing Efficiency: Goals_home ÷ xG_For_home (cap 0.7-1.3 range)
        finishing = self.calculate_finishing_efficiency(home_data['goals'], home_data['xg_for'])
        
        # Form Adjustment: Convert Form_Last_5_home to 0-1 scale: (Form_Last_5_home ÷ 15)
        form_score = self.calculate_form_adjustment(home_data['form_last_5'])
        form_adjustment = 0.7 + CONSTANTS['FORM_CONTRIBUTION'] * form_score
        
        # Motivation Boost: 1 + (Motivation_home - 3) × 0.02
        motivation_boost = self.calculate_motivation_boost(home_data['motivation'])
        
        # Adjusted Attack: Base × Finishing × (0.7 + 0.3×Form) × Motivation
        adjusted_attack = base_attack * finishing * form_adjustment * motivation_boost
        
        # B. AWAY TEAM DEFENSE QUALITY
        # Base Defense: xGA_away ÷ Matches_Played_away
        base_defense = away_data['away_xga'] / away_data['matches_played']
        
        # Defensive Overperformance: 1 ÷ (1 + abs(xGDiff_Def_away) ÷ 10)
        overperformance = self.calculate_defensive_overperformance(away_data['away_xgdiff_def'])
        
        # Injury Impact: 1 - (Defenders_Out_away × 0.08) (max 40% reduction)
        injury_impact = self.calculate_injury_impact(away_data['defenders_out'])
        
        # Recent Defense Form: Goals_Conceded_Last_5_away ÷ 5 (lower is better)
        recent_defense = away_data['goals_conceded_last_5'] / 5
        
        # Effective Defense: Base × Overperformance × Injury × (Recent/League_Avg)
        league_avg = self.league_params['league_avg_goals_conceded']
        effective_defense = base_defense * overperformance * injury_impact * (recent_defense / league_avg)
        
        # C. HOME λ CALCULATION
        # Defense Factor: League_Avg_Goals_Conceded ÷ Effective_Defense
        defense_factor = league_avg / effective_defense if effective_defense > 0 else 1.0
        
        # Home λ: Adjusted_Attack ÷ Defense_Factor
        home_lambda = adjusted_attack / defense_factor if defense_factor > 0 else adjusted_attack
        
        # Apply Minimum: λ_home ≥ 0.5
        return max(CONSTANTS['MIN_HOME_LAMBDA'], home_lambda)
    
    def calculate_away_expected_goals(self, away_data, home_data):
        """Calculate λ_away following your logic exactly."""
        
        # A. AWAY TEAM ATTACK STRENGTH
        # Base Attack: xG_For_away ÷ Matches_Played_away
        base_attack = away_data['xg_for'] / away_data['matches_played']
        
        # Finishing Efficiency: Goals_away ÷ xG_For_away
        finishing = self.calculate_finishing_efficiency(away_data['goals'], away_data['xg_for'])
        
        # Form Adjustment: Same as home team
        form_score = self.calculate_form_adjustment(away_data['form_last_5'])
        form_adjustment = 0.7 + CONSTANTS['FORM_CONTRIBUTION'] * form_score
        
        # Motivation Boost: Same as home team
        motivation_boost = self.calculate_motivation_boost(away_data['motivation'])
        
        # Adjusted Attack: Calculated same as home team
        adjusted_attack = base_attack * finishing * form_adjustment * motivation_boost
        
        # B. HOME TEAM DEFENSE QUALITY
        # Base Defense: xGA_home ÷ Matches_Played_home
        base_defense = home_data['home_xga'] / home_data['matches_played']
        
        # Defensive Overperformance: Using xGDiff_Def_home
        overperformance = self.calculate_defensive_overperformance(home_data['home_xgdiff_def'])
        
        # Injury Impact: Using Defenders_Out_home
        injury_impact = self.calculate_injury_impact(home_data['defenders_out'])
        
        # Recent Defense Form: Using Goals_Conceded_Last_5_home
        recent_defense = home_data['goals_conceded_last_5'] / 5
        
        # Effective Defense: Calculated same as away defense
        league_avg = self.league_params['league_avg_goals_conceded']
        effective_defense = base_defense * overperformance * injury_impact * (recent_defense / league_avg)
        
        # C. AWAY λ CALCULATION
        # Defense Factor: League_Avg_Goals_Conceded ÷ Effective_Defense
        defense_factor = league_avg / effective_defense if effective_defense > 0 else 1.0
        
        # Away λ: Adjusted_Attack ÷ Defense_Factor
        away_lambda = adjusted_attack / defense_factor if defense_factor > 0 else adjusted_attack
        
        # Apply Minimum: λ_away ≥ 0.4
        return max(CONSTANTS['MIN_AWAY_LAMBDA'], away_lambda)
    
    def apply_style_matchup_adjustments(self, home_data, away_data, home_lambda, away_lambda):
        """Apply style matchup adjustments."""
        adjustments = []
        
        # SET PIECE ADVANTAGE
        if 'set_piece_pct' in home_data and 'set_piece_pct' in away_data:
            set_piece_diff = home_data['set_piece_pct'] - away_data['set_piece_pct']
            if set_piece_diff > CONSTANTS['SET_PIECE_THRESHOLD']:
                home_lambda += CONSTANTS['SET_PIECE_BOOST']
                adjustments.append(f"Home set piece advantage: {set_piece_diff:.1%}")
            elif -set_piece_diff > CONSTANTS['SET_PIECE_THRESHOLD']:
                away_lambda += CONSTANTS['SET_PIECE_BOOST']
                adjustments.append(f"Away set piece advantage: {-set_piece_diff:.1%}")
        
        # COUNTER ATTACK POTENTIAL
        if ('counter_attack_pct' in away_data and 
            'shots_allowed_pg' in home_data):
            if (away_data['counter_attack_pct'] > CONSTANTS['COUNTER_ATTACK_THRESHOLD'] and 
                home_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']):
                away_lambda += CONSTANTS['COUNTER_ATTACK_BOOST']
                adjustments.append("Away counter attack threat")
        
        # OPEN PLAY DOMINANCE
        if ('open_play_pct' in home_data and 
            home_data['open_play_pct'] > CONSTANTS['OPEN_PLAY_THRESHOLD']):
            home_lambda += CONSTANTS['OPEN_PLAY_BOOST']
            adjustments.append("Home open play dominance")
        
        return home_lambda, away_lambda, adjustments
    
    def apply_final_adjustments(self, home_lambda, away_lambda):
        """Apply final adjustments and bounds."""
        # Home Advantage: Multiply λ_home by 1.12
        home_lambda *= CONSTANTS['HOME_ADVANTAGE_MULTIPLIER']
        
        # Away Penalty: Multiply λ_away by 0.88
        away_lambda *= CONSTANTS['AWAY_PENALTY_MULTIPLIER']
        
        # Variance Adjustment: For extreme mismatches, reduce favorite's λ by 5-10%
        if home_lambda > away_lambda * 2:
            reduction = 0.05 if home_lambda > 2.5 else 0.02
            home_lambda *= (1 - reduction)
        elif away_lambda > home_lambda * 2:
            reduction = 0.05 if away_lambda > 2.5 else 0.02
            away_lambda *= (1 - reduction)
        
        # Realistic Bounds
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], 
                         min(CONSTANTS['MAX_HOME_LAMBDA'], home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], 
                         min(CONSTANTS['MAX_AWAY_LAMBDA'], away_lambda))
        
        return home_lambda, away_lambda
    
    def calculate_poisson_probabilities(self, home_lambda, away_lambda):
        """Calculate probabilities using Poisson distribution."""
        simulations = CONSTANTS['POISSON_SIMULATIONS']
        
        np.random.seed(42)
        home_goals = np.random.poisson(home_lambda, simulations)
        away_goals = np.random.poisson(away_lambda, simulations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        total_goals = home_goals + away_goals
        over_25 = np.sum(total_goals > 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        
        probabilities = {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations,
            'over_25': over_25 / simulations,
            'btts_yes': btts_yes / simulations
        }
        
        # Validate probability sum
        total = probabilities['home_win'] + probabilities['draw'] + probabilities['away_win']
        if abs(total - 1.0) > 0.001:
            # Normalize
            scale = 1.0 / total
            probabilities['home_win'] *= scale
            probabilities['draw'] *= scale
            probabilities['away_win'] *= scale
        
        return probabilities
    
    def calculate_scoreline_probabilities(self, home_lambda, away_lambda):
        """Calculate scoreline probabilities."""
        max_goals = CONSTANTS['MAX_GOALS_CONSIDERED']
        scoreline_probs = {}
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = (stats.poisson.pmf(i, home_lambda) * 
                       stats.poisson.pmf(j, away_lambda))
                if prob > 0.001:  # Only store significant probabilities
                    scoreline_probs[f"{i}-{j}"] = prob
        
        # Normalize to 100%
        total = sum(scoreline_probs.values())
        if total > 0:
            scoreline_probs = {k: v/total for k, v in scoreline_probs.items()}
        
        # Identify most likely scoreline
        if scoreline_probs:
            most_likely = max(scoreline_probs.items(), key=lambda x: x[1])[0]
        else:
            most_likely = "0-0"
            scoreline_probs = {"0-0": 1.0}
        
        return scoreline_probs, most_likely
    
    def calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """Calculate prediction confidence."""
        base_confidence = 50
        
        # Goal Difference Boost
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.0:
            base_confidence += 20
        elif goal_diff > 0.5:
            base_confidence += 10
        
        # Form Clarity Boost
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        if form_diff > 5:
            base_confidence += 10
        
        # Injury Clarity Boost
        injury_diff = abs(home_data['defenders_out'] - away_data['defenders_out'])
        if injury_diff > 2:
            base_confidence += 10
        
        # Apply league variance factor
        base_confidence *= self.league_params['variance_factor']
        
        # Cap Confidence
        confidence = max(CONSTANTS['MIN_CONFIDENCE'], 
                        min(CONSTANTS['MAX_CONFIDENCE'], base_confidence))
        
        return confidence
    
    def identify_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate human-readable key factors."""
        factors = []
        
        # Home Advantage: Always included
        factors.append(f"Home advantage: {CONSTANTS['HOME_ADVANTAGE_MULTIPLIER']:.2f}x")
        
        # Form Advantage
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if abs(form_diff) > 2:
            if form_diff > 0:
                factors.append(f"Form advantage: Home +{form_diff} points")
            else:
                factors.append(f"Form advantage: Away +{abs(form_diff)} points")
        
        # Injury Impact
        if home_data['defenders_out'] > 1:
            factors.append(f"Home injuries: {home_data['defenders_out']} defenders out")
        if away_data['defenders_out'] > 1:
            factors.append(f"Away injuries: {away_data['defenders_out']} defenders out")
        
        # Defensive Overperformance
        if abs(home_data['home_xgdiff_def']) > 2.0:
            if home_data['home_xgdiff_def'] < 0:
                factors.append(f"Home defense overperforming xGA by {abs(home_data['home_xgdiff_def']):.1f}")
            else:
                factors.append(f"Home defense underperforming xGA by {home_data['home_xgdiff_def']:.1f}")
        
        if abs(away_data['away_xgdiff_def']) > 2.0:
            if away_data['away_xgdiff_def'] < 0:
                factors.append(f"Away defense overperforming xGA by {abs(away_data['away_xgdiff_def']):.1f}")
            else:
                factors.append(f"Away defense underperforming xGA by {away_data['away_xgdiff_def']:.1f}")
        
        # Motivation Difference
        if abs(home_data['motivation'] - away_data['motivation']) > 1:
            factors.append(f"Motivation difference: {home_data['motivation']} vs {away_data['motivation']}")
        
        # Style Advantages
        if 'set_piece_pct' in home_data and 'set_piece_pct' in away_data:
            set_piece_diff = home_data['set_piece_pct'] - away_data['set_piece_pct']
            if abs(set_piece_diff) > 0.1:
                factors.append(f"Set piece advantage: {set_piece_diff:.1%}")
        
        return factors
    
    def calculate_fair_odds(self, probabilities):
        """Calculate fair odds from probabilities."""
        return {
            'home': 1 / probabilities['home_win'] if probabilities['home_win'] > 0 else 1000,
            'draw': 1 / probabilities['draw'] if probabilities['draw'] > 0 else 1000,
            'away': 1 / probabilities['away_win'] if probabilities['away_win'] > 0 else 1000,
            'over_25': 1 / probabilities['over_25'] if probabilities['over_25'] > 0 else 1000,
            'btts_yes': 1 / probabilities['btts_yes'] if probabilities['btts_yes'] > 0 else 1000
        }
    
    def calculate_expected_value(self, market_odds, fair_odds):
        """Calculate Expected Value: (Market_Odds ÷ Fair_Odds) - 1."""
        if fair_odds <= 0:
            return -1
        return (market_odds / fair_odds) - 1
    
    def get_recommendations(self, probabilities, market_odds, confidence):
        """Generate betting recommendations."""
        recommendations = []
        
        fair_odds = self.calculate_fair_odds(probabilities)
        
        markets = [
            ('home_win', 'HOME', market_odds.get('home', fair_odds['home']), fair_odds['home']),
            ('draw', 'DRAW', market_odds.get('draw', fair_odds['draw']), fair_odds['draw']),
            ('away_win', 'AWAY', market_odds.get('away', fair_odds['away']), fair_odds['away']),
            ('over_25', 'Over 2.5', market_odds.get('over_25', fair_odds['over_25']), fair_odds['over_25']),
            ('btts_yes', 'BTTS Yes', market_odds.get('btts_yes', fair_odds['btts_yes']), fair_odds['btts_yes'])
        ]
        
        for prob_key, prediction, market_odd, fair_odd in markets:
            if prob_key in probabilities:
                ev = self.calculate_expected_value(market_odd, fair_odd)
                
                if (ev >= CONSTANTS['MIN_EV_FOR_RECOMMENDATION'] and 
                    confidence >= CONSTANTS['MIN_CONFIDENCE_FOR_RECOMMENDATION']):
                    
                    # Determine risk level
                    if ev > 0.25:
                        risk_level = "Very High Risk"
                    elif ev > 0.15:
                        risk_level = "High Risk"
                    elif ev > 0.08:
                        risk_level = "Medium Risk"
                    else:
                        risk_level = "Low Risk"
                    
                    recommendations.append({
                        'market': 'Match Result' if prob_key in ['home_win', 'draw', 'away_win'] else 
                                 'Total Goals' if prob_key == 'over_25' else 'Both Teams to Score',
                        'prediction': prediction,
                        'probability': probabilities[prob_key],
                        'fair_odds': round(fair_odd, 2),
                        'market_odds': round(market_odd, 2),
                        'ev': ev,
                        'risk_level': risk_level,
                        'rationale': f"Model probability: {probabilities[prob_key]:.1%} vs Market implied: {1/market_odd:.1%}"
                    })
        
        return recommendations
    
    def predict(self, home_data, away_data, market_odds):
        """Main prediction function following your logic exactly."""
        try:
            self.reset()
            
            # Validate data
            self.validate_data(home_data, away_data)
            
            # STEP 2: Calculate Home λ
            home_lambda = self.calculate_home_expected_goals(home_data, away_data)
            
            # STEP 3: Calculate Away λ
            away_lambda = self.calculate_away_expected_goals(away_data, home_data)
            
            # STEP 4: Style Matchup Adjustments
            home_lambda, away_lambda, style_adjustments = self.apply_style_matchup_adjustments(
                home_data, away_data, home_lambda, away_lambda
            )
            
            # STEP 5: Final Adjustments & Bounds
            home_lambda, away_lambda = self.apply_final_adjustments(home_lambda, away_lambda)
            
            self.home_lambda = home_lambda
            self.away_lambda = away_lambda
            
            # STEP 6: Probability Calculations
            # A. Poisson Distribution
            probabilities = self.calculate_poisson_probabilities(home_lambda, away_lambda)
            
            # B. Scoreline Probabilities
            scoreline_probs, most_likely = self.calculate_scoreline_probabilities(home_lambda, away_lambda)
            
            # C. Confidence Calculation
            confidence = self.calculate_confidence(home_lambda, away_lambda, home_data, away_data)
            
            # Identify Key Factors
            key_factors = self.identify_key_factors(home_data, away_data, home_lambda, away_lambda)
            key_factors.extend(style_adjustments)
            
            # Get Recommendations
            recommendations = self.get_recommendations(probabilities, market_odds, confidence)
            
            return {
                'success': True,
                'expected_goals': {
                    'home': round(home_lambda, 2),
                    'away': round(away_lambda, 2)
                },
                'probabilities': {k: round(v, 4) for k, v in probabilities.items()},
                'scorelines': {
                    'most_likely': most_likely,
                    'top_10': dict(sorted(scoreline_probs.items(), key=lambda x: x[1], reverse=True)[:10])
                },
                'confidence': round(confidence, 1),
                'key_factors': key_factors,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_league_data(league_name):
    """Load league data from GitHub."""
    github_urls = {
        'LA LIGA': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/la_liga.csv',
        'PREMIER LEAGUE': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
    }
    
    url = github_urls.get(league_name.upper())
    if not url:
        raise ValueError(f"League {league_name} not found")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Convert column names to lowercase for consistency
        df.columns = df.columns.str.lower()
        
        # Validate required columns
        required_cols = ['team', 'venue', 'matches_played', 'xg_for', 'goals',
                        'home_xga', 'away_xga', 'goals_conceded', 'home_xgdiff_def', 
                        'away_xgdiff_def', 'defenders_out', 'form_last_5', 'motivation']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to load data from GitHub: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing data: {str(e)}")

def prepare_team_data(df, team_name, venue):
    """Prepare team data for prediction."""
    team_data = df[(df['team'] == team_name) & (df['venue'] == venue.lower())]
    
    if team_data.empty:
        raise ValueError(f"No data found for {team_name} at {venue} venue")
    
    return team_data.iloc[0].to_dict()

# ============================================================================
# UI COMPONENTS
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
        home_odds = st.number_input("Home Win Odds", min_value=1.01, max_value=100.0, 
                                   value=2.50, step=0.01, format="%.2f", key="home_odds")
    
    with col2:
        draw_odds = st.number_input("Draw Odds", min_value=1.01, max_value=100.0,
                                   value=3.40, step=0.01, format="%.2f", key="draw_odds")
    
    with col3:
        away_odds = st.number_input("Away Win Odds", min_value=1.01, max_value=100.0,
                                   value=2.80, step=0.01, format="%.2f", key="away_odds")
    
    col4, col5 = st.columns(2)
    with col4:
        over_odds = st.number_input("Over 2.5 Goals Odds", min_value=1.01, max_value=100.0,
                                   value=1.85, step=0.01, format="%.2f", key="over_odds")
    
    with col5:
        btts_odds = st.number_input("BTTS Yes Odds", min_value=1.01, max_value=100.0,
                                   value=1.75, step=0.01, format="%.2f", key="btts_odds")
    
    return {
        'home': home_odds,
        'draw': draw_odds,
        'away': away_odds,
        'over_25': over_odds,
        'btts_yes': btts_odds
    }

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Football Prediction Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Strict Logic Compliance • xG/xGA Based • Professional</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        
        available_leagues = ['LA LIGA', 'PREMIER LEAGUE']
        selected_league = st.selectbox("Choose League:", available_leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Load Data")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data..."):
                try:
                    df = load_league_data(selected_league)
                    st.session_state['league_data'] = df
                    st.session_state['selected_league'] = selected_league
                    st.session_state['league_params'] = LEAGUE_PARAMS.get(selected_league.upper(), LEAGUE_PARAMS['LA LIGA'])
                    st.success(f"✅ Successfully loaded {len(df)} records")
                    
                    # Show data preview
                    st.markdown("#### Data Preview:")
                    st.dataframe(df.head(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
        
        if 'league_params' in st.session_state:
            st.markdown("---")
            st.markdown("### 📈 League Parameters")
            params = st.session_state['league_params']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Goals Conceded", f"{params['league_avg_goals_conceded']:.2f}")
                st.metric("Home Advantage", f"{params['home_advantage']:.2f}x")
            with col2:
                st.metric("Avg Shots Allowed", f"{params['league_avg_shots_allowed']:.2f}")
                st.metric("Variance Factor", f"{params['variance_factor']:.2f}")
            
            st.caption(f"Source: {params['source']}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Model Settings")
        
        show_advanced = st.checkbox("Show Advanced Settings", value=False)
        if show_advanced:
            CONSTANTS['POISSON_SIMULATIONS'] = st.slider("Simulation Count", 
                                                        1000, 100000, 20000, 1000)
            CONSTANTS['HOME_ADVANTAGE_MULTIPLIER'] = st.slider("Home Advantage", 
                                                              1.00, 1.25, 1.12, 0.01)
            CONSTANTS['AWAY_PENALTY_MULTIPLIER'] = st.slider("Away Penalty", 
                                                           0.50, 1.00, 0.88, 0.01)
        
        st.markdown("---")
        st.markdown("### 📊 How It Works")
        st.info("""
        1. **Load Data**: xG/xGA statistics from GitHub
        2. **Select Match**: Home and away teams
        3. **Input Odds**: Current market odds
        4. **Run Analysis**: Strict logic compliance
        5. **Review**: Professional predictions
        """)
    
    # Main content
    if 'league_data' not in st.session_state:
        st.info("👈 Please load league data from the sidebar to begin.")
        return
    
    df = st.session_state['league_data']
    selected_league = st.session_state['selected_league']
    league_params = st.session_state['league_params']
    
    # Match setup
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 🏟️ Match Setup")
    
    # Get unique teams
    available_teams = sorted(df['team'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", available_teams, key="home_team_select")
        
        # Show home team stats
        home_stats = df[(df['team'] == home_team) & (df['venue'] == 'home')]
        if not home_stats.empty:
            home_row = home_stats.iloc[0]
            st.markdown(f"**{home_team} Home Stats:**")
            
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("Matches", int(home_row['matches_played']))
                st.metric("xG/Game", f"{home_row['xg_for']/home_row['matches_played']:.2f}")
            with col2a:
                st.metric("Defenders Out", int(home_row['defenders_out']))
                st.metric("Form Last 5", f"{home_row['form_last_5']:.1f}")
    
    with col2:
        # Filter out home team from away options
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options, key="away_team_select")
        
        # Show away team stats
        away_stats = df[(df['team'] == away_team) & (df['venue'] == 'away')]
        if not away_stats.empty:
            away_row = away_stats.iloc[0]
            st.markdown(f"**{away_team} Away Stats:**")
            
            col1b, col2b = st.columns(2)
            with col1b:
                st.metric("Matches", int(away_row['matches_played']))
                st.metric("xG/Game", f"{away_row['xg_for']/away_row['matches_played']:.2f}")
            with col2b:
                st.metric("Defenders Out", int(away_row['defenders_out']))
                st.metric("Form Last 5", f"{away_row['form_last_5']:.1f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market odds
    market_odds = display_market_odds_interface()
    
    # Run prediction
    if st.button("🚀 Run Prediction Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        try:
            # Prepare team data
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            # Create engine and predict
            engine = FootballPredictionEngine(league_params)
            
            with st.spinner("Running complete analysis with strict logic compliance..."):
                progress_bar = st.progress(0)
                
                # Simulate steps
                steps = [
                    "Loading Data",
                    "Calculating Home Attack Strength",
                    "Calculating Away Defense Quality",
                    "Calculating Away Attack Strength",
                    "Applying Style Matchups",
                    "Running Poisson Simulations",
                    "Calculating Probabilities",
                    "Generating Recommendations"
                ]
                
                for i, step in enumerate(steps):
                    time.sleep(0.2)
                    progress_bar.progress((i + 1) / len(steps))
                
                # Run prediction
                result = engine.predict(home_data, away_data, market_odds)
                
                if result['success']:
                    st.session_state['prediction_result'] = result
                    st.session_state['prediction_engine'] = engine
                    st.success("✅ Analysis complete!")
                else:
                    st.error(f"❌ Prediction failed: {result['error']}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Display results if available
    if 'prediction_result' in st.session_state:
        result = st.session_state['prediction_result']
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Expected Goals
        st.markdown("### 📈 Expected Goals (λ)")
        col1, col2 = st.columns(2)
        
        with col1:
            display_prediction_box(
                f"🏠 {home_team} Expected Goals",
                f"{result['expected_goals']['home']:.2f}",
                "Home λ (Poisson mean)"
            )
        
        with col2:
            display_prediction_box(
                f"✈️ {away_team} Expected Goals",
                f"{result['expected_goals']['away']:.2f}",
                "Away λ (Poisson mean)"
            )
        
        # Match probabilities
        st.markdown("### 🎯 Match Probabilities")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            home_prob = result['probabilities']['home_win'] * 100
            display_prediction_box(
                f"🏠 {home_team} Win",
                f"{home_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['home_win']:.2f}"
            )
        
        with col2:
            draw_prob = result['probabilities']['draw'] * 100
            display_prediction_box(
                "Draw",
                f"{draw_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['draw']:.2f}"
            )
        
        with col3:
            away_prob = result['probabilities']['away_win'] * 100
            display_prediction_box(
                f"✈️ {away_team} Win",
                f"{away_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['away_win']:.2f}"
            )
        
        # Predicted scoreline
        st.markdown("### 🎯 Predicted Scoreline")
        score_prob = result['scorelines']['top_10'].get(result['scorelines']['most_likely'], 0) * 100
        display_prediction_box(
            "Most Likely Score",
            result['scorelines']['most_likely'],
            f"Probability: {score_prob:.1f}%"
        )
        
        # Additional probabilities
        st.markdown("### 📊 Additional Markets")
        col1, col2 = st.columns(2)
        
        with col1:
            over_prob = result['probabilities']['over_25'] * 100
            display_prediction_box(
                "Over 2.5 Goals",
                f"{over_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['over_25']:.2f}"
            )
        
        with col2:
            btts_prob = result['probabilities']['btts_yes'] * 100
            display_prediction_box(
                "Both Teams to Score",
                f"{btts_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['btts_yes']:.2f}"
            )
        
        # Confidence
        st.markdown("### 🤖 Model Confidence")
        confidence = result['confidence']
        if confidence >= 70:
            confidence_class = "success-box"
            confidence_text = "High Confidence"
        elif confidence >= 50:
            confidence_class = "prediction-box"
            confidence_text = "Medium Confidence"
        else:
            confidence_class = "data-warning"
            confidence_text = "Low Confidence"
        
        st.markdown(f'<div class="{confidence_class}">', unsafe_allow_html=True)
        st.markdown(f"### Confidence: **{confidence:.1f}%**")
        st.markdown(f"{confidence_text} • Based on {CONSTANTS['POISSON_SIMULATIONS']:,} simulations")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key factors
        if result['key_factors']:
            st.markdown("### 🔑 Key Factors")
            for factor in result['key_factors']:
                st.markdown(f'<span class="factor-badge">{factor}</span>', unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("---")
        st.markdown("### 💰 Betting Recommendations")
        
        if result['recommendations']:
            for rec in result['recommendations']:
                ev_class = "ev-positive" if rec['ev'] > 0 else "ev-negative"
                ev_display = f"+{rec['ev']:.1%}" if rec['ev'] > 0 else f"{rec['ev']:.1%}"
                
                with st.expander(f"{rec['market']}: {rec['prediction']} (EV: {ev_display})", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Probability", f"{rec['probability']:.1%}")
                    
                    with col2:
                        st.metric("Fair Odds", f"{rec['fair_odds']:.2f}")
                    
                    with col3:
                        st.metric("Market Odds", f"{rec['market_odds']:.2f}")
                    
                    with col4:
                        st.markdown(f'<div class="{ev_class}">EV: {ev_display}</div>', unsafe_allow_html=True)
                        st.metric("Risk Level", rec['risk_level'])
                    
                    st.info(f"**Rationale:** {rec['rationale']}")
        else:
            st.info("No strong betting recommendations based on current market odds and confidence thresholds.")
        
        # Scoreline distribution chart
        st.markdown("---")
        st.markdown("### 📊 Scoreline Probability Distribution")
        
        if result['scorelines']['top_10']:
            scoreline_df = pd.DataFrame(
                list(result['scorelines']['top_10'].items()),
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
        
        # Raw data for debugging
        with st.expander("📋 View Raw Prediction Data"):
            st.json(result)

if __name__ == "__main__":
    main()
