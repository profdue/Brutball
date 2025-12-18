# app.py - NARRATIVE PREDICTION ENGINE v2.2 - HYBRID EDITION
# ✅ Complete hybrid narrative system with stress-tested discipline

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

# ==============================================
# HYBRID NARRATIVE PREDICTION ENGINE
# ✅ Implements hybrid narratives with 8-point margin rule
# ==============================================

class HybridNarrativePredictionEngine:
    """Enhanced engine with hybrid narrative logic"""
    
    def __init__(self):
        # Manager style database
        self.manager_db = {
            "Mikel Arteta": {"style": "Possession-based & control", "attack": 9, "defense": 7, "press": 8, "possession": 9, "pragmatic": 6},
            "Unai Emery": {"style": "Balanced/Adaptive", "attack": 8, "defense": 8, "press": 7, "possession": 7, "pragmatic": 7},
            "Andoni Iraola": {"style": "Progressive/Developing", "attack": 7, "defense": 6, "press": 9, "possession": 6, "pragmatic": 5},
            "Keith Andrews": {"style": "Balanced/Adaptive", "attack": 6, "defense": 7, "press": 7, "possession": 6, "pragmatic": 7},
            "Fabian Hürzeler": {"style": "Progressive/Developing", "attack": 8, "defense": 6, "press": 7, "possession": 8, "pragmatic": 4},
            "Scott Parker": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 8, "press": 6, "possession": 5, "pragmatic": 8},
            "Enzo Maresca": {"style": "Possession-based & control", "attack": 8, "defense": 7, "press": 7, "possession": 9, "pragmatic": 6},
            "Oliver Glasner": {"style": "Balanced/Adaptive", "attack": 7, "defense": 7, "press": 6, "possession": 7, "pragmatic": 7},
            "David Moyes": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 9, "press": 6, "possession": 5, "pragmatic": 9},
            "Marco Silva": {"style": "Balanced/Adaptive", "attack": 8, "defense": 7, "press": 7, "possession": 7, "pragmatic": 6},
            "Daniel Farke": {"style": "Progressive/Developing", "attack": 8, "defense": 6, "press": 8, "possession": 7, "pragmatic": 5},
            "Arne Slot": {"style": "High press & transition", "attack": 9, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Pep Guardiola": {"style": "Possession-based & control", "attack": 10, "defense": 8, "press": 9, "possession": 10, "pragmatic": 4},
            "Ruben Amorim": {"style": "High press & transition", "attack": 8, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Eddie Howe": {"style": "High press & transition", "attack": 9, "defense": 6, "press": 9, "possession": 7, "pragmatic": 5},
            "Ange Postecoglou": {"style": "High press & transition", "attack": 9, "defense": 5, "press": 9, "possession": 6, "pragmatic": 4},
            "Régis Le Bris": {"style": "Progressive/Developing", "attack": 6, "defense": 7, "press": 7, "possession": 6, "pragmatic": 6},
            "Thomas Frank": {"style": "Balanced/Adaptive", "attack": 7, "defense": 8, "press": 7, "possession": 7, "pragmatic": 7},
            "Graham Potter": {"style": "Balanced/Adaptive", "attack": 7, "defense": 7, "press": 6, "possession": 8, "pragmatic": 7},
            "Vítor Pereira": {"style": "Pragmatic/Defensive", "attack": 5, "defense": 8, "press": 5, "possession": 5, "pragmatic": 8}
        }
        
        # Narrative definitions with hybrid compatibility
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "flow": "• Early pressure from favorite (0-15 mins)\n• Breakthrough before 30 mins\n• Opponent confidence collapses after first goal\n• Additional goals in 35-65 minute window\n• Game effectively over by 70 mins",
                "primary_markets": ["Favorite to win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals for favorite", "Favorite -1.5 Asian handicap"],
                "color": "#4CAF50",
                "eligibility_rules": {
                    "min_attack_diff": 2,
                    "min_possession_diff": 2,
                    "max_favorite_odds": 1.60,
                    "min_favorite_prob": 65,
                    "min_tier": 2
                }
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "primary_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"],
                "color": "#FF5722",
                "btts_range": (65, 75),
                "over25_range": (75, 85)
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "primary_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"],
                "color": "#2196F3"
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both teams (0-30 mins)\n• Midfield battle dominates, few clear chances\n• Set pieces become primary scoring threats\n• First goal (if any) often decisive\n• Late tactical changes unlikely to alter outcome significantly",
                "primary_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0 correct score", "Few goals first half", "Under 1.5 goals"],
                "color": "#9C27B0"
            },
            "CONTROLLED_EDGE": {
                "description": "Grinding Advantage - Favorite edges cautious game",
                "flow": "• Cautious start from both sides\n• Favorite gradually establishes control\n• Breakthrough likely 30-60 mins\n• Limited scoring chances overall\n• Narrow victory or draw",
                "primary_markets": ["Under 2.5 goals", "BTTS: No", "Favorite to win or draw", "First goal 30-60 mins", "Few corners total"],
                "color": "#FF9800"
            }
        }
        
        # Hybrid narrative definitions
        self.hybrid_narratives = {
            "EDGE-CHAOS": {
                "description": "Tight but Explosive - Controlled game that could erupt",
                "parent_narratives": ["CONTROLLED_EDGE", "SHOOTOUT"],
                "color": "#FF9800",  # Orange (mix of CONTROLLED_EDGE orange + SHOOTOUT red)
                "secondary_color": "#FF5722",
                "hybrid_markets": [
                    "Over 2.25 goals (Asian)",
                    "BTTS: Lean Yes", 
                    "Both teams 3+ shots on target",
                    "Game to have 15+ total shots",
                    "Late goal after 70' possible"
                ],
                "flow": "• Cautious start but high attacking quality present\n• Game could remain tight or explode based on early chances\n• Both teams capable of scoring if opportunities arise\n• Higher variance than pure CONTROLLED_EDGE"
            },
            "EDGE-DOMINATION": {
                "description": "Patient Pressure - Controlled favorite grinding down resistance",
                "parent_narratives": ["CONTROLLED_EDGE", "SIEGE"],
                "color": "#FF9800",  # Orange (mix of CONTROLLED_EDGE orange + SIEGE blue)
                "secondary_color": "#2196F3",
                "hybrid_markets": [
                    "Under 2.75 goals (Asian)",
                    "Favorite to win to nil OR 1-0 correct score",
                    "First goal 30-60 minutes",
                    "Favorite to have 60%+ possession",
                    "Under 10.5 corners total"
                ],
                "flow": "• Controlled start with favorite establishing dominance\n• Patient buildup against organized defense\n• Breakthrough likely mid-game rather than early\n• Low-scoring but controlled by favorite"
            },
            "HIGH-TEMPO": {
                "description": "Fast Start, High Scoring - Early goals lead to open game",
                "parent_narratives": ["SHOOTOUT", "BLITZKRIEG"],
                "color": "#FF5722",  # Red (mix of SHOOTOUT red + BLITZKRIEG green)
                "secondary_color": "#4CAF50",
                "hybrid_markets": [
                    "Over 3.0 goals (Asian)",
                    "First goal before 25:00",
                    "Both teams to score",
                    "Game to have 3+ goals",
                    "Favorite to win & Over 2.5"
                ],
                "flow": "• High intensity from start\n• Early goals likely\n• Game opens up after first goal\n• Could become one-sided or remain chaotic"
            }
        }
    
    # ========== CORE CALCULATION METHODS ==========
    
    def calculate_favorite_probability(self, home_odds, away_odds):
        """Convert odds to implied probabilities"""
        if home_odds <= 0 or away_odds <= 0:
            return {
                "home_probability": 50,
                "away_probability": 50,
                "favorite_probability": 50,
                "favorite_is_home": True,
                "favorite_strength": "EVEN",
                "favorite_odds": 2.0
            }
        
        home_implied = 1 / home_odds
        away_implied = 1 / away_odds
        total = home_implied + away_implied
        
        home_prob = home_implied / total * 100
        away_prob = away_implied / total * 100
        
        favorite_prob = max(home_prob, away_prob)
        favorite_is_home = home_prob > away_prob
        favorite_odds = home_odds if favorite_is_home else away_odds
        
        # Strength classification
        if favorite_prob >= 75:
            strength = "ELITE"
        elif favorite_prob >= 65:
            strength = "STRONG"
        elif favorite_prob >= 60:
            strength = "MODERATE"
        elif favorite_prob >= 55:
            strength = "SLIGHT"
        else:
            strength = "EVEN"
        
        return {
            "home_probability": home_prob,
            "away_probability": away_prob,
            "favorite_probability": favorite_prob,
            "favorite_is_home": favorite_is_home,
            "favorite_strength": strength,
            "favorite_odds": favorite_odds,
            "odds_gap": abs(home_odds - away_odds)
        }
    
    def analyze_form(self, form_string):
        """Convert form string to rating"""
        if not form_string or len(form_string) < 3:
            return {"rating": 5, "confidence": 3, "trend": "stable", "scoring_rate": 0.5}
        
        form_map = {"W": 2, "D": 1, "L": 0}
        points = 0
        scoring_games = 0
        
        for char in form_string.upper():
            if char in form_map:
                points += form_map[char]
                if char != 'L':
                    scoring_games += 1
        
        avg_points = points / len(form_string)
        rating = (avg_points / 2) * 10
        scoring_rate = scoring_games / len(form_string)
        
        # Determine trend
        recent = form_string[-3:] if len(form_string) >= 3 else form_string
        win_count = recent.count('W') + recent.count('w')
        
        if win_count >= 2:
            trend = "improving"
        elif 'W' not in recent and 'w' not in recent:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "rating": min(10, rating),
            "confidence": min(10, len(form_string) * 2),
            "trend": trend,
            "points": points,
            "games": len(form_string),
            "scoring_rate": scoring_rate
        }
    
    # ========== NARRATIVE SCORING METHODS ==========
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score"""
        score = 0
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        # 1. FAVORITE STRENGTH
        if prob["favorite_strength"] == "ELITE":
            score += 35
        elif prob["favorite_strength"] == "STRONG":
            score += 25
        elif prob["favorite_strength"] == "MODERATE":
            score += 15
        
        # 2. ATTACK vs DEFENSE MISMATCH
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        away_attack = match_data["away_attack_rating"]
        home_defense = match_data["home_defense_rating"]
        
        home_advantage = home_attack - (10 - away_defense)
        away_advantage = away_attack - (10 - home_defense)
        
        if home_advantage >= 3 or away_advantage >= 3:
            score += 30
        elif home_advantage >= 2 or away_advantage >= 2:
            score += 20
        
        # 3. FORM DOMINANCE
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        form_diff = abs(home_form - away_form)
        score += min(20, form_diff * 2)
        
        # 4. TACTICAL MISMATCH
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        press_diff = abs(home_press - away_press)
        if press_diff >= 3:
            score += 15
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score"""
        score = 0
        
        # 1. BOTH ATTACKING
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        
        if home_attack >= 8 and away_attack >= 8:
            score += 30
        elif home_attack >= 7 and away_attack >= 7:
            score += 20
        elif home_attack >= 6 and away_attack >= 6:
            score += 10
        
        # 2. BOTH WEAK DEFENSE
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        avg_defense = (home_defense + away_defense) / 2
        
        if avg_defense <= 5.5:
            score += 25
        elif avg_defense <= 6.5:
            score += 18
        
        # 3. HIGH PRESS BOTH
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        
        if home_press >= 8 and away_press >= 8:
            score += 20
        elif home_press >= 7 and away_press >= 7:
            score += 12
        
        # 4. HISTORICAL HIGH SCORING
        if match_data["last_h2h_goals"] >= 4:
            score += 15
        elif match_data["last_h2h_goals"] >= 3:
            score += 10
        
        # 5. BTTS HISTORY + FORM
        if match_data["last_h2h_btts"] == "Yes":
            score += 8
        
        home_form = match_data["home_form"]
        away_form = match_data["away_form"]
        home_scoring = sum(1 for r in home_form[-3:] if r.upper() != 'L')
        away_scoring = sum(1 for r in away_form[-3:] if r.upper() != 'L')
        
        if home_scoring >= 2 and away_scoring >= 2:
            score += 7
        
        return min(100, score)
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score"""
        score = 0
        
        # 1. ATTACKER vs DEFENDER MISMATCH
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        away_attack = match_data["away_attack_rating"]
        home_defense = match_data["home_defense_rating"]
        
        if home_attack >= 8 and away_defense >= 8:
            score += 30
        elif home_attack >= 7 and away_defense >= 7:
            score += 20
        
        if away_attack >= 8 and home_defense >= 8:
            score += 25
        
        # 2. POSSESSION DOMINANCE
        home_possession = match_data["home_possession_rating"]
        away_possession = match_data["away_possession_rating"]
        possession_diff = abs(home_possession - away_possession)
        if possession_diff >= 3:
            score += 20
        
        # 3. PRAGMATIC DEFENDER
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if (home_pragmatic >= 7 and away_pragmatic <= 5) or (away_pragmatic >= 7 and home_pragmatic <= 5):
            score += 15
        
        # 4. LOW H2H GOALS
        if match_data["last_h2h_goals"] <= 1:
            score += 15
        elif match_data["last_h2h_goals"] <= 2:
            score += 10
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score"""
        score = 0
        
        # 1. CLOSE MATCH
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        
        if favorite_prob < 52:
            score += 25
        elif favorite_prob < 55:
            score += 18
        
        # 2. BOTH PRAGMATIC
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic >= 7 and away_pragmatic >= 7:
            score += 25
        
        # 3. BOTH STRONG DEFENSE
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        if home_defense >= 8 and away_defense >= 8:
            score += 20
        
        # 4. BOTH MODERATE/LOW ATTACK
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        
        if home_attack <= 6 and away_attack <= 6:
            score += 15
        
        # 5. HISTORICAL LOW SCORING
        if match_data["last_h2h_goals"] <= 2:
            score += 15
        
        return min(100, score)
    
    def calculate_controlled_edge_score(self, match_data):
        """Calculate CONTROLLED EDGE score"""
        score = 0
        
        # 1. SLIGHT FAVORITE
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if 55 <= prob["favorite_probability"] < 65:
            score += 20
        elif 50 <= prob["favorite_probability"] < 55:
            score += 10
        
        # 2. BALANCED TEAMS
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        attack_diff = abs(home_attack - away_attack)
        defense_diff = abs(home_defense - away_defense)
        
        if attack_diff <= 2 and defense_diff <= 2:
            score += 18
        
        # 3. MODERATE DEFENSE BOTH
        if 6 <= home_defense <= 8 and 6 <= away_defense <= 8:
            score += 15
        
        # 4. CONSERVATIVE APPROACH
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic >= 5 and away_pragmatic >= 5:
            score += 12
        
        # 5. CLOSE TABLE POSITIONS
        position_gap = abs(match_data["home_position"] - match_data["away_position"])
        if position_gap <= 3:
            score += 10
        
        # 6. LOW/MODERATE H2H GOALS
        if match_data["last_h2h_goals"] <= 3:
            score += 8
        
        return min(100, score)
    
    # ========== HYBRID LOGIC METHODS ==========
    
    def calculate_all_scores(self, match_data):
        """Calculate all narrative scores"""
        return {
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "SIEGE": self.calculate_siege_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data),
            "CONTROLLED_EDGE": self.calculate_controlled_edge_score(match_data)
        }
    
    def check_hybrid_eligibility(self, scores, tier_level):
        """Check if match qualifies for hybrid narrative"""
        # Get top two narratives
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_narrative, top_score = sorted_scores[0]
        second_narrative, second_score = sorted_scores[1]
        
        # Rule 1: Margin < 8 points
        margin = top_score - second_score
        if margin >= 8:
            return None  # No hybrid, clear winner
        
        # Rule 2: Tier must be 1 or 2
        if tier_level not in [1, 2]:
            return None
        
        # Rule 3: Check if combination is allowed
        allowed_hybrids = self.hybrid_narratives.keys()
        for hybrid_name, hybrid_data in self.hybrid_narratives.items():
            parents = set(hybrid_data["parent_narratives"])
            if {top_narrative, second_narrative} == parents:
                return {
                    "hybrid_type": hybrid_name,
                    "primary_narrative": top_narrative,
                    "secondary_narrative": second_narrative,
                    "primary_score": top_score,
                    "secondary_score": second_score,
                    "margin": margin,
                    "weight": top_score / (top_score + second_score)
                }
        
        return None
    
    def is_blitzkrieg_eligible(self, match_data, prob, tier_level):
        """Check BLITZKRIEG eligibility"""
        if tier_level < 2:
            return False
        
        # Get favorite's ratings
        if prob["favorite_is_home"]:
            attack_rating = match_data["home_attack_rating"]
            defense_rating = match_data["away_defense_rating"]
            possession_rating = match_data["home_possession_rating"]
            opp_possession = match_data["away_possession_rating"]
        else:
            attack_rating = match_data["away_attack_rating"]
            defense_rating = match_data["home_defense_rating"]
            possession_rating = match_data["away_possession_rating"]
            opp_possession = match_data["home_possession_rating"]
        
        # Check all rules
        if attack_rating - defense_rating < 2:
            return False
        if possession_rating - opp_possession < 2:
            return False
        if prob["favorite_odds"] > 1.60:
            return False
        if prob["favorite_probability"] < 65:
            return False
        
        return True
    
    # ========== PROBABILITY CALCULATION METHODS ==========
    
    def calculate_base_probabilities(self, narrative, match_data):
        """Calculate base probabilities for a narrative"""
        # Base BTTS calculation
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        defense_factor = (home_defense + away_defense) / 20
        
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        attack_factor = (home_attack + away_attack) / 20
        
        if narrative == "BLITZKRIEG":
            btts = 30 + (15 * (1 - defense_factor))
            btts = min(45, max(30, btts + (5 * attack_factor)))
            xg = 3.4
        
        elif narrative == "SHOOTOUT":
            btts = 65 + (10 * (1 - defense_factor))
            btts = min(80, max(65, btts + (10 * attack_factor)))
            xg = 3.6
        
        elif narrative == "SIEGE":
            btts = 40 * (1 - defense_factor)
            xg = 2.4
        
        elif narrative == "CHESS_MATCH":
            btts = 30 * (1 - defense_factor)
            xg = 1.9
        
        elif narrative == "CONTROLLED_EDGE":
            btts = 40 + (10 * (1 - defense_factor))
            xg = 2.8
        
        else:
            btts = 50
            xg = 2.5
        
        # Calculate Over 2.5 based on xG
        if xg >= 3.5:
            over25 = 80
        elif xg >= 3.0:
            over25 = 70
        elif xg >= 2.5:
            over25 = 60
        elif xg >= 2.0:
            over25 = 50
        else:
            over25 = 40
        
        # Narrative adjustments
        if narrative == "SHOOTOUT":
            over25 += 10
        elif narrative == "BLITZKRIEG":
            over25 += 5
        elif narrative in ["SIEGE", "CHESS_MATCH", "CONTROLLED_EDGE"]:
            over25 -= 10
        
        return {
            "btts": max(20, min(85, btts)),
            "over25": max(25, min(90, over25)),
            "xg": max(1.8, min(4.0, xg))
        }
    
    def calculate_hybrid_probabilities(self, hybrid_info, match_data):
        """Calculate blended probabilities for hybrid narrative"""
        primary = hybrid_info["primary_narrative"]
        secondary = hybrid_info["secondary_narrative"]
        weight = hybrid_info["weight"]
        
        # Get base probabilities
        primary_probs = self.calculate_base_probabilities(primary, match_data)
        secondary_probs = self.calculate_base_probabilities(secondary, match_data)
        
        # Blend probabilities
        btts = (primary_probs["btts"] * weight) + (secondary_probs["btts"] * (1 - weight))
        over25 = (primary_probs["over25"] * weight) + (secondary_probs["over25"] * (1 - weight))
        xg = (primary_probs["xg"] * weight) + (secondary_probs["xg"] * (1 - weight))
        
        return {
            "btts": round(btts, 1),
            "over25": round(over25, 1),
            "xg": round(xg, 1),
            "primary_weight": weight,
            "secondary_weight": 1 - weight
        }
    
    # ========== MAIN PREDICTION FUNCTION ==========
    
    def predict_match(self, match_data):
        """Main prediction function with hybrid logic"""
        # Calculate all scores
        scores = self.calculate_all_scores(match_data)
        
        # Get probability info for BLITZKRIEG eligibility check
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        # Determine initial tier and confidence
        initial_dominant = max(scores, key=scores.get)
        initial_score = scores[initial_dominant]
        
        if initial_score >= 75:
            tier = "TIER 1 (STRONG)"
            confidence = "High"
            stake = "2-3 units"
            tier_level = 1
        elif initial_score >= 60:
            tier = "TIER 2 (MEDIUM)"
            confidence = "Medium"
            stake = "1-2 units"
            tier_level = 2
        elif initial_score >= 50:
            tier = "TIER 3 (WEAK)"
            confidence = "Low"
            stake = "0.5-1 unit"
            tier_level = 3
        else:
            tier = "TIER 4 (AVOID)"
            confidence = "Very Low"
            stake = "No bet"
            tier_level = 4
        
        # Check BLITZKRIEG eligibility
        if initial_dominant == "BLITZKRIEG":
            if not self.is_blitzkrieg_eligible(match_data, prob, tier_level):
                scores["BLITZKRIEG"] = 0  # Remove from consideration
                # Recalculate after removal
                initial_dominant = max(scores, key=scores.get)
                initial_score = scores[initial_dominant]
                
                # Recalculate tier
                if initial_score >= 75:
                    tier = "TIER 1 (STRONG)"
                    confidence = "High"
                    stake = "2-3 units"
                    tier_level = 1
                elif initial_score >= 60:
                    tier = "TIER 2 (MEDIUM)"
                    confidence = "Medium"
                    stake = "1-2 units"
                    tier_level = 2
                elif initial_score >= 50:
                    tier = "TIER 3 (WEAK)"
                    confidence = "Low"
                    stake = "0.5-1 unit"
                    tier_level = 3
                else:
                    tier = "TIER 4 (AVOID)"
                    confidence = "Very Low"
                    stake = "No bet"
                    tier_level = 4
        
        # Check for hybrid eligibility
        hybrid_info = self.check_hybrid_eligibility(scores, tier_level)
        
        if hybrid_info and tier_level in [1, 2]:
            # HYBRID MODE
            hybrid_type = hybrid_info["hybrid_type"]
            primary = hybrid_info["primary_narrative"]
            secondary = hybrid_info["secondary_narrative"]
            
            # Get hybrid probabilities
            probs = self.calculate_hybrid_probabilities(hybrid_info, match_data)
            
            # Adjust stake for hybrid (slightly reduce due to uncertainty)
            if stake == "2-3 units":
                stake = "1.5-2.5 units"
            elif stake == "1-2 units":
                stake = "0.75-1.5 units"
            
            # Get hybrid info
            hybrid_data = self.hybrid_narratives[hybrid_type]
            
            return {
                "match": f"{match_data['home_team']} vs {match_data['away_team']}",
                "date": match_data["date"],
                "scores": scores,
                "is_hybrid": True,
                "hybrid_type": hybrid_type,
                "primary_narrative": primary,
                "secondary_narrative": secondary,
                "dominant_narrative": hybrid_type,
                "dominant_score": hybrid_info["primary_score"],
                "tier": tier,
                "confidence": confidence,
                "tier_level": tier_level,
                "expected_goals": probs["xg"],
                "btts_probability": probs["btts"],
                "over_25_probability": probs["over25"],
                "stake_recommendation": stake,
                "expected_flow": hybrid_data["flow"],
                "betting_markets": hybrid_data["hybrid_markets"],
                "description": hybrid_data["description"],
                "narrative_color": hybrid_data["color"],
                "secondary_color": hybrid_data["secondary_color"],
                "probabilities": prob,
                "hybrid_info": hybrid_info,
                "margin": hybrid_info["margin"]
            }
        
        else:
            # SINGLE NARRATIVE MODE
            dominant_narrative = max(scores, key=scores.get)
            dominant_score = scores[dominant_narrative]
            
            # Recalculate tier based on final dominant narrative
            if dominant_score >= 75:
                tier = "TIER 1 (STRONG)"
                confidence = "High"
                stake = "2-3 units"
                tier_level = 1
            elif dominant_score >= 60:
                tier = "TIER 2 (MEDIUM)"
                confidence = "Medium"
                stake = "1-2 units"
                tier_level = 2
            elif dominant_score >= 50:
                tier = "TIER 3 (WEAK)"
                confidence = "Low"
                stake = "0.5-1 unit"
                tier_level = 3
            else:
                tier = "TIER 4 (AVOID)"
                confidence = "Very Low"
                stake = "No bet"
                tier_level = 4
            
            # Get base probabilities
            base_probs = self.calculate_base_probabilities(dominant_narrative, match_data)
            
            # Get narrative info
            narrative_info = self.narratives.get(dominant_narrative, self.narratives["CONTROLLED_EDGE"])
            
            return {
                "match": f"{match_data['home_team']} vs {match_data['away_team']}",
                "date": match_data["date"],
                "scores": scores,
                "is_hybrid": False,
                "dominant_narrative": dominant_narrative,
                "dominant_score": dominant_score,
                "tier": tier,
                "confidence": confidence,
                "tier_level": tier_level,
                "expected_goals": base_probs["xg"],
                "btts_probability": base_probs["btts"],
                "over_25_probability": base_probs["over25"],
                "stake_recommendation": stake,
                "expected_flow": narrative_info["flow"],
                "betting_markets": narrative_info["primary_markets"],
                "description": narrative_info["description"],
                "narrative_color": narrative_info["color"],
                "probabilities": prob,
                "blitzkrieg_eligible": self.is_blitzkrieg_eligible(match_data, prob, tier_level) if dominant_narrative == "BLITZKRIEG" else False,
                "margin": 0
            }

# ==============================================
# ENHANCED STREAMLIT APP WITH HYBRID UI/UX
# ==============================================

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.2 - Hybrid Edition",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS with hybrid support
    st.markdown("""
    <style>
    .hybrid-card {
        background: linear-gradient(135deg, var(--primary-color, #f8f9fa) 0%, var(--secondary-color, #ffffff) 100%) !important;
        border: 2px solid;
        border-image: linear-gradient(90deg, var(--primary-color, #FF9800), var(--secondary-color, #FF5722)) 1;
    }
    .hybrid-badge {
        background: linear-gradient(90deg, var(--primary-color, #FF9800), var(--secondary-color, #FF5722));
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .hybrid-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
    }
    .primary-tag {
        background-color: var(--primary-color, #FF9800)20;
        border-color: var(--primary-color, #FF9800);
        color: var(--primary-color, #FF9800);
    }
    .secondary-tag {
        background-color: var(--secondary-color, #FF5722)20;
        border-color: var(--secondary-color, #FF5722);
        color: var(--secondary-color, #FF5722);
    }
    .probability-blend {
        background: linear-gradient(90deg, var(--primary-color, #FF9800) 0%, var(--secondary-color, #FF5722) 100%);
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
        position: relative;
    }
    .blend-marker {
        position: absolute;
        top: -4px;
        width: 3px;
        height: 16px;
        background-color: #333;
    }
    .hybrid-explanation {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        padding: 12px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header
    st.markdown('<h1 style="font-size: 2.8rem; color: #1E88E5; text-align: center; margin-bottom: 0.5rem;">⚽ NARRATIVE PREDICTION ENGINE v2.2</h1>', unsafe_allow_html=True)
    st.markdown("### **Hybrid Edition • 8-Point Margin Rule • Stress-Tested**")
    
    # Initialize engine
    engine = HybridNarrativePredictionEngine()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        data_source = st.radio(
            "Data Source",
            ["Upload CSV", "Use Sample Data", "GitHub URL"],
            index=0
        )
        
        df = None
        
        if data_source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload premier_league_matches.csv", type="csv")
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} matches")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        elif data_source == "Use Sample Data":
            # Sample matches including problematic ones
            sample_matches = [
                # Tottenham vs Liverpool (should be hybrid)
                {
                    "match_id": "EPL_2025-12-20_TOT_LIV",
                    "league": "Premier League",
                    "date": "2025-12-20",
                    "home_team": "Tottenham",
                    "away_team": "Liverpool",
                    "home_position": 5,
                    "away_position": 3,
                    "home_odds": 2.45,
                    "away_odds": 2.65,
                    "home_form": "WWLWD",
                    "away_form": "DWWWD",
                    "home_manager": "Ange Postecoglou",
                    "away_manager": "Arne Slot",
                    "last_h2h_goals": 3,
                    "last_h2h_btts": "Yes",
                    "home_manager_style": "High press & transition",
                    "away_manager_style": "High press & transition",
                    "home_attack_rating": 9,
                    "away_attack_rating": 9,
                    "home_defense_rating": 5,
                    "away_defense_rating": 6,
                    "home_press_rating": 9,
                    "away_press_rating": 9,
                    "home_possession_rating": 6,
                    "away_possession_rating": 7,
                    "home_pragmatic_rating": 4,
                    "away_pragmatic_rating": 5
                },
                # Manchester City vs West Ham (clear SIEGE)
                {
                    "match_id": "EPL_2025-12-20_MCI_WHU",
                    "league": "Premier League",
                    "date": "2025-12-20",
                    "home_team": "Manchester City",
                    "away_team": "West Ham",
                    "home_position": 1,
                    "away_position": 15,
                    "home_odds": 1.25,
                    "away_odds": 13.00,
                    "home_form": "WWWWW",
                    "away_form": "LLLLL",
                    "home_manager": "Pep Guardiola",
                    "away_manager": "David Moyes",
                    "last_h2h_goals": 4,
                    "last_h2h_btts": "No",
                    "home_manager_style": "Possession-based & control",
                    "away_manager_style": "Pragmatic/Defensive",
                    "home_attack_rating": 10,
                    "away_attack_rating": 5,
                    "home_defense_rating": 8,
                    "away_defense_rating": 9,
                    "home_press_rating": 9,
                    "away_press_rating": 6,
                    "home_possession_rating": 10,
                    "away_possession_rating": 5,
                    "home_pragmatic_rating": 4,
                    "away_pragmatic_rating": 9
                },
                # Newcastle vs Chelsea (should be hybrid)
                {
                    "match_id": "EPL_2025-12-20_NEW_CHE",
                    "league": "Premier League",
                    "date": "2025-12-20",
                    "home_team": "Newcastle United",
                    "away_team": "Chelsea",
                    "home_position": 12,
                    "away_position": 4,
                    "home_odds": 2.68,
                    "away_odds": 2.57,
                    "home_form": "WWWWL",
                    "away_form": "DWWWD",
                    "home_manager": "Eddie Howe",
                    "away_manager": "Enzo Maresca",
                    "last_h2h_goals": 2,
                    "last_h2h_btts": "No",
                    "home_manager_style": "High press & transition",
                    "away_manager_style": "Possession-based & control",
                    "home_attack_rating": 9,
                    "away_attack_rating": 8,
                    "home_defense_rating": 6,
                    "away_defense_rating": 7,
                    "home_press_rating": 9,
                    "away_press_rating": 7,
                    "home_possession_rating": 7,
                    "away_possession_rating": 9,
                    "home_pragmatic_rating": 5,
                    "away_pragmatic_rating": 6
                }
            ]
            df = pd.DataFrame(sample_matches)
            st.success(f"✅ Loaded {len(df)} sample matches")
        
        # Analysis settings
        st.markdown("### 🔧 Analysis Settings")
        
        show_hybrid_details = st.checkbox("Show Hybrid Analysis", value=True)
        debug_mode = st.checkbox("Debug Mode", value=False)
        
        # Navigation
        st.markdown("### 📋 Navigation")
        page = st.radio("Go to", ["Predictions", "Hybrid Guide", "Export"])
    
    # Main content
    if df is not None:
        # Data preview
        with st.expander("📊 Data Preview", expanded=False):
            st.dataframe(df.head())
        
        # Match selection
        st.markdown("### 🎯 Select Matches")
        
        match_options = df.apply(
            lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", 
            axis=1
        ).tolist()
        
        selected_matches = st.multiselect(
            "Choose matches to analyze",
            match_options,
            default=match_options[:min(3, len(match_options))]
        )
        
        # Generate predictions
        if st.button("🚀 Generate Hybrid Predictions", type="primary"):
            with st.spinner("Running hybrid narrative analysis..."):
                predictions = []
                
                for match_str in selected_matches:
                    match_idx = match_options.index(match_str)
                    match_row = df.iloc[match_idx]
                    
                    # Prepare match data
                    match_data = {
                        "home_team": match_row["home_team"],
                        "away_team": match_row["away_team"],
                        "date": match_row["date"],
                        "home_position": int(match_row["home_position"]),
                        "away_position": int(match_row["away_position"]),
                        "home_odds": float(match_row["home_odds"]),
                        "away_odds": float(match_row["away_odds"]),
                        "home_form": str(match_row["home_form"]),
                        "away_form": str(match_row["away_form"]),
                        "home_manager": match_row["home_manager"],
                        "away_manager": match_row["away_manager"],
                        "last_h2h_goals": int(match_row["last_h2h_goals"]),
                        "last_h2h_btts": str(match_row["last_h2h_btts"]),
                        "home_attack_rating": int(match_row["home_attack_rating"]),
                        "away_attack_rating": int(match_row["away_attack_rating"]),
                        "home_defense_rating": int(match_row["home_defense_rating"]),
                        "away_defense_rating": int(match_row["away_defense_rating"]),
                        "home_press_rating": int(match_row["home_press_rating"]),
                        "away_press_rating": int(match_row["away_press_rating"]),
                        "home_possession_rating": int(match_row["home_possession_rating"]),
                        "away_possession_rating": int(match_row["away_possession_rating"]),
                        "home_pragmatic_rating": int(match_row["home_pragmatic_rating"]),
                        "away_pragmatic_rating": int(match_row["away_pragmatic_rating"])
                    }
                    
                    # Get prediction
                    prediction = engine.predict_match(match_data)
                    predictions.append(prediction)
                
                # Store results
                st.session_state.predictions = predictions
                st.success(f"✅ Generated {len(predictions)} hybrid predictions")
    
    # Display predictions
    if "predictions" in st.session_state:
        predictions = st.session_state.predictions
        
        if page == "Predictions":
            # Summary dashboard
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                hybrid_count = sum(1 for p in predictions if p["is_hybrid"])
                st.metric("🔄 Hybrid Predictions", hybrid_count)
            
            with col2:
                single_count = len(predictions) - hybrid_count
                st.metric("🎯 Single Narratives", single_count)
            
            with col3:
                avg_margin = sum(p.get("margin", 0) for p in predictions) / len(predictions)
                st.metric("📊 Avg Narrative Margin", f"{avg_margin:.1f}")
            
            with col4:
                tier1_count = sum(1 for p in predictions if p["tier"] == "TIER 1 (STRONG)")
                st.metric("🏆 Tier 1 Predictions", tier1_count)
            
            # Individual predictions
            for pred in predictions:
                # Determine card styling
                if pred["is_hybrid"]:
                    card_style = f"""
                    <style>
                    .hybrid-card-{pred['match'].replace(' ', '-').replace('vs', '-')} {{
                        --primary-color: {pred['narrative_color']};
                        --secondary-color: {pred.get('secondary_color', '#6c757d')};
                    }}
                    </style>
                    """
                    st.markdown(card_style, unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="prediction-card hybrid-card hybrid-card-{pred["match"].replace(" ", "-").replace("vs", "-")}">', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="prediction-card" style="border-left: 5px solid {pred["narrative_color"]};">', unsafe_allow_html=True)
                
                # Header
                col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
                
                with col_h1:
                    st.markdown(f"### {pred['match']}")
                    st.markdown(f"**Date:** {pred['date']} | **Tier:** {pred['tier']}")
                    
                    if pred["is_hybrid"]:
                        st.markdown(f'<div class="hybrid-badge" style="--primary-color: {pred["narrative_color"]}; --secondary-color: {pred.get("secondary_color", "#6c757d")};">{pred["hybrid_type"]}</div>', unsafe_allow_html=True)
                        
                        # Show parent narratives
                        st.markdown(f'<span class="hybrid-tag primary-tag">{pred["primary_narrative"]}</span> + <span class="hybrid-tag secondary-tag">{pred["secondary_narrative"]}</span>', unsafe_allow_html=True)
                    else:
                        color = pred["narrative_color"]
                        st.markdown(f'<div style="background-color: {color}20; padding: 8px 16px; border-radius: 20px; border: 2px solid {color}; display: inline-block; margin-bottom: 10px;">'
                                  f'<strong style="color: {color};">{pred["dominant_narrative"]}</strong>'
                                  f'</div>', unsafe_allow_html=True)
                
                with col_h2:
                    # Score display
                    if pred["is_hybrid"]:
                        st.markdown(f"**Primary Score:** {pred['hybrid_info']['primary_score']:.1f}")
                        st.markdown(f"**Secondary Score:** {pred['hybrid_info']['secondary_score']:.1f}")
                        st.markdown(f"**Margin:** {pred['margin']:.1f}")
                    else:
                        st.markdown(f"**Score:** {pred['dominant_score']:.1f}/100")
                
                with col_h3:
                    # Stake and confidence
                    stake_class = "stake-high" if "2-3" in pred["stake_recommendation"] or "1.5-2.5" in pred["stake_recommendation"] else \
                                 "stake-medium" if "1-2" in pred["stake_recommendation"] or "0.75-1.5" in pred["stake_recommendation"] else \
                                 "stake-low"
                    
                    st.markdown(f'<div class="stake-badge {stake_class}">{pred["stake_recommendation"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"**Confidence:** {pred['confidence']}")
                
                # Main content
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    # Narrative scores visualization
                    st.markdown("#### 📊 Narrative Scores")
                    
                    if pred["is_hybrid"] and show_hybrid_details:
                        # Show probability blend visualization
                        st.markdown("**Probability Blend:**")
                        weight = pred["hybrid_info"]["weight"]
                        st.markdown(f'<div class="probability-blend" style="--primary-color: {pred["narrative_color"]}; --secondary-color: {pred.get("secondary_color", "#6c757d")};">'
                                  f'<div class="blend-marker" style="left: {weight*100}%;"></div>'
                                  f'</div>', unsafe_allow_html=True)
                        
                        col_w1, col_w2 = st.columns(2)
                        with col_w1:
                            st.markdown(f"**Primary Weight:** {weight:.2f}")
                        with col_w2:
                            st.markdown(f"**Secondary Weight:** {1-weight:.2f}")
                    
                    # Show all scores
                    for narrative, score in pred["scores"].items():
                        if narrative in engine.narratives:
                            color = engine.narratives[narrative]["color"]
                            is_primary = pred.get("primary_narrative") == narrative
                            is_secondary = pred.get("secondary_narrative") == narrative
                            
                            label = narrative
                            if is_primary:
                                label = f"🏆 {narrative}"
                            elif is_secondary:
                                label = f"🥈 {narrative}"
                            
                            st.markdown(f"**{label}:** {score:.1f}")
                            st.markdown(f'<div class="score-bar"><div style="width: {score}%; height: 100%; background-color: {color}; border-radius: 10px;"></div></div>', unsafe_allow_html=True)
                    
                    # Key stats
                    st.markdown("#### 📈 Key Statistics")
                    
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.metric("Expected Goals", f"{pred['expected_goals']:.1f}")
                    with col_s2:
                        st.metric("BTTS %", f"{pred['btts_probability']}%")
                    with col_s3:
                        st.metric("Over 2.5 %", f"{pred['over_25_probability']}%")
                
                with col_m2:
                    # Insights and flow
                    st.markdown("#### 💡 Insights")
                    st.info(pred["description"])
                    
                    # Expected flow
                    with st.expander("📈 Expected Match Flow", expanded=False):
                        st.write(pred["expected_flow"])
                    
                    # Betting markets
                    st.markdown("#### 💰 Recommended Markets")
                    for market in pred["betting_markets"]:
                        st.markdown(f"• {market}")
                    
                    # Hybrid explanation
                    if pred["is_hybrid"] and show_hybrid_details:
                        with st.expander("🔄 Hybrid Analysis", expanded=False):
                            st.markdown(f"""
                            **Why Hybrid?**
                            - Primary narrative: **{pred['primary_narrative']}** ({pred['hybrid_info']['primary_score']:.1f})
                            - Secondary narrative: **{pred['secondary_narrative']}** ({pred['hybrid_info']['secondary_score']:.1f})
                            - Margin: **{pred['margin']:.1f}** points (< 8, so hybrid triggered)
                            
                            **Probability Blend:**
                            - BTTS: {pred['btts_probability']}% (between {pred['primary_narrative']} and {pred['secondary_narrative']})
                            - Over 2.5: {pred['over_25_probability']}% (weighted average)
                            - xG: {pred['expected_goals']:.1f} (blended expectation)
                            """)
                
                # Debug info
                if debug_mode:
                    with st.expander("🔍 Debug Info", expanded=False):
                        st.json(pred.get("probabilities", {}))
                        if pred["is_hybrid"]:
                            st.json(pred.get("hybrid_info", {}))
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Overall analysis
            if len(predictions) > 1:
                st.markdown("### 📊 Overall Analysis")
                
                # Create narrative distribution chart
                narrative_counts = {}
                hybrid_counts = {}
                
                for pred in predictions:
                    if pred["is_hybrid"]:
                        hybrid_counts[pred["hybrid_type"]] = hybrid_counts.get(pred["hybrid_type"], 0) + 1
                    else:
                        narrative_counts[pred["dominant_narrative"]] = narrative_counts.get(pred["dominant_narrative"], 0) + 1
                
                # Combine for display
                all_counts = {**narrative_counts, **hybrid_counts}
                
                if all_counts:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=list(all_counts.keys()),
                            values=list(all_counts.values()),
                            hole=0.3,
                            marker_colors=[pred["narrative_color"] if not pred["is_hybrid"] else engine.hybrid_narratives.get(pred["hybrid_type"], {}).get("color", "#6c757d") 
                                          for pred in predictions for _ in range(all_counts.get(pred["dominant_narrative"] if not pred["is_hybrid"] else pred["hybrid_type"], 0))]
                        )
                    ])
                    
                    fig.update_layout(
                        title="Narrative Distribution",
                        height=400,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        elif page == "Hybrid Guide":
            # Hybrid narrative guide
            st.markdown("## 🔄 Hybrid Narrative Guide")
            
            st.markdown("""
            ### What are Hybrid Narratives?
            
            Hybrid narratives are triggered when:
            1. **Margin < 8 points** between top two narratives
            2. **Tier ≥ 2** (Medium or High confidence)
            3. **Valid combination** of parent narratives
            
            This prevents overconfidence in close-call matches and creates more nuanced predictions.
            """)
            
            # Show hybrid types
            for hybrid_name, hybrid_data in engine.hybrid_narratives.items():
                col_g1, col_g2 = st.columns([1, 2])
                
                with col_g1:
                    st.markdown(
                        f'<div style="background: linear-gradient(135deg, {hybrid_data["color"]}20, {hybrid_data.get("secondary_color", "#6c757d")}20); padding: 20px; border-radius: 10px; border-left: 5px solid {hybrid_data["color"]}; border-right: 5px solid {hybrid_data.get("secondary_color", "#6c757d")};">'
                        f'<h3 style="color: {hybrid_data["color"]}; margin-top: 0;">{hybrid_name}</h3>'
                        f'<p><strong>{hybrid_data["description"]}</strong></p>'
                        f'<p>Parents: {hybrid_data["parent_narratives"][0]} + {hybrid_data["parent_narratives"][1]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                with col_g2:
                    with st.expander(f"Detailed Analysis", expanded=False):
                        st.markdown("**Expected Match Flow:**")
                        st.write(hybrid_data["flow"])
                        
                        st.markdown("**Typical Characteristics:**")
                        
                        if hybrid_name == "EDGE-CHAOS":
                            st.write("""
                            - Close match with explosive potential
                            - Both teams capable of attacking
                            - Could remain tight or open up
                            - Higher variance than pure CONTROLLED_EDGE
                            - Expected BTTS: 45-65%
                            - Expected xG: 2.8-3.4
                            """)
                        
                        elif hybrid_name == "EDGE-DOMINATION":
                            st.write("""
                            - Controlled favorite vs organized defense
                            - Patient buildup rather than early pressure
                            - Breakthrough likely mid-game
                            - Low-scoring but controlled
                            - Expected BTTS: 30-50%
                            - Expected xG: 2.2-2.8
                            """)
                        
                        elif hybrid_name == "HIGH-TEMPO":
                            st.write("""
                            - Fast start from both teams
                            - Early goals likely
                            - Game could become one-sided or remain chaotic
                            - High scoring potential
                            - Expected BTTS: 60-75%
                            - Expected xG: 3.2-3.8
                            """)
                        
                        st.markdown("**Recommended Markets:**")
                        for market in hybrid_data["hybrid_markets"]:
                            st.write(f"• {market}")
                
                st.markdown("---")
        
        elif page == "Export":
            # Export functionality
            st.markdown("## 📊 Export Predictions")
            
            export_data = []
            for pred in predictions:
                export_row = {
                    "Match": pred["match"],
                    "Date": pred["date"],
                    "Narrative_Type": "Hybrid" if pred["is_hybrid"] else "Single",
                    "Prediction": pred["hybrid_type"] if pred["is_hybrid"] else pred["dominant_narrative"],
                    "Primary_Narrative": pred.get("primary_narrative", ""),
                    "Secondary_Narrative": pred.get("secondary_narrative", ""),
                    "Narrative_Score": pred["dominant_score"],
                    "Tier": pred["tier"],
                    "Confidence": pred["confidence"],
                    "Expected_Goals": pred["expected_goals"],
                    "BTTS_Probability": pred["btts_probability"],
                    "Over_25_Probability": pred["over_25_probability"],
                    "Stake_Recommendation": pred["stake_recommendation"],
                    "Margin": pred.get("margin", 0)
                }
                export_data.append(export_row)
            
            export_df = pd.DataFrame(export_data)
            
            # Preview
            st.dataframe(export_df)
            
            # Download
            csv = export_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="hybrid_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv">📥 Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    else:
        # Initial state
        st.info("👈 **Upload a CSV file or use sample data to get started**")
        
        # Show what's new
        with st.expander("🎯 What's New in v2.2", expanded=True):
            st.markdown("""
            ### 🔄 Hybrid Narrative System
            
            **8-Point Margin Rule:**
            - If top narrative leads by < 8 points → Hybrid triggered
            - Prevents overconfidence in close-call matches
            - Creates more nuanced probability estimates
            
            **Three Hybrid Types:**
            1. **EDGE-CHAOS** - Tight but explosive (CONTROLLED_EDGE + SHOOTOUT)
            2. **EDGE-DOMINATION** - Patient pressure (CONTROLLED_EDGE + SIEGE)  
            3. **HIGH-TEMPO** - Fast start, high scoring (SHOOTOUT + BLITZKRIEG)
            
            **Key Benefits:**
            - More realistic EPL variance
            - Better probability calibration
            - Maintains stress-test discipline
            - Truthful uncertainty communication
            """)

if __name__ == "__main__":
    main()
