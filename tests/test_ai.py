from jobs_ai.ai import HeuristicAnalyzer


def test_heuristic_profile_generates_search_queries_from_resume():
    analyzer = HeuristicAnalyzer()

    profile = analyzer.build_candidate_profile(
        "Nicolas Alves\nIngeniero de Software Full Stack con Python, FastAPI, React y OpenAI."
    )

    assert profile.search_queries
    assert any("remote Spain" in query for query in profile.search_queries)
    assert "python backend developer" in profile.target_titles
