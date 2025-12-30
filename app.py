import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== SYSTEM CONSTANTS (IMMUTABLE) ===================
# v6.0 Edge Detection Engine Constants
CONTROL_CRITERIA_REQUIRED = 2  # Minimum for edge detection
GOALS_ENV_THRESHOLD = 2.8      # Combined xG for goals environment
ELITE_ATTACK_THRESHOLD = 1.6   # Max xG for elite attack

# v6.1.1 State Lock Authority Engine Constants
DIRECTION_THRESHOLD = 0.25     # LAW 2: Minimum directional dominance
ENFORCEMENT_METHODS_REQUIRED = 2  # LAW 3: Redundant enforcement
STATE_FLIP_FAILURES_REQUIRED = 2  # Opponent fails ≥2 escalation checks
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1  # v6.1.2 mutual control

# Totals Lock Constants (NEW) - STRICT BINARY GATE
TOTALS_LOCK_THRESHOLD = 1.2    # Last 5 matches avg goals ≤ 1.2 for both teams
UNDER_GOALS_THRESHOLD = 2.5    # Lock for Under 2.5 goals

# Market-Specific Thresholds for Agency-State Framework
MARKET_THRESHOLDS = {
    'WINNER': {
        'opponent_xg_max': 1.1,      # Standard chase threshold
        'state_flip_failures': 2,    # ≥2/4 failures
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can win without urgency
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,      # Stricter - opponent can't score
        'state_flip_failures': 3,    # ≥3/4 failures (more stringent)
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can defend without pushing
    },
    'TEAM_NO_SCORE': {  # Team to Score: NO
        'opponent_xg_max': 0.6,      # Very strict - almost no threat
        'state_flip_failures': 4,    # ALL 4 failures required
        'enforcement_methods': 3,    # ≥3 methods (elite defense needed)
        'urgency_required': False    # Can suppress without risk
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,      # Limited scoring capacity
        'state_flip_failures': 2,    # ≥2/4 failures
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can control without opening
    },
    'TOTALS_UNDER_2_5': {  # NEW: Totals Lock - STRICT BINARY
        'home_goals_threshold': TOTALS_LOCK_THRESHOLD,  # ≤ 1.2 avg goals LAST 5
        'away_goals_threshold': TOTALS_LOCK_THRESHOLD,  # ≤ 1.2 avg goals LAST 5
        'both_teams_required': True,  # BOTH must meet threshold
        'trend_based': True,          # Trend-based, not agency-suppression
        'capital_multiplier': 2.0,    # Same as LOCK_MODE
        'strict_binary': True         # NO multipliers, NO smoothing
    }
}

# Capital Multipliers
CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,     # v6.0 only
    'LOCK_MODE': 2.0,     # v6.0 + Agency-State LOCKED
    'ABSOLUTE_MODE': 3.0  # For future Absolute Lock
}

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1.2 + TOTALS LOCK (FIXED)",
    page_icon="⚖️🔒✅",
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
    },
    'Eredivisie': {
        'filename': 'eredivisie.csv',
        'display_name': '🇳🇱 Eredivisie',
        'country': 'Netherlands',
        'color': '#F59E0B'
    },
    'Primeira Liga': {
        'filename': 'premeira_portugal.csv',
        'display_name': '🇵🇹 Primeira Liga',
        'country': 'Portugal',
        'color': '#DC2626'
    },
    'Super Lig': {
        'filename': 'super_league.csv',
        'display_name': '🇹🇷 Super Lig',
        'country': 'Turkey',
        'color': '#E11D48'
    }
}

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .system-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 1rem;
    }
    .system-subheader {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .totals-lock-strict {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 4px solid #D97706;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(217, 119, 6, 0.15);
    }
    .strict-binary-gate {
        background: #FFFBEB;
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #D97706;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .gate-passed {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #16A34A;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .gate-failed {
        background: #FEF2F2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DC2626;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .market-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .badge-strict {
        background: #FEF3C7;
        color: #92400E;
        border: 2px solid #D97706;
        font-weight: 800;
    }
    .data-validation {
        background: #ECFDF5;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #10B981;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# =================== v6.0 EDGE DETECTION ENGINE ===================
class BrutballEdgeEngine:
    """
    BRUTBALL v6.0 - EDGE DETECTION ENGINE
    Heuristic layer: identifies structural advantages in football
    """
    
    @staticmethod
    def evaluate_control_criteria(team_data: Dict, opponent_data: Dict,
                                 is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """Evaluate 4 control criteria with weighted scoring."""
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
        
        # CRITERION 2: Scoring efficiency (weight: 1.0)
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
            rationale.append(f"✅ {team_name}: Scoring efficiency ({efficiency:.1%} of xG > 90%)")
        
        # CRITERION 3: Critical area threat (weight: 0.8)
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"✅ {team_name}: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # CRITERION 4: Repeatable patterns (weight: 0.8)
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
    
    @staticmethod
    def execute_decision_tree(home_data: Dict, away_data: Dict,
                            home_name: str, away_name: str,
                            league_avg_xg: float) -> Dict:
        """Execute v6.0 decision tree to identify structural edges."""
        audit_log = []
        
        audit_log.append("=" * 70)
        audit_log.append("🔍 BRUTBALL v6.0 - EDGE DETECTION ENGINE")
        audit_log.append("=" * 70)
        audit_log.append(f"Match: {home_name} vs {away_name}")
        audit_log.append("")
        
        # Step 1: Identify potential controller
        audit_log.append("STEP 1: CONTROL CRITERIA EVALUATION")
        
        home_score, home_weighted, home_criteria, home_rationale = BrutballEdgeEngine.evaluate_control_criteria(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_score, away_weighted, away_criteria, away_rationale = BrutballEdgeEngine.evaluate_control_criteria(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        audit_log.extend(home_rationale)
        audit_log.extend(away_rationale)
        
        # Get xG values
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # Determine controller for v6.0 logic
        controller = None
        if home_score >= 2 and away_score >= 2:
            if home_weighted > away_weighted:
                controller = home_name
            else:
                controller = away_name
        elif home_score >= 2 and home_score > away_score:
            controller = home_name
        elif away_score >= 2 and away_score > home_score:
            controller = away_name
        
        # Step 2: Apply v6.0 decision logic
        audit_log.append("")
        audit_log.append("STEP 2: DECISION LOGIC APPLICATION")
        
        primary_action = "UNDER 2.5"  # Default conservative
        confidence = 5.0
        secondary_logic = ""
        stake_pct = 1.0
        
        if controller:
            opponent = away_name if controller == home_name else home_name
            
            if combined_xg >= 2.8 and max(home_xg, away_xg) >= 1.6:
                # Goals environment present
                primary_action = f"BACK {controller} & OVER 2.5"
                confidence = 7.5
                secondary_logic = f"Controller + goals environment"
            else:
                # No goals environment
                primary_action = f"BACK {controller}"
                confidence = 8.0
                secondary_logic = "Clean win expected (likely UNDER)"
            
            # Confidence-based stake
            if confidence >= 8.0:
                stake_pct = 2.5
            elif confidence >= 7.0:
                stake_pct = 2.0
            elif confidence >= 6.0:
                stake_pct = 1.5
            else:
                stake_pct = 1.0
                
        elif combined_xg >= 2.8:
            # No controller but goals environment
            primary_action = "OVER 2.5"
            confidence = 6.0
            secondary_logic = "Goals only - no clear controller"
            stake_pct = 1.0
        
        else:
            # No controller, no goals
            primary_action = "UNDER 2.5"
            confidence = 5.5
            secondary_logic = "Low-scoring match expected"
            stake_pct = 0.5
        
        # Ensure reasonable confidence bounds
        confidence = max(5.0, min(confidence, 9.0))
        
        audit_log.append(f"• Primary Action: {primary_action}")
        audit_log.append(f"• Confidence: {confidence:.1f}/10")
        audit_log.append(f"• Stake: {stake_pct:.1f}% (EDGE MODE)")
        if secondary_logic:
            audit_log.append(f"• Logic: {secondary_logic}")
        
        audit_log.append("=" * 70)
        
        return {
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'secondary_logic': secondary_logic,
            'audit_log': audit_log,
            'key_metrics': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'combined_xg': combined_xg,
                'controller': controller,
            },
            'mode': 'EDGE_MODE'
        }

# =================== AGENCY-STATE LOCK ENGINE (UNIFIED) ===================
class AgencyStateLockEngine:
    """
    AGENCY-STATE LOCK ENGINE
    Unified engine for all agency-bound markets
    STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION
    """
    
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, opponent_data: Dict,
                              is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """GATE 1: Evaluate Quiet Control."""
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
            rationale.append(f"GATE 1.1: Tempo dominance (xG: {tempo_xg:.2f} > 1.4)")
        
        # CRITERION 2: Scoring efficiency (weight: 1.0)
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
            rationale.append(f"GATE 1.2: Scoring efficiency ({efficiency:.1%} of xG > 90%)")
        
        # CRITERION 3: Critical area threat (weight: 0.8)
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"GATE 1.3: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # CRITERION 4: Repeatable patterns (weight: 0.8)
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
            rationale.append(f"GATE 1.4: Repeatable attacking patterns")
        
        return raw_score, weighted_score, criteria_met, rationale
    
    @staticmethod
    def check_totals_lock_condition(home_data: Dict, away_data: Dict,
                                   home_name: str, away_name: str) -> Tuple[bool, Dict, List[str]]:
        """Check Totals Lock condition with ACTUAL last 5 data - STRICT BINARY GATE."""
        rationale = []
        
        rationale.append(f"🔍 TOTALS LOCK CONDITION CHECK (STRICT BINARY)")
        rationale.append(f"• Metric: goals_scored_last_5 / 5")
        rationale.append(f"• Threshold: ≤ {TOTALS_LOCK_THRESHOLD}")
        rationale.append(f"• Condition: BOTH teams must pass")
        rationale.append(f"• Gate: Strict binary (NO multipliers, NO smoothing)")
        rationale.append("")
        
        # GET ACTUAL LAST 5 DATA FROM CSV - CORRECT METRIC
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        # Calculate actual averages
        home_last5_avg = home_last5_goals / 5
        away_last5_avg = away_last5_goals / 5
        
        rationale.append(f"📊 ACTUAL LAST 5 DATA FROM CSV:")
        rationale.append(f"• {home_name}: goals_scored_last_5 = {home_last5_goals} → {home_last5_avg:.2f}/match")
        rationale.append(f"• {away_name}: goals_scored_last_5 = {away_last5_goals} → {away_last5_avg:.2f}/match")
        rationale.append("")
        rationale.append(f"📏 THRESHOLD CHECK (≤ {TOTALS_LOCK_THRESHOLD}):")
        
        # STRICT BINARY GATE - NO MULTIPLIERS
        home_passes = home_last5_avg <= TOTALS_LOCK_THRESHOLD
        away_passes = away_last5_avg <= TOTALS_LOCK_THRESHOLD
        
        rationale.append(f"• {home_name}: {home_last5_avg:.2f} {'≤' if home_passes else '>'} {TOTALS_LOCK_THRESHOLD} → {'✅ PASS' if home_passes else '❌ FAIL'}")
        rationale.append(f"• {away_name}: {away_last5_avg:.2f} {'≤' if away_passes else '>'} {TOTALS_LOCK_THRESHOLD} → {'✅ PASS' if away_passes else '❌ FAIL'}")
        
        # BOTH TEAMS MUST PASS - BINARY AND GATE
        totals_lock_condition = home_passes and away_passes
        
        rationale.append("")
        if totals_lock_condition:
            rationale.append(f"✅ TOTALS LOCK CONDITION MET: Both teams ≤ {TOTALS_LOCK_THRESHOLD}")
            rationale.append(f"• Structural certainty: Total goals ≤ {UNDER_GOALS_THRESHOLD}")
        else:
            rationale.append(f"❌ TOTALS LOCK CONDITION NOT MET")
            if not home_passes:
                rationale.append(f"  • {home_name}: {home_last5_avg:.2f} > {TOTALS_LOCK_THRESHOLD} (threshold violated)")
            if not away_passes:
                rationale.append(f"  • {away_name}: {away_last5_avg:.2f} > {TOTALS_LOCK_THRESHOLD} (threshold violated)")
            rationale.append(f"• Totals Lock requires BOTH teams ≤ {TOTALS_LOCK_THRESHOLD}")
        
        # DATA VALIDATION CHECK
        rationale.append("")
        rationale.append("🔍 DATA VALIDATION:")
        rationale.append(f"CSV Column Used: 'goals_scored_last_5'")
        rationale.append(f"Home value: {home_last5_goals}")
        rationale.append(f"Away value: {away_last5_goals}")
        rationale.append(f"Calculation: value / 5")
        rationale.append(f"No season averages used")
        rationale.append(f"No multipliers applied")
        
        return totals_lock_condition, {
            'home_last5_goals': home_last5_goals,
            'away_last5_goals': away_last5_goals,
            'home_last5_avg': home_last5_avg,
            'away_last5_avg': away_last5_avg,
            'home_passes': home_passes,
            'away_passes': away_passes,
            'threshold': TOTALS_LOCK_THRESHOLD,
            'calculation': 'goals_scored_last_5 / 5',
            'strict_binary': True
        }, rationale
    
    @classmethod
    def evaluate_market_state_lock(cls, home_data: Dict, away_data: Dict,
                                 home_name: str, away_name: str,
                                 league_avg_xg: float, market_type: str) -> Dict:
        """Evaluate STATE LOCK for a specific market type."""
        system_log = []
        
        system_log.append("=" * 70)
        system_log.append(f"🔐 STATE LOCK EVALUATION: {market_type}")
        system_log.append("=" * 70)
        system_log.append(f"MATCH: {home_name} vs {away_name}")
        system_log.append("")
        
        # =================== SPECIAL CASE: TOTALS LOCK ===================
        if market_type == 'TOTALS_UNDER_2_5':
            system_log.append("🎯 SPECIAL CASE: TOTALS LOCK (Trend-Based)")
            system_log.append("• Logic: Both teams exhibit low-offense trends")
            system_log.append(f"• Condition: Last 5 matches avg goals ≤ {TOTALS_LOCK_THRESHOLD} for both teams")
            system_log.append("• Gate: Strict binary (NO multipliers, NO smoothing)")
            system_log.append("• CSV Column: goals_scored_last_5")
            system_log.append("")
            
            totals_lock_condition, trend_data, trend_rationale = cls.check_totals_lock_condition(
                home_data, away_data, home_name, away_name
            )
            system_log.extend(trend_rationale)
            
            if totals_lock_condition:
                system_log.append("")
                system_log.append("=" * 70)
                system_log.append(f"🔒 TOTALS LOCK DECLARATION (STRICT)")
                system_log.append("=" * 70)
                
                declaration = f"🔒 TOTALS LOCKED\nTotal goals ≤ {UNDER_GOALS_THRESHOLD}\nBoth teams exhibit sustained low-offense trends\nStructural certainty for UNDER\nSTRICT BINARY GATE: Both ≤ {TOTALS_LOCK_THRESHOLD}"
                
                system_log.append(declaration)
                system_log.append("")
                system_log.append("💰 CAPITAL AUTHORIZATION: GRANTED")
                system_log.append(f"• Trend Condition: BOTH teams last 5 avg goals ≤ {TOTALS_LOCK_THRESHOLD}")
                system_log.append(f"• {home_name}: {trend_data['home_last5_avg']:.2f} goals/match (last 5)")
                system_log.append(f"• {away_name}: {trend_data['away_last5_avg']:.2f} goals/match (last 5)")
                system_log.append("• Gate: Strict binary (no multipliers)")
                system_log.append("• Match: Structurally low-scoring")
                system_log.append("=" * 70)
                
                return {
                    'market': market_type,
                    'state_locked': True,
                    'declaration': declaration,
                    'system_log': system_log,
                    'reason': f"Totals Lock condition met (both teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals - STRICT)",
                    'capital_authorized': True,
                    'trend_based': True,
                    'trend_data': trend_data,
                    'key_metrics': trend_data,
                    'strict_binary': True
                }
            else:
                system_log.append("❌ TOTALS LOCK NOT APPLICABLE")
                system_log.append("• Threshold condition not met")
                system_log.append("⚠️ FALLBACK TO EDGE MODE FOR TOTALS")
                
                return {
                    'market': market_type,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': f"Totals Lock condition not met",
                    'capital_authorized': False,
                    'trend_based': True,
                    'strict_binary': True
                }
        
        # =================== STANDARD AGENCY-STATE MARKETS ===================
        # (Keeping existing logic for other markets)
        system_log.append("🎯 STANDARD AGENCY-STATE MARKET")
        system_log.append("• Logic: Agency suppression of one team")
        system_log.append("")
        
        # ... existing agency-state logic for other markets ...
        
        return {
            'market': market_type,
            'state_locked': False,
            'system_log': system_log,
            'reason': f"Agency-state logic for {market_type} (not implemented in this fix)",
            'capital_authorized': False
        }
    
    @classmethod
    def evaluate_all_markets(cls, home_data: Dict, away_data: Dict,
                           home_name: str, away_name: str,
                           league_avg_xg: float) -> Dict:
        """Evaluate STATE LOCK for all markets including Totals Lock."""
        
        # For now, just evaluate Totals Lock (primary focus of fix)
        markets_to_evaluate = ['TOTALS_UNDER_2_5']
        
        results = {}
        locked_markets = []
        
        for market in markets_to_evaluate:
            result = cls.evaluate_market_state_lock(
                home_data, away_data, home_name, away_name, league_avg_xg, market
            )
            results[market] = result
            
            if result['state_locked']:
                locked_markets.append({
                    'market': market,
                    'type': 'trend_based',
                    'reason': result['reason'],
                    'strict_binary': result.get('strict_binary', False)
                })
        
        # Determine if Totals Lock is active
        has_totals_lock = results.get('TOTALS_UNDER_2_5', {}).get('state_locked', False)
        strongest_market = 'TOTALS_UNDER_2_5' if has_totals_lock else None
        
        return {
            'all_results': results,
            'locked_markets': locked_markets,
            'strongest_market': strongest_market,
            'total_markets': len(markets_to_evaluate),
            'locked_count': len(locked_markets),
            'has_totals_lock': has_totals_lock,
            'strict_binary': results.get('TOTALS_UNDER_2_5', {}).get('strict_binary', False)
        }

# =================== INTEGRATED BRUTBALL ARCHITECTURE ===================
class BrutballIntegratedArchitecture:
    """
    BRUTBALL INTEGRATED ARCHITECTURE
    v6.0 Edge Detection + Totals Lock (FIXED)
    """
    
    @staticmethod
    def execute_totals_lock_analysis(home_data: Dict, away_data: Dict,
                                   home_name: str, away_name: str,
                                   league_avg_xg: float) -> Dict:
        """Execute analysis with FIXED Totals Lock."""
        
        # Run v6.0 Edge Detection Engine
        edge_result = BrutballEdgeEngine.execute_decision_tree(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Run Totals Lock Evaluation with FIXED logic
        totals_lock_result = AgencyStateLockEngine.evaluate_all_markets(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Determine capital mode
        if totals_lock_result['has_totals_lock']:
            capital_mode = 'LOCK_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['LOCK_MODE']
            capital_authorization = "AUTHORIZED (TOTALS LOCK - STRICT)"
            system_verdict = "DUAL LOW-OFFENSE STATE DETECTED (STRICT)"
        else:
            capital_mode = 'EDGE_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['EDGE_MODE']
            capital_authorization = "STANDARD (v6.0 EDGE)"
            system_verdict = "NO TOTALS LOCK"
        
        # Create integrated system log
        system_log = []
        system_log.append("=" * 70)
        system_log.append("⚖️🔒✅ BRUTBALL TOTALS LOCK (FIXED)")
        system_log.append("=" * 70)
        system_log.append(f"ARCHITECTURE: v6.0 Edge + Totals Lock (STRICT BINARY)")
        system_log.append(f"  • Metric: goals_scored_last_5 / 5")
        system_log.append(f"  • Threshold: ≤ {TOTALS_LOCK_THRESHOLD}")
        system_log.append(f"  • Gate: Strict binary (NO multipliers)")
        system_log.append(f"  • Condition: BOTH teams must pass")
        system_log.append("")
        
        system_log.append("🔍 v6.0 EDGE DETECTION RESULT")
        system_log.append(f"  • Action: {edge_result['primary_action']}")
        system_log.append(f"  • Confidence: {edge_result['confidence']:.1f}/10")
        system_log.append(f"  • Base Stake: {edge_result['stake_pct']:.1f}%")
        system_log.append("")
        
        system_log.append("🔐 TOTALS LOCK EVALUATION (FIXED)")
        system_log.append(f"  • CSV Column: goals_scored_last_5")
        
        totals_result = totals_lock_result['all_results']['TOTALS_UNDER_2_5']
        trend_data = totals_result.get('trend_data', {})
        
        system_log.append(f"  • {home_name} last 5 goals: {trend_data.get('home_last5_goals', 0)}")
        system_log.append(f"  • {away_name} last 5 goals: {trend_data.get('away_last5_goals', 0)}")
        system_log.append(f"  • {home_name} avg: {trend_data.get('home_last5_avg', 0):.2f}/match")
        system_log.append(f"  • {away_name} avg: {trend_data.get('away_last5_avg', 0):.2f}/match")
        
        if totals_lock_result['has_totals_lock']:
            system_log.append(f"  • Result: TOTALS LOCKED (Both ≤ {TOTALS_LOCK_THRESHOLD})")
            system_log.append("  • Capital Authorization: GRANTED")
        else:
            system_log.append(f"  • Result: NO TOTALS LOCK")
            system_log.append(f"  • Reason: {totals_result['reason']}")
            system_log.append("  • Capital Authorization: STANDARD")
        system_log.append("")
        
        system_log.append("💰 CAPITAL DECISION")
        system_log.append(f"  • Capital Mode: {capital_mode}")
        system_log.append(f"  • Stake Multiplier: {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x")
        system_log.append(f"  • Final Stake: {final_stake:.2f}%")
        system_log.append(f"  • Authorization: {capital_authorization}")
        system_log.append("")
        system_log.append(f"🎯 SYSTEM VERDICT: {system_verdict}")
        system_log.append("=" * 70)
        
        return {
            'architecture': 'Totals Lock (Fixed)',
            'v6_result': edge_result,
            'totals_lock_result': totals_lock_result,
            'capital_mode': capital_mode,
            'final_stake': final_stake,
            'system_verdict': system_verdict,
            'system_log': system_log,
            'integrated_output': {
                'primary_action': edge_result['primary_action'],
                'has_totals_lock': totals_lock_result['has_totals_lock'],
                'capital_authorized': capital_authorization,
                'stake_multiplier': CAPITAL_MULTIPLIERS[capital_mode],
                'final_stake_pct': final_stake,
                'edge_confidence': edge_result['confidence'],
                'strict_binary': True
            }
        }

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data with correct CSV headings."""
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
        
        # Calculate derived metrics using correct CSV headings
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
    """Calculate all derived metrics using correct CSV headings."""
    
    # Calculate per-match averages using CSV headings
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Calculate LAST 5 averages (already in CSV as totals, need per-match)
    df['home_last5_avg_goals'] = df['goals_scored_last_5'] / 5
    df['away_last5_avg_goals'] = df['goals_scored_last_5'] / 5  # Note: CSV has total last 5, not split home/away
    
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
    st.markdown('<div class="system-header">⚖️🔒✅ BRUTBALL TOTALS LOCK (FIXED)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>STRICT BINARY GATE FIXED • NO MULTIPLIERS • ACTUAL CSV DATA</strong></p>
        <p>Metric: goals_scored_last_5 / 5 • Threshold: ≤ 1.2 • Condition: BOTH teams must pass</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Strict Binary Gate Display
    st.markdown("""
    <div class="totals-lock-strict">
        <h3 style="color: #92400E; margin: 0 0 1rem 0;">✅ TOTALS LOCK FIXED - STRICT BINARY GATE</h3>
        <div style="margin: 1rem 0;">
            <div class="strict-binary-gate">
                home_last5_avg = goals_scored_last_5 / 5<br>
                away_last5_avg = goals_scored_last_5 / 5<br>
                <br>
                home_passes = home_last5_avg ≤ 1.2<br>
                away_passes = away_last5_avg ≤ 1.2<br>
                <br>
                totals_lock = home_passes AND away_passes<br>
                <br>
                <strong>NO multipliers • NO smoothing • NO season averages</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(8)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary"
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
    if st.button("⚡ EXECUTE TOTALS LOCK ANALYSIS (FIXED)", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute fixed analysis
        result = BrutballIntegratedArchitecture.execute_totals_lock_analysis(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 TOTALS LOCK ANALYSIS (FIXED)")
        
        # Get results
        totals_lock_result = result['totals_lock_result']
        totals_data = totals_lock_result['all_results']['TOTALS_UNDER_2_5'].get('trend_data', {})
        
        # Data Validation Display
        st.markdown("""
        <div class="data-validation">
            <h4 style="color: #065F46; margin: 0 0 1rem 0;">📊 DATA VALIDATION</h4>
            <div style="font-family: 'Courier New', monospace;">
                CSV Column Used: goals_scored_last_5<br>
                Home ({home_team}): {home_goals} goals in last 5<br>
                Away ({away_team}): {away_goals} goals in last 5<br>
                Calculation: goals / 5<br>
                Threshold: ≤ {threshold}<br>
                Gate: Strict binary (no multipliers)
            </div>
        </div>
        """.format(
            home_team=home_team,
            away_team=away_team,
            home_goals=totals_data.get('home_last5_goals', 'N/A'),
            away_goals=totals_data.get('away_last5_goals', 'N/A'),
            threshold=TOTALS_LOCK_THRESHOLD
        ), unsafe_allow_html=True)
        
        # Threshold Check Display
        st.markdown("### 📏 THRESHOLD CHECK (STRICT)")
        
        home_passes = totals_data.get('home_passes', False)
        away_passes = totals_data.get('away_passes', False)
        
        if home_passes:
            st.markdown(f"""
            <div class="gate-passed">
                <h4 style="color: #16A34A; margin: 0;">{home_team}</h4>
                <div style="margin: 0.5rem 0;">
                    Last 5 goals: {totals_data.get('home_last5_goals', 0)}<br>
                    Average: {totals_data.get('home_last5_avg', 0):.2f}/match<br>
                    Status: ✅ PASSES (≤ {TOTALS_LOCK_THRESHOLD})
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="gate-failed">
                <h4 style="color: #DC2626; margin: 0;">{home_team}</h4>
                <div style="margin: 0.5rem 0;">
                    Last 5 goals: {totals_data.get('home_last5_goals', 0)}<br>
                    Average: {totals_data.get('home_last5_avg', 0):.2f}/match<br>
                    Status: ❌ FAILS (> {TOTALS_LOCK_THRESHOLD})
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if away_passes:
            st.markdown(f"""
            <div class="gate-passed">
                <h4 style="color: #16A34A; margin: 0;">{away_team}</h4>
                <div style="margin: 0.5rem 0;">
                    Last 5 goals: {totals_data.get('away_last5_goals', 0)}<br>
                    Average: {totals_data.get('away_last5_avg', 0):.2f}/match<br>
                    Status: ✅ PASSES (≤ {TOTALS_LOCK_THRESHOLD})
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="gate-failed">
                <h4 style="color: #DC2626; margin: 0;">{away_team}</h4>
                <div style="margin: 0.5rem 0;">
                    Last 5 goals: {totals_data.get('away_last5_goals', 0)}<br>
                    Average: {totals_data.get('away_last5_avg', 0):.2f}/match<br>
                    Status: ❌ FAILS (> {TOTALS_LOCK_THRESHOLD})
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Final Decision
        if totals_lock_result['has_totals_lock']:
            st.markdown("""
            <div class="totals-lock-strict">
                <h3 style="color: #92400E; margin: 0 0 1rem 0;">✅ TOTALS LOCK ACTIVE</h3>
                <p style="color: #374151; margin: 0.5rem 0;">
                    Both teams ≤ {threshold} avg goals (last 5)<br>
                    Structural certainty for UNDER {under_goals}<br>
                    Capital: 2.0x multiplier authorized
                </p>
                <span class="market-badge badge-strict">TOTALS ≤{under_goals} LOCKED</span>
            </div>
            """.format(
                threshold=TOTALS_LOCK_THRESHOLD,
                under_goals=UNDER_GOALS_THRESHOLD
            ), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="gate-failed">
                <h3 style="color: #DC2626; margin: 0 0 1rem 0;">❌ NO TOTALS LOCK</h3>
                <p style="color: #374151; margin: 0.5rem 0;">
                    Condition not met: Both teams must be ≤ {threshold}<br>
                    Falls back to Edge Mode<br>
                    Capital: 1.0x multiplier only
                </p>
            </div>
            """.format(threshold=TOTALS_LOCK_THRESHOLD), unsafe_allow_html=True)
        
        # System log
        with st.expander("📋 VIEW SYSTEM LOG", expanded=True):
            st.code('\n'.join(result['system_log']), language='text')
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        export_text = f"""BRUTBALL TOTALS LOCK ANALYSIS (FIXED)
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

TOTALS LOCK CONFIGURATION:
• Metric: goals_scored_last_5 / 5
• Threshold: ≤ {TOTALS_LOCK_THRESHOLD}
• Gate: Strict binary (NO multipliers)
• Condition: BOTH teams must pass

DATA VALIDATION:
• CSV Column Used: goals_scored_last_5
• {home_team}: {totals_data.get('home_last5_goals', 0)} goals in last 5
• {away_team}: {totals_data.get('away_last5_goals', 0)} goals in last 5
• Calculation: value / 5
• No season averages used
• No multipliers applied

THRESHOLD CHECKS:
{home_team}:
  • Last 5 goals: {totals_data.get('home_last5_goals', 0)}
  • Average: {totals_data.get('home_last5_avg', 0):.2f}/match
  • Passes ≤ {TOTALS_LOCK_THRESHOLD}: {'YES' if home_passes else 'NO'}

{away_team}:
  • Last 5 goals: {totals_data.get('away_last5_goals', 0)}
  • Average: {totals_data.get('away_last5_avg', 0):.2f}/match
  • Passes ≤ {TOTALS_LOCK_THRESHOLD}: {'YES' if away_passes else 'NO'}

FINAL DECISION:
• Totals Lock Active: {'YES' if totals_lock_result['has_totals_lock'] else 'NO'}
• Capital Multiplier: {CAPITAL_MULTIPLIERS[result['capital_mode']]:.1f}x
• Final Stake: {result['final_stake']:.2f}%
• System Verdict: {result['system_verdict']}

SYSTEM LOG:
{chr(10).join(result['system_log'])}

===========================================
BRUTBALL TOTALS LOCK (FIXED)
STRICT BINARY GATE • NO MULTIPLIERS • ACTUAL CSV DATA
        """
        
        st.download_button(
            label="📥 Download Analysis",
            data=export_text,
            file_name=f"brutball_totals_lock_fixed_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL TOTALS LOCK (FIXED)</strong></p>
        <p>Metric: goals_scored_last_5 / 5 • Threshold: ≤ 1.2 • Condition: BOTH teams must pass</p>
        <p>STRICT BINARY GATE • NO MULTIPLIERS • ACTUAL CSV DATA</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
