import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import math
import io
import requests
from scipy import stats

# Page configuration
st.set_page_config(page_title="Advanced Football Predictor", page_icon="⚽", layout="wide")

# ============================================================================
# LEAGUE-SPECIFIC PARAMETERS & CONSTANTS
# ============================================================================

LEAGUE_PARAMS = {
    'LA LIGA': {
        'league_avg_goals_conceded': 1.26,
        'league_avg_shots_allowed': 12.3,
        'home_advantage_base': 1.12,
        'variance_factor': 0.95,
    },
    'PREMIER LEAGUE': {
        'league_avg_goals_conceded': 1.42,
        'league_avg_shots_allowed': 12.7,
        'home_advantage_base': 1.15,
        'variance_factor': 1.05,
    }
}

CONSTANTS = {
    'POISSON_SIMULATIONS': 20000,
    'MAX_GOALS_CONSIDERED': 6,
    'MIN_LAMBDA': 0.3,
    'MAX_LAMBDA': 4.0,
    'SET_PIECE_THRESHOLD': 0.15,
    'COUNTER_ATTACK_THRESHOLD': 0.15,
    'DEFENDER_INJURY_IMPACT': 0.08,
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
    
    def _calculate_position_factor(self, position, is_attack=True):
        """Calculate position-based multiplier for attack/defense."""
        if position <= 4:          # Top 4
            return 1.2 if is_attack else 0.8
        elif position <= 10:       # Upper mid-table
            return 1.1 if is_attack else 0.9
        elif position <= 16:       # Lower mid-table
            return 0.9 if is_attack else 1.1
        else:                      # Relegation zone
            return 0.8 if is_attack else 1.2
    
    def _calculate_recent_attack(self, team_data):
        """Calculate attack strength based on recent performance and position."""
        # Use recent goals as primary indicator
        recent_goals_pg = team_data['goals_scored_last_5'] / 5
        
        # Position-based attack boost
        pos_boost = self._calculate_position_factor(team_data['overall_position'], is_attack=True)
        
        # Finishing efficiency adjustment
        if team_data['xg_for'] > 0:
            finishing_ratio = team_data['goals'] / team_data['xg_for']
            finishing_adj = max(0.7, min(1.3, finishing_ratio))
        else:
            finishing_adj = 1.0
        
        # Form momentum (from form_last_5)
        form_score = min(team_data['form_last_5'] / 15, 1.0)
        form_adj = 0.7 + (0.3 * form_score)
        
        # Motivation adjustment
        motivation_adj = 1.0 + (team_data['motivation'] - 3) * 0.02
        
        return recent_goals_pg * pos_boost * finishing_adj * form_adj * motivation_adj
    
    def _calculate_recent_defense(self, team_data, is_home):
        """Calculate defensive quality based on recent performance and position."""
        # Use recent goals conceded as primary indicator
        recent_conceded_pg = team_data['goals_conceded_last_5'] / 5
        
        # Position-based defense factor
        pos_factor = self._calculate_position_factor(team_data['overall_position'], is_attack=False)
        
        # Shot suppression factor
        shots_factor = team_data['shots_allowed_pg'] / self.league_params['league_avg_shots_allowed']
        if shots_factor < 0.9:
            shots_adj = 0.9
        elif shots_factor > 1.1:
            shots_adj = 1.1
        else:
            shots_adj = 1.0
        
        # Injury impact
        injury_adj = 1.0 - (team_data['defenders_out'] * CONSTANTS['DEFENDER_INJURY_IMPACT'])
        injury_adj = max(0.6, injury_adj)
        
        # Venue-specific adjustment
        if is_home:
            venue_adj = 1.0 + (team_data.get('home_ppg_diff', 0) * 0.1)
        else:
            venue_adj = 1.0
        
        return recent_conceded_pg * pos_factor * shots_adj * injury_adj * venue_adj
    
    def _calculate_style_adjustments(self, home_data, away_data):
        """Calculate style matchup adjustments."""
        adjustments = {'home': 0, 'away': 0}
        
        # Set piece advantage
        set_piece_diff = home_data['set_piece_pct'] - away_data['set_piece_pct']
        if abs(set_piece_diff) > CONSTANTS['SET_PIECE_THRESHOLD']:
            if set_piece_diff > 0:
                # Home advantage, but weighted by position difference
                pos_diff = away_data['overall_position'] - home_data['overall_position']
                if pos_diff > 3:  # Home is much stronger
                    adjustments['home'] += 0.10
                else:
                    adjustments['home'] += 0.05
                self.key_factors.append(f"Home set piece advantage: {set_piece_diff:.0%}")
            else:
                pos_diff = home_data['overall_position'] - away_data['overall_position']
                if pos_diff > 3:  # Away is much stronger
                    adjustments['away'] += 0.10
                else:
                    adjustments['away'] += 0.05
                self.key_factors.append(f"Away set piece advantage: {-set_piece_diff:.0%}")
        
        # Counter attack threat
        if (away_data['counter_attack_pct'] > CONSTANTS['COUNTER_ATTACK_THRESHOLD'] and 
            home_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']):
            adjustments['away'] += 0.08
            self.key_factors.append("Away counter attack threat")
        
        return adjustments
    
    def calculate_expected_goals(self, home_data, away_data):
        """Calculate expected goals for both teams."""
        # Home team expected goals
        home_attack = self._calculate_recent_attack(home_data)
        away_defense = self._calculate_recent_defense(away_data, is_home=False)
        defense_factor_away = away_defense / self.league_params['league_avg_goals_conceded']
        
        home_lambda = home_attack * defense_factor_away
        
        # Away team expected goals
        away_attack = self._calculate_recent_attack(away_data)
        home_defense = self._calculate_recent_defense(home_data, is_home=True)
        defense_factor_home = home_defense / self.league_params['league_avg_goals_conceded']
        
        away_lambda = away_attack * defense_factor_home
        
        # Apply style adjustments
        style_adjustments = self._calculate_style_adjustments(home_data, away_data)
        home_lambda += style_adjustments['home']
        away_lambda += style_adjustments['away']
        
        # Apply venue adjustments
        home_lambda *= self.league_params['home_advantage_base']
        away_lambda *= (2.0 - self.league_params['home_advantage_base'])  # Complementary away factor
        
        # Apply bounds
        home_lambda = max(CONSTANTS['MIN_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], home_lambda))
        away_lambda = max(CONSTANTS['MIN_LAMBDA'], min(CONSTANTS['MAX_LAMBDA'], away_lambda))
        
        # Add position difference factor
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 8:  # Home playing much weaker team
            home_lambda *= 0.9
            away_lambda *= 1.1
        elif pos_diff <= -8:  # Home playing much stronger team
            home_lambda *= 1.1
            away_lambda *= 0.9
        
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
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        
        probabilities = {
            'home_win': home_wins / simulations,
            'draw': draws / simulations,
            'away_win': away_wins / simulations,
            'over_25': over_25 / simulations,
            'btts_yes': btts_yes / simulations,
        }
        
        # Calculate scoreline probabilities
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
        
        # Goal difference clarity
        goal_diff = abs(home_lambda - away_lambda)
        if goal_diff > 1.5:
            confidence += 25
        elif goal_diff > 1.0:
            confidence += 15
        elif goal_diff > 0.5:
            confidence += 5
        
        # Position difference clarity
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 20
        elif pos_diff >= 5:
            confidence += 10
        
        # Form difference clarity
        form_diff = abs(home_data['form_last_5'] - away_data['form_last_5'])
        if form_diff >= 10:
            confidence += 15
        elif form_diff >= 5:
            confidence += 8
        
        # Apply bounds and variance factor
        confidence = max(35, min(85, confidence))
        confidence *= self.league_params['variance_factor']
        
        return round(max(35, min(85, confidence)), 1)
    
    def generate_key_factors(self, home_data, away_data, home_lambda, away_lambda):
        """Generate key factors for the prediction."""
        factors = []
        
        # Position factors
        pos_diff = away_data['overall_position'] - home_data['overall_position']
        if pos_diff >= 5:
            factors.append(f"Home position advantage: {home_data['overall_position']} vs {away_data['overall_position']}")
        elif pos_diff <= -5:
            factors.append(f"Away position advantage: {away_data['overall_position']} vs {home_data['overall_position']}")
        
        # Form factors
        form_diff = home_data['form_last_5'] - away_data['form_last_5']
        if form_diff > 5:
            factors.append(f"Home form advantage: +{form_diff} points")
        elif form_diff < -5:
            factors.append(f"Away form advantage: +{-form_diff} points")
        
        # Defensive factors
        if home_data['shots_allowed_pg'] < self.league_params['league_avg_shots_allowed']:
            factors.append(f"Home strong shot suppression: {home_data['shots_allowed_pg']:.1f} shots/game")
        if away_data['shots_allowed_pg'] > self.league_params['league_avg_shots_allowed']:
            factors.append(f"Away defensive vulnerability: {away_data['shots_allowed_pg']:.1f} shots/game")
        
        # Injury factors
        if home_data['defenders_out'] > 0:
            factors.append(f"Home injuries: {home_data['defenders_out']} defenders out")
        if away_data['defenders_out'] > 0:
            factors.append(f"Away injuries: {away_data['defenders_out']} defenders out")
        
        return factors
    
    def predict(self, home_data, away_data):
        """Main prediction function."""
        self.reset()
        
        # Calculate expected goals
        home_lambda, away_lambda = self.calculate_expected_goals(home_data, away_data)
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        
        # Calculate probabilities
        probabilities, scoreline_probs, most_likely = self.calculate_probabilities(home_lambda, away_lambda)
        self.probabilities = probabilities
        self.scoreline_probs = scoreline_probs
        self.most_likely_score = most_likely
        
        # Calculate confidence
        self.confidence = self.calculate_confidence(home_lambda, away_lambda, home_data, away_data)
        
        # Generate key factors
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
        raise ValueError(f"League {league_name} not found in available datasets")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Validate required columns
        required_cols = [
            'overall_position', 'team', 'venue', 'matches_played', 'xg_for', 'goals',
            'home_xga', 'away_xga', 'goals_conceded', 'home_xgdiff_def', 'away_xgdiff_def',
            'defenders_out', 'form_last_5', 'motivation', 'open_play_pct', 'set_piece_pct',
            'counter_attack_pct', 'form', 'shots_allowed_pg', 'home_ppg_diff',
            'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.warning(f"Missing columns in data: {', '.join(missing_cols)}")
            st.warning("Some predictions may be less accurate")
        
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load data from GitHub: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
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

def display_prediction_box(title, value, subtitle=""):
    """Display prediction in styled box."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(69,183,209,0.9), rgba(78,205,196,0.9));
                border-radius: 15px; padding: 20px; margin: 15px 0; color: white;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 1.2em; text-align: center; opacity: 0.9;">{title}</div>
        <div style="font-size: 2.5em; font-weight: 800; margin: 10px 0; text-align: center;">{value}</div>
        <div style="font-size: 1.2em; text-align: center; opacity: 0.9;">{subtitle}</div>
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
    # Header
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Advanced Football Prediction Engine</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Complete Logic • Position-Based • Professional</p>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'league_data' not in st.session_state:
        st.session_state.league_data = None
    if 'prediction_result' not in st.session_state:
        st.session_state.prediction_result = None
    
    # Sidebar
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
                    st.success(f"✅ Successfully loaded {len(df)} records")
                    
                    # Show data preview
                    with st.expander("Data Preview"):
                        st.dataframe(df.head(), use_container_width=True)
                else:
                    st.error("Failed to load data")
        
        if selected_league in LEAGUE_PARAMS:
            st.markdown("---")
            st.markdown("### 📈 League Parameters")
            params = LEAGUE_PARAMS[selected_league]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Goals Conceded", f"{params['league_avg_goals_conceded']:.2f}")
            with col2:
                st.metric("Avg Shots Allowed", f"{params['league_avg_shots_allowed']:.2f}")
    
    # Main content
    if st.session_state.league_data is None:
        st.info("👈 Please load league data from the sidebar to begin.")
        return
    
    df = st.session_state.league_data
    selected_league = st.session_state.selected_league
    league_params = LEAGUE_PARAMS[selected_league]
    
    # Match setup
    st.markdown("## 🏟️ Match Setup")
    
    # Get available teams
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
    
    # Market odds
    market_odds = display_market_odds_interface()
    
    # Run prediction
    if st.button("🚀 Run Advanced Prediction", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams for home and away.")
            return
        
        try:
            # Prepare team data
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            # Create engine and predict
            engine = FootballPredictionEngine(league_params)
            
            with st.spinner("Running complete analysis..."):
                result = engine.predict(home_data, away_data)
                
                if result['success']:
                    st.session_state.prediction_result = result
                    st.session_state.prediction_engine = engine
                    st.success("✅ Analysis complete!")
                else:
                    st.error("Prediction failed")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Display results if available
    if st.session_state.prediction_result:
        result = st.session_state.prediction_result
        
        st.markdown("---")
        st.markdown("# 📊 Prediction Results")
        
        # Expected goals
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
        
        # Match probabilities
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
        
        # Predicted scoreline
        score_prob = result['scorelines']['top_10'].get(result['scorelines']['most_likely'], 0) * 100
        display_prediction_box(
            "🎯 Most Likely Score",
            result['scorelines']['most_likely'],
            f"Probability: {score_prob:.1f}%"
        )
        
        # Additional markets
        col1, col2 = st.columns(2)
        with col1:
            display_prediction_box(
                "Over 2.5 Goals",
                f"{result['probabilities']['over_25']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['over_25']:.2f}"
            )
        with col2:
            display_prediction_box(
                "Both Teams to Score",
                f"{result['probabilities']['btts_yes']*100:.1f}%",
                f"Fair odds: {1/result['probabilities']['btts_yes']:.2f}"
            )
        
        # Confidence
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
        
        # Key factors
        if result['key_factors']:
            st.markdown("### 🔑 Key Factors")
            for factor in result['key_factors']:
                st.markdown(f'<span style="display: inline-block; padding: 8px 16px; margin: 5px; '
                          f'border-radius: 20px; background: rgba(255,107,107,0.15); '
                          f'border: 1px solid #FF6B6B; color: #FF6B6B;">{factor}</span>', 
                          unsafe_allow_html=True)
        
        # Scoreline distribution
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
        
        # Raw data for debugging
        with st.expander("📋 View Raw Prediction Data"):
            st.json(result)

if __name__ == "__main__":
    main()
