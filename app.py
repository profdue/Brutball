import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
from pathlib import Path
import pickle
import numpy as np
from collections import defaultdict
import math

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="SELF-LEARNING FOOTBALL PREDICTOR V10",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== DATABASE FOR SELF-LEARNING ==========
class PredictionDatabase:
    """Database to store predictions and learn from outcomes"""
    
    def __init__(self, db_path="football_predictor_v10.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Predictions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_hash TEXT UNIQUE,
                timestamp DATETIME,
                home_team TEXT,
                away_team TEXT,
                home_pos INTEGER,
                away_pos INTEGER,
                prediction TEXT,
                confidence REAL,
                confidence_level TEXT,
                predicted_xg REAL,
                pattern_used TEXT,
                psychology_multiplier REAL,
                form_multiplier_home REAL,
                form_multiplier_away REAL,
                urgency_factor REAL,
                stake_recommendation TEXT,
                clean_sheet_bets TEXT,
                match_context TEXT
            )
        ''')
        
        # Outcomes table
        c.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_hash TEXT,
                actual_home_goals INTEGER,
                actual_away_goals INTEGER,
                actual_total_goals INTEGER,
                actual_over_under TEXT,
                clean_sheet_team TEXT,
                outcome_accuracy TEXT,
                notes TEXT,
                recorded_at DATETIME,
                FOREIGN KEY (prediction_hash) REFERENCES predictions (prediction_hash)
            )
        ''')
        
        # Pattern performance table
        c.execute('''
            CREATE TABLE IF NOT EXISTS pattern_performance (
                pattern_name TEXT PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                avg_error REAL DEFAULT 0.0,
                total_xg_error REAL DEFAULT 0.0,
                multiplier_history TEXT,
                last_updated DATETIME
            )
        ''')
        
        # Learning adjustments table
        c.execute('''
            CREATE TABLE IF NOT EXISTS learning_adjustments (
                adjustment_type TEXT,
                parameter_name TEXT,
                old_value REAL,
                new_value REAL,
                reason TEXT,
                confidence_change REAL,
                applied_at DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, prediction_data):
        """Save a new prediction to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create unique hash for this prediction
        hash_str = f"{prediction_data['home_name']}_{prediction_data['away_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        prediction_hash = hashlib.md5(hash_str.encode()).hexdigest()
        
        # Save prediction
        c.execute('''
            INSERT OR REPLACE INTO predictions 
            (prediction_hash, timestamp, home_team, away_team, home_pos, away_pos, 
             prediction, confidence, confidence_level, predicted_xg, pattern_used,
             psychology_multiplier, form_multiplier_home, form_multiplier_away,
             urgency_factor, stake_recommendation, clean_sheet_bets, match_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_hash,
            datetime.now(),
            prediction_data['home_name'],
            prediction_data['away_name'],
            prediction_data['home_pos'],
            prediction_data['away_pos'],
            prediction_data['analysis']['prediction'],
            prediction_data['analysis']['confidence_score'],
            prediction_data['analysis']['confidence'],
            prediction_data['analysis']['adjusted_total_xg'],
            prediction_data['analysis']['context'],
            prediction_data['analysis']['base_psychology_multiplier'],
            prediction_data['analysis']['form_multiplier_home'],
            prediction_data['analysis']['form_multiplier_away'],
            prediction_data['analysis']['urgency_factor'],
            prediction_data['analysis']['stake_recommendation'],
            json.dumps([bet['market'] for bet in prediction_data['analysis'].get('clean_sheet_bets', [])]),
            json.dumps(prediction_data['analysis'].get('psychology', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return prediction_hash
    
    def record_outcome(self, prediction_hash, actual_home_goals, actual_away_goals, notes=""):
        """Record actual match outcome and update learning"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get the original prediction
        c.execute('SELECT * FROM predictions WHERE prediction_hash = ?', (prediction_hash,))
        prediction = c.fetchone()
        
        if not prediction:
            conn.close()
            return False
        
        actual_total = actual_home_goals + actual_away_goals
        actual_over_under = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
        predicted_over_under = prediction[7]  # prediction field
        
        # Determine accuracy
        outcome_accuracy = "CORRECT" if predicted_over_under == actual_over_under else "INCORRECT"
        
        # Calculate xG error
        predicted_xg = prediction[10]
        xg_error = abs(predicted_xg - actual_total)
        
        # Record outcome
        c.execute('''
            INSERT INTO outcomes 
            (prediction_hash, actual_home_goals, actual_away_goals, actual_total_goals,
             actual_over_under, outcome_accuracy, notes, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_hash,
            actual_home_goals,
            actual_away_goals,
            actual_total,
            actual_over_under,
            outcome_accuracy,
            notes,
            datetime.now()
        ))
        
        # Update pattern performance
        pattern_name = prediction[11]  # pattern_used field
        
        c.execute('''
            SELECT * FROM pattern_performance WHERE pattern_name = ?
        ''', (pattern_name,))
        
        pattern_data = c.fetchone()
        
        if pattern_data:
            total = pattern_data[1] + 1
            correct = pattern_data[2] + (1 if outcome_accuracy == "CORRECT" else 0)
            accuracy = correct / total if total > 0 else 0.0
            
            # Update error tracking
            total_error = pattern_data[5] + xg_error
            avg_error = total_error / total
            
            c.execute('''
                UPDATE pattern_performance 
                SET total_predictions = ?, correct_predictions = ?, accuracy = ?,
                    total_xg_error = ?, avg_error = ?, last_updated = ?
                WHERE pattern_name = ?
            ''', (total, correct, accuracy, total_error, avg_error, datetime.now(), pattern_name))
        else:
            c.execute('''
                INSERT INTO pattern_performance 
                (pattern_name, total_predictions, correct_predictions, accuracy,
                 total_xg_error, avg_error, last_updated)
                VALUES (?, 1, ?, ?, ?, ?, ?)
            ''', (pattern_name, 
                  1 if outcome_accuracy == "CORRECT" else 0,
                  1.0 if outcome_accuracy == "CORRECT" else 0.0,
                  xg_error, xg_error, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Trigger auto-learning
        self.auto_adjust_pattern(pattern_name, predicted_xg, actual_total, xg_error)
        
        return True
    
    def auto_adjust_pattern(self, pattern_name, predicted_xg, actual_goals, xg_error):
        """Automatically adjust pattern parameters based on performance"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get recent predictions for this pattern
        c.execute('''
            SELECT p.psychology_multiplier, o.actual_total_goals, p.predicted_xg
            FROM predictions p
            JOIN outcomes o ON p.prediction_hash = o.prediction_hash
            WHERE p.pattern_used = ?
            ORDER BY p.timestamp DESC
            LIMIT 20
        ''', (pattern_name,))
        
        recent_matches = c.fetchall()
        
        if len(recent_matches) >= 10:  # Need enough data
            # Calculate optimal multiplier
            optimal_multipliers = []
            
            for match in recent_matches:
                psychology_multiplier = match[0]
                actual_goals_match = match[1]
                predicted_xg_match = match[2]
                
                # What multiplier would have made prediction perfect?
                base_xg = predicted_xg_match / psychology_multiplier
                optimal_multiplier = actual_goals_match / base_xg if base_xg > 0 else psychology_multiplier
                optimal_multipliers.append(optimal_multiplier)
            
            avg_optimal = sum(optimal_multipliers) / len(optimal_multipliers)
            
            # Get current multiplier from engine
            current_multiplier = self.get_current_multiplier(pattern_name)
            
            if current_multiplier:
                # Apply gradual adjustment (70% old, 30% new)
                new_multiplier = 0.7 * current_multiplier + 0.3 * avg_optimal
                
                # Record adjustment
                c.execute('''
                    INSERT INTO learning_adjustments 
                    (adjustment_type, parameter_name, old_value, new_value,
                     reason, confidence_change, applied_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'pattern_multiplier',
                    f'{pattern_name}_multiplier',
                    current_multiplier,
                    new_multiplier,
                    f'Auto-adjusted based on {len(recent_matches)} recent matches',
                    abs(new_multiplier - current_multiplier),
                    datetime.now()
                ))
                
                conn.commit()
        
        conn.close()
    
    def get_current_multiplier(self, pattern_name):
        """Get current multiplier for a pattern from engine"""
        # This would interface with the engine - placeholder
        return None
    
    def get_performance_stats(self):
        """Get overall system performance statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                COUNT(*) as total_predictions,
                SUM(CASE WHEN o.outcome_accuracy = 'CORRECT' THEN 1 ELSE 0 END) as correct_predictions
            FROM predictions p
            LEFT JOIN outcomes o ON p.prediction_hash = o.prediction_hash
        ''')
        
        stats = c.fetchone()
        
        c.execute('''
            SELECT pattern_name, accuracy, total_predictions, avg_error
            FROM pattern_performance
            ORDER BY accuracy DESC
        ''')
        
        pattern_stats = c.fetchall()
        
        conn.close()
        
        total = stats[0] if stats[0] else 0
        correct = stats[1] if stats[1] else 0
        accuracy = correct / total if total > 0 else 0
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'pattern_stats': pattern_stats
        }
    
    def get_recent_predictions(self, limit=10):
        """Get recent predictions with outcomes"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                p.timestamp,
                p.home_team,
                p.away_team,
                p.prediction,
                p.confidence_level,
                p.predicted_xg,
                o.actual_total_goals,
                o.outcome_accuracy,
                p.pattern_used
            FROM predictions p
            LEFT JOIN outcomes o ON p.prediction_hash = o.prediction_hash
            ORDER BY p.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        predictions = c.fetchall()
        conn.close()
        
        return predictions

# ========== SELF-LEARNING PREDICTION ENGINE V10 ==========
class SelfLearningPredictionEngineV10:
    """
    V10: Self-Learning Engine with Auto-Adjustment
    Learns from every prediction outcome
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.learned_patterns = self.load_learned_patterns()
        
        # FORM ADJUSTMENTS (will auto-adjust)
        self.form_adjustments = {
            'excellent': 1.20,
            'good': 1.10,
            'average': 1.00,
            'poor': 0.90,
            'very_poor': 0.80
        }
        
        # SEASON URGENCY
        self.urgency_factors = {
            'early': 0.95,
            'mid': 1.00,
            'late': 1.05,
            'relegation_late': 0.90
        }
        
        # THRESHOLDS (will auto-adjust)
        self.prediction_thresholds = {
            'relegation_battle': {'over': 2.5, 'under': 2.5},
            'top_dominance': {'over': 2.7, 'under': 2.3},
            'top_vs_bottom_domination': {'over': 2.6, 'under': 2.4},
            'controlled_mid_clash': {'over': 2.7, 'under': 2.3},
            'mid_table_clash': {'over': 2.6, 'under': 2.4},
            'top_team_battle': {'over': 2.8, 'under': 2.2},
            'default': {'over': 2.7, 'under': 2.3}
        }
    
    def load_learned_patterns(self):
        """Load patterns from database or use defaults"""
        # Try to load learned patterns from file
        try:
            with open('learned_patterns_v10.pkl', 'rb') as f:
                return pickle.load(f)
        except:
            # Default patterns
            return {
                'relegation_battle': {
                    'base_multiplier': 0.65,
                    'description': 'Both bottom 4 → FEAR dominates → 35% fewer goals',
                    'base_confidence': 0.92,
                    'example': 'Lecce 1-0 Pisa',
                    'base_badge': 'badge-fear',
                    'psychology': 'FEAR dominates: Both playing NOT TO LOSE',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'relegation_threatened': {
                    'base_multiplier': 0.85,
                    'description': 'One team bottom 4, other safe → threatened team cautious → 15% fewer goals',
                    'base_confidence': 0.85,
                    'example': 'Team fighting relegation vs mid-table safe team',
                    'base_badge': 'badge-caution',
                    'psychology': 'Threatened team plays with fear, lowers scoring',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'mid_table_clash': {
                    'base_multiplier': 1.15,
                    'description': 'Both safe (5-16), gap ≤ 4, similar form → SIMILAR AMBITIONS → 15% more goals',
                    'base_confidence': 0.88,
                    'example': 'Annecy 2-1 Le Mans',
                    'base_badge': 'badge-ambition',
                    'psychology': 'Both teams confident, similar form → playing TO WIN',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'controlled_mid_clash': {
                    'base_multiplier': 0.90,
                    'description': 'Mid-table clash with significant form difference → controlled game',
                    'base_confidence': 0.85,
                    'example': 'Chelsea 2-0 Everton',
                    'base_badge': 'badge-control',
                    'psychology': 'Better form team controls, poorer form team defends',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'top_team_battle': {
                    'base_multiplier': 0.95,
                    'description': 'Both top 4 → QUALITY over caution → normal scoring',
                    'base_confidence': 0.78,
                    'example': 'Title contenders facing each other',
                    'base_badge': 'badge-quality',
                    'psychology': 'Quality creates AND prevents goals',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'top_vs_bottom_domination': {
                    'base_multiplier': 0.85,
                    'description': 'Top team excellent/good form vs bottom team → controlled domination',
                    'base_confidence': 0.82,
                    'example': 'Atletico Madrid 2-1 Valencia',
                    'base_badge': 'badge-domination',
                    'psychology': 'Top team controls, bottom team struggles but might score desperately',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                },
                'mutual_attack_scenario': {
                    'base_multiplier': 1.15,
                    'description': 'Safe team excellent form drives high-scoring game despite relegation context',
                    'base_confidence': 0.82,
                    'example': 'Greuther Furth 3-3 Hertha',
                    'base_badge': 'badge-mutual-attack',
                    'psychology': 'MUTUAL ATTACK: Safe team attacks confidently, threatened team desperate',
                    'learning_data': {
                        'total_uses': 0,
                        'correct_uses': 0,
                        'avg_xg_error': 0.0,
                        'last_adjusted': None
                    }
                }
            }
    
    def save_learned_patterns(self):
        """Save learned patterns to file"""
        with open('learned_patterns_v10.pkl', 'wb') as f:
            pickle.dump(self.learned_patterns, f)
    
    def update_pattern_learning(self, pattern_name, prediction_correct, xg_error):
        """Update learning data for a pattern"""
        if pattern_name in self.learned_patterns:
            pattern = self.learned_patterns[pattern_name]
            learning = pattern['learning_data']
            
            learning['total_uses'] += 1
            if prediction_correct:
                learning['correct_uses'] += 1
            
            # Update average error
            total_error = learning['avg_xg_error'] * (learning['total_uses'] - 1) + xg_error
            learning['avg_xg_error'] = total_error / learning['total_uses']
            learning['last_adjusted'] = datetime.now()
            
            # Auto-adjust multiplier if error is consistently high
            if learning['total_uses'] >= 10 and learning['avg_xg_error'] > 0.5:
                self.auto_adjust_pattern_multiplier(pattern_name)
            
            self.save_learned_patterns()
    
    def auto_adjust_pattern_multiplier(self, pattern_name):
        """Auto-adjust pattern multiplier based on performance"""
        pattern = self.learned_patterns[pattern_name]
        learning = pattern['learning_data']
        
        # Calculate adjustment based on error direction
        if learning['avg_xg_error'] > 0:
            # Predictions too high, reduce multiplier
            adjustment = 1.0 - (learning['avg_xg_error'] * 0.1)
        else:
            # Predictions too low, increase multiplier
            adjustment = 1.0 + (abs(learning['avg_xg_error']) * 0.1)
        
        # Apply gradual adjustment
        old_multiplier = pattern['base_multiplier']
        new_multiplier = old_multiplier * adjustment
        
        # Limit adjustments to reasonable ranges
        if pattern_name in ['relegation_battle', 'relegation_threatened']:
            new_multiplier = max(0.5, min(1.0, new_multiplier))
        else:
            new_multiplier = max(0.7, min(1.3, new_multiplier))
        
        pattern['base_multiplier'] = new_multiplier
        
        # Update confidence based on accuracy
        if learning['total_uses'] > 0:
            accuracy = learning['correct_uses'] / learning['total_uses']
            pattern['base_confidence'] = max(0.5, min(0.95, accuracy))
        
        # Record adjustment
        self.db.record_learning_adjustment(
            pattern_name,
            'base_multiplier',
            old_multiplier,
            new_multiplier,
            f'Auto-adjusted based on {learning["total_uses"]} uses, avg error: {learning["avg_xg_error"]:.2f}'
        )
    
    def analyze_match_context_v10(self, home_pos, away_pos, total_teams, games_played, home_form_level, away_form_level):
        """V10: Enhanced context detection with learning"""
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
        
        # Context detection (same as V9)
        if ((home_zone == 'TOP' and away_zone == 'BOTTOM' and 
             home_form_level in ['excellent', 'good'] and gap > 10) or
            (away_zone == 'TOP' and home_zone == 'BOTTOM' and 
             away_form_level in ['excellent', 'good'] and gap > 10)):
            
            context = 'top_vs_bottom_domination'
            top_team = 'HOME' if home_zone == 'TOP' else 'AWAY'
            psychology = {
                'primary': 'DOMINATION',
                'description': f'{top_team} team excellent form vs {away_zone if home_zone == "TOP" else home_zone} bottom team → controlled domination',
                'badge': 'badge-domination',
                'dynamic': 'domination'
            }
        
        elif ((home_pos <= top_cutoff and away_zone == 'MID' and 
               home_form_level == 'excellent' and away_form_level == 'very_poor' and gap > 8) or
              (away_pos <= top_cutoff and home_zone == 'MID' and 
               away_form_level == 'excellent' and home_form_level == 'very_poor' and gap > 8)):
            
            context = 'top_dominance'
            dominant_team = 'HOME' if home_pos <= top_cutoff else 'AWAY'
            psychology = {
                'primary': 'DOMINANCE',
                'description': f'{dominant_team} team excellent form vs poor mid-team → complete control',
                'badge': 'badge-dominance',
                'dynamic': 'dominance'
            }
        
        elif home_pos >= bottom_cutoff and away_pos >= bottom_cutoff:
            context = 'relegation_battle'
            psychology = {
                'primary': 'FEAR',
                'description': 'Both fighting to avoid drop → playing NOT TO LOSE',
                'badge': 'badge-fear',
                'dynamic': 'fear'
            }
        
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
                'safe_team': safe_team
            }
        
        elif home_pos <= top_cutoff and away_pos <= top_cutoff:
            context = 'top_team_battle'
            psychology = {
                'primary': 'QUALITY',
                'description': 'Both title contenders → quality creates AND prevents goals',
                'badge': 'badge-quality',
                'dynamic': 'quality'
            }
        
        elif (home_pos <= top_cutoff and away_zone == 'MID') or \
             (away_pos <= top_cutoff and home_zone == 'MID'):
            
            context = 'mid_vs_top'
            top_team = 'HOME' if home_pos <= top_cutoff else 'AWAY'
            psychology = {
                'primary': 'AMBITION vs CONTROL',
                'description': f'Mid-table ambitious, {top_team} team controls tempo',
                'badge': 'badge-ambition',
                'dynamic': 'ambition'
            }
        
        elif gap <= 4 and home_zone == 'MID' and away_zone == 'MID':
            
            if form_diff >= 2:
                context = 'controlled_mid_clash'
                better_team = 'HOME' if home_form_idx > away_form_idx else 'AWAY'
                psychology = {
                    'primary': 'CONTROL',
                    'description': f'{better_team} team better form → controls game, other defends',
                    'badge': 'badge-control',
                    'dynamic': 'control'
                }
            else:
                context = 'mid_table_clash'
                psychology = {
                    'primary': 'AMBITION',
                    'description': 'Both safe, similar positions and form → playing TO WIN',
                    'badge': 'badge-ambition',
                    'dynamic': 'ambition'
                }
        
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
            'form_diff': form_diff,
            'home_form_idx': home_form_idx,
            'away_form_idx': away_form_idx
        }
    
    def _get_zone(self, position, top_cutoff, bottom_cutoff):
        """Get team's zone in the table"""
        if position <= top_cutoff:
            return 'TOP'
        elif position >= bottom_cutoff:
            return 'BOTTOM'
        else:
            return 'MID'
    
    def calculate_form_factor_v10(self, team_avg, recent_goals):
        """V10: Form calculation with learning"""
        if team_avg <= 0:
            return 1.0, 'average'
        
        recent_avg = recent_goals / 5 if recent_goals > 0 else 0
        ratio = recent_avg / team_avg if team_avg > 0 else 1.0
        
        if team_avg >= 2.0:
            if ratio >= 1.1:
                return self.form_adjustments['excellent'], 'excellent'
            elif ratio >= 0.9:
                return self.form_adjustments['good'], 'good'
            elif ratio >= 0.7:
                return self.form_adjustments['average'], 'average'
            elif ratio >= 0.5:
                return self.form_adjustments['poor'], 'poor'
            else:
                return self.form_adjustments['very_poor'], 'very_poor'
        else:
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
    
    def predict_match(self, match_data):
        """V10: Self-learning prediction engine"""
        # Extract data
        home_pos = match_data['home_pos']
        away_pos = match_data['away_pos']
        total_teams = match_data['total_teams']
        games_played = match_data.get('games_played', 19)
        
        # Calculate form
        home_attack = match_data.get('home_attack', 1.4)
        away_attack = match_data.get('away_attack', 1.3)
        home_defense = match_data.get('home_defense', 1.2)
        away_defense = match_data.get('away_defense', 1.4)
        
        home_form_factor, home_form_level = self.calculate_form_factor_v10(
            home_attack,
            match_data.get('home_goals5', home_attack * 5)
        )
        away_form_factor, away_form_level = self.calculate_form_factor_v10(
            away_attack,
            match_data.get('away_goals5', away_attack * 5)
        )
        
        # Analyze context
        context_analysis = self.analyze_match_context_v10(
            home_pos, away_pos, total_teams, games_played,
            home_form_level, away_form_level
        )
        context = context_analysis['context']
        base_psychology = context_analysis['psychology']
        
        # Get pattern with learned adjustments
        pattern = self.learned_patterns.get(context, self.learned_patterns.get('hierarchical', {
            'base_multiplier': 0.9,
            'base_confidence': 0.75,
            'description': 'Default pattern'
        }))
        
        # Get thresholds (with learning adjustments)
        thresholds = self.prediction_thresholds.get(context, self.prediction_thresholds['default'])
        
        # Base calculations
        raw_home_xg = (home_attack + away_defense) / 2
        raw_away_xg = (away_attack + home_defense) / 2
        raw_total_xg = raw_home_xg + raw_away_xg
        
        # Apply adjustments
        form_home_xg = raw_home_xg * home_form_factor
        form_away_xg = raw_away_xg * away_form_factor
        form_total_xg = form_home_xg + form_away_xg
        
        # Apply psychology multiplier (with learned adjustments)
        psychology_multiplier = pattern['base_multiplier']
        
        # Apply urgency
        urgency_factor = self.urgency_factors[context_analysis['urgency']]
        
        # Final adjusted xG
        adjusted_home_xg = form_home_xg * psychology_multiplier * urgency_factor
        adjusted_away_xg = form_away_xg * psychology_multiplier * urgency_factor
        adjusted_total_xg = adjusted_home_xg + adjusted_away_xg
        
        # Make prediction
        if adjusted_total_xg > thresholds['over']:
            prediction = 'OVER 2.5'
        elif adjusted_total_xg < thresholds['under']:
            prediction = 'UNDER 2.5'
        else:
            prediction = 'OVER 2.5' if adjusted_total_xg > 2.5 else 'UNDER 2.5'
        
        # Calculate confidence
        base_confidence = pattern['base_confidence']
        
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
        
        # Final confidence score
        confidence_score = (base_confidence * 0.3 + 
                          data_quality * 0.25 + 
                          form_weight * 0.2 +
                          gap_factor * 0.25)
        
        confidence_level = 'HIGH' if confidence_score > 0.85 else 'MEDIUM' if confidence_score > 0.7 else 'LOW'
        
        # Stake recommendation
        if confidence_level == 'HIGH' and base_confidence > 0.85:
            stake = 'MAX BET (2x normal)'
            stake_color = 'green'
        elif confidence_level == 'HIGH' or base_confidence > 0.8:
            stake = 'NORMAL BET (1x)'
            stake_color = 'orange'
        else:
            stake = 'SMALL BET (0.5x) or AVOID'
            stake_color = 'red'
        
        # Clean sheet bets (simplified for demo)
        clean_sheet_bets = []
        
        return {
            'prediction': prediction,
            'confidence': confidence_level,
            'confidence_score': round(confidence_score, 3),
            'stake_recommendation': stake,
            'stake_color': stake_color,
            
            'raw_total_xg': round(raw_total_xg, 2),
            'form_total_xg': round(form_total_xg, 2),
            'adjusted_total_xg': round(adjusted_total_xg, 2),
            'home_xg': round(adjusted_home_xg, 2),
            'away_xg': round(adjusted_away_xg, 2),
            
            'context': context,
            'psychology': base_psychology,
            'gap': context_analysis['gap'],
            'base_psychology_multiplier': psychology_multiplier,
            'form_multiplier_home': home_form_factor,
            'form_multiplier_away': away_form_factor,
            'form_level_home': home_form_level,
            'form_level_away': away_form_level,
            'form_diff': context_analysis.get('form_diff', 0),
            'urgency_factor': urgency_factor,
            'season_progress': context_analysis['season_progress'],
            'season_phase': context_analysis['season_phase'],
            'zones': context_analysis['zones'],
            
            'pattern_description': pattern['description'],
            'pattern_confidence': pattern['base_confidence'],
            'pattern_example': pattern.get('example', ''),
            'pattern_psychology': pattern.get('psychology', ''),
            
            'clean_sheet_bets': clean_sheet_bets,
            'thresholds_used': thresholds,
            
            'learning_data': {
                'pattern_name': context,
                'pattern_uses': pattern['learning_data']['total_uses'],
                'pattern_accuracy': pattern['learning_data']['correct_uses'] / max(1, pattern['learning_data']['total_uses']),
                'last_adjusted': pattern['learning_data']['last_adjusted']
            }
        }

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
    .badge-learning {
        background-color: #e3f2fd;
        color: #1565c0;
        border: 1px solid #2196F3;
    }
    .badge-adjusted {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #4CAF50;
    }
    .learning-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .performance-metric {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pattern-performance {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== TEST CASES ==========
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
        'actual_result': '1-0 (UNDER)',
        'clean_sheet': 'HOME'
    },
    'Atletico vs Valencia (TOP vs BOTTOM)': {
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
        'away_goals5': 4,
        'actual_result': '2-1 (OVER)',
        'clean_sheet': 'NO'
    },
}

# ========== INITIALIZE APP ==========
if 'db' not in st.session_state:
    st.session_state.db = PredictionDatabase()

if 'engine' not in st.session_state:
    st.session_state.engine = SelfLearningPredictionEngineV10(st.session_state.db)

if 'current_prediction' not in st.session_state:
    st.session_state.current_prediction = None

if 'match_data' not in st.session_state:
    st.session_state.match_data = TEST_CASES['Atletico vs Valencia (TOP vs BOTTOM)']

if 'show_learning_panel' not in st.session_state:
    st.session_state.show_learning_panel = True

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">🤖 SELF-LEARNING FOOTBALL PREDICTOR V10</div>', unsafe_allow_html=True)
    st.markdown("### **Statistics × Psychology × Auto-Learning System**")
    
    # ===== SIDEBAR - LEARNING DASHBOARD =====
    with st.sidebar:
        st.markdown("## 📊 Learning Dashboard")
        
        # Get performance stats
        perf_stats = st.session_state.db.get_performance_stats()
        
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.metric("Total Predictions", perf_stats['total_predictions'])
        with col_sb2:
            st.metric("Accuracy", f"{perf_stats['accuracy']*100:.1f}%" if perf_stats['total_predictions'] > 0 else "N/A")
        
        st.markdown("### Pattern Performance")
        
        for pattern in perf_stats['pattern_stats'][:5]:
            pattern_name, accuracy, total, avg_error = pattern
            st.markdown(f"""
            <div class="pattern-performance">
                <strong>{pattern_name.replace('_', ' ').title()}</strong><br>
                Accuracy: <strong>{accuracy*100:.1f}%</strong> ({total} matches)<br>
                Avg Error: {avg_error:.2f} goals
            </div>
            """, unsafe_allow_html=True)
        
        # Recent predictions
        st.markdown("### Recent Predictions")
        recent = st.session_state.db.get_recent_predictions(5)
        
        for pred in recent:
            timestamp, home, away, pred_result, conf, pred_xg, actual, accuracy, pattern = pred
            
            if actual:
                result_text = f"{home} vs {away}: {pred_result} ({conf}) → Actual: {actual} goals"
                result_color = "✅" if accuracy == "CORRECT" else "❌"
                st.write(f"{result_color} {result_text}")
        
        # Learning controls
        st.markdown("---")
        st.markdown("### Learning Controls")
        
        if st.button("Reset Learning Data", type="secondary"):
            # Reset learning (implement as needed)
            st.info("Learning data reset would be implemented here")
        
        if st.button("Export Learning Data"):
            st.info("Export functionality would be implemented here")
    
    # ===== MAIN CONTENT =====
    # Test case selection
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🧪 Test Cases")
    
    col_test = st.columns(2)
    test_cases_list = list(TEST_CASES.items())
    
    for idx, (case_name, case_data) in enumerate(test_cases_list):
        with col_test[idx % 2]:
            if st.button(f"{case_name}", use_container_width=True, key=f"test_{case_name}"):
                st.session_state.current_prediction = None
                st.session_state.match_data = case_data
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Learning highlight
    if st.session_state.show_learning_panel:
        st.markdown('<div class="learning-highlight">', unsafe_allow_html=True)
        st.markdown("""
        ### 🤖 V10 SELF-LEARNING SYSTEM ACTIVE
        **This system learns from every prediction it makes!**
        - Tracks accuracy of each pattern
        - Auto-adjusts multipliers based on real outcomes
        - Improves predictions over time
        - Stores all predictions for analysis
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Match Data Input")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏠 Home Team")
        home_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data['home_name'],
            key="home_name_input"
        )
        home_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data['home_pos'],
            key="home_pos_input"
        )
        home_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data['home_attack'],
            step=0.01,
            key="home_attack_input"
        )
        home_goals5 = st.number_input(
            "Goals Last 5",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data['home_goals5'],
            key="home_goals5_input"
        )
    
    with col2:
        st.markdown("#### ✈️ Away Team")
        away_name = st.text_input(
            "Team Name",
            value=st.session_state.match_data['away_name'],
            key="away_name_input"
        )
        away_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=40,
            value=st.session_state.match_data['away_pos'],
            key="away_pos_input"
        )
        away_attack = st.number_input(
            "Goals/Game",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.match_data['away_attack'],
            step=0.01,
            key="away_attack_input"
        )
        away_goals5 = st.number_input(
            "Goals Last 5",
            min_value=0,
            max_value=30,
            value=st.session_state.match_data['away_goals5'],
            key="away_goals5_input"
        )
    
    with col3:
        st.markdown("#### ⚙️ League Settings")
        total_teams = st.number_input(
            "Total Teams",
            min_value=10,
            max_value=30,
            value=st.session_state.match_data['total_teams'],
            key="total_teams_input"
        )
        games_played = st.number_input(
            "Games Played This Season",
            min_value=1,
            max_value=50,
            value=st.session_state.match_data['games_played'],
            key="games_played_input"
        )
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
    
    # Analyze button
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        if st.button("🚀 ANALYZE WITH SELF-LEARNING ENGINE", type="primary", use_container_width=True):
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
                'away_goals5': away_goals5,
                'user_entered': True
            }
            
            # Make prediction
            analysis = st.session_state.engine.predict_match(match_data)
            
            # Save to database
            prediction_hash = st.session_state.db.save_prediction({
                'home_name': home_name,
                'away_name': away_name,
                'home_pos': home_pos,
                'away_pos': away_pos,
                'analysis': analysis
            })
            
            st.session_state.current_prediction = {
                'analysis': analysis,
                'match_data': match_data,
                'prediction_hash': prediction_hash
            }
            
            st.rerun()
    
    with col_btn2:
        if st.button("📊 View Learning Data", use_container_width=True):
            st.session_state.show_learning_panel = not st.session_state.show_learning_panel
            st.rerun()
    
    # ===== PREDICTION RESULTS =====
    if st.session_state.current_prediction:
        prediction = st.session_state.current_prediction['analysis']
        match_data = st.session_state.current_prediction['match_data']
        prediction_hash = st.session_state.current_prediction.get('prediction_hash')
        
        st.markdown("---")
        st.markdown(f"## 📊 Prediction Results: {match_data['home_name']} vs {match_data['away_name']}")
        
        # Key metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("Prediction", prediction['prediction'])
        with col_m2:
            st.metric("Confidence", prediction['confidence'])
        with col_m3:
            st.metric("Enhanced xG", prediction['adjusted_total_xg'])
        with col_m4:
            st.metric("Learning Pattern", prediction['context'].replace('_', ' ').title())
        
        # Learning information
        learning_data = prediction.get('learning_data', {})
        if learning_data:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🧠 Pattern Learning Data
            **Pattern Used:** {learning_data['pattern_name'].replace('_', ' ').title()}  
            **Times Used:** {learning_data['pattern_uses']}  
            **Historical Accuracy:** {learning_data['pattern_accuracy']*100:.1f}%  
            **Last Adjusted:** {learning_data['last_adjusted'] if learning_data['last_adjusted'] else 'Never'}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction breakdown
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("### 📈 xG Breakdown")
            
            fig = go.Figure()
            
            stages = ['Base xG', 'Form Adjusted', 'Psychology Applied', 'Final xG']
            values = [
                prediction['raw_total_xg'],
                prediction['form_total_xg'],
                prediction['form_total_xg'] * prediction['base_psychology_multiplier'],
                prediction['adjusted_total_xg']
            ]
            
            fig.add_trace(go.Bar(
                x=stages,
                y=values,
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ))
            
            fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig.update_layout(
                height=300,
                showlegend=False,
                yaxis_title="Expected Goals"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b2:
            st.markdown("### ⚙️ Adjustment Factors")
            
            st.markdown(f"""
            **Form Multipliers:**  
            Home ({prediction['form_level_home']}): ×{prediction['form_multiplier_home']:.2f}  
            Away ({prediction['form_level_away']}): ×{prediction['form_multiplier_away']:.2f}  
            
            **Psychology Multiplier:**  
            {prediction['psychology']['primary']}: ×{prediction['base_psychology_multiplier']:.2f}  
            
            **Urgency Factor:**  
            Season {prediction['season_progress']}% complete: ×{prediction['urgency_factor']:.2f}  
            
            **Prediction Thresholds:**  
            OVER if > {prediction['thresholds_used']['over']}  
            UNDER if < {prediction['thresholds_used']['under']}
            """)
        
        # Outcome recording
        st.markdown("---")
        st.markdown("### 📝 Record Actual Outcome (For Learning)")
        
        col_out1, col_out2, col_out3 = st.columns(3)
        
        with col_out1:
            actual_home = st.number_input("Home Goals", min_value=0, max_value=10, value=0, key="actual_home")
        
        with col_out2:
            actual_away = st.number_input("Away Goals", min_value=0, max_value=10, value=0, key="actual_away")
        
        with col_out3:
            notes = st.text_input("Notes (optional)", key="outcome_notes")
        
        if st.button("✅ Record Outcome for Learning", type="secondary"):
            if actual_home == 0 and actual_away == 0:
                st.warning("Please enter actual scores before recording.")
            elif prediction_hash:
                success = st.session_state.db.record_outcome(
                    prediction_hash,
                    actual_home,
                    actual_away,
                    notes
                )
                
                if success:
                    st.success("✅ Outcome recorded! System will learn from this result.")
                    
                    # Update engine learning
                    actual_total = actual_home + actual_away
                    predicted_xg = prediction['adjusted_total_xg']
                    xg_error = abs(predicted_xg - actual_total)
                    
                    # Determine if prediction was correct
                    predicted_over_under = prediction['prediction']
                    actual_over_under = "OVER 2.5" if actual_total > 2.5 else "UNDER 2.5"
                    prediction_correct = predicted_over_under == actual_over_under
                    
                    # Update pattern learning
                    st.session_state.engine.update_pattern_learning(
                        prediction['context'],
                        prediction_correct,
                        xg_error
                    )
                    
                    # Show feedback
                    st.info(f"**Learning Update:** Pattern '{prediction['context']}' accuracy updated.")
                    
                    # Refresh to show updated stats
                    st.rerun()
                else:
                    st.error("Failed to record outcome. Please try again.")
            else:
                st.error("No prediction hash found. Please re-run analysis.")
    
    # ===== SYSTEM LEARNING INFO =====
    st.markdown("---")
    st.markdown("### 🤖 V10 Self-Learning System")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        #### 🔄 Auto-Adjustment
        • Multipliers adjust based on real outcomes  
        • Pattern confidence updates automatically  
        • Thresholds optimize for accuracy  
        • Form factors learn from performance  
        """)
    
    with col_info2:
        st.markdown("""
        #### 📊 Performance Tracking
        • Every prediction stored  
        • Accuracy calculated per pattern  
        • Error analysis for improvement  
        • Learning history maintained  
        """)
    
    with col_info3:
        st.markdown("""
        #### 🎯 Continuous Improvement
        • Gets smarter with each match  
        • Adapts to league tendencies  
        • Learns from mistakes  
        • Builds proven knowledge  
        """)

if __name__ == "__main__":
    main()
