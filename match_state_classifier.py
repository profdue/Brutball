"""
MATCH STATE CLASSIFIER with PROVEN PATTERN DETECTION
Integrates 25-match empirical analysis patterns with beautiful UI display
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from datetime import datetime

# =================== PROVEN PATTERN DETECTION ENGINE ===================
class ProvenPatternDetector:
    """
    R&D PATTERNS FROM 25-MATCH EMPIRICAL ANALYSIS
    
    PATTERN A: ELITE DEFENSE UNDER 1.5 (100% - 8 matches)
    PATTERN B: WINNER LOCK DOUBLE CHANCE (100% - 6 matches) 
    PATTERN C: UNDER 3.5 WHEN PATTERNS PRESENT (83.3% - 10/12 matches)
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
                    'stake_multiplier': 2.0,  # Higher confidence (100% in sample)
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
    def detect_under_3_5_pattern(
        elite_defense_bets: List[Dict], 
        winner_lock_bet: Optional[Dict]
    ) -> Optional[Dict]:
        """
        PATTERN C: UNDER 3.5 TOTAL WHEN PATTERNS PRESENT
        
        Condition:
        1. EITHER Elite Defense OR Winner Lock pattern is present
        2. Bet UNDER 3.5 total goals
        """
        has_any_pattern = len(elite_defense_bets) > 0 or winner_lock_bet is not None
        
        if not has_any_pattern:
            return None
        
        # Determine which patterns are present
        pattern_description = []
        if elite_defense_bets:
            pattern_description.append('Elite Defense')
        if winner_lock_bet:
            pattern_description.append('Winner Lock')
        
        return {
            'pattern': 'PATTERN_DRIVEN_UNDER_3_5',
            'bet_type': 'TOTAL_UNDER_3_5',
            'reason': (
                f"Pattern detected - "
                f"{' & '.join(pattern_description)} present"
            ),
            'pattern_count': len(elite_defense_bets) + (1 if winner_lock_bet else 0),
            'stake_multiplier': 1.0,  # Lower confidence (83.3% in sample)
            'sample_accuracy': '10/12 matches (83.3%)',
            'sample_matches': [
                'Porto 2-0 AVS', 'Espanyol 2-1 Athletic', 'Parma 1-0 Fiorentina',
                'Juventus 2-0 Pisa', 'Milan 3-0 Verona', 'Man City 0-0 Sunderland',
                'Udinese 1-1 Lazio', 'Man Utd 1-1 Wolves', 'Brentford 0-0 Spurs',
                # Exceptions: Betis 4-0 Getafe, Arsenal 4-1 Villa
            ]
        }
    
    @classmethod
    def generate_all_patterns(
        cls, 
        home_data: Dict, 
        away_data: Dict, 
        match_metadata: Dict
    ) -> Dict:
        """
        Generate all betting pattern recommendations for a match
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
        
        # Detect patterns
        elite_defense_bets = cls.detect_elite_defense_pattern(
            home_team_data, away_team_data
        )
        winner_lock_bet = cls.detect_winner_lock_pattern(match_metadata)
        under_3_5_bet = cls.detect_under_3_5_pattern(elite_defense_bets, winner_lock_bet)
        
        # Combine all recommendations
        all_recommendations = []
        all_recommendations.extend(elite_defense_bets)
        
        if winner_lock_bet:
            all_recommendations.append(winner_lock_bet)
        
        if under_3_5_bet:
            all_recommendations.append(under_3_5_bet)
        
        # Generate summary
        pattern_counts = {
            'ELITE_DEFENSE_UNDER_1_5': 0,
            'WINNER_LOCK_DOUBLE_CHANCE': 0,
            'PATTERN_DRIVEN_UNDER_3_5': 0
        }
        
        for rec in all_recommendations:
            pattern_counts[rec['pattern']] += 1
        
        summary_parts = []
        if pattern_counts['ELITE_DEFENSE_UNDER_1_5'] > 0:
            summary_parts.append(f"{pattern_counts['ELITE_DEFENSE_UNDER_1_5']} Elite Defense bet(s)")
        if pattern_counts['WINNER_LOCK_DOUBLE_CHANCE'] > 0:
            summary_parts.append("1 Winner Lock bet")
        if pattern_counts['PATTERN_DRIVEN_UNDER_3_5'] > 0:
            summary_parts.append("1 UNDER 3.5 bet")
        
        summary = f"Detected: {', '.join(summary_parts)}" if summary_parts else "No proven patterns detected"
        
        return {
            'patterns_detected': len(all_recommendations),
            'recommendations': all_recommendations,
            'summary': summary,
            'pattern_counts': pattern_counts,
            'generated_at': datetime.now().isoformat(),
            'system_version': 'BRUTBALL_PROVEN_PATTERNS_v1.0'
        }

# =================== BANKROLL MANAGER ===================
class BankrollManager:
    """Professional bankroll management for pattern-based betting"""
    
    def __init__(self, initial_bankroll: float = 10000.0):
        self.bankroll = initial_bankroll
        self.base_unit = initial_bankroll * 0.01  # 1% of bankroll
        self.consecutive_losses = 0
        self.daily_profit_loss = 0.0
        self.trades_today = 0
        
    def calculate_stake(self, recommendation: Dict, risk_level: str = 'MEDIUM') -> float:
        """
        Calculate stake based on pattern confidence and bankroll percentage
        
        Risk Levels:
        - CONSERVATIVE: 0.5% of bankroll per bet
        - MEDIUM: 1.0% of bankroll per bet (default)
        - AGGRESSIVE: 1.5% of bankroll per bet
        """
        # Base percentage based on risk level
        base_percentage = {
            'CONSERVATIVE': 0.005,
            'MEDIUM': 0.01,
            'AGGRESSIVE': 0.015
        }.get(risk_level, 0.01)
        
        # Base stake
        base_stake = self.bankroll * base_percentage
        
        # Adjust for pattern confidence
        pattern_multipliers = {
            'ELITE_DEFENSE_UNDER_1_5': 1.5,    # Higher confidence (100%)
            'WINNER_LOCK_DOUBLE_CHANCE': 1.0,  # Medium confidence (100% no-loss)
            'PATTERN_DRIVEN_UNDER_3_5': 0.75   # Lower confidence (83.3%)
        }
        
        multiplier = pattern_multipliers.get(
            recommendation.get('pattern', 'UNKNOWN'), 
            0.5  # Default for unknown patterns
        )
        
        stake = base_stake * multiplier
        
        # Ensure minimum and maximum stakes
        min_stake = self.bankroll * 0.001  # 0.1% minimum
        max_stake = self.bankroll * 0.05   # 5% maximum
        
        return max(min_stake, min(stake, max_stake))
    
    def update_after_result(self, result_profit: float):
        """Update bankroll and risk metrics after bet result"""
        self.bankroll += result_profit
        self.daily_profit_loss += result_profit
        self.trades_today += 1
        
        if result_profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
    
    def should_continue_betting(self) -> Tuple[bool, str]:
        """Risk management rules to continue/stop betting"""
        # Rule 1: Stop if 3 consecutive losses (shouldn't happen with 100% patterns)
        if self.consecutive_losses >= 3:
            return False, "STOP: 3 consecutive losses - system verification needed"
        
        # Rule 2: Daily loss limit (10% of bankroll)
        if self.daily_profit_loss < -self.bankroll * 0.10:
            return False, f"STOP: Daily loss limit reached (-{abs(self.daily_profit_loss):.2f})"
        
        # Rule 3: Daily profit target (optional: 15% profit)
        if self.daily_profit_loss > self.bankroll * 0.15:
            return False, f"SUCCESS: Daily profit target reached (+{self.daily_profit_loss:.2f})"
        
        # Rule 4: Maximum trades per day
        if self.trades_today >= 20:
            return False, f"STOP: Maximum trades per day reached ({self.trades_today})"
        
        # Rule 5: Minimum bankroll
        if self.bankroll < self.base_unit * 10:
            return False, f"STOP: Insufficient bankroll ({self.bankroll:.2f})"
        
        return True, f"OK to continue (Bankroll: {self.bankroll:.2f}, Today: {self.daily_profit_loss:+.2f})"
    
    def get_status(self) -> Dict:
        """Get current bankroll status"""
        return {
            'bankroll': self.bankroll,
            'base_unit': self.base_unit,
            'consecutive_losses': self.consecutive_losses,
            'daily_profit_loss': self.daily_profit_loss,
            'trades_today': self.trades_today,
            'risk_per_bet': self.base_unit / self.bankroll * 100 if self.bankroll > 0 else 0
        }

# =================== ORIGINAL CLASSIFIER (MAINTAINED FOR COMPATIBILITY) ===================
class MatchStateClassifier:
    """Original classifier maintained for backward compatibility"""
    
    # State configurations
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
        # This maintains compatibility with existing code
        try:
            # Extract goals data
            home_goals = home_data.get('goals_scored_last_5', 0)
            home_conceded = home_data.get('goals_conceded_last_5', 0)
            away_goals = away_data.get('goals_scored_last_5', 0)
            away_conceded = away_data.get('goals_conceded_last_5', 0)
            
            # Calculate averages (assuming 5 matches)
            home_goals_avg = home_goals / 5 if home_goals > 0 else 0
            home_conceded_avg = home_conceded / 5 if home_conceded > 0 else 0
            away_goals_avg = away_goals / 5 if away_goals > 0 else 0
            away_conceded_avg = away_conceded / 5 if away_conceded > 0 else 0
            
            # Determine state (simplified logic)
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
    
    @staticmethod
    def create_ui_display_data(classification_result: Dict) -> Dict:
        """Create UI-friendly display data"""
        if classification_result.get('classification_error', True):
            return {
                'display_type': 'ERROR',
                'error_message': classification_result.get('error_message', 'Unknown error')
            }
        
        # Extract data
        state = classification_result.get('dominant_state', 'NEUTRAL')
        averages = classification_result.get('averages', {})
        
        # Determine durability
        totals_durability = 'STABLE' if averages.get('home_goals_avg', 0) < 1.2 and averages.get('away_goals_avg', 0) < 1.2 else 'FRAGILE'
        
        # Determine under suggestion
        if averages.get('home_conceded_avg', 0) < 1.0 or averages.get('away_conceded_avg', 0) < 1.0:
            under_suggestion = 'Strong defensive setup for UNDER markets'
        else:
            under_suggestion = 'Standard UNDER consideration'
        
        # Reliability scoring
        reliability_score = 4  # Default medium-high reliability
        if averages.get('home_goals_avg', 0) > 0 and averages.get('away_goals_avg', 0) > 0:
            reliability_score = 5  # High reliability with complete data
        
        return {
            'display_type': 'CLASSIFICATION',
            'match_state': {
                'code': state,
                'label': classification_result.get('state_config', {}).get('label', 'Neutral'),
                'emoji': classification_result.get('state_config', {}).get('emoji', '⚖️'),
                'color': classification_result.get('state_config', {}).get('color', '#6B7280')
            },
            'averages': {
                'home_goals': averages.get('home_goals_avg', 0),
                'home_conceded': averages.get('home_conceded_avg', 0),
                'away_goals': averages.get('away_goals_avg', 0),
                'away_conceded': averages.get('away_conceded_avg', 0)
            },
            'durability': {
                'code': totals_durability,
                'label': totals_durability,
                'color': '#16A34A' if totals_durability == 'STABLE' else '#F59E0B'
            },
            'under_suggestion': under_suggestion,
            'reliability': {
                'reliability_score': reliability_score,
                'reliability_label': ['NONE', 'LOW', 'MEDIUM', 'HIGH', 'VERY HIGH', 'ELITE'][reliability_score]
            },
            'defensive_analysis': {
                'home_strong_defense': averages.get('home_conceded_avg', 0) < 1.0,
                'away_strong_defense': averages.get('away_conceded_avg', 0) < 1.0
            }
        }

# =================== COMPLETE CLASSIFICATION FUNCTION ===================
def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
    """
    Main function that runs both original classifier and pattern detector
    """
    # Run original classifier
    classification_result = MatchStateClassifier.classify_match_state(home_data, away_data)
    
    # Add pattern detection results
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
        5: '🟢',  # Green
        4: '🟡',  # Yellow
        3: '🟠',  # Orange
        2: '⚪',  # Light gray
        1: '⚪',  # Light gray
        0: '⚫'   # Gray
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
