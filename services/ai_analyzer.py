import os
import requests
import json

class AIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("openRouter_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/nemotron-3-super-120b-a12b:free"

    def analyze_matchup(self, team_a_data, team_b_data, lang="en"):
        if not self.api_key:
            return "OpenRouter API Key not found. Please set openRouter_API_KEY in .env"

        prompt = self._build_prompt(team_a_data, team_b_data, lang)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/nilville/Stratos", # Optional
            "X-Title": "Stratos Football Analyzer", # Optional
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an elite football analyst specializing in data-driven match predictions and tactical analysis. Your expertise includes team form analysis, goal-scoring patterns, defensive vulnerabilities, and betting market insights. Always provide specific, actionable intelligence based strictly on the statistical data provided. Avoid generic statements and focus on unique insights that give genuine predictive value."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data), timeout=30)
            if response.status_code != 200:
                return f"AI Error ({response.status_code}): {response.text}"
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error during AI analysis: {str(e)}"

    def _build_prompt(self, team_a, team_b, lang):
        def format_matches(team):
            matches_str = ""
            for m in team['matches']:
                result_map = {"W": "Win", "L": "Loss", "D": "Draw"}
                matches_str += f"- vs {m['opponent']}: {m['scored']}-{m['conceded']} ({result_map[m['result']]})\n"
            return matches_str

        def calculate_team_stats(team):
            matches = team.get('matches', [])
            if not matches:
                return {"avg_scored": 0, "avg_conceded": 0, "win_rate": 0, "form": ""}
            
            count = len(matches)
            total_scored = sum(m.get("scored", 0) for m in matches)
            total_conceded = sum(m.get("conceded", 0) for m in matches)
            wins = sum(1 for m in matches if m.get("result") == "W")
            
            # Calculate recent form (last 5 matches)
            recent_form = ""
            for m in matches[:5]:
                recent_form += m.get("result", "D")
            
            return {
                "avg_scored": round(total_scored / count, 2),
                "avg_conceded": round(total_conceded / count, 2),
                "win_rate": round((wins / count) * 100, 2),
                "form": recent_form
            }

        stats_a = calculate_team_stats(team_a)
        stats_b = calculate_team_stats(team_b)

        prompt = f"""
You are an elite football analyst with deep expertise in match prediction, team tactics, and betting markets. Analyze the following matchup using advanced football intelligence.

MATCHUP: {team_a['team_name']} vs {team_b['team_name']}

TEAM PERFORMANCE ANALYSIS:

{team_a['team_name']}:
- Recent Form: {stats_a['form']}
- Goals Scored: {stats_a['avg_scored']} per game
- Goals Conceded: {stats_a['avg_conceded']} per game  
- Win Rate: {stats_a['win_rate']}%
- Recent Results:
{format_matches(team_a)}

{team_b['team_name']}:
- Recent Form: {stats_b['form']}
- Goals Scored: {stats_b['avg_scored']} per game
- Goals Conceded: {stats_b['avg_conceded']} per game
- Win Rate: {stats_b['win_rate']}%
- Recent Results:
{format_matches(team_b)}

ANALYSIS REQUIREMENTS:
1. Evaluate head-to-head tactical matchups
2. Consider current form and momentum
3. Analyze attacking/defensive balance
4. Identify key performance trends
5. Factor in goal-scoring patterns

OUTPUT FORMAT (strictly follow):
**Match Analysis**: [2-3 sentences of tactical insight]
**Key Factors**: [Bullet 2-3 critical factors influencing the outcome]
**Prediction**: [Clear prediction with score expectation]
**Best Bet**: [Single strongest betting recommendation with reasoning]
**Confidence**: [High/Medium/Low with brief justification]

CRITICAL INSTRUCTIONS:
- Base analysis ONLY on provided statistics and recent form
- No generic football clichés or obvious statements
- Provide specific, actionable insights
- Consider both teams' current momentum
- Respond in {lang} language
- Maximum 150 words total
"""
        return prompt
