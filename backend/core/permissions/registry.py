from core.permissions.base_policy import PermissionPolicy
from core.permissions.department_policy import DepartmentPermissionPolicy
from typing import Type

POLICY_REGISTRY: dict[str, Type] = {}


def register_permission_policy(name: str, policy_class: Type)-> None:
    """
    Register a permission policy class with a given name.
    """
    POLICY_REGISTRY[name] = policy_class


def get_policy(sql_store, name: str = "department")-> PermissionPolicy:
    """
    Retrieve a permission policy instance by name.
    """

    policy_class = POLICY_REGISTRY.get(name,DepartmentPermissionPolicy)

    if not policy_class:
        raise ValueError(f"Permission policy '{name}' is not registered.")

    return policy_class(sql_store)


register_permission_policy("department", DepartmentPermissionPolicy)