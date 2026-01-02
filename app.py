"""
COMPLETE BRUTBALL PATTERN DETECTION APP
Fully independent - no hardcoded teams or matches
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =================== IMPORT COMPLETE SYSTEM ===================
try:
    from match_state_classifier import (
        CompletePatternDetector,
        DataValidator,
        ResultFormatter,
        get_complete_classification
    )
    SYSTEM_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ System import error: {str(e)}")
    SYSTEM_AVAILABLE = False

# =================== GLOBAL CSS ===================
st.markdown("""
    <style>
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
    
    .tier-display {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 3px solid;
        box-sizing: border-box;
        width: 100%;
    }
    
    .tier-1 {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        border-color: #F97316;
    }
    
    .tier-2 {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-color: #16A34A;
    }
    
    .tier-3 {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-color: #2563EB;
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
    }
    
    .data-input-section {
        background: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E2E8F0;
        margin: 1rem 0;
    }
    
    .validation-error {
        background: #FEF2F2;
        color: #DC2626;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #FCA5A5;
        margin: 1rem 0;
    }
    
    .validation-success {
        background: #F0FDF4;
        color: #059669;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #86EFAC;
        margin: 1rem 0;
    }
    
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

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600)
def load_league_csv(league_name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load league CSV from GitHub"""
    try:
        url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}"
        df = pd.read_csv(url)
        
        # Ensure required columns exist
        required_cols = ['team', 'goals_conceded_last_5']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"CSV missing required columns: {missing_cols}")
            return None
        
        # Clean and prepare data
        df = df.fillna(0)
        
        # Add derived metrics if needed
        if 'goals_conceded_last_5' in df.columns:
            df['goals_conceded_last_5'] = pd.to_numeric(df['goals_conceded_last_5'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== DISPLAY FUNCTIONS ===================
def display_tier_system():
    """Display the three-tier system explanation"""
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; margin-bottom: 2rem; font-size: 0.95rem;">
            <h3>🎯 THREE-TIER PATTERN DETECTION SYSTEM</h3>
            <p><strong>Completely independent analysis based on input data only</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tier 1 Display
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div class="tier-display tier-1">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">🛡️</div>
                <div>
                    <h3 style="color: #9A3412; margin: 0;">TIER 1: ELITE DEFENSE</h3>
                    <div style="color: #374151;">Team concedes ≤4 goals in last 5 matches</div>
                </div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px;">
                <strong>Bet:</strong> Opponent to score UNDER 1.5 goals
                <br><strong>Confidence:</strong> 100% (8/8 matches)
                <br><strong>Condition:</strong> Defense gap > 2.0 vs opponent
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tier 2 Display
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div class="tier-display tier-2">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">👑</div>
                <div>
                    <h3 style="color: #065F46; margin: 0;">TIER 2: WINNER LOCK</h3>
                    <div style="color: #374151;">Agency-State system Winner Lock detection</div>
                </div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px;">
                <strong>Bet:</strong> Team Double Chance (Win or Draw)
                <br><strong>Confidence:</strong> 100% (6/6 matches)
                <br><strong>Source:</strong> External Agency-State system input
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tier 3 Display
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div class="tier-display tier-3">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">📊</div>
                <div>
                    <h3 style="color: #1E40AF; margin: 0;">TIER 3: UNDER 3.5 TIERS</h3>
                    <div style="color: #374151;">Confidence varies by pattern presence</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #F97316;">
                    <strong>Both Patterns:</strong> 100%
                    <br><small>3/3 matches</small>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #16A34A;">
                    <strong>Only Elite Defense:</strong> 87.5%
                    <br><small>7/8 matches</small>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #2563EB;">
                    <strong>Only Winner Lock:</strong> 83.3%
                    <br><small>5/6 matches</small>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_pattern_card(recommendation: Dict, home_team: str, away_team: str):
    """Display a pattern recommendation card"""
    formatter = ResultFormatter()
    style = formatter.get_pattern_style(recommendation['pattern'])
    
    # Get bet description
    if recommendation['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
        team_to_bet = formatter.get_team_under_15_name(recommendation, home_team, away_team)
        bet_desc = f"{team_to_bet} to score UNDER 1.5 goals"
    elif recommendation['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
        bet_desc = f"{recommendation.get('team_to_bet', 'Team')} Double Chance"
    else:
        bet_desc = f"Total UNDER 3.5 goals"
    
    # Format pattern name
    pattern_name = formatter.format_pattern_name(recommendation['pattern'])
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div class="pattern-card" style="border-color: {style['border_color']}; border-left: 6px solid {style['border_color']};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 250px;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">{style['emoji']}</span>
                        <h3 style="color: {style['color']}; margin: 0;">{recommendation['bet_type']}</h3>
                    </div>
                    <div style="font-weight: 700; color: #374151; margin-bottom: 0.25rem; font-size: 1.1rem;">
                        {bet_desc}
                    </div>
                    <div style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        {recommendation.get('reason', recommendation.get('condition_1', ''))}
                    </div>
                    <div style="font-size: 0.85rem; color: #4B5563;">
                        <strong>Pattern:</strong> {pattern_name}
                    </div>
                </div>
                <div style="text-align: right; min-width: 100px;">
                    <div style="background: {style['color']}; color: white; padding: 0.25rem 0.75rem; 
                            border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block;">
                        {recommendation['stake_multiplier']:.1f}x
                    </div>
                    <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">Stake Multiplier</div>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.7); padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap;">
                    <div style="margin-bottom: 0.5rem;">
                        <div style="font-size: 0.85rem; color: #6B7280;">Confidence</div>
                        <div style="font-weight: 600; color: {style['color']};">
                            {recommendation.get('confidence', recommendation.get('sample_accuracy', 'N/A'))}
                        </div>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <div style="font-size: 0.85rem; color: #6B7280;">Historical Accuracy</div>
                        <div style="font-weight: 600; color: #059669;">{recommendation.get('sample_accuracy', 'N/A')}</div>
                    </div>
                </div>
                
                {'<div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.1); font-size: 0.85rem; color: #DC2626;"><strong>⚠️ Warning:</strong> ' + recommendation.get('warning', '') + '</div>' if 'warning' in recommendation else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_pattern_combination(analysis_result: Dict):
    """Display pattern combination result"""
    stats = analysis_result['pattern_stats']
    
    combination_colors = {
        'BOTH_PATTERNS': {'color': '#9A3412', 'bg': '#FFEDD5', 'border': '#F97316'},
        'ONLY_ELITE_DEFENSE': {'color': '#065F46', 'bg': '#F0FDF4', 'border': '#16A34A'},
        'ONLY_WINNER_LOCK': {'color': '#1E40AF', 'bg': '#EFF6FF', 'border': '#2563EB'},
        'NO_PATTERNS': {'color': '#6B7280', 'bg': '#F3F4F6', 'border': '#9CA3AF'}
    }
    
    combo = stats['pattern_combination']
    colors = combination_colors.get(combo, combination_colors['NO_PATTERNS'])
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div style="
            background: {colors['bg']};
            padding: 2rem;
            border-radius: 10px;
            border: 3px solid {colors['border']};
            text-align: center;
            margin: 1.5rem 0;
            box-sizing: border-box;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{stats['combination_emoji']}</div>
            <h2 style="color: {colors['color']}; margin: 0 0 0.5rem 0;">
                {analysis_result['combination_desc'].upper()}
            </h2>
            <div style="color: #374151; font-size: 0.9rem;">
                {analysis_result['combination_desc']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION ===================
def main():
    """Complete independent pattern detection application"""
    
    if not SYSTEM_AVAILABLE:
        st.error("❌ System components not available. Check match_state_classifier.py")
        return
    
    # Header
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL COMPLETE TIER SYSTEM</div>', unsafe_allow_html=True)
    
    # Display tier system
    display_tier_system()
    
    # Initialize session state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # League configuration
    LEAGUES = {
        'Premier League': 'premier_league.csv',
        'La Liga': 'la_liga.csv',
        'Bundesliga': 'bundesliga.csv',
        'Serie A': 'serie_a.csv',
        'Ligue 1': 'ligue_1.csv',
        'Eredivisie': 'eredivisie.csv',
        'Primeira Liga': 'premeira_portugal.csv',
        'Super Lig': 'super_league.csv'
    }
    
    # League selection
    st.markdown("### 🌍 League Selection")
    cols = st.columns(4)
    
    for idx, league in enumerate(LEAGUES.keys()):
        col_idx = idx % 4
        with cols[col_idx]:
            if st.button(
                league,
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary",
                key=f"league_{league}"
            ):
                with st.spinner(f"Loading {league} data..."):
                    df = load_league_csv(league, LEAGUES[league])
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.selected_league = league
                        st.session_state.analysis_result = None
                        st.success(f"✅ Loaded {len(df)} teams")
                        st.rerun()
    
    df = st.session_state.df
    
    if df is None:
        st.info("👆 Select a league to begin analysis")
        return
    
    # Data Input Section
    st.markdown("### 📥 Match Data Input")
    
    with st.container():
        st.markdown('<div class="data-input-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Team selection from CSV
            teams = sorted(df['team'].unique())
            home_team = st.selectbox("Home Team", teams, key="home_select")
            
            # Get home team data
            home_row = df[df['team'] == home_team].iloc[0] if home_team in df['team'].values else None
            
            if home_row is not None:
                home_conceded = home_row.get('goals_conceded_last_5', 0)
                st.info(f"**{home_team} Defense:** {home_conceded} goals conceded (last 5)")
        
        with col2:
            # Away team selection
            away_options = [t for t in teams if t != home_team]
            away_team = st.selectbox("Away Team", away_options, key="away_select")
            
            # Get away team data
            away_row = df[df['team'] == away_team].iloc[0] if away_team in df['team'].values else None
            
            if away_row is not None:
                away_conceded = away_row.get('goals_conceded_last_5', 0)
                st.info(f"**{away_team} Defense:** {away_conceded} goals conceded (last 5)")
        
        # Winner Lock Input Section
        st.markdown("---")
        st.markdown("#### 👑 Winner Lock Data (From Agency-State System)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            winner_lock_detected = st.checkbox("Winner Lock Detected", value=False,
                                              help="Check if Agency-State system detected Winner Lock")
        
        with col2:
            if winner_lock_detected:
                lock_team = st.radio("Team with Winner Lock", ['Home', 'Away'], horizontal=True)
                delta_value = st.slider("Δ Value (Directional Dominance)", 0.1, 2.0, 0.8, 0.1,
                                       help="Agency-State system Δ value")
            else:
                lock_team = 'Home'
                delta_value = 0.0
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Prepare data for analysis
    if home_row is None or away_row is None:
        st.error("Could not load team data")
        return
    
    # Prepare data structures
    home_data = {
        'team_name': home_team,
        'goals_conceded_last_5': home_row.get('goals_conceded_last_5', 0)
    }
    
    away_data = {
        'team_name': away_team,
        'goals_conceded_last_5': away_row.get('goals_conceded_last_5', 0)
    }
    
    match_metadata = {
        'home_team': home_team,
        'away_team': away_team,
        'winner_lock_detected': winner_lock_detected,
        'winner_lock_team': 'home' if lock_team == 'Home' else 'away',
        'winner_delta_value': delta_value if winner_lock_detected else 0.0
    }
    
    # Validate data
    validator = DataValidator()
    validation_errors = validator.validate_match_data(home_data, away_data, match_metadata)
    
    if validation_errors:
        st.markdown("""
        <div class="brutball-card-wrapper">
            <div class="validation-error">
                <h4>❌ Data Validation Errors</h4>
        """, unsafe_allow_html=True)
        
        for error in validation_errors:
            st.write(f"• {error}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        return
    
    # Data validation passed
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div class="validation-success">
            <h4>✅ Data Validation Passed</h4>
            <p>All required data present for pattern detection</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyze button
    if st.button("⚡ RUN COMPLETE PATTERN ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Analyzing all tiers..."):
            try:
                # Run complete analysis
                analysis_result = CompletePatternDetector.analyze_match_complete(
                    home_data, away_data, match_metadata
                )
                
                # Store result
                st.session_state.analysis_result = analysis_result
                st.session_state.current_home_team = home_team
                st.session_state.current_away_team = away_team
                
                st.success(f"✅ Analysis complete! Found {analysis_result['pattern_stats']['total_patterns']} pattern(s)")
                
            except Exception as e:
                st.error(f"❌ Analysis error: {str(e)}")
    
    # Display results if available
    if st.session_state.analysis_result:
        analysis_result = st.session_state.analysis_result
        home_team = st.session_state.current_home_team
        away_team = st.session_state.current_away_team
        
        # Display pattern combination
        st.markdown("### 🎯 PATTERN COMBINATION DETECTED")
        display_pattern_combination(analysis_result)
        
        # Display recommendations
        if analysis_result['recommendations']:
            st.markdown("### 📊 RECOMMENDED BETS")
            
            for rec in analysis_result['recommendations']:
                display_pattern_card(rec, home_team, away_team)
        
        # Display statistics
        stats = analysis_result['pattern_stats']
        st.markdown("### 📈 ANALYSIS STATISTICS")
        
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
                    padding: 1.5rem; border-radius: 10px; border: 2px solid #E2E8F0; 
                    margin: 1rem 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Elite Defense</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #16A34A;">{stats['elite_defense_count']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Winner Lock</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #2563EB;">{stats['winner_lock_count']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">UNDER 3.5</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: {'#059669' if stats['under_35_present'] else '#DC2626'}">
                            {'✅ Yes' if stats['under_35_present'] else '❌ No'}
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Total Patterns</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #7C3AED;">{stats['total_patterns']}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tier summary
        if analysis_result['tier_summary']:
            st.markdown("### 🏆 TIER SUMMARY")
            
            for tier in analysis_result['tier_summary']:
                if "TIER 1" in tier:
                    color = "#F97316"
                elif "TIER 2" in tier:
                    color = "#16A34A"
                else:
                    color = "#2563EB"
                
                st.markdown(f"""
                <div class="brutball-card-wrapper">
                    <div style="background: white; padding: 1rem; border-radius: 8px; 
                            border-left: 4px solid {color}; margin: 0.5rem 0;">
                        <strong>{tier}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
            <p><strong>🎯 BRUTBALL COMPLETE TIER SYSTEM v1.0</strong></p>
            <p><strong>Fully Independent Analysis:</strong> No hardcoded teams or matches</p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
                <div style="background: #FFEDD5; color: #9A3412; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🛡️ Tier 1: Elite Defense Detection
                </div>
                <div style="background: #F0FDF4; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    👑 Tier 2: Winner Lock Integration
                </div>
                <div style="background: #EFF6FF; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    📊 Tier 3: Confidence-Tiered UNDER 3.5
                </div>
            </div>
            <p><strong>Data Source:</strong> GitHub CSV • <strong>Logic:</strong> Pure pattern detection</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
