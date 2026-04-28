import os
import requests
import unicodedata
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_DATA_API_KEY")
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.api_key}

    def normalize(self, text):
        if not text: return ""
        normalized = unicodedata.normalize('NFD', text)
        return "".join([c for c in normalized if unicodedata.category(c) != 'Mn']).lower()

    def is_match(self, search_term, team_obj):
        target = self.normalize(search_term)
        names = [
            self.normalize(team_obj.get("name", "")),
            self.normalize(team_obj.get("shortName", "")),
            self.normalize(team_obj.get("tla", ""))
        ]
        if any(target == n for n in names): return True
        search_words = target.split()
        for name in names:
            if all(word in name for word in search_words): return True
        return False

    def get_team_id(self, team_name, league_code):
        if not self.api_key: return "NO_KEY", None
        url = f"{self.base_url}/competitions/{league_code}/teams"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 429: return "RATE_LIMIT", None
            if response.status_code == 403: return "FORBIDDEN", None
            
            if response.status_code == 200:
                data = response.json()
                for team in data.get("teams", []):
                    if self.is_match(team_name, team):
                        return team["id"], team["name"]
            return "NOT_FOUND", None
        except Exception: return "ERROR", None

    def get_last_matches(self, team_id, last=10):
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {"status": "FINISHED", "limit": 20}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                matches.sort(key=lambda x: x["utcDate"], reverse=True)
                return matches[:last]
            return []
        except Exception: return []

    def get_match_data(self, team_name, league_code):
        res = self.get_team_id(team_name, league_code)
        
        # Check if we got an error code instead of a team_id
        if isinstance(res[0], str) and not isinstance(res[0], int) and len(str(res[0])) > 4:
            return {"error": res[0], "team": team_name}

        team_id, real_name = res
        fixtures = self.get_last_matches(team_id)
        
        if not fixtures:
            return {"error": "NO_MATCHES", "team": real_name}
        
        processed_matches = []
        for f in fixtures:
            score = f.get("score", {}).get("fullTime", {})
            home_id = f["homeTeam"]["id"]
            is_home = (home_id == team_id)
            scored = score.get("home") if is_home else score.get("away")
            conceded = score.get("away") if is_home else score.get("home")
            if scored is None or conceded is None: continue
                
            processed_matches.append({
                "date": f["utcDate"],
                "opponent": f["awayTeam"]["name"] if is_home else f["homeTeam"]["name"],
                "is_home": is_home,
                "scored": scored,
                "conceded": conceded,
                "result": "W" if scored > conceded else ("L" if scored < conceded else "D"),
                "over_2_5": (scored + conceded) > 2.5,
                "btts": scored > 0 and conceded > 0
            })
        return {"team_name": real_name, "matches": processed_matches}
