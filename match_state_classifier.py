"""
BRUTBALL MATCH STATE & DURABILITY CLASSIFIER v1.4
READ-ONLY MODULE - NO SIDE EFFECTS

CRITICAL FIX: Added data validation guard rails
- No more fabricating 0.00 averages from missing data
- Classifier DISABLES itself if last-5 data is missing/invalid
- Clear error messaging instead of misleading outputs

PURPOSE:
Classify matches into structural states, durability categories, and reliability scores.
This does NOT affect betting logic, stakes, or existing tiers.
It only labels reality to provide intelligent insights.
"""

from typing import Dict, Tuple, List, Optional
import pandas as pd


class MatchStateClassifier:
    """
    MATCH STATE & DURABILITY CLASSIFIER (Read-Only)
    
    IMPORTANT: This is READ-ONLY. It does NOT:
    - Alter betting logic
    - Change capital allocation
    - Modify existing tiers
    - Create new locks
    
    It only labels reality to provide intelligent insights.
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
    
    # =================== DATA VALIDATION ===================
    
    @classmethod
    def validate_last5_data(cls, home_data: Dict, away_data: Dict) -> Tuple[bool, List[str], Dict]:
        """
        VALIDATE LAST 5 MATCHES DATA
        
        Returns: (is_valid, missing_fields, validated_data)
        
        CRITICAL: If data is missing, classifier should DISABLE itself
        instead of fabricating 0.00 averages.
        """
        missing_fields = []
        validated_data = {
            'home': {},
            'away': {}
        }
        
        # Check all required fields exist and are not None
        for field in cls.MINIMUM_DATA_REQUIREMENTS:
            # Check home data
            if field not in home_data or home_data.get(field) is None:
                missing_fields.append(f"home.{field}")
            else:
                validated_data['home'][field] = home_data[field]
            
            # Check away data
            if field not in away_data or away_data.get(field) is None:
                missing_fields.append(f"away.{field}")
            else:
                validated_data['away'][field] = away_data[field]
        
        # Additional validation: ensure values are numeric and reasonable
        if not missing_fields:
            for team in ['home', 'away']:
                for field in cls.MINIMUM_DATA_REQUIREMENTS:
                    value = validated_data[team][field]
                    if not isinstance(value, (int, float)):
                        missing_fields.append(f"{team}.{field}_type_error")
                    elif value < 0 or value > 50:  # Reasonable bounds for last 5 matches
                        missing_fields.append(f"{team}.{field}_range_error")
        
        is_valid = len(missing_fields) == 0
        
        return is_valid, missing_fields, validated_data
    
    # =================== CORE CLASSIFICATION FUNCTIONS ===================
    
    @classmethod
    def classify_totals_durability(cls, home_data: Dict, away_data: Dict) -> str:
        """
        CLASSIFY TOTALS DURABILITY (Under 2.5)
        
        Returns 'STABLE', 'FRAGILE', or 'NONE' for Under 2.5 durability.
        Uses ONLY last 5 matches data.
        
        ASSUMES: Data has been validated by validate_last5_data()
        """
        # Extract last 5 matches goals scored (already validated)
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        # Calculate averages (last 5 only)
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
    def classify_opponent_under_15(cls, home_data: Dict, away_data: Dict) -> Dict:
        """
        CLASSIFY OPPONENT UNDER 1.5 (PERSPECTIVE-SENSITIVE)
        
        IMPORTANT: "Opponent" depends on perspective:
        • If analyzing Home Team → Opponent = Away Team
        • If analyzing Away Team → Opponent = Home Team
        
        Returns defensive strength classification for BOTH perspectives.
        
        Signal = PRESENT if opponent concedes ≤1.0 avg goals in last 5 matches.
        Uses ONLY last 5 matches conceded data.
        
        ASSUMES: Data has been validated by validate_last5_data()
        """
        # Extract last 5 matches goals conceded (already validated)
        home_conceded_last5 = home_data.get('goals_conceded_last_5', 0)
        away_conceded_last5 = away_data.get('goals_conceded_last_5', 0)
        
        # Calculate averages (last 5 only)
        home_avg_conceded = home_conceded_last5 / 5 if home_conceded_last5 is not None else 0
        away_avg_conceded = away_conceded_last5 / 5 if away_conceded_last5 is not None else 0
        
        # =================== CRITICAL: PERSPECTIVE-BASED ANALYSIS ===================
        # If we're analyzing HOME TEAM → OPPONENT = AWAY TEAM
        home_perspective_opponent_under_15 = away_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        # If we're analyzing AWAY TEAM → OPPONENT = HOME TEAM
        away_perspective_opponent_under_15 = home_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        return {
            # Home Team Perspective: "Can we back Home Team given Away's defense?"
            'home_perspective': {
                'opponent_under_15': home_perspective_opponent_under_15,
                'opponent_name': 'AWAY_TEAM',
                'opponent_avg_conceded': away_avg_conceded,
                'interpretation': f"When backing HOME: Away concedes {away_avg_conceded:.2f} avg (last 5) {'≤1.0' if home_perspective_opponent_under_15 else '>1.0'}"
            },
            
            # Away Team Perspective: "Can we back Away Team given Home's defense?"
            'away_perspective': {
                'opponent_under_15': away_perspective_opponent_under_15,
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
            
            # Legacy field for compatibility (uses home perspective by default)
            'any_opponent_under_15': home_perspective_opponent_under_15 or away_perspective_opponent_under_15
        }
    
    @classmethod
    def suggest_under_market(cls, home_data: Dict, away_data: Dict) -> str:
        """
        SUGGEST UNDER MARKET BASED ON DURABILITY
        
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
    def compute_reliability_score(cls, classifications: Dict, perspective: str = 'home') -> Dict:
        """
        COMPUTE RELIABILITY SCORE (0-5) - PERSPECTIVE-SENSITIVE
        
        perspective: 'home' or 'away' - which team we're analyzing from
        """
        # Extract classification values
        totals_durability = classifications.get('totals_durability', 'NONE')
        under_suggestion = classifications.get('under_suggestion', 'No Under recommendation')
        
        # CRITICAL: Get opponent signal from correct perspective
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
                'score_range': '0-5',
                'interpretation': 'Higher score indicates stronger under structure',
                'purpose': 'Informational reliability indicator only'
            }
        }
    
    # =================== EXISTING MATCH STATE FUNCTIONS ===================
    
    @classmethod
    def check_terminal_stagnation(cls, home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        Existing function - preserved for backward compatibility
        ASSUMES: Data has been validated by validate_last5_data()
        """
        rationale = []
        
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        home_avg = home_last5_goals / 5 if home_last5_goals is not None else 0
        away_avg = away_last5_goals / 5 if away_last5_goals is not None else 0
        
        low_scoring = (home_avg <= 1.2) and (away_avg <= 1.2)
        
        home_setpiece = home_data.get('home_setpiece_pct', 0)
        home_counter = home_data.get('home_counter_pct', 0)
        away_setpiece = away_data.get('away_setpiece_pct', 0)
        away_counter = away_data.get('away_counter_pct', 0)
        
        no_dominant_pathways = (
            (home_setpiece < 0.3 and home_counter < 0.18) and
            (away_setpiece < 0.3 and away_counter < 0.18)
        )
        
        is_terminal_stagnation = low_scoring and no_dominant_pathways
        
        rationale.append(f"TERMINAL STAGNATION CHECK:")
        rationale.append(f"• Home avg goals: {home_avg:.2f}")
        rationale.append(f"• Away avg goals: {away_avg:.2f}")
        rationale.append(f"• Low scoring: {'✅' if low_scoring else '❌'}")
        rationale.append(f"• No dominant pathways: {'✅' if no_dominant_pathways else '❌'}")
        
        return is_terminal_stagnation, {
            'home_avg': home_avg,
            'away_avg': away_avg,
            'low_scoring': low_scoring,
            'no_dominant_pathways': no_dominant_pathways
        }, rationale
    
    @classmethod
    def check_asymmetric_suppression(cls, home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        Existing function - preserved for backward compatibility
        ASSUMES: Data has been validated by validate_last5_data()
        """
        rationale = []
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        
        home_dominates = (home_xg > 1.4) and (home_xg - away_xg > 0.5)
        away_dominates = (away_xg > 1.2) and (away_xg - home_xg > 0.5)
        
        home_suppressed = away_data.get('away_xg_per_match', 0) < 1.0
        away_suppressed = home_data.get('home_xg_per_match', 0) < 1.0
        
        is_asymmetric = (
            (home_dominates and home_suppressed) or
            (away_dominates and away_suppressed)
        )
        
        dominating_team = None
        if home_dominates and home_suppressed:
            dominating_team = "HOME"
        elif away_dominates and away_suppressed:
            dominating_team = "AWAY"
        
        rationale.append(f"ASYMMETRIC SUPPRESSION CHECK:")
        rationale.append(f"• Home xG: {home_xg:.2f}")
        rationale.append(f"• Away xG: {away_xg:.2f}")
        rationale.append(f"• Home dominates: {'✅' if home_dominates else '❌'}")
        rationale.append(f"• Away dominates: {'✅' if away_dominates else '❌'}")
        rationale.append(f"• Home suppressed: {'✅' if home_suppressed else '❌'}")
        rationale.append(f"• Away suppressed: {'✅' if away_suppressed else '❌'}")
        
        if is_asymmetric:
            rationale.append(f"• Dominating team: {dominating_team}")
        
        return is_asymmetric, {
            'home_xg': home_xg,
            'away_xg': away_xg,
            'home_dominates': home_dominates,
            'away_dominates': away_dominates,
            'home_suppressed': home_suppressed,
            'away_suppressed': away_suppressed,
            'dominating_team': dominating_team
        }, rationale
    
    # =================== MAIN CLASSIFICATION FUNCTION ===================
    
    @classmethod
    def classify_match_state(cls, home_data: Dict, away_data: Dict) -> Dict:
        """
        MAIN CLASSIFICATION FUNCTION - COMPLETE SYSTEM
        
        Returns ALL classifications in a single dictionary.
        
        IMPORTANT: This is 100% READ-ONLY and informational only.
        Does NOT affect betting logic, stakes, or existing tiers.
        Uses ONLY last 5 matches data for all calculations.
        
        CRITICAL FIX: If last-5 data is missing/invalid, classifier DISABLES itself
        instead of fabricating 0.00 averages and misleading outputs.
        """
        
        classification_log = []
        classification_log.append("=" * 70)
        classification_log.append("🧠 BRUTBALL INTELLIGENCE LAYER v1.4 (READ-ONLY)")
        classification_log.append("=" * 70)
        classification_log.append("PURPOSE: Structural classification for intelligent insights")
        classification_log.append("RULES: Does not affect betting logic - informational only")
        classification_log.append("DATA: Uses ONLY last 5 matches for all calculations")
        classification_log.append("")
        
        # ========== 1. DATA VALIDATION CHECK ==========
        classification_log.append("🔍 DATA VALIDATION CHECK:")
        classification_log.append("-" * 40)
        
        is_valid, missing_fields, validated_data = cls.validate_last5_data(home_data, away_data)
        
        if not is_valid:
            classification_log.append(f"❌ INSUFFICIENT DATA FOR CLASSIFICATION")
            classification_log.append(f"• Missing or invalid fields: {', '.join(missing_fields)}")
            classification_log.append(f"• Required fields: {', '.join(cls.MINIMUM_DATA_REQUIREMENTS)}")
            classification_log.append(f"• Last 5 matches data required for all calculations")
            classification_log.append(f"• Classifier DISABLED - No structural insights available")
            classification_log.append("=" * 70)
            
            return {
                'classification_error': True,
                'error_message': f"Insufficient last-5 data: {', '.join(missing_fields)}",
                'error_type': 'MISSING_DATA',
                'missing_fields': missing_fields,
                'classification_log': classification_log,
                'is_read_only': True,
                'metadata': {
                    'version': '1.4',
                    'status': 'DISABLED - INSUFFICIENT_DATA',
                    'action': 'Check data source for goals_scored_last_5 and goals_conceded_last_5 fields',
                    'data_requirements': cls.MINIMUM_DATA_REQUIREMENTS,
                    'data_source': 'last_5_matches_only'
                }
            }
        
        # Extract validated data for processing
        home_validated = validated_data['home']
        away_validated = validated_data['away']
        
        classification_log.append("✅ Last 5 matches data validation passed")
        classification_log.append(f"• Home goals scored (last 5): {home_validated.get('goals_scored_last_5')}")
        classification_log.append(f"• Away goals scored (last 5): {away_validated.get('goals_scored_last_5')}")
        classification_log.append(f"• Home goals conceded (last 5): {home_validated.get('goals_conceded_last_5')}")
        classification_log.append(f"• Away goals conceded (last 5): {away_validated.get('goals_conceded_last_5')}")
        classification_log.append("")
        
        # ========== 2. TOTALS DURABILITY CLASSIFICATION ==========
        classification_log.append("📊 TOTALS DURABILITY CLASSIFICATION (LAST 5 ONLY):")
        classification_log.append("-" * 40)
        
        totals_durability = cls.classify_totals_durability(home_validated, away_validated)
        home_last5_goals = home_validated.get('goals_scored_last_5', 0)
        away_last5_goals = away_validated.get('goals_scored_last_5', 0)
        home_avg = home_last5_goals / 5 if home_last5_goals is not None else 0
        away_avg = away_last5_goals / 5 if away_last5_goals is not None else 0
        
        classification_log.append(f"• Home avg goals (last 5): {home_avg:.2f}")
        classification_log.append(f"• Away avg goals (last 5): {away_avg:.2f}")
        classification_log.append(f"• Max avg: {max(home_avg, away_avg):.2f}")
        classification_log.append(f"• Durability: {totals_durability}")
        classification_log.append(f"• Thresholds: STABLE≤{cls.DURABILITY_STABLE_THRESHOLD}, FRAGILE≤{cls.DURABILITY_FRAGILE_THRESHOLD}")
        classification_log.append("")
        
        # ========== 3. OPPONENT UNDER 1.5 CLASSIFICATION ==========
        classification_log.append("🛡️ OPPONENT UNDER 1.5 CLASSIFICATION (LAST 5 ONLY):")
        classification_log.append("-" * 40)
        classification_log.append("PERSPECTIVE-SENSITIVE: 'Opponent' depends on which team is backed")
        classification_log.append("")
        
        opponent_under_15 = cls.classify_opponent_under_15(home_validated, away_validated)
        
        classification_log.append(f"• Home avg conceded (last 5): {opponent_under_15['home_avg_conceded']:.2f}")
        classification_log.append(f"• Away avg conceded (last 5): {opponent_under_15['away_avg_conceded']:.2f}")
        classification_log.append(f"• Home defense strong (≤{cls.OPPONENT_UNDER_15_THRESHOLD}): {'✅' if opponent_under_15['home_avg_conceded'] <= cls.OPPONENT_UNDER_15_THRESHOLD else '❌'}")
        classification_log.append(f"• Away defense strong (≤{cls.OPPONENT_UNDER_15_THRESHOLD}): {'✅' if opponent_under_15['away_avg_conceded'] <= cls.OPPONENT_UNDER_15_THRESHOLD else '❌'}")
        
        # Show perspective-based signals
        classification_log.append("")
        classification_log.append("📋 PERSPECTIVE-BASED SIGNALS:")
        classification_log.append(f"• {opponent_under_15['home_perspective']['interpretation']}")
        classification_log.append(f"• Signal when backing HOME: {'✅ PRESENT' if opponent_under_15['home_perspective']['opponent_under_15'] else '❌ ABSENT'}")
        classification_log.append("")
        classification_log.append(f"• {opponent_under_15['away_perspective']['interpretation']}")
        classification_log.append(f"• Signal when backing AWAY: {'✅ PRESENT' if opponent_under_15['away_perspective']['opponent_under_15'] else '❌ ABSENT'}")
        classification_log.append("")
        
        # ========== 4. UNDER MARKET SUGGESTIONS ==========
        classification_log.append("🎯 UNDER MARKET SUGGESTIONS:")
        classification_log.append("-" * 40)
        
        under_suggestion = cls.suggest_under_market(home_validated, away_validated)
        classification_log.append(f"• Based on {totals_durability} durability (from last 5):")
        classification_log.append(f"• Suggestion: {under_suggestion}")
        classification_log.append("")
        
        # ========== 5. EXISTING MATCH STATES (Preserved) ==========
        classification_log.append("⚙️ STRUCTURAL MATCH STATES:")
        classification_log.append("-" * 40)
        
        states = []
        
        # Check terminal stagnation
        is_stagnation, stagnation_data, stagnation_rationale = cls.check_terminal_stagnation(home_validated, away_validated)
        if is_stagnation:
            states.append(('TERMINAL_STAGNATION', stagnation_data))
        classification_log.extend(stagnation_rationale)
        
        # Check asymmetric suppression
        is_asymmetric, asymmetric_data, asymmetric_rationale = cls.check_asymmetric_suppression(home_validated, away_validated)
        if is_asymmetric:
            states.append(('ASYMMETRIC_SUPPRESSION', asymmetric_data))
        classification_log.extend(asymmetric_rationale)
        
        # Determine dominant state
        dominant_state = "NEUTRAL"
        state_hierarchy = ['TERMINAL_STAGNATION', 'ASYMMETRIC_SUPPRESSION']
        for state in state_hierarchy:
            if any(s[0] == state for s in states):
                dominant_state = state
                break
        
        classification_log.append(f"• Dominant Structural State: {dominant_state}")
        classification_log.append("")
        
        # ========== 6. RELIABILITY SCORING ==========
        classification_log.append("📈 RELIABILITY SCORING (0-5):")
        classification_log.append("-" * 40)
        
        # Build intermediate classifications dict
        intermediate_classifications = {
            'totals_durability': totals_durability,
            'under_suggestion': under_suggestion,
            'opponent_under_15': opponent_under_15
        }
        
        # Compute reliability scores for both perspectives
        reliability_home = cls.compute_reliability_score(intermediate_classifications, perspective='home')
        reliability_away = cls.compute_reliability_score(intermediate_classifications, perspective='away')
        
        classification_log.append(f"• Totals Durability: {totals_durability} (+{reliability_home['component_scores']['durability']})")
        classification_log.append(f"• Under Suggestion: {under_suggestion} (+{reliability_home['component_scores']['under_suggestion']})")
        classification_log.append(f"• Opponent Under 1.5 (HOME perspective): {'✅' if opponent_under_15['home_perspective']['opponent_under_15'] else '❌'} (+{reliability_home['component_scores']['opponent_under_15']})")
        classification_log.append(f"• Opponent Under 1.5 (AWAY perspective): {'✅' if opponent_under_15['away_perspective']['opponent_under_15'] else '❌'} (+{reliability_away['component_scores']['opponent_under_15']})")
        classification_log.append(f"• HOME Perspective Score: {reliability_home['reliability_score']}/5 - {reliability_home['reliability_label']}")
        classification_log.append(f"• AWAY Perspective Score: {reliability_away['reliability_score']}/5 - {reliability_away['reliability_label']}")
        classification_log.append("")
        
        # ========== 7. FINAL SUMMARY ==========
        classification_log.append("🎯 INTELLIGENCE SUMMARY (LAST 5 DATA ONLY):")
        classification_log.append("-" * 40)
        
        classification_log.append(f"1. Durability: {totals_durability}")
        classification_log.append(f"2. Under Suggestion: {under_suggestion}")
        classification_log.append(f"3. Opponent Under 1.5 - Backing HOME: {'PRESENT' if opponent_under_15['home_perspective']['opponent_under_15'] else 'ABSENT'}")
        classification_log.append(f"4. Opponent Under 1.5 - Backing AWAY: {'PRESENT' if opponent_under_15['away_perspective']['opponent_under_15'] else 'ABSENT'}")
        classification_log.append(f"5. Structural State: {dominant_state}")
        classification_log.append(f"6. Reliability (HOME perspective): {reliability_home['reliability_label']} ({reliability_home['reliability_score']}/5)")
        classification_log.append(f"7. Reliability (AWAY perspective): {reliability_away['reliability_label']} ({reliability_away['reliability_score']}/5)")
        classification_log.append("")
        
        classification_log.append("⚠️ IMPORTANT: This is READ-ONLY INTELLIGENCE ONLY")
        classification_log.append("   • Does NOT affect Tier 1-3 logic")
        classification_log.append("   • Does NOT modify stakes or capital allocation")
        classification_log.append("   • Does NOT create market locks")
        classification_log.append("   • Informational insights for decision support only")
        classification_log.append("=" * 70)
        
        # ========== 8. RETURN COMPLETE RESULTS ==========
        return {
            # Core Classifications
            'totals_durability': totals_durability,
            'under_suggestion': under_suggestion,
            'opponent_under_15': opponent_under_15,
            'dominant_state': dominant_state,
            'all_states': [s[0] for s in states],
            
            # Reliability Scoring (both perspectives)
            'reliability_home': reliability_home,
            'reliability_away': reliability_away,
            'reliability_score': reliability_home['reliability_score'],  # Default to home perspective
            
            # Data for display/analysis
            'averages': {
                'home_goals_avg': home_avg,
                'away_goals_avg': away_avg,
                'home_conceded_avg': opponent_under_15['home_avg_conceded'],
                'away_conceded_avg': opponent_under_15['away_avg_conceded']
            },
            
            # Validation info
            'data_validated': True,
            'validation_status': 'PASSED',
            
            # Logs and metadata
            'classification_log': classification_log,
            'is_read_only': True,  # CRITICAL SAFETY FLAG
            'metadata': {
                'version': '1.4',
                'purpose': 'Read-only intelligence layer for structural insights',
                'no_side_effects': True,
                'components': {
                    'match_states': True,
                    'totals_durability': True,
                    'opponent_under_15': True,
                    'under_suggestions': True,
                    'reliability_scoring': True
                },
                'data_source': 'last_5_matches_only',
                'perspective_sensitive': True,
                'data_validation': 'ENABLED'
            }
        }


# =================== INTEGRATION HELPER FUNCTIONS ===================

def get_complete_classification(home_data: Dict, away_data: Dict) -> Dict:
    """
    SAFE INTEGRATION HELPER - MAIN ENTRY POINT
    
    Use this function in app.py to get ALL classification results.
    Ensures classification stays 100% read-only.
    
    CRITICAL FIX: Graceful error handling - classifier either works or disables
    """
    try:
        return MatchStateClassifier.classify_match_state(home_data, away_data)
    except Exception as e:
        # Graceful fallback - classifier unavailable due to unexpected error
        error_log = [
            "=" * 70,
            "🧠 BRUTBALL INTELLIGENCE LAYER v1.4 (READ-ONLY)",
            "=" * 70,
            "❌ CLASSIFIER ERROR",
            f"Error: {str(e)}",
            "Classifier DISABLED - Unexpected error during classification",
            "=" * 70
        ]
        
        return {
            'classification_error': True,
            'error_message': f"Classifier error: {str(e)}",
            'error_type': 'UNEXPECTED_ERROR',
            'classification_log': error_log,
            'is_read_only': True,
            'metadata': {
                'version': '1.4',
                'status': 'DISABLED - UNEXPECTED_ERROR',
                'action': 'Check data structure and classifier integrity',
                'data_requirements': MatchStateClassifier.MINIMUM_DATA_REQUIREMENTS
            }
        }


def format_reliability_badge(reliability_data: Dict) -> str:
    """
    FORMAT RELIABILITY SCORE AS UI BADGE
    
    Returns HTML/emoji formatted badge for display in Streamlit.
    """
    score = reliability_data.get('reliability_score', 0)
    label = reliability_data.get('reliability_label', 'NONE')
    color = reliability_data.get('reliability_color', 'gray')
    
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
    
    Returns emoji-formatted durability indicator.
    """
    indicators = {
        'STABLE': '🟢 STABLE',
        'FRAGILE': '🟡 FRAGILE',
        'NONE': '⚫ NONE'
    }
    return indicators.get(durability, '⚫ NONE')


def get_classifier_status_message(classification_result: Dict) -> str:
    """
    GET CLASSIFIER STATUS MESSAGE FOR DISPLAY
    
    Returns appropriate message based on classifier state.
    """
    if classification_result.get('classification_error', False):
        error_type = classification_result.get('error_type', 'UNKNOWN_ERROR')
        error_message = classification_result.get('error_message', 'Unknown error')
        
        if error_type == 'MISSING_DATA':
            return f"⚠️ Classifier unavailable: Missing last-5 data ({error_message})"
        elif error_type == 'UNEXPECTED_ERROR':
            return f"⚠️ Classifier error: {error_message}"
        else:
            return f"⚠️ Classifier unavailable: {error_message}"
    else:
        return "✅ Classifier active - Read-only insights available"
