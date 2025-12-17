import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Narrative Predictor Pro",
    page_icon="⚽",
    layout="wide"
)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'current_match' not in st.session_state:
    st.session_state.current_match = None

# -------------------------------------------------------------------
# INTERPRETATION ENGINE
# -------------------------------------------------------------------
class InterpretationEngine:
    """Interprets raw data into narrative signals"""
    
    @staticmethod
    def interpret_odds(home_odds, draw_odds, away_odds):
        """Interpret betting odds"""
        # Calculate implied probabilities
        home_prob = 1 / home_odds if home_odds > 1 else 0
        away_prob = 1 / away_odds if away_odds > 1 else 0
        draw_prob = 1 / draw_odds if draw_odds > 1 else 0
        
        # Normalize to 100%
        total = home_prob + draw_prob + away_prob
        if total > 0:
            home_prob = home_prob / total * 100
            away_prob = away_prob / total * 100
            draw_prob = draw_prob / total * 100
        
        # Determine favorite strength
        if home_odds <= 1.40:
            return "STRONG FAVORITE", home_prob, "Home"
        elif home_odds <= 1.80:
            return "MODERATE FAVORITE", home_prob, "Home"
        elif away_odds <= 1.40:
            return "STRONG FAVORITE", away_prob, "Away"
        elif away_odds <= 1.80:
            return "MODERATE FAVORITE", away_prob, "Away"
        else:
            return "EVEN MATCH", max(home_prob, away_prob), "Even"
    
    @staticmethod
    def interpret_table(home_pos, home_pts, away_pos, away_pts):
        """Interpret table positions"""
        # Position categories
        def get_category(position):
            if position <= 4:
                return "European places"
            elif position <= 6:
                return "Conference League"
            elif position <= 10:
                return "Midtable"
            elif position <= 17:
                return "Relegation battle"
            else:
                return "Relegation zone"
        
        home_cat = get_category(home_pos)
        away_cat = get_category(away_pos)
        
        # Determine stakes
        if home_cat == "European places" and away_cat == "Relegation zone":
            return "TITLE VS RELEGATION", "High mismatch"
        elif home_cat == "European places" and away_cat == "Midtable":
            return "NEEDS WIN VS SAFE", "Moderate mismatch"
        elif home_cat == "Relegation battle" and away_cat == "Relegation battle":
            return "RELEGATION 6-POINTER", "High stakes both"
        elif "European" in home_cat and "European" in away_cat:
            return "TOP 4 BATTLE", "High stakes both"
        else:
            return "STANDARD MATCH", "Medium stakes"
    
    @staticmethod
    def interpret_h2h(scores):
        """Interpret H2H scores"""
        if len(scores) < 2:
            return "INSUFFICIENT DATA", "Needs more matches"
        
        home_wins = 0
        away_wins = 0
        draws = 0
        total_goals = 0
        
        for score in scores:
            try:
                if '-' in score:
                    home_goals, away_goals = map(int, score.split('-'))
                    total_goals += home_goals + away_goals
                    
                    if home_goals > away_goals:
                        home_wins += 1
                    elif away_goals > home_goals:
                        away_wins += 1
                    else:
                        draws += 1
            except:
                continue
        
        # Determine pattern
        if home_wins >= 2 and home_wins > away_wins:
            return "HOME DOMINATES", f"{home_wins} wins, {total_goals} total goals"
        elif away_wins >= 2 and away_wins > home_wins:
            return "AWAY DOMINATES", f"{away_wins} wins, {total_goals} total goals"
        elif draws >= 2:
            return "FREQUENT DRAWS", f"{draws} draws, {total_goals} total goals"
        elif total_goals / len(scores) > 3:
            return "HIGH SCORING", f"{total_goals/len(scores):.1f} goals per game"
        else:
            return "MIXED RESULTS", f"{home_wins}-{draws}-{away_wins}, {total_goals} goals"
    
    @staticmethod
    def interpret_form(home_form, away_form):
        """Interpret recent form"""
        def analyze_form(form_string):
            if not form_string:
                return 0, 0, 0
            wins = form_string.count('W')
            draws = form_string.count('D')
            losses = form_string.count('L')
            points = wins * 3 + draws
            return wins, losses, points
        
        home_wins, home_losses, home_pts = analyze_form(home_form)
        away_wins, away_losses, away_pts = analyze_form(away_form)
        
        # Determine form pattern
        if home_wins >= 4 and away_losses >= 3:
            return "HOME FLYING, AWAY STRUGGLING", f"Home {home_wins}W, Away {away_losses}L"
        elif away_wins >= 4 and home_losses >= 3:
            return "AWAY FLYING, HOME STRUGGLING", f"Away {away_wins}W, Home {home_losses}L"
        elif home_wins >= 3 and away_wins >= 3:
            return "BOTH IN FORM", f"Home {home_wins}W, Away {away_wins}W"
        elif home_losses >= 3 and away_losses >= 3:
            return "BOTH STRUGGLING", f"Home {home_losses}L, Away {away_losses}L"
        else:
            return "MIXED FORM", f"Home {home_pts}pts, Away {away_pts}pts"
    
    @staticmethod
    def interpret_styles(home_manager, away_manager):
        """Interpret manager styles"""
        attacking_managers = ["Guardiola", "Klopp", "Arteta", "Postecoglou", "De Zerbi", "Emery"]
        defensive_managers = ["Moyes", "Dyche", "Hodgson", "Allardyce", "Pulis"]
        pragmatic_managers = ["Ten Hag", "Howe", "Silva", "Frank", "Cooper"]
        
        home_style = "Unknown"
        away_style = "Unknown"
        
        for manager in attacking_managers:
            if manager.lower() in home_manager.lower():
                home_style = "Attack"
            if manager.lower() in away_manager.lower():
                away_style = "Attack"
        
        for manager in defensive_managers:
            if manager.lower() in home_manager.lower():
                home_style = "Defense"
            if manager.lower() in away_manager.lower():
                away_style = "Defense"
        
        for manager in pragmatic_managers:
            if manager.lower() in home_manager.lower():
                home_style = "Pragmatic"
            if manager.lower() in away_manager.lower():
                away_style = "Pragmatic"
        
        if home_style == "Attack" and away_style == "Defense":
            return "ATTACK VS DEFENSE", "Classic clash"
        elif home_style == "Defense" and away_style == "Attack":
            return "DEFENSE VS ATTACK", "Classic clash"
        elif home_style == "Attack" and away_style == "Attack":
            return "BOTH ATTACKING", "Entertaining match"
        elif home_style == "Defense" and away_style == "Defense":
            return "BOTH DEFENSIVE", "Tactical battle"
        else:
            return "MIXED STYLES", "Unpredictable"

# -------------------------------------------------------------------
# NARRATIVE PREDICTION ENGINE
# -------------------------------------------------------------------
class NarrativePredictor:
    """Predicts narrative based on interpreted data"""
    
    def __init__(self):
        self.engine = InterpretationEngine()
    
    def predict(self, match_data):
        """Make prediction from raw data"""
        
        # Interpret all inputs
        odds_interpretation = self.engine.interpret_odds(
            match_data['home_odds'], 
            match_data['draw_odds'], 
            match_data['away_odds']
        )
        
        table_interpretation = self.engine.interpret_table(
            match_data['home_pos'],
            match_data['home_pts'],
            match_data['away_pos'],
            match_data['away_pts']
        )
        
        h2h_interpretation = self.engine.interpret_h2h(
            match_data['h2h_scores']
        )
        
        form_interpretation = self.engine.interpret_form(
            match_data['home_form'],
            match_data['away_form']
        )
        
        style_interpretation = self.engine.interpret_styles(
            match_data['home_manager'],
            match_data['away_manager']
        )
        
        # Score each narrative
        scores = {
            'BLITZKRIEG': self.score_blitzkrieg(odds_interpretation, table_interpretation, 
                                               h2h_interpretation, form_interpretation, style_interpretation),
            'SHOOTOUT': self.score_shootout(odds_interpretation, table_interpretation,
                                           h2h_interpretation, form_interpretation, style_interpretation),
            'SIEGE': self.score_siege(odds_interpretation, table_interpretation,
                                     h2h_interpretation, form_interpretation, style_interpretation),
            'CHESS': self.score_chess(odds_interpretation, table_interpretation,
                                     h2h_interpretation, form_interpretation, style_interpretation)
        }
        
        # Get best narrative
        best_narrative = max(scores.items(), key=lambda x: x[1])
        
        return {
            'narrative': best_narrative[0],
            'score': best_narrative[1],
            'scores': scores,
            'interpretations': {
                'odds': odds_interpretation,
                'table': table_interpretation,
                'h2h': h2h_interpretation,
                'form': form_interpretation,
                'style': style_interpretation
            }
        }
    
    def score_blitzkrieg(self, odds, table, h2h, form, style):
        """Score Blitzkrieg narrative"""
        score = 0
        
        # Odds: Strong favorite
        if odds[0] == "STRONG FAVORITE":
            score += 30
        elif odds[0] == "MODERATE FAVORITE":
            score += 20
        
        # Table: Mismatch
        if "VS RELEGATION" in table[0] or "NEEDS WIN VS SAFE" in table[0]:
            score += 25
        
        # H2H: Dominance
        if "DOMINATES" in h2h[0]:
            score += 20
        
        # Form: Strong vs Weak
        if "FLYING, AWAY STRUGGLING" in form[0] or "HOME FLYING" in form[0]:
            score += 15
        
        # Style: Attack vs Defense
        if "ATTACK VS DEFENSE" in style[0]:
            score += 10
        
        return min(score, 100)
    
    def score_shootout(self, odds, table, h2h, form, style):
        """Score Shootout narrative"""
        score = 0
        
        # Odds: Even match
        if odds[0] == "EVEN MATCH":
            score += 20
        
        # Table: Both need points
        if "HIGH STAKES BOTH" in table[1] or "TOP 4 BATTLE" in table[0]:
            score += 25
        
        # H2H: High scoring
        if "HIGH SCORING" in h2h[0]:
            score += 25
        
        # Form: Both in form
        if "BOTH IN FORM" in form[0]:
            score += 20
        
        # Style: Both attacking
        if "BOTH ATTACKING" in style[0]:
            score += 10
        
        return min(score, 100)
    
    def score_siege(self, odds, table, h2h, form, style):
        """Score Siege narrative"""
        score = 0
        
        # Odds: Favorite but not too strong
        if odds[0] in ["MODERATE FAVORITE", "STRONG FAVORITE"]:
            score += 20
        
        # Table: Attacker needs win
        if "NEEDS WIN" in table[0] or "VS SAFE" in table[0]:
            score += 25
        
        # H2H: Close but favorite wins
        if "DOMINATES" in h2h[0] or "MIXED RESULTS" in h2h[0]:
            score += 15
        
        # Form: Attacker better form
        if "HOME FLYING" in form[0] or "AWAY STRUGGLING" in form[0]:
            score += 20
        
        # Style: Attack vs Defense
        if "ATTACK VS DEFENSE" in style[0]:
            score += 20
        
        return min(score, 100)
    
    def score_chess(self, odds, table, h2h, form, style):
        """Score Chess Match narrative"""
        score = 0
        
        # Odds: Close match
        if odds[0] == "EVEN MATCH" or odds[2] == "Even":
            score += 20
        
        # Table: High stakes both
        if "HIGH STAKES" in table[1] or "BATTLE" in table[0]:
            score += 25
        
        # H2H: Low scoring or draws
        if "FREQUENT DRAWS" in h2h[0] or "MIXED RESULTS" in h2h[0]:
            score += 20
        
        # Form: Both inconsistent
        if "MIXED FORM" in form[0] or "BOTH STRUGGLING" in form[0]:
            score += 15
        
        # Style: Both defensive or pragmatic
        if "BOTH DEFENSIVE" in style[0] or "TACTICAL BATTLE" in style[1]:
            score += 20
        
        return min(score, 100)

# -------------------------------------------------------------------
# STREAMLIT APP
# -------------------------------------------------------------------
st.title("⚽ Narrative Predictor Pro")
st.markdown("**Input raw data → System interprets → Get prediction**")

# Initialize predictor
predictor = NarrativePredictor()

# -------------------------------------------------------------------
# 1. MATCH SELECTION
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("1️⃣ SELECT MATCH")

# Pre-defined examples
examples = {
    "Manchester City vs Nottingham Forest": {
        "home_odds": 1.30, "draw_odds": 5.50, "away_odds": 11.00,
        "home_pos": 1, "home_pts": 68, "away_pos": 17, "away_pts": 25,
        "h2h_scores": ["6-0", "2-0", "3-0"],
        "home_form": "WWWWW", "away_form": "LLLDL",
        "home_manager": "Guardiola", "away_manager": "Nuno"
    },
    "Tottenham vs Liverpool": {
        "home_odds": 3.80, "draw_odds": 4.00, "away_odds": 1.90,
        "home_pos": 5, "home_pts": 57, "away_pos": 2, "away_pts": 64,
        "h2h_scores": ["2-1", "1-1", "2-2"],
        "home_form": "WWLWW", "away_form": "WWDWW",
        "home_manager": "Postecoglou", "away_manager": "Klopp"
    },
    "Arsenal vs Chelsea": {
        "home_odds": 1.80, "draw_odds": 3.75, "away_odds": 4.50,
        "home_pos": 3, "home_pts": 61, "away_pos": 9, "away_pts": 47,
        "h2h_scores": ["1-0", "0-0", "2-2"],
        "home_form": "WLWDW", "away_form": "DLLWD",
        "home_manager": "Arteta", "away_manager": "Pochettino"
    },
    "Newcastle vs Everton": {
        "home_odds": 1.70, "draw_odds": 3.90, "away_odds": 5.00,
        "home_pos": 8, "home_pts": 50, "away_pos": 16, "away_pts": 28,
        "h2h_scores": ["1-0", "0-0", "2-1"],
        "home_form": "WLDWW", "away_form": "LLDLD",
        "home_manager": "Howe", "away_manager": "Dyche"
    }
}

# Match selection
match_options = list(examples.keys()) + ["Custom Match"]
selected_match = st.selectbox("Choose match:", match_options)

if selected_match == "Custom Match":
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("Home Team")
    with col2:
        away_team = st.text_input("Away Team")
    if home_team and away_team:
        selected_match = f"{home_team} vs {away_team}"
    else:
        selected_match = "Manchester City vs Nottingham Forest"

st.session_state.current_match = selected_match

st.markdown(f"""
<div style="padding: 1rem; border-radius: 10px; border: 2px solid #e0e0e0; margin-bottom: 1rem;">
    <h4>{selected_match}</h4>
    <p>Premier League • Saturday 3pm</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. INPUT RAW DATA
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("2️⃣ INPUT RAW DATA")

# Get example data or initialize empty
if selected_match in examples:
    example_data = examples[selected_match]
else:
    example_data = examples["Manchester City vs Nottingham Forest"]

# Create input columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 ODDS")
    home_odds = st.number_input("Home Odds", min_value=1.01, max_value=100.0, 
                               value=example_data["home_odds"], step=0.1)
    draw_odds = st.number_input("Draw Odds", min_value=1.01, max_value=100.0,
                               value=example_data["draw_odds"], step=0.1)
    away_odds = st.number_input("Away Odds", min_value=1.01, max_value=100.0,
                               value=example_data["away_odds"], step=0.1)
    
    st.markdown("#### 🏆 TABLE POSITION")
    home_pos = st.number_input("Home Position", min_value=1, max_value=20,
                              value=example_data["home_pos"])
    home_pts = st.number_input("Home Points", min_value=0, max_value=100,
                              value=example_data["home_pts"])
    away_pos = st.number_input("Away Position", min_value=1, max_value=20,
                              value=example_data["away_pos"])
    away_pts = st.number_input("Away Points", min_value=0, max_value=100,
                              value=example_data["away_pts"])

with col2:
    st.markdown("#### 🔄 H2H (Last 3 meetings)")
    h2h1 = st.text_input("Match 1", value=example_data["h2h_scores"][0])
    h2h2 = st.text_input("Match 2", value=example_data["h2h_scores"][1])
    h2h3 = st.text_input("Match 3", value=example_data["h2h_scores"][2])
    h2h_scores = [h2h1, h2h2, h2h3]
    
    st.markdown("#### 📈 RECENT FORM (Last 5)")
    home_form = st.text_input("Home Form (W/D/L)", value=example_data["home_form"],
                             placeholder="e.g., WWLWD")
    away_form = st.text_input("Away Form (W/D/L)", value=example_data["away_form"],
                             placeholder="e.g., LDDLW")
    
    st.markdown("#### 🎯 MANAGER STYLES")
    home_manager = st.text_input("Home Manager", value=example_data["home_manager"])
    away_manager = st.text_input("Away Manager", value=example_data["away_manager"])

# -------------------------------------------------------------------
# 3. ANALYZE AND PREDICT
# -------------------------------------------------------------------
st.markdown("---")

if st.button("🔍 ANALYZE & PREDICT", type="primary", use_container_width=True):
    
    # Prepare match data
    match_data = {
        'home_odds': home_odds,
        'draw_odds': draw_odds,
        'away_odds': away_odds,
        'home_pos': home_pos,
        'home_pts': home_pts,
        'away_pos': away_pos,
        'away_pts': away_pts,
        'h2h_scores': h2h_scores,
        'home_form': home_form.upper(),
        'away_form': away_form.upper(),
        'home_manager': home_manager,
        'away_manager': away_manager
    }
    
    # Get prediction
    prediction = predictor.predict(match_data)
    interpretations = prediction['interpretations']
    
    # Store in session state
    st.session_state.current_prediction = {
        'match': selected_match,
        'prediction': prediction,
        'match_data': match_data
    }
    
    # -------------------------------------------------------------------
    # 3A. SHOW SYSTEM INTERPRETATION
    # -------------------------------------------------------------------
    st.subheader("🧠 SYSTEM INTERPRETATION")
    
    interp_col1, interp_col2 = st.columns(2)
    
    with interp_col1:
        st.markdown("##### 📊 ODDS ANALYSIS")
        st.info(f"**{interpretations['odds'][0]}**")
        st.write(f"Probability: {interpretations['odds'][1]:.1f}%")
        st.write(f"Favorite: {interpretations['odds'][2]}")
        
        st.markdown("##### 🏆 TABLE ANALYSIS")
        st.info(f"**{interpretations['table'][0]}**")
        st.write(interpretations['table'][1])
        
        st.markdown("##### 🔄 H2H ANALYSIS")
        st.info(f"**{interpretations['h2h'][0]}**")
        st.write(interpretations['h2h'][1])
    
    with interp_col2:
        st.markdown("##### 📈 FORM ANALYSIS")
        st.info(f"**{interpretations['form'][0]}**")
        st.write(interpretations['form'][1])
        
        st.markdown("##### 🎯 STYLE ANALYSIS")
        st.info(f"**{interpretations['style'][0]}**")
        st.write(interpretations['style'][1])
    
    # -------------------------------------------------------------------
    # 3B. SHOW PREDICTION
    # -------------------------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 PREDICTION")
    
    narrative_descriptions = {
        "BLITZKRIEG": "Early domination - Favorite crushes weak opponent",
        "SHOOTOUT": "End-to-end chaos - Both teams attack relentlessly",
        "SIEGE": "Attack vs Defense - Attacker dominates but struggles to break through",
        "CHESS": "Tactical battle - Low scoring, cautious approach from both"
    }
    
    confidence = prediction['score']
    narrative = prediction['narrative']
    
    if confidence >= 75:
        tier = "TIER 1 (HIGH CONFIDENCE)"
        stake = "2-3% of bankroll"
        color = "green"
    elif confidence >= 60:
        tier = "TIER 2 (MEDIUM CONFIDENCE)"
        stake = "1-2% of bankroll"
        color = "orange"
    else:
        tier = "TIER 3 (LOW CONFIDENCE)"
        stake = "0.5-1% of bankroll"
        color = "red"
    
    # Prediction display
    col_pred1, col_pred2 = st.columns(2)
    
    with col_pred1:
        st.markdown(f"""
        <div style="padding: 1.5rem; border-radius: 10px; background-color: #f8f9fa; border-left: 5px solid {color};">
            <h2>🏆 {narrative}</h2>
            <h1>{confidence}/100</h1>
            <p>{narrative_descriptions[narrative]}</p>
            <br>
            <p><strong>{tier}</strong></p>
            <p>Recommended stake: {stake}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pred2:
        # Show all scores
        st.markdown("#### All Narrative Scores")
        for narr, score in prediction['scores'].items():
            col_score1, col_score2, col_score3 = st.columns([2, 5, 1])
            with col_score1:
                st.write(narr)
            with col_score2:
                st.progress(score/100)
            with col_score3:
                st.write(f"{score}")
    
    # -------------------------------------------------------------------
    # 3C. BETTING RECOMMENDATIONS
    # -------------------------------------------------------------------
    st.markdown("---")
    st.subheader("💰 BETTING RECOMMENDATIONS")
    
    # Get teams for bet names
    home_team = selected_match.split(" vs ")[0]
    away_team = selected_match.split(" vs ")[1]
    
    betting_recommendations = {
        "BLITZKRIEG": [
            {"bet": f"{home_team if interpretations['odds'][2] == 'Home' else away_team} -1.5 Handicap", 
             "odds": "1.85-2.00", "stake": "2-3%", "why": "Favorite expected to dominate"},
            {"bet": "First Goal < 30 minutes", 
             "odds": "1.70-1.90", "stake": "1-2%", "why": "Early pressure likely"},
            {"bet": f"{home_team if interpretations['odds'][2] == 'Home' else away_team} Clean Sheet", 
             "odds": "2.00-2.30", "stake": "1-2%", "why": "Weak opponent unlikely to score"}
        ],
        "SHOOTOUT": [
            {"bet": "Over 2.5 Goals", 
             "odds": "1.70-1.90", "stake": "2-3%", "why": "High scoring history expected"},
            {"bet": "Both Teams to Score", 
             "odds": "1.60-1.80", "stake": "2-3%", "why": "Both teams attacking"},
            {"bet": "Late Goal (75+ minutes)", 
             "odds": "2.30-2.70", "stake": "1-2%", "why": "End-to-end action continues late"}
        ],
        "SIEGE": [
            {"bet": "Under 2.5 Goals", 
             "odds": "1.80-2.00", "stake": "2-3%", "why": "Defensive setup limits goals"},
            {"bet": f"{home_team if interpretations['odds'][2] == 'Home' else away_team} to Win", 
             "odds": "1.60-1.80", "stake": "2-3%", "why": "Attacker should eventually break through"},
            {"bet": "BTTS: No", 
             "odds": "1.90-2.10", "stake": "1-2%", "why": "Defender struggles to score"}
        ],
        "CHESS": [
            {"bet": "Under 2.5 Goals", 
             "odds": "1.70-1.90", "stake": "2-3%", "why": "Cautious approach from both"},
            {"bet": "BTTS: No", 
             "odds": "1.80-2.00", "stake": "2-3%", "why": "Defensive focus limits scoring chances"},
            {"bet": "0-0 or 1-0 Correct Score", 
             "odds": "3.00-4.00", "stake": "1-2%", "why": "Low scoring patterns expected"}
        ]
    }
    
    bets = betting_recommendations[narrative]
    
    bet_cols = st.columns(3)
    
    for idx, bet in enumerate(bets):
        with bet_cols[idx]:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 8px; background-color: white; border: 1px solid #e0e0e0; height: 250px;">
                <h4>✅ BET {idx+1}</h4>
                <h3>{bet['bet']}</h3>
                <p><strong>Odds:</strong> {bet['odds']}</p>
                <p><strong>Stake:</strong> {bet['stake']}</p>
                <p><em>{bet['why']}</em></p>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 4. TRACK RESULTS (Always visible if we have prediction)
# -------------------------------------------------------------------
if 'current_prediction' in st.session_state:
    st.markdown("---")
    st.subheader("📋 TRACK RESULT")
    
    pred = st.session_state.current_prediction
    
    col_track1, col_track2, col_track3, col_track4 = st.columns([2, 1, 1, 1])
    
    with col_track1:
        actual_score = st.text_input("Final Score", placeholder="e.g., 3-0")
        notes = st.text_input("Match Notes", placeholder="What actually happened?")
    
    with col_track2:
        if st.button("✅ Correct", use_container_width=True):
            st.session_state.predictions.append({
                'match': pred['match'],
                'predicted_narrative': pred['prediction']['narrative'],
                'predicted_score': pred['prediction']['score'],
                'actual_score': actual_score,
                'notes': notes,
                'correct': 'Yes',
                'date': datetime.now().strftime("%Y-%m-%d")
            })
            st.success("✅ Prediction saved as correct!")
            st.rerun()
    
    with col_track3:
        if st.button("⚠️ Partial", use_container_width=True):
            st.session_state.predictions.append({
                'match': pred['match'],
                'predicted_narrative': pred['prediction']['narrative'],
                'predicted_score': pred['prediction']['score'],
                'actual_score': actual_score,
                'notes': notes,
                'correct': 'Partial',
                'date': datetime.now().strftime("%Y-%m-%d")
            })
            st.warning("⚠️ Prediction saved as partial match")
            st.rerun()
    
    with col_track4:
        if st.button("❌ Wrong", use_container_width=True):
            st.session_state.predictions.append({
                'match': pred['match'],
                'predicted_narrative': pred['prediction']['narrative'],
                'predicted_score': pred['prediction']['score'],
                'actual_score': actual_score,
                'notes': notes,
                'correct': 'No',
                'date': datetime.now().strftime("%Y-%m-%d")
            })
            st.error("❌ Prediction saved - we'll learn from this!")
            st.rerun()

# -------------------------------------------------------------------
# 5. PERFORMANCE HISTORY
# -------------------------------------------------------------------
if st.session_state.predictions:
    st.markdown("---")
    st.subheader("📊 PERFORMANCE HISTORY")
    
    # Calculate metrics
    rated_predictions = [p for p in st.session_state.predictions if p.get('correct') in ['Yes', 'Partial', 'No']]
    
    if rated_predictions:
        correct = sum(1 for p in rated_predictions if p['correct'] == 'Yes')
        partial = sum(1 for p in rated_predictions if p['correct'] == 'Partial')
        total = len(rated_predictions)
        accuracy = (correct + partial * 0.5) / total * 100
        
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1:
            st.metric("Total Predictions", total)
        with col_met2:
            st.metric("Correct", correct)
        with col_met3:
            st.metric("Partial", partial)
        with col_met4:
            st.metric("Accuracy", f"{accuracy:.1f}%")
        
        # Show recent predictions
        st.markdown("#### Recent Predictions")
        recent_data = []
        for pred in st.session_state.predictions[-10:]:  # Last 10
            recent_data.append({
                "Date": pred.get('date', 'N/A'),
                "Match": pred['match'],
                "Prediction": pred['predicted_narrative'],
                "Score": pred['predicted_score'],
                "Actual": pred.get('actual_score', 'N/A'),
                "Result": pred.get('correct', 'Not rated'),
                "Notes": pred.get('notes', '')[:30] + "..." if pred.get('notes') else ''
            })
        
        df = pd.DataFrame(recent_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------
# 6. QUICK START GUIDE
# -------------------------------------------------------------------
with st.expander("📚 QUICK START GUIDE"):
    st.markdown("""
    ### **How to Use This Tool:**
    
    1. **SELECT A MATCH** - Choose from examples or create custom
    2. **INPUT RAW DATA** - Enter what you see (no interpretation needed):
       - **Odds** from betting sites
       - **Table positions** from league table
       - **H2H scores** from head-to-head history
       - **Recent form** (W/D/L from last 5 games)
       - **Manager names** for style analysis
    3. **CLICK ANALYZE** - System interprets data and makes prediction
    4. **SEE BETS** - Get 3 tailored betting recommendations
    5. **TRACK RESULT** - Save outcome after the match
    
    ### **Where to Find Data:**
    - **Odds**: Bet365, William Hill, any betting site
    - **Table**: Premier League official site, Sky Sports
    - **H2H**: FlashScore, Premier League H2H
    - **Form**: Last 5 results (W = win, D = draw, L = loss)
    - **Managers**: Just enter names (system knows styles)
    
    ### **Try the Examples:**
    - **Man City vs Forest** → Shows BLITZKRIEG
    - **Spurs vs Liverpool** → Shows SHOOTOUT  
    - **Arsenal vs Chelsea** → Shows CHESS MATCH
    
    ### **Time Required:**
    - **First time**: 5 minutes to understand
    - **Per match**: 2-3 minutes to input data
    - **Analysis**: Instant after clicking
    """)

# -------------------------------------------------------------------
# 7. QUICK EXAMPLE BUTTONS
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("⚡ QUICK EXAMPLES")

example_cols = st.columns(4)

with example_cols[0]:
    if st.button("Man City vs Forest", use_container_width=True):
        st.session_state.current_match = "Manchester City vs Nottingham Forest"
        st.rerun()

with example_cols[1]:
    if st.button("Spurs vs Liverpool", use_container_width=True):
        st.session_state.current_match = "Tottenham vs Liverpool"
        st.rerun()

with example_cols[2]:
    if st.button("Arsenal vs Chelsea", use_container_width=True):
        st.session_state.current_match = "Arsenal vs Chelsea"
        st.rerun()

with example_cols[3]:
    if st.button("Newcastle vs Everton", use_container_width=True):
        st.session_state.current_match = "Newcastle vs Everton"
        st.rerun()
