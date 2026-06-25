import asyncio

from core.database import create_db_pool

from storage.sql.sql_store import SQLStore

from core.auth.user_context import UserContext

from core.permissions.base_policy import (
    PermissionPolicy
)

from core.permissions.registry import (
    register_permission_policy,
    get_policy
)


class NullPolicy(PermissionPolicy):

    def __init__(self, sql_store):
        self.sql_store = sql_store

    async def get_allowed_departments(
        self,
        user_context
    ):
        return ["*"]

    async def get_allowed_visibilities(
        self,
        user_context
    ):
        return [
            "public",
            "department",
            "restricted"
        ]

    async def can_access_document(
        self,
        user_context,
        doc_metadata
    ):
        return True


async def main():

    pool = await create_db_pool()

    sql_store = SQLStore(pool)

    register_permission_policy(
        "null",
        NullPolicy
    )

    policy = get_policy(
        sql_store,
        "null"
    )

    user = UserContext(
        id="1",
        email="test@test.com",
        role="employee",
        department_id="dept",
        is_active=True
    )

    print(
        await policy.get_allowed_departments(
            user
        )
    )

    print(
        await policy.get_allowed_visibilities(
            user
        )
    )

    print(
        await policy.can_access_document(
            user,
            {}
        )
    )

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())