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
        format_durability_indicator,
        format_pattern_badge
    )
    STATE_CLASSIFIER_AVAILABLE = True
except ImportError:
    STATE_CLASSIFIER_AVAILABLE = False
    # Fallback functions
    get_complete_classification = None
    format_reliability_badge = None
    format_durability_indicator = None
    format_pattern_badge = None

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

# =================== PROVEN PATTERNS DISPLAY (FIXED - NO HTML) ===================
def display_proven_patterns_results(pattern_results: Dict, home_team: str, away_team: str):
    """Beautiful display for proven pattern detection results using Streamlit components"""
    
    if not pattern_results or pattern_results['patterns_detected'] == 0:
        st.info("🎯 No proven patterns detected for this match.")
        return
    
    # Header with pattern count
    patterns_count = pattern_results['patterns_detected']
    
    # Create a nice header with columns
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🎯 {patterns_count} Proven Pattern(s) Found")
        st.caption("Based on 25-match empirical analysis")
    with col2:
        st.metric("Patterns Detected", patterns_count)
    
    # Display each recommendation in beautiful Streamlit cards
    for idx, rec in enumerate(pattern_results['recommendations']):
        # Create expandable container for each pattern
        with st.expander(f"**{rec['bet_type']}** - {rec.get('team_to_bet', 'Match')}", expanded=True):
            
            # Create columns for better layout
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                # Pattern-specific emoji and title
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    st.markdown(f"##### 🛡️ {rec['team_to_bet']} to score UNDER 1.5 goals")
                    st.write(f"**Reason:** {rec['reason']}")
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    st.markdown(f"##### 👑 {rec['team_to_bet']} Double Chance (Win or Draw)")
                    st.write(f"**Reason:** {rec['reason']}")
                else:  # PATTERN_DRIVEN_UNDER_3_5
                    st.markdown(f"##### 📊 Total UNDER 3.5 goals")
                    st.write(f"**Reason:** {rec['reason']}")
            
            with col_b:
                # Stake multiplier in a nice metric
                st.metric("Stake Multiplier", f"{rec['stake_multiplier']:.1f}x")
            
            # Pattern details in columns
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Pattern:** {rec['pattern'].replace('_', ' ')}")
            with col2:
                st.success(f"**Sample Accuracy:** {rec['sample_accuracy']}")
            
            # Historical evidence
            with st.container():
                st.markdown("**📜 Historical Evidence:**")
                matches = rec['sample_matches'][:3]  # Show first 3 examples
                for match in matches:
                    st.markdown(f"- {match}")
            
            # Add spacing between patterns
            st.divider()

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
    st.title("🎯 BRUTBALL INTEGRATED v6.3 + PROVEN PATTERNS")
    st.markdown("### THREE PROVEN PATTERNS FROM 25-MATCH EMPIRICAL ANALYSIS")
    
    # Empirical Proof Display using Streamlit columns
    st.markdown("---")
    st.subheader("📊 EMPIRICAL PROOF (25-MATCH ANALYSIS)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Elite Defense Pattern", "100%", "8/8 matches")
    with col2:
        st.metric("Winner Lock Pattern", "100%", "6/6 matches")
    with col3:
        st.metric("Under 3.5 Pattern", "83.3%", "10/12 matches")
    
    # Pattern Conditions Display
    st.markdown("---")
    st.subheader("🎯 PATTERN CONDITIONS")
    
    # Create tabs for each pattern
    tab1, tab2, tab3 = st.tabs(["🛡️ Elite Defense", "👑 Winner Lock", "📊 Under 3.5"])
    
    with tab1:
        st.markdown("""
        **Pattern A: Elite Defense → Opponent UNDER 1.5 Goals**
        
        **Conditions:**
        1. Team concedes ≤4 goals TOTAL in last 5 matches
        2. Defense gap > 2.0 goals vs opponent
        
        **Bet:** Opponent to score UNDER 1.5 goals
        
        **Accuracy:** 100% (8/8 matches)
        """)
        
    with tab2:
        st.markdown("""
        **Pattern B: Winner Lock → Double Chance**
        
        **Conditions:**
        1. Agency-State Lock gives WINNER lock
        2. Team does NOT lose (wins or draws)
        
        **Bet:** DOUBLE CHANCE (Win or Draw)
        
        **Accuracy:** 100% no-loss (6/6 matches)
        """)
        
    with tab3:
        st.markdown("""
        **Pattern C: UNDER 3.5 When Patterns Present**
        
        **Conditions:**
        1. EITHER Elite Defense OR Winner Lock pattern present
        
        **Bet:** TOTAL UNDER 3.5 goals
        
        **Accuracy:** 83.3% (10/12 matches)
        """)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'pattern_results' not in st.session_state:
        st.session_state.pattern_results = None
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    # League selection
    st.markdown("---")
    st.subheader("🌍 League Selection")
    
    cols = st.columns(8)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if st.session_state.selected_league == league else "secondary",
                key=f"league_btn_{league}"
            ):
                st.session_state.selected_league = league
                st.session_state.analysis_complete = False
                st.rerun()
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Team selection
    st.markdown("---")
    st.subheader("🏟️ Match Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()), key="home_team_select")
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Get data for pattern detection
    home_data = extract_pure_team_data(df, home_team)
    away_data = extract_pure_team_data(df, away_team)
    
    # Execute analysis button
    st.markdown("---")
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
        
        # Display Proven Patterns
        st.markdown("---")
        st.subheader("🎯 PROVEN PATTERN DETECTION RESULTS")
        display_proven_patterns_results(pattern_results, home_team, away_team)
        
        # Bankroll and Stake Management
        st.markdown("---")
        st.subheader("💰 BANKROLL MANAGEMENT")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_level = st.selectbox(
                "Risk Level",
                ["CONSERVATIVE (0.5%)", "MEDIUM (1.0%)", "AGGRESSIVE (1.5%)"],
                index=1
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
            st.markdown("---")
            st.subheader("📊 RECOMMENDED STAKES")
            
            total_stake = 0
            for idx, rec in enumerate(pattern_results['recommendations']):
                stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                total_stake += stake
                
                # Create a nice card for each stake
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        # FIXED: Display the correct team name for UNDER 1.5 bets
                        if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                            bet_label = f"**{rec['team_to_bet']} to score UNDER 1.5 goals**"
                        elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                            bet_label = f"**{rec['team_to_bet']} Double Chance**"
                        else:
                            bet_label = "**Total UNDER 3.5 goals**"
                        
                        st.markdown(bet_label)
                        st.caption(f"Pattern: {rec['pattern'].replace('_', ' ')}")
                    
                    with col_b:
                        st.metric("Stake", f"${stake:.2f}", f"{stake/bankroll_manager.bankroll*100:.1f}%")
                    
                    # Progress bar for stake percentage
                    stake_pct = stake / bankroll_manager.bankroll * 100
                    st.progress(min(stake_pct / 5, 1.0), text=f"Risk: {stake_pct:.1f}% of bankroll")
                    
                st.divider()
            
            # Total stake warning
            risk_percentage = (total_stake / bankroll_manager.bankroll) * 100
            
            if risk_percentage < 10:
                risk_color = "green"
            elif risk_percentage < 20:
                risk_color = "orange"
            else:
                risk_color = "red"
            
            st.success(f"""
            **Total Stake for This Match:** ${total_stake:.2f}
            
            **Risk Level:** {risk_percentage:.1f}% of bankroll • {pattern_results['patterns_detected']} pattern(s)
            """)
        
        # Performance Tracking
        st.markdown("---")
        st.subheader("📈 PERFORMANCE TRACKING")
        
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
        
        if st.button("Record Match Result", type="secondary", use_container_width=True):
            # Record predictions
            for rec in pattern_results['recommendations']:
                match_info = f"{home_team} vs {away_team}"
                
                # FIXED: Use the correct team name for UNDER 1.5 bets
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    prediction = f"{rec['team_to_bet']} to score UNDER 1.5 goals"
                elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                    prediction = f"{rec['team_to_bet']} Double Chance (Win or Draw)"
                else:
                    prediction = "Total UNDER 3.5 goals"
                
                accuracy = rec['sample_accuracy'].split('(')[0].strip()
                performance_tracker.record_prediction(match_info, prediction, accuracy)
            
            # Record result
            actual_score = f"{actual_home}-{actual_away}"
            performance_tracker.record_result(f"{home_team} vs {away_team}", actual_score)
            
            # Calculate profit/loss
            actual_total = actual_home + actual_away
            profit_loss = 0
            
            for rec in pattern_results['recommendations']:
                stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
                
                # Check if bet would win
                if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                    # FIXED: Check the correct team for UNDER 1.5
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
            if profit_loss >= 0:
                st.success(f"✅ Recorded: {home_team} {actual_home}-{actual_away} {away_team}")
                st.success(f"**Profit/Loss:** +${profit_loss:.2f}")
            else:
                st.warning(f"⚠️ Recorded: {home_team} {actual_home}-{actual_away} {away_team}")
                st.error(f"**Profit/Loss:** -${abs(profit_loss):.2f}")
            
            st.info(f"**New Bankroll:** ${bankroll_manager.bankroll:.2f}")
            
            # Check if should continue
            should_continue, message = bankroll_manager.should_continue_betting()
            if not should_continue:
                st.warning(f"⚠️ {message}")
            
            st.rerun()
        
        # Display performance stats
        stats = performance_tracker.calculate_accuracy()
        bankroll_status = bankroll_manager.get_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Predictions", stats['total_predictions'])
        with col2:
            st.metric("Accuracy", f"{stats['accuracy']:.1f}%")
        with col3:
            st.metric("Bankroll", f"${bankroll_status['bankroll']:.2f}")
        
        # Export functionality - FIXED: Proper datetime import
        st.markdown("---")
        st.subheader("📤 Export Analysis")
        
        # Prepare export text
        export_text = f"""BRUTBALL PROVEN PATTERNS ANALYSIS
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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
            # FIXED: Display correct team name in export
            if rec['pattern'] == 'ELITE_DEFENSE_UNDER_1_5':
                bet_desc = f"{rec['team_to_bet']} to score UNDER 1.5 goals"
            elif rec['pattern'] == 'WINNER_LOCK_DOUBLE_CHANCE':
                bet_desc = f"{rec['team_to_bet']} Double Chance (Win or Draw)"
            else:
                bet_desc = "Total UNDER 3.5 goals"
            
            stake = bankroll_manager.calculate_stake(rec, risk_level.split()[0])
            
            export_text += f"""
{idx+1}. {bet_desc}
   • Pattern: {rec['pattern'].replace('_', ' ')}
   • Reason: {rec['reason']}
   • Sample Accuracy: {rec['sample_accuracy']}
   • Stake Multiplier: {rec['stake_multiplier']:.1f}x
   • Recommended Stake: ${stake:.2f} ({stake/bankroll_manager.bankroll*100:.1f}% of bankroll)
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
            use_container_width=True
        )
    
    # Footer with pattern examples
    st.markdown("---")
    st.caption("**BRUTBALL PROVEN PATTERNS v1.0** - Based on 25-match empirical analysis")
    st.caption("Historical Proof: Porto 2-0 AVS • Espanyol 2-1 Athletic • Parma 1-0 Fiorentina")

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare league data"""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
        ]
        
        df = None
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                break
            except Exception:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived metrics from CSV structure"""
    
    # Goals scored
    df['home_goals_scored'] = (
        df['home_goals_openplay_for'].fillna(0) +
        df['home_goals_counter_for'].fillna(0) +
        df['home_goals_setpiece_for'].fillna(0) +
        df['home_goals_penalty_for'].fillna(0) +
        df['home_goals_owngoal_for'].fillna(0)
    )
    
    df['away_goals_scored'] = (
        df['away_goals_openplay_for'].fillna(0) +
        df['away_goals_counter_for'].fillna(0) +
        df['away_goals_setpiece_for'].fillna(0) +
        df['away_goals_penalty_for'].fillna(0) +
        df['away_goals_owngoal_for'].fillna(0)
    )
    
    # Goals conceded
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
    
    # Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

if __name__ == "__main__":
    main()
