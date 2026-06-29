from storage.sql.sql_store import SQLStore


class SessionService:
    """
    Handles chat session lifecycle.

    Responsibilities
    ----------------
    - Create sessions
    - Validate ownership
    - Update last activity

    Future (Day 14+)
    ----------------
    - List sessions
    - Delete sessions
    - Rename sessions
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    async def create_session(
        self,
        user_id: str,
    ) -> dict:
        """
        Create a new chat session.
        """

        return await self.sql_store.save(
            "sessions",
            {
                "user_id": user_id,
            },
        )

    async def get_session(
        self,
        session_id: str,
        user_id: str,
    ) -> dict | None:
        """
        Return a session only if it belongs
        to the current user.
        """

        sessions = await self.sql_store.query(
            "sessions",
            {
                "id": session_id,
                "user_id": user_id,
            },
        )

        if not sessions:
            return None

        return sessions[0]

    async def get_or_create_session(
        self,
        session_id: str | None,
        user_id: str,
    ) -> dict:
        """
        Reuse an existing session or create
        a new one.
        """

        if session_id:

            session = await self.get_session(
                session_id=session_id,
                user_id=user_id,
            )

            if session is not None:

                return await self.touch_session(
                    session["id"]
                ) 

        return await self.create_session(user_id)

    async def touch_session(
        self,
        session_id: str,
    ) -> dict:
        """
        Update last activity timestamp.
        Returns the updated session.
        """

        return await self.sql_store.update(
            "sessions",
            session_id,
            {
                "last_active": "NOW()",
            },
        )