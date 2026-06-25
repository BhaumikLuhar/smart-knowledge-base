import asyncio

from storage.sql.sql_store import SQLStore

from core.database import create_db_pool

from core.auth.user_context import UserContext

from core.permissions.permission_service import (
    PermissionService
)


async def main():

    pool = await create_db_pool()

    sql_store = SQLStore(pool)

    permission_service = PermissionService(
        sql_store
    )

    departments = await sql_store.query(
        "departments"
    )

    department_map = {
        row["name"]: str(row["id"])
        for row in departments
    }

    print("\n========================")
    print("DEPARTMENTS")
    print("========================")

    for name, dept_id in department_map.items():
        print(name, "->", dept_id)

    hr_user = UserContext(
        id="test-hr",
        email="hr@test.com",
        role="employee",
        department_id=department_map["hr"],
        is_active=True
    )

    engineering_user = UserContext(
        id="test-eng",
        email="eng@test.com",
        role="employee",
        department_id=department_map["engineering"],
        is_active=True
    )

    engineering_manager = UserContext(
        id="test-manager",
        email="manager@test.com",
        role="manager",
        department_id=department_map["engineering"],
        is_active=True
    )

    admin_user = UserContext(
        id="test-admin",
        email="admin@test.com",
        role="admin",
        department_id=None,
        is_active=True
    )

    print("\n========================")
    print("HR EMPLOYEE")
    print("========================")

    allowed = await (
        permission_service.policy
        .get_allowed_departments(
            hr_user
        )
    )

    print("Allowed departments:")
    print(allowed)

    print("\n========================")
    print("ENGINEERING EMPLOYEE")
    print("========================")

    allowed = await (
        permission_service.policy
        .get_allowed_departments(
            engineering_user
        )
    )

    print("Allowed departments:")
    print(allowed)

    print("\n========================")
    print("ENGINEERING MANAGER")
    print("========================")

    allowed = await (
        permission_service.policy
        .get_allowed_departments(
            engineering_manager
        )
    )

    print("Allowed departments:")
    print(allowed)

    print("\n========================")
    print("ADMIN")
    print("========================")

    allowed = await (
        permission_service.policy
        .get_allowed_departments(
            admin_user
        )
    )

    print("Allowed departments:")
    print(allowed)

    hr_document = {
        "department_id":
            department_map["hr"],
        "visibility":
            "department"
    }

    restricted_hr_document = {
        "department_id":
            department_map["hr"],
        "visibility":
            "restricted"
    }

    print("\n========================")
    print("DOCUMENT ACCESS TESTS")
    print("========================")

    result = await (
        permission_service.policy
        .can_access_document(
            hr_user,
            hr_document
        )
    )

    print(
        "HR employee -> HR document:",
        result
    )

    result = await (
        permission_service.policy
        .can_access_document(
            engineering_user,
            hr_document
        )
    )

    print(
        "Engineering employee -> HR document:",
        result
    )

    result = await (
        permission_service.policy
        .can_access_document(
            hr_user,
            restricted_hr_document
        )
    )

    print(
        "HR employee -> restricted HR document:",
        result
    )

    result = await (
        permission_service.policy
        .can_access_document(
            admin_user,
            restricted_hr_document
        )
    )

    print(
        "Admin -> restricted HR document:",
        result
    )

    print("\n========================")
    print("CHROMA FILTER TEST")
    print("========================")

    filters = await (
        permission_service
        .get_user_context_filters(
            hr_user
        )
    )

    print(filters)

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())