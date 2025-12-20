import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import math
import io
import requests
from scipy import stats

# ============================================================================
# LEAGUE-SPECIFIC PARAMETERS & CONSTANTS - FINAL TIER-BASED VERSION
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'avg_goals': 1.26,
        'avg_shots': 12.3,
        'home_advantage': 1.18,
        'goal_variance': 'medium'
    },
    'PREMIER LEAGUE': {
        'avg_goals': 1.42,
        'avg_shots': 12.7,
        'home_advantage': 1.18,
        'goal_variance': 'high'
    }
}

CONSTANTS = {
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 6,
    'MIN_HOME_LAMBDA': 0.8,
    'MIN_AWAY_LAMBDA': 0.6,
    'DEFENDER_INJURY_IMPACT': 0.03,
    'TREND_CAP_MIN': 0.7,
    'TREND_CAP_MAX': 1.3,
    'SET_PIECE_THRESHOLD': 0.15,
    'COUNTER_ATTACK_THRESHOLD': 0.15,
    'MOTIVATION_BASE': 0.95,
    'MOTIVATION_INCREMENT': 0.02,
}

# ============================================================================
# PREDICTION ENGINE CORE - FIXED VERSION WITH DEBUGGING
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
        self.debug_info = []  # New: Store debug information
    
    def _get_tier_based_max_lambda(self, position, is_home):
        """Get tier-based maximum λ based on team position."""
        if position <= 3:  # Elite team
            if is_home:
                return 3.0  # Elite home teams can score more
            else:
                return 2.5  # Elite away teams
        elif position <= 6:  # Top team
            if is_home:
                return 2.7
            else:
                return 2.2
        elif position <= 12:  # Mid-table
            if is_home:
                return 2.3
            else:
                return 1.8
        else:  # Lower team
            if is_home:
                return 2.0
            else:
                return 1.5
    
    def _step1_base_expected_goals(self, team_data, is_home):
        """STEP 1: Calculate base expected goals using venue-specific xG."""
        if is_home:
            home_xg_for = team_data.get('home_xg_for', 0)
            home_matches = team_data.get('matches_played', 1)
            if home_matches > 0:
                return home_xg_for / home_matches
            else:
                return self.league_params['avg_goals'] * 1.1
        else:
            away_xg_for = team_data.get('away_xg_for', 0)
            away_matches = team_data.get('matches_played', 1)
            if away_matches > 0:
                return away_xg_for / away_matches
            else:
                return self.league_params['avg_goals'] * 0.9
    
    def _step2_opponent_adjustment(self, attack_team_data, defense_team_data, is_home):
        """STEP 2: Calibrated opponent defense adjustment with piecewise dampening."""
        if is_home:
            opp_xga = defense_team_data.get('away_xga', 0)
            opp_matches = defense_team_data.get('matches_played', 1)
        else:
            opp_xga = defense_team_data.get('home_xga', 0)
            opp_matches = defense_team_data.get('matches_played', 1)
        
        if opp_matches > 0:
            opp_defense = opp_xga / opp_matches
        else:
            opp_defense = self.league_params['avg_goals']
        
        raw_ratio = opp_defense / self.league_params['avg_goals']
        
        # CALIBRATED PIECEWISE DAMPENING
        if raw_ratio > 1.8:  # Opponent is 80%+ worse than average (EXTREME)
            # Very strong dampening: only 25% of the excess
            dampened_factor = 1.0 + (raw_ratio - 1.0) * 0.25
        elif raw_ratio > 1.4:  # Opponent is 40%+ worse than average (HIGH)
            # Strong dampening: 50% of the excess
            dampened_factor = 1.0 + (raw_ratio - 1.0) * 0.5
        elif raw_ratio < 0.6:  # Opponent is 40%+ better than average (EXTREME)
            # Very strong dampening for excellent defenses
            dampened_factor = 1.0 - (1.0 - raw_ratio) * 0.4
        elif raw_ratio < 0.8:  # Opponent is 20%+ better than average (HIGH)
            # Strong dampening
            dampened_factor = 1.0 - (1.0 - raw_ratio) * 0.6
        else:
            # Normal range: moderate dampening
            dampened_factor = raw_ratio ** 0.8
        
        # Additional caps based on reality
        dampened_factor = max(0.6, min(1.8, dampened_factor))
        
        return dampened_factor
    
    def _step3_recent_form_override(self, team_data, is_home):
        """STEP 3: Apply recent form trends with venue-aware calculation."""
        # Calculate recent averages (actual goals)
        recent_goals_pg = team_data.get('goals_scored_last_5', 0) / 5
        
        # Calculate venue-specific season goals
        matches_played = max(team_data.get('matches_played', 1), 1)
        total_goals = team_data.get('goals', 0)  # This is TOTAL goals (home + away)
        
        # IMPORTANT: We need venue-specific goals, not total goals
        # Since we don't have venue-specific goals in data, estimate
        if is_home:
            # Home teams typically score ~55% of goals at home
            venue_goals_estimate = total_goals * 0.55
        else:
            # Away teams typically score ~45% of goals away
            venue_goals_estimate = total_goals * 0.45
        
        venue_goals_pg = venue_goals_estimate / matches_played
        
        # Calculate attack trend
        if venue_goals_pg > 0:
            attack_trend = recent_goals_pg / venue_goals_pg
        else:
            attack_trend = 1.0
        
        # Get team position for tier-based caps
        position = team_data.get('overall_position', 10)
        
        # TIER-BASED FORM CAPS
        if position <= 3:  # Elite teams
            trend_min = 0.8  # Less harsh for elite teams
            trend_max = 1.4
        elif position <= 6:  # Top teams
            trend_min = 0.75
            trend_max = 1.3
        else:  # Other teams
            trend_min = 0.7
            trend_max = 1.3
        
        # Apply tier-based caps
        attack_trend = max(trend_min, min(trend_max, attack_trend))
        
        return attack_trend
    
    def _step4_key_factor_adjustments(self, home_data, away_data):
        """STEP 4: Apply calibrated key factor adjustments."""
        adjustments = {'home': 1.0, 'away': 1.0}
        
        # 1. Injuries - calibrated impact
        home_injury_impact = 1.0 - (home_data.get('defenders_out', 0) * 
                                   CONSTANTS['DEFENDER_INJURY_IMPACT'])
        away_injury_impact = 1.0 - (away_data.get('defenders_out', 0) * 
                                   CONSTANTS['DEFENDER_INJURY_IMPACT'])
        
        adjustments['home'] *= max(0.85, home_injury_impact)
        adjustments['away'] *= max(0.85, away_injury_impact)
        
        # 2. Motivation
        home_motivation = home_data.get('motivation', 3)
        away_motivation = away_data.get('motivation', 3)
        
        home_motivation_impact = CONSTANTS['MOTIVATION_BASE'] + (home_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        away_motivation_impact = CONSTANTS['MOTIVATION_BASE'] + (away_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        
        adjustments['home'] *= home_motivation_impact
        adjustments['away'] *= away_motivation_impact
        
        # 3. Home/Away Strength - calibrated
        home_advantage = self.league_params['home_advantage'] * (
            1 + home_data.get('home_ppg_diff', 0) * 0.03  # Reduced impact
        )
        away_disadvantage = 2.0 - home_advantage
        
        adjustments['home'] *= home_advantage
        adjustments['away'] *= away_disadvantage
        
        # 4. Playing Style Matchups - reduced impact
        style_adjustments = {'home': 0, 'away': 0}
        
        set_piece_diff = home_data.get('set_piece_pct', 0) - away_data.get('set_piece_pct', 0)
        if abs(set_piece_diff) > CONSTANTS['SET_PIECE_THRESHOLD']:
            if set_piece_diff > 0:
                style_adjustments['home'] += 0.05
            else:
                style_adjustments['away'] += 0.05
        
        if (away_data.get('counter_attack_pct', 0) > CONSTANTS['COUNTER_ATTACK_THRESHOLD'] and 
            home_data.get('shots_allowed_pg', 0) > self.league_params['avg_shots']):
            style_adjustments['away'] += 0.04
        
        adjustments['home'] += style_adjustments['home']
        adjustments['away'] += style_adjustments['away']
        
        # 5. Defensive Performance - minor impact
        home_goals_conceded = home_data.get('goals_conceded', 0)
        home_xga = home_data.get('home_xga', 0)
        if home_xga > 0 and home_goals_conceded / home_xga < 0.9:
            adjustments['away'] *= 0.98
        
        away_goals_conceded = away_data.get('goals_conceded', 0)
        away_xga = away_data.get('away_xga', 0)
        if away_xga > 0 and away_goals_conceded / away_xga < 0.9:
            adjustments['home'] *= 0.98
        
        return adjustments
    
    def _step5_final_calibration(self, home_lambda, away_lambda, home_data, away_data):
        """STEP 5: Tier-based final calibration."""
        # Get tier-based maximum λ values
        home_position = home_data.get('overall_position', 10)
        away_position = away_data.get('overall_position', 10)
        
        max_home_lambda = self._get_tier_based_max_lambda(home_position, is_home=True)
        max_away_lambda = self._get_tier_based_max_lambda(away_position, is_home=False)
        
        # Apply tier-based caps
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], 
                         min(max_home_lambda, home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], 
                         min(max_away_lambda, away_lambda))
        
        # Ensure sum is realistic for football
        total_lambda = home_lambda + away_lambda
        
        # Adjust based on team tiers
        if home_position <= 3 and away_position >= 16:  # Elite vs weak
            # Allow higher total for dominant matchups
            max_total = 5.0
        elif home_position <= 6 and away_position >= 14:  # Strong vs weak
            max_total = 4.5
        else:  # Normal matchups
            max_total = 4.0
        
        if total_lambda > max_total:
            scale_factor = max_total / total_lambda
            home_lambda *= scale_factor
            away_lambda *= scale_factor
        elif total_lambda < 1.5:  # Minimum for competitive matches
            scale_factor = 1.5 / total_lambda
            home_lambda *= scale_factor
            away_lambda *= scale_factor
        
        # Ensure reasonable difference
        diff_ratio = home_lambda / away_lambda if away_lambda > 0.1 else 4.0
        if diff_ratio > 4.0:  # Cap extreme differences
            target_ratio = 4.0
            home_lambda = (home_lambda + away_lambda * target_ratio) / (1 + target_ratio)
            away_lambda = home_lambda / target_ratio
        
        return round(home_lambda, 2), round(away_lambda, 2)
    
    def calculate_expected_goals(self, home_data, away_data):
        """Calculate expected goals with tier-based calibration and debugging."""
        
        # Clear debug info
        self.debug_info = []
        
        # STEP 1: Base expected goals
        home_base = self._step1_base_expected_goals(home_data, is_home=True)
        away_base = self._step1_base_expected_goals(away_data, is_home=False)
        
        self.debug_info.append(f"STEP 1 - Home base xG: {home_base:.2f}")
        self.debug_info.append(f"STEP 1 - Away base xG: {away_base:.2f}")
        
        # STEP 2: Calibrated opponent defense adjustment
        home_opp_factor = self._step2_opponent_adjustment(home_data, away_data, is_home=True)
        away_opp_factor = self._step2_opponent_adjustment(away_data, home_data, is_home=False)
        
        self.debug_info.append(f"STEP 2 - Home opp factor: {home_opp_factor:.2f}")
        self.debug_info.append(f"STEP 2 - Away opp factor: {away_opp_factor:.2f}")
        
        home_lambda = home_base * home_opp_factor
        away_lambda = away_base * away_opp_factor
        
        self.debug_info.append(f"After STEP 2 - Home λ: {home_lambda:.2f}, Away λ: {away_lambda:.2f}")
        
        # STEP 3: Recent form override
        home_trend = self._step3_recent_form_override(home_data, is_home=True)
        away_trend = self._step3_recent_form_override(away_data, is_home=False)
        
        self.debug_info.append(f"STEP 3 - Home trend: {home_trend:.2f}")
        self.debug_info.append(f"STEP 3 - Away trend: {away_trend:.2f}")
        
        home_lambda *= home_trend
        away_lambda *= away_trend
        
        self.debug_info.append(f"After STEP 3 - Home λ: {home_lambda:.2f}, Away λ: {away_lambda:.2f}")
        
        # STEP 4: Key factor adjustments
        key_factors = self._step4_key_factor_adjustments(home_data, away_data)
        home_lambda *= key_factors['home']
        away_lambda *= key_factors['away']
        
        self.debug_info.append(f"STEP 4 - Home key factor: {key_factors['home']:.2f}")
        self.debug_info.append(f"STEP 4 - Away key factor: {key_factors['away']:.2f}")
        self.debug_info.append(f"After STEP 4 - Home λ: {home_lambda:.2f}, Away λ: {away_lambda:.2f}")
        
        # STEP 5: Tier-based final calibration
        home_lambda, away_lambda = self._step5_final_calibration(home_lambda, away_lambda, home_data, away_data)
        
        self.debug_info.append(f"STEP 5 - Final Home λ: {home_lambda:.2f}, Final Away λ: {away_lambda:.2f}")
        
        return home_lambda, away_lambda
    
    def calculate_probabilities(self, home_lambda, away_lambda):
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
        under_25 = np.sum(total_goals < 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        btts_no = np.sum((home_goals == 0) | (away_goals == 0))
        
        probabilities = {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations,
            'over_25': over_25 / simulations,
            'under_25': under_25 / simulations,
            'btts_yes': btts_yes / simulations,
            'btts_no': btts_no / simulations,
        }
        
        # Calculate exact scoreline probabilities
        scoreline_probs = {}
        max_goals = CONSTANTS['MAX_GOALS_CONSIDERED']
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = (stats.poisson.pmf(i, home_lambda) * 
                       stats.poisson.pmf(j, away_lambda))
                if prob > 0.001:
                    scoreline_probs[f"{i}-{j}"] = prob
        
        # Normalize scoreline probabilities
        total_score_prob = sum(scoreline_probs.values())
        if total_score_prob > 0:
            scoreline_probs = {k: v/total_score_prob for k, v in scoreline_probs.items()}
        
        most_likely = max(scoreline_probs.items(), key=lambda x: x[1])[0] if scoreline_probs else "1-1"
        
        return probabilities, scoreline_probs, most_likely
    
    def calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """Calculate model confidence with tier consideration."""
        confidence = 50
        
        # Goal difference factor
        goal_diff = abs(home_lambda - away_lambda)
        confidence += goal_diff * 15
        
        # Position gap factor - enhanced for tier differences
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:  # Large gap
            confidence += 25
        elif pos_diff >= 5:  # Medium gap
            confidence += 15
        else:  # Small gap
            confidence += pos_diff * 1.5
        
        # Form gap factor
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        confidence += min(15, form_diff * 0.8)
        
        # Uncertainty from injuries
        total_injuries = home_data.get('defenders_out', 0) + away_data.get('defenders_out', 0)
        confidence -= total_injuries * 2
        
        # Apply league variance
        if self.league_params['goal_variance'] == 'high':
            confidence *= 0.97
        
        # Clamp to reasonable range
        return round(max(30, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors for the prediction."""
        factors = []
        
        # Add debug info first
        factors.extend(self.debug_info)
        
        # Position and tier analysis
        home_position = home_data['overall_position']
        away_position = away_data['overall_position']
        pos_diff = away_position - home_position
        
        if abs(pos_diff) >= 10:
            factors.append(f"Huge position difference: #{home_position} vs #{away_position}")
        elif abs(pos_diff) >= 5:
            factors.append(f"Significant position difference: #{home_position} vs #{away_position}")
        
        # Tier-based insights
        if home_position <= 3:
            factors.append(f"Elite home team: #{home_position} position")
        if away_position >= 16:
            factors.append(f"Struggling away team: #{away_position} position")
        
        # Expected goals insight
        if home_lambda > 2.5:
            factors.append(f"Extremely high home expected goals: {home_lambda:.2f}")
        elif home_lambda > 2.0:
            factors.append(f"Very high home expected goals: {home_lambda:.2f}")
        
        if away_lambda > 2.0:
            factors.append(f"Very high away expected goals: {away_lambda:.2f}")
        elif away_lambda > 1.5:
            factors.append(f"High away expected goals: {away_lambda:.2f}")
        
        # Defensive quality
        home_xga_pg = home_data.get('home_xga', 0) / max(home_data.get('matches_played', 1), 1)
        away_xga_pg = away_data.get('away_xga', 0) / max(away_data.get('matches_played', 1), 1)
        
        if home_xga_pg < self.league_params['avg_goals'] * 0.8:
            factors.append(f"Strong home defense: {home_xga_pg:.2f} xGA/game")
        if away_xga_pg > self.league_params['avg_goals'] * 1.5:
            factors.append(f"Weak away defense: {away_xga_pg:.2f} xGA/game")
        
        # Recent scoring form
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        
        if home_recent > self.league_params['avg_goals'] * 1.5:
            factors.append(f"Home excellent recent scoring: {home_recent:.2f} goals/game")
        if away_recent < self.league_params['avg_goals'] * 0.5:
            factors.append(f"Away poor recent scoring: {away_recent:.2f} goals/game")
        
        # Injuries
        if home_data.get('defenders_out', 0) >= 3:
            factors.append(f"Home defensive crisis: {home_data['defenders_out']} defenders out")
        if away_data.get('defenders_out', 0) >= 3:
            factors.append(f"Away defensive crisis: {away_data['defenders_out']} defenders out")
        
        return factors
    
    def get_market_recommendations(self, probabilities, market_odds):
        """Get market recommendations."""
        recommendations = []
        
        # Total goals recommendation
        if probabilities['over_25'] > probabilities['under_25']:
            over_rec = {
                'market': 'Total Goals',
                'prediction': 'Over 2.5',
                'probability': probabilities['over_25'],
                'fair_odds': 1 / probabilities['over_25'],
                'market_odds': market_odds.get('over_25', 1.85),
                'strength': 'Strong' if probabilities['over_25'] > 0.65 else 'Moderate' if probabilities['over_25'] > 0.55 else 'Weak'
            }
            recommendations.append(over_rec)
        else:
            under_rec = {
                'market': 'Total Goals',
                'prediction': 'Under 2.5',
                'probability': probabilities['under_25'],
                'fair_odds': 1 / probabilities['under_25'],
                'market_odds': 1 / (1 - 1/market_odds.get('over_25', 1.85)) if market_odds.get('over_25', 1.85) > 1 else 2.00,
                'strength': 'Strong' if probabilities['under_25'] > 0.65 else 'Moderate' if probabilities['under_25'] > 0.55 else 'Weak'
            }
            recommendations.append(under_rec)
        
        # BTTS recommendation
        if probabilities['btts_yes'] > probabilities['btts_no']:
            btts_rec = {
                'market': 'Both Teams to Score',
                'prediction': 'Yes',
                'probability': probabilities['btts_yes'],
                'fair_odds': 1 / probabilities['btts_yes'],
                'market_odds': market_odds.get('btts_yes', 1.75),
                'strength': 'Strong' if probabilities['btts_yes'] > 0.65 else 'Moderate' if probabilities['btts_yes'] > 0.55 else 'Weak'
            }
            recommendations.append(btts_rec)
        else:
            btts_rec = {
                'market': 'Both Teams to Score',
                'prediction': 'No',
                'probability': probabilities['btts_no'],
                'fair_odds': 1 / probabilities['btts_no'],
                'market_odds': 1 / (1 - 1/market_odds.get('btts_yes', 1.75)) if market_odds.get('btts_yes', 1.75) > 1 else 2.00,
                'strength': 'Strong' if probabilities['btts_no'] > 0.65 else 'Moderate' if probabilities['btts_no'] > 0.55 else 'Weak'
            }
            recommendations.append(btts_rec)
        
        return recommendations
    
    def predict(self, home_data, away_data):
        """Main prediction function."""
        self.reset()
        
        home_lambda, away_lambda = self.calculate_expected_goals(home_data, away_data)
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        probabilities, scoreline_probs, most_likely = self.calculate_probabilities(home_lambda, away_lambda)
        self.probabilities = probabilities
        self.scoreline_probs = scoreline_probs
        self.most_likely_score = most_likely
        
        self.confidence = self.calculate_confidence(home_lambda, away_lambda, home_data, away_data)
        self.key_factors = self.generate_key_factors(home_data, away_data, home_lambda, away_lambda)
        
        return {
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'probabilities': probabilities,
            'scorelines': {
                'most_likely': most_likely,
                'top_10': dict(sorted(scoreline_probs.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            'confidence': self.confidence,
            'key_factors': self.key_factors,
            'debug_info': self.debug_info,  # Add debug info to output
            'success': True
        }

# ============================================================================
# REST OF THE CODE REMAINS THE SAME
# ============================================================================

# [Data loading, UI components, and main function remain exactly as before]
# Only need to update the main function to show debug info

def main():
    # ... [Previous main function code remains exactly the same until prediction result display] ...
    
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        recommendations = st.session_state.get('recommendations', [])
        
        # ... [All previous display code remains the same] ...
        
        # Add debug info section
        if 'debug_info' in result and result['debug_info']:
            with st.expander("🔍 Debug Calculation Steps"):
                for debug_line in result['debug_info']:
                    st.code(debug_line)
        
        # ... [Rest of the display code remains the same] ...

# Run the app
if __name__ == "__main__":
    main()
