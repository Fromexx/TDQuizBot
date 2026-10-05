import asyncio

from db import (
    DataBase,
    Table, QuizColumn, QuestionColumn, AnswerColumn,
    table_quiz, table_quest, table_answers)

async def main():
    db = DataBase()
    await db.init([table_quiz, table_quest, table_answers])
    try:
        # ---------- insert ----------
        quiz_id = await db.insert(Table.QUIZZES, {QuizColumn.TITLE: "Python"})
        assert quiz_id == 1, f"ожидал 1, получил {quiz_id}"
        print("PASS insert returns id")

        # ---------- insert many ----------
        id2 = await db.insert(Table.QUIZZES, {QuizColumn.TITLE: "Go"})
        assert id2 == 2, f"ожидал 2, получил {id2}"
        print("PASS insert second")

        # ---------- get by id ----------
        row = await db.get_by_id(Table.QUIZZES, quiz_id)
        assert row is not None, "строка не найдена"
        assert row["title"] == "Python", f"title={row['title']}"
        assert row["id"] == quiz_id
        print("PASS get_by_id returns row")

        # ---------- get missing ----------
        missing = await db.get_by_id(Table.QUIZZES, 999)
        assert missing is None, f"ожидал None, получил {missing}"
        print("PASS get_by_id missing None")

        # ---------- связь question → quiz ----------
        q_id = await db.insert(Table.QUESTIONS, {
            QuestionColumn.QUIZ_ID: quiz_id,
            QuestionColumn.TEXT: "Что такое GIL?",
            QuestionColumn.SORT_ORDER: 1,
        })
        q = await db.get_by_id(Table.QUESTIONS, q_id)
        assert q["quiz_id"] == quiz_id, f"quiz_id={q['quiz_id']}"
        assert q["text"] == "Что такое GIL?"
        print("PASS question linked to quiz")

        # ---------- FK работает ----------
        try:
            await db.insert(Table.QUESTIONS, {
                QuestionColumn.QUIZ_ID: 999,
                QuestionColumn.TEXT: "orphan",
                QuestionColumn.SORT_ORDER: 1,
            })
            raise AssertionError("ожидал ошибку FK, но вставка прошла")
        except AssertionError:
            raise
        except Exception:
            print("PASS foreign key blocks orphan")

        # ---------- delete ----------
        cnt = await db.delete(Table.QUIZZES, quiz_id)
        assert cnt == 1, f"удалил {cnt} строк"
        assert await db.get_by_id(Table.QUIZZES, quiz_id) is None
        print("PASS delete removes row")

        # ---------- delete missing ----------
        cnt = await db.delete(Table.QUIZZES, 999)
        assert cnt == 0, f"ожидал 0, получил {cnt}"
        print("PASS delete missing 0")

        # ---------- clear ----------
        await db.clear(Table.QUIZZES)
        assert await db.get_by_id(Table.QUIZZES, id2) is None
        print("PASS clear removes all")

        print("\nall tests passed")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())