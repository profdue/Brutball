"""
VULNERABILITY-LOCK BETTING SYSTEM (VLBS)
Streamlit App - Direct GitHub Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
from io import StringIO
import requests
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="VLBS Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .bet-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .no-bet-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #ddd;
    }
    .high-confidence {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
    }
    .medium-confidence {
        background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%);
    }
    .low-confidence {
        background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .rule-tag {
        display: inline-block;
        background: #FF6B6B;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .success-badge {
        background: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .warning-badge {
        background: #FF9800;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .danger-badge {
        background: #F44336;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .league-badge {
        display: inline-block;
        background: #1E88E5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# =================== CONSTANTS ===================
VLBS_THRESHOLDS = {
    'RULE1_AWAY_XGA': 2.0,
    'RULE2_HOME_XG': 1.4,
    'RULE2_AWAY_XGA': 1.8,
    'RULE3_HOME_AWAY_RATIO': 1.8,
    'RULE4_AVG_SCORED': 1.0,
    'RULE5_AWAY_XG': 0.9,
    'RULE5_HOME_XGA': 1.3,
}

# GitHub repository information
GITHUB_BASE_URL = "https://raw.githubusercontent.com/profdue/Brutball/main/leagues"

# League files mapping
LEAGUE_FILES = {
    "Premier League": "premier-league.csv",
    "La Liga": "laliga.csv",
    "Serie A": "serie-a.csv",
    "Bundesliga": "bundesliga.csv",
    "Ligue 1": "ligue-1.csv",
    "Primeira Liga": "primeira-liga.csv",
    "Eredivisie": "eredivisie.csv"
}

# =================== GITHUB DATA LOADING ===================
@st.cache_data(ttl=3600)
def load_league_from_github(league_name):
    """Load league data directly from GitHub"""
    try:
        # Get the filename for the league
        filename = LEAGUE_FILES.get(league_name)
        if not filename:
            st.error(f"League '{league_name}' not found in available leagues")
            return None
        
        # Construct GitHub URL
        url = f"{GITHUB_BASE_URL}/{filename}"
        
        # Load CSV from GitHub
        df = pd.read_csv(url)
        
        # Clean column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Ensure required columns exist
        required_columns = [
            'team', 'home_matches_played', 'away_matches_played',
            'home_goals_scored', 'away_goals_scored',
            'home_goals_conceded', 'away_goals_conceded',
            'home_xg_for', 'away_xg_for',
            'home_xg_against', 'away_xg_against',
            'goals_scored_last_5', 'goals_conceded_last_5'
        ]
        
        # Check for missing columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.warning(f"Missing columns in {league_name}: {', '.join(missing_cols)}")
            return None
        
        # Check for optional columns
        if 'home_goals_conceded_last_5' not in df.columns:
            df['home_goals_conceded_last_5'] = None
        if 'away_goals_conceded_last_5' not in df.columns:
            df['away_goals_conceded_last_5'] = None
        
        # ========== PRE-CALCULATIONS (Section 2) ==========
        
        # Venue-specific averages
        df['home_xg_per_match'] = df.apply(
            lambda x: x['home_xg_for'] / x['home_matches_played'] 
            if x['home_matches_played'] > 0 else 0, axis=1
        )
        
        df['away_xg_per_match'] = df.apply(
            lambda x: x['away_xg_for'] / x['away_matches_played'] 
            if x['away_matches_played'] > 0 else 0, axis=1
        )
        
        df['home_xga_per_match'] = df.apply(
            lambda x: x['home_xg_against'] / x['home_matches_played'] 
            if x['home_matches_played'] > 0 else 0, axis=1
        )
        
        df['away_xga_per_match'] = df.apply(
            lambda x: x['away_xg_against'] / x['away_matches_played'] 
            if x['away_matches_played'] > 0 else 0, axis=1
        )
        
        # Recent form (last 5 matches)
        df['avg_scored_last_5'] = df['goals_scored_last_5'] / 5
        df['avg_conceded_last_5'] = df['goals_conceded_last_5'] / 5
        
        df['home_avg_conceded_last_5'] = df.apply(
            lambda x: x['home_goals_conceded_last_5'] / 5 
            if pd.notnull(x['home_goals_conceded_last_5']) else x['avg_conceded_last_5'], 
            axis=1
        )
        
        df['away_avg_conceded_last_5'] = df.apply(
            lambda x: x['away_goals_conceded_last_5'] / 5 
            if pd.notnull(x['away_goals_conceded_last_5']) else x['avg_conceded_last_5'], 
            axis=1
        )
        
        # Home/Away performance ratio (critical)
        def calculate_home_away_ratio(row):
            if row['away_xg_per_match'] > 0:
                return row['home_xg_per_match'] / row['away_xg_per_match']
            else:
                return 999  # Treat as infinite home advantage
        
        df['home_away_ratio'] = df.apply(calculate_home_away_ratio, axis=1)
        
        # Add some defensive vulnerability metrics
        df['defensive_vulnerability_score'] = df['away_xga_per_match'] * 1.5 + df['avg_conceded_last_5'] * 0.5
        
        st.success(f"✅ Loaded {len(df)} teams from {league_name}")
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading {league_name}: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def list_available_leagues():
    """Check which leagues are available in the GitHub repository"""
    available_leagues = {}
    
    for league_name, filename in LEAGUE_FILES.items():
        url = f"{GITHUB_BASE_URL}/{filename}"
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                available_leagues[league_name] = filename
        except:
            continue
    
    return available_leagues

# =================== VLBS RULES IMPLEMENTATION ===================
def rule1_terrible_away_defense(home_team, away_team):
    """RULE 1: TERRIBLE AWAY DEFENSE LOCK (Highest Priority)"""
    condition = away_team['away_xga_per_match'] > VLBS_THRESHOLDS['RULE1_AWAY_XGA']
    
    if condition:
        return {
            'rule_triggered': 'RULE_1_TERRIBLE_AWAY_DEFENSE',
            'bet': 'HOME_WIN',
            'market': 'Match Winner',
            'confidence': 'HIGH',
            'stake_multiplier': 2.0,
            'reason': f"Away team concedes {away_team['away_xga_per_match']:.2f} xG/match away (critical threshold: >2.0)",
            'data_evidence': {
                'home_xg_per_match': home_team['home_xg_per_match'],
                'away_xga_per_match': away_team['away_xga_per_match'],
                'threshold_violation': f"+{away_team['away_xga_per_match'] - 2.0:.2f} above 2.0"
            }
        }
    return None

def rule2_attack_defense_mismatch(home_team, away_team):
    """RULE 2: HOME ATTACK vs AWAY DEFENSE MISMATCH"""
    condition = (
        home_team['home_xg_per_match'] > VLBS_THRESHOLDS['RULE2_HOME_XG'] and 
        away_team['away_xga_per_match'] > VLBS_THRESHOLDS['RULE2_AWAY_XGA']
    )
    
    if condition:
        return {
            'rule_triggered': 'RULE_2_ATTACK_DEFENSE_MISMATCH',
            'bet': 'HOME_WIN',
            'market': 'Match Winner',
            'confidence': 'HIGH',
            'stake_multiplier': 1.5,
            'reason': f"Home attack ({home_team['home_xg_per_match']:.2f} xG) vs weak away defense ({away_team['away_xga_per_match']:.2f} xGA)",
            'data_evidence': {
                'home_xg_per_match': home_team['home_xg_per_match'],
                'away_xga_per_match': away_team['away_xga_per_match'],
                'home_threshold': f"{home_team['home_xg_per_match']:.2f} > {VLBS_THRESHOLDS['RULE2_HOME_XG']}",
                'away_threshold': f"{away_team['away_xga_per_match']:.2f} > {VLBS_THRESHOLDS['RULE2_AWAY_XGA']}"
            }
        }
    return None

def rule3_extreme_home_advantage(home_team, away_team):
    """RULE 3: EXTREME HOME ADVANTAGE"""
    condition = home_team['home_away_ratio'] > VLBS_THRESHOLDS['RULE3_HOME_AWAY_RATIO']
    
    if condition:
        return {
            'rule_triggered': 'RULE_3_EXTREME_HOME_ADVANTAGE',
            'bet': 'HOME_WIN',
            'market': 'Match Winner',
            'confidence': 'MEDIUM',
            'stake_multiplier': 1.0,
            'reason': f"Home/away performance ratio: {home_team['home_away_ratio']:.2f}x (threshold: >1.8x)",
            'data_evidence': {
                'home_xg_per_match': home_team['home_xg_per_match'],
                'away_xg_per_match': home_team['away_xg_per_match'],
                'home_away_ratio': home_team['home_away_ratio'],
                'threshold': f"{home_team['home_away_ratio']:.2f} > {VLBS_THRESHOLDS['RULE3_HOME_AWAY_RATIO']}"
            }
        }
    return None

def rule4_dual_low_offense_under(home_team, away_team):
    """RULE 4: DUAL LOW-OFFENSE UNDER"""
    condition = (
        home_team['avg_scored_last_5'] < VLBS_THRESHOLDS['RULE4_AVG_SCORED'] and 
        away_team['avg_scored_last_5'] < VLBS_THRESHOLDS['RULE4_AVG_SCORED']
    )
    
    if condition:
        return {
            'rule_triggered': 'RULE_4_DUAL_LOW_OFFENSE_UNDER',
            'bet': 'UNDER_2_5',
            'market': 'Total Goals',
            'confidence': 'MEDIUM',
            'stake_multiplier': 1.0,
            'reason': f"Both teams low scoring: Home {home_team['avg_scored_last_5']:.1f}, Away {away_team['avg_scored_last_5']:.1f} goals/match (last 5)",
            'data_evidence': {
                'home_avg_scored_last_5': home_team['avg_scored_last_5'],
                'away_avg_scored_last_5': away_team['avg_scored_last_5'],
                'threshold': f"both < {VLBS_THRESHOLDS['RULE4_AVG_SCORED']}"
            }
        }
    return None

def rule5_clean_sheet_no(home_team, away_team):
    """RULE 5: CLEAN SHEET NO FOR TERRIBLE AWAY ATTACK"""
    condition = (
        away_team['away_xg_per_match'] < VLBS_THRESHOLDS['RULE5_AWAY_XG'] and 
        home_team['home_xga_per_match'] < VLBS_THRESHOLDS['RULE5_HOME_XGA']
    )
    
    if condition:
        return {
            'rule_triggered': 'RULE_5_CLEAN_SHEET_NO',
            'bet': 'AWAY_NO_SCORE',
            'market': 'Both Teams to Score',
            'confidence': 'MEDIUM',
            'stake_multiplier': 1.0,
            'reason': f"Away attack weak ({away_team['away_xg_per_match']:.2f} xG) vs home defense solid ({home_team['home_xga_per_match']:.2f} xGA)",
            'data_evidence': {
                'away_xg_per_match': away_team['away_xg_per_match'],
                'home_xga_per_match': home_team['home_xga_per_match'],
                'away_threshold': f"{away_team['away_xg_per_match']:.2f} < {VLBS_THRESHOLDS['RULE5_AWAY_XG']}",
                'home_threshold': f"{home_team['home_xga_per_match']:.2f} < {VLBS_THRESHOLDS['RULE5_HOME_XGA']}"
            }
        }
    return None

# =================== MAIN ANALYSIS FUNCTION ===================
def analyze_match(home_team, away_team):
    """Main analysis function - returns betting recommendations"""
    recommendations = []
    
    # Check Rule 1 (Highest priority)
    rec1 = rule1_terrible_away_defense(home_team, away_team)
    if rec1:
        recommendations.append(rec1)
        # Rule 1 is so strong, return immediately
        return recommendations
    
    # Check Rule 2 (Second priority)
    rec2 = rule2_attack_defense_mismatch(home_team, away_team)
    if rec2:
        recommendations.append(rec2)
    
    # Check Rule 3 (Third priority)
    rec3 = rule3_extreme_home_advantage(home_team, away_team)
    if rec3:
        recommendations.append(rec3)
    
    # Check Under rules (if no strong winner bet found)
    if not recommendations:
        rec4 = rule4_dual_low_offense_under(home_team, away_team)
        if rec4:
            recommendations.append(rec4)
        
        rec5 = rule5_clean_sheet_no(home_team, away_team)
        if rec5:
            recommendations.append(rec5)
    
    # If still nothing
    if not recommendations:
        recommendations.append({
            'bet': 'NO_BET',
            'reason': 'No clear edge found',
            'data_evidence': {
                'home_xg_per_match': home_team['home_xg_per_match'],
                'away_xga_per_match': away_team['away_xga_per_match'],
                'home_away_ratio': home_team['home_away_ratio']
            }
        })
    
    return recommendations

# =================== STAKE CALCULATION ===================
def calculate_stake(base_stake, recommendation):
    """Calculate stake based on confidence level"""
    stake_multipliers = {
        'HIGH': 2.0,    # Rule 1 bets
        'MEDIUM': 1.5,  # Rule 2 bets  
        'LOW': 1.0      # Rule 3+ bets
    }
    
    if recommendation['bet'] == 'NO_BET':
        return 0.0
    
    multiplier = recommendation.get('stake_multiplier', 1.0)
    confidence = recommendation.get('confidence', 'LOW')
    
    stake = base_stake * stake_multipliers.get(confidence, 1.0) * multiplier
    
    # Cap at 5% of bankroll
    return min(stake, 0.05)

# =================== VALIDATION CHECKS ===================
def validate_data(home_team, away_team):
    """Ensure data quality before analysis"""
    checks = []
    
    # Check minimum matches played
    if home_team['home_matches_played'] < 5:
        checks.append(f"⚠️ Home team only {home_team['home_matches_played']} home matches")
    
    if away_team['away_matches_played'] < 5:
        checks.append(f"⚠️ Away team only {away_team['away_matches_played']} away matches")
    
    # Check for data anomalies
    if home_team['home_xga_per_match'] > 3.0:
        checks.append(f"⚠️ Home xGA suspiciously high: {home_team['home_xga_per_match']:.2f}")
    
    if away_team['away_xga_per_match'] > 3.0:
        checks.append(f"⚠️ Away xGA suspiciously high: {away_team['away_xga_per_match']:.2f}")
    
    return checks

# =================== UI COMPONENTS ===================
def display_match_analysis(home_team, away_team, recommendations, base_stake=0.01):
    """Display beautiful match analysis"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🏆 {home_team['team']} vs {away_team['team']}")
        
        # Display key metrics
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("Home xG/Match", f"{home_team['home_xg_per_match']:.2f}")
        with metric_cols[1]:
            st.metric("Away xGA/Match", f"{away_team['away_xga_per_match']:.2f}")
        with metric_cols[2]:
            st.metric("Home/Away Ratio", f"{home_team['home_away_ratio']:.2f}")
        with metric_cols[3]:
            st.metric("Form (Last 5)", f"{home_team['avg_scored_last_5']:.1f}-{away_team['avg_scored_last_5']:.1f}")
    
    with col2:
        validation_checks = validate_data(home_team, away_team)
        if validation_checks:
            with st.expander("Data Quality Warnings", expanded=False):
                for check in validation_checks:
                    st.warning(check)
    
    # Display recommendations
    if recommendations[0]['bet'] == 'NO_BET':
        st.markdown("""
        <div class="no-bet-card">
            <h3>🤔 No Bet Recommended</h3>
            <p>No clear vulnerability detected in this match.</p>
            <p><strong>Analysis:</strong> {}</p>
        </div>
        """.format(recommendations[0]['reason']), unsafe_allow_html=True)
    else:
        for rec in recommendations:
            stake_percentage = calculate_stake(base_stake, rec) * 100
            
            # Determine confidence class
            conf_class = ""
            if rec['confidence'] == 'HIGH':
                conf_class = "high-confidence"
            elif rec['confidence'] == 'MEDIUM':
                conf_class = "medium-confidence"
            else:
                conf_class = "low-confidence"
            
            st.markdown(f"""
            <div class="bet-card {conf_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="rule-tag">{rec['rule_triggered'].replace('_', ' ')}</span>
                        <h3 style="margin: 0.5rem 0; color: white;">🎯 Bet: {rec['bet'].replace('_', ' ')}</h3>
                    </div>
                    <div style="text-align: right;">
                        <div class="success-badge" style="font-size: 1.2rem;">{stake_percentage:.1f}%</div>
                        <div style="font-size: 0.9rem; margin-top: 0.25rem;">Stake</div>
                    </div>
                </div>
                <p style="margin: 1rem 0;"><strong>Market:</strong> {rec['market']}</p>
                <p style="margin: 1rem 0;"><strong>Reason:</strong> {rec['reason']}</p>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>Data Evidence:</strong>
                    <pre style="margin: 0; color: white; font-size: 0.9rem;">{rec.get('data_evidence', {})}</pre>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_team_comparison(home_team, away_team):
    """Display detailed team comparison"""
    st.markdown("### 📊 Detailed Team Comparison")
    
    # Create comparison dataframe
    comparison_data = {
        'Metric': [
            'xG Per Match (Home)', 'xG Per Match (Away)',
            'xGA Per Match (Home)', 'xGA Per Match (Away)',
            'Home/Away Ratio', 'Avg Scored (Last 5)',
            'Avg Conceded (Last 5)', 'Defensive Vulnerability'
        ],
        home_team['team']: [
            f"{home_team['home_xg_per_match']:.2f}", 
            f"{home_team['away_xg_per_match']:.2f}",
            f"{home_team['home_xga_per_match']:.2f}",
            f"{home_team['away_xga_per_match']:.2f}",
            f"{home_team['home_away_ratio']:.2f}",
            f"{home_team['avg_scored_last_5']:.2f}",
            f"{home_team['avg_conceded_last_5']:.2f}",
            f"{home_team.get('defensive_vulnerability_score', 0):.2f}"
        ],
        away_team['team']: [
            f"{away_team['home_xg_per_match']:.2f}",
            f"{away_team['away_xg_per_match']:.2f}",
            f"{away_team['home_xga_per_match']:.2f}",
            f"{away_team['away_xga_per_match']:.2f}",
            f"{away_team['home_away_ratio']:.2f}",
            f"{away_team['avg_scored_last_5']:.2f}",
            f"{away_team['avg_conceded_last_5']:.2f}",
            f"{away_team.get('defensive_vulnerability_score', 0):.2f}"
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

def display_league_overview(df, league_name):
    """Display league-wide vulnerability analysis"""
    st.markdown(f"### 🏆 {league_name} Vulnerability Analysis")
    
    # Find most vulnerable away defenses
    vulnerable_away = df.nlargest(10, 'away_xga_per_match')[['team', 'away_xga_per_match', 'away_matches_played']]
    vulnerable_away.columns = ['Team', 'Away xGA/Match', 'Away Matches']
    
    # Find best home attacks
    strong_home = df.nlargest(10, 'home_xg_per_match')[['team', 'home_xg_per_match', 'home_matches_played']]
    strong_home.columns = ['Team', 'Home xG/Match', 'Home Matches']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Most Vulnerable Away Defenses")
        st.dataframe(vulnerable_away, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### ⚡ Strongest Home Attacks")
        st.dataframe(strong_home, use_container_width=True, hide_index=True)

# =================== MAIN APP ===================
def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Vulnerability-Lock Betting System (VLBS)</h1>', unsafe_allow_html=True)
    st.markdown("**Defensive Vulnerability Detection System - Direct GitHub Integration**")
    
    # Check available leagues
    with st.spinner("Checking available leagues..."):
        available_leagues = list_available_leagues()
    
    if not available_leagues:
        st.error("""
        ❌ No leagues found in GitHub repository!
        
        Please ensure:
        1. Your CSV files are in the `leagues/` folder
        2. Files are named correctly (e.g., premier-league.csv, laliga.csv)
        3. Repository is public
        
        Available leagues should be at: `https://github.com/profdue/Brutball/tree/main/leagues`
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Display available leagues
        st.markdown(f"#### 📁 Available Leagues ({len(available_leagues)})")
        for league in available_leagues.keys():
            st.markdown(f'<span class="league-badge">{league}</span>', unsafe_allow_html=True)
        
        # League selection
        selected_league = st.selectbox(
            "Select League", 
            list(available_leagues.keys()),
            help="Choose a league to analyze"
        )
        
        # Bankroll settings
        st.markdown("---")
        st.markdown("### 💰 Bankroll Management")
        bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=1000000, value=1000, step=100)
        base_stake_percentage = st.slider("Base Stake (% of bankroll)", 0.5, 5.0, 1.0, 0.5) / 100
        
        # Load data button
        if st.button("🔄 Load League Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data from GitHub..."):
                st.session_state.df = load_league_from_github(selected_league)
                st.session_state.league_name = selected_league
                if st.session_state.df is not None:
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Stats")
        if 'df' in st.session_state:
            st.metric("Teams Loaded", len(st.session_state.df))
            avg_xga = st.session_state.df['away_xga_per_match'].mean()
            st.metric("Avg Away xGA", f"{avg_xga:.2f}")
    
    # Main content
    if 'df' in st.session_state and st.session_state.df is not None:
        df = st.session_state.df
        league_name = st.session_state.league_name
        
        # Team selection
        st.markdown("### 🏟️ Match Selection")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            teams = sorted(df['team'].unique())
            home_team_name = st.selectbox("Home Team", teams, key="home_select")
        
        with col2:
            st.markdown("<br><br><h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True)
        
        with col3:
            # Filter out home team from away options
            away_options = [t for t in teams if t != home_team_name]
            away_team_name = st.selectbox("Away Team", away_options, key="away_select")
        
        # Analyze button
        if st.button("🔍 Analyze Match", type="primary", use_container_width=True):
            # Get team data
            home_team = df[df['team'] == home_team_name].iloc[0].to_dict()
            away_team = df[df['team'] == away_team_name].iloc[0].to_dict()
            
            # Analyze match
            recommendations = analyze_match(home_team, away_team)
            
            # Store in session state
            st.session_state.home_team = home_team
            st.session_state.away_team = away_team
            st.session_state.recommendations = recommendations
            st.session_state.analyzed = True
        
        # Display analysis if available
        if 'analyzed' in st.session_state and st.session_state.analyzed:
            st.markdown("---")
            
            # Display match analysis
            display_match_analysis(
                st.session_state.home_team,
                st.session_state.away_team,
                st.session_state.recommendations,
                base_stake_percentage
            )
            
            # Detailed analysis tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Team Comparison", "⚖️ Rule Analysis", "🏆 League Overview", "📚 System Info"])
            
            with tab1:
                display_team_comparison(st.session_state.home_team, st.session_state.away_team)
            
            with tab2:
                st.markdown("### ⚖️ VLBS Rule Analysis")
                
                # Rule 1 analysis
                rule1_cols = st.columns([3, 1])
                with rule1_cols[0]:
                    st.markdown("#### Rule 1: Terrible Away Defense")
                    st.markdown("**Condition:** `away_xga_per_match > 2.0`")
                
                with rule1_cols[1]:
                    away_xga = st.session_state.away_team['away_xga_per_match']
                    threshold = VLBS_THRESHOLDS['RULE1_AWAY_XGA']
                    status = "✅ TRIGGERED" if away_xga > threshold else "❌ NOT TRIGGERED"
                    st.metric("Status", status, f"{away_xga:.2f} vs {threshold}")
                
                # Rule 2 analysis
                rule2_cols = st.columns([3, 1])
                with rule2_cols[0]:
                    st.markdown("#### Rule 2: Attack vs Defense Mismatch")
                    st.markdown("**Condition:** `home_xg > 1.4 AND away_xga > 1.8`")
                
                with rule2_cols[1]:
                    home_xg = st.session_state.home_team['home_xg_per_match']
                    away_xga = st.session_state.away_team['away_xga_per_match']
                    condition1 = home_xg > VLBS_THRESHOLDS['RULE2_HOME_XG']
                    condition2 = away_xga > VLBS_THRESHOLDS['RULE2_AWAY_XGA']
                    status = "✅ TRIGGERED" if condition1 and condition2 else "❌ NOT TRIGGERED"
                    st.metric("Status", status)
            
            with tab3:
                display_league_overview(df, league_name)
            
            with tab4:
                st.markdown("### 📚 VLBS System Philosophy")
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.info("""
                    **Core Principle**: Find and exploit DEFENSIVE VULNERABILITIES
                    
                    **Why it works**:
                    1. Defensive stats are more stable than offensive stats
                    2. Away defense is most predictive
                    3. Extreme values matter (>2.0 away xGA)
                    4. Home advantage is real
                    """)
                
                with col_info2:
                    st.warning("""
                    **Thresholds are empirically derived**
                    - DO NOT MODIFY thresholds
                    - DO NOT add new rules without testing
                    - ALWAYS use venue-specific data
                    - NEVER bet if data quality fails
                    """)
                
                st.markdown("#### 📋 Current Thresholds")
                thresholds_df = pd.DataFrame(list(VLBS_THRESHOLDS.items()), columns=['Rule', 'Threshold'])
                st.dataframe(thresholds_df, use_container_width=True, hide_index=True)
        
        # Display data preview
        with st.expander("📁 Data Preview", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show column information
            st.markdown("#### 📊 Data Columns")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null': df.notnull().sum()
            })
            st.dataframe(col_info, use_container_width=True, height=300)
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to VLBS Predictor
        
        This app implements the **Vulnerability-Lock Betting System** to find and exploit defensive vulnerabilities in football matches.
        
        ### How to use:
        1. **Select a league** from the sidebar
        2. **Click "Load League Data"** to fetch data from GitHub
        3. **Choose home and away teams**
        4. **Click "Analyze Match"** to get VLBS predictions
        
        ### Available Leagues:
        """)
        
        for league in available_leagues.keys():
            st.markdown(f"- **{league}**")
        
        st.markdown("""
        ---
        **⚡ System Status**: Ready to connect to GitHub
        **📊 Data Source**: `https://github.com/profdue/Brutball/tree/main/leagues`
        """)

if __name__ == "__main__":
    main()