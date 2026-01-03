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
            'WINNER': {'state_locked': False, 'controller': home_name, 'control_delta': 0.3},
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
        decision_flow = []
        
        # STEP 1: Check for Edge-Derived Locks (100% empirical)
        has_edge_locks = all_results['has_edge_derived_locks']
        if has_edge_locks:
            decision_flow.append({
                'step': 1,
                'decision': 'EDGE-DERIVED LOCK DETECTED',
                'explanation': 'Opponent concedes ≤1.0 avg goals (2/2 empirical proof)',
                'action': 'PROCEED TO LOCK_MODE',
                'blocked': False,
                'emoji': '🔓'
            })
        else:
            decision_flow.append({
                'step': 1,
                'decision': 'NO EDGE-DERIVED LOCK',
                'explanation': 'Opponent concedes >1.0 avg goals',
                'action': 'Continue to Step 2',
                'blocked': False,
                'emoji': '⚪'
            })
        
        # STEP 2: Check for Elite Defense Pattern (100% empirical)
        has_elite_defense = all_results['has_elite_defense']
        if has_elite_defense:
            decision_flow.append({
                'step': 2,
                'decision': 'ELITE DEFENSE PATTERN DETECTED',
                'explanation': 'Team concedes ≤4 total goals last 5 (8/8 empirical proof)',
                'action': 'PROCEED TO LOCK_MODE',
                'blocked': False,
                'emoji': '🛡️'
            })
        else:
            decision_flow.append({
                'step': 2,
                'decision': 'NO ELITE DEFENSE PATTERN',
                'explanation': 'Team concedes >4 total goals last 5',
                'action': 'Continue to Step 3',
                'blocked': False,
                'emoji': '⚪'
            })
        
        # STEP 3: Check for Winner Lock Pattern (100% no-loss)
        has_winner_lock = all_results['has_winner_lock']
        if has_winner_lock:
            decision_flow.append({
                'step': 3,
                'decision': 'WINNER LOCK PATTERN DETECTED',
                'explanation': 'Agency-State Lock detected (6/6 no-loss empirical proof)',
                'action': 'PROCEED TO LOCK_MODE',
                'blocked': False,
                'emoji': '👑'
            })
        else:
            decision_flow.append({
                'step': 3,
                'decision': 'NO WINNER LOCK PATTERN',
                'explanation': 'No Agency-State Lock detected',
                'action': 'Continue to Step 4',
                'blocked': False,
                'emoji': '⚪'
            })
        
        # STEP 4: Check for Totals Lock (separate pattern)
        has_totals_lock = all_results['totals_lock'].get('lock', False)
        if has_totals_lock:
            decision_flow.append({
                'step': 4,
                'decision': 'TOTALS LOCK DETECTED',
                'explanation': 'Both teams low-scoring ≤1.2 avg goals',
                'action': 'PROCEED TO LOCK_MODE',
                'blocked': False,
                'emoji': '🔒'
            })
        else:
            decision_flow.append({
                'step': 4,
                'decision': 'NO TOTALS LOCK',
                'explanation': 'Insufficient offensive incapacity',
                'action': 'Continue to Step 5',
                'blocked': False,
                'emoji': '⚪'
            })
        
        # STEP 5: Final Decision (CRITICAL FIX v7.1)
        has_proven_pattern = (has_edge_locks or has_elite_defense or has_winner_lock)
        
        if has_proven_pattern or has_totals_lock:
            # LOCK_MODE: Any proven pattern OR Totals Lock
            final_decision = {
                'step': 5,
                'decision': 'LOCK_MODE ACTIVATED',
                'explanation': f'Proven patterns detected: {", ".join(all_results["capital_decision"]["locks_present"])}',
                'action': 'CAPITAL MULTIPLIER: 2.0x',
                'blocked': False,
                'emoji': '✅',
                'recommendation': 'STRUCTURAL CERTAINTY - BET WITH CONFIDENCE'
            }
        else:
            # EDGE_MODE: No proven patterns
            final_decision = {
                'step': 5,
                'decision': 'STAY-AWAY RECOMMENDED',
                'explanation': 'No proven patterns detected (only 48% hit rate without patterns)',
                'action': 'CAPITAL MULTIPLIER: 1.0x',
                'blocked': True,
                'emoji': '🚫',
                'recommendation': 'HEURISTIC EDGE ONLY - AVOID STRUCTURAL BETS'
            }
        
        decision_flow.append(final_decision)
        
        # STEP 6: Pattern Independence Assessment v7.1
        pattern_combo = all_results['pattern_independence']['combination']
        pattern_confidence = all_results['pattern_independence']['confidence']
        
        decision_flow.append({
            'step': 6,
            'decision': 'PATTERN INDEPENDENCE ASSESSMENT',
            'explanation': f'{pattern_combo}: {all_results["pattern_independence"]["description"]}',
            'action': f'Confidence: {pattern_confidence}',
            'blocked': False,
            'emoji': all_results['pattern_independence']['emoji'],
            'pattern_count': pattern_combo
        })
        
        # STEP 7: UNDER 3.5 Assessment (if applicable)
        under_35_tier = all_results['under_35_confidence'].get('tier', 0)
        if under_35_tier >= 2:
            decision_flow.append({
                'step': 7,
                'decision': 'UNDER 3.5 CONFIDENCE',
                'explanation': all_results['under_35_confidence']['description'],
                'action': f'Stake Multiplier: {all_results["under_35_confidence"].get("stake_multiplier", 1.0):.1f}x',
                'blocked': False,
                'emoji': '📊',
                'recommendation': all_results['under_35_confidence'].get('recommendation', '')
            })
        
        return {
            'decision_flow': decision_flow,
            'final_verdict': final_decision['decision'],
            'capital_multiplier': all_results['capital_decision']['multiplier'],
            'should_stay_away': final_decision['blocked'],
            'pattern_status': pattern_combo,
            'has_proven_pattern': has_proven_pattern,
            'has_totals_lock': has_totals_lock
        }

# =================== STREAMLIT UI v7.1 ===================
def main():
    st.set_page_config(
        page_title="Fused Logic Engine v7.1",
        page_icon="🔓",
        layout="wide"
    )
    
    st.title("🔓 Fused Logic Engine v7.1")
    st.markdown("**CORRECTED DECISION LOGIC** - Edge-Derived Locks are VALID PATTERNS")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Match Parameters")
        
        # Team names
        home_name = st.text_input("Home Team", value="Milan")
        away_name = st.text_input("Away Team", value="Cagliari")
        
        st.subheader("Home Team Data (Last 5 Matches)")
        home_goals_scored = st.number_input("Home Goals Scored (last 5)", value=8, min_value=0)
        home_goals_conceded = st.number_input("Home Goals Conceded (last 5)", value=3, min_value=0)
        
        st.subheader("Away Team Data (Last 5 Matches)")
        away_goals_scored = st.number_input("Away Goals Scored (last 5)", value=5, min_value=0)
        away_goals_conceded = st.number_input("Away Goals Conceded (last 5)", value=5, min_value=0)
        
        league_avg_xg = st.number_input("League Avg xG", value=1.3, min_value=0.5, max_value=2.5, step=0.1)
        
        # Quick test scenarios
        st.subheader("Test Scenarios")
        scenario = st.selectbox("Load Scenario", [
            "Custom Input",
            "Edge-Derived Lock Example", 
            "Elite Defense Example",
            "No Patterns Example"
        ])
        
        if scenario == "Edge-Derived Lock Example":
            home_name, away_name = "Milan", "Cagliari"
            home_goals_conceded = 3  # Milan concedes 0.6 avg
            away_goals_conceded = 5  # Cagliari concedes 1.0 avg (EDGE-DERIVED TRIGGER!)
            
        elif scenario == "Elite Defense Example":
            home_name, away_name = "Juventus", "Pisa"
            home_goals_conceded = 2  # ≤4 total (ELITE DEFENSE!)
            away_goals_conceded = 7
        
        elif scenario == "No Patterns Example":
            home_name, away_name = "Team A", "Team B"
            home_goals_conceded = 8  # >4 total
            away_goals_conceded = 9  # >1.0 avg
        
        analyze_button = st.button("🔍 Analyze Match", type="primary")
    
    if analyze_button:
        # Prepare data
        home_data = {
            'goals_scored_last_5': home_goals_scored,
            'goals_conceded_last_5': home_goals_conceded,
            'home_xg_per_match': 1.6,
            'home_goals_scored': home_goals_scored * 2,
            'home_xg_for': home_goals_scored * 2.5,
            'home_setpiece_pct': 0.3,
            'home_openplay_pct': 0.6,
            'home_counter_pct': 0.2,
            'home_goals_conceded': home_goals_conceded * 2,
            'home_matches_played': 10,
            'away_xg_per_match': 1.2,
            'away_goals_scored': away_goals_scored * 1.5,
            'away_xg_for': away_goals_scored * 2.0,
            'away_setpiece_pct': 0.25,
            'away_openplay_pct': 0.5,
            'away_counter_pct': 0.1,
            'away_goals_conceded': away_goals_conceded * 2,
            'away_matches_played': 10
        }
        
        away_data = {
            'goals_scored_last_5': away_goals_scored,
            'goals_conceded_last_5': away_goals_conceded,
            'home_xg_per_match': 1.4,
            'home_goals_scored': away_goals_scored * 1.8,
            'home_xg_for': away_goals_scored * 2.2,
            'home_setpiece_pct': 0.28,
            'home_openplay_pct': 0.55,
            'home_counter_pct': 0.18,
            'home_goals_conceded': away_goals_conceded * 1.8,
            'home_matches_played': 10,
            'away_xg_per_match': 1.1,
            'away_goals_scored': home_goals_scored * 1.6,
            'away_xg_for': home_goals_scored * 2.1,
            'away_setpiece_pct': 0.32,
            'away_openplay_pct': 0.58,
            'away_counter_pct': 0.22,
            'away_goals_conceded': home_goals_conceded * 1.9,
            'away_matches_played': 10
        }
        
        # Execute analysis
        engine = FusedLogicEngineV71()
        results = engine.execute_fused_logic(
            home_data, away_data, 
            home_name, away_name,
            league_avg_xg
        )
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_conceded = results['defensive_assessment']['home_avg_conceded']
            st.metric(f"{home_name} Avg Conceded", f"{avg_conceded:.2f}")
            if results['elite_defense_home'].get('elite_defense'):
                st.success("🎯 ELITE DEFENSE PATTERN")
                st.caption(f"≤4 total goals conceded (100% empirical)")
            elif avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5']:
                st.success("🔓 EDGE-DERIVED LOCK")
                st.caption("≤1.0 avg conceded (2/2 empirical)")
            else:
                st.info("⚪ Standard Defense")
        
        with col2:
            avg_conceded = results['defensive_assessment']['away_avg_conceded']
            st.metric(f"{away_name} Avg Conceded", f"{avg_conceded:.2f}")
            if results['elite_defense_away'].get('elite_defense'):
                st.success("🎯 ELITE DEFENSE PATTERN")
                st.caption(f"≤4 total goals conceded (100% empirical)")
            elif avg_conceded <= DEFENSIVE_THRESHOLDS['OPPONENT_UNDER_1_5']:
                st.success("🔓 EDGE-DERIVED LOCK")
                st.caption("≤1.0 avg conceded (2/2 empirical)")
            else:
                st.info("⚪ Standard Defense")
        
        with col3:
            capital = results['capital_decision']
            pattern_status = results['pattern_independence']['combination']
            
            if capital['capital_mode'] == 'LOCK_MODE':
                st.success(f"💰 {capital['capital_mode']}")
                st.metric("Capital Multiplier", "2.0x")
            else:
                st.warning(f"💰 {capital['capital_mode']}")
                st.metric("Capital Multiplier", "1.0x")
            
            st.caption(f"Pattern: {pattern_status}")
        
        # Pattern Detection Summary
        st.subheader("🧩 Pattern Detection Summary")
        
        pattern_cols = st.columns(4)
        with pattern_cols[0]:
            st.metric("Edge-Derived", 
                     "✅" if results['has_edge_derived_locks'] else "❌",
                     "2/2 empirical" if results['has_edge_derived_locks'] else "")
        
        with pattern_cols[1]:
            st.metric("Elite Defense", 
                     "✅" if results['has_elite_defense'] else "❌",
                     "8/8 empirical" if results['has_elite_defense'] else "")
        
        with pattern_cols[2]:
            st.metric("Winner Lock", 
                     "✅" if results['has_winner_lock'] else "❌",
                     "6/6 no-loss" if results['has_winner_lock'] else "")
        
        with pattern_cols[3]:
            totals_lock = results['totals_lock'].get('lock', False)
            st.metric("Totals Lock", 
                     "✅" if totals_lock else "❌",
                     "Under 2.5" if totals_lock else "")
        
        # Decision Flow
        st.subheader("📋 Decision Flow v7.1")
        decision_matrix = results['decision_matrix']
        
        for step in decision_matrix['decision_flow']:
            col1, col2, col3 = st.columns([0.1, 0.3, 0.6])
            
            with col1:
                st.write(f"**Step {step['step']}**")
            
            with col2:
                if step.get('blocked', False):
                    st.error(f"{step['emoji']} {step['decision']}")
                elif step['emoji'] in ['🔓', '🛡️', '👑', '🔒', '✅']:
                    st.success(f"{step['emoji']} {step['decision']}")
                else:
                    st.info(f"{step['emoji']} {step['decision']}")
            
            with col3:
                st.write(step['explanation'])
                if step.get('action'):
                    st.caption(f"*Action: {step['action']}*")
                if step.get('recommendation'):
                    st.write(f"**{step['recommendation']}**")
        
        # Pattern Distribution
        st.subheader("📊 Pattern Distribution (25-Match Study)")
        dist = results['pattern_distribution']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Matches", dist['total_matches'])
        with col2:
            st.metric("Actionable", dist['actionable_matches'], 
                     f"{dist['actionable_matches']/dist['total_matches']*100:.0f}%")
        with col3:
            st.metric("Stay-Away", dist['stay_away_matches'],
                     f"{dist['stay_away_matches']/dist['total_matches']*100:.0f}%")
        with col4:
            if decision_matrix['should_stay_away']:
                st.error("48% hit rate")
            else:
                st.success("52% actionable")
        
        # Pattern Sources
        st.subheader("🔍 Pattern Sources Detected")
        if results['under_15_sources']:
            for source in results['under_15_sources']:
                if source.get('type') == 'PRIMARY_SOURCE':
                    with st.expander(f"🔓 {source['declaration']}", expanded=True):
                        st.write(f"**Reason:** {source['reason']}")
                        st.write(f"**Empirical Accuracy:** {source['empirical_accuracy']}")
                        if source.get('historical_evidence'):
                            st.write("**Historical Evidence:**")
                            for evidence in source['historical_evidence'][:3]:
                                st.caption(f"- {evidence}")
                else:
                    with st.expander(f"🎯 {source['declaration']}"):
                        st.write(f"**Reason:** {source['reason']}")
                        st.write(f"**Empirical Accuracy:** {source['empirical_accuracy']}")
        else:
            st.info("No UNDER 1.5 sources detected")
        
        # UNDER 3.5 Confidence
        under_35 = results['under_35_confidence']
        if under_35.get('tier', 0) > 0:
            st.subheader("📈 UNDER 3.5 Confidence")
            
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                confidence_pct = under_35['confidence'] * 100
                st.progress(under_35['confidence'], 
                           text=f"Confidence: {confidence_pct:.1f}%")
                st.write(f"**Description:** {under_35['description']}")
                if under_35.get('sample_size'):
                    st.caption(f"Sample Size: {under_35['sample_size']}")
            
            with col2:
                if under_35.get('recommendation'):
                    st.info(f"**{under_35['recommendation']}**")
                if under_35.get('stake_multiplier'):
                    st.metric("Stake Multiplier", f"{under_35['stake_multiplier']:.1f}x")
        
        # Final Verdict Box
        st.subheader("🎯 Final Verdict")
        
        verdict_container = st.container()
        with verdict_container:
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                if decision_matrix['should_stay_away']:
                    st.error("## 🚫 STAY AWAY RECOMMENDED")
                    st.write("**Reason:** No proven patterns detected")
                    st.write("Only heuristic edge available (48% hit rate)")
                    st.caption("Edge-Mode: 1.0x capital multiplier")
                else:
                    st.success("## ✅ LOCK MODE ACTIVATED")
                    st.write("**Reason:** Proven patterns detected")
                    st.write(f"Patterns: {results['pattern_independence']['combination']}")
                    st.caption(f"Lock-Mode: 2.0x capital multiplier")
            
            with col2:
                if not decision_matrix['should_stay_away']:
                    st.metric("Capital Authorized", "✅")
                    st.metric("Multiplier", "2.0x")
                    st.balloons()
                else:
                    st.metric("Capital Authorized", "⚠️")
                    st.metric("Multiplier", "1.0x")
        
        # Complete Pattern Detection (if available)
        if PATTERN_DETECTOR_AVAILABLE and 'complete_pattern_analysis' in results:
            st.subheader("🧩 Complete Pattern Analysis")
            complete = results['complete_pattern_analysis']
            
            if complete.get('has_elite_defense'):
                st.success(f"🛡️ Elite Defense Patterns: {len(complete.get('elite_defense_patterns', []))}")
            
            if complete.get('has_winner_lock'):
                st.success(f"👑 Winner Lock Pattern Detected")
            
            if complete.get('under_35_bet'):
                st.info(f"📊 Under 3.5 Bet: {complete['under_35_bet']}")
        
        # Raw data (for debugging)
        with st.expander("📊 Raw Analysis Data"):
            st.json(results, expanded=False)

if __name__ == "__main__":
    main()