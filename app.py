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
    .badge-deception { background-color: #fff3e0; color: #ef6c00; }
    .badge-caution { background-color: #fce4ec; color: #c2185b; }
    .status-safe { color: #4CAF50; font-weight: bold; }
    .status-danger { color: #F44336; font-weight: bold; }
    .status-mid { color: #FF9800; font-weight: bold; }
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
    .fixes-highlight {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #2196F3;
    }
    .performance-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .card-overperforming { border-color: #4CAF50; }
    .card-underperforming { border-color: #F44336; }
    .card-normal { border-color: #FF9800; }
    .xg-comparison {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf7 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #7E57C2;
    }
</style>
""", unsafe_allow_html=True)

# ========== ENHANCED PERFORMANCE MATRICES ==========
class PerformanceMatrices:
    """League-specific expected performance matrices"""
    
    MATRICES = {
        18: {  # German Bundesliga 2 (18 teams)
            1:  {'attack': 2.00, 'defense': 0.80},
            2:  {'attack': 1.85, 'defense': 0.90},
            3:  {'attack': 1.75, 'defense': 1.00},
            4:  {'attack': 1.70, 'defense': 1.05},
            5:  {'attack': 1.60, 'defense': 1.15},
            6:  {'attack': 1.55, 'defense': 1.20},
            7:  {'attack': 1.50, 'defense': 1.25},
            8:  {'attack': 1.45, 'defense': 1.30},
            9:  {'attack': 1.40, 'defense': 1.35},
            10: {'attack': 1.35, 'defense': 1.40},
            11: {'attack': 1.30, 'defense': 1.45},
            12: {'attack': 1.25, 'defense': 1.50},
            13: {'attack': 1.20, 'defense': 1.55},
            14: {'attack': 1.15, 'defense': 1.60},
            15: {'attack': 1.10, 'defense': 1.65},
            16: {'attack': 1.05, 'defense': 1.70},
            17: {'attack': 1.00, 'defense': 1.75},
            18: {'attack': 0.95, 'defense': 1.80}
        },
        12: {  # Australian A-League (12 teams)
            1:  {'attack': 1.80, 'defense': 0.90},
            2:  {'attack': 1.70, 'defense': 1.00},
            3:  {'attack': 1.60, 'defense': 1.05},
            4:  {'attack': 1.50, 'defense': 1.10},
            5:  {'attack': 1.40, 'defense': 1.15},
            6:  {'attack': 1.35, 'defense': 1.20},
            7:  {'attack': 1.30, 'defense': 1.25},
            8:  {'attack': 1.25, 'defense': 1.30},
            9:  {'attack': 1.20, 'defense': 1.35},
            10: {'attack': 1.15, 'defense': 1.40},
            11: {'attack': 1.10, 'defense': 1.45},
            12: {'attack': 1.05, 'defense': 1.50}
        },
        20: {  # Premier League (default)
            1:  {'attack': 2.20, 'defense': 0.75},
            2:  {'attack': 2.05, 'defense': 0.80},
            3:  {'attack': 1.95, 'defense': 0.85},
            4:  {'attack': 1.85, 'defense': 0.90},
            5:  {'attack': 1.75, 'defense': 0.95},
            6:  {'attack': 1.65, 'defense': 1.00},
            7:  {'attack': 1.60, 'defense': 1.05},
            8:  {'attack': 1.55, 'defense': 1.10},
            9:  {'attack': 1.50, 'defense': 1.15},
            10: {'attack': 1.45, 'defense': 1.20},
            11: {'attack': 1.40, 'defense': 1.25},
            12: {'attack': 1.35, 'defense': 1.30},
            13: {'attack': 1.30, 'defense': 1.35},
            14: {'attack': 1.25, 'defense': 1.40},
            15: {'attack': 1.20, 'defense': 1.45},
            16: {'attack': 1.15, 'defense': 1.50},
            17: {'attack': 1.10, 'defense': 1.55},
            18: {'attack': 1.05, 'defense': 1.60},
            19: {'attack': 1.00, 'defense': 1.65},
            20: {'attack': 0.95, 'defense': 1.70}
        }
    }
    
    @classmethod
    def get_expected_performance(cls, position, total_teams):
        """Get expected attack/defense for position in league"""
        matrix = cls.MATRICES.get(total_teams, cls.MATRICES[20])
        
        # If exact position in matrix, return it
        if position in matrix:
            return matrix[position].copy()
        
        # Interpolate between closest positions
        positions = sorted(matrix.keys())
        lower = max([p for p in positions if p <= position], default=positions[0])
        upper = min([p for p in positions if p >= position], default=positions[-1])
        
        if lower == upper:
            return matrix[lower].copy()
        
        # Linear interpolation
        ratio = (position - lower) / (upper - lower)
        attack = matrix[lower]['attack'] + ratio * (matrix[upper]['attack'] - matrix[lower]['attack'])
        defense = matrix[lower]['defense'] + ratio * (matrix[upper]['defense'] - matrix[lower]['defense'])
        
        return {'attack': round(attack, 2), 'defense': round(defense, 2)}

# ========== ENHANCED PREDICTION ENGINE ==========
class EnhancedPredictionEngine:
    def __init__(self):
        # ORIGINAL PATTERNS (preserved)
        self.learned_patterns = {
            'top_vs_bottom_domination': {
                'base_multiplier': 1.05,
                'description': 'Top team good form vs bottom team → 2-1 type scores',
                'psychology': 'DOMINATION',
                'badge': 'badge-domination',
            },
            'relegation_battle': {
                'base_multiplier': 0.65,
                'description': 'Both fighting relegation → defensive football',
                'psychology': 'FEAR',
                'badge': 'badge-fear',
            },
            'mid_table_ambition': {
                'base_multiplier': 1.15,
                'description': 'Both safe mid-table → attacking football',
                'psychology': 'AMBITION',
                'badge': 'badge-ambition',
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.90,
                'description': 'Mid-table with form difference → controlled game',
                'psychology': 'CONTROL',
                'badge': 'badge-control',
            },
            'top_team_battle': {
                'base_multiplier': 0.95,
                'description': 'Top teams facing → quality creates and prevents goals',
                'psychology': 'QUALITY',
                'badge': 'badge-quality',
            },
            'top_vs_bottom_dominance': {
                'base_multiplier': 0.85,
                'description': 'Top team excellent form vs very poor bottom → 1-0 type',
                'psychology': 'DOMINANCE',
                'badge': 'badge-dominance',
            }
        }
        
        # NEW PERFORMANCE-BASED PATTERNS
        self.performance_patterns = {
            'top_team_false_positive': {
                'base_multiplier': 0.80,
                'description': 'Top team by position but underperforming metrics',
                'psychology': 'DECEPTION',
                'badge': 'badge-deception',
                'conditions': ['position <= 4', 'attack_ratio < 0.9']
            },
            'mid_team_hidden_quality': {
                'base_multiplier': 1.10,
                'description': 'Mid-table position but overperforming metrics',
                'psychology': 'AMBITION',
                'badge': 'badge-ambition',
                'conditions': ['5 <= position <= 12', 'attack_ratio > 1.1']
            },
            'defensive_stalemate': {
                'base_multiplier': 0.65,
                'description': 'Both teams strong defense, weak attack',
                'psychology': 'CAUTION',
                'badge': 'badge-caution',
                'conditions': ['defense_ratio < 0.95', 'attack_ratio < 0.95']
            },
            'attack_mismatch': {
                'base_multiplier': 1.20,
                'description': 'One team overperforming attack vs weak defense',
                'psychology': 'EXPLOITATION',
                'badge': 'badge-domination',
                'conditions': ['attack_ratio > 1.15', 'opponent_defense_ratio > 1.1']
            }
        }
        
        # Edge patterns
        self.edge_patterns = {
            'new_manager_bounce': {
                'multiplier': 1.25,
                'edge_value': 0.20,
                'description': 'Players desperate to impress new manager',
                'bet_type': 'HOME_WIN'
            },
            'derby_fear': {
                'multiplier': 0.60,
                'edge_value': 0.30,
                'description': 'Fear of losing derby > desire to win',
                'bet_type': 'UNDER_2_0'
            },
            'european_hangover': {
                'multiplier': 0.75,
                'edge_value': 0.28,
                'description': 'Physical/mental exhaustion from European travel',
                'bet_type': 'OPPONENT_DOUBLE_CHANCE'
            },
            'dead_rubber': {
                'multiplier': 1.30,
                'edge_value': 0.25,
                'description': 'Beach football mentality, relaxed play',
                'bet_type': 'OVER_2_5'
            }
        }
        
        # Thresholds
        self.thresholds = {
            'relegation_battle': {'over': 2.3, 'under': 2.7},
            'top_vs_bottom_domination': {'over': 2.6, 'under': 2.4},
            'dead_rubber': {'over': 2.4, 'under': 2.6},
            'derby_fear': {'over': 2.8, 'under': 2.2},
            'mid_table_ambition': {'over': 2.6, 'under': 2.4},
            'defensive_stalemate': {'over': 2.5, 'under': 2.5},  # Neutral
            'default': {'over': 2.7, 'under': 2.3}
        }
    
    def auto_detect_context(self, match_data):
        """Auto-detect season phase, safety, classification"""
        total_teams = match_data.get('total_teams', 20)
        games_played = match_data.get('games_played', 1)
        home_pos = match_data.get('home_pos', 10)
        away_pos = match_data.get('away_pos', 10)
        
        # Season phase
        total_games_season = total_teams * 2
        season_progress = (games_played / total_games_season) * 100
        
        if season_progress <= 33.33:
            season_phase = 'early'
            is_late_season = False
        elif season_progress <= 66.66:
            season_phase = 'mid'
            is_late_season = False
        else:
            season_phase = 'late'
            is_late_season = True
        
        # Team safety
        safe_cutoff = int(total_teams * 0.7)
        danger_cutoff = total_teams - 3
        
        home_status = 'safe' if home_pos <= safe_cutoff else 'danger'
        away_status = 'safe' if away_pos <= safe_cutoff else 'danger'
        both_safe = home_pos < danger_cutoff and away_pos < danger_cutoff
        
        # Classification
        top_cutoff = 4
        bottom_cutoff = total_teams - 5
        
        if home_pos <= top_cutoff:
            home_class = 'top'
        elif home_pos <= safe_cutoff:
            home_class = 'mid'
        else:
            home_class = 'bottom'
        
        if away_pos <= top_cutoff:
            away_class = 'top'
        elif away_pos <= safe_cutoff:
            away_class = 'mid'
        else:
            away_class = 'bottom'
        
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
            'safe_cutoff': safe_cutoff,
            'danger_cutoff': danger_cutoff,
            'top_cutoff': top_cutoff,
            'bottom_cutoff': bottom_cutoff
        }
    
    def calculate_performance_ratios(self, team_data):
        """Calculate performance vs expected for position"""
        expected = PerformanceMatrices.get_expected_performance(
            team_data['position'], 
            team_data['total_teams']
        )
        
        attack_ratio = team_data['attack'] / expected['attack']
        defense_ratio = team_data['defense'] / expected['defense']
        
        # Classify performance
        if attack_ratio > 1.15:
            attack_perf = 'STRONG_OVER'
        elif attack_ratio > 1.05:
            attack_perf = 'OVER'
        elif attack_ratio < 0.85:
            attack_perf = 'STRONG_UNDER'
        elif attack_ratio < 0.95:
            attack_perf = 'UNDER'
        else:
            attack_perf = 'NORMAL'
        
        if defense_ratio < 0.85:  # Lower = better defense
            defense_perf = 'STRONG_OVER'
        elif defense_ratio < 0.95:
            defense_perf = 'OVER'
        elif defense_ratio > 1.15:
            defense_perf = 'STRONG_UNDER'
        elif defense_ratio > 1.05:
            defense_perf = 'UNDER'
        else:
            defense_perf = 'NORMAL'
        
        return {
            'attack_ratio': round(attack_ratio, 3),
            'defense_ratio': round(defense_ratio, 3),
            'attack_perf': attack_perf,
            'defense_perf': defense_perf,
            'expected_attack': expected['attack'],
            'expected_defense': expected['defense'],
            'attack_discrepancy': round(team_data['attack'] - expected['attack'], 2),
            'defense_discrepancy': round(team_data['defense'] - expected['defense'], 2)
        }
    
    def calculate_adjusted_xg(self, match_data, home_perf, away_perf):
        """Calculate xG with performance adjustments"""
        # Original calculation
        original_home_xg = (match_data['home_attack'] + match_data['away_defense']) / 2
        original_away_xg = (match_data['away_attack'] + match_data['home_defense']) / 2
        original_total = original_home_xg + original_away_xg
        
        # Adjusted calculation (position-normalized)
        adjusted_home_xg = (
            (match_data['home_attack'] * home_perf['attack_ratio']) +  # Home's adjusted attack
            (match_data['away_defense'] / away_perf['defense_ratio'])  # Away's adjusted defense
        ) / 2
        
        adjusted_away_xg = (
            (match_data['away_attack'] * away_perf['attack_ratio']) +  # Away's adjusted attack
            (match_data['home_defense'] / home_perf['defense_ratio'])  # Home's adjusted defense
        ) / 2
        
        adjusted_total = adjusted_home_xg + adjusted_away_xg
        
        return {
            'original': round(original_total, 2),
            'adjusted': round(adjusted_total, 2),
            'original_home': round(original_home_xg, 2),
            'original_away': round(original_away_xg, 2),
            'adjusted_home': round(adjusted_home_xg, 2),
            'adjusted_away': round(adjusted_away_xg, 2)
        }
    
    def get_performance_multiplier(self, home_perf, away_perf, home_pos, away_pos):
        """Apply multipliers based on performance patterns"""
        multiplier = 1.0
        patterns_detected = []
        
        # PATTERN: Top team slump
        if home_pos <= 4 and home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']:
            multiplier *= 0.85
            patterns_detected.append("Top team slump (home)")
        
        if away_pos <= 4 and away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']:
            multiplier *= 0.85
            patterns_detected.append("Top team slump (away)")
        
        # PATTERN: Mid-table surge
        if 5 <= home_pos <= 12 and home_perf['attack_perf'] in ['OVER', 'STRONG_OVER']:
            multiplier *= 1.10
            patterns_detected.append("Mid-table surge (home)")
        
        if 5 <= away_pos <= 12 and away_perf['attack_perf'] in ['OVER', 'STRONG_OVER']:
            multiplier *= 1.10
            patterns_detected.append("Mid-table surge (away)")
        
        # PATTERN: Both overperforming
        if (home_perf['attack_perf'] in ['OVER', 'STRONG_OVER'] and 
            away_perf['attack_perf'] in ['OVER', 'STRONG_OVER']):
            multiplier *= 1.15
            patterns_detected.append("Both teams overperforming")
        
        # PATTERN: Both underperforming
        if (home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER'] and 
            away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']):
            multiplier *= 0.80
            patterns_detected.append("Both teams underperforming")
        
        # PATTERN: Defensive mismatch
        if (home_perf['defense_perf'] in ['OVER', 'STRONG_OVER'] and 
            away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']):
            multiplier *= 0.90
            patterns_detected.append("Defensive mismatch (home strong)")
        
        if (away_perf['defense_perf'] in ['OVER', 'STRONG_OVER'] and 
            home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']):
            multiplier *= 0.90
            patterns_detected.append("Defensive mismatch (away strong)")
        
        return round(multiplier, 3), patterns_detected
    
    def league_size_adjustment(self, total_teams, base_xg):
        """Adjust for league size characteristics"""
        if total_teams <= 14:  # Small leagues
            return base_xg * 1.10, "Small league (+10%)"
        elif total_teams <= 16:  # Medium
            return base_xg * 1.00, "Medium league (no adjustment)"
        elif total_teams == 18:  # Bundesliga 2 style
            return base_xg * 0.90, "18-team league (-10%)"
        elif total_teams == 20:  # Top leagues
            return base_xg * 1.05, "20-team league (+5%)"
        else:
            return base_xg * 0.95, f"Large league ({total_teams} teams, -5%)"
    
    def position_gap_adjustment(self, home_pos, away_pos, base_xg, home_perf, away_perf):
        """Adjust based on position gap"""
        gap = abs(home_pos - away_pos)
        adjustment = 1.0
        gap_notes = []
        
        if gap >= 10:
            adjustment *= 0.75
            gap_notes.append(f"Large gap ({gap} positions): ×0.75")
            
            # Check if dominant team underperforming
            dominant_pos = min(home_pos, away_pos)
            dominant_perf = home_perf if home_pos == dominant_pos else away_perf
            
            if dominant_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']:
                adjustment *= 0.90
                gap_notes.append("Dominant team underperforming: ×0.90")
        
        elif gap >= 6:
            adjustment *= 0.85
            gap_notes.append(f"Medium gap ({gap} positions): ×0.85")
        
        elif gap >= 3:
            adjustment *= 0.95
            gap_notes.append(f"Small gap ({gap} positions): ×0.95")
        
        # Underdog overperforming adjustment
        if gap >= 6:
            underdog_pos = max(home_pos, away_pos)
            underdog_perf = home_perf if home_pos == underdog_pos else away_perf
            
            if underdog_perf['attack_perf'] in ['OVER', 'STRONG_OVER']:
                adjustment *= 1.15
                gap_notes.append(f"Underdog (pos {underdog_pos}) overperforming: ×1.15")
        
        return base_xg * adjustment, gap_notes
    
    def recent_form_adjustment(self, home_goals5, away_goals5, home_avg, away_avg, base_xg):
        """Adjust based on recent form vs season average"""
        home_recent_avg = home_goals5 / 5 if home_goals5 > 0 else 0
        away_recent_avg = away_goals5 / 5 if away_goals5 > 0 else 0
        
        home_ratio = home_recent_avg / home_avg if home_avg > 0 else 1.0
        away_ratio = away_recent_avg / away_avg if away_avg > 0 else 1.0
        
        adjustment = 1.0
        form_notes = []
        
        # Hot form
        if home_ratio >= 1.3 or away_ratio >= 1.3:
            adjustment *= 1.10
            form_notes.append(f"Hot form detected: ×1.10")
        
        # Cold form
        if home_ratio <= 0.7 or away_ratio <= 0.7:
            adjustment *= 0.90
            form_notes.append(f"Cold form detected: ×0.90")
        
        # Momentum shift
        if (home_ratio >= 1.3 and away_ratio <= 0.7) or (away_ratio >= 1.3 and home_ratio <= 0.7):
            adjustment *= 1.05
            form_notes.append(f"Momentum shift: ×1.05")
        
        return base_xg * adjustment, form_notes
    
    def calculate_dynamic_thresholds(self, context, home_perf, away_perf):
        """Calculate dynamic OVER/UNDER thresholds"""
        base_over = 2.7
        base_under = 2.3
        adjustments = []
        
        # League size adjustment
        if context['total_teams'] >= 18:
            base_over -= 0.15
            adjustments.append("Large league: -0.15 OVER")
        
        # Season phase
        if context['season_phase'] == 'early':
            base_over += 0.10
            adjustments.append("Early season: +0.10 OVER")
        elif context['season_phase'] == 'late':
            base_over -= 0.10
            adjustments.append("Late season: -0.10 OVER")
        
        # Performance adjustments
        if (home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER'] and 
            away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']):
            base_over -= 0.20
            adjustments.append("Both underperforming: -0.20 OVER")
        
        if (home_perf['attack_perf'] in ['OVER', 'STRONG_OVER'] and 
            away_perf['attack_perf'] in ['OVER', 'STRONG_OVER']):
            base_over += 0.15
            adjustments.append("Both overperforming: +0.15 OVER")
        
        # Defensive quality
        if (home_perf['defense_perf'] in ['OVER', 'STRONG_OVER'] or 
            away_perf['defense_perf'] in ['OVER', 'STRONG_OVER']):
            base_over -= 0.10
            adjustments.append("Strong defense: -0.10 OVER")
        
        # Ensure minimum gap
        min_gap = 0.3
        if base_over - base_under < min_gap:
            base_under = base_over - min_gap
        
        return {
            'over': round(base_over, 2),
            'under': round(base_under, 2),
            'adjustments': adjustments
        }
    
    def detect_core_pattern_original(self, home_class, away_class, position_gap, both_safe):
        """Original pattern detection logic"""
        if (home_class == 'top' and away_class == 'bottom') or (away_class == 'top' and home_class == 'bottom'):
            if position_gap > 8:
                return 'top_vs_bottom_domination'
            else:
                return 'top_vs_bottom_dominance'
        
        if home_class == 'bottom' and away_class == 'bottom':
            return 'relegation_battle'
        
        if home_class == 'top' and away_class == 'top':
            return 'top_team_battle'
        
        if both_safe and home_class == 'mid' and away_class == 'mid':
            return 'mid_table_ambition'
        
        return 'controlled_mid_clash'
    
    def detect_performance_pattern(self, home_data, away_data, home_perf, away_perf):
        """Detect performance-based patterns"""
        patterns = []
        
        # Top team false positive
        if home_data['position'] <= 4 and home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']:
            patterns.append('top_team_false_positive')
        
        if away_data['position'] <= 4 and away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']:
            patterns.append('top_team_false_positive')
        
        # Mid team hidden quality
        if 5 <= home_data['position'] <= 12 and home_perf['attack_perf'] in ['OVER', 'STRONG_OVER']:
            patterns.append('mid_team_hidden_quality')
        
        if 5 <= away_data['position'] <= 12 and away_perf['attack_perf'] in ['OVER', 'STRONG_OVER']:
            patterns.append('mid_team_hidden_quality')
        
        # Defensive stalemate
        if (home_perf['defense_perf'] in ['OVER', 'STRONG_OVER'] and 
            away_perf['defense_perf'] in ['OVER', 'STRONG_OVER'] and
            home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER'] and
            away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER']):
            patterns.append('defensive_stalemate')
        
        return patterns
    
    def analyze_match_enhanced(self, match_data, manual_edges):
        """Enhanced analysis with all fixes"""
        # Auto-detect context
        auto_context = self.auto_detect_context(match_data)
        
        # Calculate performance ratios
        home_perf = self.calculate_performance_ratios({
            'position': match_data['home_pos'],
            'attack': match_data['home_attack'],
            'defense': match_data['home_defense'],
            'total_teams': match_data['total_teams']
        })
        
        away_perf = self.calculate_performance_ratios({
            'position': match_data['away_pos'],
            'attack': match_data['away_attack'],
            'defense': match_data['away_defense'],
            'total_teams': match_data['total_teams']
        })
        
        # Calculate adjusted xG
        xg_data = self.calculate_adjusted_xg(match_data, home_perf, away_perf)
        
        # Apply performance multiplier
        perf_multiplier, perf_patterns = self.get_performance_multiplier(
            home_perf, away_perf,
            match_data['home_pos'], match_data['away_pos']
        )
        
        adjusted_xg = xg_data['adjusted'] * perf_multiplier
        
        # Apply league size adjustment
        adjusted_xg, league_note = self.league_size_adjustment(match_data['total_teams'], adjusted_xg)
        
        # Apply position gap adjustment
        adjusted_xg, gap_notes = self.position_gap_adjustment(
            match_data['home_pos'], match_data['away_pos'],
            adjusted_xg, home_perf, away_perf
        )
        
        # Apply recent form adjustment
        adjusted_xg, form_notes = self.recent_form_adjustment(
            match_data['home_goals5'], match_data['away_goals5'],
            match_data['home_attack'], match_data['away_attack'],
            adjusted_xg
        )
        
        final_xg = round(adjusted_xg, 2)
        
        # Detect patterns
        core_pattern = self.detect_core_pattern_original(
            auto_context['home_class'],
            auto_context['away_class'],
            auto_context['position_gap'],
            auto_context['both_safe']
        )
        
        perf_patterns_list = self.detect_performance_pattern(
            {'position': match_data['home_pos'], 'class': auto_context['home_class']},
            {'position': match_data['away_pos'], 'class': auto_context['away_class']},
            home_perf, away_perf
        )
        
        # Calculate dynamic thresholds
        thresholds = self.calculate_dynamic_thresholds({
            'total_teams': match_data['total_teams'],
            'season_phase': auto_context['season_phase']
        }, home_perf, away_perf)
        
        # Make prediction
        if final_xg > thresholds['over']:
            prediction = 'OVER 2.5'
        elif final_xg < thresholds['under']:
            prediction = 'UNDER 2.5'
        else:
            prediction = 'OVER 2.5' if final_xg > 2.5 else 'UNDER 2.5'
        
        # Calculate confidence
        confidence = self.calculate_confidence(final_xg, thresholds, perf_patterns_list)
        
        # Calculate probability
        probability = self._calculate_probability(final_xg, prediction)
        
        # Stake recommendation
        stake = self.calculate_stake_recommendation(confidence, len(perf_patterns_list))
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probability': probability,
            'final_xg': final_xg,
            'original_xg': xg_data['original'],
            'adjusted_xg': xg_data['adjusted'],
            'performance_multiplier': perf_multiplier,
            'home_performance': home_perf,
            'away_performance': away_perf,
            'core_pattern': core_pattern,
            'performance_patterns': perf_patterns_list,
            'dynamic_thresholds': thresholds,
            'stake_recommendation': stake,
            'adjustment_notes': {
                'league': league_note,
                'gap': gap_notes,
                'form': form_notes,
                'performance_patterns': perf_patterns
            },
            'psychology': self.learned_patterns[core_pattern]['psychology'],
            'badge': self.learned_patterns[core_pattern]['badge']
        }, auto_context
    
    def calculate_confidence(self, final_xg, thresholds, perf_patterns):
        """Calculate confidence with performance patterns"""
        # Base confidence from xG distance from 2.5
        distance = abs(final_xg - 2.5)
        
        if distance > 0.8:
            base_confidence = 'HIGH'
        elif distance > 0.4:
            base_confidence = 'MEDIUM'
        else:
            base_confidence = 'LOW'
        
        # Boost from performance patterns
        if len(perf_patterns) >= 2:
            if base_confidence == 'LOW':
                return 'MEDIUM'
            elif base_confidence == 'MEDIUM':
                return 'HIGH'
        
        # Strong patterns boost confidence
        if 'defensive_stalemate' in perf_patterns and final_xg < 2.3:
            return 'HIGH'
        
        if 'top_team_false_positive' in perf_patterns and final_xg < 2.4:
            return 'HIGH'
        
        return base_confidence
    
    def calculate_stake_recommendation(self, confidence, num_patterns):
        """Calculate stake recommendation"""
        if confidence == 'HIGH' and num_patterns >= 2:
            return 'HEAVY BET (2x) ⚡'
        elif confidence == 'HIGH':
            return 'NORMAL BET (1x) ✅'
        elif confidence == 'MEDIUM' and num_patterns >= 1:
            return 'NORMAL BET (1x) ✅'
        elif confidence == 'MEDIUM':
            return 'SMALL BET (0.5x) ⚖️'
        else:
            return 'SMALL BET (0.25x) ⚖️'
    
    def _calculate_probability(self, enhanced_xg, prediction):
        """Calculate probability for display"""
        if prediction == 'OVER 2.5':
            prob = 0.5 + min((enhanced_xg - 2.5) * 0.15, 0.35)
        else:
            prob = 0.5 + min((2.5 - enhanced_xg) * 0.15, 0.35)
        
        return min(max(prob, 0.35), 0.85)

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
        """Load data from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.predictions = data.get('predictions', [])
                    self.outcomes = data.get('outcomes', [])
                    logger.info(f"Loaded {len(self.predictions)} predictions from {self.storage_file}")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
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
            
            logger.info(f"Prediction saved: {prediction_hash}")
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
        
        # Recent performance
        recent = self.outcomes[-10:] if len(self.outcomes) >= 10 else self.outcomes
        recent_correct = len([o for o in recent if o.get('outcome_accuracy') == "CORRECT"])
        recent_accuracy = recent_correct / len(recent) if recent else 0
        
        # Confidence performance
        conf_stats = {}
        for pred in self.predictions:
            hash_val = pred.get('hash')
            conf = pred.get('analysis', {}).get('confidence', 'MEDIUM')
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
    'Brentford vs Leeds': {
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
    'Adelaide vs Brisbane (12-team)': {
        'home_name': 'Adelaide',
        'away_name': 'Brisbane',
        'home_pos': 6,
        'away_pos': 4,
        'total_teams': 12,
        'games_played': 6,
        'home_attack': 1.5,
        'away_attack': 1.1,
        'home_defense': 1.37,
        'away_defense': 1.29,
        'home_goals5': 8,
        'away_goals5': 2,
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
    },
    'Darmstadt vs Preußen Münster': {
        'home_name': 'Darmstadt',
        'away_name': 'Preußen Münster',
        'home_pos': 4,
        'away_pos': 10,
        'total_teams': 18,
        'games_played': 15,
        'home_attack': 1.81,
        'away_attack': 1.27,
        'home_defense': 1.31,
        'away_defense': 1.53,
        'home_goals5': 11,
        'away_goals5': 4,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
        }
    },
    'Schalke vs Nuremberg': {
        'home_name': 'Schalke',
        'away_name': 'Nuremberg',
        'home_pos': 1,
        'away_pos': 11,
        'total_teams': 18,
        'games_played': 15,
        'home_attack': 1.59,
        'away_attack': 1.46,
        'home_defense': 0.97,
        'away_defense': 1.56,
        'home_goals5': 5,
        'away_goals5': 7,
        'edge_conditions': {
            'new_manager': False,
            'is_derby': False,
            'european_game': False
        }
    }
}

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

# ========== INITIALIZE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = EnhancedPredictionEngine()
    logger.info("EnhancedPredictionEngine initialized")

if 'db' not in st.session_state:
    st.session_state.db = PersistentFootballDatabase()
    logger.info("PersistentFootballDatabase initialized")

if 'loaded_test_case' not in st.session_state:
    st.session_state.loaded_test_case = None
if 'test_case_data' not in st.session_state:
    st.session_state.test_case_data = TEST_CASES['Darmstadt vs Preußen Münster']

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">👑 ULTIMATE FOOTBALL PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("### **Enhanced with Performance-Based Analysis**")
    
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
        
        if perf_stats['recent_10_total'] > 0:
            st.markdown("### 📈 Recent Performance (Last 10)")
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                st.metric("Recent Total", perf_stats['recent_10_total'])
            with col_rec2:
                recent_acc = f"{perf_stats['recent_10_accuracy']*100:.1f}%"
                st.metric("Recent Accuracy", recent_acc)
        
        if perf_stats['confidence_accuracies']:
            st.markdown("### 🎯 Confidence Performance")
            for conf, acc in perf_stats['confidence_accuracies'].items():
                st.markdown(f"""
                <div class="performance-metric">
                    <strong>{conf}:</strong> {acc*100:.1f}% accuracy
                    <br><small>{sum(1 for p in st.session_state.db.predictions if p.get('analysis', {}).get('confidence') == conf)} predictions</small>
                </div>
                """, unsafe_allow_html=True)
        
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
        
        if st.button("🔄 Reset All Inputs", type="secondary", use_container_width=True, key="reset_btn"):
            for key in list(st.session_state.keys()):
                if key.endswith('_input'):
                    del st.session_state[key]
            st.session_state.loaded_test_case = None
            st.session_state.test_case_data = TEST_CASES['Darmstadt vs Preußen Münster']
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
        progress = auto_context['season_progress']
        phase = auto_context['season_phase']
        phase_class = f"season-{phase}"
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>📅 SEASON PHASE</h4>
            <p>Progress: <span style="font-size: 1.2em;"><strong>{progress:.1f}%</strong></span></p>
            <p>Phase: <span class="{phase_class}">{phase.upper()} SEASON</span></p>
            <small>Games: {games_played}/{total_teams * 2}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto2:
        home_status = auto_context['home_status']
        away_status = auto_context['away_status']
        safe_cutoff = auto_context['safe_cutoff']
        
        st.markdown(f"""
        <div class="auto-detection">
            <h4>🛡️ TEAM SAFETY</h4>
            <p><strong>{home_name}:</strong> 
            <span class="status-{home_status}">{home_status.upper()}</span>
            (Position {home_pos} ≤ {safe_cutoff})</p>
            <p><strong>{away_name}:</strong> 
            <span class="status-{away_status}">{away_status.upper()}</span>
            (Position {away_pos} ≤ {safe_cutoff})</p>
            <small>Safe if position ≤ {safe_cutoff}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_auto3:
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
                
                # Run enhanced analysis
                analysis, auto_context = st.session_state.engine.analyze_match_enhanced(match_data, manual_edges)
                
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
                <p><strong>Both Safe:</strong> 
                <span class="{'status-safe' if both_safe else 'status-danger'}">
                {'✓ YES' if both_safe else '✗ NO'}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
        
        # ===== PERFORMANCE ANALYSIS =====
        st.markdown("### 📈 PERFORMANCE ANALYSIS")
        
        home_perf = analysis['home_performance']
        away_perf = analysis['away_performance']
        
        col_perf1, col_perf2 = st.columns(2)
        
        with col_perf1:
            home_card_class = "card-overperforming" if home_perf['attack_perf'] in ['OVER', 'STRONG_OVER'] else "card-underperforming" if home_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER'] else "card-normal"
            
            st.markdown(f"""
            <div class="performance-card {home_card_class}">
                <h4>🏠 {match_data['home_name']} Performance</h4>
                <p><strong>Position:</strong> {match_data['home_pos']}</p>
                <p><strong>Expected Attack:</strong> {home_perf['expected_attack']} goals/game</p>
                <p><strong>Actual Attack:</strong> {match_data['home_attack']} goals/game</p>
                <p><strong>Attack Ratio:</strong> {home_perf['attack_ratio']} 
                <span class="{'status-safe' if home_perf['attack_ratio'] > 1 else 'status-danger' if home_perf['attack_ratio'] < 1 else 'status-mid'}">
                ({home_perf['attack_perf'].replace('_', ' ')})
                </span></p>
                <p><strong>Defense Ratio:</strong> {home_perf['defense_ratio']} 
                <span class="{'status-safe' if home_perf['defense_ratio'] < 1 else 'status-danger' if home_perf['defense_ratio'] > 1 else 'status-mid'}">
                ({home_perf['defense_perf'].replace('_', ' ')})
                </span></p>
                <p><strong>Discrepancy:</strong> {home_perf['attack_discrepancy']:+.2f} attack, {home_perf['defense_discrepancy']:+.2f} defense</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_perf2:
            away_card_class = "card-overperforming" if away_perf['attack_perf'] in ['OVER', 'STRONG_OVER'] else "card-underperforming" if away_perf['attack_perf'] in ['UNDER', 'STRONG_UNDER'] else "card-normal"
            
            st.markdown(f"""
            <div class="performance-card {away_card_class}">
                <h4>✈️ {match_data['away_name']} Performance</h4>
                <p><strong>Position:</strong> {match_data['away_pos']}</p>
                <p><strong>Expected Attack:</strong> {away_perf['expected_attack']} goals/game</p>
                <p><strong>Actual Attack:</strong> {match_data['away_attack']} goals/game</p>
                <p><strong>Attack Ratio:</strong> {away_perf['attack_ratio']} 
                <span class="{'status-safe' if away_perf['attack_ratio'] > 1 else 'status-danger' if away_perf['attack_ratio'] < 1 else 'status-mid'}">
                ({away_perf['attack_perf'].replace('_', ' ')})
                </span></p>
                <p><strong>Defense Ratio:</strong> {away_perf['defense_ratio']} 
                <span class="{'status-safe' if away_perf['defense_ratio'] < 1 else 'status-danger' if away_perf['defense_ratio'] > 1 else 'status-mid'}">
                ({away_perf['defense_perf'].replace('_', ' ')})
                </span></p>
                <p><strong>Discrepancy:</strong> {away_perf['attack_discrepancy']:+.2f} attack, {away_perf['defense_discrepancy']:+.2f} defense</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ===== xG COMPARISON =====
        st.markdown("### 📊 xG CALCULATION BREAKDOWN")
        
        col_xg1, col_xg2 = st.columns(2)
        
        with col_xg1:
            fig = go.Figure()
            
            stages = ['Original xG', 'Adjusted xG', 'Performance Adj', 'League Adj', 'Gap Adj', 'Form Adj', 'Final xG']
            values = [
                analysis['original_xg'],
                analysis['adjusted_xg'],
                analysis['adjusted_xg'] * analysis['performance_multiplier'],
                analysis['adjusted_xg'] * analysis['performance_multiplier'],
                analysis['adjusted_xg'] * analysis['performance_multiplier'],
                analysis['adjusted_xg'] * analysis['performance_multiplier'],
                analysis['final_xg']
            ]
            
            fig.add_trace(go.Bar(
                x=stages,
                y=values,
                marker_color=['#FF6B6B', '#4ECDC4', '#96CEB4', '#FFD166', '#06D6A0', '#118AB2', '#073B4C'],
                text=[f'{v:.2f}' for v in values],
                textposition='auto'
            ))
            
            fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_hline(y=analysis['dynamic_thresholds']['over'], line_dash="dot", line_color="green", opacity=0.7)
            fig.add_hline(y=analysis['dynamic_thresholds']['under'], line_dash="dot", line_color="red", opacity=0.7)
            
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis_title="Expected Goals",
                title="xG Calculation Process with Adjustments"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_xg2:
            st.markdown(f"""
            <div class="xg-comparison">
                <h4>📐 ADJUSTMENT DETAILS</h4>
                
                <p><strong>Original xG:</strong> {analysis['original_xg']:.2f}</p>
                <p><strong>Performance Adjusted:</strong> {analysis['adjusted_xg']:.2f} (×{analysis['performance_multiplier']})</p>
                
                <h5>⚙️ Applied Adjustments:</h5>
                <ul>
                    <li><strong>League Size:</strong> {analysis['adjustment_notes']['league']}</li>
            """)
            
            for note in analysis['adjustment_notes']['gap']:
                st.markdown(f"<li><strong>Position Gap:</strong> {note}</li>", unsafe_allow_html=True)
            
            for note in analysis['adjustment_notes']['form']:
                st.markdown(f"<li><strong>Recent Form:</strong> {note}</li>", unsafe_allow_html=True)
            
            st.markdown(f"""
                </ul>
                
                <h5>🎯 Dynamic Thresholds:</h5>
                <p><strong>OVER if ></strong> {analysis['dynamic_thresholds']['over']} (normally 2.7)</p>
                <p><strong>UNDER if <</strong> {analysis['dynamic_thresholds']['under']} (normally 2.3)</p>
                
                <h5>🧠 Performance Patterns:</h5>
            """)
            
            if analysis['performance_patterns']:
                for pattern in analysis['performance_patterns']:
                    st.markdown(f"<div class='pattern-badge'>{pattern.replace('_', ' ').title()}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p>No specific performance patterns detected</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== PREDICTION SUMMARY =====
        st.markdown("### 🎯 PREDICTION SUMMARY")
        
        col_pred = st.columns(5)
        
        with col_pred[0]:
            st.metric("Prediction", analysis['prediction'])
        with col_pred[1]:
            st.metric("Confidence", analysis['confidence'])
        with col_pred[2]:
            st.metric("Probability", f"{analysis['probability']*100:.1f}%")
        with col_pred[3]:
            st.metric("Expected Goals", analysis['final_xg'])
        with col_pred[4]:
            stake_text = analysis['stake_recommendation']
            stake_value = 1.0
            if '2x' in stake_text:
                stake_value = 2.0
            elif '0.5x' in stake_text:
                stake_value = 0.5
            elif '0.25x' in stake_text:
                stake_value = 0.25
            st.metric("Stake", f"{stake_value}x")
        
        # Psychology badge
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <span class="psychology-badge {analysis['badge']}">
                {analysis['psychology']} PSYCHOLOGY
            </span>
            <small style="margin-left: 15px; color: #666;">
                Core Pattern: {analysis['core_pattern'].replace('_', ' ').title()}
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== FIXES HIGHLIGHT =====
        st.markdown("### 🔧 APPLIED ENHANCEMENTS")
        
        col_fixes1, col_fixes2, col_fixes3 = st.columns(3)
        
        with col_fixes1:
            st.markdown("""
            <div class="fixes-highlight">
                <h5>🎯 Position-Adjusted xG</h5>
                <p>Accounts for team performance relative to position expectations</p>
                <small>Fixes: Schalke underperformance detection</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_fixes2:
            st.markdown("""
            <div class="fixes-highlight">
                <h5>📏 Dynamic Thresholds</h5>
                <p>Adjusts OVER/UNDER thresholds based on league and performance</p>
                <small>Fixes: German league defensive bias</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_fixes3:
            st.markdown("""
            <div class="fixes-highlight">
                <h5>⚡ Performance Patterns</h5>
                <p>Detects over/underperforming teams and adjusts multipliers</p>
                <small>Fixes: Mid-table surge patterns</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Profit simulation
        st.markdown('<div class="profit-highlight">', unsafe_allow_html=True)
        
        stake_text = analysis['stake_recommendation']
        stake_multiplier = 1.0
        if '2x' in stake_text:
            stake_multiplier = 2.0
        elif '0.5x' in stake_text:
            stake_multiplier = 0.5
        elif '0.25x' in stake_text:
            stake_multiplier = 0.25
        
        # Calculate edge value from patterns
        edge_value = 0.0
        if len(analysis['performance_patterns']) >= 2:
            edge_value = 0.15
        elif len(analysis['performance_patterns']) >= 1:
            edge_value = 0.10
        
        if analysis['confidence'] == 'HIGH':
            edge_value += 0.05
        
        st.markdown(f"""
        ### 💰 PROFIT POTENTIAL
        
        **Match:** {match_data['home_name']} vs {match_data['away_name']}
        **Prediction:** {analysis['prediction']} ({analysis['confidence']} confidence)
        **Edge Value:** +{edge_value*100:.1f}%
        **Stake:** {analysis['stake_recommendation']}
        
        *Assuming standard stake = $100:*
        - Stake this match: **${100 * stake_multiplier:.0f}**
        - Expected value per bet: **+${100 * stake_multiplier * edge_value:.2f}**
        - Weekly (5 bets): **+${100 * stake_multiplier * 5 * edge_value:.0f}**
        - Monthly (20 bets): **+${100 * stake_multiplier * 20 * edge_value:.0f}**
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
                    - Performance Patterns: {', '.join(analysis['performance_patterns']) if analysis['performance_patterns'] else 'None'}
                    - xG: {analysis['final_xg']} vs Actual: {actual_total}
                    """)
                    
                    st.rerun()
                else:
                    st.error("Failed to save result")

if __name__ == "__main__":
    main()
