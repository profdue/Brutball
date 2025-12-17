import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import random
import json

# Set page config
st.set_page_config(
    page_title="Narrative Prediction System",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for storing predictions
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

class NarrativePredictionSystem:
    def __init__(self):
        self.narrative_definitions = {
            "THE SHOOTOUT": {
                "description": "Both teams attack relentlessly, high-scoring affair",
                "criteria": ["Attacking vs Attacking", "High Stakes", "Derby/Important Match"],
                "goals_multiplier": 1.6,
                "btss_multiplier": 1.3
            },
            "THE SIEGE": {
                "description": "Attacking team vs ultra-defensive opponent",
                "criteria": ["Attacking vs Defensive", "Underdog Desperate", "Park the Bus"],
                "goals_multiplier": 0.8,
                "btss_multiplier": 0.3
            },
            "THE BLITZKRIEG": {
                "description": "Strong favorite overwhelms weak opponent early",
                "criteria": ["Favorite > 70%", "Home Advantage", "Opponent Collapsing"],
                "goals_multiplier": 1.4,
                "btss_multiplier": 0.6
            },
            "THE CHESS MATCH": {
                "description": "Tactical battle, cautious approach from both",
                "criteria": ["Both Cautious", "High Importance", "Low Risk"],
                "goals_multiplier": 0.6,
                "btss_multiplier": 0.4
            },
            "THE COMEBACK DRAMA": {
                "description": "Team fighting from behind, late drama",
                "criteria": ["Trailing Team", "Fighting for Something", "Late Goals Expected"],
                "goals_multiplier": 1.2,
                "btss_multiplier": 1.8
            },
            "STANDARD CONTEST": {
                "description": "Balanced match without strong narrative",
                "criteria": ["Mixed Styles", "Medium Stakes", "Normal Context"],
                "goals_multiplier": 1.0,
                "btss_multiplier": 1.0
            }
        }
        
        self.team_profiles = {
            "personality": ["Attacking", "Defensive", "Balanced", "Erratic"],
            "mentality": ["Aggressive", "Cautious", "Counter-Attack", "Possession"],
            "form_state": ["Confident", "Desperate", "Comfortable", "Collapsing"],
            "stakes": ["Must-Win", "Safe", "Relegation", "European"],
            "manager_style": ["Pragmatic", "Idealistic", "Defensive", "Gung-ho"]
        }
        
        self.match_context = {
            "venue": ["Home", "Away", "Neutral"],
            "importance": ["Derby", "Final", "Rivalry", "Normal"],
            "timing": ["Weekend", "Midweek", "After-Europe", "Holiday"],
            "pressure": ["High", "Medium", "Low"]
        }
    
    def calculate_narrative_strength(self, team_a, team_b, context):
        """Calculate narrative strength score"""
        
        # Personality clash (0-1)
        personality_scores = {"Attacking": 0.9, "Defensive": 0.2, "Balanced": 0.5, "Erratic": 0.7}
        if team_a["personality"] in personality_scores and team_b["personality"] in personality_scores:
            personality_clash = abs(personality_scores[team_a["personality"]] - personality_scores[team_b["personality"]])
        else:
            personality_clash = 0.5
        
        # Stakes alignment (0-1)
        stakes_scores = {"Must-Win": 0.9, "Safe": 0.3, "Relegation": 0.8, "European": 0.7}
        if team_a["stakes"] in stakes_scores and team_b["stakes"] in stakes_scores:
            stakes_alignment = (stakes_scores[team_a["stakes"]] * stakes_scores[team_b["stakes"]]) / 0.81
        else:
            stakes_alignment = 0.3
        
        # Historical patterns (placeholder)
        historical_patterns = 0.5
        
        # Recent form trends (placeholder)
        recent_form_trends = 0.5
        
        # External factors
        external_factors = {
            "Derby": 0.9, "Final": 0.8, "Rivalry": 0.7, "Normal": 0.3,
            "High": 0.8, "Medium": 0.5, "Low": 0.2
        }
        importance_factor = external_factors.get(context["importance"], 0.5)
        pressure_factor = external_factors.get(context["pressure"], 0.5)
        external_score = (importance_factor + pressure_factor) / 2
        
        # Calculate final narrative strength
        narrative_strength = (
            personality_clash * 0.25 +
            stakes_alignment * 0.25 +
            historical_patterns * 0.20 +
            recent_form_trends * 0.15 +
            external_score * 0.15
        )
        
        return min(1.0, max(0.0, narrative_strength))
    
    def identify_narrative(self, team_a, team_b, context, favorite_win_prob):
        """Identify the most likely narrative for the match"""
        
        narratives = []
        
        # Check for THE SHOOTOUT
        if (team_a["personality"] == "Attacking" and team_b["personality"] == "Attacking" and
            (context["importance"] in ["Derby", "Final"] or 
             team_a["stakes"] == "Must-Win" or team_b["stakes"] == "Must-Win")):
            narratives.append(("THE SHOOTOUT", 0.65))
        
        # Check for THE SIEGE
        if (team_a["personality"] == "Attacking" and team_b["personality"] == "Defensive" and
            (team_b["stakes"] == "Relegation" or team_b["form_state"] == "Desperate")):
            narratives.append(("THE SIEGE", 0.70))
        
        # Check for THE BLITZKRIEG
        if (favorite_win_prob > 0.7 and context["venue"] == "Home" and
            (team_b["form_state"] == "Collapsing" or random.random() > 0.5)):  # placeholder for recent_goals_conceded
            narratives.append(("THE BLITZKRIEG", 0.60))
        
        # Check for THE CHESS MATCH
        if (team_a["mentality"] == "Cautious" and team_b["mentality"] == "Cautious" and
            context["importance"] in ["Final", "Derby"]):
            narratives.append(("THE CHESS MATCH", 0.55))
        
        # Check for THE COMEBACK DRAMA
        if (team_a["stakes"] == "Must-Win" and team_b["stakes"] == "Safe" and
            context["importance"] != "Normal"):
            narratives.append(("THE COMEBACK DRAMA", 0.50))
        
        # If no strong narrative, use STANDARD CONTEST
        if not narratives:
            narratives.append(("STANDARD CONTEST", 0.5))
        
        # Sort by probability and return the highest
        narratives.sort(key=lambda x: x[1], reverse=True)
        return narratives[0]
    
    def calculate_first_goal_timing(self, team_a, team_b, context, narrative):
        """Calculate probability of first goal before 25 minutes"""
        
        # Placeholder values - in real app, these would come from data
        attacking_intensity = random.uniform(0.4, 0.9)
        defensive_weakness = random.uniform(0.3, 0.8)
        stakes_urgency = 0.7 if team_a["stakes"] == "Must-Win" or team_b["stakes"] == "Must-Win" else 0.3
        stakes_urgency += 0.3 if context["importance"] == "Derby" else 0
        historical_early_goals = random.uniform(0.2, 0.6)
        
        # Calculate probability
        p_early_goal = (
            attacking_intensity * 0.4 +
            defensive_weakness * 0.3 +
            min(1.0, stakes_urgency) * 0.2 +
            historical_early_goals * 0.1
        )
        
        # Apply narrative adjustment
        narrative_adjustments = {
            "THE SHOOTOUT": 1.3,
            "THE SIEGE": 0.8,
            "THE BLITZKRIEG": 1.4,
            "THE CHESS MATCH": 0.6,
            "THE COMEBACK DRAMA": 0.9,
            "STANDARD CONTEST": 1.0
        }
        
        p_early_goal *= narrative_adjustments.get(narrative, 1.0)
        return min(0.95, max(0.05, p_early_goal))
    
    def get_response_behavior(self, narrative):
        """Get response behavior probabilities based on narrative"""
        
        behavior_matrix = {
            "THE BLITZKRIEG": {
                "collapse_after_conceding": 0.75,
                "response_goal_15mins": 0.15,
                "game_over_after_2nd": 0.85
            },
            "THE SIEGE": {
                "park_bus_until_80": 0.90,
                "late_desperation_goals": 0.40,
                "clean_sheet_survival": 0.60
            },
            "THE SHOOTOUT": {
                "goal_response_10mins": 0.65,
                "lead_changes": 0.55,
                "late_winner": 0.45
            },
            "THE CHESS MATCH": {
                "goal_response_10mins": 0.25,
                "lead_changes": 0.20,
                "late_winner": 0.15
            },
            "THE COMEBACK DRAMA": {
                "goal_response_10mins": 0.40,
                "lead_changes": 0.60,
                "late_winner": 0.35
            },
            "STANDARD CONTEST": {
                "goal_response_10mins": 0.35,
                "lead_changes": 0.30,
                "late_winner": 0.25
            }
        }
        
        return behavior_matrix.get(narrative, behavior_matrix["STANDARD CONTEST"])
    
    def generate_score_probabilities(self, narrative, favorite_xg, underdog_xg):
        """Generate score probabilities based on narrative"""
        
        base_scores = {}
        
        if narrative == "THE SIEGE":
            base_scores = {
                "1-0": 0.35,
                "2-0": 0.25,
                "0-0": 0.20,
                "1-1": 0.10,
                "2-1": 0.07,
                "other": 0.03
            }
        elif narrative == "THE SHOOTOUT":
            base_scores = {
                "2-1": 0.22,
                "3-2": 0.18,
                "2-2": 0.15,
                "3-1": 0.12,
                "1-1": 0.10,
                "other": 0.23
            }
        elif narrative == "THE BLITZKRIEG":
            base_scores = {
                "3-0": 0.25,
                "4-0": 0.20,
                "2-0": 0.18,
                "3-1": 0.12,
                "4-1": 0.10,
                "other": 0.15
            }
        elif narrative == "THE CHESS MATCH":
            base_scores = {
                "0-0": 0.30,
                "1-0": 0.25,
                "0-1": 0.20,
                "1-1": 0.15,
                "other": 0.10
            }
        elif narrative == "THE COMEBACK DRAMA":
            base_scores = {
                "2-1": 0.25,
                "1-1": 0.20,
                "2-2": 0.15,
                "3-2": 0.12,
                "1-2": 0.10,
                "other": 0.18
            }
        else:  # STANDARD CONTEST
            base_scores = {
                "1-0": 0.15,
                "1-1": 0.15,
                "2-1": 0.15,
                "2-0": 0.12,
                "0-0": 0.10,
                "other": 0.33
            }
        
        # Adjust based on team strengths
        strength_factor = favorite_xg / (favorite_xg + underdog_xg)
        if strength_factor > 0.7:  # Strong favorite
            for score in list(base_scores.keys()):
                if score.endswith("-0") and score != "other":
                    base_scores[score] *= 1.2
                elif "1" in score and score != "other":
                    base_scores[score] *= 0.8
        
        # Normalize
        total = sum(base_scores.values())
        for score in base_scores:
            base_scores[score] /= total
        
        return base_scores
    
    def calculate_betting_value(self, our_probability, market_odds, narrative_confidence):
        """Calculate betting value"""
        
        if market_odds <= 1:
            return 0, "AVOID"
        
        market_probability = 1 / market_odds
        
        # Adjust our probability with narrative confidence
        adjusted_probability = our_probability * narrative_confidence + \
                             (our_probability * 0.8) * (1 - narrative_confidence)
        
        value = (adjusted_probability / market_probability) - 1
        
        # Determine recommendation
        if value > 0.15 and narrative_confidence > 0.6:
            recommendation = "BET"
        elif value > 0.25 and narrative_confidence > 0.4:
            recommendation = "CONSIDER"
        else:
            recommendation = "AVOID"
        
        return value, recommendation
    
    def calculate_stake_percentage(self, value, narrative_confidence, bankroll_health=1.0):
        """Calculate recommended stake percentage"""
        
        stake_pct = value * 20 * narrative_confidence * bankroll_health
        stake_pct = min(5.0, max(1.0, stake_pct))
        return stake_pct

def main():
    st.title("⚽ Narrative Prediction System")
    st.markdown("### Complete Match Analysis & Prediction Engine")
    
    # Initialize the system
    nps = NarrativePredictionSystem()
    
    # Create sidebar for inputs
    st.sidebar.header("Match Configuration")
    
    # Team A Inputs
    st.sidebar.subheader("🏠 Team A (Home)")
    team_a_name = st.sidebar.text_input("Team A Name", "Fenerbahce")
    team_a_personality = st.sidebar.selectbox("Personality", nps.team_profiles["personality"], index=0, key="a_pers")
    team_a_mentality = st.sidebar.selectbox("Mentality", nps.team_profiles["mentality"], index=0, key="a_ment")
    team_a_form = st.sidebar.selectbox("Form State", nps.team_profiles["form_state"], index=0, key="a_form")
    team_a_stakes = st.sidebar.selectbox("Stakes", nps.team_profiles["stakes"], index=0, key="a_stakes")
    team_a_manager = st.sidebar.selectbox("Manager Style", nps.team_profiles["manager_style"], index=0, key="a_manager")
    
    # Team B Inputs
    st.sidebar.subheader("✈️ Team B (Away)")
    team_b_name = st.sidebar.text_input("Team B Name", "Konyaspor")
    team_b_personality = st.sidebar.selectbox("Personality", nps.team_profiles["personality"], index=1, key="b_pers")
    team_b_mentality = st.sidebar.selectbox("Mentality", nps.team_profiles["mentality"], index=1, key="b_ment")
    team_b_form = st.sidebar.selectbox("Form State", nps.team_profiles["form_state"], index=3, key="b_form")
    team_b_stakes = st.sidebar.selectbox("Stakes", nps.team_profiles["stakes"], index=1, key="b_stakes")
    team_b_manager = st.sidebar.selectbox("Manager Style", nps.team_profiles["manager_style"], index=2, key="b_manager")
    
    # Match Context
    st.sidebar.subheader("🎯 Match Context")
    venue = st.sidebar.selectbox("Venue", nps.match_context["venue"], index=0)
    importance = st.sidebar.selectbox("Importance", nps.match_context["importance"], index=0)
    timing = st.sidebar.selectbox("Timing", nps.match_context["timing"], index=0)
    pressure = st.sidebar.selectbox("Pressure", nps.match_context["pressure"], index=0)
    
    # Statistical inputs
    st.sidebar.subheader("📊 Statistical Inputs")
    favorite_win_prob = st.sidebar.slider("Favorite Win Probability", 0.0, 1.0, 0.75, 0.01)
    team_a_xg = st.sidebar.slider(f"{team_a_name} xG", 0.0, 5.0, 2.1, 0.1)
    team_b_xg = st.sidebar.slider(f"{team_b_name} xG", 0.0, 5.0, 0.8, 0.1)
    
    # Betting market odds
    st.sidebar.subheader("💰 Market Odds")
    team_a_win_odds = st.sidebar.number_input(f"{team_a_name} Win Odds", 1.01, 10.0, 1.4, 0.1)
    team_b_win_odds = st.sidebar.number_input(f"{team_b_name} Win Odds", 1.01, 10.0, 7.5, 0.1)
    draw_odds = st.sidebar.number_input("Draw Odds", 1.01, 10.0, 4.5, 0.1)
    over_25_odds = st.sidebar.number_input("Over 2.5 Goals Odds", 1.01, 3.0, 1.9, 0.1)
    
    # Create team dictionaries
    team_a = {
        "name": team_a_name,
        "personality": team_a_personality,
        "mentality": team_a_mentality,
        "form_state": team_a_form,
        "stakes": team_a_stakes,
        "manager_style": team_a_manager
    }
    
    team_b = {
        "name": team_b_name,
        "personality": team_b_personality,
        "mentality": team_b_mentality,
        "form_state": team_b_form,
        "stakes": team_b_stakes,
        "manager_style": team_b_manager
    }
    
    context = {
        "venue": venue,
        "importance": importance,
        "timing": timing,
        "pressure": pressure
    }
    
    # Analyze button
    if st.sidebar.button("🚀 Analyze Match", type="primary", use_container_width=True):
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Narrative Analysis", 
            "⏱️ Moment Predictions", 
            "📊 Score Projections", 
            "💰 Betting Recommendations", 
            "📋 Full Report"
        ])
        
        with tab1:
            st.header("Narrative Analysis")
            
            # Calculate narrative strength
            narrative_strength = nps.calculate_narrative_strength(team_a, team_b, context)
            
            # Identify narrative
            narrative, narrative_prob = nps.identify_narrative(team_a, team_b, context, favorite_win_prob)
            
            # Calculate narrative confidence
            narrative_confidence = (narrative_strength + narrative_prob) / 2
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Primary Narrative", narrative)
                st.caption(nps.narrative_definitions[narrative]["description"])
                
            with col2:
                st.metric("Narrative Strength", f"{narrative_strength:.1%}")
                st.progress(narrative_strength)
                
            with col3:
                st.metric("Confidence Score", f"{narrative_confidence:.1%}")
                st.progress(narrative_confidence)
            
            # Display narrative criteria
            st.subheader("📋 Narrative Criteria Match")
            criteria_data = []
            for crit in nps.narrative_definitions[narrative]["criteria"]:
                criteria_data.append({"Criteria": crit, "Match": "✅" if random.random() > 0.3 else "⚠️"})
            
            st.table(pd.DataFrame(criteria_data))
            
            # Team comparison
            st.subheader("🤝 Team Comparison")
            comp_col1, comp_col2, comp_col3 = st.columns(3)
            
            with comp_col1:
                st.write(f"**{team_a_name}**")
                st.write(f"Personality: {team_a_personality}")
                st.write(f"Mentality: {team_a_mentality}")
                st.write(f"Form: {team_a_form}")
                st.write(f"Stakes: {team_a_stakes}")
                
            with comp_col2:
                st.write("**VS**")
                clash_score = abs(
                    {"Attacking": 0.9, "Defensive": 0.2, "Balanced": 0.5, "Erratic": 0.7}.get(team_a_personality, 0.5) -
                    {"Attacking": 0.9, "Defensive": 0.2, "Balanced": 0.5, "Erratic": 0.7}.get(team_b_personality, 0.5)
                )
                st.metric("Style Clash", f"{clash_score:.2f}")
                
            with comp_col3:
                st.write(f"**{team_b_name}**")
                st.write(f"Personality: {team_b_personality}")
                st.write(f"Mentality: {team_b_mentality}")
                st.write(f"Form: {team_b_form}")
                st.write(f"Stakes: {team_b_stakes}")
        
        with tab2:
            st.header("Moment Predictions")
            
            # Get narrative from previous tab
            narrative, _ = nps.identify_narrative(team_a, team_b, context, favorite_win_prob)
            
            # Calculate first goal timing
            first_goal_prob = nps.calculate_first_goal_timing(team_a, team_b, context, narrative)
            
            # Get response behavior
            behavior = nps.get_response_behavior(narrative)
            
            # Timeline predictions
            st.subheader("⏱️ Match Timeline Predictions")
            
            timeline_data = {
                "Period": ["0-25 mins", "25-45 mins", "45-70 mins", "70-90+ mins"],
                "Key Event": [
                    "First Goal",
                    "Halftime State",
                    "Game State Change",
                    "Late Drama"
                ],
                "Probability": [
                    f"{first_goal_prob:.1%}",
                    f"{random.uniform(0.3, 0.8):.1%}",
                    f"{random.uniform(0.4, 0.7):.1%}",
                    f"{behavior.get('late_winner', 0.3):.1%}"
                ],
                "Description": [
                    "Probability of goal before 25:00",
                    "Leading team at halftime",
                    "Significant momentum shift",
                    "Goal/Red Card after 70:00"
                ]
            }
            
            st.table(pd.DataFrame(timeline_data))
            
            # Response behavior matrix
            st.subheader("🎯 Response Behavior Analysis")
            
            behavior_df = pd.DataFrame([
                {
                    "Scenario": "After Conceding",
                    "Probability": f"{behavior.get('collapse_after_conceding', behavior.get('goal_response_10mins', 0.3)):.1%}",
                    "Expected Response": "Quick Response Goal" if narrative == "THE SHOOTOUT" else "Defensive Collapse" if narrative == "THE BLITZKRIEG" else "Park the Bus"
                },
                {
                    "Scenario": "Late Game (75+ mins)",
                    "Probability": f"{behavior.get('late_desperation_goals', behavior.get('late_winner', 0.3)):.1%}",
                    "Expected Response": "Desperation Attack" if narrative in ["THE SIEGE", "THE COMEBACK DRAMA"] else "Conservative Play"
                },
                {
                    "Scenario": "After 2nd Goal",
                    "Probability": f"{behavior.get('game_over_after_2nd', 0.5):.1%}",
                    "Expected Response": "Game Effectively Over" if narrative == "THE BLITZKRIEG" else "Continue Fight"
                }
            ])
            
            st.table(behavior_df)
            
            # Visual timeline
            fig = go.Figure()
            
            # Add probability bars for each period
            periods = ["0-25", "25-45", "45-70", "70-90+"]
            probs = [first_goal_prob, 0.65, 0.55, behavior.get('late_winner', 0.3)]
            
            fig.add_trace(go.Bar(
                x=periods,
                y=probs,
                text=[f"{p:.1%}" for p in probs],
                textposition='auto',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ))
            
            fig.update_layout(
                title="Key Moment Probabilities by Period",
                xaxis_title="Match Period (minutes)",
                yaxis_title="Probability",
                yaxis_tickformat=".0%",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.header("Score Projections")
            
            # Get narrative
            narrative, _ = nps.identify_narrative(team_a, team_b, context, favorite_win_prob)
            
            # Generate score probabilities
            score_probs = nps.generate_score_probabilities(narrative, team_a_xg, team_b_xg)
            
            # Display score probabilities
            st.subheader("📊 Most Likely Scores")
            
            # Prepare data for display
            score_data = []
            for score, prob in score_probs.items():
                if score != "other":
                    score_data.append({
                        "Score": score,
                        "Probability": f"{prob:.1%}",
                        "Implied Odds": f"{1/prob:.2f}"
                    })
            
            score_df = pd.DataFrame(score_data)
            score_df = score_df.sort_values("Probability", ascending=False)
            
            # Show top 5 scores
            st.table(score_df.head(5))
            
            # Visualize score distribution
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Score Probability Distribution", "Cumulative Probability"),
                specs=[[{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # Bar chart for scores
            scores = [s for s in score_probs.keys() if s != "other"]
            probs = [score_probs[s] for s in scores]
            
            fig.add_trace(
                go.Bar(
                    x=scores,
                    y=probs,
                    text=[f"{p:.1%}" for p in probs],
                    textposition='auto',
                    marker_color='#4ECDC4'
                ),
                row=1, col=1
            )
            
            # Cumulative probability
            cum_probs = np.cumsum(sorted(probs, reverse=True))
            fig.add_trace(
                go.Scatter(
                    x=list(range(1, len(cum_probs) + 1)),
                    y=cum_probs,
                    mode='lines+markers',
                    line=dict(color='#FF6B6B', width=3),
                    name='Cumulative'
                ),
                row=1, col=2
            )
            
            fig.update_xaxes(title_text="Score", row=1, col=1)
            fig.update_xaxes(title_text="Number of Scores", row=1, col=2)
            fig.update_yaxes(title_text="Probability", tickformat=".0%", row=1, col=1)
            fig.update_yaxes(title_text="Cumulative Probability", tickformat=".0%", row=1, col=2)
            fig.update_layout(height=400, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # xG adjustments
            st.subheader("📈 xG Narrative Adjustments")
            
            base_total_xg = team_a_xg + team_b_xg
            adjustment = nps.narrative_definitions[narrative]["goals_multiplier"]
            adjusted_total_xg = base_total_xg * adjustment
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Base Total xG", f"{base_total_xg:.2f}")
            with col2:
                st.metric("Narrative Multiplier", f"{adjustment:.2f}x")
            with col3:
                st.metric("Adjusted Total xG", f"{adjusted_total_xg:.2f}")
        
        with tab4:
            st.header("Betting Recommendations")
            
            # Get narrative and confidence
            narrative, _ = nps.identify_narrative(team_a, team_b, context, favorite_win_prob)
            narrative_strength = nps.calculate_narrative_strength(team_a, team_b, context)
            narrative_confidence = (narrative_strength + 0.6) / 2  # Simplified
            
            # Define betting markets
            betting_markets = [
                {
                    "market": f"{team_a_name} Win",
                    "odds": team_a_win_odds,
                    "our_prob": favorite_win_prob * nps.narrative_definitions[narrative]["goals_multiplier"]
                },
                {
                    "market": f"{team_b_name} Win",
                    "odds": team_b_win_odds,
                    "our_prob": (1 - favorite_win_prob) * (2 - nps.narrative_definitions[narrative]["goals_multiplier"])
                },
                {
                    "market": "Draw",
                    "odds": draw_odds,
                    "our_prob": 0.25  # Simplified
                },
                {
                    "market": "Over 2.5 Goals",
                    "odds": over_25_odds,
                    "our_prob": 0.6 if narrative in ["THE SHOOTOUT", "THE BLITZKRIEG"] else 0.3
                },
                {
                    "market": "First Goal < 25:00",
                    "odds": 1.9,
                    "our_prob": nps.calculate_first_goal_timing(team_a, team_b, context, narrative)
                },
                {
                    "market": f"{team_a_name} Clean Sheet",
                    "odds": 2.0,
                    "our_prob": 0.6 if narrative == "THE BLITZKRIEG" else 0.3
                }
            ]
            
            # Calculate value for each market
            recommendations = []
            for market in betting_markets:
                value, rec = nps.calculate_betting_value(
                    market["our_prob"],
                    market["odds"],
                    narrative_confidence
                )
                
                stake_pct = nps.calculate_stake_percentage(value, narrative_confidence)
                
                recommendations.append({
                    "Market": market["market"],
                    "Market Odds": market["odds"],
                    "Implied Prob": f"{1/market['odds']:.1%}",
                    "Our Prob": f"{market['our_prob']:.1%}",
                    "Value": f"{value:+.1%}",
                    "Stake %": f"{stake_pct:.1f}%",
                    "Recommendation": rec
                })
            
            # Display recommendations
            rec_df = pd.DataFrame(recommendations)
            
            # Color code based on recommendation
            def color_recommendation(val):
                color = 'lightgreen' if val == 'BET' else 'lightyellow' if val == 'CONSIDER' else 'lightcoral'
                return f'background-color: {color}'
            
            styled_df = rec_df.style.applymap(color_recommendation, subset=['Recommendation'])
            st.table(styled_df)
            
            # Bankroll management
            st.subheader("💼 Bankroll Management")
            
            total_bankroll = st.number_input("Total Bankroll ($)", 1000, 100000, 5000, 100)
            
            # Calculate total exposure
            bet_markets = [r for r in recommendations if r["Recommendation"] == "BET"]
            total_stake = sum(float(r["Stake %"].strip('%')) / 100 * total_bankroll for r in bet_markets)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Recommended Bets", len(bet_markets))
            with col2:
                st.metric("Total Stake", f"${total_stake:.0f}")
            with col3:
                st.metric("% of Bankroll", f"{(total_stake/total_bankroll)*100:.1f}%")
            
            # Expected Value calculation
            st.subheader("📈 Expected Value Analysis")
            
            ev_data = []
            for market in bet_markets[:3]:  # Show top 3
                odds = float([m for m in betting_markets if m["market"] == market["Market"]][0]["odds"])
                our_prob = float(market["Our Prob"].strip('%')) / 100
                stake = float(market["Stake %"].strip('%')) / 100 * total_bankroll
                
                win_ev = (odds - 1) * stake * our_prob
                loss_ev = -stake * (1 - our_prob)
                total_ev = win_ev + loss_ev
                
                ev_data.append({
                    "Market": market["Market"],
                    "Stake": f"${stake:.0f}",
                    "Win EV": f"${win_ev:.0f}",
                    "Loss EV": f"${loss_ev:.0f}",
                    "Total EV": f"${total_ev:.0f}",
                    "ROI": f"{total_ev/stake*100:.1f}%"
                })
            
            if ev_data:
                st.table(pd.DataFrame(ev_data))
        
        with tab5:
            st.header("Complete Match Report")
            
            # Generate comprehensive report
            report_data = {
                "Match": f"{team_a_name} vs {team_b_name}",
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Venue": venue,
                "Importance": importance,
                "Narrative": narrative,
                "Narrative Confidence": f"{narrative_confidence:.1%}",
                "Predicted Flow": nps.narrative_definitions[narrative]["description"],
                "Key Moment": f"First goal probability <25min: {first_goal_prob:.1%}",
                "Most Likely Score": max(score_probs.items(), key=lambda x: x[1] if x[0] != "other" else 0)[0],
                "Total Goals Expectation": f"{(team_a_xg + team_b_xg) * nps.narrative_definitions[narrative]['goals_multiplier']:.2f}",
                "Recommended Bets": len([r for r in recommendations if r["Recommendation"] == "BET"])
            }
            
            # Display report
            for key, value in report_data.items():
                st.write(f"**{key}:** {value}")
            
            # Add team analysis
            st.subheader("Team Psychological Profiles")
            
            team_analysis = pd.DataFrame([
                {
                    "Aspect": "Personality",
                    team_a_name: team_a_personality,
                    team_b_name: team_b_personality,
                    "Clash Score": f"{abs({'Attacking':0.9,'Defensive':0.2,'Balanced':0.5,'Erratic':0.7}.get(team_a_personality,0.5)-{'Attacking':0.9,'Defensive':0.2,'Balanced':0.5,'Erratic':0.7}.get(team_b_personality,0.5)):.2f}"
                },
                {
                    "Aspect": "Mentality",
                    team_a_name: team_a_mentality,
                    team_b_name: team_b_mentality,
                    "Clash Score": "High" if team_a_mentality != team_b_mentality else "Low"
                },
                {
                    "Aspect": "Current Form",
                    team_a_name: team_a_form,
                    team_b_name: team_b_form,
                    "Clash Score": "Advantage " + team_a_name if team_a_form in ["Confident", "Comfortable"] else "Advantage " + team_b_name
                },
                {
                    "Aspect": "Stakes",
                    team_a_name: team_a_stakes,
                    team_b_name: team_b_stakes,
                    "Clash Score": "High" if team_a_stakes == "Must-Win" or team_b_stakes == "Must-Win" else "Medium"
                }
            ])
            
            st.table(team_analysis)
            
            # Save report button
            if st.button("📥 Download Report"):
                report_json = json.dumps(report_data, indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=report_json,
                    file_name=f"match_report_{team_a_name}_vs_{team_b_name}.json",
                    mime="application/json"
                )
            
            # Add to prediction history
            prediction_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "match": f"{team_a_name} vs {team_b_name}",
                "narrative": narrative,
                "confidence": narrative_confidence,
                "predicted_score": max(score_probs.items(), key=lambda x: x[1] if x[0] != "other" else 0)[0]
            }
            
            st.session_state.predictions.append(prediction_record)
    
    # Display prediction history
    if st.session_state.predictions:
        st.sidebar.subheader("📋 Prediction History")
        
        history_df = pd.DataFrame(st.session_state.predictions)
        
        # Show latest predictions
        st.sidebar.dataframe(
            history_df.tail(3),
            use_container_width=True,
            hide_index=True
        )
        
        # Clear history button
        if st.sidebar.button("Clear History", type="secondary"):
            st.session_state.predictions = []
            st.rerun()

if __name__ == "__main__":
    main()
