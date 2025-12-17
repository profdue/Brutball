import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Narrative Prediction Engine",
    page_icon="⚽",
    layout="wide"
)

# -------------------------------------------------------------------
# CORE PREDICTION ENGINE
# -------------------------------------------------------------------
class NarrativeEngine:
    """Bare-bones prediction engine - No fluff, just predictions"""
    
    def __init__(self):
        # Narrative definitions
        self.narratives = {
            "BLITZKRIEG": {
                "desc": "Favorite dominates early, opponent collapses",
                "criteria": ["favorite_prob", "home_advantage", "early_goal_history", "stakes_mismatch", "opponent_collapse"],
                "weights": [0.30, 0.20, 0.25, 0.15, 0.10],
                "min_score": 75
            },
            "SHOOTOUT": {
                "desc": "End-to-end chaos, both teams attack",
                "criteria": ["both_btts_pct", "both_over25_pct", "both_attack", "weak_defenses", "high_stakes_both"],
                "weights": [0.25, 0.20, 0.20, 0.15, 0.10, 0.10],
                "min_score": 75
            },
            "SIEGE": {
                "desc": "Attack vs defense, breakthrough comes late",
                "criteria": ["possession_mismatch", "shots_ratio", "attacker_motivation", "defender_desperation", "counter_threat", "clean_sheet_hist"],
                "weights": [0.25, 0.20, 0.20, 0.15, 0.10, 0.10],
                "min_score": 60
            },
            "CHESS": {
                "desc": "Tactical battle, low scoring",
                "criteria": ["both_cautious", "high_importance", "manager_pragmatism", "h2h_low_scoring", "both_under25_pct"],
                "weights": [0.30, 0.25, 0.20, 0.15, 0.10],
                "min_score": 75
            }
        }
    
    def score_blitzkrieg(self, data):
        """Calculate Blitzkrieg score"""
        score = 0
        
        # Favorite probability (0-30 points)
        if data.get('favorite_prob', 0) > 0.65:
            score += min(data['favorite_prob'] * 30, 30)
        
        # Home advantage (0-20 points)
        if data.get('home_advantage', False):
            score += 20
        
        # Early goal history (0-25 points)
        if data.get('early_goal_history', 0) > 0.6:
            score += min(data['early_goal_history'] * 25, 25)
        
        # Stakes mismatch (0-15 points)
        if data.get('stakes_mismatch', False):
            score += 15
        
        # Opponent collapse tendency (0-10 points)
        if data.get('opponent_collapse', 0) > 0.5:
            score += min(data['opponent_collapse'] * 10, 10)
        
        return min(score, 100)
    
    def score_shootout(self, data):
        """Calculate Shootout score"""
        score = 0
        
        # Both BTTS % (0-25 points)
        if data.get('both_btts_pct', 0) > 0.6:
            score += min(data['both_btts_pct'] * 25, 25)
        
        # Both Over 2.5 % (0-20 points)
        if data.get('both_over25_pct', 0) > 0.6:
            score += min(data['both_over25_pct'] * 20, 20)
        
        # Both attack-minded (0-20 points)
        if data.get('both_attack', False):
            score += 20
        
        # Weak defenses both (0-15 points)
        if data.get('weak_defenses', 0) > 1.5:
            score += min((data['weak_defenses']/2) * 15, 15)
        
        # High stakes both (0-10 points)
        if data.get('high_stakes_both', False):
            score += 10
        
        # Derby/rivalry (0-10 points)
        if data.get('derby', False):
            score += 10
        
        return min(score, 100)
    
    def score_siege(self, data):
        """Calculate Siege score"""
        score = 0
        
        # Possession mismatch (0-25 points)
        if data.get('possession_mismatch', 0) > 0.15:
            score += min(data['possession_mismatch'] * 100 * 0.25, 25)
        
        # Shots ratio (0-20 points)
        if data.get('shots_ratio', 1) > 2:
            score += min((data['shots_ratio']/4) * 20, 20)
        
        # Attacker motivation (0-20 points)
        if data.get('attacker_motivation', 0) > 0.7:
            score += min(data['attacker_motivation'] * 20, 20)
        
        # Defender desperation (0-15 points)
        if data.get('defender_desperation', 0) > 0.5:
            score += min(data['defender_desperation'] * 15, 15)
        
        # Counter threat (0-10 points) - NEGATIVE factor
        counter_threat = data.get('counter_threat', 0)
        if counter_threat > 0.5:
            score -= min(counter_threat * 10, 10)
        else:
            score += 5  # Bonus if no counter threat
        
        # Clean sheet history (0-10 points)
        if data.get('clean_sheet_hist', 0) > 0.5:
            score += min(data['clean_sheet_hist'] * 10, 10)
        
        return max(0, min(score, 100))
    
    def score_chess(self, data):
        """Calculate Chess Match score"""
        score = 0
        
        # Both cautious (0-30 points)
        if data.get('both_cautious', False):
            score += 30
        
        # High importance (0-25 points)
        if data.get('high_importance', 0) > 0.7:
            score += min(data['high_importance'] * 25, 25)
        
        # Manager pragmatism (0-20 points)
        if data.get('manager_pragmatism', 0) > 0.6:
            score += min(data['manager_pragmatism'] * 20, 20)
        
        # H2H low scoring (0-15 points)
        if data.get('h2h_low_scoring', False):
            score += 15
        
        # Both Under 2.5 % (0-10 points)
        if data.get('both_under25_pct', 0) > 0.6:
            score += min(data['both_under25_pct'] * 10, 10)
        
        return min(score, 100)
    
    def predict(self, match_data):
        """Make prediction - returns narrative and score"""
        scores = {}
        
        # Calculate all scores
        scores['BLITZKRIEG'] = self.score_blitzkrieg(match_data)
        scores['SHOOTOUT'] = self.score_shootout(match_data)
        scores['SIEGE'] = self.score_siege(match_data)
        scores['CHESS'] = self.score_chess(match_data)
        
        # Get highest score
        best_narrative = max(scores.items(), key=lambda x: x[1])
        
        return {
            'narrative': best_narrative[0],
            'score': best_narrative[1],
            'all_scores': scores,
            'confidence': self.get_confidence(best_narrative[1])
        }
    
    def get_confidence(self, score):
        """Get confidence level based on score"""
        if score >= 75:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 50:
            return "LOW"
        else:
            return "VERY LOW"
    
    def get_betting_recommendations(self, narrative, score):
        """Get simple betting recommendations"""
        recs = {
            'BLITZKRIEG': [
                'Favorite to win',
                'Favorite clean sheet',
                'First goal before 25:00',
                'Favorite -1.5 handicap'
            ],
            'SHOOTOUT': [
                'Over 2.5 goals',
                'BTTS: Yes',
                'Late goal (after 75:00)',
                '2-1 or 3-2 correct score'
            ],
            'SIEGE': [
                'Under 2.5 goals',
                'Favorite to win',
                'BTTS: No',
                '1-0 or 2-0 correct score'
            ],
            'CHESS': [
                'Under 2.5 goals',
                'BTTS: No',
                '0-0 or 1-0 correct score',
                'Fewer than 10 corners'
            ]
        }
        
        stake = "2-3%" if score >= 75 else "1-2%" if score >= 60 else "0.5-1%" if score >= 50 else "AVOID"
        
        return {
            'stake': stake,
            'recommendations': recs.get(narrative, ['No clear recommendations'])
        }

# -------------------------------------------------------------------
# SIMPLE INTERFACE
# -------------------------------------------------------------------
def main():
    st.title("⚽ Narrative Prediction Engine")
    st.markdown("### **No fluff, just predictions**")
    
    # Initialize engine
    engine = NarrativeEngine()
    
    # Simple match input
    st.header("📝 Match Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.text_input("Home Team", "Manchester City")
        away_team = st.text_input("Away Team", "Nottingham Forest")
        
        # Quick style assessment
        st.subheader("Team Styles")
        home_style = st.selectbox(
            f"{home_team} Style",
            ["Attacking", "Defensive", "Balanced", "Counter-Attack"]
        )
        away_style = st.selectbox(
            f"{away_team} Style",
            ["Attacking", "Defensive", "Balanced", "Counter-Attack"]
        )
        
        # Stakes
        st.subheader("Stakes")
        home_stakes = st.selectbox(
            f"{home_team} Situation",
            ["Must-win", "Comfortable", "Relegation fight", "Nothing to play for"]
        )
        away_stakes = st.selectbox(
            f"{away_team} Situation",
            ["Must-win", "Comfortable", "Relegation fight", "Nothing to play for"]
        )
    
    with col2:
        # Key metrics
        st.subheader("Key Metrics")
        
        favorite_prob = st.slider("Favorite Win Probability", 0.0, 1.0, 0.75, 0.01)
        home_advantage = st.checkbox("Strong Home Advantage", True)
        
        possession_mismatch = st.slider("Possession Mismatch (Home - Away)", 0, 100, 65, 5)
        
        btts_home = st.slider(f"{home_team} BTTS %", 0.0, 1.0, 0.6, 0.05)
        btts_away = st.slider(f"{away_team} BTSS %", 0.0, 1.0, 0.4, 0.05)
        
        over25_home = st.slider(f"{home_team} Over 2.5 %", 0.0, 1.0, 0.7, 0.05)
        over25_away = st.slider(f"{away_team} Over 2.5 %", 0.0, 1.0, 0.5, 0.05)
    
    # Advanced toggles
    with st.expander("⚙️ Advanced Parameters"):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            early_goal_history = st.slider("Home Early Goal History %", 0.0, 1.0, 0.7, 0.05)
            opponent_collapse = st.slider("Away Collapse Tendency", 0.0, 1.0, 0.6, 0.05)
            
            both_cautious = st.checkbox("Both Teams Cautious", False)
            high_importance = st.slider("Match Importance", 0.0, 1.0, 0.5, 0.1)
            
        with col_adv2:
            manager_pragmatism = st.slider("Manager Pragmatism", 0.0, 1.0, 0.5, 0.1)
            h2h_low_scoring = st.checkbox("H2H Usually Low Scoring", False)
            
            counter_threat = st.slider("Away Counter Threat", 0.0, 1.0, 0.3, 0.05)
            clean_sheet_hist = st.slider("Home Clean Sheet History", 0.0, 1.0, 0.5, 0.05)
    
    # Prepare data
    match_data = {
        'favorite_prob': favorite_prob,
        'home_advantage': home_advantage,
        'early_goal_history': early_goal_history,
        'stakes_mismatch': home_stakes == "Must-win" and away_stakes in ["Nothing to play for", "Comfortable"],
        'opponent_collapse': opponent_collapse,
        
        'both_btts_pct': (btts_home + btts_away) / 2,
        'both_over25_pct': (over25_home + over25_away) / 2,
        'both_attack': home_style == "Attacking" and away_style == "Attacking",
        'weak_defenses': 1.8 if btts_home > 0.6 and btts_away > 0.6 else 1.2,
        'high_stakes_both': home_stakes == "Must-win" and away_stakes == "Must-win",
        'derby': False,  # Could add this
        
        'possession_mismatch': possession_mismatch / 100,
        'shots_ratio': 3.0 if possession_mismatch > 60 else 1.5,
        'attacker_motivation': 0.9 if home_stakes == "Must-win" else 0.5,
        'defender_desperation': 0.8 if away_stakes == "Relegation fight" else 0.3,
        'counter_threat': counter_threat,
        'clean_sheet_hist': clean_sheet_hist,
        
        'both_cautious': both_cautious,
        'high_importance': high_importance,
        'manager_pragmatism': manager_pragmatism,
        'h2h_low_scoring': h2h_low_scoring,
        'both_under25_pct': 1 - ((over25_home + over25_away) / 2)
    }
    
    # Make prediction
    if st.button("🚀 PREDICT", type="primary", use_container_width=True):
        
        prediction = engine.predict(match_data)
        betting = engine.get_betting_recommendations(prediction['narrative'], prediction['score'])
        
        st.header("🎯 Prediction Results")
        
        # Main prediction
        col_pred1, col_pred2, col_pred3 = st.columns(3)
        
        with col_pred1:
            st.metric("Predicted Narrative", prediction['narrative'])
            st.caption(engine.narratives[prediction['narrative']]['desc'])
        
        with col_pred2:
            st.metric("Score", f"{prediction['score']}/100")
            st.progress(prediction['score']/100)
        
        with col_pred3:
            st.metric("Confidence", prediction['confidence'])
            st.metric("Recommended Stake", betting['stake'])
        
        # All scores
        st.subheader("All Narrative Scores")
        
        scores_df = pd.DataFrame({
            'Narrative': list(prediction['all_scores'].keys()),
            'Score': list(prediction['all_scores'].values()),
            'Status': ['✅' if k == prediction['narrative'] else '' for k in prediction['all_scores'].keys()]
        })
        
        st.dataframe(scores_df, use_container_width=True, hide_index=True)
        
        # Betting recommendations
        st.subheader("💰 Betting Recommendations")
        
        for rec in betting['recommendations']:
            st.write(f"• {rec}")
        
        # Expected flow
        st.subheader("📈 Expected Match Flow")
        
        flows = {
            'BLITZKRIEG': [
                "Early pressure from favorite (0-15 mins)",
                "Breakthrough likely before 30 mins",
                "Opponent confidence collapses after first goal",
                "Additional goals in 35-65 minute window",
                "Game effectively over by 70 mins"
            ],
            'SHOOTOUT': [
                "Fast start from both teams (0-10 mins)",
                "Early goals probable (first 25 mins)",
                "Lead changes possible",
                "End-to-end throughout",
                "Late drama very likely"
            ],
            'SIEGE': [
                "Attacker dominates possession",
                "Defender parks bus",
                "Frustration builds",
                "Breakthrough often 45-70 mins",
                "Clean sheet OR counter-attack goal"
            ],
            'CHESS': [
                "Cautious start (0-30 mins)",
                "Few clear chances",
                "Set pieces crucial",
                "First goal often decisive",
                "Late changes unlikely"
            ]
        }
        
        for flow in flows.get(prediction['narrative'], []):
            st.write(f"• {flow}")
        
        # Validation
        st.divider()
        st.subheader("📋 Validation")
        
        actual_outcome = st.selectbox(
            "Actual Outcome (for validation)",
            ["Prediction Correct", "Partial Match", "Wrong Prediction", "Not Played Yet"]
        )
        
        if st.button("Save Validation"):
            # Simple validation tracking
            validation_data = {
                'match': f"{home_team} vs {away_team}",
                'date': datetime.now().strftime("%Y-%m-%d"),
                'predicted': prediction['narrative'],
                'score': prediction['score'],
                'actual': actual_outcome,
                'correct': 1 if actual_outcome == "Prediction Correct" else 0.5 if actual_outcome == "Partial Match" else 0
            }
            
            # Store in session state
            if 'validations' not in st.session_state:
                st.session_state.validations = []
            
            st.session_state.validations.append(validation_data)
            st.success("Validation saved!")
    
    # Show validation history
    if 'validations' in st.session_state and st.session_state.validations:
        st.divider()
        st.subheader("📊 Validation History")
        
        df = pd.DataFrame(st.session_state.validations)
        
        if len(df) > 0:
            accuracy = df['correct'].mean() * 100
            
            col_hist1, col_hist2, col_hist3 = st.columns(3)
            with col_hist1:
                st.metric("Total Predictions", len(df))
            with col_hist2:
                st.metric("Correct", f"{len(df[df['correct'] == 1])}/{len(df)}")
            with col_hist3:
                st.metric("Accuracy", f"{accuracy:.1f}%")
            
            st.dataframe(df, use_container_width=True)
    
    # Quick examples
    st.divider()
    st.subheader("⚡ Quick Examples")
    
    example_cols = st.columns(3)
    
    with example_cols[0]:
        if st.button("Man City vs Forest", use_container_width=True):
            st.session_state['home_team'] = "Manchester City"
            st.session_state['away_team'] = "Nottingham Forest"
            st.session_state['home_style'] = "Attacking"
            st.session_state['away_style'] = "Defensive"
            st.session_state['favorite_prob'] = 0.85
            st.rerun()
    
    with example_cols[1]:
        if st.button("West Ham vs Villa", use_container_width=True):
            st.session_state['home_team'] = "West Ham"
            st.session_state['away_team'] = "Aston Villa"
            st.session_state['home_style'] = "Attacking"
            st.session_state['away_style'] = "Attacking"
            st.session_state['favorite_prob'] = 0.5
            st.rerun()
    
    with example_cols[2]:
        if st.button("Arsenal vs Chelsea", use_container_width=True):
            st.session_state['home_team'] = "Arsenal"
            st.session_state['away_team'] = "Chelsea"
            st.session_state['home_style'] = "Balanced"
            st.session_state['away_style'] = "Balanced"
            st.session_state['both_cautious'] = True
            st.session_state['high_importance'] = 0.9
            st.rerun()

# -------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------------
if 'home_team' not in st.session_state:
    st.session_state['home_team'] = "Manchester City"
if 'away_team' not in st.session_state:
    st.session_state['away_team'] = "Nottingham Forest"
if 'home_style' not in st.session_state:
    st.session_state['home_style'] = "Attacking"
if 'away_style' not in st.session_state:
    st.session_state['away_style'] = "Defensive"
if 'favorite_prob' not in st.session_state:
    st.session_state['favorite_prob'] = 0.75

if __name__ == "__main__":
    main()
