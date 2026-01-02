"""
BRUTBALL MATCH STATE & DURABILITY CLASSIFIER v1.4 - FIXED VERSION
READ-ONLY MODULE - NO SIDE EFFECTS

FIXED: Now handles missing data gracefully, uses same data as main system
"""

from typing import Dict, Tuple, List, Optional
import pandas as pd


class MatchStateClassifier:
    """
    MATCH STATE & DURABILITY CLASSIFIER (Read-Only) - FIXED
    
    FIXES APPLIED:
    1. Uses same defensive data as bet-ready signals (goals_conceded_last_5)
    2. Handles missing data gracefully
    3. Simplified logic to match main system
    """
    
    # =================== CONFIGURATION CONSTANTS ===================
    
    # Durability thresholds (same as main system)
    DURABILITY_STABLE_THRESHOLD = 1.2  # Both teams ≤ 1.2 for Totals Lock
    DURABILITY_FRAGILE_THRESHOLD = 1.5
    
    # Opponent Under 1.5 threshold (same as bet-ready signals)
    OPPONENT_UNDER_15_THRESHOLD = 1.0  # ≤1.0 avg conceded for defensive strength
    
    # Reliability scoring weights
    RELIABILITY_WEIGHTS = {
        'totals_durability': {
            'STABLE': 2,
            'FRAGILE': 1,
            'NONE': 0
        },
        'under_suggestion': {
            'Under 2.5 recommended': 2,
            'Under 3.5 recommended': 1,
            'No Under recommendation': 0
        },
        'opponent_under_15': {
            True: 1,
            False: 0
        }
    }
    
    # Reliability score mappings
    RELIABILITY_LEVELS = {
        5: {
            'label': 'HIGH CONFIDENCE',
            'description': 'Strong defensive/low-scoring structure',
            'color': 'green',
            'actionable_cue': 'Under 2.5 high probability'
        },
        4: {
            'label': 'MODERATE CONFIDENCE',
            'description': 'Under markets possible, monitor pressure',
            'color': 'yellow',
            'actionable_cue': 'Under 2.5 possible, consider Under 3.5'
        },
        3: {
            'label': 'CAUTION',
            'description': 'Under 3.5 safer option',
            'color': 'orange',
            'actionable_cue': 'Under 3.5 safer, avoid Under 2.5'
        },
        2: {
            'label': 'LOW',
            'description': 'Weak under signal',
            'color': 'lightgray',
            'actionable_cue': 'Weak signal, monitor only'
        },
        1: {
            'label': 'LOW',
            'description': 'Very weak under signal',
            'color': 'lightgray',
            'actionable_cue': 'Very weak signal, informational only'
        },
        0: {
            'label': 'NONE',
            'description': 'No structural under detected',
            'color': 'gray',
            'actionable_cue': 'No under recommendation'
        }
    }
    
    # =================== CORE CLASSIFICATION FUNCTIONS ===================
    
    @staticmethod
    def classify_totals_durability(home_data: Dict, away_data: Dict) -> str:
        """
        CLASSIFY TOTALS DURABILITY - FIXED
        
        Uses same logic as Totals Lock Engine: BOTH teams ≤ 1.2 avg goals
        """
        try:
            # Extract last 5 matches goals scored - HANDLE MISSING DATA
            home_last5_goals = home_data.get('goals_scored_last_5', 0)
            away_last5_goals = away_data.get('goals_scored_last_5', 0)
            
            # Calculate averages (last 5 only)
            home_avg = home_last5_goals / 5 if home_last5_goals > 0 else 0
            away_avg = away_last5_goals / 5 if away_last5_goals > 0 else 0
            
            # Totals Lock condition: BOTH teams ≤ 1.2
            if home_avg <= 1.2 and away_avg <= 1.2:
                return "STABLE"
            elif home_avg <= 1.5 or away_avg <= 1.5:
                return "FRAGILE"
            else:
                return "NONE"
                
        except Exception as e:
            # Graceful degradation
            return "NONE"
    
    @staticmethod
    def classify_opponent_under_15(home_data: Dict, away_data: Dict) -> Dict:
        """
        CLASSIFY OPPONENT UNDER 1.5 - FIXED
        
        Uses same logic as Edge-Derived locks: Team concedes ≤ 1.0 avg goals
        """
        try:
            # Extract last 5 matches goals conceded - SAME AS BET-READY SIGNALS
            home_conceded_last5 = home_data.get('goals_conceded_last_5', 0)
            away_conceded_last5 = away_data.get('goals_conceded_last_5', 0)
            
            # Calculate averages (last 5 only)
            home_avg_conceded = home_conceded_last5 / 5 if home_conceded_last5 > 0 else 0
            away_avg_conceded = away_conceded_last5 / 5 if away_conceded_last5 > 0 else 0
            
            # Check defensive strength (≤1.0 avg conceded)
            home_defense_strong = home_avg_conceded <= 1.0
            away_defense_strong = away_avg_conceded <= 1.0
            
            return {
                # Home Team Perspective: "Can we back Home Team given Away's defense?"
                'home_perspective': {
                    'opponent_under_15': away_defense_strong,  # Away team's defense
                    'opponent_name': 'AWAY_TEAM',
                    'opponent_avg_conceded': away_avg_conceded,
                    'interpretation': f"Away team concedes {away_avg_conceded:.2f} avg (last 5)"
                },
                
                # Away Team Perspective: "Can we back Away Team given Home's defense?"
                'away_perspective': {
                    'opponent_under_15': home_defense_strong,  # Home team's defense
                    'opponent_name': 'HOME_TEAM',
                    'opponent_avg_conceded': home_avg_conceded,
                    'interpretation': f"Home team concedes {home_avg_conceded:.2f} avg (last 5)"
                },
                
                # General defensive strength
                'any_team_defensive_strength': home_defense_strong or away_defense_strong,
                
                # Raw data
                'home_avg_conceded': home_avg_conceded,
                'away_avg_conceded': away_avg_conceded,
                'threshold': 1.0,
                
                # For bet-ready signal compatibility
                'home_defense_strong': home_defense_strong,
                'away_defense_strong': away_defense_strong
            }
            
        except Exception as e:
            # Graceful degradation
            return {
                'home_perspective': {'opponent_under_15': False, 'opponent_avg_conceded': 0},
                'away_perspective': {'opponent_under_15': False, 'opponent_avg_conceded': 0},
                'home_avg_conceded': 0,
                'away_avg_conceded': 0
            }
    
    @staticmethod
    def suggest_under_market(home_data: Dict, away_data: Dict) -> str:
        """
        SUGGEST UNDER MARKET - SIMPLIFIED
        
        Based on totals durability only
        """
        try:
            durability = MatchStateClassifier.classify_totals_durability(home_data, away_data)
            
            if durability == "STABLE":
                return "Under 2.5 recommended"
            elif durability == "FRAGILE":
                return "Under 3.5 recommended"
            else:
                return "No Under recommendation"
                
        except Exception as e:
            return "No Under recommendation"
    
    # =================== RELIABILITY SCORING SYSTEM ===================
    
    @classmethod
    def compute_reliability_score(cls, classifications: Dict, perspective: str = 'home') -> Dict:
        """
        COMPUTE RELIABILITY SCORE (0-5) - SIMPLIFIED
        """
        try:
            # Extract classification values
            totals_durability = classifications.get('totals_durability', 'NONE')
            under_suggestion = classifications.get('under_suggestion', 'No Under recommendation')
            
            # Get opponent signal
            opponent_data = classifications.get('opponent_under_15', {})
            if perspective == 'home':
                opponent_under_15 = opponent_data.get('home_perspective', {}).get('opponent_under_15', False)
            else:
                opponent_under_15 = opponent_data.get('away_perspective', {}).get('opponent_under_15', False)
            
            # Calculate score components
            durability_score = cls.RELIABILITY_WEIGHTS['totals_durability'].get(totals_durability, 0)
            under_score = cls.RELIABILITY_WEIGHTS['under_suggestion'].get(under_suggestion, 0)
            opponent_score = cls.RELIABILITY_WEIGHTS['opponent_under_15'].get(opponent_under_15, 0)
            
            # Total score
            total_score = durability_score + under_score + opponent_score
            
            # Get reliability level details
            reliability_info = cls.RELIABILITY_LEVELS.get(total_score, cls.RELIABILITY_LEVELS[0])
            
            return {
                'reliability_score': total_score,
                'reliability_label': reliability_info['label'],
                'reliability_description': reliability_info['description'],
                'reliability_color': reliability_info['color'],
                'actionable_cue': reliability_info['actionable_cue'],
                'component_scores': {
                    'durability': durability_score,
                    'under_suggestion': under_score,
                    'opponent_under_15': opponent_score
                },
                'perspective_used': perspective,
                'is_read_only': True
            }
            
        except Exception as e:
            # Return minimum score on error
            return {
                'reliability_score': 0,
                'reliability_label': 'ERROR',
                'reliability_description': 'Classification error occurred',
                'reliability_color': 'red',
                'actionable_cue': 'Data error, check inputs',
                'is_read_only': True
            }
    
    # =================== SIMPLIFIED MATCH STATE DETECTION ===================
    
    @staticmethod
    def detect_match_state(home_data: Dict, away_data: Dict) -> str:
        """
        SIMPLIFIED MATCH STATE DETECTION
        
        Only checks for obvious states based on available data
        """
        try:
            # Get defensive data
            home_conceded = home_data.get('goals_conceded_last_5', 0) / 5
            away_conceded = away_data.get('goals_conceded_last_5', 0) / 5
            home_scored = home_data.get('goals_scored_last_5', 0) / 5
            away_scored = away_data.get('goals_scored_last_5', 0) / 5
            
            # Check for low-scoring match
            if home_scored <= 1.0 and away_scored <= 1.0:
                return "LOW_SCORING_TREND"
            
            # Check for defensive strength
            if home_conceded <= 0.8 or away_conceded <= 0.8:
                return "DEFENSIVE_STRENGTH"
            
            # Default state
            return "NEUTRAL"
            
        except Exception as e:
            return "DATA_UNAVAILABLE"
    
    # =================== MAIN CLASSIFICATION FUNCTION ===================
    
    @classmethod
    def classify_match_state(cls, home_data: Dict, away_data: Dict) -> Dict:
        """
        MAIN CLASSIFICATION FUNCTION - FIXED & SIMPLIFIED
        
        Returns ALL classifications with graceful error handling
        """
        try:
            # ========== 1. TOTALS DURABILITY ==========
            totals_durability = cls.classify_totals_durability(home_data, away_data)
            
            # ========== 2. OPPONENT UNDER 1.5 ==========
            opponent_under_15 = cls.classify_opponent_under_15(home_data, away_data)
            
            # ========== 3. UNDER MARKET SUGGESTIONS ==========
            under_suggestion = cls.suggest_under_market(home_data, away_data)
            
            # ========== 4. MATCH STATE ==========
            match_state = cls.detect_match_state(home_data, away_data)
            
            # ========== 5. RELIABILITY SCORING ==========
            reliability_home = cls.compute_reliability_score({
                'totals_durability': totals_durability,
                'under_suggestion': under_suggestion,
                'opponent_under_15': opponent_under_15
            }, perspective='home')
            
            reliability_away = cls.compute_reliability_score({
                'totals_durability': totals_durability,
                'under_suggestion': under_suggestion,
                'opponent_under_15': opponent_under_15
            }, perspective='away')
            
            # ========== 6. RETURN RESULTS ==========
            return {
                # Core Classifications
                'totals_durability': totals_durability,
                'under_suggestion': under_suggestion,
                'opponent_under_15': opponent_under_15,
                'dominant_state': match_state,
                
                # Reliability Scoring
                'reliability_home': reliability_home,
                'reliability_away': reliability_away,
                
                # Data for display
                'averages': {
                    'home_goals_avg': home_data.get('goals_scored_last_5', 0) / 5,
                    'away_goals_avg': away_data.get('goals_scored_last_5', 0) / 5,
                    'home_conceded_avg': opponent_under_15.get('home_avg_conceded', 0),
                    'away_conceded_avg': opponent_under_15.get('away_avg_conceded', 0)
                },
                
                # Metadata
                'is_read_only': True,
                'classification_success': True,
                'metadata': {
                    'version': '1.4',
                    'data_source': 'last_5_matches',
                    'simplified_logic': True
                }
            }
            
        except Exception as e:
            # Return error result
            return {
                'totals_durability': 'NONE',
                'under_suggestion': 'No Under recommendation',
                'opponent_under_15': {
                    'home_perspective': {'opponent_under_15': False, 'opponent_avg_conceded': 0},
                    'away_perspective': {'opponent_under_15': False, 'opponent_avg_conceded': 0},
                    'home_avg_conceded': 0,
                    'away_avg_conceded': 0
                },
                'dominant_state': 'CLASSIFIER_ERROR',
                'reliability_home': {
                    'reliability_score': 0,
                    'reliability_label': 'ERROR',
                    'reliability_description': 'Classifier error occurred',
                    'is_read_only': True
                },
                'reliability_away': {
                    'reliability_score': 0,
                    'reliability_label': 'ERROR',
                    'reliability_description': 'Classifier error occurred',
                    'is_read_only': True
                },
                'averages': {
                    'home_goals_avg': 0,
                    'away_goals_avg': 0,
                    'home_conceded_avg': 0,
                    'away_conceded_avg': 0
                },
                'is_read_only': True,
                'classification_success': False,
                'error_message': str(e)
            }


# =================== INTEGRATION HELPER FUNCTIONS ===================

def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
    """
    SAFE INTEGRATION HELPER - MAIN ENTRY POINT
    
    Uses fixed classifier that handles missing data gracefully
    """
    return MatchStateClassifier.classify_match_state(home_data, away_data)


def format_reliability_badge(reliability_data: Dict) -> str:
    """
    FORMAT RELIABILITY SCORE AS UI BADGE
    """
    score = reliability_data.get('reliability_score', 0)
    label = reliability_data.get('reliability_label', 'NONE')
    
    # Emoji mapping
    emoji_map = {
        5: '🟢',  # Green
        4: '🟡',  # Yellow
        3: '🟠',  # Orange
        2: '⚪',  # Light gray
        1: '⚪',  # Light gray
        0: '⚫'   # Gray
    }
    
    emoji = emoji_map.get(score, '⚫')
    
    # Return formatted badge
    return f"{emoji} **Reliability: {label} ({score}/5)**"


def format_durability_indicator(durability: str) -> str:
    """
    FORMAT DURABILITY AS UI INDICATOR
    """
    indicators = {
        'STABLE': '🟢 STABLE',
        'FRAGILE': '🟡 FRAGILE',
        'NONE': '⚫ NONE'
    }
    return indicators.get(durability, '⚫ NONE')
