"""
CONCRETE BATTLE-TESTED BETTING SYSTEM
Clean, Professional UI/UX Design
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Pro Betting Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for clean, professional styling
st.markdown("""
<style>
    /* Main Layout */
    .main-header {
        font-size: 2.8rem;
        color: #2E4053;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #2C3E50;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #EAEDED;
        font-weight: 600;
    }
    .section-title {
        font-size: 1.2rem;
        color: #3498DB;
        margin: 1.5rem 0 0.8rem 0;
        font-weight: 600;
    }
    
    /* Cards */
    .match-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #F0F3F4;
    }
    .team-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .prediction-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1.2rem;
        border-left: 4px solid;
        transition: transform 0.2s ease;
    }
    .prediction-card:hover {
        transform: translateY(-2px);
    }
    .aligned-card {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    .single-card {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    .calculated-card {
        border-left-color: #3B82F6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }
    
    /* Badges */
    .trend-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .trend-70 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
    }
    .trend-60 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    .trend-low {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
    }
    .probability-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .value-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .high-value {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    .medium-value {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    .low-value {
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%);
        color: white;
    }
    
    /* Metrics */
    .metric-box {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1F2937;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Dividers */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
        margin: 1.5rem 0;
    }
    
    /* Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .data-table th {
        background: #F9FAFB;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #374151;
        border-bottom: 2px solid #E5E7EB;
    }
    .data-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .data-table tr:hover {
        background: #F9FAFB;
    }
    
    /* Odds Display */
    .odds-display {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
    }
    
    /* Status Indicators */
    .status-approved {
        color: #10B981;
        font-weight: 600;
    }
    .status-warning {
        color: #F59E0B;
        font-weight: 600;
    }
    .status-rejected {
        color: #EF4444;
        font-weight: 600;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for form data
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'league': 'Other',
        'match_date': datetime.now(),
        'home_team': 'Roma',
        'home_btts_pct': 30,
        'home_over_pct': 20,
        'home_under_pct': 70,
        'home_gf_avg': 1.0,
        'home_ga_avg': 0.8,
        'away_team': 'Como',
        'away_btts_pct': 40,
        'away_over_pct': 35,
        'away_under_pct': 60,
        'away_gf_avg': 1.3,
        'away_ga_avg': 0.9,
        'is_big_club_home': True,
        'is_big_club_home_after_poor_run': False,
        'is_relegation_desperation': False,
        'is_title_chase': False,
        'btts_yes_odds': 1.80,
        'over_25_odds': 2.20,
        'under_25_odds': 1.58
    }

def save_form_data():
    """Save form data to session state"""
    st.session_state.form_data = {
        'league': st.session_state.league,
        'match_date': st.session_state.match_date,
        'home_team': st.session_state.home_team,
        'home_btts_pct': st.session_state.home_btts_pct,
        'home_over_pct': st.session_state.home_over_pct,
        'home_under_pct': st.session_state.home_under_pct,
        'home_gf_avg': st.session_state.home_gf_avg,
        'home_ga_avg': st.session_state.home_ga_avg,
        'away_team': st.session_state.away_team,
        'away_btts_pct': st.session_state.away_btts_pct,
        'away_over_pct': st.session_state.away_over_pct,
        'away_under_pct': st.session_state.away_under_pct,
        'away_gf_avg': st.session_state.away_gf_avg,
        'away_ga_avg': st.session_state.away_ga_avg,
        'is_big_club_home': st.session_state.get('is_big_club_home', False),
        'is_big_club_home_after_poor_run': st.session_state.get('is_big_club_home_after_poor_run', False),
        'is_relegation_desperation': st.session_state.get('is_relegation_desperation', False),
        'is_title_chase': st.session_state.get('is_title_chase', False),
        'btts_yes_odds': st.session_state.btts_yes_odds,
        'over_25_odds': st.session_state.over_25_odds,
        'under_25_odds': st.session_state.under_25_odds
    }

def create_sidebar():
    """Create clean sidebar for data input"""
    with st.sidebar:
        st.markdown("### 📊 Match Data")
        
        # Match Info
        col1, col2 = st.columns(2)
        with col1:
            league = st.selectbox(
                "League",
                ["Premier League", "Bundesliga", "Serie A", "La Liga", "Ligue 1", "Other"],
                index=5,
                key="league"
            )
        with col2:
            match_date = st.date_input("Date", datetime.now(), key="match_date")
        
        # Home Team
        st.markdown("---")
        st.markdown("#### 🏠 Home Team")
        home_team = st.text_input("Team Name", "Roma", key="home_team")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Trends (Last 10)**")
            home_btts_pct = st.slider("BTTS %", 0, 100, 30, key="home_btts_pct")
            home_over_pct = st.slider("Over 2.5 %", 0, 100, 20, key="home_over_pct")
            home_under_pct = st.slider("Under 2.5 %", 0, 100, 70, key="home_under_pct")
        
        with col2:
            st.markdown("**Averages (per game)**")
            home_gf_avg = st.number_input("Goals Scored", 0.0, 5.0, 1.0, 0.1, key="home_gf_avg")
            home_ga_avg = st.number_input("Goals Conceded", 0.0, 5.0, 0.8, 0.1, key="home_ga_avg")
        
        # Away Team
        st.markdown("---")
        st.markdown("#### ✈️ Away Team")
        away_team = st.text_input("Team Name ", "Como", key="away_team")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Trends (Last 10)**")
            away_btts_pct = st.slider("BTTS % ", 0, 100, 40, key="away_btts_pct")
            away_over_pct = st.slider("Over 2.5 % ", 0, 100, 35, key="away_over_pct")
            away_under_pct = st.slider("Under 2.5 % ", 0, 100, 60, key="away_under_pct")
        
        with col2:
            st.markdown("**Averages (per game)**")
            away_gf_avg = st.number_input("Goals Scored ", 0.0, 5.0, 1.3, 0.1, key="away_gf_avg")
            away_ga_avg = st.number_input("Goals Conceded ", 0.0, 5.0, 0.9, 0.1, key="away_ga_avg")
        
        # Context
        st.markdown("---")
        st.markdown("#### 🎯 Match Context")
        col1, col2 = st.columns(2)
        with col1:
            is_big_club_home = st.checkbox("Big Club at Home", True, key="is_big_club_home")
            is_big_club_home_after_poor_run = st.checkbox("After Poor Run", key="is_big_club_home_after_poor_run")
        with col2:
            is_relegation_desperation = st.checkbox("Relegation Battle", key="is_relegation_desperation")
            is_title_chase = st.checkbox("Title Chase", key="is_title_chase")
        
        # Market Odds
        st.markdown("---")
        st.markdown("#### 💰 Market Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            btts_yes_odds = st.number_input("BTTS Yes", 1.01, 10.0, 1.80, 0.01, key="btts_yes_odds")
        with col2:
            over_25_odds = st.number_input("Over 2.5", 1.01, 10.0, 2.20, 0.01, key="over_25_odds")
        with col3:
            under_25_odds = st.number_input("Under 2.5", 1.01, 10.0, 1.58, 0.01, key="under_25_odds")
        
        st.markdown("---")
        if st.button("🎯 Run Analysis", type="primary", use_container_width=True):
            save_form_data()
            st.rerun()

def get_trend_badge_class(percentage):
    """Get CSS class for trend badge"""
    if percentage >= 70:
        return "trend-70"
    elif percentage >= 60:
        return "trend-60"
    else:
        return "trend-low"

def display_team_analysis():
    """Display team analysis in a clean layout"""
    data = st.session_state.form_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### 🏠 {data['home_team']}")
        
        # Trend badges
        st.markdown("##### Trend Analysis")
        badges_html = f"""
        <div style="margin-bottom: 1rem;">
            <span class="trend-badge {get_trend_badge_class(data['home_btts_pct'])}">BTTS: {data['home_btts_pct']}%</span>
            <span class="trend-badge {get_trend_badge_class(data['home_over_pct'])}">Over: {data['home_over_pct']}%</span>
            <span class="trend-badge {get_trend_badge_class(data['home_under_pct'])}">Under: {data['home_under_pct']}%</span>
        </div>
        """
        st.markdown(badges_html, unsafe_allow_html=True)
        
        # Stats
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Goals Scored", f"{data['home_gf_avg']:.1f}/game")
        with col_b:
            st.metric("Goals Conceded", f"{data['home_ga_avg']:.1f}/game")
        
        # Context
        if data['is_big_club_home']:
            st.info("🏆 Big Club at Home")
        if data['is_big_club_home_after_poor_run']:
            st.warning("📉 After poor run")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="team-card">', unsafe_allow_html=True)
        st.markdown(f"### ✈️ {data['away_team']}")
        
        # Trend badges
        st.markdown("##### Trend Analysis")
        badges_html = f"""
        <div style="margin-bottom: 1rem;">
            <span class="trend-badge {get_trend_badge_class(data['away_btts_pct'])}">BTTS: {data['away_btts_pct']}%</span>
            <span class="trend-badge {get_trend_badge_class(data['away_over_pct'])}">Over: {data['away_over_pct']}%</span>
            <span class="trend-badge {get_trend_badge_class(data['away_under_pct'])}">Under: {data['away_under_pct']}%</span>
        </div>
        """
        st.markdown(badges_html, unsafe_allow_html=True)
        
        # Stats
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Goals Scored", f"{data['away_gf_avg']:.1f}/game")
        with col_b:
            st.metric("Goals Conceded", f"{data['away_ga_avg']:.1f}/game")
        
        # Context
        if data['is_relegation_desperation']:
            st.error("🔥 Relegation battle")
        if data['is_title_chase']:
            st.success("🏆 Title chase")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_expected_goals():
    """Display expected goals calculation"""
    data = st.session_state.form_data
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Expected Goals Analysis")
    
    # Calculate expected goals
    baseline = ((data['home_gf_avg'] + data['away_ga_avg']) + (data['away_gf_avg'] + data['home_ga_avg'])) / 2
    
    # Apply adjustments for single trends
    adjustment = 0
    if data['home_under_pct'] >= 70:
        adjustment -= 0.15
    if data['away_under_pct'] >= 70 and not data['is_big_club_home']:
        adjustment -= 0.15
    
    adjusted = baseline * (1 + adjustment)
    
    # Display formula
    formula = f"[({data['home_gf_avg']:.1f} + {data['away_ga_avg']:.1f}) + ({data['away_gf_avg']:.1f} + {data['home_ga_avg']:.1f})] ÷ 2 = {baseline:.1f}"
    
    if adjustment != 0:
        formula += f" × {1+adjustment:.2f} = {adjusted:.1f}"
    
    st.markdown(f"**Formula:** `{formula}`")
    
    # Visual indicator
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">' + f"{adjusted:.1f}" + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Expected Goals</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="text-align: center; padding-top: 2rem;">→</div>', unsafe_allow_html=True)
    
    with col3:
        if adjusted > 2.5:
            st.markdown('<div class="metric-box" style="border-color: #EF4444;">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value" style="color: #EF4444;">Over 2.5</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Prediction</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-box" style="border-color: #10B981;">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value" style="color: #10B981;">Under 2.5</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Prediction</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations based on expected goals
    probability = 0.75 if abs(adjusted - 2.5) > 0.5 else 0.65
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return adjusted, probability

def display_betting_recommendations(expected_goals, probability):
    """Display betting recommendations"""
    data = st.session_state.form_data
    
    st.markdown("### 🎯 Betting Recommendations")
    
    # Determine which bet to recommend
    if expected_goals > 2.5:
        bet_type = "Over 2.5"
        market_odds = data['over_25_odds']
    else:
        bet_type = "Under 2.5"
        market_odds = data['under_25_odds']
    
    # Calculate value
    value = (probability * market_odds) - 1
    
    # Determine value category
    if value >= 0.25:
        value_class = "high-value"
        value_label = "High Value"
        action = "Strong Bet"
        stake = "2-3%"
    elif value >= 0.15:
        value_class = "high-value"
        value_label = "Good Value"
        action = "Consider"
        stake = "1-2%"
    else:
        value_class = "low-value"
        value_label = "Limited Value"
        action = "Avoid"
        stake = "0%"
    
    # Check for single strong trends
    single_trend = False
    if data['home_under_pct'] >= 70 or data['home_over_pct'] >= 70 or data['home_btts_pct'] >= 70:
        single_trend = True
    if (data['away_under_pct'] >= 70 or data['away_over_pct'] >= 70 or data['away_btts_pct'] >= 70) and not data['is_big_club_home']:
        single_trend = True
    
    # Main recommendation card
    if single_trend:
        card_class = "single-card"
        priority = "Single Trend Detected"
        emoji = "📊"
    else:
        card_class = "calculated-card"
        priority = "Calculated Prediction"
        emoji = "🧮"
    
    st.markdown(f'<div class="prediction-card {card_class}">', unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"##### {emoji} {priority}")
        st.markdown(f"### {bet_type}")
    with col2:
        st.markdown(f'<span class="probability-badge" style="background: {"#10B981" if probability >= 0.7 else "#F59E0B"}; color: white;">{probability:.0%}</span>', unsafe_allow_html=True)
    
    # Value badge
    st.markdown(f'<span class="value-badge {value_class}">Value: {value:+.1%} • {value_label}</span>', unsafe_allow_html=True)
    
    # Details
    st.markdown(f"**Market Odds:** `{market_odds:.2f}`")
    st.markdown(f"**Expected Goals:** `{expected_goals:.1f}`")
    
    # Context notes
    context_notes = []
    if data['home_under_pct'] >= 70 and bet_type == "Under 2.5":
        context_notes.append(f"🏠 {data['home_team']} has {data['home_under_pct']}% Under trend at home")
    if data['away_under_pct'] >= 70 and bet_type == "Under 2.5" and not data['is_big_club_home']:
        context_notes.append(f"✈️ {data['away_team']} has {data['away_under_pct']}% Under trend away")
    if data['is_big_club_home'] and data['away_under_pct'] >= 70:
        context_notes.append(f"⚠️ Discounted {data['away_team']}'s trend (facing big club)")
    
    if context_notes:
        st.markdown("**Context:**")
        for note in context_notes:
            st.markdown(f"- {note}")
    
    # Betting decision
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Decision**")
        st.markdown(f'<div class="status-{"approved" if value >= 0.15 else "rejected"}">{action}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Stake**")
        st.markdown(f"**{stake}**")
    with col3:
        st.markdown("**Value**")
        st.markdown(f"**{value:+.1%}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alternative bets
    if value >= 0.15:
        st.markdown("#### 🔄 Alternative Markets")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            st.markdown("##### Correct Score")
            
            # Suggest likely scores based on expected goals
            if expected_goals < 2.0:
                scores = ["1-0", "0-1", "1-1", "2-0"]
            elif expected_goals < 2.5:
                scores = ["2-0", "1-1", "2-1", "0-2"]
            else:
                scores = ["2-1", "1-2", "2-2", "3-1"]
            
            for score in scores[:3]:
                st.markdown(f"- **{score}**")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="match-card">', unsafe_allow_html=True)
            st.markdown("##### Bet Builder")
            
            suggestions = []
            if expected_goals < 2.5:
                suggestions.append("Under 2.5 Goals")
                suggestions.append("Total Corners Under 10.5")
            else:
                suggestions.append("Over 2.5 Goals")
                suggestions.append("Both Teams to Score")
            
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_market_odds():
    """Display market odds comparison"""
    data = st.session_state.form_data
    
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    st.markdown("### 💰 Market Odds")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### BTTS Yes")
        st.markdown(f'<div class="odds-display">{data["btts_yes_odds"]:.2f}</div>', unsafe_allow_html=True)
        implied_prob = (1 / data['btts_yes_odds']) * 100
        st.markdown(f"*Implied: {implied_prob:.1f}%*")
    
    with col2:
        st.markdown("##### Over 2.5")
        st.markdown(f'<div class="odds-display">{data["over_25_odds"]:.2f}</div>', unsafe_allow_html=True)
        implied_prob = (1 / data['over_25_odds']) * 100
        st.markdown(f"*Implied: {implied_prob:.1f}%*")
    
    with col3:
        st.markdown("##### Under 2.5")
        st.markdown(f'<div class="odds-display">{data["under_25_odds"]:.2f}</div>', unsafe_allow_html=True)
        implied_prob = (1 / data['under_25_odds']) * 100
        st.markdown(f"*Implied: {implied_prob:.1f}%*")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">PRO BETTING ANALYZER</h1>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">Professional Football Betting Analysis System</div>', unsafe_allow_html=True)
    
    # Create sidebar
    create_sidebar()
    
    # Only show analysis if we have form data
    if 'form_data' in st.session_state:
        data = st.session_state.form_data
        
        # Match header
        st.markdown('<div class="match-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"### 🏠 {data['home_team']}")
        with col2:
            st.markdown(f"### vs")
        with col3:
            st.markdown(f"### ✈️ {data['away_team']}")
        st.markdown(f"*{data['league']} • {data['match_date'].strftime('%B %d, %Y')}*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Team Analysis
        display_team_analysis()
        
        # Expected Goals
        expected_goals, probability = display_expected_goals()
        
        # Market Odds
        display_market_odds()
        
        # Betting Recommendations
        display_betting_recommendations(expected_goals, probability)
        
        # System Info (collapsible)
        with st.expander("📋 System Logic Overview", expanded=False):
            st.markdown("""
            #### 🎯 Decision Hierarchy
            
            1. **Aligned Strong Trends (≥70%)**
               - Both teams show same ≥70% trend → BET IMMEDIATELY
            
            2. **Single Dominant Trends (≥70%)**
               - One team shows ≥70% trend → Apply ±15% adjustment
            
            3. **Calculated Expected Goals**
               - Baseline: [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2
            
            4. **Value Calculation**
               - Value = (Probability × Odds) - 1
               - Bet if Value ≥ 15%
            """)
    
    else:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="match-card" style="text-align: center;">', unsafe_allow_html=True)
            st.markdown("### 👋 Welcome to Pro Betting Analyzer")
            st.markdown("Enter match data in the sidebar to begin analysis")
            st.markdown("")
            st.markdown("🎯 **Key Features:**")
            st.markdown("- Trend-based analysis")
            st.markdown("- Expected goals calculation")
            st.markdown("- Value betting identification")
            st.markdown("- Professional recommendations")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
