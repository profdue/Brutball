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
# LEAGUE-SPECIFIC PARAMETERS - FINAL CALIBRATED VERSION
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
    'MIN_HOME_LAMBDA': 0.7,    # BALANCED: was 0.6, original was 0.8
    'MIN_AWAY_LAMBDA': 0.6,    # BALANCED: was 0.5, original was 0.6
    'DEFENDER_INJURY_IMPACT': 0.04,  # BALANCED: was 0.05, original was 0.03
    'SET_PIECE_THRESHOLD': 0.15,
    'COUNTER_ATTACK_THRESHOLD': 0.15,
    'MOTIVATION_BASE': 0.95,
    'MOTIVATION_INCREMENT': 0.02,
}

# ============================================================================
# PREDICTION ENGINE - FINAL CALIBRATED VERSION
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
    
    def _calculate_context_aware_trend(self, team_data, is_home):
        """Calculate trend considering BOTH attacking and defensive context."""
        recent_goals_pg = team_data.get('goals_scored_last_5', 0) / 5
        recent_conceded_pg = team_data.get('goals_conceded_last_5', 0) / 5
        
        matches_played = max(team_data.get('matches_played', 1), 1)
        
        if is_home:
            venue_xg = team_data.get('home_xg_for', 0)
            venue_xga = team_data.get('home_xga', 0)
        else:
            venue_xg = team_data.get('away_xg_for', 0)
            venue_xga = team_data.get('away_xga', 0)
        
        venue_xg_pg = venue_xg / matches_played if matches_played > 0 else self.league_params['avg_goals']
        venue_xga_pg = venue_xga / matches_played if matches_played > 0 else self.league_params['avg_goals']
        
        # ATTACKING TREND
        if venue_xg_pg > 0:
            attack_trend = recent_goals_pg / venue_xg_pg
        else:
            attack_trend = 1.0
        
        # DEFENSIVE CONTEXT (NEW)
        if venue_xga_pg > 0:
            defense_ratio = recent_conceded_pg / venue_xga_pg
        else:
            defense_ratio = 1.0
        
        position = team_data.get('overall_position', 10)
        
        # CONTEXT-AWARE TREND ADJUSTMENT
        if attack_trend < 0.5:  # Severely underperforming attack
            if defense_ratio < 0.7:  # But strong defense recently
                # Team focusing on defense - less penalty
                context_factor = 0.8
            elif defense_ratio > 1.3:  # And weak defense
                # Team in complete crisis - more penalty
                context_factor = 1.2
            else:
                context_factor = 1.0
        else:
            context_factor = 1.0
        
        # Apply context factor
        adjusted_trend = attack_trend * context_factor
        
        # POSITION-AWARE CAPS (LESS PUNITIVE)
        if position <= 3:  # Elite teams
            min_trend = 0.6  # Was 0.8 original, 0.4 fixed
            max_trend = 1.4  # Was 1.4 original, 1.4 fixed
        elif position <= 6:  # Top teams
            min_trend = 0.55
            max_trend = 1.3
        elif position >= 16:  # Bottom teams
            min_trend = 0.45  # Less punitive than 0.4
            max_trend = 1.2
        else:  # Mid-table
            min_trend = 0.5
            max_trend = 1.25
        
        # Special case: 0 goals but strong defense
        if recent_goals_pg == 0 and defense_ratio < 0.6:
            min_trend = 0.4  # Allow even lower for defensive teams
        
        final_trend = max(min_trend, min(max_trend, adjusted_trend))
        
        self.debug_info.append(f"Trend {'Home' if is_home else 'Away'}: attack={attack_trend:.2f}, defense_ratio={defense_ratio:.2f}, context={context_factor:.2f}, final={final_trend:.2f}")
        return final_trend
    
    def _step1_base_expected_goals(self, team_data, is_home):
        """STEP 1: Base expected goals."""
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
        """STEP 2: Opponent defense adjustment."""
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
        
        # CALIBRATED DAMPENING
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
        
        self.debug_info.append(f"Step 2 {'Home' if is_home else 'Away'}: opp_defense={opp_defense:.2f}, raw_ratio={raw_ratio:.2f}, factor={dampened_factor:.2f}")
        return dampened_factor
    
    def _step3_recent_form_override(self, team_data, is_home):
        """STEP 3: Context-aware form adjustment."""
        return self._calculate_context_aware_trend(team_data, is_home)
    
    def _step4_key_factor_adjustments(self, home_data, away_data):
        """STEP 4: Key factor adjustments with BALANCED home advantage."""
        adjustments = {'home': 1.0, 'away': 1.0}
        
        home_position = home_data.get('overall_position', 10)
        away_position = away_data.get('overall_position', 10)
        
        # BALANCED HOME ADVANTAGE
        if home_position <= 3:  # Elite home
            home_adv = self.league_params['home_advantage'] * 1.08  # Balanced
        elif home_position >= 16:  # Weak home
            home_adv = 1.08  # Minimal advantage
        else:  # Normal home
            home_adv = self.league_params['home_advantage']
        
        # AWAY TEAM CONTEXT
        if away_position <= 6:  # Strong away
            away_factor = 1.12  # Good boost
        elif away_position >= 16:  # Weak away
            away_factor = 0.92  # Small penalty
        else:
            away_factor = 1.0
        
        adjustments['home'] *= home_adv
        adjustments['away'] *= (2.0 - home_adv) * away_factor
        
        # DEFENSIVE INJURIES (BALANCED)
        home_defenders = home_data.get('defenders_out', 0)
        away_defenders = away_data.get('defenders_out', 0)
        
        if home_defenders >= 4:
            home_injury = 1.0 - (0.04 * home_defenders * 1.2)
        elif home_defenders >= 2:
            home_injury = 1.0 - (0.04 * home_defenders)
        else:
            home_injury = 1.0 - (0.03 * home_defenders)
        
        if away_defenders >= 4:
            away_injury = 1.0 - (0.04 * away_defenders * 1.2)
        elif away_defenders >= 2:
            away_injury = 1.0 - (0.04 * away_defenders)
        else:
            away_injury = 1.0 - (0.03 * away_defenders)
        
        adjustments['home'] *= max(0.8, home_injury)
        adjustments['away'] *= max(0.8, away_injury)
        
        # MOTIVATION
        home_motivation = home_data.get('motivation', 3)
        away_motivation = away_data.get('motivation', 3)
        
        home_mot = CONSTANTS['MOTIVATION_BASE'] + (home_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        away_mot = CONSTANTS['MOTIVATION_BASE'] + (away_motivation * CONSTANTS['MOTIVATION_INCREMENT'])
        
        adjustments['home'] *= home_mot
        adjustments['away'] *= away_mot
        
        self.debug_info.append(f"Step 4: Home adj={adjustments['home']:.2f}, Away adj={adjustments['away']:.2f}")
        return adjustments
    
    def _step5_final_calibration(self, home_lambda, away_lambda, home_data, away_data, home_trend, away_trend):
        """STEP 5: Final calibration with DRAW AWARENESS."""
        home_position = home_data.get('overall_position', 10)
        away_position = away_data.get('overall_position', 10)
        
        # MAX λ BASED ON POSITION AND FORM
        def get_max_lambda(position, is_home, trend):
            if position <= 3:
                base = 3.2 if is_home else 2.6
            elif position <= 6:
                base = 2.8 if is_home else 2.3
            elif position <= 12:
                base = 2.4 if is_home else 1.9
            else:
                base = 2.1 if is_home else 1.6
            
            # Form adjustment (less aggressive)
            if trend < 0.6:
                form_mult = 0.85 + (trend - 0.4) * 0.75  # 0.4→0.85, 0.6→1.0
            else:
                form_mult = 1.0
            
            return base * form_mult
        
        max_home = get_max_lambda(home_position, True, home_trend)
        max_away = get_max_lambda(away_position, False, away_trend)
        
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], min(max_home, home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], min(max_away, away_lambda))
        
        self.debug_info.append(f"Step 5a: Home max={max_home:.1f}, Away max={max_away:.1f}")
        
        # DRAW CALIBRATION - CRITICAL FIX
        pos_diff = abs(home_position - away_position)
        total_lambda = home_lambda + away_lambda
        
        # Close matchups → increase draw probability
        if pos_diff <= 4:
            # Reduce goal difference for closer matches
            goal_diff = abs(home_lambda - away_lambda)
            if goal_diff > 0.8:
                # Bring closer together
                avg = (home_lambda + away_lambda) / 2
                home_lambda = avg + (home_lambda - avg) * 0.6
                away_lambda = avg + (away_lambda - avg) * 0.6
                self.debug_info.append(f"Step 5b: Close matchup (diff={pos_diff}), reduced goal difference")
        
        # Low total goals expected → higher draw chance
        expected_total = self.league_params['avg_total_goals']
        if total_lambda < expected_total * 0.7:
            # Already low-scoring, good for draws
            pass
        elif total_lambda > expected_total * 1.5:
            # High-scoring, slightly reduce for more realistic draws
            scale = (expected_total * 1.3) / total_lambda
            home_lambda *= scale
            away_lambda *= scale
            self.debug_info.append(f"Step 5c: High total λ={total_lambda:.2f}, scaled by {scale:.2f}")
        
        # FINAL ROUNDING
        home_lambda = round(home_lambda, 2)
        away_lambda = round(away_lambda, 2)
        
        self.debug_info.append(f"Step 5 Final: Home λ={home_lambda:.2f}, Away λ={away_lambda:.2f}")
        return home_lambda, away_lambda
    
    def calculate_expected_goals(self, home_data, away_data):
        """Calculate expected goals with balanced calibration."""
        self.debug_info = []
        
        home_base = self._step1_base_expected_goals(home_data, is_home=True)
        away_base = self._step1_base_expected_goals(away_data, is_home=False)
        
        home_opp = self._step2_opponent_adjustment(home_data, away_data, is_home=True)
        away_opp = self._step2_opponent_adjustment(away_data, home_data, is_home=False)
        
        home_lambda = home_base * home_opp
        away_lambda = away_base * away_opp
        
        home_trend = self._step3_recent_form_override(home_data, is_home=True)
        away_trend = self._step3_recent_form_override(away_data, is_home=False)
        
        home_lambda *= home_trend
        away_lambda *= away_trend
        
        adjustments = self._step4_key_factor_adjustments(home_data, away_data)
        home_lambda *= adjustments['home']
        away_lambda *= adjustments['away']
        
        home_lambda, away_lambda = self._step5_final_calibration(
            home_lambda, away_lambda, home_data, away_data, home_trend, away_trend
        )
        
        for debug_line in self.debug_info:
            self.key_factors.append(f"DEBUG: {debug_line}")
        
        return home_lambda, away_lambda
    
    def calculate_probabilities(self, home_lambda, away_lambda):
        """Calculate probabilities."""
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
        
        # Scoreline probabilities
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
        """Calculate confidence with form consistency."""
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
        
        # Form consistency check
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        home_xg_pg = home_data.get('home_xg_for', 0) / max(home_data.get('matches_played', 1), 1)
        home_form_ratio = home_recent / home_xg_pg if home_xg_pg > 0 else 1.0
        
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        away_xg_pg = away_data.get('away_xg_for', 0) / max(away_data.get('matches_played', 1), 1)
        away_form_ratio = away_recent / away_xg_pg if away_xg_pg > 0 else 1.0
        
        # Teams performing as expected increase confidence
        form_consistency = (min(1.0, home_form_ratio) + min(1.0, away_form_ratio)) / 2
        confidence += (form_consistency - 0.8) * 20  # 0.8 baseline
        
        total_injuries = home_data.get('defenders_out', 0) + away_data.get('defenders_out', 0)
        confidence -= total_injuries * 2.5
        
        if self.league_params['goal_variance'] == 'high':
            confidence *= 0.97
        
        return round(max(30, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors."""
        factors = []
        
        home_pos = home_data['overall_position']
        away_pos = away_data['overall_position']
        pos_diff = abs(home_pos - away_pos)
        
        if pos_diff >= 10:
            factors.append(f"Huge position gap: #{home_pos} vs #{away_pos}")
        elif pos_diff >= 5:
            factors.append(f"Significant position gap: #{home_pos} vs #{away_pos}")
        
        if home_pos <= 3:
            factors.append(f"Elite home team")
        if away_pos <= 6:
            factors.append(f"Strong away team")
        
        # Form analysis
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        home_xg_pg = home_data.get('home_xg_for', 0) / max(home_data.get('matches_played', 1), 1)
        if home_xg_pg > 0 and home_recent / home_xg_pg < 0.6:
            factors.append(f"Home poor recent form: {home_recent:.1f} goals/game")
        
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        away_xg_pg = away_data.get('away_xg_for', 0) / max(away_data.get('matches_played', 1), 1)
        if away_xg_pg > 0 and away_recent / away_xg_pg < 0.6:
            factors.append(f"Away poor recent form: {away_recent:.1f} goals/game")
        
        # Defensive analysis
        home_xga = home_data.get('home_xga', 0) / max(home_data.get('matches_played', 1), 1)
        away_xga = away_data.get('away_xga', 0) / max(away_data.get('matches_played', 1), 1)
        
        if home_xga < self.league_params['avg_goals'] * 0.8:
            factors.append(f"Strong home defense")
        if away_xga > self.league_params['avg_goals'] * 1.5:
            factors.append(f"Weak away defense")
        
        # Injury crisis
        if home_data.get('defenders_out', 0) >= 3:
            factors.append(f"Home defensive issues: {home_data['defenders_out']} defenders out")
        if away_data.get('defenders_out', 0) >= 3:
            factors.append(f"Away defensive issues: {away_data['defenders_out']} defenders out")
        
        return factors
    
    def get_market_recommendations(self, probabilities, market_odds):
        """Get market recommendations."""
        recommendations = []
        
        # Total Goals
        if probabilities['over_25'] > probabilities['under_25']:
            rec = {
                'market': 'Total Goals',
                'prediction': 'Over 2.5',
                'probability': probabilities['over_25'],
                'fair_odds': 1 / probabilities['over_25'],
                'market_odds': market_odds.get('over_25', 1.85),
                'strength': 'Strong' if probabilities['over_25'] > 0.65 else 'Moderate' if probabilities['over_25'] > 0.55 else 'Weak'
            }
        else:
            rec = {
                'market': 'Total Goals',
                'prediction': 'Under 2.5',
                'probability': probabilities['under_25'],
                'fair_odds': 1 / probabilities['under_25'],
                'market_odds': 1 / (1 - 1/market_odds.get('over_25', 1.85)) if market_odds.get('over_25', 1.85) > 1 else 2.00,
                'strength': 'Strong' if probabilities['under_25'] > 0.65 else 'Moderate' if probabilities['under_25'] > 0.55 else 'Weak'
            }
        recommendations.append(rec)
        
        # BTTS
        if probabilities['btts_yes'] > probabilities['btts_no']:
            rec = {
                'market': 'Both Teams to Score',
                'prediction': 'Yes',
                'probability': probabilities['btts_yes'],
                'fair_odds': 1 / probabilities['btts_yes'],
                'market_odds': market_odds.get('btts_yes', 1.75),
                'strength': 'Strong' if probabilities['btts_yes'] > 0.65 else 'Moderate' if probabilities['btts_yes'] > 0.55 else 'Weak'
            }
        else:
            rec = {
                'market': 'Both Teams to Score',
                'prediction': 'No',
                'probability': probabilities['btts_no'],
                'fair_odds': 1 / probabilities['btts_no'],
                'market_odds': 1 / (1 - 1/market_odds.get('btts_yes', 1.75)) if market_odds.get('btts_yes', 1.75) > 1 else 2.00,
                'strength': 'Strong' if probabilities['btts_no'] > 0.65 else 'Moderate' if probabilities['btts_no'] > 0.55 else 'Weak'
            }
        recommendations.append(rec)
        
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
# DATA LOADING & UI FUNCTIONS (UNCHANGED)
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
        
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Handle missing columns
        required_cols = [
            'overall_position', 'team', 'venue', 'matches_played', 'home_xg_for', 
            'away_xg_for', 'goals', 'home_xga', 'away_xga', 'goals_conceded',
            'defenders_out', 'form_last_5', 'motivation', 'open_play_pct', 
            'set_piece_pct', 'counter_attack_pct', 'form', 'shots_allowed_pg', 
            'home_ppg_diff', 'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        # Convert numeric
        numeric_cols = ['matches_played', 'home_xg_for', 'away_xg_for', 'goals', 
                       'home_xga', 'away_xga', 'goals_conceded', 'defenders_out',
                       'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct', 
                       'counter_attack_pct', 'shots_allowed_pg', 'home_ppg_diff',
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
# STREAMLIT UI (UNCHANGED FROM PREVIOUS VERSION)
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
        page_title="Football Prediction Engine - FINAL",
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
    
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Football Prediction Engine</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">FINAL CALIBRATED VERSION</p>', 
                unsafe_allow_html=True)
    
    if 'league_data' not in st.session_state:
        st.session_state.league_data = None
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None
    
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
        st.markdown("### 🎯 FINAL CALIBRATION")
        st.success("""
        **Balanced approach:**
        • Context-aware form analysis
        • Defensive performance considered
        • Higher draw probabilities
        • Less punitive poor-form caps
        • Better away team recognition
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Expected Improvements")
        st.info("""
        **For test matches:**
        1. Higher draw probabilities
        2. Better Real Oviedo prediction
        3. More balanced xG distributions
        4. Context-aware adjustments
        """)
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        st.markdown("""
        ### 🎯 FINAL CALIBRATION STRATEGY:
        
        **Key improvements:**
        1. **Context-aware form**: Considers defensive performance
        2. **Balanced caps**: Less punitive for poor form
        3. **Draw awareness**: Higher draw probabilities for close matchups
        4. **Injury impact**: Graduated (minor/moderate/crisis)
        5. **Away recognition**: Strong away teams get proper boost
        
        **Expected to fix:**
        • 0-0 predictions for defensively strong teams
        • Underestimated draw probabilities  
        • Over-punitive poor form adjustments
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
                home_xg = home_row['home_xg_for']/home_row['matches_played'] if home_row['matches_played'] > 0 else 0
                st.metric("Home xG/Game", f"{home_xg:.2f}")
            with col2a:
                recent_goals = home_row['goals_scored_last_5']/5
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
                st.metric("Recent Goals/Game", f"{recent_goals:.1f}")
    
    market_odds = display_market_odds_interface()
    
    if st.button("🚀 Run Final Calibrated Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams.")
            return
        
        try:
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            engine = FootballPredictionEngine(league_params)
            
            with st.spinner("Running calibrated analysis..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                result = engine.predict(home_data, away_data)
                
                if result['success']:
                    recommendations = engine.get_market_recommendations(result['probabilities'], market_odds)
                    
                    st.session_state.prediction_result = result
                    st.session_state.recommendations = recommendations
                    st.success("✅ Calibrated analysis complete!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
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
        
        if recommendations:
            st.markdown("### 💰 Market Recommendations")
            for rec in recommendations:
                display_market_recommendation(rec)
        
        st.markdown(f"""
        <div style="background: #4ECDC4; border-radius: 15px; padding: 20px; margin: 15px 0; color: white;">
            <h3 style="text-align: center; margin: 0;">🤖 Model Confidence: {result['confidence']:.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
