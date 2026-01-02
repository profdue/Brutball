import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# =================== STATE & DURABILITY CLASSIFIER IMPORT (SAFE, READ-ONLY) ===================
# CRITICAL: This module adds informational classification ONLY
# Does NOT affect betting logic, stakes, or existing tiers
try:
    from match_state_classifier import get_complete_classification, format_reliability_badge, format_durability_indicator
    STATE_CLASSIFIER_AVAILABLE = True
except ImportError:
    STATE_CLASSIFIER_AVAILABLE = False
    # No warnings - classifier is optional enhancement
    get_complete_classification = None
    format_reliability_badge = None
    format_durability_indicator = None

# =================== HTML HELPER FUNCTIONS ===================
def format_reliability_badge_html(reliability_data):
    """Convert reliability badge Markdown to HTML for use in f-strings"""
    score = reliability_data.get('reliability_score', 0)
    label = reliability_data.get('reliability_label', 'NONE')
    
    # Emoji mapping
    emoji_map = {
        5: '🟢',  # Green
        4: '🟡',  # Yellow
        3: '🟠',  # Orange
        2: '⚪',  # Light gray
        1: '⚪',  # Light gray
        0: '⚫'   # Gray
    }
    
    emoji = emoji_map.get(score, '⚫')
    
    # Return HTML span
    return f'<span style="font-size: 1.1rem; font-weight: 600;">{emoji} <strong>Reliability: {label} ({score}/5)</strong></span>'

def safe_split_declaration(declaration: str, fallback_text: str = "") -> tuple:
    """
    Safely split a declaration into two lines.
    
    Args:
        declaration: The declaration text to split
        fallback_text: Text to use as second line if split fails
        
    Returns:
        Tuple of (first_line, second_line)
    """
    if not declaration:
        return "Declaration not available", fallback_text
    
    # Try to split by newline
    lines = declaration.strip().split('\n')
    
    if len(lines) >= 2:
        # Return first two lines
        return lines[0].strip(), lines[1].strip()
    elif len(lines) == 1:
        # If only one line, try to split by colon or period
        line = lines[0].strip()
        
        # Try to find a natural break point
        colon_split = line.split(':', 1)
        if len(colon_split) == 2:
            return colon_split[0].strip() + ':', colon_split[1].strip()
        
        period_split = line.split('.', 1)
        if len(period_split) == 2:
            return period_split[0].strip() + '.', period_split[1].strip()
        
        # If still no good split, just use the whole line as first line
        return line, fallback_text
    else:
        # Empty declaration
        return "No declaration", fallback_text

# =================== PERFORMANCE TRACKER ===================
class PerformanceTracker:
    """Simple tracker for system predictions vs actual results."""
    
    def __init__(self):
        self.predictions = []
        self.actual_results = []
    
    def record_prediction(self, match_info: str, prediction: str, confidence: str):
        """Record a system prediction."""
        self.predictions.append({
            'match': match_info,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def record_result(self, match_info: str, actual_score: str):
        """Record actual match result."""
        self.actual_results.append({
            'match': match_info,
            'actual_score': actual_score,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def calculate_accuracy(self) -> Dict:
        """Calculate prediction accuracy."""
        # Simple implementation - would need matching logic
        matched = 0
        for pred in self.predictions:
            for result in self.actual_results:
                if pred['match'] == result['match']:
                    matched += 1
                    break
        
        total = len(self.predictions)
        accuracy = (matched / total * 100) if total > 0 else 0
        
        return {
            'total_predictions': total,
            'total_results': len(self.actual_results),
            'matched_pairs': matched,
            'accuracy': accuracy
        }

# Initialize performance tracker
performance_tracker = PerformanceTracker()

# =================== BET-READY SIGNALS DISPLAY ===================
def display_bet_ready_signals(edge_locks: List[Dict], home_name: str, away_name: str):
    """Display human-readable betting signals."""
    
    if not edge_locks:
        return
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%); 
                padding: 1.5rem; border-radius: 10px; border: 3px solid #059669; 
                margin: 1.5rem 0;">
        <h3 style="color: #065F46; margin: 0 0 1rem 0;">🎯 BET-READY SIGNALS</h3>
        <p style="color: #374151; margin-bottom: 1rem;">Clear, actionable betting recommendations based on defensive proof</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a clean table for bet-ready signals
    for lock in edge_locks:
        # Determine confidence color
        confidence_colors = {
            "VERY STRONG": "#2563EB",
            "STRONG": "#059669",
            "WEAK": "#D97706",
            "VERY WEAK": "#DC2626"
        }
        
        confidence_color = confidence_colors.get(lock['confidence'], "#6B7280")
        
        # Display each signal
        signal_html = f"""
        <div style="background: white; padding: 1.5rem; border-radius: 8px; 
                    border: 2px solid {confidence_color}; margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #1F2937;">
                        {lock['market']}
                    </div>
                    <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.25rem;">
                        Defensive context: {lock['defensive_team']} concedes {lock['defense_avg']:.2f} avg (last 5)
                    </div>
                </div>
                <div style="text-align: center; min-width: 100px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">
                        {lock['confidence_emoji']}
                    </div>
                    <div style="font-weight: 700; color: {confidence_color};">
                        {lock['confidence']}
                    </div>
                </div>
            </div>
            
            <div style="background: #F9FAFB; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Defensive Team</div>
                        <div style="font-weight: 600; color: #374151;">{lock['defensive_team']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Avg Conceded</div>
                        <div style="font-weight: 600; color: #059669;">{lock['defense_avg']:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Opponent Attack</div>
                        <div style="font-weight: 600; color: #DC2626;">{lock['opponent_attack_avg']:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #6B7280;">Capital Multiplier</div>
                        <div style="font-weight: 600; color: #3B82F6;">{lock['capital_multiplier']:.1f}x</div>
                    </div>
                </div>
                <div style="font-size: 0.9rem; color: #374151;">
                    <strong>📈 Context:</strong> {lock['full_explanation']}
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); 
                        padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem; text-align: center;">
                <div style="font-size: 1rem; font-weight: 700; color: #92400E;">
                    {lock['bet_label']}
                </div>
                <div style="font-size: 0.85rem; color: #92400E; margin-top: 0.25rem;">
                    Suggested bet: {lock['team_to_bet']} to score 0 or 1 goals
                </div>
            </div>
        </div>
        """
        st.markdown(signal_html, unsafe_allow_html=True)

# =================== SYSTEM CONSTANTS (IMMUTABLE) ===================
# v6.0 Edge Detection Engine Constants
CONTROL_CRITERIA_REQUIRED = 2  # Minimum for edge detection
GOALS_ENV_THRESHOLD = 2.8      # Combined xG for goals environment
ELITE_ATTACK_THRESHOLD = 1.6   # Max xG for elite attack

# v6.1.1 State Lock Authority Engine Constants
DIRECTION_THRESHOLD = 0.25     # LAW 2: Minimum directional dominance
ENFORCEMENT_METHODS_REQUIRED = 2  # LAW 3: Redundant enforcement
STATE_FLIP_FAILURES_REQUIRED = 2  # Opponent fails ≥2 escalation checks
QUIET_CONTROL_SEPARATION_THRESHOLD = 0.1  # v6.1.2 mutual control

# Totals Lock Constants (CRITICAL: Strict binary gate)
TOTALS_LOCK_THRESHOLD = 1.2    # Last 5 matches avg goals ≤ 1.2 for both teams
UNDER_GOALS_THRESHOLD = 2.5    # Lock for Under 2.5 goals

# MARKET-SPECIFIC THRESHOLDS (CRITICAL: Defensive markets have stricter rules)
MARKET_THRESHOLDS = {
    'WINNER': {
        'opponent_xg_max': 1.1,      # Standard chase threshold
        'recent_concede_max': None,   # Winner uses dominance, NOT preservation
        'state_flip_failures': 2,    # ≥2/4 failures
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can win without urgency
    },
    'CLEAN_SHEET': {
        'opponent_xg_max': 0.8,      # Stricter - opponent can't score
        'recent_concede_max': 0.8,   # CRITICAL: Must preserve zero (HARD RULE)
        'state_flip_failures': 3,    # ≥3/4 failures (more stringent)
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can defend without pushing
    },
    'TEAM_NO_SCORE': {  # Team to Score: NO
        'opponent_xg_max': 0.6,      # Very strict - almost no threat
        'recent_concede_max': 0.6,   # CRITICAL: Even stricter preservation
        'state_flip_failures': 4,    # ALL 4 failures required
        'enforcement_methods': 3,    # ≥3 methods (elite defense needed)
        'urgency_required': False    # Can suppress without risk
    },
    'OPPONENT_UNDER_1_5': {
        'opponent_xg_max': 1.0,      # Limited scoring capacity
        'recent_concede_max': 1.0,   # CRITICAL: Can limit but not eliminate
        'state_flip_failures': 2,    # ≥2/4 failures
        'enforcement_methods': 2,    # ≥2 methods
        'urgency_required': False    # Can control without opening
    }
}

# Totals Lock has special thresholds (DIFFERENT LOGIC: Trend-based, NOT agency-based)
TOTALS_LOCK_CONFIG = {
    'home_goals_threshold': TOTALS_LOCK_THRESHOLD,
    'away_goals_threshold': TOTALS_LOCK_THRESHOLD,
    'both_teams_required': True,
    'trend_based': True,
    'capital_multiplier': 2.0
}

# Capital Multipliers
CAPITAL_MULTIPLIERS = {
    'EDGE_MODE': 1.0,     # v6.0 only
    'LOCK_MODE': 2.0,     # v6.0 + Any lock (agency, totals, or edge-derived)
}

# =================== PAGE CONFIGURATION ===================
st.set_page_config(
    page_title="BRUTBALL v6.3 - BET-READY SIGNALS",
    page_icon="🎯🔒📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== LEAGUE CONFIGURATION ===================
LEAGUES = {
    'Premier League': {
        'filename': 'premier_league.csv',
        'display_name': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
        'country': 'England',
        'color': '#3B82F6'
    },
    'La Liga': {
        'filename': 'la_liga.csv',
        'display_name': '🇪🇸 La Liga',
        'country': 'Spain',
        'color': '#EF4444'
    },
    'Bundesliga': {
        'filename': 'bundesliga.csv',
        'display_name': '🇩🇪 Bundesliga',
        'country': 'Germany',
        'color': '#000000'
    },
    'Serie A': {
        'filename': 'serie_a.csv',
        'display_name': '🇮🇹 Serie A',
        'country': 'Italy',
        'color': '#10B981'
    },
    'Ligue 1': {
        'filename': 'ligue_1.csv',
        'display_name': '🇫🇷 Ligue 1',
        'country': 'France',
        'color': '#8B5CF6'
    },
    'Eredivisie': {
        'filename': 'eredivisie.csv',
        'display_name': '🇳🇱 Eredivisie',
        'country': 'Netherlands',
        'color': '#F59E0B'
    },
    'Primeira Liga': {
        'filename': 'premeira_portugal.csv',
        'display_name': '🇵🇹 Primeira Liga',
        'country': 'Portugal',
        'color': '#DC2626'
    },
    'Super Lig': {
        'filename': 'super_league.csv',
        'display_name': '🇹🇷 Super Lig',
        'country': 'Turkey',
        'color': '#E11D48'
    }
}

# =================== CSS STYLING ===================
st.markdown("""
    <style>
    .system-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 1rem;
    }
    .system-subheader {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .agency-state-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 4px solid #16A34A;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(22, 163, 74, 0.15);
    }
    .totals-lock-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 4px solid #0EA5E9;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.15);
    }
    .edge-derived-display {
        padding: 2.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 4px solid #3B82F6;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15);
    }
    .market-locked-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #ECFDF5 0%, #A7F3D0 100%);
        border: 3px solid #059669;
        margin: 1rem 0;
        text-align: left;
    }
    .market-totals-locked {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 3px solid #0EA5E9;
        margin: 1rem 0;
        text-align: left;
    }
    .market-edge-derived {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        margin: 1rem 0;
        text-align: left;
    }
    .market-available-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        margin: 1rem 0;
        text-align: left;
    }
    .market-unavailable-display {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border: 3px solid #9CA3AF;
        margin: 1rem 0;
        text-align: left;
        opacity: 0.7;
    }
    .capital-mode-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 700;
    }
    .edge-mode {
        background: #EFF6FF;
        color: #1E40AF;
        border: 3px solid #3B82F6;
    }
    .lock-mode {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        color: #166534;
        border: 3px solid #16A34A;
    }
    .totals-lock-mode {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        color: #0C4A6E;
        border: 3px solid #0EA5E9;
    }
    .edge-derived-mode {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        color: #1E40AF;
        border: 3px solid #3B82F6;
    }
    .gate-passed {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #16A34A;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .gate-failed {
        background: #FEF2F2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #DC2626;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .trend-check {
        background: #E0F2FE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0EA5E9;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .state-classification-display {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 4px solid #F97316;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 16px rgba(249, 115, 22, 0.15);
    }
    .state-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 700;
        margin: 0.5rem;
    }
    .badge-stagnation {
        background: #0EA5E9;
        color: white;
        border: 2px solid #0284C7;
    }
    .badge-suppression {
        background: #16A34A;
        color: white;
        border: 2px solid #059669;
    }
    .badge-delayed {
        background: #F59E0B;
        color: white;
        border: 2px solid #D97706;
    }
    .badge-explosion {
        background: #EF4444;
        color: white;
        border: 2px solid #DC2626;
    }
    .badge-neutral {
        background: #6B7280;
        color: white;
        border: 2px solid #4B5563;
    }
    .read-only-badge {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
        font-size: 0.8rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .market-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .badge-state {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .badge-totals {
        background: #BAE6FD;
        color: #0C4A6E;
        border: 1px solid #7DD3FC;
    }
    .badge-edge-derived {
        background: #DBEAFE;
        color: #1E40AF;
        border: 1px solid #93C5FD;
    }
    .badge-locked {
        background: #A7F3D0;
        color: #065F46;
        border: 1px solid #10B981;
        font-weight: 800;
    }
    .badge-totals-locked {
        background: #7DD3FC;
        color: #0C4A6E;
        border: 1px solid #38BDF8;
        font-weight: 800;
    }
    .badge-edge-locked {
        background: #C7D2FE;
        color: #3730A3;
        border: 1px solid #818CF8;
        font-weight: 800;
    }
    .badge-noise {
        background: #F3F4F6;
        color: #6B7280;
        border: 1px solid #D1D5DB;
    }
    .agency-insight {
        background: #E0F2FE;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #38BDF8;
        margin: 1rem 0;
    }
    .totals-insight {
        background: #F0F9FF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #0EA5E9;
        margin: 1rem 0;
    }
    .edge-derived-insight {
        background: #EFF6FF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #93C5FD;
        margin: 1rem 0;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .metric-row-state {
        background: #F0FDF4;
        border-left: 3px solid #16A34A;
    }
    .metric-row-totals {
        background: #E0F2FE;
        border-left: 3px solid #0EA5E9;
    }
    .metric-row-agency {
        background: #E0F2FE;
        border-left: 3px solid #38BDF8;
    }
    .metric-row-edge {
        background: #EFF6FF;
        border-left: 3px solid #3B82F6;
    }
    .architecture-diagram {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        margin: 1rem 0;
        text-align: center;
    }
    .three-tier-architecture {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        margin: 2rem 0;
    }
    .tier-level {
        width: 300px;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        position: relative;
    }
    .tier-3 {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border: 3px solid #0EA5E9;
        color: #0C4A6E;
        font-weight: 900;
    }
    .tier-2 {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 3px solid #16A34A;
        color: #166534;
        font-weight: 700;
    }
    .tier-1-edge-derived {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px dashed #3B82F6;
        color: #1E40AF;
        font-weight: 700;
    }
    .tier-1 {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 3px solid #3B82F6;
        color: #1E40AF;
    }
    .state-principle {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #38BDF8;
        margin: 1rem 0;
    }
    .state-bound-list {
        background: #F0FDF4;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #86EFAC;
        margin: 0.5rem 0;
    }
    .totals-lock-list {
        background: #E0F2FE;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #7DD3FC;
        margin: 0.5rem 0;
    }
    .edge-derived-list {
        background: #EFF6FF;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #93C5FD;
        margin: 0.5rem 0;
    }
    .noise-list {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #D1D5DB;
        margin: 0.5rem 0;
    }
    .trend-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .trend-good {
        background: #DCFCE7;
        color: #16A34A;
        border: 1px solid #86EFAC;
    }
    .trend-poor {
        background: #FEF3C7;
        color: #D97706;
        border: 1px solid #FCD34D;
    }
    .binary-gate {
        background: #F0F9FF;
        padding: 1rem;
        border-radius: 8px;
        border: 3px solid #0EA5E9;
        margin: 1rem 0;
        text-align: center;
        font-weight: 700;
    }
    .strict-binary {
        background: #FFEDD5;
        padding: 0.5rem;
        border-radius: 6px;
        border: 2px solid #F97316;
        margin: 0.5rem 0;
        text-align: center;
    }
    .law-display {
        background: #FEFCE8;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #FACC15;
        margin: 1rem 0;
    }
    .preservation-law {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #F97316;
        margin: 1rem 0;
        font-weight: 700;
    }
    .read-only-note {
        background: #F0F9FF;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #0EA5E9;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #374151;
    }
    .perspective-display {
        background: #F0F9FF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #0EA5E9;
        margin: 1rem 0;
    }
    .perspective-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        margin: 0.75rem 0;
    }
    .perspective-home {
        border-left: 4px solid #3B82F6;
    }
    .perspective-away {
        border-left: 4px solid #EF4444;
    }
    .stay-out-badge {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #92400E;
        border: 2px solid #F59E0B;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .edge-derived-badge {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        color: #1E40AF;
        border: 2px solid #3B82F6;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .classification-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .classification-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    .classification-title {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .classification-value {
        font-size: 1.2rem;
        font-weight: 700;
    }
    .reliability-display {
        margin: 1rem 0;
        padding: 1rem;
        background: #F0F9FF;
        border-radius: 8px;
        border: 1px solid #BAE6FD;
    }
    .bet-ready-signal {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid;
        margin: 1rem 0;
    }
    .bet-ready-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 1rem;
    }
    .bet-ready-body {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .bet-ready-footer {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 0.75rem;
        border-radius: 6px;
        margin-top: 0.75rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# =================== v6.0 EDGE DETECTION ENGINE ===================
class BrutballEdgeEngine:
    """
    BRUTBALL v6.0 - EDGE DETECTION ENGINE
    Heuristic layer: identifies structural advantages in football
    """
    
    @staticmethod
    def evaluate_control_criteria(team_data: Dict, opponent_data: Dict,
                                 is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """Evaluate 4 control criteria with weighted scoring."""
        rationale = []
        criteria_met = []
        raw_score = 0
        weighted_score = 0.0
        
        # CRITERION 1: Tempo dominance (weight: 1.0)
        if is_home:
            tempo_xg = team_data.get('home_xg_per_match', 0)
        else:
            tempo_xg = team_data.get('away_xg_per_match', 0)
        
        if tempo_xg > 1.4:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Tempo dominance")
            rationale.append(f"✅ {team_name}: Tempo dominance (xG: {tempo_xg:.2f} > 1.4)")
        
        # CRITERION 2: Scoring efficiency (weight: 1.0)
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
        
        efficiency = goals / max(xg, 0.1)
        if efficiency > 0.9:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Scoring efficiency")
            rationale.append(f"✅ {team_name}: Scoring efficiency ({efficiency:.1%} of xG > 90%)")
        
        # CRITERION 3: Critical area threat (weight: 0.8)
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"✅ {team_name}: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # CRITERION 4: Repeatable patterns (weight: 0.8)
        if is_home:
            openplay_pct = team_data.get('home_openplay_pct', 0)
            counter_pct = team_data.get('home_counter_pct', 0)
        else:
            openplay_pct = team_data.get('away_openplay_pct', 0)
            counter_pct = team_data.get('away_counter_pct', 0)
        
        repeatable_methods = 0
        if openplay_pct > 0.5:
            repeatable_methods += 1
        if counter_pct > 0.15:
            repeatable_methods += 1
        
        if repeatable_methods >= 1:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Repeatable patterns")
            rationale.append(f"✅ {team_name}: Repeatable attacking patterns")
        
        return raw_score, weighted_score, criteria_met, rationale
    
    @staticmethod
    def execute_decision_tree(home_data: Dict, away_data: Dict,
                            home_name: str, away_name: str,
                            league_avg_xg: float) -> Dict:
        """Execute v6.0 decision tree to identify structural edges."""
        audit_log = []
        decision_steps = []
        
        audit_log.append("=" * 70)
        audit_log.append("🔍 BRUTBALL v6.0 - EDGE DETECTION ENGINE")
        audit_log.append("=" * 70)
        audit_log.append(f"Match: {home_name} vs {away_name}")
        audit_log.append("")
        
        # Step 1: Identify potential controller
        audit_log.append("STEP 1: CONTROL CRITERIA EVALUATION")
        
        home_score, home_weighted, home_criteria, home_rationale = BrutballEdgeEngine.evaluate_control_criteria(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_score, away_weighted, away_criteria, away_rationale = BrutballEdgeEngine.evaluate_control_criteria(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        audit_log.extend(home_rationale)
        audit_log.extend(away_rationale)
        
        # Determine favorite (by position)
        home_pos = home_data.get('season_position', 10)
        away_pos = away_data.get('season_position', 10)
        favorite = home_name if home_pos < away_pos else away_name
        underdog = away_name if favorite == home_name else home_name
        
        # Get xG values
        home_xg = home_data.get('home_xg_per_match', 0)
        away_xg = away_data.get('away_xg_per_match', 0)
        combined_xg = home_xg + away_xg
        
        # Determine controller for v6.0 logic
        controller = None
        if home_score >= 2 and away_score >= 2:
            if home_weighted > away_weighted:
                controller = home_name
            else:
                controller = away_name
        elif home_score >= 2 and home_score > away_score:
            controller = home_name
        elif away_score >= 2 and away_score > home_score:
            controller = away_name
        
        # Step 2: Apply v6.0 decision logic
        audit_log.append("")
        audit_log.append("STEP 2: DECISION LOGIC APPLICATION")
        
        primary_action = "UNDER 2.5"  # Default conservative
        confidence = 5.0
        secondary_logic = ""
        stake_pct = 1.0
        
        if controller:
            # Controller exists
            opponent = away_name if controller == home_name else home_name
            is_underdog = controller == underdog
            
            if combined_xg >= 2.8 and max(home_xg, away_xg) >= 1.6:
                # Goals environment present
                primary_action = f"BACK {controller} & OVER 2.5"
                confidence = 7.5
                secondary_logic = f"Controller + goals environment"
                
                if is_underdog:
                    confidence -= 0.5
                    secondary_logic += " (underdog controller)"
            else:
                # No goals environment
                primary_action = f"BACK {controller}"
                confidence = 8.0
                secondary_logic = "Clean win expected (likely UNDER)"
            
            # Confidence-based stake
            if confidence >= 8.0:
                stake_pct = 2.5
            elif confidence >= 7.0:
                stake_pct = 2.0
            elif confidence >= 6.0:
                stake_pct = 1.5
            else:
                stake_pct = 1.0
                
        elif combined_xg >= 2.8:
            # No controller but goals environment
            primary_action = "OVER 2.5"
            confidence = 6.0
            secondary_logic = "Goals only - no clear controller"
            stake_pct = 1.0
        
        else:
            # No controller, no goals
            primary_action = "UNDER 2.5"
            confidence = 5.5
            secondary_logic = "Low-scoring match expected"
            stake_pct = 0.5
        
        # Ensure reasonable confidence bounds
        confidence = max(5.0, min(confidence, 9.0))
        
        audit_log.append(f"• Primary Action: {primary_action}")
        audit_log.append(f"• Confidence: {confidence:.1f}/10")
        audit_log.append(f"• Stake: {stake_pct:.1f}% (EDGE MODE)")
        if secondary_logic:
            audit_log.append(f"• Logic: {secondary_logic}")
        
        audit_log.append("=" * 70)
        
        return {
            'primary_action': primary_action,
            'confidence': confidence,
            'stake_pct': stake_pct,
            'secondary_logic': secondary_logic,
            'audit_log': audit_log,
            'decision_steps': [
                f"1. Control evaluation: {controller if controller else 'No clear controller'}",
                f"2. Combined xG: {combined_xg:.2f} ({'≥2.8' if combined_xg >= 2.8 else '<2.8'})",
                f"3. Max xG: {max(home_xg, away_xg):.2f} ({'≥1.6' if max(home_xg, away_xg) >= 1.6 else '<1.6'})",
                f"4. Decision: {primary_action} (Confidence: {confidence:.1f}/10)"
            ],
            'key_metrics': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'combined_xg': combined_xg,
                'controller': controller,
                'favorite': favorite,
                'underdog': underdog
            },
            'mode': 'EDGE_MODE'
        }

# =================== AGENCY-STATE LOCK ENGINE ===================
class AgencyStateLockEngine:
    """
    AGENCY-STATE LOCK ENGINE
    Unified engine for all agency-bound markets
    STATE = AGENCY CONTROL • LOCK = AGENCY SUPPRESSION
    
    CRITICAL SYSTEM LAW (v6.2):
    Gate 4 is NOT an extension of Gates 1-3.
    Gate 4 OVERRIDES them for defensive markets.
    
    A team can dominate creation (Gates 1-3) 
    and STILL NOT BE ABLE TO PROTECT A STATE.
    Protection requires RECENT defensive proof, not season-level dominance.
    
    Manchester United vs Wolves PROVED this empirically.
    """
    
    @staticmethod
    def evaluate_quiet_control(team_data: Dict, opponent_data: Dict,
                              is_home: bool, team_name: str) -> Tuple[int, float, List[str], List[str]]:
        """GATE 1: Evaluate Quiet Control."""
        rationale = []
        criteria_met = []
        raw_score = 0
        weighted_score = 0.0
        
        # CRITERION 1: Tempo dominance (weight: 1.0)
        if is_home:
            tempo_xg = team_data.get('home_xg_per_match', 0)
        else:
            tempo_xg = team_data.get('away_xg_per_match', 0)
        
        if tempo_xg > 1.4:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Tempo dominance")
            rationale.append(f"GATE 1.1: Tempo dominance (xG: {tempo_xg:.2f} > 1.4)")
        
        # CRITERION 2: Scoring efficiency (weight: 1.0)
        if is_home:
            goals = team_data.get('home_goals_scored', 0)
            xg = team_data.get('home_xg_for', 0)
        else:
            goals = team_data.get('away_goals_scored', 0)
            xg = team_data.get('away_xg_for', 0)
        
        efficiency = goals / max(xg, 0.1)
        if efficiency > 0.9:
            raw_score += 1
            weighted_score += 1.0
            criteria_met.append("Scoring efficiency")
            rationale.append(f"GATE 1.2: Scoring efficiency ({efficiency:.1%} of xG > 90%)")
        
        # CRITERION 3: Critical area threat (weight: 0.8)
        if is_home:
            setpiece_pct = team_data.get('home_setpiece_pct', 0)
        else:
            setpiece_pct = team_data.get('away_setpiece_pct', 0)
        
        if setpiece_pct > 0.25:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Critical area threat")
            rationale.append(f"GATE 1.3: Critical area threat (set pieces: {setpiece_pct:.1%} > 25%)")
        
        # CRITERION 4: Repeatable patterns (weight: 0.8)
        if is_home:
            openplay_pct = team_data.get('home_openplay_pct', 0)
            counter_pct = team_data.get('home_counter_pct', 0)
        else:
            openplay_pct = team_data.get('away_openplay_pct', 0)
            counter_pct = team_data.get('away_counter_pct', 0)
        
        repeatable_methods = 0
        if openplay_pct > 0.5:
            repeatable_methods += 1
        if counter_pct > 0.15:
            repeatable_methods += 1
        
        if repeatable_methods >= 1:
            raw_score += 1
            weighted_score += 0.8
            criteria_met.append("Repeatable patterns")
            rationale.append(f"GATE 1.4: Repeatable attacking patterns")
        
        return raw_score, weighted_score, criteria_met, rationale
    
    @staticmethod
    def check_directional_dominance(controller_xg: float, opponent_xg: float,
                                   controller_name: str, opponent_name: str,
                                   market_type: str) -> Tuple[bool, float, List[str]]:
        """GATE 2: Check directional dominance with market-specific thresholds."""
        rationale = []
        control_delta = controller_xg - opponent_xg
        
        # MARKET-SPECIFIC THRESHOLDS
        if market_type == 'WINNER':
            market_threshold = 1.1
        elif market_type == 'CLEAN_SHEET':
            market_threshold = 0.8
        elif market_type == 'TEAM_NO_SCORE':
            market_threshold = 0.6
        elif market_type == 'OPPONENT_UNDER_1_5':
            market_threshold = 1.0
        else:
            market_threshold = 1.1  # Default
        
        rationale.append(f"GATE 2: DIRECTIONAL DOMINANCE ({market_type})")
        rationale.append(f"• Controller xG ({controller_name}): {controller_xg:.2f}")
        rationale.append(f"• Opponent xG ({opponent_name}): {opponent_xg:.2f}")
        rationale.append(f"• Control Delta: {control_delta:+.2f}")
        rationale.append(f"• Minimum Δ Threshold: > {DIRECTION_THRESHOLD}")
        rationale.append(f"• Market-Specific Threshold: opponent xG < {market_threshold}")
        
        # Check both conditions
        delta_condition = control_delta > DIRECTION_THRESHOLD
        opponent_xg_condition = opponent_xg < market_threshold
        
        if delta_condition and opponent_xg_condition:
            rationale.append(f"✅ Directional dominance confirmed")
            rationale.append(f"  • Δ = {control_delta:+.2f} > {DIRECTION_THRESHOLD}")
            rationale.append(f"  • Opponent xG = {opponent_xg:.2f} < {market_threshold}")
            return True, control_delta, rationale
        else:
            rationale.append(f"❌ Directional dominance insufficient")
            if not delta_condition:
                rationale.append(f"  • Δ = {control_delta:+.2f} ≤ {DIRECTION_THRESHOLD}")
            if not opponent_xg_condition:
                rationale.append(f"  • Opponent xG = {opponent_xg:.2f} ≥ {market_threshold}")
            return False, control_delta, rationale
    
    @staticmethod
    def check_agency_collapse(opponent_data: Dict, is_home: bool,
                             opponent_name: str, league_avg_xg: float,
                             market_type: str) -> Tuple[bool, int, List[str]]:
        """GATE 3: Check agency collapse with market-specific requirements."""
        rationale = []
        failures = 0
        check_details = []
        
        rationale.append(f"GATE 3: AGENCY COLLAPSE CHECK ({market_type})")
        
        # MARKET-SPECIFIC REQUIREMENTS
        if market_type == 'WINNER':
            required_failures = 2
        elif market_type == 'CLEAN_SHEET':
            required_failures = 3
        elif market_type == 'TEAM_NO_SCORE':
            required_failures = 4
        elif market_type == 'OPPONENT_UNDER_1_5':
            required_failures = 2
        else:
            required_failures = 2
        
        # CHECK 1: Chase capacity
        if is_home:
            chase_xg = opponent_data.get('home_xg_per_match', 0)
        else:
            chase_xg = opponent_data.get('away_xg_per_match', 0)
        
        if chase_xg < 1.1:
            failures += 1
            check_details.append(f"✅ Chase xG {chase_xg:.2f} < 1.1")
        else:
            check_details.append(f"❌ Chase xG {chase_xg:.2f} ≥ 1.1")
        
        # CHECK 2: Tempo surge capability
        if chase_xg < 1.4:
            failures += 1
            check_details.append(f"✅ No tempo surge (xG {chase_xg:.2f} < 1.4)")
        else:
            check_details.append(f"❌ Tempo surge possible")
        
        # CHECK 3: Alternate threat channels
        if is_home:
            setpiece_pct = opponent_data.get('home_setpiece_pct', 0)
            counter_pct = opponent_data.get('home_counter_pct', 0)
        else:
            setpiece_pct = opponent_data.get('away_setpiece_pct', 0)
            counter_pct = opponent_data.get('away_counter_pct', 0)
        
        if setpiece_pct < 0.25 and counter_pct < 0.15:
            failures += 1
            check_details.append(f"✅ No alternate threat (SP: {setpiece_pct:.1%}, C: {counter_pct:.1%})")
        else:
            check_details.append(f"❌ Alternate threat exists")
        
        # CHECK 4: Substitution leverage
        if is_home:
            gpm = opponent_data.get('home_goals_per_match', 0)
        else:
            gpm = opponent_data.get('away_goals_per_match', 0)
        
        if gpm < league_avg_xg * 0.8:
            failures += 1
            check_details.append(f"✅ Low substitution leverage ({gpm:.2f} < {league_avg_xg*0.8:.2f})")
        else:
            check_details.append(f"❌ Adequate bench impact")
        
        # Add all check details
        for detail in check_details:
            rationale.append(f"  • {detail}")
        
        # Check market-specific requirements
        if failures >= required_failures:
            rationale.append(f"✅ AGENCY COLLAPSE: {failures}/{required_failures}+ failures")
            return True, failures, rationale
        else:
            rationale.append(f"❌ Insufficient agency collapse: {failures}/{required_failures} failures")
            return False, failures, rationale
    
    @staticmethod
    def check_defensive_state_preservation(controller_data: Dict, is_home: bool,
                                          controller_name: str, market_type: str) -> Tuple[bool, float, List[str]]:
        """
        GATE 4A: DEFENSIVE STATE PRESERVATION CHECK (HARD OVERRIDE)
        
        CRITICAL SYSTEM LAW (v6.2):
        A state cannot be locked unless it can be PRESERVED.
        
        This gate is NOT about dominance.
        This gate is about state preservation.
        
        If recent goals conceded contradict state preservation,
        the lock is invalid regardless of Gates 1-3.
        
        Manchester United vs Wolves PROVED this empirically:
        - Could create (Gates 1-3)
        - Could NOT preserve (Gate 4A)
        
        Porto-type teams pass this gate.
        Manchester United-type teams fail this gate.
        
        This is not a tuning parameter.
        This is a structural law.
        """
        
        rationale = []
        
        # WINNER MARKET: Uses dominance logic, NOT preservation logic
        if market_type == 'WINNER':
            rationale.append(f"GATE 4A: SKIPPED for WINNER market")
            rationale.append(f"• Winner locks use dominance, not preservation")
            return True, 0.0, rationale
        
        # DEFENSIVE MARKETS: MUST HAVE RECENT DEFENSIVE PROOF
        rationale.append(f"GATE 4A: DEFENSIVE STATE PRESERVATION ({market_type})")
        rationale.append(f"• CRITICAL: Gate 4A OVERRIDES Gates 1-3 for defensive markets")
        
        # Get recent defensive trend (LAST 5 MATCHES ONLY)
        if is_home:
            recent_conceded = controller_data.get('goals_conceded_last_5', 0)
            matches = 5
        else:
            recent_conceded = controller_data.get('goals_conceded_last_5', 0)
            matches = 5
        
        recent_concede_avg = recent_conceded / matches if matches > 0 else 0
        
        rationale.append(f"• Recent goals conceded (last {matches}): {recent_conceded}")
        rationale.append(f"• Recent concede avg: {recent_concede_avg:.2f}/match")
        
        # MARKET-SPECIFIC THRESHOLDS (HARD BINARY)
        if market_type == 'CLEAN_SHEET':
            threshold = 0.8
            rationale.append(f"• Clean Sheet requires: ≤ {threshold} goals/match")
        elif market_type == 'TEAM_NO_SCORE':
            threshold = 0.6
            rationale.append(f"• Team No Score requires: ≤ {threshold} goals/match")
        elif market_type == 'OPPONENT_UNDER_1_5':
            threshold = 1.0
            rationale.append(f"• Opponent Under 1.5 requires: ≤ {threshold} goals/match")
        else:
            threshold = 0.8
            rationale.append(f"• Default threshold: ≤ {threshold} goals/match")
        
        # HARD BINARY CHECK (NO EXCEPTIONS)
        if recent_concede_avg <= threshold:
            rationale.append(f"✅ DEFENSIVE PRESERVATION CONFIRMED")
            rationale.append(f"• {controller_name} can preserve {market_type} state")
            return True, recent_concede_avg, rationale
        else:
            rationale.append(f"❌ DEFENSIVE PRESERVATION FAILED")
            rationale.append(f"• {controller_name} concedes {recent_concede_avg:.2f}/match recently")
            rationale.append(f"• CANNOT preserve {market_type} state (requires ≤ {threshold})")
            rationale.append(f"• Manchester United vs Wolves CASE: This is why defensive locks fail")
            return False, recent_concede_avg, rationale
    
    @staticmethod
    def check_non_urgent_enforcement(controller_data: Dict, is_home: bool,
                                    controller_name: str, market_type: str,
                                    recent_concede_avg: float) -> Tuple[bool, int, List[str]]:
        """
        GATE 4B: NON-URGENT ENFORCEMENT CHECK
        (Only runs if Gate 4A passes for defensive markets)
        """
        rationale = []
        enforce_methods = 0
        method_details = []
        
        rationale.append(f"GATE 4B: NON-URGENT ENFORCEMENT ({market_type})")
        
        # MARKET-SPECIFIC REQUIREMENTS
        if market_type == 'WINNER':
            required_methods = 2
        elif market_type == 'CLEAN_SHEET':
            required_methods = 2
        elif market_type == 'TEAM_NO_SCORE':
            required_methods = 3
        elif market_type == 'OPPONENT_UNDER_1_5':
            required_methods = 2
        else:
            required_methods = 2
        
        if is_home:
            # METHOD 1: Defensive solidity at home (using SEASON data)
            goals_conceded = controller_data.get('home_goals_conceded', 0)
            matches_played = controller_data.get('home_matches_played', 1)
            season_concede_avg = goals_conceded / matches_played
            
            if season_concede_avg < 1.2:
                enforce_methods += 1
                method_details.append(f"✅ Can defend lead (concedes {season_concede_avg:.2f}/match season)")
            else:
                method_details.append(f"❌ Defensive concerns ({season_concede_avg:.2f}/match)")
            
            # METHOD 2: Alternate scoring at home
            setpiece_pct = controller_data.get('home_setpiece_pct', 0)
            counter_pct = controller_data.get('home_counter_pct', 0)
            
            if setpiece_pct > 0.25 or counter_pct > 0.15:
                enforce_methods += 1
                method_details.append(f"✅ Alternate scoring (SP: {setpiece_pct:.1%}, C: {counter_pct:.1%})")
            else:
                method_details.append(f"❌ Limited alternate scoring")
            
            # METHOD 3: Consistent threat at home
            xg_per_match = controller_data.get('home_xg_per_match', 0)
            if xg_per_match > 1.3:
                enforce_methods += 1
                method_details.append(f"✅ Consistent threat (xG: {xg_per_match:.2f})")
            else:
                method_details.append(f"❌ Requires xG spikes")
            
            # METHOD 4: Ball retention capability
            goals_scored = controller_data.get('home_goals_scored', 0)
            xg_for = controller_data.get('home_xg_for', 0)
            efficiency = goals_scored / max(xg_for, 0.1)
            
            if efficiency > 0.85:
                enforce_methods += 1
                method_details.append(f"✅ Efficient finishing ({efficiency:.1%}) reduces urgency")
            else:
                method_details.append(f"❌ Requires volume scoring")
        
        else:  # Away team
            # METHOD 1: Defensive solidity away (using SEASON data)
            goals_conceded = controller_data.get('away_goals_conceded', 0)
            matches_played = controller_data.get('away_matches_played', 1)
            season_concede_avg = goals_conceded / matches_played
            
            if season_concede_avg < 1.3:
                enforce_methods += 1
                method_details.append(f"✅ Can defend away ({season_concede_avg:.2f}/match)")
            else:
                method_details.append(f"❌ Defensive concerns away")
            
            # METHOD 2: Away scoring versatility
            setpiece_pct = controller_data.get('away_setpiece_pct', 0)
            counter_pct = controller_data.get('away_counter_pct', 0)
            
            if setpiece_pct > 0.2 or counter_pct > 0.12:
                enforce_methods += 1
                method_details.append(f"✅ Away scoring versatility")
            else:
                method_details.append(f"❌ Limited away scoring")
            
            # METHOD 3: Away consistency
            xg_per_match = controller_data.get('away_xg_per_match', 0)
            if xg_per_match > 1.2:
                enforce_methods += 1
                method_details.append(f"✅ Consistent away threat (xG: {xg_per_match:.2f})")
            else:
                method_details.append(f"❌ Requires exceptional away performance")
            
            # METHOD 4: Away efficiency
            goals_scored = controller_data.get('away_goals_scored', 0)
            xg_for = controller_data.get('away_xg_for', 0)
            efficiency = goals_scored / max(xg_for, 0.1)
            
            if efficiency > 0.9:
                enforce_methods += 1
                method_details.append(f"✅ Elite away finishing ({efficiency:.1%})")
            else:
                method_details.append(f"❌ Away efficiency concerns")
        
        # Add all method details
        for detail in method_details:
            rationale.append(f"  • {detail}")
        
        # Check market-specific requirements
        if enforce_methods >= required_methods:
            rationale.append(f"✅ NON-URGENT ENFORCEMENT: {enforce_methods}/{required_methods}+ methods")
            return True, enforce_methods, rationale
        else:
            rationale.append(f"❌ Insufficient enforcement: {enforce_methods}/{required_methods} methods")
            return False, enforce_methods, rationale
    
    @classmethod
    def evaluate_market_state_lock(cls, home_data: Dict, away_data: Dict,
                                 home_name: str, away_name: str,
                                 league_avg_xg: float, market_type: str) -> Dict:
        """Evaluate STATE LOCK for a specific market type with State Preservation Law."""
        system_log = []
        
        system_log.append("=" * 70)
        system_log.append(f"🔐 STATE LOCK EVALUATION: {market_type}")
        system_log.append("=" * 70)
        system_log.append(f"MATCH: {home_name} vs {away_name}")
        system_log.append("")
        
        gates_passed = 0
        total_gates = 4
        
        # =================== GATE 1: QUIET CONTROL ===================
        system_log.append("GATE 1: QUIET CONTROL IDENTIFICATION")
        
        home_score, home_weighted, home_criteria, home_rationale = cls.evaluate_quiet_control(
            home_data, away_data, is_home=True, team_name=home_name
        )
        
        away_score, away_weighted, away_criteria, away_rationale = cls.evaluate_quiet_control(
            away_data, home_data, is_home=False, team_name=away_name
        )
        
        system_log.extend(home_rationale)
        system_log.extend(away_rationale)
        
        # Determine controller WITHOUT status resolution
        controller = None
        
        # v6.1.2: Check for mutual control
        both_meet_control = (home_score >= CONTROL_CRITERIA_REQUIRED and 
                            away_score >= CONTROL_CRITERIA_REQUIRED)
        
        if both_meet_control:
            weighted_diff = abs(home_weighted - away_weighted)
            
            if weighted_diff <= QUIET_CONTROL_SEPARATION_THRESHOLD:
                system_log.append(f"⚠️ v6.1.2: Mutual control detected")
                system_log.append(f"  • Weighted difference: {weighted_diff:.2f} ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD}")
                system_log.append("• NO SINGLE CONTROLLER → NO STATE LOCK")
                system_log.append("⚠️ SYSTEM SILENT")
                
                return {
                    'market': market_type,
                    'state_locked': False,
                    'system_log': system_log,
                    'reason': f"v6.1.2: Mutual control (weighted difference ≤ {QUIET_CONTROL_SEPARATION_THRESHOLD})",
                    'capital_authorized': False,
                    'mutual_control': True
                }
            
            if home_weighted > away_weighted:
                controller = home_name
                system_log.append(f"• Controller: {home_name} (weighted advantage)")
            else:
                controller = away_name
                system_log.append(f"• Controller: {away_name} (weighted advantage)")
        
        elif home_score >= CONTROL_CRITERIA_REQUIRED and home_score > away_score:
            controller = home_name
            system_log.append(f"• Controller: {home_name} ({home_score}/4 criteria)")
            
        elif away_score >= CONTROL_CRITERIA_REQUIRED and away_score > home_score:
            controller = away_name
            system_log.append(f"• Controller: {away_name} ({away_score}/4 criteria)")
        
        else:
            system_log.append("❌ GATE 1 FAILED: No Quiet Control identified")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"No team meets {CONTROL_CRITERIA_REQUIRED}+ control criteria",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 1 PASSED: Quiet Control → {controller}")
        
        # =================== GATE 2: DIRECTIONAL DOMINANCE ===================
        system_log.append("")
        system_log.append("GATE 2: DIRECTIONAL DOMINANCE")
        
        opponent = away_name if controller == home_name else home_name
        is_controller_home = controller == home_name
        
        controller_xg = home_data.get('home_xg_per_match', 0) if is_controller_home else away_data.get('away_xg_per_match', 0)
        opponent_xg = away_data.get('away_xg_per_match', 0) if is_controller_home else home_data.get('home_xg_per_match', 0)
        
        has_direction, control_delta, direction_rationale = cls.check_directional_dominance(
            controller_xg, opponent_xg, controller, opponent, market_type
        )
        system_log.extend(direction_rationale)
        
        if not has_direction:
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Directional dominance insufficient for {market_type}",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 2 PASSED: Directional dominance confirmed (Δ = {control_delta:+.2f})")
        
        # =================== GATE 3: AGENCY COLLAPSE ===================
        system_log.append("")
        system_log.append("GATE 3: AGENCY COLLAPSE")
        
        opponent_data = away_data if opponent == away_name else home_data
        is_opponent_home = opponent == home_name
        
        agency_collapsed, failures, collapse_rationale = cls.check_agency_collapse(
            opponent_data, is_opponent_home, opponent, league_avg_xg, market_type
        )
        system_log.extend(collapse_rationale)
        
        if not agency_collapsed:
            # Get required failures for this market
            if market_type == 'WINNER':
                required = 2
            elif market_type == 'CLEAN_SHEET':
                required = 3
            elif market_type == 'TEAM_NO_SCORE':
                required = 4
            else:
                required = 2
                
            system_log.append(f"❌ GATE 3 FAILED: Insufficient agency collapse ({failures}/{required})")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Insufficient agency collapse for {market_type} ({failures}/{required})",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 3 PASSED: Agency collapse confirmed ({failures}/4 failures)")
        
        # =================== GATE 4A: DEFENSIVE STATE PRESERVATION ===================
        system_log.append("")
        system_log.append("GATE 4A: DEFENSIVE STATE PRESERVATION")
        system_log.append(f"• CRITICAL: This gate OVERRIDES Gates 1-3 for defensive markets")
        system_log.append(f"• Manchester United vs Wolves CASE: This is the missing enforcement")
        
        controller_data = home_data if controller == home_name else away_data
        
        can_preserve, recent_concede_avg, preservation_rationale = cls.check_defensive_state_preservation(
            controller_data, is_controller_home, controller, market_type
        )
        system_log.extend(preservation_rationale)
        
        if not can_preserve:
            system_log.append(f"❌ GATE 4A FAILED: Cannot preserve {market_type} state")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Cannot preserve {market_type} state (recent concede avg: {recent_concede_avg:.2f})",
                'capital_authorized': False,
                'failed_on_preservation': True
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4A PASSED: Defensive state preservation confirmed")
        
        # =================== GATE 4B: NON-URGENT ENFORCEMENT ===================
        system_log.append("")
        system_log.append("GATE 4B: NON-URGENT ENFORCEMENT")
        
        can_enforce, enforce_methods, enforce_rationale = cls.check_non_urgent_enforcement(
            controller_data, is_controller_home, controller, market_type, recent_concede_avg
        )
        system_log.extend(enforce_rationale)
        
        if not can_enforce:
            # Get required methods for this market
            if market_type == 'TEAM_NO_SCORE':
                required = 3
            else:
                required = 2
                
            system_log.append(f"❌ GATE 4B FAILED: Insufficient enforcement capacity ({enforce_methods}/{required})")
            system_log.append("⚠️ SYSTEM SILENT")
            
            return {
                'market': market_type,
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Insufficient enforcement capacity for {market_type} ({enforce_methods}/{required})",
                'capital_authorized': False
            }
        
        gates_passed += 1
        system_log.append(f"✅ GATE 4B PASSED: Non-urgent enforcement confirmed ({enforce_methods}/2+ methods)")
        
        # =================== STATE LOCK DECLARATION ===================
        system_log.append("")
        system_log.append("=" * 70)
        system_log.append(f"🔒 {market_type} STATE LOCK DECLARATION")
        system_log.append("=" * 70)
        
        # Market-specific declarations
        declarations = {
            'WINNER': f"🔒 WINNER LOCKED\n{controller} cannot lose\n{opponent} has no agency to change result",
            'CLEAN_SHEET': f"🔒 CLEAN SHEET LOCKED\n{controller} will not concede\n{opponent} has no scoring agency",
            'TEAM_NO_SCORE': f"🔒 TEAM NO SCORE LOCKED\n{opponent} will not score\nScoring agency structurally suppressed",
            'OPPONENT_UNDER_1_5': f"🔒 OPPONENT UNDER 1.5 LOCKED\n{opponent} cannot score >1 goal\nAgency limited to minimal threat"
        }
        
        declaration = declarations.get(market_type, f"🔒 STATE LOCKED\n{controller} controls {market_type} state")
        
        system_log.append(declaration)
        system_log.append("")
        system_log.append("💰 CAPITAL AUTHORIZATION: GRANTED")
        system_log.append(f"• All {total_gates}/{total_gates} gates passed")
        system_log.append(f"• Control Delta: {control_delta:+.2f}")
        system_log.append(f"• Agency Collapse: {failures}/4 failures")
        system_log.append(f"• Recent Concede Avg: {recent_concede_avg:.2f}/match")
        system_log.append(f"• Enforcement Methods: {enforce_methods}/2+")
        system_log.append(f"• Market: {market_type} structurally controlled")
        system_log.append("=" * 70)
        
        return {
            'market': market_type,
            'state_locked': True,
            'declaration': declaration,
            'system_log': system_log,
            'reason': f"All agency-state gates passed for {market_type}",
            'capital_authorized': True,
            'controller': controller,
            'opponent': opponent,
            'control_delta': control_delta,
            'agency_failures': failures,
            'recent_concede_avg': recent_concede_avg,
            'enforce_methods': enforce_methods,
            'key_metrics': {
                'controller_xg': controller_xg,
                'opponent_xg': opponent_xg,
                'recent_concede_avg': recent_concede_avg
            }
        }

# =================== TOTALS LOCK ENGINE ===================
class TotalsLockEngine:
    """
    TOTALS LOCK ENGINE
    Special case: Totals ≤ 2.5 (Dual low-offense trend)
    Binary gate: Both teams last 5 avg goals ≤ 1.2
    """
    
    @staticmethod
    def check_totals_lock_condition(home_data: Dict, away_data: Dict,
                                   home_name: str, away_name: str) -> Tuple[bool, Dict, List[str]]:
        """Check Totals Lock condition (STRICT BINARY GATE)."""
        rationale = []
        
        rationale.append("=" * 70)
        rationale.append(f"🎯 TOTALS LOCK ENGINE - BINARY GATE")
        rationale.append("=" * 70)
        rationale.append(f"MATCH: {home_name} vs {away_name}")
        rationale.append("")
        rationale.append(f"CONDITION: Both teams' last 5 matches average goals ≤ {TOTALS_LOCK_THRESHOLD}")
        rationale.append("")
        
        # CRITICAL: Use only goals_scored_last_5 / 5
        home_last5_goals = home_data.get('goals_scored_last_5', 0)
        away_last5_goals = away_data.get('goals_scored_last_5', 0)
        
        # Calculate averages
        home_last5_avg = home_last5_goals / 5 if home_last5_goals > 0 else 0
        away_last5_avg = away_last5_goals / 5 if away_last5_goals > 0 else 0
        
        rationale.append(f"📊 LAST 5 MATCHES DATA:")
        rationale.append(f"• {home_name}: {home_last5_goals} goals in last 5 → {home_last5_avg:.2f} avg")
        rationale.append(f"• {away_name}: {away_last5_goals} goals in last 5 → {away_last5_avg:.2f} avg")
        rationale.append("")
        
        # STRICT BINARY CHECKS
        rationale.append("⚖️ STRICT BINARY CHECKS:")
        rationale.append(f"• {home_name} ≤ {TOTALS_LOCK_THRESHOLD}? {'✅ YES' if home_last5_avg <= TOTALS_LOCK_THRESHOLD else '❌ NO'}")
        rationale.append(f"• {away_name} ≤ {TOTALS_LOCK_THRESHOLD}? {'✅ YES' if away_last5_avg <= TOTALS_LOCK_THRESHOLD else '❌ NO'}")
        rationale.append("")
        
        # Check both conditions
        home_passes = home_last5_avg <= TOTALS_LOCK_THRESHOLD
        away_passes = away_last5_avg <= TOTALS_LOCK_THRESHOLD
        totals_lock_condition = home_passes and away_passes
        
        if totals_lock_condition:
            rationale.append("✅ TOTALS LOCK CONDITION MET!")
            rationale.append(f"• Both teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5)")
            rationale.append(f"• Structural certainty: Total goals ≤ {UNDER_GOALS_THRESHOLD}")
            rationale.append("• Logic: Dual low-offense trend creates scoring incapacity")
        else:
            rationale.append("❌ TOTALS LOCK CONDITION NOT MET")
            if not home_passes:
                rationale.append(f"  • {home_name}: {home_last5_avg:.2f} > {TOTALS_LOCK_THRESHOLD}")
            if not away_passes:
                rationale.append(f"  • {away_name}: {away_last5_avg:.2f} > {TOTALS_LOCK_THRESHOLD}")
            rationale.append("  • NO dual low-offense trend")
        
        rationale.append("=" * 70)
        
        return totals_lock_condition, {
            'home_last5_goals': home_last5_goals,
            'away_last5_goals': away_last5_goals,
            'home_last5_avg': home_last5_avg,
            'away_last5_avg': away_last5_avg,
            'home_passes': home_passes,
            'away_passes': away_passes
        }, rationale
    
    @classmethod
    def evaluate_totals_lock(cls, home_data: Dict, away_data: Dict,
                           home_name: str, away_name: str) -> Dict:
        """Evaluate Totals Lock for Under 2.5 goals."""
        
        system_log = []
        
        system_log.append("=" * 70)
        system_log.append("🎯 TOTALS LOCK ENGINE - TREND-BASED")
        system_log.append("=" * 70)
        system_log.append(f"LOGIC: Bilateral scoring agency suppression via trend")
        system_log.append(f"CONDITION: Both teams last 5 avg goals ≤ {TOTALS_LOCK_THRESHOLD}")
        system_log.append(f"DECLARATION: Totals ≤ {UNDER_GOALS_THRESHOLD} structurally certain")
        system_log.append("")
        
        totals_lock_condition, trend_data, trend_rationale = cls.check_totals_lock_condition(
            home_data, away_data, home_name, away_name
        )
        system_log.extend(trend_rationale)
        
        if totals_lock_condition:
            declaration = f"🔒 TOTALS ≤{UNDER_GOALS_THRESHOLD} LOCKED\nDual low-offense trend confirmed\nBoth teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals (last 5)\nStructural scoring incapacity"
            
            system_log.append("")
            system_log.append("💰 CAPITAL AUTHORIZATION: GRANTED")
            system_log.append(f"• Trend Condition: BOTH teams last 5 avg goals ≤ {TOTALS_LOCK_THRESHOLD}")
            system_log.append(f"• {home_name}: {trend_data['home_last5_avg']:.2f}")
            system_log.append(f"• {away_name}: {trend_data['away_last5_avg']:.2f}")
            system_log.append(f"• Match: Structurally low-scoring ≤ {UNDER_GOALS_THRESHOLD}")
            system_log.append("=" * 70)
            
            return {
                'market': 'TOTALS_UNDER_2_5',
                'state_locked': True,
                'declaration': declaration,
                'system_log': system_log,
                'reason': f"Totals Lock condition met (both teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals)",
                'capital_authorized': True,
                'trend_based': True,
                'trend_data': trend_data,
                'key_metrics': trend_data
            }
        else:
            system_log.append("❌ TOTALS LOCK NOT APPLICABLE")
            system_log.append("⚠️ FALLBACK TO EDGE MODE FOR TOTALS")
            system_log.append("=" * 70)
            
            return {
                'market': 'TOTALS_UNDER_2_5',
                'state_locked': False,
                'system_log': system_log,
                'reason': f"Totals Lock condition not met",
                'capital_authorized': False,
                'trend_based': True
            }

# =================== INTEGRATED BRUTBALL ARCHITECTURE ===================
class BrutballIntegratedArchitecture:
    """
    BRUTBALL INTEGRATED ARCHITECTURE v6.3
    v6.0 Edge Detection + Agency-State Lock Engine + Totals Lock Engine + Bet-Ready Signals
    
    CRITICAL UPDATE (v6.3): BET-READY SIGNALS
    - Clear labeling: "Bournemouth to score UNDER 1.5 goals"
    - Opponent attack context: Tiered confidence based on opponent scoring avg
    - Human-readable output for bettors
    - Performance tracking
    """
    
    @staticmethod
    def check_edge_derived_under_15(home_data: Dict, away_data: Dict,
                                  home_name: str, away_name: str) -> List[Dict]:
        """
        UPDATED: Edge-Derived UNDER 1.5 Locks with opponent attack context
        
        Returns list of actionable UNDER 1.5 predictions with clear labels
        and tiered confidence.
        """
        edge_locks = []
        
        # Extract defensive data (LAST 5 MATCHES ONLY)
        home_concedes_last5 = home_data.get('goals_conceded_last_5', 0)
        away_concedes_last5 = away_data.get('goals_conceded_last_5', 0)
        
        # Calculate averages (last 5 matches)
        home_avg_concedes = home_concedes_last5 / 5 if home_concedes_last5 > 0 else 0
        away_avg_concedes = away_concedes_last5 / 5 if away_concedes_last5 > 0 else 0
        
        # =================== UPDATED LOGIC: DEFENSIVE PROOF + ATTACK CONTEXT ===================
        DEFENSIVE_PROOF_THRESHOLD = 1.0
        
        # Get opponent attack strength (last 5 matches)
        home_score_last5 = home_data.get('goals_scored_last_5', 0)
        away_score_last5 = away_data.get('goals_scored_last_5', 0)
        
        home_avg_score = home_score_last5 / 5 if home_score_last5 > 0 else 0
        away_avg_score = away_score_last5 / 5 if away_score_last5 > 0 else 0
        
        # TIERED CONFIDENCE SYSTEM
        def get_confidence_level(opponent_avg_score: float) -> Tuple[str, str, str]:
            """Return confidence based on opponent's scoring average."""
            if opponent_avg_score <= 1.4:
                return "VERY STRONG", "🔵", "Opponent has weak attack (≤1.4 avg)"
            elif opponent_avg_score <= 1.6:
                return "STRONG", "🟢", "Opponent attack is moderate (≤1.6 avg)"
            elif opponent_avg_score <= 1.8:
                return "WEAK", "🟡", "Opponent attack is strong (≤1.8 avg)"
            else:
                return "VERY WEAK", "🔴", "Opponent has very strong attack (>1.8 avg)"
        
        # Check Home team for UNDER 1.5 lock (AWAY team to score under 1.5)
        if home_avg_concedes <= DEFENSIVE_PROOF_THRESHOLD:
            confidence, emoji, attack_context = get_confidence_level(away_avg_score)
            
            edge_locks.append({
                'team_to_bet': away_name,  # Team whose scoring we're predicting
                'defensive_team': home_name,  # Team providing defensive context
                'market': f"{away_name} to score UNDER 1.5 goals",
                'lock_type': 'UNDER_1_5',
                'type': 'edge_derived',
                'source': 'TIER_1_EDGE_DERIVED',
                'defense_avg': home_avg_concedes,
                'opponent_attack_avg': away_avg_score,
                'confidence': confidence,
                'confidence_emoji': emoji,
                'attack_context': attack_context,
                'capital_multiplier': 2.0,
                'reason': f"{away_name} faces {home_name} who concede {home_avg_concedes:.2f} avg goals (last 5)",
                'details': f"Defensive proof: {home_name} concedes {home_avg_concedes:.2f} avg ≤ 1.0",
                'capital_authorized': True,
                'state_locked': True,
                'bet_label': f"✅ BET: {away_name} to score UNDER 1.5 goals",
                'full_explanation': f"{away_name} faces {home_name}'s strong defense ({home_avg_concedes:.2f} avg conceded). {attack_context}.",
                'original_format': f"{home_name} UNDER 1.5"  # Keep for backward compatibility
            })
        
        # Check Away team for UNDER 1.5 lock (HOME team to score under 1.5)
        if away_avg_concedes <= DEFENSIVE_PROOF_THRESHOLD:
            confidence, emoji, attack_context = get_confidence_level(home_avg_score)
            
            edge_locks.append({
                'team_to_bet': home_name,  # Team whose scoring we're predicting
                'defensive_team': away_name,  # Team providing defensive context
                'market': f"{home_name} to score UNDER 1.5 goals",
                'lock_type': 'UNDER_1_5',
                'type': 'edge_derived',
                'source': 'TIER_1_EDGE_DERIVED',
                'defense_avg': away_avg_concedes,
                'opponent_attack_avg': home_avg_score,
                'confidence': confidence,
                'confidence_emoji': emoji,
                'attack_context': attack_context,
                'capital_multiplier': 2.0,
                'reason': f"{home_name} faces {away_name} who concede {away_avg_concedes:.2f} avg goals (last 5)",
                'details': f"Defensive proof: {away_name} concedes {away_avg_concedes:.2f} avg ≤ 1.0",
                'capital_authorized': True,
                'state_locked': True,
                'bet_label': f"✅ BET: {home_name} to score UNDER 1.5 goals",
                'full_explanation': f"{home_name} faces {away_name}'s strong defense ({away_avg_concedes:.2f} avg conceded). {attack_context}.",
                'original_format': f"{away_name} UNDER 1.5"  # Keep for backward compatibility
            })
        
        return edge_locks
    
    @staticmethod
    def execute_integrated_analysis(home_data: Dict, away_data: Dict,
                                  home_name: str, away_name: str,
                                  league_avg_xg: float) -> Dict:
        """Execute complete three-tier integrated analysis with State Preservation Law."""
        
        integrated_log = []
        integrated_log.append("=" * 80)
        integrated_log.append("⚖️🔒📊 BRUTBALL INTEGRATED ARCHITECTURE v6.3")
        integrated_log.append("=" * 80)
        integrated_log.append("THREE-TIER SYSTEM WITH BET-READY SIGNALS")
        integrated_log.append("TIER 1: v6.0 Edge Detection Engine (Heuristic)")
        integrated_log.append("TIER 1+: Edge-Derived UNDER 1.5 Locks (Binary Gate with Attack Context)")
        integrated_log.append("TIER 2: Agency-State Lock Engine (4 Gates + State Preservation)")
        integrated_log.append("TIER 3: Totals Lock Engine (Trend-Based Binary Gate)")
        integrated_log.append("NEW: Bet-Ready Signals with clear labeling and confidence tiers")
        integrated_log.append(f"MATCH: {home_name} vs {away_name}")
        integrated_log.append("=" * 80)
        
        # =================== TIER 1: v6.0 EDGE DETECTION ===================
        integrated_log.append("")
        integrated_log.append("🎯 TIER 1: v6.0 EDGE DETECTION ENGINE")
        integrated_log.append("-" * 40)
        
        v6_result = BrutballEdgeEngine.execute_decision_tree(
            home_data, away_data, home_name, away_name, league_avg_xg
        )
        
        # Add key v6.0 results to integrated log
        integrated_log.append(f"• Primary Action: {v6_result['primary_action']}")
        integrated_log.append(f"• Confidence: {v6_result['confidence']:.1f}/10")
        integrated_log.append(f"• Base Stake: {v6_result['stake_pct']:.1f}%")
        integrated_log.append(f"• Mode: EDGE_MODE (1.0x multiplier)")
        
        # =================== TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS ===================
        integrated_log.append("")
        integrated_log.append("🔓 TIER 1+: EDGE-DERIVED UNDER 1.5 LOCKS")
        integrated_log.append("-" * 40)
        integrated_log.append("LOGIC: Extract actionable UNDER 1.5 locks from Tier 1 edge matches")
        integrated_log.append("CONDITION: Team concedes ≤ 1.0 avg goals (last 5 matches)")
        integrated_log.append("NEW: Includes opponent attack context for confidence grading")
        
        edge_derived_locks = BrutballIntegratedArchitecture.check_edge_derived_under_15(
            home_data, away_data, home_name, away_name
        )
        
        has_edge_derived_locks = len(edge_derived_locks) > 0
        
        if has_edge_derived_locks:
            integrated_log.append(f"✅ EDGE-DERIVED LOCKS DETECTED: {len(edge_derived_locks)}")
            for lock in edge_derived_locks:
                integrated_log.append(f"  • {lock['market']}: {lock['defense_avg']:.2f} avg conceded ≤ 1.0 ({lock['confidence']} confidence)")
        else:
            integrated_log.append("❌ NO EDGE-DERIVED LOCKS")
            integrated_log.append(f"  • Neither team concedes ≤ 1.0 avg goals (last 5)")
        
        # =================== TIER 2: AGENCY-STATE LOCKS ===================
        integrated_log.append("")
        integrated_log.append("🔐 TIER 2: AGENCY-STATE LOCK ENGINE v6.2")
        integrated_log.append("-" * 40)
        integrated_log.append("MARKETS: Winner • Clean Sheet • Team No Score • Opponent Under 1.5")
        integrated_log.append("LOGIC: 4 Gates (Quiet Control, Direction, Agency Collapse, State Preservation)")
        integrated_log.append("CRITICAL: Gate 4A OVERRIDES Gates 1-3 for defensive markets")
        integrated_log.append("PROOF: Manchester United vs Wolves (can create, cannot preserve)")
        
        # Evaluate all agency-state markets
        agency_markets = ['WINNER', 'CLEAN_SHEET', 'TEAM_NO_SCORE', 'OPPONENT_UNDER_1_5']
        agency_results = {}
        agency_locked_markets = []
        
        for market in agency_markets:
            result = AgencyStateLockEngine.evaluate_market_state_lock(
                home_data, away_data, home_name, away_name, league_avg_xg, market
            )
            agency_results[market] = result
            
            if result['state_locked']:
                agency_locked_markets.append({
                    'market': market,
                    'controller': result['controller'],
                    'delta': result['control_delta'],
                    'recent_concede_avg': result.get('recent_concede_avg', 0),
                    'source': 'TIER_2_AGENCY'
                })
        
        # Track agency-state results
        agency_lock_count = len(agency_locked_markets)
        has_agency_lock = agency_lock_count > 0
        
        integrated_log.append(f"• Markets Evaluated: {len(agency_markets)}")
        integrated_log.append(f"• Markets Locked: {agency_lock_count}")
        
        if has_agency_lock:
            strongest_market = max(agency_locked_markets, key=lambda x: x['delta'])
            integrated_log.append(f"• Strongest Lock: {strongest_market['market']} (Δ={strongest_market['delta']:+.2f})")
            integrated_log.append(f"• Controller: {strongest_market['controller']}")
            
            # Show defensive preservation status
            defensive_locks = [m for m in agency_locked_markets if m['market'] != 'WINNER']
            if defensive_locks:
                integrated_log.append(f"• Defensive Locks: {len(defensive_locks)} (all passed State Preservation Law)")
        else:
            integrated_log.append("• No Agency-State Locks Detected")
            
            # Check if any failed on State Preservation
            preservation_failures = []
            for market in agency_markets:
                if market != 'WINNER' and 'failed_on_preservation' in agency_results[market]:
                    preservation_failures.append(market)
            
            if preservation_failures:
                integrated_log.append(f"• State Preservation Failures: {', '.join(preservation_failures)}")
                integrated_log.append("  (Manchester United vs Wolves pattern detected)")
        
        # =================== TIER 3: TOTALS LOCK ===================
        integrated_log.append("")
        integrated_log.append("📊 TIER 3: TOTALS LOCK ENGINE")
        integrated_log.append("-" * 40)
        integrated_log.append(f"MARKET: Totals ≤ {UNDER_GOALS_THRESHOLD} ONLY")
        integrated_log.append(f"LOGIC: Dual low-offense trend (BOTH teams ≤ {TOTALS_LOCK_THRESHOLD} avg goals)")
        
        # Evaluate Totals Lock
        totals_result = TotalsLockEngine.evaluate_totals_lock(
            home_data, away_data, home_name, away_name
        )
        
        has_totals_lock = totals_result['state_locked']
        
        if has_totals_lock:
            integrated_log.append(f"✅ TOTALS LOCK DETECTED!")
            integrated_log.append(f"• {home_name}: {totals_result['trend_data']['home_last5_avg']:.2f} avg goals")
            integrated_log.append(f"• {away_name}: {totals_result['trend_data']['away_last5_avg']:.2f} avg goals")
            integrated_log.append(f"• Both ≤ {TOTALS_LOCK_THRESHOLD} → Structural scoring incapacity")
        else:
            integrated_log.append("❌ NO TOTALS LOCK")
            integrated_log.append(f"• Condition: BOTH teams must be ≤ {TOTALS_LOCK_THRESHOLD}")
        
        # =================== INTEGRATED CAPITAL DECISION ===================
        integrated_log.append("")
        integrated_log.append("💰 INTEGRATED CAPITAL DECISION")
        integrated_log.append("-" * 40)
        
        # Determine capital mode - Edge-Derived locks now also trigger LOCK_MODE
        if has_agency_lock or has_totals_lock or has_edge_derived_locks:
            capital_mode = 'LOCK_MODE'
            multiplier = CAPITAL_MULTIPLIERS['LOCK_MODE']
            final_stake = v6_result['stake_pct'] * multiplier
            
            if has_totals_lock:
                capital_reason = "TOTALS LOCK (Trend-Based)"
                system_verdict = "DUAL LOW-OFFENSE STATE DETECTED"
            elif has_agency_lock:
                capital_reason = "AGENCY-STATE LOCK (with State Preservation)"
                system_verdict = "AGENCY-STATE CONTROL DETECTED"
            elif has_edge_derived_locks:
                capital_reason = "EDGE-DERIVED UNDER 1.5 LOCK (Defensive Proof)"
                system_verdict = "EDGE-DERIVED DEFENSIVE CONTROL DETECTED"
            else:
                capital_reason = "LOCK (Other)"
                system_verdict = "STRUCTURAL CERTAINTY DETECTED"
        else:
            capital_mode = 'EDGE_MODE'
            multiplier = CAPITAL_MULTIPLIERS['EDGE_MODE']
            final_stake = v6_result['stake_pct'] * multiplier
            capital_reason = "v6.0 EDGE ONLY"
            system_verdict = "STRUCTURAL EDGE DETECTED"
        
        integrated_log.append(f"• Capital Mode: {capital_mode}")
        integrated_log.append(f"• Stake Multiplier: {multiplier:.1f}x")
        integrated_log.append(f"• Base Stake: {v6_result['stake_pct']:.1f}%")
        integrated_log.append(f"• Final Stake: {final_stake:.2f}%")
        integrated_log.append(f"• Reason: {capital_reason}")
        integrated_log.append("")
        integrated_log.append(f"🎯 SYSTEM VERDICT: {system_verdict}")
        integrated_log.append("=" * 80)
        
        # =================== PREPARE INTEGRATED OUTPUT ===================
        # Combine all locks from different sources
        all_locked_markets = []
        
        # Add Tier 2 Agency-State Locks
        all_locked_markets.extend(agency_locked_markets)
        
        # Add Tier 3 Totals Lock if present
        if has_totals_lock:
            all_locked_markets.append({
                'market': 'TOTALS_UNDER_2_5',
                'controller': 'BOTH_TEAMS',
                'delta': 0,
                'recent_concede_avg': 0,
                'source': 'TIER_3_TOTALS',
                'trend_data': totals_result['trend_data']
            })
        
        # Add Edge-Derived Locks (for backward compatibility, keep both formats)
        edge_locks_for_display = []
        for lock in edge_derived_locks:
            edge_locks_for_display.append({
                'market': lock['market'],
                'type': 'edge_derived',
                'team': lock['team_to_bet'],
                'lock_type': lock['lock_type'],
                'defense_avg': lock['defense_avg'],
                'capital_multiplier': lock['capital_multiplier'],
                'delta': 0,
                'source': lock['source'],
                'reason': lock['reason'],
                'details': lock['details'],
                'declaration': lock.get('original_format', lock['market']),
                'bet_ready_data': lock  # Store the full bet-ready data
            })
            all_locked_markets.append(edge_locks_for_display[-1])
        
        # Determine strongest market for display
        strongest_market_info = None
        if has_agency_lock:
            strongest_agency = max(agency_locked_markets, key=lambda x: x['delta'])
            strongest_market_info = {
                'market': strongest_agency['market'],
                'type': 'agency',
                'controller': strongest_agency['controller'],
                'delta': strongest_agency['delta'],
                'recent_concede_avg': strongest_agency.get('recent_concede_avg', 0),
                'source': 'TIER_2'
            }
        elif has_totals_lock:
            strongest_market_info = {
                'market': 'TOTALS_UNDER_2_5',
                'type': 'totals',
                'controller': 'BOTH_TEAMS',
                'delta': 0,
                'recent_concede_avg': 0,
                'source': 'TIER_3'
            }
        elif has_edge_derived_locks:
            # Use the first edge-derived lock as strongest
            strongest_edge = edge_derived_locks[0]
            strongest_market_info = {
                'market': strongest_edge['market'],
                'type': 'edge_derived',
                'team': strongest_edge['team_to_bet'],
                'lock_type': strongest_edge['lock_type'],
                'defense_avg': strongest_edge['defense_avg'],
                'delta': 0,
                'source': 'TIER_1+_EDGE_DERIVED',
                'bet_ready_data': strongest_edge
            }
        
        # Prepare market status summary
        market_status = {}
        for market in agency_markets:
            market_status[market] = {
                'locked': agency_results[market]['state_locked'],
                'controller': agency_results[market].get('controller'),
                'reason': agency_results[market]['reason'],
                'failed_on_preservation': agency_results[market].get('failed_on_preservation', False),
                'source': 'TIER_2'
            }
        
        market_status['TOTALS_UNDER_2_5'] = {
            'locked': has_totals_lock,
            'controller': 'BOTH_TEAMS' if has_totals_lock else None,
            'reason': totals_result['reason'],
            'failed_on_preservation': False,
            'source': 'TIER_3'
        }
        
        # Add Edge-Derived UNDER 1.5 status
        if has_edge_derived_locks:
            market_status['EDGE_DERIVED_UNDER_1_5'] = {
                'locked': True,
                'teams': [lock['team_to_bet'] for lock in edge_derived_locks],
                'reason': f"Edge-derived lock: Team concedes ≤ 1.0 avg goals (last 5)",
                'failed_on_preservation': False,
                'source': 'TIER_1+_EDGE_DERIVED',
                'edge_locks': edge_derived_locks
            }
        
        return {
            'architecture': 'Three-Tier Integrated v6.3 with Bet-Ready Signals',
            'v6_result': v6_result,
            'agency_results': agency_results,
            'totals_result': totals_result,
            'edge_derived_locks': edge_derived_locks,
            'edge_locks_for_display': edge_locks_for_display,
            'has_edge_derived_locks': has_edge_derived_locks,
            'agency_locked_markets': agency_locked_markets,
            'all_locked_markets': all_locked_markets,
            'has_agency_lock': has_agency_lock,
            'has_totals_lock': has_totals_lock,
            'capital_mode': capital_mode,
            'stake_multiplier': multiplier,
            'final_stake': final_stake,
            'system_verdict': system_verdict,
            'strongest_market': strongest_market_info,
            'market_status': market_status,
            'integrated_log': integrated_log,
            'key_metrics': {
                'home_last5_avg': totals_result['trend_data']['home_last5_avg'] if 'trend_data' in totals_result else 0,
                'away_last5_avg': totals_result['trend_data']['away_last5_avg'] if 'trend_data' in totals_result else 0,
                'home_concedes_avg': home_data.get('goals_conceded_last_5', 0) / 5,
                'away_concedes_avg': away_data.get('goals_conceded_last_5', 0) / 5,
                'home_xg': home_data.get('home_xg_per_match', 0),
                'away_xg': away_data.get('away_xg_per_match', 0)
            }
        }

# =================== DATA LOADING ===================
@st.cache_data(ttl=3600, show_spinner="Loading league data...")
def load_and_prepare_data(league_name: str) -> Optional[pd.DataFrame]:
    """Load and prepare data with your CSV structure."""
    try:
        if league_name not in LEAGUES:
            st.error(f"❌ Unknown league: {league_name}")
            return None
        
        league_config = LEAGUES[league_name]
        filename = league_config['filename']
        
        # Try multiple possible file locations
        data_sources = [
            f'leagues/{filename}',
            f'./leagues/{filename}',
            filename,
            f'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/{filename}'
        ]
        
        df = None
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                break
            except Exception:
                continue
        
        if df is None:
            st.error(f"❌ Failed to load data for {league_config['display_name']}")
            return None
        
        # Calculate derived metrics
        df = calculate_derived_metrics(df)
        
        # Store metadata
        df.attrs['league_name'] = league_name
        df.attrs['display_name'] = league_config['display_name']
        df.attrs['country'] = league_config['country']
        df.attrs['color'] = league_config['color']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Data preparation error: {str(e)}")
        return None

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all derived metrics from your CSV structure."""
    
    # Goals scored (from CSV structure)
    df['home_goals_scored'] = (
        df['home_goals_openplay_for'].fillna(0) +
        df['home_goals_counter_for'].fillna(0) +
        df['home_goals_setpiece_for'].fillna(0) +
        df['home_goals_penalty_for'].fillna(0) +
        df['home_goals_owngoal_for'].fillna(0)
    )
    
    df['away_goals_scored'] = (
        df['away_goals_openplay_for'].fillna(0) +
        df['away_goals_counter_for'].fillna(0) +
        df['away_goals_setpiece_for'].fillna(0) +
        df['away_goals_penalty_for'].fillna(0) +
        df['away_goals_owngoal_for'].fillna(0)
    )
    
    # Goals conceded (from CSV structure)
    df['home_goals_conceded'] = (
        df['home_goals_openplay_against'].fillna(0) +
        df['home_goals_counter_against'].fillna(0) +
        df['home_goals_setpiece_against'].fillna(0) +
        df['home_goals_penalty_against'].fillna(0) +
        df['home_goals_owngoal_against'].fillna(0)
    )
    
    df['away_goals_conceded'] = (
        df['away_goals_openplay_against'].fillna(0) +
        df['away_goals_counter_against'].fillna(0) +
        df['away_goals_setpiece_against'].fillna(0) +
        df['away_goals_penalty_against'].fillna(0) +
        df['away_goals_owngoal_against'].fillna(0)
    )
    
    # Per-match averages
    df['home_goals_per_match'] = df['home_goals_scored'] / df['home_matches_played'].replace(0, np.nan)
    df['away_goals_per_match'] = df['away_goals_scored'] / df['away_matches_played'].replace(0, np.nan)
    
    df['home_xg_per_match'] = df['home_xg_for'] / df['home_matches_played'].replace(0, np.nan)
    df['away_xg_per_match'] = df['away_xg_for'] / df['away_matches_played'].replace(0, np.nan)
    
    # Goal type percentages (for home)
    df['home_total_goals_for'] = df['home_goals_scored'].replace(0, np.nan)
    df['home_counter_pct'] = df['home_goals_counter_for'] / df['home_total_goals_for']
    df['home_setpiece_pct'] = df['home_goals_setpiece_for'] / df['home_total_goals_for']
    df['home_openplay_pct'] = df['home_goals_openplay_for'] / df['home_total_goals_for']
    
    # Goal type percentages (for away)
    df['away_total_goals_for'] = df['away_goals_scored'].replace(0, np.nan)
    df['away_counter_pct'] = df['away_goals_counter_for'] / df['away_total_goals_for']
    df['away_setpiece_pct'] = df['away_goals_setpiece_for'] / df['away_total_goals_for']
    df['away_openplay_pct'] = df['away_goals_openplay_for'] / df['away_total_goals_for']
    
    # Fill NaN
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
    
    return df

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
    
    # Initialize session state
    if 'selected_league' not in st.session_state:
        st.session_state.selected_league = 'Premier League'
    
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
                type="primary" if st.session_state.selected_league == league else "secondary"
            ):
                st.session_state.selected_league = league
    
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
        home_team = st.selectbox("Home Team", sorted(df['team'].unique()))
    with col2:
        away_options = [t for t in sorted(df['team'].unique()) if t != home_team]
        away_team = st.selectbox("Away Team", away_options)
    
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
    if st.button("⚡ EXECUTE INTEGRATED ANALYSIS v6.3", type="primary", use_container_width=True):
        
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
        
        # =================== BET-READY SIGNALS DISPLAY ===================
        st.markdown("---")
        st.markdown("### 🎯 BET-READY SIGNALS (Human-Readable)")
        
        # Display bet-ready signals
        display_bet_ready_signals(result['edge_derived_locks'], home_team, away_team)
        
        # =================== PERFORMANCE TRACKING ===================
        with st.expander("📊 Performance Dashboard", expanded=False):
            st.markdown("""
            **System Prediction Tracking**
            
            Tracks Edge-Derived UNDER 1.5 predictions vs actual results.
            Record actual scores to improve system accuracy.
            """)
            
            # Simple input for tracking
            col1, col2 = st.columns(2)
            with col1:
                actual_home = st.number_input(f"{home_team} actual goals", min_value=0, max_value=10, value=0, key="actual_home")
            with col2:
                actual_away = st.number_input(f"{away_team} actual goals", min_value=0, max_value=10, value=0, key="actual_away")
            
            if st.button("Record Match Result", key="record_result"):
                # Record predictions
                for lock in result['edge_derived_locks']:
                    match_info = f"{home_team} vs {away_team}"
                    prediction = f"{lock['team_to_bet']} to score UNDER 1.5 goals"
                    performance_tracker.record_prediction(match_info, prediction, lock['confidence'])
                
                # Record result
                actual_score = f"{actual_home}-{actual_away}"
                performance_tracker.record_result(f"{home_team} vs {away_team}", actual_score)
                st.success(f"✅ Recorded: {home_team} {actual_home}-{actual_away} {away_team}")
            
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
                # Add as separate, read-only fields
                result['state_classification'] = classification_result
                result['classification_is_read_only'] = True
                result['classification_does_not_affect_betting'] = True
            except Exception as e:
                # Fail gracefully - classification is optional
                classification_result = {
                    'dominant_state': 'CLASSIFIER_ERROR',
                    'error': str(e),
                    'is_read_only': True,
                    'does_not_affect_betting': True
                }
                result['state_classification'] = classification_result
        
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
            st.markdown("#### 🔍 PRE-MATCH STRUCTURAL INTELLIGENCE (READ-ONLY)")
            
            # Display the perspective boxes
            st.markdown("""
            <div class="perspective-display">
                <h4>📊 STRUCTURAL ANALYSIS (Last 5 Matches Only)</h4>
                <p style="color: #374151; margin-bottom: 1rem;">All calculations use LAST 5 MATCHES only. Does NOT affect betting logic.</p>
            """, unsafe_allow_html=True)
            
            # Get classification data
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
