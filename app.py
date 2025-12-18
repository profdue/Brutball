import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class NarrativePredictionEngine:
    """Core prediction engine with all our tested logic - FIXED VERSION"""
    
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
        
        # Narrative definitions - UPDATED with better flow descriptions
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "flow": "• Early pressure from favorite (0-15 mins)\n• Breakthrough before 30 mins\n• Opponent confidence collapses after first goal\n• Additional goals in 35-65 minute window\n• Game effectively over by 70 mins",
                "betting_markets": ["Favorite to win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals for favorite", "Favorite -1.5 Asian handicap"]
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "betting_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"]
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "betting_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"]
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both teams (0-30 mins)\n• Midfield battle dominates, few clear chances\n• Set pieces become primary scoring threats\n• First goal (if any) often decisive\n• Late tactical changes unlikely to alter outcome significantly",
                "betting_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0 correct score", "Few goals first half", "Under 1.5 goals"]
            }
        }
    
    def calculate_favorite_probability(self, home_odds, away_odds):
        """Convert odds to implied probabilities"""
        if home_odds <= 0 or away_odds <= 0:
            return {
                "home_probability": 50,
                "away_probability": 50,
                "favorite_probability": 50,
                "favorite_is_home": True,
                "favorite_strength": "EVEN"
            }
        
        home_implied = 1 / home_odds
        away_implied = 1 / away_odds
        total = home_implied + away_implied
        
        home_prob = home_implied / total * 100
        away_prob = away_implied / total * 100
        
        favorite_prob = max(home_prob, away_prob)
        favorite_is_home = home_prob > away_prob
        
        # Strength classification
        if favorite_prob >= 70:
            strength = "STRONG"
        elif favorite_prob >= 60:
            strength = "MODERATE"
        elif favorite_prob >= 55:
            strength = "SLIGHT"
        else:
            strength = "EVEN"
        
        return {
            "home_probability": home_prob,
            "away_probability": away_prob,
            "favorite_probability": favorite_prob,
            "favorite_is_home": favorite_is_home,
            "favorite_strength": strength,
            "odds_gap": abs(home_odds - away_odds)
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
        rating = (avg_points / 2) * 10  # Convert to 0-10 scale
        
        # Determine trend
        recent = form_string[-3:] if len(form_string) >= 3 else form_string
        win_count = recent.count('W') + recent.count('w')
        
        if win_count >= 2:
            trend = "improving"
        elif 'W' not in recent and 'w' not in recent:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "rating": min(10, rating),
            "confidence": min(10, len(form_string) * 2),
            "trend": trend,
            "points": points,
            "games": len(form_string)
        }
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score (0-100) - FIXED"""
        score = 0
        
        # 1. FAVORITE STRENGTH (0-40 points) - INCREASED WEIGHT
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        
        if favorite_prob >= 70:
            score += 40  # STRONG favorite
        elif favorite_prob >= 60:
            score += 25  # MODERATE favorite
        elif favorite_prob >= 55:
            score += 10  # SLIGHT favorite
        
        # 2. ODDS GAP (0-20 points) - NEW FACTOR
        odds_gap = abs(match_data["home_odds"] - match_data["away_odds"])
        if odds_gap >= 2.0:
            score += 20  # Big mismatch
        elif odds_gap >= 1.0:
            score += 15  # Moderate mismatch
        elif odds_gap >= 0.5:
            score += 5   # Slight mismatch
        
        # 3. FORM MISMATCH (0-20 points)
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        form_diff = abs(home_form - away_form)
        score += min(20, form_diff * 2)
        
        # 4. ATTACK vs DEFENSE MISMATCH (0-20 points)
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        attack_defense_diff = home_attack - (10 - away_defense)  # Positive = attacker advantage
        if attack_defense_diff >= 3:
            score += 20
        elif attack_defense_diff >= 2:
            score += 15
        elif attack_defense_diff >= 1:
            score += 10
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score (0-100) - FIXED"""
        score = 0
        
        # 1. BOTH ATTACKING (0-30 points)
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        
        if home_attack >= 8 and away_attack >= 8:
            score += 30  # Both extremely attacking
        elif home_attack >= 7 and away_attack >= 7:
            score += 20  # Both attacking
        elif home_attack >= 6 and away_attack >= 6:
            score += 10  # Both moderately attacking
        
        # 2. BOTH WEAK DEFENSE (0-25 points)
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        if home_defense <= 6 and away_defense <= 6:
            score += 25  # Both weak defense
        elif home_defense <= 7 or away_defense <= 7:
            score += 15  # At least one weak defense
        
        # 3. HIGH PRESS BOTH (0-20 points)
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        
        if home_press >= 8 and away_press >= 8:
            score += 20  # Both high press
        elif home_press >= 7 or away_press >= 7:
            score += 10  # At least one high press
        
        # 4. RECENT HIGH SCORING (0-15 points) - MORE WEIGHT
        if match_data["last_h2h_goals"] >= 4:
            score += 15
        elif match_data["last_h2h_goals"] >= 3:
            score += 10
        elif match_data["last_h2h_goals"] >= 2:
            score += 5
        
        # 5. BTTS HISTORY (0-10 points)
        if match_data["last_h2h_btts"] == "Yes":
            score += 10
        
        return min(100, score)
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score (0-100) - FIXED"""
        score = 0
        
        # 1. POSSESSION/ATTACK MISMATCH (0-30 points)
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        home_possession = match_data["home_possession_rating"]
        
        # Strong attacker vs strong defender
        if home_attack >= 8 and away_defense >= 8:
            score += 30  # Classic siege scenario
        elif home_attack >= 7 and away_defense >= 7:
            score += 20
        elif abs(home_attack - away_defense) >= 3:
            score += 15  # Big mismatch
        
        # 2. FAVORITE AT HOME (0-25 points)
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if prob["favorite_is_home"] and prob["favorite_probability"] >= 65:
            score += 25  # Strong home favorite
        elif prob["favorite_is_home"] and prob["favorite_probability"] >= 55:
            score += 15
        
        # 3. PRAGMATIC vs ATTACKING (0-20 points)
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic <= 5 and away_pragmatic >= 7:  # Attacker vs Pragmatic defender
            score += 20
        elif abs(home_pragmatic - away_pragmatic) >= 3:
            score += 15
        
        # 4. LOW H2H GOALS (0-15 points)
        if match_data["last_h2h_goals"] <= 1:
            score += 15
        elif match_data["last_h2h_goals"] <= 2:
            score += 10
        elif match_data["last_h2h_goals"] <= 3:
            score += 5
        
        # 5. FORM DOMINANCE (0-10 points)
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        if home_form - away_form >= 2:
            score += 10
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score (0-100) - FIXED"""
        score = 0
        
        # 1. CLOSE MATCH (0-30 points) - MOST IMPORTANT
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        
        if favorite_prob < 52:  # Very close match
            score += 30
        elif favorite_prob < 55:  # Close match
            score += 20
        elif favorite_prob < 58:  # Slight favorite
            score += 10
        
        # 2. BOTH MANAGERS PRAGMATIC (0-25 points)
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic >= 7 and away_pragmatic >= 7:
            score += 25  # Both pragmatic
        elif home_pragmatic >= 6 and away_pragmatic >= 6:
            score += 15  # Both somewhat pragmatic
        
        # 3. BOTH GOOD DEFENSE (0-20 points)
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        if home_defense >= 8 and away_defense >= 8:
            score += 20  # Both strong defense
        elif home_defense >= 7 and away_defense >= 7:
            score += 10  # Both decent defense
        
        # 4. LOW H2H GOALS HISTORY (0-15 points)
        if match_data["last_h2h_goals"] <= 2:
            score += 15
        elif match_data["last_h2h_goals"] <= 3:
            score += 10
        else:
            score += 0  # High scoring history = not chess match
        
        # 5. SIMILAR STAKES (0-10 points)
        home_stakes = 10 - (match_data["home_position"] / 20 * 10)
        away_stakes = 10 - (match_data["away_position"] / 20 * 10)
        stakes_diff = abs(home_stakes - away_stakes)
        if stakes_diff <= 2:
            score += 10  # Similar stakes
        
        return min(100, score)
    
    def debug_match_scoring(self, match_data):
        """Show detailed scoring breakdown for debugging"""
        debug_info = {}
        
        # Calculate all scores
        scores = {
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "SIEGE": self.calculate_siege_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data)
        }
        
        # Get probability info
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        debug_info = {
            "match": f"{match_data['home_team']} vs {match_data['away_team']}",
            "probabilities": prob,
            "scores": scores,
            "prediction": max(scores, key=scores.get),
            "home_form_rating": self.analyze_form(match_data["home_form"])["rating"],
            "away_form_rating": self.analyze_form(match_data["away_form"])["rating"]
        }
        
        return debug_info
    
    def predict_match(self, match_data):
        """Main prediction function for one match - FIXED"""
        
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
        
        # Calculate expected goals based on narrative
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if dominant_narrative == "BLITZKRIEG":
            if prob["favorite_strength"] == "STRONG":
                expected_goals = 3.5
                btts_prob = 30
                over_25_prob = 80
            else:
                expected_goals = 3.0
                btts_prob = 40
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
            "description": narrative_info["description"],
            "debug_info": self.debug_match_scoring(match_data)  # For troubleshooting
        }

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.0",
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
        background-color: #f1f8e9;
    }
    .tier-2 {
        border-left: 5px solid #FF9800;
        background-color: #fff3e0;
    }
    .tier-3 {
        border-left: 5px solid #F44336;
        background-color: #ffebee;
    }
    .score-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 5px 0;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        border-radius: 10px;
        background-color: #1E88E5;
        transition: width 0.5s ease;
    }
    .blitzkrieg-fill { background-color: #4CAF50; }
    .shootout-fill { background-color: #FF5722; }
    .siege-fill { background-color: #2196F3; }
    .chess-fill { background-color: #9C27B0; }
    .debug-info {
        font-size: 0.8rem;
        color: #666;
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">⚽ NARRATIVE PREDICTION ENGINE v2.0</h1>', unsafe_allow_html=True)
    st.markdown("### **Fixed Scoring Formulas • Better Predictions • Clear Insights**")
    
    # Initialize engine
    engine = NarrativePredictionEngine()
    
    # Create two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h3 class="sub-header">📤 Upload Match Data</h3>', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
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
                selected_matches = st.multiselect("Choose matches", match_options, default=match_options)
                
                # Debug mode toggle
                debug_mode = st.checkbox("🔍 Enable Debug Mode (Show Scoring Details)")
                
                # Process selected matches
                if st.button("🚀 Generate Predictions", type="primary", key="predict_button"):
                    predictions = []
                    debug_data = []
                    
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
                                "home_position": int(match_row["home_position"]),
                                "away_position": int(match_row["away_position"]),
                                "home_odds": float(match_row["home_odds"]),
                                "away_odds": float(match_row["away_odds"]),
                                "home_form": str(match_row["home_form"]),
                                "away_form": str(match_row["away_form"]),
                                "home_manager": match_row["home_manager"],
                                "away_manager": match_row["away_manager"],
                                "last_h2h_goals": int(match_row["last_h2h_goals"]),
                                "last_h2h_btts": str(match_row["last_h2h_btts"]),
                                "home_attack_rating": int(match_row["home_attack_rating"]),
                                "away_attack_rating": int(match_row["away_attack_rating"]),
                                "home_defense_rating": int(match_row["home_defense_rating"]),
                                "away_defense_rating": int(match_row["away_defense_rating"]),
                                "home_press_rating": int(match_row["home_press_rating"]),
                                "away_press_rating": int(match_row["away_press_rating"]),
                                "home_possession_rating": int(match_row["home_possession_rating"]),
                                "away_possession_rating": int(match_row["away_possession_rating"]),
                                "home_pragmatic_rating": int(match_row["home_pragmatic_rating"]),
                                "away_pragmatic_rating": int(match_row["away_pragmatic_rating"])
                            }
                            
                            # Get prediction
                            prediction = engine.predict_match(match_data)
                            predictions.append(prediction)
                            
                            # Store debug data if enabled
                            if debug_mode:
                                debug_data.append(prediction["debug_info"])
                    
                    # Store predictions in session state
                    st.session_state.predictions = predictions
                    if debug_mode:
                        st.session_state.debug_data = debug_data
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV: {str(e)}")
                st.info("Make sure your CSV has the correct columns and data types.")
                st.code("""Required columns:
match_id,league,date,home_team,away_team,home_position,away_position,home_odds,away_odds,
home_form,away_form,home_manager,away_manager,last_h2h_goals,last_h2h_btts,
home_manager_style,away_manager_style,home_attack_rating,away_attack_rating,
home_defense_rating,away_defense_rating,home_press_rating,away_press_rating,
home_possession_rating,away_possession_rating,home_pragmatic_rating,away_pragmatic_rating""")
        
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
                mime="text/csv",
                key="sample_download"
            )
    
    with col2:
        st.markdown('<h3 class="sub-header">🎯 Prediction Results</h3>', unsafe_allow_html=True)
        
        if "predictions" in st.session_state and st.session_state.predictions:
            predictions = st.session_state.predictions
            
            # Summary statistics
            if len(predictions) > 1:
                narratives_count = {}
                for pred in predictions:
                    narrative = pred["dominant_narrative"]
                    narratives_count[narrative] = narratives_count.get(narrative, 0) + 1
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    st.metric("Total Matches", len(predictions))
                with col_sum2:
                    st.metric("Tier 1 Predictions", sum(1 for p in predictions if p["tier"] == "TIER 1 (STRONG)"))
                with col_sum3:
                    most_common = max(narratives_count, key=narratives_count.get) if narratives_count else "None"
                    st.metric("Most Common Narrative", most_common)
            
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
                    # Color-coded narrative badge
                    narrative_colors = {
                        "BLITZKRIEG": "#4CAF50",
                        "SHOOTOUT": "#FF5722", 
                        "SIEGE": "#2196F3",
                        "CHESS_MATCH": "#9C27B0"
                    }
                    
                    narrative_color = narrative_colors.get(pred["dominant_narrative"], "#1E88E5")
                    
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: {narrative_color}20; border-radius: 5px; border-left: 4px solid {narrative_color};">
                        <h4 style="margin: 0; color: {narrative_color};">{pred['dominant_narrative']}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold;">Score: {pred['dominant_score']:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Narrative scores visualization
                    st.markdown("**All Narrative Scores:**")
                    for narrative, score in pred["scores"].items():
                        fill_class = f"{narrative.lower().replace(' ', '-')}-fill"
                        st.markdown(f"**{narrative}:**")
                        st.markdown(f'<div class="score-bar"><div class="score-fill {fill_class}" style="width: {score}%"></div></div>', unsafe_allow_html=True)
                        st.markdown(f"<small>{score:.1f}/100</small>", unsafe_allow_html=True)
                
                with col_pred2:
                    # Key stats
                    st.markdown("**📊 Key Statistics:**")
                    st.write(f"**Expected Goals:** {pred['expected_goals']:.1f}")
                    st.write(f"**BTTS Probability:** {pred['btts_probability']}%")
                    st.write(f"**Over 2.5 Probability:** {pred['over_25_probability']}%")
                    st.write(f"**Recommended Stake:** {pred['stake_recommendation']}")
                    
                    # Quick insights
                    st.markdown("**💡 Quick Insights:**")
                    st.write(pred["description"])
                
                # Expected flow
                with st.expander("📈 Expected Match Flow", expanded=False):
                    st.write(pred["expected_flow"])
                
                # Betting recommendations
                st.markdown("**💰 Betting Recommendations:**")
                rec_cols = st.columns(2)
                for j, bet in enumerate(pred["betting_markets"]):
                    with rec_cols[j % 2]:
                        st.write(f"• {bet}")
                
                # Debug info if enabled
                if debug_mode and "debug_data" in st.session_state and i < len(st.session_state.debug_data):
                    debug_info = st.session_state.debug_data[i]
                    with st.expander("🔍 Debug Scoring Details", expanded=False):
                        st.write(f"**Match:** {debug_info['match']}")
                        st.write(f"**Favorite Probability:** {debug_info['probabilities']['favorite_probability']:.1f}%")
                        st.write(f"**Favorite Strength:** {debug_info['probabilities']['favorite_strength']}")
                        st.write(f"**Home Form Rating:** {debug_info['home_form_rating']:.1f}/10")
                        st.write(f"**Away Form Rating:** {debug_info['away_form_rating']:.1f}/10")
                        st.write(f"**Final Prediction:** {debug_info['prediction']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export predictions
            st.markdown("---")
            st.markdown("### 📊 Export Predictions")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("Export to CSV", key="export_csv"):
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
                        "Stake_Recommendation": p["stake_recommendation"],
                        "Betting_Market_1": p["betting_markets"][0] if len(p["betting_markets"]) > 0 else "",
                        "Betting_Market_2": p["betting_markets"][1] if len(p["betting_markets"]) > 1 else "",
                        "Betting_Market_3": p["betting_markets"][2] if len(p["betting_markets"]) > 2 else ""
                    } for p in predictions])
                    
                    csv_export = export_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Predictions CSV",
                        data=csv_export,
                        file_name=f"narrative_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_predictions"
                    )
            
            with col_export2:
                if st.button("Clear Predictions", key="clear_predictions"):
                    st.session_state.predictions = None
                    if "debug_data" in st.session_state:
                        st.session_state.debug_data = None
                    st.rerun()
        
        else:
            st.info("👈 **Upload a CSV file and generate predictions to see results here**")
            
            # Show example prediction
            st.markdown("### 🎯 Example Prediction:")
            st.markdown('<div class="prediction-card tier-1">', unsafe_allow_html=True)
            st.markdown("#### **Manchester City vs West Ham**")
            st.markdown("**Predicted Narrative:** BLITZKRIEG")
            st.markdown("**Score:** 88.5/100 | **Tier:** TIER 1 | **Confidence:** High")
            st.markdown("**Expected Flow:** Early pressure from City, breakthrough before 30 mins, opponent collapses")
            st.markdown("**Betting Recommendations:**")
            st.write("1. Manchester City -2.5 handicap")
            st.write("2. Manchester City clean sheet")
            st.write("3. First goal before 25:00")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
