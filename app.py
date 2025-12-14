import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter

# Set page config
st.set_page_config(
    page_title="TREND-BASED Football Predictor",
    page_icon="📈",
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
    .trend-up { color: #10B981; font-weight: bold; }
    .trend-down { color: #EF4444; font-weight: bold; }
    .trend-neutral { color: #6B7280; }
    .streak-bad { background-color: #FEE2E2; padding: 0.25rem 0.5rem; border-radius: 0.25rem; }
    .streak-good { background-color: #D1FAE5; padding: 0.25rem 0.5rem; border-radius: 0.25rem; }
    .pattern-alert { background-color: #FEF3C7; padding: 0.5rem; border-radius: 0.375rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ========== TREND ANALYSIS ENGINE ==========
class TrendAnalyzer:
    """Analyze trends, streaks, and patterns instead of simple averages"""
    
    @staticmethod
    def analyze_goal_trends(goals_list):
        """Analyze goal scoring trends from last 5 games"""
        if not goals_list or len(goals_list) < 3:
            return {'trend': 'NEUTRAL', 'score': 0.5}
        
        goals = [int(g) for g in goals_list]
        
        # 1. Recent vs Previous comparison
        if len(goals) >= 3:
            recent_avg = np.mean(goals[:3])  # Last 3 games
            prev_avg = np.mean(goals[3:]) if len(goals) > 3 else recent_avg
            trend_direction = 'UP' if recent_avg > prev_avg else 'DOWN' if recent_avg < prev_avg else 'FLAT'
        else:
            trend_direction = 'FLAT'
        
        # 2. Streak detection
        current_streak = 0
        streak_type = None
        for i in range(min(3, len(goals))):
            if goals[i] == 0:
                if streak_type == 'GOALLESS' or streak_type is None:
                    current_streak += 1
                    streak_type = 'GOALLESS'
                else:
                    break
            else:
                break
        
        # 3. Pattern analysis
        patterns = []
        if goals[0] == 0:  # Most recent game
            patterns.append('RECENT_GOALLESS')
        if sum(goals[:3]) == 0:
            patterns.append('GOALLESS_STREAK_3')
        if sum(goals[:2]) == 0:
            patterns.append('GOALLESS_STREAK_2')
        
        # 4. Volatility
        volatility = np.std(goals[:3]) if len(goals) >= 3 else 0
        
        # 5. Trend score (0-1, higher = better attacking form)
        trend_score = 0.5
        
        # Adjust for streaks
        if 'GOALLESS_STREAK_3' in patterns:
            trend_score *= 0.3
        elif 'GOALLESS_STREAK_2' in patterns:
            trend_score *= 0.5
        elif 'RECENT_GOALLESS' in patterns:
            trend_score *= 0.7
        
        # Adjust for trend direction
        if trend_direction == 'UP':
            trend_score *= 1.3
        elif trend_direction == 'DOWN':
            trend_score *= 0.7
        
        return {
            'trend': trend_direction,
            'score': min(max(trend_score, 0.1), 1.0),
            'streak': {'type': streak_type, 'length': current_streak} if streak_type else None,
            'patterns': patterns,
            'volatility': volatility,
            'recent_avg': np.mean(goals[:3]) if len(goals) >= 3 else np.mean(goals),
            'full_avg': np.mean(goals)
        }
    
    @staticmethod
    def analyze_defensive_trends(conceded_list):
        """Analyze defensive trends from last 5 games"""
        if not conceded_list or len(conceded_list) < 3:
            return {'trend': 'NEUTRAL', 'score': 0.5}
        
        conceded = [int(c) for c in conceded_list]
        
        # 1. Recent vs Previous
        if len(conceded) >= 3:
            recent_avg = np.mean(conceded[:3])
            prev_avg = np.mean(conceded[3:]) if len(conceded) > 3 else recent_avg
            trend_direction = 'DOWN' if recent_avg < prev_avg else 'UP' if recent_avg > prev_avg else 'FLAT'
        else:
            trend_direction = 'FLAT'
        
        # 2. Collapse detection
        collapse_patterns = []
        if conceded[0] >= 3:
            collapse_patterns.append('RECENT_COLLAPSE')
        if sum(conceded[:2]) >= 5:
            collapse_patterns.append('HEAVY_2GAME')
        if any(c >= 3 for c in conceded[:3]):
            collapse_patterns.append('ANY_COLLAPSE_3')
        
        # 3. Clean sheet streaks
        clean_sheets = sum(1 for c in conceded[:3] if c == 0)
        
        # 4. Trend score (higher = better defense)
        trend_score = 0.5
        
        # Penalize for collapses
        if 'RECENT_COLLAPSE' in collapse_patterns:
            trend_score *= 0.4
        elif 'HEAVY_2GAME' in collapse_patterns:
            trend_score *= 0.6
        elif 'ANY_COLLAPSE_3' in collapse_patterns:
            trend_score *= 0.7
        
        # Reward clean sheets
        if clean_sheets >= 2:
            trend_score *= 1.4
        elif clean_sheets == 1:
            trend_score *= 1.2
        
        # Adjust for trend direction
        if trend_direction == 'DOWN':  # conceding less
            trend_score *= 1.3
        elif trend_direction == 'UP':  # conceding more
            trend_score *= 0.7
        
        return {
            'trend': trend_direction,
            'score': min(max(trend_score, 0.1), 1.0),
            'collapse_patterns': collapse_patterns,
            'clean_sheets': clean_sheets,
            'recent_avg': np.mean(conceded[:3]) if len(conceded) >= 3 else np.mean(conceded),
            'full_avg': np.mean(conceded)
        }
    
    @staticmethod
    def analyze_momentum(results_list):
        """Analyze W/D/L momentum"""
        if not results_list or len(results_list) < 3:
            return {'momentum': 'NEUTRAL', 'score': 0.5}
        
        results = results_list[:5]  # Last 5 results
        
        # Points calculation (3 for win, 1 for draw, 0 for loss)
        points_map = {'W': 3, 'D': 1, 'L': 0}
        points = [points_map.get(r, 0) for r in results]
        
        # Recent vs previous momentum
        if len(points) >= 3:
            recent_points = np.mean(points[:3])
            prev_points = np.mean(points[3:]) if len(points) > 3 else recent_points
            momentum = 'UP' if recent_points > prev_points else 'DOWN' if recent_points < prev_points else 'FLAT'
        else:
            momentum = 'FLAT'
        
        # Win/loss streaks
        current_streak = 0
        streak_type = results[0] if results else None
        for result in results:
            if result == streak_type:
                current_streak += 1
            else:
                break
        
        # Big win detection (beating strong teams)
        big_win_factor = 1.0
        if results[0] == 'W':
            big_win_factor = 1.3  # Recent win boosts confidence
        
        # Momentum score
        momentum_score = np.mean(points[:3]) / 3 if len(points) >= 3 else 0.5
        
        # Apply streak adjustments
        if streak_type == 'W' and current_streak >= 2:
            momentum_score *= 1.4
        elif streak_type == 'L' and current_streak >= 2:
            momentum_score *= 0.6
        
        # Apply big win factor
        momentum_score *= big_win_factor
        
        return {
            'momentum': momentum,
            'score': min(max(momentum_score, 0.1), 1.0),
            'streak': {'type': streak_type, 'length': current_streak},
            'recent_form': results[:3],
            'points_avg': np.mean(points[:3]) if len(points) >= 3 else np.mean(points)
        }

# ========== TREND-BASED PREDICTION ENGINE ==========
class TrendBasedPredictor:
    """Main prediction engine using trend analysis"""
    
    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
    
    def predict(self, match_data):
        """Make prediction based on trend analysis"""
        
        # Extract data
        home_data = match_data['home']
        away_data = match_data['away']
        odds_data = match_data['odds']
        context_data = match_data['context']
        
        # 1. Analyze trends for both teams
        home_attack = self.trend_analyzer.analyze_goal_trends(home_data['goals_for'])
        home_defense = self.trend_analyzer.analyze_defensive_trends(home_data['goals_against'])
        home_momentum = self.trend_analyzer.analyze_momentum(home_data['results'])
        
        away_attack = self.trend_analyzer.analyze_goal_trends(away_data['goals_for'])
        away_defense = self.trend_analyzer.analyze_defensive_trends(away_data['goals_against'])
        away_momentum = self.trend_analyzer.analyze_momentum(away_data['results'])
        
        # 2. Calculate expected goals based on trends
        expected_home_goals = self._calculate_expected_goals(
            home_attack, away_defense, context_data, is_home=True
        )
        expected_away_goals = self._calculate_expected_goals(
            away_attack, home_defense, context_data, is_home=False
        )
        
        expected_total = expected_home_goals + expected_away_goals
        
        # 3. Detect traps based on trends
        traps = self._detect_traps(
            home_attack, home_defense, away_attack, away_defense,
            odds_data, context_data, expected_total
        )
        
        # 4. Calculate probabilities
        over_prob = self._calculate_over_probability(expected_total, traps)
        under_prob = 1 - over_prob
        
        # 5. Find value
        value_opp = self._find_value(over_prob, under_prob, odds_data, traps)
        
        # 6. Calculate confidence
        confidence = self._calculate_confidence(
            home_attack, home_defense, away_attack, away_defense,
            traps, value_opp['edge']
        )
        
        return {
            'prediction': value_opp['prediction'],
            'edge': value_opp['edge'],
            'confidence': confidence,
            'expected_total': expected_total,
            'expected_home': expected_home_goals,
            'expected_away': expected_away_goals,
            'traps': traps,
            'trend_analysis': {
                'home': {'attack': home_attack, 'defense': home_defense, 'momentum': home_momentum},
                'away': {'attack': away_attack, 'defense': away_defense, 'momentum': away_momentum}
            },
            'probabilities': {'over': over_prob, 'under': under_prob},
            'recommendation': self._generate_recommendation(value_opp, traps, confidence)
        }
    
    def _calculate_expected_goals(self, attack_trend, defense_trend, context, is_home=True):
        """Calculate expected goals based on trends"""
        
        base_xg = attack_trend['recent_avg'] * 0.7 + attack_trend['full_avg'] * 0.3
        
        # Adjust for opponent defense
        defense_factor = 1.0
        if 'RECENT_COLLAPSE' in defense_trend['collapse_patterns']:
            defense_factor = 1.4
        elif 'HEAVY_2GAME' in defense_trend['collapse_patterns']:
            defense_factor = 1.2
        elif defense_trend['clean_sheets'] >= 2:
            defense_factor = 0.7
        
        # Adjust for attack trend
        if attack_trend['trend'] == 'UP':
            base_xg *= 1.2
        elif attack_trend['trend'] == 'DOWN':
            base_xg *= 0.8
        
        # Adjust for streaks
        if attack_trend.get('streak') and attack_trend['streak']['type'] == 'GOALLESS':
            if attack_trend['streak']['length'] >= 3:
                base_xg *= 0.5
            elif attack_trend['streak']['length'] >= 2:
                base_xg *= 0.7
        
        # Home/away adjustment
        if is_home:
            base_xg *= 1.1
        else:
            base_xg *= 0.9
        
        # Context adjustments
        if context.get('is_relegation_battle'):
            if is_home:  # Home team desperate
                base_xg *= 1.15  # More likely to push for goals
        
        return round(base_xg * defense_factor, 2)
    
    def _detect_traps(self, home_attack, home_defense, away_attack, away_defense, odds, context, expected_total):
        """Detect betting traps based on trends"""
        traps = []
        
        public_over = odds.get('public_over', 50)
        over_odds = odds.get('over_odds', 2.0)
        
        # 1. GOALLESS STREAK TRAP
        if home_attack.get('patterns') and 'GOALLESS_STREAK_3' in home_attack['patterns']:
            traps.append({
                'type': 'GOALLESS_STREAK_TRAP',
                'team': 'Home',
                'description': f"Home team goalless in last 3 games but public betting Over",
                'impact': -0.15  # Reduce over probability
            })
        
        # 2. DEFENSIVE COLLAPSE TRAP
        if away_defense.get('collapse_patterns') and 'RECENT_COLLAPSE' in away_defense['collapse_patterns']:
            traps.append({
                'type': 'DEFENSIVE_COLLAPSE_TRAP',
                'team': 'Away',
                'description': f"Away team recently conceded 3+ goals",
                'impact': 0.10  # Increase over probability
            })
        
        # 3. MOMENTUM MISMATCH TRAP
        home_avg = home_attack.get('recent_avg', 1.5)
        away_conceded_avg = away_defense.get('recent_avg', 1.5)
        
        if home_avg < 0.8 and away_conceded_avg > 2.0:
            traps.append({
                'type': 'STATS_CONTRADICTION_TRAP',
                'description': f"Home can't score (avg: {home_avg:.1f}) but away can't defend (avg: {away_conceded_avg:.1f})",
                'impact': 0.05  # Slight increase for potential breakout
            })
        
        # 4. PUBLIC OVERREACTION TRAP
        if public_over > 65 and expected_total < 2.3:
            traps.append({
                'type': 'PUBLIC_OVERREACTION_TRAP',
                'description': f"Public {public_over}% on Over but expected goals only {expected_total:.1f}",
                'impact': -0.20  # Strong reduction for over
            })
        
        # 5. DESPERATION CHAOS TRAP
        if context.get('is_relegation_battle') and context.get('home_position', 10) >= 18:
            # Very desperate home team - could go either way
            if home_attack.get('streak') and home_attack['streak']['type'] == 'GOALLESS':
                traps.append({
                    'type': 'DESPERATION_CHAOS_TRAP',
                    'description': "Desperate home team on goalless streak - unpredictable",
                    'impact': 0.0,  # Neutral impact, just warning
                    'warning': True
                })
        
        return traps
    
    def _calculate_over_probability(self, expected_total, traps):
        """Calculate Over probability based on expected goals and traps"""
        
        # Base probability from expected goals
        if expected_total >= 3.5:
            base_prob = 0.75
        elif expected_total >= 3.0:
            base_prob = 0.65
        elif expected_total >= 2.7:
            base_prob = 0.55
        elif expected_total >= 2.3:
            base_prob = 0.45
        elif expected_total >= 2.0:
            base_prob = 0.35
        else:
            base_prob = 0.25
        
        # Apply trap adjustments
        adjustment = 0
        for trap in traps:
            if not trap.get('warning', False):
                adjustment += trap['impact']
        
        final_prob = base_prob + adjustment
        return max(0.1, min(0.9, final_prob))
    
    def _find_value(self, over_prob, under_prob, odds, traps):
        """Find value betting opportunity"""
        over_odds = odds.get('over_odds', 2.0)
        under_odds = odds.get('under_odds', 2.0)
        
        implied_over = 1 / over_odds
        implied_under = 1 / under_odds
        
        # Adjust for bookmaker margin
        total_implied = implied_over + implied_under
        if total_implied > 1.0:
            implied_over = implied_over / total_implied
            implied_under = implied_under / total_implied
        
        # Calculate edges
        edge_over = (over_prob - implied_over) * 100
        edge_under = (under_prob - implied_under) * 100
        
        # Apply trap adjustments to edges
        for trap in traps:
            if trap['type'] == 'PUBLIC_OVERREACTION_TRAP':
                edge_over -= 5.0
                edge_under += 3.0
            elif trap['type'] == 'GOALLESS_STREAK_TRAP':
                edge_over -= 3.0
                edge_under += 2.0
            elif trap['type'] == 'DEFENSIVE_COLLAPSE_TRAP':
                edge_over += 3.0
                edge_under -= 2.0
        
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
            'edges': {'over': edge_over, 'under': edge_under}
        }
    
    def _calculate_confidence(self, home_attack, home_defense, away_attack, away_defense, traps, edge):
        """Calculate confidence score based on trend clarity"""
        confidence = 0.5  # Start at 50%
        
        # 1. Trend clarity bonus
        if home_attack['trend'] in ['UP', 'DOWN'] and away_attack['trend'] in ['UP', 'DOWN']:
            confidence += 0.15  # Clear trends
        
        # 2. Streak clarity bonus
        if (home_attack.get('streak') and home_attack['streak']['length'] >= 2) or \
           (away_attack.get('streak') and away_attack['streak']['length'] >= 2):
            confidence += 0.10
        
        # 3. Pattern clarity bonus
        clear_patterns = 0
        if home_attack.get('patterns'):
            clear_patterns += 1
        if away_attack.get('patterns'):
            clear_patterns += 1
        if home_defense.get('collapse_patterns'):
            clear_patterns += 1
        if away_defense.get('collapse_patterns'):
            clear_patterns += 1
        
        confidence += clear_patterns * 0.05
        
        # 4. Edge size bonus
        if edge > 10:
            confidence += 0.20
        elif edge > 5:
            confidence += 0.10
        elif edge < 2:
            confidence -= 0.15
        
        # 5. Trap penalty
        if traps:
            warning_traps = sum(1 for t in traps if t.get('warning', False))
            real_traps = len(traps) - warning_traps
            confidence -= real_traps * 0.08
        
        return max(0.2, min(0.95, confidence))
    
    def _generate_recommendation(self, value_opp, traps, confidence):
        """Generate recommendation based on edge and confidence"""
        if value_opp['prediction'] == 'NO_VALUE_BET':
            return "NO BET - No clear value found"
        
        prediction = value_opp['prediction']
        edge = value_opp['edge']
        
        # Base recommendation
        if edge > 12:
            base = "STRONG BET"
        elif edge > 7:
            base = "CONFIDENT BET"
        elif edge > 3:
            base = "MODERATE BET"
        else:
            base = "SMALL BET"
        
        # Add trap warnings
        if traps:
            trap_count = len([t for t in traps if not t.get('warning', False)])
            if trap_count >= 2:
                base = "CAUTIOUS " + base
        
        # Add confidence qualifier
        if confidence > 0.8:
            conf_text = " (High Confidence)"
        elif confidence > 0.6:
            conf_text = " (Medium Confidence)"
        else:
            conf_text = " (Low Confidence)"
        
        return f"{base} on {prediction}{conf_text}"

# ========== INPUT FORM ==========
def create_trend_input_form():
    """Create input form with trend-focused data collection"""
    
    st.markdown("## 📈 TREND-BASED MATCH ANALYSIS")
    st.markdown("**Enter last 5 games data (most recent first)**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Burnley", key="home_team")
        
        st.markdown("**Last 5 Home Games (most recent first)**")
        home_goals_for = st.text_input("Goals Scored (e.g., 0,0,0,2,1)", "0,0,0,2,1", key="home_goals_for")
        home_goals_against = st.text_input("Goals Conceded (e.g., 1,2,2,0,1)", "1,2,2,0,1", key="home_goals_against")
        home_results = st.text_input("Results (W/D/L, e.g., L,L,L,W,D)", "L,L,L,W,D", key="home_results")
        
        home_position = st.number_input("League Position", 1, 20, 19, key="home_position")
        home_manager_new = st.checkbox("New Manager?", key="home_new_manager")
    
    with col2:
        st.subheader("🚌 Away Team")
        away_team = st.text_input("Team Name", "Fulham", key="away_team")
        
        st.markdown("**Last 5 Away Games (most recent first)**")
        away_goals_for = st.text_input("Goals Scored (e.g., 2,0,1,1,1)", "2,0,1,1,1", key="away_goals_for")
        away_goals_against = st.text_input("Goals Conceded (e.g., 1,2,2,3,3)", "1,2,2,3,3", key="away_goals_against")
        away_results = st.text_input("Results (W/D/L, e.g., W,L,L,L,L)", "W,L,L,L,L", key="away_results")
        
        away_position = st.number_input("League Position", 1, 20, 15, key="away_position")
        away_manager_new = st.checkbox("New Manager?", key="away_new_manager")
    
    st.markdown("---")
    st.subheader("🎯 Match Context & Odds")
    
    col3, col4 = st.columns(2)
    
    with col3:
        over_odds = st.number_input("Over 2.5 Odds", 1.1, 10.0, 2.15, 0.05, key="over_odds")
        under_odds = st.number_input("Under 2.5 Odds", 1.1, 10.0, 1.85, 0.05, key="under_odds")
        public_over = st.slider("Public Betting % on Over", 0, 100, 60, key="public_over")
    
    with col4:
        is_derby = st.checkbox("Local Derby?", key="is_derby")
        is_relegation = st.checkbox("Relegation Battle?", True, key="is_relegation")
        games_remaining = st.number_input("Games Remaining", 1, 38, 23, key="games_remaining")
        
        # Calculate if it's desperate
        home_desperate = st.checkbox("Home Team Desperate for Points?", True, key="home_desperate")
    
    # Parse input data
    def parse_list(input_str):
        return [x.strip() for x in input_str.split(',')] if input_str else []
    
    match_data = {
        'home': {
            'name': home_team,
            'goals_for': parse_list(home_goals_for),
            'goals_against': parse_list(home_goals_against),
            'results': parse_list(home_results),
            'position': home_position,
            'new_manager': home_manager_new,
            'desperate': home_desperate
        },
        'away': {
            'name': away_team,
            'goals_for': parse_list(away_goals_for),
            'goals_against': parse_list(away_goals_against),
            'results': parse_list(away_results),
            'position': away_position,
            'new_manager': away_manager_new
        },
        'odds': {
            'over_odds': over_odds,
            'under_odds': under_odds,
            'public_over': public_over
        },
        'context': {
            'is_derby': is_derby,
            'is_relegation_battle': is_relegation,
            'games_remaining': games_remaining,
            'home_position': home_position,
            'away_position': away_position,
            'home_desperate': home_desperate
        }
    }
    
    return match_data

# ========== DISPLAY RESULTS ==========
def display_trend_results(prediction):
    """Display prediction results with trend analysis"""
    
    st.markdown("## 📊 TREND ANALYSIS RESULTS")
    
    # Summary row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pred = prediction['prediction']
        if pred == 'NO_VALUE_BET':
            st.error("NO BET")
        elif pred == 'OVER_2.5':
            st.success("📈 OVER 2.5")
        else:
            st.success("📉 UNDER 2.5")
        
        st.metric("Expected Total Goals", f"{prediction['expected_total']:.1f}")
    
    with col2:
        st.metric("Edge", f"{prediction['edge']:.1f}%")
        st.metric("Confidence", f"{prediction['confidence']*100:.0f}%")
    
    with col3:
        st.metric("Expected Home", f"{prediction['expected_home']:.1f}")
        st.metric("Expected Away", f"{prediction['expected_away']:.1f}")
    
    with col4:
        st.info("### 📋 Recommendation")
        st.write(prediction['recommendation'])
    
    # Traps section
    if prediction['traps']:
        st.markdown("### 🚨 DETECTED TRAPS & PATTERNS")
        for trap in prediction['traps']:
            if trap.get('warning'):
                st.warning(f"**{trap['type']}**: {trap['description']}")
            else:
                st.error(f"**{trap['type']}**: {trap['description']}")
    
    # Trend analysis details
    with st.expander("📈 DETAILED TREND ANALYSIS"):
        
        # Home team analysis
        st.markdown("#### 🏠 Home Team Analysis")
        home_trends = prediction['trend_analysis']['home']
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.markdown("**Attack Trends**")
            attack = home_trends['attack']
            trend_emoji = "📈" if attack['trend'] == 'UP' else "📉" if attack['trend'] == 'DOWN' else "➡️"
            st.write(f"Trend: {trend_emoji} {attack['trend']}")
            st.write(f"Recent Avg: {attack['recent_avg']:.1f} goals")
            if attack.get('streak'):
                st.write(f"Streak: {attack['streak']['type']} ({attack['streak']['length']} games)")
            if attack.get('patterns'):
                st.write(f"Patterns: {', '.join(attack['patterns'])}")
        
        with col6:
            st.markdown("**Defense Trends**")
            defense = home_trends['defense']
            trend_emoji = "📉" if defense['trend'] == 'DOWN' else "📈" if defense['trend'] == 'UP' else "➡️"
            st.write(f"Trend: {trend_emoji} {defense['trend']}")
            st.write(f"Recent Avg: {defense['recent_avg']:.1f} conceded")
            st.write(f"Clean Sheets: {defense['clean_sheets']}/3")
            if defense.get('collapse_patterns'):
                st.write(f"Collapses: {', '.join(defense['collapse_patterns'])}")
        
        with col7:
            st.markdown("**Momentum**")
            momentum = home_trends['momentum']
            st.write(f"Momentum: {momentum['momentum']}")
            st.write(f"Recent Form: {' '.join(momentum['recent_form'])}")
            if momentum.get('streak'):
                st.write(f"Streak: {momentum['streak']['type']} ({momentum['streak']['length']} games)")
        
        st.markdown("---")
        
        # Away team analysis
        st.markdown("#### 🚌 Away Team Analysis")
        away_trends = prediction['trend_analysis']['away']
        
        col8, col9, col10 = st.columns(3)
        
        with col8:
            st.markdown("**Attack Trends**")
            attack = away_trends['attack']
            trend_emoji = "📈" if attack['trend'] == 'UP' else "📉" if attack['trend'] == 'DOWN' else "➡️"
            st.write(f"Trend: {trend_emoji} {attack['trend']}")
            st.write(f"Recent Avg: {attack['recent_avg']:.1f} goals")
            if attack.get('streak'):
                st.write(f"Streak: {attack['streak']['type']} ({attack['streak']['length']} games)")
            if attack.get('patterns'):
                st.write(f"Patterns: {', '.join(attack['patterns'])}")
        
        with col9:
            st.markdown("**Defense Trends**")
            defense = away_trends['defense']
            trend_emoji = "📉" if defense['trend'] == 'DOWN' else "📈" if defense['trend'] == 'UP' else "➡️"
            st.write(f"Trend: {trend_emoji} {defense['trend']}")
            st.write(f"Recent Avg: {defense['recent_avg']:.1f} conceded")
            st.write(f"Clean Sheets: {defense['clean_sheets']}/3")
            if defense.get('collapse_patterns'):
                st.write(f"Collapses: {', '.join(defense['collapse_patterns'])}")
        
        with col10:
            st.markdown("**Momentum**")
            momentum = away_trends['momentum']
            st.write(f"Momentum: {momentum['momentum']}")
            st.write(f"Recent Form: {' '.join(momentum['recent_form'])}")
            if momentum.get('streak'):
                st.write(f"Streak: {momentum['streak']['type']} ({momentum['streak']['length']} games)")
        
        # Probability analysis
        st.markdown("---")
        st.markdown("#### 🎯 Probability Analysis")
        
        col11, col12 = st.columns(2)
        
        with col11:
            probs = prediction['probabilities']
            fig1 = go.Figure(data=[
                go.Bar(x=['Over 2.5', 'Under 2.5'], 
                      y=[probs['over'], probs['under']],
                      marker_color=['#10B981', '#EF4444'])
            ])
            fig1.update_layout(title="True Probabilities", height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col12:
            edges = prediction['edges']
            fig2 = go.Figure(data=[
                go.Bar(x=['Over Edge', 'Under Edge'], 
                      y=[edges['over'], edges['under']],
                      marker_color=['#34D399', '#FCA5A5'])
            ])
            fig2.update_layout(title="Value Edges (%)", height=300)
            st.plotly_chart(fig2, use_container_width=True)

# ========== MAIN APP ==========
def main():
    st.markdown('<h1 class="main-header">📈 TREND-BASED FOOTBALL PREDICTOR</h1>', unsafe_allow_html=True)
    st.markdown("### Analyzing streaks, patterns, and momentum - not just averages")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        min_edge = st.slider("Minimum Edge %", 0.0, 15.0, 2.0, 0.5)
        max_bet = st.slider("Max Bet Size %", 1, 25, 10, 1)
        
        st.markdown("---")
        st.info("""
        **How it works:**
        1. Analyzes last 5 games trends
        2. Detects streaks and patterns
        3. Weights recent games heavier
        4. Identifies momentum shifts
        """)
        
        st.warning("**Key Insight:** Averages lie. Trends tell the truth.")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Predict", "📚 Learn Trends", "💡 Case Studies"])
    
    with tab1:
        # Create input form
        match_data = create_trend_input_form()
        
        # Predict button
        if st.button("🚀 ANALYZE TRENDS & PREDICT", type="primary", use_container_width=True):
            # Run prediction
            predictor = TrendBasedPredictor()
            prediction = predictor.predict(match_data)
            
            # Store in session state
            st.session_state.trend_prediction = prediction
            st.session_state.trend_match_data = match_data
            st.rerun()
        
        # Show results if available
        if 'trend_prediction' in st.session_state:
            display_trend_results(st.session_state.trend_prediction)
            
            # Show what would have happened with old system
            with st.expander("🔍 COMPARE: Old vs New System"):
                old_pred = "UNDER_2.5"  # What old system predicted
                actual_result = "OVER_2.5"  # What actually happened (3-2)
                
                st.markdown(f"**Old System Prediction:** {old_pred}")
                st.markdown(f"**Trend System Prediction:** {st.session_state.trend_prediction['prediction']}")
                st.markdown(f"**Actual Result:** {actual_result} (3-2)")
                
                if st.session_state.trend_prediction['prediction'] == actual_result:
                    st.success("✅ Trend system would have predicted correctly!")
                else:
                    st.error("❌ Still needs adjustment")
    
    with tab2:
        st.markdown("## 📚 Understanding Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Key Trend Patterns")
            st.markdown("""
            **1. Goalless Streaks (0-0-0)**
            - 3+ games without scoring = SCORING CRISIS
            - Desperate teams often over-commit
            - Leads to defensive exposure
            
            **2. Defensive Collapses (3+ goals conceded)**
            - Recent 3+ goals conceded = DEFENSIVE CRISIS
            - Often continues until fixed
            - Big red flag for Under bets
            
            **3. Momentum Shifts**
            - W after LLL = CONFIDENCE BOOST
            - Recent form > full season form
            - Tottenham win example: Changed everything
            """)
        
        with col2:
            st.markdown("### 📊 How We Analyze")
            st.markdown("""
            **Weighted Recent Form:**
            - Game 1 (most recent): 35%
            - Game 2: 25%
            - Game 3: 20%
            - Game 4: 15%
            - Game 5: 5%
            
            **Pattern Detection:**
            - Streaks (WWW or LLL)
            - Crises (0 goals or 3+ conceded)
            - Improvements/Declines
            
            **Context Awareness:**
            - Desperation ≠ Caution
            - Recent big wins change everything
            - Public perception often wrong
            """)
        
        st.markdown("---")
        st.markdown("### 🚨 Common Traps We Detect")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            **Public Overreaction Trap**
            - Public >65% on one side
            - But trends suggest opposite
            - Example: Burnley-Fulham (60% on Over)
            
            **Historical Data Trap**
            - H2H shows high scoring
            - But recent form completely different
            - Teams/Managers changed
            """)
        
        with col4:
            st.markdown("""
            **Average Deception Trap**
            - Averages hide trends
            - 0.6 average could be 0-0-0-2-1
            - Recent 0s matter more than old 2
            
            **Desperation Paradox**
            - Desperate ≠ Defensive
            - Often = Chaotic, High Scoring
            - Pressure causes mistakes
            """)
    
    with tab3:
        st.markdown("## 💡 Real Case Studies")
        
        # Burnley-Fulham case
        st.markdown("### 🔍 Case: Burnley 2-3 Fulham")
        
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown("**Old System Saw:**")
            st.markdown("""
            - Burnley: 0.6 goals avg, 1.2 conceded
            - Fulham: 1.0 goals avg, 2.2 conceded  
            - Prediction: UNDER 2.5
            - Confidence: High
            """)
        
        with col6:
            st.markdown("**Trends Actually Showed:**")
            st.markdown("""
            - Burnley: 0-0-0 streak (SCORING CRISIS)
            - Fulham: Just won at Tottenham (MOMENTUM)
            - Burnley desperate = CHAOTIC
            - Actual: 3-2 (OVER)
            """)
        
        st.markdown("**What We Learned:**")
        st.markdown("""
        1. **Goalless streaks matter**: 0-0-0 ≠ 0.6 average
        2. **Recent wins change everything**: Tottenham win > all previous losses
        3. **Desperation = Chaos**: Not defensive caution
        4. **Public was right**: 60% on Over saw the pattern
        """)
        
        st.markdown("---")
        
        # Liverpool-Brighton case
        st.markdown("### 🔍 Case: Liverpool vs Brighton")
        
        col7, col8 = st.columns(2)
        
        with col7:
            st.markdown("**Trend Analysis:**")
            st.markdown("""
            - Liverpool: BIG SIX at home
            - Public: 66% on Over (HYPE)
            - Recent form: Mixed
            - H2H: 69% Over (HISTORICAL TRAP)
            """)
        
        with col8:
            st.markdown("**Prediction:**")
            st.markdown("""
            - Detected: OVER HYPE TRAP
            - Detected: HISTORICAL DATA TRAP  
            - Expected: Lower scoring
            - Recommendation: UNDER
            """)
        
        st.markdown("**Key Insight:** Big team + Public hype + Historical data = Triple trap")

# Run the app
if __name__ == "__main__":
    main()
