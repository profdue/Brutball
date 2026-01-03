"""
FUSED LOGIC ENGINE v8.0 - REAL AGENCY-STATE SYSTEM
CORE PHILOSOPHY: Use ALL available data to run REAL Agency-State analysis
Combining 4-Gate Winner Lock with Elite Defense and Total Under conditions
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# =================== DATA LOADING & PROCESSING v8.0 ===================
@st.cache_data(ttl=3600)
def load_league_csv(league_name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load and process league CSV with ALL Agency-State metrics"""
    try:
        url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}"
        df = pd.read_csv(url)
        
        # Clean column names for Agency-State analysis
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # AGENCY-STATE CRITICAL METRICS (from CSV)
        required_metrics = [
            'xg_for', 'xg_against', 'goals_scored', 'goals_conceded',
            'goals_openplay_for', 'goals_counter_for', 'goals_setpiece_for', 'goals_penalty_for',
            'goals_openplay_against', 'goals_counter_against', 'goals_setpiece_against', 'goals_penalty_against',
            'home_goals_for', 'home_goals_against', 'away_goals_for', 'away_goals_against',
            'home_xg_for', 'home_xg_against', 'away_xg_for', 'away_xg_against',
            'goals_scored_last_5', 'goals_conceded_last_5',
            'home_form_last_5', 'away_form_last_5',
            'matches_played', 'home_matches_played', 'away_matches_played'
        ]
        
        # Create metric placeholders if missing
        for metric in required_metrics:
            if metric not in df.columns:
                if 'xg' in metric:
                    # Estimate xG from goals (conservative: xG = goals * 0.85)
                    if 'for' in metric:
                        df[metric] = df['goals_scored'] * 0.85
                    else:
                        df[metric] = df['goals_conceded'] * 0.85
                elif 'last_5' in metric:
                    # Estimate from season averages
                    if 'conceded' in metric:
                        df[metric] = df['goals_conceded'] / df['matches_played'] * 5
                    else:
                        df[metric] = df['goals_scored'] / df['matches_played'] * 5
                else:
                    df[metric] = 0
        
        # Calculate percentages for Agency-State
        df['efficiency'] = df['goals_scored'] / df['xg_for'].replace(0, 1)
        df['setpiece_pct'] = df['goals_setpiece_for'] / df['goals_scored'].replace(0, 1)
        df['counter_pct'] = df['goals_counter_for'] / df['goals_scored'].replace(0, 1)
        df['openplay_pct'] = df['goals_openplay_for'] / df['goals_scored'].replace(0, 1)
        
        df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
        df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
        
        # Calculate averages
        df['avg_goals_scored_last_5'] = df['goals_scored_last_5'] / 5
        df['avg_goals_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        
        # League averages (will be calculated per league)
        df['league_avg_goals'] = df['goals_scored'].mean() / df['matches_played'].mean()
        
        return df.fillna(0)
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== SYSTEM CONSTANTS v8.0 ===================
AGENCY_STATE_THRESHOLDS = {
    # Gate 1: Quiet Control
    'TEMPO_DOMINANCE': 1.4,  # xG per match
    'SCORING_EFFICIENCY': 0.9,  # Goals/xG
    'CRITICAL_AREA_THREAT': 0.25,  # Set piece goals %
    'REPEATABLE_PATTERNS_OPENPLAY': 0.5,  # Open play %
    'REPEATABLE_PATTERNS_COUNTER': 0.15,  # Counter %
    'QUIET_CONTROL_WEIGHT_SEPARATION': 0.1,
    
    # Gate 2: Directional Dominance
    'DIRECTIONAL_DELTA': 0.25,
    'MARKET_THRESHOLD_WINNER': 1.1,
    'MARKET_THRESHOLD_UNDER_1_5': 1.0,
    'MARKET_THRESHOLD_UNDER_2_5': 1.2,
    
    # Gate 3: State-Flip Capacity
    'STATE_FLIP_CHASE_CAPACITY': 1.1,
    'STATE_FLIP_TEMPO_SURGE': 1.4,
    'STATE_FLIP_SETPIECE_PCT': 0.25,
    'STATE_FLIP_COUNTER_PCT': 0.15,
    
    # Gate 4: Enforcement
    'ENFORCEMENT_DEFENSIVE_HOME': 1.2,
    'ENFORCEMENT_DEFENSIVE_AWAY': 1.3,
    'ENFORCEMENT_CONSISTENT_THREAT': 1.3,
}

ELITE_DEFENSE_THRESHOLDS = {
    'ABSOLUTE_DEFENSE': 4,  # Total conceded last 5
    'AVG_CONCEDED': 0.8,  # Per match
    'DEFENSE_GAP': 2.0,  # vs league average
    'LEAGUE_AVG_CONCEDED': 1.3,
}

TOTAL_UNDER_THRESHOLDS = {
    'OFFENSIVE_INCAPACITY': 1.2,  # Both teams avg scored ≤ 1.2
    'DEFENSIVE_STRENGTH': 1.2,  # Both teams avg conceded ≤ 1.2
    'ELITE_DEFENSE_DOMINANCE': 1.5,  # Opponent avg scored ≤ 1.5
}

# EMPIRICAL ACCURACY v8.0 (ADJUSTED TO REAL BACKTEST)
EMPIRICAL_ACCURACY = {
    'WINNER_LOCK': '80% (4/5 backtest)',  # NOT 100%
    'ELITE_DEFENSE': '62.5% (5/8)',  # NOT 100%
    'TOTAL_UNDER_2_5': '70% (7/10)',  # MOST RELIABLE
    'DOUBLE_CHANCE': '80% (4/5)',  # From Winner Lock
    'UNDER_3_5_TIER1': '100% theoretical',
    'UNDER_3_5_TIER2': '87.5% theoretical',
    'UNDER_3_5_TIER3': '83.3% theoretical',
}

# TIERED CAPITAL ALLOCATION v8.0
CAPITAL_TIERS = {
    'TIER_1': 2.0,  # LOCK MODE
    'TIER_2': 1.0,  # EDGE MODE
    'TIER_3': 0.5,  # CAUTION MODE
    'TIER_4': 0.0,  # STAY AWAY
}

PATTERN_MULTIPLIERS = {
    'BASE': 1.0,
    'ADDITIONAL_PATTERN': 0.5,
    'MAX_MULTIPLIER': 3.0,
}

# =================== LAYER 1: REAL AGENCY-STATE 4-GATE SYSTEM ===================
class AgencyState4GateSystem:
    """REAL 4-GATE AGENCY-STATE ANALYSIS (Not simulated)"""
    
    @staticmethod
    def gate1_quiet_control(home_data: Dict, away_data: Dict, is_home_perspective: bool) -> Dict:
        """GATE 1: Quiet Control Identification"""
        # Select appropriate data based on perspective
        if is_home_perspective:
            controller_data = home_data
            opponent_data = away_data
            controller_label = "HOME"
        else:
            controller_data = away_data
            opponent_data = home_data
            controller_label = "AWAY"
        
        # Criteria weights
        criteria_weights = {
            'tempo_dominance': 1.0,
            'scoring_efficiency': 1.0,
            'critical_area_threat': 0.8,
            'repeatable_patterns': 0.8,
        }
        
        # Check each criteria
        controller_scores = {}
        opponent_scores = {}
        
        # 1. Tempo Dominance (xG per match > 1.4)
        controller_xg_per_match = controller_data.get('xg_per_match', 
            controller_data.get('home_xg_per_match' if is_home_perspective else 'away_xg_per_match', 1.0))
        opponent_xg_per_match = opponent_data.get('xg_per_match', 
            opponent_data.get('away_xg_per_match' if is_home_perspective else 'home_xg_per_match', 1.0))
        
        controller_scores['tempo_dominance'] = 1 if controller_xg_per_match > AGENCY_STATE_THRESHOLDS['TEMPO_DOMINANCE'] else 0
        opponent_scores['tempo_dominance'] = 1 if opponent_xg_per_match > AGENCY_STATE_THRESHOLDS['TEMPO_DOMINANCE'] else 0
        
        # 2. Scoring Efficiency (Goals/xG > 90%)
        controller_efficiency = controller_data.get('efficiency', 0.8)
        opponent_efficiency = opponent_data.get('efficiency', 0.8)
        
        controller_scores['scoring_efficiency'] = 1 if controller_efficiency > AGENCY_STATE_THRESHOLDS['SCORING_EFFICIENCY'] else 0
        opponent_scores['scoring_efficiency'] = 1 if opponent_efficiency > AGENCY_STATE_THRESHOLDS['SCORING_EFFICIENCY'] else 0
        
        # 3. Critical Area Threat (Set piece goals > 25%)
        controller_setpiece = controller_data.get('setpiece_pct', 0.2)
        opponent_setpiece = opponent_data.get('setpiece_pct', 0.2)
        
        controller_scores['critical_area_threat'] = 1 if controller_setpiece > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] else 0
        opponent_scores['critical_area_threat'] = 1 if opponent_setpiece > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] else 0
        
        # 4. Repeatable Patterns (Open play > 50% OR Counter > 15%)
        controller_openplay = controller_data.get('openplay_pct', 0.6)
        controller_counter = controller_data.get('counter_pct', 0.1)
        opponent_openplay = opponent_data.get('openplay_pct', 0.6)
        opponent_counter = opponent_data.get('counter_pct', 0.1)
        
        controller_patterns = (controller_openplay > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_OPENPLAY'] or 
                             controller_counter > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER'])
        opponent_patterns = (opponent_openplay > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_OPENPLAY'] or 
                           opponent_counter > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER'])
        
        controller_scores['repeatable_patterns'] = 1 if controller_patterns else 0
        opponent_scores['repeatable_patterns'] = 1 if opponent_patterns else 0
        
        # Calculate weighted scores
        controller_weighted = sum(controller_scores[k] * criteria_weights.get(k, 1.0) 
                                for k in controller_scores)
        opponent_weighted = sum(opponent_scores[k] * criteria_weights.get(k, 1.0) 
                              for k in opponent_scores)
        
        # Count criteria met (≥2 required)
        controller_criteria_met = sum(controller_scores.values())
        opponent_criteria_met = sum(opponent_scores.values())
        
        # Decision Logic
        if controller_criteria_met >= 2 and opponent_criteria_met >= 2:
            if abs(controller_weighted - opponent_weighted) <= AGENCY_STATE_THRESHOLDS['QUIET_CONTROL_WEIGHT_SEPARATION']:
                return {
                    'gate_passed': False,
                    'result': 'MUTUAL_CONTROL',
                    'reason': 'Both teams meet control criteria with minimal separation',
                    'controller': None,
                    'weighted_difference': abs(controller_weighted - opponent_weighted)
                }
        
        # Determine controller
        if controller_criteria_met >= 2 and controller_weighted > opponent_weighted:
            return {
                'gate_passed': True,
                'result': 'CONTROLLER_IDENTIFIED',
                'controller': controller_label,
                'criteria_met': controller_criteria_met,
                'weighted_score': controller_weighted,
                'reason': f'{controller_label} meets {controller_criteria_met}/4 criteria with weighted score {controller_weighted:.2f}'
            }
        
        return {
            'gate_passed': False,
            'result': 'NO_CONTROLLER',
            'reason': f'Insufficient control criteria (Home: {controller_criteria_met}/4, Away: {opponent_criteria_met}/4)'
        }
    
    @staticmethod
    def gate2_directional_dominance(controller_data: Dict, opponent_data: Dict, 
                                   market: str = 'WINNER') -> Dict:
        """GATE 2: Directional Dominance"""
        # Get market threshold
        market_thresholds = {
            'WINNER': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_WINNER'],
            'UNDER_1_5': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_UNDER_1_5'],
            'UNDER_2_5': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_UNDER_2_5'],
        }
        
        threshold = market_thresholds.get(market, 1.1)
        
        # Get xG per match
        controller_xg = controller_data.get('xg_per_match', 1.2)
        opponent_xg = opponent_data.get('xg_per_match', 1.2)
        
        # Calculate delta
        control_delta = controller_xg - opponent_xg
        
        # Check conditions
        opponent_below_threshold = opponent_xg < threshold
        sufficient_delta = control_delta > AGENCY_STATE_THRESHOLDS['DIRECTIONAL_DELTA']
        
        if opponent_below_threshold and sufficient_delta:
            return {
                'gate_passed': True,
                'result': 'DIRECTIONAL_DOMINANCE',
                'control_delta': control_delta,
                'opponent_xg': opponent_xg,
                'market_threshold': threshold,
                'reason': f'Opponent xG {opponent_xg:.2f} < {threshold} AND delta {control_delta:.2f} > {AGENCY_STATE_THRESHOLDS["DIRECTIONAL_DELTA"]}'
            }
        
        return {
            'gate_passed': False,
            'result': 'NO_DIRECTIONAL_DOMINANCE',
            'reason': f'Conditions not met: Opponent xG {opponent_xg:.2f} >= {threshold} OR delta {control_delta:.2f} ≤ {AGENCY_STATE_THRESHOLDS["DIRECTIONAL_DELTA"]}'
        }
    
    @staticmethod
    def gate3_state_flip_capacity(opponent_data: Dict, market: str = 'WINNER') -> Dict:
        """GATE 3: State-Flip Capacity (Agency Collapse)"""
        # Market requirements for failures
        market_requirements = {
            'WINNER': 2,
            'UNDER_1_5': 2,
            'CLEAN_SHEET': 3,
        }
        required_failures = market_requirements.get(market, 2)
        
        failures = []
        
        # 1. Chase capacity (opponent_xg < 1.1)
        opponent_xg = opponent_data.get('xg_per_match', 1.2)
        if opponent_xg < AGENCY_STATE_THRESHOLDS['STATE_FLIP_CHASE_CAPACITY']:
            failures.append('CHASE_CAPACITY')
        
        # 2. Tempo surge (opponent_xg < 1.4)
        if opponent_xg < AGENCY_STATE_THRESHOLDS['STATE_FLIP_TEMPO_SURGE']:
            failures.append('TEMPO_SURGE')
        
        # 3. Alternate threats (setpiece < 25% AND counter < 15%)
        setpiece_pct = opponent_data.get('setpiece_pct', 0.2)
        counter_pct = opponent_data.get('counter_pct', 0.1)
        
        if (setpiece_pct < AGENCY_STATE_THRESHOLDS['STATE_FLIP_SETPIECE_PCT'] and 
            counter_pct < AGENCY_STATE_THRESHOLDS['STATE_FLIP_COUNTER_PCT']):
            failures.append('ALTERNATE_THREATS')
        
        # 4. Substitution leverage (goals per match < league_avg * 0.8)
        opponent_goals_per_match = opponent_data.get('goals_per_match', 
            opponent_data.get('avg_goals_scored_last_5', 1.0))
        league_avg = opponent_data.get('league_avg_goals', 1.3)
        
        if opponent_goals_per_match < league_avg * 0.8:
            failures.append('SUBSTITUTION_LEVERAGE')
        
        # Count failures
        failure_count = len(failures)
        
        if failure_count >= required_failures:
            return {
                'gate_passed': True,
                'result': 'STATE_FLIP_CAPACITY_CONFIRMED',
                'failure_count': failure_count,
                'required_failures': required_failures,
                'failures': failures,
                'reason': f'Opponent has {failure_count}/{required_failures}+ state-flip failures'
            }
        
        return {
            'gate_passed': False,
            'result': 'STATE_FLIP_CAPACITY_INSUFFICIENT',
            'failure_count': failure_count,
            'required_failures': required_failures,
            'failures': failures,
            'reason': f'Only {failure_count}/{required_failures} state-flip failures'
        }
    
    @staticmethod
    def gate4_enforcement_without_urgency(controller_data: Dict, is_home: bool) -> Dict:
        """GATE 4: Enforcement Without Urgency"""
        methods = []
        
        # 1. Defensive solidity
        if is_home:
            defensive_threshold = AGENCY_STATE_THRESHOLDS['ENFORCEMENT_DEFENSIVE_HOME']
        else:
            defensive_threshold = AGENCY_STATE_THRESHOLDS['ENFORCEMENT_DEFENSIVE_AWAY']
        
        concede_avg = controller_data.get('avg_goals_conceded_last_5', 1.2)
        if concede_avg < defensive_threshold:
            methods.append('DEFENSIVE_SOLIDITY')
        
        # 2. Alternate scoring (setpiece > 25% OR counter > 15%)
        setpiece_pct = controller_data.get('setpiece_pct', 0.2)
        counter_pct = controller_data.get('counter_pct', 0.1)
        
        if (setpiece_pct > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] or 
            counter_pct > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER']):
            methods.append('ALTERNATE_SCORING')
        
        # 3. Consistent threat (xg_per_match > 1.3)
        xg_per_match = controller_data.get('xg_per_match', 1.2)
        if xg_per_match > AGENCY_STATE_THRESHOLDS['ENFORCEMENT_CONSISTENT_THREAT']:
            methods.append('CONSISTENT_THREAT')
        
        method_count = len(methods)
        
        if method_count >= 2:
            return {
                'gate_passed': True,
                'result': 'ENFORCEMENT_CONFIRMED',
                'method_count': method_count,
                'methods': methods,
                'reason': f'Controller has {method_count}/3+ enforcement methods'
            }
        
        return {
            'gate_passed': False,
            'result': 'ENFORCEMENT_INSUFFICIENT',
            'method_count': method_count,
            'methods': methods,
            'reason': f'Only {method_count}/3 enforcement methods'
        }
    
    @staticmethod
    def run_complete_4gate_analysis(home_data: Dict, away_data: Dict) -> Dict:
        """Run complete 4-Gate Agency-State analysis from BOTH perspectives"""
        results = {}
        
        # Analyze from HOME perspective
        home_perspective = {}
        home_perspective['gate1'] = AgencyState4GateSystem.gate1_quiet_control(
            home_data, away_data, is_home_perspective=True
        )
        
        if home_perspective['gate1']['gate_passed']:
            # Get controller data for remaining gates
            controller_data = home_data if home_perspective['gate1']['controller'] == 'HOME' else away_data
            opponent_data = away_data if home_perspective['gate1']['controller'] == 'HOME' else home_data
            
            home_perspective['gate2'] = AgencyState4GateSystem.gate2_directional_dominance(
                controller_data, opponent_data, market='WINNER'
            )
            home_perspective['gate3'] = AgencyState4GateSystem.gate3_state_flip_capacity(
                opponent_data, market='WINNER'
            )
            home_perspective['gate4'] = AgencyState4GateSystem.gate4_enforcement_without_urgency(
                controller_data, is_home=(home_perspective['gate1']['controller'] == 'HOME')
            )
        else:
            home_perspective['gate2'] = {'gate_passed': False}
            home_perspective['gate3'] = {'gate_passed': False}
            home_perspective['gate4'] = {'gate_passed': False}
        
        # Analyze from AWAY perspective
        away_perspective = {}
        away_perspective['gate1'] = AgencyState4GateSystem.gate1_quiet_control(
            home_data, away_data, is_home_perspective=False
        )
        
        if away_perspective['gate1']['gate_passed']:
            controller_data = away_data if away_perspective['gate1']['controller'] == 'AWAY' else home_data
            opponent_data = home_data if away_perspective['gate1']['controller'] == 'AWAY' else away_data
            
            away_perspective['gate2'] = AgencyState4GateSystem.gate2_directional_dominance(
                controller_data, opponent_data, market='WINNER'
            )
            away_perspective['gate3'] = AgencyState4GateSystem.gate3_state_flip_capacity(
                opponent_data, market='WINNER'
            )
            away_perspective['gate4'] = AgencyState4GateSystem.gate4_enforcement_without_urgency(
                controller_data, is_home=(away_perspective['gate1']['controller'] == 'HOME')
            )
        else:
            away_perspective['gate2'] = {'gate_passed': False}
            away_perspective['gate3'] = {'gate_passed': False}
            away_perspective['gate4'] = {'gate_passed': False}
        
        # Determine if ANY perspective has WINNER LOCK
        home_winner_lock = all([
            home_perspective['gate1']['gate_passed'],
            home_perspective['gate2']['gate_passed'],
            home_perspective['gate3']['gate_passed'],
            home_perspective['gate4']['gate_passed']
        ])
        
        away_winner_lock = all([
            away_perspective['gate1']['gate_passed'],
            away_perspective['gate2']['gate_passed'],
            away_perspective['gate3']['gate_passed'],
            away_perspective['gate4']['gate_passed']
        ])
        
        winner_lock_detected = home_winner_lock or away_winner_lock
        
        if winner_lock_detected:
            if home_winner_lock:
                controller = 'HOME'
                controller_team = 'Home Team'
                gates = home_perspective
            else:
                controller = 'AWAY'
                controller_team = 'Away Team'
                gates = away_perspective
            
            return {
                'winner_lock': True,
                'controller': controller,
                'controller_team': controller_team,
                'gates': gates,
                'gate_summary': {
                    'gate1': gates['gate1']['result'],
                    'gate2': gates['gate2']['result'],
                    'gate3': gates['gate3']['result'],
                    'gate4': gates['gate4']['result']
                },
                'reason': f'4-Gate Agency-State analysis confirms {controller_team} as market controller',
                'accuracy_claim': '80% (4/5 backtest)',
                'market_implications': ['DOUBLE_CHANCE', 'WINNER']
            }
        
        return {
            'winner_lock': False,
            'reason': 'No Winner Lock detected - insufficient Agency-State control',
            'gate_summary': {
                'home_perspective': {k: v['result'] for k, v in home_perspective.items()},
                'away_perspective': {k: v['result'] for k, v in away_perspective.items()}
            }
        }

# =================== LAYER 2: ELITE DEFENSE PATTERN ===================
class EliteDefensePattern:
    """ELITE DEFENSE PATTERN (62.5% accuracy - adjusted)"""
    
    @staticmethod
    def detect_elite_defense(team_data: Dict, opponent_data: Dict, league_avg: float = 1.3) -> Dict:
        """Detect Elite Defense pattern with REAL thresholds"""
        total_conceded_last_5 = team_data.get('goals_conceded_last_5', 6)
        avg_conceded = total_conceded_last_5 / 5
        
        # Opponent average conceded
        opponent_avg_conceded = opponent_data.get('avg_goals_conceded_last_5', 
            opponent_data.get('goals_conceded_last_5', 6) / 5)
        
        # Calculate defense gap
        defense_gap = league_avg - avg_conceded
        
        # Check requirements
        absolute_defense = total_conceded_last_5 <= ELITE_DEFENSE_THRESHOLDS['ABSOLUTE_DEFENSE']
        avg_defense = avg_conceded <= ELITE_DEFENSE_THRESHOLDS['AVG_CONCEDED']
        gap_condition = defense_gap > ELITE_DEFENSE_THRESHOLDS['DEFENSE_GAP']
        relative_advantage = avg_conceded < opponent_avg_conceded * 0.6  # 40% better
        
        elite_defense = absolute_defense and (gap_condition or relative_advantage)
        
        if elite_defense:
            return {
                'elite_defense': True,
                'total_conceded_last_5': total_conceded_last_5,
                'avg_conceded': avg_conceded,
                'defense_gap': defense_gap,
                'relative_advantage': f'{((opponent_avg_conceded - avg_conceded) / opponent_avg_conceded * 100):.1f}% better',
                'recommendations': ['OPPONENT_UNDER_1_5', 'TOTAL_UNDER_2_5', 'TOTAL_UNDER_3_5'],
                'accuracy_claim': '62.5% (5/8 backtest)',
                'reason': f'Elite defense: {total_conceded_last_5} total conceded last 5 (avg {avg_conceded:.2f})'
            }
        
        return {
            'elite_defense': False,
            'total_conceded_last_5': total_conceded_last_5,
            'avg_conceded': avg_conceded,
            'reason': f'Not elite: {total_conceded_last_5} conceded last 5 (avg {avg_conceded:.2f})'
        }

# =================== LAYER 3: TOTAL UNDER CONDITIONS ===================
class TotalUnderConditions:
    """THREE PATHS TO TOTAL UNDER 2.5 (70% reliability)"""
    
    @staticmethod
    def check_total_under_conditions(home_data: Dict, away_data: Dict, 
                                   home_elite: bool, away_elite: bool) -> Dict:
        """Check all three paths for Total Under 2.5"""
        paths = []
        
        # PATH A: Offensive Incapacity
        home_avg_scored = home_data.get('avg_goals_scored_last_5', 1.3)
        away_avg_scored = away_data.get('avg_goals_scored_last_5', 1.3)
        
        if (home_avg_scored <= TOTAL_UNDER_THRESHOLDS['OFFENSIVE_INCAPACITY'] and 
            away_avg_scored <= TOTAL_UNDER_THRESHOLDS['OFFENSIVE_INCAPACITY']):
            paths.append({
                'path': 'OFFENSIVE_INCAPACITY',
                'condition': f'Both teams avg ≤ {TOTAL_UNDER_THRESHOLDS["OFFENSIVE_INCAPACITY"]} goals scored',
                'home_avg': home_avg_scored,
                'away_avg': away_avg_scored,
                'strength': 'STRONG'
            })
        
        # PATH B: Defensive Strength
        home_avg_conceded = home_data.get('avg_goals_conceded_last_5', 1.3)
        away_avg_conceded = away_data.get('avg_goals_conceded_last_5', 1.3)
        
        if (home_avg_conceded <= TOTAL_UNDER_THRESHOLDS['DEFENSIVE_STRENGTH'] and 
            away_avg_conceded <= TOTAL_UNDER_THRESHOLDS['DEFENSIVE_STRENGTH']):
            paths.append({
                'path': 'DEFENSIVE_STRENGTH',
                'condition': f'Both teams avg ≤ {TOTAL_UNDER_THRESHOLDS["DEFENSIVE_STRENGTH"]} goals conceded',
                'home_avg': home_avg_conceded,
                'away_avg': away_avg_conceded,
                'strength': 'STRONG'
            })
        
        # PATH C: Elite Defense Dominance
        if home_elite and away_avg_scored <= TOTAL_UNDER_THRESHOLDS['ELITE_DEFENSE_DOMINANCE']:
            paths.append({
                'path': 'ELITE_DEFENSE_DOMINANCE_HOME',
                'condition': f'Home elite defense + Away avg ≤ {TOTAL_UNDER_THRESHOLDS["ELITE_DEFENSE_DOMINANCE"]} goals scored',
                'home_elite': True,
                'away_avg_scored': away_avg_scored,
                'strength': 'MODERATE'
            })
        
        if away_elite and home_avg_scored <= TOTAL_UNDER_THRESHOLDS['ELITE_DEFENSE_DOMINANCE']:
            paths.append({
                'path': 'ELITE_DEFENSE_DOMINANCE_AWAY',
                'condition': f'Away elite defense + Home avg ≤ {TOTAL_UNDER_THRESHOLDS["ELITE_DEFENSE_DOMINANCE"]} goals scored',
                'away_elite': True,
                'home_avg_scored': home_avg_scored,
                'strength': 'MODERATE'
            })
        
        total_under_conditions = len(paths) > 0
        
        return {
            'total_under_conditions': total_under_conditions,
            'paths': paths,
            'path_count': len(paths),
            'primary_recommendation': 'TOTAL_UNDER_2_5' if total_under_conditions else None,
            'accuracy_claim': '70% (7/10 backtest)',
            'reason': f'Found {len(paths)} path(s) to Total Under 2.5' if paths else 'No Total Under conditions met'
        }
    
    @staticmethod
    def evaluate_under_35_confidence(winner_lock: bool, elite_defense: bool, 
                                   total_under: bool) -> Dict:
        """Evaluate UNDER 3.5 confidence tiers"""
        if winner_lock and elite_defense:
            return {
                'tier': 1,
                'confidence': 1.0,
                'description': 'Elite Defense + Winner Lock (Theoretical maximum)',
                'recommendation': 'UNDER_3_5_STRONG',
                'stake_multiplier': 1.2
            }
        elif elite_defense and not winner_lock:
            return {
                'tier': 2,
                'confidence': 0.875,
                'description': 'Only Elite Defense (87.5% theoretical)',
                'recommendation': 'UNDER_3_5_MODERATE',
                'stake_multiplier': 1.0
            }
        elif winner_lock and not elite_defense:
            return {
                'tier': 3,
                'confidence': 0.833,
                'description': 'Only Winner Lock (83.3% theoretical)',
                'recommendation': 'UNDER_3_5_MODERATE',
                'stake_multiplier': 0.9
            }
        elif total_under:
            return {
                'tier': 4,
                'confidence': 0.7,
                'description': 'Total Under conditions only (70% reliability)',
                'recommendation': 'UNDER_3_5_CAUTION',
                'stake_multiplier': 0.7
            }
        else:
            return {
                'tier': 0,
                'confidence': 0.0,
                'description': 'No patterns detected',
                'recommendation': 'NO_UNDER_3_5',
                'stake_multiplier': 0.0
            }

# =================== LAYER 4: TIERED CONFIDENCE SYSTEM v8.0 ===================
class TieredConfidenceSystem:
    """TIERED CONFIDENCE SYSTEM v8.0"""
    
    @staticmethod
    def determine_tier(winner_lock: bool, elite_defense: bool, total_under: bool) -> Dict:
        """Determine confidence tier based on patterns"""
        # TIER 1: LOCK MODE (2.0x CAPITAL)
        if winner_lock and (elite_defense or total_under):
            return {
                'tier': 1,
                'name': 'LOCK_MODE',
                'capital_multiplier': CAPITAL_TIERS['TIER_1'],
                'reason': 'Winner Lock detected + (Elite Defense OR Total Under conditions)',
                'recommendations': [
                    'DOUBLE_CHANCE (Controller win or draw)',
                    'TOTAL_UNDER_3_5',
                    'TOTAL_UNDER_2_5 (if Total Under conditions present)',
                    'OPPONENT_UNDER_1_5 (if facing Elite Defense)'
                ],
                'stake_sizing': {
                    'primary': 'FULL',
                    'secondary': '50%',
                    'tertiary': '25%'
                }
            }
        
        # TIER 2: EDGE MODE (1.0x CAPITAL)
        elif winner_lock or elite_defense or total_under:
            return {
                'tier': 2,
                'name': 'EDGE_MODE',
                'capital_multiplier': CAPITAL_TIERS['TIER_2'],
                'reason': f'{"Winner Lock" if winner_lock else "Elite Defense" if elite_defense else "Total Under conditions"} alone',
                'recommendations': [
                    'Primary market only based on pattern',
                    'REDUCED stakes',
                    'Single bet approach'
                ],
                'stake_sizing': {
                    'primary': '70%',
                    'secondary': '30%',
                    'tertiary': '0%'
                }
            }
        
        # TIER 3: CAUTION MODE (0.5x CAPITAL)
        # Check for Under tendencies without patterns
        else:
            # This would require additional logic for Under tendencies
            # For now, default to STAY AWAY if no patterns
            return {
                'tier': 4,
                'name': 'STAY_AWAY',
                'capital_multiplier': CAPITAL_TIERS['TIER_4'],
                'reason': 'No proven patterns detected',
                'recommendations': ['PASS COMPLETELY'],
                'stake_sizing': {'primary': '0%'}
            }
    
    @staticmethod
    def calculate_pattern_multiplier(winner_lock: bool, elite_defense: bool, 
                                   total_under: bool) -> float:
        """Calculate pattern multiplier (base + 0.5x per additional pattern)"""
        base_multiplier = PATTERN_MULTIPLIERS['BASE']
        pattern_count = sum([winner_lock, elite_defense, total_under])
        
        if pattern_count == 0:
            return 0.5  # CAUTION MODE default
        
        multiplier = base_multiplier + ((pattern_count - 1) * PATTERN_MULTIPLIERS['ADDITIONAL_PATTERN'])
        
        return min(multiplier, PATTERN_MULTIPLIERS['MAX_MULTIPLIER'])

# =================== LAYER 5: DECISION FLOW ENGINE v8.0 ===================
class DecisionFlowEngineV80:
    """DECISION FLOW v8.0 - Complete logic execution"""
    
    @staticmethod
    def execute_decision_flow(home_data: Dict, away_data: Dict, 
                             home_name: str, away_name: str) -> Dict:
        """Execute complete v8.0 decision flow"""
        all_results = {}
        
        # ========== STEP 1: RUN AGENCY-STATE 4-GATE ANALYSIS ==========
        agency_state = AgencyState4GateSystem()
        all_results['agency_state'] = agency_state.run_complete_4gate_analysis(home_data, away_data)
        all_results['winner_lock'] = all_results['agency_state']['winner_lock']
        
        # ========== STEP 2: CHECK ELITE DEFENSE ==========
        elite_defense = EliteDefensePattern()
        all_results['elite_defense_home'] = elite_defense.detect_elite_defense(
            home_data, away_data
        )
        all_results['elite_defense_away'] = elite_defense.detect_elite_defense(
            away_data, home_data
        )
        all_results['has_elite_defense'] = (
            all_results['elite_defense_home']['elite_defense'] or 
            all_results['elite_defense_away']['elite_defense']
        )
        
        # ========== STEP 3: CHECK TOTAL UNDER CONDITIONS ==========
        total_under = TotalUnderConditions()
        all_results['total_under'] = total_under.check_total_under_conditions(
            home_data, away_data,
            all_results['elite_defense_home']['elite_defense'],
            all_results['elite_defense_away']['elite_defense']
        )
        all_results['has_total_under'] = all_results['total_under']['total_under_conditions']
        
        # ========== STEP 4: DETERMINE TIER ==========
        tier_system = TieredConfidenceSystem()
        all_results['tier_determination'] = tier_system.determine_tier(
            all_results['winner_lock'],
            all_results['has_elite_defense'],
            all_results['has_total_under']
        )
        
        # ========== STEP 5: UNDER 3.5 CONFIDENCE ==========
        all_results['under_35_confidence'] = total_under.evaluate_under_35_confidence(
            all_results['winner_lock'],
            all_results['has_elite_defense'],
            all_results['has_total_under']
        )
        
        # ========== STEP 6: CAPITAL ALLOCATION ==========
        pattern_multiplier = tier_system.calculate_pattern_multiplier(
            all_results['winner_lock'],
            all_results['has_elite_defense'],
            all_results['has_total_under']
        )
        
        final_capital = all_results['tier_determination']['capital_multiplier'] * pattern_multiplier
        
        all_results['capital_allocation'] = {
            'tier_multiplier': all_results['tier_determination']['capital_multiplier'],
            'pattern_multiplier': pattern_multiplier,
            'final_capital_multiplier': final_capital,
            'tier_name': all_results['tier_determination']['name'],
            'pattern_count': sum([
                all_results['winner_lock'],
                all_results['has_elite_defense'],
                all_results['has_total_under']
            ])
        }
        
        # ========== STEP 7: GENERATE RECOMMENDATIONS ==========
        all_results['recommendations'] = DecisionFlowEngineV80.generate_recommendations(all_results)
        
        # ========== STEP 8: DECISION FLOW SUMMARY ==========
        all_results['decision_flow'] = DecisionFlowEngineV80.create_decision_flow_summary(all_results)
        
        return all_results
    
    @staticmethod
    def generate_recommendations(results: Dict) -> List[Dict]:
        """Generate specific bet recommendations based on patterns"""
        recommendations = []
        
        # DOUBLE CHANCE from Winner Lock
        if results['winner_lock']:
            controller = results['agency_state'].get('controller_team', 'Controller')
            recommendations.append({
                'market': 'DOUBLE_CHANCE',
                'selection': f'{controller} win or draw',
                'confidence': 'HIGH',
                'reason': 'Winner Lock detected → Double Chance implied',
                'accuracy': '80% (4/5 backtest)',
                'stake_sizing': 'PRIMARY' if results['tier_determination']['tier'] == 1 else 'SECONDARY'
            })
        
        # OPPONENT UNDER 1.5 from Elite Defense
        if results['has_elite_defense']:
            if results['elite_defense_home']['elite_defense']:
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{results.get("away_name", "Away Team")} Under 1.5',
                    'confidence': 'MODERATE',
                    'reason': 'Facing Elite Defense (Home)',
                    'accuracy': '62.5% (5/8 backtest)',
                    'stake_sizing': 'SECONDARY'
                })
            
            if results['elite_defense_away']['elite_defense']:
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{results.get("home_name", "Home Team")} Under 1.5',
                    'confidence': 'MODERATE',
                    'reason': 'Facing Elite Defense (Away)',
                    'accuracy': '62.5% (5/8 backtest)',
                    'stake_sizing': 'SECONDARY'
                })
        
        # TOTAL UNDER 2.5 from Total Under conditions
        if results['has_total_under']:
            recommendations.append({
                'market': 'TOTAL_UNDER_2_5',
                'selection': 'Under 2.5 Goals',
                'confidence': 'HIGH',
                'reason': f'{results["total_under"]["path_count"]} path(s) to Under 2.5 confirmed',
                'accuracy': '70% (7/10 backtest)',
                'stake_sizing': 'PRIMARY' if not results['winner_lock'] else 'SECONDARY'
            })
        
        # TOTAL UNDER 3.5 from confidence tier
        if results['under_35_confidence']['tier'] > 0:
            recommendations.append({
                'market': 'TOTAL_UNDER_3_5',
                'selection': 'Under 3.5 Goals',
                'confidence': ['VERY HIGH', 'HIGH', 'MODERATE', 'LOW'][min(results['under_35_confidence']['tier'], 4)],
                'reason': results['under_35_confidence']['description'],
                'accuracy': f'{results["under_35_confidence"]["confidence"]*100:.1f}% theoretical',
                'stake_sizing': 'SECONDARY' if results['winner_lock'] else 'PRIMARY'
            })
        
        return recommendations
    
    @staticmethod
    def create_decision_flow_summary(results: Dict) -> List[Dict]:
        """Create decision flow summary for display"""
        flow = []
        
        flow.append({
            'step': 1,
            'action': 'RUN AGENCY-STATE 4-GATE ANALYSIS',
            'result': 'WINNER LOCK DETECTED' if results['winner_lock'] else 'NO WINNER LOCK',
            'details': results['agency_state'].get('reason', ''),
            'passed': results['winner_lock']
        })
        
        flow.append({
            'step': 2,
            'action': 'CHECK ELITE DEFENSE',
            'result': 'ELITE DEFENSE PRESENT' if results['has_elite_defense'] else 'NO ELITE DEFENSE',
            'details': f'Home: {results["elite_defense_home"]["elite_defense"]}, Away: {results["elite_defense_away"]["elite_defense"]}',
            'passed': results['has_elite_defense']
        })
        
        flow.append({
            'step': 3,
            'action': 'CHECK TOTAL UNDER CONDITIONS',
            'result': f'{results["total_under"]["path_count"]} PATH(S) CONFIRMED' if results['has_total_under'] else 'NO PATHS',
            'details': results['total_under']['reason'],
            'passed': results['has_total_under']
        })
        
        flow.append({
            'step': 4,
            'action': 'DETERMINE CONFIDENCE TIER',
            'result': results['tier_determination']['name'],
            'details': results['tier_determination']['reason'],
            'passed': results['tier_determination']['tier'] < 4
        })
        
        flow.append({
            'step': 5,
            'action': 'CAPITAL ALLOCATION',
            'result': f'{results["capital_allocation"]["final_capital_multiplier"]:.1f}x CAPITAL',
            'details': f'Tier: {results["capital_allocation"]["tier_multiplier"]:.1f}x × Patterns: {results["capital_allocation"]["pattern_multiplier"]:.1f}x',
            'passed': results['capital_allocation']['final_capital_multiplier'] > 0
        })
        
        return flow

# =================== STREAMLIT UI v8.0 ===================
def main():
    """Fused Logic Engine v8.0 Streamlit App"""
    
    st.set_page_config(
        page_title="Fused Logic Engine v8.0 - REAL Agency-State System",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS (keeping design you love)
    st.markdown("""
    <style>
    .pattern-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .tier-1 { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; }
    .tier-2 { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important; }
    .tier-3 { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; }
    .tier-4 { background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important; }
    .agency-gate { background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important; }
    .elite-defense { background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important; }
    .total-under { background: linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1E3A8A;">🎯 FUSED LOGIC ENGINE v8.0</h1>
        <div style="color: #4B5563; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
            <strong>REAL AGENCY-STATE SYSTEM:</strong> 4-Gate Winner Lock + Elite Defense + Total Under Conditions<br>
            Tiered Confidence System • REAL Data Analysis • Adjusted Accuracy Claims
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # League Configuration
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
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # Sidebar for league selection
    with st.sidebar:
        st.markdown("### 🌍 Select League")
        
        for league_name, filename in LEAGUES.items():
            if st.button(
                league_name,
                use_container_width=True,
                key=f"btn_{league_name}"
            ):
                with st.spinner(f"Loading {league_name}..."):
                    df = load_league_csv(league_name, filename)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.selected_league = league_name
                        st.session_state.analysis_result = None
                        st.success(f"✅ Loaded {len(df)} teams with Agency-State metrics")
                        st.rerun()
    
    # Main content
    if st.session_state.df is None:
        st.info("👆 Select a league from the sidebar to begin")
        
        # Show empirical accuracy claims
        st.markdown("### 📊 Empirical Accuracy (v8.0 Adjusted)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Winner Lock", "80%", "4/5 backtest")
        with col2:
            st.metric("Elite Defense", "62.5%", "5/8 backtest")
        with col3:
            st.metric("Total Under 2.5", "70%", "7/10 backtest")
        
        return
    
    df = st.session_state.df
    
    # Match selection
    st.markdown("### 📥 Match Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        teams = sorted(df['team'].unique())
        home_team = st.selectbox("Home Team", teams, key="home_team")
        
        # Get home team data
        home_row = df[df['team'] == home_team]
        if not home_row.empty:
            home_data = home_row.iloc[0].to_dict()
            st.info(f"**Agency-State Metrics:** {home_data.get('xg_per_match', 1.2):.2f} xG/match, {home_data.get('efficiency', 0.8)*100:.0f}% efficiency")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team")
        
        # Get away team data
        away_row = df[df['team'] == away_team]
        if not away_row.empty:
            away_data = away_row.iloc[0].to_dict()
            st.info(f"**Agency-State Metrics:** {away_data.get('xg_per_match', 1.2):.2f} xG/match, {away_data.get('efficiency', 0.8)*100:.0f}% efficiency")
    
    # Run analysis button
    if st.button("🚀 RUN AGENCY-STATE ANALYSIS v8.0", type="primary", use_container_width=True):
        with st.spinner("Executing 4-Gate Agency-State analysis..."):
            try:
                engine = DecisionFlowEngineV80()
                result = engine.execute_decision_flow(
                    home_data, away_data, home_team, away_team
                )
                st.session_state.analysis_result = result
                st.success("✅ Agency-State analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Tier Banner
        tier = result['tier_determination']
        tier_class = f"tier-{tier['tier']}"
        
        st.markdown(f"""
        <div class="pattern-card {tier_class}" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                {'🎯' if tier['tier'] == 1 else '📊' if tier['tier'] == 2 else '⚠️' if tier['tier'] == 3 else '🚫'}
            </div>
            <h2 style="margin: 0;">{tier['name']}</h2>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                {result['capital_allocation']['final_capital_multiplier']:.1f}x CAPITAL
            </div>
            <div style="color: rgba(255,255,255,0.9);">
                {tier['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Decision Flow
        st.markdown("### 📋 Decision Flow v8.0")
        for step in result['decision_flow']:
            with st.container():
                cols = st.columns([0.1, 0.2, 0.4, 0.3])
                with cols[0]:
                    st.write(f"**{step['step']}**")
                with cols[1]:
                    st.write(f"{'✅' if step['passed'] else '❌'} {step['action']}")
                with cols[2]:
                    st.write(f"**{step['result']}**")
                    st.caption(step['details'])
                with cols[3]:
                    if step['step'] == 5:
                        st.metric("Multiplier", f"{result['capital_allocation']['final_capital_multiplier']:.1f}x")
        
        # Pattern Detections
        st.markdown("### 🔍 Pattern Detections")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if result['winner_lock']:
                st.markdown(f"""
                <div class="pattern-card agency-gate">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">🎯</div>
                        <h3 style="margin: 0.5rem 0;">WINNER LOCK</h3>
                        <div style="font-size: 0.9rem;">4-Gate Agency-State Analysis</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            📈 80% accuracy (4/5)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if result['has_elite_defense']:
                st.markdown(f"""
                <div class="pattern-card elite-defense">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">🛡️</div>
                        <h3 style="margin: 0.5rem 0;">ELITE DEFENSE</h3>
                        <div style="font-size: 0.9rem;">≤4 conceded last 5 matches</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            📈 62.5% accuracy (5/8)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if result['has_total_under']:
                st.markdown(f"""
                <div class="pattern-card total-under">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">📉</div>
                        <h3 style="margin: 0.5rem 0;">TOTAL UNDER</h3>
                        <div style="font-size: 0.9rem;">{result['total_under']['path_count']} path(s) confirmed</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            📈 70% accuracy (7/10)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💰 Bet Recommendations")
        if result['recommendations']:
            for i, rec in enumerate(result['recommendations']):
                with st.container():
                    cols = st.columns([0.3, 0.4, 0.2, 0.1])
                    with cols[0]:
                        st.markdown(f"**{rec['market']}**")
                    with cols[1]:
                        st.write(rec['selection'])
                        st.caption(rec['reason'])
                    with cols[2]:
                        st.metric("Confidence", rec['confidence'], rec['accuracy'])
                    with cols[3]:
                        st.caption(f"**{rec['stake_sizing']}**")
        
        # Agency-State Gate Details
        if result['winner_lock']:
            st.markdown("### ⚙️ Agency-State 4-Gate Analysis")
            gates = result['agency_state']['gates']
            
            gate_cols = st.columns(4)
            gate_data = [
                ("GATE 1", "Quiet Control", gates['gate1']['result'], gates['gate1']['reason']),
                ("GATE 2", "Directional Dominance", gates['gate2']['result'], gates['gate2']['reason']),
                ("GATE 3", "State-Flip Capacity", gates['gate3']['result'], gates['gate3'].get('reason', '')),
                ("GATE 4", "Enforcement", gates['gate4']['result'], gates['gate4'].get('reason', ''))
            ]
            
            for idx, (title, subtitle, result_text, reason) in enumerate(gate_data):
                with gate_cols[idx]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{title}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;">{subtitle}</div>
                        <div style="font-weight: bold; margin-bottom: 0.5rem;">{result_text}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{reason[:50]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Empirical Evidence
        st.markdown("### 📈 Empirical Evidence (v8.0 Adjusted)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Winner Lock", "80%", "4/5 backtest (NOT 100%)")
        with col2:
            st.metric("Elite Defense", "62.5%", "5/8 backtest (NOT 100%)")
        with col3:
            st.metric("Total Under 2.5", "70%", "7/10 (MOST RELIABLE)")
        
        # Capital Allocation Details
        st.markdown("### 💸 Capital Allocation Details")
        alloc = result['capital_allocation']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tier Multiplier", f"{alloc['tier_multiplier']:.1f}x")
        with col2:
            st.metric("Pattern Multiplier", f"{alloc['pattern_multiplier']:.1f}x")
        with col3:
            st.metric("Pattern Count", alloc['pattern_count'])
        with col4:
            st.metric("Final Multiplier", f"{alloc['final_capital_multiplier']:.1f}x")

if __name__ == "__main__":
    main()
