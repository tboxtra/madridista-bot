def live_handler() -> str:
    """Handle /live command - show current live match status"""
    try:
        from live.monitor_providers import PROV
        ev = PROV.get_team_live_event()
        if ev:
            return PROV.short_event_line(ev)
        else:
            return "No live match currently."
    except Exception as e:
        return f"Live data temporarily unavailable. ({e})"
