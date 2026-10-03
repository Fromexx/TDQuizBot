from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext  # хранилище данных и текущего состояния пользователя
from aiogram.fsm.state import State, StatesGroup  # State - одно состояние, StatesGroup — группа состояний
import random

router = Router()

class NewPol(StatesGroup):
    # StatesGroup — это "контейнер" состояний диалога.
    # Каждый атрибут-класса (in_progress) - это отдельное состояние.
    # Аналогия: enum/константы, но aiogram сам регистрирует их в диспетчере.
    # StatesGroup - машина состояний для конкретного сценария
    in_progress = State()


@router.message(Command('new'))
async def start(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer('Введите название опроса')
        return
    # Переводим пользователя в состояние NewPol.in_progress.
    # Пока он в нём - сработают только хендлеры, которые явно ждут это состояние.
    await state.set_state(NewPol.in_progress)
    # FSMContext — это key-value хранилище, привязанное к пользователю/чату.
    # update_data мержит переданные поля с уже сохранёнными (не перезаписывает словарь целиком).
    # name - имя опроса; -index - счётчик вопросов; answers - список; pol_id - рандомный ID опроса.
    # пока такие ключи в качестве тестов, но мб и для итогового результата сойдёт
    await state.update_data(name=command.args.strip().lower(), index=0, answers=[], pol_id=random.randint(10, 21))
    await message.answer('Начинаем создавать новый опрос. Присылай вопросы по порядку, пока не напишешь "стоп"')


@router.message(NewPol.in_progress, F.text)
# Первый аргумент фильтра — состояние. Это значит:
# хендлер вызовется ТОЛЬКО если у пользователя state == NewPol.in_progress.
# F.text - плюс фильтр «это текстовое сообщение».
# То есть, маршрутизация по текущему состоянию.
async def get_questions(message: Message, state: FSMContext):
    data = await state.get_data() # получения словаря состояния
    index = data['index']
    answers = data['answers']
    name = data['name']

    if message.text.strip().lower() == 'стоп':
        await state.clear()  # сбрасываем состояние в None + удаляем все данные
        await message.answer(f'Вопросы собраны:\n{answers}\nID опроса: {data['pol_id']}\nНазвание: {name}')
        return

    index += 1
    answers += [message.text]
    await state.update_data(index=index, answers=answers)
    await message.answer(f'Вопрос {index} собран!')
