from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
from config import ADMIN_TELEGRAM_ID
from requests import get_users_by_course, get_students_by_course_and_direction, get_users_by_group_id
from run import get_bot

router_a = Router()

class TextForKurs(StatesGroup):
    kurs = State()
    text = State()
    
class TextForPotok(StatesGroup):
    kurs = State()
    potok_id = State()
    text = State()
    
class TextForGroup(StatesGroup):
    kurs = State()
    potok_id = State()
    group_id = State()    
    text = State()       

@router_a.message(Command("commands"))
async def Cmd_commands(message: Message):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Привет 👋🏼,\nЯ - чат-бот \n\n'
                             f'Через меня можно написать ?сообщение?: \n\n'
                             f'• Курсу\n\n'
                             f'• Потоку\n\n'
                             f'• Или конкретной группе\n\n')
        await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu_a())
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

# Работа для написания текста Курсу
@router_a.message(F.text == '📖 Курс')
async def Kurs(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Выберите курс которому вы бы хотели написать', reply_markup=await kb.kurs())  
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("kurs.number_"))
async def Kurs_bottons_act(query: CallbackQuery, state: FSMContext):
    kurs_id = int(query.data.split("_")[1])
    await state.update_data(kurs=kurs_id) 
    await query.message.answer(f'Введите сообщение для Курса')     
    await state.set_state(TextForKurs.text)     
    
@router_a.message(TextForKurs.text)
async def Kurs_text_act(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    kurs_id = data["kurs"]    
    await message.answer(data["text"], reply_markup=await kb.ready_kurs(kurs_id))  
    
@router_a.callback_query(F.data.startswith("kurs.ready_"))
async def Kurs_ready_act(query: CallbackQuery, state: FSMContext):
    kurs_id = int(query.data.split("_")[1])
    data = await state.get_data()
    message_text = data["text"]
    users = await get_users_by_course(kurs_id)
    if users:
            for user in users:
                await send_message_to_user(user.telegram_id, message_text)
            await query.message.answer("Сообщение успешно отправлено всем пользователям курса")
    else:
            await query.message.answer("На выбранный курс не подписан ни один пользователь")
    await state.clear()

# Работа для написания текста Потоку
@router_a.message(F.text == '🎓 Поток')
async def Potok(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Чтобы выбрать поток, выберите курс', reply_markup=await kb.potok_kurs())  
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("potok.kurs.number_"))
async def Potok_bottons_act(query: CallbackQuery, state: FSMContext):
    kurs_id = int(query.data.split("_")[1])
    await state.update_data(kurs=kurs_id)        
    await query.message.answer(f'Выберете поток', reply_markup=await kb.direction_for_curs(kurs_id))          

@router_a.callback_query(F.data.startswith("potok.direction_"))
async def Potok_text_act(query: CallbackQuery, state: FSMContext):
    potok = int(query.data.split("_")[1])
    await state.update_data(potok_id=potok)       
    await query.message.answer(f'Введите сообщение для Потока')
    await state.set_state(TextForPotok.text)    

@router_a.message(TextForPotok.text)
async def Kurs_text_act(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    potok_id = data["potok_id"]  
    await message.answer(data['text'], reply_markup=await kb.ready_direction(potok_id))   

@router_a.callback_query(F.data.startswith("potok.ready_"))
async def Potok_ready_act(query: CallbackQuery, state: FSMContext):
    potok_id = int(query.data.split("_")[1])
    data = await state.get_data()
    message_text = data["text"]
    course_id = data["kurs"]
    users = await get_students_by_course_and_direction(course_id, potok_id)
    if users:
        for user in users:
            await send_message_to_user(user.telegram_id, message_text)
        await query.message.answer("Сообщение успешно отправлено всем пользователям потока")
    else:
        await query.message.answer("На выбранный курс не подписан ни один пользователь")
    await state.clear()

# Работа для написания текста Группе
@router_a.message(F.text == '📚 Группа')
async def Group(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Чтобы выбрать группу, выберите курс', reply_markup=await kb.kurs_group())  
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("group.number_"))
async def Group_bottons_act(query: CallbackQuery, state: FSMContext):
    kurs_id = int(query.data.split("_")[1])
    await state.update_data(kurs=kurs_id)        
    await query.message.answer(f'Выберете поток', reply_markup=await kb.group_direction_for_curs(kurs_id)) 

@router_a.callback_query(F.data.startswith("group.direction_"))
async def Group_2bot_act(query: CallbackQuery, state: FSMContext):
    potok = int(query.data.split("_")[1])
    await state.update_data(potok_id=potok) 
    data = await state.get_data()
    kurs = data["kurs"]      
    await query.message.answer(f'Выберете группу', reply_markup=await kb.generate_group_keyboard(kurs, potok))     
    
@router_a.callback_query(F.data.startswith("group.group_"))
async def Group_text_act(query: CallbackQuery, state: FSMContext):
    group_id = int(query.data.split("_")[1])
    await state.update_data(group_id=group_id)       
    await query.message.answer(f'Введите сообщение для Группы')
    await state.set_state(TextForGroup.text)    

@router_a.message(TextForGroup.text)
async def Group_text_do(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    group_id = data["group_id"]  
    await message.answer(data['text'], reply_markup=await kb.ready_group(group_id))   

@router_a.callback_query(F.data.startswith("group.ready_"))
async def Group_ready_act(query: CallbackQuery, state: FSMContext):
    group_id = int(query.data.split("_")[1])
    data = await state.get_data()
    message_text = data["text"]
    users = await get_users_by_group_id(group_id)
    if users:
        for user in users:
            await send_message_to_user(user.telegram_id, message_text)
        await query.message.answer("Сообщение успешно отправлено всем пользователям группы")
    else:
        await query.message.answer("На выбранный курс не подписан ни один пользователь")
    await state.clear()
        
# Функция отправки сообщения пользователю
async def send_message_to_user(user_id, message_text):
    bot = await get_bot()
    try:
        await bot.send_message(user_id, message_text)
        return True  
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю с ID {user_id}: {e}")
        return False   