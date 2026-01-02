"""
BRUTBALL MATCH STATE & DURABILITY CLASSIFIER v1.6
WITH DEFENSIVE STABILITY FILTER (DSF) INTEGRATION

COMPLETE UNIFIED FILE - ALL LOGIC IN ONE PLACE

CRITICAL ENHANCEMENT: Defensive Stability Filter (DSF)
- Fixes Chelsea vs Bournemouth-type false positives
- Principle: Average ≠ Preservation
- Rule: If team conceded 2+ goals in ≥2 of last 5 matches → NO UNDER 1.5 LOCK
- Eliminates variance-blind false positives without breaking v6.3 architecture

PURPOSE:
Classify matches into structural states, durability categories, and reliability scores.
Includes DSF for edge-derived lock validation.
This does NOT affect betting logic, stakes, or existing tiers.
It only labels reality to provide intelligent insights.

USAGE:
1. First validate data with validate_last5_data()
2. If valid, run full classification
3. Use display functions for clean UI output
4. DSF automatically applied to defensive assessments
"""

from typing import Dict, Tuple, List, Optional, Any
import pandas as pd


class MatchStateClassifier:
    """
    MATCH STATE & DURABILITY CLASSIFIER (Read-Only) WITH DSF INTEGRATION
    
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
    
    # Defensive Stability Filter (DSF) thresholds
    DSF_VOLATILITY_SPIKE = 2  # ≥2 goals conceded = volatility spike
    DSF_UNSTABLE_THRESHOLD = 2  # ≥2 spikes in last 5 = unstable defense
    
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
        },
        'defensive_stability': {  # NEW: DSF scoring
            'LOW-VARIANCE': 1,
            'MODERATE-VARIANCE': 0,
            'HIGH-VARIANCE': -2  # Penalty for high volatility
        }
    }
    
    # Reliability score mappings
    RELIABILITY_LEVELS = {
        5: {
            'label': 'HIGH CONFIDENCE',
            'description': 'Under 2.5 likely; strong defensive/low-scoring structure',
            'color': 'green',
            'actionable_cue': 'Under 2.5 high probability',
            'dsf_required': 'LOW-VARIANCE only'
        },
        4: {
            'label': 'MODERATE CONFIDENCE',
            'description': 'Under 2.5 possible, monitor match pressure',
            'color': 'yellow',
            'actionable_cue': 'Under 2.5 possible, consider Under 3.5 for safety',
            'dsf_required': 'LOW-VARIANCE or MODERATE-VARIANCE'
        },
        3: {
            'label': 'CAUTION',
            'description': 'Under 3.5 safer, low structural confidence',
            'color': 'orange',
            'actionable_cue': 'Under 3.5 safer, avoid Under 2.5',
            'dsf_required': 'Any stability type'
        },
        2: {
            'label': 'LOW',
            'description': 'Weak under signal, mostly informational',
            'color': 'lightgray',
            'actionable_cue': 'Weak signal, monitor only',
            'dsf_required': 'Any stability type'
        },
        1: {
            'label': 'LOW',
            'description': 'Very weak under signal',
            'color': 'lightgray',
            'actionable_cue': 'Very weak signal, informational only',
            'dsf_required': 'Any stability type'
        },
        0: {
            'label': 'NONE',
            'description': 'No structural under detected',
            'color': 'gray',
            'actionable_cue': 'No under recommendation',
            'dsf_required': 'Any stability type'
        },
        -1: {  # NEW: DSF rejection score
            'label': 'DSF REJECTED',
            'description': 'Defense unstable - cannot preserve suppression state',
            'color': 'black',
            'actionable_cue': 'NO BET - Structural fragility detected',
            'dsf_required': 'HIGH-VARIANCE'
        }
    }
    
    # Match state configurations
    STATE_CONFIG = {
        'TERMINAL_STAGNATION': {'emoji': '🌀', 'color': '#0EA5E9', 'label': 'Terminal Stagnation'},
        'ASYMMETRIC_SUPPRESSION': {'emoji': '🛡️', 'color': '#16A34A', 'label': 'Asymmetric Suppression'},
        'DELAYED_RELEASE': {'emoji': '⏳', 'color': '#F59E0B', 'label': 'Delayed Release'},
        'FORCED_EXPLOSION': {'emoji': '💥', 'color': '#EF4444', 'label': 'Forced Explosion'},
        'NEUTRAL': {'emoji': '⚖️', 'color': '#6B7280', 'label': 'Neutral'},
        'CLASSIFIER_ERROR': {'emoji': '⚠️', 'color': '#DC2626', 'label': 'Classifier Error'},
        'DSF_UNSTABLE': {'emoji': '💥', 'color': '#DC2626', 'label': 'Structurally Unstable'}  # NEW
    }
    
    # =================== DEFENSIVE STABILITY FILTER (DSF) ===================
    
    @classmethod
    def assess_defensive_stability(cls, concede_data: List[int]) -> Dict[str, Any]:
        """
        DEFENSIVE STABILITY FILTER (DSF CORE LOGIC)
        
        Purpose: Eliminate variance-blind false positives
        Rule: If team conceded 2+ goals in ≥2 of last 5 matches → structurally unstable
        
        Example Chelsea false positive: [0, 1, 2, 0, 2]
        - Average: 1.0 ✅ (meets numerical preservation)
        - Volatility spikes: 2 ❌ (≥2 goals in 2/5 matches)
        - Verdict: UNSTABLE, cannot preserve suppression state
        """
        if not concede_data or len(concede_data) != 5:
            return {
                'error': 'Invalid concede_data format',
                'required_format': 'List of 5 integers (goals conceded in last 5 matches)',
                'example': '[0, 1, 2, 0, 2]'
            }
        
        # Count volatility spikes (≥2 goals conceded in a match)
        volatility_spikes = sum(1 for goals in concede_data if goals >= cls.DSF_VOLATILITY_SPIKE)
        
        # Calculate average
        concede_avg = sum(concede_data) / len(concede_data)
        
        # DSF RULE: If ≥2 volatility spikes → UNSTABLE
        is_stable = volatility_spikes < cls.DSF_UNSTABLE_THRESHOLD
        
        # Classify stability type
        if volatility_spikes == 0:
            stability_type = "LOW-VARIANCE"
            description = "Consistent defense, no high-concede games"
            structural_risk = "Low"
        elif volatility_spikes == 1:
            stability_type = "MODERATE-VARIANCE"
            description = "One high-concede game, generally stable"
            structural_risk = "Moderate"
        else:  # ≥2
            stability_type = "HIGH-VARIANCE"
            description = "Multiple high-concede games, structurally fragile"
            structural_risk = "High"
        
        # Determine lock eligibility
        lock_allowed = is_stable
        
        # Chelsea/Bournemouth example analysis
        example_analysis = None
        if volatility_spikes >= 2 and concede_avg <= 1.0:
            example_analysis = {
                'type': 'CHELSEA_FALSE_POSITIVE',
                'description': 'Matches Chelsea vs Bournemouth failure pattern',
                'lesson': 'Average ≠ Preservation - numerically preserved but structurally fragile'
            }
        
        return {
            'concede_data': concede_data,
            'concede_avg': round(concede_avg, 2),
            'volatility_spikes': volatility_spikes,
            'stability_type': stability_type,
            'description': description,
            'structural_risk': structural_risk,
            'is_stable': is_stable,
            'dsf_verdict': "STABLE" if is_stable else "UNSTABLE",
            'lock_allowed': lock_allowed,
            'thresholds': {
                'volatility_spike': cls.DSF_VOLATILITY_SPIKE,
                'unstable_threshold': cls.DSF_UNSTABLE_THRESHOLD,
                'spike_count': volatility_spikes
            },
            'preservation_assessment': {
                'numerical_preservation': concede_avg <= cls.OPPONENT_UNDER_15_THRESHOLD,
                'structural_preservation': is_stable,
                'full_preservation': (concede_avg <= cls.OPPONENT_UNDER_15_THRESHOLD) and is_stable
            },
            'example_analysis': example_analysis,
            'metadata': {
                'principle': 'Average ≠ Preservation',
                'purpose': 'Prevent Chelsea vs Bournemouth false positives',
                'compatibility': 'Tier 1+ Edge-Derived locks only'
            }
        }
    
    @classmethod
    def apply_dsf_to_edge_lock(cls, team_name: str, concede_data: List[int], 
                               current_lock_status: bool, confidence_tier: str) -> Dict[str, Any]:
        """
        APPLY DSF TO EXISTING EDGE-DERIVED LOCK
        
        Integrates DSF with existing Tier 1+ Edge-Derived logic.
        Returns final verdict after stability assessment.
        """
        # Run DSF assessment
        dsf_assessment = cls.assess_defensive_stability(concede_data)
        
        if 'error' in dsf_assessment:
            return {
                'error': dsf_assessment['error'],
                'team': team_name,
                'dsf_applied': False
            }
        
        # DSF OVERRIDE: Lock only if both conditions met
        final_lock = current_lock_status and dsf_assessment['lock_allowed']
        
        # Determine reason for rejection (if any)
        rejection_reason = None
        if current_lock_status and not dsf_assessment['lock_allowed']:
            rejection_reason = (
                f"DSF REJECTION: {team_name} concedes ≥2 goals in {dsf_assessment['volatility_spikes']} "
                f"of last 5 matches (avg {dsf_assessment['concede_avg']}). "
                f"Defense is {dsf_assessment['stability_type']} - cannot preserve suppression state."
            )
        
        # Adjust confidence based on stability
        adjusted_confidence = cls.adjust_confidence_with_dsf(
            confidence_tier, dsf_assessment['stability_type']
        )
        
        # Determine bet readiness
        bet_ready = final_lock and adjusted_confidence not in ['NO BET ⚫', 'DSF REJECTED ⚫']
        
        return {
            'team': team_name,
            'original_analysis': {
                'lock': current_lock_status,
                'confidence': confidence_tier
            },
            'dsf_assessment': dsf_assessment,
            'final_verdict': {
                'lock': final_lock,
                'confidence': adjusted_confidence,
                'bet_ready': bet_ready,
                'rejection_reason': rejection_reason,
                'volatility_warning': dsf_assessment['volatility_spikes'] >= 1
            },
            'preservation_summary': {
                'numerical': dsf_assessment['preservation_assessment']['numerical_preservation'],
                'structural': dsf_assessment['preservation_assessment']['structural_preservation'],
                'full': dsf_assessment['preservation_assessment']['full_preservation']
            },
            'metadata': {
                'dsf_version': '1.0',
                'applied_to': 'Tier 1+ Edge-Derived locks',
                'philosophy': 'Average ≠ Preservation'
            }
        }
    
    @classmethod
    def adjust_confidence_with_dsf(cls, original_tier: str, stability_type: str) -> str:
        """
        ADJUST CONFIDENCE TIER BASED ON DEFENSIVE STABILITY
        
        Critical: HIGH-VARIANCE defenses get NO BET, not just lower confidence
        """
        # Map original confidence tiers to DSF-adjusted tiers
        tier_map = {
            'VERY STRONG 🔵': {
                'LOW-VARIANCE': 'VERY STRONG 🔵',
                'MODERATE-VARIANCE': 'STRONG 🟢',
                'HIGH-VARIANCE': 'DSF REJECTED ⚫'  # Not 🔴 - this means NO SIGNAL
            },
            'STRONG 🟢': {
                'LOW-VARIANCE': 'STRONG 🟢',
                'MODERATE-VARIANCE': 'WEAK 🟡',
                'HIGH-VARIANCE': 'DSF REJECTED ⚫'
            },
            'WEAK 🟡': {
                'LOW-VARIANCE': 'WEAK 🟡',
                'MODERATE-VARIANCE': 'NO BET ⚫',  # Single spike disqualifies WEAK
                'HIGH-VARIANCE': 'DSF REJECTED ⚫'
            },
            'VERY WEAK 🔴': {
                'LOW-VARIANCE': 'NO BET ⚫',  # VERY WEAK shouldn't bet anyway
                'MODERATE-VARIANCE': 'NO BET ⚫',
                'HIGH-VARIANCE': 'DSF REJECTED ⚫'
            }
        }
        
        return tier_map.get(original_tier, {}).get(stability_type, 'NO BET ⚫')
    
    @classmethod
    def get_dsf_rules(cls) -> Dict[str, Any]:
        """Return the DSF rules for transparency"""
        return {
            'principle': 'Average ≠ Preservation',
            'rule': f'If team conceded ≥{cls.DSF_VOLATILITY_SPIKE}+ goals in ≥{cls.DSF_UNSTABLE_THRESHOLD} of last 5 matches → NO UNDER 1.5 LOCK',
            'rationale': 'Eliminates variance-blind false positives (Chelsea-type defenses)',
            'example_failure': {
                'chelsea_bournemouth': 'Chelsea: [0, 1, 2, 0, 2] → avg=1.0 ✅, spikes=2 ❌ → NO LOCK',
                'lesson': 'Defense can be numerically preserved (avg ≤1.0) but structurally fragile'
            },
            'thresholds': {
                'volatility_spike': f'≥{cls.DSF_VOLATILITY_SPIKE} goals conceded in a single match',
                'unstable_defense': f'≥{cls.DSF_UNSTABLE_THRESHOLD} volatility spikes in last 5 matches',
                'lock_requirement': f'Average ≤{cls.OPPONENT_UNDER_15_THRESHOLD} AND volatility_spikes < {cls.DSF_UNSTABLE_THRESHOLD}'
            },
            'defense_types': {
                'LOW-VARIANCE': '0 volatility spikes (stable, lock allowed)',
                'MODERATE-VARIANCE': '1 volatility spike (caution, reduced confidence)',
                'HIGH-VARIANCE': '≥2 volatility spikes (unstable, no lock)'
            },
            'compatibility': {
                'tier_1+': 'Enhances existing Edge-Derived logic',
                'state_preservation_law': 'Directly implements preservation principle',
                'data_requirements': 'Last 5 matches only (no new data)',
                'architectural_integrity': 'No changes to Tiers 1, 2, 3'
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
                    
                    # Type validation
                    if not isinstance(value, (int, float)):
                        missing_fields.append(f"{team}.{field}_type_error")
                        continue
                    
                    # Range validation for last 5 matches
                    # Max reasonable: 5 matches × 10 goals/match = 50
                    if value < 0 or value > 50:
                        missing_fields.append(f"{team}.{field}_range_error")
                    
                    # Zero-sum validation (if both are zero, likely missing data)
                    if value == 0 and field == 'goals_scored_last_5':
                        # Check if this is likely real data or missing data
                        conceded_field = 'goals_conceded_last_5'
                        conceded_value = validated_data[team].get(conceded_field, 0)
                        if conceded_value == 0:
                            # Both zero - likely missing data
                            missing_fields.append(f"{team}.{field}_zero_data_suspected")
        
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
    def classify_opponent_under_15(cls, home_data: Dict, away_data: Dict, 
                                   include_dsf: bool = True) -> Dict[str, Any]:
        """
        CLASSIFY OPPONENT UNDER 1.5 (PERSPECTIVE-SENSITIVE) WITH DSF
        
        IMPORTANT: "Opponent" depends on perspective:
        • If analyzing Home Team → Opponent = Away Team
        • If analyzing Away Team → Opponent = Home Team
        
        Returns defensive strength classification for BOTH perspectives.
        Includes DSF assessment if include_dsf=True.
        
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
        
        # =================== DSF ASSESSMENT (NEW) ===================
        dsf_assessment = {}
        if include_dsf:
            # Try to get match-by-match concede data
            home_concede_data = home_data.get('concede_last_5_list')
            away_concede_data = away_data.get('concede_last_5_list')
            
            if home_concede_data and isinstance(home_concede_data, list):
                dsf_assessment['home'] = cls.assess_defensive_stability(home_concede_data)
            
            if away_concede_data and isinstance(away_concede_data, list):
                dsf_assessment['away'] = cls.assess_defensive_stability(away_concede_data)
        
        # =================== PERSPECTIVE-BASED ANALYSIS ===================
        # If we're analyzing HOME TEAM → OPPONENT = AWAY TEAM
        home_perspective_opponent_under_15 = away_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        # If we're analyzing AWAY TEAM → OPPONENT = HOME TEAM
        away_perspective_opponent_under_15 = home_avg_conceded <= cls.OPPONENT_UNDER_15_THRESHOLD
        
        # Apply DSF if available
        home_perspective_dsf_stable = True
        away_perspective_dsf_stable = True
        
        if dsf_assessment:
            if 'away' in dsf_assessment:
                home_perspective_dsf_stable = dsf_assessment['away'].get('is_stable', True)
            if 'home' in dsf_assessment:
                away_perspective_dsf_stable = dsf_assessment['home'].get('is_stable', True)
        
        # Final verdict with DSF
        home_perspective_final = home_perspective_opponent_under_15 and home_perspective_dsf_stable
        away_perspective_final = away_perspective_opponent_under_15 and away_perspective_dsf_stable
        
        return {
            # Home Team Perspective: "Can we back Home Team given Away's defense?"
            'home_perspective': {
                'opponent_under_15': home_perspective_opponent_under_15,
                'dsf_stable': home_perspective_dsf_stable,
                'final_verdict': home_perspective_final,
                'opponent_name': 'AWAY_TEAM',
                'opponent_avg_conceded': away_avg_conceded,
                'interpretation': f"When backing HOME: Away concedes {away_avg_conceded:.2f} avg (last 5) {'≤1.0' if home_perspective_opponent_under_15 else '>1.0'}{' + DSF STABLE' if home_perspective_dsf_stable else ' + DSF UNSTABLE'}"
            },
            
            # Away Team Perspective: "Can we back Away Team given Home's defense?"
            'away_perspective': {
                'opponent_under_15': away_perspective_opponent_under_15,
                'dsf_stable': away_perspective_dsf_stable,
                'final_verdict': away_perspective_final,
                'opponent_name': 'HOME_TEAM',
                'opponent_avg_conceded': home_avg_conceded,
                'interpretation': f"When backing AWAY: Home concedes {home_avg_conceded:.2f} avg (last 5) {'≤1.0' if away_perspective_opponent_under_15 else '>1.0'}{' + DSF STABLE' if away_perspective_dsf_stable else ' + DSF UNSTABLE'}"
            },
            
            # DSF Assessments
            'dsf_assessments': dsf_assessment,
            'dsf_applied': bool(dsf_assessment),
            
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
            'any_opponent_under_15': home_perspective_opponent_under_15 or away_perspective_opponent_under_15,
            
            # DSF-enhanced legacy field
            'any_opponent_under_15_with_dsf': home_perspective_final or away_perspective_final
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
    def compute_reliability_score(cls, classifications: Dict, perspective: str = 'home') -> Dict[str, Any]:
        """
        COMPUTE RELIABILITY SCORE (0-5) - PERSPECTIVE-SENSITIVE WITH DSF
        
        perspective: 'home' or 'away' - which team we're analyzing from
        """
        # Extract classification values
        totals_durability = classifications.get('totals_durability', 'NONE')
        under_suggestion = classifications.get('under_suggestion', 'No Under recommendation')
        
        # CRITICAL: Get opponent signal from correct perspective with DSF
        opponent_data = classifications.get('opponent_under_15', {})
        if perspective == 'home':
            perspective_data = opponent_data.get('home_perspective', {})
            opponent_under_15 = perspective_data.get('final_verdict', False)
            
            # Get DSF stability if available
            dsf_stable = perspective_data.get('dsf_stable', True)
            dsf_assessments = opponent_data.get('dsf_assessments', {})
            away_dsf = dsf_assessments.get('away', {})
            dsf_stability_type = away_dsf.get('stability_type', 'LOW-VARIANCE')
        else:
            perspective_data = opponent_data.get('away_perspective', {})
            opponent_under_15 = perspective_data.get('final_verdict', False)
            
            # Get DSF stability if available
            dsf_stable = perspective_data.get('dsf_stable', True)
            dsf_assessments = opponent_data.get('dsf_assessments', {})
            home_dsf = dsf_assessments.get('home', {})
            dsf_stability_type = home_dsf.get('stability_type', 'LOW-VARIANCE')
        
        # Calculate score components
        durability_score = cls.RELIABILITY_WEIGHTS['totals_durability'].get(totals_durability, 0)
        under_score = cls.RELIABILITY_WEIGHTS['under_suggestion'].get(under_suggestion, 0)
        opponent_score = cls.RELIABILITY_WEIGHTS['opponent_under_15'].get(opponent_under_15, 0)
        
        # NEW: DSF penalty/reward
        dsf_score = cls.RELIABILITY_WEIGHTS['defensive_stability'].get(dsf_stability_type, 0)
        
        # Total score with DSF adjustment
        total_score = durability_score + under_score + opponent_score + dsf_score
        
        # Cap at 5, floor at -1 (DSF rejection)
        total_score = max(-1, min(5, total_score))
        
        # Get reliability level details
        reliability_info = cls.RELIABILITY_LEVELS.get(total_score, cls.RELIABILITY_LEVELS[0])
        
        # Build detailed breakdown with DSF
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
            },
            'defensive_stability': {
                'value': dsf_stability_type,
                'score': dsf_score,
                'weight': cls.RELIABILITY_WEIGHTS['defensive_stability'].get(dsf_stability_type, 0),
                'dsf_stable': dsf_stable
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
                'opponent_under_15': opponent_score,
                'defensive_stability': dsf_score
            },
            'perspective_used': perspective,
            'dsf_included': True,
            'dsf_stability': dsf_stability_type,
            'is_read_only': True,
            'metadata': {
                'score_range': '-1 to 5',
                'interpretation': 'Higher score indicates stronger under structure',
                'purpose': 'Informational reliability indicator only',
                'dsf_note': 'Score includes Defensive Stability Filter assessment'
            }
        }
    
    # =================== FULL CLASSIFICATION PIPELINE ===================
    
    @classmethod
    def run_full_classification(cls, home_data: Dict, away_data: Dict, 
                                perspective: str = 'home', include_dsf: bool = True) -> Dict[str, Any]:
        """
        RUN FULL CLASSIFICATION PIPELINE WITH DSF
        
        Validates data first, then runs all classification functions.
        Returns complete classification results or error state.
        
        This is the MAIN ENTRY POINT for the classifier.
        """
        # Step 1: Validate data
        is_valid, missing_fields, validated_data = cls.validate_last5_data(home_data, away_data)
        
        if not is_valid:
            return {
                'classification_error': True,
                'error_type': 'MISSING_DATA',
                'error_message': f'Missing/invalid last-5 data fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'is_valid': False,
                'averages': {
                    'home_goals_avg': 0.0,
                    'home_conceded_avg': 0.0,
                    'away_goals_avg': 0.0,
                    'away_conceded_avg': 0.0
                },
                'dominant_state': 'CLASSIFIER_ERROR',
                'totals_durability': 'NONE',
                'under_suggestion': 'No Under recommendation',
                'opponent_under_15': {},
                'reliability_home': {
                    'reliability_score': 0,
                    'reliability_label': 'NONE',
                    'reliability_description': 'Classifier unavailable due to missing data'
                },
                'validation_passed': False,
                'dsf_applied': False
            }
        
        # Step 2: Calculate averages for display
        home_goals_avg = validated_data['home']['goals_scored_last_5'] / 5
        home_conceded_avg = validated_data['home']['goals_conceded_last_5'] / 5
        away_goals_avg = validated_data['away']['goals_scored_last_5'] / 5
        away_conceded_avg = validated_data['away']['goals_conceded_last_5'] / 5
        
        # Step 3: Run all classification functions with DSF
        totals_durability = cls.classify_totals_durability(
            validated_data['home'], validated_data['away']
        )
        
        opponent_under_15 = cls.classify_opponent_under_15(
            validated_data['home'], validated_data['away'], include_dsf=include_dsf
        )
        
        under_suggestion = cls.suggest_under_market(
            validated_data['home'], validated_data['away']
        )
        
        # Step 4: Determine dominant match state (with DSF consideration)
        dominant_state = cls.determine_dominant_match_state(
            validated_data['home'], validated_data['away'], include_dsf=include_dsf
        )
        
        # Step 5: Compute reliability scores with DSF
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
            'dsf_applied': include_dsf,
            'dsf_rules': cls.get_dsf_rules() if include_dsf else None,
            'metadata': {
                'version': '1.6',
                'data_source': 'last_5_matches_only',
                'read_only': True,
                'purpose': 'Informational classification only',
                'dsf_integrated': include_dsf
            }
        }
    
    @classmethod
    def determine_dominant_match_state(cls, home_data: Dict, away_data: Dict, 
                                       include_dsf: bool = True) -> str:
        """
        DETERMINEDOMINANT MATCH STATE WITH DSF CONSIDERATION
        
        Simplified state determination based on scoring/conceding patterns.
        Uses last 5 matches data only.
        """
        # Extract and calculate averages
        home_goals_avg = home_data.get('goals_scored_last_5', 0) / 5
        home_conceded_avg = home_data.get('goals_conceded_last_5', 0) / 5
        away_goals_avg = away_data.get('goals_scored_last_5', 0) / 5
        away_conceded_avg = away_data.get('goals_conceded_last_5', 0) / 5
        
        # Check for DSF instability if include_dsf is True
        if include_dsf:
            home_concede_data = home_data.get('concede_last_5_list')
            away_concede_data = away_data.get('concede_last_5_list')
            
            home_dsf_unstable = False
            away_dsf_unstable = False
            
            if home_concede_data and isinstance(home_concede_data, list):
                home_dsf = cls.assess_defensive_stability(home_concede_data)
                home_dsf_unstable = not home_dsf.get('is_stable', True)
            
            if away_concede_data and isinstance(away_concede_data, list):
                away_dsf = cls.assess_defensive_stability(away_concede_data)
                away_dsf_unstable = not away_dsf.get('is_stable', True)
            
            # If either defense is DSF unstable, mark as structurally unstable
            if home_dsf_unstable or away_dsf_unstable:
                return "DSF_UNSTABLE"
        
        # Original state determination logic
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
        CREATE UI-FRIENDLY DISPLAY DATA WITH DSF
        
        Transforms classification results into a format suitable for
        Streamlit UI display with clean formatting.
        """
        if classification_result.get('classification_error', False):
            return {
                'display_type': 'ERROR',
                'error_message': classification_result.get('error_message', 'Unknown error'),
                'missing_fields': classification_result.get('missing_fields', []),
                'suggestion': 'Check CSV data for goals_scored_last_5 and goals_conceded_last_5 fields',
                'dsf_applied': False
            }
        
        # Extract data
        averages = classification_result.get('averages', {})
        totals_durability = classification_result.get('totals_durability', 'NONE')
        under_suggestion = classification_result.get('under_suggestion', 'No Under recommendation')
        dominant_state = classification_result.get('dominant_state', 'NEUTRAL')
        reliability_home = classification_result.get('reliability_home', {})
        opponent_under_15 = classification_result.get('opponent_under_15', {})
        dsf_applied = classification_result.get('dsf_applied', False)
        
        # Get state configuration
        state_config = cls.STATE_CONFIG.get(dominant_state, cls.STATE_CONFIG['NEUTRAL'])
        
        # Determine durability display
        durability_config = {
            'STABLE': {'emoji': '🟢', 'color': '#16A34A', 'label': 'STABLE'},
            'FRAGILE': {'emoji': '🟡', 'color': '#F59E0B', 'label': 'FRAGILE'},
            'NONE': {'emoji': '⚫', 'color': '#6B7280', 'label': 'NONE'}
        }
        durability_info = durability_config.get(totals_durability, durability_config['NONE'])
        
        # Extract DSF data if available
        dsf_data = {}
        if dsf_applied and opponent_under_15:
            dsf_assessments = opponent_under_15.get('dsf_assessments', {})
            if dsf_assessments:
                dsf_data = {
                    'home': dsf_assessments.get('home'),
                    'away': dsf_assessments.get('away'),
                    'home_perspective': opponent_under_15.get('home_perspective', {}),
                    'away_perspective': opponent_under_15.get('away_perspective', {})
                }
        
        # Create UI data structure
        return {
            'display_type': 'CLASSIFICATION',
            'averages': {
                'home_goals': averages.get('home_goals_avg', 0.0),
                'home_conceded': averages.get('home_conceded_avg', 0.0),
                'away_goals': averages.get('away_goals_avg', 0.0),
                'away_conceded': averages.get('away_conceded_avg', 0.0)
            },
            'match_state': {
                'code': dominant_state,
                'emoji': state_config['emoji'],
                'color': state_config['color'],
                'label': state_config['label'],
                'is_dsf_unstable': dominant_state == 'DSF_UNSTABLE'
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
                'breakdown': reliability_home.get('score_breakdown', {}),
                'dsf_included': reliability_home.get('dsf_included', False)
            },
            'defensive_analysis': {
                'home_strong_defense': averages.get('home_conceded_avg', 0) <= cls.OPPONENT_UNDER_15_THRESHOLD,
                'away_strong_defense': averages.get('away_conceded_avg', 0) <= cls.OPPONENT_UNDER_15_THRESHOLD,
                'threshold': cls.OPPONENT_UNDER_15_THRESHOLD,
                'home_perspective_final': opponent_under_15.get('home_perspective', {}).get('final_verdict', False),
                'away_perspective_final': opponent_under_15.get('away_perspective', {}).get('final_verdict', False)
            },
            'dsf_data': dsf_data,
            'dsf_applied': dsf_applied,
            'dsf_rules': cls.get_dsf_rules() if dsf_applied else None,
            'metadata': {
                'data_source': 'Last 5 matches only',
                'read_only': True,
                'version': 'v1.6',
                'dsf_integrated': dsf_applied
            }
        }
    
    @classmethod
    def generate_streamlit_ui(cls, home_team: str, away_team: str, 
                            home_data: Dict, away_data: Dict,
                            include_dsf: bool = True) -> Dict[str, Any]:
        """
        GENERATE COMPLETE STREAMLIT UI DATA WITH DSF
        
        One function to run everything and return data ready for Streamlit display.
        This is the recommended integration point for your app.py.
        """
        # Step 1: Run full classification with DSF
        classification_result = cls.run_full_classification(
            home_data, away_data, include_dsf=include_dsf
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
        
        # Step 5: Add Chelsea/Bournemouth example if applicable
        if include_dsf and 'dsf_data' in ui_data and ui_data['dsf_data']:
            # Check if pattern matches Chelsea false positive
            for team_key in ['home', 'away']:
                dsf_info = ui_data['dsf_data'].get(team_key)
                if dsf_info and dsf_info.get('example_analysis'):
                    ui_data['example_case'] = {
                        'type': 'CHELSEA_FALSE_POSITIVE_PATTERN',
                        'team': team_key,
                        'analysis': dsf_info['example_analysis'],
                        'lesson': 'Average ≠ Preservation - defense numerically preserved but structurally fragile'
                    }
        
        return ui_data
    
    # =================== UTILITY FUNCTIONS ===================
    
    @classmethod
    def get_data_requirements(cls, include_dsf: bool = True) -> Dict[str, Any]:
        """
        GET DATA REQUIREMENTS FOR CSV/INPUT WITH DSF
        
        Returns the exact data fields needed for classification.
        Helpful for CSV preparation and validation.
        """
        requirements = {
            'required_fields': cls.MINIMUM_DATA_REQUIREMENTS,
            'data_format': 'Sum totals for last 5 matches (not averages)',
            'examples': {
                'goals_scored_last_5': 'Total goals scored in last 5 matches (e.g., 8)',
                'goals_conceded_last_5': 'Total goals conceded in last 5 matches (e.g., 4)'
            },
            'validation_rules': [
                'Values must be integers ≥ 0',
                'Values represent SUM totals, not averages',
                'Divide by 5 internally to get averages'
            ]
        }
        
        if include_dsf:
            requirements['dsf_requirements'] = {
                'recommended_field': 'concede_last_5_list',
                'format': 'List of goals conceded in each of last 5 matches',
                'example': '[0, 1, 2, 0, 2] for Chelsea pattern',
                'alternative': 'Can be derived from match-by-match data',
                'purpose': 'Enables Defensive Stability Filter (prevents false positives)'
            }
        
        return requirements
    
    @classmethod
    def check_data_quality(cls, home_data: Dict, away_data: Dict, 
                          include_dsf_check: bool = True) -> Dict[str, Any]:
        """
        CHECK DATA QUALITY AND PROVIDE FEEDBACK WITH DSF
        
        Useful for debugging data issues before classification.
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
                suggestions.append("Home team data shows all zeros - verify this is correct")
            if away_goals_avg == 0 and away_conceded_avg == 0:
                suggestions.append("Away team data shows all zeros - verify this is correct")
            
            # DSF data check
            dsf_ready = False
            dsf_suggestions = []
            if include_dsf_check:
                home_concede_list = home_data.get('concede_last_5_list')
                away_concede_list = away_data.get('concede_last_5_list')
                
                if home_concede_list and away_concede_list:
                    dsf_ready = True
                    # Quick DSF assessment
                    home_dsf = cls.assess_defensive_stability(home_concede_list)
                    away_dsf = cls.assess_defensive_stability(away_concede_list)
                    
                    if not home_dsf.get('is_stable', True):
                        dsf_suggestions.append(f"Home defense shows DSF instability: {home_dsf.get('stability_type')}")
                    if not away_dsf.get('is_stable', True):
                        dsf_suggestions.append(f"Away defense shows DSF instability: {away_dsf.get('stability_type')}")
                else:
                    dsf_suggestions.append("Add 'concede_last_5_list' field to enable Defensive Stability Filter")
            
            suggestions.extend(dsf_suggestions)
        else:
            home_goals_avg = home_conceded_avg = away_goals_avg = away_conceded_avg = 0
            quality_score = 0
            suggestions = [f"Fix missing fields: {', '.join(missing_fields)}"]
            dsf_ready = False
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_score,
            'missing_fields': missing_fields,
            'calculated_averages': {
                'home_goals': round(home_goals_avg, 2),
                'home_conceded': round(home_conceded_avg, 2),
                'away_goals': round(away_goals_avg, 2),
                'away_conceded': round(away_conceded_avg, 2)
            },
            'suggestions': suggestions,
            'data_quality': 'GOOD' if is_valid else 'POOR',
            'can_run_classifier': is_valid,
            'dsf_ready': dsf_ready if is_valid else False,
            'dsf_note': 'Defensive Stability Filter requires concede_last_5_list field'
        }
    
    @classmethod
    def analyze_chelsea_bournemouth_pattern(cls, concede_data: List[int]) -> Dict[str, Any]:
        """
        ANALYZE CHELSEA/BOURNEMOUTH FALSE POSITIVE PATTERN
        
        Specifically checks for the pattern that caused the system failure:
        - Average ≤1.0 (numerically preserved)
        - ≥2 volatility spikes (structurally fragile)
        """
        dsf_assessment = cls.assess_defensive_stability(concede_data)
        
        is_chelsea_pattern = (
            dsf_assessment.get('concede_avg', 0) <= 1.0 and
            dsf_assessment.get('volatility_spikes', 0) >= 2
        )
        
        return {
            'is_chelsea_pattern': is_chelsea_pattern,
            'dsf_assessment': dsf_assessment,
            'pattern_analysis': {
                'numerical_preservation': dsf_assessment.get('concede_avg', 0) <= 1.0,
                'structural_preservation': dsf_assessment.get('is_stable', True),
                'contradiction': is_chelsea_pattern,
                'lesson': 'Average ≠ Preservation'
            },
            'system_impact': {
                'tier_1+_lock': 'Would be granted without DSF',
                'tier_1+_lock_with_dsf': 'REJECTED if DSF applied',
                'false_positive_prevented': is_chelsea_pattern
            },
            'example_data': {
                'chelsea_actual': [0, 1, 2, 0, 2],
                'bournemouth_result': 'Scored 2 goals',
                'system_failure': 'UNDER 1.5 lock granted, Bournemouth scored 2'
            }
        }


# =================== EXAMPLE USAGE ===================
if __name__ == "__main__":
    print("=== BRUTBALL MATCH STATE CLASSIFIER v1.6 WITH DSF ===")
    print("Principle: Average ≠ Preservation")
    print("Fixes Chelsea vs Bournemouth false positives\n")
    
    # Example data (Chelsea pattern - would cause false positive)
    chelsea_pattern_data = {
        'goals_scored_last_5': 6,
        'goals_conceded_last_5': 5,  # Sum: 0+1+2+0+2 = 5 (avg=1.0)
        'concede_last_5_list': [0, 1, 2, 0, 2]  # DSF data
    }
    
    bournemouth_data = {
        'goals_scored_last_5': 9,
        'goals_conceded_last_5': 7,
        'concede_last_5_list': [1, 2, 1, 1, 2]
    }
    
    # Example 1: DSF assessment
    print("=== DSF ASSESSMENT (Chelsea Pattern) ===")
    dsf_result = MatchStateClassifier.assess_defensive_stability(
        chelsea_pattern_data['concede_last_5_list']
    )
    print(f"Concede data: {dsf_result['concede_data']}")
    print(f"Average: {dsf_result['concede_avg']}")
    print(f"Volatility spikes: {dsf_result['volatility_spikes']}")
    print(f"Stability type: {dsf_result['stability_type']}")
    print(f"DSF verdict: {dsf_result['dsf_verdict']}")
    print(f"Lock allowed: {dsf_result['lock_allowed']}")
    
    if dsf_result.get('example_analysis'):
        print(f"Pattern match: {dsf_result['example_analysis']['type']}")
        print(f"Lesson: {dsf_result['example_analysis']['lesson']}")
    
    # Example 2: Apply DSF to edge lock
    print("\n=== APPLY DSF TO EDGE LOCK ===")
    lock_result = MatchStateClassifier.apply_dsf_to_edge_lock(
        team_name="Chelsea",
        concede_data=chelsea_pattern_data['concede_last_5_list'],
        current_lock_status=True,  # Would be granted without DSF
        confidence_tier="WEAK 🟡"
    )
    
    print(f"Original lock: {lock_result['original_analysis']['lock']}")
    print(f"DSF assessment: {lock_result['dsf_assessment']['dsf_verdict']}")
    print(f"Final lock: {lock_result['final_verdict']['lock']}")
    print(f"Adjusted confidence: {lock_result['final_verdict']['confidence']}")
    
    if lock_result['final_verdict']['rejection_reason']:
        print(f"Rejection reason: {lock_result['final_verdict']['rejection_reason']}")
    
    # Example 3: Full classification
    print("\n=== FULL CLASSIFICATION WITH DSF ===")
    classification = MatchStateClassifier.run_full_classification(
        chelsea_pattern_data, bournemouth_data, include_dsf=True
    )
    
    if classification['classification_error']:
        print(f"ERROR: {classification['error_message']}")
    else:
        print(f"Match state: {classification['dominant_state']}")
        print(f"Durability: {classification['totals_durability']}")
        print(f"Under suggestion: {classification['under_suggestion']}")
        print(f"Reliability score: {classification['reliability_home']['reliability_score']}")
        print(f"DSF applied: {classification['dsf_applied']}")
    
    # Example 4: Chelsea/Bournemouth pattern analysis
    print("\n=== CHELSEA/BOURNEMOUTH PATTERN ANALYSIS ===")
    pattern_analysis = MatchStateClassifier.analyze_chelsea_bournemouth_pattern(
        chelsea_pattern_data['concede_last_5_list']
    )
    
    print(f"Is Chelsea pattern: {pattern_analysis['is_chelsea_pattern']}")
    print(f"Numerical preservation: {pattern_analysis['pattern_analysis']['numerical_preservation']}")
    print(f"Structural preservation: {pattern_analysis['pattern_analysis']['structural_preservation']}")
    print(f"False positive prevented: {pattern_analysis['system_impact']['false_positive_prevented']}")
    
    # Get DSF rules
    print("\n=== DSF RULES ===")
    dsf_rules = MatchStateClassifier.get_dsf_rules()
    print(f"Principle: {dsf_rules['principle']}")
    print(f"Rule: {dsf_rules['rule']}")
    print(f"Example: {dsf_rules['example_failure']['chelsea_bournemouth']}")
    print(f"Lock requirement: {dsf_rules['thresholds']['lock_requirement']}")
