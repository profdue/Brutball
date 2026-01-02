import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime  # ADD THIS IMPORT
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

# =================== FIXED: TEAM NAME FOR UNDER 1.5 ===================
def get_team_under_15_name(recommendation: Dict, home_team: str, away_team: str) -> str:
    """
    FIXED: Get the correct team name for UNDER 1.5 bets
    
    For ELITE_DEFENSE_UNDER_1_5 pattern:
    - If HOME is elite defense → Bet: AWAY to score UNDER 1.5
    - If AWAY is elite defense → Bet: HOME to score UNDER 1.5
    """
    if recommendation['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
        defensive_team = recommendation.get('defensive_team', '')
        
        # Determine which team is being bet on
        if defensive_team == home_team:
            # HOME is elite defense → Bet AWAY UNDER 1.5
            return away_team
        else:
            # AWAY is elite defense → Bet HOME UNDER 1.5
            return home_team
    else:
        return recommendation.get('team_to_bet', '')

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
        
        # FIXED: Get correct team name for UNDER 1.5
        if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
            team_to_display = get_team_under_15_name(rec, home_team, away_team)
            bet_description = f"{team_to_display} to score UNDER 1.5 goals"
        elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
            team_to_display = rec.get('team_to_bet', '')
            bet_description = f"{team_to_display} Double Chance (Win or Draw)"
        else:
            team_to_display = ''
            bet_description = rec.get('reason', '')
        
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
                    <div style="font-weight: 700; color: #374151; margin-bottom: 0.25rem; font-size: 1.1rem;">
                        {bet_description}
                    </div>
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
            
            <!-- FIXED: Clear TEAM_UNDER_1.5 naming -->
            {f'<div style="margin-top: 1rem; padding: 0.75rem; background: #DCFCE7; border-radius: 6px; border-left: 4px solid #16A34A;"><strong>🎯 CLEAR BETTING SIGNAL:</strong> Bet on <strong>{team_to_display}</strong> to score 0 or 1 goals</div>' if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5' else ''}
            
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
bankroll_manager = BankrollManager(initial_bankroll=10000.0) if 'BankrollManager' in globals() else None

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
    .team-under-15-highlight {
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #16A34A;
        margin: 1rem 0;
        text-align: center;
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
        <p><strong style="color: #16A34A;">Pattern A:</strong> Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)</p>
        <p><strong style="color: #2563EB;">Pattern B:</strong> Winner Lock → Double Chance (100% - 6 matches)</p>
        <p><strong style="color: #7C3AED;">Pattern C:</strong> UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)</p>
        <p><strong>🎯 CLEAR TEAM NAMES:</strong> "Team X to score UNDER 1.5 goals" - No confusion</p>
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
    
    # TEAM_UNDER_1.5 Explanation
    st.markdown("""
    <div class="team-under-15-highlight">
        <h4>🎯 TEAM_UNDER_1.5 EXPLANATION</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 2px solid #86EFAC;">
                <div style="font-weight: 700; color: #065F46; margin-bottom: 0.5rem;">IF HOME is Elite Defense</div>
                <div style="font-size: 1.2rem; color: #16A34A; font-weight: 700;">Bet: AWAY to score ≤1 goals</div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">Example: Porto (elite) vs AVS → Bet AVS UNDER 1.5</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 6px; border: 2px solid #86EFAC;">
                <div style="font-weight: 700; color: #065F46; margin-bottom: 0.5rem;">IF AWAY is Elite Defense</div>
                <div style="font-size: 1.2rem; color: #16A34A; font-weight: 700;">Bet: HOME to score ≤1 goals</div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">Example: AVS vs Porto (elite) → Bet AVS UNDER 1.5</div>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 0.75rem; background: #BBF7D0; border-radius: 6px;">
            <strong>📊 Elite Defense Definition:</strong> Team concedes ≤4 goals TOTAL in last 5 matches (avg ≤0.8/match)
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
        
        # Show TEAM_UNDER_1.5 summary
        elite_defense_patterns = [r for r in pattern_results['recommendations'] 
                                 if r['pattern'] == 'ELITE_DEFENSE_UNDER_1_5']
        
        if elite_defense_patterns:
            st.markdown("### 🎯 TEAM_UNDER_1.5 SUMMARY")
            
            for pattern in elite_defense_patterns:
                team_to_bet = get_team_under_15_name(pattern, home_team, away_team)
                defensive_team = pattern.get('defensive_team', '')
                
                st.markdown(f"""
                <div class="team-under-15-highlight">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 2rem;">🎯</div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #065F46;">
                                Bet: {team_to_bet} to score UNDER 1.5 goals
                            </div>
                            <div style="color: #374151;">
                                Because {defensive_team} has elite defense ({pattern.get('home_conceded', 0)}/5 goals conceded)
                            </div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; color: #6B7280;">Defensive Team</div>
                            <div style="font-size: 1.2rem; font-weight: 700; color: #16A34A;">{defensive_team}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.9rem; color: #6B7280;">Team to Bet</div>
                            <div style="font-size: 1.2rem; font-weight: 700; color: #DC2626;">{team_to_bet}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
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
            # FIXED: Get correct team name for export
            if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                team_name = get_team_under_15_name(rec, home_team, away_team)
                bet_desc = f"{team_name} to score UNDER 1.5 goals"
            elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                team_name = rec.get('team_to_bet', '')
                bet_desc = f"{team_name} Double Chance (Win or Draw)"
            else:
                team_name = ''
                bet_desc = rec.get('reason', '')
            
            export_text += f"""
{idx+1}. {rec['bet_type']}
   • Bet: {bet_desc}
   • Pattern: {rec['pattern'].replace('_', ' ')}
   • Reason: {rec['reason']}
   • Sample Accuracy: {rec['sample_accuracy']}
   • Stake Multiplier: {rec['stake_multiplier']:.1f}x
"""
        
        # Add TEAM_UNDER_1.5 summary
        if elite_defense_patterns:
            export_text += f"""

TEAM_UNDER_1.5 SUMMARY:
"""
            for pattern in elite_defense_patterns:
                team_to_bet = get_team_under_15_name(pattern, home_team, away_team)
                defensive_team = pattern.get('defensive_team', '')
                export_text += f"""
• Bet {team_to_bet} to score 0 or 1 goals
  - Because {defensive_team} has elite defense ({pattern.get('home_conceded', 0)} goals in last 5 matches)
  - Defense gap: +{pattern.get('defense_gap', 0)} goals vs opponent
  - Historical evidence: {pattern['sample_accuracy']}
"""
        
        export_text += f"""

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
        <p>🎯 <strong>CLEAR TEAM NAMES FOR UNDER 1.5 BETS:</strong> "Team X to score 0 or 1 goals"</p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
            <div style="background: #DCFCE7; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                🛡️ Elite Defense → Bet Opponent UNDER 1.5
            </div>
            <div style="background: #DBEAFE; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                👑 Winner Lock → Bet Double Chance
            </div>
            <div style="background: #F3E8FF; color: #5B21B6; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                📊 Pattern Present → Bet UNDER 3.5
            </div>
        </div>
        <p><strong>Historical Proof:</strong> Porto 2-0 AVS • Espanyol 2-1 Athletic • Parma 1-0 Fiorentina</p>
        <p>Juventus 2-0 Pisa • Milan 3-0 Verona • Arsenal 4-1 Villa • Man City 0-0 Sunderland</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
