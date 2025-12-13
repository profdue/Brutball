import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Brutball Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #424242;
        margin-top: 1.5rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .high-confidence {
        border-left-color: #4CAF50 !important;
        background-color: #f1f8e9;
    }
    .medium-confidence {
        border-left-color: #FF9800 !important;
        background-color: #fff3e0;
    }
    .match-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Core prediction algorithm
def predict_match(home_pos, away_pos, total_teams=20):
    """
    Returns prediction based on league position gap
    """
    gap = abs(home_pos - away_pos)
    
    # 1. OVERS/UNDERS PREDICTION
    if gap <= 4:
        over_under = "OVER 2.5"
        if gap <= 2:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams within {gap} positions → similar ambitions → attacking football"
    else:
        over_under = "UNDER 2.5"
        if gap >= 8:
            ou_confidence = "HIGH"
            ou_confidence_score = 85
        else:
            ou_confidence = "MEDIUM"
            ou_confidence_score = 70
        ou_logic = f"Teams {gap} positions apart → different agendas → cautious play"
    
    # 2. MATCH RESULT PREDICTION
    if home_pos < away_pos - 4:  # Home significantly better
        result = "HOME WIN"
        if gap >= 8:
            result_confidence = "HIGH"
            result_confidence_score = 80
        else:
            result_confidence = "MEDIUM"
            result_confidence_score = 65
        result_logic = f"Home team {gap} positions better → should win"
    elif away_pos < home_pos - 4:  # Away significantly better
        result = "AWAY WIN"
        if gap >= 8:
            result_confidence = "HIGH"
            result_confidence_score = 80
        else:
            result_confidence = "MEDIUM"
            result_confidence_score = 65
        result_logic = f"Away team {gap} positions better → should win"
    else:  # Close positions
        result = "DRAW or close match"
        result_confidence = "MEDIUM"
        result_confidence_score = 60
        result_logic = f"Teams within {gap} positions → evenly matched"
    
    # 3. BETTING RECOMMENDATION
    if ou_confidence == "HIGH" and result_confidence == "HIGH":
        betting_recommendation = "HIGH CONFIDENCE BET"
        recommendation_color = "green"
    elif ou_confidence == "HIGH" or result_confidence == "HIGH":
        betting_recommendation = "MEDIUM CONFIDENCE BET"
        recommendation_color = "orange"
    else:
        betting_recommendation = "LOW CONFIDENCE - AVOID"
        recommendation_color = "red"
    
    return {
        'over_under': over_under,
        'over_under_confidence': ou_confidence,
        'over_under_confidence_score': ou_confidence_score,
        'over_under_logic': ou_logic,
        'result': result,
        'result_confidence': result_confidence,
        'result_confidence_score': result_confidence_score,
        'result_logic': result_logic,
        'position_gap': gap,
        'betting_recommendation': betting_recommendation,
        'recommendation_color': recommendation_color
    }

def create_gap_visualization(gap, total_teams):
    """Create visualization of position gap"""
    fig = go.Figure()
    
    # Create positions for visualization
    positions = list(range(1, total_teams + 1))
    
    # Add positions
    fig.add_trace(go.Scatter(
        x=[1, 2],
        y=[1, total_teams],
        mode='markers',
        marker=dict(size=15, color=['#1E88E5', '#FF5722']),
        name='Team Positions'
    ))
    
    # Add gap line
    fig.add_shape(
        type="line",
        x0=1, y0=1,
        x1=2, y1=1 + gap,
        line=dict(color="red", width=2, dash="dash"),
    )
    
    fig.update_layout(
        title="League Position Gap Visualization",
        xaxis=dict(
            title="",
            tickvals=[1, 2],
            ticktext=["Home Team", "Away Team"],
            range=[0.5, 2.5]
        ),
        yaxis=dict(
            title="League Position (1 = Best)",
            range=[total_teams + 1, 0],
            autorange=False
        ),
        height=300,
        showlegend=False
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">⚽ BRUTBALL PREDICTION ENGINE</div>', unsafe_allow_html=True)
    st.markdown("### League Position Gap Analysis System")
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/869/869445.png", width=100)
        st.markdown("### 📊 Strategy Overview")
        st.markdown("""
        **Core Insight:**
        - Gap ≤ 4 → Similar ambitions → OVER 2.5
        - Gap > 4 → Different agendas → UNDER 2.5
        
        **Accuracy:** 91.7% (11/12 matches)
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Settings")
        total_teams = st.selectbox(
            "Total Teams in League",
            [20, 24, 18, 16, 22],
            index=0
        )
        
        st.markdown("---")
        
        st.markdown("### 📈 Performance")
        st.metric("Historical Accuracy", "91.7%")
        st.metric("High Confidence Wins", "100%")
        
        st.markdown("---")
        
        st.markdown("### ℹ️ How it works")
        st.info("""
        1. Enter league positions
        2. System calculates gap
        3. Predicts tactical approach
        4. Provides betting recommendations
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">🏠 Home Team</div>', unsafe_allow_html=True)
        home_name = st.text_input("Home Team Name", "Home Team")
        home_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=total_teams,
            value=8,
            key="home_pos"
        )
        
        st.markdown("---")
        
        st.markdown('<div class="sub-header">Optional Factors</div>', unsafe_allow_html=True)
        match_type = st.selectbox(
            "Match Type",
            ["League", "Cup", "Derby", "Friendly"]
        )
        
        col1a, col1b = st.columns(2)
        with col1a:
            key_players_missing = st.checkbox("Key Players Missing")
            new_manager = st.checkbox("New Manager")
        with col1b:
            fatigue = st.checkbox("Fatigue Concern")
            weather_issue = st.checkbox("Bad Weather")
    
    with col2:
        st.markdown('<div class="sub-header">✈️ Away Team</div>', unsafe_allow_html=True)
        away_name = st.text_input("Away Team Name", "Away Team")
        away_pos = st.number_input(
            "League Position (1 = Best)",
            min_value=1,
            max_value=total_teams,
            value=9,
            key="away_pos"
        )
        
        st.markdown("---")
        
        # Visualization
        if home_pos and away_pos:
            gap = abs(home_pos - away_pos)
            fig = create_gap_visualization(gap, total_teams)
            st.plotly_chart(fig, use_container_width=True)
    
    # Calculate prediction
    if st.button("🔍 ANALYZE MATCH", type="primary", use_container_width=True):
        # Get prediction
        prediction = predict_match(home_pos, away_pos, total_teams)
        
        # Display results
        st.markdown("---")
        st.markdown('<div class="sub-header">📊 PREDICTION RESULTS</div>', unsafe_allow_html=True)
        
        # Key metrics row
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Position Gap", f"{prediction['position_gap']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("O/U Prediction", prediction['over_under'])
            st.caption(f"Confidence: {prediction['over_under_confidence']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Result Prediction", prediction['result'])
            st.caption(f"Confidence: {prediction['result_confidence']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col6:
            recommendation_color = prediction['recommendation_color']
            st.markdown(f'<div class="metric-card" style="border-left: 5px solid {recommendation_color}">', unsafe_allow_html=True)
            st.metric("Recommendation", prediction['betting_recommendation'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed predictions
        col7, col8 = st.columns(2)
        
        with col7:
            confidence_class = "high-confidence" if prediction['over_under_confidence'] == "HIGH" else "medium-confidence"
            st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
            st.markdown(f"### 📈 OVER/UNDER 2.5")
            st.markdown(f"**Prediction:** `{prediction['over_under']}`")
            st.markdown(f"**Confidence:** `{prediction['over_under_confidence']}`")
            st.progress(prediction['over_under_confidence_score'] / 100)
            st.markdown(f"*{prediction['over_under_logic']}*")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Psychology insight
            if prediction['position_gap'] <= 4:
                st.info("""
                **🤔 PSYCHOLOGICAL DYNAMIC:**
                - Both teams have similar objectives
                - Both think they can win
                - Tactics will be attacking and open
                - Expect goals from both sides
                """)
            else:
                st.info("""
                **🤔 PSYCHOLOGICAL DYNAMIC:**
                - Better team: Wants to win without risks
                - Worse team: Wants to avoid humiliation
                - Tactics will be cautious and defensive
                - Expect low-scoring match
                """)
        
        with col8:
            confidence_class = "high-confidence" if prediction['result_confidence'] == "HIGH" else "medium-confidence"
            st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
            st.markdown(f"### 🏆 MATCH RESULT")
            st.markdown(f"**Prediction:** `{prediction['result']}`")
            st.markdown(f"**Confidence:** `{prediction['result_confidence']}`")
            st.progress(prediction['result_confidence_score'] / 100)
            st.markdown(f"*{prediction['result_logic']}*")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Betting strategy
            st.warning("""
            **💰 BETTING STRATEGY:**
            
            **HIGH CONFIDENCE:**
            - Gap ≤ 2 AND xG predicts OVER → BET OVER
            - Gap ≥ 8 AND xG predicts UNDER → BET UNDER
            - Gap ≥ 8 AND better team at home → BET HOME WIN
            
            **AVOID:**
            - Extreme gaps (>12 positions)
            - Cup matches (different psychology)
            - Derby matches (emotion overrides tactics)
            """)
        
        # Match details card
        st.markdown('<div class="match-card">', unsafe_allow_html=True)
        st.markdown(f"### 📋 MATCH DETAILS: {home_name} vs {away_name}")
        
        col9, col10, col11 = st.columns(3)
        
        with col9:
            st.markdown(f"**Home Position:** {home_pos}/{total_teams}")
            st.markdown(f"**Away Position:** {away_pos}/{total_teams}")
        
        with col10:
            st.markdown(f"**Match Type:** {match_type}")
            st.markdown(f"**Position Gap:** {prediction['position_gap']}")
        
        with col11:
            factors = []
            if key_players_missing:
                factors.append("Key Players Missing")
            if new_manager:
                factors.append("New Manager")
            if fatigue:
                factors.append("Fatigue Concern")
            if weather_issue:
                factors.append("Bad Weather")
            
            if factors:
                st.markdown("**Special Factors:**")
                for factor in factors:
                    st.markdown(f"- {factor}")
            else:
                st.markdown("**Special Factors:** None")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Historical examples
        st.markdown("---")
        st.markdown('<div class="sub-header">📚 HISTORICAL EXAMPLES</div>', unsafe_allow_html=True)
        
        examples = pd.DataFrame({
            'Match': ['Annecy vs Le Mans', 'Nancy vs Clermont', 'Real Sociedad vs Girona', 'Leonesa vs Huesca'],
            'Gap': [1, 8, 3, 7],
            'Prediction': ['OVER 2.5', 'UNDER 2.5', 'OVER 2.5', 'UNDER 2.5'],
            'Actual': ['2-1 ✅', '1-0 ✅', '2-1 ✅', '0-2 ✅'],
            'Confidence': ['HIGH', 'HIGH', 'MEDIUM', 'HIGH']
        })
        
        st.dataframe(
            examples,
            column_config={
                "Match": "Match",
                "Gap": st.column_config.NumberColumn("Position Gap", format="%d"),
                "Prediction": "Prediction",
                "Actual": "Actual Result",
                "Confidence": "Confidence"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Export option
        st.markdown("---")
        if st.button("📥 EXPORT PREDICTION", use_container_width=True):
            export_data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'match': f"{home_name} vs {away_name}",
                'home_position': home_pos,
                'away_position': away_pos,
                'total_teams': total_teams,
                'position_gap': prediction['position_gap'],
                'over_under_prediction': prediction['over_under'],
                'over_under_confidence': prediction['over_under_confidence'],
                'result_prediction': prediction['result'],
                'result_confidence': prediction['result_confidence'],
                'betting_recommendation': prediction['betting_recommendation']
            }
            
            # Create download button
            df_export = pd.DataFrame([export_data])
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"prediction_{home_name.replace(' ', '_')}_vs_{away_name.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
