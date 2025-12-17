import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Narrative Football Predictor",
    page_icon="⚽",
    layout="centered"
)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'current_match' not in st.session_state:
    st.session_state.current_match = None

# CSS for better styling
st.markdown("""
<style>
    .match-card {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .prediction-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #00cc96;
    }
    .bet-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: white;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .check-card {
        padding: 0.5rem;
        border-radius: 8px;
        background-color: #f0f7ff;
        border: 1px solid #d0e0ff;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("⚽ Narrative Football Predictor")
st.markdown("**5 checks → 1 prediction → 3 bets → 1 validation**")

# -------------------------------------------------------------------
# 1. MATCH SELECTION
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("1️⃣ SELECT MATCH")

matches = [
    "Manchester City vs Nottingham Forest",
    "Tottenham Hotspur vs Liverpool",
    "Newcastle United vs Everton", 
    "Arsenal vs Chelsea",
    "West Ham vs Aston Villa",
    "Custom Match..."
]

selected_match = st.selectbox("Choose a match:", matches)

if selected_match == "Custom Match...":
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
<div class="match-card">
    <h4>{selected_match}</h4>
    <p>Premier League • Saturday 3pm</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. CHECK THE 5 THINGS
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("2️⃣ CHECK THE 5 THINGS")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="check-card">
        <h5>📊 ODDS</h5>
    </div>
    """, unsafe_allow_html=True)
    
    odds_choice = st.radio(
        "Favorite strength:",
        ["Strong favorite (1.20-1.40)", "Moderate favorite (1.50-1.80)", "Even match (2.00+)", "Underdog favored"],
        key="odds",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="check-card">
        <h5>📈 FORM</h5>
    </div>
    """, unsafe_allow_html=True)
    
    form_choice = st.radio(
        "Last 5 games:",
        ["Favorite winning, opponent losing", "Both in good form", "Both struggling", "Mixed results"],
        key="form",
        label_visibility="collapsed"
    )

with col3:
    st.markdown("""
    <div class="check-card">
        <h5>🔄 H2H</h5>
    </div>
    """, unsafe_allow_html=True)
    
    h2h_choice = st.radio(
        "Last 3 meetings:",
        ["Favorite dominates", "Close low-scoring", "High scoring games", "No clear pattern"],
        key="h2h",
        label_visibility="collapsed"
    )

with col4:
    st.markdown("""
    <div class="check-card">
        <h5>🏆 TABLE</h5>
    </div>
    """, unsafe_allow_html=True)
    
    table_choice = st.radio(
        "Motivation:",
        ["Favorite needs win, opponent safe", "Both need points", "Nothing to play for", "Underdog desperate"],
        key="table",
        label_visibility="collapsed"
    )

with col5:
    st.markdown("""
    <div class="check-card">
        <h5>🎯 STYLE</h5>
    </div>
    """, unsafe_allow_html=True)
    
    style_choice = st.radio(
        "Manager styles:",
        ["Attack vs Defense", "Both attack-minded", "Both defensive", "Mixed approaches"],
        key="style",
        label_visibility="collapsed"
    )

# -------------------------------------------------------------------
# 3. PREDICTION ENGINE
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ PREDICTED NARRATIVE")

# Calculate prediction based on selections
def calculate_prediction(odds, form, h2h, table, style):
    """Simple prediction logic"""
    
    # Count checks for each narrative
    blitzkrieg_checks = 0
    shootout_checks = 0
    siege_checks = 0
    chess_checks = 0
    
    # Odds check
    if "Strong favorite" in odds:
        blitzkrieg_checks += 2
        siege_checks += 1
    elif "Even match" in odds:
        shootout_checks += 1
        chess_checks += 1
    
    # Form check
    if "Favorite winning, opponent losing" in form:
        blitzkrieg_checks += 2
    elif "Both in good form" in form:
        shootout_checks += 2
    
    # H2H check
    if "Favorite dominates" in h2h:
        blitzkrieg_checks += 2
    elif "Close low-scoring" in h2h:
        chess_checks += 2
        siege_checks += 1
    elif "High scoring games" in h2h:
        shootout_checks += 2
    
    # Table check
    if "Favorite needs win, opponent safe" in table:
        blitzkrieg_checks += 2
        siege_checks += 1
    elif "Both need points" in table:
        shootout_checks += 1
        chess_checks += 1
    
    # Style check
    if "Attack vs Defense" in style:
        blitzkrieg_checks += 1
        siege_checks += 2
    elif "Both attack-minded" in style:
        shootout_checks += 2
    elif "Both defensive" in style:
        chess_checks += 2
    
    # Determine winner
    scores = {
        "BLITZKRIEG": blitzkrieg_checks,
        "SHOOTOUT": shootout_checks,
        "SIEGE": siege_checks,
        "CHESS": chess_checks
    }
    
    winner = max(scores, key=scores.get)
    score = scores[winner] * 10 + 35  # Convert to 45-85 range
    
    # Adjust score based on consistency
    if scores[winner] >= 4:
        score += 10
    elif scores[winner] <= 2:
        score -= 10
    
    return winner, min(max(score, 45), 85)

if st.button("🎯 GENERATE PREDICTION", type="primary", use_container_width=True):
    narrative, confidence = calculate_prediction(odds_choice, form_choice, h2h_choice, table_choice, style_choice)
    
    # Store prediction
    prediction_data = {
        "match": selected_match,
        "narrative": narrative,
        "confidence": confidence,
        "checks": {
            "odds": odds_choice,
            "form": form_choice,
            "h2h": h2h_choice,
            "table": table_choice,
            "style": style_choice
        }
    }
    st.session_state.current_prediction = prediction_data
    
    # Display prediction
    narrative_descriptions = {
        "BLITZKRIEG": "Early domination - Favorite crushes weak opponent",
        "SHOOTOUT": "End-to-end chaos - Both teams attack relentlessly",
        "SIEGE": "Attack vs Defense - Attacker dominates but struggles to break through",
        "CHESS": "Tactical battle - Low scoring, cautious approach from both"
    }
    
    tier = "TIER 1 (High)" if confidence >= 75 else "TIER 2 (Medium)" if confidence >= 60 else "TIER 3 (Low)"
    
    st.markdown(f"""
    <div class="prediction-card">
        <h3>🏆 {narrative}</h3>
        <h2>{confidence}/100 • {tier}</h2>
        <p>{narrative_descriptions[narrative]}</p>
        <br>
        <p><strong>Checks matched:</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show which checks matched
    checks = []
    if "Strong favorite" in odds_choice and narrative == "BLITZKRIEG":
        checks.append("✓ Strong favorite odds")
    if "Favorite winning, opponent losing" in form_choice and narrative in ["BLITZKRIEG", "SIEGE"]:
        checks.append("✓ Form mismatch")
    if "Favorite dominates" in h2h_choice and narrative == "BLITZKRIEG":
        checks.append("✓ Historical domination")
    if "Favorite needs win, opponent safe" in table_choice and narrative in ["BLITZKRIEG", "SIEGE"]:
        checks.append("✓ Table position mismatch")
    if "Attack vs Defense" in style_choice and narrative in ["BLITZKRIEG", "SIEGE"]:
        checks.append("✓ Style clash")
    if "Both attack-minded" in style_choice and narrative == "SHOOTOUT":
        checks.append("✓ Both attacking")
    if "Both defensive" in style_choice and narrative == "CHESS":
        checks.append("✓ Both cautious")
    if "Both need points" in table_choice and narrative in ["SHOOTOUT", "CHESS"]:
        checks.append("✓ High stakes both")
    
    for check in checks:
        st.write(check)
    
    # -------------------------------------------------------------------
    # 4. BETTING RECOMMENDATIONS
    # -------------------------------------------------------------------
    st.markdown("---")
    st.subheader("4️⃣ RECOMMENDED BETS")
    
    # Get teams for bet names
    home_team = selected_match.split(" vs ")[0]
    away_team = selected_match.split(" vs ")[1]
    
    betting_recommendations = {
        "BLITZKRIEG": [
            {"bet": f"{home_team} -1.5 Handicap", "odds": "1.90", "stake": "2-3%"},
            {"bet": f"{home_team} Clean Sheet", "odds": "2.10", "stake": "1-2%"},
            {"bet": "First Goal < 25 mins", "odds": "1.85", "stake": "1-2%"}
        ],
        "SHOOTOUT": [
            {"bet": "Over 2.5 Goals", "odds": "1.80", "stake": "2-3%"},
            {"bet": "Both Teams to Score", "odds": "1.70", "stake": "2-3%"},
            {"bet": "Late Goal (>75 mins)", "odds": "2.50", "stake": "1-2%"}
        ],
        "SIEGE": [
            {"bet": f"{home_team} to Win", "odds": "1.60", "stake": "2-3%"},
            {"bet": "Under 2.5 Goals", "odds": "1.90", "stake": "2-3%"},
            {"bet": "BTTS: No", "odds": "2.00", "stake": "1-2%"}
        ],
        "CHESS": [
            {"bet": "Under 2.5 Goals", "odds": "1.80", "stake": "2-3%"},
            {"bet": "BTTS: No", "odds": "1.90", "stake": "2-3%"},
            {"bet": "0-0 or 1-0 Correct Score", "odds": "3.50", "stake": "1-2%"}
        ]
    }
    
    bets = betting_recommendations[narrative]
    
    col1, col2, col3 = st.columns(3)
    
    for idx, bet in enumerate(bets):
        with [col1, col2, col3][idx]:
            st.markdown(f"""
            <div class="bet-card">
                <h5>✅ BET {idx+1}</h5>
                <h4>{bet['bet']}</h4>
                <p>Odds: {bet['odds']}</p>
                <p><strong>Stake: {bet['stake']}</strong></p>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 5. TRACK RESULT (Always visible)
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("5️⃣ TRACK RESULT")

if 'current_prediction' in st.session_state:
    pred = st.session_state.current_prediction
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        actual_result = st.text_input("Actual Score", placeholder="e.g., 3-0")
    
    with col2:
        if st.button("✅ Prediction Correct", use_container_width=True):
            st.session_state.predictions.append({
                **pred,
                "actual_score": actual_result if actual_result else "N/A",
                "correct": "Yes"
            })
            st.success("Result saved! Prediction marked as correct.")
            st.rerun()
    
    with col3:
        if st.button("❌ Wrong Prediction", use_container_width=True):
            st.session_state.predictions.append({
                **pred,
                "actual_score": actual_result if actual_result else "N/A",
                "correct": "No"
            })
            st.error("Result saved! We'll learn from this.")
            st.rerun()

# -------------------------------------------------------------------
# 6. PREDICTION HISTORY
# -------------------------------------------------------------------
if st.session_state.predictions:
    st.markdown("---")
    st.subheader("📊 PREDICTION HISTORY")
    
    history_data = []
    for pred in st.session_state.predictions[-5:]:  # Show last 5
        history_data.append({
            "Match": pred["match"],
            "Prediction": pred["narrative"],
            "Confidence": f"{pred['confidence']}/100",
            "Actual": pred.get("actual_score", "Not recorded"),
            "Correct": pred.get("correct", "Not rated")
        })
    
    if history_data:
        df = pd.DataFrame(history_data)
        
        # Calculate accuracy
        rated_predictions = [p for p in st.session_state.predictions if p.get("correct") in ["Yes", "No"]]
        if rated_predictions:
            correct_count = sum(1 for p in rated_predictions if p["correct"] == "Yes")
            accuracy = (correct_count / len(rated_predictions)) * 100
            
            col_acc1, col_acc2, col_acc3 = st.columns(3)
            with col_acc1:
                st.metric("Total Predictions", len(rated_predictions))
            with col_acc2:
                st.metric("Correct", correct_count)
            with col_acc3:
                st.metric("Accuracy", f"{accuracy:.1f}%")
        
        st.dataframe(df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------
# 7. QUICK EXAMPLES
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("⚡ QUICK EXAMPLES")

examples = st.columns(3)

with examples[0]:
    if st.button("Man City vs Forest\nBLITZKRIEG", use_container_width=True):
        st.session_state.odds = "Strong favorite (1.20-1.40)"
        st.session_state.form = "Favorite winning, opponent losing"
        st.session_state.h2h = "Favorite dominates"
        st.session_state.table = "Favorite needs win, opponent safe"
        st.session_state.style = "Attack vs Defense"
        st.rerun()

with examples[1]:
    if st.button("West Ham vs Villa\nSHOOTOUT", use_container_width=True):
        st.session_state.odds = "Even match (2.00+)"
        st.session_state.form = "Both in good form"
        st.session_state.h2h = "High scoring games"
        st.session_state.table = "Both need points"
        st.session_state.style = "Both attack-minded"
        st.rerun()

with examples[2]:
    if st.button("Arsenal vs Chelsea\nCHESS", use_container_width=True):
        st.session_state.odds = "Even match (2.00+)"
        st.session_state.form = "Mixed results"
        st.session_state.h2h = "Close low-scoring"
        st.session_state.table = "Both need points"
        st.session_state.style = "Both defensive"
        st.rerun()

# -------------------------------------------------------------------
# 8. HOW TO USE
# -------------------------------------------------------------------
with st.expander("📚 HOW TO USE THIS TOOL"):
    st.markdown("""
    ### **Simple 5-Step Process:**
    
    1. **SELECT MATCH** - Pick from examples or create your own
    2. **CHECK 5 THINGS** - Answer simple questions about the match
    3. **GET PREDICTION** - System identifies the narrative pattern
    4. **SEE BETTING TIPS** - Get 3 clear betting recommendations
    5. **TRACK RESULT** - One-click validation after the match
    
    ### **The 5 Checks Explained:**
    
    **📊 ODDS** - How strong is the favorite?
    - Strong favorite (1.20-1.40 odds) = 70-83% win probability
    
    **📈 FORM** - How are teams performing?
    - Check last 5 games on FlashScore
    
    **🔄 H2H** - What's the historical pattern?
    - Look up last 3 meetings
    
    **🏆 TABLE** - Who needs what?
    - League position = motivation level
    
    **🎯 STYLE** - Attack or defense?
    - Manager tendencies (Klopp = attack, Dyche = defense)
    
    ### **Betting Stake Guide:**
    - **TIER 1 (75+ confidence)**: 2-3% of bankroll
    - **TIER 2 (60-74 confidence)**: 1-2% of bankroll  
    - **TIER 3 (45-59 confidence)**: 0.5-1% of bankroll
    
    ### **Start Now:**
    1. Click "Man City vs Forest" example
    2. Click "Generate Prediction"
    3. See the BLITZKRIEG prediction
    4. Try other examples to see different narratives
    """)

# Initialize session state values
if 'odds' not in st.session_state:
    st.session_state.odds = "Strong favorite (1.20-1.40)"
if 'form' not in st.session_state:
    st.session_state.form = "Favorite winning, opponent losing"
if 'h2h' not in st.session_state:
    st.session_state.h2h = "Favorite dominates"
if 'table' not in st.session_state:
    st.session_state.table = "Favorite needs win, opponent safe"
if 'style' not in st.session_state:
    st.session_state.style = "Attack vs Defense"
