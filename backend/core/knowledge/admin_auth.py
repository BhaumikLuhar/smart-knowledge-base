from fastapi import Header, HTTPException


async def verify_admin_token(
    x_admin_token: str | None = Header(default=None)
):
    """
    Temporary admin protection.

    Day 8:
    Replace with JWT authentication.
    """

    if x_admin_token != "dev-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )