from secrets import token_urlsafe


def generate_token():
    return token_urlsafe(16)
