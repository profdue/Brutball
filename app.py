import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import json
import math
import io
import requests

# Page config - Beautiful UI/UX (EXACTLY as you had it)
st.set_page_config(
    page_title="Professional Football Prediction Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Beautiful UI/UX (EXACTLY as you had it)
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
    
    .section-header {
        font-size: 1.8rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        border-left: 5px solid #667eea;
        padding-left: 15px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.9), rgba(118,75,162,0.9));
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    .prediction-card {
        background: linear-gradient(135deg, rgba(240,147,251,0.9), rgba(245,87,108,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .yes-card {
        background: linear-gradient(135deg, rgba(0,176,155,0.9), rgba(150,201,61,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .no-card {
        background: linear-gradient(135deg, rgba(255,65,108,0.9), rgba(255,75,43,0.9));
        border-radius: 15px;
        padding: 25px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .confidence-high {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    
    .league-card {
        background: linear-gradient(135deg, rgba(69,183,209,0.9), rgba(78,205,196,0.9));
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .team-box {
        border: 2px solid #4ECDC4;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        background: rgba(78, 205, 196, 0.08);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .factor-badge {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 25px;
        margin: 8px 5px;
        font-size: 0.85em;
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
    
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
    }
    
    .input-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .footer {
        text-align: center;
        color: #666;
        padding: 30px;
        margin-top: 40px;
        border-top: 1px solid #eee;
        font-size: 0.9em;
    }
    
    .value-positive {
        color: #00b09b;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .value-negative {
        color: #ff416c;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .prediction-badge {
        display: inline-block;
        padding: 10px 25px;
        border-radius: 30px;
        font-size: 1.2em;
        font-weight: 800;
        margin: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .prediction-yes {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        border: 3px solid #00b09b;
    }
    
    .prediction-no {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border: 3px solid #ff416c;
    }
    
    .prediction-over {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: 3px solid #667eea;
    }
    
    .prediction-under {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        border: 3px solid #f093fb;
    }
    
    .warning-banner {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #ff416c;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LEAGUE-SPECIFIC AVERAGES (EXACTLY as you had it)
# ============================================================================

LEAGUE_STATS = {
    'Premier League': {
        'matches': 160,
        'goals_total': 457,
        'goals_per_match': 2.86,
        'home_goals_per_match': 1.62,
        'away_goals_per_match': 1.24,
        'home_win_pct': 0.49,
        'draw_pct': 0.21,
        'away_win_pct': 0.30,
        'over_15_pct': 0.81,
        'over_25_pct': 0.57,
        'over_35_pct': 0.29,
        'btts_pct': 0.53,
        'shots_allowed_avg': 11.2,
        'set_piece_pct': 0.25,
        'avg_goals_conceded': 1.43,
        'home_ppg': 1.68,
        'scoring_factor': 1.0,
        'lead_defending_home': 0.64,
        'lead_defending_away': 0.55,
        'equalizing_home': 0.45,
        'equalizing_away': 0.36,
        'home_advantage_factor': 1.15
    },
    'La Liga': {
        'matches': 161,
        'goals_total': 412,
        'goals_per_match': 2.56,
        'home_goals_per_match': 1.47,
        'away_goals_per_match': 1.09,
        'home_win_pct': 0.48,
        'draw_pct': 0.25,
        'away_win_pct': 0.27,
        'over_15_pct': 0.76,
        'over_25_pct': 0.47,
        'over_35_pct': 0.24,
        'btts_pct': 0.52,
        'shots_allowed_avg': 12.0,
        'set_piece_pct': 0.20,
        'avg_goals_conceded': 1.28,
        'home_ppg': 1.69,
        'scoring_factor': 0.95,
        'lead_defending_home': 0.65,
        'lead_defending_away': 0.53,
        'equalizing_home': 0.47,
        'equalizing_away': 0.35,
        'home_advantage_factor': 1.13
    },
    'Bundesliga': {
        'matches': 126,
        'goals_total': 406,
        'goals_per_match': 3.22,
        'home_goals_per_match': 1.77,
        'away_goals_per_match': 1.45,
        'home_win_pct': 0.47,
        'draw_pct': 0.21,
        'away_win_pct': 0.33,
        'over_15_pct': 0.83,
        'over_25_pct': 0.63,
        'over_35_pct': 0.42,
        'btts_pct': 0.56,
        'shots_allowed_avg': 13.5,
        'set_piece_pct': 0.22,
        'avg_goals_conceded': 1.61,
        'home_ppg': 1.62,
        'scoring_factor': 1.13,
        'lead_defending_home': 0.70,
        'lead_defending_away': 0.59,
        'equalizing_home': 0.41,
        'equalizing_away': 0.30,
        'home_advantage_factor': 1.12
    },
    'Serie A': {
        'matches': 150,
        'goals_total': 350,
        'goals_per_match': 2.33,
        'home_goals_per_match': 1.26,
        'away_goals_per_match': 1.07,
        'home_win_pct': 0.40,
        'draw_pct': 0.29,
        'away_win_pct': 0.31,
        'over_15_pct': 0.67,
        'over_25_pct': 0.44,
        'over_35_pct': 0.23,
        'btts_pct': 0.47,
        'shots_allowed_avg': 10.8,
        'set_piece_pct': 0.18,
        'avg_goals_conceded': 1.165,
        'home_ppg': 1.49,
        'scoring_factor': 0.81,
        'lead_defending_home': 0.67,
        'lead_defending_away': 0.57,
        'equalizing_home': 0.43,
        'equalizing_away': 0.33,
        'home_advantage_factor': 1.08
    },
    'Ligue 1': {
        'matches': 144,
        'goals_total': 411,
        'goals_per_match': 2.85,
        'home_goals_per_match': 1.72,
        'away_goals_per_match': 1.14,
        'home_win_pct': 0.51,
        'draw_pct': 0.22,
        'away_win_pct': 0.27,
        'over_15_pct': 0.68,
        'over_25_pct': 0.51,
        'over_35_pct': 0.33,
        'btts_pct': 0.49,
        'shots_allowed_avg': 11.8,
        'set_piece_pct': 0.23,
        'avg_goals_conceded': 1.425,
        'home_ppg': 1.75,
        'scoring_factor': 1.0,
        'lead_defending_home': 0.76,
        'lead_defending_away': 0.46,
        'equalizing_home': 0.54,
        'equalizing_away': 0.24,
        'home_advantage_factor': 1.16
    },
    'Eredivisie': {
        'matches': 143,
        'goals_total': 469,
        'goals_per_match': 3.28,
        'home_goals_per_match': 1.83,
        'away_goals_per_match': 1.45,
        'home_win_pct': 0.48,
        'draw_pct': 0.23,
        'away_win_pct': 0.29,
        'over_15_pct': 0.85,
        'over_25_pct': 0.63,
        'over_35_pct': 0.40,
        'btts_pct': 0.62,
        'shots_allowed_avg': 14.0,
        'set_piece_pct': 0.21,
        'avg_goals_conceded': 1.64,
        'home_ppg': 1.67,
        'scoring_factor': 1.15,
        'lead_defending_home': 0.57,
        'lead_defending_away': 0.53,
        'equalizing_home': 0.47,
        'equalizing_away': 0.42,
        'home_advantage_factor': 1.13
    },
    'Liga Portugal': {
        'matches': 126,
        'goals_total': 338,
        'goals_per_match': 2.68,
        'home_goals_per_match': 1.41,
        'away_goals_per_match': 1.27,
        'home_win_pct': 0.37,
        'draw_pct': 0.25,
        'away_win_pct': 0.37,
        'over_15_pct': 0.79,
        'over_25_pct': 0.52,
        'over_35_pct': 0.28,
        'btts_pct': 0.44,
        'shots_allowed_avg': 11.5,
        'set_piece_pct': 0.19,
        'avg_goals_conceded': 1.34,
        'home_ppg': 1.36,
        'scoring_factor': 0.94,
        'lead_defending_home': 0.59,
        'lead_defending_away': 0.61,
        'equalizing_home': 0.39,
        'equalizing_away': 0.41,
        'home_advantage_factor': 1.04
    },
    'Super League (Swiss)': {
        'matches': 107,
        'goals_total': 349,
        'goals_per_match': 3.26,
        'home_goals_per_match': 1.79,
        'away_goals_per_match': 1.47,
        'home_win_pct': 0.40,
        'draw_pct': 0.22,
        'away_win_pct': 0.37,
        'over_15_pct': 0.80,
        'over_25_pct': 0.68,
        'over_35_pct': 0.46,
        'btts_pct': 0.64,
        'shots_allowed_avg': 13.8,
        'set_piece_pct': 0.20,
        'avg_goals_conceded': 1.63,
        'home_ppg': 1.42,
        'scoring_factor': 1.14,
        'lead_defending_home': 0.60,
        'lead_defending_away': 0.53,
        'equalizing_home': 0.47,
        'equalizing_away': 0.40,
        'home_advantage_factor': 1.08
    }
}

def validate_league_data(df, selected_league):
    """Check if CSV data matches selected league - FIX 2"""
    
    premier_league_teams = [
        'Arsenal', 'Manchester City', 'Liverpool', 'Chelsea', 'Manchester Utd',
        'Tottenham', 'Newcastle', 'Aston Villa', 'Brighton', 'West Ham',
        'Everton', 'Brentford', 'Fulham', 'Crystal Palace', 'Wolves',
        'Nottingham Forest', 'Burnley', 'Sheffield Utd', 'Luton', 'Bournemouth'
    ]
    
    la_liga_teams = [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad',
        'Real Betis', 'Villarreal', 'Athletic Bilbao', 'Valencia', 'Getafe',
        'Osasuna', 'Celta Vigo', 'Mallorca', 'Rayo Vallecano', 'Alaves',
        'Granada', 'Cadiz', 'Las Palmas', 'Real Oviedo', 'Levante'
    ]
    
    teams_in_data = set(df['team'].unique())
    
    if selected_league == 'Premier League':
        premier_count = sum(1 for team in teams_in_data if team in premier_league_teams)
        return premier_count >= 15
    
    elif selected_league == 'La Liga':
        la_liga_count = sum(1 for team in teams_in_data if team in la_liga_teams)
        return la_liga_count >= 15
    
    return True

def detect_actual_league(df):
    """Detect which league the data belongs to"""
    teams_in_data = set(df['team'].unique())
    
    premier_league_teams = [
        'Arsenal', 'Manchester City', 'Liverpool', 'Chelsea', 'Manchester Utd',
        'Tottenham', 'Newcastle', 'Aston Villa', 'Brighton', 'West Ham',
        'Everton', 'Brentford', 'Fulham', 'Crystal Palace', 'Wolves',
        'Nottingham Forest', 'Burnley', 'Sheffield Utd', 'Luton', 'Bournemouth'
    ]
    
    la_liga_teams = [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad',
        'Real Betis', 'Villarreal', 'Athletic Bilbao', 'Valencia', 'Getafe',
        'Osasuna', 'Celta Vigo', 'Mallorca', 'Rayo Vallecano', 'Alaves',
        'Granada', 'Cadiz', 'Las Palmas'
    ]
    
    premier_count = sum(1 for team in teams_in_data if team in premier_league_teams)
    la_liga_count = sum(1 for team in teams_in_data if team in la_liga_teams)
    
    if premier_count >= 15:
        return "Premier League"
    elif la_liga_count >= 15:
        return "La Liga"
    else:
        return "Unknown League"

def display_market_odds(home_team=None, away_team=None):
    """Display market odds with smart defaults - FIX 1 & FIX 8"""
    st.markdown("### 📊 Market Odds Input")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # FIX 1: Smart defaults based on team matchup
        if home_team and away_team:
            if home_team == 'Manchester City' and away_team == 'Everton':
                default_home = 1.25
            elif home_team == 'Arsenal' and away_team == 'Manchester City':
                default_home = 2.50
            elif home_team == 'Everton' and away_team == 'Arsenal':
                default_home = 6.00
            elif home_team == 'Real Madrid' and away_team == 'Barcelona':
                default_home = 2.30
            else:
                default_home = 2.50
        else:
            default_home = 2.50
        
        # FIX 8: Input Home, Draw, AND Away odds
        home_odds = st.number_input("Home Win", min_value=1.01, value=default_home, step=0.01)
    
    with col2:
        draw_odds = st.number_input("Draw", min_value=1.01, value=3.40, step=0.01)
    
    with col3:
        # Smart defaults for away odds
        if home_team and away_team:
            if home_team == 'Manchester City' and away_team == 'Everton':
                default_away = 13.00
            elif home_team == 'Arsenal' and away_team == 'Manchester City':
                default_away = 2.80
            elif home_team == 'Everton' and away_team == 'Arsenal':
                default_away = 1.57
            elif home_team == 'Real Madrid' and away_team == 'Barcelona':
                default_away = 3.10
            else:
                default_away = 2.80
        else:
            default_away = 2.80
            
        away_odds = st.number_input("Away Win", min_value=1.01, value=default_away, step=0.01)
    
    col4, col5 = st.columns(2)
    with col4:
        over_odds = st.number_input("Over 2.5", min_value=1.01, value=1.85, step=0.01)
    
    with col5:
        btts_yes_odds = st.number_input("BTTS Yes", min_value=1.01, value=1.75, step=0.01)
    
    # Calculate implied odds
    under_odds = 1 / (1 - 1/over_odds) if over_odds > 1 else 2.00
    btts_no_odds = 1 / (1 - 1/btts_yes_odds) if btts_yes_odds > 1 else 2.00
    
    return {
        'home_win': home_odds,
        'draw': draw_odds,
        'away_win': away_odds,
        'over_25': over_odds,
        'under_25': under_odds,
        'btts_yes': btts_yes_odds,
        'btts_no': btts_no_odds
    }

def load_league_from_github(league_name):
    """Load league data from GitHub - FIX 5"""
    github_base_url = "https://raw.githubusercontent.com/profdue/Brutball/main/leagues/"
    
    league_files = {
        'Premier League': 'epl.csv',
        'La Liga': 'la_liga.csv',
    }
    
    # FIX 5: Only show leagues that actually exist
    if league_name not in league_files:
        st.error(f"⚠️ {league_name} data not available yet. Please select Premier League or La Liga.")
        return None
    
    file_name = league_files[league_name]
    url = f"{github_base_url}{file_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_content = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading data: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

class ProfessionalPredictionEngine:
    def __init__(self):
        self.reset_calculations()
        
    def reset_calculations(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.confidence = 0
        self.expected_values = {}
        self.key_factors = []
        self.betting_recommendations = []
        self.scoreline_probabilities = {}
        self.binary_predictions = {}
        self.league_stats = None
        
    def calculate_injury_level(self, defenders_out):
        """Calculate injury level (0-10 scale)"""
        return min(10, defenders_out * 2)
    
    def calculate_weighted_form(self, form_string):
        """Convert form string to weighted score"""
        if not form_string or len(form_string) < 3:
            return 9.0
        
        weights = [1.0, 0.8, 0.64, 0.51, 0.41]
        points = {'W': 3, 'D': 1, 'L': 0}
        
        last_5 = form_string[-5:] if len(form_string) >= 5 else form_string
        last_5 = last_5[::-1]
        
        weighted_score = 0
        for i, result in enumerate(last_5[:5]):
            weighted_score += points.get(result, 0) * weights[i]
        
        max_possible = sum(weights[:len(last_5)]) * 3
        normalized_score = (weighted_score / max_possible) * 15 if max_possible > 0 else 9.0
        
        return round(normalized_score, 1)
    
    def calculate_base_expected_goals(self, home_data, away_data, league_stats):
        """Calculate base expected goals with LEAGUE-SPECIFIC adjustments"""
        # FIXED: Using the actual column names from your CSV
        home_xg_total = home_data['xg']
        away_xg_total = away_data['xg']
        
        # Divide by games played to get xG per game
        home_xg_per_game = home_xg_total / home_data['games_played']
        away_xg_per_game = away_xg_total / away_data['games_played']
        
        # Apply correction factor for inflated xG values
        correction_factor = 0.5
        
        home_xg_per_game *= correction_factor
        away_xg_per_game *= correction_factor
        
        # Apply league scoring factor
        home_xg_per_game *= league_stats['scoring_factor']
        away_xg_per_game *= league_stats['scoring_factor']
        
        # Base formula with league-specific averages
        home_lambda_base = home_xg_per_game * (away_data['shots_allowed_pg'] / league_stats['shots_allowed_avg']) * 0.85
        away_lambda_base = away_xg_per_game * (home_data['shots_allowed_pg'] / league_stats['shots_allowed_avg']) * 0.85
        
        # FIX 3: Reduce team quality adjustment (1.1/0.9 instead of 1.2/0.8)
        top_teams = ['Arsenal', 'Manchester City', 'Liverpool', 'Real Madrid', 'Barcelona', 'Bayern']
        
        if home_data['team'] in top_teams and away_data['team'] not in top_teams:
            home_lambda_base *= 1.1  # FIXED: Reduced from 1.2
            away_lambda_base *= 0.9  # FIXED: Increased from 0.8
        
        if away_data['team'] in top_teams and home_data['team'] not in top_teams:
            away_lambda_base *= 1.1  # FIXED: Reduced from 1.2
            home_lambda_base *= 0.9  # FIXED: Increased from 0.8
        
        # For top matches, ensure minimum expected goals
        if (home_data['team'] in top_teams and away_data['team'] in top_teams):
            min_total_xg = 2.5
            current_total = home_lambda_base + away_lambda_base
            if current_total < min_total_xg:
                scale_factor = min_total_xg / current_total
                home_lambda_base *= scale_factor * 0.9
                away_lambda_base *= scale_factor * 0.9
        
        # Cap at reasonable values
        home_lambda_base = min(home_lambda_base, 4.0)
        away_lambda_base = min(away_lambda_base, 4.0)
        
        return home_lambda_base, away_lambda_base, home_xg_per_game, away_xg_per_game
    
    def apply_home_advantage(self, home_lambda_base, away_lambda_base, league_stats):
        """Apply LEAGUE-AVERAGE home advantage"""
        home_advantage_factor = league_stats.get('home_advantage_factor', 1.15)
        
        home_boost = home_advantage_factor
        away_penalty = 1 - ((home_advantage_factor - 1) * 0.5)
        
        home_lambda = home_lambda_base * home_boost
        away_lambda = away_lambda_base * away_penalty
        
        return home_lambda, away_lambda, home_boost, away_penalty
    
    def apply_injury_adjustment(self, home_lambda, away_lambda, home_injury_level, away_injury_level):
        """Apply injury adjustment"""
        home_defense_strength = 1 - (home_injury_level / 20)
        away_defense_strength = 1 - (away_injury_level / 20)
        
        home_lambda = home_lambda * away_defense_strength
        away_lambda = away_lambda * home_defense_strength
        
        return home_lambda, away_lambda, home_defense_strength, away_defense_strength
    
    def apply_form_adjustment(self, home_lambda, away_lambda, home_form_last_5, away_form_last_5, home_form_string=None, away_form_string=None):
        """Apply form adjustment"""
        if home_form_string:
            home_weighted_form = self.calculate_weighted_form(home_form_string)
        else:
            home_weighted_form = home_form_last_5
            
        if away_form_string:
            away_weighted_form = self.calculate_weighted_form(away_form_string)
        else:
            away_weighted_form = away_form_last_5
        
        home_form_factor = 1 + ((home_weighted_form - 9) * 0.02)
        away_form_factor = 1 + ((away_weighted_form - 9) * 0.02)
        
        home_lambda = home_lambda * home_form_factor
        away_lambda = away_lambda * away_form_factor
        
        return home_lambda, away_lambda, home_form_factor, away_form_factor
    
    def apply_motivation_adjustment(self, home_lambda, away_lambda, home_motivation, away_motivation):
        """Apply motivation adjustment"""
        home_motivation_norm = home_motivation / 5.0
        away_motivation_norm = away_motivation / 5.0
        
        home_motivation_factor = 1 + (home_motivation_norm * 0.03)
        away_motivation_factor = 1 + (away_motivation_norm * 0.03)
        
        home_lambda = home_lambda * home_motivation_factor
        away_lambda = away_lambda * away_motivation_factor
        
        return home_lambda, away_lambda, home_motivation_factor, away_motivation_factor
    
    def apply_style_matchup(self, home_lambda, away_lambda, 
                           home_set_piece_pct, away_set_piece_pct,
                           home_counter_pct, away_counter_pct,
                           home_open_play_pct, away_open_play_pct,
                           home_injury_level, away_injury_level,
                           home_shots_allowed, away_shots_allowed,
                           league_stats):
        """Apply style matchup adjustments"""
        adjustments = []
        
        if away_set_piece_pct > league_stats['set_piece_pct'] and home_injury_level > 5:
            away_lambda += 0.15
            adjustments.append(f"Away strong on set pieces ({away_set_piece_pct*100:.0f}% vs league {league_stats['set_piece_pct']*100:.0f}%)")
        
        if away_counter_pct > 0.10:
            away_lambda += 0.10
            adjustments.append(f"Away effective on counter ({away_counter_pct*100:.0f}% of goals)")
        
        if home_open_play_pct > 0.60 and away_shots_allowed > league_stats['shots_allowed_avg']:
            home_lambda += 0.05
            adjustments.append(f"Home dominant in open play ({home_open_play_pct*100:.0f}% of goals)")
            
        return home_lambda, away_lambda, adjustments
    
    def apply_defense_form(self, home_lambda, away_lambda, 
                          home_goals_conceded_last_5, away_goals_conceded_last_5,
                          league_stats):
        """Apply defense form adjustment"""
        home_defense_form = home_goals_conceded_last_5 / 5
        away_defense_form = away_goals_conceded_last_5 / 5
        
        league_avg_goals_conceded = league_stats['avg_goals_conceded']
        
        home_lambda = home_lambda * (1 + (away_defense_form - league_avg_goals_conceded) * 0.1)
        away_lambda = away_lambda * (1 + (home_defense_form - league_avg_goals_conceded) * 0.1)
        
        return home_lambda, away_lambda, home_defense_form, away_defense_form
    
    def poisson_pmf(self, k, lambda_val):
        """Poisson probability mass function"""
        if k > 20:
            return 0
        return (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
    
    def simulate_match(self, home_lambda, away_lambda, iterations=10000):
        """Poisson simulation - FIX 4"""
        home_goals = np.random.poisson(home_lambda, iterations)
        away_goals = np.random.poisson(away_lambda, iterations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        over_25 = np.sum(home_goals + away_goals > 2.5)
        under_25 = np.sum(home_goals + away_goals < 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        btts_no = np.sum((home_goals == 0) | (away_goals == 0))
        
        probabilities = {
            'home_win': home_wins / iterations,
            'draw': draws / iterations,
            'away_win': away_wins / iterations,
            'over_25': over_25 / iterations,
            'under_25': under_25 / iterations,
            'btts_yes': btts_yes / iterations,
            'btts_no': btts_no / iterations
        }
        
        # FIX 4: Apply probability caps
        probabilities['home_win'] = min(probabilities['home_win'], 0.80)
        probabilities['away_win'] = min(probabilities['away_win'], 0.80)
        probabilities['draw'] = max(probabilities['draw'], 0.10)
        
        # Re-normalize
        total = probabilities['home_win'] + probabilities['draw'] + probabilities['away_win']
        if total > 0:
            probabilities['home_win'] /= total
            probabilities['draw'] /= total
            probabilities['away_win'] /= total
        
        return probabilities, home_goals, away_goals
    
    def calculate_binary_predictions(self, probabilities, league_stats):
        """Make binary predictions with LEAGUE-SPECIFIC benchmarks"""
        binary_preds = {}
        
        btts_yes_prob = probabilities['btts_yes']
        league_btts_avg = league_stats['btts_pct']
        
        if btts_yes_prob > league_btts_avg:
            binary_preds['btts'] = {
                'prediction': 'YES',
                'probability': btts_yes_prob,
                'confidence': (btts_yes_prob - league_btts_avg) * 100,
                'opposite_prob': probabilities['btts_no'],
                'league_avg': league_btts_avg
            }
        else:
            binary_preds['btts'] = {
                'prediction': 'NO',
                'probability': probabilities['btts_no'],
                'confidence': (probabilities['btts_no'] - (1 - league_btts_avg)) * 100,
                'opposite_prob': btts_yes_prob,
                'league_avg': league_btts_avg
            }
        
        over_prob = probabilities['over_25']
        league_over_avg = league_stats['over_25_pct']
        
        if over_prob > league_over_avg:
            binary_preds['over_under'] = {
                'prediction': 'OVER',
                'probability': over_prob,
                'confidence': (over_prob - league_over_avg) * 100,
                'opposite_prob': probabilities['under_25'],
                'league_avg': league_over_avg
            }
        else:
            binary_preds['over_under'] = {
                'prediction': 'UNDER',
                'probability': probabilities['under_25'],
                'confidence': (probabilities['under_25'] - (1 - league_over_avg)) * 100,
                'opposite_prob': over_prob,
                'league_avg': league_over_avg
            }
        
        return binary_preds
    
    def calculate_scoreline_probabilities(self, home_lambda, away_lambda, max_goals=6):
        """Calculate scoreline probabilities"""
        scorelines = {}
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = self.poisson_pmf(i, home_lambda) * self.poisson_pmf(j, away_lambda)
                if prob > 0.0001:
                    scorelines[f"{i}-{j}"] = prob
        
        if scorelines:
            sorted_scores = sorted(scorelines.items(), key=lambda x: x[1], reverse=True)
            predicted_score = sorted_scores[0][0]
            return dict(sorted_scores[:10]), predicted_score
        else:
            return {"1-1": 0.1, "1-0": 0.08, "2-1": 0.07, "0-0": 0.06, "0-1": 0.05}, "1-1"
    
    def calculate_confidence(self, home_lambda, away_lambda, 
                           home_injury_level, away_injury_level,
                           form_diff, league_stats):
        """Calculate confidence with LEAGUE context"""
        confidence = 0.5
        
        goal_diff = abs(home_lambda - away_lambda)
        league_avg_diff = league_stats['home_goals_per_match'] - league_stats['away_goals_per_match']
        
        if goal_diff > league_avg_diff * 2:
            confidence += 0.2
        elif goal_diff > league_avg_diff:
            confidence += 0.1
        
        injury_diff = abs(home_injury_level - away_injury_level)
        if injury_diff > 4:
            confidence += 0.15
        
        if abs(form_diff) > 4:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    def calculate_expected_value(self, probability, market_odds):
        """Calculate expected value"""
        if probability == 0 or market_odds == 0:
            return -1
        fair_odds = 1 / probability
        expected_value = (market_odds / fair_odds) - 1
        return expected_value
    
    def get_predicted_outcome(self, probabilities):
        """Get the outcome predicted by the model - PART OF FIX 7"""
        home_prob = probabilities['home_win']
        away_prob = probabilities['away_win']
        draw_prob = probabilities['draw']
        
        if home_prob > away_prob and home_prob > draw_prob:
            return 'HOME'
        elif away_prob > home_prob and away_prob > draw_prob:
            return 'AWAY'
        else:
            return 'DRAW'
    
    def get_betting_recommendations(self, probabilities, binary_preds, market_odds, confidence, league_stats):
        """Get betting recommendations - FIX 7 (COMPLETE FIX)"""
        recommendations = []
        
        # FIX 7: Get model's predicted outcome FIRST
        predicted_outcome = self.get_predicted_outcome(probabilities)
        
        # Check value for each possible outcome
        ev_home = self.calculate_expected_value(probabilities['home_win'], market_odds['home_win'])
        ev_draw = self.calculate_expected_value(probabilities['draw'], market_odds['draw'])
        ev_away = self.calculate_expected_value(probabilities['away_win'], market_odds['away_win'])
        
        # FIX 7: Only recommend if model predicts that outcome AND there's value
        if predicted_outcome == 'HOME' and ev_home > 0.10 and probabilities['home_win'] > 0.20:
            fair_odds_home = 1 / probabilities['home_win']
            recommendations.append({
                'market': 'Match Result',
                'prediction': 'HOME',
                'probability': probabilities['home_win'],
                'market_odds': market_odds['home_win'],
                'fair_odds': fair_odds_home,
                'ev': ev_home,
                'reason': f"Model predicts HOME win ({probabilities['home_win']*100:.1f}%) vs market implied ({1/market_odds['home_win']*100:.1f}%)",
                'confidence': confidence
            })
        
        elif predicted_outcome == 'AWAY' and ev_away > 0.10 and probabilities['away_win'] > 0.20:
            fair_odds_away = 1 / probabilities['away_win']
            recommendations.append({
                'market': 'Match Result',
                'prediction': 'AWAY',
                'probability': probabilities['away_win'],
                'market_odds': market_odds['away_win'],
                'fair_odds': fair_odds_away,
                'ev': ev_away,
                'reason': f"Model predicts AWAY win ({probabilities['away_win']*100:.1f}%) vs market implied ({1/market_odds['away_win']*100:.1f}%)",
                'confidence': confidence
            })
        
        elif predicted_outcome == 'DRAW' and ev_draw > 0.10 and probabilities['draw'] > 0.15:
            fair_odds_draw = 1 / probabilities['draw']
            recommendations.append({
                'market': 'Match Result',
                'prediction': 'DRAW',
                'probability': probabilities['draw'],
                'market_odds': market_odds['draw'],
                'fair_odds': fair_odds_draw,
                'ev': ev_draw,
                'reason': f"Model predicts DRAW ({probabilities['draw']*100:.1f}%) vs market implied ({1/market_odds['draw']*100:.1f}%)",
                'confidence': confidence
            })
        
        # Check Over/Under 2.5
        over_prob = probabilities['over_25']
        under_prob = probabilities['under_25']
        ev_over = self.calculate_expected_value(over_prob, market_odds['over_25'])
        ev_under = self.calculate_expected_value(under_prob, market_odds['under_25'])
        
        league_over_avg = league_stats['over_25_pct']
        
        if over_prob > league_over_avg and ev_over > 0.10:
            fair_odds_over = 1 / over_prob
            recommendations.append({
                'market': 'Over/Under 2.5',
                'prediction': 'OVER',
                'probability': over_prob,
                'market_odds': market_odds['over_25'],
                'fair_odds': fair_odds_over,
                'ev': ev_over,
                'reason': f"Model predicts OVER ({over_prob*100:.1f}%) vs market implied ({1/market_odds['over_25']*100:.1f}%)",
                'confidence': abs(over_prob - league_over_avg) * 100
            })
        elif under_prob > (1 - league_over_avg) and ev_under > 0.10:
            fair_odds_under = 1 / under_prob
            recommendations.append({
                'market': 'Over/Under 2.5',
                'prediction': 'UNDER',
                'probability': under_prob,
                'market_odds': market_odds['under_25'],
                'fair_odds': fair_odds_under,
                'ev': ev_under,
                'reason': f"Model predicts UNDER ({under_prob*100:.1f}%) vs market implied ({1/market_odds['under_25']*100:.1f}%)",
                'confidence': abs(under_prob - (1 - league_over_avg)) * 100
            })
        
        # Check BTTS
        btts_yes_prob = probabilities['btts_yes']
        btts_no_prob = probabilities['btts_no']
        ev_btts_yes = self.calculate_expected_value(btts_yes_prob, market_odds['btts_yes'])
        ev_btts_no = self.calculate_expected_value(btts_no_prob, market_odds['btts_no'])
        
        league_btts_avg = league_stats['btts_pct']
        
        if btts_yes_prob > league_btts_avg and ev_btts_yes > 0.10:
            fair_odds_btts_yes = 1 / btts_yes_prob
            recommendations.append({
                'market': 'Both Teams to Score',
                'prediction': 'YES',
                'probability': btts_yes_prob,
                'market_odds': market_odds['btts_yes'],
                'fair_odds': fair_odds_btts_yes,
                'ev': ev_btts_yes,
                'reason': f"Model predicts BTTS YES ({btts_yes_prob*100:.1f}%) vs market implied ({1/market_odds['btts_yes']*100:.1f}%)",
                'confidence': abs(btts_yes_prob - league_btts_avg) * 100
            })
        elif btts_no_prob > (1 - league_btts_avg) and ev_btts_no > 0.10:
            fair_odds_btts_no = 1 / btts_no_prob
            recommendations.append({
                'market': 'Both Teams to Score',
                'prediction': 'NO',
                'probability': btts_no_prob,
                'market_odds': market_odds['btts_no'],
                'fair_odds': fair_odds_btts_no,
                'ev': ev_btts_no,
                'reason': f"Model predicts BTTS NO ({btts_no_prob*100:.1f}%) vs market implied ({1/market_odds['btts_no']*100:.1f}%)",
                'confidence': abs(btts_no_prob - (1 - league_btts_avg)) * 100
            })
        
        return recommendations
    
    def display_odds_comparison(self, probabilities, market_odds):
        """Show model vs market comparison"""
        model_home = probabilities['home_win'] * 100
        model_draw = probabilities['draw'] * 100
        model_away = probabilities['away_win'] * 100
        
        market_home = (1 / market_odds['home_win']) * 100 if market_odds['home_win'] > 0 else 0
        market_draw = (1 / market_odds['draw']) * 100 if market_odds['draw'] > 0 else 0
        market_away = (1 / market_odds['away_win']) * 100 if market_odds['away_win'] > 0 else 0
        
        fig = go.Figure(data=[
            go.Bar(name='Model Probability', x=['Home', 'Draw', 'Away'], 
                   y=[model_home, model_draw, model_away], marker_color='#4ECDC4'),
            go.Bar(name='Market Implied', x=['Home', 'Draw', 'Away'], 
                   y=[market_home, market_draw, market_away], marker_color='#FF6B6B')
        ])
        
        fig.update_layout(
            title="📊 Model vs Market View",
            barmode='group',
            yaxis_title="Probability (%)",
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def predict(self, home_data, away_data, league_stats):
        """Main prediction function"""
        self.reset_calculations()
        self.league_stats = league_stats
        
        # Calculate injury levels
        home_injury_level = self.calculate_injury_level(home_data['defenders_out'])
        away_injury_level = self.calculate_injury_level(away_data['defenders_out'])
        
        # 1. Calculate base expected goals
        home_lambda_base, away_lambda_base, home_xg_per_game, away_xg_per_game = \
            self.calculate_base_expected_goals(home_data, away_data, league_stats)
        
        # 2. Apply home advantage
        home_lambda, away_lambda, home_boost, away_penalty = \
            self.apply_home_advantage(home_lambda_base, away_lambda_base, league_stats)
        
        # 3. Apply injury adjustment
        home_lambda, away_lambda, home_defense_strength, away_defense_strength = \
            self.apply_injury_adjustment(home_lambda, away_lambda, home_injury_level, away_injury_level)
        
        # 4. Apply form adjustment
        home_form_string = home_data.get('form', '')
        away_form_string = away_data.get('form', '')
        
        home_lambda, away_lambda, home_form_factor, away_form_factor = \
            self.apply_form_adjustment(home_lambda, away_lambda, 
                                      home_data['form_last_5'], away_data['form_last_5'],
                                      home_form_string, away_form_string)
        
        # 5. Apply motivation adjustment
        home_lambda, away_lambda, home_motivation_factor, away_motivation_factor = \
            self.apply_motivation_adjustment(home_lambda, away_lambda, 
                                           home_data['motivation'], away_data['motivation'])
        
        # 6. Apply style matchup
        style_adjustments = []
        if all(key in home_data for key in ['set_piece_pct', 'counter_attack_pct', 'open_play_pct']):
            home_lambda, away_lambda, style_adj = \
                self.apply_style_matchup(home_lambda, away_lambda,
                                       home_data['set_piece_pct'], away_data['set_piece_pct'],
                                       home_data['counter_attack_pct'], away_data['counter_attack_pct'],
                                       home_data['open_play_pct'], away_data['open_play_pct'],
                                       home_injury_level, away_injury_level,
                                       away_data['shots_allowed_pg'], home_data['shots_allowed_pg'],
                                       league_stats)
            style_adjustments.extend(style_adj)
        
        # 7. Apply defense form
        home_lambda, away_lambda, home_defense_form, away_defense_form = \
            self.apply_defense_form(home_lambda, away_lambda,
                                  home_data['goals_conceded_last_5'], away_data['goals_conceded_last_5'],
                                  league_stats)
        
        # Store final lambdas
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # 8. Run simulation
        probabilities, home_goals, away_goals = self.simulate_match(home_lambda, away_lambda)
        self.probabilities = probabilities
        
        # 9. Calculate binary predictions
        self.binary_predictions = self.calculate_binary_predictions(probabilities, league_stats)
        
        # 10. Calculate scoreline probabilities
        self.scoreline_probabilities, predicted_score = \
            self.calculate_scoreline_probabilities(home_lambda, away_lambda)
        
        # 11. Calculate confidence
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        self.confidence = self.calculate_confidence(home_lambda, away_lambda,
                                                   home_injury_level, away_injury_level,
                                                   form_diff, league_stats)
        
        # 12. Collect key factors
        self.key_factors = []
        
        if home_boost > 1.1:
            self.key_factors.append(f"Strong home advantage ({home_boost:.2f}x)")
        
        if home_injury_level > 5:
            self.key_factors.append(f"Home injury issues ({home_injury_level}/10)")
        if away_injury_level > 5:
            self.key_factors.append(f"Away injury issues ({away_injury_level}/10)")
        
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if abs(form_diff) > 2:
            if form_diff > 0:
                self.key_factors.append(f"Home in better form ({home_data['form_last_5']:.1f} vs {away_data['form_last_5']:.1f})")
            else:
                self.key_factors.append(f"Away in better form ({away_data['form_last_5']:.1f} vs {home_data['form_last_5']:.1f})")
        
        if home_motivation_factor > 1.05:
            self.key_factors.append(f"High home motivation ({home_data['motivation']}/5)")
        if away_motivation_factor > 1.05:
            self.key_factors.append(f"High away motivation ({away_data['motivation']}/5)")
        
        self.key_factors.extend(style_adjustments)
        
        return {
            'probabilities': probabilities,
            'binary_predictions': self.binary_predictions,
            'scoreline_probabilities': self.scoreline_probabilities,
            'predicted_score': predicted_score,
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'confidence': self.confidence,
            'key_factors': self.key_factors,
            'home_lambda': home_lambda,
            'away_lambda': away_lambda
        }

def main():
    # Header (EXACTLY as you had it)
    st.markdown('<h1 class="main-header">⚽ Professional Football Prediction Engine</h1>', unsafe_allow_html=True)
    
    # Sidebar (EXACTLY as you had it)
    with st.sidebar:
        st.markdown("### 🏆 Select League")
        
        available_leagues = ['Premier League', 'La Liga']
        selected_league = st.selectbox("Choose League:", available_leagues)
        
        st.markdown("---")
        st.markdown("### 📈 League Stats Preview")
        
        if selected_league in LEAGUE_STATS:
            league_stats = LEAGUE_STATS[selected_league]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Goals/Match", f"{league_stats['goals_per_match']:.2f}")
                st.metric("Home Win %", f"{league_stats['home_win_pct']*100:.0f}%")
                st.metric("Over 2.5 %", f"{league_stats['over_25_pct']*100:.0f}%")
            
            with col2:
                st.metric("BTTS %", f"{league_stats['btts_pct']*100:.0f}%")
                st.metric("Draw %", f"{league_stats['draw_pct']*100:.0f}%")
                st.metric("Away Win %", f"{league_stats['away_win_pct']*100:.0f}%")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        simulation_iterations = st.slider("Simulation Iterations:", 1000, 50000, 10000, 1000)
        
        st.markdown("---")
        st.markdown("### 📊 How It Works")
        st.info("""
        1. **Select League** and load data
        2. **Choose Teams** for prediction
        3. **Input Market Odds** for value betting
        4. **Run Analysis** to get predictions
        5. **Check Recommendations** for betting value
        """)
    
    # Main content area
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 📥 Load League Data")
    
    # Load data button
    if st.button(f"📂 Load {selected_league} Data", type="primary"):
        with st.spinner(f"Loading {selected_league} data from GitHub..."):
            df = load_league_from_github(selected_league)
            
            if df is not None:
                st.session_state['league_data'] = df
                st.session_state['selected_league'] = selected_league
                
                # FIX 6: Check for data mismatch warning
                if not validate_league_data(df, selected_league):
                    actual_league = detect_actual_league(df)
                    st.error(f"""
                    ⚠️ **DATA MISMATCH WARNING**
                    
                    Selected league: **{selected_league}**
                    But data contains teams from: **{actual_league}**
                    
                    This will affect prediction accuracy!
                    """)
                else:
                    st.success(f"✅ Successfully loaded {selected_league} data with {len(df)} teams!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if data is loaded
    if 'league_data' not in st.session_state:
        st.warning("Please load league data first using the button above.")
        return
    
    df = st.session_state['league_data']
    selected_league = st.session_state['selected_league']
    
    # Team selection (EXACTLY as you had it with correct column names)
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("## 🏟️ Match Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", sorted(df['team'].unique()))
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        
        st.markdown(f"**{home_team} Stats:**")
        st.metric("Form (Last 5)", f"{home_data['form_last_5']:.1f}")
        # FIXED: Using 'goals' from your CSV, not 'goals_scored'
        st.metric("Goals Scored", f"{home_data['goals']}")
        st.metric("Defenders Out", f"{home_data['defenders_out']}")
    
    with col2:
        away_team = st.selectbox("✈️ Away Team:", sorted(df['team'].unique()))
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        st.markdown(f"**{away_team} Stats:**")
        st.metric("Form (Last 5)", f"{away_data['form_last_5']:.1f}")
        # FIXED: Using 'goals' from your CSV, not 'goals_scored'
        st.metric("Goals Scored", f"{away_data['goals']}")
        st.metric("Defenders Out", f"{away_data['defenders_out']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market odds input
    market_odds = display_market_odds(home_team, away_team)
    
    # Run prediction button
    if st.button("🚀 Run Prediction Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        # Initialize engine
        engine = ProfessionalPredictionEngine()
        
        # Run prediction
        with st.spinner("Running advanced prediction model..."):
            progress_bar = st.progress(0)
            
            # Simulate progress
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Get league stats
            league_stats = LEAGUE_STATS[selected_league]
            
            # Run prediction
            result = engine.predict(home_data, away_data, league_stats)
            
            # Calculate betting recommendations
            recommendations = engine.get_betting_recommendations(
                result['probabilities'],
                result['binary_predictions'],
                market_odds,
                result['confidence'],
                league_stats
            )
            
            st.session_state['result'] = result
            st.session_state['recommendations'] = recommendations
            st.session_state['market_odds'] = market_odds
    
    # Display results if available
    if 'result' in st.session_state:
        result = st.session_state['result']
        recommendations = st.session_state['recommendations']
        market_odds = st.session_state['market_odds']
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Match header
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"<h2 style='text-align: center;'>🏠 {home_team}</h2>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h2 style='text-align: center;'>✈️ {away_team}</h2>", unsafe_allow_html=True)
        
        # Model vs Market Comparison
        st.markdown("---")
        st.markdown("### 📈 Model vs Market View")
        
        fig = engine.display_odds_comparison(result['probabilities'], market_odds)
        st.plotly_chart(fig, use_container_width=True)
        
        # Main predictions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            home_win_prob = result['probabilities']['home_win'] * 100
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Home Win Probability", f"{home_win_prob:.1f}%", 
                     f"Fair odds: {1/result['probabilities']['home_win']:.2f}" if result['probabilities']['home_win'] > 0 else "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            draw_prob = result['probabilities']['draw'] * 100
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Draw Probability", f"{draw_prob:.1f}%",
                     f"Fair odds: {1/result['probabilities']['draw']:.2f}" if result['probabilities']['draw'] > 0 else "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            away_win_prob = result['probabilities']['away_win'] * 100
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Away Win Probability", f"{away_win_prob:.1f}%",
                     f"Fair odds: {1/result['probabilities']['away_win']:.2f}" if result['probabilities']['away_win'] > 0 else "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Predicted score
        st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 Predicted Score: **{result['predicted_score']}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Expected goals
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Home Expected Goals", f"{result['expected_goals']['home']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Away Expected Goals", f"{result['expected_goals']['away']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Binary predictions
        st.markdown("---")
        st.markdown("### 🔍 Binary Predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            btts_pred = result['binary_predictions']['btts']
            if btts_pred['prediction'] == 'YES':
                st.markdown('<div class="yes-card">', unsafe_allow_html=True)
                st.markdown(f"#### ✅ Both Teams to Score: **YES**")
                st.metric("Probability", f"{btts_pred['probability']*100:.1f}%")
                st.metric("League Average", f"{btts_pred['league_avg']*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-card">', unsafe_allow_html=True)
                st.markdown(f"#### ❌ Both Teams to Score: **NO**")
                st.metric("Probability", f"{btts_pred['probability']*100:.1f}%")
                st.metric("League Average", f"{(1-btts_pred['league_avg'])*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            over_under_pred = result['binary_predictions']['over_under']
            if over_under_pred['prediction'] == 'OVER':
                st.markdown('<div class="yes-card">', unsafe_allow_html=True)
                st.markdown(f"#### ✅ Over 2.5 Goals: **YES**")
                st.metric("Probability", f"{over_under_pred['probability']*100:.1f}%")
                st.metric("League Average", f"{over_under_pred['league_avg']*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-card">', unsafe_allow_html=True)
                st.markdown(f"#### ❌ Over 2.5 Goals: **NO**")
                st.metric("Probability", f"{over_under_pred['probability']*100:.1f}%")
                st.metric("League Average", f"{(1-over_under_pred['league_avg'])*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Betting recommendations
        st.markdown("---")
        st.markdown("### 💰 Betting Recommendations")
        
        if recommendations:
            for rec in recommendations:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{rec['market']} - {rec['prediction']}**")
                    st.markdown(f"*{rec['reason']}*")
                
                with col2:
                    ev_pct = rec['ev'] * 100
                    if ev_pct > 0:
                        st.markdown(f'<div class="value-positive">+{ev_pct:.1f}% EV</div>', unsafe_allow_html=True)
                        st.markdown(f"Odds: {rec['market_odds']:.2f}")
                    else:
                        st.markdown(f'<div class="value-negative">{ev_pct:.1f}% EV</div>', unsafe_allow_html=True)
                
                st.markdown("---")
        else:
            st.info("No strong betting recommendations based on current market odds.")
        
        # Key factors
        st.markdown("### 🔑 Key Factors Influencing Prediction")
        
        for factor in result['key_factors']:
            st.markdown(f'<span class="factor-badge">{factor}</span>', unsafe_allow_html=True)
        
        # Scoreline probabilities
        st.markdown("---")
        st.markdown("### 📊 Most Likely Scorelines")
        
        scorelines = result['scoreline_probabilities']
        score_df = pd.DataFrame(list(scorelines.items()), columns=['Scoreline', 'Probability'])
        score_df['Probability'] = score_df['Probability'] * 100
        
        fig = go.Figure(data=[
            go.Bar(x=score_df['Scoreline'], y=score_df['Probability'],
                   marker_color='#4ECDC4')
        ])
        
        fig.update_layout(
            title="Scoreline Probabilities",
            xaxis_title="Scoreline",
            yaxis_title="Probability (%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Confidence
        st.markdown("---")
        confidence_pct = result['confidence'] * 100
        
        if confidence_pct > 70:
            st.markdown('<div class="confidence-high">', unsafe_allow_html=True)
            st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
            st.markdown("High confidence prediction")
            st.markdown('</div>', unsafe_allow_html=True)
        elif confidence_pct > 50:
            st.markdown('<div class="confidence-medium">', unsafe_allow_html=True)
            st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
            st.markdown("Medium confidence prediction")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="confidence-low">', unsafe_allow_html=True)
            st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
            st.markdown("Low confidence prediction - consider with caution")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
