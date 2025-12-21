import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="Brutball Pro Quantitative Framework",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== CUSTOM CSS STYLING ===================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 1.5rem;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .framework-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #374151;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    .layer-box {
        padding: 1.2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border-left: 6px solid #3B82F6;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .layer-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.08);
    }
    .crisis-alert {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 5px solid #DC2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
    }
    .opportunity-alert {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 5px solid #16A34A;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(22, 163, 74, 0.1);
    }
    .defensive-alert {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 5px solid #2563EB;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        margin: 0.75rem 0;
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.12);
        border-color: #3B82F6;
    }
    .archetype-badge {
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.1rem;
        display: inline-block;
        margin: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stake-display {
        font-size: 2.5rem;
        font-weight: 800;
        color: #059669;
        text-align: center;
        margin: 0.5rem 0;
    }
    .confidence-meter {
        height: 12px;
        background: linear-gradient(90deg, #EF4444 0%, #F59E0B 50%, #10B981 100%);
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #F3F4F6;
        border-left: 4px solid #6B7280;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #4B5563;
    }
    .data-table {
        font-size: 0.85rem;
    }
    .league-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.25rem;
    }
    .axiom-card {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        border-left: 5px solid #10B981;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

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

# =================== UNBREAKABLE CORE LOGIC ===================
class UnbreakableCoreLogic:
    """
    UNBREAKABLE CORE LOGIC - Grounded in reality, not theory.
    Outcome-validated, minimal, non-contradictory.
    """
    
    @staticmethod
    def has_match_control(team_data: Dict, opponent_data: Dict, is_home: bool, team_name: str) -> Tuple[bool, List[str]]:
        """
        AXIOM 1: MATCH CONTROL IS NON-NEGOTIABLE
        If a team cannot impose control, it cannot be trusted.
        """
        rationale = []
        control_signals = []
        
        # Get xG metrics
        if is_home:
            team_xg = team_data.get('home_xg_per_match', 0)
            opp_xg = opponent_data.get('away_xg_per_match', 0)
        else:
            team_xg = team_data.get('away_xg_per_match', 0)
            opp_xg = opponent_data.get('home_xg_per_match', 0)
        
        # CRITERIA 1: Team xG ≥ 1.40
        if team_xg >= 1.40:
            control_signals.append(f"✅ {team_name} elite attack: {team_xg:.2f} xG")
        
        # CRITERIA 2: Team creates ≥ 1.2 xG MORE than opponent
        xg_dominance = team_xg - opp_xg
        if xg_dominance >= 1.2:
            control_signals.append(f"✅ {team_name} dominant: +{xg_dominance:.2f} xG edge")
        
        # CRITERIA 3: Elite squad + home (simplified: top 4 position + home)
        if is_home:
            position = team_data.get('season_position', 20)
            if position <= 4:
                control_signals.append(f"✅ {team_name} elite squad at home (#{position})")
        
        # CRITERIA 4: Repeatable scoring method
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
            openplay_pct = team_data.get('home_openplay_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
            openplay_pct = team_data.get('away_openplay_pct', 0)
        
        if setpiece_pct > 0.25:  # Strong set piece threat
            control_signals.append(f"✅ {team_name} repeatable set pieces: {setpiece_pct:.1%}")
        elif openplay_pct > 0.65:  # Dominant open play
            control_signals.append(f"✅ {team_name} open play dominance: {openplay_pct:.1%}")
        
        # FINAL DECISION
        has_control = len(control_signals) > 0
        
        if has_control:
            rationale.extend(control_signals)
            rationale.append(f"🎯 {team_name} HAS MATCH CONTROL")
        else:
            rationale.append(f"❌ {team_name} lacks control mechanisms")
            rationale.append(f"  • xG: {team_xg:.2f} (needs ≥1.40)")
            rationale.append(f"  • xG edge: +{xg_dominance:.2f} (needs ≥1.20)")
        
        return has_control, rationale
    
    @staticmethod
    def can_fade_favorite(favorite_data: Dict, underdog_data: Dict, 
                         favorite_name: str, underdog_name: str,
                         is_favorite_home: bool) -> Tuple[bool, List[str]]:
        """
        AXIOM 3: FAVORITES LOSE ONLY WHEN THEY LACK CONTROL
        Fading a favorite is valid ONLY if the favorite cannot score repeatedly.
        """
        rationale = []
        
        # Get xG metrics
        if is_favorite_home:
            favorite_xg = favorite_data.get('home_xg_per_match', 0)
            underdog_xg = underdog_data.get('away_xg_per_match', 0)
        else:
            favorite_xg = favorite_data.get('away_xg_per_match', 0)
            underdog_xg = underdog_data.get('home_xg_per_match', 0)
        
        # HARD STOP: If favorite xG ≥ 1.50 → DO NOT FADE
        if favorite_xg >= 1.50:
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • xG {favorite_xg:.2f} ≥ 1.50 → scores repeatedly")
            return False, rationale
        
        # CONDITION 1: Favorite xG < 1.30
        if favorite_xg >= 1.30:
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • xG {favorite_xg:.2f} ≥ 1.30 → sufficient scoring")
            return False, rationale
        
        # CONDITION 2: Opponent xG ≥ 1.10
        if underdog_xg < 1.10:
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • {underdog_name} xG {underdog_xg:.2f} < 1.10 → no threat")
            return False, rationale
        
        # CONDITION 3: Favorite away OR declining form
        form = str(favorite_data.get('form_last_5_overall', ''))
        momentum = favorite_data.get('momentum_overall', 'NEUTRAL')
        
        away_weakness = not is_favorite_home
        declining = momentum in ['DECLINING', 'STRONG_DOWN'] or form[-2:] == 'LL'
        
        if not (away_weakness or declining):
            rationale.append(f"❌ CANNOT FADE {favorite_name}")
            rationale.append(f"  • Not away and not declining")
            return False, rationale
        
        # ALL CONDITIONS MET
        rationale.append(f"✅ CAN FADE {favorite_name}")
        rationale.append(f"  • xG {favorite_xg:.2f} < 1.30 → weak scoring")
        rationale.append(f"  • {underdog_name} xG {underdog_xg:.2f} ≥ 1.10 → has threat")
        rationale.append(f"  • {'Away' if away_weakness else 'Declining form'}")
        
        return True, rationale
    
    @staticmethod
    def should_expect_goals(home_data: Dict, away_data: Dict, 
                          home_name: str, away_name: str) -> Tuple[bool, List[str]]:
        """
        AXIOM 4: GOALS REQUIRE INTENT + CAPACITY
        Over 2.5 ONLY if both teams can AND want to attack.
        """
        rationale = []
        
        # Get xG metrics
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # HARD REQUIREMENT 1: Combined xG ≥ 2.8
        if combined_xg < 2.8:
            rationale.append(f"❌ NOT ENOUGH GOAL CAPACITY")
            rationale.append(f"  • Combined xG {combined_xg:.2f} < 2.8")
            return False, rationale
        
        # HARD REQUIREMENT 2: At least one team xG ≥ 1.6
        max_xg = max(home_xg, away_xg)
        if max_xg < 1.6:
            rationale.append(f"❌ NO ELITE ATTACK")
            rationale.append(f"  • Best attack: {max_xg:.2f} xG < 1.6")
            return False, rationale
        
        # Check tactical edge (simplified)
        home_setpiece = home_data.get('home_setpiece_pct', 0)
        away_setpiece = away_data.get('away_setpiece_pct', 0)
        home_counter = home_data.get('home_counter_pct', 0)
        away_counter = away_data.get('away_counter_pct', 0)
        
        tactical_edge = False
        
        # Set piece mismatch
        if home_setpiece > 0.25 and away_setpiece < 0.15:
            tactical_edge = True
            rationale.append(f"✅ Tactical edge: {home_name} set pieces vs {away_name} weakness")
        elif away_setpiece > 0.25 and home_setpiece < 0.15:
            tactical_edge = True
            rationale.append(f"✅ Tactical edge: {away_name} set pieces vs {home_name} weakness")
        
        # Counter attack mismatch
        if home_counter > 0.20 and away_counter < 0.10:
            tactical_edge = True
            rationale.append(f"✅ Tactical edge: {home_name} counters vs {away_name} vulnerability")
        elif away_counter > 0.20 and home_counter < 0.10:
            tactical_edge = True
            rationale.append(f"✅ Tactical edge: {away_name} counters vs {home_name} vulnerability")
        
        if not tactical_edge:
            rationale.append(f"⚠️ No clear tactical edge")
        
        # Check crisis as potential goal amplifier (but not trigger)
        home_crisis = home_data.get('goals_conceded_last_5', 0) >= 12
        away_crisis = away_data.get('goals_conceded_last_5', 0) >= 12
        
        if home_crisis or away_crisis:
            rationale.append(f"⚠️ Defensive crisis present (amplifier only)")
        
        # FINAL DECISION
        rationale.append(f"✅ EXPECT GOALS")
        rationale.append(f"  • Combined xG: {combined_xg:.2f} ≥ 2.8")
        rationale.append(f"  • Elite attack: {max_xg:.2f} xG ≥ 1.6")
        rationale.append(f"  • Intent + capacity confirmed")
        
        return True, rationale
    
    @staticmethod
    def should_expect_low_scoring(home_data: Dict, away_data: Dict,
                                home_name: str, away_name: str) -> Tuple[bool, List[str]]:
        """
        AXIOM 5: LOW-SCORING IS A FIRST-CLASS OUTPUT
        Under / Low scoring if fundamental conditions align.
        """
        rationale = []
        
        # Get xG metrics
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # CONDITION 1: Combined xG < 2.4
        if combined_xg >= 2.4:
            rationale.append(f"❌ TOO MUCH GOAL POTENTIAL")
            rationale.append(f"  • Combined xG {combined_xg:.2f} ≥ 2.4")
            return False, rationale
        
        # CONDITION 2: No elite attack (both teams xG < 1.3)
        if home_xg >= 1.3 or away_xg >= 1.3:
            rationale.append(f"❌ ELITE ATTACK PRESENT")
            rationale.append(f"  • {home_name if home_xg >= 1.3 else away_name}: {max(home_xg, away_xg):.2f} xG")
            return False, rationale
        
        # CONDITION 3: Check for tactical suppression
        home_setpiece = home_data.get('home_setpiece_pct', 0)
        away_setpiece = away_data.get('away_setpiece_pct', 0)
        home_counter = home_data.get('home_counter_pct', 0)
        away_counter = away_data.get('away_counter_pct', 0)
        
        # Both teams lack dangerous set pieces
        if home_setpiece > 0.25 or away_setpiece > 0.25:
            rationale.append(f"⚠️ Set piece threat present")
            # Could still be low scoring, but less confident
        
        # Both teams lack counter threat
        if home_counter > 0.15 or away_counter > 0.15:
            rationale.append(f"⚠️ Counter threat present")
            # Could still be low scoring, but less confident
        
        # CONDITION 4: Check for underperformance
        home_goals = home_data.get('home_goals_per_match', 0)
        away_goals = away_data.get('away_goals_per_match', 0)
        
        home_underperforming = home_goals < home_xg * 0.8 if home_xg > 0 else False
        away_underperforming = away_goals < away_xg * 0.8 if away_xg > 0 else False
        
        if home_underperforming or away_underperforming:
            rationale.append(f"✅ Underperforming attack(s)")
        
        # FINAL DECISION
        rationale.append(f"✅ EXPECT LOW SCORING")
        rationale.append(f"  • Combined xG: {combined_xg:.2f} < 2.4")
        rationale.append(f"  • No elite attacks")
        rationale.append(f"  • Limited tactical threats")
        
        return True, rationale
    
    @staticmethod
    def apply_hierarchical_decision(home_data: Dict, away_data: Dict,
                                  home_name: str, away_name: str) -> Dict:
        """
        AXIOM 6: WINNER SELECTION IS HIERARCHICAL
        System asks in this order:
        1. Can someone control the match?
        2. If no → Can both attack?
        3. If no → Under / Avoid
        """
        
        rationale = []
        decision_tree = []
        
        # STEP 1: Determine favorite (by league position)
        home_position = home_data.get('season_position', 10)
        away_position = away_data.get('season_position', 10)
        
        favorite_name = home_name if home_position < away_position else away_name
        underdog_name = away_name if home_position < away_position else home_name
        
        favorite_data = home_data if favorite_name == home_name else away_data
        underdog_data = away_data if favorite_name == home_name else home_data
        is_favorite_home = favorite_name == home_name
        
        rationale.append(f"⭐ Favorite: {favorite_name} (#{home_position if favorite_name == home_name else away_position})")
        rationale.append(f"⚫ Underdog: {underdog_name} (#{away_position if favorite_name == home_name else home_position})")
        
        # STEP 2: Check if favorite can be faded
        can_fade, fade_rationale = UnbreakableCoreLogic.can_fade_favorite(
            favorite_data, underdog_data, favorite_name, underdog_name, is_favorite_home
        )
        rationale.extend(fade_rationale)
        decision_tree.append(f"Fade check: {'YES' if can_fade else 'NO'}")
        
        # STEP 3: Check match control for both teams
        home_control, home_control_rationale = UnbreakableCoreLogic.has_match_control(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_control, away_control_rationale = UnbreakableCoreLogic.has_match_control(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        rationale.extend([f"--- {home_name} Control ---"])
        rationale.extend(home_control_rationale)
        rationale.extend([f"--- {away_name} Control ---"])
        rationale.extend(away_control_rationale)
        
        decision_tree.append(f"{home_name} control: {'YES' if home_control else 'NO'}")
        decision_tree.append(f"{away_name} control: {'YES' if away_control else 'NO'}")
        
        # STEP 4: Hierarchical decision making
        archetype = 'AVOID'
        confidence = 0
        secondary_signal = None
        
        # CASE 1: Clear control by one team → BACK THAT TEAM
        if home_control and not away_control:
            archetype = 'BACK_THE_UNDERDOG' if can_fade else 'BACK_THE_CONTROLLER'
            confidence = 7
            secondary_signal = f"BACK {home_name}"
            rationale.append(f"🎯 DECISION: {home_name} has control, {away_name} doesn't")
            
        elif away_control and not home_control:
            archetype = 'BACK_THE_UNDERDOG' if can_fade else 'BACK_THE_CONTROLLER'
            confidence = 7
            secondary_signal = f"BACK {away_name}"
            rationale.append(f"🎯 DECISION: {away_name} has control, {home_name} doesn't")
        
        # CASE 2: Both teams have control OR favorite control but can be faded
        elif (home_control and away_control) or (home_control and can_fade and favorite_name == home_name) or (away_control and can_fade and favorite_name == away_name):
            # Check for goals
            expect_goals, goals_rationale = UnbreakableCoreLogic.should_expect_goals(
                home_data, away_data, home_name, away_name
            )
            
            rationale.extend(["--- Goals Check ---"])
            rationale.extend(goals_rationale)
            
            if expect_goals:
                archetype = 'GOALS_GALORE'
                confidence = 6
                secondary_signal = "OVER 2.5 GOALS"
                rationale.append(f"🎯 DECISION: Both can attack → Goals expected")
            else:
                # Check for low scoring
                expect_low, low_rationale = UnbreakableCoreLogic.should_expect_low_scoring(
                    home_data, away_data, home_name, away_name
                )
                
                rationale.extend(["--- Low Scoring Check ---"])
                rationale.extend(low_rationale)
                
                if expect_low:
                    archetype = 'DEFENSIVE_GRIND'
                    confidence = 5
                    secondary_signal = "UNDER 2.5 GOALS"
                    rationale.append(f"🎯 DECISION: Control but no goals → Low scoring")
                else:
                    archetype = 'AVOID'
                    confidence = 0
                    rationale.append(f"🎯 DECISION: Mixed signals → Avoid")
        
        # CASE 3: Neither team has control
        else:
            # Check for goals anyway (sometimes chaos produces goals)
            expect_goals, goals_rationale = UnbreakableCoreLogic.should_expect_goals(
                home_data, away_data, home_name, away_name
            )
            
            rationale.extend(["--- Goals Check (no control) ---"])
            rationale.extend(goals_rationale)
            
            if expect_goals:
                archetype = 'GOALS_GALORE'
                confidence = 5  # Lower confidence without control
                secondary_signal = "OVER 2.5 GOALS"
                rationale.append(f"🎯 DECISION: No control but goals expected")
            else:
                # Check for low scoring
                expect_low, low_rationale = UnbreakableCoreLogic.should_expect_low_scoring(
                    home_data, away_data, home_name, away_name
                )
                
                rationale.extend(["--- Low Scoring Check (no control) ---"])
                rationale.extend(low_rationale)
                
                if expect_low:
                    archetype = 'DEFENSIVE_GRIND'
                    confidence = 6  # Higher confidence for low scoring without control
                    secondary_signal = "UNDER 2.5 GOALS"
                    rationale.append(f"🎯 DECISION: No control, no goals → Low scoring")
                else:
                    archetype = 'AVOID'
                    confidence = 0
                    rationale.append(f"🎯 DECISION: No control, ambiguous scoring → Avoid")
        
        # Add decision tree to rationale
        rationale.insert(0, "DECISION TREE:")
        for step in decision_tree:
            rationale.insert(1, f"  • {step}")
        
        return {
            'archetype': archetype,
            'confidence': confidence,
            'rationale': rationale,
            'secondary_signal': secondary_signal,
            'team_context': {
                'favorite': favorite_name,
                'underdog': underdog_name,
                'home': home_name,
                'away': away_name
            }
        }

# =================== DATA LOADING & PREPARATION ===================
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
                st.success(f"✅ {league_config['display_name']} data loaded from: {source.split('/')[-1]}")
                break
            except Exception as e:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Clean and validate column names
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower()
        cleaned_columns = df.columns.tolist()
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['country'] = league_config['country']
        df.attrs['color'] = league_config['color']
        df.attrs['source'] = source_used
        df.attrs['original_columns'] = original_columns
        df.attrs['cleaned_columns'] = cleaned_columns
        df.attrs['total_teams'] = len(df)
        df.attrs['filename'] = filename
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error for {league_name}: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics from YOUR actual CSV columns."""
    
    # 1. Calculate home/away goals conceded from components
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
    
    df['home_xgc_per_match'] = df['home_xg_against'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xgc_per_match'] = df['away_xg_against'] / df['away_matches_played'].replace(0, np.nan)
    
    # 3. Goal type percentages FOR
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_goals_scored'].replace(0, np.nan)
    
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_goals_scored'].replace(0, np.nan)
    
    # 4. Goal type percentages AGAINST (using our calculated totals)
    df['home_counter_vuln'] = df['home_goals_counter_against'] / df['home_goals_conceded'].replace(0, np.nan)
    df['home_setpiece_vuln'] = df['home_goals_setpiece_against'] / df['home_goals_conceded'].replace(0, np.nan)
    df['home_openplay_vuln'] = df['home_goals_openplay_against'] / df['home_goals_conceded'].replace(0, np.nan)
    
    df['away_counter_vuln'] = df['away_goals_counter_against'] / df['away_goals_conceded'].replace(0, np.nan)
    df['away_setpiece_vuln'] = df['away_goals_setpiece_against'] / df['away_goals_conceded'].replace(0, np.nan)
    df['away_openplay_vuln'] = df['away_goals_openplay_against'] / df['away_goals_conceded'].replace(0, np.nan)
    
    # 5. Form points calculation
    def calculate_form_points(form_string):
        if pd.isna(form_string):
            return 0
        points_map = {'W': 3, 'D': 1, 'L': 0}
        return sum(points_map.get(char, 0) for char in str(form_string))
    
    df['form_points_overall'] = df['form_last_5_overall'].apply(calculate_form_points)
    df['form_points_home'] = df['form_last_5_home'].apply(calculate_form_points)
    df['form_points_away'] = df['form_last_5_away'].apply(calculate_form_points)
    
    # 6. Form momentum
    def calculate_momentum(form_string):
        if pd.isna(form_string) or len(str(form_string)) < 3:
            return 'NEUTRAL'
        last_three = str(form_string)[-3:]
        wins = last_three.count('W')
        losses = last_three.count('L')
        if wins >= 2: return 'STRONG_UP'
        if losses >= 2: return 'STRONG_DOWN'
        if 'W' in last_three and 'L' not in last_three: return 'IMPROVING'
        if 'L' in last_three and 'W' not in last_three: return 'DECLINING'
        return 'VOLATILE'
    
    df['momentum_overall'] = df['form_last_5_overall'].apply(calculate_momentum)
    df['momentum_home'] = df['form_last_5_home'].apply(calculate_momentum)
    df['momentum_away'] = df['form_last_5_away'].apply(calculate_momentum)
    
    # Replace NaN with 0 for calculated columns
    calculated_columns = [col for col in df.columns if col not in [
        'team', 'form_last_5_overall', 'form_last_5_home', 'form_last_5_away',
        'momentum_overall', 'momentum_home', 'momentum_away'
    ]]
    
    for col in calculated_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    return df

# =================== PROFESSIONAL ENGINE ===================
class BrutballProQuantitative:
    """Professional quantitative decision engine with unbreakable core logic."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.performance_log = []
        
    def analyze_match(self, home_team_name: str, away_team_name: str) -> Dict:
        """Complete quantitative analysis pipeline using unbreakable core logic."""
        
        # Get team data
        home_data = self.df[self.df['team'] == home_team_name].iloc[0].to_dict()
        away_data = self.df[self.df['team'] == away_team_name].iloc[0].to_dict()
        
        # Apply unbreakable core logic
        result = UnbreakableCoreLogic.apply_hierarchical_decision(
            home_data, away_data, home_team_name, away_team_name
        )
        
        # Calculate stake size
        stake_pct = self.calculate_stake_size(
            result['archetype'],
            result['confidence']
        )
        
        # Compile comprehensive report
        report = {
            'match': f"{home_team_name} vs {away_team_name}",
            'timestamp': pd.Timestamp.now().isoformat(),
            
            'archetype': result['archetype'],
            'confidence': result['confidence'],
            'rationale': result['rationale'],
            'secondary_signal': result['secondary_signal'],
            'team_context': result['team_context'],
            
            'recommended_stake': stake_pct,
            
            'key_metrics': {
                'home_attack_xg': home_data.get('home_xg_per_match', 0),
                'away_attack_xg': away_data.get('away_xg_per_match', 0),
                'home_defense_xg': home_data.get('home_xgc_per_match', 0),
                'away_defense_xg': away_data.get('away_xgc_per_match', 0),
                'home_form': home_data.get('form_last_5_overall', ''),
                'away_form': away_data.get('form_last_5_overall', ''),
                'home_momentum': home_data.get('momentum_overall', ''),
                'away_momentum': away_data.get('momentum_overall', ''),
                'home_position': home_data.get('season_position', 0),
                'away_position': away_data.get('season_position', 0),
                'home_setpiece_pct': home_data.get('home_setpiece_pct', 0),
                'away_setpiece_pct': away_data.get('away_setpiece_pct', 0),
                'home_counter_pct': home_data.get('home_counter_pct', 0),
                'away_counter_pct': away_data.get('away_counter_pct', 0)
            }
        }
        
        self.log_decision(report)
        return report
    
    def calculate_stake_size(self, archetype: str, confidence: float) -> float:
        """Professional stake sizing with risk management."""
        
        if archetype == 'AVOID' or confidence < 4.0:
            return 0.0
        
        base_stakes = {
            'BACK_THE_UNDERDOG': {8: 2.5, 7: 2.0, 6: 1.5, 5: 1.0, 4: 0.5},
            'BACK_THE_CONTROLLER': {8: 2.5, 7: 2.0, 6: 1.5, 5: 1.0, 4: 0.5},
            'GOALS_GALORE': {8: 2.0, 7: 1.5, 6: 1.0, 5: 0.5, 4: 0.25},
            'DEFENSIVE_GRIND': {8: 1.5, 7: 1.0, 6: 0.5, 5: 0.25, 4: 0.1}
        }
        
        thresholds = base_stakes.get(archetype, {})
        
        for threshold, stake in sorted(thresholds.items(), reverse=True):
            if confidence >= threshold:
                return round(stake, 2)
        
        return 0.0
    
    def log_decision(self, analysis: Dict):
        """Log decision for performance tracking."""
        log_entry = {
            'timestamp': analysis['timestamp'],
            'match': analysis['match'],
            'archetype': analysis['archetype'],
            'confidence': analysis['confidence'],
            'stake_percent': analysis['recommended_stake']
        }
        self.performance_log.append(log_entry)

# =================== STREAMLIT UI COMPONENTS ===================
def render_header():
    """Render main application header."""
    st.markdown('<div class="main-header">⚽ BRUTBALL PRO UNBREAKABLE CORE LOGIC</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem;">Outcome-Validated • Minimal • Non-Contradictory • 5 European Leagues</p>
    </div>
    """, unsafe_allow_html=True)

def render_unbreakable_axioms():
    """Render the unbreakable core logic axioms."""
    st.markdown('<div class="framework-header">🔐 UNBREAKABLE CORE LOGIC (6 AXIOMS)</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="axiom-card">
        <h4>🔑 AXIOM 1</h4>
        <p><strong>MATCH CONTROL IS NON-NEGOTIABLE</strong></p>
        <p>If a team cannot impose control, it cannot be trusted.</p>
        <p>• Team xG ≥ 1.40<br>• xG dominance ≥ 1.20<br>• Elite squad + home<br>• Repeatable scoring method</p>
        </div>
        
        <div class="axiom-card">
        <h4>🔑 AXIOM 2</h4>
        <p><strong>CHAOS ≠ GOALS</strong></p>
        <p>Chaos is only a modifier, never a trigger.</p>
        <p>Goals require intent + capacity.</p>
        </div>
        
        <div class="axiom-card">
        <h4>🔑 AXIOM 3</h4>
        <p><strong>FAVORITES LOSE ONLY WHEN THEY LACK CONTROL</strong></p>
        <p>Fade favorite ONLY if:<br>• xG < 1.30<br>• Opponent xG ≥ 1.10<br>• Away OR declining</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="axiom-card">
        <h4>🔑 AXIOM 4</h4>
        <p><strong>GOALS REQUIRE INTENT + CAPACITY</strong></p>
        <p>Over 2.5 ONLY if:<br>• Combined xG ≥ 2.80<br>• One team xG ≥ 1.60<br>• Tactical edge OR tempo</p>
        </div>
        
        <div class="axiom-card">
        <h4>🔑 AXIOM 5</h4>
        <p><strong>LOW-SCORING IS FIRST-CLASS</strong></p>
        <p>Under / Low scoring if:<br>• Combined xG < 2.40<br>• No elite attack<br>• Limited tactical edge</p>
        </div>
        
        <div class="axiom-card">
        <h4>🔑 AXIOM 6</h4>
        <p><strong>HIERARCHICAL DECISION MAKING</strong></p>
        <p>1. Can someone control? → Back them<br>2. If no → Can both attack? → Goals<br>3. If no → Under / Avoid</p>
        </div>
        """, unsafe_allow_html=True)

def render_league_selector():
    """Render league selection interface."""
    st.markdown('<div class="framework-header">🌍 SELECT LEAGUE</div>', 
                unsafe_allow_html=True)
    
    # Create columns for league selection
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        premier_league = st.button(
            "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
            use_container_width=True,
            type="primary" if 'selected_league' not in st.session_state else "secondary",
            help="English Premier League"
        )
        if premier_league:
            st.session_state.selected_league = 'Premier League'
    
    with col2:
        la_liga = st.button(
            "🇪🇸 La Liga",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'La Liga' else "secondary",
            help="Spanish La Liga"
        )
        if la_liga:
            st.session_state.selected_league = 'La Liga'
    
    with col3:
        bundesliga = st.button(
            "🇩🇪 Bundesliga",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Bundesliga' else "secondary",
            help="German Bundesliga"
        )
        if bundesliga:
            st.session_state.selected_league = 'Bundesliga'
    
    with col4:
        serie_a = st.button(
            "🇮🇹 Serie A",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Serie A' else "secondary",
            help="Italian Serie A"
        )
        if serie_a:
            st.session_state.selected_league = 'Serie A'
    
    with col5:
        ligue_1 = st.button(
            "🇫🇷 Ligue 1",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Ligue 1' else "secondary",
            help="French Ligue 1"
        )
        if ligue_1:
            st.session_state.selected_league = 'Ligue 1'
    
    # Default selection
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # Display current selection
    league_config = LEAGUES[st.session_state.selected_league]
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 10px;
        background: {league_config['color']}15;
        border-left: 6px solid {league_config['color']};
        margin: 1rem 0;
        text-align: center;
    ">
        <h3 style="color: {league_config['color']}; margin: 0;">
            {league_config['display_name']} • {league_config['country']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.selected_league

def render_match_selector(df: pd.DataFrame, league_name: str):
    """Render team selection interface."""
    st.markdown('<div class="framework-header">🏟️ MATCH ANALYSIS</div>', 
                unsafe_allow_html=True)
    
    # Add league context
    league_config = LEAGUES[league_name]
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {league_config['color']}10;
        border-radius: 8px;
        border: 1px solid {league_config['color']}30;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        color: {league_config['color']};
    ">
        {league_config['display_name']} • {df.attrs['total_teams']} Teams Loaded
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox(
            "🏠 **HOME TEAM**",
            options=sorted(df['team'].unique()),
            index=0,
            help="Select home team for analysis"
        )
    
    with col2:
        away_options = [team for team in sorted(df['team'].unique()) if team != home_team]
        away_team = st.selectbox(
            "✈️ **AWAY TEAM**",
            options=away_options,
            index=min(1, len(away_options)-1),
            help="Select away team for analysis"
        )
    
    return home_team, away_team

def render_archetype_decision(analysis: Dict, league_config: Dict):
    """Render archetype decision with styling."""
    
    archetype_colors = {
        'BACK_THE_UNDERDOG': {'bg': '#F0FDF4', 'border': '#16A34A', 'text': '#16A34A'},
        'BACK_THE_CONTROLLER': {'bg': '#F0FDF4', 'border': '#16A34A', 'text': '#16A34A'},
        'GOALS_GALORE': {'bg': '#FFEDD5', 'border': '#EA580C', 'text': '#EA580C'},
        'DEFENSIVE_GRIND': {'bg': '#EFF6FF', 'border': '#2563EB', 'text': '#2563EB'},
        'AVOID': {'bg': '#F3F4F6', 'border': '#6B7280', 'text': '#6B7280'}
    }
    
    colors = archetype_colors.get(analysis['archetype'], archetype_colors['AVOID'])
    
    # Add league badge
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {league_config['color']}15;
        border-radius: 8px;
        border: 1px solid {league_config['color']}30;
        margin-bottom: 0.5rem;
        text-align: center;
        font-weight: 600;
        color: {league_config['color']};
    ">
        {league_config['display_name']} • Unbreakable Core Logic
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="
        padding: 2rem;
        border-radius: 12px;
        background: {colors['bg']};
        border-left: 8px solid {colors['border']};
        margin: 0.5rem 0 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <h2 style="color: {colors['text']}; margin-top: 0;">{analysis['archetype'].replace('_', ' ')}</h2>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
            <div>
                <h3 style="color: #374151; margin-bottom: 0.5rem;">Logic Confidence</h3>
                <div style="font-size: 3rem; font-weight: 800; color: {colors['text']};">{analysis['confidence']}/10</div>
            </div>
            
            <div style="text-align: center;">
                <h3 style="color: #374151; margin-bottom: 0.5rem;">Recommended Stake</h3>
                <div class="stake-display">{analysis['recommended_stake']}%</div>
                <div style="color: #6B7280; font-size: 0.9rem;">of bankroll</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if analysis['secondary_signal']:
        st.markdown(f"""
        <div style="
            padding: 1rem;
            background: {colors['border']}15;
            border-radius: 8px;
            border: 2px dashed {colors['border']}50;
            text-align: center;
            margin: 1rem 0;
        ">
            <h4 style="color: {colors['text']}; margin: 0;">Primary Signal: {analysis['secondary_signal']}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    confidence_pct = analysis['confidence'] * 10
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #6B7280;">Logic Confidence</span>
            <span style="font-weight: bold; color: {colors['text']}">{analysis['confidence']}/10</span>
        </div>
        <div class="confidence-meter" style="width: {confidence_pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)

def render_logic_rationale(analysis: Dict):
    """Render the unbreakable logic rationale."""
    
    st.markdown('<div class="framework-header">🧠 UNBREAKABLE LOGIC RATIONALE</div>', 
                unsafe_allow_html=True)
    
    with st.expander("📋 View Complete Decision Logic", expanded=True):
        for line in analysis['rationale']:
            if '🎯 DECISION:' in line or 'DECISION TREE:' in line:
                st.markdown(f"**{line}**")
            elif '✅' in line or '❌' in line or '⚠️' in line:
                st.markdown(f"**{line}**")
            elif '---' in line:
                st.markdown(f"**{line}**")
            elif '⭐' in line or '⚫' in line:
                st.markdown(f"**{line}**")
            else:
                st.markdown(f"• {line}")

def render_key_metrics(analysis: Dict):
    """Render key metrics for the match."""
    
    st.markdown('<div class="framework-header">📊 KEY METRICS</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### ⚽ Expected Goals")
        st.metric("Home xG/Match", f"{analysis['key_metrics']['home_attack_xg']:.2f}")
        st.metric("Away xG/Match", f"{analysis['key_metrics']['away_attack_xg']:.2f}")
        st.metric("Combined xG", f"{analysis['key_metrics']['home_attack_xg'] + analysis['key_metrics']['away_attack_xg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Tactical Profile")
        st.metric("Home Set Pieces", f"{analysis['key_metrics']['home_setpiece_pct']:.1%}")
        st.metric("Away Set Pieces", f"{analysis['key_metrics']['away_setpiece_pct']:.1%}")
        st.metric("Home Counters", f"{analysis['key_metrics']['home_counter_pct']:.1%}")
        st.metric("Away Counters", f"{analysis['key_metrics']['away_counter_pct']:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🏆 Team Context")
        team_context = analysis['team_context']
        home_team = analysis['match'].split(' vs ')[0]
        away_team = analysis['match'].split(' vs ')[1]
        
        home_label = f"{home_team} {'⭐' if team_context['favorite'] == home_team else '⚫'}"
        away_label = f"{away_team} {'⭐' if team_context['favorite'] == away_team else '⚫'}"
        
        st.metric(home_label, f"#{analysis['key_metrics']['home_position']}")
        st.metric(away_label, f"#{analysis['key_metrics']['away_position']}")
        st.metric("Home Form", analysis['key_metrics']['home_form'])
        st.metric("Away Form", analysis['key_metrics']['away_form'])
        st.markdown('</div>', unsafe_allow_html=True)

def render_professional_notes(analysis: Dict, league_config: Dict):
    """Render professional betting notes."""
    
    st.markdown('<div class="framework-header">📝 PROFESSIONAL NOTES</div>', 
                unsafe_allow_html=True)
    
    notes = []
    archetype = analysis['archetype']
    team_context = analysis['team_context']
    
    home_team = analysis['match'].split(' vs ')[0]
    away_team = analysis['match'].split(' vs ')[1]
    
    if archetype in ['BACK_THE_UNDERDOG', 'BACK_THE_CONTROLLER']:
        team_to_back = analysis['secondary_signal'].replace('BACK ', '') if analysis['secondary_signal'] else team_context['favorite']
        notes.append(f"**🎯 PRIMARY BET:** Back {team_to_back}")
        notes.append(f"**💡 LOGIC:** Match control established per Axiom 1")
        notes.append("**💰 STAKE:** Standard allocation (1.5-2.5%)")
        notes.append("**⚠️ RISK:** Control doesn't guarantee win, just highest probability")
        
    elif archetype == 'GOALS_GALORE':
        notes.append("**🎯 PRIMARY BET:** Over 2.5 Goals")
        notes.append("**💡 LOGIC:** Both teams have intent + capacity (Axiom 4)")
        notes.append("**💰 STAKE:** Conservative allocation (1.0-2.0%)")
        notes.append("**⚠️ RISK:** Early goal could change dynamics")
        notes.append("**📊 MARKET:** Consider Both Teams to Score as alternative")
        
    elif archetype == 'DEFENSIVE_GRIND':
        notes.append("**🎯 PRIMARY BET:** Under 2.5 Goals")
        notes.append("**💡 LOGIC:** Limited goal capacity + no elite attack (Axiom 5)")
        notes.append("**💰 STAKE:** Conservative allocation (0.5-1.5%)")
        notes.append("**⚠️ RISK:** Early goal destroys the bet completely")
        notes.append("**📊 MARKET:** Consider 0-0 or 1-0 correct score for enhanced odds")
        
    else:  # AVOID
        notes.append("**🎯 ACTION:** NO BET - Preserve capital")
        notes.append("**💡 LOGIC:** No clear control, ambiguous scoring (Axiom 6)")
        notes.append("**💰 STAKE:** 0% of bankroll")
        notes.append("**📊 INSIGHT:** Mixed signals create noise, not edge")
        notes.append("**✅ PROFESSIONAL MOVE:** Walking away is profitable")
    
    # Add Axiom references
    notes.append("\n**🔐 UNBREAKABLE LOGIC ACTIVE:**")
    notes.append("• No forced bets")
    notes.append("• No chaos assumptions")
    notes.append("• No fading teams that can score")
    notes.append("• Low-scoring treated as valid edge")
    
    for note in notes:
        if '**' in note:
            st.markdown(note)
        else:
            st.markdown(f"• {note}")

def render_data_preview(df: pd.DataFrame, league_config: Dict):
    """Render data preview section."""
    
    with st.expander("📊 DATA PREVIEW & VALIDATION", expanded=False):
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Teams", len(df))
        with col2:
            st.metric("CSV Columns", len(df.columns))
        with col3:
            st.metric("Data Source", df.attrs.get('filename', 'Unknown'))
        with col4:
            st.metric("League", league_config['display_name'])
        
        st.markdown("**📋 Raw Data (First 10 Rows):**")
        st.dataframe(df.head(10), use_container_width=True)

def render_footer():
    """Render application footer."""
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Brutball Professional Quantitative Framework v5.0</strong></p>
        <p>Unbreakable Core Logic • 6 Outcome-Validated Axioms • Hierarchical Decision Making</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            For professional use only. All betting involves risk. Never bet more than you can afford to lose.
            <br>Logic grounded in reality, not theory. No forced bets, no chaos assumptions.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    render_header()
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # Render unbreakable axioms
    render_unbreakable_axioms()
    
    # Render league selector
    selected_league = render_league_selector()
    
    # Load data for selected league
    with st.spinner(f"Loading {LEAGUES[selected_league]['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error(f"Failed to load data for {selected_league}. Please check your data files and try again.")
        return
    
    # Get league config
    league_config = LEAGUES[selected_league]
    
    # Initialize engine
    engine = BrutballProQuantitative(df)
    
    # Render match selector with league context
    home_team, away_team = render_match_selector(df, selected_league)
    
    if st.button("🚀 RUN UNBREAKABLE ANALYSIS", type="primary", use_container_width=True):
        
        with st.spinner(f"Applying unbreakable core logic to {home_team} vs {away_team}..."):
            analysis = engine.analyze_match(home_team, away_team)
            
            st.markdown("---")
            
            render_archetype_decision(analysis, league_config)
            
            render_logic_rationale(analysis)
            
            render_key_metrics(analysis)
            
            render_professional_notes(analysis, league_config)
            
            st.markdown("---")
            st.markdown("#### 📤 Export Analysis Report")
            
            team_context = analysis['team_context']
            report = f"""
BRUTBALL PROFESSIONAL ANALYSIS REPORT (v5.0)
=============================================

LEAGUE: {league_config['display_name']}
Match: {analysis['match']}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

UNBREAKABLE CORE LOGIC ACTIVE
-----------------------------
• Match control is non-negotiable
• Chaos ≠ goals (modifier only)
• Favorites lose only when lacking control
• Goals require intent + capacity
• Low-scoring is first-class output
• Hierarchical decision making

TEAM CONTEXT:
• Home: {home_team} (Position: #{analysis['key_metrics']['home_position']})
• Away: {away_team} (Position: #{analysis['key_metrics']['away_position']})
• Favorite: {team_context['favorite']} ⭐
• Underdog: {team_context['underdog']} ⚫

KEY METRICS:
• Home xG/Match: {analysis['key_metrics']['home_attack_xg']:.2f}
• Away xG/Match: {analysis['key_metrics']['away_attack_xg']:.2f}
• Combined xG: {analysis['key_metrics']['home_attack_xg'] + analysis['key_metrics']['away_attack_xg']:.2f}
• Home Set Pieces: {analysis['key_metrics']['home_setpiece_pct']:.1%}
• Away Set Pieces: {analysis['key_metrics']['away_setpiece_pct']:.1%}

DECISION OUTPUT:
Archetype: {analysis['archetype'].replace('_', ' ')}
Logic Confidence: {analysis['confidence']}/10
Primary Signal: {analysis['secondary_signal'] if analysis['secondary_signal'] else 'N/A'}
Recommended Stake: {analysis['recommended_stake']}% of bankroll

DECISION RATIONALE:
{chr(10).join(['• ' + line for line in analysis['rationale']])}

=============================================
Brutball Professional Framework v5.0
Unbreakable Core Logic • Outcome-Validated Axioms
            """
            
            st.download_button(
                label="📥 Download Complete Report",
                data=report,
                file_name=f"brutball_{selected_league.replace(' ', '_').lower()}_{home_team}_vs_{away_team}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    render_data_preview(df, league_config)
    render_footer()

# =================== APPLICATION ENTRY POINT ===================
if __name__ == "__main__":
    main()
