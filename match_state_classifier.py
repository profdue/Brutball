import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

class MatchStateClassifier:
    """
    STATE & DURABILITY CLASSIFIER v1.0
    READ-ONLY PRE-MATCH INTELLIGENCE LAYER
    
    CRITICAL PRINCIPLES:
    1. Uses ONLY last-5 matches data
    2. NO season averages or external assumptions
    3. Does NOT affect betting logic, stakes, or existing tiers
    4. Mathematically consistent with v6.3 architecture
    """
    
    # State configurations
    STATE_CONFIG = {
        'STAGNATION': {
            'label': 'Stagnation Match',
            'emoji': '🌀',
            'description': 'Both teams low-scoring, high defensive stability',
            'totals_suggestion': 'STRONG UNDER 2.5'
        },
        'SUPPRESSION': {
            'label': 'One-Sided Suppression',
            'emoji': '🔒',
            'description': 'One team dominates, other suppressed',
            'totals_suggestion': 'MODERATE UNDER 2.5'
        },
        'DELAYED_EXPLOSION': {
            'label': 'Delayed Explosion Risk',
            'emoji': '💣',
            'description': 'Both capable of scoring, timing risk',
            'totals_suggestion': 'UNDER 3.5'
        },
        'EXPLOSION': {
            'label': 'High-Scoring Explosion',
            'emoji': '💥',
            'description': 'Both teams high-scoring, defensive weakness',
            'totals_suggestion': 'OVER 2.5'
        },
        'NEUTRAL': {
            'label': 'Neutral State',
            'emoji': '⚖️',
            'description': 'Balanced match, no clear pattern',
            'totals_suggestion': 'NO STRONG TOTALS BIAS'
        }
    }
    
    @staticmethod
    def calculate_averages_from_last5(home_data: Dict, away_data: Dict) -> Dict:
        """Calculate averages from last 5 matches data ONLY."""
        try:
            # Safely extract and calculate
            home_goals = home_data.get('goals_scored_last_5')
            home_conceded = home_data.get('goals_conceded_last_5')
            away_goals = away_data.get('goals_scored_last_5')
            away_conceded = away_data.get('goals_conceded_last_5')
            
            # Type safety check
            if any(not isinstance(x, (int, float, np.integer, np.floating)) 
                   for x in [home_goals, home_conceded, away_goals, away_conceded]):
                return {'classification_error': True, 'error_message': 'Type mismatch in last-5 data'}
            
            # Calculate averages (last 5 matches)
            home_goals_avg = home_goals / 5 if home_goals is not None else 0
            home_conceded_avg = home_conceded / 5 if home_conceded is not None else 0
            away_goals_avg = away_goals / 5 if away_goals is not None else 0
            away_conceded_avg = away_conceded / 5 if away_conceded is not None else 0
            
            return {
                'home_goals_avg': round(home_goals_avg, 2),
                'home_conceded_avg': round(home_conceded_avg, 2),
                'away_goals_avg': round(away_goals_avg, 2),
                'away_conceded_avg': round(away_conceded_avg, 2),
                'classification_error': False
            }
        except Exception as e:
            return {'classification_error': True, 'error_message': f'Calculation error: {str(e)}'}
    
    @staticmethod
    def determine_dominant_state(averages: Dict) -> str:
        """Determine match state based on last-5 averages."""
        try:
            hg = averages.get('home_goals_avg', 0)
            hc = averages.get('home_conceded_avg', 0)
            ag = averages.get('away_goals_avg', 0)
            ac = averages.get('away_conceded_avg', 0)
            
            # STAGNATION: Both teams low-scoring (≤1.2) AND low-conceding (≤1.0)
            if hg <= 1.2 and hc <= 1.0 and ag <= 1.2 and ac <= 1.0:
                return 'STAGNATION'
            
            # SUPPRESSION: One team low-conceding (≤0.8) AND opponent low-scoring (≤1.0)
            if hc <= 0.8 and ag <= 1.0:
                return 'SUPPRESSION'
            if ac <= 0.8 and hg <= 1.0:
                return 'SUPPRESSION'
            
            # EXPLOSION: Both teams high-scoring (≥1.6) OR high-conceding (≥1.6)
            if (hg >= 1.6 or hc >= 1.6) and (ag >= 1.6 or ac >= 1.6):
                return 'EXPLOSION'
            
            # DELAYED_EXPLOSION: Moderate scoring (1.2-1.6) with defensive concerns
            if (1.2 <= hg <= 1.6 or 1.2 <= hc <= 1.6) and (1.2 <= ag <= 1.6 or 1.2 <= ac <= 1.6):
                return 'DELAYED_EXPLOSION'
            
            return 'NEUTRAL'
        except:
            return 'NEUTRAL'
    
    @staticmethod
    def calculate_totals_durability(averages: Dict) -> Dict:
        """Calculate totals durability score and classification."""
        try:
            hg = averages.get('home_goals_avg', 0)
            hc = averages.get('home_conceded_avg', 0)
            ag = averages.get('away_goals_avg', 0)
            ac = averages.get('away_conceded_avg', 0)
            
            # Base durability score (0-10)
            durability_score = 0
            
            # Factors that INCREASE durability (lower scoring = more durable)
            if hg <= 1.0: durability_score += 2
            if hc <= 1.0: durability_score += 2
            if ag <= 1.0: durability_score += 2
            if ac <= 1.0: durability_score += 2
            
            # Factors that DECREASE durability (higher scoring = less durable)
            if hg >= 1.6: durability_score -= 2
            if hc >= 1.6: durability_score -= 2
            if ag >= 1.6: durability_score -= 2
            if ac >= 1.6: durability_score -= 2
            
            # Ensure score stays within bounds
            durability_score = max(0, min(10, durability_score))
            
            # Classify
            if durability_score >= 6:
                durability_class = 'STABLE'
                emoji = '🟢'
            elif durability_score >= 3:
                durability_class = 'FRAGILE'
                emoji = '🟡'
            else:
                durability_class = 'NONE'
                emoji = '🔴'
            
            return {
                'score': durability_score,
                'class': durability_class,
                'emoji': emoji,
                'code': f"{durability_class}_{durability_score}"
            }
        except:
            return {'score': 0, 'class': 'ERROR', 'emoji': '❌', 'code': 'ERROR_0'}
    
    @staticmethod
    def generate_under_suggestion(averages: Dict, state: str) -> str:
        """Generate UNDER market suggestion based on state and averages."""
        try:
            hg = averages.get('home_goals_avg', 0)
            hc = averages.get('home_conceded_avg', 0)
            ag = averages.get('away_goals_avg', 0)
            ac = averages.get('away_conceded_avg', 0)
            
            # Strong UNDER conditions
            if state == 'STAGNATION':
                return f"STRONG UNDER 2.5 (both teams ≤1.2 goals scored)"
            
            if state == 'SUPPRESSION':
                if hc <= 0.8 and ag <= 1.0:
                    return f"UNDER 2.5 (home concedes {hc:.1f}, away scores {ag:.1f})"
                if ac <= 0.8 and hg <= 1.0:
                    return f"UNDER 2.5 (away concedes {ac:.1f}, home scores {hg:.1f})"
            
            # Moderate UNDER conditions
            if hg <= 1.2 and ag <= 1.2:
                return f"MODERATE UNDER 2.5 (both teams low-scoring)"
            
            # Check for individual team defensive strength (for UNDER 1.5)
            if hc <= 1.0:
                return f"CONSIDER {averages.get('home_team', 'Home')} OPPONENT UNDER 1.5 (concedes {hc:.1f})"
            if ac <= 1.0:
                return f"CONSIDER {averages.get('away_team', 'Away')} OPPONENT UNDER 1.5 (concedes {ac:.1f})"
            
            return "NO STRONG UNDER MARKET"
        except:
            return "ERROR GENERATING SUGGESTION"
    
    @staticmethod
    def calculate_reliability(averages: Dict) -> Dict:
        """Calculate reliability score (0-5) for the classification."""
        try:
            reliability_score = 0
            
            # Data completeness check
            required_fields = ['home_goals_avg', 'home_conceded_avg', 'away_goals_avg', 'away_conceded_avg']
            if all(field in averages for field in required_fields):
                reliability_score += 1
            
            # Data quality check (no extreme outliers)
            for field in required_fields:
                value = averages.get(field, 0)
                if 0 <= value <= 5:  # Reasonable range for goals per match
                    reliability_score += 1
            
            # Pattern consistency check
            hg = averages.get('home_goals_avg', 0)
            hc = averages.get('home_conceded_avg', 0)
            ag = averages.get('away_goals_avg', 0)
            ac = averages.get('away_conceded_avg', 0)
            
            # Check if patterns are internally consistent
            if (hg <= 1.2 and ag <= 1.2) or (hg >= 1.6 and ag >= 1.6):
                reliability_score += 1
            
            if (hc <= 1.0 and ac <= 1.0) or (hc >= 1.6 and ac >= 1.6):
                reliability_score += 1
            
            # Cap at 5
            reliability_score = min(5, reliability_score)
            
            # Label mapping
            labels = {
                5: 'EXCELLENT',
                4: 'HIGH',
                3: 'MODERATE',
                2: 'LOW',
                1: 'VERY LOW',
                0: 'UNRELIABLE'
            }
            
            return {
                'reliability_score': reliability_score,
                'reliability_label': labels.get(reliability_score, 'UNKNOWN'),
                'data_points': 4  # home_goals, home_conceded, away_goals, away_conceded
            }
        except:
            return {'reliability_score': 0, 'reliability_label': 'ERROR', 'data_points': 0}
    
    @staticmethod
    def check_defensive_strength(averages: Dict) -> Dict:
        """Check which team has defensive strength for UNDER 1.5 markets."""
        try:
            hc = averages.get('home_conceded_avg', 0)
            ac = averages.get('away_conceded_avg', 0)
            
            home_strong_defense = hc <= 1.0
            away_strong_defense = ac <= 1.0
            
            suggestions = []
            if home_strong_defense:
                suggestions.append(f"Home team concedes {hc:.2f} avg ≤ 1.0 → Opponent UNDER 1.5")
            if away_strong_defense:
                suggestions.append(f"Away team concedes {ac:.2f} avg ≤ 1.0 → Opponent UNDER 1.5")
            
            return {
                'home_strong_defense': home_strong_defense,
                'away_strong_defense': away_strong_defense,
                'suggestions': suggestions,
                'strong_defense_count': sum([home_strong_defense, away_strong_defense])
            }
        except:
            return {
                'home_strong_defense': False,
                'away_strong_defense': False,
                'suggestions': ['Error in defensive analysis'],
                'strong_defense_count': 0
            }
    
    @staticmethod
    def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
        """Main function: Get complete classification from last-5 data."""
        
        result = {
            'classification_error': True,
            'error_message': 'Initialization error',
            'missing_fields': [],
            'type_errors': []
        }
        
        try:
            # Check for required fields
            required_fields = ['goals_scored_last_5', 'goals_conceded_last_5']
            missing_home = [f for f in required_fields if f not in home_data]
            missing_away = [f for f in required_fields if f not in away_data]
            
            if missing_home or missing_away:
                result['missing_fields'] = missing_home + missing_away
                result['error_message'] = f"Missing required fields: {result['missing_fields']}"
                return result
            
            # Check data types
            type_errors = []
            for field in required_fields:
                if not isinstance(home_data.get(field), (int, float, np.integer, np.floating)):
                    type_errors.append(f"home.{field}: {type(home_data.get(field))}")
                if not isinstance(away_data.get(field), (int, float, np.integer, np.floating)):
                    type_errors.append(f"away.{field}: {type(away_data.get(field))}")
            
            if type_errors:
                result['type_errors'] = type_errors
                result['error_message'] = f"Type errors: {type_errors}"
                return result
            
            # Calculate averages from last 5
            averages = MatchStateClassifier.calculate_averages_from_last5(home_data, away_data)
            
            if averages.get('classification_error', True):
                result['error_message'] = averages.get('error_message', 'Average calculation failed')
                return result
            
            # Determine dominant state
            dominant_state = MatchStateClassifier.determine_dominant_state(averages)
            
            # Calculate totals durability
            durability = MatchStateClassifier.calculate_totals_durability(averages)
            
            # Generate UNDER suggestion
            under_suggestion = MatchStateClassifier.generate_under_suggestion(averages, dominant_state)
            
            # Calculate reliability
            reliability = MatchStateClassifier.calculate_reliability(averages)
            
            # Check defensive strength
            defensive_analysis = MatchStateClassifier.check_defensive_strength(averages)
            
            # Get state config
            state_config = MatchStateClassifier.STATE_CONFIG.get(
                dominant_state, 
                MatchStateClassifier.STATE_CONFIG['NEUTRAL']
            )
            
            # Prepare complete result
            result = {
                'classification_error': False,
                'averages': averages,
                'dominant_state': dominant_state,
                'state_config': state_config,
                'totals_durability': durability,
                'under_suggestion': under_suggestion,
                'reliability': reliability,
                'defensive_analysis': defensive_analysis,
                'calculation_timestamp': pd.Timestamp.now().isoformat(),
                'data_source': 'LAST_5_MATCHES_ONLY'
            }
            
            return result
            
        except Exception as e:
            result['error_message'] = f"Classification error: {str(e)}"
            return result
    
    @staticmethod
    def create_ui_display_data(classification_result: Dict) -> Dict:
        """Format classification result for UI display."""
        if classification_result.get('classification_error', True):
            return {
                'display_type': 'ERROR',
                'error_message': classification_result.get('error_message', 'Unknown error')
            }
        
        return {
            'display_type': 'CLASSIFICATION',
            'averages': classification_result.get('averages', {}),
            'match_state': classification_result.get('state_config', {}),
            'durability': classification_result.get('totals_durability', {}),
            'under_suggestion': classification_result.get('under_suggestion', ''),
            'reliability': classification_result.get('reliability', {}),
            'defensive_analysis': classification_result.get('defensive_analysis', {})
        }

def format_reliability_badge(reliability_data: Dict) -> str:
    """Format reliability as a badge."""
    score = reliability_data.get('reliability_score', 0)
    label = reliability_data.get('reliability_label', 'NONE')
    
    emoji_map = {
        5: '🟢', 4: '🟡', 3: '🟠', 2: '⚪', 1: '⚪', 0: '⚫'
    }
    
    emoji = emoji_map.get(score, '⚫')
    return f"{emoji} **Reliability: {label} ({score}/5)**"

def format_durability_indicator(durability_code: str) -> str:
    """Format durability indicator."""
    if 'STABLE' in durability_code:
        return f"🟢 {durability_code}"
    elif 'FRAGILE' in durability_code:
        return f"🟡 {durability_code}"
    elif 'NONE' in durability_code:
        return f"🔴 {durability_code}"
    else:
        return f"⚪ {durability_code}"
