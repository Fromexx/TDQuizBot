from DB.db import Table, AnswerColumn

def texter(index: int, data: list, name: (str | None) = None, ):
    if name is not None:
        return f"Вы начали опрос {name}\n{'-'*20}\nВопрос {index+1}/{len(data)}:\n{data[index]}"
    return f'Вопрос {index+1}/{len(data)}:\n{data[index]}'


async def isUser(base, questions_ids: list, user_id: int):
    ids_dict = await base.get_all(Table.USER_ANSWERS, [AnswerColumn.USER_ID, AnswerColumn.QUESTION_ID])
    us_qu_id = [row[AnswerColumn.QUESTION_ID] for row in ids_dict if row[AnswerColumn.USER_ID]==user_id]
    return set(questions_ids).issubset(set(us_qu_id))