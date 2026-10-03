import aiosqlite
import asyncio

db_path = 'bot.db'

table_quiz  = 'CREATE TABLE IF NOT EXISTS quizzes ' \
'(id INTEGER PRIMARY KEY, ' \
'title TEXT NOT NULL);'

table_quest = 'CREATE TABLE IF NOT EXISTS questions ' \
'(id INTEGER PRIMARY KEY, ' \
'quiz_id  INTEGER NOT NULL REFERENCES quizzes(id), ' \
'text TEXT NOT NULL, ' \
'sort_order INTEGER NOT NULL);'


table_answers = 'CREATE TABLE IF NOT EXISTS user_answers ' \
'(id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
'user_id INTEGER NOT NULL, ' \
'question_id INTEGER NOT NULL REFERENCES questions(id), ' \
'answer_text TEXT NOT NULL, ' \
'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'


async def init_db(tables: list):
    db = await aiosqlite.connect(db_path)
    await db.execute('PRAGMA journal_mode=WAL')
    await db.execute('PRAGMA busy_timeout=5000')
    for table in tables:
        await db.executescript(table)
        await db.commit()
    await db.close()


asyncio.run(init_db([table_quiz, table_quest, table_answers]))
