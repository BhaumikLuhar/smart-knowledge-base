from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    department_id: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    department_id: str | None = None
    role: str


class UpdateUserRequest(BaseModel):
    role: str | None = None
    department_id: str | None = None
    is_active: bool | None = None



class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str