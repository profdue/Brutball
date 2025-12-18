import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="⚡ Narrative Intelligence Engine",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .narrative-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid;
    }
    .siege { border-color: #EF4444; }
    .blitzkrieg { border-color: #F59E0B; }
    .edge-chaos { border-color: #10B981; }
    .controlled-edge { border-color: #3B82F6; }
    .shootout { border-color: #8B5CF6; }
    .chess-match { border-color: #6B7280; }
    
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        margin: 2px;
    }
    .tier-1 { background-color: #10B981; color: white; }
    .tier-2 { background-color: #F59E0B; color: white; }
    .tier-3 { background-color: #EF4444; color: white; }
    .tier-4 { background-color: #6B7280; color: white; }
    
    .recommendation {
        background: #F8FAFC;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

class NarrativeIntelligenceEngine:
    """Pure Logic Narrative Engine"""
    
    def __init__(self):
        # Narrative definitions
        self.narrative_rules = {
            'SIEGE': {
                'description': 'Dominant possession team vs defensive bus. Low scoring, methodical breakthrough.',
                'markets': ['Under 2.5 goals', 'BTTS: No', 'Favorite win to nil', 'Few corners total'],
                'color': 'siege'
            },
            'BLITZKRIEG': {
                'description': 'Early onslaught expected. High press overwhelming weak defense.',
                'markets': ['Favorite -1.5 Asian', 'First goal before 25:00', 'Over 1.5 first half goals'],
                'color': 'blitzkrieg'
            },
            'EDGE-CHAOS': {
                'description': 'Style clash creating transitions. Tight but explosive with late drama.',
                'markets': ['Over 2.25 goals Asian', 'BTTS: Yes', 'Late goal after 70:00', 'Lead change'],
                'color': 'edge-chaos'
            },
            'CONTROLLED_EDGE': {
                'description': 'Methodical favorite vs organized underdog. Grinding, low-event match.',
                'markets': ['Under 2.5 goals', 'Favorite win by 1 goal', 'First goal 30-60 mins'],
                'color': 'controlled-edge'
            },
            'SHOOTOUT': {
                'description': 'End-to-end chaos. Weak defenses, attacking mentality from both teams.',
                'markets': ['Over 2.5 goals', 'BTTS: Yes', 'Both teams 2+ shots on target'],
                'color': 'shootout'
            },
            'CHESS_MATCH': {
                'description': 'Tactical stalemate. Low event, set-piece focused, high draw probability.',
                'markets': ['Under 2.0 goals', 'Draw', '0-0 or 1-1 correct score'],
                'color': 'chess-match'
            }
        }
        
    def analyze_match(self, row):
        """Analyze a single match and determine its narrative"""
        # Convert row to dict for easier access
        data = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
        
        # Calculate scores for each narrative
        scores = {}
        
        # SIEGE scoring
        siege_score = 0
        if data.get('home_manager_style') == 'Possession-based & control' and data.get('away_manager_style') == 'Pragmatic/Defensive':
            siege_score += 30
        if data.get('home_odds', 2.0) < 1.5:
            siege_score += 20
        if data.get('home_attack_rating', 5) - data.get('away_defense_rating', 5) > 2:
            siege_score += 20
        if isinstance(data.get('home_form'), str) and 'W' in data['home_form']:
            siege_score += 15
        if isinstance(data.get('away_form'), str) and 'L' in data['away_form']:
            siege_score += 15
        scores['SIEGE'] = min(100, siege_score)
        
        # BLITZKRIEG scoring
        blitzkrieg_score = 0
        if data.get('home_manager_style') == 'High press & transition':
            blitzkrieg_score += 25
        if data.get('away_defense_rating', 5) < 6:
            blitzkrieg_score += 20
        if isinstance(data.get('home_form'), str) and data['home_form'][:2] == 'WW':
            blitzkrieg_score += 20
        if isinstance(data.get('away_form'), str) and 'L' in data['away_form']:
            blitzkrieg_score += 15
        if data.get('home_press_rating', 5) - data.get('away_defense_rating', 5) > 3:
            blitzkrieg_score += 20
        scores['BLITZKRIEG'] = min(100, blitzkrieg_score)
        
        # EDGE-CHAOS scoring
        edge_chaos_score = 0
        home_style = data.get('home_manager_style', '')
        away_style = data.get('away_manager_style', '')
        
        if (home_style == 'High press & transition' and away_style == 'Possession-based & control') or \
           (away_style == 'High press & transition' and home_style == 'Possession-based & control'):
            edge_chaos_score += 30
        
        try:
            if data.get('last_h2h_goals', 0) > 3:
                edge_chaos_score += 25
        except:
            pass
            
        if data.get('last_h2h_btts') == 'Yes':
            edge_chaos_score += 20
            
        if abs(data.get('home_attack_rating', 5) - data.get('away_attack_rating', 5)) < 2:
            edge_chaos_score += 15
            
        if data.get('home_attack_rating', 5) > 7 and data.get('away_attack_rating', 5) > 7:
            edge_chaos_score += 10
            
        scores['EDGE-CHAOS'] = min(100, edge_chaos_score)
        
        # CONTROLLED_EDGE scoring
        controlled_score = 0
        if 'Possession' in str(home_style) or 'Balanced' in str(home_style):
            if away_style == 'Pragmatic/Defensive':
                controlled_score += 30
                
        if data.get('home_odds', 2.0) < 2.0:
            controlled_score += 20
            
        if data.get('home_attack_rating', 5) > data.get('away_attack_rating', 5):
            controlled_score += 20
            
        if isinstance(data.get('home_form'), str) and ('W' in data['home_form'] or 'D' in data['home_form']):
            controlled_score += 15
            
        if isinstance(data.get('home_form'), str) and 'LLL' not in data['home_form']:
            controlled_score += 15
            
        scores['CONTROLLED_EDGE'] = min(100, controlled_score)
        
        # SHOOTOUT scoring
        shootout_score = 0
        if data.get('home_defense_rating', 5) < 6 and data.get('away_defense_rating', 5) < 6:
            shootout_score += 25
            
        if data.get('home_attack_rating', 5) > 7 and data.get('away_attack_rating', 5) > 7:
            shootout_score += 25
            
        try:
            if data.get('last_h2h_goals', 0) > 4:
                shootout_score += 25
        except:
            pass
            
        if isinstance(data.get('home_form'), str) and 'W' in data['home_form']:
            if isinstance(data.get('away_form'), str) and 'W' in data['away_form']:
                shootout_score += 25
                
        scores['SHOOTOUT'] = min(100, shootout_score)
        
        # CHESS_MATCH scoring
        chess_score = 0
        if home_style == 'Pragmatic/Defensive' and away_style == 'Pragmatic/Defensive':
            chess_score += 40
            
        if data.get('home_pragmatic_rating', 5) > 7 and data.get('away_pragmatic_rating', 5) > 7:
            chess_score += 30
            
        try:
            if data.get('last_h2h_goals', 0) < 2:
                chess_score += 15
        except:
            pass
            
        if data.get('last_h2h_btts') == 'No':
            chess_score += 15
            
        scores['CHESS_MATCH'] = min(100, chess_score)
        
        # Determine primary narrative
        primary_narrative = max(scores, key=scores.get)
        confidence = scores[primary_narrative]
        
        # Determine tier based on confidence
        if confidence >= 70:
            tier = 'TIER 1 (STRONG)'
            units = '2-3 units'
        elif confidence >= 50:
            tier = 'TIER 2 (MEDIUM)'
            units = '1-2 units'
        elif confidence >= 30:
            tier = 'TIER 3 (WEAK)'
            units = '0.5-1 unit'
        else:
            tier = 'TIER 4 (AVOID)'
            units = 'No bet'
        
        # Calculate probabilities
        probs = self._calculate_probabilities(data, primary_narrative)
        
        return {
            'narrative': primary_narrative,
            'confidence': confidence,
            'tier': tier,
            'units': units,
            'description': self.narrative_rules[primary_narrative]['description'],
            'markets': self.narrative_rules[primary_narrative]['markets'],
            'color': self.narrative_rules[primary_narrative]['color'],
            'probabilities': probs,
            'scores': scores,
            'match_data': data
        }
    
    def _calculate_probabilities(self, data, narrative):
        """Calculate narrative-specific probabilities"""
        # Get ratings with defaults
        home_attack = float(data.get('home_attack_rating', 5)) / 10
        away_attack = float(data.get('away_attack_rating', 5)) / 10
        home_defense = float(data.get('home_defense_rating', 5)) / 10
        away_defense = float(data.get('away_defense_rating', 5)) / 10
        
        # Get form scores
        home_form = self._form_score(data.get('home_form', ''))
        away_form = self._form_score(data.get('away_form', ''))
        
        # Base adjustments based on narrative
        if narrative == 'SIEGE':
            base_home_win = 0.6 + (home_attack - away_defense) * 0.2
            base_draw = 0.25
            total_goals = 2.0 + (home_attack - 0.5) * 0.5
            btts_prob = 0.3
            
        elif narrative == 'BLITZKRIEG':
            press_diff = (float(data.get('home_press_rating', 5)) - float(data.get('away_defense_rating', 5))) / 20
            base_home_win = 0.7 + press_diff
            base_draw = 0.15
            total_goals = 3.0 + home_attack * 0.5
            btts_prob = 0.4
            
        elif narrative == 'EDGE-CHAOS':
            base_home_win = 0.4 + (home_attack - away_attack) * 0.1
            base_draw = 0.3
            total_goals = 3.5
            btts_prob = 0.7
            
        elif narrative == 'CONTROLLED_EDGE':
            base_home_win = 0.55 + (home_attack - away_attack) * 0.15
            base_draw = 0.3
            total_goals = 2.2
            btts_prob = 0.35
            
        elif narrative == 'SHOOTOUT':
            base_home_win = 0.45 + (home_attack - away_attack) * 0.1
            base_draw = 0.2
            total_goals = 3.8
            btts_prob = 0.8
            
        elif narrative == 'CHESS_MATCH':
            base_home_win = 0.35
            base_draw = 0.4
            total_goals = 1.8
            btts_prob = 0.25
            
        else:
            # Balanced battle (default)
            base_home_win = 0.4 + (home_attack - away_attack) * 0.1
            base_draw = 0.3
            total_goals = 2.5
            btts_prob = 0.5
        
        # Adjust based on form
        form_diff = (home_form - away_form) * 0.1
        home_win_prob = base_home_win + form_diff
        draw_prob = base_draw - abs(form_diff) * 0.1
        total_goals += (home_form + away_form - 1) * 0.3
        btts_prob += (home_form + away_form - 1) * 0.1
        
        # Adjust based on odds
        try:
            home_odds = float(data.get('home_odds', 2.0))
            if home_odds < 1.5:
                home_win_prob += 0.1
                total_goals -= 0.3
        except:
            pass
        
        # Normalize probabilities
        home_win_prob = max(0.15, min(0.85, home_win_prob))
        draw_prob = max(0.1, min(0.4, draw_prob))
        away_win_prob = 1 - home_win_prob - draw_prob
        away_win_prob = max(0.1, min(0.85, away_win_prob))
        
        # Re-normalize if needed
        total = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total
        draw_prob /= total
        away_win_prob /= total
        
        # Final adjustments
        total_goals = max(1.0, min(5.0, total_goals))
        btts_prob = max(0.1, min(0.9, btts_prob))
        
        return {
            'home_win': home_win_prob * 100,
            'draw': draw_prob * 100,
            'away_win': away_win_prob * 100,
            'total_goals': total_goals,
            'btts': btts_prob * 100,
            'over_25': 70 if total_goals > 2.5 else 30,
            'under_25': 70 if total_goals < 2.5 else 30
        }
    
    def _form_score(self, form_str):
        """Convert form string to numeric score"""
        if not isinstance(form_str, str):
            return 0.5
        
        points = {'W': 1.0, 'D': 0.5, 'L': 0.0}
        total = 0
        count = 0
        
        for result in form_str[-5:]:
            if result in points:
                total += points[result]
                count += 1
        
        return total / max(count, 1)
    
    def analyze_all_matches(self, df):
        """Analyze all matches in dataframe"""
        results = []
        
        for idx, row in df.iterrows():
            analysis = self.analyze_match(row)
            results.append({
                'Match': f"{row['home_team']} vs {row['away_team']}",
                'Date': row['date'] if 'date' in row else 'Unknown',
                'Narrative': analysis['narrative'],
                'Confidence': f"{analysis['confidence']:.1f}%",
                'Tier': analysis['tier'],
                'Units': analysis['units'],
                'Home Win %': f"{analysis['probabilities']['home_win']:.1f}",
                'Draw %': f"{analysis['probabilities']['draw']:.1f}",
                'Away Win %': f"{analysis['probabilities']['away_win']:.1f}",
                'Expected Goals': f"{analysis['probabilities']['total_goals']:.2f}",
                'BTTS %': f"{analysis['probabilities']['btts']:.1f}",
                'Over 2.5 %': f"{analysis['probabilities']['over_25']:.1f}"
            })
        
        return pd.DataFrame(results)

def main():
    st.markdown('<div class="main-header">⚡ NARRATIVE INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #4B5563;">Pure Logic • Team Names in Markets • Actionable Insights</p>', unsafe_allow_html=True)
    
    # Initialize engine
    if 'engine' not in st.session_state:
        st.session_state.engine = NarrativeIntelligenceEngine()
    
    engine = st.session_state.engine
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Data Input")
        
        uploaded_file = st.file_uploader("Upload Match CSV", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} matches")
                
                # Data preview
                with st.expander("📋 Preview Data"):
                    st.dataframe(df.head())
                
                # Store in session state
                st.session_state.df = df
                
                # League selection
                if 'league' in df.columns:
                    league = st.selectbox("Select League", df['league'].unique())
                    df_filtered = df[df['league'] == league].copy()
                    st.session_state.df_filtered = df_filtered
                else:
                    st.session_state.df_filtered = df.copy()
                    
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.session_state.df = None
                st.session_state.df_filtered = None
    
    # Main content
    if 'df_filtered' in st.session_state and st.session_state.df_filtered is not None:
        df = st.session_state.df_filtered
        
        # Batch analysis
        if st.button("🚀 Analyze All Matches", type="primary", use_container_width=True):
            with st.spinner("Analyzing matches..."):
                results_df = engine.analyze_all_matches(df)
            
            st.markdown("### 📈 Batch Analysis Results")
            st.dataframe(results_df, use_container_width=True, height=400)
            
            # Summary statistics
            st.markdown("### 📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                narrative_counts = results_df['Narrative'].value_counts()
                most_common = narrative_counts.index[0] if len(narrative_counts) > 0 else "None"
                st.metric("Most Common Narrative", most_common)
            
            with col2:
                try:
                    avg_conf = results_df['Confidence'].str.rstrip('%').astype(float).mean()
                    st.metric("Avg Confidence", f"{avg_conf:.1f}%")
                except:
                    st.metric("Avg Confidence", "N/A")
            
            with col3:
                tier1_count = len(results_df[results_df['Tier'].str.contains('TIER 1')])
                st.metric("Tier 1 Matches", tier1_count)
            
            with col4:
                value_matches = len(results_df[results_df['Units'] != 'No bet'])
                st.metric("Betting Opportunities", value_matches)
            
            # Narrative distribution
            st.markdown("### 📊 Narrative Distribution")
            fig = go.Figure(data=[
                go.Pie(
                    labels=narrative_counts.index,
                    values=narrative_counts.values,
                    hole=0.3,
                    marker_colors=['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#6B7280']
                )
            ])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name="narrative_analysis.csv",
                mime="text/csv"
            )
        
        # Individual match analysis
        st.markdown("---")
        st.markdown("### 🎯 Individual Match Analysis")
        
        # Create match selector
        match_options = []
        for idx, row in df.iterrows():
            home = row.get('home_team', 'Home')
            away = row.get('away_team', 'Away')
            date = row.get('date', 'Unknown')
            match_options.append(f"{home} vs {away} ({date})")
        
        selected_match = st.selectbox("Select Match", match_options)
        
        if selected_match:
            # Get the selected match data
            match_idx = match_options.index(selected_match)
            match_data = df.iloc[match_idx]
            
            # Analyze match
            analysis = engine.analyze_match(match_data)
            
            # Display analysis
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"""
                <div class="narrative-card {analysis['color']}">
                    <h3>{analysis['narrative']}</h3>
                    <p>{analysis['description']}</p>
                    <div style="margin-top: 15px;">
                        <span class="badge tier-{analysis['tier'].split()[1]}">{analysis['tier']}</span>
                        <span class="badge" style="background: #3B82F6; color: white;">Confidence: {analysis['confidence']:.1f}%</span>
                        <span class="badge" style="background: #10B981; color: white;">{analysis['units']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display match info
                st.markdown("#### 🏟️ Match Details")
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown(f"**{match_data.get('home_team', 'Home')}**")
                    st.caption(f"Position: {match_data.get('home_position', 'N/A')}")
                    st.caption(f"Form: {match_data.get('home_form', 'N/A')}")
                    st.caption(f"Manager: {match_data.get('home_manager_style', 'N/A')}")
                    st.caption(f"Attack/Defense: {match_data.get('home_attack_rating', 'N/A')}/{match_data.get('home_defense_rating', 'N/A')}")
                    st.caption(f"Odds: {match_data.get('home_odds', 'N/A')}")
                
                with info_col2:
                    st.markdown(f"**{match_data.get('away_team', 'Away')}**")
                    st.caption(f"Position: {match_data.get('away_position', 'N/A')}")
                    st.caption(f"Form: {match_data.get('away_form', 'N/A')}")
                    st.caption(f"Manager: {match_data.get('away_manager_style', 'N/A')}")
                    st.caption(f"Attack/Defense: {match_data.get('away_attack_rating', 'N/A')}/{match_data.get('away_defense_rating', 'N/A')}")
                    st.caption(f"Odds: {match_data.get('away_odds', 'N/A')}")
            
            with col2:
                # Probability gauges
                st.markdown("#### 📊 Probabilities")
                
                fig = make_subplots(
                    rows=2, cols=2,
                    specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                          [{'type': 'indicator'}, {'type': 'indicator'}]],
                    subplot_titles=('Home Win', 'Draw', 'Away Win', 'BTTS')
                )
                
                # Home win
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=analysis['probabilities']['home_win'],
                    domain={'row': 0, 'column': 0},
                    gauge={'axis': {'range': [0, 100]}}
                ), row=1, col=1)
                
                # Draw
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=analysis['probabilities']['draw'],
                    domain={'row': 0, 'column': 1},
                    gauge={'axis': {'range': [0, 100]}}
                ), row=1, col=2)
                
                # Away win
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=analysis['probabilities']['away_win'],
                    domain={'row': 1, 'column': 0},
                    gauge={'axis': {'range': [0, 100]}}
                ), row=2, col=1)
                
                # BTTS
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=analysis['probabilities']['btts'],
                    domain={'row': 1, 'column': 1},
                    gauge={'axis': {'range': [0, 100]}}
                ), row=2, col=2)
                
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Expected goals
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Expected Goals", f"{analysis['probabilities']['total_goals']:.2f}")
                with col2:
                    over_under = "Over" if analysis['probabilities']['total_goals'] > 2.5 else "Under"
                    st.metric("Over/Under 2.5", over_under)
            
            # Market recommendations
            st.markdown("#### 💰 Recommended Markets")
            
            if analysis['markets']:
                for market in analysis['markets']:
                    st.markdown(f"""
                    <div class="recommendation">
                        <strong>{market}</strong>
                        <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #4B5563;">
                            Based on {analysis['narrative']} narrative analysis
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific market recommendations for this narrative")
            
            # Narrative scores breakdown
            with st.expander("🔍 Narrative Scores Breakdown"):
                scores_df = pd.DataFrame({
                    'Narrative': list(analysis['scores'].keys()),
                    'Score': list(analysis['scores'].values())
                }).sort_values('Score', ascending=False)
                
                st.dataframe(scores_df, use_container_width=True)
                
                # Visualize scores
                fig = go.Figure(data=[
                    go.Bar(
                        x=scores_df['Narrative'],
                        y=scores_df['Score'],
                        marker_color=['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#6B7280']
                    )
                ])
                fig.update_layout(
                    title="Narrative Match Scores",
                    xaxis_title="Narrative",
                    yaxis_title="Score (%)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Welcome screen
        st.markdown("""
        ## ⚽ Welcome to the Narrative Intelligence Engine
        
        This engine analyzes football matches based on **tactical narratives** rather than just statistics.
        
        ### 🔑 How it works:
        1. **Upload your CSV** with match data
        2. **Engine analyzes** each match's tactical setup
        3. **Classifies into narratives** (Siege, Blitzkrieg, Edge-Chaos, etc.)
        4. **Provides specific betting recommendations** for each narrative
        
        ### 📋 Required CSV Columns:
        ```
        home_team, away_team, date
        home_position, away_position
        home_odds, away_odds
        home_form, away_form (e.g., "WWDLW")
        home_manager_style, away_manager_style
        home_attack_rating, away_attack_rating (1-10)
        home_defense_rating, away_defense_rating (1-10)
        home_press_rating, away_press_rating (1-10)
        home_pragmatic_rating, away_pragmatic_rating (1-10)
        last_h2h_goals, last_h2h_btts
        ```
        
        ### 🎯 Key Narratives:
        - **SIEGE**: Dominant possession vs parked bus
        - **BLITZKRIEG**: Early high-press onslaught
        - **EDGE-CHAOS**: Style clash with transitions
        - **CONTROLLED_EDGE**: Methodical favorite vs organized underdog
        - **SHOOTOUT**: End-to-end attacking chaos
        - **CHESS_MATCH**: Tactical stalemate
        
        **Upload a CSV file to get started!**
        """)

if __name__ == "__main__":
    main()
