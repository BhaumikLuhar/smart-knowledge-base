from core.permissions.base_policy import PermissionPolicy
from core.permissions.department_policy import DepartmentPermissionPolicy
from typing import Type

POLICY_REGISTRY: dict[str, Type] = {}

_ACTIVE_POLICY = "department"


def register_permission_policy(name: str, policy_class: Type)-> None:
    """
    Register a permission policy class with a given name.
    """
    POLICY_REGISTRY[name] = policy_class


def get_policy(sql_store, name: str | None = None)-> PermissionPolicy:
    """
    Retrieve a permission policy instance by name.
    """

    selected = name or _ACTIVE_POLICY
    policy_class = POLICY_REGISTRY.get(selected, DepartmentPermissionPolicy)

    if not policy_class:
        raise ValueError(f"Permission policy '{name}' is not registered.")

    return policy_class(sql_store)

def inject_permission_policy(name: str) -> None:
    """
    Activate a registered permission policy.
    """

    if name not in POLICY_REGISTRY:
        raise ValueError(
            f"Permission policy '{name}' is not registered."
        )

    global _ACTIVE_POLICY
    _ACTIVE_POLICY = name


def reset_permission_policy() -> None:
    """
    Restore the default department policy.
    """

    global _ACTIVE_POLICY
    _ACTIVE_POLICY = "department"



register_permission_policy("department", DepartmentPermissionPolicy)