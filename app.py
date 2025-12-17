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
    page_title="Narrative Prediction System v2",
    page_icon="📊",
    layout="wide"
)

class NarrativePredictionSystem:
    def __init__(self):
        # Detailed narrative archetypes with testable criteria
        self.narrative_definitions = {
            "THE BLITZKRIEG (Early Domination)": {
                "description": "Heavy favorite dominates early, opponent collapses",
                "criteria": {
                    "favorite_win_prob": 0.65,
                    "home_scored_first_pct": 0.70,
                    "opponent_concedes_early_pct": 0.60,
                    "stakes_mismatch": True
                },
                "outcome_patterns": {
                    "early_goal_prob": 0.70,
                    "halftime_lead_prob": 0.80,
                    "clean_sheet_prob": 0.60,
                    "common_scores": ["3-0", "4-0", "2-0"],
                    "btts_prob": 0.30,
                    "over_25_prob": 0.60
                }
            },
            "THE SIEGE (Attack vs Defense)": {
                "description": "Attacker frustrates against parked bus",
                "criteria": {
                    "home_avg_shots": 15,
                    "away_avg_possession": 40,
                    "stakes_mismatch": True,
                    "away_poor_record": True
                },
                "outcome_patterns": {
                    "low_total_goals_prob": 0.70,
                    "late_goal_prob": 0.40,
                    "common_scores": ["1-0", "0-0", "2-0"],
                    "btts_prob": 0.20,
                    "over_25_prob": 0.30
                }
            },
            "THE SHOOTOUT (End-to-End Chaos)": {
                "description": "Both teams attack relentlessly, high-scoring chaos",
                "criteria": {
                    "both_btts_pct": 0.65,
                    "both_over_25_pct": 0.60,
                    "both_attack_minded": True,
                    "both_weak_defense": 1.5,
                    "high_stakes_both": True
                },
                "outcome_patterns": {
                    "early_goal_prob": 0.60,
                    "lead_changes_prob": 0.40,
                    "late_drama_prob": 0.50,
                    "common_scores": ["2-1", "3-2", "2-2", "3-1"],
                    "btts_prob": 0.75,
                    "over_25_prob": 0.85
                }
            },
            "THE CHESS MATCH (Tactical Stalemate)": {
                "description": "Cautious tactical battle, low scoring",
                "criteria": {
                    "both_avg_goals": 1.2,
                    "both_cautious": True,
                    "high_importance": True,
                    "h2h_low_scoring": True,
                    "both_under_25_pct": 0.70
                },
                "outcome_patterns": {
                    "first_goal_decisive_prob": 0.70,
                    "late_goals_rare_prob": 0.20,
                    "common_scores": ["1-0", "0-0", "1-1"],
                    "btts_prob": 0.35,
                    "over_25_prob": 0.25
                }
            },
            "THE COMEBACK DRAMA (Momentum Swings)": {
                "description": "Late drama and momentum shifts",
                "criteria": {
                    "strong_second_half": True,
                    "comeback_history": True,
                    "manager_tactical": True,
                    "recent_late_drama": True,
                    "underdog_spirit": True
                },
                "outcome_patterns": {
                    "second_half_goals_prob": 0.60,
                    "late_goals_prob": 0.55,
                    "common_scores": ["2-1", "1-1", "2-2"],
                    "btts_prob": 0.50,
                    "over_25_prob": 0.55
                }
            }
        }
    
    def calculate_narrative_scores(self, match_data):
        """Calculate narrative scores based on detailed criteria"""
        
        scores = {}
        
        for narrative, definition in self.narrative_definitions.items():
            score = 0
            max_possible = 100
            
            if narrative == "THE BLITZKRIEG (Early Domination)":
                # Check each criterion
                if match_data.get('favorite_win_prob', 0) > definition['criteria']['favorite_win_prob']:
                    score += 25
                
                if match_data.get('home_scored_first_pct', 0) > definition['criteria']['home_scored_first_pct']:
                    score += 20
                
                if match_data.get('opponent_concedes_early_pct', 0) > definition['criteria']['opponent_concedes_early_pct']:
                    score += 20
                
                if match_data.get('stakes_mismatch', False):
                    score += 15
                
                if match_data.get('venue_advantage_strong', False):
                    score += 20
            
            elif narrative == "THE SIEGE (Attack vs Defense)":
                if match_data.get('home_avg_shots', 0) > definition['criteria']['home_avg_shots']:
                    score += 30
                
                if match_data.get('away_avg_possession', 100) < definition['criteria']['away_avg_possession']:
                    score += 25
                
                if match_data.get('stakes_mismatch', False):
                    score += 20
                
                if match_data.get('away_poor_record', False):
                    score += 25
            
            elif narrative == "THE SHOOTOUT (End-to-End Chaos)":
                if match_data.get('both_btts_pct', 0) > definition['criteria']['both_btts_pct']:
                    score += 30
                
                if match_data.get('both_over_25_pct', 0) > definition['criteria']['both_over_25_pct']:
                    score += 25
                
                if match_data.get('both_attack_minded', False):
                    score += 20
                
                if match_data.get('high_stakes_both', False):
                    score += 15
                
                if match_data.get('both_weak_defense', 0) > definition['criteria']['both_weak_defense']:
                    score += 10
            
            elif narrative == "THE CHESS MATCH (Tactical Stalemate)":
                if match_data.get('both_avg_goals', 5) < definition['criteria']['both_avg_goals']:
                    score += 30
                
                if match_data.get('both_cautious', False):
                    score += 25
                
                if match_data.get('high_importance', False):
                    score += 20
                
                if match_data.get('h2h_low_scoring', False):
                    score += 15
                
                if match_data.get('both_under_25_pct', 0) > definition['criteria']['both_under_25_pct']:
                    score += 10
            
            elif narrative == "THE COMEBACK DRAMA (Momentum Swings)":
                if match_data.get('strong_second_half', False):
                    score += 25
                
                if match_data.get('comeback_history', False):
                    score += 20
                
                if match_data.get('manager_tactical', False):
                    score += 20
                
                if match_data.get('recent_late_drama', False):
                    score += 20
                
                if match_data.get('underdog_spirit', False):
                    score += 15
            
            scores[narrative] = min(score, max_possible)
        
        return scores
    
    def classify_retrospective_matches(self):
        """Classify our 9 matches retroactively"""
        
        matches = [
            {
                "name": "Atalanta 2-1 Cagliari",
                "data": {
                    "home_avg_shots": 18,  # Atalanta attacking
                    "away_avg_possession": 38,  # Cagliari defensive
                    "stakes_mismatch": True,  # Atalanta needs win
                    "away_poor_record": True  # Cagliari poor away
                },
                "predicted_narrative": "THE SIEGE (Attack vs Defense)",
                "actual_score": "2-1",
                "notes": "Siege but BTTS happened (anomaly)"
            },
            {
                "name": "Man City 3-0 Crystal Palace",
                "data": {
                    "favorite_win_prob": 0.85,
                    "home_scored_first_pct": 0.75,
                    "opponent_concedes_early_pct": 0.65,
                    "stakes_mismatch": True,
                    "venue_advantage_strong": True
                },
                "predicted_narrative": "THE BLITZKRIEG (Early Domination)",
                "actual_score": "3-0",
                "notes": "Perfect Blitzkrieg"
            },
            {
                "name": "Liverpool 2-0 Brighton",
                "data": {
                    "home_avg_shots": 16,
                    "away_avg_possession": 42,
                    "stakes_mismatch": True,
                    "away_poor_record": False  # Brighton decent away
                },
                "predicted_narrative": "THE SIEGE (Attack vs Defense)",
                "actual_score": "2-0",
                "notes": "Siege pattern - control but not thrashing"
            },
            {
                "name": "Fenerbahce 4-0 Konyaspor",
                "data": {
                    "favorite_win_prob": 0.80,
                    "home_scored_first_pct": 0.70,
                    "opponent_concedes_early_pct": 0.70,
                    "stakes_mismatch": True,
                    "venue_advantage_strong": True
                },
                "predicted_narrative": "THE BLITZKRIEG (Early Domination)",
                "actual_score": "4-0",
                "notes": "Perfect Blitzkrieg"
            },
            {
                "name": "West Ham 2-3 Aston Villa",
                "data": {
                    "both_btts_pct": 0.70,
                    "both_over_25_pct": 0.75,
                    "both_attack_minded": True,
                    "both_weak_defense": 1.6,
                    "high_stakes_both": True
                },
                "predicted_narrative": "THE SHOOTOUT (End-to-End Chaos)",
                "actual_score": "2-3",
                "notes": "Perfect Shootout"
            },
            {
                "name": "Sunderland 1-0 Newcastle",
                "data": {
                    "both_avg_goals": 1.1,
                    "both_cautious": True,
                    "high_importance": True,
                    "h2h_low_scoring": True,
                    "both_under_25_pct": 0.75
                },
                "predicted_narrative": "THE CHESS MATCH (Tactical Stalemate)",
                "actual_score": "1-0",
                "notes": "Perfect Chess Match"
            }
        ]
        
        return matches
    
    def get_narrative_recommendations(self, narrative, narrative_score):
        """Get specific recommendations based on narrative and score"""
        
        recommendations = {
            "THE BLITZKRIEG (Early Domination)": {
                "strong_fit": ["Favorite -1 handicap", "First goal before 30:00", "Favorite clean sheet"],
                "moderate_fit": ["Favorite win", "Under 3.5 goals", "Favorite to score first"],
                "weak_fit": ["Avoid or small stakes"]
            },
            "THE SIEGE (Attack vs Defense)": {
                "strong_fit": ["Under 2.5 goals", "BTTS: No", "1-0 correct score"],
                "moderate_fit": ["Home win", "Under 3.5 goals", "0-0 correct score"],
                "weak_fit": ["Small stakes on low scoring"]
            },
            "THE SHOOTOUT (End-to-End Chaos)": {
                "strong_fit": ["Over 2.5 goals", "BTTS: Yes", "2-1 correct score"],
                "moderate_fit": ["Over 1.5 goals", "Both teams to score", "3+ total goals"],
                "weak_fit": ["Goals expected markets"]
            },
            "THE CHESS MATCH (Tactical Stalemate)": {
                "strong_fit": ["Under 2.5 goals", "0-0 correct score", "1-0 correct score"],
                "moderate_fit": ["Under 1.5 goals", "Draw", "Low scoring first half"],
                "weak_fit": ["Small stakes on draw"]
            },
            "THE COMEBACK DRAMA (Momentum Swings)": {
                "strong_fit": ["Second half most goals", "Late goal (after 75:00)", "Draw no bet"],
                "moderate_fit": ["Over 1.5 second half goals", "Both teams to score", "Double chance"],
                "weak_fit": ["In-play betting opportunities"]
            }
        }
        
        if narrative_score >= 70:
            confidence = "strong_fit"
        elif narrative_score >= 50:
            confidence = "moderate_fit"
        else:
            confidence = "weak_fit"
        
        return recommendations.get(narrative, {}).get(confidence, [])

def main():
    st.title("⚽ Narrative Prediction System v2.0")
    st.markdown("### Quantitative Narrative Analysis & Betting Framework")
    
    # Initialize the system
    nps = NarrativePredictionSystem()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Narrative Analysis", 
        "🔍 Retrospective Testing", 
        "⚡ Live Match Analysis", 
        "📈 Performance Tracking"
    ])
    
    with tab1:
        st.header("Narrative Analysis Engine")
        
        # Match Data Inputs
        st.subheader("Match Data Input")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Statistical Data")
            favorite_win_prob = st.slider("Favorite Win Probability", 0.0, 1.0, 0.75, 0.01)
            home_scored_first_pct = st.slider("Home Team Scored First %", 0.0, 1.0, 0.70, 0.01)
            opponent_concedes_early_pct = st.slider("Opponent Concedes Early %", 0.0, 1.0, 0.60, 0.01)
            home_avg_shots = st.number_input("Home Avg Shots/Game", 0, 30, 16)
            away_avg_possession = st.number_input("Away Avg Possession %", 0, 100, 40)
        
        with col2:
            st.markdown("#### 🎯 Qualitative Factors")
            stakes_mismatch = st.checkbox("Stakes Mismatch", True)
            venue_advantage_strong = st.checkbox("Strong Venue Advantage", True)
            away_poor_record = st.checkbox("Away Team Poor Record", True)
            both_attack_minded = st.checkbox("Both Teams Attack-minded", False)
            high_stakes_both = st.checkbox("High Stakes for Both", False)
            both_cautious = st.checkbox("Both Teams Cautious", False)
            high_importance = st.checkbox("High Importance Match", False)
        
        # Calculate narrative scores
        match_data = {
            'favorite_win_prob': favorite_win_prob,
            'home_scored_first_pct': home_scored_first_pct,
            'opponent_concedes_early_pct': opponent_concedes_early_pct,
            'stakes_mismatch': stakes_mismatch,
            'venue_advantage_strong': venue_advantage_strong,
            'home_avg_shots': home_avg_shots,
            'away_avg_possession': away_avg_possession,
            'away_poor_record': away_poor_record,
            'both_attack_minded': both_attack_minded,
            'high_stakes_both': high_stakes_both,
            'both_cautious': both_cautious,
            'high_importance': high_importance
        }
        
        if st.button("🔍 Calculate Narrative Scores", type="primary"):
            scores = nps.calculate_narrative_scores(match_data)
            
            # Display results
            st.subheader("Narrative Scores")
            
            for narrative, score in scores.items():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{narrative}**")
                with col2:
                    st.progress(score/100)
                with col3:
                    confidence = "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak"
                    st.write(f"{score}/100 ({confidence})")
            
            # Identify dominant narrative
            dominant_narrative = max(scores.items(), key=lambda x: x[1])
            st.success(f"**Dominant Narrative:** {dominant_narrative[0]} (Score: {dominant_narrative[1]}/100)")
            
            # Get recommendations
            recommendations = nps.get_narrative_recommendations(
                dominant_narrative[0], 
                dominant_narrative[1]
            )
            
            if recommendations:
                st.subheader("🎯 Betting Recommendations")
                for rec in recommendations:
                    st.write(f"• {rec}")
    
    with tab2:
        st.header("Retrospective Testing")
        st.markdown("### Testing our narrative framework on completed matches")
        
        matches = nps.classify_retrospective_matches()
        
        for match in matches:
            with st.expander(f"{match['name']} - {match['predicted_narrative']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Predicted", match['predicted_narrative'].split('(')[0].strip())
                with col2:
                    st.metric("Actual", match['actual_score'])
                with col3:
                    st.metric("Result", "✓ Match" if "perfect" in match['notes'].lower() else "~ Partial" if "anomaly" not in match['notes'].lower() else "✗ Anomaly")
                
                st.write(f"**Notes:** {match['notes']}")
                
                # Calculate narrative score for this match
                scores = nps.calculate_narrative_scores(match['data'])
                st.write("**Narrative Scores:**")
                for narrative, score in scores.items():
                    if score > 0:
                        st.write(f"- {narrative.split('(')[0].strip()}: {score}/100")
    
    with tab3:
        st.header("Live Match Analysis")
        
        st.subheader("Select Example Match")
        example_matches = [
            "Man City vs Crystal Palace (Blitzkrieg Example)",
            "West Ham vs Aston Villa (Shootout Example)", 
            "Sunderland vs Newcastle (Chess Match Example)",
            "Atalanta vs Cagliari (Siege Example)"
        ]
        
        selected_match = st.selectbox("Choose match to analyze", example_matches)
        
        if selected_match:
            # Pre-populate based on match type
            if "Blitzkrieg" in selected_match:
                preset_data = {
                    'favorite_win_prob': 0.85,
                    'home_scored_first_pct': 0.75,
                    'opponent_concedes_early_pct': 0.65,
                    'stakes_mismatch': True,
                    'venue_advantage_strong': True
                }
            elif "Shootout" in selected_match:
                preset_data = {
                    'both_btts_pct': 0.70,
                    'both_over_25_pct': 0.75,
                    'both_attack_minded': True,
                    'both_weak_defense': 1.6,
                    'high_stakes_both': True
                }
            elif "Chess" in selected_match:
                preset_data = {
                    'both_avg_goals': 1.1,
                    'both_cautious': True,
                    'high_importance': True,
                    'h2h_low_scoring': True,
                    'both_under_25_pct': 0.75
                }
            else:  # Siege
                preset_data = {
                    'home_avg_shots': 18,
                    'away_avg_possession': 38,
                    'stakes_mismatch': True,
                    'away_poor_record': True
                }
            
            scores = nps.calculate_narrative_scores(preset_data)
            
            # Display analysis
            st.subheader(f"Analysis: {selected_match}")
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(scores.keys()),
                    y=list(scores.values()),
                    text=[f"{v}/100" for v in scores.values()],
                    textposition='auto',
                    marker_color=['#FF6B6B' if v == max(scores.values()) else '#4ECDC4' for v in scores.values()]
                )
            ])
            
            fig.update_layout(
                title="Narrative Scores",
                xaxis_tickangle=45,
                yaxis_range=[0, 100],
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show expected outcomes
            dominant_narrative = max(scores.items(), key=lambda x: x[1])
            if dominant_narrative[1] >= 50:
                patterns = nps.narrative_definitions[dominant_narrative[0]]['outcome_patterns']
                
                st.subheader("Expected Outcome Patterns")
                pattern_df = pd.DataFrame([
                    {"Pattern": "Early Goal (<30min)", "Probability": f"{patterns.get('early_goal_prob', 0)*100:.0f}%"},
                    {"Pattern": "BTTS", "Probability": f"{patterns.get('btts_prob', 0)*100:.0f}%"},
                    {"Pattern": "Over 2.5 Goals", "Probability": f"{patterns.get('over_25_prob', 0)*100:.0f}%"},
                    {"Pattern": "Clean Sheet", "Probability": f"{patterns.get('clean_sheet_prob', 0)*100:.0f}%"}
                ])
                
                st.table(pattern_df)
    
    with tab4:
        st.header("Performance Tracking")
        
        st.subheader("Testing Framework")
        
        # Manual testing interface
        st.markdown("### Phase 1: Manual Testing")
        st.write("""
        **Instructions:**
        1. Select 10 new matches (not in our 9 test matches)
        2. Manually classify each match into a narrative archetype
        3. Make predictions based on the narrative
        4. Track accuracy vs traditional statistical model
        """)
        
        # Testing template
        st.download_button(
            label="📥 Download Testing Template",
            data=pd.DataFrame(columns=[
                "Match", "Date", "Narrative", "Confidence", 
                "Predicted Score", "Actual Score", "Narrative Correct",
                "Key Moments Predicted", "Notes"
            ]).to_csv(index=False),
            file_name="narrative_testing_template.csv",
            mime="text/csv"
        )
        
        # Phase progress
        st.subheader("Implementation Phases")
        
        phases = [
            {"phase": "Phase 1", "name": "Manual Testing", "status": "Current", "tasks": ["Classify 10 matches", "Track accuracy", "Refine criteria"]},
            {"phase": "Phase 2", "name": "Semi-Automated", "status": "Next", "tasks": ["Build spreadsheet", "Input match data", "Get narrative suggestions"]},
            {"phase": "Phase 3", "name": "Decision Framework", "status": "Future", "tasks": ["Create betting rules", "Define stake sizes", "Build track record"]}
        ]
        
        for phase in phases:
            with st.expander(f"{phase['phase']}: {phase['name']} ({phase['status']})"):
                for task in phase['tasks']:
                    st.write(f"• {task}")

if __name__ == "__main__":
    main()
