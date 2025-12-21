import streamlit as st
import pandas as pd
import numpy as np
import warnings
from typing import Dict, Tuple, List
warnings.filterwarnings('ignore')

# =================== PAGE CONFIG ===================
st.set_page_config(
    page_title="Brutball Professional Decision Framework",
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
    </style>
""", unsafe_allow_html=True)

# =================== DATA LOADING ===================
@st.cache_data
def load_league_data():
    """Load and prepare the league data"""
    try:
        # Try loading from different possible paths
        paths_to_try = [
            'leagues/premier_league.csv',
            './leagues/premier_league.csv',
            'premier_league.csv',
            'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
        ]
        
        df = None
        for path in paths_to_try:
            try:
                df = pd.read_csv(path)
                st.success(f"✅ Data loaded successfully from: {path}")
                break
            except Exception as e:
                continue
        
        if df is None:
            st.error("❌ Could not load data from any source")
            return None
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Add derived columns
        if 'home_matches_played' in df.columns and 'home_goals_scored' in df.columns:
            df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, 1)
            df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, 1)
            df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, 1)
            df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, 1)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# =================== QUANTITATIVE ENGINE ===================
class BrutballQuantitativeEngine:
    """Professional Quantitative Decision Engine"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.league_avg_xg = self._calculate_league_averages()
        
    def _calculate_league_averages(self) -> Dict:
        """Calculate league-wide xG averages for context"""
        total_home_xg = self.df['home_xg_for'].sum()
        total_home_matches = self.df['home_matches_played'].sum()
        total_away_xg = self.df['away_xg_for'].sum()
        total_away_matches = self.df['away_matches_played'].sum()
        
        avg_home_xg = total_home_xg / total_home_matches if total_home_matches > 0 else 1.5
        avg_away_xg = total_away_xg / total_away_matches if total_away_matches > 0 else 1.2
        
        return {'home': avg_home_xg, 'away': avg_away_xg}
    
    # ========== PHASE 1: QUANTITATIVE CRISIS SCORING ==========
    def calculate_crisis_score(self, team_data: Dict) -> Dict:
        """Quantitative crisis scoring (0-15 scale)"""
        score = 0
        signals = []
        
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
        
        # Severity Classification
        if score >= 6:
            severity = 'CRITICAL'
        elif score >= 3:
            severity = 'WARNING'
        else:
            severity = 'STABLE'
        
        return {
            'score': score,
            'severity': severity,
            'signals': signals,
            'defenders_out': defenders_out,
            'goals_conceded': goals_conceded,
            'form': form
        }
    
    # ========== PHASE 2: DYNAMIC REALITY CHECK ==========
    def analyze_xg_deviation(self, team_data: Dict, is_home: bool) -> Tuple[str, float]:
        """League-contextual xG analysis"""
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
            games = team_data.get('home_matches_played', 1)
            league_avg = self.league_avg_xg['home']
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
            games = team_data.get('away_matches_played', 1)
            league_avg = self.league_avg_xg['away']
        
        goals_per_game = goals / max(games, 1)
        xg_per_game = xg / max(games, 1)
        
        # Dynamic threshold based on team strength
        base_threshold = 0.3
        if xg_per_game > league_avg * 1.2:
            threshold = base_threshold * 0.8
        elif xg_per_game < league_avg * 0.8:
            threshold = base_threshold * 1.2
        else:
            threshold = base_threshold
        
        deviation = goals_per_game - xg_per_game
        
        if deviation > threshold:
            confidence = min(2.0, 1.0 + (deviation - threshold) / threshold)
            return 'OVERPERFORMING', confidence
        elif deviation < -threshold:
            confidence = min(2.0, 1.0 + abs(deviation - threshold) / threshold)
            return 'UNDERPERFORMING', confidence
        else:
            return 'NEUTRAL', 1.0
    
    # ========== PHASE 3: TACTICAL EDGE SCORING ==========
    def calculate_tactical_edge(self, home_team: Dict, away_team: Dict) -> Dict:
        """Quantifiable tactical advantage (0-10 scale)"""
        edge_score = 0
        edges = []
        
        # 1. Counter-Attack Matchup
        home_counter_for = home_team.get('home_goals_counter_for', 0)
        home_total_goals = max(1, home_team.get('home_goals_scored', 1))
        away_counter_against = away_team.get('away_goals_counter_against', 0)
        away_total_conceded = max(1, away_team.get('away_goals_conceded', 1))
        
        home_counter_pct = home_counter_for / home_total_goals
        away_counter_vuln = away_counter_against / away_total_conceded
        
        if home_counter_pct > 0.15 and away_counter_vuln > 0.15:
            counter_edge = (home_counter_pct * away_counter_vuln) * 20
            edge_score += min(4.0, counter_edge)
            edges.append({
                'type': 'COUNTER_ATTACK',
                'score': min(4.0, counter_edge),
                'detail': f"Home scores {home_counter_pct:.1%} from counters, Away concedes {away_counter_vuln:.1%}"
            })
        
        # 2. Set-Piece Matchup
        home_setpiece_for = home_team.get('home_goals_setpiece_for', 0)
        away_setpiece_against = away_team.get('away_goals_setpiece_against', 0)
        
        home_setpiece_pct = home_setpiece_for / home_total_goals
        away_setpiece_vuln = away_setpiece_against / away_total_conceded
        
        if home_setpiece_pct > 0.2 and away_setpiece_vuln > 0.2:
            setpiece_edge = (home_setpiece_pct * away_setpiece_vuln) * 25
            edge_score += min(4.0, setpiece_edge)
            edges.append({
                'type': 'SET_PIECE',
                'score': min(4.0, setpiece_edge),
                'detail': f"Home scores {home_setpiece_pct:.1%} from set pieces, Away concedes {away_setpiece_vuln:.1%}"
            })
        
        # 3. Attack Competence Check
        home_attack_xg = home_team.get('home_xg_for', 0) / max(1, home_team.get('home_matches_played', 1))
        away_attack_xg = away_team.get('away_xg_for', 0) / max(1, away_team.get('away_matches_played', 1))
        
        competence_score = 0
        if home_attack_xg > 1.0:
            competence_score += 1
        if away_attack_xg > 1.0:
            competence_score += 1
        
        edge_score += competence_score
        both_competent = (home_attack_xg > 0.7 and away_attack_xg > 0.7)
        
        return {
            'score': min(10.0, edge_score),
            'edges': edges,
            'competence_score': competence_score,
            'both_competent': both_competent,
            'home_attack_xg': home_attack_xg,
            'away_attack_xg': away_attack_xg
        }
    
    # ========== PHASE 4: QUANTITATIVE ARCHETYPE ==========
    def determine_archetype(self, home_crisis: Dict, away_crisis: Dict,
                           home_xg: Tuple, away_xg: Tuple,
                           tactical: Dict) -> Dict:
        """Quantitative archetype classification"""
        fade_score = 0
        goals_score = 0
        back_score = 0
        rationale = []
        
        # 1. FADE scoring (one-sided crisis + overperformance)
        if away_crisis['severity'] == 'CRITICAL' and home_crisis['severity'] in ['STABLE', 'WARNING']:
            fade_score = away_crisis['score'] * away_xg[1]
            if away_xg[0] == 'OVERPERFORMING':
                fade_score *= 1.5
            if fade_score > 0:
                rationale.append(f"FADE base: {fade_score:.1f}")
        
        # 2. GOALS GALORE scoring (crisis + attack competence)
        if home_crisis['severity'] == 'CRITICAL' or away_crisis['severity'] == 'CRITICAL':
            crisis_sum = home_crisis['score'] + away_crisis['score']
            goals_score = crisis_sum * (tactical['score'] / 5)
            if not tactical['both_competent']:
                goals_score *= 0.7
                rationale.append("Goals score penalized: weak attack competence")
            if goals_score > 0:
                rationale.append(f"GOALS base: {goals_score:.1f}")
        
        # 3. BACK scoring (underperformance + stability)
        if home_xg[0] == 'UNDERPERFORMING' and home_crisis['severity'] == 'STABLE':
            stability_factor = max(1, 10 - away_crisis['score']) / 10
            back_score = home_xg[1] * stability_factor * 10
            if back_score > 0:
                rationale.append(f"BACK base: {back_score:.1f}")
        
        # Decision with thresholds
        if fade_score > 15 and fade_score > max(goals_score, back_score):
            confidence = min(10.0, fade_score / 3)
            archetype = 'FADE_THE_FAVORITE'
            rationale.append(f"→ FADE selected (score: {fade_score:.1f})")
            
        elif goals_score > 12 and goals_score > max(fade_score, back_score):
            confidence = min(10.0, goals_score / 3)
            archetype = 'GOALS_GALORE'
            rationale.append(f"→ GOALS selected (score: {goals_score:.1f})")
            
        elif back_score > 10:
            confidence = min(8.0, back_score / 3)
            archetype = 'BACK_THE_UNDERDOG'
            rationale.append(f"→ BACK selected (score: {back_score:.1f})")
            
        else:
            archetype = 'AVOID'
            confidence = 0
            rationale.append("→ No quantitative edge above thresholds")
        
        return {
            'archetype': archetype,
            'confidence': round(confidence, 1),
            'scores': {
                'fade': round(fade_score, 1),
                'goals': round(goals_score, 1),
                'back': round(back_score, 1)
            },
            'rationale': rationale
        }
    
    # ========== PHASE 5: PRECISION STAKING ==========
    def calculate_stake_size(self, archetype: str, confidence: float) -> float:
        """Capital allocation based on confidence"""
        if archetype == 'AVOID' or confidence < 4:
            return 0.0
        
        base_stakes = {
            'FADE_THE_FAVORITE': {8: 2.5, 6: 2.0, 4: 1.0},
            'GOALS_GALORE': {8: 2.0, 6: 1.5, 4: 0.5},
            'BACK_THE_UNDERDOG': {8: 1.5, 6: 1.0, 4: 0.5}
        }
        
        thresholds = base_stakes.get(archetype, {})
        for threshold, stake in sorted(thresholds.items(), reverse=True):
            if confidence >= threshold:
                return stake
        
        return 0.0
    
    # ========== COMPLETE ANALYSIS ==========
    def analyze_match(self, home_team_name: str, away_team_name: str) -> Dict:
        """Complete quantitative analysis pipeline"""
        # Get team data
        home_data = self.df[self.df['team'] == home_team_name].iloc[0].to_dict()
        away_data = self.df[self.df['team'] == away_team_name].iloc[0].to_dict()
        
        # Phase 1: Crisis Scoring
        home_crisis = self.calculate_crisis_score(home_data)
        away_crisis = self.calculate_crisis_score(away_data)
        
        # Phase 2: xG Reality Check
        home_xg = self.analyze_xg_deviation(home_data, is_home=True)
        away_xg = self.analyze_xg_deviation(away_data, is_home=False)
        
        # Phase 3: Tactical Edge
        tactical = self.calculate_tactical_edge(home_data, away_data)
        
        # Phase 4: Archetype Classification
        archetype_result = self.determine_archetype(
            home_crisis, away_crisis, home_xg, away_xg, tactical
        )
        
        # Phase 5: Capital Allocation
        stake_pct = self.calculate_stake_size(
            archetype_result['archetype'],
            archetype_result['confidence']
        )
        
        return {
            'match': f"{home_team_name} vs {away_team_name}",
            'crisis_analysis': {'home': home_crisis, 'away': away_crisis},
            'reality_check': {
                'home': {'type': home_xg[0], 'confidence': home_xg[1]},
                'away': {'type': away_xg[0], 'confidence': away_xg[1]}
            },
            'tactical_edge': tactical,
            'archetype': archetype_result['archetype'],
            'confidence': archetype_result['confidence'],
            'quantitative_scores': archetype_result['scores'],
            'rationale': archetype_result['rationale'],
            'recommended_stake': stake_pct,
            'home_attack_xg': home_data.get('home_xg_for', 0) / max(1, home_data.get('home_matches_played', 1)),
            'away_attack_xg': away_data.get('away_xg_for', 0) / max(1, away_data.get('away_matches_played', 1)),
            'home_form': home_data.get('form_last_5_overall', ''),
            'away_form': away_data.get('form_last_5_overall', '')
        }

# =================== UI FUNCTIONS ===================
def render_header():
    """Render the main header"""
    st.markdown('<div class="main-header">⚽ Brutball Professional Decision Framework</div>', unsafe_allow_html=True)

def render_framework_status():
    """Render the three-layer framework status"""
    st.markdown("### 🏗️ Three-Layer Decision Framework")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 1: Situation Classification**")
        st.markdown("✅ Ready")
        st.markdown("Quantitative Crisis + Reality + Tactical")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 2: Decision Firewall**")
        st.markdown("✅ Ready")
        st.markdown("Market Validation & Conservative Gates")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="layer-box">', unsafe_allow_html=True)
        st.markdown("**Layer 3: Capital Allocation**")
        st.markdown("✅ Automated")
        st.markdown("Precision Staking & Bankroll Management")
        st.markdown('</div>', unsafe_allow_html=True)

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
        analysis = engine.analyze_match(home_team, away_team)
        display_quantitative_results(analysis)
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        if st.button("📋 Generate Analysis Report"):
            report = create_report(analysis)
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"brutball_{home_team}_vs_{away_team}.txt",
                mime="text/plain"
            )

def display_quantitative_results(analysis):
    """Display quantitative analysis results"""
    st.markdown("---")
    st.markdown("### 🔍 Layer 1: Quantitative Situation Analysis")
    
    # Crisis Analysis
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {analysis['match'].split(' vs ')[0]}")
        home_crisis = analysis['crisis_analysis']['home']
        if home_crisis['severity'] != 'STABLE':
            st.markdown(f'<div class="crisis-alert">', unsafe_allow_html=True)
            st.markdown(f"**{home_crisis['severity']} ALERT** - Score: {home_crisis['score']}/15")
            for signal in home_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"✅ **STABLE** - Score: {home_crisis['score']}/15")
    
    with col2:
        st.markdown(f"#### {analysis['match'].split(' vs ')[1]}")
        away_crisis = analysis['crisis_analysis']['away']
        if away_crisis['severity'] != 'STABLE':
            st.markdown(f'<div class="crisis-alert">', unsafe_allow_html=True)
            st.markdown(f"**{away_crisis['severity']} ALERT** - Score: {away_crisis['score']}/15")
            for signal in away_crisis['signals']:
                st.markdown(f"- {signal}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"✅ **STABLE** - Score: {away_crisis['score']}/15")
    
    # Reality Check
    st.markdown("#### 📊 Reality Check (xG Analysis)")
    col1, col2 = st.columns(2)
    with col1:
        home_xg = analysis['reality_check']['home']
        st.markdown(f"**Home:** {home_xg['type']}")
        st.markdown(f"Confidence: {home_xg['confidence']:.1f}")
    with col2:
        away_xg = analysis['reality_check']['away']
        st.markdown(f"**Away:** {away_xg['type']}")
        st.markdown(f"Confidence: {away_xg['confidence']:.1f}")
    
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
    if not tactical['both_competent']:
        st.warning(f"⚠️ Attack Competence Warning: Home xG={analysis['home_attack_xg']:.2f}, Away xG={analysis['away_attack_xg']:.2f}")
    
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
        <p><strong>Quantitative Scores:</strong> Fade={analysis['quantitative_scores']['fade']:.1f}, 
           Goals={analysis['quantitative_scores']['goals']:.1f}, 
           Back={analysis['quantitative_scores']['back']:.1f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Decision Rationale
    st.markdown("#### 🧠 Decision Rationale")
    for line in analysis['rationale']:
        st.markdown(f"- {line}")
    
    # Layer 3: Capital Allocation
    st.markdown("---")
    st.markdown("### 💰 Layer 3: Professional Capital Allocation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Recommended Stake**")
        st.markdown(f"# {analysis['recommended_stake']}%")
        st.markdown("of bankroll")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Expected Goals**")
        st.metric("Home Attack xG", f"{analysis['home_attack_xg']:.2f}")
        st.metric("Away Attack xG", f"{analysis['away_attack_xg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Form & Momentum**")
        st.metric("Home Form", analysis['home_form'])
        st.metric("Away Form", analysis['away_form'])
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
        notes.append("**Avoid:** Betting on the favorite outright")
    
    elif archetype == 'GOALS_GALORE':
        notes.append("**Primary Bet:** Over 2.5 Goals")
        if analysis['tactical_edge']['both_competent']:
            notes.append("**Secondary:** Both Teams to Score (Yes)")
        else:
            notes.append("**Caution:** BTTS less likely with weak attack")
    
    elif archetype == 'BACK_THE_UNDERDOG':
        notes.append("**Primary Bet:** Underdog to win or double chance")
        notes.append("**Consider:** Smaller stake due to medium confidence")
        notes.append("**Risk:** Favorite may still dominate possession")
    
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
BRUTBALL PROFESSIONAL ANALYSIS REPORT
=====================================

Match: {analysis['match']}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

LAYER 1: QUANTITATIVE SITUATION ANALYSIS
---------------------------------------
Home Team ({analysis['match'].split(' vs ')[0]}):
- Crisis Score: {analysis['crisis_analysis']['home']['score']}/15
- Severity: {analysis['crisis_analysis']['home']['severity']}
- xG Analysis: {analysis['reality_check']['home']['type']} (Confidence: {analysis['reality_check']['home']['confidence']:.1f})
- Attack xG: {analysis['home_attack_xg']:.2f}/game
- Form: {analysis['home_form']}

Away Team ({analysis['match'].split(' vs ')[1]}):
- Crisis Score: {analysis['crisis_analysis']['away']['score']}/15
- Severity: {analysis['crisis_analysis']['away']['severity']}
- xG Analysis: {analysis['reality_check']['away']['type']} (Confidence: {analysis['reality_check']['away']['confidence']:.1f})
- Attack xG: {analysis['away_attack_xg']:.2f}/game
- Form: {analysis['away_form']}

Tactical Edge Score: {analysis['tactical_edge']['score']:.1f}/10
Attack Competent: {analysis['tactical_edge']['both_competent']}

LAYER 2: DECISION CLASSIFICATION
--------------------------------
Archetype: {analysis['archetype'].replace('_', ' ')}
Confidence Score: {analysis['confidence']}/10

Quantitative Scores:
- Fade Score: {analysis['quantitative_scores']['fade']:.1f}
- Goals Score: {analysis['quantitative_scores']['goals']:.1f}
- Back Score: {analysis['quantitative_scores']['back']:.1f}

Decision Rationale:
{chr(10).join(analysis['rationale'])}

LAYER 3: CAPITAL ALLOCATION
--------------------------
Recommended Stake: {analysis['recommended_stake']}% of bankroll

PROFESSIONAL RECOMMENDATION:
{generate_professional_notes(analysis)}

=====================================
Brutball Professional Framework v2.0
Quantitative Decision System
    """
    return report

def render_data_preview(df):
    """Render data preview expander"""
    with st.expander("📊 View Raw Data"):
        st.dataframe(df)

def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>Brutball Professional Decision Framework v2.0 • Quantitative System</p>
        <p>For professional use only. All betting involves risk.</p>
    </div>
    """, unsafe_allow_html=True)

# =================== MAIN APP ===================
def main():
    """Main application function"""
    
    # Render header
    render_header()
    
    # Load data
    df = load_league_data()
    if df is None:
        st.error("Failed to load data. Please check your data file.")
        return
    
    # Initialize engine
    engine = BrutballQuantitativeEngine(df)
    
    # Render framework status
    render_framework_status()
    
    # Render match analysis
    render_match_analysis(engine, df)
    
    # Render data preview
    render_data_preview(df)
    
    # Render footer
    render_footer()

# =================== RUN APP ===================
if __name__ == "__main__":
    main()