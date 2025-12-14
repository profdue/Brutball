import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Live Football Predictor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .data-card {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .odds-display {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .over-odds {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .under-odds {
        background-color: #FEE2E2;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

# ========== LIVE PREDICTION ENGINE ==========
class LivePredictionEngine:
    """Optimized for live betting site data"""
    
    BIG_SIX = ["Manchester United", "Manchester City", "Liverpool", 
               "Chelsea", "Arsenal", "Tottenham"]
    
    def predict(self, match_data):
        """Make prediction from live betting data"""
        
        # Extract live data
        home_team = match_data['home_team']
        away_team = match_data['away_team']
        
        # Live odds data (from betting site)
        over_odds = float(match_data['over_odds'])
        under_odds = float(match_data['under_odds'])
        public_over = float(match_data['public_over'])
        
        # Team performance data
        home_recent_goals = float(match_data['home_recent_goals'])
        home_recent_conceded = float(match_data['home_recent_conceded'])
        away_recent_goals = float(match_data['away_recent_goals'])
        away_recent_conceded = float(match_data['away_recent_conceded'])
        
        # Context
        home_position = int(match_data['home_position'])
        away_position = int(match_data['away_position'])
        is_relegation = match_data.get('is_relegation', False)
        
        # ===== 1. CALCULATE EXPECTED GOALS =====
        # Simple average of attack vs defense
        home_attack = home_recent_goals
        away_defense = away_recent_conceded
        away_attack = away_recent_goals
        home_defense = home_recent_conceded
        
        expected_home = (home_attack + away_defense) / 2
        expected_away = (away_attack + home_defense) / 2
        expected_total = expected_home + expected_away
        
        # ===== 2. DETECT LIVE TRAPS =====
        traps = []
        
        # TRAP 1: Public vs Odds Mismatch
        implied_over = 1 / over_odds
        public_dec = public_over / 100
        
        if public_dec > implied_over + 0.15:  # Public much higher than odds suggest
            traps.append({
                'type': 'PUBLIC_OVERCONFIDENCE',
                'description': f'Public {public_over}% on Over but odds only imply {implied_over:.0%}',
                'impact': -0.10
            })
        
        # TRAP 2: Big Team at Home Trap
        if home_team in self.BIG_SIX and over_odds < 1.70:
            traps.append({
                'type': 'BIG_TEAM_HOME_TRAP',
                'description': f'{home_team} at home with low Over odds',
                'impact': -0.08
            })
        
        # TRAP 3: Relegation Fear Trap
        if is_relegation and under_odds < 1.80:
            traps.append({
                'type': 'RELEGATION_FEAR_TRAP',
                'description': 'Relegation battle with low Under odds',
                'impact': 0.05  # Slight increase for Over
            })
        
        # TRAP 4: Odds Value Trap
        if over_odds > 2.10 and under_odds < 1.90:
            # High Over odds, low Under odds = market expects Under
            traps.append({
                'type': 'ODDS_VALUE_TRAP',
                'description': f'Over odds {over_odds} offer potential value',
                'impact': 0.07
            })
        
        # ===== 3. CALCULATE TRUE PROBABILITY =====
        # Base probability from expected goals
        if expected_total >= 3.2:
            base_over = 0.68
        elif expected_total >= 2.8:
            base_over = 0.58
        elif expected_total >= 2.5:
            base_over = 0.48
        elif expected_total >= 2.2:
            base_over = 0.38
        elif expected_total >= 1.8:
            base_over = 0.28
        else:
            base_over = 0.18
        
        # Apply position pressure
        if home_position >= 17:  # Deep relegation
            base_over += 0.05  # Desperate teams take risks
        elif 1 <= home_position <= 4:  # Title race
            base_over -= 0.03  # More cautious
        
        # Apply trap adjustments
        trap_adjustment = sum(trap['impact'] for trap in traps)
        true_over = base_over + trap_adjustment
        true_over = max(0.15, min(0.85, true_over))
        true_under = 1 - true_over
        
        # ===== 4. CALCULATE EDGE =====
        implied_over = 1 / over_odds
        implied_under = 1 / under_odds
        
        # Normalize for bookmaker margin
        total_implied = implied_over + implied_under
        if total_implied > 1.0:
            implied_over = implied_over / total_implied
            implied_under = implied_under / total_implied
        
        edge_over = (true_over - implied_over) * 100
        edge_under = (true_under - implied_under) * 100
        
        # ===== 5. MAKE DECISION =====
        if edge_over > 1.5 and edge_over > edge_under:
            prediction = 'OVER_2.5'
            edge = edge_over
        elif edge_under > 1.5 and edge_under > edge_over:
            prediction = 'UNDER_2.5'
            edge = edge_under
        else:
            prediction = 'NO_VALUE_BET'
            edge = 0
        
        # ===== 6. CONFIDENCE & BET SIZE =====
        confidence = self._calculate_confidence(expected_total, abs(edge), len(traps))
        bet_size = self._calculate_bet_size(edge, confidence, len(traps))
        
        return {
            'prediction': prediction,
            'edge': edge,
            'confidence': confidence,
            'expected_total': expected_total,
            'home_expected': expected_home,
            'away_expected': expected_away,
            'traps': traps,
            'bet_size': bet_size,
            'true_over': true_over,
            'true_under': true_under,
            'implied_over': implied_over,
            'implied_under': implied_under,
            'edge_over': edge_over,
            'edge_under': edge_under,
            'recommendation': self._get_recommendation(prediction, edge, len(traps))
        }
    
    def _calculate_confidence(self, expected_total, edge, trap_count):
        """Calculate confidence based on clarity of signals"""
        confidence = 0.6  # Base
        
        # Clear expected goals
        if expected_total > 3.0 or expected_total < 2.0:
            confidence += 0.15
        
        # Strong edge
        if edge > 8:
            confidence += 0.20
        elif edge > 4:
            confidence += 0.10
        
        # Trap penalty
        confidence -= trap_count * 0.05
        
        return max(0.3, min(0.95, confidence))
    
    def _calculate_bet_size(self, edge, confidence, trap_count):
        """Simple bet sizing"""
        if edge <= 0:
            return 0.0
        
        base = (edge / 100) * confidence
        
        if trap_count > 0:
            base *= 0.7
        
        if base > 0.10:
            return 0.10
        elif base < 0.01:
            return 0.01
        
        return round(base, 3)
    
    def _get_recommendation(self, prediction, edge, trap_count):
        """Generate clear recommendation"""
        if prediction == 'NO_VALUE_BET':
            return "NO BET - No clear value"
        
        if edge > 10:
            strength = "STRONG"
        elif edge > 5:
            strength = "CONFIDENT"
        elif edge > 2:
            strength = "MODERATE"
        else:
            strength = "SMALL"
        
        if trap_count > 0:
            return f"{strength} BET on {prediction} (traps detected)"
        else:
            return f"{strength} BET on {prediction}"

# ========== LIVE DATA INPUT FORM ==========
def create_live_input_form():
    """Form optimized for live betting data entry"""
    
    st.markdown("## ⚡ LIVE BETTING DATA INPUT")
    
    # Match info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Home Team")
        home_team = st.text_input("Team", "Burnley")
        
        st.markdown("**Recent Home Form (Last 5 Games)**")
        home_recent_goals = st.number_input("Goals Scored Avg", 0.0, 5.0, 0.6, 0.1)
        home_recent_conceded = st.number_input("Goals Conceded Avg", 0.0, 5.0, 1.2, 0.1)
        
        home_position = st.number_input("League Position", 1, 20, 19)
    
    with col2:
        st.markdown("### 🚌 Away Team")
        away_team = st.text_input("Team", "Fulham")
        
        st.markdown("**Recent Away Form (Last 5 Games)**")
        away_recent_goals = st.number_input("Goals Scored Avg", 0.0, 5.0, 1.0, 0.1)
        away_recent_conceded = st.number_input("Goals Conceded Avg", 0.0, 5.0, 2.2, 0.1)
        
        away_position = st.number_input("League Position", 1, 20, 15)
    
    st.markdown("---")
    
    # Live betting data (FROM YOUR SITE)
    st.markdown("### 📊 LIVE MARKET DATA")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="odds-display over-odds">OVER 2.5</div>', unsafe_allow_html=True)
        over_odds = st.number_input("Odds", 1.1, 10.0, 2.15, 0.05, key="over_live")
        
        st.markdown("**Public Betting**")
        public_over = st.number_input("% on Over", 0, 100, 60, key="public_live")
    
    with col4:
        st.markdown('<div class="odds-display under-odds">UNDER 2.5</div>', unsafe_allow_html=True)
        under_odds = st.number_input("Odds", 1.1, 10.0, 1.85, 0.05, key="under_live")
        
        st.markdown("**Match Context**")
        is_relegation = st.checkbox("Relegation Battle?", True, key="relegation")
    
    # Create match data
    match_data = {
        'home_team': home_team,
        'away_team': away_team,
        'home_recent_goals': home_recent_goals,
        'home_recent_conceded': home_recent_conceded,
        'away_recent_goals': away_recent_goals,
        'away_recent_conceded': away_recent_conceded,
        'over_odds': over_odds,
        'under_odds': under_odds,
        'public_over': public_over,
        'home_position': home_position,
        'away_position': away_position,
        'is_relegation': is_relegation
    }
    
    return match_data

# ========== DISPLAY LIVE RESULTS ==========
def display_live_results(prediction):
    """Display results for live betting"""
    
    st.markdown("## 🎯 LIVE PREDICTION")
    
    # Quick decision
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pred = prediction['prediction']
        if pred == 'NO_VALUE_BET':
            st.error("### ⛔ NO BET")
        elif pred == 'OVER_2.5':
            st.success("### 📈 BET OVER 2.5")
        else:
            st.success("### 📉 BET UNDER 2.5")
        
        st.metric("Expected Goals", f"{prediction['expected_total']:.1f}")
        st.metric("Edge", f"{prediction['edge']:.1f}%")
    
    with col2:
        st.metric("Confidence", f"{prediction['confidence']*100:.0f}%")
        st.metric("Bet Size", f"{prediction['bet_size']*100:.1f}%")
        
        # Quick recommendation
        st.info(f"**{prediction['recommendation']}**")
    
    with col3:
        st.metric("True Over Prob", f"{prediction['true_over']:.1%}")
        st.metric("Implied Over Prob", f"{prediction['implied_over']:.1%}")
    
    # Traps detected
    if prediction['traps']:
        st.markdown("### 🚨 MARKET WARNINGS")
        for trap in prediction['traps']:
            st.warning(f"**{trap['type']}**: {trap['description']}")
    
    # Detailed analysis
    with st.expander("📊 DETAILED ANALYSIS"):
        
        # Probability chart
        st.markdown("#### Probability Comparison")
        fig = go.Figure(data=[
            go.Bar(name='True Probability', 
                   x=['Over 2.5', 'Under 2.5'], 
                   y=[prediction['true_over'], prediction['true_under']],
                   marker_color=['#10B981', '#EF4444']),
            go.Bar(name='Implied Probability', 
                   x=['Over 2.5', 'Under 2.5'],
                   y=[prediction['implied_over'], prediction['implied_under']],
                   marker_color=['#34D399', '#FCA5A5'])
        ])
        fig.update_layout(barmode='group', height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Edge analysis
        col4, col5 = st.columns(2)
        
        with col4:
            st.metric("Over Edge", f"{prediction['edge_over']:.1f}%")
            st.metric("Under Edge", f"{prediction['edge_under']:.1f}%")
        
        with col5:
            st.write("**Expected Breakdown:**")
            st.write(f"Home: {prediction['home_expected']:.1f} goals")
            st.write(f"Away: {prediction['away_expected']:.1f} goals")
            st.write(f"Total: {prediction['expected_total']:.1f} goals")
        
        # Decision factors
        st.markdown("#### Decision Factors")
        factors = []
        
        if prediction['edge'] > 5:
            factors.append(f"Strong edge ({prediction['edge']:.1f}%)")
        if prediction['expected_total'] > 2.8:
            factors.append("High expected goals")
        elif prediction['expected_total'] < 2.2:
            factors.append("Low expected goals")
        if prediction['traps']:
            factors.append(f"{len(prediction['traps'])} market traps detected")
        
        for factor in factors:
            st.write(f"✅ {factor}")

# ========== MAIN APP ==========
def main():
    st.markdown('<h1 class="main-header">⚡ LIVE FOOTBALL PREDICTOR</h1>', unsafe_allow_html=True)
    st.markdown("### Optimized for real-time betting site data")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 DATA FROM YOUR SITE")
        st.info("""
        **Enter exactly what you see:**
        
        FT
        Burnley 2:3 Fulham
        60% public on Over
        O 2.5 @ 2.15
        U 2.5 @ 1.85
        
        **Plus recent form:**
        Last 5 HOME games (Burnley)
        Last 5 AWAY games (Fulham)
        """)
        
        st.warning("**Copy ALL values from site**")
    
    # Create input form
    match_data = create_live_input_form()
    
    # Predict button
    if st.button("⚡ ANALYZE LIVE DATA", type="primary", use_container_width=True):
        engine = LivePredictionEngine()
        prediction = engine.predict(match_data)
        
        st.session_state.live_prediction = prediction
        st.session_state.live_match_data = match_data
        st.rerun()
    
    # Show results
    if 'live_prediction' in st.session_state:
        display_live_results(st.session_state.live_prediction)
        
        # Data verification
        st.markdown("---")
        st.markdown("### ✅ DATA VERIFICATION")
        
        data = st.session_state.live_match_data
        col6, col7 = st.columns(2)
        
        with col6:
            st.write("**From Your Site:**")
            st.write(f"Over 2.5: {data['over_odds']}")
            st.write(f"Under 2.5: {data['under_odds']}")
            st.write(f"Public: {data['public_over']}% on Over")
        
        with col7:
            st.write("**Team Form:**")
            st.write(f"{data['home_team']}: {data['home_recent_goals']} scored, {data['home_recent_conceded']} conceded")
            st.write(f"{data['away_team']}: {data['away_recent_goals']} scored, {data['away_recent_conceded']} conceded")

# Run the app
if __name__ == "__main__":
    main()
