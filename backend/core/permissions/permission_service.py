from storage.sql.sql_store import SQLStore

from core.auth.user_context import UserContext

from core.permissions.registry import get_policy


class PermissionService:

    def __init__(self, sql_store: SQLStore, policy_name: str = "department"):
        self.sql_store = sql_store
        self.policy = get_policy(sql_store, policy_name)


    async def get_allowed_departments(
        self,
        user_context: UserContext
    ) -> list[str]:
        return await self.policy.get_allowed_departments(
            user_context
        )


    async def get_allowed_visibilities(
        self,
        user_context: UserContext
    ) -> list[str]:
        return await self.policy.get_allowed_visibilities(
            user_context
        )


    async def get_user_context_filters(self,user_context: UserContext)-> dict:
        """
        Build Chroma metadata filter.

        Used BEFORE retrieval.
        """

        allowed_departments = await self.policy.get_allowed_departments(user_context)

        allowed_visibilities = await self.policy.get_allowed_visibilities(user_context)


        return {
            "$and": [
                {
                    "department_id": {
                        "$in": allowed_departments
                    }
                },
                {
                    "visibility": {
                        "$in": allowed_visibilities
                    }
                }
            ]
        }
    

    async def filter_chunks(
        self,
        user: UserContext,
        chunks: list[dict]
    ) -> list[dict]:
        """
        Secondary authorization layer.

        Permissions are loaded once per request,
        then all candidate chunks are validated
        in memory.
        """

        if not chunks:
            return []

        #
        # Load permissions once
        #
        allowed_departments = set(
            await self.policy.get_allowed_departments(user)
        )

        allowed_visibilities = set(
            await self.policy.get_allowed_visibilities(user)
        )

        authorized_chunks = []

        for chunk in chunks:

            department_allowed = (
                str(chunk.get("department_id"))
                in allowed_departments
            )

            visibility_allowed = (
                chunk.get("visibility")
                in allowed_visibilities
            )

            if department_allowed and visibility_allowed:
                authorized_chunks.append(chunk)
            else:
                await self.log_permission_denial(
                    user,
                    (
                        f"Chunk denied "
                        f"(department="
                        f"{chunk.get('department_id')}, "
                        f"visibility="
                        f"{chunk.get('visibility')})"
                    )
                )

        return authorized_chunks

    
    async def log_permission_denial(self, user: UserContext, reason: str)-> None:
        """
        Log permission denial.
        """

        await self.sql_store.save(
            "audit_logs",
            {
                "user_id": user.id,
                "action": "permission_denied",
                "details": {
                    "reason": reason,
                    "user_role": user.role,
                    "user_department":
                        user.department_id
                }
            }
        )