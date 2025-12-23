import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== SYSTEM CONSTANTS (IMMUTABLE) ===================
# v6.1.1 State Lock Authority Engine Constants
DIRECTION_THRESHOLD = 0.25  # LAW 2: Direction is mandatory
ENFORCEMENT_METHODS_REQUIRED = 2  # LAW 3: Enforcement must be redundant
CONTROL_CRITERIA_REQUIRED = 2  # GATE 1: Minimum for Quiet Control
STATE_FLIP_FAILURES_REQUIRED = 2  # GATE 3: Opponent fails ≥2 escalation paths
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1  # v6.1.2: Mutual control check

# v6.0 Edge Detection Engine Constants
CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,  # Base stake for v6.0-only decisions
    'LOCK_MODE': 2.0   # Stake multiplier for STATE LOCKED authorization
}

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1.2 - Two Engine Architecture",
    page_icon="⚖️",
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
    .state-locked-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 4px solid #16A34A;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(22, 163, 74, 0.15);
    }
    .no-declaration-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border: 4px solid #6B7280;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .edge-analysis-display {
        padding: 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
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
    .law-display {
        background: #EFF6FF;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #3B82F6;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .law-violation {
        background: #FEF3C7;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #F59E0B;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .capital-authorized {
        background: #1E3A8A;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 3px solid #3B82F6;
    }
    .no-capital {
        background: #6B7280;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 3px solid #9CA3AF;
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
    .status-danger {
        background: #FEE2E2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
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
    .metric-row-edge {
        background: #EFF6FF;
        border-left: 3px solid #3B82F6;
    }
    .gate-sequence {
        counter-reset: gate-counter;
        margin: 1rem 0;
    }
    .gate-step {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        position: relative;
        counter-increment: gate-counter;
    }
    .gate-step::before {
        content: "GATE " counter(gate-counter) ": ";
        font-weight: 800;
        color: #3B82F6;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    .system-log {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        background: #1F2937;
        color: #E5E7EB;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        white-space: pre-wrap;
    }
    .architecture-diagram {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        text-align: center;
    }
    .engine-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        margin: 0.5rem;
    }
    .engine-v6 {
        background: #DBEAFE;
        color: #1E40AF;
        border: 2px solid #3B82F6;
    }
    .engine-v61 {
        background: #DCFCE7;
        color: #166534;
        border: 2px solid #16A34A;
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

# =================== v6.1.1 STATE LOCK AUTHORITY ENGINE ===================
class BrutballStateLockEngine:
    """
    BRUTBALL v6.1.1 - STATE LOCK AUTHORITY ENGINE
    Governance layer: detects structural inevitability
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
                                   controller_name: str, opponent_name: str) -> Tuple[bool, float, List[str]]:
        """GATE 2: Check directional dominance (LAW 2)."""
        rationale = []
        control_delta = controller_xg - opponent_xg
        
        rationale.append(f"GATE 2: DIRECTIONAL DOMINANCE CHECK")
        rationale.append(f"• Controller xG ({controller_name}): {controller_xg:.2f}")
        rationale.append(f"• Opponent xG ({opponent_name}): {opponent_xg:.2f}")
        rationale.append(f"• Control Delta: {control_delta:+.2f}")
        rationale.append(f"• Required Threshold: > {DIRECTION_THRESHOLD}")
        
        if control_delta > DIRECTION_THRESHOLD:
            rationale.append(f"✅ Directional dominance confirmed (Δ = {control_delta:+.2f} > {DIRECTION_THRESHOLD})")
            return True, control_delta, rationale
        else:
            rationale.append(f"❌ LAW 2 VIOLATION: Insufficient directional dominance (Δ = {control_delta:+.2f} ≤ {DIRECTION_THRESHOLD})")
            rationale.append("• No pressure gradient → NO DECLARATION")
            return False, control_delta, rationale
    
    @staticmethod
    def check_state_flip_capacity(opponent_data: Dict, is_home: bool,
                                 opponent_name: str, league_avg_xg: float) -> Tuple[int, List[str]]:
        """GATE 3: Check state-flip capacity."""
        rationale = []
        failures = 0
        check_details = []
        
        rationale.append(f"GATE 3: STATE-FLIP CAPACITY CHECK")
        
        # CHECK 1: Chase xG < 1.1
        if is_home:
            chase_xg = opponent_data.get('home_xg_per_match', 0)
        else:
            chase_xg = opponent_data.get('away_xg_per_match', 0)
        
        if chase_xg < 1.1:
            failures += 1
            check_details.append(f"❌ Chase xG {chase_xg:.2f} < 1.1")
        else:
            check_details.append(f"✅ Chase xG {chase_xg:.2f} ≥ 1.1")
        
        # CHECK 2: No tempo surge capability
        if chase_xg < 1.4:
            failures += 1
            check_details.append(f"❌ No tempo surge (xG {chase_xg:.2f} < 1.4)")
        else:
            check_details.append(f"✅ Tempo surge possible")
        
        # CHECK 3: No alternate threat channel
        if is_home:
            setpiece_pct = opponent_data.get('home_setpiece_pct', 0)
            counter_pct = opponent_data.get('home_counter_pct', 0)
        else:
            setpiece_pct = opponent_data.get('away_setpiece_pct', 0)
            counter_pct = opponent_data.get('away_counter_pct', 0)
        
        if setpiece_pct < 0.25 and counter_pct < 0.15:
            failures += 1
            check_details.append(f"❌ No alternate threat (SP: {setpiece_pct:.1%}, C: {counter_pct:.1%})")
        else:
            check_details.append(f"✅ Alternate threat exists")
        
        # CHECK 4: Low substitution leverage
        if is_home:
            gpm = opponent_data.get('home_goals_per_match', 0)
        else:
            gpm = opponent_data.get('away_goals_per_match', 0)
        
        if gpm < league_avg_xg * 0.8:
            failures += 1
            check_details.append(f"❌ Low substitution leverage ({gpm:.2f} < {league_avg_xg*0.8:.2f})")
        else:
            check_details.append(f"✅ Adequate bench impact")
        
        # Add all check details
        for detail in check_details:
            rationale.append(f"  • {detail}")
        
        # Summary
        if failures >= STATE_FLIP_FAILURES_REQUIRED:
            rationale.append(f"✅ State-flip capacity absent ({failures}/4 checks failed)")
        else:
            rationale.append(f"❌ State-flip capacity retained ({failures}/4 checks failed)")
            rationale.append(f"• Requires ≥{STATE_FLIP_FAILURES_REQUIRED} failures")
        
        return failures, rationale
    
    @staticmethod
    def check_enforcement_capacity(controller_data: Dict, is_home: bool,
                                  controller_name: str) -> Tuple[int, List[str]]:
        """GATE 4: Check enforcement without urgency (LAW 3)."""
        rationale = []
        enforce_methods = 0
        method_details = []
        
        rationale.append(f"GATE 4: ENFORCEMENT CAPACITY CHECK")
        
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
        
        # Add all method details
        for detail in method_details:
            rationale.append(f"  • {detail}")
        
        # Check LAW 3 compliance
        if enforce_methods >= ENFORCEMENT_METHODS_REQUIRED:
            rationale.append(f"✅ LAW 3 SATISFIED: Redundant enforcement ({enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED}+ methods)")
        else:
            rationale.append(f"❌ LAW 3 VIOLATION: Insufficient enforcement ({enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} methods)")
            rationale.append(f"• Requires ≥{ENFORCEMENT_METHODS_REQUIRED} independent methods")
        
        return enforce_methods, rationale
    
    @classmethod
    def execute_state_lock_evaluation(cls, home_data: Dict, away_data: Dict,
                                     home_name: str, away_name: str,
                                     league_avg_xg: float) -> Dict:
        """Execute STATE LOCK evaluation."""
        system_log = []
        gates_passed = 0
        total_gates = 4
        
        system_log.append("=" * 70)
        system_log.append("🔐 BRUTBALL v6.1.1 - STATE LOCK AUTHORITY ENGINE")
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
        controller_criteria = []
        
        # v6.1.2: Check for mutual control
        both_meet_control = (home_score >= CONTROL_CRITERIA_REQUIRED and 
                            away_score >= CONTROL_CRITERIA_REQUIRED)
        
        if both_meet_control:
            weighted_diff = abs(home_weighted - away_weighted)
            
            if weighted_diff <= QUIET_CONTROL_SEPARATION_THRESHOLD:
                system_log.append(f"⚠️ v6.1.2: Mutual control detected")
                system_log.append(f"  • Weighted difference: {weighted_diff:.2f} ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD}")
                system_log.append("• NO SINGLE CONTROLLER → NO DECLARATION")
                system_log.append("⚠️ SYSTEM SILENT")
                
                return {
                    'declaration': None,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': f"v6.1.2: Mutual control (weighted difference ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD})",
                    'capital_authorized': False,
                    'mutual_control': True
                }
            
            if home_weighted > away_weighted:
                controller = home_name
                controller_criteria = home_criteria
                system_log.append(f"• Controller: {home_name} (weighted advantage)")
            else:
                controller = away_name
                controller_criteria = away_criteria
                system_log.append(f"• Controller: {away_name} (weighted advantage)")
        
        elif home_score >= CONTROL_CRITERIA_REQUIRED and home_score > away_score:
            controller = home_name
            controller_criteria = home_criteria
            system_log.append(f"• Controller: {home_name} ({home_score}/4 criteria)")
            
        elif away_score >= CONTROL_CRITERIA_REQUIRED and away_score > home_score:
            controller = away_name
            controller_criteria = away_criteria
            system_log.append(f"• Controller: {away_name} ({away_score}/4 criteria)")
        
        else:
            system_log.append("❌ GATE 1 FAILED: No Quiet Control identified")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"No team meets {CONTROL_CRITERIA_REQUIRED}+ control criteria",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 1 PASSED: Quiet Control → {controller}")
        
        # =================== GATE 2: DIRECTIONAL DOMINANCE ===================
        system_log.append("")
        system_log.append("GATE 2: DIRECTIONAL DOMINANCE (LAW 2)")
        
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        controller_xg = home_data.get('home_xg_per_match', 0) if is_controller_home else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if is_controller_home else home_data.get('home_xg_per_match', 0)
        
        has_direction, control_delta, direction_rationale = cls.check_directional_dominance(
            controller_xg, opponent_xg, controller, opponent
        )
        system_log.extend(direction_rationale)
        
        if not has_direction:
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"LAW 2 VIOLATION: Insufficient directional dominance (Δ = {control_delta:+.2f} ≤ {DIRECTION_THRESHOLD})",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 2 PASSED: Directional dominance confirmed (Δ = {control_delta:+.2f})")
        
        # =================== GATE 3: STATE-FLIP CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 3: STATE-FLIP CAPACITY")
        
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        failures, flip_rationale = cls.check_state_flip_capacity(
            opponent_data, is_opponent_home, opponent, league_avg_xg
        )
        system_log.extend(flip_rationale)
        
        if failures < STATE_FLIP_FAILURES_REQUIRED:
            system_log.append("❌ GATE 3 FAILED: Opponent retains escalation paths")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Opponent retains state-flip capacity ({failures}/{STATE_FLIP_FAILURES_REQUIRED} failures)",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 3 PASSED: State-flip capacity absent ({failures}/4 failures)")
        
        # =================== GATE 4: ENFORCEMENT CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 4: ENFORCEMENT WITHOUT URGENCY (LAW 3)")
        
        controller_data = home_data if controller == home_name else away_data
        
        enforce_methods, enforce_rationale = cls.check_enforcement_capacity(
            controller_data, is_controller_home, controller
        )
        system_log.extend(enforce_rationale)
        
        if enforce_methods < ENFORCEMENT_METHODS_REQUIRED:
            system_log.append("❌ GATE 4 FAILED: Insufficient enforcement capacity")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"LAW 3 VIOLATION: Insufficient enforcement capacity ({enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} methods)",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4 PASSED: Redundant enforcement confirmed ({enforce_methods}/2+ methods)")
        
        # =================== STATE LOCK DECLARATION ===================
        system_log.append("")
        system_log.append("=" * 70)
        system_log.append("🔒 STATE LOCK DECLARATION")
        system_log.append("=" * 70)
        
        if opponent_xg < 1.1:
            declaration = f"🔒 STATE LOCKED\n{opponent} lacks chase capacity\n{controller} can win at walking pace"
        elif control_delta > 0.5:
            declaration = f"🔒 STATE LOCKED\nStructural dominance established\n{controller} never forced into urgency"
        elif failures >= 3:
            declaration = f"🔒 STATE LOCKED\n{opponent} has no credible escalation\n{controller} controls all restart leverage"
        else:
            declaration = f"🔒 STATE LOCKED\n{opponent} cannot disrupt state structure\n{controller} maintains coercive tempo"
        
        system_log.append(declaration)
        system_log.append("")
        system_log.append("💰 CAPITAL AUTHORIZATION: GRANTED")
        system_log.append(f"• All {total_gates}/{total_gates} gates passed")
        system_log.append(f"• Control Delta: {control_delta:+.2f} > {DIRECTION_THRESHOLD}")
        system_log.append(f"• State-Flip Failures: {failures}/4")
        system_log.append(f"• Enforcement Methods: {enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED}+")
        system_log.append("• Match outcome structurally constrained")
        system_log.append("=" * 70)
        
        return {
            'declaration': declaration,
            'state_locked': True,
            'system_log': system_log,
            'reason': "All canonical gates passed. State structurally locked.",
            'capital_authorized': True,
            'controller': controller,
            'control_delta': control_delta,
            'state_flip_failures': failures,
            'enforce_methods': enforce_methods,
            'key_metrics': {
                'controller_xg': controller_xg,
                'opponent_xg': opponent_xg
            }
        }

# =================== INTEGRATED BRUTBALL ARCHITECTURE ===================
class BrutballIntegratedArchitecture:
    """
    BRUTBALL INTEGRATED ARCHITECTURE
    Two-engine system: v6.0 (Edge Detection) + v6.1.1 (State Lock Authority)
    """
    
    @staticmethod
    def execute_two_engine_analysis(home_data: Dict, away_data: Dict,
                                   home_name: str, away_name: str,
                                   league_avg_xg: float) -> Dict:
        """Execute both engines and combine results."""
        
        # Run v6.0 Edge Detection Engine
        edge_result = BrutballEdgeEngine.execute_decision_tree(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Run v6.1.1 State Lock Authority Engine
        state_lock_result = BrutballStateLockEngine.execute_state_lock_evaluation(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Determine capital mode and final stake
        if state_lock_result['state_locked']:
            capital_mode = 'LOCK_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['LOCK_MODE']
            capital_authorization = "AUTHORIZED (STATE LOCKED)"
            system_verdict = "STRUCTURAL INEVITABILITY DETECTED"
        else:
            capital_mode = 'EDGE_MODE'
            final_stake = edge_result['stake_pct'] * CAPITAL_MULTIPLIERS['EDGE_MODE']
            capital_authorization = "STANDARD (v6.0 EDGE)"
            system_verdict = "STRUCTURAL EDGE DETECTED"
        
        # Create integrated system log
        system_log = []
        system_log.append("=" * 70)
        system_log.append("⚖️ BRUTBALL INTEGRATED ARCHITECTURE")
        system_log.append("=" * 70)
        system_log.append(f"ARCHITECTURE: Two-Engine System")
        system_log.append(f"  • Layer 1: v6.0 Edge Detection Engine")
        system_log.append(f"  • Layer 2: v6.1.1 State Lock Authority Engine")
        system_log.append("")
        
        system_log.append("🔍 v6.0 EDGE DETECTION RESULT")
        system_log.append(f"  • Action: {edge_result['primary_action']}")
        system_log.append(f"  • Confidence: {edge_result['confidence']:.1f}/10")
        system_log.append(f"  • Base Stake: {edge_result['stake_pct']:.1f}%")
        system_log.append("")
        
        system_log.append("🔐 v6.1.1 STATE LOCK EVALUATION")
        if state_lock_result['state_locked']:
            system_log.append("  • Result: STATE LOCKED")
            system_log.append(f"  • Declaration: {state_lock_result['declaration']}")
            system_log.append("  • Capital Authorization: GRANTED")
        else:
            system_log.append("  • Result: NO DECLARATION")
            system_log.append(f"  • Reason: {state_lock_result['reason']}")
            system_log.append("  • Capital Authorization: STANDARD (v6.0 edge preserved)")
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
            'architecture': 'Two-Engine System',
            'v6_result': edge_result,
            'v61_result': state_lock_result,
            'capital_mode': capital_mode,
            'final_stake': final_stake,
            'system_verdict': system_verdict,
            'system_log': system_log,
            'integrated_output': {
                'primary_action': edge_result['primary_action'],
                'state_locked': state_lock_result['state_locked'],
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
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="system-header">⚖️ BRUTBALL v6.1.2 - TWO ENGINE ARCHITECTURE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>Layer 1: v6.0 Edge Detection • Layer 2: v6.1.1 State Lock Authority • Integrated Capital Logic</strong></p>
        <p>EDGE MODE (v6.0 only) vs LOCK MODE (v6.0 + v6.1.1 STATE LOCKED)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Architecture diagram
    st.markdown("""
    <div class="architecture-diagram">
        <h4>🏗️ SYSTEM ARCHITECTURE</h4>
        <div style="margin: 1rem 0;">
            <span class="engine-indicator engine-v61">v6.1.1 STATE LOCK AUTHORITY</span>
            <div style="margin: 0.5rem; font-size: 1.5rem;">↑</div>
            <div style="font-size: 0.9rem; color: #6B7280;">Governance Layer<br>Permission-granting only</div>
        </div>
        <div style="margin: 1rem 0;">
            <span class="engine-indicator engine-v6">v6.0 EDGE DETECTION</span>
            <div style="margin: 0.5rem; font-size: 0.9rem; color: #6B7280;">Heuristic Layer<br>Continuous operation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System constants display
    with st.expander("🔧 SYSTEM CONFIGURATION", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Edge Mode Multiplier", f"{CAPITAL_MULTIPLIERS['EDGE_MODE']}x", "v6.0 only")
        with col2:
            st.metric("Lock Mode Multiplier", f"{CAPITAL_MULTIPLIERS['LOCK_MODE']}x", "STATE LOCKED")
        with col3:
            st.metric("Direction Threshold", f"> {DIRECTION_THRESHOLD}", "LAW 2")
        with col4:
            st.metric("Enforcement Methods", f"≥ {ENFORCEMENT_METHODS_REQUIRED}", "LAW 3")
        
        st.markdown('<div class="law-display">', unsafe_allow_html=True)
        st.markdown("**🎯 OPERATIONAL MODES**")
        st.markdown("1. **EDGE MODE:** v6.0 edge detection only • Normal variance • 1.0x stake")
        st.markdown("2. **LOCK MODE:** v6.0 + v6.1.1 STATE LOCKED • Structural inevitability • 2.0x stake")
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
    if st.button("⚡ EXECUTE TWO-ENGINE ANALYSIS", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute integrated architecture
        result = BrutballIntegratedArchitecture.execute_two_engine_analysis(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 INTEGRATED SYSTEM VERDICT")
        
        # Capital mode display
        capital_mode = result['capital_mode']
        capital_display = "LOCK MODE" if capital_mode == 'LOCK_MODE' else "EDGE MODE"
        capital_color = "#16A34A" if capital_mode == 'LOCK_MODE' else "#3B82F6"
        capital_bg = "linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)" if capital_mode == 'LOCK_MODE' else "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)"
        
        st.markdown(f"""
        <div class="capital-mode-box {'lock-mode' if capital_mode == 'LOCK_MODE' else 'edge-mode'}">
            <h2 style="margin: 0; font-size: 2rem;">{capital_display}</h2>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                Stake: <strong>{result['final_stake']:.2f}%</strong> ({result['v6_result']['stake_pct']:.1f}% × {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x)
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
        
        # v6.1.1 State Lock Display
        st.markdown("#### 🔐 v6.1.1 STATE LOCK EVALUATION")
        
        v61_result = result['v61_result']
        
        if v61_result['state_locked']:
            st.markdown(f"""
            <div class="state-locked-display">
                <h3 style="color: #16A34A; margin: 0 0 1rem 0;">STATE LOCKED</h3>
                <div style="font-size: 1.2rem; color: #059669; margin-bottom: 0.5rem;">
                    {v61_result['declaration'].split('\\n')[1] if '\\n' in v61_result['declaration'] else ''}
                </div>
                <div style="color: #374151;">
                    {v61_result['declaration'].split('\\n')[2] if len(v61_result['declaration'].split('\\n')) > 2 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="capital-authorized">
                <h3 style="margin: 0; color: white;">💰 CAPITAL AUTHORIZATION: GRANTED</h3>
                <p style="margin: 0.5rem 0 0 0; color: #D1FAE5; font-size: 0.95rem;">
                    Structural inevitability detected • LOCK MODE activated • 2.0x stake multiplier
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gate sequence
            st.markdown("##### 🚪 STATE LOCK GATE SEQUENCE")
            gates = [
                f"GATE 1: Quiet Control → {v61_result['controller']}",
                f"GATE 2: Directional Dominance → Δ = {v61_result['control_delta']:+.2f}",
                f"GATE 3: State-Flip Capacity → {v61_result['state_flip_failures']}/4 failures",
                f"GATE 4: Enforcement Capacity → {v61_result['enforce_methods']}/2+ methods"
            ]
            
            for gate in gates:
                st.markdown(f'<div class="gate-passed">{gate}</div>', unsafe_allow_html=True)
                
        else:
            st.markdown(f"""
            <div class="no-declaration-display">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO DECLARATION</h3>
                <div style="color: #374151;">
                    {v61_result['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="no-capital">
                <h3 style="margin: 0; color: white;">🔒 CAPITAL AUTHORIZATION: STANDARD</h3>
                <p style="margin: 0.5rem 0 0 0; color: #E5E7EB; font-size: 0.95rem;">
                    v6.0 edge preserved • EDGE MODE active • 1.0x stake multiplier
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if v61_result.get('mutual_control'):
                st.markdown("""
                <div class="mutual-control-alert">
                    <h4 style="color: #D97706; margin: 0;">v6.1.2 REFINEMENT: MUTUAL CONTROL DETECTED</h4>
                    <p style="color: #92400E; margin: 0.5rem 0;">
                        Both teams meet Quiet Control criteria with insufficient separation
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
            <div class="metric-row metric-row-edge">
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
            st.markdown("**v6.1.1 State Lock**")
            
            if v61_result['state_locked']:
                st.markdown(f"""
                <div class="metric-row metric-row-controller">
                    <span>Controller:</span>
                    <span><strong>{v61_result['controller']}</strong></span>
                </div>
                <div class="metric-row">
                    <span>Control Delta:</span>
                    <span><strong>{v61_result['control_delta']:+.2f}</strong></span>
                </div>
                <div class="metric-row">
                    <span>State-Flip Failures:</span>
                    <span><strong>{v61_result['state_flip_failures']}/4</strong></span>
                </div>
                <div class="metric-row">
                    <span>Enforcement Methods:</span>
                    <span><strong>{v61_result['enforce_methods']}/2+</strong></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-row">
                    <span>Result:</span>
                    <span><strong>NO DECLARATION</strong></span>
                </div>
                <div class="metric-row">
                    <span>Reason:</span>
                    <span style="color: #DC2626;"><strong>{v61_result['reason'].split(':')[-1].strip()}</strong></span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # System log
        with st.expander("📋 VIEW INTEGRATED SYSTEM LOG", expanded=True):
            st.markdown('<div class="system-log">', unsafe_allow_html=True)
            for line in result['system_log']:
                st.text(line)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export Integrated Analysis")
        
        export_text = f"""BRUTBALL v6.1.2 - TWO ENGINE ARCHITECTURE ANALYSIS
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

ARCHITECTURE SUMMARY:
• System: Two-Engine Architecture
• Layer 1: v6.0 Edge Detection Engine
• Layer 2: v6.1.1 State Lock Authority Engine
• Capital Mode: {capital_display}

v6.0 EDGE DETECTION RESULT:
• Primary Action: {v6_result['primary_action']}
• Confidence: {v6_result['confidence']:.1f}/10
• Base Stake: {v6_result['stake_pct']:.1f}%
• Secondary Logic: {v6_result['secondary_logic']}

v6.1.1 STATE LOCK EVALUATION:
• Result: {'STATE LOCKED' if v61_result['state_locked'] else 'NO DECLARATION'}
{'• Declaration: ' + v61_result['declaration'] if v61_result['state_locked'] else '• Reason: ' + v61_result['reason']}
• Capital Authorization: {'GRANTED (LOCK MODE)' if v61_result['state_locked'] else 'STANDARD (EDGE MODE)'}

INTEGRATED CAPITAL DECISION:
• Final Capital Mode: {capital_display}
• Stake Multiplier: {CAPITAL_MULTIPLIERS[capital_mode]:.1f}x
• Final Stake: {result['final_stake']:.2f}%
• System Verdict: {result['system_verdict']}

KEY METRICS:
v6.0:
  • Controller: {v6_metrics.get('controller', 'None')}
  • Favorite: {v6_metrics.get('favorite', 'N/A')}
  • Underdog: {v6_metrics.get('underdog', 'N/A')}
  • Home xG: {v6_metrics.get('home_xg', 0):.2f}
  • Away xG: {v6_metrics.get('away_xg', 0):.2f}
  • Combined xG: {v6_metrics.get('combined_xg', 0):.2f}

{'v6.1.1:' if v61_result['state_locked'] else ''}
{'  • Controller: ' + v61_result['controller'] if v61_result['state_locked'] else ''}
{'  • Control Delta: ' + f"{v61_result['control_delta']:+.2f}" if v61_result['state_locked'] else ''}
{'  • State-Flip Failures: ' + f"{v61_result['state_flip_failures']}/4" if v61_result['state_locked'] else ''}
{'  • Enforcement Methods: ' + f"{v61_result['enforce_methods']}/2+" if v61_result['state_locked'] else ''}

INTEGRATED SYSTEM LOG:
{chr(10).join(result['system_log'])}

===========================================
BRUTBALL v6.1.2 - Two Engine Architecture
Layer 1: v6.0 Edge Detection (heuristic)
Layer 2: v6.1.1 State Lock Authority (governance)
Capital flows differently based on structural certainty
        """
        
        st.download_button(
            label="📥 Download Integrated Analysis",
            data=export_text,
            file_name=f"brutball_v6.1.2_integrated_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL v6.1.2 – Two Engine Architecture</strong></p>
        <p>Layer 1: v6.0 Edge Detection Engine • Layer 2: v6.1.1 State Lock Authority Engine</p>
        <p>EDGE MODE (normal variance) • LOCK MODE (structural inevitability)</p>
        <p>Governance layer sits above, never replaces, heuristic layer</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
