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
    .edge-high { border-left-color: #4CAF50; }
    .edge-medium { border-left-color: #FF9800; }
    .edge-low { border-left-color: #F44336; }
    .pattern-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 3px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .psychology-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px;
    }
    .profit-highlight {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    .badge-domination { background-color: #ede7f6; color: #5e35b1; }
    .badge-fear { background-color: #ffebee; color: #c62828; }
    .badge-ambition { background-color: #e8f5e9; color: #2e7d32; }
    .badge-control { background-color: #fff8e1; color: #ff8f00; }
    .badge-quality { background-color: #e3f2fd; color: #1565c0; }
    .badge-dominance { background-color: #f3e5f5; color: #6a1b9a; }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE ==========
class FootballDatabase:
    def __init__(self):
        self.predictions = []
        self.outcomes = []
        self.team_stats = {}
    
    def save_prediction(self, prediction_data):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_input = f"{prediction_data.get('match_data', {}).get('home_name', '')}_{prediction_data.get('match_data', {}).get('away_name', '')}_{timestamp}"
            prediction_hash = hashlib.md5(hash_input.encode()).hexdigest()
            
            prediction_record = {
                'hash': prediction_hash,
                'timestamp': datetime.now(),
                'match_data': prediction_data.get('match_data', {}),
                'analysis': prediction_data.get('analysis', {})
            }
            
            self.predictions.append(prediction_record)
            
            return prediction_hash
        except Exception:
            return f"pred_{len(self.predictions)}"
    
    def record_outcome(self, prediction_hash, actual_home, actual_away, notes=""):
        try:
            prediction = None
            for pred in self.predictions:
                if pred.get('hash') == prediction_hash:
                    prediction = pred
                    break
            
            if not prediction:
                return False
            
            actual_total = actual_home + actual_away
            actual_over_under = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
            predicted_over_under = prediction['analysis'].get('prediction', '')
            outcome_accuracy = "CORRECT" if predicted_over_under == actual_over_under else "INCORRECT"
            
            outcome_record = {
                'prediction_hash': prediction_hash,
                'actual_home': actual_home,
                'actual_away': actual_away,
                'actual_total': actual_total,
                'actual_over_under': actual_over_under,
                'outcome_accuracy': outcome_accuracy,
                'notes': notes,
                'recorded_at': datetime.now()
            }
            
            self.outcomes.append(outcome_record)
            return True
        except Exception:
            return False
    
    def get_performance_stats(self):
        total = len(self.outcomes)
        correct = len([o for o in self.outcomes if o.get('outcome_accuracy') == "CORRECT"])
        accuracy = correct / total if total > 0 else 0
        return {'total': total, 'correct': correct, 'accuracy': accuracy}

# ========== ULTIMATE PREDICTION ENGINE ==========
class UltimatePredictionEngine:
    def __init__(self):
        self.learned_patterns = {
            'top_vs_bottom_domination': {
                'base_multiplier': 1.05,
                'description': 'Top team good form vs bottom team → 2-1 type scores',
                'psychology': 'DOMINATION',
                'badge': 'badge-domination',
            },
            'relegation_battle': {
                'base_multiplier': 0.65,
                'description': 'Both fighting relegation → defensive football',
                'psychology': 'FEAR',
                'badge': 'badge-fear',
            },
            'mid_table_ambition': {
                'base_multiplier': 1.15,
                'description': 'Both safe mid-table → attacking football',
                'psychology': 'AMBITION',
                'badge': 'badge-ambition',
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.90,
                'description': 'Mid-table with form difference → controlled game',
                'psychology': 'CONTROL',
                'badge': 'badge-control',
            },
            'top_team_battle': {
                'base_multiplier': 0.95,
                'description': 'Top teams facing → quality creates and prevents goals',
                'psychology': 'QUALITY',
                'badge': 'badge-quality',
            },
            'top_vs_bottom_dominance': {
                'base_multiplier': 0.85,
                'description': 'Top team excellent form vs very poor bottom → 1-0 type',
                'psychology': 'DOMINANCE',
                'badge': 'badge-dominance',
            }
        }
        
        self.edge_patterns = {
            'new_manager_bounce': {
                'multiplier': 1.25,
                'edge_value': 0.20,
                'description': 'Players desperate to impress new manager',
                'bet_type': 'HOME_WIN'
            },
            'derby_fear': {
                'multiplier': 0.60,
                'edge_value': 0.30,
                'description': 'Fear of losing derby > desire to win',
                'bet_type': 'UNDER_2_0'
            },
            'european_hangover': {
                'multiplier': 0.75,
                'edge_value': 0.28,
                'description': 'Physical/mental exhaustion from European travel',
                'bet_type': 'OPPONENT_DOUBLE_CHANCE'
            },
            'dead_rubber': {
                'multiplier': 1.30,
                'edge_value': 0.25,
                'description': 'Beach football mentality, relaxed play',
                'bet_type': 'OVER_2_5'
            }
        }
        
        self.thresholds = {
            'relegation_battle': {'over': 2.3, 'under': 2.7},
            'top_vs_bottom_domination': {'over': 2.6, 'under': 2.4},
            'dead_rubber': {'over': 2.4, 'under': 2.6},
            'derby_fear': {'over': 2.8, 'under': 2.2},
            'default': {'over': 2.7, 'under': 2.3}
        }
    
    def analyze_match(self, match_data, edge_conditions):
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        total_teams = match_data.get('total_teams', 20)
        
        # Detect core pattern
        core_pattern = self._detect_core_pattern(home_pos, away_pos, total_teams)
        
        # Detect edge patterns
        edge_patterns = []
        if edge_conditions.get('new_manager'):
            edge_patterns.append(self.edge_patterns['new_manager_bounce'])
        if edge_conditions.get('is_derby'):
            edge_patterns.append(self.edge_patterns['derby_fear'])
        if edge_conditions.get('european_game'):
            edge_patterns.append(self.edge_patterns['european_hangover'])
        if edge_conditions.get('late_season') and edge_conditions.get('both_safe'):
            edge_patterns.append(self.edge_patterns['dead_rubber'])
        
        # Calculate xG
        base_xg = self._calculate_base_xg(match_data)
        
        # Apply multipliers
        total_multiplier = self.learned_patterns[core_pattern]['base_multiplier']
        edge_value = 0
        
        for edge in edge_patterns:
            total_multiplier *= edge['multiplier']
            edge_value += edge['edge_value']
        
        enhanced_xg = base_xg * total_multiplier
        
        # Make prediction
        thresholds = self.thresholds.get(core_pattern, self.thresholds['default'])
        
        if enhanced_xg > thresholds['over']:
            prediction = 'OVER 2.5'
            confidence = 'HIGH' if enhanced_xg > 3.0 else 'MEDIUM'
        elif enhanced_xg < thresholds['under']:
            prediction = 'UNDER 2.5'
            confidence = 'HIGH' if enhanced_xg < 2.0 else 'MEDIUM'
        else:
            prediction = 'OVER 2.5' if enhanced_xg > 2.5 else 'UNDER 2.5'
            confidence = 'MEDIUM'
        
        # Boost confidence if edge patterns present
        if edge_value > 0.20:
            confidence = 'VERY HIGH'
        elif edge_value > 0.10:
            confidence = 'HIGH'
        
        # Stake recommendation
        if confidence == 'VERY HIGH' and edge_value > 0.25:
            stake = 'MAX BET (3x) 🔥'
        elif confidence == 'HIGH' and edge_value > 0.15:
            stake = 'HEAVY BET (2x) ⚡'
        elif edge_value > 0.10:
            stake = 'NORMAL BET (1x) ✅'
        else:
            stake = 'SMALL BET (0.5x) ⚖️'
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'base_xg': round(base_xg, 2),
            'enhanced_xg': round(enhanced_xg, 2),
            'total_multiplier': round(total_multiplier, 2),
            'core_pattern': core_pattern,
            'edge_patterns': edge_patterns,
            'total_edge_value': round(edge_value, 3),
            'stake_recommendation': stake,
            'thresholds_used': thresholds,
            'psychology': self.learned_patterns[core_pattern]['psychology'],
            'badge': self.learned_patterns[core_pattern]['badge']
        }
    
    def _detect_core_pattern(self, home_pos, away_pos, total_teams):
        bottom_cutoff = total_teams - 3
        top_cutoff = 4
        
        # Top vs Bottom patterns
        if (home_pos <= top_cutoff and away_pos >= bottom_cutoff) or (away_pos <= top_cutoff and home_pos >= bottom_cutoff):
            gap = abs(home_pos - away_pos)
            if gap > 8:
                return 'top_vs_bottom_domination'
        
        # Relegation battle
        if home_pos >= bottom_cutoff and away_pos >= bottom_cutoff:
            return 'relegation_battle'
        
        # Top team battle
        if home_pos <= top_cutoff and away_pos <= top_cutoff:
            return 'top_team_battle'
        
        return 'mid_table_ambition'
    
    def _calculate_base_xg(self, match_data):
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        home_xg = (home_attack + away_defense) / 2
        away_xg = (away_attack + home_defense) / 2
        
        return home_xg + away_xg

# ========== TEST CASES ==========
TEST_CASES = {
    'Atletico Madrid vs Valencia': {
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
        }
    },
    'Liverpool vs Burnley': {
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
        }
    },
    'Manchester Derby': {
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
        }
    }
}

# ========== INITIALIZE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = UltimatePredictionEngine()

if 'db' not in st.session_state:
    st.session_state.db = FootballDatabase()

# Initialize session state for test case loading
if 'loaded_test_case' not in st.session_state:
    st.session_state.loaded_test_case = None
if 'test_case_data' not in st.session_state:
    st.session_state.test_case_data = TEST_CASES['Atletico Madrid vs Valencia']

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">👑 ULTIMATE FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Test Case Loading Enabled**")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## 📊 Performance Dashboard")
        
        perf_stats = st.session_state.db.get_performance_stats()
        
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.metric("Total Predictions", perf_stats['total'])
        with col_sb2:
            accuracy = f"{perf_stats['accuracy']*100:.1f}%" if perf_stats['total'] > 0 else "N/A"
            st.metric("Accuracy", accuracy)
        
        st.markdown("### 🧪 Quick Test Cases")
        st.markdown("*Click to load team names and data*")
        
        # Test case buttons - FIXED to load data immediately
        for case_name, case_data in TEST_CASES.items():
            if st.button(case_name, use_container_width=True, key=f"btn_{case_name}"):
                # Store the test case data in session state
                st.session_state.test_case_data = case_data
                st.session_state.loaded_test_case = case_name
                st.rerun()
    
    # ===== MAIN INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 TEAM DATA INPUT")
    
    # Show which test case is loaded
    if st.session_state.loaded_test_case:
        st.success(f"✅ **Loaded:** {st.session_state.loaded_test_case}")
    
    # Get current data (either from test case or previous input)
    current_data = st.session_state.test_case_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 HOME TEAM")
        # Load team name from test case if available
        home_name = st.text_input("Team Name", 
                                 value=current_data['home_name'],
                                 key="home_name_input")
        
        home_pos = st.number_input("League Position (1 = Best)", 
                                  min_value=1, max_value=40,
                                  value=current_data['home_pos'],
                                  key="home_pos_input")
        
        home_attack = st.number_input("Attack: Goals per Game", 
                                     min_value=0.0, max_value=5.0, step=0.1,
                                     value=current_data['home_attack'],
                                     key="home_attack_input")
        
        home_defense = st.number_input("Defense: Conceded per Game", 
                                      min_value=0.0, max_value=5.0, step=0.1,
                                      value=current_data['home_defense'],
                                      key="home_defense_input")
        
        home_goals5 = st.number_input("Goals in Last 5 Games", 
                                     min_value=0, max_value=30,
                                     value=current_data['home_goals5'],
                                     key="home_goals5_input")
    
    with col2:
        st.markdown("#### ✈️ AWAY TEAM")
        # Load team name from test case if available
        away_name = st.text_input("Team Name", 
                                 value=current_data['away_name'],
                                 key="away_name_input")
        
        away_pos = st.number_input("League Position (1 = Best)", 
                                  min_value=1, max_value=40,
                                  value=current_data['away_pos'],
                                  key="away_pos_input")
        
        away_attack = st.number_input("Attack: Goals per Game", 
                                     min_value=0.0, max_value=5.0, step=0.1,
                                     value=current_data['away_attack'],
                                     key="away_attack_input")
        
        away_defense = st.number_input("Defense: Conceded per Game", 
                                      min_value=0.0, max_value=5.0, step=0.1,
                                      value=current_data['away_defense'],
                                      key="away_defense_input")
        
        away_goals5 = st.number_input("Goals in Last 5 Games", 
                                     min_value=0, max_value=30,
                                     value=current_data['away_goals5'],
                                     key="away_goals5_input")
    
    # League settings
    st.markdown("#### ⚙️ LEAGUE SETTINGS")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        total_teams = st.number_input("Total Teams in League", 
                                     min_value=10, max_value=40,
                                     value=current_data['total_teams'],
                                     key="total_teams_input")
    
    with col4:
        games_played = st.number_input("Games Played This Season", 
                                      min_value=1, max_value=50,
                                      value=current_data['games_played'],
                                      key="games_played_input")
    
    with col5:
        season_progress = (games_played / (total_teams * 2)) * 100
        st.metric("Season Progress", f"{season_progress:.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== EDGE PATTERN CONDITIONS =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 EDGE PATTERN CONDITIONS")
    
    # Load edge conditions from test case
    edge_data = current_data['edge_conditions']
    
    col_edge1, col_edge2, col_edge3 = st.columns(3)
    
    with col_edge1:
        new_manager = st.checkbox("New Manager Effect", 
                                 value=edge_data['new_manager'],
                                 key="new_manager_input")
        
        is_derby = st.checkbox("Local Derby Match", 
                              value=edge_data['is_derby'],
                              key="is_derby_input")
    
    with col_edge2:
        european_game = st.checkbox("European Game Midweek", 
                                   value=edge_data['european_game'],
                                   key="european_game_input")
        
        late_season = st.checkbox("Late Season Match", 
                                 value=edge_data['late_season'],
                                 key="late_season_input")
    
    with col_edge3:
        # Calculate if both teams are safe
        bottom_cutoff = total_teams - 3
        both_safe = home_pos < bottom_cutoff and away_pos < bottom_cutoff
        both_safe_box = st.checkbox("Both Teams Safe", 
                                   value=both_safe,
                                   key="both_safe_input")
        
        st.caption(f"Teams safe if position < {bottom_cutoff}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYZE BUTTON =====
    if st.button("🚀 RUN ULTIMATE ANALYSIS", type="primary", use_container_width=True):
        try:
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
            
            # Prepare edge conditions
            edge_conditions = {
                'new_manager': new_manager,
                'is_derby': is_derby,
                'european_game': european_game,
                'late_season': late_season,
                'both_safe': both_safe
            }
            
            # Run analysis
            analysis = st.session_state.engine.analyze_match(match_data, edge_conditions)
            
            # Save to database
            prediction_data = {
                'match_data': match_data,
                'analysis': analysis
            }
            
            prediction_hash = st.session_state.db.save_prediction(prediction_data)
            
            # Store in session
            st.session_state.current_prediction = {
                'analysis': analysis,
                'match_data': match_data,
                'edge_conditions': edge_conditions,
                'prediction_hash': prediction_hash,
                'teams': f"{home_name} vs {away_name}"
            }
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
    
    # ===== RESULTS DISPLAY =====
    if 'current_prediction' in st.session_state:
        pred_data = st.session_state.current_prediction
        analysis = pred_data['analysis']
        match_data = pred_data['match_data']
        
        st.markdown("---")
        st.markdown(f"## 📊 RESULTS: {pred_data['teams']}")
        
        # Team info cards
        col_team1, col_team2 = st.columns(2)
        
        with col_team1:
            st.markdown(f"""
            <div class="team-card">
                <h3>🏠 {match_data['home_name']}</h3>
                <p><strong>Position:</strong> {match_data['home_pos']}</p>
                <p><strong>Attack:</strong> {match_data['home_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['home_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['home_goals5']} goals in last 5</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_team2:
            st.markdown(f"""
            <div class="team-card">
                <h3>✈️ {match_data['away_name']}</h3>
                <p><strong>Position:</strong> {match_data['away_pos']}</p>
                <p><strong>Attack:</strong> {match_data['away_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['away_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['away_goals5']} goals in last 5</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key prediction metrics
        st.markdown("### 🎯 PREDICTION SUMMARY")
        
        col_metrics = st.columns(4)
        
        with col_metrics[0]:
            st.metric("Prediction", analysis['prediction'])
        with col_metrics[1]:
            st.metric("Confidence", analysis['confidence'])
        with col_metrics[2]:
            st.metric("Expected Goals", analysis['enhanced_xg'])
        with col_metrics[3]:
            st.metric("Recommended Stake", analysis['stake_recommendation'])
        
        # Psychology badge
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <span class="psychology-badge {analysis['badge']}">
                {analysis['psychology']} PSYCHOLOGY
            </span>
            <small style="margin-left: 15px; color: #666;">
                Core Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # Edge patterns detected
        if analysis['edge_patterns']:
            st.markdown("### ⚡ EDGE PATTERNS DETECTED")
            
            for edge in analysis['edge_patterns']:
                edge_value = edge['edge_value']
                if edge_value > 0.25:
                    edge_class = "edge-high"
                elif edge_value > 0.15:
                    edge_class = "edge-medium"
                else:
                    edge_class = "edge-low"
                
                st.markdown(f"""
                <div class="edge-card {edge_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{edge['description']}</strong>
                            <span class="pattern-badge">+{edge_value*100:.0f}% EDGE</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Bet Type: {edge['bet_type'].replace('_', ' ')}
                        </div>
                    </div>
                    <p style="margin: 10px 0 5px 0;">Multiplier: ×{edge['multiplier']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # xG visualization
        st.markdown("### 📈 EXPECTED GOALS BREAKDOWN")
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            fig = go.Figure()
            
            stages = ['Base xG', 'Pattern Adjustments', 'Final xG']
            values = [
                analysis['base_xg'],
                analysis['base_xg'] * analysis['total_multiplier'],
                analysis['enhanced_xg']
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
                title="xG Calculation Process"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_viz2:
            st.markdown(f"""
            #### 🧮 CALCULATION DETAILS
            
            **Base Statistical Model:**
            - Home Attack + Away Defense: ({match_data['home_attack']} + {match_data['away_defense']}) / 2
            - Away Attack + Home Defense: ({match_data['away_attack']} + {match_data['home_defense']}) / 2
            - **Total Base xG:** {analysis['base_xg']:.2f}
            
            **Pattern Adjustments:**
            - Core Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
            - Multiplier: ×{analysis['total_multiplier']:.2f}
            - Edge Value: +{analysis['total_edge_value']*100:.1f}%
            
            **Decision Thresholds:**
            - OVER if > {analysis['thresholds_used']['over']}
            - UNDER if < {analysis['thresholds_used']['under']}
            
            **Final Calculation:**
            - {analysis['base_xg']:.2f} × {analysis['total_multiplier']:.2f} = **{analysis['enhanced_xg']:.2f}**
            - Prediction: **{analysis['prediction']}**
            """)
        
        # Profit simulation
        st.markdown('<div class="profit-highlight">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 💰 PROFIT POTENTIAL
        
        **Match:** {match_data['home_name']} vs {match_data['away_name']}
        **Prediction:** {analysis['prediction']} ({analysis['confidence']} confidence)
        **Edge Value:** +{analysis['total_edge_value']*100:.1f}%
        **Stake:** {analysis['stake_recommendation']}
        
        *Assuming standard stake = $100:*
        - Expected value per bet: **+${100 * analysis['total_edge_value']:.2f}**
        - Weekly (5 bets): **+${100 * 5 * analysis['total_edge_value']:.0f}**
        - Monthly (20 bets): **+${100 * 20 * analysis['total_edge_value']:.0f}**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Outcome recording
        st.markdown("---")
        st.markdown("### 📝 RECORD ACTUAL OUTCOME")
        
        col_out1, col_out2, col_out3 = st.columns(3)
        
        with col_out1:
            actual_home = st.number_input(f"{match_data['home_name']} Goals", 
                                        0, 10, 0, key="actual_home_input")
        
        with col_out2:
            actual_away = st.number_input(f"{match_data['away_name']} Goals", 
                                        0, 10, 0, key="actual_away_input")
        
        with col_out3:
            notes = st.text_input("Match Notes", key="outcome_notes_input")
        
        if st.button("✅ SAVE ACTUAL RESULT", type="secondary", key="save_result_btn"):
            if actual_home == 0 and actual_away == 0:
                st.warning("Please enter actual scores (at least one goal)")
            else:
                success = st.session_state.db.record_outcome(
                    pred_data['prediction_hash'],
                    actual_home,
                    actual_away,
                    notes
                )
                
                if success:
                    st.success("Result saved! System learning updated.")
                    
                    # Show learning feedback
                    actual_total = actual_home + actual_away
                    predicted = analysis['prediction']
                    actual_type = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
                    is_correct = predicted == actual_type
                    
                    st.info(f"""
                    **Learning Update:**
                    - Predicted: **{predicted}**
                    - Actual: **{actual_type}** ({actual_home}-{actual_away})
                    - Result: **{'✅ CORRECT' if is_correct else '❌ INCORRECT'}**
                    - Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to save result")

if __name__ == "__main__":
    main()