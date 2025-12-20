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
# LEAGUE-SPECIFIC PARAMETERS - REFINED VERSION
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
# REFINED CALIBRATED PREDICTION ENGINE
# ============================================================================

class RefinedFootballPredictor:
    """
    Refined version with soft penalty bands for mid-range scoring slumps
    """
    
    def __init__(self, league_params):
        self.league_params = league_params
        self.reset()
    
    def reset(self):
        self.debug_info = []
        self.key_factors = []
        self.scoring_insights = []
        self.calibration_notes = []
    
    # ==================== REFINED CORE LOGIC ====================
    
    def _adjust_for_recent_scoring(self, team_data, base_lambda, is_home):
        """
        REFINEMENT: Graduated penalty system for mid-range scoring slumps
        """
        recent_goals = team_data.get('goals_scored_last_5', 0) / 5
        
        # REFINED: Graduated penalties based on scoring performance
        if recent_goals == 0:
            adjustment = 0.5  # Crisis: -50%
            note = f"{'Home' if is_home else 'Away'} scoring crisis: 0 goals in last 5 games (-50% penalty)"
        elif recent_goals < 0.4:
            adjustment = 0.7  # Very poor: -30%
            note = f"{'Home' if is_home else 'Away'} very poor scoring: {recent_goals:.1f} goals/game (-30% penalty)"
        elif recent_goals < 0.8:
            adjustment = 0.85  # Poor: -15% (NEW FIX!)
            note = f"{'Home' if is_home else 'Away'} poor scoring: {recent_goals:.1f} goals/game (-15% penalty)"
        elif recent_goals < 1.2:
            adjustment = 1.0  # Average: no adjustment
            note = None
        elif recent_goals < 1.8:
            adjustment = 1.1  # Good: +10%
            note = f"{'Home' if is_home else 'Away'} good scoring: {recent_goals:.1f} goals/game (+10% boost)"
        else:
            adjustment = 1.2  # Excellent: +20%
            note = f"{'Home' if is_home else 'Away'} excellent scoring: {recent_goals:.1f} goals/game (+20% boost)"
        
        if note:
            self.calibration_notes.append(note)
        
        adjusted_lambda = base_lambda * adjustment
        
        self.debug_info.append(f"Recent Scoring ({'Home' if is_home else 'Away'}): recent={recent_goals:.1f}, adj={adjustment:.2f}, λ={adjusted_lambda:.2f}")
        
        return adjusted_lambda
    
    def _calculate_btts_probability(self, home_data, away_data):
        """
        REFINED: Better BTTS logic with recent scoring bands
        """
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        
        # Start with base probability
        base = 0.5
        
        # REFINED: Use same scoring bands as lambda adjustment
        if home_recent == 0:
            base -= 0.3
        elif home_recent < 0.4:
            base -= 0.2
        elif home_recent < 0.8:
            base -= 0.1  # Soft penalty
        elif home_recent > 1.8:
            base += 0.15
        
        if away_recent == 0:
            base -= 0.3
        elif away_recent < 0.4:
            base -= 0.2
        elif away_recent < 0.8:
            base -= 0.1  # Soft penalty
        elif away_recent > 1.8:
            base += 0.15
        
        # Position gap effect
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff > 10:
            base -= 0.15
        
        # Both teams scoring well recently
        if home_recent > 1.5 and away_recent > 1.2:
            base += 0.15
        
        # Apply bounds
        btts_prob = max(0.15, min(0.85, base))
        
        self.debug_info.append(f"BTTS: home={home_recent:.1f}, away={away_recent:.1f}, prob={btts_prob:.2f}")
        
        return btts_prob
    
    def _calculate_confidence(self, home_lambda, away_lambda, home_data, away_data):
        """
        REFINED: Better confidence calculation
        """
        confidence = 50
        
        # Goal difference
        goal_diff = abs(home_lambda - away_lambda)
        confidence += goal_diff * 10  # Reduced from 15
        
        # Position difference
        pos_diff = abs(home_data['overall_position'] - away_data['overall_position'])
        if pos_diff >= 10:
            confidence += 20
        elif pos_diff >= 5:
            confidence += 10
        
        # REFINEMENT: Reduce confidence for poor recent scoring
        home_recent = home_data.get('goals_scored_last_5', 0) / 5
        away_recent = away_data.get('goals_scored_last_5', 0) / 5
        
        if home_recent < 0.8 or away_recent < 0.8:
            confidence -= 10  # Lower confidence for poor scoring teams
        
        # REFINEMENT: Increase confidence for consistent teams
        home_goals = home_data.get('goals', 0) / max(home_data.get('matches_played', 1), 1)
        away_goals = away_data.get('goals', 0) / max(away_data.get('matches_played', 1), 1)
        
        home_consistency = min(1.0, home_recent / home_goals) if home_goals > 0 else 0.5
        away_consistency = min(1.0, away_recent / away_goals) if away_goals > 0 else 0.5
        
        consistency_bonus = (home_consistency + away_consistency - 1.0) * 5
        confidence += consistency_bonus
        
        return round(max(30, min(85, confidence)), 1)
    
    # ==================== EXISTING METHODS (KEEPING ODDS LOGIC) ====================
    
    def _calculate_position_factor(self, position):
        """Realistic position impact"""
        if position <= 3:
            factor = 1.25
        elif position <= 6:
            factor = 1.15
        elif position <= 12:
            factor = 1.05
        elif position <= 16:
            factor = 0.95
        else:
            factor = 0.85
        return factor
    
    def _calculate_true_strength(self, team_data, is_home):
        """Team strength calculation"""
        if is_home:
            base_xg = team_data.get('home_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        else:
            base_xg = team_data.get('away_xg_for', 0) / max(team_data.get('matches_played', 1), 1)
        
        position = team_data.get('overall_position', 20)
        position_factor = self._calculate_position_factor(position)
        
        total_goals = team_data.get('goals', 0)
        total_xg = team_data.get('xg', 0)
        efficiency = total_goals / total_xg if total_xg > 0 else 1.0
        
        true_strength = base_xg * position_factor * efficiency
        
        self.debug_info.append(f"True Strength ({'Home' if is_home else 'Away'}): base={base_xg:.2f}, pos={position}, factor={position_factor:.2f}, eff={efficiency:.2f}, strength={true_strength:.2f}")
        
        return true_strength
    
    def _calculate_home_advantage(self, home_data, away_data):
        """Home advantage calculation"""
        home_ppg_diff = home_data.get('home_ppg_diff', 0)
        home_position = home_data.get('overall_position', 10)
        
        base = self.league_params['home_advantage']
        
        if home_position >= 16:
            base = 1.05
        
        ppg_adjustment = 1.0 + (min(1.0, max(-0.5, home_ppg_diff)) * 0.1)
        final_advantage = base * ppg_adjustment
        
        away_position = away_data.get('overall_position', 10)
        if away_position <= 6:
            final_advantage *= 0.9
        
        final_advantage = max(1.02, min(1.35, final_advantage))
        
        self.debug_info.append(f"Home Advantage: base={base:.2f}, ppg={home_ppg_diff:.1f}, final={final_advantage:.2f}")
        
        return final_advantage
    
    # ==================== MAIN PREDICTION METHOD ====================
    
    def predict_match(self, home_data, away_data):
        """Main prediction method"""
        self.reset()
        
        # Calculate true strength
        home_strength = self._calculate_true_strength(home_data, is_home=True)
        away_strength = self._calculate_true_strength(away_data, is_home=False)
        
        # Apply recent scoring adjustment (REFINED)
        home_strength = self._adjust_for_recent_scoring(home_data, home_strength, is_home=True)
        away_strength = self._adjust_for_recent_scoring(away_data, away_strength, is_home=False)
        
        # Other factors
        home_advantage = self._calculate_home_advantage(home_data, away_data)
        
        # Integrate factors
        home_lambda = home_strength * home_advantage
        away_lambda = away_strength * (2.0 - home_advantage)
        
        # Final calibration
        home_lambda, away_lambda = self._final_calibration(home_lambda, away_lambda, home_data, away_data)
        
        # Scoring predictions
        scoring_prediction = self._predict_scoring_patterns(home_data, away_data, home_lambda, away_lambda)
        
        # Calculate probabilities
        probabilities = self._calculate_probabilities(home_lambda, away_lambda)
        
        # Generate key factors
        key_factors = self._generate_key_factors(home_data, away_data, home_lambda, away_lambda, scoring_prediction)
        
        # Combine debug info
        all_info = self.calibration_notes + self.debug_info + [f"Final: Home λ={home_lambda:.2f}, Away λ={away_lambda:.2f}, Total={home_lambda+away_lambda:.2f}"]
        
        return {
            'expected_goals': {'home': home_lambda, 'away': away_lambda},
            'probabilities': probabilities,
            'scoring_analysis': scoring_prediction,
            'confidence': self._calculate_confidence(home_lambda, away_lambda, home_data, away_data),
            'key_factors': key_factors + all_info,
            'success': True
        }
    
    def _predict_scoring_patterns(self, home_data, away_data, home_lambda, away_lambda):
        """Predict total goals and BTTS"""
        total_lambda = home_lambda + away_lambda
        
        # Over/under probability based on total
        if total_lambda <= 1.8:
            over_prob = 0.25
        elif total_lambda <= 2.2:
            over_prob = 0.40
        elif total_lambda <= 2.6:
            over_prob = 0.55
        elif total_lambda <= 3.0:
            over_prob = 0.70
        else:
            over_prob = 0.85
        
        # BTTS probability (REFINED)
        btts_prob = self._calculate_btts_probability(home_data, away_data)
        
        return {
            'predicted_total': total_lambda,
            'over_25_prob': over_prob,
            'under_25_prob': 1 - over_prob,
            'btts_prob': btts_prob,
            'btts_no_prob': 1 - btts_prob,
        }
    
    def _final_calibration(self, home_lambda, away_lambda, home_data, away_data):
        """Final calibration"""
        home_lambda = max(CONSTANTS['MIN_HOME_LAMBDA'], home_lambda)
        away_lambda = max(CONSTANTS['MIN_AWAY_LAMBDA'], away_lambda)
        
        home_lambda = min(3.0, home_lambda)
        away_lambda = min(2.5, away_lambda)
        
        total = home_lambda + away_lambda
        if total > 4.5:
            scale = 4.5 / total
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
        
        return factors
    
    def get_market_recommendations(self, probabilities, scoring_analysis, market_odds):
        """
        CRITICAL: KEEPING ODDS RECOMMENDATIONS
        Generate market recommendations with expected value
        """
        recommendations = []
        
        # Total Goals recommendation
        if scoring_analysis['over_25_prob'] > scoring_analysis['under_25_prob']:
            rec = {
                'market': 'Total Goals',
                'prediction': 'Over 2.5',
                'probability': scoring_analysis['over_25_prob'],
                'fair_odds': 1 / scoring_analysis['over_25_prob'],
                'market_odds': market_odds.get('over_25', 1.85),
                'strength': self._get_strength_level(scoring_analysis['over_25_prob'])
            }
        else:
            rec = {
                'market': 'Total Goals',
                'prediction': 'Under 2.5',
                'probability': scoring_analysis['under_25_prob'],
                'fair_odds': 1 / scoring_analysis['under_25_prob'],
                'market_odds': 1 / (1 - 1/market_odds.get('over_25', 1.85)) if market_odds.get('over_25', 1.85) > 1 else 2.00,
                'strength': self._get_strength_level(scoring_analysis['under_25_prob'])
            }
        recommendations.append(rec)
        
        # BTTS recommendation
        if scoring_analysis['btts_prob'] > scoring_analysis['btts_no_prob']:
            rec = {
                'market': 'Both Teams to Score',
                'prediction': 'Yes',
                'probability': scoring_analysis['btts_prob'],
                'fair_odds': 1 / scoring_analysis['btts_prob'],
                'market_odds': market_odds.get('btts_yes', 1.75),
                'strength': self._get_strength_level(scoring_analysis['btts_prob'])
            }
        else:
            rec = {
                'market': 'Both Teams to Score',
                'prediction': 'No',
                'probability': scoring_analysis['btts_no_prob'],
                'fair_odds': 1 / scoring_analysis['btts_no_prob'],
                'market_odds': 1 / (1 - 1/market_odds.get('btts_yes', 1.75)) if market_odds.get('btts_yes', 1.75) > 1 else 2.00,
                'strength': self._get_strength_level(scoring_analysis['btts_no_prob'])
            }
        recommendations.append(rec)
        
        # Match outcome recommendation
        if probabilities['home_win'] > max(probabilities['draw'], probabilities['away_win']):
            rec = {
                'market': 'Match Result',
                'prediction': 'Home Win',
                'probability': probabilities['home_win'],
                'fair_odds': 1 / probabilities['home_win'],
                'market_odds': market_odds.get('home', 2.50),
                'strength': self._get_strength_level(probabilities['home_win'])
            }
        elif probabilities['draw'] > probabilities['away_win']:
            rec = {
                'market': 'Match Result',
                'prediction': 'Draw',
                'probability': probabilities['draw'],
                'fair_odds': 1 / probabilities['draw'],
                'market_odds': market_odds.get('draw', 3.40),
                'strength': self._get_strength_level(probabilities['draw'])
            }
        else:
            rec = {
                'market': 'Match Result',
                'prediction': 'Away Win',
                'probability': probabilities['away_win'],
                'fair_odds': 1 / probabilities['away_win'],
                'market_odds': market_odds.get('away', 2.80),
                'strength': self._get_strength_level(probabilities['away_win'])
            }
        recommendations.append(rec)
        
        return recommendations
    
    def _get_strength_level(self, probability):
        """Determine recommendation strength"""
        if probability > 0.65:
            return 'Strong'
        elif probability > 0.55:
            return 'Moderate'
        else:
            return 'Weak'

# ============================================================================
# STREAMLIT UI WITH ODDS RECOMMENDATIONS
# ============================================================================

def display_market_recommendation(rec):
    """Display market recommendation with odds"""
    if rec['prediction'] in ['Over 2.5', 'Yes', 'Home Win']:
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
    """Display market odds input"""
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
# MAIN APPLICATION (KEEPING ODDS)
# ============================================================================

def main():
    st.set_page_config(
        page_title="Refined Football Predictor",
        page_icon="⚽",
        layout="wide"
    )
    
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">⚽ Refined Football Predictor</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">REFINED: Soft penalty bands for mid-range scoring slumps</p>', 
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
        st.markdown("### 🔧 Refinement Updates")
        st.success("""
        **Key Refinements:**
        1. **Soft penalty bands**: 0.5-0.9 goals = -15%
        2. **Better BTTS logic**: Graduated penalties
        3. **Improved confidence**: Accounts for poor scoring
        4. **Kept odds recommendations**: Market analysis included
        """)
    
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
    with col2:
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options, key="away_team")
    
    # Market odds input
    market_odds = display_market_odds_interface()
    
    if st.button("🚀 Run Refined Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams.")
            return
        
        try:
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            predictor = RefinedFootballPredictor(league_params)
            
            with st.spinner("Running refined analysis..."):
                result = predictor.predict_match(home_data, away_data)
                
                if result['success']:
                    # Generate market recommendations
                    recommendations = predictor.get_market_recommendations(
                        result['probabilities'], 
                        result['scoring_analysis'], 
                        market_odds
                    )
                    
                    st.session_state.prediction_result = result
                    st.session_state.recommendations = recommendations
                    st.success("✅ Refined analysis complete!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.session_state.get('prediction_result'):
        result = st.session_state.prediction_result
        recommendations = st.session_state.get('recommendations', [])
        
        st.markdown("---")
        st.markdown("# 📊 Refined Analysis Results")
        
        # Display predictions
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"🏠 {home_team} Expected Goals", f"{result['expected_goals']['home']:.2f}")
        with col2:
            st.metric(f"✈️ {away_team} Expected Goals", f"{result['expected_goals']['away']:.2f}")
        
        # Display scoring analysis
        st.markdown("### ⚽ Scoring Analysis")
        scoring = result['scoring_analysis']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Over 2.5", f"{scoring['over_25_prob']*100:.1f}%")
        with col2:
            st.metric("Under 2.5", f"{scoring['under_25_prob']*100:.1f}%")
        with col3:
            st.metric("BTTS Yes", f"{scoring['btts_prob']*100:.1f}%")
        with col4:
            st.metric("BTTS No", f"{scoring['btts_no_prob']*100:.1f}%")
        
        # Display market recommendations (CRITICAL - KEEPING THIS)
        if recommendations:
            st.markdown("### 💰 Market Recommendations")
            for rec in recommendations:
                display_market_recommendation(rec)
        
        # Display confidence
        confidence = result['confidence']
        st.metric("Model Confidence", f"{confidence:.1f}%")
        
        # Display key factors
        if result['key_factors']:
            with st.expander("🔍 View Analysis Details"):
                for factor in result['key_factors']:
                    st.write(f"• {factor}")

# Helper functions (kept from previous versions)
def load_league_data(league_name):
    """Load league data"""
    github_urls = {
        'LA LIGA': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/la_liga.csv',
        'PREMIER LEAGUE': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
    }
    
    url = github_urls.get(league_name.upper())
    if not url:
        return None
    
    try:
        response = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        return df
    except:
        return None

def prepare_team_data(df, team_name, venue):
    """Prepare team data"""
    team_data = df[(df['team'] == team_name) & (df['venue'] == venue.lower())]
    if team_data.empty:
        raise ValueError(f"No data found for {team_name}")
    return team_data.iloc[0].to_dict()

if __name__ == "__main__":
    main()
