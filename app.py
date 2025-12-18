import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Universal Football Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-top: 1.5rem;
    }
    .match-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .prediction-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        margin: 5px;
    }
    .high-confidence { background-color: #10B981; color: white; }
    .medium-confidence { background-color: #F59E0B; color: white; }
    .low-confidence { background-color: #EF4444; color: white; }
    .value-bet { 
        background-color: #8B5CF6; 
        color: white;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# League configurations
LEAGUE_CONFIGS = {
    'Premier League': {
        'name': 'Premier League',
        'size': 20,
        'home_advantage': 2.5,
        'market_efficiency': 0.90,
        'draw_frequency': 0.25,
        'avg_goals': 2.85,
        'style': 'high'
    },
    'La Liga': {
        'name': 'La Liga',
        'size': 20,
        'home_advantage': 2.0,
        'market_efficiency': 0.85,
        'draw_frequency': 0.28,
        'avg_goals': 2.50,
        'style': 'technical'
    },
    'Serie A': {
        'name': 'Serie A',
        'size': 20,
        'home_advantage': 2.2,
        'market_efficiency': 0.80,
        'draw_frequency': 0.30,
        'avg_goals': 2.65,
        'style': 'tactical'
    },
    'Bundesliga': {
        'name': 'Bundesliga',
        'size': 18,
        'home_advantage': 3.0,
        'market_efficiency': 0.88,
        'draw_frequency': 0.22,
        'avg_goals': 3.10,
        'style': 'attacking'
    },
    'Ligue 1': {
        'name': 'Ligue 1',
        'size': 18,
        'home_advantage': 2.3,
        'market_efficiency': 0.82,
        'draw_frequency': 0.26,
        'avg_goals': 2.70,
        'style': 'mixed'
    }
}

# Manager style matchups
STYLE_MATCHUPS = {
    'Possession-based & control': {
        'weak_against': ['High press & transition', 'Counter-attack'],
        'strong_against': ['Pragmatic/Defensive'],
        'base_rating': 8
    },
    'High press & transition': {
        'weak_against': ['Pragmatic/Defensive', 'Counter-attack'],
        'strong_against': ['Possession-based & control'],
        'base_rating': 7
    },
    'Pragmatic/Defensive': {
        'weak_against': ['Possession-based & control'],
        'strong_against': ['High press & transition'],
        'base_rating': 6
    },
    'Balanced/Adaptive': {
        'weak_against': [],
        'strong_against': [],
        'base_rating': 7
    },
    'Progressive/Developing': {
        'weak_against': ['Pragmatic/Defensive', 'High press & transition'],
        'strong_against': ['Progressive/Developing'],
        'base_rating': 6
    },
    'Counter-attack': {
        'weak_against': ['Pragmatic/Defensive'],
        'strong_against': ['Possession-based & control', 'High press & transition'],
        'base_rating': 7
    }
}

class UniversalFootballPredictor:
    def __init__(self):
        self.league_configs = LEAGUE_CONFIGS
        self.style_matchups = STYLE_MATCHUPS
        
    def calculate_form_score(self, form_string, is_home=True, quality_adjust=False, opponents=None):
        """Calculate form score from WWDL string"""
        form_points = {
            'W': 3,
            'D': 1,
            'L': 0
        }
        
        total_points = 0
        for i, result in enumerate(form_string[-5:]):  # Last 5 games
            if result in form_points:
                points = form_points[result]
                
                # Recency weighting (more recent = more weight)
                recency_weight = 1.0 + (i * 0.1)  # 1.0, 1.1, 1.2, 1.3, 1.4
                weighted_points = points * recency_weight
                
                # Location adjustment
                if is_home and result == 'W':
                    weighted_points *= 1.0  # Home wins standard
                elif not is_home and result == 'W':
                    weighted_points *= 1.1  # Away wins weighted more
                elif is_home and result == 'L':
                    weighted_points *= 0.9  # Home losses penalized more
                
                total_points += weighted_points
        
        # Normalize to max possible (5 games * 3 points * max weight)
        max_possible = sum([3 * (1.0 + i * 0.1) for i in range(5)])
        normalized_score = total_points / max_possible if max_possible > 0 else 0
        
        return normalized_score
    
    def calculate_market_score(self, home_odds, away_odds, draw_odds=None):
        """Calculate market implied probabilities"""
        home_implied = 1 / home_odds
        away_implied = 1 / away_odds
        
        # Adjust for overround (bookmaker margin)
        total_implied = home_implied + away_implied
        if draw_odds:
            total_implied += 1 / draw_odds
        
        # True probabilities (normalized)
        home_prob = home_implied / total_implied
        away_prob = away_implied / total_implied
        
        return home_prob, away_prob
    
    def calculate_quality_score(self, position, league_size):
        """Calculate quality score from table position"""
        if pd.isna(position) or position == 0:
            return 0.5  # Neutral if no position data
        
        # Normalize position (1st = highest, last = lowest)
        normalized = (league_size - position) / league_size
        return normalized
    
    def calculate_manager_score(self, manager_style, opponent_style, manager_rating=None):
        """Calculate managerial advantage score"""
        if pd.isna(manager_style) or manager_style not in self.style_matchups:
            return 0.5  # Neutral if no style data
        
        base_score = 0.5
        style_info = self.style_matchups.get(manager_style, {})
        
        # Check if style has advantage/disadvantage
        if opponent_style in style_info.get('weak_against', []):
            base_score -= 0.15
        elif opponent_style in style_info.get('strong_against', []):
            base_score += 0.15
        
        # Apply manager rating if available
        if manager_rating and not pd.isna(manager_rating):
            rating_adj = (manager_rating - 5) / 10  # Scale from -0.5 to +0.5
            base_score += rating_adj * 0.3  # Reduce impact of rating
        
        return max(0.1, min(0.9, base_score))  # Clamp between 0.1 and 0.9
    
    def calculate_home_advantage(self, league_name, is_derby=False, stadium_factor=1.0):
        """Calculate home advantage points"""
        league_config = self.league_configs.get(league_name, self.league_configs['Premier League'])
        base_advantage = league_config['home_advantage']
        
        adjustments = 0
        if is_derby:
            adjustments += 0.5
        
        # Stadium factor (big stadium = more advantage)
        adjustments += (stadium_factor - 1) * 0.3
        
        return base_advantage + adjustments
    
    def dynamic_weight_adjustment(self, match_context, league_name):
        """Dynamically adjust weights based on match context"""
        base_weights = {
            'form': 0.60,
            'market': 0.25,
            'quality': 0.10,
            'manager': 0.05
        }
        
        # Get league efficiency
        league_config = self.league_configs.get(league_name, self.league_configs['Premier League'])
        market_efficiency = league_config['market_efficiency']
        
        # Adjust market weight based on efficiency
        market_adjust = (market_efficiency - 0.85) * 0.2  # ±0.03
        base_weights['market'] += market_adjust
        base_weights['form'] -= market_adjust * 0.5
        base_weights['quality'] -= market_adjust * 0.5
        
        # Context adjustments
        if match_context.get('early_season', False):
            base_weights['form'] -= 0.10
            base_weights['quality'] += 0.10
        
        if match_context.get('late_season', False):
            base_weights['form'] += 0.05
            base_weights['quality'] += 0.05
        
        if match_context.get('derby', False):
            base_weights['market'] -= 0.05
            base_weights['form'] += 0.05
        
        # Normalize weights
        total = sum(base_weights.values())
        normalized = {k: v/total for k, v in base_weights.items()}
        
        return normalized
    
    def predict_match(self, home_data, away_data, league_name, match_context=None):
        """Main prediction function for a single match"""
        if match_context is None:
            match_context = {}
        
        league_config = self.league_configs.get(league_name, self.league_configs['Premier League'])
        league_size = league_config['size']
        
        # Get dynamic weights
        weights = self.dynamic_weight_adjustment(match_context, league_name)
        
        # 1. Calculate form scores
        home_form_raw = self.calculate_form_score(
            home_data.get('form', ''),
            is_home=True
        )
        away_form_raw = self.calculate_form_score(
            away_data.get('form', ''),
            is_home=False
        )
        
        home_form_score = home_form_raw * 100 * weights['form']
        away_form_score = away_form_raw * 100 * weights['form']
        
        # 2. Calculate market scores
        home_odds = float(home_data.get('home_odds', 2.0))
        away_odds = float(away_data.get('away_odds', 2.0))
        
        home_market_prob, away_market_prob = self.calculate_market_score(home_odds, away_odds)
        home_market_score = home_market_prob * 100 * weights['market']
        away_market_score = away_market_prob * 100 * weights['market']
        
        # 3. Calculate quality scores
        home_position = home_data.get('home_position', league_size/2)
        away_position = away_data.get('away_position', league_size/2)
        
        home_quality_score = self.calculate_quality_score(home_position, league_size) * 100 * weights['quality']
        away_quality_score = self.calculate_quality_score(away_position, league_size) * 100 * weights['quality']
        
        # 4. Calculate manager scores
        home_manager_style = home_data.get('home_manager_style', 'Balanced/Adaptive')
        away_manager_style = away_data.get('away_manager_style', 'Balanced/Adaptive')
        
        home_manager_score = self.calculate_manager_score(
            home_manager_style, 
            away_manager_style,
            home_data.get('home_manager_rating', 7)
        ) * 100 * weights['manager']
        
        away_manager_score = self.calculate_manager_score(
            away_manager_style,
            home_manager_style,
            away_data.get('away_manager_rating', 7)
        ) * 100 * weights['manager']
        
        # 5. Home advantage
        is_derby = match_context.get('derby', False)
        home_advantage = self.calculate_home_advantage(league_name, is_derby)
        
        # Total scores
        home_total = (
            home_form_score + 
            home_market_score + 
            home_quality_score + 
            home_manager_score + 
            home_advantage
        )
        
        away_total = (
            away_form_score + 
            away_market_score + 
            away_quality_score + 
            away_manager_score
        )
        
        # Convert to probabilities
        total_points = home_total + away_total
        
        # Base win probabilities (adjusted for home advantage)
        home_win_prob = (home_total / total_points) * (1 - league_config['draw_frequency'])
        away_win_prob = (away_total / total_points) * (1 - league_config['draw_frequency'])
        draw_prob = league_config['draw_frequency']
        
        # Adjust draw probability based on team styles
        if (home_manager_style == 'Pragmatic/Defensive' or 
            away_manager_style == 'Pragmatic/Defensive'):
            draw_prob *= 1.2  # Increase draw likelihood
        
        # Re-normalize
        total_probs = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_probs
        away_win_prob /= total_probs
        draw_prob /= total_probs
        
        # Calculate expected value for bets
        home_ev = (home_win_prob * home_odds) - 1
        away_ev = (away_win_prob * away_odds) - 1
        draw_ev = (draw_prob * 3.4) - 1  # Assuming avg draw odds of 3.4
        
        # Determine favorite
        favorite = 'home' if home_total > away_total else 'away'
        confidence = abs(home_total - away_total) / total_points * 100
        
        # Value bet detection
        value_bets = []
        if home_ev > 0.05:  # Positive expected value > 5%
            value_bets.append({'market': 'home_win', 'odds': home_odds, 'ev': home_ev})
        if away_ev > 0.05:
            value_bets.append({'market': 'away_win', 'odds': away_odds, 'ev': away_ev})
        if draw_ev > 0.05:
            value_bets.append({'market': 'draw', 'odds': 3.4, 'ev': draw_ev})
        
        # Calculate expected goals
        avg_goals = league_config['avg_goals']
        home_attack = home_data.get('home_attack_rating', 5) / 10
        away_defense = away_data.get('away_defense_rating', 5) / 10
        away_attack = away_data.get('away_attack_rating', 5) / 10
        home_defense = home_data.get('home_defense_rating', 5) / 10
        
        home_xg = avg_goals * home_attack * (1 - away_defense/2)
        away_xg = avg_goals * away_attack * (1 - home_defense/2)
        total_xg = home_xg + away_xg
        
        # BTTS probability
        btts_prob = (1 - np.exp(-home_xg)) * (1 - np.exp(-away_xg))
        
        # Over/under probabilities using Poisson distribution
        poisson_home = stats.poisson(home_xg)
        poisson_away = stats.poisson(away_xg)
        
        # Calculate probability of over 2.5 goals
        over_25_prob = 0
        for i in range(0, 4):  # 0-3 goals for home
            for j in range(0, 4):  # 0-3 goals for away
                if i + j > 2.5:
                    prob = poisson_home.pmf(i) * poisson_away.pmf(j)
                    over_25_prob += prob
        # Add complement for higher scores
        over_25_prob += 1 - (poisson_home.cdf(3) * poisson_away.cdf(3))
        
        return {
            'home_team': home_data.get('home_team', 'Home'),
            'away_team': home_data.get('away_team', 'Away'),
            'home_win_prob': round(home_win_prob * 100, 1),
            'away_win_prob': round(away_win_prob * 100, 1),
            'draw_prob': round(draw_prob * 100, 1),
            'favorite': favorite,
            'confidence': round(confidence, 1),
            'home_total_score': round(home_total, 1),
            'away_total_score': round(away_total, 1),
            'value_bets': value_bets,
            'expected_goals': {
                'home_xg': round(home_xg, 2),
                'away_xg': round(away_xg, 2),
                'total_xg': round(total_xg, 2)
            },
            'btts_prob': round(btts_prob * 100, 1),
            'over_25_prob': round(over_25_prob * 100, 1),
            'component_scores': {
                'form': {
                    'home': round(home_form_score, 1),
                    'away': round(away_form_score, 1)
                },
                'market': {
                    'home': round(home_market_score, 1),
                    'away': round(away_market_score, 1)
                },
                'quality': {
                    'home': round(home_quality_score, 1),
                    'away': round(away_quality_score, 1)
                },
                'manager': {
                    'home': round(home_manager_score, 1),
                    'away': round(away_manager_score, 1)
                }
            },
            'weights': weights
        }

def load_and_preprocess_data(uploaded_file):
    """Load and preprocess uploaded CSV data"""
    df = pd.read_csv(uploaded_file)
    
    # Convert numeric columns
    numeric_columns = ['home_position', 'away_position', 'home_odds', 'away_odds',
                      'home_attack_rating', 'away_attack_rating',
                      'home_defense_rating', 'away_defense_rating',
                      'home_press_rating', 'away_press_rating',
                      'home_possession_rating', 'away_possession_rating',
                      'home_pragmatic_rating', 'away_pragmatic_rating']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure required columns exist
    required_columns = ['home_team', 'away_team', 'league', 'date']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return None
    
    return df

def create_radar_chart(prediction):
    """Create radar chart for component scores"""
    categories = ['Form', 'Market', 'Quality', 'Manager']
    
    home_scores = [
        prediction['component_scores']['form']['home'],
        prediction['component_scores']['market']['home'],
        prediction['component_scores']['quality']['home'],
        prediction['component_scores']['manager']['home']
    ]
    
    away_scores = [
        prediction['component_scores']['form']['away'],
        prediction['component_scores']['market']['away'],
        prediction['component_scores']['quality']['away'],
        prediction['component_scores']['manager']['away']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=home_scores + [home_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=prediction['home_team'],
        line_color='#3B82F6'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=away_scores + [away_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=prediction['away_team'],
        line_color='#EF4444'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Component Score Comparison"
    )
    
    return fig

def create_probability_gauge(prediction):
    """Create gauge chart for win probabilities"""
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=('Home Win', 'Draw', 'Away Win')
    )
    
    # Home win gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=prediction['home_win_prob'],
        title={'text': f"{prediction['home_team']}"},
        domain={'row': 0, 'column': 0},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ]
        }
    ), row=1, col=1)
    
    # Draw gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=prediction['draw_prob'],
        title={'text': "Draw"},
        domain={'row': 0, 'column': 1},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#10B981"},
            'steps': [
                {'range': [0, 20], 'color': "lightgray"},
                {'range': [20, 40], 'color': "gray"},
                {'range': [40, 100], 'color': "darkgray"}
            ]
        }
    ), row=1, col=2)
    
    # Away win gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=prediction['away_win_prob'],
        title={'text': f"{prediction['away_team']}"},
        domain={'row': 0, 'column': 2},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#EF4444"},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ]
        }
    ), row=1, col=3)
    
    fig.update_layout(height=300, margin=dict(l=50, r=50, t=50, b=50))
    
    return fig

def main():
    st.markdown('<div class="main-header">⚽ Universal Football Predictor</div>', unsafe_allow_html=True)
    
    # Initialize predictor
    predictor = UniversalFootballPredictor()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Configuration")
        
        uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
        
        if uploaded_file:
            df = load_and_preprocess_data(uploaded_file)
            
            if df is not None:
                # League selection
                leagues = df['league'].unique() if 'league' in df.columns else ['Unknown']
                selected_league = st.selectbox("Select League", leagues)
                
                # Match selection
                matches = df.apply(lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", axis=1)
                selected_match = st.selectbox("Select Match", matches)
                
                # Match context options
                st.subheader("Match Context")
                is_derby = st.checkbox("Derby Match", value=False)
                early_season = st.checkbox("Early Season (<10 games)", value=False)
                late_season = st.checkbox("Late Season (>30 games)", value=False)
                
                match_context = {
                    'derby': is_derby,
                    'early_season': early_season,
                    'late_season': late_season
                }
                
                # Analysis settings
                st.subheader("Analysis Settings")
                show_components = st.checkbox("Show Component Scores", value=True)
                show_value_bets = st.checkbox("Highlight Value Bets", value=True)
                
        else:
            st.info("Please upload a CSV file to get started")
            st.code("""Required columns:
- home_team, away_team
- league, date
- home_odds, away_odds
- home_position, away_position
- home_form, away_form
- home_manager_style, away_manager_style
- home_attack_rating, away_attack_rating
- home_defense_rating, away_defense_rating""")
    
    # Main content area
    if uploaded_file and df is not None:
        # Get selected match data
        match_idx = matches.tolist().index(selected_match)
        match_data = df.iloc[match_idx]
        
        # Prepare data for prediction
        home_data = {
            'home_team': match_data['home_team'],
            'home_position': match_data['home_position'],
            'home_odds': match_data['home_odds'],
            'form': match_data['home_form'],
            'home_manager_style': match_data.get('home_manager_style', 'Balanced/Adaptive'),
            'home_attack_rating': match_data.get('home_attack_rating', 5),
            'home_defense_rating': match_data.get('home_defense_rating', 5),
            'home_manager_rating': match_data.get('home_pragmatic_rating', 7)
        }
        
        away_data = {
            'away_team': match_data['away_team'],
            'away_position': match_data['away_position'],
            'away_odds': match_data['away_odds'],
            'form': match_data['away_form'],
            'away_manager_style': match_data.get('away_manager_style', 'Balanced/Adaptive'),
            'away_attack_rating': match_data.get('away_attack_rating', 5),
            'away_defense_rating': match_data.get('away_defense_rating', 5),
            'away_manager_rating': match_data.get('away_pragmatic_rating', 7)
        }
        
        # Make prediction
        prediction = predictor.predict_match(
            home_data, 
            away_data, 
            selected_league,
            match_context
        )
        
        # Display main prediction card
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="match-card">
                <h3>🏠 {prediction['home_team']}</h3>
                <p><strong>Position:</strong> {match_data['home_position']}</p>
                <p><strong>Form:</strong> {match_data['home_form']}</p>
                <p><strong>Manager Style:</strong> {home_data['home_manager_style']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2>VS</h2>
                <p style="font-size: 0.9rem; color: #666;">{match_data['date']}</p>
                <p style="font-size: 0.9rem; color: #666;">{selected_league}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="match-card">
                <h3>✈️ {prediction['away_team']}</h3>
                <p><strong>Position:</strong> {match_data['away_position']}</p>
                <p><strong>Form:</strong> {match_data['away_form']}</p>
                <p><strong>Manager Style:</strong> {away_data['away_manager_style']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Prediction results
        st.markdown('<div class="sub-header">📈 Prediction Results</div>', unsafe_allow_html=True)
        
        # Confidence badge
        confidence = prediction['confidence']
        if confidence >= 70:
            confidence_class = "high-confidence"
            confidence_text = "High Confidence"
        elif confidence >= 40:
            confidence_class = "medium-confidence"
            confidence_text = "Medium Confidence"
        else:
            confidence_class = "low-confidence"
            confidence_text = "Low Confidence"
        
        favorite_text = f"{prediction['home_team'] if prediction['favorite'] == 'home' else prediction['away_team']}"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="metric-card"><h4>🏆 Favorite</h4><h3>{favorite_text}</h3></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="metric-card"><h4>📊 Confidence</h4><span class="prediction-badge {confidence_class}">{confidence_text} ({confidence}%)</span></div>', unsafe_allow_html=True)
        
        with col3:
            total_score_diff = abs(prediction['home_total_score'] - prediction['away_total_score'])
            st.markdown(f'<div class="metric-card"><h4>⚔️ Score Difference</h4><h3>{total_score_diff:.1f} pts</h3></div>', unsafe_allow_html=True)
        
        with col4:
            ev_count = len(prediction['value_bets'])
            st.markdown(f'<div class="metric-card"><h4>💰 Value Bets</h4><h3>{ev_count}</h3></div>', unsafe_allow_html=True)
        
        # Probability gauges
        st.plotly_chart(create_probability_gauge(prediction), use_container_width=True)
        
        # Value bets section
        if prediction['value_bets'] and show_value_bets:
            st.markdown('<div class="sub-header">💰 Value Bet Opportunities</div>', unsafe_allow_html=True)
            
            for bet in prediction['value_bets']:
                ev_percent = bet['ev'] * 100
                st.markdown(f"""
                <div class="match-card">
                    <span class="prediction-badge value-bet">VALUE BET</span>
                    <strong>{bet['market'].replace('_', ' ').title()}</strong> at odds {bet['odds']:.2f}<br>
                    Expected Value: <strong>{ev_percent:.1f}%</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Statistical predictions
        st.markdown('<div class="sub-header">📊 Statistical Predictions</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Expected Goals</h4>
                <p><strong>Home:</strong> {prediction['expected_goals']['home_xg']}</p>
                <p><strong>Away:</strong> {prediction['expected_goals']['away_xg']}</p>
                <p><strong>Total:</strong> {prediction['expected_goals']['total_xg']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Both Teams to Score</h4>
                <h2>{prediction['btts_prob']}%</h2>
                <p>Probability</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Over 2.5 Goals</h4>
                <h2>{prediction['over_25_prob']}%</h2>
                <p>Probability</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            home_odds = match_data['home_odds']
            away_odds = match_data['away_odds']
            st.markdown(f"""
            <div class="metric-card">
                <h4>Market Odds</h4>
                <p><strong>Home:</strong> {home_odds:.2f}</p>
                <p><strong>Away:</strong> {away_odds:.2f}</p>
                <p><strong>Implied:</strong> {(1/home_odds)*100:.1f}% / {(1/away_odds)*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Component analysis
        if show_components:
            st.markdown('<div class="sub-header">🔍 Component Analysis</div>', unsafe_allow_html=True)
            
            # Display weights
            weights = prediction['weights']
            weight_text = ", ".join([f"{k.title()}: {v*100:.0f}%" for k, v in weights.items()])
            st.info(f"**Dynamic Weights Applied:** {weight_text}")
            
            # Component scores table
            comp_data = prediction['component_scores']
            comp_df = pd.DataFrame({
                'Component': ['Form', 'Market', 'Quality', 'Manager'],
                prediction['home_team']: [
                    comp_data['form']['home'],
                    comp_data['market']['home'],
                    comp_data['quality']['home'],
                    comp_data['manager']['home']
                ],
                prediction['away_team']: [
                    comp_data['form']['away'],
                    comp_data['market']['away'],
                    comp_data['quality']['away'],
                    comp_data['manager']['away']
                ]
            })
            
            st.dataframe(comp_df, use_container_width=True, hide_index=True)
            
            # Radar chart
            st.plotly_chart(create_radar_chart(prediction), use_container_width=True)
        
        # Detailed analysis
        with st.expander("📋 Detailed Analysis Report"):
            st.markdown(f"""
            ### Match Analysis Summary
            
            **Favorite Designation:** {favorite_text} is predicted as the favorite with {confidence:.1f}% confidence.
            
            **Key Factors:**
            1. **Form Advantage:** {'Home team' if comp_data['form']['home'] > comp_data['form']['away'] else 'Away team'} has better recent form
            2. **Market View:** Odds suggest {favorite_text} is {'underpriced' if prediction['value_bets'] else 'fairly priced'}
            3. **Quality Differential:** {abs(match_data['home_position'] - match_data['away_position'])} positions difference in table
            4. **Managerial Battle:** {home_data['home_manager_style']} vs {away_data['away_manager_style']}
            
            **Recommended Approach:**
            - This is a **{confidence_text.lower()}** confidence prediction
            - {f"Consider value bets identified above" if prediction['value_bets'] else "No strong value bets identified"}
            - Expected to be a {'high' if prediction['over_25_prob'] > 60 else 'low' if prediction['over_25_prob'] < 40 else 'moderate'} scoring game
            """)
        
        # Batch processing option
        if st.button("📊 Analyze All Matches in File"):
            st.markdown('<div class="sub-header">📈 Batch Analysis Results</div>', unsafe_allow_html=True)
            
            all_predictions = []
            for idx, row in df.iterrows():
                home_data = {
                    'home_team': row['home_team'],
                    'home_position': row['home_position'],
                    'home_odds': row['home_odds'],
                    'form': row['home_form'],
                    'home_manager_style': row.get('home_manager_style', 'Balanced/Adaptive'),
                    'home_attack_rating': row.get('home_attack_rating', 5),
                    'home_defense_rating': row.get('home_defense_rating', 5),
                    'home_manager_rating': row.get('home_pragmatic_rating', 7)
                }
                
                away_data = {
                    'away_team': row['away_team'],
                    'away_position': row['away_position'],
                    'away_odds': row['away_odds'],
                    'form': row['away_form'],
                    'away_manager_style': row.get('away_manager_style', 'Balanced/Adaptive'),
                    'away_attack_rating': row.get('away_attack_rating', 5),
                    'away_defense_rating': row.get('away_defense_rating', 5),
                    'away_manager_rating': row.get('away_pragmatic_rating', 7)
                }
                
                pred = predictor.predict_match(home_data, away_data, row['league'], match_context)
                all_predictions.append(pred)
            
            # Create summary dataframe
            summary_df = pd.DataFrame([{
                'Match': f"{p['home_team']} vs {p['away_team']}",
                'Favorite': p['home_team'] if p['favorite'] == 'home' else p['away_team'],
                'Confidence': p['confidence'],
                'Home Win %': p['home_win_prob'],
                'Draw %': p['draw_prob'],
                'Away Win %': p['away_win_prob'],
                'Value Bets': len(p['value_bets'])
            } for p in all_predictions])
            
            st.dataframe(summary_df, use_container_width=True)
            
            # Download button for results
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Predictions as CSV",
                data=csv,
                file_name="football_predictions.csv",
                mime="text/csv"
            )
    
    else:
        # Show welcome/instructions
        st.markdown("""
        ## Welcome to the Universal Football Predictor
        
        This advanced prediction engine uses a sophisticated weighted framework to analyze football matches across any league.
        
        ### How it works:
        1. **Upload your CSV file** with match data (see sidebar for required columns)
        2. **Select a league and match** to analyze
        3. **Configure match context** (derby, season timing)
        4. **Get detailed predictions** including probabilities, value bets, and component analysis
        
        ### Key Features:
        - **Universal Framework**: Works for any league worldwide
        - **Dynamic Weighting**: Adjusts based on league efficiency and match context
        - **Value Bet Detection**: Identifies positive expected value opportunities
        - **Component Analysis**: Breaks down form, market, quality, and manager factors
        - **Statistical Modeling**: Uses Poisson distributions for goal expectations
        
        ### Sample CSV format:
        ```csv
        match_id,league,date,home_team,away_team,home_position,away_position,home_odds,away_odds,home_form,away_form,home_manager_style,away_manager_style,home_attack_rating,away_attack_rating,home_defense_rating,away_defense_rating
        EPL_001,Premier League,2025-12-20,Team A,Team B,5,12,1.80,4.20,WWDLW,LLDWL,Possession-based & control,High press & transition,8,6,7,5
        ```
        
        Upload a file in the sidebar to get started!
        """)
        
        # Show sample data
        with st.expander("📋 View Sample Data Structure"):
            sample_data = pd.DataFrame({
                'match_id': ['EPL_001', 'EPL_002'],
                'league': ['Premier League', 'Premier League'],
                'date': ['2025-12-20', '2025-12-21'],
                'home_team': ['Manchester City', 'Liverpool'],
                'away_team': ['Chelsea', 'Arsenal'],
                'home_position': [1, 3],
                'away_position': [4, 2],
                'home_odds': [1.80, 2.10],
                'away_odds': [4.20, 3.50],
                'home_form': ['WWWDW', 'WLDWW'],
                'away_form': ['LWWDL', 'WWWLD'],
                'home_manager_style': ['Possession-based & control', 'High press & transition'],
                'away_manager_style': ['High press & transition', 'Possession-based & control'],
                'home_attack_rating': [9, 8],
                'away_attack_rating': [8, 9],
                'home_defense_rating': [8, 7],
                'away_defense_rating': [7, 8]
            })
            st.dataframe(sample_data, use_container_width=True)

if __name__ == "__main__":
    main()
