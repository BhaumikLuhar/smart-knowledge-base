from storage.sql.sql_store import SQLStore

from core.auth.user_context import UserContext

from core.permissions.base_policy import PermissionPolicy


class DepartmentPermissionPolicy(PermissionPolicy):

    def __init__(self, sql_store: SQLStore):
        self.sql_store = sql_store

    async def get_public_department_id(self) -> str:

        public_departments = await self.sql_store.query(
            "departments",
            {
                "name": "public"
            }
        )

        if not public_departments:
            raise Exception("Public department not found")

        return str(public_departments[0]["id"])
    

    async def get_allowed_departments(self, user_context: UserContext) -> list[str]:

        if user_context.role == "admin":
            departments = await self.sql_store.query(
                "departments",
                {}
            )

            return [str(dept["id"]) for dept in departments]
        

        allowed_departments = set()

        if user_context.department_id:
            allowed_departments.add(str(user_context.department_id))
    
        public_department_id = await self.get_public_department_id()

        if public_department_id:
            allowed_departments.add(str(public_department_id))

        permission_rows = await self.sql_store.query(
            "permissions",
            {
                "role": user_context.role,
                "department_id": user_context.department_id
            }
        )

        for row in permission_rows:
            allowed_departments.add(str(row["can_access_department_id"]))

        return list(allowed_departments)
    

    async def get_allowed_visibilities(self, user_context: UserContext) -> list[str]:

        if user_context.role == "admin":
            return ["public", "department", "restricted"]

        return ["public", "department"]
    

    async def can_access_document(self, user_context: UserContext, doc_metadata: dict) -> bool:

        allowed_departments = await self.get_allowed_departments(user_context)

        allowed_visibilities = await self.get_allowed_visibilities(user_context)

        department_id = doc_metadata.get(
            "department_id"
        )

        visibility = doc_metadata.get(
            "visibility"
        )

        if department_id is None:
            return False

        if visibility is None:
            return False

        department_allowed = (
            str(department_id)
            in allowed_departments
        )

        visibility_allowed = (
            visibility
            in allowed_visibilities
        )

        return department_allowed and visibility_allowed