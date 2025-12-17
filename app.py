import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Narrative Predictor Pro",
    page_icon="⚽",
    layout="wide"
)

# Initialize session state
if 'all_predictions' not in st.session_state:
    st.session_state.all_predictions = []
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []

# -------------------------------------------------------------------
# FIXTURES DATABASE
# -------------------------------------------------------------------
fixtures_db = {
    "SPANISH LA LIGA": [
        {"match": "Valencia vs Real Mallorca", "date": "19/12/2025"},
        {"match": "Real Oviedo vs Celta Vigo", "date": "20/12/2025"},
        {"match": "Levante vs Real Sociedad", "date": "20/12/2025"},
        {"match": "Osasuna vs Deportivo Alavés", "date": "20/12/2025"},
        {"match": "Real Madrid vs Sevilla", "date": "20/12/2025"},
        {"match": "Girona vs Atlético Madrid", "date": "21/12/2025"},
        {"match": "Villarreal vs Barcelona", "date": "21/12/2025"},
        {"match": "Elche vs Rayo Vallecano", "date": "21/12/2025"},
        {"match": "Real Betis vs Getafe", "date": "21/12/2025"},
        {"match": "Athletic Bilbao vs Espanyol", "date": "22/12/2025"}
    ],
    "ENGLISH PREMIER LEAGUE": [
        {"match": "Newcastle United vs Chelsea", "date": "20/12/2025"},
        {"match": "Bournemouth vs Burnley", "date": "20/12/2025"},
        {"match": "Brighton vs Sunderland", "date": "20/12/2025"},
        {"match": "Manchester City vs West Ham", "date": "20/12/2025"},
        {"match": "Wolverhampton vs Brentford", "date": "20/12/2025"},
        {"match": "Tottenham vs Liverpool", "date": "20/12/2025"},
        {"match": "Everton vs Arsenal", "date": "20/12/2025"},
        {"match": "Leeds United vs Crystal Palace", "date": "20/12/2025"},
        {"match": "Aston Villa vs Manchester United", "date": "21/12/2025"},
        {"match": "Fulham vs Nottingham Forest", "date": "22/12/2025"}
    ],
    "GERMAN BUNDESLIGA": [
        {"match": "Borussia Dortmund vs Borussia M'gladbach", "date": "19/12/2025"},
        {"match": "Köln vs Union Berlin", "date": "20/12/2025"},
        {"match": "Stuttgart vs Hoffenheim", "date": "20/12/2025"},
        {"match": "Wolfsburg vs Freiburg", "date": "20/12/2025"},
        {"match": "Hamburger SV vs Eintracht Frankfurt", "date": "20/12/2025"},
        {"match": "Augsburg vs Werder Bremen", "date": "20/12/2025"},
        {"match": "RB Leipzig vs Bayer Leverkusen", "date": "20/12/2025"},
        {"match": "Mainz vs St Pauli", "date": "21/12/2025"},
        {"match": "Heidenheim vs Bayern Munich", "date": "21/12/2025"}
    ],
    "ITALIAN SERIE A": [
        {"match": "Lazio vs Cremonese", "date": "20/12/2025"},
        {"match": "Juventus vs Roma", "date": "20/12/2025"},
        {"match": "Cagliari vs AC Pisa", "date": "21/12/2025"},
        {"match": "Inter vs Lecce", "date": "21/12/2025"},
        {"match": "Verona vs Bologna", "date": "21/12/2025"},
        {"match": "Calcio Como vs Milan", "date": "21/12/2025"},
        {"match": "Napoli vs Parma", "date": "21/12/2025"},
        {"match": "Sassuolo vs Torino", "date": "21/12/2025"},
        {"match": "Fiorentina vs Udinese", "date": "21/12/2025"},
        {"match": "Genoa vs Atalanta", "date": "21/12/2025"}
    ],
    "FRENCH LIGUE 1": [
        {"match": "Toulouse vs Lens", "date": "02/01/2026"},
        {"match": "Monaco vs Lyon", "date": "03/01/2026"},
        {"match": "Nice vs Strasbourg", "date": "03/01/2026"},
        {"match": "Lille vs Rennes", "date": "03/01/2026"},
        {"match": "Olympique Marseille vs Nantes", "date": "04/01/2026"},
        {"match": "Lorient vs Metz", "date": "04/01/2026"},
        {"match": "Brest vs Auxerre", "date": "04/01/2026"},
        {"match": "PSG vs Paris FC", "date": "04/01/2026"}
    ],
    "DUTCH EREDIVISIE": [
        {"match": "Heracles vs Heerenveen", "date": "20/12/2025"},
        {"match": "Excelsior vs PEC Zwolle", "date": "20/12/2025"},
        {"match": "Nijmegen vs Ajax", "date": "20/12/2025"},
        {"match": "NAC Breda vs SC Telstar", "date": "20/12/2025"},
        {"match": "Utrecht vs PSV Eindhoven", "date": "21/12/2025"},
        {"match": "Go Ahead Eagles vs Groningen", "date": "21/12/2025"},
        {"match": "Feyenoord vs Twente", "date": "21/12/2025"},
        {"match": "Volendam vs Sparta Rotterdam", "date": "21/12/2025"}
    ],
    "PORTUGUESE PRIMEIRA LIGA": [
        {"match": "GD Estoril vs Sporting Braga", "date": "19/12/2025"},
        {"match": "Gil Vicente vs Rio Ave", "date": "20/12/2025"},
        {"match": "Estrela Amadora vs Moreirense FC", "date": "20/12/2025"},
        {"match": "AVS vs Nacional Madeira", "date": "21/12/2025"},
        {"match": "CD Tondela vs Casa Pia AC", "date": "21/12/2025"},
        {"match": "Santa Clara vs FC Arouca", "date": "21/12/2025"},
        {"match": "FC Alverca vs Porto", "date": "22/12/2025"},
        {"match": "SL Benfica vs FC Famalicão", "date": "22/12/2025"},
        {"match": "Vitória vs Sporting CP", "date": "23/12/2025"}
    ],
    "TURKISH SÜPER LIG": [
        {"match": "Kocaelispor vs Antalyaspor", "date": "19/12/2025"},
        {"match": "Konyaspor vs Kayserispor", "date": "20/12/2025"},
        {"match": "Besiktas vs Rizespor", "date": "20/12/2025"},
        {"match": "Alanyaspor vs Fatih Karagümrük", "date": "21/12/2025"},
        {"match": "Galatasaray vs Kasımpasa SK", "date": "21/12/2025"},
        {"match": "Göztepe Izmir vs Samsunspor", "date": "21/12/2025"},
        {"match": "Basaksehir vs Gaziantep", "date": "22/12/2025"}
    ]
}

# -------------------------------------------------------------------
# QUICK PREDICTION ENGINE
# -------------------------------------------------------------------
class QuickPredictor:
    """Quick narrative prediction based on team reputation and match context"""
    
    def __init__(self):
        # Team reputation database (simplified for quick predictions)
        self.team_tiers = {
            # Spanish La Liga
            "Real Madrid": {"tier": 1, "style": "attack"},
            "Barcelona": {"tier": 1, "style": "attack"},
            "Atlético Madrid": {"tier": 1, "style": "defense"},
            "Real Sociedad": {"tier": 2, "style": "balanced"},
            "Villarreal": {"tier": 2, "style": "attack"},
            "Real Betis": {"tier": 2, "style": "attack"},
            "Sevilla": {"tier": 2, "style": "balanced"},
            "Athletic Bilbao": {"tier": 2, "style": "attack"},
            "Valencia": {"tier": 2, "style": "balanced"},
            "Girona": {"tier": 2, "style": "attack"},
            "Osasuna": {"tier": 3, "style": "defense"},
            "Getafe": {"tier": 3, "style": "defense"},
            "Celta Vigo": {"tier": 3, "style": "balanced"},
            "Rayo Vallecano": {"tier": 3, "style": "attack"},
            "Mallorca": {"tier": 3, "style": "defense"},
            "Alavés": {"tier": 3, "style": "defense"},
            "Levante": {"tier": 3, "style": "balanced"},
            "Espanyol": {"tier": 3, "style": "balanced"},
            "Elche": {"tier": 4, "style": "defense"},
            "Oviedo": {"tier": 4, "style": "balanced"},
            
            # Premier League
            "Manchester City": {"tier": 1, "style": "attack"},
            "Liverpool": {"tier": 1, "style": "attack"},
            "Arsenal": {"tier": 1, "style": "attack"},
            "Chelsea": {"tier": 1, "style": "attack"},
            "Manchester United": {"tier": 1, "style": "balanced"},
            "Tottenham": {"tier": 1, "style": "attack"},
            "Newcastle United": {"tier": 1, "style": "attack"},
            "Aston Villa": {"tier": 2, "style": "attack"},
            "West Ham": {"tier": 2, "style": "balanced"},
            "Brighton": {"tier": 2, "style": "attack"},
            "Brentford": {"tier": 2, "style": "attack"},
            "Crystal Palace": {"tier": 3, "style": "defense"},
            "Fulham": {"tier": 3, "style": "balanced"},
            "Wolverhampton": {"tier": 3, "style": "defense"},
            "Everton": {"tier": 3, "style": "defense"},
            "Bournemouth": {"tier": 3, "style": "attack"},
            "Nottingham Forest": {"tier": 3, "style": "defense"},
            "Burnley": {"tier": 4, "style": "defense"},
            "Sunderland": {"tier": 4, "style": "balanced"},
            "Leeds United": {"tier": 4, "style": "attack"},
            
            # Bundesliga
            "Bayern Munich": {"tier": 1, "style": "attack"},
            "Borussia Dortmund": {"tier": 1, "style": "attack"},
            "Bayer Leverkusen": {"tier": 1, "style": "attack"},
            "RB Leipzig": {"tier": 1, "style": "attack"},
            "Eintracht Frankfurt": {"tier": 2, "style": "balanced"},
            "Wolfsburg": {"tier": 2, "style": "balanced"},
            "Freiburg": {"tier": 2, "style": "defense"},
            "Hoffenheim": {"tier": 2, "style": "attack"},
            "Stuttgart": {"tier": 2, "style": "attack"},
            "Werder Bremen": {"tier": 3, "style": "attack"},
            "Borussia M'gladbach": {"tier": 3, "style": "balanced"},
            "Union Berlin": {"tier": 3, "style": "defense"},
            "Köln": {"tier": 3, "style": "balanced"},
            "Augsburg": {"tier": 3, "style": "defense"},
            "Heidenheim": {"tier": 4, "style": "defense"},
            "Mainz": {"tier": 4, "style": "balanced"},
            "Hamburger SV": {"tier": 4, "style": "attack"},
            "St Pauli": {"tier": 4, "style": "balanced"},
            
            # Serie A
            "Inter": {"tier": 1, "style": "balanced"},
            "Milan": {"tier": 1, "style": "attack"},
            "Juventus": {"tier": 1, "style": "defense"},
            "Napoli": {"tier": 1, "style": "attack"},
            "Roma": {"tier": 1, "style": "balanced"},
            "Atalanta": {"tier": 1, "style": "attack"},
            "Lazio": {"tier": 2, "style": "balanced"},
            "Fiorentina": {"tier": 2, "style": "attack"},
            "Torino": {"tier": 2, "style": "defense"},
            "Bologna": {"tier": 2, "style": "balanced"},
            "Genoa": {"tier": 3, "style": "defense"},
            "Monza": {"tier": 3, "style": "balanced"},
            "Udinese": {"tier": 3, "style": "balanced"},
            "Sassuolo": {"tier": 3, "style": "attack"},
            "Verona": {"tier": 3, "style": "defense"},
            "Cagliari": {"tier": 4, "style": "defense"},
            "Lecce": {"tier": 4, "style": "defense"},
            "Parma": {"tier": 4, "style": "balanced"},
            "Cremonese": {"tier": 4, "style": "defense"},
            "AC Pisa": {"tier": 4, "style": "balanced"},
            "Calcio Como": {"tier": 4, "style": "balanced"},
            
            # Ligue 1
            "PSG": {"tier": 1, "style": "attack"},
            "Monaco": {"tier": 1, "style": "attack"},
            "Lyon": {"tier": 1, "style": "attack"},
            "Lille": {"tier": 1, "style": "balanced"},
            "Olympique Marseille": {"tier": 1, "style": "attack"},
            "Rennes": {"tier": 2, "style": "attack"},
            "Nice": {"tier": 2, "style": "defense"},
            "Lens": {"tier": 2, "style": "attack"},
            "Toulouse": {"tier": 3, "style": "attack"},
            "Strasbourg": {"tier": 3, "style": "balanced"},
            "Nantes": {"tier": 3, "style": "defense"},
            "Lorient": {"tier": 3, "style": "attack"},
            "Metz": {"tier": 4, "style": "defense"},
            "Brest": {"tier": 4, "style": "balanced"},
            "Auxerre": {"tier": 4, "style": "defense"},
            "Paris FC": {"tier": 4, "style": "balanced"},
            
            # Eredivisie
            "Ajax": {"tier": 1, "style": "attack"},
            "PSV Eindhoven": {"tier": 1, "style": "attack"},
            "Feyenoord": {"tier": 1, "style": "attack"},
            "Twente": {"tier": 2, "style": "balanced"},
            "AZ Alkmaar": {"tier": 2, "style": "attack"},
            "Utrecht": {"tier": 2, "style": "balanced"},
            "Heerenveen": {"tier": 3, "style": "attack"},
            "Groningen": {"tier": 3, "style": "balanced"},
            "Nijmegen": {"tier": 3, "style": "defense"},
            "Heracles": {"tier": 3, "style": "balanced"},
            "Excelsior": {"tier": 4, "style": "attack"},
            "PEC Zwolle": {"tier": 4, "style": "balanced"},
            "NAC Breda": {"tier": 4, "style": "balanced"},
            "SC Telstar": {"tier": 4, "style": "defense"},
            "Go Ahead Eagles": {"tier": 4, "style": "balanced"},
            "Volendam": {"tier": 4, "style": "attack"},
            "Sparta Rotterdam": {"tier": 4, "style": "defense"},
            
            # Primeira Liga
            "Porto": {"tier": 1, "style": "attack"},
            "SL Benfica": {"tier": 1, "style": "attack"},
            "Sporting CP": {"tier": 1, "style": "attack"},
            "Sporting Braga": {"tier": 1, "style": "attack"},
            "Vitória": {"tier": 2, "style": "attack"},
            "Rio Ave": {"tier": 3, "style": "balanced"},
            "Gil Vicente": {"tier": 3, "style": "balanced"},
            "Estrela Amadora": {"tier": 3, "style": "defense"},
            "Moreirense FC": {"tier": 3, "style": "defense"},
            "AVS": {"tier": 4, "style": "defense"},
            "Nacional Madeira": {"tier": 4, "style": "balanced"},
            "CD Tondela": {"tier": 4, "style": "defense"},
            "Casa Pia AC": {"tier": 4, "style": "defense"},
            "Santa Clara": {"tier": 4, "style": "balanced"},
            "FC Arouca": {"tier": 4, "style": "defense"},
            "FC Alverca": {"tier": 4, "style": "defense"},
            "FC Famalicão": {"tier": 4, "style": "balanced"},
            "GD Estoril": {"tier": 4, "style": "balanced"},
            
            # Süper Lig
            "Galatasaray": {"tier": 1, "style": "attack"},
            "Besiktas": {"tier": 1, "style": "attack"},
            "Fenerbahce": {"tier": 1, "style": "attack"},
            "Basaksehir": {"tier": 2, "style": "balanced"},
            "Antalyaspor": {"tier": 2, "style": "balanced"},
            "Kayserispor": {"tier": 2, "style": "balanced"},
            "Konyaspor": {"tier": 3, "style": "defense"},
            "Alanyaspor": {"tier": 3, "style": "attack"},
            "Rizespor": {"tier": 3, "style": "defense"},
            "Fatih Karagümrük": {"tier": 3, "style": "balanced"},
            "Kasımpasa SK": {"tier": 3, "style": "attack"},
            "Göztepe Izmir": {"tier": 3, "style": "attack"},
            "Samsunspor": {"tier": 4, "style": "defense"},
            "Gaziantep": {"tier": 4, "style": "defense"},
            "Kocaelispor": {"tier": 4, "style": "balanced"}
        }
    
    def get_team_info(self, team_name):
        """Get team tier and style, with fallback for unknown teams"""
        # Try exact match
        if team_name in self.team_tiers:
            return self.team_tiers[team_name]
        
        # Try partial match
        for known_team, info in self.team_tiers.items():
            if known_team.lower() in team_name.lower() or team_name.lower() in known_team.lower():
                return info
        
        # Default for unknown teams
        return {"tier": 3, "style": "balanced"}
    
    def predict_match(self, match_name):
        """Make quick prediction based on team reputations"""
        # Split match into teams
        if " vs " in match_name:
            home_team, away_team = match_name.split(" vs ")
        else:
            home_team, away_team = match_name, "Unknown"
        
        # Get team info
        home_info = self.get_team_info(home_team.strip())
        away_info = self.get_team_info(away_team.strip())
        
        # Calculate tier difference
        tier_diff = home_info["tier"] - away_info["tier"]
        
        # Determine favorite
        if tier_diff > 1:
            favorite = "HOME"
            favorite_strength = "STRONG"
        elif tier_diff > 0:
            favorite = "HOME"
            favorite_strength = "MODERATE"
        elif tier_diff < -1:
            favorite = "AWAY"
            favorite_strength = "STRONG"
        elif tier_diff < 0:
            favorite = "AWAY"
            favorite_strength = "MODERATE"
        else:
            favorite = "EVEN"
            favorite_strength = "EVEN"
        
        # Determine style clash
        style_clash = f"{home_info['style'].upper()} vs {away_info['style'].upper()}"
        
        # Make prediction based on tier difference and styles
        if favorite_strength == "STRONG" and "ATTACK vs DEFENSE" in style_clash:
            narrative = "BLITZKRIEG"
            confidence = 75 + (abs(tier_diff) * 5)
        elif favorite_strength == "MODERATE" and "ATTACK vs DEFENSE" in style_clash:
            narrative = "SIEGE"
            confidence = 65 + (abs(tier_diff) * 5)
        elif favorite == "EVEN" and "ATTACK vs ATTACK" in style_clash:
            narrative = "SHOOTOUT"
            confidence = 70
        elif favorite == "EVEN" and ("DEFENSE vs DEFENSE" in style_clash or "BALANCED" in style_clash):
            narrative = "CHESS"
            confidence = 65
        elif abs(tier_diff) <= 1:
            narrative = "SIEGE" if "ATTACK vs DEFENSE" in style_clash else "CHESS"
            confidence = 60
        else:
            narrative = "MIXED"
            confidence = 50
        
        # Add variance based on home advantage
        if favorite == "HOME":
            confidence += 5
        elif favorite == "AWAY":
            confidence -= 5
        
        # Cap confidence
        confidence = min(max(confidence, 45), 85)
        
        # Determine tier
        if confidence >= 75:
            prediction_tier = "TIER 1 (HIGH)"
        elif confidence >= 60:
            prediction_tier = "TIER 2 (MEDIUM)"
        else:
            prediction_tier = "TIER 3 (LOW)"
        
        return {
            "match": match_name,
            "narrative": narrative,
            "confidence": confidence,
            "tier": prediction_tier,
            "home_team": home_team.strip(),
            "away_team": away_team.strip(),
            "home_tier": home_info["tier"],
            "away_tier": away_info["tier"],
            "style_clash": style_clash,
            "favorite": favorite,
            "favorite_strength": favorite_strength,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

# -------------------------------------------------------------------
# STREAMLIT APP
# -------------------------------------------------------------------
st.title("⚽ Weekend Narrative Predictor")
st.markdown("**Batch analysis for 70+ matches across 8 leagues**")

# Initialize predictor
predictor = QuickPredictor()

# -------------------------------------------------------------------
# 1. LEAGUE SELECTION
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("1️⃣ SELECT LEAGUES TO ANALYZE")

# League selection checkboxes
leagues = list(fixtures_db.keys())
selected_leagues = []

cols = st.columns(4)
for i, league in enumerate(leagues):
    with cols[i % 4]:
        if st.checkbox(league, value=True):
            selected_leagues.append(league)

# -------------------------------------------------------------------
# 2. BATCH PREDICTION
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("2️⃣ GENERATE BATCH PREDICTIONS")

if st.button("🎯 PREDICT ALL SELECTED MATCHES", type="primary", use_container_width=True):
    
    all_matches = []
    for league in selected_leagues:
        for fixture in fixtures_db[league]:
            all_matches.append({
                "league": league,
                "match": fixture["match"],
                "date": fixture["date"]
            })
    
    st.session_state.batch_results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Make predictions
    for idx, match_info in enumerate(all_matches):
        status_text.text(f"Analyzing {match_info['match']}...")
        
        prediction = predictor.predict_match(match_info["match"])
        prediction["league"] = match_info["league"]
        prediction["date"] = match_info["date"]
        
        st.session_state.batch_results.append(prediction)
        
        # Update progress
        progress_bar.progress((idx + 1) / len(all_matches))
    
    status_text.text("✅ Analysis complete!")
    progress_bar.empty()

# -------------------------------------------------------------------
# 3. RESULTS DISPLAY
# -------------------------------------------------------------------
if st.session_state.batch_results:
    st.markdown("---")
    st.subheader("3️⃣ PREDICTION RESULTS")
    
    # Convert to DataFrame for display
    results_df = pd.DataFrame(st.session_state.batch_results)
    
    # Summary statistics
    total_matches = len(results_df)
    tier1_count = len(results_df[results_df['tier'].str.contains('TIER 1')])
    tier2_count = len(results_df[results_df['tier'].str.contains('TIER 2')])
    tier3_count = len(results_df[results_df['tier'].str.contains('TIER 3')])
    
    # Narrative distribution
    narrative_counts = results_df['narrative'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", total_matches)
    with col2:
        st.metric("Tier 1 Predictions", tier1_count)
    with col3:
        st.metric("Tier 2 Predictions", tier2_count)
    with col4:
        st.metric("Average Confidence", f"{results_df['confidence'].mean():.1f}")
    
    # Narrative distribution chart
    st.markdown("#### Narrative Distribution")
    narrative_data = pd.DataFrame({
        'Narrative': narrative_counts.index,
        'Count': narrative_counts.values
    })
    
    # Display as bar chart
    chart_data = narrative_data.set_index('Narrative')
    st.bar_chart(chart_data)
    
    # -------------------------------------------------------------------
    # 3A. FILTERABLE RESULTS TABLE
    # -------------------------------------------------------------------
    st.markdown("#### Filter Predictions")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_narratives = st.multiselect(
            "Filter by Narrative",
            options=results_df['narrative'].unique(),
            default=results_df['narrative'].unique()
        )
    
    with filter_col2:
        selected_tiers = st.multiselect(
            "Filter by Tier",
            options=results_df['tier'].unique(),
            default=results_df['tier'].unique()
        )
    
    with filter_col3:
        selected_leagues_filter = st.multiselect(
            "Filter by League",
            options=results_df['league'].unique(),
            default=results_df['league'].unique()
        )
    
    # Apply filters
    filtered_df = results_df[
        (results_df['narrative'].isin(selected_narratives)) &
        (results_df['tier'].isin(selected_tiers)) &
        (results_df['league'].isin(selected_leagues_filter))
    ]
    
    # Display table with key columns
    display_df = filtered_df[['league', 'match', 'date', 'narrative', 'confidence', 'tier', 'style_clash']].copy()
    display_df = display_df.sort_values(['confidence', 'league'], ascending=[False, True])
    
    # Color coding for narratives
    def color_narrative(val):
        if val == 'BLITZKRIEG':
            return 'background-color: #FFE5E5'
        elif val == 'SHOOTOUT':
            return 'background-color: #E5FFE5'
        elif val == 'SIEGE':
            return 'background-color: #E5F3FF'
        elif val == 'CHESS':
            return 'background-color: #FFF9E5'
        else:
            return ''
    
    # Color coding for tiers
    def color_tier(val):
        if 'TIER 1' in val:
            return 'background-color: #D4EDDA; color: #155724'
        elif 'TIER 2' in val:
            return 'background-color: #FFF3CD; color: #856404'
        else:
            return 'background-color: #F8D7DA; color: #721C24'
    
    styled_df = display_df.style\
        .applymap(color_narrative, subset=['narrative'])\
        .applymap(color_tier, subset=['tier'])\
        .format({'confidence': '{:.1f}'})
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # -------------------------------------------------------------------
    # 3B. KEY MATCHES HIGHLIGHTS
    # -------------------------------------------------------------------
    st.markdown("#### 🎯 Key Matches to Watch")
    
    # Get top 10 highest confidence predictions
    top_matches = filtered_df.nlargest(10, 'confidence')
    
    for idx, match in top_matches.iterrows():
        with st.expander(f"**{match['match']}** - {match['narrative']} ({match['confidence']:.1f}/100)"):
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.write(f"**League:** {match['league']}")
                st.write(f"**Date:** {match['date']}")
                st.write(f"**Style:** {match['style_clash']}")
            
            with col_info2:
                st.write(f"**Narrative:** {match['narrative']}")
                st.write(f"**Confidence:** {match['confidence']:.1f}/100")
                st.write(f"**Tier:** {match['tier']}")
            
            with col_info3:
                # Betting recommendations
                bets = {
                    "BLITZKRIEG": [
                        "Favorite -1.5 handicap",
                        "Favorite clean sheet",
                        "First goal <30 mins"
                    ],
                    "SHOOTOUT": [
                        "Over 2.5 goals",
                        "BTTS: Yes",
                        "Late goal (75+ mins)"
                    ],
                    "SIEGE": [
                        "Under 2.5 goals",
                        "Favorite to win",
                        "BTTS: No"
                    ],
                    "CHESS": [
                        "Under 2.5 goals",
                        "BTTS: No",
                        "0-0 or 1-0 score"
                    ]
                }
                
                st.write("**Recommended Bets:**")
                for bet in bets.get(match['narrative'], ["Monitor odds"]):
                    st.write(f"• {bet}")
    
    # -------------------------------------------------------------------
    # 3C. BULK ACTIONS
    # -------------------------------------------------------------------
    st.markdown("#### 📋 Bulk Actions")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("📥 Save All Predictions", use_container_width=True):
            # Save to session state
            for pred in st.session_state.batch_results:
                st.session_state.all_predictions.append(pred)
            st.success(f"✅ Saved {len(st.session_state.batch_results)} predictions")
    
    with col_act2:
        # Export to CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Export to CSV",
            data=csv,
            file_name=f"narrative_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_act3:
        # Export to JSON
        json_data = filtered_df.to_dict(orient='records')
        st.download_button(
            label="📊 Export to JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"narrative_predictions_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# -------------------------------------------------------------------
# 4. PREDICTION HISTORY
# -------------------------------------------------------------------
if st.session_state.all_predictions:
    st.markdown("---")
    st.subheader("📊 PREDICTION HISTORY")
    
    history_df = pd.DataFrame(st.session_state.all_predictions)
    
    # Calculate accuracy metrics
    st.markdown("##### 📈 Performance Summary")
    
    col_hist1, col_hist2, col_hist3, col_hist4 = st.columns(4)
    with col_hist1:
        st.metric("Total Predictions", len(history_df))
    with col_hist2:
        st.metric("Unique Matches", history_df['match'].nunique())
    with col_hist3:
        avg_conf = history_df['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_conf:.1f}")
    with col_hist4:
        # Narrative distribution
        top_narrative = history_df['narrative'].mode()[0] if not history_df.empty else "N/A"
        st.metric("Most Common", top_narrative)
    
    # Recent predictions
    st.markdown("##### Recent Predictions")
    recent_display = history_df[['timestamp', 'league', 'match', 'narrative', 'confidence', 'tier']].tail(10)
    st.dataframe(recent_display, use_container_width=True)

# -------------------------------------------------------------------
# 5. QUICK ANALYSIS TOOLS
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("🔍 Quick Analysis Tools")

tool_cols = st.columns(3)

with tool_cols[0]:
    if st.button("🔍 Analyze Single Match", use_container_width=True):
        st.session_state.show_single_analysis = True

with tool_cols[1]:
    if st.button("📊 Compare Leagues", use_container_width=True):
        st.session_state.show_league_comparison = True

with tool_cols[2]:
    if st.button("🎯 Find Best Bets", use_container_width=True):
        st.session_state.show_best_bets = True

# Single match analysis
if 'show_single_analysis' in st.session_state and st.session_state.show_single_analysis:
    st.markdown("---")
    st.subheader("🔍 Single Match Analysis")
    
    # Get all unique matches
    all_matches_list = []
    for league, fixtures in fixtures_db.items():
        for fixture in fixtures:
            all_matches_list.append(f"{fixture['match']} ({league})")
    
    selected_single_match = st.selectbox("Select a match:", all_matches_list[:50])
    
    if selected_single_match:
        match_name = selected_single_match.split(" (")[0]
        prediction = predictor.predict_match(match_name)
        
        col_single1, col_single2 = st.columns(2)
        
        with col_single1:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 10px; background-color: #f8f9fa; border-left: 5px solid #00cc96;">
                <h3>🏆 {prediction['narrative']}</h3>
                <h1>{prediction['confidence']:.1f}/100</h1>
                <p><strong>{prediction['tier']}</strong></p>
                <p>Style: {prediction['style_clash']}</p>
                <p>Favorite: {prediction['favorite']} ({prediction['favorite_strength']})</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_single2:
            # Team analysis
            st.markdown("#### Team Analysis")
            st.write(f"**{prediction['home_team']}**: Tier {prediction['home_tier']}")
            st.write(f"**{prediction['away_team']}**: Tier {prediction['away_tier']}")
            st.write(f"**Tier Difference**: {abs(prediction['home_tier'] - prediction['away_tier'])}")
            
            # Betting recommendations
            st.markdown("#### 💰 Betting Tips")
            bets = {
                "BLITZKRIEG": ["Favorite -1.5 handicap", "Clean sheet", "Early goal"],
                "SHOOTOUT": ["Over 2.5 goals", "BTTS: Yes", "Late drama"],
                "SIEGE": ["Under 2.5 goals", "Favorite win", "BTTS: No"],
                "CHESS": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0"]
            }
            
            for bet in bets.get(prediction['narrative'], ["Monitor odds"]):
                st.write(f"• {bet}")

# -------------------------------------------------------------------
# 6. HOW TO USE
# -------------------------------------------------------------------
with st.expander("📚 HOW TO USE THIS TOOL"):
    st.markdown("""
    ### **Weekend Analysis Workflow:**
    
    1. **SELECT LEAGUES** - Choose which leagues to analyze (default: all)
    2. **CLICK PREDICT** - System analyzes 70+ matches in seconds
    3. **REVIEW RESULTS** - See narrative predictions for all matches
    4. **FILTER & EXPORT** - Focus on specific narratives or tiers
    5. **TRACK PERFORMANCE** - Save predictions and compare with results
    
    ### **Understanding the Predictions:**
    
    **🏆 NARRATIVES:**
    - **BLITZKRIEG**: Strong favorite vs weak opponent
    - **SHOOTOUT**: Two attack-minded teams, high scoring
    - **SIEGE**: Attack vs defense, low scoring
    - **CHESS**: Two cautious teams, tactical battle
    
    **📊 TIERS:**
    - **TIER 1 (HIGH)**: 75+ confidence - Strong bets
    - **TIER 2 (MEDIUM)**: 60-74 confidence - Good bets
    - **TIER 3 (LOW)**: <60 confidence - Caution advised
    
    ### **Quick Tips:**
    
    1. **Focus on Tier 1 matches** for strongest predictions
    2. **Use filters** to find specific narrative types
    3. **Export predictions** for weekend tracking
    4. **Check key matches** highlighted by the system
    
    ### **This Weekend's Key Matches:**
    
    Based on team reputations, watch for:
    - **Real Madrid vs Sevilla** (likely BLITZKRIEG)
    - **Tottenham vs Liverpool** (likely SHOOTOUT)
    - **Arsenal vs Everton** (could be SIEGE)
    - **Juventus vs Roma** (likely CHESS)
    
    ### **Start Now:**
    1. Keep all leagues selected
    2. Click "Predict All Selected Matches"
    3. Watch as 70+ matches are analyzed
    4. Review the predictions and betting tips
    """)

# -------------------------------------------------------------------
# 7. FOOTER
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚽ <strong>Narrative Predictor Pro</strong> | Analyze 70+ matches in seconds</p>
    <p>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
""".format(datetime=datetime), unsafe_allow_html=True)
