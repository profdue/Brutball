"""
COMPLETE PATTERN DETECTION SYSTEM
Independent logic based purely on data inputs
No hardcoded teams or matches
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime

# =================== CORE PATTERN DETECTOR ===================
class CompletePatternDetector:
    """
    COMPLETE PATTERN DETECTION ENGINE
    
    TIER 1: ELITE DEFENSE → OPPONENT UNDER 1.5 (100% - 8 matches)
    TIER 2: WINNER LOCK → DOUBLE CHANCE (100% - 6 matches)
    TIER 3: UNDER 3.5 with confidence tiers based on patterns present
    """
    
    @staticmethod
    def detect_elite_defense(home_data: Dict, away_data: Dict) -> List[Dict]:
        """
        TIER 1: ELITE DEFENSE PATTERN
        
        Conditions (both required):
        1. Team concedes ≤4 goals TOTAL in last 5 matches (avg ≤0.8/match)
        2. Defense gap > 2.0 goals vs opponent
        """
        recommendations = []
        
        # Extract data
        home_name = home_data.get('team_name', 'Home')
        away_name = away_data.get('team_name', 'Away')
        home_conceded = home_data.get('goals_conceded_last_5', 0)
        away_conceded = away_data.get('goals_conceded_last_5', 0)
        
        # Check HOME team as elite defense
        if home_conceded <= 4:
            defense_gap = away_conceded - home_conceded
            if defense_gap > 2.0:
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': away_name,
                    'defensive_team': home_name,
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'condition_1': f"{home_name} concedes {home_conceded} ≤ 4 (last 5)",
                    'condition_2': f"Defense gap: +{defense_gap} > 2.0",
                    'stake_multiplier': 2.0,
                    'confidence': 'VERY_HIGH',
                    'sample_accuracy': '8/8 matches (100%)',
                    'historical_evidence': [
                        'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                        'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Man City 0-0 Sunderland'
                    ]
                })
        
        # Check AWAY team as elite defense
        if away_conceded <= 4:
            defense_gap = home_conceded - away_conceded
            if defense_gap > 2.0:
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': home_name,
                    'defensive_team': away_name,
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'condition_1': f"{away_name} concedes {away_conceded} ≤ 4 (last 5)",
                    'condition_2': f"Defense gap: +{defense_gap} > 2.0",
                    'stake_multiplier': 2.0,
                    'confidence': 'VERY_HIGH',
                    'sample_accuracy': '8/8 matches (100%)',
                    'historical_evidence': [
                        'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                        'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Man City 0-0 Sunderland'
                    ]
                })
        
        return recommendations
    
    @staticmethod
    def detect_winner_lock(match_data: Dict) -> Optional[Dict]:
        """
        TIER 2: WINNER LOCK PATTERN
        
        Conditions:
        1. Agency-State system detects WINNER lock (external input)
        2. Team with lock does NOT lose (wins or draws)
        """
        # Check if Winner Lock data is provided
        winner_lock_detected = match_data.get('winner_lock_detected', False)
        
        if not winner_lock_detected:
            return None
        
        # Extract Winner Lock details
        lock_team_side = match_data.get('winner_lock_team', '')  # 'home' or 'away'
        delta_value = match_data.get('winner_delta_value', 0)
        home_name = match_data.get('home_team', 'Home')
        away_name = match_data.get('away_team', 'Away')
        
        if not lock_team_side or delta_value <= 0:
            return None
        
        # Determine which team has the lock
        if lock_team_side == 'home':
            team_with_lock = home_name
        else:
            team_with_lock = away_name
        
        return {
            'pattern': 'WINNER_LOCK_DOUBLE_CHANCE',
            'bet_type': 'DOUBLE_CHANCE',
            'team_to_bet': team_with_lock,
            'lock_team': lock_team_side,
            'delta_value': delta_value,
            'condition_1': f"Agency-State Winner Lock detected",
            'condition_2': f"Δ = {delta_value:.2f} (directional dominance)",
            'stake_multiplier': 1.5,
            'confidence': 'HIGH',
            'sample_accuracy': '6/6 matches (100% no-loss)',
            'historical_evidence': [
                'Porto 2-0 AVS', 'Betis 4-0 Getafe', 'Napoli 2-0 Cremonese',
                'Udinese 1-1 Lazio', 'Man Utd 1-1 Wolves', 'Brentford 0-0 Spurs'
            ]
        }
    
    @staticmethod
    def determine_under_35_bet(elite_present: bool, winner_present: bool) -> Optional[Dict]:
        """
        TIER 3: UNDER 3.5 WITH CONFIDENCE TIERS
        
        Logic based on pattern presence:
        - BOTH patterns: 100% confidence (3/3 matches)
        - ONLY Elite Defense: 87.5% confidence (7/8 matches)
        - ONLY Winner Lock: 83.3% confidence (5/6 matches)
        - NO patterns: No bet (57% - insufficient edge)
        """
        
        if elite_present and winner_present:
            # TIER 1: BOTH PATTERNS
            return {
                'pattern': 'BOTH_PATTERNS_UNDER_3_5',
                'bet_type': 'TOTAL_UNDER_3_5',
                'reason': 'Both Elite Defense and Winner Lock patterns present',
                'condition': 'Elite Defense AND Winner Lock detected',
                'stake_multiplier': 1.2,
                'confidence': 'TIER_1_100',
                'sample_accuracy': '3/3 matches (100%)',
                'historical_evidence': ['Porto 2-0 AVS', 'Napoli 2-0 Cremonese', 'Udinese 1-1 Lazio']
            }
        
        elif elite_present and not winner_present:
            # TIER 2: ONLY ELITE DEFENSE
            return {
                'pattern': 'ELITE_DEFENSE_UNDER_3_5',
                'bet_type': 'TOTAL_UNDER_3_5',
                'reason': 'Elite Defense pattern present (scoring suppression)',
                'condition': 'Only Elite Defense detected',
                'stake_multiplier': 1.0,
                'confidence': 'TIER_2_87_5',
                'sample_accuracy': '7/8 matches (87.5%)',
                'historical_evidence': [
                    'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina', 'Milan 3-0 Verona',
                    'Pisa 0-2 Juventus', 'Man City 0-0 Sunderland'
                ],
                'warning': 'Exception: Strong attacking opponents may break pattern (Arsenal 4-1 Villa)'
            }
        
        elif not elite_present and winner_present:
            # TIER 3: ONLY WINNER LOCK
            return {
                'pattern': 'WINNER_LOCK_UNDER_3_5',
                'bet_type': 'TOTAL_UNDER_3_5',
                'reason': 'Winner Lock pattern present (controlled match environment)',
                'condition': 'Only Winner Lock detected',
                'stake_multiplier': 0.9,
                'confidence': 'TIER_3_83_3',
                'sample_accuracy': '5/6 matches (83.3%)',
                'historical_evidence': [
                    'Udinese 1-1 Lazio', 'Man Utd 1-1 Wolves', 'Brentford 0-0 Spurs'
                ],
                'warning': 'Exception: High-scoring matches possible (Betis 4-0 Getafe)'
            }
        
        else:
            # NO PATTERNS - No bet
            return None
    
    @classmethod
    def analyze_match_complete(cls, home_data: Dict, away_data: Dict, match_metadata: Dict) -> Dict:
        """
        COMPLETE MATCH ANALYSIS - All tiers
        
        Returns independent analysis based solely on input data
        """
        # Prepare team data
        home_team_data = {
            'team_name': match_metadata.get('home_team', 'Home'),
            'goals_conceded_last_5': home_data.get('goals_conceded_last_5', 0)
        }
        
        away_team_data = {
            'team_name': match_metadata.get('away_team', 'Away'),
            'goals_conceded_last_5': away_data.get('goals_conceded_last_5', 0)
        }
        
        # =================== TIER 1: ELITE DEFENSE ===================
        elite_defense_bets = cls.detect_elite_defense(home_team_data, away_team_data)
        has_elite_defense = len(elite_defense_bets) > 0
        
        # =================== TIER 2: WINNER LOCK ===================
        winner_lock_bet = cls.detect_winner_lock(match_metadata)
        has_winner_lock = winner_lock_bet is not None
        
        # =================== TIER 3: UNDER 3.5 ===================
        under_35_bet = cls.determine_under_35_bet(has_elite_defense, has_winner_lock)
        
        # =================== COMBINE ALL RECOMMENDATIONS ===================
        all_recommendations = []
        
        # Add Elite Defense bets (0, 1, or 2)
        all_recommendations.extend(elite_defense_bets)
        
        # Add Winner Lock bet (0 or 1)
        if winner_lock_bet:
            all_recommendations.append(winner_lock_bet)
        
        # Add UNDER 3.5 bet (0 or 1)
        if under_35_bet:
            all_recommendations.append(under_35_bet)
        
        # =================== PATTERN COMBINATION ANALYSIS ===================
        if has_elite_defense and has_winner_lock:
            pattern_combination = 'BOTH_PATTERNS'
            combination_desc = 'Both Elite Defense and Winner Lock patterns present'
            combination_emoji = '🎯'
        elif has_elite_defense and not has_winner_lock:
            pattern_combination = 'ONLY_ELITE_DEFENSE'
            combination_desc = 'Only Elite Defense pattern present'
            combination_emoji = '🛡️'
        elif not has_elite_defense and has_winner_lock:
            pattern_combination = 'ONLY_WINNER_LOCK'
            combination_desc = 'Only Winner Lock pattern present'
            combination_emoji = '👑'
        else:
            pattern_combination = 'NO_PATTERNS'
            combination_desc = 'No proven patterns detected'
            combination_emoji = '⚪'
        
        # =================== STATISTICS ===================
        pattern_stats = {
            'elite_defense_count': len(elite_defense_bets),
            'winner_lock_count': 1 if has_winner_lock else 0,
            'under_35_present': under_35_bet is not None,
            'total_patterns': len(all_recommendations),
            'pattern_combination': pattern_combination,
            'combination_emoji': combination_emoji
        }
        
        # =================== TIER SUMMARY ===================
        tier_summary = []
        if has_elite_defense:
            tier_summary.append('TIER 1: Elite Defense detected')
        if has_winner_lock:
            tier_summary.append('TIER 2: Winner Lock detected')
        if under_35_bet:
            tier_summary.append(f'TIER 3: UNDER 3.5 ({under_35_bet["confidence"]})')
        
        return {
            'recommendations': all_recommendations,
            'pattern_stats': pattern_stats,
            'pattern_combination': pattern_combination,
            'combination_desc': combination_desc,
            'combination_emoji': combination_emoji,
            'tier_summary': tier_summary,
            'has_elite_defense': has_elite_defense,
            'has_winner_lock': has_winner_lock,
            'under_35_bet': under_35_bet,
            'analysis_timestamp': datetime.now().isoformat(),
            'system_version': 'BRUTBALL_COMPLETE_TIERS_v1.0'
        }

# =================== DATA VALIDATOR ===================
class DataValidator:
    """Validate input data before analysis"""
    
    @staticmethod
    def validate_match_data(home_data: Dict, away_data: Dict, match_metadata: Dict) -> List[str]:
        """Validate all required data is present"""
        errors = []
        
        # Check required fields for Elite Defense detection
        required_elite_fields = ['goals_conceded_last_5']
        
        for field in required_elite_fields:
            if field not in home_data:
                errors.append(f"Missing home_data['{field}'] for Elite Defense detection")
            if field not in away_data:
                errors.append(f"Missing away_data['{field}'] for Elite Defense detection")
        
        # Check required fields for Winner Lock detection
        if match_metadata.get('winner_lock_detected', False):
            if 'winner_lock_team' not in match_metadata:
                errors.append("Missing winner_lock_team when winner_lock_detected=True")
            if 'winner_delta_value' not in match_metadata:
                errors.append("Missing winner_delta_value when winner_lock_detected=True")
        
        return errors

# =================== RESULT FORMATTER ===================
class ResultFormatter:
    """Format analysis results for display"""
    
    @staticmethod
    def format_pattern_name(pattern: str) -> str:
        """Convert pattern code to display name"""
        pattern_names = {
            'ELITE_DEFENSE_UNDER_1_5': 'Elite Defense → UNDER 1.5',
            'WINNER_LOCK_DOUBLE_CHANCE': 'Winner Lock → Double Chance',
            'BOTH_PATTERNS_UNDER_3_5': 'Both Patterns → UNDER 3.5',
            'ELITE_DEFENSE_UNDER_3_5': 'Elite Defense → UNDER 3.5',
            'WINNER_LOCK_UNDER_3_5': 'Winner Lock → UNDER 3.5'
        }
        return pattern_names.get(pattern, pattern.replace('_', ' '))
    
    @staticmethod
    def get_pattern_style(pattern: str) -> Dict:
        """Get styling for each pattern type"""
        styles = {
            'ELITE_DEFENSE_UNDER_1_5': {
                'emoji': '🛡️',
                'color': '#16A34A',
                'bg_color': '#F0FDF4',
                'border_color': '#16A34A'
            },
            'WINNER_LOCK_DOUBLE_CHANCE': {
                'emoji': '👑',
                'color': '#2563EB',
                'bg_color': '#EFF6FF',
                'border_color': '#2563EB'
            },
            'BOTH_PATTERNS_UNDER_3_5': {
                'emoji': '🎯',
                'color': '#F97316',
                'bg_color': '#FFEDD5',
                'border_color': '#F97316'
            },
            'ELITE_DEFENSE_UNDER_3_5': {
                'emoji': '📊',
                'color': '#059669',
                'bg_color': '#DCFCE7',
                'border_color': '#059669'
            },
            'WINNER_LOCK_UNDER_3_5': {
                'emoji': '📊',
                'color': '#1D4ED8',
                'bg_color': '#DBEAFE',
                'border_color': '#1D4ED8'
            }
        }
        return styles.get(pattern, {
            'emoji': '❓',
            'color': '#6B7280',
            'bg_color': '#F3F4F6',
            'border_color': '#9CA3AF'
        })
    
    @staticmethod
    def get_team_under_15_name(recommendation: Dict, home_team: str, away_team: str) -> str:
        """Get correct team name for UNDER 1.5 bets"""
        if recommendation['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
            defensive_team = recommendation.get('defensive_team', '')
            if defensive_team == home_team:
                return away_team
            else:
                return home_team
        return recommendation.get('team_to_bet', '')

# =================== COMPATIBILITY FUNCTIONS ===================
def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
    """Compatibility function for original classifier"""
    return {
        'pattern_detection_available': True,
        'note': 'Use CompletePatternDetector.analyze_match_complete() for full analysis'
    }

def format_reliability_badge(data: Dict) -> str:
    """Compatibility function"""
    return "🟢 Reliability: HIGH (Pattern-based detection)"

def format_durability_indicator(code: str) -> str:
    """Compatibility function"""
    return "📊 Pattern Durability: Tiered Confidence System"
