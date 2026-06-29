import asyncio

from core.database import create_db_pool
from storage.sql.sql_store import SQLStore

from core.chat.session_service import SessionService


USER_ID = "edbf7259-9ac7-4c71-9ee9-afdfd682b4b7"


async def main():

    pool = await create_db_pool()

    sql_store = SQLStore(pool)

    service = SessionService(sql_store)

    session = await service.create_session(USER_ID)

    print(session)

    await asyncio.sleep(3)

    updated = await service.get_session(
        session["id"],
        USER_ID,
    )

    print(updated)

    session = await service.get_or_create_session(
        session["id"],
        USER_ID,
    )

    print(session)

    await pool.close()


asyncio.run(main())