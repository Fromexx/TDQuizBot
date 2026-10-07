import aiosqlite
from enum import StrEnum
from Configs.DBConfig import DB_PATH

class Table(StrEnum):
    QUIZZES      = "quizzes"
    QUESTIONS    = "questions"
    USER_ANSWERS = "user_answers"

class Column(StrEnum):
    pass

class QuizColumn(Column):
    ID    = "id"
    TITLE = "title"

class QuestionColumn(Column):
    ID         = "id"
    QUIZ_ID    = "quiz_id"
    TEXT       = "text"
    SORT_ORDER = "sort_order"

class AnswerColumn(Column):
    ID          = "id"
    USER_ID     = "user_id"
    QUESTION_ID = "question_id"
    ANSWER_TEXT = "answer_text"
    CREATED_AT  = "created_at"


class DataBase:
    async def init(self, tables: list):
        self.__db = await aiosqlite.connect(DB_PATH)
        self.__db.row_factory = aiosqlite.Row
        await self.__db.execute('PRAGMA journal_mode=WAL')
        await self.__db.execute('PRAGMA busy_timeout=5000')
        await self.__db.execute('PRAGMA foreign_keys=ON')
        for table in tables:
            await self.__db.executescript(table)
            await self.__db.commit()

    async def insert(self, table: Table, values: dict[Column, object]):
        columns = list(values)
        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)})"
        )
        cursor = await self.__db.execute(sql, tuple(values.values()))
        await self.__db.commit()
        return cursor.lastrowid


    async def get_by_id(self, table: Table, row_id: int):
        cursor = await self.__db.execute(
            f"SELECT * FROM {table} WHERE id = ?",
            (row_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    # ищем всё по конкретному id
    async def get_all_by_id(self, table: Table, PoleId: Column, row_id: int):
        cursor = await self.__db.execute(
            f"SELECT * FROM {table} WHERE {PoleId} = ?",
            (row_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

    # ищем всё по выбранным полям
    async def get_all(self, table: Table, fields: list[Column]):
        cursor = await self.__db.execute(
            f"SELECT {', '.join(list(fields))} FROM {table}"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []
        

    # async def get_by_command(self, table: Table, command: str)
        

    async def delete(self, table: Table, row_id: int):
        cursor = await self.__db.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        await self.__db.commit()
        return cursor.rowcount

    async def clear(self, table: Table):
        await self.__db.execute(f"DELETE FROM {table}")
        await self.__db.commit()

    async def close(self):
        await self.__db.close()

# asyncio.run(dataBase)
