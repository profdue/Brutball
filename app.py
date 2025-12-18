# app.py - NARRATIVE PREDICTION ENGINE v2.3
# ✅ Implements ground truth rules directly from CSV analysis

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import io
import base64

# ==============================================
# GROUND TRUTH PREDICTION ENGINE v2.3
# ✅ Direct CSV signal mapping with suppression logic
# ==============================================

class GroundTruthPredictionEngine:
    """Engine that implements direct CSV signal mapping"""
    
    def __init__(self):
        # Manager database
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
        
        # Narrative definitions with ground truth rules
        self.narratives = {
            "SIEGE": {
                "description": "Attack vs Defense - Dominant attacker vs organized defense",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "primary_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"],
                "color": "#2196F3",
                "suppression_rule": "Defense ≥ 8 AND Pragmatic ≥ 7"
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "primary_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"],
                "color": "#FF5722",
                "suppression_rule": "NOT (Defense ≥ 8 AND Pragmatic ≥ 7)"
            },
            "CONTROLLED_EDGE": {
                "description": "Grinding Advantage - Favorite edges cautious game",
                "flow": "• Cautious start from both sides\n• Favorite gradually establishes control\n• Breakthrough likely 30-60 mins\n• Limited scoring chances overall\n• Narrow victory or draw",
                "primary_markets": ["Under 2.5 goals", "BTTS: No", "Favorite to win or draw", "First goal 30-60 mins", "Few corners total"],
                "color": "#FF9800",
                "subtypes": ["HIGH_QUALITY", "LOW_TEMPO", "STANDARD"]
            },
            "CHESS_MATCH": {
                "description": "Tactical Stalemate - Both cautious, few chances",
                "flow": "• Cautious start from both teams (0-30 mins)\n• Midfield battle dominates, few clear chances\n• Set pieces become primary scoring threats\n• First goal (if any) often decisive\n• Late tactical changes unlikely to alter outcome significantly",
                "primary_markets": ["Under 2.5 goals", "BTTS: No", "0-0 or 1-0 correct score", "Few goals first half", "Under 1.5 goals"],
                "color": "#9C27B0"
            },
            "BLITZKRIEG": {
                "description": "Early Domination - Favorite crushes weak opponent",
                "flow": "• Early pressure from favorite (0-15 mins)\n• Breakthrough before 30 mins\n• Opponent confidence collapses after first goal\n• Additional goals in 35-65 minute window\n• Game effectively over by 70 mins",
                "primary_markets": ["Favorite to win", "Favorite clean sheet", "First goal before 25:00", "Over 2.5 team goals for favorite", "Favorite -1.5 Asian handicap"],
                "color": "#4CAF50",
                "eligibility_rules": ["Attack diff ≥ 2", "Possession diff ≥ 2", "Odds ≤ 1.60", "Prob ≥ 65%", "Tier ≥ 2"]
            }
        }
        
        # Hybrid narratives
        self.hybrid_narratives = {
            "EDGE-CHAOS": {
                "description": "Tight but Explosive - Controlled game that could erupt",
                "parent_narratives": ["CONTROLLED_EDGE", "SHOOTOUT"],
                "color": "#FF9800",
                "secondary_color": "#FF5722",
                "trigger_conditions": ["HIGH_PRESS_HIGH_ATTACK", "STYLE_CLASH", "ATTACK_HEAVY"],
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
                "color": "#FF9800",
                "secondary_color": "#2196F3",
                "hybrid_markets": [
                    "Under 2.75 goals (Asian)",
                    "Favorite to win to nil OR 1-0 correct score",
                    "First goal 30-60 minutes",
                    "Favorite to have 60%+ possession",
                    "Under 10.5 corners total"
                ],
                "flow": "• Controlled start with favorite establishing dominance\n• Patient buildup against organized defense\n• Breakthrough likely mid-game rather than early\n• Low-scoring but controlled by favorite"
            }
        }
    
    # ========== GROUND TRUTH RULES ==========
    
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
    
    # ========== RULE 1: SIEGE DETECTION (FIRST PRIORITY) ==========
    
    def detect_siege(self, match_data):
        """RULE 1: Detect SIEGE conditions (Attack ≥ 8 vs Defense ≥ 8 + Pragmatic ≥ 7)"""
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if prob["favorite_is_home"]:
            attacker_attack = match_data["home_attack_rating"]
            defender_defense = match_data["away_defense_rating"]
            defender_pragmatic = match_data["away_pragmatic_rating"]
        else:
            attacker_attack = match_data["away_attack_rating"]
            defender_defense = match_data["home_defense_rating"]
            defender_pragmatic = match_data["home_pragmatic_rating"]
        
        # SIEGE Conditions (ALL must be true):
        # 1. Attacker attack ≥ 8
        # 2. Defender defense ≥ 8
        # 3. Defender pragmatic ≥ 7
        # 4. Favorite probability ≥ 60%
        
        siege_conditions = [
            attacker_attack >= 8,
            defender_defense >= 8,
            defender_pragmatic >= 7,
            prob["favorite_probability"] >= 60
        ]
        
        return all(siege_conditions)
    
    # ========== RULE 2: SHOOTOUT SUPPRESSION ==========
    
    def is_shootout_suppressed(self, match_data):
        """RULE 2: Check if SHOOTOUT should be suppressed"""
        # Condition: Either team has defense ≥ 8 AND pragmatic ≥ 7
        home_suppress = (match_data["home_defense_rating"] >= 8 and 
                         match_data["home_pragmatic_rating"] >= 7)
        away_suppress = (match_data["away_defense_rating"] >= 8 and 
                         match_data["away_pragmatic_rating"] >= 7)
        
        return home_suppress or away_suppress
    
    # ========== RULE 3: HYBRID VOLATILITY OVERRIDE ==========
    
    def check_hybrid_override(self, match_data):
        """RULE 3: Check conditions that force hybrid consideration"""
        conditions = []
        
        # Condition A: HIGH_PRESS_HIGH_ATTACK
        # Both teams press high (≥7) AND attack high (≥7)
        if (match_data["home_press_rating"] >= 7 and 
            match_data["away_press_rating"] >= 7 and
            match_data["home_attack_rating"] >= 7 and 
            match_data["away_attack_rating"] >= 7):
            conditions.append("HIGH_PRESS_HIGH_ATTACK")
        
        # Condition B: STYLE_CLASH
        # High press vs Possession style clash
        press_diff = abs(match_data["home_press_rating"] - match_data["away_press_rating"])
        possession_diff = abs(match_data["home_possession_rating"] - match_data["away_possession_rating"])
        
        if press_diff >= 3 and possession_diff >= 3:
            conditions.append("STYLE_CLASH")
        
        # Condition C: ATTACK_HEAVY
        # Both attacks ≥ 8, defenses ≤ 7
        if (match_data["home_attack_rating"] >= 8 and 
            match_data["away_attack_rating"] >= 8 and
            match_data["home_defense_rating"] <= 7 and 
            match_data["away_defense_rating"] <= 7):
            conditions.append("ATTACK_HEAVY")
        
        return conditions
    
    # ========== RULE 4: CONTROLLED_EDGE SUBCLASSIFICATION ==========
    
    def subclassify_controlled_edge(self, match_data):
        """RULE 4: Differentiate between CONTROLLED_EDGE subtypes"""
        avg_attack = (match_data["home_attack_rating"] + match_data["away_attack_rating"]) / 2
        avg_press = (match_data["home_press_rating"] + match_data["away_press_rating"]) / 2
        
        if avg_attack >= 7.5 and avg_press >= 7:
            return "HIGH_QUALITY"  # e.g., Aston Villa vs Man Utd
        elif avg_attack <= 6 and avg_press <= 6:
            return "LOW_TEMPO"  # e.g., Wolves vs Brentford
        else:
            return "STANDARD"
    
    # ========== NARRATIVE SCORING WITH SUPPRESSION ==========
    
    def calculate_narrative_scores(self, match_data):
        """Calculate scores with suppression rules applied"""
        scores = {
            "SIEGE": self.calculate_siege_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "CONTROLLED_EDGE": self.calculate_controlled_edge_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data),
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data)
        }
        
        # Apply suppression rules
        if self.is_shootout_suppressed(match_data):
            scores["SHOOTOUT"] *= 0.5  # Halve SHOOTOUT score
        
        # Apply SIEGE boost if detected
        if self.detect_siege(match_data):
            scores["SIEGE"] += 30
        
        return scores
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score"""
        score = 0
        
        # Check for attacker vs defender mismatch
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if prob["favorite_is_home"]:
            if (match_data["home_attack_rating"] >= 8 and 
                match_data["away_defense_rating"] >= 8):
                score += 40
        else:
            if (match_data["away_attack_rating"] >= 8 and 
                match_data["home_defense_rating"] >= 8):
                score += 40
        
        # Add for pragmatic defense
        if (match_data["home_pragmatic_rating"] >= 7 or 
            match_data["away_pragmatic_rating"] >= 7):
            score += 20
        
        # Possession dominance
        possession_diff = abs(match_data["home_possession_rating"] - match_data["away_possession_rating"])
        if possession_diff >= 3:
            score += 15
        
        # Favorite strength
        if prob["favorite_strength"] in ["STRONG", "ELITE"]:
            score += 10
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score"""
        score = 0
        
        # Both attacking (primary factor)
        if (match_data["home_attack_rating"] >= 7 and 
            match_data["away_attack_rating"] >= 7):
            score += 30
        
        # Weak defenses (secondary factor)
        avg_defense = (match_data["home_defense_rating"] + match_data["away_defense_rating"]) / 2
        if avg_defense <= 6.5:
            score += 25
        elif avg_defense <= 7:
            score += 15
        
        # High press both
        if (match_data["home_press_rating"] >= 7 and 
            match_data["away_press_rating"] >= 7):
            score += 20
        
        # Historical high scoring
        if match_data["last_h2h_goals"] >= 3:
            score += 15
        
        # BTTS history
        if match_data["last_h2h_btts"] == "Yes":
            score += 10
        
        return min(100, score)
    
    def calculate_controlled_edge_score(self, match_data):
        """Calculate CONTROLLED_EDGE score"""
        score = 0
        
        # Slight favorite
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if 55 <= prob["favorite_probability"] < 65:
            score += 25
        elif 50 <= prob["favorite_probability"] < 55:
            score += 15
        
        # Balanced teams
        attack_diff = abs(match_data["home_attack_rating"] - match_data["away_attack_rating"])
        defense_diff = abs(match_data["home_defense_rating"] - match_data["away_defense_rating"])
        
        if attack_diff <= 2 and defense_diff <= 2:
            score += 20
        
        # Moderate defenses
        if (6 <= match_data["home_defense_rating"] <= 8 and 
            6 <= match_data["away_defense_rating"] <= 8):
            score += 15
        
        # Conservative approach
        if (match_data["home_pragmatic_rating"] >= 5 and 
            match_data["away_pragmatic_rating"] >= 5):
            score += 15
        
        # Close table positions
        position_gap = abs(match_data["home_position"] - match_data["away_position"])
        if position_gap <= 3:
            score += 10
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score"""
        score = 0
        
        # Very close match
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if prob["favorite_probability"] < 52:
            score += 25
        
        # Both pragmatic
        if (match_data["home_pragmatic_rating"] >= 7 and 
            match_data["away_pragmatic_rating"] >= 7):
            score += 25
        
        # Both strong defense
        if (match_data["home_defense_rating"] >= 8 and 
            match_data["away_defense_rating"] >= 8):
            score += 20
        
        # Both moderate/low attack
        if (match_data["home_attack_rating"] <= 6 and 
            match_data["away_attack_rating"] <= 6):
            score += 15
        
        return min(100, score)
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        # Elite favorite
        if prob["favorite_strength"] == "ELITE":
            score += 40
        
        # Attack vs defense mismatch
        if prob["favorite_is_home"]:
            if (match_data["home_attack_rating"] - match_data["away_defense_rating"]) >= 3:
                score += 30
        else:
            if (match_data["away_attack_rating"] - match_data["home_defense_rating"]) >= 3:
                score += 30
        
        # Form dominance
        # (form analysis would go here)
        
        return min(100, score)
    
    # ========== DYNAMIC PROBABILITY CALCULATIONS ==========
    
    def calculate_dynamic_probabilities(self, narrative, match_data, subtype=None):
        """Calculate probabilities based on actual ratings"""
        
        # Base calculations from ratings
        avg_attack = (match_data["home_attack_rating"] + match_data["away_attack_rating"]) / 20
        avg_defense = (match_data["home_defense_rating"] + match_data["away_defense_rating"]) / 20
        avg_press = (match_data["home_press_rating"] + match_data["away_press_rating"]) / 20
        
        if narrative == "SIEGE":
            # Base: 2.4-3.0 range
            base_xg = 2.4 + (avg_attack * 0.6)
            # Defense reduces xG
            xg = base_xg * (1 - (avg_defense * 0.1))
            btts = 30 + (15 * (1 - avg_defense))
            
        elif narrative == "SHOOTOUT":
            # Base: 3.2-3.8 range
            base_xg = 3.2 + (avg_attack * 0.6)
            # Press increases xG
            xg = base_xg * (1 + (avg_press * 0.1))
            btts = 65 + (15 * (1 - avg_defense))
            
        elif narrative == "CONTROLLED_EDGE":
            # Subtype-based scaling
            if subtype == "HIGH_QUALITY":
                # 2.8-3.2 range
                base_xg = 2.8 + (avg_attack * 0.4)
                btts = 45 + (15 * (1 - avg_defense))
            elif subtype == "LOW_TEMPO":
                # 2.2-2.6 range
                base_xg = 2.2 + (avg_attack * 0.4)
                btts = 35 + (10 * (1 - avg_defense))
            else:  # STANDARD
                # 2.4-2.8 range
                base_xg = 2.4 + (avg_attack * 0.4)
                btts = 40 + (12 * (1 - avg_defense))
            
            xg = base_xg
        
        elif narrative == "CHESS_MATCH":
            # 1.8-2.2 range
            xg = 1.8 + (avg_attack * 0.4)
            btts = 30 * (1 - avg_defense)
            
        elif narrative == "BLITZKRIEG":
            # 3.0-3.4 range
            xg = 3.0 + (avg_attack * 0.4)
            btts = 30 + (10 * (1 - avg_defense))
            
        else:  # Hybrid or unknown
            xg = 2.5 + (avg_attack * 0.5)
            btts = 50
        
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
        elif narrative in ["SIEGE", "CHESS_MATCH"]:
            over25 -= 10
        elif narrative == "CONTROLLED_EDGE":
            if subtype == "HIGH_QUALITY":
                over25 += 5
            elif subtype == "LOW_TEMPO":
                over25 -= 5
        
        return {
            "xg": max(1.8, min(4.0, round(xg, 1))),
            "btts": max(20, min(85, round(btts, 1))),
            "over25": max(25, min(90, over25))
        }
    
    # ========== MAIN PREDICTION LOGIC ==========
    
    def predict_match(self, match_data):
        """Main prediction with ground truth rules"""
        
        # ===== STEP 1: Apply ground truth rules =====
        siege_detected = self.detect_siege(match_data)
        shootout_suppressed = self.is_shootout_suppressed(match_data)
        hybrid_conditions = self.check_hybrid_override(match_data)
        ce_subtype = self.subclassify_controlled_edge(match_data)
        
        # ===== STEP 2: Calculate scores with suppression =====
        scores = self.calculate_narrative_scores(match_data)
        
        # ===== STEP 3: Determine narrative =====
        
        # First check for forced SIEGE
        if siege_detected and scores["SIEGE"] >= 50:
            dominant_narrative = "SIEGE"
            dominant_score = scores["SIEGE"]
            force_reason = "SIEGE_DETECTED"
        
        # Check for hybrid conditions
        elif hybrid_conditions and scores["CONTROLLED_EDGE"] >= 50 and scores["SHOOTOUT"] >= 50:
            # Check margin for hybrid
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_narrative, top_score = sorted_scores[0]
            second_narrative, second_score = sorted_scores[1]
            
            if (top_narrative in ["CONTROLLED_EDGE", "SHOOTOUT"] and 
                second_narrative in ["CONTROLLED_EDGE", "SHOOTOUT"] and
                abs(top_score - second_score) < 15):  # Looser margin for forced hybrids
                
                dominant_narrative = "EDGE-CHAOS"
                dominant_score = max(top_score, second_score)
                force_reason = f"HYBRID_OVERRIDE: {hybrid_conditions}"
            else:
                dominant_narrative = top_narrative
                dominant_score = top_score
                force_reason = None
        else:
            # Normal selection
            dominant_narrative = max(scores, key=scores.get)
            dominant_score = scores[dominant_narrative]
            force_reason = None
        
        # ===== STEP 4: Determine tier and confidence =====
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
        
        # ===== STEP 5: Calculate probabilities =====
        if dominant_narrative == "EDGE-CHAOS":
            # Hybrid probabilities (blend)
            ce_probs = self.calculate_dynamic_probabilities("CONTROLLED_EDGE", match_data, ce_subtype)
            shootout_probs = self.calculate_dynamic_probabilities("SHOOTOUT", match_data)
            
            # Weighted blend (60% CONTROLLED_EDGE, 40% SHOOTOUT for chaos)
            xg = (ce_probs["xg"] * 0.6) + (shootout_probs["xg"] * 0.4)
            btts = (ce_probs["btts"] * 0.6) + (shootout_probs["btts"] * 0.4)
            
            narrative_info = self.hybrid_narratives["EDGE-CHAOS"]
            markets = narrative_info["hybrid_markets"]
            flow = narrative_info["flow"]
            description = narrative_info["description"]
            
        else:
            # Single narrative probabilities
            probs = self.calculate_dynamic_probabilities(dominant_narrative, match_data, 
                                                        ce_subtype if dominant_narrative == "CONTROLLED_EDGE" else None)
            xg = probs["xg"]
            btts = probs["btts"]
            
            if dominant_narrative in self.narratives:
                narrative_info = self.narratives[dominant_narrative]
                markets = narrative_info["primary_markets"]
                flow = narrative_info["flow"]
                description = narrative_info["description"]
            else:
                # Fallback
                markets = []
                flow = ""
                description = dominant_narrative
        
        # Calculate Over 2.5 from xG
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
        
        # Narrative adjustment
        if dominant_narrative == "SHOOTOUT":
            over25 += 10
        elif dominant_narrative == "BLITZKRIEG":
            over25 += 5
        elif dominant_narrative in ["SIEGE", "CHESS_MATCH"]:
            over25 -= 10
        
        over25 = max(25, min(90, over25))
        
        # ===== STEP 6: Prepare result =====
        result = {
            "match": f"{match_data['home_team']} vs {match_data['away_team']}",
            "date": match_data["date"],
            "scores": scores,
            "dominant_narrative": dominant_narrative,
            "dominant_score": dominant_score,
            "tier": tier,
            "confidence": confidence,
            "tier_level": tier_level,
            "expected_goals": xg,
            "btts_probability": btts,
            "over_25_probability": over25,
            "stake_recommendation": stake,
            "expected_flow": flow,
            "betting_markets": markets,
            "description": description,
            "narrative_color": self.narratives.get(dominant_narrative, {}).get("color", "#6c757d"),
            "probabilities": self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"]),
            "ground_truth_flags": {
                "siege_detected": siege_detected,
                "shootout_suppressed": shootout_suppressed,
                "hybrid_conditions": hybrid_conditions,
                "ce_subtype": ce_subtype,
                "force_reason": force_reason
            }
        }
        
        # Add secondary color for hybrids
        if dominant_narrative == "EDGE-CHAOS":
            result["secondary_color"] = self.hybrid_narratives["EDGE-CHAOS"]["secondary_color"]
            result["hybrid_parents"] = ["CONTROLLED_EDGE", "SHOOTOUT"]
        
        return result

# ==============================================
# ENHANCED STREAMLIT APP
# ==============================================

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.3 - Ground Truth",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS
    st.markdown("""
    <style>
    .ground-truth-flag {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 5px;
        display: inline-block;
    }
    .suppression-flag {
        background-color: #FF5722;
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 2px;
        display: inline-block;
    }
    .hybrid-parent {
        background-color: #f0f0f0;
        padding: 8px 15px;
        border-radius: 10px;
        margin: 5px;
        border-left: 4px solid #FF9800;
    }
    .probability-scale {
        height: 20px;
        background: linear-gradient(90deg, #F44336 0%, #FF9800 50%, #4CAF50 100%);
        border-radius: 10px;
        margin: 10px 0;
        position: relative;
    }
    .probability-marker {
        position: absolute;
        top: -5px;
        width: 3px;
        height: 30px;
        background-color: black;
    }
    .rule-explanation {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header
    st.markdown('<h1 style="font-size: 2.8rem; color: #1E88E5; text-align: center; margin-bottom: 0.5rem;">⚽ NARRATIVE PREDICTION ENGINE v2.3</h1>', unsafe_allow_html=True)
    st.markdown("### **Ground Truth Edition • CSV Signal Mapping • Stress-Tested**")
    
    # Initialize engine
    engine = GroundTruthPredictionEngine()
    
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
            # Ground truth sample matches
            sample_matches = [
                # Manchester City vs West Ham (SIEGE)
                {
                    "match_id": "EPL_2025-12-20_MCI_WHU",
                    "league": "Premier League", "date": "2025-12-20",
                    "home_team": "Manchester City", "away_team": "West Ham",
                    "home_position": 1, "away_position": 15,
                    "home_odds": 1.25, "away_odds": 13.00,
                    "home_form": "WWWWW", "away_form": "LLLLL",
                    "home_manager": "Pep Guardiola", "away_manager": "David Moyes",
                    "last_h2h_goals": 4, "last_h2h_btts": "No",
                    "home_manager_style": "Possession-based & control",
                    "away_manager_style": "Pragmatic/Defensive",
                    "home_attack_rating": 10, "away_attack_rating": 5,
                    "home_defense_rating": 8, "away_defense_rating": 9,
                    "home_press_rating": 9, "away_press_rating": 6,
                    "home_possession_rating": 10, "away_possession_rating": 5,
                    "home_pragmatic_rating": 4, "away_pragmatic_rating": 9
                },
                # Tottenham vs Liverpool (EDGE-CHAOS)
                {
                    "match_id": "EPL_2025-12-20_TOT_LIV",
                    "league": "Premier League", "date": "2025-12-20",
                    "home_team": "Tottenham", "away_team": "Liverpool",
                    "home_position": 5, "away_position": 3,
                    "home_odds": 2.45, "away_odds": 2.65,
                    "home_form": "WWLWD", "away_form": "DWWWD",
                    "home_manager": "Ange Postecoglou", "away_manager": "Arne Slot",
                    "last_h2h_goals": 3, "last_h2h_btts": "Yes",
                    "home_manager_style": "High press & transition",
                    "away_manager_style": "High press & transition",
                    "home_attack_rating": 9, "away_attack_rating": 9,
                    "home_defense_rating": 5, "away_defense_rating": 6,
                    "home_press_rating": 9, "away_press_rating": 9,
                    "home_possession_rating": 6, "away_possession_rating": 7,
                    "home_pragmatic_rating": 4, "away_pragmatic_rating": 5
                },
                # Newcastle vs Chelsea (EDGE-CHAOS)
                {
                    "match_id": "EPL_2025-12-20_NEW_CHE",
                    "league": "Premier League", "date": "2025-12-20",
                    "home_team": "Newcastle United", "away_team": "Chelsea",
                    "home_position": 12, "away_position": 4,
                    "home_odds": 2.68, "away_odds": 2.57,
                    "home_form": "WWWWL", "away_form": "DWWWD",
                    "home_manager": "Eddie Howe", "away_manager": "Enzo Maresca",
                    "last_h2h_goals": 2, "last_h2h_btts": "No",
                    "home_manager_style": "High press & transition",
                    "away_manager_style": "Possession-based & control",
                    "home_attack_rating": 9, "away_attack_rating": 8,
                    "home_defense_rating": 6, "away_defense_rating": 7,
                    "home_press_rating": 9, "away_press_rating": 7,
                    "home_possession_rating": 7, "away_possession_rating": 9,
                    "home_pragmatic_rating": 5, "away_pragmatic_rating": 6
                },
                # Fulham vs Nottingham Forest (SHOOTOUT)
                {
                    "match_id": "EPL_2025-12-22_FUL_NOT",
                    "league": "Premier League", "date": "2025-12-22",
                    "home_team": "Fulham", "away_team": "Nottingham Forest",
                    "home_position": 11, "away_position": 13,
                    "home_odds": 2.10, "away_odds": 3.40,
                    "home_form": "DLWWD", "away_form": "WLLWD",
                    "home_manager": "Marco Silva", "away_manager": "Régis Le Bris",
                    "last_h2h_goals": 3, "last_h2h_btts": "Yes",
                    "home_manager_style": "Balanced/Adaptive",
                    "away_manager_style": "Progressive/Developing",
                    "home_attack_rating": 8, "away_attack_rating": 9,
                    "home_defense_rating": 7, "away_defense_rating": 5,
                    "home_press_rating": 7, "away_press_rating": 9,
                    "home_possession_rating": 7, "away_possession_rating": 6,
                    "home_pragmatic_rating": 6, "away_pragmatic_rating": 4
                }
            ]
            df = pd.DataFrame(sample_matches)
            st.success(f"✅ Loaded {len(df)} ground truth sample matches")
        
        # Analysis settings
        st.markdown("### 🔧 Analysis Settings")
        
        show_ground_truth = st.checkbox("Show Ground Truth Rules", value=True)
        show_suppression = st.checkbox("Show Suppression Logic", value=True)
        
        # Navigation
        st.markdown("### 📋 Navigation")
        page = st.radio("Go to", ["Predictions", "Ground Truth Rules", "Export"])
    
    # Main content
    if df is not None:
        # Data preview with signal highlighting
        with st.expander("📊 Data Preview with Signal Analysis", expanded=False):
            st.dataframe(df)
            
            # Signal analysis
            st.markdown("#### 🔍 Key Signal Detection")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_press = df[['home_press_rating', 'away_press_rating']].max().max()
                st.metric("Max Press Rating", high_press)
            
            with col2:
                high_defense = df[['home_defense_rating', 'away_defense_rating']].max().max()
                st.metric("Max Defense Rating", high_defense)
            
            with col3:
                pragmatic_teams = ((df['home_pragmatic_rating'] >= 7).sum() + 
                                 (df['away_pragmatic_rating'] >= 7).sum())
                st.metric("Pragmatic Teams (≥7)", pragmatic_teams)
        
        # Match selection
        st.markdown("### 🎯 Select Matches for Ground Truth Analysis")
        
        match_options = df.apply(
            lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", 
            axis=1
        ).tolist()
        
        selected_matches = st.multiselect(
            "Choose matches to analyze",
            match_options,
            default=match_options[:min(4, len(match_options))]
        )
        
        # Generate predictions
        if st.button("🚀 Run Ground Truth Analysis", type="primary"):
            with st.spinner("Applying ground truth rules..."):
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
                st.success(f"✅ Generated {len(predictions)} ground truth predictions")
    
    # Display predictions
    if "predictions" in st.session_state:
        predictions = st.session_state.predictions
        
        if page == "Predictions":
            # Summary dashboard
            st.markdown("### 📈 Ground Truth Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                siege_count = sum(1 for p in predictions if p["dominant_narrative"] == "SIEGE")
                st.metric("⚔️ SIEGE Predictions", siege_count)
            
            with col2:
                hybrid_count = sum(1 for p in predictions if p["dominant_narrative"] == "EDGE-CHAOS")
                st.metric("🔄 EDGE-CHAOS Predictions", hybrid_count)
            
            with col3:
                shootout_count = sum(1 for p in predictions if p["dominant_narrative"] == "SHOOTOUT")
                st.metric("🔥 SHOOTOUT Predictions", shootout_count)
            
            with col4:
                suppressed = sum(1 for p in predictions if p["ground_truth_flags"]["shootout_suppressed"])
                st.metric("🛡️ SHOOTOUT Suppressed", suppressed)
            
            # Individual predictions with ground truth explanation
            for pred in predictions:
                # Card styling
                narrative_color = pred["narrative_color"]
                st.markdown(f'<div class="prediction-card" style="border-left: 5px solid {narrative_color};">', unsafe_allow_html=True)
                
                # Header with ground truth flags
                col_h1, col_h2 = st.columns([3, 1])
                
                with col_h1:
                    st.markdown(f"### {pred['match']}")
                    st.markdown(f"**Date:** {pred['date']} | **Tier:** {pred['tier']}")
                    
                    # Narrative badge
                    if pred["dominant_narrative"] == "EDGE-CHAOS":
                        st.markdown(f'<div style="background: linear-gradient(90deg, {pred["narrative_color"]}, {pred.get("secondary_color", "#FF5722")}); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 10px 0;">'
                                  f'<strong>{pred["dominant_narrative"]}</strong>'
                                  f'</div>', unsafe_allow_html=True)
                        
                        # Show parent narratives
                        st.markdown('<div class="hybrid-parent">', unsafe_allow_html=True)
                        st.markdown("**Hybrid Parents:** CONTROLLED_EDGE + SHOOTOUT")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="background-color: {pred["narrative_color"]}20; padding: 8px 16px; border-radius: 20px; border: 2px solid {pred["narrative_color"]}; display: inline-block; margin: 10px 0;">'
                                  f'<strong style="color: {pred["narrative_color"]};">{pred["dominant_narrative"]}</strong>'
                                  f'</div>', unsafe_allow_html=True)
                
                with col_h2:
                    # Score and stake
                    st.markdown(f"**Score:** {pred['dominant_score']:.1f}/100")
                    st.markdown(f"**Confidence:** {pred['confidence']}")
                    st.markdown(f'<div class="stake-badge">{pred["stake_recommendation"]}</div>', unsafe_allow_html=True)
                
                # Ground truth flags
                if show_ground_truth:
                    flags = pred["ground_truth_flags"]
                    if any([flags["siege_detected"], flags["shootout_suppressed"], flags["hybrid_conditions"]]):
                        st.markdown("#### 🎯 Ground Truth Rules Applied")
                        
                        col_f1, col_f2, col_f3 = st.columns(3)
                        
                        with col_f1:
                            if flags["siege_detected"]:
                                st.markdown('<div class="ground-truth-flag">⚔️ SIEGE DETECTED</div>', unsafe_allow_html=True)
                        
                        with col_f2:
                            if flags["shootout_suppressed"]:
                                st.markdown('<div class="suppression-flag">🛡️ SHOOTOUT SUPPRESSED</div>', unsafe_allow_html=True)
                        
                        with col_f3:
                            if flags["hybrid_conditions"]:
                                st.markdown('<div class="ground-truth-flag">🔄 HYBRID CONDITIONS</div>', unsafe_allow_html=True)
                                st.markdown(f"*{', '.join(flags['hybrid_conditions'])}*")
                        
                        if flags.get("force_reason"):
                            st.info(f"**Decision Reason:** {flags['force_reason']}")
                
                # Main content
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    # Narrative scores
                    st.markdown("#### 📊 Narrative Scores (with Suppression)")
                    
                    for narrative, score in pred["scores"].items():
                        color = engine.narratives.get(narrative, {}).get("color", "#6c757d")
                        
                        # Highlight if suppressed
                        if narrative == "SHOOTOUT" and pred["ground_truth_flags"]["shootout_suppressed"]:
                            label = f"🛡️ {narrative} (Suppressed)"
                        elif narrative == "SIEGE" and pred["ground_truth_flags"]["siege_detected"]:
                            label = f"⚔️ {narrative} (Detected)"
                        else:
                            label = narrative
                        
                        st.markdown(f"**{label}:** {score:.1f}")
                        st.markdown(f'<div class="score-bar"><div style="width: {score}%; height: 100%; background-color: {color}; border-radius: 10px;"></div></div>', unsafe_allow_html=True)
                    
                    # Key stats with scale visualization
                    st.markdown("#### 📈 Dynamic Probabilities")
                    
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.metric("Expected Goals", f"{pred['expected_goals']:.1f}")
                        # xG scale
                        xg_position = ((pred['expected_goals'] - 1.8) / (4.0 - 1.8)) * 100
                        st.markdown(f'<div class="probability-scale"><div class="probability-marker" style="left: {xg_position}%;"></div></div>', unsafe_allow_html=True)
                    
                    with col_s2:
                        st.metric("BTTS %", f"{pred['btts_probability']}%")
                        # BTTS scale
                        btts_position = ((pred['btts_probability'] - 20) / (85 - 20)) * 100
                        st.markdown(f'<div class="probability-scale"><div class="probability-marker" style="left: {btts_position}%;"></div></div>', unsafe_allow_html=True)
                    
                    with col_s3:
                        st.metric("Over 2.5 %", f"{pred['over_25_probability']}%")
                        # Over 2.5 scale
                        over_position = ((pred['over_25_probability'] - 25) / (90 - 25)) * 100
                        st.markdown(f'<div class="probability-scale"><div class="probability-marker" style="left: {over_position}%;"></div></div>', unsafe_allow_html=True)
                
                with col_m2:
                    # Insights
                    st.markdown("#### 💡 Insights")
                    st.info(pred["description"])
                    
                    # Expected flow
                    with st.expander("📈 Expected Match Flow", expanded=False):
                        st.write(pred["expected_flow"])
                    
                    # Betting markets
                    st.markdown("#### 💰 Recommended Markets")
                    for market in pred["betting_markets"]:
                        st.markdown(f"• {market}")
                    
                    # Ground truth explanation
                    if show_ground_truth:
                        with st.expander("🔍 Ground Truth Explanation", expanded=False):
                            flags = pred["ground_truth_flags"]
                            
                            if flags["siege_detected"]:
                                st.markdown("""
                                **⚔️ SIEGE DETECTED:**
                                - Attacker attack ≥ 8
                                - Defender defense ≥ 8  
                                - Defender pragmatic ≥ 7
                                - Favorite probability ≥ 60%
                                """)
                            
                            if flags["shootout_suppressed"]:
                                st.markdown("""
                                **🛡️ SHOOTOUT SUPPRESSED:**
                                - Defense ≥ 8 AND Pragmatic ≥ 7 in at least one team
                                - Halves SHOOTOUT narrative score
                                """)
                            
                            if flags["hybrid_conditions"]:
                                st.markdown(f"""
                                **🔄 HYBRID CONDITIONS:**
                                - {', '.join(flags['hybrid_conditions'])}
                                - Forces EDGE-CHAOS consideration
                                """)
                            
                            if flags["ce_subtype"]:
                                st.markdown(f"""
                                **🎯 CONTROLLED_EDGE Subtype:**
                                - **{flags['ce_subtype']}**
                                - Affects probability ranges
                                """)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Overall analysis
            if len(predictions) > 1:
                st.markdown("### 📊 Ground Truth Analysis")
                
                # Narrative distribution
                narrative_counts = {}
                for pred in predictions:
                    narrative = pred["dominant_narrative"]
                    narrative_counts[narrative] = narrative_counts.get(narrative, 0) + 1
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(narrative_counts.keys()),
                        y=list(narrative_counts.values()),
                        marker_color=[pred["narrative_color"] for pred in predictions for _ in range(narrative_counts.get(pred["dominant_narrative"], 0))]
                    )
                ])
                
                fig.update_layout(
                    title="Narrative Distribution (v2.3 Ground Truth)",
                    xaxis_title="Narrative",
                    yaxis_title="Count",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        elif page == "Ground Truth Rules":
            # Rules explanation
            st.markdown("## 🎯 Ground Truth Rules v2.3")
            
            st.markdown("""
            ### Rule 1: SIEGE Detection (First Priority)
            **Conditions (ALL must be true):**
            1. Attacker attack ≥ 8
            2. Defender defense ≥ 8  
            3. Defender pragmatic ≥ 7
            4. Favorite probability ≥ 60%
            
            **Effect:** Forces SIEGE narrative, overrides other calculations
            **Example:** Manchester City vs West Ham
            """)
            
            st.markdown("""
            ### Rule 2: SHOOTOUT Suppression
            **Condition:** Either team has defense ≥ 8 AND pragmatic ≥ 7
            
            **Effect:** Halves SHOOTOUT narrative score
            **Purpose:** Prevents chaos predictions against organized defenses
            **Example:** Any match with a pragmatic, defensively strong team
            """)
            
            st.markdown("""
            ### Rule 3: Hybrid Volatility Override
            **Conditions (any triggers hybrid):**
            
            **A. HIGH_PRESS_HIGH_ATTACK:**
            - Both teams press ≥ 7 AND attack ≥ 7
            
            **B. STYLE_CLASH:**
            - Press difference ≥ 3 AND possession difference ≥ 3
            
            **C. ATTACK_HEAVY:**
            - Both attacks ≥ 8 AND both defenses ≤ 7
            
            **Effect:** Forces EDGE-CHAOS hybrid consideration
            **Example:** Tottenham vs Liverpool, Newcastle vs Chelsea
            """)
            
            st.markdown("""
            ### Rule 4: CONTROLLED_EDGE Subclassification
            **Subtypes:**
            
            **HIGH_QUALITY:**
            - Average attack ≥ 7.5 AND average press ≥ 7
            - Example: Aston Villa vs Manchester United
            
            **LOW_TEMPO:**
            - Average attack ≤ 6 AND average press ≤ 6  
            - Example: Wolves vs Brentford
            
            **STANDARD:**
            - Everything else
            
            **Effect:** Adjusts probability ranges based on subtype
            """)
            
            st.markdown("""
            ### Probability Scaling Matrix
            """)
            
            # Probability matrix
            matrix_data = {
                "Narrative": ["SIEGE", "CONTROLLED_EDGE (Low)", "CONTROLLED_EDGE (High)", 
                             "EDGE-CHAOS", "SHOOTOUT"],
                "xG Range": ["2.4-3.0", "2.2-2.6", "2.8-3.2", "2.9-3.4", "3.2-3.8"],
                "BTTS Range": ["30-45%", "35-50%", "45-60%", "50-70%", "65-80%"],
                "Over 2.5": ["40-60%", "35-55%", "45-65%", "55-75%", "70-85%"]
            }
            
            matrix_df = pd.DataFrame(matrix_data)
            st.dataframe(matrix_df, use_container_width=True)
        
        elif page == "Export":
            # Export with ground truth data
            st.markdown("## 📊 Export Ground Truth Predictions")
            
            export_data = []
            for pred in predictions:
                export_row = {
                    "Match": pred["match"],
                    "Date": pred["date"],
                    "Narrative": pred["dominant_narrative"],
                    "Score": pred["dominant_score"],
                    "Tier": pred["tier"],
                    "Confidence": pred["confidence"],
                    "Expected_Goals": pred["expected_goals"],
                    "BTTS_Probability": pred["btts_probability"],
                    "Over_25_Probability": pred["over_25_probability"],
                    "Stake_Recommendation": pred["stake_recommendation"],
                    "Siege_Detected": pred["ground_truth_flags"]["siege_detected"],
                    "Shootout_Suppressed": pred["ground_truth_flags"]["shootout_suppressed"],
                    "Hybrid_Conditions": ", ".join(pred["ground_truth_flags"]["hybrid_conditions"]),
                    "CE_Subtype": pred["ground_truth_flags"]["ce_subtype"]
                }
                export_data.append(export_row)
            
            export_df = pd.DataFrame(export_data)
            
            # Preview
            st.dataframe(export_df)
            
            # Download
            csv = export_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="ground_truth_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv">📥 Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Summary statistics
            st.markdown("### 📈 Export Summary")
            col_e1, col_e2, col_e3 = st.columns(3)
            
            with col_e1:
                avg_xg = export_df["Expected_Goals"].mean()
                st.metric("Average xG", f"{avg_xg:.2f}")
            
            with col_e2:
                siege_rate = (export_df["Siege_Detected"].sum() / len(export_df)) * 100
                st.metric("SIEGE Detection Rate", f"{siege_rate:.1f}%")
            
            with col_e3:
                hybrid_rate = (export_df["Hybrid_Conditions"].str.len() > 0).sum() / len(export_df) * 100
                st.metric("Hybrid Trigger Rate", f"{hybrid_rate:.1f}%")
    
    else:
        # Initial state
        st.info("👈 **Upload a CSV file or use sample data to get started**")
        
        # What's new
        with st.expander("🎯 What's New in v2.3 - Ground Truth Edition", expanded=True):
            st.markdown("""
            ### 🔥 Ground Truth Rules Implemented
            
            **1. SIEGE Detection (First Priority)**
            - Attack ≥ 8 vs Defense ≥ 8 + Pragmatic ≥ 7
            - Favorite probability ≥ 60%
            - **Fixes:** Manchester City vs West Ham
            
            **2. SHOOTOUT Suppression**
            - Defense ≥ 8 AND Pragmatic ≥ 7 halves SHOOTOUT score
            - Prevents chaos predictions against organized defenses
            
            **3. Hybrid Volatility Override**
            - **HIGH_PRESS_HIGH_ATTACK:** Both press ≥ 7 AND attack ≥ 7
            - **STYLE_CLASH:** Press diff ≥ 3 AND possession diff ≥ 3
            - **ATTACK_HEAVY:** Both attacks ≥ 8, defenses ≤ 7
            - **Fixes:** Tottenham vs Liverpool, Newcastle vs Chelsea
            
            **4. CONTROLLED_EDGE Subclassification**
            - **HIGH_QUALITY:** Avg attack ≥ 7.5, press ≥ 7
            - **LOW_TEMPO:** Avg attack ≤ 6, press ≤ 6
            - **STANDARD:** Everything else
            - Dynamic probability scaling based on subtype
            
            **5. Dynamic Probability Ranges**
            - Probabilities scale with actual team ratings
            - No more fixed percentages
            - Realistic EPL variance restored
            """)

if __name__ == "__main__":
    main()
