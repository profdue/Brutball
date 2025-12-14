import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import logging

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
class EnhancedPredictionEngine:
    def __init__(self):
        self.learned_patterns = {
            'top_vs_bottom_domination': {
                'base_multiplier': 1.05,
                'description': 'Top team good form vs bottom team → 2-1 type scores',
                'psychology': 'DOMINATION',
                'badge': 'badge-domination',
                'accuracy_weight': 1.1
            },
            'relegation_battle': {
                'base_multiplier': 0.65,
                'description': 'Both fighting relegation → defensive football',
                'psychology': 'FEAR',
                'badge': 'badge-fear',
                'accuracy_weight': 0.9
            },
            'mid_table_ambition': {
                'base_multiplier': 1.15,
                'description': 'Both safe mid-table → attacking football',
                'psychology': 'AMBITION',
                'badge': 'badge-ambition',
                'accuracy_weight': 1.05
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.90,
                'description': 'Mid-table with form difference → controlled game',
                'psychology': 'CONTROL',
                'badge': 'badge-control',
                'accuracy_weight': 1.0
            },
            'top_team_battle': {
                'base_multiplier': 0.95,
                'description': 'Top teams facing → quality creates and prevents goals',
                'psychology': 'QUALITY',
                'badge': 'badge-quality',
                'accuracy_weight': 0.95
            },
            'top_vs_bottom_dominance': {
                'base_multiplier': 0.85,
                'description': 'Top team excellent form vs very poor bottom → 1-0 type',
                'psychology': 'DOMINANCE',
                'badge': 'badge-dominance',
                'accuracy_weight': 1.08
            }
        }
        
        self.edge_patterns = {
            'new_manager_bounce': {
                'multiplier': 1.25,
                'edge_value': 0.20,
                'description': 'Players desperate to impress new manager',
                'bet_type': 'HOME_WIN',
                'accuracy_boost': 0.05
            },
            'derby_fear': {
                'multiplier': 0.60,
                'edge_value': 0.30,
                'description': 'Fear of losing derby > desire to win',
                'bet_type': 'UNDER_2_0',
                'accuracy_boost': 0.08
            },
            'european_hangover': {
                'multiplier': 0.75,
                'edge_value': 0.28,
                'description': 'Physical/mental exhaustion from European travel',
                'bet_type': 'OPPONENT_DOUBLE_CHANCE',
                'accuracy_boost': 0.06
            },
            'dead_rubber': {
                'multiplier': 1.30,
                'edge_value': 0.25,
                'description': 'Beach football mentality, relaxed play',
                'bet_type': 'OVER_2_5',
                'accuracy_boost': 0.07
            }
        }
        
        self.thresholds = {
            'relegation_battle': {'over': 2.3, 'under': 2.7},
            'top_vs_bottom_domination': {'over': 2.6, 'under': 2.4},
            'dead_rubber': {'over': 2.4, 'under': 2.6},
            'derby_fear': {'over': 2.8, 'under': 2.2},
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
        total_games_season = total_teams * 2  # Double round-robin
        season_progress = (games_played / total_games_season) * 100
        
        # EARLY SEASON ADJUSTMENT (first 8 games)
        early_season = games_played < 8
        if season_progress <= 33.33 or early_season:
            season_phase = 'early'
            is_late_season = False
            early_season_adj = 0.7  # Reduce position confidence by 30%
        elif season_progress <= 66.66:
            season_phase = 'mid'
            is_late_season = False
            early_season_adj = 1.0
        else:
            season_phase = 'late'
            is_late_season = True
            early_season_adj = 1.0
        
        # 2. Calculate team safety zones with early season adjustment
        safe_cutoff = int(total_teams * 0.7)  # Top 70% safe
        danger_cutoff = total_teams - 3  # Bottom 3 always danger
        
        # Adjust for early season uncertainty
        if early_season:
            home_status = 'uncertain'
            away_status = 'uncertain'
            both_safe = False
        else:
            home_status = 'safe' if home_pos <= safe_cutoff else 'danger'
            away_status = 'safe' if away_pos <= safe_cutoff else 'danger'
            both_safe = home_pos < danger_cutoff and away_pos < danger_cutoff
        
        # 3. Detect top/bottom classification with early season adjustment
        top_cutoff = 4  # Top 4 considered elite
        bottom_cutoff = total_teams - 5  # Bottom 5 considered poor
        
        if early_season:
            # Default to mid in early season due to uncertainty
            home_class = 'mid'
            away_class = 'mid'
        else:
            home_class = 'top' if home_pos <= top_cutoff else 'mid' if home_pos <= safe_cutoff else 'bottom'
            away_class = 'top' if away_pos <= top_cutoff else 'mid' if away_pos <= safe_cutoff else 'bottom'
        
        # 4. Position gap for pattern detection
        position_gap = abs(home_pos - away_pos)
        
        return {
            'season_phase': season_phase,
            'season_progress': season_progress,
            'home_status': home_status,
            'away_status': away_status,
            'both_safe': both_safe,
            'home_class': home_class,
            'away_class': away_class,
            'position_gap': position_gap,
            'is_late_season': is_late_season,
            'is_early_season': early_season,
            'early_season_adjustment': early_season_adj,
            'safe_cutoff': safe_cutoff,
            'danger_cutoff': danger_cutoff,
            'top_cutoff': top_cutoff,
            'bottom_cutoff': bottom_cutoff
        }
    
    def analyze_match(self, match_data, manual_edges):
        # Validate inputs first
        validation_errors = validate_match_data(match_data)
        if validation_errors:
            logger.warning(f"Validation errors in match data: {validation_errors}")
            # Use defaults for invalid values
            match_data = self._apply_defaults(match_data)
        
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        total_teams = match_data.get('total_teams', 20)
        
        # Auto-detect context once and cache it
        auto_context = self.auto_detect_context(match_data)
        match_data['auto_context'] = auto_context  # Cache for reuse
        
        # Use auto-detected values, override with manual only if provided
        edge_conditions = {
            'new_manager': manual_edges.get('new_manager', False),
            'is_derby': manual_edges.get('is_derby', False),
            'european_game': manual_edges.get('european_game', False),
            'late_season': auto_context['is_late_season'],
            'both_safe': auto_context['both_safe']
        }
        
        # Detect core pattern using auto-context
        core_pattern = self._detect_core_pattern_auto(auto_context, home_pos, away_pos, total_teams)
        
        # Detect edge patterns
        edge_patterns = []
        if edge_conditions.get('new_manager'):
            edge_patterns.append(self.edge_patterns['new_manager_bounce'])
        if edge_conditions.get('is_derby'):
            edge_patterns.append(self.edge_patterns['derby_fear'])
        if edge_conditions.get('european_game'):
            edge_patterns.append(self.edge_patterns['european_hangover'])
        if edge_conditions.get('late_season') and edge_conditions.get('both_safe'):
            edge_patterns.append(self.edge_patterns['dead_rubber'])
        
        # Calculate xG
        base_xg = self._calculate_base_xg(match_data)
        
        # Apply multipliers
        total_multiplier = self.learned_patterns[core_pattern]['base_multiplier']
        edge_value = 0
        accuracy_boost = 0
        
        for edge in edge_patterns:
            total_multiplier *= edge['multiplier']
            edge_value += edge['edge_value']
            accuracy_boost += edge.get('accuracy_boost', 0)
        
        enhanced_xg = base_xg * total_multiplier
        
        # Make prediction
        thresholds = self.thresholds.get(core_pattern, self.thresholds['default'])
        
        if enhanced_xg > thresholds['over']:
            prediction = 'OVER 2.5'
        elif enhanced_xg < thresholds['under']:
            prediction = 'UNDER 2.5'
        else:
            prediction = 'OVER 2.5' if enhanced_xg > 2.5 else 'UNDER 2.5'
        
        # ENHANCED CONFIDENCE CALCULATION WITH ACTUAL PROBABILITY
        base_confidence_score = 0.5  # Start at 50%
        
        # Add factors
        if edge_value > 0.25:
            base_confidence_score += 0.25
        elif edge_value > 0.15:
            base_confidence_score += 0.15
        
        # Position gap factor
        position_gap = auto_context['position_gap']
        if position_gap > 10:
            base_confidence_score += 0.15
        elif position_gap > 5:
            base_confidence_score += 0.08
        
        # Recent form consistency factor
        home_form_var = abs(match_data.get('home_goals5', 0) / 5 - match_data.get('home_attack', 1.5))
        away_form_var = abs(match_data.get('away_goals5', 0) / 5 - match_data.get('away_attack', 1.5))
        if home_form_var < 0.3 and away_form_var < 0.3:
            base_confidence_score += 0.10
        
        # Early season adjustment
        if auto_context['is_early_season']:
            base_confidence_score *= 0.8  # Reduce confidence by 20% in early season
        
        # Add accuracy boost from edge patterns
        base_confidence_score += accuracy_boost
        
        # Cap at 0.85 (85%) - never 100% certain in football
        base_confidence_score = min(base_confidence_score, 0.85)
        base_confidence_score = max(base_confidence_score, 0.35)  # Minimum 35%
        
        # Map to confidence labels
        if base_confidence_score > 0.75:
            confidence = 'VERY HIGH'
        elif base_confidence_score > 0.65:
            confidence = 'HIGH'
        elif base_confidence_score > 0.55:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        # Kelly Criterion stake recommendation
        stake_recommendation = self.calculate_kelly_stake(
            confidence, edge_value, 
            base_confidence_score, 
            auto_context['is_early_season']
        )
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'actual_probability': round(base_confidence_score, 3),
            'base_xg': round(base_xg, 2),
            'enhanced_xg': round(enhanced_xg, 2),
            'total_multiplier': round(total_multiplier, 2),
            'core_pattern': core_pattern,
            'edge_patterns': edge_patterns,
            'total_edge_value': round(edge_value, 3),
            'stake_recommendation': stake_recommendation,
            'thresholds_used': thresholds,
            'psychology': self.learned_patterns[core_pattern]['psychology'],
            'badge': self.learned_patterns[core_pattern]['badge'],
            'pattern_accuracy_weight': self.learned_patterns[core_pattern]['accuracy_weight']
        }, auto_context
    
    def calculate_kelly_stake(self, confidence, edge_value, probability, is_early_season=False):
        """
        Calculate optimal stake using Kelly Criterion
        """
        # Base odds (decimal)
        if confidence == 'VERY HIGH':
            odds = 1.75
            p = probability
        elif confidence == 'HIGH':
            odds = 1.83
            p = probability
        elif confidence == 'MEDIUM':
            odds = 1.91
            p = probability
        else:
            odds = 2.00
            p = probability
        
        # Adjust probability with edge value
        p_adj = min(0.85, p + edge_value * 0.5)
        
        # Reduce probability in early season
        if is_early_season:
            p_adj *= 0.9
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds - 1, q = 1 - p
        b = odds - 1
        q = 1 - p_adj
        
        if b * p_adj - q <= 0:
            return {
                'recommendation': 'NO BET ❌',
                'reason': 'Negative expected value',
                'kelly_percentage': 0.0,
                'fractional_percentage': 0.0,
                'expected_value': 0.0  # Added this key
            }
        
        f = (b * p_adj - q) / b
        
        # Conservative fractional Kelly (1/4 for safety)
        f_fractional = f / 4
        
        # Cap at 10% of bankroll
        f_fractional = min(f_fractional, 0.10)
        
        if f_fractional > 0.075:
            rec_text = f'HIGH BET ({f_fractional*100:.1f}% of bankroll) ⚡'
        elif f_fractional > 0.04:
            rec_text = f'MEDIUM BET ({f_fractional*100:.1f}% of bankroll) ✅'
        elif f_fractional > 0.01:
            rec_text = f'SMALL BET ({f_fractional*100:.1f}% of bankroll) ⚖️'
        else:
            rec_text = 'MINIMAL BET (≤1%) 📉'
        
        # Calculate expected value
        expected_value = (b * p_adj - q) * 100
        
        return {
            'recommendation': rec_text,
            'reason': f'Kelly Criterion suggests {f*100:.1f}%, using 1/4 Kelly for safety',
            'kelly_percentage': round(f, 3),
            'fractional_percentage': round(f_fractional, 3),
            'expected_value': round(expected_value, 1)  # This key was missing!
        }
    
    def _detect_core_pattern_auto(self, auto_context, home_pos, away_pos, total_teams):
        """Enhanced pattern detection with early season handling"""
        if auto_context['is_early_season']:
            # Default to controlled mid clash in early season due to uncertainty
            return 'controlled_mid_clash'
        
        home_class = auto_context['home_class']
        away_class = auto_context['away_class']
        position_gap = auto_context['position_gap']
        both_safe = auto_context['both_safe']
        
        # Top vs Bottom patterns
        if (home_class == 'top' and away_class == 'bottom') or (away_class == 'top' and home_class == 'bottom'):
            if position_gap > 8:
                return 'top_vs_bottom_domination'
            else:
                return 'top_vs_bottom_dominance'
        
        # Both in danger zone (relegation battle)
        if home_class == 'bottom' and away_class == 'bottom':
            return 'relegation_battle'
        
        # Top team battle
        if home_class == 'top' and away_class == 'top':
            return 'top_team_battle'
        
        # Both safe mid-table
        if both_safe and home_class == 'mid' and away_class == 'mid':
            return 'mid_table_ambition'
        
        # Default - controlled mid-table clash
        return 'controlled_mid_clash'
    
    def _calculate_base_xg(self, match_data):
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        # Apply bounds
        home_attack = min(max(home_attack, 0.0), 5.0)
        away_attack = min(max(away_attack, 0.0), 5.0)
        home_defense = min(max(home_defense, 0.0), 5.0)
        away_defense = min(max(away_defense, 0.0), 5.0)
        
        home_xg = (home_attack + away_defense) / 2
        away_xg = (away_attack + home_defense) / 2
        
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
    'Early Season Uncertainty': {
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
    }
}

# ========== INITIALIZE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = EnhancedPredictionEngine()
    logger.info("EnhancedPredictionEngine initialized")

if 'db' not in st.session_state:
    st.session_state.db = PersistentFootballDatabase()
    logger.info("PersistentFootballDatabase initialized")

# Initialize session state for test case loading
if 'loaded_test_case' not in st.session_state:
    st.session_state.loaded_test_case = None
if 'test_case_data' not in st.session_state:
    st.session_state.test_case_data = TEST_CASES['Atletico Madrid vs Valencia']

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">👑 ULTIMATE FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Enhanced with Validation, Persistence & Kelly Criterion**")
    
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
            st.session_state.test_case_data = TEST_CASES['Atletico Madrid vs Valencia']
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
        phase = auto_context['season_phase']
        phase_class = f"season-{phase}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>📅 SEASON PHASE</h4>
            <p>Progress: <span style="font-size: 1.2em;"><strong>{progress:.1f}%</strong></span></p>
            <p>Phase: <span class="{phase_class}">{phase.upper()} SEASON</span></p>
            <small>Games: {games_played}/{total_teams * 2}</small>
            {f"<br><small>⚠️ Early season adjustment active</small>" if auto_context['is_early_season'] else ""}
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto2:
        # Team safety
        home_status = auto_context['home_status']
        away_status = auto_context['away_status']
        safe_cutoff = auto_context['safe_cutoff']
        
        status_class_home = f"status-{home_status}"
        status_class_away = f"status-{away_status}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🛡️ TEAM SAFETY</h4>
            <p><strong>{home_name}:</strong> 
            <span class="{status_class_home}">{home_status.upper()}</span>
            (Position {home_pos})</p>
            <p><strong>{away_name}:</strong> 
            <span class="{status_class_away}">{away_status.upper()}</span>
            (Position {away_pos})</p>
            <small>Safe if position ≤ {safe_cutoff}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto3:
        # Team classification
        home_class = auto_context['home_class']
        away_class = auto_context['away_class']
        both_safe = auto_context['both_safe']
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🏆 TEAM CLASS</h4>
            <p><strong>{home_name}:</strong> {home_class.upper()}</p>
            <p><strong>{away_name}:</strong> {away_class.upper()}</p>
            <p><strong>Both Teams Safe:</strong> 
            <span class="{'status-safe' if both_safe else 'status-danger'}">
            {'✓ YES' if both_safe else '✗ NO'}
            </span></p>
            <small>Position gap: {auto_context['position_gap']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== EDGE PATTERN CONDITIONS =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 EDGE PATTERN CONDITIONS")
    
    edge_data = current_data['edge_conditions']
    
    st.info("ℹ️ **Note:** 'Late Season' and 'Both Teams Safe' are auto-detected based on league data above.")
    
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
        
        # Show auto-detected late season status
        is_late_season = auto_context['is_late_season']
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
            <strong>⏰ Late Season Detection:</strong>
            <p style="margin: 5px 0;">Progress: {auto_context['season_progress']:.1f}% → 
            <span class="{'season-late' if is_late_season else 'season-mid'}">
            {'LATE SEASON' if is_late_season else 'NOT LATE SEASON'}
            </span></p>
            <small>Auto-detected: Late season = >66.6% of games played</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Show auto-detected both teams safe status
    both_safe_detected = auto_context['both_safe']
    st.markdown(f"""
    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 4px solid #2196F3;">
        <strong>🛡️ Both Teams Safe Detection:</strong>
        <p style="margin: 5px 0;">
        {home_name} (pos {home_pos}) and {away_name} (pos {away_pos}) are 
        <span class="{'status-safe' if both_safe_detected else 'status-danger'}">
        {'BOTH SAFE' if both_safe_detected else 'NOT BOTH SAFE'}
        </span>
        </p>
        <small>Auto-detected: Safe = position < {auto_context['danger_cutoff']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYZE BUTTON =====
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        analyze_disabled = len(all_errors) > 0
        
        if analyze_disabled:
            st.warning("⚠️ Fix validation errors before analysis")
        
        if st.button("🚀 RUN ENHANCED ANALYSIS", 
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
                
                # Manual edge conditions only
                manual_edges = {
                    'new_manager': new_manager,
                    'is_derby': is_derby,
                    'european_game': european_game
                }
                
                # Run analysis (auto-detection happens inside)
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
        st.markdown(f"## 📊 ENHANCED RESULTS: {pred_data['teams']}")
        
        # Show auto-detection summary
        st.markdown("### 🔍 AUTO-DETECTION SUMMARY")
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            season_progress = auto_context.get('season_progress', 0)
            season_phase = auto_context.get('season_phase', 'mid')
            phase_class = f"season-{season_phase}"
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>📅 Season Context</h4>
                <p><strong>Progress:</strong> {season_progress:.1f}%</p>
                <p><strong>Phase:</strong> <span class="{phase_class}">{season_phase.upper()} SEASON</span></p>
                <p><strong>Early Season:</strong> {'YES' if auto_context.get('is_early_season', False) else 'NO'}</p>
                <p><strong>Games:</strong> {match_data['games_played']} / {match_data['total_teams'] * 2}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_sum2:
            home_class = auto_context.get('home_class', 'mid')
            away_class = auto_context.get('away_class', 'mid')
            both_safe = auto_context.get('both_safe', False)
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;">
                <h4>🏆 Team Status</h4>
                <p><strong>{match_data['home_name']}:</strong> {home_class.upper()} (pos {match_data['home_pos']})</p>
                <p><strong>{match_data['away_name']}:</strong> {away_class.upper()} (pos {match_data['away_pos']})</p>
                <p><strong>Position Gap:</strong> {auto_context.get('position_gap', 0)}</p>
                <p><strong>Both Safe:</strong> 
                <span class="{'status-safe' if both_safe else 'status-danger'}">
                {'✓ YES' if both_safe else '✗ NO'}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Team info cards
        col_team1, col_team2 = st.columns(2)
        
        with col_team1:
            st.markdown(f"""
            <div class="team-card">
                <h3>🏠 {match_data['home_name']}</h3>
                <p><strong>Position:</strong> {match_data['home_pos']}</p>
                <p><strong>Attack:</strong> {match_data['home_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['home_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['home_goals5']} goals in last 5</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_team2:
            st.markdown(f"""
            <div class="team-card">
                <h3>✈️ {match_data['away_name']}</h3>
                <p><strong>Position:</strong> {match_data['away_pos']}</p>
                <p><strong>Attack:</strong> {match_data['away_attack']} goals/game</p>
                <p><strong>Defense:</strong> {match_data['away_defense']} conceded/game</p>
                <p><strong>Recent Form:</strong> {match_data['away_goals5']} goals in last 5</p>
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
                st.metric("Recommended Stake", stake_info['recommendation'])
            else:
                st.metric("Recommended Stake", stake_info)
        
        # Kelly Criterion details - FIXED HERE
        if isinstance(analysis['stake_recommendation'], dict):
            stake_info = analysis['stake_recommendation']
            # Check if 'expected_value' exists before using it
            expected_value = stake_info.get('expected_value', 0.0)
            
            st.markdown(f"""
            <div class="kelly-bet">
                <h4>💰 Kelly Criterion Analysis</h4>
                <p><strong>Full Kelly Percentage:</strong> {stake_info.get('kelly_percentage', 0.0)*100:.1f}% of bankroll</p>
                <p><strong>Fractional Kelly (1/4):</strong> {stake_info.get('fractional_percentage', 0.0)*100:.1f}% of bankroll</p>
                <p><strong>Expected Value:</strong> +{expected_value:.1f}% per bet</p>
                <p><small>{stake_info.get('reason', 'Based on probability and edge value')}</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Psychology badge
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <span class="psychology-badge {analysis['badge']}">
                {analysis['psychology']} PSYCHOLOGY
            </span>
            <small style="margin-left: 15px; color: #666;">
                Core Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
                (Accuracy Weight: {analysis['pattern_accuracy_weight']})
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # Edge patterns detected
        if analysis['edge_patterns']:
            st.markdown("### ⚡ EDGE PATTERNS DETECTED")
            
            for edge in analysis['edge_patterns']:
                edge_value = edge['edge_value']
                if edge_value > 0.25:
                    edge_class = "edge-high"
                elif edge_value > 0.15:
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
                    <p style="margin: 10px 0 5px 0;">Multiplier: ×{edge['multiplier']:.2f} | Accuracy Boost: +{edge.get('accuracy_boost', 0)*100:.1f}%</p>
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
            # Auto-detection details
            early_season_warning = "⚠️ **Early Season Warning:** Positions are less reliable in early season. Confidence reduced by 20%." if auto_context.get('is_early_season') else ""
            
            st.markdown(f"""
            #### 🔍 AUTO-DETECTED CONTEXT
            
            **Season Phase:**
            - Progress: {auto_context.get('season_progress', 0):.1f}%
            - Phase: {auto_context.get('season_phase', 'mid').upper()} SEASON
            - Late Season: {'YES' if auto_context.get('is_late_season', False) else 'NO'}
            - Early Season: {'YES' if auto_context.get('is_early_season', False) else 'NO'}
            
            {early_season_warning}
            
            **Team Safety:**
            - {match_data['home_name']}: {auto_context.get('home_status', 'mid').upper()}
            - {match_data['away_name']}: {auto_context.get('away_status', 'mid').upper()}
            - Both Teams Safe: {'YES' if auto_context.get('both_safe', False) else 'NO'}
            
            **Team Classification:**
            - {match_data['home_name']}: {auto_context.get('home_class', 'mid').upper()}
            - {match_data['away_name']}: {auto_context.get('away_class', 'mid').upper()}
            - Position Gap: {auto_context.get('position_gap', 0)}
            
            **Decision Thresholds:**
            - OVER if > {analysis['thresholds_used']['over']}
            - UNDER if < {analysis['thresholds_used']['under']}
            
            **Final Calculation:**
            - {analysis['base_xg']:.2f} × {analysis['total_multiplier']:.2f} = **{analysis['enhanced_xg']:.2f}**
            - Prediction: **{analysis['prediction']}**
            - Probability: **{analysis['actual_probability']*100:.1f}%**
            """)
        
        # Profit simulation - FIXED HERE TOO
        if isinstance(analysis['stake_recommendation'], dict):
            stake_info = analysis['stake_recommendation']
            kelly_pct = stake_info.get('fractional_percentage', 0.0)
            expected_value = stake_info.get('expected_value', 0.0)
            
            if kelly_pct > 0 and expected_value > 0:
                st.markdown('<div class="profit-highlight">', unsafe_allow_html=True)
                st.markdown(f"""
                ### 💰 PROFIT POTENTIAL (Kelly Criterion)
                
                **Match:** {match_data['home_name']} vs {match_data['away_name']}
                **Prediction:** {analysis['prediction']} ({analysis['confidence']} confidence)
                **Probability:** {analysis['actual_probability']*100:.1f}%
                **Recommended Stake:** {kelly_pct*100:.1f}% of bankroll
                **Expected Value:** +{expected_value:.1f}% per bet
                
                *Assuming $10,000 bankroll:*
                - Stake this match: **${kelly_pct*10000:.0f}**
                - Expected value: **+${kelly_pct*10000 * expected_value/100:.0f}**
                - Weekly (5 bets): **+${kelly_pct*10000 * 5 * expected_value/100:.0f}**
                - Monthly (20 bets): **+${kelly_pct*10000 * 20 * expected_value/100:.0f}**
                
                <small>*Note: These are theoretical values. Real results will vary.*</small>
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
                    - Predicted: **{predicted}** ({analysis['confidence']})
                    - Actual: **{actual_type}** ({actual_home}-{actual_away})
                    - Result: **{'✅ CORRECT' if is_correct else '❌ INCORRECT'}**
                    - Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
                    - Season: {auto_context.get('season_phase', 'mid').upper()} ({auto_context.get('season_progress', 0):.1f}%)
                    - Auto-detections recorded for future learning
                    """)
                    
                    # Update performance stats
                    new_stats = st.session_state.db.get_performance_stats()
                    st.rerun()
                else:
                    st.error("Failed to save result")

if __name__ == "__main__":
    main()