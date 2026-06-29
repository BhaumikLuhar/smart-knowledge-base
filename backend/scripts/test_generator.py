from core.generation.generator import Generator
from core.auth.user_context import UserContext

chunks = [
    {
        "document_name": "Employee Handbook",
        "page_number": 4,
        "chunk_index": 1,
        "department_id": "hr",
        "text": "Annual leave is 20 days.",
        "score": 5.8,
    }
]

user = UserContext(
    id="1",
    email="test@test.com",
    role="employee",
    department_id="hr",
    is_active=True,
)

response = Generator().generate_response(
    "How much annual leave do employees get?",
    chunks,
    user,
)

print(response.model_dump())