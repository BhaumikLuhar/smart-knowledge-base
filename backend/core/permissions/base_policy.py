from abc import ABC, abstractmethod

from core.auth.user_context import UserContext


class PermissionPolicy(ABC):
    """
    Base class for permission policies.
    """

    @abstractmethod
    async def get_allowed_departments(self, user: UserContext) -> list[str]:
        """
        Return a list of department IDs that the user is allowed to access.
        """
        pass


    @abstractmethod
    async def get_allowed_visibilities(self, user: UserContext) -> list[str]:
        """
        Return a list of visibilities that the user is allowed to access.
        """
        pass


    @abstractmethod
    async def can_access_document(self, user: UserContext, doc_metadata: dict) -> bool:
        """
        Final authorization check.
        """
        pass