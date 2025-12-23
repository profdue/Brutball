import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== SYSTEM CONSTANTS (IMMUTABLE) ===================
DIRECTION_THRESHOLD = 0.25  # LAW 2: Direction is mandatory
ENFORCEMENT_METHODS_REQUIRED = 2  # LAW 3: Enforcement must be redundant
CONTROL_CRITERIA_REQUIRED = 2  # GATE 1: Minimum for Quiet Control
STATE_FLIP_FAILURES_REQUIRED = 2  # GATE 3: Opponent fails ≥2 escalation paths

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1.1 - Canonical State Lock",
    page_icon="🔒",
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
    </style>
""", unsafe_allow_html=True)

# =================== BRUTBALL v6.1.1 - CANONICAL STATE LOCK ENGINE ===================
class BrutballCanonicalEngine:
    """
    BRUTBALL v6.1.1 - CANONICAL STATE LOCK ENGINE
    Logically complete. No status resolution. Direction mandatory.
    """
    
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, opponent_data: Dict,
                              is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """
        GATE 1: Evaluate Quiet Control.
        Returns: (raw_score, weighted_score, criteria_met, rationale)
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
        """
        GATE 2: Check directional dominance (LAW 2).
        Control Delta must exceed DIRECTION_THRESHOLD.
        """
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
        """
        GATE 3: Check state-flip capacity.
        Opponent must fail ≥2 of 4 escalation checks.
        """
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
        """
        GATE 4: Check enforcement without urgency (LAW 3).
        Must have ≥2 independent enforcement methods.
        """
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
    def execute_canonical_gates(cls, home_data: Dict, away_data: Dict,
                               home_name: str, away_name: str,
                               league_avg_xg: float) -> Dict:
        """
        Execute canonical gate sequence. No status resolution. Direction mandatory.
        Returns STATE LOCKED declaration or NO DECLARATION.
        """
        system_log = []
        gates_passed = 0
        total_gates = 4
        
        system_log.append("=" * 70)
        system_log.append("🔐 BRUTBALL v6.1.1 - CANONICAL STATE LOCK")
        system_log.append("=" * 70)
        system_log.append(f"MATCH: {home_name} vs {away_name}")
        system_log.append(f"SYSTEM TIME: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        system_log.append("")
        
        # =================== GATE 1: QUIET CONTROL ===================
        system_log.append("GATE 1: QUIET CONTROL IDENTIFICATION")
        
        # Evaluate both teams
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
        tie_breaker_applied = False
        used_status_resolution = False
        
        if home_score >= CONTROL_CRITERIA_REQUIRED and away_score >= CONTROL_CRITERIA_REQUIRED:
            # Both teams meet minimum criteria - check for clear winner
            if home_weighted > away_weighted + 0.1:  # Clear weighted advantage
                controller = home_name
                controller_criteria = home_criteria
                system_log.append(f"• Controller: {home_name} (weighted advantage: {home_weighted:.2f} > {away_weighted:.2f})")
            elif away_weighted > home_weighted + 0.1:
                controller = away_name
                controller_criteria = away_criteria
                system_log.append(f"• Controller: {away_name} (weighted advantage: {away_weighted:.2f} > {home_weighted:.2f})")
            else:
                # Weighted scores are too close - check LAW 1
                system_log.append("❌ LAW 1 VIOLATION: Quiet Control ambiguous")
                system_log.append(f"  • Home weighted score: {home_weighted:.2f}")
                system_log.append(f"  • Away weighted score: {away_weighted:.2f}")
                system_log.append(f"  • Difference: {abs(home_weighted - away_weighted):.2f} ≤ 0.1")
                system_log.append("• STATUS RESOLUTION REQUIRED → NO DECLARATION")
                system_log.append("⚠️ SYSTEM SILENT")
                
                return {
                    'declaration': None,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': "LAW 1 VIOLATION: Quiet Control ambiguous (requires status resolution)",
                    'capital_authorized': False,
                    'gates_passed': gates_passed,
                    'total_gates': total_gates,
                    'law_violations': ["LAW 1: Status resolution required"]
                }
        
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
            system_log.append(f"  • {home_name}: {home_score}/4 criteria (need {CONTROL_CRITERIA_REQUIRED}+)")
            system_log.append(f"  • {away_name}: {away_score}/4 criteria (need {CONTROL_CRITERIA_REQUIRED}+)")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"No team meets {CONTROL_CRITERIA_REQUIRED}+ control criteria",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 1 PASSED: Quiet Control → {controller}")
        
        # =================== GATE 2: DIRECTIONAL DOMINANCE ===================
        system_log.append("")
        system_log.append("GATE 2: DIRECTIONAL DOMINANCE (LAW 2)")
        
        # Determine opponent and get xG values
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        controller_xg = home_data.get('home_xg_per_match', 0) if is_controller_home else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if is_controller_home else home_data.get('home_xg_per_match', 0)
        
        # Check directional dominance
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
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'law_violations': ["LAW 2: Insufficient directional dominance"],
                'controller': controller,
                'control_delta': control_delta
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 2 PASSED: Directional dominance confirmed (Δ = {control_delta:+.2f})")
        
        # =================== GATE 3: STATE-FLIP CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 3: STATE-FLIP CAPACITY")
        
        # Get opponent data
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        # Check state-flip capacity
        failures, flip_rationale = cls.check_state_flip_capacity(
            opponent_data, is_opponent_home, opponent, league_avg_xg
        )
        system_log.extend(flip_rationale)
        
        if failures < STATE_FLIP_FAILURES_REQUIRED:
            system_log.append("❌ GATE 3 FAILED: Opponent retains escalation paths")
            system_log.append(f"  • Failures: {failures}/{STATE_FLIP_FAILURES_REQUIRED} required")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Opponent retains state-flip capacity ({failures}/{STATE_FLIP_FAILURES_REQUIRED} failures)",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'controller': controller,
                'control_delta': control_delta,
                'state_flip_failures': failures
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 3 PASSED: State-flip capacity absent ({failures}/4 failures)")
        
        # =================== GATE 4: ENFORCEMENT CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 4: ENFORCEMENT WITHOUT URGENCY (LAW 3)")
        
        # Get controller data
        controller_data = home_data if controller == home_name else away_data
        
        # Check enforcement capacity
        enforce_methods, enforce_rationale = cls.check_enforcement_capacity(
            controller_data, is_controller_home, controller
        )
        system_log.extend(enforce_rationale)
        
        if enforce_methods < ENFORCEMENT_METHODS_REQUIRED:
            system_log.append("❌ GATE 4 FAILED: Insufficient enforcement capacity")
            system_log.append(f"  • Methods: {enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} required")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"LAW 3 VIOLATION: Insufficient enforcement capacity ({enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} methods)",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'controller': controller,
                'control_delta': control_delta,
                'state_flip_failures': failures,
                'enforce_methods': enforce_methods,
                'law_violations': ["LAW 3: Insufficient enforcement methods"]
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4 PASSED: Redundant enforcement confirmed ({enforce_methods}/2+ methods)")
        
        # =================== STATE LOCK DECLARATION ===================
        system_log.append("")
        system_log.append("=" * 70)
        system_log.append("🔒 STATE LOCK DECLARATION")
        system_log.append("=" * 70)
        
        # Generate appropriate declaration
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
        system_log.append("💰 CAPITAL AUTHORIZED")
        system_log.append(f"• All {total_gates}/{total_gates} gates passed")
        system_log.append(f"• Control Delta: {control_delta:+.2f} (threshold: >{DIRECTION_THRESHOLD})")
        system_log.append(f"• State-Flip Failures: {failures}/4")
        system_log.append(f"• Enforcement Methods: {enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED}+")
        system_log.append("• Match outcome structurally constrained")
        system_log.append("• Opponent agency eliminated")
        system_log.append("=" * 70)
        
        return {
            'declaration': declaration,
            'state_locked': True,
            'system_log': system_log,
            'reason': "All canonical gates passed. State structurally locked.",
            'capital_authorized': True,
            'gates_passed': gates_passed,
            'total_gates': total_gates,
            'controller': controller,
            'controller_criteria': controller_criteria,
            'opponent': opponent,
            'control_delta': control_delta,
            'state_flip_failures': failures,
            'enforce_methods': enforce_methods,
            'key_metrics': {
                'controller_xg': controller_xg,
                'opponent_xg': opponent_xg,
                'league_avg_xg': league_avg_xg
            },
            'team_context': {
                'home': home_name,
                'away': away_name,
                'home_pos': home_data.get('season_position', 10),
                'away_pos': away_data.get('season_position', 10)
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
    st.markdown('<div class="system-header">🔐 BRUTBALL v6.1.1 – CANONICAL STATE LOCK</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>Logically complete • No status resolution • Direction mandatory • Redundant enforcement</strong></p>
        <p>STATE LOCKED or NO DECLARATION – silence is discipline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System constants display
    with st.expander("🔒 SYSTEM CONSTANTS (IMMUTABLE)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Direction Threshold", f"> {DIRECTION_THRESHOLD}", "LAW 2")
        with col2:
            st.metric("Enforcement Methods", f"≥ {ENFORCEMENT_METHODS_REQUIRED}", "LAW 3")
        with col3:
            st.metric("Control Criteria", f"≥ {CONTROL_CRITERIA_REQUIRED}", "GATE 1")
        with col4:
            st.metric("State-Flip Failures", f"≥ {STATE_FLIP_FAILURES_REQUIRED}", "GATE 3")
        
        st.markdown('<div class="law-display">', unsafe_allow_html=True)
        st.markdown("**🔒 SYSTEM LAWS**")
        st.markdown("1. **LAW 1:** Status resolution → NO DECLARATION")
        st.markdown("2. **LAW 2:** Direction Δ ≤ 0.25 → NO DECLARATION")  
        st.markdown("3. **LAW 3:** Enforcement methods < 2 → NO DECLARATION")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(7)
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
    if st.button("🔒 EXECUTE CANONICAL GATES", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute canonical gates
        result = BrutballCanonicalEngine.execute_canonical_gates(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🔍 SYSTEM VERDICT")
        
        if result['state_locked']:
            # STATE LOCKED DECLARATION
            st.markdown(f"""
            <div class="state-locked-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #16A34A; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">STATE LOCKED</h1>
                <div style="font-size: 1.3rem; color: #059669; margin-bottom: 1.5rem; font-weight: 600; line-height: 1.4;">
                    {result['declaration'].split('\\n')[1] if '\\n' in result['declaration'] else ''}
                </div>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem; line-height: 1.4;">
                    {result['declaration'].split('\\n')[2] if len(result['declaration'].split('\\n')) > 2 else ''}
                </div>
                <div style="background: #16A34A; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    CAPITAL AUTHORIZED
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gate sequence results
            st.markdown("#### 🚪 CANONICAL GATE SEQUENCE")
            
            gate_steps = [
                f"GATE 1: Quiet Control → {result['controller']}",
                f"GATE 2: Directional Dominance → Δ = {result['control_delta']:+.2f}",
                f"GATE 3: State-Flip Capacity → {result['state_flip_failures']}/4 failures",
                f"GATE 4: Enforcement Capacity → {result['enforce_methods']}/2+ methods"
            ]
            
            for i, step in enumerate(gate_steps):
                st.markdown(f"""
                <div class="gate-step">
                    <div style="color: #16A34A; font-weight: 600;">✅ {step}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Capital authorization
            st.markdown("""
            <div class="capital-authorized">
                <h3 style="margin: 0; color: white;">💰 CAPITAL AUTHORIZATION ACTIVE</h3>
                <p style="margin: 0.5rem 0 0 0; color: #D1FAE5; font-size: 0.95rem;">
                    All canonical gates passed. System has declared STATE LOCKED.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Structural metrics
            st.markdown("#### 📊 STRUCTURAL METRICS")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Directional Analysis**")
                
                controller_xg = result['key_metrics']['controller_xg']
                opponent_xg = result['key_metrics']['opponent_xg']
                control_delta = result['control_delta']
                
                st.markdown(f"""
                <div class="metric-row metric-row-controller">
                    <span>🎯 {result['controller']}:</span>
                    <span><strong>{controller_xg:.2f}</strong></span>
                    <span class="status-badge status-success">Controller</span>
                </div>
                
                <div class="metric-row">
                    <span>⚫ {result['opponent']}:</span>
                    <span><strong>{opponent_xg:.2f}</strong></span>
                    <span class="status-badge status-neutral">Opponent</span>
                </div>
                
                <div class="metric-row" style="background: #EFF6FF;">
                    <span>📈 Control Delta:</span>
                    <span><strong>{control_delta:+.2f}</strong></span>
                    <span class="status-badge status-success">> {DIRECTION_THRESHOLD}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Capacity Analysis**")
                
                st.markdown(f"""
                <div class="metric-row">
                    <span>🔓 State-Flip Failures:</span>
                    <span><strong>{result['state_flip_failures']}/4</strong></span>
                    <span class="status-badge {'status-success' if result['state_flip_failures'] >= 2 else 'status-warning'}">
                        ≥{STATE_FLIP_FAILURES_REQUIRED}
                    </span>
                </div>
                
                <div class="metric-row">
                    <span>🛡️ Enforcement Methods:</span>
                    <span><strong>{result['enforce_methods']}/2+</strong></span>
                    <span class="status-badge {'status-success' if result['enforce_methods'] >= 2 else 'status-danger'}">
                        LAW 3
                    </span>
                </div>
                
                <div class="metric-row">
                    <span>🏆 Quiet Control Criteria:</span>
                    <span><strong>{len(result['controller_criteria'])}/4</strong></span>
                    <span class="status-badge {'status-success' if len(result['controller_criteria']) >= 2 else 'status-warning'}">
                        ≥{CONTROL_CRITERIA_REQUIRED}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # NO DECLARATION
            st.markdown(f"""
            <div class="no-declaration-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #6B7280; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">NO DECLARATION</h1>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem; line-height: 1.4;">
                    {result['reason']}
                </div>
                <div style="background: #6B7280; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    SYSTEM SILENT
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # No capital authorization
            st.markdown("""
            <div class="no-capital">
                <h3 style="margin: 0; color: white;">🚫 CAPITAL NOT AUTHORIZED</h3>
                <p style="margin: 0.5rem 0 0 0; color: #E5E7EB; font-size: 0.95rem;">
                    System has not declared STATE LOCKED. No capital deployment permitted.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gate failures
            if result.get('gates_passed', 0) > 0:
                st.markdown("#### 🚫 GATE FAILURE ANALYSIS")
                
                gates_passed = result.get('gates_passed', 0)
                total_gates = result.get('total_gates', 4)
                
                st.markdown(f"**Gates passed:** {gates_passed}/{total_gates}")
                
                if result.get('law_violations'):
                    st.markdown('<div class="law-violation">', unsafe_allow_html=True)
                    st.markdown("**LAW VIOLATIONS DETECTED:**")
                    for violation in result['law_violations']:
                        st.markdown(f"• {violation}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show controller info if identified
                if result.get('controller'):
                    st.markdown(f"""
                    <div class="no-control-indicator">
                        <h4 style="color: #6B7280; margin: 0;">CONTROLLER IDENTIFIED: {result['controller']}</h4>
                        <p style="color: #6B7280; margin: 0.5rem 0;">
                            But canonical gates not fully satisfied
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # System log
        with st.expander("📋 VIEW SYSTEM LOG", expanded=True):
            st.markdown('<div class="system-log">', unsafe_allow_html=True)
            for line in result['system_log']:
                st.text(line)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export System Verdict")
        
        export_text = f"""BRUTBALL v6.1.1 - CANONICAL STATE LOCK VERDICT
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
System Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM DECLARATION:
{result['declaration'] if result['state_locked'] else 'NO DECLARATION'}

CAPITAL AUTHORIZATION: {'AUTHORIZED' if result['state_locked'] else 'NOT AUTHORIZED'}

REASON:
{result['reason']}

GATE SEQUENCE RESULTS:
Gates passed: {result.get('gates_passed', 0)}/{result.get('total_gates', 4)}
{result.get('law_violations', ['No law violations'])[0] if result.get('law_violations') else 'All laws satisfied'}

{'CONTROLLER:' if result.get('controller') else ''}
{result.get('controller', 'N/A')}
{', '.join(result.get('controller_criteria', [])) if result.get('controller_criteria') else ''}

{'KEY METRICS:' if result.get('key_metrics') else ''}
{''.join([f'{k}: {v:.2f}\\n' for k, v in result.get('key_metrics', {}).items()])}

SYSTEM LOG:
{chr(10).join(result['system_log'])}

===========================================
BRUTBALL v6.1.1 - Canonical State Lock Engine
Logically complete • No status resolution • Direction mandatory
Silence is discipline • Capital flows only on STATE LOCKED
        """
        
        st.download_button(
            label="📥 Download System Verdict",
            data=export_text,
            file_name=f"brutball_v6.1.1_verdict_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL v6.1.1 – Canonical State Lock Engine</strong></p>
        <p>Logically complete • No status resolution • Direction mandatory • Redundant enforcement</p>
        <p>STATE LOCKED or NO DECLARATION – silence is not failure, silence is discipline</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== SYSTEM CONSTANTS (IMMUTABLE) ===================
DIRECTION_THRESHOLD = 0.25  # LAW 2: Direction is mandatory
ENFORCEMENT_METHODS_REQUIRED = 2  # LAW 3: Enforcement must be redundant
CONTROL_CRITERIA_REQUIRED = 2  # GATE 1: Minimum for Quiet Control
STATE_FLIP_FAILURES_REQUIRED = 2  # GATE 3: Opponent fails ≥2 escalation paths

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1.1 - Canonical State Lock",
    page_icon="🔒",
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
    </style>
""", unsafe_allow_html=True)

# =================== BRUTBALL v6.1.1 - CANONICAL STATE LOCK ENGINE ===================
class BrutballCanonicalEngine:
    """
    BRUTBALL v6.1.1 - CANONICAL STATE LOCK ENGINE
    Logically complete. No status resolution. Direction mandatory.
    """
    
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, opponent_data: Dict,
                              is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """
        GATE 1: Evaluate Quiet Control.
        Returns: (raw_score, weighted_score, criteria_met, rationale)
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
        """
        GATE 2: Check directional dominance (LAW 2).
        Control Delta must exceed DIRECTION_THRESHOLD.
        """
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
        """
        GATE 3: Check state-flip capacity.
        Opponent must fail ≥2 of 4 escalation checks.
        """
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
        """
        GATE 4: Check enforcement without urgency (LAW 3).
        Must have ≥2 independent enforcement methods.
        """
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
    def execute_canonical_gates(cls, home_data: Dict, away_data: Dict,
                               home_name: str, away_name: str,
                               league_avg_xg: float) -> Dict:
        """
        Execute canonical gate sequence. No status resolution. Direction mandatory.
        Returns STATE LOCKED declaration or NO DECLARATION.
        """
        system_log = []
        gates_passed = 0
        total_gates = 4
        
        system_log.append("=" * 70)
        system_log.append("🔐 BRUTBALL v6.1.1 - CANONICAL STATE LOCK")
        system_log.append("=" * 70)
        system_log.append(f"MATCH: {home_name} vs {away_name}")
        system_log.append(f"SYSTEM TIME: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        system_log.append("")
        
        # =================== GATE 1: QUIET CONTROL ===================
        system_log.append("GATE 1: QUIET CONTROL IDENTIFICATION")
        
        # Evaluate both teams
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
        tie_breaker_applied = False
        used_status_resolution = False
        
        if home_score >= CONTROL_CRITERIA_REQUIRED and away_score >= CONTROL_CRITERIA_REQUIRED:
            # Both teams meet minimum criteria - check for clear winner
            if home_weighted > away_weighted + 0.1:  # Clear weighted advantage
                controller = home_name
                controller_criteria = home_criteria
                system_log.append(f"• Controller: {home_name} (weighted advantage: {home_weighted:.2f} > {away_weighted:.2f})")
            elif away_weighted > home_weighted + 0.1:
                controller = away_name
                controller_criteria = away_criteria
                system_log.append(f"• Controller: {away_name} (weighted advantage: {away_weighted:.2f} > {home_weighted:.2f})")
            else:
                # Weighted scores are too close - check LAW 1
                system_log.append("❌ LAW 1 VIOLATION: Quiet Control ambiguous")
                system_log.append(f"  • Home weighted score: {home_weighted:.2f}")
                system_log.append(f"  • Away weighted score: {away_weighted:.2f}")
                system_log.append(f"  • Difference: {abs(home_weighted - away_weighted):.2f} ≤ 0.1")
                system_log.append("• STATUS RESOLUTION REQUIRED → NO DECLARATION")
                system_log.append("⚠️ SYSTEM SILENT")
                
                return {
                    'declaration': None,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': "LAW 1 VIOLATION: Quiet Control ambiguous (requires status resolution)",
                    'capital_authorized': False,
                    'gates_passed': gates_passed,
                    'total_gates': total_gates,
                    'law_violations': ["LAW 1: Status resolution required"]
                }
        
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
            system_log.append(f"  • {home_name}: {home_score}/4 criteria (need {CONTROL_CRITERIA_REQUIRED}+)")
            system_log.append(f"  • {away_name}: {away_score}/4 criteria (need {CONTROL_CRITERIA_REQUIRED}+)")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"No team meets {CONTROL_CRITERIA_REQUIRED}+ control criteria",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 1 PASSED: Quiet Control → {controller}")
        
        # =================== GATE 2: DIRECTIONAL DOMINANCE ===================
        system_log.append("")
        system_log.append("GATE 2: DIRECTIONAL DOMINANCE (LAW 2)")
        
        # Determine opponent and get xG values
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        controller_xg = home_data.get('home_xg_per_match', 0) if is_controller_home else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if is_controller_home else home_data.get('home_xg_per_match', 0)
        
        # Check directional dominance
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
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'law_violations': ["LAW 2: Insufficient directional dominance"],
                'controller': controller,
                'control_delta': control_delta
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 2 PASSED: Directional dominance confirmed (Δ = {control_delta:+.2f})")
        
        # =================== GATE 3: STATE-FLIP CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 3: STATE-FLIP CAPACITY")
        
        # Get opponent data
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        # Check state-flip capacity
        failures, flip_rationale = cls.check_state_flip_capacity(
            opponent_data, is_opponent_home, opponent, league_avg_xg
        )
        system_log.extend(flip_rationale)
        
        if failures < STATE_FLIP_FAILURES_REQUIRED:
            system_log.append("❌ GATE 3 FAILED: Opponent retains escalation paths")
            system_log.append(f"  • Failures: {failures}/{STATE_FLIP_FAILURES_REQUIRED} required")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Opponent retains state-flip capacity ({failures}/{STATE_FLIP_FAILURES_REQUIRED} failures)",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'controller': controller,
                'control_delta': control_delta,
                'state_flip_failures': failures
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 3 PASSED: State-flip capacity absent ({failures}/4 failures)")
        
        # =================== GATE 4: ENFORCEMENT CAPACITY ===================
        system_log.append("")
        system_log.append("GATE 4: ENFORCEMENT WITHOUT URGENCY (LAW 3)")
        
        # Get controller data
        controller_data = home_data if controller == home_name else away_data
        
        # Check enforcement capacity
        enforce_methods, enforce_rationale = cls.check_enforcement_capacity(
            controller_data, is_controller_home, controller
        )
        system_log.extend(enforce_rationale)
        
        if enforce_methods < ENFORCEMENT_METHODS_REQUIRED:
            system_log.append("❌ GATE 4 FAILED: Insufficient enforcement capacity")
            system_log.append(f"  • Methods: {enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} required")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'declaration': None,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"LAW 3 VIOLATION: Insufficient enforcement capacity ({enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED} methods)",
                'capital_authorized': False,
                'gates_passed': gates_passed,
                'total_gates': total_gates,
                'controller': controller,
                'control_delta': control_delta,
                'state_flip_failures': failures,
                'enforce_methods': enforce_methods,
                'law_violations': ["LAW 3: Insufficient enforcement methods"]
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4 PASSED: Redundant enforcement confirmed ({enforce_methods}/2+ methods)")
        
        # =================== STATE LOCK DECLARATION ===================
        system_log.append("")
        system_log.append("=" * 70)
        system_log.append("🔒 STATE LOCK DECLARATION")
        system_log.append("=" * 70)
        
        # Generate appropriate declaration
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
        system_log.append("💰 CAPITAL AUTHORIZED")
        system_log.append(f"• All {total_gates}/{total_gates} gates passed")
        system_log.append(f"• Control Delta: {control_delta:+.2f} (threshold: >{DIRECTION_THRESHOLD})")
        system_log.append(f"• State-Flip Failures: {failures}/4")
        system_log.append(f"• Enforcement Methods: {enforce_methods}/{ENFORCEMENT_METHODS_REQUIRED}+")
        system_log.append("• Match outcome structurally constrained")
        system_log.append("• Opponent agency eliminated")
        system_log.append("=" * 70)
        
        return {
            'declaration': declaration,
            'state_locked': True,
            'system_log': system_log,
            'reason': "All canonical gates passed. State structurally locked.",
            'capital_authorized': True,
            'gates_passed': gates_passed,
            'total_gates': total_gates,
            'controller': controller,
            'controller_criteria': controller_criteria,
            'opponent': opponent,
            'control_delta': control_delta,
            'state_flip_failures': failures,
            'enforce_methods': enforce_methods,
            'key_metrics': {
                'controller_xg': controller_xg,
                'opponent_xg': opponent_xg,
                'league_avg_xg': league_avg_xg
            },
            'team_context': {
                'home': home_name,
                'away': away_name,
                'home_pos': home_data.get('season_position', 10),
                'away_pos': away_data.get('season_position', 10)
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
    st.markdown('<div class="system-header">🔐 BRUTBALL v6.1.1 – CANONICAL STATE LOCK</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>Logically complete • No status resolution • Direction mandatory • Redundant enforcement</strong></p>
        <p>STATE LOCKED or NO DECLARATION – silence is discipline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System constants display
    with st.expander("🔒 SYSTEM CONSTANTS (IMMUTABLE)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Direction Threshold", f"> {DIRECTION_THRESHOLD}", "LAW 2")
        with col2:
            st.metric("Enforcement Methods", f"≥ {ENFORCEMENT_METHODS_REQUIRED}", "LAW 3")
        with col3:
            st.metric("Control Criteria", f"≥ {CONTROL_CRITERIA_REQUIRED}", "GATE 1")
        with col4:
            st.metric("State-Flip Failures", f"≥ {STATE_FLIP_FAILURES_REQUIRED}", "GATE 3")
        
        st.markdown('<div class="law-display">', unsafe_allow_html=True)
        st.markdown("**🔒 SYSTEM LAWS**")
        st.markdown("1. **LAW 1:** Status resolution → NO DECLARATION")
        st.markdown("2. **LAW 2:** Direction Δ ≤ 0.25 → NO DECLARATION")  
        st.markdown("3. **LAW 3:** Enforcement methods < 2 → NO DECLARATION")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(7)
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
    if st.button("🔒 EXECUTE CANONICAL GATES", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute canonical gates
        result = BrutballCanonicalEngine.execute_canonical_gates(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🔍 SYSTEM VERDICT")
        
        if result['state_locked']:
            # STATE LOCKED DECLARATION
            st.markdown(f"""
            <div class="state-locked-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #16A34A; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">STATE LOCKED</h1>
                <div style="font-size: 1.3rem; color: #059669; margin-bottom: 1.5rem; font-weight: 600; line-height: 1.4;">
                    {result['declaration'].split('\\n')[1] if '\\n' in result['declaration'] else ''}
                </div>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem; line-height: 1.4;">
                    {result['declaration'].split('\\n')[2] if len(result['declaration'].split('\\n')) > 2 else ''}
                </div>
                <div style="background: #16A34A; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    CAPITAL AUTHORIZED
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gate sequence results
            st.markdown("#### 🚪 CANONICAL GATE SEQUENCE")
            
            gate_steps = [
                f"GATE 1: Quiet Control → {result['controller']}",
                f"GATE 2: Directional Dominance → Δ = {result['control_delta']:+.2f}",
                f"GATE 3: State-Flip Capacity → {result['state_flip_failures']}/4 failures",
                f"GATE 4: Enforcement Capacity → {result['enforce_methods']}/2+ methods"
            ]
            
            for i, step in enumerate(gate_steps):
                st.markdown(f"""
                <div class="gate-step">
                    <div style="color: #16A34A; font-weight: 600;">✅ {step}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Capital authorization
            st.markdown("""
            <div class="capital-authorized">
                <h3 style="margin: 0; color: white;">💰 CAPITAL AUTHORIZATION ACTIVE</h3>
                <p style="margin: 0.5rem 0 0 0; color: #D1FAE5; font-size: 0.95rem;">
                    All canonical gates passed. System has declared STATE LOCKED.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Structural metrics
            st.markdown("#### 📊 STRUCTURAL METRICS")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Directional Analysis**")
                
                controller_xg = result['key_metrics']['controller_xg']
                opponent_xg = result['key_metrics']['opponent_xg']
                control_delta = result['control_delta']
                
                st.markdown(f"""
                <div class="metric-row metric-row-controller">
                    <span>🎯 {result['controller']}:</span>
                    <span><strong>{controller_xg:.2f}</strong></span>
                    <span class="status-badge status-success">Controller</span>
                </div>
                
                <div class="metric-row">
                    <span>⚫ {result['opponent']}:</span>
                    <span><strong>{opponent_xg:.2f}</strong></span>
                    <span class="status-badge status-neutral">Opponent</span>
                </div>
                
                <div class="metric-row" style="background: #EFF6FF;">
                    <span>📈 Control Delta:</span>
                    <span><strong>{control_delta:+.2f}</strong></span>
                    <span class="status-badge status-success">> {DIRECTION_THRESHOLD}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Capacity Analysis**")
                
                st.markdown(f"""
                <div class="metric-row">
                    <span>🔓 State-Flip Failures:</span>
                    <span><strong>{result['state_flip_failures']}/4</strong></span>
                    <span class="status-badge {'status-success' if result['state_flip_failures'] >= 2 else 'status-warning'}">
                        ≥{STATE_FLIP_FAILURES_REQUIRED}
                    </span>
                </div>
                
                <div class="metric-row">
                    <span>🛡️ Enforcement Methods:</span>
                    <span><strong>{result['enforce_methods']}/2+</strong></span>
                    <span class="status-badge {'status-success' if result['enforce_methods'] >= 2 else 'status-danger'}">
                        LAW 3
                    </span>
                </div>
                
                <div class="metric-row">
                    <span>🏆 Quiet Control Criteria:</span>
                    <span><strong>{len(result['controller_criteria'])}/4</strong></span>
                    <span class="status-badge {'status-success' if len(result['controller_criteria']) >= 2 else 'status-warning'}">
                        ≥{CONTROL_CRITERIA_REQUIRED}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # NO DECLARATION
            st.markdown(f"""
            <div class="no-declaration-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #6B7280; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">NO DECLARATION</h1>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem; line-height: 1.4;">
                    {result['reason']}
                </div>
                <div style="background: #6B7280; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    SYSTEM SILENT
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # No capital authorization
            st.markdown("""
            <div class="no-capital">
                <h3 style="margin: 0; color: white;">🚫 CAPITAL NOT AUTHORIZED</h3>
                <p style="margin: 0.5rem 0 0 0; color: #E5E7EB; font-size: 0.95rem;">
                    System has not declared STATE LOCKED. No capital deployment permitted.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gate failures
            if result.get('gates_passed', 0) > 0:
                st.markdown("#### 🚫 GATE FAILURE ANALYSIS")
                
                gates_passed = result.get('gates_passed', 0)
                total_gates = result.get('total_gates', 4)
                
                st.markdown(f"**Gates passed:** {gates_passed}/{total_gates}")
                
                if result.get('law_violations'):
                    st.markdown('<div class="law-violation">', unsafe_allow_html=True)
                    st.markdown("**LAW VIOLATIONS DETECTED:**")
                    for violation in result['law_violations']:
                        st.markdown(f"• {violation}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show controller info if identified
                if result.get('controller'):
                    st.markdown(f"""
                    <div class="no-control-indicator">
                        <h4 style="color: #6B7280; margin: 0;">CONTROLLER IDENTIFIED: {result['controller']}</h4>
                        <p style="color: #6B7280; margin: 0.5rem 0;">
                            But canonical gates not fully satisfied
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # System log
        with st.expander("📋 VIEW SYSTEM LOG", expanded=True):
            st.markdown('<div class="system-log">', unsafe_allow_html=True)
            for line in result['system_log']:
                st.text(line)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export System Verdict")
        
        export_text = f"""BRUTBALL v6.1.1 - CANONICAL STATE LOCK VERDICT
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
System Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM DECLARATION:
{result['declaration'] if result['state_locked'] else 'NO DECLARATION'}

CAPITAL AUTHORIZATION: {'AUTHORIZED' if result['state_locked'] else 'NOT AUTHORIZED'}

REASON:
{result['reason']}

GATE SEQUENCE RESULTS:
Gates passed: {result.get('gates_passed', 0)}/{result.get('total_gates', 4)}
{result.get('law_violations', ['No law violations'])[0] if result.get('law_violations') else 'All laws satisfied'}

{'CONTROLLER:' if result.get('controller') else ''}
{result.get('controller', 'N/A')}
{', '.join(result.get('controller_criteria', [])) if result.get('controller_criteria') else ''}

{'KEY METRICS:' if result.get('key_metrics') else ''}
{''.join([f'{k}: {v:.2f}\\n' for k, v in result.get('key_metrics', {}).items()])}

SYSTEM LOG:
{chr(10).join(result['system_log'])}

===========================================
BRUTBALL v6.1.1 - Canonical State Lock Engine
Logically complete • No status resolution • Direction mandatory
Silence is discipline • Capital flows only on STATE LOCKED
        """
        
        st.download_button(
            label="📥 Download System Verdict",
            data=export_text,
            file_name=f"brutball_v6.1.1_verdict_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL v6.1.1 – Canonical State Lock Engine</strong></p>
        <p>Logically complete • No status resolution • Direction mandatory • Redundant enforcement</p>
        <p>STATE LOCKED or NO DECLARATION – silence is not failure, silence is discipline</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
