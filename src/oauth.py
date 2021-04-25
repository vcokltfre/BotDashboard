from os import getenv


def build_oauth_token_request(code: str) -> tuple:
    """Given a code, return a dict of query params needed to complete the oath flow."""
    query = dict(
        client_id=int(getenv("CLIENT_ID")),
        client_secret=int(getenv("CLIENT_SECRET")),
        grant_type="authorization_code",
        code=code,
        redirect_uri=f"{int(getenv('BASE_URL'))}/callback",
        scope="identify",
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return query, headers
