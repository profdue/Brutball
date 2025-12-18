# app.py - Complete Narrative Prediction Engine v2.0

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

# ==============================================
# NARRATIVE PREDICTION ENGINE CORE
# ==============================================

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
                "betting_markets": ["Favorite to win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals for favorite", "Favorite -1.5 Asian handicap"],
                "color": "#4CAF50"
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "betting_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"],
                "color": "#FF5722"
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "betting_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"],
                "color": "#2196F3"
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both teams (0-30 mins)\n• Midfield battle dominates, few clear chances\n• Set pieces become primary scoring threats\n• First goal (if any) often decisive\n• Late tactical changes unlikely to alter outcome significantly",
                "betting_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0 correct score", "Few goals first half", "Under 1.5 goals"],
                "color": "#9C27B0"
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
            btts_prob = 40 if match_data.get("last_h2h_btts", "No") == "Yes" else 35
            over_25_prob = 30
        else:  # CHESS_MATCH
            expected_goals = 1.8
            btts_prob = 35 if match_data.get("last_h2h_btts", "No") == "Yes" else 30
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
            "narrative_color": narrative_info["color"],
            "probabilities": prob
        }

# ==============================================
# STREAMLIT APP MAIN FUNCTION
# ==============================================

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.0",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS with improved styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #424242;
        margin-top: 1.5rem;
        font-weight: 600;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 0.5rem;
    }
    .prediction-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .prediction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .tier-1 {
        border-top: 4px solid #4CAF50;
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
    }
    .tier-2 {
        border-top: 4px solid #FF9800;
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    }
    .tier-3 {
        border-top: 4px solid #F44336;
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    }
    .tier-4 {
        border-top: 4px solid #9E9E9E;
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
    }
    .score-bar {
        height: 12px;
        background-color: #e0e0e0;
        border-radius: 6px;
        margin: 5px 0 8px 0;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    .score-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.8s ease;
    }
    .blitzkrieg-fill { background: linear-gradient(90deg, #4CAF50, #81C784); }
    .shootout-fill { background: linear-gradient(90deg, #FF5722, #FF8A65); }
    .siege-fill { background: linear-gradient(90deg, #2196F3, #64B5F6); }
    .chess-fill { background: linear-gradient(90deg, #9C27B0, #BA68C8); }
    .stake-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .stake-high { background-color: #4CAF50; color: white; }
    .stake-medium { background-color: #FF9800; color: white; }
    .stake-low { background-color: #F44336; color: white; }
    .stake-none { background-color: #9E9E9E; color: white; }
    .narrative-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
        margin: 5px;
    }
    .betting-market {
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        border-left: 4px solid #1E88E5;
    }
    .export-section {
        background: linear-gradient(135deg, #E3F2FD 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid #BBDEFB;
    }
    .debug-info {
        font-size: 0.85rem;
        color: #666;
        background-color: #fafafa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        border: 1px solid #E0E0E0;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header
    st.markdown('<h1 class="main-header">⚽ NARRATIVE PREDICTION ENGINE v2.0</h1>', unsafe_allow_html=True)
    st.markdown("### **Fixed Scoring Formulas • Better Predictions • Clear Insights • CSV Ready**")
    
    # Initialize engine
    engine = NarrativePredictionEngine()
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown('<h3 class="sub-header">⚙️ Configuration</h3>', unsafe_allow_html=True)
        
        # Data source selection
        data_source = st.radio(
            "Select Data Source",
            ["Upload CSV File", "Use Sample Data", "GitHub URL"],
            index=0
        )
        
        # File upload section
        if data_source == "Upload CSV File":
            st.markdown("### 📤 Upload Match Data")
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=["csv"],
                help="Upload your premier_league_matches.csv file"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Successfully loaded {len(df)} matches")
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {str(e)}")
                    df = None
            else:
                df = None
                st.info("👆 Upload your match data CSV")
        
        elif data_source == "Use Sample Data":
            st.info("Using built-in sample data")
            # Create sample dataframe
            sample_data = [{
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
            }]
            df = pd.DataFrame(sample_data)
            st.success(f"✅ Loaded {len(df)} sample matches")
        
        else:  # GitHub URL
            st.markdown("### 🔗 GitHub CSV URL")
            github_url = st.text_input(
                "Enter raw GitHub CSV URL",
                value="https://raw.githubusercontent.com/username/repo/main/premier_league_matches.csv",
                help="Enter the raw URL to your CSV file on GitHub"
            )
            
            if st.button("Load from GitHub", type="primary"):
                try:
                    df = pd.read_csv(github_url)
                    st.success(f"✅ Successfully loaded {len(df)} matches from GitHub")
                except Exception as e:
                    st.error(f"❌ Error loading from GitHub: {str(e)}")
                    st.info("Make sure you're using the raw GitHub URL")
                    df = None
            else:
                df = None
        
        # Analysis settings
        st.markdown('<h3 class="sub-header">🔧 Analysis Settings</h3>', unsafe_allow_html=True)
        
        debug_mode = st.checkbox("🔍 Enable Debug Mode", value=False, 
                                help="Show detailed scoring calculations")
        
        show_visualizations = st.checkbox("📊 Show Visualizations", value=True,
                                         help="Display charts and graphs")
        
        auto_generate = st.checkbox("🚀 Auto-generate on load", value=True,
                                   help="Automatically generate predictions when data loads")
        
        # Navigation
        st.markdown("---")
        st.markdown("### 📋 Navigation")
        page = st.radio("Go to", ["Predictions", "Manager Database", "Narrative Guide", "Export"])
        
        # About section
        with st.expander("ℹ️ About this Engine"):
            st.write("""
            **Narrative Prediction Engine v2.0**
            
            This engine analyzes football matches using 4 narrative archetypes:
            1. **BLITZKRIEG** - Early domination by favorite
            2. **SHOOTOUT** - End-to-end attacking chaos
            3. **SIEGE** - Attack vs defense stalemate
            4. **CHESS MATCH** - Tactical, low-scoring affair
            
            Uses: Form analysis, odds conversion, tactical ratings, and historical data.
            """)
    
    # Main content area
    if df is not None:
        # Data preview
        with st.expander("📊 Data Preview (First 5 Rows)", expanded=False):
            st.dataframe(df.head(), use_container_width=True)
            
            # Data info
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Total Matches", len(df))
            with col_info2:
                st.metric("Columns", len(df.columns))
            with col_info3:
                st.metric("Date Range", f"{df['date'].min()} to {df['date'].max()}")
        
        # Match selection
        st.markdown('<h3 class="sub-header">🎯 Select Matches to Predict</h3>', unsafe_allow_html=True)
        
        # Create match selection options
        if 'home_team' in df.columns and 'away_team' in df.columns:
            match_options = df.apply(
                lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", 
                axis=1
            ).tolist()
            
            # Default to all matches
            selected_matches = st.multiselect(
                "Choose matches to analyze",
                match_options,
                default=match_options[:min(5, len(match_options))] if len(match_options) > 5 else match_options,
                help="Select matches to generate predictions for"
            )
            
            # Prediction button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                predict_button = st.button("🚀 Generate Predictions", type="primary", use_container_width=True)
            with col_btn2:
                clear_button = st.button("🗑️ Clear Results", use_container_width=True)
            
            if clear_button:
                if "predictions" in st.session_state:
                    del st.session_state.predictions
                if "debug_data" in st.session_state:
                    del st.session_state.debug_data
                st.rerun()
            
            # Generate predictions
            if predict_button or (auto_generate and selected_matches):
                with st.spinner(f"🔮 Analyzing {len(selected_matches)} matches..."):
                    predictions = []
                    
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
                    
                    # Store predictions in session state
                    st.session_state.predictions = predictions
                    st.success(f"✅ Generated predictions for {len(predictions)} matches")
        
        else:
            st.error("❌ CSV file must contain 'home_team' and 'away_team' columns")
            st.stop()
    
    # Display predictions if available
    if "predictions" in st.session_state and st.session_state.predictions:
        predictions = st.session_state.predictions
        
        # Summary dashboard
        st.markdown('<h3 class="sub-header">📈 Prediction Dashboard</h3>', unsafe_allow_html=True)
        
        # Summary statistics
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            tier1_count = sum(1 for p in predictions if p["tier"] == "TIER 1 (STRONG)")
            st.metric("🎯 Tier 1 Predictions", tier1_count)
        
        with col_sum2:
            narratives_count = {}
            for pred in predictions:
                narrative = pred["dominant_narrative"]
                narratives_count[narrative] = narratives_count.get(narrative, 0) + 1
            most_common = max(narratives_count, key=narratives_count.get) if narratives_count else "None"
            st.metric("📊 Most Common Narrative", most_common)
        
        with col_sum3:
            avg_confidence = sum(p["dominant_score"] for p in predictions) / len(predictions)
            st.metric("📈 Average Confidence", f"{avg_confidence:.1f}/100")
        
        with col_sum4:
            total_stake_units = 0
            for p in predictions:
                if "2-3" in p["stake_recommendation"]:
                    total_stake_units += 2.5
                elif "1-2" in p["stake_recommendation"]:
                    total_stake_units += 1.5
                elif "0.5-1" in p["stake_recommendation"]:
                    total_stake_units += 0.75
            st.metric("💰 Total Stake Units", f"{total_stake_units:.1f}")
        
        # Visualization if enabled
        if show_visualizations and len(predictions) > 1:
            # Create narrative distribution chart
            narrative_counts = {}
            for pred in predictions:
                narrative = pred["dominant_narrative"]
                narrative_counts[narrative] = narrative_counts.get(narrative, 0) + 1
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(narrative_counts.keys()),
                    y=list(narrative_counts.values()),
                    marker_color=[engine.narratives[n]["color"] for n in narrative_counts.keys()],
                    text=list(narrative_counts.values()),
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="Narrative Distribution",
                xaxis_title="Narrative",
                yaxis_title="Count",
                template="plotly_white",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Individual match predictions
        st.markdown('<h3 class="sub-header">🎯 Detailed Match Predictions</h3>', unsafe_allow_html=True)
        
        for i, pred in enumerate(predictions):
            # Determine tier class
            if pred["tier"] == "TIER 1 (STRONG)":
                tier_class = "tier-1"
                stake_badge_class = "stake-high"
            elif pred["tier"] == "TIER 2 (MEDIUM)":
                tier_class = "tier-2"
                stake_badge_class = "stake-medium"
            elif pred["tier"] == "TIER 3 (WEAK)":
                tier_class = "tier-3"
                stake_badge_class = "stake-low"
            else:
                tier_class = "tier-4"
                stake_badge_class = "stake-none"
            
            # Create prediction card
            st.markdown(f'<div class="prediction-card {tier_class}">', unsafe_allow_html=True)
            
            # Match header with narrative badge
            col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
            
            with col_header1:
                st.markdown(f"### **{pred['match']}**")
                st.markdown(f"**Date:** {pred['date']} | **League:** Premier League")
            
            with col_header2:
                narrative_color = pred["narrative_color"]
                st.markdown(
                    f'<div class="narrative-badge" style="background-color: {narrative_color}20; color: {narrative_color}; border: 1px solid {narrative_color};">'
                    f'<strong>{pred["dominant_narrative"]}</strong></div>',
                    unsafe_allow_html=True
                )
            
            with col_header3:
                st.markdown(f'<div class="stake-badge {stake_badge_class}">{pred["stake_recommendation"]}</div>', unsafe_allow_html=True)
                st.markdown(f"**Confidence:** {pred['confidence']}")
            
            # Main content columns
            col_main1, col_main2 = st.columns([1, 1])
            
            with col_main1:
                st.markdown("#### 📊 Narrative Scores")
                
                # Display all narrative scores with progress bars
                for narrative, score in pred["scores"].items():
                    fill_class = f"{narrative.lower().replace(' ', '-')}-fill"
                    st.markdown(f"**{narrative}:**")
                    st.markdown(f'<div class="score-bar"><div class="score-fill {fill_class}" style="width: {score}%"></div></div>', unsafe_allow_html=True)
                    st.markdown(f"<small>{score:.1f}/100</small>", unsafe_allow_html=True)
                
                # Key stats in cards
                st.markdown("#### 📈 Key Statistics")
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                    st.markdown("**Expected Goals**")
                    st.markdown(f"### {pred['expected_goals']:.1f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_stats2:
                    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                    st.markdown("**BTTS Probability**")
                    st.markdown(f"### {pred['btts_probability']}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_stats3:
                    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                    st.markdown("**Over 2.5 Probability**")
                    st.markdown(f"### {pred['over_25_probability']}%")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col_main2:
                st.markdown("#### 💡 Quick Insights")
                st.info(pred["description"])
                
                # Expected flow
                with st.expander("📈 Expected Match Flow", expanded=False):
                    st.write(pred["expected_flow"])
                
                # Betting recommendations
                st.markdown("#### 💰 Betting Recommendations")
                for j, bet in enumerate(pred["betting_markets"]):
                    st.markdown(f'<div class="betting-market">✓ {bet}</div>', unsafe_allow_html=True)
            
            # Debug info if enabled
            if debug_mode:
                with st.expander("🔍 Debug Scoring Details", expanded=False):
                    st.json(pred["probabilities"])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export section
        if page == "Export" or len(predictions) > 0:
            st.markdown('<div class="export-section">', unsafe_allow_html=True)
            st.markdown("### 📊 Export Predictions")
            
            # Create export dataframe
            export_data = []
            for p in predictions:
                export_data.append({
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
                    "Betting_Market_3": p["betting_markets"][2] if len(p["betting_markets"]) > 2 else "",
                    "Expected_Flow_Summary": p["description"]
                })
            
            export_df = pd.DataFrame(export_data)
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                # Download as CSV
                csv = export_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="narrative_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv">📥 Download as CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            with col_exp2:
                # Display export preview
                with st.expander("Preview Export Data"):
                    st.dataframe(export_df, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif page == "Manager Database":
        # Manager database viewer
        st.markdown('<h3 class="sub-header">👔 Manager Style Database</h3>', unsafe_allow_html=True)
        
        manager_df = pd.DataFrame.from_dict(engine.manager_db, orient='index').reset_index()
        manager_df = manager_df.rename(columns={"index": "Manager"})
        
        st.dataframe(manager_df, use_container_width=True)
        
        # Manager stats
        col_mgr1, col_mgr2, col_mgr3 = st.columns(3)
        
        with col_mgr1:
            st.metric("Total Managers", len(engine.manager_db))
        
        with col_mgr2:
            # Count by style
            styles = [data["style"] for data in engine.manager_db.values()]
            style_counts = pd.Series(styles).value_counts()
            most_common_style = style_counts.index[0] if len(style_counts) > 0 else "None"
            st.metric("Most Common Style", most_common_style)
        
        with col_mgr3:
            avg_attack = np.mean([data["attack"] for data in engine.manager_db.values()])
            st.metric("Avg Attack Rating", f"{avg_attack:.1f}/10")
    
    elif page == "Narrative Guide":
        # Narrative guide
        st.markdown('<h3 class="sub-header">📖 Narrative Guide</h3>', unsafe_allow_html=True)
        
        for narrative_name, narrative_info in engine.narratives.items():
            col_guide1, col_guide2 = st.columns([1, 2])
            
            with col_guide1:
                st.markdown(
                    f'<div style="background-color: {narrative_info["color"]}20; padding: 20px; border-radius: 10px; border-left: 5px solid {narrative_info["color"]};">'
                    f'<h4 style="color: {narrative_info["color"]}; margin-top: 0;">{narrative_name}</h4>'
                    f'<p>{narrative_info["description"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col_guide2:
                with st.expander(f"Details for {narrative_name}", expanded=False):
                    st.markdown("**Expected Match Flow:**")
                    st.write(narrative_info["flow"])
                    
                    st.markdown("**Common Betting Markets:**")
                    for bet in narrative_info["betting_markets"]:
                        st.write(f"• {bet}")
            
            st.markdown("---")
    
    else:
        # Initial state - no data loaded
        st.info("👈 **Upload a CSV file or select a data source from the sidebar to get started**")
        
        # Quick start guide
        with st.expander("🚀 Quick Start Guide", expanded=True):
            st.markdown("""
            1. **Prepare your CSV file** with the required columns
            2. **Upload your CSV** using the sidebar options
            3. **Select matches** you want to analyze
            4. **Generate predictions** with one click
            5. **Review results** and export if needed
            
            ### Required CSV Columns:
            - `home_team`, `away_team`, `date`
            - `home_position`, `away_position` (league positions)
            - `home_odds`, `away_odds` (decimal odds)
            - `home_form`, `away_form` (e.g., "WWDLW")
            - `home_manager`, `away_manager` (must match manager database)
            - `last_h2h_goals`, `last_h2h_btts` ("Yes"/"No")
            - Rating columns: `*_attack_rating`, `*_defense_rating`, etc. (1-10 scale)
            """)
        
        # Sample data display
        st.markdown("### 📋 Sample Data Format")
        sample_df = pd.DataFrame([{
            "Column": "home_team",
            "Type": "String",
            "Example": "Newcastle United",
            "Required": "Yes"
        }, {
            "Column": "home_odds", 
            "Type": "Float",
            "Example": "2.68",
            "Required": "Yes"
        }, {
            "Column": "home_form",
            "Type": "String",
            "Example": "WWWWL",
            "Required": "Yes"
        }, {
            "Column": "home_attack_rating",
            "Type": "Integer (1-10)",
            "Example": "9",
            "Required": "Yes"
        }])
        
        st.dataframe(sample_df, use_container_width=True)

if __name__ == "__main__":
    main()
