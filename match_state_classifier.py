"""
MATCH STATE CLASSIFIER with PROPER PATTERN SEPARATION
Correctly handles independent pattern appearance based on 25-match analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime

# =================== PROVEN PATTERN DETECTION WITH SEPARATION ===================
class ProvenPatternDetector:
    """
    REVISED LOGIC: Patterns appear INDEPENDENTLY
    
    📊 PATTERN DISTRIBUTION IN 25 MATCHES:
    • Total matches with Elite Defense: 8
    • Total matches with Winner Lock: 6  
    • Matches with BOTH patterns: 3 (Porto, Napoli, Udinese)
    • Matches with ONLY Elite Defense: 5
    • Matches with ONLY Winner Lock: 3
    • Matches with NEITHER pattern: 14
    
    🎯 UNDER 3.5 ACCURACY BY PATTERN TYPE:
    • Elite Defense (8): 7/8 UNDER 3.5 (87.5%)
    • Winner Lock (6): 5/6 UNDER 3.5 (83.3%)
    • Both patterns (3): 3/3 UNDER 3.5 (100%)
    • Neither pattern (14): 8/14 UNDER 3.5 (57.1%)
    """
    
    @staticmethod
    def detect_elite_defense_pattern(home_data: Dict, away_data: Dict) -> List[Dict]:
        """
        PATTERN A: ELITE DEFENSE → OPPONENT UNDER 1.5 GOALS
        
        Condition:
        1. Team concedes ≤4 goals TOTAL in last 5 matches (avg ≤0.8)
        2. Defense gap > 2.0 goals vs opponent
        """
        recommendations = []
        
        # Check HOME team as elite defense
        home_conceded = home_data.get('goals_conceded_last_5', 0)
        away_conceded = away_data.get('goals_conceded_last_5', 0)
        
        if home_conceded <= 4:
            defense_gap = away_conceded - home_conceded
            if defense_gap > 2.0:
                # Get attack strength for confidence tier
                away_scored = away_data.get('goals_scored_last_5', 0)
                away_attack_avg = away_scored / 5 if away_scored > 0 else 0
                
                confidence_tier = "STRONG"  # Default
                if away_attack_avg <= 1.4:
                    confidence_tier = "VERY_STRONG"
                elif away_attack_avg <= 1.6:
                    confidence_tier = "STRONG"
                elif away_attack_avg <= 1.8:
                    confidence_tier = "WEAK"
                else:
                    confidence_tier = "VERY_WEAK"  # Arsenal vs Villa case
                
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': away_data.get('team_name', 'Away'),
                    'defensive_team': home_data.get('team_name', 'Home'),
                    'reason': (
                        f"{home_data.get('team_name', 'Home')} elite defense: "
                        f"{home_conceded}/5 goals conceded, "
                        f"+{defense_gap} defense gap vs {away_data.get('team_name', 'Away')}"
                    ),
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'away_attack_avg': away_attack_avg,
                    'confidence_tier': confidence_tier,
                    'stake_multiplier': 2.0 if confidence_tier in ['VERY_STRONG', 'STRONG'] else 1.0,
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
                # Get attack strength for confidence tier
                home_scored = home_data.get('goals_scored_last_5', 0)
                home_attack_avg = home_scored / 5 if home_scored > 0 else 0
                
                confidence_tier = "STRONG"  # Default
                if home_attack_avg <= 1.4:
                    confidence_tier = "VERY_STRONG"
                elif home_attack_avg <= 1.6:
                    confidence_tier = "STRONG"
                elif home_attack_avg <= 1.8:
                    confidence_tier = "WEAK"
                else:
                    confidence_tier = "VERY_WEAK"
                
                recommendations.append({
                    'pattern': 'ELITE_DEFENSE_UNDER_1_5',
                    'bet_type': 'TEAM_UNDER_1_5',
                    'team_to_bet': home_data.get('team_name', 'Home'),
                    'defensive_team': away_data.get('team_name', 'Away'),
                    'reason': (
                        f"{away_data.get('team_name', 'Away')} elite defense: "
                        f"{away_conceded}/5 goals conceded, "
                        f"+{defense_gap} defense gap vs {home_data.get('team_name', 'Home')}"
                    ),
                    'defense_gap': defense_gap,
                    'home_conceded': home_conceded,
                    'away_conceded': away_conceded,
                    'home_attack_avg': home_attack_avg,
                    'confidence_tier': confidence_tier,
                    'stake_multiplier': 2.0 if confidence_tier in ['VERY_STRONG', 'STRONG'] else 1.0,
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
            'stake_multiplier': 1.5,  # Medium confidence (100% no-loss, 50% win rate)
            'sample_accuracy': '6/6 matches no losses (3 wins, 3 draws)',
            'sample_matches': [
                'Porto 2-0 AVS (win)', 'Betis 4-0 Getafe (win)', 
                'Napoli 2-0 Cremonese (win)', 'Udinese 1-1 Lazio (draw)',
                'Man Utd 1-1 Wolves (draw)', 'Brentford 0-0 Spurs (draw)'
            ]
        }
    
    @staticmethod
    def get_betting_decisions(has_elite_defense: bool, has_winner_lock: bool) -> Dict:
        """
        DECISION MATRIX based on pattern presence
        """
        
        decisions = {
            'elite_defense_bets': has_elite_defense,
            'winner_lock_bet': has_winner_lock,
            'under_3_5_bet': None,
            'under_3_5_confidence': None,
            'stake_multiplier': 0.0,
            'pattern_combination': ''
        }
        
        if has_elite_defense and has_winner_lock:
            # BOTH PATTERNS → Tier 1 (100% confidence)
            decisions.update({
                'under_3_5_bet': True,
                'under_3_5_confidence': 'TIER_1_100_PERCENT',
                'stake_multiplier': 1.2,
                'pattern_combination': 'BOTH_PATTERNS',
                'under_3_5_rate': '3/3 matches (100%)',
                'sample_matches': ['Porto 2-0 AVS', 'Napoli 2-0 Cremonese', 'Udinese 1-1 Lazio']
            })
            
        elif has_elite_defense and not has_winner_lock:
            # ONLY ELITE DEFENSE → Tier 2 (87.5% confidence)
            decisions.update({
                'under_3_5_bet': True,
                'under_3_5_confidence': 'TIER_2_87_5_PERCENT',
                'stake_multiplier': 1.0,
                'pattern_combination': 'ONLY_ELITE_DEFENSE',
                'under_3_5_rate': '7/8 matches (87.5%)',
                'sample_matches': ['Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina', 
                                  'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 
                                  'Man City 0-0 Sunderland']
            })
            
        elif not has_elite_defense and has_winner_lock:
            # ONLY WINNER LOCK → Tier 3 (83.3% confidence)
            decisions.update({
                'under_3_5_bet': True,
                'under_3_5_confidence': 'TIER_3_83_3_PERCENT',
                'stake_multiplier': 0.9,
                'pattern_combination': 'ONLY_WINNER_LOCK',
                'under_3_5_rate': '5/6 matches (83.3%)',
                'sample_matches': ['Betis 4-0 Getafe', 'Man Utd 1-1 Wolves', 
                                  'Brentford 0-0 Spurs']
            })
            
        else:
            # NO PATTERNS → No bet (57% not enough edge)
            decisions.update({
                'under_3_5_bet': False,
                'under_3_5_confidence': 'NO_BET_57_PERCENT',
                'stake_multiplier': 0.0,
                'pattern_combination': 'NO_PATTERNS',
                'under_3_5_rate': '8/14 matches (57.1%)',
                'sample_matches': ['Lecce 0-0 Como', 'Torino 0-0 Cagliari', 
                                  'Bologna 0-0 Sassuolo', 'Atalanta 0-0 Inter']
            })
        
        return decisions
    
    @staticmethod
    def get_under_35_reason(pattern_combination: str) -> str:
        """Get reason text for UNDER 3.5 based on pattern combination"""
        reasons = {
            'BOTH_PATTERNS': 'Both Elite Defense and Winner Lock patterns present (100% accuracy)',
            'ONLY_ELITE_DEFENSE': 'Elite Defense pattern present (87.5% accuracy for UNDER 3.5)',
            'ONLY_WINNER_LOCK': 'Winner Lock pattern present (83.3% accuracy for UNDER 3.5)',
            'NO_PATTERNS': 'No proven patterns detected'
        }
        return reasons.get(pattern_combination, 'Pattern analysis')
    
    @classmethod
    def generate_final_recommendations(
        cls, 
        home_data: Dict, 
        away_data: Dict, 
        match_metadata: Dict
    ) -> Dict:
        """
        FINAL VERSION: Handles pattern separation properly
        
        Patterns can appear:
        1. ALONE: Only Elite Defense
        2. ALONE: Only Winner Lock  
        3. TOGETHER: Both patterns
        4. NEITHER: No patterns
        """
        
        # Prepare team data
        home_team_data = {
            'team_name': match_metadata.get('home_team', 'Home'),
            'goals_conceded_last_5': home_data.get('goals_conceded_last_5', 0),
            'goals_scored_last_5': home_data.get('goals_scored_last_5', 0)
        }
        
        away_team_data = {
            'team_name': match_metadata.get('away_team', 'Away'),
            'goals_conceded_last_5': away_data.get('goals_conceded_last_5', 0),
            'goals_scored_last_5': away_data.get('goals_scored_last_5', 0)
        }
        
        # 1. Detect patterns INDEPENDENTLY
        elite_defense_bets = cls.detect_elite_defense_pattern(
            home_team_data, away_team_data
        )
        winner_lock_bet = cls.detect_winner_lock_pattern(match_metadata)
        
        has_elite_defense = len(elite_defense_bets) > 0
        has_winner_lock = winner_lock_bet is not None
        
        # 2. Get decisions based on pattern combination
        decisions = cls.get_betting_decisions(has_elite_defense, has_winner_lock)
        
        # 3. Generate specific bets
        all_recommendations = []
        
        # Add Elite Defense bets (if present)
        all_recommendations.extend(elite_defense_bets)
        
        # Add Winner Lock bet (if present)
        if winner_lock_bet:
            all_recommendations.append(winner_lock_bet)
        
        # Add UNDER 3.5 bet (if decision says yes)
        if decisions['under_3_5_bet']:
            reason = cls.get_under_35_reason(decisions['pattern_combination'])
            
            all_recommendations.append({
                'pattern': f'PATTERN_DRIVEN_UNDER_3_5',
                'bet_type': 'TOTAL_UNDER_3_5',
                'reason': reason,
                'stake_multiplier': decisions['stake_multiplier'],
                'confidence': decisions['under_3_5_confidence'],
                'pattern_combination': decisions['pattern_combination'],
                'under_3_5_rate': decisions['under_3_5_rate'],
                'sample_accuracy': decisions['under_3_5_rate'],
                'sample_matches': decisions['sample_matches']
            })
        
        # Generate summary based on pattern combination
        summary_parts = []
        if has_elite_defense:
            summary_parts.append(f"{len(elite_defense_bets)} Elite Defense bet(s)")
        if has_winner_lock:
            summary_parts.append("1 Winner Lock bet")
        if decisions['under_3_5_bet']:
            summary_parts.append("1 UNDER 3.5 bet")
        
        summary = f"Detected: {', '.join(summary_parts)}" if summary_parts else "No proven patterns detected"
        
        return {
            'patterns_detected': len(all_recommendations),
            'recommendations': all_recommendations,
            'summary': summary,
            'pattern_analysis': {
                'has_elite_defense': has_elite_defense,
                'has_winner_lock': has_winner_lock,
                'pattern_combination': decisions['pattern_combination'],
                'under_3_5_decision': decisions['under_3_5_bet'],
                'under_3_5_confidence': decisions['under_3_5_confidence']
            },
            'generated_at': datetime.now().isoformat(),
            'system_version': 'BRUTBALL_PATTERN_SEPARATION_v1.0'
        }

# =================== BANKROLL MANAGER (UPDATED) ===================
class BankrollManager:
    """Professional bankroll management with pattern-specific stakes"""
    
    def __init__(self, initial_bankroll: float = 10000.0):
        self.bankroll = initial_bankroll
        self.base_unit = initial_bankroll * 0.01
        self.consecutive_losses = 0
        self.daily_profit_loss = 0.0
        self.trades_today = 0
        
    def calculate_stake(self, recommendation: Dict, risk_level: str = 'MEDIUM') -> float:
        """
        Calculate stake based on pattern confidence and bankroll percentage
        """
        # Base percentage based on risk level
        base_percentage = {
            'CONSERVATIVE': 0.005,
            'MEDIUM': 0.01,
            'AGGRESSIVE': 0.015
        }.get(risk_level, 0.01)
        
        # Base stake
        base_stake = self.bankroll * base_percentage
        
        # Pattern-specific multipliers
        pattern_multipliers = {
            'ELITE_DEFENSE_UNDER_1_5': recommendation.get('stake_multiplier', 1.0),
            'WINNER_LOCK_DOUBLE_CHANCE': 1.0,
            'PATTERN_DRIVEN_UNDER_3_5': recommendation.get('stake_multiplier', 0.8)
        }
        
        multiplier = pattern_multipliers.get(
            recommendation.get('pattern', 'UNKNOWN'), 
            0.5
        )
        
        stake = base_stake * multiplier
        
        # Adjust for confidence tier (Elite Defense only)
        if recommendation.get('pattern') == 'ELITE_DEFENSE_UNDER_1_5':
            confidence = recommendation.get('confidence_tier', 'STRONG')
            if confidence == 'VERY_WEAK':
                stake *= 0.5  # Reduce stake for weak confidence
            elif confidence == 'WEAK':
                stake *= 0.75
        
        # Ensure minimum and maximum stakes
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
            
            home_goals_avg = home_goals / 5 if home_goals > 0 else 0
            home_conceded_avg = home_conceded / 5 if home_conceded > 0 else 0
            away_goals_avg = away_goals / 5 if away_goals > 0 else 0
            away_conceded_avg = away_conceded / 5 if away_conceded > 0 else 0
            
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
    """Main function that runs both original classifier and pattern detector"""
    classification_result = MatchStateClassifier.classify_match_state(home_data, away_data)
    
    classification_result['pattern_detection'] = {
        'available': True,
        'integration_note': 'Pattern detection runs separately via ProvenPatternDetector'
    }
    
    return classification_result

# =================== FORMATTING FUNCTIONS ===================
def format_reliability_badge(reliability_data: Dict) -> str:
    """Format reliability badge for display"""
    score = reliability_data.get('reliability_score', 0)
    label = reliability_data.get('reliability_label', 'NONE')
    
    emoji_map = {
        5: '🟢', 4: '🟡', 3: '🟠', 2: '⚪', 1: '⚪', 0: '⚫'
    }
    
    emoji = emoji_map.get(score, '⚫')
    return f'{emoji} **Reliability: {label} ({score}/5)**'

def format_durability_indicator(durability_code: str) -> str:
    """Format durability indicator for display"""
    if durability_code == 'STABLE':
        return '🟢 **Stable** (Both teams ≤ 1.2 avg goals)'
    elif durability_code == 'FRAGILE':
        return '🟡 **Fragile** (Potential scoring volatility)'
    else:
        return '⚪ **Unknown**'

def format_pattern_badge(pattern_type: str) -> str:
    """Format pattern badge for beautiful UI display"""
    pattern_configs = {
        'ELITE_DEFENSE_UNDER_1_5': {
            'emoji': '🛡️',
            'color': '#16A34A',
            'label': 'Elite Defense'
        },
        'WINNER_LOCK_DOUBLE_CHANCE': {
            'emoji': '👑',
            'color': '#2563EB',
            'label': 'Winner Lock'
        },
        'PATTERN_DRIVEN_UNDER_3_5': {
            'emoji': '📊',
            'color': '#7C3AED',
            'label': 'Under 3.5'
        }
    }
    
    config = pattern_configs.get(pattern_type, {
        'emoji': '❓',
        'color': '#6B7280',
        'label': 'Unknown'
    })
    
    return f"<span style='background: {config['color']}15; color: {config['color']}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid {config['color']}30;'>{config['emoji']} {config['label']}</span>"

def get_confidence_color(confidence_tier: str) -> str:
    """Get color for confidence tier"""
    colors = {
        'VERY_STRONG': '#16A34A',  # Green
        'STRONG': '#10B981',       # Emerald
        'WEAK': '#F59E0B',         # Amber
        'VERY_WEAK': '#DC2626',    # Red
        'TIER_1_100_PERCENT': '#059669',   # Green
        'TIER_2_87_5_PERCENT': '#10B981',  # Emerald
        'TIER_3_83_3_PERCENT': '#D97706',  # Yellow
        'NO_BET_57_PERCENT': '#6B7280'     # Gray
    }
    return colors.get(confidence_tier, '#6B7280')
