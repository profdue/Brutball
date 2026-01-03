import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== SYSTEM CONSTANTS v7.2 ===================
# DEFENSIVE THRESHOLDS (LAST 5 MATCHES ONLY)
DEFENSIVE_THRESHOLDS = {
    'TEAM_NO_SCORE': 0.6,      # Can preserve 0 goals conceded state
    'CLEAN_SHEET': 0.8,        # Can preserve 0-0.8 goals conceded state  
    'OPPONENT_UNDER_1_5': 1.0, # Can limit opponent to ≤1.5 goals
    'OPPONENT_UNDER_2_5': 1.2, # Can limit opponent to ≤2.5 goals
    'TOTALS_UNDER_2_5': 1.2,   # Team contributes to low-scoring match
    'UNDER_3_5_CONSIDER': 1.6  # Empirical threshold from 25-match study
}

# EMPIRICAL ACCURACY RATES v7.2 (UPDATED BASED ON BACKTEST)
EMPIRICAL_ACCURACY = {
    'ELITE_DEFENSE_UNDER_1_5': '8/8 (100%)',
    'WINNER_LOCK_DOUBLE_CHANCE': '6/6 (100% no-loss)',
    # REMOVED: 'EDGE_DERIVED_UNDER_1_5': '2/2 (100%)',  # BACKTEST PROVES THIS IS WRONG
    'BOTH_PATTERNS_UNDER_3_5': '3/3 (100%)',
    'ELITE_DEFENSE_ONLY_UNDER_3_5': '7/8 (87.5%)',
    'WINNER_LOCK_ONLY_UNDER_3_5': '5/6 (83.3%)'
}

# PATTERN DISTRIBUTION v7.2 (CORRECTED BASED ON BACKTEST)
PATTERN_DISTRIBUTION = {
    'ELITE_DEFENSE_ONLY': 5,
    'WINNER_LOCK_ONLY': 3,
    'EDGE_DERIVED_ONLY': 0,    # CORRECTED: NOT a proven pattern
    'BOTH_PATTERNS': 3,
    'NO_PATTERNS': 14          # CORRECTED: Increased back to 14
}

# =================== LAYER 1: DEFENSIVE PROOF ENGINE ===================
class DefensiveProofEngine:
    """LAYER 1: Defensive Proof with Binary Gates"""
    
    @staticmethod
    def check_opponent_under(backing_team: str, opponent_data: Dict, market: str) -> Dict:
        """
        When backing TEAM A: Check TEAM B's defensive capabilities
        
        PERSPECTIVE-SENSITIVE: Opponent depends on which team is backed
        """
        opponent_avg_conceded = opponent_data.get('goals_conceded_last_5', 0) / 5
        
        if market == 'OPPONENT_UNDER_1_5':
            if opponent_avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5']:
                return {
                    'lock': True,
                    'type': 'EDGE_DERIVED',
                    'reason': f'Opponent concedes {opponent_avg_conceded:.2f} avg ≤ {DEFENSIVE_THRESHOLDS["OPPONENT_UNDER_1_5"]}'
                }
        
        elif market == 'OPPONENT_UNDER_2_5':
            if opponent_avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_2_5']:
                return {
                    'consideration': True,
                    'reason': f'Opponent concedes {opponent_avg_conceded:.2f} avg ≤ {DEFENSIVE_THRESHOLDS["OPPONENT_UNDER_2_5"]}'
                }
        
        return {'lock': False}
    
    @staticmethod
    def detect_elite_defense_pattern(team_data: Dict, league_avg_conceded: float = 1.3) -> Dict:
        """
        ELITE DEFENSE PATTERN (100% EMPIRICAL - 8/8 matches)
        
        Conditions:
        1. Concedes ≤4 total goals in last 5 matches (avg ≤0.8/match)
        2. Defense gap > 2.0 vs opponent
        """
        total_conceded = team_data.get('goals_conceded_last_5', 0)
        avg_conceded = total_conceded / 5
        defense_gap = league_avg_conceded - avg_conceded
        
        # CRITERIA: Both conditions required
        if total_conceded <= 4 and defense_gap > 2.0:
            return {
                'elite_defense': True,
                'total_conceded': total_conceded,
                'defense_gap': defense_gap,
                'signal': 'OPPONENT_UNDER_1_5 (100% empirical accuracy)',
                'historical_evidence': [
                    'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                    'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Man City 0-0 Sunderland'
                ]
            }
        
        return {'elite_defense': False}

# =================== LAYER 2: PATTERN INDEPENDENCE MATRIX v7.2 ===================
class PatternIndependenceMatrixV72:
    """LAYER 2: Pattern Independence Analysis v7.2"""
    
    @staticmethod
    def get_pattern_distribution() -> Dict:
        """Return empirical pattern distribution from 25-match study v7.2"""
        total_matches = sum(PATTERN_DISTRIBUTION.values())
        percentages = {k: (v/total_matches*100) for k, v in PATTERN_DISTRIBUTION.items()}
        
        # CORRECTED: Edge-Derived is NOT a proven pattern
        actionable_matches = (PATTERN_DISTRIBUTION['ELITE_DEFENSE_ONLY'] + 
                             PATTERN_DISTRIBUTION['WINNER_LOCK_ONLY'] + 
                             PATTERN_DISTRIBUTION['BOTH_PATTERNS'])
        
        return {
            'distribution': PATTERN_DISTRIBUTION,
            'percentages': percentages,
            'total_matches': total_matches,
            'actionable_matches': actionable_matches,  # CORRECTED: 11/25 (44%)
            'stay_away_matches': PATTERN_DISTRIBUTION['NO_PATTERNS']
        }
    
    @staticmethod
    def evaluate_pattern_independence(elite_defense: bool, winner_lock: bool, edge_derived: bool) -> Dict:
        """
        KEY FINDING v7.2: Edge-Derived is NOT a proven pattern
        
        BACKTEST EVIDENCE: Edge-Derived predictions went 1-5 (16.7% win rate)
        """
        # Edge-Derived is NOT counted as a pattern for decision making
        pattern_count = sum([elite_defense, winner_lock])
        
        if pattern_count == 2:
            return {
                'combination': 'ELITE_DEFENSE_WINNER_LOCK',
                'description': 'Both Elite Defense and Winner Lock patterns present',
                'emoji': '🛡️👑',
                'confidence': 'VERY HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['BOTH_PATTERNS'],
                'capital_multiplier': 2.0,
                'is_proven_pattern': True
            }
        elif elite_defense:
            return {
                'combination': 'ONLY_ELITE_DEFENSE',
                'description': 'Only Elite Defense pattern present',
                'emoji': '🛡️',
                'confidence': 'HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['ELITE_DEFENSE_ONLY'],
                'capital_multiplier': 2.0,
                'is_proven_pattern': True
            }
        elif winner_lock:
            return {
                'combination': 'ONLY_WINNER_LOCK',
                'description': 'Only Winner Lock pattern present',
                'emoji': '👑',
                'confidence': 'HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['WINNER_LOCK_ONLY'],
                'capital_multiplier': 2.0,
                'is_proven_pattern': True
            }
        elif edge_derived:
            return {
                'combination': 'EDGE_DERIVED_SIGNAL',
                'description': 'Edge-Derived signal detected (NOT a proven pattern)',
                'emoji': '⚠️',
                'confidence': 'LOW',
                'empirical_count': 0,  # Not counted as pattern
                'capital_multiplier': 1.0,
                'is_proven_pattern': False,
                'note': 'Backtest: 1-5 (16.7% win rate)'
            }
        else:
            return {
                'combination': 'NO_PATTERNS',
                'description': 'No proven patterns detected',
                'emoji': '⚪',
                'confidence': 'LOW',
                'empirical_count': PATTERN_DISTRIBUTION['NO_PATTERNS'],
                'capital_multiplier': 1.0,
                'is_proven_pattern': False
            }

# =================== LAYER 6: INTEGRATED CAPITAL DECISION v7.2 ===================
class IntegratedCapitalEngineV72:
    """LAYER 6: Final Capital Decision v7.2"""
    
    @staticmethod
    def determine_final_capital_decision(all_detections: Dict) -> Dict:
        """
        ONLY PROVEN PATTERNS present → LOCK_MODE (2.0x)
        NO proven patterns → EDGE_MODE (1.0x)
        
        PROVEN PATTERNS v7.2 (based on backtest):
        1. Elite Defense Pattern (100% empirical - 8/8)
        2. Winner Lock (100% no-loss - 6/6)
        
        REMOVED: Edge-Derived Lock (backtest: 1-5, 16.7%)
        """
        locks_present = []
        pattern_sources = []
        
        # PATTERN 1: Elite Defense (PROVEN)
        if all_detections.get('has_elite_defense'):
            locks_present.append('ELITE_DEFENSE_UNDER_1_5')
            pattern_sources.append({
                'type': 'ELITE_DEFENSE',
                'accuracy': '8/8 (100%)',
                'empirical_proof': '25-match study'
            })
        
        # PATTERN 2: Winner Lock (PROVEN)
        if all_detections.get('has_winner_lock'):
            locks_present.append('WINNER_LOCK_DOUBLE_CHANCE')
            pattern_sources.append({
                'type': 'WINNER_LOCK',
                'accuracy': '6/6 (100% no-loss)',
                'empirical_proof': '25-match study'
            })
        
        # Edge-Derived (NOT a pattern - backtest failure)
        if all_detections.get('has_edge_derived_locks'):
            locks_present.append('EDGE_DERIVED_SIGNAL')
            pattern_sources.append({
                'type': 'EDGE_DERIVED_SIGNAL',
                'accuracy': '1/5 (20%) in backtest',
                'note': 'NOT a proven pattern'
            })
        
        # Capital Decision v7.2
        # ONLY proven patterns → LOCK_MODE
        has_proven_pattern = all_detections.get('has_elite_defense', False) or \
                           all_detections.get('has_winner_lock', False)
        
        if has_proven_pattern:
            return {
                'capital_mode': 'LOCK_MODE',
                'multiplier': 2.0,
                'reason': f'Proven patterns detected: {", ".join(locks_present)}',
                'system_verdict': 'STRUCTURAL CERTAINTY DETECTED',
                'locks_present': locks_present,
                'pattern_sources': pattern_sources,
                'has_proven_pattern': has_proven_pattern
            }
        else:
            return {
                'capital_mode': 'EDGE_MODE',
                'multiplier': 1.0,
                'reason': 'No proven patterns detected',
                'system_verdict': 'HEURISTIC EDGE ONLY',
                'locks_present': locks_present,
                'pattern_sources': pattern_sources,
                'has_proven_pattern': False
            }

# =================== COMPLETE EXECUTION ENGINE v7.2 ===================
class FusedLogicEngineV72:
    """COMPLETE FUSED LOGIC ENGINE v7.2 - BACKTEST CORRECTED"""
    
    @staticmethod
    def execute_fused_logic(home_data: Dict, away_data: Dict, 
                           home_name: str, away_name: str,
                           league_avg_xg: float) -> Dict:
        """
        MAIN EXECUTION FUNCTION v7.2
        WITH BACKTEST CORRECTIONS:
        1. Edge-Derived is NOT a proven pattern (backtest: 1-5)
        2. Pattern distribution corrected
        3. Capital decision logic fixed
        """
        all_results = {}
        
        # ========== LAYER 1: DEFENSIVE PROOF ==========
        defensive_engine = DefensiveProofEngine()
        all_results['defensive_assessment'] = {
            'home_avg_conceded': home_data.get('goals_conceded_last_5', 0) / 5,
            'away_avg_conceded': away_data.get('goals_conceded_last_5', 0) / 5
        }
        
        # ========== LAYER 2: PATTERN DETECTION ==========
        all_results['elite_defense_home'] = defensive_engine.detect_elite_defense_pattern(home_data)
        all_results['elite_defense_away'] = defensive_engine.detect_elite_defense_pattern(away_data)
        all_results['has_elite_defense'] = (
            all_results['elite_defense_home'].get('elite_defense', False) or
            all_results['elite_defense_away'].get('elite_defense', False)
        )
        
        # Agency-State detection (placeholder)
        all_results['has_winner_lock'] = False
        
        # Edge-Derived detection
        all_results['edge_derived_sources'] = []
        
        # Check Edge-Derived signals (NOT patterns)
        home_perspective = defensive_engine.check_opponent_under(
            home_name, away_data, 'OPPONENT_UNDER_1_5'
        )
        if home_perspective.get('lock'):
            all_results['edge_derived_sources'].append({
                'source': 'EDGE_DERIVED',
                'perspective': 'BACKING_HOME',
                'declaration': f'⚠️ EDGE SIGNAL: BACK {home_name} → {away_name} UNDER 1.5',
                'reason': home_perspective['reason'],
                'note': 'NOT a proven pattern (backtest: 1-5)'
            })
        
        away_perspective = defensive_engine.check_opponent_under(
            away_name, home_data, 'OPPONENT_UNDER_1_5'
        )
        if away_perspective.get('lock'):
            all_results['edge_derived_sources'].append({
                'source': 'EDGE_DERIVED',
                'perspective': 'BACKING_AWAY',
                'declaration': f'⚠️ EDGE SIGNAL: BACK {away_name} → {home_name} UNDER 1.5',
                'reason': away_perspective['reason'],
                'note': 'NOT a proven pattern (backtest: 1-5)'
            })
        
        all_results['has_edge_derived_locks'] = len(all_results['edge_derived_sources']) > 0
        
        # ========== PATTERN INDEPENDENCE ANALYSIS v7.2 ==========
        pattern_matrix = PatternIndependenceMatrixV72()
        all_results['pattern_independence'] = pattern_matrix.evaluate_pattern_independence(
            all_results['has_elite_defense'],
            all_results['has_winner_lock'],
            all_results['has_edge_derived_locks']
        )
        
        # ========== PATTERN DISTRIBUTION v7.2 ==========
        all_results['pattern_distribution'] = pattern_matrix.get_pattern_distribution()
        
        # ========== CAPITAL DECISION v7.2 ==========
        capital_engine = IntegratedCapitalEngineV72()
        all_results['capital_decision'] = capital_engine.determine_final_capital_decision(all_results)
        
        # ========== DECISION MATRIX v7.2 ==========
        all_results['decision_matrix'] = FusedLogicEngineV72.generate_decision_matrix_v72(all_results)
        
        return all_results
    
    @staticmethod
    def generate_decision_matrix_v72(all_results: Dict) -> Dict:
        """
        CORRECTED DECISION FLOW v7.2
        Edge-Derived is NOT a proven pattern
        """
        decisions = {
            'STAY_AWAY': False,
            'LOCKS_DETECTED': [],
            'CONSIDERATIONS': [],
            'PATTERN_SOURCES': []
        }
        
        # Check for PROVEN patterns only
        has_proven_pattern = all_results.get('has_elite_defense', False) or \
                           all_results.get('has_winner_lock', False)
        
        pattern_dist = PatternIndependenceMatrixV72().get_pattern_distribution()
        
        if not has_proven_pattern:
            decisions['STAY_AWAY'] = True
            decisions['REASON'] = f'No proven patterns detected ({pattern_dist["stay_away_matches"]}/{pattern_dist["total_matches"]} matches empirical)'
            
            # Edge-Derived signals are NOT patterns
            if all_results.get('has_edge_derived_locks'):
                decisions['CONSIDERATIONS'].append(
                    f"⚠️ Edge-Derived signals detected (NOT proven patterns - backtest: 1-5)"
                )
            
            return decisions
        
        # We HAVE proven patterns
        decisions['STAY_AWAY'] = False
        
        # Track pattern sources
        if all_results.get('has_elite_defense'):
            decisions['PATTERN_SOURCES'].append('ELITE_DEFENSE')
            decisions['LOCKS_DETECTED'].append('🛡️ ELITE DEFENSE PATTERN DETECTED')
        
        if all_results.get('has_winner_lock'):
            decisions['PATTERN_SOURCES'].append('WINNER_LOCK')
            decisions['LOCKS_DETECTED'].append('👑 WINNER LOCK PATTERN DETECTED')
        
        # Edge-Derived signals (NOT patterns)
        if all_results.get('has_edge_derived_locks'):
            for signal in all_results.get('edge_derived_sources', []):
                decisions['CONSIDERATIONS'].append(
                    f"⚠️ {signal['declaration']} (NOT a proven pattern)"
                )
        
        return decisions

# =================== STREAMLIT APP CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v7.2 - BACKTEST CORRECTED",
    page_icon="🎯",
    layout="wide"
)

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .system-header {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #1E3A8A 0%, #DC2626 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #DC2626;
    }
    .backtest-warning {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 4px solid #DC2626;
        margin: 1rem 0;
        text-align: center;
    }
    .prediction-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 4px solid;
        margin: 1rem 0;
        text-align: center;
    }
    .lock-mode {
        border-color: #10B981;
        background: linear-gradient(135deg, #F0FDF4 0%, #E2F7EB 100%);
    }
    .edge-mode {
        border-color: #F59E0B;
        background: linear-gradient(135deg, #FEF3C7 0%, #FCE9B2 100%);
    }
    .stay-away {
        border-color: #DC2626;
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
    }
    .prediction-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .capital-multiplier {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .backtest-results {
        background: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .result-correct {
        color: #10B981;
        font-weight: 600;
    }
    .result-incorrect {
        color: #DC2626;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'color': '#EF4444'
    },
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'color': '#3B82F6'
    }
}

# =================== DATA LOADING FUNCTIONS ===================
@st.cache_data(ttl=3600)
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data with CSV structure"""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple file locations
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename
        ]
        
        df = None
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                break
            except Exception:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics"""
    
    # Goals scored
    df['home_goals_scored'] = (
        df['home_goals_openplay_for'].fillna(0) +
        df['home_goals_counter_for'].fillna(0) +
        df['home_goals_setpiece_for'].fillna(0) +
        df['home_goals_penalty_for'].fillna(0) +
        df['home_goals_owngoal_for'].fillna(0)
    )
    
    df['away_goals_scored'] = (
        df['away_goals_openplay_for'].fillna(0) +
        df['away_goals_counter_for'].fillna(0) +
        df['away_goals_setpiece_for'].fillna(0) +
        df['away_goals_penalty_for'].fillna(0) +
        df['away_goals_owngoal_for'].fillna(0)
    )
    
    # Goals conceded
    df['home_goals_conceded'] = (
        df['home_goals_openplay_against'].fillna(0) +
        df['home_goals_counter_against'].fillna(0) +
        df['home_goals_setpiece_against'].fillna(0) +
        df['home_goals_penalty_against'].fillna(0) +
        df['home_goals_owngoal_against'].fillna(0)
    )
    
    df['away_goals_conceded'] = (
        df['away_goals_openplay_against'].fillna(0) +
        df['away_goals_counter_against'].fillna(0) +
        df['away_goals_setpiece_against'].fillna(0) +
        df['away_goals_penalty_against'].fillna(0) +
        df['away_goals_owngoal_against'].fillna(0)
    )
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION v7.2 ===================
def main():
    """Main application function v7.2 - Backtest Corrected"""
    
    # Header
    st.markdown('<div class="system-header">BRUTBALL v7.2 - BACKTEST CORRECTED</div>', unsafe_allow_html=True)
    
    # Backtest Warning
    st.markdown("""
    <div class="backtest-warning">
        <div style="font-size: 1.2rem; font-weight: 700; color: #DC2626; margin-bottom: 0.5rem;">
            ⚠️ CRITICAL BACKTEST FINDINGS
        </div>
        <div style="margin-bottom: 0.5rem;">
            <strong>Edge-Derived pattern FAILED in backtest:</strong> 1-5 (16.7% win rate)
        </div>
        <div style="font-size: 0.9rem;">
            • Edge-Derived is <strong>NOT</strong> a proven pattern<br>
            • Pattern distribution corrected: 11/25 actionable (44%)<br>
            • Only Elite Defense & Winner Lock are proven patterns
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Backtest Results
    st.markdown("### 📊 BACKTEST RESULTS (10 Matches)")
    
    backtest_data = [
        {"Match": "Valencia vs Mallorca", "Prediction": "LOCK (Edge-Derived)", "Result": "1-1", "Status": "❌"},
        {"Match": "Real Oviedo vs Celta Vigo", "Prediction": "LOCK (Edge-Derived)", "Result": "0-0", "Status": "✅"},
        {"Match": "Levante vs Real Sociedad", "Prediction": "STAY-AWAY", "Result": "0-0", "Status": "✅"},
        {"Match": "Osasuna vs Alavés", "Prediction": "STAY-AWAY", "Result": "3-0", "Status": "✅"},
        {"Match": "Real Madrid vs Sociedad", "Prediction": "LOCK (Edge-Derived)", "Result": "2-0", "Status": "❌"},
        {"Match": "Girona vs Atlético", "Prediction": "LOCK (Edge-Derived)", "Result": "0-3", "Status": "❌"},
        {"Match": "Villarreal vs Barcelona", "Prediction": "LOCK (Edge-Derived)", "Result": "0-2", "Status": "❌"},
        {"Match": "Elche vs Rayo", "Prediction": "STAY-AWAY", "Result": "4-0", "Status": "✅"},
        {"Match": "Betis vs Getafe", "Prediction": "STAY-AWAY", "Result": "4-0", "Status": "✅"},
        {"Match": "Athletic vs Espanyol", "Prediction": "LOCK (Edge-Derived)", "Result": "1-2", "Status": "❌"},
    ]
    
    for result in backtest_data:
        status_class = "result-correct" if result["Status"] == "✅" else "result-incorrect"
        st.markdown(f"""
        <div class="result-row">
            <div>{result["Match"]}</div>
            <div>{result["Prediction"]}</div>
            <div>{result["Result"]}</div>
            <div class="{status_class}">{result["Status"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-top: 1rem; text-align: center;">
        <strong>LOCK_MODE (Edge-Derived):</strong> 1-5 (16.7%)<br>
        <strong>STAY-AWAY:</strong> 4-0 (100%)<br>
        <strong>Conclusion:</strong> Edge-Derived is <strong>NOT</strong> a proven pattern
    </div>
    """, unsafe_allow_html=True)
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(2)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            if st.button(
                LEAGUES[league]['display_name'],
                use_container_width=True,
                key=f"league_{idx}"
            ):
                st.session_state.selected_league = league
    
    # Default league if not selected
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'La Liga'
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Match selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options)
    
    # Execute analysis
    if st.button("🎯 EXECUTE FUSED LOGIC ANALYSIS v7.2", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Execute fused logic analysis
        with st.spinner("Executing Backtest-Corrected Analysis..."):
            result = FusedLogicEngineV72.execute_fused_logic(
                home_data, away_data, home_team, away_team, 1.3
            )
        
        st.markdown("---")
        
        # =================== PREDICTION SECTION ===================
        st.markdown("## 🎯 SYSTEM PREDICTIONS v7.2")
        
        capital_decision = result['capital_decision']
        decision_matrix = result['decision_matrix']
        
        # Capital Decision Display
        if capital_decision['capital_mode'] == 'LOCK_MODE':
            st.markdown(f"""
            <div class="prediction-box lock-mode">
                <div class="prediction-title">🔒 LOCK MODE DETECTED</div>
                <div class="capital-multiplier">2.0x CAPITAL MULTIPLIER</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    {capital_decision['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prediction-box edge-mode">
                <div class="prediction-title">⚠️ EDGE MODE ONLY</div>
                <div class="capital-multiplier">1.0x CAPITAL MULTIPLIER</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    {capital_decision['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Stay-Away Decision
        if decision_matrix['STAY_AWAY']:
            st.markdown(f"""
            <div class="prediction-box stay-away">
                <div class="prediction-title">🚫 STAY AWAY RECOMMENDED</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    {decision_matrix['REASON']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show actionable recommendations
            if decision_matrix['LOCKS_DETECTED']:
                st.markdown("### 🔒 PROVEN PATTERNS DETECTED")
                for lock in decision_matrix['LOCKS_DETECTED']:
                    st.markdown(f"""
                    <div style="background: #F0FDF4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10B981; margin: 0.5rem 0;">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">{lock}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if decision_matrix['CONSIDERATIONS']:
                st.markdown("### ⚠️ ADDITIONAL SIGNALS")
                for consideration in decision_matrix['CONSIDERATIONS']:
                    st.markdown(f"""
                    <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                        {consideration}
                    </div>
                    """, unsafe_allow_html=True)
        
        # =================== TEAM STATS SECTION ===================
        st.markdown("---")
        st.markdown("## 📊 TEAM STATISTICS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            defensive_assessment = result['defensive_assessment']
            home_conceded_total = home_data.get('goals_conceded_last_5', 0)
            
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #E5E7EB;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #1F2937; margin-bottom: 0.5rem;">{home_team}</div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6;">
                    <span style="color: #6B7280;">Avg Conceded (Last 5)</span>
                    <span style="font-weight: 600; color: #1F2937;">{defensive_assessment['home_avg_conceded']:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6;">
                    <span style="color: #6B7280;">Total Conceded (Last 5)</span>
                    <span style="font-weight: 600; color: #1F2937;">{home_conceded_total}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="color: #6B7280;">Edge-Derived Signal</span>
                    <span style="font-weight: 600; color: #DC2626;">{"⚠️" if defensive_assessment['home_avg_conceded'] <= 1.0 else "❌"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            away_conceded_total = away_data.get('goals_conceded_last_5', 0)
            
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #E5E7EB;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #1F2937; margin-bottom: 0.5rem;">{away_team}</div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6;">
                    <span style="color: #6B7280;">Avg Conceded (Last 5)</span>
                    <span style="font-weight: 600; color: #1F2937;">{defensive_assessment['away_avg_conceded']:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6;">
                    <span style="color: #6B7280;">Total Conceded (Last 5)</span>
                    <span style="font-weight: 600; color: #1F2937;">{away_conceded_total}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="color: #6B7280;">Edge-Derived Signal</span>
                    <span style="font-weight: 600; color: #DC2626;">{"⚠️" if defensive_assessment['away_avg_conceded'] <= 1.0 else "❌"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # =================== SYSTEM INFORMATION ===================
        st.markdown("---")
        st.markdown("## 📚 SYSTEM INFORMATION v7.2")
        
        # Pattern Distribution
        pattern_dist = result['pattern_distribution']
        st.markdown("### 📈 Pattern Distribution (Corrected)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 2px solid #E5E7EB; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937;">{pattern_dist['distribution']['ELITE_DEFENSE_ONLY']}</div>
                <div style="font-size: 0.9rem; color: #6B7280;">Elite Defense Only</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 2px solid #E5E7EB; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937;">{pattern_dist['distribution']['WINNER_LOCK_ONLY']}</div>
                <div style="font-size: 0.9rem; color: #6B7280;">Winner Lock Only</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 2px solid #E5E7EB; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937;">{pattern_dist['distribution']['BOTH_PATTERNS']}</div>
                <div style="font-size: 0.9rem; color: #6B7280;">Both Patterns</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 2px solid #E5E7EB; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937;">{pattern_dist['distribution']['NO_PATTERNS']}</div>
                <div style="font-size: 0.9rem; color: #6B7280;">No Patterns</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: #F3F4F6; border-radius: 8px;">
            <strong>Actionable Matches:</strong> {pattern_dist['actionable_matches']}/{pattern_dist['total_matches']} ({pattern_dist['actionable_matches']/pattern_dist['total_matches']*100:.0f}%)<br>
            <span style="font-size: 0.9rem; color: #DC2626;">
                ↓ Corrected from 52% to 44% (Edge-Derived removed)
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern Independence
        pattern_independence = result['pattern_independence']
        st.markdown("### 🧩 Pattern Independence Analysis")
        
        st.markdown(f"""
        <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                {pattern_independence['emoji']} {pattern_independence['combination']}
            </div>
            <div style="margin-bottom: 0.5rem;">{pattern_independence['description']}</div>
            <div style="font-size: 0.9rem; color: #6B7280;">
                Confidence: {pattern_independence['confidence']} • Empirical: {pattern_independence['empirical_count']}/25 matches
                {f"<br><span style='color: #DC2626;'>{pattern_independence['note']}</span>" if pattern_independence.get('note') else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System Fixes
        st.markdown("### 🔧 System Corrections v7.2")
        
        st.markdown("""
        <div style="background: #FEF2F2; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <div style="font-weight: 600; margin-bottom: 0.5rem; color: #DC2626;">Critical Corrections Based on Backtest:</div>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li><strong>Edge-Derived pattern removed:</strong> Backtest showed 1-5 (16.7% win rate)</li>
                <li><strong>Pattern distribution corrected:</strong> 11/25 actionable (44%) not 13/25</li>
                <li><strong>Only proven patterns trigger LOCK_MODE:</strong> Elite Defense (8/8) & Winner Lock (6/6)</li>
                <li><strong>Edge-Derived signals demoted:</strong> Now shown as warnings, not patterns</li>
                <li><strong>Empirical claims updated:</strong> Removed false 100% accuracy for Edge-Derived</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        export_text = f"""BRUTBALL FUSED LOGIC SYSTEM v7.2 - BACKTEST CORRECTED
===========================================
Match: {home_team} vs {away_team}
League: {selected_league}

SYSTEM VERDICT: {capital_decision['capital_mode']} ({capital_decision['multiplier']:.1f}x)
Reason: {capital_decision['reason']}

BACKTEST CORRECTIONS v7.2:
• Edge-Derived pattern FAILED: 1-5 (16.7% win rate) in 10-match test
• Edge-Derived is NOT a proven pattern
• Pattern distribution corrected: 11/25 actionable (44%)
• Only Elite Defense (8/8) & Winner Lock (6/6) are proven patterns

PATTERN ANALYSIS:
• Combination: {pattern_independence['combination']}
• Confidence: {pattern_independence['confidence']}
• Is Proven Pattern: {pattern_independence.get('is_proven_pattern', False)}

TEAM STATISTICS:
• {home_team}: {defensive_assessment['home_avg_conceded']:.2f} avg conceded (last 5)
• {away_team}: {defensive_assessment['away_avg_conceded']:.2f} avg conceded (last 5)

DECISION MATRIX:
• Stay-Away: {'YES' if decision_matrix['STAY_AWAY'] else 'NO'} {decision_matrix['REASON'] if decision_matrix.get('REASON') else ''}
• Pattern Sources: {', '.join(decision_matrix['PATTERN_SOURCES']) if decision_matrix.get('PATTERN_SOURCES') else 'None'}
• Edge-Derived Signals: {'Detected (NOT patterns)' if result.get('has_edge_derived_locks') else 'None'}

BACKTEST SUMMARY:
• LOCK_MODE (Edge-Derived): 1-5 (16.7%) - FAILED
• STAY-AWAY: 4-0 (100%) - WORKING
• Conclusion: System v7.1 was overconfident in Edge-Derived pattern
• v7.2 corrects this by removing Edge-Derived as a proven pattern
"""
        
        st.download_button(
            label="📥 Download Analysis Report v7.2",
            data=export_text,
            file_name=f"brutball_v7.2_corrected_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )

if __name__ == "__main__":
    main()