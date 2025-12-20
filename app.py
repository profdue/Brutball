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
# LEAGUE-SPECIFIC PARAMETERS - CALIBRATED VERSION
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'avg_goals': 1.26,
        'avg_shots': 12.3,
        'home_advantage': 1.18,
        'goal_variance': 'medium',
        'draw_rate': 0.28,
        'avg_total_goals': 2.52
    },
    'PREMIER LEAGUE': {
        'avg_goals': 1.42,
        'avg_shots': 12.7,
        'home_advantage': 1.18,
        'goal_variance': 'high',
        'draw_rate': 0.25,
        'avg_total_goals': 2.84
    }
}

CONSTANTS = {
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 6,
    'MIN_HOME_LAMBDA': 0.5,
    'MIN_AWAY_LAMBDA': 0.4,
}

# ============================================================================
# REFINED PROFESSIONAL PREDICTION ENGINE (With Explainability)
# ============================================================================

class RefinedFootballPredictor:
    """
    Second-order refinement after calibration
    Fixes: Mid-range scoring slumps, overconfidence, context-aware probabilities
    Now with: Explainability layer for decisions
    """
    
    def __init__(self, league_params):
        self.league_params = league_params
        self.reset()
    
    def reset(self):
        self.debug_info = []
        self.key_factors = []
        self.scoring_insights = []
        self.calibration_notes = []
        self.explanations = {
            'over_under': [],
            'btts': [],
            'confidence': []
        }
    
    # ==================== REFINED CORE LOGIC ====================
    
    def _calculate_position_factor(self, position):
        """Calibrated position factor"""
        if position <= 3:
            return 1.25
        elif position <= 6:
            return 1.15
        elif position <= 12:
            return 1.05
        elif position <= 16:
            return 0.95
        else:
            return 0.85
    
    def _calculate_true_strength(self, team_data, is_home):
        """
        CALIBRATED: Team Strength with realistic position factor
        """
        # Get venue-specific xG
        if is_home:
            base_xg = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        else:
            base_xg = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        
        position = team_data.get('overall_position', 20)
        
        # CALIBRATED: Use realistic position factor
        position_factor = self._calculate_position_factor(position)
        
        # xG efficiency: Actual goals vs xG
        total_goals = team_data.get('goals', 0)
        total_xg = team_data.get('xg', 0)
        efficiency = total_goals / total_xg if total_xg > 0 else 1.0
        
        # True strength = Base xG × Position × Efficiency
        true_strength = base_xg * position_factor * efficiency
        
        self.debug_info.append(f"True Strength ({'Home' if is_home else 'Away'}): base_xg={base_xg:.2f}, pos_factor={position_factor:.2f}, efficiency={efficiency:.2f}, strength={true_strength:.2f}")
        
        return true_strength
    
    def _adjust_for_recent_scoring(self, team_data, base_lambda, is_home):
        """
        REFINED: Proper penalties for mid-range scoring slumps
        0.0 goals → ×0.50 (crisis)
        0.1-0.4 → ×0.70 (very poor)
        0.5-0.9 → ×0.85 (poor but not crisis) ← NEW
        1.0-1.4 → ×0.95 (slightly below average)
        1.5+ → ×1.05-1.30 (good to excellent)
        """
        recent_goals = team_data.get('goals_scored_last_5', 0) / 5
        historical_avg = team_data.get('goals', 0) / max(team_data.get('matches_played', 1), 1)
        
        # Calculate performance ratio
        if historical_avg > 0:
            performance_ratio = recent_goals / historical_avg
        else:
            performance_ratio = 1.0
        
        # REFINED ADJUSTMENT MATRIX
        if recent_goals == 0:
            adjustment = 0.50  # Scoring crisis
            self.calibration_notes.append(f"{'Home' if is_home else 'Away'} scoring crisis: 0 goals in last 5 (-50% penalty)")
        
        elif recent_goals < 0.5:
            adjustment = 0.70  # Very poor
            self.calibration_notes.append(f"{'Home' if is_home else 'Away'} very poor scoring: {recent_goals:.1f} goals/game (-30% penalty)")
        
        elif recent_goals < 1.0:
            # MID-RANGE SLUMP: 0.5-0.9 goals/game
            if performance_ratio < 0.6:
                adjustment = 0.80  # Severely underperforming vs historical
                self.calibration_notes.append(f"{'Home' if is_home else 'Away'} severe slump: {recent_goals:.1f} goals/game ({performance_ratio:.0%} of historical, -20% penalty)")
            elif performance_ratio < 0.8:
                adjustment = 0.85  # Moderately underperforming
                self.calibration_notes.append(f"{'Home' if is_home else 'Away'} scoring slump: {recent_goals:.1f} goals/game ({performance_ratio:.0%} of historical, -15% penalty)")
            else:
                adjustment = 0.90  # Slightly underperforming
                self.calibration_notes.append(f"{'Home' if is_home else 'Away'} slight slump: {recent_goals:.1f} goals/game ({performance_ratio:.0%} of historical, -10% penalty)")
        
        elif recent_goals < 1.5:
            adjustment = 0.95  # Slightly below average
        
        elif recent_goals < 2.0:
            adjustment = 1.05  # Good form
            self.calibration_notes.append(f"{'Home' if is_home else 'Away'} good scoring form: {recent_goals:.1f} goals/game (+5% boost)")
        
        elif recent_goals < 2.5:
            adjustment = 1.15  # Very good form
            self.calibration_notes.append(f"{'Home' if is_home else 'Away'} very good scoring form: {recent_goals:.1f} goals/game (+15% boost)")
        
        else:
            adjustment = 1.30  # Excellent form
            self.calibration_notes.append(f"{'Home' if is_home else 'Away'} excellent scoring: {recent_goals:.1f} goals/game (+30% boost)")
        
        adjusted_lambda = base_lambda * adjustment
        
        self.debug_info.append(f"Recent Scoring Adjust ({'Home' if is_home else 'Away'}): recent={recent_goals:.1f}, hist={historical_avg:.1f}, ratio={performance_ratio:.2f}, adjustment={adjustment:.2f}, before={base_lambda:.2f}, after={adjusted_lambda:.2f}")
        
        return adjusted_lambda
    
    def _calculate_home_advantage(self, home_data, away_data):
        """Calibrated home advantage"""
        home_ppg_diff = home_data.get('home_ppg_diff', 0)
        home_position = home_data.get('overall_position', 10)
        
        # Base advantage
        base = self.league_params['home_advantage']
        if home_position >= 16:
            base = 1.05
        
        # Adjust by ppg_diff (capped)
        ppg_adjustment = 1.0 + (min(1.0, max(-0.5, home_ppg_diff)) * 0.1)
        final_advantage = base * ppg_adjustment
        
        # Strong away teams reduce advantage
        if away_data.get('overall_position', 10) <= 6:
            final_advantage *= 0.9
        
        return max(1.02, min(1.35, final_advantage))
    
    def _calculate_btts_probability(self, home_data, away_data):
        """REFINED: Better BTTS logic with explanations"""
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        
        # Start with base probability
        base = 0.5
        self.explanations['btts'].append(f"Base probability: 50% (neutral prior)")
        
        # CALIBRATED: Recent scoring is CRITICAL
        if home_recent == 0:
            base -= 0.3
            self.explanations['btts'].append(f"Home scoring crisis: 0 goals in last 5 → -30%")
        elif home_recent < 0.5:
            base -= 0.15
            self.explanations['btts'].append(f"Home poor recent scoring: {home_recent:.1f} goals/game → -15%")
        
        if away_recent == 0:
            base -= 0.3
            self.explanations['btts'].append(f"Away scoring crisis: 0 goals in last 5 → -30%")
        elif away_recent < 0.5:
            base -= 0.15
            self.explanations['btts'].append(f"Away poor recent scoring: {away_recent:.1f} goals/game → -15%")
        
        # Position gap
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff > 10:
            base -= 0.2
            self.explanations['btts'].append(f"Big position gap (#{home_data['overall_position']} vs #{away_data['overall_position']}) → often one-sided → -20%")
        
        # Both teams scoring well recently → increase
        if home_recent > 1.5 and away_recent > 1.0:
            base += 0.2
            self.explanations['btts'].append(f"Both teams scoring well recently → +20%")
        
        # Add openness factor based on expected goals
        home_expected = home_data.get('home_xg_for', 0) / max(home_data.get('matches_played', 1), 1)
        away_expected = away_data.get('away_xg_for', 0) / max(away_data.get('matches_played', 1), 1)
        
        if home_expected > 1.2 and away_expected > 1.2:
            base += 0.05
            self.explanations['btts'].append(f"Both teams create good chances (Home xG: {home_expected:.1f}, Away xG: {away_expected:.1f}) → +5%")
        
        # Add match total factor
        total_expected = home_expected + away_expected
        if total_expected > 3.0:
            base += 0.05
            self.explanations['btts'].append(f"High expected goal total ({total_expected:.1f}) → +5%")
        
        # Apply bounds
        btts_prob = max(0.1, min(0.9, base))
        
        # Add final explanation if near neutral
        if 0.45 <= btts_prob <= 0.55:
            self.explanations['btts'].append("Insufficient strong signals → staying near neutral (50%)")
        
        self.debug_info.append(f"BTTS Probability: home_recent={home_recent:.1f}, away_recent={away_recent:.1f}, base={base:.2f}, final={btts_prob:.2f}")
        
        return btts_prob
    
    # ==================== REFINED CONFIDENCE CALCULATION ====================
    
    def _calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """
        REFINED: Better confidence scores with explanations
        Reduce confidence when:
        1. Both teams poor recent scoring
        2. Bottom teams involved
        3. High variance situations
        """
        confidence = 50
        self.explanations['confidence'].append(f"Base confidence: 50%")
        
        # Goal difference (still important)
        goal_diff = abs(home_lambda - away_lambda)
        confidence += goal_diff * 15
        self.explanations['confidence'].append(f"Goal expectation difference: {goal_diff:.2f} → +{goal_diff * 15:.1f}%")
        
        # Position difference
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 25
            self.explanations['confidence'].append(f"Huge position gap (#{home_data['overall_position']} vs #{away_data['overall_position']}) → +25%")
        elif pos_diff >= 5:
            confidence += 15
            self.explanations['confidence'].append(f"Significant position gap (#{home_data['overall_position']} vs #{away_data['overall_position']}) → +15%")
        
        # REFINEMENT: Recent scoring consistency penalty
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        home_avg = home_data.get('goals', 0) / max(home_data.get('matches_played', 1), 1)
        home_consistency = home_recent / home_avg if home_avg > 0 else 1.0
        
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        away_avg = away_data.get('goals', 0) / max(away_data.get('matches_played', 1), 1)
        away_consistency = away_recent / away_avg if away_avg > 0 else 1.0
        
        # Penalty for teams severely underperforming
        consistency_penalty = 0
        if home_consistency < 0.6:
            consistency_penalty += 10
            self.explanations['confidence'].append(f"Home severely underperforming: {home_consistency:.0%} of historical → -10%")
        if away_consistency < 0.6:
            consistency_penalty += 10
            self.explanations['confidence'].append(f"Away severely underperforming: {away_consistency:.0%} of historical → -10%")
        
        # Penalty for bottom teams (high variance)
        if home_data['overall_position'] >= 16 or away_data['overall_position'] >= 16:
            consistency_penalty += 5
            self.explanations['confidence'].append(f"Bottom teams involved → higher variance → -5%")
        
        confidence -= consistency_penalty
        
        # Apply reasonable bounds with explanation
        if confidence > 70:
            self.explanations['confidence'].append(f"High confidence: Clear signals in match analysis")
        elif confidence < 40:
            self.explanations['confidence'].append(f"Low confidence: Many uncertainties in this matchup")
        
        return round(max(30, min(85, confidence)), 1)
    
    # ==================== REFINED SCORING PATTERN PREDICTION ====================
    
    def _predict_scoring_patterns(self, home_data, away_data, home_lambda, away_lambda):
        """REFINED: Better Over/Under probabilities with explanations"""
        total_lambda = home_lambda + away_lambda
        
        # Get recent scoring context
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        home_avg = home_data.get('goals', 0) / max(home_data.get('matches_played', 1), 1)
        away_avg = away_data.get('goals', 0) / max(away_data.get('matches_played', 1), 1)
        
        # Base probability from Poisson
        if total_lambda <= 1.8:
            base_over = 0.25
            self.explanations['over_under'].append(f"Low total λ ({total_lambda:.2f}) → Base Over: 25%")
        elif total_lambda <= 2.2:
            base_over = 0.40
            self.explanations['over_under'].append(f"Moderate total λ ({total_lambda:.2f}) → Base Over: 40%")
        elif total_lambda <= 2.6:
            base_over = 0.55
            self.explanations['over_under'].append(f"Good total λ ({total_lambda:.2f}) → Base Over: 55%")
        elif total_lambda <= 3.0:
            base_over = 0.70
            self.explanations['over_under'].append(f"High total λ ({total_lambda:.2f}) → Base Over: 70%")
        else:
            base_over = 0.85
            self.explanations['over_under'].append(f"Very high total λ ({total_lambda:.2f}) → Base Over: 85%")
        
        # REFINEMENT: Adjust for recent scoring context
        recent_adjustment = 1.0
        
        # If both teams scoring poorly recently, reduce Over probability
        if home_recent < 1.0 and away_recent < 1.0:
            recent_adjustment *= 0.8  # -20% for poor scoring
            self.explanations['over_under'].append(f"Both teams poor recent scoring (Home: {home_recent:.1f}, Away: {away_recent:.1f}) → -20%")
        
        # If both teams scoring well recently, increase Over probability
        if home_recent > 1.5 and away_recent > 1.5:
            recent_adjustment *= 1.2  # +20% for good scoring
            self.explanations['over_under'].append(f"Both teams good recent scoring (Home: {home_recent:.1f}, Away: {away_recent:.1f}) → +20%")
        
        # Add joint finishing suppression (your insight)
        home_ratio = home_recent / home_avg if home_avg > 0 else 1.0
        away_ratio = away_recent / away_avg if away_avg > 0 else 1.0
        
        if home_ratio < 0.7 and away_ratio < 0.7:
            recent_adjustment *= 0.85  # Both teams finishing poorly
            self.explanations['over_under'].append(f"Both teams finishing below 70% of historical (Home: {home_ratio:.0%}, Away: {away_ratio:.0%}) → -15%")
        elif home_ratio < 0.7 or away_ratio < 0.7:
            recent_adjustment *= 0.92  # One team finishing poorly
            team = "Home" if home_ratio < 0.7 else "Away"
            ratio = home_ratio if home_ratio < 0.7 else away_ratio
            self.explanations['over_under'].append(f"{team} team finishing below 70% of historical ({ratio:.0%}) → -8%")
        
        final_over = base_over * recent_adjustment
        final_over = max(0.15, min(0.90, final_over))  # Keep within bounds
        
        # Add final explanation
        if final_over > 0.7:
            self.explanations['over_under'].append(f"Strong Over expectation: High total goals expected")
        elif final_over < 0.4:
            self.explanations['over_under'].append(f"Strong Under expectation: Low total goals expected")
        else:
            self.explanations['over_under'].append(f"Balanced expectation: Moderate goal expectation")
        
        # BTTS probability (already refined)
        btts_prob = self._calculate_btts_probability(home_data, away_data)
        
        return {
            'predicted_total': total_lambda,
            'over_25_prob': final_over,
            'under_25_prob': 1 - final_over,
            'btts_prob': btts_prob,
            'btts_no_prob': 1 - btts_prob,
        }
    
    # ==================== SUPPORTING METHODS ====================
    
    def _assess_injury_impact(self, home_data, away_data):
        """Calibrated injury impact"""
        def calculate_impact(defenders_out, is_home):
            if defenders_out == 0:
                return 1.0
            elif defenders_out <= 2:
                return 1.0 - (defenders_out * 0.04)  # 4% per defender
            elif defenders_out <= 4:
                return 0.92 - ((defenders_out - 2) * 0.06)  # 6% for 3-4
            else:  # Crisis (5+)
                return 0.80 - ((defenders_out - 4) * 0.08)  # 8% for 5+
        
        home_impact = calculate_impact(home_data.get('defenders_out', 0), is_home=True)
        away_impact = calculate_impact(away_data.get('defenders_out', 0), is_home=False)
        
        return {'home': home_impact, 'away': away_impact}
    
    def _assess_form_with_context(self, home_data, away_data):
        """Calibrated form assessment"""
        def calculate_form(team_data, is_home):
            recent_goals = team_data.get('goals_scored_last_5', 0) / 5
            recent_conceded = team_data.get('goals_conceded_last_5', 0) / 5
            
            # Historical averages
            if is_home:
                hist_goals = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
            else:
                hist_goals = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
            
            hist_conceded = team_data.get('goals_conceded', 0) / max(team_data.get('matches_played', 1), 1)
            
            # Attack form ratio (calibrated)
            if hist_goals > 0:
                attack_form = recent_goals / hist_goals
            else:
                attack_form = 1.0
            
            # Defense form ratio
            if recent_conceded > 0:
                defense_form = hist_conceded / recent_conceded
            else:
                defense_form = 1.5  # Excellent recent defense
            
            # Combined with caps
            combined = (attack_form + defense_form) / 2
            return max(0.5, min(1.5, combined))
        
        return {
            'home': calculate_form(home_data, is_home=True),
            'away': calculate_form(away_data, is_home=False)
        }
    
    def _analyze_style_matchup(self, home_data, away_data):
        """Style matchup analysis"""
        adjustments = {'home': 1.0, 'away': 1.0}
        
        # Simple style adjustments (can be enhanced with more data)
        home_open = home_data.get('open_play_pct', 0) / 100
        away_counter = away_data.get('counter_attack_pct', 0) / 100
        
        if home_open > 0.65 and away_counter > 0.2:
            adjustments['away'] *= 1.10  # Counter opportunities
        
        return adjustments
    
    def _final_calibration(self, home_lambda, away_lambda, home_data, away_data):
        """Final calibration with realistic constraints"""
        # Minimum values
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], home_lambda)
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], away_lambda)
        
        # Reasonable maximums
        home_lambda = min(3.0, home_lambda)
        away_lambda = min(2.5, away_lambda)
        
        # Ensure reasonable total
        total = home_lambda + away_lambda
        if total > 4.5:
            scale = 4.5 / total
            home_lambda *= scale
            away_lambda *= scale
            self.calibration_notes.append(f"Total goals capped: was {total:.2f}, scaled by {scale:.2f}")
        
        return round(home_lambda, 2), round(away_lambda, 2)
    
    def _calculate_probabilities(self, home_lambda, away_lambda):
        """Calculate match outcome probabilities"""
        simulations = CONSTANTS['POISSON_SIMULATIONS']
        
        np.random.seed(42)
        home_goals = np.random.poisson(home_lambda, simulations)
        away_goals = np.random.poisson(away_lambda, simulations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        return {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations
        }
    
    def _generate_key_factors(self, home_data, away_data, home_lambda, away_lambda, scoring_prediction):
        """Generate key factors"""
        factors = []
        
        home_pos = home_data['overall_position']
        away_pos = away_data['overall_position']
        pos_diff = abs(home_pos - away_pos)
        
        if pos_diff >= 10:
            factors.append(f"Huge position gap: #{home_pos} vs #{away_pos}")
        elif pos_diff >= 5:
            factors.append(f"Significant position gap: #{home_pos} vs #{away_pos}")
        
        # Recent scoring factors
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        home_avg = home_data.get('goals', 0) / max(home_data.get('matches_played', 1), 1)
        away_avg = away_data.get('goals', 0) / max(away_data.get('matches_played', 1), 1)
        
        if home_recent == 0:
            factors.append("Home not scoring recently (0 goals in last 5)")
        elif home_recent < 0.5:
            factors.append(f"Home very poor recent scoring: {home_recent:.1f} goals/game")
        elif home_recent < 1.0 and home_avg > 0:
            ratio = home_recent / home_avg
            factors.append(f"Home scoring slump: {home_recent:.1f} goals/game ({ratio:.0%} of historical average)")
        
        if away_recent == 0:
            factors.append("Away not scoring recently (0 goals in last 5)")
        elif away_recent < 0.5:
            factors.append(f"Away very poor recent scoring: {away_recent:.1f} goals/game")
        elif away_recent < 1.0 and away_avg > 0:
            ratio = away_recent / away_avg
            factors.append(f"Away scoring slump: {away_recent:.1f} goals/game ({ratio:.0%} of historical average)")
        
        # Expected goals factors
        if home_lambda > 2.0:
            factors.append(f"High home expected goals: {home_lambda:.2f}")
        if away_lambda > 1.8:
            factors.append(f"High away expected goals: {away_lambda:.2f}")
        
        return factors
    
    # ==================== MAIN PREDICTION METHOD ====================
    
    def predict_match(self, home_data, away_data):
        """Main prediction with all refinements"""
        self.reset()
        
        # 1. TRUE STRENGTH (with calibrated position factor)
        home_strength = self._calculate_true_strength(home_data, is_home=True)
        away_strength = self._calculate_true_strength(away_data, is_home=False)
        
        # 2. REFINED RECENT SCORING ADJUSTMENT
        home_strength = self._adjust_for_recent_scoring(home_data, home_strength, is_home=True)
        away_strength = self._adjust_for_recent_scoring(away_data, away_strength, is_home=False)
        
        # 3. OTHER FACTORS
        injury_impact = self._assess_injury_impact(home_data, away_data)
        form_context = self._assess_form_with_context(home_data, away_data)
        style_analysis = self._analyze_style_matchup(home_data, away_data)
        home_advantage = self._calculate_home_advantage(home_data, away_data)
        
        # INTEGRATE ALL FACTORS
        home_lambda = home_strength
        away_lambda = away_strength
        
        # Apply adjustments
        adjustments = [
            ('Injury', injury_impact['home'], injury_impact['away']),
            ('Form', form_context['home'], form_context['away']),
            ('Style', style_analysis['home'], style_analysis['away']),
            ('Home/away', home_advantage, 2.0 - home_advantage),
        ]
        
        for name, home_adj, away_adj in adjustments:
            home_lambda *= home_adj
            away_lambda *= away_adj
            self.debug_info.append(f"{name}: Home ×{home_adj:.2f}, Away ×{away_adj:.2f}")
        
        # FINAL CALIBRATION
        home_lambda, away_lambda = self._final_calibration(home_lambda, away_lambda, home_data, away_data)
        
        # REFINED SCORING PREDICTIONS
        scoring_prediction = self._predict_scoring_patterns(home_data, away_data, home_lambda, away_lambda)
        
        # CALCULATE PROBABILITIES
        probabilities = self._calculate_probabilities(home_lambda, away_lambda)
        
        # REFINED CONFIDENCE SCORE
        confidence = self._calculate_confidence(home_lambda, away_lambda, home_data, away_data)
        
        # GENERATE KEY FACTORS
        key_factors = self._generate_key_factors(home_data, away_data, home_lambda, away_lambda, scoring_prediction)
        
        # COMBINE ALL INFO
        all_info = self.calibration_notes + self.debug_info + [f"Final: Home λ={home_lambda:.2f}, Away λ={away_lambda:.2f}, Total={home_lambda+away_lambda:.2f}"]
        
        return {
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'probabilities': probabilities,
            'scoring_analysis': scoring_prediction,
            'confidence': confidence,
            'key_factors': key_factors + all_info,
            'explanations': self.explanations,
            'success': True
        }

# ============================================================================
# DATA LOADING & UI (UPDATED WITH EXPLANATIONS)
# ============================================================================

def load_league_data(league_name):
    """Load league data from GitHub."""
    github_urls = {
        'LA LIGA': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/la_liga.csv',
        'PREMIER LEAGUE': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
    }
    
    url = github_urls.get(league_name.upper())
    if not url:
        st.error(f"League {league_name} not configured")
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Handle column name variations
        column_mapping = {
            'games_played': 'matches_played',
            'xg_for': 'xg'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
        
        # Ensure required columns exist
        required = ['overall_position', 'team', 'venue', 'matches_played', 
                   'home_xg_for', 'away_xg_for', 'goals', 'xg',
                   'home_xga', 'away_xga', 'goals_conceded', 'defenders_out',
                   'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct',
                   'counter_attack_pct', 'form', 'shots_allowed_pg', 'home_ppg_diff',
                   'goals_scored_last_5', 'goals_conceded_last_5']
        
        for col in required:
            if col not in df.columns:
                df[col] = 0
        
        # Convert numeric columns
        numeric_cols = ['matches_played', 'home_xg_for', 'away_xg_for', 'goals', 'xg',
                       'home_xga', 'away_xga', 'goals_conceded', 'defenders_out',
                       'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct',
                       'counter_attack_pct', 'form', 'shots_allowed_pg', 'home_ppg_diff',
                       'goals_scored_last_5', 'goals_conceded_last_5']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col].fillna(0, inplace=True)
        
        st.success(f"✅ Loaded {league_name} data ({len(df)} records)")
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def prepare_team_data(df, team_name, venue):
    """Prepare team data for prediction."""
    team_data = df[(df['team'] == team_name) & (df['venue'] == venue.lower())]
    
    if team_data.empty:
        team_data = df[(df['team'].str.lower() == team_name.lower()) & 
                      (df['venue'] == venue.lower())]
    
    if team_data.empty:
        raise ValueError(f"No data found for {team_name} at {venue} venue")
    
    return team_data.iloc[0].to_dict()

# ============================================================================
# STREAMLIT UI COMPONENTS (UPDATED WITH EXPLANATIONS)
# ============================================================================

def display_prediction_box(title, value, subtitle="", color="#4ECDC4"):
    """Display prediction in styled box."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}, rgba(78,205,196,0.9));
                border-radius: 15px; padding: 20px; margin: 15px 0; color: white;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 1.2em; text-align: center; opacity: 0.9;">{title}</div>
        <div style="font-size: 2.5em; font-weight: 800; margin: 10px 0; text-align: center;">{value}</div>
        <div style="font-size: 1.2em; text-align: center; opacity: 0.9;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_scoring_analysis(analysis, explanations=None):
    """Display scoring pattern analysis with explanations."""
    st.markdown("### ⚽ Scoring Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        over_color = "#00b09b" if analysis['over_25_prob'] > 0.5 else "#4ECDC4"
        display_prediction_box(
            "Over 2.5 Goals",
            f"{analysis['over_25_prob']*100:.1f}%",
            f"Fair odds: {1/analysis['over_25_prob']:.2f}" if analysis['over_25_prob'] > 0 else "N/A",
            over_color
        )
    
    with col2:
        under_color = "#ff416c" if analysis['under_25_prob'] > 0.5 else "#4ECDC4"
        display_prediction_box(
            "Under 2.5 Goals",
            f"{analysis['under_25_prob']*100:.1f}%",
            f"Fair odds: {1/analysis['under_25_prob']:.2f}" if analysis['under_25_prob'] > 0 else "N/A",
            under_color
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        btts_yes_color = "#00b09b" if analysis['btts_prob'] > 0.5 else "#4ECDC4"
        display_prediction_box(
            "BTTS - Yes",
            f"{analysis['btts_prob']*100:.1f}%",
            f"Fair odds: {1/analysis['btts_prob']:.2f}" if analysis['btts_prob'] > 0 else "N/A",
            btts_yes_color
        )
    
    with col4:
        btts_no_color = "#ff416c" if analysis['btts_no_prob'] > 0.5 else "#4ECDC4"
        display_prediction_box(
            "BTTS - No",
            f"{analysis['btts_no_prob']*100:.1f}%",
            f"Fair odds: {1/analysis['btts_no_prob']:.2f}" if analysis['btts_no_prob'] > 0 else "N/A",
            btts_no_color
        )
    
    # Display explanations if available
    if explanations:
        st.markdown("#### 📝 Analysis Reasoning")
        
        with st.expander("🔍 Over/Under 2.5 Goals Logic"):
            if 'over_under' in explanations and explanations['over_under']:
                for explanation in explanations['over_under']:
                    st.write(f"• {explanation}")
            else:
                st.info("No specific over/under reasoning available.")
        
        with st.expander("🔍 Both Teams to Score (BTTS) Logic"):
            if 'btts' in explanations and explanations['btts']:
                for explanation in explanations['btts']:
                    st.write(f"• {explanation}")
            else:
                st.info("No specific BTTS reasoning available.")

def display_confidence_breakdown(confidence, explanations=None):
    """Display confidence score with breakdown."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4ECDC4, #44A08D);
                border-radius: 15px; padding: 20px; margin: 15px 0; color: white;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <h3 style="text-align: center; margin: 0;">🤖 Model Confidence: {confidence:.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if explanations and 'confidence' in explanations:
        with st.expander("🔍 Confidence Breakdown"):
            for explanation in explanations['confidence']:
                st.write(f"• {explanation}")

def display_validation_metrics():
    """Display validation tracking metrics."""
    st.markdown("---")
    st.markdown("## 📊 Model Performance Tracking")
    
    # Initialize session state for tracking
    if 'performance_history' not in st.session_state:
        st.session_state.performance_history = []
    
    if 'validation_mode' not in st.session_state:
        st.session_state.validation_mode = False
    
    # Toggle validation mode
    st.session_state.validation_mode = st.checkbox("📝 Enable Prediction Tracking", value=st.session_state.validation_mode)
    
    if st.session_state.validation_mode:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Track This Prediction", use_container_width=True):
                if 'prediction_result' in st.session_state:
                    # Store prediction with timestamp
                    result = st.session_state.prediction_result
                    track_data = {
                        'timestamp': pd.Timestamp.now(),
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_xg': result['expected_goals']['home'],
                        'away_xg': result['expected_goals']['away'],
                        'home_win_prob': result['probabilities']['home_win'],
                        'draw_prob': result['probabilities']['draw'],
                        'away_win_prob': result['probabilities']['away_win'],
                        'over_prob': result['scoring_analysis']['over_25_prob'],
                        'confidence': result['confidence']
                    }
                    st.session_state.performance_history.append(track_data)
                    st.success("✅ Prediction tracked!")
        
        with col2:
            if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
                st.session_state.performance_history = []
                st.success("History cleared!")
        
        # Show history if exists
        if st.session_state.performance_history:
            df_history = pd.DataFrame(st.session_state.performance_history)
            
            # Calculate some metrics
            avg_confidence = df_history['confidence'].mean()
            avg_total_goals = (df_history['home_xg'] + df_history['away_xg']).mean()
            avg_over_prob = df_history['over_prob'].mean()
            
            st.markdown("### 📈 Tracking Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Predictions", len(df_history))
            with col2:
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
            with col3:
                st.metric("Avg Expected Total", f"{avg_total_goals:.2f}")
            with col4:
                st.metric("Avg Over Probability", f"{avg_over_prob:.1%}")
            
            # Show recent predictions
            st.markdown("### 📋 Recent Predictions")
            st.dataframe(df_history.tail(5))
    else:
        st.info("Enable prediction tracking to monitor model performance over time.")

def main():
    st.set_page_config(
        page_title="Professional Football Predictor",
        page_icon="⚽",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #4ECDC4, #44A08D);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
    }
    
    .stExpander {
        border: 1px solid #4ECDC4;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Professional Football Predictor</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">With Explainable AI & Performance Tracking</p>', 
                unsafe_allow_html=True)
    
    if 'league_data' not in st.session_state:
        st.session_state.league_data = None
    
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        leagues = ['LA LIGA', 'PREMIER LEAGUE']
        selected_league = st.selectbox("Choose League:", leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Load Data")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data..."):
                df = load_league_data(selected_league)
                if df is not None:
                    st.session_state.league_data = df
                    st.session_state.selected_league = selected_league
                else:
                    st.error(f"Failed to load {selected_league} data")
        
        st.markdown("---")
        st.markdown("### 🔧 Model Features")
        st.success("""
        **Professional Features:**
        1. **Explainable AI** - Full reasoning chain
        2. **Confidence Breakdown** - Why 50% vs 80%?
        3. **Performance Tracking** - Monitor predictions
        4. **Edge Case Handling** - Crises, slumps, elite teams
        5. **Market-Ready Outputs** - Fair odds & probabilities
        """)
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        return
    
    df = st.session_state.league_data
    selected_league = st.session_state.selected_league
    league_params = LEAGUE_PARAMS[selected_league]
    
    # Make home_team and away_team available globally
    global home_team, away_team
    
    st.markdown("## 🏟️ Match Setup")
    available_teams = sorted(df['team'].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 Home Team:", available_teams, key="home_team")
        home_stats = df[(df['team'] == home_team) & (df['venue'] == 'home')]
        if not home_stats.empty:
            home_row = home_stats.iloc[0]
            st.markdown(f"**{home_team} Home Stats:**")
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("Position", f"#{int(home_row['overall_position'])}")
                home_xg = home_row['home_xg_for']/home_row['matches_played'] if home_row['matches_played'] > 0 else 0
                st.metric("Home xG/Game", f"{home_xg:.2f}")
            with col2a:
                recent_goals = home_row['goals_scored_last_5']/5
                hist_avg = home_row['goals']/home_row['matches_played'] if home_row['matches_played'] > 0 else 0
                if hist_avg > 0:
                    ratio = recent_goals / hist_avg
                    st.metric("Recent Goals/Game", f"{recent_goals:.1f}", f"{ratio:.0%} of historical")
                else:
                    st.metric("Recent Goals/Game", f"{recent_goals:.1f}")
    
    with col2:
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options, key="away_team")
        away_stats = df[(df['team'] == away_team) & (df['venue'] == 'away')]
        if not away_stats.empty:
            away_row = away_stats.iloc[0]
            st.markdown(f"**{away_team} Away Stats:**")
            col1b, col2b = st.columns(2)
            with col1b:
                st.metric("Position", f"#{int(away_row['overall_position'])}")
                away_xg = away_row['away_xg_for']/away_row['matches_played'] if away_row['matches_played'] > 0 else 0
                st.metric("Away xG/Game", f"{away_xg:.2f}")
            with col2b:
                recent_goals = away_row['goals_scored_last_5']/5
                hist_avg = away_row['goals']/away_row['matches_played'] if away_row['matches_played'] > 0 else 0
                if hist_avg > 0:
                    ratio = recent_goals / hist_avg
                    st.metric("Recent Goals/Game", f"{recent_goals:.1f}", f"{ratio:.0%} of historical")
                else:
                    st.metric("Recent Goals/Game", f"{recent_goals:.1f}")
    
    if st.button("🚀 Run Professional Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams.")
            return
        
        try:
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            predictor = RefinedFootballPredictor(league_params)
            
            with st.spinner("Running professional analysis..."):
                result = predictor.predict_match(home_data, away_data)
                
                if result['success']:
                    st.session_state.prediction_result = result
                    st.success("✅ Professional analysis complete!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.session_state.get('prediction_result'):
        result = st.session_state.prediction_result
        
        st.markdown("---")
        st.markdown("# 📊 Professional Analysis Results")
        
        st.markdown("### 🎯 Expected Goals (Calibrated)")
        col1, col2 = st.columns(2)
        with col1:
            display_prediction_box(
                f"🏠 {home_team} Expected Goals",
                f"{result['expected_goals']['home']:.2f}",
                "λ (Poisson mean)"
            )
        with col2:
            display_prediction_box(
                f"✈️ {away_team} Expected Goals",
                f"{result['expected_goals']['away']:.2f}",
                "λ (Poisson mean)"
            )
        
        st.markdown("### 📈 Match Outcome Probabilities")
        col1, col2, col3 = st.columns(3)
        with col1:
            display_prediction_box(
                f"🏠 {home_team} Win",
                f"{result['probabilities']['home_win']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['home_win']:.2f}"
            )
        with col2:
            display_prediction_box(
                "Draw",
                f"{result['probabilities']['draw']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['draw']:.2f}"
            )
        with col3:
            display_prediction_box(
                f"✈️ {away_team} Win",
                f"{result['probabilities']['away_win']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['away_win']:.2f}"
            )
        
        # Display scoring analysis with explanations
        display_scoring_analysis(result['scoring_analysis'], result.get('explanations', {}))
        
        # Display confidence breakdown
        display_confidence_breakdown(result['confidence'], result.get('explanations', {}))
        
        # Display key factors
        if result['key_factors']:
            st.markdown("### 🔑 Key Analytical Factors")
            for factor in result['key_factors']:
                if "scoring crisis" in str(factor).lower() or "severe slump" in str(factor).lower():
                    st.error(f"⚡ {factor}")
                elif "slump" in str(factor).lower() or "underperforming" in str(factor).lower():
                    st.warning(f"⚠️ {factor}")
                elif "boost" in str(factor).lower() or "excellent" in str(factor).lower():
                    st.success(f"📈 {factor}")
                elif "Calibration" in str(factor) or "confidence" in str(factor):
                    st.info(f"🎯 {factor}")
                elif "DEBUG" in str(factor):
                    continue  # Hide debug info now that we have explanations
                else:
                    st.success(f"• {factor}")
        
        # Display validation metrics
        display_validation_metrics()

if __name__ == "__main__":
    main()
