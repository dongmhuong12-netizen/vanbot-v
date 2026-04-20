import time

cache = {}

def check_spam(user_id, guild_id):

    now = time.time()
    key = f"{guild_id}:{user_id}"

    if key not in cache:
        cache[key] = []

    cache[key].append(now)

    # giữ 1 giây window
    cache[key] = [t for t in cache[key] if now - t < 1]

    return len(cache[key]) >= 5
