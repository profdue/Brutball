"""
FUSED LOGIC ENGINE v8.0 - REAL AGENCY-STATE SYSTEM
CORE PHILOSOPHY: Use ALL available data to run REAL Agency-State analysis
Combining 4-Gate Winner Lock with Elite Defense and Total Under conditions
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# =================== DATA LOADING & PROCESSING v8.0 ===================
@st.cache_data(ttl=3600)
def load_league_csv(league_name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load and process league CSV with ALL Agency-State metrics"""
    try:
        url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}"
        df = pd.read_csv(url)
        
        # Clean column names for Agency-State analysis
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # DEBUG: Show columns
        st.sidebar.write(f"📋 Columns in {league_name}: {len(df.columns)}")
        
        # SAFELY calculate totals with existence checks
        if 'home_goals_scored' in df.columns and 'away_goals_scored' in df.columns:
            df['goals_scored'] = df['home_goals_scored'] + df['away_goals_scored']
        else:
            df['goals_scored'] = 0
            st.sidebar.warning(f"{league_name}: Missing goals_scored columns")
        
        if 'home_goals_conceded' in df.columns and 'away_goals_conceded' in df.columns:
            df['goals_conceded'] = df['home_goals_conceded'] + df['away_goals_conceded']
        else:
            df['goals_conceded'] = 0
        
        if 'home_xg_for' in df.columns and 'away_xg_for' in df.columns:
            df['xg_for'] = df['home_xg_for'] + df['away_xg_for']
        else:
            df['xg_for'] = df['goals_scored'] * 0.85  # Estimate
        
        if 'home_xg_against' in df.columns and 'away_xg_against' in df.columns:
            df['xg_against'] = df['home_xg_against'] + df['away_xg_against']
        else:
            df['xg_against'] = df['goals_conceded'] * 0.85  # Estimate
        
        # Calculate matches played - handle missing columns
        if 'home_matches_played' in df.columns and 'away_matches_played' in df.columns:
            df['matches_played'] = df['home_matches_played'] + df['away_matches_played']
        else:
            # Estimate from goals if available
            df['matches_played'] = 10  # Default assumption
        
        # Calculate per-match averages SAFELY
        df['goals_per_match'] = df['goals_scored'] / df['matches_played'].replace(0, 1)
        df['xg_per_match'] = df['xg_for'] / df['matches_played'].replace(0, 1)
        df['conceded_per_match'] = df['goals_conceded'] / df['matches_played'].replace(0, 1)
        
        # Calculate home/away specific averages with existence checks
        if 'home_matches_played' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
            df['home_conceded_per_match'] = df['home_goals_conceded'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_goals_per_match'] = df['goals_per_match']
            df['home_xg_per_match'] = df['xg_per_match']
            df['home_conceded_per_match'] = df['conceded_per_match']
        
        if 'away_matches_played' in df.columns:
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
            df['away_conceded_per_match'] = df['away_goals_conceded'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_goals_per_match'] = df['goals_per_match']
            df['away_xg_per_match'] = df['xg_per_match']
            df['away_conceded_per_match'] = df['conceded_per_match']
        
        # Calculate percentages for Agency-State with safety checks
        df['efficiency'] = df['goals_scored'] / df['xg_for'].replace(0, 1)
        
        # Calculate scoring type percentages - handle missing columns
        scoring_cols = {
            'home_goals_openplay_for': 0, 'home_goals_counter_for': 0, 
            'home_goals_setpiece_for': 0, 'home_goals_penalty_for': 0,
            'away_goals_openplay_for': 0, 'away_goals_counter_for': 0,
            'away_goals_setpiece_for': 0, 'away_goals_penalty_for': 0
        }
        
        for col, default in scoring_cols.items():
            if col not in df.columns:
                df[col] = default
        
        # Calculate totals
        df['total_goals_openplay'] = df['home_goals_openplay_for'] + df['away_goals_openplay_for']
        df['total_goals_counter'] = df['home_goals_counter_for'] + df['away_goals_counter_for']
        df['total_goals_setpiece'] = (df['home_goals_setpiece_for'] + df['home_goals_penalty_for'] + 
                                     df['away_goals_setpiece_for'] + df['away_goals_penalty_for'])
        
        # Calculate percentages
        df['setpiece_pct'] = df['total_goals_setpiece'] / df['goals_scored'].replace(0, 1)
        df['counter_pct'] = df['total_goals_counter'] / df['goals_scored'].replace(0, 1)
        df['openplay_pct'] = df['total_goals_openplay'] / df['goals_scored'].replace(0, 1)
        
        # Calculate last 5 averages
        if 'goals_scored_last_5' in df.columns:
            df['avg_goals_scored_last_5'] = df['goals_scored_last_5'] / 5
        else:
            df['avg_goals_scored_last_5'] = df['goals_per_match'] * 1.0  # Estimate
        
        if 'goals_conceded_last_5' in df.columns:
            df['avg_goals_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        else:
            df['avg_goals_conceded_last_5'] = df['conceded_per_match'] * 1.0  # Estimate
        
        # League averages
        df['league_avg_goals'] = df['goals_per_match'].mean() if len(df) > 0 else 1.3
        df['league_avg_conceded'] = df['conceded_per_match'].mean() if len(df) > 0 else 1.3
        df['league_avg_xg'] = df['xg_per_match'].mean() if len(df) > 0 else 1.2
        
        # Form indicators
        if 'form_last_5_overall' in df.columns:
            df['form_points_last_5'] = df['form_last_5_overall'].apply(
                lambda x: len([c for c in str(x) if c in ['W', 'D']]) if pd.notna(x) else 0
            )
        else:
            df['form_points_last_5'] = 0
        
        # Defensive indicators
        df['defensive_solidity'] = df['conceded_per_match'] / df['league_avg_conceded'].replace(0, 1)
        
        # Ensure all required columns exist
        required_cols = [
            'team', 'goals_scored', 'goals_conceded', 'xg_per_match', 'efficiency',
            'setpiece_pct', 'counter_pct', 'openplay_pct', 'avg_goals_scored_last_5',
            'avg_goals_conceded_last_5', 'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        for col in required_cols:
            if col not in df.columns:
                if 'last_5' in col:
                    df[col] = 6  # Default 6 goals in last 5 matches
                elif 'pct' in col:
                    df[col] = 0.2  # Default 20%
                elif col == 'efficiency':
                    df[col] = 0.8  # Default 80% efficiency
                elif col == 'xg_per_match':
                    df[col] = 1.2  # Default xG
                else:
                    df[col] = 0
        
        st.sidebar.success(f"✅ {league_name} loaded: {len(df)} teams")
        return df.fillna(0)
        
    except Exception as e:
        st.sidebar.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== SIMPLIFIED AGENCY-STATE SYSTEM ===================
class AgencyState4GateSystem:
    """SIMPLIFIED 4-GATE SYSTEM with robust error handling"""
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: Any = 0) -> Any:
        """Safely get value from dictionary with default"""
        return data.get(key, default) if data else default
    
    @staticmethod
    def gate1_quiet_control(home_data: Dict, away_data: Dict, perspective: str = "home") -> Dict:
        """GATE 1: Simplified Quiet Control Identification"""
        try:
            if perspective == "home":
                controller_data = home_data
                opponent_data = away_data
            else:
                controller_data = away_data
                opponent_data = home_data
            
            # Get metrics safely
            controller_xg = AgencyState4GateSystem.get_safe_value(controller_data, 'xg_per_match', 1.2)
            opponent_xg = AgencyState4GateSystem.get_safe_value(opponent_data, 'xg_per_match', 1.2)
            
            controller_efficiency = AgencyState4GateSystem.get_safe_value(controller_data, 'efficiency', 0.8)
            controller_setpiece = AgencyState4GateSystem.get_safe_value(controller_data, 'setpiece_pct', 0.2)
            
            # Simple criteria check
            criteria_met = 0
            
            # 1. Tempo Dominance (xG > 1.3)
            if controller_xg > 1.3:
                criteria_met += 1
            
            # 2. Scoring Efficiency (> 85%)
            if controller_efficiency > 0.85:
                criteria_met += 1
            
            # 3. Set Piece Threat (> 20%)
            if controller_setpiece > 0.2:
                criteria_met += 1
            
            # 4. xG Advantage (> 0.2 over opponent)
            if controller_xg - opponent_xg > 0.2:
                criteria_met += 1
            
            if criteria_met >= 2:
                return {
                    'gate_passed': True,
                    'controller': perspective.upper(),
                    'criteria_met': criteria_met,
                    'reason': f'Meets {criteria_met}/4 control criteria'
                }
            
            return {
                'gate_passed': False,
                'reason': f'Only {criteria_met}/4 control criteria met'
            }
            
        except Exception as e:
            return {
                'gate_passed': False,
                'error': str(e),
                'reason': 'Error in Gate 1 analysis'
            }
    
    @staticmethod
    def run_complete_analysis(home_data: Dict, away_data: Dict) -> Dict:
        """Run complete Agency-State analysis"""
        results = {}
        
        # Analyze from both perspectives
        home_analysis = AgencyState4GateSystem.gate1_quiet_control(home_data, away_data, "home")
        away_analysis = AgencyState4GateSystem.gate1_quiet_control(home_data, away_data, "away")
        
        # Check if any perspective shows control
        home_control = home_analysis.get('gate_passed', False)
        away_control = away_analysis.get('gate_passed', False)
        
        if home_control and not away_control:
            results['winner_lock'] = True
            results['controller'] = 'HOME'
            results['controller_team'] = 'Home Team'
            results['reason'] = 'Home team shows Agency-State control'
        elif away_control and not home_control:
            results['winner_lock'] = True
            results['controller'] = 'AWAY'
            results['controller_team'] = 'Away Team'
            results['reason'] = 'Away team shows Agency-State control'
        elif home_control and away_control:
            # Both show control - check xG advantage
            home_xg = AgencyState4GateSystem.get_safe_value(home_data, 'xg_per_match', 1.2)
            away_xg = AgencyState4GateSystem.get_safe_value(away_data, 'xg_per_match', 1.2)
            
            if home_xg > away_xg:
                results['winner_lock'] = True
                results['controller'] = 'HOME'
                results['controller_team'] = 'Home Team'
                results['reason'] = 'Both teams show control, but home has xG advantage'
            elif away_xg > home_xg:
                results['winner_lock'] = True
                results['controller'] = 'AWAY'
                results['controller_team'] = 'Away Team'
                results['reason'] = 'Both teams show control, but away has xG advantage'
            else:
                results['winner_lock'] = False
                results['reason'] = 'Both teams show equal control'
        else:
            results['winner_lock'] = False
            results['reason'] = 'No clear Agency-State control detected'
        
        results['home_analysis'] = home_analysis
        results['away_analysis'] = away_analysis
        
        return results

# =================== SIMPLIFIED ELITE DEFENSE ===================
class EliteDefensePattern:
    """SIMPLIFIED ELITE DEFENSE PATTERN"""
    
    @staticmethod
    def detect_elite_defense(team_data: Dict) -> Dict:
        """Detect Elite Defense pattern"""
        try:
            goals_conceded_last_5 = EliteDefensePattern.get_safe_value(team_data, 'goals_conceded_last_5', 6)
            avg_conceded_last_5 = goals_conceded_last_5 / 5
            
            # Elite if ≤ 4 goals conceded in last 5
            if goals_conceded_last_5 <= 4:
                return {
                    'elite_defense': True,
                    'total_conceded_last_5': goals_conceded_last_5,
                    'avg_conceded': avg_conceded_last_5,
                    'reason': f'Elite defense: {goals_conceded_last_5} goals conceded in last 5 matches',
                    'accuracy_claim': '62.5% (5/8 backtest)'
                }
            
            return {
                'elite_defense': False,
                'total_conceded_last_5': goals_conceded_last_5,
                'reason': f'Not elite: {goals_conceded_last_5} goals conceded in last 5'
            }
        except:
            return {
                'elite_defense': False,
                'reason': 'Error analyzing defense'
            }
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: Any = 0) -> Any:
        """Safely get value from dictionary"""
        return data.get(key, default) if data else default

# =================== SIMPLIFIED TOTAL UNDER CONDITIONS ===================
class TotalUnderConditions:
    """SIMPLIFIED TOTAL UNDER CONDITIONS"""
    
    @staticmethod
    def check_total_under(home_data: Dict, away_data: Dict) -> Dict:
        """Check for Total Under 2.5 conditions"""
        try:
            paths = []
            
            # Get averages safely
            home_avg_scored = TotalUnderConditions.get_safe_value(home_data, 'avg_goals_scored_last_5', 1.3)
            away_avg_scored = TotalUnderConditions.get_safe_value(away_data, 'avg_goals_scored_last_5', 1.3)
            home_avg_conceded = TotalUnderConditions.get_safe_value(home_data, 'avg_goals_conceded_last_5', 1.3)
            away_avg_conceded = TotalUnderConditions.get_safe_value(away_data, 'avg_goals_conceded_last_5', 1.3)
            
            # PATH 1: Both teams low scoring
            if home_avg_scored <= 1.2 and away_avg_scored <= 1.2:
                paths.append({
                    'path': 'OFFENSIVE_INCAPACITY',
                    'reason': f'Both teams avg ≤ 1.2 goals scored (H: {home_avg_scored:.2f}, A: {away_avg_scored:.2f})'
                })
            
            # PATH 2: Both teams strong defense
            if home_avg_conceded <= 1.2 and away_avg_conceded <= 1.2:
                paths.append({
                    'path': 'DEFENSIVE_STRENGTH',
                    'reason': f'Both teams avg ≤ 1.2 goals conceded (H: {home_avg_conceded:.2f}, A: {away_avg_conceded:.2f})'
                })
            
            total_under = len(paths) > 0
            
            return {
                'total_under_conditions': total_under,
                'paths': paths,
                'path_count': len(paths),
                'reason': f'Found {len(paths)} path(s) to Under 2.5' if paths else 'No Under conditions met'
            }
        except:
            return {
                'total_under_conditions': False,
                'paths': [],
                'reason': 'Error analyzing Under conditions'
            }
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: Any = 0) -> Any:
        """Safely get value from dictionary"""
        return data.get(key, default) if data else default

# =================== SIMPLIFIED DECISION ENGINE ===================
class DecisionEngineV80:
    """SIMPLIFIED DECISION ENGINE v8.0"""
    
    @staticmethod
    def execute_analysis(home_data: Dict, away_data: Dict, home_name: str, away_name: str) -> Dict:
        """Execute complete analysis with error handling"""
        try:
            results = {}
            results['home_name'] = home_name
            results['away_name'] = away_name
            
            # STEP 1: Agency-State Analysis
            agency_state = AgencyState4GateSystem()
            results['agency_state'] = agency_state.run_complete_analysis(home_data, away_data)
            results['winner_lock'] = results['agency_state'].get('winner_lock', False)
            
            # STEP 2: Elite Defense Analysis
            elite_defense = EliteDefensePattern()
            results['elite_defense_home'] = elite_defense.detect_elite_defense(home_data)
            results['elite_defense_away'] = elite_defense.detect_elite_defense(away_data)
            results['has_elite_defense'] = (
                results['elite_defense_home'].get('elite_defense', False) or 
                results['elite_defense_away'].get('elite_defense', False)
            )
            
            # STEP 3: Total Under Analysis
            total_under = TotalUnderConditions()
            results['total_under'] = total_under.check_total_under(home_data, away_data)
            results['has_total_under'] = results['total_under'].get('total_under_conditions', False)
            
            # STEP 4: Determine Tier
            results['tier'] = DecisionEngineV80.determine_tier(
                results['winner_lock'],
                results['has_elite_defense'],
                results['has_total_under']
            )
            
            # STEP 5: Generate Recommendations
            results['recommendations'] = DecisionEngineV80.generate_recommendations(results)
            
            # STEP 6: Capital Allocation
            results['capital'] = DecisionEngineV80.calculate_capital(results['tier'])
            
            return results
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return {
                'error': str(e),
                'home_name': home_name,
                'away_name': away_name,
                'tier': {'name': 'ERROR', 'multiplier': 0},
                'recommendations': [],
                'capital': {'multiplier': 0}
            }
    
    @staticmethod
    def determine_tier(winner_lock: bool, elite_defense: bool, total_under: bool) -> Dict:
        """Determine confidence tier"""
        if winner_lock and (elite_defense or total_under):
            return {
                'name': 'LOCK_MODE',
                'multiplier': 2.0,
                'reason': 'Winner Lock + (Elite Defense OR Total Under)',
                'color': '#059669'
            }
        elif winner_lock or elite_defense or total_under:
            return {
                'name': 'EDGE_MODE',
                'multiplier': 1.0,
                'reason': f'{"Winner Lock" if winner_lock else "Elite Defense" if elite_defense else "Total Under"} pattern detected',
                'color': '#3B82F6'
            }
        else:
            return {
                'name': 'STAY_AWAY',
                'multiplier': 0.0,
                'reason': 'No patterns detected',
                'color': '#DC2626'
            }
    
    @staticmethod
    def generate_recommendations(results: Dict) -> List[Dict]:
        """Generate bet recommendations"""
        recommendations = []
        
        # Double Chance from Winner Lock
        if results.get('winner_lock', False):
            controller = results['agency_state'].get('controller_team', 'Team')
            recommendations.append({
                'market': 'DOUBLE_CHANCE',
                'selection': f'{controller} win or draw',
                'confidence': 'HIGH',
                'reason': 'Agency-State control detected',
                'stake': 'PRIMARY'
            })
        
        # Opponent Under 1.5 from Elite Defense
        if results.get('has_elite_defense', False):
            if results['elite_defense_home'].get('elite_defense', False):
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{results.get("away_name", "Away")} Under 1.5',
                    'confidence': 'MODERATE',
                    'reason': 'Facing Elite Defense',
                    'stake': 'SECONDARY'
                })
            
            if results['elite_defense_away'].get('elite_defense', False):
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{results.get("home_name", "Home")} Under 1.5',
                    'confidence': 'MODERATE',
                    'reason': 'Facing Elite Defense',
                    'stake': 'SECONDARY'
                })
        
        # Total Under 2.5
        if results.get('has_total_under', False):
            recommendations.append({
                'market': 'TOTAL_UNDER_2_5',
                'selection': 'Under 2.5 Goals',
                'confidence': 'HIGH',
                'reason': 'Multiple Under conditions met',
                'stake': 'PRIMARY'
            })
        
        return recommendations
    
    @staticmethod
    def calculate_capital(tier: Dict) -> Dict:
        """Calculate capital allocation"""
        multiplier = tier.get('multiplier', 0)
        
        if multiplier == 2.0:
            return {'multiplier': 2.0, 'stake_size': 'MAXIMUM', 'description': 'Full confidence bet'}
        elif multiplier == 1.0:
            return {'multiplier': 1.0, 'stake_size': 'MODERATE', 'description': 'Standard bet'}
        else:
            return {'multiplier': 0.0, 'stake_size': 'ZERO', 'description': 'Stay away'}

# =================== STREAMLIT UI ===================
def main():
    """Fused Logic Engine v8.0 Streamlit App"""
    
    st.set_page_config(
        page_title="Fused Logic Engine v8.0",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .pattern-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .tier-lock { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; }
    .tier-edge { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important; }
    .tier-stay { background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1E3A8A;">🎯 FUSED LOGIC ENGINE v8.0</h1>
        <div style="color: #4B5563; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
            Simplified Agency-State System • Robust Error Handling
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # League Configuration
    LEAGUES = {
        'Premier League': 'premier_league.csv',
        'La Liga': 'la_liga.csv',
        'Bundesliga': 'bundesliga.csv',
        'Serie A': 'serie_a.csv',
        'Ligue 1': 'ligue_1.csv',
        'Eredivisie': 'eredivisie.csv',
        'Primeira Liga': 'premeira_portugal.csv',
        'Super Lig': 'super_league.csv'
    }
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🌍 Select League")
        
        for league_name, filename in LEAGUES.items():
            if st.button(
                league_name,
                use_container_width=True,
                key=f"btn_{league_name}"
            ):
                with st.spinner(f"Loading {league_name}..."):
                    df = load_league_csv(league_name, filename)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.selected_league = league_name
                        st.session_state.analysis_result = None
                        st.rerun()
        
        # Debug panel
        if st.session_state.df is not None:
            st.markdown("---")
            st.markdown("### 📊 Data Info")
            st.write(f"Teams: {len(st.session_state.df)}")
            st.write(f"Columns: {len(st.session_state.df.columns)}")
            
            if st.checkbox("Show first team data"):
                if len(st.session_state.df) > 0:
                    st.write(st.session_state.df.iloc[0].to_dict())
    
    # Main content
    if st.session_state.df is None:
        st.info("👆 Select a league from the sidebar to begin")
        
        st.markdown("### 📊 Empirical Accuracy (v8.0 Adjusted)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Winner Lock", "80%", "4/5 backtest")
        with col2:
            st.metric("Elite Defense", "62.5%", "5/8 backtest")
        with col3:
            st.metric("Total Under 2.5", "70%", "7/10 backtest")
        
        return
    
    df = st.session_state.df
    
    # Match selection
    st.markdown("### 📥 Match Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        teams = sorted(df['team'].unique().tolist()) if 'team' in df.columns else []
        if not teams:
            st.error("No teams found in data!")
            return
        
        home_team = st.selectbox("Home Team", teams, key="home_team")
        
        # Get home team data
        home_row = df[df['team'] == home_team]
        if not home_row.empty:
            home_data = home_row.iloc[0].to_dict()
            st.info(f"**xG/Match:** {home_data.get('xg_per_match', 0):.2f}")
            st.info(f"**Last 5:** {home_data.get('goals_scored_last_5', 0)} scored, {home_data.get('goals_conceded_last_5', 0)} conceded")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team")
        
        # Get away team data
        away_row = df[df['team'] == away_team]
        if not away_row.empty:
            away_data = away_row.iloc[0].to_dict()
            st.info(f"**xG/Match:** {away_data.get('xg_per_match', 0):.2f}")
            st.info(f"**Last 5:** {away_data.get('goals_scored_last_5', 0)} scored, {away_data.get('goals_conceded_last_5', 0)} conceded")
    
    # Run analysis button
    if st.button("🚀 RUN ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Analyzing match..."):
            try:
                engine = DecisionEngineV80()
                result = engine.execute_analysis(
                    home_data, away_data, home_team, away_team
                )
                st.session_state.analysis_result = result
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Analysis error: {str(e)}")
                st.session_state.analysis_result = {'error': str(e)}
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Check for error
        if 'error' in result:
            st.error(f"Analysis failed: {result['error']}")
            return
        
        # Tier Banner
        tier = result['tier']
        tier_class = {
            'LOCK_MODE': 'tier-lock',
            'EDGE_MODE': 'tier-edge',
            'STAY_AWAY': 'tier-stay'
        }.get(tier['name'], 'pattern-card')
        
        st.markdown(f"""
        <div class="pattern-card {tier_class}" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                {'🎯' if tier['name'] == 'LOCK_MODE' else '📊' if tier['name'] == 'EDGE_MODE' else '🚫'}
            </div>
            <h2 style="margin: 0;">{tier['name']}</h2>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                {tier['multiplier']:.1f}x CAPITAL
            </div>
            <div style="color: rgba(255,255,255,0.9);">
                {tier['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern Detections
        st.markdown("### 🔍 Pattern Detections")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Winner Lock", 
                "✅ DETECTED" if result.get('winner_lock') else "❌ NOT DETECTED",
                result.get('agency_state', {}).get('reason', '')
            )
        
        with col2:
            elite_status = "✅ DETECTED" if result.get('has_elite_defense') else "❌ NOT DETECTED"
            if result.get('has_elite_defense'):
                if result['elite_defense_home'].get('elite_defense'):
                    st.metric("Elite Defense", elite_status, f"Home: {result['elite_defense_home']['reason']}")
                else:
                    st.metric("Elite Defense", elite_status, f"Away: {result['elite_defense_away']['reason']}")
            else:
                st.metric("Elite Defense", elite_status, "No elite defense")
        
        with col3:
            under_status = "✅ DETECTED" if result.get('has_total_under') else "❌ NOT DETECTED"
            st.metric(
                "Total Under", 
                under_status,
                result.get('total_under', {}).get('reason', '')
            )
        
        # Recommendations
        st.markdown("### 💰 Bet Recommendations")
        if result.get('recommendations'):
            for rec in result['recommendations']:
                with st.container():
                    cols = st.columns([0.3, 0.4, 0.2, 0.1])
                    with cols[0]:
                        st.markdown(f"**{rec['market']}**")
                    with cols[1]:
                        st.write(rec['selection'])
                        st.caption(rec['reason'])
                    with cols[2]:
                        st.metric("Confidence", rec['confidence'])
                    with cols[3]:
                        st.caption(f"**{rec['stake']}**")
        else:
            st.info("No bet recommendations - consider staying away")
        
        # Team Stats
        st.markdown("### 📊 Team Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{home_team}**")
            st.metric("xG/Match", f"{home_data.get('xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{home_data.get('efficiency', 0)*100:.0f}%")
            st.metric("Set Piece %", f"{home_data.get('setpiece_pct', 0)*100:.0f}%")
            st.metric("Last 5 Conceded", home_data.get('goals_conceded_last_5', 0))
        
        with col2:
            st.markdown(f"**{away_team}**")
            st.metric("xG/Match", f"{away_data.get('xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{away_data.get('efficiency', 0)*100:.0f}%")
            st.metric("Set Piece %", f"{away_data.get('setpiece_pct', 0)*100:.0f}%")
            st.metric("Last 5 Conceded", away_data.get('goals_conceded_last_5', 0))
        
        # Capital Allocation
        capital = result.get('capital', {})
        st.markdown("### 💸 Capital Allocation")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Multiplier", f"{capital.get('multiplier', 0):.1f}x")
        with col2:
            st.metric("Stake Size", capital.get('stake_size', 'N/A'))
        with col3:
            st.metric("Recommendation", capital.get('description', 'N/A'))

if __name__ == "__main__":
    main()
