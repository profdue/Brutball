import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from collections import defaultdict

# Set page config
st.set_page_config(
    page_title="Narrative Prediction System v2.5",
    page_icon="📊",
    layout="wide"
)

class EnhancedNarrativeSystem:
    def __init__(self):
        # Enhanced narratives based on your analysis
        self.narrative_definitions = {
            "TIER 1 - CLEAR NARRATIVES": {
                "THE BLITZKRIEG (Early Domination)": {
                    "description": "Heavy favorite dominates early, opponent collapses",
                    "success_rate": 1.00,  # 100% from testing
                    "criteria_weights": {
                        "favorite_win_prob": 30,
                        "home_advantage": 20,
                        "early_goal_history": 25,
                        "stakes_mismatch": 15,
                        "opponent_collapse_tendency": 10
                    },
                    "betting_confidence": "HIGH",
                    "stake_percentage": "2-3%"
                },
                "THE SHOOTOUT (End-to-End Chaos)": {
                    "description": "Both teams attack relentlessly, high-scoring chaos",
                    "success_rate": 1.00,  # 100% from testing
                    "criteria_weights": {
                        "both_btts_pct": 25,
                        "both_over_25_pct": 20,
                        "manager_attack_style": 20,
                        "defensive_weakness_both": 15,
                        "high_stakes_both": 10,
                        "derby_rivalry": 10
                    },
                    "betting_confidence": "HIGH",
                    "stake_percentage": "2-3%"
                },
                "THE CHESS MATCH (Tactical Stalemate)": {
                    "description": "Cautious tactical battle, low scoring",
                    "success_rate": 1.00,  # 100% from testing
                    "criteria_weights": {
                        "both_cautious": 30,
                        "match_importance": 25,
                        "manager_pragmatism": 20,
                        "h2h_low_scoring": 15,
                        "both_under_25_pct": 10
                    },
                    "betting_confidence": "HIGH",
                    "stake_percentage": "2-3%"
                }
            },
            "TIER 2 - MODIFIED NARRATIVES": {
                "THE SIEGE v2.0 (Attack vs Defense)": {
                    "description": "Attacker dominates but defense has counter threat",
                    "success_rate": 0.33,  # 33% from testing
                    "criteria_weights": {
                        "possession_mismatch": 25,
                        "shots_ratio": 20,
                        "attacker_motivation": 20,
                        "defender_desperation": 15,
                        "counter_attack_threat": 10,
                        "clean_sheet_history": 10
                    },
                    "betting_confidence": "MEDIUM",
                    "stake_percentage": "1-1.5%",
                    "key_insight": "BTTS probability = 40% (not 20%), Clean Sheet = 50% (not 70%)"
                },
                "THE CONTROLLED BLITZKRIG": {
                    "description": "Favorite dominates but opponent resilient",
                    "success_rate": None,  # New category
                    "criteria_weights": {
                        "favorite_win_prob": 20,
                        "control_possession": 25,
                        "opponent_resilience": 20,
                        "stakes_mismatch": 15,
                        "late_goals_unlikely": 10,
                        "low_risk_approach": 10
                    },
                    "betting_confidence": "MEDIUM",
                    "stake_percentage": "1-1.5%"
                }
            },
            "TIER 3 - HYBRID NARRATIVES": {
                "SIEGE-SHOOTOUT HYBRID": {
                    "description": "Attack vs Defense but both find scoring opportunities",
                    "success_rate": None,  # New category
                    "criteria_weights": {
                        "possession_mismatch": 20,
                        "counter_attack_threat": 25,
                        "set_piece_threat": 15,
                        "attacker_pressure": 15,
                        "defender_scoring_form": 15,
                        "game_state_changes": 10
                    },
                    "betting_confidence": "LOW",
                    "stake_percentage": "0.5%",
                    "example": "Atalanta 2-1 Cagliari"
                },
                "CHESS-SIEGE HYBRID": {
                    "description": "Cautious start then one team takes initiative",
                    "success_rate": None,  # New category
                    "criteria_weights": {
                        "both_cautious_start": 25,
                        "second_half_intensity": 20,
                        "fatigue_factor": 15,
                        "substitution_impact": 15,
                        "late_breakthrough": 15,
                        "low_scoring_tendency": 10
                    },
                    "betting_confidence": "LOW",
                    "stake_percentage": "0.5%"
                },
                "NO CLEAR NARRATIVE": {
                    "description": "Conflicting signals, unpredictable outcome",
                    "success_rate": 0.00,  # Avoid betting
                    "criteria_weights": {},
                    "betting_confidence": "AVOID",
                    "stake_percentage": "0%"
                }
            }
        }
        
        # Historical performance data
        self.historical_performance = {
            "total_tested": 6,
            "perfect_matches": 4,
            "partial_matches": 2,
            "anomalies": 1,
            "narrative_success": {
                "BLITZKRIEG": {"tested": 2, "correct": 2, "success_rate": 1.00},
                "SHOOTOUT": {"tested": 1, "correct": 1, "success_rate": 1.00},
                "CHESS MATCH": {"tested": 1, "correct": 1, "success_rate": 1.00},
                "SIEGE": {"tested": 3, "correct": 1, "success_rate": 0.33}
            }
        }
    
    def calculate_tiered_scores(self, match_data):
        """Calculate scores for all narratives with tier classification"""
        
        scores = {}
        tier_classification = {}
        
        # Calculate for each narrative
        for tier, narratives in self.narrative_definitions.items():
            for narrative_name, narrative_def in narratives.items():
                if narrative_name == "NO CLEAR NARRATIVE":
                    continue
                    
                score = 0
                weights = narrative_def["criteria_weights"]
                
                # Calculate score based on criteria weights
                for criterion, weight in weights.items():
                    if criterion in match_data:
                        value = match_data[criterion]
                        # Normalize to 0-100 scale
                        if isinstance(value, (int, float)):
                            if criterion.endswith('_pct') or criterion.endswith('_prob'):
                                score += value * weight
                            elif 'mismatch' in criterion or 'advantage' in criterion:
                                score += (1 if value else 0) * weight
                            elif 'ratio' in criterion and value > 0:
                                # For shots ratio > 3:1 = max points
                                score += min(value/3, 1) * weight
                            else:
                                # Generic scoring
                                score += min(value/10, 1) * weight
                
                scores[narrative_name] = min(100, score)
                tier_classification[narrative_name] = tier
        
        # Check for NO CLEAR NARRATIVE
        if scores:
            max_score = max(scores.values())
            if max_score < 40:  # Very low confidence
                scores["NO CLEAR NARRATIVE"] = 100 - max_score
        
        return scores, tier_classification
    
    def analyze_match_flow(self, match_data, dominant_narrative, narrative_score):
        """Generate detailed match flow prediction"""
        
        flow_predictions = {
            "BLITZKRIEG": {
                "expected_flow": [
                    "Early pressure from favorite (0-15 mins)",
                    "Breakthrough likely before 30 mins",
                    "Opponent confidence collapses after first goal",
                    "Additional goals in 35-65 minute window",
                    "Game effectively over by 70 mins"
                ],
                "key_moments": [
                    "First goal timing: 15-30 mins",
                    "Second goal within 15 mins of first",
                    "Opponent yellow cards increase after conceding",
                    "Substitutions reflect surrender"
                ],
                "risk_factors": [
                    "Early set piece concession",
                    "Red card changes dynamic",
                    "Weather conditions neutralize advantage"
                ]
            },
            "SIEGE v2.0": {
                "expected_flow": [
                    "Attacker dominates possession (60-70%)",
                    "Defender organizes in low block",
                    "Frustration builds as chances missed",
                    "Breakthrough via set piece or individual brilliance",
                    "Counter-attack threat persists throughout"
                ],
                "key_moments": [
                    "First goal timing: 40-70 mins",
                    "Defender's best chance comes on counter",
                    "Attacker substitution around 60 mins for breakthrough",
                    "Set piece opportunities crucial"
                ],
                "risk_factors": [
                    "Early counter-attack goal changes narrative",
                    "Attacker red card kills momentum",
                    "Defender loses discipline under pressure"
                ]
            },
            "SHOOTOUT": {
                "expected_flow": [
                    "Fast start from both teams",
                    "Goals likely at both ends",
                    "Lead changes possible",
                    "High intensity throughout",
                    "Late drama highly probable"
                ],
                "key_moments": [
                    "First goal timing: 0-25 mins",
                    "Response goal within 10 mins likely",
                    "Second half goals increase",
                    "Late winner/equalizer threat"
                ],
                "risk_factors": [
                    "Early red card ruins open game",
                    "Weather conditions affect passing",
                    "Injuries to key attackers"
                ]
            },
            "CHESS MATCH": {
                "expected_flow": [
                    "Cautious opening 20 mins",
                    "Midfield battle dominates",
                    "Few clear chances created",
                    "First goal often decisive",
                    "Late goals rare"
                ],
                "key_moments": [
                    "First goal timing: 40-70 mins if any",
                    "Set pieces primary threat",
                    "Substitutions cautious, tactical",
                    "Discipline maintained throughout"
                ],
                "risk_factors": [
                    "Early goal forces tactical change",
                    "Individual mistake breaks deadlock",
                    "Referee decisions crucial"
                ]
            }
        }
        
        # Get base flow for narrative
        narrative_key = dominant_narrative.split("(")[0].strip().upper()
        for key in flow_predictions:
            if key in narrative_key:
                return flow_predictions[key]
        
        return flow_predictions.get("BLITZKRIEG", {})  # Default
    
    def generate_betting_recommendations(self, narrative, score, tier):
        """Generate tier-specific betting recommendations"""
        
        recommendations = {
            "TIER 1 - CLEAR NARRATIVES": {
                "BLITZKRIEG": [
                    "Favorite -1.5 Asian Handicap",
                    "Favorite to win both halves",
                    "Over 2.5 team goals for favorite",
                    "Favorite clean sheet",
                    "First goal before 25:00"
                ],
                "SHOOTOUT": [
                    "Over 2.5 goals",
                    "BTTS: Yes",
                    "Both teams to score & Over 2.5",
                    "2-1 correct score group",
                    "Goal in both halves"
                ],
                "CHESS MATCH": [
                    "Under 2.5 goals",
                    "BTTS: No",
                    "0-0 or 1-0 correct score",
                    "Draw no bet (if evenly matched)",
                    "Fewer than 10 corners total"
                ]
            },
            "TIER 2 - MODIFIED NARRATIVES": {
                "SIEGE v2.0": [
                    "Home win (if attacker is home)",
                    "Under 3.5 goals",
                    "BTTS: No (but check defender scoring form)",
                    "1-0 correct score",
                    "Team to win to nil (if clean sheet likely)"
                ],
                "CONTROLLED BLITZKRIEG": [
                    "Favorite win",
                    "Under 3.5 goals",
                    "Favorite to score 2+",
                    "Win to nil if strong defense",
                    "Half-time/Full-time favorite/favorite"
                ]
            },
            "TIER 3 - HYBRID NARRATIVES": {
                "SIEGE-SHOOTOUT HYBRID": [
                    "BTTS: Yes (40% probability)",
                    "Over 2.5 goals (medium probability)",
                    "Double chance: Home win or Draw",
                    "In-play betting opportunities",
                    "Avoid pre-match major positions"
                ],
                "CHESS-SIEGE HYBRID": [
                    "Under 2.5 goals",
                    "Second half most goals",
                    "Late goal after 75:00",
                    "Draw no bet",
                    "Small stakes only"
                ],
                "NO CLEAR NARRATIVE": [
                    "AVOID pre-match betting",
                    "Consider in-play after 20 mins",
                    "Alternative markets only",
                    "Micro-stakes entertainment bets only"
                ]
            }
        }
        
        # Get narrative key
        narrative_key = narrative.split("(")[0].strip().upper()
        
        # Find matching recommendations
        for tier_key, tier_recs in recommendations.items():
            for rec_narrative, rec_list in tier_recs.items():
                if rec_narrative in narrative_key or narrative_key in rec_narrative:
                    return rec_list
        
        return ["No specific recommendations - use caution"]
    
    def get_stake_guidance(self, tier, narrative_score):
        """Get stake sizing guidance based on tier and score"""
        
        if tier == "TIER 1 - CLEAR NARRATIVES":
            if narrative_score >= 80:
                return {
                    "stake_percentage": "3%",
                    "rationale": "High confidence, proven track record",
                    "max_bets_per_day": 2,
                    "bankroll_requirement": "Full allocation"
                }
            elif narrative_score >= 60:
                return {
                    "stake_percentage": "2%",
                    "rationale": "Good confidence but slight uncertainties",
                    "max_bets_per_day": 3,
                    "bankroll_requirement": "80% of allocation"
                }
        
        elif tier == "TIER 2 - MODIFIED NARRATIVES":
            if narrative_score >= 70:
                return {
                    "stake_percentage": "1.5%",
                    "rationale": "Medium confidence, mixed historical results",
                    "max_bets_per_day": 4,
                    "bankroll_requirement": "60% of allocation"
                }
            elif narrative_score >= 50:
                return {
                    "stake_percentage": "1%",
                    "rationale": "Lower confidence, hedging recommended",
                    "max_bets_per_day": 5,
                    "bankroll_requirement": "40% of allocation"
                }
        
        elif tier == "TIER 3 - HYBRID NARRATIVES":
            return {
                "stake_percentage": "0.5%",
                "rationale": "Low confidence, high uncertainty",
                "max_bets_per_day": "Avoid or 1-2 maximum",
                "bankroll_requirement": "20% of allocation for entertainment only"
            }
        
        # Default for NO CLEAR NARRATIVE
        return {
            "stake_percentage": "0%",
            "rationale": "Avoid betting - no clear edge",
            "max_bets_per_day": 0,
            "bankroll_requirement": "0%"
        }

def main():
    st.title("⚽ Narrative Prediction System v2.5")
    st.markdown("### **Enhanced Tiered System with Hybrid Narratives**")
    
    # Initialize the system
    ns = EnhancedNarrativeSystem()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Match Analysis", 
        "📊 Performance Dashboard", 
        "🔄 Live Testing Protocol", 
        "📈 System Evolution"
    ])
    
    with tab1:
        st.header("Enhanced Match Analysis")
        
        # Match selection
        st.subheader("Select Match Type")
        
        match_type = st.radio(
            "Analysis Mode:",
            ["Historical Match", "Live Match", "Custom Input"],
            horizontal=True
        )
        
        if match_type == "Historical Match":
            historical_matches = [
                "Atalanta 2-1 Cagliari (Siege anomaly)",
                "Man City 3-0 Crystal Palace (Blitzkrieg perfect)",
                "West Ham 2-3 Aston Villa (Shootout perfect)",
                "Sunderland 1-0 Newcastle (Chess Match perfect)",
                "Liverpool 2-0 Brighton (Siege partial)",
                "Fenerbahce 4-0 Konyaspor (Blitzkrieg perfect)"
            ]
            
            selected_match = st.selectbox("Select historical match:", historical_matches)
            
            # Pre-populate based on selection
            if "Atalanta" in selected_match:
                match_data = {
                    "possession_mismatch": 0.65,  # Atalanta 65% possession
                    "shots_ratio": 3.5,  # 21 shots vs 6
                    "attacker_motivation": 1.0,
                    "defender_desperation": 0.8,
                    "counter_attack_threat": 0.7,  # Cagliari scored
                    "clean_sheet_history": 0.3  # Atalanta clean sheet % low
                }
            elif "Man City" in selected_match:
                match_data = {
                    "favorite_win_prob": 0.85,
                    "home_advantage": 1.0,
                    "early_goal_history": 0.8,
                    "stakes_mismatch": 1.0,
                    "opponent_collapse_tendency": 0.9
                }
            elif "West Ham" in selected_match:
                match_data = {
                    "both_btts_pct": 0.75,
                    "both_over_25_pct": 0.8,
                    "manager_attack_style": 1.0,
                    "defensive_weakness_both": 0.9,
                    "high_stakes_both": 0.7,
                    "derby_rivalry": 0.6
                }
            else:
                match_data = {}
        
        elif match_type == "Live Match":
            st.subheader("Today's Premier League Matches")
            
            live_matches = [
                "Arsenal vs Chelsea",
                "Manchester United vs Leeds",
                "Tottenham vs Brentford",
                "Liverpool vs Everton",
                "Manchester City vs Wolves"
            ]
            
            selected_match = st.selectbox("Select live match:", live_matches)
            
            # Quick analysis based on team characteristics
            if "Arsenal vs Chelsea" in selected_match:
                st.info("**Quick Assessment:** Potential Chess Match - both teams cautious, high stakes")
                match_data = {
                    "both_cautious": 0.8,
                    "match_importance": 0.9,
                    "manager_pragmatism": 0.7,
                    "h2h_low_scoring": 0.6,
                    "both_under_25_pct": 0.7
                }
            elif "Manchester United vs Leeds" in selected_match:
                st.info("**Quick Assessment:** Potential Shootout - both attack-minded, weak defenses")
                match_data = {
                    "both_btts_pct": 0.65,
                    "both_over_25_pct": 0.7,
                    "manager_attack_style": 0.9,
                    "defensive_weakness_both": 0.8,
                    "high_stakes_both": 0.5,
                    "derby_rivalry": 0.9
                }
            else:
                match_data = {}
        
        else:  # Custom Input
            st.subheader("Custom Match Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Team A (Attacker/Home)**")
                team_a = st.text_input("Team A Name", "Team A")
                possession_a = st.slider(f"{team_a} Avg Possession %", 0, 100, 60)
                shots_a = st.number_input(f"{team_a} Avg Shots/Game", 0, 30, 15)
                motivation_a = st.slider(f"{team_a} Motivation", 0.0, 1.0, 0.8, 0.1)
                
            with col2:
                st.markdown("**Team B (Defender/Away)**")
                team_b = st.text_input("Team B Name", "Team B")
                possession_b = 100 - possession_a
                shots_b = st.number_input(f"{team_b} Avg Shots/Game", 0, 30, 8)
                counter_threat = st.slider(f"{team_b} Counter Attack Threat", 0.0, 1.0, 0.4, 0.1)
            
            # Calculate derived metrics
            possession_mismatch = abs(possession_a - possession_b) / 100
            shots_ratio = shots_a / max(shots_b, 1)
            
            match_data = {
                "possession_mismatch": possession_mismatch,
                "shots_ratio": shots_ratio,
                "attacker_motivation": motivation_a,
                "counter_attack_threat": counter_threat,
                "favorite_win_prob": 0.6 if possession_a > 55 else 0.4,
                "both_cautious": 0.3 if possession_mismatch < 0.2 else 0.7
            }
        
        # Calculate narrative scores
        if 'match_data' in locals() and match_data:
            scores, tiers = ns.calculate_tiered_scores(match_data)
            
            if scores:
                # Display results
                st.subheader("📊 Narrative Analysis Results")
                
                # Get dominant narrative
                dominant_narrative = max(scores.items(), key=lambda x: x[1])
                dominant_tier = tiers.get(dominant_narrative[0], "Unknown")
                
                # Display dominant narrative
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Dominant Narrative", dominant_narrative[0])
                with col2:
                    st.metric("Score", f"{dominant_narrative[1]}/100")
                with col3:
                    st.metric("Tier", dominant_tier.split(" - ")[0])
                
                # Progress bar for confidence
                st.progress(dominant_narrative[1]/100)
                st.caption(f"Confidence Level: {'High' if dominant_narrative[1] >= 70 else 'Medium' if dominant_narrative[1] >= 50 else 'Low'}")
                
                # All narrative scores visualization
                st.subheader("All Narrative Scores")
                
                # Group by tier for visualization
                tier_groups = defaultdict(list)
                for narrative, score in scores.items():
                    tier = tiers.get(narrative, "Unknown")
                    tier_groups[tier].append((narrative, score))
                
                # Create bar chart
                fig = go.Figure()
                
                colors = {
                    "TIER 1 - CLEAR NARRATIVES": "#00CC96",
                    "TIER 2 - MODIFIED NARRATIVES": "#FFA15A",
                    "TIER 3 - HYBRID NARRATIVES": "#EF553B"
                }
                
                for tier, narratives in tier_groups.items():
                    if narratives:
                        narrative_names = [n[0] for n in narratives]
                        narrative_scores = [n[1] for n in narratives]
                        
                        fig.add_trace(go.Bar(
                            x=narrative_scores,
                            y=narrative_names,
                            orientation='h',
                            name=tier,
                            marker_color=colors.get(tier, "#636EFA"),
                            text=[f"{s}/100" for s in narrative_scores],
                            textposition='auto'
                        ))
                
                fig.update_layout(
                    title="Narrative Scores by Tier",
                    xaxis_title="Score (0-100)",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Match flow prediction
                st.subheader("🎯 Expected Match Flow")
                
                flow = ns.analyze_match_flow(match_data, dominant_narrative[0], dominant_narrative[1])
                
                if flow:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Expected Flow:**")
                        for item in flow.get("expected_flow", []):
                            st.write(f"• {item}")
                    
                    with col2:
                        st.markdown("**Key Moments:**")
                        for item in flow.get("key_moments", []):
                            st.write(f"• {item}")
                    
                    with col3:
                        st.markdown("**Risk Factors:**")
                        for item in flow.get("risk_factors", []):
                            st.write(f"• {item}")
                
                # Betting recommendations
                st.subheader("💰 Betting Recommendations")
                
                recommendations = ns.generate_betting_recommendations(
                    dominant_narrative[0], 
                    dominant_narrative[1], 
                    dominant_tier
                )
                
                stake_guidance = ns.get_stake_guidance(dominant_tier, dominant_narrative[1])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Recommended Markets:**")
                    for rec in recommendations:
                        st.write(f"✓ {rec}")
                
                with col2:
                    st.markdown("**Stake Guidance:**")
                    for key, value in stake_guidance.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    with tab2:
        st.header("Performance Dashboard")
        
        # Historical performance
        perf = ns.historical_performance
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tested", perf["total_tested"])
        with col2:
            st.metric("Perfect Matches", perf["perfect_matches"])
        with col3:
            success_rate = (perf["perfect_matches"] / perf["total_tested"]) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col4:
            st.metric("Anomalies", perf["anomalies"])
        
        # Narrative success rates
        st.subheader("Narrative Success Rates")
        
        narrative_data = []
        for narrative, stats in perf["narrative_success"].items():
            narrative_data.append({
                "Narrative": narrative,
                "Tested": stats["tested"],
                "Correct": stats["correct"],
                "Success Rate": f"{stats['success_rate']*100:.0f}%"
            })
        
        df = pd.DataFrame(narrative_data)
        
        # Color coding based on success rate
        def color_success_rate(val):
            rate = float(val.strip('%'))
            if rate >= 80:
                return 'background-color: #90EE90'
            elif rate >= 50:
                return 'background-color: #FFFFE0'
            else:
                return 'background-color: #FFB6C1'
        
        styled_df = df.style.applymap(color_success_rate, subset=['Success Rate'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Insights from data
        st.subheader("Key Insights")
        
        insights = [
            "✅ **Tier 1 narratives (Blitzkrieg, Shootout, Chess) are highly reliable**",
            "⚠️ **Siege narrative needs modification - BTTS occurs more often than expected**",
            "🎯 **High narrative scores (>80) correlate with perfect predictions**",
            "📊 **Hybrid narratives identified as new opportunity**",
            "💰 **Tier-based betting approach minimizes risk**"
        ]
        
        for insight in insights:
            st.write(insight)
    
    with tab3:
        st.header("Live Testing Protocol")
        
        st.markdown("""
        ## **Week 1: Validation & Refinement**
        
        ### **Step 1: Refine Siege Narrative**
        Based on Atalanta 2-1 Cagliari:
        - Add counter-attack threat assessment
        - Adjust BTTS probability from 20% → 40%
        - Adjust clean sheet probability from 70% → 50%
        
        ### **Step 2: Test on New Historical Matches**
        Select 5 additional historical matches:
        1. One clear Blitzkrieg
        2. One clear Shootout  
        3. One clear Chess Match
        4. Two Siege matches (one with BTTS, one without)
        
        ### **Step 3: Build Quick-Reference Guide**
        Create decision tree for narrative identification
        """)
        
        # Weekly testing template
        st.subheader("Weekly Testing Template")
        
        week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3"])
        
        if week == "Week 1":
            tasks = [
                "Refine Siege narrative criteria",
                "Test on 5 new historical matches",
                "Create hybrid narrative definitions",
                "Build quick-reference guide"
            ]
        elif week == "Week 2":
            tasks = [
                "Select 5 weekend matches for live testing",
                "Make pre-match narrative predictions",
                "Track outcomes vs predictions",
                "Adjust real-time based on results"
            ]
        else:  # Week 3
            tasks = [
                "Create betting rules per narrative",
                "Define optimal markets for each narrative type",
                "Develop stake sizing based on narrative confidence",
                "Build full integration with betting strategy"
            ]
        
        for i, task in enumerate(tasks, 1):
            st.checkbox(f"{i}. {task}")
        
        # Download testing log
        st.download_button(
            label="📥 Download Testing Log Template",
            data=pd.DataFrame(columns=[
                "Date", "Match", "Predicted Narrative", "Score",
                "Tier", "Actual Outcome", "Narrative Match?", 
                "Key Learning", "Adjustment Needed"
            ]).to_csv(index=False),
            file_name="narrative_testing_log.csv",
            mime="text/csv"
        )
        
        # Live match prediction form
        st.subheader("Live Match Prediction Form")
        
        with st.form("live_prediction"):
            match_date = st.date_input("Match Date")
            home_team = st.text_input("Home Team")
            away_team = st.text_input("Away Team")
            predicted_narrative = st.selectbox(
                "Predicted Narrative",
                ["BLITZKRIEG", "SHOOTOUT", "CHESS MATCH", "SIEGE v2.0", 
                 "CONTROLLED BLITZKRIEG", "SIEGE-SHOOTOUT HYBRID", "NO CLEAR NARRATIVE"]
            )
            confidence = st.slider("Confidence (0-100)", 0, 100, 70)
            key_reasoning = st.text_area("Key Reasoning")
            
            submitted = st.form_submit_button("Submit Prediction")
            
            if submitted:
                st.success(f"Prediction submitted for {home_team} vs {away_team}")
                st.info(f"Narrative: {predicted_narrative} | Confidence: {confidence}/100")
    
    with tab4:
        st.header("System Evolution")
        
        st.markdown("""
        ## **Three-Tier System Implementation**
        
        Based on retrospective testing, we've developed a tiered approach:
        """)
        
        # Tier explanation
        tiers_explanation = {
            "TIER 1 - CLEAR NARRATIVES": {
                "description": "Proven success rate >80%",
                "examples": ["Blitzkrieg", "Shootout", "Chess Match"],
                "betting_approach": "Confident betting, 2-3% stakes",
                "success_rate": "100% in testing"
            },
            "TIER 2 - MODIFIED NARRATIVES": {
                "description": "Mixed results, needs refinement",
                "examples": ["Siege v2.0", "Controlled Blitzkrieg"],
                "betting_approach": "Cautious betting, 1-1.5% stakes",
                "success_rate": "33-50% expected"
            },
            "TIER 3 - HYBRID NARRATIVES": {
                "description": "New categories, high uncertainty",
                "examples": ["Siege-Shootout Hybrid", "Chess-Siege Hybrid"],
                "betting_approach": "Micro-stakes only (0.5%) or avoid",
                "success_rate": "Testing phase"
            }
        }
        
        for tier, info in tiers_explanation.items():
            with st.expander(f"{tier}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {info['description']}")
                    st.write(f"**Examples:** {', '.join(info['examples'])}")
                with col2:
                    st.write(f"**Betting Approach:** {info['betting_approach']}")
                    st.write(f"**Success Rate:** {info['success_rate']}")
        
        # Evolution roadmap
        st.subheader("Evolution Roadmap")
        
        roadmap = [
            {"phase": "Phase 1", "goal": "Validate core narratives", "status": "✓ Completed", "result": "67% accuracy"},
            {"phase": "Phase 2", "goal": "Refine Siege narrative", "status": "🔄 In Progress", "result": "Target: 80% accuracy"},
            {"phase": "Phase 3", "goal": "Test hybrid narratives", "status": "⏳ Planned", "result": "Identify new patterns"},
            {"phase": "Phase 4", "goal": "Live betting integration", "status": "⏳ Future", "result": "Full automation"}
        ]
        
        for phase in roadmap:
            status_color = {
                "✓ Completed": "🟢",
                "🔄 In Progress": "🟡",
                "⏳ Planned": "🟠",
                "⏳ Future": "⚪"
            }
            st.write(f"{status_color[phase['status']]} **{phase['phase']}:** {phase['goal']} - {phase['result']}")

if __name__ == "__main__":
    main()
