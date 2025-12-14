import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Anti-Manipulation Football Predictor",
    page_icon="🎯",
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
    .input-section {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== ORIGINAL WORKING LOGIC WITH ONE FIX ==========
class FootballPredictionEngine:
    """Original working logic with ONE critical fix for desperate goalless teams"""
    
    BIG_SIX = ["Manchester United", "Manchester City", "Liverpool", 
               "Chelsea", "Arsenal", "Tottenham"]
    
    def predict(self, match_data):
        """Make prediction based on original logic with one fix"""
        
        # Extract data
        home_team = match_data['home_team']
        away_team = match_data['away_team']
        
        # Get recent form (last 5 games)
        home_recent_goals = float(match_data['home_recent_goals'])
        home_recent_conceded = float(match_data['home_recent_conceded'])
        away_recent_goals = float(match_data['away_recent_goals'])
        away_recent_conceded = float(match_data['away_recent_conceded'])
        
        # Get historical data
        home_hist_goals = float(match_data.get('home_hist_goals', home_recent_goals))
        home_hist_conceded = float(match_data.get('home_hist_conceded', home_recent_conceded))
        away_hist_goals = float(match_data.get('away_hist_goals', away_recent_goals))
        away_hist_conceded = float(match_data.get('away_hist_conceded', away_recent_conceded))
        
        # Get odds and public betting
        over_odds = float(match_data['over_odds'])
        under_odds = float(match_data['under_odds'])
        public_over = float(match_data['public_over'])
        
        # Get context
        home_position = int(match_data['home_position'])
        away_position = int(match_data['away_position'])
        home_points = int(match_data.get('home_points', 30))
        is_relegation = match_data.get('is_relegation', False)
        is_derby = match_data.get('is_derby', False)
        h2h_over = float(match_data.get('h2h_over', 50))
        recent_over = float(match_data.get('recent_over', 50))
        
        # ===== STEP 1: Calculate expected goals =====
        # Weighted: 80% recent form, 20% historical
        home_expected = (home_recent_goals * 0.8) + (home_hist_goals * 0.2)
        away_expected = (away_recent_goals * 0.8) + (away_hist_goals * 0.2)
        
        # Adjust for opponent defense
        home_expected_adj = (home_expected + away_recent_conceded) / 2
        away_expected_adj = (away_expected + home_recent_conceded) / 2
        
        expected_total = home_expected_adj + away_expected_adj
        
        # ===== STEP 2: Detect traps (ORIGINAL LOGIC) =====
        traps = []
        
        # TRAP 1: Over Hype (Big team at home, public heavy on Over)
        if (home_team in self.BIG_SIX and 
            public_over > 70 and  # ORIGINAL: >70%
            over_odds < 1.65):    # ORIGINAL: <1.65
            traps.append({
                'type': 'OVER_HYPE_TRAP',
                'description': f'Big team at home, public {public_over}% on Over',
                'impact': -0.15
            })
        
        # TRAP 2: Under Fear (Relegation battle, public heavy on Under)
        if (is_relegation and 
            public_over < 30 and  # ORIGINAL: <30%
            under_odds < 1.70):   # ORIGINAL: <1.70
            traps.append({
                'type': 'UNDER_FEAR_TRAP', 
                'description': f'Relegation battle, public only {public_over}% on Over',
                'impact': 0.10
            })
        
        # TRAP 3: Historical Data Trap (ORIGINAL)
        if h2h_over > 70 and recent_over < 40:  # ORIGINAL thresholds
            traps.append({
                'type': 'HISTORICAL_DATA_TRAP',
                'description': f'H2H shows {h2h_over}% Over but recent only {recent_over}%',
                'impact': -0.10
            })
        
        # ===== STEP 3: Pressure Context Analysis (ORIGINAL WITH ONE FIX) =====
        pressure_adjustment = 0
        pressure_scenarios = []
        
        # SCENARIO 1: Desperation Home Win (ORIGINAL WITH FIX)
        if home_position >= 15 and home_points <= 20:
            # ===== THE ONE CRITICAL FIX =====
            if home_recent_goals < 0.8:  # Goalless desperate team
                pressure_scenarios.append('DESPERATION_CHAOS')
                pressure_adjustment += 0.0  # Neutral - unpredictable
            else:
                pressure_scenarios.append('DESPERATION_HOME_WIN')
                pressure_adjustment -= 0.10  # Original: more cautious
            # ===== END FIX =====
        
        # SCENARIO 2: Nothing to Play For (ORIGINAL)
        if (8 <= home_position <= 12 and 
            8 <= away_position <= 12 and
            int(match_data.get('games_remaining', 10)) <= 5):
            pressure_scenarios.append('NOTHING_TO_PLAY_FOR')
            pressure_adjustment += 0.15  # Original: more open
        
        # SCENARIO 3: Derby Pressure Cooker (ORIGINAL)
        if is_derby:
            pressure_scenarios.append('DERBY_PRESSURE')
            pressure_adjustment -= 0.05  # Original: tighter
        
        # ===== STEP 4: Form vs History Conflict (ORIGINAL) =====
        form_adjustment = 1.0
        form_conflicts = []
        
        # Conflict 1: Scoring Decline (ORIGINAL)
        if home_hist_goals > 2.8 and home_recent_goals < 2.2:
            form_conflicts.append('HOME_SCORING_DECLINE')
            form_adjustment *= 0.75  # Original: 25% reduction
        
        if away_hist_goals > 2.8 and away_recent_goals < 2.2:
            form_conflicts.append('AWAY_SCORING_DECLINE')
            form_adjustment *= 0.75
        
        # Conflict 2: Defensive Improvement (ORIGINAL)
        if home_hist_conceded > 1.5 and home_recent_conceded < 1.0:
            form_conflicts.append('HOME_DEFENSIVE_IMPROVEMENT')
            form_adjustment *= 0.85  # Original: 15% reduction
        
        if away_hist_conceded > 1.5 and away_recent_conceded < 1.0:
            form_conflicts.append('AWAY_DEFENSIVE_IMPROVEMENT')
            form_adjustment *= 0.85
        
        # ===== STEP 5: Calculate true probabilities =====
        # Base probability from expected goals (ORIGINAL MAPPING)
        if expected_total >= 3.2:
            base_over = 0.70
        elif expected_total >= 2.8:
            base_over = 0.60
        elif expected_total >= 2.5:
            base_over = 0.50
        elif expected_total >= 2.2:
            base_over = 0.40
        elif expected_total >= 1.8:
            base_over = 0.30
        else:
            base_over = 0.20
        
        # Apply adjustments (ORIGINAL)
        trap_adjustment = sum(trap['impact'] for trap in traps)
        
        true_over = base_over + pressure_adjustment + trap_adjustment
        true_over *= form_adjustment  # Apply form conflict adjustment
        
        true_over = max(0.15, min(0.85, true_over))
        true_under = 1 - true_over
        
        # ===== STEP 6: Calculate value =====
        implied_over = 1 / over_odds
        implied_under = 1 / under_odds
        
        # Adjust for bookmaker margin (ORIGINAL)
        total_implied = implied_over + implied_under
        if total_implied > 1.0:
            implied_over = implied_over / total_implied
            implied_under = implied_under / total_implied
        
        edge_over = (true_over - implied_over) * 100
        edge_under = (true_under - implied_under) * 100
        
        # ===== STEP 7: Make decision (ORIGINAL) =====
        if edge_over > 2 and edge_over > edge_under:
            prediction = 'OVER_2.5'
            edge = edge_over
            recommendation = self._get_recommendation(edge_over, len(traps))
        elif edge_under > 2 and edge_under > edge_over:
            prediction = 'UNDER_2.5'
            edge = edge_under
            recommendation = self._get_recommendation(edge_under, len(traps))
        else:
            prediction = 'NO_VALUE_BET'
            edge = 0
            recommendation = "No clear value found"
        
        # ===== STEP 8: Calculate confidence =====
        confidence = self._calculate_confidence(
            expected_total, abs(edge), len(traps), len(form_conflicts),
            'DESPERATION_CHAOS' in pressure_scenarios
        )
        
        # ===== STEP 9: Calculate bet size =====
        bet_size = self._calculate_bet_size(edge, confidence, len(traps), 
                                           'DESPERATION_CHAOS' in pressure_scenarios)
        
        return {
            'prediction': prediction,
            'edge': edge,
            'confidence': confidence,
            'expected_total': expected_total,
            'home_expected': home_expected_adj,
            'away_expected': away_expected_adj,
            'traps': traps,
            'pressure_scenarios': pressure_scenarios,
            'form_conflicts': form_conflicts,
            'recommendation': recommendation,
            'bet_size': bet_size,
            'probabilities': {
                'true_over': true_over,
                'true_under': true_under,
                'implied_over': implied_over,
                'implied_under': implied_under
            },
            'edges': {
                'over_edge': edge_over,
                'under_edge': edge_under
            }
        }
    
    def _get_recommendation(self, edge, trap_count):
        """ORIGINAL recommendation logic"""
        if edge > 10:
            base = "STRONG BET"
        elif edge > 5:
            base = "CONFIDENT BET"
        elif edge > 2:
            base = "MODERATE BET"
        else:
            return "NO BET"
        
        if trap_count >= 2:
            return f"CAUTIOUS {base}"
        elif trap_count == 1:
            return f"{base} (trap detected)"
        else:
            return f"{base}"
    
    def _calculate_confidence(self, expected_total, edge, trap_count, 
                            conflict_count, is_chaos_scenario):
        """ORIGINAL confidence with chaos penalty"""
        confidence = 0.7
        
        # Clear expected goals
        if expected_total > 3.0 or expected_total < 2.0:
            confidence += 0.15
        
        # Strong edge
        if edge > 8:
            confidence += 0.15
        elif edge > 4:
            confidence += 0.10
        
        # Penalties
        confidence -= trap_count * 0.08
        confidence -= conflict_count * 0.05
        
        # ===== THE FIX: Chaos scenario reduces confidence =====
        if is_chaos_scenario:
            confidence *= 0.7  # 30% reduction for unpredictability
        
        return max(0.3, min(0.95, confidence))
    
    def _calculate_bet_size(self, edge, confidence, trap_count, is_chaos_scenario):
        """ORIGINAL bet size with chaos reduction"""
        if edge <= 0:
            return 0.0
        
        base_size = (edge / 100) * confidence
        
        # Original reductions
        if trap_count > 0:
            base_size *= 0.7
        
        # ===== THE FIX: Chaos scenario further reduces bet size =====
        if is_chaos_scenario:
            base_size *= 0.5  # Half bet size for unpredictable matches
        
        # Original limits
        if base_size > 0.10:
            return 0.10
        elif base_size < 0.01:
            return 0.01
        
        return round(base_size, 3)

# ========== INPUT FORM ==========
def create_input_form():
    """Create input form matching our original data requirements"""
    
    with st.container():
        st.markdown("### 📝 Match Data Input")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏠 Home Team")
            home_team = st.text_input("Team", "Liverpool")
            
            st.markdown("**Recent Form (Last 5 HOME Games)**")
            home_recent_goals = st.number_input("Avg Goals Scored", 0.0, 5.0, 1.6, 0.1, key="home_rg")
            home_recent_conceded = st.number_input("Avg Goals Conceded", 0.0, 5.0, 1.4, 0.1, key="home_rc")
            
            st.markdown("**Historical Data**")
            home_hist_goals = st.number_input("Historical Avg Goals", 0.0, 5.0, 2.0, 0.1, key="home_hg")
            home_hist_conceded = st.number_input("Historical Avg Conceded", 0.0, 5.0, 1.3, 0.1, key="home_hc")
            
            home_position = st.number_input("League Position", 1, 20, 10, key="home_pos")
            home_points = st.number_input("Team Points", 0, 100, 23, key="home_pts")
        
        with col2:
            st.subheader("🚌 Away Team")
            away_team = st.text_input("Team", "Brighton")
            
            st.markdown("**Recent Form (Last 5 AWAY Games)**")
            away_recent_goals = st.number_input("Avg Goals Scored", 0.0, 5.0, 1.8, 0.1, key="away_rg")
            away_recent_conceded = st.number_input("Avg Goals Conceded", 0.0, 5.0, 1.2, 0.1, key="away_rc")
            
            st.markdown("**Historical Data**")
            away_hist_goals = st.number_input("Historical Avg Goals", 0.0, 5.0, 1.3, 0.1, key="away_hg")
            away_hist_conceded = st.number_input("Historical Avg Conceded", 0.0, 5.0, 2.0, 0.1, key="away_hc")
            
            away_position = st.number_input("League Position", 1, 20, 8, key="away_pos")
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("🎯 Market Data")
            over_odds = st.number_input("Over 2.5 Odds", 1.1, 10.0, 1.55, 0.05)
            under_odds = st.number_input("Under 2.5 Odds", 1.1, 10.0, 2.60, 0.05)
            public_over = st.number_input("Public % on Over", 0, 100, 66)
        
        with col4:
            st.subheader("📊 Match Context")
            is_derby = st.checkbox("Local Derby?")
            is_relegation = st.checkbox("Relegation Battle?")
            games_remaining = st.number_input("Games Remaining", 1, 38, 23)
            
            st.markdown("**Historical Stats**")
            h2h_over = st.number_input("H2H Over 2.5 %", 0, 100, 69)
            recent_over = st.number_input("Recent Over 2.5 %", 0, 100, 40)
        
        # Prepare match data
        match_data = {
            'home_team': home_team,
            'away_team': away_team,
            'home_recent_goals': home_recent_goals,
            'home_recent_conceded': home_recent_conceded,
            'home_hist_goals': home_hist_goals,
            'home_hist_conceded': home_hist_conceded,
            'away_recent_goals': away_recent_goals,
            'away_recent_conceded': away_recent_conceded,
            'away_hist_goals': away_hist_goals,
            'away_hist_conceded': away_hist_conceded,
            'over_odds': over_odds,
            'under_odds': under_odds,
            'public_over': public_over,
            'home_position': home_position,
            'away_position': away_position,
            'home_points': home_points,
            'is_derby': is_derby,
            'is_relegation': is_relegation,
            'games_remaining': games_remaining,
            'h2h_over': h2h_over,
            'recent_over': recent_over
        }
        
        return match_data

# ========== DISPLAY RESULTS ==========
def display_results(prediction):
    """Display prediction results"""
    
    st.markdown("## 🎯 Prediction Result")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pred = prediction['prediction']
        if pred == 'NO_VALUE_BET':
            st.error("NO BET")
        elif pred == 'OVER_2.5':
            st.success("📈 OVER 2.5")
        else:
            st.success("📉 UNDER 2.5")
        
        st.metric("Expected Goals", f"{prediction['expected_total']:.1f}")
    
    with col2:
        st.metric("Edge", f"{prediction['edge']:.1f}%")
        st.metric("Confidence", f"{prediction['confidence']*100:.0f}%")
    
    with col3:
        st.metric("Bet Size", f"{prediction['bet_size']*100:.1f}%")
        st.write(f"**{prediction['recommendation']}**")
    
    with col4:
        st.metric("True Over Prob", f"{prediction['probabilities']['true_over']:.1%}")
        st.metric("Implied Over Prob", f"{prediction['probabilities']['implied_over']:.1%}")
    
    # Analysis sections
    if prediction['traps']:
        st.markdown("### 🚨 Detected Traps")
        for trap in prediction['traps']:
            st.warning(f"**{trap['type']}**: {trap['description']}")
    
    if prediction['pressure_scenarios']:
        st.markdown("### 📊 Pressure Context")
        for scenario in prediction['pressure_scenarios']:
            if scenario == 'DESPERATION_CHAOS':
                st.error(f"**{scenario}**: Goalless desperate team - UNPREDICTABLE")
            else:
                st.info(f"**{scenario}**")
    
    if prediction['form_conflicts']:
        st.markdown("### ⚠️ Form Conflicts")
        for conflict in prediction['form_conflicts']:
            st.warning(f"**{conflict}**")
    
    # Detailed analysis
    with st.expander("📈 View Detailed Analysis"):
        
        # Probability comparison
        probs = prediction['probabilities']
        
        fig = go.Figure(data=[
            go.Bar(name='True Probability', 
                   x=['Over 2.5', 'Under 2.5'], 
                   y=[probs['true_over'], probs['true_under']],
                   marker_color=['#10B981', '#EF4444']),
            go.Bar(name='Implied Probability', 
                   x=['Over 2.5', 'Under 2.5'],
                   y=[probs['implied_over'], probs['implied_under']],
                   marker_color=['#34D399', '#FCA5A5'])
        ])
        fig.update_layout(barmode='group', height=300, title="True vs Implied Probabilities")
        st.plotly_chart(fig, use_container_width=True)
        
        # Edge comparison
        edges = prediction['edges']
        st.metric("Over Edge", f"{edges['over_edge']:.1f}%")
        st.metric("Under Edge", f"{edges['under_edge']:.1f}%")

# ========== MAIN APP ==========
def main():
    st.markdown('<h1 class="main-header">🎯 ANTI-MANIPULATION FOOTBALL PREDICTION SYSTEM</h1>', unsafe_allow_html=True)
    st.markdown("### **Original Logic with One Critical Fix**")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ System Configuration")
        st.info("""
        **Original Logic Applied:**
        - Public Sentiment Traps
        - Form vs History Conflicts  
        - Pressure Context Analysis
        - Odds Manipulation Detection
        
        **One Critical Fix:**
        - Desperate goalless teams = UNPREDICTABLE
        - Not defensive, but chaotic
        - Reduces confidence & bet size
        """)
        
        st.warning("""
        **Key Thresholds:**
        - Over Hype Trap: Public >70%, Odds <1.65
        - Under Fear Trap: Public <30%, Odds <1.70
        - Desperation Chaos: Position ≥15, Goals <0.8
        - Minimum Edge: 2.0%
        """)
    
    # Create input form
    match_data = create_input_form()
    
    # Predict button
    if st.button("🚀 RUN PREDICTION ANALYSIS", type="primary", use_container_width=True):
        # Run prediction
        engine = FootballPredictionEngine()
        prediction = engine.predict(match_data)
        
        # Store in session state
        st.session_state.prediction = prediction
        st.session_state.match_data = match_data
        st.rerun()
    
    # Show results if available
    if 'prediction' in st.session_state:
        display_results(st.session_state.prediction)

# Run the app
if __name__ == "__main__":
    main()
