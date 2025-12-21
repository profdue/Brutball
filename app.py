import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import requests
from datetime import datetime

# ============================================================================
# PROFESSIONAL'S DECISION-MAKING FRAMEWORK (LAYER 1)
# ============================================================================

class ProfessionalDecisionFramework:
    """
    Layer 1: Situation Classification
    Answers: "What kind of match is this?"
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all tracking variables"""
        self.crisis_flags = []
        self.reality_gaps = []
        self.tactical_edges = []
        self.decision_log = []
        self.archetype = None
    
    def crisis_scan(self, home_data, away_data):
        """
        STEP 1: Check if either team is structurally broken
        """
        crisis_flags = []
        
        # Check defenders_out >= 3 → RED FLAG
        if home_data.get('defenders_out', 0) >= 3:
            crisis_flags.append(f"🚨 HOME CRISIS: {home_data.get('defenders_out', 0)} defenders out")
        if away_data.get('defenders_out', 0) >= 3:
            crisis_flags.append(f"🚨 AWAY CRISIS: {away_data.get('defenders_out', 0)} defenders out")
        
        # Check goals_conceded_last_5 > 12 → RED FLAG
        if home_data.get('goals_conceded_last_5', 0) > 12:
            crisis_flags.append(f"🚨 HOME DEFENSIVE CRISIS: {home_data.get('goals_conceded_last_5', 0)} goals conceded in last 5")
        if away_data.get('goals_conceded_last_5', 0) > 12:
            crisis_flags.append(f"🚨 AWAY DEFENSIVE CRISIS: {away_data.get('goals_conceded_last_5', 0)} goals conceded in last 5")
        
        # Check form ending in 'LL' or 'LLL' → RED FLAG
        home_form = str(home_data.get('form_last_5_overall', '')).strip()
        away_form = str(away_data.get('form_last_5_overall', '')).strip()
        
        if home_form.endswith('LL') or home_form.endswith('LLL'):
            crisis_flags.append(f"🚨 HOME FORM CRISIS: Recent form {home_form}")
        if away_form.endswith('LL') or away_form.endswith('LLL'):
            crisis_flags.append(f"🚨 AWAY FORM CRISIS: Recent form {away_form}")
        
        self.crisis_flags = crisis_flags
        
        # Determine if this is a "Crisis Game"
        home_in_crisis = any("HOME" in flag for flag in crisis_flags)
        away_in_crisis = any("AWAY" in flag for flag in crisis_flags)
        
        return {
            'home_crisis': home_in_crisis,
            'away_crisis': away_in_crisis,
            'any_crisis': len(crisis_flags) > 0,
            'crisis_count': len(crisis_flags),
            'flags': crisis_flags
        }
    
    def reality_check(self, home_data, away_data):
        """
        STEP 2: Check if results are telling the truth
        """
        reality_gaps = []
        
        # Calculate home reality gap
        home_xg = home_data.get('home_xg_for', 0)
        home_goals = home_data.get('home_goals_scored', 0)
        home_gap = home_goals - home_xg
        
        if abs(home_gap) > 3:
            if home_gap > 0:
                reality_gaps.append(f"📈 HOME OVERPERFORMING: Scored {home_gap:.1f} more goals than xG suggests")
            else:
                reality_gaps.append(f"📉 HOME UNDERPERFORMING: Scored {abs(home_gap):.1f} fewer goals than xG suggests")
        
        # Calculate away reality gap
        away_xg = away_data.get('away_xg_for', 0)
        away_goals = away_data.get('away_goals_scored', 0)
        away_gap = away_goals - away_xg
        
        if abs(away_gap) > 3:
            if away_gap > 0:
                reality_gaps.append(f"📈 AWAY OVERPERFORMING: Scored {away_gap:.1f} more goals than xG suggests")
            else:
                reality_gaps.append(f"📉 AWAY UNDERPERFORMING: Scored {abs(away_gap):.1f} fewer goals than xG suggests")
        
        self.reality_gaps = reality_gaps
        
        # Determine market mispricing opportunities
        home_overperforming = home_gap > 3
        home_underperforming = home_gap < -3
        away_overperforming = away_gap > 3
        away_underperforming = away_gap < -3
        
        return {
            'home_gap': home_gap,
            'away_gap': away_gap,
            'home_overperforming': home_overperforming,
            'home_underperforming': home_underperforming,
            'away_overperforming': away_overperforming,
            'away_underperforming': away_underperforming,
            'gaps': reality_gaps
        }
    
    def tactical_edge(self, home_data, away_data, crisis_context):
        """
        STEP 3: Find whose strength hits whose weakness
        """
        tactical_edges = []
        
        # Only analyze tactical edges if no crisis
        if crisis_context['any_crisis']:
            tactical_edges.append("⚠️ Crisis detected - tactical analysis limited")
            self.tactical_edges = tactical_edges
            return {'edges': tactical_edges, 'has_edge': False}
        
        # Check counter-attack matchup
        home_counter_ratio = home_data.get('home_goals_counter_for', 0) / max(home_data.get('home_goals_scored', 1), 1)
        away_counter_vuln = away_data.get('away_goals_counter_against', 0) / max(away_data.get('goals_conceded', 1), 1)
        
        if home_counter_ratio > 0.2 and away_counter_vuln > 0.2:
            tactical_edges.append(f"⚡ COUNTER-ATTACK EDGE: Home scores {home_counter_ratio:.0%} from counters, Away concedes {away_counter_vuln:.0%} from counters")
        
        # Check set-piece matchup
        home_setpiece_ratio = home_data.get('home_goals_setpiece_for', 0) / max(home_data.get('home_goals_scored', 1), 1)
        away_setpiece_vuln = away_data.get('away_goals_setpiece_against', 0) / max(away_data.get('goals_conceded', 1), 1)
        
        if home_setpiece_ratio > 0.25 and away_setpiece_vuln > 0.3:
            tactical_edges.append(f"🎯 SET-PIECE EDGE: Home scores {home_setpiece_ratio:.0%} from set-pieces, Away concedes {away_setpiece_vuln:.0%} from set-pieces")
        
        self.tactical_edges = tactical_edges
        
        return {
            'edges': tactical_edges,
            'has_edge': len(tactical_edges) > 0,
            'counter_matchup': home_counter_ratio > 0.2 and away_counter_vuln > 0.2,
            'setpiece_matchup': home_setpiece_ratio > 0.25 and away_setpiece_vuln > 0.3
        }
    
    def classify_archetype(self, crisis_context, reality_context, tactical_context):
        """
        STEP 4: Classify match into one of five archetypes
        """
        # Extract key conditions
        home_crisis = crisis_context['home_crisis']
        away_crisis = crisis_context['away_crisis']
        any_crisis = crisis_context['any_crisis']
        
        home_over = reality_context['home_overperforming']
        home_under = reality_context['home_underperforming']
        away_over = reality_context['away_overperforming']
        away_under = reality_context['away_underperforming']
        
        # DECISION MATRIX
        # 1. FADE THE FAVORITE: Favorite in crisis AND overperforming
        if home_crisis and home_over:
            archetype = "FADE THE FAVORITE"
            explanation = "Home favorite in crisis AND overperforming → Bet against"
        elif away_crisis and away_over:
            archetype = "FADE THE FAVORITE"
            explanation = "Away favorite in crisis AND overperforming → Bet against"
        
        # 2. BACK THE UNDERDOG: Underdog stable AND underperforming
        elif (not home_crisis) and home_under and away_over:
            archetype = "BACK THE UNDERDOG"
            explanation = "Home stable AND underperforming, Away overperforming → Back Home"
        elif (not away_crisis) and away_under and home_over:
            archetype = "BACK THE UNDERDOG"
            explanation = "Away stable AND underperforming, Home overperforming → Back Away"
        
        # 3. GOALS GALORE: Both defenses shaky (crisis both sides)
        elif home_crisis and away_crisis:
            archetype = "GOALS GALORE"
            explanation = "Both teams in defensive crisis → High-scoring game likely"
        
        # 4. DEFENSIVE GRIND: Both defenses solid, both attacks poor
        elif (not any_crisis) and home_under and away_under:
            archetype = "DEFENSIVE GRIND"
            explanation = "Both teams solid defensively AND underperforming offensively → Low-scoring game"
        
        # 5. AVOID: Mixed signals or no clear edge
        else:
            archetype = "AVOID"
            explanation = "Mixed signals or no clear edge → No bet"
        
        self.archetype = archetype
        
        # Log the decision logic
        self.decision_log.append(f"CLASSIFIED: {archetype}")
        self.decision_log.append(f"REASON: {explanation}")
        
        return {
            'archetype': archetype,
            'explanation': explanation,
            'layer1_complete': True
        }
    
    def analyze_match(self, home_data, away_data):
        """
        Complete Layer 1 analysis
        Returns: Dict with situation classification
        """
        self.reset()
        
        # STEP 1: Crisis Scan
        crisis_context = self.crisis_scan(home_data, away_data)
        
        # STEP 2: Reality Check
        reality_context = self.reality_check(home_data, away_data)
        
        # STEP 3: Tactical Edge
        tactical_context = self.tactical_edge(home_data, away_data, crisis_context)
        
        # STEP 4: Archetype Classification
        classification = self.classify_archetype(crisis_context, reality_context, tactical_context)
        
        # Compile Layer 1 analysis
        analysis = {
            'layer': 1,
            'crisis_analysis': crisis_context,
            'reality_analysis': reality_context,
            'tactical_analysis': tactical_context,
            'classification': classification,
            'decision_log': self.decision_log
        }
        
        return analysis

# ============================================================================
# DECISION FIREWALL: MARKET VALIDATION LAYER (LAYER 2)
# ============================================================================

class DecisionFirewall:
    """
    Layer 2: Market Eligibility & Safety Check
    Answers: "Is this market safe enough to expose capital?"
    
    Philosophy: Default state is REJECT unless ALL gates pass
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset validator tracking"""
        self.validation_results = {}
        self.rejected_markets = {}
        self.validation_log = []
        self.final_decisions = []
    
    def _log_validation(self, market, passed, gates_passed, gates_failed, message):
        """Log validation results"""
        self.validation_log.append({
            'market': market,
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'message': message
        })
        
        if not passed:
            self.rejected_markets[market] = {
                'gates_passed': gates_passed,
                'gates_failed': gates_failed,
                'message': message
            }
    
    # ==================== MARKET VALIDATORS ====================
    
    def validate_match_winner(self, team_to_back, opponent, layer1_context, home_data, away_data):
        """
        MATCH WINNER VALIDATOR (1X2)
        ALL gates must pass:
        1. Context Gate: Backed team has no crisis, opponent has ≥1 red flag
        2. Reality Gate: Backed team underperforming xG, opponent overperforming
        3. Tactical Gate: Clear style advantage
        """
        gates_passed = []
        gates_failed = []
        
        # Determine which team is which
        if team_to_back == 'home':
            backed_data = home_data
            opp_data = away_data
            backed_crisis = layer1_context['crisis_analysis']['home_crisis']
            opp_crisis = layer1_context['crisis_analysis']['away_crisis']
            backed_gap = layer1_context['reality_analysis']['home_gap']
            opp_gap = layer1_context['reality_analysis']['away_gap']
        else:
            backed_data = away_data
            opp_data = home_data
            backed_crisis = layer1_context['crisis_analysis']['away_crisis']
            opp_crisis = layer1_context['crisis_analysis']['home_crisis']
            backed_gap = layer1_context['reality_analysis']['away_gap']
            opp_gap = layer1_context['reality_analysis']['home_gap']
        
        # GATE 1: Context
        if not backed_crisis and opp_crisis:
            gates_passed.append("Context: Backed team stable, opponent in crisis")
        else:
            gates_failed.append(f"Context: Backed crisis={backed_crisis}, Opponent crisis={opp_crisis}")
        
        # GATE 2: Reality
        if backed_gap < -3 and opp_gap > 3:
            gates_passed.append(f"Reality: Backed underperforming ({backed_gap:.1f}), opponent overperforming ({opp_gap:.1f})")
        else:
            gates_failed.append(f"Reality: Backed gap={backed_gap:.1f}, Opponent gap={opp_gap:.1f}")
        
        # GATE 3: Tactical
        tactical_edge = layer1_context['tactical_analysis']['has_edge']
        if tactical_edge:
            edges = layer1_context['tactical_analysis']['edges']
            tactical_reason = edges[0] if edges else "Clear tactical edge"
            gates_passed.append(f"Tactical: {tactical_reason}")
        else:
            gates_failed.append("Tactical: No clear style advantage")
        
        # FINAL DECISION: ALL gates must pass
        passed = len(gates_failed) == 0
        
        message = f"Match Winner ({team_to_back.upper()}): {'✅ ALL gates passed' if passed else '❌ Failed gates: ' + ', '.join([g.split(':')[0] for g in gates_failed])}"
        
        self._log_validation(f"MATCH WINNER - {team_to_back.upper()}", passed, gates_passed, gates_failed, message)
        
        return {
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'recommendation': f"{team_to_back.upper()} to win" if passed else None,
            'confidence': 'High' if passed and len(gates_passed) >= 3 else 'None'
        }
    
    def validate_over_25(self, home_data, away_data, layer1_context):
        """
        OVER 2.5 GOALS VALIDATOR
        At least 2 of 3 gates must pass:
        1. Defensive Instability: One team in crisis OR combined conceded ≥10
        2. Chance Creation: Combined xG strong
        3. Game Shape: Open tactical interaction
        """
        gates_passed = []
        gates_failed = []
        
        # GATE 1: Defensive Instability
        home_crisis = layer1_context['crisis_analysis']['home_crisis']
        away_crisis = layer1_context['crisis_analysis']['away_crisis']
        home_conceded = home_data.get('goals_conceded_last_5', 0)
        away_conceded = away_data.get('goals_conceded_last_5', 0)
        combined_conceded = home_conceded + away_conceded
        
        defensive_instability = (home_crisis or away_crisis or combined_conceded >= 10)
        
        if defensive_instability:
            reason = []
            if home_crisis:
                reason.append("Home crisis")
            if away_crisis:
                reason.append("Away crisis")
            if combined_conceded >= 10:
                reason.append(f"Combined conceded={combined_conceded}")
            gates_passed.append(f"Defensive Instability: {' + '.join(reason)}")
        else:
            gates_failed.append(f"Defensive Instability: Home crisis={home_crisis}, Away crisis={away_crisis}, Combined conceded={combined_conceded}")
        
        # GATE 2: Chance Creation
        home_xg = home_data.get('home_xg_for', 0)
        away_xg = away_data.get('away_xg_for', 0)
        combined_xg = home_xg + away_xg
        
        # Strong chance creation: combined xG > 25 (approx 1.25 per game per team)
        chance_creation = combined_xg > 25
        
        if chance_creation:
            gates_passed.append(f"Chance Creation: Combined xG={combined_xg:.1f} (strong)")
        else:
            gates_failed.append(f"Chance Creation: Combined xG={combined_xg:.1f} (modest)")
        
        # GATE 3: Game Shape
        tactical_edge = layer1_context['tactical_analysis']['has_edge']
        counter_matchup = layer1_context['tactical_analysis'].get('counter_matchup', False)
        open_interaction = tactical_edge or counter_matchup
        
        if open_interaction:
            gates_passed.append("Game Shape: Open tactical interaction likely")
        else:
            gates_failed.append("Game Shape: Styles may cancel or control")
        
        # FINAL DECISION: At least 2 of 3 gates must pass
        gates_passed_count = len(gates_passed)
        passed = gates_passed_count >= 2
        
        message = f"Over 2.5 Goals: {'✅' if passed else '❌'} {gates_passed_count}/3 gates passed"
        
        self._log_validation("OVER 2.5 GOALS", passed, gates_passed, gates_failed, message)
        
        return {
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'recommendation': "Over 2.5 goals" if passed else None,
            'confidence': 'High' if gates_passed_count == 3 else 'Medium' if gates_passed_count == 2 else 'None'
        }
    
    def validate_under_25(self, home_data, away_data, layer1_context):
        """
        UNDER 2.5 GOALS VALIDATOR
        ALL gates must pass:
        1. No defensive crisis
        2. No underperforming attack screaming regression
        3. Canceling styles
        4. Low emotional stakes (estimated)
        """
        gates_passed = []
        gates_failed = []
        
        # GATE 1: No defensive crisis
        home_crisis = layer1_context['crisis_analysis']['home_crisis']
        away_crisis = layer1_context['crisis_analysis']['away_crisis']
        
        if not home_crisis and not away_crisis:
            gates_passed.append("No defensive crisis")
        else:
            crisis_reason = []
            if home_crisis:
                crisis_reason.append("Home")
            if away_crisis:
                crisis_reason.append("Away")
            gates_failed.append(f"Defensive crisis: {' and '.join(crisis_reason)}")
        
        # GATE 2: No regression scream
        home_gap = layer1_context['reality_analysis']['home_gap']
        away_gap = layer1_context['reality_analysis']['away_gap']
        
        # Under 2.5 fails when a team is severely underperforming (screaming for goals)
        regression_scream = home_gap < -5 or away_gap < -5
        
        if not regression_scream:
            gates_passed.append(f"No regression scream (gaps: {home_gap:.1f}, {away_gap:.1f})")
        else:
            gates_failed.append(f"Regression scream: Home gap={home_gap:.1f}, Away gap={away_gap:.1f}")
        
        # GATE 3: Canceling styles (no tactical edge)
        tactical_edge = layer1_context['tactical_analysis']['has_edge']
        
        if not tactical_edge:
            gates_passed.append("Styles likely to cancel")
        else:
            gates_failed.append("Clear tactical edge (not canceling)")
        
        # GATE 4: Low emotional stakes (estimated from form and position context)
        # Simple heuristic: If both teams have similar recent form and no crisis
        home_form = str(home_data.get('form_last_5_overall', '')).strip()
        away_form = str(away_data.get('form_last_5_overall', '')).strip()
        
        # Check for extreme form (WWWWW or LLLLL indicates high stakes)
        home_form_extreme = home_form in ['WWWWW', 'LLLLL'] if len(home_form) == 5 else False
        away_form_extreme = away_form in ['WWWWW', 'LLLLL'] if len(away_form) == 5 else False
        
        low_emotional_stakes = not (home_form_extreme or away_form_extreme)
        
        if low_emotional_stakes:
            gates_passed.append("Low emotional stakes (no extreme form)")
        else:
            form_info = []
            if home_form_extreme:
                form_info.append(f"Home: {home_form}")
            if away_form_extreme:
                form_info.append(f"Away: {away_form}")
            gates_failed.append(f"High emotional stakes: {'; '.join(form_info)}")
        
        # FINAL DECISION: ALL gates must pass
        passed = len(gates_failed) == 0
        
        message = f"Under 2.5 Goals: {'✅ ALL gates passed' if passed else '❌ Failed gates: ' + ', '.join([g.split(':')[0] for g in gates_failed])}"
        
        self._log_validation("UNDER 2.5 GOALS", passed, gates_passed, gates_failed, message)
        
        return {
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'recommendation': "Under 2.5 goals" if passed else None,
            'confidence': 'High' if passed and len(gates_passed) >= 4 else 'None'
        }
    
    def validate_btts_yes(self, home_data, away_data, layer1_context):
        """
        BTTS YES VALIDATOR
        BOTH teams must pass:
        1. Psychologically alive (recent goals)
        2. Clear path to goal (tactical or defensive weakness)
        3. No domination scenario likely
        """
        gates_passed = []
        gates_failed = []
        
        # Team-level checks
        home_alive = home_data.get('goals_scored_last_5', 0) >= 3  # At least 3 goals in last 5
        away_alive = away_data.get('goals_scored_last_5', 0) >= 3
        
        # GATE 1: Both teams psychologically alive
        if home_alive and away_alive:
            gates_passed.append(f"Both alive: Home {home_data.get('goals_scored_last_5', 0)} goals, Away {away_data.get('goals_scored_last_5', 0)} goals in last 5")
        else:
            dead_teams = []
            if not home_alive:
                dead_teams.append(f"Home ({home_data.get('goals_scored_last_5', 0)} goals)")
            if not away_alive:
                dead_teams.append(f"Away ({away_data.get('goals_scored_last_5', 0)} goals)")
            gates_failed.append(f"Psychologically dead: {', '.join(dead_teams)}")
        
        # GATE 2: Both have path to goal
        home_crisis = layer1_context['crisis_analysis']['home_crisis']
        away_crisis = layer1_context['crisis_analysis']['away_crisis']
        
        # Path exists if opponent has defensive issues OR tactical matchup favors
        home_has_path = away_crisis or layer1_context['tactical_analysis'].get('counter_matchup', False) or layer1_context['tactical_analysis'].get('setpiece_matchup', False)
        away_has_path = home_crisis or layer1_context['tactical_analysis'].get('counter_matchup', False) or layer1_context['tactical_analysis'].get('setpiece_matchup', False)
        
        if home_has_path and away_has_path:
            paths = []
            if away_crisis:
                paths.append("Away defensive crisis")
            if home_crisis:
                paths.append("Home defensive crisis")
            if layer1_context['tactical_analysis'].get('counter_matchup', False):
                paths.append("Counter matchup")
            if layer1_context['tactical_analysis'].get('setpiece_matchup', False):
                paths.append("Set-piece matchup")
            gates_passed.append(f"Paths to goal: {'; '.join(paths)}")
        else:
            missing_paths = []
            if not home_has_path:
                missing_paths.append("Home")
            if not away_has_path:
                missing_paths.append("Away")
            gates_failed.append(f"No clear path for: {', '.join(missing_paths)}")
        
        # GATE 3: No domination scenario likely
        # Domination likely if one team is much stronger and other is in crisis
        home_gap = layer1_context['reality_analysis']['home_gap']
        away_gap = layer1_context['reality_analysis']['away_gap']
        
        domination_scenario = (home_gap > 3 and away_crisis) or (away_gap > 3 and home_crisis)
        
        if not domination_scenario:
            gates_passed.append("No clear domination scenario")
        else:
            if home_gap > 3 and away_crisis:
                gates_failed.append("Domination: Home overperforming + Away crisis")
            elif away_gap > 3 and home_crisis:
                gates_failed.append("Domination: Away overperforming + Home crisis")
        
        # FINAL DECISION: At least 2 of 3 gates must pass
        gates_passed_count = len(gates_passed)
        passed = gates_passed_count >= 2
        
        message = f"BTTS YES: {'✅' if passed else '❌'} {gates_passed_count}/3 gates passed"
        
        self._log_validation("BTTS YES", passed, gates_passed, gates_failed, message)
        
        return {
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'recommendation': "BTTS Yes" if passed else None,
            'confidence': 'High' if gates_passed_count == 3 else 'Medium' if gates_passed_count >= 2 else 'None'
        }
    
    def validate_btts_no(self, home_data, away_data, layer1_context):
        """
        BTTS NO VALIDATOR
        One team must fail at multiple layers:
        1. Low xG AND no underperformance
        2. No tactical route
        3. Likely to accept defeat or park bus
        """
        gates_passed = []
        gates_failed = []
        
        # Check which team might be neutralized
        home_xg = home_data.get('home_xg_for', 0)
        away_xg = away_data.get('away_xg_for', 0)
        home_gap = layer1_context['reality_analysis']['home_gap']
        away_gap = layer1_context['reality_analysis']['away_gap']
        
        # Identify potentially neutralized team (lower xG, not underperforming much)
        home_neutralized = home_xg < 15 and home_gap > -2  # Low creation, not unlucky
        away_neutralized = away_xg < 15 and away_gap > -2
        
        # GATE 1: One team has low xG and no underperformance
        if home_neutralized or away_neutralized:
            neutralized = []
            if home_neutralized:
                neutralized.append(f"Home (xG={home_xg:.1f}, gap={home_gap:.1f})")
            if away_neutralized:
                neutralized.append(f"Away (xG={away_xg:.1f}, gap={away_gap:.1f})")
            gates_passed.append(f"Neutralized team(s): {', '.join(neutralized)}")
        else:
            gates_failed.append(f"No clearly neutralized team: Home xG={home_xg:.1f}, gap={home_gap:.1f}; Away xG={away_xg:.1f}, gap={away_gap:.1f}")
        
        # GATE 2: No tactical route for neutralized team
        tactical_edge = layer1_context['tactical_analysis']['has_edge']
        
        # If there's a tactical edge, it might give the weak team a route
        if not tactical_edge:
            gates_passed.append("No tactical edge gives weak team a route")
        else:
            # Check if the tactical edge favors the weak team
            # Simple check: if weak team is home and has counter edge
            home_counter = home_data.get('home_goals_counter_for', 0) / max(home_data.get('home_goals_scored', 1), 1)
            away_counter_vuln = away_data.get('away_goals_counter_against', 0) / max(away_data.get('goals_conceded', 1), 1)
            
            weak_team_has_route = (home_neutralized and home_counter > 0.2 and away_counter_vuln > 0.2) or \
                                 (away_neutralized and layer1_context['tactical_analysis'].get('counter_matchup', False))
            
            if not weak_team_has_route:
                gates_passed.append("Weak team has no tactical route")
            else:
                gates_failed.append("Weak team has tactical route to goal")
        
        # GATE 3: Likely to accept defeat or park bus
        # Check form: teams on losing streaks more likely to park bus
        home_form = str(home_data.get('form_last_5_overall', '')).strip()
        away_form = str(away_data.get('form_last_5_overall', '')).strip()
        
        home_losing = home_form.endswith('L') or home_form.endswith('LL')
        away_losing = away_form.endswith('L') or away_form.endswith('LL')
        
        park_bus_likely = (home_neutralized and home_losing) or (away_neutralized and away_losing)
        
        if park_bus_likely:
            gates_passed.append("Weak team on poor form → likely to park bus")
        else:
            gates_failed.append("Weak team not in park-bus mentality")
        
        # FINAL DECISION: At least 2 of 3 gates must pass
        gates_passed_count = len(gates_passed)
        passed = gates_passed_count >= 2
        
        message = f"BTTS NO: {'✅' if passed else '❌'} {gates_passed_count}/3 gates passed"
        
        self._log_validation("BTTS NO", passed, gates_passed, gates_failed, message)
        
        return {
            'passed': passed,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'recommendation': "BTTS No" if passed else None,
            'confidence': 'High' if gates_passed_count == 3 else 'Medium' if gates_passed_count >= 2 else 'None'
        }
    
    # ==================== COMPLETE MARKET VALIDATION ====================
    
    def validate_all_markets(self, layer1_analysis, home_data, away_data, archetype):
        """
        Validate all markets based on Layer 1 analysis and archetype
        Returns only markets that pass ALL validation gates
        """
        self.reset()
        
        # Skip validation if archetype is AVOID
        if archetype == "AVOID":
            self.validation_log.append("Archetype is AVOID → No market validation performed")
            return {
                'passed_markets': [],
                'rejected_markets': self.rejected_markets,
                'validation_log': self.validation_log,
                'final_decisions': ["NO BET - Archetype: AVOID"]
            }
        
        validated_markets = []
        
        # Determine which markets to validate based on archetype
        markets_to_validate = []
        
        if archetype == "FADE THE FAVORITE":
            # Determine which team is the favorite (simplified: team NOT in crisis)
            if layer1_analysis['crisis_analysis']['home_crisis']:
                markets_to_validate.append(('match_winner', 'away'))  # Fade home, back away
            elif layer1_analysis['crisis_analysis']['away_crisis']:
                markets_to_validate.append(('match_winner', 'home'))  # Fade away, back home
            markets_to_validate.append('over_25')
            
        elif archetype == "BACK THE UNDERDOG":
            # Determine which team is the underdog (team underperforming)
            if layer1_analysis['reality_analysis']['home_underperforming']:
                markets_to_validate.append(('match_winner', 'home'))
            elif layer1_analysis['reality_analysis']['away_underperforming']:
                markets_to_validate.append(('match_winner', 'away'))
            markets_to_validate.append('btts_yes')
            
        elif archetype == "GOALS GALORE":
            markets_to_validate.extend(['over_25', 'btts_yes'])
            
        elif archetype == "DEFENSIVE GRIND":
            markets_to_validate.extend(['under_25', 'btts_no'])
        
        # Run validators for each market
        for market in markets_to_validate:
            if market == 'over_25':
                result = self.validate_over_25(home_data, away_data, layer1_analysis)
                if result['passed']:
                    validated_markets.append(result['recommendation'])
                    
            elif market == 'under_25':
                result = self.validate_under_25(home_data, away_data, layer1_analysis)
                if result['passed']:
                    validated_markets.append(result['recommendation'])
                    
            elif market == 'btts_yes':
                result = self.validate_btts_yes(home_data, away_data, layer1_analysis)
                if result['passed']:
                    validated_markets.append(result['recommendation'])
                    
            elif market == 'btts_no':
                result = self.validate_btts_no(home_data, away_data, layer1_analysis)
                if result['passed']:
                    validated_markets.append(result['recommendation'])
                    
            elif isinstance(market, tuple) and market[0] == 'match_winner':
                team = market[1]
                result = self.validate_match_winner(team, 'opponent', layer1_analysis, home_data, away_data)
                if result['passed']:
                    validated_markets.append(result['recommendation'])
        
        # Compile final decisions
        if not validated_markets:
            self.final_decisions.append("NO BET - No markets passed validation")
        else:
            self.final_decisions.extend(validated_markets)
        
        return {
            'passed_markets': validated_markets,
            'rejected_markets': self.rejected_markets,
            'validation_log': self.validation_log,
            'final_decisions': self.final_decisions,
            'archetype': archetype
        }

# ============================================================================
# DATA LOADING & PREPARATION
# ============================================================================

def load_league_data(league_name):
    """Load league data from GitHub with only necessary columns."""
    github_urls = {
        'LA LIGA': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/la_liga.csv',
        'PREMIER LEAGUE': 'https://raw.githubusercontent.com/profdue/Brutball/main/leagues/premier_league.csv'
    }
    
    url = github_urls.get(league_name.upper())
    if not url:
        st.error(f"League {league_name} not configured")
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Required columns
        required_columns = [
            'team',
            'defenders_out',
            'goals_conceded_last_5',
            'goals_scored_last_5',
            'form_last_5_overall',
            'form_last_5_home',
            'form_last_5_away',
            'home_xg_for', 'home_goals_scored',
            'away_xg_for', 'away_goals_scored',
            'home_goals_counter_for', 'home_goals_setpiece_for',
            'away_goals_counter_against', 'away_goals_setpiece_against'
        ]
        
        # Add venue column if not present
        if 'venue' not in df.columns:
            df['venue'] = 'home'
        
        # Check which columns we have
        available_columns = [col for col in required_columns if col in df.columns]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"Missing some required columns: {missing_columns}")
        
        # Create clean DataFrame
        clean_df = df[['team', 'venue'] + available_columns].copy()
        
        # Convert numeric columns
        numeric_columns = [
            'defenders_out', 'goals_conceded_last_5', 'goals_scored_last_5',
            'home_xg_for', 'home_goals_scored', 'away_xg_for', 'away_goals_scored',
            'home_goals_counter_for', 'home_goals_setpiece_for',
            'away_goals_counter_against', 'away_goals_setpiece_against'
        ]
        
        for col in numeric_columns:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
                clean_df[col].fillna(0, inplace=True)
        
        st.success(f"✅ Loaded {league_name} data ({len(clean_df)} records)")
        return clean_df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def prepare_team_data(df, team_name, venue):
    """Prepare team data for analysis."""
    team_data = df[(df['team'] == team_name) & (df['venue'] == venue.lower())]
    
    if team_data.empty:
        team_data = df[(df['team'].str.lower() == team_name.lower()) & 
                      (df['venue'] == venue.lower())]
    
    if team_data.empty:
        team_data = df[df['team'].str.lower() == team_name.lower()]
        if not team_data.empty:
            team_data = team_data.iloc[[0]]
    
    if team_data.empty:
        raise ValueError(f"No data found for {team_name}")
    
    return team_data.iloc[0].to_dict()

# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def display_layer1_analysis(layer1_result, home_team, away_team):
    """Display Layer 1: Situation Classification"""
    st.markdown("## 📊 Layer 1: Situation Classification")
    
    # Crisis Scan
    crisis = layer1_result['crisis_analysis']
    if crisis['flags']:
        st.error("### 🚨 Crisis Scan: RED FLAGS DETECTED")
        for flag in crisis['flags']:
            st.error(f"• {flag}")
    else:
        st.success("### ✅ Crisis Scan: No structural crisis")
    
    # Reality Check
    reality = layer1_result['reality_analysis']
    if reality['gaps']:
        st.warning("### 📈 Reality Check: Market Mispricing Detected")
        for gap in reality['gaps']:
            st.warning(f"• {gap}")
    else:
        st.info("### ⚖️ Reality Check: Market perception aligns with reality")
    
    # Tactical Edge
    tactical = layer1_result['tactical_analysis']
    if tactical['has_edge']:
        st.success("### ⚡ Tactical Edge: Style Advantage Identified")
        for edge in tactical['edges']:
            st.success(f"• {edge}")
    else:
        st.info("### 🔄 Tactical Edge: No clear style mismatch")
    
    # Archetype Classification
    archetype = layer1_result['classification']['archetype']
    explanation = layer1_result['classification']['explanation']
    
    # Color code based on archetype
    if archetype == "FADE THE FAVORITE":
        color = "#FF6B6B"
        icon = "🚫"
    elif archetype == "BACK THE UNDERDOG":
        color = "#4ECDC4"
        icon = "📈"
    elif archetype == "GOALS GALORE":
        color = "#FFD166"
        icon = "⚽"
    elif archetype == "DEFENSIVE GRIND":
        color = "#06D6A0"
        icon = "🛡️"
    else:
        color = "#118AB2"
        icon = "⚠️"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}, rgba(78,205,196,0.9));
                border-radius: 15px; padding: 25px; margin: 20px 0; color: white;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 2.5em; text-align: center; margin-bottom: 15px;">{icon}</div>
        <div style="font-size: 2em; font-weight: 800; margin: 15px 0; text-align: center;">{archetype}</div>
        <div style="font-size: 1.3em; text-align: center; opacity: 0.9;">{explanation}</div>
        <div style="font-size: 1.1em; text-align: center; margin-top: 15px; opacity: 0.8;">
        {home_team} vs {away_team}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_layer2_validation(validation_result, archetype):
    """Display Layer 2: Market Validation Results"""
    st.markdown("## 🛡️ Layer 2: Decision Firewall")
    
    if archetype == "AVOID":
        st.warning("### ⚠️ No Market Validation Performed")
        st.info("Archetype is AVOID → No bets considered regardless of validation")
        return
    
    # Show passed markets
    passed_markets = validation_result['passed_markets']
    rejected_markets = validation_result['rejected_markets']
    
    if passed_markets:
        st.success("### ✅ Markets That Passed Validation")
        for market in passed_markets:
            st.success(f"• **{market}**")
    else:
        st.error("### ❌ No Markets Passed Validation")
    
    # Show rejected markets with reasons
    if rejected_markets:
        st.warning("### 🚫 Markets Rejected (With Reasons)")
        
        for market, reasons in rejected_markets.items():
            with st.expander(f"❌ {market}"):
                if reasons['gates_failed']:
                    st.error("**Failed Gates:**")
                    for gate in reasons['gates_failed']:
                        st.error(f"• {gate}")
                if reasons['gates_passed']:
                    st.info("**Passed Gates:**")
                    for gate in reasons['gates_passed']:
                        st.info(f"• {gate}")
    
    # Show validation log
    with st.expander("📋 Validation Log"):
        for log in validation_result['validation_log']:
            if log['passed']:
                st.success(f"✅ {log['market']}: {log['message']}")
            else:
                st.error(f"❌ {log['market']}: {log['message']}")

def display_final_decisions(validation_result, home_team, away_team):
    """Display Final Betting Decisions"""
    st.markdown("## 🎯 Final Decisions")
    
    decisions = validation_result['final_decisions']
    
    if decisions and decisions[0].startswith("NO BET"):
        st.error("### ❌ NO BET RECOMMENDED")
        for decision in decisions:
            st.error(f"• {decision}")
        
        st.info("""
        **Professional Discipline:**
        - Save your bankroll for clearer opportunities
        - Watch the game for learning, not betting
        - Look for better matches in the fixture list
        """)
    elif decisions:
        st.success("### ✅ ACTIONABLE BETS")
        
        # Display in a clean format
        for decision in decisions:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #06D6A0, #4ECDC4);
                        border-radius: 10px; padding: 15px; margin: 10px 0; color: white;">
                <div style="font-size: 1.3em; font-weight: 600;">{decision}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add professional context
        st.info("""
        **Professional Context:**
        - These markets passed ALL validation gates
        - Default state was REJECT - these earned permission
        - Consider position sizing based on confidence
        """)
    else:
        st.warning("### ⚠️ No Clear Decisions")
        st.info("The system completed analysis but produced no actionable bets.")

def display_three_layer_model():
    """Display the three-layer mental model"""
    st.markdown("---")
    st.markdown("## 🏗️ Three-Layer Professional Model")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #2D3047; border-radius: 10px; padding: 20px; color: white; height: 300px;">
            <div style="font-size: 2em; text-align: center; margin-bottom: 15px;">🔍</div>
            <h3 style="text-align: center;">Layer 1</h3>
            <h4 style="text-align: center; color: #4ECDC4;">Situation Classification</h4>
            <p style="text-align: center;">"What kind of match is this?"</p>
            <ul style="font-size: 0.9em;">
                <li>Crisis Scan</li>
                <li>Reality Check</li>
                <li>Tactical Edge</li>
                <li>Archetype Classification</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #2D3047; border-radius: 10px; padding: 20px; color: white; height: 300px;">
            <div style="font-size: 2em; text-align: center; margin-bottom: 15px;">🛡️</div>
            <h3 style="text-align: center;">Layer 2</h3>
            <h4 style="text-align: center; color: #4ECDC4;">Decision Firewall</h4>
            <p style="text-align: center;">"Is this market safe enough?"</p>
            <ul style="font-size: 0.9em;">
                <li>Market-Specific Gates</li>
                <li>Conservative Defaults</li>
                <li>Multi-Gate Validation</li>
                <li>"Why Not" Tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #2D3047; border-radius: 10px; padding: 20px; color: white; height: 300px;">
            <div style="font-size: 2em; text-align: center; margin-bottom: 15px;">🎯</div>
            <h3 style="text-align: center;">Layer 3</h3>
            <h4 style="text-align: center; color: #4ECDC4;">Capital Allocation</h4>
            <p style="text-align: center;">"Do I actually pull the trigger?"</p>
            <ul style="font-size: 0.9em;">
                <li>Position Sizing</li>
                <li>Bankroll Management</li>
                <li>Emotional Discipline</li>
                <li>Post-Mortem Review</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #1A1B2E; border-radius: 10px; padding: 20px; margin-top: 20px; color: white;">
        <h4 style="color: #4ECDC4;">Professional Insight:</h4>
        <p>Most money is made by saying <strong>NO</strong>, not YES. This framework doesn't win because it predicts better — it wins because it avoids false edges and emotional bets, acting only when signals align.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN STREAMLIT APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="Professional Decision Framework",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #4ECDC4, #44A08D);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #44A08D, #4ECDC4);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2D3047, #1A1B2E);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin: 10px 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2D3047;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 style="text-align: center; color: #4ECDC4;">🎯 Professional Decision Framework</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2em;">Three-Layer Decision System: Classification → Validation → Action</p>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'league_data' not in st.session_state:
        st.session_state.league_data = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏆 League Selection")
        leagues = ['LA LIGA', 'PREMIER LEAGUE']
        selected_league = st.selectbox("Choose League:", leagues)
        
        st.markdown("---")
        st.markdown("### 📥 Data Loading")
        
        if st.button(f"📂 Load {selected_league} Data", type="primary", use_container_width=True):
            with st.spinner(f"Loading {selected_league} data..."):
                df = load_league_data(selected_league)
                if df is not None:
                    st.session_state.league_data = df
                    st.session_state.selected_league = selected_league
                    st.success(f"Loaded {len(df)} records")
                else:
                    st.error("Failed to load data")
        
        st.markdown("---")
        st.markdown("### 🏗️ Three-Layer Model")
        st.info("""
        **Layer 1:** Situation Classification
        - Crisis Scan → Reality Check → Tactical Edge → Archetype
        
        **Layer 2:** Decision Firewall  
        - Market-specific validation gates
        - Conservative defaults
        - "Why not?" tracking
        
        **Layer 3:** Capital Allocation
        - Position sizing
        - Bankroll management
        - Emotional discipline
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Framework Status")
        if st.session_state.get('league_data') is not None:
            st.success("✅ Layer 1: Ready")
            st.success("✅ Layer 2: Ready")
            st.info("⏳ Layer 3: Manual (Professional Judgment)")
        else:
            st.warning("⏳ Load data to begin")
    
    # Main content
    if st.session_state.league_data is None:
        st.info("👈 **Please load league data from the sidebar to begin**")
        
        # Display the three-layer model
        display_three_layer_model()
        
        st.markdown("""
        ### How to Use This Framework:
        
        1. **Load Data**: Select league and click "Load Data"
        2. **Select Teams**: Choose home and away teams
        3. **Run Analysis**: Click "Run Three-Layer Analysis"
        4. **Review Decisions**: Only act on markets that pass ALL validation
        
        **Professional Discipline:**
        - Most money is made by saying NO
        - Default state is REJECT unless proven safe
        - Track "why not" more than "why yes"
        """)
        return
    
    df = st.session_state.league_data
    selected_league = st.session_state.get('selected_league', 'Unknown League')
    
    # Team selection
    st.markdown("## 🏟️ Match Selection")
    
    available_teams = sorted(df['team'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team:", available_teams, key="home_team")
        
        # Quick home stats
        home_stats = df[df['team'] == home_team]
        if not home_stats.empty:
            home_row = home_stats.iloc[0]
            st.markdown(f"**{home_team} Quick Stats:**")
            
            cols = st.columns(2)
            with cols[0]:
                defenders = home_row.get('defenders_out', 0)
                st.metric("Defenders Out", defenders, 
                         "🚨 CRISIS" if defenders >= 3 else "")
            with cols[1]:
                recent_goals = home_row.get('goals_scored_last_5', 0)
                st.metric("Goals L5", recent_goals)
    
    with col2:
        away_options = [t for t in available_teams if t != home_team]
        away_team = st.selectbox("✈️ Away Team:", away_options, key="away_team")
        
        # Quick away stats
        away_stats = df[df['team'] == away_team]
        if not away_stats.empty:
            away_row = away_stats.iloc[0]
            st.markdown(f"**{away_team} Quick Stats:**")
            
            cols = st.columns(2)
            with cols[0]:
                defenders = away_row.get('defenders_out', 0)
                st.metric("Defenders Out", defenders,
                         "🚨 CRISIS" if defenders >= 3 else "")
            with cols[1]:
                recent_goals = away_row.get('goals_scored_last_5', 0)
                st.metric("Goals L5", recent_goals)
    
    # Run analysis button
    if st.button("🎯 Run Three-Layer Analysis", type="primary", use_container_width=True):
        if home_team == away_team:
            st.error("Please select different teams.")
            return
        
        try:
            # Prepare data
            home_data = prepare_team_data(df, home_team, 'home')
            away_data = prepare_team_data(df, away_team, 'away')
            
            # Layer 1: Situation Classification
            with st.spinner("Running Layer 1: Situation Classification..."):
                framework = ProfessionalDecisionFramework()
                layer1_result = framework.analyze_match(home_data, away_data)
                st.session_state.layer1_result = layer1_result
            
            # Layer 2: Market Validation
            with st.spinner("Running Layer 2: Decision Firewall..."):
                firewall = DecisionFirewall()
                archetype = layer1_result['classification']['archetype']
                validation_result = firewall.validate_all_markets(
                    layer1_result, home_data, away_data, archetype
                )
                st.session_state.validation_result = validation_result
            
            # Store team names
            st.session_state.home_team = home_team
            st.session_state.away_team = away_team
            
            st.success("✅ Three-layer analysis complete!")
            
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
    
    # Display results
    if st.session_state.get('layer1_result') and st.session_state.get('validation_result'):
        layer1_result = st.session_state.layer1_result
        validation_result = st.session_state.validation_result
        home_team = st.session_state.home_team
        away_team = st.session_state.away_team
        archetype = layer1_result['classification']['archetype']
        
        # Create tabs for detailed view
        tab1, tab2, tab3 = st.tabs(["📊 Full Analysis", "🎯 Final Decisions", "🏗️ Model Overview"])
        
        with tab1:
            # Layer 1 Analysis
            display_layer1_analysis(layer1_result, home_team, away_team)
            
            # Layer 2 Validation
            display_layer2_validation(validation_result, archetype)
            
            # Layer 3 would be manual professional judgment
        
        with tab2:
            # Final Decisions
            display_final_decisions(validation_result, home_team, away_team)
            
            # Professional Context
            st.markdown("---")
            st.markdown("### 💼 Professional Context")
            
            if validation_result['final_decisions'] and not validation_result['final_decisions'][0].startswith("NO BET"):
                st.success("""
                **These markets earned permission to bet:**
                - Passed Layer 1 archetype filtering
                - Passed ALL Layer 2 validation gates
                - Default state was REJECT - these are exceptions
                
                **Next Steps (Layer 3 - Manual):**
                1. Check current odds against "fair value"
                2. Determine position size (1-3% of bankroll)
                3. Set stop-loss and take-profit levels
                4. Review post-match regardless of outcome
                """)
            else:
                st.warning("""
                **No actionable bets identified.**
                
                **Professional Response:**
                - Save bankroll for clearer opportunities
                - Watch the match for learning purposes
                - Update tracking with "good rejection" note
                - Move to next fixture without emotional attachment
                """)
        
        with tab3:
            # Display the three-layer model
            display_three_layer_model()
            
            # Show architecture diagram
            st.markdown("### 🔄 Decision Flow")
            st.markdown("""
            ```
            RAW DATA
                ↓
            [LAYER 1] Situation Classification
            ├── Crisis Scan (defenders_out ≥ 3, goals_conceded_last_5 > 12)
            ├── Reality Check (xG vs goals gap > 3)
            ├── Tactical Edge (style matchups)
            └── Archetype (5 categories)
                ↓
            [LAYER 2] Decision Firewall
            ├── Market eligibility based on archetype
            ├── Market-specific validation gates
            ├── Conservative defaults (reject unless proven)
            └── "Why not?" tracking for rejected markets
                ↓
            [LAYER 3] Capital Allocation (MANUAL)
            ├── Odds check vs "fair value"
            ├── Position sizing (1-3% rule)
            ├── Bankroll management
            └── Post-mortem review
                ↓
            ACTION or NO ACTION
            ```
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
    <p><strong>Professional Insight:</strong> This framework doesn't win because it predicts better. It wins because it avoids false edges, avoids emotional bets, and acts only when signals align across multiple layers.</p>
    <p>Most money is made by saying <strong>NO</strong>, not YES.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()