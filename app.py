"""
COMPLETE BRUTBALL PATTERN DETECTION APP - PATTERN INDEPENDENT VERSION
Each pattern detected independently - No forced combinations
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =================== PATTERN-INDEPENDENT LOGIC ===================
class PatternIndependentDetector:
    """Detect patterns completely independently based on 25-match analysis"""
    
    @staticmethod
    def detect_all_patterns_independently(home_team: str, away_team: str, 
                                         home_conceded: int, away_conceded: int,
                                         winner_lock_info: Dict) -> Dict:
        """
        Each pattern detected independently from match data
        Returns dict with pattern presence and specific bets
        """
        
        patterns = {
            'has_elite_defense': False,
            'has_winner_lock': False,
            'elite_defense_bets': [],  # Can be 0, 1, or 2 bets (both directions)
            'winner_lock_bet': None,   # 0 or 1 bet
            'under_3_5_recommended': False,
            'under_3_5_confidence': None,
            'pattern_combination': 'NO_PATTERNS'
        }
        
        # ====================
        # 1. ELITE DEFENSE CHECK (BOTH DIRECTIONS - INDEPENDENT)
        # ====================
        
        elite_bets = []
        
        # Check HOME as defensive team
        if home_conceded <= 4:
            defense_gap = away_conceded - home_conceded
            if defense_gap > 2.0:
                patterns['has_elite_defense'] = True
                elite_bets.append({
                    'type': 'TEAM_UNDER_1_5',
                    'team_to_bet': away_team,
                    'defensive_team': home_team,
                    'bet_description': f"{away_team} to score UNDER 1.5 goals",
                    'reason': f"{home_team} has elite defense ({home_conceded}/5 conceded)",
                    'defense_gap': defense_gap
                })
        
        # Check AWAY as defensive team  
        if away_conceded <= 4:
            defense_gap = home_conceded - away_conceded
            if defense_gap > 2.0:
                patterns['has_elite_defense'] = True
                elite_bets.append({
                    'type': 'TEAM_UNDER_1_5',
                    'team_to_bet': home_team,
                    'defensive_team': away_team,
                    'bet_description': f"{home_team} to score UNDER 1.5 goals",
                    'reason': f"{away_team} has elite defense ({away_conceded}/5 conceded)",
                    'defense_gap': defense_gap
                })
        
        patterns['elite_defense_bets'] = elite_bets
        
        # ====================
        # 2. WINNER LOCK CHECK (INDEPENDENT)
        # ====================
        
        if winner_lock_info['detected']:
            patterns['has_winner_lock'] = True
            team_name = winner_lock_info['team_name']
            patterns['winner_lock_bet'] = {
                'type': 'DOUBLE_CHANCE',
                'team_to_bet': team_name,
                'bet_description': f"{team_name} Double Chance (Win or Draw)",
                'reason': f"Automated Winner Lock detection (Δ=+{winner_lock_info['delta_value']:.2f})",
                'delta_value': winner_lock_info['delta_value']
            }
        
        # ====================
        # 3. UNDER 3.5 DECISION (CONDITIONAL ON PATTERNS)
        # ====================
        
        # Decision matrix based on which patterns are present (from 25-match analysis)
        if patterns['has_elite_defense'] and patterns['has_winner_lock']:
            # BOTH patterns → HIGH confidence UNDER 3.5 (3/3 matches)
            patterns['under_3_5_recommended'] = True
            patterns['under_3_5_confidence'] = 'TIER_1_100'
            patterns['pattern_combination'] = 'BOTH_PATTERNS'
            
        elif patterns['has_elite_defense'] and not patterns['has_winner_lock']:
            # ONLY Elite Defense → MEDIUM confidence UNDER 3.5 (7/8 matches)
            patterns['under_3_5_recommended'] = True
            patterns['under_3_5_confidence'] = 'TIER_2_87_5'
            patterns['pattern_combination'] = 'ONLY_ELITE_DEFENSE'
            
        elif not patterns['has_elite_defense'] and patterns['has_winner_lock']:
            # ONLY Winner Lock → LOWER confidence UNDER 3.5 (5/6 matches)
            patterns['under_3_5_recommended'] = True
            patterns['under_3_5_confidence'] = 'TIER_3_83_3'
            patterns['pattern_combination'] = 'ONLY_WINNER_LOCK'
            
        else:
            # NO patterns → NO UNDER 3.5 bet (correct decision)
            patterns['under_3_5_recommended'] = False
            patterns['under_3_5_confidence'] = None
            patterns['pattern_combination'] = 'NO_PATTERNS'
        
        return patterns
    
    @staticmethod
    def generate_pattern_specific_recommendations(patterns: Dict) -> List[Dict]:
        """
        Generate recommendations based on WHICH patterns are present
        Each pattern type gets different stake/confidence
        """
        
        recommendations = []
        
        # ====================
        # A. ELITE DEFENSE BETS (if present)
        # ====================
        for bet in patterns['elite_defense_bets']:
            recommendations.append({
                'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                'bet_type': 'TEAM_UNDER_1_5',
                'bet_description': bet['bet_description'],
                'team_to_bet': bet['team_to_bet'],
                'defensive_team': bet['defensive_team'],
                'reason': bet['reason'],
                'stake_multiplier': 2.0,  # High confidence (100% in sample)
                'confidence': 'VERY_HIGH (100% historical)',
                'sample_accuracy': '8/8 matches',
                'display_priority': 1,
                'icon': '🛡️',
                'color': '#F97316'
            })
        
        # ====================
        # B. WINNER LOCK BET (if present)
        # ====================
        if patterns['winner_lock_bet']:
            recommendations.append({
                'pattern': 'WINNER_LOCK_DOUBLE_CHANCE',
                'bet_type': 'DOUBLE_CHANCE',
                'bet_description': patterns['winner_lock_bet']['bet_description'],
                'team_to_bet': patterns['winner_lock_bet']['team_to_bet'],
                'reason': patterns['winner_lock_bet']['reason'],
                'stake_multiplier': 1.5,  # Medium confidence (100% no-loss, 50% win)
                'confidence': 'VERY_HIGH (100% no-loss)',
                'sample_accuracy': '6/6 matches',
                'display_priority': 2,
                'icon': '🤖',
                'color': '#16A34A'
            })
        
        # ====================
        # C. UNDER 3.5 BET (if recommended)
        # ====================
        if patterns['under_3_5_recommended']:
            
            # Different messages based on which patterns triggered it
            if patterns['pattern_combination'] == 'BOTH_PATTERNS':
                reason = "Both Elite Defense and Winner Lock patterns present"
                stake = 1.2
                confidence = "TIER 1: 100% (3/3 matches)"
                icon = '🎯'
                color = '#9A3412'
                
            elif patterns['pattern_combination'] == 'ONLY_ELITE_DEFENSE':
                reason = "Elite Defense pattern present (scoring suppression)"
                stake = 1.0
                confidence = "TIER 2: 87.5% (7/8 matches)"
                icon = '🛡️'
                color = '#065F46'
                
            else:  # ONLY_WINNER_LOCK
                reason = "Winner Lock pattern present (market control)"
                stake = 0.9
                confidence = "TIER 3: 83.3% (5/6 matches)"
                icon = '🤖'
                color = '#1E40AF'
            
            recommendations.append({
                'pattern': f'UNDER_3_5_{patterns["under_3_5_confidence"]}',
                'bet_type': 'TOTAL_UNDER_3_5',
                'bet_description': "Total UNDER 3.5 goals",
                'reason': reason,
                'stake_multiplier': stake,
                'confidence': confidence,
                'sample_accuracy': patterns['under_3_5_confidence'],
                'display_priority': 3,
                'icon': icon,
                'color': color
            })
        
        # Sort by priority for display
        recommendations.sort(key=lambda x: x['display_priority'])
        
        return recommendations
    
    @staticmethod
    def generate_context_aware_display(recommendations: List[Dict], patterns: Dict) -> Dict:
        """
        Generate different display based on which patterns are present
        """
        
        if not recommendations:
            return {
                'title': '⚠️ No Proven Patterns Detected',
                'message': 'No Elite Defense or Winner Lock patterns found.',
                'advice': 'Avoid betting on this match with current system.',
                'color': '#6B7280',
                'icon': '🔍',
                'emoji': '⚪'
            }
        
        # Count pattern types
        elite_count = len([r for r in recommendations if 'ELITE_DEFENSE' in r['pattern']])
        winner_count = len([r for r in recommendations if 'WINNER_LOCK' in r['pattern']])
        under_35_count = len([r for r in recommendations if 'UNDER_3_5' in r['pattern']])
        
        # Generate context-specific display
        if elite_count > 0 and winner_count > 0:
            # Both patterns
            return {
                'title': '🎯 STRONG SIGNAL: Multiple Patterns Detected',
                'message': f'Found {elite_count} Elite Defense bet(s) + Winner Lock',
                'subtitle': 'High confidence across multiple markets',
                'color': '#9A3412',
                'icon': '🎯',
                'emoji': '🟠'
            }
        
        elif elite_count > 0:
            # Only Elite Defense
            return {
                'title': '🛡️ Elite Defense Pattern Detected',
                'message': f'Found {elite_count} Elite Defense bet(s)',
                'subtitle': 'Opponent scoring suppression expected',
                'color': '#065F46',
                'icon': '🛡️',
                'emoji': '🟢'
            }
        
        elif winner_count > 0:
            # Only Winner Lock
            return {
                'title': '🤖 Winner Lock Pattern Detected',
                'message': 'Controlled match expected - team unlikely to lose',
                'subtitle': 'Double Chance market recommended',
                'color': '#1E40AF',
                'icon': '🤖',
                'emoji': '🔵'
            }
        
        else:
            # Only UNDER 3.5 (shouldn't happen alone based on logic)
            return {
                'title': '📊 Secondary Pattern Detected',
                'message': 'UNDER 3.5 total goals recommended',
                'subtitle': 'Based on pattern presence in match',
                'color': '#7C3AED',
                'icon': '📊',
                'emoji': '🟣'
            }

# =================== AUTOMATED WINNER LOCK DETECTOR ===================
class AutomatedWinnerLockDetector:
    """Automatically detect Winner Lock from Agency-State system output"""
    
    @staticmethod
    def parse_agency_state_output(output_text: str, home_team: str, away_team: str) -> Dict:
        """
        Parse Agency-State system output to detect Winner Lock automatically
        """
        if not output_text or not isinstance(output_text, str):
            return {
                'detected': False,
                'team': None,
                'team_name': None,
                'delta_value': 0.0,
                'confidence': 'No Agency-State output provided',
                'raw_line': None
            }
        
        lines = [line.strip() for line in output_text.split('\n') if line.strip()]
        
        winner_lock_data = {
            'detected': False,
            'team': None,
            'team_name': None,
            'delta_value': 0.0,
            'confidence': 'Not detected',
            'raw_line': None
        }
        
        # Pattern 1: Look for explicit WINNER mentions
        for line in lines:
            line_upper = line.upper()
            
            if any(keyword in line_upper for keyword in ['WINNER', 'LOCK', 'Δ =', 'DELTA =', 'AGENCY-STATE']):
                winner_lock_data['detected'] = True
                winner_lock_data['raw_line'] = line
                
                # Extract delta value
                delta_match = re.search(r'Δ\s*[=:]\s*([+-]?\d+\.?\d*)', line)
                if delta_match:
                    winner_lock_data['delta_value'] = float(delta_match.group(1))
                else:
                    delta_match = re.search(r'([+-]?\d+\.?\d+)\s*(?:Delta|Δ)', line, re.IGNORECASE)
                    if delta_match:
                        winner_lock_data['delta_value'] = float(delta_match.group(1))
                
                # Determine which team has the lock
                line_lower = line.lower()
                
                if home_team.lower() in line_lower:
                    winner_lock_data['team'] = 'home'
                    winner_lock_data['team_name'] = home_team
                elif away_team.lower() in line_lower:
                    winner_lock_data['team'] = 'away'
                    winner_lock_data['team_name'] = away_team
                else:
                    if any(word in line_lower for word in ['home', 'hometeam', 'host']):
                        winner_lock_data['team'] = 'home'
                        winner_lock_data['team_name'] = home_team
                    elif any(word in line_lower for word in ['away', 'visitor', 'guest']):
                        winner_lock_data['team'] = 'away'
                        winner_lock_data['team_name'] = away_team
        
        # Set confidence level
        if winner_lock_data['detected']:
            if winner_lock_data['delta_value'] >= 1.0:
                winner_lock_data['confidence'] = 'High (Δ ≥ 1.0)'
            elif winner_lock_data['delta_value'] >= 0.5:
                winner_lock_data['confidence'] = 'Medium (Δ ≥ 0.5)'
            else:
                winner_lock_data['confidence'] = 'Low (Δ < 0.5)'
        
        return winner_lock_data

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
        margin: 1rem auto;
        border: 3px solid;
        box-sizing: border-box;
        width: 100%;
        max-width: 1000px;
    }
    
    .pattern-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid;
        margin: 1rem auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        width: 100%;
        max-width: 1000px;
        box-sizing: border-box;
    }
    
    .data-input-section {
        background: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E2E8F0;
        margin: 1rem auto;
        max-width: 1000px;
    }
    
    .validation-success {
        background: #F0FDF4;
        color: #059669;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #86EFAC;
        margin: 1rem auto;
        max-width: 1000px;
    }
    
    .winner-lock-display {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #16A34A;
        margin: 1rem auto;
        max-width: 1000px;
    }
    
    .detection-result {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .detected-team {
        background: #16A34A;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
    }
    
    .delta-value {
        background: #0D9488;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: monospace;
        font-weight: 700;
    }
    
    .pattern-combination-card {
        padding: 2rem;
        border-radius: 10px;
        border: 3px solid;
        text-align: center;
        margin: 1.5rem auto;
        box-sizing: border-box;
        max-width: 1000px;
    }
    
    @media (max-width: 768px) {
        .system-header {
            font-size: 1.8rem;
        }
        .pattern-card {
            padding: 1rem;
        }
        .detection-result {
            flex-direction: column;
            gap: 0.5rem;
            align-items: stretch;
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
        
        required_cols = ['team', 'goals_conceded_last_5']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"CSV missing required columns: {missing_cols}")
            return None
        
        df = df.fillna(0)
        
        if 'goals_conceded_last_5' in df.columns:
            df['goals_conceded_last_5'] = pd.to_numeric(df['goals_conceded_last_5'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== DISPLAY FUNCTIONS ===================
def display_betting_card(recommendation: Dict):
    """Display a clear betting recommendation card"""
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div class="pattern-card" style="border-color: {recommendation['color']}; border-left: 6px solid {recommendation['color']};">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">{recommendation['icon']}</span>
                <div style="flex: 1;">
                    <h3 style="color: {recommendation['color']}; margin: 0 0 0.5rem 0;">
                        {recommendation['pattern'].replace('_', ' ').title()}
                    </h3>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">
                        {recommendation['bet_description']}
                    </div>
                    <div style="color: #374151; margin-bottom: 0.5rem;">
                        {recommendation['reason']}
                    </div>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.7); padding: 1rem; border-radius: 8px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #6B7280;">Confidence</div>
                        <div style="font-size: 1rem; font-weight: 700; color: {recommendation['color']};">{recommendation['confidence']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #6B7280;">Stake Multiplier</div>
                        <div style="font-size: 1rem; font-weight: 700; color: {recommendation['color']};">{recommendation['stake_multiplier']}x</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #6B7280;">Historical Accuracy</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #059669;">{recommendation['sample_accuracy']}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_pattern_combination(patterns: Dict, display_info: Dict):
    """Display pattern combination result"""
    
    combination_colors = {
        'BOTH_PATTERNS': {'color': '#9A3412', 'bg': '#FFEDD5', 'border': '#F97316'},
        'ONLY_ELITE_DEFENSE': {'color': '#065F46', 'bg': '#F0FDF4', 'border': '#16A34A'},
        'ONLY_WINNER_LOCK': {'color': '#1E40AF', 'bg': '#EFF6FF', 'border': '#2563EB'},
        'NO_PATTERNS': {'color': '#6B7280', 'bg': '#F3F4F6', 'border': '#9CA3AF'}
    }
    
    combo = patterns['pattern_combination']
    colors = combination_colors.get(combo, combination_colors['NO_PATTERNS'])
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div class="pattern-combination-card" style="
            background: {colors['bg']};
            border-color: {colors['border']};
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{display_info.get('emoji', '⚪')}</div>
            <h2 style="color: {colors['color']}; margin: 0 0 0.5rem 0;">
                {display_info['title']}
            </h2>
            <div style="color: #374151; font-size: 1rem; margin-bottom: 0.5rem;">
                {display_info['message']}
            </div>
            <div style="color: #6B7280; font-size: 0.9rem;">
                {display_info.get('subtitle', '')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION ===================
def main():
    """Complete independent pattern detection application"""
    
    # Header
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL PATTERN-INDEPENDENT SYSTEM</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); 
                padding: 1rem; border-radius: 10px; border: 2px solid #3B82F6; margin: 1rem 0;">
            <strong>🎯 PATTERN-INDEPENDENT DETECTION:</strong> Each pattern detected separately based on 25-match analysis
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'agency_output' not in st.session_state:
        st.session_state.agency_output = ""
    if 'winner_lock_detected' not in st.session_state:
        st.session_state.winner_lock_detected = None
    
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
        
        # Agency-State Output Input
        st.markdown("---")
        st.markdown("#### 🤖 Agency-State System Output")
        
        st.info("""
        **AUTOMATED DETECTION:** Paste the Agency-State system output below. The system will automatically 
        detect Winner Lock patterns without any manual selection.
        """)
        
        # Use a different key for the widget
        agency_output_key = "agency_output_widget"
        
        # Text area for Agency-State output
        agency_output = st.text_area(
            "Paste Agency-State System Output:",
            height=150,
            placeholder="""Example Agency-State output:
🔐 TIER 2: AGENCY-STATE LOCKS v6.2
AGENCY-STATE CONTROL DETECTED
1 market(s) structurally locked
Strongest lock: WINNER (Δ = +1.08)
WINNER: Real Betis""",
            value=st.session_state.agency_output,
            key=agency_output_key
        )
        
        # Parse Agency-State output automatically
        if agency_output and home_team and away_team:
            detector = AutomatedWinnerLockDetector()
            winner_lock_result = detector.parse_agency_state_output(agency_output, home_team, away_team)
            st.session_state.winner_lock_detected = winner_lock_result
            st.session_state.agency_output = agency_output
            
            # Display automated detection result
            if winner_lock_result['detected']:
                st.markdown(f"""
                <div class="brutball-card-wrapper">
                    <div class="winner-lock-display">
                        <div class="detection-result">
                            <span class="detected-team">🤖 {winner_lock_result['team_name']} ({winner_lock_result['team'].title()})</span>
                            <span class="delta-value">Δ = +{winner_lock_result['delta_value']:.2f}</span>
                        </div>
                        <div style="color: #065F46; font-weight: 600; margin-top: 0.5rem;">
                            ✅ Winner Lock Automatically Detected
                        </div>
                        <div style="color: #374151; font-size: 0.9rem; margin-top: 0.25rem;">
                            Confidence: {winner_lock_result['confidence']} • Source: Agency-State System Output
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if we have data for analysis
    if home_row is None or away_row is None:
        st.error("Could not load team data")
        return
    
    # Get defense stats
    home_conceded = home_row.get('goals_conceded_last_5', 0)
    away_conceded = away_row.get('goals_conceded_last_5', 0)
    
    # Get automated Winner Lock detection result
    winner_lock_result = st.session_state.winner_lock_detected or {
        'detected': False,
        'team': None,
        'team_name': None,
        'delta_value': 0.0,
        'confidence': 'No detection performed'
    }
    
    # Data validation passed
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div class="validation-success">
            <h4>✅ Data Validation Passed</h4>
            <p>Ready for pattern-independent analysis</p>
            {'<p><strong>Winner Lock Detection:</strong> ' + winner_lock_result['confidence'] + '</p>' if winner_lock_result['detected'] else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyze button
    if st.button("🎯 RUN PATTERN-INDEPENDENT ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Running pattern-independent analysis..."):
            try:
                # 1. Detect all patterns independently
                detector = PatternIndependentDetector()
                patterns = detector.detect_all_patterns_independently(
                    home_team, away_team, home_conceded, away_conceded, winner_lock_result
                )
                
                # 2. Generate specific recommendations
                recommendations = detector.generate_pattern_specific_recommendations(patterns)
                
                # 3. Generate context-aware display
                display_info = detector.generate_context_aware_display(recommendations, patterns)
                
                # Store result
                st.session_state.analysis_result = {
                    'patterns': patterns,
                    'recommendations': recommendations,
                    'display_info': display_info,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded
                }
                
                st.success(f"✅ Analysis complete! Found {len(recommendations)} betting opportunity(s)")
                
            except Exception as e:
                st.error(f"❌ Analysis error: {str(e)}")
    
    # Display results if available
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Display pattern combination
        st.markdown("### 🎯 PATTERN COMBINATION DETECTED")
        display_pattern_combination(result['patterns'], result['display_info'])
        
        # Display recommendations
        if result['recommendations']:
            st.markdown("### 📊 RECOMMENDED BETS")
            
            for rec in result['recommendations']:
                display_betting_card(rec)
        
        # Display statistics
        st.markdown("### 📈 ANALYSIS STATISTICS")
        
        patterns = result['patterns']
        
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
                    padding: 1.5rem; border-radius: 10px; border: 2px solid #E2E8F0; 
                    margin: 1rem 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Elite Defense Bets</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #F97316;">{len(patterns['elite_defense_bets'])}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Winner Lock</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #16A34A;">{'1' if patterns['has_winner_lock'] else '0'}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">UNDER 3.5</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: {'#059669' if patterns['under_3_5_recommended'] else '#DC2626'}">
                            {'✅ Yes' if patterns['under_3_5_recommended'] else '❌ No'}
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #6B7280;">Total Patterns</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #7C3AED;">{len(result['recommendations'])}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern independence explanation
        st.markdown("### 🏗️ PATTERN INDEPENDENCE EXPLAINED")
        
        st.markdown("""
        <div class="brutball-card-wrapper">
            <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 10px; border: 2px solid #E2E8F0;">
                <h4>📊 From 25-Match Analysis:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #F97316;">
                        <strong>Only Elite Defense:</strong> 5 matches
                        <br><small>Espanyol, Parma, Juventus, Milan, Sunderland</small>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #16A34A;">
                        <strong>Only Winner Lock:</strong> 3 matches
                        <br><small>Betis, Man Utd, Brentford</small>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #9A3412;">
                        <strong>Both Patterns:</strong> 3 matches
                        <br><small>Porto, Napoli, Udinese</small>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #6B7280;">
                        <strong>Neither Pattern:</strong> 14 matches
                        <br><small>Chelsea, Liverpool, etc.</small>
                    </div>
                </div>
                <p style="color: #6B7280; font-size: 0.9rem; margin-top: 1rem;">
                    <strong>Key Insight:</strong> Patterns appear independently. Elite Defense doesn't require Winner Lock, and vice versa.
                    Each pattern triggers its own specific bets.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
            <p><strong>🎯 BRUTBALL PATTERN-INDEPENDENT SYSTEM v3.0</strong></p>
            <p><strong>Pattern Independence:</strong> Each pattern detected separately based on 25-match analysis</p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
                <div style="background: #FFEDD5; color: #9A3412; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🛡️ Elite Defense (Independent)
                </div>
                <div style="background: #F0FDF4; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🤖 Winner Lock (Independent)
                </div>
                <div style="background: #EFF6FF; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    📊 UNDER 3.5 (Conditional)
                </div>
            </div>
            <p><strong>Empirical Validation:</strong> 25-match historical analysis • Pattern independence proven</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()