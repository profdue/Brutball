import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import logging
import math

# ========== SETUP LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('football_predictor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="ULTIMATE FOOTBALL PREDICTOR",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== VALIDATION FUNCTIONS ==========
def validate_match_data(match_data):
    """Validate all match data inputs"""
    errors = []
    total_teams = match_data.get('total_teams', 20)
    
    # Position validation
    home_pos = match_data.get('home_pos', 10)
    away_pos = match_data.get('away_pos', 10)
    
    if not isinstance(home_pos, (int, float)):
        errors.append("Home position must be a number")
    elif not (1 <= home_pos <= total_teams):
        errors.append(f"Home position must be between 1 and {total_teams}")
    
    if not isinstance(away_pos, (int, float)):
        errors.append("Away position must be a number")
    elif not (1 <= away_pos <= total_teams):
        errors.append(f"Away position must be between 1 and {total_teams}")
    
    # Attack/defense range validation
    stat_fields = ['home_attack', 'away_attack', 'home_defense', 'away_defense']
    for field in stat_fields:
        value = match_data.get(field, 1.5)
        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be a number")
        elif value < 0.0 or value > 5.0:
            errors.append(f"{field} must be between 0.0 and 5.0")
    
    # Goals in last 5 validation
    if not isinstance(match_data.get('home_goals5', 0), (int, float)):
        errors.append("Home goals in last 5 must be a number")
    elif match_data.get('home_goals5', 0) < 0:
        errors.append("Home goals in last 5 cannot be negative")
    
    if not isinstance(match_data.get('away_goals5', 0), (int, float)):
        errors.append("Away goals in last 5 must be a number")
    elif match_data.get('away_goals5', 0) < 0:
        errors.append("Away goals in last 5 cannot be negative")
    
    return errors

def validate_league_settings(total_teams, games_played):
    """Validate league settings"""
    errors = []
    
    if not isinstance(total_teams, (int, float)):
        errors.append("Total teams must be a number")
    elif total_teams < 10 or total_teams > 40:
        errors.append("Total teams must be between 10 and 40")
    
    if not isinstance(games_played, (int, float)):
        errors.append("Games played must be a number")
    elif games_played < 1:
        errors.append("Games played must be at least 1")
    elif games_played > total_teams * 2:
        errors.append(f"Games played cannot exceed {total_teams * 2} (full season)")
    
    return errors

# ========== CSS STYLING ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .input-section {
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .team-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .edge-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 8px solid;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .edge-high { border-left-color: #4CAF50; }
    .edge-medium { border-left-color: #FF9800; }
    .edge-low { border-left-color: #F44336; }
    .pattern-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 3px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .psychology-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px;
    }
    .profit-highlight {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    .badge-domination { background-color: #ede7f6; color: #5e35b1; }
    .badge-fear { background-color: #ffebee; color: #c62828; }
    .badge-ambition { background-color: #e8f5e9; color: #2e7d32; }
    .badge-control { background-color: #fff8e1; color: #ff8f00; }
    .badge-quality { background-color: #e3f2fd; color: #1565c0; }
    .badge-dominance { background-color: #f3e5f5; color: #6a1b9a; }
    .status-safe { color: #4CAF50; font-weight: bold; }
    .status-danger { color: #F44336; font-weight: bold; }
    .status-mid { color: #FF9800; font-weight: bold; }
    .status-uncertain { color: #2196F3; font-weight: bold; }
    .season-early { color: #2196F3; font-weight: bold; }
    .season-mid { color: #FF9800; font-weight: bold; }
    .season-late { color: #F44336; font-weight: bold; }
    .auto-detection {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
    }
    .validation-error {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #F44336;
        color: #c62828;
    }
    .performance-metric {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        border: 1px solid #e0e0e0;
    }
    .kelly-bet {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .no-bet {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #F44336;
    }
    .bet-reason {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ========== PERSISTENT DATABASE ==========
class PersistentFootballDatabase:
    def __init__(self, storage_file="predictions_db.json"):
        self.storage_file = storage_file
        self.predictions = []
        self.outcomes = []
        self.team_stats = {}
        self.load_data()
        logger.info(f"Database initialized with {len(self.predictions)} predictions")
    
    def load_data(self):
        """Load data from JSON file if it exists"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.predictions = data.get('predictions', [])
                    self.outcomes = data.get('outcomes', [])
                    logger.info(f"Loaded {len(self.predictions)} predictions from {self.storage_file}")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            # Start fresh if file is corrupted
            self.predictions = []
            self.outcomes = []
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'predictions': self.predictions,
                'outcomes': self.outcomes,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, default=str)
            logger.info(f"Database saved with {len(self.predictions)} predictions")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def save_prediction(self, prediction_data):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_input = f"{prediction_data.get('match_data', {}).get('home_name', '')}_{prediction_data.get('match_data', {}).get('away_name', '')}_{timestamp}"
            prediction_hash = hashlib.md5(hash_input.encode()).hexdigest()
            
            prediction_record = {
                'hash': prediction_hash,
                'timestamp': datetime.now().isoformat(),
                'match_data': prediction_data.get('match_data', {}),
                'analysis': prediction_data.get('analysis', {}),
                'auto_detections': prediction_data.get('auto_detections', {})
            }
            
            self.predictions.append(prediction_record)
            self.save_data()
            
            logger.info(f"Prediction saved: {prediction_hash} - {prediction_data.get('match_data', {}).get('home_name', '')} vs {prediction_data.get('match_data', {}).get('away_name', '')}")
            return prediction_hash
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return f"pred_{len(self.predictions)}"
    
    def record_outcome(self, prediction_hash, actual_home, actual_away, notes=""):
        try:
            prediction = None
            for pred in self.predictions:
                if pred.get('hash') == prediction_hash:
                    prediction = pred
                    break
            
            if not prediction:
                logger.warning(f"Prediction not found: {prediction_hash}")
                return False
            
            actual_total = actual_home + actual_away
            actual_over_under = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
            predicted_over_under = prediction['analysis'].get('prediction', '')
            outcome_accuracy = "CORRECT" if predicted_over_under == actual_over_under else "INCORRECT"
            
            outcome_record = {
                'prediction_hash': prediction_hash,
                'actual_home': actual_home,
                'actual_away': actual_away,
                'actual_total': actual_total,
                'actual_over_under': actual_over_under,
                'outcome_accuracy': outcome_accuracy,
                'notes': notes,
                'recorded_at': datetime.now().isoformat()
            }
            
            self.outcomes.append(outcome_record)
            self.save_data()
            
            logger.info(f"Outcome recorded: {prediction_hash} - {actual_home}-{actual_away} - {outcome_accuracy}")
            return True
        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False
    
    def get_performance_stats(self):
        total = len(self.outcomes)
        correct = len([o for o in self.outcomes if o.get('outcome_accuracy') == "CORRECT"])
        accuracy = correct / total if total > 0 else 0
        
        # Calculate recent performance (last 10)
        recent = self.outcomes[-10:] if len(self.outcomes) >= 10 else self.outcomes
        recent_correct = len([o for o in recent if o.get('outcome_accuracy') == "CORRECT"])
        recent_accuracy = recent_correct / len(recent) if recent else 0
        
        # Calculate by confidence level
        conf_stats = {}
        for pred in self.predictions:
            hash_val = pred.get('hash')
            conf = pred.get('analysis', {}).get('confidence', 'MEDIUM')
            # Find matching outcome
            outcome = next((o for o in self.outcomes if o.get('prediction_hash') == hash_val), None)
            if outcome:
                if conf not in conf_stats:
                    conf_stats[conf] = {'total': 0, 'correct': 0}
                conf_stats[conf]['total'] += 1
                if outcome.get('outcome_accuracy') == "CORRECT":
                    conf_stats[conf]['correct'] += 1
        
        conf_accuracies = {}
        for conf, stats in conf_stats.items():
            conf_accuracies[conf] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'recent_10_total': len(recent),
            'recent_10_correct': recent_correct,
            'recent_10_accuracy': recent_accuracy,
            'confidence_accuracies': conf_accuracies
        }
    
    def get_recent_outcomes(self, limit=5):
        """Get most recent outcomes for display"""
        recent = self.outcomes[-limit:] if self.outcomes else []
        formatted = []
        for outcome in recent:
            # Find the matching prediction
            pred = next((p for p in self.predictions if p.get('hash') == outcome.get('prediction_hash')), None)
            if pred:
                match_data = pred.get('match_data', {})
                analysis = pred.get('analysis', {})
                formatted.append({
                    'teams': f"{match_data.get('home_name', '?')} vs {match_data.get('away_name', '?')}",
                    'prediction': analysis.get('prediction', '?'),
                    'confidence': analysis.get('confidence', '?'),
                    'actual': f"{outcome.get('actual_home', 0)}-{outcome.get('actual_away', 0)}",
                    'result': outcome.get('outcome_accuracy', '?'),
                    'timestamp': outcome.get('recorded_at', '')
                })
        return formatted

# ========== ENHANCED PREDICTION ENGINE ==========
class BalancedPredictionEngine:
    def __init__(self):
        self.learned_patterns = {
            'top_vs_bottom_domination': {
                'base_multiplier': 1.08,
                'description': 'Top team good form vs bottom team → 2-1 type scores',
                'psychology': 'DOMINATION',
                'badge': 'badge-domination',
                'accuracy_weight': 1.1,
                'over_bias': 0.15  # Bias towards OVER
            },
            'relegation_battle': {
                'base_multiplier': 0.70,
                'description': 'Both fighting relegation → defensive football',
                'psychology': 'FEAR',
                'badge': 'badge-fear',
                'accuracy_weight': 0.9,
                'under_bias': 0.20  # Bias towards UNDER
            },
            'mid_table_ambition': {
                'base_multiplier': 1.12,
                'description': 'Both safe mid-table → attacking football',
                'psychology': 'AMBITION',
                'badge': 'badge-ambition',
                'accuracy_weight': 1.05,
                'over_bias': 0.10
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.95,
                'description': 'Mid-table with form difference → controlled game',
                'psychology': 'CONTROL',
                'badge': 'badge-control',
                'accuracy_weight': 1.0,
                'neutral_bias': 0.0
            },
            'top_team_battle': {
                'base_multiplier': 0.92,
                'description': 'Top teams facing → quality creates and prevents goals',
                'psychology': 'QUALITY',
                'badge': 'badge-quality',
                'accuracy_weight': 0.95,
                'neutral_bias': 0.0
            },
            'top_vs_bottom_dominance': {
                'base_multiplier': 0.88,
                'description': 'Top team excellent form vs very poor bottom → 1-0 type',
                'psychology': 'DOMINANCE',
                'badge': 'badge-dominance',
                'accuracy_weight': 1.08,
                'under_bias': 0.10
            }
        }
        
        self.edge_patterns = {
            'new_manager_bounce': {
                'multiplier': 1.20,
                'edge_value': 0.18,
                'description': 'Players desperate to impress new manager',
                'bet_type': 'HOME_WIN',
                'accuracy_boost': 0.05,
                'over_bias': 0.08
            },
            'derby_fear': {
                'multiplier': 0.70,
                'edge_value': 0.25,
                'description': 'Fear of losing derby > desire to win',
                'bet_type': 'UNDER_2_0',
                'accuracy_boost': 0.07,
                'under_bias': 0.15
            },
            'european_hangover': {
                'multiplier': 0.80,
                'edge_value': 0.22,
                'description': 'Physical/mental exhaustion from European travel',
                'bet_type': 'OPPONENT_DOUBLE_CHANCE',
                'accuracy_boost': 0.06,
                'under_bias': 0.10
            },
            'dead_rubber': {
                'multiplier': 1.25,
                'edge_value': 0.20,
                'description': 'Beach football mentality, relaxed play',
                'bet_type': 'OVER_2_5',
                'accuracy_boost': 0.08,
                'over_bias': 0.12
            }
        }
        
        # Dynamic thresholds based on match context
        self.thresholds = {
            'relegation_battle': {'over': 2.4, 'under': 2.6},
            'top_vs_bottom_domination': {'over': 2.7, 'under': 2.3},
            'dead_rubber': {'over': 2.3, 'under': 2.7},
            'derby_fear': {'over': 2.9, 'under': 2.1},
            'mid_table_ambition': {'over': 2.6, 'under': 2.4},
            'top_team_battle': {'over': 2.8, 'under': 2.2},
            'top_vs_bottom_dominance': {'over': 2.8, 'under': 2.2},
            'controlled_mid_clash': {'over': 2.7, 'under': 2.3},
            'default': {'over': 2.7, 'under': 2.3}
        }
    
    def auto_detect_context(self, match_data):
        """Enhanced auto-detection with early season handling"""
        total_teams = match_data.get('total_teams', 20)
        games_played = match_data.get('games_played', 1)
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        
        # Validate inputs
        if games_played < 1:
            games_played = 1
        if home_pos < 1 or home_pos > total_teams:
            home_pos = min(max(1, home_pos), total_teams)
        if away_pos < 1 or away_pos > total_teams:
            away_pos = min(max(1, away_pos), total_teams)
        
        # 1. Calculate season phase with enhanced logic
        total_games_season = total_teams * 2
        season_progress = (games_played / total_games_season) * 100
        
        # More nuanced season phases
        if games_played < 6:  # Very early
            season_phase = 'very_early'
            is_late_season = False
            season_factor = 0.65
        elif season_progress <= 33.33:
            season_phase = 'early'
            is_late_season = False
            season_factor = 0.8
        elif season_progress <= 66.66:
            season_phase = 'mid'
            is_late_season = False
            season_factor = 1.0
        elif season_progress <= 85:
            season_phase = 'late'
            is_late_season = True
            season_factor = 1.1
        else:  # Very late
            season_phase = 'very_late'
            is_late_season = True
            season_factor = 1.2
        
        # 2. Calculate team safety zones
        safe_cutoff = int(total_teams * 0.7)
        danger_cutoff = total_teams - 3
        relegation_zone = total_teams - 5
        
        # More nuanced statuses
        if home_pos <= safe_cutoff:
            home_status = 'safe'
        elif home_pos <= relegation_zone:
            home_status = 'mid'
        else:
            home_status = 'danger'
            
        if away_pos <= safe_cutoff:
            away_status = 'safe'
        elif away_pos <= relegation_zone:
            away_status = 'mid'
        else:
            away_status = 'danger'
        
        both_safe = home_status == 'safe' and away_status == 'safe'
        both_danger = home_status == 'danger' and away_status == 'danger'
        
        # 3. Detect team classification
        top_cutoff = 4
        europe_cutoff = 7
        
        if home_pos <= top_cutoff:
            home_class = 'top'
        elif home_pos <= europe_cutoff:
            home_class = 'europe'
        elif home_pos <= safe_cutoff:
            home_class = 'mid'
        elif home_pos <= relegation_zone:
            home_class = 'low_mid'
        else:
            home_class = 'bottom'
            
        if away_pos <= top_cutoff:
            away_class = 'top'
        elif away_pos <= europe_cutoff:
            away_class = 'europe'
        elif away_pos <= safe_cutoff:
            away_class = 'mid'
        elif away_pos <= relegation_zone:
            away_class = 'low_mid'
        else:
            away_class = 'bottom'
        
        # 4. Position gap and form indicators
        position_gap = abs(home_pos - away_pos)
        
        return {
            'season_phase': season_phase,
            'season_progress': season_progress,
            'season_factor': season_factor,
            'home_status': home_status,
            'away_status': away_status,
            'both_safe': both_safe,
            'both_danger': both_danger,
            'home_class': home_class,
            'away_class': away_class,
            'position_gap': position_gap,
            'is_late_season': is_late_season,
            'safe_cutoff': safe_cutoff,
            'danger_cutoff': danger_cutoff,
            'relegation_zone': relegation_zone
        }
    
    def analyze_match(self, match_data, manual_edges):
        # Validate inputs first
        validation_errors = validate_match_data(match_data)
        if validation_errors:
            logger.warning(f"Validation errors in match data: {validation_errors}")
            match_data = self._apply_defaults(match_data)
        
        # Auto-detect context
        auto_context = self.auto_detect_context(match_data)
        match_data['auto_context'] = auto_context
        
        # Detect core pattern
        core_pattern = self._detect_core_pattern_auto(auto_context)
        
        # Detect edge patterns
        edge_conditions = {
            'new_manager': manual_edges.get('new_manager', False),
            'is_derby': manual_edges.get('is_derby', False),
            'european_game': manual_edges.get('european_game', False),
            'late_season': auto_context['is_late_season'],
            'both_safe': auto_context['both_safe']
        }
        
        edge_patterns = []
        for edge_name, condition in edge_conditions.items():
            if condition and edge_name in ['new_manager', 'is_derby', 'european_game']:
                edge_key = {
                    'new_manager': 'new_manager_bounce',
                    'is_derby': 'derby_fear',
                    'european_game': 'european_hangover'
                }[edge_name]
                edge_patterns.append(self.edge_patterns[edge_key])
        
        if edge_conditions['late_season'] and edge_conditions['both_safe']:
            edge_patterns.append(self.edge_patterns['dead_rubber'])
        
        # Calculate base xG
        base_xg = self._calculate_base_xg(match_data)
        
        # Apply pattern multiplier
        pattern_info = self.learned_patterns[core_pattern]
        total_multiplier = pattern_info['base_multiplier']
        
        # Apply edge multipliers
        edge_value = 0
        accuracy_boost = 0
        pattern_bias = pattern_info.get('over_bias', 0) - pattern_info.get('under_bias', 0)
        
        for edge in edge_patterns:
            total_multiplier *= edge['multiplier']
            edge_value += edge['edge_value']
            accuracy_boost += edge.get('accuracy_boost', 0)
            pattern_bias += edge.get('over_bias', 0) - edge.get('under_bias', 0)
        
        enhanced_xg = base_xg * total_multiplier
        
        # Apply season factor
        season_factor = auto_context.get('season_factor', 1.0)
        if auto_context['season_phase'] in ['very_early', 'early']:
            # Less predictable in early season
            enhanced_xg = (enhanced_xg + 2.5) / 2  # Regress toward mean
        
        # Make prediction with dynamic thresholds
        thresholds = self.thresholds.get(core_pattern, self.thresholds['default'])
        
        # Adjust thresholds based on pattern bias
        over_threshold = thresholds['over'] - (pattern_bias * 0.2)
        under_threshold = thresholds['under'] + (pattern_bias * 0.2)
        
        if enhanced_xg > over_threshold:
            prediction = 'OVER 2.5'
            prediction_bias = 'over'
        elif enhanced_xg < under_threshold:
            prediction = 'UNDER 2.5'
            prediction_bias = 'under'
        else:
            # Close call - use bias to decide
            if pattern_bias > 0:
                prediction = 'OVER 2.5'
                prediction_bias = 'over'
            elif pattern_bias < 0:
                prediction = 'UNDER 2.5'
                prediction_bias = 'under'
            else:
                prediction = 'OVER 2.5' if enhanced_xg > 2.5 else 'UNDER 2.5'
                prediction_bias = 'neutral'
        
        # Calculate probability - BALANCED APPROACH
        # Base probability from xG deviation
        if prediction_bias == 'over':
            # For OVER predictions
            xg_deviation = enhanced_xg - 2.5
            base_prob = 0.5 + (xg_deviation * 0.12)  # 0.12 sensitivity
            
            # Adjust based on how far above threshold
            if enhanced_xg > over_threshold + 0.3:
                base_prob += 0.10
            elif enhanced_xg > over_threshold + 0.1:
                base_prob += 0.05
        else:
            # For UNDER predictions
            xg_deviation = 2.5 - enhanced_xg
            base_prob = 0.5 + (xg_deviation * 0.15)  # Slightly more sensitive for UNDER
            
            # Adjust based on how far below threshold
            if enhanced_xg < under_threshold - 0.3:
                base_prob += 0.12
            elif enhanced_xg < under_threshold - 0.1:
                base_prob += 0.06
        
        # Edge pattern boost
        if edge_value > 0.20:
            base_prob += 0.12
        elif edge_value > 0.10:
            base_prob += 0.06
        elif edge_value > 0.05:
            base_prob += 0.03
        
        # Position gap factor
        position_gap = auto_context['position_gap']
        if position_gap > 12:
            base_prob += 0.10
        elif position_gap > 8:
            base_prob += 0.06
        elif position_gap > 4:
            base_prob += 0.03
        
        # Recent form consistency
        home_form = match_data.get('home_goals5', 0) / 5
        away_form = match_data.get('away_goals5', 0) / 5
        home_consistency = 1 - abs(home_form - match_data.get('home_attack', 1.5)) / 2
        away_consistency = 1 - abs(away_form - match_data.get('away_attack', 1.5)) / 2
        
        if home_consistency > 0.8 and away_consistency > 0.8:
            base_prob += 0.06
        elif home_consistency > 0.7 or away_consistency > 0.7:
            base_prob += 0.03
        
        # Season adjustments
        season_phase = auto_context['season_phase']
        if season_phase == 'very_early':
            base_prob *= 0.75
        elif season_phase == 'early':
            base_prob *= 0.85
        elif season_phase == 'very_late':
            base_prob *= 1.05  # Slight boost for very late season
        
        # Pattern accuracy weight
        base_prob *= pattern_info['accuracy_weight']
        
        # Add accuracy boost from edge patterns
        base_prob += accuracy_boost
        
        # Apply caps
        base_prob = min(base_prob, 0.88)  # Max 88%
        base_prob = max(base_prob, 0.42)  # Min 42%
        
        # Map to confidence labels
        if base_prob > 0.75:
            confidence = 'VERY HIGH'
        elif base_prob > 0.65:
            confidence = 'HIGH'
        elif base_prob > 0.55:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        # Kelly Criterion stake recommendation
        stake_recommendation = self.calculate_kelly_stake(
            confidence, edge_value, base_prob, 
            prediction_bias, auto_context['season_phase'],
            enhanced_xg
        )
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'actual_probability': round(base_prob, 3),
            'base_xg': round(base_xg, 2),
            'enhanced_xg': round(enhanced_xg, 2),
            'total_multiplier': round(total_multiplier, 2),
            'core_pattern': core_pattern,
            'edge_patterns': edge_patterns,
            'total_edge_value': round(edge_value, 3),
            'stake_recommendation': stake_recommendation,
            'thresholds_used': {'over': round(over_threshold, 2), 'under': round(under_threshold, 2)},
            'psychology': pattern_info['psychology'],
            'badge': pattern_info['badge'],
            'pattern_accuracy_weight': pattern_info['accuracy_weight'],
            'prediction_bias': prediction_bias,
            'pattern_bias': round(pattern_bias, 3),
            'season_factor': auto_context.get('season_factor', 1.0)
        }, auto_context
    
    def calculate_kelly_stake(self, confidence, edge_value, probability, prediction_bias, season_phase, enhanced_xg):
        """
        Balanced Kelly Criterion calculation for all scenarios
        """
        # Dynamic odds based on confidence and xG
        if prediction_bias == 'over':
            # OVER bets - odds adjust based on xG
            if enhanced_xg > 3.2:
                base_odds = 1.70  # Low odds for high xG
            elif enhanced_xg > 2.8:
                base_odds = 1.80
            elif enhanced_xg > 2.5:
                base_odds = 1.85
            else:
                base_odds = 1.90
        else:
            # UNDER bets - odds adjust based on xG
            if enhanced_xg < 1.8:
                base_odds = 1.70  # Low odds for very low xG
            elif enhanced_xg < 2.2:
                base_odds = 1.80
            elif enhanced_xg < 2.5:
                base_odds = 1.85
            else:
                base_odds = 1.90
        
        # Confidence adjustment to odds
        if confidence == 'VERY HIGH':
            odds = base_odds * 0.95  # Better odds for high confidence
        elif confidence == 'HIGH':
            odds = base_odds * 0.97
        elif confidence == 'MEDIUM':
            odds = base_odds
        else:  # LOW
            odds = base_odds * 1.03  # Worse odds for low confidence
        
        # Edge value adjustment to probability
        p_adj = probability + (edge_value * 0.6)  # Moderate edge impact
        
        # Season phase adjustment
        if season_phase in ['very_early', 'early']:
            p_adj *= 0.9  # Reduce confidence in early season
            odds *= 1.05  # Increase odds (worse value)
        elif season_phase == 'very_late':
            p_adj *= 1.05  # Slight boost in very late season
            odds *= 0.98  # Slightly better odds
        
        # Ensure probability is reasonable
        p_adj = min(p_adj, 0.90)
        p_adj = max(p_adj, 0.40)
        
        # Kelly formula
        b = odds - 1
        q = 1 - p_adj
        expected_value = (b * p_adj - q) * 100
        
        # Calculate Kelly fraction
        if expected_value <= 0:
            return {
                'recommendation': 'NO BET ❌',
                'reason': f'Negative expected value ({expected_value:.1f}%)',
                'kelly_percentage': 0.0,
                'fractional_percentage': 0.0,
                'expected_value': round(expected_value, 1),
                'adjusted_probability': round(p_adj, 3),
                'odds_used': round(odds, 2),
                'quality': 'poor'
            }
        
        f = (b * p_adj - q) / b
        
        # Conservative fractional Kelly with dynamic fraction
        if confidence == 'VERY HIGH' and edge_value > 0.2:
            fraction = 1/3  # More aggressive for high confidence + edge
        elif confidence in ['HIGH', 'VERY HIGH']:
            fraction = 1/4  # Standard conservative
        elif confidence == 'MEDIUM':
            fraction = 1/5  # More conservative
        else:
            fraction = 1/6  # Very conservative for low confidence
        
        f_fractional = f * fraction
        
        # Dynamic caps based on confidence
        if confidence == 'VERY HIGH':
            max_stake = 0.08  # 8% max
        elif confidence == 'HIGH':
            max_stake = 0.06  # 6% max
        elif confidence == 'MEDIUM':
            max_stake = 0.04  # 4% max
        else:
            max_stake = 0.02  # 2% max
        
        f_fractional = min(f_fractional, max_stake)
        
        # Minimum bet for positive EV
        min_stake = 0.005  # 0.5% minimum
        if expected_value > 5:  # Good EV
            f_fractional = max(f_fractional, min_stake)
        
        # Determine stake level
        if f_fractional > 0.05:
            rec_text = f'HIGH BET ({f_fractional*100:.1f}% of bankroll) ⚡'
            quality = 'excellent'
        elif f_fractional > 0.03:
            rec_text = f'MEDIUM BET ({f_fractional*100:.1f}% of bankroll) ✅'
            quality = 'good'
        elif f_fractional > 0.01:
            rec_text = f'SMALL BET ({f_fractional*100:.1f}% of bankroll) ⚖️'
            quality = 'moderate'
        else:
            rec_text = f'MINIMAL BET ({f_fractional*100:.1f}% of bankroll) 📉'
            quality = 'low'
        
        # Reason based on factors
        reasons = []
        if edge_value > 0.15:
            reasons.append(f"strong edge (+{edge_value*100:.0f}%)")
        if confidence in ['HIGH', 'VERY HIGH']:
            reasons.append(f"high confidence")
        if expected_value > 10:
            reasons.append(f"excellent value (+{expected_value:.1f}%)")
        
        reason_text = " + ".join(reasons) if reasons else "positive expected value"
        
        return {
            'recommendation': rec_text,
            'reason': f'Based on {reason_text}',
            'kelly_percentage': round(f, 3),
            'fractional_percentage': round(f_fractional, 3),
            'expected_value': round(expected_value, 1),
            'adjusted_probability': round(p_adj, 3),
            'odds_used': round(odds, 2),
            'quality': quality,
            'full_kelly': round(f * 100, 1),
            'fraction_used': f"1/{int(1/fraction)}"
        }
    
    def _detect_core_pattern_auto(self, auto_context):
        """Enhanced pattern detection"""
        home_class = auto_context['home_class']
        away_class = auto_context['away_class']
        both_safe = auto_context['both_safe']
        both_danger = auto_context['both_danger']
        position_gap = auto_context['position_gap']
        
        # Top vs Bottom patterns
        if (home_class in ['top', 'europe'] and away_class in ['bottom', 'low_mid']):
            if position_gap > 10:
                return 'top_vs_bottom_domination'
            else:
                return 'top_vs_bottom_dominance'
        
        if (away_class in ['top', 'europe'] and home_class in ['bottom', 'low_mid']):
            if position_gap > 10:
                return 'top_vs_bottom_domination'
            else:
                return 'top_vs_bottom_dominance'
        
        # Both in danger zone
        if both_danger:
            return 'relegation_battle'
        
        # Top team battle
        if home_class in ['top', 'europe'] and away_class in ['top', 'europe']:
            return 'top_team_battle'
        
        # Both safe mid-table
        if both_safe and home_class == 'mid' and away_class == 'mid':
            return 'mid_table_ambition'
        
        # Late season dead rubber (detected separately)
        
        # Default
        return 'controlled_mid_clash'
    
    def _calculate_base_xg(self, match_data):
        """Calculate base expected goals with form consideration"""
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        home_goals5 = match_data.get('home_goals5', 7)
        away_goals5 = match_data.get('away_goals5', 6)
        
        # Apply bounds
        home_attack = min(max(home_attack, 0.0), 5.0)
        away_attack = min(max(away_attack, 0.0), 5.0)
        home_defense = min(max(home_defense, 0.0), 5.0)
        away_defense = min(max(away_defense, 0.0), 5.0)
        
        # Recent form adjustment (weighted 30% recent form, 70% season average)
        home_recent = home_goals5 / 5
        away_recent = away_goals5 / 5
        
        home_attack_adj = (home_attack * 0.7) + (home_recent * 0.3)
        away_attack_adj = (away_attack * 0.7) + (away_recent * 0.3)
        
        # Calculate xG
        home_xg = (home_attack_adj + away_defense) / 2
        away_xg = (away_attack_adj + home_defense) / 2
        
        return home_xg + away_xg
    
    def _apply_defaults(self, match_data):
        """Apply default values for invalid inputs"""
        defaults = {
            'home_attack': 1.4,
            'away_attack': 1.3,
            'home_defense': 1.2,
            'away_defense': 1.4,
            'home_goals5': 7,
            'away_goals5': 6,
            'home_pos': 10,
            'away_pos': 10,
            'total_teams': 20,
            'games_played': 25
        }
        
        for key, default in defaults.items():
            if key not in match_data or not isinstance(match_data[key], (int, float)):
                match_data[key] = default
            elif key in ['home_attack', 'away_attack', 'home_defense', 'away_defense']:
                match_data[key] = min(max(match_data[key], 0.0), 5.0)
            elif key in ['home_pos', 'away_pos']:
                match_data[key] = min(max(int(match_data[key]), 1), match_data.get('total_teams', 20))
        
        return match_data

# ========== TEST CASES ==========
TEST_CASES = {
    'Atletico Madrid vs Valencia': {
        'home_name': 'Atletico Madrid',
        'away_name': 'Valencia',
        'home_pos': 4,
        'away_pos': 17,
        'total_teams': 20,
        'games_played': 25,
        'home_attack': 1.8,
        'away_attack': 1.1,
        'home_defense': 0.9,
        'away_defense': 1.4,
        'home_goals5': 12,
        'away_goals5': 5,
        'edge_conditions': {
            'new_manager': True,
            'is_derby': False,
            'european_game': False
        }
    },
    'Liverpool vs Burnley': {
        'home_name': 'Liverpool',
        'away_name': 'Burnley',
        'home_pos': 2,
        'away_pos': 19,
        'total_teams': 20,
        'games_played': 28,
        'home_attack': 2.2,
        'away_attack': 0.9,
        'home_defense': 0.8,
        'away_defense': 1.8,
        'home_goals5': 14,
        'away_goals5': 4,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': True
        }
    },
    'Manchester Derby': {
        'home_name': 'Manchester United',
        'away_name': 'Manchester City',
        'home_pos': 6,
        'away_pos': 3,
        'total_teams': 20,
        'games_played': 30,
        'home_attack': 1.5,
        'away_attack': 2.1,
        'home_defense': 1.3,
        'away_defense': 0.9,
        'home_goals5': 8,
        'away_goals5': 15,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': True,
            'european_game': False
        }
    },
    'Late Season Dead Rubber': {
        'home_name': 'West Ham',
        'away_name': 'Brentford',
        'home_pos': 8,
        'away_pos': 12,
        'total_teams': 20,
        'games_played': 35,
        'home_attack': 1.6,
        'away_attack': 1.5,
        'home_defense': 1.4,
        'away_defense': 1.3,
        'home_goals5': 7,
        'away_goals5': 6,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
        }
    },
    'Brentford vs Leeds (Your Example)': {
        'home_name': 'Brentford',
        'away_name': 'Leeds United',
        'home_pos': 15,
        'away_pos': 16,
        'total_teams': 24,
        'games_played': 20,
        'home_attack': 2.14,
        'away_attack': 0.86,
        'home_defense': 1.14,
        'away_defense': 2.57,
        'home_goals5': 12,
        'away_goals5': 6,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
        }
    },
    'Early Season Test': {
        'home_name': 'Newcastle',
        'away_name': 'Aston Villa',
        'home_pos': 5,
        'away_pos': 8,
        'total_teams': 20,
        'games_played': 3,
        'home_attack': 1.7,
        'away_attack': 1.6,
        'home_defense': 1.2,
        'away_defense': 1.3,
        'home_goals5': 5,
        'away_goals5': 4,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
        }
    },
    'Relegation Battle': {
        'home_name': 'Sheffield Utd',
        'away_name': 'Burnley',
        'home_pos': 19,
        'away_pos': 20,
        'total_teams': 20,
        'games_played': 30,
        'home_attack': 0.9,
        'away_attack': 0.8,
        'home_defense': 2.1,
        'away_defense': 2.3,
        'home_goals5': 4,
        'away_goals5': 3,
        'edge_conditions': {
            'new_manager': True,
            'is_derby': False,
            'european_game': False
        }
    }
}

# ========== INITIALIZE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = BalancedPredictionEngine()
    logger.info("BalancedPredictionEngine initialized")

if 'db' not in st.session_state:
    st.session_state.db = PersistentFootballDatabase()
    logger.info("PersistentFootballDatabase initialized")

# Initialize session state for test case loading
if 'loaded_test_case' not in st.session_state:
    st.session_state.loaded_test_case = None
if 'test_case_data' not in st.session_state:
    st.session_state.test_case_data = TEST_CASES['Brentford vs Leeds (Your Example)']

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">👑 ULTIMATE FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Balanced Engine - Captures All Scenarios**")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## 📊 Performance Dashboard")
        
        perf_stats = st.session_state.db.get_performance_stats()
        
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.metric("Total Predictions", perf_stats['total'])
        with col_sb2:
            accuracy = f"{perf_stats['accuracy']*100:.1f}%" if perf_stats['total'] > 0 else "N/A"
            st.metric("Accuracy", accuracy)
        
        # Recent performance
        if perf_stats['recent_10_total'] > 0:
            st.markdown("### 📈 Recent Performance (Last 10)")
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                st.metric("Recent Total", perf_stats['recent_10_total'])
            with col_rec2:
                recent_acc = f"{perf_stats['recent_10_accuracy']*100:.1f}%"
                st.metric("Recent Accuracy", recent_acc)
        
        # Confidence level accuracies
        if perf_stats['confidence_accuracies']:
            st.markdown("### 🎯 Confidence Performance")
            for conf, acc in perf_stats['confidence_accuracies'].items():
                st.markdown(f"""
                <div class="performance-metric">
                    <strong>{conf}:</strong> {acc*100:.1f}% accuracy
                    <br><small>{sum(1 for p in st.session_state.db.predictions if p.get('analysis', {}).get('confidence') == conf)} predictions</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Recent outcomes
        recent_outcomes = st.session_state.db.get_recent_outcomes(3)
        if recent_outcomes:
            st.markdown("### 📝 Recent Outcomes")
            for outcome in recent_outcomes:
                st.markdown(f"""
                <div class="performance-metric">
                    <strong>{outcome['teams']}</strong><br>
                    Predicted: {outcome['prediction']} ({outcome['confidence']})<br>
                    Actual: {outcome['actual']} - <strong>{outcome['result']}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### 🧪 Quick Test Cases")
        st.markdown("*Click to load team names and data*")
        
        for case_name, case_data in TEST_CASES.items():
            if st.button(case_name, use_container_width=True, key=f"btn_{case_name}"):
                st.session_state.test_case_data = case_data
                st.session_state.loaded_test_case = case_name
                st.rerun()
        
        # Reset button
        if st.button("🔄 Reset All Inputs", type="secondary", use_container_width=True, key="reset_btn"):
            for key in list(st.session_state.keys()):
                if key.endswith('_input'):
                    del st.session_state[key]
            st.session_state.loaded_test_case = None
            st.session_state.test_case_data = TEST_CASES['Brentford vs Leeds (Your Example)']
            st.rerun()
    
    # ===== MAIN INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 TEAM DATA INPUT")
    
    if st.session_state.loaded_test_case:
        st.success(f"✅ **Loaded:** {st.session_state.loaded_test_case}")
    
    current_data = st.session_state.test_case_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 HOME TEAM")
        home_name = st.text_input("Team Name", 
                                 value=current_data['home_name'],
                                 key="home_name_input")
        
        home_pos = st.number_input("League Position (1 = Best)", 
                                  min_value=1, max_value=40,
                                  value=current_data['home_pos'],
                                  key="home_pos_input")
        
        home_attack = st.number_input("Attack: Goals per Game", 
                                     min_value=0.0, max_value=5.0, step=0.1,
                                     value=current_data['home_attack'],
                                     key="home_attack_input")
        
        home_defense = st.number_input("Defense: Conceded per Game", 
                                      min_value=0.0, max_value=5.0, step=0.1,
                                      value=current_data['home_defense'],
                                      key="home_defense_input")
        
        home_goals5 = st.number_input("Goals in Last 5 Games", 
                                     min_value=0, max_value=30,
                                     value=current_data['home_goals5'],
                                     key="home_goals5_input")
    
    with col2:
        st.markdown("#### ✈️ AWAY TEAM")
        away_name = st.text_input("Team Name", 
                                 value=current_data['away_name'],
                                 key="away_name_input")
        
        away_pos = st.number_input("League Position (1 = Best)", 
                                  min_value=1, max_value=40,
                                  value=current_data['away_pos'],
                                  key="away_pos_input")
        
        away_attack = st.number_input("Attack: Goals per Game", 
                                     min_value=0.0, max_value=5.0, step=0.1,
                                     value=current_data['away_attack'],
                                     key="away_attack_input")
        
        away_defense = st.number_input("Defense: Conceded per Game", 
                                      min_value=0.0, max_value=5.0, step=0.1,
                                      value=current_data['away_defense'],
                                     key="away_defense_input")
        
        away_goals5 = st.number_input("Goals in Last 5 Games", 
                                     min_value=0, max_value=30,
                                     value=current_data['away_goals5'],
                                     key="away_goals5_input")
    
    # League settings
    st.markdown("#### ⚙️ LEAGUE SETTINGS")
    col3, col4 = st.columns(2)
    
    with col3:
        total_teams = st.number_input("Total Teams in League", 
                                     min_value=10, max_value=40,
                                     value=current_data['total_teams'],
                                     key="total_teams_input")
    
    with col4:
        games_played = st.number_input("Games Played This Season", 
                                      min_value=1, max_value=50,
                                      value=current_data['games_played'],
                                      key="games_played_input")
    
    # Validation
    match_data_temp = {
        'home_pos': home_pos,
        'away_pos': away_pos,
        'total_teams': total_teams,
        'home_attack': home_attack,
        'away_attack': away_attack,
        'home_defense': home_defense,
        'away_defense': away_defense,
        'home_goals5': home_goals5,
        'away_goals5': away_goals5
    }
    
    validation_errors = validate_match_data(match_data_temp)
    league_errors = validate_league_settings(total_teams, games_played)
    all_errors = validation_errors + league_errors
    
    if all_errors:
        st.markdown('<div class="validation-error">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Validation Errors")
        for error in all_errors:
            st.markdown(f"• {error}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== AUTO-DETECTION DISPLAY =====
    st.markdown("### 🔍 AUTO-DETECTION SYSTEM")
    
    # Run auto-detection for display
    match_data_temp['total_teams'] = total_teams
    match_data_temp['games_played'] = games_played
    
    auto_context = st.session_state.engine.auto_detect_context(match_data_temp)
    
    col_auto1, col_auto2, col_auto3 = st.columns(3)
    
    with col_auto1:
        # Season phase
        progress = auto_context['season_progress']
        phase = auto_context['season_phase'].replace('_', ' ').title()
        phase_class = f"season-{auto_context['season_phase'].split('_')[-1]}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>📅 SEASON PHASE</h4>
            <p>Progress: <span style="font-size: 1.2em;"><strong>{progress:.1f}%</strong></span></p>
            <p>Phase: <span class="{phase_class}">{phase}</span></p>
            <p>Factor: <strong>{auto_context.get('season_factor', 1.0):.2f}x</strong></p>
            <small>Games: {games_played}/{total_teams * 2}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto2:
        # Team safety
        home_status = auto_context['home_status']
        away_status = auto_context['away_status']
        
        status_class_home = f"status-{home_status}"
        status_class_away = f"status-{away_status}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🛡️ TEAM SAFETY</h4>
            <p><strong>{home_name}:</strong> 
            <span class="{status_class_home}">{home_status.upper()}</span></p>
            <p><strong>{away_name}:</strong> 
            <span class="{status_class_away}">{away_status.upper()}</span></p>
            <p><strong>Both Safe:</strong> {'✓ YES' if auto_context['both_safe'] else '✗ NO'}</p>
            <p><strong>Both Danger:</strong> {'✓ YES' if auto_context['both_danger'] else '✗ NO'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto3:
        # Team classification
        home_class = auto_context['home_class'].replace('_', ' ').title()
        away_class = auto_context['away_class'].replace('_', ' ').title()
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🏆 TEAM CLASS</h4>
            <p><strong>{home_name}:</strong> {home_class}</p>
            <p><strong>{away_name}:</strong> {away_class}</p>
            <p><strong>Position Gap:</strong> {auto_context['position_gap']}</p>
            <p><strong>Late Season:</strong> {'✓ YES' if auto_context['is_late_season'] else '✗ NO'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== EDGE PATTERN CONDITIONS =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 EDGE PATTERN CONDITIONS")
    
    edge_data = current_data['edge_conditions']
    
    col_edge1, col_edge2 = st.columns(2)
    
    with col_edge1:
        new_manager = st.checkbox("New Manager Effect", 
                                 value=edge_data['new_manager'],
                                 key="new_manager_input")
        
        is_derby = st.checkbox("Local Derby Match", 
                              value=edge_data['is_derby'],
                              key="is_derby_input")
    
    with col_edge2:
        european_game = st.checkbox("European Game Midweek", 
                                   value=edge_data['european_game'],
                                   key="european_game_input")
        
        # Show season phase info
        season_phase = auto_context['season_phase'].replace('_', ' ').title()
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
            <strong>📅 Season Context</strong>
            <p style="margin: 5px 0;">Phase: <strong>{season_phase}</strong></p>
            <p>Progress: {auto_context['season_progress']:.1f}%</p>
            <p>Factor: {auto_context.get('season_factor', 1.0):.2f}x</p>
            <small>Affects predictability and odds</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Team status summary
    both_safe_detected = auto_context['both_safe']
    both_danger_detected = auto_context['both_danger']
    
    status_color = "#4CAF50" if both_safe_detected else "#F44336" if both_danger_detected else "#FF9800"
    status_text = "BOTH SAFE" if both_safe_detected else "BOTH IN DANGER" if both_danger_detected else "MIXED STATUS"
    
    st.markdown(f"""
    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 4px solid {status_color};">
        <strong>🛡️ Team Status Summary</strong>
        <p style="margin: 5px 0;">
        <strong>{status_text}</strong>
        </p>
        <p>{home_name}: {auto_context['home_class'].replace('_', ' ').title()} (pos {home_pos})</p>
        <p>{away_name}: {auto_context['away_class'].replace('_', ' ').title()} (pos {away_pos})</p>
        <small>Position gap: {auto_context['position_gap']} | Late season: {'Yes' if auto_context['is_late_season'] else 'No'}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYZE BUTTON =====
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        analyze_disabled = len(all_errors) > 0
        
        if analyze_disabled:
            st.warning("⚠️ Fix validation errors before analysis")
        
        if st.button("🚀 RUN BALANCED ANALYSIS", 
                    type="primary", 
                    use_container_width=True,
                    disabled=analyze_disabled):
            try:
                # Prepare match data
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
                
                # Manual edge conditions
                manual_edges = {
                    'new_manager': new_manager,
                    'is_derby': is_derby,
                    'european_game': european_game
                }
                
                # Run analysis
                analysis, auto_context = st.session_state.engine.analyze_match(match_data, manual_edges)
                
                # Save to database
                prediction_data = {
                    'match_data': match_data,
                    'analysis': analysis,
                    'auto_detections': auto_context
                }
                
                prediction_hash = st.session_state.db.save_prediction(prediction_data)
                
                # Store in session
                st.session_state.current_prediction = {
                    'analysis': analysis,
                    'match_data': match_data,
                    'auto_context': auto_context,
                    'prediction_hash': prediction_hash,
                    'teams': f"{home_name} vs {away_name}"
                }
                
                st.rerun()
                
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                st.error(f"Analysis error: {str(e)}")
                st.error("Check logs for details")
    
    # ===== RESULTS DISPLAY =====
    if 'current_prediction' in st.session_state:
        pred_data = st.session_state.current_prediction
        analysis = pred_data['analysis']
        match_data = pred_data['match_data']
        auto_context = pred_data.get('auto_context', {})
        
        st.markdown("---")
        st.markdown(f"## 📊 BALANCED RESULTS: {pred_data['teams']}")
        
        # Show auto-detection summary
        st.markdown("### 🔍 CONTEXT ANALYSIS")
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            season_phase = auto_context.get('season_phase', 'mid').replace('_', ' ').title()
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>📅 Season & Context</h4>
                <p><strong>Phase:</strong> {season_phase}</p>
                <p><strong>Progress:</strong> {auto_context.get('season_progress', 0):.1f}%</p>
                <p><strong>Factor:</strong> {auto_context.get('season_factor', 1.0):.2f}x</p>
                <p><strong>Games:</strong> {match_data['games_played']} / {match_data['total_teams'] * 2}</p>
                <p><strong>Predictability:</strong> {'High' if auto_context.get('season_factor', 1.0) > 1.0 else 'Medium' if auto_context.get('season_factor', 1.0) == 1.0 else 'Lower'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_sum2:
            home_class = auto_context.get('home_class', 'mid').replace('_', ' ').title()
            away_class = auto_context.get('away_class', 'mid').replace('_', ' ').title()
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>🏆 Team Analysis</h4>
                <p><strong>{match_data['home_name']}:</strong> {home_class} (pos {match_data['home_pos']})</p>
                <p><strong>{match_data['away_name']}:</strong> {away_class} (pos {match_data['away_pos']})</p>
                <p><strong>Position Gap:</strong> {auto_context.get('position_gap', 0)}</p>
                <p><strong>Match Type:</strong> {analysis['core_pattern'].replace('_', ' ').title()}</p>
                <p><strong>Psychology:</strong> {analysis['psychology']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Team info cards with form analysis
        col_team1, col_team2 = st.columns(2)
        
        with col_team1:
            home_avg_last5 = match_data['home_goals5'] / 5
            form_consistency = 1 - abs(home_avg_last5 - match_data['home_attack']) / 2
            form_status = "👍 Consistent" if form_consistency > 0.7 else "⚠️ Inconsistent" if form_consistency > 0.5 else "❌ Volatile"
            
            st.markdown(f"""
            <div class="team-card">
                <h3>🏠 {match_data['home_name']}</h3>
                <p><strong>Position:</strong> {match_data['home_pos']} ({auto_context.get('home_class', 'mid').replace('_', ' ').title()})</p>
                <p><strong>Attack:</strong> {match_data['home_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['home_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['home_goals5']} goals in last 5 ({home_avg_last5:.1f}/game)</p>
                <p><strong>Form Status:</strong> {form_status} ({form_consistency:.0%})</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_team2:
            away_avg_last5 = match_data['away_goals5'] / 5
            form_consistency = 1 - abs(away_avg_last5 - match_data['away_attack']) / 2
            form_status = "👍 Consistent" if form_consistency > 0.7 else "⚠️ Inconsistent" if form_consistency > 0.5 else "❌ Volatile"
            
            st.markdown(f"""
            <div class="team-card">
                <h3>✈️ {match_data['away_name']}</h3>
                <p><strong>Position:</strong> {match_data['away_pos']} ({auto_context.get('away_class', 'mid').replace('_', ' ').title()})</p>
                <p><strong>Attack:</strong> {match_data['away_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['away_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['away_goals5']} goals in last 5 ({away_avg_last5:.1f}/game)</p>
                <p><strong>Form Status:</strong> {form_status} ({form_consistency:.0%})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key prediction metrics
        st.markdown("### 🎯 PREDICTION SUMMARY")
        
        col_metrics = st.columns(5)
        
        with col_metrics[0]:
            st.metric("Prediction", analysis['prediction'])
        with col_metrics[1]:
            st.metric("Confidence", analysis['confidence'])
        with col_metrics[2]:
            st.metric("Probability", f"{analysis['actual_probability']*100:.1f}%")
        with col_metrics[3]:
            st.metric("Expected Goals", analysis['enhanced_xg'])
        with col_metrics[4]:
            stake_info = analysis['stake_recommendation']
            if isinstance(stake_info, dict):
                st.metric("Stake", stake_info['recommendation'])
            else:
                st.metric("Stake", stake_info)
        
        # Psychology badge and pattern info
        st.markdown(f"""
        <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 10px; border: 1px solid #e0e0e0;">
            <span class="psychology-badge {analysis['badge']}">
                {analysis['psychology']} PSYCHOLOGY
            </span>
            <div style="margin-top: 10px;">
                <strong>Pattern:</strong> {analysis['core_pattern'].replace('_', ' ').title()}
                <br><strong>Accuracy Weight:</strong> {analysis['pattern_accuracy_weight']}
                <br><strong>Pattern Bias:</strong> {analysis['pattern_bias']}
                <br><strong>Prediction Bias:</strong> {analysis['prediction_bias'].upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kelly Criterion details
        if isinstance(analysis['stake_recommendation'], dict):
            stake_info = analysis['stake_recommendation']
            
            if stake_info['recommendation'] == 'NO BET ❌':
                st.markdown(f"""
                <div class="no-bet">
                    <h4>💰 BETTING ANALYSIS</h4>
                    <p><strong>Recommendation:</strong> {stake_info['recommendation']}</p>
                    <p><strong>Reason:</strong> {stake_info['reason']}</p>
                    <p><strong>Adjusted Probability:</strong> {stake_info.get('adjusted_probability', 0)*100:.1f}%</p>
                    <p><strong>Market Odds:</strong> {stake_info.get('odds_used', 0):.2f}</p>
                    <p><strong>Expected Value:</strong> {stake_info.get('expected_value', 0):.1f}%</p>
                    <p class="bet-reason">No positive expected value found. Wait for better opportunities.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="kelly-bet">
                    <h4>💰 KELLY CRITERION ANALYSIS</h4>
                    <p><strong>Recommendation:</strong> {stake_info['recommendation']}</p>
                    <p><strong>Reason:</strong> {stake_info['reason']}</p>
                    <p><strong>Full Kelly:</strong> {stake_info.get('full_kelly', 0):.1f}% of bankroll</p>
                    <p><strong>Fraction Used:</strong> {stake_info.get('fraction_used', '1/4')} Kelly</p>
                    <p><strong>Your Stake:</strong> {stake_info.get('fractional_percentage', 0)*100:.1f}% of bankroll</p>
                    <p><strong>Adjusted Probability:</strong> {stake_info.get('adjusted_probability', 0)*100:.1f}%</p>
                    <p><strong>Market Odds:</strong> {stake_info.get('odds_used', 0):.2f}</p>
                    <p><strong>Expected Value:</strong> +{stake_info.get('expected_value', 0):.1f}% per bet</p>
                    <p><strong>Bet Quality:</strong> {stake_info.get('quality', 'moderate').upper()}</p>
                    <p class="bet-reason">Based on probability {stake_info.get('adjusted_probability', 0)*100:.1f}% vs market odds {stake_info.get('odds_used', 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Edge patterns detected
        if analysis['edge_patterns']:
            st.markdown("### ⚡ EDGE PATTERNS DETECTED")
            
            for edge in analysis['edge_patterns']:
                edge_value = edge['edge_value']
                if edge_value > 0.20:
                    edge_class = "edge-high"
                elif edge_value > 0.12:
                    edge_class = "edge-medium"
                else:
                    edge_class = "edge-low"
                
                st.markdown(f"""
                <div class="edge-card {edge_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{edge['description']}</strong>
                            <span class="pattern-badge">+{edge_value*100:.0f}% EDGE</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Bet Type: {edge['bet_type'].replace('_', ' ')}
                        </div>
                    </div>
                    <p style="margin: 10px 0 5px 0;">
                    Multiplier: ×{edge['multiplier']:.2f} | 
                    Accuracy Boost: +{edge.get('accuracy_boost', 0)*100:.1f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # xG visualization
        st.markdown("### 📈 EXPECTED GOALS BREAKDOWN")
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            fig = go.Figure()
            
            stages = ['Base xG', 'Pattern Adjustments', 'Final xG']
            values = [
                analysis['base_xg'],
                analysis['base_xg'] * analysis['total_multiplier'],
                analysis['enhanced_xg']
            ]
            
            fig.add_trace(go.Bar(
                x=stages,
                y=values,
                marker_color=['#FF6B6B', '#4ECDC4', '#96CEB4'],
                text=[f'{v:.2f}' for v in values],
                textposition='auto'
            ))
            
            fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig.update_layout(
                height=350,
                showlegend=False,
                yaxis_title="Expected Goals",
                title="xG Calculation Process"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_viz2:
            # Detailed analysis
            season_phase = auto_context.get('season_phase', 'mid').replace('_', ' ').title()
            season_warning = ""
            
            if auto_context.get('season_phase') in ['very_early', 'early']:
                season_warning = "⚠️ **Early Season Caution:** Results are less predictable early in the season. "
                season_warning += f"Confidence reduced by {int((1-auto_context.get('season_factor', 1.0))*100)}%."
            
            st.markdown(f"""
            #### 🔍 DETAILED ANALYSIS
            
            **Match Context:**
            - Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
            - Season: {season_phase} ({auto_context.get('season_progress', 0):.1f}%)
            - Position Gap: {auto_context.get('position_gap', 0)}
            
            **Decision Framework:**
            - Base xG: {analysis['base_xg']:.2f}
            - Pattern Multiplier: ×{analysis['total_multiplier']:.2f}
            - Season Factor: {auto_context.get('season_factor', 1.0):.2f}x
            - Final xG: **{analysis['enhanced_xg']:.2f}**
            
            **Prediction Logic:**
            - OVER if > {analysis['thresholds_used']['over']:.2f}
            - UNDER if < {analysis['thresholds_used']['under']:.2f}
            - Actual: {analysis['enhanced_xg']:.2f} → **{analysis['prediction']}**
            
            **Probability Assessment:**
            - Base Probability: {analysis['actual_probability']*100:.1f}%
            - Edge Value: +{analysis['total_edge_value']*100:.0f}%
            - Pattern Weight: {analysis['pattern_accuracy_weight']:.2f}x
            - Confidence: {analysis['confidence']}
            
            {season_warning}
            """)
        
        # Profit simulation
        if isinstance(analysis['stake_recommendation'], dict):
            stake_info = analysis['stake_recommendation']
            if stake_info['recommendation'] != 'NO BET ❌':
                kelly_pct = stake_info.get('fractional_percentage', 0.0)
                expected_value = stake_info.get('expected_value', 0.0)
                
                if kelly_pct > 0 and expected_value > 0:
                    st.markdown('<div class="profit-highlight">', unsafe_allow_html=True)
                    st.markdown(f"""
                    ### 💰 PROFIT POTENTIAL ANALYSIS
                    
                    **Match:** {match_data['home_name']} vs {match_data['away_name']}
                    **Prediction:** {analysis['prediction']} ({analysis['confidence']} confidence)
                    **Probability:** {analysis['actual_probability']*100:.1f}%
                    **Recommended Stake:** {kelly_pct*100:.1f}% of bankroll
                    **Expected Value:** +{expected_value:.1f}% per bet
                    **Bet Quality:** {stake_info.get('quality', 'moderate').upper()}
                    
                    *Assuming $10,000 bankroll:*
                    - Stake this match: **${kelly_pct*10000:.0f}**
                    - Expected profit: **+${kelly_pct*10000 * expected_value/100:.0f}**
                    - Weekly (5 similar bets): **+${kelly_pct*10000 * 5 * expected_value/100:.0f}**
                    - Monthly (20 similar bets): **+${kelly_pct*10000 * 20 * expected_value/100:.0f}**
                    
                    *Risk Management:*
                    - Max drawdown (5 losses): ${kelly_pct*10000 * 5:.0f}
                    - Recovery needed: {((1/(1-kelly_pct*5))-1)*100:.1f}% win rate
                    
                    <small>*Note: Theoretical values. Real results vary. Never risk more than 10% of bankroll.*</small>
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Outcome recording
        st.markdown("---")
        st.markdown("### 📝 RECORD ACTUAL OUTCOME")
        
        col_out1, col_out2, col_out3 = st.columns(3)
        
        with col_out1:
            actual_home = st.number_input(f"{match_data['home_name']} Goals", 
                                        0, 10, 0, key="actual_home_input")
        
        with col_out2:
            actual_away = st.number_input(f"{match_data['away_name']} Goals", 
                                        0, 10, 0, key="actual_away_input")
        
        with col_out3:
            notes = st.text_input("Match Notes", key="outcome_notes_input")
        
        if st.button("✅ SAVE ACTUAL RESULT", type="secondary", key="save_result_btn"):
            if actual_home == 0 and actual_away == 0:
                st.warning("Please enter actual scores (at least one goal)")
            else:
                success = st.session_state.db.record_outcome(
                    pred_data['prediction_hash'],
                    actual_home,
                    actual_away,
                    notes
                )
                
                if success:
                    st.success("✅ Result saved! System learning updated.")
                    
                    # Show learning feedback
                    actual_total = actual_home + actual_away
                    predicted = analysis['prediction']
                    actual_type = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
                    is_correct = predicted == actual_type
                    
                    st.info(f"""
                    **Learning Update:**
                    - Predicted: **{predicted}** ({analysis['confidence']}, {analysis['actual_probability']*100:.1f}%)
                    - Actual: **{actual_type}** ({actual_home}-{actual_away})
                    - Result: **{'✅ CORRECT' if is_correct else '❌ INCORRECT'}**
                    - Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
                    - Season: {auto_context.get('season_phase', 'mid').replace('_', ' ').title()}
                    - Edge Patterns: {len(analysis['edge_patterns'])} detected
                    - Auto-detections recorded for future learning
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to save result")

if __name__ == "__main__":
    main()