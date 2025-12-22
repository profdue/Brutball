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
    .key-metrics-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .key-metrics-table th {
        background: #F3F4F6;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #4B5563;
        border: 1px solid #E5E7EB;
    }
    .key-metrics-table td {
        padding: 0.75rem;
        border: 1px solid #E5E7EB;
        text-align: left;
    }
    .key-metrics-table tr:nth-child(even) {
        background: #F9FAFB;
    }
    .consolidated-justification {
        background: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0EA5E9;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =================== AUDIT-READY BRUTBALL v6.0 ENGINE ===================
class BrutballAuditEngine:
    """AUDIT-READY v6.0 TEMPLATE IMPLEMENTATION"""
    
    @staticmethod
    def evaluate_control_criteria(team_data: Dict, opponent_data: Dict,
                                 is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """Evaluate 4 control criteria with weighted scoring."""
        rationale = []
        criteria_met = []
        raw_score = 0
        weighted_score = 0.0
        
        # Tempo dominance
        if is_home:
            tempo_xg = team_data.get('home_xg_per_match', 0)
        else:
            tempo_xg = team_data.get('away_xg_per_match', 0)
        
        if tempo_xg > 1.4:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Tempo dominance")
            rationale.append(f"✅ {team_name}: Tempo dominance (xG: {tempo_xg:.2f} > 1.4)")
        
        # Scoring efficiency
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
        
        # Critical area threat
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"✅ {team_name}: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # Repeatable patterns
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
    def evaluate_goals_environment(home_data: Dict, away_data: Dict,
                                 controller: Optional[str],
                                 home_name: str, away_name: str) -> Tuple[bool, List[str], float, Dict]:
        """AXIOM 4: Goals are consequence, not strategy"""
        rationale = []
        metrics = {}
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        max_xg = max(home_xg, away_xg)
        
        metrics['home_xg'] = home_xg
        metrics['away_xg'] = away_xg
        metrics['combined_xg'] = combined_xg
        metrics['max_xg'] = max_xg
        
        rationale.append("🎯 AXIOM 4: GOALS ENVIRONMENT EVALUATION")
        rationale.append(f"• Combined xG: {combined_xg:.2f} (threshold: ≥2.8)")
        rationale.append(f"• Home xG: {home_xg:.2f}, Away xG: {away_xg:.2f}")
        
        if combined_xg < 2.8:
            rationale.append(f"❌ AXIOM 4: Combined xG {combined_xg:.2f} < 2.8 threshold")
            return False, rationale, 0.0, metrics
        
        if max_xg < 1.6:
            rationale.append(f"❌ AXIOM 4: No elite attack (max: {max_xg:.2f} < 1.6 threshold)")
            return False, rationale, 0.0, metrics
        
        rationale.append(f"✅ AXIOM 4: Combined xG {combined_xg:.2f} ≥ 2.8 threshold")
        rationale.append(f"✅ AXIOM 4: Elite attack present ({max_xg:.2f} ≥ 1.6)")
        
        controller_xg = 0.0
        if controller:
            controller_xg = home_xg if controller == home_name else away_xg
            metrics['controller_xg'] = controller_xg
        
        return True, rationale, controller_xg, metrics
    
    @staticmethod
    def apply_one_sided_override(controller: str, opponent_name: str,
                               controller_xg: float, has_goals_env: bool,
                               combined_xg: float, is_underdog: bool,
                               asymmetry_level: float) -> Tuple[str, float, List[str], List[str]]:
        """AXIOM 5: ONE-SIDED CONTROL OVERRIDE"""
        rationale = []
        adjustments = []
        
        action = f"BACK {controller}"
        confidence = 8.5
        
        rationale.append("🎯 AXIOM 5: ONE-SIDED CONTROL OVERRIDE")
        rationale.append(f"• Controller: {controller}")
        rationale.append(f"• Controller xG: {controller_xg:.2f}")
        rationale.append(f"• Goals environment: {'Present' if has_goals_env else 'Absent'}")
        
        if has_goals_env:
            action += " & OVER 2.5"
            confidence = 8.0
            
            if controller_xg < 1.6:
                rationale.append(f"⚠️ Controller xG {controller_xg:.2f} < 1.6 elite threshold")
                rationale.append(f"  • Valid because: Combined xG {combined_xg:.2f} ≥ 2.8 supports scoring")
                confidence *= 0.94
            
            rationale.append("• AXIOM 5: Controller + goals environment → Back & Over")
        else:
            action += " (Clean win expected)"
            confidence = 9.0
            rationale.append("• AXIOM 5: Controller without goals → Clean win (likely UNDER)")
        
        # Standardized adjustments (multipliers only)
        if is_underdog:
            confidence *= 0.9
            adjustments.append("Underdog controller (×0.9)")
        
        if asymmetry_level > 0.5:
            confidence *= 1.1
            adjustments.append(f"High asymmetry {asymmetry_level:.2f} (×1.1)")
        
        confidence = max(5.0, min(10.0, confidence))
        
        if adjustments:
            rationale.append(f"• Confidence adjustments: {', '.join(adjustments)}")
            rationale.append(f"• Final confidence: {confidence:.1f}/10")
        
        return action, confidence, rationale, adjustments
    
    @staticmethod
    def allocate_capital(controller: Optional[str],
                        confidence: float,
                        has_goals_env: bool,
                        is_underdog_controller: bool,
                        asymmetry_level: float,
                        adjustments: List[str]) -> Tuple[float, List[str], List[str]]:
        """AXIOM 10: CAPITAL FOLLOWS STATE CONFIDENCE"""
        rationale = []
        stake_adjustments = []
        
        rationale.append("💰 AXIOM 10: CAPITAL ALLOCATION")
        rationale.append(f"• Base confidence: {confidence:.1f}/10")
        
        if controller:
            # Base stake based on confidence
            if confidence >= 8.5:
                stake = 2.5
                rationale.append(f"• High confidence → 2.5% base stake")
            elif confidence >= 7.5:
                stake = 2.0
                rationale.append(f"• Moderate-high confidence → 2.0% base stake")
            elif confidence >= 6.5:
                stake = 1.5
                rationale.append(f"• Moderate confidence → 1.5% base stake")
            else:
                stake = 1.0
                rationale.append(f"• Low confidence → 1.0% base stake")
            
            # Apply stake adjustments
            if is_underdog_controller:
                stake *= 0.8
                stake_adjustments.append("Underdog controller (×0.8)")
                rationale.append(f"• Underdog controller → stake reduced by 20% (×0.8)")
            
            if asymmetry_level > 0.5:
                stake *= 1.2
                stake_adjustments.append(f"High asymmetry {asymmetry_level:.2f} (×1.2)")
                rationale.append(f"• High asymmetry ({asymmetry_level:.2f} > 0.5) → stake increased by 20% (×1.2)")
            else:
                rationale.append(f"• Asymmetry {asymmetry_level:.2f} → no stake adjustment per AXIOM 10")
            
            if stake_adjustments:
                rationale.append(f"• Applied adjustments: {', '.join(stake_adjustments)}")
                stake = max(0.5, min(stake, 3.0))
            
        elif has_goals_env:
            stake = 0.5
            rationale.append("• No controller, goals only → 0.5% stake")
        else:
            stake = 0.0
            rationale.append("• No edge → 0.0% stake (AVOID)")
        
        rationale.append(f"• Final stake: {stake:.2f}% of bankroll")
        return stake, rationale, stake_adjustments
    
    @classmethod
    def execute_audit_tree(cls, home_data: Dict, away_data: Dict,
                          home_name: str, away_name: str,
                          league_avg_xg: float) -> Dict:
        """Execute exact 4-step decision tree with tie-breakers."""
        
        audit_log = []
        decision_steps = []
        
        # Determine favorite
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
        
        home_score, home_weighted, home_criteria, home_rationale = cls.evaluate_control_criteria(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_score, away_weighted, away_criteria, away_rationale = cls.evaluate_control_criteria(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        audit_log.extend(home_rationale)
        audit_log.extend(away_rationale)
        
        controller = None
        controller_criteria = []
        
        if home_score >= 2 and away_score >= 2:
            audit_log.append("⚖️ TIE-BREAKER SITUATION: Both teams meet ≥2 criteria")
            
            if home_weighted > away_weighted:
                controller = home_name
                controller_criteria = home_criteria
                audit_log.append(f"  • Tie-breaker: {home_name} selected (higher structured control score)")
            elif away_weighted > home_weighted:
                controller = away_name
                controller_criteria = away_criteria
                audit_log.append(f"  • Tie-breaker: {away_name} selected (higher structured control score)")
            else:
                if home_pos < away_pos:
                    controller = home_name
                    controller_criteria = home_criteria
                else:
                    controller = away_name
                    controller_criteria = away_criteria
            
        elif home_score >= 2 and home_score > away_score:
            controller = home_name
            controller_criteria = home_criteria
            audit_log.append(f"🎯 GAME-STATE CONTROLLER: {home_name} ({home_score}/4 criteria)")
            
        elif away_score >= 2 and away_score > home_score:
            controller = away_name
            controller_criteria = away_criteria
            audit_log.append(f"🎯 GAME-STATE CONTROLLER: {away_name} ({away_score}/4 criteria)")
            
        else:
            audit_log.append("⚠️ NO CLEAR GAME-STATE CONTROLLER")
        
        decision_steps.append(f"1. Controller: {controller if controller else 'None'}")
        
        # =================== STEP 2: EVALUATE GOALS ENVIRONMENT ===================
        audit_log.append("")
        audit_log.append("STEP 2: EVALUATE GOALS ENVIRONMENT (AXIOM 4)")
        
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        asymmetry_level = abs(home_xg - away_xg) / max(home_xg + away_xg, 0.1)
        
        has_goals_env, goals_rationale, controller_xg, metrics = cls.evaluate_goals_environment(
            home_data, away_data, controller, home_name, away_name
        )
        audit_log.extend(goals_rationale)
        
        decision_steps.append(f"2. Goals Environment: {'Present' if has_goals_env else 'Absent'}")
        
        # =================== STEP 3: APPLY DECISION LOGIC ===================
        audit_log.append("")
        audit_log.append("STEP 3: APPLY DECISION LOGIC (AXIOM 5)")
        
        primary_action = "ANALYZING"
        confidence = 5.0
        secondary_logic = ""
        confidence_adjustments = []
        
        if controller:
            is_underdog = controller == underdog
            
            action, conf, override_rationale, adjustments = cls.apply_one_sided_override(
                controller, away_name if controller == home_name else home_name,
                controller_xg, has_goals_env, combined_xg, is_underdog,
                asymmetry_level
            )
            audit_log.extend(override_rationale)
            primary_action = action
            confidence = conf
            confidence_adjustments = adjustments
            
            decision_steps.append("3A. One-Sided Control Override (AXIOM 5)")
        
        # =================== STEP 4: ALLOCATE CAPITAL ===================
        audit_log.append("")
        audit_log.append("STEP 4: ALLOCATE CAPITAL (AXIOM 10)")
        
        is_underdog_controller = controller == underdog if controller else False
        stake_pct, stake_rationale, stake_adjustments = cls.allocate_capital(
            controller, confidence, has_goals_env,
            is_underdog_controller, asymmetry_level, confidence_adjustments
        )
        audit_log.extend(stake_rationale)
        
        decision_steps.append(f"4. Stake: {stake_pct:.2f}% of bankroll")
        
        # Final summary
        audit_log.append("")
        audit_log.append("=" * 70)
        audit_log.append("🎯 FINAL DECISION")
        audit_log.append(f"• Action: {primary_action}")
        audit_log.append(f"• Confidence: {confidence:.1f}/10")
        audit_log.append(f"• Stake: {stake_pct:.2f}% of bankroll")
        audit_log.append("=" * 70)
        
        return {
            'match': f"{home_name} vs {away_name}",
            'controller': controller,
            'controller_criteria': controller_criteria,
            'has_goals_env': has_goals_env,
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'audit_log': audit_log,
            'decision_steps': decision_steps,
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
                'max_xg': metrics.get('max_xg', max(home_xg, away_xg)),
                'asymmetry_level': asymmetry_level,
            },
            'stake_adjustments': stake_adjustments,
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
        
        # Try different paths for data loading
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
        ]
        
        df = None
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                st.success(f"✅ Loaded data from {source}")
                break
            except:
                continue
        
        if df is None:
            st.error(f"❌ Could not load {filename}. Please check file exists.")
            return None
        
        # Ensure required columns exist
        required_cols = ['team', 'home_xg_per_match', 'away_xg_per_match', 'season_position']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"❌ Missing required column: {col}")
                return None
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data loading error: {str(e)}")
        return None

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
                type="primary" if st.session_state.selected_league != league else "secondary"
            ):
                st.session_state.selected_league = league
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Please check your CSV files.")
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
        
        # Get team data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average xG
        league_avg_xg = 1.3  # Default
        
        # Execute audit tree
        result = BrutballAuditEngine.execute_audit_tree(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        st.markdown("---")
        
        # Display results
        st.markdown("### 🎯 ANALYSIS RESULTS")
        
        # Controller display
        if result['controller']:
            controller_name = result['controller']
            criteria_count = len(result['controller_criteria'])
            
            st.markdown(f"""
            <div class="control-indicator">
                <h3 style="color: #16A34A; margin: 0;">GAME-STATE CONTROLLER IDENTIFIED</h3>
                <h2 style="color: #16A34A; margin: 0.5rem 0;">{controller_name}</h2>
                <p style="color: #6B7280; margin-bottom: 0.5rem;">
                    <strong>Criteria met: {', '.join(result['controller_criteria'])} ({criteria_count}/4)</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="no-control-indicator">
                <h3 style="color: #6B7280; margin: 0;">NO CLEAR GAME-STATE CONTROLLER</h3>
                <p style="color: #6B7280;">Neither team meets 2+ control criteria</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Primary action
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
        </div>
        """, unsafe_allow_html=True)
        
        # SINGLE KEY METRICS TABLE
        st.markdown("#### 📊 KEY METRICS SUMMARY")
        
        metrics = result['key_metrics']
        ctx = result['team_context']
        
        # Build consolidated metrics table
        metrics_html = f"""
        <table class="key-metrics-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Threshold</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Home xG ({ctx['home']})</td>
                    <td>{metrics['home_xg']:.2f}</td>
                    <td>≥1.6 (elite)</td>
                    <td>{'✅ Elite' if metrics['home_xg'] >= 1.6 else '⚠️ Sub-elite' if metrics['home_xg'] >= 1.0 else '❌ Low'}</td>
                </tr>
                <tr>
                    <td>Away xG ({ctx['away']})</td>
                    <td>{metrics['away_xg']:.2f}</td>
                    <td>≥1.6 (elite)</td>
                    <td>{'✅ Elite' if metrics['away_xg'] >= 1.6 else '⚠️ Sub-elite' if metrics['away_xg'] >= 1.0 else '❌ Low'}</td>
                </tr>
                <tr>
                    <td>Combined xG</td>
                    <td>{metrics['combined_xg']:.2f}</td>
                    <td>≥2.8</td>
                    <td>{'✅ ≥2.8' if metrics['combined_xg'] >= 2.8 else '⚠️ 2.0-2.8' if metrics['combined_xg'] >= 2.0 else '❌ <2.0'}</td>
                </tr>
                <tr>
                    <td>Max xG (Elite Attack)</td>
                    <td>{metrics['max_xg']:.2f}</td>
                    <td>≥1.6</td>
                    <td>{'✅ Elite' if metrics['max_xg'] >= 1.6 else '⚠️ Sub-elite'}</td>
                </tr>
        """
        
        if result['controller']:
            controller_status = '✅ Elite' if metrics['controller_xg'] >= 1.6 else '⚠️ Sub-elite'
            metrics_html += f"""
                <tr>
                    <td>Controller xG ({result['controller']})</td>
                    <td>{metrics['controller_xg']:.2f}</td>
                    <td>≥1.6 (elite)</td>
                    <td>{controller_status}</td>
                </tr>
            """
        
        metrics_html += f"""
                <tr>
                    <td>Asymmetry Level</td>
                    <td>{metrics['asymmetry_level']:.2f}</td>
                    <td>>0.5 (High)</td>
                    <td>{'✅ High' if metrics['asymmetry_level'] > 0.5 else '⚠️ Moderate' if metrics['asymmetry_level'] > 0.3 else '⚫ Low'}</td>
                </tr>
            </tbody>
        </table>
        """
        
        st.markdown(metrics_html, unsafe_allow_html=True)
        
        # CONSOLIDATED JUSTIFICATION
        if result['controller'] and "BACK" in result['primary_action']:
            st.markdown("#### 🎯 CONSOLIDATED DECISION JUSTIFICATION")
            
            justification = f"""
            <div class="consolidated-justification">
                <strong>Controller + Goals Environment → BACK & OVER (AXIOMS 4,5)</strong><br><br>
                
                <strong>1. Control Established (AXIOM 2):</strong><br>
                • {result['controller']} meets {len(result['controller_criteria'])}/4 control criteria<br>
                • Criteria: {', '.join(result['controller_criteria'])}<br><br>
                
                <strong>2. Goals Environment Valid (AXIOM 4):</strong><br>
                • Combined xG: {metrics['combined_xg']:.2f} {"≥ 2.8 threshold" if metrics['combined_xg'] >= 2.8 else "< 2.8 threshold"}<br>
                • Elite attack present: {metrics['max_xg']:.2f} {"≥ 1.6" if metrics['max_xg'] >= 1.6 else "< 1.6"}<br>
                • Controller xG: {metrics['controller_xg']:.2f} {"≥ 1.6 (elite)" if metrics['controller_xg'] >= 1.6 else "< 1.6 (sub-elite)"}<br><br>
                
                <strong>3. One-Sided Override (AXIOM 5):</strong><br>
                • Clear controller enables directional bet<br>
                • Goals environment: {result['has_goals_env'] and 'Present → supports OVER 2.5' or 'Absent → clean win expected (likely UNDER)'}<br><br>
                
                <strong>4. Capital Allocation (AXIOM 10):</strong><br>
                • Base confidence: {result['confidence']:.1f}/10<br>
                • Stake: {result['stake_pct']:.2f}% of bankroll<br>
                {"• Adjustments: " + ", ".join(result['stake_adjustments']) if result.get('stake_adjustments') else "• No stake adjustments applied"}
            </div>
            """
            
            st.markdown(justification, unsafe_allow_html=True)
        
        # Decision steps
        st.markdown("#### 📋 Decision Steps")
        for step in result['decision_steps']:
            st.markdown(f"- {step}")
        
        # Audit log
        with st.expander("📋 VIEW COMPLETE AUDIT LOG", expanded=False):
            for line in result['audit_log']:
                if '=' in line or '🎯' in line or 'STEP' in line:
                    st.markdown(f"**{line}**")
                elif '✅' in line or '❌' in line or '⚠️' in line:
                    st.markdown(f"**{line}**")
                elif line.startswith("•") or line.startswith("  •"):
                    st.markdown(f"`{line}`")
                elif line.strip():
                    st.markdown(line)
        
        # Export - CLEAN TEXT FORMAT
        st.markdown("---")
        st.markdown("#### 📤 Export Audit Report")
        
        # Build clean export text - NO COMPLEX F-STRINGS
        controller_xg_display = f"{metrics['controller_xg']:.2f}" if result['controller'] else "N/A"
        controller_status = "Elite" if result['controller'] and metrics['controller_xg'] >= 1.6 else "Sub-elite" if result['controller'] else "N/A"
        
        export_text = f"""BRUTBALL v6.0 - AUDIT-READY ANALYSIS REPORT
===========================================
League: {selected_league}
Match: {result['match']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

FINAL DECISION:
• Action: {result['primary_action']}
• Confidence: {result['confidence']:.1f}/10
• Stake: {result['stake_pct']:.2f}% of bankroll

KEY METRICS:
• Home xG ({ctx['home']}): {metrics['home_xg']:.2f} ({'≥1.6' if metrics['home_xg'] >= 1.6 else '<1.6'})
• Away xG ({ctx['away']}): {metrics['away_xg']:.2f} ({'≥1.6' if metrics['away_xg'] >= 1.6 else '<1.6'})
• Combined xG: {metrics['combined_xg']:.2f} ({'≥2.8' if metrics['combined_xg'] >= 2.8 else '<2.8'})
• Max xG (Elite Attack): {metrics['max_xg']:.2f} ({'Elite' if metrics['max_xg'] >= 1.6 else 'Sub-elite'})
• Controller xG: {controller_xg_display} ({controller_status})
• Asymmetry Level: {metrics['asymmetry_level']:.2f} ({'High' if metrics['asymmetry_level'] > 0.5 else 'Moderate' if metrics['asymmetry_level'] > 0.3 else 'Low'})

CONTROLLER ANALYSIS:
• Controller: {result['controller'] if result['controller'] else 'None'}
• Criteria Met: {len(result['controller_criteria'])}/4 ({', '.join(result['controller_criteria']) if result['controller'] else 'N/A'})

STAKE ADJUSTMENTS (AXIOM 10):"""
        
        # Add stake adjustments safely
        if result.get('stake_adjustments'):
            for adj in result['stake_adjustments']:
                export_text += f"\n• {adj}"
        else:
            export_text += "\n• None"
        
        export_text += f"""

DECISION TREE EXECUTION:
{chr(10).join(['• ' + step for step in result['decision_steps']])}

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

if __name__ == "__main__":
    main()
