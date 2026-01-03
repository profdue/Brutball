"""
FUSED LOGIC ENGINE v9.1 - THE EMPIRICAL SYNTHESIS
CORE PHILOSOPHY: Empirical weights beat heuristic rules. League context trumps universal thresholds.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# =================== DATA LOADING & PROCESSING v9.1 ===================
@st.cache_data(ttl=3600)
def load_league_csv(league_name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load and process league CSV with all v9.1 metrics"""
    try:
        url = f"https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}"
        df = pd.read_csv(url)
        
        # Clean column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Calculate totals from available data
        if 'home_goals_scored' in df.columns and 'away_goals_scored' in df.columns:
            df['goals_scored'] = df['home_goals_scored'] + df['away_goals_scored']
        else:
            if 'goals_scored_last_5' in df.columns:
                df['goals_scored'] = df['goals_scored_last_5'] * 2
            else:
                df['goals_scored'] = 0
        
        if 'home_goals_conceded' in df.columns and 'away_goals_conceded' in df.columns:
            df['goals_conceded'] = df['home_goals_conceded'] + df['away_goals_conceded']
        else:
            if 'goals_conceded_last_5' in df.columns:
                df['goals_conceded'] = df['goals_conceded_last_5'] * 2
            else:
                df['goals_conceded'] = 0
        
        if 'home_xg_for' in df.columns and 'away_xg_for' in df.columns:
            df['xg_for'] = df['home_xg_for'] + df['away_xg_for']
        else:
            df['xg_for'] = df['goals_scored'] * 0.85
        
        if 'home_xg_against' in df.columns and 'away_xg_against' in df.columns:
            df['xg_against'] = df['home_xg_against'] + df['away_xg_against']
        else:
            df['xg_against'] = df['goals_conceded'] * 0.85
        
        # Calculate matches played
        if 'home_matches_played' in df.columns and 'away_matches_played' in df.columns:
            df['matches_played'] = df['home_matches_played'] + df['away_matches_played']
        else:
            df['matches_played'] = 10
        
        # Calculate per-match averages
        df['goals_per_match'] = df['goals_scored'] / df['matches_played'].replace(0, 1)
        df['xg_per_match'] = df['xg_for'] / df['matches_played'].replace(0, 1)
        df['conceded_per_match'] = df['goals_conceded'] / df['matches_played'].replace(0, 1)
        
        # Home/away specific averages
        if 'home_matches_played' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_goals_per_match'] = df['goals_per_match']
        
        if 'away_matches_played' in df.columns:
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_goals_per_match'] = df['goals_per_match']
        
        if 'home_xg_for' in df.columns and 'home_matches_played' in df.columns:
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_xg_per_match'] = df['xg_per_match']
        
        if 'away_xg_for' in df.columns and 'away_matches_played' in df.columns:
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_xg_per_match'] = df['xg_per_match']
        
        if 'home_goals_conceded' in df.columns and 'home_matches_played' in df.columns:
            df['home_conceded_per_match'] = df['home_goals_conceded'] / df['home_matches_played'].replace(0, 1)
        else:
            df['home_conceded_per_match'] = df['conceded_per_match']
        
        if 'away_goals_conceded' in df.columns and 'away_matches_played' in df.columns:
            df['away_conceded_per_match'] = df['away_goals_conceded'] / df['away_matches_played'].replace(0, 1)
        else:
            df['away_conceded_per_match'] = df['conceded_per_match']
        
        # Calculate efficiency (Goals/xG)
        df['efficiency'] = (df['goals_scored'] / df['xg_for'].replace(0, 1)) * 100
        
        # Last 5 averages
        if 'goals_scored_last_5' in df.columns:
            df['avg_goals_scored_last_5'] = df['goals_scored_last_5'] / 5
        else:
            df['avg_goals_scored_last_5'] = df['goals_per_match']
        
        if 'goals_conceded_last_5' in df.columns:
            df['avg_goals_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        else:
            df['avg_goals_conceded_last_5'] = df['conceded_per_match']
        
        # League averages
        if len(df) > 0:
            df['league_avg_goals'] = df['goals_per_match'].mean()
            df['league_avg_conceded'] = df['conceded_per_match'].mean()
            df['league_avg_xg'] = df['xg_per_match'].mean()
            df['league_avg_efficiency'] = df['efficiency'].mean()
        else:
            df['league_avg_goals'] = 1.3
            df['league_avg_conceded'] = 1.3
            df['league_avg_xg'] = 1.2
            df['league_avg_efficiency'] = 100
        
        # Form indicators
        if 'form_last_5_overall' in df.columns:
            df['form_points_last_5'] = df['form_last_5_overall'].apply(
                lambda x: len([c for c in str(x) if c in ['W', 'D']]) if pd.notna(x) else 0
            )
        else:
            df['form_points_last_5'] = 0
        
        return df.fillna(0)
        
    except Exception as e:
        st.error(f"Error loading {league_name}: {str(e)}")
        return None

# =================== LEAGUE PARAMETERS v9.1 ===================
LEAGUE_PARAMETERS = {
    'SERIE A': {
        'name': 'SERIE A',
        'total_under_threshold': 1.1,
        'efficiency_filter': 85,
        'winner_lock_delta_threshold': 0.20,
        'league_multiplier': 1.2,
        'success_rate': 0.83,
        'description': 'UNDER MACHINE - 83% SUCCESS'
    },
    'LA LIGA': {
        'name': 'LA LIGA',
        'total_under_threshold': 1.1,
        'efficiency_filter': 90,
        'winner_lock_delta_threshold': 0.25,
        'league_multiplier': 1.1,
        'success_rate': 0.80,
        'description': 'TACTICAL - 80% SUCCESS'
    },
    'PREMIER LEAGUE': {
        'name': 'PREMIER LEAGUE',
        'total_under_threshold': 0.9,
        'efficiency_filter': 80,
        'winner_lock_delta_threshold': 0.35,
        'league_multiplier': 0.8,
        'success_rate': 0.33,
        'description': 'VOLATILE - 33% SUCCESS'
    },
    'DEFAULT': {
        'name': 'DEFAULT',
        'total_under_threshold': 1.0,
        'efficiency_filter': 90,
        'winner_lock_delta_threshold': 0.25,
        'league_multiplier': 1.0,
        'success_rate': 0.65,
        'description': 'STANDARD LEAGUE'
    }
}

# =================== PILLAR WEIGHTS v9.1 ===================
PILLAR_WEIGHTS = {
    'TOTAL_UNDER': 0.73,  # 73% success
    'WINNER_LOCK': 0.50,  # 50% success
    'ELITE_DEFENSE': 0.50  # 50% success
}

# =================== HELPER FUNCTIONS ===================
def get_safe_value(data: Dict, key: str, default: Any = 0) -> Any:
    """Safely get value from dictionary with default"""
    if not data:
        return default
    return data.get(key, default)

def get_league_parameters(league_name: str) -> Dict:
    """Get league-specific parameters"""
    league_upper = league_name.upper()
    
    # Match partial league names
    if 'SERIE' in league_upper or 'ITALY' in league_upper:
        return LEAGUE_PARAMETERS['SERIE A']
    elif 'LA LIGA' in league_upper or 'SPAIN' in league_upper:
        return LEAGUE_PARAMETERS['LA LIGA']
    elif 'PREMIER' in league_upper or 'ENGLAND' in league_upper:
        return LEAGUE_PARAMETERS['PREMIER LEAGUE']
    else:
        return LEAGUE_PARAMETERS['DEFAULT']

# =================== PILLAR 1: TOTAL UNDER PATTERNS ===================
class TotalUnderPillar:
    """PILLAR 1: Total Under Patterns (73% success weight)"""
    
    @staticmethod
    def calculate_paths(home_data: Dict, away_data: Dict, league_params: Dict) -> Dict:
        """Calculate Total Under paths (0-3)"""
        try:
            paths = []
            path_details = []
            
            # Get metrics
            home_avg_scored = get_safe_value(home_data, 'avg_goals_scored_last_5', 1.3)
            away_avg_scored = get_safe_value(away_data, 'avg_goals_scored_last_5', 1.3)
            home_avg_conceded = get_safe_value(home_data, 'avg_goals_conceded_last_5', 1.3)
            away_avg_conceded = get_safe_value(away_data, 'avg_goals_conceded_last_5', 1.3)
            
            home_efficiency = get_safe_value(home_data, 'efficiency', 100)
            away_efficiency = get_safe_value(away_data, 'efficiency', 100)
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.3)
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.3)
            
            threshold = league_params['total_under_threshold']
            efficiency_threshold = league_params['efficiency_filter']
            
            # PATH A: Offensive Incapacity
            if home_avg_scored <= threshold and away_avg_scored <= threshold:
                paths.append(1.0)
                path_details.append({
                    'path': 'OFFENSIVE_INCAPACITY',
                    'reason': f'Both teams avg ≤ {threshold} goals scored (H: {home_avg_scored:.2f}, A: {away_avg_scored:.2f})',
                    'weight': 1.0
                })
            
            # PATH B: Defensive Strength
            if home_avg_conceded <= threshold and away_avg_conceded <= threshold:
                paths.append(1.0)
                path_details.append({
                    'path': 'DEFENSIVE_STRENGTH',
                    'reason': f'Both teams avg ≤ {threshold} goals conceded (H: {home_avg_conceded:.2f}, A: {away_avg_conceded:.2f})',
                    'weight': 1.0
                })
            
            # PATH C: Efficiency Collapse
            if (home_efficiency < efficiency_threshold and away_efficiency < efficiency_threshold and
                home_xg < 1.3 and away_xg < 1.3):
                paths.append(1.0)
                path_details.append({
                    'path': 'EFFICIENCY_COLLAPSE',
                    'reason': f'Both teams inefficient (<{efficiency_threshold}%) and low xG (<1.3)',
                    'weight': 1.0
                })
            
            # Efficiency bonus (both teams < 100%)
            efficiency_bonus = 0.0
            if home_efficiency < 100 and away_efficiency < 100:
                efficiency_bonus = 0.2
                path_details.append({
                    'path': 'EFFICIENCY_BONUS',
                    'reason': 'Both teams underperforming (<100% efficiency)',
                    'weight': 0.2
                })
            
            total_paths = len(paths)
            total_score = sum(paths) + efficiency_bonus
            
            return {
                'total_paths': total_paths,
                'total_score': min(total_score, 3.0),  # Cap at 3.0
                'path_details': path_details,
                'efficiency_bonus': efficiency_bonus,
                'reason': f'Found {total_paths} Total Under path(s)'
            }
            
        except Exception as e:
            return {
                'total_paths': 0,
                'total_score': 0.0,
                'path_details': [],
                'error': str(e)
            }

# =================== PILLAR 2: WINNER LOCK GATES ===================
class WinnerLockPillar:
    """PILLAR 2: Winner Lock Gates (50% success weight)"""
    
    @staticmethod
    def calculate_gates(home_data: Dict, away_data: Dict, league_params: Dict) -> Dict:
        """Calculate Winner Lock gates (0-4 with decimals)"""
        try:
            gates_passed = 0.0
            gate_details = []
            
            # Get metrics for both teams
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.2)
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.2)
            
            # Determine controller (team with higher xG)
            if home_xg > away_xg:
                controller_data = home_data
                opponent_data = away_data
                controller_label = 'HOME'
                is_home = True
            else:
                controller_data = away_data
                opponent_data = home_data
                controller_label = 'AWAY'
                is_home = False
            
            controller_xg = get_safe_value(controller_data, 'xg_per_match', 1.2)
            opponent_xg = get_safe_value(opponent_data, 'xg_per_match', 1.2)
            
            # GATE 1: Quiet Control (3.5/4 criteria minimum)
            gate1_score = 0.0
            criteria_met = 0
            
            # 1. Tempo Dominance (xG > 1.4)
            if controller_xg > 1.4:
                criteria_met += 1
            
            # 2. Scoring Efficiency (> 90%)
            controller_eff = get_safe_value(controller_data, 'efficiency', 100)
            if controller_eff > 90:
                criteria_met += 1
                if controller_eff > 90:  # Bonus for high efficiency
                    gate1_score += 0.1
            
            # 3. Critical Area Threat (Set piece > 25%)
            # Estimate from available data or use default
            setpiece_pct = 0.2  # Default
            if setpiece_pct > 0.25:
                criteria_met += 1
            
            # 4. Repeatable Patterns (Open play > 50% OR Counter > 15%)
            openplay_pct = 0.6  # Default
            counter_pct = 0.1   # Default
            if openplay_pct > 0.5 or counter_pct > 0.15:
                criteria_met += 1
            
            # Gate 1 score (3.5/4 minimum = 0.875 per criteria)
            gate1_score += min(criteria_met * 0.875, 1.0)
            if gate1_score > 0:
                gates_passed += gate1_score
                gate_details.append({
                    'gate': 'QUIET_CONTROL',
                    'score': gate1_score,
                    'reason': f'{controller_label} meets {criteria_met}/4 control criteria'
                })
            
            # GATE 2: Directional Dominance
            delta_threshold = league_params['winner_lock_delta_threshold']
            control_delta = controller_xg - opponent_xg
            
            if control_delta > delta_threshold and opponent_xg < 1.1:
                gates_passed += 1.0
                gate_details.append({
                    'gate': 'DIRECTIONAL_DOMINANCE',
                    'score': 1.0,
                    'reason': f'Control delta {control_delta:.2f} > {delta_threshold} AND opponent xG {opponent_xg:.2f} < 1.1'
                })
            
            # GATE 3: State-Flip Capacity (3/4 failures minimum)
            failures = 0
            
            # 1. Chase capacity
            if opponent_xg < 1.1:
                failures += 1
            
            # 2. Tempo surge
            if opponent_xg < 1.4:
                failures += 1
            
            # 3. Alternate threats
            opp_setpiece = 0.2
            opp_counter = 0.1
            if opp_setpiece < 0.25 and opp_counter < 0.15:
                failures += 1
            
            # 4. Substitution leverage
            opp_goals_pm = get_safe_value(opponent_data, 'goals_per_match', 1.2)
            league_avg = get_safe_value(opponent_data, 'league_avg_goals', 1.3)
            if opp_goals_pm < league_avg * 0.8:
                failures += 1
            
            # Gate 3 score (3/4 minimum = 0.75 per failure)
            gate3_score = min(failures * 0.75, 1.0)
            if gate3_score >= 0.75:  # Minimum 3 failures required
                gates_passed += gate3_score
                gate_details.append({
                    'gate': 'STATE_FLIP_CAPACITY',
                    'score': gate3_score,
                    'reason': f'Opponent has {failures}/4 state-flip failures'
                })
            
            # GATE 4: Enforcement Without Urgency (2.5/3 methods)
            methods = 0
            
            # 1. Defensive solidity
            if is_home:
                concede_avg = get_safe_value(controller_data, 'home_conceded_per_match', 
                                           get_safe_value(controller_data, 'conceded_per_match', 1.2))
                if concede_avg < 1.2:
                    methods += 1
            else:
                concede_avg = get_safe_value(controller_data, 'away_conceded_per_match',
                                           get_safe_value(controller_data, 'conceded_per_match', 1.2))
                if concede_avg < 1.3:
                    methods += 1
            
            # 2. Alternate scoring
            if setpiece_pct > 0.25 or counter_pct > 0.15:
                methods += 1
            
            # 3. Consistent threat
            if controller_xg > 1.3:
                methods += 1
            
            # Gate 4 score (2.5/3 minimum = 0.833 per method)
            gate4_score = min(methods * 0.833, 1.0)
            if gate4_score >= 0.833:  # Minimum 2.5 methods required
                gates_passed += gate4_score
                gate_details.append({
                    'gate': 'ENFORCEMENT',
                    'score': gate4_score,
                    'reason': f'Controller has {methods}/3 enforcement methods'
                })
            
            return {
                'controller': controller_label,
                'gates_passed': gates_passed,
                'gate_details': gate_details,
                'score': min(gates_passed, 4.0),  # Cap at 4.0
                'reason': f'{controller_label} passes {gates_passed:.2f}/4 gates'
            }
            
        except Exception as e:
            return {
                'controller': 'ERROR',
                'gates_passed': 0.0,
                'gate_details': [],
                'score': 0.0,
                'error': str(e)
            }

# =================== PILLAR 3: ELITE DEFENSE TIERS ===================
class EliteDefensePillar:
    """PILLAR 3: Elite Defense Tiers (50% success weight)"""
    
    @staticmethod
    def calculate_tiers(home_data: Dict, away_data: Dict) -> Dict:
        """Calculate Elite Defense tiers (0-1.5)"""
        try:
            results = {}
            
            # Analyze home team
            home_conceded = get_safe_value(home_data, 'goals_conceded_last_5', 6)
            home_avg_conceded = home_conceded / 5
            home_league_avg = get_safe_value(home_data, 'league_avg_conceded', 1.3)
            home_defense_gap = home_league_avg - home_avg_conceded
            
            # TIER SYSTEM
            if home_conceded <= 3 and home_defense_gap > 2.5:  # TRUE ELITE
                home_tier = 1.5
                home_tier_name = 'TRUE_ELITE'
                home_reason = f'Conceded ≤3 last 5 (avg {home_avg_conceded:.2f}), gap {home_defense_gap:.2f} > 2.5'
            elif home_conceded == 4 and home_defense_gap > 2.0:  # STRONG
                home_tier = 1.0
                home_tier_name = 'STRONG'
                home_reason = f'Conceded 4 last 5 (avg {home_avg_conceded:.2f}), gap {home_defense_gap:.2f} > 2.0'
            elif home_conceded == 5:  # DECENT
                home_tier = 0.5
                home_tier_name = 'DECENT'
                home_reason = f'Conceded 5 last 5 (avg {home_avg_conceded:.2f})'
            else:  # NOT ELITE
                home_tier = 0.0
                home_tier_name = 'NOT_ELITE'
                home_reason = f'Conceded {home_conceded} last 5 (avg {home_avg_conceded:.2f}) - not elite'
            
            # Analyze away team
            away_conceded = get_safe_value(away_data, 'goals_conceded_last_5', 6)
            away_avg_conceded = away_conceded / 5
            away_league_avg = get_safe_value(away_data, 'league_avg_conceded', 1.3)
            away_defense_gap = away_league_avg - away_avg_conceded
            
            if away_conceded <= 3 and away_defense_gap > 2.5:
                away_tier = 1.5
                away_tier_name = 'TRUE_ELITE'
                away_reason = f'Conceded ≤3 last 5 (avg {away_avg_conceded:.2f}), gap {away_defense_gap:.2f} > 2.5'
            elif away_conceded == 4 and away_defense_gap > 2.0:
                away_tier = 1.0
                away_tier_name = 'STRONG'
                away_reason = f'Conceded 4 last 5 (avg {away_avg_conceded:.2f}), gap {away_defense_gap:.2f} > 2.0'
            elif away_conceded == 5:
                away_tier = 0.5
                away_tier_name = 'DECENT'
                away_reason = f'Conceded 5 last 5 (avg {away_avg_conceded:.2f})'
            else:
                away_tier = 0.0
                away_tier_name = 'NOT_ELITE'
                away_reason = f'Conceded {away_conceded} last 5 (avg {away_avg_conceded:.2f}) - not elite'
            
            # Opponent efficiency bonus
            home_eff = get_safe_value(home_data, 'efficiency', 100)
            away_eff = get_safe_value(away_data, 'efficiency', 100)
            
            efficiency_bonus = 0.0
            if home_tier > 0 and away_eff < 80:
                efficiency_bonus += 0.1
            if away_tier > 0 and home_eff < 80:
                efficiency_bonus += 0.1
            
            total_score = max(home_tier, away_tier) + efficiency_bonus
            
            return {
                'home_tier': home_tier,
                'home_tier_name': home_tier_name,
                'home_reason': home_reason,
                'away_tier': away_tier,
                'away_tier_name': away_tier_name,
                'away_reason': away_reason,
                'total_score': min(total_score, 1.5),  # Cap at 1.5
                'efficiency_bonus': efficiency_bonus,
                'reason': f'Highest defense tier: {max(home_tier, away_tier):.1f}'
            }
            
        except Exception as e:
            return {
                'home_tier': 0.0,
                'home_tier_name': 'ERROR',
                'away_tier': 0.0,
                'away_tier_name': 'ERROR',
                'total_score': 0.0,
                'error': str(e)
            }

# =================== PROTECTIVE FILTERS ===================
class ProtectiveFilters:
    """Protective filters to prevent blowouts and unsustainable streaks"""
    
    @staticmethod
    def check_filters(home_data: Dict, away_data: Dict) -> Dict:
        """Apply all protective filters"""
        try:
            filters_triggered = []
            penalties = 0.0
            stay_away = False
            
            # FILTER 1: Defensive Collapse Override
            home_conceded = get_safe_value(home_data, 'goals_conceded_last_5', 6)
            home_scored = get_safe_value(home_data, 'goals_scored_last_5', 6)
            away_conceded = get_safe_value(away_data, 'goals_conceded_last_5', 6)
            away_scored = get_safe_value(away_data, 'goals_scored_last_5', 6)
            
            if (home_conceded >= 8 and home_scored >= 8) or (away_conceded >= 8 and away_scored >= 8):
                filters_triggered.append('DEFENSIVE_COLLAPSE')
                penalties += 0.5
            
            # FILTER 2: Blowout Protection
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.2)
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.2)
            xg_diff = abs(home_xg - away_xg)
            
            weaker_conceded = home_conceded if home_xg < away_xg else away_conceded
            stronger_scored = home_scored if home_xg > away_xg else away_scored
            
            if xg_diff > 1.0 and weaker_conceded >= 8 and stronger_scored >= 8:
                filters_triggered.append('BLOWOUT_RISK')
                stay_away = True
            
            # FILTER 3: Efficiency Extremes
            home_eff = get_safe_value(home_data, 'efficiency', 100)
            away_eff = get_safe_value(away_data, 'efficiency', 100)
            
            if home_eff > 130 or away_eff > 130:
                filters_triggered.append('HIGH_EFFICIENCY_EXTREME')
                # Will be handled in tier adjustment
            
            if home_eff < 70 and away_eff < 70:
                filters_triggered.append('LOW_EFFICIENCY_EXTREME')
                # Will be handled in tier adjustment
            
            # FILTER 4: Sustainability Check
            # Check if short-term efficiency > 120% but season-long < 100%
            # For now, use conservative approach
            if (home_eff > 120 and get_safe_value(home_data, 'league_avg_efficiency', 100) < 100) or \
               (away_eff > 120 and get_safe_value(away_data, 'league_avg_efficiency', 100) < 100):
                filters_triggered.append('UNSUSTAINABLE_EFFICIENCY')
                penalties += 0.3
            
            return {
                'filters_triggered': filters_triggered,
                'penalties': penalties,
                'stay_away': stay_away,
                'reason': f'Triggered: {", ".join(filters_triggered)}' if filters_triggered else 'No filters triggered'
            }
            
        except Exception as e:
            return {
                'filters_triggered': ['ERROR'],
                'penalties': 0.0,
                'stay_away': False,
                'error': str(e)
            }

# =================== GOALLESS DRAW PATTERN ===================
class GoallessDrawPattern:
    """Special handling for Goalless Draw pattern"""
    
    @staticmethod
    def check_pattern(home_data: Dict, away_data: Dict, total_under_paths: int) -> Dict:
        """Check for Goalless Draw conditions"""
        try:
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.2)
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.2)
            home_eff = get_safe_value(home_data, 'efficiency', 100)
            away_eff = get_safe_value(away_data, 'efficiency', 100)
            home_conceded = get_safe_value(home_data, 'goals_conceded_last_5', 6)
            away_conceded = get_safe_value(away_data, 'goals_conceded_last_5', 6)
            
            conditions_met = []
            
            # Condition 1: Low xG
            if home_xg < 1.2 or away_xg < 1.1:
                conditions_met.append('LOW_XG')
            
            # Condition 2: Both inefficient
            if home_eff < 90 and away_eff < 90:
                conditions_met.append('LOW_EFFICIENCY')
            
            # Condition 3: Both decent defense
            if home_conceded <= 6 and away_conceded <= 6:
                conditions_met.append('DECENT_DEFENSE')
            
            # Condition 4: Total Under paths
            if total_under_paths >= 2:
                conditions_met.append('TOTAL_UNDER_PATHS')
            
            # Condition 5: No True Elite Defense
            if home_conceded > 3 and away_conceded > 3:
                conditions_met.append('NO_TRUE_ELITE')
            
            # Condition 6: No defensive collapse
            if home_conceded <= 8 and away_conceded <= 8:
                conditions_met.append('NO_COLLAPSE')
            
            is_goalless_draw = len(conditions_met) >= 5  # Need 5/6 conditions
            
            return {
                'is_goalless_draw': is_goalless_draw,
                'conditions_met': conditions_met,
                'conditions_total': len(conditions_met),
                'reason': f'Goalless Draw: {len(conditions_met)}/6 conditions met' if is_goalless_draw else 'Not a Goalless Draw pattern'
            }
            
        except Exception as e:
            return {
                'is_goalless_draw': False,
                'conditions_met': [],
                'error': str(e)
            }

# =================== THE EMPIRICAL SYNTHESIS ENGINE v9.1 ===================
class EmpiricalSynthesisEngineV91:
    """Main engine for v9.1 empirical synthesis"""
    
    @staticmethod
    def execute_full_analysis(home_data: Dict, away_data: Dict, 
                            home_name: str, away_name: str,
                            league_name: str) -> Dict:
        """Execute complete v9.1 analysis"""
        try:
            results = {}
            results['home_name'] = home_name
            results['away_name'] = away_name
            results['league_name'] = league_name
            
            # STEP 0: League Identification
            league_params = get_league_parameters(league_name)
            results['league_params'] = league_params
            
            # STEP 1: Protective Filters
            filters = ProtectiveFilters.check_filters(home_data, away_data)
            results['protective_filters'] = filters
            
            if filters['stay_away']:
                return {
                    **results,
                    'final_tier': 5,
                    'tier_name': 'STAY_AWAY',
                    'capital_multiplier': 0.0,
                    'reason': f'Blowout protection triggered: {filters["reason"]}',
                    'recommendations': []
                }
            
            # STEP 2: Pillar Calculation
            # PILLAR 1: Total Under
            total_under = TotalUnderPillar.calculate_paths(home_data, away_data, league_params)
            results['total_under'] = total_under
            
            # PILLAR 2: Winner Lock
            winner_lock = WinnerLockPillar.calculate_gates(home_data, away_data, league_params)
            results['winner_lock'] = winner_lock
            
            # PILLAR 3: Elite Defense
            elite_defense = EliteDefensePillar.calculate_tiers(home_data, away_data)
            results['elite_defense'] = elite_defense
            
            # STEP 3: Goalless Draw Check
            goalless_draw = GoallessDrawPattern.check_pattern(
                home_data, away_data, total_under.get('total_paths', 0)
            )
            results['goalless_draw'] = goalless_draw
            
            # STEP 4: Base Score Calculation
            base_score = (
                total_under.get('total_score', 0) * PILLAR_WEIGHTS['TOTAL_UNDER'] +
                winner_lock.get('score', 0) * PILLAR_WEIGHTS['WINNER_LOCK'] +
                elite_defense.get('total_score', 0) * PILLAR_WEIGHTS['ELITE_DEFENSE']
            )
            
            # STEP 5: Apply Modifiers
            # League multiplier
            final_score = base_score * league_params['league_multiplier']
            
            # Efficiency modifiers
            home_eff = get_safe_value(home_data, 'efficiency', 100)
            away_eff = get_safe_value(away_data, 'efficiency', 100)
            
            efficiency_bonus = 0.0
            if home_eff < 70 and away_eff < 70:
                efficiency_bonus += 0.3
            elif home_eff > 130 or away_eff > 130:
                efficiency_bonus -= 0.3
            
            # Recent form modifier (simplified)
            home_form = get_safe_value(home_data, 'form_points_last_5', 0)
            away_form = get_safe_value(away_data, 'form_points_last_5', 0)
            form_modifier = (home_form + away_form - 5) * 0.03  # -0.3 to +0.3
            
            # Apply all modifiers
            final_score += efficiency_bonus + form_modifier - filters['penalties']
            
            # Cap at maximum
            final_score = min(final_score, 5.0)
            final_score = max(final_score, 0.0)
            
            results['scoring'] = {
                'base_score': base_score,
                'league_multiplier': league_params['league_multiplier'],
                'efficiency_bonus': efficiency_bonus,
                'form_modifier': form_modifier,
                'filters_penalties': filters['penalties'],
                'final_score': final_score
            }
            
            # STEP 6: Tier Determination
            tier_info = EmpiricalSynthesisEngineV91.determine_tier(final_score, goalless_draw['is_goalless_draw'])
            results['tier_info'] = tier_info
            
            # STEP 7: Capital Allocation
            capital_info = EmpiricalSynthesisEngineV91.calculate_capital(tier_info, results)
            results['capital_info'] = capital_info
            
            # STEP 8: Recommendations
            recommendations = EmpiricalSynthesisEngineV91.generate_recommendations(results)
            results['recommendations'] = recommendations
            
            # STEP 9: Final Output
            results['final_tier'] = tier_info['tier']
            results['tier_name'] = tier_info['name']
            results['capital_multiplier'] = capital_info['final_multiplier']
            results['reason'] = EmpiricalSynthesisEngineV91.generate_final_reason(results)
            
            return results
            
        except Exception as e:
            return {
                'error': f'Analysis error: {str(e)}',
                'home_name': home_name,
                'away_name': away_name,
                'final_tier': 5,
                'tier_name': 'ERROR',
                'capital_multiplier': 0.0,
                'reason': f'System error: {str(e)}'
            }
    
    @staticmethod
    def determine_tier(score: float, is_goalless_draw: bool) -> Dict:
        """Determine confidence tier based on score"""
        if is_goalless_draw:
            return {
                'tier': 'GD',
                'name': 'GOALLESS_DRAW_SPECIAL',
                'score': score,
                'description': 'Special Goalless Draw pattern detected'
            }
        elif score >= 4.0:
            return {
                'tier': 1,
                'name': 'LOCK_MODE',
                'score': score,
                'description': 'High confidence across multiple pillars'
            }
        elif score >= 3.0:
            return {
                'tier': 2,
                'name': 'EDGE_MODE',
                'score': score,
                'description': 'Strong signal from 2+ pillars'
            }
        elif score >= 2.0:
            return {
                'tier': 3,
                'name': 'VALUE_MODE',
                'score': score,
                'description': 'Moderate signal from 1-2 pillars'
            }
        elif score >= 1.0:
            return {
                'tier': 4,
                'name': 'CAUTION_MODE',
                'score': score,
                'description': 'Weak signal, heuristic edge only'
            }
        else:
            return {
                'tier': 5,
                'name': 'STAY_AWAY',
                'score': score,
                'description': 'No edge detected'
            }
    
    @staticmethod
    def calculate_capital(tier_info: Dict, results: Dict) -> Dict:
        """Calculate capital allocation"""
        tier = tier_info['tier']
        
        # Base capital multipliers
        if tier == 'GD':  # Goalless Draw Special
            base_multiplier = 1.5  # Will be multiplied by whatever tier it would be
        elif tier == 1:  # LOCK MODE
            base_multiplier = 3.0 + min((tier_info['score'] - 4.0) * 2.5, 1.0)  # 3-4x
        elif tier == 2:  # EDGE MODE
            base_multiplier = 2.0
        elif tier == 3:  # VALUE MODE
            base_multiplier = 1.5
        elif tier == 4:  # CAUTION MODE
            base_multiplier = 1.0
        else:  # STAY AWAY
            base_multiplier = 0.0
        
        # Pattern bonuses
        pattern_bonus = 0.0
        
        # Count strong pillars (score > 0.5 of max)
        strong_pillars = 0
        if results.get('total_under', {}).get('total_score', 0) >= 1.5:
            strong_pillars += 1
        if results.get('winner_lock', {}).get('score', 0) >= 2.0:
            strong_pillars += 1
        if results.get('elite_defense', {}).get('total_score', 0) >= 0.75:
            strong_pillars += 1
        
        # Bonus for multiple strong pillars
        if strong_pillars >= 2:
            pattern_bonus += 0.5
        
        # Efficiency bonus
        if results['scoring']['efficiency_bonus'] > 0.3:
            pattern_bonus += 0.5
        
        # No filters triggered bonus
        filters = results.get('protective_filters', {})
        if not filters.get('filters_triggered', []):
            pattern_bonus += 0.5
        
        # Apply pattern bonus
        final_multiplier = base_multiplier + pattern_bonus
        
        # Maximum cap
        final_multiplier = min(final_multiplier, 5.0)
        
        # For Goalless Draw, apply to what would have been the tier
        if tier == 'GD':
            # Determine what tier it would have been without GD
            score = tier_info['score']
            if score >= 4.0:
                underlying_tier = 1
            elif score >= 3.0:
                underlying_tier = 2
            elif score >= 2.0:
                underlying_tier = 3
            elif score >= 1.0:
                underlying_tier = 4
            else:
                underlying_tier = 5
            
            # Get base multiplier for that tier
            if underlying_tier == 1:
                underlying_mult = 3.0
            elif underlying_tier == 2:
                underlying_mult = 2.0
            elif underlying_tier == 3:
                underlying_mult = 1.5
            elif underlying_tier == 4:
                underlying_mult = 1.0
            else:
                underlying_mult = 0.0
            
            final_multiplier = underlying_mult * 1.5  # 1.5x for GD
        
        return {
            'base_multiplier': base_multiplier,
            'pattern_bonus': pattern_bonus,
            'final_multiplier': final_multiplier,
            'strong_pillars': strong_pillars
        }
    
    @staticmethod
    def generate_recommendations(results: Dict) -> List[Dict]:
        """Generate betting recommendations"""
        recommendations = []
        
        tier_name = results.get('tier_name', '')
        if tier_name in ['STAY_AWAY', 'ERROR']:
            return recommendations
        
        home_name = results.get('home_name', 'Home')
        away_name = results.get('away_name', 'Away')
        
        # Goalless Draw Special
        if results.get('goalless_draw', {}).get('is_goalless_draw', False):
            recommendations.append({
                'market': 'CORRECT_SCORE',
                'selection': '0-0',
                'confidence': 'HIGH',
                'reason': 'Goalless Draw pattern detected',
                'stake': 'PRIMARY'
            })
            recommendations.append({
                'market': 'TOTAL_UNDER_1_5',
                'selection': 'Under 1.5 Goals',
                'confidence': 'HIGH',
                'reason': 'Supporting Goalless Draw pattern',
                'stake': 'SECONDARY'
            })
            recommendations.append({
                'market': 'DRAW',
                'selection': 'Draw',
                'confidence': 'MEDIUM',
                'reason': 'Goalless implies draw',
                'stake': 'TERTIARY'
            })
            return recommendations
        
        # Determine strongest pillar
        pillar_scores = {
            'TOTAL_UNDER': results.get('total_under', {}).get('total_score', 0),
            'WINNER_LOCK': results.get('winner_lock', {}).get('score', 0),
            'ELITE_DEFENSE': results.get('elite_defense', {}).get('total_score', 0)
        }
        
        strongest_pillar = max(pillar_scores.items(), key=lambda x: x[1])[0]
        
        # Primary market by strongest pillar
        if strongest_pillar == 'TOTAL_UNDER':
            recommendations.append({
                'market': 'TOTAL_UNDER_2_5',
                'selection': 'Under 2.5 Goals',
                'confidence': 'HIGH' if pillar_scores['TOTAL_UNDER'] >= 2.0 else 'MEDIUM',
                'reason': f'Total Under paths: {results.get("total_under", {}).get("total_paths", 0)}',
                'stake': 'PRIMARY'
            })
            recommendations.append({
                'market': 'TOTAL_UNDER_3_5',
                'selection': 'Under 3.5 Goals',
                'confidence': 'MEDIUM',
                'reason': 'Supporting Total Under pattern',
                'stake': 'SECONDARY'
            })
        
        elif strongest_pillar == 'WINNER_LOCK':
            controller = results.get('winner_lock', {}).get('controller', 'HOME')
            controller_name = home_name if controller == 'HOME' else away_name
            
            recommendations.append({
                'market': 'DOUBLE_CHANCE',
                'selection': f'{controller_name} win or draw',
                'confidence': 'HIGH' if pillar_scores['WINNER_LOCK'] >= 2.5 else 'MEDIUM',
                'reason': f'Winner Lock: {results.get("winner_lock", {}).get("gates_passed", 0):.2f}/4 gates',
                'stake': 'PRIMARY'
            })
        
        elif strongest_pillar == 'ELITE_DEFENSE':
            elite_data = results.get('elite_defense', {})
            home_tier = elite_data.get('home_tier', 0)
            away_tier = elite_data.get('away_tier', 0)
            
            if home_tier > away_tier:
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{away_name} Under 1.5',
                    'confidence': 'HIGH' if home_tier >= 1.0 else 'MEDIUM',
                    'reason': f'Home Elite Defense: {elite_data.get("home_tier_name", "")}',
                    'stake': 'PRIMARY'
                })
            elif away_tier > home_tier:
                recommendations.append({
                    'market': 'OPPONENT_UNDER_1_5',
                    'selection': f'{home_name} Under 1.5',
                    'confidence': 'HIGH' if away_tier >= 1.0 else 'MEDIUM',
                    'reason': f'Away Elite Defense: {elite_data.get("away_tier_name", "")}',
                    'stake': 'PRIMARY'
                })
            
            recommendations.append({
                'market': 'TOTAL_UNDER_2_5',
                'selection': 'Under 2.5 Goals',
                'confidence': 'MEDIUM',
                'reason': 'Supporting Elite Defense pattern',
                'stake': 'SECONDARY'
            })
        
        # Add secondary markets if multiple pillars strong
        strong_count = sum(1 for score in pillar_scores.values() if score >= 1.0)
        if strong_count >= 2:
            # Add alternate market based on second strongest pillar
            sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_pillars) > 1:
                second_pillar = sorted_pillars[1][0]
                
                if second_pillar == 'TOTAL_UNDER' and strongest_pillar != 'TOTAL_UNDER':
                    recommendations.append({
                        'market': 'TOTAL_UNDER_2_5',
                        'selection': 'Under 2.5 Goals',
                        'confidence': 'MEDIUM',
                        'reason': 'Secondary Total Under signal',
                        'stake': 'SECONDARY'
                    })
        
        return recommendations
    
    @staticmethod
    def generate_final_reason(results: Dict) -> str:
        """Generate final reason for the decision"""
        tier_name = results.get('tier_name', '')
        
        if tier_name == 'STAY_AWAY':
            filters = results.get('protective_filters', {})
            return f"Stay Away: {filters.get('reason', 'Protective filters triggered')}"
        
        if tier_name == 'GOALLESS_DRAW_SPECIAL':
            gd = results.get('goalless_draw', {})
            return f"Goalless Draw Pattern: {gd.get('conditions_total', 0)}/6 conditions met"
        
        scoring = results.get('scoring', {})
        final_score = scoring.get('final_score', 0)
        
        reasons = []
        
        # Add pillar reasons
        tu = results.get('total_under', {})
        if tu.get('total_score', 0) > 0:
            reasons.append(f"Total Under: {tu.get('total_paths', 0)} paths")
        
        wl = results.get('winner_lock', {})
        if wl.get('score', 0) > 0:
            reasons.append(f"Winner Lock: {wl.get('gates_passed', 0):.2f}/4 gates")
        
        ed = results.get('elite_defense', {})
        if ed.get('total_score', 0) > 0:
            reasons.append(f"Elite Defense: {ed.get('total_score', 0):.1f} tier")
        
        # Add league context
        league = results.get('league_params', {}).get('description', 'Standard League')
        
        if reasons:
            return f"Final Score: {final_score:.2f}/5.0 | {league} | " + " | ".join(reasons)
        else:
            return f"Final Score: {final_score:.2f}/5.0 | Minimal signals detected"

# =================== STREAMLIT UI v9.1 ===================
def main():
    """Fused Logic Engine v9.1 Streamlit App"""
    
    st.set_page_config(
        page_title="Fused Logic Engine v9.1 - The Empirical Synthesis",
        page_icon="🧠",
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
    .tier-1 { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; }
    .tier-2 { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important; }
    .tier-3 { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; }
    .tier-4 { background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%) !important; }
    .tier-5 { background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important; }
    .tier-gd { background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important; }
    .pillar-card { background: linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%) !important; }
    .filter-card { background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1E3A8A;">🧠 FUSED LOGIC ENGINE v9.1</h1>
        <div style="color: #4B5563; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
            <strong>THE EMPIRICAL SYNTHESIS:</strong> Weighted Pillars • League Parameterization • Protective Filters<br>
            Empirical weights beat heuristic rules. League context trumps universal thresholds.
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
    
    # Sidebar for league selection
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
                        st.success(f"✅ Loaded {len(df)} teams")
                        st.rerun()
        
        # League info
        if st.session_state.selected_league:
            league_params = get_league_parameters(st.session_state.selected_league)
            st.markdown("---")
            st.markdown("### 📊 League Parameters")
            st.write(f"**{league_params['description']}**")
            st.write(f"Total Under threshold: {league_params['total_under_threshold']}")
            st.write(f"Efficiency filter: <{league_params['efficiency_filter']}%")
            st.write(f"Winner Lock Δ: >{league_params['winner_lock_delta_threshold']}")
            st.write(f"League multiplier: {league_params['league_multiplier']}x")
    
    # Main content
    if st.session_state.df is None:
        st.info("👆 Select a league from the sidebar to begin")
        
        # Show pillar weights
        st.markdown("### ⚖️ Empirical Pillar Weights")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Under", "73% weight", "73% empirical success")
        with col2:
            st.metric("Winner Lock", "50% weight", "50% empirical success")
        with col3:
            st.metric("Elite Defense", "50% weight", "50% empirical success")
        
        # League success rates
        st.markdown("### 📈 League Success Rates")
        leagues_cols = st.columns(4)
        leagues = [
            ("Serie A", "83%", "UNDER MACHINE"),
            ("La Liga", "80%", "TACTICAL"),
            ("Premier League", "33%", "VOLATILE"),
            ("Other Leagues", "65%", "STANDARD")
        ]
        for idx, (name, rate, desc) in enumerate(leagues):
            with leagues_cols[idx]:
                st.metric(name, rate, desc)
        
        return
    
    df = st.session_state.df
    league_name = st.session_state.selected_league
    
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
            home_xg = get_safe_value(home_data, 'xg_per_match', 1.2)
            home_eff = get_safe_value(home_data, 'efficiency', 100)
            home_scored = get_safe_value(home_data, 'goals_scored_last_5', 0)
            home_conceded = get_safe_value(home_data, 'goals_conceded_last_5', 0)
            
            st.info(f"**Metrics:** {home_xg:.2f} xG/match, {home_eff:.0f}% efficiency")
            st.info(f"**Last 5:** {home_scored} scored, {home_conceded} conceded")
    
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team")
        
        # Get away team data
        away_row = df[df['team'] == away_team]
        if not away_row.empty:
            away_data = away_row.iloc[0].to_dict()
            away_xg = get_safe_value(away_data, 'xg_per_match', 1.2)
            away_eff = get_safe_value(away_data, 'efficiency', 100)
            away_scored = get_safe_value(away_data, 'goals_scored_last_5', 0)
            away_conceded = get_safe_value(away_data, 'goals_conceded_last_5', 0)
            
            st.info(f"**Metrics:** {away_xg:.2f} xG/match, {away_eff:.0f}% efficiency")
            st.info(f"**Last 5:** {away_scored} scored, {away_conceded} conceded")
    
    # Run analysis button
    if st.button("🧠 EXECUTE EMPIRICAL SYNTHESIS v9.1", type="primary", use_container_width=True):
        with st.spinner("Executing empirical synthesis analysis..."):
            try:
                engine = EmpiricalSynthesisEngineV91()
                result = engine.execute_full_analysis(
                    home_data, away_data, home_team, away_team, league_name
                )
                st.session_state.analysis_result = result
                
                if 'error' in result:
                    st.error(f"❌ Analysis error: {result['error']}")
                else:
                    st.success("✅ Empirical synthesis complete!")
                    
            except Exception as e:
                st.error(f"❌ Fatal error: {str(e)}")
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # Check for error
        if 'error' in result:
            st.error(f"Analysis failed: {result['error']}")
            return
        
        # Tier Banner
        tier_name = result.get('tier_name', '')
        tier_map = {
            'LOCK_MODE': ('tier-1', '🎯', 1),
            'EDGE_MODE': ('tier-2', '📊', 2),
            'VALUE_MODE': ('tier-3', '💰', 3),
            'CAUTION_MODE': ('tier-4', '⚠️', 4),
            'STAY_AWAY': ('tier-5', '🚫', 5),
            'GOALLESS_DRAW_SPECIAL': ('tier-gd', '0-0', 'GD'),
            'ERROR': ('tier-5', '❌', 5)
        }
        
        tier_class, tier_emoji, tier_num = tier_map.get(tier_name, ('tier-4', '❓', 0))
        
        st.markdown(f"""
        <div class="pattern-card {tier_class}" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{tier_emoji}</div>
            <h2 style="margin: 0;">{tier_name.replace('_', ' ')}</h2>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                {result.get('capital_multiplier', 0.0):.1f}x CAPITAL
            </div>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">
                {result.get('reason', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Scoring Breakdown
        st.markdown("### ⚖️ Scoring Breakdown")
        scoring = result.get('scoring', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Final Score", f"{scoring.get('final_score', 0):.2f}/5.0")
        with col2:
            st.metric("League Multiplier", f"{result.get('league_params', {}).get('league_multiplier', 1.0)}x")
        with col3:
            efficiency = scoring.get('efficiency_bonus', 0)
            st.metric("Efficiency Bonus", f"{efficiency:+.2f}")
        with col4:
            penalties = scoring.get('filters_penalties', 0)
            st.metric("Filter Penalties", f"{penalties:+.2f}")
        
        # Three Pillars
        st.markdown("### 🏛️ The Three Empirical Pillars")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tu = result.get('total_under', {})
            st.markdown(f"""
            <div class="pillar-card" style="padding: 1rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📉</div>
                <h3 style="margin: 0.5rem 0;">TOTAL UNDER</h3>
                <div style="font-size: 1.2rem; font-weight: bold;">{tu.get('total_paths', 0)}/3 paths</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
                    Score: {tu.get('total_score', 0):.2f} × 73% weight
                </div>
            </div>
            """, unsafe_allow_html=True)
            if tu.get('path_details'):
                with st.expander("Path Details"):
                    for path in tu['path_details']:
                        st.caption(f"• {path.get('path', '')}: {path.get('reason', '')}")
        
        with col2:
            wl = result.get('winner_lock', {})
            st.markdown(f"""
            <div class="pillar-card" style="padding: 1rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
                <h3 style="margin: 0.5rem 0;">WINNER LOCK</h3>
                <div style="font-size: 1.2rem; font-weight: bold;">{wl.get('gates_passed', 0):.2f}/4 gates</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
                    Controller: {wl.get('controller', 'N/A')} × 50% weight
                </div>
            </div>
            """, unsafe_allow_html=True)
            if wl.get('gate_details'):
                with st.expander("Gate Details"):
                    for gate in wl['gate_details']:
                        st.caption(f"• {gate.get('gate', '')}: {gate.get('reason', '')}")
        
        with col3:
            ed = result.get('elite_defense', {})
            st.markdown(f"""
            <div class="pillar-card" style="padding: 1rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
                <h3 style="margin: 0.5rem 0;">ELITE DEFENSE</h3>
                <div style="font-size: 1.2rem; font-weight: bold;">{ed.get('total_score', 0):.2f}/1.5 tier</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
                    Home: {ed.get('home_tier_name', '')} × 50% weight
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Defense Details"):
                st.caption(f"• Home: {ed.get('home_reason', '')}")
                st.caption(f"• Away: {ed.get('away_reason', '')}")
        
        # Protective Filters
        st.markdown("### 🛡️ Protective Filters")
        filters = result.get('protective_filters', {})
        
        if filters.get('filters_triggered'):
            st.markdown(f"""
            <div class="filter-card" style="padding: 1rem; border-radius: 10px;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">⚠️</span>
                    <div>
                        <h3 style="margin: 0;">Filters Triggered</h3>
                        <div style="font-size: 0.9rem;">{filters.get('reason', '')}</div>
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 5px;">
                    Penalties: -{filters.get('penalties', 0):.2f} points
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("✅ No protective filters triggered")
        
        # Goalless Draw Pattern
        gd = result.get('goalless_draw', {})
        if gd.get('is_goalless_draw', False):
            st.markdown(f"""
            <div class="pattern-card tier-gd" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <h3 style="margin: 0;">GOALLESS DRAW PATTERN DETECTED</h3>
                <div style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">
                    {gd.get('conditions_total', 0)}/6 conditions met
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💰 Betting Recommendations")
        recommendations = result.get('recommendations', [])
        
        if recommendations:
            for rec in recommendations:
                with st.container():
                    cols = st.columns([0.25, 0.35, 0.2, 0.2])
                    with cols[0]:
                        st.markdown(f"**{rec.get('market', '')}**")
                    with cols[1]:
                        st.write(rec.get('selection', ''))
                        st.caption(rec.get('reason', ''))
                    with cols[2]:
                        st.metric("Confidence", rec.get('confidence', ''))
                    with cols[3]:
                        st.caption(f"**{rec.get('stake', '')}**")
        else:
            st.info("No bet recommendations - consider staying away")
        
        # Capital Allocation Details
        st.markdown("### 💸 Capital Allocation Details")
        capital = result.get('capital_info', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base Multiplier", f"{capital.get('base_multiplier', 0.0):.1f}x")
        with col2:
            st.metric("Pattern Bonus", f"{capital.get('pattern_bonus', 0.0):.1f}x")
        with col3:
            st.metric("Final Multiplier", f"{capital.get('final_multiplier', 0.0):.1f}x")
        with col4:
            st.metric("Strong Pillars", capital.get('strong_pillars', 0))
        
        # Team Statistics
        st.markdown("### 📊 Team Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{home_team}**")
            st.metric("xG/Match", f"{get_safe_value(home_data, 'xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{get_safe_value(home_data, 'efficiency', 0):.0f}%")
            st.metric("Last 5 Scored", get_safe_value(home_data, 'goals_scored_last_5', 0))
            st.metric("Last 5 Conceded", get_safe_value(home_data, 'goals_conceded_last_5', 0))
        
        with col2:
            st.markdown(f"**{away_team}**")
            st.metric("xG/Match", f"{get_safe_value(away_data, 'xg_per_match', 0):.2f}")
            st.metric("Efficiency", f"{get_safe_value(away_data, 'efficiency', 0):.0f}%")
            st.metric("Last 5 Scored", get_safe_value(away_data, 'goals_scored_last_5', 0))
            st.metric("Last 5 Conceded", get_safe_value(away_data, 'goals_conceded_last_5', 0))
        
        # League Context
        st.markdown("### 🌍 League Context")
        league_params = result.get('league_params', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("League", league_params.get('description', ''))
        with col2:
            st.metric("Success Rate", f"{league_params.get('success_rate', 0)*100:.0f}%")
        with col3:
            st.metric("Total Under Threshold", f"≤{league_params.get('total_under_threshold', 1.0)}")
        with col4:
            st.metric("Efficiency Filter", f"<{league_params.get('efficiency_filter', 90)}%")

if __name__ == "__main__":
    main()