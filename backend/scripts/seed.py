import asyncio
import asyncpg

from core.config import settings
from core.auth.password import hash_password


ADMIN_EMAIL = "admin@skb.local"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "System Administrator"


async def seed():

    conn = await asyncpg.connect(
        settings.DATABASE_URL,
        ssl="require"
    )

    try:

        print("🌱 Starting seed...")

        departments = {}

        dept_rows = await conn.fetch(
            """
            SELECT id, name
            FROM departments
            """
        )

        for row in dept_rows:
            departments[row["name"]] = row["id"]

        print(
            f"✅ Found {len(departments)} departments"
        )

        existing_admin = await conn.fetchrow(
            """
            SELECT id
            FROM users
            WHERE email = $1
            """,
            ADMIN_EMAIL
        )

        if not existing_admin:

            admin_id = await conn.fetchval(
                """
                INSERT INTO users (
                    email,
                    hashed_password,
                    full_name,
                    role,
                    department_id
                )
                VALUES (
                    $1,
                    $2,
                    $3,
                    'admin',
                    NULL
                )
                RETURNING id
                """,
                ADMIN_EMAIL,
                hash_password(
                    ADMIN_PASSWORD
                ),
                ADMIN_NAME,
            )

            print(
                f"✅ Admin user created: {admin_id}"
            )

        else:

            print(
                "⏭ Admin user already exists"
            )

        permission_rows = [

            (
                "employee",
                departments["engineering"],
                departments["engineering"]
            ),

            (
                "employee",
                departments["engineering"],
                departments["public"]
            ),

            (
                "employee",
                departments["hr"],
                departments["hr"]
            ),

            (
                "employee",
                departments["hr"],
                departments["public"]
            ),

        ]

        for role, dept_id, access_id in permission_rows:

            await conn.execute(
                """
                INSERT INTO permissions (
                    role,
                    department_id,
                    can_access_department_id
                )
                VALUES (
                    $1,
                    $2,
                    $3
                )
                ON CONFLICT (
                    role,
                    department_id,
                    can_access_department_id
                )
                DO NOTHING
                """,
                role,
                dept_id,
                access_id
            )

        print(
            "✅ Permission rules seeded"
        )

        print(
            "\n🎉 Seed completed successfully"
        )

        print(
            f"\nAdmin Email: {ADMIN_EMAIL}"
        )

        print(
            f"Admin Password: {ADMIN_PASSWORD}"
        )

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())