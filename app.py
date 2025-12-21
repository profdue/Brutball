import streamlit as st
import pandas as pd
import numpy as np
import warnings
from typing import Dict, Tuple, List
warnings.filterwarnings('ignore')

# =================== PAGE CONFIG ===================
st.set_page_config(
    page_title="Brutball Professional Decision Framework v3.0",
    page_icon="⚽",
    layout="wide"
)

# =================== CUSTOM CSS ===================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .layer-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #F8FAFC;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .crisis-alert {
        background-color: #FEF2F2;
        border-left: 5px solid #DC2626;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .opportunity-alert {
        background-color: #F0FDF4;
        border-left: 5px solid #16A34A;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .defensive-alert {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .archetype-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .threshold-slider {
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# =================== DATA LOADING ===================
@st.cache_data
def load_league_data():
    """Load and prepare the league data with all CSV headings"""
    try:
        # Try loading from different possible paths
        paths_to_try = [
            'leagues/premier_league.csv',
            './leagues/premier_league.csv',
            'premier_league.csv',
            'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
        ]
        
        df = None
        loaded_path = ""
        for path in paths_to_try:
            try:
                df = pd.read_csv(path)
                loaded_path = path
                break
            except Exception as e:
                continue
        
        if df is None:
            st.error("❌ Could not load data from any source")
            return None, None
        
        st.success(f"✅ Data loaded successfully from: {loaded_path}")
        
        # Clean column names
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower()
        cleaned_columns = df.columns.tolist()
        
        # Add derived columns using ALL available data
        if 'home_matches_played' in df.columns and 'home_goals_scored' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
            df['home_xgc_per_match'] = df['home_xg_against'] / df['home_matches_played'].replace(0, 1)
            df['away_xgc_per_match'] = df['away_xg_against'] / df['away_matches_played'].replace(0, 1)
        
        # Calculate form points
        def form_to_points(form_str):
            if pd.isna(form_str):
                return 7.5
            points = {'W': 3, 'D': 1, 'L': 0}
            return sum(points.get(char, 0) for char in str(form_str))
        
        for form_col in ['form_last_5_overall', 'form_last_5_home', 'form_last_5_away']:
            if form_col in df.columns:
                df[f'{form_col}_points'] = df[form_col].apply(form_to_points)
        
        return df, original_columns
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None, None

# =================== QUANTITATIVE ENGINE ===================
class BrutballQuantitativeEngine:
    """Professional Quantitative Decision Engine - Complete Implementation"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.league_avg_xg = self._calculate_league_averages()
        self.performance_log = []
        
        # Configuration - can be adjusted via UI
        self.config = {
            'crisis_critical_threshold': 6,
            'crisis_warning_threshold': 3,
            'xg_deviation_threshold': 0.3,
            'counter_threat_threshold': 0.12,  # 12%
            'setpiece_threat_threshold': 0.20,  # 20%
            'attack_suppression_threshold': 1.1,
            'defensive_grind_confidence_min': 5.0,
            'fade_score_threshold': 15,
            'goals_score_threshold': 12,
            'back_score_threshold': 10
        }
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        self.config.update(kwargs)
    
    def _calculate_league_averages(self) -> Dict:
        """Calculate league-wide averages for context"""
        metrics = {}
        
        # xG averages
        if 'home_xg_for' in self.df.columns and 'home_matches_played' in self.df.columns:
            total_home_xg = self.df['home_xg_for'].sum()
            total_home_matches = self.df['home_matches_played'].sum()
            metrics['home_xg'] = total_home_xg / total_home_matches if total_home_matches > 0 else 1.5
        
        if 'away_xg_for' in self.df.columns and 'away_matches_played' in self.df.columns:
            total_away_xg = self.df['away_xg_for'].sum()
            total_away_matches = self.df['away_matches_played'].sum()
            metrics['away_xg'] = total_away_xg / total_away_matches if total_away_matches > 0 else 1.2
        
        # Goal type averages
        goal_type_columns = [
            'home_goals_openplay_for', 'home_goals_counter_for', 'home_goals_setpiece_for',
            'away_goals_openplay_for', 'away_goals_counter_for', 'away_goals_setpiece_for'
        ]
        
        for col in goal_type_columns:
            if col in self.df.columns:
                metrics[f'avg_{col}'] = self.df[col].mean() if len(self.df) > 0 else 0
        
        return metrics
    
    # ========== PHASE 1: QUANTITATIVE CRISIS SCORING ==========
    def calculate_crisis_score(self, team_data: Dict) -> Dict:
        """Quantitative crisis scoring using all available data"""
        score = 0
        signals = []
        detailed_metrics = {}
        
        # 1. Defenders Out (0-5 points)
        defenders_out = team_data.get('defenders_out', 0)
        if defenders_out >= 4:
            score += 5
            signals.append(f"🚨 {defenders_out} defenders out (5pts)")
        elif defenders_out == 3:
            score += 3
            signals.append(f"⚠️ {defenders_out} defenders out (3pts)")
        elif defenders_out == 2:
            score += 1
            signals.append(f"{defenders_out} defenders out (1pt)")
        detailed_metrics['defenders_out'] = defenders_out
        
        # 2. Goals Conceded Last 5 (0-5 points)
        goals_conceded = team_data.get('goals_conceded_last_5', 0)
        if goals_conceded >= 15:
            score += 5
            signals.append(f"📉 {goals_conceded} conceded last 5 (5pts)")
        elif goals_conceded >= 12:
            score += 3
            signals.append(f"📉 {goals_conceded} conceded last 5 (3pts)")
        elif goals_conceded >= 10:
            score += 1
            signals.append(f"{goals_conceded} conceded last 5 (1pt)")
        detailed_metrics['goals_conceded_last_5'] = goals_conceded
        
        # 3. Form Momentum (0-5 points)
        form = str(team_data.get('form_last_5_overall', ''))
        if len(form) >= 2:
            if form[-2:] == 'LL':
                score += 3
                signals.append("📉 Recent LL streak (3pts)")
            elif form[-1] == 'L':
                score += 1
                signals.append("Recent loss (1pt)")
            
            if 'LLL' in form:
                score += 2
                signals.append("📉 LLL in form (2pts)")
        
        # 4. Additional defensive metrics from xG
        if 'home_xg_against' in team_data and 'home_matches_played' in team_data:
            home_xgc = team_data.get('home_xg_against', 0)
            home_games = team_data.get('home_matches_played', 1)
            home_xgc_per_game = home_xgc / home_games
            
            if home_xgc_per_game > 1.8:
                score += 2
                signals.append(f"📊 High home xG conceded: {home_xgc_per_game:.2f}/game")
        
        if 'away_xg_against' in team_data and 'away_matches_played' in team_data:
            away_xgc = team_data.get('away_xg_against', 0)
            away_games = team_data.get('away_matches_played', 1)
            away_xgc_per_game = away_xgc / away_games
            
            if away_xgc_per_game > 1.8:
                score += 2
                signals.append(f"📊 High away xG conceded: {away_xgc_per_game:.2f}/game")
        
        # Severity Classification
        if score >= self.config['crisis_critical_threshold']:
            severity = 'CRITICAL'
        elif score >= self.config['crisis_warning_threshold']:
            severity = 'WARNING'
        else:
            severity = 'STABLE'
        
        return {
            'score': score,
            'severity': severity,
            'signals': signals,
            'detailed_metrics': detailed_metrics
        }
    
    # ========== PHASE 2: DYNAMIC REALITY CHECK ==========
    def analyze_xg_deviation(self, team_data: Dict, is_home: bool) -> Tuple[str, float]:
        """Comprehensive xG analysis using all available metrics"""
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
            games = team_data.get('home_matches_played', 1)
            league_avg = self.league_avg_xg.get('home_xg', 1.5)
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
            games = team_data.get('away_matches_played', 1)
            league_avg = self.league_avg_xg.get('away_xg', 1.2)
        
        goals_per_game = goals / max(games, 1)
        xg_per_game = xg / max(games, 1)
        
        # Dynamic threshold based on team strength
        base_threshold = self.config['xg_deviation_threshold']
        if xg_per_game > league_avg * 1.2:  # Top attacking team
            threshold = base_threshold * 0.8
        elif xg_per_game < league_avg * 0.8:  # Weak attacking team
            threshold = base_threshold * 1.2
        else:
            threshold = base_threshold
        
        deviation = goals_per_game - xg_per_game
        
        if deviation > threshold:
            confidence = min(2.0, 1.0 + (deviation - threshold) / threshold)
            return 'OVERPERFORMING', confidence, deviation
        elif deviation < -threshold:
            confidence = min(2.0, 1.0 + abs(deviation - threshold) / threshold)
            return 'UNDERPERFORMING', confidence, deviation
        else:
            return 'NEUTRAL', 1.0, deviation
    
    # ========== PHASE 3: COMPREHENSIVE TACTICAL ANALYSIS ==========
    def calculate_tactical_edge(self, home_team: Dict, away_team: Dict) -> Dict:
        """Complete tactical analysis using all goal type data"""
        edge_score = 0
        edges = []
        detailed_analysis = {}
        
        # Get all goal type percentages for home team
        home_total_goals = max(1, home_team.get('home_goals_scored', 1))
        away_total_goals = max(1, away_team.get('away_goals_scored', 1))
        
        # 1. Counter-Attack Analysis
        home_counter_for = home_team.get('home_goals_counter_for', 0)
        away_counter_against = away_team.get('away_goals_counter_against', 0)
        away_total_conceded = max(1, away_team.get('away_goals_conceded', 1))
        
        home_counter_pct = home_counter_for / home_total_goals
        away_counter_vuln = away_counter_against / away_total_conceded
        
        if home_counter_pct > 0.10 and away_counter_vuln > 0.10:
            counter_edge = (home_counter_pct * away_counter_vuln) * 25
            edge_score += min(4.0, counter_edge)
            edges.append({
                'type': 'COUNTER_ATTACK',
                'score': min(4.0, counter_edge),
                'home_pct': home_counter_pct,
                'away_vuln': away_counter_vuln,
                'detail': f"Home scores {home_counter_pct:.1%} from counters, Away concedes {away_counter_vuln:.1%}"
            })
        
        # 2. Set-Piece Analysis
        home_setpiece_for = home_team.get('home_goals_setpiece_for', 0)
        away_setpiece_against = away_team.get('away_goals_setpiece_against', 0)
        
        home_setpiece_pct = home_setpiece_for / home_total_goals
        away_setpiece_vuln = away_setpiece_against / away_total_conceded
        
        if home_setpiece_pct > 0.15 and away_setpiece_vuln > 0.15:
            setpiece_edge = (home_setpiece_pct * away_setpiece_vuln) * 30
            edge_score += min(4.0, setpiece_edge)
            edges.append({
                'type': 'SET_PIECE',
                'score': min(4.0, setpiece_edge),
                'home_pct': home_setpiece_pct,
                'away_vuln': away_setpiece_vuln,
                'detail': f"Home scores {home_setpiece_pct:.1%} from set pieces, Away concedes {away_setpiece_vuln:.1%}"
            })
        
        # 3. Open Play Analysis
        home_openplay_for = home_team.get('home_goals_openplay_for', 0)
        away_openplay_against = away_team.get('away_goals_openplay_against', 0)
        
        home_openplay_pct = home_openplay_for / home_total_goals
        away_openplay_vuln = away_openplay_against / away_total_conceded
        
        if home_openplay_pct > 0.60:
            openplay_edge = home_openplay_pct * 2
            edge_score += min(3.0, openplay_edge)
            edges.append({
                'type': 'OPEN_PLAY',
                'score': min(3.0, openplay_edge),
                'home_pct': home_openplay_pct,
                'detail': f"Home heavily reliant on open play: {home_openplay_pct:.1%}"
            })
        
        # 4. Attack Competence Check
        home_attack_xg = home_team.get('home_xg_for', 0) / max(1, home_team.get('home_matches_played', 1))
        away_attack_xg = away_team.get('away_xg_for', 0) / max(1, away_team.get('away_matches_played', 1))
        
        competence_score = 0
        if home_attack_xg > 1.0:
            competence_score += 1
        if away_attack_xg > 1.0:
            competence_score += 1
        
        edge_score += competence_score
        both_competent = (home_attack_xg > 0.7 and away_attack_xg > 0.7)
        
        # 5. Defensive Vulnerability Analysis
        home_goals_conceded = home_team.get('home_goals_conceded', 0) if 'home_goals_conceded' in home_team else 0
        away_goals_conceded = away_team.get('away_goals_conceded', 0) if 'away_goals_conceded' in away_team else 0
        
        detailed_analysis = {
            'home_attack_xg': home_attack_xg,
            'away_attack_xg': away_attack_xg,
            'home_goals_conceded': home_goals_conceded,
            'away_goals_conceded': away_goals_conceded,
            'goal_type_breakdown': {
                'home': {
                    'openplay': home_openplay_pct,
                    'counter': home_counter_pct,
                    'setpiece': home_setpiece_pct,
                    'penalty': home_team.get('home_goals_penalty_for', 0) / home_total_goals if home_total_goals > 0 else 0,
                    'owngoal': home_team.get('home_goals_owngoal_for', 0) / home_total_goals if home_total_goals > 0 else 0
                },
                'away': {
                    'openplay': away_openplay_pct,
                    'counter': away_counter_vuln,
                    'setpiece': away_setpiece_vuln,
                    'penalty': away_team.get('away_goals_penalty_for', 0) / away_total_goals if away_total_goals > 0 else 0,
                    'owngoal': away_team.get('away_goals_owngoal_for', 0) / away_total_goals if away_total_goals > 0 else 0
                }
            }
        }
        
        return {
            'score': min(10.0, edge_score),
            'edges': edges,
            'competence_score': competence_score,
            'both_competent': both_competent,
            'detailed_analysis': detailed_analysis
        }
    
    # ========== PHASE 4A: DEFENSIVE GRIND VALIDATOR ==========
    def validate_defensive_grind(self, home_team: Dict, away_team: Dict, 
                               home_crisis: Dict, away_crisis: Dict) -> Tuple[bool, float, List[str]]:
        """Defensive Grind (Under 2.5) validation"""
        reasons = []
        confidence = 0
        
        # ===== 1. HARD REJECTIONS =====
        if home_crisis['severity'] == 'CRITICAL' or away_crisis['severity'] == 'CRITICAL':
            reasons.append("❌ CRITICAL defensive crisis present")
            return False, 0.0, reasons
        
        # ===== 2. ATTACK SUPPRESSION CHECK =====
        home_xg_per_game = home_team.get('home_xg_for', 0) / max(1, home_team.get('home_matches_played', 1))
        away_xg_per_game = away_team.get('away_xg_for', 0) / max(1, away_team.get('away_matches_played', 1))
        
        if home_xg_per_game > self.config['attack_suppression_threshold'] or away_xg_per_game > self.config['attack_suppression_threshold']:
            reasons.append(f"❌ Attack too strong (Home: {home_xg_per_game:.2f}, Away: {away_xg_per_game:.2f})")
            return False, 0.0, reasons
        else:
            reasons.append(f"✅ Attacks suppressed (Home: {home_xg_per_game:.2f}, Away: {away_xg_per_game:.2f})")
            confidence += 2.0
        
        # ===== 3. STYLE CANCELLATION CHECK =====
        home_total_goals = max(1, home_team.get('home_goals_scored', 1))
        away_total_goals = max(1, away_team.get('away_goals_scored', 1))
        
        # Counter-attack suppression
        home_counter_pct = home_team.get('home_goals_counter_for', 0) / home_total_goals
        away_counter_pct = away_team.get('away_goals_counter_for', 0) / away_total_goals
        
        if home_counter_pct > self.config['counter_threat_threshold'] or away_counter_pct > self.config['counter_threat_threshold']:
            reasons.append(f"❌ Counter-attack threat (Home: {home_counter_pct:.1%}, Away: {away_counter_pct:.1%})")
            return False, 0.0, reasons
        else:
            reasons.append(f"✅ No counter threat (Home: {home_counter_pct:.1%}, Away: {away_counter_pct:.1%})")
            confidence += 1.5
        
        # Set-piece suppression
        home_setpiece_pct = home_team.get('home_goals_setpiece_for', 0) / home_total_goals
        away_setpiece_pct = away_team.get('away_goals_setpiece_for', 0) / away_total_goals
        
        if home_setpiece_pct > self.config['setpiece_threat_threshold'] or away_setpiece_pct > self.config['setpiece_threat_threshold']:
            reasons.append(f"❌ Set-piece threat (Home: {home_setpiece_pct:.1%}, Away: {away_setpiece_pct:.1%})")
            return False, 0.0, reasons
        else:
            reasons.append(f"✅ No set-piece threat (Home: {home_setpiece_pct:.1%}, Away: {away_setpiece_pct:.1%})")
            confidence += 1.5
        
        # ===== 4. GAME-STATE CONTROL CHECK =====
        home_form = str(home_team.get('form_last_5_overall', ''))
        away_form = str(away_team.get('form_last_5_overall', ''))
        
        home_draws = home_form.count('D')
        away_draws = away_form.count('D')
        
        if home_draws >= 2 and away_draws >= 2:
            reasons.append(f"✅ Both teams draw-heavy (Home: {home_draws}/5, Away: {away_draws}/5)")
            confidence += 2.0
        elif home_draws >= 2 or away_draws >= 2:
            reasons.append(f"⚠️ One team draw-prone")
            confidence += 1.0
        else:
            reasons.append("❌ No draw tendency")
            return False, 0.0, reasons
        
        # Recent scoring suppression
        home_goals_last_5 = home_team.get('goals_scored_last_5', 0)
        away_goals_last_5 = away_team.get('goals_scored_last_5', 0)
        
        if home_goals_last_5 <= 5 and away_goals_last_5 <= 5:
            reasons.append(f"✅ Low recent scoring (Home: {home_goals_last_5}, Away: {away_goals_last_5})")
            confidence += 1.0
        
        # ===== 5. FINAL VALIDATION =====
        if confidence >= self.config['defensive_grind_confidence_min']:
            reasons.append(f"✅ DEFENSIVE GRIND VALID (Confidence: {confidence:.1f}/8.0)")
            return True, confidence, reasons
        else:
            reasons.append(f"❌ Insufficient confidence (Score: {confidence:.1f}/8.0)")
            return False, 0.0, reasons
    
    # ========== PHASE 4B: QUANTITATIVE ARCHETYPE ==========
    def determine_archetype(self, home_crisis: Dict, away_crisis: Dict,
                           home_xg: Tuple, away_xg: Tuple,
                           tactical: Dict, home_team: Dict, away_team: Dict) -> Dict:
        """Complete archetype classification with all options"""
        fade_score = 0
        goals_score = 0
        back_score = 0
        defensive_grind_valid = False
        grind_confidence = 0.0
        grind_reasons = []
        rationale = []
        
        # ===== 1. DEFENSIVE GRIND CHECK =====
        defensive_grind_valid, grind_confidence, grind_reasons = self.validate_defensive_grind(
            home_team, away_team, home_crisis, away_crisis
        )
        
        if defensive_grind_valid:
            rationale.append(f"DEFENSIVE GRIND qualified (Score: {grind_confidence:.1f})")
        
        # ===== 2. FADE scoring =====
        if away_crisis['severity'] == 'CRITICAL' and home_crisis['severity'] in ['STABLE', 'WARNING']:
            fade_score = away_crisis['score'] * away_xg[1]
            if away_xg[0] == 'OVERPERFORMING':
                fade_score *= 1.5
            if fade_score > 0:
                rationale.append(f"FADE base: {fade_score:.1f}")
        
        # ===== 3. GOALS GALORE scoring =====
        if home_crisis['severity'] == 'CRITICAL' or away_crisis['severity'] == 'CRITICAL':
            crisis_sum = home_crisis['score'] + away_crisis['score']
            goals_score = crisis_sum * (tactical['score'] / 5)
            if not tactical['both_competent']:
                goals_score *= 0.7
                rationale.append("Goals score penalized: weak attack competence")
            if goals_score > 0:
                rationale.append(f"GOALS base: {goals_score:.1f}")
        
        # ===== 4. BACK scoring =====
        if home_xg[0] == 'UNDERPERFORMING' and home_crisis['severity'] == 'STABLE':
            stability_factor = max(1, 10 - away_crisis['score']) / 10
            back_score = home_xg[1] * stability_factor * 10
            if back_score > 0:
                rationale.append(f"BACK base: {back_score:.1f}")
        
        # ===== 5. DECISION HIERARCHY =====
        # DEFENSIVE GRIND has priority when valid with sufficient confidence
        if defensive_grind_valid and grind_confidence >= 6.0:
            confidence = min(10.0, grind_confidence)
            archetype = 'DEFENSIVE_GRIND'
            rationale.append(f"→ DEFENSIVE GRIND selected (confidence: {confidence:.1f})")
            
        elif fade_score > self.config['fade_score_threshold'] and fade_score > max(goals_score, back_score):
            confidence = min(10.0, fade_score / 3)
            archetype = 'FADE_THE_FAVORITE'
            rationale.append(f"→ FADE selected (score: {fade_score:.1f})")
            
        elif goals_score > self.config['goals_score_threshold'] and goals_score > max(fade_score, back_score):
            confidence = min(10.0, goals_score / 3)
            archetype = 'GOALS_GALORE'
            rationale.append(f"→ GOALS selected (score: {goals_score:.1f})")
            
        elif back_score > self.config['back_score_threshold']:
            confidence = min(8.0, back_score / 3)
            archetype = 'BACK_THE_UNDERDOG'
            rationale.append(f"→ BACK selected (score: {back_score:.1f})")
            
        else:
            archetype = 'AVOID'
            confidence = 0
            rationale.append("→ No quantitative edge above thresholds")
        
        # Add defensive grind reasons if checked
        if defensive_grind_valid:
            rationale.extend([f"Defensive Grind: {reason}" for reason in grind_reasons])
        
        return {
            'archetype': archetype,
            'confidence': round(confidence, 1),
            'scores': {
                'fade': round(fade_score, 1),
                'goals': round(goals_score, 1),
                'back': round(back_score, 1),
                'defensive_grind': round(grind_confidence, 1) if defensive_grind_valid else 0
            },
            'rationale': rationale,
            'defensive_grind_valid': defensive_grind_valid,
            'defensive_grind_reasons': grind_reasons
        }
    
    # ========== PHASE 5: PRECISION STAKING ==========
    def calculate_stake_size(self, archetype: str, confidence: float) -> float:
        """Capital allocation with all archetypes"""
        if archetype == 'AVOID' or confidence < 4:
            return 0.0
        
        base_stakes = {
            'FADE_THE_FAVORITE': {8: 2.5, 6: 2.0, 4: 1.0},
            'GOALS_GALORE': {8: 2.0, 6: 1.5, 4: 0.5},
            'BACK_THE_UNDERDOG': {8: 1.5, 6: 1.0, 4: 0.5},
            'DEFENSIVE_GRIND': {8: 2.0, 6: 1.5, 4: 1.0}
        }
        
        thresholds = base_stakes.get(archetype, {})
        for threshold, stake in sorted(thresholds.items(), reverse=True):
            if confidence >= threshold:
                return stake
        
        return 0.0
    
    # ========== COMPLETE ANALYSIS PIPELINE ==========
    def analyze_match(self, home_team_name: str, away_team_name: str) -> Dict:
        """Complete quantitative analysis pipeline"""
        # Get team data with ALL available fields
        home_data = self.df[self.df['team'] == home_team_name].iloc[0].to_dict()
        away_data = self.df[self.df['team'] == away_team_name].iloc[0].to_dict()
        
        # Phase 1: Crisis Scoring
        home_crisis = self.calculate_crisis_score(home_data)
        away_crisis = self.calculate_crisis_score(away_data)
        
        # Phase 2: xG Reality Check
        home_xg_result = self.analyze_xg_deviation(home_data, is_home=True)
        away_xg_result = self.analyze_xg_deviation(away_data, is_home=False)
        home_xg = (home_xg_result[0], home_xg_result[1])
        away_xg = (away_xg_result[0], away_xg_result[1])
        
        # Phase 3: Tactical Edge
        tactical = self.calculate_tactical_edge(home_data, away_data)
        
        # Phase 4: Archetype Classification
        archetype_result = self.determine_archetype(
            home_crisis, away_crisis, home_xg, away_xg, tactical, home_data, away_data
        )
        
        # Phase 5: Capital Allocation
        stake_pct = self.calculate_stake_size(
            archetype_result['archetype'],
            archetype_result['confidence']
        )
        
        # Log the decision
        self.log_decision({
            'match': f"{home_team_name} vs {away_team_name}",
            'archetype': archetype_result['archetype'],
            'confidence': archetype_result['confidence'],
            'recommended_stake': stake_pct,
            'crisis_analysis': {'home': home_crisis, 'away': away_crisis},
            'reality_check': {
                'home': {'type': home_xg[0], 'confidence': home_xg[1]},
                'away': {'type': away_xg[0], 'confidence': away_xg[1]}
            }
        })
        
        # Compile comprehensive result
        return {
            'match': f"{home_team_name} vs {away_team_name}",
            
            # Phase 1 Results
            'crisis_analysis': {'home': home_crisis, 'away': away_crisis},
            
            # Phase 2 Results
            'reality_check': {
                'home': {'type': home_xg[0], 'confidence': home_xg[1], 'deviation': home_xg_result[2]},
                'away': {'type': away_xg[0], 'confidence': away_xg[1], 'deviation': away_xg_result[2]}
            },
            
            # Phase 3 Results
            'tactical_edge': tactical,
            
            # Phase 4 Results
            'archetype': archetype_result['archetype'],
            'confidence': archetype_result['confidence'],
            'quantitative_scores': archetype_result['scores'],
            'rationale': archetype_result['rationale'],
            'defensive_grind_valid': archetype_result['defensive_grind_valid'],
            'defensive_grind_reasons': archetype_result['defensive_grind_reasons'],
            
            # Phase 5 Results
            'recommended_stake': stake_pct,
            
            # Derived metrics for display
            'home_attack_xg': home_data.get('home_xg_for', 0) / max(1, home_data.get('home_matches_played', 1)),
            'away_attack_xg': away_data.get('away_xg_for', 0) / max(1, away_data.get('away_matches_played', 1)),
            'home_form': home_data.get('form_last_5_overall', ''),
            'away_form': away_data.get('form_last_5_overall', ''),
            
            # Additional metrics from CSV
            'home_season_position': home_data.get('season_position', 'N/A'),
            'away_season_position': away_data.get('season_position', 'N/A'),
            'home_goals_last_5': home_data.get('goals_scored_last_5', 0),
            'away_goals_last_5': away_data.get('goals_scored_last_5', 0)
        }
    
    # ========== PERFORMANCE TRACKING ==========
    def log_decision(self, analysis: Dict):
        """Log decision for performance tracking"""
        log_entry = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'match': analysis['match'],
            'archetype': analysis.get('archetype'),
            'confidence': analysis.get('confidence'),
            'stake_percent': analysis.get('recommended_stake'),
            'home_crisis_score': analysis['crisis_analysis']['home']['score'],
            'away_crisis_score': analysis['crisis_analysis']['away']['score']
        }
        self.performance_log.append(log_entry)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.performance_log:
            return {}
        
        df_log = pd.DataFrame(self.performance_log)
        
        stats = {
            'total_decisions': len(df_log),
            'archetype_distribution': df_log['archetype'].value_counts().to_dict(),
            'avg_confidence': df_log['confidence'].mean() if 'confidence' in df_log.columns else 0,
            'bets_recommended': len(df_log[df_log['stake_percent'] > 0]) if 'stake_percent' in df_log.columns else 0,
            'avoid_count': len(df_log[df_log['archetype'] == 'AVOID']) if 'archetype' in df_log.columns else 0
        }
        
        return stats

# =================== UI FUNCTIONS ===================
def render_header():
    """Render the main header"""
    st.markdown('<div class="main-header">⚽ Brutball Professional Decision Framework v3.0</div>', unsafe_allow_html=True)
    st.markdown("**Complete Quantitative System - All CSV Headings Utilized**")

def render_framework_status():
    """Render the three-layer framework status"""
    st.markdown("### 🏗️ Three-Layer Decision Framework")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 1: Quantitative Analysis**")
        st.markdown("✅ Crisis Scoring + xG Deviation + Tactical Edge")
        st.markdown("**Status:** FULLY OPERATIONAL")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 2: Decision Firewall**")
        st.markdown("✅ Archetype Classification + Validation Gates")
        st.markdown("**Status:** FULLY OPERATIONAL")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 3: Capital Allocation**")
        st.markdown("✅ Precision Staking + Performance Tracking")
        st.markdown("**Status:** FULLY AUTOMATED")
        st.markdown('</div>', unsafe_allow_html=True)

def render_system_configuration(engine):
    """Render system configuration controls"""
    with st.expander("⚙️ System Configuration", expanded=False):
        st.markdown("#### Threshold Calibration")
        
        col1, col2 = st.columns(2)
        with col1:
            crisis_critical = st.slider("Crisis Critical Threshold", 4, 10, engine.config['crisis_critical_threshold'], 
                                       help="Score ≥ this = CRITICAL crisis")
            xg_threshold = st.slider("xG Deviation Threshold", 0.1, 0.5, engine.config['xg_deviation_threshold'], 
                                    help="Minimum xG deviation for OVER/UNDER performance")
            attack_threshold = st.slider("Attack Suppression", 0.8, 1.5, engine.config['attack_suppression_threshold'],
                                        help="Max xG/game for DEFENSIVE GRIND")
        
        with col2:
            crisis_warning = st.slider("Crisis Warning Threshold", 1, 8, engine.config['crisis_warning_threshold'],
                                      help="Score ≥ this = WARNING crisis")
            counter_threshold = st.slider("Counter Threat %", 0.05, 0.25, engine.config['counter_threat_threshold'],
                                         help="Max counter-attack % for DEFENSIVE GRIND")
            setpiece_threshold = st.slider("Set-Piece Threat %", 0.10, 0.35, engine.config['setpiece_threat_threshold'],
                                          help="Max set-piece % for DEFENSIVE GRIND")
        
        if st.button("Apply Configuration", type="primary"):
            engine.update_config(
                crisis_critical_threshold=crisis_critical,
                crisis_warning_threshold=crisis_warning,
                xg_deviation_threshold=xg_threshold,
                attack_suppression_threshold=attack_threshold,
                counter_threat_threshold=counter_threshold,
                setpiece_threat_threshold=setpiece_threshold
            )
            st.success("✅ Configuration updated")

def render_match_analysis(engine, df):
    """Render the match analysis section"""
    st.markdown("### 🏟️ Match Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 Home Team", df['team'].unique())
    with col2:
        away_teams = [t for t in df['team'].unique() if t != home_team]
        away_team = st.selectbox("✈️ Away Team", away_teams)
    
    if home_team and away_team:
        with st.spinner("Running quantitative analysis..."):
            analysis = engine.analyze_match(home_team, away_team)
            display_quantitative_results(analysis)
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Generate Analysis Report", use_container_width=True):
                report = create_report(analysis)
                st.session_state['report'] = report
                st.success("Report generated!")
        
        with col2:
            if 'report' in st.session_state:
                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state['report'],
                    file_name=f"brutball_{home_team}_vs_{away_team}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

def display_quantitative_results(analysis):
    """Display complete quantitative analysis results"""
    st.markdown("---")
    st.markdown("### 🔍 Layer 1: Quantitative Situation Analysis")
    
    # Crisis Analysis
    col1, col2 = st.columns(2)
    with col1:
        home_team = analysis['match'].split(' vs ')[0]
        st.markdown(f"#### {home_team}")
        home_crisis = analysis['crisis_analysis']['home']
        
        st.metric("Crisis Score", f"{home_crisis['score']}")
        st.caption(f"Severity: {home_crisis['severity']}")
        
        if home_crisis['signals']:
            st.markdown('<div class="crisis-alert">', unsafe_allow_html=True)
            for signal in home_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional metrics
        st.markdown(f"**Season Position:** {analysis.get('home_season_position', 'N/A')}")
        st.markdown(f"**Goals Last 5:** {analysis.get('home_goals_last_5', 0)}")
    
    with col2:
        away_team = analysis['match'].split(' vs ')[1]
        st.markdown(f"#### {away_team}")
        away_crisis = analysis['crisis_analysis']['away']
        
        st.metric("Crisis Score", f"{away_crisis['score']}")
        st.caption(f"Severity: {away_crisis['severity']}")
        
        if away_crisis['signals']:
            st.markdown('<div class="crisis-alert">', unsafe_allow_html=True)
            for signal in away_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional metrics
        st.markdown(f"**Season Position:** {analysis.get('away_season_position', 'N/A')}")
        st.markdown(f"**Goals Last 5:** {analysis.get('away_goals_last_5', 0)}")
    
    # Reality Check
    st.markdown("#### 📊 Reality Check (xG Analysis)")
    col1, col2 = st.columns(2)
    with col1:
        home_xg = analysis['reality_check']['home']
        st.markdown(f"**{home_team}:** {home_xg['type']}")
        st.metric("xG Deviation", f"{home_xg['deviation']:.2f}")
        st.metric("Attack xG", f"{analysis['home_attack_xg']:.2f}/game")
        st.caption(f"Confidence: {home_xg['confidence']:.1f}")
    
    with col2:
        away_xg = analysis['reality_check']['away']
        st.markdown(f"**{away_team}:** {away_xg['type']}")
        st.metric("xG Deviation", f"{away_xg['deviation']:.2f}")
        st.metric("Attack xG", f"{analysis['away_attack_xg']:.2f}/game")
        st.caption(f"Confidence: {away_xg['confidence']:.1f}")
    
    # Tactical Edge
    st.markdown("#### ⚽ Tactical Edge Analysis")
    tactical = analysis['tactical_edge']
    st.markdown(f"**Overall Tactical Score:** {tactical['score']:.1f}/10")
    
    if tactical['edges']:
        for edge in tactical['edges']:
            st.markdown(f'<div class="opportunity-alert">', unsafe_allow_html=True)
            st.markdown(f"**{edge['type'].replace('_', ' ')}** - Score: {edge['score']:.1f}/4")
            st.markdown(f"{edge['detail']}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Attack Competence
    if not tactical.get('both_competent', True):
        st.warning(f"⚠️ Attack Competence Warning")
        st.markdown(f"Home xG: {analysis['home_attack_xg']:.2f}, Away xG: {analysis['away_attack_xg']:.2f}")
    
    # Layer 2: Decision Classification
    st.markdown("---")
    st.markdown("### 🎯 Layer 2: Quantitative Decision Classification")
    
    # Archetype with color coding
    archetype_colors = {
        'FADE_THE_FAVORITE': '#DC2626',
        'BACK_THE_UNDERDOG': '#16A34A',
        'GOALS_GALORE': '#EA580C',
        'DEFENSIVE_GRIND': '#2563EB',
        'AVOID': '#6B7280'
    }
    
    color = archetype_colors.get(analysis['archetype'], '#6B7280')
    
    st.markdown(f"""
    <div style="padding: 1.5rem; border-radius: 10px; background-color: {color}10; border-left: 5px solid {color};">
        <h3 style="color: {color}; margin-top: 0;">{analysis['archetype'].replace('_', ' ')}</h3>
        <p><strong>Confidence Score:</strong> {analysis['confidence']}/10</p>
        <p><strong>Quantitative Scores:</strong></p>
        <p>• Fade: {analysis['quantitative_scores']['fade']:.1f}</p>
        <p>• Goals: {analysis['quantitative_scores']['goals']:.1f}</p>
        <p>• Back: {analysis['quantitative_scores']['back']:.1f}</p>
        <p>• Defensive Grind: {analysis['quantitative_scores']['defensive_grind']:.1f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Decision Rationale
    st.markdown("#### 🧠 Decision Rationale")
    for line in analysis['rationale']:
        if '❌' in line or '✅' in line or '⚠️' in line:
            st.markdown(f"- {line}")
        else:
            st.markdown(f"- {line}")
    
    # Defensive Grind specific reasons
    if analysis['defensive_grind_valid']:
        st.markdown("#### 🛡️ Defensive Grind Validation")
        st.markdown('<div class="defensive-alert">', unsafe_allow_html=True)
        for reason in analysis['defensive_grind_reasons']:
            st.markdown(f"- {reason}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Layer 3: Capital Allocation
    st.markdown("---")
    st.markdown("### 💰 Layer 3: Professional Capital Allocation")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Recommended Stake**")
        st.markdown(f"# {analysis['recommended_stake']}%")
        st.markdown("of bankroll")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Form & Momentum**")
        st.metric(f"{analysis['match'].split(' vs ')[0]}", analysis['home_form'])
        st.metric(f"{analysis['match'].split(' vs ')[1]}", analysis['away_form'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Season Context**")
        st.metric("Home Position", analysis.get('home_season_position', 'N/A'))
        st.metric("Away Position", analysis.get('away_season_position', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Recent Scoring**")
        st.metric("Home Goals Last 5", analysis.get('home_goals_last_5', 0))
        st.metric("Away Goals Last 5", analysis.get('away_goals_last_5', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Professional Notes
    st.markdown("#### 📝 Professional Notes & Market Translation")
    notes = generate_professional_notes(analysis)
    for note in notes:
        st.markdown(f"- {note}")

def generate_professional_notes(analysis):
    """Generate professional betting notes"""
    notes = []
    archetype = analysis['archetype']
    
    if archetype == 'FADE_THE_FAVORITE':
        notes.append("**Primary Bet:** Back the underdog or draw")
        notes.append("**Secondary:** Consider Over 2.5 if both attacks competent")
        notes.append("**Key Risk:** Market may overvalue favorite's reputation")
        
    elif archetype == 'GOALS_GALORE':
        notes.append("**Primary Bet:** Over 2.5 Goals")
        if analysis['tactical_edge'].get('both_competent', False):
            notes.append("**Secondary:** Both Teams to Score (Yes)")
        else:
            notes.append("**Caution:** BTTS less likely - one team may not score")
        notes.append("**Key Insight:** Defensive crisis creates scoring opportunities")
        
    elif archetype == 'DEFENSIVE_GRIND':
        notes.append("**Primary Bet:** Under 2.5 Goals")
        notes.append("**Secondary:** Consider 0-0 or 1-0 Correct Score (small stake)")
        notes.append("**Key Insight:** Styles cancel, risk aversion present")
        notes.append("**Risk:** Early goal changes everything - stake conservatively")
        
    elif archetype == 'BACK_THE_UNDERDOG':
        notes.append("**Primary Bet:** Underdog to win or double chance")
        notes.append("**Consider:** Smaller stake due to medium confidence")
        notes.append("**Key Insight:** Underperformance creating value opportunity")
        
    elif archetype == 'AVOID':
        notes.append("**Action:** NO BET - Preserve capital")
        notes.append("**Reason:** Insufficient quantitative edge")
        notes.append("**Professional Move:** Wait for clearer opportunities")
    
    # Add crisis-specific notes
    home_crisis = analysis['crisis_analysis']['home']['severity']
    away_crisis = analysis['crisis_analysis']['away']['severity']
    
    if home_crisis == 'CRITICAL' and away_crisis == 'CRITICAL':
        notes.append("🚨 **Dual defensive crisis** - Expect chaotic, high-scoring match")
    elif home_crisis == 'CRITICAL' or away_crisis == 'CRITICAL':
        notes.append("⚠️ **Single-team defensive crisis** - Exploit with goals or fade")
    
    return notes

def create_report(analysis):
    """Create downloadable report"""
    report = f"""
BRUTBALL PROFESSIONAL ANALYSIS REPORT v3.0
==========================================

Match: {analysis['match']}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
System Version: Quantitative Framework v3.0

LAYER 1: QUANTITATIVE SITUATION ANALYSIS
---------------------------------------
Home Team ({analysis['match'].split(' vs ')[0]}):
- Crisis Score: {analysis['crisis_analysis']['home']['score']}
- Severity: {analysis['crisis_analysis']['home']['severity']}
- xG Analysis: {analysis['reality_check']['home']['type']}
- xG Deviation: {analysis['reality_check']['home']['deviation']:.2f}
- Attack xG: {analysis['home_attack_xg']:.2f}/game
- Form: {analysis['home_form']}
- Season Position: {analysis.get('home_season_position', 'N/A')}
- Goals Last 5: {analysis.get('home_goals_last_5', 0)}

Away Team ({analysis['match'].split(' vs ')[1]}):
- Crisis Score: {analysis['crisis_analysis']['away']['score']}
- Severity: {analysis['crisis_analysis']['away']['severity']}
- xG Analysis: {analysis['reality_check']['away']['type']}
- xG Deviation: {analysis['reality_check']['away']['deviation']:.2f}
- Attack xG: {analysis['away_attack_xg']:.2f}/game
- Form: {analysis['away_form']}
- Season Position: {analysis.get('away_season_position', 'N/A')}
- Goals Last 5: {analysis.get('away_goals_last_5', 0)}

Tactical Edge Score: {analysis['tactical_edge']['score']:.1f}/10

LAYER 2: DECISION CLASSIFICATION
--------------------------------
Archetype: {analysis['archetype'].replace('_', ' ')}
Confidence Score: {analysis['confidence']}/10

Quantitative Scores:
- Fade Score: {analysis['quantitative_scores']['fade']:.1f}
- Goals Score: {analysis['quantitative_scores']['goals']:.1f}
- Back Score: {analysis['quantitative_scores']['back']:.1f}
- Defensive Grind Score: {analysis['quantitative_scores']['defensive_grind']:.1f}

Decision Rationale:
{chr(10).join(analysis['rationale'])}

LAYER 3: CAPITAL ALLOCATION
--------------------------
Recommended Stake: {analysis['recommended_stake']}% of bankroll

PROFESSIONAL RECOMMENDATION:
{chr(10).join(generate_professional_notes(analysis))}

==========================================
Brutball Professional Framework v3.0
Complete Quantitative Decision System
All CSV Headings Utilized
    """
    return report

def render_performance_dashboard(engine):
    """Render performance tracking dashboard"""
    with st.expander("📊 Performance Dashboard", expanded=False):
        stats = engine.get_performance_stats()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Decisions", stats['total_decisions'])
            with col2:
                st.metric("Bets Recommended", stats['bets_recommended'])
            with col3:
                avoid_rate = stats['avoid_count'] / stats['total_decisions'] * 100 if stats['total_decisions'] > 0 else 0
                st.metric("Avoid Rate", f"{avoid_rate:.1f}%")
            
            # Archetype distribution
            st.markdown("#### Archetype Distribution")
            arch_data = stats['archetype_distribution']
            
            for archetype, count in arch_data.items():
                percentage = count / stats['total_decisions'] * 100
                st.progress(percentage/100, text=f"{archetype}: {count} ({percentage:.1f}%)")
            
            st.metric("Average Confidence", f"{stats.get('avg_confidence', 0):.1f}/10")
        else:
            st.info("Performance data will appear after analyzing matches.")

def render_data_preview(df, original_columns):
    """Render data preview expander"""
    with st.expander("📁 Data Overview", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Teams Loaded", len(df))
            st.metric("Data Columns", len(df.columns))
        with col2:
            st.metric("Original Columns", len(original_columns))
            st.metric("Derived Columns", len(df.columns) - len(original_columns))
        
        st.markdown("#### Data Preview")
        st.dataframe(df.head(10))
        
        st.markdown("#### Column Summary")
        column_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            total = len(df)
            pct = (non_null / total) * 100
            column_info.append([col, dtype, non_null, f"{pct:.1f}%"])
        
        column_df = pd.DataFrame(column_info, columns=['Column', 'Type', 'Non-Null', 'Complete %'])
        st.dataframe(column_df)

def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>Brutball Professional Decision Framework v3.0 • Complete Quantitative System</p>
        <p>All CSV headings utilized • For professional use only • All betting involves risk</p>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APP ===================
def main():
    """Main application function"""
    
    # Render header
    render_header()
    
    # Load data
    df, original_columns = load_league_data()
    if df is None:
        st.error("Failed to load data. Please check your data file.")
        return
    
    # Initialize engine
    engine = BrutballQuantitativeEngine(df)
    
    # Render framework status
    render_framework_status()
    
    # System configuration
    render_system_configuration(engine)
    
    # Performance dashboard
    render_performance_dashboard(engine)
    
    # Render match analysis
    render_match_analysis(engine, df)
    
    # Render data preview
    render_data_preview(df, original_columns)
    
    # Render footer
    render_footer()

# =================== RUN APP ===================
if __name__ == "__main__":
    main()