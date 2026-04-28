from flask import Flask, render_template, request
from services.api_client import APIClient
from services.analyzer import Analyzer
import os

app = Flask(__name__)
cache = {}

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

    client = APIClient()
    cache_key = f"{team_a_name.lower()}_{league_a}_{team_b_name.lower()}_{league_b}"
    
    if cache_key in cache:
        return render_template("results.html", **cache[cache_key], lang=lang)

    try:
        # Fetch data for Team A
        team_a_data = client.get_match_data(team_a_name, league_a)
        if "error" in team_a_data:
            return render_template("index.html", error_code=team_a_data["error"], error_team=team_a_data["team"], lang=lang)

        # Fetch data for Team B
        team_b_data = client.get_match_data(team_b_name, league_b)
        if "error" in team_b_data:
            return render_template("index.html", error_code=team_b_data["error"], error_team=team_b_data["team"], lang=lang)

        # Analyze
        analyzer = Analyzer(team_a_data, team_b_data)
        analysis_results = analyzer.get_analysis()

        render_data = {
            "team_a": team_a_data,
            "team_b": team_b_data,
            "analysis": analysis_results,
            "league_a": league_a,
            "league_b": league_b
        }

        cache[cache_key] = render_data
        return render_template("results.html", **render_data, lang=lang)


    except Exception as e:
        return render_template("index.html", error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Use environment variable for debug, default to False for security
    app.run(debug=os.getenv("FLASK_DEBUG", "True").lower() == "true")
