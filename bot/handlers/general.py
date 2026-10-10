from aiogram import F, Router
from aiogram.filters import Command, CommandObject, Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from DB.db import DataBase, Table, QuizColumn, QuestionColumn, AnswerColumn
from bot.filters.filters import isPol
from bot.utils.utils import texter, isUser

router = Router()
base = DataBase()

COMMANDS = ['start', 'help', 'list', 'new', 'delete', 'clear', 'close']

class NewPol(StatesGroup):
    in_progress = State()

class StartPol(StatesGroup):
    in_progress = State()

@router.message(Command('start'))
async def start(message: Message):
    text = 'Здарова!\n/help\n/list'
    await message.answer(text)

@router.message(Command('help'))
async def help(message: Message):
    text = 'Здесь подробная инструкция'
    await message.answer(text)

@router.message(Command('list'))
async def show_list(message: Message):
    titles_dict = await base.get_all(Table.QUIZZES, [QuizColumn.TITLE, QuizColumn.ID])
    titles_list = [f'/{titles["title"]}  ID: {titles["id"]}' for titles in titles_dict]
    text = 'Список актуальных опросов:\n' + '\n'.join(titles_list)
    await message.answer(text)

@router.message(Command('delete'))
async def delete_from_db(message: Message, command: CommandObject):
    command_id = command.args
    if command_id is None:
        await message.answer('Напишите ID опроса!')
        return
    if (stripped := command_id.strip()).isdigit():
        info = await base.delete(Table.QUIZZES, int(stripped)) 
        await message.answer(f'Опрос [{stripped}] успешно удалён!'if info else f'Не удалось найти  опрос [{stripped}]. Проверьте ID!')

@router.message(Command('clear'))
async def clear_all(message: Message):
    all_tables = [Table.QUIZZES, Table.QUESTIONS, Table.USER_ANSWERS]
    for table in all_tables:
        await base.clear(table)
    await message.answer('БД полностью очищена')


@router.message(Command('close'))
async def close_db(message: Message):
    await base.close()
    await message.answer('БД закрыта для изменений')

@router.message(isPol())
async def starting_pol(message: Message, state: FSMContext, PolName: tuple[str, int]):
    QuizName = PolName[0]
    QuizRelatedID = PolName[1]
    data = await base.get_all_by_id(Table.QUESTIONS, QuestionColumn.QUIZ_ID, QuizRelatedID)
    questions = [q['text'] for q in data]
    questions_ids = [ids['id'] for ids in data]
    if await isUser(questions_ids, message.from_user.id):
        await message.answer('Вы уже проходили этот опрос')
        return
    await state.set_state(StartPol.in_progress)
    await state.update_data(index=0, questions=questions, questions_ids=questions_ids)
    await message.answer(texter(name=QuizName, index=0, data=questions))

@router.message(StartPol.in_progress, F.text)
async def get_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data['index']
    q_ids = data['questions_ids']
    questions = data['questions']
    answer = message.text.strip()
    await base.insert(Table.USER_ANSWERS, 
                      {AnswerColumn.USER_ID: message.from_user.id, 
                       AnswerColumn.QUESTION_ID: q_ids[index], AnswerColumn.ANSWER_TEXT: answer}
                      )
    
    if index == len(questions)-1:
            await state.clear()
            await message.answer('Опрос пройден!')
            return
    
    index += 1
    await message.answer(texter(index=index, data=questions))
    await state.update_data(index=index)

@router.message(Command('new'))
async def new(message: Message, command: CommandObject, state: FSMContext):
    pol_name = command.args
    if pol_name is None:
        await message.answer('Введите название опроса')
        return
    elif pol_name.strip().lower() in COMMANDS:
        await message.answer('Нельзя называть опросы служебными командами!')
        return
    titles_dict = await base.get_all(Table.QUIZZES, [QuizColumn.TITLE])
    titles_list = [titles['title'] for titles in titles_dict]
    if pol_name.strip().upper() in titles_list:
        await message.answer('Опрос с таким именем уже есть')
        return
    await state.set_state(NewPol.in_progress)
    quiz_id = await base.insert(Table.QUIZZES, {QuizColumn.TITLE: str(pol_name.strip().upper())})
    await state.update_data(name=pol_name.strip().upper(), index=0, answers=[], pol_id=quiz_id)
    await message.answer('Начинаем создавать новый опрос. Присылай вопросы по порядку, пока не напишешь "стоп"')

@router.message(NewPol.in_progress, F.text)
async def get_questions(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data['index']
    answers = data['answers']
    name = data['name']

    if message.text.strip().lower() == 'стоп':
        await state.clear()
        await message.answer(f'Вопросы собраны:\n{answers}\nНазвание: {name}')
        return

    answers += [message.text]
    await base.insert(Table.QUESTIONS, {QuestionColumn.TEXT: answers[index], QuestionColumn.SORT_ORDER: index, QuestionColumn.QUIZ_ID: data['pol_id']})
    index += 1
    await state.update_data(index=index, answers=answers)
    await message.answer(f'Вопрос {index} собран!')