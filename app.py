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
# LEAGUE-SPECIFIC PARAMETERS
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
    'MIN_HOME_LAMBDA': 0.7,
    'MIN_AWAY_LAMBDA': 0.6,
}

# ============================================================================
# PROFESSIONAL PREDICTION ENGINE
# ============================================================================

class ProfessionalFootballPredictor:
    """
    Implements: Underlying performance + squad context + tactical fit
    Focuses on: Total goals patterns + team scoring
    """
    
    def __init__(self, league_params):
        self.league_params = league_params
        self.reset()
    
    def reset(self):
        self.debug_info = []
        self.key_factors = []
        self.scoring_insights = []
    
    # ==================== CORE PROFESSIONAL LOGIC ====================
    
    def _calculate_true_strength(self, team_data, is_home):
        """
        PRIORITY 1: Team Strength (True Performance Level)
        Uses xG efficiency with position for true strength
        """
        # Get venue-specific xG
        if is_home:
            base_xg = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        else:
            base_xg = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        
        position = team_data.get('overall_position', 20)
        
        # Position factor: Better position = higher strength
        position_factor = 1.0 + ((21 - position) * 0.05)  # #1 = 2.0, #20 = 1.05
        
        # xG efficiency: Actual goals vs xG
        total_goals = team_data.get('goals', 0)
        total_xg = team_data.get('xg', 0)  # Note: using 'xg' column from CSV
        efficiency = total_goals / total_xg if total_xg > 0 else 1.0
        
        # True strength = Base xG × Position × Efficiency
        true_strength = base_xg * position_factor * efficiency
        
        self.debug_info.append(f"True Strength ({'Home' if is_home else 'Away'}): base_xg={base_xg:.2f}, pos={position}, pos_factor={position_factor:.2f}, efficiency={efficiency:.2f}, strength={true_strength:.2f}")
        
        return true_strength
    
    def _assess_injury_impact(self, home_data, away_data):
        """
        PRIORITY 2: Team News & Squad Availability
        Defender injuries with context awareness
        """
        home_defenders = home_data.get('defenders_out', 0)
        away_defenders = away_data.get('defenders_out', 0)
        
        # Graduated impact
        def calculate_impact(defenders_out, is_home):
            if defenders_out == 0:
                return 1.0
            elif defenders_out <= 2:
                impact = 1.0 - (defenders_out * 0.04)  # 4% per defender
            elif defenders_out <= 4:
                impact = 0.92 - ((defenders_out - 2) * 0.06)  # 6% for 3-4
            else:  # Crisis (5+)
                impact = 0.80 - ((defenders_out - 4) * 0.08)  # 8% for 5+
            
            # Away teams suffer more
            if not is_home:
                impact *= 0.95
            
            return max(0.6, impact)
        
        home_impact = calculate_impact(home_defenders, is_home=True)
        away_impact = calculate_impact(away_defenders, is_home=False)
        
        self.debug_info.append(f"Injury Impact: Home={home_impact:.2f} ({home_defenders} def out), Away={away_impact:.2f} ({away_defenders} def out)")
        
        return {'home': home_impact, 'away': away_impact}
    
    def _analyze_style_matchup(self, home_data, away_data):
        """
        PRIORITY 3: Tactical Matchup
        Uses open_play_pct, set_piece_pct, counter_attack_pct
        """
        home_open = home_data.get('open_play_pct', 0) / 100
        home_set = home_data.get('set_piece_pct', 0) / 100
        home_counter = home_data.get('counter_attack_pct', 0) / 100
        
        away_open = away_data.get('open_play_pct', 0) / 100
        away_set = away_data.get('set_piece_pct', 0) / 100
        away_counter = away_data.get('counter_attack_pct', 0) / 100
        
        adjustments = {'home': 1.0, 'away': 1.0}
        insights = []
        
        # OPEN PLAY DOMINANCE vs COUNTER ATTACK
        if home_open > 0.65 and away_counter > 0.2:
            adjustments['away'] *= 1.15  # Counter opportunities
            insights.append("Home dominates possession, away strong on counters → away scoring chances")
        
        # SET PIECE ADVANTAGE
        set_piece_diff = home_set - away_set
        if abs(set_piece_diff) > 0.15:
            if set_piece_diff > 0:
                adjustments['home'] *= 1.10
                insights.append(f"Home set piece advantage: +{set_piece_diff*100:.0f}%")
            else:
                adjustments['away'] *= 1.10
                insights.append(f"Away set piece advantage: +{abs(set_piece_diff)*100:.0f}%")
        
        # COUNTER ATTACK OPPORTUNITIES
        if away_counter > 0.25:
            home_shots_allowed = home_data.get('shots_allowed_pg', 12)
            if home_shots_allowed > 14:  # Home allows many shots
                adjustments['away'] *= 1.12
                insights.append(f"Away counters vs home defensive weakness ({home_shots_allowed} shots allowed/game)")
        
        # Add tactical insights to scoring insights
        if insights:
            self.scoring_insights.extend(insights)
        
        self.debug_info.append(f"Style Matchup: Home adj={adjustments['home']:.2f}, Away adj={adjustments['away']:.2f}")
        
        return adjustments
    
    def _assess_form_with_context(self, home_data, away_data):
        """
        PRIORITY 4: Recent Form (With Context)
        Recent vs historical, adjusted for position
        """
        def calculate_form(team_data, is_home):
            recent_goals = team_data.get('goals_scored_last_5', 0) / 5
            recent_conceded = team_data.get('goals_conceded_last_5', 0) / 5
            
            # Historical averages
            if is_home:
                hist_goals = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
            else:
                hist_goals = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
            
            hist_conceded = team_data.get('goals_conceded', 0) / max(team_data.get('matches_played', 1), 1)
            
            # Attack form ratio
            attack_form = recent_goals / hist_goals if hist_goals > 0 else 1.0
            
            # Defense form ratio (lower recent conceded = better)
            defense_form = hist_conceded / recent_conceded if recent_conceded > 0 else 2.0
            defense_form = min(2.0, defense_form)  # Cap at 2.0
            
            # Position-based weighting
            position = team_data.get('overall_position', 10)
            
            if position <= 6:  # Top teams: attack matters more
                combined = (attack_form * 0.7) + (defense_form * 0.3)
            elif position >= 16:  # Bottom teams: defense matters more
                combined = (attack_form * 0.3) + (defense_form * 0.7)
            else:  # Mid-table: balanced
                combined = (attack_form * 0.5) + (defense_form * 0.5)
            
            # Cap extremes
            return max(0.4, min(1.6, combined))
        
        home_form = calculate_form(home_data, is_home=True)
        away_form = calculate_form(away_data, is_home=False)
        
        self.debug_info.append(f"Context Form: Home={home_form:.2f}, Away={away_form:.2f}")
        
        return {'home': home_form, 'away': away_form}
    
    def _calculate_home_advantage(self, home_data, away_data):
        """
        PRIORITY 5: Home vs Away Factors
        Uses home_ppg_diff for true home strength
        """
        home_ppg_diff = home_data.get('home_ppg_diff', 0)
        away_position = away_data.get('overall_position', 10)
        
        # Base home advantage from league
        base = self.league_params['home_advantage']
        
        # Adjust by home_ppg_diff (critical insight!)
        if home_ppg_diff > 1.0:
            advantage = base * 1.3  # Very strong home team
            self.scoring_insights.append(f"Strong home advantage: +{home_ppg_diff:.1f} PPG at home")
        elif home_ppg_diff > 0.5:
            advantage = base * 1.15
        elif home_ppg_diff < -0.5:
            advantage = 1.05  # Actually worse at home!
            self.scoring_insights.append(f"Weak at home: {home_ppg_diff:.1f} PPG diff")
        else:
            advantage = base
        
        # Adjust for away team strength
        if away_position <= 6:
            advantage *= 0.9  # Strong away teams reduce home advantage
            self.scoring_insights.append("Strong away team reduces home advantage")
        
        self.debug_info.append(f"Home Advantage: base={base:.2f}, ppg_diff={home_ppg_diff:.1f}, final={advantage:.2f}")
        
        return advantage
    
    def _assess_motivation(self, home_data, away_data):
        """
        PRIORITY 6: Motivation & Match Importance
        Uses motivation column + position implications
        """
        home_mot = home_data.get('motivation', 3)
        away_mot = away_data.get('motivation', 3)
        
        home_pos = home_data.get('overall_position', 10)
        away_pos = away_data.get('overall_position', 10)
        
        adjustments = {'home': 1.0, 'away': 1.0}
        
        # Motivation rating impact (1-5 scale)
        home_mult = 0.95 + (home_mot * 0.03)  # 1=0.98, 5=1.10
        away_mult = 0.95 + (away_mot * 0.03)
        
        adjustments['home'] *= home_mult
        adjustments['away'] *= away_mult
        
        # Position-based motivation
        # Relegation battle (positions 18-20)
        if home_pos >= 18:
            adjustments['home'] *= 1.1
            self.scoring_insights.append("Home in relegation battle → high motivation")
        if away_pos >= 18:
            adjustments['away'] *= 1.1
            self.scoring_insights.append("Away in relegation battle → high motivation")
        
        # European spots (positions 1-7)
        if home_pos <= 7:
            adjustments['home'] *= 1.05
        if away_pos <= 7:
            adjustments['away'] *= 1.05
        
        self.debug_info.append(f"Motivation: Home={adjustments['home']:.2f} (rating={home_mot}), Away={adjustments['away']:.2f} (rating={away_mot})")
        
        return adjustments
    
    # ==================== SCORING PATTERNS LOGIC ====================
    
    def _get_scoring_profile(self, team_data, is_home):
        """Get detailed scoring profile for a team"""
        if is_home:
            xg_per_game = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        else:
            xg_per_game = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        
        return {
            'xg_per_game': xg_per_game,
            'open_play_strength': team_data.get('open_play_pct', 0) / 100,
            'set_piece_strength': team_data.get('set_piece_pct', 0) / 100,
            'counter_strength': team_data.get('counter_attack_pct', 0) / 100,
            'recent_scoring': team_data.get('goals_scored_last_5', 0) / 5,
            'historical_scoring': team_data.get('goals', 0) / max(team_data.get('matches_played', 1), 1),
            'scoring_efficiency': team_data.get('goals', 0) / max(team_data.get('xg', 1), 1)
        }
    
    def _predict_scoring_patterns(self, home_data, away_data, home_strength, away_strength, style_adjustments):
        """
        Core logic for total goals and scoring patterns
        """
        home_pos = home_data.get('overall_position', 10)
        away_pos = away_data.get('overall_position', 10)
        pos_diff = abs(home_pos - away_pos)
        
        # Get scoring profiles
        home_scoring = self._get_scoring_profile(home_data, is_home=True)
        away_scoring = self._get_scoring_profile(away_data, is_home=False)
        
        # Base total from strengths
        base_total = home_strength + away_strength
        
        # Style-based scoring adjustment
        style_scoring_factor = 1.0
        style_insights = []
        
        # Open play vs Counter analysis
        if home_scoring['open_play_strength'] > 0.65 and away_scoring['counter_strength'] > 0.2:
            style_scoring_factor *= 1.25
            style_insights.append("Open play vs Counter clash → high scoring potential")
        
        # Set piece threat
        total_set_piece = (home_scoring['set_piece_strength'] + away_scoring['set_piece_strength']) / 2
        if total_set_piece > 0.25:
            style_scoring_factor *= 1.10
            style_insights.append(f"Strong set piece threat ({total_set_piece*100:.0f}% average)")
        
        # Recent vs historical scoring
        home_recent_ratio = home_scoring['recent_scoring'] / home_scoring['historical_scoring'] if home_scoring['historical_scoring'] > 0 else 1.0
        away_recent_ratio = away_scoring['recent_scoring'] / away_scoring['historical_scoring'] if away_scoring['historical_scoring'] > 0 else 1.0
        
        recent_factor = (home_recent_ratio + away_recent_ratio) / 2
        
        # Position mismatch effect
        if pos_diff > 10:
            # Big mismatch - could be defensive from weaker team
            style_scoring_factor *= 0.9
            style_insights.append(f"Big position gap (#{home_pos} vs #{away_pos}) → cautious approach likely")
        
        # Final total goals prediction
        predicted_total = base_total * style_scoring_factor * recent_factor
        
        # BTTS Probability Calculation
        btts_base = 0.5  # Base 50%
        
        # Both teams scoring ability
        if home_scoring['xg_per_game'] > 1.5 and away_scoring['xg_per_game'] > 1.2:
            btts_base += 0.2
            style_insights.append("Both teams strong attack → BTTS likely")
        elif home_scoring['xg_per_game'] < 1.0 or away_scoring['xg_per_game'] < 1.0:
            btts_base -= 0.2
            style_insights.append("One team weak attack → BTTS less likely")
        
        # Recent scoring form
        if home_scoring['recent_scoring'] == 0:
            btts_base -= 0.15
            style_insights.append("Home not scoring recently → BTTS unlikely")
        if away_scoring['recent_scoring'] == 0:
            btts_base -= 0.15
            style_insights.append("Away not scoring recently → BTTS unlikely")
        
        # Position gap
        if pos_diff > 8:
            btts_base -= 0.1
        
        # Cap probabilities
        btts_prob = max(0.2, min(0.8, btts_base))
        
        # Add style insights to scoring insights
        self.scoring_insights.extend(style_insights)
        
        # Store for debug
        self.debug_info.append(f"Scoring Patterns: base_total={base_total:.2f}, style_factor={style_scoring_factor:.2f}, recent_factor={recent_factor:.2f}, predicted_total={predicted_total:.2f}")
        self.debug_info.append(f"BTTS Analysis: base={btts_base:.2f}, final={btts_prob:.2f}")
        
        return {
            'predicted_total': predicted_total,
            'over_25_prob': self._poisson_over_probability(predicted_total),
            'under_25_prob': 1 - self._poisson_over_probability(predicted_total),
            'btts_prob': btts_prob,
            'btts_no_prob': 1 - btts_prob,
            'scoring_insights': style_insights
        }
    
    def _poisson_over_probability(self, total_lambda):
        """Calculate Over 2.5 probability using Poisson"""
        # Simplified calculation
        if total_lambda <= 1.5:
            return 0.25
        elif total_lambda <= 2.0:
            return 0.40
        elif total_lambda <= 2.5:
            return 0.55
        elif total_lambda <= 3.0:
            return 0.70
        else:
            return 0.85
    
    # ==================== MAIN PREDICTION METHOD ====================
    
    def predict_match(self, home_data, away_data):
        """Main prediction function integrating all professional priorities"""
        self.reset()
        
        # 1. UNDERLYING PERFORMANCE
        home_strength = self._calculate_true_strength(home_data, is_home=True)
        away_strength = self._calculate_true_strength(away_data, is_home=False)
        
        # 2. SQUAD CONTEXT
        injury_impact = self._assess_injury_impact(home_data, away_data)
        form_context = self._assess_form_with_context(home_data, away_data)
        
        # 3. TACTICAL FIT
        style_analysis = self._analyze_style_matchup(home_data, away_data)
        
        # 4. HOME ADVANTAGE
        home_advantage = self._calculate_home_advantage(home_data, away_data)
        away_disadvantage = 2.0 - home_advantage
        
        # 5. MOTIVATION
        motivation = self._assess_motivation(home_data, away_data)
        
        # INTEGRATE ALL FACTORS
        home_lambda = home_strength
        away_lambda = away_strength
        
        # Apply all adjustments
        adjustments = [
            ('Injury', injury_impact['home'], injury_impact['away']),
            ('Form', form_context['home'], form_context['away']),
            ('Style', style_analysis['home'], style_analysis['away']),
            ('Home/away', home_advantage, away_disadvantage),
            ('Motivation', motivation['home'], motivation['away'])
        ]
        
        for name, home_adj, away_adj in adjustments:
            home_lambda *= home_adj
            away_lambda *= away_adj
        
        # 6. SCORING PATTERNS PREDICTION
        scoring_prediction = self._predict_scoring_patterns(
            home_data, away_data, home_strength, away_strength, style_analysis
        )
        
        # Final calibration
        home_lambda, away_lambda = self._final_calibration(home_lambda, away_lambda, home_data, away_data)
        
        # Calculate match probabilities
        probabilities = self._calculate_probabilities(home_lambda, away_lambda)
        
        # Generate key factors
        key_factors = self._generate_key_factors(home_data, away_data, home_lambda, away_lambda, scoring_prediction)
        
        # Combine debug info
        all_debug = self.debug_info + [f"Final: Home λ={home_lambda:.2f}, Away λ={away_lambda:.2f}, Total={home_lambda+away_lambda:.2f}"]
        
        return {
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'probabilities': probabilities,
            'scoring_analysis': scoring_prediction,
            'confidence': self._calculate_confidence(home_lambda, away_lambda, home_data, away_data),
            'key_factors': key_factors + all_debug + self.scoring_insights,
            'success': True
        }
    
    def _final_calibration(self, home_lambda, away_lambda, home_data, away_data):
        """Final calibration with realistic constraints"""
        home_pos = home_data.get('overall_position', 10)
        away_pos = away_data.get('overall_position', 10)
        
        # Minimum values
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], home_lambda)
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], away_lambda)
        
        # Maximum values based on position
        max_home = 3.5 if home_pos <= 3 else 3.0 if home_pos <= 6 else 2.5 if home_pos <= 12 else 2.0
        max_away = 2.8 if away_pos <= 3 else 2.3 if away_pos <= 6 else 1.9 if away_pos <= 12 else 1.5
        
        home_lambda = min(max_home, home_lambda)
        away_lambda = min(max_away, away_lambda)
        
        # Ensure reasonable total
        total = home_lambda + away_lambda
        if total > 5.0:
            scale = 5.0 / total
            home_lambda *= scale
            away_lambda *= scale
        
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
    
    def _calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """Calculate model confidence"""
        confidence = 50
        
        # Goal difference
        goal_diff = abs(home_lambda - away_lambda)
        confidence += goal_diff * 15
        
        # Position difference
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 25
        elif pos_diff >= 5:
            confidence += 15
        
        # Recent form consistency
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        home_avg = home_data.get('goals', 0) / max(home_data.get('matches_played', 1), 1)
        home_consistency = min(1.0, home_recent / home_avg) if home_avg > 0 else 0.5
        
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        away_avg = away_data.get('goals', 0) / max(away_data.get('matches_played', 1), 1)
        away_consistency = min(1.0, away_recent / away_avg) if away_avg > 0 else 0.5
        
        confidence += (home_consistency + away_consistency - 1.0) * 10
        
        return round(max(30, min(85, confidence)), 1)
    
    def _generate_key_factors(self, home_data, away_data, home_lambda, away_lambda, scoring_prediction):
        """Generate key factors for the prediction"""
        factors = []
        
        home_pos = home_data.get('overall_position', 10)
        away_pos = away_data.get('overall_position', 10)
        pos_diff = abs(home_pos - away_pos)
        
        if pos_diff >= 10:
            factors.append(f"Huge position gap: #{home_pos} vs #{away_pos}")
        elif pos_diff >= 5:
            factors.append(f"Significant position gap: #{home_pos} vs #{away_pos}")
        
        # Scoring factors
        if home_lambda > 2.5:
            factors.append(f"Extremely high home expected goals: {home_lambda:.2f}")
        elif home_lambda > 2.0:
            factors.append(f"Very high home expected goals: {home_lambda:.2f}")
        
        if away_lambda > 2.0:
            factors.append(f"Very high away expected goals: {away_lambda:.2f}")
        
        # Recent form
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        if home_recent == 0:
            factors.append("Home not scoring recently (0 goals in last 5)")
        elif home_recent < 0.5:
            factors.append(f"Home poor recent scoring: {home_recent:.1f} goals/game")
        
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        if away_recent == 0:
            factors.append("Away not scoring recently (0 goals in last 5)")
        elif away_recent < 0.5:
            factors.append(f"Away poor recent scoring: {away_recent:.1f} goals/game")
        
        # Injuries
        if home_data.get('defenders_out', 0) >= 3:
            factors.append(f"Home defensive crisis: {home_data['defenders_out']} defenders out")
        if away_data.get('defenders_out', 0) >= 3:
            factors.append(f"Away defensive crisis: {away_data['defenders_out']} defenders out")
        
        # Add scoring insights
        factors.extend(scoring_prediction.get('scoring_insights', []))
        
        return factors

# ============================================================================
# DATA LOADING & UI (SAME AS BEFORE)
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

def display_scoring_analysis(analysis):
    """Display scoring pattern analysis."""
    st.markdown("### ⚽ Scoring Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        over_color = "#00b09b" if analysis['over_25_prob'] > 0.5 else "#4ECDC4"
        under_color = "#ff416c" if analysis['under_25_prob'] > 0.5 else "#4ECDC4"
        
        display_prediction_box(
            "Over 2.5 Goals",
            f"{analysis['over_25_prob']*100:.1f}%",
            f"Fair odds: {1/analysis['over_25_prob']:.2f}" if analysis['over_25_prob'] > 0 else "N/A",
            over_color
        )
    
    with col2:
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
    
    # Display scoring insights
    if analysis.get('scoring_insights'):
        st.markdown("#### 📊 Scoring Insights")
        for insight in analysis['scoring_insights']:
            st.info(f"• {insight}")

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
    .stButton > button:hover {
        background: linear-gradient(135deg, #44A08D, #4ECDC4);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Professional Football Predictor</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Underlying Performance + Squad Context + Tactical Fit</p>', 
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
        st.markdown("### 🎯 Professional Methodology")
        st.success("""
        **Priorities:**
        1. Team Strength (xG efficiency)
        2. Squad Availability
        3. Tactical Matchup
        4. Context-Aware Form
        5. Home Advantage
        6. Motivation
        **Focus: Total goals & scoring patterns**
        """)
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        st.markdown("""
        ### 🎯 Professional Football Prediction
        
        **This engine implements professional analysis:**
        - **Underlying performance**: xG efficiency, not just results
        - **Squad context**: Injuries, form vs historical
        - **Tactical fit**: Style matchups, scoring patterns
        - **Focus**: Total goals and team scoring likelihood
        
        **Using all your data:**
        - `open_play_pct`, `set_piece_pct`, `counter_attack_pct` → Tactical analysis
        - `home_ppg_diff` → True home strength
        - `goals_scored_last_5` vs historical → Form context
        - `defenders_out` → Squad availability impact
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
    
    if st.button("🚀 Run Professional Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams.")
            return
        
        try:
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            predictor = ProfessionalFootballPredictor(league_params)
            
            with st.spinner("Running professional analysis..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                result = predictor.predict_match(home_data, away_data)
                
                if result['success']:
                    # Generate market recommendations
                    recommendations = []
                    
                    # Total Goals recommendation
                    if result['scoring_analysis']['over_25_prob'] > 0.5:
                        rec = {
                            'market': 'Total Goals',
                            'prediction': 'Over 2.5',
                            'probability': result['scoring_analysis']['over_25_prob'],
                            'fair_odds': 1 / result['scoring_analysis']['over_25_prob'],
                            'market_odds': market_odds.get('over_25', 1.85),
                            'strength': 'Strong' if result['scoring_analysis']['over_25_prob'] > 0.65 else 'Moderate'
                        }
                    else:
                        rec = {
                            'market': 'Total Goals',
                            'prediction': 'Under 2.5',
                            'probability': result['scoring_analysis']['under_25_prob'],
                            'fair_odds': 1 / result['scoring_analysis']['under_25_prob'],
                            'market_odds': 1 / (1 - 1/market_odds.get('over_25', 1.85)) if market_odds.get('over_25', 1.85) > 1 else 2.00,
                            'strength': 'Strong' if result['scoring_analysis']['under_25_prob'] > 0.65 else 'Moderate'
                        }
                    recommendations.append(rec)
                    
                    # BTTS recommendation
                    if result['scoring_analysis']['btts_prob'] > 0.5:
                        rec = {
                            'market': 'Both Teams to Score',
                            'prediction': 'Yes',
                            'probability': result['scoring_analysis']['btts_prob'],
                            'fair_odds': 1 / result['scoring_analysis']['btts_prob'],
                            'market_odds': market_odds.get('btts_yes', 1.75),
                            'strength': 'Strong' if result['scoring_analysis']['btts_prob'] > 0.65 else 'Moderate'
                        }
                    else:
                        rec = {
                            'market': 'Both Teams to Score',
                            'prediction': 'No',
                            'probability': result['scoring_analysis']['btts_no_prob'],
                            'fair_odds': 1 / result['scoring_analysis']['btts_no_prob'],
                            'market_odds': 1 / (1 - 1/market_odds.get('btts_yes', 1.75)) if market_odds.get('btts_yes', 1.75) > 1 else 2.00,
                            'strength': 'Strong' if result['scoring_analysis']['btts_no_prob'] > 0.65 else 'Moderate'
                        }
                    recommendations.append(rec)
                    
                    st.session_state.prediction_result = result
                    st.session_state.recommendations = recommendations
                    st.success("✅ Professional analysis complete!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        recommendations = st.session_state.get('recommendations', [])
        
        st.markdown("---")
        st.markdown("# 📊 Professional Analysis Results")
        
        st.markdown("### 🎯 Expected Goals (True Performance)")
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
        
        # Display scoring analysis
        display_scoring_analysis(result['scoring_analysis'])
        
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
            st.markdown("### 🔑 Key Factors & Analysis")
            cols = st.columns(2)
            for idx, factor in enumerate(result['key_factors']):
                with cols[idx % 2]:
                    if factor.startswith("DEBUG:"):
                        bg_color = "rgba(255,255,0,0.1)"
                        border_color = "#FFD700"
                    elif "scoring" in factor.lower() or "attack" in factor.lower() or "defense" in factor.lower():
                        bg_color = "rgba(78,205,196,0.1)"
                        border_color = "#4ECDC4"
                    else:
                        bg_color = "rgba(255,107,107,0.1)"
                        border_color = "#FF6B6B"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; border-radius: 10px; padding: 10px; 
                                margin: 5px 0; border-left: 4px solid {border_color};">
                        <span style="color: #333; font-weight: 500;">{factor}</span>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
