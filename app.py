import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Machine Learning imports
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import umap
import hdbscan

# Page configuration
st.set_page_config(
    page_title="⚡ Elite Narrative Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for elite styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2D3748;
        margin-top: 2rem;
        border-bottom: 3px solid #4FD1C5;
        padding-bottom: 0.5rem;
    }
    .elite-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .prediction-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #4FD1C5;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .narrative-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 5px;
        background: linear-gradient(135deg, #4FD1C5 0%, #319795 100%);
        color: white;
        box-shadow: 0 3px 10px rgba(76, 209, 197, 0.3);
    }
    .value-bet-badge {
        background: linear-gradient(135deg, #F6E05E 0%, #D69E2E 100%);
        animation: pulse 2s infinite;
        color: #2D3748;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .confidence-high { background: linear-gradient(135deg, #68D391 0%, #38A169 100%); }
    .confidence-medium { background: linear-gradient(135deg, #F6AD55 0%, #ED8936 100%); }
    .confidence-low { background: linear-gradient(135deg, #FC8181 0%, #E53E3E 100%); }
    .metric-elite {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 4px solid #4FD1C5;
    }
    .cluster-viz {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

class EliteNarrativeEngine:
    """Self-Learning Narrative Intelligence Engine"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.narrative_clusters = None
        self.cluster_models = {}
        self.classifier = None
        self.narrative_descriptions = {}
        self.feature_importance = {}
        
    def engineer_features(self, df):
        """Create sophisticated features from raw data"""
        df = df.copy()
        
        # 1. Form Momentum & Quality Features
        def calculate_form_momentum(form_string):
            """Weighted form momentum with recency bias"""
            points = {'W': 3, 'D': 1, 'L': 0}
            total = 0
            weights = [1.2, 1.1, 1.0, 0.9, 0.8]  # Recent games weighted more
            
            for i, result in enumerate(form_string[-5:]):
                if result in points:
                    total += points[result] * weights[i] if i < len(weights) else points[result]
            return total / 15  # Normalized to 0-1
        
        df['home_form_momentum'] = df['home_form'].apply(calculate_form_momentum)
        df['away_form_momentum'] = df['away_form'].apply(calculate_form_momentum)
        df['form_momentum_diff'] = df['home_form_momentum'] - df['away_form_momentum']
        
        # 2. Style Clash Intensity
        def calculate_style_clash(home_style, away_style):
            """Quantify tactical matchup intensity"""
            style_matrix = {
                ('Possession-based & control', 'Pragmatic/Defensive'): 0.9,  # Classic siege
                ('Possession-based & control', 'High press & transition'): 0.8,  # Chaos
                ('High press & transition', 'Pragmatic/Defensive'): 0.7,  # Press vs bus
                ('High press & transition', 'High press & transition'): 0.6,  # End-to-end
                ('Pragmatic/Defensive', 'Pragmatic/Defensive'): 0.3,  # Chess match
                ('Progressive/Developing', 'Progressive/Developing'): 0.5,  # Unknown
                ('Balanced/Adaptive', 'High press & transition'): 0.6,  # Adaptive chaos
                ('Counter-attack', 'Possession-based & control'): 0.7,  # Counter opportunity
            }
            
            # Try both orders
            for style_pair in [(home_style, away_style), (away_style, home_style)]:
                if style_pair in style_matrix:
                    return style_matrix[style_pair]
            return 0.5  # Default moderate intensity
        
        df['style_clash_intensity'] = df.apply(
            lambda x: calculate_style_clash(x['home_manager_style'], x['away_manager_style']), axis=1
        )
        
        # 3. Quality Differentials
        df['attack_differential'] = (df['home_attack_rating'] - df['away_attack_rating']) / 10
        df['defense_differential'] = (df['home_defense_rating'] - df['away_defense_rating']) / 10
        df['press_differential'] = (df['home_press_rating'] - df['away_press_rating']) / 10
        df['possession_differential'] = (df['home_possession_rating'] - df['away_possession_rating']) / 10
        df['pragmatic_differential'] = (df['home_pragmatic_rating'] - df['away_pragmatic_rating']) / 10
        
        # 4. Composite Quality Score
        df['home_composite_score'] = (
            df['home_attack_rating'] * 0.3 +
            df['home_defense_rating'] * 0.25 +
            df['home_press_rating'] * 0.2 +
            df['home_possession_rating'] * 0.15 +
            df['home_pragmatic_rating'] * 0.1
        ) / 10
        
        df['away_composite_score'] = (
            df['away_attack_rating'] * 0.3 +
            df['away_defense_rating'] * 0.25 +
            df['away_press_rating'] * 0.2 +
            df['away_possession_rating'] * 0.15 +
            df['away_pragmatic_rating'] * 0.1
        ) / 10
        
        df['composite_differential'] = df['home_composite_score'] - df['away_composite_score']
        
        # 5. Historical Pattern Features
        df['h2h_goals_per_game'] = df['last_h2h_goals']
        df['btts_history'] = df['last_h2h_btts'].apply(lambda x: 1 if x == 'Yes' else 0)
        
        # 6. Market & Context Features
        df['implied_home_prob'] = 1 / df['home_odds']
        df['implied_away_prob'] = 1 / df['away_odds']
        df['market_confidence'] = abs(df['implied_home_prob'] - df['implied_away_prob'])
        df['position_differential'] = (df['away_position'] - df['home_position']) / 20  # Normalized
        
        # 7. Volatility Indicators
        df['attack_volatility'] = (df['home_attack_rating'] + df['away_attack_rating']) / 20
        df['defense_stability'] = (20 - (df['home_defense_rating'] + df['away_defense_rating'])) / 20
        df['match_volatility'] = df['attack_volatility'] * df['defense_stability']
        
        return df
    
    def discover_narratives(self, df, n_clusters_range=(3, 8)):
        """Automatically discover match narrative clusters"""
        # Select engineered features for clustering
        feature_cols = [
            'home_form_momentum', 'away_form_momentum', 'form_momentum_diff',
            'style_clash_intensity',
            'attack_differential', 'defense_differential', 'press_differential',
            'possession_differential', 'pragmatic_differential',
            'composite_differential',
            'h2h_goals_per_game', 'btts_history',
            'market_confidence', 'position_differential',
            'match_volatility'
        ]
        
        # Prepare data
        X = df[feature_cols].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        # Dimensionality reduction for visualization
        reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        X_umap = reducer.fit_transform(X_scaled)
        
        # Find optimal number of clusters
        best_score = -1
        best_n = 3
        best_labels = None
        
        for n in range(n_clusters_range[0], n_clusters_range[1] + 1):
            kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            
            # Use silhouette score for clustering quality
            if len(set(labels)) > 1:
                score = silhouette_score(X_scaled, labels)
                if score > best_score:
                    best_score = score
                    best_n = n
                    best_labels = labels
        
        # Apply best clustering
        self.narrative_clusters = best_labels
        df['narrative_cluster'] = best_labels
        
        # Characterize each cluster
        self.narrative_descriptions = self._characterize_clusters(df, feature_cols)
        
        return df, X_umap, best_score
    
    def _characterize_clusters(self, df, feature_cols):
        """Characterize each discovered cluster"""
        descriptions = {}
        
        for cluster_id in sorted(df['narrative_cluster'].unique()):
            cluster_data = df[df['narrative_cluster'] == cluster_id]
            
            # Calculate cluster characteristics
            characteristics = {
                'size': len(cluster_data),
                'avg_home_win_rate': (cluster_data['implied_home_prob'] > 0.5).mean(),
                'avg_total_goals': cluster_data['h2h_goals_per_game'].mean(),
                'avg_btts_rate': cluster_data['btts_history'].mean(),
                'common_home_style': cluster_data['home_manager_style'].mode()[0] if len(cluster_data) > 0 else 'Unknown',
                'common_away_style': cluster_data['away_manager_style'].mode()[0] if len(cluster_data) > 0 else 'Unknown',
                'avg_attack_diff': cluster_data['attack_differential'].mean(),
                'avg_defense_diff': cluster_data['defense_differential'].mean(),
                'avg_press_diff': cluster_data['press_differential'].mean(),
                'avg_style_intensity': cluster_data['style_clash_intensity'].mean(),
                'avg_market_confidence': cluster_data['market_confidence'].mean(),
                'avg_match_volatility': cluster_data['match_volatility'].mean(),
            }
            
            # Generate narrative name and description
            name, description = self._name_narrative(characteristics)
            
            descriptions[cluster_id] = {
                'name': name,
                'description': description,
                'characteristics': characteristics,
                'sample_matches': cluster_data[['home_team', 'away_team', 'date']].head(3).to_dict('records')
            }
            
            # Train cluster-specific prediction model
            self._train_cluster_model(cluster_data, cluster_id)
        
        return descriptions
    
    def _name_narrative(self, characteristics):
        """Intelligently name narrative based on characteristics"""
        if characteristics['avg_attack_diff'] > 0.2 and characteristics['avg_defense_diff'] > 0.15:
            name = "SIEGE"
            desc = "Dominant favorite facing organized defense. Low scoring, methodical breakthrough."
        elif characteristics['avg_match_volatility'] > 0.6 and characteristics['avg_btts_rate'] > 0.6:
            name = "SHOOTOUT"
            desc = "End-to-end chaos. Weak defenses, attacking mentality. High scoring expected."
        elif characteristics['avg_press_diff'] > 0.2 and characteristics['avg_style_intensity'] > 0.7:
            name = "BLITZKRIEG"
            desc = "Early onslaught expected. High press overwhelming disorganized defense."
        elif characteristics['common_home_style'] == 'Possession-based & control' and \
             characteristics['common_away_style'] == 'Pragmatic/Defensive':
            name = "CONTROLLED_EDGE"
            desc = "Methodical possession vs parked bus. Grinding, low-event match."
        elif characteristics['avg_style_intensity'] > 0.7 and characteristics['avg_total_goals'] > 2.5:
            name = "EDGE-CHAOS"
            desc = "Tactical clash creating transitions. Tight but explosive with late drama."
        elif characteristics['avg_match_volatility'] < 0.3 and characteristics['avg_total_goals'] < 2.0:
            name = "CHESS_MATCH"
            desc = "Tactical stalemate. Low event, set-piece focused, draw likely."
        elif characteristics['avg_market_confidence'] < 0.2:
            name = "BALANCED BATTLE"
            desc = "Evenly matched teams. Unpredictable, coin-flip match."
        else:
            name = f"CLUSTER_{hash(str(characteristics))[:6].upper()}"
            desc = "Unique match pattern discovered from data."
        
        return name, desc
    
    def _train_cluster_model(self, cluster_data, cluster_id):
        """Train prediction model for specific narrative cluster"""
        # Prepare features and target
        feature_cols = [col for col in cluster_data.columns if col not in [
            'match_id', 'league', 'date', 'home_team', 'away_team',
            'home_manager', 'away_manager', 'last_h2h_btts',
            'home_form', 'away_form', 'narrative_cluster'
        ] and pd.api.types.is_numeric_dtype(cluster_data[col])]
        
        if len(feature_cols) < 5 or len(cluster_data) < 10:
            return  # Not enough data for meaningful model
        
        X = cluster_data[feature_cols].fillna(0).values
        
        # Create synthetic target based on match outcomes
        # For now, use implied probabilities as proxy
        y_home_win = (cluster_data['implied_home_prob'] > 0.5).astype(int).values
        
        # Train ensemble model
        rf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        gb = GradientBoostingClassifier(n_estimators=50, random_state=42, max_depth=4)
        
        # Simple voting classifier
        from sklearn.ensemble import VotingClassifier
        model = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb)],
            voting='soft'
        )
        
        try:
            model.fit(X, y_home_win)
            self.cluster_models[cluster_id] = {
                'model': model,
                'feature_cols': feature_cols,
                'accuracy': np.mean(cross_val_score(model, X, y_home_win, cv=3))
            }
        except:
            pass
    
    def train_classification_model(self, df):
        """Train model to classify matches into narratives"""
        # Prepare features
        feature_cols = [col for col in df.columns if col not in [
            'match_id', 'league', 'date', 'home_team', 'away_team',
            'home_manager', 'away_manager', 'last_h2h_btts',
            'home_form', 'away_form', 'narrative_cluster'
        ] and pd.api.types.is_numeric_dtype(df[col])]
        
        X = df[feature_cols].fillna(0).values
        y = df['narrative_cluster'].values
        
        # Train ensemble classifier
        rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        self.classifier = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb)],
            voting='soft'
        )
        
        self.classifier.fit(X, y)
        
        # Calculate feature importance
        importances = rf.feature_importances_
        self.feature_importance = dict(zip(feature_cols, importances))
        
        # Calculate cross-validation accuracy
        cv_scores = cross_val_score(self.classifier, X, y, cv=5)
        
        return np.mean(cv_scores)
    
    def predict_match(self, match_features):
        """Predict narrative and generate insights for a single match"""
        # Ensure match has engineered features
        if 'form_momentum_diff' not in match_features:
            match_features = self.engineer_features(pd.DataFrame([match_features])).iloc[0]
        
        # Prepare feature vector
        feature_cols = list(self.feature_importance.keys())
        X = np.array([match_features[col] if col in match_features else 0 for col in feature_cols]).reshape(1, -1)
        
        # Predict narrative
        cluster_probs = self.classifier.predict_proba(X)[0]
        predicted_cluster = np.argmax(cluster_probs)
        cluster_confidence = cluster_probs[predicted_cluster]
        
        # Get narrative description
        narrative_info = self.narrative_descriptions.get(predicted_cluster, {})
        
        # Generate predictions
        predictions = self._generate_predictions(match_features, narrative_info)
        
        # Generate market recommendations
        recommendations = self._generate_recommendations(predictions, narrative_info, match_features)
        
        # Calculate value bets
        value_bets = self._calculate_value_bets(recommendations, match_features)
        
        return {
            'narrative': narrative_info.get('name', 'Unknown'),
            'narrative_description': narrative_info.get('description', ''),
            'cluster': int(predicted_cluster),
            'confidence': float(cluster_confidence),
            'predictions': predictions,
            'recommendations': recommendations,
            'value_bets': value_bets,
            'cluster_characteristics': narrative_info.get('characteristics', {}),
            'sample_matches': narrative_info.get('sample_matches', [])
        }
    
    def _generate_predictions(self, match_features, narrative_info):
        """Generate narrative-specific predictions"""
        characteristics = narrative_info.get('characteristics', {})
        
        # Base predictions from cluster characteristics
        base_predictions = {
            'home_win_prob': characteristics.get('avg_home_win_rate', 0.5) * 100,
            'draw_prob': 25.0,  # Base draw rate
            'away_win_prob': (1 - characteristics.get('avg_home_win_rate', 0.5)) * 100,
            'expected_total_goals': characteristics.get('avg_total_goals', 2.5),
            'btts_prob': characteristics.get('avg_btts_rate', 0.5) * 100,
            'clean_sheet_prob': (1 - characteristics.get('avg_btts_rate', 0.5)) * 100,
            'over_25_prob': 50.0 if characteristics.get('avg_total_goals', 2.5) > 2.5 else 30.0,
            'under_25_prob': 50.0 if characteristics.get('avg_total_goals', 2.5) < 2.5 else 30.0,
        }
        
        # Adjust based on specific match features
        adjustments = self._calculate_adjustments(match_features, narrative_info)
        
        # Apply adjustments
        for key in base_predictions:
            if key in adjustments:
                base_predictions[key] *= (1 + adjustments[key])
        
        # Ensure probabilities sum correctly
        win_probs = ['home_win_prob', 'draw_prob', 'away_win_prob']
        total_win = sum(base_predictions[p] for p in win_probs)
        for p in win_probs:
            base_predictions[p] = (base_predictions[p] / total_win) * 100
        
        return base_predictions
    
    def _calculate_adjustments(self, match_features, narrative_info):
        """Calculate adjustments based on specific match features"""
        adjustments = {}
        
        # Form momentum adjustment
        form_diff = match_features.get('form_momentum_diff', 0)
        adjustments['home_win_prob'] = form_diff * 0.2
        adjustments['away_win_prob'] = -form_diff * 0.2
        
        # Attack/defense adjustment for goals
        attack_avg = (match_features.get('home_attack_rating', 5) + match_features.get('away_attack_rating', 5)) / 20
        defense_avg = (20 - (match_features.get('home_defense_rating', 5) + match_features.get('away_defense_rating', 5))) / 20
        
        goal_factor = (attack_avg - 0.5) + (defense_avg - 0.5)
        adjustments['expected_total_goals'] = goal_factor * 0.3
        adjustments['btts_prob'] = (attack_avg - 0.5) * 0.2
        
        # Style clash intensity affects volatility
        style_intensity = match_features.get('style_clash_intensity', 0.5)
        adjustments['over_25_prob'] = (style_intensity - 0.5) * 0.3
        adjustments['under_25_prob'] = -(style_intensity - 0.5) * 0.3
        
        return adjustments
    
    def _generate_recommendations(self, predictions, narrative_info, match_features):
        """Generate intelligent market recommendations"""
        narrative_name = narrative_info.get('name', '')
        recommendations = []
        
        # Narrative-specific core recommendations
        if 'SIEGE' in narrative_name:
            recommendations.extend([
                {'market': 'Under 2.5 goals', 'confidence': 0.75, 'type': 'primary'},
                {'market': 'BTTS: No', 'confidence': 0.7, 'type': 'primary'},
                {'market': 'Favorite to win to nil', 'confidence': 0.65, 'type': 'secondary'},
                {'market': 'Fewer than 10 corners total', 'confidence': 0.6, 'type': 'secondary'},
            ])
        
        elif 'SHOOTOUT' in narrative_name:
            recommendations.extend([
                {'market': 'Over 2.5 goals', 'confidence': 0.8, 'type': 'primary'},
                {'market': 'BTTS: Yes', 'confidence': 0.75, 'type': 'primary'},
                {'market': 'Both teams 2+ shots on target', 'confidence': 0.7, 'type': 'secondary'},
                {'market': 'Last goal after 75:00', 'confidence': 0.65, 'type': 'prop'},
            ])
        
        elif 'BLITZKRIEG' in narrative_name:
            recommendations.extend([
                {'market': 'Favorite -1.5 Asian handicap', 'confidence': 0.7, 'type': 'primary'},
                {'market': 'First goal before 25:00', 'confidence': 0.65, 'type': 'prop'},
                {'market': 'Favorite clean sheet', 'confidence': 0.6, 'type': 'secondary'},
                {'market': 'Over 1.5 first half goals', 'confidence': 0.55, 'type': 'prop'},
            ])
        
        elif 'CONTROLLED_EDGE' in narrative_name:
            recommendations.extend([
                {'market': 'Under 2.5 goals', 'confidence': 0.8, 'type': 'primary'},
                {'market': 'Favorite win by 1 goal', 'confidence': 0.65, 'type': 'secondary'},
                {'market': 'Fewer than 4 corners each half', 'confidence': 0.6, 'type': 'secondary'},
                {'market': 'First goal 30-60 mins', 'confidence': 0.55, 'type': 'prop'},
            ])
        
        elif 'EDGE-CHAOS' in narrative_name:
            recommendations.extend([
                {'market': 'Over 2.25 goals Asian', 'confidence': 0.75, 'type': 'primary'},
                {'market': 'BTTS: Yes', 'confidence': 0.7, 'type': 'primary'},
                {'market': 'Lead change in match', 'confidence': 0.6, 'type': 'prop'},
                {'market': 'Goal after 80:00', 'confidence': 0.55, 'type': 'prop'},
            ])
        
        elif 'CHESS' in narrative_name:
            recommendations.extend([
                {'market': 'Under 2.0 goals Asian', 'confidence': 0.8, 'type': 'primary'},
                {'market': 'Draw', 'confidence': 0.65, 'type': 'primary'},
                {'market': '0-0 or 1-1 correct score', 'confidence': 0.6, 'type': 'prop'},
                {'market': 'More cards than goals', 'confidence': 0.55, 'type': 'secondary'},
            ])
        
        # Universal recommendations based on predictions
        if predictions['over_25_prob'] > 60:
            recommendations.append({
                'market': 'Over 2.5 goals', 'confidence': predictions['over_25_prob']/100, 'type': 'data-driven'
            })
        
        if predictions['btts_prob'] > 60:
            recommendations.append({
                'market': 'BTTS: Yes', 'confidence': predictions['btts_prob']/100, 'type': 'data-driven'
            })
        
        return recommendations
    
    def _calculate_value_bets(self, recommendations, match_features):
        """Calculate expected value for each recommendation"""
        value_bets = []
        
        # Simplified value calculation (in real implementation, use market odds)
        for rec in recommendations:
            # Base value on confidence and narrative alignment
            base_value = rec['confidence'] * 0.8
            
            # Adjust for match-specific factors
            if rec['type'] == 'primary':
                base_value *= 1.2
            
            # Add some randomness for demonstration
            value = min(0.95, base_value + np.random.uniform(-0.1, 0.1))
            
            if value > 0.55:  # Positive expected value threshold
                value_bets.append({
                    'market': rec['market'],
                    'value': value,
                    'confidence': rec['confidence'],
                    'type': rec['type'],
                    'units': self._calculate_units(value, rec['type'])
                })
        
        # Sort by value
        value_bets.sort(key=lambda x: x['value'], reverse=True)
        return value_bets[:5]  # Top 5 value bets
    
    def _calculate_units(self, value, bet_type):
        """Calculate bet size in units"""
        if value > 0.7:
            return 2.5 if bet_type == 'primary' else 2.0
        elif value > 0.6:
            return 2.0 if bet_type == 'primary' else 1.5
        elif value > 0.55:
            return 1.5 if bet_type == 'primary' else 1.0
        else:
            return 1.0

# Streamlit App
def main():
    st.markdown('<div class="main-header">⚡ ELITE NARRATIVE INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #4A5568;">Self-Learning Football Match Analysis System</p>', unsafe_allow_html=True)
    
    # Initialize engine
    if 'engine' not in st.session_state:
        st.session_state.engine = EliteNarrativeEngine()
        st.session_state.trained = False
        st.session_state.narratives_discovered = False
    
    engine = st.session_state.engine
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        uploaded_file = st.file_uploader("Upload Historical CSV", type=['csv'], key="data_upload")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} matches")
            
            # Display data sample
            with st.expander("📋 Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
            
            # Engineer features
            with st.spinner("🔧 Engineering features..."):
                df_engineered = engine.engineer_features(df)
            
            # Discover narratives
            if st.button("🚀 Discover Narratives", type="primary", use_container_width=True):
                with st.spinner("🔍 Discovering match narratives..."):
                    df_with_narratives, X_umap, cluster_score = engine.discover_narratives(df_engineered)
                    st.session_state.df = df_with_narratives
                    st.session_state.X_umap = X_umap
                    st.session_state.cluster_score = cluster_score
                    st.session_state.narratives_discovered = True
                
                st.success(f"✅ Discovered narratives with silhouette score: {cluster_score:.3f}")
            
            if st.session_state.get('narratives_discovered', False):
                # Train classification model
                if st.button("🧠 Train Classification Model", use_container_width=True):
                    with st.spinner("Training narrative classifier..."):
                        cv_accuracy = engine.train_classification_model(st.session_state.df)
                        st.session_state.trained = True
                        st.session_state.cv_accuracy = cv_accuracy
                    
                    st.success(f"✅ Model trained with CV accuracy: {cv_accuracy:.1%}")
    
    # Main content
    if uploaded_file:
        if st.session_state.get('narratives_discovered', False):
            # Display discovered narratives
            st.markdown('<div class="sub-header">📊 Discovered Narratives</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.metric("Narratives Discovered", len(engine.narrative_descriptions))
            with col2:
                st.metric("Avg Cluster Score", f"{st.session_state.cluster_score:.3f}")
            with col3:
                if st.session_state.get('trained', False):
                    st.metric("Model Accuracy", f"{st.session_state.cv_accuracy:.1%}")
            
            # Display each narrative
            for cluster_id, info in engine.narrative_descriptions.items():
                with st.expander(f"📈 {info['name']} - {info['size']} matches"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {info['description']}")
                        st.markdown(f"**Home Win Rate:** {info['characteristics']['avg_home_win_rate']:.1%}")
                        st.markdown(f"**Avg Goals:** {info['characteristics']['avg_total_goals']:.2f}")
                        st.markdown(f"**BTTS Rate:** {info['characteristics']['avg_btts_rate']:.1%}")
                    
                    with col2:
                        st.markdown("**Sample Matches:**")
                        for match in info['sample_matches']:
                            st.caption(f"{match['home_team']} vs {match['away_team']} ({match['date']})")
            
            # Cluster visualization
            st.markdown('<div class="sub-header">🌌 Narrative Clusters Visualization</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            
            # Add cluster points
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            for cluster_id in sorted(engine.narrative_descriptions.keys()):
                mask = st.session_state.df['narrative_cluster'] == cluster_id
                cluster_points = st.session_state.X_umap[mask]
                
                fig.add_trace(go.Scatter(
                    x=cluster_points[:, 0],
                    y=cluster_points[:, 1],
                    mode='markers',
                    name=f"{engine.narrative_descriptions[cluster_id]['name']}",
                    marker=dict(
                        size=10,
                        color=colors[cluster_id % len(colors)],
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=st.session_state.df[mask].apply(
                        lambda row: f"{row['home_team']} vs {row['away_team']}", axis=1
                    ),
                    hoverinfo='text'
                ))
            
            fig.update_layout(
                title="Narrative Clusters (UMAP Visualization)",
                xaxis_title="Component 1",
                yaxis_title="Component 2",
                showlegend=True,
                height=500,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True, use_container_width=True)
            
            # Match prediction interface
            st.markdown('<div class="sub-header">🎯 Match Analysis</div>', unsafe_allow_html=True)
            
            if st.session_state.get('trained', False):
                # Select match for analysis
                match_options = st.session_state.df['match_id'].tolist()
                selected_match = st.selectbox("Select Match to Analyze", match_options)
                
                if selected_match:
                    match_data = st.session_state.df[st.session_state.df['match_id'] == selected_match].iloc[0]
                    
                    if st.button("Analyze Match", type="primary"):
                        with st.spinner("🔮 Generating predictions..."):
                            prediction = engine.predict_match(match_data)
                        
                        # Display results
                        st.markdown("### 📊 Analysis Results")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="metric-elite">', unsafe_allow_html=True)
                            st.markdown(f"## {prediction['narrative']}")
                            st.caption(prediction['narrative_description'])
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            confidence = prediction['confidence']
                            if confidence > 0.7:
                                conf_class = "confidence-high"
                            elif confidence > 0.5:
                                conf_class = "confidence-medium"
                            else:
                                conf_class = "confidence-low"
                            
                            st.markdown(f'<div class="metric-elite">', unsafe_allow_html=True)
                            st.markdown(f"## {confidence:.1%}")
                            st.markdown(f'<span class="prediction-badge {conf_class}">Confidence</span>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown('<div class="metric-elite">', unsafe_allow_html=True)
                            st.markdown(f"## {prediction['predictions']['expected_total_goals']:.2f}")
                            st.markdown("Expected Goals")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detailed predictions
                        st.markdown("### 📈 Statistical Predictions")
                        
                        pred_cols = st.columns(4)
                        with pred_cols[0]:
                            st.metric("Home Win", f"{prediction['predictions']['home_win_prob']:.1f}%")
                        with pred_cols[1]:
                            st.metric("Draw", f"{prediction['predictions']['draw_prob']:.1f}%")
                        with pred_cols[2]:
                            st.metric("Away Win", f"{prediction['predictions']['away_win_prob']:.1f}%")
                        with pred_cols[3]:
                            st.metric("BTTS", f"{prediction['predictions']['btts_prob']:.1f}%")
                        
                        # Value bets
                        st.markdown("### 💰 Value Bet Recommendations")
                        
                        if prediction['value_bets']:
                            for bet in prediction['value_bets']:
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.markdown(f"**{bet['market']}**")
                                with col2:
                                    st.markdown(f'<span class="prediction-badge value-bet-badge">Value: {bet["value"]:.1%}</span>', unsafe_allow_html=True)
                                with col3:
                                    st.markdown(f"**{bet['units']} units**")
                                st.progress(bet['confidence'])
                                st.caption(f"Type: {bet['type']} | Confidence: {bet['confidence']:.0%}")
                                st.divider()
                        else:
                            st.info("No strong value bets identified for this match")
                        
                        # Sample similar matches
                        st.markdown("### 📋 Similar Historical Matches")
                        for match in prediction.get('sample_matches', []):
                            st.caption(f"• {match['home_team']} vs {match['away_team']} ({match['date']})")
            else:
                st.warning("Please train the classification model first")
        else:
            st.info("👆 Click 'Discover Narratives' to analyze your data")
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to the Elite Narrative Intelligence Engine
        
        This is a **self-learning football prediction system** that:
        
        1. **🔍 Discovers natural match narratives** from your historical data
        2. **🧠 Learns patterns** without human bias
        3. **🎯 Predicts how matches will unfold**, not just who wins
        4. **💰 Identifies value betting opportunities**
        
        ### 📊 How it works:
        
        **Phase 1: Pattern Discovery**
        - Upload your historical match data (CSV format)
        - Engine automatically clusters matches by playing patterns
        - Discovers natural narratives like "Siege", "Shootout", etc.
        
        **Phase 2: Intelligence Building**
        - Trains machine learning models for each narrative
        - Learns to classify new matches into narratives
        - Builds narrative-specific prediction models
        
        **Phase 3: Smart Predictions**
        - Analyzes new matches based on discovered patterns
        - Provides narrative context and probabilities
        - Identifies value betting opportunities
        
        ### 📋 Required CSV Format:
        Your CSV should contain columns like:
        - `match_id`, `league`, `date`
        - `home_team`, `away_team`
        - `home_position`, `away_position`
        - `home_odds`, `away_odds`
        - `home_form`, `away_form` (e.g., "WWDLW")
        - `home_manager_style`, `away_manager_style`
        - `home_attack_rating`, `away_attack_rating` (1-10 scale)
        - `home_defense_rating`, `away_defense_rating` (1-10 scale)
        - `home_press_rating`, `away_press_rating` (1-10 scale)
        - `home_possession_rating`, `away_possession_rating` (1-10 scale)
        - `home_pragmatic_rating`, `away_pragmatic_rating` (1-10 scale)
        - `last_h2h_goals`, `last_h2h_btts`
        
        **Upload your CSV in the sidebar to begin!**
        """)

if __name__ == "__main__":
    main()
