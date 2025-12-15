import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import logging
from scipy import stats

# ========== SETUP LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hybrid_predictor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="HYBRID FOOTBALL PREDICTOR",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== HYBRID PREDICTION ENGINE ==========
class HybridPredictionEngine:
    """Seamless hybrid of both systems - balanced and comprehensive"""
    
    def __init__(self):
        # From System 1: Pattern recognition
        self.learned_patterns = {
            'top_vs_bottom_domination': {
                'description': 'Top team good form vs bottom team',
                'psychology': 'DOMINATION',
                'over_adjust': 0.10,  # Probability adjustment
                'edge_boost': 0.15    # Edge boost when pattern matches
            },
            'relegation_battle': {
                'description': 'Both fighting relegation → defensive',
                'psychology': 'FEAR',
                'over_adjust': -0.12,
                'edge_boost': 0.10
            },
            'mid_table_ambition': {
                'description': 'Both safe mid-table → attacking',
                'psychology': 'AMBITION',
                'over_adjust': 0.08,
                'edge_boost': 0.08
            },
            'top_team_battle': {
                'description': 'Top teams facing → quality vs quality',
                'psychology': 'QUALITY',
                'over_adjust': -0.05,
                'edge_boost': 0.05
            },
            'desperation_chaos': {
                'description': 'Goalless desperate team → unpredictable',
                'psychology': 'CHAOS',
                'over_adjust': 0.00,  # Neutral
                'edge_boost': -0.20   # REDUCE edge due to unpredictability
            }
        }
        
        # From System 2: Market traps
        self.market_traps = {
            'OVER_HYPE_TRAP': {
                'conditions': ['public_over > 70', 'over_odds < 1.65', 'is_big_team_home'],
                'edge_penalty': -0.25,
                'confidence_penalty': 0.15
            },
            'UNDER_FEAR_TRAP': {
                'conditions': ['public_over < 30', 'under_odds < 1.70', 'is_relegation'],
                'edge_penalty': -0.20,
                'confidence_penalty': 0.10
            },
            'HISTORICAL_DATA_TRAP': {
                'conditions': ['h2h_over > 70', 'recent_over < 40'],
                'edge_penalty': -0.15,
                'confidence_penalty': 0.08
            }
        }
        
        # Big Six teams for trap detection
        self.BIG_SIX = ["Manchester United", "Manchester City", "Liverpool", 
                       "Chelsea", "Arsenal", "Tottenham", "Barcelona", "Real Madrid",
                       "Bayern Munich", "PSG", "Juventus", "AC Milan", "Inter Milan"]
    
    def auto_detect_context(self, match_data):
        """Comprehensive context detection (from System 1 enhanced)"""
        total_teams = match_data.get('total_teams', 20)
        games_played = match_data.get('games_played', 1)
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        
        # Season phase
        total_games_season = total_teams * 2
        season_progress = (games_played / total_games_season) * 100
        
        if season_progress <= 33.33:
            season_phase = 'early'
            season_multiplier = 0.9  # Early season more unpredictable
        elif season_progress <= 66.66:
            season_phase = 'mid'
            season_multiplier = 1.0  # Normal
        else:
            season_phase = 'late'
            season_multiplier = 1.1  # Late season patterns stronger
        
        # Team classification (enhanced)
        top_cutoff = max(4, int(total_teams * 0.2))  # Top 20%
        bottom_cutoff = total_teams - int(total_teams * 0.3)  # Bottom 30%
        
        if home_pos <= top_cutoff:
            home_class = 'top'
        elif home_pos <= bottom_cutoff:
            home_class = 'mid'
        else:
            home_class = 'bottom'
            
        if away_pos <= top_cutoff:
            away_class = 'top'
        elif away_pos <= bottom_cutoff:
            away_class = 'mid'
        else:
            away_class = 'bottom'
        
        # Safety zones
        safe_cutoff = int(total_teams * 0.7)
        home_safe = home_pos <= safe_cutoff
        away_safe = away_pos <= safe_cutoff
        both_safe = home_safe and away_safe
        
        # Desperation detection (from System 2)
        home_desperation = (home_pos >= int(total_teams * 0.75) and 
                           match_data.get('home_goals5', 0) / 5 < 0.8)
        away_desperation = (away_pos >= int(total_teams * 0.75) and 
                           match_data.get('away_goals5', 0) / 5 < 0.8)
        
        return {
            'season_phase': season_phase,
            'season_progress': season_progress,
            'season_multiplier': season_multiplier,
            'home_class': home_class,
            'away_class': away_class,
            'home_safe': home_safe,
            'away_safe': away_safe,
            'both_safe': both_safe,
            'position_gap': abs(home_pos - away_pos),
            'home_desperation': home_desperation,
            'away_desperation': away_desperation,
            'top_cutoff': top_cutoff,
            'bottom_cutoff': bottom_cutoff,
            'safe_cutoff': safe_cutoff
        }
    
    def detect_pattern(self, match_data, context):
        """Detect the dominant match pattern"""
        home_class = context['home_class']
        away_class = context['away_class']
        position_gap = context['position_gap']
        
        # Desperation chaos (from System 2)
        if context['home_desperation'] or context['away_desperation']:
            return 'desperation_chaos'
        
        # Top vs Bottom
        if (home_class == 'top' and away_class == 'bottom') or (away_class == 'top' and home_class == 'bottom'):
            if position_gap > 8:
                return 'top_vs_bottom_domination'
        
        # Relegation battle
        if home_class == 'bottom' and away_class == 'bottom':
            return 'relegation_battle'
        
        # Top team battle
        if home_class == 'top' and away_class == 'top':
            return 'top_team_battle'
        
        # Mid table (both safe)
        if context['both_safe'] and home_class == 'mid' and away_class == 'mid':
            return 'mid_table_ambition'
        
        # Default: controlled game (no strong pattern)
        return None
    
    def calculate_base_probability(self, match_data):
        """Calculate base probability using statistical methods"""
        # Expected goals calculation (System 1 approach)
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        home_xg = (home_attack + away_defense) / 2
        away_xg = (away_attack + home_defense) / 2
        total_xg = home_xg + away_xg
        
        # Recent form weighting (System 2 approach)
        home_goals5 = match_data.get('home_goals5', 0) / 5
        away_goals5 = match_data.get('away_goals5', 0) / 5
        
        # Weight: 60% xG model, 40% recent form
        weighted_xg = (total_xg * 0.6) + ((home_goals5 + away_goals5) * 0.4)
        
        # Convert xG to over probability using Poisson distribution
        # P(Over 2.5) = 1 - P(0 goals) - P(1 goal) - P(2 goals)
        lam = weighted_xg
        p0 = np.exp(-lam)
        p1 = lam * np.exp(-lam)
        p2 = (lam**2 / 2) * np.exp(-lam)
        
        base_over_prob = 1 - (p0 + p1 + p2)
        
        # Adjust for Poisson distribution limitations
        if lam < 1.5:
            base_over_prob *= 0.8
        elif lam > 3.5:
            base_over_prob = min(0.95, base_over_prob * 1.1)
        
        return {
            'base_over_prob': max(0.05, min(0.95, base_over_prob)),
            'total_xg': total_xg,
            'weighted_xg': weighted_xg,
            'home_xg': home_xg,
            'away_xg': away_xg
        }
    
    def detect_market_traps(self, match_data, context):
        """Detect market manipulation traps (System 2)"""
        traps = []
        
        # Check each trap condition
        public_over = match_data.get('public_over', 50)
        over_odds = match_data.get('over_odds', 2.0)
        under_odds = match_data.get('under_odds', 2.0)
        h2h_over = match_data.get('h2h_over', 50)
        recent_over = match_data.get('recent_over', 50)
        
        home_team = match_data.get('home_name', '')
        is_big_team_home = any(team in home_team for team in self.BIG_SIX)
        is_relegation = (context['home_class'] == 'bottom' and 
                        context['away_class'] == 'bottom')
        
        # Over hype trap
        if (public_over > 70 and over_odds < 1.65 and is_big_team_home):
            traps.append({
                'type': 'OVER_HYPE_TRAP',
                'description': f'Big team at home, public {public_over}% on Over, odds too low',
                'edge_penalty': -0.25,
                'confidence_penalty': 0.15
            })
        
        # Under fear trap
        if (public_over < 30 and under_odds < 1.70 and is_relegation):
            traps.append({
                'type': 'UNDER_FEAR_TRAP',
                'description': f'Relegation battle, public only {public_over}% on Over',
                'edge_penalty': -0.20,
                'confidence_penalty': 0.10
            })
        
        # Historical data trap
        if (h2h_over > 70 and recent_over < 40):
            traps.append({
                'type': 'HISTORICAL_DATA_TRAP',
                'description': f'H2H shows {h2h_over}% Over but recent only {recent_over}%',
                'edge_penalty': -0.15,
                'confidence_penalty': 0.08
            })
        
        return traps
    
    def calculate_edge(self, true_prob, odds):
        """Calculate mathematical edge (System 2)"""
        if odds <= 1.0:
            return 0.0
        
        implied_prob = 1 / odds
        edge = (true_prob - implied_prob) * 100
        
        # Adjust for bookmaker margin
        total_margin = 0.05  # 5% typical margin
        adjusted_edge = edge - (total_margin * 100 * implied_prob)
        
        return adjusted_edge
    
    def analyze_match(self, match_data):
        """Main hybrid analysis method"""
        
        # Step 1: Auto-detect context
        context = self.auto_detect_context(match_data)
        
        # Step 2: Calculate base probability
        prob_data = self.calculate_base_probability(match_data)
        base_over_prob = prob_data['base_over_prob']
        
        # Step 3: Detect pattern and apply adjustments
        pattern = self.detect_pattern(match_data, context)
        pattern_adjustment = 0
        pattern_edge_boost = 0
        
        if pattern:
            pattern_info = self.learned_patterns.get(pattern, {})
            pattern_adjustment = pattern_info.get('over_adjust', 0)
            pattern_edge_boost = pattern_info.get('edge_boost', 0)
            
            # Apply season multiplier
            pattern_adjustment *= context['season_multiplier']
        
        # Step 4: Apply edge conditions (from System 1)
        edge_adjustments = []
        
        if match_data.get('new_manager', False):
            edge_adjustments.append(0.08)  # New manager bounce
        
        if match_data.get('is_derby', False):
            edge_adjustments.append(-0.06)  # Derby pressure
        
        if match_data.get('european_game', False):
            edge_adjustments.append(-0.05)  # European hangover
        
        # Late season dead rubber (both safe)
        if (context['season_progress'] > 66.6 and 
            context['both_safe'] and 
            not match_data.get('is_derby', False)):
            edge_adjustments.append(0.07)
        
        # Step 5: Apply all adjustments
        adjusted_over_prob = base_over_prob + pattern_adjustment + sum(edge_adjustments)
        adjusted_over_prob = max(0.05, min(0.95, adjusted_over_prob))
        
        # Step 6: Calculate mathematical edge
        over_odds = match_data.get('over_odds', 2.0)
        under_odds = match_data.get('under_odds', 2.0)
        
        over_edge = self.calculate_edge(adjusted_over_prob, over_odds)
        under_edge = self.calculate_edge(1 - adjusted_over_prob, under_odds)
        
        # Apply pattern edge boost
        if over_edge > 0:
            over_edge *= (1 + pattern_edge_boost)
        if under_edge > 0:
            under_edge *= (1 + pattern_edge_boost)
        
        # Step 7: Detect market traps
        traps = self.detect_market_traps(match_data, context)
        
        # Apply trap penalties
        for trap in traps:
            if over_edge > 0:
                over_edge *= (1 + trap['edge_penalty'])
            if under_edge > 0:
                under_edge *= (1 + trap['edge_penalty'])
        
        # Step 8: Make final decision
        min_edge_threshold = 2.0  # Minimum edge required to bet
        
        if over_edge >= min_edge_threshold and over_edge > under_edge:
            prediction = 'OVER 2.5'
            edge_value = over_edge
            bet_type = 'VALUE_BET_OVER'
        elif under_edge >= min_edge_threshold and under_edge > over_edge:
            prediction = 'UNDER 2.5'
            edge_value = under_edge
            bet_type = 'VALUE_BET_UNDER'
        else:
            prediction = 'NO_BET'
            edge_value = max(over_edge, under_edge)
            bet_type = 'NO_VALUE'
        
        # Step 9: Calculate confidence
        confidence = self.calculate_confidence(
            edge_value, 
            prob_data['weighted_xg'], 
            len(traps), 
            pattern == 'desperation_chaos',
            context
        )
        
        # Step 10: Calculate optimal bet size
        bet_size = self.calculate_bet_size(edge_value, confidence, len(traps), pattern)
        
        # Step 11: Generate recommendation
        recommendation = self.generate_recommendation(prediction, edge_value, confidence, bet_size)
        
        return {
            'prediction': prediction,
            'bet_type': bet_type,
            'edge_value': edge_value,
            'confidence': confidence,
            'bet_size': bet_size,
            'recommendation': recommendation,
            'pattern': pattern,
            'pattern_info': self.learned_patterns.get(pattern, {}),
            'context': context,
            'probabilities': {
                'base_over': base_over_prob,
                'adjusted_over': adjusted_over_prob,
                'true_over': adjusted_over_prob,
                'true_under': 1 - adjusted_over_prob,
                'implied_over': 1 / over_odds if over_odds > 0 else 0,
                'implied_under': 1 / under_odds if under_odds > 0 else 0
            },
            'edges': {
                'over_edge': over_edge,
                'under_edge': under_edge
            },
            'xg_data': prob_data,
            'traps': traps,
            'edge_adjustments': edge_adjustments,
            'pattern_adjustment': pattern_adjustment
        }
    
    def calculate_confidence(self, edge, weighted_xg, trap_count, is_chaos, context):
        """Calculate confidence score (0-1)"""
        confidence = 0.5
        
        # Edge strength
        if edge > 10:
            confidence += 0.25
        elif edge > 5:
            confidence += 0.15
        elif edge > 2:
            confidence += 0.05
        
        # xG clarity
        if weighted_xg > 3.0 or weighted_xg < 2.0:
            confidence += 0.15
        elif weighted_xg > 2.8 or weighted_xg < 2.2:
            confidence += 0.10
        
        # Trap penalties
        confidence -= trap_count * 0.08
        
        # Chaos penalty (from System 2)
        if is_chaos:
            confidence *= 0.7
        
        # Season phase adjustment
        confidence *= context['season_multiplier']
        
        return max(0.2, min(0.95, confidence))
    
    def calculate_bet_size(self, edge, confidence, trap_count, pattern):
        """Calculate optimal bet size using Kelly Criterion principles"""
        if edge <= 0:
            return 0.0
        
        # Base Kelly fraction (simplified)
        kelly_fraction = (edge / 100) * confidence
        
        # Apply reductions
        if trap_count > 0:
            kelly_fraction *= 0.7
        
        if pattern == 'desperation_chaos':
            kelly_fraction *= 0.5
        
        # Conservative limits
        if kelly_fraction > 0.10:  # Max 10% of bankroll
            return 0.10
        elif kelly_fraction < 0.01:  # Min 1% bet
            return 0.01 if edge > 2.0 else 0.0
        
        return round(kelly_fraction, 3)
    
    def generate_recommendation(self, prediction, edge, confidence, bet_size):
        """Generate human-readable recommendation"""
        if prediction == 'NO_BET':
            return "NO VALUE BET - Avoid this match"
        
        # Confidence levels
        if confidence > 0.8:
            conf_text = "VERY HIGH CONFIDENCE"
        elif confidence > 0.65:
            conf_text = "HIGH CONFIDENCE"
        elif confidence > 0.5:
            conf_text = "MODERATE CONFIDENCE"
        else:
            conf_text = "LOW CONFIDENCE"
        
        # Bet size categories
        if bet_size >= 0.07:
            size_text = "STRONG BET"
        elif bet_size >= 0.04:
            size_text = "MEDIUM BET"
        else:
            size_text = "SMALL BET"
        
        return f"{size_text} on {prediction} ({conf_text}, +{edge:.1f}% edge)"

# ========== PERSISTENT DATABASE ==========
class HybridFootballDatabase:
    """Enhanced database with performance tracking"""
    
    def __init__(self, storage_file="hybrid_predictions.json"):
        self.storage_file = storage_file
        self.predictions = []
        self.outcomes = []
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.predictions = data.get('predictions', [])
                    self.outcomes = data.get('outcomes', [])
                    logger.info(f"Loaded {len(self.predictions)} predictions")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
    
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
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def save_prediction(self, prediction_data):
        """Save prediction with hash"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_input = f"{prediction_data.get('match_data', {}).get('home_name', '')}_{prediction_data.get('match_data', {}).get('away_name', '')}_{timestamp}"
            prediction_hash = hashlib.md5(hash_input.encode()).hexdigest()
            
            prediction_record = {
                'hash': prediction_hash,
                'timestamp': datetime.now().isoformat(),
                'match_data': prediction_data.get('match_data', {}),
                'analysis': prediction_data.get('analysis', {}),
                'type': 'HYBRID'
            }
            
            self.predictions.append(prediction_record)
            self.save_data()
            return prediction_hash
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        total = len(self.outcomes)
        correct = len([o for o in self.outcomes if o.get('outcome_accuracy') == "CORRECT"])
        accuracy = correct / total if total > 0 else 0
        
        # ROI calculation
        total_staked = 0
        total_won = 0
        
        for outcome in self.outcomes:
            pred_hash = outcome.get('prediction_hash')
            prediction = next((p for p in self.predictions if p.get('hash') == pred_hash), None)
            
            if prediction:
                bet_size = prediction.get('analysis', {}).get('bet_size', 0.02)
                odds = 2.0  # Default odds
                
                # Find odds from match data
                match_data = prediction.get('match_data', {})
                if prediction.get('analysis', {}).get('prediction', '').startswith('OVER'):
                    odds = match_data.get('over_odds', 2.0)
                elif prediction.get('analysis', {}).get('prediction', '').startswith('UNDER'):
                    odds = match_data.get('under_odds', 2.0)
                
                stake = 100 * bet_size  # Assuming $100 unit stake
                total_staked += stake
                
                if outcome.get('outcome_accuracy') == "CORRECT":
                    total_won += stake * (odds - 1)
        
        roi = ((total_won - total_staked) / total_staked * 100) if total_staked > 0 else 0
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'total_staked': total_staked,
            'total_won': total_won,
            'roi': roi,
            'profit': total_won - total_staked
        }

# ========== STREAMLIT UI ==========
def create_hybrid_ui():
    """Create comprehensive input UI"""
    
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
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pattern-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .badge-domination { background: #e8f5e9; color: #2e7d32; }
    .badge-fear { background: #ffebee; color: #c62828; }
    .badge-ambition { background: #fff8e1; color: #ff8f00; }
    .badge-chaos { background: #f3e5f5; color: #6a1b9a; }
    .badge-quality { background: #e3f2fd; color: #1565c0; }
    .trap-warning {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #F44336;
    }
    .edge-highlight {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🎯 HYBRID FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Balanced System: Pattern Recognition + Mathematical Edge**")
    
    # Initialize session state
    if 'hybrid_engine' not in st.session_state:
        st.session_state.hybrid_engine = HybridPredictionEngine()
    if 'hybrid_db' not in st.session_state:
        st.session_state.hybrid_db = HybridFootballDatabase()
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Performance Dashboard")
        
        stats = st.session_state.hybrid_db.get_performance_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Predictions", stats['total_predictions'])
            st.metric("Accuracy", f"{stats['accuracy']*100:.1f}%" if stats['total_predictions'] > 0 else "N/A")
        
        with col2:
            st.metric("ROI", f"{stats['roi']:.1f}%" if stats['total_staked'] > 0 else "N/A")
            st.metric("Profit/Loss", f"${stats['profit']:.2f}" if stats['total_staked'] > 0 else "N/A")
        
        st.markdown("---")
        st.markdown("### ⚙️ System Features")
        st.info("""
        **Hybrid Approach:**
        - Pattern Recognition (System 1)
        - Mathematical Edge (System 2)
        - Market Trap Detection
        - Value Betting Principles
        - Kelly Bet Sizing
        """)
        
        st.markdown("### 📈 Recent Predictions")
        recent = st.session_state.hybrid_db.predictions[-5:] if st.session_state.hybrid_db.predictions else []
        for pred in recent:
            match_data = pred.get('match_data', {})
            analysis = pred.get('analysis', {})
            st.markdown(f"""
            **{match_data.get('home_name', '?')} vs {match_data.get('away_name', '?')}**
            - {analysis.get('prediction', '?')} ({analysis.get('edge_value', 0):.1f}% edge)
            - {analysis.get('confidence', 0)*100:.0f}% confidence
            """)
    
    # Main input form
    st.markdown("### 📝 INPUT DATA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 HOME TEAM")
        home_name = st.text_input("Team Name", "Liverpool")
        home_pos = st.number_input("League Position", 1, 40, 4)
        home_attack = st.number_input("Avg Goals Scored", 0.0, 5.0, 2.1, 0.1)
        home_defense = st.number_input("Avg Goals Conceded", 0.0, 5.0, 0.9, 0.1)
        home_goals5 = st.number_input("Goals in Last 5 Games", 0, 30, 12)
    
    with col2:
        st.subheader("🚌 AWAY TEAM")
        away_name = st.text_input("Team Name", "Burnley")
        away_pos = st.number_input("League Position", 1, 40, 18)
        away_attack = st.number_input("Avg Goals Scored", 0.0, 5.0, 0.8, 0.1)
        away_defense = st.number_input("Avg Goals Conceded", 0.0, 5.0, 1.9, 0.1)
        away_goals5 = st.number_input("Goals in Last 5 Games", 0, 30, 5)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("⚙️ LEAGUE SETTINGS")
        total_teams = st.number_input("Total Teams", 10, 40, 20)
        games_played = st.number_input("Games Played", 1, 50, 28)
        
        st.subheader("🎯 MARKET DATA")
        over_odds = st.number_input("Over 2.5 Odds", 1.1, 10.0, 1.65, 0.05)
        under_odds = st.number_input("Under 2.5 Odds", 1.1, 10.0, 2.40, 0.05)
        public_over = st.number_input("Public % on Over", 0, 100, 68)
    
    with col4:
        st.subheader("📊 CONTEXT DATA")
        h2h_over = st.number_input("H2H Over 2.5 %", 0, 100, 55)
        recent_over = st.number_input("Recent Over 2.5 %", 0, 100, 45)
        
        st.subheader("🎭 EDGE CONDITIONS")
        new_manager = st.checkbox("New Manager Effect")
        is_derby = st.checkbox("Local Derby")
        european_game = st.checkbox("European Game Midweek")
    
    # Prepare match data
    match_data = {
        'home_name': home_name,
        'away_name': away_name,
        'home_pos': home_pos,
        'away_pos': away_pos,
        'home_attack': home_attack,
        'away_attack': away_attack,
        'home_defense': home_defense,
        'away_defense': away_defense,
        'home_goals5': home_goals5,
        'away_goals5': away_goals5,
        'total_teams': total_teams,
        'games_played': games_played,
        'over_odds': over_odds,
        'under_odds': under_odds,
        'public_over': public_over,
        'h2h_over': h2h_over,
        'recent_over': recent_over,
        'new_manager': new_manager,
        'is_derby': is_derby,
        'european_game': european_game
    }
    
    # Analyze button
    if st.button("🚀 RUN HYBRID ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Analyzing match with hybrid engine..."):
            analysis = st.session_state.hybrid_engine.analyze_match(match_data)
            
            # Save to database
            pred_data = {
                'match_data': match_data,
                'analysis': analysis
            }
            st.session_state.hybrid_db.save_prediction(pred_data)
            
            st.session_state.current_analysis = analysis
            st.rerun()
    
    # Display results
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        
        st.markdown("---")
        st.markdown("## 📊 HYBRID ANALYSIS RESULTS")
        
        # Key metrics
        col_metrics = st.columns(4)
        with col_metrics[0]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Prediction", analysis['prediction'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_metrics[1]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Edge Value", f"{analysis['edge_value']:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_metrics[2]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Confidence", f"{analysis['confidence']*100:.0f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_metrics[3]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Bet Size", f"{analysis['bet_size']*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Pattern detection
        if analysis['pattern']:
            pattern_info = analysis['pattern_info']
            badge_class = f"badge-{analysis['pattern'].split('_')[-1]}"
            
            st.markdown(f"""
            ### 🎭 DETECTED PATTERN
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                <span class="pattern-badge {badge_class}">
                    {analysis['pattern'].replace('_', ' ').upper()}
                </span>
                <p style="margin-top: 10px;"><strong>Psychology:</strong> {pattern_info.get('psychology', 'N/A')}</p>
                <p><strong>Description:</strong> {pattern_info.get('description', 'N/A')}</p>
                <p><strong>Probability Adjustment:</strong> {analysis['pattern_adjustment']:+.3f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Edge adjustments
        if analysis['edge_adjustments']:
            st.markdown("### ⚡ APPLIED EDGE ADJUSTMENTS")
            for i, adj in enumerate(analysis['edge_adjustments']):
                source = ["New Manager", "Derby", "European Game", "Dead Rubber"][min(i, 3)]
                st.info(f"**{source}**: {adj:+.3f} probability adjustment")
        
        # Market traps
        if analysis['traps']:
            st.markdown('<div class="trap-warning">', unsafe_allow_html=True)
            st.markdown("### 🚨 MARKET TRAPS DETECTED")
            for trap in analysis['traps']:
                st.warning(f"**{trap['type']}**: {trap['description']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Probability analysis
        st.markdown("### 📈 PROBABILITY BREAKDOWN")
        
        col_prob1, col_prob2 = st.columns(2)
        
        with col_prob1:
            probs = analysis['probabilities']
            fig = go.Figure(data=[
                go.Bar(name='True Probability', 
                       x=['Over 2.5', 'Under 2.5'], 
                       y=[probs['true_over'], probs['true_under']],
                       marker_color=['#10B981', '#EF4444']),
                go.Bar(name='Implied Probability', 
                       x=['Over 2.5', 'Under 2.5'],
                       y=[probs['implied_over'], probs['implied_under']],
                       marker_color=['#34D399', '#FCA5A5'])
            ])
            fig.update_layout(
                barmode='group', 
                height=300, 
                title="True vs Implied Probabilities",
                yaxis_title="Probability",
                yaxis_tickformat=".0%"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_prob2:
            # xG visualization
            xg_data = analysis['xg_data']
            fig = go.Figure(data=[
                go.Bar(name='Home xG', x=['Expected Goals'], y=[xg_data['home_xg']],
                       marker_color='#3B82F6'),
                go.Bar(name='Away xG', x=['Expected Goals'], y=[xg_data['away_xg']],
                       marker_color='#10B981')
            ])
            fig.update_layout(
                height=300,
                title="Expected Goals Breakdown",
                yaxis_title="Expected Goals",
                showlegend=True
            )
            fig.add_hline(y=2.5, line_dash="dash", line_color="gray", 
                         annotation_text="2.5 Line", annotation_position="bottom right")
            st.plotly_chart(fig, use_container_width=True)
        
        # Betting recommendation
        if analysis['prediction'] != 'NO_BET':
            st.markdown('<div class="edge-highlight">', unsafe_allow_html=True)
            st.markdown(f"### 💰 BETTING RECOMMENDATION")
            st.markdown(f"#### **{analysis['recommendation']}**")
            
            # Profit simulation
            stake = 100 * analysis['bet_size']
            odds = over_odds if analysis['prediction'] == 'OVER 2.5' else under_odds
            potential_win = stake * (odds - 1)
            expected_value = stake * (analysis['edge_value'] / 100)
            
            st.markdown(f"""
            **Assuming $100 unit stake:**
            - Bet size: **${stake:.2f}** ({analysis['bet_size']*100:.1f}%)
            - Odds: **{odds:.2f}**
            - Potential profit: **${potential_win:.2f}**
            - Expected value: **${expected_value:.2f}** (+{analysis['edge_value']:.1f}% edge)
            
            **Confidence Factors:**
            - Mathematical edge: {analysis['edge_value']:.1f}%
            - Pattern recognition: {analysis['pattern'] or 'None'}
            - Market traps: {len(analysis['traps'])} detected
            - Context adjustments: {len(analysis['edge_adjustments'])} applied
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #fef3c7; padding: 20px; border-radius: 10px; border-left: 4px solid #f59e0b;">
                <h3>⚠️ NO BET RECOMMENDED</h3>
                <p>Insufficient mathematical edge detected for a profitable bet.</p>
                <p><strong>Reasons:</strong></p>
                <ul>
                    <li>Edge value ({analysis['edge_value']:.1f}%) below minimum threshold (2.0%)</li>
                    <li>Market traps may be affecting value</li>
                    <li>Pattern indicates unpredictability</li>
                </ul>
                <p><em>Smart betting sometimes means not betting at all.</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Context summary
        with st.expander("🔍 VIEW DETAILED CONTEXT ANALYSIS"):
            context = analysis['context']
            
            col_ctx1, col_ctx2 = st.columns(2)
            
            with col_ctx1:
                st.markdown("**Season Context:**")
                st.write(f"- Progress: {context['season_progress']:.1f}%")
                st.write(f"- Phase: {context['season_phase'].upper()} season")
                st.write(f"- Multiplier: ×{context['season_multiplier']:.2f}")
                
                st.markdown("**Team Classification:**")
                st.write(f"- {home_name}: {context['home_class'].upper()} (safe: {'✓' if context['home_safe'] else '✗'})")
                st.write(f"- {away_name}: {context['away_class'].upper()} (safe: {'✓' if context['away_safe'] else '✗'})")
                st.write(f"- Both safe: {'✓' if context['both_safe'] else '✗'}")
            
            with col_ctx2:
                st.markdown("**Risk Factors:**")
                st.write(f"- Position gap: {context['position_gap']}")
                st.write(f"- {home_name} desperation: {'✓' if context['home_desperation'] else '✗'}")
                st.write(f"- {away_name} desperation: {'✓' if context['away_desperation'] else '✗'}")
                
                st.markdown("**Cutoffs Used:**")
                st.write(f"- Top cutoff: position ≤ {context['top_cutoff']}")
                st.write(f"- Bottom cutoff: position > {context['bottom_cutoff']}")
                st.write(f"- Safe cutoff: position ≤ {context['safe_cutoff']}")
        
        # Record outcome
        st.markdown("---")
        st.markdown("### 📝 RECORD ACTUAL OUTCOME")
        
        col_out1, col_out2 = st.columns(2)
        
        with col_out1:
            actual_home = st.number_input("Home Goals", 0, 10, 0, key="act_home")
        
        with col_out2:
            actual_away = st.number_input("Away Goals", 0, 10, 0, key="act_away")
        
        if st.button("✅ SAVE RESULT", type="secondary"):
            if actual_home == 0 and actual_away == 0:
                st.warning("Please enter actual scores")
            else:
                actual_total = actual_home + actual_away
                predicted_type = analysis['prediction']
                actual_type = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
                is_correct = predicted_type == actual_type
                
                st.success(f"""
                **Result recorded:**
                - Predicted: **{predicted_type}**
                - Actual: **{actual_type}** ({actual_home}-{actual_away})
                - Result: **{'✅ CORRECT' if is_correct else '❌ INCORRECT'}**
                """)

# Run the app
if __name__ == "__main__":
    create_hybrid_ui()
