import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Football Prediction Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
    }
    .prediction-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
    }
    .confidence-high {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    .confidence-medium {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    .confidence-low {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        border-radius: 15px;
        padding: 15px;
        color: white;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    }
    .team-box {
        border: 2px solid #4ECDC4;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: rgba(78, 205, 196, 0.1);
    }
    .factor-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.9em;
        background: rgba(255, 107, 107, 0.2);
        border: 1px solid #FF6B6B;
    }
    .input-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

# League averages (La Liga example)
LEAGUE_AVG_SHOTS_ALLOWED = 12.0
LEAGUE_AVG_SHOTS_ON_TARGET = 4.5
LEAGUE_AVG_EFFICIENCY = 0.375

class PredictionEngine:
    def __init__(self):
        self.reset_calculations()
    
    def reset_calculations(self):
        self.home_lambda = None
        self.away_lambda = None
        self.probabilities = {}
        self.confidence = 0
        self.expected_values = {}
        self.key_factors = {}
    
    def calculate_base_xg(self, home_xg, away_xg, home_shots_allowed, away_shots_allowed):
        """Step 1: Base Expected Goals"""
        home_lambda_base = home_xg * (away_shots_allowed / LEAGUE_AVG_SHOTS_ALLOWED) * 0.5
        away_lambda_base = away_xg * (home_shots_allowed / LEAGUE_AVG_SHOTS_ALLOWED) * 0.5
        return home_lambda_base, away_lambda_base
    
    def apply_home_advantage(self, home_lambda_base, away_lambda_base, home_ppg, away_ppg, league_avg_ppg):
        """Step 2: Home Advantage Adjustment"""
        home_ppg_diff = home_ppg - league_avg_ppg
        away_ppg_diff = away_ppg - league_avg_ppg
        
        home_boost = 1 + (home_ppg_diff * 0.3)
        away_penalty = 1 - (abs(away_ppg_diff) * 0.25)
        
        home_lambda = home_lambda_base * home_boost
        away_lambda = away_lambda_base * away_penalty
        
        return home_lambda, away_lambda, home_ppg_diff, away_ppg_diff
    
    def apply_injury_adjustment(self, home_lambda, away_lambda, home_injury_level, away_injury_level):
        """Step 3: Injury Adjustment"""
        home_defense_strength = 1 - (home_injury_level / 20)
        away_defense_strength = 1 - (away_injury_level / 20)
        
        home_lambda = home_lambda * away_defense_strength  # Attack vs weakened defense
        away_lambda = away_lambda * home_defense_strength  # Attack vs weakened defense
        
        return home_lambda, away_lambda, home_defense_strength, away_defense_strength
    
    def apply_form_adjustment(self, home_lambda, away_lambda, home_form_last_5, away_form_last_5):
        """Step 4: Form Adjustment"""
        home_form_factor = 1 + ((home_form_last_5 - 9) * 0.02)
        away_form_factor = 1 + ((away_form_last_5 - 9) * 0.02)
        
        home_lambda = home_lambda * home_form_factor
        away_lambda = away_lambda * away_form_factor
        
        return home_lambda, away_lambda, home_form_factor, away_form_factor
    
    def apply_motivation_adjustment(self, home_lambda, away_lambda, home_motivation, away_motivation):
        """Step 5: Motivation Adjustment"""
        home_motivation_factor = 1 + (home_motivation * 0.03)
        away_motivation_factor = 1 + (away_motivation * 0.03)
        
        home_lambda = home_lambda * home_motivation_factor
        away_lambda = away_lambda * away_motivation_factor
        
        return home_lambda, away_lambda, home_motivation_factor, away_motivation_factor
    
    def apply_efficiency_adjustment(self, home_lambda, away_lambda, 
                                   home_shots_on_target, away_shots_on_target,
                                   home_shots_allowed, away_shots_allowed):
        """Step 6: Efficiency Adjustment"""
        home_efficiency = home_shots_on_target / away_shots_allowed if away_shots_allowed > 0 else 0
        away_efficiency = away_shots_on_target / home_shots_allowed if home_shots_allowed > 0 else 0
        
        home_lambda = home_lambda * (1 + (home_efficiency - LEAGUE_AVG_EFFICIENCY))
        away_lambda = away_lambda * (1 + (away_efficiency - LEAGUE_AVG_EFFICIENCY))
        
        return home_lambda, away_lambda, home_efficiency, away_efficiency
    
    def calculate_probabilities(self, home_lambda, away_lambda, iterations=10000):
        """Steps 7-9: Final Lambdas and Poisson Simulation"""
        # Run Poisson simulations
        home_goals = np.random.poisson(home_lambda, iterations)
        away_goals = np.random.poisson(away_lambda, iterations)
        
        # Calculate probabilities
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        over_2_5 = np.sum(home_goals + away_goals > 2.5)
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
        
        probabilities = {
            'home_win': home_wins / iterations,
            'draw': draws / iterations,
            'away_win': away_wins / iterations,
            'over_2.5': over_2_5 / iterations,
            'btts_yes': btts_yes / iterations
        }
        
        return probabilities, home_goals, away_goals
    
    def calculate_confidence(self, home_lambda, away_lambda, home_injury_level, away_injury_level,
                           home_ppg_diff, form_diff):
        """Step 10: Confidence Scoring"""
        base_confidence = 1 - (abs(home_lambda - away_lambda) / (home_lambda + away_lambda))
        
        # Additional confidence factors
        injury_diff = abs(home_injury_level - away_injury_level)
        home_advantage = abs(home_ppg_diff)
        
        confidence_boost = 0
        if abs(home_lambda - away_lambda) > 1.0:
            confidence_boost += 0.15
        if injury_diff > 4:
            confidence_boost += 0.15
        if home_advantage > 0.5:
            confidence_boost += 0.1
        if form_diff > 4:
            confidence_boost += 0.1
            
        confidence = min(0.95, base_confidence + confidence_boost)
        
        return confidence, base_confidence, confidence_boost
    
    def calculate_expected_value(self, probabilities, market_odds):
        """Step 11: Expected Value Calculation"""
        fair_odds = {
            'home_win': 1 / probabilities['home_win'],
            'over_2.5': 1 / probabilities['over_2.5'],
            'btts_yes': 1 / probabilities['btts_yes']
        }
        
        expected_values = {}
        for key in fair_odds:
            if key in market_odds and market_odds[key] > 0:
                ev = (market_odds[key] / fair_odds[key]) - 1
                expected_values[key] = ev
            else:
                expected_values[key] = 0
                
        return expected_values, fair_odds
    
    def run_full_prediction(self, inputs):
        """Run complete prediction pipeline"""
        self.reset_calculations()
        
        # Step 1: Base Expected Goals
        home_lambda, away_lambda = self.calculate_base_xg(
            inputs['home_xg'], inputs['away_xg'],
            inputs['home_shots_allowed'], inputs['away_shots_allowed']
        )
        
        # Step 2: Home Advantage
        home_lambda, away_lambda, home_ppg_diff, away_ppg_diff = self.apply_home_advantage(
            home_lambda, away_lambda,
            inputs['home_ppg'], inputs['away_ppg'],
            inputs['league_avg_ppg']
        )
        
        # Step 3: Injury Adjustment
        home_lambda, away_lambda, home_defense_str, away_defense_str = self.apply_injury_adjustment(
            home_lambda, away_lambda,
            inputs['home_injury_level'], inputs['away_injury_level']
        )
        
        # Step 4: Form Adjustment
        home_lambda, away_lambda, home_form_factor, away_form_factor = self.apply_form_adjustment(
            home_lambda, away_lambda,
            inputs['home_form_last_5'], inputs['away_form_last_5']
        )
        
        # Step 5: Motivation Adjustment
        home_lambda, away_lambda, home_motivation_factor, away_motivation_factor = self.apply_motivation_adjustment(
            home_lambda, away_lambda,
            inputs['home_motivation'], inputs['away_motivation']
        )
        
        # Step 6: Efficiency Adjustment
        home_lambda, away_lambda, home_efficiency, away_efficiency = self.apply_efficiency_adjustment(
            home_lambda, away_lambda,
            inputs['home_shots_on_target'], inputs['away_shots_on_target'],
            inputs['home_shots_allowed'], inputs['away_shots_allowed']
        )
        
        # Steps 7-9: Final calculations and probabilities
        probabilities, home_goals_sim, away_goals_sim = self.calculate_probabilities(home_lambda, away_lambda)
        
        # Step 10: Confidence
        form_diff = inputs['home_form_last_5'] - inputs['away_form_last_5']
        confidence, base_conf, conf_boost = self.calculate_confidence(
            home_lambda, away_lambda,
            inputs['home_injury_level'], inputs['away_injury_level'],
            home_ppg_diff, form_diff
        )
        
        # Step 11: Expected Value
        expected_values, fair_odds = self.calculate_expected_value(
            probabilities, inputs['market_odds']
        )
        
        # Store results
        self.home_lambda = home_lambda
        self.away_lambda = away_lambda
        self.probabilities = probabilities
        self.confidence = confidence
        self.expected_values = expected_values
        self.fair_odds = fair_odds
        
        # Key factors
        self.key_factors = {
            'home_advantage': home_ppg_diff,
            'injury_mismatch': inputs['home_injury_level'] - inputs['away_injury_level'],
            'form_difference': form_diff,
            'lambda_difference': abs(home_lambda - away_lambda),
            'defense_strength_home': home_defense_str,
            'defense_strength_away': away_defense_str
        }
        
        return {
            'home_lambda': home_lambda,
            'away_lambda': away_lambda,
            'probabilities': probabilities,
            'confidence': confidence,
            'expected_values': expected_values,
            'fair_odds': fair_odds,
            'key_factors': self.key_factors,
            'simulated_goals': (home_goals_sim, away_goals_sim)
        }

def create_input_interface():
    """Create the input interface with team information"""
    st.sidebar.markdown("## ⚙️ Match Configuration")
    
    # Pre-filled data based on corrected input
    default_home_name = "Home Team"
    default_away_name = "Away Team"
    
    # Home Team Section
    st.sidebar.markdown("### 🏠 Home Team")
    home_name = st.sidebar.text_input("Home Team Name", default_home_name, key="home_name")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        home_xg = st.number_input("xG (per game)", min_value=0.0, max_value=5.0, value=1.43, step=0.01, key="home_xg")
        home_shots_allowed = st.number_input("Shots Allowed", min_value=0.0, max_value=30.0, value=7.3, step=0.1, key="home_shots_allowed")
        home_shots_on_target = st.number_input("Shots on Target", min_value=0.0, max_value=20.0, value=4.2, step=0.1, key="home_shots_on_target")
    with col2:
        home_ppg = st.number_input("PPG", min_value=0.0, max_value=3.0, value=1.78, step=0.01, key="home_ppg")
        home_form_last_5 = st.slider("Form Last 5", min_value=0, max_value=15, value=9, key="home_form", help="Points from last 5 matches")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        home_injury_level = st.slider("Injury Level", min_value=0, max_value=10, value=8, key="home_injury", help="0 = No injuries, 10 = Critical")
    with col2:
        home_motivation = st.slider("Motivation", min_value=1, max_value=10, value=2, key="home_motivation", help="1 = Low, 10 = High")
    
    st.sidebar.markdown("---")
    
    # Away Team Section
    st.sidebar.markdown("### 🏃 Away Team")
    away_name = st.sidebar.text_input("Away Team Name", default_away_name, key="away_name")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        away_xg = st.number_input("xG (per game)", min_value=0.0, max_value=5.0, value=0.94, step=0.01, key="away_xg")
        away_shots_allowed = st.number_input("Shots Allowed", min_value=0.0, max_value=30.0, value=12.9, step=0.1, key="away_shots_allowed")
        away_shots_on_target = st.number_input("Shots on Target", min_value=0.0, max_value=20.0, value=4.9, step=0.1, key="away_shots_on_target")
    with col2:
        away_ppg = st.number_input("PPG", min_value=0.0, max_value=3.0, value=1.57, step=0.01, key="away_ppg")
        away_form_last_5 = st.slider("Form Last 5", min_value=0, max_value=15, value=10, key="away_form", help="Points from last 5 matches")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        away_injury_level = st.slider("Injury Level", min_value=0, max_value=10, value=2, key="away_injury", help="0 = No injuries, 10 = Critical")
    with col2:
        away_motivation = st.slider("Motivation", min_value=1, max_value=10, value=4, key="away_motivation", help="1 = Low, 10 = High")
    
    st.sidebar.markdown("---")
    
    # League & Market Section
    st.sidebar.markdown("### 📊 League & Market")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        league_avg_ppg = st.number_input("League Avg PPG", min_value=0.5, max_value=2.5, value=1.5, step=0.01, key="league_ppg")
    with col2:
        st.markdown("###")
        st.info(f"Shots Allowed Avg: {LEAGUE_AVG_SHOTS_ALLOWED}")
    
    st.sidebar.markdown("### 💰 Market Odds")
    
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        home_odds = st.number_input("Home Win", min_value=1.1, max_value=20.0, value=1.79, step=0.01, key="home_odds")
        st.caption("Market: 1.79")
    with col2:
        over_odds = st.number_input("Over 2.5", min_value=1.1, max_value=20.0, value=2.30, step=0.01, key="over_odds")
        st.caption("Market: 2.30")
    with col3:
        btts_odds = st.number_input("BTTS Yes", min_value=1.1, max_value=20.0, value=2.10, step=0.01, key="btts_odds")
        st.caption("Market: ~2.10")
    
    market_odds = {
        'home_win': home_odds,
        'over_2.5': over_odds,
        'btts_yes': btts_odds
    }
    
    inputs = {
        'home_name': home_name,
        'away_name': away_name,
        'home_xg': home_xg,
        'away_xg': away_xg,
        'home_shots_allowed': home_shots_allowed,
        'away_shots_allowed': away_shots_allowed,
        'home_shots_on_target': home_shots_on_target,
        'away_shots_on_target': away_shots_on_target,
        'home_ppg': home_ppg,
        'away_ppg': away_ppg,
        'home_form_last_5': home_form_last_5,
        'away_form_last_5': away_form_last_5,
        'home_injury_level': home_injury_level,
        'away_injury_level': away_injury_level,
        'home_motivation': home_motivation,
        'away_motivation': away_motivation,
        'league_avg_ppg': league_avg_ppg,
        'market_odds': market_odds
    }
    
    return inputs

def display_team_comparison(home_name, away_name, inputs):
    """Display team comparison metrics"""
    st.markdown("## 📊 Team Comparison")
    
    metrics = [
        ("xG", inputs['home_xg'], inputs['away_xg'], "Expected Goals per game"),
        ("PPG", inputs['home_ppg'], inputs['away_ppg'], "Points Per Game"),
        ("Form", inputs['home_form_last_5'], inputs['away_form_last_5'], "Last 5 Games"),
        ("Injuries", inputs['home_injury_level'], inputs['away_injury_level'], "Injury Level (0-10)"),
        ("Motivation", inputs['home_motivation'], inputs['away_motivation'], "Motivation Level (1-10)"),
        ("Shots Allowed", inputs['home_shots_allowed'], inputs['away_shots_allowed'], "Avg shots allowed per game")
    ]
    
    cols = st.columns(len(metrics))
    
    for idx, (label, home_val, away_val, desc) in enumerate(metrics):
        with cols[idx]:
            st.markdown(f"**{label}**")
            st.markdown(f"<div class='team-box'><small>{desc}</small><br><b>{home_name}:</b> {home_val:.2f}<br><b>{away_name}:</b> {away_val:.2f}</div>", 
                       unsafe_allow_html=True)

def display_probability_charts(probabilities, home_name, away_name):
    """Display probability charts"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Match outcome probabilities
        fig = go.Figure(data=[
            go.Bar(
                x=['Home Win', 'Draw', 'Away Win'],
                y=[probabilities['home_win'], probabilities['draw'], probabilities['away_win']],
                marker_color=['#4ECDC4', '#FFD166', '#FF6B6B'],
                text=[f"{p*100:.1f}%" for p in [probabilities['home_win'], probabilities['draw'], probabilities['away_win']]],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Match Outcome Probabilities",
            yaxis_title="Probability",
            yaxis=dict(range=[0, 1]),
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart for additional markets
        fig2 = go.Figure(data=[
            go.Pie(
                labels=['Over 2.5', 'Under 2.5'],
                values=[probabilities['over_2.5'], 1-probabilities['over_2.5']],
                marker_colors=['#06D6A0', '#EF476F'],
                hole=0.4
            )
        ])
        
        fig2.update_layout(
            title="Over/Under 2.5",
            height=300,
            showlegend=True
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # BTTS probabilities
        btts_data = {
            'BTTS Yes': probabilities['btts_yes'],
            'BTTS No': 1 - probabilities['btts_yes']
        }
        
        st.markdown(f"""
        <div class='prediction-card'>
            <h4>🏆 Both Teams to Score</h4>
            <h3>Yes: {probabilities['btts_yes']*100:.1f}%</h3>
            <small>Probability that both teams score</small>
        </div>
        """, unsafe_allow_html=True)

def display_expected_values(expected_values, fair_odds, market_odds, probabilities, confidence):
    """Display expected value analysis"""
    st.markdown("## 💰 Expected Value Analysis")
    
    cols = st.columns(3)
    
    ev_data = [
        ("Home Win", expected_values.get('home_win', 0), 
         fair_odds.get('home_win', 0), market_odds.get('home_win', 0),
         probabilities['home_win']),
        ("Over 2.5", expected_values.get('over_2.5', 0),
         fair_odds.get('over_2.5', 0), market_odds.get('over_2.5', 0),
         probabilities['over_2.5']),
        ("BTTS Yes", expected_values.get('btts_yes', 0),
         fair_odds.get('btts_yes', 0), market_odds.get('btts_yes', 0),
         probabilities['btts_yes'])
    ]
    
    bet_recommendations = []
    
    for idx, (bet_type, ev, fair_odd, market_odd, prob) in enumerate(ev_data):
        with cols[idx]:
            ev_color = "green" if ev > 0.1 else "orange" if ev > 0 else "red"
            ev_emoji = "✅" if ev > 0.1 else "⚠️" if ev > 0 else "❌"
            
            st.markdown(f"""
            <div class='metric-card'>
                <h4>{bet_type} {ev_emoji}</h4>
                <h3 style='color: {ev_color}'>{ev*100:.1f}%</h3>
                <small>Fair Odds: {fair_odd:.2f}<br>
                Market Odds: {market_odd:.2f}<br>
                Probability: {prob*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
            
            if ev > 0.1 and confidence > 0.65:
                bet_recommendations.append(f"**{bet_type}** (Edge: {ev*100:.1f}%)")
    
    if bet_recommendations:
        st.success(f"🎯 **Betting Recommendations:** {' | '.join(bet_recommendations)}")
        st.info(f"Confidence: {confidence*100:.1f}% > 65% threshold")

def display_confidence_meter(confidence, key_factors):
    """Display confidence meter and key factors"""
    st.markdown("## 🎯 Prediction Confidence")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Confidence gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence Level"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 65
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Key factors
        st.markdown("### 🔑 Key Influencing Factors")
        
        factors_html = ""
        
        # Home advantage
        home_adv = key_factors.get('home_advantage', 0)
        if abs(home_adv) > 0.5:
            direction = "Positive" if home_adv > 0 else "Negative"
            factors_html += f"<span class='factor-badge'>🏠 Home Advantage: {direction} ({home_adv:.2f})</span>"
        
        # Injury mismatch
        injury_diff = key_factors.get('injury_mismatch', 0)
        if abs(injury_diff) > 4:
            direction = "Home Favored" if injury_diff < 0 else "Away Favored"
            factors_html += f"<span class='factor-badge'>🏥 Injury Mismatch: {direction} ({abs(injury_diff)})</span>"
        
        # Form difference
        form_diff = key_factors.get('form_difference', 0)
        if abs(form_diff) > 4:
            direction = "Home Better" if form_diff > 0 else "Away Better"
            factors_html += f"<span class='factor-badge'>📈 Form Difference: {direction} ({abs(form_diff)} pts)</span>"
        
        # Lambda difference
        lambda_diff = key_factors.get('lambda_difference', 0)
        if lambda_diff > 1.0:
            factors_html += f"<span class='factor-badge'>⚡ Expected Goals Gap: {lambda_diff:.2f}</span>"
        
        if factors_html:
            st.markdown(factors_html, unsafe_allow_html=True)
        else:
            st.info("No strongly influencing factors identified")
        
        # Defense strength indicators
        st.markdown("### 🛡️ Defense Strength")
        col_a, col_b = st.columns(2)
        with col_a:
            defense_str = key_factors.get('defense_strength_home', 1)
            st.progress(defense_str, text=f"Home Defense: {defense_str:.1%}")
        with col_b:
            defense_str = key_factors.get('defense_strength_away', 1)
            st.progress(defense_str, text=f"Away Defense: {defense_str:.1%}")

def display_simulation_results(result, home_name, away_name):
    """Display simulation results"""
    st.markdown("## 🔮 Simulation Results")
    
    home_goals_sim, away_goals_sim = result.get('simulated_goals', (np.array([]), np.array([])))
    
    if len(home_goals_sim) > 0:
        # Most likely scorelines
        score_counts = {}
        for h, a in zip(home_goals_sim[:1000], away_goals_sim[:1000]):
            score = f"{h}-{a}"
            score_counts[score] = score_counts.get(score, 0) + 1
        
        top_scores = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Goal Distribution")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=home_goals_sim, name=home_name, opacity=0.7, marker_color='#4ECDC4'))
            fig.add_trace(go.Histogram(x=away_goals_sim, name=away_name, opacity=0.7, marker_color='#FF6B6B'))
            fig.update_layout(barmode='overlay', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Most Likely Scores")
            for score, count in top_scores:
                percentage = (count / 1000) * 100
                st.markdown(f"**{score}** - {percentage:.1f}%")
                st.progress(percentage / 100)
        
        with col3:
            st.markdown("### 📊 Match Statistics")
            avg_home = np.mean(home_goals_sim)
            avg_away = np.mean(away_goals_sim)
            clean_sheet_home = np.sum(away_goals_sim == 0) / len(away_goals_sim)
            clean_sheet_away = np.sum(home_goals_sim == 0) / len(home_goals_sim)
            
            metrics = [
                (f"Avg Goals ({home_name})", f"{avg_home:.2f}"),
                (f"Avg Goals ({away_name})", f"{avg_away:.2f}"),
                (f"{home_name} Clean Sheet", f"{clean_sheet_home:.1%}"),
                (f"{away_name} Clean Sheet", f"{clean_sheet_away:.1%}"),
                ("Total Goals > 2.5", f"{np.mean(home_goals_sim + away_goals_sim > 2.5):.1%}")
            ]
            
            for label, value in metrics:
                st.metric(label, value)

def main():
    """Main application"""
    
    # Header
    st.markdown("<h1 class='main-header'>⚽ Football Prediction Engine</h1>", unsafe_allow_html=True)
    st.markdown("### Advanced match prediction using Poisson distribution and machine learning")
    
    # Display current input configuration
    st.info("""
    **Current Configuration:**
    - Home Team: Higher xG (1.43) but high injury level (8) and low motivation (2)
    - Away Team: Lower xG (0.94) but better defense (12.9 shots allowed) and low injury level (2)
    - Market Odds: Home Win (1.79), Over 2.5 (2.30), BTTS Yes (2.10)
    """)
    
    # Initialize engine
    if 'engine' not in st.session_state:
        st.session_state.engine = PredictionEngine()
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    # Input section
    inputs = create_input_interface()
    
    # Calculate button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Calculate Prediction", type="primary", use_container_width=True):
        with st.spinner("Running simulations..."):
            # Simulate calculation time
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            # Run prediction
            result = st.session_state.engine.run_full_prediction(inputs)
            st.session_state.last_result = result
            
            st.success("✅ Prediction calculated successfully!")
    
    # Display results if available
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        # Display match header
        st.markdown(f"# 🏆 {inputs['home_name']} vs {inputs['away_name']}")
        
        # Team comparison
        display_team_comparison(inputs['home_name'], inputs['away_name'], inputs)
        
        # Lambda values
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Home Team λ (Expected Goals)", f"{result['home_lambda']:.3f}")
        with col2:
            st.metric("Away Team λ (Expected Goals)", f"{result['away_lambda']:.3f}")
        
        st.markdown("---")
        
        # Probability charts
        display_probability_charts(result['probabilities'], inputs['home_name'], inputs['away_name'])
        
        st.markdown("---")
        
        # Expected value analysis
        display_expected_values(
            result['expected_values'],
            result.get('fair_odds', {}),
            inputs['market_odds'],
            result['probabilities'],
            result['confidence']
        )
        
        st.markdown("---")
        
        # Confidence and key factors
        display_confidence_meter(result['confidence'], result.get('key_factors', {}))
        
        st.markdown("---")
        
        # Simulation results
        display_simulation_results(result, inputs['home_name'], inputs['away_name'])
        
        # Download results
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📥 Export Results"):
                # Create summary DataFrame
                summary = pd.DataFrame({
                    'Metric': ['Home Win', 'Draw', 'Away Win', 'Over 2.5', 'BTTS Yes', 'Confidence'],
                    'Value': [
                        f"{result['probabilities']['home_win']*100:.1f}%",
                        f"{result['probabilities']['draw']*100:.1f}%",
                        f"{result['probabilities']['away_win']*100:.1f}%",
                        f"{result['probabilities']['over_2.5']*100:.1f}%",
                        f"{result['probabilities']['btts_yes']*100:.1f}%",
                        f"{result['confidence']*100:.1f}%"
                    ],
                    'Expected Goals': [result['home_lambda'], '', result['away_lambda'], '', '', ''],
                    'Expected Value': [
                        f"{result['expected_values'].get('home_win', 0)*100:.1f}%",
                        '', '',
                        f"{result['expected_values'].get('over_2.5', 0)*100:.1f}%",
                        f"{result['expected_values'].get('btts_yes', 0)*100:.1f}%",
                        ''
                    ]
                })
                
                csv = summary.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"prediction_{inputs['home_name']}_vs_{inputs['away_name']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <small>
            ⚠️ Disclaimer: This is a simulation tool for educational purposes only. 
            Sports betting involves risk. Always gamble responsibly.<br>
            Prediction Engine v1.0 | Built with Streamlit
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
