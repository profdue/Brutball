import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Narrative Predictor",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ 3-Input Narrative Predictor")
st.markdown("**No data needed - just your football knowledge**")

# -------------------------------------------------------------------
# ULTRA-SIMPLE PREDICTION ENGINE
# -------------------------------------------------------------------
class SimplePredictor:
    def __init__(self):
        self.narratives = {
            "BLITZKRIEG": "Favorite crushes weak opponent early",
            "SHOOTOUT": "End-to-end chaos, both teams attack",
            "SIEGE": "Attacker dominates but struggles to break down defense",
            "CHESS": "Tactical battle, low scoring, cautious"
        }
    
    def predict(self, style_clash, stakes, favorite_strength):
        """Predict based on 3 simple inputs"""
        
        # Decision logic
        if favorite_strength >= 8 and style_clash >= 7:  # Strong favorite vs weak
            narrative = "BLITZKRIEG"
            score = 75 + (favorite_strength * 2)
        
        elif style_clash >= 6 and stakes >= 7:  # Both attack, high stakes
            narrative = "SHOOTOUT"
            score = 70 + (style_clash * 3)
        
        elif style_clash >= 7 and stakes >= 6:  # Attack vs defense
            narrative = "SIEGE"
            score = 65 + (style_clash * 2)
        
        elif favorite_strength <= 5 and stakes >= 8:  # Even, high importance
            narrative = "CHESS"
            score = 68 + (stakes * 2)
        
        else:
            narrative = "MIXED"
            score = 55
        
        return {
            "narrative": narrative,
            "score": min(score, 95),
            "description": self.narratives.get(narrative, "Mixed signals")
        }
    
    def get_bets(self, narrative, home, away):
        """Simple betting recommendations"""
        bets = {
            "BLITZKRIEG": [
                f"{home} to win",
                f"{home} clean sheet",
                "First goal before 30:00",
                f"{home} -1.5 handicap"
            ],
            "SHOOTOUT": [
                "Over 2.5 goals",
                "BTTS: Yes",
                "Late goal (after 75:00)",
                "2-1 or 3-2 correct score"
            ],
            "SIEGE": [
                f"{home} to win",
                "Under 2.5 goals",
                "BTTS: No",
                "1-0 or 2-0 correct score"
            ],
            "CHESS": [
                "Under 2.5 goals",
                "BTTS: No",
                "0-0 or 1-0 correct score",
                "Fewer than 10 corners"
            ],
            "MIXED": [
                "Avoid pre-match bets",
                "Wait for in-play",
                "Consider alternative markets",
                "Small stakes only"
            ]
        }
        
        return bets.get(narrative, ["No clear edge"])

# -------------------------------------------------------------------
# SIMPLE INTERFACE
# -------------------------------------------------------------------
st.header("🎯 Match Assessment")

col1, col2 = st.columns(2)

with col1:
    home = st.text_input("Home Team", "Manchester City")
    away = st.text_input("Away Team", "Nottingham Forest")

with col2:
    st.write("**Quick Context:**")
    competition = st.selectbox("Competition", ["Premier League", "Championship", "FA Cup", "Other"])
    is_derby = st.checkbox("Derby/Rivalry Match")

st.divider()

# -------------------------------------------------------------------
# ONLY 3 INPUTS NEEDED
# -------------------------------------------------------------------
st.header("📊 Only 3 Questions Needed")

# 1. Style Clash
st.subheader("1. Style Clash")
st.write("How different are the teams' playing styles?")
style_clash = st.slider(
    "Attacking vs Defensive mismatch (1 = similar, 10 = complete opposites)",
    1, 10, 7,
    help="7 = Man City attack vs Forest defense\n3 = Two similar midtable teams"
)

# 2. Stakes
st.subheader("2. Stakes Pressure")
st.write("How much does this match matter?")
stakes = st.slider(
    "Match Importance (1 = friendly, 10 = must-win final)",
    1, 10, 8,
    help="10 = Title decider, relegation 6-pointer\n5 = Midtable with nothing to play for"
)

# 3. Favorite Strength
st.subheader("3. Favorite Strength")
st.write("How much stronger is the favorite?")
favorite_strength = st.slider(
    "Favorite Advantage (1 = even, 10 = massive favorite)",
    1, 10, 9,
    help="9 = Man City vs Forest\n3 = Two closely matched teams\n1 = Complete toss-up"
)

st.divider()

# -------------------------------------------------------------------
# PREDICTION
# -------------------------------------------------------------------
if st.button("🎯 GET PREDICTION", type="primary", use_container_width=True):
    
    predictor = SimplePredictor()
    prediction = predictor.predict(style_clash, stakes, favorite_strength)
    bets = predictor.get_bets(prediction["narrative"], home, away)
    
    # Display results
    st.header("📈 Prediction Results")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric("Predicted Narrative", prediction["narrative"])
        st.write(f"**{prediction['description']}**")
        
        st.metric("Confidence Score", f"{prediction['score']}/100")
        st.progress(prediction['score']/100)
    
    with col_res2:
        # Confidence tier
        if prediction["score"] >= 75:
            tier = "TIER 1 (HIGH CONFIDENCE)"
            stake = "2-3% of bankroll"
        elif prediction["score"] >= 60:
            tier = "TIER 2 (MEDIUM CONFIDENCE)"
            stake = "1-2% of bankroll"
        else:
            tier = "TIER 3 (LOW CONFIDENCE)"
            stake = "0.5-1% or avoid"
        
        st.metric("Confidence Tier", tier)
        st.metric("Recommended Stake", stake)
    
    # Betting recommendations
    st.subheader("💰 Betting Recommendations")
    
    for bet in bets:
        st.write(f"✅ **{bet}**")
    
    # Expected flow
    st.subheader("📊 Expected Match Flow")
    
    flows = {
        "BLITZKRIEG": [
            f"• {home} dominates from start",
            "• Early goal likely (0-30 mins)",
            "• Opponent confidence collapses",
            "• Multiple goals for favorite",
            "• Clean sheet probable"
        ],
        "SHOOTOUT": [
            "• Fast start from both teams",
            "• Early goals at both ends",
            "• Lead changes possible",
            "• End-to-end throughout",
            "• Late drama likely"
        ],
        "SIEGE": [
            f"• {home} controls possession",
            f"• {away} defends deep",
            "• Frustration builds",
            "• Breakthrough 45-70 mins",
            "• Clean sheet OR counter goal"
        ],
        "CHESS": [
            "• Cautious opening 30 mins",
            "• Few clear chances",
            "• Set pieces crucial",
            "• First goal decisive",
            "• Low scoring throughout"
        ],
        "MIXED": [
            "• Unpredictable start",
            "• Could go multiple ways",
            "• Watch first 20 mins closely",
            "• In-play opportunities better",
            "• Risk of surprise result"
        ]
    }
    
    for flow in flows.get(prediction["narrative"], []):
        st.write(flow)
    
    # Validation
    st.divider()
    st.subheader("📋 Quick Validation")
    
    col_val1, col_val2, col_val3 = st.columns(3)
    
    with col_val1:
        if st.button("✅ Correct", use_container_width=True):
            st.success("Prediction validated as correct!")
    
    with col_val2:
        if st.button("⚠️ Partial", use_container_width=True):
            st.warning("Partial match - some elements right")
    
    with col_val3:
        if st.button("❌ Wrong", use_container_width=True):
            st.error("Prediction missed - will learn from this")

# -------------------------------------------------------------------
# EXAMPLES
# -------------------------------------------------------------------
st.divider()
st.header("⚡ Quick Examples")

examples = [
    ("Man City vs Forest", 8, 8, 9, "BLITZKRIEG"),
    ("West Ham vs Villa", 7, 7, 5, "SHOOTOUT"),
    ("Arsenal vs Chelsea", 4, 9, 6, "CHESS"),
    ("Newcastle vs Everton", 7, 6, 7, "SIEGE")
]

for i, (match, style, stake, fav, expected) in enumerate(examples):
    if st.button(f"{match} → {expected}", key=f"ex_{i}", use_container_width=True):
        st.session_state["style_clash"] = style
        st.session_state["stakes"] = stake
        st.session_state["favorite_strength"] = fav
        st.rerun()

# -------------------------------------------------------------------
# HOW TO USE GUIDE
# -------------------------------------------------------------------
with st.expander("📚 How to Use This System"):
    st.markdown("""
    ## **Only 3 Questions Needed:**
    
    ### **1. Style Clash (1-10)**
    - **1-3**: Similar styles (both defensive/both attacking)
    - **4-6**: Some differences but not extreme
    - **7-10**: Complete mismatch (attack vs defense)
    
    ### **2. Stakes (1-10)**
    - **1-3**: Friendly, preseason, nothing to play for
    - **4-6**: Normal league match, some importance
    - **7-10**: Must-win, derby, final, relegation battle
    
    ### **3. Favorite Strength (1-10)**
    - **1-3**: Even match, toss-up
    - **4-6**: Slight favorite
    - **7-10**: Heavy favorite vs weak opponent
    
    ## **That's it!** 
    
    No stats needed. Just your football knowledge.
    """)

# Initialize session state
if "style_clash" not in st.session_state:
    st.session_state["style_clash"] = 7
if "stakes" not in st.session_state:
    st.session_state["stakes"] = 8
if "favorite_strength" not in st.session_state:
    st.session_state["favorite_strength"] = 9
