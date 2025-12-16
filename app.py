"""
COMPLETE BETTING SYSTEM - CLEAN DISPLAY WITH EXPLANATIONS
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Complete Betting System",
    page_icon="🎯",
    layout="wide"
)

# CSS for professional styling - FIXED FOR MOBILE VISIBILITY
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .header {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .prediction-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        border-left: 5px solid;
        margin-bottom: 1rem;
    }
    .prediction-high {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border: 1px solid #10B98120;
    }
    .prediction-medium {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #F59E0B20;
    }
    .secondary-card {
        border-left-color: #3B82F6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #3B82F620;
    }
    .no-value-card {
        border-left-color: #6B7280;
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        border: 1px solid #6B728020;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .card, .prediction-card {
            padding: 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h2 {
            font-size: 1.4rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
        .header {
            font-size: 1.6rem !important;
        }
    }
    
    /* Ensure text is always visible */
    .prediction-card h3 {
        color: #1F2937 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .prediction-card div {
        color: #4B5563 !important;
    }
    .card h4 {
        color: #1F2937 !important;
        margin: 0 0 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# ============================================================================
# ENHANCED PREDICTION LOGIC
# ============================================================================

def check_aligned_strong_trends(home_btts, home_over, home_under, away_btts, away_over, away_under):
    """TIER 1: ALIGNED STRONG TRENDS (≥70%)"""
    aligned_trends = []
    
    # Check for BTTS aligned trend
    if home_btts >= 70 and away_btts >= 70:
        aligned_trends.append({
            'type': 'BTTS Yes',
            'probability': 0.75,
            'reason': f"Both teams show ≥70% BTTS trend (Home: {home_btts}%, Away: {away_btts}%)"
        })
    
    # Check for Over aligned trend
    if home_over >= 70 and away_over >= 70:
        aligned_trends.append({
            'type': 'Over 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Over trend (Home: {home_over}%, Away: {away_over}%)"
        })
    
    # Check for Under aligned trend
    if home_under >= 70 and away_under >= 70:
        aligned_trends.append({
            'type': 'Under 2.5',
            'probability': 0.70,
            'reason': f"Both teams show ≥70% Under trend (Home: {home_under}%, Away: {away_under}%)"
        })
    
    return aligned_trends

def calculate_expected_goals(home_gf, away_ga, away_gf, home_ga, aligned_trends=None):
    """Calculate expected goals with trend adjustments"""
    baseline = ((home_gf + away_ga) + (away_gf + home_ga)) / 2
    
    # Apply adjustments for aligned trends
    if aligned_trends:
        for trend in aligned_trends:
            if trend['type'] == 'Over 2.5':
                baseline *= 1.30  # +30% for aligned Over trends
            elif trend['type'] == 'Under 2.5':
                baseline *= 0.70  # -30% for aligned Under trends
    
    return baseline

def get_best_secondary_option(primary_bet, expected_goals, home_gf, away_gf, home_ga, away_ga):
    """Get ONE strong secondary option based on primary bet and stats"""
    
    # RULE 1: If primary is BTTS, secondary is based on expected goals
    if primary_bet == 'BTTS Yes':
        if expected_goals > 2.8:
            return {
                'bet': 'Over 2.5',
                'probability': 0.65,
                'reason': f"BTTS + High expected goals ({expected_goals:.1f}) suggests Over",
                'logic': "High scoring teams that both score often tend to produce Over 2.5 results"
            }
        elif expected_goals < 2.2:
            return {
                'bet': 'Under 2.5',
                'probability': 0.60,
                'reason': f"BTTS likely but low total goals expected ({expected_goals:.1f})",
                'logic': "While both may score, limited offensive power suggests low total goals"
            }
        else:
            # Moderate expected goals
            return {
                'bet': 'Draw',
                'probability': 0.52,
                'reason': f"BTTS + balanced match ({expected_goals:.1f} expected goals)",
                'logic': "Close matches where both teams score often end level"
            }
    
    # RULE 2: If primary is Over 2.5
    elif primary_bet == 'Over 2.5':
        if home_gf > 1.8 or away_gf > 1.8:
            return {
                'bet': 'BTTS Yes',
                'probability': 0.68,
                'reason': f"High scoring teams (Home: {home_gf:.1f}, Away: {away_gf:.1f} GF/game)",
                'logic': "High-scoring matches often feature goals from both sides"
            }
        else:
            return {
                'bet': 'Home Win',
                'probability': 0.55,
                'reason': f"Home advantage in attacking stats",
                'logic': "When Over is expected, the stronger home team often wins"
            }
    
    # RULE 3: If primary is Under 2.5
    elif primary_bet == 'Under 2.5':
        if home_ga < 1.0 and away_ga < 1.0:
            return {
                'bet': 'BTTS No',
                'probability': 0.70,
                'reason': f"Strong defenses (Home: {home_ga:.1f}, Away: {away_ga:.1f} GA/game)",
                'logic': "Teams with strong defenses often prevent opposition from scoring"
            }
        else:
            return {
                'bet': '1-0 or 2-0',
                'probability': 0.48,
                'reason': f"Low scoring match ({expected_goals:.1f} expected goals)",
                'logic': "Low scoring matches typically end with narrow scorelines"
            }
    
    return None

def calculate_value_and_action(probability, odds):
    """Calculate value and determine action"""
    if probability == 0 or odds == 0:
        return {'value': -1, 'action': 'NO BET', 'reason': 'Insufficient data'}
    
    value = (probability * odds) - 1
    
    if value >= 0.25:
        return {'value': value, 'action': 'STRONG BET', 'stake': 3.0, 
                'reason': f"Excellent value (+{value:.1%} edge over market)"}
    elif value >= 0.15:
        return {'value': value, 'action': 'BET', 'stake': 2.0,
                'reason': f"Good value (+{value:.1%} edge)"}
    elif value >= 0.05:
        return {'value': value, 'action': 'CONSIDER', 'stake': 1.0,
                'reason': f"Limited value (+{value:.1%} edge)"}
    elif value >= 0:
        return {'value': value, 'action': 'SMALL BET', 'stake': 0.5,
                'reason': f"Marginal value (+{value:.1%} edge)"}
    else:
        return {'value': value, 'action': 'AVOID', 'stake': 0.0,
                'reason': f"No value ({value:.1%} edge)"}

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    st.markdown('<div class="header">🎯 CLEAN BETTING SYSTEM</div>', unsafe_allow_html=True)
    st.markdown("**Primary prediction + ONE secondary option with clear explanations**")
    
    # Sidebar for data input
    with st.sidebar:
        st.header("📊 Match Data Input")
        
        st.subheader("🏠 Home Team")
        home_team = st.text_input("Team Name", "Fenerbahce")
        
        col1, col2 = st.columns(2)
        with col1:
            home_btts = st.slider("BTTS % (Last 10)", 0, 100, 70)
            home_over = st.slider("Over 2.5 %", 0, 100, 50)
        with col2:
            home_gf = st.number_input("GF/game", 0.0, 5.0, 1.90, 0.01)
            home_ga = st.number_input("GA/game", 0.0, 5.0, 0.90, 0.01)
        
        st.subheader("✈️ Away Team")
        away_team = st.text_input("Team Name ", "Konyaspor")
        
        col1, col2 = st.columns(2)
        with col1:
            away_btts = st.slider("BTTS % (Last 10) ", 0, 100, 80)
            away_over = st.slider("Over 2.5 % ", 0, 100, 60)
        with col2:
            away_gf = st.number_input("GF/game ", 0.0, 5.0, 1.40, 0.01)
            away_ga = st.number_input("GA/game ", 0.0, 5.0, 1.70, 0.01)
        
        st.subheader("💰 Market Odds")
        col1, col2, col3 = st.columns(3)
        with col1:
            odds_btts = st.number_input("BTTS Yes", 1.01, 10.0, 2.02, 0.01)
        with col2:
            odds_over = st.number_input("Over 2.5", 1.01, 10.0, 1.46, 0.01)
        with col3:
            odds_under = st.number_input("Under 2.5", 1.01, 10.0, 2.48, 0.01)
        
        if st.button("🎯 Analyze Match", type="primary", use_container_width=True):
            st.session_state.match_data = {
                'home_team': home_team,
                'away_team': away_team,
                'home_btts': home_btts,
                'home_over': home_over,
                'home_under': 100 - home_over,
                'home_gf': home_gf,
                'home_ga': home_ga,
                'away_btts': away_btts,
                'away_over': away_over,
                'away_under': 100 - away_over,
                'away_gf': away_gf,
                'away_ga': away_ga,
                'odds': {
                    'btts': odds_btts,
                    'over': odds_over,
                    'under': odds_under
                }
            }
            st.rerun()
    
    # Check if we have data to analyze
    if not st.session_state.match_data:
        st.info("👈 Enter match data in the sidebar and click 'Analyze Match'")
        return
    
    data = st.session_state.match_data
    
    # Match header with better contrast
    st.markdown(f"""
    <div class="card">
        <div style="text-align: center;">
            <h2 style="margin: 0; color: #1F2937;">🏠 {data['home_team']} vs ✈️ {data['away_team']}</h2>
            <div style="color: #6B7280; margin-top: 0.5rem;">Clean Betting Analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for aligned trends
    aligned_trends = check_aligned_strong_trends(
        data['home_btts'], data['home_over'], data['home_under'],
        data['away_btts'], data['away_over'], data['away_under']
    )
    
    # Calculate expected goals
    expected_goals = calculate_expected_goals(
        data['home_gf'], data['away_ga'], data['away_gf'], data['home_ga'],
        aligned_trends
    )
    
    # Display primary prediction
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">🎯 PRIMARY BET</div>', unsafe_allow_html=True)
    
    if aligned_trends:
        primary_trend = aligned_trends[0]
        
        # Get odds for this bet
        if primary_trend['type'] == 'Over 2.5':
            odds = data['odds']['over']
        elif primary_trend['type'] == 'Under 2.5':
            odds = data['odds']['under']
        else:  # BTTS Yes
            odds = data['odds']['btts']
        
        value_data = calculate_value_and_action(primary_trend['probability'], odds)
        
        # Show primary bet with explanation
        card_class = "prediction-high" if value_data['action'] in ['STRONG BET', 'BET'] else "prediction-medium"
        
        st.markdown(f"""
        <div class="prediction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #1F2937;">{primary_trend['type']}</h3>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Why this bet:</strong> {primary_trend['reason']}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Probability:</strong> {primary_trend['probability']:.0%}
                    </div>
                    <div style="color: #4B5563; margin-bottom: 0.5rem;">
                        <strong style="color: #374151;">Market Odds:</strong> {odds:.2f}
                    </div>
                    <div style="color: #4B5563;">
                        <strong style="color: #374151;">Decision:</strong> {value_data['action']} - {value_data['reason']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        primary_bet = primary_trend['type']
    else:
        st.warning("⚠️ No aligned strong trends detected")
        primary_bet = None
    
    # Get secondary option
    if primary_bet:
        st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">🔄 SECONDARY OPTION</div>', unsafe_allow_html=True)
        
        secondary = get_best_secondary_option(
            primary_bet, expected_goals,
            data['home_gf'], data['away_gf'],
            data['home_ga'], data['away_ga']
        )
        
        if secondary:
            # Determine odds for secondary bet
            if secondary['bet'] == 'BTTS Yes':
                sec_odds = data['odds']['btts']
            elif secondary['bet'] == 'Over 2.5':
                sec_odds = data['odds']['over']
            elif secondary['bet'] == 'Under 2.5':
                sec_odds = data['odds']['under']
            else:
                sec_odds = 2.50  # Default for other markets
            
            sec_value = calculate_value_and_action(secondary['probability'], sec_odds)
            
            # Show secondary with explanation
            sec_card_class = "secondary-card" if sec_value['action'] not in ['AVOID', 'NO BET'] else "no-value-card"
            
            st.markdown(f"""
            <div class="prediction-card {sec_card_class}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h3 style="margin: 0 0 0.5rem 0; color: #1F2937;">{secondary['bet']}</h3>
                        <div style="color: #4B5563; margin-bottom: 0.5rem;">
                            <strong style="color: #374151;">Why this bet:</strong> {secondary['reason']}
                        </div>
                        <div style="color: #4B5563; margin-bottom: 0.5rem;">
                            <strong style="color: #374151;">Logic:</strong> {secondary['logic']}
                        </div>
                        <div style="color: #4B5563; margin-bottom: 0.5rem;">
                            <strong style="color: #374151;">Probability:</strong> {secondary['probability']:.0%}
                        </div>
                        <div style="color: #4B5563;">
                            <strong style="color: #374151;">Decision:</strong> {sec_value['action']} - {sec_value['reason']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No suitable secondary option for this match configuration")
    
    # Match Analysis
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #1F2937;">📊 MATCH ANALYSIS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        interpretation = "High-scoring match expected" if expected_goals > 2.7 else "Moderate scoring expected" if expected_goals > 2.3 else "Low-scoring match expected"
        
        st.markdown(f"""
        <div class="card">
            <h4 style="color: #1F2937;">⚽ Expected Goals Analysis</h4>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Calculation:</strong><br>
                (Home GF + Away GA) + (Away GF + Home GA) ÷ 2
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1F2937; margin: 1rem 0;">
                {expected_goals:.2f} expected goals
            </div>
            <div style="color: #4B5563;">
                <strong style="color: #374151;">Interpretation:</strong> {interpretation}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate trend strength
        trend_strength = 0
        trend_explanation = []
        
        if data['home_btts'] >= 70 and data['away_btts'] >= 70:
            trend_strength += 1
            trend_explanation.append("BTTS aligned trend")
        
        if data['home_over'] >= 70 and data['away_over'] >= 70:
            trend_strength += 1
            trend_explanation.append("Over aligned trend")
        
        if data['home_under'] >= 70 and data['away_under'] >= 70:
            trend_strength += 1
            trend_explanation.append("Under aligned trend")
        
        strength_text = "Strong trends" if trend_strength >= 2 else "One trend" if trend_strength == 1 else "No strong trends"
        trends_list = ', '.join(trend_explanation) if trend_explanation else 'No aligned trends'
        
        st.markdown(f"""
        <div class="card">
            <h4 style="color: #1F2937;">📈 Trend Analysis</h4>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Home Trends:</strong><br>
                • BTTS: {data['home_btts']}%<br>
                • Over 2.5: {data['home_over']}%
            </div>
            <div style="color: #4B5563; margin: 0.5rem 0;">
                <strong style="color: #374151;">Away Trends:</strong><br>
                • BTTS: {data['away_btts']}%<br>
                • Over 2.5: {data['away_over']}%
            </div>
            <div style="color: #4B5563; margin-top: 1rem;">
                <strong style="color: #374151;">Result:</strong> {strength_text}<br>
                {trends_list}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Betting Strategy
    with st.expander("🎯 BETTING STRATEGY EXPLAINED", expanded=True):
        if primary_bet and aligned_trends:
            primary_trend = aligned_trends[0]
            
            # Prepare secondary info
            if secondary:
                secondary_bet = secondary['bet']
                secondary_prob = f"{secondary['probability']:.0%}"
                sec_stake = sec_value['stake'] if 'sec_value' in locals() else 0.0
            else:
                secondary_bet = 'None'
                secondary_prob = 'N/A'
                sec_stake = 0.0
            
            st.markdown(f"""
            ### Recommended Approach
            
            **Primary Bet: {primary_bet}**
            - Based on aligned trends from both teams
            - Historical data shows consistent pattern
            - Probability: {primary_trend['probability']:.0%}
            
            **Secondary Option: {secondary_bet}**
            - Complementary to primary bet
            - Based on expected goals and team statistics
            - Probability: {secondary_prob}
            
            **Bankroll Management:**
            - Primary bet: {value_data['stake']:.1f}% of bankroll
            - Secondary bet: {sec_stake:.1f}% of bankroll
            - Total exposure: {(value_data['stake'] + sec_stake):.1f}%
            
            **Key Insight:**
            {primary_trend['reason']}
            """)
        else:
            st.markdown("""
            ### No Strong Bet Identified
            
            **Why:**
            - No aligned trends from both teams
            - Inconsistent patterns in historical data
            - Market odds don't offer value
            
            **Recommendation:**
            - Avoid betting on this match
            - Look for matches with clearer patterns
            - Consider other betting markets if you must bet
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <div><strong>🎯 CLEAN SYSTEM:</strong> Optimized for mobile visibility</div>
        <div style="margin-top: 0.5rem;">Clear contrast on all devices</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
