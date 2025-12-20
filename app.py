import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from scipy import stats

# ============================================================================
# STRESS TEST FRAMEWORK
# ============================================================================

class StressTestFramework:
    def __init__(self, engine_class):
        self.engine_class = engine_class
        self.test_results = []
        self.anomalies = []
        
    def create_mock_team_data(self, position, is_home=True, strength_factor=1.0):
        """Create realistic mock team data for testing."""
        base_data = {
            'overall_position': position,
            'team': f"Team_{position}",
            'venue': 'home' if is_home else 'away',
            'matches_played': 20,
            'home_xg_for': 25 * strength_factor if is_home else 0,
            'away_xg_for': 0 if is_home else 20 * strength_factor,
            'goals': 30 * strength_factor,
            'home_xga': 15 if is_home else 0,
            'away_xga': 0 if is_home else 18,
            'goals_conceded': 20,
            'defenders_out': random.randint(0, 2),
            'form_last_5': random.uniform(1.0, 2.0) * strength_factor,
            'motivation': random.randint(3, 5),
            'open_play_pct': 0.7,
            'set_piece_pct': 0.2,
            'counter_attack_pct': 0.1,
            'form': 'WWDLW',
            'shots_allowed_pg': 12.0,
            'home_ppg_diff': 0.5 if is_home else -0.3,
            'goals_scored_last_5': 8 * strength_factor,
            'goals_conceded_last_5': 5
        }
        return base_data
    
    def run_extreme_case_test(self, league_params):
        """Test extreme matchups."""
        engine = self.engine_class(league_params)
        
        test_cases = [
            # Case 1: Elite vs Bottom (Position 1 vs 20)
            {
                'name': 'Elite vs Bottom',
                'home': self.create_mock_team_data(1, is_home=True, strength_factor=1.5),
                'away': self.create_mock_team_data(20, is_home=False, strength_factor=0.6)
            },
            # Case 2: Two Elite Teams
            {
                'name': 'Elite vs Elite',
                'home': self.create_mock_team_data(2, is_home=True, strength_factor=1.3),
                'away': self.create_mock_team_data(3, is_home=False, strength_factor=1.3)
            },
            # Case 3: Mid-table Mediocrity
            {
                'name': 'Mid-table Clash',
                'home': self.create_mock_team_data(10, is_home=True, strength_factor=1.0),
                'away': self.create_mock_team_data(11, is_home=False, strength_factor=1.0)
            },
            # Case 4: Strong Defense vs Weak Attack
            {
                'name': 'Defensive vs Weak Attack',
                'home': self.create_mock_team_data(5, is_home=True, strength_factor=1.0),
                'away': self.create_mock_team_data(18, is_home=False, strength_factor=0.7)
            },
            # Case 5: Many Injuries
            {
                'name': 'Injury Crisis',
                'home': self.create_mock_team_data(8, is_home=True, strength_factor=1.0),
                'away': self.create_mock_team_data(9, is_home=False, strength_factor=1.0)
            }
        ]
        
        # Add extra injuries for case 5
        test_cases[4]['home']['defenders_out'] = 4
        test_cases[4]['away']['defenders_out'] = 3
        
        results = []
        for case in test_cases:
            result = engine.predict(case['home'], case['away'])
            results.append({
                'case': case['name'],
                'home_λ': result['expected_goals']['home'],
                'away_λ': result['expected_goals']['away'],
                'home_win': result['probabilities']['home_win'],
                'draw': result['probabilities']['draw'],
                'away_win': result['probabilities']['away_win'],
                'confidence': result['confidence'],
                'total_λ': result['expected_goals']['home'] + result['expected_goals']['away']
            })
            
            # Check for anomalies
            λ_diff = abs(result['expected_goals']['home'] - result['expected_goals']['away'])
            if λ_diff > 2.0 and 'Elite' not in case['name']:
                self.anomalies.append(f"Large λ diff ({λ_diff:.2f}) in {case['name']}")
            
            if result['expected_goals']['home'] > 3.0:
                self.anomalies.append(f"Very high home λ ({result['expected_goals']['home']:.2f}) in {case['name']}")
        
        return results
    
    def run_monte_carlo_calibration(self, league_params, n_simulations=1000):
        """Run Monte Carlo simulations to test calibration."""
        engine = self.engine_class(league_params)
        
        calibration_data = []
        for _ in range(n_simulations):
            # Random team positions
            home_pos = random.randint(1, 20)
            away_pos = random.randint(1, 20)
            
            # Create random strength factors
            home_strength = 1.0 + (1 - home_pos/20) * 0.5
            away_strength = 1.0 + (1 - away_pos/20) * 0.5
            
            home_data = self.create_mock_team_data(
                home_pos, is_home=True, strength_factor=home_strength
            )
            away_data = self.create_mock_team_data(
                away_pos, is_home=False, strength_factor=away_strength
            )
            
            result = engine.predict(home_data, away_data)
            
            calibration_data.append({
                'home_pos': home_pos,
                'away_pos': away_pos,
                'pos_diff': abs(home_pos - away_pos),
                'home_λ': result['expected_goals']['home'],
                'away_λ': result['expected_goals']['away'],
                'λ_diff': abs(result['expected_goals']['home'] - result['expected_goals']['away']),
                'total_λ': result['expected_goals']['home'] + result['expected_goals']['away'],
                'home_win_prob': result['probabilities']['home_win'],
                'confidence': result['confidence']
            })
        
        return pd.DataFrame(calibration_data)
    
    def run_tier_boundary_test(self, league_params):
        """Test boundary conditions between tiers."""
        engine = self.engine_class(league_params)
        
        boundaries = [
            (3, 4),  # Elite/Top boundary
            (6, 7),  # Top/Mid boundary
            (12, 13),  # Mid/Lower boundary
            (15, 16),  # Lower tier boundary
        ]
        
        results = []
        for home_pos, away_pos in boundaries:
            # Test both directions
            home_data = self.create_mock_team_data(home_pos, is_home=True)
            away_data = self.create_mock_team_data(away_pos, is_home=False)
            
            result = engine.predict(home_data, away_data)
            
            results.append({
                'boundary': f'{home_pos}-{away_pos}',
                'home_pos': home_pos,
                'away_pos': away_pos,
                'home_λ': result['expected_goals']['home'],
                'away_λ': result['expected_goals']['away'],
                'home_max': engine._get_tier_based_max_lambda(home_pos, True),
                'away_max': engine._get_tier_based_max_lambda(away_pos, False)
            })
            
            # Check if max λ constraints are working
            if result['expected_goals']['home'] > engine._get_tier_based_max_lambda(home_pos, True):
                self.anomalies.append(f"Home λ exceeds max for position {home_pos}")
            
            if result['expected_goals']['away'] > engine._get_tier_based_max_lambda(away_pos, False):
                self.anomalies.append(f"Away λ exceeds max for position {away_pos}")
        
        return results
    
    def run_consistency_test(self, league_params, n_repeats=50):
        """Test consistency of predictions for same matchup."""
        engine = self.engine_class(league_params)
        
        home_data = self.create_mock_team_data(5, is_home=True)
        away_data = self.create_mock_team_data(15, is_home=False)
        
        results = []
        for _ in range(n_repeats):
            result = engine.predict(home_data.copy(), away_data.copy())
            results.append({
                'home_λ': result['expected_goals']['home'],
                'away_λ': result['expected_goals']['away'],
                'total_λ': result['expected_goals']['home'] + result['expected_goals']['away'],
                'home_win': result['probabilities']['home_win']
            })
        
        df = pd.DataFrame(results)
        
        # Calculate consistency metrics
        consistency = {
            'home_λ_std': df['home_λ'].std(),
            'away_λ_std': df['away_λ'].std(),
            'home_λ_cv': df['home_λ'].std() / df['home_λ'].mean() if df['home_λ'].mean() > 0 else 0,
            'home_win_std': df['home_win'].std(),
            'is_consistent': df['home_λ'].std() < 0.1 and df['home_win'].std() < 0.02
        }
        
        return df, consistency
    
    def run_probability_calibration_test(self, league_params):
        """Test if probabilities are well-calibrated."""
        engine = self.engine_class(league_params)
        
        # Test different probability ranges
        test_bins = []
        for target_prob in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            # Find matchup that gives approximately this probability
            best_matchup = None
            best_diff = float('inf')
            
            for _ in range(100):
                home_pos = random.randint(1, 20)
                away_pos = random.randint(1, 20)
                
                home_strength = 1.0 + (1 - home_pos/20) * 0.5
                away_strength = 1.0 + (1 - away_pos/20) * 0.5
                
                home_data = self.create_mock_team_data(home_pos, True, home_strength)
                away_data = self.create_mock_team_data(away_pos, False, away_strength)
                
                result = engine.predict(home_data, away_data)
                prob = result['probabilities']['home_win']
                
                if abs(prob - target_prob) < best_diff:
                    best_diff = abs(prob - target_prob)
                    best_matchup = {
                        'target_prob': target_prob,
                        'actual_prob': prob,
                        'home_pos': home_pos,
                        'away_pos': away_pos,
                        'home_λ': result['expected_goals']['home'],
                        'away_λ': result['expected_goals']['away']
                    }
            
            if best_matchup:
                test_bins.append(best_matchup)
        
        return test_bins

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_lambda_distribution(df, title):
    """Plot distribution of λ values."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Home λ Distribution', 'Away λ Distribution', 
                       'Total λ Distribution', 'λ Difference Distribution'),
        specs=[[{'type': 'histogram'}, {'type': 'histogram'}],
               [{'type': 'histogram'}, {'type': 'histogram'}]]
    )
    
    fig.add_trace(go.Histogram(x=df['home_λ'], nbinsx=30, name='Home λ'), row=1, col=1)
    fig.add_trace(go.Histogram(x=df['away_λ'], nbinsx=30, name='Away λ'), row=1, col=2)
    fig.add_trace(go.Histogram(x=df['total_λ'], nbinsx=30, name='Total λ'), row=2, col=1)
    fig.add_trace(go.Histogram(x=df['λ_diff'], nbinsx=30, name='λ Diff'), row=2, col=2)
    
    fig.update_layout(height=600, title_text=title, showlegend=False)
    return fig

def plot_position_vs_lambda(df):
    """Plot λ values vs team positions."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Home λ vs Position', 'Away λ vs Position',
                       'λ Diff vs Position Diff', 'Confidence vs Position Diff'),
        specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'scatter'}]]
    )
    
    fig.add_trace(
        go.Scatter(x=df['home_pos'], y=df['home_λ'], mode='markers', name='Home'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['away_pos'], y=df['away_λ'], mode='markers', name='Away'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['pos_diff'], y=df['λ_diff'], mode='markers', name='λ Diff'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['pos_diff'], y=df['confidence'], mode='markers', name='Confidence'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text="Position-Based Analysis", showlegend=False)
    return fig

def plot_extreme_case_results(results):
    """Visualize extreme case test results."""
    cases = [r['case'] for r in results]
    home_lambda = [r['home_λ'] for r in results]
    away_lambda = [r['away_λ'] for r in results]
    home_win_prob = [r['home_win'] * 100 for r in results]
    confidence = [r['confidence'] for r in results]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Expected Goals (λ)', 'Win Probability (%)',
                       'Model Confidence (%)', 'Total Expected Goals'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Bar(x=cases, y=home_lambda, name='Home λ', marker_color='blue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=cases, y=away_lambda, name='Away λ', marker_color='red'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=cases, y=home_win_prob, name='Home Win %', marker_color='green'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=cases, y=confidence, name='Confidence', marker_color='orange'),
        row=2, col=1
    )
    
    total_lambda = [r['total_λ'] for r in results]
    fig.add_trace(
        go.Bar(x=cases, y=total_lambda, name='Total λ', marker_color='purple'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text="Extreme Case Analysis", barmode='group')
    return fig

def plot_calibration_curve(test_bins):
    """Plot probability calibration curve."""
    target_probs = [b['target_prob'] for b in test_bins]
    actual_probs = [b['actual_prob'] for b in test_bins]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=target_probs, y=actual_probs,
        mode='markers+lines',
        name='Actual vs Target',
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Perfect Calibration',
        line=dict(dash='dash', color='gray')
    ))
    
    fig.update_layout(
        title='Probability Calibration Curve',
        xaxis_title='Target Probability',
        yaxis_title='Actual Probability',
        height=500
    )
    
    return fig

# ============================================================================
# MAIN STRESS TEST APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="Prediction Engine Stress Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Football Prediction Engine Stress Test")
    st.markdown("### Comprehensive Calibration Analysis")
    
    # Select league for testing
    league_options = ['LA LIGA', 'PREMIER LEAGUE']
    selected_league = st.selectbox("Select League for Testing:", league_options)
    league_params = LEAGUE_PARAMS[selected_league]
    
    # Initialize test framework
    test_framework = StressTestFramework(FootballPredictionEngine)
    
    # Run different tests
    st.markdown("## 1️⃣ Extreme Case Analysis")
    if st.button("Run Extreme Case Test", type="primary"):
        with st.spinner("Testing extreme matchups..."):
            extreme_results = test_framework.run_extreme_case_test(league_params)
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(pd.DataFrame(extreme_results), use_container_width=True)
            with col2:
                fig = plot_extreme_case_results(extreme_results)
                st.plotly_chart(fig, use_container_width=True)
            
            # Display anomalies
            if test_framework.anomalies:
                st.warning("⚠️ Anomalies Detected:")
                for anomaly in test_framework.anomalies:
                    st.write(f"• {anomalie}")
    
    st.markdown("## 2️⃣ Monte Carlo Calibration")
    if st.button("Run Monte Carlo Simulation", type="primary"):
        with st.spinner(f"Running {1000} simulations..."):
            mc_df = test_framework.run_monte_carlo_calibration(league_params, 1000)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Home λ", f"{mc_df['home_λ'].mean():.2f}")
            with col2:
                st.metric("Avg Away λ", f"{mc_df['away_λ'].mean():.2f}")
            with col3:
                st.metric("Avg Total λ", f"{mc_df['total_λ'].mean():.2f}")
            with col4:
                st.metric("Avg Confidence", f"{mc_df['confidence'].mean():.1f}%")
            
            # Distributions
            fig1 = plot_lambda_distribution(mc_df, "Monte Carlo λ Distributions")
            st.plotly_chart(fig1, use_container_width=True)
            
            # Position analysis
            fig2 = plot_position_vs_lambda(mc_df)
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("## 3️⃣ Tier Boundary Testing")
    if st.button("Test Tier Boundaries", type="primary"):
        with st.spinner("Testing tier boundaries..."):
            boundary_results = test_framework.run_tier_boundary_test(league_params)
            
            st.subheader("Tier Boundary Analysis")
            df_boundary = pd.DataFrame(boundary_results)
            st.dataframe(df_boundary, use_container_width=True)
            
            # Check max λ constraints
            st.subheader("Max λ Constraint Check")
            for idx, row in df_boundary.iterrows():
                home_ok = row['home_λ'] <= row['home_max']
                away_ok = row['away_λ'] <= row['away_max']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{row['boundary']} - Home:**")
                    st.write(f"λ: {row['home_λ']:.2f}, Max: {row['home_max']:.1f}")
                    st.success("✓ Within limit") if home_ok else st.error("✗ Exceeds limit")
                
                with col2:
                    st.write(f"**{row['boundary']} - Away:**")
                    st.write(f"λ: {row['away_λ']:.2f}, Max: {row['away_max']:.1f}")
                    st.success("✓ Within limit") if away_ok else st.error("✗ Exceeds limit")
    
    st.markdown("## 4️⃣ Consistency Testing")
    if st.button("Test Prediction Consistency", type="primary"):
        with st.spinner("Testing consistency..."):
            consistency_df, consistency_metrics = test_framework.run_consistency_test(league_params, 50)
            
            st.subheader("Consistency Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Home λ Std Dev", f"{consistency_metrics['home_λ_std']:.4f}")
            with col2:
                st.metric("Home λ Coeff Var", f"{consistency_metrics['home_λ_cv']:.4f}")
            with col3:
                st.metric("Home Win Prob Std", f"{consistency_metrics['home_win_std']:.4f}")
            with col4:
                status = "Consistent ✓" if consistency_metrics['is_consistent'] else "Inconsistent ✗"
                st.metric("Consistency", status)
            
            st.subheader("Distribution of Repeated Predictions")
            fig = make_subplots(rows=1, cols=2, subplot_titles=('Home λ Distribution', 'Home Win Probability Distribution'))
            
            fig.add_trace(go.Histogram(x=consistency_df['home_λ'], nbinsx=20, name='Home λ'), row=1, col=1)
            fig.add_trace(go.Histogram(x=consistency_df['home_win'], nbinsx=20, name='Home Win Prob'), row=1, col=2)
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("## 5️⃣ Probability Calibration")
    if st.button("Test Probability Calibration", type="primary"):
        with st.spinner("Testing probability calibration..."):
            test_bins = test_framework.run_probability_calibration_test(league_params)
            
            st.subheader("Calibration Test Results")
            df_calib = pd.DataFrame(test_bins)
            st.dataframe(df_calib, use_container_width=True)
            
            fig = plot_calibration_curve(test_bins)
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate calibration error
            calib_error = np.mean([abs(b['target_prob'] - b['actual_prob']) for b in test_bins])
            st.metric("Average Calibration Error", f"{calib_error:.4f}")
    
    st.markdown("## 6️⃣ Comprehensive Report")
    if st.button("Generate Full Stress Test Report", type="primary"):
        with st.spinner("Running comprehensive analysis..."):
            # Run all tests
            extreme_results = test_framework.run_extreme_case_test(league_params)
            mc_df = test_framework.run_monte_carlo_calibration(league_params, 500)
            boundary_results = test_framework.run_tier_boundary_test(league_params)
            consistency_df, consistency_metrics = test_framework.run_consistency_test(league_params, 30)
            test_bins = test_framework.run_probability_calibration_test(league_params)
            
            # Generate report
            st.markdown("### 📊 Comprehensive Stress Test Report")
            
            # Executive summary
            st.markdown("#### Executive Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_home_lambda = mc_df['home_λ'].mean()
                status = "✓" if 1.0 <= avg_home_lambda <= 2.0 else "⚠"
                st.metric("Avg Home λ", f"{avg_home_lambda:.2f}", delta=status)
            
            with col2:
                avg_confidence = mc_df['confidence'].mean()
                status = "✓" if avg_confidence >= 50 else "⚠"
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%", delta=status)
            
            with col3:
                calib_error = np.mean([abs(b['target_prob'] - b['actual_prob']) for b in test_bins])
                status = "✓" if calib_error < 0.05 else "⚠"
                st.metric("Calibration Error", f"{calib_error:.4f}", delta=status)
            
            with col4:
                is_consistent = consistency_metrics['is_consistent']
                status = "✓" if is_consistent else "⚠"
                st.metric("Consistency", "Good" if is_consistent else "Issues", delta=status)
            
            # Issues and recommendations
            st.markdown("#### 🚨 Issues Detected")
            if test_framework.anomalies:
                for anomaly in test_framework.anomalies:
                    st.error(anomalie)
            else:
                st.success("No major anomalies detected")
            
            # Recommendations
            st.markdown("#### 💡 Recommendations")
            
            recommendations = []
            
            # Check max λ constraints
            max_home_lambda = mc_df['home_λ'].max()
            max_away_lambda = mc_df['away_λ'].max()
            
            if max_home_lambda > 3.0:
                recommendations.append(f"Consider reducing max home λ (current max: {max_home_lambda:.2f})")
            if max_away_lambda > 2.5:
                recommendations.append(f"Consider reducing max away λ (current max: {max_away_lambda:.2f})")
            
            # Check probability calibration
            if calib_error > 0.1:
                recommendations.append("Improve probability calibration - predictions may be biased")
            
            # Check consistency
            if not is_consistent:
                recommendations.append("Improve prediction consistency")
            
            # Check tier boundaries
            for boundary in boundary_results:
                if boundary['home_λ'] > boundary['home_max'] or boundary['away_λ'] > boundary['away_max']:
                    recommendations.append(f"Review tier boundaries at position {boundary['boundary']}")
            
            if recommendations:
                for rec in recommendations:
                    st.info(f"• {rec}")
            else:
                st.success("Engine appears well-calibrated!")
            
            # Detailed metrics
            with st.expander("View Detailed Metrics"):
                st.subheader("λ Statistics")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Home λ:**")
                    st.write(f"Mean: {mc_df['home_λ'].mean():.3f}")
                    st.write(f"Std: {mc_df['home_λ'].std():.3f}")
                    st.write(f"Min: {mc_df['home_λ'].min():.3f}")
                    st.write(f"Max: {mc_df['home_λ'].max():.3f}")
                
                with col2:
                    st.write("**Away λ:**")
                    st.write(f"Mean: {mc_df['away_λ'].mean():.3f}")
                    st.write(f"Std: {mc_df['away_λ'].std():.3f}")
                    st.write(f"Min: {mc_df['away_λ'].min():.3f}")
                    st.write(f"Max: {mc_df['away_λ'].max():.3f}")
                
                st.subheader("Confidence Statistics")
                st.write(f"Mean: {mc_df['confidence'].mean():.1f}%")
                st.write(f"Std: {mc_df['confidence'].std():.1f}%")
                st.write(f"Range: {mc_df['confidence'].min():.1f}% to {mc_df['confidence'].max():.1f}%")
            
            # Export results
            st.markdown("#### 📥 Export Results")
            if st.button("Download Test Results as CSV"):
                # Combine all results
                all_results = []
                
                # Add extreme cases
                for result in extreme_results:
                    result['test_type'] = 'extreme_case'
                    all_results.append(result)
                
                # Add Monte Carlo samples
                for _, row in mc_df.iterrows():
                    all_results.append({
                        'test_type': 'monte_carlo',
                        'home_pos': row['home_pos'],
                        'away_pos': row['away_pos'],
                        'home_λ': row['home_λ'],
                        'away_λ': row['away_λ'],
                        'confidence': row['confidence']
                    })
                
                # Create CSV
                df_export = pd.DataFrame(all_results)
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"stress_test_results_{selected_league}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    # Import your existing code
    from your_main_file import FootballPredictionEngine, LEAGUE_PARAMS, CONSTANTS
    main()
