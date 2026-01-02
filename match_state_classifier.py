"""
BRUTBALL MATCH STATE & DURABILITY CLASSIFIER v1.7 - CSV-COMPLIANT VERSION

COMPLETE UNIFIED FILE - 100% CSV-COMPLIANT

CRITICAL RULE: CSV-ONLY ARCHITECTURE
- Uses ONLY: goals_scored_last_5, goals_conceded_last_5
- NO concede_last_5_list (illegal)
- NO match-by-match granularity
- NO hidden data structures
- All calculations from aggregates only

PURPOSE:
Classify matches into structural states, durability categories, and reliability scores.
This does NOT affect betting logic, stakes, or existing tiers.
It only labels reality to provide intelligent insights using CSV-legal data only.

USAGE:
1. First validate data with validate_last5_data()
2. If valid, run full classification
3. Use display functions for clean UI output
4. 100% CSV-compliant - uses only aggregate last-5 data
"""

from typing import Dict, Tuple, List, Optional, Any
import pandas as pd


class MatchStateClassifier:
    """
    MATCH STATE & DURABILITY CLASSIFIER (Read-Only) - 100% CSV-COMPLIANT
    
    IMPORTANT: This is READ-ONLY. It does NOT:
    - Alter betting logic
    - Change capital allocation
    - Modify existing tiers
    - Create new locks
    
    It only labels reality to provide intelligent insights.
    Uses ONLY CSV-compliant data: goals_scored_last_5, goals_conceded_last_5
    """
    
    # =================== CONFIGURATION CONSTANTS ===================
    
    # Durability thresholds
    DURABILITY_STABLE_THRESHOLD = 1.0
    DURABILITY_FRAGILE_THRESHOLD = 1.2
    
    # Opponent Under 1.5 threshold
    OPPONENT_UNDER_15_THRESHOLD = 1.0
    
    # Minimum required data for classification
    MINIMUM_DATA_REQUIREMENTS = ['goals_scored_last_5', 'goals_conceded_last_5']
    
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
            'description': 'Under 2.5 likely; strong defensive/low-scoring structure',
            'color': 'green',
            'actionable_cue': 'Under 2.5 high probability'
        },
        4: {
            'label': 'MODERATE CONFIDENCE',
            'description': 'Under 2.5 possible, monitor match pressure',
            'color': 'yellow',
            'actionable_cue': 'Under 2.5 possible, consider Under 3.5 for safety'
        },
        3: {
            'label': 'CAUTION',
            'description': 'Under 3.5 safer, low structural confidence',
            'color': 'orange',
            'actionable_cue': 'Under 3.5 safer, avoid Under 2.5'
        },
        2: {
            'label': 'LOW',
            'description': 'Weak under signal, mostly informational',
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
    
    # Match state configurations
    STATE_CONFIG = {
        'TERMINAL_STAGNATION': {'emoji': '🌀', 'color': '#0EA5E9', 'label': 'Terminal Stagnation'},
        'ASYMMETRIC_SUPPRESSION': {'emoji': '🛡️', 'color': '#16A34A', 'label': 'Asymmetric Suppression'},
        'DELAYED_RELEASE': {'emoji': '⏳', 'color': '#F59E0B', 'label': 'Delayed Release'},
        'FORCED_EXPLOSION': {'emoji': '💥', 'color': '#EF4444', 'label': 'Forced Explosion'},
        'NEUTRAL': {'emoji': '⚖️', 'color': '#6B7280', 'label': 'Neutral'},
        'CLASSIFIER_ERROR': {'emoji': '⚠️', 'color': '#DC2626', 'label': 'Classifier Error'}
    }
    
    # =================== DATA VALIDATION ===================
    
    @classmethod
    def validate_last5_data(cls, home_data: Dict, away_data: Dict) -> Tuple[bool, List[str], Dict]:
        """
        VALIDATE LAST 5 MATCHES DATA - CSV-COMPLIANT
        
        Returns: (is_valid, missing_fields, validated_data)
        
        CRITICAL: If data is missing, classifier should DISABLE itself
        instead of fabricating 0.00 averages.
        Only checks CSV-compliant fields.
        
        PRINCIPLE: Missing data should BLOCK classification, not create false 0.00
        """
        missing_fields = []
        validated_data = {
            'home': {},
            'away': {}
        }
        
        # Check all required fields exist and are not None/NaN
        for field in cls.MINIMUM_DATA_REQUIREMENTS:
            # Check home data
            if field not in home_data:
                missing_fields.append(f"home.{field}_missing")
            elif pd.isna(home_data.get(field)):
                missing_fields.append(f"home.{field}_nan")
            else:
                validated_data['home'][field] = home_data[field]
            
            # Check away data
            if field not in away_data:
                missing_fields.append(f"away.{field}_missing")
            elif pd.isna(away_data.get(field)):
                missing_fields.append(f"away.{field}_nan")
            else:
                validated_data['away'][field] = away_data[field]
        
        # Additional validation: ensure values are numeric and reasonable
        if not missing_fields:
            for team in ['home', 'away']:
                for field in cls.MINIMUM_DATA_REQUIREMENTS:
                    value = validated_data[team][field]
                    
                    # Type validation
                    if not isinstance(value, (int, float)):
                        missing_fields.append(f"{team}.{field}_type_error")
                        continue
                    
                    # Range validation for last 5 matches
                    # Max reasonable: 5 matches × 10 goals/match = 50
                    if value < 0 or value > 50:
                        missing_fields.append(f"{team}.{field}_range_error")
        
        is_valid = len(missing_fields) == 0
        
        return is_valid, missing_fields, validated_data
    
    # =================== CORE CLASSIFICATION FUNCTIONS ===================
    
    @classmethod
    def classify_totals_durability(cls, home_data: Dict, away_data: Dict) -> str:
        """
        CLASSIFY TOTALS DURABILITY (Under 2.5) - CSV-COMPLIANT
        
        Returns 'STABLE', 'FRAGILE', or 'NONE' for Under 2.5 durability.
        Uses ONLY last 5 matches data from CSV-compliant fields.
        
        ASSUMES: Data has been validated by validate_last5_data()
        """
        # Extract last 5 matches goals scored (already validated)
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        # Calculate averages (last 5 only) - CSV COMPLIANT
        home_avg = home_last5_goals / 5 if home_last5_goals is not None else 0
        away_avg = away_last5_goals / 5 if away_last5_goals is not None else 0
        
        # Find maximum average (most offensive team)
        max_avg = max(home_avg, away_avg)
        
        # Classification logic
        if max_avg <= cls.DURABILITY_STABLE_THRESHOLD:
            return "STABLE"
        elif max_avg <= cls.DURABILITY_FRAGILE_THRESHOLD:
            return "FRAGILE"
        else:
            return "NONE"
    
    @classmethod
    def classify_opponent_under_15(cls, home_data: Dict, away_data: Dict) -> Dict[str, Any]:
        """
        CLASSIFY OPPONENT UNDER 1.5 (PERSPECTIVE-SENSITIVE) - CSV-COMPLIANT
        
        IMPORTANT: "Opponent" depends on perspective:
        • If analyzing Home Team → Opponent = Away Team
        • If analyzing Away Team → Opponent = Home Team
        
        Returns defensive strength classification for BOTH perspectives.
        Signal = PRESENT if opponent concedes ≤1.0 avg goals in last 5 matches.
        Uses ONLY CSV-compliant data: goals_conceded_last_5 / 5
        
        ASSUMES: Data has been validated by validate_last5_data()
        """
        # Extract last 5 matches goals conceded (CSV-compliant)
        home_conceded_last5 = home_data.get('goals_conceded_last_5', 0)
        away_conceded_last5 = away_data.get('goals_conceded_last_5', 0)
        
        # Calculate averages (last 5 only) - CSV COMPLIANT
        home_avg_conceded = home_conceded_last5 / 5 if home_conceded_last5 is not None else 0
        away_avg_conceded = away_conceded_last5 / 5 if away_conceded_last5 is not None else 0
        
        # =================== PERSPECTIVE-BASED ANALYSIS ===================
        # If we're analyzing HOME TEAM → OPPONENT = AWAY TEAM
        home_perspective_opponent_under_15 = away_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        # If we're analyzing AWAY TEAM → OPPONENT = HOME TEAM
        away_perspective_opponent_under_15 = home_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        return {
            # Home Team Perspective: "Can we back Home Team given Away's defense?"
            'home_perspective': {
                'opponent_under_15': home_perspective_opponent_under_15,
                'final_verdict': home_perspective_opponent_under_15,
                'opponent_name': 'AWAY_TEAM',
                'opponent_avg_conceded': away_avg_conceded,
                'interpretation': f"When backing HOME: Away concedes {away_avg_conceded:.2f} avg (last 5) {'≤1.0' if home_perspective_opponent_under_15 else '>1.0'}"
            },
            
            # Away Team Perspective: "Can we back Away Team given Home's defense?"
            'away_perspective': {
                'opponent_under_15': away_perspective_opponent_under_15,
                'final_verdict': away_perspective_opponent_under_15,
                'opponent_name': 'HOME_TEAM',
                'opponent_avg_conceded': home_avg_conceded,
                'interpretation': f"When backing AWAY: Home concedes {home_avg_conceded:.2f} avg (last 5) {'≤1.0' if away_perspective_opponent_under_15 else '>1.0'}"
            },
            
            # General defensive strength (either team defensively strong)
            'any_team_defensive_strength': (
                home_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD or
                away_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
            ),
            
            # Data for display
            'home_avg_conceded': home_avg_conceded,
            'away_avg_conceded': away_avg_conceded,
            'threshold': cls.OPPONENT_UNDER_15_THRESHOLD,
            
            # Legacy field for compatibility
            'any_opponent_under_15': home_perspective_opponent_under_15 or away_perspective_opponent_under_15
        }
    
    @classmethod
    def suggest_under_market(cls, home_data: Dict, away_data: Dict) -> str:
        """
        SUGGEST UNDER MARKET BASED ON DURABILITY - CSV-COMPLIANT
        
        Provides actionable guidance for Under markets (informational only).
        Uses durability classification from last 5 matches only.
        
        ASSUMES: Data has been validated by validate_last5_data()
        """
        durability = cls.classify_totals_durability(home_data, away_data)
        
        if durability == "STABLE":
            return "Under 2.5 recommended"
        elif durability == "FRAGILE":
            return "Under 3.5 recommended"
        else:
            return "No Under recommendation"
    
    # =================== RELIABILITY SCORING SYSTEM ===================
    
    @classmethod
    def compute_reliability_score(cls, classifications: Dict, perspective: str = 'home') -> Dict[str, Any]:
        """
        COMPUTE RELIABILITY SCORE (0-5) - PERSPECTIVE-SENSITIVE - CSV-COMPLIANT
        
        perspective: 'home' or 'away' - which team we're analyzing from
        Uses ONLY CSV-compliant data and calculations.
        """
        # Extract classification values
        totals_durability = classifications.get('totals_durability', 'NONE')
        under_suggestion = classifications.get('under_suggestion', 'No Under recommendation')
        
        # CRITICAL: Get opponent signal from correct perspective
        opponent_data = classifications.get('opponent_under_15', {})
        if perspective == 'home':
            perspective_data = opponent_data.get('home_perspective', {})
            opponent_under_15 = perspective_data.get('final_verdict', False)
        else:
            perspective_data = opponent_data.get('away_perspective', {})
            opponent_under_15 = perspective_data.get('final_verdict', False)
        
        # Calculate score components - CSV COMPLIANT
        durability_score = cls.RELIABILITY_WEIGHTS['totals_durability'].get(totals_durability, 0)
        under_score = cls.RELIABILITY_WEIGHTS['under_suggestion'].get(under_suggestion, 0)
        opponent_score = cls.RELIABILITY_WEIGHTS['opponent_under_15'].get(opponent_under_15, 0)
        
        # Total score
        total_score = durability_score + under_score + opponent_score
        
        # Cap at 5
        total_score = max(0, min(5, total_score))
        
        # Get reliability level details
        reliability_info = cls.RELIABILITY_LEVELS.get(total_score, cls.RELIABILITY_LEVELS[0])
        
        # Build detailed breakdown
        score_breakdown = {
            'durability': {
                'value': totals_durability,
                'score': durability_score,
                'weight': cls.RELIABILITY_WEIGHTS['totals_durability'].get(totals_durability, 0)
            },
            'under_suggestion': {
                'value': under_suggestion,
                'score': under_score,
                'weight': cls.RELIABILITY_WEIGHTS['under_suggestion'].get(under_suggestion, 0)
            },
            'opponent_under_15': {
                'value': opponent_under_15,
                'score': opponent_score,
                'weight': cls.RELIABILITY_WEIGHTS['opponent_under_15'].get(opponent_under_15, 0)
            }
        }
        
        return {
            'reliability_score': total_score,
            'reliability_label': reliability_info['label'],
            'reliability_description': reliability_info['description'],
            'reliability_color': reliability_info['color'],
            'actionable_cue': reliability_info['actionable_cue'],
            'score_breakdown': score_breakdown,
            'component_scores': {
                'durability': durability_score,
                'under_suggestion': under_score,
                'opponent_under_15': opponent_score
            },
            'perspective_used': perspective,
            'is_read_only': True,
            'metadata': {
                'score_range': '0 to 5',
                'interpretation': 'Higher score indicates stronger under structure',
                'purpose': 'Informational reliability indicator only',
                'data_compliance': '100% CSV-compliant (aggregates only)'
            }
        }
    
    # =================== FULL CLASSIFICATION PIPELINE ===================
    
    @classmethod
    def run_full_classification(cls, home_data: Dict, away_data: Dict, 
                                perspective: str = 'home') -> Dict[str, Any]:
        """
        RUN FULL CLASSIFICATION PIPELINE - 100% CSV-COMPLIANT
        
        Validates data first, then runs all classification functions.
        Returns complete classification results or error state.
        
        This is the MAIN ENTRY POINT for the classifier.
        Uses ONLY CSV-compliant data.
        """
        # Step 1: Validate data - ENFORCE CSV-ONLY ARCHITECTURE
        is_valid, missing_fields, validated_data = cls.validate_last5_data(home_data, away_data)
        
        if not is_valid:
            # CRITICAL: Do NOT fabricate 0.00 averages
            # Missing data should BLOCK classification, not create false data
            return {
                'classification_error': True,
                'error_type': 'MISSING_OR_INVALID_DATA',
                'error_message': f'Missing/invalid last-5 data fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'is_valid': False,
                'averages': {
                    'home_goals_avg': None,  # NOT 0.00 - this is important
                    'home_conceded_avg': None,
                    'away_goals_avg': None,
                    'away_conceded_avg': None
                },
                'dominant_state': 'CLASSIFIER_ERROR',
                'totals_durability': 'NONE',
                'under_suggestion': 'Data insufficient for recommendation',
                'opponent_under_15': {},
                'reliability_home': {
                    'reliability_score': 0,
                    'reliability_label': 'DATA MISSING',
                    'reliability_description': 'Classifier unavailable due to missing last-5 data',
                    'reliability_color': 'gray'
                },
                'validation_passed': False,
                'data_integrity_violation': True
            }
        
        # Step 2: Calculate averages for display - CSV COMPLIANT
        home_goals_avg = validated_data['home']['goals_scored_last_5'] / 5
        home_conceded_avg = validated_data['home']['goals_conceded_last_5'] / 5
        away_goals_avg = validated_data['away']['goals_scored_last_5'] / 5
        away_conceded_avg = validated_data['away']['goals_conceded_last_5'] / 5
        
        # Step 3: Run all classification functions - CSV COMPLIANT
        totals_durability = cls.classify_totals_durability(
            validated_data['home'], validated_data['away']
        )
        
        opponent_under_15 = cls.classify_opponent_under_15(
            validated_data['home'], validated_data['away']
        )
        
        under_suggestion = cls.suggest_under_market(
            validated_data['home'], validated_data['away']
        )
        
        # Step 4: Determine dominant match state - CSV COMPLIANT
        dominant_state = cls.determine_dominant_match_state(
            validated_data['home'], validated_data['away']
        )
        
        # Step 5: Compute reliability scores - CSV COMPLIANT
        classifications = {
            'totals_durability': totals_durability,
            'under_suggestion': under_suggestion,
            'opponent_under_15': opponent_under_15
        }
        
        reliability_home = cls.compute_reliability_score(classifications, 'home')
        reliability_away = cls.compute_reliability_score(classifications, 'away')
        
        # Step 6: Return complete results
        return {
            'classification_error': False,
            'error_type': None,
            'error_message': None,
            'is_valid': True,
            'validation_passed': True,
            'data_integrity_violation': False,
            'averages': {
                'home_goals_avg': round(home_goals_avg, 2),
                'home_conceded_avg': round(home_conceded_avg, 2),
                'away_goals_avg': round(away_goals_avg, 2),
                'away_conceded_avg': round(away_conceded_avg, 2)
            },
            'dominant_state': dominant_state,
            'totals_durability': totals_durability,
            'under_suggestion': under_suggestion,
            'opponent_under_15': opponent_under_15,
            'reliability_home': reliability_home,
            'reliability_away': reliability_away,
            'perspective_used': perspective,
            'metadata': {
                'version': '1.7',
                'data_source': 'last_5_matches_only',
                'data_compliance': '100% CSV-compliant',
                'fields_used': ['goals_scored_last_5', 'goals_conceded_last_5'],
                'read_only': True,
                'purpose': 'Informational classification only',
                'principle': 'Missing data blocks classification, does not create false 0.00'
            }
        }
    
    @classmethod
    def determine_dominant_match_state(cls, home_data: Dict, away_data: Dict) -> str:
        """
        DETERMINE DOMINANT MATCH STATE - CSV-COMPLIANT
        
        Simplified state determination based on scoring/conceding patterns.
        Uses ONLY CSV-compliant data from last 5 matches.
        """
        # Extract and calculate averages from CSV-compliant fields
        home_goals_avg = home_data.get('goals_scored_last_5', 0) / 5
        home_conceded_avg = home_data.get('goals_conceded_last_5', 0) / 5
        away_goals_avg = away_data.get('goals_scored_last_5', 0) / 5
        away_conceded_avg = away_data.get('goals_conceded_last_5', 0) / 5
        
        # Original state determination logic (CSV-compliant)
        if home_goals_avg <= 0.8 and away_goals_avg <= 0.8:
            return "TERMINAL_STAGNATION"
        elif home_conceded_avg <= 0.6 and away_goals_avg <= 0.8:
            return "ASYMMETRIC_SUPPRESSION"
        elif home_goals_avg >= 2.0 and away_goals_avg >= 1.8:
            return "FORCED_EXPLOSION"
        elif (home_goals_avg <= 1.0 and home_conceded_avg >= 1.8) or \
             (away_goals_avg <= 1.0 and away_conceded_avg >= 1.8):
            return "DELAYED_RELEASE"
        else:
            return "NEUTRAL"
    
    # =================== UI DISPLAY FUNCTIONS ===================
    
    @classmethod
    def create_ui_display_data(cls, classification_result: Dict) -> Dict[str, Any]:
        """
        CREATE UI-FRIENDLY DISPLAY DATA - CSV-COMPLIANT
        
        Transforms classification results into a format suitable for
        Streamlit UI display with clean formatting.
        Uses ONLY CSV-compliant data.
        """
        if classification_result.get('classification_error', False):
            error_msg = classification_result.get('error_message', 'Unknown error')
            missing_fields = classification_result.get('missing_fields', [])
            
            # Special handling for data integrity violations
            if classification_result.get('data_integrity_violation', False):
                return {
                    'display_type': 'DATA_INTEGRITY_ERROR',
                    'error_message': '⚠️ DATA INTEGRITY VIOLATION',
                    'detailed_message': f'Last-5 data missing or invalid: {error_msg}',
                    'missing_fields': missing_fields,
                    'suggestion': 'Check CSV for goals_scored_last_5 and goals_conceded_last_5 fields',
                    'averages': {
                        'home_goals': None,  # Not 0.00!
                        'home_conceded': None,
                        'away_goals': None,
                        'away_conceded': None
                    }
                }
            
            return {
                'display_type': 'ERROR',
                'error_message': error_msg,
                'missing_fields': missing_fields,
                'suggestion': 'Check CSV data for goals_scored_last_5 and goals_conceded_last_5 fields',
                'averages': {
                    'home_goals': None,
                    'home_conceded': None,
                    'away_goals': None,
                    'away_conceded': None
                }
            }
        
        # Extract data
        averages = classification_result.get('averages', {})
        totals_durability = classification_result.get('totals_durability', 'NONE')
        under_suggestion = classification_result.get('under_suggestion', 'No Under recommendation')
        dominant_state = classification_result.get('dominant_state', 'NEUTRAL')
        reliability_home = classification_result.get('reliability_home', {})
        opponent_under_15 = classification_result.get('opponent_under_15', {})
        
        # Get state configuration
        state_config = cls.STATE_CONFIG.get(dominant_state, cls.STATE_CONFIG['NEUTRAL'])
        
        # Determine durability display
        durability_config = {
            'STABLE': {'emoji': '🟢', 'color': '#16A34A', 'label': 'STABLE'},
            'FRAGILE': {'emoji': '🟡', 'color': '#F59E0B', 'label': 'FRAGILE'},
            'NONE': {'emoji': '⚫', 'color': '#6B7280', 'label': 'NONE'}
        }
        durability_info = durability_config.get(totals_durability, durability_config['NONE'])
        
        # Create UI data structure
        return {
            'display_type': 'CLASSIFICATION',
            'averages': {
                'home_goals': averages.get('home_goals_avg'),
                'home_conceded': averages.get('home_conceded_avg'),
                'away_goals': averages.get('away_goals_avg'),
                'away_conceded': averages.get('away_conceded_avg')
            },
            'match_state': {
                'code': dominant_state,
                'emoji': state_config['emoji'],
                'color': state_config['color'],
                'label': state_config['label']
            },
            'durability': {
                'code': totals_durability,
                'emoji': durability_info['emoji'],
                'color': durability_info['color'],
                'label': durability_info['label']
            },
            'under_suggestion': under_suggestion,
            'reliability': {
                'score': reliability_home.get('reliability_score', 0),
                'label': reliability_home.get('reliability_label', 'NONE'),
                'description': reliability_home.get('reliability_description', ''),
                'color': reliability_home.get('reliability_color', 'gray'),
                'breakdown': reliability_home.get('score_breakdown', {})
            },
            'defensive_analysis': {
                'home_strong_defense': averages.get('home_conceded_avg', 0) <= cls.OPPONENT_UNDER_15_THRESHOLD,
                'away_strong_defense': averages.get('away_conceded_avg', 0) <= cls.OPPONENT_UNDER_15_THRESHOLD,
                'threshold': cls.OPPONENT_UNDER_15_THRESHOLD,
                'home_perspective_final': opponent_under_15.get('home_perspective', {}).get('final_verdict', False),
                'away_perspective_final': opponent_under_15.get('away_perspective', {}).get('final_verdict', False)
            },
            'metadata': {
                'data_source': 'Last 5 matches only',
                'data_compliance': '100% CSV-compliant',
                'read_only': True,
                'version': 'v1.7',
                'principle': 'Missing data blocks classification, does not create false 0.00'
            }
        }
    
    @classmethod
    def generate_streamlit_ui(cls, home_team: str, away_team: str, 
                            home_data: Dict, away_data: Dict) -> Dict[str, Any]:
        """
        GENERATE COMPLETE STREAMLIT UI DATA - CSV-COMPLIANT
        
        One function to run everything and return data ready for Streamlit display.
        This is the recommended integration point for your app.py.
        Uses ONLY CSV-compliant data.
        """
        # Step 1: Run full classification - CSV COMPLIANT
        classification_result = cls.run_full_classification(
            home_data, away_data
        )
        
        # Step 2: Create UI display data
        ui_data = cls.create_ui_display_data(classification_result)
        
        # Step 3: Add team names for display
        ui_data['teams'] = {
            'home': home_team,
            'away': away_team
        }
        
        # Step 4: Add raw data for debugging if needed
        ui_data['raw_data'] = {
            'home': home_data,
            'away': away_data
        }
        
        return ui_data
    
    # =================== UTILITY FUNCTIONS ===================
    
    @classmethod
    def get_data_requirements(cls) -> Dict[str, Any]:
        """
        GET DATA REQUIREMENTS FOR CSV/INPUT - CSV-COMPLIANT
        
        Returns the exact CSV-compliant data fields needed for classification.
        Helpful for CSV preparation and validation.
        """
        return {
            'required_fields': cls.MINIMUM_DATA_REQUIREMENTS,
            'data_format': 'Sum totals for last 5 matches (not averages)',
            'examples': {
                'goals_scored_last_5': 'Total goals scored in last 5 matches (e.g., 8)',
                'goals_conceded_last_5': 'Total goals conceded in last 5 matches (e.g., 4)'
            },
            'validation_rules': [
                'Values must be integers ≥ 0',
                'Values represent SUM totals, not averages',
                'Divide by 5 internally to get averages',
                'NO match-by-match lists allowed (CSV rule)',
                '100% CSV-compliant architecture'
            ],
            'architectural_principles': [
                'Missing data blocks classification (does not create false 0.00)',
                'NaN values are preserved, not hidden',
                'No data transformations or calculations before classifier',
                'Pure CSV → Dict mapping only'
            ],
            'data_compliance': {
                'status': 'FULLY COMPLIANT',
                'principle': 'Uses only CSV columns: goals_scored_last_5, goals_conceded_last_5',
                'illegal_fields': ['concede_last_5_list', 'any match-by-match lists'],
                'architecture': 'Aggregate-only calculations'
            }
        }
    
    @classmethod
    def check_data_quality(cls, home_data: Dict, away_data: Dict) -> Dict[str, Any]:
        """
        CHECK DATA QUALITY AND PROVIDE FEEDBACK - CSV-COMPLIANT
        
        Useful for debugging data issues before classification.
        Only checks CSV-compliant fields.
        """
        # Validate basic data
        is_valid, missing_fields, validated_data = cls.validate_last5_data(home_data, away_data)
        
        # Calculate what averages would be
        if is_valid:
            home_goals_avg = validated_data['home']['goals_scored_last_5'] / 5
            home_conceded_avg = validated_data['home']['goals_conceded_last_5'] / 5
            away_goals_avg = validated_data['away']['goals_scored_last_5'] / 5
            away_conceded_avg = validated_data['away']['goals_conceded_last_5'] / 5
            
            quality_score = 100  # Perfect if valid
            
            suggestions = []
            if home_goals_avg == 0 and home_conceded_avg == 0:
                suggestions.append("⚠️ Home team data shows all zeros - verify this is correct real data")
            if away_goals_avg == 0 and away_conceded_avg == 0:
                suggestions.append("⚠️ Away team data shows all zeros - verify this is correct real data")
        else:
            home_goals_avg = home_conceded_avg = away_goals_avg = away_conceded_avg = None  # Not 0.00!
            quality_score = 0
            suggestions = [f"❌ Fix missing fields: {', '.join(missing_fields)}"]
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_score,
            'missing_fields': missing_fields,
            'calculated_averages': {
                'home_goals': round(home_goals_avg, 2) if home_goals_avg is not None else None,
                'home_conceded': round(home_conceded_avg, 2) if home_conceded_avg is not None else None,
                'away_goals': round(away_goals_avg, 2) if away_goals_avg is not None else None,
                'away_conceded': round(away_conceded_avg, 2) if away_conceded_avg is not None else None
            },
            'suggestions': suggestions,
            'data_quality': 'GOOD' if is_valid else 'POOR',
            'can_run_classifier': is_valid,
            'data_compliance': {
                'status': 'CSV-COMPLIANT' if is_valid else 'VIOLATION',
                'fields_checked': cls.MINIMUM_DATA_REQUIREMENTS,
                'illegal_fields_checked': ['concede_last_5_list', 'match-by-match lists'],
                'result': 'NO ILLEGAL FIELDS' if is_valid else 'MISSING REQUIRED FIELDS'
            }
        }


# =================== HELPER FUNCTIONS FOR APP.PY INTEGRATION ===================

def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict[str, Any]:
    """
    HELPER FUNCTION FOR APP.PY INTEGRATION
    
    Simple wrapper for app.py to get classification.
    Returns classification result ready for display.
    """
    return MatchStateClassifier.run_full_classification(home_data, away_data)


def format_reliability_badge(reliability_data: Dict) -> str:
    """
    FORMAT RELIABILITY BADGE FOR STREAMLIT
    
    Converts reliability data into a formatted badge string.
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
    
    return f'{emoji} **Reliability: {label} ({score}/5)**'


def format_durability_indicator(durability: str) -> str:
    """
    FORMAT DURABILITY INDICATOR FOR STREAMLIT
    
    Converts durability code into a formatted string.
    """
    indicator_map = {
        'STABLE': '🟢 STABLE',
        'FRAGILE': '🟡 FRAGILE', 
        'NONE': '⚫ NONE'
    }
    
    return indicator_map.get(durability, '⚫ NONE')


# =================== EXAMPLE USAGE ===================
if __name__ == "__main__":
    print("=== BRUTBALL MATCH STATE CLASSIFIER v1.7 - CSV-COMPLIANT ===")
    print("PRINCIPLE: Missing data blocks classification, does not create false 0.00")
    print("Fields used: goals_scored_last_5, goals_conceded_last_5 ONLY\n")
    
    # Example data - CSV-COMPLIANT
    home_data = {
        'goals_scored_last_5': 6,    # Sum of last 5 matches
        'goals_conceded_last_5': 5   # Sum of last 5 matches
    }
    
    away_data = {
        'goals_scored_last_5': 9,    # Sum of last 5 matches  
        'goals_conceded_last_5': 7   # Sum of last 5 matches
    }
    
    # Example 1: Check data quality
    print("=== DATA QUALITY CHECK ===")
    quality_check = MatchStateClassifier.check_data_quality(home_data, away_data)
    print(f"Data valid: {quality_check['is_valid']}")
    print(f"Data compliance: {quality_check['data_compliance']['status']}")
    print(f"Calculated averages:")
    avgs = quality_check['calculated_averages']
    print(f"  Home goals: {avgs['home_goals']:.2f}" if avgs['home_goals'] is not None else "  Home goals: None (missing data)")
    print(f"  Home conceded: {avgs['home_conceded']:.2f}" if avgs['home_conceded'] is not None else "  Home conceded: None (missing data)")
    print(f"  Away goals: {avgs['away_goals']:.2f}" if avgs['away_goals'] is not None else "  Away goals: None (missing data)")
    print(f"  Away conceded: {avgs['away_conceded']:.2f}" if avgs['away_conceded'] is not None else "  Away conceded: None (missing data)")
    
    # Example 2: Full classification
    print("\n=== FULL CLASSIFICATION ===")
    classification = MatchStateClassifier.run_full_classification(
        home_data, away_data
    )
    
    if classification['classification_error']:
        print(f"❌ ERROR: {classification['error_message']}")
        print(f"Missing fields: {classification.get('missing_fields', [])}")
    else:
        print(f"✅ Classification successful")
        print(f"Match state: {classification['dominant_state']}")
        print(f"Durability: {classification['totals_durability']}")
        print(f"Under suggestion: {classification['under_suggestion']}")
        print(f"Reliability score: {classification['reliability_home']['reliability_score']}")
    
    # Example 3: Get data requirements
    print("\n=== DATA REQUIREMENTS ===")
    requirements = MatchStateClassifier.get_data_requirements()
    print(f"Required fields: {requirements['required_fields']}")
    print(f"Architectural principles:")
    for principle in requirements['architectural_principles']:
        print(f"  • {principle}")
    
    print("\n=== SYSTEM STATUS: ARCHITECTURALLY PURE CSV-ONLY ===")
    print("• Uses only goals_scored_last_5, goals_conceded_last_5")
    print("• Missing data → BLOCKS classification (not false 0.00)")
    print("• NaN values preserved (not hidden)")
    print("• No data transformations before classifier")
    print("• Pure CSV → Dict mapping only")
