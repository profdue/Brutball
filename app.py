import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Consistent Betting System - Professional Model",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Consistent Betting System - Professional Model")
st.markdown("""
**Professional Betting Engine** - Based on venue-specific scoring/conceding patterns with priority rules and bankroll management.
""")

# ==================== CORE ENGINE ====================

class ConsistentBettingSystem:
    def __init__(self, min_matches=5):
        self.min_matches = min_matches
        
    def analyze_match(self, home_stats, away_stats):
        """
        Analyze match using the consistent betting system logic.
        
        Args:
            home_stats: dict with 'home_goals', 'home_conceded', 'home_matches'
            away_stats: dict with 'away_conceded', 'away_matches'
            
        Returns:
            dict with bet recommendation
        """
        
        # Check minimum data
        if (home_stats['home_matches'] < self.min_matches or 
            away_stats['away_matches'] < self.min_matches):
            return {
                'bet': 'NO_BET', 
                'tier': 0,
                'reason': 'Insufficient data',
                'confidence': 'LOW'
            }
        
        # Calculate metrics (per game averages)
        home_scoring = home_stats['home_goals'] / home_stats['home_matches']
        home_conceding = home_stats['home_conceded'] / home_stats['home_matches']
        away_conceding = away_stats['away_conceded'] / away_stats['away_matches']
        
        # Priority Rules (in order)
        # 1. If Home_Scoring < 1.0 → BET: BTTS NO
        if home_scoring < 1.0:
            return {
                'bet': 'BTTS_NO',
                'tier': 2,
                'confidence': 'HIGH',
                'reason': f'Home scoring too low ({home_scoring:.2f} < 1.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding
            }
        
        # 2. If Home_Conceding > 2.0 → BET: BTTS YES
        if home_conceding > 2.0:
            return {
                'bet': 'BTTS_YES',
                'tier': 2,
                'confidence': 'HIGH',
                'reason': f'Home conceding too high ({home_conceding:.2f} > 2.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding
            }
        
        # 3. If (Home_Scoring + Away_Conceding) < 2.2 → BET: Under 2.5
        if (home_scoring + away_conceding) < 2.2:
            return {
                'bet': 'UNDER_2.5',
                'tier': 2,
                'confidence': 'HIGH',
                'reason': f'Low combined scoring ({home_scoring:.2f} + {away_conceding:.2f} = {home_scoring + away_conceding:.2f} < 2.2)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding
            }
        
        # 4. If Home_Scoring > 0.9 AND Away_Conceding > 1.0 → BET: Home Team to Score YES
        if home_scoring > 0.9 and away_conceding > 1.0:
            return {
                'bet': 'HOME_TO_SCORE',
                'tier': 1,
                'confidence': 'HIGH',
                'reason': f'Home scoring ({home_scoring:.2f} > 0.9) and away conceding ({away_conceding:.2f} > 1.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding
            }
        
        # No clear pattern
        return {
            'bet': 'NO_BET',
            'tier': 0,
            'reason': 'No clear pattern matches priority rules',
            'confidence': 'LOW',
            'home_scoring': home_scoring,
            'home_conceding': home_conceding,
            'away_conceding': away_conceding
        }
    
    def calculate_stake(self, bankroll, tier):
        """
        Calculate stake based on bankroll and tier.
        
        Args:
            bankroll: current bankroll in units
            tier: 1 or 2
            
        Returns:
            stake in units
        """
        if tier == 1:
            return 1.0  # 1% of 100 unit bankroll
        elif tier == 2:
            return 1.5  # 1.5% of 100 unit bankroll
        return 0.0
    
    def calculate_odds_range(self, tier, bet_type):
        """
        Get recommended odds range for bet type.
        
        Returns:
            tuple (min_odds, max_odds)
        """
        if tier == 1 and bet_type == 'HOME_TO_SCORE':
            return (1.20, 1.45)
        elif tier == 2:
            if bet_type in ['BTTS_YES', 'BTTS_NO', 'UNDER_2.5']:
                return (1.60, 2.20)
        return (1.50, 2.50)  # Default range
    
    def get_bankroll_structure(self):
        """Return bankroll management structure."""
        return {
            'initial_bankroll': 100,
            'risk_per_bet_tier1': '1.0% (1 unit)',
            'risk_per_bet_tier2': '1.5% (1.5 units)',
            'max_drawdown_stop': '20%',
            'weekly_loss_limit': '5 units',
            'monthly_review': 'Accuracy < 85%'
        }

def calculate_expected_value(odds, probability, stake):
    """
    Calculate expected value of a bet.
    
    Args:
        odds: decimal odds
        probability: win probability (0-1)
        stake: bet amount
        
    Returns:
        expected value
    """
    win_return = (odds - 1) * stake
    loss_amount = stake
    
    ev = (probability * win_return) - ((1 - probability) * loss_amount)
    return ev

def get_probability_estimate(bet_type, home_scoring, home_conceding, away_conceding):
    """
    Estimate probability based on metrics.
    
    Returns:
        probability (0-1)
    """
    if bet_type == 'HOME_TO_SCORE':
        # Based on home scoring > 0.9 and away conceding > 1.0
        base_prob = 0.90  # Conservative from 93%
        adjustment = min(0.05, (home_scoring - 0.9) * 0.1 + (away_conceding - 1.0) * 0.1)
        return min(0.95, base_prob + adjustment)
    
    elif bet_type == 'BTTS_NO':
        # Home scoring < 1.0
        base_prob = 0.95  # Conservative from 100%
        adjustment = min(0.03, (1.0 - home_scoring) * 0.2)
        return min(0.98, base_prob + adjustment)
    
    elif bet_type == 'BTTS_YES':
        # Home conceding > 2.0
        base_prob = 0.95
        adjustment = min(0.03, (home_conceding - 2.0) * 0.1)
        return min(0.98, base_prob + adjustment)
    
    elif bet_type == 'UNDER_2.5':
        # Home scoring + away conceding < 2.2
        base_prob = 0.95
        total = home_scoring + away_conceding
        adjustment = min(0.03, (2.2 - total) * 0.2)
        return min(0.98, base_prob + adjustment)
    
    return 0.5  # Default

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("🎯 System Rules")
    st.markdown("""
    **Priority Order:**
    1. Home Scoring < 1.0 → **BTTS NO**
    2. Home Conceding > 2.0 → **BTTS YES**  
    3. Home Scoring + Away Conceding < 2.2 → **Under 2.5**
    4. Home Scoring > 0.9 AND Away Conceding > 1.0 → **Home to Score**
    
    **Minimum Data:** 5 home/away matches
    """)
    
    st.header("💰 Bankroll Management")
    
    system = ConsistentBettingSystem()
    bankroll_info = system.get_bankroll_structure()
    
    for key, value in bankroll_info.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.header("📊 League Priority")
    st.markdown("""
    **Strong Home Bias:**
    - Premier League, Bundesliga
    - Serie A, La Liga
    - Brasileirão, Süper Lig
    
    **Avoid:**
    - Youth/U23 leagues
    - Friendlies
    - Extreme defensive leagues
    """)
    
    st.header("⚙️ How to Use")
    st.markdown("""
    1. Enter team statistics
    2. Input actual odds
    3. View bet recommendation
    4. Check expected value
    5. Track results
    """)

# ==================== MAIN INPUT ====================

st.markdown("---")
st.subheader("📊 Team Statistics Input")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🏠 Home Team")
    home_name = st.text_input("Team Name", value="Liverpool", key="home_name")
    
    st.markdown("##### Last N Home Games")
    home_matches = st.number_input(
        "Matches Played (Home)", 
        min_value=0, max_value=50, value=10, step=1,
        key="home_matches",
        help="Number of home matches in sample"
    )
    
    home_goals = st.number_input(
        "Total Goals Scored", 
        min_value=0, max_value=200, value=21, step=1,
        key="home_goals",
        help="Total goals scored in home matches"
    )
    
    home_conceded = st.number_input(
        "Total Goals Conceded", 
        min_value=0, max_value=200, value=8, step=1,
        key="home_conceded",
        help="Total goals conceded in home matches"
    )

with col2:
    st.markdown("#### ✈️ Away Team")
    away_name = st.text_input("Team Name", value="Manchester City", key="away_name")
    
    st.markdown("##### Last N Away Games")
    away_matches = st.number_input(
        "Matches Played (Away)", 
        min_value=0, max_value=50, value=10, step=1,
        key="away_matches",
        help="Number of away matches in sample"
    )
    
    away_conceded = st.number_input(
        "Total Goals Conceded", 
        min_value=0, max_value=200, value=10, step=1,
        key="away_conceded",
        help="Total goals conceded in away matches"
    )

with col3:
    st.markdown("#### 📈 Market Odds")
    
    odds_home_score = st.number_input(
        f"{home_name} to Score Odds", 
        min_value=1.01, max_value=10.0, value=1.25, step=0.01,
        key="odds_home_score",
        help="Decimal odds for Home Team to Score"
    )
    
    odds_btts_yes = st.number_input(
        "BTTS Yes Odds", 
        min_value=1.01, max_value=10.0, value=1.70, step=0.01,
        key="odds_btts_yes",
        help="Decimal odds for Both Teams to Score"
    )
    
    odds_btts_no = st.number_input(
        "BTTS No Odds", 
        min_value=1.01, max_value=10.0, value=2.10, step=0.01,
        key="odds_btts_no"
    )
    
    odds_under_25 = st.number_input(
        "Under 2.5 Goals Odds", 
        min_value=1.01, max_value=10.0, value=1.90, step=0.01,
        key="odds_under_25"
    )

# ==================== ANALYSIS ====================

st.markdown("---")
analyze_button = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

if analyze_button:
    # Prepare statistics
    home_stats = {
        'home_goals': home_goals,
        'home_conceded': home_conceded,
        'home_matches': home_matches
    }
    
    away_stats = {
        'away_conceded': away_conceded,
        'away_matches': away_matches
    }
    
    # Run analysis
    system = ConsistentBettingSystem(min_matches=5)
    analysis = system.analyze_match(home_stats, away_stats)
    
    # Calculate metrics
    home_scoring = home_goals / home_matches if home_matches > 0 else 0
    home_conceding = home_conceded / home_matches if home_matches > 0 else 0
    away_conceding = away_conceded / away_matches if away_matches > 0 else 0
    
    # ==================== DISPLAY RESULTS ====================
    
    st.header("🎯 Bet Recommendation")
    
    # Recommendation Card
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if analysis['bet'] == 'NO_BET':
            st.error("## ❌ NO BET")
            st.caption(f"Reason: {analysis['reason']}")
        else:
            bet_display = {
                'HOME_TO_SCORE': f"{home_name} to Score",
                'BTTS_YES': 'BTTS: YES',
                'BTTS_NO': 'BTTS: NO',
                'UNDER_2.5': 'Under 2.5 Goals'
            }
            
            tier_color = "🟢" if analysis['tier'] == 1 else "🔵"
            st.success(f"## {tier_color} BET: {bet_display[analysis['bet']]}")
            st.caption(f"Tier {analysis['tier']} • {analysis['confidence']} Confidence")
    
    with col2:
        st.metric("Home Scoring Avg", f"{home_scoring:.2f}")
    
    with col3:
        st.metric("Away Conceding Avg", f"{away_conceding:.2f}")
    
    # ==================== DETAILED ANALYSIS ====================
    
    st.markdown("---")
    st.subheader("📊 Detailed Analysis")
    
    # Metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Home Scoring", 
            f"{home_scoring:.2f}",
            delta="GOOD" if home_scoring > 0.9 else "LOW",
            delta_color="normal" if home_scoring > 0.9 else "off"
        )
    
    with col2:
        st.metric(
            "Home Conceding", 
            f"{home_conceding:.2f}",
            delta="HIGH" if home_conceding > 2.0 else "OK",
            delta_color="off" if home_conceding > 2.0 else "normal"
        )
    
    with col3:
        st.metric(
            "Away Conceding", 
            f"{away_conceding:.2f}",
            delta="HIGH" if away_conceding > 1.0 else "LOW",
            delta_color="normal" if away_conceding > 1.0 else "off"
        )
    
    with col4:
        combined = home_scoring + away_conceding
        st.metric(
            "Combined Score/Concede", 
            f"{combined:.2f}",
            delta="LOW" if combined < 2.2 else "HIGH",
            delta_color="normal" if combined < 2.2 else "off"
        )
    
    # Rules Evaluation
    st.markdown("#### 📋 Rules Evaluation")
    
    rules_data = []
    
    # Rule 1: Home Scoring < 1.0
    rule1_met = home_scoring < 1.0
    rules_data.append({
        'Rule': 'Home Scoring < 1.0',
        'Value': home_scoring,
        'Threshold': 1.0,
        'Met': rule1_met,
        'Bet': 'BTTS NO' if rule1_met else '-'
    })
    
    # Rule 2: Home Conceding > 2.0
    rule2_met = home_conceding > 2.0
    rules_data.append({
        'Rule': 'Home Conceding > 2.0',
        'Value': home_conceding,
        'Threshold': 2.0,
        'Met': rule2_met,
        'Bet': 'BTTS YES' if rule2_met else '-'
    })
    
    # Rule 3: Home Scoring + Away Conceding < 2.2
    rule3_met = (home_scoring + away_conceding) < 2.2
    rules_data.append({
        'Rule': 'Home Score + Away Concede < 2.2',
        'Value': home_scoring + away_conceding,
        'Threshold': 2.2,
        'Met': rule3_met,
        'Bet': 'Under 2.5' if rule3_met else '-'
    })
    
    # Rule 4: Home Scoring > 0.9 AND Away Conceding > 1.0
    rule4_met = home_scoring > 0.9 and away_conceding > 1.0
    rules_data.append({
        'Rule': 'Home Score > 0.9 AND Away Concede > 1.0',
        'Value': f'{home_scoring:.2f} & {away_conceding:.2f}',
        'Threshold': '0.9 & 1.0',
        'Met': rule4_met,
        'Bet': 'Home to Score' if rule4_met else '-'
    })
    
    # Display rules table
    df_rules = pd.DataFrame(rules_data)
    st.dataframe(
        df_rules,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Rule': st.column_config.TextColumn('Rule'),
            'Value': st.column_config.TextColumn('Actual Value'),
            'Threshold': st.column_config.TextColumn('Threshold'),
            'Met': st.column_config.CheckboxColumn('Met', default=False),
            'Bet': st.column_config.TextColumn('Recommended Bet')
        }
    )
    
    # ==================== BETTING CALCULATIONS ====================
    
    if analysis['bet'] != 'NO_BET':
        st.markdown("---")
        st.subheader("💰 Betting Calculations")
        
        # Get odds for the recommended bet
        odds_map = {
            'HOME_TO_SCORE': odds_home_score,
            'BTTS_YES': odds_btts_yes,
            'BTTS_NO': odds_btts_no,
            'UNDER_2.5': odds_under_25
        }
        
        odds = odds_map.get(analysis['bet'], 0)
        
        # Calculate probability
        probability = get_probability_estimate(
            analysis['bet'], 
            home_scoring, 
            home_conceding, 
            away_conceding
        )
        
        # Calculate stake
        bankroll = 100
        stake = system.calculate_stake(bankroll, analysis['tier'])
        
        # Calculate expected value
        ev = calculate_expected_value(odds, probability, stake)
        
        # Calculate recommended odds range
        min_odds, max_odds = system.calculate_odds_range(analysis['tier'], analysis['bet'])
        odds_in_range = min_odds <= odds <= max_odds
        
        # Display betting info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Recommended Stake", f"{stake:.1f} units")
        
        with col2:
            st.metric("Probability", f"{probability*100:.1f}%")
        
        with col3:
            odds_status = "✅ Good" if odds_in_range else "⚠️ Check"
            st.metric("Current Odds", f"{odds:.2f}", delta=odds_status)
        
        with col4:
            ev_color = "normal" if ev > 0 else "inverse"
            st.metric("Expected Value", f"{ev:.3f}", delta_color=ev_color)
        
        # Odds Range Check
        st.markdown("#### 📊 Odds Quality Check")
        
        if odds_in_range:
            st.success(f"✅ Odds {odds:.2f} are within recommended range ({min_odds:.2f} - {max_odds:.2f})")
        else:
            if odds < min_odds:
                st.warning(f"⚠️ Odds {odds:.2f} are BELOW recommended minimum {min_odds:.2f}")
            else:
                st.warning(f"⚠️ Odds {odds:.2f} are ABOVE recommended maximum {max_odds:.2f}")
            
            st.info("Consider waiting for better odds or checking other bookmakers")
        
        # Value Chart
        st.markdown("#### 📈 Value Visualization")
        
        # Create value comparison
        fig = go.Figure()
        
        # Fair odds line (based on probability)
        fair_odds = 1 / probability
        
        # Add traces
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=odds,
            title={'text': "Current Odds"},
            delta={'reference': fair_odds, 'relative': False},
            gauge={
                'axis': {'range': [min_odds - 0.2, max_odds + 0.2]},
                'bar': {'color': "green" if odds_in_range else "orange"},
                'steps': [
                    {'range': [min_odds, max_odds], 'color': "lightgreen"},
                    {'range': [min_odds - 0.2, min_odds], 'color': "lightcoral"},
                    {'range': [max_odds, max_odds + 0.2], 'color': "lightcoral"}
                ]
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== DATA SUFFICIENCY ====================
    
    st.markdown("---")
    st.subheader("📊 Data Quality")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📝 Sample Size Check")
        
        home_ok = home_matches >= 5
        away_ok = away_matches >= 5
        
        if home_ok:
            st.success(f"✅ Home matches: {home_matches} (≥ 5 minimum)")
        else:
            st.error(f"❌ Home matches: {home_matches} (< 5 minimum)")
        
        if away_ok:
            st.success(f"✅ Away matches: {away_matches} (≥ 5 minimum)")
        else:
            st.error(f"❌ Away matches: {away_matches} (< 5 minimum)")
        
        if home_ok and away_ok:
            st.success("✅ Data sufficient for analysis")
        else:
            st.error("⚠️ Insufficient data - consider more matches")
    
    with col2:
        st.markdown("##### 🎯 Confidence Factors")
        
        confidence_factors = []
        
        if home_matches >= 10:
            confidence_factors.append("Large home sample size")
        
        if away_matches >= 10:
            confidence_factors.append("Large away sample size")
        
        if abs(home_scoring - 1.0) > 0.3:
            confidence_factors.append("Clear home scoring pattern")
        
        if abs(home_conceding - 2.0) > 0.5:
            confidence_factors.append("Clear home conceding pattern")
        
        if abs(away_conceding - 1.0) > 0.3:
            confidence_factors.append("Clear away conceding pattern")
        
        if confidence_factors:
            st.success("**Positive Factors:**")
            for factor in confidence_factors[:3]:
                st.markdown(f"• {factor}")
        else:
            st.info("No strong confidence factors identified")
    
    # ==================== SYSTEM PERFORMANCE ====================
    
    st.markdown("---")
    st.subheader("📈 System Performance Estimates")
    
    # Stress test results
    stress_test_data = {
        'Metric': ['Tier 1 Accuracy', 'Tier 2 Accuracy', 'Overall ROI', 'Win Rate'],
        'Value': ['90%', '95%', '+26.1%', '90.9%'],
        'Description': [
            'Conservative estimate (from 93%)',
            'Conservative estimate (from 100%)',
            'Based on 100-match stress test',
            'Combined win rate across tiers'
        ]
    }
    
    df_performance = pd.DataFrame(stress_test_data)
    
    # Display performance metrics
    cols = st.columns(4)
    for idx, row in df_performance.iterrows():
        with cols[idx]:
            if 'Accuracy' in row['Metric'] or 'Rate' in row['Metric']:
                delta_color = "normal"
            elif 'ROI' in row['Metric']:
                delta_color = "normal" if '+' in row['Value'] else "inverse"
            else:
                delta_color = "off"
            
            st.metric(
                row['Metric'],
                row['Value'],
                delta=row['Description'],
                delta_color=delta_color
            )
    
    # ==================== TRACKING TEMPLATE ====================
    
    with st.expander("📋 Tracking Template"):
        st.markdown("""
        Copy this format for manual tracking:
        
        | Date | League | Home | Away | H_Score | A_Concede | Bet | Tier | Odds | Result | Profit |
        |------|--------|------|------|---------|-----------|-----|------|------|--------|--------|
        | | | | | | | | | | | |
        
        **Bankroll Management:**
        - Initial: 100 units
        - Tier 1: 1.0 unit
        - Tier 2: 1.5 units
        - Stop if -20% drawdown
        """)

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Consistent Betting System</strong> - Professional Football Betting Model</p>
    <p><small>Based on venue-specific patterns with priority rules and bankroll management</small></p>
    <p><small>Minimum 5 matches required • Follow rules in order • Manage bankroll strictly</small></p>
</div>
""", unsafe_allow_html=True)

# ==================== SAMPLE DATA ====================

with st.expander("📋 Load Sample Scenarios"):
    sample_scenarios = {
        "Scenario 1: Strong Home Scoring": {
            "home_goals": 15, "home_conceded": 8, "home_matches": 10,
            "away_conceded": 12, "away_matches": 10,
            "description": "Home scoring > 0.9 & Away conceding > 1.0 → Home to Score"
        },
        "Scenario 2: Low Home Scoring": {
            "home_goals": 7, "home_conceded": 10, "home_matches": 10,
            "away_conceded": 8, "away_matches": 10,
            "description": "Home scoring < 1.0 → BTTS NO"
        },
        "Scenario 3: High Home Conceding": {
            "home_goals": 12, "home_conceded": 25, "home_matches": 10,
            "away_conceded": 9, "away_matches": 10,
            "description": "Home conceding > 2.0 → BTTS YES"
        },
        "Scenario 4: Low Combined": {
            "home_goals": 9, "home_conceded": 7, "home_matches": 10,
            "away_conceded": 10, "away_matches": 10,
            "description": "Home scoring + Away conceding < 2.2 → Under 2.5"
        }
    }
    
    selected_scenario = st.selectbox("Choose a sample scenario:", list(sample_scenarios.keys()))
    
    if st.button("Load Scenario Data"):
        scenario = sample_scenarios[selected_scenario]
        st.session_state.home_goals = scenario["home_goals"]
        st.session_state.home_conceded = scenario["home_conceded"]
        st.session_state.home_matches = scenario["home_matches"]
        st.session_state.away_conceded = scenario["away_conceded"]
        st.session_state.away_matches = scenario["away_matches"]
        
        st.info(f"**Scenario:** {scenario['description']}")
        st.rerun()
