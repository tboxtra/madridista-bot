def route_related(text: str):
    """Route related Real Madrid questions"""
    text_lower = text.lower()
    
    # Basic routing for common questions
    if any(word in text_lower for word in ['injured', 'injury', 'injuries']):
        return "Use /injuries to see current injury information."
    
    if any(word in text_lower for word in ['squad', 'players', 'roster']):
        return "Use /squad to see the current squad."
    
    if any(word in text_lower for word in ['table', 'standings', 'position']):
        return "Use /table to see the league table."
    
    if any(word in text_lower for word in ['form', 'results', 'recent']):
        return "Use /form to see recent results."
    
    if any(word in text_lower for word in ['scorers', 'goals', 'top scorer']):
        return "Use /scorers to see top scorers."
    
    return None
