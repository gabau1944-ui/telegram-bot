import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = "8330900181:AAHCcdEUiSubo_BoHrGPfPNdpZeF5W35L_w"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Активные пользователи и пары
waiting_users = set()
active_pairs = {}

# --- Кнопки ---
def main_keyboard():
    buttons = [
        [types.KeyboardButton("🔍 Найти собеседника")],
        [types.KeyboardButton("❌ Завершить диалог")]
    ]
    return types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

# --- Команды ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Это анонимный чат.\nНажми «🔍 Найти собеседника» чтобы начать общение.",
        reply_markup=main_keyboard()
    )

# --- Поиск собеседника ---
@dp.message_handler(lambda m: m.text == "🔍 Найти собеседника")
async def find_chat(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_pairs:
        await message.answer("💬 Вы уже в чате. Завершите его, чтобы начать новый.")
        return

    if waiting_users:
        partner_id = waiting_users.pop()
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await bot.send_message(user_id, "✅ Собеседник найден! Можно начинать чат.")
        await bot.send_message(partner_id, "✅ Собеседник найден! Можно начинать чат.")
    else:
        waiting_users.add(user_id)
        await message.answer("⌛ Ожидаем собеседника...")

# --- Завершение диалога ---
@dp.message_handler(lambda m: m.text == "❌ Завершить диалог")
async def end_chat(message: types.Message):
    user_id = message.from_user.id

    if user_id not in active_pairs:
        await message.answer("⚠️ У вас нет активного чата.")
        return

    partner_id = active_pairs.pop(user_id)
    active_pairs.pop(partner_id, None)

    await message.answer("✅ Вы завершили диалог.")
    await bot.send_message(partner_id, "⚠️ Собеседник покинул чат.")

# --- Пересылка сообщений ---
@dp.message_handler(content_types=types.ContentType.ANY)
async def relay_message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in active_pairs:
        return

    partner_id = active_pairs[user_id]
    try:
        if message.text:
            await bot.send_message(partner_id, message.text)
        elif message.photo:
            await bot.send_photo(partner_id, message.photo[-1].file_id, caption=message.caption)
        elif message.voice:
            await bot.send_voice(partner_id, message.voice.file_id, caption=message.caption)
        elif message.sticker:
            await bot.send_sticker(partner_id, message.sticker.file_id)
        elif message.video:
            await bot.send_video(partner_id, message.video.file_id, caption=message.caption)
    except Exception as e:
        logging.error(f"Ошибка при пересылке: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
