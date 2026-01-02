"""
MATCH STATE CLASSIFIER with PROPER PATTERN SEPARATION
Patterns appear independently: Alone, Together, or Neither
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime

# =================== PROVEN PATTERN DETECTOR WITH SEPARATION ===================
class ProvenPatternDetector:
    """
    REVISED: Patterns appear independently (Alone, Together, Neither)
    
    PATTERN A: ELITE DEFENSE → OPPONENT UNDER 1.5 (8 matches, 100%)
    PATTERN B: WINNER LOCK → DOUBLE CHANCE (6 matches, 100%)
    PATTERN C: UNDER 3.5 → Different confidence based on patterns present
    """
    
    @staticmethod
    def detect_elite_defense_pattern(home_data: Dict, away_data: Dict) -> List[Dict]:
        """
        PATTERN A: ELITE DEFENSE → OPPONENT UNDER 1.5
        
        Condition:
        1. Team concedes ≤4 goals TOTAL in last 5 matches (avg ≤0.8)
        2. Defense gap > 2.0 goals vs opponent
        
        Returns: List of bets (0, 1, or 2 depending on teams)
        """
        recommendations = []
        
        # Check HOME team as elite defense
        home_conceded = home_data.get('goals_conceded_last_5', 0)
        away_conceded = away_data.get('goals_conceded_last_5', 0)
        
        if home_conceded <= 4:
            defense_gap = away_conceded - home_conceded
            if defense_gap > 2.0:
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': away_data.get('team_name', 'Away'),
                    'defensive_team': home_data.get('team_name', 'Home'),
                    'reason': (
                        f"{home_data.get('team_name', 'Home')} elite defense: "
                        f"{home_conceded}/5 goals conceded, "
                        f"+{defense_gap} defense gap"
                    ),
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'stake_multiplier': 2.0,
                    'sample_accuracy': '8/8 matches (100%)',
                    'sample_matches': [
                        'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                        'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Arsenal 4-1 Villa',
                        'Man City 0-0 Sunderland'
                    ]
                })
        
        # Check AWAY team as elite defense
        if away_conceded <= 4:
            defense_gap = home_conceded - away_conceded
            if defense_gap > 2.0:
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': home_data.get('team_name', 'Home'),
                    'defensive_team': away_data.get('team_name', 'Away'),
                    'reason': (
                        f"{away_data.get('team_name', 'Away')} elite defense: "
                        f"{away_conceded}/5 goals conceded, "
                        f"+{defense_gap} defense gap"
                    ),
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'stake_multiplier': 2.0,
                    'sample_accuracy': '8/8 matches (100%)',
                    'sample_matches': [
                        'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                        'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Arsenal 4-1 Villa',
                        'Man City 0-0 Sunderland'
                    ]
                })
        
        return recommendations
    
    @staticmethod
    def detect_winner_lock_pattern(match_data: Dict) -> Optional[Dict]:
        """
        PATTERN B: WINNER LOCK → DOUBLE CHANCE (WIN OR DRAW)
        
        Condition:
        1. System's Agency-State Lock gives WINNER lock
        2. That team does NOT lose (wins or draws)
        
        Returns: Single bet or None
        """
        if not match_data.get('winner_lock_detected', False):
            return None
        
        team_with_lock = match_data.get('winner_lock_team', '')
        delta_value = match_data.get('winner_delta_value', 0)
        
        if not team_with_lock or delta_value <= 0:
            return None
        
        return {
            'pattern': 'WINNER_LOCK_DOUBLE_CHANCE',
            'bet_type': 'DOUBLE_CHANCE',
            'team_to_bet': match_data.get(f'{team_with_lock}_team', ''),
            'lock_team': team_with_lock,
            'delta_value': delta_value,
            'reason': (
                f"Winner lock detected (Δ={delta_value:.2f}) - "
                f"Team does not lose (wins or draws)"
            ),
            'stake_multiplier': 1.5,
            'sample_accuracy': '6/6 matches no losses (3 wins, 3 draws)',
            'sample_matches': [
                'Porto 2-0 AVS (win)', 'Betis 4-0 Getafe (win)', 
                'Napoli 2-0 Cremonese (win)', 'Udinese 1-1 Lazio (draw)',
                'Man Utd 1-1 Wolves (draw)', 'Brentford 0-0 Spurs (draw)'
            ]
        }
    
    @staticmethod
    def determine_under_35_decision(
        has_elite_defense: bool, 
        has_winner_lock: bool
    ) -> Dict:
        """
        PATTERN C: UNDER 3.5 with TIERED CONFIDENCE
        
        Different confidence based on which patterns are present:
        - Tier 1: BOTH patterns (100% - 3/3 matches)
        - Tier 2: ONLY Elite Defense (87.5% - 7/8 matches)  
        - Tier 3: ONLY Winner Lock (83.3% - 5/6 matches)
        - Tier 4: NO patterns (57% - No bet)
        """
        
        if has_elite_defense and has_winner_lock:
            # BOTH patterns → Highest confidence
            return {
                'should_bet': True,
                'pattern': 'BOTH_PATTERNS_UNDER_3_5',
                'reason': 'Both Elite Defense and Winner Lock patterns present',
                'stake_multiplier': 1.2,
                'confidence': 'TIER_1_100',
                'sample_accuracy': '3/3 matches (100%)',
                'sample_matches': ['Porto 2-0 AVS', 'Napoli 2-0 Cremonese', 'Udinese 1-1 Lazio']
            }
        
        elif has_elite_defense and not has_winner_lock:
            # ONLY Elite Defense → Medium confidence
            return {
                'should_bet': True,
                'pattern': 'ELITE_DEFENSE_UNDER_3_5',
                'reason': 'Elite Defense pattern present',
                'stake_multiplier': 1.0,
                'confidence': 'TIER_2_87_5',
                'sample_accuracy': '7/8 matches (87.5%)',
                'sample_matches': [
                    'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina', 'Milan 3-0 Verona',
                    'Pisa 0-2 Juventus', 'Man City 0-0 Sunderland', 'Arsenal 4-1 Villa'
                ]
            }
        
        elif not has_elite_defense and has_winner_lock:
            # ONLY Winner Lock → Lower confidence
            return {
                'should_bet': True,
                'pattern': 'WINNER_LOCK_UNDER_3_5',
                'reason': 'Winner Lock pattern present',
                'stake_multiplier': 0.9,
                'confidence': 'TIER_3_83_3',
                'sample_accuracy': '5/6 matches (83.3%)',
                'sample_matches': [
                    'Betis 4-0 Getafe', 'Man Utd 1-1 Wolves', 'Brentford 0-0 Spurs'
                ]
            }
        
        else:
            # NO patterns → No bet
            return {
                'should_bet': False,
                'pattern': 'NO_PATTERNS',
                'reason': 'No proven patterns detected',
                'confidence': 'TIER_4_57',
                'sample_accuracy': '8/14 matches UNDER 3.5 (57%)',
                'note': 'Not enough edge for profitable betting'
            }
    
    @classmethod
    def generate_separated_patterns(
        cls, 
        home_data: Dict, 
        away_data: Dict, 
        match_metadata: Dict
    ) -> Dict:
        """
        MAIN FUNCTION: Generate patterns with proper separation
        
        Patterns can appear:
        1. Alone (Only Elite Defense)
        2. Alone (Only Winner Lock)  
        3. Together (Both patterns)
        4. Neither (No patterns)
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
        
        # 1. Detect patterns independently
        elite_defense_bets = cls.detect_elite_defense_pattern(
            home_team_data, away_team_data
        )
        winner_lock_bet = cls.detect_winner_lock_pattern(match_metadata)
        
        has_elite_defense = len(elite_defense_bets) > 0
        has_winner_lock = winner_lock_bet is not None
        
        # 2. Determine UNDER 3.5 decision
        under_35_decision = cls.determine_under_35_decision(
            has_elite_defense, has_winner_lock
        )
        
        # 3. Combine all recommendations
        all_recommendations = []
        
        # Add Elite Defense bets (0, 1, or 2)
        all_recommendations.extend(elite_defense_bets)
        
        # Add Winner Lock bet (0 or 1)
        if winner_lock_bet:
            all_recommendations.append(winner_lock_bet)
        
        # Add UNDER 3.5 bet if applicable
        if under_35_decision['should_bet']:
            all_recommendations.append({
                'pattern': under_35_decision['pattern'],
                'bet_type': 'TOTAL_UNDER_3_5',
                'reason': under_35_decision['reason'],
                'stake_multiplier': under_35_decision['stake_multiplier'],
                'confidence': under_35_decision['confidence'],
                'sample_accuracy': under_35_decision['sample_accuracy'],
                'sample_matches': under_35_decision['sample_matches']
            })
        
        # 4. Generate pattern combination summary
        pattern_combination = None
        if has_elite_defense and has_winner_lock:
            pattern_combination = 'BOTH_PATTERNS'
            combination_desc = 'Both Elite Defense and Winner Lock patterns present'
        elif has_elite_defense and not has_winner_lock:
            pattern_combination = 'ONLY_ELITE_DEFENSE'
            combination_desc = 'Only Elite Defense pattern present'
        elif not has_elite_defense and has_winner_lock:
            pattern_combination = 'ONLY_WINNER_LOCK'
            combination_desc = 'Only Winner Lock pattern present'
        else:
            pattern_combination = 'NO_PATTERNS'
            combination_desc = 'No proven patterns detected'
        
        # 5. Pattern statistics
        pattern_stats = {
            'elite_defense_count': len(elite_defense_bets),
            'winner_lock_count': 1 if has_winner_lock else 0,
            'under_35_decision': under_35_decision['should_bet'],
            'under_35_confidence': under_35_decision['confidence'],
            'pattern_combination': pattern_combination,
            'combination_description': combination_desc,
            'total_patterns_detected': len(all_recommendations)
        }
        
        return {
            'recommendations': all_recommendations,
            'pattern_stats': pattern_stats,
            'pattern_combination': pattern_combination,
            'combination_desc': combination_desc,
            'generated_at': datetime.now().isoformat(),
            'system_version': 'BRUTBALL_PATTERN_SEPARATION_v2.0'
        }

# =================== BANKROLL MANAGER (UPDATED) ===================
class BankrollManager:
    """Bankroll management with pattern-based stake adjustment"""
    
    def __init__(self, initial_bankroll: float = 10000.0):
        self.bankroll = initial_bankroll
        self.base_unit = initial_bankroll * 0.01
        
    def calculate_stake(self, recommendation: Dict, risk_level: str = 'MEDIUM') -> float:
        """Calculate stake with pattern-specific adjustments"""
        
        # Base percentage
        base_percentage = {
            'CONSERVATIVE': 0.005,
            'MEDIUM': 0.01,
            'AGGRESSIVE': 0.015
        }.get(risk_level, 0.01)
        
        base_stake = self.bankroll * base_percentage
        
        # Pattern-specific multipliers
        pattern_multipliers = {
            'ELITE_DEFENSE_UNDER_1_5': 2.0,    # Highest confidence (100%)
            'WINNER_LOCK_DOUBLE_CHANCE': 1.5,  # Medium confidence (100% no-loss)
            'BOTH_PATTERNS_UNDER_3_5': 1.2,    # Tier 1 UNDER 3.5 (100%)
            'ELITE_DEFENSE_UNDER_3_5': 1.0,    # Tier 2 UNDER 3.5 (87.5%)
            'WINNER_LOCK_UNDER_3_5': 0.9       # Tier 3 UNDER 3.5 (83.3%)
        }
        
        multiplier = pattern_multipliers.get(
            recommendation.get('pattern'), 
            0.5  # Default for unknown patterns
        )
        
        stake = base_stake * multiplier
        
        # Ensure reasonable bounds
        min_stake = self.bankroll * 0.001
        max_stake = self.bankroll * 0.05
        
        return max(min_stake, min(stake, max_stake))

# =================== ORIGINAL CLASSIFIER (MAINTAINED) ===================
class MatchStateClassifier:
    """Original classifier maintained for backward compatibility"""
    
    STATE_CONFIG = {
        'STAGNATION': {'emoji': '🌀', 'label': 'Stagnation', 'color': '#0EA5E9'},
        'SUPPRESSION': {'emoji': '🔒', 'label': 'Suppression', 'color': '#16A34A'},
        'DELAYED_EXPLOSION': {'emoji': '⏳', 'label': 'Delayed Explosion', 'color': '#F59E0B'},
        'EXPLOSION': {'emoji': '💥', 'label': 'Explosion', 'color': '#EF4444'},
        'NEUTRAL': {'emoji': '⚖️', 'label': 'Neutral', 'color': '#6B7280'}
    }
    
    @staticmethod
    def classify_match_state(home_data: Dict, away_data: Dict) -> Dict:
        """Classify match state based on goals data"""
        try:
            home_goals = home_data.get('goals_scored_last_5', 0)
            home_conceded = home_data.get('goals_conceded_last_5', 0)
            away_goals = away_data.get('goals_scored_last_5', 0)
            away_conceded = away_data.get('goals_conceded_last_5', 0)
            
            # Calculate averages
            home_goals_avg = home_goals / 5 if home_goals > 0 else 0
            home_conceded_avg = home_conceded / 5 if home_conceded > 0 else 0
            away_goals_avg = away_goals / 5 if away_goals > 0 else 0
            away_conceded_avg = away_conceded / 5 if away_conceded > 0 else 0
            
            # Determine state
            if home_goals_avg < 1.0 and away_goals_avg < 1.0:
                state = 'STAGNATION'
            elif (home_conceded_avg < 0.8 and away_goals_avg < 1.0) or (away_conceded_avg < 0.8 and home_goals_avg < 1.0):
                state = 'SUPPRESSION'
            elif home_goals_avg > 2.0 or away_goals_avg > 2.0:
                state = 'EXPLOSION'
            elif (home_goals_avg > 1.5 and away_goals_avg > 1.5) and (home_conceded_avg > 1.5 or away_conceded_avg > 1.5):
                state = 'DELAYED_EXPLOSION'
            else:
                state = 'NEUTRAL'
            
            return {
                'dominant_state': state,
                'state_config': MatchStateClassifier.STATE_CONFIG.get(state, MatchStateClassifier.STATE_CONFIG['NEUTRAL']),
                'averages': {
                    'home_goals_avg': home_goals_avg,
                    'home_conceded_avg': home_conceded_avg,
                    'away_goals_avg': away_goals_avg,
                    'away_conceded_avg': away_conceded_avg
                },
                'classification_error': False
            }
            
        except Exception as e:
            return {
                'classification_error': True,
                'error_message': f"Classification error: {str(e)}"
            }

# =================== COMPLETE CLASSIFICATION FUNCTION ===================
def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
    """Main function for original classifier"""
    return MatchStateClassifier.classify_match_state(home_data, away_data)
