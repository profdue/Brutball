import streamlit as st
import pandas as pd

# ============================================================================
# NARRATIVE SCORING ENGINE (FROM v3.0)
# ============================================================================

class NarrativePredictionEngine:
    """Core prediction engine - no fluff, just predictions"""
    
    def __init__(self):
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "key_indicators": ["favorite_prob > 65%", "home_advantage", "early_goal_history"],
                "scoring_weights": {
                    "favorite_probability": 30,
                    "home_advantage": 20,
                    "early_goal_history": 25,
                    "stakes_mismatch": 15,
                    "opponent_collapse_tendency": 10
                }
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "key_indicators": ["both_BTTS_high", "both_attack_minded", "weak_defenses"],
                "scoring_weights": {
                    "both_btts_percentage": 30,
                    "both_over_25_percentage": 25,
                    "manager_attack_style": 20,
                    "defensive_weakness_both": 15,
                    "high_stakes_both": 10
                }
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "key_indicators": ["possession_mismatch", "attacker_motivation", "defender_desperation"],
                "scoring_weights": {
                    "possession_mismatch": 25,
                    "shots_ratio": 20,
                    "attacker_motivation": 20,
                    "defender_desperation": 15,
                    "counter_attack_threat": 10,
                    "clean_sheet_history": 10
                }
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "key_indicators": ["both_cautious", "high_importance", "low_scoring_history"],
                "scoring_weights": {
                    "both_cautious": 30,
                    "match_importance": 25,
                    "manager_pragmatism": 20,
                    "h2h_low_scoring": 15,
                    "both_under_25_percentage": 10
                }
            }
        }
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score"""
        score = 0
        
        # Favorite probability (0-30 points)
        favorite_prob = match_data.get("favorite_probability", 50)
        score += min(30, (favorite_prob - 50) * 0.6)  # 50% = 0, 100% = 30
        
        # Home advantage (0-20 points)
        if match_data.get("home_team_favorite", False):
            score += 20
        elif match_data.get("neutral_venue", False):
            score += 5
        
        # Early goal history (0-25 points)
        home_early = match_data.get("home_early_goal_percentage", 0)
        away_early = match_data.get("away_early_goal_conceded_percentage", 0)
        early_score = (home_early + away_early) / 2
        score += min(25, early_score * 0.25)
        
        # Stakes mismatch (0-15 points)
        favorite_stakes = match_data.get("favorite_stakes", 0)  # 0-10
        underdog_stakes = match_data.get("underdog_stakes", 0)  # 0-10
        stakes_diff = abs(favorite_stakes - underdog_stakes)
        score += min(15, stakes_diff * 1.5)
        
        # Opponent collapse tendency (0-10 points)
        collapse_history = match_data.get("opponent_collapse_history", 0)  # 0-100%
        score += min(10, collapse_history * 0.1)
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score"""
        score = 0
        
        # Both BTTS percentage (0-30 points)
        home_btts = match_data.get("home_btts_percentage", 0)
        away_btts = match_data.get("away_btts_percentage", 0)
        avg_btts = (home_btts + away_btts) / 2
        score += min(30, avg_btts * 0.3)
        
        # Both Over 2.5 percentage (0-25 points)
        home_over = match_data.get("home_over_25_percentage", 0)
        away_over = match_data.get("away_over_25_percentage", 0)
        avg_over = (home_over + away_over) / 2
        score += min(25, avg_over * 0.25)
        
        # Manager attack style (0-20 points)
        home_attack = match_data.get("home_manager_attack_rating", 0)  # 0-10
        away_attack = match_data.get("away_manager_attack_rating", 0)  # 0-10
        avg_attack = (home_attack + away_attack) / 2
        score += min(20, avg_attack * 2)
        
        # Defensive weakness both (0-15 points)
        home_def_weak = match_data.get("home_defensive_weakness", 0)  # 0-10
        away_def_weak = match_data.get("away_defensive_weakness", 0)  # 0-10
        avg_def_weak = (home_def_weak + away_def_weak) / 2
        score += min(15, avg_def_weak * 1.5)
        
        # High stakes both (0-10 points)
        both_high_stakes = match_data.get("both_high_stakes", False)
        score += 10 if both_high_stakes else 0
        
        return min(100, score)
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score"""
        score = 0
        
        # Possession mismatch (0-25 points)
        home_possession = match_data.get("home_avg_possession", 50)
        away_possession = match_data.get("away_avg_possession", 50)
        possession_diff = abs(home_possession - away_possession)
        score += min(25, possession_diff * 0.5)
        
        # Shots ratio (0-20 points)
        home_shots = match_data.get("home_avg_shots", 10)
        away_shots_conceded = match_data.get("away_avg_shots_conceded", 10)
        shots_ratio = home_shots / max(away_shots_conceded, 1)
        if shots_ratio > 1.5:
            score += 20
        elif shots_ratio > 1.2:
            score += 15
        elif shots_ratio > 1.0:
            score += 10
        
        # Attacker motivation (0-20 points)
        attacker_motivation = match_data.get("attacker_motivation", 0)  # 0-10
        score += attacker_motivation * 2
        
        # Defender desperation (0-15 points)
        defender_desperation = match_data.get("defender_desperation", 0)  # 0-10
        score += defender_desperation * 1.5
        
        # Counter attack threat (0-10 points)
        counter_threat = match_data.get("defender_counter_threat", 0)  # 0-10
        score += counter_threat
        
        # Clean sheet history (0-10 points)
        attacker_clean_sheets = match_data.get("attacker_clean_sheet_percentage", 0)
        score += min(10, attacker_clean_sheets * 0.1)
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score"""
        score = 0
        
        # Both cautious (0-30 points)
        home_cautious = match_data.get("home_cautious_rating", 0)  # 0-10
        away_cautious = match_data.get("away_cautious_rating", 0)  # 0-10
        avg_cautious = (home_cautious + away_cautious) / 2
        score += min(30, avg_cautious * 3)
        
        # Match importance (0-25 points)
        importance = match_data.get("match_importance", 0)  # 0-10
        score += importance * 2.5
        
        # Manager pragmatism (0-20 points)
        home_pragmatic = match_data.get("home_manager_pragmatic_rating", 0)  # 0-10
        away_pragmatic = match_data.get("away_manager_pragmatic_rating", 0)  # 0-10
        avg_pragmatic = (home_pragmatic + away_pragmatic) / 2
        score += min(20, avg_pragmatic * 2)
        
        # H2H low scoring (0-15 points)
        h2h_low_scoring = match_data.get("h2h_low_scoring_percentage", 0)  # % of low scoring H2H
        score += min(15, h2h_low_scoring * 0.15)
        
        # Both Under 2.5 percentage (0-10 points)
        home_under = match_data.get("home_under_25_percentage", 0)
        away_under = match_data.get("away_under_25_percentage", 0)
        avg_under = (home_under + away_under) / 2
        score += min(10, avg_under * 0.1)
        
        return min(100, score)
    
    def predict_narrative(self, match_data):
        """MAIN PREDICTION FUNCTION"""
        scores = {}
        
        scores["BLITZKRIEG"] = self.calculate_blitzkrieg_score(match_data)
        scores["SHOOTOUT"] = self.calculate_shootout_score(match_data)
        scores["SIEGE"] = self.calculate_siege_score(match_data)
        scores["CHESS_MATCH"] = self.calculate_chess_match_score(match_data)
        
        # Determine dominant narrative
        dominant_narrative = max(scores, key=scores.get)
        dominant_score = scores[dominant_narrative]
        
        # Determine tier
        if dominant_score >= 75:
            tier = "TIER 1 (STRONG)"
        elif dominant_score >= 60:
            tier = "TIER 2 (MEDIUM)"
        elif dominant_score >= 50:
            tier = "TIER 3 (WEAK)"
        else:
            tier = "TIER 4 (AVOID)"
        
        return {
            "scores": scores,
            "dominant_narrative": dominant_narrative,
            "dominant_score": dominant_score,
            "tier": tier,
            "confidence": "High" if dominant_score >= 75 else "Medium" if dominant_score >= 60 else "Low"
        }
    
    def generate_betting_recommendations(self, narrative, score):
        """Generate betting recommendations based on narrative"""
        
        recommendations = {
            "BLITZKRIEG": [
                "Favorite to win",
                "Favorite clean sheet",
                "First goal before 25:00",
                "Over 2.5 team goals for favorite",
                "Favorite -1.5 Asian handicap"
            ],
            "SHOOTOUT": [
                "Over 2.5 goals",
                "BTTS: Yes",
                "Both teams to score & Over 2.5",
                "Late goal (after 75:00)",
                "Lead changes in match"
            ],
            "SIEGE": [
                "Under 2.5 goals",
                "Favorite to win",
                "BTTS: No",
                "First goal 45-70 mins",
                "Fewer than 10 corners total"
            ],
            "CHESS_MATCH": [
                "Under 2.5 goals",
                "BTTS: No",
                "0-0 or 1-0 correct score",
                "Few goals first half",
                "Under 1.5 goals"
            ]
        }
        
        # Adjust based on score
        if score >= 75:
            stake = "2-3 units"
        elif score >= 60:
            stake = "1-2 units"
        else:
            stake = "0.5-1 unit"
        
        return {
            "narrative": narrative,
            "score": score,
            "recommended_bets": recommendations.get(narrative, ["No clear recommendations"]),
            "suggested_stake": stake,
            "key_insight": self.narratives[narrative]["description"]
        }

# ============================================================================
# SIMPLE STREAMLIT INTERFACE
# ============================================================================

def main():
    st.set_page_config(page_title="Narrative Prediction Engine", layout="wide")
    
    st.title("⚽ **NARRATIVE PREDICTION ENGINE**")
    st.markdown("### Simple Input → Algorithm → Prediction")
    
    # Initialize engine
    engine = NarrativePredictionEngine()
    
    # Two columns: Input on left, Output on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📥 **Match Data Input**")
        
        with st.form("match_data_form"):
            st.subheader("Basic Match Info")
            match_name = st.text_input("Match", "Manchester City vs Nottingham Forest")
            
            col1a, col1b = st.columns(2)
            with col1a:
                home_team = st.text_input("Home Team", "Manchester City")
                away_team = st.text_input("Away Team", "Nottingham Forest")
            
            with col1b:
                competition = st.text_input("Competition", "Premier League")
                date = st.date_input("Date")
            
            st.divider()
            st.subheader("Key Statistics")
            
            # BLITZKRIEG factors
            st.markdown("**BLITZKRIEG Indicators**")
            col2a, col2b = st.columns(2)
            with col2a:
                favorite_probability = st.slider("Favorite Win Probability %", 0, 100, 75)
                home_team_favorite = st.checkbox("Home team is favorite", True)
                home_early_goal_pct = st.slider(f"{home_team} early goals % (0-25 mins)", 0, 100, 40)
            
            with col2b:
                away_early_goal_conceded_pct = st.slider(f"{away_team} early goals conceded %", 0, 100, 60)
                favorite_stakes = st.slider("Favorite stakes (0-10)", 0, 10, 8)
                underdog_stakes = st.slider("Underdog stakes (0-10)", 0, 10, 2)
            
            # SHOOTOUT factors
            st.markdown("**SHOOTOUT Indicators**")
            col3a, col3b = st.columns(2)
            with col3a:
                home_btts_pct = st.slider(f"{home_team} BTTS %", 0, 100, 60)
                home_over_25_pct = st.slider(f"{home_team} Over 2.5 %", 0, 100, 70)
                home_manager_attack = st.slider(f"{home_team} manager attack rating (0-10)", 0, 10, 8)
            
            with col3b:
                away_btts_pct = st.slider(f"{away_team} BTTS %", 0, 100, 40)
                away_over_25_pct = st.slider(f"{away_team} Over 2.5 %", 0, 100, 50)
                away_manager_attack = st.slider(f"{away_team} manager attack rating (0-10)", 0, 10, 6)
                both_high_stakes = st.checkbox("Both teams have high stakes", False)
            
            # SIEGE factors
            st.markdown("**SIEGE Indicators**")
            col4a, col4b = st.columns(2)
            with col4a:
                home_avg_possession = st.slider(f"{home_team} avg possession %", 0, 100, 65)
                home_avg_shots = st.slider(f"{home_team} avg shots per game", 0, 30, 15)
                attacker_motivation = st.slider("Attacker motivation (0-10)", 0, 10, 7)
            
            with col4b:
                away_avg_possession = st.slider(f"{away_team} avg possession %", 0, 100, 40)
                away_avg_shots_conceded = st.slider(f"{away_team} avg shots conceded", 0, 30, 18)
                defender_desperation = st.slider("Defender desperation (0-10)", 0, 10, 8)
                defender_counter_threat = st.slider("Defender counter threat (0-10)", 0, 10, 6)
            
            # CHESS MATCH factors
            st.markdown("**CHESS MATCH Indicators**")
            col5a, col5b = st.columns(2)
            with col5a:
                home_cautious_rating = st.slider(f"{home_team} cautious rating (0-10)", 0, 10, 5)
                match_importance = st.slider("Match importance (0-10)", 0, 10, 7)
                home_manager_pragmatic = st.slider(f"{home_team} manager pragmatic rating", 0, 10, 6)
            
            with col5b:
                away_cautious_rating = st.slider(f"{away_team} cautious rating (0-10)", 0, 10, 7)
                h2h_low_scoring_pct = st.slider("H2H low scoring % (<3 goals)", 0, 100, 60)
                away_manager_pragmatic = st.slider(f"{away_team} manager pragmatic rating", 0, 10, 7)
            
            # Submit button
            submitted = st.form_submit_button("🚀 **RUN PREDICTION ENGINE**")
    
    with col2:
        st.header("📤 **Prediction Output**")
        
        if submitted:
            # Prepare match data
            match_data = {
                "match_name": match_name,
                "home_team": home_team,
                "away_team": away_team,
                "competition": competition,
                "date": date,
                
                # BLITZKRIEG data
                "favorite_probability": favorite_probability,
                "home_team_favorite": home_team_favorite,
                "home_early_goal_percentage": home_early_goal_pct,
                "away_early_goal_conceded_percentage": away_early_goal_conceded_pct,
                "favorite_stakes": favorite_stakes,
                "underdog_stakes": underdog_stakes,
                "opponent_collapse_history": 70 if underdog_stakes <= 3 else 30,
                
                # SHOOTOUT data
                "home_btts_percentage": home_btts_pct,
                "away_btts_percentage": away_btts_pct,
                "home_over_25_percentage": home_over_25_pct,
                "away_over_25_percentage": away_over_25_pct,
                "home_manager_attack_rating": home_manager_attack,
                "away_manager_attack_rating": away_manager_attack,
                "home_defensive_weakness": 10 - home_manager_attack,  # Simplified
                "away_defensive_weakness": 10 - away_manager_attack,
                "both_high_stakes": both_high_stakes,
                
                # SIEGE data
                "home_avg_possession": home_avg_possession,
                "away_avg_possession": away_avg_possession,
                "home_avg_shots": home_avg_shots,
                "away_avg_shots_conceded": away_avg_shots_conceded,
                "attacker_motivation": attacker_motivation,
                "defender_desperation": defender_desperation,
                "defender_counter_threat": defender_counter_threat,
                "attacker_clean_sheet_percentage": 60 if home_manager_attack >= 7 else 40,
                
                # CHESS MATCH data
                "home_cautious_rating": home_cautious_rating,
                "away_cautious_rating": away_cautious_rating,
                "match_importance": match_importance,
                "home_manager_pragmatic_rating": home_manager_pragmatic,
                "away_manager_pragmatic_rating": away_manager_pragmatic,
                "h2h_low_scoring_percentage": h2h_low_scoring_pct,
                "home_under_25_percentage": 100 - home_over_25_pct,
                "away_under_25_percentage": 100 - away_over_25_pct
            }
            
            # Run prediction engine
            with st.spinner("Running narrative analysis..."):
                prediction = engine.predict_narrative(match_data)
                betting_recs = engine.generate_betting_recommendations(
                    prediction["dominant_narrative"],
                    prediction["dominant_score"]
                )
            
            # Display results
            st.success(f"✅ **PREDICTION COMPLETE**")
            
            # Narrative prediction
            st.subheader("🎯 **Dominant Narrative Prediction**")
            
            narrative_info = engine.narratives[prediction["dominant_narrative"]]
            
            col_result1, col_result2 = st.columns(2)
            
            with col_result1:
                st.metric(
                    "Predicted Narrative",
                    prediction["dominant_narrative"],
                    delta=f"Score: {prediction['dominant_score']:.1f}/100"
                )
                st.metric("Confidence Tier", prediction["tier"])
                st.metric("Confidence Level", prediction["confidence"])
            
            with col_result2:
                st.info(f"**Description:** {narrative_info['description']}")
                st.write(f"**Key Indicators:** {', '.join(narrative_info['key_indicators'])}")
            
            # All narrative scores
            st.subheader("📊 **All Narrative Scores**")
            
            scores_df = pd.DataFrame({
                "Narrative": list(prediction["scores"].keys()),
                "Score": list(prediction["scores"].values())
            }).sort_values("Score", ascending=False)
            
            st.dataframe(scores_df.style.highlight_max(subset=["Score"]), use_container_width=True)
            
            # Betting recommendations
            st.subheader("💰 **Betting Recommendations**")
            
            st.info(f"**Key Insight:** {betting_recs['key_insight']}")
            st.write(f"**Suggested Stake:** {betting_recs['suggested_stake']}")
            
            st.write("**Recommended Bets:**")
            for i, bet in enumerate(betting_recs["recommended_bets"], 1):
                st.write(f"{i}. {bet}")
            
            # Simple validation
            st.divider()
            st.subheader("✅ **Validation**")
            
            actual_narrative = st.selectbox(
                "Actual Match Narrative (post-match)",
                ["", "BLITZKRIEG", "SHOOTOUT", "SIEGE", "CHESS_MATCH", "OTHER"]
            )
            
            if actual_narrative:
                correct = actual_narrative == prediction["dominant_narrative"]
                if correct:
                    st.success(f"✅ **CORRECT!** Predicted {prediction['dominant_narrative']}")
                else:
                    st.warning(f"❌ **INCORRECT** Predicted {prediction['dominant_narrative']}, Actual {actual_narrative}")
        
        else:
            # Show empty state
            st.info("👈 **Enter match data on the left and click 'RUN PREDICTION ENGINE'**")
            st.write("The engine will:")
            st.write("1. 📊 Calculate scores for all 4 narratives")
            st.write("2. 🎯 Identify dominant narrative")
            st.write("3. 💰 Generate betting recommendations")
            st.write("4. 📈 Provide confidence levels")
            
            # Show example
            st.divider()
            st.subheader("🎯 **Example Prediction**")
            
            example_data = {
                "scores": {"BLITZKRIEG": 78.5, "SHOOTOUT": 45.2, "SIEGE": 32.1, "CHESS_MATCH": 25.8},
                "dominant_narrative": "BLITZKRIEG",
                "dominant_score": 78.5,
                "tier": "TIER 1 (STRONG)",
                "confidence": "High"
            }
            
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.metric("Predicted Narrative", "BLITZKRIEG", delta="78.5/100")
                st.metric("Confidence Tier", "TIER 1")
            
            with col_ex2:
                st.info("**Description:** Early Domination - Favorite crushes weak opponent")
                st.write("**Recommended Bets:** Favorite win, clean sheet, early goal")

if __name__ == "__main__":
    main()
