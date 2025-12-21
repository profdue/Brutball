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
    .league-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'country': 'England',
        'color': '#3B82F6'
    },
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'country': 'Spain',
        'color': '#EF4444'
    },
    'Bundesliga': {
        'filename': 'bundesliga.csv',
        'display_name': '🇩🇪 Bundesliga',
        'country': 'Germany',
        'color': '#000000'
    },
    'Serie A': {
        'filename': 'serie_a.csv',
        'display_name': '🇮🇹 Serie A',
        'country': 'Italy',
        'color': '#10B981'
    },
    'Ligue 1': {
        'filename': 'ligue_1.csv',
        'display_name': '🇫🇷 Ligue 1',
        'country': 'France',
        'color': '#8B5CF6'
    }
}

# =================== DATA LOADING & PREPARATION ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load, validate, and prepare the dataset for selected league."""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple data source locations
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
        ]
        
        df = None
        source_used = ""
        
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                source_used = source
                st.success(f"✅ {league_config['display_name']} data loaded from: {source.split('/')[-1]}")
                break
            except Exception as e:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Clean and validate column names
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower()
        cleaned_columns = df.columns.tolist()
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['country'] = league_config['country']
        df.attrs['color'] = league_config['color']
        df.attrs['source'] = source_used
        df.attrs['original_columns'] = original_columns
        df.attrs['cleaned_columns'] = cleaned_columns
        df.attrs['total_teams'] = len(df)
        df.attrs['filename'] = filename
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error for {league_name}: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics from YOUR actual CSV columns."""
    
    # 1. Calculate home/away goals conceded from components
    df['home_goals_conceded'] = (
        df['home_goals_openplay_against'].fillna(0) +
        df['home_goals_counter_against'].fillna(0) +
        df['home_goals_setpiece_against'].fillna(0) +
        df['home_goals_penalty_against'].fillna(0) +
        df['home_goals_owngoal_against'].fillna(0)
    )
    
    df['away_goals_conceded'] = (
        df['away_goals_openplay_against'].fillna(0) +
        df['away_goals_counter_against'].fillna(0) +
        df['away_goals_setpiece_against'].fillna(0) +
        df['away_goals_penalty_against'].fillna(0) +
        df['away_goals_owngoal_against'].fillna(0)
    )
    
    # 2. Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xgc_per_match'] = df['home_xg_against'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xgc_per_match'] = df['away_xg_against'] / df['away_matches_played'].replace(0, np.nan)
    
    # 3. Goal type percentages FOR
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_goals_scored'].replace(0, np.nan)
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_goals_scored'].replace(0, np.nan)
    
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_goals_scored'].replace(0, np.nan)
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_goals_scored'].replace(0, np.nan)
    
    # 4. Goal type percentages AGAINST (using our calculated totals)
    df['home_counter_vuln'] = df['home_goals_counter_against'] / df['home_goals_conceded'].replace(0, np.nan)
    df['home_setpiece_vuln'] = df['home_goals_setpiece_against'] / df['home_goals_conceded'].replace(0, np.nan)
    df['home_openplay_vuln'] = df['home_goals_openplay_against'] / df['home_goals_conceded'].replace(0, np.nan)
    
    df['away_counter_vuln'] = df['away_goals_counter_against'] / df['away_goals_conceded'].replace(0, np.nan)
    df['away_setpiece_vuln'] = df['away_goals_setpiece_against'] / df['away_goals_conceded'].replace(0, np.nan)
    df['away_openplay_vuln'] = df['away_goals_openplay_against'] / df['away_goals_conceded'].replace(0, np.nan)
    
    # 5. Form points calculation
    def calculate_form_points(form_string):
        if pd.isna(form_string):
            return 0
        points_map = {'W': 3, 'D': 1, 'L': 0}
        return sum(points_map.get(char, 0) for char in str(form_string))
    
    df['form_points_overall'] = df['form_last_5_overall'].apply(calculate_form_points)
    df['form_points_home'] = df['form_last_5_home'].apply(calculate_form_points)
    df['form_points_away'] = df['form_last_5_away'].apply(calculate_form_points)
    
    # 6. Form momentum
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
    
    for col in calculated_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
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
        
        # League averages - FIXED: Use simple mean instead of combine
        metrics['avg_home_xg'] = self.df['home_xg_per_match'].mean()
        metrics['avg_away_xg'] = self.df['away_xg_per_match'].mean()
        metrics['avg_home_goals'] = self.df['home_goals_per_match'].mean()
        metrics['avg_away_goals'] = self.df['away_goals_per_match'].mean()
        
        # Percentile thresholds - FIXED: Simple calculation
        all_home_xg = self.df['home_xg_per_match'].dropna()
        all_away_xg = self.df['away_xg_per_match'].dropna()
        
        if len(all_home_xg) > 0 and len(all_away_xg) > 0:
            all_xg = pd.concat([all_home_xg, all_away_xg])
            metrics['xg_75th'] = np.percentile(all_xg, 75)
            metrics['xg_25th'] = np.percentile(all_xg, 25)
        else:
            metrics['xg_75th'] = 1.5
            metrics['xg_25th'] = 0.8
        
        # Goal type averages - FIXED: Simple mean of means
        home_counter_mean = self.df['home_counter_pct'].mean() if 'home_counter_pct' in self.df.columns else 0
        away_counter_mean = self.df['away_counter_pct'].mean() if 'away_counter_pct' in self.df.columns else 0
        metrics['avg_counter_pct'] = (home_counter_mean + away_counter_mean) / 2
        
        home_setpiece_mean = self.df['home_setpiece_pct'].mean() if 'home_setpiece_pct' in self.df.columns else 0
        away_setpiece_mean = self.df['away_setpiece_pct'].mean() if 'away_setpiece_pct' in self.df.columns else 0
        metrics['avg_setpiece_pct'] = (home_setpiece_mean + away_setpiece_mean) / 2
        
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
        goals_conceded = team_data.get('goals_conceded_last_5', 0)
        
        if is_home:
            xgc_per_match = team_data.get('home_xgc_per_match', 0)
        else:
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
        goals_scored = team_data.get('goals_scored_last_5', 0)
        
        if is_home:
            xg_per_match = team_data.get('home_xg_per_match', 0)
        else:
            xg_per_match = team_data.get('away_xg_per_match', 0)
        
        if goals_scored <= 4 and xg_per_match < self.league_metrics.get('xg_25th', 0.8):
            score += 4
            signals.append(f"⚽ Attack crisis: {goals_scored} goals, {xg_per_match:.2f} xG (4pts)")
        elif goals_scored <= 6 and xg_per_match < self.league_metrics.get('avg_home_xg', 1.5):
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
            league_avg = self.league_metrics.get('avg_home_xg', 1.5)
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
            matches = team_data.get('away_matches_played', 1)
            league_avg = self.league_metrics.get('avg_away_xg', 1.2)
        
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
        away_openplay_vuln = away_data.get('away_openplay_vuln', 0)
        home_openplay_goals = home_data.get('home_goals_openplay_for', 0)
        away_openplay_conceded = away_data.get('away_goals_openplay_against', 0)
        
        if home_openplay_pct > 0.6 and away_openplay_vuln > 0.5:
            openplay_edge = (home_openplay_pct * away_openplay_vuln) * 20
            edge_score += min(4.0, openplay_edge)
            edges.append({
                'type': 'OPEN_PLAY',
                'score': min(4.0, openplay_edge),
                'strength': 'HIGH' if openplay_edge > 2.5 else 'MEDIUM',
                'detail': f"Home: {home_openplay_pct:.1%} open play ({home_openplay_goals} goals) | Away concedes: {away_openplay_vuln:.1%} ({away_openplay_conceded} goals)"
            })
        
        # 4. ATTACK COMPETENCE CHECK
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
        if home_xgc < self.league_metrics.get('avg_home_xg', 1.5) * 0.8:
            defensive_stability += 1
        if away_xgc < self.league_metrics.get('avg_away_xg', 1.2) * 0.8:
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
    
    # ========== PHASE 5: CORRECTED QUANTITATIVE ARCHETYPE CLASSIFICATION ==========
    def calculate_attack_competence_factor(self, home_data: Dict, away_data: Dict) -> float:
        """Calculate attack competence factor (0.0-1.5)."""
        home_xg_per_game = home_data.get('home_xg_per_match', 0)
        away_xg_per_game = away_data.get('away_xg_per_match', 0)
        
        if home_xg_per_game > 1.4 and away_xg_per_game > 1.4:
            return 1.5
        elif home_xg_per_game > 1.1 and away_xg_per_game > 1.1:
            return 1.3
        elif home_xg_per_game > 0.8 and away_xg_per_game > 0.8:
            return 1.0
        elif home_xg_per_game > 0.6 and away_xg_per_game > 0.6:
            return 0.8
        else:
            return 0.6
    
    def calculate_goals_galore_score(self, home_crisis: Dict, away_crisis: Dict, 
                                   tactical: Dict, home_data: Dict, away_data: Dict,
                                   home_team_name: str, away_team_name: str) -> Tuple[float, List[str]]:
        """
        CORRECTED GOALS GALORE SCORING with Chaos Override and Volume Concession Boost.
        Returns: (score, rationale)
        """
        rationale = []
        goals_score = 0

        # 1️⃣ Determine if Chaos Override applies
        chaos_override = home_crisis['severity'] == 'CRITICAL' and away_crisis['severity'] == 'CRITICAL'
        if chaos_override:
            rationale.append(f"⚡ Chaos Override: Both {home_team_name} and {away_team_name} in CRITICAL crisis")
        
        # 2️⃣ Base GOALS score
        crisis_sum = home_crisis['score'] + away_crisis['score']
        if chaos_override:
            # Reduced reliance on tactical edge for chaos games
            goals_score = crisis_sum * (max(1.0, tactical['total_score']) / 10)
        else:
            # Standard calculation
            goals_score = crisis_sum * (tactical['total_score'] / 5)
        
        rationale.append(f"Base GOALS score: {goals_score:.1f}")

        # 3️⃣ Volume Concession Boost
        home_conceded = home_data.get('goals_conceded_last_5', 0)
        away_conceded = away_data.get('goals_conceded_last_5', 0)
        total_goals_conceded = home_conceded + away_conceded
        
        if total_goals_conceded >= 30:
            boost = 0.3 * goals_score
            goals_score += boost
            rationale.append(f"📈 Volume Boost: +{boost:.1f} for {home_team_name} ({home_conceded}) + {away_team_name} ({away_conceded}) goals conceded")

        # 4️⃣ Attack Competence Modifier
        attack_factor = self.calculate_attack_competence_factor(home_data, away_data)
        
        if attack_factor < 0.7:
            goals_score *= 0.7
            rationale.append(f"⚠️ Low attack competence ({attack_factor:.2f}) → 30% penalty")
        elif attack_factor > 1.2:
            goals_score *= 1.2
            rationale.append(f"✅ High attack competence ({attack_factor:.2f}) → 20% boost")
        else:
            goals_score *= attack_factor

        return goals_score, rationale
    
    def calculate_fade_score(self, favorite_name: str, underdog_name: str,
                           favorite_crisis: Dict, underdog_crisis: Dict, 
                           favorite_reality: Dict, xg_deviation: float) -> Tuple[float, List[str]]:
        """Score for FADE archetype (bet against the favorite)."""
        rationale = []
        
        base = favorite_crisis['score'] * (underdog_crisis['score'] / 5)
        if xg_deviation > 0.5:  # Favorite significantly overperforming xG
            base *= 1.5
            rationale.append(f"📈 {favorite_name} overperforming xG (+{xg_deviation:.2f}) → 50% boost")
        
        rationale.append(f"FADE {favorite_name}: Crisis {favorite_crisis['score']}/20, {underdog_name} stability {underdog_crisis['score']}/20")
        return base, rationale
    
    def calculate_back_score(self, underdog_name: str, favorite_name: str,
                           underdog_crisis: Dict, favorite_reality: Dict,
                           tactical_mismatch: float) -> Tuple[float, List[str]]:
        """Score for BACK archetype (bet on underdog)."""
        rationale = []
        
        score = underdog_crisis['score'] * favorite_reality['confidence'] * (tactical_mismatch / 10)
        rationale.append(f"BACK {underdog_name}: Stable ({underdog_crisis['score']}/20), {favorite_name} underperforming ({favorite_reality['confidence']:.1f})")
        return score, rationale
    
    def calculate_defensive_grind_score(self, home_team_name: str, away_team_name: str,
                                      home_attack: float, away_attack: float, 
                                      home_crisis: Dict, away_crisis: Dict) -> Tuple[float, List[str]]:
        """Score for DEFENSIVE_GRIND archetype (Under 2.5)."""
        rationale = []
        
        if home_crisis['score'] > 5 or away_crisis['score'] > 5:
            rationale.append(f"❌ Defensive grind rejected: {home_team_name if home_crisis['score'] > 5 else away_team_name} in crisis")
            return 0, rationale
        
        attack_suppression = (max(0, 3 - home_attack) + max(0, 3 - away_attack)) / 2
        score = attack_suppression * 2
        rationale.append(f"✅ Attacks suppressed: {home_team_name} ({home_attack:.2f} xG), {away_team_name} ({away_attack:.2f} xG)")
        return score, rationale
    
    def determine_archetype(self, home_crisis: Dict, away_crisis: Dict,
                           home_reality: Dict, away_reality: Dict,
                           tactical: Dict, home_data: Dict, away_data: Dict,
                           home_team_name: str, away_team_name: str) -> Dict:
        """
        CORRECTED QUANTITATIVE ARCHETYPE CLASSIFICATION with clear team names.
        """
        
        # Determine favorite based on league position (lower number = higher position = favorite)
        home_position = home_data.get('season_position', 10)
        away_position = away_data.get('season_position', 10)
        
        favorite_name = home_team_name if home_position < away_position else away_team_name
        underdog_name = away_team_name if home_position < away_position else home_team_name
        
        # Get crisis and reality data for favorite/underdog
        favorite_crisis = home_crisis if favorite_name == home_team_name else away_crisis
        underdog_crisis = away_crisis if favorite_name == home_team_name else home_crisis
        favorite_reality = home_reality if favorite_name == home_team_name else away_reality
        underdog_reality = away_reality if favorite_name == home_team_name else home_reality
        
        # Calculate all archetype scores
        goals_score, goals_rationale = self.calculate_goals_galore_score(
            home_crisis, away_crisis, tactical, home_data, away_data,
            home_team_name, away_team_name
        )
        
        fade_score, fade_rationale = self.calculate_fade_score(
            favorite_name, underdog_name, favorite_crisis, underdog_crisis,
            favorite_reality, abs(favorite_reality['metrics']['deviation'])
        )
        
        back_score, back_rationale = self.calculate_back_score(
            underdog_name, favorite_name, underdog_crisis, favorite_reality,
            tactical['total_score'] / 2
        )
        
        # Defensive Grind validation
        defensive_grind_valid, grind_confidence, grind_reasons = self.validate_defensive_grind(
            home_data, away_data, home_crisis, away_crisis
        )
        
        defensive_score, defensive_rationale = self.calculate_defensive_grind_score(
            home_team_name, away_team_name,
            home_data.get('home_xg_per_match', 0),
            away_data.get('away_xg_per_match', 0),
            home_crisis, away_crisis
        )
        
        # Collect all scores with thresholds
        archetype_scores = [
            ('GOALS GALORE', goals_score, goals_rationale, 8.0),
            ('FADE_THE_FAVORITE', fade_score, fade_rationale, 7.0),
            ('BACK_THE_UNDERDOG', back_score, back_rationale, 6.5),
            ('DEFENSIVE_GRIND', defensive_score, defensive_rationale, 7.0)
        ]
        
        rationale = []
        
        # Filter and select the highest scoring archetype that meets its minimum threshold
        viable = [(name, score, sub_rationale) for name, score, sub_rationale, threshold in archetype_scores if score >= threshold]
        
        if not viable:
            archetype = 'AVOID'
            confidence = 0
            rationale.append("No archetype score met the minimum threshold for action.")
        else:
            # Select the highest score
            selected = max(viable, key=lambda x: x[1])
            archetype_name, score, sub_rationale = selected
            archetype = archetype_name
            rationale.extend(sub_rationale)
            
            # Add team context based on archetype
            if archetype == 'FADE_THE_FAVORITE':
                rationale.append(f"🎯 Action: Bet against {favorite_name} (favorite)")
            elif archetype == 'BACK_THE_UNDERDOG':
                rationale.append(f"🎯 Action: Bet on {underdog_name} (underdog)")
            
            # Convert score to confidence (0-10 scale)
            if score >= 15:
                confidence = 10
            elif score >= 12:
                confidence = 9
            elif score >= 10:
                confidence = 8
            elif score >= 8:
                confidence = 7
            elif score >= 6:
                confidence = 6
            elif score >= 5:
                confidence = 5
            elif score >= 4:
                confidence = 4
            else:
                confidence = 3  # Minimal confidence, but still actionable
        
        if defensive_grind_valid:
            rationale.extend([f"Defensive Grind Check: {reason}" for reason in grind_reasons])
        
        # Store team context for display
        team_context = {
            'favorite': favorite_name,
            'underdog': underdog_name,
            'home': home_team_name,
            'away': away_team_name,
            'home_position': home_position,
            'away_position': away_position
        }
        
        return {
            'archetype': archetype,
            'confidence': confidence,
            'team_context': team_context,
            'quantitative_scores': {
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
        
        base_stakes = {
            'GOALS GALORE': {8: 2.5, 7: 2.0, 6: 2.0, 5: 1.5, 4: 1.0},
            'FADE_THE_FAVORITE': {8: 2.5, 7: 2.0, 6: 1.5, 5: 1.0, 4: 1.0},
            'BACK_THE_UNDERDOG': {8: 2.0, 7: 1.5, 6: 1.5, 5: 1.0, 4: 1.0},
            'DEFENSIVE_GRIND': {8: 2.0, 7: 1.5, 6: 1.5, 5: 1.0, 4: 1.0}
        }
        
        thresholds = base_stakes.get(archetype, {})
        
        for threshold, stake in sorted(thresholds.items(), reverse=True):
            if confidence >= threshold:
                risk_multiplier = 1.0
                if home_crisis['severity'] == 'WARNING' or away_crisis['severity'] == 'WARNING':
                    risk_multiplier = 0.8
                
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
        
        # ===== PHASE 4 & 5: CORRECTED ARCHETYPE CLASSIFICATION =====
        archetype_result = self.determine_archetype(
            home_crisis, away_crisis, home_reality, away_reality,
            tactical, home_data, away_data,
            home_team_name, away_team_name  # Pass team names explicitly
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
            
            'crisis_analysis': {'home': home_crisis, 'away': away_crisis},
            'reality_check': {'home': home_reality, 'away': away_reality},
            'tactical_edge': tactical,
            
            'archetype': archetype_result['archetype'],
            'confidence': archetype_result['confidence'],
            'team_context': archetype_result['team_context'],  # Add team context
            'quantitative_scores': archetype_result['quantitative_scores'],
            'rationale': archetype_result['rationale'],
            'defensive_grind_valid': archetype_result['defensive_grind_valid'],
            'defensive_grind_reasons': archetype_result['defensive_grind_reasons'],
            
            'recommended_stake': stake_pct,
            
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
            }
        }
        
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

# =================== STREAMLIT UI COMPONENTS ===================
def render_header():
    """Render main application header."""
    st.markdown('<div class="main-header">⚽ BRUTBALL PRO MULTI-LEAGUE QUANTITATIVE FRAMEWORK</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem;">Professional Decision System | All CSV Columns Utilized | Six-Phase Quantitative Logic | 5 European Leagues</p>
    </div>
    """, unsafe_allow_html=True)

def render_league_selector():
    """Render league selection interface."""
    st.markdown('<div class="framework-header">🌍 SELECT LEAGUE</div>', 
                unsafe_allow_html=True)
    
    # Create columns for league selection
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        premier_league = st.button(
            "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
            use_container_width=True,
            type="primary" if 'selected_league' not in st.session_state else "secondary",
            help="English Premier League"
        )
        if premier_league:
            st.session_state.selected_league = 'Premier League'
    
    with col2:
        la_liga = st.button(
            "🇪🇸 La Liga",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'La Liga' else "secondary",
            help="Spanish La Liga"
        )
        if la_liga:
            st.session_state.selected_league = 'La Liga'
    
    with col3:
        bundesliga = st.button(
            "🇩🇪 Bundesliga",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Bundesliga' else "secondary",
            help="German Bundesliga"
        )
        if bundesliga:
            st.session_state.selected_league = 'Bundesliga'
    
    with col4:
        serie_a = st.button(
            "🇮🇹 Serie A",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Serie A' else "secondary",
            help="Italian Serie A"
        )
        if serie_a:
            st.session_state.selected_league = 'Serie A'
    
    with col5:
        ligue_1 = st.button(
            "🇫🇷 Ligue 1",
            use_container_width=True,
            type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == 'Ligue 1' else "secondary",
            help="French Ligue 1"
        )
        if ligue_1:
            st.session_state.selected_league = 'Ligue 1'
    
    # Default selection
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # Display current selection
    league_config = LEAGUES[st.session_state.selected_league]
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 10px;
        background: {league_config['color']}15;
        border-left: 6px solid {league_config['color']};
        margin: 1rem 0;
        text-align: center;
    ">
        <h3 style="color: {league_config['color']}; margin: 0;">
            {league_config['display_name']} • {league_config['country']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    return st.session_state.selected_league

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
        st.markdown("**Status:** ✅ OPERATIONAL")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 LAYER 2")
        st.markdown("**Decision Firewall**")
        st.markdown("• 4 Archetype Classification")
        st.markdown("• Defensive Grind Validator")
        st.markdown("• Confidence Scoring (0-10)")
        st.markdown("**Status:** ✅ CORRECTED")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("### 💰 LAYER 3")
        st.markdown("**Capital Allocation**")
        st.markdown("• Precision Stake Sizing")
        st.markdown("• Risk-Adjusted Betting")
        st.markdown("• Bankroll Management")
        st.markdown("**Status:** ✅ AUTOMATED")
        st.markdown('</div>', unsafe_allow_html=True)

def render_match_selector(df: pd.DataFrame, league_name: str):
    """Render team selection interface."""
    st.markdown('<div class="framework-header">🏟️ MATCH ANALYSIS</div>', 
                unsafe_allow_html=True)
    
    # Add league context
    league_config = LEAGUES[league_name]
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {league_config['color']}10;
        border-radius: 8px;
        border: 1px solid {league_config['color']}30;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        color: {league_config['color']};
    ">
        {league_config['display_name']} • {df.attrs['total_teams']} Teams Loaded
    </div>
    """, unsafe_allow_html=True)
    
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
        
        for signal in crisis_data['signals'][:3]:
            st.markdown(f"• {signal}")
        
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
        
        st.markdown("**Validation Gates Passed:**")
        for reason in analysis['defensive_grind_reasons']:
            if '✅' in reason:
                st.markdown(f"• {reason}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_archetype_decision(analysis: Dict, league_config: Dict):
    """Render archetype decision with styling."""
    
    archetype_colors = {
        'GOALS GALORE': {'bg': '#FFEDD5', 'border': '#EA580C', 'text': '#EA580C'},
        'FADE_THE_FAVORITE': {'bg': '#FEF2F2', 'border': '#DC2626', 'text': '#DC2626'},
        'BACK_THE_UNDERDOG': {'bg': '#F0FDF4', 'border': '#16A34A', 'text': '#16A34A'},
        'DEFENSIVE_GRIND': {'bg': '#EFF6FF', 'border': '#2563EB', 'text': '#2563EB'},
        'AVOID': {'bg': '#F3F4F6', 'border': '#6B7280', 'text': '#6B7280'}
    }
    
    colors = archetype_colors.get(analysis['archetype'], archetype_colors['AVOID'])
    
    # Add league badge
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {league_config['color']}15;
        border-radius: 8px;
        border: 1px solid {league_config['color']}30;
        margin-bottom: 0.5rem;
        text-align: center;
        font-weight: 600;
        color: {league_config['color']};
    ">
        {league_config['display_name']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="
        padding: 2rem;
        border-radius: 12px;
        background: {colors['bg']};
        border-left: 8px solid {colors['border']};
        margin: 0.5rem 0 1.5rem 0;
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
    
    with st.expander("📝 Decision Rationale", expanded=True):
        for line in analysis['rationale']:
            if '→' in line or '📈' in line or '⚡' in line or '✅' in line or '⚠️' in line or '🎯' in line:
                st.markdown(f"**{line}**")
            else:
                st.markdown(f"• {line}")

def render_capital_allocation(analysis: Dict, league_config: Dict):
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
        team_context = analysis.get('team_context', {})
        home_team = analysis['match'].split(' vs ')[0]
        away_team = analysis['match'].split(' vs ')[1]
        
        # Add favorite/underdog indicators
        home_label = f"{home_team} {'⭐' if team_context.get('favorite') == home_team else '⚫'}"
        away_label = f"{away_team} {'⭐' if team_context.get('favorite') == away_team else '⚫'}"
        
        st.metric(home_label, f"#{analysis['key_metrics']['home_position']}")
        st.metric(away_label, f"#{analysis['key_metrics']['away_position']}")
        position_diff = abs(analysis['key_metrics']['home_position'] - analysis['key_metrics']['away_position'])
        st.metric("Position Gap", position_diff)
        st.markdown('</div>', unsafe_allow_html=True)

def render_professional_notes(analysis: Dict, league_config: Dict):
    """Render professional betting notes with actual team names."""
    
    st.markdown('<div class="framework-header">📝 PROFESSIONAL NOTES & MARKET TRANSLATION</div>', 
                unsafe_allow_html=True)
    
    # Add league context
    st.markdown(f"""
    <div style="
        padding: 0.5rem 1rem;
        background: {league_config['color']}10;
        border-radius: 8px;
        border: 1px solid {league_config['color']}30;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        color: {league_config['color']};
    ">
        {league_config['display_name']} Market Analysis
    </div>
    """, unsafe_allow_html=True)
    
    notes = []
    archetype = analysis['archetype']
    team_context = analysis.get('team_context', {})
    
    home_team = analysis['match'].split(' vs ')[0]
    away_team = analysis['match'].split(' vs ')[1]
    
    if archetype == 'GOALS GALORE':
        notes.append("**🎯 PRIMARY BET:** Over 2.5 Goals")
        
        # Check for Chaos Override signals
        rationale_text = ' '.join(analysis['rationale'])
        if 'Chaos Override' in rationale_text:
            notes.append(f"**⚡ CHAOS OVERRIDE ACTIVE:** Both {home_team} and {away_team} in CRITICAL crisis")
            notes.append("**💡 STRATEGY:** Pure defensive collapse - expect high-volume chaos")
            notes.append("**💰 STAKE:** Full allocation (2.0-2.5%) - High confidence signal")
        elif 'Volume Boost' in rationale_text:
            notes.append(f"**📈 VOLUME BOOST ACTIVE:** Extreme goals conceded by both teams")
            notes.append("**💡 STRATEGY:** High-volume concession environment")
            notes.append("**💰 STAKE:** Standard allocation (2.0%)")
        else:
            notes.append("**💡 STRATEGY:** Tactical goals matchup")
            notes.append("**💰 STAKE:** Standard allocation (1.5-2.0%)")
        
        notes.append("**⚠️ RISK:** Early goal could change game state")
        notes.append("**📊 MARKET:** Consider Both Teams to Score as secondary bet")
    
    elif archetype == 'FADE_THE_FAVORITE':
        favorite = team_context.get('favorite', 'Favorite')
        underdog = team_context.get('underdog', 'Underdog')
        notes.append(f"**🎯 PRIMARY BET:** Back {underdog} or Draw")
        notes.append(f"**💡 STRATEGY:** Exploit {favorite}'s crisis while they're overperforming")
        notes.append("**💰 STAKE:** Full allocation (2.0-2.5%) - High confidence signal")
        notes.append(f"**⚠️ RISK:** Market may have already adjusted for {favorite}'s crisis")
        notes.append(f"**📊 MARKET:** {underdog} Double Chance or {underdog} Asian Handicap +0.5")
    
    elif archetype == 'BACK_THE_UNDERDOG':
        underdog = team_context.get('underdog', 'Underdog')
        favorite = team_context.get('favorite', 'Favorite')
        notes.append(f"**🎯 PRIMARY BET:** {underdog} to win or Draw")
        notes.append(f"**💡 STRATEGY:** {underdog} undervalued, {favorite} underperforming")
        notes.append("**💰 STAKE:** Conservative allocation (1.0-1.5%)")
        notes.append(f"**⚠️ RISK:** {favorite} may still dominate possession")
        notes.append(f"**📊 MARKET:** {underdog} Asian Handicap +0.5 or +1.0 for safety")
    
    elif archetype == 'DEFENSIVE_GRIND':
        notes.append("**🎯 PRIMARY BET:** Under 2.5 Goals")
        notes.append(f"**💡 STRATEGY:** {home_team} vs {away_team} - style cancellation + risk suppression")
        notes.append("**💰 STAKE:** Conservative allocation (1.0-1.5%) - High variance")
        notes.append("**⚠️ RISK:** Early goal destroys the bet completely")
        notes.append("**📊 MARKET:** Consider 0-0 or 1-0 correct score for enhanced odds")
    
    else:
        notes.append("**🎯 ACTION:** NO BET - Preserve capital")
        notes.append("**💡 STRATEGY:** Wait for clearer opportunities")
        notes.append("**💰 STAKE:** 0% of bankroll")
        notes.append("**📊 INSIGHT:** Mixed signals create noise, not edge")
        notes.append("**✅ PROFESSIONAL MOVE:** Walking away is profitable")
    
    home_crisis = analysis['crisis_analysis']['home']['severity']
    away_crisis = analysis['crisis_analysis']['away']['severity']
    
    if home_crisis == 'CRITICAL' and away_crisis == 'CRITICAL':
        notes.append(f"\n**🚨 DUAL CRISIS ALERT:** Both {home_team} and {away_team} defenses compromised - expect chaos")
    elif home_crisis == 'CRITICAL':
        notes.append(f"\n**⚠️ SINGLE-TEAM CRISIS:** {home_team} defense in CRITICAL state - exploit with goals")
    elif away_crisis == 'CRITICAL':
        notes.append(f"\n**⚠️ SINGLE-TEAM CRISIS:** {away_team} defense in CRITICAL state - exploit with goals")
    
    for note in notes:
        if '**' in note:
            st.markdown(note)
        else:
            st.markdown(f"• {note}")

def render_data_preview(df: pd.DataFrame, league_config: Dict):
    """Render data preview section."""
    
    with st.expander("📊 DATA PREVIEW & VALIDATION", expanded=False):
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Teams", len(df))
        with col2:
            st.metric("CSV Columns", len(df.columns))
        with col3:
            st.metric("Data Source", df.attrs.get('filename', 'Unknown'))
        with col4:
            st.metric("League", league_config['display_name'])
        
        st.markdown("**📋 Raw Data (First 10 Rows):**")
        st.dataframe(df.head(10), use_container_width=True)

def render_footer():
    """Render application footer."""
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>Brutball Professional Quantitative Framework v4.0</strong></p>
        <p>Complete Six-Phase Logic | 5 European Leagues | Multi-League Analysis</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            For professional use only. All betting involves risk. Never bet more than you can afford to lose.
            <br>Supports Premier League, La Liga, Bundesliga, Serie A, and Ligue 1.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_all_leagues_overview():
    """Render overview of all available leagues."""
    st.markdown('<div class="framework-header">🌍 AVAILABLE LEAGUES</div>', 
                unsafe_allow_html=True)
    
    cols = st.columns(5)
    for idx, (league_name, config) in enumerate(LEAGUES.items()):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                padding: 1rem;
                border-radius: 10px;
                background: {config['color']}15;
                border: 2px solid {config['color']}30;
                text-align: center;
                margin-bottom: 0.5rem;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{config['display_name'].split(' ')[0]}</div>
                <div style="font-weight: 600; color: {config['color']};">{league_name}</div>
                <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.25rem;">{config['country']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_professional_notes_text(analysis: Dict) -> List[str]:
    """Generate professional notes text for report."""
    notes = []
    archetype = analysis['archetype']
    team_context = analysis.get('team_context', {})
    
    home_team = analysis['match'].split(' vs ')[0]
    away_team = analysis['match'].split(' vs ')[1]
    
    if archetype == 'GOALS GALORE':
        notes.append("PRIMARY BET: Over 2.5 Goals")
        rationale_text = ' '.join(analysis['rationale'])
        if 'Chaos Override' in rationale_text:
            notes.append(f"CHAOS OVERRIDE ACTIVE: Both {home_team} and {away_team} in CRITICAL crisis")
        elif 'Volume Boost' in rationale_text:
            notes.append(f"VOLUME BOOST ACTIVE: Extreme goals conceded by both teams")
    
    elif archetype == 'FADE_THE_FAVORITE':
        favorite = team_context.get('favorite', 'Favorite')
        underdog = team_context.get('underdog', 'Underdog')
        notes.append(f"PRIMARY BET: Back {underdog} or Draw")
        notes.append(f"STRATEGY: Exploit {favorite}'s crisis while overperforming")
    
    elif archetype == 'BACK_THE_UNDERDOG':
        underdog = team_context.get('underdog', 'Underdog')
        favorite = team_context.get('favorite', 'Favorite')
        notes.append(f"PRIMARY BET: {underdog} to win or Draw")
        notes.append(f"STRATEGY: {underdog} undervalued, {favorite} underperforming")
    
    elif archetype == 'DEFENSIVE_GRIND':
        notes.append("PRIMARY BET: Under 2.5 Goals")
        notes.append(f"STRATEGY: {home_team} vs {away_team} style cancellation")
    
    else:
        notes.append("ACTION: NO BET - Preserve capital")
    
    return notes

# =================== MAIN APPLICATION ===================
def main():
    """Main application function."""
    
    render_header()
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # Render league selector
    selected_league = render_league_selector()
    
    # Render all leagues overview
    render_all_leagues_overview()
    
    # Load data for selected league
    with st.spinner(f"Loading {LEAGUES[selected_league]['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error(f"Failed to load data for {selected_league}. Please check your data files and try again.")
        return
    
    # Get league config
    league_config = LEAGUES[selected_league]
    
    # Initialize engine
    engine = BrutballProQuantitative(df)
    
    render_framework_overview()
    
    # Render match selector with league context
    home_team, away_team = render_match_selector(df, selected_league)
    
    if st.button("🚀 RUN QUANTITATIVE ANALYSIS", type="primary", use_container_width=True):
        
        with st.spinner(f"Running complete quantitative analysis for {home_team} vs {away_team}..."):
            analysis = engine.analyze_match(home_team, away_team)
            
            st.markdown("---")
            
            st.markdown('<div class="framework-header">🔍 LAYER 1: QUANTITATIVE SITUATION ANALYSIS</div>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                render_crisis_analysis(analysis['crisis_analysis']['home'], home_team, True)
            with col2:
                render_crisis_analysis(analysis['crisis_analysis']['away'], away_team, False)
            
            st.markdown("#### 📊 Reality Check (xG Performance vs Expectations)")
            col1, col2 = st.columns(2)
            with col1:
                render_reality_check(analysis['reality_check']['home'], home_team)
            with col2:
                render_reality_check(analysis['reality_check']['away'], away_team)
            
            st.markdown("#### ⚽ Tactical Edge Analysis")
            render_tactical_analysis(analysis['tactical_edge'])
            
            if analysis['defensive_grind_valid']:
                render_defensive_grind_analysis(analysis)
            
            st.markdown("---")
            st.markdown('<div class="framework-header">🎯 LAYER 2: CORRECTED QUANTITATIVE DECISION CLASSIFICATION</div>', 
                       unsafe_allow_html=True)
            
            render_archetype_decision(analysis, league_config)
            
            render_capital_allocation(analysis, league_config)
            
            render_professional_notes(analysis, league_config)
            
            st.markdown("---")
            st.markdown("#### 📤 Export Analysis Report")
            
            team_context = analysis.get('team_context', {})
            report = f"""
BRUTBALL PROFESSIONAL ANALYSIS REPORT (v4.0)
=============================================

LEAGUE: {league_config['display_name']}
Match: {analysis['match']}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

TEAM CONTEXT:
• Home: {home_team} (Position: #{analysis['key_metrics']['home_position']})
• Away: {away_team} (Position: #{analysis['key_metrics']['away_position']})
• Favorite: {team_context.get('favorite', 'N/A')} ⭐
• Underdog: {team_context.get('underdog', 'N/A')} ⚫

LAYER 1: QUANTITATIVE SITUATION ANALYSIS
---------------------------------------
Home Team ({home_team}):
• Crisis Score: {analysis['crisis_analysis']['home']['score']}/20
• Severity: {analysis['crisis_analysis']['home']['severity']}

Away Team ({away_team}):
• Crisis Score: {analysis['crisis_analysis']['away']['score']}/20
• Severity: {analysis['crisis_analysis']['away']['severity']}

CORRECTED LOGIC ACTIVE:
• Chaos Override: {analysis['crisis_analysis']['home']['severity'] == 'CRITICAL' and analysis['crisis_analysis']['away']['severity'] == 'CRITICAL'}
• Volume Concession: {analysis['crisis_analysis']['home']['details']['goals_conceded'] + analysis['crisis_analysis']['away']['details']['goals_conceded']} goals conceded last 5

LAYER 2: DECISION CLASSIFICATION
--------------------------------
Archetype: {analysis['archetype'].replace('_', ' ')}
Confidence Score: {analysis['confidence']}/10

Quantitative Scores:
• Goals Score: {analysis['quantitative_scores']['goals']:.1f}
• Fade Score: {analysis['quantitative_scores']['fade']:.1f}
• Back Score: {analysis['quantitative_scores']['back']:.1f}
• Defensive Grind: {analysis['quantitative_scores']['defensive_grind']:.1f}

LAYER 3: CAPITAL ALLOCATION
--------------------------
Recommended Stake: {analysis['recommended_stake']}% of bankroll

DECISION RATIONALE:
{chr(10).join(['• ' + line for line in analysis['rationale']])}

PROFESSIONAL ACTION:
{chr(10).join(['• ' + note.replace('**', '') for note in render_professional_notes_text(analysis)])}

=============================================
Brutball Professional Framework v4.0
Multi-League Analysis | 5 European Leagues Supported
            """
            
            st.download_button(
                label="📥 Download Complete Report",
                data=report,
                file_name=f"brutball_{selected_league.replace(' ', '_').lower()}_{home_team}_vs_{away_team}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    render_data_preview(df, league_config)
    render_footer()

# =================== APPLICATION ENTRY POINT ===================
if __name__ == "__main__":
    main()
