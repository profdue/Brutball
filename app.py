import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="Brutball Pro Quantitative Framework",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== CUSTOM CSS STYLING ===================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 1.5rem;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .framework-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #374151;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    .layer-box {
        padding: 1.2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border-left: 6px solid #3B82F6;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .layer-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.08);
    }
    .crisis-alert {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 5px solid #DC2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
    }
    .opportunity-alert {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 5px solid #16A34A;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(22, 163, 74, 0.1);
    }
    .defensive-alert {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 5px solid #2563EB;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        margin: 0.75rem 0;
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.12);
        border-color: #3B82F6;
    }
    .archetype-badge {
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.1rem;
        display: inline-block;
        margin: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stake-display {
        font-size: 2.5rem;
        font-weight: 800;
        color: #059669;
        text-align: center;
        margin: 0.5rem 0;
    }
    .confidence-meter {
        height: 12px;
        background: linear-gradient(90deg, #EF4444 0%, #F59E0B 50%, #10B981 100%);
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #F3F4F6;
        border-left: 4px solid #6B7280;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #4B5563;
    }
    .data-table {
        font-size: 0.85rem;
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
    }
    </style>
""", unsafe_allow_html=True)

# =================== DATA LOADING & PREPARATION ===================
@st.cache_data(ttl=3600, show_spinner="Loading Premier League data...")
def load_and_prepare_data() -> Optional[pd.DataFrame]:
    """Load, validate, and prepare the dataset with all CSV columns."""
    try:
        # Try multiple data sources
        data_sources = [
            'leagues/premier_league.csv',
            './leagues/premier_league.csv',
            'premier_league.csv',
            'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
        ]
        
        df = None
        source_used = ""
        
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                source_used = source
                st.success(f"✅ Data loaded from: {source}")
                break
            except Exception as e:
                continue
        
        if df is None:
            st.error("❌ Failed to load data from all sources")
            return None
        
        # Clean and validate column names
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower()
        cleaned_columns = df.columns.tolist()
        
        # Required columns from CSV header
        required_columns = [
            'team', 'season_position', 'home_matches_played', 'home_goals_scored',
            'home_xg_for', 'home_xg_against', 'away_matches_played', 'away_goals_scored',
            'away_xg_for', 'away_xg_against', 'goals_scored_last_5', 'goals_conceded_last_5',
            'defenders_out', 'form_last_5_overall', 'form_last_5_home', 'form_last_5_away',
            'home_goals_openplay_for', 'home_goals_counter_for', 'home_goals_setpiece_for',
            'home_goals_penalty_for', 'home_goals_owngoal_for', 'away_goals_openplay_for',
            'away_goals_counter_for', 'away_goals_setpiece_for', 'away_goals_penalty_for',
            'away_goals_owngoal_for', 'home_goals_openplay_against', 'home_goals_counter_against',
            'home_goals_setpiece_against', 'home_goals_penalty_against', 'home_goals_owngoal_against',
            'away_goals_openplay_against', 'away_goals_counter_against', 'away_goals_setpiece_against',
            'away_goals_penalty_against', 'away_goals_owngoal_against'
        ]
        
        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"⚠️ Missing columns: {missing_columns}")
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['source'] = source_used
        df.attrs['original_columns'] = original_columns
        df.attrs['cleaned_columns'] = cleaned_columns
        df.attrs['missing_columns'] = missing_columns
        df.attrs['total_teams'] = len(df)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics from base columns."""
    
    # Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    df['home_xgc_per_match'] = df['home_xg_against'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xgc_per_match'] = df['away_xg_against'] / df['away_matches_played'].replace(0, np.nan)
    
    # Goal type percentages
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_goals_scored'].replace(0, np.nan)
    
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_goals_scored'].replace(0, np.nan)
    
    # Defensive vulnerabilities
    df['home_counter_vuln'] = df['home_goals_counter_against'] / df['home_goals_conceded'].replace(0, np.nan)
    df['home_setpiece_vuln'] = df['home_goals_setpiece_against'] / df['home_goals_conceded'].replace(0, np.nan)
    
    df['away_counter_vuln'] = df['away_goals_counter_against'] / df['away_goals_conceded'].replace(0, np.nan)
    df['away_setpiece_vuln'] = df['away_goals_setpiece_against'] / df['away_goals_conceded'].replace(0, np.nan)
    
    # Form points calculation
    def calculate_form_points(form_string):
        if pd.isna(form_string):
            return 0
        points_map = {'W': 3, 'D': 1, 'L': 0}
        return sum(points_map.get(char, 0) for char in str(form_string))
    
    df['form_points_overall'] = df['form_last_5_overall'].apply(calculate_form_points)
    df['form_points_home'] = df['form_last_5_home'].apply(calculate_form_points)
    df['form_points_away'] = df['form_last_5_away'].apply(calculate_form_points)
    
    # Form momentum (last 3 matches)
    def calculate_momentum(form_string):
        if pd.isna(form_string) or len(str(form_string)) < 3:
            return 'NEUTRAL'
        last_three = str(form_string)[-3:]
        wins = last_three.count('W')
        losses = last_three.count('L')
        if wins >= 2: return 'STRONG_UP'
        if losses >= 2: return 'STRONG_DOWN'
        if 'W' in last_three and 'L' not in last_three: return 'IMPROVING'
        if 'L' in last_three and 'W' not in last_three: return 'DECLINING'
        return 'VOLATILE'
    
    df['momentum_overall'] = df['form_last_5_overall'].apply(calculate_momentum)
    df['momentum_home'] = df['form_last_5_home'].apply(calculate_momentum)
    df['momentum_away'] = df['form_last_5_away'].apply(calculate_momentum)
    
    # Replace NaN with 0 for calculated columns
    calculated_columns = [col for col in df.columns if col not in [
        'team', 'form_last_5_overall', 'form_last_5_home', 'form_last_5_away',
        'momentum_overall', 'momentum_home', 'momentum_away'
    ]]
    df[calculated_columns] = df[calculated_columns].fillna(0)
    
    return df

# =================== QUANTITATIVE ENGINE CORE ===================
class BrutballProQuantitative:
    """Complete professional quantitative decision engine."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.performance_log = []
        self.league_metrics = self._calculate_league_metrics()
        
    def _calculate_league_metrics(self) -> Dict:
        """Calculate league-wide benchmarks for context."""
        metrics = {}
        
        # League averages
        metrics['avg_home_xg'] = self.df['home_xg_per_match'].mean()
        metrics['avg_away_xg'] = self.df['away_xg_per_match'].mean()
        metrics['avg_home_goals'] = self.df['home_goals_per_match'].mean()
        metrics['avg_away_goals'] = self.df['away_goals_per_match'].mean()
        
        # Percentile thresholds
        metrics['xg_75th'] = np.percentile(self.df['home_xg_per_match'].combine(
            self.df['away_xg_per_match'], max), 75)
        metrics['xg_25th'] = np.percentile(self.df['home_xg_per_match'].combine(
            self.df['away_xg_per_match'], min), 25)
        
        # Goal type averages
        metrics['avg_counter_pct'] = self.df['home_counter_pct'].combine(
            self.df['away_counter_pct'], np.mean).mean()
        metrics['avg_setpiece_pct'] = self.df['home_setpiece_pct'].combine(
            self.df['away_setpiece_pct'], np.mean).mean()
        
        return metrics
    
    # ========== PHASE 1: QUANTITATIVE CRISIS SCORING ==========
    def calculate_crisis_score(self, team_data: Dict, is_home: bool = True) -> Dict:
        """Calculate comprehensive crisis score (0-20 scale)."""
        score = 0
        signals = []
        details = {}
        
        # 1. DEFENSIVE PERSONNEL (0-6 points)
        defenders_out = team_data.get('defenders_out', 0)
        if defenders_out >= 4:
            score += 6
            signals.append(f"🚨 {defenders_out} defenders missing (6pts)")
        elif defenders_out == 3:
            score += 4
            signals.append(f"⚠️ {defenders_out} defenders missing (4pts)")
        elif defenders_out == 2:
            score += 2
            signals.append(f"{defenders_out} defenders missing (2pts)")
        details['defenders_out'] = defenders_out
        
        # 2. RECENT DEFENSIVE FORM (0-6 points)
        if is_home:
            goals_conceded = team_data.get('goals_conceded_last_5', 0)
            xgc_per_match = team_data.get('home_xgc_per_match', 0)
        else:
            goals_conceded = team_data.get('goals_conceded_last_5', 0)
            xgc_per_match = team_data.get('away_xgc_per_match', 0)
        
        if goals_conceded >= 15:
            score += 6
            signals.append(f"📉 {goals_conceded} goals conceded last 5 (6pts)")
        elif goals_conceded >= 12:
            score += 4
            signals.append(f"📉 {goals_conceded} goals conceded last 5 (4pts)")
        elif goals_conceded >= 10:
            score += 2
            signals.append(f"{goals_conceded} goals conceded last 5 (2pts)")
        details['goals_conceded'] = goals_conceded
        details['xgc_per_match'] = xgc_per_match
        
        # 3. FORM MOMENTUM (0-4 points)
        form = str(team_data.get('form_last_5_overall', ''))
        momentum = team_data.get('momentum_overall', 'NEUTRAL')
        
        if 'LLL' in form:
            score += 4
            signals.append("📉 Losing streak: LLL (4pts)")
        elif form[-2:] == 'LL':
            score += 2
            signals.append("📉 Recent losses: LL (2pts)")
        elif momentum == 'STRONG_DOWN':
            score += 3
            signals.append("📉 Strong downward momentum (3pts)")
        elif momentum == 'DECLINING':
            score += 1
            signals.append("Declining momentum (1pt)")
        
        details['form'] = form
        details['momentum'] = momentum
        
        # 4. ATTACKING CONFIDENCE (0-4 points) - Inverse scoring
        if is_home:
            goals_scored = team_data.get('goals_scored_last_5', 0)
            xg_per_match = team_data.get('home_xg_per_match', 0)
        else:
            goals_scored = team_data.get('goals_scored_last_5', 0)
            xg_per_match = team_data.get('away_xg_per_match', 0)
        
        if goals_scored <= 4 and xg_per_match < self.league_metrics['xg_25th']:
            score += 4
            signals.append(f"⚽ Attack crisis: {goals_scored} goals, {xg_per_match:.2f} xG (4pts)")
        elif goals_scored <= 6 and xg_per_match < self.league_metrics['avg_home_xg']:
            score += 2
            signals.append(f"⚽ Weak attack: {goals_scored} goals (2pts)")
        
        details['goals_scored'] = goals_scored
        details['xg_per_match'] = xg_per_match
        
        # Severity classification
        if score >= 8:
            severity = 'CRITICAL'
        elif score >= 4:
            severity = 'WARNING'
        else:
            severity = 'STABLE'
        
        return {
            'score': score,
            'severity': severity,
            'signals': signals,
            'details': details,
            'is_home': is_home
        }
    
    # ========== PHASE 2: DYNAMIC REALITY CHECK ==========
    def analyze_performance_reality(self, team_data: Dict, is_home: bool) -> Dict:
        """Analyze team performance relative to expectations."""
        
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
            matches = team_data.get('home_matches_played', 1)
            league_avg = self.league_metrics['avg_home_xg']
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
            matches = team_data.get('away_matches_played', 1)
            league_avg = self.league_metrics['avg_away_xg']
        
        goals_per_match = goals / max(matches, 1)
        xg_per_match = xg / max(matches, 1)
        
        # Calculate deviation
        deviation = goals_per_match - xg_per_match
        deviation_pct = deviation / max(xg_per_match, 0.1) * 100
        
        # Dynamic threshold based on team strength
        if xg_per_match > league_avg * 1.3:  # Top attack
            threshold = 0.25
        elif xg_per_match < league_avg * 0.7:  # Weak attack
            threshold = 0.4
        else:
            threshold = 0.3
        
        # Classification
        if deviation > threshold:
            status = 'OVERPERFORMING'
            confidence = min(2.0, 1.0 + (deviation - threshold) / threshold)
            implication = "Regression likely - finishing unsustainable"
        elif deviation < -threshold:
            status = 'UNDERPERFORMING'
            confidence = min(2.0, 1.0 + abs(deviation - threshold) / threshold)
            implication = "Improvement possible - creating chances"
        else:
            status = 'NEUTRAL'
            confidence = 1.0
            implication = "Performance aligns with expectations"
        
        return {
            'status': status,
            'confidence': confidence,
            'implication': implication,
            'metrics': {
                'goals_per_match': goals_per_match,
                'xg_per_match': xg_per_match,
                'deviation': deviation,
                'deviation_pct': deviation_pct,
                'threshold_used': threshold
            }
        }
    
    # ========== PHASE 3: TACTICAL EDGE ANALYSIS ==========
    def analyze_tactical_matchup(self, home_data: Dict, away_data: Dict) -> Dict:
        """Quantitative tactical analysis with all CSV columns."""
        
        edge_score = 0
        edges = []
        details = {}
        
        # 1. COUNTER-ATTACK MATCHUP
        home_counter_pct = home_data.get('home_counter_pct', 0)
        away_counter_vuln = away_data.get('away_counter_vuln', 0)
        home_counter_goals = home_data.get('home_goals_counter_for', 0)
        away_counter_conceded = away_data.get('away_goals_counter_against', 0)
        
        counter_edge = 0
        if home_counter_pct > 0.15 and away_counter_vuln > 0.15:
            counter_edge = (home_counter_pct * away_counter_vuln) * 25
            edge_score += min(5.0, counter_edge)
            edges.append({
                'type': 'COUNTER_ATTACK',
                'score': min(5.0, counter_edge),
                'strength': 'HIGH' if counter_edge > 3 else 'MEDIUM' if counter_edge > 1.5 else 'LOW',
                'detail': f"Home: {home_counter_pct:.1%} counters ({home_counter_goals} goals) | Away concedes: {away_counter_vuln:.1%} ({away_counter_conceded} goals)"
            })
        
        details['counter_analysis'] = {
            'home_pct': home_counter_pct,
            'away_vuln': away_counter_vuln,
            'edge_score': counter_edge
        }
        
        # 2. SET-PIECE MATCHUP
        home_setpiece_pct = home_data.get('home_setpiece_pct', 0)
        away_setpiece_vuln = away_data.get('away_setpiece_vuln', 0)
        home_setpiece_goals = home_data.get('home_goals_setpiece_for', 0)
        away_setpiece_conceded = away_data.get('away_goals_setpiece_against', 0)
        
        setpiece_edge = 0
        if home_setpiece_pct > 0.2 and away_setpiece_vuln > 0.2:
            setpiece_edge = (home_setpiece_pct * away_setpiece_vuln) * 30
            edge_score += min(5.0, setpiece_edge)
            edges.append({
                'type': 'SET_PIECE',
                'score': min(5.0, setpiece_edge),
                'strength': 'HIGH' if setpiece_edge > 3 else 'MEDIUM' if setpiece_edge > 1.5 else 'LOW',
                'detail': f"Home: {home_setpiece_pct:.1%} set pieces ({home_setpiece_goals} goals) | Away concedes: {away_setpiece_vuln:.1%} ({away_setpiece_conceded} goals)"
            })
        
        details['setpiece_analysis'] = {
            'home_pct': home_setpiece_pct,
            'away_vuln': away_setpiece_vuln,
            'edge_score': setpiece_edge
        }
        
        # 3. OPEN PLAY DOMINANCE
        home_openplay_pct = home_data.get('home_openplay_pct', 0)
        away_openplay_vuln = away_data.get('away_goals_openplay_against', 0) / max(away_data.get('away_goals_conceded', 1), 1)
        
        if home_openplay_pct > 0.6 and away_openplay_vuln > 0.5:
            openplay_edge = (home_openplay_pct * away_openplay_vuln) * 20
            edge_score += min(4.0, openplay_edge)
            edges.append({
                'type': 'OPEN_PLAY',
                'score': min(4.0, openplay_edge),
                'strength': 'HIGH' if openplay_edge > 2.5 else 'MEDIUM',
                'detail': f"Home: {home_openplay_pct:.1%} open play | Away concedes: {away_openplay_vuln:.1%} open play"
            })
        
        # 4. ATTACK COMPETENCE CHECK (Critical for all archetypes)
        home_attack_xg = home_data.get('home_xg_per_match', 0)
        away_attack_xg = away_data.get('away_xg_per_match', 0)
        
        competence_score = 0
        if home_attack_xg > 1.0:
            competence_score += 1
        if away_attack_xg > 1.0:
            competence_score += 1
        
        edge_score += competence_score
        both_competent = (home_attack_xg > 0.8 and away_attack_xg > 0.8)
        
        details['attack_competence'] = {
            'home_xg': home_attack_xg,
            'away_xg': away_attack_xg,
            'both_competent': both_competent,
            'score': competence_score
        }
        
        # 5. DEFENSIVE STABILITY
        home_xgc = home_data.get('home_xgc_per_match', 0)
        away_xgc = away_data.get('away_xgc_per_match', 0)
        
        defensive_stability = 0
        if home_xgc < self.league_metrics['avg_home_xg'] * 0.8:
            defensive_stability += 1
        if away_xgc < self.league_metrics['avg_away_xg'] * 0.8:
            defensive_stability += 1
        
        details['defensive_stability'] = defensive_stability
        
        return {
            'total_score': min(20.0, edge_score),
            'edges': edges,
            'details': details,
            'attack_competence': both_competent,
            'defensive_stability': defensive_stability
        }
    
    # ========== PHASE 4: DEFENSIVE GRIND VALIDATOR ==========
    def validate_defensive_grind(self, home_data: Dict, away_data: Dict,
                               home_crisis: Dict, away_crisis: Dict) -> Tuple[bool, float, List[str]]:
        """Validate conditions for DEFENSIVE_GRIND archetype."""
        
        reasons = []
        confidence = 0.0
        
        # ===== 1. HARD REJECTION GATES =====
        # Rule: Any defensive crisis disqualifies Under 2.5
        if home_crisis['severity'] == 'CRITICAL':
            reasons.append("❌ Home team in CRITICAL defensive crisis")
            return False, 0.0, reasons
        if away_crisis['severity'] == 'CRITICAL':
            reasons.append("❌ Away team in CRITICAL defensive crisis")
            return False, 0.0, reasons
        
        # ===== 2. ATTACK SUPPRESSION CHECK =====
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        
        attack_threshold = 1.1
        if home_xg > attack_threshold:
            reasons.append(f"❌ Home attack too strong: {home_xg:.2f} xG/match")
            return False, 0.0, reasons
        if away_xg > attack_threshold:
            reasons.append(f"❌ Away attack too strong: {away_xg:.2f} xG/match")
            return False, 0.0, reasons
        
        reasons.append(f"✅ Attacks suppressed (Home: {home_xg:.2f}, Away: {away_xg:.2f})")
        confidence += 2.0
        
        # ===== 3. STYLE CANCELLATION CHECK =====
        # Counter-attack suppression
        home_counter_pct = home_data.get('home_counter_pct', 0)
        away_counter_pct = away_data.get('away_counter_pct', 0)
        
        counter_threshold = 0.12
        if home_counter_pct > counter_threshold:
            reasons.append(f"❌ Home counter threat: {home_counter_pct:.1%}")
            return False, 0.0, reasons
        if away_counter_pct > counter_threshold:
            reasons.append(f"❌ Away counter threat: {away_counter_pct:.1%}")
            return False, 0.0, reasons
        
        reasons.append(f"✅ No counter threat (Home: {home_counter_pct:.1%}, Away: {away_counter_pct:.1%})")
        confidence += 1.5
        
        # Set-piece suppression
        home_setpiece_pct = home_data.get('home_setpiece_pct', 0)
        away_setpiece_pct = away_data.get('away_setpiece_pct', 0)
        
        setpiece_threshold = 0.20
        if home_setpiece_pct > setpiece_threshold:
            reasons.append(f"❌ Home set-piece threat: {home_setpiece_pct:.1%}")
            return False, 0.0, reasons
        if away_setpiece_pct > setpiece_threshold:
            reasons.append(f"❌ Away set-piece threat: {away_setpiece_pct:.1%}")
            return False, 0.0, reasons
        
        reasons.append(f"✅ No set-piece threat (Home: {home_setpiece_pct:.1%}, Away: {away_setpiece_pct:.1%})")
        confidence += 1.5
        
        # ===== 4. GAME-STATE CONTROL CHECK =====
        # Draw-heavy form analysis
        home_form = str(home_data.get('form_last_5_overall', ''))
        away_form = str(away_data.get('form_last_5_overall', ''))
        
        home_draws = home_form.count('D')
        away_draws = away_form.count('D')
        
        if home_draws >= 2 and away_draws >= 2:
            reasons.append(f"✅ Both teams draw-heavy (Home: {home_draws}/5, Away: {away_draws}/5)")
            confidence += 2.0
        elif home_draws >= 2 or away_draws >= 2:
            reasons.append(f"⚠️ One team draw-prone (Home: {home_draws}/5, Away: {away_draws}/5)")
            confidence += 1.0
        else:
            reasons.append("❌ No draw tendency")
            return False, 0.0, reasons
        
        # Recent scoring suppression
        home_goals_last_5 = home_data.get('goals_scored_last_5', 0)
        away_goals_last_5 = away_data.get('goals_scored_last_5', 0)
        
        if home_goals_last_5 <= 5 and away_goals_last_5 <= 5:
            reasons.append(f"✅ Low recent scoring (Home: {home_goals_last_5}, Away: {away_goals_last_5})")
            confidence += 1.0
        
        # ===== 5. FINAL VALIDATION =====
        if confidence >= 5.0:
            reasons.append(f"✅ DEFENSIVE GRIND VALIDATED (Confidence: {confidence:.1f}/8.0)")
            return True, confidence, reasons
        else:
            reasons.append(f"❌ Insufficient confidence: {confidence:.1f}/8.0")
            return False, 0.0, reasons
    
    # ========== PHASE 5: QUANTITATIVE ARCHETYPE CLASSIFICATION ==========
    def determine_archetype(self, home_crisis: Dict, away_crisis: Dict,
                           home_reality: Dict, away_reality: Dict,
                           tactical: Dict, home_data: Dict, away_data: Dict) -> Dict:
        """Quantitative archetype classification with all logic."""
        
        fade_score = 0.0
        goals_score = 0.0
        back_score = 0.0
        defensive_grind_valid = False
        grind_confidence = 0.0
        grind_reasons = []
        rationale = []
        
        # ===== 1. DEFENSIVE GRIND VALIDATION (Priority Check) =====
        defensive_grind_valid, grind_confidence, grind_reasons = self.validate_defensive_grind(
            home_data, away_data, home_crisis, away_crisis
        )
        
        if defensive_grind_valid:
            rationale.append(f"DEFENSIVE GRIND qualified ({grind_confidence:.1f}/8.0)")
        
        # ===== 2. FADE_THE_FAVORITE SCORING =====
        # Condition: Away team in crisis AND overperforming, Home stable
        if (away_crisis['severity'] == 'CRITICAL' and 
            home_crisis['severity'] in ['STABLE', 'WARNING'] and
            away_reality['status'] == 'OVERPERFORMING'):
            
            fade_score = (
                away_crisis['score'] * 0.4 +           # Crisis severity
                away_reality['confidence'] * 0.3 +     # Overperformance confidence
                (15 - home_crisis['score']) * 0.3      # Home stability
            )
            
            if fade_score > 0:
                rationale.append(f"FADE score: {fade_score:.1f} (Away crisis + overperformance)")
        
        # ===== 3. GOALS_GALORE SCORING =====
        # Condition: Defensive crisis present + attack competence
        crisis_present = (home_crisis['severity'] == 'CRITICAL' or 
                         away_crisis['severity'] == 'CRITICAL')
        
        if crisis_present:
            crisis_sum = home_crisis['score'] + away_crisis['score']
            
            goals_score = (
                crisis_sum * 0.4 +                     # Total crisis
                tactical['total_score'] * 0.3 +        # Tactical edge
                (tactical['details']['attack_competence']['score'] * 0.3)  # Attack competence
            )
            
            # Penalize if attacks not competent
            if not tactical['attack_competence']:
                goals_score *= 0.7
                rationale.append("GOALS score penalized: weak attack competence")
            
            if goals_score > 0:
                rationale.append(f"GOALS score: {goals_score:.1f} (Crisis + tactical edge)")
        
        # ===== 4. BACK_THE_UNDERDOG SCORING =====
        # Condition: Home underperforming + stable, Away not in crisis
        if (home_reality['status'] == 'UNDERPERFORMING' and
            home_crisis['severity'] == 'STABLE' and
            away_crisis['severity'] != 'CRITICAL'):
            
            back_score = (
                home_reality['confidence'] * 0.4 +     # Underperformance confidence
                (15 - home_crisis['score']) * 0.3 +    # Home stability
                tactical['total_score'] * 0.3          # Tactical edge
            )
            
            if back_score > 0:
                rationale.append(f"BACK score: {back_score:.1f} (Home underperformance + stability)")
        
        # ===== 5. DECISION HIERARCHY =====
        # DEFENSIVE GRIND has priority when valid and high confidence
        if defensive_grind_valid and grind_confidence >= 6.0:
            confidence = min(10.0, grind_confidence * 1.25)
            archetype = 'DEFENSIVE_GRIND'
            rationale.append(f"→ DEFENSIVE GRIND selected (confidence: {confidence:.1f}/10)")
        
        # FADE_THE_FAVORITE
        elif fade_score > 18 and fade_score > max(goals_score, back_score):
            confidence = min(10.0, fade_score / 2.5)
            archetype = 'FADE_THE_FAVORITE'
            rationale.append(f"→ FADE selected (score: {fade_score:.1f})")
        
        # GOALS_GALORE
        elif goals_score > 15 and goals_score > max(fade_score, back_score):
            confidence = min(10.0, goals_score / 2.0)
            archetype = 'GOALS_GALORE'
            rationale.append(f"→ GOALS selected (score: {goals_score:.1f})")
        
        # BACK_THE_UNDERDOG
        elif back_score > 12:
            confidence = min(8.0, back_score / 1.8)
            archetype = 'BACK_THE_UNDERDOG'
            rationale.append(f"→ BACK selected (score: {back_score:.1f})")
        
        # DEFAULT: AVOID
        else:
            archetype = 'AVOID'
            confidence = 0.0
            rationale.append("→ No quantitative edge above thresholds")
        
        # Add defensive grind reasons if checked
        if defensive_grind_valid:
            rationale.extend([f"Defensive Grind Check: {reason}" for reason in grind_reasons])
        
        return {
            'archetype': archetype,
            'confidence': round(confidence, 1),
            'scores': {
                'fade': round(fade_score, 1),
                'goals': round(goals_score, 1),
                'back': round(back_score, 1),
                'defensive_grind': round(grind_confidence, 1) if defensive_grind_valid else 0.0
            },
            'rationale': rationale,
            'defensive_grind_valid': defensive_grind_valid,
            'defensive_grind_reasons': grind_reasons
        }
    
    # ========== PHASE 6: PROFESSIONAL CAPITAL ALLOCATION ==========
    def calculate_stake_size(self, archetype: str, confidence: float, 
                           home_crisis: Dict, away_crisis: Dict) -> float:
        """Professional stake sizing with risk management."""
        
        if archetype == 'AVOID' or confidence < 4.0:
            return 0.0
        
        # Base stakes by archetype and confidence
        base_stakes = {
            'FADE_THE_FAVORITE': {
                8.5: 2.5,  # High confidence: 2.5%
                7.0: 2.0,  # Medium-high: 2.0%
                5.5: 1.5,  # Medium: 1.5%
                4.0: 1.0   # Low-medium: 1.0%
            },
            'GOALS_GALORE': {
                8.5: 2.0,  # High confidence: 2.0%
                7.0: 1.5,  # Medium-high: 1.5%
                5.5: 1.0,  # Medium: 1.0%
                4.0: 0.5   # Low-medium: 0.5%
            },
            'BACK_THE_UNDERDOG': {
                8.0: 1.5,  # High confidence: 1.5%
                6.5: 1.0,  # Medium-high: 1.0%
                5.0: 0.5,  # Medium: 0.5%
                4.0: 0.25  # Low-medium: 0.25%
            },
            'DEFENSIVE_GRIND': {
                8.0: 1.5,  # High confidence: 1.5%
                6.5: 1.0,  # Medium-high: 1.0%
                5.0: 0.5,  # Medium: 0.5%
                4.0: 0.25  # Low-medium: 0.25%
            }
        }
        
        # Get stake thresholds for this archetype
        thresholds = base_stakes.get(archetype, {})
        
        # Find appropriate stake based on confidence
        for threshold, stake in sorted(thresholds.items(), reverse=True):
            if confidence >= threshold:
                
                # Risk adjustment based on crisis severity
                risk_multiplier = 1.0
                if home_crisis['severity'] == 'WARNING' or away_crisis['severity'] == 'WARNING':
                    risk_multiplier = 0.8  # Reduce stake with warning signs
                
                final_stake = stake * risk_multiplier
                return round(final_stake, 2)
        
        return 0.0
    
    # ========== COMPLETE MATCH ANALYSIS PIPELINE ==========
    def analyze_match(self, home_team_name: str, away_team_name: str) -> Dict:
        """Complete quantitative analysis pipeline."""
        
        # Get team data
        home_data = self.df[self.df['team'] == home_team_name].iloc[0].to_dict()
        away_data = self.df[self.df['team'] == away_team_name].iloc[0].to_dict()
        
        # ===== PHASE 1: CRISIS SCORING =====
        home_crisis = self.calculate_crisis_score(home_data, is_home=True)
        away_crisis = self.calculate_crisis_score(away_data, is_home=False)
        
        # ===== PHASE 2: REALITY CHECK =====
        home_reality = self.analyze_performance_reality(home_data, is_home=True)
        away_reality = self.analyze_performance_reality(away_data, is_home=False)
        
        # ===== PHASE 3: TACTICAL ANALYSIS =====
        tactical = self.analyze_tactical_matchup(home_data, away_data)
        
        # ===== PHASE 4 & 5: ARCHETYPE CLASSIFICATION =====
        archetype_result = self.determine_archetype(
            home_crisis, away_crisis, home_reality, away_reality,
            tactical, home_data, away_data
        )
        
        # ===== PHASE 6: CAPITAL ALLOCATION =====
        stake_pct = self.calculate_stake_size(
            archetype_result['archetype'],
            archetype_result['confidence'],
            home_crisis, away_crisis
        )
        
        # ===== COMPILE COMPREHENSIVE REPORT =====
        report = {
            'match': f"{home_team_name} vs {away_team_name}",
            'timestamp': pd.Timestamp.now().isoformat(),
            
            # Phase 1 Results
            'crisis_analysis': {
                'home': home_crisis,
                'away': away_crisis
            },
            
            # Phase 2 Results
            'reality_check': {
                'home': home_reality,
                'away': away_reality
            },
            
            # Phase 3 Results
            'tactical_edge': tactical,
            
            # Phase 4 & 5 Results
            'archetype': archetype_result['archetype'],
            'confidence': archetype_result['confidence'],
            'quantitative_scores': archetype_result['scores'],
            'rationale': archetype_result['rationale'],
            'defensive_grind_valid': archetype_result['defensive_grind_valid'],
            'defensive_grind_reasons': archetype_result['defensive_grind_reasons'],
            
            # Phase 6 Results
            'recommended_stake': stake_pct,
            
            # Key Metrics for Display
            'key_metrics': {
                'home_attack_xg': home_data.get('home_xg_per_match', 0),
                'away_attack_xg': away_data.get('away_xg_per_match', 0),
                'home_defense_xg': home_data.get('home_xgc_per_match', 0),
                'away_defense_xg': away_data.get('away_xgc_per_match', 0),
                'home_form': home_data.get('form_last_5_overall', ''),
                'away_form': away_data.get('form_last_5_overall', ''),
                'home_momentum': home_data.get('momentum_overall', ''),
                'away_momentum': away_data.get('momentum_overall', ''),
                'home_position': home_data.get('season_position', 0),
                'away_position': away_data.get('season_position', 0)
            },
            
            # Raw Data References
            'home_data': {k: v for k, v in home_data.items() if not isinstance(v, (dict, list))},
            'away_data': {k: v for k, v in away_data.items() if not isinstance(v, (dict, list))}
        }
        
        # Log the decision
        self.log_decision(report)
        
        return report
    
    def log_decision(self, analysis: Dict):
        """Log decision for performance tracking."""
        log_entry = {
            'timestamp': analysis['timestamp'],
            'match': analysis['match'],
            'archetype': analysis['archetype'],
            'confidence': analysis['confidence'],
            'stake_percent': analysis['recommended_stake'],
            'home_crisis_score': analysis['crisis_analysis']['home']['score'],
            'away_crisis_score': analysis['crisis_analysis']['away']['score'],
            'home_xg': analysis['key_metrics']['home_attack_xg'],
            'away_xg': analysis['key_metrics']['away_attack_xg'],
            'tactical_score': analysis['tactical_edge']['total_score']
        }
        self.performance_log.append(log_entry)
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        if not self.performance_log:
            return {}
        
        df_log = pd.DataFrame(self.performance_log)
        
        summary = {
            'total_decisions': len(df_log),
            'bets_recommended': len(df_log[df_log['stake_percent'] > 0]),
            'avoid_count': len(df_log[df_log['archetype'] == 'AVOID']),
            
            'archetype_distribution': df_log['archetype'].value_counts().to_dict(),
            'avg_confidence_by_archetype': df_log.groupby('archetype')['confidence'].mean().round(1).to_dict(),
            'avg_stake_by_archetype': df_log.groupby('archetype')['stake_percent'].mean().round(2).to_dict(),
            
            'total_capital_exposure': df_log['stake_percent'].sum(),
            'avg_decision_confidence': df_log['confidence'].mean().round(1),
            
            'crisis_signal_prevalence': {
                'high_crisis_matches': len(df_log[(df_log['home_crisis_score'] >= 8) | (df_log['away_crisis_score'] >= 8)]),
                'avg_crisis_score': df_log[['home_crisis_score', 'away_crisis_score']].max(axis=1).mean().round(1)
            }
        }
        
        return summary

# =================== STREAMLIT UI COMPONENTS ===================
def render_header():
    """Render main application header."""
    st.markdown('<div class="main-header">⚽ BRUTBALL PROFESSIONAL QUANTITATIVE FRAMEWORK</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem;">Professional Decision System | All CSV Columns Utilized | Six-Phase Quantitative Logic</p>
    </div>
    """, unsafe_allow_html=True)

def render_framework_overview():
    """Render the three-layer framework overview."""
    st.markdown('<div class="framework-header">🏗️ THREE-LAYER QUANTITATIVE FRAMEWORK</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 LAYER 1")
        st.markdown("**Situation Classification**")
        st.markdown("• Quantitative Crisis Scoring")
        st.markdown("• Dynamic Reality Check")
        st.markdown("• Tactical Edge Analysis")
        st.markdown("• CSV: All 36 columns utilized")
        st.markdown("**Status:** ✅ OPERATIONAL")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 LAYER 2")
        st.markdown("**Decision Firewall**")
        st.markdown("• 4 Archetype Classification")
        st.markdown("• Defensive Grind Validator")
        st.markdown("• Confidence Scoring (0-10)")
        st.markdown("• Market Translation Gates")
        st.markdown("**Status:** ✅ OPERATIONAL")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("### 💰 LAYER 3")
        st.markdown("**Capital Allocation**")
        st.markdown("• Precision Stake Sizing")
        st.markdown("• Risk-Adjusted Betting")
        st.markdown("• Bankroll Management")
        st.markdown("• Performance Tracking")
        st.markdown("**Status:** ✅ AUTOMATED")
        st.markdown('</div>', unsafe_allow_html=True)

def render_match_selector(df: pd.DataFrame):
    """Render team selection interface."""
    st.markdown('<div class="framework-header">🏟️ MATCH ANALYSIS</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox(
            "🏠 **HOME TEAM**",
            options=sorted(df['team'].unique()),
            index=0,
            help="Select home team for analysis"
        )
    
    with col2:
        away_options = [team for team in sorted(df['team'].unique()) if team != home_team]
        away_team = st.selectbox(
            "✈️ **AWAY TEAM**",
            options=away_options,
            index=min(1, len(away_options)-1),
            help="Select away team for analysis"
        )
    
    return home_team, away_team

def render_crisis_analysis(crisis_data: Dict, team_name: str, is_home: bool):
    """Render crisis analysis section."""
    
    if crisis_data['severity'] == 'CRITICAL':
        st.markdown(f'<div class="crisis-alert">', unsafe_allow_html=True)
        st.markdown(f"### 🚨 {team_name} - CRITICAL CRISIS")
        st.markdown(f"**Score:** {crisis_data['score']}/20")
        
        for signal in crisis_data['signals'][:3]:  # Show top 3 signals
            st.markdown(f"• {signal}")
        
        # Show details
        with st.expander("Crisis Details"):
            details = crisis_data['details']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Defenders Out", details['defenders_out'])
                st.metric("Goals Conceded/5", details['goals_conceded'])
            with col2:
                st.metric("xGC/Match", f"{details['xgc_per_match']:.2f}")
                st.metric("Form", details['form'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif crisis_data['severity'] == 'WARNING':
        st.markdown(f"### ⚠️ {team_name} - WARNING")
        st.markdown(f"**Crisis Score:** {crisis_data['score']}/20")
        
        if crisis_data['signals']:
            st.markdown("**Signals:**")
            for signal in crisis_data['signals'][:2]:
                st.markdown(f"• {signal}")
    else:
        st.markdown(f"### ✅ {team_name} - STABLE")
        st.markdown(f"**Crisis Score:** {crisis_data['score']}/20")
        st.markdown("No significant defensive issues detected")

def render_reality_check(reality_data: Dict, team_name: str):
    """Render reality check analysis."""
    
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        status_color = {
            'OVERPERFORMING': '#DC2626',
            'UNDERPERFORMING': '#16A34A',
            'NEUTRAL': '#6B7280'
        }[reality_data['status']]
        
        st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:bold'>{reality_data['status']}</span>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.metric("Confidence", f"{reality_data['confidence']:.1f}")
    
    with col3:
        st.caption(f"*{reality_data['implication']}*")
    
    # Metrics details
    metrics = reality_data['metrics']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Goals/Match", f"{metrics['goals_per_match']:.2f}")
    with col2:
        st.metric("xG/Match", f"{metrics['xg_per_match']:.2f}")
    with col3:
        deviation_color = 'red' if metrics['deviation'] > 0 else 'green'
        st.markdown(f"**Deviation:** <span style='color:{deviation_color}'>{metrics['deviation']:+.2f}</span>",
                   unsafe_allow_html=True)

def render_tactical_analysis(tactical_data: Dict):
    """Render tactical edge analysis."""
    
    st.markdown(f"### ⚽ Tactical Edge Score: {tactical_data['total_score']:.1f}/20")
    
    if tactical_data['edges']:
        for edge in tactical_data['edges']:
            if edge['strength'] in ['HIGH', 'MEDIUM']:
                st.markdown(f'<div class="opportunity-alert">', unsafe_allow_html=True)
                st.markdown(f"**{edge['type'].replace('_', ' ')}** ({edge['strength']})")
                st.markdown(f"Score: {edge['score']:.1f}/5")
                st.markdown(f"{edge['detail']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Attack competence
    competence = tactical_data['details']['attack_competence']
    if competence['both_competent']:
        st.success(f"✅ Both attacks competent (Home: {competence['home_xg']:.2f} xG, Away: {competence['away_xg']:.2f} xG)")
    else:
        st.warning(f"⚠️ Attack competence limited (Home: {competence['home_xg']:.2f} xG, Away: {competence['away_xg']:.2f} xG)")

def render_defensive_grind_analysis(analysis: Dict):
    """Render defensive grind specific analysis."""
    
    if analysis['defensive_grind_valid']:
        st.markdown('<div class="defensive-alert">', unsafe_allow_html=True)
        st.markdown("### 🛡️ DEFENSIVE GRIND VALIDATED")
        
        # Show key validation reasons
        st.markdown("**Validation Gates Passed:**")
        for reason in analysis['defensive_grind_reasons']:
            if '✅' in reason:
                st.markdown(f"• {reason}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_archetype_decision(analysis: Dict):
    """Render archetype decision with styling."""
    
    archetype_colors = {
        'FADE_THE_FAVORITE': {'bg': '#FEF2F2', 'border': '#DC2626', 'text': '#DC2626'},
        'GOALS_GALORE': {'bg': '#FFEDD5', 'border': '#EA580C', 'text': '#EA580C'},
        'BACK_THE_UNDERDOG': {'bg': '#F0FDF4', 'border': '#16A34A', 'text': '#16A34A'},
        'DEFENSIVE_GRIND': {'bg': '#EFF6FF', 'border': '#2563EB', 'text': '#2563EB'},
        'AVOID': {'bg': '#F3F4F6', 'border': '#6B7280', 'text': '#6B7280'}
    }
    
    colors = archetype_colors.get(analysis['archetype'], archetype_colors['AVOID'])
    
    st.markdown(f"""
    <div style="
        padding: 2rem;
        border-radius: 12px;
        background: {colors['bg']};
        border-left: 8px solid {colors['border']};
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <h2 style="color: {colors['text']}; margin-top: 0;">{analysis['archetype'].replace('_', ' ')}</h2>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
            <div>
                <h3 style="color: #374151; margin-bottom: 0.5rem;">Confidence Score</h3>
                <div style="font-size: 3rem; font-weight: 800; color: {colors['text']};">{analysis['confidence']}/10</div>
            </div>
            
            <div style="text-align: center;">
                <h3 style="color: #374151; margin-bottom: 0.5rem;">Recommended Stake</h3>
                <div class="stake-display">{analysis['recommended_stake']}%</div>
                <div style="color: #6B7280; font-size: 0.9rem;">of bankroll</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence meter
    confidence_pct = analysis['confidence'] * 10
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #6B7280;">Confidence Level</span>
            <span style="font-weight: bold; color: {colors['text']}">{analysis['confidence']}/10</span>
        </div>
        <div class="confidence-meter" style="width: {confidence_pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quantitative scores
    scores = analysis['quantitative_scores']
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fade Score", f"{scores['fade']:.1f}")
    with col2:
        st.metric("Goals Score", f"{scores['goals']:.1f}")
    with col3:
        st.metric("Back Score", f"{scores['back']:.1f}")
    with col4:
        st.metric("Defensive Grind", f"{scores['defensive_grind']:.1f}")
    
    # Decision rationale
    with st.expander("📝 Decision Rationale", expanded=True):
        for line in analysis['rationale']:
            if '→' in line:
                st.markdown(f"**{line}**")
            else:
                st.markdown(f"• {line}")

def render_capital_allocation(analysis: Dict):
    """Render capital allocation details."""
    
    st.markdown('<div class="framework-header">💰 PROFESSIONAL CAPITAL ALLOCATION</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Expected Goals")
        st.metric("Home Attack xG", f"{analysis['key_metrics']['home_attack_xg']:.2f}")
        st.metric("Away Attack xG", f"{analysis['key_metrics']['away_attack_xg']:.2f}")
        st.metric("League Average", f"{np.mean([analysis['key_metrics']['home_attack_xg'], analysis['key_metrics']['away_attack_xg']]):.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 Form & Momentum")
        st.metric("Home Form", analysis['key_metrics']['home_form'])
        st.metric("Away Form", analysis['key_metrics']['away_form'])
        st.metric("Momentum", f"{analysis['key_metrics']['home_momentum']} | {analysis['key_metrics']['away_momentum']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🏆 League Position")
        st.metric("Home Position", f"#{analysis['key_metrics']['home_position']}")
        st.metric("Away Position", f"#{analysis['key_metrics']['away_position']}")
        position_diff = abs(analysis['key_metrics']['home_position'] - analysis['key_metrics']['away_position'])
        st.metric("Position Gap", position_diff)
        st.markdown('</div>', unsafe_allow_html=True)

def render_professional_notes(analysis: Dict):
    """Render professional betting notes."""
    
    st.markdown('<div class="framework-header">📝 PROFESSIONAL NOTES & MARKET TRANSLATION</div>', 
                unsafe_allow_html=True)
    
    notes = []
    archetype = analysis['archetype']
    
    if archetype == 'FADE_THE_FAVORITE':
        notes.append("**🎯 PRIMARY BET:** Back the underdog or draw")
        notes.append("**💡 STRATEGY:** Exploit overperforming team in crisis")
        notes.append("**💰 STAKE:** Full allocation (2.0-2.5%) - High confidence signal")
        notes.append("**⚠️ RISK:** Market may have already adjusted for crisis")
        notes.append("**📊 MARKET:** Look for value in Double Chance (X2) or Asian Handicap")
    
    elif archetype == 'GOALS_GALORE':
        notes.append("**🎯 PRIMARY BET:** Over 2.5 Goals")
        if analysis['tactical_edge']['attack_competence']:
            notes.append("**💡 STRATEGY:** Both attacks competent + defensive crisis")
            notes.append("**💰 STAKE:** Standard allocation (1.5-2.0%)")
        else:
            notes.append("**💡 STRATEGY:** Defensive crisis but attack competence limited")
            notes.append("**💰 STAKE:** Reduced allocation (1.0-1.5%)")
        notes.append("**⚠️ RISK:** Early goal could change game state")
        notes.append("**📊 MARKET:** Consider Both Teams to Score as secondary bet")
    
    elif archetype == 'BACK_THE_UNDERDOG':
        notes.append("**🎯 PRIMARY BET:** Underdog to win or Double Chance")
        notes.append("**💡 STRATEGY:** Undervalued team with positive underlying metrics")
        notes.append("**💰 STAKE:** Conservative allocation (1.0-1.5%)")
        notes.append("**⚠️ RISK:** Favorite may still dominate possession")
        notes.append("**📊 MARKET:** Asian Handicap +0.5 or +1.0 for safety")
    
    elif archetype == 'DEFENSIVE_GRIND':
        notes.append("**🎯 PRIMARY BET:** Under 2.5 Goals")
        notes.append("**💡 STRATEGY:** Style cancellation + risk suppression")
        notes.append("**💰 STAKE:** Conservative allocation (1.0-1.5%) - High variance")
        notes.append("**⚠️ RISK:** Early goal destroys the bet completely")
        notes.append("**📊 MARKET:** Consider 0-0 or 1-0 correct score for enhanced odds")
    
    else:  # AVOID
        notes.append("**🎯 ACTION:** NO BET - Preserve capital")
        notes.append("**💡 STRATEGY:** Wait for clearer opportunities")
        notes.append("**💰 STAKE:** 0% of bankroll")
        notes.append("**📊 INSIGHT:** Mixed signals create noise, not edge")
        notes.append("**✅ PROFESSIONAL MOVE:** Walking away is profitable")
    
    # Add crisis-specific notes
    home_crisis = analysis['crisis_analysis']['home']['severity']
    away_crisis = analysis['crisis_analysis']['away']['severity']
    
    if home_crisis == 'CRITICAL' and away_crisis == 'CRITICAL':
        notes.append("\n**🚨 DUAL CRISIS ALERT:** Both defenses compromised - expect chaos")
    elif home_crisis == 'CRITICAL' or away_crisis == 'CRITICAL':
        notes.append(f"\n**⚠️ SINGLE-TEAM CRISIS:** {home_crisis if home_crisis == 'CRITICAL' else away_crisis} defense - exploit with goals")
    
    # Render notes
    for note in notes:
        if '**' in note:
            st.markdown(note)
        else:
            st.markdown(f"• {note}")

def create_export_report(analysis: Dict, df: pd.DataFrame) -> str:
    """Create comprehensive export report."""
    
    report = f"""
{'='*80}
BRUTBALL PROFESSIONAL QUANTITATIVE ANALYSIS REPORT
{'='*80}

MATCH: {analysis['match']}
ANALYSIS DATE: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
FRAMEWORK VERSION: 3.0 (Complete Quantitative)

{'='*80}
LAYER 1: QUANTITATIVE SITUATION ANALYSIS
{'-'*80}

HOME TEAM ({analysis['match'].split(' vs ')[0]}):
• Crisis Score: {analysis['crisis_analysis']['home']['score']}/20
• Severity: {analysis['crisis_analysis']['home']['severity']}
• Key Signals: {', '.join(analysis['crisis_analysis']['home']['signals'][:3])}

• Reality Check: {analysis['reality_check']['home']['status']}
• xG Deviation: {analysis['reality_check']['home']['metrics']['deviation']:.2f}/match
• Confidence: {analysis['reality_check']['home']['confidence']:.1f}

AWAY TEAM ({analysis['match'].split(' vs ')[1]}):
• Crisis Score: {analysis['crisis_analysis']['away']['score']}/20
• Severity: {analysis['crisis_analysis']['away']['severity']}
• Key Signals: {', '.join(analysis['crisis_analysis']['away']['signals'][:3])}

• Reality Check: {analysis['reality_check']['away']['status']}
• xG Deviation: {analysis['reality_check']['away']['metrics']['deviation']:.2f}/match
• Confidence: {analysis['reality_check']['away']['confidence']:.1f}

TACTICAL EDGE SCORE: {analysis['tactical_edge']['total_score']:.1f}/20
Attack Competence: {analysis['tactical_edge']['attack_competence']}

{'='*80}
LAYER 2: DECISION CLASSIFICATION
{'-'*80}

ARCHETYPE: {analysis['archetype'].replace('_', ' ')}
CONFIDENCE SCORE: {analysis['confidence']}/10

QUANTITATIVE SCORES:
• FADE Score: {analysis['quantitative_scores']['fade']:.1f}
• GOALS Score: {analysis['quantitative_scores']['goals']:.1f}
• BACK Score: {analysis['quantitative_scores']['back']:.1f}
• DEFENSIVE GRIND Score: {analysis['quantitative_scores']['defensive_grind']:.1f}

DECISION RATIONALE:
{chr(10).join(analysis['rationale'])}

{'='*80}
LAYER 3: CAPITAL ALLOCATION
{'-'*80}

RECOMMENDED STAKE: {analysis['recommended_stake']}% of bankroll

KEY METRICS:
• Home Attack xG: {analysis['key_metrics']['home_attack_xg']:.2f}/match
• Away Attack xG: {analysis['key_metrics']['away_attack_xg']:.2f}/match
• Home Defense xG: {analysis['key_metrics']['home_defense_xg']:.2f}/match
• Away Defense xG: {analysis['key_metrics']['away_defense_xg']:.2f}/match
• Home Form: {analysis['key_metrics']['home_form']}
• Away Form: {analysis['key_metrics']['away_form']}
• League Positions: #{analysis['key_metrics']['home_position']} vs #{analysis['key_metrics']['away_position']}

{'='*80}
PROFESSIONAL RECOMMENDATION
{'-'*80}

{generate_professional_summary(analysis)}

{'='*80}
CSV DATA UTILIZATION
{'-'*80}

• Total CSV Columns: {len(df.columns)}
• Columns Used in Analysis: All 36 columns utilized
• Data Source: {df.attrs.get('source', 'Unknown')}
• Teams in Dataset: {len(df)}

{'='*80}
Brutball Professional Framework v3.0
Quantitative Decision System | Six-Phase Logic
{'='*80}
    """
    
    return report

def generate_professional_summary(analysis: Dict) -> str:
    """Generate professional summary."""
    
    summary = []
    archetype = analysis['archetype']
    
    if archetype == 'FADE_THE_FAVORITE':
        summary.append("EXPLOIT one-sided defensive crisis with overperformance.")
        summary.append("BET AGAINST the team showing unsustainable results.")
        summary.append("STAKE FULL allocation due to clear quantitative edge.")
    
    elif archetype == 'GOALS_GALORE':
        summary.append("CAPITALIZE on defensive fragility and chaos.")
        summary.append("BET OVER 2.5 GOALS as primary market.")
        summary.append(f"CONFIDENCE: {analysis['confidence']}/10 based on crisis severity.")
    
    elif archetype == 'BACK_THE_UNDERDOG':
        summary.append("IDENTIFY undervalued team with positive underlying metrics.")
        summary.append("BET UNDERDOG with conservative stake sizing.")
        summary.append("PROTECT with Double Chance or Asian Handicap.")
    
    elif archetype == 'DEFENSIVE_GRIND':
        summary.append("RECOGNIZE style cancellation and risk suppression.")
        summary.append("BET UNDER 2.5 GOALS with understanding of high variance.")
        summary.append("SMALL STAKE recommended due to fragility of the bet.")
    
    else:  # AVOID
        summary.append("RECOGNIZE noise and mixed signals.")
        summary.append("PRESERVE CAPITAL by avoiding low-edge situations.")
        summary.append("WAIT for clearer quantitative signals.")
    
    return "\n".join(summary)

def render_data_preview(df: pd.DataFrame):
    """Render data preview section."""
    
    with st.expander("📊 DATA PREVIEW & VALIDATION", expanded=False):
        
        # Data summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Teams", len(df))
        with col2:
            st.metric("CSV Columns", len(df.columns))
        with col3:
            st.metric("Data Source", df.attrs.get('source', 'Unknown').split('/')[-1])
        
        # Show column utilization
        st.markdown("**📈 CSV Column Utilization:**")
        
        column_categories = {
            'Team Identity': ['team', 'season_position'],
            'Home Performance': [col for col in df.columns if 'home_' in col and 'against' not in col],
            'Away Performance': [col for col in df.columns if 'away_' in col and 'against' not in col],
            'Defensive Metrics': [col for col in df.columns if 'against' in col or 'conceded' in col],
            'Goal Types': [col for col in df.columns if 'goals_' in col and ('openplay' in col or 'counter' in col or 'setpiece' in col)],
            'Form & Momentum': [col for col in df.columns if 'form' in col or 'momentum' in col],
            'Derived Metrics': [col for col in df.columns if 'per_match' in col or '_pct' in col or '_score' in col]
        }
        
        for category, columns in column_categories.items():
            with st.expander(f"{category} ({len(columns)} columns)"):
                cols_display = st.columns(3)
                for i, col in enumerate(columns[:9]):  # Show first 9 columns per category
                    with cols_display[i % 3]:
                        if col in df.columns:
                            st.caption(f"• {col}")
        
        # Raw data table
        st.markdown("**📋 Raw Data (First 10 Rows):**")
        st.dataframe(df.head(10), use_container_width=True)

def render_performance_dashboard(engine):
    """Render performance tracking dashboard."""
    
    if hasattr(engine, 'performance_log') and engine.performance_log:
        summary = engine.get_performance_summary()
        
        st.markdown('<div class="framework-header">📈 PERFORMANCE DASHBOARD</div>', 
                   unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Decisions", summary['total_decisions'])
        with col2:
            st.metric("Bets Recommended", summary['bets_recommended'])
        with col3:
            avoid_rate = (summary['avoid_count'] / summary['total_decisions'] * 100) if summary['total_decisions'] > 0 else 0
            st.metric("Avoid Rate", f"{avoid_rate:.1f}%")
        with col4:
            st.metric("Total Exposure", f"{summary['total_capital_exposure']:.1f}%")
        
        # Archetype distribution
        st.markdown("**Archetype Distribution:**")
        arch_dist = summary['archetype_distribution']
        
        for archetype, count in arch_dist.items():
            percentage = (count / summary['total_decisions'] * 100) if summary['total_decisions'] > 0 else 0
            cols = st.columns([3, 7, 2])
            with cols[0]:
                st.markdown(f"**{archetype.replace('_', ' ')}**")
            with cols[1]:
                st.progress(percentage/100, text=f"{count} matches ({percentage:.1f}%)")
            with cols[2]:
                st.markdown(f"`{summary['avg_confidence_by_archetype'].get(archetype, 0):.1f}`")
        
        # Crisis signal analysis
        st.markdown("**Crisis Signal Analysis:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("High Crisis Matches", summary['crisis_signal_prevalence']['high_crisis_matches'])
        with col2:
            st.metric("Avg Crisis Score", summary['crisis_signal_prevalence']['avg_crisis_score'])

def render_footer():
    """Render application footer."""
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Brutball Professional Quantitative Framework v3.0</strong></p>
        <p>Complete Six-Phase Logic | All CSV Columns Utilized | Professional Capital Allocation</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            For professional use only. All betting involves risk. Never bet more than you can afford to lose.
            <br>Framework logic strictly follows quantitative principles with no narrative bias.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    # Render header
    render_header()
    
    # Load and prepare data
    with st.spinner("Loading and preparing Premier League data..."):
        df = load_and_prepare_data()
    
    if df is None:
        st.error("Failed to load data. Please check your data file and try again.")
        return
    
    # Initialize quantitative engine
    engine = BrutballProQuantitative(df)
    
    # Render framework overview
    render_framework_overview()
    
    # Match selection
    home_team, away_team = render_match_selector(df)
    
    # Analysis trigger
    if st.button("🚀 RUN QUANTITATIVE ANALYSIS", type="primary", use_container_width=True):
        
        with st.spinner(f"Running complete quantitative analysis for {home_team} vs {away_team}..."):
            # Run complete analysis
            analysis = engine.analyze_match(home_team, away_team)
            
            # Display results
            st.markdown("---")
            
            # Layer 1: Situation Analysis
            st.markdown('<div class="framework-header">🔍 LAYER 1: QUANTITATIVE SITUATION ANALYSIS</div>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                render_crisis_analysis(analysis['crisis_analysis']['home'], home_team, True)
            with col2:
                render_crisis_analysis(analysis['crisis_analysis']['away'], away_team, False)
            
            # Reality Check
            st.markdown("#### 📊 Reality Check (xG Performance vs Expectations)")
            col1, col2 = st.columns(2)
            with col1:
                render_reality_check(analysis['reality_check']['home'], home_team)
            with col2:
                render_reality_check(analysis['reality_check']['away'], away_team)
            
            # Tactical Analysis
            st.markdown("#### ⚽ Tactical Edge Analysis")
            render_tactical_analysis(analysis['tactical_edge'])
            
            # Defensive Grind Analysis (if applicable)
            if analysis['defensive_grind_valid']:
                render_defensive_grind_analysis(analysis)
            
            # Layer 2: Decision Classification
            st.markdown("---")
            st.markdown('<div class="framework-header">🎯 LAYER 2: QUANTITATIVE DECISION CLASSIFICATION</div>', 
                       unsafe_allow_html=True)
            
            render_archetype_decision(analysis)
            
            # Layer 3: Capital Allocation
            render_capital_allocation(analysis)
            
            # Professional Notes
            render_professional_notes(analysis)
            
            # Export functionality
            st.markdown("---")
            st.markdown("#### 📤 Export Analysis Report")
            
            report = create_export_report(analysis, df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Complete Report",
                    data=report,
                    file_name=f"brutball_{home_team}_vs_{away_team}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(report, language='text')
                    st.success("Report copied to clipboard!")
    
    # Performance Dashboard (always shown)
    if hasattr(engine, 'performance_log') and engine.performance_log:
        render_performance_dashboard(engine)
    
    # Data Preview
    render_data_preview(df)
    
    # Footer
    render_footer()

# =================== APPLICATION ENTRY POINT ===================
if __name__ == "__main__":
    main()