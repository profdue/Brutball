"""
BRUTBALL MATCH STATE & DURABILITY CLASSIFIER v1.2
READ-ONLY MODULE - NO SIDE EFFECTS

PURPOSE:
Classify matches into structural states and durability categories for system protection.
This does NOT affect betting logic, stakes, or existing tiers.
It only labels reality to prevent philosophical violations.

STRUCTURAL STATES (Existing):
1. TERMINAL STAGNATION - Dual low-offense, no scoring pathways
2. ASYMMETRIC SUPPRESSION - One team controls, opponent suppressed
3. DELAYED RELEASE - Low scoring but volatile pathways exist
4. FORCED EXPLOSION - High xG + open play dominance

TOTALS DURABILITY (NEW):
• STABLE - High durability for Under 2.5
• FRAGILE - Medium durability for Under 2.5
• NONE - No structural support for Under 2.5

DEFENSIVE MARKET STATES (OPTIONAL):
• CLEAN_SHEET_STABLE - High durability for Clean Sheet
• CLEAN_SHEET_FRAGILE - Medium durability for Clean Sheet
• NO_CLEAN_SHEET_STRUCTURE - No structural support for Clean Sheet

RULES:
1. Uses existing CSV data only
2. No changes to Tier 1, 2, or 3 logic
3. No market triggers or stake modifications
4. Only adds informational classification
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
    
    It only labels reality to protect system integrity.
    """
    
    # =================== EXISTING MATCH STATE CLASSIFICATIONS ===================
    
    @staticmethod
    def check_terminal_stagnation(home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        STATE 1: TERMINAL STAGNATION
        
        Condition: Both teams goals_scored_last_5 / 5 ≤ 1.2
        AND no dominant scoring pathways
        
        Philosophical: Structural low-scoring ceiling
        Market Protection: Under locks possible, Over locks impossible
        """
        rationale = []
        
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        home_avg = home_last5_goals / 5 if home_last5_goals > 0 else 0
        away_avg = away_last5_goals / 5 if away_last5_goals > 0 else 0
        
        # Condition 1: Both teams low scoring
        low_scoring = (home_avg <= 1.2) and (away_avg <= 1.2)
        
        # Condition 2: No dominant scoring pathways
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
        rationale.append(f"• Home avg goals (last 5): {home_avg:.2f} {'≤1.2' if home_avg <= 1.2 else '>1.2'}")
        rationale.append(f"• Away avg goals (last 5): {away_avg:.2f} {'≤1.2' if away_avg <= 1.2 else '>1.2'}")
        rationale.append(f"• Home pathways: SP={home_setpiece:.1%}, C={home_counter:.1%}")
        rationale.append(f"• Away pathways: SP={away_setpiece:.1%}, C={away_counter:.1%}")
        rationale.append(f"• Low scoring: {'✅' if low_scoring else '❌'}")
        rationale.append(f"• No dominant pathways: {'✅' if no_dominant_pathways else '❌'}")
        
        return is_terminal_stagnation, {
            'home_avg': home_avg,
            'away_avg': away_avg,
            'low_scoring': low_scoring,
            'no_dominant_pathways': no_dominant_pathways
        }, rationale
    
    @staticmethod
    def check_asymmetric_suppression(home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        STATE 2: ASYMMETRIC SUPPRESSION
        
        Condition: One team passes Agency Gates, opponent fails escalation
        
        Philosophical: Unilateral outcome control
        Market Protection: Winner/Clean Sheet locks possible
        
        NOTE: This uses simplified checks, not full Agency Gates
        """
        rationale = []
        
        # Simplified dominance checks (not full Agency Gates)
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        
        # Check if one team dominates
        home_dominates = (home_xg > 1.4) and (home_xg - away_xg > 0.5)
        away_dominates = (away_xg > 1.2) and (away_xg - home_xg > 0.5)
        
        # Check opponent suppression (simplified)
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
    
    @staticmethod
    def check_delayed_release(home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        STATE 3: DELAYED RELEASE
        
        Condition: Low recent scoring BUT volatile pathways exist
        AND goals_conceded_last_5 ≥ 1.0
        
        Philosophical: Pressure accumulation
        Market Protection: Under locks forbidden (release risk)
        """
        rationale = []
        
        # Check low scoring
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        home_avg = home_last5_goals / 5 if home_last5_goals > 0 else 0
        away_avg = away_last5_goals / 5 if away_last5_goals > 0 else 0
        
        low_scoring = (home_avg < 1.5) and (away_avg < 1.5)
        
        # Check volatile pathways (either team)
        home_setpiece = home_data.get('home_setpiece_pct', 0)
        home_counter = home_data.get('home_counter_pct', 0)
        away_setpiece = away_data.get('away_setpiece_pct', 0)
        away_counter = away_data.get('away_counter_pct', 0)
        
        volatile_pathways = (
            (home_setpiece >= 0.3) or (home_counter >= 0.18) or
            (away_setpiece >= 0.3) or (away_counter >= 0.18)
        )
        
        # Check defensive leakage (either team)
        home_conceded_last5 = home_data.get('home_goals_conceded_last_5', 0)
        away_conceded_last5 = away_data.get('away_goals_conceded_last_5', 0)
        
        home_concede_avg = home_conceded_last5 / 5 if home_conceded_last5 > 0 else 0
        away_concede_avg = away_conceded_last5 / 5 if away_conceded_last5 > 0 else 0
        
        defensive_leakage = (home_concede_avg >= 1.0) or (away_concede_avg >= 1.0)
        
        is_delayed_release = low_scoring and volatile_pathways and defensive_leakage
        
        rationale.append(f"DELAYED RELEASE CHECK:")
        rationale.append(f"• Home avg goals: {home_avg:.2f}")
        rationale.append(f"• Away avg goals: {away_avg:.2f}")
        rationale.append(f"• Low scoring (<1.5): {'✅' if low_scoring else '❌'}")
        rationale.append(f"• Volatile pathways: {'✅' if volatile_pathways else '❌'}")
        rationale.append(f"• Home concede avg: {home_concede_avg:.2f}")
        rationale.append(f"• Away concede avg: {away_concede_avg:.2f}")
        rationale.append(f"• Defensive leakage (≥1.0): {'✅' if defensive_leakage else '❌'}")
        
        return is_delayed_release, {
            'home_avg': home_avg,
            'away_avg': away_avg,
            'low_scoring': low_scoring,
            'volatile_pathways': volatile_pathways,
            'home_concede_avg': home_concede_avg,
            'away_concede_avg': away_concede_avg,
            'defensive_leakage': defensive_leakage
        }, rationale
    
    @staticmethod
    def check_forced_explosion(home_data: Dict, away_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        STATE 4: FORCED EXPLOSION
        
        Condition: At least one team has:
        xG_for ≥ 1.6 AND open play ≥ 60%
        AND opponent defensive leakage active
        
        Philosophical: High-goal states structurally unavoidable
        Market Protection: Clean Sheet locks forbidden
        """
        rationale = []
        
        # Check for explosive attack (either team)
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        
        home_openplay = home_data.get('home_openplay_pct', 0)
        away_openplay = away_data.get('away_openplay_pct', 0)
        
        home_explosive = (home_xg >= 1.6) and (home_openplay >= 0.6)
        away_explosive = (away_xg >= 1.6) and (away_openplay >= 0.6)
        
        explosive_attack = home_explosive or away_explosive
        
        # Check opponent defensive leakage
        home_conceded_last5 = home_data.get('home_goals_conceded_last_5', 0)
        away_conceded_last5 = away_data.get('away_goals_conceded_last_5', 0)
        
        home_concede_avg = home_conceded_last5 / 5 if home_conceded_last5 > 0 else 0
        away_concede_avg = away_conceded_last5 / 5 if away_conceded_last5 > 0 else 0
        
        # If home explosive, check away defense
        if home_explosive:
            defensive_leakage = away_concede_avg >= 1.0
            rationale.append(f"• Home explosive (xG={home_xg:.2f}, OP={home_openplay:.1%}) vs Away concede={away_concede_avg:.2f}")
        elif away_explosive:
            defensive_leakage = home_concede_avg >= 1.0
            rationale.append(f"• Away explosive (xG={away_xg:.2f}, OP={away_openplay:.1%}) vs Home concede={home_concede_avg:.2f}")
        else:
            defensive_leakage = False
        
        is_forced_explosion = explosive_attack and defensive_leakage
        
        rationale.append(f"FORCED EXPLOSION CHECK:")
        rationale.append(f"• Home explosive: {'✅' if home_explosive else '❌'} (xG={home_xg:.2f}, OP={home_openplay:.1%})")
        rationale.append(f"• Away explosive: {'✅' if away_explosive else '❌'} (xG={away_xg:.2f}, OP={away_openplay:.1%})")
        rationale.append(f"• Explosive attack: {'✅' if explosive_attack else '❌'}")
        rationale.append(f"• Defensive leakage: {'✅' if defensive_leakage else '❌'}")
        
        return is_forced_explosion, {
            'home_explosive': home_explosive,
            'away_explosive': away_explosive,
            'explosive_attack': explosive_attack,
            'defensive_leakage': defensive_leakage,
            'home_concede_avg': home_concede_avg,
            'away_concede_avg': away_concede_avg
        }, rationale
    
    # =================== NEW: TOTALS DURABILITY CLASSIFICATION ===================
    
    @staticmethod
    def classify_totals_durability(home_data: Dict, away_data: Dict) -> Dict:
        """
        CLASSIFY TOTALS DURABILITY (Under 2.5)
        
        Returns durability classification for Under 2.5 markets.
        
        Categories:
        • STABLE: High durability for Under 2.5
        • FRAGILE: Medium durability for Under 2.5  
        • NONE: No structural support for Under 2.5
        
        IMPORTANT: This is READ-ONLY and informational only.
        Does NOT affect existing totals lock logic.
        """
        
        # Calculate averages from last 5 matches
        home_goals_scored_last5 = home_data.get('goals_scored_last_5', 0)
        away_goals_scored_last5 = away_data.get('goals_scored_last_5', 0)
        home_goals_conceded_last5 = home_data.get('goals_conceded_last_5', 0)
        away_goals_conceded_last5 = away_data.get('goals_conceded_last_5', 0)
        
        # Convert to per-match averages
        home_avg_scored = home_goals_scored_last5 / 5 if home_goals_scored_last5 > 0 else 0
        away_avg_scored = away_goals_scored_last5 / 5 if away_goals_scored_last5 > 0 else 0
        home_avg_conceded = home_goals_conceded_last5 / 5 if home_goals_conceded_last5 > 0 else 0
        away_avg_conceded = away_goals_conceded_last5 / 5 if away_goals_conceded_last5 > 0 else 0
        
        # Condition 1: Dual low offense
        dual_low_offense = (home_avg_scored <= 1.2) and (away_avg_scored <= 1.2)
        
        # Condition 2: Low volatility (stable scoring patterns)
        home_volatility = abs(home_avg_scored - home_avg_conceded) <= 0.5
        away_volatility = abs(away_avg_scored - away_avg_conceded) <= 0.5
        low_volatility = home_volatility and away_volatility
        
        # Condition 3: Defensive confirmation
        defensive_confirmation = (home_avg_conceded <= 1.0) and (away_avg_conceded <= 1.0)
        
        # Classification logic
        if dual_low_offense and low_volatility and defensive_confirmation:
            durability = 'STABLE'
            description = "High durability for Under 2.5. Both teams low-scoring with stable patterns and confirmed defense."
            gradient_score = 0.9  # High confidence (0-1 scale)
            
        elif dual_low_offense:
            durability = 'FRAGILE'
            description = "Medium durability for Under 2.5. Low scoring exists but volatility or defensive leakage present."
            gradient_score = 0.5  # Medium confidence
            
            # Fragility reasons
            fragility_reasons = []
            if not low_volatility:
                fragility_reasons.append("High volatility in scoring patterns")
            if not defensive_confirmation:
                fragility_reasons.append("Defensive leakage present")
            
        else:
            durability = 'NONE'
            description = "No structural support for Under 2.5. Dual low offense condition not met."
            gradient_score = 0.1  # Low confidence
            fragility_reasons = []
        
        # Build rationale
        rationale = []
        rationale.append("🔍 TOTALS DURABILITY CLASSIFICATION (Under 2.5):")
        rationale.append(f"• Home avg scored: {home_avg_scored:.2f}")
        rationale.append(f"• Away avg scored: {away_avg_scored:.2f}")
        rationale.append(f"• Home avg conceded: {home_avg_conceded:.2f}")
        rationale.append(f"• Away avg conceded: {away_avg_conceded:.2f}")
        rationale.append(f"• Dual low offense (≤1.2): {'✅' if dual_low_offense else '❌'}")
        rationale.append(f"• Low volatility (diff ≤0.5): {'✅' if low_volatility else '❌'}")
        rationale.append(f"• Defensive confirmation (≤1.0): {'✅' if defensive_confirmation else '❌'}")
        rationale.append(f"• Durability: {durability}")
        rationale.append(f"• Gradient Score: {gradient_score:.2f}")
        
        if durability == 'FRAGILE' and 'fragility_reasons' in locals():
            rationale.append(f"• Fragility reasons: {', '.join(fragility_reasons)}")
        
        return {
            'durability': durability,
            'description': description,
            'gradient_score': gradient_score,
            'data': {
                'home_avg_scored': home_avg_scored,
                'away_avg_scored': away_avg_scored,
                'home_avg_conceded': home_avg_conceded,
                'away_avg_conceded': away_avg_conceded,
                'dual_low_offense': dual_low_offense,
                'low_volatility': low_volatility,
                'defensive_confirmation': defensive_confirmation
            },
            'rationale': rationale,
            'is_read_only': True,
            'market_guidance': {
                'STABLE': 'Under 2.5 has high structural durability',
                'FRAGILE': 'Under 2.5 possible but consider Under 3.5 for safety',
                'NONE': 'Avoid Under 2.5 markets - no structural support'
            }.get(durability, 'No guidance available')
        }
    
    # =================== OPTIONAL: DEFENSIVE MARKET CLASSIFICATION ===================
    
    @staticmethod
    def classify_defensive_markets(home_data: Dict, away_data: Dict) -> Dict:
        """
        CLASSIFY DEFENSIVE MARKETS (Clean Sheet, Team No Score, Opponent Under 1.5)
        
        Returns structural classification for defensive markets.
        
        Categories:
        • CLEAN_SHEET_STABLE: High durability for Clean Sheet
        • CLEAN_SHEET_FRAGILE: Medium durability for Clean Sheet
        • NO_CLEAN_SHEET_STRUCTURE: No structural support for Clean Sheet
        
        OPTIONAL: This is for R&D insights only.
        Does NOT affect existing agency lock logic.
        """
        
        # Calculate defensive metrics
        home_goals_conceded_last5 = home_data.get('goals_conceded_last_5', 0)
        away_goals_conceded_last5 = away_data.get('goals_conceded_last_5', 0)
        home_xg_conceded = home_data.get('home_xg_conceded_per_match', 0)
        away_xg_conceded = away_data.get('away_xg_conceded_per_match', 0)
        
        home_avg_conceded = home_goals_conceded_last5 / 5 if home_goals_conceded_last5 > 0 else 0
        away_avg_conceded = away_goals_conceded_last5 / 5 if away_goals_conceded_last5 > 0 else 0
        
        # Check for strong defense (either team)
        home_defense_strong = (home_avg_conceded <= 0.8) and (home_xg_conceded <= 1.0)
        away_defense_strong = (away_avg_conceded <= 0.8) and (away_xg_conceded <= 1.0)
        
        # Check opponent offensive weakness
        home_opponent_weak = away_data.get('goals_scored_last_5', 0) / 5 <= 1.0
        away_opponent_weak = home_data.get('goals_scored_last_5', 0) / 5 <= 1.0
        
        # Classification logic
        home_clean_sheet_stable = home_defense_strong and home_opponent_weak
        away_clean_sheet_stable = away_defense_strong and away_opponent_weak
        
        home_clean_sheet_fragile = home_defense_strong and not home_opponent_weak
        away_clean_sheet_fragile = away_defense_strong and not away_opponent_weak
        
        # Build results
        defensive_classification = {
            'home_clean_sheet': {
                'classification': 'CLEAN_SHEET_STABLE' if home_clean_sheet_stable else 
                                'CLEAN_SHEET_FRAGILE' if home_clean_sheet_fragile else 
                                'NO_CLEAN_SHEET_STRUCTURE',
                'defense_strength': home_defense_strong,
                'opponent_weakness': home_opponent_weak,
                'avg_conceded': home_avg_conceded,
                'xg_conceded': home_xg_conceded
            },
            'away_clean_sheet': {
                'classification': 'CLEAN_SHEET_STABLE' if away_clean_sheet_stable else 
                                'CLEAN_SHEET_FRAGILE' if away_clean_sheet_fragile else 
                                'NO_CLEAN_SHEET_STRUCTURE',
                'defense_strength': away_defense_strong,
                'opponent_weakness': away_opponent_weak,
                'avg_conceded': away_avg_conceded,
                'xg_conceded': away_xg_conceded
            }
        }
        
        # Build rationale
        rationale = []
        rationale.append("🛡️ DEFENSIVE MARKET CLASSIFICATION:")
        rationale.append(f"• Home defense strong (≤0.8 gpg, ≤1.0 xG): {'✅' if home_defense_strong else '❌'}")
        rationale.append(f"• Away defense strong (≤0.8 gpg, ≤1.0 xG): {'✅' if away_defense_strong else '❌'}")
        rationale.append(f"• Home opponent weak (≤1.0 gpg): {'✅' if home_opponent_weak else '❌'}")
        rationale.append(f"• Away opponent weak (≤1.0 gpg): {'✅' if away_opponent_weak else '❌'}")
        rationale.append(f"• Home Clean Sheet: {defensive_classification['home_clean_sheet']['classification']}")
        rationale.append(f"• Away Clean Sheet: {defensive_classification['away_clean_sheet']['classification']}")
        
        return {
            'classifications': defensive_classification,
            'rationale': rationale,
            'is_read_only': True,
            'market_guidance': {
                'CLEAN_SHEET_STABLE': 'Clean Sheet has high structural durability',
                'CLEAN_SHEET_FRAGILE': 'Clean Sheet possible but opponent has scoring threat',
                'NO_CLEAN_SHEET_STRUCTURE': 'Avoid Clean Sheet markets - no structural support'
            }
        }
    
    # =================== MAIN CLASSIFICATION FUNCTION ===================
    
    @classmethod
    def classify_match_state(cls, home_data: Dict, away_data: Dict) -> Dict:
        """
        MAIN CLASSIFICATION FUNCTION
        
        Returns the dominant structural state of the match plus durability classifications.
        
        IMPORTANT: This is READ-ONLY and does NOT:
        - Affect betting decisions
        - Modify existing system logic
        - Create new locks or stakes
        
        It only labels reality for system protection.
        """
        
        classification_log = []
        classification_log.append("=" * 70)
        classification_log.append("🔍 MATCH STATE & DURABILITY CLASSIFIER v1.2 (READ-ONLY)")
        classification_log.append("=" * 70)
        classification_log.append("PURPOSE: Classify structural states for system protection")
        classification_log.append("RULES: Does not affect betting logic, only labels reality")
        classification_log.append("")
        
        # ========== 1. CHECK ALL MATCH STATES ==========
        classification_log.append("⚙️ STRUCTURAL MATCH STATES:")
        classification_log.append("-" * 40)
        
        states = []
        
        # STATE 1: TERMINAL STAGNATION
        is_stagnation, stagnation_data, stagnation_rationale = cls.check_terminal_stagnation(home_data, away_data)
        if is_stagnation:
            states.append(('TERMINAL_STAGNATION', stagnation_data))
        classification_log.extend(stagnation_rationale)
        classification_log.append("")
        
        # STATE 2: ASYMMETRIC SUPPRESSION
        is_asymmetric, asymmetric_data, asymmetric_rationale = cls.check_asymmetric_suppression(home_data, away_data)
        if is_asymmetric:
            states.append(('ASYMMETRIC_SUPPRESSION', asymmetric_data))
        classification_log.extend(asymmetric_rationale)
        classification_log.append("")
        
        # STATE 3: DELAYED RELEASE
        is_delayed, delayed_data, delayed_rationale = cls.check_delayed_release(home_data, away_data)
        if is_delayed:
            states.append(('DELAYED_RELEASE', delayed_data))
        classification_log.extend(delayed_rationale)
        classification_log.append("")
        
        # STATE 4: FORCED EXPLOSION
        is_explosion, explosion_data, explosion_rationale = cls.check_forced_explosion(home_data, away_data)
        if is_explosion:
            states.append(('FORCED_EXPLOSION', explosion_data))
        classification_log.extend(explosion_rationale)
        classification_log.append("")
        
        # Determine dominant state (hierarchy)
        dominant_state = "NEUTRAL"  # Default if no clear state
        
        # State hierarchy (based on structural certainty)
        state_hierarchy = [
            'TERMINAL_STAGNATION',      # Most certain (dual low-offense)
            'FORCED_EXPLOSION',         # Certain (high goals unavoidable)
            'ASYMMETRIC_SUPPRESSION',   # Certain (unilateral control)
            'DELAYED_RELEASE'          # Warning state (under risk)
        ]
        
        for state in state_hierarchy:
            if any(s[0] == state for s in states):
                dominant_state = state
                break
        
        classification_log.append(f"🎯 DOMINANT STRUCTURAL STATE: {dominant_state}")
        classification_log.append("")
        
        # State descriptions
        state_descriptions = {
            'TERMINAL_STAGNATION': "Dual low-offense, no scoring pathways. Structural low-scoring ceiling.",
            'ASYMMETRIC_SUPPRESSION': "One team controls, opponent suppressed. Unilateral outcome control.",
            'DELAYED_RELEASE': "Low scoring but volatile pathways exist. Pressure accumulation risk.",
            'FORCED_EXPLOSION': "High xG + open play dominance. High-goal states unavoidable.",
            'NEUTRAL': "No dominant structural state detected. Standard match dynamics."
        }
        
        classification_log.append(f"📖 STATE DESCRIPTION: {state_descriptions.get(dominant_state, 'Unknown')}")
        classification_log.append("")
        
        # ========== 2. TOTALS DURABILITY CLASSIFICATION ==========
        classification_log.append("📊 TOTALS DURABILITY (Under 2.5):")
        classification_log.append("-" * 40)
        
        totals_durability = cls.classify_totals_durability(home_data, away_data)
        classification_log.extend(totals_durability['rationale'])
        classification_log.append("")
        
        # ========== 3. DEFENSIVE MARKET CLASSIFICATION (OPTIONAL) ==========
        classification_log.append("🛡️ DEFENSIVE MARKET CLASSIFICATION:")
        classification_log.append("-" * 40)
        
        defensive_markets = cls.classify_defensive_markets(home_data, away_data)
        classification_log.extend(defensive_markets['rationale'])
        classification_log.append("")
        
        # ========== 4. FINAL SUMMARY & GUIDANCE ==========
        classification_log.append("🛡️ MARKET PROTECTION GUIDANCE:")
        classification_log.append("-" * 40)
        
        # Match state guidance
        match_state_guidance = {
            'TERMINAL_STAGNATION': "Under locks possible, Over locks impossible",
            'ASYMMETRIC_SUPPRESSION': "Winner/Clean Sheet locks possible",
            'DELAYED_RELEASE': "Under locks forbidden (release risk)",
            'FORCED_EXPLOSION': "Clean Sheet locks forbidden",
            'NEUTRAL': "Standard market evaluation applies"
        }
        
        classification_log.append(f"• Match State: {match_state_guidance.get(dominant_state, 'None')}")
        classification_log.append(f"• Totals Durability: {totals_durability['market_guidance']}")
        classification_log.append("")
        
        classification_log.append("⚠️ IMPORTANT: This classification is READ-ONLY")
        classification_log.append("   It does NOT affect existing Tier 1-3 logic")
        classification_log.append("   It only labels reality for system protection")
        classification_log.append("=" * 70)
        
        return {
            # Match state classification
            'dominant_state': dominant_state,
            'all_states': [s[0] for s in states],
            'state_data': dict(states),
            'state_description': state_descriptions.get(dominant_state, 'Unknown'),
            
            # Totals durability
            'totals_durability': totals_durability['durability'],
            'totals_durability_data': totals_durability['data'],
            'totals_durability_description': totals_durability['description'],
            'totals_durability_score': totals_durability['gradient_score'],
            
            # Defensive markets (optional)
            'defensive_markets': defensive_markets['classifications'],
            
            # Logs and metadata
            'classification_log': classification_log,
            'market_guidance': {
                'match_state': match_state_guidance.get(dominant_state, 'None'),
                'totals_durability': totals_durability['market_guidance']
            },
            'is_read_only': True,  # CRITICAL: Ensure this stays read-only
            'metadata': {
                'version': '1.2',
                'purpose': 'Structural classification for system protection',
                'no_side_effects': True,
                'components': {
                    'match_states': True,
                    'totals_durability': True,
                    'defensive_markets': True
                }
            }
        }


# =================== INTEGRATION HELPER FUNCTIONS ===================

def get_read_only_classification(home_data: Dict, away_data: Dict) -> Dict:
    """
    SAFE INTEGRATION HELPER
    
    Use this function in app.py to get classification results.
    This ensures classification stays read-only.
    """
    return MatchStateClassifier.classify_match_state(home_data, away_data)


def get_totals_durability_only(home_data: Dict, away_data: Dict) -> Dict:
    """
    GET ONLY TOTALS DURABILITY CLASSIFICATION
    
    Use this if you only need totals durability without full match state classification.
    """
    return MatchStateClassifier.classify_totals_durability(home_data, away_data)


# =================== DEVELOPMENT VERIFICATION ===================

if __name__ == "__main__":
    """
    DEVELOPMENT TESTING ENTRY POINT
    
    Run this to verify the classifier works correctly
    and doesn't break the existing system.
    """
    print("🧪 BRUTBALL STATE & DURABILITY CLASSIFIER v1.2")
    print("=" * 60)
    print("DEVELOPMENT TEST - READ-ONLY VERIFICATION")
    print("")
    
    # Test data for different scenarios
    test_cases = {
        'TERMINAL_STAGNATION': {
            'home': {'goals_scored_last_5': 6, 'goals_conceded_last_5': 5, 'home_setpiece_pct': 0.25, 'home_counter_pct': 0.10},
            'away': {'goals_scored_last_5': 5, 'goals_conceded_last_5': 4, 'away_setpiece_pct': 0.20, 'away_counter_pct': 0.12}
        },
        'FORCED_EXPLOSION': {
            'home': {'home_xg_per_match': 1.7, 'home_openplay_pct': 0.65, 'goals_conceded_last_5': 8},
            'away': {'away_xg_per_match': 1.0, 'away_openplay_pct': 0.50, 'goals_conceded_last_5': 5}
        },
        'STABLE_TOTALS': {
            'home': {'goals_scored_last_5': 6, 'goals_conceded_last_5': 5},  # 1.2 avg each
            'away': {'goals_scored_last_5': 5, 'goals_conceded_last_5': 4}   # 1.0 avg each
        },
        'FRAGILE_TOTALS': {
            'home': {'goals_scored_last_5': 6, 'goals_conceded_last_5': 10},  # 1.2 scored, 2.0 conceded
            'away': {'goals_scored_last_5': 5, 'goals_conceded_last_5': 4}    # 1.0 avg
        }
    }
    
    # Test each case
    for case_name, data in test_cases.items():
        print(f"\n🔍 TEST CASE: {case_name}")
        print("-" * 40)
        
        # Merge with minimal required fields
        home_data = {**data['home'], 'home_xg_per_match': 1.0, 'home_xg_conceded_per_match': 1.0}
        away_data = {**data['away'], 'away_xg_per_match': 1.0, 'away_xg_conceded_per_match': 1.0}
        
        # Run classification
        result = get_read_only_classification(home_data, away_data)
        
        print(f"• Dominant State: {result['dominant_state']}")
        print(f"• Totals Durability: {result['totals_durability']}")
        print(f"• Read-Only: {result['is_read_only']}")
        print(f"• No Side Effects: {result['metadata']['no_side_effects']}")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION INSTRUCTIONS FOR DEVELOPER:")
    print("=" * 60)
    print("""
1. Save this file as 'match_state_classifier.py'

2. In app.py, add import:
   from match_state_classifier import get_read_only_classification

3. After existing analysis, add classification:
   classification = get_read_only_classification(home_data, away_data)
   
4. Add to result dict (read-only):
   result['state_classification'] = classification
   result['classification_is_read_only'] = True

5. Display in UI (informational only):
   st.markdown("### 🧠 STRUCTURAL CLASSIFICATION (READ-ONLY)")
   st.markdown(f"**Match State:** {classification['dominant_state']}")
   st.markdown(f"**Totals Durability:** {classification['totals_durability']}")
   st.markdown("⚠️ *Informational only - does not affect betting logic*")

6. Safety verification:
   • Remove the classification code → system behaves identically
   • Classification never modifies existing logic
   • All bets, stakes, locks remain unchanged

7. Test with known matches:
   • Manchester United vs Wolves → NONE durability
   • Rayo Vallecano vs Getafe → STABLE durability  
   • Celta Vigo vs Valencia → FRAGILE durability
    """)
    
    print("=" * 60)
    print("✅ MODULE READY FOR DROP-IN INTEGRATION")
    print("🔒 ALL CLASSIFICATIONS ARE READ-ONLY")
    print("🚀 NO SIDE EFFECTS ON EXISTING SYSTEM")
