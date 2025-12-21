import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Brutball Pro Analyzer",
    page_icon="⚽",
    layout="wide"
)

# Add custom CSS
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
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">⚽ Brutball Professional Decision Framework</div>', unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_league_data():
    try:
        # Try loading from different possible paths
        paths_to_try = [
            'leagues/premier_league.csv',
            './leagues/premier_league.csv',
            'premier_league.csv'
        ]
        
        df = None
        for path in paths_to_try:
            try:
                df = pd.read_csv(path)
                st.success(f"✅ Data loaded successfully from: {path}")
                break
            except:
                continue
        
        if df is None:
            # If file not found, try loading from GitHub URL
            github_url = "https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv"
            df = pd.read_csv(github_url)
            st.success("✅ Data loaded successfully from GitHub")
        
        # Clean column names (strip whitespace, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Add derived columns
        if 'home_matches_played' in df.columns and 'home_goals_scored' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
        
        # Calculate form points
        def form_to_points(form_str):
            if pd.isna(form_str):
                return 7.5  # Default average
            points = {'W': 3, 'D': 1, 'L': 0}
            return sum(points.get(char, 0) for char in str(form_str))
        
        if 'form_last_5_overall' in df.columns:
            df['form_points'] = df['form_last_5_overall'].apply(form_to_points)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# Load data
df = load_league_data()

if df is None:
    st.stop()

# Display framework status
st.markdown("### 🏗️ Three-Layer Decision Framework")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="layer-box">', unsafe_allow_html=True)
    st.markdown("**Layer 1: Situation Classification**")
    st.markdown("✅ Ready")
    st.markdown("Crisis Scan → Reality Check → Tactical Edge")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="layer-box">', unsafe_allow_html=True)
    st.markdown("**Layer 2: Decision Firewall**")
    st.markdown("✅ Ready")
    st.markdown("Market validation & Conservative defaults")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="layer-box">', unsafe_allow_html=True)
    st.markdown("**Layer 3: Capital Allocation**")
    st.markdown("⏳ Manual (Professional Judgment)")
    st.markdown("Position sizing & Bankroll management")
    st.markdown('</div>', unsafe_allow_html=True)

# Layer 1: Crisis Detection Functions
def detect_defensive_crisis(team_data):
    """Detect if a team is in defensive crisis"""
    crisis_score = 0
    signals = []
    
    # Check missing defenders
    defenders_out = team_data.get('defenders_out', 0)
    if defenders_out >= 3:
        crisis_score += 2
        signals.append(f"🚨 Missing {defenders_out} defenders")
    
    # Check recent goals conceded
    goals_conceded_last_5 = team_data.get('goals_conceded_last_5', 0)
    if goals_conceded_last_5 >= 12:
        crisis_score += 2
        signals.append(f"📉 Conceded {goals_conceded_last_5} in last 5")
    elif goals_conceded_last_5 >= 10:
        crisis_score += 1
        signals.append(f"⚠️ Conceded {goals_conceded_last_5} in last 5")
    
    # Check form
    form = str(team_data.get('form_last_5_overall', ''))
    if 'LLL' in form:
        crisis_score += 2
        signals.append("📉 Poor form: LLL in last 5")
    elif 'LL' in form[-2:]:
        crisis_score += 1
        signals.append("⚠️ Recent losses")
    
    return {
        'crisis_score': crisis_score,
        'signals': signals,
        'severity': 'CRITICAL' if crisis_score >= 3 else 'WARNING' if crisis_score >= 1 else 'STABLE'
    }

def reality_check(team_data):
    """Check if team is over/under performing xG"""
    insights = []
    
    # Home performance
    home_goals = team_data.get('home_goals_scored', 0)
    home_xg = team_data.get('home_xg_for', 0)
    home_games = team_data.get('home_matches_played', 1)
    
    if home_games > 0:
        home_gap = (home_goals - home_xg) / home_games
        if home_gap > 0.3:
            insights.append({
                'type': 'OVERPERFORMING_HOME',
                'value': f"+{home_gap:.2f} goals/game vs xG",
                'implication': 'Regression likely'
            })
        elif home_gap < -0.3:
            insights.append({
                'type': 'UNDERPERFORMING_HOME',
                'value': f"{home_gap:.2f} goals/game vs xG",
                'implication': 'Improvement possible'
            })
    
    # Away performance
    away_goals = team_data.get('away_goals_scored', 0)
    away_xg = team_data.get('away_xg_for', 0)
    away_games = team_data.get('away_matches_played', 1)
    
    if away_games > 0:
        away_gap = (away_goals - away_xg) / away_games
        if away_gap > 0.3:
            insights.append({
                'type': 'OVERPERFORMING_AWAY',
                'value': f"+{away_gap:.2f} goals/game vs xG",
                'implication': 'Regression likely'
            })
        elif away_gap < -0.3:
            insights.append({
                'type': 'UNDERPERFORMING_AWAY',
                'value': f"{away_gap:.2f} goals/game vs xG",
                'implication': 'Improvement possible'
            })
    
    return insights

def analyze_tactical_matchup(home_team, away_team):
    """Analyze goal type matchups"""
    stories = []
    
    # Counter attack analysis
    home_counter_pct = home_team.get('home_goals_counter_for', 0) / max(1, home_team.get('home_goals_scored', 1))
    away_counter_vuln = away_team.get('away_goals_counter_against', 0) / max(1, away_team.get('away_goals_conceded', 1))
    
    if home_counter_pct > 0.2 and away_counter_vuln > 0.2:
        stories.append({
            'title': '⚡ Counter-Attack Opportunity',
            'detail': f"Home scores {home_counter_pct:.0%} from counters, Away concedes {away_counter_vuln:.0%} from counters",
            'impact': 'HIGH'
        })
    
    # Set piece analysis
    home_setpiece_pct = home_team.get('home_goals_setpiece_for', 0) / max(1, home_team.get('home_goals_scored', 1))
    away_setpiece_vuln = away_team.get('away_goals_setpiece_against', 0) / max(1, away_team.get('away_goals_conceded', 1))
    
    if home_setpiece_pct > 0.25 and away_setpiece_vuln > 0.3:
        stories.append({
            'title': '🎯 Set-Piece Advantage',
            'detail': f"Home scores {home_setpiece_pct:.0%} from set pieces, Away concedes {away_setpiece_vuln:.0%}",
            'impact': 'MEDIUM'
        })
    
    return stories

# Layer 2: Decision Classification
def classify_archetype(home_crisis, away_crisis, home_reality, away_reality, tactical_stories):
    """Classify match into one of 5 decision archetypes"""
    
    # Check for crisis games
    home_crisis_severe = home_crisis['severity'] == 'CRITICAL'
    away_crisis_severe = away_crisis['severity'] == 'CRITICAL'
    
    # Check over/under performance
    home_over = any('OVERPERFORMING' in str(item.get('type', '')) for item in home_reality)
    home_under = any('UNDERPERFORMING' in str(item.get('type', '')) for item in home_reality)
    away_over = any('OVERPERFORMING' in str(item.get('type', '')) for item in away_reality)
    away_under = any('UNDERPERFORMING' in str(item.get('type', '')) for item in away_reality)
    
    # Archetype logic
    if away_crisis_severe and away_over:
        return {
            'archetype': 'FADE_THE_FAVORITE',
            'confidence': 'HIGH',
            'reason': 'Away team in crisis & overperforming',
            'recommendation': 'Bet against away team'
        }
    elif not home_crisis_severe and home_under and len(tactical_stories) > 0:
        return {
            'archetype': 'BACK_THE_UNDERDOG',
            'confidence': 'MEDIUM',
            'reason': 'Home team stable, underperforming, tactical edge',
            'recommendation': 'Bet on home team'
        }
    elif home_crisis_severe or away_crisis_severe:
        return {
            'archetype': 'GOALS_GALORE',
            'confidence': 'HIGH',
            'reason': 'Defensive crisis on one or both sides',
            'recommendation': 'Bet Over 2.5 goals'
        }
    elif home_crisis['crisis_score'] == 0 and away_crisis['crisis_score'] == 0:
        # Check if both have solid defenses (low goals conceded)
        home_gc = df[df['team'].str.lower() == home_team.lower()]['goals_conceded_last_5'].values[0] if not df.empty else 0
        away_gc = df[df['team'].str.lower() == away_team.lower()]['goals_conceded_last_5'].values[0] if not df.empty else 0
        
        if home_gc <= 8 and away_gc <= 8:
            return {
                'archetype': 'DEFENSIVE_GRIND',
                'confidence': 'MEDIUM',
                'reason': 'Both teams defensively solid',
                'recommendation': 'Bet Under 2.5 goals'
            }
    
    # Default if no clear pattern
    return {
        'archetype': 'AVOID',
        'confidence': 'LOW',
        'reason': 'Mixed signals, no clear edge',
        'recommendation': 'No bet recommended'
    }

# Main app interface
st.markdown("### 🏟️ Match Analysis")

# Team selection
col1, col2 = st.columns(2)
with col1:
    # Get available teams (using correct column name 'team')
    available_teams = sorted(df['team'].unique()) if 'team' in df.columns else []
    home_team = st.selectbox("🏠 Home Team", available_teams)

with col2:
    away_teams = [t for t in available_teams if t != home_team]
    away_team = st.selectbox("✈️ Away Team", away_teams)

if home_team and away_team:
    # Get team data
    home_data = df[df['team'] == home_team].iloc[0].to_dict()
    away_data = df[df['team'] == away_team].iloc[0].to_dict()
    
    # Run Layer 1 Analysis
    st.markdown("---")
    st.markdown("### 🔍 Layer 1: Situation Classification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {home_team}")
        home_crisis = detect_defensive_crisis(home_data)
        home_reality = reality_check(home_data)
        
        if home_crisis['severity'] != 'STABLE':
            st.markdown(f'<div class="crisis-alert">', unsafe_allow_html=True)
            st.markdown(f"**{home_crisis['severity']} ALERT**")
            for signal in home_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("✅ Defensive structure: STABLE")
        
        # Reality check
        for insight in home_reality:
            st.markdown(f"📊 {insight['type'].replace('_', ' ')}: {insight['value']}")
            st.markdown(f"   *Implication: {insight['implication']}*")
    
    with col2:
        st.markdown(f"#### {away_team}")
        away_crisis = detect_defensive_crisis(away_data)
        away_reality = reality_check(away_data)
        
        if away_crisis['severity'] != 'STABLE':
            st.markdown(f'<div class="crisis-alert">', unsafe_allow_html=True)
            st.markdown(f"**{away_crisis['severity']} ALERT**")
            for signal in away_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("✅ Defensive structure: STABLE")
        
        # Reality check
        for insight in away_reality:
            st.markdown(f"📊 {insight['type'].replace('_', ' ')}: {insight['value']}")
            st.markdown(f"   *Implication: {insight['implication']}*")
    
    # Tactical Analysis
    st.markdown("#### ⚽ Tactical Edge Analysis")
    tactical_stories = analyze_tactical_matchup(home_data, away_data)
    
    if tactical_stories:
        for story in tactical_stories:
            st.markdown(f'<div class="opportunity-alert">', unsafe_allow_html=True)
            st.markdown(f"**{story['title']}** ({story['impact']} Impact)")
            st.markdown(f"{story['detail']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("No clear tactical edge identified")
    
    # Layer 2: Decision Classification
    st.markdown("---")
    st.markdown("### 🎯 Layer 2: Decision Classification")
    
    archetype = classify_archetype(home_crisis, away_crisis, home_reality, away_reality, tactical_stories)
    
    # Display archetype with appropriate styling
    archetype_colors = {
        'FADE_THE_FAVORITE': '#DC2626',
        'BACK_THE_UNDERDOG': '#16A34A',
        'GOALS_GALORE': '#EA580C',
        'DEFENSIVE_GRIND': '#2563EB',
        'AVOID': '#6B7280'
    }
    
    color = archetype_colors.get(archetype['archetype'], '#6B7280')
    
    st.markdown(f"""
    <div style="padding: 1.5rem; border-radius: 10px; background-color: {color}10; border-left: 5px solid {color};">
        <h3 style="color: {color}; margin-top: 0;">{archetype['archetype'].replace('_', ' ')}</h3>
        <p><strong>Confidence:</strong> {archetype['confidence']}</p>
        <p><strong>Reason:</strong> {archetype['reason']}</p>
        <p><strong>Recommendation:</strong> <strong>{archetype['recommendation']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layer 3: Additional Metrics
    st.markdown("---")
    st.markdown("### 📈 Layer 3: Additional Metrics (Professional Judgment)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Expected Goals Analysis**")
        
        # Simple xG calculation
        home_xg_avg = home_data.get('home_xg_per_match', 0) if 'home_xg_per_match' in home_data else 0
        away_xg_avg = away_data.get('away_xg_per_match', 0) if 'away_xg_per_match' in away_data else 0
        
        st.metric(f"{home_team} Avg xG (Home)", f"{home_xg_avg:.2f}")
        st.metric(f"{away_team} Avg xG (Away)", f"{away_xg_avg:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Form & Momentum**")
        
        home_form = home_data.get('form_last_5_overall', '')
        away_form = away_data.get('form_last_5_overall', '')
        
        st.metric(f"{home_team} Last 5", home_form)
        st.metric(f"{away_team} Last 5", away_form)
        
        # Form direction
        home_trend = "↗️ Improving" if home_form and home_form[-1] == 'W' else "↘️ Declining" if home_form and home_form[-1] == 'L' else "➡️ Stable"
        away_trend = "↗️ Improving" if away_form and away_form[-1] == 'W' else "↘️ Declining" if away_form and away_form[-1] == 'L' else "➡️ Stable"
        
        st.markdown(f"**Trend:** {home_trend} | {away_trend}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Goal Type Distribution**")
        
        # Calculate goal type percentages for home team
        home_total = max(1, home_data.get('home_goals_scored', 1))
        counter_pct = (home_data.get('home_goals_counter_for', 0) / home_total) * 100
        setpiece_pct = (home_data.get('home_goals_setpiece_for', 0) / home_total) * 100
        
        st.metric("Counter-Attack %", f"{counter_pct:.1f}%")
        st.metric("Set-Piece %", f"{setpiece_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Professional Notes Section
    st.markdown("#### 📝 Professional Notes & Considerations")
    
    notes = []
    
    # Add notes based on analysis
    if home_crisis['severity'] == 'CRITICAL':
        notes.append(f"• **{home_team}** defensive crisis creates high-scoring potential")
    if away_crisis['severity'] == 'CRITICAL':
        notes.append(f"• **{away_team}** defensive crisis favors opponent's attack")
    
    for insight in home_reality:
        if 'OVERPERFORMING' in insight['type']:
            notes.append(f"• **{home_team}** may be due for regression")
        elif 'UNDERPERFORMING' in insight['type']:
            notes.append(f"• **{home_team}** could improve with better finishing")
    
    for story in tactical_stories:
        if 'Counter-Attack' in story['title']:
            notes.append("• Match likely to feature decisive counter-attacks")
        if 'Set-Piece' in story['title']:
            notes.append("• Set-pieces could be decisive")
    
    if archetype['archetype'] == 'AVOID':
        notes.append("• Mixed signals suggest waiting for better opportunities")
        notes.append("• Monitor team news for last-minute changes")
    
    # Display notes
    for note in notes:
        st.markdown(f"- {note}")
    
    # Export/Report Section
    st.markdown("---")
    st.markdown("#### 📤 Export Analysis")
    
    if st.button("📋 Generate Analysis Report"):
        report = f"""
        BRUTBALL PROFESSIONAL ANALYSIS REPORT
        =====================================
        
        Match: {home_team} vs {away_team}
        Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
        
        LAYER 1: SITUATION CLASSIFICATION
        --------------------------------
        {home_team}:
        - Defensive Status: {home_crisis['severity']}
        - Crisis Signals: {', '.join(home_crisis['signals']) if home_crisis['signals'] else 'None'}
        - Reality Check: {[f"{i['type']}: {i['value']}" for i in home_reality]}
        
        {away_team}:
        - Defensive Status: {away_crisis['severity']}
        - Crisis Signals: {', '.join(away_crisis['signals']) if away_crisis['signals'] else 'None'}
        - Reality Check: {[f"{i['type']}: {i['value']}" for i in away_reality]}
        
        Tactical Analysis:
        {[f"{s['title']}: {s['detail']}" for s in tactical_stories]}
        
        LAYER 2: DECISION CLASSIFICATION
        --------------------------------
        Archetype: {archetype['archetype'].replace('_', ' ')}
        Confidence: {archetype['confidence']}
        Reason: {archetype['reason']}
        
        FINAL RECOMMENDATION:
        {archetype['recommendation']}
        
        PROFESSIONAL NOTES:
        {chr(10).join(notes)}
        """
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"brutball_analysis_{home_team}_vs_{away_team}.txt",
            mime="text/plain"
        )

# Data Preview (optional)
with st.expander("📊 View Raw Data"):
    st.dataframe(df)
    
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>Brutball Professional Decision Framework v1.0 • For professional use only</p>
    <p>Remember: All betting involves risk. Never bet more than you can afford to lose.</p>
</div>
""", unsafe_allow_html=True)