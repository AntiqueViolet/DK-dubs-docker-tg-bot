import logging
import mariadb
import sys
import logins
from aiogram import F
import asyncio
from aiogram.types.input_file import FSInputFile
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.types import Message
import re
import shutil
import time
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class DialogStates(StatesGroup):
    waiting_for_input = State()
    waiting_for_login = State()
    waiting_for_command_data = State()
    waiting_for_org_name = State()
    waiting_for_date_start = State()
    waiting_for_date_end = State()
    waiting_for_input_dk = State()
    waiting_for_input_vin = State()
    waiting_for_input_rn = State()
    waiting_for_input_kr = State()


bot = Bot(token=config.API_TOKEN)
dp = Dispatcher()
ids = []
dict = {}

dynamic_router = Router()
dp.include_router(dynamic_router)


@dp.message(Command("tech_1"))
async def send_tech_1(message: types.Message):
    if message.from_user.id != config.SUPER_ADMIN_ID:
        await message.reply("Это админ команда")
    else:
        for admin_id in config.ADMIN_IDS:
            await bot.send_message(chat_id=admin_id, text="Бот на тех. обслуживании. Пожалуйста, подождите.")


@dp.message(Command("tech_0"))
async def send_tech_0(message: types.Message):
    if message.from_user.id != config.SUPER_ADMIN_ID:
        await message.reply("Это админ команда")
    else:
        for admin_id in config.ADMIN_IDS:
            await bot.send_message(chat_id=admin_id, text="Бот в работе. Пожалуйста, повторно авторизуйтесь.")
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )


@dp.message(Command("helpbytema"))
async def send_tech(message: types.Message):
    if message.from_user.id != config.SUPER_ADMIN_ID:
        await message.reply("Это админ команда")
    else:
        for admin_id in config.ADMIN_IDS:
            await bot.send_message(chat_id=admin_id,
                                   text="При возникновении каких-либо критических ошибок, пожалуйста, обратитесь к telegram @malsssoul. Заранее спасибо!")


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Добрый день, я телеграм бот сети техосмотров Экосмотр по всей России. "
                        "Пришли мне номер диагностической карты и я пришлю файл")
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Вход", callback_data='login_3'),
        InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
        InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
    )
    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.callback_query(F.data == 'login_3')
async def login_inline_1(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_login)
    await call.message.answer("Введите, пожалуйста, логин и пароль одним сообщением через пробел.")

@dp.callback_query(F.data == 'dk_3')
async def action_choice(call: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💻 Номер ДК", callback_data='nomer_dk'),
        InlineKeyboardButton(text="🚘 VIN", callback_data='VIN'),
        InlineKeyboardButton(text="🚐 Рег. номер", callback_data='reg_number'),
        InlineKeyboardButton(text="🚛 Кузов\Рама", callback_data='Kuzov/rama'),
    )
    await call.message.answer(
        "Выберите желаемый параметр для поиска:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.callback_query(F.data == 'nomer_dk')
async def nomer_dk(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_input_dk)
    await call.message.answer("Введите, пожалуйста, номер дк.")


@dp.callback_query(F.data == 'VIN')
async def nomer_dk(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_input_vin)
    await call.message.answer("Введите, пожалуйста, VIN.")


@dp.callback_query(F.data == 'reg_number')
async def nomer_dk(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_input_rn)
    await call.message.answer("Введите, пожалуйста, регистрационный номер.")


@dp.callback_query(F.data == 'Kuzov/rama')
async def nomer_dk(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_input_kr)
    await call.message.answer("Введите, пожалуйста, кузов\раму.")


@dp.message(DialogStates.waiting_for_input_dk)
async def process_number_0(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.reply("Скачиваю ДК..")
        res = await dwnldk_dk(user_input)
        res_2 = await dwnldk_statistic(user_input)
        print(res, res_2)
        if res_2 == 'ДК ожидает регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК ожидает регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 'ДК в процессе регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК в процессе регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 0 or res_2 == 'None' or res_2 is None:
            await bot.send_message(chat_id=message.from_user.id, text=r'Дк не существует!')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        with open("logss.txt", 'r') as f:
            asa = f.readline()
        if asa == "[Errno 2] No such file or directory: ''":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=r'ДК еще не зарегистрировалась ИЛИ В драйве нет файла ДК')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            with open('logss.txt', 'w') as file:
                pass
        else:
            if res != 0 or res != 'None' or res is not None:
                await message.reply("Ваша дк: ")
                document = FSInputFile(f'{res}.pdf')
                await bot.send_document(chat_id=message.from_user.id, document=document)
                os.remove(f'{res}.pdf')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )
            else:
                await bot.send_message(chat_id=message.from_user.id, text='ДК не существует!')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )


@dp.message(DialogStates.waiting_for_input_vin)
async def process_number_3(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.reply("Скачиваю ДК..")
        res = await dwnldk_vin(user_input)
        res_2 = await dwnldk_statistic(user_input)
        print(res, res_2)
        if res_2 == 'ДК ожидает регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК ожидает регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 'ДК в процессе регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК в процессе регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 0 or res_2 == 'None' or res_2 is None:
            await bot.send_message(chat_id=message.from_user.id, text=r'Дк не существует!')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        with open("logss.txt", 'r') as f:
            asa = f.readline()
        if asa == "[Errno 2] No such file or directory: ''":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=r'ДК еще не зарегистрировалась ИЛИ В драйве нет файла ДК')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            with open('logss.txt', 'w') as file:
                pass
        else:
            if res != 0 or res != 'None' or res is not None:
                await message.reply("Ваша дк: ")
                document = FSInputFile(f'{res}.pdf')
                await bot.send_document(chat_id=message.from_user.id, document=document)
                os.remove(f'{res}.pdf')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )
            else:
                await bot.send_message(chat_id=message.from_user.id, text='ДК не существует!')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )


@dp.message(DialogStates.waiting_for_input_rn)
async def process_number_4(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.reply("Скачиваю ДК..")
        res = await dwnldk_rn(user_input)
        res_2 = await dwnldk_statistic(user_input)
        print(res, res_2)
        if res_2 == 'ДК ожидает регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК ожидает регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 'ДК в процессе регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК в процессе регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 0 or res_2 == 'None' or res_2 is None:
            await bot.send_message(chat_id=message.from_user.id, text=r'Дк не существует!')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        with open("logss.txt", 'r') as f:
            asa = f.readline()
        if asa == "[Errno 2] No such file or directory: ''":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=r'ДК еще не зарегистрировалась ИЛИ В драйве нет файла ДК')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            with open('logss.txt', 'w') as file:
                pass
        else:
            if res != 0 or res != 'None' or res is not None:
                await message.reply("Ваша дк: ")
                document = FSInputFile(f'{res}.pdf')
                await bot.send_document(chat_id=message.from_user.id, document=document)
                os.remove(f'{res}.pdf')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )
            else:
                await bot.send_message(chat_id=message.from_user.id, text='ДК не существует!')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )


@dp.message(DialogStates.waiting_for_input_kr)
async def process_number_5(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.reply("Скачиваю ДК..")
        res = await dwnldk_kr(user_input)
        res_2 = await dwnldk_statistic(user_input)
        print(res, res_2)
        if res_2 == 'ДК ожидает регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК ожидает регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 'ДК в процессе регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК в процессе регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 0 or res_2 == 'None' or res_2 is None:
            await bot.send_message(chat_id=message.from_user.id, text=r'Дк не существует!')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        with open("logss.txt", 'r') as f:
            asa = f.readline()
        if asa == "[Errno 2] No such file or directory: ''":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=r'ДК еще не зарегистрировалась ИЛИ В драйве нет файла ДК')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            with open('logss.txt', 'w') as file:
                pass
        else:
            if res != 0 or res != 'None' or res is not None:
                await message.reply("Ваша дк: ")
                document = FSInputFile(f'{res}.pdf')
                await bot.send_document(chat_id=message.from_user.id, document=document)
                os.remove(f'{res}.pdf')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )
            else:
                await bot.send_message(chat_id=message.from_user.id, text='ДК не существует!')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )


@dp.message(DialogStates.waiting_for_input)
async def process_number_1(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        # args = message.text.split()[1:]
        await message.reply("Скачиваю ДК..")
        res = await dwnldk_dk(user_input)
        res_2 = await dwnldk_statistic(user_input)
        print(res, res_2)
        if res_2 == 'ДК ожидает регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК ожидает регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 'ДК в процессе регистрации':
            await bot.send_message(chat_id=message.from_user.id, text=r'ДК в процессе регистрации')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        if res_2 == 0 or res_2 == 'None' or res_2 is None:
            await bot.send_message(chat_id=message.from_user.id, text=r'Дк не существует!')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            return
        with open("logss.txt", 'r') as f:
            asa = f.readline()
        if asa == "[Errno 2] No such file or directory: ''":
            await bot.send_message(chat_id=message.from_user.id,
                                   text=r'ДК еще не зарегистрировалась ИЛИ В драйве нет файла ДК')
            await state.clear()
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Вход", callback_data='login_3'),
                InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
            )
            await message.answer(
                "Выберите действие:",
                reply_markup=builder.as_markup(resize_keyboard=True),
            )
            with open('logss.txt', 'w') as file:
                pass
        else:
            if res != 0 or res != 'None' or res is not None:
                a = dict.get(message.from_user.username)
                a += 1
                dict.update({message.from_user.username: a})
                await message.reply("Ваша дк: ")
                document = FSInputFile(f'{res}.pdf')
                await bot.send_document(chat_id=message.from_user.id, document=document)
                os.remove(f'{res}.pdf')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )
            else:
                await bot.send_message(chat_id=message.from_user.id, text='ДК не существует!')
                await state.clear()
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Вход", callback_data='login_3'),
                    InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
                    InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
                )
                await message.answer(
                    "Выберите действие:",
                    reply_markup=builder.as_markup(resize_keyboard=True),
                )


@dp.message(DialogStates.waiting_for_login)
async def process_number_2(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(number=user_input)
    args = user_input.split()
    if args[0] == config.CREDENTIALS_LOGIN and args[1] == config.CREDENTIALS_PASS:
        ids.append(message.from_user.id)
        dict.update({message.from_user.username: 0})
        print(ids)
        await message.reply("Авторизация успешна, добро пожаловать")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )


@dp.message(Command("stat"))
async def stat_check(message: types.Message):
    if message.from_user.id != config.SUPER_ADMIN_ID:
        await message.reply("Это админ команда")
    else:
        print(dict)
        await bot.send_message(chat_id=message.from_user.id, text='Босс, твоя статистика:')
        await bot.send_message(chat_id=message.from_user.id, text=str(dict))


async def dwnldk_dk(nomer):
    try:
        conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"""
                    SELECT
                    et.id, 
                    et.nomer,
                    CASE et.isDublicate
                    WHEN 1 THEN 'Дубликат ДК'
                    WHEN 2 THEN 'ДК ожидает регистрации'
                    WHEN 3 THEN 'ДК Удалена'
                    WHEN 4 THEN 'ДК Отменена'
                    WHEN 99 THEN 'Черновик ДК'
                    WHEN 5 THEN 'ДК в процессе регистрации'
                    WHEN 10 THEN 'ДК является шаблоном для эксперта'
                    ELSE 'ДК зарегистрирована'
                    END AS status
                    FROM tomain et 
                    WHERE 
                    et.nomer LIKE '{nomer}'
                    ORDER BY et.createdAt DESC;
                """)
    for a in cur:
        conn.close()
        if str(a) != 'None' and a is not None:
            print(a[0])
            logins.logging(a[0], a[1])
            return a[1]
        else:
            return 0
    conn.close()


async def dwnldk_vin(nomer):
    try:
        conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"""
                    SELECT
                    et.id, 
                    et.vin,
                    CASE et.isDublicate
                    WHEN 1 THEN 'Дубликат ДК'
                    WHEN 2 THEN 'ДК ожидает регистрации'
                    WHEN 3 THEN 'ДК Удалена'
                    WHEN 4 THEN 'ДК Отменена'
                    WHEN 99 THEN 'Черновик ДК'
                    WHEN 5 THEN 'ДК в процессе регистрации'
                    WHEN 10 THEN 'ДК является шаблоном для эксперта'
                    ELSE 'ДК зарегистрирована'
                    END AS status
                    FROM tomain et 
                    WHERE 
                    et.vin LIKE '{nomer}'
                    ORDER BY et.createdAt DESC;
                """)
    for a in cur:
        conn.close()
        if str(a) != 'None' and a is not None:
            print(a[0])
            logins.logging(a[0], a[1])
            return a[1]
        else:
            return 0
    conn.close()


async def dwnldk_rn(nomer):
    try:
        conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"""
                    SELECT
                    et.id, 
                    et.registrationNumber,
                    CASE et.isDublicate
                    WHEN 1 THEN 'Дубликат ДК'
                    WHEN 2 THEN 'ДК ожидает регистрации'
                    WHEN 3 THEN 'ДК Удалена'
                    WHEN 4 THEN 'ДК Отменена'
                    WHEN 99 THEN 'Черновик ДК'
                    WHEN 5 THEN 'ДК в процессе регистрации'
                    WHEN 10 THEN 'ДК является шаблоном для эксперта'
                    ELSE 'ДК зарегистрирована'
                    END AS status
                    FROM tomain et 
                    WHERE 
                    et.registrationNumber LIKE '{nomer}'
                    ORDER BY et.createdAt DESC;
                """)
    for a in cur:
        conn.close()
        if str(a) != 'None' and a is not None:
            print(a[0])
            logins.logging(a[0], a[1])
            return a[1]
        else:
            return 0
    conn.close()


async def dwnldk_kr(nomer):
    try:
        conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"""
                    SELECT
                    et.id, 
                    et.nomer,
                    CASE et.isDublicate
                    WHEN 1 THEN 'Дубликат ДК'
                    WHEN 2 THEN 'ДК ожидает регистрации'
                    WHEN 3 THEN 'ДК Удалена'
                    WHEN 4 THEN 'ДК Отменена'
                    WHEN 99 THEN 'Черновик ДК'
                    WHEN 5 THEN 'ДК в процессе регистрации'
                    WHEN 10 THEN 'ДК является шаблоном для эксперта'
                    ELSE 'ДК зарегистрирована'
                    END AS status
                    FROM tomain et 
                    WHERE 
                    et.bodyNumber LIKE '{nomer}'
                    OR et.frameNumber LIKE '{nomer}'
                    ORDER BY et.createdAt DESC;
                """)
    for a in cur:
        conn.close()
        if str(a) != 'None' and a is not None:
            print(a[0])
            logins.logging(a[0], a[1])
            return a[1]
        else:
            return 0
    conn.close()


async def dwnldk_statistic(nomer):
    try:
        conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"""
                    SELECT
                    et.id, 
                    et.nomer, 
                    et.vin, 
                    et.registrationNumber,
                    CASE et.isDublicate
                    WHEN 1 THEN 'Дубликат ДК'
                    WHEN 2 THEN 'ДК ожидает регистрации'
                    WHEN 3 THEN 'ДК Удалена'
                    WHEN 4 THEN 'ДК Отменена'
                    WHEN 99 THEN 'Черновик ДК'
                    WHEN 5 THEN 'ДК в процессе регистрации'
                    WHEN 10 THEN 'ДК является шаблоном для эксперта'
                    ELSE 'ДК зарегистрирована'
                    END AS status
                    FROM tomain et 
                    WHERE 
                    et.nomer LIKE '{nomer}' 
                    OR et.vin LIKE '{nomer}'
                    OR et.registrationNumber LIKE '{nomer}' 
                    OR et.bodyNumber LIKE '{nomer}'
                    OR et.frameNumber LIKE '{nomer}'
                    ORDER BY et.createdAt DESC;
                """)
    for a in cur:
        conn.close()
        if str(a) != 'None':
            return a[4]
        else:
            return 0
    conn.close()


@dp.callback_query(F.data == 'download_archive')
async def download_archive_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_org_name)
    await call.message.answer("Введите название организации:")


@dp.message(DialogStates.waiting_for_org_name)
async def process_org_name(message: Message, state: FSMContext):
    if message.from_user.id not in ids:
        await message.reply("Пожалуйста, авторизуйтесь")
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Вход", callback_data='login_3'),
            InlineKeyboardButton(text="Скачать дк", callback_data='dk_3'),
            InlineKeyboardButton(text="Скачать архив", callback_data='download_archive'),
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await state.update_data(org_name=message.text)
        await state.set_state(DialogStates.waiting_for_date_start)
        await message.answer("Введите дату начала периода (ГГГГ-ММ-ДД):")


@dp.message(DialogStates.waiting_for_date_start)
async def process_date_start(message: Message, state: FSMContext):
    if not re.match(r'\d{4}-\d{2}-\d{2}', message.text):
        await message.answer("Неверный формат даты! Используйте ГГГГ-ММ-ДД")
        return
    await state.update_data(date_start=message.text)
    await state.set_state(DialogStates.waiting_for_date_end)
    await message.answer("Введите дату окончания периода (ГГГГ-ММ-ДД):")


def _chunked(iterable, size: int):
    """Разбивает последовательность на куски фиксированного размера."""
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

@dp.message(DialogStates.waiting_for_date_end)
async def process_date_end(message: Message, state: FSMContext):
    if not re.match(r'\d{4}-\d{2}-\d{2}', message.text):
        await message.answer("Неверный формат даты! Используйте ГГГГ-ММ-ДД")
        return

    user_data = await state.get_data()
    org_name = user_data.get('org_name')
    date_start = user_data.get('date_start')
    date_end = message.text

    try:
        count_dk = await execute_count_query(org_name, date_start, date_end)
        if count_dk == 0:
            await message.answer("Ничего не найдено")
            await state.clear()
            return

        ids_list = await execute_ids_query(org_name, date_start, date_end)

        await message.answer(
            f"Найдено ДК: {count_dk}. Начинаю скачивание партиями по 10 и сборку архива…"
        )

        folder_name = f"archive_{int(time.time())}"
        os.makedirs(folder_name, exist_ok=True)

        skipped = []
        downloaded = 0

        for batch in _chunked(ids_list, 10):
            tasks = [dwnldk_dk(str(dk_tuple[0])) for dk_tuple in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for dk_tuple, res in zip(batch, results):
                nomer = str(dk_tuple[0])
                if isinstance(res, Exception):
                    skipped.append(nomer)
                    continue

                pdf_name = f"{res}.pdf"
                try:
                    if os.path.exists(pdf_name):
                        shutil.move(pdf_name, os.path.join(folder_name, f"{res}.pdf"))
                        downloaded += 1
                    else:
                        skipped.append(nomer)
                except Exception:
                    skipped.append(nomer)

            await asyncio.sleep(1)

        if downloaded == 0:
            shutil.rmtree(folder_name, ignore_errors=True)
            await message.answer("Не удалось собрать архив: не найдено ни одного PDF по выбранным параметрам.")
            await state.clear()
            return

        shutil.make_archive(folder_name, 'zip', folder_name)
        document = FSInputFile(f"{folder_name}.zip")
        await bot.send_document(chat_id=message.from_user.id, document=document)

        msg = [f"Готово. В архив добавлено файлов: {downloaded}."]
        if skipped:
            sample = ", ".join(skipped[:20])
            tail = "" if len(skipped) <= 20 else f" и ещё {len(skipped) - 20}…"
            msg.append(f"Не удалось найти/скачать для номеров: {sample}{tail}")
        await message.answer("\n".join(msg))

        # 7) Уборка
        shutil.rmtree(folder_name, ignore_errors=True)
        try:
            os.remove(f"{folder_name}.zip")
        except OSError:
            pass

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        await state.clear()


async def execute_count_query(org_name, date_start, date_end):
    conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT COUNT(et.id) 
        FROM tomain et 
        LEFT JOIN ur_face uf ON et.urFace = uf.id
        WHERE 
            uf.name LIKE '%{org_name}%' 
            AND et.createdAt >= %s 
            AND et.createdAt <= %s
    """, (date_start, date_end))
    result = cur.fetchone()[0]
    conn.close()
    return result


async def execute_ids_query(org_name, date_start, date_end):
    conn = mariadb.connect(**config.DB_CONFIG_MARIADB)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT et.nomer 
        FROM tomain et 
        LEFT JOIN ur_face uf ON et.urFace = uf.id
        WHERE 
            uf.name LIKE '%{org_name}%' 
            AND et.createdAt >= %s 
            AND et.createdAt <= %s 
        ORDER BY et.createdAt DESC
    """, (date_start, date_end))
    result = cur.fetchall()
    conn.close()
    return result


async def main():
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Ошибка: {e}. Перезапускаем бота через 5 секунд.")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())