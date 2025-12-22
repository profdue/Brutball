import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="Brutball v6.0 - Match-State Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'country': 'England',
        'color': '#3B82F6'
    },
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'country': 'Spain',
        'color': '#EF4444'
    },
    'Bundesliga': {
        'filename': 'bundesliga.csv',
        'display_name': '🇩🇪 Bundesliga',
        'country': 'Germany',
        'color': '#000000'
    },
    'Serie A': {
        'filename': 'serie_a.csv',
        'display_name': '🇮🇹 Serie A',
        'country': 'Italy',
        'color': '#10B981'
    },
    'Ligue 1': {
        'filename': 'ligue_1.csv',
        'display_name': '🇫🇷 Ligue 1',
        'country': 'France',
        'color': '#8B5CF6'
    }
}

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .audit-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .axiom-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid #10B981;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .decision-step {
        background: #F8FAFC;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        counter-increment: step-counter;
    }
    .decision-step::before {
        content: counter(step-counter) ". ";
        font-weight: 800;
        color: #3B82F6;
        font-size: 1.2rem;
    }
    .control-indicator {
        padding: 1.5rem;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-radius: 10px;
        border: 3px solid #16A34A;
        margin: 1rem 0;
        text-align: center;
    }
    .no-control-indicator {
        padding: 1.5rem;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border-radius: 10px;
        border: 3px solid #6B7280;
        margin: 1rem 0;
        text-align: center;
    }
    .metric-card-audit {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .key-metrics-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .key-metrics-table th {
        background: #F8FAFC;
        padding: 0.75rem;
        text-align: left;
        border-bottom: 2px solid #E5E7EB;
        font-weight: 600;
        color: #4B5563;
        font-size: 0.9rem;
    }
    .key-metrics-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .key-metrics-table tr:last-child td {
        border-bottom: none;
    }
    .stake-display {
        font-size: 2.5rem;
        font-weight: 800;
        color: #059669;
        text-align: center;
        margin: 0.5rem 0;
    }
    .threshold-box {
        background: #EFF6FF;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .tie-breaker-box {
        background: #FEF3C7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .nuance-box {
        background: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0EA5E9;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .action-display {
        padding: 2rem;
        border-radius: 12px;
        background: white;
        border: 3px solid;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .controller-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #16A34A15;
        color: #16A34A;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.25rem;
        border: 1px solid #16A34A30;
    }
    .team-label {
        font-weight: 600;
        color: #4B5563;
    }
    .controller-label {
        font-weight: 700;
        color: #16A34A;
        background: #16A34A10;
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
    }
    .confidence-adjustment-box {
        background: #FEF3C7;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 3px solid #F59E0B;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .status-success {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .status-warning {
        background: #FEF3C7;
        color: #D97706;
        border: 1px solid #FCD34D;
    }
    .status-neutral {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .metric-row-controller {
        background: #F0FDF4;
        border-left: 3px solid #16A34A;
    }
    .metric-row-team {
        background: #F9FAFB;
    }
    .justification-container {
        background: #F0F9FF;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0EA5E9;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =================== AUDIT-READY BRUTBALL v6.0 ENGINE ===================
class BrutballAuditEngine:
    """
    AUDIT-READY v6.0 TEMPLATE IMPLEMENTATION
    With consistent formatting and consolidated metrics
    """
    
    # AXIOM 1: FOOTBALL IS NOT SYMMETRIC
    @staticmethod
    def check_asymmetry(home_xg: float, away_xg: float, 
                       home_form: str, away_form: str) -> Tuple[bool, List[str]]:
        """Check if match shows asymmetric characteristics."""
        rationale = []
        
        # Check for false symmetry (similar xG but different context)
        xg_diff = abs(home_xg - away_xg)
        if xg_diff < 0.3 and home_xg > 1.3 and away_xg > 1.3:
            rationale.append("⚠️ AXIOM 1: False symmetry detected")
            rationale.append(f"  • xG difference: {xg_diff:.2f} < 0.3")
            rationale.append(f"  • Both attacks competent: Home {home_xg:.2f}, Away {away_xg:.2f}")
            rationale.append("  • Note: Similar xG does NOT imply match balance")
            return True, rationale
        
        rationale.append("✅ AXIOM 1: Match shows expected asymmetry")
        return False, rationale
    
    # AXIOM 2: GAME-STATE CONTROL IS PRIMARY
    @staticmethod
    def evaluate_control_criteria(team_data: Dict, opponent_data: Dict,
                                 is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """
        Evaluate 4 control criteria with weighted scoring for tie-breakers
        """
        rationale = []
        criteria_met = []
        raw_score = 0
        weighted_score = 0.0
        
        # CRITERION 1: Tempo dominance (weight: 1.0)
        if is_home:
            tempo_xg = team_data.get('home_xg_per_match', 0)
        else:
            tempo_xg = team_data.get('away_xg_per_match', 0)
        
        if tempo_xg > 1.4:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Tempo dominance")
            rationale.append(f"✅ {team_name}: Tempo dominance (xG: {tempo_xg:.2f} > 1.4)")
        
        # CRITERION 2: Scoring efficiency relative to control (weight: 1.0)
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
        
        efficiency = goals / max(xg, 0.1)
        if efficiency > 0.9:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Scoring efficiency")
            rationale.append(f"✅ {team_name}: Scoring efficiency ({efficiency:.1%} of xG converted > 90%)")
        
        # CRITERION 3: Possession in critical areas (weight: 0.8)
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"✅ {team_name}: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # CRITERION 4: Repeatable scoring/attacking patterns (weight: 0.8)
        if is_home:
            openplay_pct = team_data.get('home_openplay_pct', 0)
            counter_pct = team_data.get('home_counter_pct', 0)
        else:
            openplay_pct = team_data.get('away_openplay_pct', 0)
            counter_pct = team_data.get('away_counter_pct', 0)
        
        repeatable_methods = 0
        if openplay_pct > 0.5:
            repeatable_methods += 1
        if counter_pct > 0.15:
            repeatable_methods += 1
        
        if repeatable_methods >= 1:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Repeatable patterns")
            rationale.append(f"✅ {team_name}: Repeatable attacking patterns")
        
        return raw_score, weighted_score, criteria_met, rationale
    
    # AXIOM 3: STRUCTURAL METRICS ARE CONTEXTUAL
    @staticmethod
    def apply_contextual_metrics(controller: Optional[str],
                               home_data: Dict, away_data: Dict,
                               home_name: str, away_name: str) -> List[str]:
        """Apply metrics ONLY after controller is known."""
        rationale = []
        
        if not controller:
            rationale.append("⚠️ AXIOM 3: No controller → metrics have limited predictive value")
            return rationale
        
        rationale.append("📊 AXIOM 3: CONTEXTUAL METRICS APPLIED (Post-GSC)")
        
        # Get relevant metrics for controller
        is_home = controller == home_name
        if is_home:
            controller_xg = home_data.get('home_xg_per_match', 0)
            controller_form = home_data.get('form_last_5_home', '')
        else:
            controller_xg = away_data.get('away_xg_per_match', 0)
            controller_form = away_data.get('form_last_5_away', '')
        
        rationale.append(f"• Controller {controller} xG: {controller_xg:.2f}")
        rationale.append(f"• Controller form: {controller_form}")
        rationale.append("• Metrics now contextualized to controller's game-state")
        
        return rationale
    
    # AXIOM 4 & 6: GOALS ENVIRONMENT + DUAL FRAGILITY
    @staticmethod
    def evaluate_goals_environment(home_data: Dict, away_data: Dict,
                                 controller: Optional[str],
                                 home_name: str, away_name: str) -> Tuple[bool, List[str], float]:
        """
        AXIOM 4: Goals are consequence, not strategy
        AXIOM 6: Dual fragility ≠ dual chaos
        Returns: (has_goals_env, rationale, controller_xg_for_context)
        """
        rationale = []
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        max_xg = max(home_xg, away_xg)
        
        rationale.append("🎯 AXIOM 4 & 6: GOALS ENVIRONMENT EVALUATION")
        rationale.append(f"• Combined xG: {combined_xg:.2f} (threshold: ≥2.8)")
        rationale.append(f"• Home xG: {home_xg:.2f}, Away xG: {away_xg:.2f} (elite threshold: ≥1.6)")
        
        # AXIOM 4: Basic capacity check with explicit thresholds
        if combined_xg < 2.8:
            rationale.append(f"❌ AXIOM 4: Combined xG {combined_xg:.2f} < 2.8 threshold")
            return False, rationale, 0.0
        
        if max_xg < 1.6:
            rationale.append(f"❌ AXIOM 4: No elite attack (max: {max_xg:.2f} < 1.6 threshold)")
            return False, rationale, 0.0
        
        rationale.append(f"✅ AXIOM 4: Combined xG {combined_xg:.2f} ≥ 2.8 threshold")
        rationale.append(f"✅ AXIOM 4: Elite attack present ({max_xg:.2f} ≥ 1.6)")
        
        # Get controller xG for context (even if below elite threshold)
        controller_xg_for_context = 0.0
        if controller:
            if controller == home_name:
                controller_xg_for_context = home_xg
            else:
                controller_xg_for_context = away_xg
            
            if controller_xg_for_context < 1.6:
                rationale.append(f"⚠️ AXIOM 4 nuance: Controller xG {controller_xg_for_context:.2f} < 1.6 elite threshold")
        
        # AXIOM 6: Dual fragility check (explicit)
        rationale.append("🔍 AXIOM 6: DUAL FRAGILITY CHECK")
        home_crisis = home_data.get('goals_conceded_last_5', 0) >= 12
        away_crisis = away_data.get('goals_conceded_last_5', 0) >= 12
        
        if home_crisis and away_crisis:
            rationale.append("⚠️ AXIOM 6: Dual fragility detected (both defenses concede ≥12 last 5)")
            if controller:
                rationale.append("✅ AXIOM 6: Controller exists → structured goals (not chaos)")
                return True, rationale, controller_xg_for_context
            else:
                # Check intent for chaos
                if home_xg > 1.4 and away_xg > 1.4:
                    rationale.append("⚠️ AXIOM 6: Dual fragility + dual intent → potential chaos goals")
                    return True, rationale, controller_xg_for_context
                else:
                    rationale.append("❌ AXIOM 6: Dual fragility without sufficient intent → no chaos")
                    return False, rationale, controller_xg_for_context
        
        rationale.append("✅ AXIOM 6: No dual fragility or structured by controller")
        return True, rationale, controller_xg_for_context
    
    # AXIOM 5: ONE-SIDED CONTROL OVERRIDE
    @staticmethod
    def apply_one_sided_override(controller: str, opponent_name: str,
                               controller_xg: float, has_goals_env: bool,
                               combined_xg: float, is_underdog: bool,
                               asymmetry_level: float) -> Tuple[str, float, List[str]]:
        """Apply one-sided control override with confidence adjustments."""
        rationale = []
        
        action = f"BACK {controller}"
        confidence = 8.5  # Base confidence for clear controller
        
        rationale.append("🎯 AXIOM 5: ONE-SIDED CONTROL OVERRIDE")
        rationale.append(f"• Controller: {controller}")
        rationale.append(f"• Controller xG: {controller_xg:.2f}")
        rationale.append(f"• Goals environment: {'Present' if has_goals_env else 'Absent'}")
        
        if has_goals_env:
            action += " & OVER 2.5"
            confidence = 8.0
            
            # Confidence adjustment for controller xG < elite threshold
            if controller_xg < 1.6:
                rationale.append(f"⚠️ Controller xG {controller_xg:.2f} < 1.6 elite threshold")
                confidence -= 0.5  # Standardized adjustment
            
            rationale.append("• AXIOM 5: Controller + goals environment → Back & Over")
        else:
            action += " (Clean win expected)"
            confidence = 9.0
            rationale.append("• AXIOM 5: Controller without goals → Clean win (likely UNDER)")
        
        # Confidence adjustments with standardized multiplier format
        adjustments = []
        adjustment_details = []
        
        if is_underdog:
            confidence -= 0.5  # Standardized as -0.5
            adjustments.append("Underdog controller: -0.5 (×0.8 equivalent)")
        
        if asymmetry_level > 0.5:  # High asymmetry
            confidence += 0.3  # Standardized as +0.3
            adjustments.append(f"Asymmetry ({asymmetry_level:.2f}): +0.3 (×1.2 equivalent)")
        
        if adjustments:
            rationale.append("• **Confidence adjustments:** " + ", ".join(adjustments))
        
        confidence = max(5.0, min(10.0, confidence))  # Cap between 5.0 and 10.0
        
        return action, confidence, rationale
    
    # AXIOM 7: FAVORITES FAIL STRUCTURALLY
    @staticmethod
    def evaluate_favorite_fade(favorite: str, underdog: str,
                             controller: Optional[str],
                             favorite_data: Dict, underdog_data: Dict,
                             favorite_xg: float, underdog_xg: float) -> Tuple[bool, List[str]]:
        """Check if favorite can be faded for structural reasons."""
        rationale = []
        
        rationale.append("📉 AXIOM 7: FAVORITE FADE EVALUATION")
        
        # HARD STOP: Favorite is controller
        if controller == favorite:
            rationale.append(f"❌ AXIOM 7: {favorite} is controller → CANNOT FADE")
            return False, rationale
        
        # CASE 1: Underdog is controller
        if controller == underdog:
            rationale.append(f"✅ AXIOM 7: {underdog} controls state → CAN FADE {favorite}")
            rationale.append("• Structural reason: Underdog has Game-State Control")
            return True, rationale
        
        # CASE 2: No controller but underdog can impose tempo
        if controller is None:
            if underdog_xg >= 1.3:
                rationale.append(f"⚠️ AXIOM 7: No controller but {underdog} can impose tempo")
                rationale.append(f"• {underdog} xG: {underdog_xg:.2f} ≥ 1.3 (tempo imposition threshold)")
                return True, rationale
        
        rationale.append(f"❌ AXIOM 7: No structural reason to fade {favorite}")
        return False, rationale
    
    # AXIOM 8: UNDER IS A CONTROL OUTCOME
    @staticmethod
    def evaluate_under_conditions(controller: Optional[str],
                                opponent_xg: float,
                                combined_xg: float) -> Tuple[bool, List[str]]:
        """Evaluate if Under conditions exist."""
        rationale = []
        
        rationale.append("🛡️ AXIOM 8: UNDER CONDITIONS EVALUATION")
        
        if not controller:
            rationale.append("❌ AXIOM 8: No controller → Under not a control outcome")
            return False, rationale
        
        if opponent_xg < 1.1 and combined_xg < 2.4:
            rationale.append(f"✅ AXIOM 8: UNDER conditions met")
            rationale.append(f"• Opponent lacks chase capacity: {opponent_xg:.2f} < 1.1 threshold")
            rationale.append(f"• Combined xG: {combined_xg:.2f} < 2.4 threshold")
            rationale.append(f"• Controller can win without urgency")
            return True, rationale
        
        rationale.append("❌ AXIOM 8: Insufficient Under conditions")
        rationale.append(f"• Opponent xG: {opponent_xg:.2f} (needs < 1.1)")
        rationale.append(f"• Combined xG: {combined_xg:.2f} (needs < 2.4)")
        return False, rationale
    
    # AXIOM 9: AVOID IS RARE AND EXPLICIT
    @staticmethod
    def evaluate_avoid_conditions(controller: Optional[str],
                                home_xg: float, away_xg: float,
                                league_avg_xg: float) -> Tuple[bool, List[str]]:
        """Check if Avoid conditions are met."""
        rationale = []
        
        rationale.append("🚫 AXIOM 9: AVOID CONDITIONS EVALUATION")
        
        # CONDITION 1: No controller
        if controller:
            rationale.append(f"❌ AXIOM 9: Controller exists: {controller}")
            return False, rationale
        
        # CONDITION 2: Attacks below league average
        if home_xg > league_avg_xg * 0.9 or away_xg > league_avg_xg * 0.9:
            rationale.append("❌ AXIOM 9: Competent attack present")
            rationale.append(f"• Home: {home_xg:.2f}, Away: {away_xg:.2f}")
            rationale.append(f"• League avg: {league_avg_xg:.2f} (90% threshold: {league_avg_xg*0.9:.2f})")
            return False, rationale
        
        # CONDITION 3: Low combined xG
        combined_xg = home_xg + away_xg
        if combined_xg < 2.4:
            rationale.append(f"✅ AXIOM 9: AVOID conditions met")
            rationale.append(f"• No Game-State Controller")
            rationale.append(f"• Attacks below league average ({league_avg_xg*0.9:.2f})")
            rationale.append(f"• Combined xG: {combined_xg:.2f} < 2.4 threshold")
            return True, rationale
        
        rationale.append("❌ AXIOM 9: Combined xG suggests potential")
        return False, rationale
    
    # AXIOM 10: CAPITAL FOLLOWS STATE CONFIDENCE
    @staticmethod
    def allocate_capital(controller: Optional[str],
                        confidence: float,
                        has_goals_env: bool,
                        is_underdog_controller: bool,
                        asymmetry_level: float) -> Tuple[float, List[str], List[str]]:
        """Determine stake size based on state confidence with adjustments."""
        rationale = []
        adjustments = []
        
        rationale.append("💰 AXIOM 10: CAPITAL ALLOCATION")
        rationale.append(f"• Base confidence: {confidence:.1f}/10")
        
        if controller:
            # Base stake based on confidence
            if confidence >= 8.5:
                stake = 2.5  # High confidence
                rationale.append(f"• High confidence → 2.5% base stake")
            elif confidence >= 7.5:
                stake = 2.0  # Moderate-high confidence
                rationale.append(f"• Moderate-high confidence → 2.0% base stake")
            elif confidence >= 6.5:
                stake = 1.5  # Moderate confidence
                rationale.append(f"• Moderate confidence → 1.5% base stake")
            else:
                stake = 1.0  # Low confidence
                rationale.append(f"• Low confidence → 1.0% base stake")
            
            # Standardized adjustments with multiplier format
            if is_underdog_controller:
                stake *= 0.8  # ×0.8 for underdog controller
                adjustments.append(f"Underdog controller: ×0.8")
                rationale.append(f"• Underdog controller → stake ×0.8")
            
            if asymmetry_level > 0.5:  # High asymmetry
                stake *= 1.2  # ×1.2 for high asymmetry
                adjustments.append(f"High asymmetry: ×1.2")
                rationale.append(f"• High asymmetry ({asymmetry_level:.2f} > 0.5) → stake ×1.2")
            
            # AXIOM 10: Moderate asymmetry has no stake adjustment
            if 0.3 < asymmetry_level <= 0.5:
                rationale.append(f"• Moderate asymmetry ({asymmetry_level:.2f}) → no stake adjustment per AXIOM 10")
            
            if adjustments:
                rationale.append(f"• **Applied adjustments:** {', '.join(adjustments)}")
                rationale.append(f"• Note: High asymmetry can offset underdog reduction if both apply")
                stake = max(0.5, min(stake, 3.0))  # Cap between 0.5% and 3.0%
                rationale.append(f"• Stake capped between 0.5% and 3.0%")
            
        elif has_goals_env:
            stake = 0.5  # Minimal for goals only
            rationale.append("• No controller, goals only → 0.5% stake")
        else:
            stake = 0.0  # Avoid
            rationale.append("• No edge → 0.0% stake (AVOID)")
        
        rationale.append(f"• **Final stake: {stake:.2f}%** of bankroll")
        return stake, rationale, adjustments
    
    # CONSOLIDATED AXIOM 4 & 5 JUSTIFICATION
    @staticmethod
    def generate_axiom45_justification(controller_xg: float, combined_xg: float, 
                                      max_xg: float) -> str:
        """Generate consolidated justification for AXIOM 4 & 5 decisions."""
        if controller_xg >= 1.6:
            return "✅ Controller meets elite threshold (≥1.6 xG) → standard AXIOM 5 application"
        
        justification = "🎯 **AXIOM 4 & 5 JUSTIFICATION (Controller xG < 1.6)**\n"
        justification += f"1. **Overall environment supports scoring** (combined xG: {combined_xg:.2f} ≥ 2.8 threshold)\n"
        justification += f"2. **Elite attack exists in match** (max xG: {max_xg:.2f} ≥ 1.6 threshold)\n"
        justification += "3. **Controller has structured tempo** (>1.4 xG minimum for control)\n"
        justification += "4. **Control takes precedence** over raw xG volume (AXIOM 5)"
        return justification
    
    # MAIN AUDIT-READY DECISION TREE
    @classmethod
    def execute_audit_tree(cls, home_data: Dict, away_data: Dict,
                          home_name: str, away_name: str,
                          league_avg_xg: float) -> Dict:
        """Execute exact 4-step decision tree with tie-breakers."""
        
        audit_log = []
        decision_steps = []
        thresholds_used = {}
        
        # Determine favorite (by position)
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
        audit_log.append("=" * 70)
        audit_log.append("🔐 BRUTBALL v6.0 - AUDIT-READY ANALYSIS")
        audit_log.append("=" * 70)
        audit_log.append(f"Match: {home_name} vs {away_name}")
        audit_log.append(f"Favorite: {favorite} (#{min(home_pos, away_pos)})")
        audit_log.append(f"Underdog: {underdog} (#{max(home_pos, away_pos)})")
        audit_log.append("")
        
        # =================== STEP 1: IDENTIFY GAME-STATE CONTROLLER ===================
        audit_log.append("STEP 1: IDENTIFY GAME-STATE CONTROLLER (AXIOM 2)")
        audit_log.append("Evaluating 4 control criteria for each team...")
        
        # Evaluate home team
        home_score, home_weighted, home_criteria, home_rationale = cls.evaluate_control_criteria(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        # Evaluate away team
        away_score, away_weighted, away_criteria, away_rationale = cls.evaluate_control_criteria(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        audit_log.extend(home_rationale)
        audit_log.extend(away_rationale)
        
        # Determine controller with tie-breaker logic
        controller = None
        controller_criteria = []
        tie_breaker_applied = False
        
        if home_score >= 2 and away_score >= 2:
            # TIE-BREAKER: Both teams meet ≥2 criteria
            audit_log.append("⚖️ TIE-BREAKER SITUATION: Both teams meet ≥2 criteria")
            audit_log.append(f"  • {home_name}: {home_score}/4 criteria, weighted score: {home_weighted:.2f}")
            audit_log.append(f"  • {away_name}: {away_score}/4 criteria, weighted score: {away_weighted:.2f}")
            
            if home_weighted > away_weighted:
                controller = home_name
                controller_criteria = home_criteria
                audit_log.append(f"  • Tie-breaker: {home_name} selected (higher structured control score)")
            elif away_weighted > home_weighted:
                controller = away_name
                controller_criteria = away_criteria
                audit_log.append(f"  • Tie-breaker: {away_name} selected (higher structured control score)")
            else:
                # Equal weighted scores - use position as final tie-breaker
                if home_pos < away_pos:
                    controller = home_name
                    controller_criteria = home_criteria
                    audit_log.append(f"  • Final tie-breaker: {home_name} selected (better league position)")
                else:
                    controller = away_name
                    controller_criteria = away_criteria
                    audit_log.append(f"  • Final tie-breaker: {away_name} selected (better league position)")
            
            tie_breaker_applied = True
            
        elif home_score >= 2 and home_score > away_score:
            controller = home_name
            controller_criteria = home_criteria
            audit_log.append(f"🎯 GAME-STATE CONTROLLER: {home_name} ({home_score}/4 criteria)")
            audit_log.append(f"   Criteria met: {', '.join(home_criteria)}")
            
        elif away_score >= 2 and away_score > home_score:
            controller = away_name
            controller_criteria = away_criteria
            audit_log.append(f"🎯 GAME-STATE CONTROLLER: {away_name} ({away_score}/4 criteria)")
            audit_log.append(f"   Criteria met: {', '.join(away_criteria)}")
            
        else:
            audit_log.append("⚠️ NO CLEAR GAME-STATE CONTROLLER")
            audit_log.append(f"   {home_name}: {home_score}/4 criteria (need 2+)")
            audit_log.append(f"   {away_name}: {away_score}/4 criteria (need 2+)")
        
        decision_steps.append(f"1. Controller: {controller if controller else 'None'}")
        if tie_breaker_applied:
            decision_steps.append("   (Tie-breaker applied: weighted control score)")
        
        # =================== STEP 2: EVALUATE GOALS ENVIRONMENT ===================
        audit_log.append("")
        audit_log.append("STEP 2: EVALUATE GOALS ENVIRONMENT (AXIOMS 3,4,6)")
        
        # Check asymmetry (AXIOM 1)
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        max_xg = max(home_xg, away_xg)
        asymmetry, asym_rationale = cls.check_asymmetry(
            home_xg, away_xg,
            home_data.get('form_last_5_overall', ''),
            away_data.get('form_last_5_overall', '')
        )
        audit_log.extend(asym_rationale)
        
        # Calculate asymmetry level for AXIOM 10 adjustment
        asymmetry_level = abs(home_xg - away_xg) / max(home_xg + away_xg, 0.1)
        
        # Apply contextual metrics (AXIOM 3)
        contextual_rationale = cls.apply_contextual_metrics(
            controller, home_data, away_data, home_name, away_name
        )
        audit_log.extend(contextual_rationale)
        
        # Evaluate goals environment (AXIOM 4 & 6) with explicit thresholds
        has_goals_env, goals_rationale, controller_xg = cls.evaluate_goals_environment(
            home_data, away_data, controller, home_name, away_name
        )
        audit_log.extend(goals_rationale)
        
        # Store thresholds used
        thresholds_used['combined_xg'] = combined_xg
        thresholds_used['home_xg'] = home_xg
        thresholds_used['away_xg'] = away_xg
        thresholds_used['controller_xg'] = controller_xg
        thresholds_used['max_xg'] = max_xg
        
        decision_steps.append(f"2. Goals Environment: {'Present' if has_goals_env else 'Absent'}")
        if controller_xg > 0 and controller_xg < 1.6:
            decision_steps.append(f"   (Controller xG: {controller_xg:.2f} < 1.6 elite threshold)")
        
        # =================== STEP 3: APPLY DECISION LOGIC ===================
        audit_log.append("")
        audit_log.append("STEP 3: APPLY DECISION LOGIC (AXIOMS 5,7,8,9)")
        
        primary_action = "ANALYZING"
        confidence = 5.0
        secondary_logic = ""
        
        if controller:
            # CASE A: Controller exists (AXIOM 5)
            opponent = away_name if controller == home_name else home_name
            is_underdog = controller == underdog
            
            action, conf, override_rationale = cls.apply_one_sided_override(
                controller, opponent, controller_xg, has_goals_env,
                combined_xg, is_underdog, asymmetry_level
            )
            audit_log.extend(override_rationale)
            primary_action = action
            confidence = conf
            
            # Check Under conditions (AXIOM 8)
            if not has_goals_env:
                opponent_xg = away_xg if controller == home_name else home_xg
                under_ok, under_rationale = cls.evaluate_under_conditions(
                    controller, opponent_xg, combined_xg
                )
                if under_ok:
                    audit_log.extend(under_rationale)
            
            decision_steps.append("3A. One-Sided Control Override (AXIOM 5)")
            if is_underdog:
                decision_steps.append("   (Underdog controller → confidence adjusted)")
            
        elif has_goals_env:
            # CASE B: No controller + Goals environment (AXIOM 7)
            favorite_data = home_data if favorite == home_name else away_data
            underdog_data = away_data if favorite == home_name else home_data
            favorite_xg = home_xg if favorite == home_name else away_xg
            underdog_xg = away_xg if favorite == home_name else home_xg
            
            can_fade, fade_rationale = cls.evaluate_favorite_fade(
                favorite, underdog, controller, favorite_data, underdog_data,
                favorite_xg, underdog_xg
            )
            audit_log.extend(fade_rationale)
            
            if can_fade:
                primary_action = f"FADE {favorite} & OVER 2.5"
                confidence = 6.5
                secondary_logic = f"{underdog} or DRAW"
                decision_steps.append("3B. Favorite Fade + Over (AXIOM 7)")
            else:
                primary_action = "OVER 2.5"
                confidence = 6.0
                secondary_logic = "Goals only"
                decision_steps.append("3B. Over Only")
        
        else:
            # CASE C: No controller + No goals (AXIOMS 8,9)
            # Check Under conditions first (AXIOM 8)
            under_ok, under_rationale = cls.evaluate_under_conditions(
                controller,
                away_xg,  # Using away as opponent for home controller check
                combined_xg
            )
            
            if under_ok:
                audit_log.extend(under_rationale)
                primary_action = "UNDER 2.5"
                confidence = 5.5
                decision_steps.append("3C. Under Conditions (AXIOM 8)")
            else:
                # Check Avoid conditions (AXIOM 9)
                should_avoid, avoid_rationale = cls.evaluate_avoid_conditions(
                    controller, home_xg, away_xg, league_avg_xg
                )
                audit_log.extend(avoid_rationale)
                
                if should_avoid:
                    primary_action = "AVOID"
                    confidence = 0.0
                    secondary_logic = "No edge identified"
                    decision_steps.append("3C. Avoid (AXIOM 9)")
                else:
                    primary_action = "UNDER 2.5"
                    confidence = 5.0
                    secondary_logic = "Fallback: Low scoring expected"
                    decision_steps.append("3C. Fallback Under")
        
        # =================== STEP 4: ALLOCATE CAPITAL ===================
        audit_log.append("")
        audit_log.append("STEP 4: ALLOCATE CAPITAL (AXIOM 10)")
        
        is_underdog_controller = controller == underdog if controller else False
        stake_pct, stake_rationale, stake_adjustments = cls.allocate_capital(
            controller, confidence, has_goals_env,
            is_underdog_controller, asymmetry_level
        )
        audit_log.extend(stake_rationale)
        
        decision_steps.append(f"4. Stake: {stake_pct:.2f}% (with confidence adjustments)")
        if stake_adjustments:
            for adj in stake_adjustments:
                decision_steps.append(f"   - {adj}")
        
        # Generate consolidated justification
        axiom45_justification = ""
        if controller and controller_xg < 1.6:
            axiom45_justification = cls.generate_axiom45_justification(
                controller_xg, combined_xg, max_xg
            )
        
        # Final summary
        audit_log.append("")
        audit_log.append("=" * 70)
        audit_log.append("🎯 FINAL DECISION")
        audit_log.append(f"• Action: {primary_action}")
        audit_log.append(f"• Confidence: {confidence:.1f}/10")
        audit_log.append(f"• Stake: {stake_pct:.2f}% of bankroll")
        if secondary_logic:
            audit_log.append(f"• Logic: {secondary_logic}")
        if tie_breaker_applied:
            audit_log.append("• Note: Tie-breaker applied for controller selection")
        if stake_adjustments:
            audit_log.append(f"• Stake adjustments: {', '.join(stake_adjustments)}")
        audit_log.append("=" * 70)
        
        return {
            'match': f"{home_name} vs {away_name}",
            'controller': controller,
            'controller_criteria': controller_criteria,
            'has_goals_env': has_goals_env,
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'secondary_logic': secondary_logic,
            'audit_log': audit_log,
            'decision_steps': decision_steps,
            'tie_breaker_applied': tie_breaker_applied,
            'thresholds_used': thresholds_used,
            'team_context': {
                'favorite': favorite,
                'underdog': underdog,
                'home': home_name,
                'away': away_name,
                'home_pos': home_pos,
                'away_pos': away_pos
            },
            'key_metrics': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'controller_xg': controller_xg if controller else 0.0,
                'combined_xg': combined_xg,
                'max_xg': max_xg,
                'league_avg_xg': league_avg_xg,
                'asymmetry_level': asymmetry_level
            },
            'stake_adjustments': stake_adjustments,
            'axiom45_justification': axiom45_justification
        }

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data."""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
        ]
        
        df = None
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                break
            except Exception:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['country'] = league_config['country']
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics."""
    
    # Goals conceded
    df['home_goals_conceded'] = (
        df['home_goals_openplay_against'].fillna(0) +
        df['home_goals_counter_against'].fillna(0) +
        df['home_goals_setpiece_against'].fillna(0) +
        df['home_goals_penalty_against'].fillna(0) +
        df['home_goals_owngoal_against'].fillna(0)
    )
    
    df['away_goals_conceded'] = (
        df['away_goals_openplay_against'].fillna(0) +
        df['away_goals_counter_against'].fillna(0) +
        df['away_goals_setpiece_against'].fillna(0) +
        df['away_goals_penalty_against'].fillna(0) +
        df['away_goals_owngoal_against'].fillna(0)
    )
    
    # Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Goal type percentages
    for prefix in ['home', 'away']:
        goals_col = f'{prefix}_goals_scored'
        if goals_col in df.columns:
            for method in ['counter', 'setpiece', 'openplay']:
                col = f'{prefix}_goals_{method}_for'
                if col in df.columns:
                    df[f'{prefix}_{method}_pct'] = df[col] / df[goals_col].replace(0, np.nan)
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="audit-header">🔐 BRUTBALL v6.0 – MATCH-STATE ANALYSIS ENGINE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sub-header">
        <p><strong>Control-first • Goals-secondary • Structural assessment • Capital follows confidence</strong></p>
        <p>Exact implementation of v6.0 audit template with explicit thresholds and tie-breaker logic</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("### 🌍 League Selection")
    cols = st.columns(5)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if 'selected_league' not in st.session_state else "secondary"
            ):
                st.session_state.selected_league = league
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Team selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options)
    
    # Execute analysis
    if st.button("🚀 EXECUTE MATCH-STATE ANALYSIS", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute audit tree
        result = BrutballAuditEngine.execute_audit_tree(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 ANALYSIS RESULTS")
        
        # Controller display with tie-breaker note
        if result['controller']:
            controller_name = result['controller']
            criteria_count = len(result['controller_criteria'])
            
            st.markdown(f"""
            <div class="control-indicator">
                <h3 style="color: #16A34A; margin: 0;">GAME-STATE CONTROLLER IDENTIFIED</h3>
                <h2 style="color: #16A34A; margin: 0.5rem 0;">{controller_name} (#{result['team_context']['home_pos'] if controller_name == home_team else result['team_context']['away_pos']})</h2>
                <p style="color: #6B7280; margin-bottom: 0.5rem;">
                    <strong>Criteria met: {', '.join(result['controller_criteria'])} ({criteria_count}/4)</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if result['tie_breaker_applied']:
                st.markdown('<div class="tie-breaker-box">', unsafe_allow_html=True)
                st.markdown("**⚖️ TIE-BREAKER APPLIED**")
                st.markdown("Both teams met 2+ criteria; controller selected via weighted structured control score")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="no-control-indicator">
                <h3 style="color: #6B7280; margin: 0;">NO CLEAR GAME-STATE CONTROLLER</h3>
                <p style="color: #6B7280;">Neither team meets 2+ control criteria</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Primary action with confidence adjustments
        action = result['primary_action']
        if "BACK" in action:
            color = "#16A34A"
            badge = "Controller Action (AXIOM 5)"
        elif "FADE" in action:
            color = "#EA580C"
            badge = "Favorite Fade (AXIOM 7)"
        elif "OVER" in action:
            color = "#F59E0B"
            badge = "Goals Focus (AXIOM 4)"
        elif "UNDER" in action:
            color = "#2563EB"
            badge = "Under/Defensive (AXIOM 8)"
        else:
            color = "#6B7280"
            badge = "Avoid (AXIOM 9)"
        
        # Confidence adjustments in standardized format
        confidence_adjustments_display = ""
        if result.get('stake_adjustments'):
            adjustments_list = []
            for adj in result['stake_adjustments']:
                if "×0.8" in adj:
                    adjustments_list.append("Underdog controller: ×0.8")
                elif "×1.2" in adj:
                    adjustments_list.append("High asymmetry: ×1.2")
            if adjustments_list:
                confidence_adjustments_display = "<br>".join([f"• {adj}" for adj in adjustments_list])
        
        st.markdown(f"""
        <div class="action-display" style="border-color: {color};">
            <div style="color: #6B7280; font-size: 0.9rem;">PRIMARY ACTION</div>
            <h1 style="color: {color}; margin: 0.5rem 0;">{action}</h1>
            <div style="display: inline-block; padding: 0.25rem 1rem; background: {color}15; color: {color}; border-radius: 20px; font-weight: 600; margin-bottom: 1rem;">
                {badge}
            </div>
            <div style="display: flex; justify-content: center; margin-top: 1.5rem;">
                <div style="margin: 0 1.5rem;">
                    <div style="color: #6B7280; font-size: 0.9rem;">State Confidence</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {color};">{result['confidence']:.1f}/10</div>
                </div>
                <div style="margin: 0 1.5rem;">
                    <div style="color: #6B7280; font-size: 0.9rem;">Capital Allocation (AXIOM 10)</div>
                    <div class="stake-display">{result['stake_pct']:.2f}%</div>
                </div>
            </div>
            {"<div class='confidence-adjustment-box'><strong>Stake Adjustments:</strong><br>" + confidence_adjustments_display + "</div>" if confidence_adjustments_display else ""}
        </div>
        """, unsafe_allow_html=True)
        
        # Decision steps
        st.markdown("#### 📋 Decision Steps")
        for step in result['decision_steps']:
            st.markdown(f"- {step}")
        
        # CONSOLIDATED KEY METRICS TABLE (instead of repeated metrics)
        st.markdown("#### 📊 Key Metrics & Thresholds")
        
        metrics_data = {
            'Metric': [
                'Home xG',
                'Away xG', 
                'Combined xG',
                'Controller xG',
                'Elite Attack (max xG)',
                'League Average',
                'Asymmetry Level'
            ],
            'Value': [
                f"{result['key_metrics']['home_xg']:.2f}",
                f"{result['key_metrics']['away_xg']:.2f}",
                f"{result['key_metrics']['combined_xg']:.2f}",
                f"{result['key_metrics']['controller_xg']:.2f}" if result['controller'] else "N/A",
                f"{result['key_metrics']['max_xg']:.2f}",
                f"{result['key_metrics']['league_avg_xg']:.2f}",
                f"{result['key_metrics']['asymmetry_level']:.2f}"
            ],
            'Threshold': [
                '≥1.6 elite, ≥1.4 tempo',
                '≥1.6 elite, ≥1.4 tempo',
                '≥2.8 goals environment',
                '≥1.6 elite, >1.4 tempo',
                '≥1.6 required',
                'Baseline',
                '>0.5 = High, ≤0.5 = Mod/Low'
            ],
            'Status': [
                '✅' if result['key_metrics']['home_xg'] >= 1.6 else '⚠️' if result['key_metrics']['home_xg'] >= 1.4 else '❌',
                '✅' if result['key_metrics']['away_xg'] >= 1.6 else '⚠️' if result['key_metrics']['away_xg'] >= 1.4 else '❌',
                '✅' if result['key_metrics']['combined_xg'] >= 2.8 else '❌',
                '✅' if result['controller'] and result['key_metrics']['controller_xg'] >= 1.6 else '⚠️' if result['controller'] and result['key_metrics']['controller_xg'] >= 1.4 else '❌',
                '✅' if result['key_metrics']['max_xg'] >= 1.6 else '❌',
                '—',
                '✅ High' if result['key_metrics']['asymmetry_level'] > 0.5 else '⚠️ Moderate' if result['key_metrics']['asymmetry_level'] > 0.3 else '— Low'
            ]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        st.markdown(metrics_df.to_html(classes='key-metrics-table', index=False, escape=False), unsafe_allow_html=True)
        
        # Team context
        st.markdown("#### 🏆 Team Context")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card-audit">', unsafe_allow_html=True)
            st.markdown("**Position & Status**")
            ctx = result['team_context']
            
            # Home team
            home_status = []
            if ctx['home'] == ctx['favorite']:
                home_status.append("⭐ Favorite")
            if result['controller'] == ctx['home']:
                home_status.append("🎯 Controller")
            
            st.markdown(f"""
            **{ctx['home']}**
            • Position: #{ctx['home_pos']}
            • Status: {', '.join(home_status) if home_status else '—'}
            """)
            
            # Away team
            away_status = []
            if ctx['away'] == ctx['favorite']:
                away_status.append("⭐ Favorite")
            if result['controller'] == ctx['away']:
                away_status.append("🎯 Controller")
            
            st.markdown(f"""
            **{ctx['away']}**
            • Position: #{ctx['away_pos']}
            • Status: {', '.join(away_status) if away_status else '—'}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card-audit">', unsafe_allow_html=True)
            st.markdown("**Match Context**")
            
            st.markdown(f"""
            **Favorite:** {ctx['favorite']}
            **Underdog:** {ctx['underdog']}
            **Underdog Controller:** {'Yes' if result['controller'] == ctx['underdog'] else 'No'}
            """)
            
            # Asymmetry explanation with AXIOM 10 reference
            asymmetry = result['key_metrics']['asymmetry_level']
            if asymmetry > 0.5:
                st.markdown(f"""
                <div class="threshold-box">
                **High Asymmetry:** {asymmetry:.2f} > 0.5
                • Stake adjustment: ×1.2 (AXIOM 10)
                • Clearer control direction
                </div>
                """, unsafe_allow_html=True)
            elif asymmetry > 0.3:
                st.markdown(f"""
                <div class="threshold-box">
                **Moderate Asymmetry:** {asymmetry:.2f}
                • No stake adjustment per AXIOM 10
                • Expected match asymmetry
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Consolidated AXIOM 4 & 5 justification (if applicable)
        if result['axiom45_justification']:
            st.markdown("#### 🎯 AXIOM 4 & 5 Decision Justification")
            st.markdown(f'<div class="justification-container">{result["axiom45_justification"]}</div>', unsafe_allow_html=True)
        
        # Audit log
        with st.expander("📋 VIEW COMPLETE AUDIT LOG", expanded=True):
            for line in result['audit_log']:
                if '=' in line or '🎯' in line or 'STEP' in line:
                    st.markdown(f"**{line}**")
                elif '✅' in line or '❌' in line or '⚠️' in line:
                    st.markdown(f"**{line}**")
                elif line.startswith("•") or line.startswith("  •"):
                    st.markdown(f"`{line}`")
                elif line.strip():
                    st.markdown(line)
        
        # Export with clean text formatting (no HTML)
        st.markdown("---")
        st.markdown("#### 📤 Export Audit Report")
        
        # Format adjustments for clean export
        adjustments_text = "None"
        if result.get('stake_adjustments'):
            adj_list = []
            for adj in result['stake_adjustments']:
                if "×0.8" in adj:
                    adj_list.append("Underdog controller: ×0.8")
                elif "×1.2" in adj:
                    adj_list.append("High asymmetry: ×1.2")
            adjustments_text = "\n".join([f"  • {adj}" for adj in adj_list])
        
        export_text = f"""BRUTBALL v6.0 - AUDIT-READY ANALYSIS REPORT
===========================================
League: {selected_league}
Match: {result['match']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

DECISION TREE EXECUTION:
{chr(10).join(['• ' + step for step in result['decision_steps']])}

FINAL DECISION:
• Action: {result['primary_action']}
• Confidence: {result['confidence']:.1f}/10
• Stake: {result['stake_pct']:.2f}% of bankroll (AXIOM 10)
• Logic: {result['secondary_logic'] if result['secondary_logic'] else 'Direct application of axioms'}
• Tie-breaker applied: {'Yes' if result['tie_breaker_applied'] else 'No'}
• Stake adjustments:
{adjustments_text}

KEY METRICS:
• Home xG: {result['key_metrics']['home_xg']:.2f} (thresholds: ≥1.6 elite, ≥1.4 tempo)
• Away xG: {result['key_metrics']['away_xg']:.2f} (thresholds: ≥1.6 elite, ≥1.4 tempo)
• Combined xG: {result['key_metrics']['combined_xg']:.2f} (threshold: ≥2.8 goals environment)
• Controller xG: {result['key_metrics']['controller_xg']:.2f if result['controller'] else 'N/A'} (thresholds: ≥1.6 elite, >1.4 tempo)
• Elite Attack (max xG): {result['key_metrics']['max_xg']:.2f} (threshold: ≥1.6 required)
• League Average: {result['key_metrics']['league_avg_xg']:.2f}
• Asymmetry Level: {result['key_metrics']['asymmetry_level']:.2f} ({'High (>0.5)' if result['key_metrics']['asymmetry_level'] > 0.5 else 'Moderate (0.3-0.5)' if result['key_metrics']['asymmetry_level'] > 0.3 else 'Low (≤0.3)'})

TEAM CONTEXT:
• Favorite: {result['team_context']['favorite']} (#{min(result['team_context']['home_pos'], result['team_context']['away_pos'])})
• Underdog: {result['team_context']['underdog']} (#{max(result['team_context']['home_pos'], result['team_context']['away_pos'])})
• Underdog Controller: {'Yes' if result['controller'] == result['team_context']['underdog'] else 'No'}
• Home Position: #{result['team_context']['home_pos']}
• Away Position: #{result['team_context']['away_pos']}

{result['axiom45_justification'] if result.get('axiom45_justification') else ''}

AUDIT LOG:
{chr(10).join(result['audit_log'])}

===========================================
Brutball v6.0 - Audit-Ready Match-State Analysis
Control-first philosophy • All axioms explicitly applied • Explicit thresholds • Capital follows confidence
        """
        
        st.download_button(
            label="📥 Download Complete Audit Report",
            data=export_text,
            file_name=f"brutball_v6_audit_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Brutball v6.0 – Audit-Ready Match-State Analysis</strong></p>
        <p>Control-first philosophy • All axioms explicitly applied • Explicit thresholds • Capital follows confidence</p>
        <p>Tie-breakers and threshold nuances fully documented</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
