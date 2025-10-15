import telebot
from telebot import types

# 🔑 ВСТАВЬ СВОЙ ТОКЕН
bot = telebot.TeleBot("7905948326:AAHT6NbDvDG1o74qNTn54Ug5hdEtDVZpk14")

# 🔹 Твой Telegram ID (куда приходят обращения)
ADMIN_ID = 7269713366  # замени на свой ID

# 📋 Храним, кому отвечаем
pending_replies = {}

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте! 👋\n\n"
        "Напишите ваше обращение, и наши операторы свяжутся с вами в ближайшее время."
    )

# 📨 Получаем сообщения от пользователей
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def user_message(message):
    user = message.from_user
    text_to_admin = (
        f"📩 Новое обращение от @{user.username or 'Без никнейма'} (ID: {message.chat.id}):\n\n"
        f"{message.text}"
    )

    # Кнопка "Ответить"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_{message.chat.id}"))

    # Отправляем админу
    bot.send_message(ADMIN_ID, text_to_admin, reply_markup=markup)

    # Подтверждаем пользователю
    bot.send_message(
        message.chat.id,
        "✅ Ваше обращение успешно отправлено! Ожидайте ответа от поддержки."
    )

# 🎯 Обработка нажатия кнопки "Ответить"
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply(call):
    user_id = int(call.data.split("_")[1])
    pending_replies[call.message.chat.id] = user_id
    bot.send_message(call.message.chat.id, f"✍️ Напишите ответ для пользователя (ID: {user_id})")

# 💬 Отправляем ответ пользователю
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID)
def admin_reply(message):
    if message.chat.id in pending_replies:
        user_id = pending_replies.pop(message.chat.id)
        bot.send_message(user_id, f"💬 Ответ поддержки:\n{message.text}")
        bot.send_message(message.chat.id, "✅ Ответ отправлен пользователю.")
    else:
        bot.send_message(message.chat.id, "ℹ️ Напишите пользователю через кнопку 'Ответить' под его обращением.")

bot.polling(none_stop=True)