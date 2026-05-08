class Analyzer:
    WIN_THRESHOLD = 70
    OVER_UNDER_THRESHOLD = 65
    UNDER_THRESHOLD = 35

    def __init__(self, team_a_data, team_b_data):
        self.team_a = team_a_data
        self.team_b = team_b_data

    def calculate_stats(self, matches):
        stats = {
            "avg_scored": 0,
            "avg_conceded": 0,
            "win_rate": 0,
            "over_2_5_prob": 0,
            "btts_prob": 0,
            "clean_sheet_rate": 0,
        }

        if not matches:
            return stats

        count = len(matches)
        total_scored = sum(m.get("scored", 0) for m in matches)
        total_conceded = sum(m.get("conceded", 0) for m in matches)

        wins = sum(1 for m in matches if m.get("result") == "W")
        over_2_5 = sum(1 for m in matches if m.get("over_2_5"))
        btts = sum(1 for m in matches if m.get("btts"))
        clean_sheets = sum(1 for m in matches if m.get("conceded") == 0)

        stats.update(
            {
                "avg_scored": round(total_scored / count, 2),
                "avg_conceded": round(total_conceded / count, 2),
                "win_rate": round((wins / count) * 100, 2),
                "over_2_5_prob": round((over_2_5 / count) * 100, 2),
                "btts_prob": round((btts / count) * 100, 2),
                "clean_sheet_rate": round((clean_sheets / count) * 100, 2),
            }
        )
        return stats

    def get_analysis(self):
        stats_a = self.calculate_stats(self.team_a.get("matches", []))
        stats_b = self.calculate_stats(self.team_b.get("matches", []))

        combined_over_2_5 = (stats_a["over_2_5_prob"] + stats_b["over_2_5_prob"]) / 2
        combined_btts = (stats_a["btts_prob"] + stats_b["btts_prob"]) / 2

        recommendations = []

        if stats_a["win_rate"] > self.WIN_THRESHOLD:
            recommendations.append(
                {"bet": f"{self.team_a['team_name']} Win", "prob": stats_a["win_rate"]}
            )
        elif stats_b["win_rate"] > self.WIN_THRESHOLD:
            recommendations.append(
                {"bet": f"{self.team_b['team_name']} Win", "prob": stats_b["win_rate"]}
            )

        if combined_over_2_5 > self.OVER_UNDER_THRESHOLD:
            recommendations.append({"bet": "Over 2.5 Goals", "prob": combined_over_2_5})
        elif combined_over_2_5 < self.UNDER_THRESHOLD:
            recommendations.append(
                {"bet": "Under 2.5 Goals", "prob": 100 - combined_over_2_5}
            )

        if combined_btts > self.OVER_UNDER_THRESHOLD:
            recommendations.append({"bet": "BTTS - Yes", "prob": combined_btts})

        best_bet = (
            max(recommendations, key=lambda x: x["prob"]) if recommendations else None
        )

        return {
            "team_a_stats": stats_a,
            "team_b_stats": stats_b,
            "best_bet": best_bet,
            "all_insights": recommendations,
        }
