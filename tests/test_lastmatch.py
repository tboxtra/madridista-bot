from features.matches_last import last_match_handler

class DummyFD:
    team_id = 86
    def _get(self, path, params=None):
        return {"matches": [
            {"status": "FINISHED", "utcDate": "2025-09-01T20:00:00Z",
             "homeTeam": {"name": "Real Madrid"}, "awayTeam": {"name": "Barcelona"},
             "score": {"fullTime": {"home": 3, "away": 1}}},
            {"status": "SCHEDULED", "utcDate": "2025-09-13T15:15:00Z",
             "homeTeam": {"name": "Real Sociedad"}, "awayTeam": {"name": "Real Madrid"}}
        ]}

def test_last_match_handler():
    out = last_match_handler(DummyFD())
    assert "Real Madrid 3 - 1 Barcelona" in out
