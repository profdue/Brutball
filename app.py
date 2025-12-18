import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class NarrativePredictionEngine:
    """Core prediction engine with all our tested logic"""
    
    def __init__(self):
        # Manager style database (from your Premier League list)
        self.manager_db = {
            "Mikel Arteta": {"style": "Possession-based & control", "attack": 9, "defense": 7, "press": 8, "possession": 9, "pragmatic": 6},
            "Unai Emery": {"style": "Balanced/Adaptive", "attack": 8, "defense": 8, "press": 7, "possession": 7, "pragmatic": 7},
            "Andoni Iraola": {"style": "Progressive/Developing", "attack": 7, "defense": 6, "press": 9, "possession": 6, "pragmatic": 5},
            "Keith Andrews": {"style": "Balanced/Adaptive", "attack": 6, "defense": 7, "press": 7, "possession": 6, "pragmatic": 7},
            "Fabian Hürzeler": {"style": "Progressive/Developing", "attack": 8, "defense": 6, "press": 7, "possession": 8, "pragmatic": 4},
            "Scott Parker": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 8, "press": 6, "possession": 5, "pragmatic": 8},
            "Enzo Maresca": {"style": "Possession-based & control", "attack": 8, "defense": 7, "press": 7, "possession": 9, "pragmatic": 6},
            "Oliver Glasner": {"style": "Balanced/Adaptive", "attack": 7, "defense": 7, "press": 6, "possession": 7, "pragmatic": 7},
            "David Moyes": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 9, "press": 6, "possession": 5, "pragmatic": 9},
            "Marco Silva": {"style": "Balanced/Adaptive", "attack": 8, "defense": 7, "press": 7, "possession": 7, "pragmatic": 6},
            "Daniel Farke": {"style": "Progressive/Developing", "attack": 8, "defense": 6, "press": 8, "possession": 7, "pragmatic": 5},
            "Arne Slot": {"style": "High press & transition", "attack": 9, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Pep Guardiola": {"style": "Possession-based & control", "attack": 10, "defense": 8, "press": 9, "possession": 10, "pragmatic": 4},
            "Ruben Amorim": {"style": "High press & transition", "attack": 8, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Eddie Howe": {"style": "High press & transition", "attack": 9, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Ange Postecoglou": {"style": "High press & transition", "attack": 9, "defense": 5, "press": 9, "possession": 6, "pragmatic": 4},
            "Régis Le Bris": {"style": "Progressive/Developing", "attack": 6, "defense": 7, "press": 7, "possession": 6, "pragmatic": 6},
            "Thomas Frank": {"style": "Balanced/Adaptive", "attack": 7, "defense": 8, "press": 7, "possession": 7, "pragmatic": 7},
            "Graham Potter": {"style": "Balanced/Adaptive", "attack": 7, "defense": 7, "press": 6, "possession": 8, "pragmatic": 7},
            "Vítor Pereira": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 8, "press": 5, "possession": 5, "pragmatic": 8}
        }
        
        # Narrative definitions
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "flow": "• Early pressure from favorite (0-15 mins)\n• Breakthrough before 30 mins\n• Opponent confidence collapses\n• Additional goals in 35-65 minute window",
                "betting_markets": ["Favorite win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals"]
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams\n• Early goals probable\n• Lead changes possible\n• Late drama very likely",
                "betting_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00"]
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "flow": "• Attacker dominates possession (60%+)\n• Defender parks bus\n• Breakthrough often 45-70 mins\n• Clean sheet OR counter-attack goal",
                "betting_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins"]
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both\n• Midfield battle dominates\n• Set pieces become crucial\n• First goal often decisive",
                "betting_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0", "Few goals first half"]
            }
        }
    
    def calculate_favorite_probability(self, home_odds, away_odds):
        """Convert odds to implied probabilities"""
        home_implied = 1 / home_odds
        away_implied = 1 / away_odds
        total = home_implied + away_implied
        
        home_prob = home_implied / total * 100
        away_prob = away_implied / total * 100
        
        favorite_prob = max(home_prob, away_prob)
        favorite_is_home = home_prob > away_prob
        
        return {
            "home_probability": home_prob,
            "away_probability": away_prob,
            "favorite_probability": favorite_prob,
            "favorite_is_home": favorite_is_home,
            "favorite_strength": "STRONG" if favorite_prob >= 70 else "MODERATE" if favorite_prob >= 60 else "WEAK"
        }
    
    def analyze_form(self, form_string):
        """Convert form string to rating"""
        if not form_string or len(form_string) < 3:
            return {"rating": 5, "confidence": 3}
        
        form_map = {"W": 2, "D": 1, "L": 0}
        points = 0
        
        for char in form_string.upper():
            if char in form_map:
                points += form_map[char]
        
        avg_points = points / len(form_string)
        rating = (avg_points / 2) * 10
        
        return {"rating": min(10, rating), "confidence": min(10, len(form_string) * 2)}
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score (0-100)"""
        score = 0
        
        # Favorite probability (0-30 points)
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        score += min(30, (favorite_prob - 50) * 0.6) if favorite_prob > 50 else 0
        
        # Home advantage if favorite (0-20 points)
        if prob["favorite_is_home"]:
            score += 20
        
        # Stakes mismatch (0-15 points)
        home_stakes = 10 - (match_data["home_position"] / 20 * 10)
        away_stakes = 10 - (match_data["away_position"] / 20 * 10)
        stakes_diff = abs(home_stakes - away_stakes)
        score += min(15, stakes_diff * 1.5)
        
        # Form mismatch (0-20 points)
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        form_diff = abs(home_form - away_form)
        score += min(20, form_diff * 2)
        
        # Manager style mismatch (0-15 points)
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        style_mismatch = abs(home_attack - (10 - away_defense))
        score += min(15, style_mismatch * 1.5)
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score (0-100)"""
        score = 0
        
        # Both teams attacking (0-30 points)
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        avg_attack = (home_attack + away_attack) / 2
        score += min(30, avg_attack * 3)
        
        # Both teams weak defense (0-25 points)
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        avg_defense_weakness = (10 - home_defense + 10 - away_defense) / 2
        score += min(25, avg_defense_weakness * 2.5)
        
        # High press both (0-20 points)
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        avg_press = (home_press + away_press) / 2
        score += min(20, avg_press * 2)
        
        # Recent H2H high scoring (0-15 points)
        if match_data["last_h2h_goals"] >= 3:
            score += 15
        elif match_data["last_h2h_goals"] >= 2:
            score += 10
        elif match_data["last_h2h_goals"] > 0:
            score += 5
        
        # Both teams similar stakes (0-10 points)
        home_stakes = 10 - (match_data["home_position"] / 20 * 10)
        away_stakes = 10 - (match_data["away_position"] / 20 * 10)
        stakes_similarity = 10 - abs(home_stakes - away_stakes)
        score += min(10, stakes_similarity)
        
        return min(100, score)
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score (0-100)"""
        score = 0
        
        # Possession/attack mismatch (0-30 points)
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        home_possession = match_data["home_possession_rating"]
        
        attack_defense_diff = abs(home_attack - away_defense)
        score += min(30, attack_defense_diff * 3)
        
        # Favorite advantage (0-25 points)
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if prob["favorite_is_home"] and prob["favorite_probability"] >= 60:
            score += 25
        elif prob["favorite_is_home"]:
            score += 15
        
        # Pragmatic vs attacking (0-20 points)
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        pragmatic_diff = abs(home_pragmatic - away_pragmatic)
        score += min(20, pragmatic_diff * 2)
        
        # Low H2H goals (0-15 points)
        if match_data["last_h2h_goals"] <= 2:
            score += 15
        elif match_data["last_h2h_goals"] <= 3:
            score += 10
        else:
            score += 5
        
        # Form mismatch (0-10 points)
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        form_diff = abs(home_form - away_form)
        score += min(10, form_diff)
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score (0-100)"""
        score = 0
        
        # Both managers pragmatic (0-30 points)
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        avg_pragmatic = (home_pragmatic + away_pragmatic) / 2
        score += min(30, avg_pragmatic * 3)
        
        # Close match (0-25 points)
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        if favorite_prob < 55:
            score += 25
        elif favorite_prob < 60:
            score += 15
        else:
            score += 5
        
        # Both teams good defense (0-20 points)
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        avg_defense = (home_defense + away_defense) / 2
        score += min(20, avg_defense * 2)
        
        # Low H2H goals history (0-15 points)
        if match_data["last_h2h_goals"] <= 2:
            score += 15
        elif match_data["last_h2h_goals"] <= 3:
            score += 10
        else:
            score += 5
        
        # Similar stakes (0-10 points)
        home_stakes = 10 - (match_data["home_position"] / 20 * 10)
        away_stakes = 10 - (match_data["away_position"] / 20 * 10)
        stakes_diff = abs(home_stakes - away_stakes)
        score += min(10, 10 - stakes_diff)
        
        return min(100, score)
    
    def predict_match(self, match_data):
        """Main prediction function for one match"""
        
        # Calculate all narrative scores
        scores = {
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "SIEGE": self.calculate_siege_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data)
        }
        
        # Determine dominant narrative
        dominant_narrative = max(scores, key=scores.get)
        dominant_score = scores[dominant_narrative]
        
        # Determine tier and confidence
        if dominant_score >= 75:
            tier = "TIER 1 (STRONG)"
            confidence = "High"
            stake = "2-3 units"
        elif dominant_score >= 60:
            tier = "TIER 2 (MEDIUM)"
            confidence = "Medium"
            stake = "1-2 units"
        elif dominant_score >= 50:
            tier = "TIER 3 (WEAK)"
            confidence = "Low"
            stake = "0.5-1 unit"
        else:
            tier = "TIER 4 (AVOID)"
            confidence = "Very Low"
            stake = "No bet"
        
        # Calculate expected goals
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_strength = prob["favorite_strength"]
        
        if dominant_narrative == "BLITZKRIEG":
            expected_goals = 3.2 if favorite_strength == "STRONG" else 2.8
            btts_prob = 40 if match_data["last_h2h_btts"] == "Yes" else 30
            over_25_prob = 70
        elif dominant_narrative == "SHOOTOUT":
            expected_goals = 3.5
            btts_prob = 75
            over_25_prob = 85
        elif dominant_narrative == "SIEGE":
            expected_goals = 2.1
            btts_prob = 40 if match_data["last_h2h_btts"] == "Yes" else 35
            over_25_prob = 30
        else:  # CHESS_MATCH
            expected_goals = 1.8
            btts_prob = 35 if match_data["last_h2h_btts"] == "Yes" else 30
            over_25_prob = 25
        
        # Generate betting recommendations
        narrative_info = self.narratives[dominant_narrative]
        
        return {
            "match": f"{match_data['home_team']} vs {match_data['away_team']}",
            "date": match_data["date"],
            "scores": scores,
            "dominant_narrative": dominant_narrative,
            "dominant_score": dominant_score,
            "tier": tier,
            "confidence": confidence,
            "expected_goals": expected_goals,
            "btts_probability": btts_prob,
            "over_25_probability": over_25_prob,
            "stake_recommendation": stake,
            "expected_flow": narrative_info["flow"],
            "betting_markets": narrative_info["betting_markets"],
            "description": narrative_info["description"]
        }

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine",
        page_icon="⚽",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 2rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .tier-1 {
        border-left: 5px solid #4CAF50;
    }
    .tier-2 {
        border-left: 5px solid #FF9800;
    }
    .tier-3 {
        border-left: 5px solid #F44336;
    }
    .score-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 5px 0;
    }
    .score-fill {
        height: 100%;
        border-radius: 10px;
        background-color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">⚽ NARRATIVE PREDICTION ENGINE</h1>', unsafe_allow_html=True)
    st.markdown("### **Upload CSV → Get Predictions**")
    
    # Initialize engine
    engine = NarrativePredictionEngine()
    
    # Create two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h3 class="sub-header">📤 Upload Match Data</h3>', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Successfully loaded {len(df)} matches")
                
                # Show data preview
                with st.expander("📊 Data Preview", expanded=False):
                    st.dataframe(df.head())
                
                # Select matches to predict
                st.markdown("### Select Matches to Predict")
                
                match_options = df.apply(lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", axis=1).tolist()
                selected_matches = st.multiselect("Choose matches", match_options, default=match_options[:3])
                
                # Process selected matches
                if st.button("🚀 Generate Predictions", type="primary"):
                    predictions = []
                    
                    with st.spinner("Analyzing matches..."):
                        for match_str in selected_matches:
                            # Find the match in dataframe
                            match_idx = match_options.index(match_str)
                            match_row = df.iloc[match_idx]
                            
                            # Convert row to match_data dict
                            match_data = {
                                "home_team": match_row["home_team"],
                                "away_team": match_row["away_team"],
                                "date": match_row["date"],
                                "home_position": match_row["home_position"],
                                "away_position": match_row["away_position"],
                                "home_odds": match_row["home_odds"],
                                "away_odds": match_row["away_odds"],
                                "home_form": match_row["home_form"],
                                "away_form": match_row["away_form"],
                                "home_manager": match_row["home_manager"],
                                "away_manager": match_row["away_manager"],
                                "last_h2h_goals": match_row["last_h2h_goals"],
                                "last_h2h_btts": match_row["last_h2h_btts"],
                                "home_attack_rating": match_row["home_attack_rating"],
                                "away_attack_rating": match_row["away_attack_rating"],
                                "home_defense_rating": match_row["home_defense_rating"],
                                "away_defense_rating": match_row["away_defense_rating"],
                                "home_press_rating": match_row["home_press_rating"],
                                "away_press_rating": match_row["away_press_rating"],
                                "home_possession_rating": match_row["home_possession_rating"],
                                "away_possession_rating": match_row["away_possession_rating"],
                                "home_pragmatic_rating": match_row["home_pragmatic_rating"],
                                "away_pragmatic_rating": match_row["away_pragmatic_rating"]
                            }
                            
                            # Get prediction
                            prediction = engine.predict_match(match_data)
                            predictions.append(prediction)
                    
                    # Store predictions in session state
                    st.session_state.predictions = predictions
                    
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
                st.info("Make sure your CSV has the correct columns from our template.")
        
        else:
            st.info("👆 **Upload your match data CSV**")
            st.markdown("### CSV Format Required:")
            st.code("""match_id,league,date,home_team,away_team,home_position,away_position,home_odds,away_odds,home_form,away_form,home_manager,away_manager,last_h2h_goals,last_h2h_btts,home_manager_style,away_manager_style,home_attack_rating,away_attack_rating,home_defense_rating,away_defense_rating,home_press_rating,away_press_rating,home_possession_rating,away_possession_rating,home_pragmatic_rating,away_pragmatic_rating""")
            
            # Sample data download
            st.markdown("### 📥 Download Sample CSV")
            sample_data = pd.DataFrame([{
                "match_id": "EPL_2025-12-20_NEW_CHE",
                "league": "Premier League",
                "date": "2025-12-20",
                "home_team": "Newcastle United",
                "away_team": "Chelsea",
                "home_position": 12,
                "away_position": 4,
                "home_odds": 2.68,
                "away_odds": 2.57,
                "home_form": "WWWWL",
                "away_form": "DWWWD",
                "home_manager": "Eddie Howe",
                "away_manager": "Enzo Maresca",
                "last_h2h_goals": 2,
                "last_h2h_btts": "No",
                "home_manager_style": "High press & transition",
                "away_manager_style": "Possession-based & control",
                "home_attack_rating": 9,
                "away_attack_rating": 8,
                "home_defense_rating": 6,
                "away_defense_rating": 7,
                "home_press_rating": 9,
                "away_press_rating": 7,
                "home_possession_rating": 7,
                "away_possession_rating": 9,
                "home_pragmatic_rating": 5,
                "away_pragmatic_rating": 6
            }])
            
            csv = sample_data.to_csv(index=False)
            st.download_button(
                label="Download Sample CSV",
                data=csv,
                file_name="sample_match_data.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown('<h3 class="sub-header">🎯 Prediction Results</h3>', unsafe_allow_html=True)
        
        if "predictions" in st.session_state and st.session_state.predictions:
            predictions = st.session_state.predictions
            
            for i, pred in enumerate(predictions):
                # Determine tier class
                tier_class = ""
                if pred["tier"] == "TIER 1 (STRONG)":
                    tier_class = "tier-1"
                elif pred["tier"] == "TIER 2 (MEDIUM)":
                    tier_class = "tier-2"
                else:
                    tier_class = "tier-3"
                
                st.markdown(f'<div class="prediction-card {tier_class}">', unsafe_allow_html=True)
                
                # Match header
                st.markdown(f"### **{pred['match']}**")
                st.markdown(f"**Date:** {pred['date']} | **Tier:** {pred['tier']} | **Confidence:** {pred['confidence']}")
                
                # Narrative prediction
                col_pred1, col_pred2 = st.columns(2)
                
                with col_pred1:
                    st.metric(
                        "Predicted Narrative",
                        pred["dominant_narrative"],
                        delta=f"Score: {pred['dominant_score']:.1f}/100"
                    )
                    
                    # Narrative scores visualization
                    st.markdown("**All Narrative Scores:**")
                    for narrative, score in pred["scores"].items():
                        st.markdown(f"{narrative}:")
                        st.markdown(f'<div class="score-bar"><div class="score-fill" style="width: {score}%"></div></div>', unsafe_allow_html=True)
                        st.markdown(f"<small>{score:.1f}/100</small>", unsafe_allow_html=True)
                
                with col_pred2:
                    # Key stats
                    st.markdown("**Key Statistics:**")
                    st.write(f"**Expected Goals:** {pred['expected_goals']:.1f}")
                    st.write(f"**BTTS Probability:** {pred['btts_probability']}%")
                    st.write(f"**Over 2.5 Probability:** {pred['over_25_probability']}%")
                    st.write(f"**Recommended Stake:** {pred['stake_recommendation']}")
                
                # Expected flow
                with st.expander("📈 Expected Match Flow", expanded=False):
                    st.write(pred["expected_flow"])
                
                # Betting recommendations
                st.markdown("**💰 Betting Recommendations:**")
                for j, bet in enumerate(pred["betting_markets"], 1):
                    st.write(f"{j}. {bet}")
                
                # Narrative description
                st.info(f"**Insight:** {pred['description']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export predictions
            st.markdown("---")
            st.markdown("### 📊 Export Predictions")
            
            if st.button("Export to CSV"):
                export_df = pd.DataFrame([{
                    "Match": p["match"],
                    "Date": p["date"],
                    "Predicted_Narrative": p["dominant_narrative"],
                    "Narrative_Score": p["dominant_score"],
                    "Tier": p["tier"],
                    "Confidence": p["confidence"],
                    "Expected_Goals": p["expected_goals"],
                    "BTTS_Probability": p["btts_probability"],
                    "Over_25_Probability": p["over_25_probability"],
                    "Stake_Recommendation": p["stake_recommendation"]
                } for p in predictions])
                
                csv_export = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download Predictions CSV",
                    data=csv_export,
                    file_name=f"narrative_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.info("👈 **Upload a CSV file and generate predictions to see results here**")
            
            # Show example prediction
            st.markdown("### Example Prediction:")
            st.markdown('<div class="prediction-card tier-1">', unsafe_allow_html=True)
            st.markdown("#### **Manchester City vs West Ham**")
            st.markdown("**Predicted Narrative:** BLITZKRIEG")
            st.markdown("**Score:** 85.3/100 | **Tier:** TIER 1 | **Confidence:** High")
            st.markdown("**Expected Flow:** Early pressure from City, breakthrough before 30 mins, opponent collapses")
            st.markdown("**Betting Recommendations:**")
            st.write("1. Manchester City -2.5 handicap")
            st.write("2. Manchester City clean sheet")
            st.write("3. First goal before 25:00")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
