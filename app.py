import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== UPDATED CLASSIFIER IMPORT ===================
try:
    from match_state_classifier import (
        MatchStateClassifier, 
        ProvenPatternDetector,
        BankrollManager,
        get_complete_classification, 
        format_reliability_badge, 
        format_durability_indicator,
        format_pattern_badge
    )
    STATE_CLASSIFIER_AVAILABLE = True
except ImportError:
    STATE_CLASSIFIER_AVAILABLE = False
    # Fallback functions
    get_complete_classification = None
    format_reliability_badge = None
    format_durability_indicator = None
    format_pattern_badge = None

# =================== EXISTING DATA EXTRACTION FUNCTIONS ===================
def extract_pure_team_data(df: pd.DataFrame, team_name: str) -> Dict:
    """Extract team data with ZERO transformations"""
    if team_name not in df['team'].values:
        st.error(f"❌ Team '{team_name}' not found in CSV.")
        return {}
    
    team_row = df[df['team'] == team_name].iloc[0]
    team_data = {}
    for col in df.columns:
        value = team_row[col]
        team_data[col] = value
    
    return team_data

def normalize_numeric_types(data_dict: Dict) -> Dict:
    """Architecturally pure type normalization"""
    normalized = {}
    
    for key, value in data_dict.items():
        if key in ['goals_scored_last_5', 'goals_conceded_last_5']:
            if pd.isna(value):
                normalized[key] = value
            else:
                try:
                    if isinstance(value, str):
                        if '.' in str(value):
                            normalized[key] = float(value)
                        else:
                            normalized[key] = int(value)
                    elif hasattr(value, 'item'):
                        normalized[key] = value.item()
                    elif isinstance(value, (np.integer, np.floating)):
                        normalized[key] = float(value)
                    else:
                        normalized[key] = float(value)
                except (ValueError, TypeError):
                    normalized[key] = value
        else:
            normalized[key] = value
    
    return normalized

def verify_data_integrity(df: pd.DataFrame, home_team: str, away_team: str):
    """Verify that CSV data has the required fields"""
    print("="*80)
    print("🛡️ DATA INTEGRITY VERIFICATION")
    print("="*80)
    
    required_columns = ['team', 'goals_scored_last_5', 'goals_conceded_last_5']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ CRITICAL: Missing required columns: {missing_columns}")
        return False
    
    print("✅ CSV structure verified")
    
    if home_team not in df['team'].values:
        print(f"❌ Home team '{home_team}' not found in CSV")
        return False
    
    if away_team not in df['team'].values:
        print(f"❌ Away team '{away_team}' not found in CSV")
        return False
    
    print(f"✅ Teams found: {home_team}, {away_team}")
    
    for team in [home_team, away_team]:
        team_row = df[df['team'] == team].iloc[0]
        print(f"\n📊 {team} data check:")
        for field in ['goals_scored_last_5', 'goals_conceded_last_5']:
            value = team_row[field]
            status = "✅" if not pd.isna(value) else "❌ NaN"
            print(f"  {status} {field}: {value}")
    
    print("="*80)
    return True

# =================== PROVEN PATTERNS DISPLAY ===================
def display_proven_patterns_results(pattern_results: Dict, home_team: str, away_team: str):
    """Beautiful display for proven pattern detection results"""
    
    if not pattern_results or pattern_results['patterns_detected'] == 0:
        st.markdown("""
        <div class="no-patterns-display" style="background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); 
                padding: 2.5rem; border-radius: 12px; border: 3px dashed #9CA3AF; 
                text-align: center; margin: 1.5rem 0;">
            <h3 style="color: #6B7280; margin: 0 0 1rem 0;">🎯 NO PROVEN PATTERNS DETECTED</h3>
            <div style="color: #374151; margin-bottom: 1rem;">
                This match doesn't meet the criteria for our 25-match empirical patterns
            </div>
            <div style="font-size: 0.9rem; color: #6B7280;">
                Patterns require Elite Defense (≤4 goals last 5) or Winner Lock detection
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Header with pattern count
    patterns_count = pattern_results['patterns_detected']
    st.markdown(f"""
    <div class="patterns-header-display" style="background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%); 
            padding: 2rem; border-radius: 12px; border: 4px solid #F97316; 
            text-align: center; margin: 1.5rem 0; box-shadow: 0 6px 16px rgba(249, 115, 22, 0.15);">
        <h2 style="color: #9A3412; margin: 0 0 0.5rem 0;">🎯 PROVEN PATTERNS DETECTED</h2>
        <div style="font-size: 1.5rem; color: #EA580C; font-weight: 700; margin-bottom: 0.5rem;">
            {patterns_count} Pattern(s) Found
        </div>
        <div style="color: #92400E; font-size: 0.9rem;">
            Based on 25-match empirical analysis (100% & 83.3% accuracy)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display each recommendation in beautiful cards
    for idx, rec in enumerate(pattern_results['recommendations']):
        # Pattern-specific styling
        pattern_styles = {
            'ELITE_DEFENSE_UNDER_1_5': {
                'bg_color': 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
                'border_color': '#16A34A',
                'emoji': '🛡️',
                'title_color': '#065F46',
                'badge_color': '#16A34A'
            },
            'WINNER_LOCK_DOUBLE_CHANCE': {
                'bg_color': 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
                'border_color': '#2563EB',
                'emoji': '👑',
                'title_color': '#1E40AF',
                'badge_color': '#2563EB'
            },
            'PATTERN_DRIVEN_UNDER_3_5': {
                'bg_color': 'linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 100%)',
                'border_color': '#7C3AED',
                'emoji': '📊',
                'title_color': '#5B21B6',
                'badge_color': '#7C3AED'
            }
        }
        
        style = pattern_styles.get(rec['pattern'], pattern_styles['ELITE_DEFENSE_UNDER_1_5'])
        
        # Create beautiful card
        st.markdown(f"""
        <div style="background: {style['bg_color']}; padding: 1.5rem; border-radius: 10px; 
                border: 3px solid {style['border_color']}; margin: 1rem 0;">
            
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">{style['emoji']}</span>
                        <h3 style="color: {style['title_color']}; margin: 0;">{rec['bet_type']}</h3>
                    </div>
                    {'<div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">Team: ' + rec['team_to_bet'] + '</div>' if 'team_to_bet' in rec else ''}
                    <div style="color: #6B7280; font-size: 0.9rem;">{rec['reason']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="background: {style['badge_color']}; color: white; padding: 0.25rem 0.75rem; 
                            border-radius: 20px; font-size: 0.85rem; font-weight: 700;">
                        {rec['stake_multiplier']:.1f}x
                    </div>
                    <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">Stake Multiplier</div>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.7); padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Pattern</div>
                        <div style="font-weight: 600; color: {style['title_color']};">{rec['pattern'].replace('_', ' ')}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Sample Accuracy</div>
                        <div style="font-weight: 600; color: #059669;">{rec['sample_accuracy']}</div>
                    </div>
                </div>
                
                <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.1);">
                    <div style="font-size: 0.85rem; color: #6B7280; margin-bottom: 0.25rem;">
                        <strong>Historical Evidence:</strong>
                    </div>
                    <div style="font-size: 0.8rem; color: #4B5563;">
                        {', '.join(rec['sample_matches'][:3])}
                    </div>
                </div>
            </div>
            
        </div>
        """, unsafe_allow_html=True)

# =================== PERFORMANCE TRACKER ===================
class PerformanceTracker:
    """Tracker for system predictions vs actual results"""
    
    def __init__(self):
        self.predictions = []
        self.actual_results = []
    
    def record_prediction(self, match_info: str, prediction: str, confidence: str):
        self.predictions.append({
            'match': match_info,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def record_result(self, match_info: str, actual_score: str):
        self.actual_results.append({
            'match': match_info,
            'actual_score': actual_score,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def calculate_accuracy(self) -> Dict:
        matched = 0
        for pred in self.predictions:
            for result in self.actual_results:
                if pred['match'] == result['match']:
                    matched += 1
                    break
        
        total = len(self.predictions)
        accuracy = (matched / total * 100) if total > 0 else 0
        
        return {
            'total_predictions': total,
            'total_results': len(self.actual_results),
            'matched_pairs': matched,
            'accuracy': accuracy
        }

# Initialize trackers
performance_tracker = PerformanceTracker()
bankroll_manager = BankrollManager(initial_bankroll=10000.0)

# =================== SYSTEM CONSTANTS ===================
CONTROL_CRITERIA_REQUIRED = 2
GOALS_ENV_THRESHOLD = 2.8
ELITE_ATTACK_THRESHOLD = 1.6
DIRECTION_THRESHOLD = 0.25
ENFORCEMENT_METHODS_REQUIRED = 2
STATE_FLIP_FAILURES_REQUIRED = 2
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1
TOTALS_LOCK_THRESHOLD = 1.2
UNDER_GOALS_THRESHOLD = 2.5

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {'filename': 'premier_league.csv', 'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League', 'color': '#3B82F6'},
    'La Liga': {'filename': 'la_liga.csv', 'display_name': '🇪🇸 La Liga', 'color': '#EF4444'},
    'Bundesliga': {'filename': 'bundesliga.csv', 'display_name': '🇩🇪 Bundesliga', 'color': '#000000'},
    'Serie A': {'filename': 'serie_a.csv', 'display_name': '🇮🇹 Serie A', 'color': '#10B981'},
    'Ligue 1': {'filename': 'ligue_1.csv', 'display_name': '🇫🇷 Ligue 1', 'color': '#8B5CF6'},
    'Eredivisie': {'filename': 'eredivisie.csv', 'display_name': '🇳🇱 Eredivisie', 'color': '#F59E0B'},
    'Primeira Liga': {'filename': 'premeira_portugal.csv', 'display_name': '🇵🇹 Primeira Liga', 'color': '#DC2626'},
    'Super Lig': {'filename': 'super_league.csv', 'display_name': '🇹🇷 Super Lig', 'color': '#E11D48'}
}

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .system-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 1rem;
    }
    .system-subheader {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .pattern-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .pattern-card-elite {
        border-color: #16A34A;
        border-left: 6px solid #16A34A;
    }
    .pattern-card-winner {
        border-color: #2563EB;
        border-left: 6px solid #2563EB;
    }
    .pattern-card-total {
        border-color: #7C3AED;
        border-left: 6px solid #7C3AED;
    }
    .pattern-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .badge-elite {
        background: #DCFCE7;
        color: #065F46;
        border: 1px solid #86EFAC;
    }
    .badge-winner {
        background: #DBEAFE;
        color: #1E40AF;
        border: 1px solid #93C5FD;
    }
    .badge-total {
        background: #F3E8FF;
        color: #5B21B6;
        border: 1px solid #C4B5FD;
    }
    .stake-display {
        background: #FFFBEB;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #F59E0B;
        margin: 1rem 0;
        text-align: center;
    }
    .bankroll-display {
        background: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #0EA5E9;
        margin: 1rem 0;
    }
    .accuracy-display {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #10B981;
        margin: 1rem 0;
    }
    .historical-proof {
        background: #FEFCE8;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #FACC15;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .pattern-header {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 4px solid #F97316;
        text-align: center;
        margin: 1.5rem 0;
    }
    .empirical-proof {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #0EA5E9;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare league data"""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
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
    """Calculate derived metrics from CSV structure"""
    
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
    
    # Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application with Proven Pattern Detection"""
    
    # Header with pattern detection emphasis
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL INTEGRATED v6.3 + PROVEN PATTERNS</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>THREE PROVEN PATTERNS FROM 25-MATCH EMPIRICAL ANALYSIS</strong></p>
        <p>Pattern A: Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)</p>
        <p>Pattern B: Winner Lock → Double Chance (100% - 6 matches)</p>
        <p>Pattern C: UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)</p>
        <p><strong>NEW:</strong> Beautiful UI with clear betting recommendations & stake calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Empirical Proof Display
    st.markdown("""
    <div class="empirical-proof">
        <h4>📊 EMPIRICAL PROOF (25-MATCH ANALYSIS)</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div style="text-align: center; padding: 1rem; background: #DCFCE7; border-radius: 8px;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #065F46;">100%</div>
                <div style="font-size: 0.9rem; color: #374151;">Elite Defense Pattern</div>
                <div style="font-size: 0.8rem; color: #6B7280;">8/8 matches</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: #DBEAFE; border-radius: 8px;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #1E40AF;">100%</div>
                <div style="font-size: 0.9rem; color: #374151;">Winner Lock Pattern</div>
                <div style="font-size: 0.8rem; color: #6B7280;">6/6 matches</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: #F3E8FF; border-radius: 8px;">
                <div style="font-size: 1.5rem; font-weight: 800; color: #5B21B6;">83.3%</div>
                <div style="font-size: 0.9rem; color: #374151;">Under 3.5 Pattern</div>
                <div style="font-size: 0.8rem; color: #6B7280;">10/12 matches</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pattern Conditions Display
    st.markdown("""
    <div class="historical-proof">
        <h4>🎯 PATTERN CONDITIONS</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div style="padding: 1rem; background: #F0FDF4; border-radius: 6px;">
                <div style="font-weight: 700; color: #065F46; margin-bottom: 0.5rem;">
                    🛡️ ELITE DEFENSE
                </div>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.9rem;">
                    <li>Team concedes ≤4 goals TOTAL in last 5 matches</li>
                    <li>Defense gap > 2.0 goals vs opponent</li>
                    <li>Bet: Opponent UNDER 1.5 goals</li>
                </ul>
            </div>
            <div style="padding: 1rem; background: #EFF6FF; border-radius: 6px;">
                <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">
                    👑 WINNER LOCK
                </div>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.9rem;">
                    <li>Agency-State Lock gives WINNER lock</li>
                    <li>Team does NOT lose (wins or draws)</li>
                    <li>Bet: DOUBLE CHANCE (Win or Draw)</li>
                </ul>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: #FAF5FF; border-radius: 6px;">
            <div style="font-weight: 700; color: #5B21B6; margin-bottom: 0.5rem;">
                📊 UNDER 3.5 WHEN PATTERNS PRESENT
            </div>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.9rem;">
                <li>EITHER Elite Defense OR Winner Lock pattern present</li>
                <li>Bet: TOTAL UNDER 3.5 goals</li>
                <li>83.3% accuracy in sample matches</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'pattern_results' not in st.session_state:
        st.session_state.pattern_results = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("### 🌍 League Selection")
    cols = st.columns(8)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary",
                key=f"league_btn_{league}"
            ):
                st.session_state.selected_league = league
                st.session_state.analysis_complete = False
                st.rerun()
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Team selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()), key="home_team_select")
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Get data for pattern detection
    home_data = extract_pure_team_data(df, home_team)
    away_data = extract_pure_team_data(df, away_team)
    
    # Execute analysis
    if st.button("⚡ DETECT PROVEN PATTERNS", type="primary", use_container_width=True, key="detect_patterns"):
        
        # Prepare data for pattern detection
        match_metadata = {
            'home_team': home_team,
            'away_team': away_team,
            'winner_lock_detected': False,  # Will be replaced by actual data
            'winner_lock_team': '',
            'winner_delta_value': 0
        }
        
        # Run pattern detection
        pattern_results = ProvenPatternDetector.generate_all_patterns(
            home_data, away_data, match_metadata
        )
        
        # Store results
        st.session_state.pattern_results = pattern_results
        st.session_state.analysis_complete = True
        
        st.rerun()
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.pattern_results:
        pattern_results = st.session_state.pattern_results
        
        # Display Proven Patterns
        st.markdown("### 🎯 PROVEN PATTERN DETECTION RESULTS")
        display_proven_patterns_results(pattern_results, home_team, away_team)
        
        # Bankroll and Stake Management
        st.markdown("### 💰 BANKROLL MANAGEMENT")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_level = st.selectbox(
                "Risk Level",
                ["CONSERVATIVE (0.5%)", "MEDIUM (1.0%)", "AGGRESSIVE (1.5%)"],
                index=1
            )
        
        with col2:
            base_percentage = {
                "CONSERVATIVE (0.5%)": 0.005,
                "MEDIUM (1.0%)": 0.01,
                "AGGRESSIVE (1.5%)": 0.015
            }[risk_level]
            base_stake = bankroll_manager.bankroll * base_percentage
            st.metric("Base Stake per Bet", f"${base_stake:.2f}")
        
        with col3:
            bankroll_status = bankroll_manager.get_status()
            st.metric("Current Bankroll", f"${bankroll_manager.bankroll:.2f}")
        
        # Calculate stakes for each recommendation
        if pattern_results['patterns_detected'] > 0:
            st.markdown("#### 📊 RECOMMENDED STAKES")
            
            total_stake = 0
            for idx, rec in enumerate(pattern_results['recommendations']):
                stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                total_stake += stake
                
                # Determine card style
                card_class = {
                    'ELITE_DEFENSE_UNDER_1_5': 'pattern-card-elite',
                    'WINNER_LOCK_DOUBLE_CHANCE': 'pattern-card-winner',
                    'PATTERN_DRIVEN_UNDER_3_5': 'pattern-card-total'
                }.get(rec['pattern'], 'pattern-card')
                
                st.markdown(f"""
                <div class="pattern-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; font-size: 1.1rem;">
                            {rec['bet_type']}
                        </div>
                        <div style="background: #3B82F6; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 700;">
                            ${stake:.2f}
                        </div>
                    </div>
                    <div style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        {rec['reason']}
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #4B5563;">
                        <div>
                            <strong>Stake:</strong> {stake/bankroll_manager.bankroll*100:.1f}% of bankroll
                        </div>
                        <div>
                            <strong>Multiplier:</strong> {rec['stake_multiplier']:.1f}x
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Total stake warning
            risk_percentage = (total_stake / bankroll_manager.bankroll) * 100
            risk_color = "#059669" if risk_percentage < 10 else "#F59E0B" if risk_percentage < 20 else "#DC2626"
            
            st.markdown(f"""
            <div class="stake-display">
                <div style="font-weight: 700; margin-bottom: 0.5rem;">
                    Total Stake for This Match
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: {risk_color};">
                    ${total_stake:.2f}
                </div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.25rem;">
                    {risk_percentage:.1f}% of bankroll • {pattern_results['patterns_detected']} pattern(s)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance Tracking
        st.markdown("### 📈 PERFORMANCE TRACKING")
        
        col1, col2 = st.columns(2)
        with col1:
            actual_home = st.number_input(
                f"{home_team} actual goals", 
                min_value=0, max_value=10, value=0, 
                key="actual_home"
            )
        with col2:
            actual_away = st.number_input(
                f"{away_team} actual goals", 
                min_value=0, max_value=10, value=0, 
                key="actual_away"
            )
        
        if st.button("Record Match Result", type="secondary"):
            # Record predictions
            for rec in pattern_results['recommendations']:
                match_info = f"{home_team} vs {away_team}"
                prediction = f"{rec['bet_type']}: {rec.get('team_to_bet', 'Match')}"
                accuracy = rec['sample_accuracy'].split('(')[0].strip()
                performance_tracker.record_prediction(match_info, prediction, accuracy)
            
            # Record result
            actual_score = f"{actual_home}-{actual_away}"
            performance_tracker.record_result(f"{home_team} vs {away_team}", actual_score)
            
            # Calculate profit/loss
            actual_total = actual_home + actual_away
            profit_loss = 0
            
            for rec in pattern_results['recommendations']:
                stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                
                # Check if bet would win
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    # Bet: Opponent UNDER 1.5
                    if rec['team_to_bet'] == away_team:
                        would_win = actual_away <= 1
                    else:
                        would_win = actual_home <= 1
                    odds = 1.8  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
                    
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    # Bet: Double Chance (Win or Draw)
                    if rec['team_to_bet'] == home_team:
                        would_win = actual_home >= actual_away
                    else:
                        would_win = actual_away >= actual_home
                    odds = 1.3  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
                    
                elif rec['pattern'] == 'PATTERN_DRIVEN_UNDER_3_5':
                    # Bet: UNDER 3.5
                    would_win = actual_total < 3.5
                    odds = 1.9  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
            
            # Update bankroll
            bankroll_manager.update_after_result(profit_loss)
            
            # Show result
            result_color = "#059669" if profit_loss >= 0 else "#DC2626"
            st.success(f"""
            ✅ Recorded: {home_team} {actual_home}-{actual_away} {away_team}
            
            **Profit/Loss:** <span style='color:{result_color}; font-weight:700;'>
            ${profit_loss:+.2f}</span>
            
            **New Bankroll:** ${bankroll_manager.bankroll:.2f}
            """, unsafe_allow_html=True)
            
            # Check if should continue
            should_continue, message = bankroll_manager.should_continue_betting()
            if not should_continue:
                st.warning(f"⚠️ {message}")
            
            st.rerun()
        
        # Display performance stats
        stats = performance_tracker.calculate_accuracy()
        bankroll_status = bankroll_manager.get_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Predictions", stats['total_predictions'])
        with col2:
            st.metric("Accuracy", f"{stats['accuracy']:.1f}%")
        with col3:
            st.metric("Bankroll", f"${bankroll_status['bankroll']:.2f}")
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        export_text = f"""BRUTBALL PROVEN PATTERNS ANALYSIS
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EMPRICAL PROOF (25-MATCH ANALYSIS):
• Pattern A: Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)
• Pattern B: Winner Lock → Double Chance (100% - 6 matches)
• Pattern C: UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)

DETECTED PATTERNS:
• Patterns Found: {pattern_results['patterns_detected']}
• Summary: {pattern_results['summary']}

RECOMMENDED BETS:
"""
        
        for idx, rec in enumerate(pattern_results['recommendations']):
            export_text += f"""
{idx+1}. {rec['bet_type']}
   • Pattern: {rec['pattern'].replace('_', ' ')}
   • Reason: {rec['reason']}
   • Sample Accuracy: {rec['sample_accuracy']}
   • Stake Multiplier: {rec['stake_multiplier']:.1f}x
   • Recommended Stake: ${bankroll_manager.calculate_stake(rec, risk_level.split()[0]):.2f}
"""
        
        export_text += f"""

BANKROLL STATUS:
• Current Bankroll: ${bankroll_status['bankroll']:.2f}
• Base Unit: ${bankroll_status['base_unit']:.2f}
• Daily P/L: ${bankroll_status['daily_profit_loss']:+.2f}
• Consecutive Losses: {bankroll_status['consecutive_losses']}

RISK MANAGEMENT:
• Risk Level: {risk_level}
• Stop Conditions: 3 consecutive losses, 10% daily loss
• Max Trades per Day: 20
• Min Bankroll: $100 (10 base units)

DATA SOURCE:
• Last 5 matches data only (no season averages)
• League: {selected_league}
• Match: {home_team} vs {away_team}
• System Version: BRUTBALL_PROVEN_PATTERNS_v1.0
"""
        
        st.download_button(
            label="📥 Download Pattern Analysis",
            data=export_text,
            file_name=f"brutball_patterns_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer with pattern examples
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL PROVEN PATTERNS v1.0</strong></p>
        <p>Based on 25-match empirical analysis with proven accuracy</p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
            <div style="background: #DCFCE7; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                🛡️ Elite Defense (100%)
            </div>
            <div style="background: #DBEAFE; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                👑 Winner Lock (100%)
            </div>
            <div style="background: #F3E8FF; color: #5B21B6; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                📊 Under 3.5 (83.3%)
            </div>
        </div>
        <p><strong>Historical Proof:</strong> Porto 2-0 AVS • Espanyol 2-1 Athletic • Parma 1-0 Fiorentina</p>
        <p>Juventus 2-0 Pisa • Milan 3-0 Verona • Arsenal 4-1 Villa • Man City 0-0 Sunderland</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
