"""
BRUTBALL v6.4 - DOUBLE CHANCE ARCHITECTURE
Complete Implementation for Direct CSV Integration
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import os

# ============================================================================
# SYSTEM CONSTANTS (IMMUTABLE)
# ============================================================================

# GATE THRESHOLDS
CONTROL_CRITERIA_REQUIRED = 2
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1
DIRECTION_THRESHOLD = 0.25
STATE_FLIP_FAILURES_REQUIRED = 2
ENFORCEMENT_METHODS_REQUIRED = 2
TOTALS_LOCK_THRESHOLD = 1.2
UNDER_GOALS_THRESHOLD = 2.5

# MARKET-SPECIFIC CONFIGURATION
MARKET_THRESHOLDS = {
    'DOUBLE_CHANCE': {
        'opponent_xg_max': 1.3,
        'recent_concede_max': None,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Double Chance (Win OR Draw)",
        'declaration_template': "🔒 DOUBLE CHANCE LOCKED\n{controller} cannot lose\nCovers Win OR Draw"
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,
        'recent_concede_max': 0.8,
        'state_flip_failures': 3,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Clean Sheet",
        'declaration_template': "🔒 CLEAN SHEET LOCKED\n{controller} will not concede"
    },
    'TEAM_NO_SCORE': {
        'opponent_xg_max': 0.6,
        'recent_concede_max': 0.6,
        'state_flip_failures': 4,
        'enforcement_methods': 3,
        'urgency_required': False,
        'bet_label': "Team No Score",
        'declaration_template': "🔒 TEAM NO SCORE LOCKED\n{opponent} will not score"
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,
        'recent_concede_max': 1.0,
        'state_flip_failures': 2,
        'enforcement_methods': 2,
        'urgency_required': False,
        'bet_label': "Opponent Under 1.5 Goals",
        'declaration_template': "🔒 OPPONENT UNDER 1.5 LOCKED\n{opponent} cannot score >1"
    }
}

CAPITAL_MULTIPLIERS = {'EDGE_MODE': 1.0, 'LOCK_MODE': 2.0}

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

class BrutballDataLoader:
    """Loads and validates CSV data from GitHub/local"""
    
    REQUIRED_COLUMNS = [
        'team',
        'home_matches_played', 'away_matches_played',
        'home_goals_scored', 'away_goals_scored',
        'home_goals_conceded', 'away_goals_conceded',
        'home_xg_for', 'away_xg_for',
        'home_xg_against', 'away_xg_against',
        'goals_scored_last_5', 'goals_conceded_last_5',
        'home_goals_conceded_last_5', 'away_goals_conceded_last_5'
    ]
    
    @staticmethod
    def load_league_data(league_name: str) -> pd.DataFrame:
        """Load CSV from leagues folder"""
        csv_path = f"leagues/{league_name}.csv"
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        missing_cols = [col for col in BrutballDataLoader.REQUIRED_COLUMNS 
                       if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    @staticmethod
    def get_team_data(df: pd.DataFrame, team_name: str) -> Dict:
        """Extract and pre-calculate team data"""
        team_row = df[df['team'] == team_name].iloc[0]
        
        # Convert numpy types to Python native
        data = {}
        for col in df.columns:
            val = team_row[col]
            if pd.isna(val):
                data[col] = None
            elif isinstance(val, (np.integer, np.int64)):
                data[col] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                data[col] = float(val)
            else:
                data[col] = val
        
        # Pre-calculations
        data['home_xg_per_match'] = (data['home_xg_for'] / data['home_matches_played'] 
                                    if data['home_matches_played'] > 0 else 0)
        data['away_xg_per_match'] = (data['away_xg_for'] / data['away_matches_played'] 
                                    if data['away_matches_played'] > 0 else 0)
        data['home_xga_per_match'] = (data['home_xg_against'] / data['home_matches_played'] 
                                      if data['home_matches_played'] > 0 else 0)
        data['away_xga_per_match'] = (data['away_xg_against'] / data['away_matches_played'] 
                                      if data['away_matches_played'] > 0 else 0)
        
        # Last 5 averages
        data['avg_scored_last_5'] = data['goals_scored_last_5'] / 5
        data['avg_conceded_last_5'] = data['goals_conceded_last_5'] / 5
        data['home_avg_conceded_last_5'] = (data['home_goals_conceded_last_5'] / 5 
                                           if data.get('home_goals_conceded_last_5') is not None 
                                           else data['avg_conceded_last_5'])
        data['away_avg_conceded_last_5'] = (data['away_goals_conceded_last_5'] / 5 
                                           if data.get('away_goals_conceded_last_5') is not None 
                                           else data['avg_conceded_last_5'])
        
        return data

# ============================================================================
# TIER 1: v6.0 EDGE DETECTION ENGINE
# ============================================================================

class EdgeDetectionEngine:
    """Tier 1: Heuristic identification of structural advantages"""
    
    @staticmethod
    def evaluate_control_criteria(team_data: Dict) -> Tuple[float, List[str]]:
        """Evaluate 4 control criteria and return weighted score"""
        criteria_passed = []
        weighted_score = 0.0
        
        # 1. Tempo dominance (xG > 1.4) - weight: 1.0
        avg_xg = (team_data.get('home_xg_per_match', 0) + team_data.get('away_xg_per_match', 0)) / 2
        if avg_xg > 1.4:
            criteria_passed.append("Tempo")
            weighted_score += 1.0
        
        # 2. Scoring efficiency (goals/xG > 90%) - weight: 1.0
        total_goals = team_data.get('home_goals_scored', 0) + team_data.get('away_goals_scored', 0)
        total_xg = team_data.get('home_xg_for', 0) + team_data.get('away_xg_for', 0)
        if total_xg > 0 and (total_goals / total_xg) > 0.9:
            criteria_passed.append("Efficiency")
            weighted_score += 1.0
        
        # 3. Critical area threat (set pieces > 25%) - weight: 0.8
        # Note: Need setpiece data - using placeholder
        # If we don't have setpiece data, skip this criteria
        setpiece_pct = team_data.get('home_setpiece_pct', 0)  # Would need this column
        if setpiece_pct > 0.25:
            criteria_passed.append("SetPiece")
            weighted_score += 0.8
        else:
            # Count as passed if no data (as per spec)
            pass
        
        # 4. Repeatable patterns (open play > 50% OR counter > 15%) - weight: 0.8
        # Using goals scored as proxy
        if team_data['avg_scored_last_5'] > 1.5:  # Proxy for scoring patterns
            criteria_passed.append("Patterns")
            weighted_score += 0.8
        
        return weighted_score, criteria_passed
    
    @staticmethod
    def analyze_match(home_data: Dict, away_data: Dict) -> Dict:
        """Main edge detection analysis"""
        home_score, home_criteria = EdgeDetectionEngine.evaluate_control_criteria(home_data)
        away_score, away_criteria = EdgeDetectionEngine.evaluate_control_criteria(away_data)
        
        # Identify controller
        controller = None
        if len(home_criteria) >= CONTROL_CRITERIA_REQUIRED and len(away_criteria) >= CONTROL_CRITERIA_REQUIRED:
            if abs(home_score - away_score) > QUIET_CONTROL_SEPARATION_THRESHOLD:
                controller = 'HOME' if home_score > away_score else 'AWAY'
        elif len(home_criteria) >= CONTROL_CRITERIA_REQUIRED:
            controller = 'HOME'
        elif len(away_criteria) >= CONTROL_CRITERIA_REQUIRED:
            controller = 'AWAY'
        
        # Goals environment check
        combined_xg = home_data['home_xg_per_match'] + away_data['away_xg_per_match']
        max_xg = max(home_data['home_xg_per_match'], away_data['away_xg_per_match'])
        goals_environment = (combined_xg >= 2.8 and max_xg >= 1.6)
        
        # Decision tree
        if controller and goals_environment:
            action = f"BACK {controller} & OVER 2.5"
            confidence = 7.5
        elif controller:
            action = f"BACK {controller}"
            confidence = 8.0
        elif goals_environment:
            action = "OVER 2.5"
            confidence = 6.0
        else:
            action = "UNDER 2.5"
            confidence = 5.5
        
        # Stake calculation
        if confidence >= 8.0:
            base_stake = 2.5
        elif confidence >= 7.0:
            base_stake = 2.0
        elif confidence >= 6.0:
            base_stake = 1.5
        else:
            base_stake = 1.0
        
        return {
            'controller': controller,
            'action': action,
            'confidence': confidence,
            'base_stake': base_stake,
            'goals_environment': goals_environment,
            'home_score': home_score,
            'away_score': away_score,
            'home_criteria': home_criteria,
            'away_criteria': away_criteria
        }

# ============================================================================
# TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS
# ============================================================================

class EdgeDerivedLocks:
    """Extract binary UNDER 1.5 predictions from defensive trends"""
    
    @staticmethod
    def generate_under_locks(home_data: Dict, away_data: Dict) -> List[Dict]:
        """Generate UNDER 1.5 locks based on defensive trends"""
        locks = []
        
        # Check home team's defense for away opponent under 1.5
        if home_data['avg_conceded_last_5'] <= 1.0:
            confidence = EdgeDerivedLocks._get_confidence_tier(away_data['avg_scored_last_5'])
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': away_data['team'],
                'defensive_team': home_data['team'],
                'confidence': confidence,
                'avg_conceded': home_data['avg_conceded_last_5'],
                'opponent_avg_scored': away_data['avg_scored_last_5'],
                'bet_label': f"{away_data['team']} to score UNDER 1.5 goals"
            })
        
        # Check away team's defense for home opponent under 1.5
        if away_data['avg_conceded_last_5'] <= 1.0:
            confidence = EdgeDerivedLocks._get_confidence_tier(home_data['avg_scored_last_5'])
            locks.append({
                'market': 'OPPONENT_UNDER_1_5',
                'team': home_data['team'],
                'defensive_team': away_data['team'],
                'confidence': confidence,
                'avg_conceded': away_data['avg_conceded_last_5'],
                'opponent_avg_scored': home_data['avg_scored_last_5'],
                'bet_label': f"{home_data['team']} to score UNDER 1.5 goals"
            })
        
        return locks
    
    @staticmethod
    def _get_confidence_tier(opponent_avg_scored: float) -> str:
        """Determine confidence tier based on opponent's scoring average"""
        if opponent_avg_scored <= 1.4:
            return "VERY STRONG 🔵"
        elif opponent_avg_scored <= 1.6:
            return "STRONG 🟢"
        elif opponent_avg_scored <= 1.8:
            return "WEAK 🟡"
        else:
            return "VERY WEAK 🔴"

# ============================================================================
# TIER 2: AGENCY-STATE LOCK ENGINE v6.4
# ============================================================================

class AgencyStateLockEngine:
    """Tier 2: Evaluate structural control via 4 Gates"""
    
    def __init__(self, home_data: Dict, away_data: Dict):
        self.home_data = home_data
        self.away_data = away_data
        
    def check_market(self, market: str) -> Optional[Dict]:
        """Check if a specific market is locked via 4 Gates"""
        thresholds = MARKET_THRESHOLDS[market]
        
        # Determine controller from edge detection
        edge_result = EdgeDetectionEngine.analyze_match(self.home_data, self.away_data)
        if not edge_result['controller']:
            return None
        
        if edge_result['controller'] == 'HOME':
            controller_data = self.home_data
            opponent_data = self.away_data
            controller_xg = self.home_data['home_xg_per_match']
            opponent_xg = self.away_data['away_xg_per_match']
            controller_is_home = True
        else:
            controller_data = self.away_data
            opponent_data = self.home_data
            controller_xg = self.away_data['away_xg_per_match']
            opponent_xg = self.home_data['home_xg_per_match']
            controller_is_home = False
        
        # GATE 1: Quiet Control Identification
        if not self._gate1_quiet_control(edge_result):
            return None
        
        # GATE 2: Directional Dominance
        if not self._gate2_directional_dominance(controller_xg, opponent_xg, thresholds['opponent_xg_max']):
            return None
        
        # GATE 3: Agency Collapse
        if not self._gate3_agency_collapse(opponent_data, thresholds['state_flip_failures']):
            return None
        
        # GATE 4: State Preservation & Enforcement
        if not self._gate4_state_preservation(controller_data, opponent_data, market, thresholds):
            return None
        
        # All gates passed - market is LOCKED
        return {
            'market': market,
            'controller': controller_data['team'],
            'opponent': opponent_data['team'],
            'controller_is_home': controller_is_home,
            'control_delta': controller_xg - opponent_xg,
            'bet_label': thresholds['bet_label'],
            'declaration': thresholds['declaration_template'].format(
                controller=controller_data['team'],
                opponent=opponent_data['team']
            ),
            'capital_mode': 'LOCK_MODE'
        }
    
    def _gate1_quiet_control(self, edge_result: Dict) -> bool:
        """Gate 1: Quiet Control Identification"""
        if not edge_result['controller']:
            return False
        
        # Check for mutual control
        if (len(edge_result['home_criteria']) >= CONTROL_CRITERIA_REQUIRED and 
            len(edge_result['away_criteria']) >= CONTROL_CRITERIA_REQUIRED):
            if abs(edge_result['home_score'] - edge_result['away_score']) <= QUIET_CONTROL_SEPARATION_THRESHOLD:
                return False  # Mutual control, no single controller
        
        return True
    
    def _gate2_directional_dominance(self, controller_xg: float, opponent_xg: float, opponent_threshold: float) -> bool:
        """Gate 2: Directional Dominance"""
        delta = controller_xg - opponent_xg
        return (delta > DIRECTION_THRESHOLD and opponent_xg < opponent_threshold)
    
    def _gate3_agency_collapse(self, opponent_data: Dict, required_failures: int) -> bool:
        """Gate 3: Agency Collapse - opponent failure checks"""
        failures = 0
        
        # 1. Chase capacity (xG < 1.1)
        if opponent_data['avg_scored_last_5'] < 1.1:
            failures += 1
        
        # 2. Tempo surge capability (xG < 1.4)
        if opponent_data['avg_scored_last_5'] < 1.4:
            failures += 1
        
        # 3. Alternate threat channels (simplified)
        # Using recent scoring as proxy - if low scoring, likely lacks alternate threats
        if opponent_data['avg_scored_last_5'] < 1.2:
            failures += 1
        
        # 4. Substitution leverage (goals/match < league_avg * 0.8)
        # Using league average of 1.3 as default
        if opponent_data['avg_scored_last_5'] < (1.3 * 0.8):
            failures += 1
        
        return failures >= required_failures
    
    def _gate4_state_preservation(self, controller_data: Dict, opponent_data: Dict, 
                                  market: str, thresholds: Dict) -> bool:
        """Gate 4: State Preservation & Enforcement"""
        
        # PART A: Defensive Preservation (for defensive markets only)
        if market != 'DOUBLE_CHANCE':
            recent_concede = (controller_data['home_avg_conceded_last_5'] 
                            if controller_data.get('is_home', True) 
                            else controller_data['away_avg_conceded_last_5'])
            
            if recent_concede > thresholds['recent_concede_max']:
                return False  # Gate 4A overrides earlier gates
        
        # PART B: Non-Urgent Enforcement
        methods = 0
        
        # 1. Defensive solidity
        concede_avg = (controller_data['home_avg_conceded_last_5'] 
                      if controller_data.get('is_home', True) 
                      else controller_data['away_avg_conceded_last_5'])
        
        if (controller_data.get('is_home', True) and concede_avg < 1.2) or \
           (not controller_data.get('is_home', True) and concede_avg < 1.3):
            methods += 1
        
        # 2. Alternate scoring channels (simplified)
        if controller_data['avg_scored_last_5'] > 1.2:
            methods += 1
        
        # 3. Consistent threat
        controller_xg = (controller_data['home_xg_per_match'] 
                        if controller_data.get('is_home', True) 
                        else controller_data['away_xg_per_match'])
        if controller_xg > 1.3:
            methods += 1
        
        # 4. Ball retention capability (scoring efficiency)
        total_goals = controller_data.get('home_goals_scored', 0) + controller_data.get('away_goals_scored', 0)
        total_xg = controller_data.get('home_xg_for', 0) + controller_data.get('away_xg_for', 0)
        if total_xg > 0 and (total_goals / total_xg) > 0.85:
            methods += 1
        
        return methods >= thresholds['enforcement_methods']

# ============================================================================
# TIER 3: TOTALS LOCK ENGINE
# ============================================================================

class TotalsLockEngine:
    """Tier 3: Identify structural low-scoring matches"""
    
    @staticmethod
    def check_totals_lock(home_data: Dict, away_data: Dict) -> Optional[Dict]:
        """Check for Totals ≤ 2.5 lock"""
        home_avg_scored = home_data['avg_scored_last_5']
        away_avg_scored = away_data['avg_scored_last_5']
        
        if home_avg_scored <= TOTALS_LOCK_THRESHOLD and away_avg_scored <= TOTALS_LOCK_THRESHOLD:
            return {
                'market': 'TOTALS_UNDER_2_5',
                'condition': f"Both teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5)",
                'home_avg_scored': home_avg_scored,
                'away_avg_scored': away_avg_scored,
                'bet_label': "UNDER 2.5 Goals",
                'declaration': f"🔒 TOTALS LOCKED\nDual low-offense trend confirmed",
                'capital_mode': 'LOCK_MODE'
            }
        return None

# ============================================================================
# MAIN BRUTBALL v6.4 ENGINE
# ============================================================================

class Brutballv64:
    """Main BRUTBALL v6.4 Engine - Integrates all tiers"""
    
    def __init__(self, league_name: str):
        self.league_name = league_name
        self.df = BrutballDataLoader.load_league_data(league_name)
        self.predictions = []
    
    def analyze_match(self, home_team: str, away_team: str, bankroll: float = 1000, base_stake_pct: float = 0.5) -> Dict:
        """Complete match analysis"""
        # Load team data
        home_data = BrutballDataLoader.get_team_data(self.df, home_team)
        away_data = BrutballDataLoader.get_team_data(self.df, away_team)
        home_data['team'] = home_team
        away_data['team'] = away_team
        home_data['is_home'] = True
        away_data['is_home'] = False
        
        results = {
            'match': f"{home_team} vs {away_team}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'home_data': {k: v for k, v in home_data.items() if not isinstance(v, (dict, list))},
            'away_data': {k: v for k, v in away_data.items() if not isinstance(v, (dict, list))},
            'analysis': {}
        }
        
        # TIER 1: Edge Detection
        edge_result = EdgeDetectionEngine.analyze_match(home_data, away_data)
        results['analysis']['edge_detection'] = edge_result
        
        # TIER 1+: Edge-Derived Under 1.5 Locks
        edge_locks = EdgeDerivedLocks.generate_under_locks(home_data, away_data)
        results['analysis']['edge_derived_locks'] = edge_locks
        
        # TIER 2: Agency-State Locks
        agency_engine = AgencyStateLockEngine(home_data, away_data)
        agency_locks = []
        
        for market in ['DOUBLE_CHANCE', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
            lock = agency_engine.check_market(market)
            if lock:
                agency_locks.append(lock)
        
        results['analysis']['agency_locks'] = agency_locks
        
        # TIER 3: Totals Lock
        totals_lock = TotalsLockEngine.check_totals_lock(home_data, away_data)
        results['analysis']['totals_lock'] = totals_lock
        
        # CAPITAL DECISION
        any_lock = bool(edge_locks or agency_locks or totals_lock)
        capital_mode = 'LOCK_MODE' if any_lock else 'EDGE_MODE'
        multiplier = CAPITAL_MULTIPLIERS[capital_mode]
        
        # FINAL STAKE CALCULATION
        base_stake_amount = (bankroll * base_stake_pct / 100)
        final_stake = base_stake_amount * multiplier
        
        results['capital'] = {
            'bankroll': bankroll,
            'base_stake_pct': base_stake_pct,
            'base_stake_amount': base_stake_amount,
            'capital_mode': capital_mode,
            'multiplier': multiplier,
            'final_stake': final_stake
        }
        
        # SYSTEM VERDICT
        if totals_lock:
            verdict = "DUAL LOW-OFFENSE STATE DETECTED"
        elif agency_locks:
            verdict = "AGENCY-STATE CONTROL DETECTED"
        elif edge_locks:
            verdict = "EDGE-DERIVED DEFENSIVE CONTROL DETECTED"
        else:
            verdict = "STRUCTURAL EDGE DETECTED"
        
        results['verdict'] = verdict
        
        # BET RECOMMENDATIONS
        recommendations = []
        
        # Agency locks first
        for lock in agency_locks:
            recommendations.append({
                'type': 'AGENCY_LOCK',
                'market': lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': lock['declaration'],
                'confidence': 'HIGH'
            })
        
        # Edge-derived locks
        for lock in edge_locks:
            recommendations.append({
                'type': 'EDGE_DERIVED',
                'market': lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': f"Defensive trend: {lock['defensive_team']} concedes avg {lock['avg_conceded']:.1f}",
                'confidence': lock['confidence']
            })
        
        # Totals lock
        if totals_lock:
            recommendations.append({
                'type': 'TOTALS_LOCK',
                'market': totals_lock['bet_label'],
                'stake_pct': (final_stake / bankroll) * 100,
                'stake_amount': final_stake,
                'reason': totals_lock['declaration'],
                'confidence': 'HIGH'
            })
        
        # Edge action (if no locks)
        if not recommendations:
            recommendations.append({
                'type': 'EDGE_ACTION',
                'market': edge_result['action'],
                'stake_pct': (base_stake_amount / bankroll) * 100,
                'stake_amount': base_stake_amount,
                'reason': f"Edge detection: {edge_result['confidence']}/10 confidence",
                'confidence': 'MEDIUM'
            })
        
        results['recommendations'] = recommendations
        
        # Store for tracking
        self.predictions.append({
            'match': results['match'],
            'timestamp': results['timestamp'],
            'recommendations': recommendations,
            'actual_score': None,
            'actual_goals': None
        })
        
        return results
    
    def get_available_teams(self) -> List[str]:
        """Get list of available teams in league"""
        return self.df['team'].tolist()
    
    def save_predictions(self, filename: str = "predictions.json"):
        """Save predictions to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.predictions, f, indent=2)
    
    def load_actual_results(self, results_file: str):
        """Load actual match results and calculate accuracy"""
        # Implementation for loading results
        pass

# ============================================================================
# STREAMLIT APP INTERFACE
# ============================================================================

def create_streamlit_app():
    """Create Streamlit web interface"""
    try:
        import streamlit as st
        
        st.set_page_config(page_title="BRUTBALL v6.4", layout="wide")
        
        st.title("⚽ BRUTBALL v6.4 - Double Chance Architecture")
        st.markdown("### Defensive Vulnerability Detection System")
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=100000, value=1000, step=100)
        with col2:
            base_stake_pct = st.number_input("Base Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
        
        # League selection
        leagues = [f.replace('.csv', '') for f in os.listdir('leagues') if f.endswith('.csv')]
        selected_league = st.selectbox("📁 Select League", leagues)
        
        if selected_league:
            try:
                engine = Brutballv64(selected_league)
                teams = engine.get_available_teams()
                
                # Match selection
                col3, col4 = st.columns(2)
                with col3:
                    home_team = st.selectbox("🏟️ Home Team", teams)
                with col4:
                    away_team = st.selectbox("Away Team", [t for t in teams if t != home_team])
                
                if st.button("Analyze Match", type="primary"):
                    with st.spinner("Running BRUTBALL v6.4 Analysis..."):
                        result = engine.analyze_match(home_team, away_team, bankroll, base_stake_pct)
                        
                        # Display results
                        st.markdown("---")
                        st.subheader(f"🏆 {result['match']}")
                        
                        # Capital mode
                        capital_mode = result['capital']['capital_mode']
                        st.metric("Capital Mode", capital_mode, 
                                 f"{result['capital']['multiplier']}x multiplier")
                        
                        # Verdict
                        st.info(f"**System Verdict:** {result['verdict']}")
                        
                        # Recommendations
                        st.subheader("🎯 Betting Recommendations")
                        for rec in result['recommendations']:
                            with st.expander(f"{rec['market']} - {rec['stake_pct']:.1f}% stake (${rec['stake_amount']:.2f})"):
                                st.write(f"**Type:** {rec['type']}")
                                st.write(f"**Confidence:** {rec['confidence']}")
                                st.write(f"**Reasoning:** {rec['reason']}")
                        
                        # Raw data (collapsible)
                        with st.expander("📊 Detailed Analysis Data"):
                            st.json(result)
                
                # Team comparison
                st.markdown("---")
                st.subheader("📈 Team Comparison")
                if home_team and away_team:
                    try:
                        home_data = BrutballDataLoader.get_team_data(engine.df, home_team)
                        away_data = BrutballDataLoader.get_team_data(engine.df, away_team)
                        
                        comparison_data = {
                            'Metric': ['xG/Match (Home/Away)', 'Avg Goals Last 5', 'Avg Conceded Last 5'],
                            home_team: [
                                f"{home_data.get('home_xg_per_match', 0):.2f}",
                                f"{home_data['avg_scored_last_5']:.1f}",
                                f"{home_data['avg_conceded_last_5']:.1f}"
                            ],
                            away_team: [
                                f"{away_data.get('away_xg_per_match', 0):.2f}",
                                f"{away_data['avg_scored_last_5']:.1f}",
                                f"{away_data['avg_conceded_last_5']:.1f}"
                            ]
                        }
                        
                        st.dataframe(comparison_data, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error loading team data: {e}")
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.error("Make sure the CSV file is in the 'leagues' folder with correct format.")
        
        # System info
        with st.expander("📚 System Info"):
            st.markdown("""
            **BRUTBALL v6.4 Architecture:**
            - **Tier 1:** Edge Detection (v6.0)
            - **Tier 1+:** Edge-Derived Under 1.5 Locks
            - **Tier 2:** Agency-State Lock Engine
            - **Tier 3:** Totals Lock Engine
            
            **Primary Market:** Double Chance (Win OR Draw)
            **Data Source:** Last 5 matches only for trend-based logic
            """)
    
    except ImportError:
        print("Streamlit not installed. Running in console mode...")
        run_console_mode()

def run_console_mode():
    """Run in console mode if Streamlit not available"""
    print("=" * 60)
    print("BRUTBALL v6.4 - Console Mode")
    print("=" * 60)
    
    # Get league files
    leagues_dir = "leagues"
    if not os.path.exists(leagues_dir):
        print(f"Creating {leagues_dir} directory...")
        os.makedirs(leagues_dir)
        print("Please place your CSV files in the 'leagues' folder.")
        return
    
    league_files = [f for f in os.listdir(leagues_dir) if f.endswith('.csv')]
    
    if not league_files:
        print("No CSV files found in 'leagues' folder.")
        print("Please add your league CSV files.")
        return
    
    print("\nAvailable leagues:")
    for i, f in enumerate(league_files, 1):
        print(f"{i}. {f.replace('.csv', '')}")
    
    try:
        choice = int(input("\nSelect league (number): "))
        league_name = league_files[choice-1].replace('.csv', '')
        
        engine = Brutballv64(league_name)
        teams = engine.get_available_teams()
        
        print(f"\nTeams in {league_name}:")
        for i, team in enumerate(teams, 1):
            print(f"{i}. {team}")
        
        home_idx = int(input("\nSelect home team (number): ")) - 1
        away_idx = int(input("Select away team (number): ")) - 1
        
        home_team = teams[home_idx]
        away_team = teams[away_idx]
        
        print(f"\nAnalyzing: {home_team} vs {away_team}")
        
        result = engine.analyze_match(home_team, away_team)
        
        print("\n" + "=" * 60)
        print(f"RESULT: {result['match']}")
        print(f"Verdict: {result['verdict']}")
        print(f"Capital Mode: {result['capital']['capital_mode']} ({result['capital']['multiplier']}x)")
        print("\nRecommendations:")
        
        for rec in result['recommendations']:
            print(f"- {rec['market']}")
            print(f"  Stake: ${rec['stake_amount']:.2f} ({rec['stake_pct']:.1f}%)")
            print(f"  Confidence: {rec['confidence']}")
            print(f"  Reason: {rec['reason']}")
            print()
        
        # Save option
        save = input("Save results to JSON? (y/n): ")
        if save.lower() == 'y':
            engine.save_predictions()
            print("Results saved to predictions.json")
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Try to run Streamlit, fall back to console
    try:
        create_streamlit_app()
    except Exception as e:
        print(f"Streamlit error: {e}")
        run_console_mode()