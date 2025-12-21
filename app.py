import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="Brutball v6.0 - Match-State Engine",
    page_icon="⚽",
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
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    .axiom-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #374151;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    .control-badge {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 8px solid #16A34A;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .no-control-badge {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border-left: 8px solid #6B7280;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .action-display {
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .axiom-card {
        padding: 1rem;
        border-radius: 8px;
        background: white;
        border-left: 4px solid #10B981;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        margin: 0.5rem 0;
        border: 1px solid #E5E7EB;
    }
    .league-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.25rem;
    }
    .confidence-bar {
        height: 8px;
        background: linear-gradient(90deg, #EF4444 0%, #F59E0B 50%, #10B981 100%);
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .criteria-box {
        padding: 0.75rem;
        background: #F8FAFC;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #3B82F6;
    }
    </style>
""", unsafe_allow_html=True)

# =================== BRUTBALL v6.0 CORE ENGINE ===================
class BrutballStateEngine:
    """
    BRUTBALL v6.0 - Match-State Identification Engine
    No hype. No redundancy. Every axiom has a job and failure condition.
    """
    
    # AXIOM 2: GAME-STATE CONTROL IS PRIMARY
    @staticmethod
    def identify_game_state_controller(home_data: Dict, away_data: Dict,
                                     home_name: str, away_name: str,
                                     league_avg_xg: float) -> Tuple[Optional[str], List[str], Dict]:
        """Identify which team controls game state."""
        rationale = []
        home_score = 0
        away_score = 0
        
        # Track which criteria each team meets
        home_criteria = []
        away_criteria = []
        
        # CRITERION 1: Home advantage + attack ≥ league average +20%
        home_xg = home_data.get('home_xg_per_match', 0)
        if home_xg >= league_avg_xg * 1.2:
            home_score += 1
            home_criteria.append(f"Home attack {home_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
            rationale.append(f"✅ {home_name}: Home attack {home_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
        
        away_xg = away_data.get('away_xg_per_match', 0)
        if away_xg >= league_avg_xg * 1.2:
            away_score += 1
            away_criteria.append(f"Away attack {away_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
            rationale.append(f"✅ {away_name}: Away attack {away_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
        
        # CRITERION 2: Negative momentum
        def has_negative_momentum(form: str) -> bool:
            if len(form) < 2:
                return False
            return form.endswith('LL') or form.endswith('L')
        
        home_form = home_data.get('form_last_5_overall', '')
        if has_negative_momentum(home_form):
            away_score += 1
            away_criteria.append(f"Opponent {home_name} negative momentum: {home_form}")
            rationale.append(f"✅ {away_name}: {home_name} has negative momentum ({home_form})")
        
        away_form = away_data.get('form_last_5_overall', '')
        if has_negative_momentum(away_form):
            home_score += 1
            home_criteria.append(f"Opponent {away_name} negative momentum: {away_form}")
            rationale.append(f"✅ {home_name}: {away_name} has negative momentum ({away_form})")
        
        # CRITERION 3: Repeatable scoring method
        def has_repeatable_scoring(team_data: Dict, is_home: bool) -> bool:
            if is_home:
                setpiece = team_data.get('home_setpiece_pct', 0)
                openplay = team_data.get('home_openplay_pct', 0)
            else:
                setpiece = team_data.get('away_setpiece_pct', 0)
                openplay = team_data.get('away_openplay_pct', 0)
            return setpiece > 0.25 or openplay > 0.65
        
        if has_repeatable_scoring(home_data, is_home=True):
            home_score += 1
            home_criteria.append("Repeatable scoring method")
            rationale.append(f"✅ {home_name}: Repeatable scoring method")
        
        if has_repeatable_scoring(away_data, is_home=False):
            away_score += 1
            away_criteria.append("Repeatable scoring method")
            rationale.append(f"✅ {away_name}: Repeatable scoring method")
        
        # CRITERION 4: Opponent concedes early frequently
        def concedes_early(team_data: Dict, is_home: bool) -> bool:
            if is_home:
                goals = team_data.get('home_goals_conceded', 0)
                matches = team_data.get('home_matches_played', 1)
            else:
                goals = team_data.get('away_goals_conceded', 0)
                matches = team_data.get('away_matches_played', 1)
            return (goals / matches) > 1.5 if matches > 0 else False
        
        if concedes_early(away_data, is_home=False):
            home_score += 1
            home_criteria.append(f"Opponent {away_name} concedes early")
            rationale.append(f"✅ {home_name}: {away_name} concedes early")
        
        if concedes_early(home_data, is_home=True):
            away_score += 1
            away_criteria.append(f"Opponent {home_name} concedes early")
            rationale.append(f"✅ {away_name}: {home_name} concedes early")
        
        # DETERMINE CONTROLLER (v6.0: Need at least 2 criteria)
        criteria_met = {
            'home': {'count': home_score, 'details': home_criteria},
            'away': {'count': away_score, 'details': away_criteria}
        }
        
        if home_score >= 2 and home_score > away_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {home_name} (2+ criteria met: {home_score}/4)")
            rationale.append(f"   ⚙️ Criteria met: {', '.join(home_criteria)}")
            return home_name, rationale, criteria_met
        elif away_score >= 2 and away_score > home_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {away_name} (2+ criteria met: {away_score}/4)")
            rationale.append(f"   ⚙️ Criteria met: {', '.join(away_criteria)}")
            return away_name, rationale, criteria_met
        else:
            rationale.append(f"⚠️ NO CLEAR GAME-STATE CONTROLLER")
            rationale.append(f"   • {home_name}: {home_score}/4 criteria (need 2+)")
            if home_criteria:
                rationale.append(f"     Met: {', '.join(home_criteria)}")
            rationale.append(f"   • {away_name}: {away_score}/4 criteria (need 2+)")
            if away_criteria:
                rationale.append(f"     Met: {', '.join(away_criteria)}")
            return None, rationale, criteria_met
    
    # AXIOM 4: GOALS ARE A CONSEQUENCE, NOT A STRATEGY
    @staticmethod
    def evaluate_goals_environment(home_data: Dict, away_data: Dict,
                                 controller: Optional[str]) -> Tuple[bool, List[str]]:
        """Evaluate if goals environment exists."""
        rationale = []
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # Base conditions
        if combined_xg < 2.8:
            rationale.append(f"❌ Combined xG {combined_xg:.2f} < 2.8 (AXIOM 4: Insufficient capacity)")
            return False, rationale
        
        if max(home_xg, away_xg) < 1.6:
            rationale.append(f"❌ No elite attack (max: {max(home_xg, away_xg):.2f} < 1.6)")
            return False, rationale
        
        # AXIOM 6: DUAL FRAGILITY ≠ DUAL CHAOS
        home_crisis = home_data.get('goals_conceded_last_5', 0) >= 12
        away_crisis = away_data.get('goals_conceded_last_5', 0) >= 12
        
        if home_crisis and away_crisis and controller is None:
            # Check if both have intent
            if home_xg > 1.4 and away_xg > 1.4:
                rationale.append("✅ DUAL FRAGILITY + DUAL INTENT → Chaos goals (AXIOM 6 satisfied)")
                return True, rationale
            else:
                rationale.append("❌ Dual fragility but insufficient intent (AXIOM 6: No chaos)")
                return False, rationale
        
        rationale.append(f"✅ GOALS ENVIRONMENT: Combined xG {combined_xg:.2f} ≥ 2.8, Elite attack present")
        return True, rationale
    
    # AXIOM 5: ONE-SIDED CONTROL OVERRIDE
    @staticmethod
    def apply_control_override(controller: str, opponent_name: str,
                             controller_data: Dict, opponent_data: Dict,
                             has_goals_env: bool, combined_xg: float) -> Tuple[str, float, List[str]]:
        """Apply one-sided control override (AXIOM 5)."""
        rationale = []
        
        action = f"BACK {controller}"
        confidence = 8.0
        
        rationale.append(f"🎯 ONE-SIDED CONTROL OVERRIDE (AXIOM 5)")
        rationale.append(f"   • Controller: {controller}")
        rationale.append(f"   • Opponent: {opponent_name}")
        
        # Check if opponent must chase (capacity)
        opponent_xg = opponent_data.get('away_xg_per_match' if 'away' in opponent_name.lower() else 'home_xg_per_match', 0)
        
        if has_goals_env:
            action += " & OVER 2.5"
            confidence = 7.5
            rationale.append(f"   • Controller + goals environment → Back & Over")
            rationale.append(f"   • Opponent chase capacity: {opponent_xg:.2f} xG")
        else:
            # Low xG but controller exists
            action += " (Clean win expected)"
            confidence = 8.5 if combined_xg < 2.4 else 8.0
            rationale.append(f"   • AXIOM 4: Low combined xG ({combined_xg:.2f}) but controller exists")
            rationale.append(f"   • Controller can win without goals bias")
            rationale.append(f"   • Opponent lacks chase capacity: {opponent_xg:.2f} xG < 1.3")
        
        return action, confidence, rationale
    
    # AXIOM 7: FAVORITES FAIL STRUCTURALLY
    @staticmethod
    def evaluate_favorite_fade(favorite: str, underdog: str,
                             controller: Optional[str],
                             favorite_data: Dict, underdog_data: Dict) -> Tuple[bool, List[str]]:
        """Evaluate if favorite can be faded (AXIOM 7)."""
        rationale = []
        
        if controller == favorite:
            rationale.append(f"❌ CANNOT FADE {favorite} (AXIOM 7: Favorite controls state)")
            return False, rationale
        
        if controller == underdog:
            rationale.append(f"✅ CAN FADE {favorite} (AXIOM 7: Underdog controls state)")
            rationale.append(f"   • {underdog} has game-state control")
            return True, rationale
        
        if controller is None:
            # Check if underdog can impose tempo
            underdog_xg = underdog_data.get('away_xg_per_match' if 'away' in underdog.lower() else 'home_xg_per_match', 0)
            if underdog_xg >= 1.2:
                rationale.append(f"⚠️ CONSIDER FADING {favorite}")
                rationale.append(f"   • No clear controller but {underdog} can impose tempo")
                rationale.append(f"   • {underdog} xG: {underdog_xg:.2f} ≥ 1.2")
                return True, rationale
        
        rationale.append(f"❌ CANNOT FADE {favorite}")
        rationale.append(f"   • No structural advantage for underdog")
        return False, rationale
    
    # AXIOM 8: UNDER IS A CONTROL OUTCOME
    @staticmethod
    def evaluate_under_conditions(controller: Optional[str],
                                controller_data: Dict,
                                opponent_data: Dict,
                                combined_xg: float) -> Tuple[bool, List[str]]:
        """Evaluate if Under conditions exist (AXIOM 8)."""
        rationale = []
        
        if controller is None:
            rationale.append("❌ No controller → Under not a control outcome")
            return False, rationale
        
        # Check opponent chase capacity
        opponent_xg = opponent_data.get('away_xg_per_match' if 'away' in str(controller_data.get('team', '')) else 'home_xg_per_match', 0)
        
        if opponent_xg < 1.1 and combined_xg < 2.4:
            rationale.append(f"✅ UNDER CONDITIONS (AXIOM 8)")
            rationale.append(f"   • Controller: {controller}")
            rationale.append(f"   • Opponent lacks chase capacity: {opponent_xg:.2f} xG < 1.1")
            rationale.append(f"   • Combined xG {combined_xg:.2f} < 2.4")
            rationale.append(f"   • Controller can win without urgency")
            return True, rationale
        
        rationale.append(f"❌ Insufficient Under conditions")
        rationale.append(f"   • Opponent xG: {opponent_xg:.2f} (needs < 1.1)")
        rationale.append(f"   • Combined xG: {combined_xg:.2f} (needs < 2.4)")
        return False, rationale
    
    # AXIOM 9: AVOID IS RARE AND EXPLICIT
    @staticmethod
    def evaluate_avoid_conditions(controller: Optional[str],
                                home_xg: float, away_xg: float,
                                league_avg_xg: float) -> Tuple[bool, List[str]]:
        """Evaluate if Avoid conditions exist (AXIOM 9)."""
        rationale = []
        
        if controller is not None:
            rationale.append(f"❌ Controller exists: {controller} → Not Avoid")
            return False, rationale
        
        # Check if attacks are below league average
        if home_xg > league_avg_xg * 0.9 or away_xg > league_avg_xg * 0.9:
            rationale.append(f"❌ At least one competent attack → Not Avoid")
            rationale.append(f"   • Home: {home_xg:.2f}, Away: {away_xg:.2f}")
            rationale.append(f"   • League avg: {league_avg_xg:.2f}")
            return False, rationale
        
        # Check combined xG
        combined_xg = home_xg + away_xg
        if combined_xg < 2.4:
            rationale.append(f"✅ AVOID CONDITIONS MET (AXIOM 9)")
            rationale.append(f"   • No game-state controller")
            rationale.append(f"   • Attacks below league average")
            rationale.append(f"   • Combined xG: {combined_xg:.2f} < 2.4")
            return True, rationale
        
        rationale.append(f"❌ Combined xG suggests potential: {combined_xg:.2f}")
        return False, rationale
    
    # AXIOM 10: CAPITAL FOLLOWS STATE CONFIDENCE
    @staticmethod
    def calculate_capital_allocation(controller: Optional[str],
                                   confidence: float,
                                   has_goals_env: bool) -> float:
        """Calculate stake percentage (AXIOM 10)."""
        if controller:
            if confidence >= 8.0:
                return 2.0  # Full allocation
            elif confidence >= 7.0:
                return 1.5  # Strong allocation
            elif confidence >= 6.0:
                return 1.0  # Moderate allocation
            else:
                return 0.5  # Small allocation
        elif has_goals_env:
            return 0.5  # Minimal allocation for goals only
        else:
            return 0.0  # Avoid
    
    # MAIN DECISION TREE
    @classmethod
    def execute_v6_tree(cls, home_data: Dict, away_data: Dict,
                       home_name: str, away_name: str,
                       league_avg_xg: float) -> Dict:
        """Execute v6.0 decision tree."""
        
        rationale = ["🧠 BRUTBALL v6.0 DECISION TREE EXECUTION"]
        decision_steps = []
        
        # Determine favorite (by position)
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
        favorite_data = home_data if favorite == home_name else away_data
        underdog_data = away_data if favorite == home_name else home_data
        
        rationale.append(f"⭐ Favorite: {favorite} (#{min(home_pos, away_pos)})")
        rationale.append(f"⚫ Underdog: {underdog} (#{max(home_pos, away_pos)})")
        rationale.append("")  # Spacer
        
        # STEP 1: Identify Game-State Controller (AXIOM 2)
        rationale.append("📋 STEP 1: IDENTIFY GAME-STATE CONTROLLER (AXIOM 2)")
        controller, control_rationale, criteria_met = cls.identify_game_state_controller(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        rationale.extend(control_rationale)
        decision_steps.append(f"1. Controller: {controller if controller else 'None'}")
        
        # Get combined xG for later use
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # STEP 2: Evaluate Goals Environment (AXIOM 4)
        rationale.append("")
        rationale.append("📋 STEP 2: EVALUATE GOALS ENVIRONMENT (AXIOM 4)")
        has_goals_env, goals_rationale = cls.evaluate_goals_environment(
            home_data, away_data, controller
        )
        rationale.extend(goals_rationale)
        decision_steps.append(f"2. Goals Environment: {'Yes' if has_goals_env else 'No'}")
        
        # STEP 3: Apply Decision Logic
        primary_action = "ANALYZING"
        confidence = 5.0
        secondary_signal = None
        detailed_logic = []
        
        rationale.append("")
        rationale.append("📋 STEP 3: APPLY DECISION LOGIC")
        
        if controller:
            # CASE A: Controller exists → AXIOM 5 override
            opponent = away_name if controller == home_name else home_name
            opponent_data = away_data if controller == home_name else home_data
            controller_data = home_data if controller == home_name else away_data
            
            action, conf, override_rationale = cls.apply_control_override(
                controller, opponent, controller_data, opponent_data,
                has_goals_env, combined_xg
            )
            rationale.extend(override_rationale)
            detailed_logic.extend(override_rationale)
            primary_action = action
            confidence = conf
            
            # Check if controller is underdog vs favorite
            if controller == underdog:
                rationale.append(f"   • Note: Controller is underdog (control > status)")
                secondary_signal = "Underdog controls state"
            
            decision_steps.append(f"3a. One-Sided Control Override (AXIOM 5)")
            
        elif has_goals_env:
            # CASE B: No controller but goals environment
            rationale.append("🔍 No controller but goals environment exists")
            
            can_fade, fade_rationale = cls.evaluate_favorite_fade(
                favorite, underdog, controller, favorite_data, underdog_data
            )
            rationale.extend(fade_rationale)
            detailed_logic.extend(fade_rationale)
            
            if can_fade:
                primary_action = f"FADE {favorite} & OVER 2.5"
                confidence = 6.5
                secondary_signal = f"{underdog} or DRAW (AXIOM 7)"
                decision_steps.append(f"3b. Favorite Fade (AXIOM 7)")
            else:
                primary_action = "OVER 2.5 GOALS"
                confidence = 6.0
                secondary_signal = "Goals only, no side"
                decision_steps.append(f"3b. Goals Only")
        
        else:
            # CASE C: Neither controller nor goals
            rationale.append("🔍 No controller, no goals environment")
            
            # Check Under conditions (AXIOM 8)
            if controller:  # This shouldn't happen but safety check
                can_under, under_rationale = cls.evaluate_under_conditions(
                    controller,
                    home_data if controller == home_name else away_data,
                    away_data if controller == home_name else home_data,
                    combined_xg
                )
                if can_under:
                    rationale.extend(under_rationale)
                    primary_action = "UNDER 2.5 GOALS"
                    confidence = 5.5
                    secondary_signal = "Low-scoring control outcome (AXIOM 8)"
                    decision_steps.append(f"3c. Under Conditions (AXIOM 8)")
                else:
                    # Check Avoid conditions (AXIOM 9)
                    should_avoid, avoid_rationale = cls.evaluate_avoid_conditions(
                        controller, home_xg, away_xg, league_avg_xg
                    )
                    if should_avoid:
                        rationale.extend(avoid_rationale)
                        primary_action = "AVOID"
                        confidence = 0.0
                        secondary_signal = "Preserve capital (AXIOM 9)"
                        decision_steps.append(f"3c. Avoid (AXIOM 9)")
                    else:
                        primary_action = "UNDER 2.5 GOALS"
                        confidence = 5.0
                        secondary_signal = "Fallback: Low scoring expected"
                        decision_steps.append(f"3c. Fallback Under")
            else:
                # No controller at all
                should_avoid, avoid_rationale = cls.evaluate_avoid_conditions(
                    controller, home_xg, away_xg, league_avg_xg
                )
                if should_avoid:
                    rationale.extend(avoid_rationale)
                    primary_action = "AVOID"
                    confidence = 0.0
                    secondary_signal = "No edge identified (AXIOM 9)"
                    decision_steps.append(f"3c. Avoid (AXIOM 9)")
                else:
                    primary_action = "UNDER 2.5 GOALS"
                    confidence = 5.0
                    secondary_signal = "Low-scoring expected"
                    decision_steps.append(f"3c. Default Under")
        
        # STEP 4: Calculate Stake (AXIOM 10)
        stake_pct = cls.calculate_capital_allocation(controller, confidence, has_goals_env)
        rationale.append("")
        rationale.append(f"📋 STEP 4: CAPITAL ALLOCATION (AXIOM 10)")
        rationale.append(f"   • Controller present: {'Yes' if controller else 'No'}")
        rationale.append(f"   • Confidence score: {confidence}/10")
        rationale.append(f"   • Goals environment: {'Yes' if has_goals_env else 'No'}")
        rationale.append(f"   → Recommended stake: {stake_pct}% of bankroll")
        
        # Compile final output
        rationale.append("")
        rationale.append("🎯 FINAL DECISION")
        rationale.append(f"   • Action: {primary_action}")
        rationale.append(f"   • Confidence: {confidence}/10")
        rationale.append(f"   • Stake: {stake_pct}%")
        
        if secondary_signal:
            rationale.append(f"   • Logic: {secondary_signal}")
        
        return {
            'match': f"{home_name} vs {away_name}",
            'controller': controller,
            'has_goals_env': has_goals_env,
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'secondary_signal': secondary_signal,
            'rationale': rationale,
            'decision_steps': decision_steps,
            'criteria_met': criteria_met,
            'team_context': {
                'favorite': favorite,
                'underdog': underdog,
                'home': home_name,
                'away': away_name
            },
            'key_metrics': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'combined_xg': combined_xg,
                'home_pos': home_pos,
                'away_pos': away_pos,
                'league_avg_xg': league_avg_xg
            }
        }

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load, validate, and prepare the dataset for selected league."""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple data source locations
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
        ]
        
        df = None
        source_used = ""
        
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                source_used = source
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
    """Calculate all derived metrics from YOUR actual CSV columns."""
    
    # 1. Calculate home/away goals conceded
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
    
    # 2. Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # 3. Goal type percentages
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_goals_scored'].replace(0, np.nan)
    
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_goals_scored'].replace(0, np.nan)
    
    # 4. Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

# =================== STREAMLIT UI ===================
def render_header():
    """Render main header."""
    st.markdown('<div class="main-header">🧠 BRUTBALL v6.0 - MATCH-STATE IDENTIFICATION ENGINE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
        <p><strong>No hype. No redundancy. Every axiom has a job and failure condition.</strong></p>
        <p>Controller Identification → One-Sided Override → Capital Allocation</p>
    </div>
    """, unsafe_allow_html=True)

def render_league_selector():
    """Render league selection buttons."""
    st.markdown('<div class="axiom-header">🌍 SELECT LEAGUE</div>', unsafe_allow_html=True)
    
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
    
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    config = LEAGUES[st.session_state.selected_league]
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 10px;
        background: {config['color']}15;
        border-left: 6px solid {config['color']};
        margin: 1rem 0;
        text-align: center;
    ">
        <h3 style="color: {config['color']}; margin: 0;">
            {config['display_name']} • {config['country']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.selected_league

def render_match_selector(df: pd.DataFrame, league_name: str):
    """Render team selection."""
    st.markdown('<div class="axiom-header">🏟️ MATCH ANALYSIS</div>', unsafe_allow_html=True)
    
    config = LEAGUES[league_name]
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {config['color']}10;
        border-radius: 8px;
        border: 1px solid {config['color']}30;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        color: {config['color']};
    ">
        {config['display_name']} • {len(df)} Teams Loaded
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 HOME TEAM", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("✈️ AWAY TEAM", away_options)
    
    return home_team, away_team

def render_v6_axioms():
    """Display v6.0 axioms in correct order."""
    st.markdown('<div class="axiom-header">🔐 BRUTBALL v6.0 AXIOMS (SEQUENTIAL)</div>', unsafe_allow_html=True)
    
    axioms = [
        ("1", "FOOTBALL IS NOT SYMMETRIC", "Structural balance ≠ match balance"),
        ("2", "GAME-STATE CONTROL IS PRIMARY", "Team that imposes tempo after scoring owns match"),
        ("3", "STRUCTURAL METRICS ARE CONTEXTUAL", "xG, form, crisis only matter after control known"),
        ("4", "GOALS ARE A CONSEQUENCE, NOT A STRATEGY", "Goals follow state; they do not define it"),
        ("5", "ONE-SIDED CONTROL OVERRIDE", "When control is asymmetric, direction beats volume"),
        ("6", "DUAL FRAGILITY ≠ DUAL CHAOS", "Two bad defenses don't guarantee wild match"),
        ("7", "FAVORITES FAIL FOR STRUCTURAL REASONS", "Not because favorites, but lack GSC"),
        ("8", "UNDER IS A CONTROL OUTCOME", "Controller wins without urgency"),
        ("9", "AVOID IS RARE AND EXPLICIT", "Only when no state advantage exists"),
        ("10", "CAPITAL FOLLOWS STATE CONFIDENCE", "Stake size reflects control clarity")
    ]
    
    cols = st.columns(2)
    for idx, (num, title, desc) in enumerate(axioms):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="axiom-card">
            <strong>AXIOM {num}: {title}</strong><br>
            <small style="color: #6B7280;">{desc}</small>
            </div>
            """, unsafe_allow_html=True)

def render_decision_tree():
    """Display decision tree."""
    st.markdown('<div class="axiom-header">🧠 v6.0 DECISION TREE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        padding: 1.5rem;
        background: #F8FAFC;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
    ">
    <strong>1. IDENTIFY GAME-STATE CONTROLLER (AXIOM 2)</strong><br>
    &nbsp;&nbsp;• Need 2+ of 4 criteria<br>
    &nbsp;&nbsp;• If exists → Proceed to Step 3<br>
    <br>
    <strong>2. EVALUATE GOALS ENVIRONMENT (AXIOM 4)</strong><br>
    &nbsp;&nbsp;• Combined xG ≥ 2.8<br>
    &nbsp;&nbsp;• Elite attack (≥1.6 xG)<br>
    &nbsp;&nbsp;• Dual fragility check (AXIOM 6)<br>
    <br>
    <strong>3. APPLY DECISION LOGIC</strong><br>
    &nbsp;&nbsp;<strong>A.</strong> Controller exists → BACK CONTROLLER (AXIOM 5)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• +Goals env → & OVER 2.5<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• -Goals env → Clean win expected<br>
    <br>
    &nbsp;&nbsp;<strong>B.</strong> No controller + Goals env →<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• Can fade favorite? → FADE & OVER (AXIOM 7)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• Cannot fade → OVER only<br>
    <br>
    &nbsp;&nbsp;<strong>C.</strong> No controller + No goals →<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• Under conditions? → UNDER (AXIOM 8)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• Avoid conditions? → AVOID (AXIOM 9)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• Fallback → UNDER<br>
    <br>
    <strong>4. ALLOCATE CAPITAL (AXIOM 10)</strong><br>
    &nbsp;&nbsp;• Controller clarity determines stake size<br>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    
    render_header()
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # Select league
    selected_league = render_league_selector()
    
    # Load data
    with st.spinner(f"Loading {LEAGUES[selected_league]['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Please check if CSV files exist in the 'leagues/' directory.")
        return
    
    # Calculate league average xG
    if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
        league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
    else:
        league_avg_xg = 1.3
    
    # Select match
    home_team, away_team = render_match_selector(df, selected_league)
    
    # Show axioms and decision tree
    render_v6_axioms()
    render_decision_tree()
    
    # Analysis button
    if st.button("🚀 EXECUTE MATCH-STATE ANALYSIS", type="primary", use_container_width=True):
        
        # Get team data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Execute v6.0 engine
        result = BrutballStateEngine.execute_v6_tree(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display controller identification with criteria explanation
        config = LEAGUES[selected_league]
        if result['controller']:
            criteria_info = result['criteria_met']
            controller_name = result['controller']
            
            # Determine if controller is home or away
            is_home_controller = controller_name == result['team_context']['home']
            key = 'home' if is_home_controller else 'away'
            
            criteria_data = criteria_info[key]
            criteria_count = criteria_data['count']
            criteria_details = criteria_data['details']
            
            st.markdown(f"""
            <div class="control-badge">
            <h2>🎯 GAME-STATE CONTROLLER IDENTIFIED (AXIOM 2)</h2>
            <h1 style="color: #16A34A; margin: 0.5rem 0;">{controller_name}</h1>
            <p style="color: #6B7280; margin-bottom: 0.5rem;">
                <strong>2+ criteria met: {criteria_count}/4</strong> • Controls tempo, scoring, match flow
            </p>
            <div class="criteria-box">
                <strong>Criteria Met:</strong><br>
                {chr(10).join(['• ' + crit for crit in criteria_details])}
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Note if controller is underdog
            if result['controller'] == result['team_context']['underdog']:
                st.info(f"📌 **Note:** {result['controller']} is underdog but controls game state (Control > Status)")
        else:
            st.markdown(f"""
            <div class="no-control-badge">
            <h2>⚠️ NO CLEAR GAME-STATE CONTROLLER</h2>
            <p style="color: #6B7280;">Neither team meets 2+ control criteria (AXIOM 2)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display primary action
        action = result['primary_action']
        if "BACK" in action:
            color = "#16A34A"
            action_type = "Controller Backing"
        elif "OVER" in action or "FADE" in action:
            color = "#EA580C"
            action_type = "Goals/Fade"
        elif "UNDER" in action:
            color = "#2563EB"
            action_type = "Under/Defensive"
        else:
            color = "#6B7280"
            action_type = "Avoid/No Action"
        
        st.markdown(f"""
        <div class="action-display" style="border: 3px solid {color};">
            <h3 style="color: #374151; margin: 0 0 0.5rem 0;">PRIMARY ACTION</h3>
            <h1 style="color: {color}; margin: 0;">{action}</h1>
            <p style="color: {color}80; margin: 0.5rem 0 1.5rem 0;">{action_type}</p>
            <div style="display: flex; justify-content: center;">
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">State Confidence</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {color};">{result['confidence']}/10</div>
                </div>
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">Capital Allocation</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #059669;">{result['stake_pct']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence bar with explanation
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="color: #6B7280; font-size: 0.9rem;">State Confidence (AXIOM 10)</span>
                <span style="font-weight: 600; color: {color}">{result['confidence']}/10</span>
            </div>
            <div class="confidence-bar" style="width: {result['confidence'] * 10}%;"></div>
            <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">
                Based on controller clarity: {'Clear controller' if result['controller'] else 'No clear controller'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display decision steps
        st.markdown("### 📋 DECISION STEPS")
        for step in result['decision_steps']:
            st.markdown(f"- {step}")
        
        # Display rationale
        with st.expander("🧠 VIEW COMPLETE RATIONALE", expanded=True):
            for line in result['rationale']:
                if '🧠' in line or '🎯' in line or '📋' in line:
                    st.markdown(f"**{line}**")
                elif '✅' in line or '❌' in line or '⚠️' in line:
                    st.markdown(f"**{line}**")
                elif line.startswith("   •") or line.startswith("   →"):
                    st.markdown(f"`{line}`")
                elif line.strip():
                    st.markdown(line)
        
        # Key metrics with explanations
        st.markdown('<div class="axiom-header">📊 KEY METRICS & CONTEXT</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### ⚽ Expected Goals (AXIOM 4)")
            st.metric("Home xG/Match", f"{result['key_metrics']['home_xg']:.2f}")
            st.metric("Away xG/Match", f"{result['key_metrics']['away_xg']:.2f}")
            st.metric("Combined xG", f"{result['key_metrics']['combined_xg']:.2f}",
                     delta=f"{'≥2.8' if result['key_metrics']['combined_xg'] >= 2.8 else '<2.8'}")
            st.metric("League Average", f"{result['key_metrics']['league_avg_xg']:.2f}")
            if result['key_metrics']['combined_xg'] < 2.8 and result['controller']:
                st.info("**AXIOM 4 Note:** Low xG but controller exists → Clean win possible")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### 🏆 Team Context (AXIOM 7)")
            team_context = result['team_context']
            home_display = f"{team_context['home']} {'⭐' if team_context['favorite'] == team_context['home'] else '⚫'}"
            away_display = f"{team_context['away']} {'⭐' if team_context['favorite'] == team_context['away'] else '⚫'}"
            
            st.metric(home_display, f"#{result['key_metrics']['home_pos']}")
            st.metric(away_display, f"#{result['key_metrics']['away_pos']}")
            st.metric("Favorite", team_context['favorite'])
            st.metric("Underdog", team_context['underdog'])
            if result['controller'] and result['controller'] == team_context['underdog']:
                st.info("**AXIOM 7 Note:** Underdog controls state → Control > Status")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        # Get controller criteria info safely
        controller_criteria_info = ""
        if result['controller']:
            # Determine if controller is home or away
            is_home_controller = result['controller'] == result['team_context']['home']
            key = 'home' if is_home_controller else 'away'
            criteria_data = result['criteria_met'][key]
            controller_criteria_info = f"{criteria_data['count']}/4 met"
        else:
            controller_criteria_info = "0/4 met"
        
        export_text = f"""
BRUTBALL v6.0 - MATCH-STATE ANALYSIS
=====================================
League: {selected_league}
Match: {result['match']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

GAME-STATE IDENTIFICATION (AXIOM 2):
• Controller: {result['controller'] if result['controller'] else 'NONE'}
• Controller Criteria: {controller_criteria_info}
• Goals Environment: {result['has_goals_env']} (AXIOM 4)

TEAM CONTEXT:
• Favorite: {result['team_context']['favorite']} (#{min(result['key_metrics']['home_pos'], result['key_metrics']['away_pos'])})
• Underdog: {result['team_context']['underdog']} (#{max(result['key_metrics']['home_pos'], result['key_metrics']['away_pos'])})
• Control > Status: {'YES' if result['controller'] and result['controller'] == result['team_context']['underdog'] else 'NO'}

DECISION:
• Primary Action: {result['primary_action']}
• Confidence: {result['confidence']}/10 (AXIOM 10)
• Stake: {result['stake_pct']}% of bankroll
• Secondary Logic: {result['secondary_signal'] if result['secondary_signal'] else 'N/A'}

KEY METRICS:
• Home xG: {result['key_metrics']['home_xg']:.2f}
• Away xG: {result['key_metrics']['away_xg']:.2f}
• Combined xG: {result['key_metrics']['combined_xg']:.2f} ({'≥2.8' if result['key_metrics']['combined_xg'] >= 2.8 else '<2.8'})
• League Avg xG: {result['key_metrics']['league_avg_xg']:.2f}

DECISION STEPS:
{chr(10).join(['• ' + step for step in result['decision_steps']])}

RATIONALE:
{chr(10).join(result['rationale'])}

=====================================
Brutball v6.0 - Match-State Identification Engine
Controller (2+ criteria) → One-Sided Override → Capital Allocation
        """
        
        st.download_button(
            label="📥 Download Complete Analysis",
            data=export_text,
            file_name=f"brutball_v6_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Brutball v6.0 - Match-State Identification Engine</strong></p>
        <p>Football reality identification. Controller (2+ criteria) → One-Sided Override → Capital Allocation.</p>
        <p>No forced bets. No chaos assumptions. Every axiom has a job and failure condition.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
