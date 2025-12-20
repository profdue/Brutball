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
    },
    'PREMIER LEAGUE': {
        'league_avg_goals_conceded': 1.42,
        'league_avg_shots_allowed': 12.7,
        'home_advantage_base': 1.18,
        'variance_factor': 1.05,
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
    
    def _apply_tiered_penalties(self, position, recent_goals_pg, recent_conceded_pg, is_attack):
        """Apply tiered penalties for extreme cases."""
        attack_penalty = 1.0
        defense_penalty = 1.0
        
        # TIER 1: Terrible teams (position 18-20)
        if position >= 18:
            if is_attack:
                if recent_goals_pg < 1.0:
                    attack_penalty = 0.75
            else:
                if recent_conceded_pg > 2.0:
                    defense_penalty = 1.25
                elif recent_conceded_pg > 1.5:
                    defense_penalty = 1.15
        
        # TIER 2: Very bad teams (position 15-17)
        elif position >= 15:
            if is_attack:
                if recent_goals_pg < 0.8:
                    attack_penalty = 0.85
            else:
                if recent_conceded_pg > 1.8:
                    defense_penalty = 1.15
                elif recent_conceded_pg > 1.4:
                    defense_penalty = 1.08
        
        # TIER 3: Top teams (position 1-4)
        elif position <= 4:
            if is_attack:
                if recent_goals_pg > 1.8:
                    attack_penalty = 1.15
            else:
                if recent_conceded_pg < 0.8:
                    defense_penalty = 0.85
        
        return attack_penalty, defense_penalty
    
    def _calculate_position_factor(self, position, is_attack=True):
        """More realistic position multipliers."""
        if position <= 4:          # Top 4
            return 1.15 if is_attack else 0.85
        elif position <= 8:        # European spots
            return 1.08 if is_attack else 0.92
        elif position <= 12:       # Mid-table
            return 1.0 if is_attack else 1.0
        elif position <= 16:       # Lower mid-table
            return 0.92 if is_attack else 1.08
        else:                      # Relegation battle
            return 0.85 if is_attack else 1.15
    
    def _calculate_recent_attack(self, team_data):
        """Calculate attack strength with tiered penalties."""
        recent_goals_pg = team_data['goals_scored_last_5'] / 5
        season_xg_pg = team_data['xg_for'] / team_data['matches_played']
        
        base_attack = (recent_goals_pg * 0.7) + (season_xg_pg * 0.3)
        
        attack_penalty, _ = self._apply_tiered_penalties(
            team_data['overall_position'], 
            recent_goals_pg, 
            0,
            is_attack=True
        )
        base_attack *= attack_penalty
        
        base_attack = max(0.7, base_attack)
        pos_boost = self._calculate_position_factor(team_data['overall_position'], is_attack=True)
        
        if team_data['xg_for'] > 0:
            finishing_ratio = team_data['goals'] / team_data['xg_for']
            finishing_adj = max(0.8, min(1.2, finishing_ratio))
        else:
            finishing_adj = 1.0
        
        form_string = team_data.get('form', '')
        form_momentum = 1.0
        if form_string:
            last_3 = form_string[-3:] if len(form_string) >= 3 else form_string
            wins = last_3.count('W')
            draws = last_3.count('D')
            form_momentum = 0.95 + (wins * 0.05) + (draws * 0.025)
        
        motivation_adj = 1.0 + (team_data['motivation'] - 3) * 0.03
        
        return base_attack * pos_boost * finishing_adj * form_momentum * motivation_adj
    
    def _calculate_recent_defense(self, team_data, is_home):
        """Calculate defensive quality with tiered penalties."""
        recent_conceded_pg = team_data['goals_conceded_last_5'] / 5
        
        if is_home:
            season_xga_pg = team_data['home_xga'] / team_data['matches_played']
        else:
            season_xga_pg = team_data['away_xga'] / team_data['matches_played']
        
        base_defense = (recent_conceded_pg * 0.6) + (season_xga_pg * 0.4)
        
        _, defense_penalty = self._apply_tiered_penalties(
            team_data['overall_position'],
            0,
            recent_conceded_pg,
            is_attack=False
        )
        base_defense *= defense_penalty
        
        pos_factor = self._calculate_position_factor(team_data['overall_position'], is_attack=False)
        shots_factor = team_data['shots_allowed_pg'] / self.league_params['league_avg_shots_allowed']
        
        if shots_factor < 0.85:
            shots_adj = 0.85
        elif shots_factor > 1.15:
            shots_adj = 1.15
        else:
            shots_adj = shots_factor
        
        injury_adj = 1.0 - (team_data['defenders_out'] * CONSTANTS['DEFENDER_INJURY_IMPACT'])
        injury_adj = max(0.7, injury_adj)
        
        return base_defense * pos_factor * shots_adj * injury_adj
    
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
        """Calculate expected goals with tiered penalties."""
        home_attack = self._calculate_recent_attack(home_data)
        away_defense = self._calculate_recent_defense(away_data, is_home=False)
        defense_factor_away = away_defense / self.league_params['league_avg_goals_conceded']
        home_lambda = home_attack * defense_factor_away
        
        away_attack = self._calculate_recent_attack(away_data)
        home_defense = self._calculate_recent_defense(home_data, is_home=True)
        defense_factor_home = home_defense / self.league_params['league_avg_goals_conceded']
        away_lambda = away_attack * defense_factor_home
        
        style_adjustments = self._calculate_style_adjustments(home_data, away_data)
        home_lambda += style_adjustments['home']
        away_lambda += style_adjustments['away']
        
        home_lambda *= self.league_params['home_advantage_base']
        away_lambda *= (2.0 - self.league_params['home_advantage_base'])
        
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], home_lambda))
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], away_lambda))
        
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 8:
            home_lambda *= 1.08
            away_lambda *= 0.92
        elif pos_diff <= -8:
            home_lambda *= 0.92
            away_lambda *= 1.08
        
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
        """Calculate model confidence."""
        confidence = 50
        
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.5:
            confidence += 25
        elif goal_diff > 1.0:
            confidence += 15
        elif goal_diff > 0.5:
            confidence += 5
        
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 20
        elif pos_diff >= 5:
            confidence += 10
        
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        if form_diff >= 10:
            confidence += 15
        elif form_diff >= 5:
            confidence += 8
        
        confidence = max(35, min(85, confidence))
        confidence *= self.league_params['variance_factor']
        
        return round(max(35, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors for the prediction."""
        factors = []
        
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 5:
            factors.append(f"Home position disadvantage: #{home_data['overall_position']} vs #{away_data['overall_position']}")
        elif pos_diff <= -5:
            factors.append(f"Away position disadvantage: #{away_data['overall_position']} vs #{home_data['overall_position']}")
        
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if form_diff > 5:
            factors.append(f"Home form advantage: +{form_diff} points")
        elif form_diff < -5:
            factors.append(f"Away form advantage: +{-form_diff} points")
        
        if home_data['shots_allowed_pg'] < self.league_params['league_avg_shots_allowed']:
            factors.append(f"Home strong shot suppression: {home_data['shots_allowed_pg']:.1f} shots/game")
        if away_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']:
            factors.append(f"Away defensive vulnerability: {away_data['shots_allowed_pg']:.1f} shots/game")
        
        if home_data['xg_for'] / home_data['matches_played'] > 1.5:
            factors.append(f"Home attacking strength: {home_data['xg_for']/home_data['matches_played']:.2f} xG/game")
        if away_data['xg_for'] / away_data['matches_played'] > 1.5:
            factors.append(f"Away attacking strength: {away_data['xg_for']/away_data['matches_played']:.2f} xG/game")
        
        if home_data['defenders_out'] > 0:
            factors.append(f"Home injuries: {home_data['defenders_out']} defenders out")
        if away_data['defenders_out'] > 0:
            factors.append(f"Away injuries: {away_data['defenders_out']} defenders out")
        
        if home_data['overall_position'] >= 18:
            factors.append(f"Home in relegation zone")
        elif home_data['overall_position'] >= 15:
            factors.append(f"Home in relegation battle")
        
        if away_data['overall_position'] >= 18:
            factors.append(f"Away in relegation zone")
        elif away_data['overall_position'] >= 15:
            factors.append(f"Away in relegation battle")
        
        return factors
    
    def get_market_recommendations(self, probabilities, market_odds):
        """Get clear market recommendations."""
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
            4. Ensure it has the EXACT same format as `la_liga.csv`:
            
            **Required columns (EXACTLY as shown):**
            ```
            overall_position,team,venue,matches_played,xg_for,goals,home_xga,away_xga,
            goals_conceded,home_xgdiff_def,away_xgdiff_def,defenders_out,form_last_5,
            motivation,open_play_pct,set_piece_pct,counter_attack_pct,form,
            shots_allowed_pg,home_ppg_diff,goals_scored_last_5,goals_conceded_last_5
            ```
            """)
            return None
        
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Standardize column names to lowercase with underscores
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Check for column name variations
        column_variations = {
            'xg_for': ['xG_for', 'xgfor', 'expected_goals_for', 'xgf', 'xg', 'xgoals'],
            'home_xga': ['home_xg_against', 'home_xga', 'home_xgagainst', 'home_expected_goals_against'],
            'away_xga': ['away_xg_against', 'away_xga', 'away_xgagainst', 'away_expected_goals_against'],
            'shots_allowed_pg': ['shots_allowed', 'shots_against', 'shots_conceded', 'shots_against_pg'],
        }
        
        # Try to map variations to standard names
        for standard_name, variations in column_variations.items():
            if standard_name not in df.columns:
                for variation in variations:
                    if variation.lower() in df.columns:
                        df[standard_name] = df[variation.lower()]
                        st.info(f"Mapped '{variation}' to '{standard_name}'")
                        break
        
        # Required columns EXACTLY as you specified
        required_cols = [
            'overall_position', 'team', 'venue', 'matches_played', 'xg_for', 'goals',
            'home_xga', 'away_xga', 'goals_conceded', 'home_xgdiff_def', 'away_xgdiff_def',
            'defenders_out', 'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct',
            'counter_attack_pct', 'form', 'shots_allowed_pg', 'home_ppg_diff',
            'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        # Check what columns we have
        available_cols = list(df.columns)
        missing_cols = [col for col in required_cols if col not in available_cols]
        
        if missing_cols:
            st.warning(f"⚠️ Missing columns in {league_name} data: {', '.join(missing_cols)}")
            st.info(f"Available columns: {', '.join(available_cols)}")
            
            # Try to use the first few rows to understand the data
            with st.expander("🔍 View Raw Data Structure"):
                st.write("**Original column names:**", original_columns)
                st.write("**Standardized column names:**", available_cols)
                st.write("**First 3 rows of data:**")
                st.dataframe(df.head(3))
            
            # Check if it's just capitalization issues
            for missing_col in missing_cols[:3]:  # Show first 3 issues
                similar_cols = [col for col in available_cols if missing_col.lower() in col.lower()]
                if similar_cols:
                    st.info(f"Found similar columns for '{missing_col}': {similar_cols}")
            
            return None
        
        # Validate data types and fix if needed
        numeric_cols = ['matches_played', 'xg_for', 'goals', 'home_xga', 'away_xga', 
                       'goals_conceded', 'home_xgdiff_def', 'away_xgdiff_def', 'defenders_out',
                       'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct', 
                       'counter_attack_pct', 'shots_allowed_pg', 'home_ppg_diff',
                       'goals_scored_last_5', 'goals_conceded_last_5']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with reasonable defaults
                if df[col].isna().any():
                    if col == 'xg_for':
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
    
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
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
            with col2a:
                st.metric("Recent Conceded/Game", f"{home_row['goals_conceded_last_5']/5:.1f}")
                st.metric("Form Last 5", f"{home_row['form_last_5']:.1f}")
    
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
            with col2b:
                st.metric("Recent Conceded/Game", f"{away_row['goals_conceded_last_5']/5:.1f}")
                st.metric("Form Last 5", f"{away_row['form_last_5']:.1f}")
    
    market_odds = display_market_odds_interface()
    
    if st.button("🚀 Run Advanced Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        try:
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            engine = FootballPredictionEngine(league_params)
            
            with st.spinner("Running complete analysis..."):
                result = engine.predict(home_data, away_data)
                
                if result['success']:
                    recommendations = engine.get_market_recommendations(result['probabilities'], market_odds)
                    
                    st.session_state.prediction_result = result
                    st.session_state.prediction_engine = engine
                    st.session_state.recommendations = recommendations
                    st.success("✅ Analysis complete!")
                else:
                    st.error("Prediction failed")
        
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
            for factor in result['key_factors']:
                st.markdown(f'<span style="display: inline-block; padding: 8px 16px; margin: 5px; '
                          f'border-radius: 20px; background: rgba(255,107,107,0.15); '
                          f'border: 1px solid #FF6B6B; color: #FF6B6B;">{factor}</span>', 
                          unsafe_allow_html=True)
        
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
