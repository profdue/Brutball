# Add this function near the top of your code, after the CSS
def display_data_transparency(home_data, away_data, home_team, away_team):
    """Show CSV data and calculations transparently"""
    
    with st.expander("📊 **Data & Calculation Transparency**", expanded=False):
        tab1, tab2, tab3 = st.tabs(["📋 Raw Data", "🧮 Calculations", "⚖️ Factor Impact"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"##### {home_team} CSV Data")
                # Create a clean dataframe for display
                home_display = {
                    'Metric': ['Goals', 'Games Played', 'Shots Allowed PG', 'xG', 'Form Last 5', 
                              'Defenders Out', 'Motivation', 'Open Play %', 'Set Piece %', 'Counter %'],
                    'Value': [
                        home_data['goals'],
                        home_data['games_played'],
                        f"{home_data['shots_allowed_pg']:.1f}",
                        f"{home_data['xg']:.1f}",
                        f"{home_data['form_last_5']:.1f}",
                        home_data['defenders_out'],
                        f"{home_data['motivation']}/5",
                        f"{home_data.get('open_play_pct', 0)*100:.0f}%" if 'open_play_pct' in home_data else "N/A",
                        f"{home_data.get('set_piece_pct', 0)*100:.0f}%" if 'set_piece_pct' in home_data else "N/A",
                        f"{home_data.get('counter_attack_pct', 0)*100:.0f}%" if 'counter_attack_pct' in home_data else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(home_display), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown(f"##### {away_team} CSV Data")
                away_display = {
                    'Metric': ['Goals', 'Games Played', 'Shots Allowed PG', 'xG', 'Form Last 5',
                              'Defenders Out', 'Motivation', 'Open Play %', 'Set Piece %', 'Counter %'],
                    'Value': [
                        away_data['goals'],
                        away_data['games_played'],
                        f"{away_data['shots_allowed_pg']:.1f}",
                        f"{away_data['xg']:.1f}",
                        f"{away_data['form_last_5']:.1f}",
                        away_data['defenders_out'],
                        f"{away_data['motivation']}/5",
                        f"{away_data.get('open_play_pct', 0)*100:.0f}%" if 'open_play_pct' in away_data else "N/A",
                        f"{away_data.get('set_piece_pct', 0)*100:.0f}%" if 'set_piece_pct' in away_data else "N/A",
                        f"{away_data.get('counter_attack_pct', 0)*100:.0f}%" if 'counter_attack_pct' in away_data else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(away_display), use_container_width=True, hide_index=True)
        
        with tab2:
            st.markdown("##### Key Calculation Factors")
            
            # Form calculation
            if 'form' in home_data and home_data['form']:
                form_str = home_data['form'][-5:] if len(home_data['form']) >= 5 else home_data['form']
                form_points = {'W': 3, 'D': 1, 'L': 0}
                weights = [1.0, 0.8, 0.64, 0.51, 0.41]
                
                st.write(f"**Form Translation**: `{form_str}` → {home_data['form_last_5']:.1f}")
                st.caption(f"Recent matches weighted more heavily")
            
            # Injury impact
            st.write(f"**Injury Impact**: {away_data['defenders_out']} defenders out = {min(10, away_data['defenders_out']*2)}/10 injury level")
            st.caption(f"Reduces opponent's attack by {(away_data['defenders_out']*2)*5:.0f}%")
            
            # Shots multiplier explanation
            st.write(f"**Defense Multiplier**: {away_data['shots_allowed_pg']:.1f} shots allowed / league avg = {(away_data['shots_allowed_pg']/11.9):.2f}x")
            st.caption(f"Lower shots allowed = stronger defense = reduced opponent xG")
        
        with tab3:
            st.markdown("##### Factor Ranking by Impact")
            
            factors = []
            
            # Home advantage
            factors.append(("Home Advantage", "15%", "League standard boost"))
            
            # Form difference
            form_diff = home_data['form_last_5'] - away_data['form_last_5']
            if abs(form_diff) > 1:
                impact = f"{'+" if form_diff > 0 else ''}{form_diff*2:.0f}%"
                factors.append(("Form Advantage", impact, f"{home_team} in better form"))
            
            # Injuries
            if away_data['defenders_out'] > 2:
                factors.append(("Opponent Injuries", f"-{away_data['defenders_out']*10}%", f"{away_data['defenders_out']} key defenders out"))
            
            if home_data['defenders_out'] > 2:
                factors.append(("Team Injuries", f"-{home_data['defenders_out']*10}%", f"{home_team} defensive issues"))
            
            # Display factors
            for factor, impact, reason in factors:
                col1, col2, col3 = st.columns([2, 1, 3])
                with col1:
                    st.write(f"• {factor}")
                with col2:
                    st.write(f"`{impact}`")
                with col3:
                    st.caption(reason)

def display_market_intelligence(probabilities, market_odds, home_team, away_team):
    """Show why model differs from market"""
    
    market_home_prob = 1 / market_odds['home_win']
    model_home_prob = probabilities['home_win']
    difference = model_home_prob - market_home_prob
    
    if abs(difference) > 0.15:  # Significant difference
        with st.expander("🔍 **Market Intelligence Alert**", expanded=False):
            st.warning(f"**Significant Model-Market Discrepancy**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Market Implied", f"{market_home_prob*100:.1f}%")
            with col2:
                st.metric("Model Prediction", f"{model_home_prob*100:.1f}%", 
                         f"{'+' if difference > 0 else ''}{difference*100:.1f}%")
            
            st.caption(f"**Potential Reasons**:")
            if model_home_prob < market_home_prob:
                st.write("• Market may be overvaluing home team reputation")
                st.write("• Recent high-profile results influencing odds")
                st.write("• Public betting bias toward favorites")
            else:
                st.write("• Market undervaluing form/injury factors")
                st.write("• Recent underperformance affecting odds")
                st.write("• Value opportunity detected")

def explain_form_string(form_string):
    """Briefly explain form string conversion"""
    if not form_string or len(form_string) < 3:
        return "Insufficient form data"
    
    # Simple explanation
    recent = form_string[-3:] if len(form_string) >= 3 else form_string
    w_count = recent.count('W')
    d_count = recent.count('D')
    l_count = recent.count('L')
    
    return f"Recent form: {w_count}W {d_count}D {l_count}L in last {len(recent)}"

# In your ProfessionalPredictionEngine class, update get_betting_recommendations:
def get_betting_recommendations(self, probabilities, binary_preds, market_odds, confidence, league_stats):
    """Get betting recommendations with brief reasoning"""
    recommendations = []
    
    predicted_outcome = self.get_predicted_outcome(probabilities)
    
    # Match result recommendations
    ev_home = self.calculate_expected_value(probabilities['home_win'], market_odds['home_win'])
    ev_draw = self.calculate_expected_value(probabilities['draw'], market_odds['draw'])
    ev_away = self.calculate_expected_value(probabilities['away_win'], market_odds['away_win'])
    
    if predicted_outcome == 'HOME' and ev_home > 0.10:
        reason = f"Model sees {probabilities['home_win']*100:.0f}% vs market {1/market_odds['home_win']*100:.0f}%"
        recommendations.append({
            'market': 'Match Result', 'prediction': 'HOME', 'probability': probabilities['home_win'],
            'market_odds': market_odds['home_win'], 'fair_odds': 1/probabilities['home_win'],
            'ev': ev_home, 'reason': reason, 'confidence': confidence
        })
    
    elif predicted_outcome == 'AWAY' and ev_away > 0.10:
        reason = f"Model sees {probabilities['away_win']*100:.0f}% vs market {1/market_odds['away_win']*100:.0f}%"
        recommendations.append({
            'market': 'Match Result', 'prediction': 'AWAY', 'probability': probabilities['away_win'],
            'market_odds': market_odds['away_win'], 'fair_odds': 1/probabilities['away_win'],
            'ev': ev_away, 'reason': reason, 'confidence': confidence
        })
    
    elif predicted_outcome == 'DRAW' and ev_draw > 0.10:
        reason = f"Model sees {probabilities['draw']*100:.0f}% vs market {1/market_odds['draw']*100:.0f}%"
        recommendations.append({
            'market': 'Match Result', 'prediction': 'DRAW', 'probability': probabilities['draw'],
            'market_odds': market_odds['draw'], 'fair_odds': 1/probabilities['draw'],
            'ev': ev_draw, 'reason': reason, 'confidence': confidence
        })
    
    # Over/Under with brief reasoning
    over_prob = probabilities['over_25']
    under_prob = probabilities['under_25']
    ev_over = self.calculate_expected_value(over_prob, market_odds['over_25'])
    ev_under = self.calculate_expected_value(under_prob, market_odds['under_25'])
    
    league_over_avg = league_stats['over_25_pct']
    
    if over_prob > league_over_avg and ev_over > 0.10:
        reason = f"High-scoring trend ({over_prob*100:.0f}% vs {league_over_avg*100:.0f}% avg)"
        recommendations.append({
            'market': 'Over/Under 2.5', 'prediction': 'OVER', 'probability': over_prob,
            'market_odds': market_odds['over_25'], 'fair_odds': 1/over_prob,
            'ev': ev_over, 'reason': reason, 'confidence': abs(over_prob - league_over_avg) * 100
        })
    elif under_prob > (1 - league_over_avg) and ev_under > 0.10:
        reason = f"Defensive matchup ({under_prob*100:.0f}% vs {(1-league_over_avg)*100:.0f}% avg)"
        recommendations.append({
            'market': 'Over/Under 2.5', 'prediction': 'UNDER', 'probability': under_prob,
            'market_odds': market_odds['under_25'], 'fair_odds': 1/under_prob,
            'ev': ev_under, 'reason': reason, 'confidence': abs(under_prob - (1 - league_over_avg)) * 100
        })
    
    # BTTS with brief reasoning
    btts_yes_prob = probabilities['btts_yes']
    btts_no_prob = probabilities['btts_no']
    ev_btts_yes = self.calculate_expected_value(btts_yes_prob, market_odds['btts_yes'])
    ev_btts_no = self.calculate_expected_value(btts_no_prob, market_odds['btts_no'])
    
    league_btts_avg = league_stats['btts_pct']
    
    if btts_yes_prob > league_btts_avg and ev_btts_yes > 0.10:
        reason = f"Both teams scoring likely ({btts_yes_prob*100:.0f}% vs {league_btts_avg*100:.0f}% avg)"
        recommendations.append({
            'market': 'Both Teams to Score', 'prediction': 'YES', 'probability': btts_yes_prob,
            'market_odds': market_odds['btts_yes'], 'fair_odds': 1/btts_yes_prob,
            'ev': ev_btts_yes, 'reason': reason, 'confidence': abs(btts_yes_prob - league_btts_avg) * 100
        })
    elif btts_no_prob > (1 - league_btts_avg) and ev_btts_no > 0.10:
        reason = f"Clean sheet likely ({btts_no_prob*100:.0f}% vs {(1-league_btts_avg)*100:.0f}% avg)"
        recommendations.append({
            'market': 'Both Teams to Score', 'prediction': 'NO', 'probability': btts_no_prob,
            'market_odds': market_odds['btts_no'], 'fair_odds': 1/btts_no_prob,
            'ev': ev_btts_no, 'reason': reason, 'confidence': abs(btts_no_prob - (1 - league_btts_avg)) * 100
        })
    
    return recommendations

# In your main() function, update the results section:
if 'result' in st.session_state:
    result = st.session_state['result']
    recommendations = st.session_state['recommendations']
    market_odds = st.session_state['market_odds']
    
    st.markdown("---")
    st.markdown("# 📊 Prediction Results")
    
    # Match header
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown(f"<h2 style='text-align: center;'>🏠 {home_team}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h2 style='text-align: center;'>✈️ {away_team}</h2>", unsafe_allow_html=True)
    
    # Model vs Market Comparison
    st.markdown("---")
    st.markdown("### 📈 Model vs Market View")
    
    fig = engine.display_odds_comparison(result['probabilities'], market_odds)
    st.plotly_chart(fig, use_container_width=True)
    
    # Main predictions in cards (EXACTLY as you had)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        home_win_prob = result['probabilities']['home_win'] * 100
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Home Win Probability", f"{home_win_prob:.1f}%", 
                 f"Fair odds: {1/result['probabilities']['home_win']:.2f}" if result['probabilities']['home_win'] > 0 else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        draw_prob = result['probabilities']['draw'] * 100
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Draw Probability", f"{draw_prob:.1f}%",
                 f"Fair odds: {1/result['probabilities']['draw']:.2f}" if result['probabilities']['draw'] > 0 else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        away_win_prob = result['probabilities']['away_win'] * 100
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Away Win Probability", f"{away_win_prob:.1f}%",
                 f"Fair odds: {1/result['probabilities']['away_win']:.2f}" if result['probabilities']['away_win'] > 0 else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Predicted score card
    st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
    st.markdown(f"### 🎯 Predicted Score: **{result['predicted_score']}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Expected goals cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Home Expected Goals", f"{result['expected_goals']['home']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Away Expected Goals", f"{result['expected_goals']['away']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add transparency section (new)
    display_data_transparency(home_data, away_data, home_team, away_team)
    
    # Binary predictions (your original cards)
    st.markdown("---")
    st.markdown("### 🔍 Binary Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        btts_pred = result['binary_predictions']['btts']
        if btts_pred['prediction'] == 'YES':
            st.markdown('<div class="yes-card">', unsafe_allow_html=True)
            st.markdown(f"#### ✅ Both Teams to Score: **YES**")
            st.metric("Probability", f"{btts_pred['probability']*100:.1f}%")
            st.metric("League Average", f"{btts_pred['league_avg']*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-card">', unsafe_allow_html=True)
            st.markdown(f"#### ❌ Both Teams to Score: **NO**")
            st.metric("Probability", f"{btts_pred['probability']*100:.1f}%")
            st.metric("League Average", f"{(1-btts_pred['league_avg'])*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        over_under_pred = result['binary_predictions']['over_under']
        if over_under_pred['prediction'] == 'OVER':
            st.markdown('<div class="yes-card">', unsafe_allow_html=True)
            st.markdown(f"#### ✅ Over 2.5 Goals: **YES**")
            st.metric("Probability", f"{over_under_pred['probability']*100:.1f}%")
            st.metric("League Average", f"{over_under_pred['league_avg']*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-card">', unsafe_allow_html=True)
            st.markdown(f"#### ❌ Over 2.5 Goals: **NO**")
            st.metric("Probability", f"{over_under_pred['probability']*100:.1f}%")
            st.metric("League Average", f"{(1-over_under_pred['league_avg'])*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add market intelligence (only when significant difference)
    display_market_intelligence(result['probabilities'], market_odds, home_team, away_team)
    
    # Betting recommendations (your original format)
    st.markdown("---")
    st.markdown("### 💰 Betting Recommendations")
    
    if recommendations:
        for rec in recommendations:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{rec['market']} - {rec['prediction']}**")
                st.markdown(f"*{rec['reason']}*")
            
            with col2:
                ev_pct = rec['ev'] * 100
                if ev_pct > 0:
                    st.markdown(f'<div class="value-positive">+{ev_pct:.1f}% EV</div>', unsafe_allow_html=True)
                    st.markdown(f"Odds: {rec['market_odds']:.2f}")
                else:
                    st.markdown(f'<div class="value-negative">{ev_pct:.1f}% EV</div>', unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("No strong betting recommendations based on current market odds.")
    
    # Key factors (your original format)
    st.markdown("### 🔑 Key Factors Influencing Prediction")
    
    for factor in result['key_factors']:
        st.markdown(f'<span class="factor-badge">{factor}</span>', unsafe_allow_html=True)
    
    # Scoreline probabilities (your original format)
    st.markdown("---")
    st.markdown("### 📊 Most Likely Scorelines")
    
    scorelines = result['scoreline_probabilities']
    score_df = pd.DataFrame(list(scorelines.items()), columns=['Scoreline', 'Probability'])
    score_df['Probability'] = score_df['Probability'] * 100
    
    fig = go.Figure(data=[
        go.Bar(x=score_df['Scoreline'], y=score_df['Probability'],
               marker_color='#4ECDC4')
    ])
    
    fig.update_layout(
        title="Scoreline Probabilities",
        xaxis_title="Scoreline",
        yaxis_title="Probability (%)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Confidence (your original format)
    st.markdown("---")
    confidence_pct = result['confidence'] * 100
    
    if confidence_pct > 70:
        st.markdown('<div class="confidence-high">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
        st.markdown("High confidence prediction")
        st.markdown('</div>', unsafe_allow_html=True)
    elif confidence_pct > 50:
        st.markdown('<div class="confidence-medium">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
        st.markdown("Medium confidence prediction")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="confidence-low">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 Model Confidence: **{confidence_pct:.1f}%**")
        st.markdown("Low confidence prediction - consider with caution")
        st.markdown('</div>', unsafe_allow_html=True)
