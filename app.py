import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== STATE & DURABILITY CLASSIFIER IMPORT ===================
try:
    from match_state_classifier import get_complete_classification, format_reliability_badge, format_durability_indicator
    STATE_CLASSIFIER_AVAILABLE = True
except ImportError:
    STATE_CLASSIFIER_AVAILABLE = False
    get_complete_classification = None
    format_reliability_badge = None
    format_durability_indicator = None

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

MARKET_THRESHOLDS = {
    'WINNER': {
        'opponent_xg_max': 1.1,
        'recent_concede_max': None,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,
        'recent_concede_max': 0.8,
        'state_flip_failures': 3,
        'enforcement_methods': 2,
        'urgency_required': False
    },
    'TEAM_NO_SCORE': {
        'opponent_xg_max': 0.6,
        'recent_concede_max': 0.6,
        'state_flip_failures': 4,
        'enforcement_methods': 3,
        'urgency_required': False
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,
        'recent_concede_max': 1.0,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False
    }
}

TOTALS_LOCK_CONFIG = {
    'home_goals_threshold': TOTALS_LOCK_THRESHOLD,
    'away_goals_threshold': TOTALS_LOCK_THRESHOLD,
    'both_teams_required': True,
    'trend_based': True,
    'capital_multiplier': 2.0
}

CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,
    'LOCK_MODE': 2.0,
}

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.2 - STATE PRESERVATION LAW",
    page_icon="⚖️🔒📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'country': 'England',
        'color': '#3B82F6'
    },
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'country': 'Spain',
        'color': '#EF4444'
    },
    'Bundesliga': {
        'filename': 'bundesliga.csv',
        'display_name': '🇩🇪 Bundesliga',
        'country': 'Germany',
        'color': '#000000'
    },
    'Serie A': {
        'filename': 'serie_a.csv',
        'display_name': '🇮🇹 Serie A',
        'country': 'Italy',
        'color': '#10B981'
    },
    'Ligue 1': {
        'filename': 'ligue_1.csv',
        'display_name': '🇫🇷 Ligue 1',
        'country': 'France',
        'color': '#8B5CF6'
    },
    'Eredivisie': {
        'filename': 'eredivisie.csv',
        'display_name': '🇳🇱 Eredivisie',
        'country': 'Netherlands',
        'color': '#F59E0B'
    },
    'Primeira Liga': {
        'filename': 'premeira_portugal.csv',
        'display_name': '🇵🇹 Primeira Liga',
        'country': 'Portugal',
        'color': '#DC2626'
    },
    'Super Lig': {
        'filename': 'super_league.csv',
        'display_name': '🇹🇷 Super Lig',
        'country': 'Turkey',
        'color': '#E11D48'
    }
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
    .agency-state-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 4px solid #16A34A;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(22, 163, 74, 0.15);
    }
    .totals-lock-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 4px solid #0EA5E9;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.15);
    }
    .market-locked-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%);
        border: 3px solid #059669;
        margin: 1rem 0;
        text-align: left;
    }
    .market-totals-locked {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 3px solid #0EA5E9;
        margin: 1rem 0;
        text-align: left;
    }
    .market-available-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        margin: 1rem 0;
        text-align: left;
    }
    .market-unavailable-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border: 3px solid #9CA3AF;
        margin: 1rem 0;
        text-align: left;
        opacity: 0.7;
    }
    .capital-mode-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 700;
    }
    .edge-mode {
        background: #EFF6FF;
        color: #1E40AF;
        border: 3px solid #3B82F6;
    }
    .lock-mode {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        color: #166534;
        border: 3px solid #16A34A;
    }
    .totals-lock-mode {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        color: #0C4A6E;
        border: 3px solid #0EA5E9;
    }
    .gate-passed {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #16A34A;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .gate-failed {
        background: #FEF2F2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DC2626;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .trend-check {
        background: #E0F2FE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0EA5E9;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .state-classification-display {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 4px solid #F97316;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(249, 115, 22, 0.15);
    }
    .state-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 700;
        margin: 0.5rem;
    }
    .badge-stagnation {
        background: #0EA5E9;
        color: white;
        border: 2px solid #0284C7;
    }
    .badge-suppression {
        background: #16A34A;
        color: white;
        border: 2px solid #059669;
    }
    .badge-delayed {
        background: #F59E0B;
        color: white;
        border: 2px solid #D97706;
    }
    .badge-explosion {
        background: #EF4444;
        color: white;
        border: 2px solid #DC2626;
    }
    .badge-neutral {
        background: #6B7280;
        color: white;
        border: 2px solid #4B5563;
    }
    .read-only-badge {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
        font-size: 0.8rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .market-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .badge-state {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .badge-totals {
        background: #BAE6FD;
        color: #0C4A6E;
        border: 1px solid #7DD3FC;
    }
    .badge-locked {
        background: #A7F3D0;
        color: #065F46;
        border: 1px solid #10B981;
        font-weight: 800;
    }
    .badge-totals-locked {
        background: #7DD3FC;
        color: #0C4A6E;
        border: 1px solid #38BDF8;
        font-weight: 800;
    }
    .badge-noise {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
    }
    .agency-insight {
        background: #E0F2FE;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #38BDF8;
        margin: 1rem 0;
    }
    .totals-insight {
        background: #F0F9FF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #0EA5E9;
        margin: 1rem 0;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .metric-row-state {
        background: #F0FDF4;
        border-left: 3px solid #16A34A;
    }
    .metric-row-totals {
        background: #E0F2FE;
        border-left: 3px solid #0EA5E9;
    }
    .metric-row-agency {
        background: #E0F2FE;
        border-left: 3px solid #38BDF8;
    }
    .architecture-diagram {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        text-align: center;
    }
    .three-tier-architecture {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        margin: 2rem 0;
    }
    .tier-level {
        width: 300px;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        position: relative;
    }
    .tier-3 {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 3px solid #0EA5E9;
        color: #0C4A6E;
        font-weight: 900;
    }
    .tier-2 {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 3px solid #16A34A;
        color: #166534;
        font-weight: 700;
    }
    .tier-1 {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        color: #1E40AF;
    }
    .state-principle {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #38BDF8;
        margin: 1rem 0;
    }
    .state-bound-list {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #86EFAC;
        margin: 0.5rem 0;
    }
    .totals-lock-list {
        background: #E0F2FE;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #7DD3FC;
        margin: 0.5rem 0;
    }
    .noise-list {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #D1D5DB;
        margin: 0.5rem 0;
    }
    .trend-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .trend-good {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .trend-poor {
        background: #FEF3C7;
        color: #D97706;
        border: 1px solid #FCD34D;
    }
    .binary-gate {
        background: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #0EA5E9;
        margin: 1rem 0;
        text-align: center;
        font-weight: 700;
    }
    .strict-binary {
        background: #FFEDD5;
        padding: 0.5rem;
        border-radius: 6px;
        border: 2px solid #F97316;
        margin: 0.5rem 0;
        text-align: center;
    }
    .law-display {
        background: #FEFCE8;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #FACC15;
        margin: 1rem 0;
    }
    .preservation-law {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #F97316;
        margin: 1rem 0;
        font-weight: 700;
    }
    .read-only-note {
        background: #F0F9FF;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #0EA5E9;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #374151;
    }
    .perspective-display {
        background: #F0F9FF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #0EA5E9;
        margin: 1rem 0;
    }
    .perspective-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        margin: 0.75rem 0;
    }
    .perspective-home {
        border-left: 4px solid #3B82F6;
    }
    .perspective-away {
        border-left: 4px solid #EF4444;
    }
    .stay-out-badge {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #92400E;
        border: 2px solid #F59E0B;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .info-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    .info-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .info-value {
        font-size: 1.2rem;
        font-weight: 700;
    }
    .reliability-box {
        margin: 1rem 0;
        padding: 1rem;
        background: #F0F9FF;
        border-radius: 8px;
        border: 1px solid #BAE6FD;
    }
    </style>
""", unsafe_allow_html=True)

# =================== ENGINE CLASSES (KEEP THE SAME AS BEFORE) ===================
# [All the engine classes remain exactly the same - BrutballEdgeEngine, AgencyStateLockEngine, 
# TotalsLockEngine, BrutballIntegratedArchitecture]
# These are too long to include here but they should remain unchanged from your working version

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data with your CSV structure."""
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
        
        df = calculate_derived_metrics(df)
        
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['country'] = league_config['country']
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics from your CSV structure."""
    
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
    
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_total_goals_for'] = df['home_goals_scored'].replace(0, np.nan)
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_total_goals_for']
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_total_goals_for']
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_total_goals_for']
    
    df['away_total_goals_for'] = df['away_goals_scored'].replace(0, np.nan)
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_total_goals_for']
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_total_goals_for']
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_total_goals_for']
    
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application function with corrected HTML rendering."""
    
    # Header
    st.markdown('<div class="system-header">⚖️🔒📊 BRUTBALL INTEGRATED ARCHITECTURE v6.2</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>THREE-TIER SYSTEM WITH STATE PRESERVATION LAW</strong></p>
        <p>Tier 1: v6.0 Edge Detection • Tier 2: Agency-State Lock • Tier 3: Totals Lock</p>
        <p><strong>CRITICAL UPDATE:</strong> Gate 4A enforces that defensive markets require RECENT defensive proof</p>
        <p><strong>PRE-MATCH INTELLIGENCE:</strong> State & Durability Classification available for system protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # State Preservation Law Display
    st.markdown("""
    <div class="preservation-law">
        <h4>⚖️ STATE PRESERVATION LAW (v6.2)</h4>
        <div style="margin: 1rem 0; font-size: 1.1rem;">
            <strong>A state cannot be locked unless it can be PRESERVED.</strong>
        </div>
        <div style="margin: 0.5rem 0;">
            <strong>Gate 4A OVERRIDES Gates 1-3 for defensive markets.</strong>
        </div>
        <div style="margin: 0.5rem 0; font-size: 0.95rem;">
            Dominance ≠ Protection • Creation ≠ Suppression • Control ≠ Safety
        </div>
        <div style="margin-top: 1rem; padding: 0.75rem; background: #FEF3C7; border-radius: 6px;">
            <strong>Manchester United vs Wolves:</strong> Passed Gates 1-3 (creation), FAILED Gate 4A (preservation)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
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
                type="primary" if st.session_state.selected_league == league else "secondary"
            ):
                st.session_state.selected_league = league
    
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
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options)
    
    # Special test case button
    if home_team == "Manchester United" and away_team == "Wolves":
        st.markdown("""
        <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; border: 2px solid #F59E0B; margin: 1rem 0;">
            <strong>🧪 STATE PRESERVATION LAW TEST CASE</strong>
            <p>Manchester United vs Wolves is the empirical proof of State Preservation Law.</p>
            <p><strong>Expected Result:</strong> United may pass Winner lock, but MUST FAIL Clean Sheet/Team No Score locks.</p>
            <p><strong>Reason:</strong> United concedes 1.6 avg goals recently (last 5) → cannot preserve defensive states.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Execute analysis
    if st.button("⚡ EXECUTE INTEGRATED ANALYSIS v6.2", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average xG
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute integrated analysis
        result = BrutballIntegratedArchitecture.execute_integrated_analysis(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        # Get classification results
        classification_result = None
        if STATE_CLASSIFIER_AVAILABLE and get_complete_classification:
            try:
                classification_result = get_complete_classification(home_data, away_data)
                result['state_classification'] = classification_result
            except Exception as e:
                classification_result = {
                    'dominant_state': 'CLASSIFIER_ERROR',
                    'error': str(e),
                    'is_read_only': True
                }
                result['state_classification'] = classification_result
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 INTEGRATED SYSTEM VERDICT v6.2")
        
        # Capital mode display
        capital_mode = result['capital_mode']
        if result['has_totals_lock']:
            capital_display = "TOTALS LOCK MODE"
            capital_class = "totals-lock-mode"
        elif capital_mode == 'LOCK_MODE':
            capital_display = "LOCK MODE"
            capital_class = "lock-mode"
        else:
            capital_display = "EDGE MODE"
            capital_class = "edge-mode"
        
        capital_html = f"""
        <div class="capital-mode-box {capital_class}">
            <h2 style="margin: 0; font-size: 2rem;">{capital_display}</h2>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                Stake: <strong>{result['final_stake']:.2f}%</strong> ({result['v6_result']['stake_pct']:.1f}% × {result['stake_multiplier']:.1f}x)
            </div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">
                {result['system_verdict']}
            </div>
        </div>
        """
        st.markdown(capital_html, unsafe_allow_html=True)
        
        # =================== STATE & DURABILITY CLASSIFICATION DISPLAY ===================
        if classification_result and 'state_classification' in result:
            st.markdown("#### 🔍 PRE-MATCH STRUCTURAL INTELLIGENCE (READ-ONLY)")
            
            # Get opponent under 1.5 data
            opponent_data = classification_result.get('opponent_under_15', {})
            home_perspective = opponent_data.get('home_perspective', {})
            away_perspective = opponent_data.get('away_perspective', {})
            
            # Perspective Display
            perspective_html = f"""
            <div class="perspective-display">
                <h4>📊 PERSPECTIVE-BASED ANALYSIS</h4>
                <p style="color: #374151; margin-bottom: 1rem;">"Opponent" depends on which team you're backing. All calculations use LAST 5 MATCHES only.</p>
                
                <div class="perspective-box perspective-home">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; color: #1E40AF;">BACKING HOME ({home_team})</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">Opponent = {away_team}</div>
                    </div>
                    <div style="color: #374151; margin-bottom: 0.5rem;">
                        {home_perspective.get('interpretation', 'N/A')}
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 0.5rem;">
                            {'✅' if home_perspective.get('opponent_under_15') else '❌'}
                        </div>
                        <div style="font-weight: 600; color: {'#16A34A' if home_perspective.get('opponent_under_15') else '#DC2626'};">
                            Signal: {'PRESENT' if home_perspective.get('opponent_under_15') else 'ABSENT'}
                        </div>
                    </div>
                </div>
                
                <div class="perspective-box perspective-away">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; color: #DC2626;">BACKING AWAY ({away_team})</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">Opponent = {home_team}</div>
                    </div>
                    <div style="color: #374151; margin-bottom: 0.5rem;">
                        {away_perspective.get('interpretation', 'N/A')}
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 0.5rem;">
                            {'✅' if away_perspective.get('opponent_under_15') else '❌'}
                        </div>
                        <div style="font-weight: 600; color: {'#16A34A' if away_perspective.get('opponent_under_15') else '#DC2626'};">
                            Signal: {'PRESENT' if away_perspective.get('opponent_under_15') else 'ABSENT'}
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(perspective_html, unsafe_allow_html=True)
            
            # Map state to badge class
            state_badge_classes = {
                'TERMINAL_STAGNATION': 'badge-stagnation',
                'ASYMMETRIC_SUPPRESSION': 'badge-suppression',
                'DELAYED_RELEASE': 'badge-delayed',
                'FORCED_EXPLOSION': 'badge-explosion',
                'NEUTRAL': 'badge-neutral',
                'CLASSIFIER_ERROR': 'badge-neutral'
            }
            
            dominant_state = classification_result.get('dominant_state', 'NEUTRAL')
            badge_class = state_badge_classes.get(dominant_state, 'badge-neutral')
            
            # Get classification values
            totals_durability = classification_result.get('totals_durability', 'NONE')
            under_suggestion = classification_result.get('under_suggestion', 'No Under recommendation')
            
            # Format durability indicator
            if format_durability_indicator:
                durability_display = format_durability_indicator(totals_durability)
            else:
                durability_display = totals_durability
            
            # State classification display
            classification_html = f"""
            <div class="state-classification-display">
                <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                    <span class="state-badge {badge_class}">{dominant_state.replace('_', ' ')}</span>
                    <span class="read-only-badge">READ-ONLY</span>
                </div>
                
                <div class="info-grid">
                    <div class="info-box">
                        <div class="info-label">Totals Durability</div>
                        <div class="info-value" style="color: #1E40AF;">{durability_display}</div>
                        <div class="info-label" style="font-size: 0.85rem; margin-top: 0.25rem;">Based on last 5 matches only</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">Under Market Suggestion</div>
                        <div class="info-value" style="color: #059669;">{under_suggestion}</div>
                        <div class="info-label" style="font-size: 0.85rem; margin-top: 0.25rem;">Informational guidance only</div>
                    </div>
                </div>
                
                <div class="reliability-box">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.1rem; font-weight: 600;">Reliability Assessment</div>
                    </div>
            """
            
            # Add reliability badge
            if format_reliability_badge and classification_result.get('reliability_home'):
                reliability_html = format_reliability_badge(classification_result['reliability_home'])
                classification_html += f'<div style="text-align: center; margin-bottom: 0.5rem;">{reliability_html}</div>'
            
            classification_html += """
                    <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem; text-align: center;">
                        Based on durability, under suggestions, and opponent defense
                    </div>
                </div>
                
                <div style="color: #DC2626; font-size: 0.85rem; margin-top: 1rem; padding: 0.75rem; background: #FEF2F2; border-radius: 6px;">
                    <strong>⚠️ IMPORTANT:</strong> This classification is 100% read-only and informational only. Does NOT affect betting logic, stakes, or existing tiers.
                </div>
            </div>
            """
            
            st.markdown(classification_html, unsafe_allow_html=True)
        
        # Check for State Preservation failures
        preservation_failures = []
        for market in ['CLEAN_SHEET', 'TEAM_NO_SCORE']:
            if result['market_status'][market].get('failed_on_preservation', False):
                preservation_failures.append(market.replace('_', ' '))
        
        if preservation_failures:
            stay_out_html = f"""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div class="stay-out-badge">
                    ⚠️ STAY-OUT RECOMMENDED
                </div>
                <div style="color: #92400E; margin-top: 0.5rem; font-size: 0.9rem;">
                    {', '.join(preservation_failures)} failed State Preservation Law
                </div>
                <div style="color: #6B7280; font-size: 0.85rem; margin-top: 0.25rem;">
                    Recent defensive proof insufficient for these markets
                </div>
            </div>
            """
            st.markdown(stay_out_html, unsafe_allow_html=True)
        
        # v6.0 Edge Detection Display
        st.markdown("#### 🔍 TIER 1: v6.0 EDGE DETECTION")
        
        v6_result = result['v6_result']
        edge_html = f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #3B82F6; margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: #1E40AF; margin: 0;">{v6_result['primary_action']}</h3>
                    <p style="color: #6B7280; margin: 0.5rem 0 0 0;">{v6_result['secondary_logic']}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #3B82F6;">{v6_result['confidence']:.1f}/10</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Confidence</div>
                </div>
            </div>
        </div>
        """
        st.markdown(edge_html, unsafe_allow_html=True)
        
        # Agency-State Market Evaluation
        st.markdown("#### 🔐 TIER 2: AGENCY-STATE LOCKS v6.2")
        
        if result['has_agency_lock']:
            strongest = result['strongest_market']
            agency_html = f"""
            <div class="agency-state-display">
                <h3 style="color: #16A34A; margin: 0 0 1rem 0;">AGENCY-STATE CONTROL DETECTED</h3>
                <div style="font-size: 1.2rem; color: #059669; margin-bottom: 0.5rem;">
                    {len(result['agency_locked_markets'])} market(s) structurally locked
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Strongest lock: <strong>{strongest['market']}</strong> (Δ = {strongest['delta']:+.2f})
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
            """
            
            for market_info in result['agency_locked_markets']:
                agency_html += f'<span class="market-badge badge-locked">{market_info["market"]}</span>'
            
            agency_html += """
                </div>
            </div>
            """
            st.markdown(agency_html, unsafe_allow_html=True)
            
            # Show defensive preservation status
            defensive_locks = [m for m in result['agency_locked_markets'] if m['market'] != 'WINNER']
            if defensive_locks:
                st.markdown("""
                <div class="gate-passed">
                    <strong>✅ STATE PRESERVATION LAW SATISFIED</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        All defensive locks passed Gate 4A (recent defensive proof confirmed)
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            no_agency_html = """
            <div style="background: #F3F4F6; padding: 2rem; border-radius: 12px; border: 2px solid #D1D5DB; text-align: center; margin: 1.5rem 0;">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO AGENCY-STATE LOCKS DETECTED</h3>
                <div style="color: #374151;">
                    No markets meet agency-suppression criteria
                </div>
            </div>
            """
            st.markdown(no_agency_html, unsafe_allow_html=True)
            
            # Check if any failed on State Preservation
            preservation_failures_display = []
            for market in ['CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
                if result['market_status'][market].get('failed_on_preservation', False):
                    preservation_failures_display.append(market.replace('_', ' '))
            
            if preservation_failures_display:
                preservation_html = f"""
                <div class="gate-failed">
                    <strong>❌ STATE PRESERVATION LAW FAILURES DETECTED</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        Markets failed on recent defensive proof: {', '.join(preservation_failures_display)}
                    </p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #DC2626;">
                        Manchester United vs Wolves pattern detected
                    </p>
                </div>
                """
                st.markdown(preservation_html, unsafe_allow_html=True)
        
        # Totals Lock Display
        st.markdown("#### 📊 TIER 3: TOTALS LOCK")
        
        if result['has_totals_lock']:
            trend_data = result['totals_result']['trend_data']
            totals_html = f"""
            <div class="totals-lock-display">
                <h3 style="color: #0EA5E9; margin: 0 0 1rem 0;">TOTALS LOCK DETECTED</h3>
                <div style="font-size: 1.2rem; color: #0284C7; margin-bottom: 0.5rem;">
                    Dual Low-Offense Trend Confirmed
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Both teams exhibit sustained low-scoring trends
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                    <span class="market-badge badge-totals-locked">TOTALS ≤2.5 LOCKED</span>
                </div>
            </div>
            
            <div class="trend-check">
                <h4 style="color: #0C4A6E; margin: 0 0 0.5rem 0;">📊 LAST 5 MATCHES TREND DATA</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <div style="font-weight: 600; color: #374151;">{home_team}</div>
                        <div style="font-size: 1.5rem; color: #0EA5E9; font-weight: 700;">{trend_data['home_last5_avg']:.2f}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">avg goals (last 5)</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #374151;">{away_team}</div>
                        <div style="font-size: 1.5rem; color: #0EA5E9; font-weight: 700;">{trend_data['away_last5_avg']:.2f}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">avg goals (last 5)</div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 0.75rem; background: #F0F9FF; border-radius: 6px;">
                    <strong>Condition Met:</strong> Both ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5 matches)
                </div>
            </div>
            """
            st.markdown(totals_html, unsafe_allow_html=True)
        else:
            no_totals_html = f"""
            <div style="background: #F3F4F6; padding: 2rem; border-radius: 12px; border: 2px solid #D1D5DB; text-align: center; margin: 1.5rem 0;">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO TOTALS LOCK DETECTED</h3>
                <div style="color: #374151;">
                    {result['totals_result']['reason']}
                </div>
            </div>
            """
            st.markdown(no_totals_html, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL INTEGRATED ARCHITECTURE v6.2</strong></p>
        <p>Three-Tier System with State Preservation Law</p>
        <p>Tier 1: v6.0 Edge Detection • Tier 2: Agency-State Lock • Tier 3: Totals Lock</p>
        <p><strong>STATE PRESERVATION LAW:</strong> Gate 4A OVERRIDES Gates 1-3 for defensive markets</p>
        <p><strong>PRE-MATCH INTELLIGENCE:</strong> Perspective-sensitive, last-5 data only, read-only</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()