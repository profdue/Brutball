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
# PREDICTION ENGINE CORE - FINAL TIER-BASED VERSION
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
        self.debug_info = []
    
    def _get_tier_based_max_lambda(self, position, is_home):
        """Get tier-based maximum λ based on team position."""
        if position <= 3:  # Elite team
            if is_home:
                return 3.0
            else:
                return 2.5
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
                base_xg = home_xg_for / home_matches
            else:
                base_xg = self.league_params['avg_goals'] * 1.1
        else:
            away_xg_for = team_data.get('away_xg_for', 0)
            away_matches = team_data.get('matches_played', 1)
            if away_matches > 0:
                base_xg = away_xg_for / away_matches
            else:
                base_xg = self.league_params['avg_goals'] * 0.9
        
        self.debug_info.append(f"Step 1 {'Home' if is_home else 'Away'}: base_xg = {base_xg:.2f}")
        return base_xg
    
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
        if raw_ratio > 1.8:
            dampened_factor = 1.0 + (raw_ratio - 1.0) * 0.25
        elif raw_ratio > 1.4:
            dampened_factor = 1.0 + (raw_ratio - 1.0) * 0.5
        elif raw_ratio < 0.6:
            dampened_factor = 1.0 - (1.0 - raw_ratio) * 0.4
        elif raw_ratio < 0.8:
            dampened_factor = 1.0 - (1.0 - raw_ratio) * 0.6
        else:
            dampened_factor = raw_ratio ** 0.8
        
        dampened_factor = max(0.6, min(1.8, dampened_factor))
        
        self.debug_info.append(f"Step 2 {'Home' if is_home else 'Away'}: opp_defense={opp_defense:.2f}, raw_ratio={raw_ratio:.2f}, dampened_factor={dampened_factor:.2f}")
        return dampened_factor
    
    def _step3_recent_form_override(self, team_data, is_home):
        """STEP 3: Apply recent form trends with venue-aware calculation."""
        recent_goals_pg = team_data.get('goals_scored_last_5', 0) / 5
        
        matches_played = max(team_data.get('matches_played', 1), 1)
        
        if is_home:
            venue_xg = team_data.get('home_xg_for', 0)
        else:
            venue_xg = team_data.get('away_xg_for', 0)
        
        if matches_played > 0:
            venue_xg_pg = venue_xg / matches_played
        else:
            venue_xg_pg = self.league_params['avg_goals']
        
        if venue_xg_pg > 0:
            attack_trend = recent_goals_pg / venue_xg_pg
        else:
            attack_trend = 1.0
        
        position = team_data.get('overall_position', 10)
        
        # TIER-BASED FORM CAPS
        if position <= 3:
            trend_min = 0.8
            trend_max = 1.4
        elif position <= 6:
            trend_min = 0.75
            trend_max = 1.3
        else:
            trend_min = 0.7
            trend_max = 1.3
        
        attack_trend = max(trend_min, min(trend_max, attack_trend))
        
        self.debug_info.append(f"Step 3 {'Home' if is_home else 'Away'}: recent_goals={recent_goals_pg:.2f}, venue_xg_pg={venue_xg_pg:.2f}, raw_trend={recent_goals_pg/venue_xg_pg if venue_xg_pg>0 else 1.0:.2f}, final_trend={attack_trend:.2f}")
        return attack_trend
    
    def _step4_key_factor_adjustments(self, home_data, away_data):
        """STEP 4: Apply calibrated key factor adjustments."""
        adjustments = {'home': 1.0, 'away': 1.0}
        
        home_injury_impact = 1.0 - (home_data.get('defenders_out', 0) * 
                                   CONSTANTS['DEFENDER_INJURY_IMPACT'])
        away_injury_impact = 1.0 - (away_data.get('defenders_out', 0) * 
                                   CONSTANTS['DEFENDER_INJURY_IMPACT'])
        
        adjustments['home'] *= max(0.85, home_injury_impact)
        adjustments['away'] *= max(0.85, away_injury_impact)
        
        home_motivation = home_data.get('motivation', 3)
        away_motivation = away_data.get('motivation', 3)
        
        home_motivation_impact = CONSTANTS['MOTIVATION_BASE'] + (home_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        away_motivation_impact = CONSTANTS['MOTIVATION_BASE'] + (away_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        
        adjustments['home'] *= home_motivation_impact
        adjustments['away'] *= away_motivation_impact
        
        home_advantage = self.league_params['home_advantage'] * (
            1 + home_data.get('home_ppg_diff', 0) * 0.03
        )
        away_disadvantage = 2.0 - home_advantage
        
        adjustments['home'] *= home_advantage
        adjustments['away'] *= away_disadvantage
        
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
        
        home_goals_conceded = home_data.get('goals_conceded', 0)
        home_xga = home_data.get('home_xga', 0)
        if home_xga > 0 and home_goals_conceded / home_xga < 0.9:
            adjustments['away'] *= 0.98
        
        away_goals_conceded = away_data.get('goals_conceded', 0)
        away_xga = away_data.get('away_xga', 0)
        if away_xga > 0 and away_goals_conceded / away_xga < 0.9:
            adjustments['home'] *= 0.98
        
        self.debug_info.append(f"Step 4: Home adjustments={adjustments['home']:.2f}, Away adjustments={adjustments['away']:.2f}")
        return adjustments
    
    def _step5_final_calibration(self, home_lambda, away_lambda, home_data, away_data):
        """STEP 5: Tier-based final calibration with tier-based diff ratio caps."""
        home_position = home_data.get('overall_position', 10)
        away_position = away_data.get('overall_position', 10)
        
        max_home_lambda = self._get_tier_based_max_lambda(home_position, is_home=True)
        max_away_lambda = self._get_tier_based_max_lambda(away_position, is_home=False)
        
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], 
                         min(max_home_lambda, home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], 
                         min(max_away_lambda, away_lambda))
        
        self.debug_info.append(f"Step 5a: Home pos={home_position}, max_λ={max_home_lambda}, pre-cap_λ={home_lambda:.2f}")
        self.debug_info.append(f"Step 5a: Away pos={away_position}, max_λ={max_away_lambda}, pre-cap_λ={away_lambda:.2f}")
        
        total_lambda = home_lambda + away_lambda
        
        if home_position <= 3 and away_position >= 16:
            max_total = 5.0
        elif home_position <= 6 and away_position >= 14:
            max_total = 4.5
        else:
            max_total = 4.0
        
        if total_lambda > max_total:
            scale_factor = max_total / total_lambda
            home_lambda *= scale_factor
            away_lambda *= scale_factor
            self.debug_info.append(f"Step 5b: Scaled down, total_λ={total_lambda:.2f} > max={max_total}, scale={scale_factor:.2f}")
        elif total_lambda < 1.5:
            scale_factor = 1.5 / total_lambda
            home_lambda *= scale_factor
            away_lambda *= scale_factor
            self.debug_info.append(f"Step 5b: Scaled up, total_λ={total_lambda:.2f} < min=1.5, scale={scale_factor:.2f}")
        
        # TIER-BASED DIFF RATIO CAPS - FIXED VERSION
        diff_ratio = home_lambda / away_lambda if away_lambda > 0.1 else 6.0
        
        # Determine max diff ratio based on team tiers
        if home_position <= 3 and away_position >= 14:  # Elite vs weak
            max_diff_ratio = 6.0
        elif home_position <= 3 or away_position >= 16:  # Elite team or very weak opponent
            max_diff_ratio = 5.0
        elif home_position <= 6 and away_position >= 12:  # Strong vs weak
            max_diff_ratio = 4.5
        else:  # Normal matchups
            max_diff_ratio = 4.0
        
        if diff_ratio > max_diff_ratio:
            home_lambda = (home_lambda + away_lambda * max_diff_ratio) / (1 + max_diff_ratio)
            away_lambda = home_lambda / max_diff_ratio
            self.debug_info.append(f"Step 5c: Tier-based cap, was {diff_ratio:.2f}, max={max_diff_ratio}, now {home_lambda/away_lambda if away_lambda>0.1 else 'N/A':.2f}")
        
        self.debug_info.append(f"Step 5 Final: Home λ={home_lambda:.2f}, Away λ={away_lambda:.2f}")
        return round(home_lambda, 2), round(away_lambda, 2)
    
    def calculate_expected_goals(self, home_data, away_data):
        """Calculate expected goals with tier-based calibration."""
        self.debug_info = []
        
        home_base = self._step1_base_expected_goals(home_data, is_home=True)
        away_base = self._step1_base_expected_goals(away_data, is_home=False)
        
        home_opp_factor = self._step2_opponent_adjustment(home_data, away_data, is_home=True)
        away_opp_factor = self._step2_opponent_adjustment(away_data, home_data, is_home=False)
        
        home_lambda = home_base * home_opp_factor
        away_lambda = away_base * away_opp_factor
        
        home_trend = self._step3_recent_form_override(home_data, is_home=True)
        away_trend = self._step3_recent_form_override(away_data, is_home=False)
        
        home_lambda *= home_trend
        away_lambda *= away_trend
        
        key_factors = self._step4_key_factor_adjustments(home_data, away_data)
        home_lambda *= key_factors['home']
        away_lambda *= key_factors['away']
        
        home_lambda, away_lambda = self._step5_final_calibration(home_lambda, away_lambda, home_data, away_data)
        
        for debug_line in self.debug_info:
            self.key_factors.append(f"DEBUG: {debug_line}")
        
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
        
        scoreline_probs = {}
        max_goals = CONSTANTS['MAX_GOALS_CONSIDERED']
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = (stats.poisson.pmf(i, home_lambda) * 
                       stats.poisson.pmf(j, away_lambda))
                if prob > 0.001:
                    scoreline_probs[f"{i}-{j}"] = prob
        
        total_score_prob = sum(scoreline_probs.values())
        if total_score_prob > 0:
            scoreline_probs = {k: v/total_score_prob for k, v in scoreline_probs.items()}
        
        most_likely = max(scoreline_probs.items(), key=lambda x: x[1])[0] if scoreline_probs else "1-1"
        
        return probabilities, scoreline_probs, most_likely
    
    def calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """Calculate model confidence with tier consideration."""
        confidence = 50
        
        goal_diff = abs(home_lambda - away_lambda)
        confidence += goal_diff * 15
        
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 25
        elif pos_diff >= 5:
            confidence += 15
        else:
            confidence += pos_diff * 1.5
        
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        confidence += min(15, form_diff * 0.8)
        
        total_injuries = home_data.get('defenders_out', 0) + away_data.get('defenders_out', 0)
        confidence -= total_injuries * 2
        
        if self.league_params['goal_variance'] == 'high':
            confidence *= 0.97
        
        return round(max(30, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors for the prediction."""
        factors = []
        
        home_position = home_data['overall_position']
        away_position = away_data['overall_position']
        pos_diff = away_position - home_position
        
        if abs(pos_diff) >= 10:
            factors.append(f"Huge position difference: #{home_position} vs #{away_position}")
        elif abs(pos_diff) >= 5:
            factors.append(f"Significant position difference: #{home_position} vs #{away_position}")
        
        if home_position <= 3:
            factors.append(f"Elite home team: #{home_position} position")
        if away_position >= 16:
            factors.append(f"Struggling away team: #{away_position} position")
        
        if home_lambda > 2.5:
            factors.append(f"Extremely high home expected goals: {home_lambda:.2f}")
        elif home_lambda > 2.0:
            factors.append(f"Very high home expected goals: {home_lambda:.2f}")
        
        if away_lambda > 2.0:
            factors.append(f"Very high away expected goals: {away_lambda:.2f}")
        elif away_lambda > 1.5:
            factors.append(f"High away expected goals: {away_lambda:.2f}")
        
        home_xga_pg = home_data.get('home_xga', 0) / max(home_data.get('matches_played', 1), 1)
        away_xga_pg = away_data.get('away_xga', 0) / max(away_data.get('matches_played', 1), 1)
        
        if home_xga_pg < self.league_params['avg_goals'] * 0.8:
            factors.append(f"Strong home defense: {home_xga_pg:.2f} xGA/game")
        if away_xga_pg > self.league_params['avg_goals'] * 1.5:
            factors.append(f"Weak away defense: {away_xga_pg:.2f} xGA/game")
        
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        
        if home_recent > self.league_params['avg_goals'] * 1.5:
            factors.append(f"Home excellent recent scoring: {home_recent:.2f} goals/game")
        if away_recent < self.league_params['avg_goals'] * 0.5:
            factors.append(f"Away poor recent scoring: {away_recent:.2f} goals/game")
        
        if home_data.get('defenders_out', 0) >= 3:
            factors.append(f"Home defensive crisis: {home_data['defenders_out']} defenders out")
        if away_data.get('defenders_out', 0) >= 3:
            factors.append(f"Away defensive crisis: {away_data['defenders_out']} defenders out")
        
        return factors
    
    def get_market_recommendations(self, probabilities, market_odds):
        """Get market recommendations."""
        recommendations = []
        
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
        regular_factors = self.generate_key_factors(home_data, away_data, home_lambda, away_lambda)
        self.key_factors = self.key_factors + regular_factors
        
        return {
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'probabilities': probabilities,
            'scorelines': {
                'most_likely': most_likely,
                'top_10': dict(sorted(scoreline_probs.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            'confidence': self.confidence,
            'key_factors': self.key_factors,
            'success': True
        }

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

def load_league_data(league_name):
    """Load league data from GitHub with validation."""
    github_urls = {
        'LA LIGA': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/la_liga.csv',
        'PREMIER LEAGUE': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
    }
    
    url = github_urls.get(league_name.upper())
    if not url:
        st.error(f"League {league_name} not configured in the system")
        return None
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            st.error(f"❌ Data file not found for {league_name}")
            st.info(f"""
            **File not found:** `{url.split('/')[-1]}`
            
            To add {league_name} data:
            1. Go to your GitHub repository: https://github.com/profdue/Brutball
            2. Navigate to the `leagues` folder
            3. Upload a CSV file named `{league_name.lower().replace(' ', '_')}.csv`
            4. Ensure it has the EXACT same format
            
            **Required columns:**
            ```
            overall_position,team,venue,matches_played,home_xg_for,away_xg_for,goals,
            home_xga,away_xga,goals_conceded,home_xgdiff_def,away_xgdiff_def,defenders_out,
            form_last_5,motivation,open_play_pct,set_piece_pct,counter_attack_pct,form,
            shots_allowed_pg,home_ppg_diff,goals_scored_last_5,goals_conceded_last_5
            ```
            """)
            return None
        
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        available_cols = list(df.columns)
        
        if 'xg_for' in df.columns and 'home_xg_for' not in df.columns:
            st.info("⚠️ Using estimated home/away xG splits for La Liga data")
            
            for idx, row in df.iterrows():
                venue = row['venue']
                if venue == 'home':
                    df.at[idx, 'home_xg_for'] = row['xg_for'] * 0.55
                    df.at[idx, 'away_xg_for'] = 0
                    df.at[idx, 'home_xga'] = row.get('home_xga', row['xg_for'] * 0.8)
                    df.at[idx, 'away_xga'] = 0
                else:
                    df.at[idx, 'home_xg_for'] = 0
                    df.at[idx, 'away_xg_for'] = row['xg_for'] * 0.45
                    df.at[idx, 'home_xga'] = 0
                    df.at[idx, 'away_xga'] = row.get('away_xga', row['xg_for'] * 0.8)
        
        required_cols = [
            'overall_position', 'team', 'venue', 'matches_played', 'home_xg_for', 
            'away_xg_for', 'goals', 'home_xga', 'away_xga', 'goals_conceded',
            'defenders_out', 'form_last_5', 'motivation', 'open_play_pct', 
            'set_piece_pct', 'counter_attack_pct', 'form', 'shots_allowed_pg', 
            'home_ppg_diff', 'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"⚠️ Missing columns in {league_name} data: {', '.join(missing_cols)}")
            
            with st.expander("🔍 View Raw Data Structure"):
                st.write("**Original column names:**", original_columns)
                st.write("**Standardized column names:**", available_cols)
                st.write("**First 3 rows of data:**")
                st.dataframe(df.head(3))
            
            for col in missing_cols:
                if col not in df.columns:
                    df[col] = 0
            
        numeric_cols = ['matches_played', 'home_xg_for', 'away_xg_for', 'goals', 
                       'home_xga', 'away_xga', 'goals_conceded', 'defenders_out',
                       'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct', 
                       'counter_attack_pct', 'shots_allowed_pg', 'home_ppg_diff',
                       'goals_scored_last_5', 'goals_conceded_last_5']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].isna().any():
                    if col in ['home_xg_for', 'away_xg_for']:
                        df[col].fillna(1.0, inplace=True)
                    elif col in ['home_xga', 'away_xga', 'goals_conceded']:
                        df[col].fillna(1.5, inplace=True)
                    elif col == 'form_last_5':
                        df[col].fillna(5.0, inplace=True)
                    elif col == 'motivation':
                        df[col].fillna(3.0, inplace=True)
                    elif col == 'shots_allowed_pg':
                        df[col].fillna(12.0, inplace=True)
                    else:
                        df[col].fillna(0, inplace=True)
        
        st.success(f"✅ Successfully loaded {league_name} data ({len(df)} records)")
        
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load {league_name} data from GitHub: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing {league_name} data: {str(e)}")
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
# STREAMLIT UI COMPONENTS
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

def display_market_recommendation(rec):
    """Display market recommendation."""
    if rec['prediction'] in ['Over 2.5', 'Yes']:
        color = "#00b09b"
        icon = "📈"
    else:
        color = "#ff416c"
        icon = "📉"
    
    ev = (rec['market_odds'] / rec['fair_odds']) - 1
    ev_color = "green" if ev > 0 else "red"
    ev_text = f"+{ev:.1%}" if ev > 0 else f"{ev:.1%}"
    
    st.markdown(f"""
    <div style="background: {color}; border-radius: 15px; padding: 20px; margin: 15px 0; color: white;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 1.5em; font-weight: 600; margin-bottom: 10px;">
            {icon} {rec['market']}: {rec['prediction']}
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div>
                <div style="font-size: 0.9em; opacity: 0.8;">Probability</div>
                <div style="font-size: 1.3em; font-weight: 600;">{rec['probability']:.1%}</div>
            </div>
            <div>
                <div style="font-size: 0.9em; opacity: 0.8;">Fair Odds</div>
                <div style="font-size: 1.3em; font-weight: 600;">{rec['fair_odds']:.2f}</div>
            </div>
            <div>
                <div style="font-size: 0.9em; opacity: 0.8;">Market Odds</div>
                <div style="font-size: 1.3em; font-weight: 600;">{rec['market_odds']:.2f}</div>
            </div>
            <div>
                <div style="font-size: 0.9em; opacity: 0.8;">Expected Value</div>
                <div style="font-size: 1.3em; font-weight: 600; color: {ev_color};">{ev_text}</div>
            </div>
        </div>
        <div style="font-size: 1em; text-align: center; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
            Strength: {rec['strength']}
        </div>
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
    st.set_page_config(
        page_title="Advanced Football Prediction Engine",
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
    .stButton > button:hover {
        background: linear-gradient(135deg, #44A08D, #4ECDC4);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Advanced Football Prediction Engine</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">FIXED TIER-BASED CALIBRATION</p>', 
                unsafe_allow_html=True)
    
    if 'league_data' not in st.session_state:
        st.session_state.league_data = None
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None
    
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        available_leagues = ['LA LIGA', 'PREMIER LEAGUE']
        selected_league = st.selectbox("Choose League:", available_leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Load Data")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data..."):
                df = load_league_data(selected_league)
                if df is not None:
                    st.session_state.league_data = df
                    st.session_state.selected_league = selected_league
                    
                    with st.expander(f"📊 {selected_league} Data Preview"):
                        st.dataframe(df.head(), use_container_width=True)
                        st.metric("Total Records", len(df))
                        st.metric("Unique Teams", len(df['team'].unique()))
                else:
                    st.error(f"Failed to load {selected_league} data")
        
        if selected_league in LEAGUE_PARAMS:
            st.markdown("---")
            st.markdown("### 📈 League Parameters")
            params = LEAGUE_PARAMS[selected_league]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Goals", f"{params['avg_goals']:.2f}")
            with col2:
                st.metric("Home Advantage", f"{params['home_advantage']:.2f}")
        
        st.markdown("---")
        st.markdown("### 🔧 FIXED CALIBRATION")
        st.success("""
        **Tier-based improvements:**
        • Tier-based diff ratio caps
        • Elite teams: max ratio 6.0
        • Strong teams: max ratio 5.0
        • Better elite team handling
        """)
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        st.markdown("""
        ### 🚀 FIXED CALIBRATION:
        
        **Improved tier-based diff caps:**
        - Elite vs weak: ratio ≤ 6.0
        - Elite team or very weak: ratio ≤ 5.0
        - Strong vs weak: ratio ≤ 4.5
        - Normal: ratio ≤ 4.0
        
        **Fixes Real Madrid λ issue**
        """)
        return
    
    df = st.session_state.league_data
    selected_league = st.session_state.selected_league
    league_params = LEAGUE_PARAMS[selected_league]
    
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
                st.metric("Home xG/Game", f"{home_row['home_xg_for']/home_row['matches_played']:.2f}")
                st.metric("Home xGA/Game", f"{home_row['home_xga']/home_row['matches_played']:.2f}")
            with col2a:
                st.metric("Recent Goals/Game", f"{home_row['goals_scored_last_5']/5:.1f}")
                st.metric("Recent Conceded/Game", f"{home_row['goals_conceded_last_5']/5:.1f}")
    
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
                st.metric("Away xG/Game", f"{away_row['away_xg_for']/away_row['matches_played']:.2f}")
                st.metric("Away xGA/Game", f"{away_row['away_xga']/away_row['matches_played']:.2f}")
            with col2b:
                st.metric("Recent Goals/Game", f"{away_row['goals_scored_last_5']/5:.1f}")
                st.metric("Recent Conceded/Game", f"{away_row['goals_conceded_last_5']/5:.1f}")
    
    market_odds = display_market_odds_interface()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Run Advanced Prediction", type="primary", use_container_width=True):
            if home_team == away_team:
                st.error("Please select different teams for home and away.")
                return
            
            try:
                home_data = prepare_team_data(df, home_team, 'home')
                away_data = prepare_team_data(df, away_team, 'away')
                
                engine = FootballPredictionEngine(league_params)
                
                with st.spinner("Running fixed analysis..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    result = engine.predict(home_data, away_data)
                    
                    if result['success']:
                        recommendations = engine.get_market_recommendations(result['probabilities'], market_odds)
                        
                        st.session_state.prediction_result = result
                        st.session_state.prediction_engine = engine
                        st.session_state.recommendations = recommendations
                        st.success("✅ Fixed analysis complete!")
                    else:
                        st.error("Prediction failed")
            
            except ValueError as e:
                st.error(f"Data error: {str(e)}")
                st.info("Please ensure both teams have data for the selected venue.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
    
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        recommendations = st.session_state.get('recommendations', [])
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
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
        
        st.markdown("### 🎯 Match Probabilities")
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
        
        score_prob = result['scorelines']['top_10'].get(result['scorelines']['most_likely'], 0) * 100
        display_prediction_box(
            "🎯 Most Likely Score",
            result['scorelines']['most_likely'],
            f"Probability: {score_prob:.1f}%"
        )
        
        st.markdown("### 📊 Total Goals Market")
        col1, col2 = st.columns(2)
        with col1:
            display_prediction_box(
                "Over 2.5 Goals",
                f"{result['probabilities']['over_25']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['over_25']:.2f}",
                color="#00b09b" if result['probabilities']['over_25'] > 0.5 else "#4ECDC4"
            )
        with col2:
            display_prediction_box(
                "Under 2.5 Goals",
                f"{result['probabilities']['under_25']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['under_25']:.2f}",
                color="#ff416c" if result['probabilities']['under_25'] > 0.5 else "#4ECDC4"
            )
        
        st.markdown("### ⚽ Both Teams to Score")
        col1, col2 = st.columns(2)
        with col1:
            display_prediction_box(
                "BTTS - Yes",
                f"{result['probabilities']['btts_yes']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['btts_yes']:.2f}",
                color="#00b09b" if result['probabilities']['btts_yes'] > 0.5 else "#4ECDC4"
            )
        with col2:
            display_prediction_box(
                "BTTS - No",
                f"{result['probabilities']['btts_no']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['btts_no']:.2f}",
                color="#ff416c" if result['probabilities']['btts_no'] > 0.5 else "#4ECDC4"
            )
        
        if recommendations:
            st.markdown("### 💰 Market Recommendations")
            for rec in recommendations:
                display_market_recommendation(rec)
        
        confidence = result['confidence']
        confidence_color = "#00b09b" if confidence >= 70 else "#f7971e" if confidence >= 50 else "#ff416c"
        st.markdown(f"""
        <div style="background: {confidence_color}; border-radius: 15px; padding: 20px; margin: 15px 0; color: white;">
            <h3 style="text-align: center; margin: 0;">🤖 Model Confidence: {confidence:.1f}%</h3>
            <p style="text-align: center; margin: 5px 0 0 0;">
                {'High Confidence' if confidence >= 70 else 'Medium Confidence' if confidence >= 50 else 'Low Confidence'}
                • Based on {CONSTANTS['POISSON_SIMULATIONS']:,} simulations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if result['key_factors']:
            st.markdown("### 🔑 Key Factors & Debug Info")
            cols = st.columns(2)
            for idx, factor in enumerate(result['key_factors']):
                with cols[idx % 2]:
                    if factor.startswith("DEBUG:"):
                        bg_color = "rgba(255,255,0,0.1)"
                        border_color = "#FFD700"
                    else:
                        bg_color = "rgba(255,107,107,0.1)"
                        border_color = "#FF6B6B"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; border-radius: 10px; padding: 10px; 
                                margin: 5px 0; border-left: 4px solid {border_color};">
                        <span style="color: #333; font-weight: 500;">{factor}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Scoreline Probability Distribution")
        
        if result['scorelines']['top_10']:
            scoreline_df = pd.DataFrame(
                list(result['scorelines']['top_10'].items())[:10],
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
        
        with st.expander("📋 View Raw Prediction Data"):
            st.json(result)

if __name__ == "__main__":
    main()
