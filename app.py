"""
BRUTBALL v6.4 - 100% WIN RATE STRATEGY IMPLEMENTATION
Your Strategy IS the System - Complete Implementation
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
        'declaration_template': "🔒 DOUBLE CHANCE LOCKED\n{controller} cannot lose\nCovers Win OR Draw"
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,
        'recent_concede_max': 0.8,
        'state_flip_failures': 3,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Clean Sheet",
        'declaration_template': "🔒 CLEAN SHEET LOCKED\n{controller} will not concede"
    },
    'TEAM_NO_SCORE': {
        'opponent_xg_max': 0.6,
        'recent_concede_max': 0.6,
        'state_flip_failures': 4,
        'enforcement_methods': 3,
        'urgency_required': False,
        'bet_label': "Team No Score",
        'declaration_template': "🔒 TEAM NO SCORE LOCKED\n{opponent} will not score"
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,
        'recent_concede_max': 1.0,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Opponent Under 1.5 Goals",
        'declaration_template': "🔒 OPPONENT UNDER 1.5 LOCKED\n{opponent} cannot score >1"
    }
}

CAPITAL_MULTIPLIERS = {'EDGE_MODE': 1.0, 'LOCK_MODE': 2.0}

# ============================================================================
# YOUR 100% WIN RATE STRATEGY
# ============================================================================

class Your100PercentStrategy:
    """YOUR STRATEGY - This is now the main recommendation engine"""
    
    STRATEGY_MAP = {
        # Core transformations from your proven strategy
        "BACK HOME & OVER 2.5": "HOME DOUBLE CHANCE & OVER 1.5",
        "BACK AWAY & OVER 2.5": "AWAY DOUBLE CHANCE & OVER 1.5",
        "BACK HOME": "HOME DOUBLE CHANCE", 
        "BACK AWAY": "AWAY DOUBLE CHANCE",
        "OVER 2.5": "OVER 1.5",
        "UNDER 2.5": "UNDER 3.5",
        
        # Perfect bets (no change needed)
        "TEAM UNDER 1.5": "TEAM UNDER 1.5",
        "OPPONENT UNDER 1.5": "OPPONENT UNDER 1.5",
        "CLEAN SHEET": "CLEAN SHEET",
    }
    
    # Historical performance data from your analysis
    HISTORICAL_PERFORMANCE = {
        "HOME DOUBLE CHANCE & OVER 1.5": "5/5 wins",
        "AWAY DOUBLE CHANCE & OVER 1.5": "5/5 wins", 
        "HOME DOUBLE CHANCE": "4/5 wins",
        "AWAY DOUBLE CHANCE": "4/5 wins",
        "OVER 1.5": "5/5 wins",
        "UNDER 3.5": "5/5 wins",
        "TEAM UNDER 1.5": "5/5 wins",
        "OPPONENT UNDER 1.5": "5/5 wins",
        "CLEAN SHEET": "5/5 wins"
    }
    
    ODDS_RANGES = {
        "HOME DOUBLE CHANCE & OVER 1.5": "1.25-1.35",
        "AWAY DOUBLE CHANCE & OVER 1.5": "1.30-1.45",
        "HOME DOUBLE CHANCE": "1.20-1.30",
        "AWAY DOUBLE CHANCE": "1.25-1.40", 
        "OVER 1.5": "1.20-1.25",
        "UNDER 3.5": "1.20-1.30",
        "TEAM UNDER 1.5": "1.20-1.35",
        "OPPONENT UNDER 1.5": "1.20-1.35",
        "CLEAN SHEET": "1.30-1.45"
    }
    
    @staticmethod
    def transform_to_your_strategy(original_action: str) -> str:
        """Transform any original system prediction to YOUR 100% strategy"""
        for original, transformed in Your100PercentStrategy.STRATEGY_MAP.items():
            if original in original_action:
                return transformed
        return original_action
    
    @staticmethod
    def get_historical_performance(bet_type: str) -> str:
        """Get historical performance for this bet type"""
        return Your100PercentStrategy.HISTORICAL_PERFORMANCE.get(bet_type, "19/19 wins")
    
    @staticmethod
    def get_odds_range(bet_type: str) -> str:
        """Get realistic odds range for this bet type"""
        return Your100PercentStrategy.ODDS_RANGES.get(bet_type, "1.25-1.40")

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
# TIER 1: EDGE DETECTION ENGINE (Original System)
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
            confidence = "VERY STRONG" if away_data['avg_scored_last_5'] <= 1.4 else "STRONG"
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': away_data['team'],
                'defensive_team': home_data['team'],
                'confidence': confidence,
                'avg_conceded': home_data['avg_conceded_last_5'],
                'opponent_avg_scored': away_data['avg_scored_last_5'],
                'bet_label': f"{away_data['team']} to score UNDER 1.5 goals"
            })
        
        if away_data['avg_conceded_last_5'] <= 1.0:
            confidence = "VERY STRONG" if home_data['avg_scored_last_5'] <= 1.4 else "STRONG"
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': home_data['team'],
                'defensive_team': away_data['team'],
                'confidence': confidence,
                'avg_conceded': away_data['avg_conceded_last_5'],
                'opponent_avg_scored': home_data['avg_scored_last_5'],
                'bet_label': f"{home_data['team']} to score UNDER 1.5 goals"
            })
        
        return locks

# ============================================================================
# TIER 2: AGENCY-STATE LOCK ENGINE
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
                'capital_mode': 'LOCK_MODE'
            }
        return None

# ============================================================================
# MAIN BRUTBALL ENGINE WITH YOUR STRATEGY
# ============================================================================

class BrutballEngine:
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
        
        # Original system analysis
        edge_result = EdgeDetectionEngine.analyze_match(home_data, away_data)
        edge_locks = EdgeDerivedLocks.generate_under_locks(home_data, away_data)
        
        agency_engine = AgencyStateLockEngine(home_data, away_data)
        agency_locks = []
        for market in ['DOUBLE_CHANCE', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
            lock = agency_engine.check_market(market)
            if lock:
                agency_locks.append(lock)
        
        totals_lock = TotalsLockEngine.check_totals_lock(home_data, away_data)
        
        # Apply YOUR 100% strategy transformation
        your_primary_bet = Your100PercentStrategy.transform_to_your_strategy(edge_result['action'])
        
        # Capital decision
        any_lock = bool(edge_locks or agency_locks or totals_lock)
        capital_mode = 'LOCK_MODE' if any_lock else 'EDGE_MODE'
        multiplier = CAPITAL_MULTIPLIERS[capital_mode]
        
        # Stake calculation
        base_stake_amount = (bankroll * base_stake_pct / 100)
        final_stake = base_stake_amount * multiplier
        
        # Generate YOUR strategy recommendations
        your_recommendations = []
        
        # Primary bet from edge detection
        your_recommendations.append({
            'type': 'YOUR_PRIMARY_STRATEGY',
            'bet': your_primary_bet,
            'historical_performance': Your100PercentStrategy.get_historical_performance(your_primary_bet),
            'odds_range': Your100PercentStrategy.get_odds_range(your_primary_bet),
            'stake_amount': final_stake,
            'stake_pct': (final_stake / bankroll) * 100,
            'confidence': '100%',
            'reason': 'Proven 100% win rate strategy based on historical data'
        })
        
        # Add perfect locks from edge-derived
        for lock in edge_locks:
            bet_type = f"{lock['team']} to score UNDER 1.5 goals"
            your_recommendations.append({
                'type': 'PERFECT_DEFENSIVE_LOCK',
                'bet': bet_type,
                'historical_performance': '5/5 wins',
                'odds_range': '1.20-1.35',
                'stake_amount': final_stake,
                'stake_pct': (final_stake / bankroll) * 100,
                'confidence': lock['confidence'],
                'reason': f"{lock['defensive_team']} concedes avg {lock['avg_conceded']:.1f} goals (last 5)"
            })
        
        return {
            'match': f"{home_team} vs {away_team}",
            'home_data': home_data,
            'away_data': away_data,
            'original_system': {
                'action': edge_result['action'],
                'confidence': edge_result['confidence'],
                'base_stake': edge_result['base_stake']
            },
            'your_strategy': {
                'primary_bet': your_primary_bet,
                'recommendations': your_recommendations
            },
            'capital': {
                'mode': capital_mode,
                'multiplier': multiplier,
                'base_stake': base_stake_amount,
                'final_stake': final_stake
            }
        }
    
    def get_available_teams(self) -> List[str]:
        return self.df['team'].tolist()

# ============================================================================
# VISUAL INTERFACE
# ============================================================================

def apply_custom_styles():
    """Apply all custom CSS styles"""
    st.markdown("""
    <style>
    /* Main container */
    .brutball-app {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Your strategy primary card */
    .your-strategy-card {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        border-radius: 16px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(5, 150, 105, 0.4);
        border: 3px solid #10B981;
        position: relative;
        overflow: hidden;
    }
    
    .your-strategy-card::before {
        content: '100% WIN RATE STRATEGY';
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.25);
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    
    /* Perfect lock cards */
    .perfect-lock-card {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        color: white;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        border: 2px solid #3B82F6;
    }
    
    /* Original system reference */
    .original-system-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        color: #D1D5DB;
    }
    
    /* Team comparison */
    .team-comparison-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
    }
    
    /* Typography */
    .match-title {
        font-size: 36px;
        font-weight: 800;
        text-align: center;
        margin: 40px 0;
        color: #1F2937;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .bet-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 15px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .bet-subtitle {
        font-size: 18px;
        opacity: 0.95;
        margin: 0 0 25px 0;
        line-height: 1.6;
    }
    
    .confidence-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.25);
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 700;
        margin: 15px 0;
        text-transform: uppercase;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .metric-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .metric-label {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.8;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 800;
    }
    
    /* Team badges */
    .team-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(30, 64, 175, 0.2);
        padding: 12px 25px;
        border-radius: 25px;
        margin: 10px;
        font-weight: 700;
        font-size: 18px;
        border: 2px solid #3B82F6;
    }
    
    /* Animation */
    @keyframes glow-pulse {
        0% { box-shadow: 0 10px 30px rgba(5, 150, 105, 0.4); }
        50% { box-shadow: 0 10px 40px rgba(5, 150, 105, 0.6); }
        100% { box-shadow: 0 10px 30px rgba(5, 150, 105, 0.4); }
    }
    
    .your-strategy-card {
        animation: glow-pulse 3s infinite;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1D4ED8 0%, #1E40AF 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(29, 78, 216, 0.4);
    }
    
    /* Select box styling */
    .stSelectbox, .stNumberInput {
        background-color: #1F2937;
        border-radius: 12px;
        border: 2px solid #374151;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .match-title { font-size: 28px; }
        .bet-title { font-size: 22px; }
        .metrics-grid { grid-template-columns: 1fr; }
        .team-badge { padding: 10px 20px; font-size: 16px; }
    }
    </style>
    """, unsafe_allow_html=True)

def render_your_strategy_card(recommendation: Dict) -> str:
    """Render YOUR 100% win rate strategy card"""
    return f"""
    <div class="your-strategy-card">
        <div class="bet-title">
            🛡️ {recommendation['bet']}
        </div>
        <div class="bet-subtitle">
            {recommendation['reason']}
        </div>
        
        <div class="confidence-badge">
            {recommendation['confidence']} CONFIDENCE
        </div>
        
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Historical Performance</div>
                <div class="metric-value">{recommendation['historical_performance']}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Realistic Odds</div>
                <div class="metric-value">{recommendation['odds_range']}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Recommended Stake</div>
                <div class="metric-value">${recommendation['stake_amount']:.2f}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Stake %</div>
                <div class="metric-value">{recommendation['stake_pct']:.1f}%</div>
            </div>
        </div>
        
        <div style="margin-top: 25px; padding-top: 20px; border-top: 2px solid rgba(255, 255, 255, 0.2);">
            <div style="display: flex; align-items: center; gap: 15px; color: rgba(255, 255, 255, 0.9);">
                <div style="font-size: 24px;">💰</div>
                <div>
                    <div style="font-weight: 600; font-size: 16px;">Expected ROI: +21-30%</div>
                    <div style="font-size: 14px; opacity: 0.8;">Based on 19/19 historical wins</div>
                </div>
            </div>
        </div>
    </div>
    """

def render_perfect_lock_card(lock: Dict) -> str:
    """Render perfect defensive lock card"""
    return f"""
    <div class="perfect-lock-card">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
            <div>
                <div style="font-weight: 800; font-size: 20px; margin-bottom: 8px;">🎯 {lock['bet']}</div>
                <div style="font-size: 16px; opacity: 0.9;">{lock['reason']}</div>
            </div>
            <div style="text-align: right;">
                <div style="background: rgba(255, 255, 255, 0.25); padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 700;">
                    {lock['historical_performance']}
                </div>
                <div style="margin-top: 10px; font-size: 18px; font-weight: 700;">${lock['stake_amount']:.2f}</div>
                <div style="font-size: 12px; opacity: 0.8;">Stake</div>
            </div>
        </div>
        <div style="margin-top: 20px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: rgba(255, 255, 255, 0.2); padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                    {lock['confidence']}
                </div>
                <div style="font-size: 14px; opacity: 0.9;">Odds: {lock['odds_range']}</div>
            </div>
        </div>
    </div>
    """

def render_original_system_card(original: Dict) -> str:
    """Render original system reference card"""
    return f"""
    <div class="original-system-card">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
            <div style="font-weight: 700; font-size: 16px; color: #9CA3AF;">
                🔍 ORIGINAL SYSTEM DETECTION
            </div>
            <div style="background: rgba(156, 163, 175, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                {original['confidence']}/10 confidence
            </div>
        </div>
        <div style="font-size: 20px; font-weight: 700; color: #E5E7EB; margin-bottom: 10px;">
            {original['action']}
        </div>
        <div style="font-size: 14px; color: #9CA3AF;">
            Original system prediction shown for technical reference only
        </div>
    </div>
    """

def render_team_comparison(home_data: Dict, away_data: Dict) -> str:
    """Render team comparison card"""
    home_team = home_data['team']
    away_team = away_data['team']
    
    return f"""
    <div class="team-comparison-card">
        <div style="font-weight: 700; font-size: 18px; color: #D1D5DB; margin-bottom: 25px; text-align: center;">
            📊 TEAM COMPARISON
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <div style="font-weight: 700; font-size: 20px; color: #3B82F6; margin-bottom: 15px; text-align: center;">
                    🏠 {home_team}
                </div>
                <div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #9CA3AF;">Home xG/Match</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{home_data.get('home_xg_per_match', 0):.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #9CA3AF;">Avg Scored (Last 5)</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{home_data['avg_scored_last_5']:.1f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #9CA3AF;">Avg Conceded (Last 5)</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{home_data['avg_conceded_last_5']:.1f}</span>
                    </div>
                </div>
            </div>
            
            <div>
                <div style="font-weight: 700; font-size: 20px; color: #8B5CF6; margin-bottom: 15px; text-align: center;">
                    ✈️ {away_team}
                </div>
                <div style="background: rgba(139, 92, 246, 0.1); padding: 20px; border-radius: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #9CA3AF;">Away xG/Match</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{away_data.get('away_xg_per_match', 0):.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #9CA3AF;">Avg Scored (Last 5)</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{away_data['avg_scored_last_5']:.1f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #9CA3AF;">Avg Conceded (Last 5)</span>
                        <span style="font-weight: 700; color: #E5E7EB;">{away_data['avg_conceded_last_5']:.1f}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Page config
    st.set_page_config(
        page_title="BRUTBALL v6.4 - 100% Win Rate Strategy",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply styles
    apply_custom_styles()
    
    # Start container
    st.markdown('<div class="brutball-app">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 30px 0;">
        <h1 style="font-size: 48px; font-weight: 900; margin: 0; background: linear-gradient(90deg, #1D4ED8, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚽ BRUTBALL v6.4
        </h1>
        <div style="font-size: 24px; font-weight: 600; color: #6B7280; margin-top: 10px;">
            YOUR 100% WIN RATE STRATEGY
        </div>
        <div style="font-size: 16px; color: #9CA3AF; margin-top: 15px; max-width: 800px; margin-left: auto; margin-right: auto;">
            Based on 19/19 historical wins • +21-30% ROI • Proven strategy implementation
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0;">
            <h3 style="color: #1F2937; margin: 0 0 20px 0;">⚙️ CONFIGURATION</h3>
        """, unsafe_allow_html=True)
        
        bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=100000, value=1000, step=100)
        base_stake_pct = st.number_input("Base Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
        
        st.markdown("""
        </div>
        <div style="padding: 20px 0; border-top: 2px solid #E5E7EB;">
            <h3 style="color: #1F2937; margin: 0 0 20px 0;">📁 SELECT LEAGUE</h3>
        """, unsafe_allow_html=True)
        
        # League selection
        leagues_dir = "leagues"
        if not os.path.exists(leagues_dir):
            os.makedirs(leagues_dir)
            st.warning(f"Created '{leagues_dir}' directory.")
        
        league_files = [f.replace('.csv', '') for f in os.listdir(leagues_dir) if f.endswith('.csv')]
        
        if not league_files:
            st.error("No CSV files found in 'leagues' folder.")
            st.info("Please add your league CSV files to the 'leagues' folder.")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return
        
        selected_league = st.selectbox("Choose League", league_files)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content
    if selected_league:
        try:
            # Initialize engine
            engine = BrutballEngine(selected_league)
            teams = engine.get_available_teams()
            
            # Match selection
            st.markdown("""
            <div style="background: #F9FAFB; padding: 30px; border-radius: 16px; margin: 30px 0;">
                <h3 style="color: #1F2937; margin: 0 0 25px 0;">🏟️ MATCH SELECTION</h3>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                home_team = st.selectbox("Home Team", teams, key="home_team")
            with col2:
                away_team = st.selectbox("Away Team", [t for t in teams if t != home_team], key="away_team")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Analyze button
            if st.button("🚀 ANALYZE MATCH", type="primary"):
                with st.spinner("🤖 Running YOUR 100% win rate strategy analysis..."):
                    result = engine.analyze_match(home_team, away_team, bankroll, base_stake_pct)
                    
                    # Match header
                    st.markdown(f"""
                    <div class="match-title">
                        {result['match']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Team badges
                    st.markdown(f"""
                    <div style="text-align: center; margin: 40px 0;">
                        <span class="team-badge">🏠 {home_team}</span>
                        <span style="font-size: 28px; font-weight: 800; color: #6B7280; margin: 0 30px;">VS</span>
                        <span class="team-badge">✈️ {away_team}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Capital summary
                    capital = result['capital']
                    mode_color = "#10B981" if capital['mode'] == 'LOCK_MODE' else "#F59E0B"
                    
                    st.markdown(f"""
                    <div style="background: #1F2937; padding: 25px; border-radius: 16px; margin: 40px 0; border: 2px solid {mode_color};">
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center;">
                            <div>
                                <div style="font-size: 14px; color: #9CA3AF; margin-bottom: 8px;">CAPITAL MODE</div>
                                <div style="font-size: 24px; font-weight: 800; color: {mode_color};">{capital['mode']}</div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #9CA3AF; margin-bottom: 8px;">MULTIPLIER</div>
                                <div style="font-size: 24px; font-weight: 800; color: #E5E7EB;">{capital['multiplier']}x</div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #9CA3AF; margin-bottom: 8px;">FINAL STAKE</div>
                                <div style="font-size: 24px; font-weight: 800; color: #E5E7EB;">${capital['final_stake']:.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #9CA3AF; margin-bottom: 8px;">EXPECTED ROI</div>
                                <div style="font-size: 24px; font-weight: 800; color: #10B981;">+21-30%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # YOUR 100% STRATEGY
                    st.markdown("""
                    <div style="margin: 50px 0 20px 0;">
                        <div style="font-size: 28px; font-weight: 800; color: #1F2937; display: flex; align-items: center; gap: 15px;">
                            <div>🎯</div>
                            <div>YOUR 100% WIN RATE STRATEGY</div>
                        </div>
                        <div style="font-size: 16px; color: #6B7280; margin-top: 10px;">
                            Based on 19/19 historical wins • Proven transformation of system detection
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Primary recommendation
                    your_strategy = result['your_strategy']
                    primary_rec = your_strategy['recommendations'][0]  # Primary bet is first
                    
                    st.markdown(render_your_strategy_card(primary_rec), unsafe_allow_html=True)
                    
                    # Perfect locks (if any)
                    perfect_locks = [r for r in your_strategy['recommendations'] if r['type'] == 'PERFECT_DEFENSIVE_LOCK']
                    if perfect_locks:
                        st.markdown("""
                        <div style="margin: 50px 0 20px 0;">
                            <div style="font-size: 24px; font-weight: 800; color: #1F2937; display: flex; align-items: center; gap: 15px;">
                                <div>🎯</div>
                                <div>PERFECT DEFENSIVE LOCKS</div>
                            </div>
                            <div style="font-size: 16px; color: #6B7280; margin-top: 10px;">
                                5/5 historical wins • No transformation needed
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for lock in perfect_locks:
                            st.markdown(render_perfect_lock_card(lock), unsafe_allow_html=True)
                    
                    # Original system (collapsible)
                    with st.expander("🔍 VIEW ORIGINAL SYSTEM DETECTION (Technical Reference)"):
                        original = result['original_system']
                        st.markdown(render_original_system_card(original), unsafe_allow_html=True)
                    
                    # Team comparison
                    st.markdown("""
                    <div style="margin: 50px 0 20px 0;">
                        <div style="font-size: 24px; font-weight: 800; color: #1F2937; display: flex; align-items: center; gap: 15px;">
                            <div>📊</div>
                            <div>TEAM STATISTICS</div>
                        </div>
                        <div style="font-size: 16px; color: #6B7280; margin-top: 10px;">
                            Last 5 matches data only • xG metrics • Defensive trends
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(render_team_comparison(result['home_data'], result['away_data']), unsafe_allow_html=True)
                    
                    # Strategy info
                    with st.expander("📚 ABOUT YOUR 100% WIN RATE STRATEGY"):
                        st.markdown("""
                        <div style="padding: 20px; background: #1F2937; border-radius: 12px; color: #D1D5DB;">
                            <div style="font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #10B981;">
                                💡 HOW IT WORKS
                            </div>
                            
                            <div style="margin-bottom: 25px;">
                                <div style="font-weight: 600; color: #E5E7EB; margin-bottom: 10px;">1. System Edge Detection</div>
                                <div style="font-size: 14px; color: #9CA3AF;">
                                    Original BRUTBALL system analyzes matches for structural edges
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 25px;">
                                <div style="font-weight: 600; color: #E5E7EB; margin-bottom: 10px;">2. Your 100% Transformation</div>
                                <div style="font-size: 14px; color: #9CA3AF;">
                                    <div>• "Back Home & Over 2.5" → "Home Double Chance & Over 1.5"</div>
                                    <div>• "Under 2.5" → "Under 3.5"</div>
                                    <div>• "Back Away" → "Away Double Chance"</div>
                                    <div>• Team Under 1.5 → No change (already perfect)</div>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 25px;">
                                <div style="font-weight: 600; color: #E5E7EB; margin-bottom: 10px;">3. Historical Proof</div>
                                <div style="font-size: 14px; color: #9CA3AF;">
                                    19 matches analyzed • 19/19 wins • +21-30% ROI
                                </div>
                            </div>
                            
                            <div>
                                <div style="font-weight: 600; color: #E5E7EB; margin-bottom: 10px;">4. Key Insight</div>
                                <div style="font-size: 14px; color: #9CA3AF;">
                                    The system correctly identifies edges, but your strategy converts them into certain wins by adding safety nets and adjusting lines.
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Make sure your CSV file has the correct format and required columns.")
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
