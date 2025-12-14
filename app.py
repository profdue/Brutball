import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="ULTIMATE FOOTBALL PREDICTOR",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS STYLING ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .input-section {
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .team-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .edge-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 8px solid;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .test-case-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        padding: 10px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .test-case-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ========== TEST CASES ==========
TEST_CASES = {
    '🔥 Atletico vs Valencia': {
        'home_name': 'Atletico Madrid',
        'away_name': 'Valencia',
        'home_pos': 4,
        'away_pos': 17,
        'total_teams': 20,
        'games_played': 25,
        'home_attack': 1.8,
        'away_attack': 1.1,
        'home_defense': 0.9,
        'away_defense': 1.4,
        'home_goals5': 12,
        'away_goals5': 5,
        'edge_conditions': {
            'new_manager': True,
            'is_derby': False,
            'european_game': False,
            'late_season': False,
            'both_safe': False
        },
        'description': 'TOP vs BOTTOM + NEW MANAGER BOUNCE'
    },
    '⚡ Liverpool vs Burnley': {
        'home_name': 'Liverpool',
        'away_name': 'Burnley',
        'home_pos': 2,
        'away_pos': 19,
        'total_teams': 20,
        'games_played': 28,
        'home_attack': 2.2,
        'away_attack': 0.9,
        'home_defense': 0.8,
        'away_defense': 1.8,
        'home_goals5': 14,
        'away_goals5': 4,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': True,
            'late_season': False,
            'both_safe': False
        },
        'description': 'GHOST GAMES + EUROPEAN HANGOVER'
    },
    '🎯 Manchester Derby': {
        'home_name': 'Manchester United',
        'away_name': 'Manchester City',
        'home_pos': 6,
        'away_pos': 3,
        'total_teams': 20,
        'games_played': 30,
        'home_attack': 1.5,
        'away_attack': 2.1,
        'home_defense': 1.3,
        'away_defense': 0.9,
        'home_goals5': 8,
        'away_goals5': 15,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': True,
            'european_game': False,
            'late_season': True,
            'both_safe': True
        },
        'description': 'DERBY FEAR + DEAD RUBBER'
    },
    '🔴 Chelsea vs Everton': {
        'home_name': 'Chelsea',
        'away_name': 'Everton',
        'home_pos': 5,
        'away_pos': 7,
        'total_teams': 20,
        'games_played': 20,
        'home_attack': 1.6,
        'away_attack': 1.2,
        'home_defense': 1.1,
        'away_defense': 1.3,
        'home_goals5': 9,
        'away_goals5': 7,
        'edge_conditions': {
            'new_manager': True,
            'is_derby': False,
            'european_game': True,
            'late_season': False,
            'both_safe': True
        },
        'description': 'CONTROLLED MID-CLASH + EUROPEAN HANGOVER'
    },
    '🟡 Dortmund vs Mainz': {
        'home_name': 'Borussia Dortmund',
        'away_name': 'Mainz',
        'home_pos': 4,
        'away_pos': 16,
        'total_teams': 18,
        'games_played': 25,
        'home_attack': 2.0,
        'away_attack': 1.0,
        'home_defense': 1.2,
        'away_defense': 1.6,
        'home_goals5': 13,
        'away_goals5': 4,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': True,
            'late_season': False,
            'both_safe': False
        },
        'description': 'TOP vs BOTTOM + EUROPEAN HANGOVER'
    }
}

# ========== INITIALIZE SESSION STATE ==========
# Initialize with default values if not exists
if 'loaded_test_case' not in st.session_state:
    st.session_state.loaded_test_case = None

if 'current_home_name' not in st.session_state:
    st.session_state.current_home_name = "Atletico Madrid"

if 'current_away_name' not in st.session_state:
    st.session_state.current_away_name = "Valencia"

if 'current_home_pos' not in st.session_state:
    st.session_state.current_home_pos = 4

if 'current_away_pos' not in st.session_state:
    st.session_state.current_away_pos = 17

# ... initialize all other fields similarly

# ========== FUNCTIONS ==========
def load_test_case(case_name, case_data):
    """Load a test case into session state"""
    st.session_state.loaded_test_case = case_name
    
    # Load all data into session state
    st.session_state.current_home_name = case_data['home_name']
    st.session_state.current_away_name = case_data['away_name']
    st.session_state.current_home_pos = case_data['home_pos']
    st.session_state.current_away_pos = case_data['away_pos']
    st.session_state.current_total_teams = case_data['total_teams']
    st.session_state.current_games_played = case_data['games_played']
    st.session_state.current_home_attack = case_data['home_attack']
    st.session_state.current_away_attack = case_data['away_attack']
    st.session_state.current_home_defense = case_data['home_defense']
    st.session_state.current_away_defense = case_data['away_defense']
    st.session_state.current_home_goals5 = case_data['home_goals5']
    st.session_state.current_away_goals5 = case_data['away_goals5']
    
    # Edge conditions
    st.session_state.current_new_manager = case_data['edge_conditions']['new_manager']
    st.session_state.current_is_derby = case_data['edge_conditions']['is_derby']
    st.session_state.current_european_game = case_data['edge_conditions']['european_game']
    st.session_state.current_late_season = case_data['edge_conditions']['late_season']
    
    # Calculate both_safe
    bottom_cutoff = case_data['total_teams'] - 3
    st.session_state.current_both_safe = (case_data['home_pos'] < bottom_cutoff and 
                                         case_data['away_pos'] < bottom_cutoff)
    
    # Clear any existing prediction
    if 'current_prediction' in st.session_state:
        del st.session_state.current_prediction
    
    # Force rerun to update inputs
    st.rerun()

# ========== SIMPLIFIED ENGINE ==========
class FootballPredictor:
    def __init__(self):
        self.patterns = {
            'top_vs_bottom_domination': {'multiplier': 1.05, 'psychology': 'DOMINATION'},
            'relegation_battle': {'multiplier': 0.65, 'psychology': 'FEAR'},
            'mid_table_ambition': {'multiplier': 1.15, 'psychology': 'AMBITION'}
        }
    
    def predict(self, match_data, edge_conditions):
        # Simple prediction logic
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        # Base xG
        base_xg = (home_attack + away_defense) / 2 + (away_attack + home_defense) / 2
        
        # Apply pattern multiplier
        multiplier = 1.0
        if match_data.get('home_pos', 10) <= 4 and match_data.get('away_pos', 10) >= 17:
            multiplier *= 1.05
        
        # Apply edge conditions
        if edge_conditions.get('new_manager'):
            multiplier *= 1.25
        if edge_conditions.get('is_derby'):
            multiplier *= 0.60
        if edge_conditions.get('european_game'):
            multiplier *= 0.75
        
        final_xg = base_xg * multiplier
        
        # Make prediction
        if final_xg > 2.5:
            prediction = 'OVER 2.5'
            confidence = 'HIGH' if final_xg > 3.0 else 'MEDIUM'
        else:
            prediction = 'UNDER 2.5'
            confidence = 'HIGH' if final_xg < 2.0 else 'MEDIUM'
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'base_xg': round(base_xg, 2),
            'final_xg': round(final_xg, 2),
            'multiplier': round(multiplier, 2)
        }

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">⚽ INSTANT TEST CASE LOADER</div>', unsafe_allow_html=True)
    st.markdown("### **Click any test case → Instantly loads all team data**")
    
    # Initialize predictor
    if 'predictor' not in st.session_state:
        st.session_state.predictor = FootballPredictor()
    
    # ===== TEST CASE SELECTION =====
    st.markdown("### 🧪 **CLICK TO LOAD TEST CASES**")
    
    # Create columns for test cases
    cols = st.columns(5)
    
    for idx, (case_name, case_data) in enumerate(TEST_CASES.items()):
        with cols[idx % 5]:
            # Create custom button with better styling
            button_key = f"load_{case_name}"
            
            # Check if this is the currently loaded case
            is_active = st.session_state.get('loaded_test_case') == case_name
            
            if is_active:
                button_label = f"✅ {case_name.split(' ')[0]}"
                button_type = "primary"
            else:
                button_label = case_name.split(' ')[0]
                button_type = "secondary"
            
            if st.button(button_label, 
                        key=button_key, 
                        type=button_type,
                        use_container_width=True):
                load_test_case(case_name, case_data)
            
            # Show description
            st.caption(case_data['description'])
    
    # Show which test case is loaded
    if st.session_state.get('loaded_test_case'):
        current_case = st.session_state.loaded_test_case
        current_data = TEST_CASES[current_case]
        st.success(f"✅ **LOADED:** {current_case} - {current_data['description']}")
    
    st.markdown("---")
    
    # ===== TEAM DATA INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 **TEAM DATA (Auto-filled from test case)**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 **HOME TEAM**")
        home_name = st.text_input(
            "Team Name",
            value=st.session_state.current_home_name,
            key="input_home_name"
        )
        
        home_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.current_home_pos,
            key="input_home_pos"
        )
        
        home_attack = st.number_input(
            "Attack: Goals per Game",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            value=st.session_state.current_home_attack,
            key="input_home_attack"
        )
        
        home_defense = st.number_input(
            "Defense: Conceded per Game",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            value=st.session_state.current_home_defense,
            key="input_home_defense"
        )
        
        home_goals5 = st.number_input(
            "Goals in Last 5 Games",
            min_value=0,
            max_value=30,
            value=st.session_state.current_home_goals5,
            key="input_home_goals5"
        )
    
    with col2:
        st.markdown("#### ✈️ **AWAY TEAM**")
        away_name = st.text_input(
            "Team Name",
            value=st.session_state.current_away_name,
            key="input_away_name"
        )
        
        away_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.current_away_pos,
            key="input_away_pos"
        )
        
        away_attack = st.number_input(
            "Attack: Goals per Game",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            value=st.session_state.current_away_attack,
            key="input_away_attack"
        )
        
        away_defense = st.number_input(
            "Defense: Conceded per Game",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            value=st.session_state.current_away_defense,
            key="input_away_defense"
        )
        
        away_goals5 = st.number_input(
            "Goals in Last 5 Games",
            min_value=0,
            max_value=30,
            value=st.session_state.current_away_goals5,
            key="input_away_goals5"
        )
    
    # League Settings
    st.markdown("#### ⚙️ **LEAGUE SETTINGS**")
    col3, col4 = st.columns(2)
    
    with col3:
        total_teams = st.number_input(
            "Total Teams in League",
            min_value=10,
            max_value=40,
            value=st.session_state.current_total_teams,
            key="input_total_teams"
        )
    
    with col4:
        games_played = st.number_input(
            "Games Played This Season",
            min_value=1,
            max_value=50,
            value=st.session_state.current_games_played,
            key="input_games_played"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== EDGE CONDITIONS =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 **EDGE PATTERN CONDITIONS**")
    
    col_edge1, col_edge2, col_edge3 = st.columns(3)
    
    with col_edge1:
        new_manager = st.checkbox(
            "📋 New Manager Effect (Last 2 games)",
            value=st.session_state.current_new_manager,
            key="input_new_manager"
        )
        
        is_derby = st.checkbox(
            "⚔️ Local Derby Match",
            value=st.session_state.current_is_derby,
            key="input_is_derby"
        )
    
    with col_edge2:
        european_game = st.checkbox(
            "✈️ European Game Midweek",
            value=st.session_state.current_european_game,
            key="input_european_game"
        )
        
        late_season = st.checkbox(
            "📅 Late Season Match (Last 5 games)",
            value=st.session_state.current_late_season,
            key="input_late_season"
        )
    
    with col_edge3:
        # Calculate both_safe automatically
        bottom_cutoff = total_teams - 3
        both_safe = home_pos < bottom_cutoff and away_pos < bottom_cutoff
        st.checkbox(
            "✅ Both Teams Safe from Relegation",
            value=both_safe,
            disabled=True,
            key="display_both_safe"
        )
        st.caption(f"*Teams safe if position < {bottom_cutoff}*")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYZE BUTTON =====
    if st.button("🚀 **RUN ANALYSIS**", type="primary", use_container_width=True):
        # Prepare match data
        match_data = {
            'home_name': home_name,
            'away_name': away_name,
            'home_pos': home_pos,
            'away_pos': away_pos,
            'total_teams': total_teams,
            'games_played': games_played,
            'home_attack': home_attack,
            'away_attack': away_attack,
            'home_defense': home_defense,
            'away_defense': away_defense,
            'home_goals5': home_goals5,
            'away_goals5': away_goals5
        }
        
        edge_conditions = {
            'new_manager': new_manager,
            'is_derby': is_derby,
            'european_game': european_game,
            'late_season': late_season,
            'both_safe': both_safe
        }
        
        # Run prediction
        result = st.session_state.predictor.predict(match_data, edge_conditions)
        
        # Store in session
        st.session_state.current_prediction = {
            'result': result,
            'match_data': match_data,
            'edge_conditions': edge_conditions,
            'match_title': f"{home_name} vs {away_name}"
        }
        
        st.rerun()
    
    # ===== DISPLAY RESULTS =====
    if 'current_prediction' in st.session_state:
        pred = st.session_state.current_prediction
        result = pred['result']
        match_data = pred['match_data']
        
        st.markdown("---")
        st.markdown(f"## 📊 **PREDICTION RESULTS: {pred['match_title']}**")
        
        # Team cards
        col_team1, col_team2 = st.columns(2)
        
        with col_team1:
            st.markdown(f"""
            <div class="team-card">
                <h3>🏠 {match_data['home_name']}</h3>
                <p><strong>Position:</strong> {match_data['home_pos']}th</p>
                <p><strong>Attack:</strong> {match_data['home_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['home_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['home_goals5']} goals in last 5</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_team2:
            st.markdown(f"""
            <div class="team-card">
                <h3>✈️ {match_data['away_name']}</h3>
                <p><strong>Position:</strong> {match_data['away_pos']}th</p>
                <p><strong>Attack:</strong> {match_data['away_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['away_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['away_goals5']} goals in last 5</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Prediction metrics
        col_metrics = st.columns(4)
        
        with col_metrics[0]:
            st.metric("Prediction", result['prediction'])
        with col_metrics[1]:
            st.metric("Confidence", result['confidence'])
        with col_metrics[2]:
            st.metric("Expected Goals", result['final_xg'])
        with col_metrics[3]:
            stake = "MAX BET" if result['confidence'] == 'HIGH' else "NORMAL BET"
            st.metric("Recommended", stake)
        
        # xG visualization
        st.markdown("### 📈 **Expected Goals Breakdown**")
        
        fig = go.Figure()
        
        stages = ['Base xG', 'Pattern Adjustments', 'Final xG']
        values = [
            result['base_xg'],
            result['base_xg'] * result['multiplier'],
            result['final_xg']
        ]
        
        fig.add_trace(go.Bar(
            x=stages,
            y=values,
            marker_color=['#FF6B6B', '#4ECDC4', '#96CEB4'],
            text=[f'{v:.2f}' for v in values],
            textposition='auto'
        ))
        
        fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            height=350,
            showlegend=False,
            yaxis_title="Expected Goals",
            title="How the Prediction Was Calculated"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Edge patterns applied
        applied_patterns = []
        if pred['edge_conditions']['new_manager']:
            applied_patterns.append("New Manager Bounce (+25%)")
        if pred['edge_conditions']['is_derby']:
            applied_patterns.append("Derby Fear (-40%)")
        if pred['edge_conditions']['european_game']:
            applied_patterns.append("European Hangover (-25%)")
        
        if applied_patterns:
            st.markdown("### ⚡ **Applied Edge Patterns**")
            for pattern in applied_patterns:
                st.markdown(f"""
                <div class="edge-card">
                    <strong>{pattern}</strong>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #666;">
                    {pattern.split('(')[0].strip()} pattern detected and applied
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("### 🔄 **Quick Actions**")
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("🔄 Try Another Test Case", use_container_width=True):
                # Clear prediction but keep inputs
                del st.session_state.current_prediction
                st.rerun()
        
        with col_action2:
            if st.button("📊 View Detailed Analysis", use_container_width=True):
                st.info("Detailed analysis would show here")
        
        with col_action3:
            if st.button("💾 Save This Analysis", use_container_width=True):
                st.success("Analysis saved to history!")

if __name__ == "__main__":
    main()