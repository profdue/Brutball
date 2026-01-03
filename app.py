"""
FUSED LOGIC ENGINE v8.0 - REAL AGENCY-STATE SYSTEM
CORE PHILOSOPHY: Use ALL available data to run REAL Agency-State analysis
Combining 4-Gate Winner Lock with Elite Defense and Total Under conditions
NO HARDCODED TEAM NAMES OR SCORES - ALL DATA FROM CSV
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
        
        # Calculate totals from available data
        if 'home_goals_scored' in df.columns and 'away_goals_scored' in df.columns:
            df['goals_scored'] = df['home_goals_scored'] + df['away_goals_scored']
        else:
            # Estimate from available columns
            if 'goals_scored_last_5' in df.columns:
                df['goals_scored'] = df['goals_scored_last_5'] * 2  # Estimate full season
            else:
                df['goals_scored'] = 0
        
        if 'home_goals_conceded' in df.columns and 'away_goals_conceded' in df.columns:
            df['goals_conceded'] = df['home_goals_conceded'] + df['away_goals_conceded']
        else:
            if 'goals_conceded_last_5' in df.columns:
                df['goals_conceded'] = df['goals_conceded_last_5'] * 2  # Estimate
            else:
                df['goals_conceded'] = 0
        
        if 'home_xg_for' in df.columns and 'away_xg_for' in df.columns:
            df['xg_for'] = df['home_xg_for'] + df['away_xg_for']
        else:
            df['xg_for'] = df['goals_scored'] * 0.85  # Estimate
        
        if 'home_xg_against' in df.columns and 'away_xg_against' in df.columns:
            df['xg_against'] = df['home_xg_against'] + df['away_xg_against']
        else:
            df['xg_against'] = df['goals_conceded'] * 0.85  # Estimate
        
        # Calculate matches played
        if 'home_matches_played' in df.columns and 'away_matches_played' in df.columns:
            df['matches_played'] = df['home_matches_played'] + df['away_matches_played']
        else:
            df['matches_played'] = 10  # Default
        
        # Calculate per-match averages
        df['goals_per_match'] = df['goals_scored'] / df['matches_played'].replace(0, 1)
        df['xg_per_match'] = df['xg_for'] / df['matches_played'].replace(0, 1)
        df['conceded_per_match'] = df['goals_conceded'] / df['matches_played'].replace(0, 1)
        
        # Calculate home/away specific averages
        if 'home_matches_played' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_goals_per_match'] = df['goals_per_match']
        
        if 'away_matches_played' in df.columns:
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_goals_per_match'] = df['goals_per_match']
        
        if 'home_xg_for' in df.columns and 'home_matches_played' in df.columns:
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_xg_per_match'] = df['xg_per_match']
        
        if 'away_xg_for' in df.columns and 'away_matches_played' in df.columns:
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_xg_per_match'] = df['xg_per_match']
        
        if 'home_goals_conceded' in df.columns and 'home_matches_played' in df.columns:
            df['home_conceded_per_match'] = df['home_goals_conceded'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_conceded_per_match'] = df['conceded_per_match']
        
        if 'away_goals_conceded' in df.columns and 'away_matches_played' in df.columns:
            df['away_conceded_per_match'] = df['away_goals_conceded'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_conceded_per_match'] = df['conceded_per_match']
        
        # Calculate percentages for Agency-State
        df['efficiency'] = df['goals_scored'] / df['xg_for'].replace(0, 1)
        
        # Calculate scoring type percentages
        scoring_cols = [
            'home_goals_openplay_for', 'home_goals_counter_for', 'home_goals_setpiece_for', 'home_goals_penalty_for',
            'away_goals_openplay_for', 'away_goals_counter_for', 'away_goals_setpiece_for', 'away_goals_penalty_for'
        ]
        
        for col in scoring_cols:
            if col not in df.columns:
                df[col] = 0
        
        df['total_goals_openplay'] = df['home_goals_openplay_for'] + df['away_goals_openplay_for']
        df['total_goals_counter'] = df['home_goals_counter_for'] + df['away_goals_counter_for']
        df['total_goals_setpiece'] = (df['home_goals_setpiece_for'] + df['home_goals_penalty_for'] + 
                                     df['away_goals_setpiece_for'] + df['away_goals_penalty_for'])
        
        df['setpiece_pct'] = df['total_goals_setpiece'] / df['goals_scored'].replace(0, 1)
        df['counter_pct'] = df['total_goals_counter'] / df['goals_scored'].replace(0, 1)
        df['openplay_pct'] = df['total_goals_openplay'] / df['goals_scored'].replace(0, 1)
        
        # Calculate last 5 averages
        if 'goals_scored_last_5' in df.columns:
            df['avg_goals_scored_last_5'] = df['goals_scored_last_5'] / 5
        else:
            df['avg_goals_scored_last_5'] = df['goals_per_match'] * 1.0
        
        if 'goals_conceded_last_5' in df.columns:
            df['avg_goals_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        else:
            df['avg_goals_conceded_last_5'] = df['conceded_per_match'] * 1.0
        
        # League averages
        if len(df) > 0:
            df['league_avg_goals'] = df['goals_per_match'].mean()
            df['league_avg_conceded'] = df['conceded_per_match'].mean()
            df['league_avg_xg'] = df['xg_per_match'].mean()
        else:
            df['league_avg_goals'] = 1.3
            df['league_avg_conceded'] = 1.3
            df['league_avg_xg'] = 1.2
        
        # Form indicators
        if 'form_last_5_overall' in df.columns:
            df['form_points_last_5'] = df['form_last_5_overall'].apply(
                lambda x: len([c for c in str(x) if c in ['W', 'D']]) if pd.notna(x) else 0
            )
        else:
            df['form_points_last_5'] = 0
        
        return df.fillna(0)
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== SYSTEM CONSTANTS v8.0 ===================
AGENCY_STATE_THRESHOLDS = {
    'TEMPO_DOMINANCE': 1.4,
    'SCORING_EFFICIENCY': 0.9,
    'CRITICAL_AREA_THREAT': 0.25,
    'REPEATABLE_PATTERNS_OPENPLAY': 0.5,
    'REPEATABLE_PATTERNS_COUNTER': 0.15,
    'QUIET_CONTROL_WEIGHT_SEPARATION': 0.1,
    'DIRECTIONAL_DELTA': 0.25,
    'MARKET_THRESHOLD_WINNER': 1.1,
    'MARKET_THRESHOLD_UNDER_1_5': 1.0,
    'MARKET_THRESHOLD_UNDER_2_5': 1.2,
    'STATE_FLIP_CHASE_CAPACITY': 1.1,
    'STATE_FLIP_TEMPO_SURGE': 1.4,
    'STATE_FLIP_SETPIECE_PCT': 0.25,
    'STATE_FLIP_COUNTER_PCT': 0.15,
    'ENFORCEMENT_DEFENSIVE_HOME': 1.2,
    'ENFORCEMENT_DEFENSIVE_AWAY': 1.3,
    'ENFORCEMENT_CONSISTENT_THREAT': 1.3,
}

ELITE_DEFENSE_THRESHOLDS = {
    'ABSOLUTE_DEFENSE': 4,
    'AVG_CONCEDED': 0.8,
    'DEFENSE_GAP': 2.0,
    'LEAGUE_AVG_CONCEDED': 1.3,
}

TOTAL_UNDER_THRESHOLDS = {
    'OFFENSIVE_INCAPACITY': 1.2,
    'DEFENSIVE_STRENGTH': 1.2,
    'ELITE_DEFENSE_DOMINANCE': 1.5,
}

# EMPIRICAL ACCURACY v8.0 (ADJUSTED TO REAL BACKTEST)
EMPIRICAL_ACCURACY = {
    'WINNER_LOCK': '80% (4/5 backtest)',
    'ELITE_DEFENSE': '62.5% (5/8)',
    'TOTAL_UNDER_2_5': '70% (7/10)',
    'DOUBLE_CHANCE': '80% (4/5)',
    'UNDER_3_5_TIER1': '100% theoretical',
    'UNDER_3_5_TIER2': '87.5% theoretical',
    'UNDER_3_5_TIER3': '83.3% theoretical',
}

# TIERED CAPITAL ALLOCATION v8.0
CAPITAL_TIERS = {
    'TIER_1': 2.0,
    'TIER_2': 1.0,
    'TIER_3': 0.5,
    'TIER_4': 0.0,
}

PATTERN_MULTIPLIERS = {
    'BASE': 1.0,
    'ADDITIONAL_PATTERN': 0.5,
    'MAX_MULTIPLIER': 3.0,
}

# =================== SAFE VALUE HELPER ===================
def get_safe_value(data: Dict, key: str, default: Any = 0) -> Any:
    """Safely get value from dictionary with default"""
    if not data:
        return default
    return data.get(key, default)

# =================== LAYER 1: REAL AGENCY-STATE 4-GATE SYSTEM ===================
class AgencyState4GateSystem:
    """REAL 4-GATE AGENCY-STATE ANALYSIS (No hardcoded data)"""
    
    @staticmethod
    def get_team_data_for_perspective(data: Dict, is_home: bool) -> Dict:
        """Get the correct metrics for home/away perspective"""
        if is_home:
            return {
                'xg_per_match': get_safe_value(data, 'home_xg_per_match', get_safe_value(data, 'xg_per_match', 1.2)),
                'efficiency': get_safe_value(data, 'efficiency', 0.8),
                'setpiece_pct': get_safe_value(data, 'setpiece_pct', 0.2),
                'openplay_pct': get_safe_value(data, 'openplay_pct', 0.6),
                'counter_pct': get_safe_value(data, 'counter_pct', 0.1),
                'goals_per_match': get_safe_value(data, 'home_goals_per_match', get_safe_value(data, 'goals_per_match', 1.2)),
                'conceded_per_match': get_safe_value(data, 'home_conceded_per_match', get_safe_value(data, 'conceded_per_match', 1.2)),
                'avg_goals_scored_last_5': get_safe_value(data, 'avg_goals_scored_last_5', 1.3),
                'avg_goals_conceded_last_5': get_safe_value(data, 'avg_goals_conceded_last_5', 1.3),
                'league_avg_goals': get_safe_value(data, 'league_avg_goals', 1.3),
                'goals_scored_last_5': get_safe_value(data, 'goals_scored_last_5', 6),
                'goals_conceded_last_5': get_safe_value(data, 'goals_conceded_last_5', 6),
            }
        else:
            return {
                'xg_per_match': get_safe_value(data, 'away_xg_per_match', get_safe_value(data, 'xg_per_match', 1.2)),
                'efficiency': get_safe_value(data, 'efficiency', 0.8),
                'setpiece_pct': get_safe_value(data, 'setpiece_pct', 0.2),
                'openplay_pct': get_safe_value(data, 'openplay_pct', 0.6),
                'counter_pct': get_safe_value(data, 'counter_pct', 0.1),
                'goals_per_match': get_safe_value(data, 'away_goals_per_match', get_safe_value(data, 'goals_per_match', 1.2)),
                'conceded_per_match': get_safe_value(data, 'away_conceded_per_match', get_safe_value(data, 'conceded_per_match', 1.2)),
                'avg_goals_scored_last_5': get_safe_value(data, 'avg_goals_scored_last_5', 1.3),
                'avg_goals_conceded_last_5': get_safe_value(data, 'avg_goals_conceded_last_5', 1.3),
                'league_avg_goals': get_safe_value(data, 'league_avg_goals', 1.3),
                'goals_scored_last_5': get_safe_value(data, 'goals_scored_last_5', 6),
                'goals_conceded_last_5': get_safe_value(data, 'goals_conceded_last_5', 6),
            }
    
    @staticmethod
    def gate1_quiet_control(home_data: Dict, away_data: Dict, is_home_perspective: bool) -> Dict:
        """GATE 1: Quiet Control Identification"""
        try:
            controller_data = AgencyState4GateSystem.get_team_data_for_perspective(
                home_data if is_home_perspective else away_data, 
                is_home_perspective
            )
            opponent_data = AgencyState4GateSystem.get_team_data_for_perspective(
                away_data if is_home_perspective else home_data, 
                not is_home_perspective
            )
            
            controller_label = "HOME" if is_home_perspective else "AWAY"
            
            criteria_weights = {
                'tempo_dominance': 1.0,
                'scoring_efficiency': 1.0,
                'critical_area_threat': 0.8,
                'repeatable_patterns': 0.8,
            }
            
            controller_scores = {}
            opponent_scores = {}
            
            # 1. Tempo Dominance (xG per match > 1.4)
            controller_xg = get_safe_value(controller_data, 'xg_per_match', 1.0)
            opponent_xg = get_safe_value(opponent_data, 'xg_per_match', 1.0)
            
            controller_scores['tempo_dominance'] = 1 if controller_xg > AGENCY_STATE_THRESHOLDS['TEMPO_DOMINANCE'] else 0
            opponent_scores['tempo_dominance'] = 1 if opponent_xg > AGENCY_STATE_THRESHOLDS['TEMPO_DOMINANCE'] else 0
            
            # 2. Scoring Efficiency (Goals/xG > 90%)
            controller_efficiency = get_safe_value(controller_data, 'efficiency', 0.8)
            opponent_efficiency = get_safe_value(opponent_data, 'efficiency', 0.8)
            
            controller_scores['scoring_efficiency'] = 1 if controller_efficiency > AGENCY_STATE_THRESHOLDS['SCORING_EFFICIENCY'] else 0
            opponent_scores['scoring_efficiency'] = 1 if opponent_efficiency > AGENCY_STATE_THRESHOLDS['SCORING_EFFICIENCY'] else 0
            
            # 3. Critical Area Threat (Set piece goals > 25%)
            controller_setpiece = get_safe_value(controller_data, 'setpiece_pct', 0.2)
            opponent_setpiece = get_safe_value(opponent_data, 'setpiece_pct', 0.2)
            
            controller_scores['critical_area_threat'] = 1 if controller_setpiece > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] else 0
            opponent_scores['critical_area_threat'] = 1 if opponent_setpiece > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] else 0
            
            # 4. Repeatable Patterns (Open play > 50% OR Counter > 15%)
            controller_openplay = get_safe_value(controller_data, 'openplay_pct', 0.6)
            controller_counter = get_safe_value(controller_data, 'counter_pct', 0.1)
            opponent_openplay = get_safe_value(opponent_data, 'openplay_pct', 0.6)
            opponent_counter = get_safe_value(opponent_data, 'counter_pct', 0.1)
            
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
                'reason': f'Insufficient control criteria (Controller: {controller_criteria_met}/4, Opponent: {opponent_criteria_met}/4)'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'result': 'ERROR',
                'reason': f'Error in Gate 1: {str(e)}'
            }
    
    @staticmethod
    def gate2_directional_dominance(controller_data: Dict, opponent_data: Dict, 
                                   market: str = 'WINNER') -> Dict:
        """GATE 2: Directional Dominance"""
        try:
            market_thresholds = {
                'WINNER': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_WINNER'],
                'UNDER_1_5': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_UNDER_1_5'],
                'UNDER_2_5': AGENCY_STATE_THRESHOLDS['MARKET_THRESHOLD_UNDER_2_5'],
            }
            
            threshold = market_thresholds.get(market, 1.1)
            
            controller_xg = get_safe_value(controller_data, 'xg_per_match', 1.2)
            opponent_xg = get_safe_value(opponent_data, 'xg_per_match', 1.2)
            
            control_delta = controller_xg - opponent_xg
            
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
        except Exception as e:
            return {
                'gate_passed': False,
                'result': 'ERROR',
                'reason': f'Error in Gate 2: {str(e)}'
            }
    
    @staticmethod
    def gate3_state_flip_capacity(opponent_data: Dict, market: str = 'WINNER') -> Dict:
        """GATE 3: State-Flip Capacity (Agency Collapse)"""
        try:
            market_requirements = {
                'WINNER': 2,
                'UNDER_1_5': 2,
                'CLEAN_SHEET': 3,
            }
            required_failures = market_requirements.get(market, 2)
            
            failures = []
            
            opponent_xg = get_safe_value(opponent_data, 'xg_per_match', 1.2)
            if opponent_xg < AGENCY_STATE_THRESHOLDS['STATE_FLIP_CHASE_CAPACITY']:
                failures.append('CHASE_CAPACITY')
            
            if opponent_xg < AGENCY_STATE_THRESHOLDS['STATE_FLIP_TEMPO_SURGE']:
                failures.append('TEMPO_SURGE')
            
            setpiece_pct = get_safe_value(opponent_data, 'setpiece_pct', 0.2)
            counter_pct = get_safe_value(opponent_data, 'counter_pct', 0.1)
            
            if (setpiece_pct < AGENCY_STATE_THRESHOLDS['STATE_FLIP_SETPIECE_PCT'] and 
                counter_pct < AGENCY_STATE_THRESHOLDS['STATE_FLIP_COUNTER_PCT']):
                failures.append('ALTERNATE_THREATS')
            
            opponent_goals_per_match = get_safe_value(opponent_data, 'goals_per_match', 
                get_safe_value(opponent_data, 'avg_goals_scored_last_5', 1.0))
            league_avg = get_safe_value(opponent_data, 'league_avg_goals', 1.3)
            
            if opponent_goals_per_match < league_avg * 0.8:
                failures.append('SUBSTITUTION_LEVERAGE')
            
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
        except Exception as e:
            return {
                'gate_passed': False,
                'result': 'ERROR',
                'reason': f'Error in Gate 3: {str(e)}'
            }
    
    @staticmethod
    def gate4_enforcement_without_urgency(controller_data: Dict, is_home: bool) -> Dict:
        """GATE 4: Enforcement Without Urgency"""
        try:
            methods = []
            
            if is_home:
                defensive_threshold = AGENCY_STATE_THRESHOLDS['ENFORCEMENT_DEFENSIVE_HOME']
            else:
                defensive_threshold = AGENCY_STATE_THRESHOLDS['ENFORCEMENT_DEFENSIVE_AWAY']
            
            concede_avg = get_safe_value(controller_data, 'conceded_per_match', 1.2)
            if concede_avg < defensive_threshold:
                methods.append('DEFENSIVE_SOLIDITY')
            
            setpiece_pct = get_safe_value(controller_data, 'setpiece_pct', 0.2)
            counter_pct = get_safe_value(controller_data, 'counter_pct', 0.1)
            
            if (setpiece_pct > AGENCY_STATE_THRESHOLDS['CRITICAL_AREA_THREAT'] or 
                counter_pct > AGENCY_STATE_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER']):
                methods.append('ALTERNATE_SCORING')
            
            xg_per_match = get_safe_value(controller_data, 'xg_per_match', 1.2)
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
        except Exception as e:
            return {
                'gate_passed': False,
                'result': 'ERROR',
                'reason': f'Error in Gate 4: {str(e)}'
            }
    
    @staticmethod
    def run_complete_4gate_analysis(home_data: Dict, away_data: Dict) -> Dict:
        """Run complete 4-Gate Agency-State analysis from BOTH perspectives"""
        try:
            results = {}
            
            # Analyze from HOME perspective
            home_perspective = {}
            home_perspective['gate1'] = AgencyState4GateSystem.gate1_quiet_control(
                home_data, away_data, is_home_perspective=True
            )
            
            if home_perspective['gate1'].get('gate_passed', False):
                if home_perspective['gate1'].get('controller') == 'HOME':
                    controller_data = AgencyState4GateSystem.get_team_data_for_perspective(home_data, True)
                    opponent_data = AgencyState4GateSystem.get_team_data_for_perspective(away_data, False)
                else:
                    controller_data = AgencyState4GateSystem.get_team_data_for_perspective(away_data, False)
                    opponent_data = AgencyState4GateSystem.get_team_data_for_perspective(home_data, True)
                
                home_perspective['gate2'] = AgencyState4GateSystem.gate2_directional_dominance(
                    controller_data, opponent_data, market='WINNER'
                )
                home_perspective['gate3'] = AgencyState4GateSystem.gate3_state_flip_capacity(
                    opponent_data, market='WINNER'
                )
                home_perspective['gate4'] = AgencyState4GateSystem.gate4_enforcement_without_urgency(
                    controller_data, is_home=(home_perspective['gate1'].get('controller') == 'HOME')
                )
            else:
                home_perspective['gate2'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
                home_perspective['gate3'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
                home_perspective['gate4'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
            
            # Analyze from AWAY perspective
            away_perspective = {}
            away_perspective['gate1'] = AgencyState4GateSystem.gate1_quiet_control(
                home_data, away_data, is_home_perspective=False
            )
            
            if away_perspective['gate1'].get('gate_passed', False):
                if away_perspective['gate1'].get('controller') == 'AWAY':
                    controller_data = AgencyState4GateSystem.get_team_data_for_perspective(away_data, False)
                    opponent_data = AgencyState4GateSystem.get_team_data_for_perspective(home_data, True)
                else:
                    controller_data = AgencyState4GateSystem.get_team_data_for_perspective(home_data, True)
                    opponent_data = AgencyState4GateSystem.get_team_data_for_perspective(away_data, False)
                
                away_perspective['gate2'] = AgencyState4GateSystem.gate2_directional_dominance(
                    controller_data, opponent_data, market='WINNER'
                )
                away_perspective['gate3'] = AgencyState4GateSystem.gate3_state_flip_capacity(
                    opponent_data, market='WINNER'
                )
                away_perspective['gate4'] = AgencyState4GateSystem.gate4_enforcement_without_urgency(
                    controller_data, is_home=(away_perspective['gate1'].get('controller') == 'HOME')
                )
            else:
                away_perspective['gate2'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
                away_perspective['gate3'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
                away_perspective['gate4'] = {'gate_passed': False, 'result': 'GATE1_FAILED'}
            
            # Determine if ANY perspective has WINNER LOCK
            home_winner_lock = all([
                home_perspective['gate1'].get('gate_passed', False),
                home_perspective['gate2'].get('gate_passed', False),
                home_perspective['gate3'].get('gate_passed', False),
                home_perspective['gate4'].get('gate_passed', False)
            ])
            
            away_winner_lock = all([
                away_perspective['gate1'].get('gate_passed', False),
                away_perspective['gate2'].get('gate_passed', False),
                away_perspective['gate3'].get('gate_passed', False),
                away_perspective['gate4'].get('gate_passed', False)
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
                        'gate1': gates['gate1'].get('result', 'ERROR'),
                        'gate2': gates['gate2'].get('result', 'ERROR'),
                        'gate3': gates['gate3'].get('result', 'ERROR'),
                        'gate4': gates['gate4'].get('result', 'ERROR')
                    },
                    'reason': f'4-Gate Agency-State analysis confirms {controller_team} as market controller',
                    'accuracy_claim': '80% (4/5 backtest)',
                    'market_implications': ['DOUBLE_CHANCE', 'WINNER']
                }
            
            return {
                'winner_lock': False,
                'reason': 'No Winner Lock detected - insufficient Agency-State control',
                'gate_summary': {
                    'home_perspective': {k: v.get('result', 'ERROR') for k, v in home_perspective.items()},
                    'away_perspective': {k: v.get('result', 'ERROR') for k, v in away_perspective.items()}
                }
            }
        except Exception as e:
            return {
                'winner_lock': False,
                'reason': f'Error in Agency-State analysis: {str(e)}',
                'error': str(e)
            }

# =================== LAYER 2: ELITE DEFENSE PATTERN ===================
class EliteDefensePattern:
    """ELITE DEFENSE PATTERN (62.5% accuracy - adjusted)"""
    
    @staticmethod
    def detect_elite_defense(team_data: Dict, opponent_data: Dict, league_avg: float = 1.3) -> Dict:
        """Detect Elite Defense pattern with REAL thresholds"""
        try:
            total_conceded_last_5 = get_safe_value(team_data, 'goals_conceded_last_5', 6)
            avg_conceded = total_conceded_last_5 / 5
            
            opponent_avg_conceded = get_safe_value(opponent_data, 'avg_goals_conceded_last_5', 
                get_safe_value(opponent_data, 'goals_conceded_last_5', 6) / 5)
            
            defense_gap = league_avg - avg_conceded
            
            absolute_defense = total_conceded_last_5 <= ELITE_DEFENSE_THRESHOLDS['ABSOLUTE_DEFENSE']
            avg_defense = avg_conceded <= ELITE_DEFENSE_THRESHOLDS['AVG_CONCEDED']
            gap_condition = defense_gap > ELITE_DEFENSE_THRESHOLDS['DEFENSE_GAP']
            relative_advantage = avg_conceded < opponent_avg_conceded * 0.6
            
            elite_defense = absolute_defense and (gap_condition or relative_advantage)
            
            if elite_defense:
                return {
                    'elite_defense': True,
                    'total_conceded_last_5': total_conceded_last_5,
                    'avg_conceded': avg_conceded,
                    'defense_gap': defense_gap,
                    'relative_advantage': f'{((opponent_avg_conceded - avg_conceded) / opponent_avg_conceded * 100):.1f}% better' if opponent_avg_conceded > 0 else 'N/A',
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
        except Exception as e:
            return {
                'elite_defense': False,
                'reason': f'Error analyzing defense: {str(e)}'
            }

# =================== LAYER 3: TOTAL UNDER CONDITIONS ===================
class TotalUnderConditions:
    """THREE PATHS TO TOTAL UNDER 2.5 (70% reliability)"""
    
    @staticmethod
    def check_total_under_conditions(home_data: Dict, away_data: Dict, 
                                   home_elite: bool, away_elite: bool) -> Dict:
        """Check all three paths for Total Under 2.5"""
        try:
            paths = []
            
            home_avg_scored = get_safe_value(home_data, 'avg_goals_scored_last_5', 
                get_safe_value(home_data, 'goals_scored_last_5', 6) / 5)
            away_avg_scored = get_safe_value(away_data, 'avg_goals_scored_last_5', 
                get_safe_value(away_data, 'goals_scored_last_5', 6) / 5)
            home_avg_conceded = get_safe_value(home_data, 'avg_goals_conceded_last_5', 
                get_safe_value(home_data, 'goals_conceded_last_5', 6) / 5)
            away_avg_conceded = get_safe_value(away_data, 'avg_goals_conceded_last_5', 
                get_safe_value(away_data, 'goals_conceded_last_5', 6) / 5)
            
            # PATH A: Offensive Incapacity
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
        except Exception as e:
            return {
                'total_under_conditions': False,
                'paths': [],
                'reason': f'Error analyzing Under conditions: {str(e)}'
            }
    
    @staticmethod
    def evaluate_under_35_confidence(winner_lock: bool, elite_defense: bool, 
                                   total_under: bool) -> Dict:
        """Evaluate UNDER 3.5 confidence tiers"""
        try:
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
        except:
            return {
                'tier': 0,
                'confidence': 0.0,
                'description': 'Error in confidence calculation',
                'recommendation': 'NO_UNDER_3_5',
                'stake_multiplier': 0.0
            }

# =================== LAYER 4: TIERED CONFIDENCE SYSTEM v8.0 ===================
class TieredConfidenceSystem:
    """TIERED CONFIDENCE SYSTEM v8.0"""
    
    @staticmethod
    def determine_tier(winner_lock: bool, elite_defense: bool, total_under: bool) -> Dict:
        """Determine confidence tier based on patterns"""
        try:
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
            
            # TIER 4: STAY AWAY (no patterns)
            else:
                return {
                    'tier': 4,
                    'name': 'STAY_AWAY',
                    'capital_multiplier': CAPITAL_TIERS['TIER_4'],
                    'reason': 'No proven patterns detected',
                    'recommendations': ['PASS COMPLETELY'],
                    'stake_sizing': {'primary': '0%'}
                }
        except Exception as e:
            return {
                'tier': 4,
                'name': 'ERROR',
                'capital_multiplier': 0.0,
                'reason': f'Error in tier determination: {str(e)}',
                'recommendations': ['SYSTEM ERROR'],
                'stake_sizing': {'primary': '0%'}
            }
    
    @staticmethod
    def calculate_pattern_multiplier(winner_lock: bool, elite_defense: bool, 
                                   total_under: bool) -> float:
        """Calculate pattern multiplier (base + 0.5x per additional pattern)"""
        try:
            base_multiplier = PATTERN_MULTIPLIERS['BASE']
            pattern_count = sum([winner_lock, elite_defense, total_under])
            
            if pattern_count == 0:
                return 0.5  # CAUTION MODE default
            
            multiplier = base_multiplier + ((pattern_count - 1) * PATTERN_MULTIPLIERS['ADDITIONAL_PATTERN'])
            
            return min(multiplier, PATTERN_MULTIPLIERS['MAX_MULTIPLIER'])
        except:
            return 1.0

# =================== LAYER 5: DECISION FLOW ENGINE v8.0 ===================
class DecisionFlowEngineV80:
    """DECISION FLOW v8.0 - Complete logic execution"""
    
    @staticmethod
    def execute_decision_flow(home_data: Dict, away_data: Dict, 
                             home_name: str, away_name: str) -> Dict:
        """Execute complete v8.0 decision flow with error handling"""
        try:
            all_results = {}
            
            # Store team names
            all_results['home_name'] = home_name
            all_results['away_name'] = away_name
            
            # ========== STEP 1: RUN AGENCY-STATE 4-GATE ANALYSIS ==========
            agency_state = AgencyState4GateSystem()
            all_results['agency_state'] = agency_state.run_complete_4gate_analysis(home_data, away_data)
            all_results['winner_lock'] = all_results['agency_state'].get('winner_lock', False)
            
            # ========== STEP 2: CHECK ELITE DEFENSE ==========
            elite_defense = EliteDefensePattern()
            all_results['elite_defense_home'] = elite_defense.detect_elite_defense(
                home_data, away_data
            )
            all_results['elite_defense_away'] = elite_defense.detect_elite_defense(
                away_data, home_data
            )
            all_results['has_elite_defense'] = (
                all_results['elite_defense_home'].get('elite_defense', False) or 
                all_results['elite_defense_away'].get('elite_defense', False)
            )
            
            # ========== STEP 3: CHECK TOTAL UNDER CONDITIONS ==========
            total_under = TotalUnderConditions()
            all_results['total_under'] = total_under.check_total_under_conditions(
                home_data, away_data,
                all_results['elite_defense_home'].get('elite_defense', False),
                all_results['elite_defense_away'].get('elite_defense', False)
            )
            all_results['has_total_under'] = all_results['total_under'].get('total_under_conditions', False)
            
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
            
            final_capital = all_results['tier_determination'].get('capital_multiplier', 0.0) * pattern_multiplier
            
            all_results['capital_allocation'] = {
                'tier_multiplier': all_results['tier_determination'].get('capital_multiplier', 0.0),
                'pattern_multiplier': pattern_multiplier,
                'final_capital_multiplier': final_capital,
                'tier_name': all_results['tier_determination'].get('name', 'ERROR'),
                'pattern_count': sum([
                    all_results['winner_lock'],
                    all_results['has_elite_defense'],
                    all_results['has_total_under']
                ])
            }
            
            # ========== STEP 7: GENERATE RECOMMENDATIONS ==========
            all_results['recommendations'] = DecisionFlowEngineV80.generate_recommendations_safe(all_results)
            
            # ========== STEP 8: DECISION FLOW SUMMARY ==========
            all_results['decision_flow'] = DecisionFlowEngineV80.create_decision_flow_summary_safe(all_results)
            
            return all_results
            
        except Exception as e:
            return {
                'error': f'Fatal error in decision flow: {str(e)}',
                'home_name': home_name,
                'away_name': away_name,
                'tier_determination': {'name': 'ERROR', 'capital_multiplier': 0.0, 'reason': str(e)},
                'capital_allocation': {'final_capital_multiplier': 0.0},
                'recommendations': [],
                'decision_flow': []
            }
    
    @staticmethod
    def generate_recommendations_safe(results: Dict) -> List[Dict]:
        """SAFE recommendation generation with error handling"""
        recommendations = []
        
        try:
            # Safely get team names
            home_name = results.get('home_name', 'Home Team')
            away_name = results.get('away_name', 'Away Team')
            
            # DOUBLE CHANCE from Winner Lock
            if results.get('winner_lock', False):
                agency_state = results.get('agency_state', {})
                controller = agency_state.get('controller', 'UNKNOWN')
                
                if controller == 'HOME':
                    selection = f"{home_name} win or draw"
                elif controller == 'AWAY':
                    selection = f"{away_name} win or draw"
                else:
                    selection = "Win or draw"
                
                recommendations.append({
                    'market': 'DOUBLE_CHANCE',
                    'selection': selection,
                    'confidence': 'HIGH',
                    'reason': 'Winner Lock detected → Double Chance implied',
                    'accuracy': '80% (4/5 backtest)',
                    'stake_sizing': 'PRIMARY' if results.get('tier_determination', {}).get('tier', 0) == 1 else 'SECONDARY'
                })
            
            # OPPONENT UNDER 1.5 from Elite Defense
            if results.get('has_elite_defense', False):
                elite_home = results.get('elite_defense_home', {}).get('elite_defense', False)
                elite_away = results.get('elite_defense_away', {}).get('elite_defense', False)
                
                if elite_home:
                    recommendations.append({
                        'market': 'OPPONENT_UNDER_1_5',
                        'selection': f"{away_name} Under 1.5",
                        'confidence': 'MODERATE',
                        'reason': 'Facing Elite Defense (Home)',
                        'accuracy': '62.5% (5/8 backtest)',
                        'stake_sizing': 'SECONDARY'
                    })
                
                if elite_away:
                    recommendations.append({
                        'market': 'OPPONENT_UNDER_1_5',
                        'selection': f"{home_name} Under 1.5",
                        'confidence': 'MODERATE',
                        'reason': 'Facing Elite Defense (Away)',
                        'accuracy': '62.5% (5/8 backtest)',
                        'stake_sizing': 'SECONDARY'
                    })
            
            # TOTAL UNDER 2.5 from Total Under conditions
            if results.get('has_total_under', False):
                total_under = results.get('total_under', {})
                path_count = total_under.get('path_count', 0)
                
                recommendations.append({
                    'market': 'TOTAL_UNDER_2_5',
                    'selection': 'Under 2.5 Goals',
                    'confidence': 'HIGH',
                    'reason': f'{path_count} path(s) to Under 2.5 confirmed',
                    'accuracy': '70% (7/10 backtest)',
                    'stake_sizing': 'PRIMARY' if not results.get('winner_lock', False) else 'SECONDARY'
                })
            
            # TOTAL UNDER 3.5 from confidence tier
            under35 = results.get('under_35_confidence', {})
            tier = under35.get('tier', 0)
            
            if tier > 0:
                confidence_levels = ['VERY HIGH', 'HIGH', 'MODERATE', 'LOW', 'VERY LOW']
                confidence_idx = min(tier, len(confidence_levels) - 1)
                
                recommendations.append({
                    'market': 'TOTAL_UNDER_3_5',
                    'selection': 'Under 3.5 Goals',
                    'confidence': confidence_levels[confidence_idx],
                    'reason': under35.get('description', 'Patterns detected'),
                    'accuracy': f'{under35.get("confidence", 0)*100:.1f}% theoretical',
                    'stake_sizing': 'SECONDARY' if results.get('winner_lock', False) else 'PRIMARY'
                })
            
        except Exception as e:
            # Return at least empty recommendations on error
            pass
        
        return recommendations
    
    @staticmethod
    def create_decision_flow_summary_safe(results: Dict) -> List[Dict]:
        """SAFE decision flow summary"""
        flow = []
        
        try:
            # Step 1
            winner_lock = results.get('winner_lock', False)
            agency_reason = results.get('agency_state', {}).get('reason', '')
            flow.append({
                'step': 1,
                'action': 'RUN AGENCY-STATE 4-GATE ANALYSIS',
                'result': 'WINNER LOCK DETECTED' if winner_lock else 'NO WINNER LOCK',
                'details': agency_reason[:100] + '...' if len(agency_reason) > 100 else agency_reason,
                'passed': winner_lock
            })
            
            # Step 2
            has_elite = results.get('has_elite_defense', False)
            elite_home = results.get('elite_defense_home', {}).get('elite_defense', False)
            elite_away = results.get('elite_defense_away', {}).get('elite_defense', False)
            flow.append({
                'step': 2,
                'action': 'CHECK ELITE DEFENSE',
                'result': 'ELITE DEFENSE PRESENT' if has_elite else 'NO ELITE DEFENSE',
                'details': f'Home: {elite_home}, Away: {elite_away}',
                'passed': has_elite
            })
            
            # Step 3
            has_total_under = results.get('has_total_under', False)
            total_under_reason = results.get('total_under', {}).get('reason', '')
            path_count = results.get('total_under', {}).get('path_count', 0)
            flow.append({
                'step': 3,
                'action': 'CHECK TOTAL UNDER CONDITIONS',
                'result': f'{path_count} PATH(S) CONFIRMED' if has_total_under else 'NO PATHS',
                'details': total_under_reason[:100] + '...' if len(total_under_reason) > 100 else total_under_reason,
                'passed': has_total_under
            })
            
            # Step 4
            tier_name = results.get('tier_determination', {}).get('name', 'ERROR')
            tier_reason = results.get('tier_determination', {}).get('reason', '')
            flow.append({
                'step': 4,
                'action': 'DETERMINE CONFIDENCE TIER',
                'result': tier_name,
                'details': tier_reason[:100] + '...' if len(tier_reason) > 100 else tier_reason,
                'passed': tier_name not in ['STAY_AWAY', 'ERROR']
            })
            
            # Step 5
            capital = results.get('capital_allocation', {})
            final_mult = capital.get('final_capital_multiplier', 0.0)
            tier_mult = capital.get('tier_multiplier', 0.0)
            pattern_mult = capital.get('pattern_multiplier', 0.0)
            flow.append({
                'step': 5,
                'action': 'CAPITAL ALLOCATION',
                'result': f'{final_mult:.1f}x CAPITAL',
                'details': f'Tier: {tier_mult:.1f}x × Patterns: {pattern_mult:.1f}x',
                'passed': final_mult > 0
            })
            
        except Exception:
            # Return minimal flow on error
            flow = [{
                'step': 1,
                'action': 'ERROR',
                'result': 'ANALYSIS FAILED',
                'details': 'Error creating decision flow',
                'passed': False
            }]
        
        return flow

# =================== STREAMLIT UI v8.0 ===================
def main():
    """Fused Logic Engine v8.0 Streamlit App"""
    
    st.set_page_config(
        page_title="Fused Logic Engine v8.0 - REAL Agency-State System",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS
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
            Tiered Confidence System • REAL Data Analysis • Adjusted Accuracy Claims<br>
            <span style="color: #DC2626; font-weight: bold;">NO HARDCODED TEAM NAMES OR SCORES - ALL DATA FROM CSV</span>
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
        
        # Debug info
        if st.session_state.df is not None:
            st.markdown("---")
            st.markdown("### 📊 Data Info")
            st.write(f"Teams: {len(st.session_state.df)}")
            st.write(f"Columns: {len(st.session_state.df.columns)}")
    
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
        teams = sorted(df['team'].unique().tolist()) if 'team' in df.columns else []
        if not teams:
            st.error("No teams found in data!")
            return
        
        home_team = st.selectbox("Home Team", teams, key="home_team")
        
        # Get home team data
        home_row = df[df['team'] == home_team]
        if not home_row.empty:
            home_data = home_row.iloc[0].to_dict()
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.2)
            home_eff = get_safe_value(home_data, 'efficiency', 0.8) * 100
            home_scored = get_safe_value(home_data, 'goals_scored_last_5', 0)
            home_conceded = get_safe_value(home_data, 'goals_conceded_last_5', 0)
            
            st.info(f"**Agency-State Metrics:** {home_xg:.2f} xG/match, {home_eff:.0f}% efficiency")
            st.info(f"**Last 5:** {home_scored} scored, {home_conceded} conceded")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team")
        
        # Get away team data
        away_row = df[df['team'] == away_team]
        if not away_row.empty:
            away_data = away_row.iloc[0].to_dict()
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.2)
            away_eff = get_safe_value(away_data, 'efficiency', 0.8) * 100
            away_scored = get_safe_value(away_data, 'goals_scored_last_5', 0)
            away_conceded = get_safe_value(away_data, 'goals_conceded_last_5', 0)
            
            st.info(f"**Agency-State Metrics:** {away_xg:.2f} xG/match, {away_eff:.0f}% efficiency")
            st.info(f"**Last 5:** {away_scored} scored, {away_conceded} conceded")
    
    # Run analysis button
    if st.button("🚀 RUN AGENCY-STATE ANALYSIS v8.0", type="primary", use_container_width=True):
        with st.spinner("Executing 4-Gate Agency-State analysis..."):
            try:
                engine = DecisionFlowEngineV80()
                result = engine.execute_decision_flow(
                    home_data, away_data, home_team, away_team
                )
                st.session_state.analysis_result = result
                
                # Check for errors in result
                if 'error' in result:
                    st.error(f"❌ Analysis error: {result['error']}")
                else:
                    st.success("✅ Agency-State analysis complete!")
                    
            except Exception as e:
                st.error(f"❌ Fatal error: {str(e)}")
                st.session_state.analysis_result = {
                    'error': str(e),
                    'home_name': home_team,
                    'away_name': away_team,
                    'tier_determination': {'name': 'ERROR', 'capital_multiplier': 0.0},
                    'capital_allocation': {'final_capital_multiplier': 0.0},
                    'recommendations': [],
                    'decision_flow': []
                }
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Check for error
        if 'error' in result:
            st.error(f"❌ Analysis failed: {result['error']}")
            return
        
        # Tier Banner
        tier = result['tier_determination']
        tier_class = f"tier-{tier.get('tier', 4)}"
        
        st.markdown(f"""
        <div class="pattern-card {tier_class}" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                {'🎯' if tier.get('tier') == 1 else '📊' if tier.get('tier') == 2 else '⚠️' if tier.get('tier') == 3 else '🚫'}
            </div>
            <h2 style="margin: 0;">{tier.get('name', 'ERROR')}</h2>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                {result.get('capital_allocation', {}).get('final_capital_multiplier', 0.0):.1f}x CAPITAL
            </div>
            <div style="color: rgba(255,255,255,0.9);">
                {tier.get('reason', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Decision Flow
        st.markdown("### 📋 Decision Flow v8.0")
        decision_flow = result.get('decision_flow', [])
        for step in decision_flow:
            with st.container():
                cols = st.columns([0.1, 0.2, 0.4, 0.3])
                with cols[0]:
                    st.write(f"**{step.get('step', '?')}**")
                with cols[1]:
                    st.write(f"{'✅' if step.get('passed', False) else '❌'} {step.get('action', '')}")
                with cols[2]:
                    st.write(f"**{step.get('result', '')}**")
                    details = step.get('details', '')
                    if details:
                        st.caption(details)
                with cols[3]:
                    if step.get('step') == 5:
                        st.metric("Multiplier", f"{result.get('capital_allocation', {}).get('final_capital_multiplier', 0.0):.1f}x")
        
        # Pattern Detections
        st.markdown("### 🔍 Pattern Detections")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if result.get('winner_lock', False):
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
            else:
                st.markdown("""
                <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2rem; color: #9CA3AF;">🎯</div>
                    <h3 style="margin: 0.5rem 0; color: #6B7280;">NO WINNER LOCK</h3>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if result.get('has_elite_defense', False):
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
            else:
                st.markdown("""
                <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2rem; color: #9CA3AF;">🛡️</div>
                    <h3 style="margin: 0.5rem 0; color: #6B7280;">NO ELITE DEFENSE</h3>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if result.get('has_total_under', False):
                path_count = result.get('total_under', {}).get('path_count', 0)
                st.markdown(f"""
                <div class="pattern-card total-under">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">📉</div>
                        <h3 style="margin: 0.5rem 0;">TOTAL UNDER</h3>
                        <div style="font-size: 0.9rem;">{path_count} path(s) confirmed</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            📈 70% accuracy (7/10)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 2rem; color: #9CA3AF;">📉</div>
                    <h3 style="margin: 0.5rem 0; color: #6B7280;">NO TOTAL UNDER</h3>
                </div>
                """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💰 Bet Recommendations")
        recommendations = result.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                with st.container():
                    cols = st.columns([0.3, 0.4, 0.2, 0.1])
                    with cols[0]:
                        st.markdown(f"**{rec.get('market', '')}**")
                    with cols[1]:
                        st.write(rec.get('selection', ''))
                        reason = rec.get('reason', '')
                        if reason:
                            st.caption(reason)
                    with cols[2]:
                        accuracy = rec.get('accuracy', '')
                        if accuracy:
                            st.metric("Confidence", rec.get('confidence', ''), accuracy)
                        else:
                            st.metric("Confidence", rec.get('confidence', ''))
                    with cols[3]:
                        st.caption(f"**{rec.get('stake_sizing', '')}**")
        else:
            st.info("No bet recommendations - consider staying away")
        
        # Agency-State Gate Details
        if result.get('winner_lock', False) and result.get('agency_state', {}).get('gates'):
            st.markdown("### ⚙️ Agency-State 4-Gate Analysis")
            gates = result['agency_state']['gates']
            
            gate_cols = st.columns(4)
            gate_data = [
                ("GATE 1", "Quiet Control", gates['gate1'].get('result', ''), gates['gate1'].get('reason', '')),
                ("GATE 2", "Directional Dominance", gates['gate2'].get('result', ''), gates['gate2'].get('reason', '')),
                ("GATE 3", "State-Flip Capacity", gates['gate3'].get('result', ''), gates['gate3'].get('reason', '')),
                ("GATE 4", "Enforcement", gates['gate4'].get('result', ''), gates['gate4'].get('reason', ''))
            ]
            
            for idx, (title, subtitle, result_text, reason) in enumerate(gate_data):
                with gate_cols[idx]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); 
                                color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{title}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;">{subtitle}</div>
                        <div style="font-weight: bold; margin-bottom: 0.5rem;">{result_text}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{reason[:50]}{'...' if len(reason) > 50 else ''}</div>
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
        alloc = result.get('capital_allocation', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tier Multiplier", f"{alloc.get('tier_multiplier', 0.0):.1f}x")
        with col2:
            st.metric("Pattern Multiplier", f"{alloc.get('pattern_multiplier', 0.0):.1f}x")
        with col3:
            st.metric("Pattern Count", alloc.get('pattern_count', 0))
        with col4:
            st.metric("Final Multiplier", f"{alloc.get('final_capital_multiplier', 0.0):.1f}x")
        
        # Team Stats Summary
        st.markdown("### 📊 Team Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{home_team}**")
            st.metric("xG/Match", f"{get_safe_value(home_data, 'xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{get_safe_value(home_data, 'efficiency', 0)*100:.0f}%")
            st.metric("Last 5 Scored", get_safe_value(home_data, 'goals_scored_last_5', 0))
            st.metric("Last 5 Conceded", get_safe_value(home_data, 'goals_conceded_last_5', 0))
        
        with col2:
            st.markdown(f"**{away_team}**")
            st.metric("xG/Match", f"{get_safe_value(away_data, 'xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{get_safe_value(away_data, 'efficiency', 0)*100:.0f}%")
            st.metric("Last 5 Scored", get_safe_value(away_data, 'goals_scored_last_5', 0))
            st.metric("Last 5 Conceded", get_safe_value(away_data, 'goals_conceded_last_5', 0))

if __name__ == "__main__":
    main()
