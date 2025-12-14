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
    .status-safe { color: #4CAF50; font-weight: bold; }
    .status-danger { color: #F44336; font-weight: bold; }
    .status-mid { color: #FF9800; font-weight: bold; }
    .season-early { color: #2196F3; font-weight: bold; }
    .season-mid { color: #FF9800; font-weight: bold; }
    .season-late { color: #F44336; font-weight: bold; }
    .auto-detection {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
    }
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
                'analysis': prediction_data.get('analysis', {}),
                'auto_detections': prediction_data.get('auto_detections', {})
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
    
    def auto_detect_context(self, match_data):
        """Automatically detect season phase, team safety, and edge conditions"""
        total_teams = match_data.get('total_teams', 20)
        games_played = match_data.get('games_played', 1)
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        
        # 1. Calculate season phase
        total_games_season = total_teams * 2  # Double round-robin
        season_progress = (games_played / total_games_season) * 100
        
        if season_progress <= 33.33:
            season_phase = 'early'
            is_late_season = False
        elif season_progress <= 66.66:
            season_phase = 'mid'
            is_late_season = False
        else:
            season_phase = 'late'
            is_late_season = True
        
        # 2. Calculate team safety zones
        # Top 4: Champions League/Europa
        # Safe zone: Top 70% of table
        # Danger zone: Bottom 30% (relegation battle)
        safe_cutoff = int(total_teams * 0.7)  # Top 70% safe
        danger_cutoff = total_teams - 3  # Bottom 3 always danger
        
        home_status = 'safe' if home_pos <= safe_cutoff else 'danger'
        away_status = 'safe' if away_pos <= safe_cutoff else 'danger'
        
        # Both teams safe? (for dead rubber detection)
        both_safe = home_pos < danger_cutoff and away_pos < danger_cutoff
        
        # 3. Detect top/bottom classification
        top_cutoff = 4  # Top 4 considered elite
        bottom_cutoff = total_teams - 5  # Bottom 5 considered poor
        
        home_class = 'top' if home_pos <= top_cutoff else 'mid' if home_pos <= safe_cutoff else 'bottom'
        away_class = 'top' if away_pos <= top_cutoff else 'mid' if away_pos <= safe_cutoff else 'bottom'
        
        # 4. Position gap for pattern detection
        position_gap = abs(home_pos - away_pos)
        
        return {
            'season_phase': season_phase,
            'season_progress': season_progress,
            'home_status': home_status,
            'away_status': away_status,
            'both_safe': both_safe,
            'home_class': home_class,
            'away_class': away_class,
            'position_gap': position_gap,
            'is_late_season': is_late_season,
            'safe_cutoff': safe_cutoff,
            'danger_cutoff': danger_cutoff,
            'top_cutoff': top_cutoff,
            'bottom_cutoff': bottom_cutoff
        }
    
    def analyze_match(self, match_data, manual_edges):
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        total_teams = match_data.get('total_teams', 20)
        
        # Auto-detect context first
        auto_context = self.auto_detect_context(match_data)
        
        # Use auto-detected values, override with manual only if provided
        edge_conditions = {
            'new_manager': manual_edges.get('new_manager', False),
            'is_derby': manual_edges.get('is_derby', False),
            'european_game': manual_edges.get('european_game', False),
            'late_season': auto_context['is_late_season'],  # Auto-detected!
            'both_safe': auto_context['both_safe']  # Auto-detected!
        }
        
        # Detect core pattern using auto-context
        core_pattern = self._detect_core_pattern_auto(auto_context, home_pos, away_pos, total_teams)
        
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
        }, auto_context
    
    def _detect_core_pattern(self, home_pos, away_pos, total_teams):
        """Legacy detection - keeping for backward compatibility"""
        bottom_cutoff = total_teams - 3
        top_cutoff = 4
        
        if (home_pos <= top_cutoff and away_pos >= bottom_cutoff) or (away_pos <= top_cutoff and home_pos >= bottom_cutoff):
            gap = abs(home_pos - away_pos)
            if gap > 8:
                return 'top_vs_bottom_domination'
        
        if home_pos >= bottom_cutoff and away_pos >= bottom_cutoff:
            return 'relegation_battle'
        
        if home_pos <= top_cutoff and away_pos <= top_cutoff:
            return 'top_team_battle'
        
        return 'mid_table_ambition'
    
    def _detect_core_pattern_auto(self, auto_context, home_pos, away_pos, total_teams):
        """Enhanced pattern detection using auto-context"""
        home_class = auto_context['home_class']
        away_class = auto_context['away_class']
        position_gap = auto_context['position_gap']
        both_safe = auto_context['both_safe']
        
        # Top vs Bottom patterns
        if (home_class == 'top' and away_class == 'bottom') or (away_class == 'top' and home_class == 'bottom'):
            if position_gap > 8:
                return 'top_vs_bottom_domination'
            else:
                return 'top_vs_bottom_dominance'
        
        # Both in danger zone (relegation battle)
        if home_class == 'bottom' and away_class == 'bottom':
            return 'relegation_battle'
        
        # Top team battle
        if home_class == 'top' and away_class == 'top':
            return 'top_team_battle'
        
        # Both safe mid-table
        if both_safe and home_class == 'mid' and away_class == 'mid':
            return 'mid_table_ambition'
        
        # Default - controlled mid-table clash
        return 'controlled_mid_clash'
    
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
            'european_game': False
            # late_season and both_safe are now AUTO-DETECTED
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
            'european_game': True
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
            'european_game': False
        }
    },
    'Late Season Dead Rubber': {
        'home_name': 'West Ham',
        'away_name': 'Brentford',
        'home_pos': 8,
        'away_pos': 12,
        'total_teams': 20,
        'games_played': 35,
        'home_attack': 1.6,
        'away_attack': 1.5,
        'home_defense': 1.4,
        'away_defense': 1.3,
        'home_goals5': 7,
        'away_goals5': 6,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
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
    st.markdown("### **Auto-Detection System Enabled**")
    
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
        
        for case_name, case_data in TEST_CASES.items():
            if st.button(case_name, use_container_width=True, key=f"btn_{case_name}"):
                st.session_state.test_case_data = case_data
                st.session_state.loaded_test_case = case_name
                st.rerun()
    
    # ===== MAIN INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 TEAM DATA INPUT")
    
    if st.session_state.loaded_test_case:
        st.success(f"✅ **Loaded:** {st.session_state.loaded_test_case}")
    
    current_data = st.session_state.test_case_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 HOME TEAM")
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
    col3, col4 = st.columns(2)
    
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
    
    # ===== AUTO-DETECTION DISPLAY =====
    st.markdown("### 🔍 AUTO-DETECTION SYSTEM")
    
    # Run auto-detection for display
    match_data_temp = {
        'total_teams': total_teams,
        'games_played': games_played,
        'home_pos': home_pos,
        'away_pos': away_pos
    }
    
    auto_context = st.session_state.engine.auto_detect_context(match_data_temp)
    
    col_auto1, col_auto2, col_auto3 = st.columns(3)
    
    with col_auto1:
        # Season phase
        progress = auto_context['season_progress']
        phase = auto_context['season_phase']
        phase_class = f"season-{phase}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>📅 SEASON PHASE</h4>
            <p>Progress: <span style="font-size: 1.2em;"><strong>{progress:.1f}%</strong></span></p>
            <p>Phase: <span class="{phase_class}">{phase.upper()} SEASON</span></p>
            <small>Auto-detected from games played</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto2:
        # Team safety
        home_status = auto_context['home_status']
        away_status = auto_context['away_status']
        safe_cutoff = auto_context['safe_cutoff']
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🛡️ TEAM SAFETY</h4>
            <p><strong>{home_name}:</strong> 
            <span class="status-{home_status}">{home_status.upper()}</span>
            (Position {home_pos} ≤ {safe_cutoff})</p>
            <p><strong>{away_name}:</strong> 
            <span class="status-{away_status}">{away_status.upper()}</span>
            (Position {away_pos} ≤ {safe_cutoff})</p>
            <small>Safe if position ≤ {safe_cutoff}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto3:
        # Team classification
        home_class = auto_context['home_class']
        away_class = auto_context['away_class']
        both_safe = auto_context['both_safe']
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🏆 TEAM CLASS</h4>
            <p><strong>{home_name}:</strong> {home_class.upper()}</p>
            <p><strong>{away_name}:</strong> {away_class.upper()}</p>
            <p><strong>Both Teams Safe:</strong> 
            <span class="{'status-safe' if both_safe else 'status-danger'}">
            {'✓ YES' if both_safe else '✗ NO'}
            </span></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== EDGE PATTERN CONDITIONS =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 EDGE PATTERN CONDITIONS")
    
    edge_data = current_data['edge_conditions']
    
    st.info("ℹ️ **Note:** 'Late Season' and 'Both Teams Safe' are now auto-detected based on league data above.")
    
    col_edge1, col_edge2 = st.columns(2)
    
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
        
        # Show auto-detected late season status
        is_late_season = auto_context['is_late_season']
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
            <strong>⏰ Late Season Detection:</strong>
            <p style="margin: 5px 0;">Progress: {auto_context['season_progress']:.1f}% → 
            <span class="{'season-late' if is_late_season else 'season-mid'}">
            {'LATE SEASON' if is_late_season else 'NOT LATE SEASON'}
            </span></p>
            <small>Auto-detected: Late season = >66.6% of games played</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Show auto-detected both teams safe status
    both_safe_detected = auto_context['both_safe']
    st.markdown(f"""
    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 4px solid #2196F3;">
        <strong>🛡️ Both Teams Safe Detection:</strong>
        <p style="margin: 5px 0;">
        {home_name} (pos {home_pos}) and {away_name} (pos {away_pos}) are 
        <span class="{'status-safe' if both_safe_detected else 'status-danger'}">
        {'BOTH SAFE' if both_safe_detected else 'NOT BOTH SAFE'}
        </span>
        </p>
        <small>Auto-detected: Safe = position < {auto_context['danger_cutoff']}</small>
    </div>
    """, unsafe_allow_html=True)
    
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
            
            # Manual edge conditions only
            manual_edges = {
                'new_manager': new_manager,
                'is_derby': is_derby,
                'european_game': european_game
                # late_season and both_safe are auto-detected
            }
            
            # Run analysis (auto-detection happens inside)
            analysis, auto_context = st.session_state.engine.analyze_match(match_data, manual_edges)
            
            # Save to database
            prediction_data = {
                'match_data': match_data,
                'analysis': analysis,
                'auto_detections': auto_context
            }
            
            prediction_hash = st.session_state.db.save_prediction(prediction_data)
            
            # Store in session
            st.session_state.current_prediction = {
                'analysis': analysis,
                'match_data': match_data,
                'auto_context': auto_context,
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
        auto_context = pred_data.get('auto_context', {})
        
        st.markdown("---")
        st.markdown(f"## 📊 RESULTS: {pred_data['teams']}")
        
        # Show auto-detection summary
        st.markdown("### 🔍 AUTO-DETECTION SUMMARY")
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            season_progress = auto_context.get('season_progress', 0)
            season_phase = auto_context.get('season_phase', 'mid')
            phase_class = f"season-{season_phase}"
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>📅 Season Context</h4>
                <p><strong>Progress:</strong> {season_progress:.1f}%</p>
                <p><strong>Phase:</strong> <span class="{phase_class}">{season_phase.upper()} SEASON</span></p>
                <p><strong>Games:</strong> {match_data['games_played']} / {match_data['total_teams'] * 2}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_sum2:
            home_class = auto_context.get('home_class', 'mid')
            away_class = auto_context.get('away_class', 'mid')
            both_safe = auto_context.get('both_safe', False)
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>🏆 Team Status</h4>
                <p><strong>{match_data['home_name']}:</strong> {home_class.upper()} (pos {match_data['home_pos']})</p>
                <p><strong>{match_data['away_name']}:</strong> {away_class.upper()} (pos {match_data['away_pos']})</p>
                <p><strong>Both Safe:</strong> 
                <span class="{'status-safe' if both_safe else 'status-danger'}">
                {'✓ YES' if both_safe else '✗ NO'}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
        
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
            # Auto-detection details
            st.markdown(f"""
            #### 🔍 AUTO-DETECTED CONTEXT
            
            **Season Phase:**
            - Progress: {auto_context.get('season_progress', 0):.1f}%
            - Phase: {auto_context.get('season_phase', 'mid').upper()} SEASON
            - Late Season: {'YES' if auto_context.get('is_late_season', False) else 'NO'}
            
            **Team Safety:**
            - {match_data['home_name']}: {auto_context.get('home_status', 'mid').upper()}
            - {match_data['away_name']}: {auto_context.get('away_status', 'mid').upper()}
            - Both Teams Safe: {'YES' if auto_context.get('both_safe', False) else 'NO'}
            
            **Team Classification:**
            - {match_data['home_name']}: {auto_context.get('home_class', 'mid').upper()}
            - {match_data['away_name']}: {auto_context.get('away_class', 'mid').upper()}
            - Position Gap: {auto_context.get('position_gap', 0)}
            
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
                    - Auto-detections: {auto_context.get('season_phase', 'mid').upper()} season, 
                      {match_data['home_name']} ({auto_context.get('home_class', 'mid')}), 
                      {match_data['away_name']} ({auto_context.get('away_class', 'mid')})
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to save result")

if __name__ == "__main__":
    main()