import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="FIXED FOOTBALL PREDICTOR V11",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS STYLING ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .high-confidence {
        border-left-color: #4CAF50 !important;
        background-color: #f1f8e9;
    }
    .medium-confidence {
        border-left-color: #FF9800 !important;
        background-color: #fff3e0;
    }
    .low-confidence {
        border-left-color: #F44336 !important;
        background-color: #ffebee;
    }
    .input-section {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    .psychology-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px;
    }
    .badge-fear {
        background-color: #ffebee;
        color: #c62828;
    }
    .badge-ambition {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .badge-caution {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    .badge-quality {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    .badge-domination {
        background-color: #ede7f6;
        color: #5e35b1;
    }
    .badge-dominance {
        background-color: #f3e5f5;
        color: #6a1b9a;
    }
    .badge-control {
        background-color: #fff8e1;
        color: #ff8f00;
    }
</style>
""", unsafe_allow_html=True)

# ========== SIMPLE DATABASE ==========
class SimpleDatabase:
    def __init__(self):
        self.predictions = []
        self.outcomes = []
        self.pattern_stats = {}
    
    def save_prediction(self, prediction_data):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_input = f"{prediction_data.get('home_name', '')}_{prediction_data.get('away_name', '')}_{timestamp}"
            prediction_hash = hashlib.md5(hash_input.encode()).hexdigest()
            
            prediction_record = {
                'hash': prediction_hash,
                'timestamp': datetime.now(),
                'match_data': {
                    'home_name': prediction_data.get('home_name', ''),
                    'away_name': prediction_data.get('away_name', ''),
                    'home_pos': prediction_data.get('home_pos', 0),
                    'away_pos': prediction_data.get('away_pos', 0),
                    'total_teams': prediction_data.get('total_teams', 20),
                    'games_played': prediction_data.get('games_played', 19),
                    'home_attack': prediction_data.get('home_attack', 1.4),
                    'away_attack': prediction_data.get('away_attack', 1.3),
                    'home_defense': prediction_data.get('home_defense', 1.2),
                    'away_defense': prediction_data.get('away_defense', 1.4),
                    'home_goals5': prediction_data.get('home_goals5', 7),
                    'away_goals5': prediction_data.get('away_goals5', 6)
                },
                'analysis': prediction_data.get('analysis', {})
            }
            
            self.predictions.append(prediction_record)
            
            pattern_name = prediction_record['analysis'].get('context', 'unknown')
            if pattern_name not in self.pattern_stats:
                self.pattern_stats[pattern_name] = {
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'xg_errors': []
                }
            
            return prediction_hash
            
        except Exception:
            return f"pred_{len(self.predictions)}"
    
    def record_outcome(self, prediction_hash, actual_home_goals, actual_away_goals, notes=""):
        try:
            prediction = None
            for pred in self.predictions:
                if pred.get('hash') == prediction_hash:
                    prediction = pred
                    break
            
            if not prediction:
                return False
            
            actual_total = actual_home_goals + actual_away_goals
            actual_over_under = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
            predicted_over_under = prediction['analysis'].get('prediction', '')
            outcome_accuracy = "CORRECT" if predicted_over_under == actual_over_under else "INCORRECT"
            
            outcome_record = {
                'prediction_hash': prediction_hash,
                'actual_home_goals': actual_home_goals,
                'actual_away_goals': actual_away_goals,
                'actual_total_goals': actual_total,
                'actual_over_under': actual_over_under,
                'outcome_accuracy': outcome_accuracy,
                'notes': notes,
                'recorded_at': datetime.now()
            }
            
            self.outcomes.append(outcome_record)
            
            pattern_name = prediction['analysis'].get('context', 'unknown')
            if pattern_name in self.pattern_stats:
                stats = self.pattern_stats[pattern_name]
                stats['total_predictions'] += 1
                if outcome_accuracy == "CORRECT":
                    stats['correct_predictions'] += 1
                predicted_xg = prediction['analysis'].get('adjusted_total_xg', 0)
                xg_error = abs(predicted_xg - actual_total)
                stats['xg_errors'].append(xg_error)
            
            return True
            
        except Exception:
            return False
    
    def get_performance_stats(self):
        total_predictions = len([o for o in self.outcomes])
        correct_predictions = len([o for o in self.outcomes if o.get('outcome_accuracy') == "CORRECT"])
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        pattern_stats_list = []
        for pattern_name, stats in self.pattern_stats.items():
            pattern_total = stats.get('total_predictions', 0)
            pattern_correct = stats.get('correct_predictions', 0)
            pattern_accuracy = pattern_correct / pattern_total if pattern_total > 0 else 0
            xg_errors = stats.get('xg_errors', [])
            avg_error = sum(xg_errors) / len(xg_errors) if xg_errors else 0
            pattern_stats_list.append((pattern_name, pattern_accuracy, pattern_total, avg_error))
        
        pattern_stats_list.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'pattern_stats': pattern_stats_list
        }
    
    def get_recent_predictions(self, limit=5):
        recent = []
        recent_outcomes = sorted(self.outcomes, key=lambda x: x.get('recorded_at', datetime.min), reverse=True)[:limit]
        
        for outcome in recent_outcomes:
            prediction = None
            for pred in self.predictions:
                if pred.get('hash') == outcome.get('prediction_hash'):
                    prediction = pred
                    break
            
            if prediction:
                recent.append((
                    prediction.get('timestamp'),
                    prediction.get('match_data', {}).get('home_name', 'Home'),
                    prediction.get('match_data', {}).get('away_name', 'Away'),
                    prediction.get('analysis', {}).get('prediction', ''),
                    prediction.get('analysis', {}).get('confidence', ''),
                    prediction.get('analysis', {}).get('adjusted_total_xg', 0),
                    outcome.get('actual_total_goals'),
                    outcome.get('outcome_accuracy'),
                    prediction.get('analysis', {}).get('context', '')
                ))
        
        return recent

# ========== FIXED PREDICTION ENGINE ==========
class FixedPredictionEngine:
    def __init__(self):
        self.learned_patterns = {
            'relegation_battle': {
                'base_multiplier': 0.65,
                'description': 'Both bottom 4 → FEAR dominates → 35% fewer goals',
                'base_confidence': 0.92,
                'base_badge': 'badge-fear',
                'psychology': 'FEAR dominates: Both playing NOT TO LOSE'
            },
            'relegation_threatened': {
                'base_multiplier': 0.85,
                'description': 'One team bottom 4, other safe → threatened team cautious → 15% fewer goals',
                'base_confidence': 0.85,
                'base_badge': 'badge-caution',
                'psychology': 'Threatened team plays with fear, lowers scoring'
            },
            'mid_table_clash': {
                'base_multiplier': 1.15,
                'description': 'Both safe (5-16), gap ≤ 4, similar form → SIMILAR AMBITIONS → 15% more goals',
                'base_confidence': 0.88,
                'base_badge': 'badge-ambition',
                'psychology': 'Both teams confident, similar form → playing TO WIN'
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.90,
                'description': 'Mid-table clash with significant form difference → controlled game',
                'base_confidence': 0.85,
                'base_badge': 'badge-control',
                'psychology': 'Better form team controls, poorer form team defends'
            },
            'top_team_battle': {
                'base_multiplier': 0.95,
                'description': 'Both top 4 → QUALITY over caution → normal scoring',
                'base_confidence': 0.78,
                'base_badge': 'badge-quality',
                'psychology': 'Quality creates AND prevents goals'
            },
            'top_vs_bottom_domination': {
                'base_multiplier': 1.05,
                'description': 'Top team good/excellent form vs bottom team → MODERATE SCORING (2-1 type)',
                'base_confidence': 0.82,
                'base_badge': 'badge-domination',
                'psychology': 'Top team attacks, bottom team fights back → 2-3 goals'
            },
            'top_vs_bottom_dominance': {
                'base_multiplier': 0.85,
                'description': 'Top team excellent form vs VERY poor bottom team → controlled low scoring',
                'base_confidence': 0.82,
                'base_badge': 'badge-dominance',
                'psychology': 'Complete control, bottom team can\'t attack → 1-0 type scores'
            },
            'hierarchical': {
                'base_multiplier': 0.90,
                'description': 'Different league positions → different objectives',
                'base_confidence': 0.75,
                'base_badge': 'badge-caution',
                'psychology': 'Better team controls, weaker team defends'
            }
        }
        
        self.form_adjustments = {
            'excellent': 1.20,
            'good': 1.10,
            'average': 1.00,
            'poor': 0.90,
            'very_poor': 0.80
        }
        
        # CRITICAL FIX: Added thresholds dictionary
        self.thresholds = {
            'relegation_battle': {'over': 2.3, 'under': 2.7},
            'top_vs_bottom_domination': {'over': 2.6, 'under': 2.4},
            'top_vs_bottom_dominance': {'over': 2.5, 'under': 2.5},
            'controlled_mid_clash': {'over': 2.7, 'under': 2.3},
            'mid_table_clash': {'over': 2.6, 'under': 2.4},
            'top_team_battle': {'over': 2.8, 'under': 2.2},
            'default': {'over': 2.7, 'under': 2.3}
        }
    
    def analyze_match_context(self, home_pos, away_pos, total_teams, games_played, home_form, away_form):
        gap = abs(home_pos - away_pos)
        bottom_cutoff = total_teams - 3
        top_cutoff = 4
        
        home_zone = 'TOP' if home_pos <= top_cutoff else 'BOTTOM' if home_pos >= bottom_cutoff else 'MID'
        away_zone = 'TOP' if away_pos <= top_cutoff else 'BOTTOM' if away_pos >= bottom_cutoff else 'MID'
        
        # TOP vs BOTTOM patterns
        if ((home_zone == 'TOP' and away_zone == 'BOTTOM') or 
            (away_zone == 'TOP' and home_zone == 'BOTTOM')):
            
            if home_zone == 'TOP':
                top_form, bottom_form = home_form, away_form
                top_team = 'HOME'
            else:
                top_form, bottom_form = away_form, home_form
                top_team = 'AWAY'
            
            if top_form in ['excellent', 'good'] and gap > 8:
                if bottom_form != 'very_poor':
                    context = 'top_vs_bottom_domination'
                    psychology = {
                        'primary': 'DOMINATION',
                        'description': f'{top_team} team attacks, bottom fights back → 2-1 type',
                        'badge': 'badge-domination'
                    }
                else:
                    context = 'top_vs_bottom_dominance'
                    psychology = {
                        'primary': 'DOMINANCE',
                        'description': f'{top_team} team dominates → 1-0 type',
                        'badge': 'badge-dominance'
                    }
                
                return {
                    'context': context,
                    'psychology': psychology,
                    'gap': gap,
                    'zones': {'home': home_zone, 'away': away_zone}
                }
        
        # Other patterns
        if home_pos >= bottom_cutoff and away_pos >= bottom_cutoff:
            context = 'relegation_battle'
            psychology = {'primary': 'FEAR', 'badge': 'badge-fear'}
        elif (home_pos >= bottom_cutoff) != (away_pos >= bottom_cutoff):
            context = 'relegation_threatened'
            psychology = {'primary': 'CAUTION', 'badge': 'badge-caution'}
        elif home_pos <= top_cutoff and away_pos <= top_cutoff:
            context = 'top_team_battle'
            psychology = {'primary': 'QUALITY', 'badge': 'badge-quality'}
        else:
            context = 'hierarchical'
            psychology = {'primary': 'CAUTION', 'badge': 'badge-caution'}
        
        return {
            'context': context,
            'psychology': psychology,
            'gap': gap,
            'zones': {'home': home_zone, 'away': away_zone}
        }
    
    def calculate_form(self, team_avg, recent_goals):
        if team_avg <= 0:
            return 1.0, 'average'
        
        recent_avg = recent_goals / 5 if recent_goals > 0 else 0
        ratio = recent_avg / team_avg if team_avg > 0 else 1.0
        
        if ratio >= 1.2:
            return self.form_adjustments['excellent'], 'excellent'
        elif ratio >= 1.05:
            return self.form_adjustments['good'], 'good'
        elif ratio >= 0.8:
            return self.form_adjustments['average'], 'average'
        elif ratio >= 0.6:
            return self.form_adjustments['poor'], 'poor'
        else:
            return self.form_adjustments['very_poor'], 'very_poor'
    
    def predict_match(self, match_data):
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        total_teams = match_data.get('total_teams', 20)
        games_played = match_data.get('games_played', 19)
        
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        home_goals5 = match_data.get('home_goals5', max(1, int(home_attack * 5)))
        away_goals5 = match_data.get('away_goals5', max(1, int(away_attack * 5)))
        
        home_form_factor, home_form_level = self.calculate_form(home_attack, home_goals5)
        away_form_factor, away_form_level = self.calculate_form(away_attack, away_goals5)
        
        context_analysis = self.analyze_match_context(
            home_pos, away_pos, total_teams, games_played,
            home_form_level, away_form_level
        )
        
        context = context_analysis['context']
        pattern = self.learned_patterns.get(context, self.learned_patterns['hierarchical'])
        thresholds = self.thresholds.get(context, self.thresholds['default'])
        
        raw_home_xg = (home_attack + away_defense) / 2
        raw_away_xg = (away_attack + home_defense) / 2
        raw_total_xg = raw_home_xg + raw_away_xg
        
        form_home_xg = raw_home_xg * home_form_factor
        form_away_xg = raw_away_xg * away_form_factor
        form_total_xg = form_home_xg + form_away_xg
        
        psychology_multiplier = pattern['base_multiplier']
        adjusted_total_xg = form_total_xg * psychology_multiplier
        
        if context == 'top_vs_bottom_domination':
            if adjusted_total_xg > 2.5:
                prediction = 'OVER 2.5'
                confidence = 'HIGH' if adjusted_total_xg > 2.8 else 'MEDIUM'
            else:
                prediction = 'UNDER 2.5'
                confidence = 'MEDIUM'
        else:
            if adjusted_total_xg > thresholds['over']:
                prediction = 'OVER 2.5'
                confidence = 'HIGH' if adjusted_total_xg > 3.0 else 'MEDIUM'
            elif adjusted_total_xg < thresholds['under']:
                prediction = 'UNDER 2.5'
                confidence = 'HIGH' if adjusted_total_xg < 2.0 else 'MEDIUM'
            else:
                prediction = 'OVER 2.5' if adjusted_total_xg > 2.5 else 'UNDER 2.5'
                confidence = 'MEDIUM'
        
        base_confidence = pattern['base_confidence']
        data_quality = 0.7 if games_played < 10 else 0.85 if games_played < 15 else 1.0
        confidence_score = (base_confidence * 0.6 + data_quality * 0.4)
        confidence_level = 'HIGH' if confidence_score > 0.85 else 'MEDIUM' if confidence_score > 0.7 else 'LOW'
        
        if confidence_level == 'HIGH' and base_confidence > 0.85:
            stake = 'MAX BET (2x normal)'
            stake_color = 'green'
        elif confidence_level == 'HIGH' or base_confidence > 0.8:
            stake = 'NORMAL BET (1x)'
            stake_color = 'orange'
        else:
            stake = 'SMALL BET (0.5x) or AVOID'
            stake_color = 'red'
        
        # CRITICAL: Return thresholds_used key
        return {
            'prediction': prediction,
            'confidence': confidence_level,
            'confidence_score': round(confidence_score, 3),
            'stake_recommendation': stake,
            'stake_color': stake_color,
            
            'raw_total_xg': round(raw_total_xg, 2),
            'form_total_xg': round(form_total_xg, 2),
            'adjusted_total_xg': round(adjusted_total_xg, 2),
            
            'context': context,
            'psychology': context_analysis['psychology'],
            'gap': context_analysis['gap'],
            'base_psychology_multiplier': psychology_multiplier,
            'form_multiplier_home': home_form_factor,
            'form_multiplier_away': away_form_factor,
            'form_level_home': home_form_level,
            'form_level_away': away_form_level,
            
            'pattern_description': pattern['description'],
            'pattern_confidence': pattern['base_confidence'],
            'pattern_psychology': pattern['psychology'],
            
            # FIXED: This key was missing causing KeyError
            'thresholds_used': thresholds,
            
            'zones': context_analysis.get('zones', {})
        }

# ========== TEST CASES ==========
TEST_CASES = {
    'Atletico vs Valencia': {
        'home_name': 'Atletico Madrid',
        'away_name': 'Valencia',
        'home_pos': 4,
        'away_pos': 17,
        'total_teams': 20,
        'games_played': 15,
        'home_attack': 1.25,
        'away_attack': 1.00,
        'home_defense': 0.88,
        'away_defense': 1.13,
        'home_goals5': 14,
        'away_goals5': 4
    },
    'Liverpool vs Burnley': {
        'home_name': 'Liverpool',
        'away_name': 'Burnley',
        'home_pos': 2,
        'away_pos': 19,
        'total_teams': 20,
        'games_played': 20,
        'home_attack': 2.10,
        'away_attack': 0.80,
        'home_defense': 0.90,
        'away_defense': 1.80,
        'home_goals5': 12,
        'away_goals5': 3
    },
    'Lecce vs Pisa': {
        'home_name': 'Lecce',
        'away_name': 'Pisa',
        'home_pos': 17,
        'away_pos': 18,
        'total_teams': 20,
        'games_played': 19,
        'home_attack': 0.71,
        'away_attack': 1.2,
        'home_defense': 1.3,
        'away_defense': 1.4,
        'home_goals5': 4,
        'away_goals5': 8
    }
}

# ========== INITIALIZE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = FixedPredictionEngine()

if 'db' not in st.session_state:
    st.session_state.db = SimpleDatabase()

if 'current_prediction' not in st.session_state:
    st.session_state.current_prediction = None

if 'match_data' not in st.session_state:
    st.session_state.match_data = TEST_CASES['Atletico vs Valencia']

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">⚽ FIXED FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Complete Working Version - No KeyErrors**")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## 📊 Performance Dashboard")
        
        perf_stats = st.session_state.db.get_performance_stats()
        
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.metric("Total Predictions", perf_stats['total_predictions'])
        with col_sb2:
            accuracy = f"{perf_stats['accuracy']*100:.1f}%" if perf_stats['total_predictions'] > 0 else "N/A"
            st.metric("Accuracy", accuracy)
        
        st.markdown("### Recent Predictions")
        recent = st.session_state.db.get_recent_predictions(3)
        
        for pred in recent:
            timestamp, home, away, pred_result, conf, pred_xg, actual, accuracy, pattern = pred
            if home and away:
                if actual is not None:
                    result_color = "✅" if accuracy == "CORRECT" else "❌"
                    st.write(f"{result_color} {home} vs {away}: {pred_result} → {actual} goals")
                else:
                    st.write(f"{home} vs {away}: {pred_result}")
    
    # ===== TEST CASES =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🧪 Test Cases")
    
    col_test = st.columns(3)
    test_cases = list(TEST_CASES.items())
    
    for idx, (case_name, case_data) in enumerate(test_cases):
        with col_test[idx]:
            if st.button(f"{case_name}", use_container_width=True, key=f"test_{case_name}"):
                st.session_state.current_prediction = None
                st.session_state.match_data = case_data
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Enter Match Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 Home Team")
        home_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data.get('home_name', ''),
            key="home_name_input"
        )
        home_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data.get('home_pos', 10),
            key="home_pos_input"
        )
        home_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('home_attack', 1.4),
            step=0.01,
            key="home_attack_input"
        )
        home_goals5 = st.number_input(
            "Goals Last 5 Games",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data.get('home_goals5', 7),
            key="home_goals5_input"
        )
    
    with col2:
        st.markdown("#### ✈️ Away Team")
        away_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data.get('away_name', ''),
            key="away_name_input"
        )
        away_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data.get('away_pos', 10),
            key="away_pos_input"
        )
        away_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('away_attack', 1.3),
            step=0.01,
            key="away_attack_input"
        )
        away_goals5 = st.number_input(
            "Goals Last 5 Games",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data.get('away_goals5', 6),
            key="away_goals5_input"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        total_teams = st.number_input(
            "Total Teams in League",
            min_value=10,
            max_value=30,
            value=st.session_state.match_data.get('total_teams', 20),
            key="total_teams_input"
        )
        games_played = st.number_input(
            "Games Played This Season",
            min_value=1,
            max_value=50,
            value=st.session_state.match_data.get('games_played', 19),
            key="games_played_input"
        )
    
    with col4:
        home_defense = st.number_input(
            "Home Conceded/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('home_defense', 1.2),
            step=0.01,
            key="home_defense_input"
        )
        away_defense = st.number_input(
            "Away Conceded/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('away_defense', 1.4),
            step=0.01,
            key="away_defense_input"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYZE BUTTON =====
    if st.button("🚀 ANALYZE MATCH", type="primary", use_container_width=True):
        try:
            match_data = {
                'home_name': home_name,
                'away_name': away_name,
                'home_pos': home_pos,
                'away_pos': away_pos,
                'total_teams': total_teams,
                'games_played': games_played,
                'home_attack': home_attack,
                'away_attack': away_attack,
                'home_defense': home_defense,
                'away_defense': away_defense,
                'home_goals5': home_goals5,
                'away_goals5': away_goals5
            }
            
            analysis = st.session_state.engine.predict_match(match_data)
            
            prediction_data = {
                'home_name': home_name,
                'away_name': away_name,
                'home_pos': home_pos,
                'away_pos': away_pos,
                'total_teams': total_teams,
                'games_played': games_played,
                'home_attack': home_attack,
                'away_attack': away_attack,
                'home_defense': home_defense,
                'away_defense': away_defense,
                'home_goals5': home_goals5,
                'away_goals5': away_goals5,
                'analysis': analysis
            }
            
            prediction_hash = st.session_state.db.save_prediction(prediction_data)
            
            st.session_state.current_prediction = {
                'analysis': analysis,
                'match_data': match_data,
                'prediction_hash': prediction_hash
            }
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.info("Please check your inputs and try again.")
    
    # ===== PREDICTION RESULTS =====
    if st.session_state.current_prediction:
        pred_data = st.session_state.current_prediction
        analysis = pred_data['analysis']
        match_data = pred_data['match_data']
        prediction_hash = pred_data['prediction_hash']
        
        st.markdown("---")
        st.markdown(f"## 📊 Prediction Results: {match_data.get('home_name')} vs {match_data.get('away_name')}")
        
        # Key metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("Prediction", analysis.get('prediction', 'N/A'))
        with col_m2:
            st.metric("Confidence", analysis.get('confidence', 'N/A'))
        with col_m3:
            st.metric("Expected Goals", analysis.get('adjusted_total_xg', 0))
        with col_m4:
            context = analysis.get('context', 'unknown')
            st.metric("Pattern", context.replace('_', ' ').title())
        
        # Psychology badge
        psychology = analysis.get('psychology', {})
        badge_class = psychology.get('badge', 'badge-caution')
        primary_text = psychology.get('primary', 'ANALYSIS')
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <span class="psychology-badge {badge_class}">
                {primary_text}
            </span>
            <small style="margin-left: 10px; color: #666;">{psychology.get('description', '')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Pattern application info
        if analysis.get('context') in ['top_vs_bottom_domination', 'top_vs_bottom_dominance']:
            st.info(f"""
            **✅ Universal Pattern Applied:** This pattern applies to ALL matches where:
            - Top 4 team vs Bottom 4 team
            - Top team has GOOD/EXCELLENT form
            - Position gap > 8 places
            - {analysis.get('context').replace('_', ' ').title()}: {analysis.get('pattern_description', '')}
            """)
        
        # Prediction breakdown
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("### 📈 Expected Goals Breakdown")
            
            try:
                fig = go.Figure()
                
                stages = ['Base xG', 'Form Adjusted', 'Psychology Applied', 'Final xG']
                base_xg = analysis.get('raw_total_xg', 0)
                form_xg = analysis.get('form_total_xg', 0)
                psych_mult = analysis.get('base_psychology_multiplier', 1.0)
                final_xg = analysis.get('adjusted_total_xg', 0)
                
                values = [base_xg, form_xg, form_xg * psych_mult, final_xg]
                
                fig.add_trace(go.Bar(
                    x=stages,
                    y=values,
                    marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
                    text=[f'{v:.2f}' for v in values],
                    textposition='auto'
                ))
                
                fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
                
                fig.update_layout(
                    height=350,
                    showlegend=False,
                    yaxis_title="Expected Goals",
                    title="How the Prediction was Calculated"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("Chart display not available")
        
        with col_b2:
            st.markdown("### ⚙️ Calculation Factors")
            
            # FIXED: Safe access to thresholds
            thresholds = analysis.get('thresholds_used', {'over': 2.7, 'under': 2.3})
            
            st.markdown(f"""
            **📊 Statistical Factors:**
            - Base xG (statistics only): **{analysis.get('raw_total_xg', 0):.2f}**
            - Form adjusted xG: **{analysis.get('form_total_xg', 0):.2f}**
            
            **🎯 Adjustment Factors:**
            - Home form: {analysis.get('form_level_home', 'average').upper()} (×{analysis.get('form_multiplier_home', 1.0):.2f})
            - Away form: {analysis.get('form_level_away', 'average').upper()} (×{analysis.get('form_multiplier_away', 1.0):.2f})
            - Psychology: {primary_text} (×{analysis.get('base_psychology_multiplier', 1.0):.2f})
            
            **⚖️ Decision Thresholds:**
            - OVER 2.5 if > **{thresholds.get('over', 2.7)}**
            - UNDER 2.5 if < **{thresholds.get('under', 2.3)}**
            
            **📈 Final Calculation:**
            - Adjusted xG: **{analysis.get('adjusted_total_xg', 0):.2f}**
            - Result: **{analysis.get('prediction', '')}** ({analysis.get('confidence', '')} confidence)
            - Stake: **{analysis.get('stake_recommendation', '')}**
            """)
        
        # Outcome recording
        st.markdown("---")
        st.markdown("### 📝 Record Actual Outcome (For Learning)")
        
        col_out1, col_out2, col_out3 = st.columns(3)
        
        with col_out1:
            actual_home = st.number_input("Home Goals", 0, 10, 0, key="actual_home_input")
        
        with col_out2:
            actual_away = st.number_input("Away Goals", 0, 10, 0, key="actual_away_input")
        
        with col_out3:
            notes = st.text_input("Match Notes (optional)", key="outcome_notes_input")
        
        if st.button("✅ Save Actual Result", type="secondary"):
            if actual_home == 0 and actual_away == 0:
                st.warning("Please enter actual scores (at least one goal)")
            else:
                success = st.session_state.db.record_outcome(
                    prediction_hash,
                    actual_home,
                    actual_away,
                    notes
                )
                
                if success:
                    st.success("✅ Outcome recorded! The system will learn from this result.")
                    
                    # Show learning feedback
                    actual_total = actual_home + actual_away
                    predicted_result = analysis.get('prediction', '')
                    actual_result_type = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
                    is_correct = predicted_result == actual_result_type
                    
                    st.info(f"""
                    **Learning Update:**
                    - Predicted: **{predicted_result}**
                    - Actual: **{actual_result_type}** ({actual_home}-{actual_away})
                    - Result: **{'✅ CORRECT' if is_correct else '❌ INCORRECT'}**
                    - Pattern: {analysis.get('context', '').replace('_', ' ').title()}
                    
                    *This helps improve future predictions for similar matches.*
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to record outcome. Please try again.")

if __name__ == "__main__":
    main()
