"""
ULTIMATE BETTING ANALYTICS DASHBOARD
Professional Data-Driven Interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

# Page config
st.set_page_config(
    page_title="Betting Analytics Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for ultimate professional styling
st.markdown("""
<style>
    /* CSS Reset and Base */
    .main {
        padding: 0 2rem;
    }
    
    /* Professional Headers */
    .dashboard-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2D3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .subsection-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #4A5568;
        margin: 1.5rem 0 0.8rem 0;
    }
    
    /* Cards - Modern Design */
    .data-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid #EDF2F7;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .data-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    
    .prediction-high {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #10B98110 0%, #05966910 100%);
    }
    
    .prediction-medium {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #F59E0B10 0%, #D9770610 100%);
    }
    
    .prediction-low {
        border-left-color: #6B7280;
        background: linear-gradient(135deg, #6B728010 0%, #4B556310 100%);
    }
    
    /* Metrics Display */
    .metric-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2D3748;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-trend-high {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
    }
    
    .badge-trend-medium {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    
    .badge-trend-low {
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%);
        color: white;
    }
    
    .badge-value {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }
    
    /* Progress Bars */
    .progress-container {
        background: #E2E8F0;
        border-radius: 10px;
        height: 8px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .progress-high { background: linear-gradient(90deg, #10B981, #059669); }
    .progress-medium { background: linear-gradient(90deg, #F59E0B, #D97706); }
    .progress-low { background: linear-gradient(90deg, #6B7280, #4B5563); }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Tables */
    .data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1rem 0;
    }
    
    .data-table th {
        background: #F7FAFC;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        color: #2D3748;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .data-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .data-table tr:hover {
        background: #F7FAFC;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #CBD5E0;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #A0AEC0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Grid Layout */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {
        'match_info': {
            'home_team': 'Roma',
            'away_team': 'Como',
            'league': 'Serie A',
            'date': datetime.now()
        },
        'home_stats': {
            'btts_pct': 30, 'over_pct': 20, 'under_pct': 70,
            'gf_avg': 1.0, 'ga_avg': 0.8,
            'is_big_club': True
        },
        'away_stats': {
            'btts_pct': 40, 'over_pct': 35, 'under_pct': 60,
            'gf_avg': 1.3, 'ga_avg': 0.9
        },
        'market_odds': {
            'btts_yes': 1.80, 'over_25': 2.20, 'under_25': 1.58
        },
        'context': {
            'big_club_home': True,
            'relegation': False,
            'title_chase': False
        }
    }

class BettingAnalyzer:
    """Professional betting analysis engine"""
    
    def __init__(self):
        self.data = st.session_state.analysis_data
        
    def calculate_expected_goals(self) -> Tuple[float, float, str]:
        """Calculate expected goals with adjustments"""
        home = self.data['home_stats']
        away = self.data['away_stats']
        context = self.data['context']
        
        # Baseline calculation
        baseline = ((home['gf_avg'] + away['ga_avg']) + (away['gf_avg'] + home['ga_avg'])) / 2
        
        # Trend adjustments
        adjustments = []
        adjusted = baseline
        
        # Home trend adjustments
        if home['under_pct'] >= 70:
            adjusted *= 0.85
            adjustments.append(f"Home Under trend: -15%")
        elif home['over_pct'] >= 70:
            adjusted *= 1.15
            adjustments.append(f"Home Over trend: +15%")
        
        # Away trend adjustments (with context)
        if away['under_pct'] >= 70:
            if context['big_club_home']:
                adjustments.append(f"Away Under trend discounted (big club home)")
            else:
                adjusted *= 0.85
                adjustments.append(f"Away Under trend: -15%")
        
        # Context adjustments
        if context['big_club_home']:
            adjusted -= 0.1
            adjustments.append("Big club at home: -0.1 goals")
        
        return baseline, adjusted, " | ".join(adjustments) if adjustments else "No adjustments"
    
    def calculate_probabilities(self, expected_goals: float) -> Dict[str, float]:
        """Calculate probabilities for different markets"""
        probs = {}
        
        # Over/Under probabilities
        if expected_goals < 2.0:
            probs['under_25'] = 0.80
            probs['over_25'] = 0.20
        elif expected_goals < 2.3:
            probs['under_25'] = 0.70
            probs['over_25'] = 0.30
        elif expected_goals < 2.7:
            probs['under_25'] = 0.55
            probs['over_25'] = 0.45
        else:
            probs['under_25'] = 0.30
            probs['over_25'] = 0.70
        
        # BTTS probability
        home_attack = self.data['home_stats']['gf_avg'] / self.data['away_stats']['ga_avg']
        away_attack = self.data['away_stats']['gf_avg'] / self.data['home_stats']['ga_avg']
        btts_raw = (home_attack * away_attack) * 0.7
        probs['btts_yes'] = max(0.05, min(0.95, btts_raw))
        
        return probs
    
    def calculate_value(self, probability: float, odds: float) -> Dict:
        """Calculate value metrics"""
        implied_prob = 1 / odds
        value = (probability * odds) - 1
        expected_value = probability * (odds - 1) - (1 - probability)
        
        # Determine value category
        if value >= 0.25:
            category = "High Value"
            color = "#10B981"
            action = "STRONG BET"
            stake_pct = 2.5
        elif value >= 0.15:
            category = "Good Value"
            color = "#3B82F6"
            action = "BET"
            stake_pct = 1.5
        elif value >= 0.05:
            category = "Low Value"
            color = "#F59E0B"
            action = "CONSIDER"
            stake_pct = 0.5
        else:
            category = "No Value"
            color = "#6B7280"
            action = "AVOID"
            stake_pct = 0.0
        
        return {
            'value': value,
            'implied_prob': implied_prob,
            'expected_value': expected_value,
            'category': category,
            'color': color,
            'action': action,
            'stake_pct': stake_pct
        }
    
    def get_confidence_level(self, probability: float, expected_goals: float) -> str:
        """Determine confidence level"""
        if probability >= 0.75 and abs(expected_goals - 2.5) > 0.5:
            return "High"
        elif probability >= 0.65:
            return "Medium"
        else:
            return "Low"
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate betting recommendations"""
        baseline, expected_goals, adjustments = self.calculate_expected_goals()
        probabilities = self.calculate_probabilities(expected_goals)
        market = self.data['market_odds']
        
        recommendations = []
        
        # Under 2.5 recommendation
        if expected_goals < 2.5:
            rec = {
                'market': 'Under 2.5 Goals',
                'probability': probabilities['under_25'],
                'expected_goals': expected_goals,
                'odds': market['under_25'],
                'type': 'Main'
            }
            value_data = self.calculate_value(rec['probability'], rec['odds'])
            rec.update(value_data)
            recommendations.append(rec)
        
        # BTTS recommendation
        if probabilities['btts_yes'] > 0.5:
            rec = {
                'market': 'Both Teams to Score',
                'probability': probabilities['btts_yes'],
                'expected_goals': expected_goals,
                'odds': market['btts_yes'],
                'type': 'Alternative'
            }
            value_data = self.calculate_value(rec['probability'], rec['odds'])
            rec.update(value_data)
            recommendations.append(rec)
        
        # Sort by value
        recommendations.sort(key=lambda x: x['value'], reverse=True)
        
        return recommendations

def create_data_input_modal():
    """Create professional data input modal"""
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;'>
        <div style='background: white; border-radius: 16px; padding: 2rem; width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto;'>
            <h2 style='margin-top: 0;'>Enter Match Data</h2>
            <!-- Form content here -->
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_team_stat_card(team_name: str, is_home: bool, stats: Dict):
    """Create professional team statistics card"""
    with st.container():
        st.markdown(f"""
        <div class='data-card'>
            <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;'>
                <div>
                    <h3 style='margin: 0 0 0.5rem 0;'>{'🏠' if is_home else '✈️'} {team_name}</h3>
                    <div style='color: #718096; font-size: 0.9rem;'>Last 10 matches analysis</div>
                </div>
                {f"<span class='badge badge-trend-high' style='margin: 0;'>Big Club</span>" if is_home and stats.get('is_big_club') else ""}
            </div>
            
            <div class='grid-container'>
                <div>
                    <div class='subsection-header'>Trend Analysis</div>
                    <div style='margin: 0.5rem 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span>BTTS</span>
                            <span style='font-weight: 600;'>{stats['btts_pct']}%</span>
                        </div>
                        <div class='progress-container'>
                            <div class='progress-bar progress-{'high' if stats['btts_pct'] >= 70 else 'medium' if stats['btts_pct'] >= 60 else 'low'}' 
                                 style='width: {stats["btts_pct"]}%'></div>
                        </div>
                    </div>
                    <div style='margin: 0.5rem 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span>Over 2.5</span>
                            <span style='font-weight: 600;'>{stats['over_pct']}%</span>
                        </div>
                        <div class='progress-container'>
                            <div class='progress-bar progress-{'high' if stats['over_pct'] >= 70 else 'medium' if stats['over_pct'] >= 60 else 'low'}' 
                                 style='width: {stats["over_pct"]}%'></div>
                        </div>
                    </div>
                    <div style='margin: 0.5rem 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span>Under 2.5</span>
                            <span style='font-weight: 600;'>{stats['under_pct']}%</span>
                        </div>
                        <div class='progress-container'>
                            <div class='progress-bar progress-{'high' if stats['under_pct'] >= 70 else 'medium' if stats['under_pct'] >= 60 else 'low'}' 
                                 style='width: {stats["under_pct"]}%'></div>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class='subsection-header'>Performance Metrics</div>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem;'>
                        <div style='text-align: center;'>
                            <div class='metric-value'>{stats['gf_avg']:.1f}</div>
                            <div class='metric-label'>Goals For</div>
                        </div>
                        <div style='text-align: center;'>
                            <div class='metric-value'>{stats['ga_avg']:.1f}</div>
                            <div class='metric-label'>Goals Against</div>
                        </div>
                        <div style='text-align: center;'>
                            <div class='metric-value'>{stats['gf_avg'] - stats['ga_avg']:+.1f}</div>
                            <div class='metric-label'>Net Rating</div>
                        </div>
                        <div style='text-align: center;'>
                            <div class='metric-value'>{(stats['gf_avg'] + stats['ga_avg'])/2:.1f}</div>
                            <div class='metric-label'>Avg Goals</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_prediction_card(recommendation: Dict):
    """Create professional prediction card"""
    card_class = "prediction-high" if recommendation['value'] >= 0.15 else "prediction-medium" if recommendation['value'] >= 0.05 else "prediction-low"
    
    st.markdown(f"""
    <div class='prediction-card {card_class}'>
        <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
            <div>
                <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
                    <h4 style='margin: 0;'>{recommendation['market']}</h4>
                    <span class='badge' style='background: {recommendation['color']};'>{recommendation['category']}</span>
                </div>
                <div style='color: #718096; font-size: 0.9rem;'>{recommendation['type']} Recommendation</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 1.5rem; font-weight: 700; color: #2D3748;'>{recommendation['probability']:.0%}</div>
                <div style='font-size: 0.9rem; color: #718096;'>Probability</div>
            </div>
        </div>
        
        <div style='background: rgba(255,255,255,0.5); padding: 1rem; border-radius: 12px; margin: 1rem 0;'>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;'>
                <div style='text-align: center;'>
                    <div style='font-size: 1.2rem; font-weight: 700; color: #2D3748;'>{recommendation['odds']:.2f}</div>
                    <div style='font-size: 0.8rem; color: #718096;'>Market Odds</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 1.2rem; font-weight: 700; color: #2D3748;'>{recommendation['value']:+.1%}</div>
                    <div style='font-size: 0.8rem; color: #718096;'>Value Edge</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 1.2rem; font-weight: 700; color: #2D3748;'>{recommendation['stake_pct']:.1f}%</div>
                    <div style='font-size: 0.8rem; color: #718096;'>Stake Size</div>
                </div>
            </div>
        </div>
        
        <div style='display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.1);'>
            <div style='font-weight: 600; color: #2D3748;'>{recommendation['action']}</div>
            <div style='display: flex; gap: 0.5rem;'>
                <span style='font-size: 0.8rem; color: #718096;'>Expected EV:</span>
                <span style='font-weight: 600; color: {recommendation['color']};'>{recommendation['expected_value']:+.3f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_expected_goals_chart(baseline: float, adjusted: float):
    """Create expected goals visualization"""
    fig = go.Figure()
    
    # Create bar chart
    fig.add_trace(go.Bar(
        x=['Baseline', 'Adjusted'],
        y=[baseline, adjusted],
        text=[f'{baseline:.2f}', f'{adjusted:.2f}'],
        textposition='auto',
        marker_color=['#CBD5E0', '#3B82F6']
    ))
    
    # Add threshold line
    fig.add_hline(y=2.5, line_dash="dash", line_color="#EF4444", 
                  annotation_text="2.5 Goal Line", 
                  annotation_position="top right")
    
    # Update layout
    fig.update_layout(
        title="Expected Goals Analysis",
        yaxis_title="Expected Goals",
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#4A5568")
    )
    
    return fig

def create_probability_chart(probabilities: Dict):
    """Create probability visualization"""
    fig = go.Figure()
    
    markets = ['Under 2.5', 'Over 2.5', 'BTTS Yes']
    probs = [probabilities['under_25'], probabilities['over_25'], probabilities['btts_yes']]
    colors = ['#10B981', '#EF4444', '#3B82F6']
    
    fig.add_trace(go.Bar(
        x=markets,
        y=probs,
        text=[f'{p:.0%}' for p in probs],
        textposition='auto',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Market Probabilities",
        yaxis_title="Probability",
        yaxis_tickformat='.0%',
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#4A5568")
    )
    
    return fig

def main():
    """Main dashboard application"""
    
    # Dashboard Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="dashboard-header">BETTING ANALYTICS PRO</h1>', unsafe_allow_html=True)
        st.markdown('<div style="color: #718096; margin-bottom: 2rem;">Professional Football Match Analysis Dashboard</div>', unsafe_allow_html=True)
    with col2:
        if st.button("📊 New Analysis", use_container_width=True):
            # In a real app, this would trigger the data input modal
            st.info("Data input modal would open here")
    
    # Initialize analyzer
    analyzer = BettingAnalyzer()
    
    # Match Header
    st.markdown("""
    <div class='data-card'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h2 style='margin: 0;'>{home} vs {away}</h2>
                <div style='color: #718096;'>Serie A • Today • 20:45 CET</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 0.9rem; color: #718096;'>Match ID</div>
                <div style='font-weight: 600;'>#MAT20231216-001</div>
            </div>
        </div>
    </div>
    """.format(
        home=analyzer.data['match_info']['home_team'],
        away=analyzer.data['match_info']['away_team']
    ), unsafe_allow_html=True)
    
    # Team Analysis Section
    st.markdown('<div class="section-header">Team Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_team_stat_card(
            analyzer.data['match_info']['home_team'],
            True,
            analyzer.data['home_stats']
        )
    
    with col2:
        create_team_stat_card(
            analyzer.data['match_info']['away_team'],
            False,
            analyzer.data['away_stats']
        )
    
    # Analytical Insights
    st.markdown('<div class="section-header">Analytical Insights</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    baseline, expected_goals, adjustments = analyzer.calculate_expected_goals()
    probabilities = analyzer.calculate_probabilities(expected_goals)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='data-card'>
            <div class='subsection-header'>Expected Goals Model</div>
            <div style='margin: 1rem 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Baseline Calculation</span>
                    <span style='font-weight: 600;'>{baseline:.2f}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Trend Adjustments</span>
                    <span style='font-weight: 600; color: #3B82F6;'>{adjustment_text}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Final Expected Goals</span>
                    <span style='font-size: 1.2rem; font-weight: 700; color: #2D3748;'>{expected_goals:.2f}</span>
                </div>
            </div>
            <div style='background: #F7FAFC; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                <div style='font-size: 0.9rem; color: #4A5568;'>
                    <strong>Interpretation:</strong> {interpretation}
                </div>
            </div>
        </div>
        """.format(
            baseline=baseline,
            expected_goals=expected_goals,
            adjustment_text="Applied" if adjustments != "No adjustments" else "None",
            interpretation="Low-scoring match expected" if expected_goals < 2.3 else 
                          "Moderate scoring expected" if expected_goals < 2.7 else 
                          "High-scoring match expected"
        ), unsafe_allow_html=True)
        
        # Visualization
        fig1 = create_expected_goals_chart(baseline, expected_goals)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class='data-card'>
            <div class='subsection-header'>Probability Distribution</div>
            <div style='margin: 1rem 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Under 2.5 Goals</span>
                    <span style='font-weight: 600; color: #10B981;'>{under_prob:.0%}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Over 2.5 Goals</span>
                    <span style='font-weight: 600; color: #EF4444;'>{over_prob:.0%}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Both Teams to Score</span>
                    <span style='font-weight: 600; color: #3B82F6;'>{btts_prob:.0%}</span>
                </div>
            </div>
            <div style='background: #F7FAFC; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                <div style='font-size: 0.9rem; color: #4A5568;'>
                    <strong>Key Insight:</strong> {insight}
                </div>
            </div>
        </div>
        """.format(
            under_prob=probabilities['under_25'],
            over_prob=probabilities['over_25'],
            btts_prob=probabilities['btts_yes'],
            insight="Defensive focus expected" if probabilities['under_25'] > 0.7 else
                    "Balanced match expected" if probabilities['under_25'] > 0.45 else
                    "Attacking match expected"
        ), unsafe_allow_html=True)
        
        # Visualization
        fig2 = create_probability_chart(probabilities)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Betting Recommendations
    st.markdown('<div class="section-header">Betting Recommendations</div>', unsafe_allow_html=True)
    
    recommendations = analyzer.generate_recommendations()
    
    for rec in recommendations:
        create_prediction_card(rec)
    
    # Market Odds Comparison
    st.markdown('<div class="section-header">Market Odds Analysis</div>', unsafe_allow_html=True)
    
    market_data = analyzer.data['market_odds']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='data-card' style='text-align: center;'>
            <div style='font-size: 0.9rem; color: #718096; margin-bottom: 0.5rem;'>BTTS Yes</div>
            <div style='font-size: 2rem; font-weight: 700; color: #3B82F6;'>{market_data['btts_yes']:.2f}</div>
            <div style='font-size: 0.8rem; color: #718096; margin-top: 0.5rem;'>
                Implied: {(1/market_data['btts_yes']*100):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='data-card' style='text-align: center;'>
            <div style='font-size: 0.9rem; color: #718096; margin-bottom: 0.5rem;'>Over 2.5</div>
            <div style='font-size: 2rem; font-weight: 700; color: #EF4444;'>{market_data['over_25']:.2f}</div>
            <div style='font-size: 0.8rem; color: #718096; margin-top: 0.5rem;'>
                Implied: {(1/market_data['over_25']*100):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='data-card' style='text-align: center;'>
            <div style='font-size: 0.9rem; color: #718096; margin-bottom: 0.5rem;'>Under 2.5</div>
            <div style='font-size: 2rem; font-weight: 700; color: #10B981;'>{market_data['under_25']:.2f}</div>
            <div style='font-size: 0.8rem; color: #718096; margin-top: 0.5rem;'>
                Implied: {(1/market_data['under_25']*100):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk Assessment
    st.markdown('<div class="section-header">Risk Assessment</div>', unsafe_allow_html=True)
    
    if recommendations:
        best_rec = recommendations[0]
        
        st.markdown(f"""
        <div class='data-card'>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;'>
                <div>
                    <div class='subsection-header'>Risk Level</div>
                    <div style='margin: 1rem 0;'>
                        <div class='progress-container'>
                            <div class='progress-bar progress-{'low' if best_rec['probability'] >= 0.7 else 'medium' if best_rec['probability'] >= 0.6 else 'high'}' 
                                 style='width: {best_rec['probability']*100}%'></div>
                        </div>
                        <div style='text-align: center; margin-top: 0.5rem; font-size: 0.9rem; color: #718096;'>
                            {best_rec['probability']:.0%} Probability
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class='subsection-header'>Expected Value</div>
                    <div style='text-align: center; margin: 1rem 0;'>
                        <div style='font-size: 2rem; font-weight: 700; color: {best_rec['color']};'>
                            {best_rec['expected_value']:+.3f}
                        </div>
                        <div style='font-size: 0.9rem; color: #718096;'>per unit bet</div>
                    </div>
                </div>
                
                <div>
                    <div class='subsection-header'>Recommended Stake</div>
                    <div style='text-align: center; margin: 1rem 0;'>
                        <div style='font-size: 2rem; font-weight: 700; color: #2D3748;'>
                            {best_rec['stake_pct']:.1f}%
                        </div>
                        <div style='font-size: 0.9rem; color: #718096;'>of bankroll</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style='margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #E2E8F0; text-align: center; color: #718096; font-size: 0.9rem;'>
        <div>Betting Analytics Pro • Version 2.0 • Professional Use Only</div>
        <div style='margin-top: 0.5rem;'>Always bet responsibly • Past performance does not guarantee future results</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
