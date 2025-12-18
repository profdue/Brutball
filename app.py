# app.py - NARRATIVE PREDICTION ENGINE v2.3 FINAL
# ✅ ALL LOGIC FIXES APPLIED - NO HARDCODING, NO DATA MANIPULATION
# ✅ Uses CSV data EXACTLY as provided

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import io
import base64
import sys
from io import StringIO

# ==============================================
# FINAL CORRECTED PREDICTION ENGINE v2.3
# ==============================================

class FinalPredictionEngine:
    """Engine with all v2.3 logic fixes - NO hardcoding, NO data manipulation"""
    
    def __init__(self):
        # Manager database - only used for reference, NOT for overriding CSV data
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
        
        self.narratives = {
            "SIEGE": {
                "description": "Attack vs Defense - Dominant attacker vs organized defense",
                "flow": "• Attacker dominates possession (60%+) from start\n• Defender parks bus in organized low block\n• Frustration builds as chances are missed\n• Breakthrough often comes 45-70 mins (not early)\n• Clean sheet OR counter-attack consolation goal",
                "primary_markets": ["Under 2.5 goals", "Favorite to win", "BTTS: No", "First goal 45-70 mins", "Fewer than 10 corners total"],
                "color": "#2196F3"
            },
            "SHOOTOUT": {
                "description": "End-to-End Chaos - Both teams attack, weak defenses",
                "flow": "• Fast start from both teams (0-10 mins high intensity)\n• Early goals probable (first 25 mins)\n• Lead changes possible throughout match\n• End-to-end action with both teams committing forward\n• Late drama very likely (goals after 75 mins)",
                "primary_markets": ["Over 2.5 goals", "BTTS: Yes", "Both teams to score & Over 2.5", "Late goal after 75:00", "Lead changes in match"],
                "color": "#FF5722"
            },
            "CONTROLLED_EDGE": {
                "description": "Grinding Advantage - Favorite edges cautious game",
                "flow": "• Cautious start from both sides\n• Favorite gradually establishes control\n• Breakthrough likely 30-60 mins\n• Limited scoring chances overall\n• Narrow victory or draw",
                "primary_markets": ["Under 2.5 goals", "BTTS: No", "Favorite to win or draw", "First goal 30-60 mins", "Few corners total"],
                "color": "#FF9800",
                "subtypes": {
                    "HIGH_QUALITY": {"description": "High Quality Grind", "color": "#FF9800"},
                    "LOW_TEMPO": {"description": "Low Tempo Grind", "color": "#795548"},
                    "STANDARD": {"description": "Standard Grind", "color": "#FF9800"}
                }
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
                "color": "#4CAF50"
            }
        }
        
        self.hybrid_narratives = {
            "EDGE-CHAOS": {
                "description": "Tight but Explosive - Controlled game that could erupt",
                "parent_narratives": ["CONTROLLED_EDGE", "SHOOTOUT"],
                "color": "#FF9800",
                "secondary_color": "#FF5722",
                "hybrid_markets": [
                    "Over 2.25 goals (Asian)",
                    "BTTS: Lean Yes", 
                    "Both teams 3+ shots on target",
                    "Game to have 15+ total shots",
                    "Late goal after 70' possible"
                ],
                "flow": "• Cautious start but high attacking quality present\n• Game could remain tight or explode based on early chances\n• Both teams capable of scoring if opportunities arise\n• Higher variance than pure CONTROLLED_EDGE"
            }
        }
    
    # ========== CORE LOGIC METHODS ==========
    
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
    
    def detect_siege(self, match_data, debug=False):
        """SIEGE detection - uses CSV data exactly as provided"""
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        # Determine attacker and defender based on who is favorite
        if prob["favorite_is_home"]:
            attacker_attack = match_data["home_attack_rating"]
            defender_defense = match_data["away_defense_rating"]
            defender_pragmatic = match_data["away_pragmatic_rating"]
        else:
            attacker_attack = match_data["away_attack_rating"]
            defender_defense = match_data["home_defense_rating"]
            defender_pragmatic = match_data["home_pragmatic_rating"]
        
        siege_conditions = [
            attacker_attack >= 8,
            defender_defense >= 8,
            defender_pragmatic >= 7,
            prob["favorite_probability"] >= 60
        ]
        
        if debug:
            print(f"\n[DEBUG] SIEGE Detection:")
            print(f"  Favorite is home: {prob['favorite_is_home']}")
            print(f"  Attacker attack: {attacker_attack} ≥ 8? {attacker_attack >= 8}")
            print(f"  Defender defense: {defender_defense} ≥ 8? {defender_defense >= 8}")
            print(f"  Defender pragmatic: {defender_pragmatic} ≥ 7? {defender_pragmatic >= 7}")
            print(f"  Favorite probability: {prob['favorite_probability']:.1f}% ≥ 60%? {prob['favorite_probability'] >= 60}")
            print(f"  SIEGE Detected: {all(siege_conditions)}")
        
        return all(siege_conditions)
    
    def subclassify_controlled_edge(self, match_data):
        """CONTROLLED_EDGE subtype classification"""
        avg_attack = (match_data["home_attack_rating"] + match_data["away_attack_rating"]) / 2
        avg_press = (match_data["home_press_rating"] + match_data["away_press_rating"]) / 2
        
        if avg_attack >= 7.5 and avg_press >= 7:
            return "HIGH_QUALITY"
        elif avg_attack <= 6 and avg_press <= 6:
            return "LOW_TEMPO"
        else:
            return "STANDARD"
    
    def check_hybrid_override(self, match_data):
        """Check conditions that force hybrid consideration"""
        conditions = []
        
        # HIGH_PRESS_HIGH_ATTACK
        if (match_data["home_press_rating"] >= 7 and 
            match_data["away_press_rating"] >= 7 and
            match_data["home_attack_rating"] >= 7 and 
            match_data["away_attack_rating"] >= 7):
            conditions.append("HIGH_PRESS_HIGH_ATTACK")
        
        # STYLE_CLASH
        press_diff = abs(match_data["home_press_rating"] - match_data["away_press_rating"])
        possession_diff = abs(match_data["home_possession_rating"] - match_data["away_possession_rating"])
        if press_diff >= 3 and possession_diff >= 3:
            conditions.append("STYLE_CLASH")
        
        # ATTACK_HEAVY
        if (match_data["home_attack_rating"] >= 8 and 
            match_data["away_attack_rating"] >= 8 and
            match_data["home_defense_rating"] <= 7 and 
            match_data["away_defense_rating"] <= 7):
            conditions.append("ATTACK_HEAVY")
        
        return conditions
    
    def is_shootout_suppressed(self, match_data):
        """Check if SHOOTOUT should be suppressed"""
        home_suppress = (match_data["home_defense_rating"] >= 8 and 
                         match_data["home_pragmatic_rating"] >= 7)
        away_suppress = (match_data["away_defense_rating"] >= 8 and 
                         match_data["away_pragmatic_rating"] >= 7)
        return home_suppress or away_suppress
    
    # ========== PROBABILITY CALCULATION ==========
    
    def calculate_base_probabilities(self, match_data):
        """Calculate base probabilities from ratings"""
        avg_attack = (match_data["home_attack_rating"] + match_data["away_attack_rating"]) / 20
        avg_defense = (match_data["home_defense_rating"] + match_data["away_defense_rating"]) / 20
        avg_press = (match_data["home_press_rating"] + match_data["away_press_rating"]) / 20
        
        base_xg = 2.5 + (avg_attack * 1.0)
        xg = base_xg * (1 + (avg_press * 0.05))
        
        base_btts = 50 + (avg_attack * 20)
        btts = base_btts * (1 - (avg_defense * 0.2))
        
        return {
            "base_xg": max(1.8, min(4.0, xg)),
            "base_btts": max(20, min(85, btts)),
            "avg_attack": avg_attack,
            "avg_defense": avg_defense,
            "avg_press": avg_press
        }
    
    def validate_probabilities(self, xg, btts, over25, narrative):
        """Ensure probability coherence"""
        
        if btts < 40 and over25 > 65:
            over25 = min(over25, 65)
            if narrative == "BLITZKRIEG":
                over25 = min(over25, 75)
        
        if xg > 3.5 and over25 < 70:
            over25 = max(over25, 70)
        
        if xg > 3.8 and over25 < 80:
            over25 = max(over25, 80)
        
        if narrative == "SIEGE":
            over25 = min(over25, 65)
            if btts < 30:
                over25 = min(over25, 55)
        
        if narrative == "CONTROLLED_EDGE":
            over25 = min(over25, 70)
        
        return max(25, min(90, over25))
    
    def calculate_narrative_probabilities(self, narrative, base_probs, ce_subtype=None):
        """Calculate probabilities for specific narrative"""
        
        if narrative == "SIEGE":
            xg = base_probs["base_xg"] * 0.8
            btts = base_probs["base_btts"] * 0.7
            base_over25 = 40 + (xg * 10)
            
        elif narrative == "SHOOTOUT":
            xg = base_probs["base_xg"] * 1.15
            btts = base_probs["base_btts"] * 1.2
            base_over25 = 60 + (xg * 8)
            
        elif narrative == "CONTROLLED_EDGE":
            if ce_subtype == "HIGH_QUALITY":
                xg = base_probs["base_xg"] * 0.95
                btts = base_probs["base_btts"] * 0.9
                base_over25 = 45 + (xg * 8)
            elif ce_subtype == "LOW_TEMPO":
                xg = base_probs["base_xg"] * 0.75
                btts = base_probs["base_btts"] * 0.7
                base_over25 = 35 + (xg * 8)
            else:
                xg = base_probs["base_xg"] * 0.85
                btts = base_probs["base_btts"] * 0.8
                base_over25 = 40 + (xg * 8)
                
        elif narrative == "BLITZKRIEG":
            xg = base_probs["base_xg"] * 1.1
            btts = base_probs["base_btts"] * 0.8
            base_over25 = 50 + (xg * 10)
            
        elif narrative == "EDGE-CHAOS":
            xg = base_probs["base_xg"] * 1.05
            btts = base_probs["base_btts"] * 1.0
            base_over25 = 50 + (xg * 10)
            
        else:
            xg = base_probs["base_xg"] * 0.7
            btts = base_probs["base_btts"] * 0.6
            base_over25 = 30 + (xg * 8)
        
        over25 = self.validate_probabilities(xg, btts, base_over25, narrative)
        
        return {
            "xg": max(1.8, min(4.0, round(xg, 1))),
            "btts": max(20, min(85, round(btts, 1))),
            "over25": round(over25, 1)
        }
    
    # ========== NARRATIVE SCORING ==========
    
    def calculate_all_scores(self, match_data):
        """Calculate all narrative scores"""
        scores = {
            "SIEGE": self.calculate_siege_score(match_data),
            "SHOOTOUT": self.calculate_shootout_score(match_data),
            "CONTROLLED_EDGE": self.calculate_controlled_edge_score(match_data),
            "CHESS_MATCH": self.calculate_chess_match_score(match_data),
            "BLITZKRIEG": self.calculate_blitzkrieg_score(match_data)
        }
        return scores
    
    def calculate_siege_score(self, match_data):
        """Calculate SIEGE score - FIXED to work for both home and away favorites"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        # CRITICAL FIX: This now correctly handles both home and away favorites
        if prob["favorite_is_home"]:
            # Favorite is home team
            if (match_data["home_attack_rating"] >= 8 and 
                match_data["away_defense_rating"] >= 8):
                score += 40
        else:
            # Favorite is away team
            if (match_data["away_attack_rating"] >= 8 and 
                match_data["home_defense_rating"] >= 8):
                score += 40
        
        # Defense/pragmatic check (applies to either team)
        if (match_data["home_pragmatic_rating"] >= 7 or 
            match_data["away_pragmatic_rating"] >= 7):
            score += 20
        
        # Favorite strength
        if prob["favorite_strength"] in ["STRONG", "ELITE"]:
            score += 10
        
        return min(100, score)
    
    def calculate_shootout_score(self, match_data):
        """Calculate SHOOTOUT score"""
        score = 0
        
        if (match_data["home_attack_rating"] >= 7 and 
            match_data["away_attack_rating"] >= 7):
            score += 30
        
        avg_defense = (match_data["home_defense_rating"] + match_data["away_defense_rating"]) / 2
        if avg_defense <= 6.5:
            score += 25
        
        if (match_data["home_press_rating"] >= 7 and 
            match_data["away_press_rating"] >= 7):
            score += 20
        
        if match_data["last_h2h_goals"] >= 3:
            score += 15
        
        if match_data["last_h2h_btts"] == "Yes":
            score += 10
        
        return min(100, score)
    
    def calculate_controlled_edge_score(self, match_data):
        """Calculate CONTROLLED_EDGE score"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if 55 <= prob["favorite_probability"] < 65:
            score += 25
        
        attack_diff = abs(match_data["home_attack_rating"] - match_data["away_attack_rating"])
        defense_diff = abs(match_data["home_defense_rating"] - match_data["away_defense_rating"])
        if attack_diff <= 2 and defense_diff <= 2:
            score += 20
        
        if (6 <= match_data["home_defense_rating"] <= 8 and 
            6 <= match_data["away_defense_rating"] <= 8):
            score += 15
        
        if (match_data["home_pragmatic_rating"] >= 5 and 
            match_data["away_pragmatic_rating"] >= 5):
            score += 15
        
        position_gap = abs(match_data["home_position"] - match_data["away_position"])
        if position_gap <= 3:
            score += 10
        
        return min(100, score)
    
    def calculate_chess_match_score(self, match_data):
        """Calculate CHESS MATCH score"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        if prob["favorite_probability"] < 52:
            score += 25
        
        if (match_data["home_pragmatic_rating"] >= 7 and 
            match_data["away_pragmatic_rating"] >= 7):
            score += 25
        
        if (match_data["home_defense_rating"] >= 8 and 
            match_data["away_defense_rating"] >= 8):
            score += 20
        
        if (match_data["home_attack_rating"] <= 6 and 
            match_data["away_attack_rating"] <= 6):
            score += 15
        
        return min(100, score)
    
    def calculate_blitzkrieg_score(self, match_data):
        """Calculate BLITZKRIEG score"""
        score = 0
        
        prob = self.calculate_favorite_probability(match_data["home_odds"], match_data["away_odds"])
        
        if prob["favorite_strength"] == "ELITE":
            score += 40
        
        if prob["favorite_is_home"]:
            if (match_data["home_attack_rating"] - match_data["away_defense_rating"]) >= 3:
                score += 30
        else:
            if (match_data["away_attack_rating"] - match_data["home_defense_rating"]) >= 3:
                score += 30
        
        return min(100, score)
    
    # ========== MAIN PREDICTION LOGIC ==========
    
    def predict_match(self, match_data, debug=False):
        """Main prediction with all logic fixes"""
        
        if debug:
            print(f"\n{'='*60}")
            print(f"PREDICTION START: {match_data['home_team']} vs {match_data['away_team']}")
            print(f"{'='*60}")
        
        # Step 1: Apply ground truth rules
        siege_detected = self.detect_siege(match_data, debug=debug)
        shootout_suppressed = self.is_shootout_suppressed(match_data)
        hybrid_conditions = self.check_hybrid_override(match_data)
        ce_subtype = self.subclassify_controlled_edge(match_data)
        
        if debug:
            print(f"\n[DEBUG] Ground Truth Rules:")
            print(f"  SIEGE Detected: {siege_detected}")
            print(f"  SHOOTOUT Suppressed: {shootout_suppressed}")
            print(f"  Hybrid Conditions: {hybrid_conditions}")
            print(f"  CONTROLLED_EDGE Subtype: {ce_subtype}")
        
        # Step 2: Calculate base scores
        scores = self.calculate_all_scores(match_data)
        
        if debug:
            print(f"\n[DEBUG] Base Scores:")
            for narrative, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {narrative}: {score:.1f}")
        
        # Step 3: Apply suppression
        if shootout_suppressed:
            scores["SHOOTOUT"] *= 0.5
        
        # Step 4: Apply SIEGE priority (CRITICAL FIX)
        if siege_detected:
            scores["SIEGE"] = 100
            scores["BLITZKRIEG"] = 0
            scores["SHOOTOUT"] *= 0.3
            
            if debug:
                print(f"\n[DEBUG] SIEGE Priority Applied:")
                print(f"  SIEGE forced to 100, BLITZKRIEG set to 0")
        
        # Step 5: Determine narrative with correct priority
        force_hybrid = False
        hybrid_reason = ""
        
        if hybrid_conditions and not siege_detected:
            if ("HIGH_PRESS_HIGH_ATTACK" in hybrid_conditions or 
                "STYLE_CLASH" in hybrid_conditions):
                ce_score = scores["CONTROLLED_EDGE"]
                shootout_score = scores["SHOOTOUT"]
                if ce_score >= 50 and shootout_score >= 40:
                    force_hybrid = True
                    hybrid_reason = f"HYBRID_OVERRIDE: {hybrid_conditions}"
        
        # CORRECT PRIORITY HIERARCHY
        if siege_detected:
            dominant_narrative = "SIEGE"
            dominant_score = scores["SIEGE"]
            force_reason = "SIEGE_PRIORITY"
        elif force_hybrid:
            dominant_narrative = "EDGE-CHAOS"
            dominant_score = max(scores["CONTROLLED_EDGE"], scores["SHOOTOUT"])
            force_reason = hybrid_reason
        else:
            dominant_narrative = max(scores, key=scores.get)
            dominant_score = scores[dominant_narrative]
            force_reason = None
        
        # Step 6: Determine tier
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
        
        # Step 7: Calculate probabilities
        base_probs = self.calculate_base_probabilities(match_data)
        
        if dominant_narrative == "EDGE-CHAOS":
            ce_probs = self.calculate_narrative_probabilities("CONTROLLED_EDGE", base_probs, ce_subtype)
            shootout_probs = self.calculate_narrative_probabilities("SHOOTOUT", base_probs)
            
            xg = (ce_probs["xg"] * 0.6) + (shootout_probs["xg"] * 0.4)
            btts = (ce_probs["btts"] * 0.6) + (shootout_probs["btts"] * 0.4)
            over25 = (ce_probs["over25"] * 0.6) + (shootout_probs["over25"] * 0.4)
            
            narrative_info = self.hybrid_narratives["EDGE-CHAOS"]
            markets = narrative_info["hybrid_markets"]
            flow = narrative_info["flow"]
            description = narrative_info["description"]
        else:
            probs = self.calculate_narrative_probabilities(
                dominant_narrative, 
                base_probs, 
                ce_subtype if dominant_narrative == "CONTROLLED_EDGE" else None
            )
            
            xg = probs["xg"]
            btts = probs["btts"]
            over25 = probs["over25"]
            
            if dominant_narrative in self.narratives:
                narrative_info = self.narratives[dominant_narrative]
                markets = narrative_info["primary_markets"]
                flow = narrative_info["flow"]
                description = narrative_info["description"]
            else:
                markets = []
                flow = ""
                description = dominant_narrative
        
        # Final validation
        over25 = self.validate_probabilities(xg, btts, over25, dominant_narrative)
        
        # Step 8: Prepare result
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
        
        if dominant_narrative == "EDGE-CHAOS":
            result["secondary_color"] = self.hybrid_narratives["EDGE-CHAOS"]["secondary_color"]
            result["hybrid_parents"] = ["CONTROLLED_EDGE", "SHOOTOUT"]
        
        if dominant_narrative == "CONTROLLED_EDGE":
            result["ce_subtype"] = ce_subtype
            result["subtype_description"] = self.narratives["CONTROLLED_EDGE"]["subtypes"][ce_subtype]["description"]
            result["subtype_color"] = self.narratives["CONTROLLED_EDGE"]["subtypes"][ce_subtype]["color"]
        
        if debug:
            print(f"\n[DEBUG] Final Prediction: {dominant_narrative}")
            print(f"  Score: {dominant_score:.1f}/100")
            print(f"  Tier: {tier}")
            print(f"  Probabilities: xG={xg:.1f}, BTTS={btts:.1f}%, Over 2.5={over25:.1f}%")
            print(f"\n{'='*60}")
            print(f"PREDICTION COMPLETE")
            print(f"{'='*60}\n")
        
        return result

# ==============================================
# STREAMLIT APP - NO DATA MANIPULATION
# ==============================================

def main():
    st.set_page_config(
        page_title="Narrative Prediction Engine v2.3 - FINAL",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS
    st.markdown("""
    <style>
    .prediction-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid;
    }
    .subtype-badge {
        background-color: var(--subtype-color, #FF9800);
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 5px;
        display: inline-block;
    }
    .debug-log {
        background-color: #f5f5f5;
        border-left: 4px solid #6c757d;
        padding: 10px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
    }
    .score-bar {
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 5px 0 15px 0;
        overflow: hidden;
    }
    .stake-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 style="font-size: 2.8rem; color: #1E88E5; text-align: center; margin-bottom: 0.5rem;">⚽ NARRATIVE PREDICTION ENGINE v2.3</h1>', unsafe_allow_html=True)
    st.markdown("### **FINAL VERSION • NO DATA MANIPULATION • PURE LOGIC**")
    
    engine = FinalPredictionEngine()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        data_source = st.radio(
            "Data Source",
            ["Upload CSV", "Manual Input"],
            index=0
        )
        
        df = None
        
        if data_source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload CSV file", type="csv")
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} matches")
                    
                    # Show data integrity warning
                    st.info("**Note:** Using CSV data exactly as provided - no modifications")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Analysis settings
        st.markdown("### 🔧 Analysis Settings")
        
        debug_mode = st.checkbox("Enable Debug Mode", value=True)
        show_priority = st.checkbox("Show Priority Rules", value=True)
        
        # Navigation
        st.markdown("### 📋 Navigation")
        page = st.radio("Go to", ["Predictions", "Debug Console", "Data View"])
    
    # Data View Page
    if df is not None and page == "Data View":
        st.markdown("## 📊 CSV Data View")
        st.dataframe(df)
        return
    
    # Main content
    if df is not None:
        # Match selection
        st.markdown("### 🎯 Select Matches for Analysis")
        
        match_options = df.apply(
            lambda row: f"{row['home_team']} vs {row['away_team']} ({row['date']})", 
            axis=1
        ).tolist()
        
        selected_matches = st.multiselect(
            "Choose matches to analyze",
            match_options,
            default=match_options[:min(5, len(match_options))]
        )
        
        # Generate predictions
        if st.button("🚀 Run Prediction Engine", type="primary"):
            with st.spinner("Running predictions..."):
                predictions = []
                debug_logs = []
                
                for match_str in selected_matches:
                    match_idx = match_options.index(match_str)
                    match_row = df.iloc[match_idx]
                    
                    # Prepare match data - using CSV values exactly
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
                    
                    # Capture debug output
                    old_stdout = sys.stdout
                    sys.stdout = StringIO()
                    
                    prediction = engine.predict_match(match_data, debug=debug_mode)
                    
                    debug_output = sys.stdout.getvalue()
                    sys.stdout = old_stdout
                    
                    predictions.append(prediction)
                    debug_logs.append({
                        "match": prediction["match"],
                        "debug": debug_output
                    })
                
                st.session_state.predictions = predictions
                st.session_state.debug_logs = debug_logs
                st.success(f"✅ Generated {len(predictions)} predictions")
    
    # Display predictions
    if "predictions" in st.session_state and page == "Predictions":
        predictions = st.session_state.predictions
        
        # Results summary
        st.markdown("### 📈 Results Summary")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            siege_count = sum(1 for p in predictions if p["dominant_narrative"] == "SIEGE")
            st.metric("⚔️ SIEGE", siege_count)
        
        with col_s2:
            hybrid_count = sum(1 for p in predictions if p["dominant_narrative"] == "EDGE-CHAOS")
            st.metric("🔄 EDGE-CHAOS", hybrid_count)
        
        with col_s3:
            blitz_count = sum(1 for p in predictions if p["dominant_narrative"] == "BLITZKRIEG")
            st.metric("⚡ BLITZKRIEG", blitz_count)
        
        with col_s4:
            edge_count = sum(1 for p in predictions if p["dominant_narrative"] == "CONTROLLED_EDGE")
            st.metric("🎯 CONTROLLED_EDGE", edge_count)
        
        # Individual predictions
        for pred in predictions:
            # Card styling
            if pred["dominant_narrative"] == "CONTROLLED_EDGE" and "subtype_color" in pred:
                border_color = pred["subtype_color"]
            else:
                border_color = pred["narrative_color"]
            
            st.markdown(f'<div class="prediction-card" style="border-left: 5px solid {border_color};">', unsafe_allow_html=True)
            
            # Header
            col_h1, col_h2 = st.columns([3, 1])
            
            with col_h1:
                st.markdown(f"### {pred['match']}")
                st.markdown(f"**Date:** {pred['date']} | **Tier:** {pred['tier']}")
                
                # Narrative display
                if pred["dominant_narrative"] == "EDGE-CHAOS":
                    st.markdown(f'<div style="background: linear-gradient(90deg, {pred["narrative_color"]}, {pred.get("secondary_color", "#FF5722")}); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 10px 0;">'
                              f'<strong>{pred["dominant_narrative"]}</strong>'
                              f'</div>', unsafe_allow_html=True)
                    
                    if pred.get("hybrid_parents"):
                        st.markdown(f"**Hybrid Parents:** {pred['hybrid_parents'][0]} + {pred['hybrid_parents'][1]}")
                
                elif pred["dominant_narrative"] == "CONTROLLED_EDGE" and "ce_subtype" in pred:
                    subtype_color = pred.get("subtype_color", "#FF9800")
                    st.markdown(f'<div style="background-color: {pred["narrative_color"]}20; padding: 8px 16px; border-radius: 20px; border: 2px solid {pred["narrative_color"]}; display: inline-block; margin: 10px 0;">'
                              f'<strong style="color: {pred["narrative_color"]};">{pred["dominant_narrative"]}</strong>'
                              f'</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="subtype-badge" style="--subtype-color: {subtype_color};">{pred["ce_subtype"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"*{pred.get('subtype_description', '')}*")
                
                else:
                    st.markdown(f'<div style="background-color: {pred["narrative_color"]}20; padding: 8px 16px; border-radius: 20px; border: 2px solid {pred["narrative_color"]}; display: inline-block; margin: 10px 0;">'
                              f'<strong style="color: {pred["narrative_color"]};">{pred["dominant_narrative"]}</strong>'
                              f'</div>', unsafe_allow_html=True)
            
            with col_h2:
                st.markdown(f"**Score:** {pred['dominant_score']:.1f}/100")
                st.markdown(f"**Confidence:** {pred['confidence']}")
                st.markdown(f'<div class="stake-badge">{pred["stake_recommendation"]}</div>', unsafe_allow_html=True)
            
            # Priority indicators
            if show_priority:
                flags = pred["ground_truth_flags"]
                if any([flags["siege_detected"], flags["shootout_suppressed"], flags["hybrid_conditions"]]):
                    st.markdown("#### 🎯 Priority Rules Applied")
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    
                    with col_p1:
                        if flags["siege_detected"]:
                            st.markdown('<div style="background: #2196F3; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; margin: 2px;">⚔️ SIEGE PRIORITY</div>', unsafe_allow_html=True)
                    
                    with col_p2:
                        if flags["shootout_suppressed"]:
                            st.markdown('<div style="background: #FF5722; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; margin: 2px;">🛡️ SHOOTOUT SUPPRESSED</div>', unsafe_allow_html=True)
                    
                    with col_p3:
                        if flags["hybrid_conditions"]:
                            st.markdown('<div style="background: #FF9800; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; margin: 2px;">🔄 HYBRID FORCED</div>', unsafe_allow_html=True)
            
            # Main content
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                # Narrative scores
                st.markdown("#### 📊 Narrative Scores")
                
                for narrative, score in pred["scores"].items():
                    color = engine.narratives.get(narrative, {}).get("color", "#6c757d")
                    
                    if narrative == "SHOOTOUT" and pred["ground_truth_flags"]["shootout_suppressed"]:
                        label = f"🛡️ {narrative}"
                        score_display = f"{score:.1f} (suppressed)"
                    elif narrative == "SIEGE" and pred["ground_truth_flags"]["siege_detected"]:
                        label = f"⚔️ {narrative}"
                        score_display = f"{score:.1f} (priority)"
                    else:
                        label = narrative
                        score_display = f"{score:.1f}"
                    
                    st.markdown(f"**{label}:** {score_display}")
                    st.markdown(f'<div class="score-bar"><div style="width: {score}%; height: 100%; background-color: {color}; border-radius: 10px;"></div></div>', unsafe_allow_html=True)
                
                # Probability matrix
                st.markdown("#### 📈 Probability Matrix")
                
                col_pm1, col_pm2, col_pm3 = st.columns(3)
                
                with col_pm1:
                    st.markdown(f'<div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;"><strong>Expected Goals</strong><br><span style="font-size: 1.5rem;">{pred["expected_goals"]:.1f}</span></div>', unsafe_allow_html=True)
                
                with col_pm2:
                    st.markdown(f'<div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;"><strong>BTTS %</strong><br><span style="font-size: 1.5rem;">{pred["btts_probability"]}%</span></div>', unsafe_allow_html=True)
                
                with col_pm3:
                    st.markdown(f'<div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;"><strong>Over 2.5 %</strong><br><span style="font-size: 1.5rem;">{pred["over_25_probability"]}%</span></div>', unsafe_allow_html=True)
            
            with col_m2:
                # Insights
                st.markdown("#### 💡 Insights")
                st.info(pred["description"])
                
                # Betting markets
                st.markdown("#### 💰 Recommended Markets")
                for market in pred["betting_markets"]:
                    st.markdown(f"• {market}")
                
                # Ground truth explanation
                with st.expander("🔍 Ground Truth Analysis", expanded=False):
                    flags = pred["ground_truth_flags"]
                    
                    if flags["siege_detected"]:
                        st.markdown("**⚔️ SIEGE DETECTED (Priority Rule)**")
                        st.markdown("Conditions met:")
                        st.markdown("- Attacker attack ≥ 8")
                        st.markdown("- Defender defense ≥ 8")  
                        st.markdown("- Defender pragmatic ≥ 7")
                        st.markdown("- Favorite probability ≥ 60%")
                    
                    if flags["shootout_suppressed"]:
                        st.markdown("**🛡️ SHOOTOUT SUPPRESSED**")
                        st.markdown("Defense ≥ 8 AND Pragmatic ≥ 7 detected")
                    
                    if flags["hybrid_conditions"]:
                        st.markdown("**🔄 HYBRID CONDITIONS**")
                        st.markdown(f"Triggers: {', '.join(flags['hybrid_conditions'])}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Overall analysis
        if len(predictions) > 1:
            st.markdown("### 📊 Overall Analysis")
            
            narrative_counts = {}
            for pred in predictions:
                narrative = pred["dominant_narrative"]
                if narrative == "CONTROLLED_EDGE" and "ce_subtype" in pred:
                    narrative = f"CONTROLLED_EDGE ({pred['ce_subtype']})"
                narrative_counts[narrative] = narrative_counts.get(narrative, 0) + 1
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(narrative_counts.keys()),
                    values=list(narrative_counts.values()),
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title="Narrative Distribution",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif page == "Debug Console" and "debug_logs" in st.session_state:
        st.markdown("## 🐞 Debug Console")
        
        for debug_log in st.session_state.debug_logs:
            with st.expander(f"Debug Output: {debug_log['match']}", expanded=True):
                st.markdown('<div class="debug-log">', unsafe_allow_html=True)
                st.text(debug_log["debug"])
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Initial state
        st.info("👈 **Upload a CSV file to get started**")
        
        with st.expander("ℹ️ About This Version", expanded=True):
            st.markdown("""
            ### ✅ **NO DATA MANIPULATION VERSION**
            
            **Key Principles:**
            1. **Uses CSV data EXACTLY as provided** - no changes to team names, managers, or ratings
            2. **NO hardcoding** of any team-specific logic
            3. **Pure logic engine** that works with any valid CSV data
            4. **All fixes applied** to the logic only
            
            ### 🔧 **Logic Fixes Applied:**
            
            1. **SIEGE Priority Bug Fixed:**
               - SIEGE now has absolute priority when detected
               - BLITZKRIEG cannot override SIEGE
            
            2. **SIEGE Score Calculation Fixed:**
               - Now correctly handles both home and away favorites
               - Uses CSV values exactly as provided
            
            3. **Probability Coherence:**
               - BTTS and Over 2.5 probabilities are logically consistent
            
            4. **Subtype Display:**
               - CONTROLLED_EDGE shows appropriate subtypes
            
            ### 📋 **How to Use:**
            1. Upload your CSV file
            2. Select matches to analyze
            3. Run the prediction engine
            4. View results based on your actual CSV data
            """)

if __name__ == "__main__":
    main()
