from core.permissions.base_policy import PermissionPolicy

from core.permissions.registry import (
    register_permission_policy,
    inject_permission_policy,
    reset_permission_policy,
)


class AllowAllPolicy(PermissionPolicy):

    def __init__(self, sql_store):
        pass

    def get_allowed_departments(self, user):
        return ["*"]

    def get_allowed_visibilities(self, user):
        return [
            "public",
            "department",
            "restricted",
        ]

    def can_access_document(
        self,
        user,
        metadata,
    ):
        return True


register_permission_policy(
    "allow_all",
    AllowAllPolicy,
)

inject_permission_policy("allow_all")

print("✓ AllowAll policy injected")

reset_permission_policy()

print("✓ Permission registry restored")