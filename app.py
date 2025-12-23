import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.1 - State Lock Engine",
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
    .state-flip-check {
        background: #FEF2F2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DC2626;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .enforcement-check {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #16A34A;
        margin: 0.5rem 0;
        font-size: 0.9rem;
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
    .metric-row-team {
        background: #F9FAFB;
    }
    .capital-authorization-box {
        padding: 1.5rem;
        background: #1E3A8A;
        color: white;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 3px solid #3B82F6;
    }
    .no-capital-box {
        padding: 1.5rem;
        background: #6B7280;
        color: white;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 3px solid #9CA3AF;
    }
    </style>
""", unsafe_allow_html=True)

# =================== BRUTBALL v6.1 - STATE LOCK ENGINE ===================
class BrutballStateLockEngine:
    """
    BRUTBALL v6.1 - DECLARATIVE STATE LOCK ENGINE
    Moves from probabilistic reasoning to declarative law
    STATE LOCKED or NO DECLARATION - nothing else
    """
    
    # =================== QUIET CONTROL (AXIOM 2) ===================
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, opponent_data: Dict,
                              is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """
        Evaluate 4 control criteria with weighted scoring for tie-breakers.
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
        
        # CRITERION 4: Repeatable scoring patterns (weight: 0.8)
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
    
    # =================== STATE FLIP CAPACITY CHECK (NEW) ===================
    @staticmethod
    def check_state_flip_capacity(opponent_data: Dict, is_home: bool, 
                                 opponent_name: str, league_avg_xg: float) -> Tuple[int, List[str]]:
        """
        Check if opponent has credible escalation paths.
        Opponent fails 2+ of 4 checks → NO STATE-FLIP CAPACITY.
        Returns: (failures_count, rationale)
        """
        rationale = []
        failures = 0
        
        rationale.append(f"🔍 STATE-FLIP CAPACITY CHECK for {opponent_name}")
        
        # CHECK 1: Chase xG < 1.1
        if is_home:
            chase_xg = opponent_data.get('home_xg_per_match', 0)
        else:
            chase_xg = opponent_data.get('away_xg_per_match', 0)
        
        if chase_xg < 1.1:
            failures += 1
            rationale.append(f"❌ {opponent_name}: Chase xG {chase_xg:.2f} < 1.1 (cannot sustain pressure)")
        else:
            rationale.append(f"✅ {opponent_name}: Chase xG {chase_xg:.2f} ≥ 1.1")
        
        # CHECK 2: No tempo surge capability
        # Assuming no surge if xG < 1.4 (cannot exceed 1.4 when trailing)
        if chase_xg < 1.4:
            failures += 1
            rationale.append(f"❌ {opponent_name}: No tempo surge (xG {chase_xg:.2f} < 1.4)")
        else:
            rationale.append(f"✅ {opponent_name}: Tempo surge possible (xG ≥ 1.4)")
        
        # CHECK 3: No alternate threat channel
        if is_home:
            setpiece_pct = opponent_data.get('home_setpiece_pct', 0)
            counter_pct = opponent_data.get('home_counter_pct', 0)
        else:
            setpiece_pct = opponent_data.get('away_setpiece_pct', 0)
            counter_pct = opponent_data.get('away_counter_pct', 0)
        
        if setpiece_pct < 0.25 and counter_pct < 0.15:
            failures += 1
            rationale.append(f"❌ {opponent_name}: No alternate threat (set pieces: {setpiece_pct:.1%}, counters: {counter_pct:.1%})")
        else:
            rationale.append(f"✅ {opponent_name}: Alternate threat exists")
        
        # CHECK 4: Low substitution leverage (simplified - check bench quality proxy)
        # Using goals per match as proxy for bench impact
        if is_home:
            gpm = opponent_data.get('home_goals_per_match', 0)
        else:
            gpm = opponent_data.get('away_goals_per_match', 0)
        
        if gpm < league_avg_xg * 0.8:  # Below 80% of league average
            failures += 1
            rationale.append(f"❌ {opponent_name}: Low substitution leverage (goals/match: {gpm:.2f} < {league_avg_xg*0.8:.2f})")
        else:
            rationale.append(f"✅ {opponent_name}: Adequate bench impact")
        
        # Summary
        if failures >= 2:
            rationale.append(f"🔒 {opponent_name} lacks state-flip capacity ({failures}/4 checks failed)")
        else:
            rationale.append(f"⚠️ {opponent_name} retains escalation paths ({failures}/4 checks failed)")
        
        return failures, rationale
    
    # =================== ENFORCEMENT WITHOUT URGENCY CHECK ===================
    @staticmethod
    def check_enforcement_capacity(controller_data: Dict, is_home: bool,
                                  controller_name: str, opponent_name: str) -> Tuple[bool, List[str]]:
        """
        Check if controller can win without urgency.
        At least ONE must be true.
        Returns: (can_enforce, rationale)
        """
        rationale = []
        enforce_methods = 0
        
        rationale.append(f"🛡️ ENFORCEMENT CAPACITY CHECK for {controller_name}")
        
        if is_home:
            # METHOD 1: Can slow tempo after lead (defensive solidity)
            goals_conceded = controller_data.get('home_goals_conceded', 0)
            matches_played = controller_data.get('home_matches_played', 1)
            gcp_match = goals_conceded / matches_played
            
            if gcp_match < 1.2:  # Defensive solidity
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Can defend lead (concedes {gcp_match:.2f}/match < 1.2)")
            else:
                rationale.append(f"❌ {controller_name}: Defensive concerns ({gcp_match:.2f} conceded/match)")
            
            # METHOD 2: Can score from dead-ball/transition
            setpiece_pct = controller_data.get('home_setpiece_pct', 0)
            counter_pct = controller_data.get('home_counter_pct', 0)
            
            if setpiece_pct > 0.25 or counter_pct > 0.15:
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Alternate scoring (set pieces: {setpiece_pct:.1%}, counters: {counter_pct:.1%})")
            else:
                rationale.append(f"❌ {controller_name}: Limited alternate scoring")
            
            # METHOD 3: Can win without xG spikes
            xg_per_match = controller_data.get('home_xg_per_match', 0)
            if xg_per_match > 1.3:  # Can generate chances consistently
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Consistent threat (xG: {xg_per_match:.2f} > 1.3)")
            else:
                rationale.append(f"❌ {controller_name}: Requires xG spikes to win")
        
        else:  # Away team
            # METHOD 1: Defensive solidity away
            goals_conceded = controller_data.get('away_goals_conceded', 0)
            matches_played = controller_data.get('away_matches_played', 1)
            gcp_match = goals_conceded / matches_played
            
            if gcp_match < 1.3:  # Slightly higher threshold for away
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Can defend away (concedes {gcp_match:.2f}/match < 1.3)")
            else:
                rationale.append(f"❌ {controller_name}: Defensive concerns away")
            
            # METHOD 2: Away scoring versatility
            setpiece_pct = controller_data.get('away_setpiece_pct', 0)
            counter_pct = controller_data.get('away_counter_pct', 0)
            
            if setpiece_pct > 0.2 or counter_pct > 0.12:  # Lower thresholds for away
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Away scoring versatility")
            else:
                rationale.append(f"❌ {controller_name}: Limited away scoring methods")
            
            # METHOD 3: Away consistency
            xg_per_match = controller_data.get('away_xg_per_match', 0)
            if xg_per_match > 1.2:  # Lower threshold for away consistency
                enforce_methods += 1
                rationale.append(f"✅ {controller_name}: Consistent away threat (xG: {xg_per_match:.2f} > 1.2)")
            else:
                rationale.append(f"❌ {controller_name}: Requires exceptional away performance")
        
        # Final determination
        if enforce_methods >= 1:
            rationale.append(f"✅ {controller_name} can enforce without urgency ({enforce_methods}/3 methods)")
            return True, rationale
        else:
            rationale.append(f"❌ {controller_name} lacks enforcement capacity (0/3 methods)")
            return False, rationale
    
    # =================== STATE LOCK DECLARATION ===================
    @classmethod
    def declare_state_lock(cls, home_data: Dict, away_data: Dict,
                          home_name: str, away_name: str,
                          league_avg_xg: float) -> Dict:
        """
        Execute STATE LOCK declaration logic.
        Returns FULL declaration or NO DECLARATION.
        No probabilities, no confidence levels, no partial states.
        """
        audit_log = []
        declaration = None
        controller = None
        controller_criteria = []
        
        audit_log.append("=" * 70)
        audit_log.append("🔐 BRUTBALL v6.1 - STATE LOCK DECLARATION ENGINE")
        audit_log.append("=" * 70)
        audit_log.append(f"Match: {home_name} vs {away_name}")
        audit_log.append("")
        
        # =================== STEP 1: IDENTIFY QUIET CONTROL ===================
        audit_log.append("STEP 1: QUIET CONTROL IDENTIFICATION (AXIOM 2)")
        
        # Evaluate home team
        home_score, home_weighted, home_criteria, home_rationale = cls.evaluate_quiet_control(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        # Evaluate away team
        away_score, away_weighted, away_criteria, away_rationale = cls.evaluate_quiet_control(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        audit_log.extend(home_rationale)
        audit_log.extend(away_rationale)
        
        # Determine controller with tie-breaker logic
        controller = None
        controller_criteria = []
        tie_breaker_applied = False
        
        if home_score >= 2 and away_score >= 2:
            # TIE-BREAKER
            audit_log.append("⚖️ TIE-BREAKER: Both teams meet ≥2 criteria")
            
            if home_weighted > away_weighted:
                controller = home_name
                controller_criteria = home_criteria
                audit_log.append(f"  • Tie-breaker: {home_name} selected (higher structured control score)")
            elif away_weighted > home_weighted:
                controller = away_name
                controller_criteria = away_criteria
                audit_log.append(f"  • Tie-breaker: {away_name} selected (higher structured control score)")
            else:
                # Equal weighted scores - use season position
                home_pos = home_data.get('season_position', 10)
                away_pos = away_data.get('season_position', 10)
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
            audit_log.append(f"🎯 QUIET CONTROL: {home_name} ({home_score}/4 criteria)")
            
        elif away_score >= 2 and away_score > home_score:
            controller = away_name
            controller_criteria = away_criteria
            audit_log.append(f"🎯 QUIET CONTROL: {away_name} ({away_score}/4 criteria)")
        
        else:
            audit_log.append("❌ NO QUIET CONTROL IDENTIFIED")
            audit_log.append("⚠️ SYSTEM SILENT: NO DECLARATION POSSIBLE")
            return {
                'declaration': None,
                'controller': None,
                'state_locked': False,
                'audit_log': audit_log,
                'reason': "No quiet control identified",
                'capital_authorized': False
            }
        
        audit_log.append(f"🔑 Controller identified: {controller}")
        
        # =================== STEP 2: CHECK STATE-FLIP CAPACITY ===================
        audit_log.append("")
        audit_log.append("STEP 2: STATE-FLIP CAPACITY CHECK (AXIOM 11)")
        
        # Determine opponent
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        # Get opponent data
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        # Check state-flip capacity
        failures, flip_rationale = cls.check_state_flip_capacity(
            opponent_data, is_opponent_home, opponent, league_avg_xg
        )
        audit_log.extend(flip_rationale)
        
        if failures < 2:
            audit_log.append(f"❌ {opponent} retains escalation paths ({failures}/4 checks failed)")
            audit_log.append("⚠️ SYSTEM SILENT: NO DECLARATION POSSIBLE")
            return {
                'declaration': None,
                'controller': controller,
                'state_locked': False,
                'audit_log': audit_log,
                'reason': f"Opponent retains state-flip capacity ({failures}/4 checks failed)",
                'capital_authorized': False
            }
        
        audit_log.append(f"✅ STATE-FLIP CAPACITY ABSENT ({failures}/4 checks failed)")
        
        # =================== STEP 3: CHECK ENFORCEMENT CAPACITY ===================
        audit_log.append("")
        audit_log.append("STEP 3: ENFORCEMENT WITHOUT URGENCY CHECK")
        
        # Get controller data
        controller_data = home_data if controller == home_name else away_data
        
        # Check enforcement capacity
        can_enforce, enforce_rationale = cls.check_enforcement_capacity(
            controller_data, is_controller_home, controller, opponent
        )
        audit_log.extend(enforce_rationale)
        
        if not can_enforce:
            audit_log.append("❌ Controller lacks enforcement capacity")
            audit_log.append("⚠️ SYSTEM SILENT: NO DECLARATION POSSIBLE")
            return {
                'declaration': None,
                'controller': controller,
                'state_locked': False,
                'audit_log': audit_log,
                'reason': "Controller lacks enforcement without urgency",
                'capital_authorized': False
            }
        
        audit_log.append("✅ Controller can enforce without urgency")
        
        # =================== STATE LOCK DECLARATION ===================
        audit_log.append("")
        audit_log.append("=" * 70)
        audit_log.append("🔒 STATE LOCK DECLARATION")
        audit_log.append("=" * 70)
        
        # Generate specific declaration text based on context
        home_xg = home_data.get('home_xg_per_match', 0) if controller == home_name else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if controller == home_name else home_data.get('home_xg_per_match', 0)
        
        # Select appropriate declaration template
        if opponent_xg < 1.1:
            declaration = f"🔒 STATE LOCKED\n{opponent} lacks chase capacity\n{controller} can win at walking pace"
        elif failures >= 3:  # Multiple escalation failures
            declaration = f"🔒 STATE LOCKED\n{opponent} has no credible escalation paths\n{controller} controls restart & dead-ball leverage"
        else:
            declaration = f"🔒 STATE LOCKED\n{opponent} cannot disrupt state structure\n{controller} never forced into urgency"
        
        audit_log.append(declaration)
        audit_log.append("")
        audit_log.append("💰 CAPITAL AUTHORIZED")
        audit_log.append(f"• Controller: {controller}")
        audit_log.append(f"• Criteria met: {', '.join(controller_criteria)}")
        audit_log.append(f"• State-flip failures: {failures}/4")
        audit_log.append("• Match outcome structurally constrained")
        audit_log.append("• Opponent agency eliminated")
        audit_log.append("=" * 70)
        
        return {
            'declaration': declaration,
            'controller': controller,
            'controller_criteria': controller_criteria,
            'state_locked': True,
            'audit_log': audit_log,
            'reason': "All STATE LOCK conditions satisfied",
            'capital_authorized': True,
            'tie_breaker_applied': tie_breaker_applied,
            'state_flip_failures': failures,
            'opponent': opponent,
            'key_metrics': {
                'home_xg': home_data.get('home_xg_per_match', 0),
                'away_xg': away_data.get('away_xg_per_match', 0),
                'controller_xg': home_xg if controller == home_name else opponent_xg,
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
    st.markdown('<div class="audit-header">🔐 BRUTBALL v6.1 – STATE LOCK DECLARATION ENGINE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sub-header">
        <p><strong>Declarative • Binary • Capital follows declaration • No probabilities • No confidence scales</strong></p>
        <p>STATE LOCKED or NO DECLARATION – nothing else matters</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    if st.button("🔒 EXECUTE STATE LOCK DECLARATION", type="primary", use_container_width=True):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute STATE LOCK declaration
        result = BrutballStateLockEngine.declare_state_lock(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🔍 DECLARATION RESULT")
        
        if result['state_locked']:
            # STATE LOCKED DECLARATION
            st.markdown(f"""
            <div class="state-locked-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #16A34A; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">STATE LOCKED</h1>
                <div style="font-size: 1.3rem; color: #059669; margin-bottom: 1.5rem; font-weight: 600;">
                    {result['declaration'].split('\\n')[1] if '\\n' in result['declaration'] else ''}
                </div>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem;">
                    {result['declaration'].split('\\n')[2] if len(result['declaration'].split('\\n')) > 2 else ''}
                </div>
                <div style="background: #16A34A; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    CAPITAL AUTHORIZED
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Capital authorization box
            st.markdown("""
            <div class="capital-authorization-box">
                <h3 style="margin: 0; color: white;">💰 CAPITAL AUTHORIZATION ACTIVE</h3>
                <p style="margin: 0.5rem 0 0 0; color: #D1FAE5; font-size: 0.95rem;">
                    System has declared STATE LOCKED. Capital deployment permitted.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Controller information
            st.markdown("#### 🎯 QUIET CONTROL IDENTIFIED")
            st.markdown(f"""
            <div class="control-indicator">
                <h4 style="color: #16A34A; margin: 0;">CONTROLLER: {result['controller']}</h4>
                <p style="color: #6B7280; margin: 0.5rem 0;">
                    <strong>Criteria met: {', '.join(result['controller_criteria'])}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if result.get('tie_breaker_applied'):
                st.markdown('<div class="tie-breaker-box">', unsafe_allow_html=True)
                st.markdown("**⚖️ TIE-BREAKER APPLIED**")
                st.markdown("Both teams met 2+ criteria; controller selected via structured control score")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # State-flip capacity analysis
            st.markdown("#### 🔍 STATE-FLIP CAPACITY ANALYSIS")
            st.markdown(f"""
            <div class="state-flip-check">
                <h4 style="color: #DC2626; margin: 0;">OPPONENT: {result['opponent']}</h4>
                <p style="color: #6B7280; margin: 0.5rem 0;">
                    <strong>Escalation failures: {result['state_flip_failures']}/4 checks</strong>
                </p>
                <p style="color: #374151; margin: 0; font-size: 0.9rem;">
                    Lacks credible paths to flip match state
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Key metrics
            st.markdown("#### 📊 STRUCTURAL METRICS")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Expected Goals Analysis**")
                
                home_xg = result['key_metrics']['home_xg']
                away_xg = result['key_metrics']['away_xg']
                controller_xg = result['key_metrics']['controller_xg']
                opponent_xg = result['key_metrics']['opponent_xg']
                
                # Controller xG
                is_home_controller = result['controller'] == result['team_context']['home']
                controller_status = "status-success" if controller_xg >= 1.4 else "status-warning"
                st.markdown(f"""
                <div class="metric-row metric-row-controller">
                    <span>🎯 {result['controller']} (Controller):</span>
                    <span><strong>{controller_xg:.2f}</strong></span>
                    <span class="status-badge {controller_status}">{'≥1.4' if controller_xg >= 1.4 else '<1.4'}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Opponent xG
                opponent_status = "status-danger" if opponent_xg < 1.1 else "status-warning" if opponent_xg < 1.4 else "status-neutral"
                st.markdown(f"""
                <div class="metric-row">
                    <span>⚫ {result['opponent']}:</span>
                    <span><strong>{opponent_xg:.2f}</strong></span>
                    <span class="status-badge {opponent_status}">{'<1.1' if opponent_xg < 1.1 else '<1.4' if opponent_xg < 1.4 else '≥1.4'}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # xG Delta
                xg_delta = controller_xg - opponent_xg
                delta_status = "status-success" if xg_delta > 0.3 else "status-warning"
                st.markdown(f"""
                <div class="metric-row">
                    <span>📈 Control Delta:</span>
                    <span><strong>{xg_delta:+.2f}</strong></span>
                    <span class="status-badge {delta_status}">{'>+0.3' if xg_delta > 0.3 else '≤+0.3'}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">', unsafe_allow_html=True)
                st.markdown("**Match Context**")
                
                home_pos = result['team_context']['home_pos']
                away_pos = result['team_context']['away_pos']
                
                # Home team
                home_star = '⭐' if result['controller'] == home_team else '⚫'
                home_badge = 'status-success' if result['controller'] == home_team else 'status-neutral'
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0;">
                    <span>{home_team}:</span>
                    <span><strong>#{home_pos}</strong></span>
                    <span class="status-badge {home_badge}">{home_star}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Away team
                away_star = '⭐' if result['controller'] == away_team else '⚫'
                away_badge = 'status-success' if result['controller'] == away_team else 'status-neutral'
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0;">
                    <span>{away_team}:</span>
                    <span><strong>#{away_pos}</strong></span>
                    <span class="status-badge {away_badge}">{away_star}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # League average
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0; padding-top: 0.5rem; border-top: 1px solid #E5E7EB;">
                    <span>League Avg xG:</span>
                    <span><strong>{result['key_metrics']['league_avg_xg']:.2f}</strong></span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # NO DECLARATION
            st.markdown(f"""
            <div class="no-declaration-display">
                <div style="font-size: 1.2rem; color: #6B7280; margin-bottom: 1rem;">SYSTEM DECLARATION</div>
                <h1 style="color: #6B7280; margin: 1rem 0; font-size: 2.5rem; font-weight: 800;">NO DECLARATION</h1>
                <div style="font-size: 1.1rem; color: #374151; margin-bottom: 2rem;">
                    {result['reason']}
                </div>
                <div style="background: #6B7280; color: white; padding: 0.75rem 2rem; border-radius: 30px; display: inline-block; font-weight: 700; font-size: 1.1rem;">
                    SYSTEM SILENT
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # No capital authorization box
            st.markdown("""
            <div class="no-capital-box">
                <h3 style="margin: 0; color: white;">🚫 CAPITAL NOT AUTHORIZED</h3>
                <p style="margin: 0.5rem 0 0 0; color: #E5E7EB; font-size: 0.95rem;">
                    System has not declared STATE LOCKED. No capital deployment permitted.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show why if controller exists but no state lock
            if result['controller']:
                st.markdown("#### ⚠️ WHY NO STATE LOCK DECLARATION")
                st.markdown(f"""
                <div class="no-control-indicator">
                    <h4 style="color: #6B7280; margin: 0;">CONTROLLER IDENTIFIED: {result['controller']}</h4>
                    <p style="color: #6B7280; margin: 0.5rem 0;">
                        But STATE LOCK conditions not fully satisfied
                    </p>
                    <p style="color: #DC2626; margin: 0; font-size: 0.9rem;">
                        {result['reason']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Audit log
        with st.expander("📋 VIEW SYSTEM AUDIT LOG", expanded=True):
            for line in result['audit_log']:
                if '=' in line or '🔒' in line or 'STEP' in line:
                    st.markdown(f"**{line}**")
                elif '✅' in line or '❌' in line or '⚠️' in line or '🔍' in line:
                    st.markdown(f"**{line}**")
                elif '🎯' in line or '💰' in line:
                    st.markdown(f"**{line}**")
                elif line.startswith("•"):
                    st.markdown(f"`{line}`")
                elif line.strip():
                    st.markdown(line)
        
        # Export declaration
        st.markdown("---")
        st.markdown("#### 📤 Export Declaration Report")
        
        export_text = f"""BRUTBALL v6.1 - STATE LOCK DECLARATION REPORT
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM DECLARATION:
{result['declaration'] if result['state_locked'] else 'NO DECLARATION'}

CAPITAL AUTHORIZATION: {'AUTHORIZED' if result['state_locked'] else 'NOT AUTHORIZED'}

REASON:
{result['reason']}

{'CONTROLLER IDENTIFIED:' if result['controller'] else 'NO CONTROLLER IDENTIFIED:'}
{result['controller'] if result['controller'] else 'N/A'}
{', '.join(result['controller_criteria']) if result.get('controller_criteria') else 'N/A'}

{'OPPONENT STATE-FLIP FAILURES:' if result.get('state_flip_failures') else ''}
{str(result.get('state_flip_failures')) + '/4 checks failed' if result.get('state_flip_failures') else 'N/A'}

KEY METRICS:
Home xG: {result['key_metrics']['home_xg']:.2f}
Away xG: {result['key_metrics']['away_xg']:.2f}
Controller xG: {result['key_metrics']['controller_xg']:.2f if result.get('controller') else 'N/A'}
Opponent xG: {result['key_metrics']['opponent_xg']:.2f if result.get('opponent') else 'N/A'}
League Avg xG: {result['key_metrics']['league_avg_xg']:.2f}

SYSTEM AUDIT LOG:
{chr(10).join(result['audit_log'])}

===========================================
BRUTBALL v6.1 - State Lock Declaration Engine
Declarative • Binary • No probabilities • No confidence scales
Capital flows only on STATE LOCKED declaration
        """
        
        st.download_button(
            label="📥 Download Declaration Report",
            data=export_text,
            file_name=f"brutball_v6.1_state_lock_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL v6.1 – State Lock Declaration Engine</strong></p>
        <p>Declarative system • Binary authorization • No probabilities • No confidence scales</p>
        <p>STATE LOCKED or NO DECLARATION – nothing else matters</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
