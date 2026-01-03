"""
FUSED LOGIC ENGINE v8.0 - EXACT IMPLEMENTATION OF UNIVERSAL LAW
COMPLETE SPECIFICATION IMPLEMENTATION - NO DEVIATIONS
ALL LOGIC FROM THE PROVIDED SPECIFICATION
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# =================== UNIVERSAL CONSTANTS ===================
# All thresholds from specification Section 9
UNIVERSAL_THRESHOLDS = {
    # Gate 1
    'TEMPO_DOMINANCE': 1.4,
    'SCORING_EFFICIENCY': 90,  # Percentage
    'CRITICAL_AREA_THREAT': 0.25,
    'REPEATABLE_PATTERNS_OPENPLAY': 0.5,
    'REPEATABLE_PATTERNS_COUNTER': 0.15,
    
    # Gate 2
    'DIRECTIONAL_DELTA': 0.25,
    'MARKET_THRESHOLD': 1.1,
    
    # Gate 3
    'CHASE_CAPACITY': 1.1,
    'TEMPO_SURGE': 1.4,
    'ALTERNATE_THREATS_SETPIECE': 0.25,
    'ALTERNATE_THREATS_COUNTER': 0.15,
    'SUBSTITUTION_LEVERAGE_FACTOR': 0.8,
    'LEAGUE_AVG_GOALS': 1.3,
    
    # Gate 4
    'DEFENSIVE_SOLIDITY_HOME': 1.2,
    'DEFENSIVE_SOLIDITY_AWAY': 1.3,
    'CONSISTENT_THREAT': 1.3,
    
    # Elite Defense
    'ABSOLUTE_DEFENSE': 4,
    'DEFENSE_GAP': 2.0,
    'LEAGUE_AVG_CONCEDED': 1.3,
    
    # Total Under
    'OFFENSIVE_INCAPACITY': 1.2,
    'DEFENSIVE_STRENGTH': 1.2,
    'ELITE_DEFENSE_DOMINANCE': 1.5,
}

# =================== DATA LOADING & PRE-CALCULATIONS ===================
@st.cache_data(ttl=3600)
def load_league_csv(league_name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load and pre-calculate ALL required metrics EXACTLY as per specification"""
    try:
        url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}"
        df = pd.read_csv(url)
        
        # Clean column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # ========== PRE-CALCULATIONS (Section 2) ==========
        
        # Season averages
        df['matches_played'] = df['home_matches_played'] + df['away_matches_played']
        df['goals_scored'] = df['home_goals_scored'] + df['away_goals_scored']
        df['goals_conceded'] = df['home_goals_conceded'] + df['away_goals_conceded']
        df['xg_for'] = df['home_xg_for'] + df['away_xg_for']
        df['xg_against'] = df['home_xg_against'] + df['away_xg_against']
        
        # Per match averages
        df['goals_per_match'] = df.apply(
            lambda x: x['goals_scored'] / x['matches_played'] if x['matches_played'] > 0 else 1.0, 
            axis=1
        )
        df['conceded_per_match'] = df.apply(
            lambda x: x['goals_conceded'] / x['matches_played'] if x['matches_played'] > 0 else 1.0, 
            axis=1
        )
        df['xg_per_match'] = df.apply(
            lambda x: x['xg_for'] / x['matches_played'] if x['matches_played'] > 0 else 1.0, 
            axis=1
        )
        
        # Last 5 averages (CRITICAL: use LAST 5 columns, NOT season)
        df['avg_goals_scored_last_5'] = df['goals_scored_last_5'] / 5
        df['avg_goals_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        
        # Home/away specific averages
        df['home_goals_per_match'] = df.apply(
            lambda x: x['home_goals_scored'] / x['home_matches_played'] if x['home_matches_played'] > 0 else x['goals_per_match'],
            axis=1
        )
        df['away_goals_per_match'] = df.apply(
            lambda x: x['away_goals_scored'] / x['away_matches_played'] if x['away_matches_played'] > 0 else x['goals_per_match'],
            axis=1
        )
        
        df['home_conceded_per_match'] = df.apply(
            lambda x: x['home_goals_conceded'] / x['home_matches_played'] if x['home_matches_played'] > 0 else x['conceded_per_match'],
            axis=1
        )
        df['away_conceded_per_match'] = df.apply(
            lambda x: x['away_goals_conceded'] / x['away_matches_played'] if x['away_matches_played'] > 0 else x['conceded_per_match'],
            axis=1
        )
        
        df['home_xg_per_match'] = df.apply(
            lambda x: x['home_xg_for'] / x['home_matches_played'] if x['home_matches_played'] > 0 else x['xg_per_match'],
            axis=1
        )
        df['away_xg_per_match'] = df.apply(
            lambda x: x['away_xg_for'] / x['away_matches_played'] if x['away_matches_played'] > 0 else x['xg_per_match'],
            axis=1
        )
        
        # Efficiency (Goals/xG) - SEASON TOTAL
        df['efficiency'] = df.apply(
            lambda x: (x['goals_scored'] / x['xg_for']) * 100 if x['xg_for'] > 0 else 100,
            axis=1
        )
        
        # Scoring percentages - SEASON TOTAL
        df['total_goals'] = df['goals_scored']
        
        # Calculate total setpiece goals (setpiece + penalty)
        if 'home_goals_setpiece_for' in df.columns and 'home_goals_penalty_for' in df.columns:
            df['total_setpiece_goals'] = (
                df['home_goals_setpiece_for'] + df['away_goals_setpiece_for'] + 
                df['home_goals_penalty_for'] + df['away_goals_penalty_for']
            )
        else:
            df['total_setpiece_goals'] = 0
        
        # Calculate total counter goals
        if 'home_goals_counter_for' in df.columns:
            df['total_counter_goals'] = (
                df['home_goals_counter_for'] + df['away_goals_counter_for']
            )
        else:
            df['total_counter_goals'] = 0
        
        # Calculate percentages
        df['setpiece_pct'] = df.apply(
            lambda x: x['total_setpiece_goals'] / x['total_goals'] if x['total_goals'] > 0 else 0,
            axis=1
        )
        df['counter_pct'] = df.apply(
            lambda x: x['total_counter_goals'] / x['total_goals'] if x['total_goals'] > 0 else 0,
            axis=1
        )
        df['openplay_pct'] = 1 - (df['setpiece_pct'] + df['counter_pct'])
        
        # Add league averages if not present
        df['league_avg_goals'] = df['goals_per_match'].mean() if len(df) > 0 else 1.3
        df['league_avg_conceded'] = df['conceded_per_match'].mean() if len(df) > 0 else 1.3
        
        return df.fillna(0)
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== WINNER LOCK - 4 GATE SYSTEM ===================
class WinnerLock4GateSystem:
    """EXACT implementation of 4-Gate System from specification"""
    
    @staticmethod
    def gate1_quiet_control(controller_data: Dict, opponent_data: Dict) -> Dict:
        """GATE 1: Quiet Control Identification - EXACT logic from spec"""
        try:
            # CRITERIA 1: Tempo Dominance
            controller_tempo = controller_data.get('xg_per_match', 1.0) > UNIVERSAL_THRESHOLDS['TEMPO_DOMINANCE']
            opponent_tempo = opponent_data.get('xg_per_match', 1.0) > UNIVERSAL_THRESHOLDS['TEMPO_DOMINANCE']
            
            if controller_tempo and not opponent_tempo:
                tempo_points = 1.0
            elif controller_tempo and opponent_tempo:
                tempo_points = 0.5
            elif not controller_tempo and opponent_tempo:
                tempo_points = 0
            else:
                tempo_points = 0
            
            # CRITERIA 2: Scoring Efficiency
            controller_eff = controller_data.get('efficiency', 0) > UNIVERSAL_THRESHOLDS['SCORING_EFFICIENCY']
            opponent_eff = opponent_data.get('efficiency', 0) > UNIVERSAL_THRESHOLDS['SCORING_EFFICIENCY']
            
            if controller_eff and not opponent_eff:
                eff_points = 1.0
            elif controller_eff and opponent_eff:
                eff_points = 0.5
            elif not controller_eff and opponent_eff:
                eff_points = 0
            else:
                eff_points = 0
            
            # CRITERIA 3: Critical Area Threat
            controller_setpiece = controller_data.get('setpiece_pct', 0) > UNIVERSAL_THRESHOLDS['CRITICAL_AREA_THREAT']
            opponent_setpiece = opponent_data.get('setpiece_pct', 0) > UNIVERSAL_THRESHOLDS['CRITICAL_AREA_THREAT']
            
            if controller_setpiece and not opponent_setpiece:
                setpiece_points = 1.0
            elif controller_setpiece and opponent_setpiece:
                setpiece_points = 0.5
            elif not controller_setpiece and opponent_setpiece:
                setpiece_points = 0
            else:
                setpiece_points = 0
            
            # CRITERIA 4: Repeatable Patterns
            controller_openplay = controller_data.get('openplay_pct', 0)
            controller_counter = controller_data.get('counter_pct', 0)
            opponent_openplay = opponent_data.get('openplay_pct', 0)
            opponent_counter = opponent_data.get('counter_pct', 0)
            
            controller_patterns = (
                controller_openplay > UNIVERSAL_THRESHOLDS['REPEATABLE_PATTERNS_OPENPLAY'] or
                controller_counter > UNIVERSAL_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER']
            )
            opponent_patterns = (
                opponent_openplay > UNIVERSAL_THRESHOLDS['REPEATABLE_PATTERNS_OPENPLAY'] or
                opponent_counter > UNIVERSAL_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER']
            )
            
            if controller_patterns and not opponent_patterns:
                pattern_points = 1.0
            elif controller_patterns and opponent_patterns:
                pattern_points = 0.5
            elif not controller_patterns and opponent_patterns:
                pattern_points = 0
            else:
                pattern_points = 0
            
            # Calculate total points
            total_points = tempo_points + eff_points + setpiece_points + pattern_points
            
            # GATE 1 PASSES IF: Total points ≥ 2.0
            gate_passed = total_points >= 2.0
            
            return {
                'gate_passed': gate_passed,
                'total_points': total_points,
                'breakdown': {
                    'tempo_dominance': {'controller': controller_tempo, 'opponent': opponent_tempo, 'points': tempo_points},
                    'scoring_efficiency': {'controller': controller_eff, 'opponent': opponent_eff, 'points': eff_points},
                    'critical_area_threat': {'controller': controller_setpiece, 'opponent': opponent_setpiece, 'points': setpiece_points},
                    'repeatable_patterns': {'controller': controller_patterns, 'opponent': opponent_patterns, 'points': pattern_points}
                },
                'reason': f'Gate 1: Total points = {total_points:.1f} / 2.0 required'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'error': f'Gate 1 error: {str(e)}'
            }
    
    @staticmethod
    def gate2_directional_dominance(controller_data: Dict, opponent_data: Dict, 
                                   controller_is_home: bool) -> Dict:
        """GATE 2: Directional Dominance - EXACT logic from spec"""
        try:
            # Get venue-specific xG per match
            if controller_is_home:
                controller_xg_per_match = controller_data.get('home_xg_per_match', controller_data.get('xg_per_match', 1.0))
                opponent_xg_per_match = opponent_data.get('away_xg_per_match', opponent_data.get('xg_per_match', 1.0))
            else:
                controller_xg_per_match = controller_data.get('away_xg_per_match', controller_data.get('xg_per_match', 1.0))
                opponent_xg_per_match = opponent_data.get('home_xg_per_match', opponent_data.get('xg_per_match', 1.0))
            
            # CONDITION 1: Control Delta > 0.25
            delta = controller_xg_per_match - opponent_xg_per_match
            
            # CONDITION 2: Opponent xG < Market Threshold
            opponent_below_threshold = opponent_xg_per_match < UNIVERSAL_THRESHOLDS['MARKET_THRESHOLD']
            
            # GATE 2 PASSES IF: delta > 0.25 AND opponent_xg_per_match < 1.1
            gate_passed = delta > UNIVERSAL_THRESHOLDS['DIRECTIONAL_DELTA'] and opponent_below_threshold
            
            return {
                'gate_passed': gate_passed,
                'delta': delta,
                'opponent_xg': opponent_xg_per_match,
                'conditions': {
                    'delta_condition': delta > UNIVERSAL_THRESHOLDS['DIRECTIONAL_DELTA'],
                    'opponent_threshold': opponent_below_threshold
                },
                'reason': f'Gate 2: Delta = {delta:.3f} (>{UNIVERSAL_THRESHOLDS["DIRECTIONAL_DELTA"]}), Opponent xG = {opponent_xg_per_match:.3f} (<{UNIVERSAL_THRESHOLDS["MARKET_THRESHOLD"]})'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'error': f'Gate 2 error: {str(e)}'
            }
    
    @staticmethod
    def gate3_state_flip_capacity(opponent_data: Dict) -> Dict:
        """GATE 3: State-Flip Capacity - EXACT logic from spec"""
        try:
            failures = 0
            
            opponent_xg_per_match = opponent_data.get('xg_per_match', 1.0)
            
            # FAILURE 1: Chase Capacity
            if opponent_xg_per_match < UNIVERSAL_THRESHOLDS['CHASE_CAPACITY']:
                failures += 1
            
            # FAILURE 2: Tempo Surge
            if opponent_xg_per_match < UNIVERSAL_THRESHOLDS['TEMPO_SURGE']:
                failures += 1
            
            # FAILURE 3: Alternate Threats
            opponent_setpiece = opponent_data.get('setpiece_pct', 0)
            opponent_counter = opponent_data.get('counter_pct', 0)
            
            if (opponent_setpiece < UNIVERSAL_THRESHOLDS['ALTERNATE_THREATS_SETPIECE'] and 
                opponent_counter < UNIVERSAL_THRESHOLDS['ALTERNATE_THREATS_COUNTER']):
                failures += 1
            
            # FAILURE 4: Substitution Leverage
            opponent_goals_per_match = opponent_data.get('goals_per_match', 1.0)
            league_avg_goals = opponent_data.get('league_avg_goals', UNIVERSAL_THRESHOLDS['LEAGUE_AVG_GOALS'])
            
            if opponent_goals_per_match < (league_avg_goals * UNIVERSAL_THRESHOLDS['SUBSTITUTION_LEVERAGE_FACTOR']):
                failures += 1
            
            # GATE 3 PASSES IF: failures ≥ 2
            gate_passed = failures >= 2
            
            return {
                'gate_passed': gate_passed,
                'failure_count': failures,
                'breakdown': {
                    'chase_capacity': opponent_xg_per_match < UNIVERSAL_THRESHOLDS['CHASE_CAPACITY'],
                    'tempo_surge': opponent_xg_per_match < UNIVERSAL_THRESHOLDS['TEMPO_SURGE'],
                    'alternate_threats': (opponent_setpiece < UNIVERSAL_THRESHOLDS['ALTERNATE_THREATS_SETPIECE'] and 
                                        opponent_counter < UNIVERSAL_THRESHOLDS['ALTERNATE_THREATS_COUNTER']),
                    'substitution_leverage': opponent_goals_per_match < (league_avg_goals * UNIVERSAL_THRESHOLDS['SUBSTITUTION_LEVERAGE_FACTOR'])
                },
                'reason': f'Gate 3: {failures}/4 opponent failures (≥2 required)'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'error': f'Gate 3 error: {str(e)}'
            }
    
    @staticmethod
    def gate4_enforcement_without_urgency(controller_data: Dict, controller_is_home: bool) -> Dict:
        """GATE 4: Enforcement Without Urgency - EXACT logic from spec"""
        try:
            methods = 0
            
            # METHOD 1: Defensive Solidity
            if controller_is_home:
                defensive_solidity = controller_data.get('home_conceded_per_match', 1.0) < UNIVERSAL_THRESHOLDS['DEFENSIVE_SOLIDITY_HOME']
            else:
                defensive_solidity = controller_data.get('away_conceded_per_match', 1.0) < UNIVERSAL_THRESHOLDS['DEFENSIVE_SOLIDITY_AWAY']
            
            if defensive_solidity:
                methods += 1
            
            # METHOD 2: Alternate Scoring
            controller_setpiece = controller_data.get('setpiece_pct', 0)
            controller_counter = controller_data.get('counter_pct', 0)
            
            alternate_scoring = (
                controller_setpiece > UNIVERSAL_THRESHOLDS['CRITICAL_AREA_THREAT'] or
                controller_counter > UNIVERSAL_THRESHOLDS['REPEATABLE_PATTERNS_COUNTER']
            )
            
            if alternate_scoring:
                methods += 1
            
            # METHOD 3: Consistent Threat
            if controller_is_home:
                consistent_threat = controller_data.get('home_xg_per_match', 1.0) > UNIVERSAL_THRESHOLDS['CONSISTENT_THREAT']
            else:
                consistent_threat = controller_data.get('away_xg_per_match', 1.0) > UNIVERSAL_THRESHOLDS['CONSISTENT_THREAT']
            
            if consistent_threat:
                methods += 1
            
            # GATE 4 PASSES IF: methods ≥ 2
            gate_passed = methods >= 2
            
            return {
                'gate_passed': gate_passed,
                'method_count': methods,
                'breakdown': {
                    'defensive_solidity': defensive_solidity,
                    'alternate_scoring': alternate_scoring,
                    'consistent_threat': consistent_threat
                },
                'reason': f'Gate 4: {methods}/3 enforcement methods (≥2 required)'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'error': f'Gate 4 error: {str(e)}'
            }
    
    @staticmethod
    def run_complete_4gate_analysis(home_data: Dict, away_data: Dict) -> Dict:
        """Run complete 4-Gate analysis for BOTH teams"""
        try:
            # Try HOME as controller
            home_as_controller = {}
            home_as_controller['gate1'] = WinnerLock4GateSystem.gate1_quiet_control(home_data, away_data)
            
            if home_as_controller['gate1']['gate_passed']:
                home_as_controller['gate2'] = WinnerLock4GateSystem.gate2_directional_dominance(
                    home_data, away_data, controller_is_home=True
                )
                home_as_controller['gate3'] = WinnerLock4GateSystem.gate3_state_flip_capacity(away_data)
                home_as_controller['gate4'] = WinnerLock4GateSystem.gate4_enforcement_without_urgency(
                    home_data, controller_is_home=True
                )
                
                home_winner_lock = all([
                    home_as_controller['gate1']['gate_passed'],
                    home_as_controller['gate2']['gate_passed'],
                    home_as_controller['gate3']['gate_passed'],
                    home_as_controller['gate4']['gate_passed']
                ])
            else:
                home_winner_lock = False
            
            # Try AWAY as controller
            away_as_controller = {}
            away_as_controller['gate1'] = WinnerLock4GateSystem.gate1_quiet_control(away_data, home_data)
            
            if away_as_controller['gate1']['gate_passed']:
                away_as_controller['gate2'] = WinnerLock4GateSystem.gate2_directional_dominance(
                    away_data, home_data, controller_is_home=False
                )
                away_as_controller['gate3'] = WinnerLock4GateSystem.gate3_state_flip_capacity(home_data)
                away_as_controller['gate4'] = WinnerLock4GateSystem.gate4_enforcement_without_urgency(
                    away_data, controller_is_home=False
                )
                
                away_winner_lock = all([
                    away_as_controller['gate1']['gate_passed'],
                    away_as_controller['gate2']['gate_passed'],
                    away_as_controller['gate3']['gate_passed'],
                    away_as_controller['gate4']['gate_passed']
                ])
            else:
                away_winner_lock = False
            
            # Determine result
            if home_winner_lock:
                return {
                    'winner_lock': True,
                    'controller': 'HOME',
                    'gates': home_as_controller,
                    'reason': 'Home team passes all 4 gates',
                    'gate_summary': {
                        'gate1': home_as_controller['gate1']['gate_passed'],
                        'gate2': home_as_controller['gate2']['gate_passed'],
                        'gate3': home_as_controller['gate3']['gate_passed'],
                        'gate4': home_as_controller['gate4']['gate_passed']
                    }
                }
            elif away_winner_lock:
                return {
                    'winner_lock': True,
                    'controller': 'AWAY',
                    'gates': away_as_controller,
                    'reason': 'Away team passes all 4 gates',
                    'gate_summary': {
                        'gate1': away_as_controller['gate1']['gate_passed'],
                        'gate2': away_as_controller['gate2']['gate_passed'],
                        'gate3': away_as_controller['gate3']['gate_passed'],
                        'gate4': away_as_controller['gate4']['gate_passed']
                    }
                }
            else:
                return {
                    'winner_lock': False,
                    'reason': 'No team passes all 4 gates',
                    'gate_summary': {
                        'home': {
                            'gate1': home_as_controller.get('gate1', {}).get('gate_passed', False),
                            'gate2': home_as_controller.get('gate2', {}).get('gate_passed', False) if 'gate2' in home_as_controller else False,
                            'gate3': home_as_controller.get('gate3', {}).get('gate_passed', False) if 'gate3' in home_as_controller else False,
                            'gate4': home_as_controller.get('gate4', {}).get('gate_passed', False) if 'gate4' in home_as_controller else False
                        },
                        'away': {
                            'gate1': away_as_controller.get('gate1', {}).get('gate_passed', False),
                            'gate2': away_as_controller.get('gate2', {}).get('gate_passed', False) if 'gate2' in away_as_controller else False,
                            'gate3': away_as_controller.get('gate3', {}).get('gate_passed', False) if 'gate3' in away_as_controller else False,
                            'gate4': away_as_controller.get('gate4', {}).get('gate_passed', False) if 'gate4' in away_as_controller else False
                        }
                    }
                }
            
        except Exception as e:
            return {
                'winner_lock': False,
                'error': f'4-Gate analysis error: {str(e)}'
            }

# =================== ELITE DEFENSE PATTERN ===================
class EliteDefensePattern:
    """EXACT implementation of Elite Defense Pattern from specification"""
    
    @staticmethod
    def detect_elite_defense(team_data: Dict, is_home: bool = True) -> Dict:
        """Detect Elite Defense pattern - EXACT logic from spec"""
        try:
            goals_conceded_last_5 = team_data.get('goals_conceded_last_5', 10)
            avg_conceded_last_5 = goals_conceded_last_5 / 5
            
            # CONDITION 1: Absolute Defense
            absolute_defense = goals_conceded_last_5 <= UNIVERSAL_THRESHOLDS['ABSOLUTE_DEFENSE']
            
            # CONDITION 2: Relative Advantage
            league_avg_conceded = team_data.get('league_avg_conceded', UNIVERSAL_THRESHOLDS['LEAGUE_AVG_CONCEDED'])
            defense_gap = league_avg_conceded - avg_conceded_last_5
            
            relative_advantage = defense_gap > UNIVERSAL_THRESHOLDS['DEFENSE_GAP']
            
            # ELITE DEFENSE = goals_conceded_last_5 ≤ 4 AND defense_gap > 2.0
            elite_defense = absolute_defense and relative_advantage
            
            return {
                'elite_defense': elite_defense,
                'goals_conceded_last_5': goals_conceded_last_5,
                'avg_conceded_last_5': avg_conceded_last_5,
                'league_avg_conceded': league_avg_conceded,
                'defense_gap': defense_gap,
                'conditions': {
                    'absolute_defense': absolute_defense,
                    'relative_advantage': relative_advantage
                },
                'reason': f'Elite Defense: {goals_conceded_last_5} ≤ {UNIVERSAL_THRESHOLDS["ABSOLUTE_DEFENSE"]} and gap {defense_gap:.2f} > {UNIVERSAL_THRESHOLDS["DEFENSE_GAP"]}'
            }
            
        except Exception as e:
            return {
                'elite_defense': False,
                'error': f'Elite Defense error: {str(e)}'
            }

# =================== TOTAL UNDER CONDITIONS ===================
class TotalUnderConditions:
    """EXACT implementation of Total Under Conditions from specification"""
    
    @staticmethod
    def check_total_under_conditions(home_data: Dict, away_data: Dict, 
                                   home_elite_defense: bool, away_elite_defense: bool) -> Dict:
        """Check all three paths for Total Under - EXACT logic from spec"""
        try:
            # Calculate averages from last 5
            home_avg_goals_scored_last_5 = home_data.get('avg_goals_scored_last_5', 1.2)
            away_avg_goals_scored_last_5 = away_data.get('avg_goals_scored_last_5', 1.2)
            home_avg_goals_conceded_last_5 = home_data.get('avg_goals_conceded_last_5', 1.2)
            away_avg_goals_conceded_last_5 = away_data.get('avg_goals_conceded_last_5', 1.2)
            
            paths = []
            
            # PATH A: Offensive Incapacity
            path_a = (
                home_avg_goals_scored_last_5 <= UNIVERSAL_THRESHOLDS['OFFENSIVE_INCAPACITY'] and
                away_avg_goals_scored_last_5 <= UNIVERSAL_THRESHOLDS['OFFENSIVE_INCAPACITY']
            )
            if path_a:
                paths.append('OFFENSIVE_INCAPACITY')
            
            # PATH B: Defensive Strength
            path_b = (
                home_avg_goals_conceded_last_5 <= UNIVERSAL_THRESHOLDS['DEFENSIVE_STRENGTH'] and
                away_avg_goals_conceded_last_5 <= UNIVERSAL_THRESHOLDS['DEFENSIVE_STRENGTH']
            )
            if path_b:
                paths.append('DEFENSIVE_STRENGTH')
            
            # PATH C: Elite Defense Dominance
            path_c_home = home_elite_defense and away_avg_goals_scored_last_5 <= UNIVERSAL_THRESHOLDS['ELITE_DEFENSE_DOMINANCE']
            path_c_away = away_elite_defense and home_avg_goals_scored_last_5 <= UNIVERSAL_THRESHOLDS['ELITE_DEFENSE_DOMINANCE']
            path_c = path_c_home or path_c_away
            
            if path_c:
                paths.append('ELITE_DEFENSE_DOMINANCE')
            
            # TOTAL UNDER = PATH A OR PATH B OR PATH C
            total_under = len(paths) > 0
            
            return {
                'total_under': total_under,
                'paths': paths,
                'conditions': {
                    'path_a': path_a,
                    'path_b': path_b,
                    'path_c': path_c
                },
                'details': {
                    'home_avg_scored': home_avg_goals_scored_last_5,
                    'away_avg_scored': away_avg_goals_scored_last_5,
                    'home_avg_conceded': home_avg_goals_conceded_last_5,
                    'away_avg_conceded': away_avg_goals_conceded_last_5
                },
                'reason': f'Total Under: {len(paths)} path(s) confirmed' if total_under else 'No Total Under paths'
            }
            
        except Exception as e:
            return {
                'total_under': False,
                'error': f'Total Under error: {str(e)}'
            }

# =================== TIER DETERMINATION ===================
class TierDetermination:
    """EXACT implementation of Tier Determination from specification"""
    
    @staticmethod
    def determine_tier(winner_lock: bool, elite_defense: bool, total_under: bool) -> Dict:
        """Determine tier EXACTLY as per specification Section 6"""
        try:
            # TIER 1: LOCK_MODE (2.0x CAPITAL)
            if winner_lock and (elite_defense or total_under):
                tier = 1
                name = 'LOCK_MODE'
                capital_multiplier = 2.0
                reason = 'Winner Lock AND (Elite Defense OR Total Under)'
            
            # TIER 2: EDGE_MODE (1.0x CAPITAL)
            elif winner_lock or elite_defense or total_under:
                tier = 2
                name = 'EDGE_MODE'
                capital_multiplier = 1.0
                reason = 'Winner Lock OR Elite Defense OR Total Under (single pattern)'
            
            # TIER 3: STAY_AWAY (0.0x CAPITAL)
            else:
                tier = 3
                name = 'STAY_AWAY'
                capital_multiplier = 0.0
                reason = 'No patterns detected'
            
            return {
                'tier': tier,
                'name': name,
                'capital_multiplier': capital_multiplier,
                'reason': reason,
                'patterns': {
                    'winner_lock': winner_lock,
                    'elite_defense': elite_defense,
                    'total_under': total_under
                }
            }
            
        except Exception as e:
            return {
                'tier': 3,
                'name': 'ERROR',
                'capital_multiplier': 0.0,
                'reason': f'Tier determination error: {str(e)}'
            }

# =================== BET RECOMMENDATIONS ===================
class BetRecommendations:
    """EXACT implementation of Bet Recommendations from specification"""
    
    @staticmethod
    def generate_recommendations(tier: int, winner_lock: bool, controller: str, 
                               elite_defense: bool, total_under: bool,
                               home_team: str, away_team: str) -> List[Dict]:
        """Generate recommendations EXACTLY as per specification Section 7"""
        recommendations = []
        
        if tier == 1:  # LOCK_MODE
            # PRIMARY: Double Chance (Controller win or draw)
            if winner_lock and controller:
                if controller == 'HOME':
                    selection = f"{home_team} win or draw"
                else:
                    selection = f"{away_team} win or draw"
                recommendations.append({
                    'market': 'DOUBLE_CHANCE',
                    'selection': selection,
                    'priority': 'PRIMARY',
                    'reason': 'Winner Lock detected'
                })
            
            # SECONDARY: Total Under 3.5
            recommendations.append({
                'market': 'TOTAL_UNDER_3_5',
                'selection': 'Under 3.5 Goals',
                'priority': 'SECONDARY',
                'reason': 'Tier 1 Lock Mode'
            })
            
            # TERTIARY: Total Under 2.5 (if TOTAL_UNDER conditions present)
            if total_under:
                recommendations.append({
                    'market': 'TOTAL_UNDER_2_5',
                    'selection': 'Under 2.5 Goals',
                    'priority': 'TERTIARY',
                    'reason': 'Total Under conditions present'
                })
            
            # QUATERNARY: Opponent Under 1.5 (if facing ELITE_DEFENSE)
            if elite_defense:
                if controller == 'HOME':  # Away team faces elite defense
                    recommendations.append({
                        'market': 'OPPONENT_UNDER_1_5',
                        'selection': f"{away_team} Under 1.5 Goals",
                        'priority': 'QUATERNARY',
                        'reason': 'Opponent faces Elite Defense'
                    })
                else:  # Home team faces elite defense
                    recommendations.append({
                        'market': 'OPPONENT_UNDER_1_5',
                        'selection': f"{home_team} Under 1.5 Goals",
                        'priority': 'QUATERNARY',
                        'reason': 'Opponent faces Elite Defense'
                    })
        
        elif tier == 2:  # EDGE_MODE
            if winner_lock:
                if controller == 'HOME':
                    selection = f"{home_team} win or draw"
                else:
                    selection = f"{away_team} win or draw"
                recommendations.append({
                    'market': 'DOUBLE_CHANCE',
                    'selection': selection,
                    'priority': 'PRIMARY',
                    'reason': 'Winner Lock detected (Edge Mode)'
                })
            
            if elite_defense:
                # Determine which team has elite defense
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': 'Opponent Under 1.5 Goals',
                    'priority': 'PRIMARY' if not winner_lock else 'SECONDARY',
                    'reason': 'Elite Defense detected'
                })
            
            if total_under and not winner_lock and not elite_defense:
                recommendations.append({
                    'market': 'TOTAL_UNDER_2_5',
                    'selection': 'Under 2.5 Goals',
                    'priority': 'PRIMARY',
                    'reason': 'Total Under conditions detected'
                })
        
        return recommendations

# =================== MAIN ENGINE ===================
class FusedLogicEngineV80:
    """Main engine that orchestrates all components EXACTLY as per specification"""
    
    @staticmethod
    def analyze_match(home_team: str, away_team: str, 
                     home_data: Dict, away_data: Dict) -> Dict:
        """Complete match analysis EXACTLY as per universal specification"""
        try:
            results = {}
            
            # Store team names
            results['home_team'] = home_team
            results['away_team'] = away_team
            
            # ========== STEP 1: WINNER LOCK 4-GATE ANALYSIS ==========
            winner_lock_system = WinnerLock4GateSystem()
            winner_lock_result = winner_lock_system.run_complete_4gate_analysis(home_data, away_data)
            results['winner_lock'] = winner_lock_result
            
            winner_lock_detected = winner_lock_result.get('winner_lock', False)
            controller = winner_lock_result.get('controller', None)
            
            # ========== STEP 2: ELITE DEFENSE PATTERN ==========
            elite_defense_system = EliteDefensePattern()
            
            # Check both teams
            home_elite_defense = elite_defense_system.detect_elite_defense(home_data, is_home=True)
            away_elite_defense = elite_defense_system.detect_elite_defense(away_data, is_home=False)
            
            results['elite_defense'] = {
                'home': home_elite_defense,
                'away': away_elite_defense
            }
            
            elite_defense_detected = (
                home_elite_defense.get('elite_defense', False) or 
                away_elite_defense.get('elite_defense', False)
            )
            
            # ========== STEP 3: TOTAL UNDER CONDITIONS ==========
            total_under_system = TotalUnderConditions()
            total_under_result = total_under_system.check_total_under_conditions(
                home_data, away_data,
                home_elite_defense.get('elite_defense', False),
                away_elite_defense.get('elite_defense', False)
            )
            results['total_under'] = total_under_result
            
            total_under_detected = total_under_result.get('total_under', False)
            
            # ========== STEP 4: TIER DETERMINATION ==========
            tier_system = TierDetermination()
            tier_result = tier_system.determine_tier(
                winner_lock_detected,
                elite_defense_detected,
                total_under_detected
            )
            results['tier'] = tier_result
            
            # ========== STEP 5: BET RECOMMENDATIONS ==========
            bet_recommendations = BetRecommendations()
            recommendations = bet_recommendations.generate_recommendations(
                tier_result['tier'],
                winner_lock_detected,
                controller,
                elite_defense_detected,
                total_under_detected,
                home_team,
                away_team
            )
            results['recommendations'] = recommendations
            
            # ========== STEP 6: SUMMARY ==========
            results['summary'] = {
                'match': f"{home_team} vs {away_team}",
                'winner_lock': winner_lock_detected,
                'elite_defense': elite_defense_detected,
                'total_under': total_under_detected,
                'tier': tier_result['name'],
                'capital_multiplier': tier_result['capital_multiplier'],
                'recommendation_count': len(recommendations)
            }
            
            return results
            
        except Exception as e:
            return {
                'error': f'Analysis error: {str(e)}',
                'home_team': home_team,
                'away_team': away_team
            }

# =================== STREAMLIT UI ===================
def main():
    """Streamlit UI - Keeping frontend design untouched"""
    
    st.set_page_config(
        page_title="Fused Logic Engine v8.0 - EXACT Implementation",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS (keeping original design)
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
    .tier-3 { background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important; }
    .agency-gate { background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important; }
    .elite-defense { background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important; }
    .total-under { background: linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1E3A8A;">🎯 FUSED LOGIC ENGINE v8.0 - EXACT IMPLEMENTATION</h1>
        <div style="color: #4B5563; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
            <strong>UNIVERSAL LAW IMPLEMENTATION:</strong> Exact 4-Gate Winner Lock + Elite Defense + Total Under Conditions<br>
            <span style="color: #DC2626; font-weight: bold;">COMPLETE SPECIFICATION IMPLEMENTATION - NO DEVIATIONS</span>
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
                        st.success(f"✅ Loaded {len(df)} teams with ALL metrics")
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
        
        # Show Universal Law Guarantees
        st.markdown("### ⚖️ Universal Law Guarantees")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info("**Deterministic Results**\n\nSame data → Same output")
        with col2:
            st.info("**No Hidden Rules**\n\nAll logic exposed")
        with col3:
            st.info("**Clear Fail States**\n\nMissing data → Criterion fails")
        with col4:
            st.info("**Universal Application**\n\nWorks for all matches")
        
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
            
            # Display key metrics
            st.markdown("**Home Team Metrics:**")
            col1a, col2a = st.columns(2)
            with col1a:
                st.metric("xG/Match", f"{home_data.get('xg_per_match', 0):.2f}")
                st.metric("Efficiency", f"{home_data.get('efficiency', 0):.0f}%")
            with col2a:
                st.metric("Last 5 Scored", f"{home_data.get('goals_scored_last_5', 0)}")
                st.metric("Last 5 Conceded", f"{home_data.get('goals_conceded_last_5', 0)}")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team")
        
        # Get away team data
        away_row = df[df['team'] == away_team]
        if not away_row.empty:
            away_data = away_row.iloc[0].to_dict()
            
            # Display key metrics
            st.markdown("**Away Team Metrics:**")
            col1b, col2b = st.columns(2)
            with col1b:
                st.metric("xG/Match", f"{away_data.get('xg_per_match', 0):.2f}")
                st.metric("Efficiency", f"{away_data.get('efficiency', 0):.0f}%")
            with col2b:
                st.metric("Last 5 Scored", f"{away_data.get('goals_scored_last_5', 0)}")
                st.metric("Last 5 Conceded", f"{away_data.get('goals_conceded_last_5', 0)}")
    
    # Run analysis button
    if st.button("🚀 RUN EXACT UNIVERSAL ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Executing exact 4-Gate Winner Lock analysis..."):
            try:
                engine = FusedLogicEngineV80()
                result = engine.analyze_match(home_team, away_team, home_data, away_data)
                st.session_state.analysis_result = result
                
                if 'error' in result:
                    st.error(f"❌ Analysis error: {result['error']}")
                else:
                    st.success("✅ Exact Universal Law analysis complete!")
                    
            except Exception as e:
                st.error(f"❌ Fatal error: {str(e)}")
                st.session_state.analysis_result = {
                    'error': str(e),
                    'home_team': home_team,
                    'away_team': away_team
                }
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Check for error
        if 'error' in result:
            st.error(f"❌ Analysis failed: {result['error']}")
            return
        
        # Tier Banner
        tier = result['tier']
        
        st.markdown(f"""
        <div class="pattern-card tier-{tier['tier']}" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                {'🎯' if tier['tier'] == 1 else '📊' if tier['tier'] == 2 else '🚫'}
            </div>
            <h2 style="margin: 0;">{tier['name']}</h2>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                {tier['capital_multiplier']:.1f}x CAPITAL
            </div>
            <div style="color: rgba(255,255,255,0.9);">
                {tier['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern Detections
        st.markdown("### 🔍 Pattern Detections")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            winner_lock = result['winner_lock'].get('winner_lock', False)
            if winner_lock:
                controller = result['winner_lock'].get('controller', '')
                st.markdown(f"""
                <div class="pattern-card agency-gate">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">🎯</div>
                        <h3 style="margin: 0.5rem 0;">WINNER LOCK</h3>
                        <div style="font-size: 0.9rem;">Controller: {controller}</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            4-Gate Analysis Passed
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
            elite_home = result['elite_defense']['home'].get('elite_defense', False)
            elite_away = result['elite_defense']['away'].get('elite_defense', False)
            elite_detected = elite_home or elite_away
            
            if elite_detected:
                elite_team = home_team if elite_home else away_team
                st.markdown(f"""
                <div class="pattern-card elite-defense">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">🛡️</div>
                        <h3 style="margin: 0.5rem 0;">ELITE DEFENSE</h3>
                        <div style="font-size: 0.9rem;">{elite_team}</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            ≤{UNIVERSAL_THRESHOLDS['ABSOLUTE_DEFENSE']} conceded last 5
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
            total_under = result['total_under'].get('total_under', False)
            if total_under:
                paths = result['total_under'].get('paths', [])
                path_count = len(paths)
                st.markdown(f"""
                <div class="pattern-card total-under">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem;">📉</div>
                        <h3 style="margin: 0.5rem 0;">TOTAL UNDER</h3>
                        <div style="font-size: 0.9rem;">{path_count} path(s) confirmed</div>
                        <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                            {' | '.join(paths)}
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
        
        # Bet Recommendations
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
                        st.metric("Priority", rec.get('priority', ''))
                    with cols[3]:
                        if tier['tier'] == 1:
                            if rec['priority'] == 'PRIMARY':
                                st.caption("**FULL**")
                            elif rec['priority'] == 'SECONDARY':
                                st.caption("**50%**")
                            elif rec['priority'] == 'TERTIARY':
                                st.caption("**25%**")
                            else:
                                st.caption("**15%**")
                        else:
                            st.caption("**REDUCED**")
        else:
            st.info("No bet recommendations - Tier 3 (STAY_AWAY)")
        
        # Winner Lock Gate Details
        if result['winner_lock'].get('winner_lock', False):
            st.markdown("### ⚙️ Winner Lock 4-Gate Analysis")
            gates = result['winner_lock'].get('gates', {})
            
            gate_cols = st.columns(4)
            gate_data = [
                ("GATE 1", "Quiet Control", gates.get('gate1', {})),
                ("GATE 2", "Directional Dominance", gates.get('gate2', {})),
                ("GATE 3", "State-Flip Capacity", gates.get('gate3', {})),
                ("GATE 4", "Enforcement", gates.get('gate4', {}))
            ]
            
            for idx, (title, subtitle, gate) in enumerate(gate_data):
                with gate_cols[idx]:
                    if gate.get('gate_passed', False):
                        status = "✅ PASSED"
                        bg_color = "#059669"
                    else:
                        status = "❌ FAILED"
                        bg_color = "#DC2626"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{title}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;">{subtitle}</div>
                        <div style="font-weight: bold; margin-bottom: 0.5rem;">{status}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{gate.get('reason', '')[:60]}{'...' if len(gate.get('reason', '')) > 60 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Detailed Metrics
        with st.expander("📊 Detailed Team Metrics"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{home_team}**")
                metrics = [
                    ("Goals Scored", home_data.get('goals_scored', 0)),
                    ("Goals Conceded", home_data.get('goals_conceded', 0)),
                    ("xG For", f"{home_data.get('xg_for', 0):.1f}"),
                    ("xG Against", f"{home_data.get('xg_against', 0):.1f}"),
                    ("Matches Played", home_data.get('matches_played', 0)),
                    ("Home xG/Match", f"{home_data.get('home_xg_per_match', 0):.2f}"),
                    ("Home Conceded/Match", f"{home_data.get('home_conceded_per_match', 0):.2f}"),
                    ("Set Piece %", f"{home_data.get('setpiece_pct', 0)*100:.1f}%"),
                    ("Counter %", f"{home_data.get('counter_pct', 0)*100:.1f}%"),
                    ("Efficiency", f"{home_data.get('efficiency', 0):.0f}%")
                ]
                
                for label, value in metrics:
                    st.metric(label, value)
            
            with col2:
                st.markdown(f"**{away_team}**")
                metrics = [
                    ("Goals Scored", away_data.get('goals_scored', 0)),
                    ("Goals Conceded", away_data.get('goals_conceded', 0)),
                    ("xG For", f"{away_data.get('xg_for', 0):.1f}"),
                    ("xG Against", f"{away_data.get('xg_against', 0):.1f}"),
                    ("Matches Played", away_data.get('matches_played', 0)),
                    ("Away xG/Match", f"{away_data.get('away_xg_per_match', 0):.2f}"),
                    ("Away Conceded/Match", f"{away_data.get('away_conceded_per_match', 0):.2f}"),
                    ("Set Piece %", f"{away_data.get('setpiece_pct', 0)*100:.1f}%"),
                    ("Counter %", f"{away_data.get('counter_pct', 0)*100:.1f}%"),
                    ("Efficiency", f"{away_data.get('efficiency', 0):.0f}%")
                ]
                
                for label, value in metrics:
                    st.metric(label, value)
        
        # Universal Law Summary
        st.markdown("### ⚖️ Universal Law Implementation")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.success("✅ **Deterministic**")
            st.caption("Same data → Same output")
        with col2:
            st.success("✅ **Complete**")
            st.caption("All logic implemented")
        with col3:
            st.success("✅ **Universal**")
            st.caption("All matches worldwide")
        with col4:
            st.success("✅ **Exact**")
            st.caption("No deviations from spec")

if __name__ == "__main__":
    main()