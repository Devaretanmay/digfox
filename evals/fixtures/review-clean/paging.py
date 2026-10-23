def page(items, limit=50):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    return items[:limit]
