import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="Brutball v6.0 - Match-State Identification",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== MINIMAL CSS ===================
st.markdown("""
    <style>
    .state-identifier {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    .axiom-card {
        padding: 1rem;
        border-radius: 8px;
        background: white;
        border-left: 4px solid #10B981;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .control-badge {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 6px solid #16A34A;
        margin: 1rem 0;
    }
    .no-control-badge {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border-left: 6px solid #6B7280;
        margin: 1rem 0;
    }
    .warning-badge {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-left: 6px solid #F59E0B;
        margin: 1rem 0;
    }
    .metric-display {
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        padding: 0.5rem;
        background: #F8FAFC;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    .decision-step {
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3B82F6;
        background: #F8FAFC;
    }
    </style>
""", unsafe_allow_html=True)

# =================== BRUTBALL v6.0 AXIOMS ===================
class BrutballStateEngine:
    """
    v6.0 - Match-State Identification Engine
    No hype. No redundancy. Every axiom has a job and failure condition.
    """
    
    # ========== AXIOM 1 ==========
    @staticmethod
    def football_is_not_symmetric(home_attack: float, away_attack: float,
                                home_form: str, away_form: str) -> Tuple[bool, List[str]]:
        """
        AXIOM 1: FOOTBALL IS NOT SYMMETRIC
        xG parity does not imply outcome parity.
        """
        rationale = []
        
        # Structural check
        attack_diff = abs(home_attack - away_attack)
        
        if attack_diff < 0.2 and home_attack > 1.3 and away_attack > 1.3:
            rationale.append("⚖️ Structural balance present")
            rationale.append(f"  • Attack difference: {attack_diff:.2f} xG")
            rationale.append("  • Both attacks > 1.30 xG")
            symmetric = True
        else:
            symmetric = False
        
        return symmetric, rationale
    
    # ========== AXIOM 2 ==========
    @staticmethod
    def identify_game_state_controller(home_data: Dict, away_data: Dict,
                                     home_name: str, away_name: str,
                                     league_avg_xg: float) -> Tuple[Optional[str], List[str]]:
        """
        AXIOM 2: GAME-STATE CONTROL IS PRIMARY
        Returns which team controls state, or None if no clear controller.
        """
        rationale = []
        home_score = 0
        away_score = 0
        
        # CRITERION 1: Home advantage + attack ≥ league average +20%
        home_xg = home_data.get('home_xg_per_match', 0)
        if home_xg >= league_avg_xg * 1.2:
            home_score += 1
            rationale.append(f"✅ {home_name}: Home attack {home_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
        
        away_xg = away_data.get('away_xg_per_match', 0)
        if away_xg >= league_avg_xg * 1.2:
            away_score += 1
            rationale.append(f"✅ {away_name}: Away attack {away_xg:.2f} ≥ {league_avg_xg*1.2:.2f}")
        
        # CRITERION 2: Negative momentum or late collapses
        def has_negative_momentum(form: str) -> bool:
            if len(form) < 3:
                return False
            last_three = str(form)[-3:]
            return last_three.count('L') >= 2 or last_three == 'LLD' or last_three == 'LDL'
        
        if has_negative_momentum(home_data.get('form_last_5_overall', '')):
            away_score += 1
            rationale.append(f"✅ {away_name}: Opponent {home_name} has negative momentum")
        
        if has_negative_momentum(away_data.get('form_last_5_overall', '')):
            home_score += 1
            rationale.append(f"✅ {home_name}: Opponent {away_name} has negative momentum")
        
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
            rationale.append(f"✅ {home_name}: Has repeatable scoring method")
        
        if has_repeatable_scoring(away_data, is_home=False):
            away_score += 1
            rationale.append(f"✅ {away_name}: Has repeatable scoring method")
        
        # CRITERION 4: Opponent struggles when trailing (simplified proxy)
        def concedes_early(team_data: Dict, is_home: bool) -> bool:
            # Simplified: if concedes frequently in first half or early
            if is_home:
                goals_conceded = team_data.get('home_goals_conceded', 0)
                matches = team_data.get('home_matches_played', 1)
            else:
                goals_conceded = team_data.get('away_goals_conceded', 0)
                matches = team_data.get('away_matches_played', 1)
            
            return (goals_conceded / matches) > 1.5 if matches > 0 else False
        
        if concedes_early(away_data, is_home=False):
            home_score += 1
            rationale.append(f"✅ {home_name}: Opponent {away_name} concedes early frequently")
        
        if concedes_early(home_data, is_home=True):
            away_score += 1
            rationale.append(f"✅ {away_name}: Opponent {home_name} concedes early frequently")
        
        # DETERMINE CONTROLLER
        if home_score >= 2 and home_score > away_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {home_name} ({home_score} criteria)")
            return home_name, rationale
        elif away_score >= 2 and away_score > home_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {away_name} ({away_score} criteria)")
            return away_name, rationale
        else:
            rationale.append(f"⚠️ NO CLEAR GAME-STATE CONTROLLER")
            rationale.append(f"  • {home_name}: {home_score} criteria")
            rationale.append(f"  • {away_name}: {away_score} criteria")
            return None, rationale
    
    # ========== AXIOM 4 ==========
    @staticmethod
    def evaluate_goals_environment(home_data: Dict, away_data: Dict,
                                 controller: Optional[str],
                                 home_name: str, away_name: str) -> Tuple[bool, List[str]]:
        """
        AXIOM 4: GOALS ARE A CONSEQUENCE, NOT A STRATEGY
        Returns True if goals environment exists.
        """
        rationale = []
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # CONDITION 1: Combined xG threshold
        if combined_xg < 2.8:
            rationale.append(f"❌ INSUFFICIENT GOAL CAPACITY")
            rationale.append(f"  • Combined xG: {combined_xg:.2f} < 2.8")
            return False, rationale
        
        # CONDITION 2: At least one elite attack
        if max(home_xg, away_xg) < 1.6:
            rationale.append(f"❌ NO ELITE ATTACK")
            rationale.append(f"  • Best attack: {max(home_xg, away_xg):.2f} < 1.6")
            return False, rationale
        
        # CONDITION 3: Dual crisis check (AXIOM 6)
        home_crisis = home_data.get('goals_conceded_last_5', 0) >= 12
        away_crisis = away_data.get('goals_conceded_last_5', 0) >= 12
        
        if home_crisis and away_crisis and controller is None:
            # Dual fragility but no controller - could be chaos
            rationale.append(f"⚠️ DUAL CRISIS WITHOUT CONTROLLER")
            # Check if both have tempo intent
            home_intent = home_xg > 1.4
            away_intent = away_xg > 1.4
            if home_intent and away_intent:
                rationale.append("  • Both teams have attacking intent")
                rationale.append("✅ GOALS ENVIRONMENT: Dual crisis chaos")
                return True, rationale
            else:
                rationale.append("❌ Chaos suppressed (insufficient intent)")
                return False, rationale
        
        # Default: Goals environment exists
        rationale.append(f"✅ GOALS ENVIRONMENT PRESENT")
        rationale.append(f"  • Combined xG: {combined_xg:.2f} ≥ 2.8")
        rationale.append(f"  • Elite attack: {max(home_xg, away_xg):.2f} ≥ 1.6")
        
        return True, rationale
    
    # ========== AXIOM 5 ==========
    @staticmethod
    def apply_one_sided_control_override(controller: str, opponent_name: str,
                                       controller_data: Dict, opponent_data: Dict,
                                       has_goals_env: bool) -> Tuple[str, float, List[str]]:
        """
        AXIOM 5: ONE-SIDED CONTROL OVERRIDE
        When control is asymmetric, direction beats volume.
        """
        rationale = []
        
        # PRIMARY ACTION: Back controller
        action = f"BACK {controller}"
        confidence = 8.0
        
        rationale.append(f"🎯 ONE-SIDED CONTROL OVERRIDE APPLIED")
        rationale.append(f"  • Controller: {controller}")
        rationale.append(f"  • Opponent: {opponent_name}")
        
        # Check if opponent must chase
        opponent_chase_capacity = opponent_data.get('away_xg_per_match' if opponent_name != 'home' else 'home_xg_per_match', 0) > 1.3
        
        if has_goals_env and opponent_chase_capacity:
            rationale.append(f"  • Opponent can chase → goals bias added")
            action += " & OVER 2.5"
            confidence = 7.5
        elif not has_goals_env:
            rationale.append(f"  • No goals environment → clean win expected")
            action += " & UNDER 2.5 bias"
            confidence = 8.5
        
        return action, confidence, rationale
    
    # ========== AXIOM 7 ==========
    @staticmethod
    def evaluate_favorite_fade(favorite_data: Dict, underdog_data: Dict,
                             favorite_name: str, underdog_name: str,
                             controller: Optional[str]) -> Tuple[bool, List[str]]:
        """
        AXIOM 7: FAVORITES FAIL FOR STRUCTURAL REASONS
        Fade only if favorite lacks GSC and underdog can disrupt.
        """
        rationale = []
        
        # HARD STOP: Favorite is controller
        if controller == favorite_name:
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • {favorite_name} is Game-State Controller")
            return False, rationale
        
        # CONDITION 1: Favorite lacks GSC
        if controller is None:
            rationale.append(f"✅ {favorite_name} lacks GSC")
        elif controller == underdog_name:
            rationale.append(f"✅ {underdog_name} controls state")
        else:
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • Neither team clearly controls")
            return False, rationale
        
        # CONDITION 2: Underdog can impose tempo or disrupt
        underdog_xg = underdog_data.get('away_xg_per_match' if underdog_name != 'home' else 'home_xg_per_match', 0)
        if underdog_xg >= 1.2:
            rationale.append(f"✅ {underdog_name} can impose tempo (xg: {underdog_xg:.2f})")
        else:
            rationale.append(f"❌ {underdog_name} lacks tempo imposition")
            return False, rationale
        
        # CONDITION 3: Favorite has structural weakness
        favorite_form = str(favorite_data.get('form_last_5_overall', ''))
        if 'LL' in favorite_form[-2:] or favorite_form.endswith('L'):
            rationale.append(f"✅ {favorite_name} shows structural decline")
        else:
            rationale.append(f"⚠️ {favorite_name} stable but controllable")
        
        rationale.append(f"✅ CAN FADE {favorite_name}")
        return True, rationale
    
    # ========== AXIOM 8 ==========
    @staticmethod
    def evaluate_under_conditions(controller: Optional[str],
                                controller_data: Dict,
                                opponent_data: Dict) -> Tuple[bool, List[str]]:
        """
        AXIOM 8: UNDER IS A CONTROL OUTCOME
        Under happens when controller wins without urgency.
        """
        rationale = []
        
        if controller is None:
            rationale.append("❌ No controller → Under is not a control outcome")
            return False, rationale
        
        # Check opponent chase capacity
        opponent_xg = opponent_data.get('away_xg_per_match' if 'away' in controller else 'home_xg_per_match', 0)
        
        if opponent_xg < 1.1:
            rationale.append(f"✅ UNDER CONDITIONS: Opponent lacks chase capacity")
            rationale.append(f"  • {controller} can win without urgency")
            rationale.append(f"  • Opponent xG: {opponent_xg:.2f} < 1.1")
            return True, rationale
        
        rationale.append(f"❌ Opponent can chase (xg: {opponent_xg:.2f})")
        return False, rationale
    
    # ========== AXIOM 9 ==========
    @staticmethod
    def evaluate_avoid_conditions(controller: Optional[str],
                                home_xg: float, away_xg: float,
                                league_avg_xg: float) -> Tuple[bool, List[str]]:
        """
        AXIOM 9: AVOID IS RARE AND EXPLICIT
        Avoid only when no state advantage exists.
        """
        rationale = []
        
        if controller is not None:
            rationale.append(f"❌ Controller exists: {controller}")
            return False, rationale
        
        # Check if attacks are below league average
        if home_xg > league_avg_xg * 0.9 or away_xg > league_avg_xg * 0.9:
            rationale.append(f"❌ At least one team has competent attack")
            rationale.append(f"  • Home: {home_xg:.2f}, Away: {away_xg:.2f}")
            rationale.append(f"  • League avg: {league_avg_xg:.2f}")
            return False, rationale
        
        # Check tactical edge neutralization (simplified)
        combined_xg = home_xg + away_xg
        if combined_xg < 2.4:
            rationale.append(f"✅ AVOID CONDITIONS MET")
            rationale.append(f"  • No game-state controller")
            rationale.append(f"  • Attacks below league average")
            rationale.append(f"  • Combined xG: {combined_xg:.2f} < 2.4")
            return True, rationale
        
        rationale.append(f"❌ Combined xG suggests some potential: {combined_xg:.2f}")
        return False, rationale
    
    # ========== AXIOM 10 ==========
    @staticmethod
    def calculate_capital_allocation(controller: Optional[str],
                                   confidence: float,
                                   goals_env: bool) -> float:
        """
        AXIOM 10: CAPITAL FOLLOWS STATE CONFIDENCE
        Stake size reflects control clarity.
        """
        if controller is None:
            # No controller
            if goals_env:
                return 0.5  # Small stake on goals only
            else:
                return 0.0  # Avoid
        
        # Clear controller
        if confidence >= 8.0:
            return 2.0  # Full allocation
        elif confidence >= 7.0:
            return 1.5  # Strong allocation
        elif confidence >= 6.0:
            return 1.0  # Moderate allocation
        else:
            return 0.5  # Small allocation
    
    # ========== MAIN DECISION TREE ==========
    @classmethod
    def execute_decision_tree(cls, home_data: Dict, away_data: Dict,
                            home_name: str, away_name: str,
                            league_avg_xg: float) -> Dict:
        """
        FINAL DECISION TREE (v6.0)
        1. Identify Game-State Controller → If exists → Back them
        2. If controller + opponent collapses when trailing → Add goals bias
        3. If no controller → Evaluate goals environment
        4. If neither control nor goals → Avoid or Under
        5. Stake proportional to control clarity
        """
        
        rationale = ["🧠 BRUTBALL v6.0 DECISION TREE"]
        decision_tree = []
        
        # Determine favorite (by position)
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
        rationale.append(f"⭐ Favorite: {favorite} (#{home_pos if favorite == home_name else away_pos})")
        rationale.append(f"⚫ Underdog: {underdog} (#{away_pos if favorite == home_name else home_pos})")
        
        # STEP 1: Check symmetry (AXIOM 1)
        symmetric, sym_rationale = cls.football_is_not_symmetric(
            home_data.get('home_xg_per_match', 0),
            away_data.get('away_xg_per_match', 0),
            home_data.get('form_last_5_overall', ''),
            away_data.get('form_last_5_overall', '')
        )
        rationale.extend(sym_rationale)
        decision_tree.append(f"Symmetry check: {'YES' if symmetric else 'NO'}")
        
        # STEP 2: Identify Game-State Controller (AXIOM 2)
        controller, control_rationale = cls.identify_game_state_controller(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        rationale.extend(control_rationale)
        decision_tree.append(f"Game-State Controller: {controller if controller else 'NONE'}")
        
        # STEP 3: Evaluate Goals Environment (AXIOM 4)
        has_goals_env, goals_rationale = cls.evaluate_goals_environment(
            home_data, away_data, controller, home_name, away_name
        )
        rationale.extend(["--- Goals Environment ---"])
        rationale.extend(goals_rationale)
        decision_tree.append(f"Goals environment: {'YES' if has_goals_env else 'NO'}")
        
        # STEP 4: Apply Overrides & Make Decision
        primary_action = "ANALYZING"
        confidence = 5.0
        secondary_signal = None
        
        if controller:
            # CASE A: Clear controller exists
            opponent_name = away_name if controller == home_name else home_name
            opponent_data = away_data if controller == home_name else home_data
            
            # Apply one-sided control override (AXIOM 5)
            action, conf, override_rationale = cls.apply_one_sided_control_override(
                controller, opponent_name,
                home_data if controller == home_name else away_data,
                opponent_data,
                has_goals_env
            )
            rationale.extend(["--- One-Sided Control Override ---"])
            rationale.extend(override_rationale)
            
            primary_action = action
            confidence = conf
            
            # Check Under conditions (AXIOM 8)
            if "UNDER" in action:
                under_ok, under_rationale = cls.evaluate_under_conditions(
                    controller,
                    home_data if controller == home_name else away_data,
                    opponent_data
                )
                if not under_ok:
                    primary_action = primary_action.replace(" & UNDER 2.5 bias", "")
            
        elif has_goals_env:
            # CASE B: No controller but goals environment
            # Check favorite fade (AXIOM 7)
            favorite_data = home_data if favorite == home_name else away_data
            underdog_data = away_data if favorite == home_name else home_data
            
            can_fade, fade_rationale = cls.evaluate_favorite_fade(
                favorite_data, underdog_data, favorite, underdog, controller
            )
            rationale.extend(["--- Favorite Fade Check ---"])
            rationale.extend(fade_rationale)
            
            if can_fade:
                primary_action = f"FADE {favorite} & OVER 2.5"
                confidence = 6.5
                secondary_signal = f"{underdog} or DRAW"
            else:
                primary_action = "OVER 2.5 GOALS"
                confidence = 6.0
                secondary_signal = "Goals only, no side"
        
        else:
            # CASE C: Neither controller nor goals
            # Check avoid conditions (AXIOM 9)
            should_avoid, avoid_rationale = cls.evaluate_avoid_conditions(
                controller,
                home_data.get('home_xg_per_match', 0),
                away_data.get('away_xg_per_match', 0),
                league_avg_xg
            )
            rationale.extend(["--- Avoid Conditions Check ---"])
            rationale.extend(avoid_rationale)
            
            if should_avoid:
                primary_action = "AVOID"
                confidence = 0.0
                secondary_signal = "Preserve capital"
            else:
                # Check Under as fallback
                primary_action = "UNDER 2.5 GOALS"
                confidence = 5.5
                secondary_signal = "Low-scoring control outcome"
        
        # STEP 5: Calculate Capital Allocation (AXIOM 10)
        stake_pct = cls.calculate_capital_allocation(controller, confidence, has_goals_env)
        
        # Compile final report
        rationale.insert(0, "=== DECISION TREE EXECUTION ===")
        for step in decision_tree:
            rationale.insert(1, f"• {step}")
        
        rationale.append(f"\n🎯 FINAL DECISION: {primary_action}")
        rationale.append(f"📊 Confidence: {confidence}/10")
        rationale.append(f"💰 Recommended Stake: {stake_pct}% of bankroll")
        
        if secondary_signal:
            rationale.append(f"🔍 Secondary: {secondary_signal}")
        
        return {
            'match': f"{home_name} vs {away_name}",
            'controller': controller,
            'has_goals_env': has_goals_env,
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'secondary_signal': secondary_signal,
            'rationale': rationale,
            'team_context': {
                'favorite': favorite,
                'underdog': underdog,
                'home': home_name,
                'away': away_name
            },
            'key_metrics': {
                'home_xg': home_data.get('home_xg_per_match', 0),
                'away_xg': away_data.get('away_xg_per_match', 0),
                'home_pos': home_pos,
                'away_pos': away_pos,
                'home_form': home_data.get('form_last_5_overall', ''),
                'away_form': away_data.get('form_last_5_overall', ''),
                'combined_xg': home_data.get('home_xg_per_match', 0) + away_data.get('away_xg_per_match', 0)
            }
        }

# =================== DATA & UI ===================
def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate necessary metrics from your CSV structure."""
    
    # Calculate home/away goals conceded
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
    for prefix in ['home', 'away']:
        matches_col = f'{prefix}_matches_played'
        if matches_col in df.columns:
            for metric in ['goals_scored', 'xg_for', 'xg_against']:
                col = f'{prefix}_{metric}'
                if col in df.columns:
                    df[f'{prefix}_{metric}_per_match'] = df[col] / df[matches_col].replace(0, np.nan)
    
    # Goal type percentages
    for prefix in ['home', 'away']:
        goals_col = f'{prefix}_goals_scored'
        if goals_col in df.columns:
            for method in ['counter', 'setpiece', 'openplay']:
                col = f'{prefix}_goals_{method}_for'
                if col in df.columns:
                    df[f'{prefix}_{method}_pct'] = df[col] / df[goals_col].replace(0, np.nan)
    
    # Fill NaN values
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

def render_axioms():
    """Display the v6.0 axioms."""
    
    axioms = [
        ("AXIOM 1", "FOOTBALL IS NOT SYMMETRIC", "Structural balance ≠ match balance"),
        ("AXIOM 2", "GAME-STATE CONTROL IS PRIMARY", "Team that imposes tempo after scoring owns match"),
        ("AXIOM 3", "STRUCTURAL METRICS ARE CONTEXTUAL", "xG, form, crisis only matter after control known"),
        ("AXIOM 4", "GOALS ARE A CONSEQUENCE", "Goals follow state; they do not define it"),
        ("AXIOM 5", "ONE-SIDED CONTROL OVERRIDE", "When control is asymmetric, direction beats volume"),
        ("AXIOM 6", "DUAL FRAGILITY ≠ DUAL CHAOS", "Two bad defenses don't guarantee wild match"),
        ("AXIOM 7", "FAVORITES FAIL STRUCTURALLY", "Not because favorites, but lack GSC"),
        ("AXIOM 8", "UNDER IS A CONTROL OUTCOME", "Controller wins without urgency"),
        ("AXIOM 9", "AVOID IS RARE AND EXPLICIT", "Only when no state advantage exists"),
        ("AXIOM 10", "CAPITAL FOLLOWS STATE CONFIDENCE", "Stake size reflects control clarity")
    ]
    
    cols = st.columns(2)
    for idx, (num, title, desc) in enumerate(axioms):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="axiom-card">
            <strong>{num}: {title}</strong><br>
            <small>{desc}</small>
            </div>
            """, unsafe_allow_html=True)

def render_decision_tree():
    """Display the decision tree."""
    
    st.markdown("""
    ### 🧠 FINAL DECISION TREE (v6.0)
    
    ```python
    1. Identify Game-State Controller
       → If exists → Back them
    
    2. If controller + opponent collapses when trailing
       → Add goals bias
    
    3. If no controller
       → Evaluate goals environment
    
    4. If neither control nor goals
       → Avoid or Under
    
    5. Stake proportional to control clarity
    ```
    """)

def main():
    """Main application."""
    
    st.markdown('<div class="state-identifier">🧠 BRUTBALL v6.0 - MATCH-STATE IDENTIFICATION</div>', unsafe_allow_html=True)
    st.markdown("**No hype. No redundancy. Every axiom has a job and failure condition.**")
    
    # Load sample data or user upload
    st.markdown("---")
    st.markdown("### 📁 DATA INPUT")
    
    uploaded_file = st.file_uploader("Upload your league CSV (or use sample)", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        # Use a sample if available
        st.info("Upload a CSV with team data, or [download sample template](https://example.com)")
        return
    
    # Calculate metrics
    df = calculate_derived_metrics(df)
    
    # Calculate league average xG
    home_xg_avg = df['home_xg_for_per_match'].mean() if 'home_xg_for_per_match' in df.columns else 1.3
    away_xg_avg = df['away_xg_for_per_match'].mean() if 'away_xg_for_per_match' in df.columns else 1.1
    league_avg_xg = (home_xg_avg + away_xg_avg) / 2
    
    # Team selection
    st.markdown("---")
    st.markdown("### 🏟️ MATCH SELECTION")
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 HOME TEAM", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("✈️ AWAY TEAM", away_options)
    
    # Get team data
    home_data = df[df['team'] == home_team].iloc[0].to_dict()
    away_data = df[df['team'] == away_team].iloc[0].to_dict()
    
    if st.button("🚀 EXECUTE STATE IDENTIFICATION", type="primary"):
        
        # Execute decision tree
        result = BrutballStateEngine.execute_decision_tree(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display controller identification
        if result['controller']:
            st.markdown(f"""
            <div class="control-badge">
            <h2>🎯 GAME-STATE CONTROLLER IDENTIFIED</h2>
            <h1 style="color: #16A34A; margin: 0.5rem 0;">{result['controller']}</h1>
            <p>Controls tempo, scoring opportunities, and match flow</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="no-control-badge">
            <h2>⚠️ NO CLEAR CONTROLLER</h2>
            <p>Match state is contested or undefined</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display primary action
        action_color = "#16A34A" if "BACK" in result['primary_action'] else \
                      "#EA580C" if "OVER" in result['primary_action'] else \
                      "#2563EB" if "UNDER" in result['primary_action'] else "#6B7280"
        
        st.markdown(f"""
        <div style="
            padding: 2rem;
            border-radius: 10px;
            background: white;
            border: 3px solid {action_color};
            text-align: center;
            margin: 1rem 0;
        ">
            <h3 style="color: #374151; margin: 0 0 0.5rem 0;">PRIMARY ACTION</h3>
            <h1 style="color: {action_color}; margin: 0;">{result['primary_action']}</h1>
            <div style="display: flex; justify-content: center; margin-top: 1rem;">
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">Confidence</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {action_color};">{result['confidence']}/10</div>
                </div>
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">Stake</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #059669;">{result['stake_pct']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display rationale
        with st.expander("📋 VIEW DECISION RATIONALE", expanded=True):
            for line in result['rationale']:
                if '===' in line:
                    st.markdown(f"**{line}**")
                elif '🎯' in line or '✅' in line or '❌' in line or '⚠️' in line:
                    st.markdown(f"**{line}**")
                elif line.startswith("•"):
                    st.markdown(f"`{line}`")
                elif line.strip():
                    st.markdown(line)
        
        # Display key metrics
        st.markdown("---")
        st.markdown("### 📊 KEY METRICS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### ⚽ Expected Goals")
            st.markdown(f'<div class="metric-display">Home: {result["key_metrics"]["home_xg"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">Away: {result["key_metrics"]["away_xg"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">Combined: {result["key_metrics"]["combined_xg"]:.2f}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🏆 Positions")
            st.markdown(f'<div class="metric-display">{result["team_context"]["home"]}: #{result["key_metrics"]["home_pos"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">{result["team_context"]["away"]}: #{result["key_metrics"]["away_pos"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">Favorite: {result["team_context"]["favorite"]}</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown("#### 📈 Form")
            st.markdown(f'<div class="metric-display">{result["team_context"]["home"]}: {result["key_metrics"]["home_form"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">{result["team_context"]["away"]}: {result["key_metrics"]["away_form"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-display">League Avg xG: {league_avg_xg:.2f}</div>', unsafe_allow_html=True)
        
        # Display axioms
        st.markdown("---")
        st.markdown("### 🔐 ACTIVE AXIOMS")
        render_axioms()
        
        # Display decision tree
        render_decision_tree()
        
        # Export
        st.markdown("---")
        st.markdown("### 📤 EXPORT ANALYSIS")
        
        export_text = f"""
BRUTBALL v6.0 - MATCH-STATE ANALYSIS
=====================================
Match: {result['match']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

GAME-STATE IDENTIFICATION:
• Controller: {result['controller'] if result['controller'] else 'NONE'}
• Goals Environment: {result['has_goals_env']}
• Symmetry: {'Present' if result['key_metrics']['home_xg'] - result['key_metrics']['away_xg'] < 0.2 else 'Broken'}

DECISION:
• Primary Action: {result['primary_action']}
• Confidence: {result['confidence']}/10
• Recommended Stake: {result['stake_pct']}% of bankroll
• Secondary Signal: {result['secondary_signal'] if result['secondary_signal'] else 'N/A'}

RATIONALE:
{chr(10).join(result['rationale'])}

KEY METRICS:
• Home xG: {result['key_metrics']['home_xg']:.2f}
• Away xG: {result['key_metrics']['away_xg']:.2f}
• Combined xG: {result['key_metrics']['combined_xg']:.2f}
• Home Position: #{result['key_metrics']['home_pos']}
• Away Position: #{result['key_metrics']['away_pos']}

=====================================
Brutball v6.0 - Match-State Identification Engine
No hype. No redundancy. Football reality only.
        """
        
        st.download_button(
            label="📥 Download Complete Analysis",
            data=export_text,
            file_name=f"brutball_{home_team}_vs_{away_team}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    # Always show axioms and decision tree
    st.markdown("---")
    render_axioms()
    render_decision_tree()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p><strong>Brutball v6.0 - Match-State Identification Engine</strong></p>
    <p>Not a betting system. Football reality identification only.</p>
    <p>Every axiom has a job. Every axiom has a failure condition.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
