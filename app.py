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

# =================== PATTERN COMBINATION DISPLAY ===================
def display_pattern_combination(combination: str, desc: str):
    """Display pattern combination with appropriate styling"""
    
    combination_styles = {
        'BOTH_PATTERNS': {
            'emoji': '🎯',
            'bg_color': 'linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%)',
            'border_color': '#F97316',
            'color': '#9A3412',
            'title': 'BOTH PATTERNS PRESENT'
        },
        'ONLY_ELITE_DEFENSE': {
            'emoji': '🛡️',
            'bg_color': 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
            'border_color': '#16A34A',
            'color': '#065F46',
            'title': 'ONLY ELITE DEFENSE'
        },
        'ONLY_WINNER_LOCK': {
            'emoji': '👑',
            'bg_color': 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
            'border_color': '#2563EB',
            'color': '#1E40AF',
            'title': 'ONLY WINNER LOCK'
        },
        'NO_PATTERNS': {
            'emoji': '⚪',
            'bg_color': 'linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%)',
            'border_color': '#9CA3AF',
            'color': '#6B7280',
            'title': 'NO PROVEN PATTERNS'
        }
    }
    
    style = combination_styles.get(combination, combination_styles['NO_PATTERNS'])
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div style="
            background: {style['bg_color']};
            padding: 1.5rem;
            border-radius: 10px;
            border: 3px solid {style['border_color']};
            text-align: center;
            margin: 1.5rem 0;
            box-sizing: border-box;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{style['emoji']}</div>
            <h3 style="color: {style['color']}; margin: 0 0 0.5rem 0;">{style['title']}</h3>
            <div style="color: #374151;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION WITH PATTERN SEPARATION ===================
def main():
    """Main application with Pattern Separation"""
    
    # Header
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL v6.3 + PATTERN SEPARATION</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; margin-bottom: 2rem; font-size: 0.95rem;">
            <p><strong>🎯 PATTERNS APPEAR INDEPENDENTLY (25-MATCH ANALYSIS)</strong></p>
            <p><strong>🔍 Key Insight:</strong> Patterns can appear Alone, Together, or Neither</p>
            <p><strong>🔄 UNDER 3.5 Confidence:</strong> Varies based on which patterns are present</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pattern Combination Matrix
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
                padding: 1.5rem; border-radius: 10px; border: 3px solid #0EA5E9; 
                margin: 1rem 0; box-sizing: border-box;">
            <h4 style="color: #0C4A6E; margin: 0 0 1rem 0;">📊 PATTERN COMBINATION MATRIX</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem;">
                
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #F97316;">
                    <div style="font-weight: 700; color: #9A3412; margin-bottom: 0.5rem;">🎯 BOTH PATTERNS</div>
                    <div style="font-size: 0.9rem; color: #374151;">3 matches</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #059669;">100%</div>
                    <div style="font-size: 0.8rem; color: #6B7280;">UNDER 3.5 rate</div>
                </div>
                
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #16A34A;">
                    <div style="font-weight: 700; color: #065F46; margin-bottom: 0.5rem;">🛡️ ONLY ELITE DEFENSE</div>
                    <div style="font-size: 0.9rem; color: #374151;">5 matches</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #059669;">87.5%</div>
                    <div style="font-size: 0.8rem; color: #6B7280;">UNDER 3.5 rate</div>
                </div>
                
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #2563EB;">
                    <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">👑 ONLY WINNER LOCK</div>
                    <div style="font-size: 0.9rem; color: #374151;">3 matches</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #059669;">83.3%</div>
                    <div style="font-size: 0.8rem; color: #6B7280;">UNDER 3.5 rate</div>
                </div>
                
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #9CA3AF;">
                    <div style="font-weight: 700; color: #6B7280; margin-bottom: 0.5rem;">⚪ NO PATTERNS</div>
                    <div style="font-size: 0.9rem; color: #374151;">14 matches</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #DC2626;">57%</div>
                    <div style="font-size: 0.8rem; color: #6B7280;">UNDER 3.5 rate (No bet)</div>
                </div>
                
            </div>
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
    LEAGUES = {
        'Premier League': {'filename': 'premier_league.csv', 'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League'},
        'La Liga': {'filename': 'la_liga.csv', 'display_name': '🇪🇸 La Liga'},
        'Bundesliga': {'filename': 'bundesliga.csv', 'display_name': '🇩🇪 Bundesliga'},
        'Serie A': {'filename': 'serie_a.csv', 'display_name': '🇮🇹 Serie A'},
        'Ligue 1': {'filename': 'ligue_1.csv', 'display_name': '🇫🇷 Ligue 1'},
        'Eredivisie': {'filename': 'eredivisie.csv', 'display_name': '🇳🇱 Eredivisie'},
        'Primeira Liga': {'filename': 'premeira_portugal.csv', 'display_name': '🇵🇹 Primeira Liga'},
        'Super Lig': {'filename': 'super_league.csv', 'display_name': '🇹🇷 Super Lig'}
    }
    
    # Load CSV data
    def load_csv_data(league_name):
        """Load CSV data from GitHub"""
        try:
            config = LEAGUES[league_name]
            url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{config['filename']}"
            df = pd.read_csv(url)
            
            # Calculate derived metrics
            df['home_goals_scored'] = (
                df['home_goals_openplay_for'].fillna(0) +
                df['home_goals_counter_for'].fillna(0) +
                df['home_goals_setpiece_for'].fillna(0)
            )
            
            df['away_goals_scored'] = (
                df['away_goals_openplay_for'].fillna(0) +
                df['away_goals_counter_for'].fillna(0) +
                df['away_goals_setpiece_for'].fillna(0)
            )
            
            df['home_goals_conceded'] = (
                df['home_goals_openplay_against'].fillna(0) +
                df['home_goals_counter_against'].fillna(0) +
                df['home_goals_setpiece_against'].fillna(0)
            )
            
            df['away_goals_conceded'] = (
                df['away_goals_openplay_against'].fillna(0) +
                df['away_goals_counter_against'].fillna(0) +
                df['away_goals_setpiece_against'].fillna(0)
            )
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error loading {league_name}: {str(e)}")
            return None
    
    # League buttons
    st.markdown("### 🌍 League Selection")
    cols = st.columns(4)
    
    for idx, league in enumerate(LEAGUES.keys()):
        col_idx = idx % 4
        with cols[col_idx]:
            if st.button(
                LEAGUES[league]['display_name'],
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary",
                key=f"league_btn_{league}"
            ):
                with st.spinner(f"Loading {league} data..."):
                    df = load_csv_data(league)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.selected_league = league
                        st.session_state.analysis_complete = False
                        st.success(f"✅ Loaded {len(df)} teams")
                        st.rerun()
    
    # Get current data
    df = st.session_state.df
    
    if df is None:
        st.info("👆 Select a league to begin analysis")
        return
    
    # Team selection
    st.markdown("### 🏟️ Match Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        teams = sorted(df['team'].unique())
        home_team = st.selectbox("Home Team", teams, key="home_team_select")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Show team stats
    with st.expander("📊 View Team Defense Stats (Last 5 Matches)", expanded=False):
        col1, col2 = st.columns(2)
        
        home_row = df[df['team'] == home_team].iloc[0] if home_team in df['team'].values else None
        away_row = df[df['team'] == away_team].iloc[0] if away_team in df['team'].values else None
        
        with col1:
            if home_row is not None:
                goals_conceded = home_row.get('goals_conceded_last_5', 0)
                elite_status = "✅ ELITE DEFENSE" if goals_conceded <= 4 else "❌ Not Elite"
                st.write(f"**{home_team}:**")
                st.write(f"- Goals Conceded: {goals_conceded}")
                st.write(f"- Status: {elite_status}")
                st.write(f"- Avg per match: {goals_conceded/5:.2f}")
        
        with col2:
            if away_row is not None:
                goals_conceded = away_row.get('goals_conceded_last_5', 0)
                elite_status = "✅ ELITE DEFENSE" if goals_conceded <= 4 else "❌ Not Elite"
                st.write(f"**{away_team}:**")
                st.write(f"- Goals Conceded: {goals_conceded}")
                st.write(f"- Status: {elite_status}")
                st.write(f"- Avg per match: {goals_conceded/5:.2f}")
    
    # Execute analysis
    if st.button("⚡ ANALYZE PATTERN SEPARATION", type="primary", use_container_width=True):
        
        if home_row is None or away_row is None:
            st.error("Could not find team data")
            return
        
        # Prepare data
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
            'winner_lock_detected': False,  # Would come from your Agency-State system
            'winner_lock_team': '',
            'winner_delta_value': 0
        }
        
        # Run pattern detection with separation
        try:
            pattern_results = ProvenPatternDetector.generate_separated_patterns(
                home_data, away_data, match_metadata
            )
            
            st.session_state.pattern_results = pattern_results
            st.session_state.analysis_complete = True
            st.session_state.current_home_team = home_team
            st.session_state.current_away_team = away_team
            
            st.success(f"✅ Analysis complete!")
            
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.pattern_results:
        pattern_results = st.session_state.pattern_results
        home_team = st.session_state.current_home_team
        away_team = st.session_state.current_away_team
        
        # Display Pattern Combination
        st.markdown("### 🎯 PATTERN COMBINATION DETECTED")
        display_pattern_combination(
            pattern_results['pattern_combination'],
            pattern_results['combination_desc']
        )
        
        # Display recommendations
        if pattern_results['recommendations']:
            st.markdown("### 📊 RECOMMENDED BETS")
            
            for rec in pattern_results['recommendations']:
                # Determine card style
                style_map = {
                    'ELITE_DEFENSE_UNDER_1_5': {
                        'bg_color': 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
                        'border_color': '#16A34A',
                        'emoji': '🛡️',
                        'title_color': '#065F46'
                    },
                    'WINNER_LOCK_DOUBLE_CHANCE': {
                        'bg_color': 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
                        'border_color': '#2563EB',
                        'emoji': '👑',
                        'title_color': '#1E40AF'
                    },
                    'BOTH_PATTERNS_UNDER_3_5': {
                        'bg_color': 'linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%)',
                        'border_color': '#F97316',
                        'emoji': '🎯',
                        'title_color': '#9A3412'
                    },
                    'ELITE_DEFENSE_UNDER_3_5': {
                        'bg_color': 'linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%)',
                        'border_color': '#16A34A',
                        'emoji': '📊',
                        'title_color': '#065F46'
                    },
                    'WINNER_LOCK_UNDER_3_5': {
                        'bg_color': 'linear-gradient(135deg, #DBEAFE 0%, #93C5FD 100%)',
                        'border_color': '#2563EB',
                        'emoji': '📊',
                        'title_color': '#1E40AF'
                    }
                }
                
                style = style_map.get(rec['pattern'], style_map['ELITE_DEFENSE_UNDER_1_5'])
                
                # Get bet description
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    defensive_team = rec.get('defensive_team', '')
                    team_to_bet = away_team if defensive_team == home_team else home_team
                    bet_desc = f"{team_to_bet} to score UNDER 1.5 goals"
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    bet_desc = f"{rec.get('team_to_bet', 'Team')} Double Chance"
                else:
                    bet_desc = f"Total UNDER 3.5 goals"
                
                st.markdown(f"""
                <div class="brutball-card-wrapper">
                    <div style="
                        background: {style['bg_color']};
                        padding: 1.5rem;
                        border-radius: 10px;
                        border: 3px solid {style['border_color']};
                        margin: 1rem 0;
                        box-sizing: border-box;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 250px;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                    <span style="font-size: 1.5rem;">{style['emoji']}</span>
                                    <h3 style="color: {style['title_color']}; margin: 0;">{rec['bet_type']}</h3>
                                </div>
                                <div style="font-weight: 700; color: #374151; margin-bottom: 0.25rem; font-size: 1.1rem;">
                                    {bet_desc}
                                </div>
                                <div style="color: #6B7280; font-size: 0.9rem;">{rec['reason']}</div>
                            </div>
                            <div style="text-align: right; min-width: 100px;">
                                <div style="background: {style['border_color']}; color: white; padding: 0.25rem 0.75rem; 
                                        border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block;">
                                    {rec['stake_multiplier']:.1f}x
                                </div>
                                <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">Stake Multiplier</div>
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.7); padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap;">
                                <div style="margin-bottom: 0.5rem;">
                                    <div style="font-size: 0.85rem; color: #6B7280;">Pattern Type</div>
                                    <div style="font-weight: 600; color: {style['title_color']};">{rec['pattern'].replace('_', ' ')}</div>
                                </div>
                                <div style="margin-bottom: 0.5rem;">
                                    <div style="font-size: 0.85rem; color: #6B7280;">Sample Accuracy</div>
                                    <div style="font-weight: 600; color: #059669;">{rec['sample_accuracy']}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Pattern Statistics
        stats = pattern_results['pattern_stats']
        st.markdown("### 📈 PATTERN STATISTICS")
        
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
                    padding: 1.5rem; border-radius: 10px; border: 3px solid #0EA5E9; 
                    margin: 1rem 0; box-sizing: border-box;">
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
                        <div style="font-size: 1.5rem; font-weight: 700; color: {'#059669' if stats['under_35_decision'] else '#DC2626'}">
                            {'✅ Yes' if stats['under_35_decision'] else '❌ No'}
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Total Bets</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #7C3AED;">{stats['total_patterns_detected']}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
            <p><strong>🎯 BRUTBALL PATTERN SEPARATION v2.0</strong></p>
            <p><strong>Key Discovery:</strong> Patterns appear independently (Alone, Together, Neither)</p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
                <div style="background: #FFEDD5; color: #9A3412; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🎯 Both Patterns: 100% UNDER 3.5
                </div>
                <div style="background: #DCFCE7; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🛡️ Only Elite Defense: 87.5% UNDER 3.5
                </div>
                <div style="background: #DBEAFE; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    👑 Only Winner Lock: 83.3% UNDER 3.5
                </div>
            </div>
            <p><strong>Data Source:</strong> GitHub CSV files • <strong>Analysis:</strong> 25-match empirical study</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
