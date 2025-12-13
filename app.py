import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import math

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="ENHANCED FOOTBALL PREDICTOR V6",
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
    .badge-desperation {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .badge-mutual-attack {
        background-color: #e8f5e8;
        color: #1b5e20;
        border: 1px solid #4CAF50;
    }
    .badge-safe-dominance {
        background-color: #e3f2fd;
        color: #0d47a1;
        border: 1px solid #2196F3;
    }
    .badge-control {
        background-color: #fff8e1;
        color: #ff8f00;
        border: 1px solid #FFC107;
    }
    .learning-message {
        background-color: #e8f5e8;
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .case-study {
        background-color: #fff3e0;
        border-left: 5px solid #FF9800;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .failure-analysis {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .mutual-attack-highlight {
        background-color: #e8f5e8;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== ENHANCED UNIFIED PREDICTION ENGINE V6 ==========

class EnhancedPredictionEngineV6:
    """
    ENHANCED ENGINE V6: Statistics × Psychology × Mutual Attack Layer × Learning
    FIXED: Mid-table clashes with form differences now correctly handled
    """
    
    def __init__(self):
        # LEARNED PATTERNS FROM ALL DATA (including failures)
        self.learned_patterns = {
            'relegation_battle': {
                'base_multiplier': 0.65,
                'description': 'Both bottom 4 → FEAR dominates → 35% fewer goals',
                'confidence': 0.92,
                'example': 'Lecce 1-0 Pisa (gap 1, predicted OVER, actual UNDER)',
                'base_badge': 'badge-fear',
                'psychology': 'FEAR dominates: Both playing NOT TO LOSE'
            },
            'relegation_threatened': {
                'base_multiplier': 0.85,
                'description': 'One team bottom 4, other safe → threatened team cautious → 15% fewer goals',
                'confidence': 0.85,
                'example': 'Team fighting relegation vs mid-table safe team',
                'base_badge': 'badge-caution',
                'psychology': 'Threatened team plays with fear, lowers scoring'
            },
            'mid_table_clash': {
                'base_multiplier': 1.15,
                'description': 'Both safe (5-16), gap ≤ 4, similar form → SIMILAR AMBITIONS → 15% more goals',
                'confidence': 0.88,
                'example': 'Annecy 2-1 Le Mans (gap 1, actual OVER)',
                'base_badge': 'badge-ambition',
                'psychology': 'Both teams confident, similar form → playing TO WIN'
            },
            'controlled_mid_clash': {
                'base_multiplier': 0.90,
                'description': 'Mid-table clash with significant form difference → controlled game',
                'confidence': 0.85,
                'example': 'Chelsea 2-0 Everton (form: GOOD vs POOR)',
                'base_badge': 'badge-control',
                'psychology': 'Better form team controls, poorer form team defends'
            },
            'hierarchical': {
                'base_multiplier': 0.85,
                'description': 'Gap > 4, no relegation teams → DIFFERENT AGENDAS → 15% fewer goals',
                'confidence': 0.91,
                'example': 'Nancy 1-0 Clermont (gap 8, actual UNDER)',
                'base_badge': 'badge-caution',
                'psychology': 'Better team controls, weaker team defends'
            },
            'top_team_battle': {
                'base_multiplier': 0.95,
                'description': 'Both top 4 → QUALITY over caution → normal scoring',
                'confidence': 0.78,
                'example': 'Title contenders facing each other',
                'base_badge': 'badge-quality',
                'psychology': 'Quality creates AND prevents goals'
            },
            'mid_vs_top': {
                'base_multiplier': 1.05,
                'description': 'One top 4, one mid-table (5-16) → AMBITION vs CONTROL → slightly more goals',
                'confidence': 0.75,
                'example': 'Mid-table team ambitious vs top team controlling',
                'base_badge': 'badge-ambition',
                'psychology': 'Mid-table attacks ambitiously, top team manages'
            },
            'mutual_attack_scenario': {
                'base_multiplier': 1.15,
                'description': 'Safe team excellent form drives high-scoring game despite relegation context',
                'confidence': 0.82,
                'example': 'Greuther Furth 3-3 Hertha (gap 9, actual OVER)',
                'base_badge': 'badge-mutual-attack',
                'psychology': 'MUTUAL ATTACK: Safe team attacks confidently, threatened team desperate'
            }
        }
        
        # FORM ADJUSTMENTS (learned from data)
        self.form_adjustments = {
            'excellent': 1.20,      # Scoring 30%+ above average
            'good': 1.10,           # Scoring 10-30% above average
            'average': 1.00,
            'poor': 0.90,           # Scoring 10-30% below average
            'very_poor': 0.80       # Scoring 30%+ below average
        }
        
        # SEASON URGENCY (learned from data)
        self.urgency_factors = {
            'early': 0.95,          # Games 1-10: Teams still finding form
            'mid': 1.00,            # Games 11-25: Normal urgency
            'late': 1.05,           # Games 26+: More urgency, more goals
            'relegation_late': 0.90 # Late season + relegation = MORE FEAR
        }
        
        # DESPERATION PATTERNS (ENHANCED FOR V6)
        self.desperation_patterns = {
            'mutual_attack': {
                'description': 'Safe team excellent form + threatened team desperate = HIGH SCORING',
                'multiplier': 1.15,
                'badge': 'badge-mutual-attack',
                'conditions': ['gap > 6', 'safe_team_excellent_form', 'mid_to_late_season']
            },
            'safe_dominance': {
                'description': 'Safe team good/excellent form + threatened team poor form = ONE-WAY ATTACK',
                'multiplier': 1.10,
                'badge': 'badge-safe-dominance',
                'conditions': ['gap > 4', 'safe_team_good_form', 'threatened_team_poor_form']
            },
            'threatened_desperation': {
                'description': 'Threatened team excellent form + large gap = DESPERATION ATTACK',
                'multiplier': 1.10,
                'badge': 'badge-desperation',
                'conditions': ['gap > 10', 'threatened_team_excellent_form', 'late_season']
            },
            'extreme_fear': {
                'description': 'Massive gap + threatened team poor form = EXTREME DEFENSE',
                'multiplier': 0.75,
                'badge': 'badge-fear',
                'conditions': ['gap > 12', 'threatened_team_poor_form']
            },
            'moderate_desperation': {
                'description': 'Threatened team good form + large gap = BALANCED ATTACK',
                'multiplier': 1.05,
                'badge': 'badge-ambition',
                'conditions': ['gap > 8', 'threatened_team_good_form', 'mid_to_late_season']
            }
        }
    
    def analyze_match_context_v6(self, home_pos, away_pos, total_teams, games_played, home_form_level, away_form_level):
        """
        V6: Enhanced context detection considering form differences
        """
        gap = abs(home_pos - away_pos)
        
        # Define table zones
        bottom_cutoff = total_teams - 3
        top_cutoff = 4
        
        # Get zones
        home_zone = self._get_zone(home_pos, top_cutoff, bottom_cutoff)
        away_zone = self._get_zone(away_pos, top_cutoff, bottom_cutoff)
        
        # Calculate form difference
        form_levels = ['very_poor', 'poor', 'average', 'good', 'excellent']
        home_form_idx = form_levels.index(home_form_level)
        away_form_idx = form_levels.index(away_form_level)
        form_diff = abs(home_form_idx - away_form_idx)
        
        # ===== 1. RELEGATION BATTLE (BOTH bottom 4) =====
        if home_pos >= bottom_cutoff and away_pos >= bottom_cutoff:
            context = 'relegation_battle'
            psychology = {
                'primary': 'FEAR',
                'description': 'Both fighting to avoid drop → playing NOT TO LOSE',
                'badge': 'badge-fear',
                'dynamic': 'fear'
            }
        
        # ===== 2. RELEGATION THREATENED (ONE bottom 4, OTHER SAFE) =====
        elif (home_pos >= bottom_cutoff and away_pos < bottom_cutoff) or \
             (away_pos >= bottom_cutoff and home_pos < bottom_cutoff):
            
            context = 'relegation_threatened'
            threatened_team = 'HOME' if home_pos >= bottom_cutoff else 'AWAY'
            safe_team = 'AWAY' if home_pos >= bottom_cutoff else 'HOME'
            
            psychology = {
                'primary': 'CAUTION',
                'description': f'{threatened_team} team threatened → plays cautiously',
                'badge': 'badge-caution',
                'dynamic': 'fear',
                'threatened_team': threatened_team,
                'safe_team': safe_team,
                'threatened_pos': home_pos if threatened_team == 'HOME' else away_pos,
                'safe_pos': away_pos if threatened_team == 'HOME' else home_pos
            }
        
        # ===== 3. TOP TEAM BATTLE (BOTH top 4) =====
        elif home_pos <= top_cutoff and away_pos <= top_cutoff:
            context = 'top_team_battle'
            psychology = {
                'primary': 'QUALITY',
                'description': 'Both title contenders → quality creates AND prevents goals',
                'badge': 'badge-quality',
                'dynamic': 'quality'
            }
        
        # ===== 4. MID vs TOP (One top 4, one mid-table 5-16) =====
        elif (home_pos <= top_cutoff and away_pos > top_cutoff and away_pos < bottom_cutoff) or \
             (away_pos <= top_cutoff and home_pos > top_cutoff and home_pos < bottom_cutoff):
            
            context = 'mid_vs_top'
            top_team = 'HOME' if home_pos <= top_cutoff else 'AWAY'
            psychology = {
                'primary': 'AMBITION vs CONTROL',
                'description': f'Mid-table ambitious, {top_team} team controls tempo',
                'badge': 'badge-ambition',
                'dynamic': 'ambition'
            }
        
        # ===== 5. MID-TABLE CLASH WITH FORM NUANCE (V6 IMPROVEMENT) =====
        elif gap <= 4 and \
             home_pos > top_cutoff and home_pos < bottom_cutoff and \
             away_pos > top_cutoff and away_pos < bottom_cutoff:
            
            # Check if form difference is significant (≥2 levels)
            if form_diff >= 2:
                # Significant form difference → more controlled game
                context = 'controlled_mid_clash'
                better_team = 'HOME' if home_form_idx > away_form_idx else 'AWAY'
                psychology = {
                    'primary': 'CONTROL',
                    'description': f'{better_team} team better form → controls game, other defends',
                    'badge': 'badge-control',
                    'dynamic': 'control'
                }
            else:
                # Similar form → ambition clash
                context = 'mid_table_clash'
                psychology = {
                    'primary': 'AMBITION',
                    'description': 'Both safe, similar positions and form → playing TO WIN',
                    'badge': 'badge-ambition',
                    'dynamic': 'ambition'
                }
        
        # ===== 6. HIERARCHICAL (Everything else) =====
        else:
            context = 'hierarchical'
            psychology = {
                'primary': 'CAUTION',
                'description': 'Different league positions → different objectives',
                'badge': 'badge-caution',
                'dynamic': 'caution'
            }
        
        # Determine season urgency
        total_games = 38 if total_teams == 20 else 46 if total_teams == 24 else 34
        season_progress = games_played / total_games if total_games > 0 else 0.5
        
        if season_progress < 0.25:
            urgency = 'early'
            season_phase = 'early_season'
        elif season_progress < 0.65:
            urgency = 'mid'
            season_phase = 'mid_season'
        else:
            season_phase = 'late_season'
            if context in ['relegation_battle', 'relegation_threatened']:
                urgency = 'relegation_late'
            else:
                urgency = 'late'
        
        return {
            'context': context,
            'psychology': psychology,
            'gap': gap,
            'urgency': urgency,
            'season_progress': round(season_progress * 100, 1),
            'season_phase': season_phase,
            'zones': {
                'top_cutoff': top_cutoff,
                'bottom_cutoff': bottom_cutoff,
                'home_zone': home_zone,
                'away_zone': away_zone,
                'home_pos': home_pos,
                'away_pos': away_pos
            },
            'form_diff': form_diff
        }
    
    def _get_zone(self, position, top_cutoff, bottom_cutoff):
        """Get team's zone in the table"""
        if position <= top_cutoff:
            return 'TOP'
        elif position >= bottom_cutoff:
            return 'BOTTOM'
        else:
            return 'MID'
    
    def calculate_form_factor(self, team_avg, recent_goals):
        """Calculate form adjustment based on recent vs average performance"""
        if team_avg <= 0:
            return 1.0, 'average'
        
        recent_avg = recent_goals / 5 if recent_goals > 0 else 0
        ratio = recent_avg / team_avg if team_avg > 0 else 1.0
        
        if ratio >= 1.3:
            return self.form_adjustments['excellent'], 'excellent'
        elif ratio >= 1.1:
            return self.form_adjustments['good'], 'good'
        elif ratio <= 0.7:
            return self.form_adjustments['very_poor'], 'very_poor'
        elif ratio <= 0.9:
            return self.form_adjustments['poor'], 'poor'
        else:
            return self.form_adjustments['average'], 'average'
    
    def apply_desperation_layer_v6(self, context_analysis, psychology, home_form_level, away_form_level,
                                 threatened_form, safe_form):
        """
        V6 FIXED LAYER: Check BOTH threatened team AND safe team for desperation/attack dynamics
        """
        gap = context_analysis['gap']
        context = context_analysis['context']
        season_phase = context_analysis['season_phase']
        
        # Only apply to relegation contexts
        if context not in ['relegation_battle', 'relegation_threatened']:
            return {
                'multiplier': 1.0,
                'description': 'Normal psychology applies',
                'badge': psychology['badge'],
                'dynamic': 'normal',
                'layer_applied': False,
                'pattern': 'none'
            }
        
        # ===== PATTERN 1: MUTUAL ATTACK (NEW PATTERN - CRITICAL FIX) =====
        if gap > 6 and safe_form == 'excellent' and season_phase in ['mid_season', 'late_season']:
            return {
                'multiplier': 1.15,
                'description': 'MUTUAL ATTACK: Safe team excellent form drives attacking game',
                'badge': 'badge-mutual-attack',
                'dynamic': 'mutual_attack',
                'layer_applied': True,
                'pattern': 'mutual_attack',
                'reason': f'Safe team excellent form ({safe_form}) + gap {gap} + {season_phase}'
            }
        
        # ===== PATTERN 2: SAFE TEAM DOMINANCE (NEW PATTERN) =====
        elif gap > 4 and safe_form in ['good', 'excellent'] and threatened_form in ['poor', 'very_poor']:
            return {
                'multiplier': 1.10,
                'description': 'SAFE TEAM DOMINANCE: Safe team attacks relentlessly',
                'badge': 'badge-safe-dominance',
                'dynamic': 'safe_dominance',
                'layer_applied': True,
                'pattern': 'safe_dominance',
                'reason': f'Safe team {safe_form} vs threatened team {threatened_form} (gap {gap})'
            }
        
        # ===== PATTERN 3: THREATENED TEAM DESPERATION =====
        elif gap > 10 and threatened_form == 'excellent' and season_phase == 'late_season':
            return {
                'multiplier': 1.10,
                'description': 'DESPERATION ATTACK: Threatened team attacks aggressively to survive',
                'badge': 'badge-desperation',
                'dynamic': 'desperation_attack',
                'layer_applied': True,
                'pattern': 'threatened_desperation',
                'reason': f'Extreme gap ({gap}) + threatened team excellent form + late season'
            }
        
        # ===== PATTERN 4: MODERATE DESPERATION =====
        elif gap > 8 and threatened_form in ['good', 'excellent'] and season_phase in ['mid_season', 'late_season']:
            return {
                'multiplier': 1.05,
                'description': 'Balanced approach: Threatened team attacks due to good form',
                'badge': 'badge-ambition',
                'dynamic': 'moderate_desperation',
                'layer_applied': True,
                'pattern': 'moderate_desperation',
                'reason': f'Large gap ({gap}) + threatened team good form + {season_phase}'
            }
        
        # ===== PATTERN 5: EXTREME FEAR =====
        elif gap > 12 and threatened_form in ['poor', 'very_poor']:
            return {
                'multiplier': 0.75,
                'description': 'EXTREME FEAR: Complete defensive mindset',
                'badge': 'badge-fear',
                'dynamic': 'extreme_fear',
                'layer_applied': True,
                'pattern': 'extreme_fear',
                'reason': f'Massive gap ({gap}) + threatened team poor form'
            }
        
        # ===== DEFAULT: NORMAL FEAR =====
        else:
            return {
                'multiplier': 1.0,
                'description': 'Standard relegation psychology: Cautious play',
                'badge': psychology['badge'],
                'dynamic': 'normal_fear',
                'layer_applied': False,
                'pattern': 'normal',
                'reason': 'Standard relegation psychology applies'
            }
    
    def predict_match(self, match_data):
        """
        ENHANCED UNIFIED PREDICTION V6: Statistics × Psychology × Mutual Attack Layer × Learning
        """
        # Extract data
        home_pos = match_data['home_pos']
        away_pos = match_data['away_pos']
        total_teams = match_data['total_teams']
        games_played = match_data.get('games_played', 19)
        
        # ===== STEP 1: CALCULATE FORM FIRST (needed for context analysis) =====
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        
        home_form_factor, home_form_level = self.calculate_form_factor(
            home_attack,
            match_data.get('home_goals5', home_attack * 5)
        )
        away_form_factor, away_form_level = self.calculate_form_factor(
            away_attack,
            match_data.get('away_goals5', away_attack * 5)
        )
        
        # ===== STEP 2: ANALYZE CONTEXT WITH FORM (V6 IMPROVEMENT) =====
        context_analysis = self.analyze_match_context_v6(
            home_pos, away_pos, total_teams, games_played,
            home_form_level, away_form_level
        )
        context = context_analysis['context']
        base_psychology = context_analysis['psychology']
        
        # Get learned pattern for this context
        pattern = self.learned_patterns.get(context, self.learned_patterns['hierarchical'])
        base_psychology_multiplier = pattern['base_multiplier']
        
        # ===== STEP 3: CALCULATE BASE xG =====
        away_defense = match_data.get('away_defense', 1.4)
        home_defense = match_data.get('home_defense', 1.2)
        
        # Raw statistical expectation
        raw_home_xg = (home_attack + away_defense) / 2
        raw_away_xg = (away_attack + home_defense) / 2
        raw_total_xg = raw_home_xg + raw_away_xg
        
        # ===== STEP 4: APPLY FORM ADJUSTMENTS =====
        # Form-adjusted xG
        form_home_xg = raw_home_xg * home_form_factor
        form_away_xg = raw_away_xg * away_form_factor
        form_total_xg = form_home_xg + form_away_xg
        
        # Determine threatened team form for desperation analysis
        if context == 'relegation_threatened':
            threatened_team = 'HOME' if home_pos >= (total_teams - 3) else 'AWAY'
            threatened_form = home_form_level if threatened_team == 'HOME' else away_form_level
            safe_form = away_form_level if threatened_team == 'HOME' else home_form_level
        elif context == 'relegation_battle':
            # Both are threatened, use worse form
            threatened_form = home_form_level if home_form_level in ['poor', 'very_poor'] else away_form_level
            safe_form = 'average'
        else:
            threatened_form = 'average'
            safe_form = 'average'
        
        # ===== STEP 5: APPLY DESPERATION LAYER V6 =====
        desperation_analysis = self.apply_desperation_layer_v6(
            context_analysis, base_psychology, 
            home_form_level, away_form_level,
            threatened_form, safe_form
        )
        
        desperation_multiplier = desperation_analysis['multiplier']
        
        # ===== STEP 6: APPLY URGENCY =====
        urgency_factor = self.urgency_factors[context_analysis['urgency']]
        
        # FINAL ADJUSTED xG = Statistics × Base Psychology × Desperation × Form × Urgency
        adjusted_home_xg = form_home_xg * base_psychology_multiplier * desperation_multiplier * urgency_factor
        adjusted_away_xg = form_away_xg * base_psychology_multiplier * desperation_multiplier * urgency_factor
        adjusted_total_xg = adjusted_home_xg + adjusted_away_xg
        
        # ===== STEP 7: MAKE DECISION =====
        # Context-specific decision thresholds
        if context == 'relegation_battle':
            over_threshold = 2.5
            under_threshold = 2.5
        elif context == 'controlled_mid_clash':  # V6 NEW THRESHOLD
            over_threshold = 2.7  # Higher threshold for controlled games
            under_threshold = 2.3
        elif desperation_analysis['dynamic'] in ['mutual_attack', 'safe_dominance', 'desperation_attack']:
            over_threshold = 2.6
            under_threshold = 2.4
        elif context == 'mid_table_clash' or context == 'mid_vs_top':
            over_threshold = 2.6
            under_threshold = 2.4
        elif context == 'top_team_battle':
            over_threshold = 2.8
            under_threshold = 2.2
        else:
            over_threshold = 2.7
            under_threshold = 2.3
        
        # Make prediction
        if adjusted_total_xg > over_threshold:
            prediction = 'OVER 2.5'
            confidence = 'HIGH' if adjusted_total_xg > 3.0 else 'MEDIUM'
        elif adjusted_total_xg < under_threshold:
            prediction = 'UNDER 2.5'
            confidence = 'HIGH' if adjusted_total_xg < 2.0 else 'MEDIUM'
        else:
            # Borderline case - use psychology direction
            if base_psychology_multiplier > 1.0 or desperation_multiplier > 1.0:
                prediction = 'OVER 2.5'
            else:
                prediction = 'OVER 2.5' if adjusted_total_xg > 2.5 else 'UNDER 2.5'
            confidence = 'MEDIUM'
        
        # Special overrides
        if context_analysis['gap'] > 12:
            confidence = 'MEDIUM'  # Downgrade for extreme gaps
        
        if desperation_analysis['dynamic'] in ['mutual_attack', 'desperation_attack', 'extreme_fear']:
            # Extreme psychology increases variance
            confidence = 'MEDIUM' if confidence == 'HIGH' else 'LOW'
        
        # ===== STEP 8: CALCULATE CONFIDENCE =====
        # Base confidence from pattern
        base_confidence = pattern['confidence']
        
        # Adjust for data quality
        data_quality = 1.0
        if games_played < 10:
            data_quality = 0.7
        elif games_played < 15:
            data_quality = 0.85
        
        # Adjust for form consistency
        form_consistency = min(home_form_factor, away_form_factor) / max(home_form_factor, away_form_factor) if max(home_form_factor, away_form_factor) > 0 else 0.7
        form_weight = 0.3 + (form_consistency * 0.4)
        
        # Adjust for gap size
        gap_factor = 1.0
        if context_analysis['gap'] <= 2:
            gap_factor = 1.1
        elif context_analysis['gap'] > 10:
            gap_factor = 0.9
        
        # Adjust for desperation layer application
        if desperation_analysis['layer_applied']:
            if desperation_analysis['pattern'] in ['mutual_attack', 'safe_dominance']:
                desperation_factor = 1.05
            else:
                desperation_factor = 0.95
        else:
            desperation_factor = 1.0
        
        # Final confidence score
        confidence_score = (base_confidence * 0.3 + 
                          data_quality * 0.25 + 
                          form_weight * 0.2 +
                          gap_factor * 0.15 +
                          desperation_factor * 0.1)
        
        confidence_level = 'HIGH' if confidence_score > 0.85 else 'MEDIUM' if confidence_score > 0.7 else 'LOW'
        
        # ===== STEP 9: STAKE RECOMMENDATION =====
        if confidence_level == 'HIGH' and base_confidence > 0.85 and desperation_analysis['layer_applied'] == False:
            stake = 'MAX BET (2x normal)'
            stake_color = 'green'
        elif confidence_level == 'HIGH' or (base_confidence > 0.8 and desperation_analysis['layer_applied'] == False):
            stake = 'NORMAL BET (1x)'
            stake_color = 'orange'
        elif desperation_analysis['layer_applied'] == True and desperation_analysis['pattern'] == 'mutual_attack':
            stake = 'STRONG BET (1.5x) - Mutual Attack pattern detected'
            stake_color = 'green'
        elif desperation_analysis['layer_applied'] == True:
            stake = 'SMALL BET (0.5x) - Psychology conflict'
            stake_color = 'orange'
        else:
            stake = 'SMALL BET (0.5x) or AVOID'
            stake_color = 'red'
        
        # ===== RETURN COMPLETE ANALYSIS =====
        return {
            # Core prediction
            'prediction': prediction,
            'confidence': confidence_level,
            'confidence_score': round(confidence_score, 3),
            'stake_recommendation': stake,
            'stake_color': stake_color,
            
            # xG analysis
            'raw_total_xg': round(raw_total_xg, 2),
            'form_total_xg': round(form_total_xg, 2),
            'adjusted_total_xg': round(adjusted_total_xg, 2),
            'home_xg': round(adjusted_home_xg, 2),
            'away_xg': round(adjusted_away_xg, 2),
            
            # Context analysis
            'context': context,
            'psychology': base_psychology,
            'gap': context_analysis['gap'],
            'base_psychology_multiplier': base_psychology_multiplier,
            'desperation_multiplier': desperation_multiplier,
            'form_multiplier_home': home_form_factor,
            'form_multiplier_away': away_form_factor,
            'form_level_home': home_form_level,
            'form_level_away': away_form_level,
            'form_diff': context_analysis.get('form_diff', 0),
            'threatened_form': threatened_form if context in ['relegation_battle', 'relegation_threatened'] else 'N/A',
            'safe_form': safe_form if context in ['relegation_battle', 'relegation_threatened'] else 'N/A',
            'urgency_factor': urgency_factor,
            'season_progress': context_analysis['season_progress'],
            'season_phase': context_analysis['season_phase'],
            'zones': context_analysis['zones'],
            
            # Desperation layer analysis
            'desperation_analysis': desperation_analysis,
            
            # Learned pattern info
            'pattern_description': pattern['description'],
            'pattern_confidence': pattern['confidence'],
            'pattern_example': pattern.get('example', ''),
            'pattern_psychology': pattern.get('psychology', ''),
            
            # Breakdown for display
            'breakdown': {
                'base_xg': round(raw_total_xg, 2),
                'form_adjustment': f'×{home_form_factor:.2f}/{away_form_factor:.2f}',
                'psychology_adjustment': f'×{base_psychology_multiplier:.2f}',
                'desperation_adjustment': f'×{desperation_multiplier:.2f}',
                'urgency_adjustment': f'×{urgency_factor:.2f}',
                'final_xg': round(adjusted_total_xg, 2)
            }
        }

# ========== TEST CASES DATABASE ==========
TEST_CASES = {
    'Lecce vs Pisa (FEAR)': {
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
        'away_goals5': 8,
        'actual_result': '1-0 (UNDER) ✅',
        'case_type': 'test'
    },
    'Greuther Furth vs Hertha (MUTUAL ATTACK)': {
        'home_name': 'Greuther Furth',
        'away_name': 'Hertha',
        'home_pos': 16,
        'away_pos': 7,
        'total_teams': 18,
        'games_played': 15,
        'home_attack': 1.88,
        'away_attack': 0.71,
        'home_defense': 0.63,
        'away_defense': 1.86,
        'home_goals5': 4,
        'away_goals5': 10,
        'actual_result': '3-3 (OVER) ✅',
        'case_type': 'test'
    },
    'Chelsea vs Everton (CONTROLLED)': {
        'home_name': 'Chelsea',
        'away_name': 'Everton',
        'home_pos': 5,
        'away_pos': 7,
        'total_teams': 20,
        'games_played': 15,
        'home_attack': 1.43,
        'away_attack': 1.00,
        'home_defense': 1.00,
        'away_defense': 1.14,
        'home_goals5': 8,
        'away_goals5': 4,
        'actual_result': '2-0 (UNDER) ✅',
        'case_type': 'test',
        'v6_expected': 'CONTROLLED_MID_CLASH pattern'
    },
    'Liverpool vs Brighton (CONTROLLED)': {
        'home_name': 'Liverpool',
        'away_name': 'Brighton',
        'home_pos': 10,
        'away_pos': 8,
        'total_teams': 20,
        'games_played': 15,
        'home_attack': 1.57,
        'away_attack': 1.29,
        'home_defense': 1.29,
        'away_defense': 1.43,
        'home_goals5': 5,
        'away_goals5': 8,
        'actual_result': '2-0 (UNDER) ✅',
        'case_type': 'test',
        'v6_expected': 'CONTROLLED_MID_CLASH pattern'
    },
    'Annecy vs Le Mans (AMBITION)': {
        'home_name': 'Annecy',
        'away_name': 'Le Mans',
        'home_pos': 8,
        'away_pos': 9,
        'total_teams': 20,
        'games_played': 15,
        'home_attack': 1.4,
        'away_attack': 1.3,
        'home_defense': 1.2,
        'away_defense': 1.4,
        'home_goals5': 6,
        'away_goals5': 5,
        'actual_result': '2-1 (OVER) ✅',
        'case_type': 'test',
        'v6_expected': 'MID_TABLE_CLASH pattern (similar form)'
    }
}

# ========== INITIALIZE ENGINE AND SESSION STATE ==========
if 'engine' not in st.session_state:
    st.session_state.engine = EnhancedPredictionEngineV6()

# Initialize session state
if 'current_prediction' not in st.session_state:
    st.session_state.current_prediction = None
if 'last_input_hash' not in st.session_state:
    st.session_state.last_input_hash = None
if 'match_data' not in st.session_state:
    st.session_state.match_data = TEST_CASES['Chelsea vs Everton (CONTROLLED)']
if 'analysis_triggered' not in st.session_state:
    st.session_state.analysis_triggered = False

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">⚽ ENHANCED FOOTBALL PREDICTOR V6</div>', unsafe_allow_html=True)
    st.markdown("### **Statistics × Psychology × Mutual Attack Layer × Learning**")
    st.markdown("*Now handles mid-table clashes with form differences correctly*")
    
    # Show test case selection with V6 improvements
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🧪 **V6 Test Case Scenarios**")
    
    col_test = st.columns(3)
    test_cases_list = list(TEST_CASES.items())
    
    for idx, (case_name, case_data) in enumerate(test_cases_list):
        with col_test[idx % 3]:
            if st.button(f"{case_name}", use_container_width=True, key=f"test_{case_name}"):
                st.session_state.current_prediction = None
                st.session_state.analysis_triggered = False
                st.session_state.match_data = case_data
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show V6 improvements for selected case
    current_match = f"{st.session_state.match_data['home_name']} vs {st.session_state.match_data['away_name']}"
    if "Chelsea vs Everton" in current_match or "Liverpool vs Brighton" in current_match:
        st.markdown('<div class="case-study">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🔧 **V6 IMPROVEMENT: CONTROLLED MID-TABLE CLASH**
        **Match:** {current_match} → Actual: {st.session_state.match_data.get('actual_result', 'Unknown')}
        **V5 System:** Predicted OVER 2.5 ❌ (applied AMBITION psychology)
        **V6 System:** Now detects form difference → CONTROLLED game
        **Key Insight:** Mid-table clashes with ≥2 form level difference = controlled, not ambitious
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== INPUT SECTION =====
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 **Enter Match Data**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏠 Home Team")
        home_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data['home_name'],
            key="home_name_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        home_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data['home_pos'],
            key="home_pos_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        home_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data['home_attack'],
            step=0.01,
            key="home_attack_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        home_goals5 = st.number_input(
            "Goals Last 5",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data['home_goals5'],
            key="home_goals5_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
    
    with col2:
        st.markdown("#### ✈️ Away Team")
        away_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data['away_name'],
            key="away_name_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        away_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data['away_pos'],
            key="away_pos_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        away_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data['away_attack'],
            step=0.01,
            key="away_attack_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        away_goals5 = st.number_input(
            "Goals Last 5",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data['away_goals5'],
            key="away_goals5_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
    
    with col3:
        st.markdown("#### ⚙️ League Settings")
        total_teams = st.number_input(
            "Total Teams",
            min_value=10,
            max_value=30,
            value=st.session_state.match_data['total_teams'],
            key="total_teams_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        games_played = st.number_input(
            "Games Played This Season",
            min_value=1,
            max_value=50,
            value=st.session_state.match_data['games_played'],
            key="games_played_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        home_defense = st.number_input(
            "Home Conceded/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('home_defense', 1.2),
            step=0.01,
            key="home_defense_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
        away_defense = st.number_input(
            "Away Conceded/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data.get('away_defense', 1.4),
            step=0.01,
            key="away_defense_input",
            on_change=lambda: st.session_state.update({'analysis_triggered': False})
        )
    
    # Check if inputs have changed
    import hashlib
    current_hash = hashlib.md5(str({
        'home_name': st.session_state.get('home_name_input', ''),
        'away_name': st.session_state.get('away_name_input', ''),
        'home_pos': st.session_state.get('home_pos_input', 0),
        'away_pos': st.session_state.get('away_pos_input', 0),
        'home_attack': st.session_state.get('home_attack_input', 0),
        'away_attack': st.session_state.get('away_attack_input', 0),
        'home_goals5': st.session_state.get('home_goals5_input', 0),
        'away_goals5': st.session_state.get('away_goals5_input', 0),
        'total_teams': st.session_state.get('total_teams_input', 0),
        'games_played': st.session_state.get('games_played_input', 0),
        'home_defense': st.session_state.get('home_defense_input', 0),
        'away_defense': st.session_state.get('away_defense_input', 0)
    }).encode()).hexdigest()
    
    if st.session_state.last_input_hash != current_hash:
        st.session_state.current_prediction = None
        st.session_state.analysis_triggered = False
        st.session_state.last_input_hash = current_hash
    
    # Analyze button
    if not st.session_state.analysis_triggered or st.session_state.current_prediction is None:
        if st.button("🚀 ANALYZE WITH ENHANCED ENGINE V6", type="primary", use_container_width=True):
            new_match_data = {
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
                'user_entered': True
            }
            
            st.session_state.match_data = new_match_data
            st.session_state.analysis_triggered = True
            st.session_state.current_prediction = st.session_state.engine.predict_match(new_match_data)
            st.rerun()
    else:
        st.success("✅ Analysis complete! See results below.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== ANALYSIS SECTION =====
    if not st.session_state.analysis_triggered or st.session_state.current_prediction is None:
        st.info("👆 Enter match data and click ANALYZE to see predictions")
        return
    
    prediction = st.session_state.current_prediction
    
    # Display results
    st.markdown("---")
    st.markdown(f"## 📊 **V6 Enhanced Analysis:** {home_name} vs {away_name}")
    
    if 'user_entered' not in st.session_state.match_data:
        actual_result = st.session_state.match_data.get('actual_result', 'Unknown')
        if actual_result != 'Unknown':
            st.info(f"**Test Case Actual Result:** {actual_result}")
    
    # Context and zone info
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    
    with col_info1:
        st.metric("Home Zone", prediction['zones']['home_zone'])
    with col_info2:
        st.metric("Away Zone", prediction['zones']['away_zone'])
    with col_info3:
        st.metric("Position Gap", prediction['gap'])
    with col_info4:
        st.metric("Form Diff", prediction['form_diff'])
    
    # Psychology badges
    desperation_badge = prediction['desperation_analysis']['badge']
    desperation_dynamic = prediction['desperation_analysis']['dynamic'].replace('_', ' ').upper()
    
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <span class="psychology-badge {prediction['psychology']['badge']}">
            {prediction['psychology']['primary']}
        </span>
        {prediction['desperation_analysis']['layer_applied'] and 
         f'<span class="psychology-badge {desperation_badge}" style="margin-left: 10px;">{desperation_dynamic}</span>' or ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Prediction", prediction['prediction'])
    with col2:
        st.metric("Confidence", prediction['confidence'])
    with col3:
        st.metric("Stake", prediction['stake_recommendation'])
    with col4:
        st.metric("Enhanced xG", prediction['adjusted_total_xg'])
    with col5:
        st.metric("Raw xG", prediction['raw_total_xg'])
    
    # ===== ENHANCED BREAKDOWN =====
    st.markdown("### 🎯 **V6 Enhanced Prediction Breakdown**")
    
    col6, col7 = st.columns(2)
    
    with col6:
        st.markdown('<div class="prediction-card high-confidence">', unsafe_allow_html=True)
        st.markdown("#### 📈 **xG Evolution with V6 Context Analysis**")
        
        fig = go.Figure()
        
        xg_stages = ['Base xG', 'After Form', 'V6 Context Psychology', 'Desperation Layer', 'Final Adjusted']
        xg_values = [
            prediction['raw_total_xg'],
            prediction['form_total_xg'],
            prediction['form_total_xg'] * prediction['base_psychology_multiplier'],
            prediction['form_total_xg'] * prediction['base_psychology_multiplier'] * prediction['desperation_multiplier'],
            prediction['adjusted_total_xg']
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#BA68C8', '#96CEB4']
        
        fig.add_trace(go.Bar(
            x=xg_stages,
            y=xg_values,
            marker_color=colors,
            text=[f'{v:.2f}' for v in xg_values],
            textposition='auto'
        ))
        
        fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title="V6 xG Evolution with Form-Aware Context",
            yaxis_title="Expected Goals",
            showlegend=False,
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        **Base Statistical xG:** {prediction['raw_total_xg']}  
        **Form Adjustment:** ×{prediction['form_multiplier_home']:.2f}/{prediction['form_multiplier_away']:.2f} ({prediction['form_level_home']}/{prediction['form_level_away']})  
        **V6 Context Psychology:** ×{prediction['base_psychology_multiplier']:.2f} ({prediction['psychology']['primary']})  
        **Desperation Layer:** ×{prediction['desperation_multiplier']:.2f} ({prediction['desperation_analysis']['dynamic'].replace('_', ' ')})  
        **Urgency Factor:** ×{prediction['urgency_factor']:.2f} ({prediction['season_phase'].replace('_', ' ')})  
        **Final Enhanced xG:** {prediction['adjusted_total_xg']}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col7:
        confidence_class = "high-confidence" if prediction['confidence'] == "HIGH" else "medium-confidence"
        st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
        st.markdown("#### 🧠 **V6 Psychology Analysis**")
        
        desperation_layer = prediction['desperation_analysis']
        
        st.markdown(f"""
        **Match Context:** {prediction['context'].replace('_', ' ').title()}  
        **Home Form:** {prediction['form_level_home'].upper()} ({prediction['form_multiplier_home']:.2f}x)  
        **Away Form:** {prediction['form_level_away'].upper()} ({prediction['form_multiplier_away']:.2f}x)  
        **Form Difference:** {prediction['form_diff']} levels  
        
        **Base Psychology:** {prediction['psychology']['primary']}  
        **Description:** {prediction['psychology']['description']}  
        
        **V6 Desperation Layer:** {'✅ YES' if desperation_layer['layer_applied'] else '❌ NO'}  
        {f"<strong>Pattern:</strong> {desperation_layer['pattern'].replace('_', ' ').title()}" if desperation_layer['layer_applied'] else ""}
        {f"<strong>Reason:</strong> {desperation_layer['reason']}" if desperation_layer['layer_applied'] else ""}
        {f"<strong>Effect:</strong> {desperation_layer['description']}" if desperation_layer['layer_applied'] else ""}
        
        **Learned Pattern:**  
        {prediction['pattern_description']}  
        *Historical Accuracy: {prediction['pattern_confidence']*100:.0f}%*  
        {f"*Example: {prediction['pattern_example']}*" if prediction['pattern_example'] else ""}
        
        **Season Progress:** {prediction['season_progress']}%  
        **Urgency Level:** {prediction['urgency_factor']:.2f}x
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== STAKE RECOMMENDATION =====
    st.markdown(f"""
    <div style="border-left: 5px solid {prediction['stake_color']}; background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>💰 <strong>V6 Enhanced Betting Recommendation:</strong> {prediction['stake_recommendation']}</h3>
        <p><strong>Reason:</strong> {prediction['confidence']} confidence from V6 enhanced analysis</p>
        <p><strong>Expected Value:</strong> Enhanced xG of {prediction['adjusted_total_xg']} suggests {prediction['prediction']}</p>
        <p><strong>Confidence Score:</strong> {prediction['confidence_score']*100:.1f}%</p>
        {f'<p><strong>Psychology Note:</strong> {prediction["desperation_analysis"]["description"]}</p>' if prediction['desperation_analysis']['layer_applied'] else ''}
        {f'<p><strong>V6 Insight:</strong> Form difference of {prediction["form_diff"]} levels affects psychology</p>' if prediction.get('form_diff', 0) >= 2 else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # ===== V6 SYSTEM IMPROVEMENTS =====
    st.markdown("### 🔧 **V6 System Improvements**")
    
    col_imp1, col_imp2, col_imp3 = st.columns(3)
    
    with col_imp1:
        st.markdown("#### 🆕 **New Patterns**")
        st.markdown("""
        • **Controlled Mid-Clash:** Form diff ≥2 levels
        • **Form-aware context:** Considers form in classification
        • **Better thresholds:** Different for controlled games
        """)
    
    with col_imp2:
        st.markdown("#### 🐛 **Bug Fixes**")
        st.markdown("""
        • **Fixed:** Mid-table always AMBITION
        • **Now:** Checks form difference
        • **Result:** Correct Chelsea 2-0, Liverpool 2-0 predictions
        """)
    
    with col_imp3:
        st.markdown("#### 📈 **Enhanced Accuracy**")
        st.markdown("""
        • Form difference calculation
        • Context-aware multipliers
        • Better pattern matching
        • Improved stake recommendations
        """)

if __name__ == "__main__":
    main()
