import json

from storage.sql.sql_store import SQLStore

from core.memory.session_memory import SessionMemory

from fastapi import HTTPException


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
        self.memory = SessionMemory(sql_store)

    async def create_session(
        self,
        user_id: str,
    ) -> dict:
        """
        Create a new chat session.
        """

        #
        # Ensure the user stays within the
        # configured session limit before
        # creating a new session.
        #
        await self.memory.enforce_session_limit(
            user_id=user_id,
        )


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

            if session is None:
                raise HTTPException(
                    status_code=403,
                    detail="Session does not belong to the current user.",
                )

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
    


    async def list_sessions(
        self,
        user_id: str,
    ) -> list[dict]:
        """
        Return all chat sessions for the current user,
        ordered by most recently active first.

        Each session includes the latest message preview
        so the frontend can render the sidebar.
        """

        return await self.sql_store.execute_raw(
            """
            SELECT
                s.id,
                s.created_at,
                s.last_active,

                lm.role AS last_message_role,
                lm.content AS last_message,

                lm.created_at AS last_message_at

            FROM sessions s

            LEFT JOIN LATERAL (
                SELECT
                    role,
                    content,
                    created_at
                FROM messages
                WHERE session_id = s.id
                ORDER BY created_at DESC
                LIMIT 1
            ) lm ON TRUE

            WHERE s.user_id = $1

            ORDER BY s.last_active DESC
            """,
            (user_id,),
        )
    


    async def get_session_messages(
        self,
        session_id: str,
        user_id: str,
    ) -> list[dict]:
        """
        Return every message belonging to a session.

        Ownership is verified before messages
        are returned.
        """

        session = await self.get_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Session does not belong "
                    "to the current user."
                ),
            )

        messages = await self.sql_store.execute_raw(
            """
            SELECT
                id,
                role,
                content,
                metadata,
                created_at
            FROM messages
            WHERE session_id = $1
            ORDER BY created_at ASC
            """,
            (session_id,),
        )

        #
        # SQLStore currently returns JSON fields as strings.
        # Convert metadata back into dictionaries so the
        # response matches the Pydantic schema.
        #
        for message in messages:
            metadata = message.get("metadata")

            if isinstance(metadata, str):
                try:
                    message["metadata"] = json.loads(metadata)
                except json.JSONDecodeError:
                    message["metadata"] = {}

        return messages