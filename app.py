# app.py - NARRATIVE PREDICTION ENGINE v2.2 - FINAL STRESS-TESTED VERSION
# ✅ All stress-test fixes implemented with dominance threshold
# 🎨 Frontend preserved exactly as before

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

# ==============================================
# FINAL NARRATIVE PREDICTION ENGINE
# All stress-test fixes with dominance threshold
# ==============================================

class FinalNarrativePredictionEngine:
    """Final prediction engine with all stress-test fixes"""
    
    def __init__(self):
        # Manager style database (unchanged)
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
        
        # Narrative definitions with colors (unchanged frontend display)
        self.narratives = {
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "flow": "• Early pressure from favorite (0-15 mins)\n• Breakthrough before 30 mins\n• Opponent confidence collapses after first goal\n• Additional goals in 35-65 minute window\n• Game effectively over by 70 mins",
                "betting_markets": ["Favorite to win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals for favorite", "Favorite -1.5 Asian handicap"],
                "color": "#4CAF50"
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "betting_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"],
                "color": "#FF5722"
            },
            "SIEGE": {
                "description": "Attack vs Defense - One dominates, other parks bus",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "betting_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"],
                "color": "#2196F3"
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both teams (0-30 mins)\n• Midfield battle dominates, few clear chances\n• Set pieces become primary scoring threats\n• First goal (if any) often decisive\n• Late tactical changes unlikely to alter outcome significantly",
                "betting_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0 correct score", "Few goals first half", "Under 1.5 goals"],
                "color": "#9C27B0"
            },
            "CONTROLLED_EDGE": {
                "description": "Grinding Advantage - Favorite edges cautious game",
                "flow": "• Cautious start from both sides\n• Favorite gradually establishes control\n• Breakthrough likely 30-60 mins\n• Limited scoring chances overall\n• Narrow victory or draw",
                "betting_markets": ["Under 2.5 goals", "BTTS: No", "Favorite to win or draw", "First goal 30-60 mins", "Few corners total"],
                "color": "#FF9800"
            }
        }
    
    # ========== CORE LOGIC WITH ALL FIXES ==========
    
    def calculate_favorite_probability(self, home_odds, away_odds):
        """Convert odds to implied probabilities (unchanged)"""
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
    
    def is_blitzkrieg_eligible(self, match_data, prob, tier_level):
        """STRESS-TEST FIX 1: Strict BLITZKRIEG eligibility"""
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
        
        # Rule 1: Attack differential ≥ +2
        attack_diff = attack_rating - defense_rating
        if attack_diff < 2:
            return False
        
        # Rule 2: Possession differential ≥ +2
        possession_diff = possession_rating - opp_possession
        if possession_diff < 2:
            return False
        
        # Rule 3: Odds ≤ 1.60
        if prob["favorite_odds"] > 1.60:
            return False
        
        # Rule 4: Favorite probability ≥ 65%
        if prob["favorite_probability"] < 65:
            return False
        
        # Rule 5: Tier ≥ 2
        if tier_level < 2:
            return False
        
        return True
    
    def calculate_blitzkrieg_score(self, match_data):
        """BLITZKRIEG calculation"""
        score = 0
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if prob["favorite_strength"] == "ELITE":
            score += 30
        elif prob["favorite_strength"] == "STRONG":
            score += 20
        elif prob["favorite_strength"] == "MODERATE":
            score += 10
        
        home_attack = match_data["home_attack_rating"]
        away_defense = match_data["away_defense_rating"]
        away_attack = match_data["away_attack_rating"]
        home_defense = match_data["home_defense_rating"]
        
        home_advantage = home_attack - (10 - away_defense)
        away_advantage = away_attack - (10 - home_defense)
        
        if home_advantage >= 3 or away_advantage >= 3:
            score += 25
        elif home_advantage >= 2 or away_advantage >= 2:
            score += 15
        elif home_advantage >= 1 or away_advantage >= 1:
            score += 5
        
        home_form = self.analyze_form(match_data["home_form"])["rating"]
        away_form = self.analyze_form(match_data["away_form"])["rating"]
        form_diff = abs(home_form - away_form)
        score += min(20, form_diff * 2)
        
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        press_diff = abs(home_press - away_press)
        if press_diff >= 3:
            score += 15
        elif press_diff >= 2:
            score += 10
        
        position_gap = abs(match_data["home_position"] - match_data["away_position"])
        if position_gap >= 10:
            score += 10
        elif position_gap >= 5:
            score += 5
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """ENHANCED SHOOTOUT scoring"""
        score = 0
        
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        
        if home_attack >= 8 and away_attack >= 8:
            score += 30
        elif home_attack >= 7 and away_attack >= 7:
            score += 22
        elif home_attack >= 6 and away_attack >= 6:
            score += 12
        
        if home_attack >= 9 or away_attack >= 9:
            score += 5
        
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        avg_defense = (home_defense + away_defense) / 2
        
        if avg_defense <= 5.5:
            score += 28
        elif avg_defense <= 6.0:
            score += 22
        elif avg_defense <= 6.5:
            score += 16
        elif avg_defense <= 7.0:
            score += 10
        
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        
        if home_press >= 8 and away_press >= 8:
            score += 25
        elif home_press >= 7 and away_press >= 7:
            score += 18
        elif (home_press >= 8 and away_press >= 6) or (away_press >= 8 and home_press >= 6):
            score += 12
        
        if match_data["last_h2h_goals"] >= 4:
            score += 18
        elif match_data["last_h2h_goals"] >= 3:
            score += 12
        elif match_data["last_h2h_goals"] >= 2:
            score += 6
        
        home_form = match_data["home_form"]
        away_form = match_data["away_form"]
        
        home_last_3 = home_form[-3:] if len(home_form) >= 3 else home_form
        away_last_3 = away_form[-3:] if len(away_form) >= 3 else away_form
        
        home_scoring = sum(1 for r in home_last_3 if r.upper() != 'L')
        away_scoring = sum(1 for r in away_last_3 if r.upper() != 'L')
        
        if home_scoring >= 2 and away_scoring >= 2:
            score += 12
        elif home_scoring >= 2 or away_scoring >= 2:
            score += 6
        
        if match_data["last_h2h_btts"] == "Yes":
            score += 10
        
        odds_gap = abs(match_data["home_odds"] - match_data["away_odds"])
        if odds_gap <= 0.5:
            score += 8
        
        attacking_managers = ["Pep Guardiola", "Mikel Arteta", "Arne Slot", 
                             "Eddie Howe", "Ange Postecoglou"]
        
        home_manager = match_data.get("home_manager", "")
        away_manager = match_data.get("away_manager", "")
        
        if home_manager in attacking_managers:
            score += 5
        if away_manager in attacking_managers:
            score += 5
        
        return min(100, score)
    
    def calculate_siege_score(self, match_data):
        """SIEGE calculation"""
        score = 0
        
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
        elif away_attack >= 7 and home_defense >= 7:
            score += 15
        
        home_possession = match_data["home_possession_rating"]
        away_possession = match_data["away_possession_rating"]
        
        possession_diff = abs(home_possession - away_possession)
        if possession_diff >= 3:
            score += 20
        elif possession_diff >= 2:
            score += 12
        
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if (home_pragmatic >= 7 and away_pragmatic <= 5) or (away_pragmatic >= 7 and home_pragmatic <= 5):
            score += 15
        
        if match_data["last_h2h_goals"] <= 1:
            score += 15
        elif match_data["last_h2h_goals"] <= 2:
            score += 10
        elif match_data["last_h2h_goals"] <= 3:
            score += 5
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if prob["favorite_is_home"] and prob["favorite_probability"] >= 60:
            score += 10
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """CHESS MATCH calculation"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        favorite_prob = prob["favorite_probability"]
        
        if favorite_prob < 52:
            score += 25
        elif favorite_prob < 55:
            score += 18
        elif favorite_prob < 58:
            score += 10
        
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic >= 7 and away_pragmatic >= 7:
            score += 25
        elif home_pragmatic >= 6 and away_pragmatic >= 6:
            score += 15
        
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        if home_defense >= 8 and away_defense >= 8:
            score += 20
        elif home_defense >= 7 and away_defense >= 7:
            score += 12
        
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        
        if home_attack <= 6 and away_attack <= 6:
            score += 15
        elif home_attack <= 7 and away_attack <= 7:
            score += 8
        
        if match_data["last_h2h_goals"] <= 2:
            score += 15
        elif match_data["last_h2h_goals"] <= 3:
            score += 8
        
        return min(100, score)
    
    def calculate_controlled_edge_score(self, match_data):
        """REVISED CONTROLLED_EDGE scoring - reduced bias"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if 55 <= prob["favorite_probability"] < 65:
            score += 12
        elif 50 <= prob["favorite_probability"] < 55:
            score += 6
        
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        attack_diff = abs(home_attack - away_attack)
        defense_diff = abs(home_defense - away_defense)
        
        if attack_diff <= 1 and defense_diff <= 1:
            score += 8
        elif attack_diff <= 2 and defense_diff <= 2:
            score += 12
        else:
            score += 5
        
        if 6 <= home_defense <= 8 and 6 <= away_defense <= 8:
            if home_attack >= 7 and away_attack >= 7:
                score += 8
            else:
                score += 12
        elif 5 <= home_defense <= 9 and 5 <= away_defense <= 9:
            score += 8
        
        home_pragmatic = match_data["home_pragmatic_rating"]
        away_pragmatic = match_data["away_pragmatic_rating"]
        
        if home_pragmatic >= 6 and away_pragmatic >= 6:
            score += 10
        elif home_pragmatic >= 5 and away_pragmatic >= 5:
            score += 6
        
        position_gap = abs(match_data["home_position"] - match_data["away_position"])
        if position_gap <= 3:
            score += 5
        elif position_gap <= 6:
            score += 2
        
        if match_data["last_h2h_goals"] <= 2:
            score += 8
        elif match_data["last_h2h_goals"] <= 3:
            score += 4
        else:
            score -= 5
        
        home_press = match_data["home_press_rating"]
        away_press = match_data["away_press_rating"]
        
        if home_attack >= 7 and away_attack >= 7:
            if home_press >= 7 or away_press >= 7:
                score -= 10
        
        if (home_attack - away_defense >= 3) or (away_attack - home_defense >= 3):
            score -= 8
        
        return max(0, min(100, score))
    
    def analyze_form(self, form_string):
        """Form analysis (unchanged)"""
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
    
    def calculate_dynamic_btts(self, match_data, narrative):
        """Dynamic BTTS probability"""
        home_defense = match_data["home_defense_rating"]
        away_defense = match_data["away_defense_rating"]
        
        defense_factor = (home_defense + away_defense) / 20
        
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        attack_factor = (home_attack + away_attack) / 20
        
        if narrative == "BLITZKRIEG":
            base_prob = 30 + (15 * (1 - defense_factor))
            adjusted = base_prob + (5 * attack_factor)
            return min(45, max(30, adjusted))
        
        elif narrative == "SHOOTOUT":
            base_prob = 65 + (10 * (1 - defense_factor))
            adjusted = base_prob + (10 * attack_factor)
            return min(80, max(65, adjusted))
        
        elif narrative == "SIEGE":
            return 40 * (1 - defense_factor)
        
        elif narrative == "CHESS_MATCH":
            return 30 * (1 - defense_factor)
        
        elif narrative == "CONTROLLED_EDGE":
            return 40 + (10 * (1 - defense_factor))
        
        return 50
    
    def calculate_dynamic_xg(self, match_data, tier_level, narrative):
        """Dynamic expected goals"""
        home_attack = match_data["home_attack_rating"]
        away_attack = match_data["away_attack_rating"]
        avg_attack = (home_attack + away_attack) / 20
        
        if tier_level == 1:
            xg_range = (3.2, 3.6)
        elif tier_level == 2:
            xg_range = (3.0, 3.4)
        else:
            xg_range = (2.6, 3.1)
        
        narrative_adjustments = {
            "BLITZKRIEG": 0.2,
            "SHOOTOUT": 0.3,
            "SIEGE": -0.3,
            "CHESS_MATCH": -0.5,
            "CONTROLLED_EDGE": -0.2
        }
        
        base_xg = xg_range[0] + (xg_range[1] - xg_range[0]) * avg_attack
        adjustment = narrative_adjustments.get(narrative, 0)
        adjusted_xg = base_xg + adjustment
        
        return max(1.8, min(4.0, round(adjusted_xg, 1)))
    
    def calculate_over_25_probability(self, expected_goals, narrative):
        """Dynamic Over 2.5 probability"""
        if expected_goals >= 3.5:
            base_prob = 80
        elif expected_goals >= 3.0:
            base_prob = 70
        elif expected_goals >= 2.5:
            base_prob = 60
        elif expected_goals >= 2.0:
            base_prob = 50
        else:
            base_prob = 40
        
        narrative_adjustments = {
            "SHOOTOUT": 10,
            "BLITZKRIEG": 5,
            "SIEGE": -15,
            "CHESS_MATCH": -25,
            "CONTROLLED_EDGE": -10
        }
        
        adjustment = narrative_adjustments.get(narrative, 0)
        final_prob = base_prob + adjustment
        
        return max(20, min(90, final_prob))
    
    # ========== FINAL PREDICTION WITH DOMINANCE THRESHOLD ==========
    
    def predict_match(self, match_data):
        """FINAL prediction with dominance threshold fix"""
        
        # Calculate all narrative scores
        scores = {
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "SIEGE": self.calculate_siege_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data),
            "CONTROLLED_EDGE": self.calculate_controlled_edge_score(match_data)
        }
        
        # Get top two narratives
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        dominant_narrative, dominant_score = sorted_scores[0]
        second_narrative, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
        
        # Calculate dominance gap (YOUR FINAL FIX)
        dominance_gap = dominant_score - second_score if second_narrative else 100
        
        # Determine base tier and confidence
        if dominant_score >= 75:
            base_tier = "TIER 1 (STRONG)"
            base_confidence = "High"
            base_stake = "2-3 units"
            tier_level = 1
        elif dominant_score >= 60:
            base_tier = "TIER 2 (MEDIUM)"
            base_confidence = "Medium"
            base_stake = "1-2 units"
            tier_level = 2
        elif dominant_score >= 50:
            base_tier = "TIER 3 (WEAK)"
            base_confidence = "Low"
            base_stake = "0.5-1 unit"
            tier_level = 3
        else:
            base_tier = "TIER 4 (AVOID)"
            base_confidence = "Very Low"
            base_stake = "No bet"
            tier_level = 4
        
        # STRESS-TEST FIX: Check BLITZKRIEG eligibility
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if dominant_narrative == "BLITZKRIEG":
            if not self.is_blitzkrieg_eligible(match_data, prob, tier_level):
                scores["BLITZKRIEG"] = 0
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                dominant_narrative, dominant_score = sorted_scores[0]
                second_narrative, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
                dominance_gap = dominant_score - second_score if second_narrative else 100
                
                if dominant_score >= 75:
                    base_tier = "TIER 1 (STRONG)"
                    base_confidence = "High"
                    base_stake = "2-3 units"
                    tier_level = 1
                elif dominant_score >= 60:
                    base_tier = "TIER 2 (MEDIUM)"
                    base_confidence = "Medium"
                    base_stake = "1-2 units"
                    tier_level = 2
                elif dominant_score >= 50:
                    base_tier = "TIER 3 (WEAK)"
                    base_confidence = "Low"
                    base_stake = "0.5-1 unit"
                    tier_level = 3
                else:
                    base_tier = "TIER 4 (AVOID)"
                    base_confidence = "Very Low"
                    base_stake = "No bet"
                    tier_level = 4
        
        # APPLY DOMINANCE THRESHOLD FIX
        final_confidence = base_confidence
        final_stake = base_stake
        close_call = False
        dual_narrative_flag = False
        
        if dominance_gap < 8:  # Less than 8-point gap
            close_call = True
            
            # Downgrade confidence by one level
            if base_confidence == "High":
                final_confidence = "Medium"
                if base_tier == "TIER 1 (STRONG)":
                    final_stake = "1.5-2.5 units"
            elif base_confidence == "Medium":
                final_confidence = "Low"
                if base_tier == "TIER 2 (MEDIUM)":
                    final_stake = "0.75-1.5 units"
            elif base_confidence == "Low":
                final_confidence = "Very Low"
                if base_tier == "TIER 3 (WEAK)":
                    final_stake = "0.25-0.75 units"
        
        # For VERY close calls (gap < 5), flag for frontend
        if dominance_gap < 5 and dominant_score >= 50:
            dual_narrative_flag = True
            if "units" in final_stake:
                if "2-3" in final_stake:
                    final_stake = "1-2 units"
                elif "1-2" in final_stake:
                    final_stake = "0.5-1 units"
                elif "0.5-1" in final_stake:
                    final_stake = "0.25-0.5 units"
        
        # Calculate dynamic probabilities
        expected_goals = self.calculate_dynamic_xg(match_data, tier_level, dominant_narrative)
        btts_prob = self.calculate_dynamic_btts(match_data, dominant_narrative)
        over_25_prob = self.calculate_over_25_probability(expected_goals, dominant_narrative)
        
        # Get narrative info (frontend display unchanged)
        narrative_info = self.narratives.get(dominant_narrative, self.narratives["CONTROLLED_EDGE"])
        
        # Prepare description (subtly indicate close calls in description)
        description = narrative_info["description"]
        if close_call and not dual_narrative_flag:
            description = f"{description} (Close call with {second_narrative})"
        elif dual_narrative_flag:
            second_info = self.narratives.get(second_narrative, {})
            second_desc = second_info.get("description", "").split(" - ")[0] if second_info else second_narrative
            description = f"Between {dominant_narrative} & {second_narrative}: {narrative_info['description'].split(' - ')[0]} or {second_desc}"
        
        # Return result (frontend structure UNCHANGED)
        return {
            "match": f"{match_data['home_team']} vs {match_data['away_team']}",
            "date": match_data["date"],
            "scores": scores,
            "dominant_narrative": dominant_narrative,
            "dominant_score": dominant_score,
            "tier": base_tier,  # Keep original tier for display
            "confidence": final_confidence,  # Adjusted confidence
            "expected_goals": expected_goals,
            "btts_probability": btts_prob,
            "over_25_probability": over_25_prob,
            "stake_recommendation": final_stake,  # Adjusted stake
            "expected_flow": narrative_info["flow"],
            "betting_markets": narrative_info["betting_markets"],
            "description": description,  # Enhanced description for close calls
            "narrative_color": narrative_info["color"],
            "probabilities": prob,
            # Internal flags (not shown in frontend)
            "_internal_flags": {
                "blitzkrieg_eligible": self.is_blitzkrieg_eligible(match_data, prob, tier_level) if dominant_narrative == "BLITZKRIEG" else False,
                "dominance_gap": dominance_gap,
                "close_call": close_call,
                "dual_narrative": dual_narrative_flag,
                "second_narrative": second_narrative,
                "second_score": second_score
            }
        }

# ==============================================
# STREAMLIT APP - FRONTEND UNCHANGED
# ==============================================

def main():
    # EXACT SAME FRONTEND CODE AS BEFORE
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.0",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS (unchanged)
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 2rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .tier-1 {
        border-left: 5px solid #4CAF50;
        background-color: #f1f8e9;
    }
    .tier-2 {
        border-left: 5px solid #FF9800;
        background-color: #fff3e0;
    }
    .tier-3 {
        border-left: 5px solid #F44336;
        background-color: #ffebee;
    }
    .score-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 5px 0;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        border-radius: 10px;
        background-color: #1E88E5;
        transition: width 0.5s ease;
    }
    .blitzkrieg-fill { background-color: #4CAF50; }
    .shootout-fill { background-color: #FF5722; }
    .siege-fill { background-color: #2196F3; }
    .chess-fill { background-color: #9C27B0; }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header (unchanged)
    st.markdown('<h1 class="main-header">⚽ NARRATIVE PREDICTION ENGINE v2.0</h1>', unsafe_allow_html=True)
    st.markdown("### **Fixed Scoring Formulas • Better Predictions • Clear Insights**")
    
    # Initialize FINAL engine
    engine = FinalNarrativePredictionEngine()
    
    # Create two columns (unchanged)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h3 class="sub-header">📤 Upload Match Data</h3>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Successfully loaded {len(df)} matches")
                
                with st.expander("📊 Data Preview", expanded=False):
                    st.dataframe(df.head())
                
                st.markdown("### Select Matches to Predict")
                
                match_options = df.apply(lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", axis=1).tolist()
                selected_matches = st.multiselect("Choose matches", match_options, default=match_options)
                
                debug_mode = st.checkbox("🔍 Enable Debug Mode (Show Scoring Details)")
                
                if st.button("🚀 Generate Predictions", type="primary", key="predict_button"):
                    predictions = []
                    debug_data = []
                    
                    with st.spinner("Analyzing matches..."):
                        for match_str in selected_matches:
                            match_idx = match_options.index(match_str)
                            match_row = df.iloc[match_idx]
                            
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
                            
                            # Use FINAL prediction engine
                            prediction = engine.predict_match(match_data)
                            predictions.append(prediction)
                            
                            if debug_mode:
                                debug_data.append({
                                    "match": prediction["match"],
                                    "scores": prediction["scores"],
                                    "dominance_gap": prediction["_internal_flags"]["dominance_gap"],
                                    "close_call": prediction["_internal_flags"]["close_call"],
                                    "second_narrative": prediction["_internal_flags"]["second_narrative"]
                                })
                    
                    st.session_state.predictions = predictions
                    if debug_mode:
                        st.session_state.debug_data = debug_data
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV: {str(e)}")
        
        else:
            st.info("👆 **Upload your match data CSV**")
    
    with col2:
        st.markdown('<h3 class="sub-header">🎯 Prediction Results</h3>', unsafe_allow_html=True)
        
        if "predictions" in st.session_state and st.session_state.predictions:
            predictions = st.session_state.predictions
            
            # Summary statistics (unchanged display)
            if len(predictions) > 1:
                narratives_count = {}
                for pred in predictions:
                    narrative = pred["dominant_narrative"]
                    narratives_count[narrative] = narratives_count.get(narrative, 0) + 1
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    st.metric("Total Matches", len(predictions))
                with col_sum2:
                    st.metric("Tier 1 Predictions", sum(1 for p in predictions if p["tier"] == "TIER 1 (STRONG)"))
                with col_sum3:
                    most_common = max(narratives_count, key=narratives_count.get) if narratives_count else "None"
                    st.metric("Most Common Narrative", most_common)
            
            # Display predictions (frontend UNCHANGED)
            for i, pred in enumerate(predictions):
                # Determine tier class (unchanged)
                if pred["tier"] == "TIER 1 (STRONG)":
                    tier_class = "tier-1"
                elif pred["tier"] == "TIER 2 (MEDIUM)":
                    tier_class = "tier-2"
                else:
                    tier_class = "tier-3"
                
                st.markdown(f'<div class="prediction-card {tier_class}">', unsafe_allow_html=True)
                
                # Match header (unchanged)
                st.markdown(f"### **{pred['match']}**")
                st.markdown(f"**Date:** {pred['date']} | **Tier:** {pred['tier']} | **Confidence:** {pred['confidence']}")
                
                # Narrative prediction (unchanged)
                col_pred1, col_pred2 = st.columns(2)
                
                with col_pred1:
                    narrative_color = pred["narrative_color"]
                    
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: {narrative_color}20; border-radius: 5px; border-left: 4px solid {narrative_color};">
                        <h4 style="margin: 0; color: {narrative_color};">{pred['dominant_narrative']}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold;">Score: {pred['dominant_score']:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Narrative scores visualization (unchanged)
                    st.markdown("**All Narrative Scores:**")
                    for narrative, score in pred["scores"].items():
                        fill_class = f"{narrative.lower().replace(' ', '-')}-fill"
                        st.markdown(f"**{narrative}:**")
                        st.markdown(f'<div class="score-bar"><div class="score-fill {fill_class}" style="width: {score}%"></div></div>', unsafe_allow_html=True)
                        st.markdown(f"<small>{score:.1f}/100</small>", unsafe_allow_html=True)
                
                with col_pred2:
                    # Key stats (unchanged)
                    st.markdown("**📊 Key Statistics:**")
                    st.write(f"**Expected Goals:** {pred['expected_goals']:.1f}")
                    st.write(f"**BTTS Probability:** {pred['btts_probability']}%")
                    st.write(f"**Over 2.5 Probability:** {pred['over_25_probability']}%")
                    st.write(f"**Recommended Stake:** {pred['stake_recommendation']}")
                    
                    # Quick insights (now includes close call info)
                    st.markdown("**💡 Quick Insights:**")
                    st.write(pred["description"])
                
                # Expected flow (unchanged)
                with st.expander("📈 Expected Match Flow", expanded=False):
                    st.write(pred["expected_flow"])
                
                # Betting recommendations (unchanged)
                st.markdown("**💰 Betting Recommendations:**")
                rec_cols = st.columns(2)
                for j, bet in enumerate(pred["betting_markets"]):
                    with rec_cols[j % 2]:
                        st.write(f"• {bet}")
                
                # Debug info if enabled (enhanced with dominance info)
                if debug_mode and "debug_data" in st.session_state and i < len(st.session_state.debug_data):
                    debug_info = st.session_state.debug_data[i]
                    with st.expander("🔍 Debug Scoring Details", expanded=False):
                        st.write(f"**Match:** {debug_info['match']}")
                        st.write(f"**Dominance Gap:** {debug_info['dominance_gap']:.1f} points")
                        if debug_info['close_call']:
                            st.write(f"**Close Call:** Yes (with {debug_info['second_narrative']})")
                        st.write("**All Scores:**")
                        for narrative, score in debug_info['scores'].items():
                            st.write(f"- {narrative}: {score:.1f}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export predictions (unchanged)
            st.markdown("---")
            st.markdown("### 📊 Export Predictions")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("Export to CSV", key="export_csv"):
                    export_df = pd.DataFrame([{
                        "Match": p["match"],
                        "Date": p["date"],
                        "Predicted_Narrative": p["dominant_narrative"],
                        "Narrative_Score": p["dominant_score"],
                        "Tier": p["tier"],
                        "Confidence": p["confidence"],
                        "Expected_Goals": p["expected_goals"],
                        "BTTS_Probability": p["btts_probability"],
                        "Over_25_Probability": p["over_25_probability"],
                        "Stake_Recommendation": p["stake_recommendation"],
                        "Betting_Market_1": p["betting_markets"][0] if len(p["betting_markets"]) > 0 else "",
                        "Betting_Market_2": p["betting_markets"][1] if len(p["betting_markets"]) > 1 else "",
                        "Betting_Market_3": p["betting_markets"][2] if len(p["betting_markets"]) > 2 else ""
                    } for p in predictions])
                    
                    csv_export = export_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Predictions CSV",
                        data=csv_export,
                        file_name=f"narrative_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_predictions"
                    )
            
            with col_export2:
                if st.button("Clear Predictions", key="clear_predictions"):
                    st.session_state.predictions = None
                    if "debug_data" in st.session_state:
                        st.session_state.debug_data = None
                    st.rerun()
        
        else:
            st.info("👈 **Upload a CSV file and generate predictions to see results here**")

if __name__ == "__main__":
    main()
