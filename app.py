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
                                     league_avg_xg: float) -> Tuple[Optional[str], List[str]]:
        """Identify which team controls game state, or None if no clear controller."""
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
        
        # CRITERION 2: Negative momentum
        def has_negative_momentum(form: str) -> bool:
            if len(form) < 2:
                return False
            return form.endswith('LL') or form.endswith('L')
        
        if has_negative_momentum(home_data.get('form_last_5_overall', '')):
            away_score += 1
            rationale.append(f"✅ {away_name}: {home_name} has negative momentum")
        
        if has_negative_momentum(away_data.get('form_last_5_overall', '')):
            home_score += 1
            rationale.append(f"✅ {home_name}: {away_name} has negative momentum")
        
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
            rationale.append(f"✅ {home_name}: Repeatable scoring method")
        
        if has_repeatable_scoring(away_data, is_home=False):
            away_score += 1
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
            rationale.append(f"✅ {home_name}: {away_name} concedes early")
        
        if concedes_early(home_data, is_home=True):
            away_score += 1
            rationale.append(f"✅ {away_name}: {home_name} concedes early")
        
        # DETERMINE CONTROLLER (need at least 2 criteria)
        if home_score >= 2 and home_score > away_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {home_name} ({home_score}/4 criteria)")
            return home_name, rationale
        elif away_score >= 2 and away_score > home_score:
            rationale.append(f"🎯 GAME-STATE CONTROLLER: {away_name} ({away_score}/4 criteria)")
            return away_name, rationale
        else:
            rationale.append(f"⚠️ NO CLEAR GAME-STATE CONTROLLER")
            rationale.append(f"  • {home_name}: {home_score}/4 criteria")
            rationale.append(f"  • {away_name}: {away_score}/4 criteria")
            return None, rationale
    
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
            rationale.append(f"❌ Combined xG {combined_xg:.2f} < 2.8")
            return False, rationale
        
        if max(home_xg, away_xg) < 1.6:
            rationale.append(f"❌ No elite attack (max: {max(home_xg, away_xg):.2f})")
            return False, rationale
        
        # AXIOM 6: DUAL FRAGILITY ≠ DUAL CHAOS
        home_crisis = home_data.get('goals_conceded_last_5', 0) >= 12
        away_crisis = away_data.get('goals_conceded_last_5', 0) >= 12
        
        if home_crisis and away_crisis and controller is None:
            # Check if both have intent
            if home_xg > 1.4 and away_xg > 1.4:
                rationale.append("✅ DUAL CRISIS + DUAL INTENT → Chaos goals")
                return True, rationale
            else:
                rationale.append("❌ Dual crisis but insufficient intent")
                return False, rationale
        
        rationale.append(f"✅ GOALS ENVIRONMENT: Combined xG {combined_xg:.2f}, Elite attack present")
        return True, rationale
    
    # AXIOM 5: ONE-SIDED CONTROL OVERRIDE
    @staticmethod
    def apply_control_override(controller: str, opponent_name: str,
                             has_goals_env: bool) -> Tuple[str, float, List[str]]:
        """Apply one-sided control override."""
        rationale = []
        
        action = f"BACK {controller}"
        confidence = 8.0
        
        rationale.append(f"🎯 ONE-SIDED CONTROL OVERRIDE")
        rationale.append(f"  • Controller: {controller}")
        rationale.append(f"  • Goals environment: {'YES' if has_goals_env else 'NO'}")
        
        if has_goals_env:
            action += " & OVER 2.5"
            confidence = 7.5
            rationale.append("  • Controller + goals environment → Back & Over")
        else:
            action += " (Clean win expected)"
            confidence = 8.5
            rationale.append("  • Controller without goals → Clean win")
        
        return action, confidence, rationale
    
    # AXIOM 7: FAVORITES FAIL STRUCTURALLY
    @staticmethod
    def evaluate_favorite_fade(favorite: str, underdog: str,
                             controller: Optional[str]) -> Tuple[bool, List[str]]:
        """Evaluate if favorite can be faded."""
        rationale = []
        
        if controller == favorite:
            rationale.append(f"❌ Cannot fade {favorite} - is controller")
            return False, rationale
        
        if controller == underdog:
            rationale.append(f"✅ {underdog} controls state → Fade {favorite}")
            return True, rationale
        
        if controller is None:
            rationale.append(f"⚠️ No controller → Consider fade carefully")
            return True, rationale
        
        rationale.append(f"❌ Controller exists but not underdog")
        return False, rationale
    
    # MAIN DECISION TREE
    @classmethod
    def execute_v6_tree(cls, home_data: Dict, away_data: Dict,
                       home_name: str, away_name: str,
                       league_avg_xg: float) -> Dict:
        """Execute v6.0 decision tree."""
        
        rationale = ["🧠 BRUTBALL v6.0 DECISION TREE"]
        
        # Determine favorite
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
        rationale.append(f"⭐ Favorite: {favorite} (#{min(home_pos, away_pos)})")
        rationale.append(f"⚫ Underdog: {underdog} (#{max(home_pos, away_pos)})")
        
        # STEP 1: Identify Game-State Controller
        controller, control_rationale = cls.identify_game_state_controller(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        rationale.extend(control_rationale)
        
        # STEP 2: Evaluate Goals Environment
        has_goals_env, goals_rationale = cls.evaluate_goals_environment(
            home_data, away_data, controller
        )
        rationale.extend(["-- Goals Environment --"])
        rationale.extend(goals_rationale)
        
        # STEP 3: Apply Decision Logic
        primary_action = "ANALYZING"
        confidence = 5.0
        secondary_signal = None
        
        if controller:
            # CASE A: Controller exists → AXIOM 5 override
            opponent = away_name if controller == home_name else home_name
            action, conf, override_rationale = cls.apply_control_override(
                controller, opponent, has_goals_env
            )
            rationale.extend(["-- Control Override --"])
            rationale.extend(override_rationale)
            primary_action = action
            confidence = conf
            
        elif has_goals_env:
            # CASE B: No controller but goals environment
            can_fade, fade_rationale = cls.evaluate_favorite_fade(
                favorite, underdog, controller
            )
            rationale.extend(["-- Favorite Fade Check --"])
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
            # Check Under conditions
            combined_xg = home_data.get('home_xg_per_match', 0) + away_data.get('away_xg_per_match', 0)
            if combined_xg < 2.4:
                primary_action = "UNDER 2.5 GOALS"
                confidence = 5.5
                secondary_signal = "Low-scoring control outcome"
            else:
                primary_action = "AVOID"
                confidence = 0.0
                secondary_signal = "No edge identified"
        
        # Calculate stake
        stake_pct = cls.calculate_stake(controller, confidence, has_goals_env)
        
        rationale.append(f"\n🎯 FINAL DECISION: {primary_action}")
        rationale.append(f"📊 Confidence: {confidence}/10")
        rationale.append(f"💰 Stake: {stake_pct}%")
        
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
                'combined_xg': home_data.get('home_xg_per_match', 0) + away_data.get('away_xg_per_match', 0),
                'league_avg_xg': league_avg_xg
            }
        }
    
    @staticmethod
    def calculate_stake(controller: Optional[str], confidence: float, has_goals_env: bool) -> float:
        """Calculate stake percentage (AXIOM 10)."""
        if controller:
            if confidence >= 8.0:
                return 2.0
            elif confidence >= 7.0:
                return 1.5
            elif confidence >= 6.0:
                return 1.0
            else:
                return 0.5
        elif has_goals_env:
            return 0.5
        else:
            return 0.0

# =================== DATA LOADING (YOUR ORIGINAL CODE) ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load, validate, and prepare the dataset for selected league."""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple data source locations (YOUR EXACT CODE)
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
        
        # Calculate derived metrics (YOUR EXACT FUNCTION)
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
        <p>No hype. No redundancy. Every axiom has a job and failure condition.</p>
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
    """Display v6.0 axioms."""
    st.markdown('<div class="axiom-header">🔐 BRUTBALL v6.0 AXIOMS</div>', unsafe_allow_html=True)
    
    axioms = [
        ("AXIOM 1", "FOOTBALL IS NOT SYMMETRIC", "Structural balance ≠ match balance"),
        ("AXIOM 2", "GAME-STATE CONTROL IS PRIMARY", "Team that imposes tempo after scoring owns match"),
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
    """Display decision tree."""
    st.markdown('<div class="axiom-header">🧠 DECISION TREE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ```python
    1. Identify Game-State Controller
       → If exists → Back them (AXIOM 5)
    
    2. If controller + opponent collapses
       → Add goals bias
    
    3. If no controller
       → Evaluate goals environment
    
    4. If neither control nor goals
       → Avoid or Under
    
    5. Stake proportional to control clarity
    ```
    """)

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
        league_avg_xg = 1.3  # Fallback
    
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
        
        # Display controller identification
        config = LEAGUES[selected_league]
        if result['controller']:
            st.markdown(f"""
            <div class="control-badge">
            <h2>🎯 GAME-STATE CONTROLLER IDENTIFIED</h2>
            <h1 style="color: #16A34A; margin: 0.5rem 0;">{result['controller']}</h1>
            <p style="color: #6B7280;">Controls tempo, scoring, and match flow</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="no-control-badge">
            <h2>⚠️ NO CLEAR GAME-STATE CONTROLLER</h2>
            <p style="color: #6B7280;">Match state is contested or undefined</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display primary action
        action = result['primary_action']
        if "BACK" in action:
            color = "#16A34A"
        elif "OVER" in action or "FADE" in action:
            color = "#EA580C"
        elif "UNDER" in action:
            color = "#2563EB"
        else:
            color = "#6B7280"
        
        st.markdown(f"""
        <div class="action-display" style="border: 3px solid {color};">
            <h3 style="color: #374151; margin: 0 0 0.5rem 0;">PRIMARY ACTION</h3>
            <h1 style="color: {color}; margin: 0;">{action}</h1>
            <div style="display: flex; justify-content: center; margin-top: 1.5rem;">
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">Confidence</div>
                    <div style="font-size: 2rem; font-weight: 800; color: {color};">{result['confidence']}/10</div>
                </div>
                <div style="margin: 0 2rem;">
                    <div style="color: #6B7280;">Stake</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #059669;">{result['stake_pct']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence bar
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="color: #6B7280; font-size: 0.9rem;">State Confidence</span>
                <span style="font-weight: 600; color: {color}">{result['confidence']}/10</span>
            </div>
            <div class="confidence-bar" style="width: {result['confidence'] * 10}%;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display rationale
        with st.expander("📋 VIEW COMPLETE RATIONALE", expanded=True):
            for line in result['rationale']:
                if '🧠' in line or '🎯' in line:
                    st.markdown(f"**{line}**")
                elif '✅' in line or '❌' in line or '⚠️' in line:
                    st.markdown(f"**{line}**")
                elif '--' in line:
                    st.markdown(f"*{line}*")
                else:
                    st.markdown(line)
        
        # Key metrics
        st.markdown('<div class="axiom-header">📊 KEY METRICS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### ⚽ Expected Goals")
            st.metric("Home xG/Match", f"{result['key_metrics']['home_xg']:.2f}")
            st.metric("Away xG/Match", f"{result['key_metrics']['away_xg']:.2f}")
            st.metric("Combined xG", f"{result['key_metrics']['combined_xg']:.2f}")
            st.metric("League Average", f"{result['key_metrics']['league_avg_xg']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### 🏆 Team Context")
            team_context = result['team_context']
            st.metric(f"{team_context['home']}", f"#{result['key_metrics']['home_pos']}")
            st.metric(f"{team_context['away']}", f"#{result['key_metrics']['away_pos']}")
            st.metric("Favorite", team_context['favorite'])
            st.metric("Underdog", team_context['underdog'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        export_text = f"""
BRUTBALL v6.0 - MATCH-STATE ANALYSIS
=====================================
League: {selected_league}
Match: {result['match']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

GAME-STATE IDENTIFICATION:
• Controller: {result['controller'] if result['controller'] else 'NONE'}
• Goals Environment: {result['has_goals_env']}
• Favorite: {result['team_context']['favorite']}
• Underdog: {result['team_context']['underdog']}

DECISION:
• Primary Action: {result['primary_action']}
• Confidence: {result['confidence']}/10
• Stake: {result['stake_pct']}% of bankroll
• Secondary: {result['secondary_signal'] if result['secondary_signal'] else 'N/A'}

KEY METRICS:
• Home xG: {result['key_metrics']['home_xg']:.2f}
• Away xG: {result['key_metrics']['away_xg']:.2f}
• Combined xG: {result['key_metrics']['combined_xg']:.2f}
• League Avg xG: {result['key_metrics']['league_avg_xg']:.2f}

RATIONALE:
{chr(10).join(result['rationale'])}

=====================================
Brutball v6.0 - Match-State Identification Engine
        """
        
        st.download_button(
            label="📥 Download Analysis Report",
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
        <p>Football reality identification. No forced bets. No chaos assumptions.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
