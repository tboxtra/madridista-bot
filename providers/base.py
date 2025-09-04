from typing import Optional, Dict, Any, List

class LiveProvider:
    """
    Interface all providers must implement.
    """
    def get_team_live_event(self) -> Optional[Dict[str, Any]]:
        """
        Return a live event dict if the team is currently playing, else None.
        The event dict must include:
          - id (event id, str or int)
          - homeName, awayName (str)
          - homeScore, awayScore (int)
          - minute (int or None)
          - competition (str or '')
        """
        raise NotImplementedError

    def get_event_incidents(self, event_id) -> List[Dict[str, Any]]:
        """
        Return a list of incidents in chronological order.
        Each incident should contain:
          - id (unique str/int if available; else compose one)
          - type ('goal', 'yellow', 'red', 'sub', 'var', 'period', etc.)
          - minute (int or None)
          - team ('home' | 'away' | None)
          - text (short human text: e.g., 'Vinícius Júnior scores')
        """
        raise NotImplementedError

    def short_event_line(self, event: Dict[str, Any]) -> str:
        """
        Return a short line summarizing current state.
        """
        raise NotImplementedError
