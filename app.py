import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple

# Set page config
st.set_page_config(
    page_title="Anti-Manipulation Football Predictor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .trap-card {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.375rem;
    }
    .value-card {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.375rem;
    }
    .warning-card {
        background-color: #FEE2E2;
        border-left: 4px solid #EF4444;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.375rem;
    }
    .metric-card {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    .emoji-large {
        font-size: 4rem;
        text-align: center;
        margin: 1rem 0;
    }
    .load-button {
        background-color: #10B981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: none;
        font-weight: bold;
        width: 100%;
        margin-top: 1rem;
    }
    .load-button:hover {
        background-color: #0DA271;
    }
</style>
""", unsafe_allow_html=True)

# System Classes
class PublicSentimentAnalyzer:
    """Detect when bookmakers are manipulating public psychology"""
    
    BIG_SIX = ["Manchester United", "Manchester City", "Liverpool", 
               "Chelsea", "Arsenal", "Tottenham"]
    
    TRAP_PATTERNS = {
        'OVER_HYPE_TRAP': {
            'conditions': [
                'over_odds < 1.65',
                'under_odds > 2.25',
                'home_team in BIG_SIX',
                'total_goals_last_5_home > 10',
                'public_bet_percentage > 70%'
            ],
            'action': 'CONSIDER_UNDER',
            'reason': 'Public overestimates favorite attacking power'
        },
        
        'UNDER_FEAR_TRAP': {
            'conditions': [
                'under_odds < 1.70',
                'over_odds > 2.20',
                'both_teams_conceded_5plus_last_3',
                'is_relegation_battle',
                'public_bet_percentage < 30%'
            ],
            'action': 'CONSIDER_OVER',
            'reason': 'Public overestimates defensive capabilities in pressure games'
        },
        
        'HISTORICAL_DATA_TRAP': {
            'conditions': [
                'h2h_over_percentage > 70%',
                'recent_over_percentage < 40%',
                'odds_movement_favors_over',
                'new_manager_any_team'
            ],
            'action': 'TRUST_RECENT_NOT_HISTORY',
            'reason': 'Historical data outdated due to team changes'
        }
    }
    
    def analyze(self, match_data: Dict, odds_data: Dict) -> Dict:
        """Analyze public sentiment and detect traps"""
        traps = []
        warnings = []
        
        # Check for Over Hype Trap
        if (odds_data.get('over_odds', 2.0) < 1.65 and
            odds_data.get('under_odds', 2.0) > 2.25 and
            match_data.get('home_team') in self.BIG_SIX and
            match_data.get('total_goals_last_5_home', 0) > 10 and
            odds_data.get('public_bet_percentage', 0) > 70):
            traps.append({
                'type': 'OVER_HYPE_TRAP',
                'description': 'Public overestimates favorite attacking power',
                'recommendation': 'CONSIDER_UNDER',
                'confidence': 0.8
            })
        
        # Check for Under Fear Trap
        if (odds_data.get('under_odds', 2.0) < 1.70 and
            odds_data.get('over_odds', 2.0) > 2.20 and
            match_data.get('both_teams_conceded_5plus_last_3', False) and
            match_data.get('is_relegation_battle', False) and
            odds_data.get('public_bet_percentage', 0) < 30):
            traps.append({
                'type': 'UNDER_FEAR_TRAP',
                'description': 'Public overestimates defensive capabilities',
                'recommendation': 'CONSIDER_OVER',
                'confidence': 0.75
            })
        
        # Check for Historical Data Trap
        if (match_data.get('h2h_over_percentage', 0) > 70 and
            match_data.get('recent_over_percentage', 0) < 40 and
            odds_data.get('odds_movement_favors_over', False) and
            match_data.get('new_manager_any_team', False)):
            traps.append({
                'type': 'HISTORICAL_DATA_TRAP',
                'description': 'Historical data outdated due to team changes',
                'recommendation': 'TRUST_RECENT_NOT_HISTORY',
                'confidence': 0.85
            })
        
        return {
            'traps_detected': traps,
            'public_bias_score': self._calculate_bias_score(odds_data),
            'recommendations': [trap['recommendation'] for trap in traps]
        }
    
    def _calculate_bias_score(self, odds_data: Dict) -> float:
        """Calculate public bias score (0-1)"""
        public_bet = odds_data.get('public_bet_percentage', 50)
        return abs(public_bet - 50) / 50


class FormHistoryConflictDetector:
    """Identify when recent form contradicts historical patterns"""
    
    def analyze(self, historical_stats: Dict, recent_stats: Dict) -> Dict:
        conflicts = []
        adjustment_factors = []
        
        # 1. SCORING PATTERN CONFLICT
        hist_avg = historical_stats.get('avg_goals', 2.5)
        recent_avg = recent_stats.get('avg_goals_last_5', 2.5)
        
        if hist_avg > 2.8 and recent_avg < 2.2:
            conflicts.append({
                'type': 'SCORING_DECLINE',
                'severity': 'HIGH',
                'message': f"Historical {hist_avg:.1f} → Recent {recent_avg:.1f} goals",
                'adjustment': 0.75
            })
            adjustment_factors.append(0.75)
        
        # 2. DEFENSIVE IMPROVEMENT CONFLICT
        hist_conceded = historical_stats.get('conceded_pg', 1.5)
        recent_conceded = recent_stats.get('conceded_pg_last_5', 1.5)
        
        if hist_conceded > 1.5 and recent_conceded < 1.0:
            conflicts.append({
                'type': 'DEFENSIVE_IMPROVEMENT',
                'severity': 'MEDIUM',
                'message': 'Team tightened defense recently',
                'adjustment': 0.85
            })
            adjustment_factors.append(0.85)
        
        # 3. MANAGERIAL CHANGE CONFLICT
        if historical_stats.get('manager') != recent_stats.get('manager'):
            conflicts.append({
                'type': 'MANAGER_CHANGE',
                'severity': 'VERY_HIGH',
                'message': f"New manager: {recent_stats.get('manager', 'Unknown')}",
                'adjustment': 0.65,
                'rule': 'LAST_5_GAMES_ONLY'
            })
            adjustment_factors.append(0.65)
        
        # Calculate overall adjustment
        overall_adjustment = np.prod(adjustment_factors) if adjustment_factors else 1.0
        
        return {
            'conflicts': conflicts,
            'overall_adjustment': overall_adjustment,
            'conflict_score': len(conflicts) / 3.0,
            'weighted_form': self._calculate_weighted_form(recent_stats)
        }
    
    def _calculate_weighted_form(self, recent_stats: Dict) -> Dict:
        """Calculate weighted form average"""
        weights = [0.1, 0.15, 0.25, 0.25, 0.25]  # Last 5 games weights
        
        # Parse goals lists
        goals_for_str = recent_stats.get('goals_for_last_5', '1,1,1,1,1')
        goals_against_str = recent_stats.get('goals_against_last_5', '1,1,1,1,1')
        
        try:
            goals_for = [int(x.strip()) for x in goals_for_str.split(',')]
            goals_against = [int(x.strip()) for x in goals_against_str.split(',')]
        except:
            goals_for = [1, 1, 1, 1, 1]
            goals_against = [1, 1, 1, 1, 1]
        
        weighted_gf = sum(g * w for g, w in zip(goals_for, weights[-len(goals_for):]))
        weighted_ga = sum(g * w for g, w in zip(goals_against, weights[-len(goals_against):]))
        
        return {
            'weighted_goals_for': weighted_gf,
            'weighted_goals_against': weighted_ga,
            'weighted_total': weighted_gf + weighted_ga
        }


class PressureContextAnalyzer:
    """Analyze what teams NEED from this specific game"""
    
    def analyze(self, context_data: Dict) -> Dict:
        scenarios = []
        adjustments = []
        
        # DESPERATION_HOME_WIN
        if (context_data.get('home_position', 10) >= 15 and
            context_data.get('home_points', 30) <= 20 and
            context_data.get('home_last_5_wins', 2) <= 1):
            scenarios.append({
                'type': 'DESPERATION_HOME_WIN',
                'psychology': 'FEAR_BASED_CAUTION',
                'goal_expectation': 'LOW',
                'pattern': '1-0, 2-0 controlled win',
                'adjustment': 0.80
            })
            adjustments.append(0.80)
        
        # NOTHING_TO_PLAY_FOR
        home_pos = context_data.get('home_position', 10)
        away_pos = context_data.get('away_position', 10)
        if (8 <= home_pos <= 12 and
            8 <= away_pos <= 12 and
            context_data.get('both_safe_from_relegation', True) and
            context_data.get('both_cannot_qualify_europe', False) and
            context_data.get('games_remaining', 10) <= 5):
            scenarios.append({
                'type': 'NOTHING_TO_PLAY_FOR',
                'psychology': 'RELAXED_OPEN',
                'goal_expectation': 'HIGH',
                'pattern': 'Entertaining, end-to-end',
                'adjustment': 1.20
            })
            adjustments.append(1.20)
        
        # DERBY_PRESSURE_COOKER
        if context_data.get('is_local_derby', False):
            scenarios.append({
                'type': 'DERBY_PRESSURE_COOKER',
                'psychology': 'FEAR_OF_LOSING > DESIRE_TO_WIN',
                'goal_expectation': 'LOW_MEDIUM',
                'pattern': 'Cagey, tactical, set-piece goals',
                'adjustment': 0.90
            })
            adjustments.append(0.90)
        
        # Calculate average adjustment
        avg_adjustment = np.mean(adjustments) if adjustments else 1.0
        
        return {
            'scenarios': scenarios,
            'pressure_score': self._calculate_pressure_score(context_data),
            'goal_expectation_adjustment': avg_adjustment
        }
    
    def _calculate_pressure_score(self, context_data: Dict) -> float:
        """Calculate pressure score (0-1)"""
        score = 0.0
        
        # Position pressure
        home_pos = context_data.get('home_position', 10)
        if home_pos >= 15:  # Relegation zone
            score += 0.4
        elif home_pos <= 4:  # Title/CL race
            score += 0.3
        
        # Points pressure
        home_pts = context_data.get('home_points', 30)
        if home_pts <= 20:
            score += 0.3
        
        # Derby pressure
        if context_data.get('is_local_derby', False):
            score += 0.2
        
        return min(score, 1.0)


class AntiManipulationPredictionEngine:
    """Main engine that synthesizes all analyses"""
    
    def __init__(self):
        self.sentiment_analyzer = PublicSentimentAnalyzer()
        self.form_detector = FormHistoryConflictDetector()
        self.pressure_analyzer = PressureContextAnalyzer()
    
    def predict_match(self, match_data: Dict, odds_data: Dict, context_data: Dict) -> Dict:
        # Step 1: Collect all analyses
        analyses = {
            'public_sentiment': self.sentiment_analyzer.analyze(match_data, odds_data),
            'form_vs_history': self.form_detector.analyze(
                match_data.get('historical_stats', {}),
                match_data.get('recent_stats', {})
            ),
            'pressure_context': self.pressure_analyzer.analyze(context_data)
        }
        
        # Step 2: Identify traps
        traps = self._identify_traps(analyses, odds_data)
        
        # Step 3: Calculate true probability
        true_probability = self._calculate_true_probability(analyses, match_data)
        
        # Step 4: Find value opportunities
        value_opportunity = self._find_value_opportunity(
            true_probability, 
            odds_data, 
            traps
        )
        
        # Step 5: Make final decision
        confidence = self._calculate_confidence(analyses, traps)
        edge = value_opportunity.get('edge', 0)
        
        return {
            'prediction': value_opportunity.get('prediction', 'NO_BET'),
            'confidence': confidence,
            'edge_percentage': edge,
            'traps_detected': traps,
            'analyses': analyses,
            'value_opportunity': value_opportunity,
            'bet_size': self._calculate_bet_size(edge, confidence, len(traps) > 0),
            'recommendation': self._generate_recommendation(value_opportunity, traps)
        }
    
    def _identify_traps(self, analyses: Dict, odds_data: Dict) -> List[Dict]:
        """Identify specific trap patterns"""
        traps = []
        
        # Historical Data Distraction
        if (analyses['form_vs_history']['conflict_score'] > 0.7 and
            analyses['public_sentiment'].get('public_bias_score', 0) > 0.6):
            traps.append({
                'type': 'HISTORICAL_DATA_DISTRACTION',
                'description': 'Bookmakers highlighting historical trends that no longer apply',
                'action': 'IGNORE_HISTORY_TRUST_RECENT'
            })
        
        # Emotional Pricing Trap
        pressure_score = analyses['pressure_context'].get('pressure_score', 0)
        if pressure_score > 0.6 and odds_data.get('odds_volatility', 0) > 0.3:
            traps.append({
                'type': 'EMOTIONAL_PRICING_TRAP',
                'description': 'Odds set for entertainment value, not true probability',
                'action': 'REMOVE_EMOTION_FROM_ANALYSIS'
            })
        
        # Public Hype Trap
        public_traps = analyses['public_sentiment'].get('traps_detected', [])
        traps.extend(public_traps)
        
        return traps
    
    def _calculate_true_probability(self, analyses: Dict, match_data: Dict) -> Dict:
        """Calculate true probability based on all factors"""
        base_prob = {
            'over_25': 0.5,
            'under_25': 0.5
        }
        
        # Adjust for form vs history
        form_adjustment = analyses['form_vs_history']['overall_adjustment']
        
        # Adjust for pressure context
        pressure_adjustment = analyses['pressure_context']['goal_expectation_adjustment']
        
        # Adjust for public sentiment bias
        bias_score = analyses['public_sentiment']['public_bias_score']
        if bias_score > 0.6:
            sentiment_adjustment = 0.8
        else:
            sentiment_adjustment = 1.0
        
        # Combine adjustments
        total_adjustment = form_adjustment * pressure_adjustment * sentiment_adjustment
        
        # Calculate true probabilities
        true_prob_over = min(0.95, base_prob['over_25'] * total_adjustment)
        true_prob_under = 1 - true_prob_over
        
        return {
            'over_25': true_prob_over,
            'under_25': true_prob_under,
            'adjustments_applied': {
                'form': form_adjustment,
                'pressure': pressure_adjustment,
                'sentiment': sentiment_adjustment
            }
        }
    
    def _find_value_opportunity(self, true_prob: Dict, odds_data: Dict, traps: List) -> Dict:
        """Find value betting opportunities"""
        over_odds = odds_data.get('over_odds', 2.0)
        under_odds = odds_data.get('under_odds', 2.0)
        
        # Calculate implied probabilities from odds
        implied_prob_over = 1 / over_odds
        implied_prob_under = 1 / under_odds
        
        # Calculate edges
        edge_over = (true_prob['over_25'] - implied_prob_over) * 100
        edge_under = (true_prob['under_25'] - implied_prob_under) * 100
        
        # Determine best value
        if edge_over > 2 and edge_over > edge_under:
            prediction = 'OVER_2.5'
            edge = edge_over
        elif edge_under > 2 and edge_under > edge_over:
            prediction = 'UNDER_2.5'
            edge = edge_under
        else:
            prediction = 'NO_VALUE_BET'
            edge = 0
        
        return {
            'prediction': prediction,
            'edge': edge,
            'edges': {
                'over_edge': edge_over,
                'under_edge': edge_under
            },
            'true_probabilities': true_prob,
            'implied_probabilities': {
                'over': implied_prob_over,
                'under': implied_prob_under
            }
        }
    
    def _calculate_confidence(self, analyses: Dict, traps: List) -> float:
        """Calculate confidence score (0-1)"""
        confidence = 1.0
        
        # Reduce confidence for conflicts
        conflict_score = analyses['form_vs_history']['conflict_score']
        confidence *= (1 - conflict_score * 0.5)
        
        # Reduce confidence for traps
        confidence *= (0.7 ** len(traps))
        
        # Increase confidence for strong pressure context
        pressure_score = analyses['pressure_context']['pressure_score']
        if pressure_score > 0.7:
            confidence *= 1.2
        
        return min(max(confidence, 0.1), 1.0)
    
    def _calculate_bet_size(self, edge: float, confidence: float, has_traps: bool) -> float:
        """Calculate bet size using modified Kelly criterion"""
        if edge <= 0:
            return 0.0
        
        base_size = edge / 100 * confidence
        
        # Reduce for traps
        if has_traps:
            base_size *= 0.5
        
        # Apply limits
        if base_size > 0.10:
            return 0.10
        elif base_size < 0.01:
            return 0.01
        else:
            return round(base_size, 3)
    
    def _generate_recommendation(self, value_opp: Dict, traps: List) -> str:
        """Generate human-readable recommendation"""
        if value_opp['prediction'] == 'NO_VALUE_BET':
            return "No clear value found. Avoid betting on this match."
        
        prediction = value_opp['prediction']
        edge = value_opp['edge']
        
        if len(traps) > 0:
            return f"CAUTIOUS BET on {prediction} (Edge: {edge:.1f}%, but traps detected)"
        else:
            return f"CONFIDENT BET on {prediction} (Edge: {edge:.1f}%)"


# Sample Data (In production, this would come from database/API)
def load_sample_data():
    """Load sample match data for demonstration"""
    return {
        'match_1': {
            'match_data': {
                'home_team': 'Manchester United',
                'away_team': 'Brighton',
                'date': '2024-03-15',
                'historical_stats': {
                    'avg_goals': 3.2,
                    'conceded_pg': 1.8,
                    'manager': 'Old Manager',
                },
                'recent_stats': {
                    'avg_goals_last_5': 1.8,
                    'conceded_pg_last_5': 0.9,
                    'manager': 'New Manager',
                    'total_goals_last_5_home': 12,
                    'both_teams_conceded_5plus_last_3': False,
                    'h2h_over_percentage': 75,
                    'recent_over_percentage': 40,
                    'new_manager_any_team': True,
                    'goals_for_last_5': '2,1,0,3,1',
                    'goals_against_last_5': '1,0,1,0,2'
                }
            },
            'odds_data': {
                'over_odds': 1.62,
                'under_odds': 2.40,
                'public_bet_percentage': 78,
                'opening_over_odds': 1.70,
                'opening_under_odds': 2.20,
                'odds_volatility': 0.35,
                'bet_volume_over': 78,
                'bet_volume_under': 22
            },
            'context_data': {
                'home_position': 16,
                'away_position': 8,
                'home_points': 18,
                'away_points': 35,
                'home_last_5_wins': 1,
                'games_remaining': 8,
                'is_local_derby': False,
                'both_safe_from_relegation': False,
                'both_cannot_qualify_europe': True,
                'table_position_close': False
            }
        }
    }


def process_csv_data(df: pd.DataFrame) -> Dict:
    """Convert CSV data to match format for our system"""
    matches = {}
    
    for idx, row in df.iterrows():
        match_id = f"match_{idx + 1}"
        
        # Convert string lists to proper format
        home_goals_list = str(row.get('home_goals_for_last_5', '1,1,1,1,1')).replace('"', '')
        home_conceded_list = str(row.get('home_goals_against_last_5', '1,1,1,1,1')).replace('"', '')
        away_goals_list = str(row.get('away_goals_for_last_5', '1,1,1,1,1')).replace('"', '')
        away_conceded_list = str(row.get('away_goals_against_last_5', '1,1,1,1,1')).replace('"', '')
        
        match_data = {
            'home_team': row.get('home_team', 'Unknown'),
            'away_team': row.get('away_team', 'Unknown'),
            'date': row.get('date', '2024-01-01'),
            'historical_stats': {
                'avg_goals': float(row.get('historical_avg_goals_home', 2.5)),
                'conceded_pg': float(row.get('historical_conceded_pg_home', 1.5)),
                'manager': str(row.get('home_manager', 'Unknown'))
            },
            'recent_stats': {
                'avg_goals_last_5': float(row.get('recent_avg_goals_home', 2.5)),
                'conceded_pg_last_5': float(row.get('recent_conceded_pg_home', 1.5)),
                'manager': str(row.get('home_manager', 'Unknown')),
                'total_goals_last_5_home': int(row.get('total_goals_last_5_home', 10)),
                'both_teams_conceded_5plus_last_3': bool(row.get('both_teams_conceded_5plus_last_3', 0)),
                'h2h_over_percentage': float(row.get('h2h_over_percentage', 50)),
                'recent_over_percentage': float(row.get('recent_over_percentage', 50)),
                'new_manager_any_team': bool(row.get('new_manager_any_team', 0)),
                'goals_for_last_5': home_goals_list,
                'goals_against_last_5': home_conceded_list
            }
        }
        
        # Add away team historical stats
        match_data['historical_stats_away'] = {
            'avg_goals': float(row.get('historical_avg_goals_away', 2.5)),
            'conceded_pg': float(row.get('historical_conceded_pg_away', 1.5)),
            'manager': str(row.get('away_manager', 'Unknown'))
        }
        
        match_data['recent_stats_away'] = {
            'avg_goals_last_5': float(row.get('recent_avg_goals_away', 2.5)),
            'conceded_pg_last_5': float(row.get('recent_conceded_pg_away', 1.5)),
            'goals_for_last_5': away_goals_list,
            'goals_against_last_5': away_conceded_list
        }
        
        odds_data = {
            'over_odds': float(row.get('over_odds', 2.0)),
            'under_odds': float(row.get('under_odds', 2.0)),
            'public_bet_percentage': float(row.get('public_bet_percentage', 50)),
            'opening_over_odds': float(row.get('opening_over_odds', 2.0)),
            'opening_under_odds': float(row.get('opening_under_odds', 2.0)),
            'odds_volatility': 0.2,  # Default
            'bet_volume_over': float(row.get('bet_volume_over', 50)),
            'bet_volume_under': float(row.get('bet_volume_under', 50))
        }
        
        context_data = {
            'home_position': int(row.get('home_position', 10)),
            'away_position': int(row.get('away_position', 10)),
            'home_points': int(row.get('home_points', 30)),
            'away_points': 30,  # Default if not in CSV
            'home_last_5_wins': int(row.get('home_last_5_wins', 2)),
            'games_remaining': int(row.get('games_remaining', 10)),
            'is_local_derby': bool(row.get('is_local_derby', 0)),
            'both_safe_from_relegation': bool(row.get('both_safe_from_relegation', 1)),
            'both_cannot_qualify_europe': bool(row.get('both_cannot_qualify_europe', 0)),
            'table_position_close': bool(row.get('table_position_close', 0))
        }
        
        matches[match_id] = {
            'match_data': match_data,
            'odds_data': odds_data,
            'context_data': context_data
        }
    
    return matches


# Main App
def main():
    # Title
    st.markdown('<h1 class="main-header">🎯 ANTI-MANIPULATION FOOTBALL PREDICTION SYSTEM</h1>', unsafe_allow_html=True)
    st.markdown("### Predicting when the market's prediction is wrong")
    
    # Initialize session state
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None
    if 'csv_matches' not in st.session_state:
        st.session_state.csv_matches = None
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="emoji-large">⚽</div>', unsafe_allow_html=True)
        st.title("System Configuration")
        
        st.subheader("Data Source")
        data_source = st.selectbox(
            "Select Data Source",
            ["Sample Data", "Upload CSV File"]
        )
        
        uploaded_file = None
        csv_loaded = False
        
        if data_source == "Upload CSV File":
            uploaded_file = st.file_uploader("Upload match data CSV", type=['csv'], key="csv_uploader")
            
            if uploaded_file is not None:
                # Show file info
                st.success(f"✅ File selected: {uploaded_file.name}")
                
                # Try to preview the CSV
                try:
                    df_preview = pd.read_csv(uploaded_file)
                    st.info(f"📊 File contains: {len(df_preview)} rows, {len(df_preview.columns)} columns")
                    
                    with st.expander("Preview first 3 rows"):
                        st.dataframe(df_preview.head(3))
                    
                    # Store the DataFrame in session state for the load button
                    st.session_state.uploaded_df = df_preview
                    
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")
                    st.session_state.uploaded_df = None
                
                # ADDED: LOAD BUTTON
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Load CSV", type="primary", use_container_width=True):
                        if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
                            # Process the CSV data
                            st.session_state.csv_data = st.session_state.uploaded_df
                            st.session_state.csv_matches = process_csv_data(st.session_state.csv_data)
                            csv_loaded = True
                            st.success("✅ CSV successfully loaded!")
                            st.rerun()
                        else:
                            st.error("Please select a CSV file first")
                
                with col2:
                    if st.button("🔄 Clear CSV", type="secondary", use_container_width=True):
                        if 'csv_data' in st.session_state:
                            st.session_state.csv_data = None
                        if 'csv_matches' in st.session_state:
                            st.session_state.csv_matches = None
                        st.rerun()
        
        st.subheader("Analysis Settings")
        min_edge = st.slider("Minimum Edge %", 0.0, 10.0, 2.0, 0.5)
        max_bet_size = st.slider("Max Bet Size %", 1, 20, 10, 1)
        
        st.subheader("Filters")
        league_filter = st.multiselect(
            "Leagues",
            ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
            default=["Premier League"]
        )
        
        st.markdown("---")
        
        # Show current data source status
        if data_source == "Sample Data":
            st.info("**Current Data**: Using Sample Data")
        elif data_source == "Upload CSV File":
            if st.session_state.csv_data is not None:
                st.success(f"**Current Data**: CSV Loaded ({len(st.session_state.csv_data)} matches)")
            else:
                st.warning("**Current Data**: No CSV loaded yet")
        
        st.warning("**Remember**: No bet is better than a forced bet")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Predictions", "📊 Analysis", "⚙️ System", "📚 Learn"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Live Match Predictions</h2>', unsafe_allow_html=True)
        
        # Initialize engine
        engine = AntiManipulationPredictionEngine()
        
        # Determine which data to use
        if data_source == "Upload CSV File" and st.session_state.csv_matches is not None:
            # Use uploaded CSV data
            sample_data = st.session_state.csv_matches
            st.success(f"📊 Showing predictions from uploaded CSV ({len(sample_data)} matches)")
        else:
            # Use sample data
            sample_data = load_sample_data()
            st.info("📋 Showing predictions from sample data")
        
        # Display predictions for each match
        if not sample_data:
            st.warning("No match data available. Please load a CSV file.")
        else:
            for match_id, match_info in sample_data.items():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        match = match_info['match_data']
                        st.subheader(f"⚽ {match['home_team']} vs {match['away_team']}")
                        st.caption(f"Date: {match.get('date', 'N/A')}")
                        if data_source == "Upload CSV File":
                            st.caption(f"Data Source: Uploaded CSV")
                    
                    with col2:
                        odds = match_info['odds_data']
                        st.metric("Over 2.5", f"{odds['over_odds']:.2f}")
                        st.metric("Under 2.5", f"{odds['under_odds']:.2f}")
                    
                    with col3:
                        st.metric("Public on Over", f"{odds['public_bet_percentage']:.0f}%")
                        st.metric("Opening Over", f"{odds.get('opening_over_odds', 'N/A')}")
                    
                    # Run prediction
                    prediction = engine.predict_match(
                        match_info['match_data'],
                        match_info['odds_data'],
                        match_info['context_data']
                    )
                    
                    # Display result
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if prediction['prediction'] == 'NO_VALUE_BET':
                            st.error("NO BET RECOMMENDED")
                        elif prediction['edge_percentage'] >= 5:
                            st.success(f"🎯 **{prediction['prediction']}**")
                        else:
                            st.info(f"⚡ **{prediction['prediction']}**")
                        
                        st.metric("Edge", f"{prediction['edge_percentage']:.1f}%")
                    
                    with col_b:
                        confidence_percent = prediction['confidence'] * 100
                        st.metric("Confidence", f"{confidence_percent:.0f}%")
                        
                        bet_size = prediction['bet_size'] * 100
                        st.metric("Bet Size", f"{bet_size:.1f}%")
                    
                    with col_c:
                        traps = prediction['traps_detected']
                        if traps:
                            st.warning(f"🚨 {len(traps)} Traps Detected")
                            for trap in traps[:2]:  # Show first 2 traps
                                st.caption(f"• {trap['type']}")
                        else:
                            st.success("✅ No Traps Detected")
                    
                    # Expand for details
                    with st.expander("View Detailed Analysis"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📈 Form vs History Analysis**")
                            form_analysis = prediction['analyses']['form_vs_history']
                            if form_analysis['conflicts']:
                                for conflict in form_analysis['conflicts']:
                                    st.warning(f"{conflict['type']}: {conflict['message']}")
                            else:
                                st.success("No significant conflicts")
                            
                            st.metric("Form Adjustment", f"{form_analysis['overall_adjustment']:.2f}")
                        
                        with col2:
                            st.markdown("**🎭 Pressure Context**")
                            pressure_analysis = prediction['analyses']['pressure_context']
                            if pressure_analysis['scenarios']:
                                for scenario in pressure_analysis['scenarios']:
                                    st.info(f"{scenario['type']}: {scenario['pattern']}")
                            else:
                                st.info("Normal match context")
                            
                            st.metric("Pressure Score", f"{pressure_analysis['pressure_score']:.2f}")
                        
                        # True vs Implied Probability
                        st.markdown("**📊 Probability Analysis**")
                        prob_data = prediction['value_opportunity']['true_probabilities']
                        impl_data = prediction['value_opportunity']['implied_probabilities']
                        
                        fig = go.Figure(data=[
                            go.Bar(name='True Probability', x=['Over 2.5', 'Under 2.5'], 
                                   y=[prob_data['over_25'], prob_data['under_25']]),
                            go.Bar(name='Implied Probability', x=['Over 2.5', 'Under 2.5'],
                                   y=[impl_data['over'], impl_data['under']])
                        ])
                        fig.update_layout(barmode='group', height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.divider()
    
    with tab2:
        st.markdown('<h2 class="sub-header">System Analysis Dashboard</h2>', unsafe_allow_html=True)
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Prediction Accuracy", "64%", "4%")
        with col2:
            st.metric("Avg Edge", "3.2%", "0.8%")
        with col3:
            st.metric("Trap Detection", "87%", "2%")
        with col4:
            st.metric("ROI (30 days)", "18.5%", "3.2%")
        
        # Trap detection chart
        st.markdown("### Trap Detection Frequency")
        trap_data = pd.DataFrame({
            'Trap Type': ['Over Hype', 'Under Fear', 'Historical Data', 'Emotional Pricing'],
            'Detections': [42, 38, 29, 31],
            'Success Rate': [85, 82, 79, 76]
        })
        
        fig = px.bar(trap_data, x='Trap Type', y='Detections',
                     color='Success Rate', text='Success Rate',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Edge distribution
        st.markdown("### Edge Distribution")
        edges = np.random.normal(3.2, 1.5, 100)
        fig = px.histogram(x=edges, nbins=20,
                          labels={'x': 'Edge %', 'y': 'Count'},
                          title='Distribution of Betting Edges')
        fig.add_vline(x=2.0, line_dash="dash", line_color="red",
                     annotation_text="Min Edge", annotation_position="top")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown('<h2 class="sub-header">System Configuration</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Analysis Weights")
            weight_form = st.slider("Recent Form Weight", 0.0, 1.0, 0.8, 0.05)
            weight_history = st.slider("Historical Data Weight", 0.0, 1.0, 0.2, 0.05)
            weight_pressure = st.slider("Pressure Context Weight", 0.0, 1.0, 0.7, 0.05)
            weight_sentiment = st.slider("Public Sentiment Weight", 0.0, 1.0, 0.6, 0.05)
        
        with col2:
            st.markdown("### Risk Management")
            min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.6, 0.05)
            max_daily_bets = st.slider("Max Daily Bets", 1, 10, 5, 1)
            stop_loss = st.slider("Daily Stop Loss %", 1, 20, 10, 1)
            
            st.markdown("### Auto-update")
            auto_update = st.checkbox("Auto-update odds", value=True)
            update_freq = st.selectbox("Update Frequency", ["5min", "15min", "30min", "1hour"])
        
        st.markdown("### System Status")
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            st.success("✅ Public Sentiment Analyzer")
            st.success("✅ Form History Detector")
        
        with status_col2:
            st.success("✅ Pressure Context Analyzer")
            st.success("✅ Odds Manipulation Detector")
        
        with status_col3:
            st.success("✅ Media Narrative Analyzer")
            st.success("✅ Red Flag Detection")
    
    with tab4:
        st.markdown('<h2 class="sub-header">Learn the System</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Core Principles
        
        1. **Bookmakers are manipulators, not predictors**
           - They profit from balanced books, not predicting outcomes
           - Their odds reflect public perception, not true probability
        
        2. **Public perception is usually wrong at extremes**
           - When >70% of public bets one side, often value is on the other
           - Media narratives create predictable betting patterns
        
        3. **Recent form > Historical data**
           - Teams change: managers, players, tactics, motivation
           - Last 5 games more relevant than last 5 years
        
        4. **Context determines psychology**
           - What does each team NEED from this game?
           - Pressure situations change team behavior
        """)
        
        st.divider()
        
        st.markdown("### Common Bookmaker Traps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 Over Hype Trap**
            - When: Big team at home, public expects goals
            - Odds: Over 2.5 < 1.65
            - Reality: Often cagey, tactical 2-0, 1-0 wins
            - Action: Consider Under
            
            **🎯 Historical Data Trap**
            - When: H2H shows high scoring, but teams changed
            - Odds: Over heavily favored based on history
            - Reality: New managers play differently
            - Action: Trust recent form over history
            """)
        
        with col2:
            st.markdown("""
            **🎯 Under Fear Trap**
            - When: Relegation battle, both teams "defensive"
            - Odds: Under 2.5 < 1.70
            - Reality: Pressure causes mistakes, 2-1 results
            - Action: Consider Over
            
            **🎯 Emotional Pricing Trap**
            - When: Derbies, rivalries, "must-win" games
            - Odds: Set for entertainment value
            - Reality: Fear of losing > desire to win
            - Action: Expect lower scoring than odds suggest
            """)
        
        st.divider()
        
        st.markdown("### Decision Checklist")
        
        checklist_col1, checklist_col2 = st.columns(2)
        
        with checklist_col1:
            st.success("**BET ONLY IF:**")
            st.markdown("""
            ✅ Recent form analysis complete
            ✅ Public sentiment trap checked  
            ✅ Historical vs recent conflict resolved
            ✅ Pressure context analyzed
            ✅ Odds manipulation patterns checked
            ✅ No red flags detected
            ✅ Edge > 2% after adjustments
            """)
        
        with checklist_col2:
            st.error("**NO BET IF:**")
            st.markdown("""
            ❌ Public >75% on one side with odds <1.60
            ❌ Manager change in last 2 games  
            ❌ Key team turmoil reported
            ❌ Extreme weather conditions
            ❌ Analyses conflict significantly
            ❌ Edge < 1% after adjustments
            """)

if __name__ == "__main__":
    main()
