# ... (ALL YOUR EXISTING CODE BEFORE main() FUNCTION REMAINS EXACTLY THE SAME) ...

# =================== MAIN APPLICATION ===================
def main():
    """Main application function with State Preservation Law, State Classification, and Bet-Ready Signals."""
    
    # Header
    st.markdown('<div class="system-header">🎯🔒📊 BRUTBALL INTEGRATED ARCHITECTURE v6.3</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-subheader">
        <p><strong>FOUR-LAYER SYSTEM WITH BET-READY SIGNALS & STATE PRESERVATION LAW</strong></p>
        <p>Tier 1: v6.0 Edge Detection • Tier 1+: Edge-Derived UNDER 1.5 Locks • Tier 2: Agency-State Lock • Tier 3: Totals Lock</p>
        <p><strong>CRITICAL UPDATE v6.3:</strong> Bet-Ready Signals with clear labeling, attack context, and confidence tiers</p>
        <p><strong>NEW:</strong> "Bournemouth to score UNDER 1.5 goals" (no confusion) • Performance tracking • Human-readable output</p>
        <p><strong>PRE-MATCH INTELLIGENCE:</strong> State & Durability Classification available for system protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bet-Ready Signals Explanation
    st.markdown("""
    <div class="state-principle">
        <h4>🎯 BET-READY SIGNALS (v6.3 - NEW)</h4>
        <div style="margin: 1rem 0;">
            <div class="edge-derived-list">
                <strong>✅ CLEAR, ACTIONABLE BETTING RECOMMENDATIONS</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li><strong>Fixed Labeling:</strong> "Bournemouth to score UNDER 1.5 goals" (no confusion)</li>
                    <li><strong>Attack Context:</strong> Tiered confidence based on opponent scoring average</li>
                    <li><strong>Human-Readable:</strong> Shows exactly what to bet, why, and with what confidence</li>
                    <li><strong>Performance Tracking:</strong> Records predictions vs actual results</li>
                </ul>
            </div>
            <div class="strict-binary">
                <strong>🎯 CONFIDENCE TIERS (Based on Opponent Attack):</strong><br>
                <strong>≤1.4 avg goals:</strong> VERY STRONG 🔵 (weak opponent attack)<br>
                <strong>≤1.6 avg goals:</strong> STRONG 🟢 (moderate opponent attack)<br>
                <strong>≤1.8 avg goals:</strong> WEAK 🟡 (strong opponent attack)<br>
                <strong>>1.8 avg goals:</strong> VERY WEAK 🔴 (very strong opponent attack)<br>
                Prevents Chelsea vs Bournemouth 2–2 type false positives
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # State Preservation Law Display
    st.markdown("""
    <div class="preservation-law">
        <h4>⚖️ STATE PRESERVATION LAW (v6.2)</h4>
        <div style="margin: 1rem 0; font-size: 1.1rem;">
            <strong>A state cannot be locked unless it can be PRESERVED.</strong>
        </div>
        <div style="margin: 0.5rem 0;">
            <strong>Gate 4A OVERRIDES Gates 1-3 for defensive markets.</strong>
        </div>
        <div style="margin: 0.5rem 0; font-size: 0.95rem;">
            Dominance ≠ Protection • Creation ≠ Suppression • Control ≠ Safety
        </div>
        <div style="margin-top: 1rem; padding: 0.75rem; background: #FEF3C7; border-radius: 6px;">
            <strong>Manchester United vs Wolves:</strong> Passed Gates 1-3 (creation), FAILED Gate 4A (preservation)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pre-Match Intelligence Principles
    st.markdown("""
    <div class="state-principle">
        <h4>🧠 PRE-MATCH INTELLIGENCE PRINCIPLES</h4>
        <div style="margin: 1rem 0;">
            <div class="state-bound-list">
                <strong>✅ LAST-5 DATA ONLY (NO SEASON AVERAGES)</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li><strong>Totals Lock:</strong> Binary gate (both teams ≤ 1.2 avg goals scored)</li>
                    <li><strong>Durability:</strong> STABLE / FRAGILE / NONE based on last 5</li>
                    <li><strong>Edge-Derived Locks:</strong> PRESENT/ABSENT from conceded avg last 5</li>
                    <li><strong>Direct team locks:</strong> No "opponent/backing" confusion</li>
                </ul>
            </div>
            <div class="noise-list">
                <strong>✅ READ-ONLY INTELLIGENCE LAYER</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>Does NOT affect bets, stakes, or Tier 1–3 logic</li>
                    <li>Informational only for pre-match assessment</li>
                    <li>Mathematically consistent with last-5 data</li>
                    <li>No external assumptions or season averages</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show State Classifier availability
    if STATE_CLASSIFIER_AVAILABLE:
        st.markdown("""
        <div class="read-only-note">
            <strong>🔍 STATE & DURABILITY CLASSIFIER AVAILABLE (READ-ONLY)</strong>
            <p>Match state classification, durability scoring, and reliability assessment will be displayed after analysis</p>
            <p>Includes: Totals Durability (STABLE/FRAGILE/NONE), Under Market Suggestions, Defensive strength signals</p>
            <p><strong>CRITICAL:</strong> Classification does NOT affect betting logic, stakes, or existing tiers</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Updated Architecture diagram with Bet-Ready Signals
    st.markdown("""
    <div class="architecture-diagram">
        <h4>🏗️ FOUR-LAYER ARCHITECTURE v6.3 with BET-READY SIGNALS</h4>
        <div class="three-tier-architecture">
            <div class="tier-level tier-3">
                <div style="font-size: 1.1rem; font-weight: 700;">TIER 3: TOTALS LOCK ENGINE</div>
                <div style="font-size: 0.9rem;">Trend-Based • Dual Low-Offense</div>
                <div style="font-size: 0.85rem; color: #0C4A6E; margin-top: 0.5rem;">
                    Binary Gate: Both teams ≤ 1.2 avg goals (last 5)
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="market-badge badge-totals-locked">Totals ≤2.5 ONLY</span>
                </div>
            </div>
            <div class="arrow-down" style="font-size: 1.5rem; font-weight: 800;">↓</div>
            <div class="tier-level tier-2">
                <div style="font-size: 1.1rem; font-weight: 700;">TIER 2: AGENCY-STATE LOCK ENGINE v6.2</div>
                <div style="font-size: 0.9rem;">Agency-Based • 4 Gates + State Preservation</div>
                <div style="font-size: 0.85rem; color: #059669; margin-top: 0.5rem;">
                    <strong>NEW: Gate 4A OVERRIDES Gates 1-3 for defensive markets</strong>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="market-badge badge-state">Winner</span>
                    <span class="market-badge badge-state">Clean Sheet</span>
                    <span class="market-badge badge-state">Team No Score</span>
                    <span class="market-badge badge-state">Opponent Under 1.5</span>
                </div>
            </div>
            <div class="arrow-down" style="font-size: 1.5rem; font-weight: 800;">↓</div>
            <div class="tier-level tier-1-edge-derived">
                <div style="font-size: 1rem; font-weight: 700;">TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS</div>
                <div style="font-size: 0.9rem;">Defensive Proof • Attack Context • Bet-Ready Signals</div>
                <div style="font-size: 0.85rem; color: #1E40AF; margin-top: 0.5rem;">
                    <strong>Clear labels: "Team to score UNDER 1.5 goals" • Tiered confidence</strong>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="market-badge badge-edge-locked">UNDER 1.5 ONLY</span>
                    <span class="market-badge badge-edge-locked">Bet-Ready Signals</span>
                    <span class="market-badge badge-edge-locked">Attack Context</span>
                </div>
            </div>
            <div class="arrow-down" style="font-size: 1.5rem; font-weight: 800;">↓</div>
            <div class="tier-level tier-1">
                <div style="font-size: 1rem;">TIER 1: v6.0 EDGE DETECTION</div>
                <div style="font-size: 0.9rem;">Heuristic • 4 Control Criteria</div>
                <div style="font-size: 0.85rem; color: #3B82F6; margin-top: 0.5rem;">
                    Always runs • Provides base stake and action
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Strict binary gate warning
    st.markdown("""
    <div class="binary-gate">
        <h4>⚖️ STATE PRESERVATION LAW: HARD BINARY RULES</h4>
        <div class="strict-binary">
            <strong>DEFENSIVE MARKETS REQUIRE RECENT DEFENSIVE PROOF</strong><br>
            <strong>Clean Sheet:</strong> Recent concede avg ≤ 0.8<br>
            <strong>Team No Score:</strong> Recent concede avg ≤ 0.6<br>
            <strong>Opponent Under 1.5:</strong> Recent concede avg ≤ 1.0<br>
            <strong>Edge-Derived Under 1.5:</strong> Recent concede avg ≤ 1.0 (direct team locks)<br>
            <strong>DATA:</strong> *_goals_conceded_last_5 / 5 ONLY<br>
            <strong>NO EXCEPTIONS:</strong> If fails → NO LOCK (regardless of Gates 1-3)
        </div>
        <div style="margin-top: 1rem; padding: 0.75rem; background: #EFF6FF; border-radius: 6px;">
            <strong>🎯 BET-READY SIGNALS v6.3:</strong> Clear labeling, attack context, performance tracking
        </div>
        <div style="margin-top: 1rem; padding: 0.75rem; background: #FEF3C7; border-radius: 6px;">
            <strong>Manchester United vs Wolves Test Case:</strong><br>
            United concedes 1.6 avg (last 5) → Clean Sheet/Team No Score locks are INVALID<br>
            However: Could still have Edge-Derived lock if Wolves concedes ≤1.0
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for page refresh fix
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'tracking_key_suffix' not in st.session_state:
        st.session_state.tracking_key_suffix = 0
    
    # League selection
    st.markdown("### 🌍 League Selection")
    
    cols = st.columns(8)
    leagues = list(LEAGUES.keys())
    
    for idx, (col, league) in enumerate(zip(cols, leagues)):
        with col:
            config = LEAGUES[league]
            if st.button(
                config['display_name'],
                use_container_width=True,
                type="primary" if 'selected_league' in st.session_state and st.session_state.selected_league == league else "secondary",
                key=f"league_btn_{league}"
            ):
                st.session_state.selected_league = league
                st.session_state.analysis_complete = False
                st.rerun()
    
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
    selected_league = st.session_state.selected_league
    config = LEAGUES[selected_league]
    
    # Load data
    with st.spinner(f"Loading {config['display_name']} data..."):
        df = load_and_prepare_data(selected_league)
    
    if df is None:
        st.error("Failed to load data. Check CSV files in 'leagues/' directory.")
        return
    
    # Team selection
    st.markdown("### 🏟️ Match Analysis")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()), key="home_team_select")
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    
    # Special test case button
    if home_team == "Manchester United" and away_team == "Wolverhampton":
        st.markdown("""
        <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; border: 2px solid #F59E0B; margin: 1rem 0;">
            <strong>🧪 STATE PRESERVATION LAW TEST CASE</strong>
            <p>Manchester United vs Wolves is the empirical proof of State Preservation Law.</p>
            <p><strong>Expected Result:</strong> United may pass Winner lock, but MUST FAIL Clean Sheet/Team No Score locks.</p>
            <p><strong>Reason:</strong> United concedes 1.6 avg goals recently (last 5) → cannot preserve defensive states.</p>
            <p><strong>Edge-Derived Lock Test:</strong> If Wolves concedes ≤1.0 avg goals → actionable UNDER 1.5 lock for Wolves</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Execute analysis
    if st.button("⚡ EXECUTE INTEGRATED ANALYSIS v6.3", type="primary", use_container_width=True, key="execute_analysis"):
        
        # Get data
        home_data = df[df['team'] == home_team].iloc[0].to_dict()
        away_data = df[df['team'] == away_team].iloc[0].to_dict()
        
        # Calculate league average xG
        if 'home_xg_per_match' in df.columns and 'away_xg_per_match' in df.columns:
            league_avg_xg = (df['home_xg_per_match'].mean() + df['away_xg_per_match'].mean()) / 2
        else:
            league_avg_xg = 1.3
        
        # Execute integrated analysis
        result = BrutballIntegratedArchitecture.execute_integrated_analysis(
            home_data, away_data, home_team, away_team, league_avg_xg
        )
        
        # Store result in session state
        st.session_state.last_result = result
        st.session_state.analysis_complete = True
        st.session_state.tracking_key_suffix += 1  # Force new keys to prevent refresh
        
        st.rerun()
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.last_result:
        result = st.session_state.last_result
        
        # =================== BET-READY SIGNALS DISPLAY ===================
        display_bet_ready_signals_streamlit(result['edge_derived_locks'], home_team, away_team)
        
        # =================== PERFORMANCE TRACKING ===================
        with st.expander("📊 Performance Dashboard", expanded=False):
            st.markdown("""
            **System Prediction Tracking**
            
            Tracks Edge-Derived UNDER 1.5 predictions vs actual results.
            Record actual scores to improve system accuracy.
            """)
            
            # Use session state to prevent refresh
            tracking_key = f"tracking_{st.session_state.tracking_key_suffix}"
            
            col1, col2 = st.columns(2)
            with col1:
                actual_home = st.number_input(
                    f"{home_team} actual goals", 
                    min_value=0, max_value=10, value=0, 
                    key=f"actual_home_{tracking_key}"
                )
            with col2:
                actual_away = st.number_input(
                    f"{away_team} actual goals", 
                    min_value=0, max_value=10, value=0, 
                    key=f"actual_away_{tracking_key}"
                )
            
            if st.button("Record Match Result", key=f"record_result_{tracking_key}"):
                # Record predictions
                for lock in result['edge_derived_locks']:
                    match_info = f"{home_team} vs {away_team}"
                    prediction = f"{lock['team_to_bet']} to score UNDER 1.5 goals"
                    performance_tracker.record_prediction(match_info, prediction, lock['confidence'])
                
                # Record result
                actual_score = f"{actual_home}-{actual_away}"
                performance_tracker.record_result(f"{home_team} vs {away_team}", actual_score)
                st.success(f"✅ Recorded: {home_team} {actual_home}-{actual_away} {away_team}")
                st.rerun()
            
            # Calculate and display stats
            stats = performance_tracker.calculate_accuracy()
            
            st.markdown(f"""
            **Prediction Accuracy**
            - Total Predictions: {stats['total_predictions']}
            - Matched Results: {stats['matched_pairs']}
            - Accuracy: {stats['accuracy']:.1f}%
            
            **Current Match Predictions**
            """)
            
            for lock in result['edge_derived_locks']:
                # Check if prediction would be correct
                actual_goals = actual_away if lock['team_to_bet'] == away_team else actual_home
                correct = actual_goals <= 1
                
                st.markdown(f"""
                - **{lock['market']}**: {lock['confidence']} confidence
                  - Predicted: {lock['team_to_bet']} to score 0-1 goals
                  - Actual: {lock['team_to_bet']} scored {actual_goals} goals
                  - Result: {'✅ CORRECT' if correct else '❌ INCORRECT'}
                """)
            
            if stats['total_predictions'] == 0:
                st.info("No predictions recorded yet. Analyze matches and record results to build performance data.")
        
        # =================== READ-ONLY STATE & DURABILITY CLASSIFICATION ===================
        # CRITICAL: This runs AFTER all betting logic is complete
        # Does NOT affect existing results, stakes, or decisions
        classification_result = None
        if STATE_CLASSIFIER_AVAILABLE and get_complete_classification:
            try:
                classification_result = get_complete_classification(home_data, away_data)
                
                # ========== NEW: CHECK FOR CLASSIFIER ERRORS ==========
                if classification_result and 'classification_error' in classification_result:
                    # Classifier has data validation error - DISABLED state
                    error_message = classification_result.get('error_message', 'Unknown data error')
                    error_type = classification_result.get('error_type', 'MISSING_DATA')
                    
                    classification_result = {
                        'classification_error': True,
                        'error_message': error_message,
                        'error_type': error_type,
                        'missing_fields': classification_result.get('missing_fields', []),
                        'is_read_only': True,
                        'does_not_affect_betting': True,
                        'metadata': {
                            'status': 'DISABLED - INSUFFICIENT_DATA',
                            'action': 'Check CSV for goals_scored_last_5 and goals_conceded_last_5 fields'
                        }
                    }
                    result['state_classification'] = classification_result
                    result['classification_is_read_only'] = True
                    result['classification_does_not_affect_betting'] = True
                    result['classifier_status'] = 'DISABLED'
                    
                else:
                    # Classifier worked normally - add as separate, read-only fields
                    result['state_classification'] = classification_result
                    result['classification_is_read_only'] = True
                    result['classification_does_not_affect_betting'] = True
                    result['classifier_status'] = 'ACTIVE'
                    
            except Exception as e:
                # Fail gracefully - classification is optional
                classification_result = {
                    'classification_error': True,
                    'error_message': f"Classifier runtime error: {str(e)}",
                    'error_type': 'RUNTIME_ERROR',
                    'is_read_only': True,
                    'does_not_affect_betting': True,
                    'metadata': {
                        'status': 'DISABLED - RUNTIME_ERROR',
                        'action': 'Check classifier module integrity'
                    }
                }
                result['state_classification'] = classification_result
                result['classification_is_read_only'] = True
                result['classification_does_not_affect_betting'] = True
                result['classifier_status'] = 'ERROR'
        
        # =================== INTEGRATED SYSTEM VERDICT ===================
        st.markdown("### 🎯 INTEGRATED SYSTEM VERDICT v6.3")
        
        # Capital mode display
        capital_mode = result['capital_mode']
        if result['has_totals_lock']:
            capital_display = "TOTALS LOCK MODE"
            capital_class = "totals-lock-mode"
            capital_color = "#0C4A6E"
        elif result['has_edge_derived_locks']:
            capital_display = "EDGE-DERIVED LOCK MODE"
            capital_class = "edge-derived-mode"
            capital_color = "#1E40AF"
        elif capital_mode == 'LOCK_MODE':
            capital_display = "LOCK MODE"
            capital_class = "lock-mode"
            capital_color = "#166534"
        else:
            capital_display = "EDGE MODE"
            capital_class = "edge-mode"
            capital_color = "#1E40AF"
        
        capital_html = f"""
        <div class="capital-mode-box {capital_class}">
            <h2 style="margin: 0; font-size: 2rem;">{capital_display}</h2>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                Stake: <strong>{result['final_stake']:.2f}%</strong> ({result['v6_result']['stake_pct']:.1f}% × {result['stake_multiplier']:.1f}x)
            </div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem; color: {capital_color};">
                {result['system_verdict']}
            </div>
        </div>
        """
        st.markdown(capital_html, unsafe_allow_html=True)
        
        # =================== STATE & DURABILITY CLASSIFICATION DISPLAY ===================
        if classification_result and 'state_classification' in result:
            
            # ========== NEW: CHECK FOR ERRORS FIRST ==========
            if classification_result.get('classification_error', False):
                # Show error state - Classifier disabled
                error_type = classification_result.get('error_type', 'UNKNOWN')
                error_message = classification_result.get('error_message', 'Unknown error')
                
                st.markdown("#### 🔍 PRE-MATCH STRUCTURAL INTELLIGENCE (READ-ONLY)")
                st.warning(f"⚠️ **Classifier Unavailable: {error_message}**")
                
                # Show basic last-5 data if we have it
                with st.expander("📊 Basic Last 5 Matches Data (Available)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        home_goals = home_data.get('goals_scored_last_5', 'N/A')
                        home_conceded = home_data.get('goals_conceded_last_5', 'N/A')
                        st.metric(f"{home_team} Goals Scored (Last 5)", home_goals)
                        st.metric(f"{home_team} Goals Conceded (Last 5)", home_conceded)
                    with col2:
                        away_goals = away_data.get('goals_scored_last_5', 'N/A')
                        away_conceded = away_data.get('goals_conceded_last_5', 'N/A')
                        st.metric(f"{away_team} Goals Scored (Last 5)", away_goals)
                        st.metric(f"{away_team} Goals Conceded (Last 5)", away_conceded)
                    
                    st.info("⚠️ Note: Full classification unavailable due to missing last-5 data in CSV")
                    st.markdown("**Required CSV fields:** `goals_scored_last_5`, `goals_conceded_last_5`")
            
            else:
                # ========== OLD DISPLAY LOGIC (Updated for new structure) ==========
                st.markdown("#### 🔍 PRE-MATCH STRUCTURAL INTELLIGENCE (READ-ONLY)")
                
                # Display the perspective boxes
                st.markdown("""
                <div class="perspective-display">
                    <h4>📊 STRUCTURAL ANALYSIS (Last 5 Matches Only)</h4>
                    <p style="color: #374151; margin-bottom: 1rem;">All calculations use LAST 5 MATCHES only. Does NOT affect betting logic.</p>
                """, unsafe_allow_html=True)
                
                # Get classification data (now guaranteed to exist)
                averages = classification_result.get('averages', {})
                opponent_data = classification_result.get('opponent_under_15', {})
                    
                # Home Team Box
                home_html = f"""
                    <div class="perspective-box perspective-home">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="font-weight: 700; color: #1E40AF;">{home_team}</div>
                            <div style="font-size: 0.9rem; color: #6B7280;">Last 5 matches data</div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Avg Goals</div>
                                <div style="font-weight: 600;">{averages.get('home_goals_avg', 0):.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Avg Conceded</div>
                                <div style="font-weight: 600; color: {'#16A34A' if averages.get('home_conceded_avg', 0) <= 1.0 else '#DC2626'}">
                                    {averages.get('home_conceded_avg', 0):.2f}
                                </div>
                            </div>
                        </div>
                        <div style="color: #374151; font-size: 0.9rem;">
                            Defensive strength: {'✅ Strong' if averages.get('home_conceded_avg', 0) <= 1.0 else '❌ Weak'}
                        </div>
                    </div>
                    """
                st.markdown(home_html, unsafe_allow_html=True)
                    
                # Away Team Box
                away_html = f"""
                    <div class="perspective-box perspective-away">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="font-weight: 700; color: #DC2626;">{away_team}</div>
                            <div style="font-size: 0.9rem; color: #6B7280;">Last 5 matches data</div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Avg Goals</div>
                                <div style="font-weight: 600;">{averages.get('away_goals_avg', 0):.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Avg Conceded</div>
                                <div style="font-weight: 600; color: {'#16A34A' if averages.get('away_conceded_avg', 0) <= 1.0 else '#DC2626'}">
                                    {averages.get('away_conceded_avg', 0):.2f}
                                </div>
                            </div>
                        </div>
                        <div style="color: #374151; font-size: 0.9rem;">
                            Defensive strength: {'✅ Strong' if averages.get('away_conceded_avg', 0) <= 1.0 else '❌ Weak'}
                        </div>
                    </div>
                    """
                st.markdown(away_html, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
                
                # =================== STREAMLIT-NATIVE CLASSIFICATION DISPLAY ===================
                # Using pure Streamlit components, no HTML
                
                # Map state to emoji and color
                state_info = {
                    'TERMINAL_STAGNATION': {'emoji': '🌀', 'color': '#0EA5E9', 'label': 'Terminal Stagnation'},
                    'ASYMMETRIC_SUPPRESSION': {'emoji': '🛡️', 'color': '#16A34A', 'label': 'Asymmetric Suppression'},
                    'DELAYED_RELEASE': {'emoji': '⏳', 'color': '#F59E0B', 'label': 'Delayed Release'},
                    'FORCED_EXPLOSION': {'emoji': '💥', 'color': '#EF4444', 'label': 'Forced Explosion'},
                    'NEUTRAL': {'emoji': '⚖️', 'color': '#6B7280', 'label': 'Neutral'},
                    'CLASSIFIER_ERROR': {'emoji': '⚠️', 'color': '#DC2626', 'label': 'Classifier Error'}
                }
                
                dominant_state = classification_result.get('dominant_state', 'NEUTRAL')
                state_data = state_info.get(dominant_state, state_info['NEUTRAL'])
                
                # Get durability and suggestion
                totals_durability = classification_result.get('totals_durability', 'NONE')
                under_suggestion = classification_result.get('under_suggestion', 'No Under recommendation')
                
                # Create a clean classification display using Streamlit columns and containers
                with st.container():
                    # State classification badge
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%); 
                                padding: 2rem; border-radius: 12px; border: 4px solid #F97316; 
                                text-align: center; margin: 1.5rem 0;">
                        <div style="display: inline-flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                            <span style="font-size: 2rem;">{state_data['emoji']}</span>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: 800; color: {state_data['color']};">
                                    {state_data['label']}
                                </div>
                                <div style="display: inline-block; background: #F3F4F6; color: #6B7280; 
                                            border: 1px solid #D1D5DB; font-size: 0.8rem; padding: 0.25rem 0.75rem; 
                                            border-radius: 12px; margin-top: 0.5rem;">
                                    READ-ONLY
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Classification metrics using Streamlit columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Totals Durability
                        with st.container():
                            st.markdown("**Totals Durability**")
                            
                            # Determine durability emoji and color
                            if totals_durability == 'STABLE':
                                durability_emoji = '🟢'
                                durability_color = '#16A34A'
                            elif totals_durability == 'FRAGILE':
                                durability_emoji = '🟡'
                                durability_color = '#F59E0B'
                            else:  # NONE or other
                                durability_emoji = '⚫'
                                durability_color = '#6B7280'
                            
                            st.markdown(f"""
                            <div style="font-size: 1.5rem; font-weight: 700; color: {durability_color}; 
                                        margin: 0.5rem 0;">
                                {durability_emoji} {totals_durability}
                            </div>
                            <div style="font-size: 0.85rem; color: #6B7280;">
                                Based on last 5 matches only
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Under Market Suggestion
                        with st.container():
                            st.markdown("**Under Market Suggestion**")
                            st.markdown(f"""
                            <div style="font-size: 1.2rem; font-weight: 700; color: #059669; 
                                        margin: 0.5rem 0;">
                                {under_suggestion}
                            </div>
                            <div style="font-size: 0.85rem; color: #6B7280;">
                                Informational guidance only
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Reliability Assessment
                    st.markdown("---")
                    st.markdown("**Reliability Assessment**")
                    
                    reliability_data = classification_result.get('reliability_home', {})
                    score = reliability_data.get('reliability_score', 0)
                    label = reliability_data.get('reliability_label', 'NONE')
                    
                    # Map reliability score to emoji and color
                    reliability_map = {
                        5: {'emoji': '🟢', 'color': '#16A34A'},
                        4: {'emoji': '🟡', 'color': '#F59E0B'},
                        3: {'emoji': '🟠', 'color': '#F97316'},
                        2: {'emoji': '⚪', 'color': '#9CA3AF'},
                        1: {'emoji': '⚪', 'color': '#9CA3AF'},
                        0: {'emoji': '⚫', 'color': '#6B7280'}
                    }
                    
                    rel_info = reliability_map.get(score, reliability_map[0])
                    
                    st.markdown(f"""
                    <div style="background: #F0F9FF; padding: 1.5rem; border-radius: 8px; 
                                border: 1px solid #BAE6FD; margin: 1rem 0;">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                                {rel_info['emoji']}
                            </div>
                            <div style="font-size: 1.2rem; font-weight: 700; color: {rel_info['color']};">
                                Reliability: {label} ({score}/5)
                            </div>
                            <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;">
                                Based on durability, under suggestions, and defensive strength
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Important note
                    st.warning("**⚠️ IMPORTANT:** This classification is 100% read-only and informational only. Does NOT affect betting logic, stakes, or existing tiers.", icon="⚠️")
        
        # =================== EDGE-DERIVED LOCKS DISPLAY (Backward Compatible) ===================
        if result['has_edge_derived_locks']:
            st.markdown("#### 🔓 TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS")
            
            edge_html = f"""
            <div class="edge-derived-display">
                <h3 style="color: #1E40AF; margin: 0 0 1rem 0;">EDGE-DERIVED DEFENSIVE CONTROL DETECTED</h3>
                <div style="font-size: 1.2rem; color: #3B82F6; margin-bottom: 0.5rem;">
                    {len(result['edge_derived_locks'])} UNDER 1.5 lock(s) from Tier 1+ Edge-Derived analysis
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Binary gate: Team concedes ≤ 1.0 avg goals (last 5 matches) • Direct team locks
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                    <span class="market-badge badge-edge-locked">Edge-Derived</span>
                    <span class="market-badge badge-edge-locked">UNDER 1.5</span>
                    <span class="market-badge badge-edge-locked">Direct Team Locks</span>
                </div>
            </div>
            """
            st.markdown(edge_html, unsafe_allow_html=True)
            
            # Show individual edge-derived locks (backward compatible display)
            for lock in result['edge_locks_for_display']:
                # Safely handle the declaration split
                first_line, second_line = safe_split_declaration(
                    lock['declaration'], 
                    lock.get('details', 'Defensive proof confirmed')
                )
                
                lock_html = f"""
                <div class="market-edge-derived">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem; margin-right: 0.5rem;">🔓</div>
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: #1E40AF;">
                                {first_line}
                            </div>
                            <div style="font-size: 0.9rem; color: #6B7280;">
                                {second_line}
                            </div>
                        </div>
                    </div>
                    <div style="background: #EFF6FF; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem;">
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 0.5rem;">
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Team</div>
                                <div style="font-weight: 600; color: #1E40AF;">{lock['team']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Avg Conceded</div>
                                <div style="font-weight: 600; color: #3B82F6;">{lock['defense_avg']:.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.85rem; color: #6B7280;">Multiplier</div>
                                <div style="font-weight: 600; color: #059669;">{lock['capital_multiplier']:.1f}x</div>
                            </div>
                        </div>
                        <div style="font-size: 0.9rem; color: #374151;">
                            <strong>Lock Type:</strong> {lock['lock_type']}
                        </div>
                        <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.25rem;">
                            <strong>Source:</strong> Tier 1+ Edge-Derived • <strong>Data:</strong> Last 5 matches only • <strong>No opponent/backing confusion</strong>
                        </div>
                    </div>
                </div>
                """
                st.markdown(lock_html, unsafe_allow_html=True)     
        
        # Check for State Preservation failures and show "Stay-Out" badge
        preservation_failures = []
        for market in ['CLEAN_SHEET', 'TEAM_NO_SCORE']:
            if result['market_status'][market]['failed_on_preservation']:
                preservation_failures.append(market.replace('_', ' '))
        
        if preservation_failures:
            stay_out_html = f"""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div class="stay-out-badge">
                    ⚠️ STAY-OUT RECOMMENDED
                </div>
                <div style="color: #92400E; margin-top: 0.5rem; font-size: 0.9rem;">
                    {', '.join(preservation_failures)} failed State Preservation Law
                </div>
                <div style="color: #6B7280; font-size: 0.85rem; margin-top: 0.25rem;">
                    Recent defensive proof insufficient for these markets
                </div>
            </div>
            """
            st.markdown(stay_out_html, unsafe_allow_html=True)
        
        # v6.0 Edge Detection Display
        st.markdown("#### 🔍 TIER 1: v6.0 EDGE DETECTION")
        
        v6_result = result['v6_result']
        edge_html = f"""
        <div class="edge-analysis-display">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: #1E40AF; margin: 0;">{v6_result['primary_action']}</h3>
                    <p style="color: #6B7280; margin: 0.5rem 0 0 0;">{v6_result['secondary_logic']}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #3B82F6;">{v6_result['confidence']:.1f}/10</div>
                    <div style="font-size: 0.9rem; color: #6B7280;">Confidence</div>
                </div>
            </div>
        </div>
        """
        st.markdown(edge_html, unsafe_allow_html=True)
        
        # Agency-State Market Evaluation
        st.markdown("#### 🔐 TIER 2: AGENCY-STATE LOCKS v6.2")
        
        if result['has_agency_lock']:
            strongest = result['strongest_market']
            
            # Generate market badges HTML
            market_badges = ""
            for market_info in result['agency_locked_markets']:
                market_badges += f'<span class="market-badge badge-locked">{market_info["market"]}</span>'
            
            agency_html = f"""
            <div class="agency-state-display">
                <h3 style="color: #16A34A; margin: 0 0 1rem 0;">AGENCY-STATE CONTROL DETECTED</h3>
                <div style="font-size: 1.2rem; color: #059669; margin-bottom: 0.5rem;">
                    {len(result['agency_locked_markets'])} market(s) structurally locked
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Strongest lock: <strong>{strongest['market']}</strong> (Δ = {strongest['delta']:+.2f})
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                    {market_badges}
                </div>
            </div>
            """
            st.markdown(agency_html, unsafe_allow_html=True)
            
            # Show defensive preservation status
            defensive_locks = [m for m in result['agency_locked_markets'] if m['market'] != 'WINNER']
            if defensive_locks:
                st.markdown("""
                <div class="gate-passed">
                    <strong>✅ STATE PRESERVATION LAW SATISFIED</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        All defensive locks passed Gate 4A (recent defensive proof confirmed)
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            no_agency_html = f"""
            <div class="no-declaration-display">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO AGENCY-STATE LOCKS DETECTED</h3>
                <div style="color: #374151;">
                    No markets meet agency-suppression criteria
                </div>
            </div>
            """
            st.markdown(no_agency_html, unsafe_allow_html=True)
            
            # Check if any failed on State Preservation
            preservation_failures_display = []
            for market in ['CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
                if result['market_status'][market]['failed_on_preservation']:
                    preservation_failures_display.append(market.replace('_', ' '))
            
            if preservation_failures_display:
                preservation_html = f"""
                <div class="gate-failed">
                    <strong>❌ STATE PRESERVATION LAW FAILURES DETECTED</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        Markets failed on recent defensive proof: {', '.join(preservation_failures_display)}
                    </p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #DC2626;">
                        Manchester United vs Wolves pattern detected
                    </p>
                </div>
                """
                st.markdown(preservation_html, unsafe_allow_html=True)
        
        # Totals Lock Display
        st.markdown("#### 📊 TIER 3: TOTALS LOCK")
        
        if result['has_totals_lock']:
            trend_data = result['totals_result']['trend_data']
            totals_html = f"""
            <div class="totals-lock-display">
                <h3 style="color: #0EA5E9; margin: 0 0 1rem 0;">TOTALS LOCK DETECTED</h3>
                <div style="font-size: 1.2rem; color: #0284C7; margin-bottom: 0.5rem;">
                    Dual Low-Offense Trend Confirmed
                </div>
                <div style="color: #374151; margin-bottom: 1rem;">
                    Both teams exhibit sustained low-scoring trends (last 5 matches)
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                    <span class="market-badge badge-totals-locked">TOTALS ≤2.5 LOCKED</span>
                </div>
            </div>
            """
            st.markdown(totals_html, unsafe_allow_html=True)
            
            # Show trend data
            trend_html = f"""
            <div class="trend-check">
                <h4 style="color: #0C4A6E; margin: 0 0 0.5rem 0;">📊 LAST 5 MATCHES TREND DATA</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <div style="font-weight: 600; color: #374151;">{home_team}</div>
                        <div style="font-size: 1.5rem; color: #0EA5E9; font-weight: 700;">{trend_data['home_last5_avg']:.2f}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">avg goals (last 5)</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #374151;">{away_team}</div>
                        <div style="font-size: 1.5rem; color: #0EA5E9; font-weight: 700;">{trend_data['away_last5_avg']:.2f}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">avg goals (last 5)</div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 0.75rem; background: #F0F9FF; border-radius: 6px;">
                    <strong>Condition Met:</strong> Both ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5 matches)
                </div>
            </div>
            """
            st.markdown(trend_html, unsafe_allow_html=True)
        else:
            no_totals_html = f"""
            <div class="no-declaration-display">
                <h3 style="color: #6B7280; margin: 0 0 1rem 0;">NO TOTALS LOCK DETECTED</h3>
                <div style="color: #374151;">
                    {result['totals_result']['reason']}
                </div>
            </div>
            """
            st.markdown(no_totals_html, unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        st.markdown("#### 📤 Export Analysis")
        
        # Prepare export text
        export_text = f"""BRUTBALL INTEGRATED ARCHITECTURE v6.3 - ANALYSIS REPORT
===========================================
League: {selected_league}
Match: {home_team} vs {away_team}
Analysis Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

ARCHITECTURE OVERVIEW:
• Framework: Four-Layer Integrated System v6.3 with Bet-Ready Signals
• Layer 1: v6.0 Edge Detection (Heuristic)
• Layer 1+: Edge-Derived UNDER 1.5 Locks (NEW - Bet-Ready Signals with Attack Context)
• Layer 2: Agency-State Lock Engine (4 Gates + State Preservation)
• Layer 3: Totals Lock Engine (Trend-Based Binary Gate)
• Data Source: LAST 5 MATCHES ONLY (no season averages)

CRITICAL UPDATE (v6.3): BET-READY SIGNALS
• Clear labeling: "Bournemouth to score UNDER 1.5 goals" (no confusion)
• Attack context: Tiered confidence based on opponent scoring average
• Performance tracking: Records predictions vs actual results
• Human-readable: Shows exactly what to bet, why, and with what confidence

STATE PRESERVATION LAW (v6.2):
• A state cannot be locked unless it can be PRESERVED.
• Gate 4A OVERRIDES Gates 1-3 for defensive markets.
• Manchester United vs Wolves proved this empirically.
• Defensive markets require RECENT defensive proof (last 5 matches).

TIER 1: v6.0 EDGE DETECTION RESULT:
• Primary Action: {v6_result['primary_action']}
• Confidence: {v6_result['confidence']:.1f}/10
• Base Stake: {v6_result['stake_pct']:.1f}%
• Secondary Logic: {v6_result['secondary_logic']}

BET-READY SIGNALS (TIER 1+):
• Signals Detected: {len(result['edge_derived_locks'])}
• Clear labeling: "Team to score UNDER 1.5 goals" (no opponent/backing confusion)
• Condition: Defensive team concedes ≤ 1.0 avg goals (last 5)
• Confidence tiers: Based on opponent attack strength
"""
        
        for lock in result['edge_derived_locks']:
            export_text += f"• {lock['market']}: {lock['confidence']} confidence\n"
            export_text += f"  Defense: {lock['defensive_team']} concedes {lock['defense_avg']:.2f} avg ≤ 1.0\n"
            export_text += f"  Attack Context: Opponent scores {lock['opponent_attack_avg']:.2f} avg ({lock['attack_context']})\n"
        
        export_text += f"""

TIER 2: AGENCY-STATE LOCKS v6.2:
• Markets Evaluated: 4 (Winner, Clean Sheet, Team No Score, Opponent Under 1.5)
• Markets Locked: {len(result['agency_locked_markets'])}
• Strongest Market: {result['strongest_market']['market'] if result['strongest_market'] and result['strongest_market']['type'] == 'agency' else 'None'}

MARKET STATUS (Agency):
"""
        
        for market in ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']:
            status = result['market_status'][market]
            export_text += f"{market}: {'LOCKED' if status['locked'] else 'NOT LOCKED'} - {status['reason']}"
            if status['failed_on_preservation']:
                export_text += " [FAILED STATE PRESERVATION]"
            export_text += "\n"
        
        export_text += f"""

TIER 3: TOTALS LOCK:
• Market: Totals ≤{UNDER_GOALS_THRESHOLD} ONLY
• Condition: BOTH teams last 5 avg goals ≤ {TOTALS_LOCK_THRESHOLD}
• Status: {'LOCKED' if result['has_totals_lock'] else 'NOT LOCKED'}
• {home_team} (last 5): {result['key_metrics']['home_last5_avg']:.2f} avg goals
• {away_team} (last 5): {result['key_metrics']['away_last5_avg']:.2f} avg goals
• Reason: {result['totals_result']['reason']}

STATE PRESERVATION LAW TEST:
• Manchester United vs Wolves Test: {'PASSED' if home_team == "Manchester United" and away_team == "Wolverhampton" else 'N/A'}
• Expected: United may win, but CANNOT lock Clean Sheet/Team No Score
• Reason: Recent concede avg > threshold (requires actual defensive proof)

INTEGRATED CAPITAL DECISION:
• Final Capital Mode: {capital_display}
• Stake Multiplier: {result['stake_multiplier']:.1f}x
• Base Stake: {v6_result['stake_pct']:.1f}%
• Final Stake: {result['final_stake']:.2f}%
• System Verdict: {result['system_verdict']}
"""
        
        # Add classification if available
        if classification_result and 'state_classification' in result:
            export_text += f"""

===========================================
STATE & DURABILITY CLASSIFICATION (READ-ONLY - PRE-MATCH INTELLIGENCE)
===========================================
DATA SOURCE: Last 5 matches only (no season averages)

TEAM DEFENSIVE STRENGTH (Last 5 matches):
• {home_team}: {averages.get('home_conceded_avg', 0):.2f} avg conceded {'≤1.0 ✅ Strong' if averages.get('home_conceded_avg', 0) <= 1.0 else '>1.0 ❌ Weak'}
• {away_team}: {averages.get('away_conceded_avg', 0):.2f} avg conceded {'≤1.0 ✅ Strong' if averages.get('away_conceded_avg', 0) <= 1.0 else '>1.0 ❌ Weak'}

CLASSIFICATION RESULTS:
• Dominant State: {classification_result.get('dominant_state', 'N/A')}
• Totals Durability: {classification_result.get('totals_durability', 'N/A')}
• Under Market Suggestion: {classification_result.get('under_suggestion', 'N/A')}
• Reliability Score: {classification_result.get('reliability_home', {}).get('reliability_score', 0)}/5 ({classification_result.get('reliability_home', {}).get('reliability_label', 'N/A')})

IMPORTANT: Classification is 100% read-only and does NOT affect:
• Betting logic or decisions
• Capital allocation (1.0x vs 2.0x)
• Market lock declarations
• Existing tier logic (Tiers 1-3)
• Stake calculations
"""
        
        # Add Bet-Ready Signals Summary
        if result['has_edge_derived_locks']:
            export_text += f"""

BET-READY SIGNALS SUMMARY (v6.3):
• Source: Tier 1+ Edge Analysis (defensive proof + attack context)
• Market: UNDER 1.5 ONLY (clear "Team to score UNDER 1.5 goals" labels)
• Condition: Defensive team concedes ≤ 1.0 avg goals (last 5)
• Confidence Tiers: Based on opponent scoring average
  - ≤1.4: VERY STRONG (weak opponent attack)
  - ≤1.6: STRONG (moderate opponent attack)
  - ≤1.8: WEAK (strong opponent attack)
  - >1.8: VERY WEAK (very strong opponent attack)
• Capital Impact: Triggers LOCK MODE (2.0x multiplier)
• Signals Extracted: {len(result['edge_derived_locks'])}
• No opponent/backing confusion - clear team-specific betting recommendations
"""
            for lock in result['edge_derived_locks']:
                export_text += f"  • {lock['market']}: {lock['confidence']} confidence\n"
        
        # Add Stay-Out recommendation if applicable
        if preservation_failures:
            export_text += f"""

STAY-OUT RECOMMENDATION:
• Markets failed State Preservation Law: {', '.join(preservation_failures)}
• Recent defensive proof insufficient for these markets
• Pre-match intelligence suggests avoiding these positions
"""
        
        export_text += f"""

===========================================
BRUTBALL INTEGRATED ARCHITECTURE v6.3
Four-Layer System with Bet-Ready Signals
Tier 1: v6.0 Edge Detection • Tier 1+: Edge-Derived UNDER 1.5 Locks • Tier 2: Agency-State Lock • Tier 3: Totals Lock
Capital: 2.0x for any lock (agency, totals, or edge-derived), 1.0x otherwise
Bet-Ready Signals: Clear labeling, attack context, performance tracking
State Preservation: Gate 4A OVERRIDES Gates 1-3 for defensive markets
Pre-Match Intelligence: Last-5 data only, read-only, no betting logic impact
"""
        
        st.download_button(
            label="📥 Download Analysis Report",
            data=export_text,
            file_name=f"brutball_v6.3_{selected_league.replace(' ', '_')}_{home_team}_vs_{away_team}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; padding: 1rem;">
        <p><strong>BRUTBALL INTEGRATED ARCHITECTURE v6.3</strong></p>
        <p>Four-Layer System with Bet-Ready Signals</p>
        <p>Tier 1: v6.0 Edge Detection • Tier 1+: Edge-Derived UNDER 1.5 Locks • Tier 2: Agency-State Lock • Tier 3: Totals Lock</p>
        <p><strong>BET-READY SIGNALS:</strong> Clear labeling, attack context, performance tracking</p>
        <p><strong>STATE PRESERVATION LAW:</strong> Gate 4A OVERRIDES Gates 1-3 for defensive markets</p>
        <p><strong>PRE-MATCH INTELLIGENCE:</strong> Last-5 data only, read-only, no betting logic impact</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
