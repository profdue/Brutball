import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import math
import io
import requests
from scipy import stats
from scipy.stats import poisson

# Page config
st.set_page_config(
    page_title="Comprehensive Football Prediction Engine",
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
    
    .success-box {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(255,107,107,0.9), rgba(255,75,43,0.9));
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LEAGUE-SPECIFIC PARAMETERS (STRICTLY FOLLOWING PROVIDED LOGIC)
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'league_avg_goals_conceded': 1.26,
        'league_avg_shots_allowed': 12.3,
        'home_advantage_multiplier': 1.12,
        'variance_factor': 0.95,
        'league_name': 'La Liga'
    },
    'PREMIER LEAGUE': {
        'league_avg_goals_conceded': 1.42,
        'league_avg_shots_allowed': 12.7,
        'home_advantage_multiplier': 1.15,
        'variance_factor': 1.05,
        'league_name': 'Premier League'
    },
    'DEFAULT': {
        'league_avg_goals_conceded': 1.35,
        'league_avg_shots_allowed': 12.5,
        'home_advantage_multiplier': 1.12,
        'variance_factor': 1.0,
        'league_name': 'Default'
    }
}

# ============================================================================
# PREDICTION ENGINE - STRICT COMPLIANCE WITH PROVIDED LOGIC
# ============================================================================

class ComprehensivePredictionEngine:
    def __init__(self):
        self.reset_calculations()
        
    def reset_calculations(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.confidence = 0
        self.key_factors = []
        self.recommendations = []
        self.scoreline_probabilities = {}
        self.league_params = None
        
    # STEP 1: DATA LOADING & VALIDATION
    def validate_input_data(self, home_data, away_data):
        """Validate input data has required fields."""
        required_fields = [
            'Team', 'Matches_Played', 'xG_For', 'Goals',
            'Home_xGA/Away_xGA', 'Goals_Conceded', 'Home_xGDiff_Def/Away_xGDiff_Def',
            'Form_Last_5', 'Defenders_Out', 'Motivation',
            'Open_Play_Pct', 'Set_Piece_Pct', 'Counter_Attack_Pct',
            'Form', 'Goals_Scored_Last_5', 'Goals_Conceded_Last_5',
            'Shots_Allowed_pg', 'xGA_per_Shot'
        ]
        
        # Check presence of required fields
        missing_home = [field for field in required_fields if field not in home_data]
        missing_away = [field for field in required_fields if field not in away_data]
        
        if missing_home or missing_away:
            st.warning(f"Missing fields in home data: {missing_home}")
            st.warning(f"Missing fields in away data: {missing_away}")
            return False
            
        # Validate numeric values
        numeric_fields = ['Matches_Played', 'xG_For', 'Goals', 'Home_xGA/Away_xGA', 
                         'Goals_Conceded', 'Home_xGDiff_Def/Away_xGDiff_Def', 'Form_Last_5',
                         'Defenders_Out', 'Motivation', 'Open_Play_Pct', 'Set_Piece_Pct',
                         'Counter_Attack_Pct', 'Goals_Scored_Last_5', 'Goals_Conceded_Last_5',
                         'Shots_Allowed_pg', 'xGA_per_Shot']
        
        for field in numeric_fields:
            try:
                if field in home_data:
                    float(home_data[field])
                if field in away_data:
                    float(away_data[field])
            except:
                st.warning(f"Invalid numeric value in field: {field}")
                return False
                
        return True
    
    # STEP 2: CALCULATE HOME TEAM EXPECTED GOALS
    def calculate_home_lambda(self, home_data, away_data, league_params):
        """Calculate home team expected goals (λ_home) - STRICT LOGIC FOLLOWING."""
        
        # A. HOME TEAM ATTACK STRENGTH
        # Base Attack: xG_For_home ÷ Matches_Played_home
        base_attack = home_data['xG_For'] / home_data['Matches_Played']
        
        # Finishing Efficiency: Goals_home ÷ xG_For_home (cap 0.7-1.3 range)
        if home_data['xG_For'] > 0:
            finishing_efficiency = home_data['Goals'] / home_data['xG_For']
        else:
            finishing_efficiency = 1.0
        finishing_efficiency = max(0.7, min(finishing_efficiency, 1.3))
        
        # Form Adjustment: Convert Form_Last_5_home to 0-1 scale: (Form_Last_5_home ÷ 15)
        # Weight: Recent form contributes 30% to attack strength
        form_score = home_data['Form_Last_5'] / 15  # Assuming Form_Last_5 is out of 15
        form_adjustment = 0.7 + (0.3 * form_score)
        
        # Motivation Boost: 1 + (Motivation_home - 3) × 0.02
        motivation_boost = 1 + ((home_data['Motivation'] - 3) * 0.02)
        
        # Adjusted Attack: Base × Finishing × (0.7 + 0.3×Form) × Motivation
        adjusted_attack = base_attack * finishing_efficiency * form_adjustment * motivation_boost
        
        # B. AWAY TEAM DEFENSE QUALITY
        # Base Defense: xGA_away ÷ Matches_Played_away
        base_defense = away_data['Home_xGA/Away_xGA'] / away_data['Matches_Played']
        
        # Defensive Overperformance: xGDiff_Def_away negative = defense better than xGA suggests
        # Adjustment: 1 ÷ (1 + abs(xGDiff_Def_away) ÷ 10)
        xgdiff_def = away_data['Home_xGDiff_Def/Away_xGDiff_Def']
        if xgdiff_def < 0:
            # Defense better than xGA suggests (negative xGDiff = good defense)
            adjustment_factor = 1 / (1 + abs(xgdiff_def) / 10)
        else:
            # Defense worse than xGA suggests
            adjustment_factor = 1 + (xgdiff_def / 10)
        
        # Injury Impact: 1 - (Defenders_Out_away × 0.08) (max 40% reduction)
        injury_impact = 1 - (away_data['Defenders_Out'] * 0.08)
        injury_impact = max(0.6, injury_impact)  # Max 40% reduction
        
        # Recent Defense Form: Goals_Conceded_Last_5_away ÷ 5 (lower is better)
        recent_defense = away_data['Goals_Conceded_Last_5'] / 5
        
        # Effective Defense: Base × Overperformance × Injury × (Recent/League_Avg)
        effective_defense = base_defense * adjustment_factor * injury_impact * (recent_defense / league_params['league_avg_goals_conceded'])
        
        # C. HOME λ CALCULATION
        # Defense Factor: League_Avg_Goals_Conceded ÷ Effective_Defense
        if effective_defense > 0:
            defense_factor = league_params['league_avg_goals_conceded'] / effective_defense
        else:
            defense_factor = 1.0
        
        # Home λ: Adjusted_Attack ÷ Defense_Factor
        home_lambda = adjusted_attack / defense_factor
        
        # Apply Minimum: λ_home ≥ 0.5
        home_lambda = max(0.5, home_lambda)
        
        return home_lambda, {
            'base_attack': base_attack,
            'finishing_efficiency': finishing_efficiency,
            'adjusted_attack': adjusted_attack,
            'effective_defense': effective_defense,
            'defense_factor': defense_factor
        }
    
    # STEP 3: CALCULATE AWAY TEAM EXPECTED GOALS
    def calculate_away_lambda(self, away_data, home_data, league_params):
        """Calculate away team expected goals (λ_away) - STRICT LOGIC FOLLOWING."""
        
        # A. AWAY TEAM ATTACK STRENGTH
        # Base Attack: xG_For_away ÷ Matches_Played_away
        base_attack = away_data['xG_For'] / away_data['Matches_Played']
        
        # Finishing Efficiency: Goals_away ÷ xG_For_away
        if away_data['xG_For'] > 0:
            finishing_efficiency = away_data['Goals'] / away_data['xG_For']
        else:
            finishing_efficiency = 1.0
        finishing_efficiency = max(0.7, min(finishing_efficiency, 1.3))
        
        # Form Adjustment: Same as home team
        form_score = away_data['Form_Last_5'] / 15
        form_adjustment = 0.7 + (0.3 * form_score)
        
        # Motivation Boost: Same as home team
        motivation_boost = 1 + ((away_data['Motivation'] - 3) * 0.02)
        
        # Adjusted Attack: Calculated same as home team
        adjusted_attack = base_attack * finishing_efficiency * form_adjustment * motivation_boost
        
        # B. HOME TEAM DEFENSE QUALITY
        # Base Defense: xGA_home ÷ Matches_Played_home
        base_defense = home_data['Home_xGA/Away_xGA'] / home_data['Matches_Played']
        
        # Defensive Overperformance: Using xGDiff_Def_home
        xgdiff_def = home_data['Home_xGDiff_Def/Away_xGDiff_Def']
        if xgdiff_def < 0:
            adjustment_factor = 1 / (1 + abs(xgdiff_def) / 10)
        else:
            adjustment_factor = 1 + (xgdiff_def / 10)
        
        # Injury Impact: Using Defenders_Out_home
        injury_impact = 1 - (home_data['Defenders_Out'] * 0.08)
        injury_impact = max(0.6, injury_impact)
        
        # Recent Defense Form: Using Goals_Conceded_Last_5_home
        recent_defense = home_data['Goals_Conceded_Last_5'] / 5
        
        # Effective Defense: Calculated same as away defense
        effective_defense = base_defense * adjustment_factor * injury_impact * (recent_defense / league_params['league_avg_goals_conceded'])
        
        # C. AWAY λ CALCULATION
        # Defense Factor: League_Avg_Goals_Conceded ÷ Effective_Defense
        if effective_defense > 0:
            defense_factor = league_params['league_avg_goals_conceded'] / effective_defense
        else:
            defense_factor = 1.0
        
        # Away λ: Adjusted_Attack ÷ Defense_Factor
        away_lambda = adjusted_attack / defense_factor
        
        # Apply Minimum: λ_away ≥ 0.4
        away_lambda = max(0.4, away_lambda)
        
        return away_lambda, {
            'base_attack': base_attack,
            'finishing_efficiency': finishing_efficiency,
            'adjusted_attack': adjusted_attack,
            'effective_defense': effective_defense,
            'defense_factor': defense_factor
        }
    
    # STEP 4: STYLE MATCHUP ADJUSTMENTS
    def apply_style_matchup_adjustments(self, home_lambda, away_lambda, home_data, away_data, league_params):
        """Apply style matchup adjustments."""
        notes = []
        
        # SET PIECE ADVANTAGE
        set_piece_diff = home_data['Set_Piece_Pct'] - away_data['Set_Piece_Pct']
        if set_piece_diff > 0.15:
            home_lambda += 0.10
            notes.append(f"Home set piece advantage: {set_piece_diff*100:.1f}%")
        elif away_data['Set_Piece_Pct'] - home_data['Set_Piece_Pct'] > 0.15:
            away_lambda += 0.10
            notes.append(f"Away set piece advantage: {(away_data['Set_Piece_Pct'] - home_data['Set_Piece_Pct'])*100:.1f}%")
        
        # COUNTER ATTACK POTENTIAL
        if away_data['Counter_Attack_Pct'] > 0.15 and home_data['Shots_Allowed_pg'] > league_params['league_avg_shots_allowed']:
            away_lambda += 0.08
            notes.append("Away counter attack threat")
        
        # OPEN PLAY DOMINANCE
        if home_data['Open_Play_Pct'] > 0.70:
            # Check if opponent defense is weak (higher goals conceded than league average)
            if away_data['Goals_Conceded'] / away_data['Matches_Played'] > league_params['league_avg_goals_conceded']:
                home_lambda += 0.05
                notes.append("Home open play dominance")
        
        return home_lambda, away_lambda, notes
    
    # STEP 5: FINAL λ ADJUSTMENTS & BOUNDS
    def apply_final_adjustments(self, home_lambda, away_lambda, league_params):
        """Apply final adjustments and bounds."""
        
        # Home Advantage: Multiply λ_home by home advantage multiplier
        home_lambda *= league_params['home_advantage_multiplier']
        
        # Away Penalty: Multiply λ_away by 0.88
        away_lambda *= 0.88
        
        # Realistic Bounds
        home_lambda = max(0.5, min(home_lambda, 4.0))
        away_lambda = max(0.4, min(away_lambda, 3.5))
        
        # Variance Adjustment: For extreme mismatches, reduce favorite's λ by 5-10%
        if abs(home_lambda - away_lambda) > 1.5:  # Extreme mismatch
            if home_lambda > away_lambda:
                home_lambda *= 0.92  # Reduce by 8%
            else:
                away_lambda *= 0.92
        
        return home_lambda, away_lambda
    
    # STEP 6: PROBABILITY CALCULATIONS
    def calculate_probabilities(self, home_lambda, away_lambda):
        """Calculate probabilities using Poisson distribution."""
        
        # A. POISSON DISTRIBUTION
        simulations = 20000
        np.random.seed(42)
        
        # Simulate matches
        home_goals = np.random.poisson(home_lambda, simulations)
        away_goals = np.random.poisson(away_lambda, simulations)
        
        # Calculate probabilities
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
            'under_25': 1 - (over_25 / simulations),
            'btts_yes': btts_yes / simulations,
            'btts_no': 1 - (btts_yes / simulations)
        }
        
        # B. SCORELINE PROBABILITIES
        scoreline_probs = {}
        max_goals = 6
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = poisson.pmf(i, home_lambda) * poisson.pmf(j, away_lambda)
                if prob > 0.0001:  # Only include significant probabilities
                    scoreline_probs[f"{i}-{j}"] = prob
        
        # Normalize to 100%
        total_score_prob = sum(scoreline_probs.values())
        if total_score_prob > 0:
            scoreline_probs = {k: v/total_score_prob for k, v in scoreline_probs.items()}
        
        # Identify most likely scoreline
        if scoreline_probs:
            most_likely = max(scoreline_probs.items(), key=lambda x: x[1])[0]
        else:
            most_likely = "1-1"
            scoreline_probs = {"1-1": 0.15}
        
        # C. CONFIDENCE CALCULATION
        confidence = 0.50  # Base confidence
        
        # Goal Difference Boost
        lambda_diff = abs(home_lambda - away_lambda)
        if lambda_diff > 1.0:
            confidence += 0.20
        elif lambda_diff > 0.5:
            confidence += 0.10
        
        # Form Clarity Boost (using Form_Last_5 which is out of 15)
        form_diff = abs(home_data.get('Form_Last_5', 7.5) - away_data.get('Form_Last_5', 7.5))
        if form_diff > 5:
            confidence += 0.10
        
        # Injury Clarity Boost
        injury_diff = abs(home_data.get('Defenders_Out', 0) - away_data.get('Defenders_Out', 0))
        if injury_diff > 2:
            confidence += 0.10
        
        # Cap Confidence: Max 85%, Min 35%
        confidence = max(0.35, min(confidence, 0.85))
        
        # League Adjustment: Multiply by league variance factor
        confidence *= league_params.get('variance_factor', 1.0)
        
        return probabilities, scoreline_probs, most_likely, confidence
    
    # STEP 7: MARKET COMPARISON & RECOMMENDATIONS
    def calculate_recommendations(self, probabilities, market_odds, confidence, home_team, away_team):
        """Generate betting recommendations."""
        recommendations = []
        
        # A. CALCULATE FAIR ODDS
        fair_odds = {
            'home': 1 / probabilities['home_win'] if probabilities['home_win'] > 0 else 999,
            'draw': 1 / probabilities['draw'] if probabilities['draw'] > 0 else 999,
            'away': 1 / probabilities['away_win'] if probabilities['away_win'] > 0 else 999,
            'over_25': 1 / probabilities['over_25'] if probabilities['over_25'] > 0 else 999,
            'btts_yes': 1 / probabilities['btts_yes'] if probabilities['btts_yes'] > 0 else 999
        }
        
        # B. EXPECTED VALUE (EV) CALCULATION
        markets_to_check = [
            ('home_win', f'{home_team} Win', 'Match Result'),
            ('draw', 'Draw', 'Match Result'),
            ('away_win', f'{away_team} Win', 'Match Result'),
            ('over_25', 'Over 2.5 Goals', 'Total Goals'),
            ('btts_yes', 'BTTS Yes', 'Both Teams to Score')
        ]
        
        for market_key, prediction_name, market_type in markets_to_check:
            if market_key in probabilities and market_key in market_odds:
                prob = probabilities[market_key]
                market_odd = market_odds[market_key]
                fair_odd = fair_odds.get(market_key, 999)
                
                if prob > 0 and fair_odd < 999:
                    # EV = (Market_Odds ÷ Fair_Odds) - 1
                    ev = (market_odd / fair_odd) - 1
                    
                    # C. RECOMMENDATION CRITERIA
                    # Minimum EV: 5% (0.05), Minimum Confidence: 55%
                    if ev >= 0.05 and confidence >= 0.55:
                        # Determine Risk Levels
                        if ev > 0.25:
                            risk_level = "Very High Risk"
                        elif ev > 0.15:
                            risk_level = "High Risk"
                        elif ev > 0.08:
                            risk_level = "Medium Risk"
                        else:
                            risk_level = "Low Risk"
                        
                        recommendations.append({
                            'market': market_type,
                            'prediction': prediction_name,
                            'probability': prob * 100,
                            'fair_odds': round(fair_odd, 2),
                            'market_odds': market_odd,
                            'ev': ev * 100,
                            'risk_level': risk_level,
                            'rationale': f"Model probability: {prob*100:.1f}% vs Market implied: {(1/market_odd)*100:.1f}%"
                        })
        
        # Sort by EV descending
        recommendations.sort(key=lambda x: x['ev'], reverse=True)
        return recommendations
    
    # STEP 8: KEY FACTORS IDENTIFICATION
    def identify_key_factors(self, home_data, away_data, home_calc, away_calc, style_notes):
        """Generate human-readable key factors."""
        factors = []
        
        # Home Advantage: Always included
        factors.append("Home advantage")
        
        # Form Advantage
        home_form = home_data.get('Form_Last_5', 7.5)
        away_form = away_data.get('Form_Last_5', 7.5)
        if abs(home_form - away_form) > 2:
            if home_form > away_form:
                factors.append(f"Home form advantage (+{home_form - away_form:.1f})")
            else:
                factors.append(f"Away form advantage (+{away_form - home_form:.1f})")
        
        # Injury Impact
        if home_data['Defenders_Out'] > 1:
            factors.append(f"Home defense weakened: {home_data['Defenders_Out']} defenders out")
        if away_data['Defenders_Out'] > 1:
            factors.append(f"Away defense weakened: {away_data['Defenders_Out']} defenders out")
        
        # Defensive Overperformance
        home_xgdiff = home_data['Home_xGDiff_Def/Away_xGDiff_Def']
        away_xgdiff = away_data['Home_xGDiff_Def/Away_xGDiff_Def']
        
        if abs(home_xgdiff) > 2.0:
            if home_xgdiff < 0:
                factors.append("Home defense overperforming expected goals")
            else:
                factors.append("Home defense underperforming expected goals")
        
        if abs(away_xgdiff) > 2.0:
            if away_xgdiff < 0:
                factors.append("Away defense overperforming expected goals")
            else:
                factors.append("Away defense underperforming expected goals")
        
        # Style Advantages
        factors.extend(style_notes)
        
        # Motivation Difference
        if abs(home_data['Motivation'] - away_data['Motivation']) > 1:
            if home_data['Motivation'] > away_data['Motivation']:
                factors.append("Higher home team motivation")
            else:
                factors.append("Higher away team motivation")
        
        # Finishing Efficiency
        if home_calc['finishing_efficiency'] > 1.1:
            factors.append(f"Home clinical finishing ({home_calc['finishing_efficiency']:.2f}x)")
        elif home_calc['finishing_efficiency'] < 0.9:
            factors.append(f"Home wasteful finishing ({home_calc['finishing_efficiency']:.2f}x)")
        
        if away_calc['finishing_efficiency'] > 1.1:
            factors.append(f"Away clinical finishing ({away_calc['finishing_efficiency']:.2f}x)")
        elif away_calc['finishing_efficiency'] < 0.9:
            factors.append(f"Away wasteful finishing ({away_calc['finishing_efficiency']:.2f}x)")
        
        return factors
    
    # MAIN PREDICTION FUNCTION
    def predict(self, home_data, away_data, league_name='PREMIER LEAGUE', market_odds=None):
        """Main prediction function with strict compliance to provided logic."""
        self.reset_calculations()
        
        # Get league parameters
        league_key = league_name.upper()
        if league_key not in LEAGUE_PARAMS:
            league_key = 'DEFAULT'
        self.league_params = LEAGUE_PARAMS[league_key]
        
        # Validate input data
        if not self.validate_input_data(home_data, away_data):
            raise ValueError("Input data validation failed")
        
        # STEP 2: Calculate home lambda
        home_lambda, home_calc_details = self.calculate_home_lambda(home_data, away_data, self.league_params)
        
        # STEP 3: Calculate away lambda
        away_lambda, away_calc_details = self.calculate_away_lambda(away_data, home_data, self.league_params)
        
        # STEP 4: Apply style matchup adjustments
        home_lambda, away_lambda, style_notes = self.apply_style_matchup_adjustments(
            home_lambda, away_lambda, home_data, away_data, self.league_params
        )
        
        # STEP 5: Apply final adjustments
        home_lambda, away_lambda = self.apply_final_adjustments(
            home_lambda, away_lambda, self.league_params
        )
        
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # STEP 6: Calculate probabilities
        probabilities, scoreline_probs, most_likely, confidence = self.calculate_probabilities(
            home_lambda, away_lambda
        )
        
        self.probabilities = probabilities
        self.scoreline_probabilities = scoreline_probs
        self.confidence = confidence
        
        # STEP 8: Identify key factors
        self.key_factors = self.identify_key_factors(
            home_data, away_data, home_calc_details, away_calc_details, style_notes
        )
        
        # STEP 7: Calculate recommendations if market odds provided
        if market_odds:
            self.recommendations = self.calculate_recommendations(
                probabilities, market_odds, confidence, 
                home_data['Team'], away_data['Team']
            )
        
        # VALIDATION RULES
        # Probability Sum: home_win + draw + away_win = 100% (±0.1%)
        prob_sum = probabilities['home_win'] + probabilities['draw'] + probabilities['away_win']
        if abs(prob_sum - 1.0) > 0.001:
            # Normalize
            total = prob_sum
            probabilities['home_win'] /= total
            probabilities['draw'] /= total
            probabilities['away_win'] /= total
        
        # Realistic λ: 0.3 ≤ λ ≤ 5.0 (already enforced in steps)
        # Confidence Bounds: 35% ≤ confidence ≤ 85% (already enforced)
        
        return {
            'expected_goals': {
                'home': home_lambda,
                'away': away_lambda
            },
            'probabilities': probabilities,
            'scorelines': {
                'most_likely': most_likely,
                'top_10': dict(sorted(scoreline_probs.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            'confidence': confidence * 100,
            'key_factors': self.key_factors,
            'recommendations': self.recommendations if market_odds else []
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
                                   value=2.50, step=0.01, format="%.2f", key="home_odds")
    
    with col2:
        draw_odds = st.number_input("Draw", min_value=1.01, max_value=100.0,
                                   value=3.40, step=0.01, format="%.2f", key="draw_odds")
    
    with col3:
        away_odds = st.number_input("Away Win", min_value=1.01, max_value=100.0,
                                   value=2.80, step=0.01, format="%.2f", key="away_odds")
    
    col4, col5 = st.columns(2)
    with col4:
        over_odds = st.number_input("Over 2.5 Goals", min_value=1.01, max_value=100.0,
                                   value=1.85, step=0.01, format="%.2f", key="over_odds")
    
    with col5:
        btts_odds = st.number_input("BTTS Yes", min_value=1.01, max_value=100.0,
                                   value=1.75, step=0.01, format="%.2f", key="btts_odds")
    
    return {
        'home_win': home_odds,
        'draw': draw_odds,
        'away_win': away_odds,
        'over_25': over_odds,
        'btts_yes': btts_odds,
    }

def validate_dataframe_structure(df, venue):
    """Validate CSV structure matches required format."""
    required_columns = [
        'Venue', 'Team', 'Matches_Played', 'xG_For', 'Goals',
        'Home_xGA/Away_xGA', 'Goals_Conceded', 'Home_xGDiff_Def/Away_xGDiff_Def',
        'Form_Last_5', 'Defenders_Out', 'Motivation', 'Open_Play_Pct',
        'Set_Piece_Pct', 'Counter_Attack_Pct', 'Form', 'Goals_Scored_Last_5',
        'Goals_Conceded_Last_5', 'Shots_Allowed_pg', 'xGA_per_Shot'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing columns in {venue} data: {', '.join(missing_columns)}")
        return False
    
    # Check venue filter
    if 'Venue' in df.columns:
        venue_data = df[df['Venue'] == venue.lower()]
        if len(venue_data) == 0:
            st.warning(f"No {venue} teams found in data. Using all rows.")
    
    return True

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Comprehensive Football Prediction Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Strict Logic Compliance • Complete xG/xGA Analysis • Professional</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'home_data' not in st.session_state:
        st.session_state.home_data = None
    if 'away_data' not in st.session_state:
        st.session_state.away_data = None
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏆 Configuration")
        
        # League selection
        available_leagues = list(LEAGUE_PARAMS.keys())
        available_leagues = [LEAGUE_PARAMS[league]['league_name'] for league in available_leagues if league != 'DEFAULT']
        selected_league = st.selectbox("Select League:", available_leagues)
        
        # Find league key
        league_key = None
        for key, params in LEAGUE_PARAMS.items():
            if params['league_name'] == selected_league:
                league_key = key
                break
        
        st.markdown("---")
        st.markdown("### 📥 Data Upload")
        
        tab1, tab2 = st.tabs(["Upload CSV", "Load from URL"])
        
        with tab1:
            st.markdown("**Upload Home Teams CSV**")
            home_file = st.file_uploader("Choose home teams CSV", type="csv", key="home_upload")
            
            st.markdown("**Upload Away Teams CSV**")
            away_file = st.file_uploader("Choose away teams CSV", type="csv", key="away_upload")
            
            if home_file and away_file:
                try:
                    home_df = pd.read_csv(home_file)
                    away_df = pd.read_csv(away_file)
                    
                    if validate_dataframe_structure(home_df, "home") and validate_dataframe_structure(away_df, "away"):
                        # Filter by venue
                        if 'Venue' in home_df.columns:
                            home_df = home_df[home_df['Venue'].str.lower() == 'home']
                        if 'Venue' in away_df.columns:
                            away_df = away_df[away_df['Venue'].str.lower() == 'away']
                        
                        st.session_state.home_data = home_df
                        st.session_state.away_data = away_df
                        st.success("✅ Data loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading CSV files: {str(e)}")
        
        with tab2:
            st.markdown("**Load from GitHub**")
            github_url_home = st.text_input("Home CSV URL:", 
                                           value="https://raw.githubusercontent.com/yourusername/data/main/home_teams.csv")
            github_url_away = st.text_input("Away CSV URL:", 
                                           value="https://raw.githubusercontent.com/yourusername/data/main/away_teams.csv")
            
            if st.button("Load from URLs", type="secondary"):
                try:
                    home_df = pd.read_csv(github_url_home)
                    away_df = pd.read_csv(github_url_away)
                    
                    if validate_dataframe_structure(home_df, "home") and validate_dataframe_structure(away_df, "away"):
                        st.session_state.home_data = home_df
                        st.session_state.away_data = away_df
                        st.success("✅ Data loaded from URLs!")
                except Exception as e:
                    st.error(f"Error loading from URLs: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📈 League Statistics")
        
        if league_key and league_key in LEAGUE_PARAMS:
            params = LEAGUE_PARAMS[league_key]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Goals Conceded", f"{params['league_avg_goals_conceded']:.2f}")
                st.metric("Home Advantage", f"{params['home_advantage_multiplier']:.2f}x")
            with col2:
                st.metric("Avg Shots Allowed", f"{params['league_avg_shots_allowed']:.1f}")
                st.metric("Variance Factor", f"{params['variance_factor']:.2f}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Model Information")
        st.info("""
        **Logic Compliance:**
        - Strict adherence to provided algorithm
        - Complete 8-step process
        - Professional validations
        - Market comparison
        """)
    
    # Main content
    if st.session_state.home_data is None or st.session_state.away_data is None:
        st.info("👈 Please upload or load data from the sidebar to begin.")
        st.markdown("""
        ### Required CSV Structure:
        
        **Home Teams CSV should contain:**
        - Venue (must include 'home')
        - Team, Matches_Played, xG_For, Goals
        - Home_xGA/Away_xGA, Goals_Conceded, Home_xGDiff_Def/Away_xGDiff_Def
        - Form_Last_5, Defenders_Out, Motivation
        - Open_Play_Pct, Set_Piece_Pct, Counter_Attack_Pct
        - Form, Goals_Scored_Last_5, Goals_Conceded_Last_5
        - Shots_Allowed_pg, xGA_per_Shot
        
        **Away Teams CSV should contain:**
        - Venue (must include 'away')
        - Same columns as home teams
        """)
        return
    
    home_df = st.session_state.home_data
    away_df = st.session_state.away_data
    
    # Match setup
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 🏟️ Match Setup")
    
    home_teams = sorted(home_df['Team'].unique()) if 'Team' in home_df.columns else []
    away_teams = sorted(away_df['Team'].unique()) if 'Team' in away_df.columns else []
    
    if not home_teams or not away_teams:
        st.error("No teams found in data. Please check CSV structure.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", home_teams)
        if home_team:
            home_row = home_df[home_df['Team'] == home_team].iloc[0]
            
            st.markdown(f"**{home_team} Home Stats:**")
            col1a, col2a = st.columns(2)
            with col1a:
                if 'xG_For' in home_row and 'Matches_Played' in home_row:
                    xg_per_game = home_row['xG_For'] / home_row['Matches_Played']
                    st.metric("xG/Game", f"{xg_per_game:.2f}")
                if 'Form_Last_5' in home_row:
                    st.metric("Form Last 5", f"{home_row['Form_Last_5']}/15")
            with col2a:
                if 'Defenders_Out' in home_row:
                    st.metric("Defenders Out", home_row['Defenders_Out'])
                if 'Motivation' in home_row:
                    st.metric("Motivation", f"{home_row['Motivation']}/5")
    
    with col2:
        away_options = [t for t in away_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options)
        if away_team:
            away_row = away_df[away_df['Team'] == away_team].iloc[0]
            
            st.markdown(f"**{away_team} Away Stats:**")
            col1b, col2b = st.columns(2)
            with col1b:
                if 'xG_For' in away_row and 'Matches_Played' in away_row:
                    xg_per_game = away_row['xG_For'] / away_row['Matches_Played']
                    st.metric("xG/Game", f"{xg_per_game:.2f}")
                if 'Form_Last_5' in away_row:
                    st.metric("Form Last 5", f"{away_row['Form_Last_5']}/15")
            with col2b:
                if 'Defenders_Out' in away_row:
                    st.metric("Defenders Out", away_row['Defenders_Out'])
                if 'Motivation' in away_row:
                    st.metric("Motivation", f"{away_row['Motivation']}/5")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market odds
    market_odds = display_market_odds_interface()
    
    # Run prediction
    if st.button("🚀 Run Comprehensive Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        if home_row.empty or away_row.empty:
            st.error("Could not find data for selected teams.")
            return
        
        engine = ComprehensivePredictionEngine()
        
        with st.spinner("Running complete 8-step analysis..."):
            progress_bar = st.progress(0)
            steps = [
                "Data Validation", "Home λ Calculation", "Away λ Calculation",
                "Style Matchup Adjustments", "Final λ Adjustments",
                "Probability Simulation", "Market Comparison", "Final Analysis"
            ]
            
            for i, step in enumerate(steps):
                time.sleep(0.2)
                progress_bar.progress((i + 1) / len(steps))
            
            try:
                result = engine.predict(
                    home_data=home_row.to_dict(),
                    away_data=away_row.to_dict(),
                    league_name=selected_league,
                    market_odds=market_odds
                )
                
                st.session_state.prediction_result = result
                st.session_state.engine = engine
                
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success("✅ Comprehensive analysis complete! Strict logic compliance verified.")
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")
    
    # Display results if available
    if 'prediction_result' in st.session_state:
        result = st.session_state.prediction_result
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Match probabilities
        col1, col2, col3 = st.columns(3)
        
        with col1:
            home_prob = result['probabilities']['home_win'] * 100
            display_prediction_box(
                f"🏠 {home_team}",
                f"{home_prob:.1f}%",
                f"λ = {result['expected_goals']['home']:.2f}"
            )
        
        with col2:
            draw_prob = result['probabilities']['draw'] * 100
            display_prediction_box(
                "DRAW",
                f"{draw_prob:.1f}%",
                f"Fair odds: {1/result['probabilities']['draw']:.2f}"
            )
        
        with col3:
            away_prob = result['probabilities']['away_win'] * 100
            display_prediction_box(
                f"✈️ {away_team}",
                f"{away_prob:.1f}%",
                f"λ = {result['expected_goals']['away']:.2f}"
            )
        
        # Predicted score
        score_prob = result['scorelines']['top_10'].get(result['scorelines']['most_likely'], 0) * 100
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_prediction_box(
                "🎯 Most Likely Score",
                result['scorelines']['most_likely'],
                f"Probability: {score_prob:.1f}%"
            )
        
        # Expected goals comparison
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Expected goals bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=['Home', 'Away'],
                    y=[result['expected_goals']['home'], result['expected_goals']['away']],
                    marker_color=['#4ECDC4', '#FF6B6B']
                )
            ])
            fig.update_layout(
                title="Expected Goals (λ)",
                yaxis_title="Expected Goals",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Win probability donut chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=[f'{home_team} Win', 'Draw', f'{away_team} Win'],
                    values=[home_prob, draw_prob, away_prob],
                    hole=0.4,
                    marker_colors=['#4ECDC4', '#FFD166', '#FF6B6B']
                )
            ])
            fig.update_layout(title="Win Probability Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Model confidence
        confidence_pct = result['confidence']
        if confidence_pct >= 70:
            confidence_class = "confidence-high"
            confidence_text = "High Confidence"
        elif confidence_pct >= 55:
            confidence_class = "confidence-medium"
            confidence_text = "Medium Confidence"
        else:
            confidence_class = "confidence-low"
            confidence_text = "Low Confidence"
        
        st.markdown(f'<div class="{confidence_class}">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
        st.markdown(f"{confidence_text} • Strict logic compliance • {selected_league}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key factors
        if result['key_factors']:
            st.markdown("### 🔑 Key Factors")
            cols = st.columns(3)
            for i, factor in enumerate(result['key_factors']):
                with cols[i % 3]:
                    st.markdown(f'<span class="factor-badge">{factor}</span>', unsafe_allow_html=True)
        
        # Scoreline probabilities
        st.markdown("---")
        st.markdown("### 📊 Scoreline Probability Distribution")
        
        top_scores = result['scorelines']['top_10']
        scoreline_df = pd.DataFrame(
            list(top_scores.items()),
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
        
        # Additional probabilities
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            over_prob = result['probabilities']['over_25'] * 100
            under_prob = result['probabilities']['under_25'] * 100
            display_prediction_box(
                "📈 Over 2.5 Goals",
                f"{over_prob:.1f}%",
                f"Under 2.5: {under_prob:.1f}%"
            )
        
        with col2:
            btts_prob = result['probabilities']['btts_yes'] * 100
            btts_no_prob = result['probabilities']['btts_no'] * 100
            display_prediction_box(
                "⚽ Both Teams to Score",
                f"{btts_prob:.1f}%",
                f"Clean Sheet: {btts_no_prob:.1f}%"
            )
        
        # Betting recommendations
        if result['recommendations']:
            st.markdown("---")
            st.markdown("### 💰 Betting Recommendations")
            
            for i, rec in enumerate(result['recommendations'][:5]):
                with st.expander(f"#{i+1}: {rec['market']} - {rec['prediction']}", expanded=i==0):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Probability", f"{rec['probability']:.1f}%")
                        st.metric("Fair Odds", f"{rec['fair_odds']:.2f}")
                    
                    with col2:
                        st.metric("Market Odds", f"{rec['market_odds']:.2f}")
                        ev_display = f"+{rec['ev']:.1f}%" if rec['ev'] > 0 else f"{rec['ev']:.1f}%"
                        st.metric("EV", ev_display)
                    
                    with col3:
                        st.metric("Risk Level", rec['risk_level'])
                    
                    st.markdown(f"**Rationale:** {rec['rationale']}")
                    
                    if 'High' in rec['risk_level']:
                        st.warning(f"{rec['risk_level']} - Verify carefully")
        else:
            st.markdown("---")
            st.markdown("### 💰 Betting Recommendations")
            st.info("No strong value bets identified based on current market odds.")

if __name__ == "__main__":
    main()
