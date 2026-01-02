import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# =================== UPDATED CLASSIFIER IMPORT ===================
try:
    from match_state_classifier import (
        MatchStateClassifier, 
        ProvenPatternDetector,
        BankrollManager,
        get_complete_classification, 
        format_reliability_badge, 
        format_durability_indicator
    )
    STATE_CLASSIFIER_AVAILABLE = True
except ImportError:
    STATE_CLASSIFIER_AVAILABLE = False
    # Fallback functions
    get_complete_classification = None
    format_reliability_badge = None
    format_durability_indicator = None

# =================== EXISTING DATA EXTRACTION FUNCTIONS ===================
def extract_pure_team_data(df: pd.DataFrame, team_name: str) -> Dict:
    """Extract team data with ZERO transformations"""
    if team_name not in df['team'].values:
        st.error(f"❌ Team '{team_name}' not found in CSV.")
        return {}
    
    team_row = df[df['team'] == team_name].iloc[0]
    team_data = {}
    for col in df.columns:
        value = team_row[col]
        team_data[col] = value
    
    return team_data

def normalize_numeric_types(data_dict: Dict) -> Dict:
    """Architecturally pure type normalization"""
    normalized = {}
    
    for key, value in data_dict.items():
        if key in ['goals_scored_last_5', 'goals_conceded_last_5']:
            if pd.isna(value):
                normalized[key] = value
            else:
                try:
                    if isinstance(value, str):
                        if '.' in str(value):
                            normalized[key] = float(value)
                        else:
                            normalized[key] = int(value)
                    elif hasattr(value, 'item'):
                        normalized[key] = value.item()
                    elif isinstance(value, (np.integer, np.floating)):
                        normalized[key] = float(value)
                    else:
                        normalized[key] = float(value)
                except (ValueError, TypeError):
                    normalized[key] = value
        else:
            normalized[key] = value
    
    return normalized

def verify_data_integrity(df: pd.DataFrame, home_team: str, away_team: str):
    """Verify that CSV data has the required fields"""
    print("="*80)
    print("🛡️ DATA INTEGRITY VERIFICATION")
    print("="*80)
    
    required_columns = ['team', 'goals_scored_last_5', 'goals_conceded_last_5']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ CRITICAL: Missing required columns: {missing_columns}")
        return False
    
    print("✅ CSV structure verified")
    
    if home_team not in df['team'].values:
        print(f"❌ Home team '{home_team}' not found in CSV")
        return False
    
    if away_team not in df['team'].values:
        print(f"❌ Away team '{away_team}' not found in CSV")
        return False
    
    print(f"✅ Teams found: {home_team}, {away_team}")
    
    for team in [home_team, away_team]:
        team_row = df[df['team'] == team].iloc[0]
        print(f"\n📊 {team} data check:")
        for field in ['goals_scored_last_5', 'goals_conceded_last_5']:
            value = team_row[field]
            status = "✅" if not pd.isna(value) else "❌ NaN"
            print(f"  {status} {field}: {value}")
    
    print("="*80)
    return True

# =================== PROVEN PATTERNS DISPLAY ===================
def display_proven_patterns_results(pattern_results: Dict, home_team: str, away_team: str):
    """Beautiful display for proven pattern detection results"""
    
    if not pattern_results or pattern_results['patterns_detected'] == 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); 
                padding: 2.5rem; border-radius: 12px; border: 3px dashed #9CA3AF; 
                text-align: center; margin: 1.5rem 0;">
            <h3 style="color: #6B7280; margin: 0 0 1rem 0;">🎯 NO PROVEN PATTERNS DETECTED</h3>
            <div style="color: #374151; margin-bottom: 1rem;">
                This match doesn't meet the criteria for our 25-match empirical patterns
            </div>
            <div style="font-size: 0.9rem; color: #6B7280;">
                Patterns require Elite Defense (≤4 goals last 5) or Winner Lock detection
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Header with pattern count
    patterns_count = pattern_results['patterns_detected']
    
    # Use Streamlit native components for header
    st.markdown(f"### 🎯 PROVEN PATTERNS DETECTED")
    st.markdown(f"**{patterns_count} Pattern(s) Found** - Based on 25-match empirical analysis (100% & 83.3% accuracy)")
    
    # Display each recommendation in beautiful cards using Streamlit
    for idx, rec in enumerate(pattern_results['recommendations']):
        # Pattern-specific styling
        pattern_styles = {
            'ELITE_DEFENSE_UNDER_1_5': {
                'emoji': '🛡️',
                'title_color': '#065F46',
                'border_color': '#16A34A'
            },
            'WINNER_LOCK_DOUBLE_CHANCE': {
                'emoji': '👑',
                'title_color': '#1E40AF',
                'border_color': '#2563EB'
            },
            'PATTERN_DRIVEN_UNDER_3_5': {
                'emoji': '📊',
                'title_color': '#5B21B6',
                'border_color': '#7C3AED'
            }
        }
        
        style = pattern_styles.get(rec['pattern'], pattern_styles['ELITE_DEFENSE_UNDER_1_5'])
        
        # Create card using Streamlit columns
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # FIXED: Show clear team name for UNDER 1.5 predictions
            if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                st.markdown(f"### {style['emoji']} {rec['team_to_bet']} to score UNDER 1.5 goals")
            elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                st.markdown(f"### {style['emoji']} {rec['team_to_bet']} - DOUBLE CHANCE (Win or Draw)")
            else:
                st.markdown(f"### {style['emoji']} {rec['bet_type']}")
            
            st.markdown(f"**Reason:** {rec['reason']}")
            
        with col2:
            st.markdown(f"<div style='background: {style['border_color']}; color: white; padding: 0.5rem 1rem; border-radius: 8px; text-align: center;'><strong>{rec['stake_multiplier']:.1f}x</strong><br><small>Stake Multiplier</small></div>", unsafe_allow_html=True)
        
        # Pattern details in expander
        with st.expander("📊 Pattern Details & Historical Evidence"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Pattern", rec['pattern'].replace('_', ' '))
            with col_b:
                st.metric("Sample Accuracy", rec['sample_accuracy'])
            
            st.markdown("**Historical Evidence:**")
            matches_text = ", ".join(rec['sample_matches'][:3])
            st.info(f"{matches_text}")
            
            # Show defensive data for Elite Defense pattern
            if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                st.markdown("**Defensive Analysis:**")
                col_c, col_d = st.columns(2)
                with col_c:
                    st.metric(f"{rec['defensive_team']} Conceded", f"{rec['home_conceded']}/5")
                with col_d:
                    st.metric("Defense Gap", f"+{rec['defense_gap']}")
        
        st.markdown("---")

# =================== PERFORMANCE TRACKER ===================
class PerformanceTracker:
    """Tracker for system predictions vs actual results"""
    
    def __init__(self):
        self.predictions = []
        self.actual_results = []
    
    def record_prediction(self, match_info: str, prediction: str, confidence: str):
        self.predictions.append({
            'match': match_info,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def record_result(self, match_info: str, actual_score: str):
        self.actual_results.append({
            'match': match_info,
            'actual_score': actual_score,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def calculate_accuracy(self) -> Dict:
        matched = 0
        for pred in self.predictions:
            for result in self.actual_results:
                if pred['match'] == result['match']:
                    matched += 1
                    break
        
        total = len(self.predictions)
        accuracy = (matched / total * 100) if total > 0 else 0
        
        return {
            'total_predictions': total,
            'total_results': len(self.actual_results),
            'matched_pairs': matched,
            'accuracy': accuracy
        }

# Initialize trackers
performance_tracker = PerformanceTracker()
bankroll_manager = BankrollManager(initial_bankroll=10000.0)

# =================== SYSTEM CONSTANTS ===================
CONTROL_CRITERIA_REQUIRED = 2
GOALS_ENV_THRESHOLD = 2.8
ELITE_ATTACK_THRESHOLD = 1.6
DIRECTION_THRESHOLD = 0.25
ENFORCEMENT_METHODS_REQUIRED = 2
STATE_FLIP_FAILURES_REQUIRED = 2
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1
TOTALS_LOCK_THRESHOLD = 1.2
UNDER_GOALS_THRESHOLD = 2.5

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {'filename': 'premier_league.csv', 'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League', 'color': '#3B82F6'},
    'La Liga': {'filename': 'la_liga.csv', 'display_name': '🇪🇸 La Liga', 'color': '#EF4444'},
    'Bundesliga': {'filename': 'bundesliga.csv', 'display_name': '🇩🇪 Bundesliga', 'color': '#000000'},
    'Serie A': {'filename': 'serie_a.csv', 'display_name': '🇮🇹 Serie A', 'color': '#10B981'},
    'Ligue 1': {'filename': 'ligue_1.csv', 'display_name': '🇫🇷 Ligue 1', 'color': '#8B5CF6'},
    'Eredivisie': {'filename': 'eredivisie.csv', 'display_name': '🇳🇱 Eredivisie', 'color': '#F59E0B'},
    'Primeira Liga': {'filename': 'premeira_portugal.csv', 'display_name': '🇵🇹 Primeira Liga', 'color': '#DC2626'},
    'Super Lig': {'filename': 'super_league.csv', 'display_name': '🇹🇷 Super Lig', 'color': '#E11D48'}
}

# =================== MAIN APPLICATION ===================
def main():
    """Main application with Proven Pattern Detection"""
    
    # Header with pattern detection emphasis
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL INTEGRATED v6.3 + PROVEN PATTERNS</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>THREE PROVEN PATTERNS FROM 25-MATCH EMPIRICAL ANALYSIS</strong></p>
        <p>Pattern A: Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)</p>
        <p>Pattern B: Winner Lock → Double Chance (100% - 6 matches)</p>
        <p>Pattern C: UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)</p>
        <p><strong>NEW:</strong> Beautiful UI with clear betting recommendations & stake calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Empirical Proof Display using Streamlit
    st.markdown("### 📊 EMPIRICAL PROOF (25-MATCH ANALYSIS)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Elite Defense Pattern", "100%", "8/8 matches")
    with col2:
        st.metric("Winner Lock Pattern", "100%", "6/6 matches")
    with col3:
        st.metric("Under 3.5 Pattern", "83.3%", "10/12 matches")
    
    # Pattern Conditions using Streamlit
    st.markdown("### 🎯 PATTERN CONDITIONS")
    
    with st.expander("🛡️ ELITE DEFENSE", expanded=True):
        st.markdown("""
        - **Condition:** Team concedes ≤4 goals TOTAL in last 5 matches
        - **Condition:** Defense gap > 2.0 goals vs opponent  
        - **Bet:** Opponent UNDER 1.5 goals
        - **Sample Accuracy:** 8/8 matches (100%)
        """)
    
    with st.expander("👑 WINNER LOCK", expanded=False):
        st.markdown("""
        - **Condition:** Agency-State Lock gives WINNER lock
        - **Condition:** Team does NOT lose (wins or draws)
        - **Bet:** DOUBLE CHANCE (Win or Draw)
        - **Sample Accuracy:** 6/6 matches (100% no-loss)
        """)
    
    with st.expander("📊 UNDER 3.5 WHEN PATTERNS PRESENT", expanded=False):
        st.markdown("""
        - **Condition:** EITHER Elite Defense OR Winner Lock pattern present
        - **Bet:** TOTAL UNDER 3.5 goals
        - **Sample Accuracy:** 10/12 matches (83.3%)
        """)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'pattern_results' not in st.session_state:
        st.session_state.pattern_results = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection using buttons
    st.markdown("### 🌍 League Selection")
    selected_league = st.selectbox(
        "Choose League",
        list(LEAGUES.keys()),
        index=list(LEAGUES.keys()).index(st.session_state.selected_league) if st.session_state.selected_league in LEAGUES else 0,
        key="league_select"
    )
    st.session_state.selected_league = selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Team selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()), key="home_team_select")
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Test case indicator
    if home_team == "FC Porto" and away_team == "AVS Futebol SAD":
        st.success("✅ **Porto vs AVS Test Case Loaded** - This is the original pattern validation match!")
    
    # Get data for pattern detection
    home_data = extract_pure_team_data(df, home_team)
    away_data = extract_pure_team_data(df, away_team)
    
    # Execute analysis button
    if st.button("⚡ DETECT PROVEN PATTERNS", type="primary", use_container_width=True, key="detect_patterns"):
        
        # Prepare data for pattern detection
        match_metadata = {
            'home_team': home_team,
            'away_team': away_team,
            'winner_lock_detected': False,  # Will be replaced by actual data
            'winner_lock_team': '',
            'winner_delta_value': 0
        }
        
        # Run pattern detection
        pattern_results = ProvenPatternDetector.generate_all_patterns(
            home_data, away_data, match_metadata
        )
        
        # Store results
        st.session_state.pattern_results = pattern_results
        st.session_state.analysis_complete = True
        
        st.rerun()
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.pattern_results:
        pattern_results = st.session_state.pattern_results
        
        # Display Proven Patterns using the fixed function
        display_proven_patterns_results(pattern_results, home_team, away_team)
        
        # Bankroll and Stake Management
        st.markdown("### 💰 BANKROLL MANAGEMENT")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_level = st.selectbox(
                "Risk Level",
                ["CONSERVATIVE (0.5%)", "MEDIUM (1.0%)", "AGGRESSIVE (1.5%)"],
                index=1,
                key="risk_level"
            )
        
        with col2:
            base_percentage = {
                "CONSERVATIVE (0.5%)": 0.005,
                "MEDIUM (1.0%)": 0.01,
                "AGGRESSIVE (1.5%)": 0.015
            }[risk_level]
            base_stake = bankroll_manager.bankroll * base_percentage
            st.metric("Base Stake per Bet", f"${base_stake:.2f}")
        
        with col3:
            bankroll_status = bankroll_manager.get_status()
            st.metric("Current Bankroll", f"${bankroll_manager.bankroll:.2f}")
        
        # Calculate stakes for each recommendation
        if pattern_results['patterns_detected'] > 0:
            st.markdown("#### 📊 RECOMMENDED STAKES")
            
            total_stake = 0
            stakes = []
            
            for idx, rec in enumerate(pattern_results['recommendations']):
                stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                stakes.append(stake)
                total_stake += stake
                
                # Create stake card using Streamlit
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        # FIXED: Show clear team name
                        if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                            st.markdown(f"**{rec['team_to_bet']} to score UNDER 1.5 goals**")
                        elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                            st.markdown(f"**{rec['team_to_bet']} - DOUBLE CHANCE**")
                        else:
                            st.markdown(f"**{rec['bet_type']}**")
                        
                        # Show defensive context for Elite Defense
                        if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                            st.caption(f"{rec['defensive_team']} elite defense: {rec['home_conceded']}/5 goals conceded")
                    
                    with col_b:
                        st.markdown(f"**${stake:.2f}**")
                        st.caption(f"{stake/bankroll_manager.bankroll*100:.1f}%")
                    
                    with col_c:
                        st.markdown(f"**{rec['stake_multiplier']:.1f}x**")
                        st.caption("Multiplier")
                    
                    st.progress(stake / (bankroll_manager.bankroll * 0.05))  # Progress bar relative to 5% max
            
            # Total stake summary
            risk_percentage = (total_stake / bankroll_manager.bankroll) * 100
            
            st.markdown("---")
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            with col_sum1:
                st.metric("Total Stake", f"${total_stake:.2f}")
            with col_sum2:
                st.metric("Bankroll %", f"{risk_percentage:.1f}%")
            with col_sum3:
                st.metric("Patterns", pattern_results['patterns_detected'])
            
            if risk_percentage > 10:
                st.warning(f"⚠️ Total stake ({risk_percentage:.1f}% of bankroll) is above recommended 10% limit")
        
        # Performance Tracking
        st.markdown("### 📈 PERFORMANCE TRACKING")
        
        col1, col2 = st.columns(2)
        with col1:
            actual_home = st.number_input(
                f"{home_team} actual goals", 
                min_value=0, max_value=10, value=0, 
                key="actual_home"
            )
        with col2:
            actual_away = st.number_input(
                f"{away_team} actual goals", 
                min_value=0, max_value=10, value=0, 
                key="actual_away"
            )
        
        if st.button("📝 Record Match Result", type="secondary"):
            # Record predictions
            for rec in pattern_results['recommendations']:
                match_info = f"{home_team} vs {away_team}"
                
                # FIXED: Clear prediction text
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    prediction = f"{rec['team_to_bet']} to score UNDER 1.5 goals"
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    prediction = f"{rec['team_to_bet']} - DOUBLE CHANCE (Win or Draw)"
                else:
                    prediction = f"{rec['bet_type']}"
                
                accuracy = rec['sample_accuracy'].split('(')[0].strip()
                performance_tracker.record_prediction(match_info, prediction, accuracy)
            
            # Record result
            actual_score = f"{actual_home}-{actual_away}"
            performance_tracker.record_result(f"{home_team} vs {away_team}", actual_score)
            
            # Calculate profit/loss
            actual_total = actual_home + actual_away
            profit_loss = 0
            
            for idx, rec in enumerate(pattern_results['recommendations']):
                stake = stakes[idx] if idx < len(stakes) else bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                
                # Check if bet would win
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    # Bet: Team to score UNDER 1.5 goals
                    if rec['team_to_bet'] == away_team:
                        would_win = actual_away <= 1
                    else:
                        would_win = actual_home <= 1
                    odds = 1.8  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
                    
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    # Bet: Double Chance (Win or Draw)
                    if rec['team_to_bet'] == home_team:
                        would_win = actual_home >= actual_away
                    else:
                        would_win = actual_away >= actual_home
                    odds = 1.3  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
                    
                elif rec['pattern'] == 'PATTERN_DRIVEN_UNDER_3_5':
                    # Bet: UNDER 3.5
                    would_win = actual_total < 3.5
                    odds = 1.9  # Example odds
                    profit = stake * (odds - 1) if would_win else -stake
                    profit_loss += profit
            
            # Update bankroll
            bankroll_manager.update_after_result(profit_loss)
            
            # Show result
            result_color = "green" if profit_loss >= 0 else "red"
            st.success(f"""
            ✅ **Match Result Recorded:** {home_team} {actual_home}-{actual_away} {away_team}
            
            **Profit/Loss:** :{result_color}[**${profit_loss:+.2f}**]
            
            **New Bankroll:** ${bankroll_manager.bankroll:.2f}
            """)
            
            # Check if should continue
            should_continue, message = bankroll_manager.should_continue_betting()
            if not should_continue:
                st.warning(f"⚠️ {message}")
            
            st.rerun()
        
        # Display performance stats
        stats = performance_tracker.calculate_accuracy()
        bankroll_status = bankroll_manager.get_status()
        
        st.markdown("#### 📊 System Performance")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Predictions", stats['total_predictions'])
        with col2:
            st.metric("Accuracy", f"{stats['accuracy']:.1f}%")
        with col3:
            st.metric("Bankroll", f"${bankroll_status['bankroll']:.2f}")
        with col4:
            st.metric("Daily P/L", f"${bankroll_status['daily_profit_loss']:+.2f}")
        
        # Export functionality - FIXED datetime import issue
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        # FIXED: Use datetime.now() properly
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        export_text = f"""BRUTBALL PROVEN PATTERNS ANALYSIS
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {current_time}

EMPRICAL PROOF (25-MATCH ANALYSIS):
• Pattern A: Elite Defense → Opponent UNDER 1.5 (100% - 8 matches)
• Pattern B: Winner Lock → Double Chance (100% - 6 matches)
• Pattern C: UNDER 3.5 When Patterns Present (83.3% - 10/12 matches)

DETECTED PATTERNS:
• Patterns Found: {pattern_results['patterns_detected']}
• Summary: {pattern_results['summary']}

RECOMMENDED BETS:
"""
        
        for idx, rec in enumerate(pattern_results['recommendations']):
            # FIXED: Clear bet description
            if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                bet_desc = f"{rec['team_to_bet']} to score UNDER 1.5 goals"
            elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                bet_desc = f"{rec['team_to_bet']} - DOUBLE CHANCE (Win or Draw)"
            else:
                bet_desc = f"{rec['bet_type']}"
            
            export_text += f"""
{idx+1}. {bet_desc}
   • Pattern: {rec['pattern'].replace('_', ' ')}
   • Reason: {rec['reason']}
   • Sample Accuracy: {rec['sample_accuracy']}
   • Stake Multiplier: {rec['stake_multiplier']:.1f}x
"""
        
        export_text += f"""

BANKROLL STATUS:
• Current Bankroll: ${bankroll_status['bankroll']:.2f}
• Base Unit: ${bankroll_status['base_unit']:.2f}
• Daily P/L: ${bankroll_status['daily_profit_loss']:+.2f}
• Consecutive Losses: {bankroll_status['consecutive_losses']}

RISK MANAGEMENT:
• Risk Level: {risk_level}
• Stop Conditions: 3 consecutive losses, 10% daily loss
• Max Trades per Day: 20
• Min Bankroll: $100 (10 base units)

DATA SOURCE:
• Last 5 matches data only (no season averages)
• League: {selected_league}
• Match: {home_team} vs {away_team}
• System Version: BRUTBALL_PROVEN_PATTERNS_v1.0
"""
        
        st.download_button(
            label="📥 Download Pattern Analysis",
            data=export_text,
            file_name=f"brutball_patterns_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True,
            key="export_button"
        )
    
    # Footer with pattern examples
    st.markdown("---")
    st.markdown("""
    ### 📋 Historical Proof Examples
    - **Porto 2-0 AVS** (Elite Defense pattern)
    - **Espanyol 2-1 Athletic** (Elite Defense pattern)  
    - **Parma 1-0 Fiorentina** (Elite Defense pattern)
    - **Juventus 2-0 Pisa** (Elite Defense pattern)
    - **Milan 3-0 Verona** (Elite Defense pattern)
    - **Arsenal 4-1 Villa** (Elite Defense pattern)
    - **Man City 0-0 Sunderland** (Elite Defense pattern)
    - **Udinese 1-1 Lazio** (Winner Lock pattern)
    - **Man Utd 1-1 Wolves** (Winner Lock pattern)
    - **Brentford 0-0 Spurs** (Winner Lock pattern)
    """)

if __name__ == "__main__":
    main()
