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

# Absolute Lock Engine Constants (NEW)
ABSOLUTE_DIRECTION_THRESHOLD = 0.75    # Δ must be significantly > 0.25
ABSOLUTE_ENFORCEMENT_REQUIRED = 3      # Must have ≥3 enforcement methods
ABSOLUTE_STATE_FLIP_FAILURES = 4       # Opponent must fail ALL 4 checks
ABSOLUTE_SHOCK_IMMUNITY_REQUIRED = 2   # Must have ≥2 shock immunity methods
ABSOLUTE_CONTROL_CRITERIA = 3          # Must meet ≥3 quiet control criteria

# Market-Specific Thresholds for Agency-State Framework (NEW)
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
    }
}

# Capital Multipliers
CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,     # v6.0 only
    'LOCK_MODE': 2.0,     # v6.0 + v6.1.1 STATE LOCKED
    'ABSOLUTE_MODE': 3.0  # v6.0 + v6.1.1 + Absolute Lock
}

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1.2 + AGENCY-STATE FRAMEWORK",
    page_icon="⚖️🔒",
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
    .agency-state-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 4px solid #16A34A;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(22, 163, 74, 0.15);
    }
    .market-locked-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%);
        border: 3px solid #059669;
        margin: 1rem 0;
        text-align: left;
    }
    .market-available-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        margin: 1rem 0;
        text-align: left;
    }
    .market-unavailable-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border: 3px solid #9CA3AF;
        margin: 1rem 0;
        text-align: left;
        opacity: 0.7;
    }
    .capital-mode-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 700;
    }
    .edge-mode {
        background: #EFF6FF;
        color: #1E40AF;
        border: 3px solid #3B82F6;
    }
    .lock-mode {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        color: #166534;
        border: 3px solid #16A34A;
    }
    .absolute-mode {
        background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%);
        color: #065F46;
        border: 3px solid #059669;
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
    .badge-state {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .badge-noise {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
    }
    .badge-locked {
        background: #A7F3D0;
        color: #065F46;
        border: 1px solid #10B981;
        font-weight: 800;
    }
    .agency-insight {
        background: #E0F2FE;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #38BDF8;
        margin: 1rem 0;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .metric-row-state {
        background: #F0FDF4;
        border-left: 3px solid #16A34A;
    }
    .metric-row-agency {
        background: #E0F2FE;
        border-left: 3px solid #38BDF8;
    }
    .architecture-diagram {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        text-align: center;
    }
    .three-tier-architecture {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        margin: 2rem 0;
    }
    .tier-level {
        width: 300px;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        position: relative;
    }
    .tier-3 {
        background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%);
        border: 3px solid #059669;
        color: #065F46;
        font-weight: 900;
    }
    .tier-2 {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 3px solid #16A34A;
        color: #166534;
        font-weight: 700;
    }
    .tier-1 {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        color: #1E40AF;
    }
    .agency-principle {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #38BDF8;
        margin: 1rem 0;
    }
    .state-bound-list {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #86EFAC;
        margin: 0.5rem 0;
    }
    .noise-list {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #D1D5DB;
        margin: 0.5rem 0;
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
        decision_steps = []
        
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
        
        # Determine favorite (by position)
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
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
            # Controller exists
            opponent = away_name if controller == home_name else home_name
            is_underdog = controller == underdog
            
            if combined_xg >= 2.8 and max(home_xg, away_xg) >= 1.6:
                # Goals environment present
                primary_action = f"BACK {controller} & OVER 2.5"
                confidence = 7.5
                secondary_logic = f"Controller + goals environment"
                
                if is_underdog:
                    confidence -= 0.5
                    secondary_logic += " (underdog controller)"
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
            'decision_steps': [
                f"1. Control evaluation: {controller if controller else 'No clear controller'}",
                f"2. Combined xG: {combined_xg:.2f} ({'≥2.8' if combined_xg >= 2.8 else '<2.8'})",
                f"3. Max xG: {max(home_xg, away_xg):.2f} ({'≥1.6' if max(home_xg, away_xg) >= 1.6 else '<1.6'})",
                f"4. Decision: {primary_action} (Confidence: {confidence:.1f}/10)"
            ],
            'key_metrics': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'combined_xg': combined_xg,
                'controller': controller,
                'favorite': favorite,
                'underdog': underdog
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
    def check_directional_dominance(controller_xg: float, opponent_xg: float,
                                   controller_name: str, opponent_name: str,
                                   market_type: str) -> Tuple[bool, float, List[str]]:
        """GATE 2: Check directional dominance with market-specific thresholds."""
        rationale = []
        control_delta = controller_xg - opponent_xg
        market_threshold = MARKET_THRESHOLDS[market_type]['opponent_xg_max']
        
        rationale.append(f"GATE 2: DIRECTIONAL DOMINANCE ({market_type})")
        rationale.append(f"• Controller xG ({controller_name}): {controller_xg:.2f}")
        rationale.append(f"• Opponent xG ({opponent_name}): {opponent_xg:.2f}")
        rationale.append(f"• Control Delta: {control_delta:+.2f}")
        rationale.append(f"• Minimum Δ Threshold: > {DIRECTION_THRESHOLD}")
        rationale.append(f"• Market-Specific Threshold: opponent xG < {market_threshold}")
        
        # Check both conditions
        delta_condition = control_delta > DIRECTION_THRESHOLD
        opponent_xg_condition = opponent_xg < market_threshold
        
        if delta_condition and opponent_xg_condition:
            rationale.append(f"✅ Directional dominance confirmed")
            rationale.append(f"  • Δ = {control_delta:+.2f} > {DIRECTION_THRESHOLD}")
            rationale.append(f"  • Opponent xG = {opponent_xg:.2f} < {market_threshold}")
            return True, control_delta, rationale
        else:
            rationale.append(f"❌ Directional dominance insufficient")
            if not delta_condition:
                rationale.append(f"  • Δ = {control_delta:+.2f} ≤ {DIRECTION_THRESHOLD}")
            if not opponent_xg_condition:
                rationale.append(f"  • Opponent xG = {opponent_xg:.2f} ≥ {market_threshold}")
            return False, control_delta, rationale
    
    @staticmethod
    def check_agency_collapse(opponent_data: Dict, is_home: bool,
                             opponent_name: str, league_avg_xg: float,
                             market_type: str) -> Tuple[bool, int, List[str]]:
        """GATE 3: Check agency collapse with market-specific requirements."""
        rationale = []
        failures = 0
        check_details = []
        
        rationale.append(f"GATE 3: AGENCY COLLAPSE CHECK ({market_type})")
        
        # Get market-specific requirements
        required_failures = MARKET_THRESHOLDS[market_type]['state_flip_failures']
        
        # CHECK 1: Chase capacity
        if is_home:
            chase_xg = opponent_data.get('home_xg_per_match', 0)
        else:
            chase_xg = opponent_data.get('away_xg_per_match', 0)
        
        if chase_xg < 1.1:
            failures += 1
            check_details.append(f"✅ Chase xG {chase_xg:.2f} < 1.1")
        else:
            check_details.append(f"❌ Chase xG {chase_xg:.2f} ≥ 1.1")
        
        # CHECK 2: Tempo surge capability
        if chase_xg < 1.4:
            failures += 1
            check_details.append(f"✅ No tempo surge (xG {chase_xg:.2f} < 1.4)")
        else:
            check_details.append(f"❌ Tempo surge possible")
        
        # CHECK 3: Alternate threat channels
        if is_home:
            setpiece_pct = opponent_data.get('home_setpiece_pct', 0)
            counter_pct = opponent_data.get('home_counter_pct', 0)
        else:
            setpiece_pct = opponent_data.get('away_setpiece_pct', 0)
            counter_pct = opponent_data.get('away_counter_pct', 0)
        
        if setpiece_pct < 0.25 and counter_pct < 0.15:
            failures += 1
            check_details.append(f"✅ No alternate threat (SP: {setpiece_pct:.1%}, C: {counter_pct:.1%})")
        else:
            check_details.append(f"❌ Alternate threat exists")
        
        # CHECK 4: Substitution leverage
        if is_home:
            gpm = opponent_data.get('home_goals_per_match', 0)
        else:
            gpm = opponent_data.get('away_goals_per_match', 0)
        
        if gpm < league_avg_xg * 0.8:
            failures += 1
            check_details.append(f"✅ Low substitution leverage ({gpm:.2f} < {league_avg_xg*0.8:.2f})")
        else:
            check_details.append(f"❌ Adequate bench impact")
        
        # Add all check details
        for detail in check_details:
            rationale.append(f"  • {detail}")
        
        # Check market-specific requirements
        if failures >= required_failures:
            rationale.append(f"✅ AGENCY COLLAPSE: {failures}/{required_failures}+ failures")
            return True, failures, rationale
        else:
            rationale.append(f"❌ Insufficient agency collapse: {failures}/{required_failures} failures")
            return False, failures, rationale
    
    @staticmethod
    def check_non_urgent_enforcement(controller_data: Dict, is_home: bool,
                                    controller_name: str, market_type: str) -> Tuple[bool, int, List[str]]:
        """GATE 4: Check non-urgent enforcement with market-specific requirements."""
        rationale = []
        enforce_methods = 0
        method_details = []
        
        rationale.append(f"GATE 4: NON-URGENT ENFORCEMENT ({market_type})")
        
        # Get market-specific requirements
        required_methods = MARKET_THRESHOLDS[market_type]['enforcement_methods']
        
        if is_home:
            # METHOD 1: Defensive solidity at home
            goals_conceded = controller_data.get('home_goals_conceded', 0)
            matches_played = controller_data.get('home_matches_played', 1)
            gcp_match = goals_conceded / matches_played
            
            if gcp_match < 1.2:
                enforce_methods += 1
                method_details.append(f"✅ Can defend lead (concedes {gcp_match:.2f}/match)")
            else:
                method_details.append(f"❌ Defensive concerns ({gcp_match:.2f}/match)")
            
            # METHOD 2: Alternate scoring at home
            setpiece_pct = controller_data.get('home_setpiece_pct', 0)
            counter_pct = controller_data.get('home_counter_pct', 0)
            
            if setpiece_pct > 0.25 or counter_pct > 0.15:
                enforce_methods += 1
                method_details.append(f"✅ Alternate scoring (SP: {setpiece_pct:.1%}, C: {counter_pct:.1%})")
            else:
                method_details.append(f"❌ Limited alternate scoring")
            
            # METHOD 3: Consistent threat at home
            xg_per_match = controller_data.get('home_xg_per_match', 0)
            if xg_per_match > 1.3:
                enforce_methods += 1
                method_details.append(f"✅ Consistent threat (xG: {xg_per_match:.2f})")
            else:
                method_details.append(f"❌ Requires xG spikes")
            
            # METHOD 4: Ball retention capability
            # Using goals/xG ratio as proxy for control
            goals_scored = controller_data.get('home_goals_scored', 0)
            xg_for = controller_data.get('home_xg_for', 0)
            efficiency = goals_scored / max(xg_for, 0.1)
            
            if efficiency > 0.85:
                enforce_methods += 1
                method_details.append(f"✅ Efficient finishing ({efficiency:.1%}) reduces urgency")
            else:
                method_details.append(f"❌ Requires volume scoring")
        
        else:  # Away team
            # METHOD 1: Defensive solidity away
            goals_conceded = controller_data.get('away_goals_conceded', 0)
            matches_played = controller_data.get('away_matches_played', 1)
            gcp_match = goals_conceded / matches_played
            
            if gcp_match < 1.3:
                enforce_methods += 1
                method_details.append(f"✅ Can defend away ({gcp_match:.2f}/match)")
            else:
                method_details.append(f"❌ Defensive concerns away")
            
            # METHOD 2: Away scoring versatility
            setpiece_pct = controller_data.get('away_setpiece_pct', 0)
            counter_pct = controller_data.get('away_counter_pct', 0)
            
            if setpiece_pct > 0.2 or counter_pct > 0.12:
                enforce_methods += 1
                method_details.append(f"✅ Away scoring versatility")
            else:
                method_details.append(f"❌ Limited away scoring")
            
            # METHOD 3: Away consistency
            xg_per_match = controller_data.get('away_xg_per_match', 0)
            if xg_per_match > 1.2:
                enforce_methods += 1
                method_details.append(f"✅ Consistent away threat (xG: {xg_per_match:.2f})")
            else:
                method_details.append(f"❌ Requires exceptional away performance")
            
            # METHOD 4: Away efficiency
            goals_scored = controller_data.get('away_goals_scored', 0)
            xg_for = controller_data.get('away_xg_for', 0)
            efficiency = goals_scored / max(xg_for, 0.1)
            
            if efficiency > 0.9:
                enforce_methods += 1
                method_details.append(f"✅ Elite away finishing ({efficiency:.1%})")
            else:
                method_details.append(f"❌ Away efficiency concerns")
        
        # Add all method details
        for detail in method_details:
            rationale.append(f"  • {detail}")
        
        # Check market-specific requirements
        if enforce_methods >= required_methods:
            rationale.append(f"✅ NON-URGENT ENFORCEMENT: {enforce_methods}/{required_methods}+ methods")
            return True, enforce_methods, rationale
        else:
            rationale.append(f"❌ Insufficient enforcement: {enforce_methods}/{required_methods} methods")
            return False, enforce_methods, rationale
    
    @classmethod
    def evaluate_market_state_lock(cls, home_data: Dict, away_data: Dict,
                                 home_name: str, away_name: str,
                                 league_avg_xg: float, market_type: str) -> Dict:
        """Evaluate STATE LOCK for a specific market type."""
        system_log = []
        gates_passed = 0
        total_gates = 4
        
        system_log.append("=" * 70)
        system_log.append(f"🔐 AGENCY-STATE LOCK EVALUATION: {market_type}")
        system_log.append("=" * 70)
        system_log.append(f"MATCH: {home_name} vs {away_name}")
        system_log.append("")
        
        # =================== GATE 1: QUIET CONTROL ===================
        system_log.append("GATE 1: QUIET CONTROL IDENTIFICATION")
        
        home_score, home_weighted, home_criteria, home_rationale = cls.evaluate_quiet_control(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_score, away_weighted, away_criteria, away_rationale = cls.evaluate_quiet_control(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        system_log.extend(home_rationale)
        system_log.extend(away_rationale)
        
        # Determine controller WITHOUT status resolution
        controller = None
        
        # v6.1.2: Check for mutual control
        both_meet_control = (home_score >= CONTROL_CRITERIA_REQUIRED and 
                            away_score >= CONTROL_CRITERIA_REQUIRED)
        
        if both_meet_control:
            weighted_diff = abs(home_weighted - away_weighted)
            
            if weighted_diff <= QUIET_CONTROL_SEPARATION_THRESHOLD:
                system_log.append(f"⚠️ v6.1.2: Mutual control detected")
                system_log.append(f"  • Weighted difference: {weighted_diff:.2f} ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD}")
                system_log.append("• NO SINGLE CONTROLLER → NO STATE LOCK")
                system_log.append("⚠️ SYSTEM SILENT")
                
                return {
                    'market': market_type,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': f"v6.1.2: Mutual control (weighted difference ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD})",
                    'capital_authorized': False,
                    'mutual_control': True
                }
            
            if home_weighted > away_weighted:
                controller = home_name
                system_log.append(f"• Controller: {home_name} (weighted advantage)")
            else:
                controller = away_name
                system_log.append(f"• Controller: {away_name} (weighted advantage)")
        
        elif home_score >= CONTROL_CRITERIA_REQUIRED and home_score > away_score:
            controller = home_name
            system_log.append(f"• Controller: {home_name} ({home_score}/4 criteria)")
            
        elif away_score >= CONTROL_CRITERIA_REQUIRED and away_score > home_score:
            controller = away_name
            system_log.append(f"• Controller: {away_name} ({away_score}/4 criteria)")
        
        else:
            system_log.append("❌ GATE 1 FAILED: No Quiet Control identified")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"No team meets {CONTROL_CRITERIA_REQUIRED}+ control criteria",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 1 PASSED: Quiet Control → {controller}")
        
        # =================== GATE 2: DIRECTIONAL DOMINANCE ===================
        system_log.append("")
        system_log.append("GATE 2: DIRECTIONAL DOMINANCE")
        
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        controller_xg = home_data.get('home_xg_per_match', 0) if is_controller_home else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if is_controller_home else home_data.get('home_xg_per_match', 0)
        
        has_direction, control_delta, direction_rationale = cls.check_directional_dominance(
            controller_xg, opponent_xg, controller, opponent, market_type
        )
        system_log.extend(direction_rationale)
        
        if not has_direction:
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Directional dominance insufficient for {market_type}",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 2 PASSED: Directional dominance confirmed (Δ = {control_delta:+.2f})")
        
        # =================== GATE 3: AGENCY COLLAPSE ===================
        system_log.append("")
        system_log.append("GATE 3: AGENCY COLLAPSE")
        
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        agency_collapsed, failures, collapse_rationale = cls.check_agency_collapse(
            opponent_data, is_opponent_home, opponent, league_avg_xg, market_type
        )
        system_log.extend(collapse_rationale)
        
        if not agency_collapsed:
            required_failures = MARKET_THRESHOLDS[market_type]['state_flip_failures']
            system_log.append(f"❌ GATE 3 FAILED: Insufficient agency collapse ({failures}/{required_failures})")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Insufficient agency collapse for {market_type} ({failures}/{required_failures})",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 3 PASSED: Agency collapse confirmed ({failures}/4 failures)")
        
        # =================== GATE 4: NON-URGENT ENFORCEMENT ===================
        system_log.append("")
        system_log.append("GATE 4: NON-URGENT ENFORCEMENT")
        
        controller_data = home_data if controller == home_name else away_data
        
        can_enforce, enforce_methods, enforce_rationale = cls.check_non_urgent_enforcement(
            controller_data, is_controller_home, controller, market_type
        )
        system_log.extend(enforce_rationale)
        
        if not can_enforce:
            required_methods = MARKET_THRESHOLDS[market_type]['enforcement_methods']
            system_log.append(f"❌ GATE 4 FAILED: Insufficient enforcement capacity ({enforce_methods}/{required_methods})")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Insufficient enforcement capacity for {market_type} ({enforce_methods}/{required_methods})",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4 PASSED: Non-urgent enforcement confirmed ({enforce_methods}/2+ methods)")
        
        # =================== STATE LOCK DECLARATION ===================
        system_log.append("")
        system_log.append("=" * 70)
        system_log.append(f"🔒 {market_type} STATE LOCK DECLARATION")
        system_log.append("=" * 70)
        
        # Market-specific declarations
        declarations = {
            'WINNER': f"🔒 WINNER LOCKED\n{controller} cannot lose\n{opponent} has no agency to change result",
            'CLEAN_SHEET': f"🔒 CLEAN SHEET LOCKED\n{controller} will not concede\n{opponent} has no scoring agency",
            'TEAM_NO_SCORE': f"🔒 TEAM NO SCORE LOCKED\n{opponent} will not score\nScoring agency structurally suppressed",
            'OPPONENT_UNDER_1_5': f"🔒 OPPONENT UNDER 1.5 LOCKED\n{opponent} cannot score >1 goal\nAgency limited to minimal threat"
        }
        
        declaration = declarations.get(market_type, f"🔒 STATE LOCKED\n{controller} controls {market_type} state")
        
        system_log.append(declaration)
        system_log.append("")
        system_log.append("💰 CAPITAL AUTHORIZATION: GRANTED")
        system_log.append(f"• All {total_gates}/{total_gates} gates passed")
        system_log.append(f"• Control Delta: {control_delta:+.2f}")
        system_log.append(f"• Agency Collapse: {failures}/4 failures")
        system_log.append(f"• Enforcement Methods: {enforce_methods}/2+")
        system_log.append(f"• Market: {market_type} structurally controlled")
        system_log.append("=" * 70)
        
        return {
            'market': market_type,
            'state_locked': True,
            'declaration': declaration,
            'system_log': system_log,
            'reason': f"All agency-state gates passed for {market_type}",
            'capital_authorized': True,
            'controller': controller,
            'opponent': opponent,
            'control_delta': control_delta,
            'agency_failures': failures,
            'enforce_methods': enforce_methods,
            'key_metrics': {
                'controller_xg': controller_xg,
                'opponent_xg': opponent_xg
            }
        }
    
    @classmethod
    def evaluate_all_markets(cls, home_data: Dict, away_data: Dict,
                           home_name: str, away_name: str,
                           league_avg_xg: float) -> Dict:
        """Evaluate STATE LOCK for all agency-bound markets."""
        
        markets_to_evaluate = ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']
        
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
                    'controller': result['controller'],
                    'delta': result['control_delta'],
                    'reason': result['reason']
                })
        
        # Determine strongest market (highest delta)
        strongest_market = None
        strongest_delta = 0
        
        for market, result in results.items():
            if result['state_locked'] and result['control_delta'] > strongest_delta:
                strongest_delta = result['control_delta']
                strongest_market = market
        
        return {
            'all_results': results,
            'locked_markets': locked_markets,
            'strongest_market': strongest_market,
            'strongest_delta': strongest_delta,
            'total_markets': len(markets_to_evaluate),
            'locked_count': len(locked_markets)
        }

# =================== ABSOLUTE LOCK ENGINE ===================
class BrutballAbsoluteLockEngine:
    """Absolute Lock Engine (for completeness, though not focus of agency-state)"""
    
    @classmethod
    def execute_absolute_lock_evaluation(cls, home_data: Dict, away_data: Dict,
                                        home_name: str, away_name: str,
                                        league_avg_xg: float,
                                        state_lock_result: Dict) -> Dict:
        """Absolute Lock evaluation - kept for completeness."""
        return {
            'absolute_locked': False,
            'system_log': ["ABSOLUTE LOCK: Focus on agency-state markets"],
            'reason': "Focusing on agency-bound markets",
            'capital_authorized': False
        }

# =================== INTEGRATED BRUTBALL ARCHITECTURE ===================
class BrutballIntegratedArchitecture:
    """
    BRUTBALL INTEGRATED ARCHITECTURE
    v6.0 Edge Detection + Agency-State Lock Engine
    """
    
    @staticmethod
    def execute_agency_state_analysis(home_data: Dict, away_data: Dict,
                                     home_name: str, away_name: str,
                                     league_avg_xg: float) -> Dict:
        """Execute agency-state analysis."""
        
        # Run v6.0 Edge Detection Engine
        edge_result = BrutballEdgeEngine.execute_decision_tree(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Run Agency-State Lock Evaluation for all markets
        agency_state_result = AgencyStateLockEngine.evaluate_all_markets(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Determine capital mode
        if agency_state_result['locked_count'] > 0:
            capital_mode = 'LOCK_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['LOCK_MODE']
            capital_authorization = "AUTHORIZED (AGENCY-STATE LOCKED)"
            system_verdict = "AGENCY-STATE CONTROL DETECTED"
        else:
            capital_mode = 'EDGE_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['EDGE_MODE']
            capital_authorization = "STANDARD (v6.0 EDGE)"
            system_verdict = "STRUCTURAL EDGE DETECTED"
        
        # Create integrated system log
        system_log = []
        system_log.append("=" * 70)
        system_log.append("⚖️🔒 BRUTBALL AGENCY-STATE ARCHITECTURE")
        system_log.append("=" * 70)
        system_log.append(f"ARCHITECTURE: Unified Agency-State Framework")
        system_log.append(f"  • Tier 1: v6.0 Edge Detection Engine")
        system_log.append(f"  • Tier 2: Agency-State Lock Engine (Unified)")
        system_log.append("")
        
        system_log.append("🔍 v6.0 EDGE DETECTION RESULT")
        system_log.append(f"  • Action: {edge_result['primary_action']}")
        system_log.append(f"  • Confidence: {edge_result['confidence']:.1f}/10")
        system_log.append(f"  • Base Stake: {edge_result['stake_pct']:.1f}%")
        system_log.append("")
        
        system_log.append("🔐 AGENCY-STATE MARKET EVALUATION")
        system_log.append(f"  • Markets Evaluated: {agency_state_result['total_markets']}")
        system_log.append(f"  • Markets Locked: {agency_state_result['locked_count']}")
        
        if agency_state_result['locked_count'] > 0:
            system_log.append(f"  • Strongest Market: {agency_state_result['strongest_market']}")
            system_log.append(f"  • Controller: {agency_state_result['all_results'][agency_state_result['strongest_market']]['controller']}")
            system_log.append("  • Capital Authorization: GRANTED")
        else:
            system_log.append("  • No agency-state markets locked")
            system_log.append("  • Capital Authorization: STANDARD")
        system_log.append("")
        
        system_log.append("💰 INTEGRATED CAPITAL DECISION")
        system_log.append(f"  • Capital Mode: {capital_mode}")
        system_log.append(f"  • Stake Multiplier: {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x")
        system_log.append(f"  • Final Stake: {final_stake:.2f}%")
        system_log.append(f"  • Authorization: {capital_authorization}")
        system_log.append("")
        system_log.append(f"🎯 SYSTEM VERDICT: {system_verdict}")
        system_log.append("=" * 70)
        
        return {
            'architecture': 'Agency-State Framework',
            'v6_result': edge_result,
            'agency_state_result': agency_state_result,
            'capital_mode': capital_mode,
            'final_stake': final_stake,
            'system_verdict': system_verdict,
            'system_log': system_log,
            'integrated_output': {
                'primary_action': edge_result['primary_action'],
                'locked_markets': agency_state_result['locked_markets'],
                'strongest_market': agency_state_result['strongest_market'],
                'capital_authorized': capital_authorization,
                'stake_multiplier': CAPITAL_MULTIPLIERS[capital_mode],
                'final_stake_pct': final_stake,
                'edge_confidence': edge_result['confidence']
            }
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
    
    # Win rates (approximated from goals data)
    df['home_win_rate'] = df['home_goals_scored'] / (df['home_goals_scored'] + df['home_goals_conceded']).replace(0, np.nan)
    df['away_win_rate'] = df['away_goals_scored'] / (df['away_goals_scored'] + df['away_goals_conceded']).replace(0, np.nan)
    
    # Wins (approximated)
    df['home_wins'] = (df['home_goals_scored'] > df['home_goals_conceded']).astype(int) * df['home_matches_played']
    df['away_wins'] = (df['away_goals_scored'] > df['away_goals_conceded']).astype(int) * df['away_matches_played']
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="system-header">⚖️🔒 BRUTBALL AGENCY-STATE FRAMEWORK</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION</strong></p>
        <p>Unified logic for Winner • Clean Sheet • Team No Score • Opponent Under</p>
        <p>Same 4 Gates • Market-specific thresholds • No new heuristics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agency-State Principles
    st.markdown("""
    <div class="agency-principle">
        <h4>🧠 AGENCY-STATE CORE PRINCIPLES</h4>
        <div style="margin: 1rem 0;">
            <div class="state-bound-list">
                <strong>✅ STATE-BOUND MARKETS (Agency-Suppressible):</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li><strong>Winner</strong> - Opponent cannot change result</li>
                    <li><strong>Clean Sheet</strong> - Opponent cannot score</li>
                    <li><strong>Team to Score: NO</strong> - Team cannot act on goal</li>
                    <li><strong>Opponent Under X</strong> - Opponent agency limited</li>
                </ul>
            </div>
            <div class="noise-list">
                <strong>❌ NON-STATE MARKETS (Emergent Noise):</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>Totals (Over/Under) - Mutual agency required</li>
                    <li>Both Teams to Score - Both must act</li>
                    <li>Correct Score - Joint agency chaos</li>
                    <li>Draw - Requires mutual inability</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Architecture diagram
    st.markdown("""
    <div class="architecture-diagram">
        <h4>🏗️ AGENCY-STATE ARCHITECTURE</h4>
        <div class="three-tier-architecture">
            <div class="tier-level tier-2">
                <div style="font-size: 1.1rem; font-weight: 700;">AGENCY-STATE LOCK ENGINE</div>
                <div style="font-size: 0.9rem;">Unified logic for all state-bound markets</div>
                <div style="font-size: 0.85rem; color: #059669; margin-top: 0.5rem;">
                    Same 4 Gates • Market-specific thresholds
                </div>
                <span class="market-badge badge-state">Winner</span>
                <span class="market-badge badge-state">Clean Sheet</span>
                <span class="market-badge badge-state">Team No Score</span>
                <span class="market-badge badge-state">Opponent Under</span>
            </div>
            <div class="arrow-down">↓</div>
            <div class="tier-level tier-1">
                <div style="font-size: 1rem;">v6.0 EDGE DETECTION</div>
                <div style="font-size: 0.9rem;">Identifies structural controllers</div>
                <div style="font-size: 0.85rem; color: #3B82F6; margin-top: 0.5rem;">
                    Provides base stake and action
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System constants display
    with st.expander("🔧 MARKET-SPECIFIC THRESHOLDS", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**WINNER**")
            st.metric("Opponent xG", "< 1.1", "Standard")
            st.metric("Agency Collapse", "≥2/4", "Failures")
        with col2:
            st.markdown("**CLEAN SHEET**")
            st.metric("Opponent xG", "< 0.8", "Stricter")
            st.metric("Agency Collapse", "≥3/4", "More stringent")
        with col3:
            st.markdown("**TEAM NO SCORE**")
            st.metric("Opponent xG", "< 0.6", "Very strict")
            st.metric("Agency Collapse", "4/4", "All required")
        with col4:
            st.markdown("**OPPONENT UNDER 1.5**")
            st.metric("Opponent xG", "< 1.0", "Limited capacity")
            st.metric("Agency Collapse", "≥2/4", "Failures")
        
        st.markdown('<div class="law-display">', unsafe_allow_html=True)
        st.markdown("**🎯 UNIFIED LOGIC (Same 4 Gates)**")
        st.markdown("1. **GATE 1:** Quiet Control Identification")
        st.markdown("2. **GATE 2:** Directional Dominance (Δ > 0.25 + opponent xG < threshold)")
        st.markdown("3. **GATE 3:** Agency Collapse (opponent fails escalation checks)")
        st.markdown("4. **GATE 4:** Non-Urgent Enforcement (controller can protect without risk)")
        st.markdown('</div>', unsafe_allow_html=True)
    
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
    if st.button("⚡ EXECUTE AGENCY-STATE ANALYSIS", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute agency-state analysis
        result = BrutballIntegratedArchitecture.execute_agency_state_analysis(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 INTEGRATED SYSTEM VERDICT")
        
        # Capital mode display
        capital_mode = result['capital_mode']
        capital_display = "LOCK MODE" if capital_mode == 'LOCK_MODE' else "EDGE MODE"
        capital_class = "lock-mode" if capital_mode == 'LOCK_MODE' else "edge-mode"
        
        st.markdown(f"""
        <div class="capital-mode-box {capital_class}">
            <h2 style="margin: 0; font-size: 2rem;">{capital_display}</h2>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                Stake: <strong>{result['final_stake']:.2f}%</strong> ({result['v6_result']['stake_pct']:.1f}% × {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x)
            </div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem; color: {'#166534' if capital_mode == 'LOCK_MODE' else '#1E40AF'};">
                {result['system_verdict']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # v6.0 Edge Detection Display
        st.markdown("#### 🔍 v6.0 EDGE DETECTION RESULT")
        
        v6_result = result['v6_result']
        st.markdown(f"""
        <div class="edge-analysis-display">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: #1E40AF; margin: 0;">{v6_result['primary_action']}</h3>
                    <p style="color: #6B7280; margin: 0.5rem 0 0 0;">{v6_result['secondary_logic']}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #3B82F6;">{v6_result['confidence']:.1f}/10</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Confidence</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Agency-State Market Evaluation
        st.markdown("#### 🔐 AGENCY-STATE MARKET EVALUATION")
        
        agency_result = result['agency_state_result']
        
        if agency_result['locked_count'] > 0:
            st.markdown(f"""
            <div class="agency-state-display">
                <h3 style="color: #16A34A; margin: 0 0 1rem 0;">AGENCY-STATE CONTROL DETECTED</h3>
                <div style="font-size: 1.2rem; color: #059669; margin-bottom: 0.5rem;">
                    {agency_result['locked_count']} market(s) structurally locked
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Strongest market: <strong>{agency_result['strongest_market']}</strong>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
            """, unsafe_allow_html=True)
            
            for market in ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
                market_result = agency_result['all_results'][market]
                if market_result['state_locked']:
                    st.markdown(f'<span class="market-badge badge-locked">{market}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="market-badge badge-state">{market}</span>', unsafe_allow_html=True)
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual Market Details
            st.markdown("##### 📊 MARKET-SPECIFIC DETAILS")
            
            for market in ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
                market_result = agency_result['all_results'][market]
                
                if market_result['state_locked']:
                    st.markdown(f"""
                    <div class="market-locked-display">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="color: #059669; margin: 0 0 0.5rem 0;">🔒 {market}</h4>
                                <div style="color: #374151; font-size: 0.9rem;">
                                    Controller: <strong>{market_result['controller']}</strong><br>
                                    Δ: <strong>{market_result['control_delta']:+.2f}</strong> | Agency Failures: <strong>{market_result['agency_failures']}/4</strong>
                                </div>
                            </div>
                            <span class="market-badge badge-locked">LOCKED</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="market-available-display">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="color: #3B82F6; margin: 0 0 0.5rem 0;">{market}</h4>
                                <div style="color: #6B7280; font-size: 0.9rem;">
                                    {market_result['reason']}
                                </div>
                            </div>
                            <span class="market-badge badge-state">AVAILABLE</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Capital authorization
            st.markdown("""
            <div class="gate-passed">
                <h3 style="margin: 0; color: #166534;">💰 CAPITAL AUTHORIZATION: GRANTED</h3>
                <p style="margin: 0.5rem 0 0 0; color: #374151;">
                    Agency-state control detected • 2.0x stake multiplier • Focus on strongest market
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="no-declaration-display">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO AGENCY-STATE CONTROL</h3>
                <div style="color: #374151;">
                    No markets meet agency-suppression criteria
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="gate-failed">
                <h3 style="margin: 0; color: #DC2626;">🔒 CAPITAL AUTHORIZATION: STANDARD</h3>
                <p style="margin: 0.5rem 0 0 0; color: #374151;">
                    v6.0 edge preserved • 1.0x stake multiplier • No agency-state locks
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key metrics
        st.markdown("#### 📊 KEY METRICS")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
            st.markdown("**v6.0 Edge Detection**")
            
            v6_metrics = v6_result['key_metrics']
            st.markdown(f"""
            <div class="metric-row metric-row-state">
                <span>Primary Action:</span>
                <span><strong>{v6_result['primary_action']}</strong></span>
            </div>
            <div class="metric-row">
                <span>Confidence:</span>
                <span><strong>{v6_result['confidence']:.1f}/10</strong></span>
            </div>
            <div class="metric-row">
                <span>Base Stake:</span>
                <span><strong>{v6_result['stake_pct']:.1f}%</strong></span>
            </div>
            <div class="metric-row">
                <span>Controller:</span>
                <span><strong>{v6_metrics['controller'] if v6_metrics['controller'] else 'None'}</strong></span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
            st.markdown("**Agency-State Analysis**")
            
            st.markdown(f"""
            <div class="metric-row metric-row-agency">
                <span>Markets Evaluated:</span>
                <span><strong>{agency_result['total_markets']}</strong></span>
            </div>
            <div class="metric-row">
                <span>Markets Locked:</span>
                <span><strong>{agency_result['locked_count']}</strong></span>
            </div>
            """, unsafe_allow_html=True)
            
            if agency_result['locked_count'] > 0:
                st.markdown(f"""
                <div class="metric-row">
                    <span>Strongest Market:</span>
                    <span><strong>{agency_result['strongest_market']}</strong></span>
                </div>
                <div class="metric-row">
                    <span>Strongest Δ:</span>
                    <span><strong>{agency_result['strongest_delta']:+.2f}</strong></span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Agency Insight
        st.markdown("#### 🧠 AGENCY INSIGHT")
        
        st.markdown("""
        <div class="agency-insight">
            <h4 style="color: #0C4A6E; margin: 0 0 1rem 0;">STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION</h4>
            <p style="color: #374151; margin: 0;">
                Markets are locked when one team's agency to affect the outcome is structurally suppressed. 
                This occurs through the same 4 gates across all state-bound markets, with only threshold adjustments.
            </p>
            <div style="margin-top: 1rem; padding: 1rem; background: #F0F9FF; border-radius: 6px;">
                <strong>Why totals/BTTS cannot be locked:</strong> They require mutual agency - both teams must act. 
                No single team can suppress the joint agency required for these outcomes.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System log
        with st.expander("📋 VIEW INTEGRATED SYSTEM LOG", expanded=True):
            st.markdown('<div class="system-log">', unsafe_allow_html=True)
            for line in result['system_log']:
                st.text(line)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export Agency-State Analysis")
        
        export_text = f"""BRUTBALL AGENCY-STATE FRAMEWORK ANALYSIS
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

ARCHITECTURE SUMMARY:
• Framework: Unified Agency-State Logic
• Core Principle: STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION
• State-Bound Markets: Winner • Clean Sheet • Team No Score • Opponent Under
• Non-State Markets: Totals • BTTS • Correct Score • Draw
• Capital Mode: {capital_display}

v6.0 EDGE DETECTION RESULT:
• Primary Action: {v6_result['primary_action']}
• Confidence: {v6_result['confidence']:.1f}/10
• Base Stake: {v6_result['stake_pct']:.1f}%
• Secondary Logic: {v6_result['secondary_logic']}

AGENCY-STATE MARKET EVALUATION:
• Markets Evaluated: {agency_result['total_markets']}
• Markets Locked: {agency_result['locked_count']}
• Strongest Market: {agency_result['strongest_market'] if agency_result['locked_count'] > 0 else 'None'}

MARKET-SPECIFIC RESULTS:"""
        
        for market in ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
            market_result = agency_result['all_results'][market]
            export_text += f"""
{market}:
  • State Locked: {'YES' if market_result['state_locked'] else 'NO'}
  {'  • Controller: ' + market_result['controller'] if market_result['state_locked'] else ''}
  {'  • Control Delta: ' + f"{market_result.get('control_delta', 0):+.2f}" if market_result['state_locked'] else ''}
  {'  • Agency Failures: ' + f"{market_result.get('agency_failures', 0)}/4" if market_result['state_locked'] else ''}
  {'  • Reason: ' + market_result['reason'] if not market_result['state_locked'] else ''}"""
        
        export_text += f"""

INTEGRATED CAPITAL DECISION:
• Final Capital Mode: {capital_display}
• Stake Multiplier: {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x
• Base Stake: {v6_result['stake_pct']:.1f}%
• Final Stake: {result['final_stake']:.2f}%
• Authorization: {result['integrated_output']['capital_authorized']}
• System Verdict: {result['system_verdict']}

AGENCY-STATE INSIGHTS:
• State-bound markets can be locked when opponent's agency is suppressed
• Non-state markets require mutual agency and cannot be structurally locked
• Same 4 gates apply to all state-bound markets with threshold adjustments
• Time decay protects agency-bound outcomes but not mutual agency outcomes

INTEGRATED SYSTEM LOG:
{chr(10).join(result['system_log'])}

===========================================
BRUTBALL AGENCY-STATE FRAMEWORK
STATE = AGENCY CONTROL
LOCK = AGENCY SUPPRESSION
Unified logic for all state-bound markets
        """
        
        st.download_button(
            label="📥 Download Agency-State Analysis",
            data=export_text,
            file_name=f"brutball_agency_state_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL AGENCY-STATE FRAMEWORK</strong></p>
        <p>STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION</p>
        <p>Unified logic for Winner • Clean Sheet • Team No Score • Opponent Under markets</p>
        <p>Same 4 gates, market-specific thresholds, no new heuristics</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
