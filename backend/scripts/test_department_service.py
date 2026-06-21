from core.knowledge.department_service import DepartmentService
from storage.sql.sql_store import SQLStore
import asyncio
from core.config import settings
import asyncpg



async def test_list_departments():

    pool = await asyncpg.create_pool(
        settings.DATABASE_URL,ssl="require",statement_cache_size=0
    )

    store= SQLStore(pool)
    service = DepartmentService(store)

    departments = await service.list_departments()

    await service.create_department(
        name="legal",
        display_name="Legal"
    )

    # await service.create_department(
    #     name="Human Resources",
    #     display_name="HR"
    # )

    print(departments)

asyncio.run(test_list_departments())