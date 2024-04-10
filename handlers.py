from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router_u = Router()

import keyboards as kb
from requests import is_user_registered_db, save_new_user, get_user_data, get_group_info_by_id, get_user_info_by_telegram_id

class AddNewUser(StatesGroup):
    kurs = State()
    direction = State()
    group = State()
    telegram_id = State()

@router_u.message(CommandStart())
async def Cmd_start(message: Message):
    user_id = message.from_user.id
    await message.answer(f'Привет 👋🏼,\nЯ - чат-бот \n\n'
                             f'Я могу показать: \n\n'
                             f'• \n\n')
    await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu_u(user_id))

@router_u.message(F.text == '📌 Регистрация')
async def Cmd_register(message: Message, state: FSMContext) -> None: 
    user_id = message.from_user.id
    if await is_user_registered_db(user_id):
        await message.answer("Вы уже зарегистрированы.")
    else:
        await state.update_data(telegram_id=user_id)
        await message.answer("Выберете свой курс", reply_markup=await kb.kurs_registration())
        
@router_u.callback_query(F.data.startswith("reg.kurs.number_"))
async def Process_kurs(query: CallbackQuery, state: FSMContext):
    kurs = int(query.data.split("_")[1])
    await state.update_data(kurs=kurs)
    await query.message.answer("Выберете своё направление", reply_markup=await kb.directions())

@router_u.callback_query(F.data.startswith("reg.direction_"))
async def Process_direction(query: CallbackQuery, state: FSMContext):
    direction_id = int(query.data.split("_")[1])
    await state.update_data(direction=direction_id)
    
    data = await state.get_data()
    course_id = data["kurs"]
    
    await query.message.answer("Выберете свою группу", reply_markup=await kb.group(course_id , direction_id))

@router_u.callback_query(F.data.startswith("reg.group_"))
async def Process_group(query: CallbackQuery, state: FSMContext):
    group = int(query.data.split("_")[1])
    data = await state.get_data()
    
    result, text = await save_new_user(data["telegram_id"], data["kurs"], data["direction"], group)
    
    message_text = text
    
    if result is True:
        group_name, direction_name, course_name = await get_group_info_by_id(group)
        message_text += (
            f"\n\nСпасибо за регистрацию!\n\n"
            f"Курс: <b>{course_name}</b>\n"
            f"Направление: <b>{direction_name}</b>\n"
            f"Группа: <b>{group_name}</b>\n")

    await query.message.answer(message_text)
    await query.message.answer(f'🔮 Главное меню', reply_markup=await kb.menu_u(data['telegram_id']))

@router_u.message(F.text == '📋 Моя анкета')
async def view_profile(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_info_by_telegram_id(user_id)
    if user_data:
        group_name, direction_name, course_name = user_data
        profile_text = (
            f"📋 Ваша анкета:\n\n"
            f"Курс: <b>{course_name}</b>\n"
            f"Направление: <b>{direction_name}</b>\n"
            f"Группа: <b>{group_name}</b>\n")
        await message.answer(profile_text, reply_markup=await kb.menu_u(user_id))
    else:
        await message.answer("Ваша анкета не найдена. Возможно, вы еще не зарегистрированы.", reply_markup=await kb.menu_u(user_id))