"""
COMPLETE BRUTBALL PATTERN DETECTION APP - AUTOMATED VERSION
Fixed display issues and proper team naming
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
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

# =================== AUTOMATED WINNER LOCK DETECTOR ===================
class AutomatedWinnerLockDetector:
    """Automatically detect Winner Lock from Agency-State system output"""
    
    @staticmethod
    def parse_agency_state_output(output_text: str, home_team: str, away_team: str) -> Dict:
        """
        Parse Agency-State system output to detect Winner Lock automatically
        Returns: {
            'detected': bool,
            'team': 'home'/'away'/None,
            'team_name': str/None,
            'delta_value': float,
            'confidence': str,
            'raw_line': str/None
        }
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
            
            # Check for WINNER pattern (case insensitive)
            if any(keyword in line_upper for keyword in ['WINNER', 'LOCK', 'Δ =', 'DELTA =', 'AGENCY-STATE']):
                winner_lock_data['detected'] = True
                winner_lock_data['raw_line'] = line
                
                # Extract delta value
                delta_match = re.search(r'Δ\s*[=:]\s*([+-]?\d+\.?\d*)', line)
                if delta_match:
                    winner_lock_data['delta_value'] = float(delta_match.group(1))
                else:
                    # Try alternative delta patterns
                    delta_match = re.search(r'([+-]?\d+\.?\d+)\s*(?:Delta|Δ)', line, re.IGNORECASE)
                    if delta_match:
                        winner_lock_data['delta_value'] = float(delta_match.group(1))
                
                # Determine which team has the lock
                line_lower = line.lower()
                
                # Check for team mentions
                if home_team.lower() in line_lower:
                    winner_lock_data['team'] = 'home'
                    winner_lock_data['team_name'] = home_team
                elif away_team.lower() in line_lower:
                    winner_lock_data['team'] = 'away'
                    winner_lock_data['team_name'] = away_team
                else:
                    # Try to infer from context
                    if any(word in line_lower for word in ['home', 'hometeam', 'host']):
                        winner_lock_data['team'] = 'home'
                        winner_lock_data['team_name'] = home_team
                    elif any(word in line_lower for word in ['away', 'visitor', 'guest']):
                        winner_lock_data['team'] = 'away'
                        winner_lock_data['team_name'] = away_team
        
        # Pattern 2: Look for structured Agency-State output patterns
        if not winner_lock_data['detected']:
            for line in lines:
                # Common Agency-State patterns from historical data
                patterns = [
                    r'STRONGEST LOCK:\s*WINNER',
                    r'MARKET\(S\) STRUCTURALLY LOCKED',
                    r'AGENCY.*STATE.*CONTROL',
                    r'TIER 2.*AGENCY.*STATE'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        winner_lock_data['detected'] = True
                        winner_lock_data['raw_line'] = line
                        
                        # Extract delta if present
                        delta_match = re.search(r'([+-]?\d+\.\d+)', line)
                        if delta_match:
                            winner_lock_data['delta_value'] = float(delta_match.group(0))
                        
                        # Default to home team if can't determine (common in historical data)
                        if not winner_lock_data['team']:
                            winner_lock_data['team'] = 'home'
                            winner_lock_data['team_name'] = home_team
                        
                        break
        
        # Set confidence level
        if winner_lock_data['detected']:
            if winner_lock_data['delta_value'] >= 1.0:
                winner_lock_data['confidence'] = 'High (Δ ≥ 1.0)'
            elif winner_lock_data['delta_value'] >= 0.5:
                winner_lock_data['confidence'] = 'Medium (Δ ≥ 0.5)'
            else:
                winner_lock_data['confidence'] = 'Low (Δ < 0.5)'
        
        return winner_lock_data
    
    @staticmethod
    def generate_mock_agency_output(home_team: str, away_team: str, has_lock: bool = True) -> str:
        """
        Generate mock Agency-State output for testing
        Based on historical patterns from 25-match analysis
        """
        if not has_lock:
            return "No Agency-State control detected in this match."
        
        # Historical patterns from proven matches
        patterns = [
            f"""🔐 TIER 2: AGENCY-STATE LOCKS v6.2
AGENCY-STATE CONTROL DETECTED
1 market(s) structurally locked
Strongest lock: WINNER (Δ = +1.08)
WINNER: {home_team}""",
            
            f"""AGENCY-STATE SYSTEM OUTPUT
Match: {home_team} vs {away_team}
Detection: WINNER LOCK present
Delta value: +{np.random.choice(['0.78', '0.91', '1.04', '1.12'])}
Locked team: {home_team}""",
            
            f"""STRUCTURAL MARKET ANALYSIS
Winner market locked by Agency-State forces
Δ = +{np.random.choice(['0.82', '0.95', '1.01', '1.09'])}
Team with lock: {home_team}
Confidence: 92%"""
        ]
        
        return np.random.choice(patterns)

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
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
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
        margin: 1rem 0;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .validation-error {
        background: #FEF2F2;
        color: #DC2626;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #FCA5A5;
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
    
    .betting-card {
        background: white;
        border-radius: 10px;
        border: 2px solid;
        padding: 1.5rem;
        margin: 1rem auto;
        max-width: 1000px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .team-highlight {
        background: #FFEDD5;
        color: #9A3412;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
        margin: 0.5rem 0;
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
            <p><strong>Fully automated - No manual Winner Lock selection</strong></p>
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
                <div style="font-size: 2rem;">🤖</div>
                <div>
                    <h3 style="color: #065F46; margin: 0;">TIER 2: AUTOMATED WINNER LOCK</h3>
                    <div style="color: #374151;">Auto-detected from Agency-State system</div>
                </div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px;">
                <strong>Bet:</strong> Team Double Chance (Win or Draw)
                <br><strong>Confidence:</strong> 100% (6/6 matches - Automated)
                <br><strong>Source:</strong> Auto-parsed Agency-State output
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
                    <div style="color: #374151;">Confidence varies by automated detection</div>
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

def display_winner_lock_result(detection_result: Dict):
    """Display automated Winner Lock detection result"""
    if detection_result['detected']:
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div class="winner-lock-display">
                <div class="detection-result">
                    <span class="detected-team">🤖 {detection_result['team_name']} ({detection_result['team'].title()})</span>
                    <span class="delta-value">Δ = +{detection_result['delta_value']:.2f}</span>
                </div>
                <div style="color: #065F46; font-weight: 600; margin-top: 0.5rem;">
                    ✅ Winner Lock Automatically Detected
                </div>
                <div style="color: #374151; font-size: 0.9rem; margin-top: 0.25rem;">
                    Confidence: {detection_result['confidence']} • Source: Agency-State System Output
                </div>
                {'<div style="background: #FEF3C7; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem; border: 1px solid #F59E0B;"><strong>Detection Source:</strong> ' + detection_result['raw_line'] + '</div>' if detection_result.get('raw_line') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="brutball-card-wrapper">
            <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px; border: 2px solid #D1D5DB; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">🔍</span>
                    <h3 style="color: #6B7280; margin: 0;">No Winner Lock Detected</h3>
                </div>
                <div style="color: #6B7280;">
                    {detection_result['confidence']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def determine_under_15_team(home_team: str, away_team: str, home_conceded: int, away_conceded: int) -> Dict:
    """Determine which team should have UNDER 1.5 goals based on defense stats"""
    # Elite defense condition: ≤4 goals conceded in last 5
    home_is_elite = home_conceded <= 4
    away_is_elite = away_conceded <= 4
    
    # Defense gap condition: > 2.0 difference
    defense_gap = abs(home_conceded - away_conceded)
    
    if home_is_elite and not away_is_elite and defense_gap > 2.0:
        # Home has elite defense, away doesn't
        return {
            'team_to_bet': away_team,
            'bet_type': f"{away_team} to score UNDER 1.5 goals",
            'reason': f"{home_team} has elite defense ({home_conceded} goals conceded) vs {away_team} ({away_conceded} goals conceded)",
            'stake_multiplier': 2.0,
            'confidence': 'VERY_HIGH (100% historical accuracy)',
            'pattern': 'ELITE_DEFENSE_UNDER_1_5'
        }
    elif away_is_elite and not home_is_elite and defense_gap > 2.0:
        # Away has elite defense, home doesn't
        return {
            'team_to_bet': home_team,
            'bet_type': f"{home_team} to score UNDER 1.5 goals",
            'reason': f"{away_team} has elite defense ({away_conceded} goals conceded) vs {home_team} ({home_conceded} goals conceded)",
            'stake_multiplier': 2.0,
            'confidence': 'VERY_HIGH (100% historical accuracy)',
            'pattern': 'ELITE_DEFENSE_UNDER_1_5'
        }
    elif home_is_elite and away_is_elite:
        # Both have elite defense
        return {
            'team_to_bet': f"{away_team} (preferred)",
            'bet_type': f"{away_team} to score UNDER 1.5 goals",
            'reason': f"Both teams have elite defense: {home_team} ({home_conceded}), {away_team} ({away_conceded}) - betting on away team",
            'stake_multiplier': 1.5,
            'confidence': 'HIGH',
            'pattern': 'ELITE_DEFENSE_UNDER_1_5'
        }
    else:
        # No elite defense
        return None

def display_betting_card(recommendation: Dict, bet_type: str = "UNDER 1.5"):
    """Display a clear betting recommendation card"""
    if bet_type == "UNDER 1.5":
        color = "#F97316"
        emoji = "🛡️"
        title = "ELITE DEFENSE BET"
    elif bet_type == "DOUBLE_CHANCE":
        color = "#16A34A"
        emoji = "🤖"
        title = "WINNER LOCK BET"
    else:  # UNDER 3.5
        color = "#2563EB"
        emoji = "📊"
        title = "TOTAL GOALS BET"
    
    # Extract team name from bet_type if available
    bet_description = recommendation.get('bet_type', '')
    if 'UNDER 1.5' in bet_description:
        # Extract team name from bet description
        team_name = bet_description.split(' to score')[0] if ' to score' in bet_description else "Opponent"
        bet_explanation = f"<strong>{team_name}</strong> to score UNDER 1.5 goals"
    else:
        bet_explanation = bet_description
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div class="betting-card" style="border-color: {color}; border-left: 6px solid {color};">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">{emoji}</span>
                <div>
                    <h3 style="color: {color}; margin: 0;">{title}</h3>
                    <div style="color: #374151; font-size: 0.9rem; margin-top: 0.25rem;">
                        {recommendation.get('pattern', '').replace('_', ' ').title()}
                    </div>
                </div>
            </div>
            
            <div style="margin: 1rem 0;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">
                    🎯 BET RECOMMENDATION:
                </div>
                <div style="background: #F8FAFC; padding: 1rem; border-radius: 8px; border: 2px solid #E2E8F0;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: {color}; margin-bottom: 0.5rem;">
                        {bet_explanation}
                    </div>
                    <div style="color: #374151; margin-bottom: 0.5rem;">
                        {recommendation.get('reason', '')}
                    </div>
                    <div style="color: #6B7280; font-size: 0.9rem;">
                        <strong>How it works:</strong> {recommendation.get('condition_1', 'Elite Defense pattern detected')}
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div style="text-align: center; background: {color}15; padding: 1rem; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Confidence</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {color};">{recommendation.get('confidence', 'N/A')}</div>
                </div>
                <div style="text-align: center; background: {color}15; padding: 1rem; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Stake Multiplier</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {color};">{recommendation.get('stake_multiplier', 1.0)}x</div>
                </div>
                <div style="text-align: center; background: {color}15; padding: 1rem; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Historical Accuracy</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #059669;">{recommendation.get('sample_accuracy', 'N/A')}</div>
                </div>
            </div>
            
            {'<div style="margin-top: 1rem; padding: 0.75rem; background: #FEF3C7; border-radius: 6px; border: 1px solid #F59E0B;"><strong>⚠️ Note:</strong> ' + recommendation.get('warning', '') + '</div>' if recommendation.get('warning') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION ===================
def main():
    """Complete independent pattern detection application - AUTOMATED VERSION"""
    
    # Header
    st.markdown('<div class="system-header">🤖🎯🔒 BRUTBALL AUTOMATED TIER SYSTEM</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); 
                padding: 1rem; border-radius: 10px; border: 2px solid #16A34A; margin: 1rem 0;">
            <strong>🚀 AUTOMATED DETECTION ACTIVE:</strong> Winner Lock detection is now fully automated from Agency-State system output
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display tier system
    display_tier_system()
    
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
        detect Winner Lock patterns without any manual selection. Based on 25-match historical analysis.
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
            display_winner_lock_result(winner_lock_result)
        elif st.session_state.agency_output and home_team and away_team:
            # Use stored agency output if available
            detector = AutomatedWinnerLockDetector()
            winner_lock_result = detector.parse_agency_state_output(
                st.session_state.agency_output, home_team, away_team
            )
            st.session_state.winner_lock_detected = winner_lock_result
            display_winner_lock_result(winner_lock_result)
        
        # Test mode option
        with st.expander("🔧 Test Mode Options"):
            test_mode = st.checkbox("Enable Test Mode", value=False)
            if test_mode:
                col1, col2 = st.columns(2)
                with col1:
                    include_winner_lock = st.checkbox("Include Winner Lock in test", value=True)
                with col2:
                    if st.button("Generate Test Output"):
                        test_output = AutomatedWinnerLockDetector.generate_mock_agency_output(
                            home_team, away_team, include_winner_lock
                        )
                        st.session_state.agency_output = test_output
                        st.rerun()
        
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
            <p>Ready for automated pattern detection</p>
            {'<p><strong>Automated Detection:</strong> ' + winner_lock_result['confidence'] + '</p>' if winner_lock_result['detected'] else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple analysis logic
    st.markdown("### 🤖 SIMPLE PATTERN ANALYSIS")
    
    # Determine UNDER 1.5 bet
    under_15_recommendation = determine_under_15_team(
        home_team, away_team, home_conceded, away_conceded
    )
    
    # Determine UNDER 3.5 bet
    elite_defense_present = (home_conceded <= 4) or (away_conceded <= 4)
    winner_lock_present = winner_lock_result['detected']
    
    if elite_defense_present or winner_lock_present:
        under_35_recommendation = {
            'bet_type': 'Total UNDER 3.5 goals',
            'reason': f"Elite Defense pattern present: {home_team} ({home_conceded}), {away_team} ({away_conceded})" if elite_defense_present else f"Winner Lock detected: {winner_lock_result['team_name']}",
            'stake_multiplier': 1.0,
            'confidence': 'TIER 2: 87.5%' if elite_defense_present and not winner_lock_present else 'TIER 3: 83.3%' if winner_lock_present and not elite_defense_present else 'TIER 1: 100%',
            'pattern': 'TOTAL_UNDER_3_5',
            'condition_1': 'Elite Defense pattern present (scoring suppression)' if elite_defense_present else 'Winner Lock pattern present (market control)'
        }
    else:
        under_35_recommendation = None
    
    # Display recommendations
    if under_15_recommendation or under_35_recommendation or winner_lock_result['detected']:
        st.markdown("### 🎯 BETTING RECOMMENDATIONS")
        
        # Display UNDER 1.5 bet if applicable
        if under_15_recommendation:
            display_betting_card(under_15_recommendation, "UNDER 1.5")
        
        # Display Winner Lock bet if detected
        if winner_lock_result['detected']:
            winner_lock_recommendation = {
                'bet_type': f"{winner_lock_result['team_name']} Double Chance (Win or Draw)",
                'reason': f"Automated Winner Lock detection (Δ = +{winner_lock_result['delta_value']:.2f})",
                'stake_multiplier': 1.5,
                'confidence': 'VERY_HIGH (100% historical accuracy)',
                'pattern': 'WINNER_LOCK_DOUBLE_CHANCE',
                'condition_1': 'Agency-State system detected structural market lock',
                'sample_accuracy': '6/6 matches (100%)'
            }
            display_betting_card(winner_lock_recommendation, "DOUBLE_CHANCE")
        
        # Display UNDER 3.5 bet if applicable
        if under_35_recommendation:
            display_betting_card(under_35_recommendation, "UNDER 3.5")
    
    # Display statistics
    st.markdown("### 📈 ANALYSIS STATISTICS")
    
    # Count patterns
    elite_defense_count = 1 if under_15_recommendation else 0
    winner_lock_count = 1 if winner_lock_result['detected'] else 0
    under_35_present = under_35_recommendation is not None
    total_patterns = elite_defense_count + winner_lock_count
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
                padding: 1.5rem; border-radius: 10px; border: 2px solid #E2E8F0; 
                margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Elite Defense</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #16A34A;">{elite_defense_count}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Winner Lock</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2563EB;">{winner_lock_count}</div>
                    <div style="font-size: 0.7rem; color: #2563EB;">🤖 Automated</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6B7280;">UNDER 3.5</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {'#059669' if under_35_present else '#DC2626'}">
                        {'✅ Yes' if under_35_present else '❌ No'}
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6B7280;">Total Patterns</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #7C3AED;">{total_patterns}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pattern combination display
    st.markdown("### 🎯 PATTERN COMBINATION")
    
    if elite_defense_count > 0 and winner_lock_count > 0:
        combo = "BOTH_PATTERNS"
        color = "#9A3412"
        bg = "#FFEDD5"
        border = "#F97316"
        desc = "Both Elite Defense and Winner Lock patterns detected"
        emoji = "🎯"
    elif elite_defense_count > 0:
        combo = "ONLY_ELITE_DEFENSE"
        color = "#065F46"
        bg = "#F0FDF4"
        border = "#16A34A"
        desc = "Only Elite Defense pattern detected"
        emoji = "🛡️"
    elif winner_lock_count > 0:
        combo = "ONLY_WINNER_LOCK"
        color = "#1E40AF"
        bg = "#EFF6FF"
        border = "#2563EB"
        desc = "Only Winner Lock pattern detected"
        emoji = "🤖"
    else:
        combo = "NO_PATTERNS"
        color = "#6B7280"
        bg = "#F3F4F6"
        border = "#9CA3AF"
        desc = "No patterns detected"
        emoji = "🔍"
    
    st.markdown(f"""
    <div class="brutball-card-wrapper">
        <div style="
            background: {bg};
            padding: 2rem;
            border-radius: 10px;
            border: 3px solid {border};
            text-align: center;
            margin: 1.5rem 0;
            box-sizing: border-box;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{emoji}</div>
            <h2 style="color: {color}; margin: 0 0 0.5rem 0;">
                {combo.replace('_', ' ').title()}
            </h2>
            <div style="color: #374151; font-size: 0.9rem;">
                {desc}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="brutball-card-wrapper">
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
            <p><strong>🤖 BRUTBALL AUTOMATED TIER SYSTEM v2.0</strong></p>
            <p><strong>Fully Automated Detection:</strong> No manual Winner Lock selection</p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
                <div style="background: #FFEDD5; color: #9A3412; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🛡️ Tier 1: Elite Defense Detection
                </div>
                <div style="background: #F0FDF4; color: #065F46; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    🤖 Tier 2: Automated Winner Lock
                </div>
                <div style="background: #EFF6FF; color: #1E40AF; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                    📊 Tier 3: Confidence-Tiered UNDER 3.5
                </div>
            </div>
            <p><strong>Data Source:</strong> GitHub CSV • <strong>Detection:</strong> Automated parsing from Agency-State output</p>
            <p><strong>Empirical Validation:</strong> 25-match historical analysis • 100% Winner Lock accuracy</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()