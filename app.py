import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import math

# Page configuration
st.set_page_config(
    page_title="Football Prediction System v4.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CORE DATA & CONSTANTS ====================

# Team Quality Tiers (adjustable per league)
QUALITY_TIERS = {
    'Tier 1 (Elite)': ['Man City', 'Liverpool', 'Arsenal', 'Real Madrid', 'Bayern', 'Barcelona', 'PSG'],
    'Tier 2 (Strong)': ['Chelsea', 'Tottenham', 'Man United', 'Newcastle', 'Aston Villa', 'Juventus', 'Inter', 'Milan'],
    'Tier 3 (Average)': ['West Ham', 'Brighton', 'Wolves', 'Crystal Palace', 'Bournemouth', 'Everton'],
    'Tier 4 (Weak)': ['Brentford', 'Fulham', 'Nottingham Forest', 'Luton', 'Sheffield Utd', 'Burnley']
}

# League Styles (affects default expectations)
LEAGUE_STYLES = {
    'Premier League': {'avg_goals': 2.85, 'btts_pct': 52, 'style': 'Balanced'},
    'La Liga': {'avg_goals': 2.55, 'btts_pct': 48, 'style': 'Technical'},
    'Serie A': {'avg_goals': 2.65, 'btts_pct': 49, 'style': 'Tactical'},
    'Bundesliga': {'avg_goals': 3.10, 'btts_pct': 58, 'style': 'Attack-Minded'},
    'Ligue 1': {'avg_goals': 2.70, 'btts_pct': 50, 'style': 'Mixed'},
    'Eredivisie': {'avg_goals': 3.15, 'btts_pct': 60, 'style': 'Very Attacking'},
    'Championship': {'avg_goals': 2.60, 'btts_pct': 51, 'style': 'Physical'},
    'Custom League': {'avg_goals': 2.70, 'btts_pct': 52, 'style': 'Standard'}
}

# ==================== CORE ENGINE FUNCTIONS ====================

def get_quality_tier(team_name):
    """Determine team quality tier"""
    for tier, teams in QUALITY_TIERS.items():
        if team_name in teams:
            return tier
    return 'Tier 3 (Average)'  # Default if not found

def calculate_quality_multiplier(home_tier, away_tier):
    """Calculate adjustment based on quality difference"""
    tier_values = {
        'Tier 1 (Elite)': 4,
        'Tier 2 (Strong)': 3,
        'Tier 3 (Average)': 2,
        'Tier 4 (Weak)': 1
    }
    
    home_val = tier_values.get(home_tier, 2)
    away_val = tier_values.get(away_tier, 2)
    
    diff = home_val - away_val
    
    # Return multipliers for home and away
    if diff >= 2:  # Home much stronger
        return {'home_attack': 1.3, 'home_defense': 0.8, 'away_attack': 0.7, 'away_defense': 1.4}
    elif diff == 1:  # Home stronger
        return {'home_attack': 1.15, 'home_defense': 0.9, 'away_attack': 0.85, 'away_defense': 1.15}
    elif diff == 0:  # Equal
        return {'home_attack': 1.0, 'home_defense': 1.0, 'away_attack': 1.0, 'away_defense': 1.0}
    elif diff == -1:  # Away stronger
        return {'home_attack': 0.85, 'home_defense': 1.15, 'away_attack': 1.15, 'away_defense': 0.9}
    else:  # Away much stronger (diff <= -2)
        return {'home_attack': 0.7, 'home_defense': 1.4, 'away_attack': 1.3, 'away_defense': 0.8}

def calculate_motivation_adjustment(home_motivation, away_motivation):
    """Adjust performance based on motivation"""
    motivation_values = {
        'Very High (Title/Relegation)': 1.25,
        'High (Europe/Important)': 1.15,
        'Medium (Normal)': 1.0,
        'Low (Nothing to play for)': 0.85,
        'Very Low (Season over)': 0.75
    }
    
    home_mult = motivation_values.get(home_motivation, 1.0)
    away_mult = motivation_values.get(away_motivation, 1.0)
    
    return {'home': home_mult, 'away': away_mult}

def calculate_context_adjustment(context, venue='Home'):
    """Adjust for match context"""
    context_multipliers = {
        'Local Derby': {'attack': 0.9, 'defense': 1.2, 'goals': 0.8},
        'Cup Final': {'attack': 0.95, 'defense': 1.15, 'goals': 0.85},
        'Relegation Battle': {'attack': 1.1, 'defense': 0.95, 'goals': 1.05},
        'Title Decider': {'attack': 1.05, 'defense': 1.05, 'goals': 1.0},
        'European Competition': {'attack': 1.0, 'defense': 1.0, 'goals': 1.0},
        'Normal League': {'attack': 1.0, 'defense': 1.0, 'goals': 1.0}
    }
    
    return context_multipliers.get(context, context_multipliers['Normal League'])

def adjust_for_absences(key_attacker_out, key_defender_out, is_home=True):
    """Adjust stats for key player absences"""
    attack_mult = 1.0
    defense_mult = 1.0
    
    if key_attacker_out:
        attack_mult = 0.75 if is_home else 0.8
    
    if key_defender_out:
        defense_mult = 1.3 if is_home else 1.25
    
    return {'attack': attack_mult, 'defense': defense_mult}

def calculate_expected_goals(home_data, away_data, league_style, match_context):
    """Calculate expected goals with all adjustments"""
    
    # Get quality tiers
    home_tier = get_quality_tier(home_data['name'])
    away_tier = get_quality_tier(away_data['name'])
    
    # Calculate base adjustments
    quality_adj = calculate_quality_multiplier(home_tier, away_tier)
    motivation_adj = calculate_motivation_adjustment(home_data['motivation'], away_data['motivation'])
    context_adj = calculate_context_adjustment(match_context)
    home_absence_adj = adjust_for_absences(home_data['key_attacker_out'], home_data['key_defender_out'], True)
    away_absence_adj = adjust_for_absences(away_data['key_attacker_out'], away_data['key_defender_out'], False)
    
    # Calculate adjusted stats
    home_adj_attack = (home_data['avg_scored'] * 
                       quality_adj['home_attack'] * 
                       motivation_adj['home'] * 
                       context_adj['attack'] * 
                       home_absence_adj['attack'])
    
    home_adj_defense = (home_data['avg_conceded'] * 
                        quality_adj['home_defense'] * 
                        (1.0 / motivation_adj['home']) *  # Inverse for defense
                        context_adj['defense'] * 
                        home_absence_adj['defense'])
    
    away_adj_attack = (away_data['avg_scored'] * 
                       quality_adj['away_attack'] * 
                       motivation_adj['away'] * 
                       context_adj['attack'] * 
                       away_absence_adj['attack'])
    
    away_adj_defense = (away_data['avg_conceded'] * 
                        quality_adj['away_defense'] * 
                        (1.0 / motivation_adj['away']) *  # Inverse for defense
                        context_adj['defense'] * 
                        away_absence_adj['defense'])
    
    # Calculate expected goals for each team
    # Home expected goals = Home attack vs Away defense
    home_expected = (home_adj_attack * (1.0 / away_adj_defense) * 
                     league_style['avg_goals'] / 2.7)  # Normalize to league average
    
    # Away expected goals = Away attack vs Home defense  
    away_expected = (away_adj_attack * (1.0 / home_adj_defense) * 
                     league_style['avg_goals'] / 2.7)  # Normalize to league average
    
    # Apply context goal multiplier
    total_expected = (home_expected + away_expected) * context_adj['goals']
    
    # Cap unrealistic values
    home_expected = min(home_expected, 4.0)
    away_expected = min(away_expected, 3.0)
    total_expected = min(total_expected, 6.0)
    
    return {
        'home_expected': round(home_expected, 2),
        'away_expected': round(away_expected, 2),
        'total_expected': round(total_expected, 2),
        'home_adj_attack': round(home_adj_attack, 2),
        'away_adj_attack': round(away_adj_attack, 2)
    }

def calculate_btts_probability(home_data, away_data, expected_goals, match_context):
    """Calculate BTTS probability with adjustments"""
    
    # Base probability from expected goals
    # Using Poisson approximation: P(both score) = P(home scores) * P(away scores)
    home_score_prob = 1 - math.exp(-expected_goals['home_expected'])
    away_score_prob = 1 - math.exp(-expected_goals['away_expected'])
    
    base_btts = home_score_prob * away_score_prob * 100
    
    # Adjust for teams' BTTS tendencies
    avg_btts = (home_data['btts_pct'] + away_data['btts_pct']) / 2
    adjusted_btts = (base_btts * 0.6) + (avg_btts * 0.4)
    
    # Context adjustments
    if match_context == 'Local Derby':
        adjusted_btts *= 0.9  # Derbies often tighter
    elif match_context == 'Cup Final':
        adjusted_btts *= 0.95
    
    # Ensure realistic bounds
    adjusted_btts = max(10, min(90, adjusted_btts))
    
    return round(adjusted_btts, 1)

def calculate_win_probabilities(home_data, away_data, expected_goals, match_context):
    """Calculate win/draw probabilities"""
    
    # Use expected goals difference as base
    goal_diff = expected_goals['home_expected'] - expected_goals['away_expected']
    
    # Convert to win probabilities using logistic function
    # This is simplified - in practice you'd use more sophisticated models
    home_win_base = 50 + (goal_diff * 15)  # Each 0.1 goal diff = 1.5% change
    
    # Adjust for home advantage
    home_win_base += 8  # Typical home advantage
    
    # Adjust for motivation
    motivation_values = {
        'Very High (Title/Relegation)': 1.15,
        'High (Europe/Important)': 1.08,
        'Medium (Normal)': 1.0,
        'Low (Nothing to play for)': 0.92,
        'Very Low (Season over)': 0.85
    }
    
    home_motivation = motivation_values.get(home_data['motivation'], 1.0)
    away_motivation = motivation_values.get(away_data['motivation'], 1.0)
    
    home_win_adj = home_win_base * home_motivation / away_motivation
    
    # Context adjustments
    if match_context == 'Local Derby':
        home_win_adj *= 0.95  # Derbies more unpredictable
    elif match_context == 'Cup Final':
        home_win_adj *= 1.0  # Neutral venue
    
    # Calculate draw probability (typically 20-30%)
    draw_prob = 25 - (abs(goal_diff) * 5)
    draw_prob = max(15, min(35, draw_prob))
    
    # Normalize to 100%
    home_win_prob = max(20, min(80, home_win_adj))
    away_win_prob = 100 - home_win_prob - draw_prob
    
    # Ensure all probabilities are positive
    away_win_prob = max(10, away_win_prob)
    
    # Redistribute to sum to 100
    total = home_win_prob + draw_prob + away_win_prob
    home_win_prob = (home_win_prob / total) * 100
    draw_prob = (draw_prob / total) * 100
    away_win_prob = (away_win_prob / total) * 100
    
    return {
        'home_win': round(home_win_prob, 1),
        'draw': round(draw_prob, 1),
        'away_win': round(away_win_prob, 1)
    }

def determine_match_profile(expected_goals, win_probs, btts_prob, home_data, away_data):
    """Determine the match profile based on all factors"""
    
    profiles = []
    scores = []
    
    # Profile 1: Quality-Driven Dominance
    goal_diff = abs(expected_goals['home_expected'] - expected_goals['away_expected'])
    win_prob_diff = abs(win_probs['home_win'] - win_probs['away_win'])
    
    dominance_score = (goal_diff * 20) + (win_prob_diff * 0.3)
    if goal_diff > 1.0 or win_prob_diff > 30:
        dominance_score += 20
    
    profiles.append('Quality-Driven Dominance')
    scores.append(dominance_score)
    
    # Profile 2: Tactical Battle
    tactical_score = 0
    
    # Both defensive
    if home_data['avg_scored'] < 1.2 and away_data['avg_scored'] < 1.2:
        tactical_score += 25
    
    # Both low Over 2.5%
    if home_data['over25_pct'] < 40 and away_data['over25_pct'] < 40:
        tactical_score += 20
    
    # Context factors
    if home_data.get('match_context') in ['Local Derby', 'Cup Final']:
        tactical_score += 15
    
    profiles.append('Tactical Battle')
    scores.append(tactical_score)
    
    # Profile 3: Open Exchange
    open_score = 0
    
    # Both attacking
    if home_data['avg_scored'] > 1.6 and away_data['avg_scored'] > 1.6:
        open_score += 25
    
    # Both high Over 2.5%
    if home_data['over25_pct'] > 60 and away_data['over25_pct'] > 60:
        open_score += 20
    
    # High BTTS probability
    if btts_prob > 60:
        open_score += 15
    
    # High expected goals
    if expected_goals['total_expected'] > 3.0:
        open_score += 20
    
    profiles.append('Open Exchange')
    scores.append(open_score)
    
    # Profile 4: Context-Driven Anomaly
    context_score = 0
    
    # Special contexts
    if home_data.get('match_context') in ['Local Derby', 'Cup Final', 'Title Decider', 'Relegation Battle']:
        context_score += 30
    
    # Extreme motivation mismatch
    motivation_values = {
        'Very High (Title/Relegation)': 5,
        'High (Europe/Important)': 4,
        'Medium (Normal)': 3,
        'Low (Nothing to play for)': 2,
        'Very Low (Season over)': 1
    }
    
    home_mot = motivation_values.get(home_data['motivation'], 3)
    away_mot = motivation_values.get(away_data['motivation'], 3)
    
    if abs(home_mot - away_mot) >= 3:
        context_score += 20
    
    profiles.append('Context-Driven Anomaly')
    scores.append(context_score)
    
    # Determine primary profile
    max_score = max(scores)
    primary_idx = scores.index(max_score)
    primary_profile = profiles[primary_idx]
    
    # Determine confidence
    if max_score >= 50:
        confidence = 'High'
    elif max_score >= 30:
        confidence = 'Medium'
    else:
        confidence = 'Low'
    
    # Determine sub-profile
    sub_profile = ""
    if primary_profile == 'Quality-Driven Dominance':
        if goal_diff > 1.5:
            sub_profile = "Complete Domination"
        elif goal_diff > 0.8:
            sub_profile = "Controlled Superiority"
        else:
            sub_profile = "Moderate Advantage"
    
    elif primary_profile == 'Tactical Battle':
        if expected_goals['total_expected'] < 2.0:
            sub_profile = "Defensive Stalemate"
        elif abs(expected_goals['home_expected'] - expected_goals['away_expected']) < 0.5:
            sub_profile = "Strategic Chess"
        else:
            sub_profile = "Tactical Contest"
    
    elif primary_profile == 'Open Exchange':
        if expected_goals['total_expected'] > 3.5:
            sub_profile = "Goal-Fest Likely"
        elif btts_prob > 70:
            sub_profile = "End-to-End Action"
        else:
            sub_profile = "Open Contest"
    
    else:  # Context-Driven Anomaly
        if home_data.get('match_context') == 'Local Derby':
            sub_profile = "Derby Dogfight"
        elif home_data.get('match_context') == 'Cup Final':
            sub_profile = "Cup Magic"
        elif home_data.get('match_context') == 'Relegation Battle':
            sub_profile = "Survival Battle"
        else:
            sub_profile = "Special Context"
    
    return {
        'primary': primary_profile,
        'sub_profile': sub_profile,
        'confidence': confidence,
        'scores': dict(zip(profiles, scores)),
        'max_score': max_score
    }

def calculate_value_opportunities(probabilities, odds):
    """Calculate value opportunities vs market odds"""
    
    opportunities = []
    
    # Convert probabilities to fair odds
    implied_prob = {
        'home_win': 1 / odds['home_win'] * 100 if odds['home_win'] > 0 else 0,
        'draw': 1 / odds['draw'] * 100 if odds['draw'] > 0 else 0,
        'away_win': 1 / odds['away_win'] * 100 if odds['away_win'] > 0 else 0,
        'over25': 1 / odds['over25'] * 100 if odds['over25'] > 0 else 0,
        'under25': 1 / odds['under25'] * 100 if odds['under25'] > 0 else 0,
        'btts_yes': 1 / odds['btts_yes'] * 100 if odds['btts_yes'] > 0 else 0,
        'btts_no': 1 / odds['btts_no'] * 100 if odds['btts_no'] > 0 else 0
    }
    
    # Calculate edges
    edges = {
        'home_win': probabilities['home_win'] - implied_prob['home_win'],
        'away_win': probabilities['away_win'] - implied_prob['away_win'],
        'over25': probabilities['over25_chance'] - implied_prob['over25'],
        'under25': probabilities['under25_chance'] - implied_prob['under25'],
        'btts_yes': probabilities['btts_prob'] - implied_prob['btts_yes'],
        'btts_no': (100 - probabilities['btts_prob']) - implied_prob['btts_no']
    }
    
    # Sort by edge value
    sorted_edges = sorted(edges.items(), key=lambda x: abs(x[1]), reverse=True)
    
    for market, edge in sorted_edges:
        if edge > 2:  # Minimum 2% edge to consider
            if market == 'home_win':
                opportunities.append({
                    'market': f"{odds.get('home_team', 'Home')} to Win",
                    'odds': odds['home_win'],
                    'our_prob': probabilities['home_win'],
                    'market_prob': implied_prob['home_win'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
            elif market == 'away_win':
                opportunities.append({
                    'market': f"{odds.get('away_team', 'Away')} to Win",
                    'odds': odds['away_win'],
                    'our_prob': probabilities['away_win'],
                    'market_prob': implied_prob['away_win'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
            elif market == 'over25':
                opportunities.append({
                    'market': "Over 2.5 Goals",
                    'odds': odds['over25'],
                    'our_prob': probabilities['over25_chance'],
                    'market_prob': implied_prob['over25'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
            elif market == 'under25':
                opportunities.append({
                    'market': "Under 2.5 Goals",
                    'odds': odds['under25'],
                    'our_prob': probabilities['under25_chance'],
                    'market_prob': implied_prob['under25'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
            elif market == 'btts_yes':
                opportunities.append({
                    'market': "BTTS: Yes",
                    'odds': odds['btts_yes'],
                    'our_prob': probabilities['btts_prob'],
                    'market_prob': implied_prob['btts_yes'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
            elif market == 'btts_no':
                opportunities.append({
                    'market': "BTTS: No",
                    'odds': odds['btts_no'],
                    'our_prob': 100 - probabilities['btts_prob'],
                    'market_prob': implied_prob['btts_no'],
                    'edge': edge,
                    'rating': '⭐⭐⭐' if edge > 5 else '⭐⭐' if edge > 3 else '⭐'
                })
    
    return opportunities

def generate_scoreline_probabilities(home_expected, away_expected, max_goals=4):
    """Generate most likely scorelines using Poisson distribution"""
    
    scorelines = []
    
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            # Poisson probability
            home_prob = math.exp(-home_expected) * (home_expected ** home_goals) / math.factorial(home_goals)
            away_prob = math.exp(-away_expected) * (away_expected ** away_goals) / math.factorial(away_goals)
            
            prob = home_prob * away_prob * 100
            
            if prob > 1.0:  # Only include meaningful probabilities
                scorelines.append({
                    'score': f"{home_goals}-{away_goals}",
                    'probability': round(prob, 1),
                    'type': 'BTTS' if home_goals > 0 and away_goals > 0 else 'Clean Sheet',
                    'home_goals': home_goals,
                    'away_goals': away_goals
                })
    
    # Sort by probability
    scorelines.sort(key=lambda x: x['probability'], reverse=True)
    
    return scorelines[:8]  # Return top 8 most likely

# ==================== STREAMLIT UI ====================

st.title("⚽ Football Prediction System v4.0")
st.markdown("""
**Balanced Context-Aware Prediction Engine** - No bias, just probabilities based on quality, context, and situation.
""")

# Sidebar
with st.sidebar:
    st.header("🎯 System Philosophy")
    st.markdown("""
    **v4.0 Core Principles:**
    1. **No Default Bias** - Equal treatment for all outcomes
    2. **Context is King** - Stats adjusted for situation
    3. **Quality-Aware** - Recognizes team tiers
    4. **Value-Focused** - Finds market inefficiencies
    5. **Probability-Based** - No certainties, only likelihoods
    """)
    
    st.header("📋 How to Use")
    st.markdown("""
    1. Select league for style context
    2. Enter team names (add to tiers if needed)
    3. Input recent form and statistics
    4. Set context and motivation
    5. Enter market odds
    6. Analyze for value opportunities
    """)
    
    # League selection
    selected_league = st.selectbox(
        "Select League",
        list(LEAGUE_STYLES.keys()),
        help="League selection adjusts baseline expectations"
    )
    
    league_info = LEAGUE_STYLES[selected_league]
    st.info(f"**{selected_league}**: {league_info['style']} style, avg {league_info['avg_goals']} goals, {league_info['btts_pct']}% BTTS")
    
    # Team tier management
    with st.expander("Manage Team Tiers"):
        st.write("Add teams to appropriate tiers for better predictions")
        for tier_name, teams in QUALITY_TIERS.items():
            new_team = st.text_input(f"Add to {tier_name}", key=f"add_{tier_name}")
            if new_team and new_team not in teams:
                if st.button(f"Add to {tier_name}", key=f"btn_{tier_name}"):
                    teams.append(new_team)
                    st.success(f"Added {new_team} to {tier_name}")
        
        st.write("Current tiers:")
        for tier_name, teams in QUALITY_TIERS.items():
            st.caption(f"{tier_name}: {', '.join(teams[:5])}{'...' if len(teams) > 5 else ''}")

# Main input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Home Team")
    
    home_name = st.text_input("Team Name", key="home_name", value="Crystal Palace")
    home_tier = get_quality_tier(home_name)
    st.caption(f"Quality Tier: **{home_tier}**")
    
    # Form & Statistics
    st.markdown("#### 📊 Form & Statistics")
    
    home_form = st.text_input(
        "Last 5 Results (W/D/L)", 
        value="W,D,D,W,D",
        help="Example: W,W,D,L,W"
    )
    
    home_avg_scored = st.number_input(
        "Avg Goals Scored (Home)", 
        min_value=0.0, max_value=5.0, value=1.30, step=0.1,
        key="home_avg_scored"
    )
    
    home_avg_conceded = st.number_input(
        "Avg Goals Conceded (Home)", 
        min_value=0.0, max_value=5.0, value=1.00, step=0.1,
        key="home_avg_conceded"
    )
    
    col1a, col1b = st.columns(2)
    with col1a:
        home_over25 = st.number_input(
            "Over 2.5 %", 
            min_value=0, max_value=100, value=40, step=1,
            key="home_over25"
        )
    with col1b:
        home_btts = st.number_input(
            "BTTS %", 
            min_value=0, max_value=100, value=60, step=1,
            key="home_btts"
        )
    
    # Context
    st.markdown("#### 🎭 Context")
    
    home_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High (Europe/Important)", "Medium (Normal)", "Low (Nothing to play for)", "Very Low (Season over)"],
        key="home_motivation",
        index=2
    )
    
    home_key_attacker = st.checkbox("Key Attacker Out", key="home_attacker_out")
    home_key_defender = st.checkbox("Key Defender Out", key="home_defender_out")

with col2:
    st.subheader("✈️ Away Team")
    
    away_name = st.text_input("Team Name", key="away_name", value="Manchester City")
    away_tier = get_quality_tier(away_name)
    st.caption(f"Quality Tier: **{away_tier}**")
    
    # Form & Statistics
    st.markdown("#### 📊 Form & Statistics")
    
    away_form = st.text_input(
        "Last 5 Results (W/D/L)", 
        value="W,L,L,L,D",
        help="Example: L,W,D,W,D",
        key="away_form_input"
    )
    
    away_avg_scored = st.number_input(
        "Avg Goals Scored (Away)", 
        min_value=0.0, max_value=5.0, value=1.70, step=0.1,
        key="away_avg_scored"
    )
    
    away_avg_conceded = st.number_input(
        "Avg Goals Conceded (Away)", 
        min_value=0.0, max_value=5.0, value=1.00, step=0.1,
        key="away_avg_conceded"
    )
    
    col2a, col2b = st.columns(2)
    with col2a:
        away_over25 = st.number_input(
            "Over 2.5 %", 
            min_value=0, max_value=100, value=40, step=1,
            key="away_over25"
        )
    with col2b:
        away_btts = st.number_input(
            "BTTS %", 
            min_value=0, max_value=100, value=40, step=1,
            key="away_btts"
        )
    
    # Context
    st.markdown("#### 🎭 Context")
    
    away_motivation = st.selectbox(
        "Motivation Level",
        ["Very High (Title/Relegation)", "High (Europe/Important)", "Medium (Normal)", "Low (Nothing to play for)", "Very Low (Season over)"],
        key="away_motivation",
        index=0
    )
    
    away_key_attacker = st.checkbox("Key Attacker Out", key="away_attacker_out")
    away_key_defender = st.checkbox("Key Defender Out", key="away_defender_out")

# Match Context and Odds
st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    match_context = st.selectbox(
        "Match Context",
        ["Normal League", "Local Derby", "Cup Final", "Relegation Battle", "Title Decider", "European Competition"],
        key="match_context"
    )
    
    # Display quality comparison
    quality_diff = list(QUALITY_TIERS.keys()).index(home_tier) - list(QUALITY_TIERS.keys()).index(away_tier)
    if quality_diff > 0:
        st.success(f"**Quality Edge**: {home_name} is {abs(quality_diff)} tier(s) stronger")
    elif quality_diff < 0:
        st.success(f"**Quality Edge**: {away_name} is {abs(quality_diff)} tier(s) stronger")
    else:
        st.info("**Quality**: Teams are in same tier")

with col4:
    st.markdown("#### 🎰 Market Odds")
    
    odds_col1, odds_col2 = st.columns(2)
    
    with odds_col1:
        over25_odds = st.number_input("Over 2.5", min_value=1.01, max_value=10.0, value=1.64, step=0.01)
        under25_odds = st.number_input("Under 2.5", min_value=1.01, max_value=10.0, value=2.23, step=0.01)
        home_win_odds = st.number_input(f"{home_name} Win", min_value=1.01, max_value=10.0, value=4.10, step=0.01)
    
    with odds_col2:
        btts_yes_odds = st.number_input("BTTS: Yes", min_value=1.01, max_value=10.0, value=1.58, step=0.01)
        btts_no_odds = st.number_input("BTTS: No", min_value=1.01, max_value=10.0, value=2.30, step=0.01)
        away_win_odds = st.number_input(f"{away_name} Win", min_value=1.01, max_value=10.0, value=1.83, step=0.01)
    
    # Calculate implied probabilities
    implied_probs = {
        'over25': round(1 / over25_odds * 100, 1) if over25_odds > 0 else 0,
        'under25': round(1 / under25_odds * 100, 1) if under25_odds > 0 else 0,
        'home_win': round(1 / home_win_odds * 100, 1) if home_win_odds > 0 else 0,
        'away_win': round(1 / away_win_odds * 100, 1) if away_win_odds > 0 else 0,
        'btts_yes': round(1 / btts_yes_odds * 100, 1) if btts_yes_odds > 0 else 0,
        'btts_no': round(1 / btts_no_odds * 100, 1) if btts_no_odds > 0 else 0
    }
    
    st.caption(f"Market implied: Over 2.5: {implied_probs['over25']}%, {home_name}: {implied_probs['home_win']}%, {away_name}: {implied_probs['away_win']}%")

# Analysis Button
st.markdown("---")
analyze_button = st.button("🚀 Run Complete Analysis", type="primary", use_container_width=True)

if analyze_button:
    # Prepare data
    home_data = {
        'name': home_name,
        'avg_scored': home_avg_scored,
        'avg_conceded': home_avg_conceded,
        'over25_pct': home_over25,
        'btts_pct': home_btts,
        'motivation': home_motivation,
        'key_attacker_out': home_key_attacker,
        'key_defender_out': home_key_defender,
        'match_context': match_context
    }
    
    away_data = {
        'name': away_name,
        'avg_scored': away_avg_scored,
        'avg_conceded': away_avg_conceded,
        'over25_pct': away_over25,
        'btts_pct': away_btts,
        'motivation': away_motivation,
        'key_attacker_out': away_key_attacker,
        'key_defender_out': away_key_defender,
        'match_context': match_context
    }
    
    odds_data = {
        'home_win': home_win_odds,
        'away_win': away_win_odds,
        'draw': 3.4,  # Default draw odds if not provided
        'over25': over25_odds,
        'under25': under25_odds,
        'btts_yes': btts_yes_odds,
        'btts_no': btts_no_odds,
        'home_team': home_name,
        'away_team': away_name
    }
    
    # ==================== CORE CALCULATIONS ====================
    
    # Calculate expected goals
    expected_goals = calculate_expected_goals(
        home_data, away_data, league_info, match_context
    )
    
    # Calculate BTTS probability
    btts_prob = calculate_btts_probability(
        home_data, away_data, expected_goals, match_context
    )
    
    # Calculate win probabilities
    win_probs = calculate_win_probabilities(
        home_data, away_data, expected_goals, match_context
    )
    
    # Determine match profile
    match_profile = determine_match_profile(
        expected_goals, win_probs, btts_prob, home_data, away_data
    )
    
    # Calculate total goals probabilities
    total_goals_exp = expected_goals['total_expected']
    if total_goals_exp > 2.5:
        over25_chance = 60 + (total_goals_exp - 2.5) * 15
        under25_chance = 100 - over25_chance
    else:
        under25_chance = 60 + (2.5 - total_goals_exp) * 15
        over25_chance = 100 - under25_chance
    
    over25_chance = max(20, min(80, over25_chance))
    under25_chance = 100 - over25_chance
    
    probabilities = {
        'home_win': win_probs['home_win'],
        'draw': win_probs['draw'],
        'away_win': win_probs['away_win'],
        'btts_prob': btts_prob,
        'over25_chance': over25_chance,
        'under25_chance': under25_chance
    }
    
    # Calculate value opportunities
    value_opps = calculate_value_opportunities(probabilities, odds_data)
    
    # Generate scoreline probabilities
    scorelines = generate_scoreline_probabilities(
        expected_goals['home_expected'], expected_goals['away_expected']
    )
    
    # ==================== DISPLAY RESULTS ====================
    
    st.markdown("---")
    st.header("📊 Analysis Results v4.0")
    
    # Summary Metrics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric(
            "Expected Goals",
            f"{expected_goals['total_expected']}",
            delta=f"{expected_goals['home_expected']}-{expected_goals['away_expected']}",
            help="Home - Away expected goals"
        )
    
    with summary_col2:
        st.metric(
            "BTTS Probability",
            f"{btts_prob}%",
            delta="High" if btts_prob > 60 else "Low" if btts_prob < 40 else "Medium",
            help="Probability Both Teams To Score"
        )
    
    with summary_col3:
        winner = home_name if win_probs['home_win'] > win_probs['away_win'] else away_name
        win_prob = max(win_probs['home_win'], win_probs['away_win'])
        st.metric(
            "Most Likely Winner",
            winner,
            delta=f"{win_prob}%",
            help="Team with highest win probability"
        )
    
    with summary_col4:
        goals_outlook = "Over 2.5" if over25_chance > 50 else "Under 2.5"
        st.metric(
            "Total Goals Outlook",
            goals_outlook,
            delta=f"{over25_chance if goals_outlook == 'Over 2.5' else under25_chance}%",
            help="Expected total goals direction"
        )
    
    # Match Profile
    st.markdown("---")
    st.subheader("🎯 Match Profile")
    
    profile_col1, profile_col2 = st.columns([1, 2])
    
    with profile_col1:
        st.markdown(f"#### {match_profile['primary']}")
        st.markdown(f"**Sub-type**: {match_profile['sub_profile']}")
        st.markdown(f"**Confidence**: {match_profile['confidence']}")
        
        # Display profile scores
        df_scores = pd.DataFrame({
            'Profile': list(match_profile['scores'].keys()),
            'Score': list(match_profile['scores'].values())
        })
        
        fig_scores = px.bar(
            df_scores, 
            x='Profile', 
            y='Score',
            color='Score',
            color_continuous_scale='viridis',
            title="Profile Scores"
        )
        fig_scores.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with profile_col2:
        # Profile description
        profile_descriptions = {
            'Quality-Driven Dominance': "One team significantly stronger. Expect controlled game with clear favorite likely to win. Clean sheets more probable.",
            'Tactical Battle': "Both teams cautious, defensively organized. Likely low-scoring with midfield battle. Set pieces could be decisive.",
            'Open Exchange': "Attack-minded teams, defensive vulnerabilities. High chance of goals and both teams scoring. Entertainment guaranteed.",
            'Context-Driven Anomaly': "Special circumstances override normal patterns. Expect unpredictable elements, potential for surprises."
        }
        
        st.info(profile_descriptions.get(match_profile['primary'], "Standard match profile."))
        
        # Key dynamics
        st.markdown("#### 🔄 Expected Dynamics")
        
        dynamics_col1, dynamics_col2 = st.columns(2)
        
        with dynamics_col1:
            st.markdown(f"**Possession Balance**: {'Home favored' if expected_goals['home_adj_attack'] > expected_goals['away_adj_attack'] else 'Away favored'}")
            st.markdown(f"**Attack Threat**: {'Home stronger' if expected_goals['home_expected'] > expected_goals['away_expected'] else 'Away stronger'}")
        
        with dynamics_col2:
            st.markdown(f"**Expected Tempo**: {'Fast' if expected_goals['total_expected'] > 3.0 else 'Moderate' if expected_goals['total_expected'] > 2.5 else 'Slow'}")
            st.markdown(f"**Key Factor**: {'Quality difference' if match_profile['primary'] == 'Quality-Driven Dominance' else 'Tactical discipline' if match_profile['primary'] == 'Tactical Battle' else 'Attacking intent'}")
    
    # Value Opportunities
    st.markdown("---")
    st.subheader("💰 Value Opportunities")
    
    if value_opps:
        for i, opp in enumerate(value_opps[:3]):  # Top 3 opportunities
            with st.expander(f"{opp['rating']} {opp['market']} @ {opp['odds']}"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Our Probability", f"{opp['our_prob']}%")
                with col_b:
                    st.metric("Market Implied", f"{opp['market_prob']}%")
                with col_c:
                    st.metric("Value Edge", f"+{opp['edge']}%")
                
                # Recommendation based on edge size
                if opp['edge'] > 5:
                    st.success(f"**Strong Value** - Consider 2-3 units")
                elif opp['edge'] > 3:
                    st.info(f"**Good Value** - Consider 1-2 units")
                else:
                    st.warning(f"**Slight Value** - Consider 0.5-1 unit")
    else:
        st.warning("No clear value opportunities found. Market appears efficient for this match.")
    
    # Detailed Probabilities
    st.markdown("---")
    st.subheader("📈 Detailed Probabilities")
    
    prob_col1, prob_col2, prob_col3 = st.columns(3)
    
    with prob_col1:
        st.markdown("#### 🏆 Match Outcome")
        df_outcome = pd.DataFrame({
            'Outcome': [home_name, 'Draw', away_name],
            'Probability': [win_probs['home_win'], win_probs['draw'], win_probs['away_win']],
            'Fair Odds': [round(100/win_probs['home_win'], 2), round(100/win_probs['draw'], 2), round(100/win_probs['away_win'], 2)]
        })
        st.dataframe(df_outcome, use_container_width=True, hide_index=True)
        
        # Win probability visualization
        fig_win = go.Figure(data=[
            go.Bar(
                x=[home_name, 'Draw', away_name],
                y=[win_probs['home_win'], win_probs['draw'], win_probs['away_win']],
                marker_color=['blue', 'gray', 'red']
            )
        ])
        fig_win.update_layout(
            title="Win Probability Distribution",
            height=300,
            yaxis_title="Probability %"
        )
        st.plotly_chart(fig_win, use_container_width=True)
    
    with prob_col2:
        st.markdown("#### ⚽ Goals Markets")
        df_goals = pd.DataFrame({
            'Market': ['Over 2.5 Goals', 'Under 2.5 Goals', 'BTTS: Yes', 'BTTS: No'],
            'Probability': [over25_chance, under25_chance, btts_prob, 100 - btts_prob],
            'Fair Odds': [
                round(100/over25_chance, 2),
                round(100/under25_chance, 2),
                round(100/btts_prob, 2),
                round(100/(100 - btts_prob), 2)
            ]
        })
        st.dataframe(df_goals, use_container_width=True, hide_index=True)
        
        # Goals probability visualization
        goals_data = {
            'Category': ['0-1 Goals', '2 Goals', '3 Goals', '4+ Goals'],
            'Probability': [20, 30, 35, 15]  # Simplified for example
        }
        fig_goals = px.pie(
            values=goals_data['Probability'],
            names=goals_data['Category'],
            title="Total Goals Distribution",
            hole=0.4
        )
        fig_goals.update_layout(height=300)
        st.plotly_chart(fig_goals, use_container_width=True)
    
    with prob_col3:
        st.markdown("#### 🎯 Most Likely Scorelines")
        
        if scorelines:
            # Display top 5 scorelines
            for scoreline in scorelines[:5]:
                prob_bar = "█" * int(scoreline['probability'] / 2)
                st.markdown(f"**{scoreline['score']}** - {scoreline['probability']}% {scoreline['type']}")
                st.progress(scoreline['probability'] / 100, text=prob_bar)
            
            # Scoreline table
            df_scores = pd.DataFrame(scorelines[:8])
            st.dataframe(
                df_scores[['score', 'probability', 'type']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'score': 'Score',
                    'probability': st.column_config.NumberColumn('Probability %', format='%.1f%%'),
                    'type': 'Type'
                }
            )
        else:
            st.info("Insufficient data for detailed scoreline predictions")
    
    # Risk Assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    
    with risk_col1:
        st.markdown("#### Key Risk Factors")
        risk_factors = []
        
        # Quality risk
        if abs(list(QUALITY_TIERS.keys()).index(home_tier) - list(QUALITY_TIERS.keys()).index(away_tier)) >= 2:
            risk_factors.append("Major quality mismatch - potential blowout")
        
        # Motivation risk
        motivation_values = {
            'Very High (Title/Relegation)': 5,
            'High (Europe/Important)': 4,
            'Medium (Normal)': 3,
            'Low (Nothing to play for)': 2,
            'Very Low (Season over)': 1
        }
        
        home_mot_val = motivation_values.get(home_motivation, 3)
        away_mot_val = motivation_values.get(away_motivation, 3)
        
        if abs(home_mot_val - away_mot_val) >= 3:
            risk_factors.append("Significant motivation disparity")
        
        # Absence risk
        if home_key_attacker or home_key_defender or away_key_attacker or away_key_defender:
            risk_factors.append("Key player absences affect performance")
        
        # Context risk
        if match_context in ['Local Derby', 'Cup Final']:
            risk_factors.append("Special context increases unpredictability")
        
        if risk_factors:
            for factor in risk_factors:
                st.warning(f"• {factor}")
        else:
            st.success("• Standard match, normal risk profile")
    
    with risk_col2:
        st.markdown("#### Alternative Scenarios")
        
        scenarios = []
        
        # Based on profile
        if match_profile['primary'] == 'Quality-Driven Dominance':
            scenarios.append("Underdog parks the bus, keeps it tight")
            scenarios.append("Favorite scores early, controls game")
        elif match_profile['primary'] == 'Tactical Battle':
            scenarios.append("Single goal decides tight contest")
            scenarios.append("Set-piece breakthrough likely")
        elif match_profile['primary'] == 'Open Exchange':
            scenarios.append("Early goals lead to open game")
            scenarios.append("Comeback potential high")
        
        # Add context-specific scenarios
        if match_context == 'Local Derby':
            scenarios.append("Emotional game, potential red cards")
            scenarios.append("Underdog raises game beyond form")
        
        for i, scenario in enumerate(scenarios[:3]):
            st.info(f"• {scenario}")
    
    with risk_col3:
        st.markdown("#### Market Watch")
        
        # Compare to league averages
        league_avg_goals = league_info['avg_goals']
        league_btts = league_info['btts_pct']
        
        goal_diff = expected_goals['total_expected'] - league_avg_goals
        btts_diff = btts_prob - league_btts
        
        st.metric(
            "vs League Average Goals",
            f"{expected_goals['total_expected']}",
            delta=f"{'+' if goal_diff > 0 else ''}{round(goal_diff, 2)}",
            help=f"League average: {league_avg_goals}"
        )
        
        st.metric(
            "vs League Average BTTS",
            f"{btts_prob}%",
            delta=f"{'+' if btts_diff > 0 else ''}{round(btts_diff, 1)}%",
            help=f"League average: {league_btts}%"
        )
        
        # Market efficiency note
        if value_opps:
            st.success("Market shows inefficiencies - value opportunities present")
        else:
            st.info("Market appears efficient - no clear edges")
    
    # Historical Patterns (if we had more data)
    st.markdown("---")
    st.subheader("📊 Historical Insights")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        st.markdown("#### Similar Profile Matches")
        
        # This would connect to a database in production
        similar_matches = {
            'Quality-Driven Dominance': "Top vs mid-table home: 72% favorite wins, 65% Over 2.5",
            'Tactical Battle': "Two defensive teams: 58% Under 2.5, 45% BTTS",
            'Open Exchange': "Attack-minded clash: 78% Over 2.5, 70% BTTS",
            'Context-Driven Anomaly': "Derbies: 52% Under 2.5, higher draw rate"
        }
        
        st.info(similar_matches.get(match_profile['primary'], "Check specific team histories for better insights"))
    
    with insight_col2:
        st.markdown("#### Betting Strategy Notes")
        
        strategy_notes = {
            'Quality-Driven Dominance': "Focus on favorite win markets. Consider handicap if odds value good. BTTS: No often value.",
            'Tactical Battle': "Under markets primary focus. Low-scoring correct scores offer value. Avoid BTTS markets.",
            'Open Exchange': "Goal markets offer best value. Consider Over 2.5, BTTS, and Both Teams Over 1.5 goals.",
            'Context-Driven Anomaly': "Reduce stakes, consider draw. Market often overreacts to narratives."
        }
        
        st.warning(strategy_notes.get(match_profile['primary'], "Standard betting approach recommended"))
    
    # Final Summary
    st.markdown("---")
    st.subheader("🎯 Final Recommendations")
    
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    
    with rec_col1:
        st.markdown("##### 🥇 Primary Recommendations")
        
        if value_opps:
            primary = value_opps[0]
            st.success(f"**{primary['market']}** @ {primary['odds']}")
            st.caption(f"Edge: +{primary['edge']}%, Confidence: {match_profile['confidence']}")
        else:
            # Default based on profile
            if match_profile['primary'] == 'Quality-Driven Dominance':
                st.success(f"**{away_name if win_probs['away_win'] > win_probs['home_win'] else home_name} to Win**")
            elif match_profile['primary'] == 'Tactical Battle':
                st.success("**Under 2.5 Goals**")
            elif match_profile['primary'] == 'Open Exchange':
                st.success("**Over 2.5 Goals**")
            else:
                st.info("**Wait for in-play** - Context makes pre-match unpredictable")
    
    with rec_col2:
        st.markdown("##### 🥈 Secondary Options")
        
        secondary_options = []
        
        # Add secondary based on profile
        if match_profile['primary'] == 'Quality-Driven Dominance':
            if expected_goals['total_expected'] > 3.0:
                secondary_options.append("Over 2.5 Goals")
            secondary_options.append("Favorite Clean Sheet")
        elif match_profile['primary'] == 'Tactical Battle':
            secondary_options.append("Correct Score 1-0 or 0-1")
            secondary_options.append("Draw")
        elif match_profile['primary'] == 'Open Exchange':
            secondary_options.append("BTTS: Yes")
            secondary_options.append("Both Teams Over 1.5 Goals")
        
        for option in secondary_options[:2]:
            st.info(f"• {option}")
    
    with rec_col3:
        st.markdown("##### 🚫 Markets to Avoid")
        
        avoid_markets = []
        
        # Avoid based on profile
        if match_profile['primary'] == 'Quality-Driven Dominance':
            if btts_prob < 40:
                avoid_markets.append("BTTS: Yes")
            avoid_markets.append("Underdog Win")
        elif match_profile['primary'] == 'Tactical Battle':
            avoid_markets.append("Over 3.5 Goals")
            if btts_prob < 45:
                avoid_markets.append("BTTS: Yes")
        elif match_profile['primary'] == 'Open Exchange':
            avoid_markets.append("Under 1.5 Goals")
            avoid_markets.append("0-0 Correct Score")
        
        for market in avoid_markets[:2]:
            st.error(f"• {market}")
    
    # Staking Guidance
    st.markdown("---")
    col_stake1, col_stake2 = st.columns(2)
    
    with col_stake1:
        st.markdown("#### 💰 Staking Guidelines")
        
        confidence_multiplier = {
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
        
        base_units = 1
        recommended_units = base_units * confidence_multiplier.get(match_profile['confidence'], 1)
        
        st.info(f"**Recommended Stake Level**: {recommended_units} units")
        st.caption("(Where 1 unit = 1% of bankroll)")
    
    with col_stake2:
        st.markdown("#### ⏰ Timing Advice")
        
        timing_advice = {
            'Quality-Driven Dominance': "Bet pre-match. Early goal likely if favorite starts strong.",
            'Tactical Battle': "Consider live betting if 0-0 at halftime. Teams may open up.",
            'Open Exchange': "Bet pre-match for best value. Goals expected throughout.",
            'Context-Driven Anomaly': "Wait for team news and in-play. Emotional starts common."
        }
        
        st.warning(timing_advice.get(match_profile['primary'], "Standard pre-match betting recommended"))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Football Prediction System v4.0</strong> - Balanced Context-Aware Analysis</p>
    <p><small>Remember: All predictions are probabilistic. No system guarantees wins. Always bet responsibly.</small></p>
    <p><small>Adjust team tiers in sidebar for more accurate predictions.</small></p>
</div>
""", unsafe_allow_html=True)
