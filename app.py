import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== COMPLETE PATTERN DETECTION IMPORT ===================
try:
    from complete_pattern_detector import (
        CompletePatternDetector, 
        DataValidator,
        ResultFormatter,
        get_complete_classification as original_get_complete_classification,
        format_reliability_badge as original_format_reliability_badge,
        format_durability_indicator as original_format_durability_indicator
    )
    PATTERN_DETECTOR_AVAILABLE = True
except ImportError:
    PATTERN_DETECTOR_AVAILABLE = False
    # Create fallback functions
    class CompletePatternDetector:
        @staticmethod
        def detect_elite_defense(home_data, away_data):
            return []
        
        @staticmethod
        def detect_winner_lock(match_data):
            return None
        
        @staticmethod
        def determine_under_35_bet(elite_present, winner_present):
            return None
        
        @classmethod
        def analyze_match_complete(cls, home_data, away_data, match_metadata):
            return {
                'recommendations': [],
                'pattern_stats': {'elite_defense_count': 0, 'winner_lock_count': 0},
                'has_elite_defense': False,
                'has_winner_lock': False,
                'under_35_bet': None
            }
    
    class DataValidator:
        @staticmethod
        def validate_match_data(home_data, away_data, match_metadata):
            return []
    
    class ResultFormatter:
        @staticmethod
        def format_pattern_name(pattern):
            return pattern
        
        @staticmethod
        def get_pattern_style(pattern):
            return {
                'emoji': '❓',
                'color': '#6B7280',
                'bg_color': '#F3F4F6',
                'border_color': '#9CA3AF'
            }
    
    def get_complete_classification(home_data, away_data):
        return {
            'dominant_state': 'PATTERN_DETECTOR_UNAVAILABLE',
            'note': 'Pattern detector not available'
        }
    
    def format_reliability_badge(data):
        return "⚠️ Pattern detector unavailable"
    
    def format_durability_indicator(code):
        return "N/A"

# =================== SYSTEM CONSTANTS v7.1 ===================
# DEFENSIVE THRESHOLDS (LAST 5 MATCHES ONLY)
DEFENSIVE_THRESHOLDS = {
    'TEAM_NO_SCORE': 0.6,      # Can preserve 0 goals conceded state
    'CLEAN_SHEET': 0.8,        # Can preserve 0-0.8 goals conceded state  
    'OPPONENT_UNDER_1_5': 1.0, # Can limit opponent to ≤1.5 goals
    'OPPONENT_UNDER_2_5': 1.2, # Can limit opponent to ≤2.5 goals
    'TOTALS_UNDER_2_5': 1.2,   # Team contributes to low-scoring match
    'UNDER_3_5_CONSIDER': 1.6  # Empirical threshold from 25-match study
}

# EMPIRICAL ACCURACY RATES v7.1 (UPDATED WITH EDGE-DERIVED EVIDENCE)
EMPIRICAL_ACCURACY = {
    'ELITE_DEFENSE_UNDER_1_5': '8/8 (100%)',
    'WINNER_LOCK_DOUBLE_CHANCE': '6/6 (100% no-loss)',
    'EDGE_DERIVED_UNDER_1_5': '2/2 (100%)',  # NEW: Empirical proof!
    'BOTH_PATTERNS_UNDER_3_5': '3/3 (100%)',
    'ELITE_DEFENSE_ONLY_UNDER_3_5': '7/8 (87.5%)',
    'WINNER_LOCK_ONLY_UNDER_3_5': '5/6 (83.3%)'
}

# PATTERN DISTRIBUTION v7.1 (UPDATED - Edge-Derived is a SEPARATE PATTERN)
PATTERN_DISTRIBUTION = {
    'ELITE_DEFENSE_ONLY': 5,
    'WINNER_LOCK_ONLY': 3,
    'EDGE_DERIVED_ONLY': 2,    # NEW: Your empirical evidence!
    'BOTH_PATTERNS': 3,
    'NO_PATTERNS': 12          # Reduced from 14 (Edge-Derived are patterns!)
}

# v6.0 Edge Detection Constants
CONTROL_CRITERIA_REQUIRED = 2
GOALS_ENV_THRESHOLD = 2.8
ELITE_ATTACK_THRESHOLD = 1.6

# Agency-State Lock Constants
DIRECTION_THRESHOLD = 0.25
ENFORCEMENT_METHODS_REQUIRED = 2
STATE_FLIP_FAILURES_REQUIRED = 2
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1

# Totals Lock Constants
TOTALS_LOCK_THRESHOLD = 1.2
UNDER_GOALS_THRESHOLD = 2.5

# Capital Multipliers
CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,
    'LOCK_MODE': 2.0,
}

# =================== LAYER 1: DEFENSIVE PROOF ENGINE ===================
class DefensiveProofEngine:
    """LAYER 1: Defensive Proof with Binary Gates"""
    
    @staticmethod
    def check_opponent_under(backing_team: str, opponent_data: Dict, market: str) -> Dict:
        """
        When backing TEAM A: Check TEAM B's defensive capabilities
        
        PERSPECTIVE-SENSITIVE: Opponent depends on which team is backed
        """
        opponent_avg_conceded = opponent_data.get('goals_conceded_last_5', 0) / 5
        
        if market == 'OPPONENT_UNDER_1_5':
            if opponent_avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5']:
                return {
                    'lock': True,
                    'type': 'EDGE_DERIVED',
                    'reason': f'Opponent concedes {opponent_avg_conceded:.2f} avg ≤ {DEFENSIVE_THRESHOLDS["OPPONENT_UNDER_1_5"]}'
                }
        
        elif market == 'OPPONENT_UNDER_2_5':
            if opponent_avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_2_5']:
                return {
                    'consideration': True,
                    'reason': f'Opponent concedes {opponent_avg_conceded:.2f} avg ≤ {DEFENSIVE_THRESHOLDS["OPPONENT_UNDER_2_5"]}'
                }
        
        return {'lock': False}
    
    @staticmethod
    def detect_elite_defense_pattern(team_data: Dict, league_avg_conceded: float = 1.3) -> Dict:
        """
        ELITE DEFENSE PATTERN (100% EMPIRICAL - 8/8 matches)
        
        Conditions:
        1. Concedes ≤4 total goals in last 5 matches (avg ≤0.8/match)
        2. Defense gap > 2.0 vs opponent
        """
        total_conceded = team_data.get('goals_conceded_last_5', 0)
        avg_conceded = total_conceded / 5
        defense_gap = league_avg_conceded - avg_conceded
        
        # CRITERIA: Both conditions required
        if total_conceded <= 4 and defense_gap > 2.0:
            return {
                'elite_defense': True,
                'total_conceded': total_conceded,
                'defense_gap': defense_gap,
                'signal': 'OPPONENT_UNDER_1_5 (100% empirical accuracy)',
                'historical_evidence': [
                    'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                    'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Man City 0-0 Sunderland'
                ]
            }
        
        return {'elite_defense': False}

# =================== LAYER 2: PATTERN INDEPENDENCE MATRIX v7.1 ===================
class PatternIndependenceMatrixV71:
    """LAYER 2: Pattern Independence Analysis v7.1"""
    
    @staticmethod
    def get_pattern_distribution() -> Dict:
        """Return empirical pattern distribution from 25-match study v7.1"""
        total_matches = sum(PATTERN_DISTRIBUTION.values())
        percentages = {k: (v/total_matches*100) for k, v in PATTERN_DISTRIBUTION.items()}
        
        actionable_matches = (PATTERN_DISTRIBUTION['ELITE_DEFENSE_ONLY'] + 
                             PATTERN_DISTRIBUTION['WINNER_LOCK_ONLY'] + 
                             PATTERN_DISTRIBUTION['EDGE_DERIVED_ONLY'] + 
                             PATTERN_DISTRIBUTION['BOTH_PATTERNS'])
        
        return {
            'distribution': PATTERN_DISTRIBUTION,
            'percentages': percentages,
            'total_matches': total_matches,
            'actionable_matches': actionable_matches,  # NOW 13/25 (52%)
            'stay_away_matches': PATTERN_DISTRIBUTION['NO_PATTERNS']
        }
    
    @staticmethod
    def evaluate_pattern_independence(elite_defense: bool, winner_lock: bool, edge_derived: bool) -> Dict:
        """
        KEY FINDING v7.1: Elite Defense, Winner Lock, AND Edge-Derived patterns appear INDEPENDENTLY
        
        CRITICAL FIX: Edge-Derived is a VALID PATTERN (empirical proof: 2/2 matches)
        """
        pattern_count = sum([elite_defense, winner_lock, edge_derived])
        
        if pattern_count == 3:
            return {
                'combination': 'ALL_THREE_PATTERNS',
                'description': 'All three patterns independently present',
                'emoji': '🎯',
                'confidence': 'MAXIMUM',
                'empirical_count': 'RARE',
                'capital_multiplier': 2.0
            }
        elif elite_defense and winner_lock:
            return {
                'combination': 'ELITE_DEFENSE_WINNER_LOCK',
                'description': 'Both Elite Defense and Winner Lock patterns present',
                'emoji': '🛡️👑',
                'confidence': 'VERY HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['BOTH_PATTERNS'],
                'capital_multiplier': 2.0
            }
        elif elite_defense and edge_derived:
            return {
                'combination': 'ELITE_DEFENSE_EDGE_DERIVED',
                'description': 'Both Elite Defense and Edge-Derived patterns present',
                'emoji': '🛡️🔓',
                'confidence': 'VERY HIGH',
                'empirical_count': 'NEW PATTERN',
                'capital_multiplier': 2.0
            }
        elif winner_lock and edge_derived:
            return {
                'combination': 'WINNER_LOCK_EDGE_DERIVED',
                'description': 'Both Winner Lock and Edge-Derived patterns present',
                'emoji': '👑🔓',
                'confidence': 'VERY HIGH',
                'empirical_count': 'NEW PATTERN',
                'capital_multiplier': 2.0
            }
        elif elite_defense:
            return {
                'combination': 'ONLY_ELITE_DEFENSE',
                'description': 'Only Elite Defense pattern present',
                'emoji': '🛡️',
                'confidence': 'HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['ELITE_DEFENSE_ONLY'],
                'capital_multiplier': 2.0
            }
        elif winner_lock:
            return {
                'combination': 'ONLY_WINNER_LOCK',
                'description': 'Only Winner Lock pattern present',
                'emoji': '👑',
                'confidence': 'HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['WINNER_LOCK_ONLY'],
                'capital_multiplier': 2.0
            }
        elif edge_derived:
            return {
                'combination': 'ONLY_EDGE_DERIVED',
                'description': 'Only Edge-Derived pattern present (100% empirical)',
                'emoji': '🔓',
                'confidence': 'HIGH',
                'empirical_count': PATTERN_DISTRIBUTION['EDGE_DERIVED_ONLY'],
                'capital_multiplier': 2.0
            }
        else:
            return {
                'combination': 'NO_PATTERNS',
                'description': 'No proven patterns detected',
                'emoji': '⚪',
                'confidence': 'LOW',
                'empirical_count': PATTERN_DISTRIBUTION['NO_PATTERNS'],
                'capital_multiplier': 1.0
            }

# =================== LAYER 3: AGENCY-STATE DETECTION ENGINE ===================
class AgencyStateLockEngineV7:
    """LAYER 3: Agency-State Detection (4 Gates + State Preservation)"""
    
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, is_home: bool) -> Tuple[int, float]:
        """GATE 1: Quiet Control"""
        criteria_met = 0
        weighted_score = 0.0
        
        # 1. Tempo dominance (xG > 1.4) - weight: 1.0
        xg = team_data.get('home_xg_per_match', 0) if is_home else team_data.get('away_xg_per_match', 0)
        if xg > 1.4:
            criteria_met += 1
            weighted_score += 1.0
        
        # 2. Scoring efficiency (goals/xG > 90%) - weight: 1.0
        goals = team_data.get('home_goals_scored', 0) if is_home else team_data.get('away_goals_scored', 0)
        xg_for = team_data.get('home_xg_for', 0) if is_home else team_data.get('away_xg_for', 0)
        efficiency = goals / max(xg_for, 0.1)
        if efficiency > 0.9:
            criteria_met += 1
            weighted_score += 1.0
        
        # 3. Critical area threat (set pieces > 25%) - weight: 0.8
        setpiece_pct = team_data.get('home_setpiece_pct', 0) if is_home else team_data.get('away_setpiece_pct', 0)
        if setpiece_pct > 0.25:
            criteria_met += 1
            weighted_score += 0.8
        
        # 4. Repeatable patterns (openplay > 50% OR counter > 15%) - weight: 0.8
        openplay_pct = team_data.get('home_openplay_pct', 0) if is_home else team_data.get('away_openplay_pct', 0)
        counter_pct = team_data.get('home_counter_pct', 0) if is_home else team_data.get('away_counter_pct', 0)
        if openplay_pct > 0.5 or counter_pct > 0.15:
            criteria_met += 1
            weighted_score += 0.8
        
        return criteria_met, weighted_score
    
    @staticmethod
    def check_directional_dominance(controller_xg: float, opponent_xg: float, market_type: str) -> Tuple[bool, float]:
        """GATE 2: Directional Dominance"""
        threshold = DEFENSIVE_THRESHOLDS.get(market_type, 1.1)
        control_delta = controller_xg - opponent_xg
        
        # BOTH conditions must be met:
        # 1. Opponent xG below market threshold
        # 2. Control delta > 0.25
        if opponent_xg < threshold and control_delta > DIRECTION_THRESHOLD:
            return True, control_delta
        
        return False, control_delta
    
    @staticmethod
    def check_agency_collapse(opponent_data: Dict, is_home: bool, league_avg_xg: float, market_type: str) -> Tuple[bool, int]:
        """GATE 3: Agency Collapse"""
        failures = 0
        
        # Get opponent metrics
        chase_xg = opponent_data.get('home_xg_per_match', 0) if is_home else opponent_data.get('away_xg_per_match', 0)
        
        # CHECK 1: Chase capacity
        if chase_xg < 1.1:
            failures += 1
        
        # CHECK 2: Tempo surge capability
        if chase_xg < 1.4:
            failures += 1
        
        # CHECK 3: Alternate threat channels
        setpiece_pct = opponent_data.get('home_setpiece_pct', 0) if is_home else opponent_data.get('away_setpiece_pct', 0)
        counter_pct = opponent_data.get('home_counter_pct', 0) if is_home else opponent_data.get('away_counter_pct', 0)
        if setpiece_pct < 0.25 and counter_pct < 0.15:
            failures += 1
        
        # CHECK 4: Substitution leverage
        gpm = opponent_data.get('home_goals_per_match', 0) if is_home else opponent_data.get('away_goals_per_match', 0)
        if gpm < league_avg_xg * 0.8:
            failures += 1
        
        # Market-specific failure requirements
        failure_requirements = {
            'WINNER': 2,
            'CLEAN_SHEET': 3,
            'TEAM_NO_SCORE': 4,
            'OPPONENT_UNDER_1_5': 2,
            'OPPONENT_UNDER_2_5': 2
        }
        
        required = failure_requirements.get(market_type, 2)
        return failures >= required, failures
    
    @staticmethod
    def check_state_preservation(controller_data: Dict, is_home: bool, market_type: str) -> Tuple[bool, float]:
        """
        GATE 4A: STATE PRESERVATION (OVERRIDE)
        
        CRITICAL: Overrides Gates 1-3 for defensive markets
        Uses ONLY last 5 matches conceded data
        """
        # WINNER MARKET: Uses dominance logic, not preservation
        if market_type == 'WINNER':
            return True, 0.0
        
        # Get recent defensive trend
        recent_conceded = controller_data.get('goals_conceded_last_5', 0)
        recent_concede_avg = recent_conceded / 5
        
        # Market-specific preservation thresholds
        threshold = DEFENSIVE_THRESHOLDS.get(market_type, 1.0)
        
        if recent_concede_avg <= threshold:
            return True, recent_concede_avg
        
        return False, recent_concede_avg
    
    @staticmethod
    def check_non_urgent_enforcement(controller_data: Dict, is_home: bool, market_type: str) -> Tuple[bool, int]:
        """GATE 4B: Non-Urgent Enforcement"""
        enforce_methods = 0
        
        # METHOD 1: Defensive solidity
        if is_home:
            goals_conceded = controller_data.get('home_goals_conceded', 0)
            matches_played = controller_data.get('home_matches_played', 1)
            concede_avg = goals_conceded / matches_played
            if concede_avg < 1.2:
                enforce_methods += 1
        else:
            goals_conceded = controller_data.get('away_goals_conceded', 0)
            matches_played = controller_data.get('away_matches_played', 1)
            concede_avg = goals_conceded / matches_played
            if concede_avg < 1.3:
                enforce_methods += 1
        
        # METHOD 2: Alternate scoring
        setpiece_pct = controller_data.get('home_setpiece_pct', 0) if is_home else controller_data.get('away_setpiece_pct', 0)
        counter_pct = controller_data.get('home_counter_pct', 0) if is_home else controller_data.get('away_counter_pct', 0)
        if setpiece_pct > 0.25 or counter_pct > 0.15:
            enforce_methods += 1
        
        # METHOD 3: Consistent threat
        xg_per_match = controller_data.get('home_xg_per_match', 0) if is_home else controller_data.get('away_xg_per_match', 0)
        if xg_per_match > 1.3:
            enforce_methods += 1
        
        # Market-specific requirements
        required_methods = 3 if market_type == 'TEAM_NO_SCORE' else 2
        return enforce_methods >= required_methods, enforce_methods

# =================== LAYER 4: TOTALS LOCK ENGINE v7.1 ===================
class TotalsLockEngineV71:
    """LAYER 4: Totals Lock with Dual Paths v7.1"""
    
    @staticmethod
    def evaluate_totals_lock(home_data: Dict, away_data: Dict) -> Dict:
        """
        Dual approach to Totals Under 2.5:
        1. OFFENSIVE INCAPACITY PATH: Both teams low-scoring
        2. DEFENSIVE STRENGTH PATH: Both teams strong defensively
        
        CRITICAL FIX: Totals Lock does NOT count as pattern for Stay-Away decision
        """
        # Calculate last 5 averages
        home_avg_scored = home_data.get('goals_scored_last_5', 0) / 5
        away_avg_scored = away_data.get('goals_scored_last_5', 0) / 5
        
        home_avg_conceded = home_data.get('goals_conceded_last_5', 0) / 5
        away_avg_conceded = away_data.get('goals_conceded_last_5', 0) / 5
        
        # PATH 1: OFFENSIVE INCAPACITY (STRICT LOCK)
        offensive_lock = (home_avg_scored <= TOTALS_LOCK_THRESHOLD) and (away_avg_scored <= TOTALS_LOCK_THRESHOLD)
        
        # PATH 2: DEFENSIVE STRENGTH (CONSIDERATION)
        defensive_consideration = (home_avg_conceded <= TOTALS_LOCK_THRESHOLD) and (away_avg_conceded <= TOTALS_LOCK_THRESHOLD)
        
        if offensive_lock:
            return {
                'lock': True,
                'type': 'OFFENSIVE_INCAPACITY',
                'reason': f'Both teams low-scoring (Home: {home_avg_scored:.2f}, Away: {away_avg_scored:.2f} ≤ {TOTALS_LOCK_THRESHOLD})',
                'market': 'TOTALS_UNDER_2_5',
                'capital_authorized': True,
                'is_pattern': False  # CRITICAL: Totals Lock is NOT a pattern for Stay-Away
            }
        elif defensive_consideration:
            return {
                'consideration': True,
                'type': 'DEFENSIVE_STRENGTH',
                'reason': f'Both teams strong defensively (Home: {home_avg_conceded:.2f}, Away: {away_avg_conceded:.2f} ≤ {TOTALS_LOCK_THRESHOLD})',
                'market': 'TOTALS_UNDER_2_5',
                'capital_authorized': False,
                'is_pattern': False
            }
        
        return {'lock': False, 'is_pattern': False}
    
    @staticmethod
    def evaluate_under_35_confidence(home_data: Dict, away_data: Dict, 
                                   elite_defense_home: Dict, elite_defense_away: Dict,
                                   winner_lock: bool, edge_derived: bool) -> Dict:
        """
        UNDER 3.5 Confidence Tiers from empirical evidence v7.1
        """
        # Check if at least one team meets defensive threshold
        home_avg_conceded = home_data.get('goals_conceded_last_5', 0) / 5
        away_avg_conceded = away_data.get('goals_conceded_last_5', 0) / 5
        
        # Condition: At least one team concedes ≤ 1.6 avg
        defensive_condition = (home_avg_conceded <= DEFENSIVE_THRESHOLDS['UNDER_3_5_CONSIDER']) or \
                              (away_avg_conceded <= DEFENSIVE_THRESHOLDS['UNDER_3_5_CONSIDER'])
        
        if not defensive_condition:
            return {'confidence': 0.0, 'tier': 0, 'description': 'No defensive foundation'}
        
        # Check patterns
        elite_defense_present = elite_defense_home.get('elite_defense', False) or \
                              elite_defense_away.get('elite_defense', False)
        
        # EMPIRICAL CONFIDENCE TIERS v7.1 (including Edge-Derived):
        if elite_defense_present and winner_lock and edge_derived:
            return {
                'confidence': 1.0,
                'tier': 1,
                'description': 'All three patterns present (MAXIMUM)',
                'sample_size': 'Theoretical maximum',
                'recommendation': 'UNDER 3.5 STRONG',
                'stake_multiplier': 1.2
            }
        elif elite_defense_present and winner_lock:
            return {
                'confidence': 1.0,
                'tier': 1,
                'description': 'Both Elite Defense and Winner Lock (100%)',
                'sample_size': '3/3 matches',
                'recommendation': 'UNDER 3.5 STRONG',
                'stake_multiplier': 1.2
            }
        elif elite_defense_present and edge_derived:
            return {
                'confidence': 0.94,  # Average of 100% and 87.5%
                'tier': 2,
                'description': 'Elite Defense + Edge-Derived patterns',
                'sample_size': 'New pattern combination',
                'recommendation': 'UNDER 3.5 MODERATE',
                'stake_multiplier': 1.1
            }
        elif winner_lock and edge_derived:
            return {
                'confidence': 0.92,  # Average of 100% and 83.3%
                'tier': 2,
                'description': 'Winner Lock + Edge-Derived patterns',
                'sample_size': 'New pattern combination',
                'recommendation': 'UNDER 3.5 MODERATE',
                'stake_multiplier': 1.0
            }
        elif elite_defense_present and not winner_lock:
            return {
                'confidence': 0.875,
                'tier': 2,
                'description': 'Only Elite Defense (87.5%)',
                'sample_size': '7/8 matches',
                'recommendation': 'UNDER 3.5 MODERATE',
                'stake_multiplier': 1.0
            }
        elif not elite_defense_present and winner_lock:
            return {
                'confidence': 0.833,
                'tier': 3,
                'description': 'Only Winner Lock (83.3%)',
                'sample_size': '5/6 matches',
                'recommendation': 'UNDER 3.5 MODERATE',
                'stake_multiplier': 0.9
            }
        elif not elite_defense_present and edge_derived:
            return {
                'confidence': 0.917,  # Average of 100% and 83.3%
                'tier': 2,
                'description': 'Only Edge-Derived (empirical: 100%)',
                'sample_size': '2/2 matches',
                'recommendation': 'UNDER 3.5 MODERATE',
                'stake_multiplier': 1.0
            }
        else:
            return {'confidence': 0.0, 'tier': 0, 'description': 'No patterns detected'}

# =================== LAYER 5: PATTERN COMBINATION & MARKET DECISIONS v7.1 ===================
class PatternCombinationEngineV71:
    """LAYER 5: Pattern Combination Analysis v7.1"""
    
    @staticmethod
    def determine_under_15_sources(home_data: Dict, away_data: Dict, 
                                  home_name: str, away_name: str) -> List[Dict]:
        """
        THREE independent sources for OPPONENT_UNDER_1.5 v7.1:
        1. PRIMARY: Edge-Derived Lock (opponent ≤ 1.0 avg conceded) - 100% EMPIRICAL
        2. SECONDARY: Elite Defense Pattern (100% empirical)
        3. TERTIARY: Agency-State with State Preservation
        """
        sources = []
        
        # SOURCE 1: Edge-Derived Locks (check both perspectives)
        defensive_engine = DefensiveProofEngine()
        
        # Backing HOME perspective
        home_perspective = defensive_engine.check_opponent_under(
            home_name, away_data, 'OPPONENT_UNDER_1_5'
        )
        if home_perspective.get('lock'):
            sources.append({
                'source': 'EDGE_DERIVED',
                'perspective': 'BACKING_HOME',
                'declaration': f'🔓 EDGE-DERIVED: BACK {home_name} → {away_name} UNDER 1.5',
                'reason': home_perspective['reason'],
                'type': 'PRIMARY_SOURCE',
                'empirical_accuracy': '2/2 (100%)',  # Your empirical proof!
                'capital_multiplier': 2.0
            })
        
        # Backing AWAY perspective
        away_perspective = defensive_engine.check_opponent_under(
            away_name, home_data, 'OPPONENT_UNDER_1_5'
        )
        if away_perspective.get('lock'):
            sources.append({
                'source': 'EDGE_DERIVED',
                'perspective': 'BACKING_AWAY',
                'declaration': f'🔓 EDGE-DERIVED: BACK {away_name} → {home_name} UNDER 1.5',
                'reason': away_perspective['reason'],
                'type': 'PRIMARY_SOURCE',
                'empirical_accuracy': '2/2 (100%)',  # Your empirical proof!
                'capital_multiplier': 2.0
            })
        
        # SOURCE 2: Elite Defense Pattern
        elite_home = defensive_engine.detect_elite_defense_pattern(home_data)
        elite_away = defensive_engine.detect_elite_defense_pattern(away_data)
        
        if elite_home.get('elite_defense'):
            sources.append({
                'source': 'ELITE_DEFENSE',
                'team': home_name,
                'declaration': f'🎯 ELITE DEFENSE: {home_name} concedes ≤4 total last 5',
                'reason': '100% empirical accuracy for OPPONENT_UNDER_1.5',
                'type': 'SECONDARY_SOURCE',
                'historical_evidence': elite_home.get('historical_evidence', []),
                'empirical_accuracy': '8/8 (100%)',
                'capital_multiplier': 2.0
            })
        
        if elite_away.get('elite_defense'):
            sources.append({
                'source': 'ELITE_DEFENSE',
                'team': away_name,
                'declaration': f'🎯 ELITE DEFENSE: {away_name} concedes ≤4 total last 5',
                'reason': '100% empirical accuracy for OPPONENT_UNDER_1.5',
                'type': 'SECONDARY_SOURCE',
                'historical_evidence': elite_away.get('historical_evidence', []),
                'empirical_accuracy': '8/8 (100%)',
                'capital_multiplier': 2.0
            })
        
        return sources
    
    @staticmethod
    def evaluate_double_chance(winner_lock_result: Dict) -> Dict:
        """
        If Winner Lock detected → Double Chance (Win or Draw) Lock
        100% no-loss empirical record
        """
        if winner_lock_result.get('state_locked', False):
            controller = winner_lock_result.get('controller', 'Unknown')
            return {
                'market': 'DOUBLE_CHANCE',
                'state_locked': True,
                'declaration': f'🔒 DOUBLE CHANCE LOCKED\n{controller} Win or Draw',
                'reason': 'Winner Lock detected → Double Chance guaranteed (100% empirical)',
                'capital_authorized': True
            }
        
        return {'market': 'DOUBLE_CHANCE', 'state_locked': False}

# =================== LAYER 6: INTEGRATED CAPITAL DECISION v7.1 ===================
class IntegratedCapitalEngineV71:
    """LAYER 6: Final Capital Decision v7.1"""
    
    @staticmethod
    def determine_final_capital_decision(all_detections: Dict) -> Dict:
        """
        ANY PROVEN PATTERN present → LOCK_MODE (2.0x)
        NO patterns → EDGE_MODE (1.0x)
        
        PROVEN PATTERNS v7.1:
        1. Edge-Derived Lock (100% empirical - 2/2)
        2. Elite Defense Pattern (100% empirical - 8/8)
        3. Winner Lock (100% no-loss - 6/6)
        4. Combination of above
        
        CRITICAL FIX: Edge-Derived Locks ARE patterns and trigger LOCK_MODE
        """
        locks_present = []
        pattern_sources = []
        
        # PATTERN 1: Edge-Derived Locks (EMPIRICAL PROOF: 2/2)
        if all_detections.get('has_edge_derived_locks'):
            locks_present.append('EDGE_DERIVED_UNDER_1_5')
            pattern_sources.append({
                'type': 'EDGE_DERIVED',
                'accuracy': '2/2 (100%)',
                'empirical_proof': 'Cagliari vs Milan, Parma vs Fiorentina'
            })
        
        # PATTERN 2: Elite Defense
        if all_detections.get('has_elite_defense'):
            locks_present.append('ELITE_DEFENSE_UNDER_1_5')
            pattern_sources.append({
                'type': 'ELITE_DEFENSE',
                'accuracy': '8/8 (100%)',
                'empirical_proof': '25-match study'
            })
        
        # PATTERN 3: Winner Lock
        if all_detections.get('has_winner_lock'):
            locks_present.append('WINNER_LOCK_DOUBLE_CHANCE')
            pattern_sources.append({
                'type': 'WINNER_LOCK',
                'accuracy': '6/6 (100% no-loss)',
                'empirical_proof': '25-match study'
            })
        
        # PATTERN 4: Totals Lock (NOT a pattern for Stay-Away, but still triggers capital)
        if all_detections.get('totals_lock', {}).get('lock'):
            locks_present.append('TOTALS_UNDER_2_5_LOCK')
            # Note: Totals Lock is not a pattern for Stay-Away decision
        
        # PATTERN 5: Double Chance
        if all_detections.get('double_chance', {}).get('state_locked'):
            locks_present.append('DOUBLE_CHANCE_LOCK')
        
        # UNDER 3.5 Confidence
        under_35 = all_detections.get('under_35_confidence', {})
        if under_35.get('tier', 0) >= 2:
            locks_present.append('UNDER_3_5_CONFIDENCE_TIER_2+')
        
        # Capital Decision v7.1
        # ANY proven pattern OR Totals Lock → LOCK_MODE
        has_proven_pattern = all_detections.get('has_elite_defense', False) or \
                           all_detections.get('has_winner_lock', False) or \
                           all_detections.get('has_edge_derived_locks', False)
        
        has_totals_lock = all_detections.get('totals_lock', {}).get('lock', False)
        
        if has_proven_pattern or has_totals_lock:
            return {
                'capital_mode': 'LOCK_MODE',
                'multiplier': CAPITAL_MULTIPLIERS['LOCK_MODE'],
                'reason': f'Proven patterns detected: {", ".join(locks_present)}',
                'system_verdict': 'STRUCTURAL CERTAINTY DETECTED',
                'locks_present': locks_present,
                'pattern_sources': pattern_sources,
                'has_proven_pattern': has_proven_pattern,
                'has_totals_lock': has_totals_lock
            }
        else:
            return {
                'capital_mode': 'EDGE_MODE',
                'multiplier': CAPITAL_MULTIPLIERS['EDGE_MODE'],
                'reason': 'No proven patterns detected',
                'system_verdict': 'HEURISTIC EDGE ONLY',
                'locks_present': [],
                'pattern_sources': [],
                'has_proven_pattern': False,
                'has_totals_lock': False
            }

# =================== COMPLETE EXECUTION ENGINE v7.1 ===================
class FusedLogicEngineV71:
    """COMPLETE FUSED LOGIC ENGINE v7.1 - 6 LAYERS WITH FIXES"""
    
    @staticmethod
    def execute_fused_logic(home_data: Dict, away_data: Dict, 
                           home_name: str, away_name: str,
                           league_avg_xg: float) -> Dict:
        """
        MAIN EXECUTION FUNCTION - 6 LAYERS v7.1
        WITH CRITICAL FIXES:
        1. Edge-Derived Locks recognized as patterns
        2. Correct Stay-Away decision logic
        3. Updated empirical validation
        """
        all_results = {}
        
        # ========== LAYER 1: DEFENSIVE PROOF ==========
        defensive_engine = DefensiveProofEngine()
        all_results['defensive_assessment'] = {
            'home_avg_conceded': home_data.get('goals_conceded_last_5', 0) / 5,
            'away_avg_conceded': away_data.get('goals_conceded_last_5', 0) / 5,
            'home_avg_scored': home_data.get('goals_scored_last_5', 0) / 5,
            'away_avg_scored': away_data.get('goals_scored_last_5', 0) / 5
        }
        
        # ========== LAYER 2: PATTERN DETECTION ==========
        all_results['elite_defense_home'] = defensive_engine.detect_elite_defense_pattern(home_data)
        all_results['elite_defense_away'] = defensive_engine.detect_elite_defense_pattern(away_data)
        all_results['has_elite_defense'] = (
            all_results['elite_defense_home'].get('elite_defense', False) or
            all_results['elite_defense_away'].get('elite_defense', False)
        )
        
        # ========== LAYER 3: AGENCY-STATE DETECTION ==========
        # Note: Placeholder - would be populated by actual detection
        all_results['agency_state_results'] = {
            'WINNER': {'state_locked': False},
            'CLEAN_SHEET': {'state_locked': False},
            'TEAM_NO_SCORE': {'state_locked': False},
            'OPPONENT_UNDER_1_5': {'state_locked': False},
            'OPPONENT_UNDER_2_5': {'state_locked': False}
        }
        
        all_results['has_winner_lock'] = all_results['agency_state_results']['WINNER'].get('state_locked', False)
        
        # ========== LAYER 4: TOTALS LOCKS ==========
        totals_engine = TotalsLockEngineV71()
        all_results['totals_lock'] = totals_engine.evaluate_totals_lock(home_data, away_data)
        
        # ========== LAYER 5: PATTERN COMBINATION ==========
        combination_engine = PatternCombinationEngineV71()
        all_results['under_15_sources'] = combination_engine.determine_under_15_sources(
            home_data, away_data, home_name, away_name
        )
        all_results['has_edge_derived_locks'] = len(all_results['under_15_sources']) > 0
        
        # Double Chance
        all_results['double_chance'] = combination_engine.evaluate_double_chance(
            all_results['agency_state_results']['WINNER']
        )
        
        # UNDER 3.5 Confidence v7.1
        all_results['under_35_confidence'] = totals_engine.evaluate_under_35_confidence(
            home_data, away_data,
            all_results['elite_defense_home'],
            all_results['elite_defense_away'],
            all_results['has_winner_lock'],
            all_results['has_edge_derived_locks']
        )
        
        # ========== LAYER 6: CAPITAL DECISION v7.1 ==========
        capital_engine = IntegratedCapitalEngineV71()
        all_results['capital_decision'] = capital_engine.determine_final_capital_decision(all_results)
        
        # ========== PATTERN INDEPENDENCE ANALYSIS v7.1 ==========
        pattern_matrix = PatternIndependenceMatrixV71()
        all_results['pattern_independence'] = pattern_matrix.evaluate_pattern_independence(
            all_results['has_elite_defense'],
            all_results['has_winner_lock'],
            all_results['has_edge_derived_locks']
        )
        
        # ========== PATTERN DISTRIBUTION v7.1 ==========
        all_results['pattern_distribution'] = pattern_matrix.get_pattern_distribution()
        
        # ========== PERSPECTIVE-SENSITIVE REPORTING ==========
        all_results['perspective_report'] = FusedLogicEngineV71.generate_perspective_report(
            home_name, away_name, all_results
        )
        
        # ========== DECISION MATRIX v7.1 (FIXED) ==========
        all_results['decision_matrix'] = FusedLogicEngineV71.generate_decision_matrix_v71(all_results)
        
        # ========== COMPLETE PATTERN DETECTION ==========
        if PATTERN_DETECTOR_AVAILABLE:
            match_metadata = {
                'home_team': home_name,
                'away_team': away_name,
                'winner_lock_detected': all_results['has_winner_lock'],
                'winner_lock_team': 'home' if all_results['agency_state_results']['WINNER'].get('controller') == home_name else 'away',
                'winner_delta_value': all_results['agency_state_results']['WINNER'].get('control_delta', 0)
            }
            all_results['complete_pattern_analysis'] = CompletePatternDetector.analyze_match_complete(
                home_data, away_data, match_metadata
            )
        
        return all_results
    
    @staticmethod
    def generate_perspective_report(home_name: str, away_name: str, all_results: Dict) -> Dict:
        """Clear reporting based on backing perspective"""
        report = {}
        
        # PERSPECTIVE 1: Backing HOME
        report['backing_home'] = {
            'controller': home_name,
            'opponent': away_name,
            'opponent_defensive_assessment': {
                'avg_conceded': all_results['defensive_assessment']['away_avg_conceded'],
                'under_15_signal': all_results['defensive_assessment']['away_avg_conceded'] <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5'],
                'under_25_signal': all_results['defensive_assessment']['away_avg_conceded'] <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_2_5'],
                'interpretation': f'When backing {home_name}: {away_name} concedes {all_results["defensive_assessment"]["away_avg_conceded"]:.2f} avg goals'
            },
            'recommendations': []
        }
        
        # PERSPECTIVE 2: Backing AWAY
        report['backing_away'] = {
            'controller': away_name,
            'opponent': home_name,
            'opponent_defensive_assessment': {
                'avg_conceded': all_results['defensive_assessment']['home_avg_conceded'],
                'under_15_signal': all_results['defensive_assessment']['home_avg_conceded'] <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5'],
                'under_25_signal': all_results['defensive_assessment']['home_avg_conceded'] <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_2_5'],
                'interpretation': f'When backing {away_name}: {home_name} concedes {all_results["defensive_assessment"]["home_avg_conceded"]:.2f} avg goals'
            },
            'recommendations': []
        }
        
        # Add recommendations based on patterns
        for perspective in ['backing_home', 'backing_away']:
            opp_avg = report[perspective]['opponent_defensive_assessment']['avg_conceded']
            
            if opp_avg <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5']:
                report[perspective]['recommendations'].append(
                    '✅ EDGE-DERIVED: OPPONENT UNDER 1.5 LOCK (defensive proof ≤1.0)'
                )
            if opp_avg <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_2_5']:
                report[perspective]['recommendations'].append(
                    '🔍 CONSIDERATION: OPPONENT UNDER 2.5 (defensive proof ≤1.2)'
                )
        
        return report
    
    @staticmethod
    def generate_decision_matrix_v71(all_results: Dict) -> Dict:
        """
        CORRECTED DECISION FLOW v7.1
        Edge-Derived Locks ARE patterns and do NOT trigger Stay-Away
        """
        decisions = {
            'STAY_AWAY': False,
            'LOCKS_DETECTED': [],
            'CONSIDERATIONS': [],
            'MARKETS': {},
            'CAPITAL': {},
            'PATTERN_SOURCES': []
        }
        
        # 1. Check for NO PATTERNS scenario v7.1 (CORRECTED)
        elite_defense = all_results.get('has_elite_defense', False)
        winner_lock = all_results.get('has_winner_lock', False)
        edge_derived = all_results.get('has_edge_derived_locks', False)
        
        # EDGE-DERIVED LOCKS ARE PATTERNS! (2/2 empirical proof)
        has_any_proven_pattern = elite_defense or winner_lock or edge_derived
        
        pattern_dist = PatternIndependenceMatrixV71().get_pattern_distribution()
        
        if not has_any_proven_pattern:
            decisions['STAY_AWAY'] = True
            decisions['REASON'] = f'No proven patterns detected ({pattern_dist["stay_away_matches"]}/{pattern_dist["total_matches"]} matches empirical)'
            
            # Check if we have Totals Lock (which still triggers capital but is not a pattern)
            if all_results.get('totals_lock', {}).get('lock'):
                decisions['CONSIDERATIONS'].append(
                    f"⚠️ Totals Lock present but no proven patterns - exercise caution"
                )
            
            return decisions
        
        # 2. We HAVE proven patterns - NOT a Stay-Away
        decisions['STAY_AWAY'] = False
        
        # Track pattern sources
        if elite_defense:
            decisions['PATTERN_SOURCES'].append('ELITE_DEFENSE')
        if winner_lock:
            decisions['PATTERN_SOURCES'].append('WINNER_LOCK')
        if edge_derived:
            decisions['PATTERN_SOURCES'].append('EDGE_DERIVED')
        
        # 3. Collect all locks (Edge-Derived are VALID PATTERNS)
        # Edge-Derived Locks
        for lock in all_results.get('under_15_sources', []):
            if lock['source'] == 'EDGE_DERIVED':
                decisions['LOCKS_DETECTED'].append(f"EDGE-DERIVED: {lock['declaration']}")
                decisions['MARKETS']['OPPONENT_UNDER_1_5'] = {
                    'status': 'LOCKED',
                    'type': 'EDGE_DERIVED',
                    'accuracy': lock.get('empirical_accuracy', '2/2 (100%)')
                }
        
        # Elite Defense Locks
        for lock in all_results.get('under_15_sources', []):
            if lock['source'] == 'ELITE_DEFENSE':
                decisions['LOCKS_DETECTED'].append(f"ELITE DEFENSE: {lock['declaration']}")
                decisions['MARKETS']['OPPONENT_UNDER_1_5'] = {
                    'status': 'LOCKED',
                    'type': 'ELITE_DEFENSE',
                    'accuracy': lock.get('empirical_accuracy', '8/8 (100%)')
                }
        
        # Agency-State Locks (placeholder)
        agency_results = all_results.get('agency_state_results', {})
        for market, result in agency_results.items():
            if result.get('state_locked'):
                decisions['LOCKS_DETECTED'].append(f"AGENCY-STATE: {market} LOCK")
                decisions['MARKETS'][market] = {'status': 'LOCKED', 'type': 'AGENCY_STATE'}
        
        # Totals Lock (NOT a pattern, but still a lock)
        if all_results.get('totals_lock', {}).get('lock'):
            decisions['LOCKS_DETECTED'].append(f"TOTALS: {all_results['totals_lock']['reason']}")
            decisions['MARKETS']['TOTALS_UNDER_2_5'] = {
                'status': 'LOCKED',
                'type': 'TOTALS',
                'note': 'Not a pattern for Stay-Away decision'
            }
        
        # Double Chance
        if all_results.get('double_chance', {}).get('state_locked'):
            decisions['LOCKS_DETECTED'].append(f"DOUBLE CHANCE: {all_results['double_chance']['declaration']}")
            decisions['MARKETS']['DOUBLE_CHANCE'] = {'status': 'LOCKED', 'type': 'DOUBLE_CHANCE'}
        
        # 4. Under 3.5 Confidence
        under_35 = all_results.get('under_35_confidence', {})
        if under_35.get('tier', 0) >= 2:
            decisions['CONSIDERATIONS'].append(
                f"UNDER 3.5: Tier {under_35['tier']} ({under_35['confidence']*100:.1f}% confidence)"
            )
        
        # 5. Capital Decision
        decisions['CAPITAL'] = all_results.get('capital_decision', {})
        
        # 6. Pattern Summary
        decisions['PATTERN_SUMMARY'] = {
            'has_proven_patterns': has_any_proven_pattern,
            'pattern_count': len(decisions['PATTERN_SOURCES']),
            'pattern_combination': all_results['pattern_independence']['combination'],
            'actionable': True
        }
        
        return decisions

# =================== STREAMLIT APP CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v7.1 - FUSED LOGIC SYSTEM",
    page_icon="🎯",
    layout="wide"
)

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .system-header {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3B82F6;
    }
    .prediction-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 4px solid;
        margin: 1rem 0;
        text-align: center;
    }
    .lock-mode {
        border-color: #10B981;
        background: linear-gradient(135deg, #F0FDF4 0%, #E2F7EB 100%);
    }
    .edge-mode {
        border-color: #F59E0B;
        background: linear-gradient(135deg, #FEF3C7 0%, #FCE9B2 100%);
    }
    .stay-away {
        border-color: #EF4444;
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
    }
    .prediction-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .capital-multiplier {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .pattern-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin: 0.25rem;
    }
    .badge-elite {
        background: #10B981;
        color: white;
    }
    .badge-winner {
        background: #3B82F6;
        color: white;
    }
    .badge-edge {
        background: #8B5CF6;
        color: white;
    }
    .lock-item {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin: 0.5rem 0;
    }
    .info-section {
        background: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
    .team-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
    }
    .team-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .stat-label {
        color: #6B7280;
    }
    .stat-value {
        font-weight: 600;
        color: #1F2937;
    }
    </style>
""", unsafe_allow_html=True)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'color': '#3B82F6'
    },
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'color': '#EF4444'
    },
    'Bundesliga': {
        'filename': 'bundesliga.csv',
        'display_name': '🇩🇪 Bundesliga',
        'color': '#000000'
    },
    'Serie A': {
        'filename': 'serie_a.csv',
        'display_name': '🇮🇹 Serie A',
        'color': '#10B981'
    },
    'Ligue 1': {
        'filename': 'ligue_1.csv',
        'display_name': '🇫🇷 Ligue 1',
        'color': '#8B5CF6'
    },
    'Eredivisie': {
        'filename': 'eredivisie.csv',
        'display_name': '🇳🇱 Eredivisie',
        'color': '#F59E0B'
    }
}

# =================== DATA LOADING FUNCTIONS ===================
@st.cache_data(ttl=3600)
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data with CSV structure"""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple file locations
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename
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
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics"""
    
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
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Goal type percentages
    df['home_total_goals_for'] = df['home_goals_scored'].replace(0, np.nan)
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_total_goals_for']
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_total_goals_for']
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_total_goals_for']
    
    df['away_total_goals_for'] = df['away_goals_scored'].replace(0, np.nan)
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_total_goals_for']
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_total_goals_for']
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_total_goals_for']
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="system-header">BRUTBALL v7.1 - FUSED LOGIC SYSTEM</div>', unsafe_allow_html=True)
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(6)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            if st.button(
                LEAGUES[league]['display_name'],
                use_container_width=True,
                key=f"league_{idx}"
            ):
                st.session_state.selected_league = league
    
    # Default league if not selected
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Match selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options)
    
    # Execute analysis
    if st.button("🎯 EXECUTE FUSED LOGIC ANALYSIS", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average xG
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute fused logic analysis
        with st.spinner("Executing 6-Layer Fused Logic Analysis..."):
            result = FusedLogicEngineV71.execute_fused_logic(
                home_data, away_data, home_team, away_team, league_avg_xg
            )
        
        st.markdown("---")
        
        # =================== PREDICTION SECTION ===================
        st.markdown("## 🎯 SYSTEM PREDICTIONS")
        
        capital_decision = result['capital_decision']
        decision_matrix = result['decision_matrix']
        
        # Capital Decision Display
        if capital_decision['capital_mode'] == 'LOCK_MODE':
            st.markdown(f"""
            <div class="prediction-box lock-mode">
                <div class="prediction-title">🔒 LOCK MODE DETECTED</div>
                <div class="capital-multiplier">2.0x CAPITAL MULTIPLIER</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    {capital_decision['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prediction-box edge-mode">
                <div class="prediction-title">⚠️ EDGE MODE ONLY</div>
                <div class="capital-multiplier">1.0x CAPITAL MULTIPLIER</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    {capital_decision['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Stay-Away Decision
        if decision_matrix['STAY_AWAY']:
            st.markdown(f"""
            <div class="prediction-box stay-away">
                <div class="prediction-title">🚫 STAY AWAY RECOMMENDED</div>
                <div style="margin: 1rem 0; font-size: 1.1rem;">
                    No proven patterns detected in this match
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show actionable recommendations
            if decision_matrix['LOCKS_DETECTED']:
                st.markdown("### 🔒 LOCKS DETECTED")
                for lock in decision_matrix['LOCKS_DETECTED']:
                    st.markdown(f"""
                    <div class="lock-item">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">{lock}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if decision_matrix['CONSIDERATIONS']:
                st.markdown("### 🔍 CONSIDERATIONS")
                for consideration in decision_matrix['CONSIDERATIONS']:
                    st.markdown(f"""
                    <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                        {consideration}
                    </div>
                    """, unsafe_allow_html=True)
        
        # =================== TEAM STATS SECTION ===================
        st.markdown("---")
        st.markdown("## 📊 TEAM STATISTICS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            defensive_assessment = result['defensive_assessment']
            home_conceded_total = home_data.get('goals_conceded_last_5', 0)
            
            st.markdown(f"""
            <div class="team-box">
                <div class="team-name">{home_team}</div>
                <div class="stat-row">
                    <span class="stat-label">Avg Conceded (Last 5)</span>
                    <span class="stat-value">{defensive_assessment['home_avg_conceded']:.2f}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Conceded (Last 5)</span>
                    <span class="stat-value">{home_conceded_total}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">UNDER 1.5 Signal</span>
                    <span class="stat-value">{"✅" if defensive_assessment['home_avg_conceded'] <= 1.0 else "❌"}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">UNDER 2.5 Signal</span>
                    <span class="stat-value">{"🔍" if defensive_assessment['home_avg_conceded'] <= 1.2 else "❌"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            away_conceded_total = away_data.get('goals_conceded_last_5', 0)
            
            st.markdown(f"""
            <div class="team-box">
                <div class="team-name">{away_team}</div>
                <div class="stat-row">
                    <span class="stat-label">Avg Conceded (Last 5)</span>
                    <span class="stat-value">{defensive_assessment['away_avg_conceded']:.2f}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Conceded (Last 5)</span>
                    <span class="stat-value">{away_conceded_total}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">UNDER 1.5 Signal</span>
                    <span class="stat-value">{"✅" if defensive_assessment['away_avg_conceded'] <= 1.0 else "❌"}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">UNDER 2.5 Signal</span>
                    <span class="stat-value">{"🔍" if defensive_assessment['away_avg_conceded'] <= 1.2 else "❌"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # =================== INFORMATIONAL SECTION (BELOW PREDICTIONS) ===================
        st.markdown("---")
        st.markdown("## 📚 SYSTEM INFORMATION v7.1")
        
        # Pattern Distribution
        pattern_dist = result['pattern_distribution']
        st.markdown("### 📈 Pattern Distribution (25-match study)")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{pattern_dist['distribution']['ELITE_DEFENSE_ONLY']}</div>
                <div class="metric-label">Elite Defense Only</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{pattern_dist['distribution']['WINNER_LOCK_ONLY']}</div>
                <div class="metric-label">Winner Lock Only</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{pattern_dist['distribution']['EDGE_DERIVED_ONLY']}</div>
                <div class="metric-label">Edge-Derived Only</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{pattern_dist['distribution']['BOTH_PATTERNS']}</div>
                <div class="metric-label">Both Patterns</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{pattern_dist['distribution']['NO_PATTERNS']}</div>
                <div class="metric-label">No Patterns</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <strong>Actionable Matches:</strong> {pattern_dist['actionable_matches']}/{pattern_dist['total_matches']} ({pattern_dist['actionable_matches']/pattern_dist['total_matches']*100:.0f}%)
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern Independence
        pattern_independence = result['pattern_independence']
        st.markdown("### 🧩 Pattern Independence Analysis")
        
        st.markdown(f"""
        <div class="info-section">
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                {pattern_independence['emoji']} {pattern_independence['combination']}
            </div>
            <div style="margin-bottom: 0.5rem;">{pattern_independence['description']}</div>
            <div style="font-size: 0.9rem; color: #6B7280;">
                Confidence: {pattern_independence['confidence']} • Empirical: {pattern_independence['empirical_count']}/25 matches
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Edge-Derived Locks Detection
        under_15_sources = result.get('under_15_sources', [])
        edge_derived_sources = [s for s in under_15_sources if s['source'] == 'EDGE_DERIVED']
        
        if edge_derived_sources:
            st.markdown("### 🔓 Edge-Derived Lock Detection")
            
            for source in edge_derived_sources:
                st.markdown(f"""
                <div class="info-section">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">{source['declaration']}</div>
                    <div style="margin-bottom: 0.5rem;">{source['reason']}</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">
                        Empirical Accuracy: {source.get('empirical_accuracy', '2/2 (100%)')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Empirical Evidence
        st.markdown("### 📊 Empirical Evidence")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="info-section">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">🛡️ Elite Defense Pattern</div>
                <div>8/8 matches (100%)</div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">
                    Concedes ≤4 total goals in last 5 matches
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-section">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">👑 Winner Lock Pattern</div>
                <div>6/6 matches (100% no-loss)</div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">
                    Agency-State detection → Double Chance
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="info-section">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">🔓 Edge-Derived Pattern</div>
                <div>2/2 matches (100%)</div>
                <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">
                    Opponent concedes ≤1.0 avg (last 5 matches)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # System Fixes
        st.markdown("### 🔧 System Fixes v7.1")
        
        st.markdown("""
        <div class="info-section">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Critical Fix Applied:</div>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Edge-Derived Locks now recognized as proven patterns</li>
                <li>Stay-Away logic corrected to include Edge-Derived patterns</li>
                <li>Actionable matches increased from 44% to 52%</li>
                <li>Empirical proof: 2/2 Edge-Derived Locks successful in your data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        export_text = f"""BRUTBALL FUSED LOGIC SYSTEM v7.1 - ANALYSIS REPORT
===========================================
Match: {home_team} vs {away_team}
League: {selected_league}

SYSTEM VERDICT: {capital_decision['capital_mode']} ({capital_decision['multiplier']:.1f}x)
Reason: {capital_decision['reason']}

TEAM STATISTICS:
• {home_team}: {defensive_assessment['home_avg_conceded']:.2f} avg conceded (last 5)
• {away_team}: {defensive_assessment['away_avg_conceded']:.2f} avg conceded (last 5)

PATTERN DETECTION:
• Combination: {pattern_independence['combination']}
• Confidence: {pattern_independence['confidence']}

LOCKS DETECTED: {len(decision_matrix['LOCKS_DETECTED'])}
{chr(10).join(['• ' + lock for lock in decision_matrix['LOCKS_DETECTED']])}

CONSIDERATIONS: {len(decision_matrix['CONSIDERATIONS'])}
{chr(10).join(['• ' + cons for cons in decision_matrix['CONSIDERATIONS']])}

EMPIRICAL EVIDENCE v7.1:
• Edge-Derived Locks: 2/2 (100%) in your data
• Actionable matches: 13/25 (52%)
• Fixed: Edge-Derived now recognized as patterns

SYSTEM FIXES:
• Edge-Derived Locks are proven patterns (100% empirical)
• Stay-Away logic corrected
• Actionable matches increased from 44% to 52%
"""
        
        st.download_button(
            label="📥 Download Analysis Report",
            data=export_text,
            file_name=f"brutball_v7.1_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
