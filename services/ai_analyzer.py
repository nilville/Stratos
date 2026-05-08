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
                {"role": "system", "content": "You are a sharp football betting expert. Provide hyper-concise predictions based ONLY on the provided match results. No introductions, no filler, no 'Based on the data'. Just direct insight."},
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

        prompt = f"""
Match: {team_a['team_name']} vs {team_b['team_name']}
Data:
{team_a['team_name']} results:
{format_matches(team_a)}

{team_b['team_name']} results:
{format_matches(team_b)}

Task: Provide a hyper-concise prediction.
Format:
**Prediction**: [One sentence prediction based on these specific results]
**Best Bet**: [The single most likely pick]

Respond in {lang}. No fluff.
"""
        return prompt
