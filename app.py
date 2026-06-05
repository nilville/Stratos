import os
import threading
from concurrent.futures import ThreadPoolExecutor

from cachetools import TTLCache
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from services.ai_analyzer import AIAnalyzer
from services.analyzer import Analyzer
from services.api_client import APIClient

load_dotenv()

LEAGUES = ["PL", "PD", "BL1", "SA", "FL1", "DED"]

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())
cache = TTLCache(maxsize=300, ttl=3600)
cache_lock = threading.Lock()


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/api/teams")
def api_teams():
    with cache_lock:
        if "teams_by_league" in cache:
            return jsonify(cache["teams_by_league"])

    client = APIClient()
    teams_by_league = {}

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = executor.map(client.get_league_teams, LEAGUES)
        teams_by_league = dict(zip(LEAGUES, list(results)))

    with cache_lock:
        cache["teams_by_league"] = teams_by_league
    return jsonify(teams_by_league)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    team_a_name = request.form.get("team_a")
    league_a = request.form.get("league_a")
    team_b_name = request.form.get("team_b")
    league_b = request.form.get("league_b")
    lang = request.form.get("lang", "en")

    if not team_a_name or not team_b_name:
        return render_template("index.html", error="Please provide both team names.")

    if league_a not in LEAGUES or league_b not in LEAGUES:
        return render_template("index.html", error="Invalid league selection.")

    cache_key = f"{team_a_name.lower()}_{league_a}_{team_b_name.lower()}_{league_b}"

    with cache_lock:
        if cache_key in cache:
            return render_template("results.html", **cache[cache_key], lang=lang)

    client = APIClient()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(client.get_match_data, team_a_name, league_a)
            future_b = executor.submit(client.get_match_data, team_b_name, league_b)

            team_a_result = future_a.result()
            if "error" in team_a_result:
                return render_template(
                    "index.html",
                    error_code=team_a_result["error"],
                    error_team=team_a_result["team"],
                    lang=lang,
                )

            team_b_result = future_b.result()
            if "error" in team_b_result:
                return render_template(
                    "index.html",
                    error_code=team_b_result["error"],
                    error_team=team_b_result["team"],
                    lang=lang,
                )

        analyzer = Analyzer(team_a_result, team_b_result)
        analysis_results = analyzer.get_analysis()

        render_data = {
            "team_a": team_a_result,
            "team_b": team_b_result,
            "analysis": analysis_results,
            "league_a": league_a,
            "league_b": league_b,
        }

        with cache_lock:
            cache[cache_key] = render_data
        return render_template("results.html", **render_data, lang=lang)

    except Exception as e:
        app.logger.exception("Analysis failed")
        return render_template("index.html", error="An error occurred during analysis. Please try again.")


@app.route("/api/ai_analyze", methods=["POST"])
def api_ai_analyze():
    team_a_data = request.json.get("team_a")
    team_b_data = request.json.get("team_b")
    lang = request.json.get("lang", "en")

    if not team_a_data or not team_b_data:
        return jsonify({"error": "Missing data"}), 400

    ai_analyzer = AIAnalyzer()
    ai_analysis = ai_analyzer.analyze_matchup(team_a_data, team_b_data, lang=lang)
    return jsonify({"analysis": ai_analysis})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
