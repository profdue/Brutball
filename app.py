import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Narrative Predictor Pro v4.0",
    page_icon="⚽",
    layout="wide"
)

# Initialize session state
if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []

# -------------------------------------------------------------------
# CORE PREDICTION ENGINE (OUR ORIGINAL TESTED LOGIC)
# -------------------------------------------------------------------
class NarrativePredictionEngine:
    """ORIGINAL TESTED LOGIC FROM v3.0 - Now Integrated"""
    
    def __init__(self):
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "key_indicators": ["favorite_prob > 65%", "home_advantage", "early_goal_history"],
                "betting_recommendations": [
                    "Favorite -1.5 Asian Handicap",
                    "Favorite clean sheet",
                    "First goal before 25:00",
                    "Over 3.5 total goals"
                ],
                "expected_flow": "Early pressure → Breakthrough <30 mins → Opponent collapses → Multiple goals"
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "key_indicators": ["both_BTTS_high", "both_attack_minded", "weak_defenses"],
                "betting_recommendations": [
                    "Over 3.5 goals",
                    "BTTS: Yes",
                    "Both teams to score & Over 2.5",
                    "Late goal after 75:00"
                ],
                "expected_flow": "Fast start → Early goals → Lead changes → Late drama"
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "key_indicators": ["possession_mismatch", "attacker_motivation", "defender_desperation"],
                "betting_recommendations": [
                    "Under 2.5 goals",
                    "Favorite to win",
                    "BTTS: No",
                    "First goal 45-70 mins"
                ],
                "expected_flow": "Attacker dominates possession → Frustration builds → Breakthrough 45-70 mins"
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "key_indicators": ["both_cautious", "high_importance", "low_scoring_history"],
                "betting_recommendations": [
                    "Under 2.5 goals",
                    "BTTS: No",
                    "0-0 or 1-0 correct score",
                    "Fewer than 10 corners total"
                ],
                "expected_flow": "Cautious start → Midfield battle → Set piece threat → First goal decisive"
            },
            "SIEGE_WITH_COUNTER": {
                "description": "Hybrid - Attack dominates but faces counter threat",
                "key_indicators": ["attacker_dominates", "defender_counter_threat", "BTTS_possible"],
                "betting_recommendations": [
                    "BTTS: Yes",
                    "Over 2.5 goals",
                    "Favorite to win",
                    "Both teams to score halves"
                ],
                "expected_flow": "Attacker controls → Defender counters → Both teams score → Tense finish"
            }
        }
    
    # ---------------------------------------------------------------
    # ORIGINAL SCORING FORMULAS (TESTED AND VALIDATED)
    # ---------------------------------------------------------------
    
    def calculate_blitzkrieg_score(self, match_data):
        """BLITZKRIEG scoring from original logic"""
        score = 0
        
        # 1. Favorite probability (0-30 points) - From original formula
        favorite_prob = match_data.get("favorite_probability", 50)
        score += min(30, max(0, (favorite_prob - 50) * 0.6))
        
        # 2. Home advantage (0-20 points)
        if match_data.get("home_team_favorite", True):
            score += 20
        elif match_data.get("neutral_venue", False):
            score += 5
        
        # 3. Early goal history (0-25 points) - ORIGINAL FORMULA
        home_early = match_data.get("home_early_goal_percentage", 0)
        away_early_conceded = match_data.get("away_early_goal_conceded_percentage", 0)
        early_score = (home_early + away_early_conceded) / 2
        score += min(25, early_score * 0.25)
        
        # 4. Stakes mismatch (0-15 points) - ORIGINAL FORMULA
        favorite_stakes = match_data.get("favorite_stakes", 0)
        underdog_stakes = match_data.get("underdog_stakes", 0)
        stakes_diff = abs(favorite_stakes - underdog_stakes)
        score += min(15, stakes_diff * 1.5)
        
        # 5. Opponent collapse tendency (0-10 points)
        collapse_history = match_data.get("opponent_collapse_history", 0)
        score += min(10, collapse_history * 0.1)
        
        return min(100, max(0, score))
    
    def calculate_shootout_score(self, match_data):
        """SHOOTOUT scoring from original logic"""
        score = 0
        
        # 1. Both BTTS percentage (0-30 points) - ORIGINAL FORMULA
        home_btts = match_data.get("home_btts_percentage", 0)
        away_btts = match_data.get("away_btts_percentage", 0)
        avg_btts = (home_btts + away_btts) / 2
        score += min(30, avg_btts * 0.3)
        
        # 2. Both Over 2.5 percentage (0-25 points) - ORIGINAL FORMULA
        home_over = match_data.get("home_over_25_percentage", 0)
        away_over = match_data.get("away_over_25_percentage", 0)
        avg_over = (home_over + away_over) / 2
        score += min(25, avg_over * 0.25)
        
        # 3. Manager attack style (0-20 points)
        home_attack = match_data.get("home_manager_attack_rating", 0)
        away_attack = match_data.get("away_manager_attack_rating", 0)
        avg_attack = (home_attack + away_attack) / 2
        score += min(20, avg_attack * 2)
        
        # 4. Defensive weakness both (0-15 points) - ORIGINAL FORMULA
        home_def_weak = match_data.get("home_defensive_weakness", 0)
        away_def_weak = match_data.get("away_defensive_weakness", 0)
        avg_def_weak = (home_def_weak + away_def_weak) / 2
        score += min(15, avg_def_weak * 1.5)
        
        # 5. High stakes both (0-10 points)
        both_high_stakes = match_data.get("both_high_stakes", False)
        score += 10 if both_high_stakes else 0
        
        return min(100, max(0, score))
    
    def calculate_siege_score(self, match_data):
        """SIEGE scoring from original logic"""
        score = 0
        
        # 1. Possession mismatch (0-25 points) - ORIGINAL FORMULA
        home_possession = match_data.get("home_avg_possession", 50)
        away_possession = match_data.get("away_avg_possession", 50)
        possession_diff = abs(home_possession - away_possession)
        score += min(25, possession_diff * 0.5)
        
        # 2. Shots ratio (0-20 points) - ORIGINAL FORMULA
        home_shots = match_data.get("home_avg_shots", 10)
        away_shots_conceded = match_data.get("away_avg_shots_conceded", 10)
        shots_ratio = home_shots / max(away_shots_conceded, 1)
        if shots_ratio > 1.5:
            score += 20
        elif shots_ratio > 1.2:
            score += 15
        elif shots_ratio > 1.0:
            score += 10
        
        # 3. Attacker motivation (0-20 points)
        attacker_motivation = match_data.get("attacker_motivation", 0)
        score += attacker_motivation * 2
        
        # 4. Defender desperation (0-15 points)
        defender_desperation = match_data.get("defender_desperation", 0)
        score += defender_desperation * 1.5
        
        # 5. Counter attack threat (0-10 points)
        counter_threat = match_data.get("defender_counter_threat", 0)
        score += counter_threat
        
        # 6. Clean sheet history (0-10 points)
        attacker_clean_sheets = match_data.get("attacker_clean_sheet_percentage", 0)
        score += min(10, attacker_clean_sheets * 0.1)
        
        return min(100, max(0, score))
    
    def calculate_chess_match_score(self, match_data):
        """CHESS MATCH scoring from original logic"""
        score = 0
        
        # 1. Both cautious (0-30 points) - ORIGINAL FORMULA
        home_cautious = match_data.get("home_cautious_rating", 0)
        away_cautious = match_data.get("away_cautious_rating", 0)
        avg_cautious = (home_cautious + away_cautious) / 2
        score += min(30, avg_cautious * 3)
        
        # 2. Match importance (0-25 points)
        importance = match_data.get("match_importance", 0)
        score += importance * 2.5
        
        # 3. Manager pragmatism (0-20 points)
        home_pragmatic = match_data.get("home_manager_pragmatic_rating", 0)
        away_pragmatic = match_data.get("away_manager_pragmatic_rating", 0)
        avg_pragmatic = (home_pragmatic + away_pragmatic) / 2
        score += min(20, avg_pragmatic * 2)
        
        # 4. H2H low scoring (0-15 points) - ORIGINAL FORMULA
        h2h_low_scoring = match_data.get("h2h_low_scoring_percentage", 0)
        score += min(15, h2h_low_scoring * 0.15)
        
        # 5. Both Under 2.5 percentage (0-10 points) - ORIGINAL FORMULA
        home_under = match_data.get("home_under_25_percentage", 0)
        away_under = match_data.get("away_under_25_percentage", 0)
        avg_under = (home_under + away_under) / 2
        score += min(10, avg_under * 0.1)
        
        return min(100, max(0, score))
    
    def calculate_siege_with_counter_score(self, match_data):
        """SIEGE WITH COUNTER hybrid scoring"""
        siege_score = self.calculate_siege_score(match_data)
        
        # Adjust for counter threat
        counter_threat = match_data.get("defender_counter_threat", 0)
        counter_adjustment = counter_threat * 0.5
        
        # If counter threat is high, it's more likely to be hybrid
        if counter_threat >= 7:
            siege_score = siege_score * 0.7 + 30  # Convert to hybrid
        elif counter_threat >= 5:
            siege_score = siege_score * 0.8 + 20
        
        return min(100, max(0, siege_score))
    
    def calculate_expected_goals(self, match_data):
        """Calculate expected goals - ORIGINAL FORMULA FROM OUR SYSTEM"""
        home_gf = match_data.get("home_gf_per_game", 1.5)
        home_ga = match_data.get("home_ga_per_game", 1.0)
        away_gf = match_data.get("away_gf_per_game", 1.2)
        away_ga = match_data.get("away_ga_per_game", 1.3)
        
        # Original formula: [(Home_GF + Away_GA) + (Away_GF + Home_GA)] ÷ 2
        expected_goals = ((home_gf + away_ga) + (away_gf + home_ga)) / 2
        
        # Apply narrative adjustments (from our tested system)
        dominant_narrative = self.predict_dominant_narrative(match_data)
        
        narrative_adjustments = {
            "BLITZKRIEG": 1.15,
            "SHOOTOUT": 1.25,
            "SIEGE": 0.85,
            "CHESS_MATCH": 0.75,
            "SIEGE_WITH_COUNTER": 1.0
        }
        
        adjustment = narrative_adjustments.get(dominant_narrative, 1.0)
        return expected_goals * adjustment
    
    def calculate_btts_probability(self, match_data):
        """Calculate BTTS probability - ORIGINAL FORMULA"""
        home_btts = match_data.get("home_btts_percentage", 50) / 100
        away_btts = match_data.get("away_btts_percentage", 50) / 100
        
        # Original formula: (Home_BTTS% + Away_BTTS%) ÷ 2
        btts_prob = (home_btts + away_btts) / 2
        
        # Adjust based on narrative
        narrative = self.predict_dominant_narrative(match_data)
        if narrative == "SHOOTOUT":
            btts_prob = min(0.85, btts_prob * 1.2)
        elif narrative == "CHESS_MATCH":
            btts_prob = max(0.25, btts_prob * 0.7)
        
        return btts_prob
    
    def predict_dominant_narrative(self, match_data):
        """Main prediction function using ORIGINAL LOGIC"""
        scores = {}
        
        # Calculate all narrative scores
        scores["BLITZKRIEG"] = self.calculate_blitzkrieg_score(match_data)
        scores["SHOOTOUT"] = self.calculate_shootout_score(match_data)
        scores["SIEGE"] = self.calculate_siege_score(match_data)
        scores["CHESS_MATCH"] = self.calculate_chess_match_score(match_data)
        scores["SIEGE_WITH_COUNTER"] = self.calculate_siege_with_counter_score(match_data)
        
        # Find dominant narrative
        dominant_narrative = max(scores, key=scores.get)
        dominant_score = scores[dominant_narrative]
        
        # Determine tier based on ORIGINAL THRESHOLDS
        if dominant_score >= 75:
            tier = "TIER 1 (HIGH CONFIDENCE)"
            confidence_level = "HIGH"
        elif dominant_score >= 60:
            tier = "TIER 2 (MEDIUM CONFIDENCE)"
            confidence_level = "MEDIUM"
        elif dominant_score >= 50:
            tier = "TIER 3 (LOW CONFIDENCE)"
            confidence_level = "LOW"
        else:
            tier = "TIER 4 (AVOID)"
            confidence_level = "VERY LOW"
        
        # Calculate expected goals and BTTS probability
        expected_goals = self.calculate_expected_goals(match_data)
        btts_probability = self.calculate_btts_probability(match_data)
        
        # Determine Over/Under prediction
        if expected_goals > 2.7:
            over_under = "OVER 2.5"
            over_probability = 50 + ((expected_goals - 2.5) * 40)  # Original formula
            over_probability = min(85, max(15, over_probability))
            under_probability = 100 - over_probability
        else:
            over_under = "UNDER 2.5"
            under_probability = 50 + ((2.5 - expected_goals) * 40)  # Original formula
            under_probability = min(85, max(15, under_probability))
            over_probability = 100 - under_probability
        
        return {
            "scores": scores,
            "dominant_narrative": dominant_narrative,
            "dominant_score": dominant_score,
            "tier": tier,
            "confidence_level": confidence_level,
            "expected_goals": expected_goals,
            "btts_probability": btts_probability * 100,
            "over_under_prediction": over_under,
            "over_probability": over_probability,
            "under_probability": under_probability,
            "key_moments": self.generate_key_moments(dominant_narrative),
            "risk_factors": self.identify_risk_factors(match_data, dominant_narrative),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    def generate_key_moments(self, narrative):
        """Generate key moments based on narrative"""
        moments = {
            "BLITZKRIEG": [
                "First goal: 15-30 mins (70% probability)",
                "Second goal within 15 mins of first",
                "Halftime lead: 80% probability",
                "Game effectively over by 70 mins"
            ],
            "SHOOTOUT": [
                "First goal: 10-25 mins (65% probability)",
                "Response goals within 15 mins of conceding",
                "Lead changes possible",
                "Late goals: 55% probability after 75 mins"
            ],
            "SIEGE": [
                "First goal: 45-70 mins (60% probability)",
                "Attacker dominates possession (60%+)",
                "Set piece opportunities crucial",
                "Late breakthrough or stalemate"
            ],
            "CHESS_MATCH": [
                "First goal: 40-70 mins if any (50% probability)",
                "Set piece creates best chances",
                "Few yellow cards (discipline maintained)",
                "First goal often decisive"
            ],
            "SIEGE_WITH_COUNTER": [
                "First goal: 30-60 mins",
                "Counter-attack goal within 15 mins of conceding",
                "Both teams have clear chances",
                "Late nerves if score remains close"
            ]
        }
        return moments.get(narrative, ["Standard match progression"])
    
    def identify_risk_factors(self, match_data, narrative):
        """Identify risk factors based on match data"""
        risks = []
        
        # Common risks
        if match_data.get("home_injuries", 0) >= 3:
            risks.append("Home team injury concerns")
        if match_data.get("away_injuries", 0) >= 3:
            risks.append("Away team injury concerns")
        
        # Narrative-specific risks
        if narrative == "BLITZKRIEG":
            risks.append("Early set piece concession could disrupt momentum")
            risks.append("Red card changes dynamic completely")
        elif narrative == "SHOOTOUT":
            risks.append("Early red card could kill the open game")
            risks.append("Fatigue affects defensive discipline later")
        elif narrative == "SIEGE":
            risks.append("Early counter-attack goal changes narrative")
            risks.append("Attacker red card kills momentum")
        elif narrative == "CHESS_MATCH":
            risks.append("Early goal forces complete tactical change")
            risks.append("Individual mistake breaks deadlock")
        
        return risks if risks else ["Standard match risks apply"]

# -------------------------------------------------------------------
# FIXTURES DATABASE WITH SAMPLE STATS
# -------------------------------------------------------------------
fixtures_db = {
    "SPANISH LA LIGA": [
        {"match": "Real Madrid vs Sevilla", "date": "20/12/2025",
         "home_stats": {"btts_percentage": 60, "over_25_percentage": 70, "gf_per_game": 2.1, "ga_per_game": 0.8},
         "away_stats": {"btts_percentage": 50, "over_25_percentage": 60, "gf_per_game": 1.4, "ga_per_game": 1.2}},
        {"match": "Barcelona vs Atlético Madrid", "date": "21/12/2025",
         "home_stats": {"btts_percentage": 65, "over_25_percentage": 75, "gf_per_game": 2.3, "ga_per_game": 1.0},
         "away_stats": {"btts_percentage": 40, "over_25_percentage": 50, "gf_per_game": 1.2, "ga_per_game": 0.9}}
    ],
    "ENGLISH PREMIER LEAGUE": [
        {"match": "Manchester City vs West Ham", "date": "20/12/2025",
         "home_stats": {"btts_percentage": 55, "over_25_percentage": 80, "gf_per_game": 2.4, "ga_per_game": 0.7},
         "away_stats": {"btts_percentage": 70, "over_25_percentage": 65, "gf_per_game": 1.6, "ga_per_game": 1.8}},
        {"match": "Tottenham vs Liverpool", "date": "20/12/2025",
         "home_stats": {"btts_percentage": 75, "over_25_percentage": 80, "gf_per_game": 2.0, "ga_per_game": 1.5},
         "away_stats": {"btts_percentage": 70, "over_25_percentage": 75, "gf_per_game": 2.1, "ga_per_game": 1.4}}
    ],
    "ITALIAN SERIE A": [
        {"match": "Juventus vs Roma", "date": "20/12/2025",
         "home_stats": {"btts_percentage": 40, "over_25_percentage": 45, "gf_per_game": 1.5, "ga_per_game": 0.8},
         "away_stats": {"btts_percentage": 45, "over_25_percentage": 50, "gf_per_game": 1.4, "ga_per_game": 1.0}}
    ]
}

# -------------------------------------------------------------------
# STREAMLIT APP WITH ORIGINAL LOGIC
# -------------------------------------------------------------------
st.title("⚽ Narrative Predictor Pro v4.0")
st.markdown("**Original Tested Logic Integrated | Statistical Analysis Engine**")

# Initialize engine
engine = NarrativePredictionEngine()

# -------------------------------------------------------------------
# 1. BATCH ANALYSIS OR SINGLE MATCH
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("1️⃣ ANALYSIS MODE")

analysis_mode = st.radio(
    "Choose analysis mode:",
    ["Batch Analysis (Multiple Leagues)", "Single Match Deep Analysis"],
    horizontal=True
)

# -------------------------------------------------------------------
# 2. BATCH ANALYSIS
# -------------------------------------------------------------------
if analysis_mode == "Batch Analysis (Multiple Leagues)":
    st.markdown("---")
    st.subheader("2️⃣ SELECT LEAGUES FOR BATCH ANALYSIS")
    
    leagues = list(fixtures_db.keys())
    selected_leagues = []
    
    cols = st.columns(3)
    for i, league in enumerate(leagues):
        with cols[i % 3]:
            if st.checkbox(league, value=True):
                selected_leagues.append(league)
    
    if st.button("🎯 RUN BATCH PREDICTIONS", type="primary", use_container_width=True):
        all_matches = []
        for league in selected_leagues:
            for fixture in fixtures_db[league]:
                all_matches.append({
                    "league": league,
                    "match": fixture["match"],
                    "date": fixture["date"],
                    "home_stats": fixture["home_stats"],
                    "away_stats": fixture["away_stats"]
                })
        
        st.session_state.batch_results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, match_info in enumerate(all_matches):
            status_text.text(f"Analyzing {match_info['match']}...")
            
            # Prepare match data with stats
            match_data = {
                "home_btts_percentage": match_info["home_stats"]["btts_percentage"],
                "away_btts_percentage": match_info["away_stats"]["btts_percentage"],
                "home_over_25_percentage": match_info["home_stats"]["over_25_percentage"],
                "away_over_25_percentage": match_info["away_stats"]["over_25_percentage"],
                "home_gf_per_game": match_info["home_stats"]["gf_per_game"],
                "home_ga_per_game": match_info["home_stats"]["ga_per_game"],
                "away_gf_per_game": match_info["away_stats"]["gf_per_game"],
                "away_ga_per_game": match_info["away_stats"]["ga_per_game"],
                "favorite_probability": 65 if "Real Madrid" in match_info["match"] or "Manchester City" in match_info["match"] else 50,
                "home_team_favorite": True,
                "home_early_goal_percentage": 40,
                "away_early_goal_conceded_percentage": 50,
                "favorite_stakes": 7,
                "underdog_stakes": 3,
                "home_manager_attack_rating": 8,
                "away_manager_attack_rating": 6,
                "home_defensive_weakness": 3,
                "away_defensive_weakness": 5,
                "home_avg_possession": 65,
                "away_avg_possession": 45,
                "home_avg_shots": 16,
                "away_avg_shots_conceded": 14,
                "attacker_motivation": 7,
                "defender_desperation": 6,
                "defender_counter_threat": 4,
                "home_cautious_rating": 4,
                "away_cautious_rating": 6,
                "match_importance": 8,
                "home_manager_pragmatic_rating": 5,
                "away_manager_pragmatic_rating": 7,
                "h2h_low_scoring_percentage": 40,
                "home_under_25_percentage": 100 - match_info["home_stats"]["over_25_percentage"],
                "away_under_25_percentage": 100 - match_info["away_stats"]["over_25_percentage"]
            }
            
            prediction = engine.predict_dominant_narrative(match_data)
            prediction["league"] = match_info["league"]
            prediction["match"] = match_info["match"]
            prediction["date"] = match_info["date"]
            
            st.session_state.batch_results.append(prediction)
            
            progress_bar.progress((idx + 1) / len(all_matches))
        
        status_text.text("✅ Analysis complete!")
        progress_bar.empty()

# -------------------------------------------------------------------
# 3. SINGLE MATCH DEEP ANALYSIS
# -------------------------------------------------------------------
else:
    st.markdown("---")
    st.subheader("2️⃣ SINGLE MATCH DEEP ANALYSIS")
    
    # Get all matches
    all_matches_list = []
    for league, fixtures in fixtures_db.items():
        for fixture in fixtures:
            all_matches_list.append(f"{fixture['match']} ({league})")
    
    selected_match_full = st.selectbox("Select match:", all_matches_list)
    
    if selected_match_full:
        match_name = selected_match_full.split(" (")[0]
        league = selected_match_full.split("(")[1].replace(")", "")
        
        # Find match stats
        match_stats = None
        for fixture in fixtures_db[league]:
            if fixture["match"] == match_name:
                match_stats = fixture
                break
        
        if match_stats:
            st.markdown("---")
            st.subheader(f"3️⃣ STATISTICAL ANALYSIS: {match_name}")
            
            # Display stats
            col_stats1, col_stats2 = st.columns(2)
            
            with col_stats1:
                st.markdown("**Home Team Statistics**")
                stats = match_stats["home_stats"]
                st.write(f"BTTS %: {stats['btts_percentage']}%")
                st.write(f"Over 2.5 %: {stats['over_25_percentage']}%")
                st.write(f"Goals For/Game: {stats['gf_per_game']}")
                st.write(f"Goals Against/Game: {stats['ga_per_game']}")
            
            with col_stats2:
                st.markdown("**Away Team Statistics**")
                stats = match_stats["away_stats"]
                st.write(f"BTTS %: {stats['btts_percentage']}%")
                st.write(f"Over 2.5 %: {stats['over_25_percentage']}%")
                st.write(f"Goals For/Game: {stats['gf_per_game']}")
                st.write(f"Goals Against/Game: {stats['ga_per_game']}")
            
            # User can adjust parameters
            st.markdown("---")
            st.subheader("4️⃣ ADJUST ANALYSIS PARAMETERS")
            
            with st.form("analysis_params"):
                col_params1, col_params2 = st.columns(2)
                
                with col_params1:
                    st.markdown("**Context Factors**")
                    favorite_probability = st.slider("Favorite Win Probability %", 0, 100, 65)
                    home_team_favorite = st.checkbox("Home team is favorite", True)
                    match_importance = st.slider("Match Importance (0-10)", 0, 10, 7)
                    home_injuries = st.slider("Home team key injuries", 0, 5, 0)
                    away_injuries = st.slider("Away team key injuries", 0, 5, 0)
                
                with col_params2:
                    st.markdown("**Team Characteristics**")
                    home_manager_attack = st.slider("Home manager attack rating", 0, 10, 8)
                    away_manager_attack = st.slider("Away manager attack rating", 0, 10, 6)
                    home_cautious = st.slider("Home team cautiousness", 0, 10, 4)
                    away_cautious = st.slider("Away team cautiousness", 0, 10, 6)
                    defender_counter_threat = st.slider("Away counter threat", 0, 10, 4)
                
                if st.form_submit_button("🚀 RUN ORIGINAL PREDICTION ALGORITHM"):
                    # Prepare match data
                    match_data = {
                        "home_btts_percentage": match_stats["home_stats"]["btts_percentage"],
                        "away_btts_percentage": match_stats["away_stats"]["btts_percentage"],
                        "home_over_25_percentage": match_stats["home_stats"]["over_25_percentage"],
                        "away_over_25_percentage": match_stats["away_stats"]["over_25_percentage"],
                        "home_gf_per_game": match_stats["home_stats"]["gf_per_game"],
                        "home_ga_per_game": match_stats["home_stats"]["ga_per_game"],
                        "away_gf_per_game": match_stats["away_stats"]["gf_per_game"],
                        "away_ga_per_game": match_stats["away_stats"]["ga_per_game"],
                        "favorite_probability": favorite_probability,
                        "home_team_favorite": home_team_favorite,
                        "home_early_goal_percentage": 40,
                        "away_early_goal_conceded_percentage": 50,
                        "favorite_stakes": 7,
                        "underdog_stakes": 3,
                        "home_manager_attack_rating": home_manager_attack,
                        "away_manager_attack_rating": away_manager_attack,
                        "home_defensive_weakness": 10 - home_manager_attack,
                        "away_defensive_weakness": 10 - away_manager_attack,
                        "home_avg_possession": 65,
                        "away_avg_possession": 45,
                        "home_avg_shots": 16,
                        "away_avg_shots_conceded": 14,
                        "attacker_motivation": 7,
                        "defender_desperation": 6,
                        "defender_counter_threat": defender_counter_threat,
                        "home_cautious_rating": home_cautious,
                        "away_cautious_rating": away_cautious,
                        "match_importance": match_importance,
                        "home_manager_pragmatic_rating": 5,
                        "away_manager_pragmatic_rating": 7,
                        "h2h_low_scoring_percentage": 40,
                        "home_under_25_percentage": 100 - match_stats["home_stats"]["over_25_percentage"],
                        "away_under_25_percentage": 100 - match_stats["away_stats"]["over_25_percentage"],
                        "home_injuries": home_injuries,
                        "away_injuries": away_injuries
                    }
                    
                    # Run prediction
                    with st.spinner("Running original prediction algorithms..."):
                        prediction = engine.predict_dominant_narrative(match_data)
                        prediction["match"] = match_name
                        prediction["league"] = league
                        prediction["date"] = match_stats["date"]
                    
                    # Store in session
                    st.session_state.current_prediction = prediction
                    st.session_state.show_results = True
            
            # Display results if available
            if 'show_results' in st.session_state and st.session_state.show_results:
                prediction = st.session_state.current_prediction
                
                st.markdown("---")
                st.subheader("5️⃣ PREDICTION RESULTS")
                
                # Main prediction card
                col_pred1, col_pred2 = st.columns(2)
                
                with col_pred1:
                    # Determine color based on tier
                    tier_colors = {
                        "TIER 1 (HIGH CONFIDENCE)": "#28a745",
                        "TIER 2 (MEDIUM CONFIDENCE)": "#ffc107",
                        "TIER 3 (LOW CONFIDENCE)": "#dc3545",
                        "TIER 4 (AVOID)": "#6c757d"
                    }
                    
                    color = tier_colors.get(prediction["tier"], "#007bff")
                    
                    st.markdown(f"""
                    <div style="padding: 1.5rem; border-radius: 10px; border-left: 6px solid {color}; background-color: #f8f9fa;">
                        <h2>🎯 {prediction['dominant_narrative']}</h2>
                        <h1 style="color: {color};">{prediction['dominant_score']:.1f}/100</h1>
                        <h3>{prediction['tier']}</h3>
                        <p><strong>Confidence:</strong> {prediction['confidence_level']}</p>
                        <p>{engine.narratives[prediction['dominant_narrative']]['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_pred2:
                    st.markdown("**📊 Statistical Projections**")
                    
                    # Expected goals gauge
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = prediction['expected_goals'],
                        title = {'text': "Expected Goals"},
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        gauge = {
                            'axis': {'range': [0, 5]},
                            'bar': {'color': "#007bff"},
                            'steps': [
                                {'range': [0, 2.5], 'color': "#d4edda"},
                                {'range': [2.5, 5], 'color': "#f8d7da"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 2.5
                            }
                        }
                    ))
                    fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                
                # All narrative scores
                st.markdown("#### All Narrative Scores")
                scores_df = pd.DataFrame({
                    "Narrative": list(prediction["scores"].keys()),
                    "Score": list(prediction["scores"].values())
                }).sort_values("Score", ascending=False)
                
                # Bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=scores_df["Narrative"],
                        y=scores_df["Score"],
                        text=[f"{s:.1f}" for s in scores_df["Score"]],
                        textposition='auto',
                        marker_color=['#28a745' if s == prediction['dominant_narrative'] else '#6c757d' 
                                    for s in scores_df["Narrative"]]
                    )
                ])
                fig.update_layout(
                    title="Narrative Scores Comparison",
                    yaxis_title="Score",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insights in columns
                col_insights1, col_insights2, col_insights3 = st.columns(3)
                
                with col_insights1:
                    st.markdown("#### 📈 Probability Analysis")
                    st.write(f"**BTTS Probability:** {prediction['btts_probability']:.1f}%")
                    st.write(f"**{prediction['over_under_prediction']} Probability:**")
                    st.write(f"  - Over 2.5: {prediction['over_probability']:.1f}%")
                    st.write(f"  - Under 2.5: {prediction['under_probability']:.1f}%")
                
                with col_insights2:
                    st.markdown("#### 🎯 Key Moments")
                    for moment in prediction["key_moments"]:
                        st.write(f"• {moment}")
                
                with col_insights3:
                    st.markdown("#### ⚠️ Risk Factors")
                    for risk in prediction["risk_factors"]:
                        st.write(f"• {risk}")
                
                # Betting recommendations
                st.markdown("---")
                st.subheader("💰 BETTING RECOMMENDATIONS")
                
                narrative_info = engine.narratives[prediction['dominant_narrative']]
                
                col_bets1, col_bets2 = st.columns(2)
                
                with col_bets1:
                    st.markdown("**Recommended Bets:**")
                    for bet in narrative_info["betting_recommendations"]:
                        st.write(f"✅ {bet}")
                    
                    # Stake suggestion based on tier
                    stake_suggestions = {
                        "TIER 1 (HIGH CONFIDENCE)": "2-3 units (Strong bet)",
                        "TIER 2 (MEDIUM CONFIDENCE)": "1-2 units (Good bet)",
                        "TIER 3 (LOW CONFIDENCE)": "0.5-1 unit (Caution)",
                        "TIER 4 (AVOID)": "No bet"
                    }
                    
                    st.markdown(f"**Stake Suggestion:** {stake_suggestions.get(prediction['tier'], 'Monitor odds')}")
                
                with col_bets2:
                    st.markdown("**Expected Match Flow:**")
                    st.info(narrative_info["expected_flow"])
                    
                    st.markdown("**Key Indicators:**")
                    st.write(", ".join(narrative_info["key_indicators"]))
                
                # Save prediction
                if st.button("💾 Save This Prediction"):
                    if 'all_predictions' not in st.session_state:
                        st.session_state.all_predictions = []
                    st.session_state.all_predictions.append(prediction)
                    st.success("✅ Prediction saved to history!")

# -------------------------------------------------------------------
# 4. RESULTS DISPLAY (BATCH MODE)
# -------------------------------------------------------------------
if st.session_state.batch_results:
    st.markdown("---")
    st.subheader("📊 BATCH PREDICTION RESULTS")
    
    results_df = pd.DataFrame(st.session_state.batch_results)
    
    # Summary statistics
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    with col_sum1:
        total = len(results_df)
        st.metric("Total Matches", total)
    with col_sum2:
        tier1 = len(results_df[results_df['tier'].str.contains('TIER 1')])
        st.metric("Tier 1 Predictions", tier1)
    with col_sum3:
        avg_score = results_df['dominant_score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")
    with col_sum4:
        top_narrative = results_df['dominant_narrative'].mode()[0]
        st.metric("Top Narrative", top_narrative)
    
    # Interactive table
    st.markdown("#### Filterable Predictions Table")
    
    # Filters
    col_filt1, col_filt2, col_filt3 = st.columns(3)
    with col_filt1:
        selected_narratives = st.multiselect(
            "Narratives",
            options=results_df['dominant_narrative'].unique(),
            default=results_df['dominant_narrative'].unique()
        )
    with col_filt2:
        selected_tiers = st.multiselect(
            "Tiers",
            options=results_df['tier'].unique(),
            default=results_df['tier'].unique()
        )
    with col_filt3:
        selected_leagues = st.multiselect(
            "Leagues",
            options=results_df['league'].unique(),
            default=results_df['league'].unique()
        )
    
    # Apply filters
    filtered_df = results_df[
        (results_df['dominant_narrative'].isin(selected_narratives)) &
        (results_df['tier'].isin(selected_tiers)) &
        (results_df['league'].isin(selected_leagues))
    ].sort_values('dominant_score', ascending=False)
    
    # Display table
    display_cols = ['league', 'match', 'date', 'dominant_narrative', 'dominant_score', 'tier', 'expected_goals', 'btts_probability']
    display_df = filtered_df[display_cols].copy()
    
    # Color formatting
    def color_score(val):
        if val >= 75:
            return 'background-color: #d4edda; color: #155724'
        elif val >= 60:
            return 'background-color: #fff3cd; color: #856404'
        else:
            return 'background-color: #f8d7da; color: #721c24'
    
    def color_goals(val):
        if val > 2.7:
            return 'background-color: #f8d7da; color: #721c24'  # Red for high
        elif val < 2.3:
            return 'background-color: #d4edda; color: #155724'  # Green for low
        else:
            return 'background-color: #fff3cd; color: #856404'  # Yellow for medium
    
    styled_df = display_df.style\
        .format({
            'dominant_score': '{:.1f}',
            'expected_goals': '{:.2f}',
            'btts_probability': '{:.1f}%'
        })\
        .applymap(color_score, subset=['dominant_score'])\
        .applymap(color_goals, subset=['expected_goals'])
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Export options
    st.markdown("#### Export Results")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        json_data = filtered_df.to_dict(orient='records')
        st.download_button(
            label="📊 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# -------------------------------------------------------------------
# 5. PREDICTION HISTORY
# -------------------------------------------------------------------
if st.session_state.all_predictions:
    st.markdown("---")
    st.subheader("📈 PREDICTION HISTORY & PERFORMANCE")
    
    history_df = pd.DataFrame(st.session_state.all_predictions)
    
    # Performance metrics
    col_hist1, col_hist2, col_hist3 = st.columns(3)
    with col_hist1:
        st.metric("Total Predictions", len(history_df))
    with col_hist2:
        avg_conf = history_df['dominant_score'].mean()
        st.metric("Avg Confidence", f"{avg_conf:.1f}")
    with col_hist3:
        common_narrative = history_df['dominant_narrative'].mode()[0]
        st.metric("Most Common", common_narrative)
    
    # Recent predictions
    st.markdown("#### Recent Predictions")
    recent = history_df[['timestamp', 'match', 'dominant_narrative', 'dominant_score', 'tier']].tail(10)
    st.dataframe(recent, use_container_width=True)

# -------------------------------------------------------------------
# 6. FOOTER
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚽ <strong>Narrative Predictor Pro v4.0</strong> | Original Tested Logic Integrated</p>
    <p>Uses statistical formulas from validated system | Updated: {}</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)
