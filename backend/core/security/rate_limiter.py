from fastapi import Request
from slowapi import Limiter

from core.auth.jwt_service import verify_token


def get_rate_limit_key(
    request: Request,
) -> str:
    """
    Use authenticated user id as the
    rate limit key.

    Falls back to client IP for
    unauthenticated endpoints.
    """

    auth = request.headers.get(
        "Authorization"
    )

    if auth and auth.startswith(
        "Bearer "
    ):

        token = auth.removeprefix(
            "Bearer "
        )

        try:

            payload = verify_token(
                token
            )

            user_id = payload.get("sub")

            if user_id:
                return str(user_id)

        except Exception:
            #
            # Invalid token.
            #
            pass

    #
    # Fallback.
    #
    return (
        request.client.host
        if request.client
        else "anonymous"
    )


limiter = Limiter(
    key_func=get_rate_limit_key,
)