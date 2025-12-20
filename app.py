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
# LEAGUE-SPECIFIC PARAMETERS & CONSTANTS
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'league_avg_goals_conceded': 1.26,
        'league_avg_shots_allowed': 12.3,
        'home_advantage_base': 1.15,
        'variance_factor': 0.95,
        'home_xg_share': 0.55,  # % of xG created at home
    },
    'PREMIER LEAGUE': {
        'league_avg_goals_conceded': 1.42,
        'league_avg_shots_allowed': 12.7,
        'home_advantage_base': 1.18,
        'variance_factor': 1.05,
        'home_xg_share': 0.55,
    }
}

CONSTANTS = {
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 6,
    'MIN_HOME_LAMBDA': 0.8,
    'MIN_AWAY_LAMBDA': 0.6,
    'MAX_LAMBDA': 4.0,
    'SET_PIECE_THRESHOLD': 0.15,
    'COUNTER_ATTACK_THRESHOLD': 0.15,
    'DEFENDER_INJURY_IMPACT': 0.06,
    'ATTACK_UNDERPERFORM_THRESHOLD': 0.7,
    'ATTACK_OVERPERFORM_THRESHOLD': 1.3,
    'DEFENSE_UNDERPERFORM_THRESHOLD': 0.8,
    'DEFENSE_OVERPERFORM_THRESHOLD': 1.2,
    'FORM_MULTIPLIER_MIN': 0.85,
    'FORM_MULTIPLIER_MAX': 1.0,
    'MOTIVATION_MIN': 0.94,
    'MOTIVATION_MAX': 1.10,
}

# ============================================================================
# PREDICTION ENGINE CORE
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
    
    def _calculate_recent_attack(self, team_data):
        """Calculate attack strength with recent performance > season averages."""
        venue = team_data['venue']
        matches_played = team_data['matches_played']
        
        # Get venue-specific xG
        if venue == 'home':
            season_xg = team_data.get('home_xg_for', 0)
            # If not available, estimate from total xg_for
            if season_xg == 0 and 'xg_for' in team_data:
                season_xg = team_data['xg_for'] * self.league_params['home_xg_share']
        else:  # away
            season_xg = team_data.get('away_xg_for', 0)
            if season_xg == 0 and 'xg_for' in team_data:
                season_xg = team_data['xg_for'] * (1 - self.league_params['home_xg_share'])
        
        # Calculate season xG per game
        if matches_played > 0:
            season_xg_pg = season_xg / matches_played
        else:
            season_xg_pg = 1.0  # Default to league average
        
        # Recent actual goals per game
        recent_goals_pg = team_data['goals_scored_last_5'] / 5
        
        # Performance ratio: actual goals vs expected goals
        if season_xg_pg > 0:
            performance_ratio = recent_goals_pg / season_xg_pg
        else:
            performance_ratio = 1.0
        
        # Apply CORE LOGIC: Recent performance > season averages
        if performance_ratio < CONSTANTS['ATTACK_UNDERPERFORM_THRESHOLD']:
            # Underperforming xG by 30%+ → trust recent actual goals
            base_attack = recent_goals_pg
        elif performance_ratio > CONSTANTS['ATTACK_OVERPERFORM_THRESHOLD']:
            # Overperforming xG by 30%+ → cap at +30%
            base_attack = season_xg_pg * 1.3
        else:
            # Normal variation → use adjusted xG
            base_attack = season_xg_pg * min(performance_ratio, 1.3)
        
        # Apply minimum attack strength
        base_attack = max(0.3, base_attack)
        
        # Add finishing ratio adjustment (using total xg_for if available)
        if 'xg_for' in team_data and team_data['xg_for'] > 0:
            finishing_ratio = team_data['goals'] / team_data['xg_for']
            finishing_adj = max(0.7, min(1.3, finishing_ratio))
        else:
            finishing_adj = 1.0
        
        # Form momentum (last 3 games)
        form_string = team_data.get('form', '')
        form_momentum = 1.0
        if form_string:
            last_3 = form_string[-3:] if len(form_string) >= 3 else form_string
            wins = last_3.count('W')
            draws = last_3.count('D')
            losses = last_3.count('L')
            
            # Form multiplier: 0.85 (all losses) to 1.0 (all wins)
            form_score = (wins * 3) + (draws * 1)
            max_possible = 9  # 3 wins
            form_momentum = CONSTANTS['FORM_MULTIPLIER_MIN'] + (
                (CONSTANTS['FORM_MULTIPLIER_MAX'] - CONSTANTS['FORM_MULTIPLIER_MIN']) * 
                (form_score / max_possible)
            )
        
        # Motivation adjustment (scale 1-5)
        motivation = team_data.get('motivation', 3)
        motivation_range = CONSTANTS['MOTIVATION_MAX'] - CONSTANTS['MOTIVATION_MIN']
        motivation_adj = CONSTANTS['MOTIVATION_MIN'] + (motivation_range * (motivation - 1) / 4)
        
        # Position factor
        position = team_data['overall_position']
        if position <= 4:          # Top 4
            pos_factor = 1.15
        elif position <= 8:        # European spots
            pos_factor = 1.08
        elif position <= 12:       # Mid-table
            pos_factor = 1.0
        elif position <= 16:       # Lower mid-table
            pos_factor = 0.92
        else:                      # Relegation battle
            pos_factor = 0.85
        
        # Track key factors
        if performance_ratio < 0.7:
            self.key_factors.append(f"{team_data['team']} underperforming xG: {performance_ratio:.0%} of expected")
        elif performance_ratio > 1.3:
            self.key_factors.append(f"{team_data['team']} overperforming xG: {performance_ratio:.0%} of expected")
        
        return base_attack * finishing_adj * form_momentum * motivation_adj * pos_factor
    
    def _calculate_recent_defense(self, team_data, is_home):
        """Calculate defensive quality with recent performance > season averages."""
        venue = 'home' if is_home else 'away'
        matches_played = team_data['matches_played']
        
        # Get venue-specific xGA
        if is_home:
            season_xga = team_data.get('home_xga', 0)
            if season_xga == 0 and 'xg_for' in team_data:
                # Estimate from league average ratio
                season_xga = team_data['xg_for'] * 0.8  # Rough estimate
        else:
            season_xga = team_data.get('away_xga', 0)
            if season_xga == 0 and 'xg_for' in team_data:
                season_xga = team_data['xg_for'] * 0.8
        
        # Calculate season xGA per game
        if matches_played > 0:
            season_xga_pg = season_xga / matches_played
        else:
            season_xga_pg = self.league_params['league_avg_goals_conceded']
        
        # Recent actual goals conceded per game
        recent_conceded_pg = team_data['goals_conceded_last_5'] / 5
        
        # Defense ratio
        if season_xga_pg > 0:
            defense_ratio = recent_conceded_pg / season_xga_pg
        else:
            defense_ratio = 1.0
        
        # Apply defense logic
        if defense_ratio < CONSTANTS['DEFENSE_UNDERPERFORM_THRESHOLD']:
            # Conceding 20%+ less than expected recently
            if team_data['goals_conceded'] > 0 and season_xga > 0:
                actual_vs_expected = team_data['goals_conceded'] / season_xga
                if actual_vs_expected < 0.9:
                    # Consistently better than xGA
                    effective_defense = recent_conceded_pg * 0.9
                    self.key_factors.append(f"{team_data['team']} defense consistently better than xGA: {actual_vs_expected:.0%}")
                else:
                    # Just recent good form
                    effective_defense = recent_conceded_pg
            else:
                effective_defense = recent_conceded_pg
                
        elif defense_ratio > CONSTANTS['DEFENSE_OVERPERFORM_THRESHOLD']:
            # Conceding 20%+ more than expected
            effective_defense = season_xga_pg * defense_ratio
            self.key_factors.append(f"{team_data['team']} conceding {defense_ratio:.0%} more than xGA recently")
        else:
            # Within normal range
            effective_defense = season_xga_pg
        
        # Performance boost based on actual vs expected
        if team_data['goals_conceded'] > 0 and season_xga > 0:
            actual_vs_expected = team_data['goals_conceded'] / season_xga
            
            if actual_vs_expected < 0.9:
                # Team consistently outperforms xGA (better defense than stats show)
                performance_boost = 0.85 + (0.15 * (1 - actual_vs_expected) / 0.1)
            elif actual_vs_expected > 1.1:
                # Team underperforms xGA (worse than stats show)
                performance_boost = 1.0 + (actual_vs_expected - 1.1)
            else:
                performance_boost = 1.0
        else:
            performance_boost = 1.0
        
        # Apply performance boost
        effective_defense = effective_defense * performance_boost
        
        # Apply injury impact
        injury_adj = 1.0 - (team_data['defenders_out'] * CONSTANTS['DEFENDER_INJURY_IMPACT'])
        injury_adj = max(0.7, injury_adj)
        
        if team_data['defenders_out'] > 0:
            self.key_factors.append(f"{team_data['team']} missing {team_data['defenders_out']} defenders")
        
        # Position factor for defense
        position = team_data['overall_position']
        if position <= 4:          # Top 4
            pos_factor = 0.85
        elif position <= 8:        # European spots
            pos_factor = 0.92
        elif position <= 12:       # Mid-table
            pos_factor = 1.0
        elif position <= 16:       # Lower mid-table
            pos_factor = 1.08
        else:                      # Relegation battle
            pos_factor = 1.15
        
        # Shots allowed adjustment
        shots_factor = team_data['shots_allowed_pg'] / self.league_params['league_avg_shots_allowed']
        shots_adj = max(0.85, min(1.15, shots_factor))
        
        effective_defense = effective_defense * pos_factor * shots_adj * injury_adj
        
        return effective_defense
    
    def _calculate_style_adjustments(self, home_data, away_data):
        """Calculate style matchup adjustments."""
        adjustments = {'home': 0, 'away': 0}
        factors = []
        
        set_piece_diff = home_data['set_piece_pct'] - away_data['set_piece_pct']
        if abs(set_piece_diff) > CONSTANTS['SET_PIECE_THRESHOLD']:
            if set_piece_diff > 0:
                pos_diff = away_data['overall_position'] - home_data['overall_position']
                if pos_diff > 3:
                    adjustments['home'] += 0.10
                else:
                    adjustments['home'] += 0.05
                factors.append(f"Home set piece advantage: {set_piece_diff:.0%}")
            else:
                pos_diff = home_data['overall_position'] - away_data['overall_position']
                if pos_diff > 3:
                    adjustments['away'] += 0.10
                else:
                    adjustments['away'] += 0.05
                factors.append(f"Away set piece advantage: {-set_piece_diff:.0%}")
        
        if (away_data['counter_attack_pct'] > CONSTANTS['COUNTER_ATTACK_THRESHOLD'] and 
            home_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']):
            adjustments['away'] += 0.08
            factors.append("Away counter attack threat")
        
        if (home_data['open_play_pct'] > 0.70 and 
            away_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']):
            adjustments['home'] += 0.05
            factors.append("Home open play dominance")
        
        self.key_factors.extend(factors)
        return adjustments
    
    def calculate_expected_goals(self, home_data, away_data):
        """Calculate expected goals with recent performance logic."""
        # Calculate attack strengths
        home_attack = self._calculate_recent_attack(home_data)
        away_attack = self._calculate_recent_attack(away_data)
        
        # Calculate defense qualities
        away_defense = self._calculate_recent_defense(away_data, is_home=False)
        home_defense = self._calculate_recent_defense(home_data, is_home=True)
        
        # Convert to defense factors
        defense_factor_away = away_defense / self.league_params['league_avg_goals_conceded']
        defense_factor_home = home_defense / self.league_params['league_avg_goals_conceded']
        
        # Base expected goals
        home_lambda = home_attack * defense_factor_away
        away_lambda = away_attack * defense_factor_home
        
        # Style adjustments
        style_adjustments = self._calculate_style_adjustments(home_data, away_data)
        home_lambda += style_adjustments['home']
        away_lambda += style_adjustments['away']
        
        # Home advantage (team-specific)
        home_advantage = self.league_params['home_advantage_base'] * (1 + home_data['home_ppg_diff'] * 0.1)
        home_lambda *= home_advantage
        away_lambda *= (2.0 - home_advantage)
        
        # Position-based adjustments for extreme differences
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 8:
            home_lambda *= 1.08
            away_lambda *= 0.92
        elif pos_diff <= -8:
            home_lambda *= 0.92
            away_lambda *= 1.08
        
        # Apply limits
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], away_lambda))
        
        return round(home_lambda, 2), round(away_lambda, 2)
    
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
        """Calculate model confidence."""
        confidence = 50
        
        # Expected goals difference
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.5:
            confidence += 25
        elif goal_diff > 1.0:
            confidence += 15
        elif goal_diff > 0.5:
            confidence += 5
        
        # Position difference
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 20
        elif pos_diff >= 5:
            confidence += 10
        
        # Form difference
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        if form_diff >= 10:
            confidence += 15
        elif form_diff >= 5:
            confidence += 8
        
        # Apply league variance factor
        confidence *= self.league_params['variance_factor']
        
        # Clamp to reasonable range
        return round(max(35, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors for the prediction."""
        factors = []
        
        # Position analysis
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 5:
            factors.append(f"Home position disadvantage: #{home_data['overall_position']} vs #{away_data['overall_position']}")
        elif pos_diff <= -5:
            factors.append(f"Away position disadvantage: #{away_data['overall_position']} vs #{home_data['overall_position']}")
        
        # Form analysis
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if form_diff > 5:
            factors.append(f"Home form advantage: +{form_diff} points")
        elif form_diff < -5:
            factors.append(f"Away form advantage: +{-form_diff} points")
        
        # Defensive analysis
        if home_data['shots_allowed_pg'] < self.league_params['league_avg_shots_allowed']:
            factors.append(f"Home strong shot suppression: {home_data['shots_allowed_pg']:.1f} shots/game")
        if away_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']:
            factors.append(f"Away defensive vulnerability: {away_data['shots_allowed_pg']:.1f} shots/game")
        
        # Attacking analysis
        if 'xg_for' in home_data and home_data['xg_for'] / home_data['matches_played'] > 1.5:
            factors.append(f"Home attacking strength: {home_data['xg_for']/home_data['matches_played']:.2f} xG/game")
        if 'xg_for' in away_data and away_data['xg_for'] / away_data['matches_played'] > 1.5:
            factors.append(f"Away attacking strength: {away_data['xg_for']/away_data['matches_played']:.2f} xG/game")
        
        # Expected goals insight
        if home_lambda > 2.0:
            factors.append(f"High home expected goals: {home_lambda:.2f}")
        if away_lambda < 0.8:
            factors.append(f"Low away expected goals: {away_lambda:.2f}")
        
        return factors
    
    def get_market_recommendations(self, probabilities, market_odds):
        """Get clear market recommendations."""
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
        
        # Standardize column names to lowercase with underscores
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Check for column name variations and data structure
        available_cols = list(df.columns)
        
        # Handle different data structures
        if 'xg_for' in df.columns and 'home_xg_for' not in df.columns:
            # La Liga old format - create estimated columns
            st.info("⚠️ Using estimated home/away xG splits for La Liga data")
            
            # Estimate home/away splits based on venue
            for idx, row in df.iterrows():
                venue = row['venue']
                if venue == 'home':
                    df.at[idx, 'home_xg_for'] = row['xg_for'] * 0.55
                    df.at[idx, 'away_xg_for'] = 0
                    df.at[idx, 'home_xga'] = row.get('home_xga', row['xg_for'] * 0.8)
                    df.at[idx, 'away_xga'] = 0
                else:  # away
                    df.at[idx, 'home_xg_for'] = 0
                    df.at[idx, 'away_xg_for'] = row['xg_for'] * 0.45
                    df.at[idx, 'home_xga'] = 0
                    df.at[idx, 'away_xga'] = row.get('away_xga', row['xg_for'] * 0.8)
        
        # Required columns
        required_cols = [
            'overall_position', 'team', 'venue', 'matches_played', 'home_xg_for', 
            'away_xg_for', 'goals', 'home_xga', 'away_xga', 'goals_conceded',
            'defenders_out', 'form_last_5', 'motivation', 'open_play_pct', 
            'set_piece_pct', 'counter_attack_pct', 'form', 'shots_allowed_pg', 
            'home_ppg_diff', 'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        # Check for missing columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"⚠️ Missing columns in {league_name} data: {', '.join(missing_cols)}")
            
            with st.expander("🔍 View Raw Data Structure"):
                st.write("**Original column names:**", original_columns)
                st.write("**Standardized column names:**", available_cols)
                st.write("**First 3 rows of data:**")
                st.dataframe(df.head(3))
            
            # Try to continue with available data
            for col in missing_cols:
                if col not in df.columns:
                    df[col] = 0  # Default value
            
        # Convert numeric columns
        numeric_cols = ['matches_played', 'home_xg_for', 'away_xg_for', 'goals', 
                       'home_xga', 'away_xga', 'goals_conceded', 'defenders_out',
                       'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct', 
                       'counter_attack_pct', 'shots_allowed_pg', 'home_ppg_diff',
                       'goals_scored_last_5', 'goals_conceded_last_5']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with reasonable defaults
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
        # Try case-insensitive match
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
    st.markdown('<p style="text-align: center; color: #666;">Complete Logic • Position-Based • Professional</p>', 
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
                st.metric("Avg Goals Conceded", f"{params['league_avg_goals_conceded']:.2f}")
            with col2:
                st.metric("Avg Shots Allowed", f"{params['league_avg_shots_allowed']:.2f}")
        
        st.markdown("---")
        st.markdown("### 🔧 Engine Settings")
        st.info("""
        **New Logic Features:**
        • Recent Performance > Season Averages
        • Actual Goals > Expected Goals (xG)
        • Last 5 Games > Whole Season
        • Venue-Specific Analysis
        """)
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        st.markdown("""
        ### 🚀 How to Use:
        1. **Select a league** from the sidebar
        2. **Click "Load Data"** to fetch the latest statistics
        3. **Choose home and away teams** for your match
        4. **Enter market odds** (optional)
        5. **Click "Run Advanced Prediction"** to get analysis
        
        ### 📊 Data Sources:
        • **La Liga:** https://github.com/profdue/Brutball/blob/main/leagues/la_liga.csv
        • **Premier League:** https://github.com/profdue/Brutball/blob/main/leagues/premier_league.csv
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
                st.metric("Recent Goals/Game", f"{home_row['goals_scored_last_5']/5:.1f}")
                st.metric("Home xG/Game", f"{home_row['home_xg_for']/home_row['matches_played']:.2f}")
            with col2a:
                st.metric("Recent Conceded/Game", f"{home_row['goals_conceded_last_5']/5:.1f}")
                st.metric("Form Last 5", f"{home_row['form_last_5']:.1f}")
                st.metric("Home xGA/Game", f"{home_row['home_xga']/home_row['matches_played']:.2f}")
    
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
                st.metric("Recent Goals/Game", f"{away_row['goals_scored_last_5']/5:.1f}")
                st.metric("Away xG/Game", f"{away_row['away_xg_for']/away_row['matches_played']:.2f}")
            with col2b:
                st.metric("Recent Conceded/Game", f"{away_row['goals_conceded_last_5']/5:.1f}")
                st.metric("Form Last 5", f"{away_row['form_last_5']:.1f}")
                st.metric("Away xGA/Game", f"{away_row['away_xga']/away_row['matches_played']:.2f}")
    
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
                
                with st.spinner("Running complete analysis..."):
                    progress_bar = st.progress(0)
                    
                    # Simulate processing steps
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    result = engine.predict(home_data, away_data)
                    
                    if result['success']:
                        recommendations = engine.get_market_recommendations(result['probabilities'], market_odds)
                        
                        st.session_state.prediction_result = result
                        st.session_state.prediction_engine = engine
                        st.session_state.recommendations = recommendations
                        st.success("✅ Analysis complete!")
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
            st.markdown("### 🔑 Key Factors")
            cols = st.columns(2)
            for idx, factor in enumerate(result['key_factors']):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div style="background: rgba(255,107,107,0.1); border-radius: 10px; padding: 10px; 
                                margin: 5px 0; border-left: 4px solid #FF6B6B;">
                        <span style="color: #FF6B6B; font-weight: 500;">{factor}</span>
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