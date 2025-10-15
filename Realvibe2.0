import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("8330900181:AAHCcdEUiSubo_BoHrGPfPNdpZeF5W35L_w")  # токен берётся из переменной окружения
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

waiting_users = set()
active_chats = {}

# ---------- Кнопки ----------
def chat_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💬 Следующий", callback_data="next"))
    kb.add(InlineKeyboardButton("❌ Завершить", callback_data="end"))
    return kb

# ---------- Команды ----------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Это анонимный чат.\n\nНажми /search, чтобы найти собеседника.",
    )

@dp.message_handler(commands=["search"])
async def search(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_chats:
        await message.answer("❗ Вы уже находитесь в чате.")
        return

    if waiting_users:
        partner_id = waiting_users.pop()
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        await bot.send_message(
            partner_id,
            "🔗 Найден собеседник! Начинайте общение.",
            reply_markup=chat_keyboard(),
        )
        await bot.send_message(
            user_id,
            "🔗 Найден собеседник! Начинайте общение.",
            reply_markup=chat_keyboard(),
        )
    else:
        waiting_users.add(user_id)
        await message.answer("🔎 Поиск собеседника...")

@dp.message_handler(commands=["support"])
async def support(message: types.Message):
    await message.answer("💬 Поддержка: @YourSupportUsername")

# ---------- Сообщения ----------
@dp.message_handler()
async def chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            await bot.send_message(partner_id, message.text)
        except:
            await message.answer("⚠️ Ошибка отправки.")
    else:
        await message.answer("🔎 Вы не в чате. Нажмите /search.")

# ---------- Кнопки ----------
@dp.callback_query_handler(lambda c: c.data == "end")
async def end_chat(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await bot.send_message(partner_id, "😔 Ваш собеседник покинул чат.")
        await call.message.edit_text("✅ Вы завершили диалог.")
    else:
        await call.message.answer("❗ Вы не находитесь в чате.")

@dp.callback_query_handler(lambda c: c.data == "next")
async def next_chat(call: types.CallbackQuery):
    user_id = call.from_user.id

    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await bot.send_message(partner_id, "😔 Ваш собеседник покинул чат. Поиск нового...")
        await call.message.edit_text("🔄 Ищем нового собеседника...")
    else:
        await call.message.answer("🔎 Поиск нового собеседника...")

    await search(call.message)

# ---------- Запуск ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
