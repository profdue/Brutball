import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime
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
    """
    if recommendation['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
        defensive_team = recommendation.get('defensive_team', '')
        
        if defensive_team == home_team:
            return away_team
        else:
            return home_team
    else:
        return recommendation.get('team_to_bet', '')

# =================== DATA LOADING FUNCTIONS (RESTORED) ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare league data from CSV"""
    try:
        # League configuration
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
        
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple possible file locations
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
        df.attrs['country'] = league_config.get('country', '')
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
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

def extract_team_data(df: pd.DataFrame, team_name: str) -> Dict:
    """Extract team data from DataFrame"""
    if team_name not in df['team'].values:
        return {}
    
    team_row = df[df['team'] == team_name].iloc[0]
    return team_row.to_dict()

# =================== ENHANCED CSS WITH WRAPPER FIX ===================
st.markdown("""
    <style>
    /* Global wrapper for proper card containment */
    .brutball-card-wrapper {
        max-width: 1000px;
        margin: 0 auto;
        width: 100%;
    }
    
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
        width: 100%;
        box-sizing: border-box;
        overflow-wrap: break-word;
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
    .stake-display {
        background: #FFFBEB;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #F59E0B;
        margin: 1rem 0;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }
    .team-under-15-highlight {
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #16A34A;
        margin: 1rem 0;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }
    .under-35-highlight {
        background: linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #7C3AED;
        margin: 1rem 0;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }
    
    /* League selection buttons */
    .league-btn {
        transition: all 0.3s ease;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        text-align: center;
        cursor: pointer;
    }
    .league-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Responsive grid fixes */
    @media (max-width: 768px) {
        .system-header {
            font-size: 1.8rem;
        }
        .pattern-card {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# =================== PROVEN PATTERNS DISPLAY (FIXED WITH WRAPPER) ===================
def display_proven_patterns_results(pattern_results: Dict, home_team: str, away_team: str):
    """Beautiful display for proven pattern detection results WITH PROPER WRAPPING"""
    
    if not pattern_results or pattern_results['patterns_detected'] == 0:
        st.markdown("""
        <div class="brutball-card-wrapper">
            <div style="background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); 
                    padding: 2.5rem; border-radius: 12px; border: 3px dashed #9CA3AF; 
                    text-align: center; margin: 1.5rem 0; box-sizing: border-box;">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">🎯 NO PROVEN PATTERNS DETECTED</h3>
                <div style="color: #374151; margin-bottom: 1rem;">
                    This match doesn't meet the criteria for our 25-match empirical patterns
                </div>
                <div style="font-size: 0.9rem; color: #6B7280;">
                    Patterns require Elite Defense (≤4 goals last 5) or Winner Lock detection
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Header with pattern count
    patterns_count = pattern_results['patterns_detected']
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div style="background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%); 
                padding: 2rem; border-radius: 12px; border: 4px solid #F97316; 
                text-align: center; margin: 1.5rem 0; box-shadow: 0 6px 16px rgba(249, 115, 22, 0.15);
                box-sizing: border-box; width: 100%;">
            <h2 style="color: #9A3412; margin: 0 0 0.5rem 0;">🎯 PROVEN PATTERNS DETECTED</h2>
            <div style="font-size: 1.5rem; color: #EA580C; font-weight: 700; margin-bottom: 0.5rem;">
                {patterns_count} Pattern(s) Found
            </div>
            <div style="color: #92400E; font-size: 0.9rem;">
                Based on 25-match empirical analysis (100% & 83.3% accuracy)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display each recommendation in beautiful cards WITH PROPER WRAPPING
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
            bet_description = f"Total UNDER 3.5 goals"
        
        # Create beautiful card WITH PROPER WRAPPER
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div style="
                background: {style['bg_color']}; 
                padding: 1.5rem; 
                border-radius: 10px; 
                border: 3px solid {style['border_color']}; 
                margin: 1rem 0;
                box-sizing: border-box;
                width: 100%;
                overflow-wrap: break-word;
            ">
                
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem;">{style['emoji']}</span>
                            <h3 style="color: {style['title_color']}; margin: 0;">{rec['bet_type']}</h3>
                        </div>
                        <div style="font-weight: 700; color: #374151; margin-bottom: 0.25rem; font-size: 1.1rem;">
                            {bet_description}
                        </div>
                        <div style="color: #6B7280; font-size: 0.9rem;">{rec['reason']}</div>
                    </div>
                    <div style="text-align: right; min-width: 100px;">
                        <div style="background: {style['badge_color']}; color: white; padding: 0.25rem 0.75rem; 
                                border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block;">
                            {rec['stake_multiplier']:.1f}x
                        </div>
                        <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">Stake Multiplier</div>
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.7); padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap;">
                        <div style="margin-bottom: 0.5rem;">
                            <div style="font-size: 0.85rem; color: #6B7280;">Pattern</div>
                            <div style="font-weight: 600; color: {style['title_color']};">{rec['pattern'].replace('_', ' ')}</div>
                        </div>
                        <div style="margin-bottom: 0.5rem;">
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
                {'<div style="margin-top: 1rem; padding: 0.75rem; background: #DCFCE7; border-radius: 6px; border-left: 4px solid #16A34A;"><strong>🎯 CLEAR BETTING SIGNAL:</strong> Bet on <strong>' + team_to_display + '</strong> to score 0 or 1 goals</div>' if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5' else ''}
                
            </div>
        </div>
        """, unsafe_allow_html=True)

# =================== MAIN APPLICATION (WITH CSV INTEGRATION RESTORED) ===================
def main():
    """Main application with Proven Pattern Detection"""
    
    # Header with pattern detection emphasis
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL INTEGRATED v6.3 + PROVEN PATTERNS</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; margin-bottom: 2rem; font-size: 0.95rem;">
            <p><strong>THREE PROVEN PATTERNS FROM 25-MATCH EMPIRICAL ANALYSIS</strong></p>
            <p><strong style="color: #16A34A;">Pattern A:</strong> Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)</p>
            <p><strong style="color: #2563EB;">Pattern B:</strong> Winner Lock → Double Chance (100% - 6 matches)</p>
            <p><strong style="color: #7C3AED;">Pattern C:</strong> UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)</p>
            <p><strong>🎯 CLEAR TEAM NAMES:</strong> "Team X to score UNDER 1.5 goals" - No confusion</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'pattern_results' not in st.session_state:
        st.session_state.pattern_results = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
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
    
    cols = st.columns(4)
    leagues = list(LEAGUES.keys())
    
    for idx, league in enumerate(leagues):
        col_idx = idx % 4
        with cols[col_idx]:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary",
                key=f"league_btn_{league}"
            ):
                st.session_state.selected_league = league
                st.session_state.analysis_complete = False
                st.session_state.df = None
                st.rerun()
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data if not already loaded
    if st.session_state.df is None:
        with st.spinner(f"Loading {config['display_name']} data..."):
            df = load_and_prepare_data(selected_league)
            if df is not None:
                st.session_state.df = df
                st.success(f"✅ Loaded {len(df)} teams from {config['display_name']}")
            else:
                st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
                return
    
    df = st.session_state.df
    
    if df is None:
        st.error("No data available. Please select a league.")
        return
    
    # Team selection from CSV data
    st.markdown("### 🏟️ Match Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Get sorted list of teams from CSV
        teams = sorted(df['team'].unique())
        home_team = st.selectbox("Home Team", teams, key="home_team_select")
    
    with col2:
        # Filter out home team from away options
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Show team stats
    with st.expander("📊 View Team Stats", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if home_team in df['team'].values:
                home_data = extract_team_data(df, home_team)
                st.write(f"**{home_team} (Last 5 matches):**")
                st.write(f"- Goals Scored: {home_data.get('goals_scored_last_5', 'N/A')}")
                st.write(f"- Goals Conceded: {home_data.get('goals_conceded_last_5', 'N/A')}")
                if home_data.get('goals_conceded_last_5'):
                    avg_conceded = home_data['goals_conceded_last_5'] / 5
                    elite_status = "✅ ELITE DEFENSE" if home_data['goals_conceded_last_5'] <= 4 else "❌ Not Elite"
                    st.write(f"- Avg Conceded: {avg_conceded:.2f} goals/match")
                    st.write(f"- Status: {elite_status}")
        
        with col2:
            if away_team in df['team'].values:
                away_data = extract_team_data(df, away_team)
                st.write(f"**{away_team} (Last 5 matches):**")
                st.write(f"- Goals Scored: {away_data.get('goals_scored_last_5', 'N/A')}")
                st.write(f"- Goals Conceded: {away_data.get('goals_conceded_last_5', 'N/A')}")
                if away_data.get('goals_conceded_last_5'):
                    avg_conceded = away_data['goals_conceded_last_5'] / 5
                    elite_status = "✅ ELITE DEFENSE" if away_data['goals_conceded_last_5'] <= 4 else "❌ Not Elite"
                    st.write(f"- Avg Conceded: {avg_conceded:.2f} goals/match")
                    st.write(f"- Status: {elite_status}")
    
    # Execute analysis button
    if st.button("⚡ DETECT PROVEN PATTERNS", type="primary", use_container_width=True, key="detect_patterns"):
        
        # Extract data from CSV
        home_data = extract_team_data(df, home_team)
        away_data = extract_team_data(df, away_team)
        
        if not home_data or not away_data:
            st.error("Could not extract team data from CSV")
            return
        
        # Prepare match metadata
        match_metadata = {
            'home_team': home_team,
            'away_team': away_team,
            'winner_lock_detected': False,
            'winner_lock_team': '',
            'winner_delta_value': 0
        }
        
        # Run pattern detection using actual CSV data
        try:
            pattern_results = ProvenPatternDetector.generate_all_patterns(
                home_data, away_data, match_metadata
            )
            
            # Store results
            st.session_state.pattern_results = pattern_results
            st.session_state.analysis_complete = True
            st.session_state.current_home_team = home_team
            st.session_state.current_away_team = away_team
            
            st.success(f"✅ Analysis complete! Found {pattern_results['patterns_detected']} pattern(s)")
            
        except Exception as e:
            st.error(f"❌ Pattern detection error: {str(e)}")
            st.info("Make sure your CSV has 'goals_conceded_last_5' column for both teams")
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.pattern_results:
        pattern_results = st.session_state.pattern_results
        home_team = st.session_state.current_home_team
        away_team = st.session_state.current_away_team
        
        # Display Proven Patterns
        st.markdown("### 🎯 PROVEN PATTERN DETECTION RESULTS")
        display_proven_patterns_results(pattern_results, home_team, away_team)
        
        # Show summaries for both patterns
        if pattern_results['patterns_detected'] > 0:
            st.markdown("### 📋 PATTERN SUMMARY")
            
            # TEAM_UNDER_1.5 Summary
            elite_defense_patterns = [r for r in pattern_results['recommendations'] 
                                     if r['pattern'] == 'ELITE_DEFENSE_UNDER_1_5']
            
            for pattern in elite_defense_patterns:
                team_to_bet = get_team_under_15_name(pattern, home_team, away_team)
                defensive_team = pattern.get('defensive_team', '')
                
                st.markdown(f"""
                <div class="brutball-card-wrapper">
                    <div style="background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
                            padding: 1rem; border-radius: 8px; border: 3px solid #16A34A; 
                            margin: 1rem 0; text-align: center; box-sizing: border-box;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                            <div style="font-size: 2rem;">🎯</div>
                            <div style="flex: 1;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: #065F46;">
                                    Bet: {team_to_bet} to score UNDER 1.5 goals
                                </div>
                                <div style="color: #374151;">
                                    Because {defensive_team} has elite defense ({pattern.get('home_conceded', 0)}/5 goals conceded)
                                </div>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Defensive Team</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #16A34A;">{defensive_team}</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Team to Bet</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #DC2626;">{team_to_bet}</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Defense Gap</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #059669;">+{pattern.get('defense_gap', 0)} goals</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # UNDER 3.5 Summary
            under_35_patterns = [r for r in pattern_results['recommendations'] 
                               if r['pattern'] == 'PATTERN_DRIVEN_UNDER_3_5']
            
            for pattern in under_35_patterns:
                st.markdown(f"""
                <div class="brutball-card-wrapper">
                    <div style="background: linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 100%);
                            padding: 1rem; border-radius: 8px; border: 3px solid #7C3AED; 
                            margin: 1rem 0; text-align: center; box-sizing: border-box;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                            <div style="font-size: 2rem;">📊</div>
                            <div style="flex: 1;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: #5B21B6;">
                                    Bet: TOTAL UNDER 3.5 goals
                                </div>
                                <div style="color: #374151;">
                                    Pattern-driven bet triggered by Elite Defense detection
                                </div>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Pattern Type</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #7C3AED;">Under 3.5</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Accuracy</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #059669;">83.3%</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.9rem; color: #6B7280;">Sample Size</div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: #7C3AED;">10/12 matches</div>
                            </div>
                        </div>
                        <div style="margin-top: 1rem; padding: 0.75rem; background: #F3E8FF; border-radius: 6px;">
                            <strong>🎯 LOGIC:</strong> When Elite Defense pattern is detected, total goals are ≤3 in 83.3% of cases
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

DATA SOURCE: CSV with last 5 matches data
• Home Team: {home_team}
• Away Team: {away_team}
• CSV File: {config['filename']}

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
                    bet_desc = f"Total UNDER 3.5 goals"
                
                export_text += f"""
{idx+1}. {rec['bet_type']}
   • Bet: {bet_desc}
   • Pattern: {rec['pattern'].replace('_', ' ')}
   • Reason: {rec['reason']}
   • Sample Accuracy: {rec['sample_accuracy']}
   • Stake Multiplier: {rec['stake_multiplier']:.1f}x
"""
            
            export_text += f"""

CSV DATA USED:
• {home_team}: {extract_team_data(df, home_team).get('goals_conceded_last_5', 'N/A')} goals conceded (last 5)
• {away_team}: {extract_team_data(df, away_team).get('goals_conceded_last_5', 'N/A')} goals conceded (last 5)

SYSTEM:
• Data Source: CSV files in 'leagues/' directory
• Pattern Detection: BRUTBALL_PROVEN_PATTERNS_v1.0
• Card Design: Beautiful responsive UI with wrapper containers
"""
            
            st.download_button(
                label="📥 Download Pattern Analysis",
                data=export_text,
                file_name=f"brutball_patterns_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="brutball-card-wrapper">
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
            <p><strong>Data Source:</strong> CSV files with last 5 matches data • <strong>Card Design:</strong> Beautiful responsive UI</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
