from services.analyzer import Analyzer


def make_team(name, matches=None):
    return {"team_name": name, "matches": matches or []}


def make_match(scored, conceded, result=None, over_2_5=None, btts=None):
    return {
        "scored": scored,
        "conceded": conceded,
        "result": result or ("W" if scored > conceded else "L" if scored < conceded else "D"),
        "over_2_5": over_2_5 if over_2_5 is not None else (scored + conceded) > 2.5,
        "btts": btts if btts is not None else (scored > 0 and conceded > 0),
    }


class TestCalculateStats:
    def test_empty_matches(self):
        analyzer = Analyzer(make_team("A"), make_team("B"))
        stats = analyzer.calculate_stats([])
        assert stats["avg_scored"] == 0
        assert stats["avg_conceded"] == 0
        assert stats["win_rate"] == 0
        assert stats["over_2_5_prob"] == 0
        assert stats["btts_prob"] == 0
        assert stats["clean_sheet_rate"] == 0

    def test_all_wins_clean_sheets(self):
        matches = [
            make_match(3, 0),
            make_match(2, 0),
            make_match(1, 0),
        ]
        analyzer = Analyzer(make_team("A"), make_team("B"))
        stats = analyzer.calculate_stats(matches)
        assert stats["avg_scored"] == 2.0
        assert stats["avg_conceded"] == 0
        assert stats["win_rate"] == 100.0
        assert stats["clean_sheet_rate"] == 100.0
        assert stats["btts_prob"] == 0

    def test_mixed_results(self):
        matches = [
            make_match(2, 1),
            make_match(0, 2),
            make_match(1, 1),
            make_match(3, 0),
            make_match(0, 0),
        ]
        analyzer = Analyzer(make_team("A"), make_team("B"))
        stats = analyzer.calculate_stats(matches)
        assert stats["avg_scored"] == 1.2
        assert stats["win_rate"] == 40.0
        assert stats["clean_sheet_rate"] == 40.0
        assert stats["btts_prob"] == 40.0


class TestGetAnalysis:
    def test_high_confidence_win(self):
        winning_matches = [make_match(3, 0) for _ in range(10)]
        losing_matches = [make_match(0, 3) for _ in range(10)]
        team_a = make_team("Arsenal", winning_matches)
        team_b = make_team("Chelsea", losing_matches)
        analyzer = Analyzer(team_a, team_b)
        result = analyzer.get_analysis()
        assert result["best_bet"] is not None
        assert "Arsenal Win" in result["best_bet"]["bet"]
        assert result["best_bet"]["prob"] > 70

    def test_no_recommendation_when_low_confidence(self):
        matches_a = [
            make_match(1, 0),
            make_match(0, 1),
            make_match(2, 2),
            make_match(0, 0),
            make_match(1, 2),
            make_match(3, 1),
            make_match(0, 3),
            make_match(2, 0),
            make_match(1, 1),
            make_match(0, 2),
        ]
        matches_b = [
            make_match(2, 1),
            make_match(0, 0),
            make_match(1, 3),
            make_match(3, 0),
            make_match(0, 1),
            make_match(1, 1),
            make_match(2, 0),
            make_match(0, 2),
            make_match(1, 2),
            make_match(2, 2),
        ]
        team_a = make_team("Team A", matches_a)
        team_b = make_team("Team B", matches_b)
        analyzer = Analyzer(team_a, team_b)
        result = analyzer.get_analysis()
        assert result["best_bet"] is None

    def test_high_btts_recommendation(self):
        matches = [make_match(2, 2, btts=True, over_2_5=True) for _ in range(5)] + [make_match(1, 1, btts=True, over_2_5=False) for _ in range(5)]
        team_a = make_team("Team A", matches)
        team_b = make_team("Team B", matches)
        analyzer = Analyzer(team_a, team_b)
        result = analyzer.get_analysis()
        assert result["best_bet"] is not None
        assert "BTTS" in result["best_bet"]["bet"]

    def test_low_scoring_under_recommendation(self):
        matches = [make_match(0, 0, btts=False, over_2_5=False) for _ in range(10)]
        team_a = make_team("Team A", matches)
        team_b = make_team("Team B", matches)
        analyzer = Analyzer(team_a, team_b)
        result = analyzer.get_analysis()
        assert result["best_bet"] is not None
        assert "Under" in result["best_bet"]["bet"]

    def test_empty_matches_no_crash(self):
        team_a = make_team("Team A", [])
        team_b = make_team("Team B", [])
        analyzer = Analyzer(team_a, team_b)
        result = analyzer.get_analysis()
        assert result["best_bet"] is not None
        assert result["best_bet"]["bet"] == "Under 2.5 Goals"
        assert result["team_a_stats"]["avg_scored"] == 0
        assert result["team_b_stats"]["avg_scored"] == 0
