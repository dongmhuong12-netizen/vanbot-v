def apply_decay(user):

    if not user.get("reset_at"):
        return user

    import time

    if time.time() >= user["reset_at"]:
        user["level"] = max(0, user["level"] - 1)

    return user
