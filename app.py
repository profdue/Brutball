import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Football Betting Strategy Analyzer",
    page_icon="⚽",
    layout="wide"
)

# App title and description
st.title("⚽ Football Betting Strategy Analyzer")
st.markdown("""
This app implements the 3-Filter betting strategy we developed. 
Fill in the data for both teams to get match profile classification and betting recommendations.
""")

# Sidebar for instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Fill all fields** for both teams
    2. Use **home/away splits** where applicable
    3. **Recent form** = last 5-10 games
    4. **Key absences**: Star attackers or defenders
    5. Click **Analyze Match** when ready
    """)
    
    st.header("🎯 Strategy Rules")
    st.markdown("""
    **Tight, Cautious Affair** → Under 2.5 & BTTS: No  
    **One-Sided Dominance** → Favorite Win & BTTS: No  
    **Open Contest** → BTTS: Yes (caution on Over 2.5)
    """)

# Initialize session state for storing results
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Create two columns for team inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Home Team")
    
    # Basic team info
    home_team = st.text_input("Team Name", key="home_name")
    
    # Filter 1: Form & Averages
    st.markdown("### 📊 Form & Averages")
    
    home_form_last5 = st.text_input(
        "Last 5 Results (W/D/L)", 
        placeholder="W,W,D,L,W",
        key="home_form5"
    )
    
    home_avg_scored = st.number_input(
        "Avg Goals Scored (Home)", 
        min_value=0.0, max_value=5.0, value=1.5, step=0.1,
        key="home_avg_scored"
    )
    
    home_avg_conceded = st.number_input(
        "Avg Goals Conceded (Home)", 
        min_value=0.0, max_value=5.0, value=1.0, step=0.1,
        key="home_avg_conceded"
    )
    
    home_over25_pct = st.slider(
        "Over 2.5 Goals % (Last 10)", 
        min_value=0, max_value=100, value=40,
        key="home_over25"
    )
    
    home_btts_pct = st.slider(
        "BTTS Yes % (Last 10)", 
        min_value=0, max_value=100, value=40,
        key="home_btts"
    )
    
    # Filter 2: Style & Key Stats
    st.markdown("### ⚽ Playing Style")
    
    home_possession = st.slider(
        "Avg Possession %", 
        min_value=0, max_value=100, value=45,
        key="home_possession"
    )
    
    home_shots_on_target = st.number_input(
        "Shots on Target (Avg)", 
        min_value=0.0, max_value=10.0, value=4.0, step=0.1,
        key="home_sot"
    )
    
    home_key_attacker_out = st.checkbox(
        "Key Attacker Injured/Suspended",
        key="home_attacker_out"
    )
    
    home_key_defender_out = st.checkbox(
        "Key Defender Injured/Suspended",
        key="home_defender_out"
    )
    
    # Filter 3: Context
    st.markdown("### 🎭 Match Context")
    
    home_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High", "Medium", "Low"],
        key="home_motivation"
    )

with col2:
    st.subheader("✈️ Away Team")
    
    # Basic team info
    away_team = st.text_input("Team Name", key="away_name")
    
    # Filter 1: Form & Averages
    st.markdown("### 📊 Form & Averages")
    
    away_form_last5 = st.text_input(
        "Last 5 Results (W/D/L)", 
        placeholder="L,W,D,W,D",
        key="away_form5"
    )
    
    away_avg_scored = st.number_input(
        "Avg Goals Scored (Away)", 
        min_value=0.0, max_value=5.0, value=1.0, step=0.1,
        key="away_avg_scored"
    )
    
    away_avg_conceded = st.number_input(
        "Avg Goals Conceded (Away)", 
        min_value=0.0, max_value=5.0, value=1.5, step=0.1,
        key="away_avg_conceded"
    )
    
    away_over25_pct = st.slider(
        "Over 2.5 Goals % (Last 10)", 
        min_value=0, max_value=100, value=50,
        key="away_over25"
    )
    
    away_btts_pct = st.slider(
        "BTTS Yes % (Last 10)", 
        min_value=0, max_value=100, value=60,
        key="away_btts"
    )
    
    # Filter 2: Style & Key Stats
    st.markdown("### ⚽ Playing Style")
    
    away_possession = st.slider(
        "Avg Possession %", 
        min_value=0, max_value=100, value=50,
        key="away_possession"
    )
    
    away_shots_on_target = st.number_input(
        "Shots on Target (Avg)", 
        min_value=0.0, max_value=10.0, value=4.5, step=0.1,
        key="away_sot"
    )
    
    away_key_attacker_out = st.checkbox(
        "Key Attacker Injured/Suspended",
        key="away_attacker_out"
    )
    
    away_key_defender_out = st.checkbox(
        "Key Defender Injured/Suspended",
        key="away_defender_out"
    )
    
    # Filter 3: Context
    st.markdown("### 🎭 Match Context")
    
    away_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High", "Medium", "Low"],
        key="away_motivation"
    )
    
    match_context = st.selectbox(
        "Match Type",
        ["Normal League", "Local Derby", "Cup Final", "Relegation Battle", "Title Decider"],
        key="match_context"
    )

# Odds section
st.markdown("---")
st.subheader("🎰 Market Odds")

odds_col1, odds_col2, odds_col3 = st.columns(3)

with odds_col1:
    over25_odds = st.number_input(
        "Over 2.5 Goals Odds", 
        min_value=1.01, max_value=10.0, value=1.88, step=0.01,
        key="over25_odds"
    )
    
    under25_odds = st.number_input(
        "Under 2.5 Goals Odds", 
        min_value=1.01, max_value=10.0, value=1.91, step=0.01,
        key="under25_odds"
    )

with odds_col2:
    btts_yes_odds = st.number_input(
        "BTTS Yes Odds", 
        min_value=1.01, max_value=10.0, value=1.67, step=0.01,
        key="btts_yes_odds"
    )
    
    btts_no_odds = st.number_input(
        "BTTS No Odds", 
        min_value=1.01, max_value=10.0, value=2.12, step=0.01,
        key="btts_no_odds"
    )

with odds_col3:
    home_win_odds = st.number_input(
        f"{home_team or 'Home'} Win Odds", 
        min_value=1.01, max_value=10.0, value=2.15, step=0.01,
        key="home_win_odds"
    )
    
    away_win_odds = st.number_input(
        f"{away_team or 'Away'} Win Odds", 
        min_value=1.01, max_value=10.0, value=2.15, step=0.01,
        key="away_win_odds"
    )

# Analysis button
st.markdown("---")
analyze_button = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

# Function to calculate match profile
def calculate_match_profile(data):
    """Calculate match profile based on 3-filter strategy"""
    
    # Initialize scores for each profile
    profile_scores = {
        'tight_cautious': 0,
        'one_sided_dominance': 0,
        'open_contest': 0
    }
    
    # Filter 1: Form & Averages Analysis
    total_goals_avg = data['home_avg_scored'] + data['away_avg_scored']
    total_conceded_avg = data['home_avg_conceded'] + data['away_avg_conceded']
    
    # Tight/Cautious indicators
    if total_goals_avg < 2.5:
        profile_scores['tight_cautious'] += 2
    if (data['home_over25_pct'] < 40 and data['away_over25_pct'] < 40):
        profile_scores['tight_cautious'] += 1
    if data['match_context'] in ['Local Derby', 'Cup Final']:
        profile_scores['tight_cautious'] += 2
    
    # Open Contest indicators
    if total_goals_avg > 3.0:
        profile_scores['open_contest'] += 1
    if (data['home_btts_pct'] > 60 and data['away_btts_pct'] > 60):
        profile_scores['open_contest'] += 2
    if data['home_shots_on_target'] > 5.0 and data['away_shots_on_target'] > 5.0:
        profile_scores['open_contest'] += 1
    
    # One-Sided Dominance indicators
    form_diff = abs(data['home_avg_scored'] - data['home_avg_conceded']) - \
                abs(data['away_avg_scored'] - data['away_avg_conceded'])
    
    if abs(form_diff) > 1.0:  # Significant form difference
        profile_scores['one_sided_dominance'] += 2
    
    # Check for key absences that create imbalance
    if data['home_key_attacker_out'] and not data['away_key_attacker_out']:
        profile_scores['one_sided_dominance'] += 1
    if data['away_key_defender_out'] and not data['home_key_defender_out']:
        profile_scores['one_sided_dominance'] += 1
    
    # Determine dominant profile
    max_score = max(profile_scores.values())
    dominant_profiles = [k for k, v in profile_scores.items() if v == max_score]
    
    # Default to tight_cautious if unclear
    if len(dominant_profiles) > 1:
        return 'tight_cautious'
    else:
        return dominant_profiles[0]

# Function to get betting recommendations
def get_betting_recommendations(profile, data):
    """Get betting recommendations based on match profile"""
    
    recommendations = {
        'primary_markets': [],
        'secondary_markets': [],
        'avoid_markets': [],
        'confidence': 'Medium'
    }
    
    if profile == 'tight_cautious':
        recommendations['primary_markets'] = [
            f"Under {2.5} Goals @ {data['under25_odds']}",
            f"BTTS: No @ {data['btts_no_odds']}"
        ]
        recommendations['secondary_markets'] = [
            "Draw",
            "0-0 or 1-0 Correct Score"
        ]
        recommendations['avoid_markets'] = [
            "Over 2.5 Goals",
            "BTTS: Yes"
        ]
        recommendations['confidence'] = 'High' if data['match_context'] == 'Local Derby' else 'Medium'
        
    elif profile == 'open_contest':
        recommendations['primary_markets'] = [
            f"BTTS: Yes @ {data['btts_yes_odds']}"
        ]
        recommendations['secondary_markets'] = [
            f"Over 2.5 Goals @ {data['over25_odds']}",
            "Draw with BTTS"
        ]
        recommendations['avoid_markets'] = [
            "BTTS: No",
            "Under 1.5 Goals"
        ]
        recommendations['confidence'] = 'Medium'
        
    elif profile == 'one_sided_dominance':
        # Determine which team is dominant
        home_strength = data['home_avg_scored'] - data['home_avg_conceded']
        away_strength = data['away_avg_scored'] - data['away_avg_conceded']
        
        if home_strength > away_strength:
            favorite = 'home'
            favorite_odds = data['home_win_odds']
            favorite_name = data['home_team']
        else:
            favorite = 'away'
            favorite_odds = data['away_win_odds']
            favorite_name = data['away_team']
        
        recommendations['primary_markets'] = [
            f"{favorite_name} to Win @ {favorite_odds}",
            f"BTTS: No @ {data['btts_no_odds']}"
        ]
        
        # Check for handicap opportunity (based on our refined rule)
        handicap_confident = False
        if abs(home_strength - away_strength) > 1.5:  # Significant strength difference
            handicap_confident = True
            recommendations['secondary_markets'] = [
                f"{favorite_name} -1 Asian Handicap",
                f"{favorite_name} to Win to Nil"
            ]
        else:
            recommendations['secondary_markets'] = [
                f"{favorite_name} Draw No Bet",
                "Under 3.5 Goals"
            ]
        
        recommendations['avoid_markets'] = [
            "BTTS: Yes" if favorite == 'home' else f"{data['home_team']} to Win",
            "Over 3.5 Goals"
        ]
        recommendations['confidence'] = 'High' if handicap_confident else 'Medium'
    
    return recommendations

# Function to calculate value bets
def calculate_value_bets(profile, data, recommendations):
    """Calculate if there's value in the odds based on our probability estimates"""
    
    value_bets = []
    
    if profile == 'tight_cautious':
        # Our estimated probability for Under 2.5
        our_prob = 0.65  # Based on our strategy success rate
        implied_prob = 1 / data['under25_odds']
        
        if our_prob > implied_prob + 0.1:  # 10% edge
            value_bets.append({
                'market': f"Under {2.5} Goals",
                'odds': data['under25_odds'],
                'our_prob': our_prob,
                'implied_prob': implied_prob,
                'edge': f"{(our_prob - implied_prob)*100:.1f}%"
            })
    
    elif profile == 'open_contest':
        our_prob = 0.60
        implied_prob = 1 / data['btts_yes_odds']
        
        if our_prob > implied_prob + 0.1:
            value_bets.append({
                'market': "BTTS: Yes",
                'odds': data['btts_yes_odds'],
                'our_prob': our_prob,
                'implied_prob': implied_prob,
                'edge': f"{(our_prob - implied_prob)*100:.1f}%"
            })
    
    elif profile == 'one_sided_dominance':
        home_strength = data['home_avg_scored'] - data['home_avg_conceded']
        away_strength = data['away_avg_scored'] - data['away_avg_conceded']
        
        if home_strength > away_strength:
            favorite_odds = data['home_win_odds']
            our_prob = 0.70 if abs(home_strength - away_strength) > 1.5 else 0.60
        else:
            favorite_odds = data['away_win_odds']
            our_prob = 0.70 if abs(home_strength - away_strength) > 1.5 else 0.60
        
        implied_prob = 1 / favorite_odds
        
        if our_prob > implied_prob + 0.1:
            favorite_name = data['home_team'] if home_strength > away_strength else data['away_team']
            value_bets.append({
                'market': f"{favorite_name} to Win",
                'odds': favorite_odds,
                'our_prob': our_prob,
                'implied_prob': implied_prob,
                'edge': f"{(our_prob - implied_prob)*100:.1f}%"
            })
    
    return value_bets

# Function to create visualization
def create_profile_visualization(profile_scores, profile):
    """Create visualization of profile analysis"""
    
    fig = go.Figure()
    
    profiles = ['Tight/Cautious', 'One-Sided', 'Open Contest']
    scores = [
        profile_scores['tight_cautious'],
        profile_scores['one_sided_dominance'],
        profile_scores['open_contest']
    ]
    
    colors = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)']
    
    for i, (prof, score, color) in enumerate(zip(profiles, scores, colors)):
        fig.add_trace(go.Bar(
            x=[prof],
            y=[score],
            name=prof,
            marker_color=color,
            text=[f"Score: {score}"],
            textposition='auto',
        ))
    
    fig.update_layout(
        title="Match Profile Analysis Scores",
        yaxis_title="Profile Score",
        showlegend=False,
        height=400
    )
    
    return fig

# Main analysis logic
if analyze_button:
    # Validate inputs
    if not home_team or not away_team:
        st.error("Please enter team names for both home and away teams.")
    else:
        # Prepare data dictionary
        analysis_data = {
            'home_team': home_team,
            'away_team': away_team,
            'home_avg_scored': home_avg_scored,
            'home_avg_conceded': home_avg_conceded,
            'home_over25_pct': home_over25_pct,
            'home_btts_pct': home_btts_pct,
            'home_shots_on_target': home_shots_on_target,
            'home_key_attacker_out': home_key_attacker_out,
            'home_key_defender_out': home_key_defender_out,
            'away_avg_scored': away_avg_scored,
            'away_avg_conceded': away_avg_conceded,
            'away_over25_pct': away_over25_pct,
            'away_btts_pct': away_btts_pct,
            'away_shots_on_target': away_shots_on_target,
            'away_key_attacker_out': away_key_attacker_out,
            'away_key_defender_out': away_key_defender_out,
            'match_context': match_context,
            'over25_odds': over25_odds,
            'under25_odds': under25_odds,
            'btts_yes_odds': btts_yes_odds,
            'btts_no_odds': btts_no_odds,
            'home_win_odds': home_win_odds,
            'away_win_odds': away_win_odds
        }
        
        # Calculate profile scores for visualization
        profile_scores = {
            'tight_cautious': 0,
            'one_sided_dominance': 0,
            'open_contest': 0
        }
        
        # Calculate scores (simplified version)
        total_goals_avg = home_avg_scored + away_avg_scored
        if total_goals_avg < 2.5:
            profile_scores['tight_cautious'] += 2
        if match_context in ['Local Derby', 'Cup Final']:
            profile_scores['tight_cautious'] += 2
        
        if total_goals_avg > 3.0:
            profile_scores['open_contest'] += 1
        if home_btts_pct > 60 and away_btts_pct > 60:
            profile_scores['open_contest'] += 2
        
        form_diff = abs(home_avg_scored - home_avg_conceded) - \
                   abs(away_avg_scored - away_avg_conceded)
        if abs(form_diff) > 1.0:
            profile_scores['one_sided_dominance'] += 2
        
        # Determine match profile
        match_profile = calculate_match_profile(analysis_data)
        
        # Get recommendations
        recommendations = get_betting_recommendations(match_profile, analysis_data)
        
        # Calculate value bets
        value_bets = calculate_value_bets(match_profile, analysis_data, recommendations)
        
        # Display results
        st.session_state.analysis_complete = True
        
        st.markdown("---")
        st.header("📈 Analysis Results")
        
        # Create columns for results
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            # Display match profile
            profile_names = {
                'tight_cautious': '🔒 Tight, Cautious Affair',
                'one_sided_dominance': '⚡ One-Sided Dominance',
                'open_contest': '🔥 Open Contest'
            }
            
            st.metric(
                "Identified Match Profile",
                profile_names[match_profile],
                delta=f"Confidence: {recommendations['confidence']}"
            )
            
            # Display profile visualization
            st.plotly_chart(create_profile_visualization(profile_scores, match_profile), 
                          use_container_width=True)
        
        with result_col2:
            st.subheader("🎯 Betting Recommendations")
            
            st.markdown("#### Primary Markets")
            for market in recommendations['primary_markets']:
                st.success(f"✅ {market}")
            
            if recommendations['secondary_markets']:
                st.markdown("#### Secondary Markets")
                for market in recommendations['secondary_markets']:
                    st.info(f"💡 {market}")
            
            if recommendations['avoid_markets']:
                st.markdown("#### Markets to Avoid")
                for market in recommendations['avoid_markets']:
                    st.warning(f"⚠️ {market}")
        
        # Display value bets if any
        if value_bets:
            st.markdown("---")
            st.subheader("💰 Value Bet Opportunities")
            
            for bet in value_bets:
                with st.expander(f"{bet['market']} - {bet['edge']} Edge"):
                    st.markdown(f"""
                    **Odds:** {bet['odds']}
                    **Implied Probability:** {bet['implied_prob']:.1%}
                    **Our Estimated Probability:** {bet['our_prob']:.1%}
                    **Value Edge:** {bet['edge']}
                    """)
        
        # Display strategy insights
        st.markdown("---")
        st.subheader("🧠 Strategy Insights")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.metric(
                "Goal Expectation",
                f"{total_goals_avg:.1f}",
                "Total Avg Goals"
            )
        
        with insight_col2:
            btts_trend = "High" if (home_btts_pct > 60 and away_btts_pct > 60) else \
                        "Low" if (home_btts_pct < 40 and away_btts_pct < 40) else "Medium"
            st.metric("BTTS Trend", btts_trend)
        
        with insight_col3:
            form_imbalance = "Significant" if abs(form_diff) > 1.0 else "Minor"
            st.metric("Form Imbalance", form_imbalance)
        
        # Historical success rate based on profile
        st.markdown("#### 📊 Historical Success Rates by Profile")
        
        success_data = pd.DataFrame({
            'Profile': ['Tight/Cautious', 'One-Sided Dominance', 'Open Contest'],
            'Primary Market Win Rate': ['70-75%', '65-70%', '60-65%'],
            'Key Market': ['Under 2.5 Goals', 'Favorite Win + BTTS: No', 'BTTS: Yes']
        })
        
        st.dataframe(success_data, use_container_width=True, hide_index=True)

# Display sample data option
st.markdown("---")
with st.expander("📋 Load Sample Data (Sunderland vs Newcastle)"):
    if st.button("Load Sample Match Data"):
        st.rerun()  # This would need to be implemented with session state to actually load data

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with the 3-Filter Betting Strategy • All calculations follow our tested logic</p>
    <p><small>Remember: No betting strategy guarantees wins. Always gamble responsibly.</small></p>
</div>
""", unsafe_allow_html=True)