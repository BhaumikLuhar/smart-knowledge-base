from dataclasses import dataclass


@dataclass
class UserContext:
    id: str
    email: str
    role: str
    department_id: str | None
    is_active: bool