"""
BRUTBALL v6.4 - DOUBLE CHANCE ARCHITECTURE
Complete Implementation with Visual Design
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import os
import streamlit as st

# ============================================================================
# SYSTEM CONSTANTS (IMMUTABLE)
# ============================================================================

# GATE THRESHOLDS
CONTROL_CRITERIA_REQUIRED = 2
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1
DIRECTION_THRESHOLD = 0.25
STATE_FLIP_FAILURES_REQUIRED = 2
ENFORCEMENT_METHODS_REQUIRED = 2
TOTALS_LOCK_THRESHOLD = 1.2
UNDER_GOALS_THRESHOLD = 2.5

# MARKET-SPECIFIC CONFIGURATION
MARKET_THRESHOLDS = {
    'DOUBLE_CHANCE': {
        'opponent_xg_max': 1.3,
        'recent_concede_max': None,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Double Chance (Win OR Draw)",
        'declaration_template': "🔒 DOUBLE CHANCE LOCKED\n{controller} cannot lose\nCovers Win OR Draw",
        'color': "#10B981",  # Emerald green
        'icon': "🛡️"
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,
        'recent_concede_max': 0.8,
        'state_flip_failures': 3,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Clean Sheet",
        'declaration_template': "🔒 CLEAN SHEET LOCKED\n{controller} will not concede",
        'color': "#3B82F6",  # Blue
        'icon': "🚫"
    },
    'TEAM_NO_SCORE': {
        'opponent_xg_max': 0.6,
        'recent_concede_max': 0.6,
        'state_flip_failures': 4,
        'enforcement_methods': 3,
        'urgency_required': False,
        'bet_label': "Team No Score",
        'declaration_template': "🔒 TEAM NO SCORE LOCKED\n{opponent} will not score",
        'color': "#8B5CF6",  # Violet
        'icon': "⚡"
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,
        'recent_concede_max': 1.0,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Opponent Under 1.5 Goals",
        'declaration_template': "🔒 OPPONENT UNDER 1.5 LOCKED\n{opponent} cannot score >1",
        'color': "#F59E0B",  # Amber
        'icon': "📉"
    }
}

CAPITAL_MULTIPLIERS = {'EDGE_MODE': 1.0, 'LOCK_MODE': 2.0}

# ============================================================================
# VISUAL DESIGN CONSTANTS
# ============================================================================

COLORS = {
    'primary': '#1E40AF',      # Deep blue
    'secondary': '#10B981',    # Emerald
    'accent': '#8B5CF6',       # Violet
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'success': '#10B981',      # Green
    'info': '#3B82F6',         # Blue
    'dark': '#1F2937',         # Gray-800
    'light': '#F9FAFB',        # Gray-50
    'background': '#0F172A',   # Slate-900
    'card': '#1E293B',         # Slate-800
    'border': '#334155'        # Slate-700
}

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

class BrutballDataLoader:
    """Loads and validates CSV data"""
    
    REQUIRED_COLUMNS = [
        'team', 'home_matches_played', 'away_matches_played',
        'home_goals_scored', 'away_goals_scored',
        'home_goals_conceded', 'away_goals_conceded',
        'home_xg_for', 'away_xg_for',
        'home_xg_against', 'away_xg_against',
        'goals_scored_last_5', 'goals_conceded_last_5',
        'home_goals_conceded_last_5', 'away_goals_conceded_last_5'
    ]
    
    @staticmethod
    def load_league_data(league_name: str) -> pd.DataFrame:
        csv_path = f"leagues/{league_name}.csv"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        missing_cols = [col for col in BrutballDataLoader.REQUIRED_COLUMNS 
                       if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    @staticmethod
    def get_team_data(df: pd.DataFrame, team_name: str) -> Dict:
        team_row = df[df['team'] == team_name].iloc[0]
        
        data = {}
        for col in df.columns:
            val = team_row[col]
            if pd.isna(val):
                data[col] = None
            elif isinstance(val, (np.integer, np.int64)):
                data[col] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                data[col] = float(val)
            else:
                data[col] = val
        
        # Pre-calculations
        data['home_xg_per_match'] = (data['home_xg_for'] / data['home_matches_played'] 
                                    if data['home_matches_played'] > 0 else 0)
        data['away_xg_per_match'] = (data['away_xg_for'] / data['away_matches_played'] 
                                    if data['away_matches_played'] > 0 else 0)
        data['home_xga_per_match'] = (data['home_xg_against'] / data['home_matches_played'] 
                                      if data['home_matches_played'] > 0 else 0)
        data['away_xga_per_match'] = (data['away_xg_against'] / data['away_matches_played'] 
                                      if data['away_matches_played'] > 0 else 0)
        
        data['avg_scored_last_5'] = data['goals_scored_last_5'] / 5
        data['avg_conceded_last_5'] = data['goals_conceded_last_5'] / 5
        data['home_avg_conceded_last_5'] = (data['home_goals_conceded_last_5'] / 5 
                                           if data.get('home_goals_conceded_last_5') is not None 
                                           else data['avg_conceded_last_5'])
        data['away_avg_conceded_last_5'] = (data['away_goals_conceded_last_5'] / 5 
                                           if data.get('away_goals_conceded_last_5') is not None 
                                           else data['avg_conceded_last_5'])
        
        return data

# ============================================================================
# TIER 1: v6.0 EDGE DETECTION ENGINE
# ============================================================================

class EdgeDetectionEngine:
    @staticmethod
    def evaluate_control_criteria(team_data: Dict) -> Tuple[float, List[str]]:
        criteria_passed = []
        weighted_score = 0.0
        
        avg_xg = (team_data.get('home_xg_per_match', 0) + team_data.get('away_xg_per_match', 0)) / 2
        if avg_xg > 1.4:
            criteria_passed.append("Tempo")
            weighted_score += 1.0
        
        total_goals = team_data.get('home_goals_scored', 0) + team_data.get('away_goals_scored', 0)
        total_xg = team_data.get('home_xg_for', 0) + team_data.get('away_xg_for', 0)
        if total_xg > 0 and (total_goals / total_xg) > 0.9:
            criteria_passed.append("Efficiency")
            weighted_score += 1.0
        
        if team_data['avg_scored_last_5'] > 1.5:
            criteria_passed.append("Patterns")
            weighted_score += 0.8
        
        return weighted_score, criteria_passed
    
    @staticmethod
    def analyze_match(home_data: Dict, away_data: Dict) -> Dict:
        home_score, home_criteria = EdgeDetectionEngine.evaluate_control_criteria(home_data)
        away_score, away_criteria = EdgeDetectionEngine.evaluate_control_criteria(away_data)
        
        controller = None
        if len(home_criteria) >= CONTROL_CRITERIA_REQUIRED and len(away_criteria) >= CONTROL_CRITERIA_REQUIRED:
            if abs(home_score - away_score) > QUIET_CONTROL_SEPARATION_THRESHOLD:
                controller = 'HOME' if home_score > away_score else 'AWAY'
        elif len(home_criteria) >= CONTROL_CRITERIA_REQUIRED:
            controller = 'HOME'
        elif len(away_criteria) >= CONTROL_CRITERIA_REQUIRED:
            controller = 'AWAY'
        
        combined_xg = home_data['home_xg_per_match'] + away_data['away_xg_per_match']
        max_xg = max(home_data['home_xg_per_match'], away_data['away_xg_per_match'])
        goals_environment = (combined_xg >= 2.8 and max_xg >= 1.6)
        
        if controller and goals_environment:
            action = f"BACK {controller} & OVER 2.5"
            confidence = 7.5
        elif controller:
            action = f"BACK {controller}"
            confidence = 8.0
        elif goals_environment:
            action = "OVER 2.5"
            confidence = 6.0
        else:
            action = "UNDER 2.5"
            confidence = 5.5
        
        if confidence >= 8.0:
            base_stake = 2.5
        elif confidence >= 7.0:
            base_stake = 2.0
        elif confidence >= 6.0:
            base_stake = 1.5
        else:
            base_stake = 1.0
        
        return {
            'controller': controller,
            'action': action,
            'confidence': confidence,
            'base_stake': base_stake,
            'goals_environment': goals_environment,
            'home_score': home_score,
            'away_score': away_score,
            'home_criteria': home_criteria,
            'away_criteria': away_criteria
        }

# ============================================================================
# TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS
# ============================================================================

class EdgeDerivedLocks:
    @staticmethod
    def generate_under_locks(home_data: Dict, away_data: Dict) -> List[Dict]:
        locks = []
        
        if home_data['avg_conceded_last_5'] <= 1.0:
            confidence = EdgeDerivedLocks._get_confidence_tier(away_data['avg_scored_last_5'])
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': away_data['team'],
                'defensive_team': home_data['team'],
                'confidence': confidence,
                'avg_conceded': home_data['avg_conceded_last_5'],
                'opponent_avg_scored': away_data['avg_scored_last_5'],
                'bet_label': f"{away_data['team']} to score UNDER 1.5 goals",
                'icon': "🛡️",
                'color': COLORS['info']
            })
        
        if away_data['avg_conceded_last_5'] <= 1.0:
            confidence = EdgeDerivedLocks._get_confidence_tier(home_data['avg_scored_last_5'])
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': home_data['team'],
                'defensive_team': away_data['team'],
                'confidence': confidence,
                'avg_conceded': away_data['avg_conceded_last_5'],
                'opponent_avg_scored': home_data['avg_scored_last_5'],
                'bet_label': f"{home_data['team']} to score UNDER 1.5 goals",
                'icon': "🛡️",
                'color': COLORS['info']
            })
        
        return locks
    
    @staticmethod
    def _get_confidence_tier(opponent_avg_scored: float) -> str:
        if opponent_avg_scored <= 1.4:
            return "VERY STRONG"
        elif opponent_avg_scored <= 1.6:
            return "STRONG"
        elif opponent_avg_scored <= 1.8:
            return "WEAK"
        else:
            return "VERY WEAK"

# ============================================================================
# TIER 2: AGENCY-STATE LOCK ENGINE v6.4
# ============================================================================

class AgencyStateLockEngine:
    def __init__(self, home_data: Dict, away_data: Dict):
        self.home_data = home_data
        self.away_data = away_data
        
    def check_market(self, market: str) -> Optional[Dict]:
        thresholds = MARKET_THRESHOLDS[market]
        
        edge_result = EdgeDetectionEngine.analyze_match(self.home_data, self.away_data)
        if not edge_result['controller']:
            return None
        
        if edge_result['controller'] == 'HOME':
            controller_data = self.home_data
            opponent_data = self.away_data
            controller_xg = self.home_data['home_xg_per_match']
            opponent_xg = self.away_data['away_xg_per_match']
        else:
            controller_data = self.away_data
            opponent_data = self.home_data
            controller_xg = self.away_data['away_xg_per_match']
            opponent_xg = self.home_data['home_xg_per_match']
        
        if not self._gate1_quiet_control(edge_result):
            return None
        if not self._gate2_directional_dominance(controller_xg, opponent_xg, thresholds['opponent_xg_max']):
            return None
        if not self._gate3_agency_collapse(opponent_data, thresholds['state_flip_failures']):
            return None
        if not self._gate4_state_preservation(controller_data, opponent_data, market, thresholds):
            return None
        
        return {
            'market': market,
            'controller': controller_data['team'],
            'opponent': opponent_data['team'],
            'control_delta': controller_xg - opponent_xg,
            'bet_label': thresholds['bet_label'],
            'declaration': thresholds['declaration_template'].format(
                controller=controller_data['team'],
                opponent=opponent_data['team']
            ),
            'icon': thresholds['icon'],
            'color': thresholds['color'],
            'capital_mode': 'LOCK_MODE'
        }
    
    def _gate1_quiet_control(self, edge_result: Dict) -> bool:
        if not edge_result['controller']:
            return False
        if (len(edge_result['home_criteria']) >= CONTROL_CRITERIA_REQUIRED and 
            len(edge_result['away_criteria']) >= CONTROL_CRITERIA_REQUIRED):
            if abs(edge_result['home_score'] - edge_result['away_score']) <= QUIET_CONTROL_SEPARATION_THRESHOLD:
                return False
        return True
    
    def _gate2_directional_dominance(self, controller_xg: float, opponent_xg: float, opponent_threshold: float) -> bool:
        delta = controller_xg - opponent_xg
        return (delta > DIRECTION_THRESHOLD and opponent_xg < opponent_threshold)
    
    def _gate3_agency_collapse(self, opponent_data: Dict, required_failures: int) -> bool:
        failures = 0
        if opponent_data['avg_scored_last_5'] < 1.1:
            failures += 1
        if opponent_data['avg_scored_last_5'] < 1.4:
            failures += 1
        if opponent_data['avg_scored_last_5'] < 1.2:
            failures += 1
        if opponent_data['avg_scored_last_5'] < (1.3 * 0.8):
            failures += 1
        return failures >= required_failures
    
    def _gate4_state_preservation(self, controller_data: Dict, opponent_data: Dict, 
                                  market: str, thresholds: Dict) -> bool:
        if market != 'DOUBLE_CHANCE':
            recent_concede = controller_data['home_avg_conceded_last_5']
            if recent_concede > thresholds['recent_concede_max']:
                return False
        
        methods = 0
        concede_avg = controller_data['home_avg_conceded_last_5']
        if concede_avg < 1.2:
            methods += 1
        if controller_data['avg_scored_last_5'] > 1.2:
            methods += 1
        controller_xg = controller_data['home_xg_per_match']
        if controller_xg > 1.3:
            methods += 1
        total_goals = controller_data.get('home_goals_scored', 0) + controller_data.get('away_goals_scored', 0)
        total_xg = controller_data.get('home_xg_for', 0) + controller_data.get('away_xg_for', 0)
        if total_xg > 0 and (total_goals / total_xg) > 0.85:
            methods += 1
        
        return methods >= thresholds['enforcement_methods']

# ============================================================================
# TIER 3: TOTALS LOCK ENGINE
# ============================================================================

class TotalsLockEngine:
    @staticmethod
    def check_totals_lock(home_data: Dict, away_data: Dict) -> Optional[Dict]:
        home_avg_scored = home_data['avg_scored_last_5']
        away_avg_scored = away_data['avg_scored_last_5']
        
        if home_avg_scored <= TOTALS_LOCK_THRESHOLD and away_avg_scored <= TOTALS_LOCK_THRESHOLD:
            return {
                'market': 'TOTALS_UNDER_2_5',
                'condition': f"Both teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5)",
                'home_avg_scored': home_avg_scored,
                'away_avg_scored': away_avg_scored,
                'bet_label': "UNDER 2.5 Goals",
                'declaration': f"🔒 TOTALS LOCKED\nDual low-offense trend confirmed",
                'icon': "📊",
                'color': COLORS['warning'],
                'capital_mode': 'LOCK_MODE'
            }
        return None

# ============================================================================
# MAIN BRUTBALL v6.4 ENGINE
# ============================================================================

class Brutballv64:
    def __init__(self, league_name: str):
        self.league_name = league_name
        self.df = BrutballDataLoader.load_league_data(league_name)
    
    def analyze_match(self, home_team: str, away_team: str, bankroll: float = 1000, base_stake_pct: float = 0.5) -> Dict:
        home_data = BrutballDataLoader.get_team_data(self.df, home_team)
        away_data = BrutballDataLoader.get_team_data(self.df, away_team)
        home_data['team'] = home_team
        away_data['team'] = away_team
        home_data['is_home'] = True
        away_data['is_home'] = False
        
        # TIER 1: Edge Detection
        edge_result = EdgeDetectionEngine.analyze_match(home_data, away_data)
        
        # TIER 1+: Edge-Derived Under 1.5 Locks
        edge_locks = EdgeDerivedLocks.generate_under_locks(home_data, away_data)
        
        # TIER 2: Agency-State Locks
        agency_engine = AgencyStateLockEngine(home_data, away_data)
        agency_locks = []
        for market in ['DOUBLE_CHANCE', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
            lock = agency_engine.check_market(market)
            if lock:
                agency_locks.append(lock)
        
        # TIER 3: Totals Lock
        totals_lock = TotalsLockEngine.check_totals_lock(home_data, away_data)
        
        # CAPITAL DECISION
        any_lock = bool(edge_locks or agency_locks or totals_lock)
        capital_mode = 'LOCK_MODE' if any_lock else 'EDGE_MODE'
        multiplier = CAPITAL_MULTIPLIERS[capital_mode]
        
        # FINAL STAKE CALCULATION
        base_stake_amount = (bankroll * base_stake_pct / 100)
        final_stake = base_stake_amount * multiplier
        
        # BET RECOMMENDATIONS
        recommendations = []
        for lock in agency_locks:
            recommendations.append({
                'type': 'AGENCY_LOCK',
                'market': lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': lock['declaration'],
                'confidence': 'HIGH',
                'icon': lock['icon'],
                'color': lock['color']
            })
        
        for lock in edge_locks:
            recommendations.append({
                'type': 'EDGE_DERIVED',
                'market': lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': f"Defensive trend: {lock['defensive_team']} concedes avg {lock['avg_conceded']:.1f}",
                'confidence': lock['confidence'],
                'icon': lock['icon'],
                'color': lock['color']
            })
        
        if totals_lock:
            recommendations.append({
                'type': 'TOTALS_LOCK',
                'market': totals_lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': totals_lock['declaration'],
                'confidence': 'HIGH',
                'icon': totals_lock['icon'],
                'color': totals_lock['color']
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'EDGE_ACTION',
                'market': edge_result['action'],
                'stake_pct': (base_stake_amount / bankroll) * 100,
                'stake_amount': base_stake_amount,
                'reason': f"Edge detection: {edge_result['confidence']}/10 confidence",
                'confidence': 'MEDIUM',
                'icon': "📈",
                'color': COLORS['secondary']
            })
        
        return {
            'match': f"{home_team} vs {away_team}",
            'home_data': home_data,
            'away_data': away_data,
            'edge_result': edge_result,
            'edge_locks': edge_locks,
            'agency_locks': agency_locks,
            'totals_lock': totals_lock,
            'capital': {
                'mode': capital_mode,
                'multiplier': multiplier,
                'base_stake': base_stake_amount,
                'final_stake': final_stake
            },
            'recommendations': recommendations
        }
    
    def get_available_teams(self) -> List[str]:
        return self.df['team'].tolist()

# ============================================================================
# VISUAL COMPONENTS
# ============================================================================

def apply_custom_css():
    st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['background']} 0%, #0c4a6e 100%);
    }}
    
    /* Cards */
    .custom-card {{
        background: {COLORS['card']};
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    .custom-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {COLORS['light']} !important;
        font-weight: 700 !important;
    }}
    
    /* Metrics */
    .stMetric {{
        background: rgba(30, 41, 59, 0.8);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid {COLORS['border']};
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['card']};
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 1px solid {COLORS['border']};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']} !important;
        color: white !important;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {COLORS['secondary']} 0%, {COLORS['accent']} 100%);
    }}
    
    /* Input fields */
    .stSelectbox, .stNumberInput {{
        background-color: {COLORS['card']};
        border-radius: 8px;
        border: 1px solid {COLORS['border']};
    }}
    
    /* Dataframe */
    .dataframe {{
        background-color: {COLORS['card']} !important;
        color: {COLORS['light']} !important;
    }}
    
    /* Badges */
    .confidence-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        margin: 4px;
    }}
    
    /* Team badges */
    .team-badge {{
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        background: rgba(30, 64, 175, 0.2);
        border: 1px solid {COLORS['primary']};
        margin: 4px;
    }}
    </style>
    """, unsafe_allow_html=True)

def create_bet_card(recommendation: Dict):
    """Create a visually appealing bet recommendation card"""
    color = recommendation.get('color', COLORS['primary'])
    icon = recommendation.get('icon', '🎯')
    
    st.markdown(f"""
    <div class="custom-card" style="border-left: 4px solid {color};">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: {color};">{icon} {recommendation['market']}</h3>
                <div style="margin-top: 10px; color: #D1D5DB;">
                    {recommendation['reason']}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: 700; color: {color};">
                    ${recommendation['stake_amount']:.2f}
                </div>
                <div style="font-size: 14px; color: #9CA3AF;">
                    {recommendation['stake_pct']:.1f}% stake
                </div>
            </div>
        </div>
        <div style="margin-top: 15px; display: flex; align-items: center;">
            <span class="confidence-badge" style="background: {color}; color: white;">
                {recommendation['confidence']} CONFIDENCE
            </span>
            <span style="margin-left: auto; font-size: 12px; color: #9CA3AF;">
                {recommendation['type']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, delta: str = None, color: str = COLORS['light']):
    """Create a metric card with custom styling"""
    delta_html = f'<div style="font-size: 14px; color: #9CA3AF;">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="custom-card" style="text-align: center; padding: 15px;">
        <div style="font-size: 14px; color: #9CA3AF; margin-bottom: 8px;">{label}</div>
        <div style="font-size: 24px; font-weight: 700; color: {color};">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_team_badge(team_name: str, is_home: bool = True):
    """Create a team badge with home/away indicator"""
    badge_type = "🏠 HOME" if is_home else "✈️ AWAY"
    bg_color = COLORS['primary'] if is_home else COLORS['accent']
    
    st.markdown(f"""
    <div style="display: inline-block; background: {bg_color}; color: white; 
                padding: 8px 16px; border-radius: 20px; margin: 4px; font-weight: 600;">
        {badge_type}: {team_name}
    </div>
    """, unsafe_allow_html=True)

def create_rule_indicator(rule_name: str, passed: bool, details: str = ""):
    """Create a visual indicator for rule passing/failing"""
    icon = "✅" if passed else "❌"
    color = COLORS['success'] if passed else COLORS['danger']
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 8px 0; padding: 12px; 
                background: {COLORS['card']}; border-radius: 8px; border-left: 3px solid {color};">
        <span style="font-size: 20px; margin-right: 12px;">{icon}</span>
        <div>
            <div style="font-weight: 600; color: {COLORS['light']};">{rule_name}</div>
            <div style="font-size: 12px; color: #9CA3AF;">{details}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    # Apply custom CSS first
    apply_custom_css()
    
    # Main header
    st.markdown(f"""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="font-size: 42px; margin-bottom: 10px;">⚽ BRUTBALL v6.4</h1>
        <div style="font-size: 18px; color: {COLORS['secondary']}; font-weight: 600;">
            DOUBLE CHANCE ARCHITECTURE | DEFENSIVE VULNERABILITY DETECTION SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="custom-card" style="margin-bottom: 20px;">
            <h3 style="color: {COLORS['light']}; margin-top: 0;">⚙️ Configuration</h3>
        """, unsafe_allow_html=True)
        
        bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=100000, value=1000, step=100)
        base_stake_pct = st.number_input("Base Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: {COLORS['light']}; margin-top: 0;">📁 Select League</h3>
        """, unsafe_allow_html=True)
        
        # League selection
        leagues_dir = "leagues"
        if not os.path.exists(leagues_dir):
            os.makedirs(leagues_dir)
            st.warning(f"Created '{leagues_dir}' directory. Please add your CSV files.")
        
        league_files = [f.replace('.csv', '') for f in os.listdir(leagues_dir) if f.endswith('.csv')]
        
        if not league_files:
            st.error("No CSV files found in 'leagues' folder. Please add your league CSV files.")
            st.stop()
        
        selected_league = st.selectbox("Choose League", league_files, key="league_select")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if selected_league:
            try:
                # Initialize engine
                engine = Brutballv64(selected_league)
                teams = engine.get_available_teams()
                
                # Match selection
                st.markdown(f"""
                <div class="custom-card">
                    <h3 style="color: {COLORS['light']}; margin-top: 0;">🏟️ Match Selection</h3>
                """, unsafe_allow_html=True)
                
                home_col, away_col = st.columns(2)
                with home_col:
                    home_team = st.selectbox("Home Team", teams, key="home_select")
                with away_col:
                    away_team = st.selectbox("Away Team", [t for t in teams if t != home_team], key="away_select")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Analyze button
                if st.button("🚀 Analyze Match", use_container_width=True, type="primary"):
                    with st.spinner("🤖 Running BRUTBALL v6.4 Analysis..."):
                        result = engine.analyze_match(home_team, away_team, bankroll, base_stake_pct)
                        
                        # Display match header
                        st.markdown(f"""
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="font-size: 32px; font-weight: 700; color: {COLORS['light']};">
                                🏆 {result['match']}
                            </div>
                            <div style="display: flex; justify-content: center; margin-top: 15px;">
                        """, unsafe_allow_html=True)
                        
                        create_team_badge(home_team, True)
                        st.markdown('<div style="margin: 0 20px; font-size: 24px; color: #9CA3AF;">VS</div>', unsafe_allow_html=True)
                        create_team_badge(away_team, False)
                        
                        st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Capital metrics
                        capital = result['capital']
                        st.markdown(f"""
                        <div class="custom-card">
                            <h3 style="color: {COLORS['light']}; margin-top: 0;">💰 Capital Management</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px;">
                        """, unsafe_allow_html=True)
                        
                        mode_color = COLORS['success'] if capital['mode'] == 'LOCK_MODE' else COLORS['warning']
                        create_metric_card("Mode", capital['mode'], f"{capital['multiplier']}x", mode_color)
                        create_metric_card("Base Stake", f"${capital['base_stake']:.2f}", f"{base_stake_pct}%")
                        create_metric_card("Final Stake", f"${capital['final_stake']:.2f}")
                        
                        st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Betting recommendations
                        if result['recommendations']:
                            st.markdown(f"""
                            <div class="custom-card">
                                <h3 style="color: {COLORS['light']}; margin-top: 0;">🎯 Betting Recommendations</h3>
                                <div style="margin-top: 20px;">
                            """, unsafe_allow_html=True)
                            
                            for rec in result['recommendations']:
                                create_bet_card(rec)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Team comparison
                        st.markdown(f"""
                        <div class="custom-card">
                            <h3 style="color: {COLORS['light']}; margin-top: 0;">📊 Team Comparison</h3>
                            <div style="margin-top: 20px;">
                        """, unsafe_allow_html=True)
                        
                        comp_col1, comp_col2, comp_col3 = st.columns(3)
                        
                        with comp_col1:
                            create_metric_card(
                                f"{home_team} Home xG",
                                f"{result['home_data'].get('home_xg_per_match', 0):.2f}",
                                color=COLORS['primary']
                            )
                        with comp_col2:
                            create_metric_card(
                                f"{away_team} Away xGA",
                                f"{result['away_data'].get('away_xga_per_match', 0):.2f}",
                                color=COLORS['accent']
                            )
                        with comp_col3:
                            create_metric_card(
                                "Delta",
                                f"{result['home_data'].get('home_xg_per_match', 0) - result['away_data'].get('away_xga_per_match', 0):.2f}",
                                color=COLORS['secondary']
                            )
                        
                        # Last 5 form
                        st.markdown("<div style='margin-top: 20px; font-weight: 600; color: #D1D5DB;'>Last 5 Matches Form</div>", unsafe_allow_html=True)
                        
                        form_col1, form_col2 = st.columns(2)
                        with form_col1:
                            create_metric_card(
                                f"{home_team} Avg Scored",
                                f"{result['home_data']['avg_scored_last_5']:.1f}",
                                color=COLORS['success']
                            )
                        with form_col2:
                            create_metric_card(
                                f"{away_team} Avg Scored",
                                f"{result['away_data']['avg_scored_last_5']:.1f}",
                                color=COLORS['success']
                            )
                        
                        st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # System info (collapsible)
                        with st.expander("📚 System Information & Logic Flow"):
                            st.markdown(f"""
                            <div style="background: {COLORS['card']}; padding: 20px; border-radius: 8px;">
                                <h4 style="color: {COLORS['light']};">BRUTBALL v6.4 Architecture</h4>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                                    <div class="custom-card" style="padding: 15px;">
                                        <div style="color: {COLORS['secondary']}; font-weight: 600;">Tier 1</div>
                                        <div>Edge Detection (v6.0)</div>
                                    </div>
                                    <div class="custom-card" style="padding: 15px;">
                                        <div style="color: {COLORS['secondary']}; font-weight: 600;">Tier 1+</div>
                                        <div>Edge-Derived Under 1.5 Locks</div>
                                    </div>
                                    <div class="custom-card" style="padding: 15px;">
                                        <div style="color: {COLORS['secondary']}; font-weight: 600;">Tier 2</div>
                                        <div>Agency-State Lock Engine</div>
                                    </div>
                                    <div class="custom-card" style="padding: 15px;">
                                        <div style="color: {COLORS['secondary']}; font-weight: 600;">Tier 3</div>
                                        <div>Totals Lock Engine</div>
                                    </div>
                                </div>
                                
                                <h4 style="color: {COLORS['light']}; margin-top: 20px;">Primary Market</h4>
                                <div class="custom-card" style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid {COLORS['success']};">
                                    <div style="font-weight: 600; color: {COLORS['success']};">DOUBLE CHANCE (Win OR Draw)</div>
                                    <div style="color: #9CA3AF; margin-top: 5px;">Higher probability, more consistent returns</div>
                                </div>
                                
                                <h4 style="color: {COLORS['light']}; margin-top: 20px;">Data Source</h4>
                                <div style="color: #9CA3AF;">Last 5 matches only for all trend-based logic</div>
                            </div>
                            """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Make sure your CSV file is in the correct format and located in the 'leagues' folder.")
    
    with col2:
        # Right sidebar - Quick stats
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: {COLORS['light']}; margin-top: 0;">📈 System Status</h3>
            <div style="margin-top: 20px;">
        """, unsafe_allow_html=True)
        
        # System metrics
        create_metric_card("Active Leagues", str(len(league_files)), "CSV files")
        
        if 'result' in locals():
            locks_count = len(result.get('agency_locks', [])) + len(result.get('edge_locks', []))
            if result.get('totals_lock'):
                locks_count += 1
            
            lock_color = COLORS['success'] if locks_count > 0 else COLORS['warning']
            create_metric_card("Locks Detected", str(locks_count), color=lock_color)
            
            # Gate indicators
            st.markdown("<div style='margin-top: 20px; font-weight: 600; color: #D1D5DB;'>Gate Analysis</div>", unsafe_allow_html=True)
            
            if result.get('agency_locks'):
                for lock in result['agency_locks'][:2]:  # Show first 2 locks
                    create_rule_indicator(
                        lock['market'].split()[0],
                        True,
                        f"Δ={lock.get('control_delta', 0):.2f}"
                    )
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Help section
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: {COLORS['light']}; margin-top: 0;">ℹ️ Quick Guide</h3>
            <div style="margin-top: 15px; color: #9CA3AF; font-size: 14px;">
                <div style="margin-bottom: 10px;">
                    <span style="color: {COLORS['success']}; font-weight: 600;">LOCK MODE:</span> 2.0x multiplier<br>
                    <small>Triggered by any lock detection</small>
                </div>
                <div style="margin-bottom: 10px;">
                    <span style="color: {COLORS['warning']}; font-weight: 600;">EDGE MODE:</span> 1.0x multiplier<br>
                    <small>No locks detected</small>
                </div>
                <div style="margin-bottom: 10px;">
                    <span style="color: {COLORS['info']}; font-weight: 600;">DOUBLE CHANCE:</span> Win OR Draw<br>
                    <small>Primary betting market</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()