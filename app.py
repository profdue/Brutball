import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Multi-Market Betting System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Multi-Market Betting System")
st.markdown("""
**Refined Multi-Market Strategy** - Tier 2 (100% patterns) → Tier 1 (93% accuracy) → Maximum coverage
""")

# ==================== CORE BETTING ENGINE ====================

class MultiMarketBettingSystem:
    def __init__(self, min_matches=5):
        self.min_matches = min_matches
        
    def analyze_match(self, home_stats, away_stats):
        """
        EXACT LOGIC from your refined multi-market strategy:
        
        STEP 1: Apply Tier 2 checks first (100% patterns):
        1. If Home_Conceding > 2.0 → BET: BTTS YES
        2. If Home_Scoring < 1.0 → BET: BTTS NO  
        3. If (Home_Scoring + Away_Conceding) < 2.2 → BET: Under 2.5
        
        STEP 2: If no Tier 2 match, apply Tier 1:
        4. If Home_Scoring > 0.9 AND Away_Conceding > 1.0 → BET: Home Team to Score YES
        
        STEP 3: If no match → NO BET
        """
        
        # Check minimum data
        if (home_stats['home_matches'] < self.min_matches or 
            away_stats['away_matches'] < self.min_matches):
            return {
                'bet': 'NO_BET', 
                'tier': 0,
                'reason': f'Insufficient data (Home: {home_stats["home_matches"]}, Away: {away_stats["away_matches"]} < {self.min_matches})',
                'confidence': 'LOW',
                'accuracy': 'N/A'
            }
        
        # Calculate metrics (per game averages)
        home_scoring = home_stats['home_goals'] / home_stats['home_matches']
        home_conceding = home_stats['home_conceded'] / home_stats['home_matches']
        away_conceding = away_stats['away_conceded'] / away_stats['away_matches']
        
        # ========== STEP 1: TIER 2 CHECKS FIRST (100% patterns) ==========
        
        # 1. Home_Conceding > 2.0 → BET: BTTS YES
        if home_conceding > 2.0:
            return {
                'bet': 'BTTS_YES',
                'tier': 2,
                'confidence': 'VERY_HIGH',
                'reason': f'Tier 2 (100% pattern): Home conceding very high ({home_conceding:.2f} > 2.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding,
                'accuracy': '100%',
                'rule_triggered': 'Tier 2A: Home_Conceding > 2.0'
            }
        
        # 2. Home_Scoring < 1.0 → BET: BTTS NO
        if home_scoring < 1.0:
            return {
                'bet': 'BTTS_NO',
                'tier': 2,
                'confidence': 'VERY_HIGH',
                'reason': f'Tier 2 (100% pattern): Home scoring too low ({home_scoring:.2f} < 1.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding,
                'accuracy': '100%',
                'rule_triggered': 'Tier 2B: Home_Scoring < 1.0'
            }
        
        # 3. If (Home_Scoring + Away_Conceding) < 2.2 → BET: Under 2.5
        combined = home_scoring + away_conceding
        if combined < 2.2:
            return {
                'bet': 'UNDER_2.5',
                'tier': 2,
                'confidence': 'VERY_HIGH',
                'reason': f'Tier 2 (100% pattern): Low combined scoring ({home_scoring:.2f} + {away_conceding:.2f} = {combined:.2f} < 2.2)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding,
                'accuracy': '100%',
                'rule_triggered': 'Tier 2C: Combined < 2.2'
            }
        
        # ========== STEP 2: TIER 1 CHECK (93% accuracy) ==========
        
        # 4. Home_Scoring > 0.9 AND Away_Conceding > 1.0 → BET: Home Team to Score YES
        if home_scoring > 0.9 and away_conceding > 1.0:
            return {
                'bet': 'HOME_TO_SCORE',
                'tier': 1,
                'confidence': 'HIGH',
                'reason': f'Tier 1 (93% accuracy): Home scoring ({home_scoring:.2f} > 0.9) and away conceding ({away_conceding:.2f} > 1.0)',
                'home_scoring': home_scoring,
                'home_conceding': home_conceding,
                'away_conceding': away_conceding,
                'accuracy': '93%',
                'rule_triggered': 'Tier 1: Home_Scoring > 0.9 AND Away_Conceding > 1.0'
            }
        
        # ========== STEP 3: NO BET ==========
        
        return {
            'bet': 'NO_BET',
            'tier': 0,
            'reason': 'No Tier 2 (100%) or Tier 1 (93%) patterns detected',
            'confidence': 'LOW',
            'home_scoring': home_scoring,
            'home_conceding': home_conceding,
            'away_conceding': away_conceding,
            'accuracy': 'N/A',
            'rule_triggered': 'None'
        }
    
    def get_strategy_summary(self):
        """Return strategy summary from your analysis."""
        return {
            'strategy_name': 'Refined Multi-Market Strategy',
            'data_based_on': '20-match analysis',
            'tier_1_description': 'HOME TEAM TO SCORE - YES',
            'tier_1_conditions': 'Home scoring > 0.9 AND Away conceding > 1.0',
            'tier_1_accuracy': '14/15 = 93%',
            'tier_1_coverage': '~15/20 matches (75%)',
            'tier_2A_description': 'BTTS YES when Home conceding > 2.0',
            'tier_2A_accuracy': '3/3 = 100%',
            'tier_2B_description': 'BTTS NO when Home scoring < 1.0',
            'tier_2B_accuracy': '4/4 = 100%',
            'tier_2C_description': 'UNDER 2.5 when Combined < 2.2',
            'tier_2C_accuracy': '3/3 = 100%',
            'tier_2_coverage': '~7/20 matches',
            'overall_coverage': '19/20 matches (95%)',
            'expected_accuracy': '>85% across all bets'
        }

class ProfessionalBankrollManager:
    def __init__(self, initial_bankroll=100):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.bets = []
        self.loss_streak = 0
        self.max_drawdown = 0
        
    def calculate_stake(self, tier):
        """
        Calculate stake based on tier and current bankroll.
        
        Tier 1 (93% accuracy): 1.0% of current bankroll
        Tier 2 (100% accuracy): 1.5% of current bankroll
        """
        if tier == 1:
            stake = self.current_bankroll * 0.01  # 1.0%
        elif tier == 2:
            stake = self.current_bankroll * 0.015  # 1.5%
        else:
            return 0.0
        
        # Apply loss streak protection
        if self.loss_streak >= 3:
            stake *= 0.75  # 25% reduction
        if self.loss_streak >= 5:
            stake *= 0.5   # 50% reduction
            
        return round(stake, 2)
    
    def update_after_bet(self, profit):
        """Update bankroll and track performance."""
        self.current_bankroll = round(self.current_bankroll + profit, 2)
        
        # Update loss streak
        if profit < 0:
            self.loss_streak += 1
            # Update max drawdown
            drawdown = ((self.initial_bankroll - self.current_bankroll) / self.initial_bankroll) * 100
            self.max_drawdown = max(self.max_drawdown, drawdown)
        else:
            self.loss_streak = 0
        
        # Track bet
        self.bets.append({
            'date': datetime.now(),
            'profit': profit,
            'bankroll_after': self.current_bankroll
        })
    
    def should_pause(self):
        """Check if system should pause trading."""
        return self.max_drawdown >= 20
    
    def get_summary(self):
        """Get bankroll summary."""
        total_profit = self.current_bankroll - self.initial_bankroll
        roi = (total_profit / self.initial_bankroll) * 100
        
        return {
            'current_bankroll': self.current_bankroll,
            'total_profit': total_profit,
            'roi': f'{roi:.1f}%',
            'loss_streak': self.loss_streak,
            'max_drawdown': f'{self.max_drawdown:.1f}%',
            'total_bets': len(self.bets),
            'winning_bets': sum(1 for b in self.bets if b['profit'] > 0),
            'should_pause': self.should_pause()
        }

def calculate_expected_value(odds, probability, stake):
    """Calculate expected value of a bet."""
    win_return = (odds - 1) * stake
    loss_amount = stake
    
    ev = (probability * win_return) - ((1 - probability) * loss_amount)
    return round(ev, 3)

def get_estimated_probability(tier, confidence):
    """
    Get estimated probability based on tier and confidence.
    From your 20-match analysis:
    - Tier 2: 100% accuracy
    - Tier 1: 93% accuracy
    """
    if tier == 2:
        return 0.95  # Conservative from 100%
    elif tier == 1:
        return 0.90  # Conservative from 93%
    else:
        return 0.50

def get_odds_range(tier, bet_type):
    """Get recommended odds range for bet type."""
    if tier == 1 and bet_type == 'HOME_TO_SCORE':
        return (1.20, 1.45)
    elif tier == 2:
        if bet_type in ['BTTS_YES', 'BTTS_NO', 'UNDER_2.5']:
            return (1.60, 2.20)
    return (1.50, 2.50)

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("🎯 Multi-Market Strategy")
    
    # Initialize system for summary
    system = MultiMarketBettingSystem()
    summary = system.get_strategy_summary()
    
    st.markdown(f"""
    **{summary['strategy_name']}**
    
    **Based on:** {summary['data_based_on']}
    
    **Expected Coverage:** {summary['overall_coverage']}
    **Expected Accuracy:** {summary['expected_accuracy']}
    """)
    
    st.header("📊 Tier 1: Primary Bet")
    st.markdown(f"""
    **Market:** {summary['tier_1_description']}
    
    **Conditions:**
    {summary['tier_1_conditions']}
    
    **Accuracy:** {summary['tier_1_accuracy']}
    **Coverage:** {summary['tier_1_coverage']}
    """)
    
    st.header("📈 Tier 2: 100% Patterns")
    
    with st.expander("Tier 2A: BTTS YES"):
        st.markdown(f"""
        **When:** Home conceding > 2.0
        **Accuracy:** {summary['tier_2A_accuracy']}
        """)
    
    with st.expander("Tier 2B: BTTS NO"):
        st.markdown(f"""
        **When:** Home scoring < 1.0
        **Accuracy:** {summary['tier_2B_accuracy']}
        """)
    
    with st.expander("Tier 2C: UNDER 2.5"):
        st.markdown(f"""
        **When:** (Home scoring + Away conceding) < 2.2
        **Accuracy:** {summary['tier_2C_accuracy']}
        """)
    
    st.header("💰 Bankroll Management")
    st.markdown("""
    **Tier 1 (93% accuracy):** 1.0% of bankroll
    **Tier 2 (100% accuracy):** 1.5% of bankroll
    
    **Loss Protection:**
    - 3+ losses: 25% stake reduction
    - 5+ losses: 50% stake reduction
    - Max drawdown stop: 20%
    """)

# ==================== MAIN INPUT ====================

st.markdown("---")
st.subheader("📊 Match Analysis Input")

# Match Information
st.markdown("#### 🏆 Match Information")
col_info = st.columns([1, 1])
with col_info[0]:
    league = st.text_input("League", value="Premier League", key="league")
with col_info[1]:
    match_date = st.date_input("Match Date", value=datetime.now())

st.markdown("---")

# Team Statistics - EXACTLY as per your data requirements
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏠 Home Team Statistics")
    st.caption("*Last N HOME games*")
    
    home_name = st.text_input("Home Team", value="Liverpool", key="home_name")
    
    home_matches = st.number_input(
        "Home Games Played", 
        min_value=0, max_value=50, value=10, step=1,
        key="home_matches"
    )
    
    home_goals = st.number_input(
        "Goals Scored (Home)", 
        min_value=0, max_value=200, value=16, step=1,
        key="home_goals"
    )
    
    home_conceded = st.number_input(
        "Goals Conceded (Home)", 
        min_value=0, max_value=200, value=8, step=1,
        key="home_conceded"
    )

with col2:
    st.markdown("#### ✈️ Away Team Statistics")
    st.caption("*Last N AWAY games*")
    
    away_name = st.text_input("Away Team", value="Brighton", key="away_name")
    
    away_matches = st.number_input(
        "Away Games Played", 
        min_value=0, max_value=50, value=10, step=1,
        key="away_matches"
    )
    
    away_conceded = st.number_input(
        "Goals Conceded (Away)", 
        min_value=0, max_value=200, value=14, step=1,
        key="away_conceded"
    )

# Calculate and display averages
if home_matches > 0 and away_matches > 0:
    home_scoring = home_goals / home_matches
    home_conceding = home_conceded / home_matches
    away_conceding = away_conceded / away_matches
    combined = home_scoring + away_conceding
    
    st.markdown("---")
    st.subheader("📈 Calculated Averages")
    
    avg_cols = st.columns(4)
    with avg_cols[0]:
        st.metric(f"{home_name} Scoring (Home)", f"{home_scoring:.2f}")
    with avg_cols[1]:
        st.metric(f"{home_name} Conceding (Home)", f"{home_conceding:.2f}")
    with avg_cols[2]:
        st.metric(f"{away_name} Conceding (Away)", f"{away_conceding:.2f}")
    with avg_cols[3]:
        st.metric("Combined", f"{combined:.2f}")

# ==================== ODDS INPUT ====================

st.markdown("---")
st.subheader("📊 Market Odds")

odds_cols = st.columns(4)

with odds_cols[0]:
    odds_home_score = st.number_input(
        f"{home_name} to Score", 
        min_value=1.01, max_value=10.0, value=1.30, step=0.01,
        key="odds_home_score"
    )

with odds_cols[1]:
    odds_btts_yes = st.number_input(
        "BTTS Yes", 
        min_value=1.01, max_value=10.0, value=1.70, step=0.01,
        key="odds_btts_yes"
    )

with odds_cols[2]:
    odds_btts_no = st.number_input(
        "BTTS No", 
        min_value=1.01, max_value=10.0, value=2.10, step=0.01,
        key="odds_btts_no"
    )

with odds_cols[3]:
    odds_under_25 = st.number_input(
        "Under 2.5 Goals", 
        min_value=1.01, max_value=10.0, value=1.90, step=0.01,
        key="odds_under_25"
    )

# ==================== ANALYSIS ====================

st.markdown("---")
analyze_button = st.button("🚀 Run Multi-Market Analysis", type="primary", use_container_width=True)

if analyze_button:
    # Initialize system and bankroll
    system = MultiMarketBettingSystem(min_matches=5)
    bankroll = ProfessionalBankrollManager()
    
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
    
    # Run analysis with EXACT logic
    analysis = system.analyze_match(home_stats, away_stats)
    
    # ==================== DISPLAY RESULTS ====================
    
    st.header("🎯 Bet Recommendation")
    
    # Display recommendation
    if analysis['bet'] == 'NO_BET':
        col1, col2 = st.columns([3, 1])
        with col1:
            st.error("## ❌ NO BET")
            st.caption(f"**Reason:** {analysis['reason']}")
        with col2:
            st.metric("Decision", "NO BET")
    else:
        # Map bet types to display names
        bet_display = {
            'HOME_TO_SCORE': f"{home_name} to Score",
            'BTTS_YES': 'Both Teams to Score: YES',
            'BTTS_NO': 'Both Teams to Score: NO',
            'UNDER_2.5': 'Under 2.5 Goals'
        }
        
        # Confidence icons
        confidence_icons = {
            'VERY_HIGH': '🔥',
            'HIGH': '✅',
            'MEDIUM': '⚠️',
            'LOW': '🔍'
        }
        
        icon = confidence_icons.get(analysis['confidence'], '📊')
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.success(f"## {icon} {bet_display[analysis['bet']]}")
            st.caption(f"**{analysis['rule_triggered']}**")
            st.caption(f"**Accuracy:** {analysis['accuracy']} • **Confidence:** {analysis['confidence']}")
            st.caption(f"**Reason:** {analysis['reason']}")
        
        with col2:
            tier_color = "🟢" if analysis['tier'] == 1 else "🔵"
            st.metric("Tier", tier_color)
        
        with col3:
            st.metric("Accuracy", analysis['accuracy'])
    
    # ==================== RULES EVALUATION ====================
    
    st.markdown("---")
    st.subheader("📋 Rules Evaluation (EXACT Logic)")
    
    # Display rules in order of evaluation
    rules_data = []
    
    # Tier 2 Rules (evaluated FIRST)
    rules_data.append({
        'Step': '1',
        'Tier': '2',
        'Rule': 'Home_Conceding > 2.0',
        'Condition': f'{home_conceding:.2f} > 2.00',
        'Result': '✅ YES' if home_conceding > 2.0 else '❌ NO',
        'Bet': 'BTTS YES' if home_conceding > 2.0 else '-',
        'Status': 'TRIGGERED' if analysis.get('rule_triggered') == 'Tier 2A: Home_Conceding > 2.0' else 'Not Met'
    })
    
    rules_data.append({
        'Step': '2',
        'Tier': '2',
        'Rule': 'Home_Scoring < 1.0',
        'Condition': f'{home_scoring:.2f} < 1.00',
        'Result': '✅ YES' if home_scoring < 1.0 else '❌ NO',
        'Bet': 'BTTS NO' if home_scoring < 1.0 else '-',
        'Status': 'TRIGGERED' if analysis.get('rule_triggered') == 'Tier 2B: Home_Scoring < 1.0' else 'Not Met'
    })
    
    rules_data.append({
        'Step': '3',
        'Tier': '2',
        'Rule': '(Home_Scoring + Away_Conceding) < 2.2',
        'Condition': f'({home_scoring:.2f} + {away_conceding:.2f}) = {combined:.2f} < 2.20',
        'Result': '✅ YES' if combined < 2.2 else '❌ NO',
        'Bet': 'UNDER 2.5' if combined < 2.2 else '-',
        'Status': 'TRIGGERED' if analysis.get('rule_triggered') == 'Tier 2C: Combined < 2.2' else 'Not Met'
    })
    
    # Tier 1 Rule (evaluated LAST if no Tier 2 match)
    rules_data.append({
        'Step': '4',
        'Tier': '1',
        'Rule': 'Home_Scoring > 0.9 AND Away_Conceding > 1.0',
        'Condition': f'{home_scoring:.2f} > 0.90 AND {away_conceding:.2f} > 1.00',
        'Result': '✅ YES' if (home_scoring > 0.9 and away_conceding > 1.0) else '❌ NO',
        'Bet': 'HOME_TO_SCORE' if (home_scoring > 0.9 and away_conceding > 1.0) else '-',
        'Status': 'TRIGGERED' if analysis.get('rule_triggered') == 'Tier 1: Home_Scoring > 0.9 AND Away_Conceding > 1.0' else 'Not Met'
    })
    
    # Display rules table
    df_rules = pd.DataFrame(rules_data)
    
    # Color triggered row
    def color_triggered(row):
        if row['Status'] == 'TRIGGERED':
            return ['background-color: #d4edda'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df_rules.style.apply(color_triggered, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Step': st.column_config.TextColumn('Step', width='small'),
            'Tier': st.column_config.TextColumn('Tier', width='small'),
            'Rule': st.column_config.TextColumn('Rule'),
            'Condition': st.column_config.TextColumn('Actual Values'),
            'Result': st.column_config.TextColumn('Result'),
            'Bet': st.column_config.TextColumn('Recommended Bet'),
            'Status': st.column_config.TextColumn('Status')
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
        
        # Calculate stake
        stake = bankroll.calculate_stake(analysis['tier'])
        
        # Get estimated probability
        probability = get_estimated_probability(analysis['tier'], analysis['confidence'])
        
        # Calculate expected value
        ev = calculate_expected_value(odds, probability, stake)
        
        # Get odds range
        min_odds, max_odds = get_odds_range(analysis['tier'], analysis['bet'])
        odds_in_range = min_odds <= odds <= max_odds
        
        # Get bankroll summary
        bankroll_summary = bankroll.get_summary()
        
        # Display calculations
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Recommended Stake", f"{stake:.2f} units")
            if bankroll.loss_streak >= 3:
                st.caption(f"⚠️ Loss streak: {bankroll.loss_streak}")
        
        with col2:
            st.metric("Current Bankroll", f"{bankroll_summary['current_bankroll']:.2f}")
        
        with col3:
            odds_status = "✅ In Range" if odds_in_range else "⚠️ Outside Range"
            odds_color = "normal" if odds_in_range else "off"
            st.metric("Current Odds", f"{odds:.2f}", delta=odds_status, delta_color=odds_color)
        
        with col4:
            ev_color = "normal" if ev > 0 else "inverse"
            st.metric("Expected Value", f"{ev:.3f}", delta_color=ev_color)
        
        # ==================== STRATEGY SUMMARY ====================
        
        st.markdown("---")
        st.subheader("📊 Strategy Performance Summary")
        
        # Display strategy metrics
        strategy_summary = system.get_strategy_summary()
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("Tier 1 Accuracy", strategy_summary['tier_1_accuracy'])
        with cols[1]:
            st.metric("Tier 2 Accuracy", "100%")
        with cols[2]:
            st.metric("Overall Coverage", strategy_summary['overall_coverage'])
        
        # ==================== BANKROLL STATUS ====================
        
        st.markdown("---")
        st.subheader("🏦 Bankroll Management Status")
        
        # Create bankroll dashboard
        br1, br2, br3, br4 = st.columns(4)
        
        with br1:
            progress = min(100, max(0, (bankroll.current_bankroll / 100) * 100))
            st.progress(progress/100, text=f"Bankroll: {bankroll.current_bankroll:.2f}")
        
        with br2:
            status = "✅ Active" if not bankroll_summary['should_pause'] else "⛔ PAUSED"
            st.metric("Trading Status", status)
        
        with br3:
            st.metric("Loss Streak", bankroll_summary['loss_streak'])
        
        with br4:
            st.metric("Max Drawdown", bankroll_summary['max_drawdown'])
        
        # ==================== DATA QUALITY ====================
        
        st.markdown("---")
        st.subheader("🔍 Data Quality Check")
        
        quality_cols = st.columns(3)
        
        with quality_cols[0]:
            if home_matches >= 5 and away_matches >= 5:
                st.success("✅ Minimum Data: ≥5 matches each")
            else:
                st.error("❌ Minimum Data: <5 matches")
        
        with quality_cols[1]:
            if analysis['bet'] != 'NO_BET':
                st.success(f"✅ Pattern Detected: {analysis['rule_triggered']}")
            else:
                st.info("ℹ️ No Pattern: Consider different match")
        
        with quality_cols[2]:
            if odds_in_range:
                st.success("✅ Odds Quality: In recommended range")
            else:
                st.warning("⚠️ Odds Quality: Outside recommended range")

# ==================== EXAMPLE FROM YOUR DATA ====================

with st.expander("📋 Examples From Your 20-Match Analysis"):
    st.markdown("""
    **Example 1: Liverpool vs Brighton (Tier 1)**
    - Home_Scoring: 1.63 (>0.9) ✅
    - Away_Conceding: 1.43 (>1.0) ✅
    - **Bet:** Home Team to Score YES ✅ (Liverpool scored 2)
    
    **Example 2: Burnley vs Fulham (Tier 2A)**
    - Home_Conceding: 2.88 (>2.0) ✅
    - **Bet:** BTTS YES ✅ (2-3)
    
    **Example 3: Celta vs Athletic (Tier 2B)**
    - Home_Scoring: 0.88 (<1.0) ✅
    - **Bet:** BTTS NO ✅ (2-0)
    
    **Example 4: Low Scoring Match (Tier 2C)**
    - Home_Scoring: 0.90
    - Away_Conceding: 1.10
    - Combined: 2.00 (<2.2) ✅
    - **Bet:** UNDER 2.5 ✅
    """)

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Refined Multi-Market Betting System</strong></p>
    <p><small>Based on 20-match analysis: Tier 2 (100% patterns) → Tier 1 (93% accuracy)</small></p>
    <p><small>Maximum coverage (95% of matches) with >85% expected accuracy</small></p>
</div>
""", unsafe_allow_html=True)
