import os
import time

import requests
import unicodedata


class APIClient:
    MAX_RETRIES = 3
    BASE_DELAY = 2

    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_DATA_API_KEY")
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.api_key}

    def normalize(self, text):
        if not text:
            return ""
        normalized = unicodedata.normalize("NFD", text)
        return "".join(
            [c for c in normalized if unicodedata.category(c) != "Mn"]
        ).lower()

    def is_match(self, search_term, team_obj):
        target = self.normalize(search_term)
        names = [
            self.normalize(team_obj.get("name", "")),
            self.normalize(team_obj.get("shortName", "")),
            self.normalize(team_obj.get("tla", "")),
        ]
        if any(target == n for n in names):
            return True
        search_words = target.split()
        for name in names:
            if all(word in name for word in search_words):
                return True
        return False

    def _request(self, url, params=None):
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=10
                )
                if response.status_code == 429:
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.BASE_DELAY**attempt)
                        continue
                    return {"status": "error", "error_code": "RATE_LIMIT"}
                if response.status_code == 403:
                    return {"status": "error", "error_code": "FORBIDDEN"}
                if response.status_code == 200:
                    return {"status": "ok", "data": response.json()}
                return {"status": "error", "error_code": "UNKNOWN"}
            except requests.RequestException:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BASE_DELAY**attempt)
                    continue
                return {"status": "error", "error_code": "NETWORK_ERROR"}
        return {"status": "error", "error_code": "RATE_LIMIT"}

    def get_team_id(self, team_name, league_code):
        if not self.api_key:
            return {"status": "error", "error_code": "NO_KEY"}

        result = self._request(f"{self.base_url}/competitions/{league_code}/teams")
        if result["status"] != "ok":
            return {"status": "error", "error_code": result["error_code"]}

        for team in result["data"].get("teams", []):
            if self.is_match(team_name, team):
                return {"status": "ok", "id": team["id"], "name": team["name"]}

        return {"status": "error", "error_code": "NOT_FOUND"}

    def get_last_matches(self, team_id, last=10):
        result = self._request(
            f"{self.base_url}/teams/{team_id}/matches",
            params={"status": "FINISHED", "limit": last},
        )
        if result["status"] != "ok":
            return []

        matches = result["data"].get("matches", [])
        matches.sort(key=lambda x: x["utcDate"], reverse=True)
        return matches[:last]

    def get_league_teams(self, league_code):
        result = self._request(
            f"{self.base_url}/competitions/{league_code}/teams"
        )
        if result["status"] != "ok":
            return []
        teams = result["data"].get("teams", [])
        return sorted(
            [{"name": t["name"], "shortName": t.get("shortName", "")} for t in teams],
            key=lambda t: t["name"],
        )

    def get_match_data(self, team_name, league_code):
        result = self.get_team_id(team_name, league_code)

        if result["status"] != "ok":
            return {"error": result["error_code"], "team": team_name}

        fixtures = self.get_last_matches(result["id"])

        if not fixtures:
            return {"error": "NO_MATCHES", "team": result["name"]}

        processed_matches = []
        for f in fixtures:
            score = f.get("score", {}).get("fullTime", {})
            home_id = f["homeTeam"]["id"]
            is_home = home_id == result["id"]
            scored = score.get("home") if is_home else score.get("away")
            conceded = score.get("away") if is_home else score.get("home")
            if scored is None or conceded is None:
                continue

            processed_matches.append(
                {
                    "date": f["utcDate"],
                    "opponent": f["awayTeam"]["name"]
                    if is_home
                    else f["homeTeam"]["name"],
                    "is_home": is_home,
                    "scored": scored,
                    "conceded": conceded,
                    "result": "W"
                    if scored > conceded
                    else ("L" if scored < conceded else "D"),
                    "over_2_5": (scored + conceded) > 2.5,
                    "btts": scored > 0 and conceded > 0,
                }
            )
        return {"team_name": result["name"], "matches": processed_matches}
