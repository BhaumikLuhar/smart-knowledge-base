from storage.sql.sql_store import SQLStore

from core.config import settings


class SessionMemory:
    """
    Conversation memory service.

    Responsibilities
    ----------------
    - Retrieve recent conversation history
    - Format history for the LLM
    - Enforce the maximum number of sessions
      retained per user

    Session creation and ownership validation
    remain the responsibility of SessionService.
    """

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    
    async def get_session_history(
            self,
            session_id: str,
            limit: int = 6,
    )-> list[dict]:
        """
        Return the most recent conversation messages
        in chronological order.

        The returned structure matches the OpenAI
        chat completion message format.

        Example

        [
            {
                "role": "user",
                "content": "What is the leave policy?"
            },
            {
                "role": "assistant",
                "content": "Employees receive..."
            }
        ]
        """

        sql = """
        SELECT role, content
        FROM messages
        WHERE session_id = $1
        ORDER BY created_at DESC
        LIMIT $2;
        """

        rows = await self.sql_store.execute_raw(
            sql,
            (session_id, limit),
        )

        rows.reverse()

        return [
            {
                "role": row["role"],
                "content": row["content"],
            }
            for row in rows
        ]
    

    async def enforce_session_limit(
            self,
            user_id: str,
    )-> None:
        """
        Ensure a user does not exceed the maximum
        allowed number of sessions.

        If the limit has already been reached,
        the oldest session (and its messages)
        is deleted before a new session is created.
        """

        sql = """
        SELECT id
        FROM sessions
        WHERE user_id = $1
        ORDER BY created_at ASC
        """

        sessions = await self.sql_store.execute_raw(
            sql,
            (user_id,),
        )

        #
        # Still below the configured limit.
        #
        if len(sessions) < settings.MAX_SESSIONS:
            return
        
        oldest_session_id = sessions[0]["id"]

        #
        # Delete conversation first.
        #
        await self.sql_store.execute_raw(
            """
            DELETE FROM messages
            WHERE session_id = $1;
            """,
            (oldest_session_id,),
        )

        #
        # Delete session.
        #
        await self.sql_store.delete(
            "sessions",
            oldest_session_id,
        )